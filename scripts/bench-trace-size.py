#!/usr/bin/env python3
"""NFR-RATE-12 — trace storage capacity projection (W11 Task 4D).

`docs/specs/03-rating-engine.md` §9 (`:906`): *"Trace storage: 1 % sampling of 50 M annual
quotes stays under 200 GB/year with the sampled-trace schema."* This is a **projection**,
not a direct measurement: nobody scores 50 M real quotes to observe a year of storage. What
is measured directly is the actual serialised byte size of a real `Trace`, produced by
`score_one(..., trace=True)` — the exact same call `app.platform.traces.write_trace`
serialises with `trace.model_dump_json().encode()` (`backend/src/app/platform/traces.py`)
— and that measured size is then multiplied out against the requirement's stated volume.
Saying which of the two this is, is itself part of Task 4D's deliverable
(`docs/plans/2026-08-29-w11-4-trace-sampling-persistence.md` Task 4D).

**No database, no blob store, no compose stack.** `BlobStore.put`
(`backend/src/app/platform/blobs.py:130`) writes the given bytes to S3/MinIO verbatim — no
compression, no re-encoding — so the on-disk blob size is exactly `len(payload)` for
`payload = trace.model_dump_json().encode()`. Measuring that serialisation directly is
therefore measuring what `write_trace` would persist, without needing Postgres or MinIO up
to prove it. (The row itself is separately bounded below; it is negligible next to the
blob and is not run through real Postgres for the same reason.)

**Fixtures are reused from `bench-rating.py` via `importlib`**, not rebuilt here — that
script's `_algorithm_payload`/`_FakeResolver`/`_compiled`/`_ctx` already build a real
compiled `RatingAlgorithm` and a real `QuoteContext`; duplicating ~150 lines of fixture
code to build a second, slightly-different motor structure would make this note's "which
structure was scored" claim harder to verify, not easier. `score_one` itself is untouched;
this script only varies the step count fed to the existing builder and calls the existing
function with `trace=True`.

    uv run python scripts/bench-trace-size.py

Not a CI gate — Ruling 6's governance (`docs/plans/2026-08-29-w11-slice1-rulings.md`),
inherited via `bench-rating.py`/`bench-score-batch.py`: a number for a workstream closure
record, read once against the budget by a human.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
_PACKAGES = _SCRIPTS.parent / "packages"
sys.path.insert(0, str(_PACKAGES / "pricing-core" / "src"))
sys.path.insert(0, str(_PACKAGES / "model-schema" / "src"))

_spec = importlib.util.spec_from_file_location("_bench_rating", _SCRIPTS / "bench-rating.py")
assert _spec is not None and _spec.loader is not None
_bench_rating = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _bench_rating  # dataclasses needs the module in sys.modules
_spec.loader.exec_module(_bench_rating)

from pricing_core.rating.score import score_one  # noqa: E402

#: NFR-RATE-12's own volume: "1 % sampling of 50 M annual quotes".
ANNUAL_QUOTES = 50_000_000
SAMPLE_RATE = 0.01
BUDGET_BYTES_PER_YEAR = 200 * 1_000_000_000  # "200 GB/year" read as decimal GB (1e9 bytes)

#: Step counts swept, in addition to `bench-rating.py`'s own `N_EXPR_STEPS` (187) — the
#: "~200-step motor structure" NFR-RATE-1 itself references, included so the projection's
#: headline figure is read off the same reference structure the latency budget uses, not
#: an arbitrary one. `with_gbm=True` throughout: every swept structure includes the one
#: `model_call` step so trace size at the reference point reflects a real motor pipeline,
#: not a GBM-free simplification.
N_EXPR_VALUES = [5, 20, 50, 100, _bench_rating.N_EXPR_STEPS]

#: Kept small — booster complexity does not change trace step *size* (a `model_call`
#: step's `produced` is one `risk_premium_minor` value regardless of tree count/rows), so
#: a large realistic booster (`bench-rating.py`'s own default: 5,000 rows / 300 rounds)
#: would only slow this script down for no effect on the number being measured.
TRAIN_ROWS = 300
TRAIN_ROUNDS = 20


def machine() -> str:
    return _bench_rating.machine()


async def _trace_bytes_for(n_expr: int) -> tuple[int, int]:
    """Returns `(step_count, serialised_byte_size)` for one scored quote at `n_expr`
    expression steps, GBM included. `payload` below is copied verbatim from
    `app.platform.traces.write_trace`'s own serialisation line, not reimplemented."""
    bundle = await _bench_rating._compiled(
        with_gbm=True, n_expr=n_expr, rounds=TRAIN_ROUNDS, rows=TRAIN_ROWS
    )
    ctx = _bench_rating._ctx()
    result = await score_one(bundle, ctx, trace=True)
    assert result.trace is not None, "trace=True must populate ScoringResult.trace"
    payload = result.trace.model_dump_json().encode()
    return len(result.trace.steps), len(payload)


