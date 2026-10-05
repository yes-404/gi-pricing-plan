"""The approval state machine (`06` §3.2, FR-351/353/354/355/356/357).

> **R1 — Separation of duties.** The submitter of an approval request can never be its
> approver. This is enforced in the backend, not the UI, and cannot be configured away.

One machine for every artifact type (FR-351). What differs between a custom objective and
a rating version is the *policy* the machine reads — how many approvers, which roles — not
the transitions, and certainly not whether the submitter may approve their own work.

Three of the six requirements here are enforced structurally rather than by a check the
service could forget:

* **Pinning** (FR-356) — the request names `{type}:{slug}@{version}`, artifacts are
  immutable, so a changed artifact is a different reference and this request does not
  describe it.
* **Distinct approvers** (FR-353) — a unique constraint on `(request, approver)`.
* **One open request per artifact version** — a partial unique index. Two open reviews of
  the same thing could reach different answers with nothing to say which one deployment
  obeys.
"""

from __future__ import annotations

import sys
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, Final, Protocol
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalDecisionRow,
    ApprovalPolicyRow,
    ApprovalRequestRow,
    AuditEventRow,
    RoleAssignmentRow,
    RoleRow,
)
from app.errors import PlatformError
from app.platform import audit, environments, rbac
from model_schema import (
    DEFAULT_POLICY,
    VALID_APPROVAL_TRANSITIONS,
    ApprovalPolicy,
    ApprovalStatus,
    ArtifactRef,
    DecisionKind,
    JobSource,
    Permission,
    Principal,
)

__all__ = [
    "CREATION_ACTIONS",
    "ArtifactResolver",
    "EvidenceAuthorResolver",
    "approval_decision",
    "decide",
    "policy_for",
    "require_in_review",
    "set_policy",
    "submit",
    "to_dict",
    "withdraw",
]


@asynccontextmanager
async def approval_decision(session: AsyncSession) -> AsyncIterator[None]:
    """The decision flag: `SET LOCAL app.approval_decision = 'on'` around a write of `approved`.

    `approval_guard()` (migration `a9f3c6d21b87`) refuses an `approved` row that has no
    decided request for its ref; on `approval_requests` itself, and on the validation tables
    while they hold an allowance, it accepts this flag instead (RL-1301 A.4.3).

    **`SET LOCAL` lasts to the end of the transaction, not of this block**, so the block
    flushes and then resets the flag to `'off'` in a `finally`. The flush comes first so the
    block's own pending write meets the trigger while the flag is on; an ORM write left
    unflushed at exit is flushed later under `'off'` and refused, which fails closed. The
    reset runs even when the body raises. If the transaction is already dead the flag died
    with it, and the original error is the one to surface.

    Entered at exactly two sanctioned sites — `decide` and `api.approvals._carry_to_the_artifact`
    — and the named allowance sites; `test_approval_guard_static.py` holds that list.
    """
    await session.execute(text("SET LOCAL app.approval_decision = 'on'"))
    try:
        yield
        await session.flush()
    finally:
        try:
            await session.execute(text("SET LOCAL app.approval_decision = 'off'"))
        except Exception:
            if sys.exc_info()[0] is None:
                raise


#: The Audit Event each approvable type's creation path records — whose actor is, by
#: `06` FR-353 as amended 2026-09-28, the version's **author**. One definition for every
#: type: `created_by` and `authored_by`, where a row carries one, are copies of the same
#: fact rather than second sources, and a test holds each equal to this event's actor.
#: A type absent here has no author the check can find, and fails closed.
CREATION_ACTIONS: Final[Mapping[str, str]] = {
    "model": "model.reserved",
    "custom_objective": "custom_objective.created",
    "custom_metric": "custom_metric.created",
    "peril_structure": "peril_structure.created",
    "validation_rule": "validation_rule.created",
    "dataset_version": "dataset_version.created",
    "rating_version": "rating_version.created",
    # A Deployment Request's Author is its submitter (`06` FR-353 as amended 2026-10-03,
    # `RL-1401`): `platform.deployments` records this event with the request's own
    # reference in the transaction that writes and submits it.
    "deployment": "deployment_request.created",
}


