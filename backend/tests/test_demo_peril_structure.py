"""The demo seeds an approved severity GLM and an approved AD Peril Structure (PL-1542
Acceptance 1 and 2; WK-1178 A-4, Tasks 1 and 2).

PREP BRANCH: red-first tests only. `examples/fremtpl2/model.py` has neither `fit_severity_glm`
nor `create_ad_peril_structure` yet; the signatures below are the tests' proposal, shaped after
`_fit` and `compare_and_approve`, and are recorded in the slice ledger.

The book is a small synthetic one, DB-backed, so it runs in CI; the real 20 000-row probe and
the rehearsal on the full seed are Task 0 Step 4 and the demo run, not this file. Severity is
the ruled column (the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-14 09:45:05
BST" item (B)): `claim_severity`, Float64, `claim_amount_minor / claim_count` with no rounding,
null where `claim_count` is 0 (the weight-0 rows SL-1675 excludes from the fit).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

import numpy as np
import pytest
from backend.tests.test_data_jobs import CAST_RECIPE, _seed_dataset_and_rules, _validate
from backend.tests.test_demo_rating_evidence import demo_model
from backend.tests.test_model_jobs import _actuary, _factor, _spec, _split
from sqlalchemy import select

from app.db.models import ApprovalDecisionRow, DatasetVersionRow, ModelRow, PerilStructureRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import perils as perils_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    DecisionKind,
    JobKind,
    JobStatus,
    ModelStatus,
    PerilStructureStatus,
    Principal,
    ResponseKind,
)

register_data_handlers()
register_model_handlers()

SEVERITY_COLUMN = "claim_severity"
_RNG = np.random.default_rng(20261014)


def _book(
    *, bad_row: str | None = None
) -> bytes:
    """400 policies over two areas. `claim_severity` = `claim_amount_minor / claim_count`,
    unrounded, and EMPTY (null) where `claim_count` is 0. `bad_row` plants one claimant row whose
    severity is `"null"` (empty) or `"non_positive"` (0.0), the two refusals the fit owes."""
    n = 400
    area = _RNG.integers(0, 2, n)
    counts = _RNG.poisson(np.where(area == 1, 0.30, 0.15))
    header = "policy_id,exposure_years,area,claim_count,claim_amount_minor,claim_severity\n"
    lines: list[str] = []
    planted = False
    for i, (a, c) in enumerate(zip(area, counts, strict=True), start=1):
        if c == 0:
            lines.append(f"P{i},1.0,{'urban' if a else 'rural'},0,0,\n")
            continue
        mean = 150_000.0 if a else 90_000.0
        amount = int(round(float(_RNG.gamma(shape=2.0 * c, scale=mean / 2.0))) + c)
        severity = repr(amount / c)
        if bad_row is not None and not planted:
            severity = "" if bad_row == "null" else "0.0"
            planted = True
        lines.append(f"P{i},1.0,{'urban' if a else 'rural'},{c},{amount},{severity}\n")
    return (header + "".join(lines)).encode()


async def _version(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal,
    book: bytes,
) -> tuple[UUID, UUID]:
    """Ingest with the recipe the seed will use (the severity cast added), validate, promote."""
    from app.platform import validation as validation_service

    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actor)
    recipe = [
        {
            "step": "cast",
            "table": "policy_exposure",
            "params": {"columns": {**CAST_RECIPE[0]["params"]["columns"],
                                   SEVERITY_COLUMN: "float"}},
        }
    ]
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, book, "text/csv")
        job = await job_service.submit(
            session, JobKind.DATASET_INGEST,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "dataset_id": str(dataset_id), "blob": ref.sha256, "filename": "exposure.csv",
             "recipe": recipe},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        version_id = (
            await session.execute(
                select(DatasetVersionRow.id)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc()).limit(1)
            )
        ).scalar_one()
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, report_id=report_id,
        )
    return dataset_id, version_id


async def _approve(
    database: Database, workspace_id: UUID, submitter: Principal, approver: Principal,
    model_id: UUID,
) -> None:
    """The frequency model, approved the way `compare_and_approve` approves (FR-355: a structure
    over an unapproved component is refused at approval)."""
    async with database.unit_of_work() as session:
        _, request = await model_service.submit_for_review(
            session, workspace_id=workspace_id, actor=submitter, model_id=model_id,
            change_summary="frequency GLM for the AD structure fixture",
        )
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request.id, approver=approver,
            decision=DecisionKind.APPROVE, comment="fixture",
        )
        await model_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )


class _World:
    def __init__(self, **fields: Any) -> None:
        self.__dict__.update(fields)


async def _world(
    database: Database, blob_store: BlobStore, workspace_id: UUID, *, bad_row: str | None = None
) -> Any:
    actuary = await _actuary(database, workspace_id)
    approver_a = await _actuary(database, workspace_id)
    approver_b = await _actuary(database, workspace_id)
    dataset_id, version_id = await _version(
        database, blob_store, workspace_id, actuary, _book(bad_row=bad_row)
    )
    area = await _factor(database, workspace_id, actuary, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actuary, version_id)
    frequency_id = await demo_model._fit(
        database, blob_store, workspace_id, actuary,
        _spec(version_id, (area,), split_ref=split, peril="AD"), "frequency",
    )
    return _World(
        actuary=actuary, approvers=(approver_a, approver_b), dataset_id=dataset_id,
        version_id=version_id, factors=(area,), split=split, frequency_id=frequency_id,
    )


@pytest.mark.req("FR-111")
async def test_seed_fits_and_approves_a_severity_glm(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """PL-1542 Acceptance 1. The severity model is `claim_severity` (ResponseKind), gamma/log,
    weighted by `claim_count`, peril AD, on the SAME dataset version and split as the frequency
    model (FR-190's holdout rule), and approved.

    Red first, by cause: `demo_model` has no `fit_severity_glm`, so no `claim_severity` model
    exists in the seed."""
    world = await _world(database, blob_store, workspace_id)

    severity_id = await demo_model.fit_severity_glm(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
        world.version_id, world.split, world.factors,
    )

    async with database.session() as session:
        row = (
            await session.execute(select(ModelRow).where(ModelRow.id == severity_id))
        ).scalar_one()
        frequency = (
            await session.execute(select(ModelRow).where(ModelRow.id == world.frequency_id))
        ).scalar_one()
    spec = row.spec
    assert row.status == ModelStatus.APPROVED.value
    assert spec["response"] == ResponseKind.CLAIM_SEVERITY.value
    assert spec["response_column"] == SEVERITY_COLUMN
    assert spec["family"] == "gamma"
    assert spec["link"] == "log"
    assert spec["weight"] == {"kind": "column", "column": "claim_count"}
    assert spec["peril"] == "AD"
    assert row.dataset_version_id == world.version_id == frequency.dataset_version_id
    assert spec["split_ref"] == frequency.spec["split_ref"]


@pytest.mark.req("FR-111")
@pytest.mark.parametrize("bad_row", ["null", "non_positive"])
async def test_a_claimant_row_without_a_positive_severity_is_refused_loudly(
    database: Database, blob_store: BlobStore, workspace_id: UUID, bad_row: str
) -> None:
    """The maintainer's (by delegation) "2026-10-14 09:45:05 BST" item (B): a null or
    non-positive `claim_severity` on a row with `claim_count > 0` is REFUSED by the fit, never
    papered over (no placeholder response; weight-0 rows are the only rows allowed to be null).

    Red first, by cause: `fit_severity_glm` does not exist. After it does, this stays the guard
    that the refusal is the fit's, and the model is not left `approved`."""
    world = await _world(database, blob_store, workspace_id, bad_row=bad_row)

    with pytest.raises((SystemExit, PlatformError, ValueError)):
        await demo_model.fit_severity_glm(
            database, blob_store, workspace_id, world.actuary, world.approvers[0],
            world.version_id, world.split, world.factors,
        )

    async with database.session() as session:
        approved = (
            await session.execute(
                select(ModelRow).where(
                    ModelRow.workspace_id == workspace_id,
                    ModelRow.status == ModelStatus.APPROVED.value,
                    ModelRow.spec["response"].astext == ResponseKind.CLAIM_SEVERITY.value,
                )
            )
        ).scalars().all()
    assert approved == []


async def _structure_world(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> Any:
    world = await _world(database, blob_store, workspace_id)
    await _approve(
        database, workspace_id, world.actuary, world.approvers[0], world.frequency_id
    )
    world.severity_id = await demo_model.fit_severity_glm(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
        world.version_id, world.split, world.factors,
    )
    return world


@pytest.mark.req("FR-190")
async def test_the_ad_peril_structure_reconciles(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """PL-1542 Acceptance 2: one `frequency_severity` component over the frequency and severity
    GLMs, its reconciliation run as the real `PERIL_STRUCTURE_RECONCILE` job and persisted.
    The tolerance is wide: the book is 400 policies (the machinery is under test).

    Red first, by cause: `demo_model` has no `create_ad_peril_structure`."""
    world = await _structure_world(database, blob_store, workspace_id)

    structure_id = await demo_model.create_ad_peril_structure(
        database, blob_store, workspace_id, world.actuary, world.approvers,
        world.frequency_id, world.severity_id, tolerance=Decimal("0.9"),
    )

    async with database.unit_of_work() as session:
        structure = await perils_service.load_structure(
            session, workspace_id=workspace_id, structure_id=structure_id
        )
    assert structure.reconciliation is not None
    assert structure.reconciliation.status.value == "pass"
    assert [p.method.value for p in structure.perils] == ["frequency_severity"]
    assert [p.peril for p in structure.perils] == ["AD"]


@pytest.mark.req("FR-191")
async def test_the_ad_peril_structure_is_approved_through_the_workflow(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """PL-1542 Acceptance 2: the structure reaches `approved` through submit and a decision by
    principals who are neither submitter nor author (A-1's carry moves it), never by a direct
    status write. Asserts the decision row, the request, and the status.

    Red first, by cause: `demo_model` has no `create_ad_peril_structure`."""
    world = await _structure_world(database, blob_store, workspace_id)

    structure_id = await demo_model.create_ad_peril_structure(
        database, blob_store, workspace_id, world.actuary, world.approvers,
        world.frequency_id, world.severity_id, tolerance=Decimal("0.9"),
    )

    async with database.session() as session:
        row = (
            await session.execute(
                select(PerilStructureRow).where(PerilStructureRow.id == structure_id)
            )
        ).scalar_one()
        assert row.status == PerilStructureStatus.APPROVED.value
        assert row.approval_request_id is not None
        decisions = (
            await session.execute(
                select(ApprovalDecisionRow).where(
                    ApprovalDecisionRow.request_id == row.approval_request_id
                )
            )
        ).scalars().all()
    assert decisions, "no approval decision recorded: the status was written, not carried"
    approver_ids = {a.id for a in world.approvers}
    assert {d.approver_id for d in decisions} <= approver_ids
    assert world.actuary.id not in {d.approver_id for d in decisions}
