"""FR-406 — a job is never published to a broker the database has not committed to."""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import select

from app.db.models import JobRow, OutboxRow, OutboxStatus
from app.db.session import Database
from app.platform import outbox
from model_schema import JobKind, JobQueue, JobSource, JobStatus, new_uuid7


class RecordingPublisher:
    """A broker that remembers instead of sending."""

    def __init__(self) -> None:
        self.published: list[dict[str, Any]] = []

    async def publish(self, *, task: str, queue: JobQueue, payload: dict[str, Any]) -> None:
        self.published.append({"task": task, "queue": queue, "payload": payload})


class BrokenPublisher:
    def __init__(self) -> None:
        self.calls = 0

    async def publish(self, *, task: str, queue: JobQueue, payload: dict[str, Any]) -> None:
        self.calls += 1
        raise ConnectionError("broker unreachable")


def _job(workspace_id, principal) -> JobRow:
    return JobRow(
        workspace_id=workspace_id,
        kind=JobKind.MODEL_FIT,
        status=JobStatus.QUEUED,
        queue=JobQueue.COMPUTE,
        source=JobSource.API,
        submitted_by=principal.model_dump(mode="json"),
        parameters={},
        retries={},
    )


@pytest.mark.req("FR-406")
async def test_publishing_inside_a_transaction_is_refused(
    database: Database, workspace_id
) -> None:
    """The rule is a mechanism, not a convention — that is what the requirement asks for."""
    publisher = RecordingPublisher()
    async with database.unit_of_work() as session:
        with pytest.raises(RuntimeError, match="refusing to publish"):
            await outbox.publish_directly(
                session, publisher, task="t", queue=JobQueue.COMPUTE, payload={}
            )
    assert publisher.published == []


@pytest.mark.req("FR-406")
async def test_publishing_outside_a_transaction_is_allowed(
    database: Database
) -> None:
    publisher = RecordingPublisher()
    async with database.session() as session:
        await outbox.publish_directly(
            session, publisher, task="t", queue=JobQueue.COMPUTE, payload={"a": 1}
        )
    assert len(publisher.published) == 1


@pytest.mark.req("FR-406")
async def test_enqueue_requires_a_transaction(database: Database) -> None:
    """Negative: an intent written outside the change's transaction guarantees nothing."""
    async with database.session() as session:
        with pytest.raises(RuntimeError, match="requires an open transaction"):
            await outbox.enqueue(
                session, job_id=new_uuid7(), queue=JobQueue.COMPUTE, task="t"
            )


@pytest.mark.req("FR-406")
async def test_rollback_discards_the_job_and_its_publish_intent_together(
    database: Database, workspace_id, principal
) -> None:
    """The failure the outbox exists to prevent: a worker acting on uncommitted state."""
    # PT012: the rollback must happen after both writes, inside the transaction.
    with pytest.raises(RuntimeError, match="deliberate"):  # noqa: PT012
        async with database.unit_of_work() as session:
            row = _job(workspace_id, principal)
            session.add(row)
            await session.flush()
            await outbox.enqueue(session, job_id=row.id, queue=row.queue, task="t")
            raise RuntimeError("deliberate failure before commit")

    async with database.session() as session:
        jobs = (
            await session.execute(select(JobRow).where(JobRow.workspace_id == workspace_id))
        ).scalars().all()
        intents = (
            await session.execute(select(OutboxRow).where(OutboxRow.task == "t"))
        ).scalars().all()
    assert jobs == []
    assert all(i.job_id != row.id for i in intents)


async def _drain(database: Database) -> None:
    """Publish every intent already pending, so a test starts from a known outbox.

    `relay_once` takes the **oldest** `batch_size` rows, and tests submit Jobs without ever
    running the relay — so pending intents accumulate across a session. Once the backlog
    passes the batch size, a test's own row is no longer in the batch and "was it
    published?" starts answering a question about the backlog instead.

    Found when the modelling tests grew: each fit now derives two split parts, and the
    accumulated intents pushed this file's subject rows out of the first hundred.
    """
    while await outbox.relay_once(database, RecordingPublisher()) > 0:
        pass


@pytest.mark.req("FR-406")
async def test_relay_publishes_pending_intents_after_commit(
    database: Database, workspace_id, principal
) -> None:
    await _drain(database)
    async with database.unit_of_work() as session:
        row = _job(workspace_id, principal)
        session.add(row)
        await session.flush()
        await outbox.enqueue(
            session, job_id=row.id, queue=row.queue, task="app.worker.run_job",
            payload={"job_id": str(row.id)},
        )

    publisher = RecordingPublisher()
    assert await outbox.relay_once(database, publisher) >= 1
    assert any(p["payload"].get("job_id") == str(row.id) for p in publisher.published)

    async with database.session() as session:
        stored = (
            await session.execute(select(OutboxRow).where(OutboxRow.job_id == row.id))
        ).scalar_one()
    assert stored.status is OutboxStatus.PUBLISHED
    assert stored.published_at is not None


@pytest.mark.req("FR-406")
async def test_a_published_intent_is_not_published_twice(
    database: Database, workspace_id, principal
) -> None:
    await _drain(database)
    async with database.unit_of_work() as session:
        row = _job(workspace_id, principal)
        session.add(row)
        await session.flush()
        await outbox.enqueue(session, job_id=row.id, queue=row.queue, task="app.worker.run_job")

    first = RecordingPublisher()
    await outbox.relay_once(database, first)
    second = RecordingPublisher()
    await outbox.relay_once(database, second)
    assert all(p["payload"].get("job_id") != str(row.id) for p in second.published)


@pytest.mark.req("FR-406")
async def test_a_failing_publish_is_recorded_and_retried_not_lost(
    database: Database, workspace_id, principal
) -> None:
    """One unroutable task must not stop every other job from starting."""
    async with database.unit_of_work() as session:
        row = _job(workspace_id, principal)
        session.add(row)
        await session.flush()
        await outbox.enqueue(session, job_id=row.id, queue=row.queue, task="app.worker.run_job")

    broken = BrokenPublisher()
    assert await outbox.relay_once(database, broken) == 0

    async with database.session() as session:
        stored = (
            await session.execute(select(OutboxRow).where(OutboxRow.job_id == row.id))
        ).scalar_one()
    assert stored.status is OutboxStatus.PENDING
    assert stored.attempts == 1
    assert "ConnectionError" in (stored.last_error or "")

    # Still pending, so a later relay picks it up — at-least-once, never never-once.
    recovered = RecordingPublisher()
    await outbox.relay_once(database, recovered)
    async with database.session() as session:
        stored = (
            await session.execute(select(OutboxRow).where(OutboxRow.job_id == row.id))
        ).scalar_one()
    assert stored.status is OutboxStatus.PUBLISHED
