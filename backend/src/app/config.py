"""Typed configuration (07 §3.8).

FR-PLAT-43 gives settings a three-layer precedence: **environment variable → workspace
setting → platform default**, and requires the effective value *and its source* to be
visible. FR-PLAT-44 requires validation at startup — an invalid setting must prevent
startup with a clear message rather than failing at first use, halfway through a job.

The workspace layer is a database read and arrives with the settings table; `SettingSource`
already names it so that adding the layer does not change this module's contract.
"""

from __future__ import annotations

import enum
from typing import Annotated, Any, Literal

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "ConfigInvalidError",
    "Environment",
    "SettingResolution",
    "SettingSource",
    "Settings",
    "load_settings",
]


class Environment(enum.StrEnum):
    """Deployment environment. `prod` carries the strict rules (FR-PLAT-5)."""

    LOCAL = "local"
    DEV = "dev"
    UAT = "uat"
    PROD = "prod"


class SettingSource(enum.StrEnum):
    """Which layer supplied the effective value (FR-PLAT-43)."""

    ENVIRONMENT = "environment"
    WORKSPACE = "workspace"
    DEFAULT = "default"


class SettingResolution[T]:
    """An effective value together with the layer it came from.

    Returned rather than a bare value because "why is this setting what it is?" is a
    support question, and answering it from three layers of precedence without a recorded
    source means reading deployment manifests.
    """

    __slots__ = ("key", "source", "value")

    def __init__(self, key: str, value: T, source: SettingSource) -> None:
        self.key = key
        self.value = value
        self.source = source

    def __repr__(self) -> str:
        return (
            f"SettingResolution(key={self.key!r}, value={self.value!r}, "
            f"source={self.source.value})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SettingResolution):
            return NotImplemented
        return (self.key, self.value, self.source) == (other.key, other.value, other.source)


class ConfigInvalidError(RuntimeError):
    """Configuration is unusable. Raised at startup, never at first use (FR-PLAT-44).

    Carries the `SETTING_INVALID` code that 07 §5.1 assigns to this module.
    """

    code = "SETTING_INVALID"


class Settings(BaseSettings):
    """Platform defaults, overridable by environment variable (`GIP_` prefix).

    Every field is typed and constrained, so an unusable value is a startup failure with a
    field-level message rather than an exception raised deep inside a request.
    """

    model_config = SettingsConfigDict(
        env_prefix="GIP_",
        env_file=".env",
        extra="forbid",
        frozen=True,
    )

    environment: Environment = Environment.LOCAL
    service_name: str = "gi-pricing-api"
    version: str = "0.1.0"

    # Postgres holds all metadata, artifacts, the audit log and job records (FR-PLAT-17).
    #
    # SecretStr because a DSN embeds a password. As a plain `str` it appeared verbatim in
    # `model_dump()`, so any structured log line carrying settings would have published the
    # database credentials — which is exactly what NFR-PLAT-7 forbids.
    database_url: SecretStr = SecretStr("postgresql+asyncpg://gip:gip@localhost:5432/gip")

    # Redis is the Celery broker and a cache; nothing durable lives here (FR-PLAT-22).
    # SecretStr for the same reason as `database_url` — a Redis URL can carry a password.
    redis_url: SecretStr = SecretStr("redis://localhost:6379/0")

    # S3-compatible blob store: MinIO locally, any S3 in production (FR-PLAT-18).
    blob_endpoint_url: str = "http://localhost:9000"
    blob_bucket: str = "gip-blobs"
    blob_region: str = "us-east-1"

    # SecretStr, not str: R3 keeps credentials out of logs, artifacts, audit events and
    # API responses. Pydantic renders these as `**********` in every repr and model_dump,
    # so an accidental `log.info("settings", extra={"settings": settings})` cannot leak
    # them — the protection is in the type rather than in remembering.
    blob_access_key: SecretStr = SecretStr("gipricing")
    blob_secret_key: SecretStr = SecretStr("gipricing")

    # FR-PLAT-20: a blob is deletable only when nothing references it *and* it is older
    # than this. Conservative by default — an over-eager GC deletes a dataset.
    blob_gc_grace_days: Annotated[int, Field(ge=1, le=3650)] = 30

    # FR-PLAT-21: uploads above this size use presigned multipart, so dataset files do not
    # transit the API process.
    blob_multipart_threshold_mb: Annotated[int, Field(ge=1, le=1024)] = 64

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # FR-PLAT-5 / NFR-OVR-8: the platform refuses to start in prod without TLS termination.
    tls_terminated: bool = False

    # Development-only identity, until OIDC lands (FR-PLAT-1..4).
    #
    # Defaults to False and is refused outright in `uat` and `prod` — see
    # `require_startable`. An endpoint that is open because a flag defaulted the wrong way
    # is the failure this is shaped to prevent: with it off, every authenticated route
    # returns 401 rather than silently trusting a header.
    dev_auth_enabled: bool = False

    # NFR-PLAT-3 treats a running job with no progress for this long as stalled.
    job_stall_seconds: Annotated[int, Field(gt=0, le=3600)] = 30

    # FR-PLAT-12: a repeat submission within this window returns the original job.
    idempotency_window_hours: Annotated[int, Field(gt=0, le=168)] = 24

    @field_validator("database_url")
    @classmethod
    def _database_must_be_async(cls, v: SecretStr) -> SecretStr:
        """SQLAlchemy picks its driver from the URL scheme.

        A sync driver in an async application does not fail loudly — it blocks the event
        loop, and the symptom is latency under concurrency rather than an error.
        """
        if not v.get_secret_value().startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url must use the postgresql+asyncpg:// scheme; a sync driver "
                "blocks the event loop instead of failing"
            )
        return v

    def require_startable(self) -> None:
        """Refuse to start when the environment's hard rules are unmet (FR-PLAT-5)."""
        if self.dev_auth_enabled and self.environment in {
            Environment.UAT,
            Environment.PROD,
        }:
            raise ConfigInvalidError(
                f"dev_auth_enabled must not be set in {self.environment.value}. It trusts "
                "a request header as identity, which would let any caller act as any "
                "principal in any workspace. Configure OIDC (FR-PLAT-1) instead."
            )
        if self.environment is Environment.PROD and not self.tls_terminated:
            raise ConfigInvalidError(
                "environment=prod requires TLS termination to be configured "
                "(set GIP_TLS_TERMINATED=true once the terminating proxy is in place). "
                "FR-PLAT-5 / NFR-OVR-8: all API traffic is TLS 1.3."
            )

    def resolve(self, key: str) -> SettingResolution[Any]:
        """Report a setting's effective value and the layer that supplied it.

        The workspace layer is not yet readable, so a value that differs from the field
        default must have come from the environment.
        """
        if key not in type(self).model_fields:
            raise ConfigInvalidError(f"unknown setting {key!r}")
        value = getattr(self, key)
        default = type(self).model_fields[key].default
        source = SettingSource.DEFAULT if value == default else SettingSource.ENVIRONMENT
        return SettingResolution(key=key, value=value, source=source)


def load_settings(**overrides: Any) -> Settings:
    """Build and validate settings, converting Pydantic's error into a startup failure.

    FR-PLAT-44 asks for "a clear message rather than failing at first use". A raw
    `ValidationError` names the field but not what the operator should do, so it is
    re-raised as `ConfigInvalidError` with the environment-variable name attached.
    """
    try:
        settings = Settings(**overrides)
    except ValidationError as exc:
        lines = [
            f"  GIP_{'.'.join(str(p) for p in err['loc']).upper()}: {err['msg']}"
            for err in exc.errors()
        ]
        raise ConfigInvalidError(
            "configuration is invalid, refusing to start:\n" + "\n".join(lines)
        ) from exc
    settings.require_startable()
    return settings
