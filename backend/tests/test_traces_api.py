"""`GET /api/v1/traces` (`03` §5.1:603, FR-RATE-42; W11 Task 4C).

Against real PostgreSQL and real MinIO, like `test_traces.py`: the row is written through
`app.platform.traces.write_trace` exactly as `test_traces.py` does, and only the read side —
the route, its filters and its two exclusions — is new here.

**Two exclusions, tested as the negative they are** (the plan's Correction 2): a
batch-produced trace (`environment IS NULL`, Ruling 25) and a still-`pending` trace (no body
yet) must never appear, even though both are real rows in the same table a naive query would
return.

**RBAC is `Permission.RATING_READ`, not a Service Account scoring permission** — see
`backend/src/app/api/traces.py`'s module docstring for why. That means Ruling 18's
three-case pattern (permitted / refused / key relabelled to another environment, refused at
authentication) does not transfer: there is no Service-Account-scoped-key path to this route
at all, because FR-GOV-6 forbids granting a Service Account `RATING_READ`. The two cases that
do apply — granted vs. not — are `test_api_rate_tables.py`'s `RATING_READ` pattern
(`auditor_headers`/no-grant), reused here rather than invented.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.session import Database
from app.main import create_app
from app.platform import traces as traces_service
from app.platform.blobs import BlobStore
from model_schema import Trace, TraceStep, new_uuid7

pytestmark = pytest.mark.usefixtures("database")


@pytest.fixture
def api_settings() -> Settings:
    """Settings with development identity on, pointed at the *test* database and bucket —
    same reasoning as `test_api_jobs.py`'s fixture of the same name."""
    from pydantic import SecretStr

    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def reader_headers(workspace_id, principal, grant) -> dict[str, str]:
    """A caller with `RATING_READ` (the `analyst` role, same as `test_api_rate_tables.py`'s
    `actuary` fixture)."""
    await grant("analyst")
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


@pytest_asyncio.fixture
async def unprivileged_headers(workspace_id, principal, membership) -> dict[str, str]:
    """Authenticated and a member, holding no role — the refusal must come from the
    permission dependency, not from missing membership."""
    await membership()
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


def _trace(*, quote_id: str, rating_version: str, bundle_hash: str) -> Trace:
    return Trace(
        rating_version_ref=rating_version,
        bundle_hash=bundle_hash,
        quote_id=quote_id,
        ladder_reconciled=True,
        steps=[
            TraceStep(
                step_id="s_area",
                type="lookup",
                label="Rating area from outcode",
                consumed={"postcode_outcode": "SW1A"},
                produced={"rating_area": "A3"},
                elapsed_us=41,
            )
        ],
    )


def _bundle_hash() -> str:
    return f"sha256:{new_uuid7().hex.ljust(64, '0')[:64]}"


async def _write_real_time(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    *,
    quote_id: str,
    rating_version: str,
    environment: str = "prod",
) -> None:
    """A complete, real-time-shaped trace row: `environment` set, body written.

    Constructed directly through `write_trace`'s own `environment=` parameter rather than
    via the pending-then-complete path (Ruling 35) — this file tests the *read* side, which
    only cares what the finished row looks like, exactly as `test_traces.py`'s
    `test_batch_produced_trace_carries_no_environment` constructs its batch-shaped row
    directly rather than through a batch Job.
    """
    trace = _trace(
        quote_id=quote_id, rating_version=rating_version, bundle_hash=_bundle_hash()
    )
    async with database.unit_of_work() as session:
        await traces_service.write_trace(
            session,
            blob_store,
            trace,
            workspace_id=workspace_id,
            sample_reason="rate",
            environment=environment,
        )


async def _write_batch_produced(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    *,
    quote_id: str,
    rating_version: str,
) -> None:
    """A trace written on request for a `score.batch` Job (FR-RATE-41, Ruling 25): no
    `environment` — the plan's Correction 2 signal this route must exclude by."""
    trace = _trace(
        quote_id=quote_id, rating_version=rating_version, bundle_hash=_bundle_hash()
    )
    async with database.unit_of_work() as session:
        await traces_service.write_trace(
            session,
            blob_store,
            trace,
            workspace_id=workspace_id,
            sample_reason="rate",
        )


