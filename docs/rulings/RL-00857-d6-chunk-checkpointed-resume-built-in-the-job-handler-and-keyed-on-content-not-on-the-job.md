---
id: RL-857
family: ruling
title: D6: chunk-checkpointed resume, built in the Job handler and keyed on content, not on the Job
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-3-d6-batch-resumability-ruling.md
---

# WK-671 Slice 3 — D6: batch resumability, the trigger that is not there, and the step-evaluator sentence this exposed (2026-08-29)

**What this is.** The ruling on **D6**, raised in
[`../plans/PL-00848-wk-671-slice-3-still-held-on-one-unruled-decision-and-d6-the-decision-that-releases-it.md`](../plans/PL-00848-wk-671-slice-3-still-held-on-one-unruled-decision-and-d6-the-decision-that-releases-it.md) §3 as
the single unruled decision holding WK-671 Slice 3, plus the spec correction that testing its
premises exposed. D6's options and recommendation are the planner's; the decision is this
role's (`delivery-process.md` §3).

**Numbering continues at 31.** Rulings 1–5 are the prework record's, 6–13 the Slice 1 record's,
14–15 the Slice 2 record's, 16–21 the Slices 2–4 record's, 22 the rate-table maturity record's,
23–25 the Slices 3–4 record's, 26–27 the ruling-vs-plan-scope record's, 28–29 the algorithm-pin
maturity record's, and 30 the FR-243 attribution record's. Nine files, thirty rulings, no
gaps, re-derived by heading sweep at `28ec778` rather than taken from any record's own summary.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code.** FR-254 takes a dated clarification in
place — the shape RL-889 used for FR-255 — and `03` §5.2's prose is corrected.
`OQ-RATE-8` stays free.

**Read against `origin/main` at `28ec778`**, with `HEAD` identical, re-fetched immediately before
filing.

---

## RL-857 — D6: chunk-checkpointed resume, built in the Job handler and keyed on content, not on the Job

**The decision, restated.** How is a batch run resumable? **(a)** full restart on failure;
**(b)** chunk-checkpointed resume, each chunk's part written to job-scoped staging, the Job's
progress record naming the last completed chunk, and a retry skipping completed chunks;
**(c)** idempotent re-scoring with output-side deduplication. The planner recommended **(b)**.

**Adopted: (b)'s mechanism — chunk checkpointing — with two of its three stated components
struck.** The staging is not job-scoped, the ledger is not the Job's progress record, and the
retry it hands off to does not exist. Findings are ordered by how much each changes the work.

### 1. Nothing re-runs a terminal Job, and the platform says so twice

Both (a) *"full restart on failure"* and (b) *"a retry skips completed chunks"* presuppose that
a failed or crashed batch Job runs again. **It does not, for any job kind.** At `28ec778`:

- **`task_acks_late=True`** and `task_reject_on_worker_lost=True` are set
  (`backend/src/app/worker/celery_app.py:46-47`), and `backend/src/app/worker/tasks.py:12`
  states the intent: *"a worker killed mid-job leaves the message for redelivery."* The broker
  does redeliver.
- **The redelivery is then discarded.** `run_job` transitions the Job to `RUNNING` *before*
  calling the handler, and guards its own entry on the Job still being `QUEUED`:

  ```python
  if row.status is not JobStatus.QUEUED:
      _log.info("job is not queued; another worker holds it", ...)
      return row.status
  ```

  A worker killed mid-chunk leaves the row in `RUNNING`; the redelivered message hits that
  guard — written for concurrent-delivery safety — and returns. The module docstring says it
  outright: *"A second delivery for a Job that is no longer `queued` is a no-op, not a second
  run."*
- **Nothing moves it back, and nothing could.** There is no retry or resubmit endpoint
  (`backend/src/app/api/jobs.py` declares exactly five routes — list, get, logs, cancel, stream
  events), and **there is no reaper**:
  `git grep -rn "reaper\|reap_" -- backend/ packages/ docs/specs/07-platform.md` returns exactly
  one hit, the comment at `backend/src/app/platform/jobs.py:229` naming *"expired by the
  reaper"* — a comment naming a mechanism that does not exist. Even a hypothetical one would be
  refused: `VALID_TRANSITIONS`
  (`packages/model-schema/src/model_schema/jobs.py:106-114`) gives `SUCCEEDED`, `FAILED` and
  `CANCELLED` each `frozenset()` — **no outbound edge from any terminal state.**