def _row_bytes_upper_bound() -> int:
    """A conservative fixed-width upper bound on `ScoringTraceRow`'s own text columns
    (`backend/src/app/db/models.py:2033`), for a `complete` row where both JSONB columns
    are `None` — the only shape `write_trace` (the real-time/on-request producer this
    projection is about) ever writes. UUIDs at 16 bytes each; `String(n)` columns bounded
    by their declared `n` in UTF-8 (every value observed is ASCII, so 1 byte/char is not
    an underestimate). This is a bound, not a measurement — reported so the row's
    contribution can be seen to be negligible next to the blob, not asserted to be zero.
    """
    return (
        16  # id
        + 16  # workspace_id
        + 128  # quote_id
        + 100  # rating_version_ref
        + 71  # bundle_hash
        + 16  # sample_reason
        + 32  # environment
        + 64  # blob_sha256
        + 16  # status
    )


async def main() -> int:
    print(machine())
    print(f"\nSweeping step counts {N_EXPR_VALUES} (all with_gbm=True), 1 scored quote each.")
    print(
        f"Booster fixture: {TRAIN_ROWS} rows / {TRAIN_ROUNDS} rounds (trace step size is "
        "unaffected by booster complexity, see module docstring)."
    )

    rows: list[dict[str, Any]] = []
    for n_expr in N_EXPR_VALUES:
        step_count, size = await _trace_bytes_for(n_expr)
        bytes_per_step = size / step_count
        rows.append(
            {"n_expr": n_expr, "step_count": step_count, "bytes": size,
             "bytes_per_step": bytes_per_step}
        )
        print(
            f"  n_expr={n_expr:>4}  steps={step_count:>4}  bytes={size:>8,}  "
            f"({bytes_per_step:6.1f} bytes/step)"
        )

    # The reference point: bench-rating.py's own ~200-step motor structure, the same
    # structure NFR-RATE-1/2 are measured against.
    reference = next(r for r in rows if r["n_expr"] == _bench_rating.N_EXPR_STEPS)
    ref_bytes = reference["bytes"]
    ref_steps = reference["step_count"]

    print(
        f"\nReference structure (NFR-RATE-1's own '~200-step motor structure', "
        f"with_gbm=True): {ref_steps} steps, {ref_bytes:,} bytes for one serialised "
        "Trace (one scored quote, single sample)."
    )

    sampled_quotes = int(ANNUAL_QUOTES * SAMPLE_RATE)
    projected_bytes = sampled_quotes * ref_bytes
    projected_gb = projected_bytes / 1_000_000_000
    budget_gb = BUDGET_BYTES_PER_YEAR / 1_000_000_000
    verdict = "PASS" if projected_bytes <= BUDGET_BYTES_PER_YEAR else "OVER"

    row_bound = _row_bytes_upper_bound()
    row_projected_gb = sampled_quotes * row_bound / 1_000_000_000

    print(
        "\nProjection — quotes only (Ruling 25: batch contributes nothing to this "
        "stream), no dedup benefit assumed (Ruling 23):"
    )
    print(f"  sampled quotes/year = {SAMPLE_RATE:.0%} of {ANNUAL_QUOTES:,} = {sampled_quotes:,}")
    print(f"  blob bytes/year     = {sampled_quotes:,} x {ref_bytes:,} = {projected_bytes:,} "
          f"({projected_gb:,.2f} GB)")
    print(f"  row bytes/year (upper bound) = {sampled_quotes:,} x {row_bound} = "
          f"{row_projected_gb:,.4f} GB")
    print(f"  budget (NFR-RATE-12) = {budget_gb:,.0f} GB/year")
    print(f"  VERDICT = {verdict} — {projected_gb / budget_gb:.3f}x budget "
          f"(blob only; row upper bound adds {row_projected_gb / budget_gb:.5f}x)")

    print(
        "\nNot included: FR-RATE-42's 100% decline/error sampling floor (this projection "
        "reads NFR-RATE-12's own text literally — '1% sampling of 50M annual quotes' — "
        "and does not add a decline/error rate assumption the requirement does not "
        "state); the request-side always-capture-then-discard cost (Ruling 35 moved "
        "capture off the serving request, so it is a worker cost, not a storage one); "
        "compression at the storage layer (none exists — BlobStore.put stores bytes "
        "verbatim); any multi-run statistical variance (n=1 per step count, see the note)."
    )
    print(json.dumps({"rows": rows, "reference": reference, "sampled_quotes": sampled_quotes,
                       "projected_bytes": projected_bytes, "verdict": verdict}, indent=2))
    return 0


if __name__ == "__main__":
    import asyncio

    sys.exit(asyncio.run(main()))
