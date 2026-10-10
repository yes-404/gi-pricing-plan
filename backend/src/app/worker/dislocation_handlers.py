"""The `dislocation.run` Job handler (03 §5.1, FR-263, FR-265, FR-266; PL-1501 Tasks 3-4).

`pricing-core` computes (`dislocation_frame`, `select_movers`, `summarise_dislocation`,
`derive_changes`, `attribute`); this module owns what it may not: the Job identity, the
output location (a content-addressed movers blob and one `dislocation_runs` row) and
resumability. It follows `_rating_regression`: load in one `run_on_loop` call, compute on the
worker thread, persist in one unit of work through the single writer.

`attribute` is `async` only for its resolver and never runs inside `run_on_loop` (a long
coroutine there hangs, the 30 s `JobProgress` timeout `scoring_handlers.py` documents): the
handler first resolves every artifact the two versions need into a `PreloadedResolver`, then
runs `attribute` on the worker thread with no database I/O.

No partial row is ever written (the persist step is one transaction); a re-submission
recomputes and the result is byte-identical (NFR-495); blob writes are content-addressed, so a
repeated `put` is idempotent. A subset bundle is in memory inside `attribute` and is never
persisted as a Rating Version (FR-1398). No log line, error message or audit payload carries a
Quote Context (NFR-499): failures name quotes only.
"""

from __future__ import annotations

import asyncio
import io
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import polars as pl

from app.db.models import RatingVersionRow
from app.errors import PlatformError
from app.platform import datasets as dataset_service
from app.platform import rating_versions as rating_versions_service
from app.platform.dislocation_runs import (
    DISLOCATION_RATINGS_PER_WORKER_HOUR,
    DISLOCATION_SINGLE_JOB_MAX_HOURS,
    MOVERS_BLOB_PREFIX,
    portfolio_table,
    read_stored_blob,
)
from app.platform.dislocation_runs import persist_run as persist_dislocation_run
from app.platform.rating_versions import WorkspaceResolver
from app.worker.data_handlers import _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from app.worker.progress import JobProgress
from model_schema import ArtifactRef, JobKind, JobResult, RatingVersion
from model_schema.dislocation import DislocationRun, DislocationSpec
from pricing_core.progress import ProgressCallback
from pricing_core.rating.analysis import (
    _FRAME_COLUMNS,
    AttributionError,
    attribute,
    dislocation_frame,
    select_movers,
    summarise_dislocation,
)
from pricing_core.rating.compile import (
    ArtifactResolver,
    Bundle,
    ResolvedArtifact,
    compile_bundle,
)
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.safe_error import safe_error_text

__all__ = [
    "DISLOCATION_RATINGS_PER_WORKER_HOUR",
    "DISLOCATION_SINGLE_JOB_MAX_HOURS",
    "MOVERS_COLUMNS",
    "PreloadedResolver",
    "preload",
    "register_dislocation_handlers",
]

_PARQUET_MEDIA_TYPE = "application/vnd.apache.parquet"

#: The movers blob holds `dislocation_frame`'s own columns, `quote_id` through `origin_rung`,
#: and never a portfolio column (`RL-1504` item 5): `/movers` joins those at read.
MOVERS_COLUMNS: tuple[str, ...] = ("quote_id", *_FRAME_COLUMNS)


class PreloadedResolver:
    """Serves artifacts already resolved, with no I/O (DP-S4-4).

    A ref that was not preloaded raises `ValueError("NOT_FOUND: …")`, the form
    `compile_bundle`'s callers read as a named code.
    """

    def __init__(self, artifacts: Mapping[ArtifactRef, ResolvedArtifact]) -> None:
        self._artifacts = dict(artifacts)

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        try:
            return self._artifacts[ref]
        except KeyError:
            raise ValueError(f"NOT_FOUND: {ref} was not preloaded for this run") from None


class _Recorder:
    """Passes every resolution to `inner` and keeps what it returned."""

    def __init__(self, inner: ArtifactResolver) -> None:
        self._inner = inner
        self.seen: dict[ArtifactRef, ResolvedArtifact] = {}

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        resolved = await self._inner.resolve(ref)
        self.seen[ref] = resolved
        return resolved


async def preload(base: ArtifactResolver, versions: Iterable[RatingVersion]) -> PreloadedResolver:
    """Every artifact a compile of each of `versions` resolves, held in memory.

    The refs are those `compile_bundle` itself asks `base` for (the algorithm, every pin and
    the Factors a model pin reads), so no list of pin kinds is kept here to drift from it.
    Run inside the one `run_on_loop` call that has the database session.
    """
    recorder = _Recorder(base)
    for version in versions:
        await compile_bundle(version, recorder)
    return PreloadedResolver(recorder.seen)


@dataclass(frozen=True)
class _Loaded:
    """What `prepare` hands the worker thread: no session, no I/O left."""

    baseline: RatingVersion
    candidate: RatingVersion
    baseline_bundle: CompiledBundle
    candidate_bundle: CompiledBundle
    baseline_hash: str
    candidate_hash: str
    portfolio: pl.DataFrame
    resolver: PreloadedResolver


