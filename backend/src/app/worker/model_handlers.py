"""The `model.*` Job handlers (`02` §3.4, `07` FR-PLAT-7).

Two handlers: `model.fit` reads the version's parquet, resolves the spec's factors against
it, fits with `pricing-core`, and records the numbers on the model row that `reserve_model`
already allocated. `model.compare` scores two or more fitted models over the holdout they
share and records the comparison artifact (FR-MODEL-56).

**The reservation happens in the request, not here**, so `02` R1 — fitting requires a
`validated` Dataset Version — is answered before a Job exists. A caller who is refused
learns it from a `409`, not from a failed job twenty seconds later.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import polars as pl
from sqlalchemy import select

from app.db.models import BlobRow, DatasetSplitRow, DatasetVersionRow, ModelRow
from app.errors import PlatformError
from app.platform import backtests as backtest_service
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import diagnostics as diagnostics_service
from app.platform import metrics as metric_service
from app.platform import modelling as model_service
from app.platform import objectives as objective_service
from app.platform import perils as peril_service
from app.platform import transformations as transform_service
from app.platform import transparency as transparency_service
from app.platform.blobs import to_ref
from app.worker.data_handlers import _actor, _bridge, _workspace
from app.worker.handlers import register_handler
from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    Banding,
    CrossValidationDiagnostics,
    CustomMetric,
    CustomObjective,
    Diagnostics,
    Factor,
    FitResult,
    GbmEvalPoint,
    GbmFitResult,
    GbmSpec,
    GlmFitResult,
    GlmSpec,
    Grouping,
    JobKind,
    JobResult,
    ModelSpec,
    PerilStructure,
    QuantileCrossing,
    ReconciledPeril,
    Reconciliation,
    SamplingSpec,
    TransparencyArtifact,
    new_uuid7,
)
from pricing_core import ProgressCallback, ScaledProgress

__all__ = ["register_model_handlers"]


@dataclass(frozen=True, slots=True)
class _Transformations:
    """The banding and grouping artifacts a spec's factors pin, keyed by id."""

    bandings: dict[UUID, Banding]
    groupings: dict[UUID, Grouping]


async def _frame_of(session: Any, blob_store: Any, version: Any) -> pl.DataFrame:
    """A version's single table, as a frame."""
    entry = version.tables[0]
    blob = await session.get(BlobRow, entry["blob"]["sha256"])
    if blob is None:
        raise PlatformError(
            "NOT_FOUND", "A table's blob is missing", 404,
            f"Version {version.id} names a blob that is not in the store.",
        )
    return pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(blob))))


async def _split_frames(
    session: Any,
    blob_store: Any,
    *,
    workspace_id: UUID,
    spec: ModelSpec,
    parent: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """The train and holdout frames the spec's `split_ref` names (`01` FR-DATA-36).

    Read from the **part versions** the split artifact records, not re-derived here. The
    whole point of recording the split on the parent is that the partition is one artifact
    two models cite; a fit that recomputed it would be trusting that its arithmetic still
    matched the arithmetic that produced the versions, which is the belief FR-DATA-36
    exists to remove.
    """
    ref = spec.split_ref
    assert ref is not None  # guarded by the caller
    split = await session.get(DatasetSplitRow, ref.split_artifact_id)
    if split is None or split.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Split not found", 404,
            f"No split {ref.split_artifact_id} in this workspace.",
        )

    frames: list[pl.DataFrame] = []
    for part in (ref.train_part, ref.holdout_part):
        version_id = split.parts.get(part)
        if version_id is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "The split has no such part",
                422,
                f"Split {split.name!r} defines {sorted(split.parts)}, not {part!r}.",
            )
        version = await session.get(DatasetVersionRow, UUID(str(version_id)))
        if version is None or version.workspace_id != workspace_id:
            raise PlatformError(
                "NOT_FOUND", "A split part's dataset version is missing", 404,
                f"Split {split.name!r} names version {version_id} for part {part!r}.",
            )
        frames.append(await _frame_of(session, blob_store, version))

    train, holdout = frames
    if train.height == 0 or holdout.height == 0:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A split part is empty",
            422,
            f"Part {ref.train_part!r} has {train.height} rows and "
            f"{ref.holdout_part!r} has {holdout.height}. An empty holdout produces "
            "diagnostics that cannot be wrong, which is not the same as a model that is "
            "right.",
        )
    if train.height + holdout.height > parent.height:
        # The failure this catches is the one that made the slice necessary: parts that
        # inherited the parent's data rather than a subset of it, so "train" and "holdout"
        # each held every row and overlapped completely.
        raise PlatformError(
            "VALIDATION_FAILED",
            "The split parts overlap",
            422,
            f"{ref.train_part!r} ({train.height}) and {ref.holdout_part!r} "
            f"({holdout.height}) together exceed the parent's {parent.height} rows, so "
            "they share rows. A holdout containing training rows reports the model's "
            "memory as though it were its performance.",
        )
    return train, holdout


