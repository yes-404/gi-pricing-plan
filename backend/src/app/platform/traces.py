"""Trace persistence: the row-plus-blob write, the read, and the retention-floor guard.

`03` §4.5's `Trace`, FR-258/259, `00` NFR-459, WK-671 Task 4A
(`docs/plans/PL-00850-wk-671-slice-4-trace-sampling-the-row-plus-blob-store-and-the-retention-floor.md`, RL-888 in
`docs/rulings/INDEX.md#2026-08-29-w11-slices-3-4-rulingsmd`).

**One serialisation, two writes.** `write_trace` serialises the `Trace` exactly once and
uses that same payload both for the blob body and for the row's three projected fields
(`quote_id`, `rating_version_ref`, `bundle_hash`) — never re-derived from anything else,
which is what keeps the row from diverging from the body it claims to summarise (Ruling
23's second constraint).

**No expiry job.** FR-420's blob GC is a deletion mechanism; NFR-459 is a
preservation floor. Nothing in this module runs on a schedule. The only way NFR-459 can
be breached is an early row deletion, so `delete_trace` is the one guard this slice owes —
refusing while the floor still covers the row, permitting once it does not.

**The sampling decision (WK-671 Task 4B) is `decide_sampling`, a pure function.** FR-259:
100 % of declines and 100 % of errors, regardless of the configured rate, plus that rate for
everything else. It takes the roll as an argument rather than calling `random.random()`
itself, so it stays pure and the statistical boundary is testable with a fixed seed — the
caller (the scoring route) supplies the roll.

**Trace production is decoupled from the serving request** (RL-862,
`docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`): always capturing a
trace inline pinned the traced fraction at 1 and put every real-time request over
NFR-489's budget. The quoting path scores untraced and, on a sampled outcome, calls
`write_pending_trace` — a row with no body yet, carrying the Quote Context an off-path Job
needs to reproduce it. `app.worker.trace_handlers` re-scores the *pinned* bundle and calls
`complete_pending_trace`, which fills in the body and records whether the re-score
reproduced the served result (RL-862 §8.2's two safety conditions). `write_trace` is
unchanged and still the single-shot path for a producer that already holds a full `Trace`
(a batch Job's on-request trace, FR-258/RL-890 — there is no serving-request budget
to protect there, so no pending phase is needed).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Final, Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BlobRow, ScoringTraceRow
from app.errors import PlatformError
from app.platform import blobs
from app.platform.blobs import BlobStore, to_ref
from model_schema import ScoringOutcome, ScoringResult, Trace

__all__ = [
    "SampleReason",
    "complete_pending_trace",
    "decide_sampling",
    "delete_trace",
    "read_trace",
    "summarise_result",
    "write_pending_trace",
    "write_trace",
]

#: The fields `summarise_result` compares a re-score against (RL-862 §8.2 condition
#: (b)) — never quote inputs, only what was actually served.
_SUMMARY_FIELDS: Final[set[str]] = {"outcome", "decline_reasons", "premium_ladder", "outputs"}

#: FR-259's three sampling reasons. Task 4B decides which applies to a given quote;
#: this module only persists the answer.
SampleReason = Literal["rate", "decline", "error"]

#: NFR-459: "≥ 13 months". 13 calendar months average 395.7 days; 396 is that floor with
#: no rounding-down risk — the same reasoning `retention.job_history_days`
#: (`app/platform/settings.py`) already uses for FR-410's identical ≥ 13-month floor.
#: A plain constant, not a workspace setting: NFR-459 states a fixed minimum, never
#: "configurable" the way FR-259's sampling *rate* is.
_RETENTION_FLOOR_DAYS: Final = 396


def decide_sampling(
    outcome: ScoringOutcome, rate: float, *, roll: float
) -> tuple[bool, SampleReason | None]:
    """FR-259's sampling policy, as a pure function (WK-671 Task 4B).

    A declined or errored quote is sampled at 100 % **regardless of `rate`**, including
    `rate == 0.0` — that is the floor the requirement states, not an additional condition on
    it. Everything else (`outcome == "quoted"`) is sampled iff `roll < rate`: at `rate ==
    0.0` no roll satisfies that (`roll` is drawn from `[0.0, 1.0)`, so it is never `< 0.0`),
    and at `rate == 1.0` every roll does.

    `roll` is the caller's concern, not this function's — passing it in rather than calling
    `random.random()` here is what keeps this pure and lets the statistical boundary test
    fix a seed. The two 100 % floors need no roll at all, so they are decided before it is
    even inspected.
    """
    if outcome == "declined":
        return True, "decline"
    if outcome == "error":
        return True, "error"
    if roll < rate:
        return True, "rate"
    return False, None


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
    (FR-258, RL-890): it has no live environment, and `GET /api/v1/traces` reads
    that absence as the signal that excludes it from the production stream (`03` §5.1).
    """
    payload = trace.model_dump_json().encode()
    ref = await blob_store.put(session, payload, "application/json")
    # Keeps `ref_count > 0` so FR-420's GC (`ref_count == 0` is its selector) can never
    # consider this blob a candidate for as long as this row exists — the claim RL-888
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


