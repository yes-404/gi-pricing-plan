"""Stored validation reports, acknowledgements and promotion (`01` §3.3, §4.6)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select

from app.db.models import AuditEventRow, RoleAssignmentRow, RoleRow, ValidationReportRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets, profiles, rbac, validation
from model_schema import (
    ActorKind,
    DatasetStatus,
    OverallOutcome,
    Principal,
    Profile,
    RuleOutcome,
    ScopeType,
    Severity,
    ValidationLayer,
    ValidationReport,
    new_uuid7,
)
from model_schema.validation import RuleResult


async def _principal_with_role(database: Database, workspace_id, slug: str) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display=f"{slug}@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == slug
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id, principal_kind="user", principal_id=user.id,
                role_id=role.id, scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return user


def _result(outcome: RuleOutcome, *, rule_id: UUID | None = None) -> RuleResult:
    return RuleResult(
        rule_id=rule_id or uuid4(),
        rule_slug=f"rule-{outcome.value}",
        rule_version=1,
        layer=ValidationLayer.STRUCTURAL,
        severity=Severity.WARN if outcome is RuleOutcome.WARN else Severity.FAIL,
        outcome=outcome,
        detail=f"a {outcome.value}",
    )


def _report(version_id: UUID, *results: RuleResult) -> ValidationReport:
    started = datetime.now(UTC)
    return ValidationReport(
        id=uuid4(),
        dataset_version_id=version_id,
        rule_set_id=uuid4(),
        rule_set_version=3,
        started_at=started,
        finished_at=started + timedelta(seconds=2),
        results=tuple(results),
    )


async def _version(database: Database, workspace_id, actor: Principal) -> UUID:
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        version = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset.id
        )
        return version.id


@pytest.mark.req("FR-DATA-20")
@pytest.mark.parametrize(
    ("outcomes", "expected"),
    [
        ((RuleOutcome.PASS,), OverallOutcome.PASS),
        ((RuleOutcome.PASS, RuleOutcome.WARN), OverallOutcome.PASS_WITH_WARNINGS),
        ((RuleOutcome.WARN, RuleOutcome.ERROR), OverallOutcome.ERROR),
        ((RuleOutcome.FAIL, RuleOutcome.ERROR), OverallOutcome.FAIL),
        ((RuleOutcome.PASS, RuleOutcome.FAIL), OverallOutcome.FAIL),
    ],
)
def test_overall_outcome_follows_the_rule_results_alone(
    outcomes: tuple[RuleOutcome, ...], expected: OverallOutcome
) -> None:
    """`01` §4.6 as amended: `overall` is a function of the results and nothing else.

    Notably `(warn, error)` is `error` and not `pass_with_warnings` — a rule that could not
    run did not check the thing it exists to check.
    """
    report = _report(uuid4(), *(_result(o) for o in outcomes))
    assert validation.overall_outcome(report) is expected


@pytest.mark.req("FR-DATA-15")
async def test_a_stored_report_reads_back_byte_identical(
    database: Database, workspace_id
) -> None:
    """NFR-DATA-5 requires byte-identical bodies; that is only checkable if storage is
    lossless. A report reshaped on the way in or out is not the evidence that was written.
    """
    actor = await _principal_with_role(database, workspace_id, "analyst")
    version_id = await _version(database, workspace_id, actor)
    report = _report(version_id, _result(RuleOutcome.PASS), _result(RuleOutcome.WARN))

    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actor, report=report
        )
    async with database.session() as session:
        restored = await validation.load_report(
            session, workspace_id=workspace_id, report_id=report.id
        )
    assert restored.model_dump_json() == report.model_dump_json()


@pytest.mark.req("FR-DATA-17")
async def test_an_analyst_cannot_acknowledge_a_warning(
    database: Database, workspace_id
) -> None:
    """FR-DATA-17 puts the acknowledgement with an actuary. An analyst who could
    acknowledge could clear the way to `validated` alone, which is the whole control."""
    analyst = await _principal_with_role(database, workspace_id, "analyst")
    version_id = await _version(database, workspace_id, analyst)
    warn = _result(RuleOutcome.WARN)
    report = _report(version_id, warn)
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=analyst, report=report
        )

    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.acknowledge(
                session, workspace_id=workspace_id, actor=analyst,
                report_id=report.id, rule_id=warn.rule_id, justification="looks fine",
            )
    assert excinfo.value.code == "ACKNOWLEDGE_FORBIDDEN_ROLE"


@pytest.mark.req("FR-DATA-17")
async def test_a_failing_rule_cannot_be_acknowledged(
    database: Database, workspace_id
) -> None:
    """`01` §1.3: there is no override. Acknowledgement is for warnings only — if a `fail`
    could be waved through, the gate would be advisory."""
    actuary = await _principal_with_role(database, workspace_id, "pricing_actuary")
    version_id = await _version(database, workspace_id, actuary)
    failed = _result(RuleOutcome.FAIL)
    report = _report(version_id, failed)
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actuary, report=report
        )

    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.acknowledge(
                session, workspace_id=workspace_id, actor=actuary,
                report_id=report.id, rule_id=failed.rule_id, justification="we accept it",
            )
    assert excinfo.value.status_code == 409


@pytest.mark.req("FR-DATA-18")
async def test_one_acknowledgement_per_report_and_rule(
    database: Database, workspace_id
) -> None:
    """FR-DATA-18 scopes an acknowledgement to `(version, rule, report)`. The unique
    constraint is what makes that a fact rather than an intention."""
    actuary = await _principal_with_role(database, workspace_id, "pricing_actuary")
    version_id = await _version(database, workspace_id, actuary)
    warn = _result(RuleOutcome.WARN)
    report = _report(version_id, warn)
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actuary, report=report
        )
    async with database.unit_of_work() as session:
        await validation.acknowledge(
            session, workspace_id=workspace_id, actor=actuary, report_id=report.id,
            rule_id=warn.rule_id, justification="mix shift is expected after the rate change",
        )

    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.acknowledge(
                session, workspace_id=workspace_id, actor=actuary, report_id=report.id,
                rule_id=warn.rule_id, justification="again",
            )
    assert excinfo.value.status_code == 409


@pytest.mark.req("FR-DATA-17")
async def test_promotion_refuses_until_every_warning_is_acknowledged(
    database: Database, workspace_id
) -> None:
    """The gate, end to end (`01` §1.3, FR-DATA-17): two warnings, one acknowledged, and
    the version stays out of `validated` until the second is too."""
    actuary = await _principal_with_role(database, workspace_id, "pricing_actuary")
    version_id = await _version(database, workspace_id, actuary)
    first, second = _result(RuleOutcome.WARN), _result(RuleOutcome.WARN)
    report = _report(version_id, first, second)

    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actuary, report=report
        )
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actuary, version_id=version_id,
            to_status=DatasetStatus.VALIDATING,
        )

    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.promote_using_report(
                session, workspace_id=workspace_id, actor=actuary,
                version_id=version_id, report_id=report.id,
            )
    assert excinfo.value.code == "WARN_NOT_ACKNOWLEDGED"

    async with database.unit_of_work() as session:
        for warn in (first, second):
            await validation.acknowledge(
                session, workspace_id=workspace_id, actor=actuary, report_id=report.id,
                rule_id=warn.rule_id, justification="reviewed against last quarter",
            )
    async with database.unit_of_work() as session:
        promoted = await validation.promote_using_report(
            session, workspace_id=workspace_id, actor=actuary,
            version_id=version_id, report_id=report.id,
        )
    assert promoted.status == DatasetStatus.VALIDATED.value
    assert promoted.validation_report_id == report.id


@pytest.mark.req("FR-DATA-15")
async def test_a_report_cannot_promote_a_version_it_did_not_validate(
    database: Database, workspace_id
) -> None:
    """Promoting on another version's report would validate data nobody checked."""
    actuary = await _principal_with_role(database, workspace_id, "pricing_actuary")
    checked = await _version(database, workspace_id, actuary)
    other = await _version(database, workspace_id, actuary)
    report = _report(checked, _result(RuleOutcome.PASS))
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actuary, report=report
        )

    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.promote_using_report(
                session, workspace_id=workspace_id, actor=actuary,
                version_id=other, report_id=report.id,
            )
    assert excinfo.value.status_code == 409


