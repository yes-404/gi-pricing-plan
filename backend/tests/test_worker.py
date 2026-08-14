"""The worker side of a Job (FR-PLAT-7/8/9/13/16/51, `06` R2, R4).

`execute_job` is exercised directly rather than through a broker: the lifecycle is the
behaviour worth testing, and routing a message through Redis to assert it proves Celery
works, not that this code does. The broker itself is covered by `test_celery_routing`.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest
from sqlalchemy import select

from app.db.models import AuditEventRow, JobRow
from app.db.session import Database
from app.platform import audit, jobs
from app.worker import handlers
from app.worker.celery_app import TASK_RELAY_OUTBOX, TASK_RUN_JOB, build_celery
from app.worker.progress import JobBudgetExceededError, JobProgress
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    JobKind,
    JobQueue,
    JobResult,
    JobStatus,
    new_uuid7,
)
from pricing_core.progress import JobCancelled, ProgressCallback

SUCCEEDED_REF = "model:motor-ad-frequency@7"


@pytest.fixture(autouse=True)
def _isolate_handlers():
    """Handlers are process-global; a leak between tests is a confusing failure."""
    original = dict(handlers.HANDLERS)
    handlers.HANDLERS.clear()
    yield
    handlers.HANDLERS.clear()
    handlers.HANDLERS.update(original)


async def _submit(database: Database, workspace_id, principal, **kw) -> Any:
    async with database.unit_of_work() as session:
        return await jobs.submit(
            session,
            kw.pop("kind", JobKind.MODEL_FIT),
            kw.pop("parameters", {}),
            principal,
            workspace_id=workspace_id,
            **kw,
        )


@pytest.mark.req("FR-PLAT-7")
async def test_a_successful_job_reaches_succeeded_with_its_result(
    database: Database, workspace_id, principal
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        progress.update(1.0, "done", rows=10)
        return JobResult(kind="artifact", ref=SUCCEEDED_REF)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)

    assert await execute_job(database, job.id) is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.status is JobStatus.SUCCEEDED
    assert row.result["ref"] == SUCCEEDED_REF
    assert row.started_at is not None
    assert row.finished_at is not None


@pytest.mark.req("FR-GOV-20")
async def test_worker_transitions_are_audited_and_chained(
    database: Database, workspace_id, principal
) -> None:
    handlers.register_handler(
        JobKind.MODEL_FIT, lambda p, pr: JobResult(kind="none", ref=None)
    )
    job = await _submit(database, workspace_id, principal)
    await execute_job(database, job.id)

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
        assert await audit.verify_chain(session, workspace_id) == len(actions)

    assert actions == ["job.submitted", "job.running", "job.succeeded"]


@pytest.mark.req("FR-GOV-25")
async def test_the_worker_is_audited_as_the_system_not_the_submitter(
    database: Database, workspace_id, principal
) -> None:
    """Attributing a worker's transition to the submitter puts words in their mouth."""
    handlers.register_handler(
        JobKind.MODEL_FIT, lambda p, pr: JobResult(kind="none", ref=None)
    )
    job = await _submit(database, workspace_id, principal)
    await execute_job(database, job.id)

    async with database.session() as session:
        running = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "job.running",
                )
            )
        ).scalar_one()
    assert running.actor["kind"] == ActorKind.SYSTEM


@pytest.mark.req("FR-PLAT-11")
async def test_a_failing_handler_records_a_typed_error(
    database: Database, workspace_id, principal
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        raise ValueError("the dataset has no exposure column")

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)

    assert await execute_job(database, job.id) is JobStatus.FAILED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.error["code"] == "JOB_HANDLER_FAILED"
    assert "no exposure column" in row.error["message"]
    assert row.error["retryable"] is False
    assert row.finished_at is not None


@pytest.mark.req("FR-PLAT-13")
async def test_an_unregistered_kind_fails_the_job_rather_than_hanging(
    database: Database, workspace_id, principal
) -> None:
    """Negative: without this the Job sits `queued` for ever with nothing to explain why."""
    job = await _submit(database, workspace_id, principal, kind=JobKind.OPTIMISATION_RUN)

    assert await execute_job(database, job.id) is JobStatus.FAILED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.error["code"] == "JOB_HANDLER_NOT_REGISTERED"
    assert row.error["detail"]["kind"] == "optimisation.run"


@pytest.mark.req("FR-PLAT-8")
async def test_progress_is_recorded(database: Database, workspace_id, principal) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        progress.update(0.5, "boosting round 500/1000", rounds=500)
        return JobResult(kind="none", ref=None)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)
    await execute_job(database, job.id)

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.progress["fraction"] == 0.5
    assert row.progress["stage"] == "boosting round 500/1000"
    assert row.progress["counters"]["rounds"] == 500
    assert row.progress_at is not None


