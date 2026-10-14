"""FD 8040: a recipe cell that does not parse is never silently nulled (FR-32), and
validation gives it a verdict (VR-STR-2, VR-STR-5, FR-46).

Every test here drives `execute_job` over the five-row fixture, the auditor's four rows plus
`p5` (PL 8042, "The fixture"): `p2` and `p3` fail the `cast` of `claim_amount`, `p5` fails the
`parse_date` of `start_date`, `p1` and `p4` are written. Read as strings, no cell is
genuinely empty, so after ingest every `null_count` is 0.

The accounting identity (the 2026-10-14 12:31:22 BST entry), for every recipe:
`rows_read - rows_rejected - Σ removed + Σ added == rows_written`, each step's heights being
recorded on the run as `step_counts` (DP-S1 (i)).
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

import polars as pl
import pytest
import pytest_asyncio
from backend.tests.approved_rows import add_approved
from sqlalchemy import select

from app.db.models import (
    BlobRow,
    DatasetVersionRow,
    IngestionRunRow,
    RoleAssignmentRow,
    RoleRow,
    ValidationRuleRow,
    ValidationRuleSetRow,
    WorkspaceMemberRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import rbac
from app.platform import validation as validation_service
from app.platform.blobs import BlobStore, to_ref
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
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

_ROW_P5 = b"p5,1.0,80.0,2024-13-01\n"  # a good number and a bad date
CSV = (
    b"policy_id,exposure,claim_amount,start_date\n"
    b"p1,1.0,100.0,2024-01-15\n"
    b"p2,0.5,np.float64(1.0),2024-02-30\n"  # unparseable number and impossible date
    b"p3,1.0,abc,not-a-date\n"  # unparseable number and unparseable date
    b"p4,0.75,250.5,2024-03-01\n" + _ROW_P5
)
RECIPE: list[dict[str, Any]] = [
    {"step": "cast", "params": {"columns": {"claim_amount": "float64"}}},
    {"step": "parse_date", "params": {"column": "start_date", "format": "%Y-%m-%d"}},
]
FILTER = {"step": "filter_rows", "params": {"expression": "claim_amount <= 200"}}

T = {"table": "policy_exposure"}
#: `(slug, layer, check, target, params)`, the auditor's five rules; severity is per test.
RULES = [
    (
        "dtype",
        ValidationLayer.STRUCTURAL,
        "dtype_match",
        T,
        {"columns": {"claim_amount": "float64", "start_date": "date"}},
    ),
    ("datep", ValidationLayer.STRUCTURAL, "date_parsed", T, {"columns": ["start_date"]}),
    (
        "cols",
        ValidationLayer.STRUCTURAL,
        "column_presence",
        T,
        {"columns": ["policy_id", "claim_amount", "start_date"]},
    ),
    (
        "claim-nonneg",
        ValidationLayer.ACTUARIAL_SANITY,
        "range",
        {"table": "policy_exposure", "column": "claim_amount"},
        {"min_inclusive": 0, "key_columns": ["policy_id"]},
    ),
    ("reject-rate", ValidationLayer.STRUCTURAL, "reject_rate", T, {}),
]


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_data_handlers()


@pytest_asyncio.fixture
async def actuary(database: Database, workspace_id) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
    async with database.unit_of_work() as session:
        from app.platform import workspaces

        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await rbac.seed_builtin_roles(session, workspace_id)
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
                    workspace_id=workspace_id,
                    principal_kind="user",
                    principal_id=user.id,
                    role_id=role.id,
                    scope_type=ScopeType.WORKSPACE.value,
                )
            )
    return user


async def _dataset(
    database: Database,
    workspace_id,
    actor: Principal,
    severities: dict[str, Severity] | None = None,
    omit: tuple[str, ...] = (),
    suffix: str = "",
) -> UUID:
    """A dataset with the fixture's rules approved as its Rule Set (`severities` overrides
    the default `fail`; `omit` leaves a rule out of the set)."""
    severities = severities or {}
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id
    async with database.unit_of_work() as session:
        rule_ids: list[str] = []
        for slug, layer, check, target, params in RULES:
            if slug in omit:
                continue
            rule = ValidationRuleRow(
                workspace_id=workspace_id,
                slug=f"{slug}{suffix}",
                version=1,
                layer=layer.value,
                check=check,
                severity=severities.get(slug, Severity.FAIL).value,
                body={
                    "target": target,
                    "params": params,
                    "scope": {},
                    "tolerance": {},
                    "message": slug,
                    "rationale": "FD 8040",
                },
                status="approved",
                authored_by=actor.id,
                approved_by=new_uuid7(),
                dry_run_report_id=new_uuid7(),
            )
            await add_approved(session, rule)
            rule_ids.append(str(rule.id))
        await add_approved(
            session,
            ValidationRuleSetRow(
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                slug=str(dataset_id),
                version=1,
                body={"rule_ids": rule_ids},
                status="approved",
            ),
        )
    return dataset_id


async def _ingest(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    actor: Principal,
    dataset_id: UUID,
    payload: bytes,
    recipe: list[dict[str, Any]],
) -> UUID:
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
                "recipe": recipe,
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        return (
            await session.execute(
                select(DatasetVersionRow.id)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()


async def _tables(
    database: Database, blob_store: BlobStore, version_id: UUID
) -> dict[str, pl.DataFrame]:
    async with database.session() as session:
        version = await session.get(DatasetVersionRow, version_id)
        out: dict[str, pl.DataFrame] = {}
        for entry in version.tables:
            blob = await session.get(BlobRow, entry["blob"]["sha256"])
            out[entry["name"]] = pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(blob))))
    return out


async def _run(database: Database, version_id: UUID) -> IngestionRunRow:
    async with database.session() as session:
        return (
            await session.execute(
                select(IngestionRunRow).where(IngestionRunRow.dataset_version_id == version_id)
            )
        ).scalar_one()


def assert_the_rows_balance(run: IngestionRunRow) -> list[dict[str, Any]]:
    """The accounting identity, read from the run record (G5; the 12:31:22 entry).

    A step's own removed/added rows are derived from its recorded heights net of its
    quarantine: `d = rows_out - (rows_in - rows_rejected)`.
    """
    steps = getattr(run, "step_counts", None)
    assert steps is not None, "the ingestion run records no step_counts"
    removed = added = 0
    for step in steps:
        d = step["rows_out"] - (step["rows_in"] - step["rows_rejected"])
        removed += max(-d, 0)
        added += max(d, 0)
    assert run.rows_read - run.rows_rejected - removed + added == run.rows_written
    return steps


def _steps(run: IngestionRunRow) -> list[tuple[str, int, int, int]]:
    steps = getattr(run, "step_counts", None)
    assert steps is not None, "the ingestion run records no step_counts"
    return [(s["name"], s["rows_in"], s["rows_out"], s["rows_rejected"]) for s in steps]


# -- limb (a): the quarantine ----------------------------------------------------------


@pytest.mark.req("FR-32")
async def test_unparseable_cells_are_quarantined_not_silently_nulled(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R1. On main the version's only table is `policy_exposure`."""
    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(database, blob_store, workspace_id, actuary, dataset_id, CSV, RECIPE)
    tables = await _tables(database, blob_store, version_id)

    assert "_rejected" in tables
    rejected = tables["_rejected"].sort("policy_id")
    assert rejected["policy_id"].to_list() == ["p2", "p3", "p5"]
    assert rejected["claim_amount"].to_list() == ["np.float64(1.0)", "abc", "80.0"]
    assert rejected["start_date"].to_list() == ["2024-02-30", "not-a-date", "2024-13-01"]
    assert rejected["_reject_column"].to_list() == ["claim_amount", "claim_amount", "start_date"]
    assert rejected["_reject_step"].to_list() == ["cast", "cast", "parse_date"]
    assert sorted(tables["policy_exposure"]["policy_id"].to_list()) == ["p1", "p4"]

    run = await _run(database, version_id)
    assert (run.rows_read, run.rows_rejected, run.rows_written) == (5, 3, 2)
    assert _steps(run) == [("cast", 5, 3, 2), ("parse_date", 3, 2, 1)]
    assert_the_rows_balance(run)


