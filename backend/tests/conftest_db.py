"""Database fixtures for the integration suite.

These tests run against a **real PostgreSQL**, not SQLite or a mock. Every invariant they
cover — advisory locks, partial unique indexes, `FOR UPDATE SKIP LOCKED`, privilege
enforcement, triggers — is a PostgreSQL behaviour. A test double would assert that the code
calls the right function, which is not the question; the question is whether the database
refuses the write.

**Audit rows cannot be deleted between tests** — that is the whole point of FR-GOV-22 — so
isolation comes from giving each test its own `workspace_id` rather than from cleanup.

That is unchanged. `_empty_the_database_after_the_session` below empties the database once
the **whole session** is over, which is a different question: not how one test is isolated
from the next, but whether six days of runs leave 766 MB behind. They did, measured
2026-08-22. Nothing between tests is cleaned, and nothing about the paragraph above moves.
"""

from __future__ import annotations

import asyncio
import os
import warnings
from collections.abc import AsyncIterator, Iterator
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import text

from app.config import Settings
from app.db.session import Database
from app.platform.blobs import BlobStore
from model_schema import ActorKind, Principal, new_uuid7

DEFAULT_TEST_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"


def test_database_url() -> str:
    return os.environ.get("GIP_TEST_DATABASE_URL", DEFAULT_TEST_DSN)


@pytest_asyncio.fixture
async def database() -> AsyncIterator[Database]:
    """An engine per test, against a database the migration has already been run on.

    Function-scoped deliberately. A session-scoped async engine binds its connections to
    the event loop that created it, and pytest-asyncio gives each test a fresh loop — the
    result is `got Future attached to a different loop`, which reads like a driver bug
    rather than a fixture-scope mistake. Creating an engine per test costs a connection.

    Skips rather than fails when nothing is listening: a developer without the compose
    stack up should still be able to run the unit tests. CI provides the service, so the
    skip never hides a regression there.
    """
    db = Database(Settings(database_url=test_database_url()))
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        await db.dispose()
        pytest.skip(f"PostgreSQL not reachable at {test_database_url()}: {type(exc).__name__}")

    async with db.session() as session:
        applied = (
            await session.execute(text("SELECT count(*) FROM alembic_version"))
        ).scalar_one()
    if not applied:
        pytest.skip("database has no migrations applied; run `uv run alembic upgrade head`")

    yield db
    await db.dispose()


@pytest_asyncio.fixture
async def blob_store() -> AsyncIterator[BlobStore]:
    """A blob store against the compose MinIO, with its bucket ensured.

    Skips when MinIO is unreachable, for the same reason the database fixture does — and
    CI runs a MinIO service so the skip never hides a regression there.
    """
    store = BlobStore(Settings(blob_bucket=os.environ.get("GIP_TEST_BUCKET", "gip-test-blobs")))
    try:
        await store.ensure_bucket()
    except Exception as exc:
        pytest.skip(f"MinIO not reachable: {type(exc).__name__}")
    yield store


@pytest_asyncio.fixture
async def grant(database: Database, workspace_id: UUID, principal: Principal):
    """Seed the built-in roles and grant one to the test principal.

    Route tests must grant explicitly, because development identity carries **no**
    permissions. Treating the dev principal as an administrator would make every route test
    pass without exercising a single permission check — coverage that is not coverage.

        await grant("analyst")
    """

    async def _grant(role_slug: str, *, principal_id: UUID | None = None) -> None:
        from sqlalchemy import select

        from app.db.models import RoleAssignmentRow, RoleRow
        from app.platform import rbac
        from model_schema import ScopeType

        async with database.unit_of_work() as session:
            await rbac.seed_builtin_roles(session, workspace_id)
            role = (
                await session.execute(
                    select(RoleRow).where(
                        RoleRow.workspace_id == workspace_id, RoleRow.slug == role_slug
                    )
                )
            ).scalar_one()
            session.add(
                RoleAssignmentRow(
                    workspace_id=workspace_id,
                    principal_kind="user",
                    principal_id=principal_id or principal.id,
                    role_id=role.id,
                    scope_type=ScopeType.WORKSPACE.value,
                )
            )

    return _grant