def _fit(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`model.fit` — fit the reserved model and store its coefficients (FR-MODEL-18..21).

    The fit result is **data** (ADR-0003): coefficients, standard errors, intervals and
    relativity tables, stored as JSON on the model row. No estimator is pickled, and
    nothing that scores this model later needs `glum` installed.
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    model_id = UUID(parameters["model_id"])
    progress.update(0.05, "loading the model spec")

    async def load() -> tuple[
        ModelSpec,
        list[Factor],
        _Transformations,
        pl.DataFrame,
        pl.DataFrame,
        CustomObjective | None,
        dict[str, CustomMetric],
    ]:
        async with progress.database.session() as session:
            row = await session.get(ModelRow, model_id)
            if row is None or row.workspace_id != workspace_id:
                raise PlatformError(
                    "NOT_FOUND", "Model not found", 404, f"No model {model_id}."
                )
            spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
            factors = await model_service.load_factors(
                session, workspace_id=workspace_id, factor_ids=list(spec.factors)
            )
            # The bandings and groupings the factors pin. Loaded here rather than inside
            # `pricing-core`, which cannot reach a database (ADR-0001) — and eagerly rather
            # than lazily, because a dangling reference should be a `404` naming the id,
            # not a resolution failure naming the factor.
            transformations = _Transformations(
                bandings=await transform_service.load_bandings(
                    session,
                    workspace_id=workspace_id,
                    ids=[f.banding_id for f in factors if f.banding_id],
                ),
                groupings=await transform_service.load_groupings(
                    session,
                    workspace_id=workspace_id,
                    ids=[f.grouping_id for f in factors if f.grouping_id],
                ),
            )

            # **R1 again, here.** Checking it at reservation answers "may this be
            # queued?"; this answers "may this be fitted?", and they are different
            # questions with a queue between them. `validated → validating → failed` are
            # both legal transitions and the analyst who can fit can also validate, so a
            # version can lose its standing after the Job is submitted and before it runs.
            # Without this a model reached `fitted` on a `failed` version.
            version = await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=spec.dataset_version_id
            )
            # One table for the spine: `02` §4.4 fits over a single record grain, and a
            # join across tables is a Preparation Recipe's job (`01` FR-DATA-12), done
            # before the version exists.
            frame = await _frame_of(session, blob_store, version)

            # The holdout, from the split the spec cites (`01` FR-DATA-36). Required, not
            # optional: FR-MODEL-49 makes diagnostics a product of every fit, FR-MODEL-54
            # makes a diagnostic without its holdout counterpart a defect, and `02` §4.8
            # makes diagnostics the condition of `fitted`. A fit with no split therefore
            # has nowhere to go, and refusing it here is cheaper than a Job that runs for
            # three minutes and then cannot record its result.
            if spec.split_ref is None:
                raise PlatformError(
                    "MODEL_SPLIT_REQUIRED",
                    "This model spec declares no split",
                    422,
                    "`split_ref` names the train/test split this model is fitted and "
                    "judged on (`01` FR-DATA-36). Without it there is no holdout, and "
                    "FR-MODEL-54 makes a diagnostic reported without its holdout "
                    "counterpart a defect.",
                )
            train, holdout = await _split_frames(
                session, blob_store, workspace_id=workspace_id, spec=spec, parent=frame
            )
            # The Custom Objective the spec names, resolved here for the reason the
            # bandings are: `pricing-core` computes and does not resolve a reference
            # (ADR-0001). `fit_gbm` refuses a `custom` objective that arrives without its
            # artifact, one whose ref does not match, and one whose status is not
            # fittable — so this loads it and lets the maths keep the invariants.
            objective = (
                await objective_service.resolve_ref(
                    session, workspace_id=workspace_id, ref=spec.objective.ref or ""
                )
                if isinstance(spec, GbmSpec) and spec.objective.kind == "custom"
                else None
            )
            # Every `kind: custom` eval metric the spec names, resolved for the same
            # reason the objective above is: `fit_gbm` takes `metrics` as already-resolved
            # artifacts (ADR-0001) and refuses a ref that arrives unsupplied
            # (`METRIC_REF_UNRESOLVED`), one outside its applicability
            # (`METRIC_NOT_APPLICABLE`) or one not fittable (`METRIC_NOT_FITTABLE`) —
            # `_resolve_metrics` needs the artifact in hand to say which. Same session,
            # same transaction as the objective resolution above it: a second
            # `unit_of_work` here would take a second connection from the pool and
            # deadlock rather than fail.
            metrics: dict[str, CustomMetric] = {}
            if isinstance(spec, GbmSpec):
                for eval_metric_ref in spec.eval_metrics:
                    if eval_metric_ref.kind != "custom":
                        continue
                    ref = eval_metric_ref.ref or ""
                    metrics[ref] = await metric_service.resolve_ref(
                        session, workspace_id=workspace_id, ref=ref
                    )
            return spec, factors, transformations, train, holdout, objective, metrics

    spec, factors, transformations, frame, holdout, objective, metrics = progress.run_on_loop(
        load()
    )

    from pricing_core.modelling import GbmFitError, GlmFitError, fit_gbm, fit_glm
    from pricing_core.modelling.factors import FactorResolutionError

    # The fit owns the middle of the bar and reports its own `0..1` inside it. Before this
    # it reported nothing, and a long fit sat at 0.35 for its whole duration — which
    # FR-PLAT-8 exists to prevent and `00` §5.5 already required.
    fitting = ScaledProgress(progress, start=0.10, end=0.85)
    booster: bytes | None = None
    covariance: bytes | None = None
    glm_cv: CrossValidationDiagnostics | None = None
    eval_curve: tuple[GbmEvalPoint, ...] = ()
    result: FitResult
    try:
        if isinstance(spec, GbmSpec):
            fit = fit_gbm(
                frame, spec, factors,
                # FR-MODEL-30: the holdout rows, not merely the declared split. `fit_gbm`
                # refuses early stopping without them rather than letting either backend
                # fall back to the training set.
                holdout=holdout,
                bandings=transformations.bandings,
                groupings=transformations.groupings,
                objective=objective,
                metrics=metrics,
                progress=fitting,
            )
            result, booster, eval_curve = fit.result, fit.booster_bytes, fit.eval_curve
        else:
            glm_fit = fit_glm(
                frame, spec, factors, seed=spec.seed,
                bandings=transformations.bandings,
                groupings=transformations.groupings,
                progress=fitting,
            )
            # The same split the GBM arm makes above, and for the same reason: the artifact
            # carries a `BlobRef` and the bytes travel beside it, because `pricing-core`
            # cannot store a blob (ADR-0001). FR-MODEL-63's interval is computed from these
            # bytes at predict time.
            result, covariance = glm_fit.result, glm_fit.covariance_bytes
            glm_cv = glm_fit.cv
    except (GbmFitError, GlmFitError) as exc:
        # `pricing-core` names the failure; the platform gives it the HTTP shape. Mapped
        # rather than re-raised so a job's stored error carries `02` §5.1's code and a
        # reader can look it up.
        raise PlatformError(
            exc.code, f"The {spec.model_type} model could not be fitted", 409, str(exc)
        ) from exc
    except FactorResolutionError as exc:
        raise PlatformError(
            "FACTOR_RESOLUTION_FAILED",
            "A factor could not be resolved against this dataset version",
            409,
            f"{exc} FR-MODEL-2: a Factor is defined against a Dataset and resolved against "
            "a version; this is that resolution failing.",
        ) from exc
    progress.update(0.85, "diagnostics")
    from pricing_core.modelling import compute_diagnostics, compute_gbm_diagnostics

    diagnostic_progress = ScaledProgress(progress, start=0.85, end=0.97)
    if isinstance(spec, GbmSpec) and isinstance(result, GbmFitResult) and booster:
        computed = compute_gbm_diagnostics(
            result, booster, spec, factors,
            train=frame, holdout=holdout, eval_curve=eval_curve,
            bandings=transformations.bandings,
            groupings=transformations.groupings,
            progress=diagnostic_progress,
        )
    elif isinstance(spec, GlmSpec) and isinstance(result, GlmFitResult):
        computed = compute_diagnostics(
            result, spec, factors,
            train=frame, holdout=holdout,
            bandings=transformations.bandings,
            groupings=transformations.groupings,
            progress=diagnostic_progress,
        )
    else:  # pragma: no cover - the unions are checked together at the type
        raise PlatformError(
            "MODEL_TYPE_UNSUPPORTED",
            "This model type cannot be fitted",
            409,
            f"{spec.model_type!r} has a spec arm and no fit path. `ebm` is declared by "
            "`CLAUDE.md` §7 and built by no slice.",
        )
    # FR-MODEL-78. Only the **second** bound of a pair has a counterpart to cross: the
    # first is fitted against nothing, and FR-MODEL-49 computes diagnostics once at fit
    # time, so there is no later pass in which to fill this in. Scoring the counterpart
    # costs one extra pass over the fit frame, which is cheap beside the fit that just
    # produced it — and this is the only moment both boosters and the population are
    # in hand together.
    gbm_diagnostics = computed.gbm
    if isinstance(spec, GbmSpec) and spec.interval_for is not None and booster is not None:
        assert isinstance(result, GbmFitResult)
        assert gbm_diagnostics is not None
        crossing = progress.run_on_loop(
            _quantile_crossing(
                progress,
                blob_store,
                workspace_id=workspace_id,
                model_id=model_id,
                spec=spec,
                result=result,
                booster=booster,
                factors=factors,
                transformations=transformations,
                frame=frame,
            )
        )
        if crossing is not None:
            gbm_diagnostics = gbm_diagnostics.model_copy(
                update={"quantile_crossing": crossing}
            )

    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=model_id,
        computed_at=datetime.now(UTC),
        job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
        universal=computed.universal,
        complexity=computed.complexity,
        glm=computed.glm,
        gbm=gbm_diagnostics,
        cross_validation=glm_cv,
    )
    progress.update(0.97, "storing the fit and its diagnostics")

    async def store() -> None:
        async with progress.database.unit_of_work() as session:
            # **The booster is stored in the same transaction as the model row.** The
            # `BlobRef` inside `fit_result` was computed by `pricing-core` from the bytes,
            # so it is already correct — what this guarantees is that a committed model
            # never references an object that was never written. `put` is idempotent on the
            # digest (FR-PLAT-19), so a retried job stores nothing twice.
            if booster is not None:
                assert isinstance(result, GbmFitResult)
                await progress.blob_store.put(
                    session, booster, result.booster_blob.media_type
                )
            if covariance is not None:
                assert isinstance(result, GlmFitResult)
                assert result.covariance_blob is not None
                await progress.blob_store.put(
                    session, covariance, result.covariance_blob.media_type
                )
            await model_service.record_fit(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                fit_result=result,
                diagnostics=diagnostics,
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )

    progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"model:{model_id}")


