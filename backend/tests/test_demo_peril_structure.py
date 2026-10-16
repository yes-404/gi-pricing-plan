"""The demo seeds an approved severity GLM and an approved AD Peril Structure (PL-1542
Acceptance 1 and 2; WK-1178 A-4, Tasks 1 and 2).

`examples/fremtpl2/model.py` carries `fit_severity_glm` and `create_ad_peril_structure` (Tasks 1
and 2); their signatures are recorded in the slice ledger. The two were red by absence on the
prep branch (`AttributeError`, recorded in LG 9879).

The book is a small synthetic one, DB-backed, so it runs in CI; the real 20 000-row probe and
the rehearsal on the full seed are Task 0 Step 4 and the demo run, not this file. Severity is
the ruled column (the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-14 09:45:05
BST" item (B)): `claim_severity`, Float64, `claim_amount_minor / claim_count` with no rounding,
null where `claim_count` is 0 (the weight-0 rows SL-1675 excludes from the fit).
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from uuid import UUID

import numpy as np
import pytest
from backend.tests.test_data_jobs import CAST_RECIPE, _seed_dataset_and_rules, _validate
from backend.tests.test_demo_rating_evidence import demo_model
from backend.tests.test_model_jobs import _actuary, _factor, _spec, _split
from sqlalchemy import select

from app.db.models import (
    ApprovalDecisionRow,
    DatasetVersionRow,
    JobRow,
    ModelRow,
    PerilStructureRow,
)
from app.db.session import Database
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
    GlmSpec,
    JobKind,
    JobStatus,
    LargeLossKind,
    ModelStatus,
    PerilStructureStatus,
    Principal,
    ResponseKind,
    WeightSpec,
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
        # float()/int(): a numpy scalar's repr is 'np.float64(..)', which the cast reads as null
        severity = repr(float(amount) / int(c))
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
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any,
    *, bad_row: str | None = None,
) -> Any:
    actuary = await _actuary(database, workspace_id)
    approver_a = await _actuary(database, workspace_id)
    approver_b = await _actuary(database, workspace_id)
    for approver in (approver_a, approver_b):
        await grant("approver", principal_id=approver.id)
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
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any
) -> None:
    """PL-1542 Acceptance 1. The severity model is `claim_severity` (ResponseKind), gamma/log,
    weighted by `claim_count`, peril AD, on the SAME dataset version and split as the frequency
    model (FR-190's holdout rule), and approved.

    Red first, by cause: `demo_model` has no `fit_severity_glm`, so no `claim_severity` model
    exists in the seed."""
    world = await _world(database, blob_store, workspace_id, grant)

    severity_id = await demo_model.fit_severity_glm(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
        world.frequency_id,
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


#: glum / sklearn's own CAUSE text for each planted row, the `{exc}` part of `GLM_FIT_FAILED`'s
#: message. Constant across causes is the family-domain sentence glm.py appends to EVERY
#: refusal, so asserting that sentence cannot tell one cause from another (the maintainer's
#: (by delegation) "2026-10-14 11:41:17 BST" correction of R1b).
_CAUSE = {
    "null": "Input y contains NaN",
    "non_positive": "out of the valid range for family",
}


async def _severity_fit(
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any,
    bad_row: str | None,
) -> tuple[JobStatus, str, str]:
    """Fit the Gamma/log severity GLM as the platform's MODEL_FIT Job and return the Job status,
    the persisted error (JSON text, empty on success) and the Model's status."""
    world = await _world(database, blob_store, workspace_id, grant, bad_row=bad_row)
    spec = GlmSpec(
        model_family_slug="fremtpl2-severity-r1b",
        dataset_version_id=world.version_id,
        split_ref=world.split,
        peril="AD",
        response=ResponseKind.CLAIM_SEVERITY,
        response_column=SEVERITY_COLUMN,
        weight=WeightSpec(kind="column", column="claim_count"),
        family="gamma",
        link="log",
        factors=world.factors,
    )
    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=world.actuary, spec=spec
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": world.actuary.model_dump(mode="json"),
             "model_id": str(model_id)},
            world.actuary, workspace_id=workspace_id,
        )
    status = await execute_job(database, job.id, blob_store)
    async with database.session() as session:
        stored = (await session.execute(select(JobRow).where(JobRow.id == job.id))).scalar_one()
        model = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
    return status, json.dumps(stored.error) if stored.error else "", model.status


@pytest.mark.req("FR-111")
async def test_a_clean_severity_book_fits(
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any
) -> None:
    """R1b's NEGATIVE CONTROL: on the clean book the severity Job succeeds. Without it a
    refusal below could come from the fixture (it did: `repr` of a numpy float wrote
    'np.float64(..)' into the CSV, so every severity read as null)."""
    status, error, _ = await _severity_fit(database, blob_store, workspace_id, grant, None)
    assert status is JobStatus.SUCCEEDED, error


