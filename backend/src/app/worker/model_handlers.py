"""The `model.*` Job handlers (`02` §3.4, `07` FR-PLAT-7).

One handler so far: `model.fit`. It reads the version's parquet, resolves the spec's
factors against it, fits with `pricing-core`, and records the numbers on the model row that
`reserve_model` already allocated.

**The reservation happens in the request, not here**, so `02` R1 — fitting requires a
`validated` Dataset Version — is answered before a Job exists. A caller who is refused
learns it from a `409`, not from a failed job twenty seconds later.
"""

from __future__ import annotations

import io
from typing import Any
from uuid import UUID

import polars as pl

from app.db.models import BlobRow, DatasetVersionRow, ModelRow
from app.errors import PlatformError
from app.platform import modelling as model_service
from app.platform.blobs import to_ref
from app.worker.data_handlers import _actor, _bridge, _workspace
from app.worker.handlers import register_handler
from model_schema import GlmSpec, JobKind, JobResult
from pricing_core import ProgressCallback

__all__ = ["register_model_handlers"]


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

    async def load() -> tuple[GlmSpec, list[Any], pl.DataFrame]:
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

            version = await session.get(DatasetVersionRow, spec.dataset_version_id)
            if version is None:
                raise PlatformError(
                    "NOT_FOUND", "Dataset version not found", 404,
                    f"No version {spec.dataset_version_id}.",
                )
            # One table for the spine: `02` §4.4 fits over a single record grain, and a
            # join across tables is a Preparation Recipe's job (`01` FR-DATA-12), done
            # before the version exists.
            entry = version.tables[0]
            blob = await session.get(BlobRow, entry["blob"]["sha256"])
            if blob is None:
                raise PlatformError(
                    "NOT_FOUND", "A table's blob is missing", 404,
                    f"Version {version.id} names a blob that is not in the store.",
                )
            frame = pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(blob))))
            return spec, factors, frame

    spec, factors, frame = progress.run_on_loop(load())
    progress.update(0.35, f"fitting {len(factors)} factor(s) over {frame.height:,} rows")

    from pricing_core.modelling import GlmFitError, fit_glm
    from pricing_core.modelling.factors import FactorResolutionError

    try:
        result = fit_glm(frame, spec, factors, seed=spec.seed)
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
    progress.update(0.85, "storing coefficients")

    async def store() -> None:
        async with progress.database.unit_of_work() as session:
            await model_service.record_fit(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                fit_result=result,
                job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
            )

    progress.run_on_loop(store())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"model:{model_id}")


def register_model_handlers() -> None:
    """Register the `model.*` handlers, idempotently — see `register_data_handlers`."""
    from app.worker import handlers as handler_registry

    if JobKind.MODEL_FIT not in handler_registry.HANDLERS:
        register_handler(JobKind.MODEL_FIT, _fit)