def require_in_review(
    artifact_ref: ArtifactRef | str, status: str, reviewable: str = "review"
) -> None:
    """Refuse an approval subject that is not in its type's reviewable state (`06` FR-351).

    `review` for every approvable type but `dataset_version`, whose lifecycle has no
    review state and whose reviewable state is `validated` (FR-351's 2026-09-28 clause).

    `draft → review → approved`: a version reaches review only through its owning module's
    own submission, which is where that module's gates run (a model's diagnostics, a peril
    structure's reconciliation, a rating version's evidence). A decision on a version that
    never got there would skip every one of them. Called by each type's resolver on the
    generic route and by the decision hooks, so neither guard is the only one.
    """
    if status != reviewable:
        raise PlatformError(
            "APPROVAL_SUBJECT_NOT_IN_REVIEW",
            "Only a version in review can be put to a decision",
            409,
            f"{artifact_ref} is {status!r}, not {reviewable!r}. `06` FR-351: a version reaches "
            "its reviewable state through its owning module's own path, and only then can it "
            "be decided on.",
        )


class ArtifactResolver(Protocol):
    """How `submit` learns whether the version a request pins actually exists (FR-386).

    A callable the caller supplies rather than a lookup performed here, because resolution
    needs one query per artifact type and DEP-1 forbids `GOV` importing `DATA` through
    `MON`. The route supplies it: `api/approvals.py` sits above both governance and the
    owning modules, which is the seam `_carry_to_the_artifact` already uses for the *decide*
    direction. A resolver registry would be a second mechanism for the same join.

    It returns nothing and raises: `NOT_FOUND` where the reference names a version the
    owning module has no row for, and — failing closed — where no module in this build owns
    the artifact type at all.
    """

    async def __call__(
        self, session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
    ) -> None: ...


async def policy_for(session: AsyncSession, workspace_id: UUID) -> ApprovalPolicy:
    """The workspace's policy, or the documented defaults (`06` §4.2, FR-354)."""
    row = await session.get(ApprovalPolicyRow, workspace_id)
    if row is None:
        return DEFAULT_POLICY
    return ApprovalPolicy.model_validate(row.policy)