- **The `RetryState` on the Job is inert.** `Job.retries` exists
  (`model_schema/jobs.py:199-204`: `attempted`, `max: int = 3`, `policy`), and `attempted` is
  never incremented anywhere. `JobError.retryable` is written `False` at all four call sites in
  `tasks.py` and is never read. Both are shape without mechanism.

**So a crashed batch Job is abandoned in `RUNNING`, permanently.** The readiness document's
ground for (a) — that it *"matches the generic Job pattern exactly"* and *"adds nothing to
build"* — is wrong in the way that matters: the generic pattern does not restart a crashed Job,
it strands one. **(a) is not the cheap option; it is not an option at all.**

### 2. The consequence that reshapes (b): any re-run is a *different Job*

This is the finding an executor would otherwise hit after the first crashed run, and it strikes
two of (b)'s three components.

The retry path is not unspecified — it is specified and unbuilt. **FR-414** (`07`:103) rules
that *"A key whose Job reached `failed` is **released** — the next submission under it is a
**fresh Job** rather than the failed one handed back — which is what makes a scheduled period
retryable (FR-413)"*, and names its owner: *"Owner: whichever workstream builds
FR-413."* Combined with §1's empty terminal transition sets, this settles the shape of every
possible re-run:

**Whatever eventually re-runs a failed batch scoring run will be a new Job row with a new id.**

Therefore, from (b) as written:

- **"job-scoped staging" is struck.** A fresh Job would not find staging keyed on the dead Job's
  id, and would re-score everything — option (a)'s behaviour wearing (b)'s name.
- **"the Job's progress record names the last completed chunk" is struck**, on two independent
  grounds. The fresh Job's progress record is empty; and the progress record could not carry a
  checkpoint even within one run, because `JobProgress.update()` **silently drops writes inside
  a one-second throttle window** (`backend/src/app/worker/progress.py:102-103`,
  `_MIN_WRITE_INTERVAL_S: Final = 1.0`), and nothing anywhere reads a Job's own prior progress
  back. It is a forward-only display field feeding the SSE stream, and a lossy one by design.

**Ruled: the checkpoint is keyed on the run's content identity, never on the Job.** The
identity is the compiled bundle's content hash (FR-239), the Dataset Version reference, and
the chunk index — all of which a re-submission of the same batch reproduces exactly, because a
Dataset Version is immutable and a bundle hash is reproducible from its pins. That is what makes
a resumed run find its predecessor's work, and it is the platform's existing idiom rather than a
new one.

### 3. Resumability cannot live in `score_batch`, and the signature already said so

`03` §5.2:606–608 publishes:

```python
def score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *,
                chunk_rows: int = 100_000,
                progress: ProgressCallback | None = None) -> pl.LazyFrame
```

It takes a frame and returns a frame. It carries no Job identity, no output location and no
resume point, and `progress` is a write-only callback — nothing in that signature can be told
*"chunks 0–16 are done"*, and nothing in it can durably record that they are.

**Nor may it acquire one.** `.importlinter`'s `core-has-no-infrastructure` contract (ADR-703 /
DEP-3) forbids `pricing_core` importing `sqlalchemy`, `app`, `redis`, `boto3` and nine others,
with `allow_indirect_imports = false`, and `lint-imports` runs in the gate. A checkpoint ledger
is durable state; `pricing-core` structurally cannot hold it. FR-400 (`07`:89) already
allocates the work — *"`pricing-core` reports through the injected `ProgressCallback`
(ADR-703); the worker translates it into Job state."*

**So `score_batch` stays a pure, chunked, lazy transform** that reports progress and honours
cancellation, and the `score.batch` **handler** owns the durable side: the chunk manifest, the
staging parts, the skip-on-re-entry, and the single content-addressed parquet FR-253 makes
the citable result.

