"""The Jobs API (`07` §5.1).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/jobs` | List, filtered, cursor-paginated |
| `GET` | `/api/v1/jobs/{id}` | Detail with progress and result |
| `GET` | `/api/v1/jobs/{id}/logs` | Captured log lines (FR-PLAT-10) |
| `POST` | `/api/v1/jobs/{id}/cancel` | Cooperative cancellation (FR-PLAT-9) |
| `GET` | `/api/v1/jobs/{id}/events` | SSE stream of progress updates |

There is deliberately **no `POST /api/v1/jobs`**. The spec does not define one: Jobs are
created by the domain action that needs them — `POST /dataset-versions/{id}/validate`,
`POST /models` — which returns `202` with the Job and a `Location` header (`00` §5.1, R1).
A generic "submit any job kind" endpoint would let a caller construct work the owning
module never sanctioned, and would have to duplicate that module's validation to be safe.

Every route is workspace-scoped through `require_caller`. A Job belongs to exactly one
workspace (FR-OVR-13), and an id from another one must be indistinguishable from an id
that does not exist — otherwise the 404/403 difference confirms the Job exists.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select

from app.api.authz import requires
from app.api.deps import Caller
from app.api.pagination import (
    COUNT_CAP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    Page,
    decode_cursor,
    decode_int_cursor,
    encode_cursor,
)
from app.api.responses import problems
from app.db.models import JobLogRow, JobRow
from app.db.session import Database
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import jobs as job_service
from model_schema import Job, JobKind, JobStatus
from model_schema import Permission as Perm

__all__ = ["router"]

_log = get_logger("app.api.jobs")

router = APIRouter(prefix="/jobs", tags=["jobs"])

#: FR-GOV-2: the permission is part of the route definition, not buried in a handler.
ReadJobs = Annotated[Caller, Depends(requires(Perm.JOB_READ))]
CancelJobs = Annotated[Caller, Depends(requires(Perm.JOB_CANCEL))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def _stall_seconds(request: Request) -> int:
    """The window after which a silent running Job is reported as stalled (NFR-PLAT-3)."""
    seconds: int = request.app.state.settings.job_stall_seconds
    return seconds


DatabaseDep = Annotated[Database, Depends(_database)]
StallDep = Annotated[int, Depends(_stall_seconds)]


class JobLogLine(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    at: str
    level: str
    logger: str
    message: str
    trace_id: str | None = None


async def _load_scoped(database: Database, job_id: UUID, caller: Caller) -> JobRow:
    """Fetch a Job that belongs to the caller's workspace, or 404.

    A Job in another workspace yields the same 404 as one that does not exist. Returning
    403 instead would confirm the id is real, which is a disclosure in a multi-tenant
    system even when the body says nothing else.
    """
    async with database.session() as session:
        row = await session.get(JobRow, job_id)
    if row is None or row.workspace_id != caller.workspace_id:
        raise PlatformError("NOT_FOUND", "Job not found", 404, f"No job with id {job_id}.")
    return row


@router.get("", summary="List jobs", responses=problems(400, 401, 403, 422))
async def list_jobs(
    caller: ReadJobs,
    database: DatabaseDep,
    stall_seconds: StallDep,
    status_filter: Annotated[JobStatus | None, Query(alias="status")] = None,
    kind: JobKind | None = None,
    submitted_by: UUID | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[Job]:
    """Filtered, cursor-paginated (`00` §5.2)."""
    after = decode_cursor(cursor)

    conditions = [JobRow.workspace_id == caller.workspace_id]
    if status_filter is not None:
        conditions.append(JobRow.status == status_filter)
    if kind is not None:
        conditions.append(JobRow.kind == kind)
    if submitted_by is not None:
        # `submitted_by` is JSONB; the id is compared as text because that is how it is
        # stored, and casting the column instead would not use an index if one is added.
        conditions.append(JobRow.submitted_by["id"].astext == str(submitted_by))

    # Newest first, by id. UUIDv7 is time-ordered, so one column gives both a stable sort
    # and a unique cursor — a (timestamp, id) pair would be needed for a random key.
    query = select(JobRow).where(*conditions).order_by(JobRow.id.desc()).limit(limit + 1)
    if after is not None:
        query = query.where(JobRow.id < after)

    async with database.session() as session:
        rows = list((await session.execute(query)).scalars())
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(JobRow.id).where(*conditions).limit(COUNT_CAP).subquery()
                )
            )
        ).scalar_one()

    # One extra row was fetched purely to answer "is there another page?" without a second
    # count query. It is not returned.
    has_more = len(rows) > limit
    page_rows = rows[:limit]

    return Page[Job](
        items=[
            job_service.to_schema(row, stall_seconds=stall_seconds) for row in page_rows
        ],
        next_cursor=encode_cursor(page_rows[-1].id) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.get(
    "/{job_id}",
    summary="Job detail with progress and result",
    responses=problems(401, 403, 404, 422),
)
async def get_job(
    job_id: UUID, caller: ReadJobs, database: DatabaseDep, stall_seconds: StallDep
) -> Job:
    return job_service.to_schema(
        await _load_scoped(database, job_id, caller), stall_seconds=stall_seconds
    )


@router.get(
    "/{job_id}/logs",
    summary="Captured log lines (FR-PLAT-10)",
    responses=problems(400, 401, 403, 404, 422),
)
async def get_job_logs(
    job_id: UUID,
    caller: ReadJobs,
    database: DatabaseDep,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[JobLogLine]:
    """Oldest first — a log read out of order is not a log.

    Ordered by the database-assigned `seq`, not by the UUIDv7 id: ids generated within one
    millisecond have no defined order, and every row written in a single transaction shares
    its `at` timestamp. Both produce scrambled output.
    """
    await _load_scoped(database, job_id, caller)
    after = decode_int_cursor(cursor)

    query = (
        select(JobLogRow)
        .where(JobLogRow.job_id == job_id)
        .order_by(JobLogRow.seq)
        .limit(limit + 1)
    )
    if after is not None:
        query = query.where(JobLogRow.seq > after)

    async with database.session() as session:
        rows = list((await session.execute(query)).scalars())
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(JobLogRow.seq)
                    .where(JobLogRow.job_id == job_id)
                    .limit(COUNT_CAP)
                    .subquery()
                )
            )
        ).scalar_one()

    has_more = len(rows) > limit
    page_rows = rows[:limit]
    return Page[JobLogLine](
        items=[
            JobLogLine(
                at=row.at.isoformat(),
                level=row.level,
                logger=row.logger,
                message=row.message,
                trace_id=row.trace_id,
            )
            for row in page_rows
        ],
        next_cursor=encode_cursor(page_rows[-1].seq) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.post(
    "/{job_id}/cancel",
    summary="Request cooperative cancellation (FR-PLAT-9)",
    status_code=status.HTTP_200_OK,
    responses=problems(401, 403, 404, 409, 422),
)
async def cancel_job(job_id: UUID, caller: CancelJobs, database: DatabaseDep) -> Job:
    """Cancel a Job.

    A `queued` Job is cancelled outright; a `running` one is *marked* and stops at its next
    checkpoint, so the response may still report `running`. That is the honest answer —
    reporting `cancelled` while the work is still burning CPU shows a freed worker slot
    that is not free.
    """
    await _load_scoped(database, job_id, caller)
    async with database.unit_of_work() as session:
        return await job_service.request_cancellation(
            session, job_id, actor=caller.principal
        )


@router.get(
    "/{job_id}/events",
    summary="SSE stream of progress updates",
    responses=problems(401, 403, 404, 422),
)
async def stream_job_events(
    job_id: UUID,
    caller: ReadJobs,
    database: DatabaseDep,
    request: Request,
) -> Response:
    """Server-sent events, so the UI shows progress where the action was taken (`07` §6).

    Polled rather than pushed. A `LISTEN`/`NOTIFY` subscription would hold a database
    connection open per viewer, and a jobs page with twenty rows open in three browsers
    exhausts the pool. Polling one row on an interval is dull and survives a restart of
    anything.

    The stream closes when the Job reaches a terminal state, so a client that forgets to
    unsubscribe does not hold the connection for ever.
    """
    await _load_scoped(database, job_id, caller)

    async def events() -> AsyncIterator[str]:
        last_payload: str | None = None
        while True:
            if await request.is_disconnected():
                return

            async with database.session() as session:
                row = await session.get(JobRow, job_id)
            if row is None:
                return

            payload = json.dumps(
                {
                    "id": str(row.id),
                    "status": row.status.value,
                    "progress": row.progress,
                    "trace_id": row.trace_id,
                }
            )
            # Only send on change: an unchanged heartbeat every second is noise the client
            # has to filter, and it defeats the point of a stream over a poll.
            if payload != last_payload:
                last_payload = payload
                yield f"event: progress\ndata: {payload}\n\n"

            if row.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}:
                yield f"event: done\ndata: {payload}\n\n"
                return

            await asyncio.sleep(1.0)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            # Without this an intermediary proxy buffers the stream and the client sees
            # nothing until the job finishes, which looks exactly like a hung job.
            "X-Accel-Buffering": "no",
        },
    )
