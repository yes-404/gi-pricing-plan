"""GLM fitting against data whose answer is known (`02` FR-MODEL-18..23).

The test that matters is not "does it return numbers" but **does it return the numbers
that generated the data**. Everything else here is a refusal: `02` FR-MODEL-23 says a
degenerate fit is a named error, never a silently returned result, and R5 says an estimate
without uncertainty is not an estimate.
"""

from __future__ import annotations

import math
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Coefficient,
    Factor,
    FactorIntent,
    FactorType,
    GlmSpec,
    MonotonicDirection,
    OffsetSpec,
    WeightSpec,
)
from pricing_core.modelling import GlmFitError, fit_glm
from pricing_core.modelling.factors import FactorResolutionError, resolve_factors


def _factor(slug: str, column: str, **over: object) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(column,), **over,
    )


def _frequency_data(n: int = 20_000, seed: int = 20260815) -> pl.DataFrame:
    """A Poisson book with coefficients we choose, so the fit has a right answer.

    log(mu) = log(exposure) - 2.0 + 0.5·[urban] + 0.03·(age - 40)
    """
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.25, 1.0, n)
    urban = rng.integers(0, 2, n)
    age = rng.integers(18, 80, n)
    eta = np.log(exposure) - 2.0 + 0.5 * urban + 0.03 * (age - 40)
    counts = rng.poisson(np.exp(eta))
    return pl.DataFrame(
        {
            "exposure_years": exposure,
            "area": ["urban" if u else "rural" for u in urban],
            "driv_age": age.astype(float),
            "claim_count": counts.astype(float),
        }
    )


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "family": "poisson",
        "link": "log",
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-18")
def test_the_fit_recovers_the_coefficients_that_generated_the_data() -> None:
    """FR-MODEL-18/19: Poisson, log link, `offset = log(exposure)`.

    Tolerances are loose enough for sampling noise at 20 000 rows and tight enough that a
    wrong offset, a dropped base level or a link mix-up moves the answer well outside them.
    """
    data = _frequency_data()
    factors = [_factor("area", "area"), _factor("driv_age", "driv_age")]

    result = fit_glm(data, _spec(), factors).result

    by_term = {c.term: c for c in result.coefficients}
    # Intercept absorbs the centring: the generator used 0.03 x (age - 40).
    assert by_term["intercept"].estimate == pytest.approx(-2.0 - 0.03 * 40, abs=0.06)
    assert by_term["area[urban]"].estimate == pytest.approx(0.5, abs=0.05)
    assert by_term["driv_age"].estimate == pytest.approx(0.03, abs=0.004)
    assert result.rows == data.height
    assert result.library_versions["glum"]


@pytest.mark.req("FR-MODEL-21")
def test_every_coefficient_carries_its_uncertainty() -> None:
    """`02` R5. A point estimate alone is half a result, and the half that reads as
    more certain than it is."""
    result = fit_glm(_frequency_data(), _spec(), [_factor("area", "area")]).result

    for coefficient in result.coefficients:
        assert coefficient.std_error > 0.0
        low, high = coefficient.ci_95
        assert low < coefficient.estimate < high
        # The interval is the estimate ± 1.96 SE, so it must bracket by that much.
        assert high - low == pytest.approx(2 * 1.959963984540054 * coefficient.std_error, rel=1e-9)
        assert 0.0 <= coefficient.p_value <= 1.0

    urban = next(c for c in result.coefficients if c.term == "area[urban]")
    assert urban.relativity == pytest.approx(math.exp(urban.estimate))
    # A real effect at this sample size must be significant, or the standard errors are
    # not measuring what they claim to.
    assert urban.p_value < 1e-6


@pytest.mark.req("FR-MODEL-21")
def test_the_relativity_table_marks_its_base_level() -> None:
    """FR-MODEL-21: the base level is *marked*, at relativity 1.0.

    Omitting it is how a reader ends up believing a factor has one fewer level than it has.
    """
    result = fit_glm(_frequency_data(), _spec(), [_factor("area", "area")]).result

    table = result.relativities["area"]
    assert [level.level for level in table] == ["rural", "urban"]
    base = next(level for level in table if level.is_base)
    assert base.level == "rural"
    assert base.relativity == 1.0
    assert sum(level.is_base for level in table) == 1
    # Exposure comes with it, because "which level is base" is an exposure question.
    assert base.exposure is not None
    assert base.exposure > 0


