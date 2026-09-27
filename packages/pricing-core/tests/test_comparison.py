"""Model comparison (`02` FR-186, §5.2).

Built on `test_diagnostics`' book, where three areas carry true relativities of 1, 2 and 3
against exposure — so a **good** model and a **bad** one can be constructed on purpose:

* the good model is fitted on `area`, the factor that drives the risk;
* the bad model is fitted on `noise`, which is independent of it.

That makes every assertion here about a number the test knows in advance. A comparison suite
that only checks the fields are populated passes just as happily on a leader chosen by
whichever model happened to come first.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Factor,
    FactorType,
    GlmSpec,
    MetricDirection,
    OffsetSpec,
    SplitRef,
    Weighting,
    WeightSpec,
    new_uuid7,
)
from pricing_core.modelling import fit_glm
from pricing_core.modelling.comparison import ComparisonCandidate, compare_models
from pricing_core.modelling.errors import ModellingError

TRUE = {"a": 1.0, "b": 2.0, "c": 3.0}
BASE_RATE = 0.10
GOOD = "model:freq-area@1"
BAD = "model:freq-noise@1"

#: **One** split, cited by every candidate. `01` FR-76 records the split on the parent
#: version precisely so that "the same holdout" is one artifact two models cite; a fixture
#: that gave each candidate its own would be testing the comparison against exactly the
#: belief the requirement exists to remove.
SHARED_SPLIT = SplitRef(split_artifact_id=new_uuid7(), train_part="train", holdout_part="test")


def _book(n: int = 4000, seed: int = 20260817) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    area = rng.choice(list(TRUE), size=n)
    exposure = rng.uniform(0.5, 1.5, size=n)
    lam = np.array([BASE_RATE * TRUE[a] for a in area]) * exposure
    return pl.DataFrame(
        {
            "area": area,
            "noise": rng.choice(["x", "y"], size=n),
            "exposure_years": exposure,
            "claim_count": rng.poisson(lam).astype(float),
            # Strictly positive, so a Gamma severity model can be fitted on it. It exists
            # only for the weighting-mismatch test: a severity model is precisely the thing
            # FR-184 says must not share a metric table with a frequency model.
            "avg_cost": rng.gamma(shape=2.0, scale=900.0, size=n),
        }
    )


def _factor(slug: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(slug,),
    )


def _spec(factors: list[Factor], **over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "freq",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "factors": tuple(f.id for f in factors),
        "family": "poisson",
        "split_ref": SHARED_SPLIT,
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


def _candidate(ref: str, frame: pl.DataFrame, slug: str, **over: object) -> ComparisonCandidate:
    factors = [_factor(slug)]
    spec = _spec(factors, **over)
    fit = fit_glm(frame, spec, factors).result
    return ComparisonCandidate(ref=ref, fit=fit, spec=spec, factors=tuple(factors))


@pytest.fixture(scope="module")
def book() -> pl.DataFrame:
    return _book()


@pytest.fixture(scope="module")
def candidates(book: pl.DataFrame) -> tuple[ComparisonCandidate, ComparisonCandidate]:
    train = book[:3000]
    return _candidate(GOOD, train, "area"), _candidate(BAD, train, "noise")


@pytest.mark.req("FR-186")
def test_the_better_model_leads_on_gini(book, candidates) -> None:
    """`area` drives the risk and `noise` does not, so the ordering is known before the run.
    A leader picked by list order would pass a test that only checked a leader exists."""
    good, bad = candidates
    summary = compare_models([good, bad], book[3000:])

    gini = next(m for m in summary.metrics if m.metric == "gini_normalised")
    assert gini.direction is MetricDirection.HIGHER_IS_BETTER
    assert gini.leader == GOOD
    values = {v.model_ref: v.value for v in gini.values}
    assert values[GOOD] is not None
    assert values[BAD] is not None
    assert values[GOOD] > values[BAD]


@pytest.mark.req("FR-186")
def test_deviance_is_lower_is_better(book, candidates) -> None:
    good, bad = candidates
    summary = compare_models([good, bad], book[3000:])

    metric = next(m for m in summary.metrics if m.metric == "holdout_deviance")
    assert metric.direction is MetricDirection.LOWER_IS_BETTER
    values = {v.model_ref: v.value for v in metric.values}
    assert values[GOOD] < values[BAD]
    assert metric.leader == GOOD


@pytest.mark.req("FR-184")
def test_a_e_leads_on_the_model_closest_to_one_not_the_highest(book, candidates) -> None:
    """The reason `MetricDirection` has three arms rather than being a boolean. An A/E of
    1.4 and one of 0.6 are equally wrong, and a higher-is-better ranking puts 1.4 first."""
    good, bad = candidates
    summary = compare_models([good, bad], book[3000:])

    ae = next(m for m in summary.metrics if m.metric == "ae_overall")
    assert ae.direction is MetricDirection.CLOSER_TO_ONE_IS_BETTER
    values = {v.model_ref: v.value for v in ae.values}
    assert ae.leader == min(values, key=lambda ref: abs(values[ref] - 1.0))


@pytest.mark.req("FR-186")
def test_the_row_count_is_reported_and_orders_nothing(book, candidates) -> None:
    """Every model sees the same holdout, so a winner on `rows` would be pure tie-break."""
    good, bad = candidates
    holdout = book[3000:]
    summary = compare_models([good, bad], holdout)

    rows = next(m for m in summary.metrics if m.metric == "rows")
    assert rows.direction is MetricDirection.NOT_ORDERED
    assert rows.leader is None
    assert {v.value for v in rows.values} == {float(holdout.height)}
    assert summary.holdout_rows == holdout.height


@pytest.mark.req("FR-186")
def test_double_lift_bins_by_the_ratio_and_conserves_the_holdout(book, candidates) -> None:
    """The ordering is what makes the chart answer "where they disagree, who is right?".

    Two properties pin it: the ratio of challenger to baseline prediction must **increase**
    across bins, and the rows must partition the holdout exactly — a binning that dropped or
    double-counted rows would show a chart of a book nobody holds.
    """
    good, bad = candidates
    holdout = book[3000:]
    summary = compare_models([good, bad], holdout, baseline=GOOD)

    assert len(summary.double_lift) == 1
    series = summary.double_lift[0]
    assert series.baseline_ref == GOOD
    assert series.challenger_ref == BAD
    assert series.weighting is Weighting.EXPOSURE

    assert sum(b.rows for b in series.bins) == holdout.height
    ratios = [b.challenger_predicted / b.baseline_predicted for b in series.bins]
    assert ratios == sorted(ratios), ratios


@pytest.mark.req("FR-186")
def test_the_baseline_defaults_to_the_first_candidate(book, candidates) -> None:
    good, bad = candidates
    summary = compare_models([bad, good], book[3000:])
    assert summary.baseline_ref == BAD
    assert summary.double_lift[0].challenger_ref == GOOD


@pytest.mark.req("FR-186")
def test_relativity_differences_name_the_gap_per_level(book, candidates) -> None:
    """The comparison an actuary argues from. Both models here are multiplicative, and only
    the good one has `area`, so `area`'s levels appear with a value for one model and `None`
    for the other — present, not dropped."""
    good, bad = candidates
    summary = compare_models([good, bad], book[3000:])

    by_level = {(d.factor, d.level): d for d in summary.relativity_differences}
    assert ("area", "b") in by_level
    urban = by_level[("area", "b")]
    values = {v.model_ref: v.value for v in urban.values}
    assert values[GOOD] is not None
    assert values[BAD] is None, "the noise model has no `area` relativity to report"
    assert urban.max_abs_difference is None, "one value is not a difference"


@pytest.mark.req("FR-186")
def test_a_comparison_of_one_model_is_refused(book, candidates) -> None:
    good, _ = candidates
    with pytest.raises(ModellingError) as refused:
        compare_models([good], book[3000:])
    assert refused.value.code == "MODELS_NOT_COMPARABLE"


@pytest.mark.req("FR-184")
def test_models_with_different_weighting_schemes_are_refused(book, candidates) -> None:
    """FR-184 makes the weighting part of the metric. An exposure-weighted A/E and a
    claim-count-weighted one are different quantities, and aligning them in one table would
    invite exactly the comparison the requirement exists to prevent."""
    good, _ = candidates
    # A real severity model, not a contrived one: Gamma on a positive cost, claim-count
    # weighted, no exposure offset — which is what `CLAUDE.md` §7 prescribes and what makes
    # `_weighting` report `claim_count` rather than `exposure`. The `GlmSpec` type refuses a
    # Poisson model with no offset (FR-111), so this is also the only route to a
    # different weighting that the contract allows.
    # Fitted on claim-bearing rows only, which is what a severity model is fitted on. Also
    # the difference between a clean run and one where `glum` divides by a zero weight.
    with_claims = book[:3000].filter(pl.col("claim_count") > 0)
    weighted = _candidate(
        "model:sev@1", with_claims, "area",
        response_column="avg_cost",
        family="gamma",
        offset=OffsetSpec(kind="none"),
        weight=WeightSpec(kind="column", column="claim_count"),
    )
    with pytest.raises(ModellingError) as refused:
        compare_models([good, weighted], book[3000:])
    assert refused.value.code == "MODELS_NOT_COMPARABLE"
    assert "weighting" in str(refused.value)


@pytest.mark.req("FR-186")
def test_the_baseline_must_be_among_the_candidates(book, candidates) -> None:
    good, bad = candidates
    with pytest.raises(ModellingError) as refused:
        compare_models([good, bad], book[3000:], baseline="model:not-here@1")
    assert refused.value.code == "MODELS_NOT_COMPARABLE"


@pytest.mark.req("FR-186")
def test_an_empty_holdout_is_refused(candidates) -> None:
    """An empty holdout produces metrics that cannot be wrong, which is not the same as two
    models that are indistinguishable — the phrasing `_split_frames` already uses."""
    good, bad = candidates
    with pytest.raises(ModellingError) as refused:
        compare_models([good, bad], pl.DataFrame(schema={"claim_count": pl.Float64}))
    assert refused.value.code == "MODELS_NOT_COMPARABLE"