def summarise_result(result: ScoringResult) -> dict[str, Any]:
    """What a re-score is checked against (RL-862 §8.2 condition (b)): `outcome`,
    `decline_reasons`, `premium_ladder` and `outputs` — the served answer, never the raw
    quote inputs that produced it (those travel separately, in `pending_quote_context`).

    Every one of these fields is already JSON-exact — `premium_ladder`'s `value_minor` is
    an `int`, and `outputs`' values are `int`/`str`/`bool` by construction
    (`_coerce_output_value`, `pricing_core.rating.score` — nothing here is a `float`), so
    comparing two dicts built this way is an exact comparison, not an approximate one.
    Shared by the serving route (the *served* summary) and the off-path Job (the
    *reproduced* one) so the two are computed the same way — a summary function that
    diverged between the two call sites could pass a broken reproduction.
    """
    return result.model_dump(mode="json", include=_SUMMARY_FIELDS)


async def write_pending_trace(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    quote_id: str | None,
    rating_version_ref: str,
    bundle_hash: str,
    sample_reason: SampleReason,
    environment: str | None,
    quote_context: dict[str, Any],
    served_summary: dict[str, Any],
) -> ScoringTraceRow:
    """Serve time (WK-671 Task 4B, RL-862): record a sampled outcome before any trace body
    exists — no `Trace` to serialise yet, so no blob write and no I/O beyond the insert.

    `quote_context` is the `QuoteContext` the off-path Job will re-score, as an
    already-JSON-safe dict (`QuoteContext.model_dump(mode="json")`) — RL-862 §8.4's
    access-controlled carrier, kept on this row rather than in `JobRow.parameters`, which
    a workspace member holding no scoring permission can already read. `served_summary` is
    `summarise_result`'s output for the result actually served, compared against the
    re-score's own summary by `complete_pending_trace`.
    """
    row = ScoringTraceRow(
        workspace_id=workspace_id,
        quote_id=quote_id,
        rating_version_ref=rating_version_ref,
        bundle_hash=bundle_hash,
        sample_reason=sample_reason,
        environment=environment,
        status="pending",
        pending_quote_context=quote_context,
        served_summary=served_summary,
        blob_sha256=None,
    )
    session.add(row)
    await session.flush()
    return row


async def complete_pending_trace(
    session: AsyncSession,
    blob_store: BlobStore,
    trace_id: UUID,
    trace: Trace | None,
    *,
    reproduced_summary: dict[str, Any] | None,
) -> ScoringTraceRow:
    """Off-path (WK-671 Task 4B, RL-862): resolve a pending row from a re-score attempt.

    **Never an `UPDATE`.** `835988d1de4c` revokes `UPDATE` on `scoring_traces` outright, so
    this deletes the pending row and inserts the finished one at the same id — and the
    same `created_at`, explicitly carried across, because NFR-459's retention floor is
    measured from it and completion must not reset the clock for a row that, from the
    floor's point of view, has not moved. Both statements run inside the caller's open
    transaction, so a crash between them leaves no orphaned state on commit.

    **Two distinct call shapes, for RL-862 §8.2's two safety conditions:**

    - `trace=None` (condition (a)): the caller could not resolve the *pinned* bundle — it
      refused to score the live one in its place, so no re-score was even attempted. The
      row completes `"mismatch"` with no body; `reproduced_summary` is ignored (pass
      `None`).
    - `trace` given (condition (b)): a re-score *was* produced against the pinned bundle.
      `reproduced_summary == row.served_summary` decides `"complete"` (reproduced) versus
      `"mismatch"` (did not) — the body is written and kept either way, because a trace
      that failed to reproduce is still evidence of what the re-score actually did, and
      the ruling requires the mismatch *recorded*, not the trace discarded.
    """
    row = await session.get(ScoringTraceRow, trace_id)
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Trace not found", 404, f"No scoring trace with id {trace_id}."
        )
    if row.status != "pending":
        raise PlatformError(
            "TRACE_NOT_PENDING",
            "Trace is not pending",
            409,
            f"scoring_traces row {trace_id} has status {row.status!r}, not 'pending' — it "
            "was already completed, or was never a pending row to begin with.",
        )

    if trace is None:
        # Condition (a): the pinned bundle was unresolvable. No re-score, no body.
        blob_sha256: str | None = None
        status = "mismatch"
    else:
        payload = trace.model_dump_json().encode()
        ref = await blob_store.put(session, payload, "application/json")
        await blobs.retain(session, ref.sha256)
        blob_sha256 = ref.sha256
        status = "complete" if reproduced_summary == row.served_summary else "mismatch"

    completed = ScoringTraceRow(
        id=row.id,
        workspace_id=row.workspace_id,
        quote_id=row.quote_id,
        rating_version_ref=row.rating_version_ref,
        bundle_hash=row.bundle_hash,
        sample_reason=row.sample_reason,
        environment=row.environment,
        status=status,
        pending_quote_context=None,
        served_summary=row.served_summary,
        blob_sha256=blob_sha256,
        created_at=row.created_at,
    )
    await session.delete(row)
    await session.flush()
    session.add(completed)
    await session.flush()
    return completed


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
    """Delete a trace row, refusing while NFR-459's ≥ 13-month floor still covers it.

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
            f"`00` NFR-459 retains sampled traces for >= {floor} days; this trace was "
            f"written {row.created_at.isoformat()} and cannot be deleted before "
            f"{eligible_at.isoformat()}.",
        )

    # A pending row (Task 4B) has no blob yet — nothing to release. Every other status
    # does, and `write_trace`/`complete_pending_trace` both `retain` on the way in.
    if row.blob_sha256 is not None:
        await blobs.release(session, row.blob_sha256)
    await session.delete(row)
