"""`JobProgress` — the backend's implementation of pricing-core's callback (`07` §5.2).

ADR-0001 keeps `pricing-core` free of I/O, so it reports progress through an injected
callback whose protocol *it* owns. This is the implementation, and it has one awkward
property to solve: the protocol is **synchronous** — a fitting loop calls
`progress.update(...)` between boosting rounds — while the data layer is async.

The bridge is deliberate. The computation runs in a worker thread
(`asyncio.to_thread`), and the callback marshals each write back onto the event loop with
`run_coroutine_threadsafe`. The alternatives are worse: `asyncio.run()` inside the callback
creates a fresh loop per tick and detaches the engine's connections from it, and a second
synchronous SQLAlchemy stack would mean two implementations of the audit write — which is
exactly the split that produced a self-consistent, externally-invalid hash chain earlier in
W2.

Both writes are throttled. Without that, a tight loop calling `update()` a thousand times a
second turns a fit into a database benchmark.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Coroutine
from datetime import UTC, datetime
from typing import Any, Final
from uuid import UUID

from sqlalchemy import select, update

from app.db.models import JobRow
from app.db.session import Database
from app.observability.logging import get_logger
from app.platform.blobs import BlobStore
from pricing_core.progress import JobCancelled

__all__ = ["JobBudgetExceededError", "JobProgress"]

_log = get_logger("app.worker.progress")

#: NFR-PLAT-3 wants an update at least every 5 s. Writing more often than this buys
#: nothing a human can see, and the cost lands on the database the whole platform shares.
_MIN_WRITE_INTERVAL_S: Final = 1.0

#: How often a cancellation request is actually looked up. FR-PLAT-9 is cooperative, so
#: latency here is the delay between pressing cancel and the job stopping.
_MIN_CANCEL_POLL_S: Final = 2.0

#: A callback write that cannot complete in this time means the loop is wedged; failing
#: the job is better than a fitting thread blocked for ever on a progress update.
_WRITE_TIMEOUT_S: Final = 30.0


class JobBudgetExceededError(Exception):
    """The job exceeded its wall-clock budget (FR-PLAT-16).

    Distinct from `JobCancelled`: a cancelled job was stopped by a person and is not a
    failure, while a job that outran its budget is one, and the error must name the budget
    rather than surfacing as an opaque kill.
    """

    def __init__(self, wall_clock_s: int, elapsed_s: float) -> None:
        super().__init__(
            f"job exceeded its wall-clock budget of {wall_clock_s}s "
            f"(elapsed {elapsed_s:.0f}s)"
        )
        self.wall_clock_s = wall_clock_s
        self.elapsed_s = elapsed_s


class JobProgress:
    """Reports progress and observes cancellation for one running Job.

    Satisfies `pricing_core.progress.ProgressCallback` structurally — the core never
    imports this class, and this class never makes the core aware of a database.
    """

    def __init__(
        self,
        job_id: UUID,
        database: Database,
        loop: asyncio.AbstractEventLoop,
        *,
        wall_clock_s: int | None = None,
        blob_store: BlobStore | None = None,
    ) -> None:
        self._job_id = job_id
        self._database = database
        self._blob_store = blob_store
        self._loop = loop
        self._wall_clock_s = wall_clock_s
        self._started = time.monotonic()
        self._last_write = 0.0
        self._last_cancel_poll = 0.0
        self._cancelled = False

    # -- ProgressCallback ---------------------------------------------------------------

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        """Record progress (FR-PLAT-8). Throttled; the final call is not the caller's job."""
        now = time.monotonic()
        if now - self._last_write < _MIN_WRITE_INTERVAL_S:
            return
        self._last_write = now
        self._run(self._write_progress(fraction, stage, counters))

    def check_cancelled(self) -> None:
        """Raise `JobCancelled` if cancellation was requested, or the budget is spent.

        Called at points where `pricing-core` can stop without leaving a half-written
        artifact, which is what makes cancellation safe rather than merely fast.
        """
        self._check_budget()

        now = time.monotonic()
        if self._cancelled:
            raise JobCancelled(f"job {self._job_id} was cancelled")
        if now - self._last_cancel_poll < _MIN_CANCEL_POLL_S:
            return
        self._last_cancel_poll = now

        if self._run(self._read_cancellation()):
            self._cancelled = True
            raise JobCancelled(f"job {self._job_id} was cancelled")

    # -- the data-layer bridge, for handlers ---------------------------------------------

    @property
    def database(self) -> Database:
        """The data layer, for a handler that needs to read or write.

        A `pricing-core` handler needs neither and must not have either (ADR-0001). A
        *platform* handler — one that loads a version's parquet, stores a report — needs
        both, and giving it this rather than letting it build its own engine is what keeps
        one connection pool and one audit path.
        """
        return self._database

    @property
    def blob_store(self) -> BlobStore:
        """The object store, for a handler that reads or writes blobs.

        Supplied by the worker rather than built from ambient settings inside the handler.
        A handler that constructs its own reads whatever `GIP_BLOB_BUCKET` happens to be —
        which is a different bucket under test, and the symptom is `NoSuchKey` for an
        object that demonstrably exists.
        """
        if self._blob_store is None:
            raise RuntimeError(
                "this Job was started without a blob store; a handler that reads blobs "
                "needs one passed to execute_job()"
            )
        return self._blob_store

    def run_on_loop[T](self, coro: Coroutine[Any, Any, T]) -> T:
        """Run a coroutine on the owning loop, from the handler's worker thread.

        The same bridge `update()` uses, made public because handlers need it for exactly
        the same reason. Calling `asyncio.run()` here instead would create a fresh loop and
        detach the engine's connections from it — the symptom is
        `Future attached to a different loop`, some way from the cause.

        No write timeout: a handler's transaction is the work itself and may legitimately
        take minutes, where a progress write that blocks for two seconds is a fault.
        """
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    # -- internals ----------------------------------------------------------------------

    def _check_budget(self) -> None:
        if self._wall_clock_s is None:
            return
        elapsed = time.monotonic() - self._started
        if elapsed > self._wall_clock_s:
            raise JobBudgetExceededError(self._wall_clock_s, elapsed)

    def _run[T](self, coro: Coroutine[Any, Any, T]) -> T:
        """Run a coroutine on the owning loop from this (worker) thread."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(
            timeout=_WRITE_TIMEOUT_S
        )

    async def _write_progress(
        self, fraction: float, stage: str, counters: dict[str, int]
    ) -> None:
        payload = {"fraction": fraction, "stage": stage, "counters": counters}
        async with self._database.unit_of_work() as session:
            await session.execute(
                update(JobRow)
                .where(JobRow.id == self._job_id)
                .values(progress=payload, progress_at=datetime.now(UTC))
            )

    async def _read_cancellation(self) -> bool:
        async with self._database.session() as session:
            requested = (
                await session.execute(
                    select(JobRow.cancellation_requested_at).where(JobRow.id == self._job_id)
                )
            ).scalar_one_or_none()
        return requested is not None
