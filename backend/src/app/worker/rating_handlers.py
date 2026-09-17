"""What the `rating.compile` Job actually does (`03` §5.1:514, FR-239/240, WK-671 Task 1.2).

The 202 endpoint submits these. `compile_rating_version` resolves the pinned algorithm
and every pin to real content and returns the full, self-contained `Bundle`; this handler
persists it as a blob and returns `JobResult(kind="blob")` with the sha256 as the ref —
the same shape `rate_table.diff` established for its own artifact. `GET /blobs/{sha256}`
is what a client fetches it back through.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.platform import audit
from app.platform import rating_versions as rating_versions_service
from app.worker.data_handlers import _actor, _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from model_schema import JobKind, JobResult, JobSource
from pricing_core.progress import ProgressCallback

__all__ = ["register_rating_handlers"]


def _rating_compile(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`rating.compile` — resolve pins to real content and persist the compiled Bundle.

    `job_identity` supplies `workspace_id`/`actor`; the 202 endpoint adds
    `rating_version_id`. The resolution itself may do real I/O (a rate table's cells, a
    reference table's rows, a GBM's booster blob), which is why this runs as a Job rather
    than inline on the request (RL-865).
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    actor = _actor(parameters)
    rating_version_id = UUID(parameters["rating_version_id"])
    progress.update(0.05, "compiling")

    async def work() -> str:
        async with progress.database.unit_of_work() as session:
            # Read the outgoing hash *before* compiling: `compile_rating_version` rebinds
            # `row.bundle` to the new summary on its way out, so after the call there is
            # nothing left to report as `before`. Captured as a value, not a reference to
            # the dict, for the same reason.
            row = await rating_versions_service.load_rating_version(
                session, workspace_id=workspace_id, rating_version_id=rating_version_id
            )
            prior_hash = (row.bundle or {}).get("content_hash")
            entity_ref = f"rating_version:{row.slug}@{row.version}"

            bundle = await rating_versions_service.compile_rating_version(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_store=progress.blob_store,
            )
            payload = bundle.model_dump_json().encode()
            ref = await progress.blob_store.put(session, payload, "application/json")
            # RL-915: the key goes on the version's own metadata, in this same
            # transaction. Without it the only record of where the bundle lives is this
            # Job's result — an operational row with its own pruning, so a trimmed Job
            # history would leave a compiled version unresolvable.
            #
            # **Before the audit write, deliberately**: the row reaches its final state
            # first, so the event that records the compile describes a completed one. It is
            # safe in either order — `prior_hash` and `entity_ref` were captured as values
            # above, and `after` reads locals rather than the row — but "finish the row,
            # then record what happened" is the sequence that stays correct if the audit
            # payload ever widens to include the key.
            #
            # This re-loads the row through the service that owns `row.bundle`'s shape;
            # within one session SQLAlchemy's identity map returns the object the handler
            # already holds, so there is no second query and no second copy to diverge.
            await rating_versions_service.record_bundle_blob(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_sha256=ref.sha256,
            )

            # NFR-498: compilations emit an Audit Event with before/after state.
            # Inside this `unit_of_work`, never its own: `06` R2 makes the audit write
            # share the caller's transaction, and `audit.record` refuses outright if there
            # is none — an event that committed independently could outlive a compile that
            # rolled back, and the chain would record something that never happened.
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=actor,
                # `JobSource` names where the *request* came from — its members are UI,
                # API, SCHEDULE, SYSTEM, all origins, none an executor — so a compile
                # submitted through `POST /rating-versions/{id}/compile` is `API` even
                # though the worker runs it. `dataset_version.ingested` sets the same
                # precedent from inside a worker handler (`data/ingestion.py:260`).
                source=JobSource.API,
                action="rating_version.compiled",
                entity_ref=entity_ref,
                before={"bundle_hash": prior_hash},
                # `blob_sha256` joins the after-state because RL-915 put it on the row
                # this event describes: without it the trail can say a compile happened and
                # what it hashed to, but not *which stored artifact* it produced — and
                # "which blob did this compile write" is exactly the question an audit of a
                # priced quote has to answer. Note it is the blob key, not
                # `bundle.content_hash`: different hashes of different things, and the
                # patterns keep them apart.
                after={
                    "bundle_hash": bundle.content_hash,
                    "bytes": len(payload),
                    "blob_sha256": ref.sha256,
                },
                job_id=progress.job_id,
            )
            return ref.sha256

    sha256 = progress.run_on_loop(work())
    progress.update(1.0, "done")
    return JobResult(kind="blob", ref=sha256)


def register_rating_handlers() -> None:
    """Register the `rating.*` handlers.

    A function rather than import-time side effects: `register_handler` refuses a
    duplicate (rightly), and a module that registers on import cannot be imported twice —
    which a test importing this module for a type would do. The `dataset.*`, `model.*`
    and `rate_table.*` handlers set the same precedent.
    """
    for kind, handler in ((JobKind.RATING_COMPILE, _rating_compile),):
        if kind not in HANDLERS:
            register_handler(kind, handler)
