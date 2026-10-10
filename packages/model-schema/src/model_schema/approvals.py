"""Approval requests, decisions and policy (`06` §3.2, §4.2, §4.3).

> **R1 — Separation of duties.** The submitter of an approval request can never be its
> approver. This is enforced in the backend, not the UI, and cannot be configured away.

The lifecycle is uniform across artifact types (FR-351), which is why it lives here
rather than in each owning module: a model, a custom objective and a rating version are
approved by the same machine, and the only thing that differs is the policy that machine
reads.

**Approval is pinned to a version, structurally.** An `ArtifactRef` carries `@version`
(ID-3) and artifacts are immutable (FR-4), so "the approval does not carry over when a
referenced artifact changes" (FR-356) needs no staleness check: a changed artifact is a
different reference, and the approval was for the old one.
"""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from model_schema.dislocation import ABS_CHANGE_PCT_QUANTILE_KEYS
from model_schema.money import DecimalStr
from model_schema.refs import ArtifactRef

__all__ = [
    "DEFAULT_APPROXIMATION_DEVIATION",
    "DEFAULT_DISLOCATION_BASELINE_ENVIRONMENT",
    "DEFAULT_POLICY",
    "EVIDENCE_FLOOR",
    "VALID_APPROVAL_TRANSITIONS",
    "ApprovalDecision",
    "ApprovalPolicy",
    "ApprovalPolicyEntry",
    "ApprovalRequest",
    "ApprovalStatus",
    "ApprovalSubmission",
    "ApprovalWithdrawal",
    "ApproximationDeviation",
    "Decide",
    "DecisionKind",
    "PromotionSkip",
    "promotion_order_refusal",
]


class ApprovalStatus(enum.StrEnum):
    """FR-351. Post-approval states (`live`, `superseded`, `retired`) belong to the
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


class Decide(BaseModel):
    """The body of `POST /approval-requests/{id}/decide`."""

    model_config = ConfigDict(extra="forbid")

    decision: DecisionKind
    comment: str | None = None


#: `changes_requested` returns to `draft` (FR-355) so a resubmission is a new review
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
#: and may never remove from (FR-364, OQ-639 decided 2026-08-18).
#:
#: This is §3.3's **checkable projection**, not the whole table, and the difference is
#: deliberate: submission fails closed on an evidence kind it cannot verify (`06` R4), so a
#: floor naming `model_comparison_if_predecessor` — which lives inside a comparison's
#: `payload` and cannot be queried — would refuse every model submission rather than raise
#: the standard. The uncheckable remainder is named in FR-364 with an owner, which is
#: the difference between a deferral and a silence.
#:
#: An artifact type absent here has an **empty** floor. `peril_structure` is that case.
#:
#: **Corrected 2026-08-22 (WK-661, the audit-remediation slice).** Until this date both this
#: docstring and FR-364 justified that empty floor by saying `peril_structure` "has no
#: §3.3 row at all". It has had one since 2026-08-14 — four days *before* the claim was
#: written, in the Phase 0 commit that created the document. The conclusion survives the
#: premise, but only for one half of the row and for a different reason: the
#: **reconciliation** is enforced structurally, since `review` is reachable only from
#: `reconciled` and a `fail` verdict is refused at submission, so a floor entry here would
#: restate a lifecycle edge. The row's other half — **per-peril model approvals** — is
#: enforced nowhere until 2026-10-10, and was FR-364's uncheckable remainder rather than
#: something this floor's silence permits. **Corrected 2026-10-10 (WK-1178, SL-1462, FD-1456):**
#: it is enforced now, at approval, by `backend/src/app/platform/perils.py:708`
#: (`_require_approved_components`), which reads the stored `perils` and refuses a structure
#: whose component model is not approved (the maintainer's (by delegation) entry
#: "2026-10-10 06:15:34 BST" in `to-lead.md`, a local file).
EVIDENCE_FLOOR: Final[dict[str, tuple[str, ...]]] = {
    "validation_rule": ("dry_run_result",),
    "custom_objective": ("objective_certificate",),
    "custom_metric": ("metric_certificate",),
    "model": ("diagnostics", "transparency_artifact_if_non_glm"),
    "rating_version": ("structural_diff", "regression_run", "dislocation_run"),
    "deployment": ("rating_version_approval", "uat_deployment"),
}


#: The Environment whose live version is FR-257 limb (2)'s baseline when a `rating_version`
#: policy entry names none (`03` FR-257's 2026-10-10 clarification, `06` §4.2). It is the slug
#: `DEFAULT_POLICY`'s `deployment` entry already uses.
DEFAULT_DISLOCATION_BASELINE_ENVIRONMENT: Final = "prod"


class ApproximationDeviation(BaseModel):
    """FR-224's threshold: a maximum absolute percentage deviation at a declared portfolio
    quantile (`03` FR-224, `06` §4.2; DP-S5-2, RL-1504 T4/T5).

    The quantile is one of the six a Dislocation Run reports (`abs_change_pct_quantiles`, `03`
    §4.6), so the gate always has a figure to read; `quantile_key` is the run's key for it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    quantile: DecimalStr
    max_abs_change_pct: DecimalStr

    @property
    def quantile_key(self) -> str:
        return format(self.quantile.normalize(), "f")

    @model_validator(mode="after")
    def _within_bounds(self) -> ApproximationDeviation:
        if self.quantile_key not in ABS_CHANGE_PCT_QUANTILE_KEYS:
            raise ValueError(
                f"quantile must be one of {list(ABS_CHANGE_PCT_QUANTILE_KEYS)} "
                "(03 §4.6, the run's fixed set)"
            )
        if self.max_abs_change_pct < 0:
            raise ValueError("max_abs_change_pct must be at least 0")
        return self


