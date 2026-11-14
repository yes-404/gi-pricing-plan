"""FR-383: the uniform history of a governed artifact, `GET /api/v1/artifacts/{ref}/history`.

One shape for every artifact type, read from the audit log by exact `entity_ref`.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.session import Database
from app.main import create_app
from app.platform import audit
from app.platform.audit import field_diff
from model_schema import ArtifactHistory, JobSource, Principal, new_uuid7


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
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


def _headers(workspace_id, principal: Principal) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def auditor_headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("auditor")
    return _headers(workspace_id, principal)


def _history(client: TestClient, headers: dict[str, str], ref: str):
    return client.get(f"/api/v1/artifacts/{ref}/history", headers=headers)


async def _record(
    database: Database, workspace_id, principal, ref, action, before, after, why=None
) -> None:
    async with database.unit_of_work() as session:
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=principal,
            source=JobSource.API,
            action=action,
            entity_ref=ref,
            before=before,
            after=after,
            justification=why,
        )


#: Three artifact types, one lifecycle each: created, then moved. The shape must not differ.
_TYPES = ("dataset_version:motor-claims@3", "rating_version:motor-gb@27", "model:motor-freq@2")


@pytest.mark.req("FR-383")
async def test_every_artifact_type_returns_the_same_shape(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    for ref in _TYPES:
        await _record(database, workspace_id, principal, ref, "artifact.created", None,
                      {"status": "draft"})
        await _record(database, workspace_id, principal, ref, "artifact.submitted",
                      {"status": "draft"}, {"status": "review"}, why="ready for review")
    shapes = []
    for ref in _TYPES:
        response = client.get(f"/api/v1/artifacts/{ref}/history", headers=auditor_headers)
        assert response.status_code == 200, response.text
        body = response.json()
        history = ArtifactHistory.model_validate(body)
        assert str(history.ref) == ref
        assert [e.action for e in history.events] == ["artifact.created", "artifact.submitted"]
        moved = history.events[1]
        assert (moved.transition.from_, moved.transition.to) == ("draft", "review")
        assert moved.justification == "ready for review"
        assert moved.actor.display == principal.display
        shapes.append((sorted(body), sorted(body["events"][1])))
    assert all(shape == shapes[0] for shape in shapes)


@pytest.mark.req("FR-383")
async def test_history_is_read_by_exact_ref_not_by_prefix(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _record(database, workspace_id, principal, "model:motor-freq@2", "model.fitted", None,
                  {"status": "fitted"})
    await _record(database, workspace_id, principal, "model:motor-freq@20", "model.fitted", None,
                  {"status": "fitted"})
    body = _history(client, auditor_headers, "model:motor-freq@2").json()
    assert len(body["events"]) == 1


@pytest.mark.req("FR-383")
async def test_a_pre_rename_return_reads_as_returned(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """C1: a stored `model.fitted` whose `before.status` is review is a return."""
    await _record(database, workspace_id, principal, "model:motor-freq@2", "model.fitted",
                  {"status": "review"}, {"status": "fitted"})
    body = _history(client, auditor_headers, "model:motor-freq@2").json()
    assert body["events"][0]["action"] == "model.returned"
    assert body["events"][0]["transition"] == {"from": "review", "to": "fitted"}


@pytest.mark.req("FR-383")
def test_the_diff_is_the_field_level_change_of_before_and_after() -> None:
    changes = field_diff(
        {"status": "draft", "terms": {"region": 1, "age": 2}, "same": 5},
        {"status": "review", "terms": {"region": 1, "age": 3}, "same": 5, "added": [1]},
    )
    assert [(c.path, c.before, c.after) for c in changes] == [
        ("added", None, [1]),
        ("status", "draft", "review"),
        ("terms.age", 2, 3),
    ]
    assert field_diff(None, None) == []


@pytest.mark.req("FR-383")
async def test_refusals_unknown_malformed_and_another_workspace(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _record(database, new_uuid7(), principal, "model:motor-freq@2", "model.fitted", None,
                  {"status": "fitted"})
    other = client.get("/api/v1/artifacts/model:motor-freq@2/history", headers=auditor_headers)
    assert other.status_code == 404  # an unknown ref, and another workspace's events are invisible
    assert other.json()["code"] == "NOT_FOUND"
    bad = client.get("/api/v1/artifacts/not-a-ref/history", headers=auditor_headers)
    assert bad.status_code == 422
    uuid_ref = client.get(
        f"/api/v1/artifacts/nonsense:{new_uuid7()}@1/history", headers=auditor_headers
    )
    assert uuid_ref.status_code == 422


@pytest.mark.req("FR-383")
@pytest.mark.parametrize("role", ["analyst", "pricing_actuary"])
async def test_a_role_without_audit_read_is_refused(
    client: TestClient, workspace_id, grant, role
) -> None:
    caller = new_uuid7()
    await grant(role, principal_id=caller)
    response = client.get(
        "/api/v1/artifacts/model:motor-freq@2/history",
        headers={DEV_PRINCIPAL_HEADER: str(caller), "Workspace-Id": str(workspace_id)},
    )
    assert response.status_code == 403
