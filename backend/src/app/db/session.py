"""Engine, session factory, and the unit of work every governed write runs inside.

`06` R2 is the reason this module is small and opinionated:

> Every governed transition writes its event in the same database transaction as the
> change — if the audit write fails, the change fails.

That is only true if there is *one* transaction to share, and if nothing can commit half of
it. So callers do not manage transactions by hand: they take a `unit_of_work()`, which
commits once at the end and rolls the whole thing back on any exception.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings
from app.observability.logging import get_logger

__all__ = ["Database", "database_probe"]

_log = get_logger("app.db")

_SELECT_ONE = text("SELECT 1")


class Database:
    """Owns the engine and session factory for one application instance."""

    def __init__(self, settings: Settings) -> None:
        self._engine: AsyncEngine = create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
            # A connection that died while idle — a database restart, a network blip —
            # otherwise fails the *next* request rather than being replaced silently.
            future=True,
        )
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            # Attribute access after commit would otherwise emit a fresh SELECT, which in
            # an async session means an await in a place the caller did not expect one.
            autoflush=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """A session with no transaction management. For reads."""
        async with self._sessionmaker() as session:
            yield session

    @asynccontextmanager
    async def unit_of_work(self) -> AsyncIterator[AsyncSession]:
        """One transaction covering the domain change, its audit event, and its outbox row.

        Commits once on clean exit; rolls back everything on any exception. There is no
        partial-commit path, which is the point: a change without its audit event, or an
        outbox row without its job, are the two states `06` R2 and FR-PLAT-51 exist to
        make unreachable.
        """
        async with self._sessionmaker() as session, session.begin():
            yield session

    async def dispose(self) -> None:
        await self._engine.dispose()


def database_probe(database: Database) -> Callable[[], Awaitable[str | None]]:
    """Build the `/readyz` probe for the database (FR-PLAT-41)."""

    async def probe() -> str | None:
        try:
            async with database.session() as session:
                await session.execute(_SELECT_ONE)
        except Exception as exc:
            # The message may carry the DSN, which can carry a password (R3). Only the
            # exception type is reported; the detail is in the logs, behind an operator
            # boundary the caller is not on.
            _log.warning("database probe failed", extra={"error_type": type(exc).__name__})
            return f"unreachable: {type(exc).__name__}"
        return None

    return probe