@pytest.mark.req("FR-111")
@pytest.mark.parametrize(
    ("bad_row", "other"), [("null", "non_positive"), ("non_positive", "null")]
)
async def test_a_claimant_row_without_a_positive_severity_fails_the_fit_with_its_own_cause(
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any,
    bad_row: str, other: str,
) -> None:
    """R1b as corrected by the maintainer's (by delegation) "2026-10-14 11:41:17 BST": one
    claimant row's `claim_severity` null, or 0, is refused by the EXISTING refusal
    (`GLM_FIT_FAILED`) with THAT row's own cause text, not the other case's. Nothing is
    filtered or clipped. Green on the base tree; red under a scratch that drops the row."""
    status, error, model_status = await _severity_fit(
        database, blob_store, workspace_id, grant, bad_row
    )
    assert status is JobStatus.FAILED
    assert "GLM_FIT_FAILED" in error
    assert _CAUSE[bad_row] in error, error
    assert _CAUSE[other] not in error, error  # the discrimination: the other case's text
    assert model_status != ModelStatus.APPROVED.value


async def _structure_world(
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any
) -> Any:
    world = await _world(database, blob_store, workspace_id, grant)
    await _approve(
        database, workspace_id, world.actuary, world.approvers[0], world.frequency_id
    )
    world.severity_id = await demo_model.fit_severity_glm(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
        world.frequency_id,
    )
    return world


@pytest.mark.req("FR-190")
async def test_the_ad_peril_structure_reconciles(
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any
) -> None:
    """PL-1542 Acceptance 2: one `frequency_severity` component over the frequency and severity
    GLMs, its reconciliation run as the real `PERIL_STRUCTURE_RECONCILE` job and persisted.
    The tolerance is wide: the book is 400 policies (the machinery is under test).

    Red first, by cause: `demo_model` has no `create_ad_peril_structure`."""
    world = await _structure_world(database, blob_store, workspace_id, grant)

    structure_id = await demo_model.create_ad_peril_structure(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
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
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any
) -> None:
    """PL-1542 Acceptance 2: the structure reaches `approved` through submit and a decision by
    principals who are neither submitter nor author (A-1's carry moves it), never by a direct
    status write. Asserts the decision row, the request, and the status.

    Red first, by cause: `demo_model` has no `create_ad_peril_structure`."""
    world = await _structure_world(database, blob_store, workspace_id, grant)

    structure_id = await demo_model.create_ad_peril_structure(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
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


@pytest.mark.req("FR-127")
async def test_guard_dp_a4_3_severity_is_uncapped_until_the_fr_127_glm_fix_merges(
    database: Database, blob_store: BlobStore, workspace_id: UUID, grant: Any
) -> None:
    """THE 11:29:53 GUARD (the maintainer's (by delegation) "2026-10-14 11:29:53 BST" entry in
    `to-lead.md`; PL-1705 "The guard test"). DP-A4-3 is ruled (x): large loss UNCAPPED, carried
    by the structure's `large_loss`, never by the severity GlmSpec's `loss_treatment`. The
    FR-127 GLM fix is off the G2 path only while that holds.

    A tripwire, not a red: it fails the day a capped choice slips in. It changes ONLY together
    with the FR-127 fix's merge, cited in the LG for SL-1543 (LG 9879 while unminted).
    """
    world = await _structure_world(database, blob_store, workspace_id, grant)
    structure_id = await demo_model.create_ad_peril_structure(
        database, blob_store, workspace_id, world.actuary, world.approvers[0],
        world.frequency_id, world.severity_id, tolerance=Decimal("0.9"),
    )
    async with database.session() as session:
        severity_row = (
            await session.execute(select(ModelRow).where(ModelRow.id == world.severity_id))
        ).scalar_one()
    async with database.unit_of_work() as session:
        structure = await perils_service.load_structure(
            session, workspace_id=workspace_id, structure_id=structure_id
        )

    why = (
        "DP-A4-3 is ruled (x), large loss UNCAPPED (the maintainer's (by delegation) "
        "'2026-10-14 11:29:53 BST' entry). A capped choice means the FR-127 GLM fix JOINS the "
        "G2 path and merges BEFORE SL-1543: STOP, restate the G2 ETA, and change this test "
        "only with that merge, cited in the LG."
    )
    severity_spec = GlmSpec.model_validate(severity_row.spec)
    assert severity_spec.loss_treatment.kind == "none", f"severity GlmSpec capped. {why}"
    assert [p.large_loss.kind for p in structure.perils] == [LargeLossKind.NONE], (
        f"AD structure large_loss is not the uncapped treatment. {why}"
    )
