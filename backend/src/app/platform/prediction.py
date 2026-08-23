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
covariance blob existed reports `covariance_not_stored` (FR-MODEL-93). A GBM reports
FR-MODEL-78's paired-quantile interval where a complete, current, sufficiently-reviewed
pair exists, and otherwise one of FR-MODEL-77's three reasons — all of which became
reachable with the paired-quantile slice (FR-MODEL-100), where before it could only ever
say `no_interval_models_fitted`.
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
    EbmFitResult,
    EbmSpec,
    Factor,
    FitResult,
    GbmFitResult,
    GbmSpec,
    GlmFitResult,
    GlmSpec,
    Grouping,
    IntervalModels,
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

    if isinstance(spec, GbmSpec) and isinstance(fit, GbmFitResult):
        expected, lower, upper, uncertainty = await _score_gbm(
            session, fit, spec, frame, factors, workspace_id=workspace_id, model=model,
            bandings=bandings, groupings=groupings, blob_store=blob_store,
        )
    elif isinstance(spec, EbmSpec):
        expected, lower, upper, uncertainty = await _score_ebm(
            fit,
            frame,
            factors,
            bandings=bandings,
            groupings=groupings,
        )
    else:
        assert isinstance(fit, GlmFitResult)
        assert isinstance(spec, GlmSpec)
        expected, lower, upper, uncertainty = await _score_glm(
            session, fit, spec, frame, factors, workspace_id=workspace_id,
            bandings=bandings, groupings=groupings, blob_store=blob_store,
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
    session: Any,
    fit: GlmFitResult,
    spec: GlmSpec,
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    workspace_id: UUID,
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

    **A model-offset spec is resolved per request** (FR-MODEL-24): the referenced model is
    looked up and its linear predictor computed on these rows, because the offset is a
    property of the model the request names, not of a stored array. The resolution is on
    the loop and the η arithmetic is pricing-core's — the split every fit makes, kept
    here so the two failure shapes stay distinct: a ref that names nothing is a `404`, and
    rows the maths cannot score are the `409` `_unscoreable` gives them.
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import (
        PredictionError,
        linear_predictor,
        predict_glm,
        predict_glm_interval,
    )

    try:
        model_offset = None
        if spec.offset.kind == "model":
            source = await model_service.resolve_offset_model(
                session,
                workspace_id=workspace_id,
                ref=str(spec.offset.offset_model_ref),
                caller_link=spec.link,
            )
            model_offset = linear_predictor(
                source.fit, frame, source.factors, source.spec,
                bandings=source.bandings, groupings=source.groupings,
            )
        if fit.covariance_blob is None:
            return (
                predict_glm(
                    fit, frame, factors, spec, model_offset=model_offset,
                    bandings=bandings, groupings=groupings,
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
            model_offset=model_offset,
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
            kind=UncertaintyKind.CONFIDENCE_INTERVAL_MEAN,
            level=CONFIDENCE_LEVEL,
            # FR-MODEL-99. Read from the spec, which is the one derivation (OQ-MODEL-14):
            # for `alpha > 0` this interval comes from the unpenalised information matrix
            # and is wider than the shrunk estimate warrants. Stating it is the whole of the
            # decision — the alternative is a number a reader takes for exact inference.
            basis=spec.uncertainty_basis,
        ),
    )


async def _score_gbm(
    session: Any,
    fit: GbmFitResult,
    spec: ModelSpec,
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    workspace_id: UUID,
    model: ModelRow,
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
    blob_store: BlobStore,
) -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64] | None,
    npt.NDArray[np.float64] | None,
    Uncertainty,
]:
    """`μ` from the booster, and either FR-MODEL-78's pair or FR-MODEL-77's typed absence.

    **All four of `UnavailableReason`'s values are reachable from here** (FR-MODEL-100).
    Until the paired-quantile slice, `no_interval_models_fitted` was the only one a GBM
    could return and the other two were declared and unreachable; the docstring that said
    so is gone with the state it described.

    The four arms are ordered **most specific first**, and the order is load-bearing: a
    superseded model whose bounds are also unapproved reports staleness, because the family
    having moved on is the more useful thing to say. Reordered, the caller is told to get
    the bounds approved for a model version nobody should be quoting.

    The variance-model approximation FR-MODEL-77 refuses would still fit here in four lines.
    That is why the requirement is written down: a wrong interval on a price is worse than
    no interval, and its cheapness is what makes refusing it a decision rather than an
    omission.
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import (
        PredictionError,
        detect_quantile_crossing,
        score_fitted,
    )

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

    def absent(reason: UnavailableReason) -> tuple[
        npt.NDArray[np.float64], None, None, Uncertainty
    ]:
        return expected, None, None, Uncertainty(
            kind=UncertaintyKind.UNAVAILABLE, reason=reason
        )

    bounds = [
        row
        for row in await model_service.load_interval_models(
            session, workspace_id=workspace_id, central_model_id=model.id
        )
        if row.fit_result is not None
    ]
    sides = {"lower": [], "upper": []}  # type: dict[str, list[ModelRow]]
    for row in bounds:
        bound_spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
        assert isinstance(bound_spec, GbmSpec)
        assert bound_spec.interval_for is not None
        sides["lower" if bound_spec.interval_for.alpha < 0.5 else "upper"].append(row)

    # 1. Half a pair is not a pair. FR-MODEL-77's vocabulary is closed, and the absence of a
    #    *pair* is what `no_interval_models_fitted` says — a lone bound needs no new code.
    if len(sides["lower"]) != 1 or len(sides["upper"]) != 1:
        return absent(UnavailableReason.NO_INTERVAL_MODELS_FITTED)

    # 2. FR-MODEL-100(iii). `superseded` is scoreable, so this model's bounds are quotable —
    #    and quoting them without saying the family has moved past this version is exactly
    #    the silence FR-MODEL-77 exists to refuse.
    if ModelStatus(model.status) is ModelStatus.SUPERSEDED:
        return absent(UnavailableReason.INTERVAL_MODELS_STALE)

    # 3. FR-MODEL-100(ii). Not "unapproved outright" — the bounds must be at least as
    #    reviewed as the model they bound. An approved Model quoting a merely `fitted` bound
    #    puts a reviewed and an unreviewed number on one line with nothing separating them.
    lower_row, upper_row = sides["lower"][0], sides["upper"][0]
    if ModelStatus(model.status) is ModelStatus.APPROVED and any(
        ModelStatus(row.status) is not ModelStatus.APPROVED
        for row in (lower_row, upper_row)
    ):
        return absent(UnavailableReason.INTERVAL_MODELS_NOT_APPROVED)

    lower_alpha, lower = await _score_bound(
        session, lower_row, frame, workspace_id=workspace_id, blob_store=blob_store
    )
    upper_alpha, upper = await _score_bound(
        session, upper_row, frame, workspace_id=workspace_id, blob_store=blob_store
    )

    # 4. FR-MODEL-78: crossing is reported, never reordered — and never quietly dropped.
    #    `PredictedRow` refuses to serialise a reversed pair, so without this the honest
    #    finding arrives as a 500 with the reason buried in a traceback.
    rows_crossing, worst_gap = detect_quantile_crossing(lower, upper)
    if rows_crossing:
        raise PlatformError(
            "MODEL_INTERVAL_UNAVAILABLE",
            "The interval models cross on these rows",
            409,
            f"{rows_crossing} of {frame.height} rows have a lower bound above their upper "
            f"bound (worst gap {worst_gap:.4g}). FR-MODEL-78: a crossing pair does not "
            "describe one distribution, so the bounds are reported as computed or not at "
            "all — reordering them would return two plausible numbers that mean nothing. "
            f"The pair's fit-time crossing is recorded on "
            f"{upper_row.model_family_slug}@{upper_row.version}'s diagnostics.",
        )

    return (
        expected,
        lower,
        upper,
        Uncertainty(
            kind=UncertaintyKind.QUANTILE_PAIR_INTERVAL,
            # The coverage the pair actually has, which is the gap between the alphas —
            # never `CONFIDENCE_LEVEL`, which describes a matrix this interval never used.
            level=upper_alpha - lower_alpha,
            interval_models=IntervalModels(
                lower_model_id=lower_row.id,
                upper_model_id=upper_row.id,
                lower_alpha=lower_alpha,
                upper_alpha=upper_alpha,
            ),
        ),
    )


async def _score_ebm(
    fit: FitResult,
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
) -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64] | None,
    npt.NDArray[np.float64] | None,
    Uncertainty,
]:
    """`mu` from an EBM's exported tables, and the typed absence its type forces.

    The shortest of the three arms, and the shortness is the requirement rather than a
    convenience: an EBM's fit result *is* its model (ADR-0003), so there is no blob to
    fetch, no link to invert, and no `model_offset` to forward — FR-MODEL-24 refuses an
    EBM offset ref at the schema, so no spec reaching here can carry one.

    The interval is absent by construction (FR-MODEL-124). `interval_for` lives on
    `GbmSpec`, so no quantile pair is fittable for an EBM, and there is no covariance
    matrix that could have been stored and was not. Reporting either of those reasons
    would tell a reader to do something the schema forbids, which is why this arm carries
    a reason of its own.
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import PredictionError, predict_ebm

    if not isinstance(fit, EbmFitResult):
        # `02` R2 freezes `spec` and `fit_result` together, so this pairing should not
        # exist — but the two are validated out of the row by independent adapters and
        # nothing in the type system joins them. Refused rather than asserted: an `assert`
        # compiled out under `-O` turns a governed refusal into an `AttributeError`, and
        # `model_handlers.py` already names this same mismatch with this same code.
        raise PlatformError(
            "MODEL_TYPE_UNSUPPORTED",
            "This model's spec and fit result disagree about its type",
            409,
            f"the spec is an EBM and the stored fit result is a "
            f"{type(fit).__name__}. `02` R2 freezes the two together, so this row was "
            "written by something that bypassed the model service.",
        )

    try:
        expected = predict_ebm(fit, frame, factors, bandings=bandings, groupings=groupings)
    except (ModellingError, PredictionError) as exc:
        raise _unscoreable(exc) from exc

    return (
        expected,
        None,
        None,
        Uncertainty(
            kind=UncertaintyKind.UNAVAILABLE,
            reason=UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
        ),
    )


async def _score_bound(
    session: Any,
    row: ModelRow,
    frame: pl.DataFrame,
    *,
    workspace_id: UUID,
    blob_store: BlobStore,
) -> tuple[float, npt.NDArray[np.float64]]:
    """One bound's declared alpha and its predictions over `frame`.

    Resolved here rather than in `pricing-core`, which is handed dataframes and artifacts
    and never ids (ADR-0001).
    """
    from pricing_core.modelling import ModellingError
    from pricing_core.modelling.predict import PredictionError, score_fitted

    spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    fit = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
    assert isinstance(spec, GbmSpec)
    assert spec.interval_for is not None
    assert isinstance(fit, GbmFitResult)

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
        scored = score_fitted(
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
    return spec.interval_for.alpha, scored


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