async def _quantile_crossing(
    progress: Any,
    blob_store: Any,
    *,
    workspace_id: UUID,
    model_id: UUID,
    spec: GbmSpec,
    result: GbmFitResult,
    booster: bytes,
    factors: list[Factor],
    transformations: _Transformations,
    frame: pl.DataFrame,
) -> QuantileCrossing | None:
    """Score this bound and its counterpart over the fit frame and compare them.

    Returns `None` when there is no counterpart yet — this is the first bound of the pair,
    and there is nothing to cross. That is the ordinary case for the lower bound, and it is
    why `QuantileCrossing` lives on the second bound rather than on the central model.

    The counterpart's spec, factors, bandings, groupings and booster are resolved here for
    the reason `_resolve_candidate` resolves them here: `pricing-core` is handed dataframes
    and artifacts, never ids, because resolving an id needs a database it may not import
    (ADR-0001).
    """
    from pricing_core.modelling.predict import detect_quantile_crossing, score_fitted

    assert spec.interval_for is not None

    async with progress.database.session() as session:
        siblings = [
            row
            for row in await model_service.load_interval_models(
                session,
                workspace_id=workspace_id,
                central_model_id=spec.interval_for.model_id,
            )
            if row.id != model_id and row.fit_result is not None
        ]
        if not siblings:
            return None
        # At most one: FR-MODEL-100(iv) allows one bound per side, and this model holds the
        # other side. A second would have been refused at `reserve_model`.
        counterpart = siblings[0]
        other_spec = MODEL_SPEC_ADAPTER.validate_python(counterpart.spec)
        other_fit = FIT_RESULT_ADAPTER.validate_python(counterpart.fit_result)
        if not isinstance(other_spec, GbmSpec) or not isinstance(other_fit, GbmFitResult):
            return None
        other_factors = await model_service.load_factors(
            session, workspace_id=workspace_id, factor_ids=list(other_spec.factors)
        )
        other_bandings = await transform_service.load_bandings(
            session,
            workspace_id=workspace_id,
            ids=[f.banding_id for f in other_factors if f.banding_id],
        )
        other_groupings = await transform_service.load_groupings(
            session,
            workspace_id=workspace_id,
            ids=[f.grouping_id for f in other_factors if f.grouping_id],
        )
        other_booster = await blob_store.read(other_fit.booster_blob)

    mine = score_fitted(
        result,
        spec,
        frame,
        factors,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        booster=booster,
    )
    theirs = score_fitted(
        other_fit,
        other_spec,
        frame,
        other_factors,
        bandings=other_bandings,
        groupings=other_groupings,
        booster=other_booster,
    )
    # Which array is the lower bound is decided by the declared alpha, never by which
    # number happens to be smaller — sorting them here would be the silent reordering
    # FR-MODEL-78 forbids, dressed as a convenience.
    lower, upper = (mine, theirs) if spec.interval_for.alpha < 0.5 else (theirs, mine)
    rows_crossing, worst_gap = detect_quantile_crossing(lower, upper)
    return QuantileCrossing(
        counterpart_model_id=counterpart.id,
        rows_checked=frame.height,
        rows_crossing=rows_crossing,
        worst_gap=worst_gap,
    )


