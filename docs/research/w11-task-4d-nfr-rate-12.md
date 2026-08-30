# NFR-RATE-12 — trace storage capacity projection (W11 Slice 4, Task 4D)

`docs/specs/03-rating-engine.md` §9 (`:906`): *"Trace storage: 1 % sampling of 50 M annual
quotes stays under 200 GB/year with the sampled-trace schema."*

**This is a projection, not a measurement of the requirement itself**, and Task 4D's own
title says so. Nobody scores 50 M quotes over a year to observe storage directly. What is
measured directly, with real code and no estimate, is the **actual serialised byte size**
of a real `Trace` produced by `score_one(bundle, ctx, trace=True)` — the exact call
`app.platform.traces.write_trace` serialises with `trace.model_dump_json().encode()`
(`backend/src/app/platform/traces.py:112`). That measured size is then multiplied out
against NFR-RATE-12's own stated volume (50 M quotes/year, 1 % sampling). The multiplication
is the projection; the byte count feeding it is the measurement.

**Verdict: OVER budget — 2.58× the 200 GB/year figure, at the actual ~200-step reference
structure.** Not tuned to pass; reported as measured. See §5.

## 1. Method

- **Code under test.** `pricing_core.rating.score.score_one`, called directly — no HTTP,
  no FastAPI, no database. `write_trace`'s serialisation line is not re-implemented: this
  script calls `result.trace.model_dump_json().encode()` itself, the same expression
  `write_trace` runs, and measures `len()` of the result.
- **No compose stack, no infra.** `BlobStore.put` (`backend/src/app/platform/blobs.py:130`)
  writes the given bytes to S3/MinIO verbatim — no compression, no re-encoding — so the
  on-disk blob size for a trace is exactly `len(trace.model_dump_json().encode())`.
  Measuring the serialisation directly measures what would be persisted, without needing
  Postgres or MinIO running to prove it. This is a size measurement, not a timed one, so
  the "quiet box" condition that gates a latency benchmark on this shared machine does not
  apply here — the byte count is deterministic for a given fixture and is unaffected by
  ambient load.
- **Script.** `scripts/bench-trace-size.py`, run as `uv run python
  scripts/bench-trace-size.py`. Fixtures (the compiled `RatingAlgorithm`, the trained
  booster, the `QuoteContext`) are reused from `scripts/bench-rating.py` via `importlib`
  rather than rebuilt — the same ~200-step "motor structure" NFR-RATE-1/2 are measured
  against, so this note's headline figure is read off the reference structure those
  requirements already use, not an arbitrary one.
- **Sweep.** Five step counts, `with_gbm=True` throughout (every structure includes the one
  `model_call` step): `n_expr ∈ {5, 20, 50, 100, 187}`. `187` is `bench-rating.py`'s own
  `N_EXPR_STEPS` constant — the value that constructs its "~200-step motor structure"
  (`2` fixed inputs + `8` feature inputs + `1` table + `1` model_call + `187` expression
  steps + `1` output = 200 algorithm steps; the persisted `Trace` carries 189 of those —
  the two synthetic input/output wire nodes `_build_trace` skips are not algorithm steps).
