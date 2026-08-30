# W11 Slice 3 — still held, on one unruled decision; and D6, the decision that releases it

**What this is.** Slices 2 and 4 have leaf plans as of today
([`2026-08-29-w11-2-realtime-scoring-endpoint.md`](2026-08-29-w11-2-realtime-scoring-endpoint.md),
[`2026-08-29-w11-4-trace-sampling-persistence.md`](2026-08-29-w11-4-trace-sampling-persistence.md)).
Slice 3 does not. This says why, raises the one decision point that is in the way, and files the
durable content so the eventual plan is short.

**This is not a plan and it rules nothing.** D6 below carries options and a recommendation; the
ruling is the decision-maker's (`delivery-process.md` §3).

**Tree:** `d6505e9`, `git rev-parse origin/main`, verified equal before this was written.

**Highest ids in use, re-derived at `d6505e9`:** FR-RATE-65, NFR-RATE-14, OQ-RATE-7.
Next free: `FR-RATE-66`, `NFR-RATE-15`, `OQ-RATE-8`.

**This document mints none of them.**

---

## 1. What released, and what did not

[`2026-08-29-w11-slices-2-4-planning-readiness.md`](2026-08-29-w11-slices-2-4-planning-readiness.md)
held Slice 3 on three signals. Two have fired.

| Signal | State at `d6505e9` |
|---|---|
| **S-E** — Task 1.4 merged, and its per-step evaluator seam readable from shipped code | **Fired.** `d6505e9`. The seam is named below |
| **S-F** — D3, where FR-RATE-38's batch abort threshold is configured | **Fired.** Ruling 24 |
| **S-G** — the chunk/resume mechanism, and whether batch traces at all | **Half fired.** Ruling 25 settles batch traces. **Nothing has ruled chunk/resume** |

**The half that did not fire is the slice's spine.** FR-RATE-37 requires batch scoring to be
*"chunked, resumable, and progress-reporting"*, and resumability is the one word in that list
the platform does not already supply.

**How the absence was established, since an absence claim is only as good as the sweep behind
it.** `git grep -iln "resumab" -- docs/plans/` at `d6505e9` returns exactly three files: the
recovery document (which *recommends* a mechanism and explicitly does not rule it), the frozen
map, and the readiness document. **No ruling record contains the word.** A narrower grep for
`chunk` across the three W11 ruling records returns nothing at all.

## 2. The seam Slice 3 was waiting for — found, and it is not what the map implies

Task 1.4 named it, and named it in the source rather than leaving it to be inferred.
`packages/pricing-core/src/pricing_core/rating/score.py` exports exactly two public functions
(`__all__ = ["build_scoring_result", "score_one"]`); every function touching per-step semantics
is underscore-private and reachable only through them.

```python
def build_scoring_result(
    bundle: CompiledBundle,
    ctx: QuoteContext,
    rating_version_ref: ArtifactRef,
    result: Mapping[str, Any],
    engine_trace: Mapping[str, Any] | None,
) -> ScoringResult
```

Its module docstring states the contract with Slice 3 directly: *"`score_batch` is expected to
call the identical function after its own (batched, likely synchronous) evaluation of the same
compiled graph — the byte-identity Slice 3 proves is exactly this function producing the same
output from the same input, not two implementations that happen to agree."*

**Two things follow that a Slice 3 plan must not get wrong.**

- **There is no per-step evaluator in `pricing-core` to share.** Step-by-step evaluation happens
  inside the ZEN engine (`bundle.decision`), which is not this repository's source. What
  FR-RATE-37's *"identical code path"* actually means here is the **post-evaluation tail** —
  `build_scoring_result`. The readiness document's phrasing, *"an evaluator seam whose name is
  Task 1.4's to choose"*, invited the reading that a step-evaluation function would appear. It
  did not, and the byte-identity proof is narrower and sharper than that reading suggests.
- **`score_batch` stays plain `def`** (Ruling 5, restated in the module docstring), against
  `score_one`'s `async def`. The engine's sync `evaluate()` blocks the event loop — which is
  exactly why it is safe in a worker and not on the request path.

## 3. D6 — how is a batch run resumable?

