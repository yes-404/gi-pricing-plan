"""The Model lifecycle, at the layers that can be reached independently (FR-MODEL-64).

`packages/model-schema/tests/test_model_lifecycle.py` proves the transition table refuses
the edges that must not exist. This file proves the three layers *below* the table hold:

* **the database** — a CHECK that survives a direct `UPDATE`, which is the only layer an
  audit rewriting rows with SQL cannot walk past;
* **the service** — the transitions, their refusals, and the audit event each one writes in
  the caller's transaction (`06` R2);
* **the seam to governance** — a decision on an approval request reaching the artifact,
  which is `wf-01` E9 → E10 and the arm of the journey that did not exist before this slice.

Every test that matters here is a **prohibition**. For a governed system the suite has to
prove the wrong thing cannot happen: a model reaching an approver with no evidence, a
submitter approving their own work, a rejected model claiming to have un-fitted itself.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from backend.tests.test_diagnostics import _fit
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.db.models import (
    DatasetVersionRow,
    DiagnosticsRow,
    ModelRow,
    RoleAssignmentRow,
    RoleRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import modelling as service
from app.platform import rbac
from model_schema import (
    ActorKind,
    ApprovalPolicy,
    ApprovalPolicyEntry,
    DatasetStatus,
    DecisionKind,
    ModelStatus,
    Principal,
    ScopeType,
    new_uuid7,
)


async def _grant_role(
    database: Database, workspace_id: UUID, principal_id: UUID, role_slug: str
) -> None:
    """Grant a built-in role to an arbitrary principal.

    The `grant` fixture defaults to the test principal; these tests need a *second* one,
    because separation of duties is the rule most of them are about and a suite that only
    ever has one identity cannot exercise it.
    """
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == role_slug
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=principal_id,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )


async def _principal_with(
    database: Database, workspace_id: UUID, role_slug: str
) -> Principal:
    who = Principal(
        kind=ActorKind.USER, id=new_uuid7(), display=f"{role_slug}@insurer.example"
    )
    await _grant_role(database, workspace_id, who.id, role_slug)
    return who


# -- The database -------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
async def test_the_database_refuses_a_status_outside_the_lifecycle(
    database, workspace_id
) -> None:
    """`models.status` is a `String(16)`, so before this constraint the column accepted
    `'aproved'`, `'live'`, or any other sixteen characters — and a typo in a status is a
    model that every lifecycle query silently skips.

    The type enumerates the six states and the transition table refuses the wrong edges;
    neither is reachable from `psql`. This is the layer that is.

    `fit_result` and `diagnostics_id` are supplied deliberately. Without them the two
    constraints the diagnostics slice added refuse the row first — for the *right* reason
    but the wrong one to be testing — and the test would pass against a table with no
    status constraint at all, which is what it did before this note was written.
    """
    async with database.unit_of_work() as session:
        with pytest.raises(Exception, match="model_status_is_in_the_lifecycle"):
            await session.execute(
                text(
                    "INSERT INTO models (id, workspace_id, model_family_slug, version, "
                    "status, dataset_version_id, spec, spec_hash, fit_result, "
                    "diagnostics_id) VALUES "
                    "(gen_random_uuid(), :ws, 'direct', 1, 'live', gen_random_uuid(), "
                    "'{}'::jsonb, 'v2:sha256:direct-status', '{}'::jsonb, "
                    "gen_random_uuid())"
                ),
                {"ws": workspace_id},
            )


@pytest.mark.req("FR-MODEL-64")
async def test_every_lifecycle_status_is_accepted_by_the_constraint(
    database, workspace_id
) -> None:
    """The other half, and the one a CHECK gets wrong more often: a constraint that
    enumerates five of six states reads as working until the sixth model arrives.

    `draft` and `archived` are the only two a bare insert can use — the other four require
    a `fit_result` and diagnostics, which the constraints added with the diagnostics slice
    already enforce — so the enumeration is asserted from the constraint's own definition
    rather than by inserting six rows that other invariants would rightly refuse.
    """
    async with database.session() as session:
        clause = (
            await session.execute(
                text(
                    "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                    "WHERE conrelid = 'models'::regclass "
                    "AND conname LIKE '%%model_status_is_in_the_lifecycle'"
                )
            )
        ).scalar_one()
    for status in ModelStatus:
        assert f"'{status.value}'" in clause, f"{status.value} missing from {clause}"



async def _draft_with_diagnostics(
    database: Database, workspace_id: UUID, slug: str
) -> tuple[UUID, UUID]:
    """A `draft` model and a diagnostics row naming it, written in `record_fit`'s order.

    Neither is fitted: the point of the pair is the *moment before* the fit lands, which is
    the only moment at which `diagnostics_id` may legitimately be written. `diagnostics` has
    `uq_diagnostics_model`, so this is also the only way to obtain a second, genuinely
    stored diagnostics artifact to try to repoint an already-fitted model at.
    """
    async with database.unit_of_work() as session:
        row = ModelRow(
            workspace_id=workspace_id,
            model_family_slug=slug,
            version=1,
            status=ModelStatus.DRAFT.value,
            dataset_version_id=new_uuid7(),
            spec={},
            spec_hash=f"v2:sha256:{new_uuid7().hex}",
        )
        session.add(row)
        await session.flush()
        diagnostics = DiagnosticsRow(
            workspace_id=workspace_id, model_id=row.id, payload={}
        )
        session.add(diagnostics)
        await session.flush()
        return row.id, diagnostics.id


@pytest.mark.req("FR-OVR-1")
async def test_the_first_write_of_a_diagnostics_pointer_is_not_refused(
    database, workspace_id
) -> None:
    """The positive control for the frozen pointer, and the case a naive guard breaks.

    `models_fit_immutable` now names `diagnostics_id`. Diagnostics are written *after* the
    numbers are computed, by the same job, so a guard that froze the column unconditionally
    would refuse the legitimate first write and no model could ever reach `fitted`.

    It does not, because `record_fit` moves the fit result, the pointer and the status in
    **one** `UPDATE` (`app/platform/modelling.py:793-797` — four assignments on one ORM
    object, one `flush`). At that statement `OLD.fit_result` is still null and the outer
    `IF` never fires. This is that statement, written as SQL so the claim does not rest on
    SQLAlchemy's batching staying as it is.
    """
    model_id, diagnostics_id = await _draft_with_diagnostics(
        database, workspace_id, f"first-write-{new_uuid7().hex[-6:]}"
    )

    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "UPDATE models SET fit_result = '{}'::jsonb, diagnostics_id = :dx, "
                "status = 'fitted' WHERE id = :id"
            ),
            {"dx": diagnostics_id, "id": model_id},
        )

    async with database.session() as session:
        row = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
        assert row.status == ModelStatus.FITTED.value
        assert row.diagnostics_id == diagnostics_id


@pytest.mark.req("FR-OVR-1")
@pytest.mark.req("FR-MODEL-65")
async def test_a_fitted_models_diagnostics_pointer_cannot_be_repointed(
    database, blob_store, workspace_id
) -> None:
    """`02` R2 covers the evidence, not only the numbers.

    `b2c3d4e5f6a7` froze `fit_result`, `spec`, `spec_hash` and `dataset_version_id` and left
    `diagnostics_id` writable. That column is what an approval rests on: `02` §4.8 makes
    `status ≥ fitted` imply a `diagnostics_id`, and `06`'s approver reads whatever it
    reaches. A raw `UPDATE` could therefore swap the A/E, lift and calibration under an
    already-approved model — the numbers unchanged, the reason to believe them replaced —
    and the trigger raised nothing.

    The repoint here is the realistic one rather than a dangling uuid: a **second, genuinely
    stored** diagnostics artifact, belonging to another model. `uq_diagnostics_model` means
    it has to come from another model, which is also what makes the attack attractive —
    point the model under review at a healthier one's evidence.
    """
    _, model_id = await _fit(database, blob_store, workspace_id)
    _, other_diagnostics_id = await _draft_with_diagnostics(
        database, workspace_id, f"donor-{new_uuid7().hex[-6:]}"
    )

    async with database.session() as session:
        before = (
            await session.execute(
                select(ModelRow.diagnostics_id).where(ModelRow.id == model_id)
            )
        ).scalar_one()
    assert before is not None
    assert before != other_diagnostics_id

    with pytest.raises(DBAPIError) as repointed:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE models SET diagnostics_id = :dx WHERE id = :id"),
                {"dx": other_diagnostics_id, "id": model_id},
            )
    assert "immutable" in str(repointed.value)

    async with database.session() as session:
        after = (
            await session.execute(
                select(ModelRow.diagnostics_id).where(ModelRow.id == model_id)
            )
        ).scalar_one()
    assert after == before, "the pointer survived the attempt"

    # ...and the lifecycle stays writable, which is why the guard is conditional rather than
    # a blanket refusal: a fitted model still moves through review and approval.
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE models SET status = 'review' WHERE id = :id"), {"id": model_id}
        )


# -- The service: `fitted → review` -------------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
async def test_a_draft_model_cannot_be_submitted_for_review(
    database, workspace_id
) -> None:
    """`draft → review` is not an edge (FR-MODEL-64), and the refusal must arrive at the
    caller rather than at an approver: a model in `draft` has no coefficients, so the
    approval request would carry nothing to review.

    The draft row is inserted rather than produced by un-fitting a fitted one — the attempt
    to do that is refused by the `models` immutability trigger (`02` R2), which is the
    trigger working and the wrong thing to be testing here.
    """
    actor = await _principal_with(database, workspace_id, "pricing_actuary")
    async with database.unit_of_work() as session:
        row = ModelRow(
            workspace_id=workspace_id,
            model_family_slug=f"unfitted-{new_uuid7().hex[-6:]}",
            version=1,
            status=ModelStatus.DRAFT.value,
            dataset_version_id=new_uuid7(),
            spec={},
            spec_hash=f"v2:sha256:{new_uuid7().hex}",
        )
        session.add(row)
        await session.flush()
        model_id = row.id

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                change_summary="first frequency model for AD",
            )
    assert refused.value.code == "VALIDATION_FAILED"
    assert "is 'draft' and cannot move to 'review'" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-64")
async def test_submission_moves_the_model_to_review_and_creates_the_request(
    database, blob_store, workspace_id
) -> None:
    """`wf-01` E6/E7 in one call: the model enters `review`, the approval request exists,
    and the model names it — `02` §4.8's `approval_request_id`, live from this slice."""
    actor, model_id = await _fit(database, blob_store, workspace_id)

    async with database.unit_of_work() as session:
        row, request = await service.submit_for_review(
            session,
            workspace_id=workspace_id,
            actor=actor,
            model_id=model_id,
            change_summary="first AD frequency model",
        )
        assert row.status == ModelStatus.REVIEW.value
        assert row.approval_request_id == request.id
        assert request.artifact_ref == f"model:{row.model_family_slug}@{row.version}"
        assert request.artifact_type == "model"


