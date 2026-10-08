"""The FR-240 family at the platform seam (`PL-1471`, SL-1472).

Approval refuses a model over an unapproved custom objective (`02` R4, `06` FR-359); the
compile Job refuses what approval could not catch (`03` FR-240); a `control`-intent Factor
never reaches a rateable path (`02` FR-88). Each test names the cause it is red by at the
slice's base in the ledger (`LG-9475`, build log).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_expression_objective_fit import _expression_objective, _fit
from backend.tests.test_glm_approximation_model import _transparency_job
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_lifecycle import _principal_with
from sqlalchemy import select, text

from app.db.models import ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import modelling as service
from app.platform.blobs import BlobStore
from model_schema import DecisionKind, JobStatus, ModelFlag, ModelStatus


async def _set_objective_status(database: Database, ref: str, status: str) -> None:
    """Move a certified objective to `status`; the certificate stays, so the CHECK holds."""
    slug, version = ref.removeprefix("custom_objective:").split("@")
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE custom_objectives SET status = :s WHERE slug = :slug AND version = :v"),
            {"s": status, "slug": slug, "v": int(version)},
        )


async def _gbm_over_objective(
    database: Database, blob_store: BlobStore, workspace_id: Any, *, objective_status: str
) -> tuple[UUID, str]:
    """A fitted GBM whose custom objective is `objective_status` at the end."""
    # `approved` is written only through `mark_approved` (the 06 FR-351 trigger); any other
    # status is moved by SQL from the `certified` the fixture's Job leaves.
    ref = await _expression_objective(
        database, blob_store, workspace_id, approve=objective_status == "approved"
    )
    model_id, fit_status = await _fit(database, blob_store, workspace_id, ref)
    assert fit_status is JobStatus.SUCCEEDED
    if objective_status not in ("approved", "certified"):
        await _set_objective_status(database, ref, objective_status)
    return model_id, ref


async def _submit_and_decide(
    database: Database, blob_store: BlobStore, workspace_id: Any, model_id: UUID
) -> Any:
    actor = await _actuary(database, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")
    await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id
    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="looks fine to me",
        )
    return approver, decided


async def _status_of(database: Database, model_id: UUID) -> str:
    async with database.session() as session:
        return (
            await session.execute(select(ModelRow.status).where(ModelRow.id == model_id))
        ).scalar_one()


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.req("FR-359")
async def test_a_model_whose_custom_objective_is_in_review_cannot_be_approved(
    database, blob_store, workspace_id
) -> None:
    """FD-1469 §3: the approval went through over a `review` objective (`02` R4)."""
    model_id, ref = await _gbm_over_objective(
        database, blob_store, workspace_id, objective_status="review"
    )
    approver, decided = await _submit_and_decide(database, blob_store, workspace_id, model_id)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=approver, request=decided
            )
    assert refused.value.code == "ARTIFACT_FLAGGED"
    assert refused.value.status == 409
    assert "custom_objective_not_approved" in str(refused.value.detail)
    assert ref in str(refused.value.detail)
    assert await _status_of(database, model_id) == ModelStatus.REVIEW.value


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.req("FR-359")
async def test_an_approved_objective_can_be_approved(
    database, blob_store, workspace_id
) -> None:
    """The control: the same chain over an `approved` objective reaches `approved`."""
    model_id, _ = await _gbm_over_objective(
        database, blob_store, workspace_id, objective_status="approved"
    )
    approver, decided = await _submit_and_decide(database, blob_store, workspace_id, model_id)
    async with database.unit_of_work() as session:
        await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
    assert await _status_of(database, model_id) == ModelStatus.APPROVED.value


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.req("FR-359")
async def test_flags_for_names_an_unapproved_objective(
    database, blob_store, workspace_id
) -> None:
    model_id, _ = await _gbm_over_objective(
        database, blob_store, workspace_id, objective_status="review"
    )
    async with database.session() as session:
        row = (await session.execute(select(ModelRow).where(ModelRow.id == model_id))).scalar_one()
        flags = await service.flags_for(session, workspace_id=workspace_id, row=row)
    assert flags == (ModelFlag.CUSTOM_OBJECTIVE_NOT_APPROVED,)
