# NFR-RATE-1 (component) and NFR-RATE-2 — W11 Slice 1 Task 1.5, the bare-metal latency harness

Measured 2026-08-29 on this branch's `packages/pricing-core/src/pricing_core/rating/score.py`
(`score_one`), `runtime.py` (`load_bundle`/`CompiledBundle`) and `compile.py`
(`compile_bundle`), on the CI-equivalent `.venv` this worktree built with
`uv sync --all-packages`, using `scripts/bench-rating.py`
(`uv run python scripts/bench-rating.py`). `docs/specs/03-rating-engine.md` §9
(`:797-798`):

- **NFR-RATE-1** (`:797`): "Real-time scoring p99 < 50 ms server-side at 200 rps per
  replica for a ~200-step motor structure with one `exact` GBM call (NFR-OVR-1). Without a
  GBM call, p99 < 15 ms." — this note measures the **component** half only (`score_one`
  called directly, no HTTP, no FastAPI, no database); the sustained-200-rps and
  full-HTTP-path halves are Slice 2's Task 2.1 per this task's own plan
  (`docs/plans/2026-08-29-w11-1-evaluator-core.md`).
- **NFR-RATE-2** (`:798`): "Tracing adds ≤ 20 % to scoring latency and never changes the
  result (R3)."

## Method

