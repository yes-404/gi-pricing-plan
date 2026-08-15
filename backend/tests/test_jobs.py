"""Job submission, idempotency and lifecycle (FR-PLAT-7/9/12), against a real database."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db.models import AuditEventRow, OutboxRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit, jobs
from model_schema import (
    ActorKind,
    JobKind,
    JobQueue,
    JobSource,
    JobStatus,
    Principal,
    new_uuid7,
)


@pytest.mark.req("FR-PLAT-7")
async def test_submit_creates_job_audit_and_outbox_in_one_transaction(
    database: Database, workspace_id, principal
) -> None:
    """The three writes that must be atomic — `06` R2 and FR-PLAT-51 together."""
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {"seed": 20260814}, principal,
            workspace_id=workspace_id,
        )

    assert job.status is JobStatus.QUEUED
    assert job.queue is JobQueue.COMPUTE
    assert job.finished_at is None

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
        intents = (
            await session.execute(select(OutboxRow).where(OutboxRow.job_id == job.id))
        ).scalars().all()

    assert [e.action for e in events] == ["job.submitted"]
    assert events[0].job_id == job.id
    assert len(intents) == 1
    assert intents[0].payload["job_id"] == str(job.id)


@pytest.mark.req("FR-PLAT-13")
async def test_kind_selects_the_worker_pool(database: Database, workspace_id, principal) -> None:
    """A model fit on the scoring pool starves the quote path, which has a 50 ms budget."""
    async with database.unit_of_work() as session:
        fit = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
        batch = await jobs.submit(
            session, JobKind.SCORE_BATCH, {}, principal, workspace_id=workspace_id
        )
        ingest = await jobs.submit(
            session, JobKind.DATASET_INGEST, {}, principal, workspace_id=workspace_id
        )
    assert (fit.queue, batch.queue, ingest.queue) == (
        JobQueue.COMPUTE, JobQueue.SCORING, JobQueue.IO
    )


@pytest.mark.req("FR-PLAT-13")
async def test_every_kind_has_a_queue() -> None:
    """Negative: a kind with no mapping routes nowhere and the job sits queued for ever."""
    assert set(jobs.DEFAULT_QUEUE_FOR_KIND) == set(JobKind)


@pytest.mark.req("FR-PLAT-12")
async def test_repeat_submission_returns_the_original_job(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        first = await jobs.submit(
            session, JobKind.MODEL_FIT, {"seed": 1}, principal,
            workspace_id=workspace_id, idempotency_key="k-1",
        )
    async with database.unit_of_work() as session:
        second = await jobs.submit(
            session, JobKind.MODEL_FIT, {"seed": 1}, principal,
            workspace_id=workspace_id, idempotency_key="k-1",
        )

    assert second.id == first.id

    async with database.session() as session:
        intents = (
            await session.execute(select(OutboxRow).where(OutboxRow.job_id == first.id))
        ).scalars().all()
    # The work must not be enqueued twice — that is the whole point of the key.
    assert len(intents) == 1


@pytest.mark.req("FR-PLAT-12")
async def test_reusing_a_key_with_different_parameters_is_a_conflict(
    database: Database, workspace_id, principal
) -> None:
    """Negative: silently returning the first job answers a question nobody asked."""
    async with database.unit_of_work() as session:
        await jobs.submit(
            session, JobKind.MODEL_FIT, {"seed": 1}, principal,
            workspace_id=workspace_id, idempotency_key="k-2",
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await jobs.submit(
                session, JobKind.MODEL_FIT, {"seed": 999}, principal,
                workspace_id=workspace_id, idempotency_key="k-2",
            )
    assert exc.value.code == "IDEMPOTENCY_KEY_CONFLICT"
    assert exc.value.status_code == 409


@pytest.mark.req("FR-PLAT-12")
async def test_the_same_key_in_another_workspace_is_a_different_job(
    database: Database, principal
) -> None:
    """Keys are scoped to a workspace, or one workspace can collide with another's."""
    a, b = new_uuid7(), new_uuid7()
    async with database.unit_of_work() as session:
        first = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=a, idempotency_key="shared"
        )
        second = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=b, idempotency_key="shared"
        )
    assert first.id != second.id


@pytest.mark.req("FR-PLAT-7")
async def test_lifecycle_transitions_are_enforced(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    async with database.unit_of_work() as session:
        running = await jobs.transition(session, job.id, JobStatus.RUNNING, actor=principal)
    assert running.started_at is not None

    async with database.unit_of_work() as session:
        from model_schema import JobResult

        done = await jobs.transition(
            session, job.id, JobStatus.SUCCEEDED, actor=principal,
            result=JobResult(kind="artifact", ref="model:motor-ad-frequency@7"),
        )
    assert done.finished_at is not None
    assert done.result is not None
    assert done.result.ref == "model:motor-ad-frequency@7"


@pytest.mark.req("FR-PLAT-7")
async def test_a_terminal_job_cannot_transition_again(
    database: Database, workspace_id, principal
) -> None:
    """Negative: a finished Job is provenance (FR-OVR-3); provenance that changes is not."""
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.RUNNING, actor=principal)
    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.FAILED, actor=principal)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await jobs.transition(session, job.id, JobStatus.RUNNING, actor=principal)
    assert exc.value.status_code == 409


@pytest.mark.req("FR-PLAT-9")
async def test_a_queued_job_cancels_immediately(
    database: Database, workspace_id, principal
) -> None:
    """No worker holds it, so there is nothing to cooperate with."""
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    async with database.unit_of_work() as session:
        cancelled = await jobs.request_cancellation(session, job.id, actor=principal)
    assert cancelled.status is JobStatus.CANCELLED
    assert cancelled.finished_at is not None


@pytest.mark.req("FR-PLAT-9")
async def test_a_running_job_is_marked_not_stopped(
    database: Database, workspace_id, principal
) -> None:
    """Cancellation is cooperative: reporting `cancelled` while the work still burns CPU
    shows a freed worker slot that is not free."""
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.RUNNING, actor=principal)
    async with database.unit_of_work() as session:
        marked = await jobs.request_cancellation(session, job.id, actor=principal)

    assert marked.status is JobStatus.RUNNING
    assert marked.finished_at is None

    async with database.session() as session:
        actions = [
            e.action
            for e in (
                await session.execute(
                    select(AuditEventRow)
                    .where(AuditEventRow.workspace_id == workspace_id)
                    .order_by(AuditEventRow.sequence)
                )
            ).scalars()
        ]
    assert "job.cancellation_requested" in actions


@pytest.mark.req("FR-PLAT-9")
async def test_a_finished_job_is_not_cancellable(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.CANCELLED, actor=principal)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await jobs.request_cancellation(session, job.id, actor=principal)
    assert exc.value.code == "JOB_NOT_CANCELLABLE"


@pytest.mark.req("FR-GOV-20")
async def test_every_lifecycle_change_is_audited_and_chained(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.RUNNING, actor=principal)
    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.SUCCEEDED, actor=principal)

    async with database.session() as session:
        assert await audit.verify_chain(session, workspace_id) == 3


@pytest.mark.req("FR-GOV-25")
async def test_a_system_principal_can_submit(database: Database, workspace_id) -> None:
    """FR-GOV-25: automated actions are audited identically to human ones."""
    system = Principal(kind=ActorKind.SYSTEM, display="scheduler")
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MONITOR_RUN, {}, system,
            workspace_id=workspace_id, source=JobSource.SCHEDULE,
        )
    assert job.submitted_by.kind is ActorKind.SYSTEM
    assert job.source is JobSource.SCHEDULE
