"""Approval requests, decisions and policy (`06` §3.2, §4.2, §4.3).

> **R1 — Separation of duties.** The submitter of an approval request can never be its
> approver. This is enforced in the backend, not the UI, and cannot be configured away.

The lifecycle is uniform across artifact types (FR-GOV-9), which is why it lives here
rather than in each owning module: a model, a custom objective and a rating version are
approved by the same machine, and the only thing that differs is the policy that machine
reads.

**Approval is pinned to a version, structurally.** An `ArtifactRef` carries `@version`
(ID-3) and artifacts are immutable (FR-OVR-1), so "the approval does not carry over when a
referenced artifact changes" (FR-GOV-14) needs no staleness check: a changed artifact is a
different reference, and the approval was for the old one.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.refs import ArtifactRef

__all__ = [
    "DEFAULT_POLICY",
    "VALID_APPROVAL_TRANSITIONS",
    "ApprovalDecision",
    "ApprovalPolicy",
    "ApprovalPolicyEntry",
    "ApprovalRequest",
    "ApprovalStatus",
    "DecisionKind",
]


class ApprovalStatus(enum.StrEnum):
    """FR-GOV-9. Post-approval states (`live`, `superseded`, `retired`) belong to the
    owning module — this machine stops at `approved`."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class DecisionKind(enum.StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


#: `changes_requested` returns to `draft` (FR-GOV-13) so a resubmission is a new review
#: rather than a continuation of the old one — the reviewer's concerns and their resolution
#: both being visible is the point.
VALID_APPROVAL_TRANSITIONS: Final[dict[ApprovalStatus, frozenset[ApprovalStatus]]] = {
    ApprovalStatus.DRAFT: frozenset({ApprovalStatus.REVIEW}),
    ApprovalStatus.REVIEW: frozenset(
        {
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.CHANGES_REQUESTED,
            ApprovalStatus.WITHDRAWN,
        }
    ),
    ApprovalStatus.CHANGES_REQUESTED: frozenset({ApprovalStatus.DRAFT}),
    ApprovalStatus.APPROVED: frozenset({ApprovalStatus.WITHDRAWN}),
    ApprovalStatus.REJECTED: frozenset(),
    ApprovalStatus.WITHDRAWN: frozenset(),
}


class ApprovalPolicyEntry(BaseModel):
    """What a given artifact type requires (`06` §4.2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_type: str
    approvers_required: int = Field(ge=1, le=5)
    approver_roles: tuple[str, ...] = Field(min_length=1)
    environment: str | None = Field(
        default=None, description="Rating Version deployments differ per target environment."
    )
    evidence: tuple[str, ...] = ()


class ApprovalPolicy(BaseModel):
    """A workspace's approval policy (FR-GOV-12)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    policies: tuple[ApprovalPolicyEntry, ...] = ()

    #: `06` §4.2 marks this `"configurable": false`. It is a field so the policy document
    #: round-trips, and a validator refuses the value that would disable R1 — a rule that
    #: can be switched off in configuration is not a rule.
    submitter_may_approve: bool = False

    @model_validator(mode="after")
    def _separation_of_duties_is_not_configurable(self) -> ApprovalPolicy:
        if self.submitter_may_approve:
            raise ValueError(
                "submitter_may_approve cannot be true: `06` R1 makes separation of duties "
                "non-configurable, and a rule that configuration can disable is not one"
            )
        return self

    def entry_for(
        self, artifact_type: str, environment: str | None = None
    ) -> ApprovalPolicyEntry | None:
        """The most specific matching entry, environment-qualified first."""
        exact = [
            p
            for p in self.policies
            if p.artifact_type == artifact_type and p.environment == environment
        ]
        if exact:
            return exact[0]
        general = [
            p
            for p in self.policies
            if p.artifact_type == artifact_type and p.environment is None
        ]
        return general[0] if general else None


#: The defaults `06` §4.2 documents. A workspace may edit them; it starts here.
DEFAULT_POLICY: Final[ApprovalPolicy] = ApprovalPolicy(
    policies=(
        ApprovalPolicyEntry(
            artifact_type="validation_rule",
            approvers_required=1,
            approver_roles=("approver", "admin"),
            evidence=("dry_run_result",),
        ),
        ApprovalPolicyEntry(
            artifact_type="custom_objective",
            approvers_required=1,
            approver_roles=("approver",),
            evidence=("objective_certificate",),
        ),
        ApprovalPolicyEntry(
            artifact_type="model",
            approvers_required=1,
            approver_roles=("approver",),
            evidence=("diagnostics",),
        ),
        ApprovalPolicyEntry(
            artifact_type="rating_version",
            approvers_required=2,
            approver_roles=("approver",),
            evidence=("structural_diff", "regression_run", "dislocation_run"),
        ),
    )
)


class ApprovalDecision(BaseModel):
    """One approver's decision (`06` §4.3)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    approver_id: UUID
    decision: DecisionKind
    at: datetime
    comment: str | None = None


class ApprovalRequest(BaseModel):
    """An artifact submitted for approval (`06` §4.3)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    artifact_ref: ArtifactRef
    artifact_type: str
    submitted_by: UUID
    submitted_at: datetime
    change_summary: str
    status: ApprovalStatus
    approvers_required: int = Field(ge=1)
    approvers_recorded: int = Field(ge=0)
    decisions: tuple[ApprovalDecision, ...] = ()
    withdrawn_reason: str | None = None

    @model_validator(mode="after")
    def _recorded_matches_decisions(self) -> ApprovalRequest:
        approvals = sum(1 for d in self.decisions if d.decision is DecisionKind.APPROVE)
        if self.approvers_recorded != approvals:
            raise ValueError(
                f"approvers_recorded ({self.approvers_recorded}) disagrees with the "
                f"{approvals} approve decisions recorded"
            )
        return self