async def _write_pending(
    database: Database, workspace_id, *, quote_id: str, rating_version: str
) -> None:
    """A real-time sampled outcome awaiting its off-path re-score (Ruling 35): an
    `environment` but no body yet."""
    async with database.unit_of_work() as session:
        await traces_service.write_pending_trace(
            session,
            workspace_id=workspace_id,
            quote_id=quote_id,
            rating_version_ref=rating_version,
            bundle_hash=_bundle_hash(),
            sample_reason="decline",
            environment="prod",
            quote_context={"quote_id": quote_id},
            served_summary={"outcome": "declined"},
        )


# -- access control ------------------------------------------------------------------------


@pytest.mark.req("NFR-RATE-11")
async def test_a_caller_holding_rating_read_may_list_traces(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    reader_headers,
) -> None:
    await _write_real_time(
        database, blob_store, workspace_id,
        quote_id="quote-1", rating_version="rating_version:motor-gb@1",
    )
    response = client.get("/api/v1/traces", headers=reader_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total_estimate"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["quote_id"] == "quote-1"
    assert body["items"][0]["trace"]["quote_id"] == "quote-1"


@pytest.mark.req("NFR-RATE-11")
async def test_a_caller_without_rating_read_is_refused_403(
    client: TestClient, unprivileged_headers
) -> None:
    """A 403 for the missing permission, not an incidental 401/404 that would pass for the
    wrong reason (Ruling 18's discipline, applied to a `RATING_READ`-gated route)."""
    response = client.get("/api/v1/traces", headers=unprivileged_headers)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-PLAT-4")
def test_an_unauthenticated_caller_is_401(client: TestClient) -> None:
    response = client.get("/api/v1/traces")
    assert response.status_code == 401, response.text


# -- filters --------------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-42")
async def test_the_route_filters_by_rating_version(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    reader_headers,
) -> None:
    await _write_real_time(
        database, blob_store, workspace_id,
        quote_id="quote-a", rating_version="rating_version:motor-gb@1",
    )
    await _write_real_time(
        database, blob_store, workspace_id,
        quote_id="quote-b", rating_version="rating_version:motor-gb@2",
    )

    response = client.get(
        "/api/v1/traces",
        params={"rating_version": "rating_version:motor-gb@1"},
        headers=reader_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total_estimate"] == 1
    assert [item["quote_id"] for item in body["items"]] == ["quote-a"]


@pytest.mark.req("FR-RATE-42")
async def test_another_workspaces_traces_are_invisible(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    reader_headers,
) -> None:
    other_workspace = new_uuid7()
    await _write_real_time(
        database, blob_store, other_workspace,
        quote_id="quote-other-ws", rating_version="rating_version:motor-gb@1",
    )

    response = client.get("/api/v1/traces", headers=reader_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["items"] == []
    assert body["total_estimate"] == 0


# -- the two exclusions (Correction 2 / Ruling 25, and the pending-body corollary) ----------


@pytest.mark.req("FR-RATE-42")
async def test_a_batch_produced_trace_is_never_returned(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    reader_headers,
) -> None:
    """The plan's Task 4C Step 3, corrected: the exclusion signal is a null `environment`,
    not a batch parent — `ScoringTraceRow` has none. A trace written on request for a
    `score.batch` Job (FR-RATE-41, Ruling 25) must not appear in this production stream."""
    await _write_real_time(
        database, blob_store, workspace_id,
        quote_id="quote-realtime", rating_version="rating_version:motor-gb@1",
    )
    await _write_batch_produced(
        database, blob_store, workspace_id,
        quote_id="quote-batch", rating_version="rating_version:motor-gb@1",
    )

    response = client.get("/api/v1/traces", headers=reader_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    quote_ids = {item["quote_id"] for item in body["items"]}
    assert quote_ids == {"quote-realtime"}
    assert body["total_estimate"] == 1


@pytest.mark.req("FR-RATE-42")
async def test_a_pending_trace_is_never_returned(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    reader_headers,
) -> None:
    """A row still awaiting its off-path re-score (Ruling 35) has an `environment` but no
    body — the second, independent exclusion this route needs beyond the null-environment
    one, or the route would try to read a blob that does not exist yet."""
    await _write_real_time(
        database, blob_store, workspace_id,
        quote_id="quote-complete", rating_version="rating_version:motor-gb@1",
    )
    await _write_pending(
        database, workspace_id,
        quote_id="quote-pending", rating_version="rating_version:motor-gb@1",
    )

    response = client.get("/api/v1/traces", headers=reader_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    quote_ids = {item["quote_id"] for item in body["items"]}
    assert quote_ids == {"quote-complete"}
    assert body["total_estimate"] == 1
