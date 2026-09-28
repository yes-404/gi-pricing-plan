"""`POST /api/v1/datasets/{slug}/versions` ingests only a blob the caller's workspace owns.

At `5ec47dc4` the route took any well-formed digest and the worker checked only that a `blobs`
row existed. `blobs` has no workspace column, so a `dataset:write` holder in workspace A who
knew a digest of workspace B's data could ingest it into A and read it there (the ingest-side
twin of the blob-route fix, #868). The owners are the same allow-list the download route uses:
a Dataset Version's tables or a job's blob result in the caller's workspace. A digest a
quote-input store references is never ingestible, and every refusal is the 404 a missing blob
gets, so the route never confirms that a digest exists.

Through the route itself, because the refusal is the route's.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from backend.tests.blob_fixtures import dataset_blob, digest, job_blob, trace_blob
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.session import Database
from model_schema import new_uuid7


@pytest_asyncio.fixture
async def writer_headers(workspace_id, principal, grant) -> dict[str, str]:
    """A `dataset:write` holder in `workspace_id`."""
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


def _ingest(client: TestClient, headers: dict[str, str], sha256: str):
    slug = f"ds-{new_uuid7().hex[-8:]}"
    assert client.post("/api/v1/datasets", json={"slug": slug}, headers=headers).status_code == 201
    return client.post(
        f"/api/v1/datasets/{slug}/versions",
        json={"blob": sha256, "filename": "exposure.csv", "recipe": []},
        headers=headers,
    )


def _assert_indistinguishable_404(response, sha256: str) -> None:
    """A refused digest and an unknown one answer identically."""
    assert response.status_code == 404, response.text
    body = response.json()
    assert (body["code"], body["title"], body["detail"]) == (
        "NOT_FOUND", "Blob not found", f"No blob with digest {sha256}."
    )


# -- the positive controls: the caller's own blobs still ingest ---------------------------


@pytest.mark.req("FR-27")
async def test_the_callers_own_dataset_blob_still_starts_an_ingestion(
    api_client: TestClient, database: Database, workspace_id, writer_headers
) -> None:
    sha256 = digest()
    await dataset_blob(database, workspace_id, sha256)
    assert _ingest(api_client, writer_headers, sha256).status_code == 202


@pytest.mark.req("FR-27")
async def test_the_callers_own_job_result_blob_still_starts_an_ingestion(
    api_client: TestClient, database: Database, workspace_id, writer_headers
) -> None:
    sha256 = digest()
    await job_blob(database, workspace_id, sha256)
    assert _ingest(api_client, writer_headers, sha256).status_code == 202


# -- the refusals, each the same 404 -------------------------------------------------------


@pytest.mark.req("FR-27")
async def test_another_workspaces_dataset_blob_cannot_be_ingested(
    api_client: TestClient, database: Database, workspace_id, writer_headers
) -> None:
    sha256 = digest()
    await dataset_blob(database, new_uuid7(), sha256)
    _assert_indistinguishable_404(_ingest(api_client, writer_headers, sha256), sha256)


@pytest.mark.req("FR-27")
async def test_a_trace_digest_cannot_be_ingested_even_in_the_callers_workspace(
    api_client: TestClient, database: Database, workspace_id, writer_headers
) -> None:
    sha256 = digest()
    await trace_blob(database, workspace_id, sha256)
    _assert_indistinguishable_404(_ingest(api_client, writer_headers, sha256), sha256)


@pytest.mark.req("FR-27")
async def test_a_digest_nothing_references_cannot_be_ingested(
    api_client: TestClient, writer_headers
) -> None:
    """Fail closed, and identical to a digest that is not in the store at all."""
    sha256 = digest()
    _assert_indistinguishable_404(_ingest(api_client, writer_headers, sha256), sha256)
