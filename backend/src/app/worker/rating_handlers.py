"""What the `rating.compile` Job actually does (`03` §5.1:514, FR-RATE-24/25, W11 Task 1.2).

The 202 endpoint submits these. `compile_rating_version` resolves the pinned algorithm
and every pin to real content and returns the full, self-contained `Bundle`; this handler
persists it as a blob and returns `JobResult(kind="blob")` with the sha256 as the ref —
the same shape `rate_table.diff` established for its own artifact. `GET /blobs/{sha256}`
is what a client fetches it back through.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.platform import rating_versions as rating_versions_service
from app.worker.data_handlers import _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from model_schema import JobKind, JobResult
from pricing_core.progress import ProgressCallback

__all__ = ["register_rating_handlers"]


def _rating_compile(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`rating.compile` — resolve pins to real content and persist the compiled Bundle.

    `job_identity` supplies `workspace_id`/`actor`; the 202 endpoint adds
    `rating_version_id`. The resolution itself may do real I/O (a rate table's cells, a
    reference table's rows, a GBM's booster blob), which is why this runs as a Job rather
    than inline on the request (Ruling 2).
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    rating_version_id = UUID(parameters["rating_version_id"])
    progress.update(0.05, "compiling")

    async def work() -> str:
        async with progress.database.unit_of_work() as session:
            bundle = await rating_versions_service.compile_rating_version(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_store=progress.blob_store,
            )
            payload = bundle.model_dump_json().encode()
            ref = await progress.blob_store.put(session, payload, "application/json")
            # Ruling 37: the key goes on the version's own metadata, in this same
            # transaction. Without it the only record of where the bundle lives is this
            # Job's result — an operational row with its own pruning, so a trimmed Job
            # history would leave a compiled version unresolvable.
            await rating_versions_service.record_bundle_blob(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_sha256=ref.sha256,
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
