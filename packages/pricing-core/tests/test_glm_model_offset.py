"""FR-MODEL-24: `kind="model"` offsets — supplied, validated, honoured. The array is the
referenced model's linear predictor; pricing-core cannot resolve the ref itself and must
refuse to fit without the array rather than fit with no offset."""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmSpec, OffsetSpec
from pricing_core.modelling import GlmFitError, PredictionError
from pricing_core.modelling.diagnostics import backtest_model, compute_diagnostics
from pricing_core.modelling.glm import fit_glm
from pricing_core.modelling.predict import linear_predictor, predict_glm


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


def _residual_data(n: int = 20_000, seed: int = 20260821) -> tuple[pl.DataFrame, np.ndarray]:
    """y ~ Poisson(exp(eta_base + 0.2·z)); `eta_base` is the referenced model's truth.

    log(mu) = log(exposure) - 2.0 + 0.5·[urban] + 0.2·[resid_flag]
    """
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.25, 1.0, n)
    urban = rng.integers(0, 2, n)
    z = rng.integers(0, 2, n)
    eta_base = np.log(exposure) - 2.0 + 0.5 * urban
    eta = eta_base + 0.2 * z
    return (
        pl.DataFrame(
            {
                "exposure_years": exposure,
                "area": ["urban" if u else "rural" for u in urban],
                "resid_flag": z.astype(float),
                "claim_count": rng.poisson(np.exp(eta)).astype(float),
            }
        ),
        eta_base,
    )


def _model_offset_spec() -> GlmSpec:
    return _spec(offset=OffsetSpec(kind="model", offset_model_ref="model:base@1"))


@pytest.mark.req("FR-MODEL-24")
def test_a_model_offset_without_the_array_is_refused() -> None:
    data, _ = _residual_data()
    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")])
    assert refused.value.code == "MODEL_OFFSET_MISSING"


@pytest.mark.req("FR-MODEL-24")
def test_a_model_offset_of_the_wrong_length_is_refused() -> None:
    data, eta_base = _residual_data()
    with pytest.raises(GlmFitError, match="rows"):
        fit_glm(
            data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")],
            model_offset=eta_base[:-1],
        )


@pytest.mark.req("FR-MODEL-24")
def test_a_model_offset_with_non_finite_values_is_refused() -> None:
    data, eta_base = _residual_data()
    eta_base[0] = np.inf
    with pytest.raises(GlmFitError, match="finite"):
        fit_glm(
            data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")],
            model_offset=eta_base,
        )


@pytest.mark.req("FR-MODEL-24")
def test_the_residual_fit_recovers_the_signal_on_top_of_the_offset() -> None:
    data, eta_base = _residual_data()
    result = fit_glm(
        data, _model_offset_spec(), [_factor("resid_flag", "resid_flag")],
        model_offset=eta_base,
    ).result
    by_term = {c.term: c for c in result.coefficients}
    assert by_term["intercept"].estimate == pytest.approx(0.0, abs=0.06)
    assert by_term["resid_flag"].estimate == pytest.approx(0.2, abs=0.05)


@pytest.mark.req("FR-MODEL-24")
def test_prediction_without_the_array_is_refused_and_with_it_reproduces_the_fit() -> None:
    data, eta_base = _residual_data()
    spec = _model_offset_spec()
    factors = [_factor("resid_flag", "resid_flag")]
    fit = fit_glm(data, spec, factors, model_offset=eta_base).result

    with pytest.raises(PredictionError) as refused:
        predict_glm(fit, data, factors, spec)
    assert refused.value.code == "MODEL_OFFSET_MISSING"

    by_term = {c.term: c for c in fit.coefficients}
    manual_mu = np.exp(eta_base + by_term["intercept"].estimate
                       + by_term["resid_flag"].estimate * data["resid_flag"].to_numpy())
    assert predict_glm(fit, data, factors, spec, model_offset=eta_base) == pytest.approx(
        manual_mu, rel=1e-9
    )
    eta = linear_predictor(fit, data, factors, spec, model_offset=eta_base)
    assert np.exp(eta) == pytest.approx(manual_mu, rel=1e-9)


@pytest.mark.req("FR-MODEL-24")
def test_diagnostics_require_the_arrays_for_a_model_offset_fit() -> None:
    data, eta_base = _residual_data()
    spec = _model_offset_spec()
    factors = [_factor("resid_flag", "resid_flag")]
    fit = fit_glm(data, spec, factors, model_offset=eta_base).result

    with pytest.raises(PredictionError) as refused:
        compute_diagnostics(fit, spec, factors, train=data, holdout=data.head(0))
    assert refused.value.code == "MODEL_OFFSET_MISSING"
    result = compute_diagnostics(
        fit, spec, factors, train=data, holdout=data.head(0),
        model_offset_train=eta_base, model_offset_holdout=eta_base[:0],
    )
    assert result.glm.deviance > 0


@pytest.mark.req("FR-MODEL-24")
def test_backtest_requires_and_honours_the_array() -> None:
    data, eta_base = _residual_data()
    spec = _model_offset_spec()
    factors = [_factor("resid_flag", "resid_flag")]
    fit = fit_glm(data, spec, factors, model_offset=eta_base).result

    with pytest.raises(PredictionError) as refused:
        backtest_model(
            fit, spec, factors, data,
            model_ref="model:residual@2",
            dataset_version_ref="dataset_version:book@2",
            fitted_on_ref="dataset_version:book@1",
        )
    assert refused.value.code == "MODEL_OFFSET_MISSING"
    summary = backtest_model(
        fit, spec, factors, data,
        model_ref="model:residual@2",
        dataset_version_ref="dataset_version:book@2",
        fitted_on_ref="dataset_version:book@1",
        model_offset=eta_base,
    )
    assert summary.partition.rows == data.height
