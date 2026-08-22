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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal, NamedTuple
from uuid import UUID

import numpy as np
import polars as pl

from model_schema import (
    FITTABLE_METRIC_STATUSES,
    FITTABLE_OBJECTIVE_STATUSES,
    Banding,
    BlobRef,
    CustomMetric,
    CustomObjective,
    DroppedEvalMetric,
    Factor,
    FactorType,
    GbmEvalPoint,
    GbmFitResult,
    GbmFunctionRef,
    GbmSpec,
    Grouping,
    LossTreatment,
    MetricDirection,
    MonotonicDirection,
    ObjectiveBackend,
    OffsetSpec,
    ResponseKind,
    WeightSpec,
)
from pricing_core.modelling.errors import ObjectiveError
from pricing_core.modelling.factors import FactorMatrix, resolve_factors
from pricing_core.modelling.metrics import evaluate_metric
from pricing_core.modelling.objectives import (
    ObjectiveFns,
    compile_objective,
    make_lgb_objective,
    make_xgb_objective,
)
from pricing_core.progress import NullProgress, ProgressCallback

#: What each backend's callable-objective hook is handed and returns. XGBoost passes the
#: raw scores and the `DMatrix`; LightGBM passes labels, scores and weights.
type XgbObjective = Callable[[np.ndarray, Any], tuple[np.ndarray, np.ndarray]]
type LgbObjective = Callable[[np.ndarray, Any], tuple[np.ndarray, np.ndarray]]
#: `feval`/`custom_metric` callables, both keyed by ref so a fit can report several at
#: once. XGBoost's `custom_metric` returns `(name, value)` pairs — direction is instead
#: carried by the `EarlyStopping` callback's `maximize`, which is per-metric because it is
#: bound to one `metric_name`. LightGBM's `feval` carries direction in the tuple itself,
#: because `first_metric_only` compares whichever metric is first without a name at all.
type XgbFeval = Callable[[np.ndarray, Any], list[tuple[str, float]]]
type LgbFeval = Callable[[np.ndarray, Any], list[tuple[str, float, bool]]]

__all__ = [
    "SUPPORTED_GBM_OBJECTIVES",
    "GbmFit",
    "GbmFitError",
    "apply_loss_treatment",
    "fit_gbm",
    "objective_family",
    "predict_gbm",
    "tree_summary",
]

#: FR-MODEL-26's closed set, spelled in XGBoost's vocabulary because that is the
#: vocabulary the requirement uses, mapped to LightGBM's. The third element is the inverse
#: link, which LightGBM's raw-score path needs and XGBoost's does not — see `predict_gbm`.
#:
#: `SUPPORTED_GBM_OBJECTIVES` below is the same set, exported: `POST /model-specs/validate`
#: reports an unsupported objective as a spec problem before a Job exists (FR-MODEL-44) and
#: the fit refuses it again as a backstop. Two hand-written lists would eventually disagree
#: about which objectives the platform supports, and the disagreement would show up as a
#: spec that validated and then failed.
_OBJECTIVES: Final[dict[str, tuple[str, str, Literal["exp", "logistic"]]]] = {
    "count:poisson": ("count:poisson", "poisson", "exp"),
    "reg:gamma": ("reg:gamma", "gamma", "exp"),
    "reg:tweedie": ("reg:tweedie", "tweedie", "exp"),
    "binary:logistic": ("binary:logistic", "binary", "logistic"),
}

#: FR-MODEL-26's set, for callers that need to *check* rather than translate.
SUPPORTED_GBM_OBJECTIVES: Final[frozenset[str]] = frozenset(_OBJECTIVES)

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
    #: FR-MODEL-52's evaluation curve, which belongs on the **diagnostics** artifact rather
    #: than on the fit. Returned here because the fit is what produces it and
    #: `compute_gbm_diagnostics` is a separate call — handing it back is what lets the
    #: caller place it where the requirement says without the fit reaching into diagnostics.
    eval_curve: tuple[GbmEvalPoint, ...] = ()


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


def _weights(data: pl.DataFrame, weight: WeightSpec) -> np.ndarray | None:
    """The weight column as a float array, or `None` for `kind: "none"` (FR-MODEL-19).

    Two lines, mirroring `fit_glm`'s (glm.py) deliberately: severity weights by claim
    count and burning cost by exposure are properties of the *response*, not of the
    estimator, so the same spec must mean the same thing for a GLM, a GBM and an EBM. A
    missing column raises Polars' own `ColumnNotFoundError` here exactly as it does there
    — a named `GbmFitError` would make the platform answer one malformed spec differently
    depending on which model type happened to read it.
    """
    if weight.kind == "none":
        return None
    return data[str(weight.column)].cast(pl.Float64).to_numpy()


class Encoded(NamedTuple):
    """The feature matrix and everything the backends and the artifact need to read it."""

    x: np.ndarray
    order: tuple[str, ...]
    #: `f64` numeric · `ord` ordered integer codes · `cat` native categorical (FR-MODEL-31).
    dtypes: dict[str, str]
    maps: dict[str, dict[str, int]]
    #: The features whose levels have **no** order — the ones a backend must be told are
    #: categorical, and the ones FR-MODEL-28 refuses a direction on.
    unordered: frozenset[str]


