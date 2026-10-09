"""`06` §3.3's evidence floor and how a policy composes with it (FR-364).

The union lives here rather than in the backend because `EVIDENCE_FLOOR` is a shape that
crosses a boundary (`CLAUDE.md` §2): the backend enforces it at submission, the API refuses a
policy that drops below it, and a second copy of either rule would be a third answer to the
question of what a submission requires — which is the defect OQ-639 existed to settle.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from model_schema import (
    DEFAULT_POLICY,
    EVIDENCE_FLOOR,
    ApprovalPolicy,
    ApprovalPolicyEntry,
    PromotionSkip,
    promotion_order_refusal,
)
from model_schema.approvals import DEFAULT_APPROXIMATION_DEVIATION


@pytest.mark.req("FR-364")
def test_the_documented_defaults_satisfy_the_floor() -> None:
    """`06` §4.2's defaults are the starting policy, so they must clear their own floor.

    This is the guard on the direction the rule is most easily broken in: a later slice
    trimming a default kind would leave the shipped policy below a floor the platform still
    enforces at submission, and the only symptom would be a refusal nobody could explain
    from the policy document.
    """
    assert DEFAULT_POLICY.below_floor() == {}


@pytest.mark.req("FR-364")
def test_a_policy_that_drops_a_floor_kind_is_below_the_floor() -> None:
    """Negative: the case OQ-639 was decided on — editing away `02` §4.8 R3.

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


