---
id: PL-851
family: plan
kind: leaf
title: WK-671 — Five Decision Points, Recovered
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-29
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-29-w11-decision-points-recovery.md
---

# WK-671 — Five Decision Points, Recovered

**What this is.** `~/w11-handover-2026-08-29/TEAM-STRUCTURE.md` §9 claimed: "Five decision
points are scoped with options and a recommendation each — evaluator caching, trace
sampling and retention, batch chunk/resume, per-quote error typing, and how a decline is
represented. They are not ruled: they are ruled when the WK-671 plan reaches their slice." That
section carried only the five names — no options, no recommendations, in any committed file.
The scoping happened in conversation during WK-671 setup and was never written down. This
document is that write-down, filed before the team's stand-down for the same reason PR #334
restated DP1/DP2/DP3 in full: a decision point that exists only in a conversation does not
exist for a team that has not had it.

**Mints no `FR-`/`NFR-`/`OQ-` id.** Cites only ids already defined in `docs/specs/`.

**Provenance, in prose, not as a resolvable link.** All five were scoped together in one
message: the decision-maker's own "WK-671 orientation report," drafted during WK-671 setup, before
the RFC-840/841 process adoption took priority over starting WK-671 itself. It was sent as a
report to the lead and never promoted into a committed file — session transcripts are
local to the machine and session that produced them, not a durable citation, so the full
text of each item is quoted below rather than pointed at. Where the wording below is
verbatim, it is marked as such; nothing here is paraphrased from memory.

**Status of each: recovered, not ruled.** Exactly as §9 said — these are options and a
recommendation, not a decision. Each still needs a decision-maker ruling, filed as a dated
sibling record next to the frozen plan, before its slice starts — the same treatment DP1/
DP2/DP3 are waiting on in `docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`.

---

## 1. Real-time evaluator caching

**Status: settled at the architecture level by RL-867; one implementation detail below is
recovered but not independently ruled.**