**Raised here because nothing else names it.** Recovery item 3 analysed it and recommended an
option; the recovery document is explicit that its items are *"recovered, not ruled"*, and no
ruling record has taken it up.

**Why the platform does not already answer it.** FR-PLAT-9 gives *"a cancelled Job leaves no
partially-visible artifact"* — and that clause governs **cancellation, not crash-resume**. The
distinction is the recovery document's own and it is the crux: FR-RATE-37's *"resumable"* is
asking for something the generic Job contract does not supply. An implementer who reads
FR-PLAT-9 as covering it will build nothing and believe the requirement is met.

**What is already settled around it**, so D6 is not re-litigated wider than it is:

- `score_batch`'s signature is published at `03` §5.2, including `chunk_rows: int = 100_000` and
  a `progress` callback — **chunking and progress reporting are specified; only resume is open.**
- `JobKind.SCORE_BATCH = "score.batch"` exists (`model_schema/jobs.py:56`) and is **already
  queue-routed** — `backend/src/app/platform/jobs.py:75` maps it to `JobQueue.SCORING`. No
  handler is registered.
- Ruling 24 settles the abort threshold: a workspace setting `rating.batch_abort_failure_rate`,
  unset by default, plus a per-run Job argument that **may only lower** the effective threshold.
- Ruling 25 settles traces: `score_batch` takes **no sampling policy**.

### The options

- **(a) Full restart on failure.** Simplest; matches the generic Job pattern exactly; adds
  nothing to build. But it gives FR-RATE-37's *"resumable"* no meaning beyond what every other
  Job already has, and at NFR-RATE-5's 1 M risks/hour a late failure on a multi-million-row run
  discards real work. The dislocation examples in `03` §4.6 use a 1,284,902-policy portfolio, so
  the scale is not hypothetical.
- **(b) Chunk-checkpointed resume.** Each chunk writes its part to job-scoped staging on
  completion; the Job's progress record names the last completed chunk; a retry skips completed
  chunks; only the final concatenated parquet is exposed as the citable result. This keeps
  FR-PLAT-9's *"no partially-visible artifact"* true for callers while satisfying resumability
  internally. Costs a staging area and its own cleanup path.
- **(c) Idempotent re-scoring with output-side deduplication.** Re-run everything on retry but
  make writes idempotent by row key. No staging; but it pays the full compute cost again, which
  is the thing (b) exists to avoid, and it needs a row key the output schema does not yet
  guarantee is unique.

**Recommendation: (b)**, on the ground the recovery document gives — it is the only reading that
gives *"resumable"* independent meaning from the platform default — with one addition that
analysis did not carry: **the staging area needs a cleanup path with an owner**, or a crashed
run leaves orphaned partial parquet nobody deletes. FR-PLAT-20's reference-counted blob GC is
the obvious candidate and it is *not* automatic here, because Ruling 23 established for traces
that a **referenced** blob is never a GC candidate. Staging parts referenced by a Job progress
record would be in the same position.

**Not this planner's to rule.** A recommendation, and the addition is flagged precisely because
it is the part an executor would otherwise discover after the first crashed run.

## 4. Why this holds the slice rather than one task

The map sizes Slice 3 as one medium slice with a single deliverable, and the resume mechanism is
not a detachable corner of it: it determines the shape of the chunk loop, what the handler writes
per chunk, what the Job's progress record carries, and what the output blob is. A plan written
for (a) and a plan written for (b) differ in most of their steps.

That is a different situation from Slice 2, where Ruling 15 shrank one task and the rest was
unaffected, and from Slice 4, where the one genuinely awkward corner could be decided in the plan
and escalated if measurement contradicted it.

**Release signal: D6 ruled.** Nothing else is outstanding. On the ruling, the plan is quick to
write, because §5 below is the part that does not depend on which option wins.

## 5. What the Slice 3 leaf plan can already take from here

Durable at `d6505e9`, and independent of D6:

