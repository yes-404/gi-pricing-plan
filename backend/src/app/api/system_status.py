"""System status (`07` §4.6, §5.1; FR-443, FR-444).

`GET /api/v1/admin/status` is the data behind the Admin's System status view: component
health, the schema version, job queue depths, blob store usage and cache counts, in one
read, deployment-wide. It publishes what `/readyz` and `/metrics` already publish, from the
same functions, plus the schema version, which neither does. When the database cannot be
read the route still answers 200, with the `database` component `down` and `null` for the
fields whose own read failed, per field: the figures read failing nulls `queues` and
`blob_store`, the alembic query failing nulls `schema_version` (decision of 2026-11-21 on
#1505, comment 7070124577). A database
that is down for the whole request fails earlier, at authentication (`resolve_caller`,
`app/api/deps.py`), before this route. It is behind `settings:read`
(the maintainer's decision of 2026-11-21 on #1505, answer 1): any role may read it.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.authz import requires
from app.api.deps import Caller
from app.api.health import (
    PlatformFigures,
    probe_components,
    read_platform_figures,
    readiness_verdict,
)
from app.api.responses import problems
from app.db.session import Database
from app.observability.logging import get_logger
from app.observability.metrics import cache_counts
from model_schema import Permission as Perm
from model_schema import SystemStatus
from model_schema.system_status import CacheCount, ComponentHealth, ComponentStatus

__all__ = ["router"]

_log = get_logger("app.system_status")

router = APIRouter(prefix="/admin", tags=["platform"])

ReadSettings = Annotated[Caller, Depends(requires(Perm.SETTINGS_READ))]


def _with_database_down(
    components: tuple[ComponentHealth, ...], failures: tuple[Exception, ...]
) -> tuple[ComponentHealth, ...]:
    """The components with `database` reported `down`, after a read of it failed.

    The probe answered before the reads, so it can still say `up` for a database that then
    failed a query; the reads are the later evidence. The detail says the read could not be
    made, not that the database was unreachable, because it may have answered (an empty or
    repeated `alembic_version` is a `NoResultFound` or `MultipleResultsFound`). It carries
    the exception types only, never a message (`00` R3, NFR-499).
    """
    types = ", ".join(dict.fromkeys(type(exc).__name__ for exc in failures))
    down = ComponentHealth(
        name="database",
        status=ComponentStatus.DOWN,
        detail=f"could not be read: {types}",
    )
    kept = tuple(c for c in components if c.name != down.name)
    return tuple(sorted((*kept, down), key=lambda c: c.name))


async def _schema_version(database: Database) -> str:
    """The database's migration revision (`07` §4.6; #1505 answer 4 (ii), option b)."""
    async with database.session() as session:
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        return str(result.scalar_one())


@router.get(
    "/status",
    summary="System status",
    responses=problems(401, 403),
)
async def get_system_status(caller: ReadSettings, request: Request) -> SystemStatus:
    database: Database = request.app.state.database
    components = await probe_components()
    # The decision of 2026-11-21 on #1505 (comment 7070124577), applied per field: the route
    # still answers, and a field is `null` only when its own read failed. The figures read
    # nulls `queues` and `blob_store`; the alembic query nulls `schema_version`. Either
    # failure marks the `database` component `down`, so `status` is `down`.
    failures: list[Exception] = []
    figures: PlatformFigures | None = None
    schema_version: str | None = None
    # A failed read is logged with its type only: the message can carry the DSN and so a
    # password (`00` R3, NFR-499), as the Redis probe's log line leaves it out.
    try:
        figures = await read_platform_figures(database)
    except (SQLAlchemyError, OSError) as exc:
        _log.warning(
            "system status platform figures read failed",
            extra={"error_type": type(exc).__name__},
        )
        failures.append(exc)
    try:
        schema_version = await _schema_version(database)
    except (SQLAlchemyError, OSError) as exc:
        _log.warning(
            "system status schema version read failed",
            extra={"error_type": type(exc).__name__},
        )
        failures.append(exc)
    if failures:
        components = _with_database_down(components, tuple(failures))
    return SystemStatus(
        status=readiness_verdict(components),
        components=components,
        schema_version=schema_version,
        queues=None if figures is None else figures.queues,
        blob_store=None if figures is None else figures.blob_store,
        caches=tuple(
            CacheCount(name=name, hits=hits, misses=misses)
            for name, (hits, misses) in cache_counts().items()
        ),
    )
