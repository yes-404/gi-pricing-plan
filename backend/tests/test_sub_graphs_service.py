"""Sub-graph service (WK-1250 Slice 1, 03 §4.11): create, revise, read, list, resolve, audit.

Covers FR-217 (the stored, versioned fragment), FR-227 (output-port types at create),
`00` FR-4 (immutable versions) and `06` FR-368 (an Audit Event in the write's transaction).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import func, select

from app.db.models import AuditEventRow, SubGraphVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import sub_graphs as service
from model_schema import ArtifactRef, Principal, new_uuid7

pytestmark = pytest.mark.req("FR-217")


def content(**changes: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "relativity", "required": True}],
        "steps": [
            {"step_id": "s_ncd", "type": "table", "label": "NCD ladder",
             "rate_table_ref": "rate_table:ncd@2", "key_expr": ["ncd_years"],
             "consumes": "ncd_years", "produces": "ncd_factor"}
        ],
        "change_note": "first",
    }
    body.update(changes)
    return body


async def _counts(database: Database, workspace_id: UUID) -> tuple[int, int]:
    async with database.session() as session:
        rows = await session.scalar(
            select(func.count()).select_from(SubGraphVersionRow).where(
                SubGraphVersionRow.workspace_id == workspace_id
            )
        )
        events = await session.scalar(
            select(func.count()).select_from(AuditEventRow).where(
                AuditEventRow.workspace_id == workspace_id,
                AuditEventRow.action == "sub_graph.created",
            )
        )
    return int(rows or 0), int(events or 0)


async def test_create_writes_version_one_and_one_audit_event(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    created = await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    assert (created.slug, created.version) == ("ncd-ladder", 1)
    assert await _counts(database, workspace_id) == (1, 1)
    async with database.session() as session:
        event = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalar_one()
    assert event.action == "sub_graph.created"
    assert event.entity_ref == "sub_graph:ncd-ladder@1"
    assert event.after["change_note"] == "first"
    assert [p["name"] for p in event.after["inputs"]] == ["ncd_years"]
    assert [p["name"] for p in event.after["outputs"]] == ["ncd_factor"]


async def test_create_on_an_existing_slug_is_409_and_changes_nothing(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    async with database.session() as session:
        before = (
            await session.execute(
                select(SubGraphVersionRow.content).where(
                    SubGraphVersionRow.workspace_id == workspace_id
                )
            )
        ).scalar_one()
    with pytest.raises(PlatformError) as caught:
        await service.create_sub_graph(
            database, workspace_id, principal,
            {"slug": "ncd-ladder", **content(change_note="second")},
        )
    assert (caught.value.status_code, caught.value.code) == (409, "VALIDATION_FAILED")
    async with database.session() as session:
        after = (
            await session.execute(
                select(SubGraphVersionRow.content).where(
                    SubGraphVersionRow.workspace_id == workspace_id
                )
            )
        ).scalar_one()
    assert after == before
    assert await _counts(database, workspace_id) == (1, 1)


async def test_a_new_version_is_the_maximum_plus_one(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    second = await service.create_version(
        database, workspace_id, principal, "ncd-ladder", content(change_note="two")
    )
    third = await service.create_version(
        database, workspace_id, principal, "ncd-ladder", content(change_note="three")
    )
    assert (second.version, third.version) == (2, 3)
    assert (await service.get_version(database, workspace_id, "ncd-ladder", 2)).change_note == "two"
    assert await _counts(database, workspace_id) == (3, 3)


async def test_versions_on_an_unknown_slug_is_not_found(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    with pytest.raises(PlatformError) as caught:
        await service.create_version(database, workspace_id, principal, "nope", content())
    assert (caught.value.status_code, caught.value.code) == (404, "NOT_FOUND")
    assert await _counts(database, workspace_id) == (0, 0)


async def test_a_refused_write_leaves_no_row_and_no_event(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    bad = content(outputs=[{"name": "ncd_factor", "type": "money_minor", "required": True}])
    bad["steps"] = [
        {"step_id": "s_x", "type": "expression", "label": "x", "expr": "ncd_years",
         "result_type": "string", "consumes": "ncd_years", "produces": "ncd_factor"}
    ]
    with pytest.raises(PlatformError) as caught:
        await service.create_sub_graph(
            database, workspace_id, principal, {"slug": "bad-one", **bad}
        )
    assert (caught.value.status_code, caught.value.code) == (422, "RATING_TYPE_MISMATCH")
    assert await _counts(database, workspace_id) == (0, 0)


async def test_a_lost_numbering_race_is_409(
    database: Database,
    workspace_id: UUID,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    real = service._latest_version

    async def stale(session: Any, workspace: UUID, slug: str) -> int | None:
        seen = await real(session, workspace, slug)
        async with database.unit_of_work() as other:  # a competing writer wins the number
            other.add(
                SubGraphVersionRow(
                    workspace_id=workspace, slug=slug, version=(seen or 0) + 1,
                    content={}, change_note="rival", created_by=new_uuid7(),
                )
            )
        return seen

    monkeypatch.setattr(service, "_latest_version", stale)
    with pytest.raises(PlatformError) as caught:
        await service.create_version(database, workspace_id, principal, "ncd-ladder", content())
    assert (caught.value.status_code, caught.value.code) == (409, "VALIDATION_FAILED")
    assert await _counts(database, workspace_id) == (2, 1)


async def test_list_versions_is_cursor_paginated(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    for n in range(2):
        await service.create_version(
            database, workspace_id, principal, "ncd-ladder", content(change_note=str(n))
        )
    first = await service.list_versions(database, workspace_id, "ncd-ladder", None, 2)
    assert [i.version for i in first.items] == [1, 2]
    assert first.next_cursor is not None
    assert first.total_estimate == 3
    rest = await service.list_versions(database, workspace_id, "ncd-ladder", first.next_cursor, 2)
    assert [i.version for i in rest.items] == [3]
    assert rest.next_cursor is None


async def test_resolve_ref_returns_exactly_the_addressed_version(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    await service.create_version(
        database, workspace_id, principal, "ncd-ladder", content(change_note="two")
    )
    async with database.session() as session:
        resolved = await service.resolve_ref(
            session,
            workspace_id=workspace_id,
            ref=ArtifactRef.model_validate("sub_graph:ncd-ladder@1"),
        )
    assert (resolved.version, resolved.change_note) == (1, "first")


@pytest.mark.parametrize(
    ("ref", "same_workspace", "status_code", "code", "cause"),
    [
        ("sub_graph:nope@1", True, 404, "NOT_FOUND", "no sub-graph"),
        ("sub_graph:ncd-ladder@9", True, 404, "NOT_FOUND", "no sub-graph"),
        ("rate_table:ncd-ladder@1", True, 422, "VALIDATION_FAILED", "not a sub_graph"),
        ("sub_graph:ncd-ladder@1", False, 404, "NOT_FOUND", "no sub-graph"),
    ],
)
async def test_resolve_ref_refuses_by_cause(
    database: Database,
    workspace_id: UUID,
    principal: Principal,
    ref: str,
    same_workspace: bool,
    status_code: int,
    code: str,
    cause: str,
) -> None:
    await service.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **content()}
    )
    asked_in = workspace_id if same_workspace else new_uuid7()
    async with database.session() as session:
        with pytest.raises(PlatformError) as caught:
            await service.resolve_ref(
                session, workspace_id=asked_in, ref=ArtifactRef.model_validate(ref)
            )
    assert (caught.value.status_code, caught.value.code) == (status_code, code)
    assert cause in (caught.value.detail or "")
