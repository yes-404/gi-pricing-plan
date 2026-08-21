"""FR-MODEL-22: the Tweedie power estimated by profile likelihood over a grid, end to end.

Not a type-level test — a feature four sites agreeing on a shape can still not work
(`.claude/skills/python-test`), and the site that matters here is the actual refit against
`glum` at every grid point, and the persistence of the curve on the fit result.
"""

from __future__ import annotations

import math
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmSpec, OffsetSpec, TweediePowerSpec
from pricing_core.modelling.diagnostics import (
    backtest_model,
    compute_diagnostics,
    deviance,
    unit_deviance,
)
from pricing_core.modelling.glm import GlmFitError, fit_glm
from pricing_core.modelling.predict import predict_glm


def _factor(slug: str, column: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(column,),
    )


def _tweedie_data(n: int = 60_000, power: float = 1.5, seed: int = 20260821) -> pl.DataFrame:
    """A compound-Poisson-Gamma book with a known power (FR-MODEL-22's target).

    Drawn directly from the Tweedie distribution: N ~ Pois(mu^(2-p) / ((2-p)*phi)) and Y
    is the sum of N Gamma(shape=(2-p)/(p-1), scale=(p-1)*phi*mu^(p-1)) draws — the
    compound representation's claim shape, which is 1 only at p = 1.5 — so E[Y] = mu and
    Var(Y) = phi*mu^p, and the sum of N iid Gamma(a, s) draws is one Gamma(N*a, s) draw.
    phi = 1, exposure = 1, mu = exp(1 + 0.5*[urban]). The noise matters: a noiseless book
    has deviance exactly 0 at every p (unit_deviance(y, y, p) == 0 for all p), so the
    profile would be flat and every grid point would tie.
    """
    rng = np.random.default_rng(seed)
    urban = rng.integers(0, 2, n)
    mu = np.exp(1.0 + 0.5 * urban)
    phi = 1.0
    lam = mu ** (2.0 - power) / ((2.0 - power) * phi)
    claim_shape = (2.0 - power) / (power - 1.0)
    scale = (power - 1.0) * phi * mu ** (power - 1.0)
    counts = rng.poisson(lam)
    y = rng.gamma(shape=counts * claim_shape, scale=scale)  # shape=0 yields 0.0
    region = rng.integers(0, 2, n)
    return pl.DataFrame(
        {
            "exposure_years": np.ones(n),
            "area": ["urban" if u else "rural" for u in urban],
            "region": ["north" if r else "south" for r in region],
            "burning_cost": y,
        }
    )


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-burning-cost",
        "dataset_version_id": uuid4(),
        "response_column": "burning_cost",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "family": "tweedie",
        "link": "log",
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-22")
@pytest.mark.parametrize(
    ("power", "grid"),
    [
        (1.05, (1.55, 1.65, 1.75, 1.85, 1.95)),  # Poisson-like truth below the scan
        (1.95, (1.05, 1.15, 1.25, 1.35, 1.45)),  # Gamma-like truth above the scan
    ],
)
def test_a_profile_minimum_at_the_grid_edge_is_refused(
    power: float, grid: tuple[float, ...],
) -> None:
    """Negative, first: an estimate at the boundary of the scan is not an estimate. The
    truth is far outside the scan, the deviance gaps are huge, and the argmin lands at the
    edge — returning it would report the scan's edge as the fit's answer (FR-MODEL-22:
    a named error, not a silently degenerate result)."""
    data = _tweedie_data(power=power, n=20_000)
    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, _spec(tweedie=TweediePowerSpec(p_grid=grid)), [_factor("area", "area")])
    assert refused.value.code == "GLM_TWEEDIE_POWER_GRID_EDGE"
    assert "tweedie.p_grid" in str(refused.value)


@pytest.mark.req("FR-MODEL-22")
def test_a_fixed_power_spec_records_no_estimate() -> None:
    """Negative, the other direction: no estimation block, no estimate — the unchanged
    fixed-power path, proven not to regress."""
    data = _tweedie_data()
    fit = fit_glm(data, _spec(family_params={"power": 1.5}), [_factor("area", "area")])
    assert fit.result.tweedie is None
    assert fit.result.converged is True


