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
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import ConfigInvalidError, Settings
from app.db.models import AuditEventRow, EnvironmentSettingRow
from app.db.session import Database
from app.errors import PlatformError
from app.main import create_app
from app.platform import audit as audit_module
from app.platform import settings as svc
from app.platform.settings import SettingDefinition, SettingScope
from model_schema import SettingSource, SettingType

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
def test_scope_defaults_to_workspace_only_and_three_keys_are_declared_environment_capable() -> None:
    assert SettingDefinition(
        key="x", type=SettingType.INT, default=1, description="d"
    ).scope is SettingScope.WORKSPACE
    environment_capable = {
        k for k, d in svc.REGISTRY.items() if d.scope is SettingScope.WORKSPACE_OR_ENVIRONMENT
    }
    # The third key is `platform.default_management_rate_limit_rps`: FR-448 declares it
    # workspace- or environment-capable (docs/specs/07-platform.md:174).
    assert environment_capable == {
        "rating.trace_sample_rate",
        "scoring.default_client_rate_limit_rps",
        "platform.default_management_rate_limit_rps",
    }
    for key in environment_capable:
        assert svc.REGISTRY[key].scope is SettingScope.WORKSPACE_OR_ENVIRONMENT


@pytest.mark.req("FR-446", "FR-270", "FR-271")
def test_the_routing_and_shadow_flags_are_environment_only() -> None:
    """WK-674 Slice 6 (`RL-1311` item 3, `03` §4.13): the two flags are declared `ENVIRONMENT`
    scope, so no workspace value can enable routing or shadow scoring for an Environment. They
    are the only Environment-only keys, so together with the three workspace-or-environment keys
    above they are every key that is not workspace-only."""
    environment_only = {
        k for k, d in svc.REGISTRY.items() if d.scope is SettingScope.ENVIRONMENT
    }
    assert environment_only == {
        "features.date_routing_enabled",
        "features.shadow_scoring_enabled",
    }


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


# --- the Environment layer (database) ------------------------------------------------------

TRACE = "rating.trace_sample_rate"
PSI = "validation.psi_warn_threshold"


@pytest_asyncio.fixture
async def clean_environment_settings(database: Database):
    """Environments are deployment-wide, so rows written here would outlive the test."""
    yield
    async with database.unit_of_work() as session:
        await session.execute(delete(EnvironmentSettingRow))


async def _set(database: Database, environment: str, key: str, value) -> None:
    async with database.unit_of_work() as session:
        await svc.set_environment_setting(session, environment, key, value, None)


@pytest.mark.req("FR-446")
async def test_a_value_set_for_uat_changes_uat_only(
    database: Database, workspace_id, clean_environment_settings
) -> None:
    await _set(database, "uat", TRACE, 0.5)
    async with database.session() as session:
        uat = await svc.resolve(session, Settings(), workspace_id, TRACE, "uat")
        prod = await svc.resolve(session, Settings(), workspace_id, TRACE, "prod")
        none = await svc.resolve(session, Settings(), workspace_id, TRACE)
    assert (uat.effective_value, uat.resolved_from) == (0.5, SettingSource.ENVIRONMENT_SETTING)
    assert prod.resolved_from is SettingSource.DEFAULT
    assert none.resolved_from is SettingSource.DEFAULT
    assert [c.source for c in uat.candidates] == [
        SettingSource.ENV,
        SettingSource.ENVIRONMENT_SETTING,
        SettingSource.WORKSPACE,
        SettingSource.DEFAULT,
    ]
    # No Environment in the call: the layer is skipped and not reported.
    assert [c.source for c in none.candidates] == [
        SettingSource.ENV,
        SettingSource.WORKSPACE,
        SettingSource.DEFAULT,
    ]


@pytest.mark.req("FR-446")
async def test_an_environment_setting_wins_over_a_workspace_setting_and_loses_to_the_process(
    database: Database, workspace_id, monkeypatch, clean_environment_settings
) -> None:
    from app.platform import workspaces

    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await svc.set_workspace_setting(session, workspace_id, TRACE, 0.2)
    await _set(database, "uat", TRACE, 0.5)
    async with database.session() as session:
        resolution = await svc.resolve(session, Settings(), workspace_id, TRACE, "uat")
    assert (resolution.effective_value, resolution.resolved_from) == (
        0.5,
        SettingSource.ENVIRONMENT_SETTING,
    )

    monkeypatch.setenv("GIP_SETTING_RATING_TRACE_SAMPLE_RATE", "0.9")
    async with database.session() as session:
        for environment in ("uat", "prod"):
            resolution = await svc.resolve(session, Settings(), workspace_id, TRACE, environment)
            assert (resolution.effective_value, resolution.resolved_from) == (
                0.9,
                SettingSource.ENV,
            )


