"""`GET /api/v1/blobs/{sha256}` serves a blob only to its owner's workspace (`07` §5.1).

Through the route itself, because the refusal is the route's. A blob is content-addressed and
`blobs` has no workspace column, so the route learns who may read a digest from the rows that
reference it: a dataset version's tables or a job's blob result **in the caller's workspace**.
A digest a quote-input store references (a scoring trace) is never served here — trace bodies
are read through the traces API, which is workspace-scoped (NFR-499, RL-917). Every refusal is
the same 404 a missing blob gets, so the route does not confirm that a blob exists.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.models import (
    BlobRow,
    DatasetRow,
    DatasetVersionRow,
    JobRow,
    ScoringTraceRow,
)
from app.db.session import Database
from app.main import create_app
from model_schema import (
    DatasetKind,
    DatasetStatus,
    JobKind,
    JobQueue,
    JobSource,
    JobStatus,
    new_uuid7,
)


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def reader_headers(workspace_id, principal, grant) -> dict[str, str]:
    """A `dataset:read` holder in `workspace_id` — the only permission the route asks for."""
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


def _digest() -> str:
    return hashlib.sha256(new_uuid7().bytes).hexdigest()


async def _blob(database: Database, sha256: str, media_type: str) -> None:
    async with database.unit_of_work() as session:
        session.add(BlobRow(sha256=sha256, bytes_=10, media_type=media_type))


async def _dataset_blob(database: Database, workspace_id, sha256: str) -> None:
    """A dataset version whose parquet table is `sha256`, in `workspace_id`."""
    await _blob(database, sha256, "application/vnd.apache.parquet")
    async with database.unit_of_work() as session:
        slug = f"ds-{sha256[:8]}"
        dataset = DatasetRow(workspace_id=workspace_id, slug=slug, name=slug, owner_id=new_uuid7())
        session.add(dataset)
        await session.flush()
        session.add(
            DatasetVersionRow(
                workspace_id=workspace_id,
                dataset_id=dataset.id,
                version=1,
                status=DatasetStatus.DRAFT.value,
                kind=DatasetKind.INGESTED.value,
                slug=slug,
                created_by=new_uuid7(),
                currency="GBP",
                tables=[{"name": "policies", "blob": {"sha256": sha256}}],
            )
        )


async def _job_blob(database: Database, workspace_id, sha256: str) -> None:
    """A job whose result is `JobResult(kind="blob")` naming `sha256` (`03` §5.2)."""
    await _blob(database, sha256, "application/json")
    async with database.unit_of_work() as session:
        session.add(
            JobRow(
                workspace_id=workspace_id,
                kind=JobKind.RATE_TABLE_DIFF,
                status=JobStatus.SUCCEEDED,
                queue=JobQueue.DEFAULT,
                source=JobSource.API,
                submitted_by={"kind": "user", "id": str(new_uuid7())},
                result={"kind": "blob", "ref": sha256},
                finished_at=datetime.now(UTC),
            )
        )


async def _trace_blob(database: Database, workspace_id, sha256: str) -> None:
    """A sampled scoring trace whose body — quote inputs — is `sha256`."""
    await _blob(database, sha256, "application/json")
    async with database.unit_of_work() as session:
        session.add(
            ScoringTraceRow(
                workspace_id=workspace_id,
                rating_version_ref="rating_version:motor-gb@1",
                bundle_hash="sha256:" + "0" * 64,
                sample_reason="rate",
                blob_sha256=sha256,
            )
        )


def _get(client: TestClient, headers: dict[str, str], sha256: str):
    return client.get(f"/api/v1/blobs/{sha256}", headers=headers, follow_redirects=False)


def _assert_indistinguishable_404(response, sha256: str) -> None:
    """A refused blob and a missing one answer identically: status, code, title and detail."""
    assert response.status_code == 404, response.text
    body = response.json()
    assert (body["code"], body["title"], body["detail"]) == (
        "NOT_FOUND", "Blob not found", f"No blob with digest {sha256}."
    )


# -- the positive controls: the caller's own blobs still download ------------------------


@pytest.mark.req("FR-421")
async def test_the_callers_own_dataset_blob_still_redirects(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    sha256 = _digest()
    await _dataset_blob(database, workspace_id, sha256)
    response = _get(client, reader_headers, sha256)
    assert response.status_code == 307, response.text
    assert sha256 in response.headers["location"]


@pytest.mark.req("FR-421")
async def test_the_callers_own_job_result_blob_still_redirects(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    sha256 = _digest()
    await _job_blob(database, workspace_id, sha256)
    response = _get(client, reader_headers, sha256)
    assert response.status_code == 307, response.text


# -- the refusals ---------------------------------------------------------------------------


@pytest.mark.req("NFR-499")
async def test_a_trace_blob_is_refused_even_in_the_callers_workspace(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    """Quote inputs are read through the traces API only, never as a raw blob."""
    sha256 = _digest()
    await _trace_blob(database, workspace_id, sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("NFR-499")
async def test_a_trace_blob_is_refused_even_when_a_job_result_also_names_it(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    """The quote-input refusal is checked first: an owner elsewhere does not re-admit it."""
    sha256 = _digest()
    await _trace_blob(database, workspace_id, sha256)
    await _job_blob_reference_only(database, workspace_id, sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


async def _job_blob_reference_only(database: Database, workspace_id, sha256: str) -> None:
    async with database.unit_of_work() as session:
        session.add(
            JobRow(
                workspace_id=workspace_id,
                kind=JobKind.RATE_TABLE_DIFF,
                status=JobStatus.SUCCEEDED,
                queue=JobQueue.DEFAULT,
                source=JobSource.API,
                submitted_by={"kind": "user", "id": str(new_uuid7())},
                result={"kind": "blob", "ref": sha256},
                finished_at=datetime.now(UTC),
            )
        )


@pytest.mark.req("FR-421")
async def test_another_workspaces_dataset_blob_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    """A `dataset:read` holder in one workspace cannot fetch another workspace's parquet."""
    sha256 = _digest()
    await _dataset_blob(database, new_uuid7(), sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("FR-421")
async def test_another_workspaces_job_result_blob_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    sha256 = _digest()
    await _job_blob(database, new_uuid7(), sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("FR-421")
async def test_a_blob_no_owner_references_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    """Fail closed: a blob nothing in the caller's workspace owns is not served."""
    sha256 = _digest()
    await _blob(database, sha256, "application/octet-stream")
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)
