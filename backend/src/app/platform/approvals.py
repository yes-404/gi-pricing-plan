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

from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalDecisionRow,
    ApprovalPolicyRow,
    ApprovalRequestRow,
    RoleAssignmentRow,
    RoleRow,
)
from app.errors import PlatformError
from app.platform import audit, rbac
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
    "ArtifactResolver",
    "decide",
    "policy_for",
    "set_policy",
    "submit",
    "to_dict",
    "withdraw",
]


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
) -> ApprovalRequestRow:
    """Submit an artifact for approval: `draft → review` (FR-351).

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

    row = ApprovalRequestRow(
        workspace_id=workspace_id,
        artifact_ref=str(artifact_ref),
        artifact_type=artifact_ref.type,
        environment=environment,
        submitted_by=submitter.id,
        change_summary=change_summary,
        status=ApprovalStatus.REVIEW.value,
        approvers_required=entry.approvers_required,
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
            "approvers_required": entry.approvers_required,
        },
        justification=change_summary,
    )
    return row


async def decide(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    request_id: UUID,
    approver: Principal,
    decision: DecisionKind,
    comment: str | None = None,
) -> ApprovalRequestRow:
    """Record a decision, enforcing separation of duties (FR-353, FR-355)."""
    row = await _load(session, workspace_id, request_id)

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
