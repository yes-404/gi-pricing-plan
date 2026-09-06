"""The comparison artifact's invariants (`02` FR-186, §4.11).

The artifact was named in `02` §5.2 from Phase 0 and defined nowhere — no §4 subsection, no
type, no contract. Designing it here means the invariants are a choice, so each of these
tests is the record of one:

* a comparison of fewer than two models is a diagnostics read wearing another name;
* a leader that is not among the values compared is a claim about a model that was not in
  the comparison;
* a double-lift series against itself is a flat line the reader will interpret as agreement.

Every one is a **prohibition**. A shape that can represent a nonsense comparison eventually
holds one, and this artifact is cited in approvals.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    ComparisonMetric,
    ComparisonSummary,
    ComparisonValue,
    DoubleLift,
    DoubleLiftBin,
    MetricDirection,
    ModelComparison,
    RelativityDifference,
    SplitRef,
    Weighting,
    new_uuid7,
)

GLM = "model:motor-ad-frequency@1"
GBM = "model:motor-ad-frequency@2"


def _split() -> SplitRef:
    return SplitRef(split_artifact_id=new_uuid7(), train_part="train", holdout_part="test")


def _metric(**over: object) -> ComparisonMetric:
    base: dict[str, object] = {
        "metric": "gini_normalised",
        "weighting": Weighting.EXPOSURE,
        "direction": MetricDirection.HIGHER_IS_BETTER,
        "values": (
            ComparisonValue(model_ref=GLM, value=0.412),
            ComparisonValue(model_ref=GBM, value=0.430),
        ),
        "leader": GBM,
    }
    base.update(over)
    return ComparisonMetric(**base)  # type: ignore[arg-type]


def _summary(**over: object) -> ComparisonSummary:
    base: dict[str, object] = {
        "model_refs": (GLM, GBM),
        "baseline_ref": GLM,
        "split_ref": _split(),
        "holdout_rows": 78,
        "metrics": (_metric(),),
        "double_lift": (
            DoubleLift(
                baseline_ref=GLM,
                challenger_ref=GBM,
                weighting=Weighting.EXPOSURE,
                bins=(
                    DoubleLiftBin(
                        bin=1, rows=39, actual=0.051,
                        baseline_predicted=0.049, challenger_predicted=0.044,
                    ),
                ),
            ),
        ),
        "relativity_differences": (
            RelativityDifference(
                factor="area",
                level="urban",
                values=(
                    ComparisonValue(model_ref=GLM, value=1.98),
                    ComparisonValue(model_ref=GBM, value=2.04),
                ),
                max_abs_difference=0.06,
            ),
        ),
    }
    base.update(over)
    return ComparisonSummary(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-186")
def test_a_valid_comparison_round_trips() -> None:
    summary = _summary()
    assert ComparisonSummary.model_validate(summary.model_dump(mode="json")) == summary


@pytest.mark.req("FR-186")
def test_a_comparison_of_one_model_is_refused() -> None:
    """FR-186 says "two or more". One model compared against nothing is a diagnostics
    read, and naming it a comparison would let an approval cite it as though a candidate had
    been considered and rejected."""
    with pytest.raises(pydantic.ValidationError):
        _summary(model_refs=(GLM,), double_lift=(), relativity_differences=())


@pytest.mark.req("FR-186")
def test_the_baseline_must_be_one_of_the_models_compared() -> None:
    """Double lift is measured *against* the baseline. A baseline outside the set is a
    series whose reference line came from a model the reader cannot look up."""
    with pytest.raises(pydantic.ValidationError):
        _summary(baseline_ref="model:something-else@3")


@pytest.mark.req("FR-186")
def test_a_metrics_leader_must_be_among_its_own_values() -> None:
    with pytest.raises(pydantic.ValidationError):
        _metric(leader="model:not-in-this-comparison@9")


@pytest.mark.req("FR-186")
def test_a_metric_may_have_no_leader() -> None:
    """Not every metric orders. `rows` is the same number for every model on a shared
    holdout, and a "winner" on it would be an artefact of tie-breaking."""
    assert _metric(metric="rows", leader=None).leader is None


@pytest.mark.req("FR-186")
def test_a_metric_needs_a_value_for_every_model() -> None:
    """A missing model reads as a model that scored nothing rather than one nobody measured.
    Where a metric genuinely does not apply, the *value* is null and the model is present."""
    with pytest.raises(pydantic.ValidationError):
        _summary(
            metrics=(
                _metric(
                    values=(ComparisonValue(model_ref=GLM, value=0.4),), leader=GLM
                ),
            )
        )


@pytest.mark.req("FR-186")
def test_a_double_lift_series_against_itself_is_refused() -> None:
    """It is a flat line at 1.0, which a reader will take for two models agreeing."""
    with pytest.raises(pydantic.ValidationError):
        DoubleLift(
            baseline_ref=GLM,
            challenger_ref=GLM,
            weighting=Weighting.EXPOSURE,
            bins=(
                DoubleLiftBin(
                    bin=1, rows=1, actual=0.05,
                    baseline_predicted=0.05, challenger_predicted=0.05,
                ),
            ),
        )


@pytest.mark.req("FR-186")
def test_a_relativity_difference_may_be_unavailable_rather_than_zero() -> None:
    """The defect the spine audit found, in its second home. A relativity is `exp(β)` and
    means nothing under `logit` or `identity`; reporting the *difference* as 0.0 there would
    say the two models agree about a factor neither expresses multiplicatively."""
    unavailable = RelativityDifference(
        factor="area",
        level="urban",
        values=(
            ComparisonValue(model_ref=GLM, value=None),
            ComparisonValue(model_ref=GBM, value=None),
        ),
        max_abs_difference=None,
    )
    assert unavailable.max_abs_difference is None


@pytest.mark.req("FR-186")
def test_the_persisted_artifact_carries_its_identity_and_the_summary() -> None:
    """The `Diagnostics` pattern: `pricing-core` computes a summary and allocates nothing;
    the backend wraps it with an id, a time and the Job that produced it."""
    comparison = ModelComparison(
        id=new_uuid7(),
        computed_at="2026-08-17T12:00:00Z",  # type: ignore[arg-type]
        job_id=new_uuid7(),
        summary=_summary(),
    )
    assert comparison.summary.baseline_ref == GLM
    assert ModelComparison.model_validate(comparison.model_dump(mode="json")) == comparison


@pytest.mark.req("FR-171")
def test_partition_diagnostics_no_longer_declares_double_lift() -> None:
    """Amended 2026-08-17. FR-171 listed "double lift vs a comparison model" among
    *universal* diagnostics, and the field was populated by nothing — it could not be.
    Double lift is pairwise, the comparison model is unknown at fit time, and FR-170
    makes diagnostics computed once and read thereafter. It lives on the comparison artifact.

    `extra="forbid"` is what makes the removal assertable rather than merely intended.
    """
    from model_schema import PartitionDiagnostics

    assert "double_lift" not in PartitionDiagnostics.model_fields
    with pytest.raises(pydantic.ValidationError):
        PartitionDiagnostics(
            weighting=Weighting.EXPOSURE,
            rows=10,
            ae_overall=1.0,
            gini=0.2,
            gini_normalised=0.3,
            double_lift=None,  # type: ignore[call-arg]
        )