RL-867 (`docs/rulings/RL-00867-compiledbundle-is-spec-only-bundle-is-the-only-thing-that-exists-and-they-are-not-the-same-type.md`, "RL-867 —
`CompiledBundle` is spec-only") settles the two-tier shape explicitly, citing this same
orientation report by name: *"This is the same two-tier shape this session's own WK-671
orientation report recommended for the caching decision point, arrived at independently
from the executor's and planner's side and now given the concrete names the spec already
committed to."* `Bundle` is the Redis-cached, content-hash-keyed, distributable record;
`CompiledBundle` is the per-worker loaded form, produced by `load_bundle()`, never itself
round-tripped through Redis. That much is ruled and does not need re-deciding.

What RL-867 does not restate is the **refresh mechanism** — how a warm worker's
in-process `CompiledBundle` learns that a new one exists after a deployment switch. The
original analysis, verbatim:

> **1. Real-time evaluator caching.** FR-239/NFR-491 (bundle scores with zero
> DB/network access) + FR-268 (atomic switch, pre-warmed) + §8 (Redis: bundle cache
> keyed by content hash) + `07` FR-422 (Redis is the named cache; "nothing durable
> lives only in Redis — reconstructible from PostgreSQL and the blob store") + FR-444
> (scoring readiness requires a compiled bundle *in cache*). `model_call` mode
> (exact|approximation) is already pinned per-version (FR-223, rating.py:99-150) — not
> a runtime branch, so caching needn't key on it. (a) Redis-only, per-request
> GET+deserialize+booster-load — simplest, but a network round-trip on the hot path
> arguably violates NFR-491 and risks the GBM booster-load cost NFR-501/§8 flag. (b)
> Two-tier: Redis is the distribution/warm tier (content-hash keyed bytes, boosters as
> blob-store refs fetched once); each worker keeps an in-process slot holding the
> deserialised Bundle + loaded booster, refreshed by a short background poll against
> "current hash for env X"; requests read only the in-process slot. (c) No shared cache,
> refetch from Postgres/blob store per worker — contradicts §8/FR-422 outright.
> **Recommend (b)** — it's the literal reading of FR-268+§8+FR-422 together and the
> only option satisfying NFR-491 as written; poll over pub/sub for the refresh trigger
> (simpler, no missed-message edge cases, NFR-494's 30s switchover budget has plenty of
> room for a ~1-2s poll).

The two-tier shape (option b's top level) is RL-867. The refresh trigger — poll over
pub/sub, ~1-2 s cadence, against a "current hash for env X" — is the part that never made
it into RL-867's own disposition text. It is consistent with RL-867, not a competing
option; carried forward here so Task 1.3's `load_bundle`/refresh logic (`docs/plans/
PL-00854-wk-671-scoring-sequenced-slice-plan.md`) has it rather than reinventing it. **Not independently ruled —
a decision-maker should confirm this mechanism (or rule a different one) when Task 1.3's
refresh behaviour is built, since RL-867 itself never says "poll" or "pub/sub."**

---

## 2. Trace sampling and retention

**Status: recovered, unruled.**

> **2. Trace sampling/retention.** FR-258/259 (sampled 1% default +100% declines/errors,
> ≥13mo retention, feeds `05`), NFR-500 (200GB/yr @ 1% of 50M quotes). Trace (§4.5) is a
> nested per-step array, not a fixed-width row. Platform already has content-addressed
> blobs (`07` FR-418-420, `put`/`open` API at 07§5.2:368-371) and precedent for "row +
> blob" (`DislocationRun.largest_movers_blob`, 03§4.6). (a) full JSON in Postgres — wrong
> scale for 200GB/yr, taxes the transactional DB. (b) thin Postgres row (quote_id,
> rating_version_ref, sample_reason, bundle_hash) + trace body as a blob via the existing
> API; `GET /traces?...` (§5.1:524) queries the row table. (c) `05-monitoring` owns
> persistence — wrong direction, §7.3 says `03` produces and `05` "consumes traces as they
> are." **Recommend (b)**, and note explicitly for the plan: FR-258/259 don't state a
> **batch** sampling default — I'd recommend batch inherit the same 1%+declines/errors
> policy rather than 100%, or a 10M-row batch Job blows the annual storage budget in one
> run. `07` FR-420's reference-counted blob GC (configurable grace period) is a
> ready-made retention mechanism.

The current plan (`docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`, Slice 4) already names "sampling
policy... persistence to the blob store" without the thin-row/blob split or the GC-based
retention mechanism above — this recovers the reasoning behind that line.

**The batch-sampling-default gap this item flags is a spec omission, not part of this
decision point, and is not resolved here** — see the separate flag at the end of this
document.

---

## 3. Batch chunk/resume

**Status: recovered, unruled.**

> **3. Batch chunk/resume.** FR-253/254 (Job, chunked+resumable+identical code path),
> `score_batch(bundle, frame, *, chunk_rows=100_000, progress)` (§5.2:600-602). Platform Job
> model: FR-400 (structured progress w/ counters), FR-401 (cancellation is
> cooperative; "a cancelled Job leaves no partially-visible artifact") — that clause governs
> **cancellation**, not crash-resume, so FR-254's "resumable" is asking for something
> the generic Job contract doesn't already give. (a) full-restart-on-failure — simplest,
> matches the generic pattern, but a late failure on a multi-million-row run (dislocation
> examples show 1.28M-policy portfolios) discards real work at NFR-493's 1M/hr target.
> (b) chunk-checkpointed resume: each 100k-row chunk writes its part to job-scoped staging
> on completion; the Job's progress record names the last completed chunk; retry skips done
> chunks; only the final concatenated parquet is exposed as the citable result — keeps
> FR-401's "no partially-visible artifact" true for callers while satisfying
> resumability internally. **Recommend (b)** — it's the only reading giving FR-254's
> "resumable" independent meaning from the platform default.

The current plan's `chunk_rows: int = 100_000` default (Slice 3) traces to this analysis —
the plan carried the number without the reasoning or the job-scoped-staging mechanism.
Both are recovered here.

---

## 4. Per-quote error typing

**Status: recovered; the plan's own choice already matches the recommendation.**

> **4. Per-quote error typing.** FR-255 names 5 categories: contract violation,
> reference miss, table miss, constraint decline, model failure. Owned codes (§5.1:526-539)
> already cover 3: `INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS`, `RATE_TABLE_MISS`.
> "constraint decline" is FR-256's successful-response path, not an error code. **No
> owned code exists for "model failure"** — checked the full list, confirmed absent. (a)
> reuse `BUNDLE_COMPILE_FAILED` — wrong moment (compile-time vs run-time call), blurs the
> audit trail. (b) new code `MODEL_CALL_FAILED`, declared in `app/errors.py` before first
> use (spec-change skill's rule), matching the existing `_FAILED` suffix family
> (`BUNDLE_COMPILE_FAILED`, `LADDER_RECONCILIATION_FAILED`). **Recommend (b)** — I'll rule
> this formally (as a spec change appending to §5.1's owned-code list) once the plan reaches
> the slice. Also flagging: FR-255's batch abort "declared threshold" needs a home —
> recommend a workspace setting (matching `modelling.max_factor_count`-style precedent, `07`
> FR-448) with an optional per-batch-request override.

`docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md` Task 1.4 already declares `MODEL_CALL_FAILED`
matching option (b) — independently arrived at, now confirmed consistent with this
recommendation rather than by coincidence. **Not yet in the plan: the batch-abort-threshold
home** (a workspace setting, `FR-448`-style, with an optional per-batch override) —
Task 1.4/Slice 3 should pick this up when built.

---

## 5. How a decline is represented

**Status: recovered, unruled — and this is the decision point the "does a decline
short-circuit the DAG" question already belongs to. It is not a separate, undiscovered gap;
it is this item's own content, previously unrecovered.**

> **5. How decline is represented.** FR-256 (decline = successful `outcome: declined` +
> reason codes, never HTTP error), FR-225 (`reason_code` per constraint step), §4.4
> example shows `decline_reasons` as a **list** alongside a fully-populated
> `premium_ladder`. FR-216's DAG has no early-exit primitive. (a) short-circuit on first
> decline — ladder rungs downstream go null/absent; not what the §4.4 example shows. (b)
> full DAG always evaluates; `outcome` flips to `declined` if any constraint step's decline
> condition fires; `decline_reasons` collects every firing step's code (matches the
> example's plural field); ladder/premium stay fully populated ("what it would have cost"),
> useful for the Quote Sandbox compare view (§5.3) and dislocation. **Recommend (b)** —
> matches the committed §4.4 shape exactly and avoids inventing a nullable-ladder variant
> nothing else anticipates; for batch parquet output this means one row schema for quoted
> and declined alike (`outcome` string col + `decline_reasons` list col), no branching.

`docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md` Task 1.4 currently says only "constraint decline is
`outcome: declined`, never an error" — silent on short-circuit-vs-collect-all. This
recommendation (collect-all, option b) should be the exit-criterion behaviour when Task 1.4
is built, pending the decision-maker's ruling.

---

## Flagged separately: a spec omission surfaced during recovery, not a decision point

**FR-258/259 state no batch sampling default.** They fix the real-time default (1%,
+100% declines/errors) but say nothing about batch runs. Item 2's own analysis recommends
batch inherit the same policy, reasoning that a 100%-sampled multi-million-row batch Job
would blow NFR-500's 200GB/yr budget in one run — but this is the spec's silence being
noticed, not an implementation choice inside an existing requirement, unlike the five items
above. It needs an `OQ-` or a spec change from the decision-maker, not a line in this
document. Not resolved here; flagged for the decision-maker to take up separately.

(A second candidate gap — whether a decline short-circuits DAG evaluation — turned out on
recovery to be item 5's own content above, already answered by the recommendation there.
Not a second spec gap.)