@pytest.mark.req("FR-446")
async def test_scope_is_enforced_on_both_write_paths(
    database: Database, workspace_id, environment_only_key, clean_environment_settings
) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as workspace_only:
            await svc.set_environment_setting(session, "uat", PSI, 0.2, None)
    assert workspace_only.value.code == "SETTING_INVALID"

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as environment_only:
            await svc.set_workspace_setting(session, workspace_id, environment_only_key, True)
    assert environment_only.value.code == "SETTING_INVALID"

    # An Environment-only key is accepted for an Environment.
    await _set(database, "uat", environment_only_key, True)


@pytest.mark.req("FR-447")
@pytest.mark.parametrize("value", ["not-a-number", 1.5, True])
async def test_an_invalid_environment_setting_is_refused_and_nothing_is_written(
    database: Database, value, clean_environment_settings
) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await svc.set_environment_setting(session, "uat", TRACE, value, None)
    assert exc.value.code == "SETTING_INVALID"
    async with database.session() as session:
        rows = (await session.execute(select(EnvironmentSettingRow))).scalars().all()
    assert rows == []


@pytest.mark.req("FR-431")
async def test_an_unknown_environment_is_a_404(database: Database) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await svc.set_environment_setting(session, "no-such-env", TRACE, 0.5, None)
    assert exc.value.code == "NOT_FOUND"


# --- the routes -----------------------------------------------------------------------------


@pytest.fixture
def client(api_settings: Settings):
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def admin_headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("admin")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def unprivileged_headers(workspace_id, principal, membership) -> dict[str, str]:
    await membership()
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


def _put(client, headers, slug, values):
    return client.put(
        f"/api/v1/environments/{slug}/settings", json={"values": values}, headers=headers
    )


async def _events(database: Database, workspace_id):
    async with database.session() as session:
        return (
            (
                await session.execute(
                    select(AuditEventRow)
                    .where(AuditEventRow.workspace_id == workspace_id)
                    .order_by(AuditEventRow.sequence)
                )
            )
            .scalars()
            .all()
        )


@pytest.mark.req("FR-431")
async def test_put_writes_the_value_and_audits_environment_key_old_and_new(
    client, database: Database, workspace_id, admin_headers, clean_environment_settings
) -> None:
    first = _put(client, admin_headers, "uat", {TRACE: 0.25})
    assert first.status_code == 200, first.text
    second = _put(client, admin_headers, "uat", {TRACE: 0.75})
    assert second.status_code == 200, second.text
    resolved = {r["key"]: r for r in second.json()}[TRACE]
    assert resolved["effective_value"] == 0.75
    assert resolved["resolved_from"] == "environment_setting"

    events = await _events(database, workspace_id)
    assert [e.action for e in events] == ["setting.updated", "setting.updated"]
    assert events[0].before == {"environment": "uat", "key": TRACE, "value": None}
    assert events[1].before == {"environment": "uat", "key": TRACE, "value": 0.25}
    assert events[1].after == {"environment": "uat", "key": TRACE, "value": 0.75}


@pytest.mark.req("FR-431")
async def test_a_put_without_its_audit_event_is_caught(
    client, monkeypatch, database: Database, workspace_id, admin_headers,
    clean_environment_settings,
) -> None:
    """Red on broken input: with the audit call a no-op the same assertion fails, so the
    audit test above is checking the write and not passing by construction."""

    async def _noop(*_a, **_k):
        return None

    monkeypatch.setattr(audit_module, "record", _noop)
    assert _put(client, admin_headers, "uat", {TRACE: 0.25}).status_code == 200
    assert await _events(database, workspace_id) == []


@pytest.mark.req("FR-431")
async def test_put_and_get_are_guarded_by_their_permissions(
    client, unprivileged_headers, clean_environment_settings
) -> None:
    denied = _put(client, unprivileged_headers, "uat", {TRACE: 0.25})
    assert denied.status_code == 403
    assert denied.json()["code"] == "PERMISSION_DENIED"
    read = client.get("/api/v1/environments/uat/settings", headers=unprivileged_headers)
    assert read.status_code == 403


@pytest.mark.req("FR-446")
async def test_get_reports_every_layers_candidate_for_the_environment(
    client, admin_headers, clean_environment_settings
) -> None:
    assert _put(client, admin_headers, "uat", {TRACE: 0.5}).status_code == 200
    body = client.get("/api/v1/environments/uat/settings", headers=admin_headers).json()
    trace = {r["key"]: r for r in body}[TRACE]
    assert [c["source"] for c in trace["candidates"]] == [
        "env",
        "environment_setting",
        "workspace",
        "default",
    ]
    prod = client.get("/api/v1/environments/prod/settings", headers=admin_headers).json()
    assert {r["key"]: r for r in prod}[TRACE]["resolved_from"] == "default"
    missing = client.get("/api/v1/environments/nope/settings", headers=admin_headers)
    assert missing.status_code == 404


@pytest.mark.req("FR-446")
async def test_put_refuses_a_workspace_only_key(client, admin_headers) -> None:
    refused = _put(client, admin_headers, "uat", {PSI: 0.2})
    assert refused.status_code == 422
    assert refused.json()["code"] == "SETTING_INVALID"