@pytest.mark.req("FR-MODEL-64")
async def test_a_second_submission_of_one_model_is_refused(
    database, blob_store, workspace_id
) -> None:
    """Two open reviews of one artifact could reach different answers with nothing to say
    which one a deployment obeys.

    **Two layers refuse it, and the outer one is the model's own.** `review → review` is not
    an edge, so `submit_for_review` never reaches governance's partial unique index — the
    code is `VALIDATION_FAILED`, not the index's 409. That index stays the backstop for
    artifact types whose owning module has no state machine of its own, and for anything
    calling `approvals.submit` directly; it is not this path's guard, and asserting that it
    were would be asserting a mechanism that never runs.
    """
    actor, model_id = await _fit(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="first attempt",
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id,
                change_summary="second attempt",
            )
    assert refused.value.code == "VALIDATION_FAILED"
    assert "cannot move to 'review'" in (refused.value.detail or "")


@pytest.mark.req("FR-GOV-10")
async def test_submission_without_the_policys_evidence_is_refused(
    database, blob_store, workspace_id
) -> None:
    """`06` R4: an approval request missing its required evidence cannot be submitted.

    `EVIDENCE_INCOMPLETE` was registered in `errors.py` and raised by nothing until this
    slice — a catalogue entry indistinguishable from a working refusal, which is the trap
    `01` fell into with `RULE_TIMEOUT`.

    The policy is tightened to require a model comparison, which this build has no way to
    verify. Failing closed is the decision under test: treating an uncheckable requirement
    as satisfied would let a policy tightening silently do nothing.

    **The example used to be `transparency_artifact`**, and was changed rather than deleted
    when that kind became checkable (FR-MODEL-89, 2026-08-17). A test whose uncheckable
    example quietly becomes checkable stops testing failing-closed and starts testing
    nothing — the same trap in the other direction.
    """
    actor, model_id = await _fit(database, blob_store, workspace_id)
    admin = await _principal_with(database, workspace_id, "admin")

    async with database.unit_of_work() as session:
        await approval_service.set_policy(
            session,
            workspace_id=workspace_id,
            actor=admin,
            policy=ApprovalPolicy(
                policies=(
                    ApprovalPolicyEntry(
                        artifact_type="model",
                        approvers_required=1,
                        approver_roles=("approver",),
                        # The floor kinds are present because FR-GOV-37 refuses a policy
                        # without them; `model_comparison` is the addition under test.
                        evidence=(
                            "diagnostics",
                            "transparency_artifact_if_non_glm",
                            "model_comparison",
                        ),
                    ),
                )
            ),
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id,
                change_summary="submitted against a tightened policy",
            )
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert "model_comparison" in (refused.value.detail or "")


