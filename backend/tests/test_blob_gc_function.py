"""FR-420, #1550 (c) — `blob_gc_delete_unreferenced`, the only DELETE path on `blobs` (slice 3b).

The application role holds no `DELETE` on `blobs` and runs the collector's one statement through an
owner-owned `SECURITY DEFINER` function. Against real PostgreSQL, as the application's login role
(the `database` fixture): the privileges that matter are the ones that role actually holds.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from backend.tests.conftest_db import seed_as_owner
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BlobRow
from app.db.session import Database
from app.platform import blobs
from app.platform.blobs import BlobStore
from model_schema import new_uuid7

_SIGNATURE = "public.blob_gc_delete_unreferenced(timestamptz)"
_CALL = text("SELECT deleted_sha256, deleted_bytes FROM blob_gc_delete_unreferenced(:cutoff)")


async def _aged_unreferenced_blob(database: Database, blob_store: BlobStore) -> str:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, f"gc-function {new_uuid7()}".encode(), "text/plain")
    async with database.unit_of_work() as session:
        assert await blobs.release(session, ref.sha256) == 0

    async def _backdate(session: AsyncSession) -> None:
        await session.execute(
            update(BlobRow)
            .where(BlobRow.sha256 == ref.sha256)
            .values(created_at=datetime.now(UTC) - timedelta(days=60))
        )

    await seed_as_owner(_backdate)
    return ref.sha256


@pytest.mark.req("FR-420")
async def test_a_cutoff_inside_the_one_day_floor_is_refused_and_deletes_nothing(
    database: Database, blob_store: BlobStore
) -> None:
    """F3. The floor is in the function, so `now()` from the login role deletes nothing."""
    digest = await _aged_unreferenced_blob(database, blob_store)

    with pytest.raises(DBAPIError, match="BLOB_GC_CUTOFF_TOO_RECENT"):
        async with database.unit_of_work() as session:
            await session.execute(_CALL, {"cutoff": datetime.now(UTC)})

    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None


@pytest.mark.req("FR-420")
async def test_the_function_is_owned_pinned_and_executable_by_the_application_role_only(
    database: Database,
) -> None:
    """F4 and the definer hardening, read from the catalogue as the login role."""
    async with database.session() as session:
        facts = (
            await session.execute(
                text(
                    "SELECT p.prosecdef AS secdef, p.proconfig::text[] AS config, "
                    "p.proowner = (SELECT relowner FROM pg_class WHERE oid = 'blobs'::regclass) "
                    "  AS owned_by_the_table_owner, "
                    "EXISTS (SELECT 1 FROM aclexplode(p.proacl) a WHERE a.grantee = 0) "
                    "  AS public_can_execute, "
                    "has_function_privilege('gip_app', p.oid, 'EXECUTE') AS app_can_execute, "
                    "has_table_privilege('gip_app', 'blobs', 'DELETE') AS app_can_delete, "
                    "has_schema_privilege('gip_app', 'public', 'CREATE') AS app_can_create "
                    "FROM pg_proc p WHERE p.oid = to_regprocedure(:sig)"
                ),
                {"sig": _SIGNATURE},
            )
        ).one()

    assert facts.secdef is True
    assert list(facts.config) == ["search_path=pg_catalog, public, pg_temp"]
    assert facts.owned_by_the_table_owner is True
    assert facts.public_can_execute is False  # PostgreSQL grants PUBLIC EXECUTE by default
    assert facts.app_can_execute is True
    assert facts.app_can_delete is False
    # A pinned search_path that includes a schema the caller can write to is not pinned.
    assert facts.app_can_create is False


@pytest.mark.req("FR-420")
async def test_the_function_body_has_no_dynamic_sql_and_one_parameter(database: Database) -> None:
    """Condition (i): no dynamic SQL, no caller-supplied identifier; the only parameter is the
    cutoff. Red against a body that builds SQL with `EXECUTE format(...)`."""
    async with database.session() as session:
        row = (
            await session.execute(
                text(
                    "SELECT p.prosrc, p.pronargs FROM pg_proc p WHERE p.oid = to_regprocedure(:sig)"
                ),
                {"sig": _SIGNATURE},
            )
        ).one()
    body = row.prosrc.upper()
    assert row.pronargs == 1
    assert "EXECUTE " not in body
    assert "FORMAT(" not in body
    assert "QUOTE_IDENT" not in body


_PLANTED_BODY = "BEGIN RETURN QUERY SELECT 'x'::text, 1::bigint WHERE false; END"


async def _definer_refusal(owner_database: Database, plant: str) -> str:
    """Apply `plant` as the owner in a transaction that is always rolled back, run the startup
    check on that connection, and return the refusal's message ('' when it did not refuse)."""
    from app.db.immutability import LeastPrivilegeError, assert_definer_functions_pinned

    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await connection.execute(text(plant))
            try:
                await assert_definer_functions_pinned(connection)
            except LeastPrivilegeError as exc:
                return str(exc)
            return ""
        finally:
            await transaction.rollback()


@pytest.mark.req("FR-420")
async def test_the_startup_check_refuses_a_replaced_definer_body_naming_the_migration(
    owner_database: Database,
) -> None:
    """Condition (iii): a function whose body was replaced is a refusal to start, and the message
    names the migration that owns it."""
    message = await _definer_refusal(
        owner_database,
        "CREATE OR REPLACE FUNCTION public.blob_gc_delete_unreferenced(p_cutoff timestamptz) "
        "RETURNS TABLE (deleted_sha256 text, deleted_bytes bigint) LANGUAGE plpgsql "
        "SECURITY DEFINER SET search_path = pg_catalog, public, pg_temp "
        f"AS $fn${_PLANTED_BODY}$fn$",
    )
    assert "d5b9f20c8a14_blob_gc_definer_function" in message
    assert "not the pinned one" in message


@pytest.mark.req("FR-420")
async def test_the_startup_check_refuses_a_changed_search_path(owner_database: Database) -> None:
    message = await _definer_refusal(
        owner_database,
        "ALTER FUNCTION public.blob_gc_delete_unreferenced(timestamptz) SET search_path = public",
    )
    assert "search_path" in message
    assert "d5b9f20c8a14_blob_gc_definer_function" in message


@pytest.mark.req("FR-420")
async def test_the_startup_check_refuses_an_unpinned_definer_function(
    owner_database: Database,
) -> None:
    message = await _definer_refusal(
        owner_database,
        "CREATE FUNCTION public.zz_unpinned_definer() RETURNS integer LANGUAGE sql "
        "SECURITY DEFINER AS $f$ SELECT 1 $f$",
    )
    assert "zz_unpinned_definer" in message
    assert "no migration pinned" in message


@pytest.mark.req("FR-420")
async def test_the_startup_check_passes_on_the_migrated_head(owner_database: Database) -> None:
    """The positive control: nothing planted, nothing refused."""
    assert await _definer_refusal(owner_database, "SELECT 1") == ""
