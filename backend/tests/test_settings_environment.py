"""The Environment-setting layer and the override check (FR-430, FR-431, FR-446, FR-447; FD-1320).

`07` §3.8: process variable → Environment setting → workspace setting → platform default.
`RL-1311` item 3a: a process variable never supplies an Environment-only setting.

The tests that need no database come first; the DB-backed ones are marked below. A key
registered here with `monkeypatch.setitem` stands in for the Environment-only flags that
Slice 6 declares (`PL-1537` R6.1).
"""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from app.config import ConfigInvalidError, Settings
from app.main import create_app
from app.platform import settings as svc
from app.platform.settings import SettingDefinition, SettingScope
from model_schema import SettingType

ENV_ONLY_KEY = "test.environment_only_flag"
ENV_ONLY_VAR = "GIP_SETTING_TEST_ENVIRONMENT_ONLY_FLAG"
PSI_VAR = "GIP_SETTING_VALIDATION_PSI_WARN_THRESHOLD"


@pytest.fixture
def environment_only_key(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setitem(
        svc.REGISTRY,
        ENV_ONLY_KEY,
        SettingDefinition(
            key=ENV_ONLY_KEY,
            type=SettingType.BOOL,
            default=False,
            description="A test-registered Environment-only flag.",
            scope=SettingScope.ENVIRONMENT,
        ),
    )
    return ENV_ONLY_KEY


@pytest.mark.req("FR-446")
def test_scope_defaults_to_workspace_only_and_two_keys_are_declared_environment_capable() -> None:
    assert SettingDefinition(
        key="x", type=SettingType.INT, default=1, description="d"
    ).scope is SettingScope.WORKSPACE
    environment_capable = {
        k for k, d in svc.REGISTRY.items() if d.scope is not SettingScope.WORKSPACE
    }
    assert environment_capable == {
        "rating.trace_sample_rate",
        "scoring.default_client_rate_limit_rps",
    }
    for key in environment_capable:
        assert svc.REGISTRY[key].scope is SettingScope.WORKSPACE_OR_ENVIRONMENT


# --- FR-447 / FD-1320: the override check -------------------------------------------------


@pytest.mark.req("FR-447")
def test_a_valid_override_passes_the_startup_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(PSI_VAR, "0.35")
    svc.validate_setting_overrides(Settings())


@pytest.mark.req("FR-447")
def test_an_unknown_override_key_is_refused_naming_the_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIP_SETTING_NO_SUCH_KEY", "1")
    with pytest.raises(ConfigInvalidError, match="GIP_SETTING_NO_SUCH_KEY"):
        svc.validate_setting_overrides(Settings())


@pytest.mark.req("FR-447")
def test_an_ill_typed_override_is_refused_naming_the_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(PSI_VAR, "not-a-number")
    with pytest.raises(ConfigInvalidError, match=PSI_VAR):
        svc.validate_setting_overrides(Settings())


@pytest.mark.req("FR-447")
def test_an_out_of_range_override_is_refused_naming_the_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(PSI_VAR, "7.5")
    with pytest.raises(ConfigInvalidError, match=PSI_VAR):
        svc.validate_setting_overrides(Settings())


@pytest.mark.req("FR-446")
def test_an_environment_only_key_in_the_process_environment_is_refused_at_startup(
    monkeypatch: pytest.MonkeyPatch, environment_only_key: str
) -> None:
    monkeypatch.setenv(ENV_ONLY_VAR, "true")
    with pytest.raises(ConfigInvalidError) as exc:
        svc.validate_setting_overrides(Settings())
    assert ENV_ONLY_VAR in str(exc.value)
    assert "Environment-only" in str(exc.value)


@pytest.mark.req("FR-446")
def test_an_environment_only_variable_seen_at_resolve_is_skipped_and_logged(
    monkeypatch: pytest.MonkeyPatch,
    environment_only_key: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv(ENV_ONLY_VAR, "true")
    definition = svc.REGISTRY[environment_only_key]
    with caplog.at_level(logging.WARNING):
        assert svc._env_candidate(Settings(), definition) is None
    assert any(ENV_ONLY_VAR in r.getMessage() for r in caplog.records)
    assert not any("true" in r.getMessage() for r in caplog.records)


# --- the same check through the real create_app lifespan, with the database ---------------


@pytest.mark.req("FR-447")
@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("GIP_SETTING_NO_SUCH_KEY", "1"),
        (PSI_VAR, "not-a-number"),
    ],
)
def test_the_lifespan_refuses_a_bad_override(
    monkeypatch: pytest.MonkeyPatch, api_settings: Settings, variable: str, value: str
) -> None:
    monkeypatch.setenv(variable, value)
    with pytest.raises(ConfigInvalidError, match=variable), TestClient(create_app(api_settings)):
        pytest.fail("the app must not finish starting")


@pytest.mark.req("FR-446")
def test_the_lifespan_refuses_an_environment_only_override(
    monkeypatch: pytest.MonkeyPatch, api_settings: Settings, environment_only_key: str
) -> None:
    monkeypatch.setenv(ENV_ONLY_VAR, "true")
    with pytest.raises(ConfigInvalidError, match=ENV_ONLY_VAR), TestClient(
        create_app(api_settings)
    ):
        pytest.fail("the app must not finish starting")
