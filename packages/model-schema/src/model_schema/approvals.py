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
    "EVIDENCE_FLOOR",
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


#: `06` §3.3's per-artifact evidence table, as the **floor** a workspace policy may add to
#: and may never remove from (FR-GOV-37, OQ-GOV-7 decided 2026-08-18).
#:
#: This is §3.3's **checkable projection**, not the whole table, and the difference is
#: deliberate: submission fails closed on an evidence kind it cannot verify (`06` R4), so a
#: floor naming `model_comparison_if_predecessor` — which lives inside a comparison's
#: `payload` and cannot be queried — would refuse every model submission rather than raise
#: the standard. The uncheckable remainder is named in FR-GOV-37 with an owner, which is
#: the difference between a deferral and a silence.
#:
#: An artifact type absent here has an **empty** floor. `peril_structure` is that case.
#:
#: **Corrected 2026-08-22 (W5, the audit-remediation slice).** Until this date both this
#: docstring and FR-GOV-37 justified that empty floor by saying `peril_structure` "has no
#: §3.3 row at all". It has had one since 2026-08-14 — four days *before* the claim was
#: written, in the Phase 0 commit that created the document. The conclusion survives the
#: premise, but only for one half of the row and for a different reason: the
#: **reconciliation** is enforced structurally, since `review` is reachable only from
#: `reconciled` and a `fail` verdict is refused at submission, so a floor entry here would
#: restate a lifecycle edge. The row's other half — **per-peril model approvals** — is
#: enforced nowhere, and is FR-GOV-37's uncheckable remainder rather than something this
#: floor's silence permits.
EVIDENCE_FLOOR: Final[dict[str, tuple[str, ...]]] = {
    "validation_rule": ("dry_run_result",),
    "custom_objective": ("objective_certificate",),
    "custom_metric": ("metric_certificate",),
    "model": ("diagnostics", "transparency_artifact_if_non_glm"),
    "rating_version": ("structural_diff", "regression_run", "dislocation_run"),
    "deployment": ("rating_version_approval", "uat_deployment"),
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

    def effective_evidence(
        self, artifact_type: str, environment: str | None = None
    ) -> tuple[str, ...]:
        """What a submission of this artifact type must actually show (FR-GOV-37).

        The union of `EVIDENCE_FLOOR` and the matching entry's own `evidence`, floor first
        and order otherwise preserved. It is a union rather than a lookup because a policy
        stored before FR-GOV-37 existed is still loaded by `policy_for`: refusing it at
        read time would lock a workspace out of its own approvals, and trusting it would
        let the floor be dodged by being old.
        """
        entry = self.entry_for(artifact_type, environment)
        required = list(EVIDENCE_FLOOR.get(artifact_type, ()))
        if entry is not None:
            required += [kind for kind in entry.evidence if kind not in required]
        return tuple(required)

    def below_floor(self) -> dict[str, tuple[str, ...]]:
        """Entries whose `evidence` drops below `EVIDENCE_FLOOR`, by artifact type.

        Empty for a policy that satisfies FR-GOV-37. `set_policy` refuses a non-empty
        result: `effective_evidence` would enforce the floor anyway, so this exists to stop
        a policy document from *saying* less than the platform enforces — an insurer
        reading its own policy is entitled to see what a submission will be held to.
        """
        below: dict[str, tuple[str, ...]] = {}
        for entry in self.policies:
            missing = tuple(
                kind
                for kind in EVIDENCE_FLOOR.get(entry.artifact_type, ())
                if kind not in entry.evidence
            )
            if missing:
                below[entry.artifact_type] = missing
        return below


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
        # FR-MODEL-45: a Custom Metric follows the same lifecycle and grammar as an
        # objective, and `platform.metrics._require_evidence` has expected this entry
        # (`metric_certificate`, mirroring `objective_certificate` above) since the slice
        # that added `submit`. Its absence was a self-documented gap, not a design choice:
        # without it, `certified -> review` 409s in every workspace on "no approval policy
        # for this artifact type" before `_require_evidence` is ever reached, and
        # `review -> approved` was unreachable regardless (see `apply_approval_decision`).
        ApprovalPolicyEntry(
            artifact_type="custom_metric",
            approvers_required=1,
            approver_roles=("approver",),
            evidence=("metric_certificate",),
        ),
        # `transparency_artifact_if_non_glm` joined this entry on 2026-08-18 with
        # FR-GOV-37. It was enforced before it was named — `02` §4.8 R3 is checked at
        # submission whatever the policy says — but a default that omits the kind teaches a
        # workspace editing its policy that the kind is optional, and it is not. The name is
        # `06` §4.2's, which the submission check had been spelling `transparency_artifact`:
        # a workspace copying the kind off the page got a fail-closed refusal for evidence
        # it had.
        ApprovalPolicyEntry(
            artifact_type="model",
            approvers_required=1,
            approver_roles=("approver",),
            evidence=("diagnostics", "transparency_artifact_if_non_glm"),
        ),
        # Added 2026-08-18 (W5, peril structures). FR-MODEL-61 makes a Peril Structure
        # approvable and `peril_structure` has been a valid artifact type since Phase 0 —
        # but with no entry here `submit` refuses with "no approval policy for this
        # artifact type", which is a correct refusal of an artifact nobody could ever
        # approve. Its evidence is the reconciliation, because FR-MODEL-60 makes that the
        # coherence check the approver is being asked to accept.
        ApprovalPolicyEntry(
            artifact_type="peril_structure",
            approvers_required=1,
            approver_roles=("approver",),
            evidence=("reconciliation",),
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