async def _resolve_candidate(
    session: Any, blob_store: Any, *, workspace_id: UUID, row: ModelRow
) -> Any:
    """One model, resolved to everything `compare_models` needs (ADR-0001).

    The same resolution `_fit` does, for the same reason: `pricing-core` is handed
    dataframes and artifacts, never ids, because resolving an id needs a database it may not
    import.
    """
    from pricing_core.modelling.comparison import ComparisonCandidate

    spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    factors = await model_service.load_factors(
        session, workspace_id=workspace_id, factor_ids=list(spec.factors)
    )
    if row.fit_result is None:
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "A model with no fit result cannot be compared",
            409,
            f"{row.model_family_slug}@{row.version} has no fit result.",
        )
    fit = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
    # `wf-01` E1 compares the GLM against the GBM. A GLM's fit result *is* its model; a
    # GBM's is a reference to the booster, so the bytes are fetched here — the resolution
    # ADR-0001 keeps out of `pricing-core`, exactly like the factors and the frames.
    booster = (
        await blob_store.read(fit.booster_blob) if isinstance(fit, GbmFitResult) else None
    )
    return ComparisonCandidate(
        ref=f"model:{row.model_family_slug}@{row.version}",
        fit=fit,
        spec=spec,
        booster=booster,
        factors=tuple(factors),
        bandings=await transform_service.load_bandings(
            session,
            workspace_id=workspace_id,
            ids=[f.banding_id for f in factors if f.banding_id],
        ),
        groupings=await transform_service.load_groupings(
            session,
            workspace_id=workspace_id,
            ids=[f.grouping_id for f in factors if f.grouping_id],
        ),
    )


def _compare(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`model.compare` — align two or more models on the holdout they share (FR-MODEL-56).

    The comparability rules are checked in `request_comparison` before this Job exists, and
    **again** here through `compare_models`. Both are needed: the first so a caller gets a
    409 rather than a failed job, the second because a Job sits in a queue while the world
    moves, and because `compare_models` is reachable from a notebook where the platform is
    not.
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    model_ids = [UUID(i) for i in parameters["model_ids"]]
    baseline_id = UUID(parameters["baseline_id"])
    progress.update(0.05, "loading the candidates")

    async def load() -> tuple[list[Any], pl.DataFrame, str]:
        async with progress.database.session() as session:
            rows: list[ModelRow] = []
            for model_id in model_ids:
                row = await session.get(ModelRow, model_id)
                if row is None or row.workspace_id != workspace_id:
                    raise PlatformError(
                        "NOT_FOUND", "Model not found", 404, f"No model {model_id}."
                    )
                rows.append(row)

            candidates = [
                await _resolve_candidate(
                    session, blob_store, workspace_id=workspace_id, row=row
                )
                for row in rows
            ]
            baseline = next(
                c for c, row in zip(candidates, rows, strict=True) if row.id == baseline_id
            )

            # The holdout, from the split every candidate cites. Read through the same
            # `_split_frames` the fit uses, so the frame compared on is the frame trained
            # against — a second reader of the same split could drift from the first.
            spec = candidates[0].spec
            version = await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=spec.dataset_version_id
            )
            parent = await _frame_of(session, blob_store, version)
            _, holdout = await _split_frames(
                session, blob_store, workspace_id=workspace_id, spec=spec, parent=parent
            )
            return candidates, holdout, baseline.ref

    candidates, holdout, baseline_ref = progress.run_on_loop(load())
    progress.update(0.35, "scoring the holdout")

    from pricing_core.modelling import ModellingError, compare_models

    try:
        summary = compare_models(candidates, holdout, baseline=baseline_ref)
    except ModellingError as exc:
        # `pricing-core` names the failure; the platform gives it the HTTP shape, so a Job's
        # stored error carries `02` §5.1's code rather than a library traceback.
        raise PlatformError(
            exc.code, "The models could not be compared", 409, str(exc)
        ) from exc

    progress.update(0.9, "storing the comparison")

    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            row = await comparison_service.record_comparison(
                session,
                workspace_id=workspace_id,
                actor=actor,
                summary=summary,
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )
            return row.id

    comparison_id = progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"model_comparison:{comparison_id}")