@pytest.mark.req("FR-MODEL-23")
def test_a_collinear_design_is_named_rather_than_returned() -> None:
    """FR-MODEL-23: rank deficiency is an error with the offending terms, not a fit.

    Two columns carrying the same information leave their coefficients unidentified. A GLM
    library will happily return *something*; what it returns is not an estimate.
    """
    data = _frequency_data(4_000).with_columns(pl.col("driv_age").alias("driv_age_copy"))
    factors = [_factor("driv_age", "driv_age"), _factor("age_again", "driv_age_copy")]

    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, _spec(), factors)
    assert refused.value.code == "GLM_RANK_DEFICIENT"
    assert "collinear" in str(refused.value)


@pytest.mark.req("FR-MODEL-19")
def test_zero_exposure_is_refused_rather_than_logged() -> None:
    """`log(0)` is `-inf`, and a row with no exposure carries no information.

    Filtering it silently would change the fitted population without saying so; passing it
    through produces a fit full of `nan` that some libraries still report as converged.
    """
    data = _frequency_data(2_000).with_columns(
        pl.when(pl.int_range(pl.len()) == 0)
        .then(0.0)
        .otherwise(pl.col("exposure_years"))
        .alias("exposure_years")
    )
    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, _spec(), [_factor("area", "area")])
    assert refused.value.code == "OFFSET_REQUIRED_FOR_FREQUENCY"


@pytest.mark.req("FR-MODEL-19")
def test_a_poisson_spec_cannot_be_built_without_an_offset() -> None:
    """FR-MODEL-19, refused at the type rather than warned about downstream.

    A frequency GLM fitted without `log(exposure)` models claims per *record* instead of
    claims per year, and its coefficients look perfectly reasonable on the screen.
    """
    with pytest.raises(ValueError, match="must declare an offset"):
        _spec(offset=OffsetSpec(kind="none"))


@pytest.mark.req("FR-MODEL-5")
def test_a_prohibited_factor_cannot_be_resolved() -> None:
    """FR-MODEL-5: the refusal is the whole point of the flag."""
    prohibited = _factor(
        "postcode", "area", prohibited=True,
        prohibited_reason="Proxy for a protected characteristic; board decision 2026-03.",
    )
    with pytest.raises(FactorResolutionError, match="prohibited"):
        resolve_factors(_frequency_data(100), [prohibited])


@pytest.mark.req("FR-MODEL-2")
def test_a_missing_column_fails_loudly_at_resolution() -> None:
    """FR-MODEL-2: a Factor is defined against a Dataset and resolved against a version.

    This is that resolution failing — the case the requirement exists for.
    """
    with pytest.raises(FactorResolutionError, match="does not have"):
        resolve_factors(_frequency_data(100), [_factor("gone", "no_such_column")])


@pytest.mark.req("FR-MODEL-1")
@pytest.mark.req("FR-MODEL-88")
def test_a_factor_type_that_is_not_implemented_says_so() -> None:
    """Silently treating a `spline` as its raw column would produce a fit nobody could
    tell from a correct one.

    The example used to be `banding`, which now resolves. Changed rather than deleted: the
    claim being tested is about the *unimplemented* arms of FR-MODEL-1's closed set, and
    **three** of the eight are still unimplemented — `spline`, `polynomial` and
    `expression`. (Was "five of the eight"; `interaction` began resolving with FR-MODEL-91
    on 2026-08-18, and `offset` stopped being unimplemented and became *superseded* with
    FR-MODEL-114 on 2026-08-22. The distinction is the point of the next test.)
    """
    splined = Factor(
        id=uuid4(), slug="age_spline", dataset_id=uuid4(), version=1,
        type=FactorType.SPLINE, source_columns=("driv_age",),
    )
    with pytest.raises(FactorResolutionError, match="does not resolve yet"):
        resolve_factors(_frequency_data(100), [splined])


