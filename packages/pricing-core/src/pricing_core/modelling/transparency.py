"""Transparency artifacts for non-GLM models (`02` §3.6, FR-MODEL-33..37, 79).

`02` R3: fitting a black box is allowed; pricing with an unexplained one is not. Two forms,
both computed here and neither of them storing anything — ADR-0001 again, so the caller
gets data and the ids and blobs are the platform's business.

**TreeSHAP comes from the backends, not from the `shap` package** (FR-MODEL-35, amended in
`02` §8 on 2026-08-17). XGBoost's `pred_contribs` and LightGBM's `pred_contrib` are the same
TreeSHAP algorithm on the same trees, already linked against the booster this module holds.
Taking `shap` would have added scikit-learn, numba and their transitive weight to
`pricing-core` — which ADR-0001 keeps importable standalone — for utilities this platform
does not use: the plotting is the frontend's job (`02` §5.3) and the aggregation is fifteen
lines below.

The asymmetry that costs something is **interaction values**: XGBoost computes them
(`pred_interactions`), LightGBM does not compute them at all. `ShapSummary` reports that as
`interactions_available=False` rather than as an empty list, because "no interactions found"
is a finding this backend cannot make.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from uuid import UUID

import numpy as np
import polars as pl

from model_schema import (
    Banding,
    Factor,
    GbmFitResult,
    GbmSpec,
    GlmApproximation,
    GlmSpec,
    Grouping,
    ShapContribution,
    ShapInteraction,
    ShapSummary,
    WorstRegion,
)
from pricing_core.modelling.errors import ModellingError
from pricing_core.modelling.factors import resolve_factors
from pricing_core.modelling.gbm import GbmFitError, predict_gbm
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = ["build_glm_approximation", "build_shap_summary", "fidelity_statement"]

#: How many cells the worst-region search reports. Three, because FR-MODEL-36 asks *where*
#: the approximation fails rather than for a ranking — a list of twenty cells is a table
#: nobody reads, and the fidelity statement quotes the first of them.
_WORST_REGIONS = 3


def build_glm_approximation(
    result: GbmFitResult,
    booster: bytes,
    spec: GbmSpec,
    factors: Sequence[Factor],
    data: pl.DataFrame,
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> GlmApproximation:
    """FR-MODEL-34 — a GLM fitted to the GBM's **own predictions**, not to the response.

    That distinction is the whole method. Fitting a GLM to the data would produce a second
    model, and the question is not "what would a GLM say" but "how much of what this GBM
    says is expressible as a table". The residual between them is the part of the booster
    that cannot be rated, and `worst_regions` is where it lives.

    Gamma with a log link: the target is a strictly positive mean, and a Gaussian
    approximation to a multiplicative structure understates the fit exactly where the
    predictions are largest.
    """
    from pricing_core.modelling.glm import fit_glm

    report = progress or NullProgress()
    report.update(0.05, "scoring the booster")
    target = predict_gbm(
        result, booster, data, factors, bandings=bandings, groupings=groupings
    ).to_numpy()
    if np.any(target <= 0):
        raise GbmFitError(
            "APPROXIMATION_TARGET_NOT_POSITIVE",
            "the booster predicts a non-positive value, which a Gamma approximation "
            "cannot take as a response (FR-MODEL-34).",
        )

    # The approximating spec mirrors the GBM's structure — same factors, same offset — and
    # differs only in what it is fitted *to*. Anything else would make the comparison
    # between them a comparison of two different questions.
    surrogate_column = "__gbm_prediction__"
    approximation_spec = GlmSpec(
        model_family_slug=f"{spec.model_family_slug}-approx",
        dataset_version_id=spec.dataset_version_id,
        response_column=surrogate_column,
        offset=spec.offset,
        weight=spec.weight,
        factors=spec.factors,
        family="gamma",
        link="log",
        seed=spec.seed,
    )
    report.update(0.35, "fitting the approximation")
    # `.result` and not the covariance bytes beside it: the surrogate is a *description* of
    # the booster, and FR-MODEL-63's interval belongs to the model that priced the row, not
    # to an approximation of it. Storing this one would give a GBM a GLM's interval.
    fitted = fit_glm(
        data.with_columns(pl.Series(surrogate_column, target)),
        approximation_spec,
        factors,
        seed=spec.seed,
        bandings=bandings,
        groupings=groupings,
    ).result

    report.update(0.75, "measuring fidelity")
    from pricing_core.modelling.diagnostics import deviance
    from pricing_core.modelling.predict import predict_glm

    approximated = predict_glm(
        fitted, data.with_columns(pl.Series(surrogate_column, target)),
        factors, approximation_spec, bandings=bandings, groupings=groupings,
    )
    mean = float(np.mean(target))
    residual_ss = float(np.sum((target - approximated) ** 2))
    total_ss = float(np.sum((target - mean) ** 2))
    r_squared = 1.0 - residual_ss / total_ss if total_ss > 0 else 1.0
    full = deviance(target, approximated, family="gamma")
    null = deviance(target, np.full_like(target, mean), family="gamma")
    explained = 1.0 - full / null if null > 0 else 1.0

    report.update(0.90, "locating the worst regions")
    regions = _worst_regions(
        data, factors, target, approximated, bandings=bandings, groupings=groupings
    )
    report.update(1.0, "approximation complete")
    return GlmApproximation(
        r_squared=r_squared,
        deviance_explained=explained,
        coefficients=fitted.coefficients,
        relativities=fitted.relativities,
        worst_regions=regions,
    )


def _worst_regions(
    data: pl.DataFrame,
    factors: Sequence[Factor],
    target: np.ndarray,
    approximated: np.ndarray,
    *,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> tuple[WorstRegion, ...]:
    """The cells where the approximation is worst, with their share of the book.

    By **factor level**, not by arbitrary slice: a region an actuary cannot name is a
    region they cannot act on, and "young high-mileage drivers" is a rating cell while
    "rows 40000 to 41000" is not.
    """
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    error = np.abs(target - approximated) / np.maximum(target, 1e-12)
    rows = data.height
    found: list[WorstRegion] = []

    for slug, column in matrix.terms.items():
        if column not in matrix.categorical:
            continue
        levels = matrix.frame[column].cast(pl.String)
        for level in sorted({v for v in levels.unique().to_list() if v is not None}):
            mask = (levels == level).to_numpy()
            if not mask.any():
                continue
            found.append(
                WorstRegion(
                    description=f"{slug} = {level}",
                    exposure_share=float(mask.sum()) / max(rows, 1),
                    mean_abs_error_pct=float(np.mean(error[mask]) * 100.0),
                )
            )

    found.sort(key=lambda region: region.mean_abs_error_pct, reverse=True)
    return tuple(found[:_WORST_REGIONS])


def build_shap_summary(
    result: GbmFitResult,
    booster: bytes,
    spec: GbmSpec,
    factors: Sequence[Factor],
    data: pl.DataFrame,
    *,
    sample: int = 200_000,
    seed: int | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> ShapSummary:
    """FR-MODEL-35 — TreeSHAP mean |contribution| per factor, on a reproducible sample.

    The sample size and the seed are **persisted on the artifact**, because a SHAP summary
    computed on a different sample is a different summary, and two of them placed side by
    side in a model document would look like a change in the model.

    `top_interactions` are FR-MODEL-79 **suggestions**: the platform never writes a Factor
    into a Model Spec. Each carries its exposure share so an actuary sees what a suggestion
    is worth and over how much of the book before authoring an `interaction` Factor for it.
    """
    report = progress or NullProgress()
    report.update(0.05, "sampling")
    chosen_seed = spec.seed if seed is None else seed
    rows = min(sample, data.height)
    if rows < 1:
        raise ModellingError(
            "SHAP_SAMPLE_EMPTY", "a SHAP summary needs at least one row"
        )
    frame = (
        data
        if rows == data.height
        else data.sample(n=rows, seed=chosen_seed, shuffle=True)
    )

    matrix = resolve_factors(frame, factors, bandings=bandings, groupings=groupings)
    from pricing_core.modelling.gbm import _encode, _native_categoricals

    x, order, *_ = _encode(matrix, factors, maps=result.categorical_maps)
    native = _native_categoricals(result)
    report.update(0.35, "tree shap")

    if result.model_type == "xgboost":
        import xgboost as xgb

        loaded = xgb.Booster()
        loaded.load_model(bytearray(booster))
        frame_x = xgb.DMatrix(
            x, feature_names=list(order),
            feature_types=["c" if slug in native else "q" for slug in order],
            enable_categorical=True,
        )
        contributions = np.asarray(loaded.predict(frame_x, pred_contribs=True))
        interactions_available = True
    else:
        import lightgbm as lgb

        loaded_lgb = lgb.Booster(model_str=booster.decode())
        contributions = np.asarray(loaded_lgb.predict(x, pred_contrib=True))
        # LightGBM computes SHAP values and **not** SHAP interaction values. Reported as a
        # capability rather than as an empty list: "no interactions found" is a finding, and
        # it is not one this backend is able to make.
        interactions_available = False

    # The last column of both backends' output is the base value, not a feature.
    per_feature = np.abs(contributions[:, : len(order)])
    mean_abs = tuple(
        ShapContribution(factor=slug, value=float(np.mean(per_feature[:, index])))
        for index, slug in enumerate(order)
    )

    report.update(0.75, "interaction candidates")
    pairs: tuple[ShapInteraction, ...] = ()
    if interactions_available:
        pairs = _interaction_candidates(loaded, x, order, result)

    report.update(1.0, "shap summary complete")
    return ShapSummary(
        sample_rows=rows,
        seed=chosen_seed,
        mean_abs_contribution=tuple(
            sorted(mean_abs, key=lambda c: c.value, reverse=True)
        ),
        top_interactions=pairs,
        interactions_available=interactions_available,
    )


def _interaction_candidates(
    loaded: object, x: np.ndarray, order: Sequence[str], result: GbmFitResult
) -> tuple[ShapInteraction, ...]:
    """FR-MODEL-79's ranked pairs, from XGBoost's SHAP interaction values.

    Capped at a small sample: the array is `(rows, features+1, features+1)` and a full book
    at sixty factors would be tens of gigabytes for a ranking whose order settles in a few
    thousand rows.
    """
    import xgboost as xgb

    from pricing_core.modelling.gbm import _native_categoricals

    assert isinstance(loaded, xgb.Booster)
    native = _native_categoricals(result)
    capped = x[: min(x.shape[0], 5_000)]
    frame = xgb.DMatrix(
        capped, feature_names=list(order),
        feature_types=["c" if slug in native else "q" for slug in order],
        enable_categorical=True,
    )
    values = np.asarray(loaded.predict(frame, pred_interactions=True))
    features = len(order)
    strengths: list[ShapInteraction] = []
    for i in range(features):
        for j in range(i + 1, features):
            # Off-diagonal entries appear twice, once each way; the pair's strength is the
            # sum, which is what the interaction contributes to the score.
            strength = float(np.mean(np.abs(values[:, i, j] + values[:, j, i])))
            strengths.append(
                ShapInteraction(pair=(order[i], order[j]), strength=strength,
                                exposure_share=1.0)
            )
    strengths.sort(key=lambda pair: pair.strength, reverse=True)
    return tuple(strengths[:5])


def fidelity_statement(
    approximation: GlmApproximation | None, summary: ShapSummary | None
) -> str:
    """FR-MODEL-36's statement, in the words a Rating Version's approver will read.

    Generated rather than left to the author, because the requirement is that the statement
    says *where* the approximation fails and over how much exposure — and a free-text field
    with that obligation is a field that eventually says "good fit".
    """
    if approximation is None:
        assert summary is not None
        top = summary.mean_abs_contribution[0].factor if summary.mean_abs_contribution else "—"
        return (
            f"No GLM approximation was built. The SHAP summary over {summary.sample_rows:,} "
            f"sampled rows attributes most of the score to {top}. Without an approximation "
            "there is no relativity table, so this model is explainable but not rateable "
            "as one (FR-MODEL-34)."
        )

    parts = [
        f"The GLM approximation reproduces {approximation.r_squared * 100:.1f}% of the "
        f"model's prediction variance ({approximation.deviance_explained * 100:.1f}% of "
        "its deviance)."
    ]
    if approximation.worst_regions:
        worst = approximation.worst_regions[0]
        parts.append(
            f"Divergence concentrates in {worst.description} "
            f"({worst.exposure_share * 100:.1f}% of rows, mean |error| "
            f"{worst.mean_abs_error_pct:.1f}%). Rating on the approximation would misprice "
            "that cell."
        )
    else:
        parts.append("No factor level diverges materially.")
    if summary is not None and not summary.interactions_available:
        parts.append(
            "Interaction candidates were not computed: this backend produces SHAP values "
            "and not SHAP interaction values (FR-MODEL-79)."
        )
    return " ".join(parts)
