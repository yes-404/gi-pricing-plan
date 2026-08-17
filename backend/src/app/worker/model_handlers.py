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
from typing import Any
from uuid import UUID

import polars as pl

from app.db.models import BlobRow, DatasetSplitRow, DatasetVersionRow, ModelRow
from app.errors import PlatformError
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import modelling as model_service
from app.platform import transformations as transform_service
from app.platform.blobs import to_ref
from app.worker.data_handlers import _actor, _bridge, _workspace
from app.worker.handlers import register_handler
from model_schema import (
    Banding,
    Diagnostics,
    Factor,
    GlmFitResult,
    GlmSpec,
    Grouping,
    JobKind,
    JobResult,
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
    spec: GlmSpec,
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
        GlmSpec, list[Factor], _Transformations, pl.DataFrame, pl.DataFrame
    ]:
        async with progress.database.session() as session:
            row = await session.get(ModelRow, model_id)
            if row is None or row.workspace_id != workspace_id:
                raise PlatformError(
                    "NOT_FOUND", "Model not found", 404, f"No model {model_id}."
                )
            spec = GlmSpec.model_validate(row.spec)
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
            return spec, factors, transformations, train, holdout

    spec, factors, transformations, frame, holdout = progress.run_on_loop(load())

    from pricing_core.modelling import GlmFitError, fit_glm
    from pricing_core.modelling.factors import FactorResolutionError

    try:
        result = fit_glm(
            frame,
            spec,
            factors,
            seed=spec.seed,
            bandings=transformations.bandings,
            groupings=transformations.groupings,
            # The fit owns the middle of the bar and reports its own `0..1` inside it.
            # Before this it reported nothing, and a long fit sat at 0.35 for its whole
            # duration — which FR-PLAT-8 exists to prevent and `00` §5.5 already required.
            progress=ScaledProgress(progress, start=0.10, end=0.85),
        )
    except GlmFitError as exc:
        # `pricing-core` names the failure; the platform gives it the HTTP shape. Mapped
        # rather than re-raised so a job's stored error carries `02` §5.1's code and a
        # reader can look it up.
        raise PlatformError(exc.code, "The GLM could not be fitted", 409, str(exc)) from exc
    except FactorResolutionError as exc:
        raise PlatformError(
            "FACTOR_RESOLUTION_FAILED",
            "A factor could not be resolved against this dataset version",
            409,
            f"{exc} FR-MODEL-2: a Factor is defined against a Dataset and resolved against "
            "a version; this is that resolution failing.",
        ) from exc
    progress.update(0.85, "diagnostics")
    from pricing_core.modelling import compute_diagnostics

    computed = compute_diagnostics(
        result,
        spec,
        factors,
        train=frame,
        holdout=holdout,
        bandings=transformations.bandings,
        groupings=transformations.groupings,
        progress=ScaledProgress(progress, start=0.85, end=0.97),
    )
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=model_id,
        computed_at=datetime.now(UTC),
        job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
        universal=computed.universal,
        complexity=computed.complexity,
        glm=computed.glm,
    )
    progress.update(0.97, "storing coefficients and diagnostics")

    async def store() -> None:
        async with progress.database.unit_of_work() as session:
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


async def _resolve_candidate(
    session: Any, blob_store: Any, *, workspace_id: UUID, row: ModelRow
) -> Any:
    """One model, resolved to everything `compare_models` needs (ADR-0001).

    The same resolution `_fit` does, for the same reason: `pricing-core` is handed
    dataframes and artifacts, never ids, because resolving an id needs a database it may not
    import.
    """
    from pricing_core.modelling.comparison import ComparisonCandidate

    spec = GlmSpec.model_validate(row.spec)
    factors = await model_service.load_factors(
        session, workspace_id=workspace_id, factor_ids=list(spec.factors)
    )
    if row.fit_result is None:
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "A model with no coefficients cannot be compared",
            409,
            f"{row.model_family_slug}@{row.version} has no fit result.",
        )
    return ComparisonCandidate(
        ref=f"model:{row.model_family_slug}@{row.version}",
        fit=GlmFitResult.model_validate(row.fit_result),
        spec=spec,
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


def register_model_handlers() -> None:
    """Register the `model.*` handlers, idempotently — see `register_data_handlers`."""
    from app.worker import handlers as handler_registry

    if JobKind.MODEL_FIT not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_FIT, _fit)
    if JobKind.MODEL_COMPARE not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_COMPARE, _compare)