- Fixture: a ~200-step motor structure built by `scripts/bench-rating.py` itself (not
  imported from the test suite — see the script's own module docstring): 2 scalar inputs
  (`driver_age`, `channel`) + 8 numeric rating-factor inputs, one `table` lookup, one
  `exact` `model_call` against a real, trained XGBoost booster (8 features, 5,000
  synthetic rows, 300 rounds — sized like Task 1.3's own NFR-RATE-4 "real large" fixture,
  not a toy 3-round one), 187 chained `expression` steps, and one `output` step — **200
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
- Machine: Intel Xeon @ 2.20GHz, 4 cores, 16.4 GB RAM — a shared development machine, not
  a dedicated benchmark host (`CLAUDE.md` §11's load-contention trap). **The 1-minute load
  average is reported per run in the NFR-RATE-1 table below, because on this machine it is
  the variable that decides the verdict**; the first run's was 0.39, and `bench-rating.py`
  has since been changed to read the load either side of every timed block and print it
  beside the figure, so a future run records the condition it was taken under rather than
  one startup reading shared across all three blocks.
- Tree: the first four runs were taken on the `w11-1-5-bench-and-ruling28` branch off
  `origin/main` at `d6505e9`; the fifth on the same branch after this note's corrections,
  and the branch has since merged `origin/main` at `6e548f8`. Nothing on the scored path
  changed between them.

## Result — NFR-RATE-1 (component)

*Verdict corrected 2026-08-30, after three independent re-runs during the audit of PR #416.
This section first read **"Both halves PASS"** on the strength of a single run. The no-GBM
half does not reproduce, and the correction is a verdict change rather than a wording fix.
Every run is tabulated below with its load: the evidence for the corrected verdict is here,
and the finding itself is **F38** in `docs/audit/register.md`, beside NFR-RATE-2's separate
failure at **F35**.*

- **Without a GBM call (p99 < 15 ms): measured; verdict unstable across runs — not
  established.** This note first recorded 9.410 ms and a "~1.6x" margin. Three re-runs of
  the same committed harness — unmodified, same tree, same command — returned **OVER**,
  **OVER**, and a PASS at 94 % of budget; a fifth run passed at 68 %. **Two of five runs
  breach the bound.** This half must not be booked as delivered on this measurement.
- **With a GBM call (p99 < 50 ms): PASS in 5 of 5 runs — but not at the number first
  reported.** 12.537 ms here, 14.8–27.8 ms on re-measurement. The verdict survives because
  every observed p99 sits under 50 ms. The **~4.0x margin does not**: at the worst observed
  figure it is **~1.8x**.

Every run, with the 1-minute load average it was taken under — the condition is part of
the measurement, not context for it, because NFR-RATE-1 states its budget *"at 200 rps per
replica"*:

| run | 1-min load | with-GBM p99 (< 50 ms) | | without-GBM p99 (< 15 ms) | | trace overhead at p99 (≤ 20 %) |
|---|---|---|---|---|---|---|
| this note's original | 0.39 | 12.537 ms | PASS | 9.410 ms | PASS | +723 % OVER |
| audit re-run 1 | 1.63 | 27.713 ms | PASS | 24.816 ms | **OVER** | +714.6 % OVER |
| audit re-run 2 | 6.42 | 25.159 ms | PASS | 26.725 ms | **OVER** | +718.9 % OVER |
| audit re-run 3 | 8.50 | 27.816 ms | PASS | 14.076 ms | PASS (94 % of budget) | +497.0 % OVER |
| post-audit, instrumented | 1.10→1.16 / 1.16→1.38 / 1.43→1.36 | 14.763 ms | PASS | 10.162 ms | PASS (68 % of budget) | +679.2 % OVER |

The first four loads are single readings taken at run start. The fifth is this branch's
`bench-rating.py` after it was changed to read the load either side of each timed block —
one span per block, in the column's own order (with-GBM / without-GBM / traced).

**Load drives the volatility without determining the verdict.** It does not order the
results — re-run 3 passed at load 8.50 while re-run 1 breached at 1.63 — so the finding is
not "the box was busy", and **a single run cannot establish this half whatever the load**.
But load does set the *spread*: the distribution table below shows it roughly five times
wider under load than on a quiet box.

The two together are the trap. **A quiet run's narrow spread makes a single run look more
trustworthy than it is** — which is exactly how one run at load 0.39 came to be written
down here as a PASS with a "~1.6x margin". Over ~40 minutes the audit observed the
1-minute load ranging 1.6–8.7, median ≈6. 0.39 is the least representative condition
available for a requirement stated at 200 rps, and it is simultaneously the condition that
produces the most convincing-looking evidence.

**The distribution — the acceptance criterion that was not met, and the one that explains
the instability once you have it.** The leaf plan
(`docs/plans/2026-08-29-w11-1-evaluator-core.md:1416`) requires *"the distribution, not
only the p99 against the bound. A single number comfortably inside a budget and a number
sitting on it are different findings, and only the distribution distinguishes them."*
`bench-rating.py` **already printed** stdev, p50 and p90 beside every p99. This note
recorded p99, mean and max only. Nothing was missing from the instrument; the numbers were
dropped on the way to the page. What they show — once there are runs at more than one load
to compare — is the table below, and the qualification that follows it.

What they were — and why one run's distribution is not *the* distribution:

| | stdev | p50 | p99 | budget |
|---|---|---|---|---|
| without GBM, under load (audit re-runs, load 1.6–8.5) | **3.5–4.0 ms** | ≈10 ms | 14.076–26.725 ms | 15 ms |
| without GBM, quiet box (fifth run, load 1.16→1.38) | **0.706 ms** | 6.858 ms | 10.162 ms | 15 ms |
| with GBM, quiet box (fifth run, load 1.10→1.16) | 1.445 ms | 9.207 ms | 14.763 ms | 50 ms |

A stdev of 3.5–4.0 ms on a 15 ms budget with p50 ≈ 10 ms describes a distribution whose
tail sits *on* the bound. 0.706 ms with p50 6.858 ms describes one that does not. **The
spread is roughly five times wider under load than on a quiet box** — that is the
instability restated as a distribution rather than as a disagreement between verdicts, and
it is why the p99 alone flips. Quoting only the quiet-box figures here would repeat this
note's original mistake in a new place. The with-GBM maximum is 2.4x its own p99, so that
half's tail is long too, even where the verdict holds.

**This qualifies the "report the distribution" criterion rather than vindicating it.** The
tempting conclusion — that printing stdev would by itself have caught the bad verdict — is
wrong, and this note's own first run is the counterexample. Its recorded mean is 6.915 ms
and its recorded maximum 12.959 ms, putting the largest of 1,000 samples just 6.044 ms
above the mean; a stdev of 3.5–4.0 ms would place that maximum only **1.5–1.7 standard
deviations out**, which no latency distribution does. So the first run's spread was
necessarily narrow — as the fifth run's **0.706 ms** is, whose mean and max sit within
2 % and 0.5 % of the first run's. Had run 1 printed its own distribution it would have read
as *reassuring*, not fragile.

**What establishes this verdict is repetition under varied load. The distribution is what
explains the result once you have both — not the trigger that reveals it.** The acceptance
criterion asks for one of the two. Reporting the distribution of a single quiet run
satisfies it and still gets the verdict wrong.

*Limits of this evidence:* one machine, five runs per configuration, load observed but not
controlled; the under-load distribution is a range across three runs rather than one run's
figures, and this note's own first run recorded none at all. The claim is that **the
verdict is unstable**, not that the true p99 is any particular number.
These are also **warm-slot** figures: `compile_bundle` and `load_bundle` — including
XGBoost booster deserialisation and the `nthread=1` baking — run once, outside the timed
region, so the boosters are resident for every sample.

This component measurement excludes the sustained-200-rps and ASGI-embedded overhead Slice
2's Task 2.1 adds. A full-path p99 at that point starts from the figures in this table, not
from the 9.410 ms first reported here.

## Result — NFR-RATE-2 (trace overhead)

From this note's original run (load 0.39); the other four are in the NFR-RATE-1 table
above.

| Metric | Measured | Budget | Verdict |
|---|---|---|---|
| p99, with GBM, 200 steps | 103.227 ms traced vs. 12.537 ms untraced = **+723 %** | ≤ 20 % | **OVER, by ~36x** |
| mean, with GBM, 200 steps (informational) | 75.511 ms traced vs. 9.235 ms untraced = **+718 %** | — | — |

**NFR-RATE-2 fails at this scale, by a wide margin, on both metrics — and unlike
NFR-RATE-1's no-GBM half, this verdict is robust.** Every one of the five runs in the
NFR-RATE-1 table above returned OVER, across loads 0.39 to 8.50 and a span of +497 % to
+723 %. Nothing about the margin is close enough for contention to decide it.

Nor is it a noisy tail: the trace-overhead percentage was measured at four graph sizes
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
super-linearly in the node count rather than a fixed per-node tax — because `to_wire`'s
`passThrough: true` (needed for the premium ladder, per this plan's own "Verified facts")
keeps the accumulated context growing at every node, and the traced response carries a
copy of that context **per node**, so the total trace payload grows faster than linearly
in the step count.

**That mechanism was offered here as the most likely one rather than a verified one. It is
now verified**, and registered as **F35** (`docs/audit/register.md`). Two levers this note
did not run establish it:

- **Causation.** Adding **one** declared `string` input carrying 4 KB that **no step
  consumes**, to the same 200-step structure, left the node count unchanged and the trace
  entry count identical at 191, more than doubled the trace payload (1,119,097 →
  2,639,646 B) and added **7.76 ms (+14.3 %)** to engine-side traced cost — while the
  engine's own reported per-node execution time stayed flat (9.142 → 10.558 ms) and the
  untraced path grew by ~1 ms. One decorative input that nothing reads costs ~8 ms of
  traced latency, because `passThrough` carries it into every trace entry.
- **Proportionality.** Across 63 and 200 steps, engine-side traced cost tracks **payload
  bytes at ≈1:1** (payload 9.88x, cost 9.63x) and does **not** track node count (entries
  3.54x, the engine's own per-node sum 2.65x).

A mid-graph trace entry is `input` 2,965 B + `output` 2,992 B ≈ **5,859 B per node** — the
accumulated context, copied into all 191 entries, twice.

**Where the added time is actually spent, measured rather than assumed:** a follow-up
comparison of `score_one`'s own `timing_ms["evaluate"]` (the `await
bundle.decision.async_evaluate(...)` call in isolation) against its total wall time, at
the 200-step scale, 200 calls each:

| | wall mean | `async_evaluate()` mean | `score_one`'s own post-processing (`build_scoring_result`/`_build_trace`) |
|---|---|---|---|
| trace=False | 9.147 ms | 8.800 ms (96 %) | 0.348 ms |
| trace=True | 77.133 ms | 68.476 ms (89 %) | 8.657 ms |

Of the ~68 ms added by tracing, **~60 ms (88 %) is inside `async_evaluate()` itself** and
**~8 ms (12 %)** is `pricing-core`'s own `_build_trace`/`build_scoring_result`
post-processing (which does its own per-node `dict(entry.get("input") or {})`/`dict(output)`
copies over the engine's returned trace, `score.py:582-583`). The split reproduced exactly
under independent re-measurement during the PR #416 audit. A second decomposition run on the
shipped code path — untraced eval, then traced eval with `engine_trace=None`, then traced
eval with the trace built — put our own share at **25 %** rather than 12 % (audit §D2);
the two decompositions are not like-for-like (different booster size, and the second
isolates the `engine_trace` argument rather than differencing the whole post-processing
block), so **our share is 12–25 % depending on how it is cut**.

**Where that cost is owned — corrected 2026-08-30.** This note originally read the 88 %
share as sitting "on the third-party side of the FFI boundary, not in code this workstream
owns outright". **That inference does not follow from the split, and direct measurement
contradicts it.** Inside a 99.3 ms trace-enabled `async_evaluate()` call, the engine's
**own** summed per-node elapsed time is **10.3 ms across 191 entries**: it is barely
evaluating. The balance is spent building and marshalling a **1,119,097-byte** trace
payload — and that payload's size is set by **our** `to_wire`, which stamps
`"passThrough": True` at `runtime.py:159`, `:253` and `:319`. Engine-side traced cost
tracks payload bytes at ≈1:1 and does not track node count (the two levers above).

**So the dominant cost is ours to cut, and the lever sits on our side of the FFI
boundary.** Not by trimming `_build_trace` — that is the 12–25 % share, and no share of
that size closes a gap this wide — but by **reducing what the trace carries per node**:
what `to_wire` asks the engine to record and return, rather than what `_build_trace` does
with it afterwards. Whether `passThrough` can carry less without breaking the premium
ladder (this note's own "Verified facts" say the ladder needs it) is a real design
question, but **our** design question. The remedy is **not** closed to us pending an
upstream `zen-engine` change.

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
no concurrency (Slice 2's Task 2.1 and Task 1.4's own concurrency note respectively); **no
bundle hydration** — `compile_bundle` and `load_bundle`, booster deserialisation included,
run once outside the timed region, so every figure here is a warm-slot, booster-resident
one; one machine, five runs but a single machine and uncontrolled load; a
synthetic fixture with a real but arbitrarily-sized booster (300 rounds/8 features/5,000
rows) rather than a production model; the without-GBM structure reuses the same 187-step
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