def _encode(
    matrix: FactorMatrix,
    factors: Sequence[Factor],
    *,
    maps: Mapping[str, Mapping[str, int]] | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
) -> Encoded:
    """One column per factor, categoricals as integer codes with the map returned.

    This *is* label encoding, and FR-MODEL-32 refuses the **silent** kind: the map comes
    back to be persisted, and `predict_gbm` reuses it rather than deriving a new one. A map
    derived from the scoring frame renumbers the levels whenever one is absent from it, and
    every prediction after that is for a different level.

    `maps` supplied means scoring: a level absent from the persisted map has no code, and
    inventing one would score it as whichever level happens to share the number.

    **A banding is ordinal, and is encoded as such**: its codes run in the artifact's own
    label order — which is boundary order, the order of the underlying values — and it is
    *not* declared to the backend as a categorical. Both halves matter.

    The order is what makes FR-MODEL-28 meaningful on a band: sorted lexicographically
    `"10-49"` lands second, between `"0-1"` and `"2-4"`, so "frequency falls with licence
    years" would constrain the alphabet. The declaration is what makes it *possible*:
    LightGBM refuses monotone constraints on a categorical feature and does so by aborting
    the process — `[LightGBM] [Fatal] The output cannot be monotone with respect to
    categorical features`, verified here on 4.7.0 — so a band declared categorical cannot
    carry the constraint `02` §4.4's own `driver_age_banded` example declares.

    FR-MODEL-32 refuses the silent label-encoding of an **unordered** categorical. A band
    is ordered and its map is persisted, so this is neither.
    """
    columns: list[np.ndarray] = []
    order: list[str] = []
    dtypes: dict[str, str] = {}
    encodings: dict[str, dict[str, int]] = {}
    unordered: set[str] = set()

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
                        "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED",
                        f"factor {slug!r} carries level(s) {unknown} that the fitted model "
                        "never saw, so they have no code in its persisted encoding map "
                        "(FR-MODEL-32).",
                        terms=unknown,
                    )
            else:
                declared = _ordered_levels(factor, bandings)
                observed = {v for v in text.unique().to_list() if v is not None}
                levels = (
                    [level for level in declared if level in observed]
                    if declared
                    else sorted(observed)
                )
                mapping = {level: code for code, level in enumerate(levels)}
            encodings[slug] = mapping
            codes = text.replace_strict(mapping, return_dtype=pl.Int32).to_numpy()
            columns.append(codes.astype(np.float64))
            ordinal = factor.type is FactorType.BANDING
            dtypes[slug] = "ord" if ordinal else "cat"
            if not ordinal:
                unordered.add(slug)
        else:
            columns.append(series.cast(pl.Float64).to_numpy())
            dtypes[slug] = "f64"

    if not columns:
        raise GbmFitError(
            "GBM_NO_FEATURES",
            "the feature matrix has no columns — every factor resolved to nothing, so "
            "there is nothing to boost on.",
        )
    return Encoded(
        np.column_stack(columns), tuple(order), dtypes, encodings, frozenset(unordered)
    )


def _ordered_levels(
    factor: Factor, bandings: Mapping[UUID, Banding] | None
) -> tuple[str, ...]:
    """The order a factor's levels genuinely have, or empty when they have none.

    A **banding** has one and the artifact states it: `labels` runs in boundary order, which
    is the order of the underlying values. Nothing else does. An `identity` categorical's
    levels are names, and a `grouping`'s targets are a modelling decision whose order this
    module would be asserting rather than reading — so both fall back to a sorted encoding
    and `_monotone` refuses a direction on them.
    """
    if factor.type is not FactorType.BANDING or not bandings or factor.banding_id is None:
        return ()
    banding = bandings.get(factor.banding_id)
    return banding.labels if banding else ()