def _transparency(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`model.transparency` — explain a fitted non-GLM model (FR-MODEL-33..37, 96, R3).

    Both forms are built when both can be: FR-MODEL-33 allows either and this produces
    both, because they answer different questions. The GLM approximation says what the
    model would look like as a rate table and where that table would misprice; the SHAP
    summary says which factors the booster is actually using and, on XGBoost, which pairs
    are worth an actuary authoring an `interaction` Factor for (FR-MODEL-79).

    The model is scored over the **training** partition of its own split, so the fidelity
    statement describes the population the model was fitted on. Approximating on the
    holdout would report how well a surrogate generalises, which is a different question
    and not the one R3 asks.

    FR-MODEL-96 makes the approximation a Model rather than a table inside the artifact, so
    this Job now *fits and persists* one: reserved on its own `spec_hash`, given diagnostics
    against the booster's predictions on both partitions, and named by the artifact. The
    holdout is loaded beside the train frame for that reason alone — the approximation is
    still built on train (above), and the holdout only ever reaches `compute_diagnostics`,
    which FR-MODEL-54 refuses to run one-sided.
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    model_id = UUID(parameters["model_id"])
    sample = int(parameters.get("sample", 200_000))
    job_id = UUID(parameters["job_id"]) if parameters.get("job_id") else None
    progress.update(0.05, "loading the model")

    async def load() -> tuple[
        GbmSpec,
        GbmFitResult,
        bytes,
        list[Factor],
        _Transformations,
        pl.DataFrame,
        pl.DataFrame,
        str,
        int,
    ]:
        async with progress.database.session() as session:
            row = await transparency_service.fitted_gbm_or_refuse(
                session, workspace_id=workspace_id, model_id=model_id
            )
            spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
            result = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
            if not isinstance(spec, GbmSpec) or not isinstance(result, GbmFitResult):
                raise PlatformError(
                    "MODEL_TYPE_UNSUPPORTED",
                    "This model type has no transparency builder",
                    409,
                    f"{spec.model_type!r} is not a gradient boosting model.",
                )
            if spec.split_ref is None:
                raise PlatformError(
                    "MODEL_SPLIT_REQUIRED",
                    "This model spec declares no split",
                    422,
                    "The approximation is a Model in its own right (FR-MODEL-96), and "
                    "FR-MODEL-54 makes a diagnostic reported without its holdout "
                    "counterpart a defect. Without a split there is no holdout to report.",
                )
            factors = await model_service.load_factors(
                session, workspace_id=workspace_id, factor_ids=list(spec.factors)
            )
            transformations = _Transformations(
                bandings=await transform_service.load_bandings(
                    session, workspace_id=workspace_id,
                    ids=[f.banding_id for f in factors if f.banding_id],
                ),
                groupings=await transform_service.load_groupings(
                    session, workspace_id=workspace_id,
                    ids=[f.grouping_id for f in factors if f.grouping_id],
                ),
            )
            version = await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=spec.dataset_version_id
            )
            parent = await _frame_of(session, blob_store, version)
            train, holdout = await _split_frames(
                session, blob_store, workspace_id=workspace_id, spec=spec, parent=parent
            )
            booster = await blob_store.read(result.booster_blob)
            # The source's identity travels with the frames rather than being re-read in a
            # second session later: `store()` needs it only for the change reason, and a
            # second read is a second answer to a question already asked.
            return (
                spec, result, booster, factors, transformations, train, holdout,
                row.model_family_slug, row.version,
            )

    (
        spec, result, booster, factors, transformations, frame, holdout,
        source_slug, source_version,
    ) = progress.run_on_loop(load())

    from pricing_core.modelling import (
        approximation_spec,
        build_glm_approximation,
        build_shap_summary,
        compute_diagnostics,
        fidelity_statement,
    )

    # `models.model_family_slug` is a `String(64)` and this Job generates a slug seven
    # characters longer than the one the analyst chose. Refused here, naming the cause,
    # rather than as a driver `DataError` naming a column at the end of the compute.
    surrogate_spec = approximation_spec(spec, source_model_id=model_id)
    if len(surrogate_spec.model_family_slug) > 64:
        raise PlatformError(
            "VALIDATION_FAILED",
            "The approximating model's slug is too long",
            422,
            f"{spec.model_family_slug!r} plus the '-approx' suffix is "
            f"{len(surrogate_spec.model_family_slug)} characters, and a model family slug "
            "is 64. Rename the model family, or the approximation FR-MODEL-96 requires "
            "cannot be stored.",
        )

    progress.update(0.20, "fitting the GLM approximation")
    approximation = build_glm_approximation(
        result, booster, spec, factors, frame,
        holdout=holdout,
        source_model_id=model_id,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.20, end=0.50),
    )
    progress.update(0.50, "diagnostics of the approximation")
    # FR-MODEL-96(iii): the surrogate reaches `fitted` on diagnostics of itself against the
    # source model's predictions — FR-MODEL-36's quantity, on both partitions. The frames
    # carry the booster's predictions in `SURROGATE_RESPONSE_COLUMN`, so this is the
    # ordinary GLM diagnostics path measuring an extraordinary target, and FR-MODEL-102's
    # spec invariant is what says so to every later reader.
    surrogate_diagnostics = compute_diagnostics(
        approximation.result, approximation.spec, factors,
        train=approximation.train, holdout=approximation.holdout,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.50, end=0.62),
    )
    progress.update(0.62, "tree shap")
    summary = build_shap_summary(
        result, booster, spec, factors, frame,
        sample=sample,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.62, end=0.90),
    )

    async def store() -> UUID:
        # **One transaction, and never a second inside it.** A failed compute leaves
        # nothing behind, and the artifact never commits without the Model it names. An
        # inner `unit_of_work` would take a second connection from the pool and deadlock
        # against it with no output and no traceback.
        async with progress.database.unit_of_work() as session:
            # FR-MODEL-52's monotonicity check, carried up to the artifact R3 reads. Taken
            # from the diagnostics rather than recomputed: the diagnostics swept the factors
            # at fit time, and a second sweep here could disagree with the evidence the
            # model was approved against.
            diagnostics = await diagnostics_service.load_diagnostics(
                session, workspace_id=workspace_id, model_id=model_id
            )
            checks = diagnostics.gbm.monotonicity if diagnostics.gbm else ()

            # FR-MODEL-96. Reserved rather than created: `spec_hash` makes a rebuilt
            # artifact find the surrogate it already fitted (FR-MODEL-66), and calling
            # `record_fit` on it a second time would raise `MODEL_IMMUTABLE` and fail a Job
            # that had done nothing wrong.
            surrogate, should_fit = await model_service.reserve_model(
                session,
                workspace_id=workspace_id,
                actor=actor,
                spec=approximation.spec,
                change_reason=(
                    f"glm approximation of {source_slug}@{source_version} (FR-MODEL-34)"
                ),
            )
            if should_fit:
                await model_service.record_fit(
                    session,
                    workspace_id=workspace_id,
                    actor=actor,
                    model_id=surrogate.id,
                    # The covariance reference is dropped, not stored: the bytes were never
                    # kept, and FR-MODEL-63's interval belongs to the model that priced the
                    # row rather than to a description of it (FR-MODEL-102).
                    fit_result=approximation.result.model_copy(
                        update={"covariance_blob": None}
                    ),
                    diagnostics=Diagnostics(
                        id=new_uuid7(),
                        model_id=surrogate.id,
                        computed_at=datetime.now(UTC),
                        job_id=job_id,
                        universal=surrogate_diagnostics.universal,
                        complexity=surrogate_diagnostics.complexity,
                        glm=surrogate_diagnostics.glm,
                    ),
                    job_id=job_id,
                )

            # On the `should_fit=False` path this block's `r_squared` and `worst_regions`
            # come from the fit **just computed**, while the Model it names holds the first
            # one. They agree only because `fit_glm` is deterministic under `spec.seed`,
            # which `approximation_spec` carries over from the GBM — an artifact that
            # disagreed with the Model it cites would be the failure this sentence exists
            # to make visible.
            block = approximation.artifact_block(surrogate.id)
            artifact = TransparencyArtifact(
                id=new_uuid7(),
                model_id=model_id,
                created_at=datetime.now(UTC),
                job_id=job_id,
                glm_approximation=block,
                shap_summary=summary,
                fidelity_statement=fidelity_statement(block, summary),
                monotonicity_verified=(
                    all(check.holds for check in checks) if checks else None
                ),
            )
            row = await transparency_service.record_transparency(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                artifact=artifact,
                job_id=job_id,
            )
            return row.id

    artifact_id = progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"transparency:{artifact_id}")


