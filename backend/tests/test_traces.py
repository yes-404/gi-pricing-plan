"""`03` §4.5 `Trace` persistence — the row-plus-blob write and the retention guard.

FR-258/259, `00` NFR-459, WK-671 Task 4A. Against real PostgreSQL and real MinIO, like
`test_blobs.py`: the retention guard and the GC-survival claim are both database
behaviours a double cannot exercise.

**Task 4B's pure `decide_sampling` tests are plain, synchronous and need no database** —
they are at the top of this file, separate from everything below that does.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import update

from app.db.models import BlobRow, ScoringTraceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import traces
from app.platform.blobs import BlobStore
from model_schema import LadderRung, ScoringResult, Trace, TraceStep, new_uuid7

# ----------------------------------------------------------------------------------------
# WK-671 Task 4B — `decide_sampling`, a pure function. No fixtures, no database.
# ----------------------------------------------------------------------------------------


@pytest.mark.req("FR-259")
@pytest.mark.parametrize("rate", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("roll", [0.0, 0.5, 0.999999])
def test_a_decline_is_always_sampled_regardless_of_rate_or_roll(rate: float, roll: float) -> None:
    """FR-259's 100 % floor: a decline is sampled at every rate, including `0.0`, and
    whatever the roll happens to be — the roll is not even inspected."""
    sampled, reason = traces.decide_sampling("declined", rate, roll=roll)
    assert (sampled, reason) == (True, "decline")


@pytest.mark.req("FR-259")
@pytest.mark.parametrize("rate", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("roll", [0.0, 0.5, 0.999999])
def test_an_error_is_always_sampled_regardless_of_rate_or_roll(rate: float, roll: float) -> None:
    sampled, reason = traces.decide_sampling("error", rate, roll=roll)
    assert (sampled, reason) == (True, "error")


@pytest.mark.req("FR-259")
def test_a_quoted_outcome_at_rate_zero_is_never_sampled() -> None:
    """Negative: the boundary at the bottom. `roll` is drawn from `[0.0, 1.0)`, so `roll <
    0.0` never holds — no roll can force a sample at a `0.0` rate."""
    for roll in (0.0, 0.001, 0.5, 0.999999):
        assert traces.decide_sampling("quoted", 0.0, roll=roll) == (False, None)


@pytest.mark.req("FR-259")
def test_a_quoted_outcome_at_rate_one_is_always_sampled() -> None:
    """The boundary at the top: every roll in `[0.0, 1.0)` is `< 1.0`."""
    for roll in (0.0, 0.001, 0.5, 0.999999):
        assert traces.decide_sampling("quoted", 1.0, roll=roll) == (True, "rate")


@pytest.mark.req("FR-259")
def test_a_quoted_outcome_is_sampled_iff_the_roll_is_below_the_rate() -> None:
    assert traces.decide_sampling("quoted", 0.5, roll=0.4) == (True, "rate")
    assert traces.decide_sampling("quoted", 0.5, roll=0.5) == (False, None)
    assert traces.decide_sampling("quoted", 0.5, roll=0.6) == (False, None)


@pytest.mark.req("FR-259")
def test_the_one_percent_default_is_correct_over_a_large_n_with_a_fixed_seed() -> None:
    """The statistical test, not eyeballed: 20 000 draws at `rate=0.01` is a Binomial(n=
    20000, p=0.01), mean 200, standard deviation `sqrt(20000 * 0.01 * 0.99)` ~= 14.07. The
    tolerance below is 6 standard deviations (~85), which a fair implementation fails by
    chance roughly once in a billion runs — fixed seed `1234` makes this exact run
    reproducible regardless, so a real regression is the only thing that can fail it."""
    rng = random.Random(1234)
    n = 20_000
    rate = 0.01
    sampled_count = sum(
        1 for _ in range(n) if traces.decide_sampling("quoted", rate, roll=rng.random())[0]
    )
    mean = n * rate
    std_dev = (n * rate * (1 - rate)) ** 0.5
    tolerance = 6 * std_dev
    assert abs(sampled_count - mean) < tolerance, (
        f"{sampled_count} sampled of {n} at rate {rate}; expected {mean} +/- {tolerance:.1f}"
    )


def _served_scoring_result(**overrides: object) -> ScoringResult:
    body: dict[str, object] = {
        "outcome": "quoted",
        "rating_version_ref": "rating_version:motor-gb@12",
        "bundle_hash": f"sha256:{new_uuid7().hex.ljust(64, '0')[:64]}",
        "premium_ladder": [
            LadderRung(rung="risk_premium", value_minor=10_000),
            LadderRung(rung="payable_premium", value_minor=12_000),
        ],
        "outputs": {"payable_premium_minor": 12_000},
        "decline_reasons": [],
        "trace": None,
        "timing_ms": {"total": 1.5},
    }
    body.update(overrides)
    return ScoringResult(**body)


@pytest.mark.req("FR-259")
def test_summarise_result_carries_only_the_served_answer() -> None:
    """`summarise_result` is the served/reproduced comparison RL-862 condition (b)
    checks — it must carry the four served-answer fields and nothing quote-input-shaped."""
    summary = traces.summarise_result(_served_scoring_result())
    assert set(summary) == {"outcome", "decline_reasons", "premium_ladder", "outputs"}
    assert summary["outcome"] == "quoted"
    assert summary["outputs"] == {"payable_premium_minor": 12_000}


@pytest.mark.req("FR-259")
def test_summarise_result_is_exact_for_two_results_built_the_same_way() -> None:
    """Money stays exact: two results built with identical ladder/outputs values produce
    byte-identical summaries, so `==` is an exact comparison rather than an approximate
    one (RL-862 condition (b))."""
    a = traces.summarise_result(_served_scoring_result())
    b = traces.summarise_result(_served_scoring_result())
    assert a == b


def _trace(*, quote_id: str, rating_version: str, bundle_hash: str) -> Trace:
    """A trace shaped like `03` §4.5's worked example, with distinguishing non-default
    values on every field the row projects — the divergence test needs that."""
    return Trace(
        rating_version_ref=rating_version,
        bundle_hash=bundle_hash,
        quote_id=quote_id,
        ladder_reconciled=True,
        steps=[
            TraceStep(
                step_id="s_area",
                type="lookup",
                label="Rating area from outcode",
                consumed={"postcode_outcode": "SW1A", "as_at": "2026-10-20"},
                produced={"rating_area": "A3"},
                matched={
                    "reference_table": "reference_table:ons-postcode-directory@7",
                    "key": {"postcode_outcode": "SW1A"},
                },
                elapsed_us=41,
            ),
            TraceStep(
                step_id="s_minprem",
                type="constraint",
                label="Minimum premium",
                consumed={"office_premium_minor": 26_400, "min_premium_minor": 28_000},
                produced={"office_premium_minor": 28_000},
                violation={"applied": "clamp", "reason_code": "MIN_PREMIUM_APPLIED"},
                elapsed_us=3,
            ),
        ],
    )


def _bundle_hash() -> str:
    return f"sha256:{new_uuid7().hex.ljust(64, '0')[:64]}"


async def _write(
    database: Database, blob_store: BlobStore, workspace_id, *, trace: Trace, sample_reason="rate"
) -> ScoringTraceRow:
    async with database.unit_of_work() as session:
        row = await traces.write_trace(
            session,
            blob_store,
            trace,
            workspace_id=workspace_id,
            sample_reason=sample_reason,
        )
        row_id = row.id
    async with database.session() as session:
        refetched = await session.get(ScoringTraceRow, row_id)
        assert refetched is not None
        return refetched


@pytest.mark.req("FR-258")
async def test_a_sampled_trace_round_trips(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Persist a `Trace`, read the row back, fetch its body: reconstructs the original."""
    original = _trace(
        quote_id="quote-abc123",
        rating_version="rating_version:motor-gb@27",
        bundle_hash=_bundle_hash(),
    )
    row = await _write(database, blob_store, workspace_id, trace=original)

    async with database.session() as session:
        reconstructed = await traces.read_trace(session, blob_store, row)

    assert reconstructed == original