@pytest.mark.req("FR-MODEL-114")
@pytest.mark.req("FR-MODEL-88")
def test_an_offset_factor_is_refused_as_superseded_and_never_as_pending() -> None:
    """A superseded arm never resolves, so its refusal must not promise that it will.

    The generic refusal says the build "does not resolve yet", which is the right message
    for `spline` and the wrong one for `offset`: OQ-MODEL-23 superseded the type on
    2026-08-22 because an offset is declared on the fit spec through `OffsetSpec`, and a
    Factor type meaning the same thing was a second mechanism for a solved problem. A
    caller told "yet" would reasonably wait for a release that is never coming.
    """
    factor = Factor(
        id=uuid4(), slug="exposure_offset", dataset_id=uuid4(), version=1,
        type=FactorType.OFFSET, source_columns=("driv_age",),
    )
    with pytest.raises(FactorResolutionError, match="superseded") as raised:
        resolve_factors(_frequency_data(100), [factor])
    assert "does not resolve yet" not in str(raised.value), (
        "a superseded arm was refused with the pending-slice message, which promises a "
        "release that FR-MODEL-114 says will never come"
    )


@pytest.mark.req("FR-MODEL-114")
@pytest.mark.req("FR-MODEL-1")
def test_the_superseded_offset_arm_stays_in_the_closed_set() -> None:
    """FR-MODEL-114 supersedes `offset` by refusing it permanently, **not** by removing it.

    Artifacts are immutable, so a Factor persisted with `type: "offset"` can never be
    rewritten; dropping the arm would turn `Factor.model_validate` on read into a
    `ValidationError` that fails a whole workspace's factor list rather than the one row.
    The enum is also the source the published OpenAPI is generated from (ADR-0002), and
    external consumers have read it since Phase 0 — FR-MODEL-87's 2026-08-22 ruling.

    This test exists because "superseded" reads like an invitation to delete the member,
    and the deletion would pass every other test in the suite.
    """
    assert FactorType.OFFSET in set(FactorType), (
        "FR-MODEL-114 supersedes the `offset` Factor type by making its refusal permanent, "
        "not by removing the arm - removing it breaks reads of already-persisted factors"
    )
    assert len(set(FactorType)) == 8, (
        "FR-MODEL-1 declares a closed set of eight; superseding an arm does not shrink it"
    )


@pytest.mark.req("FR-MODEL-88")
def test_an_expression_factor_can_be_declared_and_can_never_be_resolved() -> None:
    """FR-MODEL-88 states this verdict rather than leaving it to be discovered.

    `FactorType.EXPRESSION` is a live member of FR-MODEL-1's closed set and `Factor` carries
    no field to hold the expression, so the type is selectable and the payload cannot be
    supplied. OQ-MODEL-8 (decided 2026-08-17) called that contained rather than corrected:
    the refusal is at resolution, which is the boundary where an unresolved factor would
    otherwise become a fit nobody could tell from a correct one. The field and its validator
    arm are Phase 1b's, with the rest of the expression work.
    """
    factor = Factor(
        id=uuid4(), slug="age_over_ncd", dataset_id=uuid4(), version=1,
        type=FactorType.EXPRESSION, source_columns=("driv_age",),
    )
    assert not hasattr(factor, "expression"), (
        "an `expression` field would make this factor resolvable and FR-MODEL-88 wrong"
    )
    with pytest.raises(FactorResolutionError, match="'expression'"):
        resolve_factors(_frequency_data(100), [factor])


@pytest.mark.req("FR-MODEL-4")
def test_a_monotonic_direction_requires_a_rationale() -> None:
    """FR-MODEL-4: the direction is an actuarial judgement, and the next person needs to
    know whose and why."""
    with pytest.raises(ValueError, match="rationale"):
        _factor("age", "driv_age", monotonic_direction=MonotonicDirection.DECREASING)

    # ...and with one, it is accepted.
    assert _factor(
        "age", "driv_age",
        monotonic_direction=MonotonicDirection.DECREASING,
        monotonic_rationale="Frequency falls with age above 25; prevents noise-driven "
        "reversals in thin bands.",
    ).monotonic_direction is MonotonicDirection.DECREASING