**This is also why (c) is dead twice over.** Its deduplication would have to live at the write
side, which is the handler's; it pays the full compute again, which is the cost chunk
checkpointing exists to avoid at NFR-493's 1 M risks/hour; and its own premise is worse than
the readiness document stated. That document called the row key *"not yet guaranteed unique"*.
It does not exist: `docs/contracts/schemas/scoring.schema.json`'s `ScoringResult` has no
`quote_id` property at all — the field lives only on the optional input `QuoteContext` and the
optional `Trace` sub-object — and `model_schema.scoring.ScoringResult` mirrors that. There is no
row key to deduplicate on.

### 4. Staging is scratch, deliberately not a blob artifact

FR-420 (`07`:114) makes blob GC *"reference-counted and conservative"*: a blob is deletable
*"only when no artifact references it and it is older than a configurable grace period (default
30 days)"*. This is shipped code, not an aspiration — `BlobStore.collect_garbage`
(`backend/src/app/platform/blobs.py`) selects candidates on `ref_count == 0` and
`created_at < cutoff`, with `retain`/`release` maintaining the count. **RL-888 established
that a referenced blob is never a GC candidate**; it established it for traces, and the code
fact it rests on is general.

So chunk parts held by a manifest would be permanently uncollectable, and even released ones
would occupy the store for 30 days after every crashed multi-million-row run. **Therefore chunk
parts are scratch: written outside the content-addressed store, released when the run they
belong to completes.** Only the concatenated output enters the blob store. The cleanup owner is
the handler, not FR-420's GC.

**The residue is stated rather than smoothed over.** Because §1's crashed Job never reaches a
terminal state, its scratch is not collected by that rule either, and because §2 keys the
manifest on content rather than on a Job, the scratch deliberately outlives the Job that wrote
it. It must therefore carry a creation time so an age-based sweep can collect it. That sweep is
part of the same absent platform mechanism as the trigger, and is named in the finding below
rather than built inside a rating slice.

### 5. FR-401 is untouched, and was never the authority here

FR-401 (`07`:90), verbatim: *"Jobs are **cancellable**. Cancellation is cooperative: the
callback signals cancellation and `pricing-core` returns at the next checkpoint. A cancelled Job
leaves no partially-visible artifact (`01` NFR-474)."* Every clause is scoped to
cancellation; the words "failed" and "crash" do not appear. The readiness and recovery
documents' reading is confirmed against the text: that clause never supplied crash-resume.
Scratch parts are never visible as an artifact, so cancellation semantics are unchanged.

### 6. What Slice 3 delivers, and how it is proven

**Slice 3 builds the ledger and the skip, not the trigger.** The handler writes each completed
chunk's part to scratch, records it in a content-keyed manifest, and on entry skips every chunk
the manifest already holds. That makes a batch run resumable the moment anything re-invokes it.

**The exit criterion is testable, and at the handler.** The frozen map
([`../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`](../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md):509–510) already requires a
*"resumability test (kill mid-chunk, resume from the last committed chunk)"*. That test drives
the **handler** directly — invoke, interrupt, re-invoke with the same parameters — which is both
the level the manifest lives at and how `backend/tests/test_worker.py` already exercises
handlers. It must not go through `run_job`, whose `QUEUED` guard (§1) would refuse the second
call. An executor who concludes the criterion is untestable has tested it at the wrong level.

**The test must assert work not repeated.** A resumability test that only checks the final
output passes under (a) as well, which would make FR-254's *"resumable"* vacuous. It must
assert both: **(i)** the chunks completed before the interruption are **not** re-scored —
observable by counting chunk invocations or rows scored on the resumed call, never by inspecting
the output — and **(ii)** the final parquet is byte-identical to an uninterrupted run over the
same input. Clause (i) is the one that distinguishes this ruling from (a). **The second run must
be a different Job id**, or the test proves only within-Job resume and misses §2 entirely.

### 7. Not decided here

The manifest's storage shape (a table, or scratch keys enumerated by prefix), the scratch area's
physical location, and the chunk-part format. All are implementation choices inside the handler
that do not change the shape of the plan. `JobRow.progress` is **excluded** as a candidate, per
§2.

**The ruling is overridden** if a build puts checkpoint state in `pricing-core`, keys a
checkpoint on a Job id, uses `JobRow.progress` as the ledger, or ships a resumability test that
passes without proving work was skipped.

**Disposition.** FR-254 takes a dated clarification recording where resumability lives, what
the checkpoint is keyed on, and that the re-run trigger is outside its scope. Mints no id.

---
