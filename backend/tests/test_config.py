"""Configuration is validated at startup, not at first use (07 §3.8)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import (
    ConfigInvalidError,
    Environment,
    Settings,
    SettingSource,
    load_settings,
)

_SHA = "97b15726b1dd60ba407c6aba44735ad5cbe207ed"


@pytest.mark.req("FR-446")
def test_resolve_reports_default_source() -> None:
    settings = Settings()
    resolution = settings.resolve("job_stall_seconds")
    assert resolution.value == 30
    assert resolution.source is SettingSource.DEFAULT


@pytest.mark.req("FR-446")
def test_resolve_reports_environment_source_when_overridden() -> None:
    """A value differing from the platform default must be attributed, not just returned."""
    settings = Settings(job_stall_seconds=15)
    resolution = settings.resolve("job_stall_seconds")
    assert resolution.value == 15
    assert resolution.source is SettingSource.ENVIRONMENT


@pytest.mark.req("FR-446")
def test_resolve_rejects_unknown_key() -> None:
    with pytest.raises(ConfigInvalidError, match="unknown setting"):
        Settings().resolve("no_such_setting")


@pytest.mark.req("FR-447")
def test_out_of_range_setting_prevents_startup() -> None:
    """The failure must name the environment variable an operator would edit."""
    with pytest.raises(ConfigInvalidError) as exc:
        load_settings(job_stall_seconds=0)
    message = str(exc.value)
    assert "refusing to start" in message
    assert "GIP_JOB_STALL_SECONDS" in message


@pytest.mark.req("FR-447")
def test_extra_setting_is_rejected() -> None:
    """A typo'd variable must fail loudly rather than be silently ignored."""
    with pytest.raises(ConfigInvalidError, match="GIP_JOB_STALL_SECOND"):
        load_settings(job_stall_second=30)


@pytest.mark.req("FR-416")
def test_sync_database_driver_is_refused() -> None:
    """A sync driver does not error — it blocks the event loop. Catch it at startup."""
    with pytest.raises(ConfigInvalidError, match="asyncpg"):
        load_settings(database_url="postgresql://gip:gip@localhost:5432/gip")


@pytest.mark.req("FR-391")
def test_prod_without_tls_refuses_to_start() -> None:
    with pytest.raises(ConfigInvalidError, match="TLS"):
        load_settings(environment=Environment.PROD)


@pytest.mark.req("FR-391")
def test_prod_with_tls_and_an_identity_provider_starts() -> None:
    settings = load_settings(
        environment=Environment.PROD,
        tls_terminated=True,
        build=_SHA,
        tenant_id="acme-motor",
        oidc_issuer="https://idp.example/realms/gip",
        oidc_audience="gi-pricing-api",
        oidc_jwks_url="https://idp.example/realms/gip/protocol/openid-connect/certs",
    )
    assert settings.environment is Environment.PROD
    assert settings.oidc_configured


@pytest.mark.req("FR-387")
def test_prod_without_an_identity_provider_refuses_to_start() -> None:
    """Starting anyway would present a service that rejects every request as if broken."""
    with pytest.raises(ConfigInvalidError, match="OIDC issuer"):
        load_settings(environment=Environment.PROD, tls_terminated=True)


@pytest.mark.req("FR-391")
def test_non_prod_without_tls_starts() -> None:
    """The TLS rule is a prod rule; requiring it locally would push people to disable it."""
    assert load_settings(environment=Environment.LOCAL).tls_terminated is False


def test_the_oidc_client_id_is_configured_like_its_siblings() -> None:
    settings = load_settings(
        environment=Environment.LOCAL,
        oidc_client_id="gi-pricing-frontend",
    )
    assert settings.oidc_client_id == "gi-pricing-frontend"


def test_the_oidc_client_id_defaults_empty_like_the_rest_of_the_trio() -> None:
    assert load_settings(environment=Environment.LOCAL).oidc_client_id == ""


@pytest.mark.req("FR-4")
def test_settings_are_frozen() -> None:
    """Configuration must not drift at runtime — a mutated setting is unauditable."""
    settings = Settings()
    with pytest.raises(ValidationError):
        settings.log_level = "DEBUG"  # type: ignore[misc]


@pytest.mark.req("FR-18")
@pytest.mark.parametrize("environment", [Environment.DEV, Environment.UAT, Environment.PROD])
@pytest.mark.parametrize(
    "build",
    [None, "local", "latest", _SHA.upper(), _SHA[:39], _SHA + "0"],
    ids=["unset", "local", "word", "uppercase", "short", "long"],
)
def test_a_strict_environment_refuses_a_missing_or_malformed_build(
    environment: Environment, build: str | None
) -> None:
    """A recorded build must name exactly one build: `latest` records the same string for
    every image, which is the failure FR-18 exists to prevent."""
    extra = {"build": build} if build is not None else {}
    with pytest.raises(ConfigInvalidError, match="GIP_BUILD") as exc:
        load_settings(
            environment=environment,
            tls_terminated=True,
            tenant_id="acme-motor",
            oidc_issuer="https://idp.example/realms/gip",
            **extra,
        )
    assert exc.value.code == "SETTING_INVALID"


@pytest.mark.req("FR-18")
def test_local_starts_with_the_local_build_marker() -> None:
    assert load_settings(environment=Environment.LOCAL).build == "local"


@pytest.mark.req("FR-436")
@pytest.mark.parametrize("environment", [Environment.DEV, Environment.UAT, Environment.PROD])
@pytest.mark.parametrize("tenant_id", [None, "", "local"], ids=["unset", "empty", "local"])
def test_a_strict_environment_refuses_a_missing_or_default_tenant_id(
    environment: Environment, tenant_id: str | None
) -> None:
    """A check whose configured side is the local default proves nothing: `local` supplied
    in prod would pass as "configured" while carrying no tenant (RL-1253, DP-S1-3)."""
    extra = {"tenant_id": tenant_id} if tenant_id is not None else {}
    with pytest.raises(ConfigInvalidError, match="GIP_TENANT_ID") as exc:
        load_settings(
            environment=environment,
            tls_terminated=True,
            build=_SHA,
            oidc_issuer="https://idp.example/realms/gip",
            **extra,
        )
    assert exc.value.code == "SETTING_INVALID"


@pytest.mark.req("FR-436")
def test_local_starts_with_the_local_tenant_id() -> None:
    assert load_settings(environment=Environment.LOCAL).tenant_id == "local"