@pytest.mark.req("FR-MODEL-3")
def test_control_factors_are_fitted_but_not_rateable() -> None:
    """FR-MODEL-3: year of account absorbs variance and is never rated on."""
    from pricing_core.modelling.factors import rateable

    risk = _factor("area", "area")
    control = _factor("year", "driv_age", intent=FactorIntent.CONTROL)
    assert rateable([risk, control]) == (risk,)


# -- What the first version of this file could not catch ---------------------------------
#
# Three independent audits found the same hole: every assertion here was either about a
# coefficient (which was right) or about a standard error being positive and its interval
# symmetric (which is true by construction). An SE wrong by 48x passed. These compare
# numbers to something computed independently.


def _gamma_severity(n: int = 4_000, scale: float = 1.0, seed: int = 20260815) -> pl.DataFrame:
    """A severity book with a known effect, at a chosen monetary scale.

    `scale` exists because the defect it catches was scale-dependent: the true standard
    error of a log-link Gamma coefficient does not change when every amount is multiplied
    by a hundred, and the old computation's did.
    """
    rng = np.random.default_rng(seed)
    urban = rng.integers(0, 2, n)
    mean = np.exp(1.0 + 0.5 * urban) * scale
    return pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(n)],
            "area": ["urban" if u else "rural" for u in urban],
            "claim_count": np.ones(n),
            "severity": rng.gamma(shape=2.0, scale=mean / 2.0),
            "exposure_years": np.ones(n),
        }
    )


@pytest.mark.req("FR-MODEL-21")
def test_the_standard_error_of_a_severity_model_does_not_depend_on_the_currency_unit() -> None:
    """`02` R5, and the defect that made it a lie for every family except Poisson.

    The old working weight was `W = mu` for a log link — the Fisher information for Poisson
    and for nothing else. It ignored the variance function and the dispersion, so on a
    Gamma severity model over **minor units** the reported interval was ~48x too narrow: a
    nominal 95 % interval with 7 % coverage.

    Scale invariance is the sharpest test of it. Multiplying every amount by 100 cannot
    change what is known about a multiplicative effect, and under the old computation it
    changed the standard error by a factor of 100.
    """
    factors = [_factor("area", "area")]
    spec = _spec(
        family="gamma", response_column="severity",
        offset=OffsetSpec(kind="none"), weight=WeightSpec(kind="column", column="claim_count"),
    )

    pounds = fit_glm(_gamma_severity(scale=1.0), spec, factors).result
    pence = fit_glm(_gamma_severity(scale=100.0), spec, factors).result

    def area_term(result: object) -> Coefficient:
        """Whichever level is *not* the base — the base is chosen by exposure now, so its
        name is not knowable when the test is written."""
        return next(c for c in result.coefficients if c.term.startswith("area["))  # type: ignore[attr-defined]

    # The effect is ±0.5 depending on which level became the base; its size is the point.
    assert abs(area_term(pounds).estimate) == pytest.approx(0.5, abs=0.08)
    assert abs(area_term(pence).estimate) == pytest.approx(0.5, abs=0.08)
    assert area_term(pounds).std_error == pytest.approx(area_term(pence).std_error, rel=1e-6)
    # ...and it is the *right* size: ~0.032 at n=4000 with shape 2. A hundredfold error
    # would be unmissable against this bound.
    assert 0.01 < area_term(pounds).std_error < 0.10


