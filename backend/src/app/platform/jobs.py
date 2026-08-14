"""Job submission and lifecycle (`07` §3.2, §5.2).

Every submission does exactly one transaction's worth of work:

    job row  +  audit event  +  outbox intent

all three or none. That is `06` R2 and FR-PLAT-51 combined, and it is the reason this
module has no `commit()` in it — the unit of work owns the boundary, so there is no way to
write two of the three and return success.

The `submit` signature follows `07` §5.2, with `workspace_id` added: FR-OVR-13 puts every
artifact in exactly one workspace, and a Job that does not name its own cannot be
authorised, listed, or audited into the right chain.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobRow
from app.errors import PlatformError
from app.observability.trace import current_trace_id
from app.platform import audit, outbox
from model_schema import (
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
    Job,
    JobError,
    JobKind,
    JobQueue,
    JobResult,
    JobSource,
    JobStatus,
    Principal,
    Progress,
    RetryState,
)

__all__ = [
    "CELERY_TASK",
    "DEFAULT_QUEUE_FOR_KIND",
    "request_cancellation",
    "submit",
    "to_schema",
    "transition",
]

#: Which worker pool runs each kind (FR-PLAT-13). `compute` is few and fat, `scoring` is
#: many and thin, `io` is network-bound; putting a model fit on the scoring pool starves
#: the quote path, which is the one with a 50 ms budget.
DEFAULT_QUEUE_FOR_KIND: dict[JobKind, JobQueue] = {
    JobKind.DATASET_INGEST: JobQueue.IO,
    JobKind.DATASET_VALIDATE: JobQueue.COMPUTE,
    JobKind.DATASET_PROFILE: JobQueue.COMPUTE,
    JobKind.DATASET_DERIVE: JobQueue.COMPUTE,
    JobKind.MODEL_FIT: JobQueue.COMPUTE,
    JobKind.MODEL_TRANSPARENCY: JobQueue.COMPUTE,
    JobKind.MODEL_BACKTEST: JobQueue.COMPUTE,
    JobKind.MODEL_COMPARE: JobQueue.COMPUTE,
    JobKind.OBJECTIVE_CERTIFY: JobQueue.COMPUTE,
    JobKind.RATING_COMPILE: JobQueue.DEFAULT,
    JobKind.RATING_REGRESSION: JobQueue.COMPUTE,
    JobKind.SCORE_BATCH: JobQueue.SCORING,
    JobKind.DISLOCATION_RUN: JobQueue.COMPUTE,
    JobKind.OPTIMISATION_RUN: JobQueue.COMPUTE,
    JobKind.GIPP_CHECK: JobQueue.COMPUTE,
    JobKind.MONITOR_RUN: JobQueue.DEFAULT,
    JobKind.DOSSIER_GENERATE: JobQueue.DEFAULT,
    JobKind.EXPORT_REGULATORY: JobQueue.IO,
    JobKind.BLOB_GC: JobQueue.IO,
}

#: The Celery task name the relay publishes. One entry point for every kind: the worker
#: dispatches on `kind` from the payload, so adding a kind does not add a task route.
CELERY_TASK = "app.worker.run_job"


async def submit(
    session: AsyncSession,
    kind: JobKind,
    parameters: dict[str, Any],
    principal: Principal,
    *,
    workspace_id: UUID,
    source: JobSource = JobSource.API,
    idempotency_key: str | None = None,
    queue: JobQueue | None = None,
) -> Job:
    """Create a queued Job, its audit event and its publish intent, in one transaction.

    Returns the *existing* Job when `idempotency_key` matches a recent submission
    (FR-PLAT-12) — a retried request must not start the work twice.
    """
    if idempotency_key is not None:
        existing = await _find_by_idempotency_key(
            session, workspace_id=workspace_id, key=idempotency_key
        )
        if existing is not None:
            _reject_if_parameters_differ(existing, kind, parameters, idempotency_key)
            return to_schema(existing)

    row = JobRow(
        workspace_id=workspace_id,
        kind=kind,
        status=JobStatus.QUEUED,
        queue=queue or DEFAULT_QUEUE_FOR_KIND[kind],
        source=source,
        submitted_by=principal.model_dump(mode="json"),
        idempotency_key=idempotency_key,
        parameters=parameters,
        retries=RetryState().model_dump(mode="json"),
        trace_id=current_trace_id(),
    )
    session.add(row)

    try:
        await session.flush()
    except IntegrityError:
        # Two concurrent submissions with the same key. The unique index is the arbiter —
        # a pre-check alone cannot close this window, however carefully it is written.
        raise PlatformError(
            "IDEMPOTENCY_KEY_CONFLICT",
            "Concurrent submission with the same idempotency key",
            409,
            "Another request with this Idempotency-Key is in flight. Retry to receive the "
            "original job.",
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=principal,
        source=source,
        action="job.submitted",
        entity_ref=f"job:{row.id}@1",
        after={"kind": kind.value, "status": JobStatus.QUEUED.value, "queue": row.queue.value},
        job_id=row.id,
    )

    await outbox.enqueue(
        session,
        job_id=row.id,
        queue=row.queue,
        task=CELERY_TASK,
        payload={"job_id": str(row.id), "kind": kind.value, "trace_id": current_trace_id()},
    )

    return to_schema(row)


async def _find_by_idempotency_key(
    session: AsyncSession, *, workspace_id: UUID, key: str
) -> JobRow | None:
    return (
        await session.execute(
            select(JobRow).where(
                JobRow.workspace_id == workspace_id, JobRow.idempotency_key == key
            )
        )
    ).scalar_one_or_none()


def _reject_if_parameters_differ(
    existing: JobRow, kind: JobKind, parameters: dict[str, Any], key: str
) -> None:
    """Same key, different request — the client has a bug and must be told.

    Silently returning the first Job would answer a question the caller did not ask, and
    silently starting a second would defeat the key. `07` §5.1 names the code for this.
    """
    if existing.kind == kind and existing.parameters == parameters:
        return
    raise PlatformError(
        "IDEMPOTENCY_KEY_CONFLICT",
        "Idempotency key reused with different parameters",
        409,
        f"Idempotency-Key {key!r} was used for job {existing.id} with different "
        "parameters. Use a new key for a different request.",
    )


async def transition(
    session: AsyncSession,
    job_id: UUID,
    to_status: JobStatus,
    *,
    actor: Principal,
    progress: Progress | None = None,
    result: JobResult | None = None,
    error: JobError | None = None,
) -> Job:
    """Move a Job along its lifecycle, refusing transitions FR-PLAT-7 does not allow.

    The audit event is written in the same transaction (`06` R2), so a status change that
    cannot be audited does not happen.
    """
    row = await session.get(JobRow, job_id, with_for_update=True)
    if row is None:
        raise PlatformError("NOT_FOUND", "Job not found", 404, f"No job with id {job_id}.")

    if to_status not in VALID_TRANSITIONS[row.status]:
        raise PlatformError(
            "JOB_NOT_CANCELLABLE" if to_status is JobStatus.CANCELLED else "VALIDATION_FAILED",
            "Invalid job transition",
            409,
            f"A job in status {row.status.value!r} cannot move to {to_status.value!r}.",
        )

    before = {"status": row.status.value}
    row.status = to_status
    if to_status is JobStatus.RUNNING:
        row.started_at = datetime.now(UTC)
    if to_status in TERMINAL_STATUSES:
        row.finished_at = datetime.now(UTC)
    if progress is not None:
        row.progress = progress.model_dump(mode="json")
    if result is not None:
        row.result = result.model_dump(mode="json")
    if error is not None:
        row.error = error.model_dump(mode="json")

    await session.flush()

    await audit.record(
        session,
        workspace_id=row.workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if actor.kind.value == "system" else JobSource.API,
        action=f"job.{to_status.value}",
        entity_ref=f"job:{row.id}@1",
        before=before,
        after={"status": to_status.value},
        job_id=row.id,
    )
    return to_schema(row)


async def request_cancellation(
    session: AsyncSession, job_id: UUID, *, actor: Principal
) -> Job:
    """Ask a Job to stop (FR-PLAT-9). Cancellation is cooperative.

    A `queued` Job is cancelled outright — no worker has it. A `running` Job is *marked*:
    it stays `running` until `pricing-core` reaches its next checkpoint and returns.
    Reporting `cancelled` immediately would show a freed worker slot that is still busy.
    """
    row = await session.get(JobRow, job_id, with_for_update=True)
    if row is None:
        raise PlatformError("NOT_FOUND", "Job not found", 404, f"No job with id {job_id}.")

    if row.status in TERMINAL_STATUSES:
        raise PlatformError(
            "JOB_NOT_CANCELLABLE",
            "Job is not cancellable",
            409,
            f"Job {job_id} has already finished with status {row.status.value!r}.",
        )

    if row.cancellation_requested_at is None:
        row.cancellation_requested_at = datetime.now(UTC)
        await session.flush()
        await audit.record(
            session,
            workspace_id=row.workspace_id,
            actor=actor,
            source=JobSource.API,
            action="job.cancellation_requested",
            entity_ref=f"job:{row.id}@1",
            before={"status": row.status.value},
            after={"cancellation_requested": True},
            job_id=row.id,
        )

    if row.status is JobStatus.QUEUED:
        return await transition(session, job_id, JobStatus.CANCELLED, actor=actor)
    return to_schema(row)


def is_stalled(row: JobRow, *, stall_seconds: int) -> bool:
    """A running Job that has said nothing for longer than the window (NFR-PLAT-3).

    Only `running` jobs can stall. A queued Job is waiting for a worker, which is a queue
    depth problem with its own signal; a finished one has stopped on purpose.
    """
    if row.status is not JobStatus.RUNNING:
        return False
    last = row.progress_at or row.started_at
    if last is None:
        return False
    return (datetime.now(UTC) - last).total_seconds() > stall_seconds


def to_schema(row: JobRow, *, stall_seconds: int | None = None) -> Job:
    """Convert the ORM row to the API shape (`07` §4.1)."""
    return Job(
        id=row.id,
        workspace_id=row.workspace_id,
        kind=row.kind,
        status=row.status,
        queue=row.queue,
        submitted_by=Principal.model_validate(row.submitted_by),
        source=row.source,
        idempotency_key=row.idempotency_key,
        parameters=row.parameters,
        progress=Progress.model_validate(row.progress) if row.progress else None,
        result=JobResult.model_validate(row.result) if row.result else None,
        error=JobError.model_validate(row.error) if row.error else None,
        trace_id=row.trace_id,
        progress_at=row.progress_at,
        stalled=(
            is_stalled(row, stall_seconds=stall_seconds) if stall_seconds is not None
            else False
        ),
        queued_at=row.queued_at,
        started_at=row.started_at,
        finished_at=row.finished_at,
        retries=RetryState.model_validate(row.retries) if row.retries else RetryState(),
    )
