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

from model_schema import (
    Banding,
    BandingMethod,
    EbmSpec,
    EbmTerm,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    OffsetSpec,
    Weighting,
)
from pricing_core.modelling import (
    compute_diagnostics,
    fit_ebm,
    fit_gbm,
    fit_glm,
    predict_glm,
)
from pricing_core.modelling.diagnostics import (
    compute_ebm_diagnostics,
    compute_gbm_diagnostics,
    deviance,
    unit_deviance,
)

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


def _factor(slug: str, column: str | None = None, **over: object) -> Factor:
    """`column` defaults to the slug; `over` carries the EBM arm's banding factors."""
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": uuid4(), "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column or slug,),
    }
    fields.update(over)
    return Factor(**fields)  # type: ignore[arg-type]


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


# --------------------------------------------------------------------------------------
# FR-MODEL-50/54/81 — the EBM arm. A book of its own: `EbmSpec` refuses an offset
# (FR-MODEL-37) while `_book` above is a log-link frequency book, so the EBM arm gets
# the `test_ebm.py` fixture — numeric `speed`, categorical `area`, banded `age` — with
# `exposure_years` kept for the GBM comparison arm.
# --------------------------------------------------------------------------------------


AGE_BANDING = Banding(
    id=uuid4(), slug="age-band", dataset_id=uuid4(), version=1,
    column="age", method=BandingMethod.MANUAL,
    boundaries=(16.0, 25.0, 35.0, 50.0, 90.0),
    labels=("16-24", "25-34", "35-49", "50-89"),
)
EBM_BANDINGS = {AGE_BANDING.id: AGE_BANDING}

EBM_FACTORS = [
    _factor("speed"),
    _factor("area"),
    _factor("age_band", "age", type=FactorType.BANDING, banding_id=AGE_BANDING.id),
]


def _ebm_book(n: int = 2000, seed: int = 20260822) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    speed = rng.uniform(0.0, 120.0, n)
    area = rng.choice(["A", "B", "C"], size=n)
    age = rng.uniform(17.0, 90.0, n)
    eta = (
        -1.0
        + 0.012 * speed
        + np.where(area == "A", 0.0, np.where(area == "B", 0.4, 0.8))
        + 0.02 * (age - 40.0)
    )
    return pl.DataFrame(
        {
            "speed": speed,
            "area": area,
            "age": age,
            "exposure_years": rng.uniform(0.5, 1.0, n),
            "claim_count": rng.poisson(np.exp(eta)).astype(float),
        }
    )


def _ebm_spec(factors: list[Factor], **over: object) -> EbmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "objective": "rmse",
        "factors": tuple(f.id for f in factors),
    }
    base.update(over)
    return EbmSpec(**base)  # type: ignore[arg-type]


def _gbm_spec(factors: list[Factor]) -> GbmSpec:
    """The comparison arm of `test_the_ebm_arm_uses_the_same_partition_as_the_gbm_arm`.

    The EBM book's `claim_count` was generated without an exposure effect, but a
    frequency GBM carries one anyway — the exposure column exists, and an offset makes
    this the same shape of fit every frequency model in the repo gets."""
    return GbmSpec(
        model_type="xgboost",
        model_family_slug="motor-ad-frequency",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 3, "eta": 0.1, "num_boost_round": 40},
        factors=tuple(f.id for f in factors),
    )


@pytest.mark.req("FR-MODEL-50")
@pytest.mark.req("FR-MODEL-54")
def test_an_ebm_reports_universal_diagnostics_and_no_glm_or_gbm_block() -> None:
    """FR-MODEL-50's "all model types" and FR-MODEL-54's "both partitions", for the EBM.

    The EBM has no coefficient vector, no trees and no eval curve — its dependence
    structure *is* the transparency artifact — so `glm` and `gbm` are `None` rather
    than empty shells, and the universal block carries the whole report."""
    data = _ebm_book()
    train, holdout = data[:1500], data[1500:]
    spec = _ebm_spec(EBM_FACTORS)
    fit = fit_ebm(train, spec, EBM_FACTORS, bandings=EBM_BANDINGS)

    result = compute_ebm_diagnostics(
        fit, spec, EBM_FACTORS, train=train, holdout=holdout, bandings=EBM_BANDINGS,
    )
    assert result.universal.train.rows == 1500
    assert result.universal.holdout.rows == data.height - 1500
    # Every level of every categorical factor appears — `age_band` is a banding, and a
    # banding resolves to a categorical column, exactly as the GLM arm reports.
    assert {c.factor for c in result.universal.train.ae_by_factor} == {"area", "age_band"}
    assert {c.factor for c in result.universal.holdout.ae_by_factor} == {"area", "age_band"}
    assert result.universal.holdout.ae_overall > 0
    assert result.glm is None
    assert result.gbm is None
    assert result.complexity.factor_count == len(EBM_FACTORS)