def _backtest(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`model.backtest` — FR-MODEL-57, one model measured on data it never saw.

    Every rule that makes this a backtest rather than a re-score is answered in
    `request_backtest`, before the Job exists: the model carries a fit result, the version is
    validated, it is not the version the model was fitted on nor a part of its split, and it
    declares the columns the score needs. What is left here is resolution and arithmetic.

    Both arms, through `backtest_model`'s `score_fitted` dispatch. A GBM's booster bytes are
    fetched here for the reason `_resolve_candidate` fetches them — resolving a blob needs a
    store `pricing-core` may not import (ADR-0001).
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    model_id = UUID(parameters["model_id"])
    version_id = UUID(parameters["dataset_version_id"])
    progress.update(0.05, "loading the model")

    async def load() -> tuple[
        ModelSpec, FitResult, bytes | None, list[Factor], _Transformations,
        pl.DataFrame, str, str, str, Any, Any,
    ]:
        async with progress.database.session() as session:
            row = await session.get(ModelRow, model_id)
            if row is None or row.workspace_id != workspace_id:
                raise PlatformError(
                    "NOT_FOUND", "Model not found", 404, f"No model {model_id}."
                )
            if row.fit_result is None:
                raise PlatformError(
                    "MODEL_NOT_FITTED",
                    "A model with no fit result cannot be backtested",
                    409,
                    f"{row.model_family_slug}@{row.version} has no fit result.",
                )
            spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
            fit = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
            factors = await model_service.load_factors(
                session, workspace_id=workspace_id, factor_ids=list(spec.factors)
            )
            transformations = _Transformations(
                bandings=await transform_service.load_bandings(
                    session, workspace_id=workspace_id,
                    ids=[f.banding_id for f in factors if f.banding_id],
                ),
                groupings=await transform_service.load_groupings(
                    session, workspace_id=workspace_id,
                    ids=[f.grouping_id for f in factors if f.grouping_id],
                ),
            )
            version = await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=version_id
            )
            fitted_on = await session.get(DatasetVersionRow, spec.dataset_version_id)
            if fitted_on is None:
                raise PlatformError(
                    "NOT_FOUND", "The version the model was fitted on is gone", 404,
                    f"Model {model_id} cites version {spec.dataset_version_id}.",
                )
            frame = await _frame_of(session, blob_store, version)
            booster = (
                await blob_store.read(fit.booster_blob)
                if isinstance(fit, GbmFitResult)
                else None
            )
            return (
                spec, fit, booster, factors, transformations, frame,
                f"model:{row.model_family_slug}@{row.version}",
                await backtest_service.version_ref(
                    session, workspace_id=workspace_id, version=version
                ),
                await backtest_service.version_ref(
                    session, workspace_id=workspace_id, version=fitted_on
                ),
                version.period_from, version.period_to,
            )

    (
        spec, fit, booster, factors, transformations, frame,
        model_ref, target_ref, fitted_on_ref, period_from, period_to,
    ) = progress.run_on_loop(load())

    from pricing_core.modelling import backtest_model

    progress.update(0.2, "scoring the period")
    summary = backtest_model(
        fit, spec, factors, frame,
        model_ref=model_ref,
        dataset_version_ref=target_ref,
        fitted_on_ref=fitted_on_ref,
        period_from=period_from,
        period_to=period_to,
        booster=booster,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.2, end=0.9),
    )

    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            row = await backtest_service.record_backtest(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                dataset_version_id=version_id,
                summary=summary,
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )
            return row.id

    backtest_id = progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"backtest:{backtest_id}")


