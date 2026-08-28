"""The `rate_table.diff` job handler (03 §5.1, FR-RATE-62).

The diff Job exists only because the endpoint answered 202 — one or both versions is
`storage: parquet`. The handler therefore does not re-decide anything: it computes the
same diff the 200 path computes, then persists the artifact to the blob store and
returns `JobResult(kind="blob")` with the sha256 as the ref — the first blob-kind
result in the codebase. The client fetches `GET /blobs/{sha256}`.

`execute_job` is driven directly rather than through a broker, the `test_data_jobs`
convention.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from backend.tests.test_rate_tables_service import _seed, _set_threshold, _table_slug

from app.config import Settings
from app.db.models import BlobRow, JobRow
from app.db.session import Database
from app.platform import jobs as job_service
from app.platform import rate_tables as svc
from app.platform.blobs import BlobStore, to_ref
from app.worker.rate_table_handlers import register_rate_table_handlers
from app.worker.tasks import execute_job
from model_schema import JobKind, JobStatus, Principal
from model_schema.rating import RateTableDiff


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_rate_table_handlers()


async def _seed_parquet_diff(
    database: Database, workspace_id, principal: Principal, blob_store: BlobStore
) -> tuple[str, int]:
    """A table with version 1 in rows and version 2 in parquet, diffing to 1 cell.

    The threshold is set to 2 before the import so the 3-cell version spills to
    parquet — the only shape the endpoint answers 202 for (FR-RATE-62).
    """
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)
    content = (
        b"driver_age_band,relativity\n"
        b"17-20,1.9200\n"
        b"21-24,1.4500\n"
        b"25-29,1.1200\n"
    )
    await _set_threshold(database, workspace_id, 2)
    await svc.import_confirmed(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        version=1,
        filename="import.csv",
        content=content,
    )
    return slug, 2


def _parameters(workspace_id, principal: Principal, slug: str, version: int, against: str):
    """The parameters the 202 endpoint submits (`job_identity` + the diff address)."""
    return {
        "workspace_id": str(workspace_id),
        "actor": principal.model_dump(mode="json"),
        "slug": slug,
        "version": version,
        "against": against,
    }


async def _submit(database: Database, workspace_id, principal: Principal, parameters: dict):
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.RATE_TABLE_DIFF,
            parameters,
            principal,
            workspace_id=workspace_id,
        )
    return job


async def _read_result_blob(database: Database, blob_store: BlobStore, sha256: str) -> bytes:
    async with database.session() as session:
        row = await session.get(BlobRow, sha256)
        assert row is not None
        return await blob_store.read(to_ref(row))


@pytest.mark.req("FR-RATE-62")
async def test_a_rate_table_diff_job_stores_the_diff_artifact_as_a_blob(
    database: Database, workspace_id, principal, blob_store
) -> None:
    slug, version = await _seed_parquet_diff(database, workspace_id, principal, blob_store)
    job = await _submit(
        database,
        workspace_id,
        principal,
        _parameters(workspace_id, principal, slug, version, "previous"),
    )

    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.status is JobStatus.SUCCEEDED
    # The first blob-kind result: the ref is the sha256 the client fetches from
    # `/blobs/{sha256}`.
    assert row.result["kind"] == "blob"
    assert len(row.result["ref"]) == 64

    payload = await _read_result_blob(database, blob_store, row.result["ref"])
    diff = RateTableDiff.model_validate_json(payload)
    assert diff.changed_cells == 1


@pytest.mark.req("FR-RATE-62")
async def test_an_explicit_version_number_in_against_is_reparsed(
    database: Database, workspace_id, principal, blob_store
) -> None:
    """The endpoint forwards `against` verbatim, so a version number arrives as a string."""
    slug, version = await _seed_parquet_diff(database, workspace_id, principal, blob_store)
    job = await _submit(
        database,
        workspace_id,
        principal,
        _parameters(workspace_id, principal, slug, version, "1"),
    )

    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    payload = await _read_result_blob(database, blob_store, row.result["ref"])
    assert RateTableDiff.model_validate_json(payload).changed_cells == 1


@pytest.mark.req("FR-RATE-62")
async def test_a_rate_table_diff_job_on_a_missing_table_fails_with_the_refusal(
    database: Database, workspace_id, principal
) -> None:
    job = await _submit(
        database,
        workspace_id,
        principal,
        _parameters(workspace_id, principal, "no-such-table", 1, "previous"),
    )

    assert await execute_job(database, job.id) is JobStatus.FAILED

    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row.error["code"] == "RATE_TABLE_MISS"
    assert row.error["retryable"] is False