@pytest.mark.req("FR-MODEL-21")
def test_the_reported_interval_actually_covers_the_truth() -> None:
    """Coverage, measured rather than assumed.

    The old computation produced 7 % coverage on this shape while reporting 95 %. Forty
    replications is a coarse instrument — it would miss a 10 % error and cannot miss a
    tenfold one, which is the size of the defect it exists to catch.
    """
    truth, covered = 0.5, 0
    replications = 40
    for seed in range(replications):
        result = fit_glm(
            _gamma_severity(n=1_500, seed=seed),
            _spec(family="gamma", response_column="severity", offset=OffsetSpec(kind="none")),
            [_factor("area", "area")],
        ).result
        term = next(c for c in result.coefficients if c.term.startswith("area["))
        low, high = term.ci_95
        # ±0.5 depending on which level is the base; the interval must cover its own truth.
        signed = truth if term.estimate > 0 else -truth
        covered += low <= signed <= high

    assert covered >= replications * 0.8, (
        f"{covered}/{replications} nominal-95 % intervals covered the truth. Below 80 % the "
        "intervals are not what they claim to be."
    )


@pytest.mark.req("FR-MODEL-19")
def test_a_weight_column_changes_the_answer() -> None:
    """FR-MODEL-19: severity is weighted by claim count, burning cost by exposure.

    Nothing exercised the weight path at all — replacing `weights` with `None` left every
    test green. Here the weights are deliberately informative, so ignoring them moves the
    estimate well outside tolerance.
    """
    data = _gamma_severity(2_000).with_columns(
        pl.when(pl.col("area") == "urban").then(20.0).otherwise(1.0).alias("claim_count")
    )
    spec = _spec(family="gamma", response_column="severity", offset=OffsetSpec(kind="none"))
    weighted_spec = _spec(
        family="gamma", response_column="severity", offset=OffsetSpec(kind="none"),
        weight=WeightSpec(kind="column", column="claim_count"),
    )

    unweighted = fit_glm(data, spec, [_factor("area", "area")]).result
    weighted = fit_glm(data, weighted_spec, [_factor("area", "area")]).result

    def se(result: object) -> float:
        return next(c for c in result.coefficients if c.term.startswith("area[")).std_error  # type: ignore[attr-defined]

    # Twenty times the weight on the urban rows buys a materially tighter estimate of the
    # urban effect. Equal standard errors would mean the weights were discarded.
    assert se(weighted) < se(unweighted) * 0.75


@pytest.mark.req("FR-MODEL-18")
def test_a_burning_cost_model_fits_at_all() -> None:
    """FR-MODEL-19's third default, which had never run.

    The family string was built as `tweedie(p=1.5)`; glum parses the power by calling
    `float("p=1.5")`, so every burning cost fit raised a bare `ValueError` from inside the
    library — not even a named `GlmFitError`. No test constructed a non-Poisson family.
    """
    # Both levels carry cost; only the *amount* differs. A level at exactly zero is
    # perfect separation, which the new detector correctly refused when this fixture first
    # had it.
    data = _gamma_severity(2_000).with_columns(
        (
            pl.col("severity")
            * pl.when(pl.col("area") == "urban").then(1.0).otherwise(0.4)
        ).alias("burning_cost")
    )
    result = fit_glm(
        data,
        _spec(
            family="tweedie", family_params={"power": 1.5},
            response_column="burning_cost",
            offset=OffsetSpec(kind="log_column", column="exposure_years"),
        ),
        [_factor("area", "area")],
    ).result
    assert result.dispersion is not None
    assert all(c.std_error > 0 for c in result.coefficients)


@pytest.mark.req("FR-MODEL-18")
def test_a_tweedie_power_outside_its_range_is_refused_by_the_spec() -> None:
    """At 1 it is Poisson and at 2 it is Gamma; between them it is what burning cost needs.

    Refused when the spec is built, not when the fit runs: it is a fact about the
    specification, and a spec that cannot be fitted should not be storable.
    """
    with pytest.raises(ValueError, match="outside"):
        _spec(family="tweedie", family_params={"power": 2.5}, response_column="severity",
              offset=OffsetSpec(kind="none"))