def _monotone(
    factors: Sequence[Factor], order: Sequence[str], unordered: frozenset[str]
) -> tuple[int, ...]:
    """FR-MODEL-28: the direction is declared on the Factor and derived here.

    A direction on an **unordered** categorical is refused. Both backends accept the
    constraint and apply it to whatever integer codes the levels happened to receive, so
    the model becomes monotone in an ordering nobody chose while the artifact records a
    direction that reads as an actuarial judgement.

    A **banding is ordered** and is therefore allowed — `02` §4.4's own example is a
    monotone constraint on `driver_age_banded`, and `wf-01` C7 declares one. `_encode`
    codes it in the artifact's label order and declares it ordinal rather than categorical,
    which is what lets the constraint hold in the underlying value.
    """
    by_slug = {factor.slug: factor for factor in factors}
    vector: list[int] = []
    for slug in order:
        direction = by_slug[slug].monotonic_direction
        if direction is not MonotonicDirection.NONE and slug in unordered:
            raise GbmFitError(
                "MONOTONE_CONSTRAINT_CONFLICT",
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


def _objective(spec: GbmSpec) -> tuple[str, str, Literal["exp", "logistic"]]:
    """The builtin triple. A custom objective never reaches here — see `_compile_custom`."""
    name = str(spec.objective.name)
    if name not in _OBJECTIVES:
        raise GbmFitError(
            "OBJECTIVE_NOT_APPLICABLE",
            f"objective {name!r} is outside FR-MODEL-26's set "
            f"({', '.join(sorted(_OBJECTIVES))}).",
            terms=[name],
        )
    return _OBJECTIVES[name]


def _is_custom_metric_ref(name: str, eval_metrics: Sequence[GbmFunctionRef]) -> bool:
    """Whether `name` is one of the spec's own declared `kind: custom` eval metrics.

    Early stopping is only allowed to target a metric the spec itself declares
    (FR-MODEL-107) — a ref that merely happens to exist in the caller's `metrics` mapping
    but is not named in `eval_metrics` is not a documented stopping target, and the spec
    (not the caller's mapping) is what `spec_hash` and the model document both report.
    """
    return any(ref.kind == "custom" and str(ref.ref) == name for ref in eval_metrics)


def _builtin_eval_metric_names(eval_metrics: Sequence[GbmFunctionRef]) -> list[str]:
    """The `kind: builtin` entries of `eval_metrics`, spec order, as plain names."""
    return [str(ref.name) for ref in eval_metrics if ref.kind == "builtin" and ref.name]


def _resolve_metrics(
    spec: GbmSpec, metrics: Mapping[str, CustomMetric] | None
) -> dict[str, CustomMetric]:
    """Validate every `kind: custom` entry of `spec.eval_metrics` against `metrics`.

    Mirrors `_compile_custom`'s checks against the objective: the artifact is **passed
    in**, never looked up (ADR-0001), so an absent ref is the caller's bug, not a lookup
    failure to retry. Keyed by ref, so a fit can honour more than one custom eval metric.
    """
    supplied = metrics or {}
    resolved: dict[str, CustomMetric] = {}
    for ref in spec.eval_metrics:
        if ref.kind != "custom":
            continue
        name = str(ref.ref)
        metric = supplied.get(name)
        if metric is None:
            raise GbmFitError(
                "METRIC_REF_UNRESOLVED",
                f"the spec names Custom Metric {name!r} in `eval_metrics` and no artifact "
                "was passed. `pricing-core` does not read the metric store (ADR-0001); "
                "the caller that resolved the reference must hand the artifact to the fit.",
                terms=[name],
            )
        response = spec.response
        if response is None or response not in metric.applicability.responses:
            allowed = ", ".join(sorted(r.value for r in metric.applicability.responses))
            raise GbmFitError(
                "METRIC_NOT_APPLICABLE",
                f"Custom Metric {name!r} declares applicability to {allowed} and the spec "
                f"models {response.value if response else 'no declared response'} "
                "(FR-MODEL-106).",
                terms=[name],
            )
        backend = ObjectiveBackend(spec.model_type)
        if backend not in metric.applicability.backends:
            allowed = ", ".join(sorted(b.value for b in metric.applicability.backends))
            raise GbmFitError(
                "METRIC_NOT_APPLICABLE",
                f"Custom Metric {name!r} declares applicability to {allowed} and the spec "
                f"fits on {spec.model_type} (FR-MODEL-106).",
                terms=[name],
            )
        if metric.status not in FITTABLE_METRIC_STATUSES:
            raise GbmFitError(
                "METRIC_NOT_FITTABLE",
                f"Custom Metric {name!r} is {metric.status.value} (FR-MODEL-45, "
                f"FR-MODEL-106). A fit may use one that is "
                f"{' or '.join(sorted(s.value for s in FITTABLE_METRIC_STATUSES))}.",
                terms=[name],
            )
        resolved[name] = metric
    return resolved


def _compile_custom(spec: GbmSpec, objective: CustomObjective | None) -> ObjectiveFns | None:
    """Resolve `spec.objective` to compiled functions, or `None` for a builtin.

    The artifact is **passed in**, never looked up: ADR-0001 keeps `pricing-core` free of
    the store the objective lives in, so the caller that read the row is the caller that
    supplies it. The checks here are the ones a mismatch would otherwise turn into a fit
    against the wrong loss.
    """
    if spec.objective.kind != "custom":
        if objective is not None:
            raise GbmFitError(
                "OBJECTIVE_NOT_APPLICABLE",
                f"a Custom Objective ({objective.slug}@{objective.version}) was supplied "
                f"for a spec whose objective is the builtin {spec.objective.name!r}. One "
                "of the two would be silently ignored, and the artifact would not say "
                "which.",
                terms=[str(spec.objective.name)],
            )
        return None

    ref = str(spec.objective.ref)
    if objective is None:
        raise GbmFitError(
            "OBJECTIVE_NOT_SUPPLIED",
            f"the spec names Custom Objective {ref!r} and no artifact was passed. "
            "`pricing-core` does not read the objective store (ADR-0001); the caller that "
            "resolved the reference must hand the artifact to the fit.",
            terms=[ref],
        )
    if f"custom_objective:{objective.slug}@{objective.version}" != ref:
        raise GbmFitError(
            "OBJECTIVE_REF_MISMATCH",
            f"the spec names {ref!r} and the artifact supplied is "
            f"custom_objective:{objective.slug}@{objective.version}. A model fitted under "
            "a loss its own spec does not name cannot be reproduced from the spec.",
            terms=[ref],
        )
    if objective.status not in FITTABLE_OBJECTIVE_STATUSES:
        raise GbmFitError(
            "OBJECTIVE_NOT_APPROVED",
            f"Custom Objective {ref!r} is {objective.status.value} (`02` R4, FR-MODEL-46). "
            f"A fit may use one that is "
            f"{' or '.join(sorted(s.value for s in FITTABLE_OBJECTIVE_STATUSES))}.",
            terms=[ref],
        )
    if spec.response is None:
        raise GbmFitError(
            "OBJECTIVE_RESPONSE_UNDECLARED",
            f"the spec names Custom Objective {ref!r} and declares no `response` "
            "(FR-MODEL-44). A builtin objective names its own family; a custom one does "
            "not, so the response is what the applicability check and the diagnostics "
            "deviance are both read from, and neither may be guessed.",
            terms=[ref],
        )
    if spec.response not in objective.applicability.responses:
        allowed = ", ".join(sorted(r.value for r in objective.applicability.responses))
        raise GbmFitError(
            "OBJECTIVE_NOT_APPLICABLE",
            f"Custom Objective {ref!r} declares applicability to {allowed} and the spec "
            f"models {spec.response.value} (FR-MODEL-44).",
            terms=[ref],
        )
    backend = ObjectiveBackend(spec.model_type)
    if backend not in objective.applicability.backends:
        allowed = ", ".join(sorted(b.value for b in objective.applicability.backends))
        raise GbmFitError(
            "OBJECTIVE_NOT_APPLICABLE",
            f"Custom Objective {ref!r} declares applicability to {allowed} and the spec "
            f"fits on {spec.model_type} (FR-MODEL-44).",
            terms=[ref],
        )
    if objective.applicability.offset_required and spec.offset.kind == "none":
        raise GbmFitError(
            "OBJECTIVE_REQUIRES_OFFSET",
            f"Custom Objective {ref!r} requires an offset and the spec declares none "
            "(FR-MODEL-27/44). Fitted without one it models claims per record rather than "
            "claims per year, which converges and prices wrongly.",
            terms=[ref],
        )
    if spec.early_stopping is not None and not _is_custom_metric_ref(
        spec.early_stopping.metric, spec.eval_metrics
    ):
        raise GbmFitError(
            "OBJECTIVE_EARLY_STOPPING_UNSUPPORTED",
            f"the spec pairs Custom Objective {ref!r} with early stopping on the builtin "
            f"metric {spec.early_stopping.metric!r}. Under a callable objective both "
            "backends hand a builtin metric the **raw score** rather than the transformed "
            "prediction, so the metric it stops on is not the metric it names. Custom "
            "eval metrics (FR-MODEL-45) are the answer, and are now built: declare a "
            "Custom Metric in `eval_metrics` and stop on that instead (FR-MODEL-107).",
            terms=[ref, str(spec.early_stopping.metric)],
        )
    try:
        return compile_objective(objective)
    except ObjectiveError as error:
        raise GbmFitError(error.code, str(error), terms=[ref]) from error


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
    objective: CustomObjective | None = None,
    metrics: Mapping[str, CustomMetric] | None = None,
    progress: ProgressCallback | None = None,
) -> GbmFit:
    """Fit `spec` over `data`, returning the artifact and the booster bytes.

    `holdout` is required when `spec.early_stopping.on == "holdout"`. `GbmSpec` refuses a
    stopping rule with no `split_ref`; this refuses a caller that declared the split and
    then passed no rows, because the backends fall back to the training set — FR-MODEL-30's
    prohibition, reached by omission rather than by asking for it.

    `metrics` is `spec.eval_metrics`'s `kind: custom` entries, resolved by the caller and
    keyed by ref — the same ADR-0001 split `objective` already follows (§0, FR-MODEL-106).
    """
    report = progress or NullProgress()
    report.check_cancelled()
    report.update(0.05, "resolving factors")
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)

    report.update(0.15, "encoding features")
    x, order, dtypes, encodings, unordered = _encode(matrix, factors, bandings=bandings)
    constraints = _monotone(factors, order, unordered)
    base_margin = _offset(data, spec.offset, what="this fit")
    weights = _weights(data, spec.weight)

    response = data[spec.response_column].cast(pl.Float64).to_numpy()
    response = apply_loss_treatment(response, spec.loss_treatment)

    fns = _compile_custom(spec, objective)
    resolved_metrics = _resolve_metrics(spec, metrics)
    xgb_objective: str | XgbObjective
    lgb_objective: str | LgbObjective
    if fns is None:
        xgb_objective, lgb_objective, link = _objective(spec)
    else:
        xgb_objective, lgb_objective = make_xgb_objective(fns), make_lgb_objective(fns)
        link = fns.inverse_link
    # Who applies `g^-1` — the single fact `predict_gbm` cannot work out for itself, since
    # by then the objective is a string in a spec nobody kept. XGBoost transforms in
    # `predict` under a builtin objective and cannot under a callable one, having been
    # handed gradients and no link; LightGBM is always asked for the raw score, because
    # FR-MODEL-72's offset has to be added before the transform rather than after it.
    inverse_link: Literal["exp", "logistic"] | None = (
        None if spec.model_type == "xgboost" and fns is None else link
    )
    # `feval`/`custom_metric` see the **same** transform-or-not split as `predict` does at
    # fit time, for *both* backends: a builtin (string) objective means the backend hands
    # the callback its own transformed prediction, a callable one means it hands the raw
    # score untouched (`_to_raw`'s docstring has the evidence). `metric_link` is `None`
    # exactly when the callback already sees the raw score.
    metric_link: Literal["exp", "logistic"] | None = link if fns is None else None
    rounds = int(spec.hyperparameters.get("num_boost_round", 100))
    stopping = spec.early_stopping
    if stopping is not None and stopping.on == "holdout" and holdout is None:
        raise GbmFitError(
            "EARLY_STOPPING_REQUIRES_HOLDOUT",
            "early stopping is declared on a holdout and no holdout frame was passed "
            "(FR-MODEL-30). Without one the backend evaluates on the training rows, which "
            "is the training-set early stopping the requirement forbids.",
        )

    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None = None
    if holdout is not None:
        holdout_matrix = resolve_factors(holdout, factors, bandings=bandings, groupings=groupings)
        vx = _encode(holdout_matrix, factors, maps=encodings, bandings=bandings).x
        vy = apply_loss_treatment(
            holdout[spec.response_column].cast(pl.Float64).to_numpy(), spec.loss_treatment
        )
        # The holdout is weighted too, and for the same reason FR-MODEL-54 gives for
        # reporting both partitions: a curve whose train half is weighted and whose holdout
        # half is not is two different quantities plotted on one axis, and the divergence
        # early stopping exists to catch would be read off the difference between the
        # weightings rather than off the model.
        valid = (
            vx, vy, _offset(holdout, spec.offset, what="the holdout"),
            _weights(holdout, spec.weight),
        )

    report.update(0.30, f"boosting {rounds} rounds on {spec.model_type}")
    started = time.perf_counter()
    if spec.model_type == "xgboost":
        payload, best, curve, versions, dropped = _fit_xgboost(
            spec, x, response, base_margin, weights, valid, order, constraints,
            unordered, xgb_objective, rounds, resolved_metrics, metric_link,
        )
    else:
        payload, best, curve, versions, dropped = _fit_lightgbm(
            spec, x, response, base_margin, weights, valid, order, constraints,
            unordered, lgb_objective, rounds, resolved_metrics, metric_link,
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
            inverse_link=inverse_link,
            rows=data.height,
            fit_seconds=elapsed,
            library_versions=versions,
            dropped_eval_metrics=dropped,
        ),
        booster_bytes=payload,
        eval_curve=curve,
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


