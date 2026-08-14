"""Reference tables and their effective-dated versions (`01` §3.5, §4.8, FR-DATA-29..32).

A reference table is the least glamorous data in a pricing platform and among the most
dangerous. A vehicle-group table refreshed without versioning changes the rating of every
in-force policy retroactively, and nothing in the quote records which table it used.

Two rules carry that, and both are enforced below rather than documented:

* **A version is loaded whole and pinned by id** (FR-DATA-32). A rating version names the
  reference version it was built against; "the latest" is not a reference, it is a race.
* **Intervals for one key never overlap** (FR-DATA-31), enforced by a `btree_gist`
  exclusion constraint. Two rows covering one date give a lookup two answers, and which
  one a quote gets would depend on row order.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReferenceRowRow, ReferenceTableRow, ReferenceTableVersionRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit, rbac
from model_schema import JobSource, Permission, Principal

__all__ = [
    "create_table",
    "load_version",
    "lookup",
    "publish_version",
]

_log = get_logger("app.reference")

DRAFT, PUBLISHED = "draft", "published"


async def create_table(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    key_columns: Sequence[str],
    payload_columns: Sequence[str],
    description: str | None = None,
) -> ReferenceTableRow:
    """Declare a reference table (FR-DATA-29)."""
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.ADMIN_MANAGE_SETTINGS,
    )
    if not key_columns:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A reference table needs at least one key column",
            422,
            "Without a key there is nothing to look up by, and every row would match "
            "every query.",
        )

    row = ReferenceTableRow(
        workspace_id=workspace_id,
        slug=slug,
        key_columns=list(key_columns),
        payload_columns=list(payload_columns),
        description=description,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "That reference table already exists",
            409,
            f"Reference table {slug!r} exists. Load a new *version* of it instead.",
        ) from exc

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="reference_table.created",
        entity_ref=f"reference_table:{slug}",
        after={"slug": slug, "key_columns": list(key_columns)},
    )
    return row


async def load_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    rows: Sequence[dict[str, Any]],
    source_note: str | None = None,
) -> ReferenceTableVersionRow:
    """Load a new version of a reference table (FR-DATA-29, FR-DATA-30).

    Each row carries `key`, `payload`, `effective_from` and an optional `effective_to`.
    The version is loaded **whole**: a partial load would leave a table that looks complete
    and silently misses keys, and the lookup failure surfaces as a rating error months
    later on one postcode.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.ADMIN_MANAGE_SETTINGS,
    )
    table = await _load_table(session, workspace_id=workspace_id, slug=slug)

    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(ReferenceTableVersionRow.version), 0)).where(
                ReferenceTableVersionRow.reference_table_id == table.id
            )
        )
    ).scalar_one()

    version_row = ReferenceTableVersionRow(
        workspace_id=workspace_id,
        reference_table_id=table.id,
        version=version,
        status=DRAFT,
        source_note=source_note,
    )
    session.add(version_row)
    await session.flush()

    for entry in rows:
        session.add(
            ReferenceRowRow(
                reference_table_version_id=version_row.id,
                key=str(entry["key"]),
                payload=entry.get("payload", {}),
                effective_from=_as_date(entry["effective_from"]),
                effective_to=_as_date(entry.get("effective_to")),
            )
        )
    try:
        await session.flush()
    except IntegrityError as exc:
        # The exclusion constraint is the only thing that can fail here, and it fails for
        # exactly one reason worth naming.
        raise PlatformError(
            "REFERENCE_INTERVAL_OVERLAP",
            "Two rows cover the same key on the same date",
            409,
            "FR-DATA-31 requires effective-dated intervals for one key to be disjoint. "
            "Overlapping rows give an as-at lookup two answers, and which one a quote "
            "receives would depend on row order.",
        ) from exc

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="reference_table_version.loaded",
        entity_ref=f"reference_table:{slug}@{version}",
        after={"version": version, "rows": len(rows), "status": DRAFT},
    )
    _log.info("reference version loaded", extra={"slug": slug, "version": version})
    return version_row


async def publish_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    version: int,
) -> ReferenceTableVersionRow:
    """`draft` → `published` (FR-DATA-30). Only a published version may be pinned."""
    table = await _load_table(session, workspace_id=workspace_id, slug=slug)
    row = (
        await session.execute(
            select(ReferenceTableVersionRow).where(
                ReferenceTableVersionRow.reference_table_id == table.id,
                ReferenceTableVersionRow.version == version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Reference table version not found",
            404,
            f"{slug!r} has no version {version}.",
        )
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.ADMIN_MANAGE_SETTINGS,
    )
    if row.status == PUBLISHED:
        return row

    row.status = PUBLISHED
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="reference_table_version.published",
        entity_ref=f"reference_table:{slug}@{version}",
        before={"status": DRAFT},
        after={"status": PUBLISHED},
    )
    return row


async def lookup(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    slug: str,
    key: str,
    as_at: date,
    version: int | None = None,
) -> dict[str, Any]:
    """Point lookup, as at a date (FR-DATA-31).

    `version=None` reads the highest published version — acceptable for the debugging
    endpoint this serves, and **not** how rating resolves one. FR-DATA-32 requires a rating
    version to pin an id, because "latest" evaluated at scoring time is a different answer
    each month.
    """
    table = await _load_table(session, workspace_id=workspace_id, slug=slug)
    query = select(ReferenceTableVersionRow).where(
        ReferenceTableVersionRow.reference_table_id == table.id,
        ReferenceTableVersionRow.status == PUBLISHED,
    )
    query = (
        query.where(ReferenceTableVersionRow.version == version)
        if version is not None
        else query.order_by(ReferenceTableVersionRow.version.desc()).limit(1)
    )
    version_row = (await session.execute(query)).scalar_one_or_none()
    if version_row is None:
        raise PlatformError(
            "REFERENCE_VERSION_NOT_PINNED",
            "No published version of this reference table",
            404,
            f"{slug!r} has no published version"
            + (f" {version}." if version is not None else ". Publish one before using it."),
        )

    row = (
        await session.execute(
            select(ReferenceRowRow).where(
                ReferenceRowRow.reference_table_version_id == version_row.id,
                ReferenceRowRow.key == key,
                ReferenceRowRow.effective_from <= as_at,
                (ReferenceRowRow.effective_to.is_(None))
                | (ReferenceRowRow.effective_to > as_at),
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "No reference row for that key on that date",
            404,
            f"{slug!r}@{version_row.version} has no row for key {key!r} effective on "
            f"{as_at.isoformat()}. The interval is half-open: a row ending on that date "
            "does not cover it.",
        )
    return {
        "reference_table_version_id": str(version_row.id),
        "version": version_row.version,
        "key": row.key,
        "payload": row.payload,
        "effective_from": row.effective_from.isoformat(),
        "effective_to": row.effective_to.isoformat() if row.effective_to else None,
    }


async def _load_table(
    session: AsyncSession, *, workspace_id: UUID, slug: str
) -> ReferenceTableRow:
    row = (
        await session.execute(
            select(ReferenceTableRow).where(
                ReferenceTableRow.workspace_id == workspace_id,
                ReferenceTableRow.slug == slug,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Reference table not found", 404, f"No reference table {slug!r}."
        )
    return row


def _as_date(value: Any) -> date | None:
    if value is None or isinstance(value, date):
        return value if not isinstance(value, bool) else None
    return date.fromisoformat(str(value))
