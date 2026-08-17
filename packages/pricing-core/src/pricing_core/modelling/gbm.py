"""Gradient boosting on XGBoost and LightGBM (`02` FR-MODEL-25..32, 71..73, §5.2).

**One contract, two backends** (FR-MODEL-25). `GbmSpec.model_type` chooses the library;
everything else — objective, offset, constraints, early stopping, categorical handling —
is written once and translated here. A spec that fitted on one backend and failed on the
other would be a forked contract wearing a shared name.

The requirement this module exists to satisfy carefully is **FR-MODEL-72**, and it is
worth stating plainly because the failure is silent:

* At **fit** time both backends behave alike. XGBoost takes the offset as `base_margin`
  on the `DMatrix`, LightGBM as `init_score` on the `Dataset`, and each includes it in the
  raw score.
* At **prediction** time they do not. XGBoost re-applies `base_margin` when the prediction
  matrix carries one, and substitutes its own `base_score` when it does not.
  `lightgbm.Booster.predict` has **no offset parameter at all** — it returns the tree
  contributions and nothing else, so the caller must add `init_score` back itself.

A single "apply the offset" implementation written against XGBoost's API therefore does
nothing on LightGBM and under-predicts by exactly the exposure. Both paths are written
separately below, and `test_a_prediction_scales_exactly_with_exposure` runs on each.

ADR-0001 holds: nothing here resolves a reference. Factors, bandings and groupings arrive
as objects, and the booster arrives and leaves as **bytes** — the caller stores them under
the digest this module computes, because content addressing makes the reference derivable
without storage (ADR-0003).
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final
from uuid import UUID

import numpy as np
import polars as pl

from model_schema import (
    Banding,
    BlobRef,
    Factor,
    GbmEvalPoint,
    GbmFitResult,
    GbmSpec,
    Grouping,
    LossTreatment,
    MonotonicDirection,
    OffsetSpec,
)
from pricing_core.modelling.factors import FactorMatrix, resolve_factors
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = ["GbmFit", "GbmFitError", "apply_loss_treatment", "fit_gbm", "predict_gbm"]

#: FR-MODEL-26's closed set, spelled in XGBoost's vocabulary because that is the
#: vocabulary the requirement uses, mapped to LightGBM's. The third element is the inverse
#: link, which LightGBM's raw-score path needs and XGBoost's does not — see `predict_gbm`.
_OBJECTIVES: Final[dict[str, tuple[str, str, str]]] = {
    "count:poisson": ("count:poisson", "poisson", "exp"),
    "reg:gamma": ("reg:gamma", "gamma", "exp"),
    "reg:tweedie": ("reg:tweedie", "tweedie", "exp"),
    "binary:logistic": ("binary:logistic", "binary", "logistic"),
}

#: Eval metrics that mean the same thing under two names. Anything else is passed to the
#: backend **verbatim** — the metric vocabulary is the backend's own, and refusing an
#: unrecognised one here would refuse metrics XGBoost supports and this table has not heard
#: of. An unknown name is therefore backend-specific, in the same way `backend_params` is.
_METRICS: Final[dict[str, str]] = {
    "poisson-nloglik": "poisson",
    "gamma-nloglik": "gamma",
    "rmse": "rmse",
    "mae": "l1",
    "logloss": "binary_logloss",
}

#: Hyperparameters spelled differently by the two libraries. `eta` is XGBoost's name for
#: the learning rate and `num_boost_round` is a `train()` argument on both rather than a
#: parameter, so neither reaches the params dict.
_HYPERPARAMETER_NAMES: Final[dict[str, str]] = {
    "eta": "learning_rate",
    "lambda": "lambda_l2",
    "alpha": "lambda_l1",
    "min_child_weight": "min_sum_hessian_in_leaf",
    "colsample_bytree": "feature_fraction",
    "subsample": "bagging_fraction",
}


class GbmFitError(RuntimeError):
    """A fit or a score that cannot be returned as a result.

    `code` is the platform error code the API surfaces. Named rather than a bare
    `ValueError` for the reason `GlmFitError` gives: the caller has to distinguish "this
    spec cannot be fitted" from "this library raised something".
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