#: The threshold an `approximation_deviation`-less `rating_version` entry is governed by: the
#: maintainer's option D (RL-1504 item 7). No value switches the gate off; an unset field is this.
DEFAULT_APPROXIMATION_DEVIATION: Final = ApproximationDeviation(
    quantile=Decimal("0.99"), max_abs_change_pct=Decimal(10)
)


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
    skippable_predecessors: tuple[str, ...] = Field(
        default=(),
        description=(
            "Predecessor Environment slugs a deployment into this entry's environment may "
            "skip (`03` FR-429, RL-1296). Empty by default; valid only on a `deployment` "
            "entry that names an environment."
        ),
    )

    approximation_deviation: ApproximationDeviation | None = Field(
        default=None,
        description=(
            "FR-224's threshold for an `approximation`-mode Rating Version (`06` §4.2, "
            "RL-1504 T5). Unset means `DEFAULT_APPROXIMATION_DEVIATION`; no value switches "
            "the gate off. Valid only on a `rating_version` entry; never a Setting."
        ),
    )
    dislocation_baseline_environment: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "The Environment slug whose live Rating Version is FR-257 limb (2)'s baseline "
            "(`06` §4.2, RL-1504 T5). Unset means `DEFAULT_DISLOCATION_BASELINE_ENVIRONMENT`. "
            "Valid only on a `rating_version` entry."
        ),
    )

    @model_validator(mode="after")
    def _baseline_environment_is_only_on_a_rating_version_entry(
        self,
    ) -> ApprovalPolicyEntry:
        if self.artifact_type != "rating_version":
            for name in ("dislocation_baseline_environment", "approximation_deviation"):
                if getattr(self, name) is not None:
                    raise ValueError(
                        f"{name} is valid only on a `rating_version` entry (`06` §4.2, RL-1504 T5)"
                    )
        return self

    @model_validator(mode="after")
    def _skip_permission_is_only_on_a_qualified_deployment_entry(
        self,
    ) -> ApprovalPolicyEntry:
        """RL-1296 item 5: the skip permission has one home, and it is not the fallback.

        An unqualified entry applies to every environment, so a skip listed there would
        let any target skip its predecessor; the field is refused unless the entry is the
        `deployment` entry of one named environment.
        """
        if self.skippable_predecessors and (
            self.artifact_type != "deployment" or self.environment is None
        ):
            raise ValueError(
                "skippable_predecessors is valid only on a `deployment` entry that names an "
                "environment (`06` §4.2, RL-1296)"
            )
        return self


class ApprovalPolicy(BaseModel):
    """A workspace's approval policy (FR-354)."""

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
        """What a submission of this artifact type must actually show (FR-364).

        The union of `EVIDENCE_FLOOR` and the matching entry's own `evidence`, floor first
        and order otherwise preserved. It is a union rather than a lookup because a policy
        stored before FR-364 existed is still loaded by `policy_for`: refusing it at
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

        Empty for a policy that satisfies FR-364. `set_policy` refuses a non-empty
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


class PromotionSkip(BaseModel):
    """A recorded skip of a predecessor Environment (`03` §4.12, `07` FR-429, RL-1296)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    skipped_environment: str = Field(description="The predecessor Environment's slug.")
    reason: str = Field(description="Why the order was skipped; never empty after trimming.")

    @field_validator("reason")
    @classmethod
    def _reason_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("a promotion skip needs a reason that is not empty after trimming")
        return value


