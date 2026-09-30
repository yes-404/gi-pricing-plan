"""The approval guard trigger (WK-674 Slice 2a, PL-1303 Acceptance 2, 3, 6, 10; RL-1301 A.4.2).

Three shapes, used on purpose:

* The **real test database**, reached through `test_database_url()` *directly* — never
  through the `database` fixture, which skips on an unreachable or unmigrated database
  (`conftest_db.py`). A guard test that skips when the guard is missing proves nothing, so
  these **fail, never skip** (T3, the maintainer's CRITICAL pre-check).
* A **shadow copy** of the 8 guarded tables — `CREATE TEMP TABLE t (LIKE public.t INCLUDING
  ALL)` — with the migration's own trigger DDL installed on it. `pg_temp` precedes `public`
  on the search path, so the function's unqualified `approval_requests` resolves to the
  shadow too. That lets a row be valid by its CHECKs alone (the FKs are not copied) and the
  guard's own SQL run **verbatim**, which a pasted copy would not prove. Built `armed=False`,
  the same writes succeed: that is the broken-input proof that each refusal is the trigger's.
* **Alembic against a scratch database**, for the migration at head and head-1.
"""

from __future__ import annotations

import asyncio
import importlib.util
import pathlib
import secrets
from collections.abc import AsyncIterator, Callable
from types import ModuleType
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config

# Aliased: pytest collects any module-level name beginning `test_` as a test.
from backend.tests.conftest_db import empty_the_database
from backend.tests.conftest_db import test_database_url as _test_database_url
from sqlalchemy import func, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine

from app.db.base import Base
from app.db.models import RatingVersionRow, approval_guarded_tables
from model_schema import ArtifactRef, new_uuid7

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_MIGRATION = _REPO_ROOT / "backend" / "migrations" / "versions" / "a9f3c6d21b87_approval_guard.py"
_REVISION = "a9f3c6d21b87"
_PREVIOUS_REVISION = "d7e2a9b5c418"

#: The refusal's SQLSTATE, as the migration defines it.
GUARD_SQLSTATE = "GP001"

#: The 5 tables whose approved rows need a decided `approval_requests` row, never the flag.
EVIDENCE_ONLY = (
    "models",
    "custom_metrics",
    "custom_objectives",
    "peril_structures",
    "rating_versions",
)
#: The two that accept evidence or the flag while they hold an allowance.
EVIDENCE_OR_FLAG = ("validation_rules", "validation_rule_sets")
ALL_GUARDED = (*EVIDENCE_ONLY, *EVIDENCE_OR_FLAG, "approval_requests")

#: Each artifact table's reference type. `models` is the one whose slug column is
#: `model_family_slug`.
ARTIFACT_TYPE = {
    "models": "model",
    "custom_metrics": "custom_metric",
    "custom_objectives": "custom_objective",
    "peril_structures": "peril_structure",
    "rating_versions": "rating_version",
    "validation_rules": "validation_rule",
    "validation_rule_sets": "validation_rule_set",
}
SLUG_COLUMN = {table: "slug" for table in ARTIFACT_TYPE} | {"models": "model_family_slug"}