@dataclass(frozen=True)
class GbmFit:
    """What a GBM fit returns: the artifact, and the bytes it addresses.

    Two values rather than one because `pricing-core` cannot store a blob (ADR-0001) and
    `GbmFitResult` cannot hold a booster (ADR-0003). The `BlobRef` inside `result` is
    already complete — a content-addressed reference is a pure function of the payload —
    so the caller's job is to store `booster_bytes` under that digest, and a caller that
    forgets has a reference that resolves to nothing rather than a model that half exists.
    """

    result: GbmFitResult
    booster_bytes: bytes


def apply_loss_treatment(response: np.ndarray, treatment: LossTreatment) -> np.ndarray:
    """FR-MODEL-73: large-loss treatment is applied to the **response**, at fit time.

    Not to the dataset. `01` VR-ACT-10 flags large losses and never removes them, so one
    validated Dataset Version serves many capping assumptions without re-ingestion — which
    is only true while the assumption is applied here.

    `spliced` and `excess` are declared by FR-MODEL-73 and implemented by nothing. They are
    refused by name rather than treated as `none`: fitting an uncapped model under a spec
    that says otherwise would be wrong in the one direction nobody checks, since the spec
    is what `spec_hash` and the model document both report.
    """
    if treatment.kind == "none":
        return response
    if treatment.kind == "capped":
        capped = np.minimum(response, float(treatment.cap_minor or 0))
        return np.asarray(capped, dtype=np.float64)
    raise GbmFitError(
        "LOSS_TREATMENT_UNIMPLEMENTED",
        f"loss treatment {treatment.kind!r} is declared by FR-MODEL-73 and built by no "
        "slice yet. Refused rather than applied as 'none', which would fit an uncapped "
        "model under a spec that records a treatment.",
        terms=[treatment.kind],
    )


def _offset(data: pl.DataFrame, offset: OffsetSpec, *, what: str) -> np.ndarray | None:
    """`log(exposure)` for `log_column`, the column itself for `column`, else nothing.

    Shared by the fit and the scoring path deliberately: FR-MODEL-71 asserts at load time
    that the offset can be *reconstructed*, and reconstruction means the same arithmetic,
    not arithmetic that resembles it.
    """
    if offset.kind == "none":
        return None
    column = str(offset.column)
    if column not in data.columns:
        raise GbmFitError(
            "OFFSET_NOT_RECONSTRUCTABLE",
            f"{what} needs the offset column {column!r} and the frame does not carry it "
            "(FR-MODEL-71). Refused rather than scored without it: both backends return "
            "predictions of the right shape and every one is wrong by the exposure.",
            terms=[column],
        )
    values = data[column].cast(pl.Float64).to_numpy()
    if offset.kind == "column":
        return values
    if np.any(values <= 0):
        raise GbmFitError(
            "OFFSET_REQUIRED_FOR_FREQUENCY",
            f"{column!r} has non-positive values and the offset is log(exposure) "
            "(FR-MODEL-27). A row with zero exposure contributes no information; it must "
            "be filtered before fitting rather than silently logged to -inf.",
            terms=[column],
        )
    return np.asarray(np.log(values), dtype=np.float64)


