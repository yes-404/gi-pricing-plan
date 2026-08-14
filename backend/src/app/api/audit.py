"""The audit log API (`06` §5.1, FR-GOV-23, FR-GOV-24).

| Method | Path |
|---|---|
| `GET` | `/api/v1/audit` — query by actor, entity, action, time range, free text |
| `GET` | `/api/v1/audit/verify` — recompute the hash chain |
| `GET` | `/api/v1/audit/export` — CSV or JSON |

Read-only, and there is deliberately no write path: events are emitted by the transactions
that cause them (`06` R2), never posted. An endpoint that could append to the audit log
would be a way to write history without doing anything.

`audit:read` is the permission, held by the Auditor role and by every read-everything role.
FR-GOV-5 is the reason it is not admin-gated: an Auditor must be able to read the log
without being able to change anything, and an Admin must not be able to hide it from them.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select, func, or_, select

from app.api.authz import requires
from app.api.deps import Caller
from app.api.pagination import (
    COUNT_CAP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    Page,
    decode_int_cursor,
    encode_cursor,
)
from app.api.responses import problems
from app.db.models import AuditEventRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit as audit_service
from model_schema import Permission

__all__ = ["router"]

router = APIRouter(prefix="/audit", tags=["governance"])

ReadAudit = Annotated[Caller, Depends(requires(Permission.AUDIT_READ))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class AuditEventView(BaseModel):
    """An event as returned by the API (`06` §4.5).

    Includes `event_hash` and `prev_event_hash`: an auditor exporting the log must be able
    to recompute the chain outside the platform, which is what makes it evidence rather
    than a report (FR-GOV-24).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    sequence: int
    at: datetime
    actor: dict[str, Any]
    source: str
    action: str
    entity_ref: str
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    justification: str | None = None
    trace_id: str | None = None
    job_id: UUID | None = None
    prev_event_hash: str | None = None
    event_hash: str


