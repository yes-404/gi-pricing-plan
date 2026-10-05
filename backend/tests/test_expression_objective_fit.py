"""Fitting with an `expression` objective through the `model.fit` Job (FR-144, FR-165).

WK-690 Slice 3, Task 6 (`RL-1362` DP-S3-1): `compile_objective` compiles the artifact's
**stored** `derived` block, and the fit job surfaces the two coded errors Slice 2 added.
`packages/pricing-core/tests/test_objectives.py -k compile_dispatch` proves the compile;
what is proven here is the seam: a stored row, the resolver, the fit, the job's error.
"""

from __future__ import annotations

import functools
import json
from typing import Any
from uuid import UUID

import pytest
from backend.tests.approved_rows import mark_approved
from backend.tests.test_custom_objectives_expression import _APPLICABILITY, _INSERT
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_jobs_gbm import _CERTIFY_GRID, _fitted_gbm
from sqlalchemy import select, text

from app.db.models import CustomObjectiveRow, JobRow
from app.db.session import Database
from app.platform import jobs as job_service
from app.platform.blobs import BlobStore
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import GbmFunctionRef, JobKind, JobStatus, ResponseKind, new_uuid7
from pricing_core.modelling import gbm as gbm_module
from pricing_core.modelling.expression_objective import derive
from pricing_core.modelling.objectives import make_xgb_objective

register_model_handlers()

_POISSON_LOSS = "w * (exp(f) - y * f)"


async def _expression_objective(
    database: Database,
    blob_store: BlobStore,
    workspace_id: Any,
    *,
    loss: str = _POISSON_LOSS,
    stored_gradient: str | None = None,
    approve: bool = True,
) -> str:
    """An `expression` row with its stored derivation, certified through the real Job.

    `stored_gradient` replaces the stored gradient text, which is how a stored block that
    differs from a fresh derivation is made: `derived` is write-once, so the row is inserted
    with it.

    Fixture limit (audit A5 (c)): a stored gradient that fails certification leaves the
    objective a `draft` with no `certificate_id`, so the `certified` state this fixture then
    sets by SQL is **not reachable through the lifecycle**, and no `derive()` output could be
    such a block. What it stands for is a block that certifies on its grid and overflows on
    real data during boosting; the tests prove the fit's abort and its error code, not that
    scenario end to end.
    """
    derived = derive(loss)
    block = {
        "gradient": stored_gradient or derived.gradient,
        "hessian": derived.hessian,
        "derivation_tool": "sympy",
        "derivation_version": derived.derivation_version,
        "derived_at": "2026-10-04T10:00:00+00:00",
    }
    row_id = new_uuid7()
    applicability = {**_APPLICABILITY, "responses": ["burning_cost"]}
    async with database.unit_of_work() as session:
        await session.execute(
            _INSERT,
            {
                "id": row_id,
                "workspace_id": workspace_id,
                "slug": f"expr-{row_id.hex[-8:]}",
                "status": "draft",
                "kind": "expression",
                "template": None,
                "certificate_id": None,
                "bound_symbols": json.dumps(["y", "f", "w"]),
                "parameters": json.dumps([]),
                "loss": loss,
                "derived": json.dumps(block),
                "applicability": json.dumps(applicability),
            },
        )
    actor = await _actuary(database, workspace_id)
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "objective_id": str(row_id),
                "sampling": _CERTIFY_GRID.model_dump(mode="json"),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.unit_of_work() as session:
        row = await session.get(CustomObjectiveRow, row_id)
        assert row is not None
        if row.certificate_id is None:
            # A failing certificate leaves the objective in `draft` (`record_certificate`),
            # and a stored block that overflows is one. Point the row at the certificate the
            # run wrote, as a fit that reached `certified` would have it, so the status gate
            # passes and the fit's own abort is what is under test.
            await session.execute(
                text(
                    "UPDATE custom_objectives SET certificate_id = (SELECT id FROM "
                    "objective_certificates WHERE custom_objective_id = :id ORDER BY certified_at "
                    "DESC LIMIT 1), status = 'certified' WHERE id = :id"
                ),
                {"id": row_id},
            )
            await session.refresh(row)
        if approve:
            await mark_approved(session, row)
        ref = f"custom_objective:{row.slug}@{row.version}"
    return ref


async def _fit(
    database: Database, blob_store: BlobStore, workspace_id: Any, ref: str
) -> tuple[UUID, JobStatus]:
    return await _fitted_gbm(
        database,
        blob_store,
        workspace_id,
        objective=GbmFunctionRef(kind="custom", ref=ref),
        response=ResponseKind.BURNING_COST,
    )


async def _job_error(database: Database, workspace_id: Any) -> JobRow:
    async with database.session() as session:
        rows = (
            await session.scalars(
                select(JobRow)
                .where(JobRow.workspace_id == workspace_id, JobRow.kind == JobKind.MODEL_FIT)
                .order_by(JobRow.queued_at.desc())
            )
        ).all()
    return rows[0]


@pytest.mark.req("FR-144")
async def test_fit_an_approved_expression_objective_fits(
    database: Database, blob_store: BlobStore, workspace_id: Any
) -> None:
    ref = await _expression_objective(database, blob_store, workspace_id)
    _, status = await _fit(database, blob_store, workspace_id, ref)
    assert status is JobStatus.SUCCEEDED


@pytest.mark.req("FR-144")
async def test_fit_a_certified_expression_objective_fits_like_a_template(
    database: Database, blob_store: BlobStore, workspace_id: Any
) -> None:
    """RL-1362 DP-S3-1: the status gate is the template's own; no kind-specific narrowing."""
    ref = await _expression_objective(database, blob_store, workspace_id, approve=False)
    _, status = await _fit(database, blob_store, workspace_id, ref)
    assert status is JobStatus.SUCCEEDED


@pytest.mark.req("FR-165")
async def test_fit_an_overflowing_stored_gradient_fails_with_the_nonfinite_code(
    database: Database, blob_store: BlobStore, workspace_id: Any
) -> None:
    ref = await _expression_objective(
        database,
        blob_store,
        workspace_id,
        stored_gradient="w * exp(1000 * exp(f))",
    )
    _, status = await _fit(database, blob_store, workspace_id, ref)
    assert status is JobStatus.FAILED
    job = await _job_error(database, workspace_id)
    assert job.error is not None
    assert job.error["code"] == "OBJECTIVE_NONFINITE_DERIVATIVE"
    # FD-1219: the persisted text names the round and the fields, never a value.
    assert "round 0" in job.error["message"]


@pytest.mark.req("FR-165")
async def test_fit_a_callable_past_the_round_budget_fails_with_the_budget_code(
    database: Database,
    blob_store: BlobStore,
    workspace_id: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gbm_module, "make_xgb_objective", functools.partial(make_xgb_objective, round_budget_s=1e-9)
    )
    ref = await _expression_objective(database, blob_store, workspace_id)
    _, status = await _fit(database, blob_store, workspace_id, ref)
    assert status is JobStatus.FAILED
    job = await _job_error(database, workspace_id)
    assert job.error is not None
    assert job.error["code"] == "OBJECTIVE_ROUND_BUDGET_EXCEEDED"
