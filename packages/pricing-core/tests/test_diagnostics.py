"""Diagnostics and scoring (`02` FR-MODEL-49..55, 62, 81).

Built on a book with a **known** answer — three areas whose true relativities are 1, 2 and
3 against exposure — so the tests can assert what the numbers *are* rather than that they
exist. A diagnostics suite that only checks for non-null fields passes just as happily on
arithmetic that is wrong.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmSpec, OffsetSpec, Weighting
from pricing_core.modelling import compute_diagnostics, fit_glm, predict_glm
from pricing_core.modelling.diagnostics import deviance, unit_deviance

TRUE = {"a": 1.0, "b": 2.0, "c": 3.0}
BASE_RATE = 0.10


def _book(n: int = 6000, seed: int = 20260816) -> pl.DataFrame:
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
        }
    )


def _factor(slug: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(slug,),
    )


def _spec(factors: list[Factor]) -> GlmSpec:
    return GlmSpec(
        model_family_slug="freq",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors),
        family="poisson",
    )


def _fitted(frame: pl.DataFrame, factors: list[Factor]):
    spec = _spec(factors)
    return fit_glm(frame, spec, factors, seed=1).result, spec


@pytest.mark.req("FR-MODEL-62")
def test_a_model_scores_from_its_artifact_alone() -> None:
    """ADR-0003: a Model is data. `predict_glm` takes coefficients and a frame — nothing
    that remembers the fitting session, and nothing that needs `glum`.

    The assertion is the Poisson identity: with a log link, an intercept and an exposure
    offset, the fitted totals reproduce the observed total exactly. That only holds if the
    design columns, the base level and the offset are all reconstructed correctly, so it is
    a far stronger check than comparing shapes."""
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame, factors)

    mu = predict_glm(fit, frame, factors, spec)
    assert mu.shape == (frame.height,)
    assert float(np.sum(mu)) == pytest.approx(
        float(frame["claim_count"].sum()), rel=1e-6
    )


@pytest.mark.req("FR-MODEL-62")
def test_scoring_a_frame_without_the_offset_column_is_refused() -> None:
    """Negative: a frequency model scored with no exposure returns a rate as though it
    were a count. Silent, and wrong by whatever the exposure was."""
    from pricing_core.modelling.predict import PredictionError

    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame, factors)

    with pytest.raises(PredictionError, match="offset"):
        predict_glm(fit, frame.drop("exposure_years"), factors, spec)


@pytest.mark.req("FR-MODEL-54")
def test_diagnostics_report_train_and_holdout_side_by_side() -> None:
    frame = _book()
    train, holdout = frame[:4500], frame[4500:]
    factors = [_factor("area")]
    fit, spec = _fitted(train, factors)

    result = compute_diagnostics(fit, spec, factors, train=train, holdout=holdout)
    assert result.universal.train.rows == 4500
    assert result.universal.holdout.rows == frame.height - 4500
    # The A/E on the training set is exactly 1 for this family and link; the holdout's is
    # not, and that difference is the entire reason both are reported.
    assert result.universal.train.ae_overall == pytest.approx(1.0, abs=1e-6)
    assert result.universal.holdout.ae_overall != pytest.approx(1.0, abs=1e-9)


@pytest.mark.req("FR-MODEL-55")
def test_the_weighting_is_recorded_and_is_exposure_for_a_frequency_model() -> None:
    """FR-MODEL-55: an unweighted metric on an exposure-weighted problem must be labelled.
    It can only be labelled if the fit recorded which it was."""
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame[:4000], factors)
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:4000], holdout=frame[4000:]
    )
    assert result.universal.train.weighting is Weighting.EXPOSURE
    assert result.universal.holdout.weighting is Weighting.EXPOSURE


@pytest.mark.req("FR-MODEL-50")
def test_actual_versus_expected_is_reported_for_every_level() -> None:
    """A/E by level is what an actuary reads first. Every level of every categorical
    factor must appear — a level missing from the table is a level nobody inspects."""
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame[:4000], factors)
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:4000], holdout=frame[4000:]
    )
    levels = {c.level for c in result.universal.train.ae_by_factor}
    assert levels == set(TRUE)
    # A well-fitted model's A/E is near 1 on the data it was fitted on, per level.
    for cell in result.universal.train.ae_by_factor:
        assert cell.ae == pytest.approx(1.0, abs=0.15)
        assert cell.ci_95 is not None
        assert cell.ci_95[0] < cell.ae < cell.ci_95[1]


@pytest.mark.req("FR-MODEL-51")
def test_the_type_iii_test_separates_a_real_factor_from_noise() -> None:
    """The test that stops the p-value being decoration.

    `area` genuinely drives the response; `noise` is drawn independently of it. If both
    came back significant — or neither — the statistic would be reporting something other
    than the factor's contribution."""
    frame = _book()
    factors = [_factor("area"), _factor("noise")]
    fit, spec = _fitted(frame[:4500], factors)
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:4500], holdout=frame[4500:]
    )
    assert result.glm is not None
    tests = {t.factor: t for t in result.glm.type_iii_tests}
    assert tests["area"].p_value < 1e-10
    assert tests["noise"].p_value > 0.01
    # Two levels dropped for `area`, one for `noise` — the degrees of freedom a
    # categorical spends is levels - 1, and a wrong df gives a wrong p-value.
    assert tests["area"].df == 2
    assert tests["noise"].df == 1


