"""Database fixtures for the integration suite.

These tests run against a **real PostgreSQL**, not SQLite or a mock. Every invariant they
cover — advisory locks, partial unique indexes, `FOR UPDATE SKIP LOCKED`, privilege
enforcement, triggers — is a PostgreSQL behaviour. A test double would assert that the code
calls the right function, which is not the question; the question is whether the database
refuses the write.

**Audit rows cannot be deleted between tests** — that is the whole point of FR-GOV-22 — so
isolation comes from giving each test its own `workspace_id` rather than from cleanup.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
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


@pytest.fixture
def workspace_id() -> UUID:
    """A fresh workspace per test — the only isolation an append-only table permits."""
    return new_uuid7()


@pytest.fixture
def principal() -> Principal:
    return Principal(kind=ActorKind.USER, id=new_uuid7(), display="a.actuary@insurer.example")