def _rating_version_ref(ref: ArtifactRef) -> ArtifactRef:
    if ref.type != "rating_version":
        raise PlatformError(
            "VALIDATION_FAILED", "Not a rating version reference", 422,
            f"{ref} is not a rating_version reference.",
        )
    return ref


async def _compiled(
    progress: JobProgress, session: Any, row: RatingVersionRow, ref: ArtifactRef
) -> tuple[CompiledBundle, str]:
    """The compiled bundle a version already holds, and its content hash (the regression
    handler's text for a version with none, `rating_handlers.py`)."""
    sha256 = (row.bundle or {}).get("blob_sha256")
    if not sha256:
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED", "Rating version is not compiled", 409,
            f"{ref} has no compiled bundle to run a dislocation against.",
        )
    payload = await read_stored_blob(
        session, progress.blob_store, sha256, f"{ref}'s compiled bundle"
    )
    bundle = Bundle.model_validate_json(payload)
    return load_bundle(bundle), bundle.content_hash


def _dislocation_run(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`dislocation.run` — Baseline vs candidate over a portfolio, with attribution (`03`
    §5.1, FR-263, FR-265, FR-266; `PL-1501` Task 4).

    Ends with `JobResult(kind="artifact", ref="dislocation_run:<row id>")`. An attribution
    refusal ends the Job `failed` with its own code (`BUNDLE_COMPILE_FAILED` for a subset that
    does not compile, `ATTRIBUTION_RECONCILIATION_FAILED` for a part that does not reconcile)
    and writes no row.
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    actor_id = UUID(parameters["actor"]["id"])
    spec = DislocationSpec.model_validate(parameters["spec"])
    baseline_ref = _rating_version_ref(spec.baseline_ref)
    candidate_ref = _rating_version_ref(spec.candidate_ref)
    progress.update(0.05, "loading")

    async def prepare() -> _Loaded:
        async with progress.database.session() as session:
            rows = [
                await rating_versions_service.resolve_rating_version_ref(
                    session, workspace_id=workspace_id, ref=ref
                )
                for ref in (baseline_ref, candidate_ref)
            ]
            baseline_bundle, baseline_hash = await _compiled(
                progress, session, rows[0], baseline_ref
            )
            candidate_bundle, candidate_hash = await _compiled(
                progress, session, rows[1], candidate_ref
            )
            version = await dataset_service.read_version(
                session, workspace_id=workspace_id, version_id=spec.portfolio_dataset_version_id
            )
            sha256 = portfolio_table(version)["blob"]["sha256"]
            portfolio = pl.read_parquet(
                io.BytesIO(
                    await read_stored_blob(
                        session, progress.blob_store, sha256, "The portfolio's table"
                    )
                )
            )
            baseline, candidate = (rating_versions_service.to_schema(r) for r in rows)
            resolver = await preload(
                WorkspaceResolver(session, workspace_id, progress.blob_store),
                (baseline, candidate),
            )
        return _Loaded(
            baseline, candidate, baseline_bundle, candidate_bundle, baseline_hash,
            candidate_hash, portfolio, resolver,
        )

    loaded = progress.run_on_loop(prepare())
    progress.check_cancelled()
    progress.update(0.2, "rating")
    lazy = loaded.portfolio.lazy()
    frame = dislocation_frame(loaded.baseline_bundle, loaded.candidate_bundle, lazy, spec)
    summary = summarise_dislocation(frame, spec)
    movers = select_movers(frame, spec).select(MOVERS_COLUMNS)

    progress.check_cancelled()
    progress.update(0.5, "attributing")
    try:
        attribution = asyncio.run(
            attribute(loaded.baseline, loaded.candidate, lazy, spec, loaded.resolver)
        )
    except AttributionError as exc:
        raise PlatformError(
            exc.code, exc.code.replace("_", " ").title(), 422, safe_error_text(exc)
        ) from exc
    progress.update(0.9, "persisting")

    async def persist() -> UUID:
        async with progress.database.unit_of_work() as session:
            buffer = io.BytesIO()
            movers.write_parquet(buffer, compression="zstd")
            blob = await progress.blob_store.put(session, buffer.getvalue(), _PARQUET_MEDIA_TYPE)
            run = DislocationRun.model_validate(
                {
                    **summary.model_dump(mode="json"),
                    **attribution.model_dump(mode="json"),
                    "largest_movers_blob": f"{MOVERS_BLOB_PREFIX}{blob.sha256}",
                    "job_id": str(progress.job_id),
                }
            )
            row = await persist_dislocation_run(
                session, workspace_id=workspace_id, run=run,
                baseline_bundle_hash=loaded.baseline_hash,
                candidate_bundle_hash=loaded.candidate_hash, actor_id=actor_id,
            )
            return row.id

    row_id = progress.run_on_loop(persist())
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"dislocation_run:{row_id}")


def register_dislocation_handlers() -> None:
    """Register the `dislocation.*` handlers.

    A function rather than import-time side effects, for `register_rating_handlers`'s reason:
    `register_handler` refuses a duplicate, and a module that registers on import cannot be
    imported twice.
    """
    if JobKind.DISLOCATION_RUN not in HANDLERS:
        register_handler(JobKind.DISLOCATION_RUN, _dislocation_run)
