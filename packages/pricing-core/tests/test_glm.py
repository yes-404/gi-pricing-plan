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
    Factor,
    FactorIntent,
    FactorType,
    GlmSpec,
    MonotonicDirection,
    OffsetSpec,
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


def test_a_poisson_spec_cannot_be_built_without_an_offset() -> None:
    """FR-MODEL-19, refused at the type rather than warned about downstream.

    A frequency GLM fitted without `log(exposure)` models claims per *record* instead of
    claims per year, and its coefficients look perfectly reasonable on the screen.
    """
    with pytest.raises(ValueError, match="must declare an offset"):
        _spec(offset=OffsetSpec(kind="none"))


def test_a_prohibited_factor_cannot_be_resolved() -> None:
    """FR-MODEL-5: the refusal is the whole point of the flag."""
    prohibited = _factor(
        "postcode", "area", prohibited=True,
        prohibited_reason="Proxy for a protected characteristic; board decision 2026-03.",
    )
    with pytest.raises(FactorResolutionError, match="prohibited"):
        resolve_factors(_frequency_data(100), [prohibited])


def test_a_missing_column_fails_loudly_at_resolution() -> None:
    """FR-MODEL-2: a Factor is defined against a Dataset and resolved against a version.

    This is that resolution failing — the case the requirement exists for.
    """
    with pytest.raises(FactorResolutionError, match="does not have"):
        resolve_factors(_frequency_data(100), [_factor("gone", "no_such_column")])


def test_a_factor_type_that_is_not_implemented_says_so() -> None:
    """Silently treating a `banding` as its raw column would produce a fit nobody could
    tell from a correct one."""
    banded = Factor(
        id=uuid4(), slug="age_banded", dataset_id=uuid4(), version=1,
        type=FactorType.BANDING, source_columns=("driv_age",),
    )
    with pytest.raises(FactorResolutionError, match="does not resolve yet"):
        resolve_factors(_frequency_data(100), [banded])


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


def test_control_factors_are_fitted_but_not_rateable() -> None:
    """FR-MODEL-3: year of account absorbs variance and is never rated on."""
    from pricing_core.modelling.factors import rateable

    risk = _factor("area", "area")
    control = _factor("year", "driv_age", intent=FactorIntent.CONTROL)
    assert rateable([risk, control]) == (risk,)
