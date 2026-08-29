# NFR-RATE-1 (component) and NFR-RATE-2 — W11 Slice 1 Task 1.5, the bare-metal latency harness

Measured 2026-08-29 on this branch's `packages/pricing-core/src/pricing_core/rating/score.py`
(`score_one`), `runtime.py` (`load_bundle`/`CompiledBundle`) and `compile.py`
(`compile_bundle`), on the CI-equivalent `.venv` this worktree built with
`uv sync --all-packages`, using `scripts/bench-rating.py`
(`uv run python scripts/bench-rating.py`). `docs/specs/03-rating-engine.md` §9
(`:784-785`):

- **NFR-RATE-1** (`:784`): "Real-time scoring p99 < 50 ms server-side at 200 rps per
  replica for a ~200-step motor structure with one `exact` GBM call (NFR-OVR-1). Without a
  GBM call, p99 < 15 ms." — this note measures the **component** half only (`score_one`
  called directly, no HTTP, no FastAPI, no database); the sustained-200-rps and
  full-HTTP-path halves are Slice 2's Task 2.1 per this task's own plan
  (`docs/plans/2026-08-29-w11-1-evaluator-core.md`).
- **NFR-RATE-2** (`:785`): "Tracing adds ≤ 20 % to scoring latency and never changes the
  result (R3)."

## Method

- Fixture: a ~200-step motor structure built by `scripts/bench-rating.py` itself (not
  imported from the test suite — see the script's own module docstring): 2 scalar inputs
  (`driver_age`, `channel`) + 8 numeric rating-factor inputs, one `table` lookup, one
  `exact` `model_call` against a real, trained XGBoost booster (8 features, 5,000
  synthetic rows, 300 rounds — sized like Task 1.3's own NFR-RATE-4 "real large" fixture,
  not a toy 3-round one), 186 chained `expression` steps, and one `output` step — **200
  steps** with the GBM call, **199** without it (the model_call step is simply omitted).
- Timing: `time.perf_counter()` around `await score_one(bundle, ctx, trace=...)`, one
  `asyncio` event loop driving a **sequential** await loop — a single-caller latency
  distribution, not a concurrency or throughput measurement (Task 1.4's own
  `docs/research/w11-task-1-4-model-call-concurrency.md` already covers
  `async_evaluate()`'s concurrency behaviour on a smaller graph; deliberately not repeated
  here).
- 200-call warmup discarded, then 1,000 measured calls, matching
  `docs/research/w8-spike-resolution.md`'s own convention (p99 = the 990th sorted value of
  1,000 samples).
- Machine: Intel Xeon @ 2.20GHz, 4 cores, 16.4 GB RAM, 1-minute load average 0.39 at the
  start of the run — a shared development machine, not a dedicated benchmark host
  (`CLAUDE.md` §11's load-contention trap).
- Tree: `w11-1-5-bench-and-ruling28` branch, off `origin/main` at `d6505e9`.

## Result — NFR-RATE-1 (component)

| Metric | Measured | Budget | Margin |
|---|---|---|---|
| With GBM, 200 steps, p99 | 12.537 ms (mean 9.235 ms, max 15.566 ms) | < 50 ms | **~4.0x** |
| Without GBM, 199 steps, p99 | 9.410 ms (mean 6.915 ms, max 12.959 ms) | < 15 ms | **~1.6x** |

**Both halves PASS**, though the without-GBM margin (1.6x) is far tighter than the
with-GBM one (4.0x) — the ~200-step expression chain itself, independent of any model
call, is already 63 % of its own tighter 15 ms budget at the tail. This component
measurement excludes the sustained-200-rps and ASGI-embedded overhead Slice 2's Task 2.1
adds; a full-path p99 sitting closer to either budget at that point would leave much less
headroom than this component number on its own suggests, particularly on the no-GBM path.

## Result — NFR-RATE-2 (trace overhead)

| Metric | Measured | Budget | Verdict |
|---|---|---|---|
| p99, with GBM, 200 steps | 103.227 ms traced vs. 12.537 ms untraced = **+723 %** | ≤ 20 % | **OVER, by ~36x** |
| mean, with GBM, 200 steps (informational) | 75.511 ms traced vs. 9.235 ms untraced = **+718 %** | — | — |

**NFR-RATE-2 fails at this scale, by a wide margin, on both metrics.** This is not a
one-off or a noisy tail: the trace-overhead percentage was measured at four graph sizes
(step counts include the table and model_call steps; rounds=20/rows=200 for the three
smaller runs, a 20-call sample each — the 200-step figure above is the 1,000-call one):

| Steps | Untraced mean | Traced mean | Overhead (mean) |
|---|---|---|---|
| 18 | 2.224 ms | 2.608 ms | +17 % |
| 38 | 2.329 ms | 4.674 ms | +101 % |
| 63 | 3.017 ms | 9.357 ms | +210 % |
| 200 | 9.235 ms | 75.511 ms | +718 % |

The overhead percentage **grows with step count** rather than holding roughly constant —
at 18 steps it sits inside the 20 % budget; by 63 steps it is 10x over; at the ~200-step
scale NFR-RATE-1 itself names, it is ~36x over. The *absolute* per-step overhead
(`(traced − untraced) / steps`) is itself roughly proportional to the step count (≈0.0016
ms × steps² across the three larger points), consistent with a cost that grows
super-linearly in the node count rather than a fixed per-node tax — plausibly because
`to_wire`'s `passThrough: true` (needed for the premium ladder, per this plan's own
"Verified facts") keeps the accumulated context growing at every node, and the traced
response carries a copy of that context **per node**, so the total trace payload grows
faster than linearly in the step count. This is offered as the most likely mechanism, not
a verified one — nothing here profiled the engine's own Rust/PyO3 internals.

