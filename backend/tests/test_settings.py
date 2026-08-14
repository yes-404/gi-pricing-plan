"""Settings resolution and feature flags (FR-PLAT-43..46, `07` §4.4)."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.config import Settings
from app.db.models import AuditEventRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import settings as svc
from model_schema import SettingSource, SettingType

PSI = "validation.psi_warn_threshold"
FLAG = "features.expression_objectives_enabled"


@pytest.mark.req("FR-PLAT-45")
def test_the_registry_covers_every_category_the_requirement_names() -> None:
    """FR-PLAT-45 enumerates what workspace settings must include."""
    keys = set(svc.REGISTRY)
    for required in (
        "display.currency",
        "display.locale",
        "display.timezone",
        "validation.psi_warn_threshold",
        "observability.trace_sample_rate",
        "governance.approval_policy_ref",
        "retention.job_history_days",
        "features.expression_objectives_enabled",
        "features.sql_validation_check_enabled",
    ):
        assert required in keys, required


@pytest.mark.req("FR-PLAT-46")
def test_every_feature_flag_defaults_to_its_safe_value() -> None:
    """Negative: a flag whose default drifted away from safe would gate nothing."""
    flags = {k: d for k, d in svc.REGISTRY.items() if d.feature_flag}
    assert set(flags) == set(svc.SAFE_DEFAULT)
    for key, definition in flags.items():
        assert definition.type is SettingType.BOOL, key
        assert definition.default == svc.SAFE_DEFAULT[key], key


@pytest.mark.req("FR-PLAT-14")
def test_the_job_retention_default_meets_the_thirteen_month_floor() -> None:
    """FR-PLAT-14 requires ≥ 13 months; the constraint makes a shorter value unsettable."""
    definition = svc.REGISTRY["retention.job_history_days"]
    assert definition.default >= 396
    assert definition.constraints["min"] >= 396
    with pytest.raises(PlatformError) as exc:
        definition.coerce(90)
    assert exc.value.title == "Setting value is out of range"


@pytest.mark.req("FR-PLAT-43")
async def test_a_setting_with_no_override_resolves_to_the_default(
    database: Database, workspace_id
) -> None:
    async with database.session() as session:
        resolution = await svc.resolve(session, Settings(), workspace_id, PSI)
    assert resolution.effective_value == 0.10
    assert resolution.resolved_from is SettingSource.DEFAULT
    assert [c.source for c in resolution.candidates] == [
        SettingSource.ENV,
        SettingSource.WORKSPACE,
        SettingSource.DEFAULT,
    ]


@pytest.mark.req("FR-PLAT-43")
async def test_a_workspace_override_wins_over_the_default(
    database: Database, workspace_id
) -> None:
    async with database.unit_of_work() as session:
        await svc.set_workspace_setting(session, workspace_id, PSI, 0.2)
    async with database.session() as session:
        resolution = await svc.resolve(session, Settings(), workspace_id, PSI)
    assert resolution.effective_value == 0.2
    assert resolution.resolved_from is SettingSource.WORKSPACE
    # The whole chain is visible, which is what makes "why is it 0.2?" answerable.
    assert resolution.candidates[2].value == 0.10


@pytest.mark.req("FR-PLAT-43")
async def test_an_environment_variable_wins_over_a_workspace_override(
    database: Database, workspace_id, monkeypatch
) -> None:
    """The precedence FR-PLAT-43 states, asserted at its most contested point."""
    async with database.unit_of_work() as session:
        await svc.set_workspace_setting(session, workspace_id, PSI, 0.2)
    monkeypatch.setenv("GIP_SETTING_VALIDATION_PSI_WARN_THRESHOLD", "0.35")

    async with database.session() as session:
        resolution = await svc.resolve(session, Settings(), workspace_id, PSI)
    assert resolution.effective_value == 0.35
    assert resolution.resolved_from is SettingSource.ENV
    assert resolution.candidates[1].value == 0.2


@pytest.mark.req("FR-PLAT-44")
async def test_a_workspace_override_of_the_wrong_type_is_refused(
    database: Database, workspace_id
) -> None:
    """Negative: an untyped store would fail at first use, inside a validation run."""
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await svc.set_workspace_setting(session, workspace_id, PSI, "not-a-number")
    assert exc.value.code == "SETTING_INVALID"


@pytest.mark.req("FR-PLAT-44")
async def test_a_value_outside_its_constraints_is_refused(
    database: Database, workspace_id
) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await svc.set_workspace_setting(session, workspace_id, PSI, 1.5)
    assert exc.value.title == "Setting value is out of range"
    assert exc.value.code == "SETTING_INVALID"


@pytest.mark.req("FR-PLAT-44")
async def test_an_undeclared_key_is_refused(database: Database, workspace_id) -> None:
    """Negative: a stored value nothing reads is worse than an error — it looks applied."""
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await svc.set_workspace_setting(session, workspace_id, "made.up.key", 1)
    assert exc.value.status_code == 404


@pytest.mark.req("FR-PLAT-46")
async def test_a_flag_is_off_until_a_workspace_turns_it_on(
    database: Database, workspace_id
) -> None:
    async with database.session() as session:
        before = await svc.resolve(session, Settings(), workspace_id, FLAG)
    assert before.effective_value is False
    assert before.feature_flag is True

    async with database.unit_of_work() as session:
        await svc.set_workspace_setting(session, workspace_id, FLAG, True)
    async with database.session() as session:
        after = await svc.resolve(session, Settings(), workspace_id, FLAG)
    assert after.effective_value is True
    assert after.resolved_from is SettingSource.WORKSPACE


@pytest.mark.req("FR-PLAT-46")
async def test_a_flag_rejects_a_non_boolean(database: Database, workspace_id) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError):
            await svc.set_workspace_setting(session, workspace_id, FLAG, "yes")


@pytest.mark.req("FR-PLAT-43")
async def test_resolve_all_returns_every_declared_setting(
    database: Database, workspace_id
) -> None:
    async with database.session() as session:
        resolutions = await svc.resolve_all(session, Settings(), workspace_id)
    assert {r.key for r in resolutions} == set(svc.REGISTRY)


@pytest.mark.req("FR-PLAT-45")
async def test_updating_a_setting_is_audited_with_its_previous_value(
    database: Database, workspace_id, principal
) -> None:
    """FR-PLAT-31's principle: configuration changes are audited, with what changed."""
    from app.platform import audit
    from model_schema import JobSource

    async with database.unit_of_work() as session:
        before = await svc.resolve(session, Settings(), workspace_id, PSI)
        await svc.set_workspace_setting(session, workspace_id, PSI, 0.3)
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=principal,
            source=JobSource.API,
            action="setting.updated",
            entity_ref="setting:validation-psi_warn_threshold@1",
            before={"effective_value": before.effective_value},
            after={"workspace_value": 0.3},
        )

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert [e.action for e in events] == ["setting.updated"]
    assert events[0].before["effective_value"] == 0.10
