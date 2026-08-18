"""Scoring a fitted Model over rows a caller supplies (`02` FR-MODEL-62/63/77/93, §5.1).

**Dev/debug scale, and the cap is the specification.** §5.1 scopes `/predict` to "dev/debug
scale; production scoring is `03`", and a limit stated in prose is a limit nobody enforces —
so `MAX_PREDICT_ROWS` is where that sentence becomes a `422`. It also makes the endpoint's
one expensive property affordable: FR-MODEL-63's interval materialises the `n x p` design,
which the streaming scorers deliberately never do.

`pricing-core` owns the arithmetic. What lives here is everything ADR-0001 keeps out of it —
resolving the model, its factors and their bandings and groupings from ids, and fetching the
blobs (the booster, the covariance matrix) that the artifacts only reference.

**The uncertainty verdict is decided here, once, per model.** A GLM fitted before the
covariance blob existed reports `covariance_not_stored` (FR-MODEL-93); a GBM reports
FR-MODEL-77's `no_interval_models_fitted`, which is the only one of its three reasons that
can be true while FR-MODEL-78's paired quantile models remain unbuilt.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl

from app.db.models import ModelRow
from app.errors import PlatformError
from app.platform import modelling as model_service
from app.platform import rbac
from app.platform import transformations as transform_service
from app.platform.blobs import BlobStore
from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    SCOREABLE_MODEL_STATUSES,
    Banding,
    Factor,
    GbmFitResult,
    GlmFitResult,
    GlmSpec,
    Grouping,
    ModelSpec,
    ModelStatus,
    Permission,
    PredictedRow,
    Prediction,
    Principal,
    UnavailableReason,
    Uncertainty,
    UncertaintyKind,
)

__all__ = ["CONFIDENCE_LEVEL", "MAX_PREDICT_ROWS", "predict_rows"]

#: §5.1's "dev/debug scale", made a number. Chosen so the interval's `n x p` design stays a
#: few megabytes for any factor set a Phase-1 model carries, and so a caller who meant to
#: re-rate a portfolio is told to use `03` rather than quietly served a slow answer.
MAX_PREDICT_ROWS: Final = 1_000

#: Fixed rather than a request parameter, and fixed at the level `Coefficient.ci_95` uses.
#: An interval on a prediction and an interval on the coefficient it came from, reported at
#: two different levels, is a comparison a reader cannot make.
CONFIDENCE_LEVEL: Final = 0.95


async def predict_rows(
    session: Any,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    rows: list[dict[str, Any]],
    blob_store: BlobStore,
) -> Prediction:
    """Score `rows` with model `model_id` (FR-MODEL-62), interval included where there is one.

    `model:read`, not `model:fit`. Every other compute route here is gated on `model:fit`
    because it queues a Job that spends minutes; this one persists nothing, produces no
    artifact, and is bounded by `MAX_PREDICT_ROWS`. Gating it on `model:fit` would mean an
    approver reviewing a model could not ask it what it charges — which is the question an
    approval is *about*.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_READ
    )
    if not rows:
        raise PlatformError(
            "VALIDATION_FAILED",
            "No rows to score",
            422,
            "A prediction request with no rows has no answer. Send at least one.",
        )
    if len(rows) > MAX_PREDICT_ROWS:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Too many rows for this endpoint",
            422,
            f"{len(rows)} rows exceeds the {MAX_PREDICT_ROWS} this endpoint scores. `02` "
            "§5.1 scopes it to dev/debug scale; a portfolio re-rate is `03`'s batch scoring, "
            "which is built for it and records what it produced.",
        )

    model = await session.get(ModelRow, model_id)
    if model is None or model.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Model not found", 404, f"No model {model_id} in this workspace."
        )
    if ModelStatus(model.status) not in SCOREABLE_MODEL_STATUSES or model.fit_result is None:
        raise PlatformError(
            "MODEL_NOT_FITTED",
            "A model with no fit result cannot be scored",
            409,
            f"{model.model_family_slug}@{model.version} is {model.status!r}. There are no "
            "coefficients to score with — fit it first (`02` §4.8: only a model at "
            "`fitted` or beyond carries a fit result).",
        )

    spec = MODEL_SPEC_ADAPTER.validate_python(model.spec)
    fit = FIT_RESULT_ADAPTER.validate_python(model.fit_result)
    factors = await model_service.load_factors(
        session, workspace_id=workspace_id, factor_ids=list(spec.factors)
    )
    bandings = await transform_service.load_bandings(
        session, workspace_id=workspace_id, ids=[f.banding_id for f in factors if f.banding_id]
    )
    groupings = await transform_service.load_groupings(
        session,
        workspace_id=workspace_id,
        ids=[f.grouping_id for f in factors if f.grouping_id],
    )

    try:
        frame = pl.DataFrame(rows)
    except (TypeError, ValueError) as exc:
        # A ragged or mixed-type body is the caller's mistake, and polars states it more
        # precisely than a restatement here would: one row with a string where its
        # neighbours have numbers names the column in the message.
        raise PlatformError(
            "VALIDATION_FAILED",
            "These rows do not form a table",
            422,
            f"{exc} Every row must carry the same columns with compatible types.",
        ) from exc

    if isinstance(fit, GbmFitResult):
        expected, uncertainty = await _score_gbm(
            fit, spec, frame, factors, bandings=bandings, groupings=groupings,
            blob_store=blob_store,
        )
        lower = upper = None
    else:
        assert isinstance(fit, GlmFitResult)
        assert isinstance(spec, GlmSpec)
        expected, lower, upper, uncertainty = await _score_glm(
            fit, spec, frame, factors, bandings=bandings, groupings=groupings,
            blob_store=blob_store,
        )

    return Prediction(
        model_id=model.id,
        model_family_slug=model.model_family_slug,
        version=model.version,
        model_type=spec.model_type,
        uncertainty=uncertainty,
        rows=tuple(
            PredictedRow(
                expected=float(expected[i]),
                lower=None if lower is None else float(lower[i]),
                upper=None if upper is None else float(upper[i]),
            )
            for i in range(frame.height)
        ),
    )


