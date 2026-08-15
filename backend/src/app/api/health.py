"""Liveness, readiness and version (FR-PLAT-41).

The distinction matters operationally. `/healthz` answers "is this process alive?" — if it
fails, the orchestrator restarts the container. `/readyz` answers "can it serve?" and
includes the database, Redis and the blob store; if it fails, the pod leaves the load
balancer but is *not* restarted. Wiring dependency checks into liveness is how a brief
database blip becomes a restart storm across every replica.

Dependency probes register themselves, so adding the database check in the persistence
sprint does not touch this module.
"""

from __future__ import annotations

import asyncio
import enum
from collections.abc import Awaitable, Callable
from typing import Final

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field

from app.config import Settings
from app.db.session import Database
from app.observability.logging import get_logger
from app.observability.metrics import blob_bytes, blob_objects, job_queue_depth, render

__all__ = ["ComponentStatus", "ReadinessReport", "clear_probes", "register_probe", "router"]

_log = get_logger("app.health")

router = APIRouter(tags=["platform"])

#: A probe returns None when healthy, or a short reason when not. It must not raise, but
#: is called defensively in case it does.
Probe = Callable[[], Awaitable[str | None]]

_probes: dict[str, Probe] = {}

# A hung dependency must not hang the readiness endpoint — an unanswered probe is
# indistinguishable to the orchestrator from a hung process, and gets the wrong remedy.
_PROBE_TIMEOUT_S: Final = 2.0


class ComponentStatus(enum.StrEnum):
    UP = "up"
    DOWN = "down"


class ComponentHealth(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    status: ComponentStatus
    detail: str | None = Field(default=None, description="Why it is down. Never a secret (R3).")


class ReadinessReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: ComponentStatus
    components: tuple[ComponentHealth, ...] = ()


class VersionInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    service: str
    version: str
    environment: str


def register_probe(name: str, probe: Probe) -> None:
    """Register a readiness probe for a named dependency."""
    _probes[name] = probe


def clear_probes() -> None:
    """Remove all probes. For tests, and for application shutdown."""
    _probes.clear()


async def _run_probe(name: str, probe: Probe) -> ComponentHealth:
    try:
        async with asyncio.timeout(_PROBE_TIMEOUT_S):
            reason = await probe()
    except TimeoutError:
        reason = f"did not respond within {_PROBE_TIMEOUT_S:g}s"
    except Exception as exc:  # a broken probe is a down component, not a 500
        _log.warning("readiness probe raised", extra={"component": name})
        reason = f"probe failed: {type(exc).__name__}"
    if reason is None:
        return ComponentHealth(name=name, status=ComponentStatus.UP)
    return ComponentHealth(name=name, status=ComponentStatus.DOWN, detail=reason)


@router.get("/healthz", summary="Liveness — is the process alive?")
async def healthz() -> ReadinessReport:
    """Never touches a dependency. See the module docstring for why."""
    return ReadinessReport(status=ComponentStatus.UP)


@router.get(
    "/readyz",
    summary="Readiness — can the process serve traffic?",
    responses={503: {"description": "A dependency is unreachable", "model": ReadinessReport}},
)
async def readyz(response: Response) -> ReadinessReport:
    """Probe every registered dependency concurrently (FR-PLAT-41)."""
    results = await asyncio.gather(
        *(_run_probe(name, probe) for name, probe in sorted(_probes.items()))
    )
    healthy = all(component.status is ComponentStatus.UP for component in results)
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessReport(
        status=ComponentStatus.UP if healthy else ComponentStatus.DOWN,
        components=tuple(results),
    )


def version_route(settings: Settings) -> Callable[[], VersionInfo]:
    """Build the `/version` handler bound to the loaded settings."""

    def version() -> VersionInfo:
        return VersionInfo(
            service=settings.service_name,
            version=settings.version,
            environment=settings.environment.value,
        )

    return version


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    response_class=PlainTextResponse,
    include_in_schema=True,
)
async def metrics(request: Request) -> PlainTextResponse:
    """FR-PLAT-40.

    Unauthenticated, like `/healthz` and `/readyz`, because a scraper is infrastructure and
    not a principal — and reachable only from inside the deployment, which is where the
    boundary belongs. It carries no identifiers: every label is drawn from a bounded set
    (route template, method, status class, Job kind), so nothing here discloses which
    datasets or policies exist.

    The database-derived gauges are refreshed on scrape rather than on a timer. A timer
    would keep a connection warm to compute numbers nobody is reading, and a scrape that
    fails is a metric that stops updating rather than one that silently goes stale.
    """
    database: Database | None = getattr(request.app.state, "database", None)
    if database is not None:
        await refresh_platform_gauges(database)
    return PlainTextResponse(render().decode("utf-8"), media_type="text/plain; version=0.0.4")


async def refresh_platform_gauges(database: Database) -> None:
    """Queue depth and blob usage, read at scrape time (FR-PLAT-40)."""
    from sqlalchemy import func, select

    from app.db.models import BlobRow, JobRow
    from model_schema import TERMINAL_STATUSES

    terminal = [state.value for state in TERMINAL_STATUSES]
    async with database.session() as session:
        depths = (
            await session.execute(
                select(JobRow.kind, JobRow.status, func.count())
                .where(JobRow.status.not_in(terminal))
                .group_by(JobRow.kind, JobRow.status)
            )
        ).all()
        objects, total_bytes = (
            await session.execute(
                select(func.count(), func.coalesce(func.sum(BlobRow.bytes_), 0))
            )
        ).one()

    # Cleared first: a kind that drained to zero would otherwise keep reporting its last
    # non-zero depth for ever, which is the failure mode that makes a queue alert useless.
    job_queue_depth.clear()
    for kind, job_status, count in depths:
        job_queue_depth.labels(
            kind=getattr(kind, "value", str(kind)),
            status=getattr(job_status, "value", str(job_status)),
        ).set(count)
    blob_objects.set(objects)
    blob_bytes.set(total_bytes)
