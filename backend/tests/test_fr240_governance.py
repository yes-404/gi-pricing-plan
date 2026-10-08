"""The FR-240 family at the platform seam (`PL-1471`, SL-1472).

Approval refuses a model over an unapproved custom objective (`02` R4, `06` FR-359); the
compile Job refuses what approval could not catch (`03` FR-240); a `control`-intent Factor
never reaches a rateable path (`02` FR-88). Each test names the cause it is red by at the
slice's base in the ledger (`LG-9475`, build log).
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_expression_objective_fit import _expression_objective, _fit
from backend.tests.test_glm_approximation_model import _transparency_job
from backend.tests.test_model_jobs import _actuary
from backend.tests.approved_rows import mark_approved
from backend.tests.test_custom_objectives_api import _advance, _create
from backend.tests.test_model_lifecycle import _principal_with
from backend.tests.test_rating_version_compile import (
    _headers,
    _insert_version,
    _minimal_algorithm,
    _run_compile_job,
)
from sqlalchemy import select, text

from app.db.models import ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import modelling as service
from app.platform.blobs import BlobStore
from app.worker.rating_handlers import register_rating_handlers
from model_schema import DecisionKind, JobStatus, ModelFlag, ModelStatus, ObjectiveStatus


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_rating_handlers()



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


# -- Compile: the Job refuses what approval could not catch (FR-240) ----------------------


def _run(coro: Any) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def _compile_with_pins(
    api_client, principal, workspace_id, database, blob_store, *, models=(), objectives=()
) -> Any:
    headers = _headers(principal, workspace_id)
    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text
    row = _run(
        _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [], "models": list(models), "reference_tables": [],
                "custom_objectives": list(objectives),
            },
        )
    )
    return _run_compile_job(api_client, headers, database, blob_store, row.id)


@pytest.mark.req("FR-240")
@pytest.mark.parametrize("status", [ObjectiveStatus.CERTIFIED, ObjectiveStatus.REVIEW])
def test_a_version_pinning_an_unapproved_custom_objective_fails_to_compile(
    api_client, workspace_id, principal, grant, database, blob_store, status
) -> None:
    """Green at the base, by design: the direct refusal exists but had no negative test.
    Its proof is a broken-input run (Acceptance 8), recorded in the ledger."""
    _run(grant("analyst"))
    objective = _create(api_client, _headers(principal, workspace_id))
    _advance(UUID(objective["id"]), status=status)
    ref = f"custom_objective:{objective['slug']}@{objective['version']}"
    job_row = _compile_with_pins(
        api_client, principal, workspace_id, database, blob_store, objectives=[ref]
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-359")
def test_an_overridden_flag_never_reaches_compile(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """DP-1's condition: flag -> override -> approved -> compile still REFUSES.

    FR-359's Admin override is built for no flag (`apply_approval_decision` raises for every
    flag), so `approved` is reached with `mark_approved`, the one way an `approved` row over
    a flagged model can exist today (an override, or an approval from before the flag). The
    assertion that compile refuses does not depend on how `approved` was reached.
    """
    _run(grant("analyst"))

    async def _arrange() -> str:
        model_id, _ = await _gbm_over_objective(
            database, blob_store, workspace_id, objective_status="review"
        )
        async with database.unit_of_work() as session:
            row = await session.get(ModelRow, model_id)
            assert row is not None
            await mark_approved(session, row)
            return f"model:{row.model_family_slug}@{row.version}"

    model_ref = _run(_arrange())
    job_row = _compile_with_pins(
        api_client, principal, workspace_id, database, blob_store, models=[model_ref]
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "PIN_NOT_APPROVED"