def _encode(
    matrix: FactorMatrix,
    factors: Sequence[Factor],
    *,
    maps: Mapping[str, Mapping[str, int]] | None = None,
) -> tuple[np.ndarray, tuple[str, ...], dict[str, str], dict[str, dict[str, int]]]:
    """One column per factor, categoricals as integer codes with the map returned.

    This *is* label encoding, and FR-MODEL-32 refuses the **silent** kind: the map comes
    back to be persisted, and `predict_gbm` reuses it rather than deriving a new one. A map
    derived from the scoring frame renumbers the levels whenever one is absent from it, and
    every prediction after that is for a different level.

    `maps` supplied means scoring: a level absent from the persisted map has no code, and
    inventing one would score it as whichever level happens to share the number.
    """
    columns: list[np.ndarray] = []
    order: list[str] = []
    dtypes: dict[str, str] = {}
    encodings: dict[str, dict[str, int]] = {}

    for factor in factors:
        slug = factor.slug
        column = matrix.terms[slug]
        series = matrix.frame[column]
        order.append(slug)
        if column in matrix.categorical:
            text = series.cast(pl.String)
            if maps is not None and slug in maps:
                mapping = dict(maps[slug])
                unknown = sorted(set(text.unique().to_list()) - set(mapping))
                if unknown:
                    raise GbmFitError(
                        "UNSEEN_LEVEL",
                        f"factor {slug!r} carries level(s) {unknown} that the fitted model "
                        "never saw, so they have no code in its persisted encoding map "
                        "(FR-MODEL-32).",
                        terms=unknown,
                    )
            else:
                levels = sorted(text.unique().to_list())
                mapping = {level: code for code, level in enumerate(levels)}
            encodings[slug] = mapping
            codes = text.replace_strict(mapping, return_dtype=pl.Int32).to_numpy()
            columns.append(codes.astype(np.float64))
            dtypes[slug] = "i32"
        else:
            columns.append(series.cast(pl.Float64).to_numpy())
            dtypes[slug] = "f64"

    if not columns:
        raise GbmFitError(
            "GBM_NO_FEATURES",
            "the feature matrix has no columns — every factor resolved to nothing, so "
            "there is nothing to boost on.",
        )
    return np.column_stack(columns), tuple(order), dtypes, encodings


def _monotone(
    factors: Sequence[Factor], order: Sequence[str], categorical: set[str]
) -> tuple[int, ...]:
    """FR-MODEL-28: the direction is declared on the Factor and derived here.

    A direction on an **unordered categorical** is refused. Both backends accept the
    constraint and apply it to whatever integer codes the levels happened to receive, so
    the model becomes monotone in an ordering nobody chose while the artifact records a
    direction that reads as an actuarial judgement.
    """
    by_slug = {factor.slug: factor for factor in factors}
    vector: list[int] = []
    for slug in order:
        direction = by_slug[slug].monotonic_direction
        if direction is not MonotonicDirection.NONE and slug in categorical:
            raise GbmFitError(
                "MONOTONE_ON_UNORDERED_FACTOR",
                f"factor {slug!r} is an unordered categorical and declares a "
                f"{direction.value} direction (FR-MODEL-28). The constraint would be "
                "applied to the encoding's arbitrary order, and recorded as a judgement.",
                terms=[slug],
            )
        vector.append(
            1 if direction is MonotonicDirection.INCREASING
            else -1 if direction is MonotonicDirection.DECREASING
            else 0
        )
    return tuple(vector)


def _objective(spec: GbmSpec) -> tuple[str, str, str]:
    if spec.objective.kind == "custom":
        raise GbmFitError(
            "CUSTOM_OBJECTIVE_UNAVAILABLE",
            f"objective {spec.objective.ref!r} is a Custom Objective (FR-MODEL-38), which "
            "no slice has built. `02` R4 would also require it to be approved before a "
            "model using it could be.",
            terms=[str(spec.objective.ref)],
        )
    name = str(spec.objective.name)
    if name not in _OBJECTIVES:
        raise GbmFitError(
            "OBJECTIVE_UNSUPPORTED",
            f"objective {name!r} is outside FR-MODEL-26's set "
            f"({', '.join(sorted(_OBJECTIVES))}).",
            terms=[name],
        )
    return _OBJECTIVES[name]


def _shared_params(spec: GbmSpec) -> dict[str, Any]:
    """Hyperparameters minus the two that are `train()` arguments rather than params."""
    return {
        key: value
        for key, value in spec.hyperparameters.items()
        if key not in {"num_boost_round"}
    }


