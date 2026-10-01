"""`approval_decision()`: the flag spans the write and its flush, and resets on exit.

WK-674 Slice 2a, PL-1303 Acceptance 4; RL-1301 A.4.3 and auditor-close1255's T2. All of it
runs on the real tables through `test_database_url()`, rolled back, and fails rather than
skips when the database is unreachable.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
import pytest_asyncio
from backend.tests.conftest_db import test_database_url as _test_database_url
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.models import ApprovalRequestRow
from app.platform.approvals import approval_decision
from model_schema import new_uuid7

GUARD_SQLSTATE = "GP001"

_FLAG = "SELECT current_setting('app.approval_decision', true)"


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[Any]:
    """One connection in the pool, so a leak would be seen by the next transaction."""
    eng = create_async_engine(_test_database_url(), pool_size=1, max_overflow=0)
    try:
        async with eng.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        await eng.dispose()
        pytest.fail(f"the guard tests need PostgreSQL at {_test_database_url()!r}: {exc!r}")
    yield eng
    await eng.dispose()


def _request(status: str) -> ApprovalRequestRow:
    return ApprovalRequestRow(
        id=new_uuid7(),
        workspace_id=new_uuid7(),
        artifact_ref="model:motor@1",
        artifact_type="model",
        submitted_by=new_uuid7(),
        change_summary="s",
        status=status,
        approvers_required=1,
    )


async def _flag_reads(session: AsyncSession) -> str | None:
    return (await session.execute(text(_FLAG))).scalar_one_or_none()


async def _refused(session: AsyncSession) -> bool:
    """Whether the session's next flush is refused by the guard, in a savepoint."""
    sqlstate = None
    try:
        async with session.begin_nested():
            await session.flush()
    except DBAPIError as exc:
        sqlstate = getattr(exc.orig, "sqlstate", None)
        if sqlstate != GUARD_SQLSTATE:
            raise
    return sqlstate == GUARD_SQLSTATE


@pytest.mark.req("FR-351")
async def test_the_block_sets_the_flag_writes_and_flushes_then_resets_it(engine: Any) -> None:
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        assert await _flag_reads(session) in (None, "", "off")
        async with approval_decision(session):
            assert await _flag_reads(session) == "on"
            session.add(_request("approved"))
        # The block flushed on exit, under the flag, so the row is there and was accepted.
        assert await _flag_reads(session) == "off"
        assert (await session.execute(select(ApprovalRequestRow.id))).first() is not None
        await session.rollback()


@pytest.mark.req("FR-351")
async def test_an_approved_write_after_the_block_in_the_same_unit_of_work_is_refused(
    engine: Any,
) -> None:
    """**T2**, red first against a block that only sets the flag: `SET LOCAL` lasts to the
    end of the transaction, so without the reset this write would be allowed."""
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        async with approval_decision(session):
            session.add(_request("approved"))
        session.add(_request("approved"))
        assert await _refused(session)
        await session.rollback()


@asynccontextmanager
async def _flag_without_reset(session: AsyncSession) -> AsyncIterator[None]:
    """The broken input: `approval_decision()` with its `finally` reset removed."""
    await session.execute(text("SET LOCAL app.approval_decision = 'on'"))
    yield
    await session.flush()


@pytest.mark.req("FR-351")
async def test_without_the_reset_the_same_write_after_the_block_is_allowed(engine: Any) -> None:
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        async with _flag_without_reset(session):
            session.add(_request("approved"))
        session.add(_request("approved"))
        assert not await _refused(session), "the reset is what refuses this write"
        await session.rollback()


@pytest.mark.req("FR-351")
async def test_an_orm_attribute_left_unflushed_at_exit_is_refused_later(
    engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**F-2** (auditor-close1255), on a flag-satisfiable table. Inside the block set a
    row's `status` to `approved` on the ORM object without flushing; with the exit flush
    patched out, the flag reads `'off'` when the block ends, and the later flush is refused.
    With the reset removed, the same flush succeeds — see the control below."""
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        row = _request("review")
        session.add(row)
        await session.flush()

        real_flush = session.flush

        async def no_flush(*_args: Any, **_kwargs: Any) -> None:
            return None

        async with approval_decision(session):
            row.status = "approved"
            monkeypatch.setattr(session, "flush", no_flush)
        monkeypatch.setattr(session, "flush", real_flush)

        assert await _flag_reads(session) == "off"
        assert await _refused(session)
        await session.rollback()


@pytest.mark.req("FR-351")
async def test_without_the_reset_the_unflushed_attribute_is_flushed_under_the_flag(
    engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control for the case above: with the reset removed the same flush succeeds, so
    the case fails without the reset."""
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        row = _request("review")
        session.add(row)
        await session.flush()
        real_flush = session.flush

        async def no_flush(*_args: Any, **_kwargs: Any) -> None:
            return None

        async with _flag_without_reset(session):
            row.status = "approved"
            monkeypatch.setattr(session, "flush", no_flush)
        monkeypatch.setattr(session, "flush", real_flush)

        assert await _flag_reads(session) == "on"
        assert not await _refused(session)
        await session.rollback()


@pytest.mark.req("FR-351")
async def test_the_flag_does_not_leak_to_the_next_transaction_on_a_pooled_connection(
    engine: Any,
) -> None:
    async with AsyncSession(engine) as session, session.begin():
        async with approval_decision(session):
            session.add(_request("approved"))
        await session.rollback()
    async with AsyncSession(engine) as session, session.begin():
        reads = await _flag_reads(session)
    # `''` after a transaction-local set ends: not `on`, which is all the guard asks.
    assert reads != "on"


@pytest.mark.req("FR-351")
async def test_a_session_level_set_would_leak_which_the_check_above_detects(engine: Any) -> None:
    """**Red on broken input**: a session-level `SET` (no `LOCAL`) survives the transaction
    on the pooled connection, so the leak check above has something to catch."""
    async with AsyncSession(engine) as session, session.begin():
        await session.execute(text("SET app.approval_decision = 'on'"))
    try:
        async with AsyncSession(engine) as session, session.begin():
            assert await _flag_reads(session) == "on"
    finally:
        async with AsyncSession(engine) as session, session.begin():
            await session.execute(text("RESET app.approval_decision"))


@pytest.mark.req("FR-351")
async def test_the_flag_is_reset_when_the_body_raises(engine: Any) -> None:
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        with pytest.raises(ValueError, match="boom"):
            async with approval_decision(session):
                raise ValueError("boom")
        assert await _flag_reads(session) == "off"
        await session.rollback()


@pytest.mark.req("FR-351")
async def test_a_database_error_in_the_body_surfaces_as_itself(engine: Any) -> None:
    """The reset cannot run in an aborted transaction; the error the caller sees must be the
    body's, not a second one about the dead transaction."""
    async with AsyncSession(engine, autoflush=False) as session, session.begin():
        with pytest.raises(DBAPIError) as caught:
            async with approval_decision(session):
                await session.execute(text("SELECT 1/0"))
        assert "division by zero" in str(caught.value)
        await session.rollback()
