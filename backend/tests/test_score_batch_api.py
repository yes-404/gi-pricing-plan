"""`POST /api/v1/score/batch` — the batch scoring route (W11 Task 3C, `03` §5.1:517,
FR-RATE-36/37/38).

**The route submits a Job and nothing else.** Everything durable — the manifest, the
scratch parts, the abort threshold, the output — is `app.worker.scoring_handlers`'s (Task
3B, `backend/tests/test_scoring_handlers.py`). This file tests two things only: that the
route answers 202 with a pollable Job whose completion yields a retrievable parquet
(acceptance standard item 1 for this task), and that `Permission.SCORE_BATCH` gates it the
same way Ruling 18 established for `Permission.SCORE_EXECUTE` on `/score`
(`backend/tests/test_score.py`) — a scoped account holding it may call, an account without
it is refused at the permission dependency, and a key relabelled to another environment is
refused at authentication, before either.

Fixture shape reused rather than duplicated, the established convention in this suite
(`test_scoring_handlers.py`'s own docstring): `_headers` from `test_rating_version_compile.py`,
and `_compiled_version`/`_dataset_version`/`_scoring_frame`/`SCORED_REF` from
`test_scoring_handlers.py`, which already builds exactly the fixture this file needs — a
compiled Rating Version reachable at `SCORED_REF`, and a Dataset Version carrying a
scoring-shaped table.
"""

from __future__ import annotations

import io
import json
from typing import Any
from uuid import UUID

import polars as pl
import pytest
from backend.tests.test_rating_version_compile import _headers
from backend.tests.test_scoring_handlers import (
    SCORED_REF,
    _compiled_version,
    _dataset_version,
    _scoring_frame,
)
from fastapi.testclient import TestClient

from app.db.models import BlobRow, JobRow
from app.db.session import Database
from app.platform.blobs import BlobStore, to_ref
from app.worker.scoring_handlers import register_scoring_handlers
from app.worker.tasks import execute_job
from model_schema import JobStatus, Principal

BATCH_URL = "/api/v1/score/batch"


@pytest.fixture
async def headers(
    principal: Principal, workspace_id: UUID, grant: Any
) -> dict[str, str]:
    """Dev-auth headers for a principal granted `admin` and `analyst` — enough to create a
    Service Account and a compiled Rating Version, never to call `/score/batch` itself:
    `Permission.SCORE_BATCH` is granted by no builtin role (FR-GOV-6), so this principal can
    build the fixture but never use it (mirrors `test_score.py`'s `admin_headers`)."""
    await grant("admin")
    await grant("analyst")
    return _headers(principal, workspace_id)


@pytest.fixture
def batch_headers(
    api_client: TestClient, headers: dict[str, str], workspace_id: UUID
) -> dict[str, str]:
    """A `uat` Service Account holding `score:batch` and nothing else."""
    created = api_client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "batch-engine-uat",
            "environments": ["uat"],
            "permissions": ["score:batch"],
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    return {"X-API-Key": created.json()["key"], "Workspace-Id": str(workspace_id)}


@pytest.fixture
def execute_only_headers(
    api_client: TestClient, headers: dict[str, str], workspace_id: UUID
) -> dict[str, str]:
    """A Service Account holding `score:execute` and **not** `score:batch` — the sibling
    permission (mirrors `test_score.py`'s `unpermissioned_headers`, inverted). Proves the
    route checks for *this* permission rather than merely for a permissioned caller."""
    created = api_client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "execute-only-uat",
            "environments": ["uat"],
            "permissions": ["score:execute"],
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    return {"X-API-Key": created.json()["key"], "Workspace-Id": str(workspace_id)}


@pytest.fixture
async def scoring_table(
    database: Database, blob_store: BlobStore, workspace_id: UUID, principal: Principal
) -> UUID:
    """A Dataset Version carrying one scoring-shaped table, `_scoring_frame`'s own shape."""
    return await _dataset_version(
        database, blob_store, workspace_id, principal, _scoring_frame(8)
    )


@pytest.fixture
async def compiled_rating_version(
    api_client: TestClient,
    headers: dict[str, str],
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    principal: Principal,
    grant: Any,
) -> None:
    register_scoring_handlers()
    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )


def _body(dataset_version_id: UUID, **overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "dataset_version_id": str(dataset_version_id),
        "rating_version_refs": [SCORED_REF],
        "chunk_rows": 2,
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------------------
# Step 1: the 202 test — the route answers 202 with a Job, and polling it to completion
# yields a parquet retrievable from the blob store.
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-36")
async def test_the_route_answers_202_and_the_completed_job_yields_a_retrievable_parquet(
    api_client: TestClient,
    batch_headers: dict[str, str],
    scoring_table: UUID,
    compiled_rating_version: None,
    database: Database,
    blob_store: BlobStore,
) -> None:
    response = api_client.post(
        BATCH_URL, json=_body(scoring_table), headers=batch_headers
    )

    assert response.status_code == 202, response.text
    body = response.json()
    assert body["kind"] == "score.batch", body
    assert body["status"] == "queued", body
    assert response.headers["Location"] == f"/api/v1/jobs/{body['id']}"

    job_id = UUID(body["id"])
    status = await execute_job(database, job_id, blob_store)
    assert status is JobStatus.SUCCEEDED, status

    # Read the Job's own result back through the ORM (the same pattern
    # `test_scoring_handlers.py`'s `_summary` helper uses), the completed Job's persisted
    # state rather than a second call through the route.
    async with database.session() as session:
        job_row = await session.get(JobRow, job_id)
        assert job_row is not None
        assert job_row.result is not None
        assert job_row.result["kind"] == "blob"
        summary_row = await session.get(BlobRow, job_row.result["ref"])
        assert summary_row is not None
        summary_payload = await blob_store.read(to_ref(summary_row))

    summary = json.loads(summary_payload)
    assert summary["dataset_version_id"] == str(scoring_table)
    ref_result = summary["results"][0]
    assert ref_result["rating_version_ref"] == SCORED_REF
    assert ref_result["row_count"] == 8

    output_sha256 = ref_result["output_blob_sha256"]
    assert output_sha256 is not None
    async with database.session() as session:
        output_row = await session.get(BlobRow, output_sha256)
        assert output_row is not None
        output_bytes = await blob_store.read(to_ref(output_row))
    output_frame = pl.read_parquet(io.BytesIO(output_bytes))
    assert output_frame.height == 8
    assert set(output_frame["rating_version_ref"].unique().to_list()) == {SCORED_REF}


# --------------------------------------------------------------------------------------
# Step 2: RBAC, three cases (Ruling 18's pattern, mirrored from `test_score.py`).
# --------------------------------------------------------------------------------------


@pytest.mark.req("NFR-RATE-11")
async def test_a_scoped_account_holding_score_batch_may_call_the_route(
    api_client: TestClient,
    batch_headers: dict[str, str],
    execute_only_headers: dict[str, str],
    scoring_table: UUID,
    compiled_rating_version: None,
) -> None:
    """Ruling 18's first two cases, paired in one test on purpose (`test_score.py`'s own
    reasoning): asserting only the permitted case would pass against a route with no
    permission check at all, and asserting only the refusal would pass against a route
    refusing everyone."""
    body = _body(scoring_table)

    permitted = api_client.post(BATCH_URL, json=body, headers=batch_headers)
    refused = api_client.post(BATCH_URL, json=body, headers=execute_only_headers)

    assert permitted.status_code == 202, permitted.text
    assert refused.status_code == 403, refused.text


@pytest.mark.req("NFR-RATE-11")
def test_a_key_relabelled_to_another_environment_is_refused_at_authentication(
    api_client: TestClient, headers: dict[str, str], workspace_id: UUID
) -> None:
    """FR-PLAT-30: the environment segment of a key is a label, not an authorisation. Only
    the secret is hashed, so relabelling `uat` to `prod` still verifies and must still be
    refused, because `prod` is not among the environments the account was granted."""
    created = api_client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "batch-engine-uat-scoped",
            "environments": ["uat"],
            "permissions": ["score:batch"],
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    key = created.json()["key"]
    namespace, environment, prefix, secret = key.split("_", 3)
    assert environment == "uat", key

    relabelled = "_".join([namespace, "prod", prefix, secret])
    refused = api_client.post(
        BATCH_URL,
        json=_body(UUID(int=0)),
        headers={"X-API-Key": relabelled, "Workspace-Id": str(workspace_id)},
    )

    assert refused.status_code == 401, refused.text
    assert refused.json()["code"] == "ENVIRONMENT_SCOPE_DENIED"

    # Inversion: the untampered key is not refused at authentication — it fails later
    # (404, since `UUID(int=0)` names no real Dataset Version) and for another reason.
    intact = api_client.post(
        BATCH_URL,
        json=_body(UUID(int=0)),
        headers={"X-API-Key": key, "Workspace-Id": str(workspace_id)},
    )
    assert intact.status_code != 401, intact.text
