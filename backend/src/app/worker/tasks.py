"""The worker side of a Job (`07` §6, steps 4 to 6).

    Worker picks the Job from its queue → sets `running` → calls pricing-core with a
    JobProgress callback → persists the result → sets `succeeded` with the reference.

Every transition is audited in the same transaction as the change (`06` R2), which is why
this module goes through `app.platform.jobs` rather than writing job rows itself.

Two properties are load-bearing:

* **The task is idempotent.** The outbox delivers at least once (FR-PLAT-51), and
  `task_acks_late` means a worker killed mid-job leaves the message for redelivery. A
  second delivery for a Job that is no longer `queued` is a no-op, not a second run.
* **The trace continues.** The `trace_id` travels in the payload and is bound before any
  work starts, so the worker's log lines join the request that created the Job (R4).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

from celery import Celery

from app.config import Settings, load_settings
from app.db.models import JobRow
from app.db.session import Database
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.observability.trace import bind_trace_id, current_trace_id, reset_trace_id
from app.platform import jobs, outbox
from app.platform.blobs import BlobStore
from app.worker.celery_app import TASK_RELAY_OUTBOX, TASK_RUN_JOB, build_celery
from app.worker.handlers import handler_for
from app.worker.logs import JobLogCapture
from app.worker.progress import JobBudgetExceededError, JobProgress
from model_schema import (
    TERMINAL_STATUSES,
    ActorKind,
    JobError,
    JobQueue,
    JobResult,
    JobStatus,
    Principal,
)
from pricing_core.progress import JobCancelled

__all__ = ["CeleryPublisher", "create_worker", "execute_job"]

_log = get_logger("app.worker")

#: The worker acts as the platform, not as the person who submitted the Job. FR-GOV-25
#: audits automated actions identically to human ones, and attributing a worker's
#: transition to the submitter would put words in their mouth.
SYSTEM = Principal(kind=ActorKind.SYSTEM, display="worker")


class CeleryPublisher:
    """Publishes an outbox row to Celery. The only place the broker is touched.

    Lives here rather than in `app.platform.outbox` so the outbox stays broker-agnostic:
    the relay's guarantee is about transactions, not about Celery, and OQ-PLAT-1 could be
    revisited without rewriting it.
    """

    def __init__(self, celery: Celery) -> None:
        self._celery = celery

    async def publish(
        self, *, task: str, queue: JobQueue, payload: dict[str, Any]
    ) -> None:
        # `send_task` rather than importing the task: the API process publishes without
        # importing worker code, so it does not need pricing-core's dependencies.
        self._celery.send_task(task, kwargs=payload, queue=queue.value)


async def execute_job(
    database: Database, job_id: UUID, blob_store: BlobStore | None = None
) -> JobStatus:
    """Run one Job to a terminal state. Returns the status it reached.

    Separated from the Celery task so the whole lifecycle is testable without a broker —
    the task is a five-line adapter and this is where the behaviour lives.
    """
    async with database.session() as session:
        row = await session.get(JobRow, job_id)

    if row is None:
        _log.warning("job not found; ignoring delivery", extra={"job_id": str(job_id)})
        return JobStatus.FAILED

    if row.status in TERMINAL_STATUSES:
        # A redelivery after the job already finished. At-least-once delivery makes this
        # normal rather than exceptional, so it is logged at info and ignored.
        _log.info(
            "job already finished; ignoring redelivery",
            extra={"job_id": str(job_id), "status": row.status.value},
        )
        return row.status

    if row.status is not JobStatus.QUEUED:
        _log.info(
            "job is not queued; another worker holds it",
            extra={"job_id": str(job_id), "status": row.status.value},
        )
        return row.status

    if row.cancellation_requested_at is not None:
        # Cancelled between submission and pickup — the common case, and no work should
        # start for it.
        async with database.unit_of_work() as session:
            await jobs.transition(session, job_id, JobStatus.CANCELLED, actor=SYSTEM)
        return JobStatus.CANCELLED

    handler = handler_for(row.kind)
    if handler is None:
        await _fail(
            database,
            job_id,
            JobError(
                code="JOB_HANDLER_NOT_REGISTERED",
                message=f"No handler is registered for job kind {row.kind.value!r}.",
                retryable=False,
                detail={"kind": row.kind.value},
                trace_id=current_trace_id(),
            ),
        )
        return JobStatus.FAILED

    async with database.unit_of_work() as session:
        await jobs.transition(session, job_id, JobStatus.RUNNING, actor=SYSTEM)

    budget = (row.resource_budget or {}).get("wall_clock_s")
    progress = JobProgress(
        job_id,
        database,
        asyncio.get_running_loop(),
        wall_clock_s=budget,
        # Built here, once, when the caller did not supply one. A handler building its own
        # picks up ambient settings and reads a different bucket than the one written to.
        blob_store=blob_store or BlobStore(load_settings()),
    )
    # **`job_id` is injected by the runner, not carried in the payload.** Three handlers
    # already read `parameters.get("job_id")` to stamp the artifact they produce with the Job
    # that produced it — and no caller ever put it there, so `diagnostics.job_id`,
    # `models.job_id` and every artifact's provenance link were silently always NULL. Found
    # 2026-08-17 by the comparison slice, whose artifact is keyed on it.
    #
    # The runner is authoritative and overrides a payload that supplies one: a handler
    # stamping an artifact with somebody else's Job id is worse than one stamping nothing.
    parameters = dict(row.parameters) | {"job_id": str(job_id)}

    # FR-PLAT-10: captured for the duration of this Job only. Attached to the root logger
    # so a handler's own log calls are collected without it knowing it is being watched.
    capture = JobLogCapture(job_id, database)
    logging.getLogger().addHandler(capture)

    try:
        try:
            # In a thread: the handler is synchronous CPU-bound `pricing-core` code, and
            # running it on the loop would block the very progress writes its callback makes.
            result: JobResult = await asyncio.to_thread(handler, parameters, progress)
        except JobCancelled:
            async with database.unit_of_work() as session:
                await jobs.transition(session, job_id, JobStatus.CANCELLED, actor=SYSTEM)
            return JobStatus.CANCELLED
        except JobBudgetExceededError as exc:
            await _fail(
                database,
                job_id,
                JobError(
                    code="JOB_RESOURCE_BUDGET_EXCEEDED",
                    message=str(exc),
                    retryable=False,
                    detail={"wall_clock_s": exc.wall_clock_s, "elapsed_s": round(exc.elapsed_s)},
                    trace_id=current_trace_id(),
                ),
            )
            return JobStatus.FAILED
        except PlatformError as exc:
            # **Before the generic clause, and that order is load-bearing** (OQ-PLAT-7,
            # decided 2026-08-22). `PlatformError`, `JobCancelled` and
            # `JobBudgetExceededError` are three independent direct subclasses of
            # `Exception` — none is a subclass of another, so the two clauses above are
            # genuinely siblings and their order is free. `except Exception` is not: it is
            # a base of `PlatformError`, so placing this clause after it would never run,
            # and every named handler error would keep arriving as `JOB_HANDLER_FAILED`.
            #
            # Why it exists at all: FR-PLAT-11 makes the *code* the contract, and
            # `PlatformError.__init__` calls `super().__init__(detail or title)`, so
            # `str(exc)` is the prose and never the code. Falling through stored
            # `JOB_HANDLER_FAILED` with a message that is not even a substring match for
            # the code the handler raised, and no caller could branch on the refusal —
            # two W5 refusal tests had to bypass `execute_job` entirely to assert one.
            #
            # `retryable` stays `False`, exactly as the generic clause sets it: a
            # `PlatformError` is a deterministic refusal, and FR-PLAT-11 does not retry
            # those. Nothing here infers retryability from `status_code` — a 429 or a 503
            # raised by a handler is still a deterministic refusal of *this* job.
            _log.exception(
                "job handler failed",
                extra={"job_id": str(job_id), "code": exc.code},
            )
            await _fail(
                database,
                job_id,
                JobError(
                    code=exc.code,
                    message=exc.detail or exc.title,
                    retryable=False,
                    trace_id=current_trace_id(),
                ),
            )
            return JobStatus.FAILED
        except Exception as exc:
            # Reached only by a genuinely unexpected exception now — a handler bug rather
            # than a refusal the handler named. The message is the exception's, not the
            # caller's input: FR-PLAT-11 wants a human message, and R3 keeps secrets out —
            # a handler that puts a credential in an exception string is a bug in the
            # handler, and the type name alone would leave an operator with nothing to act
            # on.
            _log.exception("job handler failed", extra={"job_id": str(job_id)})
            await _fail(
                database,
                job_id,
                JobError(
                    code="JOB_HANDLER_FAILED",
                    message=f"{type(exc).__name__}: {exc}",
                    retryable=False,
                    trace_id=current_trace_id(),
                ),
            )
            return JobStatus.FAILED

        async with database.unit_of_work() as session:
            await jobs.transition(
                session, job_id, JobStatus.SUCCEEDED, actor=SYSTEM, result=result
            )
        return JobStatus.SUCCEEDED
    finally:
        # Detach before flushing: the flush writes through the same logger tree,
        # and a handler still attached would capture its own writes.
        logging.getLogger().removeHandler(capture)
        await capture.flush_to_database()



async def _fail(database: Database, job_id: UUID, error: JobError) -> None:
    async with database.unit_of_work() as session:
        await jobs.transition(session, job_id, JobStatus.FAILED, actor=SYSTEM, error=error)


def create_worker(settings: Settings | None = None) -> Celery:
    """Build the Celery app with its tasks registered.

    A factory rather than a module-level app: importing this module must not open a broker
    connection, or every test and every tooling script that touches worker code needs
    Redis running.
    """
    settings = settings or load_settings()
    celery = build_celery(settings)

    @celery.task(name=TASK_RUN_JOB, bind=True)
    def run_job(self: Any, *, job_id: str, kind: str, trace_id: str | None = None) -> str:
        """Adapter: bind the trace, then run the lifecycle.

        `asyncio.run` per task is deliberate. A long-lived loop shared across tasks would
        bind the engine's connections to it, and a worker child process that forks (the
        prefork pool default) inherits a loop it must not use. Jobs are long-running by
        definition — that is what makes them Jobs — so a connection per Job is not the cost
        that matters.
        """
        token = bind_trace_id(trace_id) if trace_id else None
        try:
            database = Database(settings)

            async def _run() -> str:
                try:
                    status = await execute_job(database, UUID(job_id))
                finally:
                    await database.dispose()
                return status.value

            return asyncio.run(_run())
        finally:
            if token is not None:
                reset_trace_id(token)

    @celery.task(name=TASK_RELAY_OUTBOX)
    def relay_outbox() -> int:
        """Publish committed outbox rows (FR-PLAT-51).

        Runs on a schedule rather than being triggered by the writer: the writer is inside
        a transaction and must not touch the broker, which is the whole point.
        """
        database = Database(settings)

        async def _relay() -> int:
            try:
                return await outbox.relay_once(database, CeleryPublisher(celery))
            finally:
                await database.dispose()

        return asyncio.run(_relay())

    # Bound to the app by the decorators above; named here so a reader can see what
    # this factory actually registers.
    assert celery.tasks[TASK_RUN_JOB] is not None
    assert celery.tasks[TASK_RELAY_OUTBOX] is not None
    return celery
