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

    result = fit_glm(data, _spec(), factors)

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
    result = fit_glm(_frequency_data(), _spec(), [_factor("area", "area")])

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
    result = fit_glm(_frequency_data(), _spec(), [_factor("area", "area")])

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
def test_a_factor_type_that_is_not_implemented_says_so() -> None:
    """Silently treating a `banding` as its raw column would produce a fit nobody could
    tell from a correct one."""
    banded = Factor(
        id=uuid4(), slug="age_banded", dataset_id=uuid4(), version=1,
        type=FactorType.BANDING, source_columns=("driv_age",),
    )
    with pytest.raises(FactorResolutionError, match="does not resolve yet"):
        resolve_factors(_frequency_data(100), [banded])


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

    pounds = fit_glm(_gamma_severity(scale=1.0), spec, factors)
    pence = fit_glm(_gamma_severity(scale=100.0), spec, factors)

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
        )
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

    unweighted = fit_glm(data, spec, [_factor("area", "area")])
    weighted = fit_glm(data, weighted_spec, [_factor("area", "area")])

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
    )
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
    )
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
    result = fit_glm(data, _spec(), [_factor("area", "area")])
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
    result = fit_glm(data, _spec(), [_factor("telematics", "telematics")])
    term = next(c for c in result.coefficients if c.term.startswith("telematics["))
    assert term.estimate == pytest.approx(0.4, abs=0.15)
