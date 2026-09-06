"""The transactional outbox (FR-406).

> Celery does **not** enlist in the database transaction — a task can be published to
> Redis and the surrounding transaction then roll back, leaving a worker acting on state
> that was never committed. Since audit writes share the caller's transaction (`06` R2),
> this would produce work with no audit record. Jobs are therefore enqueued through a
> **transactional outbox** … Publishing directly from inside a request transaction is
> refused at the service layer, not left to convention.

That last clause is why `publish_directly` exists and raises. A rule enforced only by code
review is a rule that holds until the first hurried change.

The trade is at-least-once delivery: a relay can publish and then fail before marking the
row, so the same job is delivered twice. That is the correct side to fail on — a duplicate
delivery is absorbed by an idempotent consumer, while a lost one leaves a job `queued`
forever with nothing to explain why.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OutboxRow, OutboxStatus
from app.db.session import Database
from app.observability.logging import get_logger
from model_schema import JobQueue

__all__ = ["Publisher", "enqueue", "publish_directly", "relay_once"]

_log = get_logger("app.outbox")


class Publisher(Protocol):
    """Sends a task to a broker. Celery's binding arrives with the worker."""

    async def publish(
        self, *, task: str, queue: JobQueue, payload: dict[str, Any]
    ) -> None: ...


async def enqueue(
    session: AsyncSession,
    *,
    job_id: UUID,
    queue: JobQueue,
    task: str,
    payload: dict[str, Any] | None = None,
) -> OutboxRow:
    """Record the intent to publish, in the caller's transaction.

    Nothing reaches the broker here. If the transaction rolls back, the intent disappears
    with the job and the audit event it was written beside — which is the entire point.
    """
    if not session.in_transaction():
        raise RuntimeError(
            "outbox.enqueue() requires an open transaction: the publish intent must be "
            "written with the change it belongs to, or the outbox guarantees nothing."
        )
    row = OutboxRow(job_id=job_id, queue=queue, task=task, payload=payload or {})
    session.add(row)
    await session.flush()
    return row


async def publish_directly(
    session: AsyncSession,
    publisher: Publisher,
    *,
    task: str,
    queue: JobQueue,
    payload: dict[str, Any],
) -> None:
    """Publish straight to the broker — refused while a transaction is open (FR-406).

    Kept as a real function so the refusal is a mechanism rather than a convention. The
    failure mode it prevents is not hypothetical: a broker publish is invisible to the
    database, so a later rollback leaves a worker processing a job that does not exist.
    """
    if session.in_transaction():
        raise RuntimeError(
            "refusing to publish from inside a database transaction (FR-406). "
            "Celery does not enlist in the transaction, so a rollback would leave a "
            "worker acting on state that was never committed — and, because audit writes "
            "share that transaction, with no audit record. Use outbox.enqueue() instead."
        )
    await publisher.publish(task=task, queue=queue, payload=payload)


async def relay_once(database: Database, publisher: Publisher, *, batch_size: int = 100) -> int:
    """Publish pending intents after commit. Returns how many were published.

    Each row is claimed with `FOR UPDATE SKIP LOCKED` so several relay processes can run
    without publishing the same row twice, and one slow publish does not block the others.

    A publish failure marks the row and moves on rather than aborting the batch: one
    unroutable task must not stop every other job in the queue from starting.
    """
    published = 0
    async with database.unit_of_work() as session:
        rows = (
            await session.execute(
                select(OutboxRow)
                .where(OutboxRow.status == OutboxStatus.PENDING)
                .order_by(OutboxRow.created_at)
                .limit(batch_size)
                .with_for_update(skip_locked=True)
            )
        ).scalars().all()

        for row in rows:
            try:
                await publisher.publish(task=row.task, queue=row.queue, payload=row.payload)
            except Exception as exc:
                row.attempts += 1
                row.last_error = f"{type(exc).__name__}: {exc}"[:2000]
                _log.warning(
                    "outbox publish failed",
                    extra={
                        "job_id": str(row.job_id),
                        "attempts": row.attempts,
                        "error_type": type(exc).__name__,
                    },
                )
                continue
            row.status = OutboxStatus.PUBLISHED
            row.published_at = datetime.now(UTC)
            published += 1

    return published
