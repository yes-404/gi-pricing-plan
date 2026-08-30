"""Trace persistence: the row-plus-blob write, the read, and the retention-floor guard.

`03` §4.5's `Trace`, FR-RATE-41/42, `00` NFR-OVR-6, W11 Task 4A
(`docs/plans/2026-08-29-w11-4-trace-sampling-persistence.md`, Ruling 23 in
`docs/plans/2026-08-29-w11-slices-3-4-rulings.md`).

**One serialisation, two writes.** `write_trace` serialises the `Trace` exactly once and
uses that same payload both for the blob body and for the row's three projected fields
(`quote_id`, `rating_version_ref`, `bundle_hash`) — never re-derived from anything else,
which is what keeps the row from diverging from the body it claims to summarise (Ruling
23's second constraint).

**No expiry job.** FR-PLAT-20's blob GC is a deletion mechanism; NFR-OVR-6 is a
preservation floor. Nothing in this module runs on a schedule. The only way NFR-OVR-6 can
be breached is an early row deletion, so `delete_trace` is the one guard this slice owes —
refusing while the floor still covers the row, permitting once it does not.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Final, Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BlobRow, ScoringTraceRow
from app.errors import PlatformError
from app.platform import blobs
from app.platform.blobs import BlobStore, to_ref
from model_schema import Trace

__all__ = ["SampleReason", "delete_trace", "read_trace", "write_trace"]

#: FR-RATE-42's three sampling reasons. Task 4B decides which applies to a given quote;
#: this module only persists the answer.
SampleReason = Literal["rate", "decline", "error"]

#: NFR-OVR-6: "≥ 13 months". 13 calendar months average 395.7 days; 396 is that floor with
#: no rounding-down risk — the same reasoning `retention.job_history_days`
#: (`app/platform/settings.py`) already uses for FR-PLAT-14's identical ≥ 13-month floor.
#: A plain constant, not a workspace setting: NFR-OVR-6 states a fixed minimum, never
#: "configurable" the way FR-RATE-42's sampling *rate* is.
_RETENTION_FLOOR_DAYS: Final = 396


async def write_trace(
    session: AsyncSession,
    blob_store: BlobStore,
    trace: Trace,
    *,
    workspace_id: UUID,
    sample_reason: SampleReason,
    environment: str | None = None,
) -> ScoringTraceRow:
    """Persist one sampled `Trace`: a blob body plus its projected row, from one payload.

    Requires the caller's transaction, same as `BlobStore.put` — the row and the blob's
    accounting must commit together or not at all.

    `environment` is left `None` for a trace written on request against a batch Job
    (FR-RATE-41, Ruling 25): it has no live environment, and `GET /api/v1/traces` reads
    that absence as the signal that excludes it from the production stream (`03` §5.1).
    """
    payload = trace.model_dump_json().encode()
    ref = await blob_store.put(session, payload, "application/json")
    # Keeps `ref_count > 0` so FR-PLAT-20's GC (`ref_count == 0` is its selector) can never
    # consider this blob a candidate for as long as this row exists — the claim Ruling 23
    # rests the whole retention design on, verified rather than assumed
    # (`backend/tests/test_traces.py`'s GC-survival test).
    await blobs.retain(session, ref.sha256)

    row = ScoringTraceRow(
        workspace_id=workspace_id,
        quote_id=trace.quote_id,
        rating_version_ref=str(trace.rating_version_ref),
        bundle_hash=trace.bundle_hash,
        sample_reason=sample_reason,
        environment=environment,
        blob_sha256=ref.sha256,
    )
    session.add(row)
    await session.flush()
    return row


async def read_trace(session: AsyncSession, blob_store: BlobStore, row: ScoringTraceRow) -> Trace:
    """Fetch a persisted trace's body and reconstruct the `Trace` it was written from."""
    blob_row = await session.get(BlobRow, row.blob_sha256)
    if blob_row is None:  # pragma: no cover - retain() keeps this from ever happening
        raise PlatformError(
            "BLOB_NOT_FOUND",
            "Blob not found",
            404,
            f"scoring_traces row {row.id} references blob {row.blob_sha256}, which is gone.",
        )
    body = await blob_store.read(to_ref(blob_row))
    return Trace.model_validate_json(body)


async def delete_trace(
    session: AsyncSession,
    trace_id: UUID,
    *,
    floor_days: int | None = None,
    now: datetime | None = None,
) -> None:
    """Delete a trace row, refusing while NFR-OVR-6's ≥ 13-month floor still covers it.

    The **only** way the retention floor can be breached is an early row deletion (Ruling
    23) — there is no expiry job, so this is the one place age is ever checked. Releases
    the blob reference on a permitted delete, mirroring `write_trace`'s `retain`: without
    it the blob would sit at `ref_count > 0` forever and never become GC-eligible.
    """
    row = await session.get(ScoringTraceRow, trace_id)
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Trace not found", 404, f"No scoring trace with id {trace_id}."
        )

    floor = floor_days if floor_days is not None else _RETENTION_FLOOR_DAYS
    cutoff = (now or datetime.now(UTC)) - timedelta(days=floor)
    if row.created_at > cutoff:
        eligible_at = row.created_at + timedelta(days=floor)
        raise PlatformError(
            "TRACE_RETENTION_FLOOR",
            "Trace is inside its retention floor",
            409,
            f"`00` NFR-OVR-6 retains sampled traces for >= {floor} days; this trace was "
            f"written {row.created_at.isoformat()} and cannot be deleted before "
            f"{eligible_at.isoformat()}.",
        )

    await blobs.release(session, row.blob_sha256)
    await session.delete(row)
