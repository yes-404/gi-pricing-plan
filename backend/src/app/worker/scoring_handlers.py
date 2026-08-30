"""`score.batch` — the batch scoring Job handler (`03` §3.7/§5.1/§5.2, FR-RATE-36/37/38;
W11 Task 3B).

**This is where the ruling lives — everything durable is here.** Task 3A's `score_batch`
(`pricing_core.rating.score`) is a pure, chunked `def` holding no state (Rulings 31 §3/5,
`docs/plans/2026-08-29-w11-3-d6-batch-resumability-ruling.md`); this module owns the four
things it structurally cannot: the manifest, the scratch parts, the abort threshold, and
the final content-addressed output.

## The manifest is the scratch key's own existence — no separate table

Ruling 31 §2 fixes the key: **the compiled bundle's content hash (FR-RATE-24), the Dataset
Version reference, and the chunk index** — never the Job id, because no terminal Job is
ever re-run (`VALID_TRANSITIONS` gives `failed` no outbound edge). Ruling 31 §7 leaves the
*storage shape* to the executor, naming *"a table, or scratch keys enumerated by
prefix"* as the two live options. This build takes the second: `BlobStore.write_scratch`/
`read_scratch` (Ruling 31 §4's "outside the content-addressed store", `blobs.py`'s own
`scratch/` prefix, never a `BlobRow`) at

    score-batch/{bundle.content_hash}/{dataset_version_id}/{chunk_index}

A chunk's manifest entry and its data are the same object: checking "is this chunk done"
*is* reading the key, so there is nothing to keep in step with a separate ledger. A
re-submission with the same parameters reproduces the identical key for every chunk — a
Dataset Version is immutable and a bundle hash is reproducible from its pins — so the
resumed run's first act, before scoring anything, is finding out how much of the key space
it can skip.

## One Job, one or more Rating Versions, one uniform result shape

FR-RATE-36 asks for *"a Dataset Version re-rated against one or more Rating Versions"*.
`score_batch` takes one `CompiledBundle` per call (`03` §5.2), so this handler loops
`rating_version_refs`, stamping the **resolved** ref into each frame it builds — never the
value a caller supplied, which `03` §4.8 rules is Task 3B's constraint to hold
(Ruling 43 §5(iii)): `CompiledBundle` carries no ref of its own, so nothing downstream of
resolution can check a mismatch, and reading `rating_version_ref` off the *dataset* would
let a parquet attribute premiums to a version that never computed them.

The Job's `JobResult` is always `kind="blob"`, pointing at one small JSON summary — never
`kind="artifact"` (no new persisted row type for this; there is nowhere Ruling 31 or the
frozen plan asks for one) and never a bare parquet ref (which cannot represent more than
one rating version). The summary lists, per ref: the output parquet's own blob ref, the row
count, the outcome counts, the per-category error counts and a few samples, and whether
that ref's run aborted. One shape regardless of how many refs were scored, rather than a
result whose type depends on the caller's own cardinality.

## Resolving a bundle reuses `app.api.score`'s resolver — never a second one

Ruling 42 (`docs/plans/2026-08-30-w11-reopen-scope-and-batch-frame-contract-rulings.md`)
put Ruling 41's NFR-RATE-1 remediation here deliberately, because this is the **second**
caller that needs a `rating_version_ref -> CompiledBundle` resolution, and
`app.api.score._compiled_for` is the only one in the repository. `CLAUDE.md` §2: *"Nobody
hand-writes a shape that already exists"* — a second resolver here would be exactly that,
and in a pricing platform a diverged shape is a mispricing. This handler's own
`BundleSlot` is local to one Job run (a fresh instance per invocation, capacity 1, unraised
per Ruling 41 §4) — it is not the API process's per-worker slot, and holds nothing across
Jobs.

## Errors are isolated per row by `score_batch` itself; this counts and, above a
## threshold, aborts

`score_batch`'s own output frame already turns a per-row failure into an `"error"` row
rather than raising (`pricing_core.rating.score`'s own module docstring) — that is the
structural half of FR-RATE-38 ("does not abort on individual failures"). What is left to
this handler is the **policy** half: counting `error_code` per category, sampling a few
messages, and comparing the running failure rate against the effective threshold
(`rating.batch_abort_failure_rate`, Ruling 24, `docs/plans/2026-08-29-w11-slices-3-4-
rulings.md`) after every chunk. A request's own `abort_failure_rate` argument may only
*lower* the resolved workspace setting — `01` FR-DATA-54's `severity_override` precedent —
refused with `BATCH_ABORT_THRESHOLD_ABOVE_SETTING` before a row is scored if it would
raise it. A run that crosses the effective threshold raises `BATCH_ABORTED`, naming both
numbers, rather than completing with a result that reads as clean.
"""

