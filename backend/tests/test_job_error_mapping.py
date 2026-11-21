"""#1888 option (d): a deadlock is a coded, retryable refusal, and nothing is retried.

PostgreSQL aborts one of two transactions that wait on each other (SQLSTATE 40P01). Before this a
route answered `500 INTERNAL_ERROR` and a Job failed `JOB_HANDLER_FAILED` with `retryable` false,
so a caller could not tell a conflict from a defect. Now a route answers `409
CONCURRENT_WRITE_RETRY` and a Job fails with that code marked retryable. No handler is re-run, so
no side effect repeats.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import DBAPIError

from app.db.models import JobRow
from app.db.session import Database
from app.errors import install_error_handlers
from app.platform import jobs
from app.platform.safe_exception import coded_job_error, is_retryable_job_code
from app.worker import handlers
from app.worker.tasks import execute_job
from model_schema import JobKind, JobResult, JobStatus
from pricing_core.progress import ProgressCallback


class _DriverError(Exception):
    """Stands in for the driver's exception: only its SQLSTATE matters to the mapping."""

    def __init__(self, sqlstate: str) -> None:
        super().__init__("driver text that must never reach a response")
        self.sqlstate = sqlstate


def _database_error(sqlstate: str) -> DBAPIError:
    return DBAPIError("SELECT 1", {}, _DriverError(sqlstate))


def _client(sqlstate: str) -> TestClient:
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/conflict")
    async def conflict() -> None:
        raise _database_error(sqlstate)

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.req("FR-420")
def test_a_deadlock_answers_409_with_the_retry_code() -> None:
    response = _client("40P01").get("/conflict")
    assert response.status_code == 409
    assert "CONCURRENT_WRITE_RETRY" in response.text
    assert "driver text" not in response.text


@pytest.mark.req("FR-420")
def test_any_other_database_error_is_still_the_backstop() -> None:
    """The control: a different SQLSTATE is not named by this mapping."""
    response = _client("23505").get("/conflict")
    assert response.status_code == 500
    assert "CONCURRENT_WRITE_RETRY" not in response.text


@pytest.mark.req("FR-420")
def test_only_a_deadlock_victim_is_a_retryable_job_code() -> None:
    coded = coded_job_error(_database_error("40P01"))
    assert coded is not None
    assert coded[0] == "CONCURRENT_WRITE_RETRY"
    assert coded_job_error(_database_error("23505")) is None
    assert is_retryable_job_code("CONCURRENT_WRITE_RETRY")
    assert not is_retryable_job_code("JOB_HANDLER_FAILED")


@pytest.fixture(autouse=True)
def _isolate_handlers():
    original = dict(handlers.HANDLERS)
    handlers.HANDLERS.clear()
    yield
    handlers.HANDLERS.clear()
    handlers.HANDLERS.update(original)


async def _failed_job(database: Database, workspace_id, principal, handler) -> JobRow:
    handlers.register_handler(JobKind.MODEL_FIT, handler)
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    assert await execute_job(database, job.id) is JobStatus.FAILED
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
        assert row is not None
        return row


@pytest.mark.req("FR-420")
async def test_a_deadlock_in_a_handler_fails_the_job_with_a_retryable_code(
    database: Database, workspace_id, principal
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        raise _database_error("40P01")

    row = await _failed_job(database, workspace_id, principal, handler)

    assert row.error is not None
    assert row.error["code"] == "CONCURRENT_WRITE_RETRY"
    assert row.error["retryable"] is True


@pytest.mark.req("FR-420")
async def test_a_handler_bug_is_still_not_retryable(
    database: Database, workspace_id, principal
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        raise ValueError("a bug")

    row = await _failed_job(database, workspace_id, principal, handler)

    assert row.error is not None
    assert row.error["code"] == "JOB_HANDLER_FAILED"
    assert row.error["retryable"] is False


@pytest.mark.req("FR-420")
async def test_a_handler_that_breaks_the_collector_contract_fails_the_job_with_a_code_not_a_hang(
    database: Database, blob_store, workspace_id, principal, monkeypatch: pytest.MonkeyPatch
) -> None:
    """#1855 (v), the Job-runner shape: a handler runs the collector while its own open
    transaction holds the workspace's audit lock. The collector's lock timeout ends the call with
    `BLOB_GC_LOCK_TIMEOUT`, the Job fails with that code (503 is a route's, a Job stores the
    code), and the runner does not hang. Without the timeout the test's `wait_for` ends it."""
    import asyncio

    from app.platform import audit, blobs
    from model_schema import JobSource

    monkeypatch.setattr(blobs, "_GC_LOCK_TIMEOUT_MS", 1000)

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        async def broken() -> None:
            async with progress.database.unit_of_work() as session:  # type: ignore[attr-defined]
                await audit.record(
                    session,
                    workspace_id=workspace_id,
                    actor=principal,
                    source=JobSource.SYSTEM,
                    action="probe.audit_lock_held",
                    entity_ref="probe:audit-lock@1",
                    after={"probe": True},
                )
                await progress.blob_store.collect_garbage(  # type: ignore[attr-defined]
                    progress.database,  # type: ignore[attr-defined]
                    actor=principal,
                    workspace_id=workspace_id,
                    dry_run=True,
                )

        progress.run_on_loop(broken())  # type: ignore[attr-defined]
        raise AssertionError("unreachable")

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    status = await asyncio.wait_for(execute_job(database, job.id, blob_store), timeout=60)
    assert status is JobStatus.FAILED
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row is not None
    assert row.error is not None
    assert row.error["code"] == "BLOB_GC_LOCK_TIMEOUT"
