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

The EBM arm needs none of the above, and says so. An EBM's artifact **is** the model
(`ebm.py`, ADR-0003): the shape functions export directly as rateable tables, so the
transparency block is those tables verbatim plus a fidelity statement that quotes no
number, and the monotonicity check (FR-MODEL-52) reads the tables rather than the
estimator.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast
from uuid import UUID

import numpy as np
import polars as pl

from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    Banding,
    EbmFitResult,
    EbmNumericBins,
    EbmShapeFunctions,
    EbmSpec,
    EbmTerm,
    Factor,
    GbmFitResult,
    GbmSpec,
    GlmApproximation,
    GlmFitResult,
    GlmSpec,
    Grouping,
    ModelSpecCommon,
    ShapContribution,
    ShapInteraction,
    ShapSummary,
    WorstRegion,
)
from pricing_core.modelling.errors import ModellingError
from pricing_core.modelling.factors import resolve_factors
from pricing_core.modelling.gbm import GbmFitError, predict_gbm
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = [
    "EBM_SHAPE_BLOB_VERSION",
    "GlmApproximationFit",
    "approximation_spec",
    "build_ebm_shape_functions",
    "build_glm_approximation",
    "build_shap_summary",
    "ebm_fidelity_statement",
    "ebm_monotonicity_verified",
    "fidelity_statement",
]

#: How many cells the worst-region search reports. Three, because FR-MODEL-36 asks *where*
#: the approximation fails rather than for a ranking — a list of twenty cells is a table
#: nobody reads, and the fidelity statement quotes the first of them.
_WORST_REGIONS = 3


def approximation_spec(spec: GbmSpec, *, source_model_id: UUID) -> GlmSpec:
    """The specification of the GLM that approximates `spec`'s model (FR-MODEL-34, 96).

    Pure, and separate from the fit, because the platform reserves the Model this describes
    **before** it spends a fit on it: `spec_hash` is taken over this object, and a surrogate
    that already exists must be recognised rather than fitted twice (FR-MODEL-66).

    The approximating spec mirrors the GBM's structure — same factors, same offset, same
    split — and differs only in what it is fitted *to*. Anything else would make the
    comparison between them a comparison of two different questions.
    """
    return GlmSpec(
        model_family_slug=f"{spec.model_family_slug}-approx",
        dataset_version_id=spec.dataset_version_id,
        split_ref=spec.split_ref,
        response_column=SURROGATE_RESPONSE_COLUMN,
        approximates_model_id=source_model_id,
        offset=spec.offset,
        weight=spec.weight,
        factors=spec.factors,
        family="gamma",
        link="log",
        seed=spec.seed,
    )


@dataclass(frozen=True)
class GlmApproximationFit:
    """What an approximation produces: the measurements, and the model behind them.

    Two halves rather than one because FR-MODEL-96 made the surrogate a Model. The
    `GlmApproximation` block is a summary and the platform gives it an identity, so it is
    built by `artifact_block` once the Model is reserved — this class cannot construct it,
    because a block with neither a model reference nor an inline table is refused at the
    type, and rightly.

    `train` and `holdout` carry the booster's predictions in
    `SURROGATE_RESPONSE_COLUMN`. They are returned rather than recomputed by the caller for
    the reason `GbmFit` returns its bytes: the scoring pass has already happened, and a
    second one is a second answer.
    """

    spec: GlmSpec
    result: GlmFitResult
    r_squared: float
    deviance_explained: float
    worst_regions: tuple[WorstRegion, ...]
    train: pl.DataFrame
    holdout: pl.DataFrame

    def artifact_block(self, approximating_model_id: UUID) -> GlmApproximation:
        """`02` §4.9's block, once the platform has reserved the Model that holds the table."""
        return GlmApproximation(
            approximating_model_id=approximating_model_id,
            r_squared=self.r_squared,
            deviance_explained=self.deviance_explained,
            worst_regions=self.worst_regions,
        )


