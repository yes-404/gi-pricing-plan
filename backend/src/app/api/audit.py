"""The audit log API (`06` §5.1, FR-371, FR-372).

| Method | Path |
|---|---|
| `GET` | `/api/v1/audit` — query by actor, entity, action, time range, free text |
| `GET` | `/api/v1/audit/verify` — recompute the hash chain |
| `GET` | `/api/v1/audit/export` — CSV or JSON |

Read-only, and there is deliberately no write path: events are emitted by the transactions
that cause them (`06` R2), never posted. An endpoint that could append to the audit log
would be a way to write history without doing anything.

`audit:read` is the permission, held by the Auditor role and by every read-everything role.
FR-346 is the reason it is not admin-gated: an Auditor must be able to read the log
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
from sqlalchemy import Select, and_, func, or_, select

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
from model_schema import AuditEventListing, AuditEventRecord, Permission, Principal

__all__ = ["router"]

router = APIRouter(prefix="/audit", tags=["governance"])

ReadAudit = Annotated[Caller, Depends(requires(Permission.AUDIT_READ))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class ChainVerification(BaseModel):
    """The result of recomputing the chain (FR-372)."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    workspace_id: UUID
    from_: datetime | None = Field(
        default=None, alias="from", description="The requested lower bound on `at`, if any."
    )
    to: datetime | None = Field(
        default=None, description="The requested upper bound on `at`, if any."
    )
    whole_chain: bool = Field(
        description="True when no range was given: the whole chain, NFR-521's proof."
    )
    first_sequence: int | None = Field(
        default=None,
        description="Where the check began. The event before it is not itself verified.",
    )
    last_sequence: int | None = Field(
        default=None, description="The last event verified, or `None` if none was."
    )
    events_checked: int
    intact: bool
    broken_at_sequence: int | None = Field(
        default=None, description="First event whose hash or link did not verify."
    )
    reason: str | None = None


