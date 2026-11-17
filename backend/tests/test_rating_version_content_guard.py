"""Once a rating version has left `draft`, the database holds its content (`01` FR-44, `06`
FR-351, clauses of 2026-11-16; ADR-2157).

Every refusal here is shown to be the guard's own: the same statements run again with the
guard disabled (an owner transaction, rolled back) and are not refused by it. A guard test that
cannot go red proves nothing, so the column list is read from the database and a column the
sweep does not know fails the test, asking for a hold decision.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

import pytest
from backend.tests.conftest_db import disable_trigger
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.session import Database
from model_schema import new_uuid7

#: A new value for each of the table's columns, one UPDATE per column. A column absent from this
#: map fails `test_the_sweep_covers_every_column`.
NEW_VALUE: dict[str, str] = {
    "id": "gen_random_uuid()",
    "workspace_id": "gen_random_uuid()",
    "slug": "'other'",
    "version": "99",
    "status": "'retired'",
    "dataset_version_id": "gen_random_uuid()",
    "model_ref": "'model:other@9'",
    "created_at": "now() - interval '1 day'",
    "created_by": "gen_random_uuid()",
    "updated_at": "now() + interval '1 day'",
    "approval_request_id": "gen_random_uuid()",
    "algorithm_ref": "'rating_algorithm:other@1'",
    "pins": "'{\"changed\": 1}'::jsonb",
    "model_reference_mode": "'latest'",
    "effective_from": "now()",
    "effective_to": "now()",
    "bundle": '\'{"blob_sha256": "changed"}\'::jsonb',
    "change_summary": "'changed'",
    "evidence": "'{\"changed\": 2}'::jsonb",
}
#: A backwards status for a row that is past `review`; `retired` above is forward for `review`.
HELD_STATUSES = ("review", "approved", "live", "retired")
GUARD = "rating_versions_content_guard"
#: The two SQLSTATEs a refusal may carry: this guard's, and the approval guard's, which fires
#: first (by name) on the identity columns of an approved or later row.
REFUSED = {"42501", "GP001"}


async def _sqlstate(conn: AsyncConnection, sql: str) -> str | None:
    """The SQLSTATE `sql` raises, or None when it runs. Inside a savepoint, so the transaction
    survives the statement."""
    nested = await conn.begin_nested()
    try:
        await conn.execute(text(sql))
    except DBAPIError as exc:
        await nested.rollback()
        return getattr(exc.orig, "sqlstate", None) or getattr(exc.orig, "pgcode", None)
    await nested.rollback()
    return None


async def plant(conn: AsyncConnection, status: str, *, slug: str = "held") -> UUID:
    """A rating version at `status` with content in every content column, and the decided
    approval request its approved, live or retired status needs. In the caller's transaction."""
    ws, row_id = new_uuid7(), new_uuid7()
    ref = f"rating_version:{slug}@1"
    await conn.execute(text("SET LOCAL app.approval_decision = 'on'"))
    await conn.execute(
        text(
            "INSERT INTO approval_requests (id, workspace_id, artifact_ref, artifact_type, "
            "submitted_by, change_summary, status, approvers_required, decided_at) "
            "VALUES (gen_random_uuid(), :ws, :ref, 'rating_version', gen_random_uuid(), 'c', "
            "'approved', 1, now())"
        ),
        {"ws": ws, "ref": ref},
    )
    await conn.execute(
        text(
            "INSERT INTO rating_versions (id, workspace_id, slug, version, status, "
            "dataset_version_id, model_ref, created_by, approval_request_id, algorithm_ref, "
            "pins, model_reference_mode, bundle, change_summary, evidence) "
            "VALUES (:id, :ws, :slug, 1, :status, gen_random_uuid(), 'model:m@1', "
            "gen_random_uuid(), gen_random_uuid(), 'rating_algorithm:a@1', '{\"p\": 1}', 'exact', "
            '\'{"blob_sha256": "b", "content_hash": "h"}\', \'seed\', \'{"e": 1}\')'
        ),
        {"id": row_id, "ws": ws, "slug": slug, "status": status},
    )
    return row_id


@asynccontextmanager
async def rolled_back(database: Database) -> AsyncIterator[AsyncConnection]:
    async with database.engine.connect() as conn:
        tx = await conn.begin()
        try:
            yield conn
        finally:
            await tx.rollback()


