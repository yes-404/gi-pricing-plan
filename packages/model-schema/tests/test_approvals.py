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
    """`peril_structure` has an empty floor — deliberately, but not for the stated reason.

    **Corrected 2026-08-22 (W5, the audit-remediation slice).** This docstring used to say
    `peril_structure` "has no `06` §3.3 row", and it has had one since 2026-08-14 — four
    days before the claim was written. The assertion below survives the correction; the
    justification does not. The row's **reconciliation** half is enforced structurally
    (`review` is reachable only from `reconciled`, and a `fail` verdict is refused at
    submission), so a floor entry would restate a lifecycle edge; its **per-peril model
    approvals** half is enforced nowhere and is FR-GOV-37's uncheckable remainder.

    Inferring a floor for it here would still be this file inventing governance the
    specification does not state, which is why the assertion is unchanged.
    """
    assert "peril_structure" not in EVIDENCE_FLOOR
    assert DEFAULT_POLICY.effective_evidence("peril_structure") == ("reconciliation",)
    #: And a type no policy names at all requires nothing here — `approvals.submit` refuses
    #: it earlier, with the reason that no policy defines it.
    assert DEFAULT_POLICY.effective_evidence("dossier") == ()


@pytest.mark.req("FR-GOV-19")
def test_a_policy_that_drops_the_metric_certificate_is_below_the_floor() -> None:
    """Negative: `custom_metric` gained a `06` §3.3 row and a floor entry on 2026-08-22.

    Before that date §4.2's `DEFAULT_POLICY` named `metric_certificate` for `custom_metric`
    while §3.3 had no row for it, so `EVIDENCE_FLOOR` had no key and `below_floor()`
    returned nothing — a workspace could edit the kind out of its own policy and be
    accepted. That was never exploitable (the lifecycle refuses an uncertified metric at
    submission regardless), but the policy reader was told a floor existed where none did,
    which is precisely what `POLICY_BELOW_EVIDENCE_FLOOR` was added to prevent.
    """
    edited = ApprovalPolicy(
        policies=(
            ApprovalPolicyEntry(
                artifact_type="custom_metric",
                approvers_required=1,
                approver_roles=("approver",),
                evidence=(),
            ),
        )
    )
    assert edited.below_floor() == {"custom_metric": ("metric_certificate",)}


@pytest.mark.req("FR-GOV-19")
def test_the_metric_floor_is_exactly_what_is_checkable() -> None:
    """The floor entry is a *complete* projection of §3.3's row, leaving no remainder.

    `record_certificate` sets `certified` only when `overall` is not `failed` and sets
    `certificate_id` in the same statement, so "Metric Certificate with `overall ≠ failed`"
    is verifiable end to end from the presence of the certificate. Unlike `model`'s
    `model_comparison_if_predecessor`, nothing in this row has to be named in FR-GOV-37 as
    an uncheckable leftover — and this test is what stops a later slice widening the row
    into something submission would then fail closed on.
    """
    assert EVIDENCE_FLOOR["custom_metric"] == ("metric_certificate",)
    assert DEFAULT_POLICY.effective_evidence("custom_metric") == ("metric_certificate",)
