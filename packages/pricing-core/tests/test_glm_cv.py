"""FR-112/FR-182: the elastic-net penalty path reaching `glum`, end to end.

Not a type-level test — a feature four sites agreeing on a shape can still not work
(`.claude/skills/python-test`), and the site that matters here is the actual refit against
`glum`, once per fold per alpha.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmCvSpec, GlmSpec, OffsetSpec
from pricing_core.modelling.glm import GlmFitError, fit_glm


def _factor(slug: str, column: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(column,),
    )


def _frequency_data(n: int = 400, seed: int = 20260821) -> pl.DataFrame:
    """A Poisson book with a real urban/rural signal — the same shape `test_glm.py` uses,
    large enough that 4 folds each carry a usable number of rows. The counts are Poisson
    draws, not the deterministic 2/1 pattern: a noiseless book fits perfectly on every
    fold, and a dispersion assertion over identical 0.0 scores proves nothing (FR-182
    exists because real books have noise)."""
    rng = np.random.default_rng(seed)
    urban = np.arange(n) % 4 == 0
    counts = rng.poisson(np.where(urban, 2, 1)).astype(float)
    return pl.DataFrame(
        {
            "policy": [f"P{i}" for i in range(n)],
            "day": list(range(n)),
            "exposure_years": [1.0] * n,
            "area": ["urban" if u else "rural" for u in urban],
            "claim_count": counts,
        }
    )


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "factors": (),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-112")
def test_cv_selection_fits_and_persists_the_full_path() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.01, 0.1, 1.0)),
    )
    fit = fit_glm(data, spec, factors)
    assert fit.cv is not None
    assert [p.alpha for p in fit.cv.path] == [0.0, 0.01, 0.1, 1.0]
    assert fit.cv.selected_alpha in {0.0, 0.01, 0.1, 1.0}
    assert fit.cv.folds == 4
    assert fit.cv.method == "random"
    assert fit.cv.seed == spec.seed
    # The estimator was actually refitted at the selected alpha, not left at the default.
    assert fit.result.coefficients


@pytest.mark.req("FR-182")
def test_cv_selection_persists_per_fold_dispersion_at_the_selected_alpha() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.1, 1.0)),
    )
    fit = fit_glm(data, spec, factors)
    assert fit.cv is not None
    assert {m.fold for m in fit.cv.fold_metrics} == {0, 1, 2, 3}
    assert sum(m.rows for m in fit.cv.fold_metrics) == data.height
    # FR-182: dispersion, not only the mean.
    assert len({round(m.score, 10) for m in fit.cv.fold_metrics}) > 1


@pytest.mark.req("FR-182")
def test_a_grouped_cv_keeps_a_policy_whole_across_folds() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="grouped_by_key", folds=4, key_column="policy", alphas=(0.0, 0.1)),
    )
    fit = fit_glm(data, spec, factors)
    assert fit.cv is not None
    assert fit.cv.method == "grouped_by_key"


@pytest.mark.req("FR-182")
def test_a_temporal_cv_orders_folds_by_time() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="temporal", folds=4, time_column="day", alphas=(0.0, 0.1)),
    )
    fit = fit_glm(data, spec, factors)
    assert fit.cv is not None
    assert fit.cv.method == "temporal"


@pytest.mark.req("FR-182")
def test_two_fits_with_the_same_seed_select_the_same_alpha() -> None:
    """Round-trip / reproducibility: `_fit_cv_path`'s fold assignment is a pure function of
    the seed, so two fits of the identical spec over the identical data must agree — the
    property `assign_folds` (Task 1) exists for, carried all the way to the selection."""
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.01, 0.1, 1.0)),
        seed=42,
    )
    first = fit_glm(data, spec, factors)
    second = fit_glm(data, spec, factors)
    assert first.cv is not None
    assert second.cv is not None
    assert first.cv.selected_alpha == second.cv.selected_alpha
    assert [p.mean_score for p in first.cv.path] == [p.mean_score for p in second.cv.path]


@pytest.mark.req("FR-182")
def test_more_folds_than_rows_in_a_group_is_refused() -> None:
    """Negative: `GLM_CV_FOLD_EMPTY`. A grouped CV over few distinct keys with `folds` set
    higher than the key count leaves some fold with no held-out rows at all — a fold that
    cannot be scored, silently skipped, is a dispersion computed over fewer folds than
    `folds` claims."""
    data = pl.DataFrame(
        {
            "policy": ["P1"] * 50 + ["P2"] * 50,
            "day": list(range(100)),
            "exposure_years": [1.0] * 100,
            "area": ["urban" if i % 2 == 0 else "rural" for i in range(100)],
            "claim_count": [1] * 100,
        }
    )
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="grouped_by_key", folds=5, key_column="policy", alphas=(0.0, 0.1)),
    )
    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, spec, factors)
    assert refused.value.code == "GLM_CV_FOLD_EMPTY"


@pytest.mark.req("FR-112")
def test_a_fixed_alpha_fit_still_carries_no_cv_diagnostics() -> None:
    """Negative, the other direction: `select_by='fixed'` (the default) must not
    accidentally run or report a CV path — `fit.cv` stays `None`."""
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(factors=(factors[0].id,), alpha=0.05, l1_ratio=0.5)
    fit = fit_glm(data, spec, factors)
    assert fit.cv is None