from __future__ import annotations

import io
import json
from typing import Any
from uuid import UUID

import polars as pl

from app.api.score import _compiled_for
from app.config import load_settings
from app.db.models import BlobRow
from app.errors import PlatformError
from app.platform import datasets as dataset_service
from app.platform import settings as settings_service
from app.platform.blobs import to_ref
from app.platform.bundle_slot import BundleSlot
from app.worker.data_handlers import _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from app.worker.progress import JobProgress
from model_schema import BlobRef, JobKind, JobResult
from model_schema.refs import ArtifactRef
from pricing_core.progress import ProgressCallback
from pricing_core.rating.score import score_batch

__all__ = ["register_scoring_handlers"]

#: `03` §5.2's default, mirrored here as the handler's own default chunk size — this is
#: also the manifest's granularity, so changing it between a run and its resumption
#: changes which keys a resumed run looks for and defeats resumability. Not validated
#: against a prior run's value: nothing records what a prior run used.
_DEFAULT_CHUNK_ROWS = 100_000

#: FR-RATE-38's five categories, plus the shape a batch row actually carries. Capped so a
#: pathological run with thousands of one kind of failure does not inflate the summary
#: blob past what a human reads.
_MAX_ERROR_SAMPLES = 5


def _scratch_key(content_hash: str, dataset_version_id: UUID, chunk_index: int) -> str:
    return f"score-batch/{content_hash}/{dataset_version_id}/{chunk_index}"


class _RefStats:
    """Running counts for one Rating Version's run, across all its chunks."""

    def __init__(self) -> None:
        self.row_count = 0
        self.outcome_counts: dict[str, int] = {"quoted": 0, "declined": 0, "error": 0}
        self.error_counts: dict[str, int] = {}
        self.error_samples: dict[str, list[str]] = {}

    def observe(self, chunk: pl.DataFrame) -> None:
        self.row_count += chunk.height
        for outcome, count in chunk["outcome"].value_counts().iter_rows():
            self.outcome_counts[outcome] = self.outcome_counts.get(outcome, 0) + count
        errors = chunk.filter(pl.col("outcome") == "error")
        for code, message in errors.select("error_code", "error_message").iter_rows():
            self.error_counts[code] = self.error_counts.get(code, 0) + 1
            samples = self.error_samples.setdefault(code, [])
            if len(samples) < _MAX_ERROR_SAMPLES:
                samples.append(message)

    @property
    def failure_rate(self) -> float:
        if self.row_count == 0:
            return 0.0
        return self.outcome_counts.get("error", 0) / self.row_count


async def _effective_threshold(
    session: Any, app_settings: Any, workspace_id: UUID, requested: float | None
) -> float | None:
    """`rating.batch_abort_failure_rate`'s three-layer resolution, plus the per-run
    argument (Ruling 24) — which is a Job argument, never a fourth resolution tier, and
    may only lower the resolved value."""
    resolution = await settings_service.resolve(
        session, app_settings, workspace_id, "rating.batch_abort_failure_rate"
    )
    workspace_threshold: float | None = resolution.effective_value
    if requested is None:
        return workspace_threshold
    if workspace_threshold is not None and requested > workspace_threshold:
        raise PlatformError(
            "BATCH_ABORT_THRESHOLD_ABOVE_SETTING",
            "Requested threshold exceeds the workspace setting",
            422,
            f"requested {requested} > workspace setting {workspace_threshold}. A batch "
            "request may only lower the effective abort threshold, never raise it.",
        )
    return requested


def _dataset_frame(table: pl.DataFrame, ref: ArtifactRef) -> pl.DataFrame:
    """The Dataset Version's chosen table, with `rating_version_ref` stamped to the
    **resolved** ref (Ruling 43 §5(iii), `03` §4.8) — overwriting whatever the table
    itself carries, since nothing about that value is trustworthy: `CompiledBundle` has
    no ref to check it against, so this handler is the only place that can make it agree
    with what is actually about to be scored."""
    return table.with_columns(pl.lit(str(ref)).alias("rating_version_ref"))