@pytest.mark.req("FR-MODEL-23")
def test_separation_is_refused_rather_than_returned_as_an_enormous_coefficient() -> None:
    """FR-MODEL-23 names separation, and nothing detected it.

    A perfectly separated logit returned `converged=True` with a coefficient of 640 and
    p=0 — the "silently returned degenerate fit" the requirement exists to forbid.
    """
    n = 400
    rng = np.random.default_rng(3)
    x = rng.normal(size=n)
    data = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(n)],
            "x": x,
            "converted": (x > 0).astype(float),
            "exposure_years": np.ones(n),
        }
    )
    with pytest.raises(GlmFitError) as refused:
        fit_glm(
            data,
            _spec(family="binomial", link="logit", response_column="converted",
                  offset=OffsetSpec(kind="none"), max_iter=10_000),
            [_factor("x", "x")],
        )
    assert refused.value.code == "GLM_SEPARATION_DETECTED"
    assert "x" in refused.value.terms


@pytest.mark.req("FR-MODEL-21")
def test_a_non_multiplicative_link_reports_no_relativity_rather_than_one() -> None:
    """A relativity is `exp(β)` — a reading of a multiplicative model.

    Under `logit` the table used to report 1.0 for every level, so a factor spanning
    eighteen log-odds was presented as having no effect anywhere. Absent is the true
    statement; 1.0 is a false one.
    """
    n = 2_000
    rng = np.random.default_rng(11)
    urban = rng.integers(0, 2, n)
    data = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(n)],
            "area": ["urban" if u else "rural" for u in urban],
            "converted": rng.binomial(1, 1 / (1 + np.exp(-(-0.5 + 1.2 * urban)))).astype(float),
            "exposure_years": np.ones(n),
        }
    )
    result = fit_glm(
        data,
        _spec(family="binomial", link="logit", response_column="converted",
              offset=OffsetSpec(kind="none")),
        [_factor("area", "area")],
    ).result
    table = result.relativities["area"]
    assert all(level.relativity is None for level in table)
    # ...and the effect is still readable, on the scale it exists on.
    urban_level = next(level for level in table if level.level == "urban")
    assert urban_level.estimate == pytest.approx(1.2, abs=0.2)


@pytest.mark.req("FR-MODEL-21")
def test_the_base_level_is_the_one_carrying_the_most_exposure() -> None:
    """`02` §4.1 declares `base_level_method: largest_exposure`; the code chose
    alphabetically.

    It is not tidiness: every other level's relativity is expressed against the base, so a
    base holding 5 % of the exposure gives every relativity the standard error of a thin
    cell.
    """
    n = 3_000
    rng = np.random.default_rng(5)
    # 'a' is alphabetically first and holds almost nothing; 'c' holds the book.
    area = rng.choice(["a", "b", "c"], size=n, p=[0.05, 0.15, 0.80])
    data = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(n)],
            "area": area,
            "exposure_years": np.ones(n),
            "claim_count": rng.poisson(0.1, n).astype(float),
        }
    )
    result = fit_glm(data, _spec(), [_factor("area", "area")]).result
    base = next(level for level in result.relativities["area"] if level.is_base)
    assert base.level == "c"


@pytest.mark.req("FR-MODEL-1")
def test_a_boolean_factor_fits_rather_than_being_called_collinear() -> None:
    """`str(True)` is `"True"`; polars renders the same value as `"true"`.

    The dummy was therefore all-zero, and the failure surfaced as `GLM_RANK_DEFICIENT`
    "two or more terms are collinear" for a single term with nothing to be collinear with —
    the wrong cause, which is what FR-MODEL-23's "offending factors identified" is for.
    """
    n = 2_000
    rng = np.random.default_rng(13)
    telematics = rng.integers(0, 2, n).astype(bool)
    data = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(n)],
            "telematics": telematics,
            "exposure_years": np.ones(n),
            "claim_count": rng.poisson(np.exp(-2.0 + 0.4 * telematics)).astype(float),
        }
    )
    result = fit_glm(data, _spec(), [_factor("telematics", "telematics")]).result
    term = next(c for c in result.coefficients if c.term.startswith("telematics["))
    assert term.estimate == pytest.approx(0.4, abs=0.15)