@pytest.mark.req("FR-MODEL-22")
def test_the_profile_recovers_the_power_the_data_was_drawn_from() -> None:
    """The profile-likelihood estimate lands on the power the data was drawn from, and the
    curve and interval are persisted on the fit result — FR-MODEL-22's three obligations:
    the grid, the persisted curve, the estimate with its own uncertainty.

    The grid brackets the truth exactly (1.25, 1.5, 1.75), so the profile log-likelihood
    is maximised at 1.5; the chi2_0.95(1)/2 = 1.92 likelihood-ratio cutoff then brackets
    1.5 from below and above. The density carries the p-dependent normaliser, so the
    profile is informative here where the deviance profile was not (02 §3.4 amendment
    2026-08-21). If the argmax ever lands at a grid edge for this seed, raise n or widen
    the grid rather than weakening the assertion."""
    data = _tweedie_data(power=1.5)
    fit = fit_glm(
        data,
        _spec(tweedie=TweediePowerSpec(p_grid=(1.25, 1.5, 1.75))),
        [_factor("area", "area")],
    )
    tweedie = fit.result.tweedie
    assert tweedie is not None
    assert tweedie.estimated_power == pytest.approx(1.5)
    assert tweedie.ci_lower <= 1.5 <= tweedie.ci_upper
    assert 1.0 < tweedie.ci_lower < tweedie.ci_upper < 2.0
    assert [p.power for p in tweedie.curve] == [1.25, 1.5, 1.75]
    assert all(math.isfinite(p.log_likelihood) for p in tweedie.curve)
    best = max(tweedie.curve, key=lambda p: p.log_likelihood)
    assert best.power == tweedie.estimated_power
    assert fit.result.converged is True


@pytest.mark.req("FR-MODEL-22")
def test_diagnostics_are_computed_under_the_estimated_power() -> None:
    """FR-MODEL-22's 'not silently baked in as a constant': the diagnostics' deviance is
    the deviance under the fitted estimate, not under the spec's 1.5 default — and the
    type-III sweep refits with p held at the estimate."""
    data = _tweedie_data(power=1.7)
    factors = [_factor("area", "area"), _factor("region", "region")]
    spec = _spec(tweedie=TweediePowerSpec(p_grid=(1.5, 1.7, 1.9)))
    fit = fit_glm(data, spec, factors)
    assert fit.result.tweedie is not None
    computed = compute_diagnostics(fit.result, spec, factors, train=data, holdout=data)
    assert computed.glm is not None
    y = data["burning_cost"].cast(pl.Float64).to_numpy()
    mu = predict_glm(fit.result, data, factors, spec)
    expected = deviance(y, mu, family="tweedie", power=fit.result.tweedie.estimated_power)
    assert computed.glm.deviance == pytest.approx(expected)
    assert computed.glm.deviance != pytest.approx(deviance(y, mu, family="tweedie", power=1.5))
    assert computed.glm.type_iii_tests


@pytest.mark.req("FR-MODEL-22")
def test_a_backtest_of_an_estimated_power_model_uses_the_estimate() -> None:
    """The backtest's residuals are the deviance residuals under the fitted estimate —
    the value the fit used, read from the fit result rather than the spec's constant."""
    data = _tweedie_data(power=1.7)
    factors = [_factor("area", "area")]
    spec = _spec(tweedie=TweediePowerSpec(p_grid=(1.5, 1.7, 1.9)))
    fit = fit_glm(data, spec, factors)
    assert fit.result.tweedie is not None
    summary = backtest_model(
        fit.result, spec, factors, data,
        model_ref="model:burning@1",
        dataset_version_ref="dataset_version:book@2",
        fitted_on_ref="dataset_version:book@1",
    )
    residuals = summary.partition.residual_summary
    assert residuals is not None
    y = data["burning_cost"].cast(pl.Float64).to_numpy()
    mu = predict_glm(fit.result, data, factors, spec)
    unit = np.sign(y - mu) * np.sqrt(
        np.maximum(
            unit_deviance(y, mu, family="tweedie", power=fit.result.tweedie.estimated_power),
            0.0,
        )
    )
    assert residuals.mean == pytest.approx(float(np.mean(unit)))
