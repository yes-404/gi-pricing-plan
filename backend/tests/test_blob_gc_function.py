"""FR-420, #1550 (c) — `blob_gc_delete_unreferenced`, the only DELETE path on `blobs` (slice 3b).

The application role holds no `DELETE` on `blobs` and runs the collector's one statement through an
owner-owned `SECURITY DEFINER` function. Against real PostgreSQL, as the application's login role
(the `database` fixture): the privileges that matter are the ones that role actually holds.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from backend.tests.conftest_db import seed_as_owner
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BlobRow, ScoringTraceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import blobs
from app.platform.blobs import BLOB_OWNERS, BlobOwner, BlobStore
from model_schema import Principal, new_uuid7

_SIGNATURE = "public.blob_gc_delete_unreferenced(timestamptz)"
_CALL = text("SELECT deleted_sha256, deleted_bytes FROM blob_gc_delete_unreferenced(:cutoff)")


async def _aged_unreferenced_blob(
    database: Database, blob_store: BlobStore, *, days: int = 60
) -> str:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, f"gc-function {new_uuid7()}".encode(), "text/plain")
    async with database.unit_of_work() as session:
        assert await blobs.release(session, ref.sha256) == 0

    async def _backdate(session: AsyncSession) -> None:
        await session.execute(
            update(BlobRow)
            .where(BlobRow.sha256 == ref.sha256)
            .values(created_at=datetime.now(UTC) - timedelta(days=days))
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


def _normalised(sql: str) -> str:
    return " ".join(sql.split())


async def _function_body(database: Database) -> str:
    async with database.session() as session:
        return str(
            (
                await session.execute(
                    text("SELECT prosrc FROM pg_proc WHERE oid = to_regprocedure(:sig)"),
                    {"sig": _SIGNATURE},
                )
            ).scalar_one()
        )


@pytest.mark.req("FR-420")
async def test_the_function_body_is_the_collectors_specification(database: Database) -> None:
    """The drift test. The function's `prosrc` contains each statement of
    `render_gc_function_statements()` (whitespace-normalised), so the owner list in the code and
    the one frozen in the migration cannot diverge: a `BlobOwner` added without a migration that
    replaces the function makes this fail, and the function would otherwise go on deleting blobs the
    new owner names."""
    body = _normalised(await _function_body(database))
    for statement in blobs.GC_FUNCTION_STATEMENTS:
        assert _normalised(statement) in body


@pytest.mark.req("FR-420")
async def test_the_drift_test_sees_a_new_owner(database: Database) -> None:
    """The negative control: a rendering over the owners plus one more is NOT in the body, so the
    test above is red the day `BLOB_OWNERS` gains an entry the function does not have."""
    extra = BlobOwner("zz.planted", "SELECT sha256 FROM zz_planted")
    planted = blobs.render_gc_function_statements((*BLOB_OWNERS, extra))
    body = _normalised(await _function_body(database))
    assert any(_normalised(statement) not in body for statement in planted)


_DELAY_FUNCTION = (
    "CREATE FUNCTION public.zz_gc_delay() RETURNS trigger LANGUAGE plpgsql AS "
    "$f$ BEGIN PERFORM pg_sleep(2); RETURN OLD; END $f$"
)
_DELAY_TRIGGER = (
    "CREATE TRIGGER zz_gc_delay BEFORE DELETE ON blobs FOR EACH ROW "
    "EXECUTE FUNCTION public.zz_gc_delay()"
)


@pytest.mark.req("FR-420")
async def test_an_owner_row_committed_while_the_delete_runs_rolls_the_run_back(
    database: Database,
    owner_database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    """#1855 (iv), the third statement. An owner row that took NO reference commits while the
    function's `DELETE` is running: the `DELETE`'s snapshot was taken before it, so it is not seen
    there (3a's collector then deleted the row and the object, probed). A `BEFORE DELETE` trigger
    that sleeps 2 s per row, created here as the owner and dropped after, holds the `DELETE` open
    so the interleaving is deterministic. The third statement looks again with a fresh snapshot,
    sees the owner row, and the run rolls back: nothing is deleted, `BLOB_GC_OWNER_APPEARED`."""
    digest = await _aged_unreferenced_blob(database, blob_store, days=400)
    async with owner_database.engine.begin() as connection:
        await connection.execute(text(_DELAY_FUNCTION))
        await connection.execute(text(_DELAY_TRIGGER))
    try:
        collector = asyncio.create_task(
            blob_store.collect_garbage(
                database, actor=principal, workspace_id=workspace_id, dry_run=False, grace_days=300
            )
        )
        asleep = False
        for _ in range(300):
            async with owner_database.session() as session:
                asleep = bool(
                    (
                        await session.execute(
                            text(
                                "SELECT count(*) FROM pg_stat_activity WHERE "
                                "datname = current_database() AND wait_event = 'PgSleep'"
                            )
                        )
                    ).scalar_one()
                )
            if asleep:
                break
            await asyncio.sleep(0.02)
        assert asleep, "the DELETE never reached the planted delay"
        async with database.unit_of_work() as session:  # the login role may INSERT a trace row
            session.add(
                ScoringTraceRow(
                    workspace_id=new_uuid7(),
                    quote_id=f"quote-{new_uuid7()}",
                    rating_version_ref="rating_version:motor-gb@3",
                    bundle_hash="sha256:" + "0" * 64,
                    sample_reason="rate",
                    blob_sha256=digest,
                    status="complete",
                )
            )  # committed while the DELETE is mid-statement, no reference taken
        with pytest.raises(PlatformError) as raised:
            await collector
    finally:
        async with owner_database.engine.begin() as connection:
            await connection.execute(text("DROP TRIGGER IF EXISTS zz_gc_delay ON blobs"))
            await connection.execute(text("DROP FUNCTION IF EXISTS public.zz_gc_delay()"))

    assert raised.value.code == "BLOB_GC_OWNER_APPEARED"
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None  # the delete was rolled back


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
