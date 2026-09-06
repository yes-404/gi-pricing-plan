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
