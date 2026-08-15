"""The `dataset.*` job handlers, and the loop Phase 1a exits on (`01` §1.3).

Phase 1a's exit criterion is *a dataset version reaches `validated`, having been through
the failure loop at least once*. This file is that criterion as a test: ingest, validate,
fail, fix the data, re-validate, acknowledge, promote.

`execute_job` is driven directly rather than through a broker — the broker hop is W2's
test, and what these need to prove is what the handlers do.
"""

from __future__ import annotations

from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.db.models import DatasetVersionRow, RoleAssignmentRow, RoleRow, ValidationRuleSetRow
from app.db.session import Database
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import profiles as profile_service
from app.platform import rbac
from app.platform import validation as validation_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    DatasetStatus,
    JobKind,
    JobStatus,
    OverallOutcome,
    Principal,
    RuleOutcome,
    ScopeType,
    Severity,
    ValidationLayer,
    new_uuid7,
)

#: `read_tabular` reads every column as a string on purpose — inference happens from the
#: confirmed schema (FR-DATA-4), so a policy id of `007` does not become `7`. The
#: consequence is that a realistic ingestion **always** carries a cast recipe: without one
#: every numeric validation rule compares a string to a number and errors.
CAST_RECIPE = [
    {
        "step": "cast",
        "table": "policy_exposure",
        "params": {
            "columns": {
                "exposure_years": "float",
                "claim_count": "int",
                "claim_amount_minor": "int",
            }
        },
    }
]

CLEAN = (
    b"Policy ID,Exposure Years,Claim Count,Claim Amount Minor,Vehicle Group\n"
    + b"".join(
        f"P{i},1.0,{i % 2},{(i % 2) * 250000},G{i % 5}\n".encode() for i in range(300)
    )
)
#: One row with negative exposure — the failure the loop is supposed to catch.
DIRTY = CLEAN + b"P999,-1.0,0,0,G1\n"


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_data_handlers()


@pytest_asyncio.fixture
async def actuary(database: Database, workspace_id) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        for slug in ("analyst", "pricing_actuary", "approver"):
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


async def _seed_dataset_and_rules(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal
) -> UUID:
    """A dataset with a rule set that refuses non-positive exposure."""
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id

    from app.db.models import ValidationRuleRow

    async with database.unit_of_work() as session:
        rule = ValidationRuleRow(
            workspace_id=workspace_id,
            slug=f"exposure-positive-{new_uuid7().hex[-6:]}",
            version=1,
            layer=ValidationLayer.ACTUARIAL_SANITY.value,
            check="range",
            severity=Severity.FAIL.value,
            body={
                "target": {"table": "policy_exposure", "column": "exposure_years"},
                "params": {"min_exclusive": 0, "key_columns": ["policy_id"]},
                "scope": {},
                "tolerance": {},
                "message": "exposure must be positive",
                "rationale": "a non-positive exposure breaks every rate per unit time",
            },
            status="approved",
            authored_by=actor.id,
            approved_by=new_uuid7(),
            dry_run_report_id=new_uuid7(),
        )
        session.add(rule)
        await session.flush()
        session.add(
            ValidationRuleSetRow(
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                slug=str(dataset_id),
                version=1,
                body={"rule_ids": [str(rule.id)]},
                status="approved",
            )
        )
    return dataset_id


async def _ingest(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal,
    dataset_id: UUID, payload: bytes,
) -> UUID:
    """Upload, submit the job, run it, return the version id."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, payload, "text/csv")
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": "exposure.csv",
                "recipe": CAST_RECIPE,
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = (
            await session.execute(
                select(DatasetVersionRow)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()
        return row.id


async def _validate(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal,
    version_id: UUID,
) -> UUID:
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_version_id": str(version_id),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        reports = await validation_service.reports_for_version(
            session, workspace_id=workspace_id, version_id=version_id
        )
    return reports[0].id


@pytest.mark.req("FR-DATA-25")
async def test_ingestion_produces_a_version_and_its_profile(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """FR-DATA-25: profiling runs after a successful ingestion.

    In the same Job, not a second one — a separate profiling Job could be cancelled,
    leaving a version with no profile and nothing recording why.
    """
    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actuary)
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CLEAN
    )

    async with database.session() as session:
        profile = await profile_service.latest_profile(
            session, workspace_id=workspace_id, version_id=version_id
        )
    assert profile.row_count == 300
    assert {summary.column for summary in profile.one_ways} == {"vehicle_group"}
    assert profile.one_ways[0].rows[0].frequency is not None


@pytest.mark.req("FR-DATA-15")
async def test_the_failure_loop_then_validated(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """Phase 1a's exit criterion, end to end (`01` §1.3, FR-DATA-15, FR-DATA-17).

    A version with a negative exposure fails validation and **cannot** be promoted — no
    override, no force-fit. The fix is to the data, not to the verdict.
    """
    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actuary)

    bad_version = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, DIRTY
    )
    bad_report = await _validate(database, blob_store, workspace_id, actuary, bad_version)

    async with database.session() as session:
        report = await validation_service.load_report(
            session, workspace_id=workspace_id, report_id=bad_report
        )
    assert validation_service.overall_outcome(report) is OverallOutcome.FAIL
    assert any(r.outcome is RuleOutcome.FAIL for r in report.results)

    from app.errors import PlatformError

    async with database.unit_of_work() as session:
        await dataset_service.transition(
            session, workspace_id=workspace_id, actor=actuary,
            version_id=bad_version, to_status=DatasetStatus.VALIDATING,
        )
    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation_service.promote_using_report(
                session, workspace_id=workspace_id, actor=actuary,
                version_id=bad_version, report_id=bad_report,
            )
    assert excinfo.value.code == "VALIDATION_HAS_FAILURES"

    # The fix is to the data. A new version, because a version is immutable.
    good_version = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CLEAN
    )
    good_report = await _validate(database, blob_store, workspace_id, actuary, good_version)

    async with database.unit_of_work() as session:
        await dataset_service.transition(
            session, workspace_id=workspace_id, actor=actuary,
            version_id=good_version, to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        promoted = await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actuary,
            version_id=good_version, report_id=good_report,
        )
    assert promoted.status == DatasetStatus.VALIDATED.value

    # And the gate the whole module exists for now opens.
    async with database.session() as session:
        fittable = await dataset_service.fittable_or_refuse(
            session, workspace_id=workspace_id, version_id=good_version
        )
        assert fittable.id == good_version
        with pytest.raises(PlatformError) as refused:
            await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=bad_version
            )
    assert refused.value.code == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-DATA-9")
async def test_a_preparation_recipe_is_applied_during_ingestion(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """FR-DATA-9 and FR-DATA-14: applied *during* ingestion and stored with the version.

    Applying it afterwards would leave the parquet on the version disagreeing with the
    totals, profile and validation report that describe it.
    """
    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actuary)

    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, DIRTY, "text/csv")
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actuary.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": "exposure.csv",
                "recipe": [
                    *CAST_RECIPE,
                    {
                        "step": "filter_rows",
                        "table": "policy_exposure",
                        "params": {"expression": "exposure_years > 0"},
                    },
                ],
            },
            actuary,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        version = (
            await session.execute(
                select(DatasetVersionRow)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()
        profile = await profile_service.latest_profile(
            session, workspace_id=workspace_id, version_id=version.id
        )

    # The bad row was filtered by the recipe, so the version holds 300 and not 301.
    assert profile.row_count == 300
    assert version.derived_from is not None
    assert [step["step"] for step in version.derived_from["recipe"]] == [
        "cast",
        "filter_rows",
    ]