async def _columns(conn: AsyncConnection) -> list[str]:
    rows = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = 'rating_versions' "
            "ORDER BY ordinal_position"
        )
    )
    return [r[0] for r in rows]


async def _sweep(
    conn: AsyncConnection, statuses: tuple[str, ...]
) -> dict[tuple[str, str], str | None]:
    """(status, column) -> the SQLSTATE of one UPDATE of that column on a row at that status."""
    out: dict[tuple[str, str], str | None] = {}
    for status in statuses:
        row_id = await plant(conn, status, slug=f"held-{status}")
        for column in await _columns(conn):
            new = NEW_VALUE[column]
            if column == "status" and status == "retired":
                new = "'live'"  # retired -> retired changes nothing, and a no-op is allowed
            sql = f"UPDATE rating_versions SET {column} = {new} WHERE id = '{row_id}'"
            out[(status, column)] = await _sqlstate(conn, sql)
    return out


@pytest.mark.req("FR-44")
async def test_the_sweep_covers_every_column(database: Database) -> None:
    async with rolled_back(database) as conn:
        assert set(await _columns(conn)) == set(NEW_VALUE)


@pytest.mark.req("FR-44")
async def test_a_version_past_draft_refuses_every_content_column(database: Database) -> None:
    """19 columns by 4 statuses, on the application's connection: each UPDATE is refused."""
    async with rolled_back(database) as conn:
        who = (await conn.execute(text("SELECT current_user"))).scalar_one()
        assert who == "gip_app_login", who
        results = await _sweep(conn, HELD_STATUSES)
    allowed = {key: state for key, state in results.items() if state not in REFUSED}
    assert allowed == {}


@pytest.mark.req("FR-44")
async def test_a_status_the_platform_does_not_define_is_not_accepted(database: Database) -> None:
    async with rolled_back(database) as conn:
        row_id = await plant(conn, "approved")
        state = await _sqlstate(
            conn, f"UPDATE rating_versions SET status = 'approvedx' WHERE id = '{row_id}'"
        )
    assert state in {"23514", "42501"}


@pytest.mark.req("FR-44")
async def test_the_status_check_names_the_five_statuses(database: Database) -> None:
    async with rolled_back(database) as conn:
        definition = (
            await conn.execute(
                text(
                    "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                    "WHERE conname = 'rating_version_status_is_in_the_lifecycle'"
                )
            )
        ).scalar_one()
    for status in ("draft", "review", "approved", "live", "retired"):
        assert f"'{status}'" in definition


@pytest.mark.req("FR-44")
async def test_a_draft_version_is_free(database: Database) -> None:
    async with rolled_back(database) as conn:
        row_id = await plant(conn, "draft")
        refused = {}
        for column in await _columns(conn):
            if column in {"status", "workspace_id", "slug", "version", "id"}:
                continue
            state = await _sqlstate(
                conn,
                f"UPDATE rating_versions SET {column} = {NEW_VALUE[column]} WHERE id = '{row_id}'",
            )
            if state is not None:
                refused[column] = state
    assert refused == {}


@pytest.mark.req("FR-44")
async def test_the_two_transitions_the_application_makes_are_permitted(database: Database) -> None:
    async with rolled_back(database) as conn:
        to_approved = await plant(conn, "review", slug="to-approved")
        to_draft = await plant(conn, "review", slug="to-draft")
        update = "UPDATE rating_versions SET {} WHERE id = '{}'"
        approved = await _sqlstate(
            conn, update.format("status = 'approved', updated_at = now()", to_approved)
        )
        drafted = await _sqlstate(
            conn, update.format("status = 'draft', updated_at = now()", to_draft)
        )
        # the same transition carrying any content change is refused
        with_content = await _sqlstate(
            conn, update.format("status = 'approved', change_summary = 'x'", to_approved)
        )
    assert (approved, drafted) == (None, None)
    assert with_content in REFUSED


@pytest.mark.req("FR-44")
async def test_an_update_that_changes_nothing_is_allowed(database: Database) -> None:
    async with rolled_back(database) as conn:
        for status in ("approved", "live"):
            row_id = await plant(conn, status, slug=f"same-{status}")
            state = await _sqlstate(
                conn,
                f"UPDATE rating_versions SET change_summary = change_summary WHERE id = '{row_id}'",
            )
            assert state is None, (status, state)