async def set_policy(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, policy: ApprovalPolicy
) -> ApprovalPolicy:
    """Replace the workspace policy. Audited, and requires `admin:manage_roles`.

    Gated on the same permission as role management because it is the same kind of power:
    a policy that drops `approvers_required` to one is a permission change written in
    another table.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.ADMIN_MANAGE_ROLES,
    )
    below = policy.below_floor()
    if below:
        named = "; ".join(
            f"{artifact_type} omits {', '.join(kinds)}"
            for artifact_type, kinds in sorted(below.items())
        )
        raise PlatformError(
            "POLICY_BELOW_EVIDENCE_FLOOR",
            "The policy drops below the required evidence floor",
            422,
            f"`06` §3.3 is a floor and §4.2 may only add to it (FR-364): {named}. "
            "Submission enforces the union either way, so a policy saved below the floor "
            "would say less than the platform requires — which is the reader of the policy "
            "being misled rather than a gate being opened.",
        )
    # `RL-1301` A.6: a `deployment` entry names an Environment by its slug, and a name no
    # Environment has (`prd` for `prod`) would leave the real target ungated. "Existing"
    # means non-retired (auditor-plans N3). `07` sits left of `06` in DEP-1's order, so this
    # read is permitted.
    for entry in policy.policies:
        if entry.artifact_type == "deployment" and entry.environment is not None:
            await environments.require_existing(
                session,
                entry.environment,
                subject="An approval policy `deployment` entry",
            )
    before = await policy_for(session, workspace_id)

    row = await session.get(ApprovalPolicyRow, workspace_id)
    if row is None:
        session.add(
            ApprovalPolicyRow(workspace_id=workspace_id, policy=policy.model_dump(mode="json"))
        )
    else:
        row.policy = policy.model_dump(mode="json")
        row.updated_at = datetime.now(UTC)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="approval_policy.updated",
        entity_ref="approval_policy:workspace@1",
        before=before.model_dump(mode="json"),
        after=policy.model_dump(mode="json"),
    )
    return policy


async def submit(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    submitter: Principal,
    artifact_ref: ArtifactRef,
    change_summary: str,
    environment: str | None = None,
    resolve: ArtifactResolver | None = None,
    additional_approvers: int = 0,
) -> ApprovalRequestRow:
    """Submit an artifact for approval: `draft → review` (FR-351).

    `additional_approvers` is what the owning module's own requirement adds to the policy
    entry's count (`02` FR-152: a non-convex Custom Objective needs one more). The request
    stores `entry.approvers_required + additional_approvers`, fixed at submission, and the
    submission's audit event records the same number. It defaults to 0, so no other artifact
    type changes, and it is an argument rather than a policy key: a rule a policy edit can
    remove is not a rule (`06` R1).

    `resolve` closes FR-386. Omitting it asserts that the caller already **holds** the
    row it names, which is true of the four module submit paths — `modelling`,
    `objectives`, `metrics` and `perils` each load the artifact, check its status, and build
    the reference out of that row's own slug and version, so a lookup here would re-read a
    row the caller is holding open.

    `POST /approval-requests` is the caller that does not: it takes the reference from the
    client, and it **must** pass a resolver. Without one a request can pin a version that
    was never created — the owning module cannot move an artifact that does not exist, so
    the request decides without effect and there is nothing for a reader to reconcile the
    decision against.
    """
    if not change_summary.strip():
        raise PlatformError(
            "VALIDATION_FAILED",
            "A change summary is required",
            422,
            "FR-352: submission requires a change summary. An approval with no "
            "statement of what changed asks the approver to derive it from a diff.",
        )

    policy = await policy_for(session, workspace_id)
    entry = policy.entry_for(artifact_ref.type, environment)
    if entry is None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "No approval policy for this artifact type",
            422,
            f"The workspace policy defines nothing for {artifact_ref.type!r}. Approving "
            "against no policy would be approving against no requirement.",
        )

    # FR-386, and **after** the policy check on purpose. A `dataset:motor-gb@3` in a
    # workspace whose policy says nothing about datasets earns two correct refusals, and
    # "no approval policy for this artifact type" is the one the submitter can act on;
    # answering "no such version" first would send them off to create a version that still
    # could not be approved. `datasets.load_version` makes the same argument about the same
    # kind of pair — the order of two correct refusals is load-bearing.
    if resolve is not None:
        await resolve(session, workspace_id=workspace_id, artifact_ref=artifact_ref)

    approvers_required = entry.approvers_required + additional_approvers
    row = ApprovalRequestRow(
        workspace_id=workspace_id,
        artifact_ref=str(artifact_ref),
        artifact_type=artifact_ref.type,
        environment=environment,
        submitted_by=submitter.id,
        change_summary=change_summary,
        status=ApprovalStatus.REVIEW.value,
        approvers_required=approvers_required,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This artifact version is already under review",
            409,
            f"{artifact_ref} already has an open approval request. Two open reviews of one "
            "artifact can reach different answers.",
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=submitter,
        source=JobSource.API,
        action="approval_request.submitted",
        entity_ref=str(artifact_ref),
        after={
            "status": ApprovalStatus.REVIEW.value,
            "approvers_required": approvers_required,
        },
        justification=change_summary,
    )
    return row


class EvidenceAuthorResolver(Protocol):
    """Who authored the evidence an approver of this artifact version is shown (`06`
    FR-353, `03` FR-260): for a Rating Version, every author in its golden-quote delta.

    Supplied by the caller, as `ArtifactResolver` is, so governance imports nothing from
    the rating module (DEP-1). It raises rather than returning an empty set on a load or
    parse failure, so a decision is refused rather than made without the check.
    """

    async def __call__(
        self, session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
    ) -> set[UUID]: ...


async def decide(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    request_id: UUID,
    approver: Principal,
    decision: DecisionKind,
    comment: str | None = None,
    evidence_authors: EvidenceAuthorResolver | None = None,
) -> ApprovalRequestRow:
    """Record a decision, enforcing separation of duties (FR-353, FR-355).

    `evidence_authors` is required for a `rating_version` request: a missing resolver is a
    programming error, raised as `TypeError` before any decision row (re-audit N1) — never
    an `assert`, which `python -O` strips.
    """
    row = await _load(session, workspace_id, request_id)
    if row.artifact_type == "rating_version" and evidence_authors is None:
        raise TypeError("decide on a rating_version requires evidence_authors")

    if row.status != ApprovalStatus.REVIEW.value:
        raise PlatformError(
            "APPROVAL_ALREADY_DECIDED",
            "This request is not open",
            409,
            f"The request is {row.status!r}; only a request in review can be decided.",
        )

    # R1, and not configurable. Checked before the permission, because "you may not approve
    # your own work" is a truer answer than "you lack a permission" for a submitter who
    # holds the approver role.
    if row.submitted_by == approver.id:
        raise PlatformError(
            "SUBMITTER_CANNOT_APPROVE",
            "The submitter cannot approve",
            403,
            "`06` R1: separation of duties is enforced in the backend and cannot be "
            "configured away.",
        )

    # FR-353 as amended 2026-09-28: nor the author. After R1, which is the more specific
    # answer for someone who is both, and before the permission for R1's own reason.
    author = await _author_of(session, workspace_id, row)
    if author is None:
        raise PlatformError(
            "APPROVAL_AUTHOR_UNRESOLVED",
            "The author of this version cannot be established",
            403,
            f"{row.artifact_ref} has no creation Audit Event, so whether the approver is "
            "its author cannot be checked. `06` FR-353: an approval that cannot be checked "
            "is refused, never allowed.",
        )
    if author == approver.id:
        raise PlatformError(
            "AUTHOR_CANNOT_APPROVE",
            "The author cannot approve",
            403,
            "`06` FR-353: the approver may be neither the submitter nor the author of the "
            "version under approval.",
        )

    # FR-353, added 2026-09-28 (PL-1189; the deputy's decision on audit finding F4): the
    # suite delta is the evidence the approver judges, so its author cannot judge it. Not
    # the general component-author case, which WK-677 owns.
    if row.artifact_type == "rating_version":
        assert evidence_authors is not None  # narrowed above; refused before this line
        authors = await evidence_authors(
            session, workspace_id=workspace_id,
            artifact_ref=ArtifactRef.model_validate(row.artifact_ref),
        )
        if approver.id in authors:
            raise PlatformError(
                "APPROVAL_BY_EVIDENCE_AUTHOR",
                "An author of a golden-quote change cannot approve",
                403,
                f"{row.artifact_ref}'s golden-quote delta lists a change you authored. "
                "`06` FR-353 and `03` FR-260: the author of the evidence cannot judge it.",
            )

    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=approver,
        permission=Permission.APPROVAL_DECIDE,
    )
    await _check_approver_role(session, workspace_id, approver, row)

    if decision is DecisionKind.REQUEST_CHANGES and not (comment or "").strip():
        raise PlatformError(
            "VALIDATION_FAILED",
            "Requesting changes requires a comment",
            422,
            "FR-355: the request and the resubmission are both audited, so the "
            "reviewer's concerns and their resolution are traceable. A bare rejection "
            "leaves the submitter guessing.",
        )

    session.add(
        ApprovalDecisionRow(
            request_id=row.id,
            approver_id=approver.id,
            decision=decision.value,
            comment=comment,
        )
    )
    try:
        await session.flush()
    except IntegrityError:
        # FR-353: "where two approvals are required they must be distinct Principals".
        raise PlatformError(
            "DUPLICATE_APPROVER",
            "You have already decided on this request",
            409,
            "Two approvals must come from distinct Principals.",
        ) from None

    approvals = await _count_approvals(session, row.id)
    new_status = _resolve_status(decision, approvals, row.approvers_required)
    _require_transition(ApprovalStatus(row.status), new_status)
    async with approval_decision(session):
        row.status = new_status.value
        if new_status is not ApprovalStatus.REVIEW:
            row.decided_at = datetime.now(UTC)
        await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=approver,
        source=JobSource.API,
        action=f"approval_request.{decision.value}",
        entity_ref=row.artifact_ref,
        before={"status": ApprovalStatus.REVIEW.value, "approvers_recorded": approvals - 1},
        after={"status": new_status.value, "approvers_recorded": approvals},
        justification=comment,
    )
    return row


async def withdraw(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    request_id: UUID,
    actor: Principal,
    reason: str,
    artifact_is_live: bool = False,
) -> ApprovalRequestRow:
    """Withdraw before deployment (FR-357).

    `artifact_is_live` is supplied by the caller because liveness belongs to the owning
    module (`03` for a Rating Version), not here. Governance owns the rule; the deployment
    state is somebody else's fact.
    """
    row = await _load(session, workspace_id, request_id)

    if artifact_is_live:
        raise PlatformError(
            "WITHDRAW_AFTER_DEPLOY_FORBIDDEN",
            "Cannot withdraw an approval after deployment",
            409,
            "The artifact is live. The correct action is a rollback or a new version — "
            "withdrawing the approval would leave live behaviour with no approval behind "
            "it (FR-357).",
        )
    if not reason.strip():
        raise PlatformError(
            "VALIDATION_FAILED", "Withdrawal requires a reason", 422, "FR-357."
        )

    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.APPROVAL_DECIDE,
    )
    _require_transition(ApprovalStatus(row.status), ApprovalStatus.WITHDRAWN)

    before = row.status
    row.status = ApprovalStatus.WITHDRAWN.value
    row.withdrawn_reason = reason
    row.decided_at = datetime.now(UTC)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="approval_request.withdrawn",
        entity_ref=row.artifact_ref,
        before={"status": before},
        after={"status": ApprovalStatus.WITHDRAWN.value},
        justification=reason,
    )
    return row


# -- internals ----------------------------------------------------------------------------


async def _load(
    session: AsyncSession, workspace_id: UUID, request_id: UUID
) -> ApprovalRequestRow:
    row = await session.get(ApprovalRequestRow, request_id, with_for_update=True)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Approval request not found", 404, f"No request {request_id}."
        )
    return row


async def _author_of(
    session: AsyncSession, workspace_id: UUID, row: ApprovalRequestRow
) -> UUID | None:
    """The actor of the version's creation Audit Event, or `None` when there is none.

    Read from the audit chain rather than from a row, because four of the seven approvable
    types carry no author column and the chain is the one record every type shares. The
    earliest matching event wins: a version is created once.
    """
    action = CREATION_ACTIONS.get(row.artifact_type)
    if action is None:
        return None
    actor = (
        await session.execute(
            select(AuditEventRow.actor)
            .where(
                AuditEventRow.workspace_id == workspace_id,
                AuditEventRow.entity_ref == row.artifact_ref,
                AuditEventRow.action == action,
            )
            .order_by(AuditEventRow.at)
            .limit(1)
        )
    ).scalar_one_or_none()
    return None if actor is None else UUID(actor["id"])


async def _count_approvals(session: AsyncSession, request_id: UUID) -> int:
    rows = (
        await session.execute(
            select(ApprovalDecisionRow).where(
                ApprovalDecisionRow.request_id == request_id,
                ApprovalDecisionRow.decision == DecisionKind.APPROVE.value,
            )
        )
    ).scalars().all()
    return len(rows)


def _resolve_status(
    decision: DecisionKind, approvals: int, required: int
) -> ApprovalStatus:
    if decision is DecisionKind.REJECT:
        return ApprovalStatus.REJECTED
    if decision is DecisionKind.REQUEST_CHANGES:
        return ApprovalStatus.CHANGES_REQUESTED
    return ApprovalStatus.APPROVED if approvals >= required else ApprovalStatus.REVIEW


def _require_transition(current: ApprovalStatus, target: ApprovalStatus) -> None:
    if current is target:
        return
    if target not in VALID_APPROVAL_TRANSITIONS[current]:
        raise PlatformError(
            "APPROVAL_ALREADY_DECIDED",
            "Invalid approval transition",
            409,
            f"A request in {current.value!r} cannot move to {target.value!r} (FR-351).",
        )


async def _check_approver_role(
    session: AsyncSession,
    workspace_id: UUID,
    approver: Principal,
    row: ApprovalRequestRow,
) -> None:
    """FR-354: the policy names which roles may approve this artifact type."""
    policy = await policy_for(session, workspace_id)
    entry = policy.entry_for(row.artifact_type, row.environment)
    if entry is None:
        return

    held = await _roles_of(session, workspace_id, approver)
    if not held & set(entry.approver_roles):
        raise PlatformError(
            "PERMISSION_DENIED",
            "Your role may not approve this artifact type",
            403,
            f"{row.artifact_type!r} requires one of {list(entry.approver_roles)} "
            "(FR-354).",
        )


async def _roles_of(
    session: AsyncSession, workspace_id: UUID, principal: Principal
) -> set[str]:
    now = datetime.now(UTC)
    rows = (
        await session.execute(
            select(RoleAssignmentRow, RoleRow)
            .join(RoleRow, RoleRow.id == RoleAssignmentRow.role_id)
            .where(
                RoleAssignmentRow.workspace_id == workspace_id,
                RoleAssignmentRow.principal_id == principal.id,
                RoleAssignmentRow.revoked_at.is_(None),
            )
        )
    ).all()
    return {
        role.slug
        for assignment, role in rows
        if assignment.expires_at is None or assignment.expires_at > now
    }


def to_dict(row: ApprovalRequestRow, decisions: list[ApprovalDecisionRow]) -> dict[str, Any]:
    """Serialise for the API."""
    return {
        "id": str(row.id),
        "artifact_ref": row.artifact_ref,
        "artifact_type": row.artifact_type,
        "environment": row.environment,
        "submitted_by": str(row.submitted_by),
        "submitted_at": row.submitted_at.isoformat(),
        "change_summary": row.change_summary,
        "status": row.status,
        "approvers_required": row.approvers_required,
        "approvers_recorded": sum(
            1 for d in decisions if d.decision == DecisionKind.APPROVE.value
        ),
        "decisions": [
            {
                "approver_id": str(d.approver_id),
                "decision": d.decision,
                "at": d.at.isoformat(),
                "comment": d.comment,
            }
            for d in decisions
        ],
        "withdrawn_reason": row.withdrawn_reason,
    }
