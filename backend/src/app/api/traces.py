"""`GET /api/v1/traces` — sampled production traces (`03` §5.1:603, FR-259; WK-671 Task 4C).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/traces?rating_version=&from=&to=` | Sampled **production** traces (FR-259) |

**Gated on `Permission.RATING_READ`, not a Service Account scoring permission — a
deliberate departure from `/score` and `/score/batch`'s pattern.** FR-347 (`06`:83)
confines Service Accounts to *scoring* permissions — `SCORE_EXECUTE`/`SCORE_BATCH` — and
forbids them holding anything else, `RATING_READ` included
(`backend/tests/test_rbac.py:102-107`). This route does not execute a quote; it reads what
scoring already produced, which is the same shape of operation as `/api/v1/rate-tables` or
`/api/v1/rating-versions` — both `RATING_READ`-gated, both readable by every human role that
touches rating (`analyst`, `pricing_actuary`, `approver`, `deployer`, `auditor`, `admin` all
hold it, the last four via `READ_PERMISSIONS`). Gating this route on `RATING_READ` also
means a Service Account structurally cannot reach it at all: FR-347 forbids granting one
`RATING_READ`, so there is no key-relabelling case to test here the way RL-884 established
for `/score` — that pattern is a Service-Account-authentication concern (an environment-scoped
API key), and this route authenticates human/dev principals against workspace role
assignments, never a scoped key. The two cases that apply are the ones every other
`RATING_READ` route already tests (`backend/tests/test_api_rate_tables.py`'s
`auditor_headers`/no-grant pair): a caller holding the permission may call it, and a
workspace member holding no role is refused **403** at the permission dependency, before the
route body runs.

**NFR-499's access-control obligation is why a permission gates this at all**, not an
afterthought: a trace's `TraceStep.consumed`/`produced` carry the same rating-factor detail a
raw quote input would (postcode, vehicle detail, whatever the bundle's steps evaluate) — the
"full quote input" `06` NFR-499 (RL-917) permits storing only inside an
access-controlled artifact, and a sampled trace is one of the two named. Access control here
is the RBAC gate on the route, exactly as the requirement's own text reads ("which are
access-controlled").

**The exclusion signal is a null `environment`, not a batch parent (Corrected 2026-08-30,
Task 4C — the plan's own Correction 2).** `ScoringTraceRow` carries no Job reference at all;
RL-890 rules that a `score.batch` Job's on-request trace (FR-258) must never appear
in this **production** stream, and `write_trace` (`app/platform/traces.py`) already leaves
`environment` unset for exactly that trace (RL-916). This route reads that absence as its
exclusion condition — `environment IS NOT NULL` — rather than looking for a parent that does
not exist on the row.

**A `pending` row (RL-862) is excluded the same way its lack of a body excludes it**: it
has an `environment` (the real-time path sets it before the off-path re-score runs) but no
`blob_sha256` yet, so `blob_sha256 IS NOT NULL` is a second, independent condition — without
it this route would try to fetch a body that does not exist yet for every row still awaiting
its off-path Job.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authz import requires
from app.api.deps import Caller
from app.api.pagination import (
    COUNT_CAP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    Page,
    decode_cursor,
    encode_cursor,
)
from app.api.responses import problems
from app.db.models import ScoringTraceRow
from app.db.session import Database
from app.platform import traces as traces_service
from app.platform.blobs import BlobStore
from model_schema import Permission, Trace

__all__ = ["router"]

router = APIRouter(prefix="/traces", tags=["rating"])

#: FR-343: the permission is part of the route definition. Not a scoring permission
#: (see module docstring) — a Service Account can never be granted this (FR-347).
ReadTraces = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


DatabaseDep = Annotated[Database, Depends(_database)]
BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]


class TraceView(BaseModel):
    """One item of `GET /api/v1/traces` — the row's queryable fields plus the
    reconstructed `Trace` body (`03` §4.5)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    quote_id: str | None
    rating_version_ref: str
    bundle_hash: str
    sample_reason: str
    #: Never `None` here — the query this view is built from excludes it (see module
    #: docstring). Typed `str` rather than `str | None` because a batch-produced or still-
    #: pending row can never reach this constructor.
    environment: str
    created_at: datetime
    trace: Trace


def _filtered(
    workspace_id: UUID,
    *,
    rating_version: str | None,
    from_: datetime | None,
    to: datetime | None,
) -> list[Any]:
    """The conditions every query below shares — filter and count alike, so the estimate
    always matches what the page could return."""
    conditions: list[Any] = [
        ScoringTraceRow.workspace_id == workspace_id,
        # RL-890's exclusion, via Correction 2's real signal: a batch-produced trace
        # (FR-258, written on request) carries no environment.
        ScoringTraceRow.environment.is_not(None),
        # A pending row (RL-862) has an environment but no body yet — nothing to read.
        ScoringTraceRow.blob_sha256.is_not(None),
    ]
    if rating_version is not None:
        conditions.append(ScoringTraceRow.rating_version_ref == rating_version)
    if from_ is not None:
        conditions.append(ScoringTraceRow.created_at >= from_)
    if to is not None:
        conditions.append(ScoringTraceRow.created_at <= to)
    return conditions


async def _view(session: AsyncSession, blob_store: BlobStore, row: ScoringTraceRow) -> TraceView:
    trace = await traces_service.read_trace(session, blob_store, row)
    assert row.environment is not None  # the query excludes any row this could fail for
    return TraceView(
        id=row.id,
        quote_id=row.quote_id,
        rating_version_ref=row.rating_version_ref,
        bundle_hash=row.bundle_hash,
        sample_reason=row.sample_reason,
        environment=row.environment,
        created_at=row.created_at,
        trace=trace,
    )


@router.get("", summary="Sampled production traces", responses=problems(400, 401, 403, 422))
async def list_traces(
    caller: ReadTraces,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    rating_version: str | None = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[TraceView]:
    """Filtered, cursor-paginated (`00` §5.2), workspace-scoped, excluding anything not a
    complete real-time production trace (see module docstring for both exclusions).
    """
    after = decode_cursor(cursor)
    conditions = _filtered(
        caller.workspace_id, rating_version=rating_version, from_=from_, to=to
    )

    query = (
        select(ScoringTraceRow)
        .where(*conditions)
        .order_by(ScoringTraceRow.id.desc())
        .limit(limit + 1)
    )
    if after is not None:
        query = query.where(ScoringTraceRow.id < after)

    async with database.session() as session:
        rows = list((await session.execute(query)).scalars())
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(ScoringTraceRow.id).where(*conditions).limit(COUNT_CAP).subquery()
                )
            )
        ).scalar_one()

        has_more = len(rows) > limit
        page_rows = rows[:limit]
        items = [await _view(session, blob_store, row) for row in page_rows]

    return Page[TraceView](
        items=items,
        next_cursor=encode_cursor(page_rows[-1].id) if has_more and page_rows else None,
        total_estimate=total,
    )
