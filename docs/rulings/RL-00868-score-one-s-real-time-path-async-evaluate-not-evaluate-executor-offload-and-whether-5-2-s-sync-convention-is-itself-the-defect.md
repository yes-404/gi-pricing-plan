---
id: RL-868
family: ruling
title: `score_one`'s real-time path: `async_evaluate()`, not `evaluate()` + executor offload; and whether §5.2's sync convention is itself the defect
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-prework-rulings.md
---

## RL-868 — `score_one`'s real-time path: `async_evaluate()`, not `evaluate()` + executor offload; and whether §5.2's sync convention is itself the defect

**The finding, precisely, and its evidence.** `docs/research/zen-evaluate-concurrency.md`
(filed #321, executor's spike, dispatched ahead of the WK-671 plan freezing, explicitly
declining to rule) measured the ZEN engine's evaluate side for the first time in this
project — S1/S2 and their WK-668 re-verification only ever tested the compile side. Two
questions, both measured twice on the same machine:

- **Does `evaluate()` block the asyncio event loop?** Yes, completely: a 1 ms heartbeat
  coroutine got **0 ticks** during a 2.8–2.9 ms sync `evaluate()` call, both runs.
  `async_evaluate()` — a real binding the project did not previously know existed
  (`zen-evaluate-concurrency.md:49-54`, `ZenEngine.async_evaluate` /
  `ZenDecision.async_evaluate`, `Awaitable[EvaluateResponse]` per the installed `.pyi`
  stub) — does not block: 3 ticks at the expected cadence, both runs.
- **Does offloading the sync call to a thread pool recover throughput?** No — it is
  **worse than doing nothing**: sequential `evaluate()` ×64 as the 1.00x baseline,
  4-worker-thread-pool-offloaded `evaluate()` ×64 measured at **0.90–0.93x**, both runs,
  consistent with the GIL held for the full native call so extra OS threads add pure
  scheduling overhead against an effectively single-threaded resource. `async_evaluate()`
  ×64 via `asyncio.gather` measured **2.10–2.25x**, both runs — real multi-core throughput,
  not merely non-blocking.

**Options, as dispatched:** (a) build `score_one`'s real-time path on `evaluate()` plus
`run_in_executor` thread-pool offload; (b) build it directly on `async_evaluate()`.

**Ruled: (b).** `async_evaluate()` dominates on every axis this spike measured — it does
not block, and it is the only one of the two that delivers any throughput gain at all.
Option (a) is not a safer, slower alternative to (b); it is strictly worse than doing
nothing, on data reproduced twice.

Rationale:

- **No axis favours (a).** Non-blocking: both achieve it, one (offload) by construction and
  the other (native) as measured. Throughput: (a) is 0.90–0.93x, (b) is 2.10–2.25x. There is
  no dimension along which paying for a second thread-pool layer — one that then has to be
  reasoned about against `NFR-501`'s own `nthread=1` GBM thread-pool discipline — buys
  anything back.
- **This is the correct scope, and I am not extending it past what was measured.** The
  ruling is for `score_one`'s real-time path specifically, called from a live FastAPI
  request handler sharing an event loop with other in-flight quotes — exactly the context
  `NFR-489`'s 200 rps/replica target describes and exactly the context blocking would
  hurt. `score_batch` (batch, Job-driven, no shared event loop with concurrent requests to
  protect) is **not** ruled here and its own `def` signature (`03-rating-engine.md:600`) is
  untouched — a batch worker may still benefit from `async_evaluate()`'s internal
  concurrency for its own chunk-level throughput, but that is an implementation choice
  inside a function whose public signature does not need to change, not a repeat of this
  ruling.
- **What the spike does not cover, weighed rather than ignored.** No `model_call` step
  exists to test — the GIL-release finding is proven for pure `expressionNode` evaluation
  and only *suggested* for a graph that also invokes XGBoost mid-evaluation via the
  ADR-706 custom-node mechanism, which is unbuilt. `NFR-501`'s `nthread=1` governs
  XGBoost's own nested thread pool — a different, separate mechanism from whatever
  `async_evaluate()` releases around it — and this spike says nothing directly about how
  the two interact once wired together. The 2.10–2.25x on 4 cores is also not the ideal 4x,
  and the spike names the gap as open rather than closing it. **None of this changes the
  ruling for the graph shape actually measured**, because a `model_call` step's own
  GIL-holding window is small and already separately budgeted (S2/WK-668: p99 ~1.09–1.626 ms
  for the booster call itself) against the other ~199 steps that would still benefit from
  the release — but it does mean this is ruled as an **instrumented default, not a closed
  question**: **the same GIL-release measurement must be repeated once a `model_call`
  custom node exists**, named explicitly as a slice prerequisite for whichever slice builds
  that integration, not assumed to transfer automatically.
