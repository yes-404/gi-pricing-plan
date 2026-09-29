"""FR-18: a Job records the platform version it ran on (`00` §3, `07` §4.1)."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.models import JobRow
from app.db.session import Database
from app.platform import jobs
from app.worker import handlers
from app.worker.tasks import execute_job
from model_schema import JobKind, JobResult, JobStatus
from pricing_core.progress import ProgressCallback

pytestmark = pytest.mark.usefixtures("database")

_SHA = "97b15726b1dd60ba407c6aba44735ad5cbe207ed"


@pytest.fixture(autouse=True)
def _isolate_handlers():
    original = dict(handlers.HANDLERS)
    handlers.HANDLERS.clear()
    yield
    handlers.HANDLERS.clear()
    handlers.HANDLERS.update(original)


async def _submit(database: Database, workspace_id, principal) -> Any:
    async with database.unit_of_work() as session:
        return await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )


def _worker_settings(build: str) -> Settings:
    return Settings(environment=Environment.LOCAL, version="9.9.9", build=build)


@pytest.mark.req("FR-18")
async def test_a_job_the_worker_runs_records_the_workers_version_and_build(
    database: Database, workspace_id, principal
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        return JobResult(kind="artifact", ref="model:motor-ad-frequency@7")

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    job = await _submit(database, workspace_id, principal)

    status = await execute_job(database, job.id, settings=_worker_settings(_SHA))
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.platform_build == f"9.9.9+{_SHA}"


@pytest.mark.req("FR-18")
async def test_a_queued_job_has_no_platform_build(
    database: Database, workspace_id, principal
) -> None:
    job = await _submit(database, workspace_id, principal)
    assert job.platform_build is None
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.platform_build is None


@pytest.mark.req("FR-18")
async def test_the_job_endpoint_returns_platform_build(
    api_client: TestClient, database: Database, workspace_id, principal, grant
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        return JobResult(kind="artifact", ref="model:motor-ad-frequency@7")

    handlers.register_handler(JobKind.MODEL_FIT, handler)
    await grant("analyst")
    headers = {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}
    job = await _submit(database, workspace_id, principal)

    queued = api_client.get(f"/api/v1/jobs/{job.id}", headers=headers).json()
    assert queued["platform_build"] is None

    await execute_job(database, job.id, settings=_worker_settings("local"))
    ran = api_client.get(f"/api/v1/jobs/{job.id}", headers=headers).json()
    assert ran["platform_build"] == "9.9.9+local"