# -- The seam to governance: E9 → E10 -----------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
async def test_the_final_approval_moves_the_model_to_approved(
    database, blob_store, workspace_id
) -> None:
    """`wf-01` E10. The whole arm this slice exists to open: before it, an approved request
    sat beside a model still in `review`, and nothing joined the two."""
    actor, model_id = await _fit(database, blob_store, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")

    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id

    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="lift looks right",
        )
        row = await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
        assert row is not None
        assert row.status == ModelStatus.APPROVED.value


@pytest.mark.req("FR-GOV-13")
async def test_requesting_changes_returns_the_model_to_fitted_not_draft(
    database, blob_store, workspace_id
) -> None:
    """The divergence this slice resolved rather than absorbed. FR-GOV-13 returns a
    changes-requested artifact to `draft`; for a Model `draft` means *reserved, not yet
    fitted*, and R2 makes the coefficients immutable — so a model cannot un-fit. `06`
    FR-GOV-13 carries the amendment; this is the test that holds the code to it."""
    actor, model_id = await _fit(database, blob_store, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")

    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id

    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.REQUEST_CHANGES,
            comment="rebanded driver age first, please",
        )
        row = await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
        assert row is not None
        assert row.status == ModelStatus.FITTED.value
        # And it still has its numbers, which is the reason `draft` was wrong.
        assert row.fit_result is not None
        assert row.diagnostics_id is not None