@pytest.fixture
def workspace_id() -> UUID:
    """A fresh workspace per test — the only isolation an append-only table permits."""
    return new_uuid7()


@pytest.fixture
def principal() -> Principal:
    return Principal(kind=ActorKind.USER, id=new_uuid7(), display="a.actuary@insurer.example")


#: Seventeen tables refuse `TRUNCATE`, not one. `audit_events` is the famous one (FR-GOV-22),
#: but artifact immutability is enforced the same way across `validation_reports`,
#: `models`, `diagnostics`, `blobs`, `transparency_artifacts` and a dozen more — so naming
#: tables here would mean editing this file every time the platform gains an immutable
#: artifact, and discovering it from a failed teardown each time.
#:
#: `session_replication_role = replica` suspends every user trigger at once, and the third
#: argument to `set_config` makes it **transaction-local**: it reverts when this statement's
#: transaction ends, by commit or by rollback, with nothing to re-enable and no ordering of
#: failures that leaves a guard off. That is the property that makes suspending them here
#: defensible; a per-table `ALTER ... DISABLE TRIGGER` would depend on reaching its own
#: re-enable. It needs superuser, which the compose and CI `gipricing` role has.
_EMPTY_THE_DATABASE = """
DO $$
DECLARE stmt text;
BEGIN
  PERFORM set_config('session_replication_role', 'replica', true);
  SELECT 'TRUNCATE TABLE '
       || string_agg(format('%I.%I', schemaname, tablename), ', ')
       || ' RESTART IDENTITY CASCADE'
    INTO stmt
    FROM pg_tables
   WHERE schemaname = 'public' AND tablename <> 'alembic_version';
  EXECUTE stmt;
END $$;
"""


async def empty_the_database() -> None:
    """Truncate every table but `alembic_version`, restoring the audit guard on the way out.

    Exposed rather than inlined so a test can call it mid-session and assert the guards are
    still in force afterwards — the one property of this teardown worth pinning, since a
    suspended trigger is silent and these tables are what the platform's governance rests on.
    """
    db = Database(Settings(database_url=test_database_url()))
    try:
        # `unit_of_work`, not `session`: the latter does no transaction management and never
        # commits, so the statement below runs and is rolled back on close. It also gives
        # the transaction that `set_config(..., true)` above is local to.
        async with db.unit_of_work() as session:
            await session.execute(text(_EMPTY_THE_DATABASE))
    finally:
        await db.dispose()


@pytest.fixture(scope="session", autouse=True)
def _empty_the_database_after_the_session() -> Iterator[None]:
    """Leave the shared database as empty as the migrations left it.

    **Session-scoped, and deliberately not per-test.** Truncating between tests would
    contradict the module docstring above and cost a full-table lock 430 times over; the
    growth it exists to bound is per-*run*, not per-test.

    Synchronous, calling `asyncio.run` at teardown, because a session-scoped *async* fixture
    binds its connections to the loop that created it while `pytest-asyncio` gives each test
    a fresh one — the `got Future attached to a different loop` the `database` fixture's
    docstring warns about. Running after the last test, this owns the only loop there is.

    Warns rather than fails when PostgreSQL is unreachable: the suite already skips its
    database tests in that case (see `database`), and a teardown that fails the run for a
    developer who never had a database would punish exactly the person the skip exists to
    help. It **warns rather than passing silently** because the first version of this
    swallowed a real bug — `session()` does not commit — and reported a clean run while
    emptying nothing.

    **This empties the whole database, including any `scripts/demo.py` seed.** Tests and the
    demo share one database, so bounding the growth of one bounds the other. Re-seed with
    `uv run python scripts/demo.py`.
    """
    yield
    try:
        asyncio.run(empty_the_database())
    # Broad by intent: no database is not a failure, but it is never silent either.
    except Exception as exc:
        warnings.warn(
            f"could not empty the test database ({type(exc).__name__}: {exc}); this run's "
            "rows remain. `.claude/skills/python-test` carries the manual reset.",
            stacklevel=1,
        )