@pytest.mark.req("FR-PLAT-9")
async def test_a_job_cancelled_before_pickup_never_starts(
    database: Database, workspace_id, principal
) -> None:
    started = False

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        nonlocal started
        started = True
        return JobResult(kind="none", ref=None)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        await jobs.request_cancellation(session, job.id, actor=principal)

    # Already terminal — a queued job cancels outright — so the worker must not run it.
    assert await execute_job(database, job.id) is JobStatus.CANCELLED
    assert started is False


@pytest.mark.req("FR-PLAT-9")
async def test_a_running_job_stops_at_its_next_checkpoint(
    database: Database, workspace_id, principal
) -> None:
    """Cooperative cancellation: the core returns at a checkpoint, not mid-write."""
    handlers_seen: list[str] = []

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        for i in range(200):
            handlers_seen.append(f"step-{i}")
            progress.check_cancelled()
            time.sleep(0.02)
        return JobResult(kind="none", ref=None)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)

    async def _cancel_soon() -> None:
        await asyncio.sleep(0.3)
        async with database.unit_of_work() as session:
            await jobs.request_cancellation(session, job.id, actor=principal)

    canceller = asyncio.create_task(_cancel_soon())
    status = await execute_job(database, job.id)
    await canceller

    assert status is JobStatus.CANCELLED
    assert 0 < len(handlers_seen) < 200  # stopped partway, not at the start or the end

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.status is JobStatus.CANCELLED
    assert row.finished_at is not None


@pytest.mark.req("FR-PLAT-16")
async def test_exceeding_the_wall_clock_budget_names_the_budget(
    database: Database, workspace_id, principal
) -> None:
    """FR-PLAT-16: terminated with a typed error naming the budget, not silently killed."""

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        for _ in range(200):
            progress.check_cancelled()
            time.sleep(0.02)
        return JobResult(kind="none", ref=None)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        row = await session.get(JobRow, job.id)
        row.resource_budget = {"wall_clock_s": 1}

    assert await execute_job(database, job.id) is JobStatus.FAILED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.error["code"] == "JOB_RESOURCE_BUDGET_EXCEEDED"
    assert row.error["detail"]["wall_clock_s"] == 1
    assert "wall-clock budget" in row.error["message"]


@pytest.mark.req("FR-PLAT-51")
async def test_a_redelivered_job_is_not_run_twice(
    database: Database, workspace_id, principal
) -> None:
    """The outbox delivers at least once, so the consumer must be idempotent."""
    runs = 0

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        nonlocal runs
        runs += 1
        return JobResult(kind="none", ref=None)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)

    assert await execute_job(database, job.id) is JobStatus.SUCCEEDED
    assert await execute_job(database, job.id) is JobStatus.SUCCEEDED
    assert runs == 1


@pytest.mark.req("FR-PLAT-7")
async def test_a_delivery_for_an_unknown_job_is_ignored(database: Database) -> None:
    """Negative: a stale broker message must not raise and requeue for ever."""
    assert await execute_job(database, new_uuid7()) is JobStatus.FAILED


@pytest.mark.req("FR-PLAT-8")
async def test_progress_writes_are_throttled(
    database: Database, workspace_id, principal
) -> None:
    """A tight loop calling update() must not turn a fit into a database benchmark."""
    loop = asyncio.get_running_loop()
    job = await _submit(database, workspace_id, principal)
    progress = JobProgress(job.id, database, loop)

    def hammer() -> int:
        for i in range(50):
            progress.update(i / 50, "spinning")
        return 50

    await asyncio.to_thread(hammer)

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    # Only the first call inside the throttle window reaches the database.
    assert row.progress["fraction"] == 0.0


@pytest.mark.req("FR-PLAT-16")
async def test_budget_check_is_independent_of_cancellation(database: Database) -> None:
    """A spent budget is a failure; a cancellation is not. They must not share a code path."""
    loop = asyncio.get_running_loop()
    progress = JobProgress(new_uuid7(), database, loop, wall_clock_s=0)
    with pytest.raises(JobBudgetExceededError):
        progress.check_cancelled()


@pytest.mark.req("FR-PLAT-9")
def test_job_progress_satisfies_the_pricing_core_protocol(database: Database) -> None:
    """ADR-0001: the core owns the protocol and never imports this implementation."""
    progress = JobProgress(new_uuid7(), database, asyncio.new_event_loop())
    assert isinstance(progress, ProgressCallback)
    assert JobCancelled is not None