@pytest.mark.req("FR-259")
async def test_row_and_body_are_written_from_one_serialisation(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The discriminating test: the row's three projected fields equal the values *inside
    the stored body* — a projection assembled separately from the body would pass the
    round-trip test above and fail this one (RL-888)."""
    original = _trace(
        quote_id="quote-divergence-check",
        rating_version="rating_version:motor-gb@41",
        bundle_hash=_bundle_hash(),
    )
    row = await _write(database, blob_store, workspace_id, trace=original)

    async with database.session() as session:
        body = await traces.read_trace(session, blob_store, row)

    assert row.quote_id == body.quote_id == original.quote_id
    assert (
        row.rating_version_ref
        == str(body.rating_version_ref)
        == str(original.rating_version_ref)
    )
    assert row.bundle_hash == body.bundle_hash == original.bundle_hash


@pytest.mark.req("FR-259")
async def test_batch_produced_trace_carries_no_environment(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A trace written on request for a batch Job (FR-258, RL-890) carries no
    `environment` — the signal `GET /api/v1/traces` (Task 4C) excludes it by."""
    original = _trace(
        quote_id="quote-batch",
        rating_version="rating_version:motor-gb@3",
        bundle_hash=_bundle_hash(),
    )
    async with database.unit_of_work() as session:
        row = await traces.write_trace(
            session,
            blob_store,
            original,
            workspace_id=workspace_id,
            sample_reason="rate",
        )
        row_id = row.id

    async with database.session() as session:
        refetched = await session.get(ScoringTraceRow, row_id)
        assert refetched is not None
        assert refetched.environment is None


@pytest.mark.req("NFR-459")
async def test_deleting_a_trace_inside_the_retention_floor_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Negative: NFR-459's >= 13-month floor refuses a delete of a fresh row."""
    row = await _write(
        database,
        blob_store,
        workspace_id,
        trace=_trace(
            quote_id="quote-young",
            rating_version="rating_version:motor-gb@5",
            bundle_hash=_bundle_hash(),
        ),
    )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await traces.delete_trace(session, row.id)
    assert exc.value.code == "TRACE_RETENTION_FLOOR"
    assert exc.value.status_code == 409

    async with database.session() as session:
        assert await session.get(ScoringTraceRow, row.id) is not None


@pytest.mark.req("NFR-459")
async def test_deleting_a_trace_outside_the_retention_floor_is_permitted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The guard has an edge: a row older than the floor may be deleted."""
    row = await _write(
        database,
        blob_store,
        workspace_id,
        trace=_trace(
            quote_id="quote-old",
            rating_version="rating_version:motor-gb@6",
            bundle_hash=_bundle_hash(),
        ),
    )
    async with database.unit_of_work() as session:
        await session.execute(
            update(ScoringTraceRow)
            .where(ScoringTraceRow.id == row.id)
            .values(created_at=datetime.now(UTC) - timedelta(days=400))
        )

    async with database.unit_of_work() as session:
        await traces.delete_trace(session, row.id)

    async with database.session() as session:
        assert await session.get(ScoringTraceRow, row.id) is None
        # The blob reference was released on delete, not left dangling at ref_count > 0.
        blob_row = await session.get(BlobRow, row.blob_sha256)
        assert blob_row is not None
        assert blob_row.ref_count == 0


@pytest.mark.req("NFR-500")
async def test_a_referenced_trace_blob_survives_garbage_collection(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    """RL-888's claim, verified rather than assumed: `write_trace`'s `retain` keeps a
    trace's blob invisible to GC's `ref_count == 0` selector even once it is old."""
    row = await _write(
        database,
        blob_store,
        workspace_id,
        trace=_trace(
            quote_id="quote-gc-check",
            rating_version="rating_version:motor-gb@7",
            bundle_hash=_bundle_hash(),
        ),
    )
    async with database.unit_of_work() as session:
        await session.execute(
            update(BlobRow)
            .where(BlobRow.sha256 == row.blob_sha256)
            .values(created_at=datetime.now(UTC) - timedelta(days=60))
        )

    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id, dry_run=False
        )

    assert row.blob_sha256 not in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, row.blob_sha256) is not None


@pytest.mark.req("NFR-459")
async def test_deleting_an_unknown_trace_is_a_typed_error(database: Database) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await traces.delete_trace(session, new_uuid7())
    assert exc.value.code == "NOT_FOUND"


@pytest.mark.req("FR-259")
async def test_write_requires_a_transaction(database: Database, blob_store: BlobStore) -> None:
    """Negative: mirrors `blobs.put`'s own guard — the row and the blob's accounting must
    commit together."""
    async with database.session() as session:
        with pytest.raises(RuntimeError, match="requires an open transaction"):
            await traces.write_trace(
                session,
                blob_store,
                _trace(
                    quote_id="quote-no-txn",
                    rating_version="rating_version:motor-gb@9",
                    bundle_hash=_bundle_hash(),
                ),
                workspace_id=new_uuid7(),
                sample_reason="rate",
            )


# ------------------------------------------------------------------------------------
# WK-671 Task 4B — the pending row and its off-path completion (RL-862,
# `docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`).
# ------------------------------------------------------------------------------------


async def _write_pending(
    database: Database, workspace_id, *, served_summary: dict | None = None
) -> ScoringTraceRow:
    summary = served_summary or traces.summarise_result(_served_scoring_result())
    async with database.unit_of_work() as session:
        row = await traces.write_pending_trace(
            session,
            workspace_id=workspace_id,
            quote_id="quote-pending",
            rating_version_ref="rating_version:motor-gb@12",
            bundle_hash=_bundle_hash(),
            sample_reason="rate",
            environment="uat",
            quote_context={"purpose": "new_business"},
            served_summary=summary,
        )
        row_id = row.id
    async with database.session() as session:
        refetched = await session.get(ScoringTraceRow, row_id)
        assert refetched is not None
        return refetched


@pytest.mark.req("FR-259")
async def test_write_pending_trace_has_no_body_yet(database: Database, workspace_id) -> None:
    row = await _write_pending(database, workspace_id)
    assert row.status == "pending"
    assert row.blob_sha256 is None
    assert row.pending_quote_context == {"purpose": "new_business"}


@pytest.mark.req("FR-259")
async def test_completing_a_pending_trace_that_reproduces_marks_it_complete(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    summary = traces.summarise_result(_served_scoring_result())
    pending = await _write_pending(database, workspace_id, served_summary=summary)
    reproduced_trace = _trace(
        quote_id="quote-pending",
        rating_version=pending.rating_version_ref,
        bundle_hash=pending.bundle_hash,
    )
    async with database.unit_of_work() as session:
        completed = await traces.complete_pending_trace(
            session, blob_store, pending.id, reproduced_trace, reproduced_summary=summary
        )
    assert completed.id == pending.id
    assert completed.status == "complete"
    assert completed.blob_sha256 is not None
    assert completed.pending_quote_context is None
    assert completed.created_at == pending.created_at

    async with database.session() as session:
        body = await traces.read_trace(session, blob_store, completed)
    assert body == reproduced_trace


@pytest.mark.req("FR-259")
async def test_completing_a_pending_trace_that_does_not_reproduce_keeps_the_body(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """RL-862 §8.2 condition (b): a reproduction that does not match is `mismatch`, and
    the body is still written — recorded as evidence, not discarded."""
    served_summary = traces.summarise_result(_served_scoring_result())
    pending = await _write_pending(database, workspace_id, served_summary=served_summary)
    different_summary = traces.summarise_result(
        _served_scoring_result(outputs={"payable_premium_minor": 99_999})
    )
    reproduced_trace = _trace(
        quote_id="quote-pending",
        rating_version=pending.rating_version_ref,
        bundle_hash=pending.bundle_hash,
    )
    async with database.unit_of_work() as session:
        completed = await traces.complete_pending_trace(
            session,
            blob_store,
            pending.id,
            reproduced_trace,
            reproduced_summary=different_summary,
        )
    assert completed.status == "mismatch"
    assert completed.blob_sha256 is not None


@pytest.mark.req("FR-259")
async def test_completing_a_pending_trace_with_no_reproduction_leaves_no_body(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """RL-862 §8.2 condition (a): the pinned bundle was unresolvable, so no re-score was
    attempted — `trace=None` — and the row still lands `mismatch`, with no body to keep."""
    pending = await _write_pending(database, workspace_id)
    async with database.unit_of_work() as session:
        completed = await traces.complete_pending_trace(
            session, blob_store, pending.id, None, reproduced_summary=None
        )
    assert completed.status == "mismatch"
    assert completed.blob_sha256 is None


@pytest.mark.req("FR-259")
async def test_completing_an_already_completed_trace_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Negative: a re-delivered `score.trace_produce` Job must not silently re-run the
    re-score against an already-settled row."""
    summary = traces.summarise_result(_served_scoring_result())
    pending = await _write_pending(database, workspace_id, served_summary=summary)
    reproduced_trace = _trace(
        quote_id="quote-pending",
        rating_version=pending.rating_version_ref,
        bundle_hash=pending.bundle_hash,
    )
    async with database.unit_of_work() as session:
        await traces.complete_pending_trace(
            session, blob_store, pending.id, reproduced_trace, reproduced_summary=summary
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await traces.complete_pending_trace(
                session, blob_store, pending.id, reproduced_trace, reproduced_summary=summary
            )
    assert exc.value.code == "TRACE_NOT_PENDING"
    assert exc.value.status_code == 409


@pytest.mark.req("NFR-459")
async def test_deleting_a_pending_trace_does_not_try_to_release_a_missing_blob(
    database: Database, workspace_id
) -> None:
    """Negative: a pending row has `blob_sha256 IS NULL`; `delete_trace` must not try to
    release it (`blobs.release` on `None` would be the bug this guards)."""
    pending = await _write_pending(database, workspace_id)
    async with database.unit_of_work() as session:
        await session.execute(
            update(ScoringTraceRow)
            .where(ScoringTraceRow.id == pending.id)
            .values(created_at=datetime.now(UTC) - timedelta(days=400))
        )
    async with database.unit_of_work() as session:
        await traces.delete_trace(session, pending.id)
    async with database.session() as session:
        assert await session.get(ScoringTraceRow, pending.id) is None