@pytest.mark.req("NFR-DATA-8")
async def test_an_acknowledgement_is_audited_with_its_justification(
    database: Database, workspace_id
) -> None:
    """NFR-DATA-8: acknowledgements emit an audit event with before/after. The
    justification is the point — an unexplained decision to model on warned data is what
    the audit exists to prevent."""
    actuary = await _principal_with_role(database, workspace_id, "pricing_actuary")
    version_id = await _version(database, workspace_id, actuary)
    warn = _result(RuleOutcome.WARN)
    report = _report(version_id, warn)
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actuary, report=report
        )
    async with database.unit_of_work() as session:
        await validation.acknowledge(
            session, workspace_id=workspace_id, actor=actuary, report_id=report.id,
            rule_id=warn.rule_id, justification="seasonal, confirmed against 2023",
        )

    async with database.session() as session:
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "validation_warning.acknowledged",
                )
            )
        ).scalar_one()
    assert event.before == {"rule_id": str(warn.rule_id), "acknowledged": False}
    assert event.after["acknowledged"] is True
    assert event.justification == "seasonal, confirmed against 2023"


@pytest.mark.req("FR-DATA-27")
async def test_a_one_way_is_read_from_storage_and_a_missing_one_is_a_refusal(
    database: Database, workspace_id
) -> None:
    """FR-DATA-27: one-ways are read, never computed on request. A fallback that computed
    the missing column would meet NFR-DATA-4 in testing and miss it in production, so a
    column with no stored one-way is a 404 that names the ones there are."""
    import polars as pl

    from pricing_core.data.profile import profile_frame

    actor = await _principal_with_role(database, workspace_id, "analyst")
    version_id = await _version(database, workspace_id, actor)
    frame = pl.DataFrame(
        {
            "vehicle_group": ["G1", "G2"] * 150,
            "postcode_area": ["AB", "CD"] * 150,
            "exposure_years": [0.5] * 300,
            "claim_count": [1, 0] * 150,
            "claim_amount_minor": [250_000, 0] * 150,
        }
    )
    profile = profile_frame(
        frame, dataset_version_id=version_id, one_way_columns=["vehicle_group"]
    )
    async with database.unit_of_work() as session:
        await profiles.store_profile(
            session, workspace_id=workspace_id, actor=actor, profile=profile
        )

    async with database.session() as session:
        summary = await profiles.one_way_of(
            session, workspace_id=workspace_id, version_id=version_id,
            column="vehicle_group",
        )
        assert {row.level for row in summary.rows} == {"G1", "G2"}

        with pytest.raises(PlatformError) as excinfo:
            await profiles.one_way_of(
                session, workspace_id=workspace_id, version_id=version_id,
                column="postcode_area",
            )
    assert excinfo.value.status_code == 404
    assert "vehicle_group" in excinfo.value.detail