@pytest.mark.req("FR-32")
async def test_after_ingest_a_null_is_a_source_null_and_nothing_else(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R6. On main `claim_amount` reads 2 nulls and `start_date` 3: the bad-cell counts."""
    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(database, blob_store, workspace_id, actuary, dataset_id, CSV, RECIPE)
    written = (await _tables(database, blob_store, version_id))["policy_exposure"]
    assert written["claim_amount"].null_count() == 0
    assert written["start_date"].null_count() == 0

    # The source's one genuinely empty cell is the one null, never the bad-cell count.
    with_empty = CSV.replace(b"p1,1.0,100.0,", b"p1,1.0,,")
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, with_empty, RECIPE
    )
    written = (await _tables(database, blob_store, version_id))["policy_exposure"]
    assert written["claim_amount"].null_count() == 1


@pytest.mark.req("FR-32")
async def test_a_source_null_makes_no_reject_row(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """G1, green at base and at head: `""` and `"NA"` are null at read (`formats.py`), so
    they are written as null and are not a coercion."""
    csv = b"policy_id,exposure,claim_amount,start_date\np1,1.0,,2024-01-15\np4,0.75,NA,2024-03-01\n"
    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(database, blob_store, workspace_id, actuary, dataset_id, csv, RECIPE)
    tables = await _tables(database, blob_store, version_id)

    assert "_rejected" not in tables
    assert tables["policy_exposure"]["claim_amount"].null_count() == 2


@pytest.mark.req("FR-32")
async def test_a_later_step_cannot_launder_a_coercion(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R3. On main `p2` and `p3` are written with `claim_amount == 0.0`."""
    fill = {"step": "fill_null", "params": {"column": "claim_amount", "value": 0}}
    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CSV, [*RECIPE, fill]
    )
    written = (await _tables(database, blob_store, version_id))["policy_exposure"]

    assert set(written["policy_id"].to_list()).isdisjoint({"p2", "p3", "p5"})


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-31")
async def test_the_rows_balance_through_a_row_removing_step(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R7. On main the run records no step counts."""
    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(
        database, blob_store, workspace_id, actuary, dataset_id, CSV, [*RECIPE, FILTER]
    )
    run = await _run(database, version_id)

    assert _steps(run) == [
        ("cast", 5, 3, 2),
        ("parse_date", 3, 2, 1),
        ("filter_rows", 2, 1, 0),
    ]
    written = (await _tables(database, blob_store, version_id))["policy_exposure"]
    assert written["policy_id"].to_list() == ["p1"]
    assert_the_rows_balance(run)
    assert 5 - 3 - 1 + 0 == run.rows_written == 1


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-31")
async def test_the_rows_balance_on_the_g2_seeds_own_recipe(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R8a. The seed's `recipe(drop_implausible_exposure=True)` is imported, never copied.
    On main the run records no step counts."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"))
    try:
        from seed import MAX_EXPOSURE, NUMERIC, RENAMES, recipe
    finally:
        sys.path.pop(0)

    source_name = {target: source for source, target in RENAMES.items()}
    columns = ["policy_id", *NUMERIC]
    header = ",".join(source_name.get(c, c) for c in columns)
    over = str(MAX_EXPOSURE + 0.5)
    rows = []
    for i in range(6):
        values = {c: "1" for c in columns}
        values["policy_id"] = f"P{i}"
        values["exposure_years"] = over if i in (1, 4) else "0.5"
        rows.append(",".join(values[c] for c in columns))
    csv = (header + "\n" + "\n".join(rows) + "\n").encode()

    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(
        database,
        blob_store,
        workspace_id,
        actuary,
        dataset_id,
        csv,
        recipe(drop_implausible_exposure=True),
    )
    run = await _run(database, version_id)

    assert ("filter_rows", 6, 4, 0) in _steps(run)
    assert_the_rows_balance(run)
    assert 6 - 0 - 2 + 0 == run.rows_written == 4


# -- limb (b): the verdict -------------------------------------------------------------


async def _report(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    actor: Principal,
    version_id: UUID,
):
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
        report_id = (
            await validation_service.reports_for_version(
                session, workspace_id=workspace_id, version_id=version_id
            )
        )[0].id
        return await validation_service.load_report(
            session, workspace_id=workspace_id, report_id=report_id
        )


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-46")
async def test_a_quarantined_coercion_fails_validation(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R4. On main the report is overall `pass`, all five rules passing."""
    dataset_id = await _dataset(database, workspace_id, actuary)
    version_id = await _ingest(database, blob_store, workspace_id, actuary, dataset_id, CSV, RECIPE)
    report = await _report(database, blob_store, workspace_id, actuary, version_id)
    by_slug = {r.rule_slug: r for r in report.results}

    assert validation_service.overall_outcome(report) is OverallOutcome.FAIL
    assert by_slug["reject-rate"].outcome is RuleOutcome.FAIL
    assert by_slug["reject-rate"].measured["rejected_rows"] == 3
    assert by_slug["reject-rate"].measured["rows_read"] == 5
    assert by_slug["dtype"].measured.get("coerced_cells") == {"claim_amount": 2, "start_date": 1}
    assert by_slug["datep"].measured.get("coerced_cells") == {"start_date": 1}


@pytest.mark.req("FR-32")
@pytest.mark.req("FR-46")
async def test_without_reject_rate_the_declared_severity_still_decides(
    database: Database, blob_store: BlobStore, workspace_id, actuary: Principal
) -> None:
    """R5. On main both reports read `pass`."""
    warn = {"dtype": Severity.WARN, "datep": Severity.WARN}
    dataset_id = await _dataset(database, workspace_id, actuary, warn, omit=("reject-rate",))
    version_id = await _ingest(database, blob_store, workspace_id, actuary, dataset_id, CSV, RECIPE)
    report = await _report(database, blob_store, workspace_id, actuary, version_id)
    assert validation_service.overall_outcome(report) is OverallOutcome.PASS_WITH_WARNINGS

    async with database.session() as session:
        report_id = (
            await validation_service.reports_for_version(
                session, workspace_id=workspace_id, version_id=version_id
            )
        )[0].id
    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await validation_service.promote_using_report(
                session,
                workspace_id=workspace_id,
                actor=actuary,
                version_id=version_id,
                report_id=report_id,
            )
    assert refused.value.code == "WARN_NOT_ACKNOWLEDGED"

    fail = {"dtype": Severity.FAIL, "datep": Severity.WARN}
    dataset_id = await _dataset(
        database, workspace_id, actuary, fail, omit=("reject-rate",), suffix="-2"
    )
    version_id = await _ingest(database, blob_store, workspace_id, actuary, dataset_id, CSV, RECIPE)
    report = await _report(database, blob_store, workspace_id, actuary, version_id)
    assert validation_service.overall_outcome(report) is OverallOutcome.FAIL