def _load_migration() -> ModuleType:
    """The guard's migration module. `versions/` is not importable by name."""
    spec = importlib.util.spec_from_file_location("_approval_guard_migration", _MIGRATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GUARD = _load_migration()


# --------------------------------------------------------------------------------------
# Rows that satisfy the CHECKs, and the evidence for them
# --------------------------------------------------------------------------------------


def _row(
    table: str, *, status: str, ws: UUID, slug: str = "motor", version: int = 1
) -> dict[str, Any]:
    """The smallest row `table` accepts at `status`. The FKs are not copied to the shadow."""
    approved = status == "approved"
    match table:
        case "models":
            values: dict[str, Any] = {
                "model_family_slug": slug,
                "version": version,
                "dataset_version_id": new_uuid7(),
                "spec": {},
                "spec_hash": "h",
            }
            if approved:
                values |= {"diagnostics_id": new_uuid7(), "fit_result": {}}
        case "peril_structures":
            values = {"slug": slug, "version": version, "perils": []}
            if approved:
                values["reconciliation"] = {}
        case "custom_objectives" | "custom_metrics":
            values = {"slug": slug, "version": version, "template": "t", "applicability": {}}
            if table == "custom_metrics":
                values["direction"] = "lower_is_better"
            if approved:
                values["certificate_id"] = new_uuid7()
        case "rating_versions":
            values = {
                "slug": slug,
                "version": version,
                "dataset_version_id": new_uuid7(),
                "model_ref": "model:motor@1",
                "created_by": new_uuid7(),
            }
        case "validation_rules":
            values = {
                "slug": slug,
                "version": version,
                "layer": "row",
                "check": "not_null",
                "severity": "error",
                "body": {},
                "authored_by": new_uuid7(),
            }
            if approved:
                values |= {"approved_by": new_uuid7(), "dry_run_report_id": new_uuid7()}
        case "validation_rule_sets":
            values = {"slug": slug, "version": version, "body": {}}
        case "approval_requests":
            return {
                "id": new_uuid7(),
                "workspace_id": ws,
                "artifact_ref": f"model:{slug}@{version}",
                "artifact_type": "model",
                "submitted_by": new_uuid7(),
                "change_summary": "s",
                "status": status,
                "approvers_required": 1,
            }
        case _:
            raise AssertionError(table)
    return {"id": new_uuid7(), "workspace_id": ws, "status": status, **values}


def _ref(table: str, slug: str = "motor", version: int = 1) -> str:
    return str(ArtifactRef(type=ARTIFACT_TYPE[table], slug=slug, version=version))


async def _sqlstate(awaitable: Any) -> str | None:
    """The SQLSTATE the awaited write raised, or `None` when it succeeded."""
    try:
        await awaitable
    except DBAPIError as exc:
        return str(getattr(exc.orig, "sqlstate", None))
    return None


async def _flag(conn: AsyncConnection, value: str) -> None:
    await conn.execute(text("SELECT set_config('app.approval_decision', :v, true)"), {"v": value})


async def _decided_request(
    conn: AsyncConnection, ws: UUID, ref: str, *, status: str = "approved"
) -> None:
    """Write an `approval_requests` row, as `decide` does: under the flag, then reset."""
    table = Base.metadata.tables["approval_requests"]
    await _flag(conn, "on")
    await conn.execute(
        table.insert().values(
            id=new_uuid7(),
            workspace_id=ws,
            artifact_ref=ref,
            artifact_type=ref.split(":")[0],
            submitted_by=new_uuid7(),
            change_summary="s",
            status=status,
            approvers_required=1,
        )
    )
    await _flag(conn, "off")


# --------------------------------------------------------------------------------------
# The shadow
# --------------------------------------------------------------------------------------


async def _shadow(conn: AsyncConnection, *, armed: bool, function_sql: str | None = None) -> None:
    for table in ALL_GUARDED:
        await conn.execute(
            text(f"CREATE TEMP TABLE {table} (LIKE public.{table} INCLUDING ALL) ON COMMIT DROP")
        )
    if function_sql is not None:
        await conn.execute(text(function_sql))
    if armed:
        for table in ALL_GUARDED:
            await conn.execute(text(_GUARD.create_trigger_sql(table)))


@pytest_asyncio.fixture
async def direct_engine() -> AsyncIterator[Any]:
    """An engine on `test_database_url()`. Fails, never skips, when it cannot connect."""
    engine = create_async_engine(_test_database_url())
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        await engine.dispose()
        pytest.fail(f"the guard tests need PostgreSQL at {_test_database_url()!r}: {exc!r}")
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(params=[True, False], ids=["armed", "trigger-dropped"])
async def shadow(
    request: pytest.FixtureRequest, direct_engine: Any
) -> AsyncIterator[tuple[AsyncConnection, bool]]:
    """One connection, one transaction, never committed, with the shadows in place."""
    async with direct_engine.connect() as conn:
        await conn.begin()
        await _shadow(conn, armed=request.param)
        yield conn, request.param
        await conn.rollback()


@pytest_asyncio.fixture
async def armed_shadow(direct_engine: Any) -> AsyncIterator[AsyncConnection]:
    async with direct_engine.connect() as conn:
        await conn.begin()
        await _shadow(conn, armed=True)
        yield conn
        await conn.rollback()


async def _expect(outcome: str | None, armed: bool, what: str) -> None:
    """Armed: the guard refuses with its SQLSTATE. Dropped: the same write succeeds."""
    if armed:
        assert outcome == GUARD_SQLSTATE, (
            f"{what}: expected refusal {GUARD_SQLSTATE}, got {outcome}"
        )
    else:
        assert outcome is None, (
            f"{what}: with the trigger dropped the write should succeed, got {outcome}"
        )


# --------------------------------------------------------------------------------------
# T3: the test database carries the trigger — fails, never skips
# --------------------------------------------------------------------------------------


_TRIGGERS_PRESENT = """
SELECT c.relname FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid
WHERE t.tgname = 'approval_guard' AND NOT t.tgisinternal
  AND c.relnamespace = 'public'::regnamespace
"""


async def _tables_missing_the_trigger(url: str) -> list[str]:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            present = {r[0] for r in await conn.execute(text(_TRIGGERS_PRESENT))}
    finally:
        await engine.dispose()
    return sorted(approval_guarded_tables() - present)


async def _assert_every_guarded_table_carries_the_trigger(url: str) -> None:
    missing = await _tables_missing_the_trigger(url)
    assert not missing, f"no approval_guard trigger on: {', '.join(missing)}"


@pytest.mark.req("FR-351")
async def test_every_guarded_table_carries_the_trigger_on_the_test_database() -> None:
    """Connects to `test_database_url()` itself. An unreachable database is a failure.

    `approval_guarded_tables()` is derived from the column declarations, so a table that
    declares an approved vocabulary and ships without the trigger fails here.
    """
    await _assert_every_guarded_table_carries_the_trigger(_test_database_url())


# --------------------------------------------------------------------------------------
# Alembic against a scratch database
# --------------------------------------------------------------------------------------


@pytest_asyncio.fixture
async def scratch_database() -> AsyncIterator[str]:
    """A throwaway database with no migrations applied. Fails, never skips."""
    admin_url = make_url(_test_database_url())
    name = f"gip_scratch_{secrets.token_hex(6)}"
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f'CREATE DATABASE "{name}"'))
    except Exception as exc:
        await engine.dispose()
        pytest.fail(f"the guard tests need PostgreSQL at {admin_url.database}: {exc!r}")
    try:
        yield admin_url.set(database=name).render_as_string(hide_password=False)
    finally:
        async with engine.connect() as conn:
            await conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": name},
            )
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        await engine.dispose()