def _record(row: AuditEventRow) -> AuditEventRecord:
    """The stored row as `model_schema.AuditEventRecord`, hashes included, and nothing else.

    The export's shape: an auditor exporting the log recomputes the chain outside the platform
    from exactly these fields (FR-372), which is what makes it evidence rather than a report.
    It is the stored event and nothing derived, and it is the contract's shape, not a copy.
    """
    return AuditEventRecord(
        id=row.id,
        workspace_id=row.workspace_id,
        sequence=row.sequence,
        at=row.at,
        actor=Principal.model_validate(row.actor),
        source=row.source,
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


def _listing(row: AuditEventRow) -> AuditEventListing:
    """What the explorer's query returns: the stored record plus the derived `current_action`.

    The derived field is for the views only and is never exported (see `_record`).
    """
    return AuditEventListing(
        **_record(row).model_dump(),
        current_action=audit_service.current_action_of(row.action, row.before),
    )


def _require_aware(from_: datetime | None, to: datetime | None) -> None:
    """Refuse a `from` or `to` that carries no UTC offset, on every route that takes them.

    A bound without an offset is ambiguous: the driver reads it in the API process's local
    timezone (asyncpg encodes a naive `datetime` through `astimezone`), so a query's range, or
    an export's, could shift without notice, and comparing it with an aware bound raises.
    The detail names the parameter and never echoes the value (NFR-499).
    """
    for name, bound in (("from", from_), ("to", to)):
        if bound is not None and bound.tzinfo is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Invalid range",
                422,
                f"`{name}` must carry a UTC offset, for example a trailing Z.",
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
        legacy = audit_service.RETURNED_LEGACY_ACTIONS.get(action)
        if legacy is None:
            conditions.append(AuditEventRow.action == action)
        else:
            # C1 (Q3 (a2)): rows written before the rename spell the return as the forward
            # state's name; the stored rows are never rewritten (FR-370), so the filter
            # finds both. A forward transition has `before.status` other than `review`.
            conditions.append(
                or_(
                    AuditEventRow.action == action,
                    and_(
                        AuditEventRow.action == legacy,
                        AuditEventRow.before["status"].astext == "review",
                    ),
                )
            )
    if from_ is not None:
        conditions.append(AuditEventRow.at >= from_)
    if to is not None:
        conditions.append(AuditEventRow.at <= to)
    if q:
        # Free text over justifications (FR-371). Deliberately not over `before`/`after`:
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
) -> Page[AuditEventListing]:
    """Filtered and cursor-paginated (FR-371, `00` §5.2).

    Ordered by `sequence`, the per-workspace monotonic counter, rather than by `at`: events
    written in one transaction share a timestamp, and a log whose order cannot be
    reconstructed cannot be verified.
    """
    _require_aware(from_, to)
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
    return Page[AuditEventListing](
        items=[_listing(row) for row in page_rows],
        next_cursor=encode_cursor(page_rows[-1].sequence) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.get(
    "/verify",
    summary="Recompute the hash chain (FR-372)",
    responses=problems(401, 403, 422),
)
async def verify_chain(
    caller: ReadAudit,
    database: DatabaseDep,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
) -> ChainVerification:
    """Recompute the hashes of this workspace's chain and report the first break.

    With neither `from` nor `to` the whole chain is verified, and that is NFR-521's proof.
    With either, the contiguous sequence span they select is verified (`first_sequence` and
    `last_sequence` say which); the event just before the span is not itself verified.

    Returns `200` with `intact: false` rather than an error status. A broken chain is a
    *finding*, and an auditor asking the question needs the answer and the sequence number
    — not a 500 that looks like the endpoint is broken.
    """
    _require_aware(from_, to)
    if from_ is not None and to is not None and from_ > to:
        raise PlatformError(
            "VALIDATION_FAILED", "Invalid range", 422, "`from` is after `to`."
        )
    # The request, echoed: `from` is an alias, which the mypy plugin will not take as a keyword.
    requested: dict[str, Any] = {"workspace_id": caller.workspace_id, "from": from_, "to": to}
    async with database.session() as session:
        try:
            span = await audit_service.verify_range(
                session, caller.workspace_id, from_=from_, to=to
            )
        except audit_service.ChainBrokenError as exc:
            return ChainVerification(
                **requested,
                whole_chain=from_ is None and to is None,
                first_sequence=exc.first_sequence,
                # The last sequence ACTUALLY verified, not the one before the break: on a gap the
                # sequence before it names an event that is absent and was never checked.
                last_sequence=exc.first_sequence + exc.checked - 1 if exc.checked else None,
                events_checked=exc.checked,
                intact=False,
                broken_at_sequence=exc.sequence,
                reason=exc.reason,
            )
    return ChainVerification(
        **requested,
        whole_chain=span.whole_chain,
        first_sequence=span.first_sequence,
        last_sequence=span.last_sequence,
        events_checked=span.events_checked,
        intact=True,
    )


@router.get(
    "/export",
    summary="Export the audit log as CSV or JSON",
    response_class=StreamingResponse,
    responses={
        **problems(400, 401, 403, 422),
        200: {
            "description": "The log as CSV, or as JSON Lines (one event per line)",
            "content": {
                "text/csv": {"schema": {"type": "string"}},
                "application/x-ndjson": {"schema": {"type": "string"}},
            },
        },
    },
)
async def export_audit(
    caller: ReadAudit,
    database: DatabaseDep,
    format: Annotated[str, Query(pattern="^(csv|json)$")] = "csv",
    actor: UUID | None = None,
    entity: str | None = None,
    action: str | None = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
    q: str | None = None,
) -> StreamingResponse:
    """Stream the events the query would show: the same filters, in `sequence` order.

    **JSON Lines is the evidence form**: one `AuditEventRecord` per line, every hashed field
    and both hashes, so an auditor recomputes each hash with `model_schema` and finds an
    edited event without the platform's help. **The CSV is a report**: readable columns and
    the two hashes, but not the whole event (no `workspace_id`, `before` or `after`, and
    only the actor's display name), so it cannot be recomputed.

    A filtered export is the matching events with gaps, so it cannot show the chain is
    unbroken. Whether it is, is `/verify`'s to say (FR-372), not the file's.
    """
    if format not in {"csv", "json"}:  # pragma: no cover - Query pattern enforces it
        raise PlatformError("VALIDATION_FAILED", "Unsupported format", 422, format)

    _require_aware(from_, to)
    conditions = _filtered(
        caller.workspace_id, actor=actor, entity=entity, action=action, from_=from_, to=to, q=q
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
                yield _record(row).model_dump_json() + "\n"

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