def fit_gbm(
    data: pl.DataFrame,
    spec: GbmSpec,
    factors: Sequence[Factor],
    *,
    holdout: pl.DataFrame | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> GbmFit:
    """Fit `spec` over `data`, returning the artifact and the booster bytes.

    `holdout` is required when `spec.early_stopping.on == "holdout"`. `GbmSpec` refuses a
    stopping rule with no `split_ref`; this refuses a caller that declared the split and
    then passed no rows, because the backends fall back to the training set — FR-MODEL-30's
    prohibition, reached by omission rather than by asking for it.
    """
    report = progress or NullProgress()
    report.check_cancelled()
    report.update(0.05, "resolving factors")
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)

    report.update(0.15, "encoding features")
    x, order, dtypes, encodings = _encode(matrix, factors)
    constraints = _monotone(factors, order, set(encodings))
    base_margin = _offset(data, spec.offset, what="this fit")

    response = data[spec.response_column].cast(pl.Float64).to_numpy()
    response = apply_loss_treatment(response, spec.loss_treatment)

    xgb_objective, lgb_objective, _ = _objective(spec)
    rounds = int(spec.hyperparameters.get("num_boost_round", 100))
    stopping = spec.early_stopping
    if stopping is not None and stopping.on == "holdout" and holdout is None:
        raise GbmFitError(
            "HOLDOUT_REQUIRED",
            "early stopping is declared on a holdout and no holdout frame was passed "
            "(FR-MODEL-30). Without one the backend evaluates on the training rows, which "
            "is the training-set early stopping the requirement forbids.",
        )

    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None] | None = None
    if holdout is not None:
        holdout_matrix = resolve_factors(holdout, factors, bandings=bandings, groupings=groupings)
        vx, _, _, _ = _encode(holdout_matrix, factors, maps=encodings)
        vy = apply_loss_treatment(
            holdout[spec.response_column].cast(pl.Float64).to_numpy(), spec.loss_treatment
        )
        valid = (vx, vy, _offset(holdout, spec.offset, what="the holdout"))

    report.update(0.30, f"boosting {rounds} rounds on {spec.model_type}")
    started = time.perf_counter()
    if spec.model_type == "xgboost":
        payload, best, curve, versions = _fit_xgboost(
            spec, x, response, base_margin, valid, order, constraints,
            set(encodings), xgb_objective, rounds,
        )
    else:
        payload, best, curve, versions = _fit_lightgbm(
            spec, x, response, base_margin, valid, order, constraints,
            set(encodings), lgb_objective, rounds,
        )
    elapsed = time.perf_counter() - started
    report.update(0.95, "recording the artifact")

    return GbmFit(
        result=GbmFitResult(
            model_type=spec.model_type,
            booster_blob=BlobRef(
                sha256=hashlib.sha256(payload).hexdigest(),
                bytes=len(payload),
                media_type="application/json" if spec.model_type == "xgboost" else "text/plain",
            ),
            booster_format="xgboost_json" if spec.model_type == "xgboost" else "lightgbm_text",
            feature_order=order,
            feature_dtypes=dtypes,
            categorical_maps=encodings,
            monotone_constraints=constraints if any(constraints) else (),
            base_margin=spec.offset,
            best_iteration=best,
            eval_curve=curve,
            rows=data.height,
            fit_seconds=elapsed,
            library_versions=versions,
        ),
        booster_bytes=payload,
    )


def _interaction_groups(spec: GbmSpec, order: Sequence[str]) -> list[list[str]] | None:
    """FR-MODEL-29's groups, validated against the feature set.

    Returned as **names**, and converted to positions only where a backend wants them —
    the two disagree, which is one more thing FR-MODEL-25's single contract has to absorb.
    XGBoost resolves the groups against the `DMatrix`'s `feature_names` and raises
    `Constrained features are not a subset of training data feature names` on an integer;
    LightGBM takes indices.

    A name matching no feature is refused here rather than passed on, because the failure
    mode of a constraint is that *nothing happens* — and nothing happening is
    indistinguishable from a constraint that was satisfied.
    """
    if not spec.interaction_constraints:
        return None
    known = set(order)
    groups: list[list[str]] = []
    for group in spec.interaction_constraints:
        unknown = [name for name in group if name not in known]
        if unknown:
            raise GbmFitError(
                "INTERACTION_FEATURE_UNKNOWN",
                f"interaction group names {unknown}, which no factor in this spec "
                "produces (FR-MODEL-29). An unmatched name would leave the group "
                "permitting what it was written to forbid.",
                terms=unknown,
            )
        groups.append(list(group))
    return groups