@pytest.mark.req("FR-MODEL-18")
def test_the_inverse_link_fits_rather_than_dying_inside_the_library() -> None:
    """FR-MODEL-18 declares `inverse` supported, and it is the canonical Gamma link.

    It reached `glum` as the string `"inverse"`, which is not in that library's link
    vocabulary, and every such fit died on a bare `ValueError` raised from inside
    `_glm.py` — not a `GlmFitError`, and not anything a caller could act on. The link
    itself was never missing: `TweedieLink(p)` is `mu**(1-p)`, so `TweedieLink(2)` is
    `1/mu`. `predict._inverse_link` had implemented it all along, so the platform could
    score a model on a link it could not fit.

    The assertion is on the recovered coefficient, not merely on the absence of an
    exception: a link mapped to the *wrong* Tweedie power would also fit, and would
    return a number for every row.
    """
    rng = np.random.default_rng(20260818)
    n = 8_000
    age = rng.integers(18, 80, n).astype(float)
    # 1/mu = 0.5 + 0.004·(age - 40), so the fit has a right answer on the link scale.
    eta = 0.5 + 0.004 * (age - 40)
    data = pl.DataFrame(
        {"driv_age": age, "cost": rng.gamma(50.0, 1.0 / (50.0 * eta), n)}
    )
    spec = GlmSpec(
        model_family_slug="motor-severity",
        dataset_version_id=uuid4(),
        response_column="cost",
        offset=OffsetSpec(kind="none"),
        family="gamma",
        link="inverse",
    )

    result = fit_glm(data, spec, [_factor("driv_age", "driv_age")]).result

    assert result.converged
    slope = next(c for c in result.coefficients if c.term.startswith("driv_age"))
    assert slope.estimate == pytest.approx(0.004, abs=5e-4)
    intercept = result.intercept
    assert intercept is not None
    assert intercept.estimate == pytest.approx(0.5 - 0.004 * 40, abs=5e-3)
    # FR-MODEL-21: no relativity under a non-multiplicative link — `exp(β)` means nothing
    # when the effect is additive on `1/mu`.
    assert slope.relativity is None


@pytest.mark.req("FR-MODEL-23")
def test_a_response_outside_the_family_domain_is_named_rather_than_a_stack_trace() -> None:
    """FR-MODEL-23's remainder: a `glum` refusal that is not rank deficiency.

    The fit site caught only `np.linalg.LinAlgError`, so the *only* library failure it
    named was a singular design. A Gamma severity response containing a nil settlement —
    an ordinary claims table, not a pathological one — reached the caller as a bare
    `ValueError: Some value(s) of y are out of the valid range for
    familyGammaDistribution.` raised from `glum/_glm.py:428`, and the job stored a stack
    trace where FR-MODEL-23 promises a named error with something to act on.

    Not `GLM_RANK_DEFICIENT`: that code's message names collinear terms, and nothing here
    is collinear with anything. A wrong diagnosis sends the reader off to drop a factor
    that was never the problem.
    """
    rng = np.random.default_rng(20260822)
    n = 2_000
    age = rng.integers(18, 80, n).astype(float)
    cost = rng.gamma(4.0, 250.0, n)
    cost[7] = 0.0  # the nil settlement — Gamma's support is strictly positive
    data = pl.DataFrame({"driv_age": age, "cost": cost})
    spec = GlmSpec(
        model_family_slug="motor-severity",
        dataset_version_id=uuid4(),
        response_column="cost",
        offset=OffsetSpec(kind="none"),
        family="gamma",
        link="log",
    )

    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, spec, [_factor("driv_age", "driv_age")])

    assert refused.value.code == "GLM_FIT_FAILED"
    # The library's own words, carried across. The code says a fit was refused; only
    # `glum` knows *which* of its input checks refused it, and paraphrasing that is how a
    # message ends up naming the wrong cause.
    assert "out of the valid range" in str(refused.value)
    assert "familyGammaDistribution" in str(refused.value)
    # Actionable, not merely named (FR-MODEL-23): the reader is told which inputs to look
    # at, and that nothing was estimated.
    assert "Nothing was estimated" in str(refused.value)
    assert refused.value.terms  # the design's terms, as every other GLM refusal carries
    assert isinstance(refused.value.__cause__, ValueError)