**Where the added time is actually spent, measured rather than assumed:** a follow-up
comparison of `score_one`'s own `timing_ms["evaluate"]` (the `await
bundle.decision.async_evaluate(...)` call in isolation) against its total wall time, at
the 200-step scale, 200 calls each:

| | wall mean | `async_evaluate()` mean | `score_one`'s own post-processing (`build_scoring_result`/`_build_trace`) |
|---|---|---|---|
| trace=False | 9.147 ms | 8.800 ms (96 %) | 0.348 ms |
| trace=True | 77.133 ms | 68.476 ms (89 %) | 8.657 ms |

Of the ~68 ms added by tracing, **~60 ms (88 %) is inside `async_evaluate()` itself** —
the third-party `zen-engine` binding's own trace-enabled evaluation — and **~8 ms (12 %)**
is `pricing-core`'s own `_build_trace`/`build_scoring_result` post-processing (which does
its own per-node `dict(entry.get("input") or {})`/`dict(output)` copies over the engine's
returned trace, `score.py:582-583`). Both contribute; the larger share sits on the
third-party side of the FFI boundary, not in code this workstream owns outright, though
`_build_trace`'s own copying is not free either and would be the first thing to revisit if
a partial mitigation were wanted from our own side.

## Reading this, not just the numbers

**This is a genuine NFR-RATE-2 failure at the scale NFR-RATE-1 itself specifies, not a
measurement artifact.** The scaling table above rules out both a fluke (four independent
runs at four sizes, the same direction every time) and a bug specific to this harness (the
same `score_one(bundle, ctx, trace=True)` call a real caller would make; `passThrough` is
baked into the compiled graph by Task 1.3's `to_wire`, not something this script
configures specially). **This measurement does not decide what to do about it** — that is
a design question (sample tracing rather than capture every node's full context, trim what
`_build_trace` copies, revisit whether `passThrough` needs to carry the full context to
every downstream node rather than only what a trace consumer needs, or amend the budget)
outside a measurement task's remit, and is recorded here as a finding for whoever next
triages `docs/audit/register.md` or reviews this slice, not resolved by this note.

**What this measurement does not cover.** No HTTP, no FastAPI, no ASGI, no sustained load,
no concurrency (Slice 2's Task 2.1 and Task 1.4's own concurrency note respectively); one
machine, one run per configuration (not repeated across machines or load conditions); a
synthetic fixture with a real but arbitrarily-sized booster (300 rounds/8 features/5,000
rows) rather than a production model; the without-GBM structure reuses the same 186-step
expression chain rather than an independently-designed no-GBM algorithm. NFR-RATE-1's
sustained-200-rps and full-path halves remain entirely unmeasured here, by design (Slice
2's).

## Scope

This measures NFR-RATE-1's *component* half and NFR-RATE-2, Task 1.5's own assignment in
`docs/plans/2026-08-29-w11-1-evaluator-core.md`'s requirement coverage table. NFR-RATE-3,
7, 8 and 14 are Task 1.4's, already measured and recorded in
`docs/research/w11-task-1-4-model-call-concurrency.md`; NFR-RATE-4 is Task 1.3's,
`docs/research/w11-task-1-3-nfr-rate-4.md`. NFR-RATE-1's sustained-load and full-path
halves are Slice 2's Task 2.1 — not claimed here.
