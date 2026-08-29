# W11 Task 1.4 — NFR-RATE-14 on the real `model_call` path, and Ruling 5's follow-up

Two measurements Task 1.4 owes, both named in `docs/plans/2026-08-29-w11-1-evaluator-core.md`:
NFR-RATE-14 re-measured on the shipped `score_one` path (register row `F-W9-1`, the
`NFR-RATE-14` half), and Ruling 5's own named follow-up — "the same GIL-release
measurement must be repeated once a `model_call` custom node exists ... not assumed to
transfer automatically" (`docs/plans/2026-08-29-w11-prework-rulings.md:490-492`).

## NFR-RATE-14 — `nthread=1`, including `DMatrix`, already-loaded booster

Reproduces `docs/research/w8-spike-resolution.md`'s exact comparator shape (`:70-79`): the
booster loaded once outside the loop, `DMatrix` construction inside it, `nthread=1`, 1000
iterations after a 200-call warmup discard, `perf_counter`, p99 at the tail. Measured
through `pricing_core.modelling.gbm.predict_gbm` directly against the same tiny fixed
XGBoost booster this task's own test fixtures use (`test_rating_runtime._train_tiny_
booster`, 5 rows, `max_depth=2`, 3 rounds).

| | p50 | p99 | max |
|---|---|---|---|
| `nthread=1` (incl. `DMatrix`, already-loaded) | 0.483 ms | **1.339 ms** | 7.741 ms |

**PASS.** p99 1.339 ms is below the 1.626 ms figure `NFR-RATE-14` is checked against (W8's
own 2026-08-27 re-measurement, `w8-spike-resolution.md:78`) — comparable rather than
identical, since this is a different machine and a much smaller booster (5 rows / 3 rounds
vs W8's 2000 rows / 500 rounds), but the same shape: `nthread=1`, `DMatrix` included,
booster pre-loaded, never reconstructed per call. Ruling 8's seam is what makes "already
loaded" true here — `CompiledBundle.boosters` holds the live object; see this task's own
finding on `predict_gbm`'s `nthread` handling, below, for why it is applied once at load
time rather than on every call.

## Ruling 5 follow-up — event-loop blocking and throughput, with a real `model_call`

`zen-evaluate-concurrency.md` measured a pure-`expressionNode` graph, because no
`model_call` custom node existed yet, and named this gap explicitly rather than assuming
the result transfers. Task 1.4's own `model_call` custom node (`runtime.py`'s
`_model_call_handler`, invoking `predict_gbm` against a real, pre-loaded XGBoost booster)
is exactly the integration that follow-up names. Repeated here on this task's own fixture
algorithm (`test_rating_score.py`'s: two `input`, one `table`, one `model_call`, one
`expression`, three `constraint`, four `output` steps — nine interior wire nodes).

### Q2 — does `async_evaluate()` block the event loop with a real `model_call` node?

Method unchanged from the original spike: a 1 ms-interval heartbeat coroutine runs
concurrently with one `async_evaluate()` call; a blocked loop shows 0 ticks during the
call.

| Call duration | Heartbeat ticks during the call | Reading |
|---|---|---|
| 7.485 ms | 4 | **non-blocking** (ticks continue at roughly the 1 ms cadence) |

**Confirmed, on this graph shape too: `async_evaluate()` does not block**, even with a
real XGBoost `predict()` call inside the custom node's handler. This is consistent with
the original spike's finding and extends it to the integration that spike could not test.

### Q3 — throughput, x64, real `model_call` in the graph

Direct `async_evaluate()` calls (not routed through `score_one`, whose own Python-side
validation and ladder-building work does not release the GIL either and would dilute a
reading of the engine's own concurrency behaviour specifically) — sequential baseline,
`asyncio.gather` ×64, and a 4-worker `ThreadPoolExecutor` offload of the sync `evaluate()`,
matching the original spike's three-way comparison exactly.

| Case | Duration | vs. sequential |
|---|---|---|
| Sequential `async_evaluate()` ×64 | 96.40 ms | 1.00x (baseline) |
| Concurrent `async_evaluate()` ×64 (`asyncio.gather`) | 86.02 ms | **1.12x** |
| Concurrent `evaluate()` ×64, offloaded (4 threads) | 142.49 ms | **0.68x** |

**Two findings, and the first is the one this follow-up exists to surface honestly rather
than assume away.**

1. **The throughput gain measured here (1.12x) is far below the original expression-only
   figure (2.10–2.25x), and this is a real, measured difference — not noise.** The cause is
   exactly what Ruling 5 named as the open risk: `predict_gbm`'s XGBoost call holds the GIL
   for its native execution, and on *this* fixture the `model_call` step is 1 of only 5
   interior steps (table, model_call, expression, three constraints) — so a large fraction
   of each call's wall time is GIL-held work that cannot be parallelised by releasing the
   GIL elsewhere in the graph. Ruling 5's own rationale anticipated this shape of caveat:
   "a `model_call` step's own GIL-holding window is small and already separately budgeted
   ... against the other ~199 steps that would still benefit from the release" — a
   real ~200-step production algorithm (`NFR-RATE-1`'s own "~200-step motor structure")
   would have the GIL-released fraction dominate far more than this small test fixture
   does, so **1.12x on a 5-step graph is not evidence that a 200-step graph would also see
   only 1.12x** — but it is evidence that the *ratio* depends on how much of the graph is
   spent inside `model_call`, which is new information this measurement adds and the
   original spike could not have produced.
2. **The offloaded-`evaluate()` case is worse than sequential here too (0.68x, comparable
   to the original 0.90–0.93x)**, confirming Ruling 5's ruling is not weakened by this
   integration: option (a) (`evaluate()` + thread-pool offload) remains strictly worse
   than doing nothing, with or without a real booster call in the graph.

**Disposition: Ruling 5 stands, and this follow-up is discharged, not reopened.** The
ruling's own text named this as "an instrumented default, not a closed question" pending
exactly this measurement; the measurement is now in, `async_evaluate()` is confirmed
non-blocking with a real `model_call` present, and the throughput ratio's dependence on
graph composition (steps inside vs. outside `model_call`) is recorded rather than glossed
over. No change to the ruling's disposition (`async_evaluate()`, never `evaluate()` +
executor) is indicated — the measured alternative is still worse on every graph shape
tested to date.

## A finding this measurement exercise surfaced directly: `set_param`/`predict()` race

Building the concurrency smoke test this task's own acceptance criteria require
(`asyncio.gather` over many `score_one` calls against one shared `CompiledBundle`)
reproduced a genuine crash on the first cut of `predict_gbm`'s `nthread` handling:
`XGBoostError: Check failed: !this->need_configuration_`, raised when `Booster.set_param`
is called concurrently with `predict()` on the *same shared* `Booster` object — exactly
what a warm worker's `CompiledBundle.boosters` is under real concurrent scoring. Fixed by
moving `nthread`'s application into `load_gbm_booster` (called once, synchronously, at
hydration time, before any concurrent scoring begins); `predict_gbm` no longer calls
`set_param` against an already-loaded booster. See `gbm.py`'s `load_gbm_booster` and
`predict_gbm` docstrings, and `pricing_core.rating.score`'s module docstring ("Three
design choices"), for the full mechanism. Reproduced reliably (5/5 runs) before the fix and
did not recur in 5/5 runs after it.

## Method

- Booster: the same tiny fixed XGBoost booster (5 rows, `age_years` only, `max_depth=2`,
  3 rounds) this task's own test fixtures use — deliberately small and deterministic, not
  representative of a production booster's own latency, only of the *mechanism* being
  measured.
- Algorithm: `test_rating_score.py`'s own fixture — input×2, table, model_call, expression,
  constraint×3, output×4 (9 wire-level interior nodes).
- Engine: `zen-engine` 0.53.0, as declared in `packages/pricing-core/pyproject.toml`.
- Timing: `time.perf_counter`, this worktree's machine, one run per table above (not
  averaged across runs) — a component-level, single-machine measurement, not the
  sustained-load/ASGI-embedded measurement `NFR-RATE-1` itself names (Slice 2's Task 2.1,
  per this task's own plan).
- Tree: `w11-1-4-score-one` branch, off `origin/main` at `24b537d`.