@pytest.mark.req("FR-351")
async def test_live_and_retired_need_the_decided_request(database: Database) -> None:
    """`approval_guard` holds `live` and `retired` as it holds `approved`: INSERT and UPDATE."""
    async with rolled_back(database) as conn:
        results = {}
        for status in ("live", "retired"):
            insert = (
                "INSERT INTO rating_versions (id, workspace_id, slug, version, status, "
                "dataset_version_id, model_ref, created_by) VALUES (gen_random_uuid(), "
                f"gen_random_uuid(), 'no-evidence', 1, '{status}', gen_random_uuid(), 'model:m@1', "
                "gen_random_uuid())"
            )
            results[("insert", status)] = await _sqlstate(conn, insert)
            await conn.execute(
                text(
                    "INSERT INTO rating_versions (id, workspace_id, slug, version, status, "
                    "dataset_version_id, model_ref, created_by) VALUES (:id, gen_random_uuid(), "
                    "'draft-row', 1, 'draft', gen_random_uuid(), 'model:m@1', gen_random_uuid())"
                ),
                {"id": (rid := new_uuid7())},
            )
            results[("update", status)] = await _sqlstate(
                conn, f"UPDATE rating_versions SET status = '{status}' WHERE id = '{rid}'"
            )
    assert set(results.values()) == {"GP001"}, results


@pytest.mark.req("FR-44")
async def test_each_refusal_is_the_guards_own(owner_database: Database) -> None:
    """The control: with the content guard disabled (owner, rolled back) the same sweep is
    refused only where the approval guard refuses on its own, the identity columns of an
    approved, live or retired row (GP001). Every other cell is the content guard's."""
    async with rolled_back(owner_database) as conn:
        await disable_trigger(conn, "rating_versions", GUARD)
        results = await _sweep(conn, HELD_STATUSES)
    refused = {key: state for key, state in results.items() if state is not None}
    identity = ("workspace_id", "slug", "version")
    assert refused == {(s, c): "GP001" for s in ("approved", "live", "retired") for c in identity}


async def _guard_enabled(database: Database) -> str:
    async with database.session() as session:
        return (
            await session.execute(
                text("SELECT tgenabled::text FROM pg_trigger WHERE tgname = :n"), {"n": GUARD}
            )
        ).scalar_one()


@pytest.mark.req("FR-44")
async def test_the_owner_edit_helper_leaves_the_guard_enabled(
    database: Database, workspace_id: UUID
) -> None:
    from backend.tests.conftest_db import edit_held_row_as_owner

    async with rolled_back(database) as conn:
        await plant(conn, "approved", slug="seed")  # the trigger exists and is on
    assert await _guard_enabled(database) == "O"
    await edit_held_row_as_owner(
        "rating_versions",
        GUARD,
        "UPDATE rating_versions SET change_summary = change_summary WHERE false",
    )
    assert await _guard_enabled(database) == "O"
    with pytest.raises(Exception):  # noqa: B017, PT011  (any failure of the UPDATE)
        await edit_held_row_as_owner(
            "rating_versions", GUARD, "UPDATE rating_versions SET no_such_column = 1"
        )
    assert await _guard_enabled(database) == "O"


@pytest.mark.req("FR-44")
def test_only_conftest_db_disables_the_two_guards() -> None:
    """`grep -rn 'DISABLE TRIGGER <guard>' backend/tests`: the statement is written once, in
    `conftest_db.disable_trigger`; no other test file names it."""
    import pathlib

    tests = pathlib.Path(__file__).parent
    needle = "DISABLE " + "TRIGGER"
    guards = ("rating_versions_content_guard", "approval_requests_decision_guard")
    hits = [
        f"{path.name}:{number}"
        for path in sorted(tests.glob("*.py"))
        for number, line in enumerate(path.read_text().splitlines(), 1)
        if needle in line and any(g in line for g in guards)
    ]
    assert hits == [], hits
    conftest = (tests / "conftest_db.py").read_text()
    assert conftest.count(needle + " {trigger}") == 1
