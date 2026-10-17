"""The upload-completion routes and the promotion they start (`07` FR-421, RL-1724, FD-1730).

These run the `blob.promote` Job inline through `execute_job`, as the other route tests run
their jobs: what they pin is what the routes and the handler do. The one test that walks the
whole public path against a real worker process is `test_upload_to_ingest.py`.

Each guard below has a **breaker**: the one-line change to the implementation that makes it
fail, named in the test's docstring so a reader can see what the test is protecting.
"""

from __future__ import annotations

import os
from uuid import UUID

import httpx
import pytest
import pytest_asyncio
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.session import Database
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import JobStatus, new_uuid7


@pytest_asyncio.fixture
async def writer(workspace_id, principal, grant) -> dict[str, str]:
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


def _payload() -> bytes:
    """Unique per call: the database is long-lived, so a fixed payload is a blob that may
    already exist (FR-419), and the tests below count what their own upload creates."""
    return b"a,b\n" + os.urandom(16).hex().encode() + b",1\n"


def _upload(client: TestClient, headers: dict[str, str], parts: list[bytes]) -> tuple[str, dict]:
    """Request an upload URL and PUT the parts. Returns the Blob Upload's id and response.

    The id is read with `.get`, so a platform that does not yet return one fails at the
    assertion about the *route under test*, not in this helper.
    """
    response = client.post(
        "/api/v1/blobs/upload-url",
        json={"media_type": "text/csv", "parts": len(parts)},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    for url, part in zip(body["urls"], parts, strict=True):
        # A single-part URL signs the media type, so the PUT must send it (FR-421).
        headers = {"Content-Type": "text/csv"} if len(parts) == 1 else {}
        assert httpx.put(url, content=part, headers=headers, timeout=60).status_code == 200
    return body.get("id", str(new_uuid7())), body


def _complete(client: TestClient, headers: dict[str, str], upload_id: str):
    return client.post(f"/api/v1/blobs/uploads/{upload_id}/complete", headers=headers)


async def _run(database: Database, blob_store: BlobStore, job_id: str) -> JobStatus:
    register_data_handlers()
    return await execute_job(database, UUID(job_id), blob_store)


async def _scalar(database: Database, sql: str, **params):
    async with database.unit_of_work() as session:
        return (await session.execute(text(sql), params)).scalar_one_or_none()


@pytest.mark.req("FR-421")
async def test_upload_url_records_an_upload_and_returns_its_id(
    api_client: TestClient, database: Database, writer, workspace_id
) -> None:
    response = api_client.post(
        "/api/v1/blobs/upload-url", json={"media_type": "text/csv", "parts": 2}, headers=writer
    )
    assert response.status_code == 200, response.text
    body = response.json()
    upload_id = body["id"]
    row = await _scalar(
        database,
        "select workspace_id::text || '|' || part_count::text || '|' || coalesce(s3_upload_id, '')"
        " from blob_uploads where id = :id",
        id=upload_id,
    )
    assert row == f"{workspace_id}|2|{body['upload_id']}"


@pytest.mark.req("FR-421")
async def test_completing_another_workspaces_upload_is_the_missing_404(
    api_client: TestClient, database: Database, writer, principal
) -> None:
    """Breaker: drop the workspace filter on the Blob Upload lookup -> 202."""
    from sqlalchemy import select

    from app.db.models import RoleAssignmentRow, RoleRow, WorkspaceMemberRow
    from app.platform import rbac, workspaces
    from model_schema import ScopeType

    upload_id, _ = _upload(api_client, writer, [_payload()])
    owner = _complete(api_client, writer, upload_id)
    assert owner.status_code == 202, owner.text  # the control: its own workspace may complete

    other = new_uuid7()
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=other)
        await rbac.seed_builtin_roles(session, other)
        role = (
            await session.execute(
                select(RoleRow).where(RoleRow.workspace_id == other, RoleRow.slug == "analyst")
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=other,
                principal_kind="user",
                principal_id=principal.id,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
        session.add(WorkspaceMemberRow(user_id=principal.id, workspace_id=other))
    foreign = {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(other)}

    second, _ = _upload(api_client, writer, [_payload()])
    refused = _complete(api_client, foreign, second)
    missing = _complete(api_client, foreign, str(new_uuid7()))
    assert refused.status_code == 404
    assert refused.json().keys() == missing.json().keys()
    assert {
        k: v for k, v in refused.json().items() if k not in {"detail", "instance", "trace_id"}
    } == {k: v for k, v in missing.json().items() if k not in {"detail", "instance", "trace_id"}}
    jobs = await _scalar(
        database,
        "select count(*) from blob_uploads where id = :id and job_id is not null",
        id=second,
    )
    assert jobs == 0, "a refused completion left a Job on the Blob Upload"


@pytest.mark.req("FR-421")
async def test_a_completion_past_the_deadline_is_refused(
    api_client: TestClient, database: Database, writer
) -> None:
    """Breaker: drop the `complete_by` check -> 202."""
    upload_id, body = _upload(api_client, writer, [_payload()])
    assert "id" in body, "no Blob Upload was recorded, so there is no deadline to pass"
    async with database.unit_of_work() as session:
        await session.execute(
            text("update blob_uploads set complete_by = now() - interval '1 hour' where id = :id"),
            {"id": upload_id},
        )
    response = _complete(api_client, writer, upload_id)
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-421")
async def test_a_repeated_completion_returns_the_first_job(
    api_client: TestClient, database: Database, writer
) -> None:
    """Breaker: drop the read of the Blob Upload's recorded Job -> two Job ids."""
    upload_id, _ = _upload(api_client, writer, [_payload()])
    first = _complete(api_client, writer, upload_id)
    assert first.status_code == 202, first.text
    second = _complete(api_client, writer, upload_id)
    assert second.status_code == 202, second.text
    assert second.json()["id"] == first.json()["id"]
    count = await _scalar(
        database,
        "select count(*) from jobs where kind = 'blob.promote' and id = :id",
        id=first.json()["id"],
    )
    assert count == 1


@pytest.mark.req("FR-421")
async def test_a_missing_part_fails_the_promotion_by_name(
    api_client: TestClient, database: Database, blob_store: BlobStore, writer
) -> None:
    """Breaker: drop the part-list check -> S3 completes from the one part it lists and the
    Job `succeeded`s with the digest of part 1 alone: a truncated file promoted as whole."""
    response = api_client.post(
        "/api/v1/blobs/upload-url", json={"media_type": "text/csv", "parts": 2}, headers=writer
    )
    assert response.status_code == 200, response.text
    two = response.json()
    assert httpx.put(two["urls"][0], content=b"x" * 5 * 1024 * 1024, timeout=60).status_code == 200
    completed = _complete(api_client, writer, two.get("id", str(new_uuid7())))
    assert completed.status_code == 202, completed.text
    status = await _run(database, blob_store, completed.json()["id"])
    job = api_client.get(f"/api/v1/jobs/{completed.json()['id']}", headers=writer).json()
    assert status is JobStatus.FAILED
    assert job["error"]["code"] == "VALIDATION_FAILED"
    assert job["error"]["message"] == "Expected parts 1 to 2; missing part(s) 2."


@pytest.mark.req("FR-421")
async def test_a_repeated_completion_after_a_failed_promotion_returns_the_first_job(
    api_client: TestClient, database: Database, blob_store: BlobStore, writer
) -> None:
    """RL-1724 "Repeat completion": the first Job, whatever its state; a failed promotion
    ends the Blob Upload and does not start a second Job.

    Breaker: start a new Job when the recorded one is `failed` -> two Job ids."""
    response = api_client.post(
        "/api/v1/blobs/upload-url", json={"media_type": "text/csv", "parts": 2}, headers=writer
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert httpx.put(body["urls"][0], content=b"x" * 5 * 1024 * 1024, timeout=60).status_code == 200
    first = _complete(api_client, writer, body["id"])
    assert first.status_code == 202, first.text
    assert await _run(database, blob_store, first.json()["id"]) is JobStatus.FAILED
    second = _complete(api_client, writer, body["id"])
    assert second.status_code == 202, second.text
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["status"] == "failed"
    count = await _scalar(
        database,
        "select count(*) from jobs where kind = 'blob.promote' and workspace_id = :w",
        w=writer["Workspace-Id"],
    )
    assert count == 1


@pytest.mark.req("FR-421")
async def test_another_principal_with_write_in_the_workspace_may_complete(
    api_client: TestClient, writer, workspace_id, grant
) -> None:
    """RL-1724 "Who may complete": any caller with `dataset:write` in the Blob Upload's
    workspace, not only the principal that requested it.

    Breaker: add a `principal_id == caller` check to the completion lookup -> 404/403."""
    upload_id, _ = _upload(api_client, writer, [_payload()])
    colleague = new_uuid7()
    await grant("analyst", principal_id=colleague)
    other = {DEV_PRINCIPAL_HEADER: str(colleague), "Workspace-Id": str(workspace_id)}
    response = _complete(api_client, other, upload_id)
    assert response.status_code == 202, response.text


@pytest.mark.req("FR-419")
@pytest.mark.req("FR-421")
async def test_identical_bytes_promote_to_one_blob(
    api_client: TestClient, database: Database, blob_store: BlobStore, writer
) -> None:
    """Breaker: skip the existence check -> a second `put` and a primary-key error."""
    payload = _payload()
    digests = []
    keys = []
    for _ in range(2):
        upload_id, body = _upload(api_client, writer, [payload])
        keys.append(body["key"])
        completed = _complete(api_client, writer, upload_id)
        assert completed.status_code == 202, completed.text
        assert await _run(database, blob_store, completed.json()["id"]) is JobStatus.SUCCEEDED
        digests.append(
            api_client.get(f"/api/v1/jobs/{completed.json()['id']}", headers=writer).json()[
                "result"
            ]["ref"]
        )
    assert digests[0] == digests[1]
    sha = digests[0]
    assert await _scalar(database, "select count(*) from blobs where sha256 = :s", s=sha) == 1
    assert await _scalar(database, "select ref_count from blobs where sha256 = :s", s=sha) == 2
    listed = blob_store._client.list_objects_v2(
        Bucket=blob_store._bucket, Prefix=f"blob/{sha[:2]}/{sha}"
    )
    assert listed["KeyCount"] == 1
    for key in keys:
        with pytest.raises(ClientError):
            blob_store._client.head_object(Bucket=blob_store._bucket, Key=key)


@pytest.mark.req("FR-420")
@pytest.mark.req("FR-421")
async def test_a_promoted_blob_is_retained(
    api_client: TestClient, database: Database, blob_store: BlobStore, writer
) -> None:
    """Breaker: drop the `retain` -> `ref_count == 0`."""
    upload_id, _ = _upload(api_client, writer, [_payload()])
    completed = _complete(api_client, writer, upload_id)
    assert completed.status_code == 202, completed.text
    assert await _run(database, blob_store, completed.json()["id"]) is JobStatus.SUCCEEDED
    sha = api_client.get(f"/api/v1/jobs/{completed.json()['id']}", headers=writer).json()["result"][
        "ref"
    ]
    assert await _scalar(database, "select ref_count from blobs where sha256 = :s", s=sha) == 1


@pytest.mark.req("FR-421")
async def test_a_promoted_digest_downloads_only_in_its_workspace(
    api_client: TestClient, database: Database, blob_store: BlobStore, writer, principal
) -> None:
    """Breaker: remove the Job-result owner from `blob_readable_by` -> 404 for the owner."""
    upload_id, _ = _upload(api_client, writer, [_payload()])
    completed = _complete(api_client, writer, upload_id)
    assert completed.status_code == 202, completed.text
    assert await _run(database, blob_store, completed.json()["id"]) is JobStatus.SUCCEEDED
    sha = api_client.get(f"/api/v1/jobs/{completed.json()['id']}", headers=writer).json()["result"][
        "ref"
    ]
    mine = api_client.get(f"/api/v1/blobs/{sha}", headers=writer, follow_redirects=False)
    assert mine.status_code == 307
    elsewhere = {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(new_uuid7())}
    theirs = api_client.get(f"/api/v1/blobs/{sha}", headers=elsewhere, follow_redirects=False)
    assert theirs.status_code in {403, 404}