@pytest.mark.req("FR-MODEL-81")
def test_ebm_complexity_counts_the_real_bins() -> None:
    """FR-MODEL-81 on an EBM: parameters are real bins, not terms and not slots.

    `bin_weights` zeroes the unused base slot, the trailing missing-value slot and any
    empty bins, so the nonzero count is what the model actually uses. The 2-D term
    proves grids count **cells**: one pair term is hundreds of parameters, and a
    term-count would report it as one."""
    data = _ebm_book()
    pair = EBM_FACTORS[:2]  # speed x area: exactly one pair term
    spec = _ebm_spec(pair, interactions=1)
    fit = fit_ebm(data, spec, pair, bandings=EBM_BANDINGS)

    grid_terms = [t for t in fit.terms if len(t.term_features) == 2]
    assert len(grid_terms) == 1

    def real_bins(term: EbmTerm) -> int:
        """The hand count the implementation's numpy is measured against: walk the
        slots cell by cell, however the term is nested."""
        weights = term.bin_weights
        if isinstance(weights[0], tuple):
            return sum(1 for row in weights for w in row if w != 0)
        return sum(1 for w in weights if w != 0)

    expected = sum(real_bins(t) for t in fit.terms)
    # A grid with a single real cell would prove nothing about cell-vs-term counting.
    assert expected > len(fit.terms)

    result = compute_ebm_diagnostics(
        fit, spec, pair, train=data[:1500], holdout=data[1500:], bandings=EBM_BANDINGS,
    )
    assert result.complexity.parameter_count == expected


@pytest.mark.req("FR-MODEL-50")
def test_the_ebm_arm_uses_the_same_partition_as_the_gbm_arm() -> None:
    """FR-MODEL-50: the universal block is one function, so both arms report the same
    shape of diagnostics on one book — same fields, same levels, same bin counts — and
    differ only in the numbers.

    That shape identity is what makes FR-MODEL-56's comparison a comparison rather than
    two conventions placed side by side: an actuary weighing an EBM's lift against a
    GBM's is reading the same arithmetic."""
    data = _ebm_book()
    train, holdout = data[:1500], data[1500:]

    ebm_spec = _ebm_spec(EBM_FACTORS)
    ebm_fit = fit_ebm(train, ebm_spec, EBM_FACTORS, bandings=EBM_BANDINGS)
    ebm_result = compute_ebm_diagnostics(
        ebm_fit, ebm_spec, EBM_FACTORS, train=train, holdout=holdout,
        bandings=EBM_BANDINGS,
    )

    gbm_spec = _gbm_spec(EBM_FACTORS)
    gbm_fit = fit_gbm(train, gbm_spec, EBM_FACTORS, bandings=EBM_BANDINGS)
    gbm_result = compute_gbm_diagnostics(
        gbm_fit.result, gbm_fit.booster_bytes, gbm_spec, EBM_FACTORS,
        train=train, holdout=holdout, bandings=EBM_BANDINGS,
    )

    ebm_holdout = ebm_result.universal.holdout
    gbm_holdout = gbm_result.universal.holdout
    assert set(type(ebm_holdout).model_fields) == set(type(gbm_holdout).model_fields)
    assert {c.factor for c in ebm_holdout.ae_by_factor} == {
        c.factor for c in gbm_holdout.ae_by_factor
    }
    assert len(ebm_holdout.lift) == len(gbm_holdout.lift)
    assert len(ebm_holdout.calibration) == len(gbm_holdout.calibration)
    # Same shape, different models: the two arms' mu's are built by different
    # arithmetic, so the holdout A/E cannot coincide.
    assert ebm_holdout.ae_overall != gbm_holdout.ae_overall