def _fit_xgboost(
    spec: GbmSpec,
    x: np.ndarray,
    y: np.ndarray,
    base_margin: np.ndarray | None,
    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None] | None,
    order: Sequence[str],
    constraints: tuple[int, ...],
    categorical: set[str],
    objective: str,
    rounds: int,
) -> tuple[bytes, int, tuple[GbmEvalPoint, ...], dict[str, str]]:
    import xgboost as xgb

    feature_types = ["c" if slug in categorical else "q" for slug in order]
    params: dict[str, Any] = {
        "objective": objective,
        "seed": spec.seed,
        # `hist` is deterministic on CPU for a fixed seed and thread count, which is what
        # NFR-MODEL-6 needs. `deterministic_histogram` is **not** set: xgboost 3.4 reports
        # it as an unused parameter, and a parameter the library ignores is a guarantee
        # that exists only in the code that sets it.
        "tree_method": "hist",
        **_shared_params(spec),
        **spec.backend_params,
    }
    if any(constraints):
        params["monotone_constraints"] = tuple(constraints)
    interactions = _interaction_groups(spec, order)
    if interactions is not None:
        # Names, not positions: see `_interaction_groups`.
        params["interaction_constraints"] = interactions

    def matrix(features: np.ndarray, label: np.ndarray, margin: np.ndarray | None) -> Any:
        return xgb.DMatrix(
            features, label=label, base_margin=margin, feature_names=list(order),
            feature_types=feature_types, enable_categorical=True,
        )

    dtrain = matrix(x, y, base_margin)
    evals: list[tuple[Any, str]] = []
    if valid is not None:
        evals = [(matrix(valid[0], valid[1], valid[2]), "holdout")]
    stopping = spec.early_stopping
    if stopping is not None:
        params["eval_metric"] = stopping.metric

    history: dict[str, dict[str, list[float]]] = {}
    booster = xgb.train(
        params, dtrain, num_boost_round=rounds, evals=evals, evals_result=history,
        early_stopping_rounds=stopping.rounds if stopping and evals else None,
        verbose_eval=False,
    )
    best = int(getattr(booster, "best_iteration", rounds - 1))
    curve = tuple(
        GbmEvalPoint(iteration=index, metric=metric, holdout=value)
        for metric, values in history.get("holdout", {}).items()
        for index, value in enumerate(values)
    )
    payload = bytes(booster.save_raw(raw_format="json"))
    return payload, best + 1, curve, {"xgboost": xgb.__version__}


def _fit_lightgbm(
    spec: GbmSpec,
    x: np.ndarray,
    y: np.ndarray,
    base_margin: np.ndarray | None,
    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None] | None,
    order: Sequence[str],
    constraints: tuple[int, ...],
    categorical: set[str],
    objective: str,
    rounds: int,
) -> tuple[bytes, int, tuple[GbmEvalPoint, ...], dict[str, str]]:
    import lightgbm as lgb

    params: dict[str, Any] = {
        "objective": objective,
        "seed": spec.seed,
        "verbose": -1,
        # NFR-MODEL-6 again, and LightGBM needs both: `deterministic` alone still varies
        # with the multi-threaded histogram construction `force_row_wise` pins down.
        "deterministic": True,
        "force_row_wise": True,
        **{_HYPERPARAMETER_NAMES.get(k, k): v for k, v in _shared_params(spec).items()},
        **spec.backend_params,
    }
    if any(constraints):
        params["monotone_constraints"] = list(constraints)
    interactions = _interaction_groups(spec, order)
    if interactions is not None:
        position = {slug: index for index, slug in enumerate(order)}
        params["interaction_constraints"] = [[position[name] for name in g] for g in interactions]
    categorical_indices = [index for index, slug in enumerate(order) if slug in categorical]

    stopping = spec.early_stopping
    if stopping is not None:
        params["metric"] = _METRICS.get(stopping.metric, stopping.metric)

    train_set = lgb.Dataset(
        x, label=y, init_score=base_margin, feature_name=list(order),
        categorical_feature=categorical_indices, free_raw_data=False,
    )
    callbacks: list[Any] = []
    history: dict[str, dict[str, list[float]]] = {}
    valid_sets: list[Any] = []
    if valid is not None:
        valid_sets = [
            lgb.Dataset(valid[0], label=valid[1], init_score=valid[2], reference=train_set,
                        feature_name=list(order), categorical_feature=categorical_indices,
                        free_raw_data=False)
        ]
        callbacks.append(lgb.record_evaluation(history))
        if stopping is not None:
            callbacks.append(lgb.early_stopping(stopping.rounds, verbose=False))

    booster = lgb.train(
        params, train_set, num_boost_round=rounds, valid_sets=valid_sets,
        valid_names=["holdout"] if valid_sets else None, callbacks=callbacks,
    )
    best = int(booster.best_iteration or rounds)
    # The curve is reported under LightGBM's metric name; FR-MODEL-30 asks for the metric
    # that was *used*, and the spec's spelling is the one a reader will recognise.
    declared = stopping.metric if stopping else ""
    curve = tuple(
        GbmEvalPoint(iteration=index, metric=declared or metric, holdout=value)
        for metric, values in history.get("holdout", {}).items()
        for index, value in enumerate(values)
    )
    payload = booster.model_to_string(num_iteration=best).encode()
    return payload, best, curve, {"lightgbm": lgb.__version__}


