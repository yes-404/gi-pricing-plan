"""The audit log API (FR-370, FR-371, FR-372, FR-346)."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from backend.tests.test_audit import _days, _seed
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.session import Database
from app.main import create_app
from app.platform import audit
from model_schema import (
    BUILTIN_ROLES,
    ActorKind,
    AuditEventRecord,
    JobSource,
    Permission,
    Principal,
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
        # Shadows conftest's `api_settings`, so it inherits no bucket — set defensively,
        # not because this file reads a blob today (`conftest_db.test_blob_bucket`).
        blob_bucket=test_blob_bucket(),
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
        "Workspace-Id": str(workspace_id),
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


@pytest.mark.req("FR-371")
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


@pytest.mark.req("FR-371")
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


@pytest.mark.req("FR-371")
async def test_the_returned_filter_finds_legacy_and_new_rows(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """C1 (#1783, Q3 (a2)): `<type>.returned` also finds the pre-rename spelling.

    Before the rename a return from review was written as the forward state's name, with
    `before.status == "review"`. The stored rows keep it (FR-370), so the filter has to find
    both, and must not match a forward `model.fitted` (draft → fitted).
    """
    async with database.unit_of_work() as session:
        for action, before, ref in (
            ("model.fitted", "draft", "model:fam@1"),  # forward: never a return
            ("model.fitted", "review", "model:fam@2"),  # legacy return
            ("model.returned", "review", "model:fam@3"),  # new return
        ):
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=principal,
                source=JobSource.API,
                action=action,
                entity_ref=ref,
                before={"status": before},
            )
    body = client.get("/api/v1/audit?action=model.returned", headers=auditor_headers).json()
    assert sorted(i["entity_ref"] for i in body["items"]) == ["model:fam@2", "model:fam@3"]
    forward = client.get("/api/v1/audit?action=model.fitted", headers=auditor_headers).json()
    assert sorted(i["entity_ref"] for i in forward["items"]) == ["model:fam@1", "model:fam@2"]


@pytest.mark.req("FR-371")
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


@pytest.mark.req("FR-16")
async def test_another_workspaces_events_are_invisible(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """Negative: the audit log is the most sensitive table in the system."""
    await _events(database, new_uuid7(), principal)
    body = client.get("/api/v1/audit", headers=auditor_headers).json()
    assert body["items"] == []


@pytest.mark.req("FR-372")
async def test_verify_reports_an_intact_chain(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal)
    body = client.get("/api/v1/audit/verify", headers=auditor_headers).json()
    assert body["intact"] is True
    assert body["events_checked"] == 3
    assert body["broken_at_sequence"] is None


@pytest.mark.req("FR-372")
async def test_verify_reports_a_break_rather_than_failing(
    client: TestClient, owner_database: Database, workspace_id, principal, auditor_headers
) -> None:
    """A broken chain is a finding, not a server error.

    Tampering is applied with `session_replication_role = replica`, which disables the
    append-only triggers — the privileged path the chain exists to detect, since privileges
    and triggers cannot prevent it.
    """
    await _events(owner_database, workspace_id, principal)
    async with owner_database.unit_of_work() as session:
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


@pytest.mark.req("FR-371")
async def test_csv_export_is_a_report_that_carries_the_hashes(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """The CSV is a readable report with both hashes. It is not recomputable: it has no
    `workspace_id`, `before` or `after`. JSON Lines is the evidence form (next test)."""
    await _events(database, workspace_id, principal)
    response = client.get("/api/v1/audit/export?format=csv", headers=auditor_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    lines = [line for line in response.text.splitlines() if line]
    assert lines[0].split(",")[-1] == "event_hash"
    assert len(lines) == 4
    assert "sha256:" in lines[1]


@pytest.mark.req("FR-451")
def test_export_publishes_csv_and_json_lines(client: TestClient) -> None:
    """FD-1684: the format query picks one of two media types; the contract publishes both."""
    content = client.app.openapi()["paths"]["/api/v1/audit/export"]["get"]["responses"]["200"][
        "content"
    ]
    assert set(content) == {"text/csv", "application/x-ndjson"}
    assert content["text/csv"]["schema"] == {"type": "string"}
    assert content["application/x-ndjson"]["schema"] == {"type": "string"}


@pytest.mark.req("FR-371")
async def test_json_export_is_line_delimited(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """An audit log is unbounded; a consumer must be able to start before the export ends."""
    await _events(database, workspace_id, principal)
    response = client.get("/api/v1/audit/export?format=json", headers=auditor_headers)
    assert response.headers["content-type"].startswith("application/x-ndjson")
    lines = [json.loads(line) for line in response.text.splitlines() if line]
    assert len(lines) == 3
    assert lines[0]["event_hash"].startswith("sha256:")


@pytest.mark.req("FR-372")
async def test_json_export_recomputes_every_hash_without_the_platform(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """The export is evidence: each line validates as the contract's shape, and its hash and
    link recompute from the line alone, using nothing but `model_schema`."""
    await _events(database, workspace_id, principal)
    response = client.get("/api/v1/audit/export?format=json", headers=auditor_headers)
    events = [
        AuditEventRecord.model_validate_json(line) for line in response.text.splitlines() if line
    ]
    assert [e.sequence for e in events] == [1, 2, 3]
    assert all(e.verify() for e in events)
    assert events[0].prev_event_hash is None
    assert [e.prev_event_hash for e in events[1:]] == [e.event_hash for e in events[:-1]]
    assert {e.workspace_id for e in events} == {workspace_id}


@pytest.mark.req("FR-371")
async def test_export_honours_the_query_filters(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """FR-371: an export is what the query shows. Every filter the query takes narrows it."""
    await _events(database, workspace_id, principal)
    for query in (
        "action=model.submitted",
        "entity=model:motor-ad-frequency@2",
        f"actor={principal.id}&action=rating_version.approved",
        "q=number 1",
    ):
        shown = client.get(f"/api/v1/audit?{query}", headers=auditor_headers).json()["items"]
        for fmt in ("json", "csv"):
            body = client.get(
                f"/api/v1/audit/export?format={fmt}&{query}", headers=auditor_headers
            ).text
            rows = [line for line in body.splitlines() if line]
            assert len(rows) - (fmt == "csv") == len(shown), (query, fmt)
        assert 0 < len(shown) < 3, query


@pytest.mark.req("FR-346")
async def test_an_auditor_can_read_the_log_but_the_api_offers_no_write(
    client: TestClient, auditor_headers
) -> None:
    """FR-370: events are emitted by the transactions that cause them, never posted.

    An endpoint that could append would be a way to write history without doing anything.
    """
    assert client.get("/api/v1/audit", headers=auditor_headers).status_code == 200
    for method in ("post", "put", "delete", "patch"):
        response = getattr(client, method)("/api/v1/audit", headers=auditor_headers)
        assert response.status_code in {404, 405}, method


@pytest.mark.req("FR-343")
async def test_reading_the_audit_log_requires_the_permission(
    client: TestClient, workspace_id, principal, membership
) -> None:
    """Negative: without audit:read the log is not readable, however authenticated.

    The caller holds a membership but no role (W6b-11): the membership check must pass
    so that the role check is the one that refuses.
    """
    await membership()
    response = client.get(
        "/api/v1/audit",
        headers={
            DEV_PRINCIPAL_HEADER: str(principal.id),
            "Workspace-Id": str(workspace_id),
        },
    )
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-346")
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
            "Workspace-Id": str(workspace_id),
        },
    )
    assert response.status_code == 403


@pytest.mark.req("FR-371")
def test_audit_read_is_held_by_exactly_the_four_read_everything_roles() -> None:
    """Pins the holder set `06` §4.1 records (#1548 (b), OQ-1726), so the spec sentence fails
    when it goes stale. Today's behaviour, pinned: it is green at the base by design."""
    holders = {role for role, perms in BUILTIN_ROLES.items() if Permission.AUDIT_READ in perms}
    assert holders == {"approver", "deployer", "auditor", "admin"}


@pytest.mark.req("FR-369")
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


@pytest.mark.req("FR-372")
async def test_verify_with_no_range_is_the_whole_chain(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal)
    body = client.get("/api/v1/audit/verify", headers=auditor_headers).json()
    assert body["whole_chain"] is True
    assert (body["first_sequence"], body["last_sequence"]) == (1, 3)
    assert body["from"] is None
    assert body["to"] is None


@pytest.mark.req("FR-372")
async def test_verify_takes_a_range_and_reports_what_it_checked(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _events(database, workspace_id, principal)
    far_future = "2999-01-01T00:00:00Z"
    body = client.get(
        f"/api/v1/audit/verify?from={far_future}", headers=auditor_headers
    ).json()
    assert body["whole_chain"] is False
    assert body["intact"] is True
    assert body["events_checked"] == 0
    assert body["first_sequence"] is None
    assert body["from"].startswith("2999-01-01")
    spanning = client.get(
        "/api/v1/audit/verify?from=2000-01-01T00:00:00Z&to=2999-01-01T00:00:00Z",
        headers=auditor_headers,
    ).json()
    assert (spanning["first_sequence"], spanning["last_sequence"]) == (1, 3)


@pytest.mark.req("FR-372")
async def test_verify_refuses_a_range_that_ends_before_it_starts(
    client: TestClient, auditor_headers
) -> None:
    response = client.get(
        "/api/v1/audit/verify?from=2026-02-01T00:00:00Z&to=2026-01-01T00:00:00Z",
        headers=auditor_headers,
    )
    assert response.status_code == 422


@pytest.mark.req("FR-372")
async def test_a_gap_reports_the_last_sequence_actually_verified(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    """#1858 L2: with event 3 absent the check verified 1 and 2 and broke at 4. The response
    must not name 3, a sequence that does not exist and was not verified, as the last one."""
    await _seed(database, workspace_id, principal, _days(5), missing=3)
    body = client.get("/api/v1/audit/verify", headers=auditor_headers).json()
    assert body["intact"] is False
    assert body["broken_at_sequence"] == 4
    assert (body["first_sequence"], body["last_sequence"], body["events_checked"]) == (1, 2, 2)


@pytest.mark.req("FR-372")
async def test_a_break_at_the_first_event_verified_nothing(
    client: TestClient, database: Database, workspace_id, principal, auditor_headers
) -> None:
    await _seed(database, workspace_id, principal, _days(3), tampered=1)
    body = client.get("/api/v1/audit/verify", headers=auditor_headers).json()
    broke = (body["broken_at_sequence"], body["events_checked"], body["last_sequence"])
    assert broke == (1, 0, None)


@pytest.mark.req("FR-372")
@pytest.mark.parametrize(
    "query",
    [
        "from=2026-01-01T00:00:00&to=2026-02-01T00:00:00Z",
        "from=2026-01-01T00:00:00Z&to=2026-02-01T00:00:00",
        "from=2026-01-01T00:00:00",
        "to=2026-02-01T00:00:00",
    ],
)
async def test_verify_refuses_a_bound_with_no_timezone(
    client: TestClient, auditor_headers, query: str
) -> None:
    """#1858 L3: a naive bound is ambiguous. It is a 422, never a 500."""
    response = client.get(f"/api/v1/audit/verify?{query}", headers=auditor_headers)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"
