"""FD-1744 limb (a): a recipe cell that does not parse is quarantined, never silently nulled.

Through a real `dataset.ingest` Job (`execute_job`) over the auditor's four rows plus `p5`
(`PL-1737`, "The fixture"). `p2` and `p3` fail the `cast` step, `p5` fails `parse_date`, `p1`
and `p4` are written — so `rows_read == 5`, `rows_rejected == 3`, `rows_written == 2`.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any

import polars as pl
import pytest
import pytest_asyncio
from sqlalchemy import select

from app.db.models import (
    DatasetVersionRow,
    IngestionRunRow,
    RoleAssignmentRow,
    RoleRow,
    WorkspaceMemberRow,
)
from app.db.session import Database
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import rbac
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    BlobRef,
    JobKind,
    JobStatus,
    Principal,
    ScopeType,
    new_uuid7,
)

CSV = (
    b"policy_id,exposure,claim_amount,start_date\n"
    b"p1,1.0,100.0,2024-01-15\n"
    b"p2,0.5,np.float64(1.0),2024-02-30\n"
    b"p3,1.0,abc,not-a-date\n"
    b"p4,0.75,250.5,2024-03-01\n"
    b"p5,1.0,80.0,2024-13-01\n"
)
RECIPE: list[dict[str, Any]] = [
    {"step": "cast", "params": {"columns": {"claim_amount": "float64"}}},
    {"step": "parse_date", "params": {"column": "start_date", "format": "%Y-%m-%d"}},
]


def assert_row_identity(run: IngestionRunRow) -> None:
    """The accounting identity, read from the run record alone (FR-31, FR-32; DP-S1 (i)).

    `rows_read - rows_rejected - sum(removed) + sum(added) == rows_written`, where a step's
    removed or added rows are its change in height net of its own quarantine. Shared by
    `test_data_jobs.py` and `test_ingestion.py` after their ingests (G5).
    """
    removed = added = 0
    for step in run.step_counts:
        delta = step["rows_out"] - (step["rows_in"] - step["rows_rejected"])
        removed += max(-delta, 0)
        added += max(delta, 0)
    assert run.rows_read - run.rows_rejected - removed + added == run.rows_written


def _steps(run: IngestionRunRow) -> list[tuple[Any, ...]]:
    return [(s["name"], s["rows_in"], s["rows_out"], s["rows_rejected"]) for s in run.step_counts]


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_data_handlers()


@pytest_asyncio.fixture
async def actor(database: Database, workspace_id) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
    async with database.unit_of_work() as session:
        from app.platform import workspaces

        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await rbac.seed_builtin_roles(session, workspace_id)
        session.add(WorkspaceMemberRow(user_id=user.id, workspace_id=workspace_id))
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "analyst"
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


async def _ingest(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal,
    payload: bytes, recipe: list[dict[str, Any]],
) -> tuple[DatasetVersionRow, IngestionRunRow]:
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id
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
                "recipe": recipe,
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        version = (
            await session.execute(
                select(DatasetVersionRow).where(DatasetVersionRow.dataset_id == dataset_id)
            )
        ).scalar_one()
        run = await session.get(IngestionRunRow, version.ingestion_run_id)
    assert run is not None
    return version, run


async def _table(blob_store: BlobStore, version: DatasetVersionRow, name: str) -> pl.DataFrame:
    entry = next(t for t in version.tables if t["name"] == name)
    body = await blob_store.read(BlobRef.model_validate(entry["blob"]))
    return pl.read_parquet(io.BytesIO(body))


@pytest.mark.req("FR-32")
async def test_unparseable_cells_are_quarantined_with_their_source_text(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R1 (and Acceptance 4): `_rejected` holds p2, p3, p5; the clean table holds p1, p4."""
    version, run = await _ingest(database, blob_store, workspace_id, actor, CSV, RECIPE)

    assert [t["name"] for t in version.tables] == ["policy_exposure", "_rejected"]
    clean = await _table(blob_store, version, "policy_exposure")
    assert clean["policy_id"].to_list() == ["p1", "p4"]

    rejected = (await _table(blob_store, version, "_rejected")).sort("policy_id")
    assert rejected["policy_id"].to_list() == ["p2", "p3", "p5"]
    assert rejected["claim_amount"].to_list() == ["np.float64(1.0)", "abc", "80.0"]
    assert rejected["start_date"].to_list() == ["2024-02-30", "not-a-date", "2024-13-01"]
    assert rejected["_reject_column"].to_list() == ["claim_amount", "claim_amount", "start_date"]
    assert rejected["_reject_step"].to_list() == ["cast", "cast", "parse_date"]

    assert (run.rows_read, run.rows_rejected, run.rows_written) == (5, 3, 2)
    assert _steps(run) == [
        ("cast", 5, 3, 2),
        ("parse_date", 3, 2, 1),
    ]
    assert_row_identity(run)