- **Requirements**, each listed individually: FR-RATE-36 (`03` §3.7, the endpoint, Job and
  content-addressed parquet output), FR-RATE-37 (§3.7, chunked/resumable/progress and the
  identical code path), FR-RATE-38's batch half (§3.7, counts and samples per error type, abort
  only past the declared threshold), NFR-RATE-5 (§9, ≥ 1 M risks/hour/worker, linear in workers).
- **The FR-RATE-37 proof, stated exactly**: `score_batch` and `score_one` scoring the identical
  rows produce **byte-identical** premiums, and the mechanism is that both call
  `build_scoring_result` on the same engine result — not two implementations that agree.
- **The seam and the sync/async split** (§2 above).
- **Ruling 24's shape**: `rating.batch_abort_failure_rate` follows the `<module>.<name>` form of
  the two shipped neighbours read at `backend/src/app/platform/model_specs.py:62` and `:65`,
  typed `| None` and guarded `if … is not None`. The per-run value is a **Job argument**, never a
  fourth settings-resolution tier — `settings.resolve` has exactly three branches (`ENV`,
  `WORKSPACE`, `DEFAULT`) and no fourth to add one to. **The argument may only lower the
  threshold**, on `01`'s `severity_override` precedent, and the Job must record both the
  threshold in force and the observed failure rate when it aborts.
- **Ruling 25's exclusion**: `score_batch` takes no sampling policy; a batch run may produce
  traces on request, written with the Job as their parent, and they never enter
  `GET /api/v1/traces`. **Slice 4's Task 4C writes the test that enforces this before Slice 3
  exists** — see that plan.
- **The registration site**, verified rather than copied from the map: handlers live in
  per-domain modules wired from `backend/src/app/worker/entrypoint.py`, not in
  `backend/src/app/worker/handlers.py`, which is the registry itself (`HANDLERS`,
  `register_handler`, `handler_for`). `rating_handlers.py` registers `RATING_COMPILE` and is the
  nearest neighbour; its `register_rating_handlers()` loop is the shape to follow.
- **`pl.LazyFrame` still has no precedent.** `git grep -c "LazyFrame" -- '*.py'` returns zero
  repo-wide at `d6505e9`, while the same pattern with no pathspec hits five documents — the type
  is specified in `03` §5.2's signature and has never been used in this codebase. The positive
  control (`git grep -c "import polars" -- '*.py'`) returns hits, so the zero is a true negative
  and not a dead pathspec. This belongs in the plan's **scope** section, not a step:
  [`README.md`](README.md)'s *"a missing neighbour is a scope finding"*.
- **The scheduling constraint**: Slice 3's deliverable is `score_batch` in
  `packages/pricing-core/src/pricing_core/rating/score.py`. **Task 1.5 is building in that
  package now.** Slice 3 must not start against it concurrently, and its plan should cite
  symbols in that package by name with a re-derivation command rather than by line number.
- **The evidence sweep the plan must re-run at its own commit**, not reuse from here:
  `git grep -n "score_batch" -- '*.py'`; `git grep -n "SCORE_BATCH" -- backend/`; and a
  `git diff` of the W11 ruling records between `d6505e9` and that commit — **by diff, not by
  re-listing `## Ruling N` headings**, because an addendum to an existing ruling gets no new
  heading.

## 6. Verification

- **Tree:** `d6505e9`, `git rev-parse HEAD` equal to `git rev-parse origin/main` before this was
  written; `git merge-base --is-ancestor d6505e9 origin/main` confirmed Task 1.4 is on `main`
  rather than taken on report.
- **The absence claim behind the hold** was made with the full marker class, not one spelling:
  `git grep -iln "resumab" -- docs/plans/` (three files, none a ruling record) plus a `chunk`
  sweep of all three W11 ruling records (no hits).
- **The seam claim** was read from `score.py`'s `__all__`, its public def lines and its module
  docstring, not inferred from the frozen map or from the readiness document — which is how the
  readiness document's own phrasing about it was found to be misleading (§2).
- `python3 scripts/audit-docs.py` — run before commit.
- This document mints no `FR-`/`NFR-`/`OQ-` id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row. **D6 is a decision point, not an open question**
  — the same treatment DP1, DP2 and D2–D5 received, each ruled in a dated sibling record rather
  than mirrored as an `OQ-`.