def register_model_handlers() -> None:
    """Register the `model.*` handlers, idempotently — see `register_data_handlers`."""
    from app.worker import handlers as handler_registry

    if JobKind.MODEL_FIT not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_FIT, _fit)
    if JobKind.MODEL_COMPARE not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_COMPARE, _compare)
    if JobKind.MODEL_TRANSPARENCY not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_TRANSPARENCY, _transparency)
    if JobKind.MODEL_BACKTEST not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_BACKTEST, _backtest)
    if JobKind.PERIL_STRUCTURE_RECONCILE not in handler_registry.HANDLERS:
        register_handler(JobKind.PERIL_STRUCTURE_RECONCILE, _reconcile)
    if JobKind.OBJECTIVE_CERTIFY not in handler_registry.HANDLERS:
        register_handler(JobKind.OBJECTIVE_CERTIFY, _certify)
    if JobKind.METRIC_CERTIFY not in handler_registry.HANDLERS:
        register_handler(JobKind.METRIC_CERTIFY, _certify_metric)


def _reconcile(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`peril_structure.reconcile` — FR-MODEL-60's coherence check, FR-MODEL-74's basis.

    Every peril's models are scored on the **one** holdout they all cite —
    `_refuse_unshared_holdout` guarantees there is exactly one before this Job exists, which
    is what makes the reconciliation's `dataset_version_id` and `part` derivable rather than
    a caller's third answer.

    A **failing** reconciliation is a successful Job. FR-MODEL-60 asks for the check to be
    persisted, and the finding that a structure does not reconcile is the finding; a job
    that failed would leave an actuary re-running it to see the same number. What a `fail`
    blocks is `review`, and that is `submit_for_review`'s answer.
    """
    from pricing_core.modelling.perils import (
        PerilPrediction,
        assemble_risk_premium,
        reconcile,
    )
    from pricing_core.modelling.predict import score_fitted

    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    structure_id = UUID(parameters["structure_id"])
    tolerance = Decimal(parameters["tolerance"])
    observed_column = str(parameters["observed_column"])
    exposure_column = str(parameters["exposure_column"])
    progress.update(0.05, "loading the structure")

    async def load() -> tuple[PerilStructure, dict[str, Any], pl.DataFrame, UUID, str]:
        async with progress.database.session() as session:
            structure = await peril_service.load_structure(
                session, workspace_id=workspace_id, structure_id=structure_id
            )
            candidates: dict[str, Any] = {}
            rows: list[ModelRow] = []
            for peril in structure.perils:
                for ref in (
                    peril.frequency_model,
                    peril.severity_model,
                    peril.burning_cost_model,
                ):
                    if ref is None or str(ref) in candidates:
                        continue
                    row = (
                        await session.execute(
                            select(ModelRow).where(
                                ModelRow.workspace_id == workspace_id,
                                ModelRow.model_family_slug == ref.slug,
                                ModelRow.version == ref.version,
                            )
                        )
                    ).scalar_one_or_none()
                    if row is None:
                        raise PlatformError(
                            "NOT_FOUND", "Model not found", 404, f"No model {ref}."
                        )
                    rows.append(row)
                    candidates[str(ref)] = await _resolve_candidate(
                        session, blob_store, workspace_id=workspace_id, row=row
                    )

            # One holdout, read through the same `_split_frames` the fit used — a second
            # reader of the same split could drift from the first.
            spec = candidates[next(iter(candidates))].spec
            version = await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=spec.dataset_version_id
            )
            parent = await _frame_of(session, blob_store, version)
            _, holdout = await _split_frames(
                session, blob_store, workspace_id=workspace_id, spec=spec, parent=parent
            )
            part = spec.split_ref.holdout_part if spec.split_ref else "test"
            return structure, candidates, holdout, spec.dataset_version_id, part

    structure, candidates, holdout, dataset_version_id, part = progress.run_on_loop(load())
    progress.update(0.4, "scoring the perils")

    for column in (observed_column, exposure_column):
        if column not in holdout.columns:
            raise PlatformError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                "The declared column is not in the holdout",
                422,
                f"Column {column!r} is not among the holdout's columns. FR-MODEL-60's "
                "observed burning cost is declared by the caller precisely because it "
                "cannot be derived, so a name that does not resolve is refused rather "
                "than substituted.",
            )

    def _score(ref: Any) -> Any:
        candidate = candidates[str(ref)]
        return score_fitted(
            candidate.fit,
            candidate.spec,
            holdout,
            candidate.factors,
            bandings=candidate.bandings,
            groupings=candidate.groupings,
            booster=candidate.booster,
        )

    predictions = [
        PerilPrediction(
            peril=peril.peril,
            method=peril.method,
            frequency=_score(peril.frequency_model) if peril.frequency_model else None,
            severity=_score(peril.severity_model) if peril.severity_model else None,
            burning_cost=(
                _score(peril.burning_cost_model) if peril.burning_cost_model else None
            ),
            large_loss=peril.large_loss,
        )
        for peril in structure.perils
    ]

    from pricing_core.modelling import ModellingError

    try:
        assembled = assemble_risk_premium(predictions)
        result = reconcile(
            assembled,
            observed=holdout[observed_column].cast(pl.Float64).to_numpy(),
            exposure=holdout[exposure_column].cast(pl.Float64).to_numpy(),
            tolerance=tolerance,
            treatments={p.peril: p.large_loss.kind for p in structure.perils},
        )
    except ModellingError as exc:
        # `pricing-core` names the failure; the platform gives it the HTTP shape, so the
        # Job's stored error carries `02` §5.1's code rather than a library traceback.
        raise PlatformError(
            exc.code, "The peril structure could not be reconciled", 409, str(exc)
        ) from exc

    progress.update(0.9, "storing the reconciliation")

    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            row = await peril_service.record_reconciliation(
                session,
                workspace_id=workspace_id,
                actor=actor,
                structure_id=structure_id,
                reconciliation=Reconciliation(
                    dataset_version_id=dataset_version_id,
                    part=part,
                    perils=tuple(
                        ReconciledPeril(
                            peril=p.peril,
                            large_loss_kind=p.large_loss_kind,
                            modelled_burning_cost_minor=p.modelled_burning_cost_minor,
                        )
                        for p in result.perils
                    ),
                    observed_burning_cost_minor=result.observed_burning_cost_minor,
                    modelled_burning_cost_minor=result.modelled_burning_cost_minor,
                    tolerance=result.tolerance,
                    computed_at=datetime.now(UTC),
                ),
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )
            return row.id

    progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(
        kind="artifact", ref=f"peril_structure:{structure.slug}@{structure.version}"
    )


def _certify(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`objective.certify` — §4.7's checks over a Custom Objective (FR-MODEL-42).

    A **failing** certificate is a successful Job, for `_reconcile`'s reason: the finding
    that an objective's analytic hessian disagrees with the numeric one *is* the answer the
    run was asked for, and a job that failed would leave an actuary re-running it to read
    the same number. What a `failed` certificate blocks is `submit`, and that is
    `submit_for_review`'s answer.

    The grid comes from the parameters rather than being re-derived here. The API resolved
    it — from the caller's request or `default_sampling` — and returned a 202 that implies
    it; re-deriving would let a change to the default rule silently change what an
    already-queued Job measures.
    """
    from pricing_core.modelling import certify_objective

    progress = _bridge(callback)
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    objective_id = UUID(parameters["objective_id"])
    sampling = SamplingSpec.model_validate(parameters["sampling"])
    progress.update(0.05, "loading the objective")

    async def load() -> CustomObjective:
        async with progress.database.session() as session:
            return await objective_service.load_objective(
                session, workspace_id=workspace_id, objective_id=objective_id
            )

    objective = progress.run_on_loop(load())
    result = certify_objective(
        objective,
        sampling=sampling,
        progress=ScaledProgress(progress, start=0.1, end=0.9),
    )

    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            _, certificate = await objective_service.record_certificate(
                session,
                workspace_id=workspace_id,
                actor=actor,
                objective_id=objective_id,
                result=result,
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )
            return certificate.id

    certificate_id = progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"objective_certificate:{certificate_id}")