def _alembic_config() -> Config:
    cfg = Config(str(_REPO_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_REPO_ROOT / "backend" / "migrations"))
    cfg.set_main_option("prepend_sys_path", str(_REPO_ROOT / "backend" / "src"))
    return cfg


async def _alembic(fn: Callable[..., None], cfg: Config, revision: str) -> None:
    """Off the test's loop: `env.py` calls `asyncio.run` at import."""
    await asyncio.to_thread(fn, cfg, revision)


async def _revision_of(url: str) -> str:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return str(
                (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar_one()
            )
    finally:
        await engine.dispose()


async def _insert_approved_request(url: str) -> str | None:
    """An approved `approval_requests` row with no flag: what the guard exists to refuse."""
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            return await _sqlstate(
                conn.execute(
                    Base.metadata.tables["approval_requests"]
                    .insert()
                    .values(**_row("approval_requests", status="approved", ws=new_uuid7()))
                )
            )
    finally:
        await engine.dispose()


async def _function_count(url: str) -> int:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return int(
                (
                    await conn.execute(
                        text("SELECT count(*) FROM pg_proc WHERE proname = 'approval_guard'")
                    )
                ).scalar_one()
            )
    finally:
        await engine.dispose()


@pytest.mark.req("FR-351")
async def test_the_trigger_test_fails_on_a_database_one_migration_short_of_head(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Red first, T3.** At the revision before the guard's, the presence check fails and
    names every guarded table — a database the suite might run on after a stale template
    (FD-1218) is not silently taken for a guarded one."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _alembic(command.upgrade, _alembic_config(), _PREVIOUS_REVISION)
    assert await _revision_of(scratch_database) == _PREVIOUS_REVISION

    with pytest.raises(AssertionError) as caught:
        await _assert_every_guarded_table_carries_the_trigger(scratch_database)
    for table in approval_guarded_tables():
        assert table in str(caught.value)


@pytest.mark.req("FR-351")
async def test_the_migration_round_trips_and_head_refuses_what_head_minus_one_allows(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FR-417: upgrade, downgrade -1, upgrade. Each step names the revision it reached."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()

    await _alembic(command.upgrade, cfg, _PREVIOUS_REVISION)
    assert await _revision_of(scratch_database) == _PREVIOUS_REVISION
    assert await _insert_approved_request(scratch_database) is None, "head-1 has no guard"
    assert await _function_count(scratch_database) == 0

    await _alembic(command.upgrade, cfg, _REVISION)
    assert await _revision_of(scratch_database) == _REVISION
    await _assert_every_guarded_table_carries_the_trigger(scratch_database)
    assert await _insert_approved_request(scratch_database) == GUARD_SQLSTATE

    await _alembic(command.downgrade, cfg, "-1")
    assert await _revision_of(scratch_database) == _PREVIOUS_REVISION
    assert await _tables_missing_the_trigger(scratch_database) == sorted(approval_guarded_tables())
    assert await _function_count(scratch_database) == 0, "the downgrade left the function behind"

    await _alembic(command.upgrade, cfg, _REVISION)
    await _assert_every_guarded_table_carries_the_trigger(scratch_database)
    assert await _function_count(scratch_database) == 1


@pytest.mark.req("FR-351")
def test_the_migration_guards_exactly_the_derived_set() -> None:
    assert set(_GUARD.GUARDED_TABLES) == approval_guarded_tables()
    assert set(ALL_GUARDED) == approval_guarded_tables()


@pytest.mark.req("FR-351")
async def test_the_trigger_is_in_force_again_after_the_teardown_suspends_it(
    direct_engine: Any,
) -> None:
    """`empty_the_database()` sets `session_replication_role = replica` for its own
    transaction only; the guard must still fire in the next one."""
    await empty_the_database()
    await _assert_every_guarded_table_carries_the_trigger(_test_database_url())
    async with direct_engine.connect() as conn:
        await conn.begin()
        outcome = await _sqlstate(
            conn.execute(
                Base.metadata.tables["approval_requests"]
                .insert()
                .values(**_row("approval_requests", status="approved", ws=new_uuid7()))
            )
        )
        await conn.rollback()
    assert outcome == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
async def test_an_approved_insert_into_every_real_table_is_refused_by_the_guard(
    direct_engine: Any,
) -> None:
    """On the real tables, through the real trigger. The row is deliberately incomplete:
    a BEFORE trigger runs ahead of NOT NULL, so the refusal is the guard's (`GP001`), and
    with no guard the same statement would fail `23502` instead."""
    for table in ALL_GUARDED:
        async with direct_engine.connect() as conn:
            await conn.begin()
            ws = new_uuid7()
            columns = {"id": new_uuid7(), "workspace_id": ws, "status": "approved"}
            if table != "approval_requests":
                columns |= {SLUG_COLUMN[table]: "motor", "version": 1}
            outcome = await _sqlstate(
                conn.execute(Base.metadata.tables[table].insert().values(**columns))
            )
            await conn.rollback()
        assert outcome == GUARD_SQLSTATE, f"{table}: {outcome}"


# --------------------------------------------------------------------------------------
# Every write form, on every table
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", ALL_GUARDED)
async def test_a_direct_approved_insert_is_refused_on_every_guarded_table(
    shadow: tuple[AsyncConnection, bool], table: str
) -> None:
    conn, armed = shadow
    ws = new_uuid7()
    outcome = await _sqlstate(
        conn.execute(
            Base.metadata.tables[table].insert().values(**_row(table, status="approved", ws=ws))
        )
    )
    await _expect(outcome, armed, f"{table} insert")


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", ALL_GUARDED)
async def test_a_direct_approved_update_is_refused_on_every_guarded_table(
    shadow: tuple[AsyncConnection, bool], table: str
) -> None:
    conn, armed = shadow
    tbl = Base.metadata.tables[table]
    ws = new_uuid7()
    values = _row(table, status="review" if table == "approval_requests" else "draft", ws=ws)
    if table in (
        "models",
        "custom_metrics",
        "custom_objectives",
        "peril_structures",
        "validation_rules",
    ):
        values |= {
            k: v for k, v in _row(table, status="approved", ws=ws).items() if k not in values
        }
    assert await _sqlstate(conn.execute(tbl.insert().values(**values))) is None
    outcome = await _sqlstate(
        conn.execute(update(tbl).where(tbl.c.id == values["id"]).values(status="approved"))
    )
    await _expect(outcome, armed, f"{table} update")


@pytest.mark.req("FR-351")
async def test_an_insert_relying_on_the_approved_column_default_is_refused(
    shadow: tuple[AsyncConnection, bool],
) -> None:
    """`validation_rule_sets.status` defaults to `approved` (`models.py`): the write names
    no status at all, and the trigger still sees `NEW.status = 'approved'`."""
    conn, armed = shadow
    tbl = Base.metadata.tables["validation_rule_sets"]
    outcome = await _sqlstate(
        conn.execute(
            tbl.insert().values(id=new_uuid7(), workspace_id=new_uuid7(), slug="s", body={})
        )
    )
    await _expect(outcome, armed, "insert relying on default='approved'")


async def _a_draft_rating_version(conn: AsyncConnection) -> UUID:
    tbl = Base.metadata.tables["rating_versions"]
    values = _row("rating_versions", status="draft", ws=new_uuid7())
    await conn.execute(tbl.insert().values(**values))
    return values["id"]  # type: ignore[no-any-return]


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "form",
    [
        "core_update",
        "raw_text",
        "non_literal",
        "bulk_update_mappings",
        "orm_bulk_update",
        "orm_attribute",
        "pg_insert",
    ],
)
async def test_every_write_form_of_approved_is_refused(
    shadow: tuple[AsyncConnection, bool], form: str
) -> None:
    """The five bypasses of the ORM-only guard at `80afeb40` and the ORM paths it caught.

    `rating_versions` stands for the evidence-only tables; the two write forms that need a
    second row (`bulk_update_mappings`, `pg_insert`) are run against it too.
    """
    conn, armed = shadow
    tbl = Base.metadata.tables["rating_versions"]
    row_id = await _a_draft_rating_version(conn)
    session = AsyncSession(bind=conn, expire_on_commit=False, autoflush=False)

    async def run() -> None:
        match form:
            case "core_update":
                await conn.execute(update(tbl).where(tbl.c.id == row_id).values(status="approved"))
            case "raw_text":
                await conn.execute(
                    text("UPDATE rating_versions SET status = 'approved' WHERE id = :i"),
                    {"i": row_id},
                )
            case "non_literal":
                await conn.execute(
                    update(tbl).where(tbl.c.id == row_id).values(status=func.lower("APPROVED"))
                )
            case "bulk_update_mappings":
                await session.run_sync(
                    lambda s: s.bulk_update_mappings(
                        RatingVersionRow, [{"id": row_id, "status": "approved"}]
                    )
                )
            case "orm_bulk_update":
                await session.execute(
                    update(RatingVersionRow)
                    .where(RatingVersionRow.id == row_id)
                    .values(status="approved")
                )
            case "orm_attribute":
                row = await session.get(RatingVersionRow, row_id)
                assert row is not None
                row.status = "approved"
                await session.flush()
            case "pg_insert":
                values = _row("rating_versions", status="approved", ws=new_uuid7(), slug="other")
                await conn.execute(
                    pg_insert(tbl)
                    .values(**values)
                    .on_conflict_do_update(index_elements=["id"], set_={"status": "approved"})
                )

    outcome = None
    try:
        await run()
    except DBAPIError as exc:
        outcome = str(getattr(exc.orig, "sqlstate", None))
    await _expect(outcome, armed, form)


# --------------------------------------------------------------------------------------
# The evidence condition
# --------------------------------------------------------------------------------------


async def _insert(conn: AsyncConnection, table: str, ws: UUID, **overrides: Any) -> str | None:
    """An approved insert inside a savepoint, so a refusal does not abort the transaction
    (and with it the flag the next attempt in the same test sets)."""
    values = _row(table, status="approved", ws=ws) | overrides
    try:
        async with conn.begin_nested():
            await conn.execute(Base.metadata.tables[table].insert().values(**values))
    except DBAPIError as exc:
        return str(getattr(exc.orig, "sqlstate", None))
    return None


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", ALL_GUARDED[:-1])
async def test_an_approved_row_with_a_decided_request_for_its_ref_is_allowed(
    armed_shadow: AsyncConnection, table: str
) -> None:
    """The positive control: the evidence path works on every artifact table, with no flag."""
    ws = new_uuid7()
    await _decided_request(armed_shadow, ws, _ref(table))
    assert await _insert(armed_shadow, table, ws) is None


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", EVIDENCE_ONLY)
async def test_the_flag_never_satisfies_an_evidence_only_table(
    armed_shadow: AsyncConnection, table: str
) -> None:
    """**The forgery.** `set_config('app.approval_decision', 'on', true)` then an approved
    write is refused on the 5 tables that take evidence only."""
    await _flag(armed_shadow, "on")
    assert await _insert(armed_shadow, table, new_uuid7()) == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", EVIDENCE_OR_FLAG)
async def test_the_flag_satisfies_a_validation_table_and_only_while_on(
    armed_shadow: AsyncConnection, table: str
) -> None:
    ws = new_uuid7()
    await _flag(armed_shadow, "on")
    assert await _insert(armed_shadow, table, ws, slug="a") is None
    await _flag(armed_shadow, "off")
    assert await _insert(armed_shadow, table, ws, slug="b") == GUARD_SQLSTATE
    # `''` is what a session reads after its transaction ended: not `on`.
    await _flag(armed_shadow, "")
    assert await _insert(armed_shadow, table, ws, slug="c") == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
async def test_the_flag_satisfies_approval_requests_and_only_while_on(
    armed_shadow: AsyncConnection,
) -> None:
    ws = new_uuid7()
    await _flag(armed_shadow, "on")
    assert await _insert(armed_shadow, "approval_requests", ws) is None
    await _flag(armed_shadow, "off")
    assert await _insert(armed_shadow, "approval_requests", ws) == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", EVIDENCE_ONLY)
@pytest.mark.parametrize(
    "case", ["other_version", "other_workspace", "still_in_review", "other_slug"]
)
async def test_an_approved_request_for_something_else_is_not_evidence(
    armed_shadow: AsyncConnection, table: str, case: str
) -> None:
    ws = new_uuid7()
    match case:
        case "other_version":
            await _decided_request(armed_shadow, ws, _ref(table, version=2))
        case "other_workspace":
            await _decided_request(armed_shadow, new_uuid7(), _ref(table))
        case "still_in_review":
            await _decided_request(armed_shadow, ws, _ref(table), status="review")
        case "other_slug":
            await _decided_request(armed_shadow, ws, _ref(table, slug="other"))
    assert await _insert(armed_shadow, table, ws) == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", EVIDENCE_ONLY)
async def test_repointing_an_approved_row_is_rechecked(
    armed_shadow: AsyncConnection, table: str
) -> None:
    """`UPDATE OF … version`: an approved row moved to a ref with no approved request."""
    ws = new_uuid7()
    tbl = Base.metadata.tables[table]
    await _decided_request(armed_shadow, ws, _ref(table))
    values = _row(table, status="approved", ws=ws)
    assert await _sqlstate(armed_shadow.execute(tbl.insert().values(**values))) is None

    outcome = await _sqlstate(
        armed_shadow.execute(update(tbl).where(tbl.c.id == values["id"]).values(version=2))
    )
    assert outcome == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
async def test_an_update_that_leaves_the_status_and_the_ref_alone_is_not_checked(
    armed_shadow: AsyncConnection,
) -> None:
    """`OF status, workspace_id, slug, version` narrows the UPDATE event: other columns move."""
    tbl = Base.metadata.tables["rating_versions"]
    values = _row("rating_versions", status="draft", ws=new_uuid7())
    await armed_shadow.execute(tbl.insert().values(**values))
    assert (
        await _sqlstate(
            armed_shadow.execute(
                update(tbl).where(tbl.c.id == values["id"]).values(model_ref="model:x@2")
            )
        )
        is None
    )


# --------------------------------------------------------------------------------------
# The ref has a second writer, in SQL
# --------------------------------------------------------------------------------------


@pytest.fixture
def separator_planted() -> str:
    """The guard's function with `'@'` replaced by `'/'` — the planted violation."""
    planted = _GUARD.APPROVAL_GUARD_FUNCTION.replace("|| '@' ||", "|| '/' ||")
    assert planted != _GUARD.APPROVAL_GUARD_FUNCTION, (
        "the separator moved; this plant no longer mutates it"
    )
    return planted


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("table", ALL_GUARDED[:-1])
async def test_the_ref_the_trigger_composes_is_the_one_artifactref_renders(
    direct_engine: Any, separator_planted: str, table: str
) -> None:
    """Green: the evidence keyed on `str(ArtifactRef(...))` satisfies the trigger for every
    artifact table. Red on the planted `'/'` separator: the same evidence no longer does."""
    for planted in (False, True):
        async with direct_engine.connect() as conn:
            await conn.begin()
            await _shadow(conn, armed=True, function_sql=separator_planted if planted else None)
            ws = new_uuid7()
            await _decided_request(conn, ws, _ref(table))
            outcome = await _insert(conn, table, ws)
            await conn.rollback()
        assert outcome == (GUARD_SQLSTATE if planted else None), (table, planted, outcome)


# --------------------------------------------------------------------------------------
# The evidence condition is load-bearing; the refusal has one name
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-351")
async def test_with_the_evidence_condition_replaced_by_the_flag_the_forgery_succeeds(
    direct_engine: Any,
) -> None:
    """**Broken input.** Replace the evidence requirement by the flag check on an
    evidence-only table and the forgery goes through, which is what
    `test_the_flag_never_satisfies_an_evidence_only_table` exists to catch."""
    planted = _GUARD.APPROVAL_GUARD_FUNCTION.replace(
        "IF mode = 'flag' AND NOT flag_is_off THEN", "IF NOT flag_is_off THEN"
    )
    assert planted != _GUARD.APPROVAL_GUARD_FUNCTION, (
        "the flag branch moved; this plant no longer mutates it"
    )
    async with direct_engine.connect() as conn:
        await conn.begin()
        await _shadow(conn, armed=True, function_sql=planted)
        await _flag(conn, "on")
        outcome = await _insert(conn, "rating_versions", new_uuid7())
        await conn.rollback()
    assert outcome is None


@pytest.mark.req("FR-351")
def test_the_errors_module_and_the_migration_name_the_same_sqlstate() -> None:
    from app.errors import APPROVAL_GUARD_SQLSTATE

    assert APPROVAL_GUARD_SQLSTATE == _GUARD.SQLSTATE == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
async def test_the_guards_refusal_is_one_named_problem_and_other_database_errors_are_not_renamed(
    direct_engine: Any, caplog: pytest.LogCaptureFixture
) -> None:
    import httpx
    from fastapi import FastAPI

    from app.errors import install_error_handlers

    app = FastAPI()
    install_error_handlers(app)
    approval_requests = Base.metadata.tables["approval_requests"]
    models = Base.metadata.tables["models"]

    @app.post("/approved")
    async def approved() -> None:
        async with direct_engine.connect() as conn:
            await conn.execute(
                approval_requests.insert().values(
                    **_row("approval_requests", status="approved", ws=new_uuid7())
                )
            )

    @app.post("/not-null")
    async def not_null() -> None:
        async with direct_engine.connect() as conn:
            await conn.execute(
                models.insert().values(id=new_uuid7(), workspace_id=new_uuid7(), status="draft")
            )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        named = await client.post("/approved")
        other = await client.post("/not-null")

    assert named.status_code == 500
    assert named.json()["code"] == "APPROVAL_OUTSIDE_DECISION_PATH"
    assert other.status_code == 500
    assert other.json()["code"] == "INTERNAL_ERROR"
    # The guard's refusal is an ERROR log naming the table (and ref) from the trigger's DETAIL.
    logged = [r for r in caplog.records if r.levelname == "ERROR" and hasattr(r, "guard_detail")]
    assert len(logged) == 1
    assert "table=approval_requests" in logged[0].guard_detail
