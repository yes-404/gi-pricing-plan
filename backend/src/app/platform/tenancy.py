"""One tenant, one deployment (`07` FR-436, ADR-710).

The deployment is configured with a tenant identifier. The database, the blob bucket and
the broker each carry a marker holding it, and a process whose configured identifier
disagrees with any marker refuses to start.
"""

from __future__ import annotations

import redis.asyncio
from sqlalchemy import select, text

from app.config import Settings
from app.db.models import TenantMarkerRow
from app.db.session import Database
from app.platform.blobs import BlobStore

TENANT_BLOB_KEY = "_platform/tenant"
TENANT_REDIS_KEY = "gip:tenant"


class TenantMismatchError(RuntimeError):
    """A store is bound to a different tenant than the one this process is configured for."""

    def __init__(self, store: str, configured: str, found: str | None, hint: str = "") -> None:
        self.store = store
        self.configured = configured
        self.found = found
        seen = "no tenant marker (it is missing)" if found is None else f"tenant {found!r}"
        super().__init__(
            f"refusing to start: the {store} carries {seen}, but this process is configured "
            f"for tenant {configured!r} (FR-436).{' ' + hint if hint else ''}"
        )


async def check_database(database: Database, configured: str) -> None:
    """The database marker must exist and equal `configured`. Read-only: only the
    migration writes it, so a missing marker is an error and never a reason to write one."""
    async with database.session() as session:
        table = (
            await session.execute(text("SELECT to_regclass('tenant_marker')"))
        ).scalar_one()
        if table is None:
            raise TenantMismatchError(
                "database",
                configured,
                None,
                "The database is not migrated to the revision that creates the marker; "
                "run `alembic upgrade head`.",
            )
        found = (
            await session.execute(select(TenantMarkerRow.tenant_id).where(TenantMarkerRow.id == 1))
        ).scalar_one_or_none()
    if found is None:
        raise TenantMismatchError(
            "database", configured, None, "Only the migration writes the marker."
        )
    if found != configured:
        raise TenantMismatchError("database", configured, found)


async def check_blob(blob_store: BlobStore, configured: str) -> None:
    """Read the bucket's marker; write `configured` if absent; refuse if it differs."""
    raw = await blob_store.read_object(TENANT_BLOB_KEY)
    if raw is None:
        await blob_store.write_object(TENANT_BLOB_KEY, configured.encode())
        return
    if (found := raw.decode()) != configured:
        raise TenantMismatchError("blob storage", configured, found)


async def check_broker(redis_url: str, configured: str) -> None:
    """Set the broker's marker if absent, then read it and refuse if it differs.

    Redis holds nothing durable (FR-422), so this key is re-armed by the next process after
    a flush; it detects a mismatch only while the key exists (RL-1253, DP-S1-2's limit).
    """
    client = redis.asyncio.from_url(redis_url)  # type: ignore[no-untyped-call]
    try:
        await client.set(TENANT_REDIS_KEY, configured, nx=True)
        raw = await client.get(TENANT_REDIS_KEY)
    finally:
        await client.aclose()
    if (found := raw.decode() if raw is not None else None) != configured:
        raise TenantMismatchError("broker", configured, found)


async def require_tenant_binding(
    settings: Settings, database: Database, blob_store: BlobStore
) -> None:
    """Every store must be bound to `settings.tenant_id`, or this raises.

    The order is the point. The database check is read-only and runs first, so a
    configuration pointing at another tenant's database stops before it writes to object
    storage or the broker. The bucket must exist before its marker can be read or written.
    """
    await check_database(database, settings.tenant_id)
    await blob_store.ensure_bucket()
    await check_blob(blob_store, settings.tenant_id)
    await check_broker(settings.redis_url.get_secret_value(), settings.tenant_id)