def predict_gbm(
    result: GbmFitResult,
    booster: bytes,
    data: pl.DataFrame,
    factors: Sequence[Factor] = (),
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> pl.Series:
    """Score `data`, on the mean scale, with the offset applied **per backend**.

    This is FR-MODEL-72's asymmetry, and the whole reason the two branches below are not
    one. `μ = g⁻¹(f(x) + offset)`, and the two libraries disagree about who adds the
    offset:

    * XGBoost applies `base_margin` when the prediction matrix carries one, so the offset
      goes on the `DMatrix` and the library returns the mean.
    * LightGBM's `predict` takes no offset. It is asked for the **raw score**, the offset
      is added here, and the inverse link is applied here too.

    `factors` is optional: with them the model's features are re-resolved from source
    columns, without them the frame is expected to carry each feature under its factor
    slug. Passing them is what a banded or grouped factor needs, since the transformation
    is part of the feature and not of the frame.
    """
    if factors:
        matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
        x, order, _, _ = _encode(matrix, factors, maps=result.categorical_maps)
    else:
        missing = [slug for slug in result.feature_order if slug not in data.columns]
        if missing:
            raise GbmFitError(
                "FEATURE_MISSING",
                f"the frame does not carry {missing}. Pass the model's factors to have "
                "them resolved, or supply each feature under its factor slug.",
                terms=missing,
            )
        x, order, _, _ = _encode(
            FactorMatrix(
                frame=data,
                terms={slug: slug for slug in result.feature_order},
                categorical=tuple(result.categorical_maps),
            ),
            [
                Factor(id=UUID(int=0), slug=slug, dataset_id=UUID(int=0), version=1,
                       type="identity", source_columns=(slug,))  # type: ignore[arg-type]
                for slug in result.feature_order
            ],
            maps=result.categorical_maps,
        )
    if tuple(order) != result.feature_order:
        raise GbmFitError(
            "FEATURE_ORDER_MISMATCH",
            f"resolved features {order} do not match the fitted order "
            f"{result.feature_order}. The booster is positional.",
        )

    margin = _offset(data, result.base_margin, what="this prediction")

    if result.model_type == "xgboost":
        import xgboost as xgb

        loaded = xgb.Booster()
        loaded.load_model(bytearray(booster))
        frame = xgb.DMatrix(
            x, base_margin=margin, feature_names=list(result.feature_order),
            feature_types=["c" if slug in result.categorical_maps else "q"
                           for slug in result.feature_order],
            enable_categorical=True,
        )
        values = loaded.predict(frame, iteration_range=(0, result.best_iteration))
    else:
        import lightgbm as lgb

        lgb_booster = lgb.Booster(model_str=booster.decode())
        raw = lgb_booster.predict(x, raw_score=True)
        raw = np.asarray(raw, dtype=np.float64)
        if margin is not None:
            raw = raw + margin
        values = np.exp(raw)

    return pl.Series("prediction", np.asarray(values, dtype=np.float64))
