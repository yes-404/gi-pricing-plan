"""The audit log API (FR-GOV-22, FR-GOV-23, FR-GOV-24, FR-GOV-5)."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Environment, Settings
from app.db.session import Database
from app.main import create_app
from app.platform import audit
from model_schema import ActorKind, JobSource, Principal, new_uuid7


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def auditor_headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("auditor")
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


async def _events(database: Database, workspace_id, principal: Principal, n: int = 3):
    async with database.unit_of_work() as session:
        for i in range(n):
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=principal,
                source=JobSource.API,
                action="rating_version.approved" if i else "model.submitted",
                entity_ref=f"model:motor-ad-frequency@{i + 1}",
                justification=f"reason number {i}",
            )


@pytest.mark.req("FR-GOV-23")
async def test_the_log_is_queryable(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal)
    body = client.get("/api/v1/audit", headers=auditor_headers).json()
    assert body["total_estimate"] == 3
    assert len(body["items"]) == 3
    # Newest first, ordered by the per-workspace sequence rather than by timestamp: events
    # written in one transaction share `at`.
    assert [i["sequence"] for i in body["items"]] == [3, 2, 1]


@pytest.mark.req("FR-GOV-23")
async def test_filters_narrow_by_action_entity_actor_and_text(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal)

    by_action = client.get(
        "/api/v1/audit?action=model.submitted", headers=auditor_headers
    ).json()
    assert [i["action"] for i in by_action["items"]] == ["model.submitted"]

    by_entity = client.get(
        "/api/v1/audit?entity=model:motor-ad-frequency@2", headers=auditor_headers
    ).json()
    assert len(by_entity["items"]) == 1

    by_actor = client.get(
        f"/api/v1/audit?actor={principal.id}", headers=auditor_headers
    ).json()
    assert by_actor["total_estimate"] == 3

    by_text = client.get("/api/v1/audit?q=number 1", headers=auditor_headers).json()
    assert len(by_text["items"]) == 1


@pytest.mark.req("FR-GOV-23")
async def test_the_query_is_cursor_paginated(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal, n=5)
    seen: list[int] = []
    cursor = None
    for _ in range(10):
        url = f"/api/v1/audit?limit=2{f'&cursor={cursor}' if cursor else ''}"
        body = client.get(url, headers=auditor_headers).json()
        seen.extend(i["sequence"] for i in body["items"])
        cursor = body["next_cursor"]
        if cursor is None:
            break
    assert seen == [5, 4, 3, 2, 1]


@pytest.mark.req("FR-OVR-13")
async def test_another_workspaces_events_are_invisible(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """Negative: the audit log is the most sensitive table in the system."""
    await _events(database, new_uuid7(), principal)
    body = client.get("/api/v1/audit", headers=auditor_headers).json()
    assert body["items"] == []


@pytest.mark.req("FR-GOV-24")
async def test_verify_reports_an_intact_chain(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal)
    body = client.get("/api/v1/audit/verify", headers=auditor_headers).json()
    assert body["intact"] is True
    assert body["events_checked"] == 3
    assert body["broken_at_sequence"] is None


@pytest.mark.req("FR-GOV-24")
async def test_verify_reports_a_break_rather_than_failing(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """A broken chain is a finding, not a server error.

    Tampering is applied with `session_replication_role = replica`, which disables the
    append-only triggers — the privileged path the chain exists to detect, since privileges
    and triggers cannot prevent it.
    """
    await _events(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        await session.execute(text("SET LOCAL session_replication_role = replica"))
        await session.execute(
            text(
                "UPDATE audit_events SET justification = 'edited' "
                "WHERE workspace_id = :ws AND sequence = 2"
            ).bindparams(ws=workspace_id)
        )

    response = client.get("/api/v1/audit/verify", headers=auditor_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["intact"] is False
    assert body["broken_at_sequence"] == 2
    assert "does not match" in body["reason"]


@pytest.mark.req("FR-GOV-23")
async def test_csv_export_carries_the_hashes(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """The hashes are the point: an auditor recomputes them without the platform's help."""
    await _events(database, workspace_id, principal)
    response = client.get("/api/v1/audit/export?format=csv", headers=auditor_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    lines = [line for line in response.text.splitlines() if line]
    assert lines[0].split(",")[-1] == "event_hash"
    assert len(lines) == 4
    assert "sha256:" in lines[1]


@pytest.mark.req("FR-GOV-23")
async def test_json_export_is_line_delimited(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """An audit log is unbounded; a consumer must be able to start before the export ends."""
    await _events(database, workspace_id, principal)
    response = client.get("/api/v1/audit/export?format=json", headers=auditor_headers)
    lines = [json.loads(line) for line in response.text.splitlines() if line]
    assert len(lines) == 3
    assert lines[0]["event_hash"].startswith("sha256:")


@pytest.mark.req("FR-GOV-5")
async def test_an_auditor_can_read_the_log_but_the_api_offers_no_write(
    client: TestClient, auditor_headers
) -> None:
    """FR-GOV-22: events are emitted by the transactions that cause them, never posted.

    An endpoint that could append would be a way to write history without doing anything.
    """
    assert client.get("/api/v1/audit", headers=auditor_headers).status_code == 200
    for method in ("post", "put", "delete", "patch"):
        response = getattr(client, method)("/api/v1/audit", headers=auditor_headers)
        assert response.status_code in {404, 405}, method


@pytest.mark.req("FR-GOV-2")
def test_reading_the_audit_log_requires_the_permission(
    client: TestClient, workspace_id, principal
) -> None:
    """Negative: without audit:read the log is not readable, however authenticated."""
    response = client.get(
        "/api/v1/audit",
        headers={
            DEV_PRINCIPAL_HEADER: str(principal.id),
            DEV_WORKSPACE_HEADER: str(workspace_id),
        },
    )
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-GOV-5")
async def test_an_analyst_cannot_read_the_audit_log(
    client: TestClient, workspace_id, grant
) -> None:
    """`audit:read` belongs to read-everything roles, not to everyone who can read data."""
    analyst = new_uuid7()
    await grant("analyst", principal_id=analyst)
    response = client.get(
        "/api/v1/audit",
        headers={
            DEV_PRINCIPAL_HEADER: str(analyst),
            DEV_WORKSPACE_HEADER: str(workspace_id),
        },
    )
    assert response.status_code == 403


@pytest.mark.req("FR-GOV-21")
async def test_an_event_carries_everything_the_requirement_lists(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    from app.observability.trace import bind_trace_id, reset_trace_id

    token = bind_trace_id("4bf92f3577b34da6a3ce929d0e0e4736")
    try:
        async with database.unit_of_work() as session:
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=Principal(kind=ActorKind.USER, id=principal.id, display="a@b.example"),
                source=JobSource.UI,
                action="rating_version.approved",
                entity_ref="rating_version:motor-gb@27",
                before={"status": "review"},
                after={"status": "approved"},
                justification="Dislocation within the agreed envelope.",
            )
    finally:
        reset_trace_id(token)

    item = client.get("/api/v1/audit", headers=auditor_headers).json()["items"][0]
    assert item["actor"]["display"] == "a@b.example"
    assert item["source"] == "ui"
    assert item["action"] == "rating_version.approved"
    assert item["entity_ref"] == "rating_version:motor-gb@27"
    assert item["before"] == {"status": "review"}
    assert item["justification"].startswith("Dislocation")
    assert item["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert item["event_hash"].startswith("sha256:")
