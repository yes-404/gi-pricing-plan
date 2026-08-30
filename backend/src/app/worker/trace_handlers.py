"""`score.trace_produce` — the off-path re-score that completes a pending sampled trace
(`03` FR-RATE-42, W11 Task 4B; Ruling 35,
`docs/plans/2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md`).

The serving route (`app.api.score.score`) scores untraced and, on a sampled outcome, writes
a **pending** `scoring_traces` row (`app.platform.traces.write_pending_trace`) carrying the
Quote Context, then submits this Job with only that row's id — never the Quote Context
itself, which is the access-controlled carrier Ruling 35 §8.4 requires in place of
`JobRow.parameters` (a Job's `parameters` are a returned API field scoped only by
workspace, `backend/src/app/api/jobs.py:91`, and NFR-RATE-11 requires quote inputs stay
inside an access-controlled trace).

This handler reads the row, resolves the compiled bundle for `row.rating_version_ref`, and
**refuses to score it unless its `content_hash` still equals the pinned `row.bundle_hash`**
(Ruling 35 §8.2 condition (a): never address the live bundle in place of the pinned one — a
trace produced against a later bundle would silently document a quote that was never
served). Only once that holds does it re-score with `trace=True` and compare the
reproduction against what was actually served (condition (b)).

**Bundle resolution reuses `app.api.score._compiled_for`, never a second resolver**
(`CLAUDE.md` §2; the same reuse `app.worker.scoring_handlers` already established for
`score.batch`, Ruling 42).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.api.score import _compiled_for
from app.db.models import ScoringTraceRow
from app.errors import PlatformError
from app.platform import traces as traces_service
from app.platform.bundle_slot import BundleSlot
from app.worker.data_handlers import _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from model_schema import ArtifactRef, JobKind, JobResult, QuoteContext
from pricing_core.progress import ProgressCallback
from pricing_core.rating.score import score_one

__all__ = ["register_trace_handlers"]


def _score_trace_produce(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`score.trace_produce`: read the pending row, re-score the pinned bundle, complete it."""
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    trace_id = UUID(parameters["scoring_trace_id"])
    progress.update(0.0, "resolving")

    async def work() -> ScoringTraceRow:
        async with progress.database.unit_of_work() as session:
            row = await session.get(ScoringTraceRow, trace_id)
            if row is None:
                raise PlatformError(
                    "NOT_FOUND",
                    "Trace not found",
                    404,
                    f"No scoring trace with id {trace_id}.",
                )
            if row.workspace_id != workspace_id:
                # Defensive: a Job's `workspace_id` parameter is set by `job_identity`
                # from the same caller that wrote the row, so this should be unreachable
                # — but a row from another workspace is exactly the kind of mistake
                # NFR-RATE-11's access control exists to catch, not silently score.
                raise PlatformError(
                    "NOT_FOUND",
                    "Trace not found",
                    404,
                    f"Scoring trace {trace_id} does not belong to workspace {workspace_id}.",
                )
            if row.status != "pending":
                # Already completed by an earlier delivery of this Job (at-least-once
                # queueing). `complete_pending_trace` would refuse with `TRACE_NOT_PENDING`
                # — returning the settled row here is the same "nothing left to do"
                # outcome without treating a duplicate delivery as a failure.
                return row

            ctx = QuoteContext.model_validate(row.pending_quote_context)
            ref = ArtifactRef.model_validate(row.rating_version_ref)
            slot = BundleSlot()
            compiled = await _compiled_for(
                progress.database,
                progress.blob_store,
                slot,
                workspace_id=workspace_id,
                ref=ref,
            )

            if compiled.content_hash != row.bundle_hash:
                # Condition (a): the version has moved on since this quote was served.
                # Scoring the live bundle would document a quote nobody ever saw —
                # refused rather than silently substituted.
                return await traces_service.complete_pending_trace(
                    session, progress.blob_store, trace_id, None, reproduced_summary=None
                )

            result = await score_one(compiled, ctx, trace=True)
            reproduced_summary = traces_service.summarise_result(result)
            assert result.trace is not None  # `trace=True` always populates it (Slice 1)
            return await traces_service.complete_pending_trace(
                session,
                progress.blob_store,
                trace_id,
                result.trace,
                reproduced_summary=reproduced_summary,
            )

    progress.run_on_loop(work())
    progress.update(1.0, "done")
    # `kind="none"`: this Job's product is the trace row itself, read through
    # `GET /api/v1/traces` (Task 4C) — never through the Job's own result the way
    # `rating.compile`'s blob ref is, because the row is what carries the access control
    # NFR-RATE-11 requires and a bare blob ref in the Job result would bypass it. Whether
    # the row landed `complete` or `mismatch` is the row's own field, not this Job's
    # concern to duplicate into a result payload.
    return JobResult(kind="none")


def register_trace_handlers() -> None:
    """Register the `score.trace_produce` handler — a function, not import-time side
    effects, for the same reason every other `register_*_handlers` here is one:
    `register_handler` refuses a duplicate, and a module that registers on import cannot
    be imported twice."""
    for kind, handler in ((JobKind.SCORE_TRACE_PRODUCE, _score_trace_produce),):
        if kind not in HANDLERS:
            register_handler(kind, handler)