def _curve(
    history: Mapping[str, Mapping[str, Sequence[float]]],
    *,
    declared: Mapping[str, str] | None = None,
) -> tuple[GbmEvalPoint, ...]:
    """Both partitions on one row per iteration (FR-MODEL-52, FR-MODEL-54).

    The two libraries key their history identically once the eval sets are named, so this
    is shared. `declared` maps a backend-reported key to the name the **spec** spelled it
    with: LightGBM translates a builtin metric name (`_METRICS`) before it ever reaches the
    backend, so what comes back is the translation, and a reviewer looking for the metric
    they asked for should find it rather than LightGBM's name for it. `_lgb_custom_feval`
    reports a custom metric under its own ref directly, so LightGBM never needs an entry
    here for one — but `_xgb_custom_feval` reports it under `_xgb_safe_metric_name(ref)`
    (XGBoost's own eval-log parser breaks on the colon a ref contains), so XGBoost's fit
    passes a `declared` entry translating the sanitised name back to the ref.

    Keyed by backend name rather than a single override string: the previous single
    `declared` string was applied to *every* key found in `history`, which happened to be
    harmless only because history never held more than one metric before FR-MODEL-106.
    """
    mapping = declared or {}
    train = dict(history.get("train", {}))
    holdout = dict(history.get("holdout", {}))
    metrics = list(holdout) or list(train)
    points: list[GbmEvalPoint] = []
    for metric in metrics:
        train_values = list(train.get(metric, []))
        holdout_values = list(holdout.get(metric, []))
        for index in range(max(len(train_values), len(holdout_values))):
            points.append(
                GbmEvalPoint(
                    iteration=index,
                    metric=mapping.get(metric, metric),
                    train=train_values[index] if index < len(train_values) else None,
                    holdout=holdout_values[index] if index < len(holdout_values) else None,
                )
            )
    return tuple(points)