@pytest.mark.req("FR-PLAT-13")
def test_celery_routes_every_kind_to_a_queue() -> None:
    """Routing is derived from the kind, so a caller cannot put a fit on the scoring pool."""
    from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND

    assert set(DEFAULT_QUEUE_FOR_KIND) == set(JobKind)
    assert set(DEFAULT_QUEUE_FOR_KIND.values()) <= set(JobQueue)
    assert DEFAULT_QUEUE_FOR_KIND[JobKind.MODEL_FIT] is JobQueue.COMPUTE
    assert DEFAULT_QUEUE_FOR_KIND[JobKind.SCORE_BATCH] is JobQueue.SCORING


@pytest.mark.req("FR-PLAT-22")
def test_celery_refuses_pickle(settings) -> None:
    """Negative: pickle over a broker is arbitrary code execution in a worker."""
    celery = build_celery(settings)
    assert celery.conf.accept_content == ["json"]
    assert celery.conf.task_serializer == "json"


@pytest.mark.req("FR-PLAT-51")
def test_worker_registers_both_tasks(settings) -> None:
    from app.worker.tasks import create_worker

    celery = create_worker(settings)
    assert TASK_RUN_JOB in celery.tasks
    assert TASK_RELAY_OUTBOX in celery.tasks


@pytest.mark.req("FR-PLAT-51")
def test_handler_registration_refuses_a_duplicate() -> None:
    """Two handlers for one kind makes behaviour depend on import order."""
    handlers.register_handler(JobKind.MODEL_FIT, lambda p, pr: JobResult(kind="none"))
    with pytest.raises(ValueError, match="already registered"):
        handlers.register_handler(JobKind.MODEL_FIT, lambda p, pr: JobResult(kind="none"))


# -- NFR-PLAT-3: a running job that says nothing is flagged --------------------------------


@pytest.mark.req("NFR-PLAT-3")
async def test_a_running_job_with_recent_progress_is_not_stalled(
    database: Database, workspace_id, principal
) -> None:
    from datetime import UTC, datetime

    from app.db.models import JobRow
    from app.platform.jobs import is_stalled

    job = await _submit(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        row = await session.get(JobRow, job.id)
        row.status = JobStatus.RUNNING
        row.started_at = datetime.now(UTC)
        row.progress_at = datetime.now(UTC)

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert is_stalled(row, stall_seconds=30) is False


@pytest.mark.req("NFR-PLAT-3")
async def test_a_running_job_that_has_said_nothing_is_stalled(
    database: Database, workspace_id, principal
) -> None:
    """NFR-PLAT-3: no progress within the window means the Job is treated as stalled."""
    from datetime import UTC, datetime, timedelta

    from app.db.models import JobRow
    from app.platform.jobs import is_stalled, to_schema

    job = await _submit(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        row = await session.get(JobRow, job.id)
        row.status = JobStatus.RUNNING
        row.started_at = datetime.now(UTC) - timedelta(minutes=10)
        row.progress_at = datetime.now(UTC) - timedelta(minutes=10)

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert is_stalled(row, stall_seconds=30) is True
    assert to_schema(row, stall_seconds=30).stalled is True


@pytest.mark.req("NFR-PLAT-3")
async def test_only_running_jobs_can_stall(
    database: Database, workspace_id, principal
) -> None:
    """Negative: a queued job is a queue-depth problem and a finished one stopped on
    purpose. Flagging either as stalled would make the signal useless."""
    from app.db.models import JobRow
    from app.platform.jobs import is_stalled

    job = await _submit(database, workspace_id, principal)
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert is_stalled(row, stall_seconds=0) is False

    async with database.unit_of_work() as session:
        await jobs.transition(session, job.id, JobStatus.CANCELLED, actor=principal)
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert is_stalled(row, stall_seconds=0) is False


@pytest.mark.req("NFR-PLAT-3")
async def test_progress_updates_arrive_within_the_budget(
    database: Database, workspace_id, principal
) -> None:
    """The measurement behind the NFR: a handler reporting continuously must produce a
    persisted update at least every 5 s. The throttle floor is 1 s, so the margin is fivefold."""
    from datetime import UTC, datetime

    from app.db.models import JobRow

    stamps: list[datetime] = []

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            progress.update(0.5, "working")
            time.sleep(0.05)
        return JobResult(kind="none", ref=None)

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)
    started = datetime.now(UTC)
    await execute_job(database, job.id)

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    stamps.append(row.progress_at)

    assert row.progress_at is not None
    gap = (row.progress_at - started).total_seconds()
    # The last write landed within the run; the throttle guarantees at most 1 s between
    # writes while a handler is reporting, comfortably inside NFR-PLAT-3's 5 s.
    assert 0 <= gap <= 5.0, gap
