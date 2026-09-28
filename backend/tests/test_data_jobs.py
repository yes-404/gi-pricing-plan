"""The `dataset.*` job handlers, and the loop Phase 1a exits on (`01` §1.3).

Phase 1a's exit criterion is *a dataset version reaches `validated`, having been through
the failure loop at least once*. This file is that criterion as a test: ingest, validate,
fail, fix the data, re-validate, acknowledge, promote.

`execute_job` is driven directly rather than through a broker — the broker hop is WK-658's
test, and what these need to prove is what the handlers do.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.db.models import (
    DatasetVersionRow,
    JobRow,
    ProfileRow,
    RoleAssignmentRow,
    RoleRow,
    ValidationRuleSetRow,
    WorkspaceMemberRow,
)
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
#: confirmed schema (FR-29), so a policy id of `007` does not become `7`. The
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

#: `0.07` rather than a round number on purpose. Summed as binary floats, 300 of them give
#: 21.000000000000004; summed as `Decimal`, exactly 21.00. A totals test over `1.0` cannot
#: tell the two apart, and FR-10 is the difference.
CLEAN = (
    b"Policy ID,Exposure Years,Claim Count,Claim Amount Minor,Vehicle Group\n"
    + b"".join(
        f"P{i},0.07,{i % 2},{(i % 2) * 250000},G{i % 5}\n".encode() for i in range(300)
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
        # The workspace row must exist for the membership FK (FR-395).
        from app.platform import workspaces

        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await rbac.seed_builtin_roles(session, workspace_id)
        # Membership as well as roles (W6b-11): the dev caller resolves through the
        # memberships the database holds, so an actor that exists only as role
        # assignments can no longer reach the routes this file tests over HTTP.
        session.add(WorkspaceMemberRow(user_id=user.id, workspace_id=workspace_id))
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


@pytest.mark.req("FR-60")
@pytest.mark.req("FR-6")
@pytest.mark.req("FR-61")
async def test_ingestion_produces_a_version_and_its_profile(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """FR-60: profiling runs after a successful ingestion.

    In the same Job, not a second one — a separate profiling Job could be cancelled,
    leaving a version with no profile and nothing recording why.

    Also the assertion that `01` §4.7's "wired from the real profiling path, not left
    decorative" is true of `job_id` and `weight_column`. Both fields default — `None` and
    `"exposure_years"` — so a profile built by a handler that never passes them validates
    and stores exactly as one that does. Nothing but this test distinguishes the two, and
    `produced_by_job_id` (FR-6) is what makes a displayed number traceable to the
    computation behind it.
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

    # FR-6 — and specifically *this* Job's id, not merely some id. `is not None` would
    # pass on a handler that invented one; the profile has to carry the ingestion Job that
    # produced it, because that is the provenance link a reader follows back.
    async with database.session() as session:
        ingest_job_id = (
            await session.execute(
                select(JobRow.id)
                .where(JobRow.workspace_id == workspace_id)
                .where(JobRow.kind == JobKind.DATASET_INGEST)
            )
        ).scalar_one()
    assert profile.job_id == ingest_job_id
    # And the persisted *column*, which is what a lineage query reads — the assertion above
    # only proves the artifact body carries the id. `store_profile` takes `job_id`
    # separately from the profile it stores, so the column can be NULL while the body is
    # right; that is exactly the state this repository shipped until Task 6.
    async with database.session() as session:
        stored_job_id = (
            await session.execute(
                select(ProfileRow.job_id).where(
                    ProfileRow.dataset_version_id == version_id
                )
            )
        ).scalar_one()
    assert stored_job_id == ingest_job_id
    # FR-61. This one is a round-trip check, not a wiring check: `weight_column`
    # defaults to "exposure_years" and this fixture's exposure column is named that too, so
    # it would pass even if nothing recorded the argument. The wiring itself is proven in
    # pricing-core, by a test that profiles a frame whose exposure column is named
    # something else — the only arrangement that can tell the two apart.
    assert profile.weight_column == "exposure_years"