def _certify_metric(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`metric.certify` — §4.13's checks over a Custom Metric (FR-MODEL-105).

    A **failing** certificate is a successful Job, `_certify`'s reason unchanged: the
    finding that a metric is non-finite or scale-sensitive over the sampled grid *is* the
    answer the run was asked for. What a `failed` certificate blocks is `submit`, and that
    is `metric_service.submit`'s answer.

    Unlike `_certify`, there is no `SamplingSpec` in `parameters`: `certify_metric` samples
    a fixed internal grid (`pricing_core.modelling.metrics._grid`) rather than one a caller
    supplies, so there is nothing here to re-derive or trust from the request — only the
    seed, held fixed by `metric_service.DEFAULT_SEED` for the same reproducibility reason
    `objective_service.DEFAULT_SEED` is.
    """
    from pricing_core.modelling.metrics import certify_metric

    progress = _bridge(callback)
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    metric_id = UUID(parameters["metric_id"])
    progress.update(0.05, "loading the metric")

    async def load() -> CustomMetric:
        async with progress.database.session() as session:
            return await metric_service.load_metric(
                session, workspace_id=workspace_id, metric_id=metric_id
            )

    metric = progress.run_on_loop(load())
    progress.update(0.2, "sampling and evaluating")
    result = certify_metric(metric, seed=metric_service.DEFAULT_SEED)

    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            _, certificate = await metric_service.record_certificate(
                session,
                workspace_id=workspace_id,
                actor=actor,
                metric_id=metric_id,
                result=result,
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )
            return certificate.id

    certificate_id = progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"metric_certificate:{certificate_id}")