def promotion_order_refusal(
    entry: ApprovalPolicyEntry | None,
    *,
    target: str,
    predecessor: str | None,
    predecessor_deployed: bool,
    skip: PromotionSkip | None,
) -> str | None:
    """`07` FR-429's one predicate: `None` when the order holds, otherwise why not.

    Satisfied when the target has no predecessor or the predecessor is deployed. Otherwise it
    is satisfied only by a skip that names the predecessor, carries a reason, and rests on an
    `entry` that names this `target` and lists the predecessor in `skippable_predecessors`.
    The `entry.environment == target` test is hardening (auditor-plans F8): an unqualified
    entry that somehow carried the field grants nothing. It reads only its arguments, so `06`
    receives deployment facts from its caller and imports nothing from `03` (DEP-1).
    """
    if predecessor is None or predecessor_deployed:
        return None
    where = f"{target!r} requires a successful deployment to {predecessor!r} first"
    if skip is None:
        return f"{where}, and no skip was given"
    if skip.skipped_environment != predecessor:
        return f"{where}; the skip names {skip.skipped_environment!r}, not {predecessor!r}"
    if not skip.reason.strip():
        return f"{where}; the skip of {predecessor!r} has no reason"
    if entry is None or entry.environment != target:
        return f"{where}; no deployment policy entry for {target!r} permits a skip"
    if predecessor not in entry.skippable_predecessors:
        return f"{where}; the policy for {target!r} does not permit skipping {predecessor!r}"
    return None


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
        # FR-154: a Custom Metric follows the same lifecycle and grammar as an
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
        # FR-364. It was enforced before it was named — `02` §4.8 R3 is checked at
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
        # Added 2026-08-18 (WK-661, peril structures). FR-191 makes a Peril Structure
        # approvable and `peril_structure` has been a valid artifact type since Phase 0 —
        # but with no entry here `submit` refuses with "no approval policy for this
        # artifact type", which is a correct refusal of an artifact nobody could ever
        # approve. Its evidence is the reconciliation, because FR-190 makes that the
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
            approximation_deviation=DEFAULT_APPROXIMATION_DEVIATION,
        ),
        # Added 2026-10-03 (WK-674 Slice 2, RL-886). `06` §4.2 shows this entry and §3.3's
        # floor names `deployment`, but the code had no entry, so `submit` refused a
        # Deployment Request with "no approval policy for this artifact type". The
        # `environment` is an Environment's slug (`07` §4.2).
        ApprovalPolicyEntry(
            artifact_type="deployment",
            environment="prod",
            approvers_required=1,
            approver_roles=("deployer",),
            evidence=("rating_version_approval", "uat_deployment"),
        ),
    )
)


class ApprovalSubmission(BaseModel):
    """The body of `POST /api/v1/approval-requests` (`06` §5.1): an artifact put forward.

    Moved here from the API module (WK-674 Slice 2, `PL-1392` Acceptance 16, DP-S2-6 (c)) so the
    request body is a published shape rather than a class the backend defines. The route's 2xx
    stays untyped until `FD-1335` Part B (owner FD 9752).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_ref: str = Field(description="Canonical `{type}:{slug}@{version}` (ID-3).")
    change_summary: str = Field(min_length=1)
    environment: str | None = None


class ApprovalWithdrawal(BaseModel):
    """The body of `POST /api/v1/approval-requests/{request_id}/withdraw` (`06` §5.1, FR-357).

    `reason` only. Whether the artifact is live is the server's to derive from the owning
    module's rows (`PL-1392` Task 6, C11): a field the client could set was a client asserting
    "not live". Moved here from the API module for `ApprovalSubmission`'s reason; the route's
    2xx stays untyped until `FD-1335` Part B (owner FD 9752).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    reason: str = Field(min_length=1)


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
    #: The target environment of a deployment approval request; `None` for every other type
    #: (DP-3 (a), RL-1522).
    environment: str | None = None
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
