"""`score_batch` (W11 Task 3A, FR-RATE-36/37, FR-PLAT-9).

Fixture shape: reuses Task 1.4's own fixtures (`_compiled`, `_ctx`) from `test_rating_
score.py` rather than duplicating them — the established convention in this test suite.
Task 3A's own acceptance standard (`docs/plans/2026-08-29-w11-3-batch-scoring.md`, Task
3A Steps 1-5) is exactly four properties: byte-identity with `score_one` through the
shared `build_scoring_result` tail, chunked progress reporting, cooperative cancellation
at a chunk boundary, and purity (no I/O, no state across calls). A fifth test (per-row
error isolation) is added because it is what makes "chunked" safe to call on real data —
FR-RATE-38's structural half, not its threshold policy (3B's) — and Task 3A's own module
docstring states it as an invariant `score_batch` introduces.
"""

from __future__ import annotations

from typing import Any

import polars as pl
import pytest
from test_rating_score import _compiled, _ctx

from model_schema.scoring import QuoteContext
from pricing_core.progress import JobCancelled
from pricing_core.rating.score import _ladder_json, score_batch, score_one


def _ctx_to_row(ctx: QuoteContext) -> dict[str, Any]:
    assert ctx.options is not None
    assert ctx.options.rating_version_ref is not None
    row: dict[str, Any] = {
        "quote_id": ctx.quote_id,
        "purpose": ctx.purpose,
        "effective_date": ctx.effective_date.isoformat(),
        "rating_version_ref": str(ctx.options.rating_version_ref),
    }
    row.update(ctx.inputs)
    return row


def _contexts(n: int) -> list[QuoteContext]:
    ages = [18, 22, 25, 30, 34, 41, 50, 60, 70, 99]
    channels = ["direct", "broker"]
    return [
        _ctx(
            quote_id=f"Q{i}",
            inputs={
                "driver_age": ages[i % len(ages)],
                "channel": channels[i % len(channels)],
                "min_premium_minor": 0,
                "sanity_cap_minor": 999_999_999,
                "sanity_floor_minor": 0,
            },
        )
        for i in range(n)
    ]


class _RecordingProgress:
    def __init__(self) -> None:
        self.updates: list[tuple[float, str, dict[str, int]]] = []

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        self.updates.append((fraction, stage, counters))

    def check_cancelled(self) -> None:
        return None


class _CancelAfter:
    """Signals cancellation once `allowed` chunk boundaries have already passed."""

    def __init__(self, allowed: int) -> None:
        self._allowed = allowed
        self.checks = 0

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        return None

    def check_cancelled(self) -> None:
        self.checks += 1
        if self.checks > self._allowed:
            raise JobCancelled("cancelled for test")


# ---------------------------------------------------------------------------
# FR-RATE-37: byte-identity through the shared `build_scoring_result` tail.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-37")
async def test_score_batch_and_score_one_produce_byte_identical_ladders() -> None:
    compiled = await _compiled()
    contexts = _contexts(6)
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()

    batch_rows = {row["quote_id"]: row for row in score_batch(compiled, frame).collect().to_dicts()}
    assert set(batch_rows) == {c.quote_id for c in contexts}

    for ctx in contexts:
        one_result = await score_one(compiled, ctx)
        batch_row = batch_rows[ctx.quote_id]
        assert batch_row["outcome"] == one_result.outcome
        assert batch_row["rating_version_ref"] == str(ctx.options.rating_version_ref)  # type: ignore[union-attr]
        assert batch_row["bundle_hash"] == one_result.bundle_hash
        assert batch_row["premium_ladder_json"] == _ladder_json(one_result.premium_ladder)
        assert batch_row["decline_reasons"] == one_result.decline_reasons
        assert batch_row["error_code"] is None


# ---------------------------------------------------------------------------
# FR-RATE-37: chunked and progress-reporting.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-37")
async def test_chunk_rows_smaller_than_input_invokes_progress_more_than_once() -> None:
    compiled = await _compiled()
    contexts = _contexts(10)
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()

    progress = _RecordingProgress()
    out = score_batch(compiled, frame, chunk_rows=3, progress=progress).collect()

    assert out.height == 10
    # ceil(10 / 3) == 4 chunk boundaries.
    assert len(progress.updates) == 4
    fractions = [fraction for fraction, _, _ in progress.updates]
    assert fractions == sorted(fractions)
    assert fractions[-1] == pytest.approx(1.0)
    assert progress.updates[-1][2]["rows_scored"] == 10


