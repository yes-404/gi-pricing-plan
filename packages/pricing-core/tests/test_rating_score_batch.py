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

import copy
import json
from decimal import Decimal
from typing import Any

import polars as pl
import pytest
from test_rating_runtime import _gbm_model_payload, _rate_table_payload, _train_tiny_booster
from test_rating_score import _algorithm_payload, _compiled, _ctx, _version

from model_schema.refs import ArtifactRef
from model_schema.scoring import QuoteContext, ScoringResult
from pricing_core.progress import JobCancelled
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import (
    _BATCH_OUTPUT_SCHEMA,
    _SCORING_RESULT_BATCH_EXCLUDED_FIELDS,
    _SCORING_RESULT_TO_BATCH_COLUMN,
    _ladder_json,
    score_batch,
    score_one,
)


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


def _decimal_output_algorithm_payload() -> dict[str, Any]:
    """Task 1.4's own fixture (`_algorithm_payload`), plus one non-money `decimal` output —
    the ladder and every existing assertion are untouched, since `driver_age * 1.5` neither
    matches a ladder rung name nor consumes anything the ladder does (module docstring's
    "Ladder construction" note: only an `output` step named `f"{rung}_minor"` is a rung, and
    `_build_outputs` reads every declared output independently of the ladder). Exists to
    prove `_outputs_json` handles a genuine `Decimal`-typed output (Ruling 43 §5(i)) —
    nothing in Task 1.4's own fixture declares one, `03` FR-RATE-13's *"decimal or
    money_minor"* being the only two monetary result types and `payable_premium_minor`
    already covering the second."""
    payload = copy.deepcopy(_algorithm_payload())
    payload["outputs"].append({"name": "age_factor", "type": "decimal", "required": False})
    payload["steps"].append(
        {
            "step_id": "s_age_factor", "type": "expression", "label": "Age factor (decimal)",
            "expr": "driver_age * 1.5", "result_type": "decimal",
            "consumes": ["driver_age"], "produces": "age_factor_raw",
        }
    )
    payload["steps"].append(
        {
            "step_id": "s_out_age_factor", "type": "output", "label": "Age factor output",
            "output_name": "age_factor", "rounding": {"mode": "half_even", "dp": 2},
            "consumes": ["age_factor_raw"],
        }
    )
    return payload


class _DecimalOutputResolver:
    """Mirrors `test_rating_score._FakeResolver` (GBM-only), swapping in the augmented
    algorithm payload above — not a subclass, since `_FakeResolver` builds its payload
    internally and gives no seam to inject a different one."""

    def __init__(self) -> None:
        booster = _train_tiny_booster()
        self._payloads: dict[str, dict[str, Any]] = {
            "rating_algorithm:score-fixture@1": _decimal_output_algorithm_payload(),
            "rate_table:motor-expense@1": _rate_table_payload(),
            "model:motor-freq@1": _gbm_model_payload(booster),
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


async def _compiled_with_decimal_output() -> CompiledBundle:
    resolver: ArtifactResolver = _DecimalOutputResolver()
    bundle = await compile_bundle(_version(), resolver)
    return load_bundle(bundle)


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
    # `_compiled_with_decimal_output` (Task 1.4's fixture plus one non-money `decimal`
    # output — see its own docstring) so this test also covers Ruling 43 §5(i): a
    # money-minor output and a genuinely `Decimal`-typed one must both round-trip through
    # `outputs_json` losslessly, which the plain fixture cannot exercise on its own since
    # its only declared output is `payable_premium_minor` (money-minor).
    compiled = await _compiled_with_decimal_output()
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

        # Ruling 43 §5(i): `outputs_json` was asserted nowhere before this. Both output
        # types this fixture declares are checked, not just that the column is non-null.
        assert one_result.outcome == "quoted", "a decline skips the outputs this asserts"
        outputs = json.loads(batch_row["outputs_json"])
        assert set(outputs) == {"payable_premium_minor", "age_factor"}

        money = outputs["payable_premium_minor"]
        assert isinstance(money, int)
        assert not isinstance(money, bool)
        assert money == one_result.outputs["payable_premium_minor"]

        decimal_value = outputs["age_factor"]
        # A Decimal output must be a JSON string, never a number.
        assert isinstance(decimal_value, str)
        driver_age = ctx.inputs["driver_age"]
        assert Decimal(decimal_value) == Decimal(repr(driver_age)) * Decimal("1.5")


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


# ---------------------------------------------------------------------------
# Ruling 43 §4: the drift guard. `CLAUDE.md` §2's "a shape defined twice will diverge"
# only holds if something notices when it does — a field added to `ScoringResult` with no
# batch column and no exclusion must fail the build, not be silently dropped.
# ---------------------------------------------------------------------------


def _assert_scoring_result_covered() -> None:
    fields = set(ScoringResult.model_fields)
    covered = set(_SCORING_RESULT_TO_BATCH_COLUMN) | _SCORING_RESULT_BATCH_EXCLUDED_FIELDS

    missing = fields - covered
    assert not missing, (
        f"ScoringResult field(s) {sorted(missing)} have no batch output column and are not "
        "on the named exclusion list — 03 §4.8 and score.py's "
        "_SCORING_RESULT_TO_BATCH_COLUMN/_SCORING_RESULT_BATCH_EXCLUDED_FIELDS have diverged "
        "from model_schema.scoring.ScoringResult"
    )
    stale = covered - fields
    assert not stale, (
        f"mapping/exclusion names field(s) {sorted(stale)} ScoringResult no longer has"
    )


def test_every_scoring_result_field_is_a_batch_column_or_a_named_exclusion() -> None:
    _assert_scoring_result_covered()
    # The mapping's targets must themselves be real batch columns, not just plausible names.
    assert set(_SCORING_RESULT_TO_BATCH_COLUMN.values()) <= set(_BATCH_OUTPUT_SCHEMA.names())


def test_the_drift_guard_fails_when_scoring_result_gains_an_unmapped_field() -> None:
    """`CLAUDE.md` §13: 'enforcement is proven on deliberately broken input.' A field the
    mapping and the exclusion list do not know about is added to `ScoringResult.model_
    fields` for the duration of this test only (restored in `finally`, verified restored
    below) — the exact shape a real new field on the model would take — and the guard
    above is shown to fail on it, not merely to exist."""
    original = dict(ScoringResult.model_fields)
    assert "a_field_the_mapping_does_not_know" not in original
    try:
        ScoringResult.model_fields["a_field_the_mapping_does_not_know"] = original["outcome"]
        with pytest.raises(AssertionError, match="a_field_the_mapping_does_not_know"):
            _assert_scoring_result_covered()
    finally:
        ScoringResult.model_fields.clear()
        ScoringResult.model_fields.update(original)
    assert "a_field_the_mapping_does_not_know" not in ScoringResult.model_fields
    _assert_scoring_result_covered()  # restored cleanly — the guard passes again