@pytest.mark.req("FR-42")
@pytest.mark.req("FR-52")
async def test_the_failure_loop_then_validated(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """Phase 1a's exit criterion, end to end (`01` §1.3, FR-42, FR-46).

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

    # No manual transition: `dataset.validate` opens `validating` and closes it. A failing
    # report now leaves the version `failed` (FR-52) rather than resting in a
    # transient state that reads as "still running".
    async with database.session() as session:
        row = await session.get(DatasetVersionRow, bad_version)
        assert row.status == DatasetStatus.FAILED.value

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

    # A passing report leaves the version `validating`: promotion is the actuary's act
    # (`01` §1.3), and a job that promoted on a pass would make the gate automatic.
    async with database.session() as session:
        row = await session.get(DatasetVersionRow, good_version)
        assert row.status == DatasetStatus.VALIDATING.value

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


@pytest.mark.req("FR-35")
async def test_a_preparation_recipe_is_applied_during_ingestion(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """FR-35 and FR-41: applied *during* ingestion and stored with the version.

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


@pytest.mark.req("FR-30")
async def test_an_ingested_version_reads_back_over_http(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """The round trip nothing exercised: ingest through the real path, then read the
    version back **through the API**.

    `GET /datasets/{slug}/versions/{version}` returned **500 on every ingested version**.
    `_store_table` writes `source_names` per table (FR-30), `DatasetTable` is
    `extra="forbid"` and did not declare it, so `DatasetVersion.model_validate` refused the
    row the platform had itself written.

    Nothing caught it because the layers were only ever tested apart: the API tests never
    fetched a version that had been ingested, the job tests read versions through the
    service rather than the route, and the frontend mocked `fetch`. It surfaced the first
    time a browser asked for a real one.
    """
    from backend.tests.conftest_db import test_database_url
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from app.api.deps import DEV_PRINCIPAL_HEADER
    from app.config import Environment, Settings
    from app.main import create_app

    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actuary)
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CLEAN
    )

    from app.db.models import DatasetRow

    async with database.session() as session:
        version = await session.get(DatasetVersionRow, version_id)
        slug = (await session.get(DatasetRow, version.dataset_id)).slug

    settings = Settings(
        environment=Environment.LOCAL, version="test", dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        response = client.get(
            f"/api/v1/datasets/{slug}/versions/{version.version}",
            headers={
                DEV_PRINCIPAL_HEADER: str(actuary.id),
                "Workspace-Id": str(workspace_id),
            },
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["version"] == version.version
    # The header the column came from, which normalisation is lossy about (FR-30).
    table = body["tables"][0]
    assert table["source_names"], "the source headers did not survive the round trip"
    assert table["row_count"] > 0


@pytest.mark.req("FR-31")
async def test_a_version_links_to_the_ingestion_run_that_made_it(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """FR-31 keeps the run whether it succeeded or failed — and the version must point
    at it, or "why is my row count short?" has no answer.

    `IngestionRunRow.id` carries a Python-side `default=new_uuid7`, which SQLAlchemy
    applies **at flush**. Reading `run.id` straight after `session.add(run)` therefore gave
    `None`, and every ingested version was written with a null link. Nothing noticed until
    `GET /dataset-versions/{id}/rejected` 404'd on a version that had demonstrably been
    ingested.
    """
    from app.db.models import IngestionRunRow

    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actuary)
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CLEAN
    )

    async with database.session() as session:
        version = await session.get(DatasetVersionRow, version_id)
        assert version.ingestion_run_id is not None, "the version does not name its run"
        run = await session.get(IngestionRunRow, version.ingestion_run_id)

    assert run is not None
    assert run.dataset_version_id == version_id, "the link does not point back"
    assert run.rows_read == run.rows_written + run.rows_rejected


@pytest.mark.req("FR-34")
async def test_ingestion_computes_the_version_totals_exactly(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """`01` §4.2's headline numbers, computed once and stored with the version.

    Exposure is summed as `Decimal` and stored as a string (FR-10). The fixture is 300
    rows at 0.07 years, chosen because binary floats sum them to 21.000000000000004 while
    `Decimal` gives exactly 21.00 — a totals test over round numbers cannot tell the two
    apart, and this one is the difference between the discipline holding and being decorative.
    """
    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actuary)
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CLEAN
    )

    async with database.session() as session:
        version = await session.get(DatasetVersionRow, version_id)

    assert version.totals is not None, "an ingested version has no totals"
    assert version.totals["exposure_years"] == "21.000000", version.totals
    assert Decimal(version.totals["exposure_years"]) == Decimal("21")
    assert version.totals["claim_count"] == 150
    assert version.totals["claim_amount_minor"] == 150 * 250_000
