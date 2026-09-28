"""`GET /api/v1/blobs/{sha256}` serves a blob only to its owner's workspace (`07` §5.1).

Through the route itself, because the refusal is the route's. A blob is content-addressed and
`blobs` has no workspace column, so the route learns who may read a digest from the rows that
reference it: a dataset version's tables or a job's blob result **in the caller's workspace**.
A digest a quote-input store references (a scoring trace) is never served here — trace bodies
are read through the traces API, which is workspace-scoped (NFR-499, RL-917). Every refusal is
the same 404 a missing blob gets, so the route does not confirm that a blob exists.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
import pytest_asyncio
from backend.tests.blob_fixtures import (
    blob_row,
    dataset_blob,
    digest,
    job_blob,
    job_result_owner,
    trace_blob,
)
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.models import (
    RatingVersionRow,
)
from app.db.session import Database
from app.main import create_app
from model_schema import (
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
    sha256 = digest()
    await dataset_blob(database, workspace_id, sha256)
    response = _get(client, reader_headers, sha256)
    assert response.status_code == 307, response.text
    assert sha256 in response.headers["location"]


@pytest.mark.req("FR-421")
async def test_the_callers_own_job_result_blob_still_redirects(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    sha256 = digest()
    await job_blob(database, workspace_id, sha256)
    response = _get(client, reader_headers, sha256)
    assert response.status_code == 307, response.text


# -- the refusals ---------------------------------------------------------------------------


@pytest.mark.req("NFR-499")
async def test_a_trace_blob_is_refused_even_in_the_callers_workspace(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    """Quote inputs are read through the traces API only, never as a raw blob."""
    sha256 = digest()
    await trace_blob(database, workspace_id, sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("NFR-499")
async def test_a_trace_blob_is_refused_even_when_a_job_result_also_names_it(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    """The quote-input refusal is checked first: an owner elsewhere does not re-admit it."""
    sha256 = digest()
    await trace_blob(database, workspace_id, sha256)
    await job_result_owner(database, workspace_id, sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("FR-421")
async def test_another_workspaces_dataset_blob_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    """A `dataset:read` holder in one workspace cannot fetch another workspace's parquet."""
    sha256 = digest()
    await dataset_blob(database, new_uuid7(), sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("FR-421")
async def test_another_workspaces_job_result_blob_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    sha256 = digest()
    await job_blob(database, new_uuid7(), sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("FR-421")
async def test_a_blob_no_owner_references_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    """Fail closed: a blob nothing in the caller's workspace owns is not served."""
    sha256 = digest()
    await blob_row(database, sha256, "application/octet-stream")
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("FR-421")
async def test_a_compiled_bundle_blob_is_refused_even_in_the_callers_workspace(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    """A Rating Version's compiled bundle is not a download: its digest is exposed in
    `BundleMetadata.blob_sha256`, and scoring reads it server-side, so this route refuses
    it even to the owning workspace (a bundle is not an allowed owner)."""
    sha256 = digest()
    await _bundle_blob(database, workspace_id, sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


async def _bundle_blob(database: Database, workspace_id, sha256: str) -> None:
    """A Rating Version in `workspace_id` whose compiled bundle is `sha256`."""
    await blob_row(database, sha256, "application/json")
    async with database.unit_of_work() as session:
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=f"rv-{sha256[:8]}",
                version=1,
                status="approved",
                dataset_version_id=new_uuid7(),
                model_ref="model:m@1",
                created_by=new_uuid7(),
                bundle={"content_hash": "sha256:" + "1" * 64, "blob_sha256": sha256},
            )
        )


@pytest.mark.req("FR-421")
async def test_another_workspaces_compiled_bundle_blob_is_refused(
    client: TestClient, database: Database, reader_headers
) -> None:
    """The cross-workspace half of the bundle case: B's bundle digest, asked for by A."""
    sha256 = digest()
    await _bundle_blob(database, new_uuid7(), sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)


@pytest.mark.req("NFR-499")
async def test_another_workspaces_trace_digest_is_refused_even_when_the_caller_owns_it(
    client: TestClient, database: Database, workspace_id, reader_headers
) -> None:
    """Content addressing: one digest can be a trace body in workspace B and a job result in
    the caller's workspace A. The quote-input refusal is global — **any** trace, in any
    workspace, that references the digest — so A's own owner does not re-admit B's quote
    inputs. A refusal scoped to the caller's workspace would serve them."""
    sha256 = digest()
    await trace_blob(database, new_uuid7(), sha256)
    await job_result_owner(database, workspace_id, sha256)
    _assert_indistinguishable_404(_get(client, reader_headers, sha256), sha256)
