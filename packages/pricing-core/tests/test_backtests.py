"""Backtesting a fitted model on data it never saw (`02` FR-MODEL-57).

Built on the same known-answer book `test_diagnostics.py` uses — three areas whose true
relativities are 1, 2 and 3 — so the tests assert what the numbers *are*.

The two claims worth proving, rather than the fields being non-null:

* **"the same diagnostic shapes" means the same arithmetic.** `backtest_model` runs the
  partition the fit ran. The test that shows it is the degenerate one: backtest a model
  against its own training frame and every figure equals the fit-time train partition, to
  the last representable digit. Two implementations that merely agreed would drift.

* **Both arms.** FR-MODEL-57 says nothing about model type, and a backtest that worked only
  for GLMs would leave the GBM an actuary trusts least as the one nothing re-measures.

The refusals that make a backtest a backtest rather than a re-score live in the platform,
which is the layer that knows what a split part is; `backend/tests/test_backtests.py` proves
those.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    OffsetSpec,
    SplitRef,
    Weighting,
)
from pricing_core.modelling import backtest_model, compute_diagnostics, fit_gbm, fit_glm

TRUE = {"a": 1.0, "b": 2.0, "c": 3.0}
BASE_RATE = 0.10

MODEL_REF = "model:freq@1"
LATER_REF = "dataset_version:motor-2025h2@4"
FITTED_ON_REF = "dataset_version:motor-2024@1"


def _book(n: int = 6000, seed: int = 20260818, uplift: float = 1.0) -> pl.DataFrame:
    """The known-answer book. `uplift` multiplies the true frequency, which is what a
    deteriorating later period looks like: the same risks, more claims."""
    rng = np.random.default_rng(seed)
    area = rng.choice(list(TRUE), size=n)
    exposure = rng.uniform(0.5, 1.5, size=n)
    lam = np.array([BASE_RATE * TRUE[a] for a in area]) * exposure * uplift
    return pl.DataFrame(
        {
            "area": area,
            "exposure_years": exposure,
            "claim_count": rng.poisson(lam).astype(float),
        }
    )


def _factor(slug: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(slug,),
    )


def _fitted(frame: pl.DataFrame, factors: list[Factor]) -> tuple[object, GlmSpec]:
    spec = GlmSpec(
        model_family_slug="freq",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors),
        family="poisson",
    )
    return fit_glm(frame, spec, factors, seed=1).result, spec


@pytest.mark.req("FR-MODEL-57")
def test_a_backtest_reproduces_the_fit_time_partition_on_the_same_rows() -> None:
    """The identity that proves "the same diagnostic shapes" is the same code.

    Backtesting against the training frame is refused by the platform and is exactly the
    right thing to do here: it is the only input for which the expected answer is already
    known — the fit's own train partition, figure for figure.
    """
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame, factors)
    diagnostics = compute_diagnostics(
        fit, spec, factors, train=frame, holdout=frame, type_iii=False
    )

    summary = backtest_model(
        fit, spec, factors, frame,
        model_ref=MODEL_REF,
        dataset_version_ref=LATER_REF,
        fitted_on_ref=FITTED_ON_REF,
    )

    assert summary.partition == diagnostics.universal.train


@pytest.mark.req("FR-MODEL-57")
def test_a_deteriorating_period_shows_up_as_a_higher_ae() -> None:
    """The whole point of the artifact: FR-MODEL-57 calls it the evidence bridge into `05`.

    A period with 30 % more claims on the same risks must read as A/E ≈ 1.3, not as a
    number the reader has to interpret. Asserted as a band rather than a point because the
    book is sampled, but a band tight enough that a scale error could not pass.
    """
    factors = [_factor("area")]
    fit, spec = _fitted(_book(), factors)

    later = _book(seed=777, uplift=1.30)
    summary = backtest_model(
        fit, spec, factors, later,
        model_ref=MODEL_REF,
        dataset_version_ref=LATER_REF,
        fitted_on_ref=FITTED_ON_REF,
    )

    assert 1.2 < summary.partition.ae_overall < 1.4
    assert summary.partition.weighting is Weighting.EXPOSURE
    assert summary.partition.rows == later.height


@pytest.mark.req("FR-MODEL-57")
def test_a_backtest_refuses_to_name_the_version_it_was_fitted_on() -> None:
    """`BacktestSummary`'s invariant, reached through the function that builds one.

    Here as well as in the contract's own suite because this is the call site: a caller that
    passed the same ref twice would otherwise get a summary describing a memorisation test
    as out-of-time performance, and nothing between here and the database would object.
    """
    frame = _book()
    factors = [_factor("area")]
    fit, spec = _fitted(frame, factors)

    with pytest.raises(ValueError, match="fitted on"):
        backtest_model(
            fit, spec, factors, frame,
            model_ref=MODEL_REF,
            dataset_version_ref=FITTED_ON_REF,
            fitted_on_ref=FITTED_ON_REF,
        )


@pytest.mark.req("FR-MODEL-57")
def test_a_missing_column_is_an_error_and_not_a_zero() -> None:
    """A later period that renamed a column must fail loudly.

    Scoring with the term dropped moves every prediction toward the base level and returns
    an A/E that looks like drift. `predict_glm` already refuses; this asserts the refusal
    survives the backtest wrapper rather than being caught and defaulted somewhere.
    """
    factors = [_factor("area")]
    fit, spec = _fitted(_book(), factors)
    renamed = _book(seed=42).rename({"area": "region"})

    with pytest.raises(Exception, match="area"):
        backtest_model(
            fit, spec, factors, renamed,
            model_ref=MODEL_REF,
            dataset_version_ref=LATER_REF,
            fitted_on_ref=FITTED_ON_REF,
        )


@pytest.mark.req("FR-MODEL-57")
@pytest.mark.parametrize("backend", ["xgboost", "lightgbm"])
def test_a_gbm_is_backtested_through_the_same_path(backend: str) -> None:
    """FR-MODEL-57 says nothing about model type, so neither does this.

    Parametrized over both backends for FR-MODEL-72's reason: the scoring-side offset is
    implemented per backend, and a backtest that dropped it on LightGBM would under-predict
    by exactly the offset and report the deficit as deterioration.

    The `_family_of` dispatch is what is under test as much as the score — a GBM's family is
    implied by its objective, and reading it wrongly would compute A/E on the wrong family's
    deviance while every field still populated.

    **300 rounds, and the train A/E is asserted first.** At 30 the booster has not converged
    — train A/E 0.53 — and the backtest then reads 0.65 on a book with 30 % more claims. That
    number is the shrinkage, not the deterioration, and a test that only checked the later
    figure would have been calibrating its own bound against an unconverged fit. The
    train-side assertion is what says the model is a model before the backtest is read.
    """
    factors = [_factor("area")]
    spec = GbmSpec(
        model_type=backend,  # type: ignore[arg-type]
        model_family_slug="freq",
        dataset_version_id=uuid4(),
        split_ref=SplitRef(split_artifact_id=uuid4()),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 3, "eta": 0.1, "num_boost_round": 300},
        early_stopping=None,
        factors=tuple(f.id for f in factors),
    )
    train = _book()
    fit = fit_gbm(train, spec, factors)

    later = _book(seed=999, uplift=1.30)
    summary = backtest_model(
        fit.result, spec, factors, later,
        model_ref=MODEL_REF,
        dataset_version_ref=LATER_REF,
        fitted_on_ref=FITTED_ON_REF,
        booster=fit.booster_bytes,
    )

    on_train = backtest_model(
        fit.result, spec, factors, train,
        model_ref=MODEL_REF,
        dataset_version_ref=LATER_REF,
        fitted_on_ref=FITTED_ON_REF,
        booster=fit.booster_bytes,
    )
    assert on_train.partition.ae_overall == pytest.approx(1.0, abs=0.01)

    assert 1.1 < summary.partition.ae_overall < 1.35
    assert summary.partition.rows == later.height