@pytest.mark.req("FR-364")
def test_submission_reads_the_union_of_floor_and_policy() -> None:
    """A policy may add to the floor, and cannot subtract from it — in one function.

    The empty-evidence entry is not hypothetical: a policy stored before FR-364 is loaded
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


@pytest.mark.req("FR-364")
def test_an_artifact_type_with_no_floor_row_requires_only_its_policy() -> None:
    """`peril_structure` has an empty floor — deliberately, but not for the stated reason.

    **Corrected 2026-08-22 (WK-661, the audit-remediation slice).** This docstring used to say
    `peril_structure` "has no `06` §3.3 row", and it has had one since 2026-08-14 — four
    days before the claim was written. The assertion below survives the correction; the
    justification does not. The row's **reconciliation** half is enforced structurally
    (`review` is reachable only from `reconciled`, and a `fail` verdict is refused at
    submission), so a floor entry would restate a lifecycle edge; its **per-peril model
    approvals** half is enforced nowhere and is FR-364's uncheckable remainder.

    Inferring a floor for it here would still be this file inventing governance the
    specification does not state, which is why the assertion is unchanged.
    """
    assert "peril_structure" not in EVIDENCE_FLOOR
    assert DEFAULT_POLICY.effective_evidence("peril_structure") == ("reconciliation",)
    #: And a type no policy names at all requires nothing here — `approvals.submit` refuses
    #: it earlier, with the reason that no policy defines it.
    assert DEFAULT_POLICY.effective_evidence("dossier") == ()


@pytest.mark.req("FR-363")
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


@pytest.mark.req("FR-363")
def test_the_metric_floor_is_exactly_what_is_checkable() -> None:
    """The floor entry is a *complete* projection of §3.3's row, leaving no remainder.

    `record_certificate` sets `certified` only when `overall` is not `failed` and sets
    `certificate_id` in the same statement, so "Metric Certificate with `overall ≠ failed`"
    is verifiable end to end from the presence of the certificate. Unlike `model`'s
    `model_comparison_if_predecessor`, nothing in this row has to be named in FR-364 as
    an uncheckable leftover — and this test is what stops a later slice widening the row
    into something submission would then fail closed on.
    """
    assert EVIDENCE_FLOOR["custom_metric"] == ("metric_certificate",)
    assert DEFAULT_POLICY.effective_evidence("custom_metric") == ("metric_certificate",)


@pytest.mark.req("FR-364")
def test_the_default_policy_has_a_prod_deployment_entry() -> None:
    """`06` §4.2 shows a `prod` `deployment` entry (`RL-886`); `DEFAULT_POLICY` must carry it.

    Predicted red: `entry_for` returns `None` (premise b, no `deployment` entry), which is why
    `submit` refused a Deployment Request with "no approval policy for this artifact type".
    """
    entry = DEFAULT_POLICY.entry_for("deployment", "prod")
    assert entry is not None
    assert entry.approvers_required == 1
    assert entry.approver_roles == ("deployer",)
    assert entry.environment == "prod"
    assert entry.evidence == EVIDENCE_FLOOR["deployment"]


def _entry_with_skip(**overrides: object) -> ApprovalPolicyEntry:
    fields: dict[str, object] = {
        "artifact_type": "deployment",
        "environment": "prod",
        "approvers_required": 1,
        "approver_roles": ("deployer",),
        "evidence": EVIDENCE_FLOOR["deployment"],
        "skippable_predecessors": ("uat",),
    }
    fields.update(overrides)
    return ApprovalPolicyEntry(**fields)  # type: ignore[arg-type]


@pytest.mark.req("FR-429")
def test_a_skippable_predecessor_is_refused_without_an_environment() -> None:
    """RL-1296 item 5: the field is valid only on the environment-qualified entry.

    Predicted red before the field exists: `extra="forbid"` rejects the unknown field
    (a `ValidationError` naming `skippable_predecessors`). After the field is added without
    the validator, the red becomes "no error raised".
    """
    with pytest.raises(ValidationError, match="skippable_predecessors"):
        _entry_with_skip(environment=None)


@pytest.mark.req("FR-429")
def test_a_skippable_predecessor_is_refused_on_another_artifact_type() -> None:
    """The same refusal for `artifact_type="rating_version"` (RL-1296 item 5)."""
    with pytest.raises(ValidationError, match="skippable_predecessors"):
        _entry_with_skip(artifact_type="rating_version", evidence=())


@pytest.mark.req("FR-429")
def test_a_qualified_deployment_entry_accepts_skippable_predecessors() -> None:
    """Control: the one place the field is valid, so the validator does not over-refuse."""
    assert _entry_with_skip().skippable_predecessors == ("uat",)
    prod = DEFAULT_POLICY.entry_for("deployment", "prod")
    assert prod is not None
    assert prod.skippable_predecessors == ()


def _prod_entry(*skippable: str) -> ApprovalPolicyEntry:
    return _entry_with_skip(skippable_predecessors=tuple(skippable))


_UAT_SKIP = PromotionSkip(skipped_environment="uat", reason="UAT frozen for the release")


@pytest.mark.req("FR-429")
@pytest.mark.parametrize(
    ("label", "entry", "predecessor", "deployed", "skip", "refused"),
    [
        ("no predecessor", None, None, False, None, False),
        ("predecessor deployed", None, "uat", True, None, False),
        ("predecessor deployed, skip ignored", None, "uat", True, _UAT_SKIP, False),
        ("not deployed, no skip", _prod_entry("uat"), "uat", False, None, True),
        ("not deployed, skip permitted", _prod_entry("uat"), "uat", False, _UAT_SKIP, False),
        ("skip, no entry", None, "uat", False, _UAT_SKIP, True),
        ("skip, predecessor not listed", _prod_entry(), "uat", False, _UAT_SKIP, True),
        (
            "skip names another environment",
            _prod_entry("uat"),
            "uat",
            False,
            PromotionSkip(skipped_environment="dev", reason="x"),
            True,
        ),
        (
            "entry names another target",
            _entry_with_skip(environment="uat"),
            "uat",
            False,
            _UAT_SKIP,
            True,
        ),
    ],
)
def test_the_promotion_order_predicate(
    label: str,
    entry: ApprovalPolicyEntry | None,
    predecessor: str | None,
    deployed: bool,
    skip: PromotionSkip | None,
    refused: bool,
) -> None:
    """`07` FR-429's one predicate, over a table (RL-1301 A.5): it reads only its arguments.

    Predicted red before it exists: `ImportError` for `promotion_order_refusal`. Every
    refusal names the target and the predecessor.
    """
    reason = promotion_order_refusal(
        entry,
        target="prod",
        predecessor=predecessor,
        predecessor_deployed=deployed,
        skip=skip,
    )
    assert (reason is not None) is refused, label
    if reason is not None:
        assert "prod" in reason
        assert predecessor is not None
        assert predecessor in reason


@pytest.mark.req("FR-429")
def test_a_blank_skip_reason_is_refused() -> None:
    """A skip whose reason is empty after trimming grants nothing (the reason is required)."""
    with pytest.raises(ValidationError, match="reason"):
        PromotionSkip(skipped_environment="uat", reason="   ")
    blank = PromotionSkip.model_construct(skipped_environment="uat", reason="  ")
    assert (
        promotion_order_refusal(
            _prod_entry("uat"),
            target="prod",
            predecessor="uat",
            predecessor_deployed=False,
            skip=blank,
        )
        is not None
    )


@pytest.mark.req("FR-429")
def test_an_unqualified_entry_carrying_the_field_grants_no_skip() -> None:
    """Hardening (auditor-plans F8): the predicate checks `entry.environment == target`.

    `model_construct` bypasses the validator, so the entry is one the validator would have
    refused; the predicate must still refuse the skip.
    """
    rogue = ApprovalPolicyEntry.model_construct(
        artifact_type="deployment",
        environment=None,
        approvers_required=1,
        approver_roles=("deployer",),
        evidence=(),
        skippable_predecessors=("uat",),
    )
    assert (
        promotion_order_refusal(
            rogue,
            target="prod",
            predecessor="uat",
            predecessor_deployed=False,
            skip=_UAT_SKIP,
        )
        is not None
    )


@pytest.mark.req("FR-257")
def test_the_dislocation_baseline_environment_is_only_on_rating_version_entries() -> None:
    """FR-257 limb (2), DP-S5-1 (a): the baseline Environment lives on the `rating_version`
    entry and nowhere else (`06` §4.2, RL-1504 T5). Before the field exists, `extra="forbid"`
    refuses it everywhere (a `ValidationError` for an unknown field), which is the red; after,
    only a `rating_version` entry accepts it."""
    accepted = ApprovalPolicyEntry(
        artifact_type="rating_version",
        approvers_required=2,
        approver_roles=("approver",),
        dislocation_baseline_environment="uat",
    )
    assert accepted.dislocation_baseline_environment == "uat"
    unset = ApprovalPolicyEntry(
        artifact_type="rating_version", approvers_required=2, approver_roles=("approver",)
    )
    assert unset.dislocation_baseline_environment is None
    with pytest.raises(ValidationError, match="dislocation_baseline_environment"):
        ApprovalPolicyEntry(
            artifact_type="model",
            approvers_required=1,
            approver_roles=("approver",),
            dislocation_baseline_environment="prod",
        )


@pytest.mark.req("FR-257")
def test_a_blank_dislocation_baseline_environment_is_refused() -> None:
    with pytest.raises(ValidationError, match="dislocation_baseline_environment"):
        ApprovalPolicyEntry(
            artifact_type="rating_version",
            approvers_required=2,
            approver_roles=("approver",),
            dislocation_baseline_environment="",
        )


def _rating_version_entry(**extra: object) -> ApprovalPolicyEntry:
    return ApprovalPolicyEntry(
        artifact_type="rating_version",
        approvers_required=2,
        approver_roles=("approver",),
        **extra,  # type: ignore[arg-type]
    )


@pytest.mark.req("FR-224")
def test_the_deviation_threshold_is_only_on_rating_version_entries() -> None:
    """DP-S5-2 (a), RL-1504 T5: FR-224's threshold lives on the `rating_version` entry only.
    Red before the field exists: `extra="forbid"` refuses it on the entry that should hold it."""
    entry = _rating_version_entry(
        approximation_deviation={"quantile": "0.95", "max_abs_change_pct": "5"}
    )
    assert entry.approximation_deviation is not None
    assert entry.approximation_deviation.quantile == Decimal("0.95")
    assert entry.approximation_deviation.max_abs_change_pct == Decimal(5)
    for artifact_type in ("model", "deployment", "peril_structure"):
        with pytest.raises(ValidationError, match="approximation_deviation"):
            ApprovalPolicyEntry(
                artifact_type=artifact_type,
                approvers_required=1,
                approver_roles=("approver",),
                approximation_deviation={"quantile": "0.99", "max_abs_change_pct": "10"},
            )


@pytest.mark.req("FR-224")
def test_the_deviation_threshold_bounds() -> None:
    """The quantile is one of the run's six keys (03 §4.6, so the gate always has a figure to
    read); the maximum is non-negative; a float is refused as money-adjacent decimals are."""
    for quantile in ("0.5", "0.9", "0.95", "0.99", "0.999", "1", "1.0", "0.50"):
        entry = _rating_version_entry(
            approximation_deviation={"quantile": quantile, "max_abs_change_pct": "0"}
        )
        assert entry.approximation_deviation is not None
    for quantile in ("0", "0.75", "1.5", "-0.5"):
        with pytest.raises(ValidationError, match="quantile"):
            _rating_version_entry(
                approximation_deviation={"quantile": quantile, "max_abs_change_pct": "5"}
            )
    with pytest.raises(ValidationError, match="max_abs_change_pct"):
        _rating_version_entry(
            approximation_deviation={"quantile": "0.99", "max_abs_change_pct": "-1"}
        )
    with pytest.raises(ValidationError, match="max_abs_change_pct"):
        _rating_version_entry(
            approximation_deviation={"quantile": "0.99", "max_abs_change_pct": 5.5}
        )


@pytest.mark.req("FR-224")
def test_the_default_policy_carries_the_ruled_default_threshold() -> None:
    """RL-1504 item 7: the maintainer's option D, `{quantile: 0.99, max_abs_change_pct: 10}`,
    on the shipped `rating_version` entry, and the constant an unset entry falls back to."""
    entry = DEFAULT_POLICY.entry_for("rating_version")
    assert entry is not None
    assert entry.approximation_deviation == DEFAULT_APPROXIMATION_DEVIATION
    assert DEFAULT_APPROXIMATION_DEVIATION.quantile == Decimal("0.99")
    assert DEFAULT_APPROXIMATION_DEVIATION.max_abs_change_pct == Decimal(10)