- **Booster fixture.** 300 rows / 20 rounds — deliberately small. A `model_call` step's
  `produced` is one `risk_premium_minor` value regardless of tree count or training rows,
  so booster complexity does not change trace *size*; a large, realistic booster
  (`bench-rating.py`'s own default of 5,000 rows / 300 rounds) would only slow this script
  down for no effect on the number being measured.
- **One scored quote per step count** — the fixture's inputs are fixed
  (`bench-rating.py`'s `_ctx()`, seed `20260829`), so the byte size for a given structure
  is deterministic, not sampled. Repeating the run at a fixed `n_expr` reproduces the same
  byte count exactly; it is not a distribution to average over the way a latency figure is.
  What *does* vary, and is reported as a distribution rather than a mean, is size **against
  step count** (§4).
- **Machine.** `x86_64`, 4 cores, 16.4 GB RAM — a shared development machine, not a
  dedicated benchmark host. 1-minute load average 0.41–0.77 across the session (not
  relevant to this measurement's correctness, since nothing here is timed).
- **What else was running.** Postgres, MinIO and Redis containers (`gi-pricing-postgres-1`,
  `gi-pricing-minio-1`, `gi-pricing-redis-1`) were up throughout, per this box's standing
  state, though this measurement used none of them. Three background pollers were also
  running on the shared host for the session (a reporter-status cycle, a balance-watch
  heartbeat, and a PR watcher) plus one `ci-watcher` subagent — none is a compute-heavy
  process and none was told to pause, since nothing here is a timed measurement.
- **Tree.** `01ba0bd2f16aef26eac3aeefb029f56140fb96b6` (`origin/main` after PR #495,
  docs-only). This worktree's branch adds only `scripts/bench-trace-size.py` and this note
  on top of it; no scored code differs from that tree.
- **Pass count.** One run of the script (one scored quote per step count, five step
  counts). Not repeated: the byte size at a fixed structure is deterministic (see above),
  so a second run would reproduce identical figures rather than add information — the
  "repeat near a bound" rule applies to a statistical measurement, and this one is not.
- **Ref cardinality.** One `RatingAlgorithm` structure per step count; one workspace; one
  `QuoteContext`.

## 2. What the sweep found, and why it is reported rather than smoothed over

Trace size does **not** scale linearly with step count. `TraceStep.consumed`/`.produced`
are populated in `pricing_core.rating.score._build_trace`
(`packages/pricing-core/src/pricing_core/rating/score.py:660`) directly from the
zen-engine's own per-node trace entry (`entry.get("input")`/`entry.get("output")`), and
that entry carries the **full accumulated evaluation context at that node**, not only the
variables the algorithm step itself declares as consumed/produced. Verified directly by
inspecting individual steps of a 50-`n_expr` trace: step `s_v047`'s `consumed` dict has 59
keys — every input and every `v000`…`v046` computed before it — not the one key
(`v046`) the algorithm step's own `consumes` list names.

Consequently each step's serialised size grows with its position in the chain, and total
trace size grows **worse than linearly** in step count (quadratically, for a chain where
each step's context includes everything before it). This is a real, shipped-code property
— not a script artifact and not something this task changes — and it is why extrapolating
the reference figure from a smaller step count would have been wrong: the reference
figure below is measured *at* 189 steps, not scaled up to it from a smaller sample.

## 3. Result — size against step count

| `n_expr` | steps in `Trace` | bytes | bytes/step |
|---|---|---|---|
| 5 | 7 | 5,955 | 850.7 |
| 20 | 22 | 26,879 | 1,221.8 |
| 50 | 52 | 103,123 | 1,983.1 |
| 100 | 102 | 332,281 | 3,257.7 |
| **187** | **189** | **1,032,137** | **5,461.0** |

The `187`/`189` row is the reference structure: `bench-rating.py`'s own "~200-step motor
structure", `with_gbm=True`, the same structure NFR-RATE-1/2 measure latency against.

## 4. Projection over NFR-RATE-12's stated volume

**Scope, per the task's own acceptance standard and Ruling 25:** quotes only. Batch rows
contribute nothing to the sampled production stream (Ruling 25,
`docs/plans/2026-08-29-w11-slices-3-4-rulings.md`), so batch volume is not added. No
deduplication benefit is assumed (Ruling 23): `elapsed_us` on every step makes two traces
of identical inputs byte-distinct, so there is no basis for a dedup discount.

```
sampled quotes/year = 1% of 50,000,000                 = 500,000
blob bytes/year      = 500,000 x 1,032,137 bytes        = 516,068,500,000 bytes
                                                          = 516.07 GB
row bytes/year (upper bound, ScoringTraceRow text columns, JSONB columns NULL on a
                `complete` row, `backend/src/app/db/models.py:2033`)
                     = 500,000 x 459 bytes               = 0.23 GB
budget (NFR-RATE-12)                                     = 200 GB/year
```

| clause | verdict |
|---|---|
| Blob storage at the ~200-step reference structure | **OVER — 2.580× budget** (516.07 GB vs. 200 GB) |
| Row storage (negligible, upper-bounded) | adds 0.001× budget — does not change the verdict |
| **NFR-RATE-12, overall** | **PROJECTED OVER BUDGET, at ~2.58×** |

Read as decimal GB (10⁹ bytes), matching how a storage budget is conventionally stated;
the spec does not disambiguate GiB vs. GB, so this is a stated reading rather than a
resolved ambiguity.

## 5. What this does and does not show

**Shows:** at the actual reference motor structure (~200 steps, one GBM `model_call`, the
same structure NFR-RATE-1/2 use), one sampled trace's real serialised size is ~1.03 MB, and
multiplying that by NFR-RATE-12's own stated annual sampled-quote volume (500,000)
projects to ~516 GB/year — over the 200 GB/year budget by roughly 2.58×. The row is
negligible next to the blob (< 0.001× the budget) and does not change the verdict either
way.

**Does not show:**

- **A year of real production storage.** This is a projection from one structure's
  measured size times the requirement's own stated volume, not an observation of traffic.
  If the real deployed algorithm has materially fewer or more steps than the ~200-step
  reference, or a different `model_call` count, the real figure moves — this note
  measures the reference structure NFR-RATE-1/2 already use, not a survey of every
  algorithm shape this platform could run.
- **FR-RATE-42's 100 % decline/error sampling floor.** NFR-RATE-12's own text is read
  literally — "1 % sampling of 50 M annual quotes" — and this projection does not add a
  decline/error rate assumption the requirement does not itself state. In production the
  persisted volume would be **higher** than this projection once declines and errors (each
  sampled at 100 % regardless of the 1 % rate) are included, so this projection is not a
  worst case.
- **The always-capture-then-discard cost.** Ruling 35 already moved trace *production* off
  the serving request onto an off-path worker Job — a latency/worker-cost question,
  unrelated to what gets stored once a trace is written, so it does not change this note's
  figures.
- **Compression or any storage-layer size reduction.** None exists in this platform's blob
  store; `BlobStore.put` stores bytes verbatim (§1). A compressed-at-rest store (if ever
  added) would change this projection; this note measures the shipped store.
- **Multi-run variance.** Byte size at a fixed structure is deterministic (§1); one run is
  what there is to measure, not one of several samples.

## 6. Disposition

**NFR-RATE-12 is projected — the task's own word — from a real measurement, and the
projection reads OVER budget by ~2.58×.** Per this task's own instruction and the pattern
already set by NFR-RATE-1 in this workstream (measured and recorded FAILING rather than
the fixture tuned until it passed): this figure is recorded as measured, not adjusted. The
remedy, if one is wanted — a smaller sampling rate, a slimmer trace-step shape that does
not carry the full accumulated context per step (§2), a lower sample rate for very long
chains, or accepting the higher budget — is the decision-maker's, not this task's; Task 4D
is the projection, not the fix.

**A separate, more general observation belongs to whoever reviews this record next.** §2's
finding — that `TraceStep.consumed`/`.produced` carry the full accumulated context rather
than only the step's own declared inputs/outputs — is a property of shipped code
(`pricing_core.rating.score._build_trace`), verified here rather than assumed, and it is
the single largest driver of the OVER verdict: a trace whose steps carried only their own
declared consumed/produced fields would be substantially smaller. This note does not
propose changing that behaviour — doing so is outside Task 4D's scope (a projection, not
an implementation change) — but the finding should not be read as merely an artifact of
this benchmark's fixture; it was verified against real per-step contents (§2) on real
shipped code.