@pytest.mark.req("FR-32")
async def test_a_null_after_ingest_is_a_source_null_and_nothing_else(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R6: the bad-cell counts (2 and 3) on main become the source's empty cells (0 and 1)."""
    version, _ = await _ingest(database, blob_store, workspace_id, actor, CSV, RECIPE)
    clean = await _table(blob_store, version, "policy_exposure")
    assert clean["claim_amount"].null_count() == 0
    assert clean["start_date"].null_count() == 0

    emptied = CSV.replace(b"p1,1.0,100.0,", b"p1,1.0,,")
    version, run = await _ingest(database, blob_store, workspace_id, actor, emptied, RECIPE)
    clean = await _table(blob_store, version, "policy_exposure")
    assert clean["claim_amount"].null_count() == 1  # G1: p1's empty cell is a null, not a reject
    assert clean["policy_id"].to_list() == ["p1", "p4"]
    assert run.rows_rejected == 3
    assert_row_identity(run)


@pytest.mark.req("FR-32")
async def test_a_later_step_cannot_launder_a_coercion(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R3: `fill_null` after the cast must not resurrect p2, p3 or p5."""
    recipe = [*RECIPE, {"step": "fill_null", "params": {"column": "claim_amount", "value": 0}}]
    version, run = await _ingest(database, blob_store, workspace_id, actor, CSV, recipe)
    clean = await _table(blob_store, version, "policy_exposure")
    assert clean["policy_id"].to_list() == ["p1", "p4"]
    assert_row_identity(run)


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-31")
async def test_the_identity_holds_through_a_row_removing_step(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R7: 5 - 3 - 1 + 0 == 1."""
    recipe = [*RECIPE, {"step": "filter_rows", "params": {"expression": "claim_amount <= 200"}}]
    version, run = await _ingest(database, blob_store, workspace_id, actor, CSV, recipe)
    clean = await _table(blob_store, version, "policy_exposure")
    assert clean["policy_id"].to_list() == ["p1"]
    assert _steps(run) == [
        ("cast", 5, 3, 2),
        ("parse_date", 3, 2, 1),
        ("filter_rows", 2, 1, 0),
    ]
    assert (run.rows_read, run.rows_rejected, run.rows_written) == (5, 3, 1)
    assert run.rows_written == 5 - 3 - 1 + 0
    assert_row_identity(run)


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-31")
async def test_the_identity_holds_on_the_g2_seed_recipe(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R8a: the freMTPL2 seed's own version-2 recipe over a six-row CSV (never a copy)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"))
    try:
        from seed import MAX_EXPOSURE, NUMERIC, RENAMES, recipe
    finally:
        sys.path.pop(0)

    source_name = {target: source for source, target in RENAMES.items()}
    header = ["IDpol", *(source_name.get(column, column) for column in NUMERIC)]
    over = float(MAX_EXPOSURE) + 1.0
    rows = []
    for index in range(6):
        values = {column: "3" if kind == "int" else "0.5" for column, kind in NUMERIC.items()}
        if index < 2:
            values["exposure_years"] = str(over)
        rows.append(",".join([str(index + 1), *(values[column] for column in NUMERIC)]))
    payload = ("\n".join([",".join(header), *rows]) + "\n").encode()

    _, run = await _ingest(
        database, blob_store, workspace_id, actor, payload,
        recipe(drop_implausible_exposure=True),
    )
    assert (run.rows_read, run.rows_rejected, run.rows_written) == (6, 0, 4)
    assert run.rows_written == 6 - 0 - 2 + 0
    assert_row_identity(run)


# -- limb (b): validation gives the quarantined cells a verdict (R4, R5) -------------------

_T = {"table": "policy_exposure"}
_RULES: dict[str, tuple[str, str, dict[str, Any], dict[str, Any]]] = {
    # slug: (layer, check, target, params)
    "dtype": (
        "structural", "dtype_match", _T,
        {"columns": {"claim_amount": "float64", "start_date": "date"}},
    ),
    "datep": ("structural", "date_parsed", _T, {"columns": ["start_date"]}),
    "cols": (
        "structural", "column_presence", _T,
        {"columns": ["policy_id", "claim_amount", "start_date"]},
    ),
    "claim-nonneg": (
        "actuarial_sanity", "range", {"table": "policy_exposure", "column": "claim_amount"},
        {"min_inclusive": 0, "key_columns": ["policy_id"]},
    ),
    "reject-rate": ("structural", "reject_rate", _T, {}),
}


async def _validate_with(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal,
    version: DatasetVersionRow, severities: dict[str, str],
):
    """Approve the named rules at the given severities as the dataset's Rule Set, validate."""
    from backend.tests.approved_rows import add_approved

    from app.db.models import ValidationRuleRow, ValidationRuleSetRow
    from app.platform import validation as validation_service

    async with database.unit_of_work() as session:
        rule_ids = []
        for slug, severity in severities.items():
            layer, check, target, params = _RULES[slug]
            rule = ValidationRuleRow(
                workspace_id=workspace_id, slug=f"{slug}-{new_uuid7().hex[-6:]}", version=1,
                layer=layer, check=check, severity=severity,
                body={"target": target, "params": params, "scope": {}, "tolerance": {},
                      "message": slug, "rationale": slug},
                status="approved", authored_by=actor.id, approved_by=new_uuid7(),
                dry_run_report_id=new_uuid7(),
            )
            await add_approved(session, rule)
            rule_ids.append(str(rule.id))
        await add_approved(
            session,
            ValidationRuleSetRow(
                workspace_id=workspace_id, dataset_id=version.dataset_id,
                slug=str(version.dataset_id), version=1, body={"rule_ids": rule_ids},
                status="approved",
            ),
        )
        job = await job_service.submit(
            session, JobKind.DATASET_VALIDATE,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "dataset_version_id": str(version.id)},
            actor, workspace_id=workspace_id,
        )
    await execute_job(database, job.id, blob_store)
    async with database.session() as session:
        report_id = (
            await validation_service.reports_for_version(
                session, workspace_id=workspace_id, version_id=version.id
            )
        )[0].id
        return await validation_service.load_report(
            session, workspace_id=workspace_id, report_id=report_id
        )


def _result(report, slug_prefix: str):
    rule_slugs = {r.rule_id: r for r in report.results}
    return next(r for r in rule_slugs.values() if r.rule_slug.startswith(slug_prefix))


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-46")
async def test_validation_fails_a_version_whose_cells_were_quarantined(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R4: the report is overall `fail`, with the three verdicts of Acceptance 8."""
    from model_schema import OverallOutcome

    version, _ = await _ingest(database, blob_store, workspace_id, actor, CSV, RECIPE)
    report = await _validate_with(
        database, blob_store, workspace_id, actor, version, dict.fromkeys(_RULES, "fail")
    )
    assert report.overall is OverallOutcome.FAIL
    assert _result(report, "reject-rate").measured["rejected_rows"] == 3
    assert _result(report, "reject-rate").measured["rows_read"] == 5
    assert _result(report, "dtype").measured["coerced_cells"] == {
        "claim_amount": 2, "start_date": 1,
    }
    assert _result(report, "datep").measured["coerced_cells"] == {"start_date": 1}


@pytest.mark.req("FR-46")
async def test_the_declared_severity_decides_without_reject_rate(
    database: Database, blob_store: BlobStore, workspace_id, actor
) -> None:
    """R5: with `reject-rate` out of the Rule Set, `warn` gives a warning verdict that blocks
    promotion until acknowledged, and `fail` gives `fail`."""
    from app.errors import PlatformError
    from app.platform import validation as validation_service
    from model_schema import OverallOutcome

    version, _ = await _ingest(database, blob_store, workspace_id, actor, CSV, RECIPE)
    report = await _validate_with(
        database, blob_store, workspace_id, actor, version, {"dtype": "warn", "datep": "warn"}
    )
    assert report.overall is OverallOutcome.PASS_WITH_WARNINGS

    # The report row is stored; promotion is refused while the warnings are unacknowledged.
    async with database.session() as session:
        report_id = (
            await validation_service.reports_for_version(
                session, workspace_id=workspace_id, version_id=version.id
            )
        )[0].id
    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation_service.promote_using_report(
                session, workspace_id=workspace_id, actor=actor,
                version_id=version.id, report_id=report_id,
            )
    assert excinfo.value.code == "WARN_NOT_ACKNOWLEDGED"

    version, _ = await _ingest(database, blob_store, workspace_id, actor, CSV, RECIPE)
    report = await _validate_with(
        database, blob_store, workspace_id, actor, version, {"dtype": "fail", "datep": "warn"}
    )
    assert report.overall is OverallOutcome.FAIL