@pytest.mark.req("FR-DATA-25")
async def test_storing_a_profile_points_the_version_at_it(
    database: Database, workspace_id
) -> None:
    """"The profile of @12" must be a lookup, not a search with a tie-break."""
    import polars as pl

    from pricing_core.data.profile import profile_frame

    actor = await _principal_with_role(database, workspace_id, "analyst")
    version_id = await _version(database, workspace_id, actor)
    profile = profile_frame(
        pl.DataFrame({"exposure_years": [1.0] * 10}), dataset_version_id=version_id
    )
    async with database.unit_of_work() as session:
        await profiles.store_profile(
            session, workspace_id=workspace_id, actor=actor, profile=profile
        )
    async with database.session() as session:
        stored = await profiles.latest_profile(
            session, workspace_id=workspace_id, version_id=version_id
        )
    assert isinstance(stored, Profile)
    assert stored.id == profile.id


@pytest.mark.req("FR-DATA-20")
async def test_report_summary_columns_match_the_body(
    database: Database, workspace_id
) -> None:
    """The columns beside the body are indexes. If they disagree with it, a list view and
    a detail view of the same report tell different stories."""
    actor = await _principal_with_role(database, workspace_id, "analyst")
    version_id = await _version(database, workspace_id, actor)
    report = _report(
        version_id,
        _result(RuleOutcome.PASS), _result(RuleOutcome.WARN),
        _result(RuleOutcome.WARN), _result(RuleOutcome.FAIL),
    )
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actor, report=report
        )
    async with database.session() as session:
        row = (
            await session.execute(
                select(ValidationReportRow).where(ValidationReportRow.id == report.id)
            )
        ).scalar_one()
    assert (row.rule_count, row.fail_count, row.warn_count, row.error_count) == (4, 1, 2, 0)
    assert row.overall == OverallOutcome.FAIL.value


@pytest.mark.req("FR-DATA-18")
async def test_the_presented_report_says_which_warning_was_acknowledged(
    database: Database, workspace_id
) -> None:
    """`01` §5.3 requires "warnings needing acknowledgement" as a band above the fold.

    A count of outstanding warnings cannot render that: with one warning a client could
    infer which, with three it cannot. The presented report carries the acknowledgement on
    the rule it belongs to, with who and why.

    The **stored** artifact is untouched — `load_report` still returns it byte for byte,
    which NFR-DATA-5 depends on. This is the read edge, where an acknowledgement is a fact
    *about* the report rather than inside it.
    """
    actuary = await _principal_with_role(database, workspace_id, "pricing_actuary")
    version_id = await _version(database, workspace_id, actuary)
    first, second = _result(RuleOutcome.WARN), _result(RuleOutcome.WARN)
    report = _report(version_id, first, second, _result(RuleOutcome.PASS))

    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actuary, report=report
        )
    async with database.unit_of_work() as session:
        await validation.acknowledge(
            session, workspace_id=workspace_id, actor=actuary, report_id=report.id,
            rule_id=second.rule_id, justification="seasonal, confirmed against 2023",
        )

    async with database.session() as session:
        presented = await validation.load_report_view(
            session, workspace_id=workspace_id, report_id=report.id
        )
        stored = await validation.load_report(
            session, workspace_id=workspace_id, report_id=report.id
        )

    by_rule = {result.rule_id: result for result in presented.results}
    assert by_rule[second.rule_id].acknowledgement is not None
    assert by_rule[second.rule_id].acknowledgement.justification == (
        "seasonal, confirmed against 2023"
    )
    assert by_rule[second.rule_id].acknowledgement.user_id == actuary.id
    # The one still needing attention is distinguishable from the one that had it.
    assert by_rule[first.rule_id].acknowledgement is None

    # And the artifact itself is unchanged, which NFR-DATA-5 compares byte for byte.
    assert all(result.acknowledgement is None for result in stored.results)
