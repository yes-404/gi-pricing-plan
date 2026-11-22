"""System status and component health (`07` §4.6, FR-443, FR-444).

`ComponentStatus` and `ComponentHealth` are what `/readyz` already published; they move
here, names and fields unchanged (decision of 2026-11-21 on #1505, answer 7), so the status
route reuses them rather than declaring a second copy (CLAUDE.md §4). The published
`/readyz` schema is unmoved by the move. `ReadinessReport` stays in `app.api.health`.

The rest is the response of `GET /api/v1/admin/status`: deployment-wide, read-only, and
carrying only figures `/readyz` and `/metrics` already publish, plus the schema version.
"""

from __future__ import annotations

import enum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "BlobStoreUsage",
    "CacheCount",
    "ComponentHealth",
    "ComponentStatus",
    "QueueDepth",
    "SystemStatus",
]


class ComponentStatus(enum.StrEnum):
    UP = "up"
    DOWN = "down"


class ComponentHealth(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    status: ComponentStatus
    detail: str | None = Field(default=None, description="Why it is down. Never a secret (R3).")


class QueueDepth(BaseModel):
    """Jobs of one kind in one non-terminal status. A kind with none has no entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str
    status: str
    depth: int = Field(ge=1)


class BlobStoreUsage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    objects: int = Field(ge=0, description="The number of blobs.")
    bytes: int = Field(ge=0, description="Their total size in bytes.")


class CacheCount(BaseModel):
    """Lookups of one cache since this API process started (`07` §4.6).

    A lookup that ended in an error is counted as neither a hit nor a miss.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    hits: int = Field(ge=0)
    misses: int = Field(ge=0)


class SystemStatus(BaseModel):
    """The response of `GET /api/v1/admin/status` (`07` §4.6)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: ComponentStatus = Field(
        description="The readiness verdict over the components as this route reports them, "
        "a failed database read included, so it can be `down` while `/readyz`, read at the "
        "same moment, is `up`. It is decided by the components that gate readiness, so "
        "`redis` can be down while this is up."
    )
    components: tuple[ComponentHealth, ...] = Field(
        description="One entry per registered readiness probe."
    )
    schema_version: str | None = Field(
        description="The database's migration revision (its `alembic_version` table). "
        "`null` means the database could not be read; it is never shown as empty "
        "(decision of 2026-11-21 on #1505, comment 7070124577)."
    )
    queues: tuple[QueueDepth, ...] | None = Field(
        description="Jobs per kind and non-terminal status. `null` means the database could "
        "not be read, never an empty list: an empty list means the read succeeded and "
        "nothing is queued."
    )
    blob_store: BlobStoreUsage | None = Field(
        description="Blob count and size. `null` means the database could not be read, "
        "never an object of zeros: zeros mean the read succeeded and there are no blobs."
    )
    caches: tuple[CacheCount, ...]