@pytest.mark.req("FR-GOV-11")
async def test_a_submitter_cannot_approve_and_the_model_stays_in_review(
    database, blob_store, workspace_id
) -> None:
    """`wf-01` E9's negative case, at the artifact rather than at the request. R1 is not
    configurable, and the model must not move on a decision that was refused."""
    actor, model_id = await _fit(database, blob_store, workspace_id)
    await _grant_role(database, workspace_id, actor.id, "approver")

    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await approval_service.decide(
                session, workspace_id=workspace_id, request_id=request_id,
                approver=actor, decision=DecisionKind.APPROVE, comment="mine, and fine",
            )
    assert refused.value.code == "SUBMITTER_CANNOT_APPROVE"

    async with database.session() as session:
        row = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
        assert row.status == ModelStatus.REVIEW.value


@pytest.mark.req("FR-MODEL-67")
async def test_a_model_whose_dataset_lost_its_standing_cannot_be_approved(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-67. The dataset version is moved out of `validated` after the fit — which
    `01` FR-DATA-23 makes a real sequence, not a contrived one, because validation is
    re-runnable and a changed rule set can fail a version that once passed.

    The flag is computed rather than stored precisely so that this test does not have to
    write one: nothing sets a column, and the block still holds.
    """
    actor, model_id = await _fit(database, blob_store, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")

    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id
        model = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
        version = await session.get(DatasetVersionRow, model.dataset_version_id)
        assert version is not None
        version.status = DatasetStatus.FAILED.value

    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="looks fine to me",
        )
        with pytest.raises(PlatformError) as refused:
            await service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=approver, request=decided
            )
    assert refused.value.code == "ARTIFACT_FLAGGED"

    async with database.session() as session:
        row = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
        assert row.status == ModelStatus.REVIEW.value, "the refusal rolled the decision back"


# -- Supersession and the end state -------------------------------------------------------


async def _next_version_of(
    database: Database, workspace_id: UUID, model_id: UUID
) -> UUID:
    """A second `fitted` version of the same family, with its own diagnostics artifact.

    Inserted rather than fitted a second time. Supersession is about two *approved* versions
    of one family, and paying a second GLM fit to arrive there would double the slowest test
    in this file while testing the fit path a fourth time. The row is a real one — its own
    diagnostics artifact included, because `models` has a CHECK that requires it and a
    fixture that dodged it would be testing a shape the platform cannot store.

    **The write order is `record_fit`'s, and it has to be.** Two invariants meet here: the
    CHECK refuses a `fitted` row with no `diagnostics_id`, and `diagnostics` needs the
    model's id to exist before it can name one — so the model lands at `draft` with no
    numbers, its diagnostics are written, and the fit result, the pointer and the status move
    together. Going straight to `fitted` fails the CHECK; writing the fit result first and
    the pointer second is refused by the immutability trigger, because by then
    `OLD.fit_result` is not null.
    """
    async with database.unit_of_work() as session:
        first = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
        payload = (
            await session.execute(
                select(DiagnosticsRow.payload).where(
                    DiagnosticsRow.id == first.diagnostics_id
                )
            )
        ).scalar_one()
        fit_result = first.fit_result
        row = ModelRow(
            workspace_id=workspace_id,
            model_family_slug=first.model_family_slug,
            version=first.version + 1,
            status=ModelStatus.DRAFT.value,
            dataset_version_id=first.dataset_version_id,
            spec=first.spec,
            spec_hash=f"v2:sha256:{new_uuid7().hex}",
            parent_model_id=first.id,
            change_reason="refit_new_data",
        )
        session.add(row)
        await session.flush()

        diagnostics = DiagnosticsRow(
            workspace_id=workspace_id, model_id=row.id, payload=payload
        )
        session.add(diagnostics)
        await session.flush()

        row.fit_result = fit_result
        row.diagnostics_id = diagnostics.id
        row.status = ModelStatus.FITTED.value
        await session.flush()
        return row.id


async def _approve(
    database: Database, workspace_id: UUID, actor: Principal, approver: Principal, model_id: UUID
) -> None:
    """Submit and approve through the real path, then carry the decision to the artifact."""
    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id
    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="approved",
        )
        await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )


async def _status_of(database: Database, model_id: UUID) -> str:
    async with database.session() as session:
        return (
            await session.execute(
                select(ModelRow.status).where(ModelRow.id == model_id)
            )
        ).scalar_one()


@pytest.mark.req("FR-MODEL-64")
async def test_approving_a_new_version_supersedes_the_approved_predecessor(
    database, blob_store, workspace_id
) -> None:
    """A family with two approved versions has nothing to say which one a Rating Version
    means, so supersession is automatic rather than an operation someone remembers."""
    actor, first = await _fit(database, blob_store, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")
    await _approve(database, workspace_id, actor, approver, first)
    assert await _status_of(database, first) == ModelStatus.APPROVED.value

    second = await _next_version_of(database, workspace_id, first)
    await _approve(database, workspace_id, actor, approver, second)

    assert await _status_of(database, second) == ModelStatus.APPROVED.value
    assert await _status_of(database, first) == ModelStatus.SUPERSEDED.value


@pytest.mark.req("FR-MODEL-64")
async def test_approving_a_new_version_leaves_a_merely_fitted_predecessor_alone(
    database, blob_store, workspace_id
) -> None:
    """Only `approved` rows move. A version still at `fitted` is a candidate, not a
    predecessor — marking it `superseded` would say it had once been in force."""
    actor, first = await _fit(database, blob_store, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")
    second = await _next_version_of(database, workspace_id, first)

    await _approve(database, workspace_id, actor, approver, second)

    assert await _status_of(database, second) == ModelStatus.APPROVED.value
    assert await _status_of(database, first) == ModelStatus.FITTED.value


@pytest.mark.req("FR-MODEL-64")
async def test_an_approved_model_cannot_be_archived(
    database, blob_store, workspace_id
) -> None:
    """`approved → archived` is not an edge. An approved model is a Rating Version's
    referent, and the operation that removes one names its replacement."""
    actor, model_id = await _fit(database, blob_store, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")
    await _approve(database, workspace_id, actor, approver, model_id)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.archive(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id
            )
    assert refused.value.code == "VALIDATION_FAILED"
    assert "cannot move to 'archived'" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-64")
async def test_a_fitted_model_can_be_archived(database, blob_store, workspace_id) -> None:
    """The lifecycle's only end state, reachable from the states that have no successor in
    force: a fit nobody submitted, and a version something else replaced."""
    actor, model_id = await _fit(database, blob_store, workspace_id)

    async with database.unit_of_work() as session:
        row = await service.archive(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id
        )
        assert row.status == ModelStatus.ARCHIVED.value


@pytest.mark.req("FR-MODEL-64")
async def test_a_model_in_review_cannot_be_archived(
    database, blob_store, workspace_id
) -> None:
    """Withdraw the request first. Archiving from `review` would take an item out of an
    approver's queue with no decision recorded against it."""
    actor, model_id = await _fit(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.archive(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id
            )
    assert refused.value.code == "VALIDATION_FAILED"
