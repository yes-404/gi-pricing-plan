# ZEN evaluate-side concurrency spike — zen-engine 0.53.0

S1 and S2 (`track-a-findings.md`) and their W8 re-verification (`w8-spike-resolution.md`)
tested the **compile side** of `zen-engine` — expression compilation and a bare XGBoost
booster benchmark — and `pricing_core.rating.compile` imports `zen` today only for
`compile_expression` vocabulary checks (`compile.py:244`). No spike in this project has
exercised the **evaluate side**: loading a decision graph and running it, which is what
W11's scorer will do on every real-time quote. Dispatched 2026-08-29 ahead of the W11 plan
freezing, because the answer bears on the evaluator's architecture, not just its estimate.

**The question, in two parts.** (1) Single-call evaluate latency for a graph of roughly
NFR-RATE-1's own reference size — an order-of-magnitude sanity check. (2) Does the binding
block the asyncio event loop during an evaluation, and does concurrent evaluation give real
multi-core throughput or merely interleave on one core? The second is the one that bears on
architecture: if evaluation blocks and offloading it to a thread pool cannot recover
throughput, that is a materially harder problem than blocking alone.

**This is a spike, not the NFR-RATE-1 harness.** It answers the two questions above and is
then thrown away — no code under `packages/` was written or touched. The script and the
JDM-fetch method live in a throwaway job-dir location, not this repository; reproduce by
regenerating the graph shown under "Version and method" below.

## Q1 — single-call latency (sanity check)

| Case | p50 | p99 | max | mean |
|---|---|---|---|---|
| `evaluate()` (sync), run 1 | 2.5404 ms | 7.4815 ms | 10.8410 ms | 2.8862 ms |
| `evaluate()` (sync), run 2 | 2.4948 ms | 11.0121 ms | 14.0512 ms | 2.8629 ms |
| `async_evaluate()`, run 1 | 2.3960 ms | 7.2676 ms | 8.2870 ms | 2.6419 ms |
| `async_evaluate()`, run 2 | 2.3180 ms | 3.3508 ms | 4.3884 ms | 2.3912 ms |

500 iterations per row (20 discarded as warmup), on a 200-step chain — comfortably inside
NFR-RATE-1's 50 ms budget on an order-of-magnitude basis, consistent with S1/S2. This is a
sanity check, not new information about the budget.

## Q2 — does evaluate block the event loop?

Method: a 1 ms heartbeat coroutine runs concurrently with one evaluate call; a blocked
event loop shows **0 ticks** during the call (the loop cannot run anything else), a
genuinely non-blocking call shows ticks continuing at roughly the heartbeat's own cadence.

| Case | Call duration | Heartbeat ticks during the call | Reading |
|---|---|---|---|
| `evaluate()` (sync), run 1 | 2.886 ms | 0 | blocks |
| `evaluate()` (sync), run 2 | 2.833 ms | 0 | blocks |
| `async_evaluate()`, run 1 | 2.684 ms | 3 | does not block |
| `async_evaluate()`, run 2 | 2.793 ms | 3 | does not block |