@pytest.mark.req("FR-MODEL-51")
def test_deviance_and_information_criteria_are_computed() -> None:
    """`GlmFitResult.deviance` was declared by the spine and never populated. These are the
    numbers that were missing."""
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame[:4000], factors)
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:4000], holdout=frame[4000:]
    )
    assert result.glm is not None
    # A fitted model explains something, so its deviance is below the null model's.
    assert 0 < result.glm.deviance < result.glm.null_deviance
    assert result.glm.aic is not None
    assert result.glm.bic is not None
    # BIC penalises parameters more heavily than AIC at any n > 7.
    assert result.glm.bic > result.glm.aic
    assert result.glm.degrees_of_freedom == 4000 - len(fit.coefficients)


@pytest.mark.req("FR-MODEL-51")
def test_a_tweedie_fit_reports_no_aic_rather_than_a_wrong_one() -> None:
    """Tweedie's density has no closed form, so there is no exact log-likelihood to take an
    AIC from. `None` says that; a deviance-based stand-in would read as a measurement and
    differ from every other tool's AIC by an additive constant."""
    frame = _book()
    factors = [_factor("area")]
    spec = _spec(factors).model_copy(
        update={"family": "tweedie", "family_params": {"power": 1.5}}
    )
    fit = fit_glm(frame[:3000], spec, factors, seed=1).result
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:3000], holdout=frame[3000:], type_iii=False
    )
    assert result.glm is not None
    assert result.glm.deviance > 0
    assert result.glm.aic is None
    assert result.glm.bic is None


@pytest.mark.req("FR-MODEL-81")
def test_complexity_records_the_counts_and_the_thresholds_in_force() -> None:
    """FR-MODEL-81: a diagnostic always, a gate only where a workspace sets one. The
    thresholds are stored beside the measurements so a later reader can see what the fit
    was judged against rather than inferring today's settings onto it."""
    frame = _book()
    factors = [_factor("area"), _factor("noise")]
    fit, spec = _fitted(frame[:4000], factors)
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:4000], holdout=frame[4000:],
        max_factor_count=40, min_exposure_per_parameter=100.0, type_iii=False,
    )
    assert result.complexity.factor_count == 2
    assert result.complexity.parameter_count == len(fit.coefficients)
    assert result.complexity.max_factor_count == 40
    assert result.complexity.min_exposure_per_parameter == 100.0
    assert result.complexity.exposure_per_parameter is not None


@pytest.mark.req("FR-MODEL-81")
def test_complexity_thresholds_are_absent_when_the_workspace_sets_none() -> None:
    """The default is unset, not zero. Zero would be a limit nothing could satisfy."""
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame[:4000], factors)
    result = compute_diagnostics(
        fit, spec, factors, train=frame[:4000], holdout=frame[4000:], type_iii=False
    )
    assert result.complexity.max_factor_count is None
    assert result.complexity.min_exposure_per_parameter is None


@pytest.mark.req("FR-MODEL-50")
def test_a_model_that_orders_risk_scores_a_higher_gini_than_one_that_does_not() -> None:
    """Gini is an ordering statistic, so the test compares two orderings rather than
    asserting a magnitude: the real factor must beat pure noise. A Gini that did not move
    between those two would be measuring nothing."""
    frame = _book()
    train, holdout = frame[:4500], frame[4500:]

    signal = [_factor("area")]
    signal_fit, signal_spec = _fitted(train, signal)
    signal_result = compute_diagnostics(
        signal_fit, signal_spec, signal, train=train, holdout=holdout, type_iii=False
    )

    noise = [_factor("noise")]
    noise_fit, noise_spec = _fitted(train, noise)
    noise_result = compute_diagnostics(
        noise_fit, noise_spec, noise, train=train, holdout=holdout, type_iii=False
    )

    assert signal_result.universal.holdout.gini > noise_result.universal.holdout.gini


@pytest.mark.req("FR-MODEL-51")
def test_the_unit_deviance_sums_to_the_deviance() -> None:
    """The residual plots use the per-row quantity and the fit statistics use the total.
    Computing them by two routes is how they drift, so one is defined as the sum of the
    other and this says so."""
    y = np.array([0.0, 1.0, 2.0, 5.0])
    mu = np.array([0.5, 1.2, 1.8, 4.0])
    assert float(np.sum(unit_deviance(y, mu, family="poisson"))) == pytest.approx(
        deviance(y, mu, family="poisson")
    )


@pytest.mark.req("FR-MODEL-51")
def test_the_deviance_of_a_perfect_fit_is_zero() -> None:
    """The property that anchors the scale: deviance measures distance from the saturated
    model, so a prediction equal to the observation contributes nothing."""
    y = np.array([0.0, 1.0, 2.0, 5.0])
    assert deviance(y, y.copy(), family="poisson") == pytest.approx(0.0, abs=1e-12)
    positive = np.array([1.0, 2.0, 5.0])
    assert deviance(positive, positive.copy(), family="gamma") == pytest.approx(0.0, abs=1e-12)


@pytest.mark.req("FR-MODEL-51")
def test_a_deviance_below_zero_by_more_than_rounding_is_refused() -> None:
    """Deviance is non-negative by construction, so a negative total means the unit
    deviance for that family is wrong. Clamping float noise is right; clamping a real sign
    error would turn a wrong formula into a plausible number, so it raises."""
    import pricing_core.modelling.diagnostics as diag

    original = diag.unit_deviance
    try:
        diag.unit_deviance = lambda y, mu, **_: np.full_like(y, -1.0)  # type: ignore[assignment]
        with pytest.raises(ValueError, match="negative by more than"):
            diag.deviance(np.array([1.0, 1.0]), np.array([1.0, 1.0]), family="poisson")
    finally:
        diag.unit_deviance = original  # type: ignore[assignment]