@pytest.mark.req("FR-MODEL-23")
def test_a_malformed_weight_column_is_named_rather_than_a_stack_trace() -> None:
    """The same clause, reached by a different `glum` check.

    `glum` refuses a negative `sample_weight` in `_validation.py` before it solves
    anything, so this never touches the linear algebra and could not have been a
    `LinAlgError` on any input. A severity model weighted by claim count is the ordinary
    way a weight column reaches a fit (FR-MODEL-19), which is what makes a bad one worth a
    named refusal rather than a traceback.
    """
    data = _frequency_data(2_000).with_columns(
        pl.when(pl.int_range(pl.len()) == 3)
        .then(-1.0)
        .otherwise(1.0)
        .alias("claim_weight")
    )
    spec = _spec(weight=WeightSpec(kind="column", column="claim_weight"))

    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, spec, [_factor("area", "area")])

    assert refused.value.code == "GLM_FIT_FAILED"
    assert "Sample weights must be non-negative" in str(refused.value)


@pytest.mark.req("FR-MODEL-23")
def test_a_singular_design_still_reaches_the_rank_deficient_code() -> None:
    """The clause order is load-bearing, and the language hides why.

    `np.linalg.LinAlgError` **subclasses `ValueError`** (numpy 2.5.2). The `except
    ValueError` backstop added for the failures above therefore swallows every singular
    design the moment it is written *above* the `LinAlgError` clause — first match wins —
    and `GLM_RANK_DEFICIENT` would never be raised again: silently, with the collinear fit
    still refused and only the diagnosis wrong.

    `test_a_collinear_design_is_named_rather_than_returned` further up would catch the
    regression; this one asserts the *reason*, so the next reader tidying the two clauses
    together meets it before running anything.
    """
    assert issubclass(np.linalg.LinAlgError, ValueError)

    data = _frequency_data(4_000).with_columns(pl.col("driv_age").alias("driv_age_copy"))
    factors = [_factor("driv_age", "driv_age"), _factor("age_again", "driv_age_copy")]

    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, _spec(), factors)
    assert refused.value.code == "GLM_RANK_DEFICIENT"


@pytest.mark.req("NFR-MODEL-6")
def test_two_fits_of_one_spec_reproduce_identical_coefficients() -> None:
    """NFR-MODEL-6's GLM half, which carried no marker until 2026-08-22.

    The requirement asks for two things and the suite proved one: `test_gbm.py` pins the
    booster hash, and nothing anywhere refitted a GLM and compared coefficients. The
    tolerance is the requirement's own 1e-10, not `pytest.approx`'s default — a solver
    that had gone non-deterministic would still pass a relative 1e-6.
    """
    data = _frequency_data()
    factors = [_factor("area", "area"), _factor("driv_age", "driv_age")]
    spec = _spec()

    first = fit_glm(data, spec, factors)
    second = fit_glm(data, spec, factors)

    assert [c.term for c in first.result.coefficients] == [
        c.term for c in second.result.coefficients
    ]
    for left, right in zip(
        first.result.coefficients, second.result.coefficients, strict=True
    ):
        assert abs(left.estimate - right.estimate) <= 1e-10, left.term


@pytest.mark.req("FR-MODEL-123")
def test_fit_glm_refuses_a_seed_argument() -> None:
    """FR-MODEL-123: `spec.seed` is the only seed, and the dead kwarg is gone.

    A deleted parameter and a silently-ignored one are indistinguishable to a caller until
    one of them raises — which is how `fit_glm(..., seed=…)` reached twenty call sites, four
    of them outside tests, without anyone noticing it did nothing. Asserting the raise is
    what stops the removal regressing into a re-added kwarg that is ignored again.

    No data is needed: Python binds arguments before the body runs, so the unexpected
    keyword is refused before the frame is ever touched.
    """
    with pytest.raises(TypeError, match="seed"):
        fit_glm(pl.DataFrame(), _spec(), [], seed=0)  # type: ignore[call-arg]