The binding ships a genuine async API — `ZenEngine.async_evaluate` /
`ZenDecision.async_evaluate`, both `Awaitable[EvaluateResponse]` per the installed `.pyi`
stub — not previously known to this project (nothing before this spike called it, and it
is absent from S1/S2 and from `pricing_core.rating.compile`'s own usage). It behaves as
advertised: the heartbeat ticks at roughly the expected 1 ms cadence throughout the call,
where the sync call produces none.

## Q3 — concurrent throughput: real parallelism, or just interleaving?

Non-blocking and *parallel* are different claims. Interleaving alone cannot reduce total
wall-clock time for CPU-bound work — only genuine multi-core execution can. K = 64 calls,
compared three ways:

| Case | Total (run 1) | Total (run 2) | Speedup vs sequential |
|---|---|---|---|
| Sequential `evaluate()` ×64 | 167.72 ms | 186.30 ms | 1.00x (baseline) |
| Concurrent `async_evaluate()` ×64 (`asyncio.gather`) | 74.53 ms | 88.66 ms | **2.25x / 2.10x** |
| Concurrent `evaluate()` ×64, offloaded to a 4-worker `ThreadPoolExecutor` | 185.90 ms | 199.99 ms | **0.90x / 0.93x** |

Machine has 4 logical CPUs; an ideal thread-pool offload would approach 4x.

**The result most worth naming plainly: thread-pool offload of the sync call is *worse*
than sequential, not merely unhelpful.** It correctly moves the blocking call off the event
loop thread, but buys no throughput — consistent with the native call holding the GIL for
its full duration, so extra OS threads add scheduling overhead against a single
effectively-serialised resource. `async_evaluate()`, by contrast, shows real multi-core
throughput: 2.10–2.25x on 4 cores, reproduced across both runs.

**The 2.1–2.25x is the other half of this finding, and it is not 4x.** Something is not
fully parallel — Python-side coroutine scheduling overhead, a bounded Rust-side thread or
tokio-runtime pool, or a fixed per-call cost that does not parallelise are all consistent
with this data and none is distinguished by it. This is flagged as an **open question for
slice 1's own latency harness**, not smoothed into "real parallelism, case closed."

## What this spike does not cover

- **No `model_call` step was tested.** GBM invocation inside a decision graph is a "custom
  node" ADR-0004 describes but which does not exist in `pricing-core` yet — there is
  nothing to build one against. The GIL-release finding above is proven for pure
  `expressionNode` evaluation and only **suggested**, not measured, for a graph that also
  invokes XGBoost mid-evaluation. NFR-RATE-14's `nthread=1` is XGBoost's own internal
  thread pool, a nested and separate mechanism from whatever `async_evaluate()` does — this
  spike says nothing directly about how the two interact once `model_call` is wired in.
- **The graph is a synthetic 200-step sequential expression chain**, each step reading the
  previous step's output (chosen to mirror a premium ladder's shape, and to match
  NFR-RATE-1's stated step count) — not a faithful motor rating structure. No lookup,
  decision-table, constraint or `model_call` steps are present.
- **No sustained load.** 64 concurrent calls once is not 200 rps sustained per replica. A
  laptop-class shared box at loadavg ~1 is not a replica under production traffic.
- **No memory or GC behaviour under sustained concurrency**, no real uvicorn/ASGI worker
  interaction — this spike runs under a bare `asyncio.run`, not inside FastAPI.
- **Two runs, not a benchmark suite.** They agree in direction and rough magnitude; neither
  is a number to cite as a budget figure without re-measuring in a quiet window, per this
  repository's own standing caution about shared-machine measurements.

## Reading — what the measurement forces, what it merely suggests

**Forced (measured, not inferred, reproduced across two runs):**

- Calling sync `evaluate()` directly inside an async request handler stalls every other
  in-flight coroutine on that worker for the call's duration.
- Offloading that same sync call to a thread pool fixes the blocking but buys **no**
  throughput — 0.90–0.93x, i.e. marginally worse than doing nothing.
- `async_evaluate()` avoids both problems on the graph shape tested: it does not block, and
  concurrent calls achieve real multi-core throughput (2.10–2.25x on 4 cores).

**Suggested, not proven:**

- That the same release-during-native-work behaviour continues once a `model_call` step is
  present. Untested — see scope limits above.
- That an evaluator built directly on `async_evaluate()` would avoid the thread-pool /
  `nthread=1` interaction this spike was dispatched to check for. The data is consistent
  with that reading; it is an architectural conclusion, not a measured fact, and this
  document does not make it.

**Not decided here, and not this document's place to decide:** which construction
`score_one`'s real-time path actually uses. The choice this evidence bears on is
`async_evaluate()` built in from the start, versus `evaluate()` plus executor offload
(non-blocking but throughput-neutral-to-negative, and a second thread-pool layer to reason
about against NFR-RATE-14). That ruling belongs to the decision-maker.

## An observation, not a ruling

`pricing_core.rating.compile.compile_bundle` is `async def` in code (`compile.py:387`)
while `03-rating-engine.md` §5.2 declares it synchronous — PR #315 ruled the code right and
the spec's declared signature wrong, and put the correction in slice 1. If `score_one`
needs to be `async def` to call `async_evaluate()` directly, that would be a **second**
instance of the same shape: §5.2's convention of declaring `pricing-core` functions
synchronous is what keeps turning out to be wrong for a function that has a genuine reason
to be async (I/O-bound artifact resolution in `compile_bundle`'s case; a native async
binding in `score_one`'s prospective case). Worth the decision-maker weighing as a pattern
rather than a second unrelated correction — not ruled here.

## Version and method

- Engine: `zen-engine` 0.53.0, via the project's own `uv`-managed venv (Python 3.12) — the
  version already resolved as a `pricing-core` dependency, not a separately fetched wheel.
  Confirmed against the same version W8 re-verified.
- Graph: a synthetic chain of 200 `expressionNode`s plus one `inputNode` and one
  `outputNode` (202 nodes total), each step's expression reading the immediately preceding
  step's output (`v{i} = v{i-1} * 1.001 + 1`, seeded from an input field). Built directly
  against the engine's real JDM wire format, verified from `gorules/zen`'s own
  `test-data/expression.json` fixture — **not** through `pricing_core.rating.compile.to_jdm`,
  which produces an intermediate shape for pricing-core's own use and is not what the
  engine's Python binding actually consumes; that further translation does not exist yet.
  Correctness spot-check: hand-computed expected value at 200 steps matched the engine's
  result exactly on both runs (1442.561411).
- Machine: 4 logical CPUs, shared with other concurrent sessions on this repository.
  loadavg (1 min) 1.01 → 1.01 across run 1, 0.67 → 0.70 across run 2 — lightly loaded but
  not exclusive.
- Timing: `time.perf_counter`, UTC timestamps throughout (`datetime.now(UTC)`). Run 1:
  2026-08-29T11:27:21Z–11:27:25Z. Run 2: 2026-08-29T11:27:54Z–11:27:57Z.
- Concurrency measurement: a 1 ms-interval heartbeat coroutine (Q2) and `asyncio.gather`
  over K = 64 calls, both native (`async_evaluate`) and thread-offloaded
  (`concurrent.futures.ThreadPoolExecutor`, 4 workers) (Q3).
- Tree: the `research/zen-evaluate-concurrency` branch off `origin/main` at `3b66ede`.
