"""The EBM arm of fitting (FR-140). `interpret` is imported at call-site scope: the
scoring path (`predict.py`) must never grow an import of the fitting stack (`07`
NFR-535, `test_scoring_without_the_fitting_stack.py`).

An EBM's artifact **is** the model: the additive lookups this module exports verbatim
from the estimator are enough to rescore the model by a process that never ran `interpret`
(ADR-705 — there is no booster blob, no serialised estimator, and therefore no
`GlmFit`/`GbmFit`-style wrapper to carry bytes beside the result).
"""

from __future__ import annotations

import importlib.metadata
import time
from collections.abc import Mapping, Sequence
from uuid import UUID

import numpy as np
import polars as pl

from model_schema import (
    Banding,
    EbmCategoricalBins,
    EbmFeatureBins,
    EbmFitResult,
    EbmNumericBins,
    EbmSpec,
    EbmTerm,
    Factor,
    FactorType,
    Grouping,
)
from pricing_core.modelling.errors import FactorResolutionError
from pricing_core.modelling.factors import resolve_factors
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = ["EbmFitError", "fit_ebm"]


class EbmFitError(RuntimeError):
    """A fit that cannot be returned as a result (FR-140).

    `code` is the platform error code the API surfaces. Named rather than a bare
    `ValueError` for the reason `GlmFitError` gives: the caller has to distinguish
    "this spec cannot be fitted" from "this library raised something".
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


def _tuples(
    values: np.ndarray,
) -> tuple[float, ...] | tuple[tuple[float, ...], ...]:
    """`.tolist()` then tuple()s — the shape `EbmTerm` carries, written verbatim.

    A univariate term's array is 1-D and becomes a flat tuple; an interaction's grid
    is 2-D and becomes nested tuples, one row per bin of the first feature.
    """
    nested = values.tolist()
    if nested and isinstance(nested[0], list):
        return tuple(tuple(float(v) for v in row) for row in nested)
    return tuple(float(v) for v in nested)


def _ordinal_levels(
    factor: Factor, bandings: Mapping[UUID, Banding] | None
) -> tuple[str, ...]:
    """The banding's levels in band order — the ordinal set `interpret` is told.

    `Banding.levels` is the model's own "every level a resolved column can take": the
    labels in band order, the null level appended when declared. `interpret` refuses any
    value outside the set it is given ("X contains values outside of the ordinal set."),
    and `apply_banding` can emit the null level, so the set has to be the complete one.

    `resolve_factors` has already refused a banding factor whose banding is missing
    (`FactorResolutionError`), so the guard below is unreachable after a successful
    resolution — it exists so this lookup can never surface as a bare `KeyError`.
    """
    if (
        bandings is None
        or factor.banding_id is None
        or factor.banding_id not in bandings
    ):
        raise FactorResolutionError(
            f"factor {factor.slug!r} is a banding and its banding ({factor.banding_id}) "
            "was not supplied. The EBM arm resolves the same shapes `resolve_factors` "
            "does (ADR-703); refusing here keeps that promise loud."
        )
    return bandings[factor.banding_id].levels


def fit_ebm(
    data: pl.DataFrame,
    spec: EbmSpec,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> EbmFitResult:
    """Fit `spec` over `data`, returning the additive lookup tables themselves.

    `factors`, `bandings` and `groupings` are passed explicitly rather than read from the
    spec's ids: `pricing-core` resolves shapes, not references — looking one up would need
    a database, which ADR-703 forbids this package.

    The estimator is seeded with `random_state=spec.seed` — the spec's seed is what
    `spec_hash` pins, so the spec alone must reproduce the fit (Task 0.5, NFR-481).
    There is no `seed` argument: it mirrored `fit_glm`'s vestigial kwarg for call-site
    symmetry, neither was read by anything, and both were removed 2026-08-22
    (OQ-599, FR-179).
    """
    report = progress or NullProgress()
    report.check_cancelled()
    report.update(0.05, "ebm: encoding")
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)

    # A categorical column is passed as the levels themselves — `interpret` builds its own
    # dict `{level: 1-based index}`, which the artifact records by reading it back, so the
    # order it ends up in never needs to match anything here.
    #
    # Dated note 2026-08-21: 0.7.8's `feature_types` has no `"categorical"` value — the
    # string the brief's spike recipe used is refused by `_clean_x` ("categorical type
    # invalid"). The two real values for a string column are `"nominal"` (no order) and
    # an ordered levels list (ordinal); a banding is ordinal by construction, and the
    # monotone constraint of FR-122 can reach it only as the levels list
    # (`_ordinal_levels`).
    columns: list[np.ndarray] = []
    feature_types: list[str | tuple[str, ...]] = []
    categorical: set[str] = set()
    for factor in factors:
        slug = factor.slug
        series = matrix.frame[matrix.terms[slug]]
        if matrix.terms[slug] in matrix.categorical:
            columns.append(series.cast(pl.String).to_numpy())
            if factor.type is FactorType.BANDING:
                feature_types.append(_ordinal_levels(factor, bandings))
            else:
                feature_types.append("nominal")
            categorical.add(slug)
        else:
            columns.append(series.cast(pl.Float64).to_numpy())
            feature_types.append("continuous")

    if not columns:
        raise EbmFitError(
            "GBM_NO_FEATURES",
            "the feature matrix has no columns — every factor resolved to nothing, so "
            "there is nothing for the EBM arm to fit on.",
        )

    # Monotone constraints pre-checked before the estimator exists, because the failure
    # mode of a constraint is that *nothing happens* — and nothing happening is
    # indistinguishable from a constraint that was satisfied (FR-122). A banding is
    # **ordinal** — the same "a banding is ordinal" rule `gbm._encode` documents — so its
    # levels have an order the constraint can reach, and it is allowed.
    #
    # Dated note 2026-08-21: the pre-check's second refusal is not what 0.7.8 would do
    # on its own — a constraint on a nominal feature is accepted and its term silently
    # zeroed, not refused. The pre-check exists so the refusal arrives as a named code,
    # exactly as the spec's `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` note intends.
    slugs = {factor.slug for factor in factors}
    for slug in spec.monotone_constraints or {}:
        if slug not in slugs:
            raise EbmFitError(
                "EBM_MONOTONE_CONSTRAINT_INCOMPLETE",
                f"monotone constraint names {slug!r}, which is not among the fitted "
                "factors. 0.7.8 consumes the constraint list positionally, so a name it "
                "has never heard of would be silently dropped — and a constraint that "
                "does nothing is indistinguishable from one that held (FR-122).",
                terms=[slug],
            )
        factor = next(f for f in factors if f.slug == slug)
        if slug in categorical and factor.type is not FactorType.BANDING:
            raise EbmFitError(
                "EBM_MONOTONE_CONSTRAINT_INCOMPLETE",
                f"a monotone constraint cannot reach a continuous feature: {slug!r} is "
                "categorical and has no order for a constraint to hold against — 0.7.8 "
                "silently zeroes its term rather than refuse (FR-122).",
                terms=[slug],
            )
    # The full positional list, not the spec's partial dict: every feature needs an
    # entry, and the 0 default keeps an unconstrained feature explicit rather than
    # absent.
    #
    # Dated note 2026-08-21: the `f"feature {i}"` keyed-dict convention the brief
    # carried is wrong for 0.7.8 — the constructor docstring declares
    # `monotone_constraints: list of int` (0/+1/-1), `fit` consumes it positionally, and
    # a dict reaches the native booster where it dies with a bare `KeyError`. The
    # pre-check above still validates the spec's slug keys; this comprehension is the
    # translation into the positional form.
    constraints = [
        (spec.monotone_constraints or {}).get(factor.slug, 0) for factor in factors
    ]

    report.update(0.25, "ebm: fitting")
    sample_weight = (
        data[str(spec.weight.column)].cast(pl.Float64).to_numpy()
        if spec.weight.kind == "column"
        else None
    )
    y = data[spec.response_column].cast(pl.Float64).to_numpy()
    x = np.column_stack(columns)

    # The fitting stack is a call-site import: `07` NFR-535 keeps the scoring path
    # free of it, and this module's import must be the only one anywhere in the package.
    from interpret.glassbox import ExplainableBoostingRegressor

    start = time.monotonic()
    estimator = ExplainableBoostingRegressor(
        interactions=spec.interactions,
        max_bins=spec.max_bins,
        max_rounds=spec.max_rounds,
        monotone_constraints=constraints,     # the full positional list, built above
        random_state=spec.seed,               # the spec's seed is what spec_hash pins
        feature_types=feature_types,
    )
    try:
        estimator.fit(x, y, sample_weight=sample_weight)
    except ValueError as exc:
        # The backstop for any library-side refusal the pre-checks did not cover: the
        # pre-checks are the named path, this is a translation so a library `ValueError`
        # never surfaces as a stack trace (the FR-115 lesson).
        raise EbmFitError(
            "EBM_MONOTONE_CONSTRAINT_INCOMPLETE",
            f"interpret refused the EBM fit: {exc}",
        ) from exc

    report.update(0.85, "ebm: exporting tables")
    feature_order = tuple(f.slug for f in factors)
    bins: list[EbmFeatureBins] = []
    for index, kind in enumerate(feature_types):
        if kind != "continuous":
            # `bins_[i]` is the `(1,)` object array holding the level dict; index `[0]`
            # first. Both categorical kinds — `"nominal"` and the ordinal levels list
            # (the 2026-08-21 mapping) — export as the same `{level: 1-based index}`
            # dict, written through verbatim in the dict's own order: the artifact
            # records interpret's dict by reading it back.
            bins.append(
                EbmCategoricalBins(
                    # Iterating the dict yields its keys in order (SIM118).
                    levels=tuple(str(k) for k in estimator.bins_[index][0])
                )
            )
        else:
            bins.append(
                EbmNumericBins(
                    cuts=tuple(float(v) for v in np.ravel(estimator.bins_[index][0]))
                )
            )
    terms = [
        EbmTerm(
            term_features=tuple(int(i) for i in tf),
            term_name=estimator.term_names_[t],
            scores=_tuples(estimator.term_scores_[t]),
            standard_deviations=_tuples(estimator.standard_deviations_[t]),
            bin_weights=_tuples(estimator.bin_weights_[t]),
        )
        for t, tf in enumerate(estimator.term_features_)
    ]

    report.update(1.0, "ebm complete")
    # Returned **directly**, with no `GlmFit`/`GbmFit`-style wrapper: those wrappers exist
    # to carry bytes beside the artifact, and this artifact has no bytes — the tables are
    # the whole model (Task 0.6, ADR-705).
    return EbmFitResult(
        objective=spec.objective,
        link="identity",
        intercept=float(estimator.intercept_),
        feature_order=feature_order,
        bins=tuple(bins),
        terms=tuple(terms),
        # Dated note 2026-08-21: `best_iteration_` is a 2-D `[stage, bag]` int array, so
        # the brief's `int(estimator.best_iteration_)` raises TypeError. Stage 0 is the
        # mains stage and bag 0 is the first bag; that scalar is what the artifact's
        # `best_iteration` records.
        best_iteration=int(np.ravel(estimator.best_iteration_)[0]),
        rows=data.height,
        fit_seconds=time.monotonic() - start,
        library_versions={"interpret": importlib.metadata.version("interpret-core")},
    )