def build_glm_approximation(
    result: GbmFitResult,
    booster: bytes,
    spec: GbmSpec,
    factors: Sequence[Factor],
    data: pl.DataFrame,
    *,
    holdout: pl.DataFrame,
    source_model_id: UUID,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> GlmApproximationFit:
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

    spec_ = approximation_spec(spec, source_model_id=source_model_id)

    frames: dict[str, pl.DataFrame] = {}
    for name, frame in (("train", data), ("holdout", holdout)):
        scored = predict_gbm(
            result, booster, frame, factors, bandings=bandings, groupings=groupings
        ).to_numpy()
        if np.any(scored <= 0):
            raise GbmFitError(
                "APPROXIMATION_TARGET_NOT_POSITIVE",
                f"the booster predicts a non-positive value on the {name} partition, "
                "which a Gamma approximation cannot take as a response (FR-MODEL-34).",
            )
        frames[name] = frame.with_columns(pl.Series(SURROGATE_RESPONSE_COLUMN, scored))

    train_frame = frames["train"]
    holdout_frame = frames["holdout"]
    target = train_frame[SURROGATE_RESPONSE_COLUMN].to_numpy()

    report.update(0.35, "fitting the approximation")
    # `.result` and not the covariance bytes beside it: the surrogate is a *description* of
    # the booster, and FR-MODEL-63's interval belongs to the model that priced the row, not
    # to an approximation of it. The platform strips `covariance_blob` from the result
    # before persisting it (FR-MODEL-102), so the reference cannot resolve to bytes nobody
    # stored.
    fitted = fit_glm(
        train_frame,
        spec_,
        factors,
        bandings=bandings,
        groupings=groupings,
    ).result

    report.update(0.75, "measuring fidelity")
    from pricing_core.modelling.diagnostics import deviance
    from pricing_core.modelling.predict import predict_glm

    # `02` §3.6 approximates the population the model was fitted on: the fit, the R², the
    # deviance and the worst regions all use the **train** frame. Approximating the holdout
    # would report how well a surrogate generalises, which is a different question.
    approximated = predict_glm(
        fitted, train_frame, factors, spec_, bandings=bandings, groupings=groupings,
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
        train_frame, factors, target, approximated,
        spec=spec, bandings=bandings, groupings=groupings,
    )
    report.update(1.0, "approximation complete")
    return GlmApproximationFit(
        spec=spec_,
        result=fitted,
        r_squared=r_squared,
        deviance_explained=explained,
        worst_regions=regions,
        train=train_frame,
        holdout=holdout_frame,
    )


def _worst_regions(
    data: pl.DataFrame,
    factors: Sequence[Factor],
    target: np.ndarray,
    approximated: np.ndarray,
    *,
    spec: ModelSpecCommon,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> tuple[WorstRegion, ...]:
    """The cells where the approximation is worst, with their share of the book.

    By **factor level**, not by arbitrary slice: a region an actuary cannot name is a
    region they cannot act on, and "young high-mileage drivers" is a rating cell while
    "rows 40000 to 41000" is not.

    The share is a share of **exposure** (FR-MODEL-36), the same quantity FR-MODEL-125
    names one module away: a row-count share on a motor book reports a level held for a
    fortnight as a region the same size as one held for a year, and stating how much of
    the book the approximation is wrong over is the whole purpose of the sentence it
    appears in. The frame is the **train** frame, deliberately — `02` §3.6 approximates
    the population the model was fitted on, so unlike a partial-dependence curve this must
    not report the holdout's profile.
    """
    from pricing_core.modelling.diagnostics import _share, _weights

    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    error = np.abs(target - approximated) / np.maximum(target, 1e-12)
    weights = _weights(spec, data)
    total_weight = float(weights.sum())
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
                    # Clamped because `WorstRegion.exposure_share` is `le=1.0` and the two sums
                    # run over different arrays: a single-level factor makes `weights[mask]` and
                    # `weights` the same set summed in a different order, which can land a last
                    # bit above 1.0 and raise rather than round. 1.0 is the exact answer there.
                    exposure_share=min(1.0, _share(float(weights[mask].sum()), total_weight)),
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
    holdout: pl.DataFrame,
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

    `top_interactions` are FR-MODEL-79 **suggestions**: the platform never writes a Factor into
    a Model Spec. Each carries its interaction `strength` and FR-MODEL-128's
    `holdout_strength_ratio` — a per-pair exposure share was `1.0` by construction and was
    withdrawn by OQ-MODEL-31 on 2026-08-23, and this ratio is the out-of-sample evidence that
    replaces it.

    `holdout` is **required, with no default**, matching `02` §5.2's declared signature and
    the sibling `build_glm_approximation`. Optional would make a forgotten argument produce
    exactly the pre-ratio artifact — silently, and indistinguishable from the legitimate
    absence a `None` ratio records.
    """
    report = progress or NullProgress()
    report.update(0.05, "sampling")
    chosen_seed = spec.seed if seed is None else seed
    rows = min(sample, data.height)
    if rows < 1:
        raise ModellingError(
            "SHAP_SAMPLE_EMPTY", "a SHAP summary needs at least one row"
        )
    x, order = _encoded_matrix(
        data, result, spec, factors,
        sample=sample, seed=chosen_seed, bandings=bandings, groupings=groupings,
    )
    from pricing_core.modelling.gbm import _native_categoricals

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
        in_sample = _pair_strengths(loaded, x, order, result)
        # FR-MODEL-128's second pass. `_encoded_matrix` is the same function that produced
        # `x` above, called with the same seed, the same row cap and the same
        # `categorical_maps` — one code path run twice, which is what makes the numerator
        # and the denominator comparable rather than merely adjacent.
        holdout_x, holdout_order = _encoded_matrix(
            holdout, result, spec, factors,
            sample=sample, seed=chosen_seed, bandings=bandings, groupings=groupings,
        )
        assert holdout_order == order, (
            "the two passes encoded to different column orders, so a pair's strengths are "
            "not the same quantity. Both encode with `result.categorical_maps`, so this is "
            "unreachable unless the maps stopped being the shared source (FR-MODEL-128)."
        )
        pairs = _interaction_candidates(
            in_sample, _pair_strengths(loaded, holdout_x, holdout_order, result)
        )

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


def _encoded_matrix(
    frame: pl.DataFrame,
    result: GbmFitResult,
    spec: GbmSpec,
    factors: Sequence[Factor],
    *,
    sample: int,
    seed: int,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> tuple[np.ndarray, Sequence[str]]:
    """Sample, resolve and encode one partition — the path both passes share.

    Extracted so FR-MODEL-128's "one code path run twice" is a fact about the code rather
    than a claim about two similar blocks. The seed, the sample size, the factor resolution
    and `result.categorical_maps` all arrive from the caller, so the two calls differ in the
    frame and in nothing else.

    A partition smaller than `sample` contributes all its rows rather than being padded;
    `OQ-MODEL-38` records that equal caps therefore give unequal N.
    """
    rows = min(sample, frame.height)
    sampled = (
        frame
        if rows == frame.height
        else frame.sample(n=rows, seed=seed, shuffle=True)
    )
    matrix = resolve_factors(sampled, factors, bandings=bandings, groupings=groupings)
    from pricing_core.modelling.gbm import _encode

    x, order, *_ = _encode(matrix, factors, maps=result.categorical_maps)
    return x, order


#: How many rows either pass measures interaction values on. The array is
#: `(rows, features+1, features+1)` and a full book at sixty factors would be tens of
#: gigabytes for a ranking whose order settles in a few thousand rows.
#:
#: **This is a cap, not a count**, and FR-MODEL-128 names "the same row cap" among the three
#: sames it draws comparability from. A partition smaller than the cap contributes all its
#: rows, so equal caps give unequal N — recorded as `OQ-MODEL-38`, not remedied here.
_INTERACTION_ROW_CAP = 5_000

#: How many ranked candidates FR-MODEL-79 publishes.
_TOP_CANDIDATES = 5


def _pair_strengths(
    loaded: object, x: np.ndarray, order: Sequence[str], result: GbmFitResult
) -> dict[tuple[str, str], float]:
    """Every pair's interaction strength on one encoded matrix, unranked.

    **This is the code path FR-MODEL-128 requires be run twice**, and returning the whole
    map rather than the ranked top five is what makes running it twice useful. The holdout
    pass needs a strength for *the pairs the in-sample pass selected* — a pair ranking fourth
    in-sample and eleventh out of sample is precisely the collapse the ratio exists to
    surface, and taking each partition's own top five would drop it silently while comparing
    two different pairs' numbers.

    So: same sampling, same `resolve_factors`, same `_encode` with the same
    `categorical_maps`, same cap, same off-diagonal sum. Only the frame differs.
    """
    import xgboost as xgb

    from pricing_core.modelling.gbm import _native_categoricals

    assert isinstance(loaded, xgb.Booster)
    native = _native_categoricals(result)
    capped = x[: min(x.shape[0], _INTERACTION_ROW_CAP)]
    frame = xgb.DMatrix(
        capped, feature_names=list(order),
        feature_types=["c" if slug in native else "q" for slug in order],
        enable_categorical=True,
    )
    values = np.asarray(loaded.predict(frame, pred_interactions=True))
    features = len(order)
    strengths: dict[tuple[str, str], float] = {}
    for i in range(features):
        for j in range(i + 1, features):
            # Off-diagonal entries appear twice, once each way; the pair's strength is the
            # sum, which is what the interaction contributes to the score.
            strengths[(order[i], order[j])] = float(
                np.mean(np.abs(values[:, i, j] + values[:, j, i]))
            )
    return strengths


def _interaction_candidates(
    in_sample: Mapping[tuple[str, str], float],
    holdout: Mapping[tuple[str, str], float] | None,
) -> tuple[ShapInteraction, ...]:
    """FR-MODEL-79's ranked pairs, with FR-MODEL-128's ratio where one is defined.

    The ranking is **by in-sample strength**, and the holdout is a lookup on the pairs that
    ranking chose. `OQ-MODEL-38` records the consequence: the denominator is a selected
    maximum and the numerator an independent re-measurement, so the expected ratio sits
    below `1` even where the structure is identical — which is not what the requirement's
    "near 1 says it survives" sentence assumes, and is not remedied here.
    """
    ranked = sorted(in_sample.items(), key=lambda item: item[1], reverse=True)
    return tuple(
        ShapInteraction(
            pair=pair,
            strength=strength,
            holdout_strength_ratio=_ratio(strength, holdout, pair),
        )
        for pair, strength in ranked[:_TOP_CANDIDATES]
    )


def _ratio(
    strength: float,
    holdout: Mapping[tuple[str, str], float] | None,
    pair: tuple[str, str],
) -> float | None:
    """The holdout value over the in-sample one, or `None` where there is no quotient.

    `None` rather than `0.0` or `1.0`: both are readable as findings — a total collapse and
    a perfect survival — and neither would be one. A zero denominator arises only when the
    booster found no interaction structure at all, and "there was nothing in sample either"
    is not the same claim as "it did not survive".
    """
    if holdout is None or strength == 0.0:
        return None
    return holdout[pair] / strength


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
            f"({worst.exposure_share * 100:.1f}% of exposure, mean |error| "
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


#: Version of the exported document. A reader that cannot parse it must refuse to
#: display it, not guess — an actuary reading tables under an unknown layout is
#: reading a different model.
EBM_SHAPE_BLOB_VERSION = "ebm-shape-functions/1"


def build_ebm_shape_functions(result: EbmFitResult) -> EbmShapeFunctions:
    """FR-MODEL-37 — the model exported as tables, which is the model.

    No approximation, no scoring, no data: everything a reader of the blob needs is
    already in `result`, and copying anything else into the document would give the
    second statement of one fact a chance to disagree with the first.

    Every float is written as a JSON number (`float(x)`): the tables are float64
    lookups, so the document carries the model's own precision rather than a rounded
    copy.
    """
    document = {
        "export_version": EBM_SHAPE_BLOB_VERSION,
        "link": result.link,
        "intercept": float(result.intercept),
        "best_iteration": result.best_iteration,
        "terms": [_ebm_term_blob(result, term) for term in result.terms],
    }
    return EbmShapeFunctions(terms_blob=json.dumps(document, sort_keys=True))


def _ebm_term_blob(result: EbmFitResult, term: EbmTerm) -> dict[str, object]:
    """One term as a rateable table: lookups, scores, uncertainty, real bins.

    `cuts`/`levels` are per feature, from `result.bins` in `features` order — a pair
    carries one list per feature of that kind, so a mixed pair has both keys, each
    aligned with the numeric (resp. categorical) features of `features`.
    """
    blob: dict[str, object] = {
        "name": term.term_name,
        "features": [result.feature_order[index] for index in term.term_features],
        "scores": _blob_values(term.scores),
        "standard_deviations": _blob_values(term.standard_deviations),
        "real_bins": _real_bins(term.bin_weights),
    }
    if len(term.term_features) == 1:
        bins = result.bins[term.term_features[0]]
        if isinstance(bins, EbmNumericBins):
            blob["kind"] = "numeric"
            blob["cuts"] = [float(cut) for cut in bins.cuts]
        else:
            blob["kind"] = "categorical"
            blob["levels"] = list(bins.levels)
    else:
        blob["kind"] = "interaction"
        cuts: list[list[float]] = []
        levels: list[list[str]] = []
        for index in term.term_features:
            bins = result.bins[index]
            if isinstance(bins, EbmNumericBins):
                cuts.append([float(cut) for cut in bins.cuts])
            else:
                levels.append(list(bins.levels))
        if cuts:
            blob["cuts"] = cuts
        if levels:
            blob["levels"] = levels
    return blob


def _blob_values(
    values: tuple[float, ...] | tuple[tuple[float, ...], ...],
) -> list[float] | list[list[float]]:
    """Scores/stds as JSON lists of numbers — nested for a grid, flat otherwise."""
    if values and isinstance(values[0], tuple):
        return [[float(v) for v in row] for row in values]
    flat = cast(tuple[float, ...], values)
    return [float(v) for v in flat]


def _real_bins(
    weights: tuple[float, ...] | tuple[tuple[float, ...], ...],
) -> list[bool] | list[list[bool]]:
    """The `bin_weights != 0` mask — where a lookup actually has a bin."""
    if weights and isinstance(weights[0], tuple):
        return [[w != 0.0 for w in row] for row in weights]
    flat = cast(tuple[float, ...], weights)
    return [w != 0.0 for w in flat]


def ebm_fidelity_statement() -> str:
    """FR-MODEL-36's statement for an EBM, which needs no measurement to make.

    The tables are the model — there is no surrogate whose divergence to report —
    so the statement says exactly that, rather than quoting a number that would
    read as a measured fidelity.
    """
    return (
        "This EBM's term shape functions are exported directly as rateable tables. "
        "There is no approximation step and no fidelity to measure: the exported "
        "tables are the fitted model, so a Rating Version that rates on them rates "
        "on the model itself (FR-MODEL-37)."
    )


def ebm_monotonicity_verified(result: EbmFitResult, spec: EbmSpec) -> bool | None:
    """FR-MODEL-52's check for the EBM arm, read off the exported tables.

    `None` when the spec declared no constraints — distinct from `False`, which
    would say a constraint was checked and failed. For a constrained feature, every
    term that contains it must be monotone in the declared direction along that
    feature's axis: the univariate term's real-bin scores, or each row/column of an
    interaction grid. Same tolerance as the GBM arm (`worst <= 1e-9`).
    """
    constraints = spec.monotone_constraints or {}
    active = {
        slug: direction for slug, direction in constraints.items() if direction != 0
    }
    if not active:
        return None
    index_of = {slug: index for index, slug in enumerate(result.feature_order)}
    worst = 0.0
    for slug, direction in active.items():
        if slug not in index_of:
            raise ModellingError(
                "EBM_MONOTONE_CONSTRAINT_UNKNOWN",
                f"monotone constraint names {slug!r}, which feature_order does not "
                "contain — a constraint on a feature the fit never saw cannot be "
                "checked (FR-MODEL-52).",
                terms=[slug],
            )
        feature = index_of[slug]
        for term in result.terms:
            if feature not in term.term_features:
                continue
            worst = max(worst, _term_monotonicity_worst(term, feature, direction))
    return worst <= 1e-9


def _term_monotonicity_worst(term: EbmTerm, feature: int, direction: int) -> float:
    """The worst step against `direction` along `feature`'s axis of `term`.

    Real bins only — the same `bin_weights != 0` mask the blob exports: a slice
    through the unused base slot, an empty bin or the trailing missing-value slot is
    not a reading of the model. A grid is checked per slice along the constrained
    feature's axis: per row when the second feature is constrained, per column when
    the first is.
    """
    if len(term.term_features) == 1:
        flat_scores = cast(tuple[float, ...], term.scores)
        flat_weights = cast(tuple[float, ...], term.bin_weights)
        return _direction_worst(
            [s for s, w in zip(flat_scores, flat_weights, strict=True) if w != 0.0],
            direction,
        )
    grid = cast(tuple[tuple[float, ...], ...], term.scores)
    grid_weights = cast(tuple[tuple[float, ...], ...], term.bin_weights)
    if not grid or not grid[0]:
        return 0.0
    axis = term.term_features.index(feature)
    worst = 0.0
    if axis == 0:
        # One column per bin of the second feature; each column's real rows are the
        # slices along the first feature's axis.
        for column in range(len(grid[0])):
            worst = max(
                worst,
                _direction_worst(
                    [grid[row][column] for row in range(len(grid))
                     if grid_weights[row][column] != 0.0],
                    direction,
                ),
            )
    else:
        for scores_row, weights_row in zip(grid, grid_weights, strict=True):
            worst = max(
                worst,
                _direction_worst(
                    [s for s, w in zip(scores_row, weights_row, strict=True) if w != 0.0],
                    direction,
                ),
            )
    return worst


def _direction_worst(sequence: Sequence[float], direction: int) -> float:
    """The GBM arm's convention (`diagnostics.py`): the largest step against the
    declared direction, clamped at zero.

    The sign convention matches the GBM arm: +1 means non-decreasing along the axis,
    -1 non-increasing. The tolerance is the caller's (`worst <= 1e-9`).
    """
    steps = np.diff(np.asarray(sequence, dtype=np.float64))
    against = -steps if direction == 1 else steps
    return float(max(0.0, float(against.max()) if against.size else 0.0))