class ChainVerification(BaseModel):
    """The result of recomputing the chain (FR-GOV-24)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workspace_id: UUID
    events_checked: int
    intact: bool
    broken_at_sequence: int | None = Field(
        default=None, description="First event whose hash or link did not verify."
    )
    reason: str | None = None


def _view(row: AuditEventRow) -> AuditEventView:
    return AuditEventView(
        id=row.id,
        sequence=row.sequence,
        at=row.at,
        actor=row.actor,
        source=row.source.value,
        action=row.action,
        entity_ref=row.entity_ref,
        before=row.before,
        after=row.after,
        justification=row.justification,
        trace_id=row.trace_id,
        job_id=row.job_id,
        prev_event_hash=row.prev_event_hash,
        event_hash=row.event_hash,
    )


def _filtered(
    workspace_id: UUID,
    *,
    actor: UUID | None,
    entity: str | None,
    action: str | None,
    from_: datetime | None,
    to: datetime | None,
    q: str | None,
) -> list[Any]:
    conditions: list[Any] = [AuditEventRow.workspace_id == workspace_id]
    if actor is not None:
        conditions.append(AuditEventRow.actor["id"].astext == str(actor))
    if entity is not None:
        conditions.append(AuditEventRow.entity_ref == entity)
    if action is not None:
        conditions.append(AuditEventRow.action == action)
    if from_ is not None:
        conditions.append(AuditEventRow.at >= from_)
    if to is not None:
        conditions.append(AuditEventRow.at <= to)
    if q:
        # Free text over justifications (FR-GOV-23). Deliberately not over `before`/`after`:
        # those are structured state, and a substring match across them would return events
        # whose relevance nobody could explain.
        conditions.append(
            or_(
                AuditEventRow.justification.ilike(f"%{q}%"),
                AuditEventRow.action.ilike(f"%{q}%"),
            )
        )
    return conditions


@router.get("", summary="Query the audit log", responses=problems(400, 401, 403, 422))
async def query_audit(
    caller: ReadAudit,
    database: DatabaseDep,
    actor: UUID | None = None,
    entity: str | None = None,
    action: str | None = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
    q: str | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[AuditEventView]:
    """Filtered and cursor-paginated (FR-GOV-23, `00` §5.2).

    Ordered by `sequence`, the per-workspace monotonic counter, rather than by `at`: events
    written in one transaction share a timestamp, and a log whose order cannot be
    reconstructed cannot be verified.
    """
    conditions = _filtered(
        caller.workspace_id, actor=actor, entity=entity, action=action,
        from_=from_, to=to, q=q,
    )
    after = decode_int_cursor(cursor)

    query: Select[Any] = (
        select(AuditEventRow)
        .where(*conditions)
        .order_by(AuditEventRow.sequence.desc())
        .limit(limit + 1)
    )
    if after is not None:
        query = query.where(AuditEventRow.sequence < after)

    async with database.session() as session:
        rows = list((await session.execute(query)).scalars())
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(AuditEventRow.id).where(*conditions).limit(COUNT_CAP).subquery()
                )
            )
        ).scalar_one()

    has_more = len(rows) > limit
    page_rows = rows[:limit]
    return Page[AuditEventView](
        items=[_view(row) for row in page_rows],
        next_cursor=encode_cursor(page_rows[-1].sequence) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.get(
    "/verify",
    summary="Recompute the hash chain (FR-GOV-24)",
    responses=problems(401, 403, 422),
)
async def verify_chain(caller: ReadAudit, database: DatabaseDep) -> ChainVerification:
    """Recompute every hash for this workspace and report the first break.

    Returns `200` with `intact: false` rather than an error status. A broken chain is a
    *finding*, and an auditor asking the question needs the answer and the sequence number
    — not a 500 that looks like the endpoint is broken.
    """
    async with database.session() as session:
        try:
            checked = await audit_service.verify_chain(session, caller.workspace_id)
        except audit_service.ChainBrokenError as exc:
            return ChainVerification(
                workspace_id=caller.workspace_id,
                events_checked=exc.sequence - 1,
                intact=False,
                broken_at_sequence=exc.sequence,
                reason=exc.reason,
            )
    return ChainVerification(
        workspace_id=caller.workspace_id, events_checked=checked, intact=True
    )


@router.get(
    "/export",
    summary="Export the audit log as CSV or JSON",
    responses=problems(400, 401, 403, 422),
)
async def export_audit(
    caller: ReadAudit,
    database: DatabaseDep,
    format: Annotated[str, Query(pattern="^(csv|json)$")] = "csv",
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
) -> StreamingResponse:
    """Stream the log out, hashes included.

    The hashes are the point of the export: an auditor recomputes them with
    `model_schema.compute_event_hash` and finds any break without the platform's help. An
    export that omitted them would be a report about the log rather than the log.
    """
    if format not in {"csv", "json"}:  # pragma: no cover - Query pattern enforces it
        raise PlatformError("VALIDATION_FAILED", "Unsupported format", 422, format)

    conditions = _filtered(
        caller.workspace_id, actor=None, entity=None, action=None, from_=from_, to=to, q=None
    )

    async def rows() -> Any:
        async with database.session() as session:
            result = await session.stream_scalars(
                select(AuditEventRow).where(*conditions).order_by(AuditEventRow.sequence)
            )
            async for row in result:
                yield row

    if format == "json":

        async def json_lines() -> Any:
            # JSON Lines, not one array: an audit log is unbounded, and a consumer should
            # be able to start verifying the chain before the export finishes.
            async for row in rows():
                yield _view(row).model_dump_json() + "\n"

        return StreamingResponse(
            json_lines(),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": 'attachment; filename="audit.jsonl"'},
        )

    async def csv_rows() -> Any:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        columns = [
            "sequence", "id", "at", "actor", "source", "action", "entity_ref",
            "justification", "trace_id", "job_id", "prev_event_hash", "event_hash",
        ]
        writer.writerow(columns)
        yield buffer.getvalue()
        async for row in rows():
            buffer.seek(0)
            buffer.truncate()
            writer.writerow(
                [
                    row.sequence, row.id, row.at.isoformat(), row.actor.get("display") or "",
                    row.source.value, row.action, row.entity_ref, row.justification or "",
                    row.trace_id or "", row.job_id or "", row.prev_event_hash or "",
                    row.event_hash,
                ]
            )
            yield buffer.getvalue()

    return StreamingResponse(
        csv_rows(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="audit.csv"'},
    )