- **No sustained-load or ASGI-embedded measurement exists yet either** (`zen-evaluate-
  concurrency.md`'s own scope limits: a bare `asyncio.run`, not inside FastAPI; 64 concurrent
  calls once, not 200 rps sustained). `NFR-489`'s own sustained-load test is already a
  named Phase 2 item (`docs/roadmap.md:146`); this ruling does not substitute for it, and
  the latency harness the roadmap's own risk row already calls for building "alongside the
  evaluator, not after" is where that measurement belongs.

**Disposition.** Spec fix, made in this commit: `03-rating-engine.md:598`'s
`score_one` signature becomes `async def score_one(...)`. No other §5.2 signature in this
block changes — `score_batch`, `dislocate`, `attribute`, `run_regression` and
`generate_contexts` all run in Job/worker contexts without a shared-event-loop concern, and
none of them is shown by this spike to need a different declared shape. **Code, WK-671 slice
1**: the evaluator built on `pricing_core.rating.score.score_one` calls
`CompiledBundle`'s loaded engine handle's `async_evaluate()`, not `evaluate()` plus an
executor. **Follow-up, named and owned by whichever slice builds `model_call`'s ADR-706
custom-node integration**: repeat Q2/Q3 of `zen-evaluate-concurrency.md` on a graph that
actually invokes a booster mid-evaluation, before trusting this ruling's GIL-release
reasoning under real load with a real GBM call in the path.

**The larger question: is §5.2's sync-by-default convention itself the defect?** No — the
convention (declare a `pricing-core` function synchronous unless something specific forces
otherwise) is a reasonable prior for a spec written before any implementation existed to
check it against, and it is right for the overwhelming majority of `pricing-core`'s own
interface: `validate_algorithm`, `to_jdm`, `bundle_hash`, `to_minor`, `apply_factor`, every
`rate_tables/operations.py` function, `score_batch`, `dislocate`, `attribute`,
`run_regression`, `generate_contexts` — none of these await anything, and sync is correct
for every one of them. What is actually defective is narrower and more precise than "the
convention": **two signatures were declared sync without checking what they actually call,
and both turned out to call something that only works correctly from an `async def`** — a
genuinely async-native binding in `score_one`'s case (`async_evaluate()`, this ruling), and
a resolver doing real async I/O in `compile_bundle`'s case (RL-866). Both are the same
underlying failure: *a spec signature declared before the thing it wraps was known to have
an async-only correct calling convention.* That is not a defect in "declare things sync by
default" as a prior — it is a gap in the **verification step**, which nothing forced before
either fact was known (zen-engine's async API was undiscovered until this spike;
`compile_bundle`'s resolver-await need was invisible until the backend actually wired a real
SQLAlchemy session into it). **Ruled: one dated rule added to `.claude/skills/spec-change`
now** (this commit), rather than treating this as a recurring correction that will keep
firing silently: a `pricing-core` interface signature is declared `async def` exactly when
it directly awaits an injected async dependency or a native async binding from a caller
context that is itself async, and is declared plain `def` otherwise — and that fact is
checked against what the function actually calls (or, pre-implementation, against a spike
of the library it wraps) before the signature is written down, not defaulted and trusted.
This is not a rewrite of §5.2's other signatures — none of the other nine are shown wrong by
anything measured — it is the rule that stops a third instance from needing its own PR to
notice.

## Verification

`python3 scripts/audit-docs.py` run clean before commit. Three spec edits total across all
five rulings — the `FR-237` citation (RL-864), the `compile_bundle` `async def`
correction (RL-866), and the `score_one` `async def` correction (RL-868) — none
introduces a new `FR-`/`NFR-`/`ADR-` id. One tooling fix (RL-866's `async def` regex gap
in `scripts/audit-docs.py`'s FR-19 check), verified as a real positive/negative pair: it
failed with the spec corrected and the old regex in place, and passed once the regex was
fixed — never asserted clean without having first seen it red. One skill addition (Ruling
5's verification-step rule in `.claude/skills/spec-change`).

**Addendum verification, filed later the same day.** Four more spec edits, across two
files, land with the addendum above: `03-rating-engine.md` §2 (glossary), §3.4 (new
`FR-243`), §8 (Redis row), and `07-platform.md`'s `FR-422`. This is the one `FR-`
id the paragraph above said this record introduced none of — correct as written at the
time, superseded by the addendum, not corrected in place, per this file's own dating
convention. `FR-243` re-derived as the next free id immediately before filing
(`git grep -oE "FR-RATE-[0-9]+" docs/specs/03-rating-engine.md | sort -t- -k3 -n -u | tail
-1` → `FR-252`, then confirmed absent everywhere in `docs/` by a direct grep, then
independently corroborated by `docs/plans/PL-00829-wk-670-implementation-plan-rate-tables-seeding-diffs-bulk-operations-import-export.md:13`'s own "Next
free: FR-243" marker, written the day before and agreeing without having been
consulted first). `python3 scripts/audit-docs.py` run clean on this delta.
