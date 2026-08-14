"""The broker hop itself (FR-PLAT-22, FR-PLAT-51).

`test_worker.py` covers the lifecycle without a broker. This covers what only a real
broker can show: that a relayed outbox row becomes a message, on the right queue, in a
form a worker can read.
"""

from __future__ import annotations

import json

import pytest
from sqlalchemy import select

from app.config import Settings
from app.db.models import JobRow, OutboxRow, OutboxStatus
from app.db.session import Database
from app.platform import jobs, outbox
from app.worker.celery_app import TASK_RUN_JOB, build_celery
from app.worker.tasks import CeleryPublisher
from model_schema import JobKind, JobQueue, JobStatus, new_uuid7

QUEUE = "test-celery-queue"


@pytest.fixture
def celery_app(settings: Settings):
    """A Celery app against the compose Redis, skipping when it is not there."""
    import redis

    app = build_celery(settings)
    try:
        client = redis.Redis.from_url(settings.redis_url.get_secret_value())
        client.ping()
    except Exception as exc:
        pytest.skip(f"Redis not reachable: {type(exc).__name__}")
    client.delete(QUEUE, JobQueue.COMPUTE.value)
    yield app
    client.delete(QUEUE, JobQueue.COMPUTE.value)


@pytest.mark.req("FR-PLAT-22")
async def test_publisher_puts_a_readable_message_on_the_named_queue(
    celery_app, settings: Settings
) -> None:
    import redis

    publisher = CeleryPublisher(celery_app)
    job_id = str(new_uuid7())
    await publisher.publish(
        task=TASK_RUN_JOB,
        queue=JobQueue.COMPUTE,
        payload={"job_id": job_id, "kind": "model.fit", "trace_id": None},
    )

    client = redis.Redis.from_url(settings.redis_url.get_secret_value())
    raw = client.lpop(JobQueue.COMPUTE.value)
    assert raw is not None, "nothing was published to the compute queue"

    envelope = json.loads(raw)
    assert envelope["headers"]["task"] == TASK_RUN_JOB
    # kwargs travel base64-encoded in the body; the headers carry the routing facts.
    assert envelope["properties"]["delivery_info"]["routing_key"] == JobQueue.COMPUTE.value


@pytest.mark.req("FR-PLAT-51")
async def test_relay_publishes_a_committed_job_and_marks_it(
    database: Database, celery_app, settings: Settings, workspace_id, principal
) -> None:
    """End to end across the seam: submit in a transaction, relay after commit."""
    import redis

    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {"seed": 1}, principal, workspace_id=workspace_id
        )

    published = await outbox.relay_once(database, CeleryPublisher(celery_app))
    assert published >= 1

    async with database.session() as session:
        row = (
            await session.execute(select(OutboxRow).where(OutboxRow.job_id == job.id))
        ).scalar_one()
        job_row = await session.get(JobRow, job.id)
    assert row.status is OutboxStatus.PUBLISHED
    assert row.published_at is not None
    # The job itself has not moved — publishing is not running.
    assert job_row.status is JobStatus.QUEUED

    client = redis.Redis.from_url(settings.redis_url.get_secret_value())
    assert client.llen(JobQueue.COMPUTE.value) >= 1


@pytest.mark.req("FR-PLAT-51")
async def test_nothing_is_published_when_the_transaction_rolls_back(
    database: Database, celery_app, settings: Settings, workspace_id, principal
) -> None:
    """Negative, and the reason the outbox exists: a rollback must reach the broker too.

    Asserted against *this job's* row rather than a global count. A shared database means
    another test's pending row could make a count-based assertion pass for the wrong
    reason — and a test that passes by accident is the failure mode this suite keeps
    finding.
    """
    import redis

    client = redis.Redis.from_url(settings.redis_url.get_secret_value())
    before = client.llen(JobQueue.COMPUTE.value)
    rolled_back: dict[str, object] = {}

    # PT012: the rollback has to happen after the submit, inside the transaction.
    with pytest.raises(RuntimeError, match="deliberate"):  # noqa: PT012
        async with database.unit_of_work() as session:
            job = await jobs.submit(
                session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
            )
            rolled_back["id"] = job.id
            raise RuntimeError("deliberate failure after submit")

    await outbox.relay_once(database, CeleryPublisher(celery_app))

    async with database.session() as session:
        assert await session.get(JobRow, rolled_back["id"]) is None
        intent = (
            await session.execute(
                select(OutboxRow).where(OutboxRow.job_id == rolled_back["id"])
            )
        ).scalar_one_or_none()
    assert intent is None
    assert client.llen(JobQueue.COMPUTE.value) == before
