"""The `02` non-functional requirements that are assertions rather than timings.

The twin of `test_data_nfrs.py`, and it draws the same line. NFR-MODEL-1/2/3/4/5/10/11 are
performance and size budgets and are **measured** rather than tested — a timing assertion in
CI fails on a busy runner and teaches everyone to re-run it, which is worse than no check.
`scripts/bench-model.py` produces those numbers and `02` §9 records them against their
budgets, which is where a human reads them once.

What is left here is NFR-MODEL-9, the audit clause, which is an assertion about what the
database holds after an act and not about how long the act took.

**Two of the twelve are not testable at all today**, and neither gets a marker in this file:

* **NFR-MODEL-7** — a stored Model round-trips export → import into a clean instance. There
  is no export path and no import path for a Model anywhere in the repository: no route, no
  CLI, no bundle schema. The one `export` in the HTTP surface is the audit log's
  (`app/api/audit.py`). Its parent, FR-OVR-2, carries no marker either.
* **NFR-MODEL-8's** position-accurate error and per-round objective budgets. Its `eval`/
  `exec` clause *is* evidenced, in `packages/pricing-core/tests/test_expression_nfrs.py`,
  where the parser lives.

And one is **half** evidenced where the record says it is whole: **NFR-MODEL-6** asks for
identical GLM coefficients to 1e-10 *and* an identical GBM booster hash, and the only marker
it carries (`packages/pricing-core/tests/test_gbm.py`) is the booster half. Nothing anywhere
refits a GLM on the same spec and seed and compares the coefficients. That test belongs
beside the GLM it is about, not here.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from backend.tests.test_custom_objectives import COUNT_GRID, _objective
from backend.tests.test_model_jobs import (
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)
from sqlalchemy import select

from app.db.models import AuditEventRow, ModelRow, RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.platform import approvals as approval_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import objectives as objective_service
from app.platform import rbac
from app.platform import transformations as transform_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    Banding,
    BandingMethod,
    DecisionKind,
    Grouping,
    GroupingMethod,
    JobKind,
    JobStatus,
    ModelStatus,
    ObjectiveStatus,
    Principal,
    ScopeType,
    UnseenLevelBehaviour,
    new_uuid7,
)

register_data_handlers()
register_model_handlers()


async def _principal_with(database: Database, workspace_id: UUID, *roles: str) -> Principal:
    """A principal holding named built-in roles in this workspace.

    Written here rather than imported so this module does not depend on another test
    module's private helper: `test_data_nfrs.py` keeps its own `_analyst` for the same
    reason, and an NFR file that fails because a lifecycle test refactored a fixture is a
    file nobody trusts.
    """
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="nfr@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        for slug in roles:
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


async def _events(database: Database, workspace_id: UUID, action: str) -> list[AuditEventRow]:
    """Every Audit Event for one action in this workspace.

    Queried by `workspace_id` + `action`, the way `test_data_nfrs.py` does it. Audit rows
    cannot be deleted between tests (FR-GOV-22), so the workspace *is* the isolation and a
    filter on it is a filter on this test's own history.
    """
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == action,
                    )
                )
            )
            .scalars()
            .all()
        )


@pytest.mark.req("NFR-MODEL-9")
async def test_a_model_status_transition_emits_an_audit_event_with_before_and_after(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """NFR-MODEL-9: every model status transition carries before and after state.

    `draft → archived`, which is the one edge reachable without a fit — and the shape it
    proves is the shape all four model transitions share (`platform/modelling.py`'s
    `model.submitted`, `model.{approved,rejected}`, `model.superseded` and
    `model.archived` all pass `before={"status": ...}`).

    The `before` is what makes the event evidence rather than a notification: an approver
    asking why a model left `review` needs to know what it left *from*, and an event
    carrying only the destination cannot answer that after a second transition has run.
    """
    actor = await _principal_with(database, workspace_id, "analyst", "pricing_actuary")
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=_spec(version_id, (area,))
        )
        model_id = row.id
        assert row.status == ModelStatus.DRAFT.value

    async with database.unit_of_work() as session:
        await model_service.archive(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id
        )

    events = await _events(database, workspace_id, "model.archived")
    assert len(events) == 1
    assert events[0].before == {"status": "draft"}
    assert events[0].after["status"] == "archived"


@pytest.mark.req("NFR-MODEL-9")
async def test_objective_certification_and_approval_emit_before_and_after(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """NFR-MODEL-9: objective certification and approval carry before and after state.

    All three acts the requirement names for a Custom Objective that exists —
    certification, submission, and the approval decision reaching the artifact — run
    through the real Job and the real approval service, because the question is what the
    audit table holds and not what the service was called with.

    **Objective *derivation* is absent from this test because it is absent from the
    platform.** `expression` objectives are Phase 2 (`platform/objectives.py`'s
    `refuse_expression_kind` refuses the kind by name), so there is no derivation to audit
    and no `custom_objective.derived` action to assert on.
    """
    actor = await _principal_with(database, workspace_id, "analyst", "pricing_actuary")
    approver = await _principal_with(database, workspace_id, "approver")
    objective = await _objective(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "objective_id": str(objective.id),
                "sampling": COUNT_GRID.model_dump(mode="json"),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    certified = await _events(database, workspace_id, "custom_objective.certified")
    assert len(certified) == 1
    assert certified[0].before == {"status": ObjectiveStatus.DRAFT.value}
    assert certified[0].after["status"] == ObjectiveStatus.CERTIFIED.value

    async with database.unit_of_work() as session:
        _, request = await objective_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor,
            objective_id=objective.id, change_summary="certified, ready for review",
        )
        request_id = request.id

    submitted = await _events(database, workspace_id, "custom_objective.submitted")
    assert len(submitted) == 1
    assert submitted[0].before == {"status": ObjectiveStatus.CERTIFIED.value}
    assert submitted[0].after["status"] == ObjectiveStatus.REVIEW.value

    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, approver=approver,
            request_id=request_id, decision=DecisionKind.APPROVE,
            comment="derivatives check out",
        )
        await objective_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )

    approved = await _events(database, workspace_id, "custom_objective.approved")
    assert len(approved) == 1
    assert approved[0].before == {"status": ObjectiveStatus.REVIEW.value}
    assert approved[0].after["status"] == ObjectiveStatus.APPROVED.value


@pytest.mark.req("NFR-MODEL-9")
async def test_fit_start_and_completion_are_audited_and_creation_carries_no_before(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """NFR-MODEL-9's other half — and the half of it that is not met, pinned rather than
    papered over.

    The requirement asks for *"factor/banding/grouping creation and edit, fit start and
    completion … with before/after state"*. Every one of those five events exists and is
    audited: `factor.created`, `banding.created`, `grouping.created`, `model.reserved`
    (fit start, written in the request so a queued Job is already accounted for) and
    `model.fitted` (completion). **None of them carries a `before`**, and this test asserts
    that they do not.

    Asserted rather than fixed, because the fix is a decision and not a keystroke. These
    artifacts are versioned, never edited: `create_factor`, `create_banding` and
    `create_grouping` each allocate the *next version* of a slug rather than rewriting one,
    so an "edit" is a new artifact whose predecessor is still readable at its own version.
    On that reading a create has no before by construction, and `before={}` would be a
    fabricated fact — an empty dict that satisfies a grep and tells an auditor the artifact
    previously existed in an empty state, which is false.

    Whether the requirement should say so, or the events should carry the superseded
    version, is a verdict for `02` §9. What this test guarantees meanwhile is that the
    shape cannot drift silently in either direction.
    """
    actor = await _principal_with(database, workspace_id, "analyst", "pricing_actuary")
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        await transform_service.create_banding(
            session, workspace_id=workspace_id, actor=actor,
            banding=Banding(
                id=uuid4(), slug=f"amt-{uuid4().hex[-6:]}", dataset_id=dataset_id,
                version=1, column="claim_amount_minor", method=BandingMethod.MANUAL,
                boundaries=(0.0, 150_000.0, 300_000.0), labels=("low", "high"),
            ),
        )
        await transform_service.create_grouping(
            session, workspace_id=workspace_id, actor=actor,
            grouping=Grouping(
                id=uuid4(), slug=f"area-{uuid4().hex[-6:]}", dataset_id=dataset_id,
                version=1, column="area", method=GroupingMethod.MANUAL,
                mapping={"urban": "ALL", "rural": "ALL"},
                unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
            ),
        )

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        assert should_fit is True
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        fitted = await session.get(ModelRow, model_id)
        assert fitted is not None
        assert fitted.status == ModelStatus.FITTED.value

    for action, key in (
        ("factor.created", "slug"),
        ("banding.created", "slug"),
        ("grouping.created", "slug"),
        ("model.reserved", "spec_hash"),
        ("model.fitted", "rows"),
    ):
        events = await _events(database, workspace_id, action)
        assert len(events) == 1, f"{action} emitted {len(events)} events"
        assert events[0].after is not None, f"{action} recorded no after state"
        assert key in events[0].after, (
            f"{action}'s after state does not carry {key!r}"
        )
        # The gap, asserted. See this test's docstring: a create has no prior state, and
        # `before={}` would be a fabricated one.
        assert events[0].before is None, (
            f"{action} now carries a before state — NFR-MODEL-9's create-only gap has been "
            "closed, and `02` §9's verdict on it needs updating rather than this assertion"
        )
