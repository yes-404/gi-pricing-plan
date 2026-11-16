"""A decided approval request's decision does not change (`06` FR-351, clause of 2026-11-16;
ADR-2157).

The expectation is derived from the state machine itself (`VALID_APPROVAL_TRANSITIONS`): a
status change is permitted exactly along its edges, and the decision's other two columns,
`decided_at` and `withdrawn_reason`, move only with such an edge. The same sweep with the guard
disabled (owner, rolled back) is not refused by it. The route-level case is the one the
decision hook decides: withdrawing the request of an approved rating version.
"""

from __future__ import annotations

import pytest
from backend.tests.conftest_db import disable_trigger
from backend.tests.test_api_approvals import (  # noqa: F401  (fixtures and helpers)
    _create_authored,
    _headers,
    _require_two_approvals,
    api_settings,
    client,
    submitter_headers,
)
from backend.tests.test_rating_version_content_guard import _sqlstate, rolled_back
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.session import Database
from model_schema import VALID_APPROVAL_TRANSITIONS, ApprovalStatus, new_uuid7

GUARD = "approval_requests_decision_guard"
STATUSES = tuple(s.value for s in ApprovalStatus)


async def _plant(conn: AsyncConnection, status: str, *, slug: str) -> str:
    """A request at `status`, decided (with `decided_at`) unless it is still open."""
    request_id = new_uuid7()
    await conn.execute(text("SET LOCAL app.approval_decision = 'on'"))
    await conn.execute(
        text(
            "INSERT INTO approval_requests (id, workspace_id, artifact_ref, artifact_type, "
            "submitted_by, change_summary, status, approvers_required, decided_at, "
            "withdrawn_reason) VALUES (:id, gen_random_uuid(), :ref, 'model', gen_random_uuid(), "
            "'c', :status, 1, CASE WHEN :status IN ('draft', 'review') THEN NULL ELSE now() END, "
            "CASE WHEN :status = 'withdrawn' THEN 'why' END)"
        ),
        {"id": request_id, "ref": f"model:{slug}@1", "status": status},
    )
    return str(request_id)


async def _status_edges(conn: AsyncConnection) -> dict[tuple[str, str], str | None]:
    """(from, to) -> the SQLSTATE of one status UPDATE, every pair of the six statuses."""
    out: dict[tuple[str, str], str | None] = {}
    for old in STATUSES:
        for new in STATUSES:
            request_id = await _plant(conn, old, slug=f"{old}-{new}")
            out[(old, new)] = await _sqlstate(
                conn, f"UPDATE approval_requests SET status = '{new}' WHERE id = '{request_id}'"
            )
    return out


def _permitted() -> set[tuple[str, str]]:
    return {
        (old.value, new.value) for old, edges in VALID_APPROVAL_TRANSITIONS.items() for new in edges
    } | {(s, s) for s in STATUSES}


@pytest.mark.req("FR-351")
async def test_a_status_changes_only_along_the_state_machines_edges(database: Database) -> None:
    async with rolled_back(database) as conn:
        who = (await conn.execute(text("SELECT current_user"))).scalar_one()
        assert who == "gip_app_login", who
        results = await _status_edges(conn)
    refused = {edge for edge, state in results.items() if state == "42501"}
    assert refused == {(o, n) for o in STATUSES for n in STATUSES} - _permitted()
    # every other edge ran, so none was refused by something that is not the guard
    assert {edge for edge, state in results.items() if state is None} == _permitted()


@pytest.mark.req("FR-351")
async def test_a_decided_requests_other_decision_columns_are_held(database: Database) -> None:
    async with rolled_back(database) as conn:
        results = {}
        for status in ("approved", "rejected", "changes_requested", "withdrawn", "review"):
            request_id = await _plant(conn, status, slug=f"col-{status}")
            for column, value in (
                ("decided_at", "now() + interval '1 day'"),
                ("withdrawn_reason", "'changed'"),
            ):
                results[(status, column)] = await _sqlstate(
                    conn,
                    f"UPDATE approval_requests SET {column} = {value} WHERE id = '{request_id}'",
                )
    assert set(results.values()) == {"42501"}, results


@pytest.mark.req("FR-351")
async def test_an_update_that_changes_no_decision_column_is_allowed(database: Database) -> None:
    async with rolled_back(database) as conn:
        request_id = await _plant(conn, "approved", slug="same")
        same = await _sqlstate(
            conn,
            "UPDATE approval_requests SET status = status, decided_at = decided_at "
            f"WHERE id = '{request_id}'",
        )
    assert same is None


@pytest.mark.req("FR-351")
async def test_each_edge_refusal_is_the_guards_own(owner_database: Database) -> None:
    """The control: with the guard disabled the same sweep is refused by nothing."""
    async with rolled_back(owner_database) as conn:
        await disable_trigger(conn, "approval_requests", GUARD)
        results = await _status_edges(conn)
    assert {edge for edge, state in results.items() if state is not None} == set()


@pytest.mark.req("FR-351")
async def test_withdrawing_the_request_of_an_approved_rating_version_moves_nothing(
    client: TestClient,  # noqa: F811
    database: Database,
    workspace_id,
    grant,
    submitter_headers,  # noqa: F811
) -> None:
    """The decision hook never reopens an approved version: the withdrawal is refused 409 and
    the request and the version both stay `approved` (the guard's table has no such edge)."""
    await _require_two_approvals(client, workspace_id, grant, database, "rating_version")
    slug = "withdraw-approved"
    ref = await _create_authored(database, workspace_id, "rating_version", slug, 1, new_uuid7())
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": ref, "change_summary": "Ship."},
        headers=submitter_headers,
    )
    assert created.status_code == 201, created.text
    request_id = created.json()["id"]
    first, second = new_uuid7(), new_uuid7()
    for who in (first, second):
        await grant("approver", principal_id=who)
        decided = client.post(
            f"/api/v1/approval-requests/{request_id}/decide",
            json={"decision": "approve", "comment": "Reviewed."},
            headers=_headers(who, workspace_id),
        )
        assert decided.status_code == 200, decided.text
    assert decided.json()["status"] == "approved"

    withdrawn = client.post(
        f"/api/v1/approval-requests/{request_id}/withdraw",
        json={"reason": "second thoughts"},
        headers=_headers(first, workspace_id),
    )
    assert withdrawn.status_code == 409, withdrawn.text
    assert withdrawn.json()["code"] == "APPROVAL_SUBJECT_NOT_IN_REVIEW"

    async with database.session() as session:
        request_status = (
            await session.execute(
                text("SELECT status, withdrawn_reason FROM approval_requests WHERE id = :id"),
                {"id": request_id},
            )
        ).one()
        version_status = (
            await session.execute(
                text("SELECT status FROM rating_versions WHERE workspace_id = :w AND slug = :s"),
                {"w": workspace_id, "s": slug},
            )
        ).scalar_one()
    assert tuple(request_status) == ("approved", None)
    assert version_status == "approved"