def _score_one_ref(
    *,
    progress: JobProgress,
    workspace_id: UUID,
    dataset_version_id: UUID,
    table: pl.DataFrame,
    ref: ArtifactRef,
    chunk_rows: int,
    effective_threshold: float | None,
    fraction_span: tuple[float, float],
) -> dict[str, Any]:
    """Score one Rating Version's chunks, synchronously — every individual database or
    blob operation goes through its own `progress.run_on_loop(...)` call, interleaved
    with plain sync `progress.check_cancelled()`/`update()` calls, exactly the shape
    `app/worker/model_handlers.py`'s fitting handlers already use and `pricing_core.
    modelling`'s own `report.check_cancelled()` call sites confirm from the other side.

    **Not one big `async def work()` awaited in a single `run_on_loop` call.**
    `JobProgress.check_cancelled()`/`update()` each do their own `run_coroutine_
    threadsafe(..., self._loop).result()` — a call that blocks until *that* coroutine
    runs on `self._loop`. Calling either of them from code that is *itself* already
    running on `self._loop` (which is exactly what happens inside a coroutine dispatched
    by an outer `run_on_loop`) deadlocks: the loop cannot service the inner scheduled
    coroutine while it is blocked waiting on the very call that would let it run. Verified
    live while building this task — the first cut nested `check_cancelled`/`update`
    inside one `async def work()` and every call hung until `JobProgress`'s own 30 s
    write timeout fired.
    """
    slot = BundleSlot()
    bundle = progress.run_on_loop(
        _compiled_for(
            progress.database, progress.blob_store, slot, workspace_id=workspace_id, ref=ref
        )
    )

    frame = _dataset_frame(table, ref)
    total_rows = frame.height
    n_chunks = max(1, -(-total_rows // chunk_rows)) if total_rows else 0

    stats = _RefStats()
    aborted = False
    scratch_keys: list[str] = []

    start_fraction, end_fraction = fraction_span
    for chunk_index in range(n_chunks):
        progress.check_cancelled()
        key = _scratch_key(bundle.content_hash, dataset_version_id, chunk_index)
        scratch_keys.append(key)

        existing = progress.run_on_loop(progress.blob_store.read_scratch(key))
        if existing is None:
            offset = chunk_index * chunk_rows
            chunk_lazy = frame.slice(offset, chunk_rows).lazy()
            chunk_frame = score_batch(bundle, chunk_lazy, chunk_rows=chunk_rows).collect()
            buffer = io.BytesIO()
            chunk_frame.write_parquet(buffer, compression="zstd")
            payload = buffer.getvalue()
            progress.run_on_loop(progress.blob_store.write_scratch(key, payload))
        else:
            payload = existing
            chunk_frame = pl.read_parquet(io.BytesIO(payload))

        stats.observe(chunk_frame)

        if effective_threshold is not None and stats.failure_rate > effective_threshold:
            aborted = True
            break

        if n_chunks:
            progress.update(
                start_fraction
                + (end_fraction - start_fraction) * ((chunk_index + 1) / n_chunks),
                "scoring",
                rows_scored=stats.row_count,
            )

    if aborted:
        for key in scratch_keys:
            progress.run_on_loop(progress.blob_store.delete_scratch(key))
        raise PlatformError(
            "BATCH_ABORTED",
            "Batch run aborted: failure rate exceeded the effective threshold",
            422,
            f"observed failure rate {stats.failure_rate:.4f} exceeded the effective "
            f"threshold {effective_threshold:.4f} for {ref}.",
        )

    parts: list[pl.DataFrame] = []
    for chunk_index in range(n_chunks):
        key = _scratch_key(bundle.content_hash, dataset_version_id, chunk_index)
        part_payload = progress.run_on_loop(progress.blob_store.read_scratch(key))
        assert part_payload is not None, f"manifest entry {key!r} vanished mid-run"
        parts.append(pl.read_parquet(io.BytesIO(part_payload)))

    output_ref: BlobRef | None = None
    if parts:
        combined = pl.concat(parts)
        buffer = io.BytesIO()
        combined.write_parquet(buffer, compression="zstd")

        async def _store_output() -> BlobRef:
            async with progress.database.unit_of_work() as session:
                return await progress.blob_store.put(
                    session, buffer.getvalue(), "application/x-parquet"
                )

        output_ref = progress.run_on_loop(_store_output())

    # Ruling 31 §4: chunk parts are released once the run completes — the output parquet
    # they were assembled into is what survives, content-addressed and reference-counted.
    for key in scratch_keys:
        progress.run_on_loop(progress.blob_store.delete_scratch(key))

    return {
        "rating_version_ref": str(ref),
        "output_blob_sha256": output_ref.sha256 if output_ref is not None else None,
        "row_count": stats.row_count,
        "outcome_counts": stats.outcome_counts,
        "error_counts": stats.error_counts,
        "error_samples": stats.error_samples,
        "aborted": False,
        "threshold": effective_threshold,
        "observed_failure_rate": stats.failure_rate,
    }


def _score_batch_handler(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`score.batch` (FR-RATE-36/37/38, `03` §5.1's `/score/batch` row — Task 3C's route
    submits this; Task 3B builds the handler and nothing that calls it yet)."""
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    dataset_version_id = UUID(parameters["dataset_version_id"])
    refs = [ArtifactRef.model_validate(r) for r in parameters["rating_version_refs"]]
    chunk_rows = int(parameters.get("chunk_rows") or _DEFAULT_CHUNK_ROWS)
    requested_threshold = parameters.get("abort_failure_rate")
    table_name = parameters.get("table_name")

    progress.update(0.0, "resolving")

    app_settings = load_settings()

    async def _resolve() -> tuple[float | None, bytes]:
        async with progress.database.session() as session:
            effective_threshold = await _effective_threshold(
                session, app_settings, workspace_id, requested_threshold
            )
            version = await dataset_service.load_version(
                session, workspace_id=workspace_id, version_id=dataset_version_id
            )
            entry = next(
                (t for t in version.tables if table_name is None or t["name"] == table_name),
                None,
            )
            if entry is None:
                raise PlatformError(
                    "NOT_FOUND",
                    "Scoring table not found",
                    404,
                    f"Dataset Version {dataset_version_id} has no table"
                    + (f" named {table_name!r}" if table_name else "")
                    + " to score.",
                )
            blob_row = await session.get(BlobRow, entry["blob"]["sha256"])
            if blob_row is None:
                raise PlatformError(
                    "NOT_FOUND",
                    "Scoring table's blob is missing",
                    404,
                    f"Dataset Version {dataset_version_id} names blob "
                    f"{entry['blob']['sha256']}, which is not in the store.",
                )
            blob = await progress.blob_store.read(to_ref(blob_row))
        return effective_threshold, blob

    effective_threshold, blob = progress.run_on_loop(_resolve())
    table = pl.read_parquet(io.BytesIO(blob))

    results: list[dict[str, Any]] = []
    for i, ref in enumerate(refs):
        progress.check_cancelled()
        span = (i / len(refs), (i + 1) / len(refs))
        result = _score_one_ref(
            progress=progress,
            workspace_id=workspace_id,
            dataset_version_id=dataset_version_id,
            table=table,
            ref=ref,
            chunk_rows=chunk_rows,
            effective_threshold=effective_threshold,
            fraction_span=span,
        )
        results.append(result)

    summary = {"dataset_version_id": str(dataset_version_id), "results": results}
    payload = json.dumps(summary).encode()

    async def _store_summary() -> str:
        async with progress.database.unit_of_work() as session:
            ref = await progress.blob_store.put(session, payload, "application/json")
        return ref.sha256

    summary_sha256 = progress.run_on_loop(_store_summary())
    progress.update(1.0, "done")
    return JobResult(kind="blob", ref=summary_sha256)


def register_scoring_handlers() -> None:
    """Register the `score.*` handlers — a function, not import-time side effects, for
    the same reason every other `register_*_handlers` here is one: `register_handler`
    refuses a duplicate, and a module that registers on import cannot be imported twice."""
    for kind, handler in ((JobKind.SCORE_BATCH, _score_batch_handler),):
        if kind not in HANDLERS:
            register_handler(kind, handler)