def _xgb_safe_metric_name(ref: str) -> str:
    """A Custom Metric ref through XGBoost's own eval-log round trip.

    `xgb.callback.EarlyStopping.after_iteration` gets the round's scores as a formatted
    string (`"[i]\tname:value\tname:value"`) and re-parses it by splitting each entry on
    a single `":"` — a convention baked into `xgboost.core._parse_eval_str`, not something
    this module controls. A Custom Metric ref such as `custom_metric:poisson-nll@1` is
    `kind:slug@version` and already contains a colon, which breaks that split with "too
    many values to unpack" the moment a name reaches XGBoost's own log line. The ref is
    still what the spec, `_resolve_metrics` and `evaluate_metric` use everywhere else;
    only the string handed to XGBoost is sanitised, and `_curve`'s `declared` map
    translates it back for the caller.
    """
    return ref.replace(":", "__")


def _xgb_custom_feval(
    entries: Mapping[str, CustomMetric], *, link: Literal["exp", "logistic"] | None
) -> XgbFeval:
    """Reports each entry under `_xgb_safe_metric_name(ref)`, not the ref itself.

    `link` is `None` exactly when `preds` already arrives as the raw score (a callable
    objective); otherwise it is the builtin objective's own link, and `_to_raw` inverts
    XGBoost's `output_margin=callable(obj)` transform before `evaluate_metric` sees it.
    """

    def feval(preds: np.ndarray, dmatrix: Any) -> list[tuple[str, float]]:
        y = dmatrix.get_label()
        weight = dmatrix.get_weight()
        w = weight if weight.size else np.ones_like(y)
        raw = preds if link is None else _to_raw(preds, link)
        return [
            (_xgb_safe_metric_name(name), evaluate_metric(metric, y, raw, w))
            for name, metric in entries.items()
        ]

    return feval


