"""`06` §3.3's evidence floor and how a policy composes with it (FR-GOV-37).

The union lives here rather than in the backend because `EVIDENCE_FLOOR` is a shape that
crosses a boundary (`CLAUDE.md` §2): the backend enforces it at submission, the API refuses a
policy that drops below it, and a second copy of either rule would be a third answer to the
question of what a submission requires — which is the defect OQ-GOV-7 existed to settle.
"""

from __future__ import annotations

import pytest

from model_schema import DEFAULT_POLICY, EVIDENCE_FLOOR, ApprovalPolicy, ApprovalPolicyEntry


@pytest.mark.req("FR-GOV-37")
def test_the_documented_defaults_satisfy_the_floor() -> None:
    """`06` §4.2's defaults are the starting policy, so they must clear their own floor.

    This is the guard on the direction the rule is most easily broken in: a later slice
    trimming a default kind would leave the shipped policy below a floor the platform still
    enforces at submission, and the only symptom would be a refusal nobody could explain
    from the policy document.
    """
    assert DEFAULT_POLICY.below_floor() == {}


@pytest.mark.req("FR-GOV-37")
def test_a_policy_that_drops_a_floor_kind_is_below_the_floor() -> None:
    """Negative: the case OQ-GOV-7 was decided on — editing away `02` §4.8 R3.

    A transparency artifact for a non-GLM model is an invariant of the artifact, not a
    workspace preference, so a policy that omits the kind is reported rather than accepted.
    """
    edited = ApprovalPolicy(
        policies=(
            ApprovalPolicyEntry(
                artifact_type="model",
                approvers_required=1,
                approver_roles=("approver",),
                evidence=("diagnostics",),
            ),
        )
    )
    assert edited.below_floor() == {"model": ("transparency_artifact_if_non_glm",)}


@pytest.mark.req("FR-GOV-37")
def test_submission_reads_the_union_of_floor_and_policy() -> None:
    """A policy may add to the floor, and cannot subtract from it — in one function.

    The empty-evidence entry is not hypothetical: a policy stored before FR-GOV-37 is loaded
    as it was written, and refusing it at read time would lock a workspace out of its own
    approvals.
    """
    added = ApprovalPolicy(
        policies=(
            ApprovalPolicyEntry(
                artifact_type="model",
                approvers_required=1,
                approver_roles=("approver",),
                evidence=("diagnostics", "transparency_artifact_if_non_glm", "backtest"),
            ),
        )
    )
    assert added.effective_evidence("model") == (
        "diagnostics",
        "transparency_artifact_if_non_glm",
        "backtest",
    )

    stripped = ApprovalPolicy(
        policies=(
            ApprovalPolicyEntry(
                artifact_type="model",
                approvers_required=1,
                approver_roles=("approver",),
                evidence=(),
            ),
        )
    )
    assert stripped.effective_evidence("model") == EVIDENCE_FLOOR["model"]


@pytest.mark.req("FR-GOV-37")
def test_an_artifact_type_with_no_floor_row_requires_only_its_policy() -> None:
    """`peril_structure` has no `06` §3.3 row, so its floor is empty — deliberately.

    A floor that says nothing permits anything, which is the right default for an artifact
    type §3.3 predates. Inferring a floor for it would be this file inventing governance the
    specification does not state.
    """
    assert "peril_structure" not in EVIDENCE_FLOOR
    assert DEFAULT_POLICY.effective_evidence("peril_structure") == ("reconciliation",)
    #: And a type no policy names at all requires nothing here — `approvals.submit` refuses
    #: it earlier, with the reason that no policy defines it.
    assert DEFAULT_POLICY.effective_evidence("dossier") == ()