async def _score_glm(
    fit: GlmFitResult,
    spec: GlmSpec,
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
    blob_store: BlobStore,
) -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64] | None,
    npt.NDArray[np.float64] | None,
    Uncertainty,
]:
    """`μ` and FR-MODEL-63's interval, or `μ` and FR-MODEL-93's typed absence.

    **The absence is a property of the stored model, not of the request.** Every GLM fitted
    before the covariance blob existed carries `covariance_blob=None`, and there is no way
    to recover the matrix from the artifact: it is `p x p` and the artifact holds `p`
    numbers. Saying so is the whole of FR-MODEL-93 — the alternative is an interval quietly
    omitted, which `02` R5 exists to forbid, or a refetch of the fit, which would mean
    re-fitting the model to answer a prediction.
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import (
        PredictionError,
        predict_glm,
        predict_glm_interval,
    )

    try:
        if fit.covariance_blob is None:
            return (
                predict_glm(
                    fit, frame, factors, spec, bandings=bandings, groupings=groupings
                ),
                None,
                None,
                Uncertainty(
                    kind=UncertaintyKind.UNAVAILABLE,
                    reason=UnavailableReason.COVARIANCE_NOT_STORED,
                ),
            )
        expected, lower, upper = predict_glm_interval(
            fit,
            frame,
            factors,
            spec,
            covariance_bytes=await blob_store.read(fit.covariance_blob),
            level=CONFIDENCE_LEVEL,
            bandings=bandings,
            groupings=groupings,
        )
    except (ModellingError, PredictionError) as exc:
        raise _unscoreable(exc) from exc
    return (
        expected,
        lower,
        upper,
        Uncertainty(
            kind=UncertaintyKind.CONFIDENCE_INTERVAL_MEAN, level=CONFIDENCE_LEVEL
        ),
    )


async def _score_gbm(
    fit: GbmFitResult,
    spec: ModelSpec,
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
    blob_store: BlobStore,
) -> tuple[npt.NDArray[np.float64], Uncertainty]:
    """`μ` from the booster, and FR-MODEL-77's statement that there is no interval.

    `no_interval_models_fitted` is the only one of FR-MODEL-77's three reasons reachable
    today, and will be until FR-MODEL-78's `interval_for` exists to make a paired quantile
    model findable. The other two are declared in `UnavailableReason` and returned by
    nothing — named there rather than omitted, so the slice that fits one adds a branch
    instead of widening the vocabulary a client already matches on.

    The variance-model approximation FR-MODEL-77 refuses would fit here in four lines. That
    is the reason the requirement is written down: a wrong interval on a price is worse than
    no interval, and its cheapness is what makes refusing it a decision rather than an
    omission.
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import PredictionError, score_fitted

    try:
        expected = score_fitted(
            fit,
            spec,
            frame,
            factors,
            bandings=bandings,
            groupings=groupings,
            booster=await blob_store.read(fit.booster_blob),
        )
    except (ModellingError, PredictionError) as exc:
        raise _unscoreable(exc) from exc
    return expected, Uncertainty(
        kind=UncertaintyKind.UNAVAILABLE,
        reason=UnavailableReason.NO_INTERVAL_MODELS_FITTED,
    )


def _unscoreable(exc: Any) -> PlatformError:
    """`pricing-core` names the failure; the platform gives it the HTTP shape.

    409 rather than 422: the request is well formed and the model is real, and what fails is
    the pairing of the two — a column the model needs that these rows do not carry. The fit
    path draws the same line for the same error type.

    **Both hierarchies, not only `PredictionError`.** Scoring resolves the factors before it
    predicts anything, so the commonest failure here — rows missing a column the model was
    fitted on — arrives as `FactorResolutionError`, a sibling of `PredictionError` rather
    than a subclass. Catching only the latter turned the single most likely caller mistake
    into a 500 with the column name buried in a traceback.
    """
    return PlatformError(
        exc.code, "These rows cannot be scored with this model", 409, str(exc)
    )