def _fit_xgboost(
    spec: GbmSpec,
    x: np.ndarray,
    y: np.ndarray,
    base_margin: np.ndarray | None,
    weights: np.ndarray | None,
    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None,
    order: Sequence[str],
    constraints: tuple[int, ...],
    categorical: frozenset[str],
    objective: str | XgbObjective,
    rounds: int,
    custom_metrics: Mapping[str, CustomMetric],
    metric_link: Literal["exp", "logistic"] | None,
) -> tuple[bytes, int, tuple[GbmEvalPoint, ...], dict[str, str], tuple[DroppedEvalMetric, ...]]:
    import xgboost as xgb

    feature_types = ["c" if slug in categorical else "q" for slug in order]
    custom = not isinstance(objective, str)
    params: dict[str, Any] = {
        # A callable is `train(obj=...)`, not a parameter — XGBoost reads `params` into its
        # C++ configuration and a Python function is not a value it can take. With one,
        # `base_score` must be pinned: 3.x estimates it from the label under an objective
        # it no longer knows the link of, and a wrong intercept under a log link is a
        # multiplicative error on every prediction.
        **({"base_score": 0.0} if custom else {"objective": objective}),
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

    def matrix(
        features: np.ndarray, label: np.ndarray, margin: np.ndarray | None,
        weight: np.ndarray | None,
    ) -> Any:
        return xgb.DMatrix(
            features, label=label, base_margin=margin, weight=weight,
            feature_names=list(order), feature_types=feature_types, enable_categorical=True,
        )

    dtrain = matrix(x, y, base_margin, weights)
    evals: list[tuple[Any, str]] = []
    if valid is not None:
        # Train **and** holdout: FR-MODEL-52 asks for the curve on both, and FR-MODEL-54
        # calls a diagnostic reported without its holdout counterpart a defect — which
        # reads the same way round. A curve on one partition cannot show the divergence
        # that early stopping exists to catch.
        evals = [
            (dtrain, "train"),
            (matrix(valid[0], valid[1], valid[2], valid[3]), "holdout"),
        ]
    stopping = spec.early_stopping
    stopping_on_custom = stopping is not None and _is_custom_metric_ref(
        stopping.metric, spec.eval_metrics
    )
    builtin_names = _builtin_eval_metric_names(spec.eval_metrics)
    if stopping is not None and not stopping_on_custom and stopping.metric not in builtin_names:
        builtin_names = [*builtin_names, str(stopping.metric)]
    if builtin_names:
        params["eval_metric"] = builtin_names if len(builtin_names) > 1 else builtin_names[0]
    elif custom_metrics:
        # Setting `eval_metric` explicitly is what stops XGBoost adding its own implicit
        # default (e.g. "rmse", picked for a callable objective it cannot introspect) — with
        # only custom eval_metrics declared, `eval_metric` is never set, so the default would
        # otherwise leak into the curve alongside metrics the spec never asked for.
        params["disable_default_eval_metric"] = 1

    custom_metric_fn = (
        _xgb_custom_feval(custom_metrics, link=metric_link) if custom_metrics else None
    )

    # A named metric_name/data_name callback rather than the `early_stopping_rounds=`
    # shorthand, **on both branches**: the shorthand auto-picks the *last* eval set and the
    # *last* eval_metric in insertion order, which is exactly ambiguous once a custom metric
    # is also being reported (FR-MODEL-106/107) — explicit targeting has no such ambiguity
    # to resolve.
    #
    # The builtin branch used the shorthand until 2026-08-20, and the ambiguity was not
    # theoretical: `EarlyStopping.after_iteration` takes `list(data_log.keys())[-1]`, and
    # XGBoost appends custom-metric results *after* the builtin ones. A spec naming
    # `poisson-nloglik` with any Custom Metric also declared therefore stopped on the
    # custom metric, minimising it whatever direction it declared. FR-MODEL-104's stated
    # failure verbatim: the fit stops at the wrong round and produces a model, not an error.
    callbacks: list[Any] = []
    if stopping is not None and evals:
        if stopping_on_custom:
            target_name = _xgb_safe_metric_name(stopping.metric)
            # `MetricDirection` is the artifact's own declaration and `certify_metric`'s
            # `direction_holds` check is what stands behind it — XGBoost has never heard of
            # this metric and cannot infer which way is better.
            maximize: bool | None = (
                custom_metrics[stopping.metric].direction is MetricDirection.HIGHER_IS_BETTER
            )
        else:
            target_name = str(stopping.metric)
            # `maximize=None` for a **backend** metric is delegation, not a guess: XGBoost
            # keeps the higher-is-better set for its own vocabulary (`auc`, `aucpr`, `map`,
            # `ndcg`, `pre`, …) and `_METRICS`'s docstring makes an unrecognised name
            # backend-specific by design, so a direction table maintained in this file
            # would go stale silently against metrics it has never heard of.
            maximize = None
        callbacks.append(
            xgb.callback.EarlyStopping(
                rounds=stopping.rounds,
                metric_name=target_name,
                data_name="holdout",
                maximize=maximize,
                save_best=False,
            )
        )

    history: dict[str, dict[str, list[float]]] = {}
    booster = xgb.train(
        params, dtrain, num_boost_round=rounds, evals=evals, evals_result=history,
        obj=None if isinstance(objective, str) else objective,
        custom_metric=custom_metric_fn,
        callbacks=callbacks or None,
        verbose_eval=False,
    )
    best = int(getattr(booster, "best_iteration", rounds - 1))
    # `_xgb_custom_feval` reports each custom metric under its sanitised name (see
    # `_xgb_safe_metric_name`); translate it back to the ref the spec and caller know.
    custom_declared = {_xgb_safe_metric_name(ref): ref for ref in custom_metrics}
    curve = _curve(history, declared=custom_declared or None)
    payload = bytes(booster.save_raw(raw_format="json"))
    # Nothing is ever dropped here: `eval_metric` takes the whole builtin list and
    # `custom_metric` runs beside it, so XGBoost evaluates both (FR-MODEL-111).
    return payload, best + 1, curve, {"xgboost": xgb.__version__}, ()


def _lgb_custom_feval(
    entries: Mapping[str, CustomMetric], *, link: Literal["exp", "logistic"] | None
) -> LgbFeval:
    """LightGBM's counterpart to `_xgb_custom_feval` — direction rides in the tuple."""

    def feval(preds: np.ndarray, dataset: Any) -> list[tuple[str, float, bool]]:
        y = dataset.get_label()
        weight = dataset.get_weight()
        w = weight if weight is not None and len(weight) else np.ones_like(y)
        raw = preds if link is None else _to_raw(preds, link)
        return [
            (name, evaluate_metric(metric, y, raw, w),
             metric.direction is MetricDirection.HIGHER_IS_BETTER)
            for name, metric in entries.items()
        ]

    return feval


def _fit_lightgbm(
    spec: GbmSpec,
    x: np.ndarray,
    y: np.ndarray,
    base_margin: np.ndarray | None,
    weights: np.ndarray | None,
    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None,
    order: Sequence[str],
    constraints: tuple[int, ...],
    categorical: frozenset[str],
    objective: str | LgbObjective,
    rounds: int,
    custom_metrics: Mapping[str, CustomMetric],
    metric_link: Literal["exp", "logistic"] | None,
) -> tuple[bytes, int, tuple[GbmEvalPoint, ...], dict[str, str], tuple[DroppedEvalMetric, ...]]:
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
    stopping_on_custom = stopping is not None and _is_custom_metric_ref(
        stopping.metric, spec.eval_metrics
    )
    declared_map: dict[str, str] = {}
    feval_entries: dict[str, CustomMetric] = {}
    dropped: tuple[DroppedEvalMetric, ...] = ()
    # LightGBM's early-stopping callback can only target "the first metric"
    # (`first_metric_only`), never one by name — but "first" is decided purely by the
    # evaluation ordering (confirmed by reading `_EarlyStoppingCallback._init`:
    # `self.first_metric = env.evaluation_result_list[0].metric_name`, and that list's
    # metric ordering, per dataset, is builtin `params["metric"]` entries followed by
    # `feval`'s in the order it returns them). So the target is bound by **arranging the
    # ordering** — stopping's metric first, on whichever of the two lists it lives in —
    # and then narrowing the callback to that first metric. Nothing is dropped from the
    # curve; only the order is chosen.
    if stopping_on_custom:
        assert stopping is not None  # narrowed by stopping_on_custom
        # `metric: None` suppresses LightGBM's own implicit default so no unrequested
        # metric can land at position 0. It also means a **builtin** entry of
        # `eval_metrics` is not reported alongside a custom stopping target: builtins are
        # always evaluated before `feval`, so one would take position 0 and drive the stop
        # instead. That is a library limitation rather than a choice, and the alternative —
        # report the builtin and stop on the wrong metric — is the defect this whole
        # section exists to prevent. Pinned by
        # `test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it`.
        params["metric"] = "None"
        # FR-MODEL-111: the builtins suppressed by the line above were *declared*, and a
        # caller who cannot see them in the curve is owed the reason rather than left to
        # infer one. The same list the `else` arm passes to `params["metric"]`.
        dropped = tuple(
            DroppedEvalMetric(
                name=name, reason="builtin_evaluated_before_custom_stopping_metric"
            )
            for name in _builtin_eval_metric_names(spec.eval_metrics)
        )
        feval_entries = {
            stopping.metric: custom_metrics[stopping.metric],
            **{ref: metric for ref, metric in custom_metrics.items() if ref != stopping.metric},
        }
    else:
        builtin_names = _builtin_eval_metric_names(spec.eval_metrics)
        if stopping is not None and str(stopping.metric) not in builtin_names:
            builtin_names = [*builtin_names, str(stopping.metric)]
        if stopping is not None:
            # Stopping's target first. Before 2026-08-20 the spec's declaration order was
            # kept and `first_metric_only` was left False whenever no custom metric was
            # declared, on the premise that "with none declared there is exactly one metric
            # and nothing to disambiguate" — which FR-MODEL-106 had already falsified by
            # letting `eval_metrics` put builtins in `params["metric"]` beside the stopping
            # one. LightGBM then halted as soon as *any* of them stalled.
            target = str(stopping.metric)
            builtin_names = [target, *(name for name in builtin_names if name != target)]
        if builtin_names:
            translated = [_METRICS.get(name, name) for name in builtin_names]
            params["metric"] = translated if len(translated) > 1 else translated[0]
            declared_map = dict(zip(translated, builtin_names, strict=True))
        feval_entries = dict(custom_metrics)

    custom_metric_fn = _lgb_custom_feval(feval_entries, link=metric_link) if feval_entries else None

    train_set = lgb.Dataset(
        x, label=y, init_score=base_margin, weight=weights, feature_name=list(order),
        categorical_feature=categorical_indices, free_raw_data=False,
    )
    callbacks: list[Any] = []
    history: dict[str, dict[str, list[float]]] = {}
    valid_sets: list[Any] = []
    valid_names: list[str] = []
    if valid is not None:
        valid_sets = [
            train_set,
            lgb.Dataset(valid[0], label=valid[1], init_score=valid[2], weight=valid[3],
                        reference=train_set, feature_name=list(order),
                        categorical_feature=categorical_indices, free_raw_data=False),
        ]
        valid_names = ["train", "holdout"]
        callbacks.append(lgb.record_evaluation(history))
        if stopping is not None:
            callbacks.append(
                lgb.early_stopping(
                    stopping.rounds, verbose=False,
                    # Always narrowed, because the ordering above has already put the
                    # spec's stopping metric first. Left False, LightGBM halts as soon as
                    # *any* registered metric stalls — which is a different rule from the
                    # one the spec states, and silently a stricter one.
                    first_metric_only=True,
                )
            )

    booster = lgb.train(
        params, train_set, num_boost_round=rounds, valid_sets=valid_sets,
        valid_names=valid_names or None, feval=custom_metric_fn, callbacks=callbacks,
    )
    best = int(booster.best_iteration or rounds)
    curve = _curve(history, declared=declared_map)
    payload = booster.model_to_string(num_iteration=best).encode()
    return payload, best, curve, {"lightgbm": lgb.__version__}, dropped


def _native_categoricals(result: GbmFitResult) -> frozenset[str]:
    """The fitted features the backend was told are categorical (FR-MODEL-31's dtypes).

    Scoring has to declare exactly what fitting declared: XGBoost splits a `c` feature by
    set membership and a `q` feature by threshold, so a band scored as `c` reads a booster
    that was grown as `q`. The encoding maps alone cannot answer this — a banding has one
    and is ordinal — which is what `feature_dtypes` is for.

    A result carrying maps and no dtypes falls back to "every encoded feature is
    categorical", which is what this module did before bandings became ordinal. `fit_gbm`
    always populates dtypes, so the fallback is for a hand-assembled result rather than for
    anything the platform has fitted.
    """
    if not result.feature_dtypes:
        return frozenset(result.categorical_maps)
    return frozenset(slug for slug, dtype in result.feature_dtypes.items() if dtype == "cat")


def _apply_inverse_link(raw: np.ndarray, link: Literal["exp", "logistic"]) -> np.ndarray:
    """`g^-1`, on the one side of the boundary that knows which one it is.

    Written out rather than left as an `np.exp` because three of the four builtin
    objectives are log-link and the fourth is not: `binary:logistic` under LightGBM was
    exponentiated here until 2026-08-18, which returns `exp(f)` where the model means
    `1 / (1 + exp(-f))` — the same number nowhere, and both plausible probabilities near
    `f = 0`.
    """
    if link == "logistic":
        return np.asarray(1.0 / (1.0 + np.exp(-raw)), dtype=np.float64)
    return np.asarray(np.exp(raw), dtype=np.float64)


def _to_raw(predicted: np.ndarray, link: Literal["exp", "logistic"]) -> np.ndarray:
    """`g`, the inverse of `_apply_inverse_link` — FR-MODEL-107's other half.

    Both backends hand `feval`/`custom_metric` the **transformed** prediction under a
    builtin (string) objective and the **raw score** under a callable one — confirmed by
    reading `xgboost.training.train`'s `output_margin=callable(obj)` and, for LightGBM,
    empirically. `evaluate_metric` is written against the raw score by construction
    (`pricing_core.modelling.metrics`), so a custom eval metric paired with a *builtin*
    objective needs this inversion to see the same quantity it would under a custom one —
    the metric's value must not depend on which objective happens to be fitting it.
    """
    if link == "logistic":
        clipped = np.clip(predicted, 1e-12, 1.0 - 1e-12)
        return np.asarray(np.log(clipped / (1.0 - clipped)), dtype=np.float64)
    return np.asarray(np.log(np.clip(predicted, 1e-12, None)), dtype=np.float64)


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
        x, order, *_ = _encode(
            matrix, factors, maps=result.categorical_maps, bandings=bandings
        )
    else:
        missing = [slug for slug in result.feature_order if slug not in data.columns]
        if missing:
            raise GbmFitError(
                "SCORING_FEATURES_MISMATCH",
                f"the frame does not carry {missing}. Pass the model's factors to have "
                "them resolved, or supply each feature under its factor slug.",
                terms=missing,
            )
        x, order, *_ = _encode(
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
            "SCORING_FEATURES_MISMATCH",
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
            feature_types=["c" if slug in _native_categoricals(result) else "q"
                           for slug in result.feature_order],
            enable_categorical=True,
        )
        values = np.asarray(
            loaded.predict(frame, iteration_range=(0, result.best_iteration)),
            dtype=np.float64,
        )
        # A builtin objective leaves `inverse_link` unset and `predict` has already
        # transformed; a custom one was a callable, so the booster holds gradients and no
        # link and this is the raw margin.
        if result.inverse_link is not None:
            values = _apply_inverse_link(values, result.inverse_link)
    else:
        import lightgbm as lgb

        lgb_booster = lgb.Booster(model_str=booster.decode())
        raw = np.asarray(lgb_booster.predict(x, raw_score=True), dtype=np.float64)
        if margin is not None:
            raw = raw + margin
        # `or "exp"` is the fallback for an artifact fitted before `inverse_link` existed,
        # when this line was an unconditional `np.exp` — which is what those artifacts have
        # always been scored with, correctly for three of the four objectives. See the
        # dated note at `02` §4.3.
        values = _apply_inverse_link(raw, result.inverse_link or "exp")

    return pl.Series("prediction", values)


#: FR-MODEL-26's objectives as the exponential-dispersion families the deviance functions
#: already know. The pair is what `unit_deviance` takes; the power is Tweedie's and is
#: ignored elsewhere.
_FAMILIES: Final[dict[str, tuple[str, float]]] = {
    "count:poisson": ("poisson", 1.5),
    "reg:gamma": ("gamma", 1.5),
    "reg:tweedie": ("tweedie", 1.5),
    "binary:logistic": ("binomial", 1.5),
}


#: The deviance a **response** is measured under, for a spec whose objective does not name
#: one. `CLAUDE.md` §7's actuarial defaults, and deliberately the response rather than the
#: loss: a severity model fitted under `capped_gamma` or `huber` is still a severity model,
#: and its A/E is compared against gamma-fitted ones. The loss is how it was fitted; the
#: family is how it is measured, and a custom objective is precisely the case where those
#: two stop being the same question.
_RESPONSE_FAMILIES: Final[dict[ResponseKind, tuple[str, float]]] = {
    ResponseKind.CLAIM_COUNT: ("poisson", 1.5),
    ResponseKind.CLAIM_SEVERITY: ("gamma", 1.5),
    ResponseKind.BURNING_COST: ("tweedie", 1.5),
    ResponseKind.CONVERSION: ("binomial", 1.5),
    ResponseKind.RETENTION: ("binomial", 1.5),
}


def objective_family(spec: GbmSpec) -> tuple[str, float]:
    """The family and Tweedie power implied by a GBM's objective.

    A GBM spec has no `family` field — a builtin objective *is* the family, spelled the
    backend's way. Diagnostics need it in the deviance functions' vocabulary, and deriving
    it here keeps the mapping in one place rather than beside every caller.

    A **Custom Objective names no family**, and the artifact that would is not in scope
    here (ADR-0001: this function takes a spec, not a store). `spec.response` is what
    carries the answer, which is why `_compile_custom` refuses to fit a custom objective
    on a spec that leaves it unset — the alternative is a `capped_gamma` severity model
    whose A/E was computed as a Poisson deviance, reported without comment.
    """
    if spec.objective.kind == "custom":
        if spec.response is None:  # pragma: no cover — `_compile_custom` refuses first
            raise GbmFitError(
                "OBJECTIVE_RESPONSE_UNDECLARED",
                f"objective {spec.objective.ref!r} is custom and the spec declares no "
                "`response`, so the deviance its diagnostics would be measured under is "
                "not determined.",
                terms=[str(spec.objective.ref)],
            )
        family, default_power = _RESPONSE_FAMILIES[spec.response]
    else:
        family, default_power = _FAMILIES.get(str(spec.objective.name), ("poisson", 1.5))
    power = float(spec.hyperparameters.get("tweedie_variance_power", default_power))
    return family, power


def tree_summary(result: GbmFitResult, booster: bytes) -> tuple[int, int, float, int]:
    """`(tree_count, max_depth, mean_depth, leaf_count)` from the persisted booster.

    Read from the artifact rather than from a live estimator, because that is what a
    reviewer will have: the diagnostics are computed once (FR-MODEL-49) and everything
    afterwards reads the stored bytes.

    `leaf_count` is what `ComplexityDiagnostic.parameter_count` means for a boosted model.
    A GBM has no coefficient vector, and counting factors instead would report the same
    complexity for a stump and for a thousand deep trees — which is the comparison
    FR-MODEL-81's exposure-per-parameter exists to make.
    """
    depths: list[int] = []
    leaves = 0

    if result.model_type == "xgboost":
        import json

        import xgboost as xgb

        loaded = xgb.Booster()
        loaded.load_model(bytearray(booster))
        dumps = loaded.get_dump(dump_format="json")[: result.best_iteration]

        def walk_xgb(node: dict[str, Any], depth: int) -> None:
            nonlocal leaves
            children = node.get("children")
            if not children:
                leaves += 1
                depths.append(depth)
                return
            for child in children:
                walk_xgb(child, depth + 1)

        for tree in dumps:
            walk_xgb(json.loads(tree), 0)
        count = len(dumps)
    else:
        import lightgbm as lgb

        loaded_lgb = lgb.Booster(model_str=booster.decode())
        model = loaded_lgb.dump_model()

        def walk_lgb(node: dict[str, Any], depth: int) -> None:
            nonlocal leaves
            if "leaf_value" in node and "left_child" not in node:
                leaves += 1
                depths.append(depth)
                return
            for key in ("left_child", "right_child"):
                if key in node:
                    walk_lgb(node[key], depth + 1)

        trees = model.get("tree_info", [])
        for tree in trees:
            walk_lgb(tree["tree_structure"], 0)
        count = len(trees)

    if not depths:
        return count, 0, 0.0, 0
    return count, max(depths), sum(depths) / len(depths), leaves