async def test_chunk_rows_does_not_change_the_row_count_or_the_row_set() -> None:
    compiled = await _compiled()
    contexts = _contexts(7)
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()

    whole = score_batch(compiled, frame, chunk_rows=100).collect()
    chunked = score_batch(compiled, frame, chunk_rows=2).collect()

    assert whole.height == chunked.height == 7
    assert set(whole["quote_id"].to_list()) == set(chunked["quote_id"].to_list())


# ---------------------------------------------------------------------------
# FR-PLAT-9: cooperative cancellation at a chunk boundary.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-9")
async def test_cancellation_stops_before_the_next_chunk_and_scores_nothing_after() -> None:
    compiled = await _compiled()
    contexts = _contexts(9)
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()

    canceller = _CancelAfter(allowed=1)
    with pytest.raises(JobCancelled):
        score_batch(compiled, frame, chunk_rows=3, progress=canceller)

    # One chunk boundary was allowed through (chunk 0 scored), the second raised before
    # chunk 1 started — never fewer than one check, never every chunk's worth.
    assert canceller.checks == 2


@pytest.mark.req("FR-PLAT-9")
async def test_no_cancellation_scores_every_row() -> None:
    compiled = await _compiled()
    contexts = _contexts(5)
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()

    progress = _RecordingProgress()
    out = score_batch(compiled, frame, chunk_rows=2, progress=progress).collect()
    assert out.height == 5


# ---------------------------------------------------------------------------
# Purity: no I/O, no state across calls (the structural override condition, made
# behavioural — `lint-imports` covers the import half).
# ---------------------------------------------------------------------------


async def test_score_batch_is_pure_across_repeated_calls(tmp_path: Any) -> None:
    import os

    compiled = await _compiled()
    contexts = _contexts(8)
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        first = score_batch(compiled, frame, chunk_rows=3).collect()
        second = score_batch(compiled, frame, chunk_rows=3).collect()
    finally:
        os.chdir(cwd)

    assert first.equals(second)
    assert list(tmp_path.iterdir()) == []  # no scratch, no output — nothing written


# ---------------------------------------------------------------------------
# The structural half of FR-RATE-38: one bad row does not abort the chunk it is in, or
# any chunk after it. The threshold policy that decides whether the *run* aborts is 3B's.
# ---------------------------------------------------------------------------


async def test_one_invalid_row_does_not_stop_the_batch() -> None:
    compiled = await _compiled()
    contexts = _contexts(4)
    rows = [_ctx_to_row(c) for c in contexts]
    # Out-of-range, not a type mismatch — a wrong-typed value here would make polars widen
    # the whole `driver_age` column to match, breaking every other row's own validation
    # rather than isolating this one.
    rows[1]["driver_age"] = 150  # INPUT_CONTRACT_VIOLATION: above the declared max (99)
    frame = pl.DataFrame(rows).lazy()

    out = score_batch(compiled, frame).collect().to_dicts()
    by_quote_id = {row["quote_id"]: row for row in out}

    assert len(out) == 4
    assert by_quote_id["Q1"]["outcome"] == "error"
    assert by_quote_id["Q1"]["error_code"] == "INPUT_CONTRACT_VIOLATION"
    assert by_quote_id["Q1"]["premium_ladder_json"] is None
    for quote_id in ("Q0", "Q2", "Q3"):
        assert by_quote_id[quote_id]["outcome"] in ("quoted", "declined")
        assert by_quote_id[quote_id]["error_code"] is None


async def test_chunk_rows_below_one_is_refused() -> None:
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(_ctx())]).lazy()
    with pytest.raises(ValueError, match="chunk_rows"):
        score_batch(compiled, frame, chunk_rows=0)


async def test_empty_frame_scores_nothing_and_calls_no_progress() -> None:
    compiled = await _compiled()
    frame = pl.DataFrame(
        schema={
            "quote_id": pl.Utf8, "purpose": pl.Utf8, "effective_date": pl.Utf8,
            "rating_version_ref": pl.Utf8, "driver_age": pl.Int64, "channel": pl.Utf8,
            "min_premium_minor": pl.Int64, "sanity_cap_minor": pl.Int64,
            "sanity_floor_minor": pl.Int64,
        }
    ).lazy()

    progress = _RecordingProgress()
    out = score_batch(compiled, frame, progress=progress).collect()
    assert out.height == 0
    assert progress.updates == []
