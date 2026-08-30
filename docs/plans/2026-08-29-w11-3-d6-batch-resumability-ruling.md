# W11 Slice 3 — D6: batch resumability, the trigger that is not there, and the step-evaluator sentence this exposed (2026-08-29)

**What this is.** The ruling on **D6**, raised in
[`2026-08-29-w11-3-batch-readiness-and-d6.md`](2026-08-29-w11-3-batch-readiness-and-d6.md) §3 as
the single unruled decision holding W11 Slice 3, plus the spec correction that testing its
premises exposed. D6's options and recommendation are the planner's; the decision is this
role's (`delivery-process.md` §3).

**Numbering continues at 31.** Rulings 1–5 are the prework record's, 6–13 the Slice 1 record's,
14–15 the Slice 2 record's, 16–21 the Slices 2–4 record's, 22 the rate-table maturity record's,
23–25 the Slices 3–4 record's, 26–27 the ruling-vs-plan-scope record's, 28–29 the algorithm-pin
maturity record's, and 30 the FR-RATE-65 attribution record's. Nine files, thirty rulings, no
gaps, re-derived by heading sweep at `28ec778` rather than taken from any record's own summary.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code.** FR-RATE-37 takes a dated clarification in
place — the shape Ruling 24 used for FR-RATE-38 — and `03` §5.2's prose is corrected.
`OQ-RATE-8` stays free.

**Read against `origin/main` at `28ec778`**, with `HEAD` identical, re-fetched immediately before
filing.

---

## Ruling 31 — D6: chunk-checkpointed resume, built in the Job handler and keyed on content, not on the Job

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

The retry path is not unspecified — it is specified and unbuilt. **FR-PLAT-64** (`07`:103) rules
that *"A key whose Job reached `failed` is **released** — the next submission under it is a
**fresh Job** rather than the failed one handed back — which is what makes a scheduled period
retryable (FR-PLAT-61)"*, and names its owner: *"Owner: whichever workstream builds
FR-PLAT-61."* Combined with §1's empty terminal transition sets, this settles the shape of every
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
identity is the compiled bundle's content hash (FR-RATE-24), the Dataset Version reference, and
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

**Nor may it acquire one.** `.importlinter`'s `core-has-no-infrastructure` contract (ADR-0001 /
DEP-3) forbids `pricing_core` importing `sqlalchemy`, `app`, `redis`, `boto3` and nine others,
with `allow_indirect_imports = false`, and `lint-imports` runs in the gate. A checkpoint ledger
is durable state; `pricing-core` structurally cannot hold it. FR-PLAT-8 (`07`:89) already
allocates the work — *"`pricing-core` reports through the injected `ProgressCallback`
(ADR-0001); the worker translates it into Job state."*

**So `score_batch` stays a pure, chunked, lazy transform** that reports progress and honours
cancellation, and the `score.batch` **handler** owns the durable side: the chunk manifest, the
staging parts, the skip-on-re-entry, and the single content-addressed parquet FR-RATE-36 makes
the citable result.

**This is also why (c) is dead twice over.** Its deduplication would have to live at the write
side, which is the handler's; it pays the full compute again, which is the cost chunk
checkpointing exists to avoid at NFR-RATE-5's 1 M risks/hour; and its own premise is worse than
the readiness document stated. That document called the row key *"not yet guaranteed unique"*.
It does not exist: `docs/contracts/schemas/scoring.schema.json`'s `ScoringResult` has no
`quote_id` property at all — the field lives only on the optional input `QuoteContext` and the
optional `Trace` sub-object — and `model_schema.scoring.ScoringResult` mirrors that. There is no
row key to deduplicate on.

### 4. Staging is scratch, deliberately not a blob artifact

FR-PLAT-20 (`07`:114) makes blob GC *"reference-counted and conservative"*: a blob is deletable
*"only when no artifact references it and it is older than a configurable grace period (default
30 days)"*. This is shipped code, not an aspiration — `BlobStore.collect_garbage`
(`backend/src/app/platform/blobs.py`) selects candidates on `ref_count == 0` and
`created_at < cutoff`, with `retain`/`release` maintaining the count. **Ruling 23 established
that a referenced blob is never a GC candidate**; it established it for traces, and the code
fact it rests on is general.

So chunk parts held by a manifest would be permanently uncollectable, and even released ones
would occupy the store for 30 days after every crashed multi-million-row run. **Therefore chunk
parts are scratch: written outside the content-addressed store, released when the run they
belong to completes.** Only the concatenated output enters the blob store. The cleanup owner is
the handler, not FR-PLAT-20's GC.

**The residue is stated rather than smoothed over.** Because §1's crashed Job never reaches a
terminal state, its scratch is not collected by that rule either, and because §2 keys the
manifest on content rather than on a Job, the scratch deliberately outlives the Job that wrote
it. It must therefore carry a creation time so an age-based sweep can collect it. That sweep is
part of the same absent platform mechanism as the trigger, and is named in the finding below
rather than built inside a rating slice.

### 5. FR-PLAT-9 is untouched, and was never the authority here

FR-PLAT-9 (`07`:90), verbatim: *"Jobs are **cancellable**. Cancellation is cooperative: the
callback signals cancellation and `pricing-core` returns at the next checkpoint. A cancelled Job
leaves no partially-visible artifact (`01` NFR-DATA-10)."* Every clause is scoped to
cancellation; the words "failed" and "crash" do not appear. The readiness and recovery
documents' reading is confirmed against the text: that clause never supplied crash-resume.
Scratch parts are never visible as an artifact, so cancellation semantics are unchanged.

### 6. What Slice 3 delivers, and how it is proven

**Slice 3 builds the ledger and the skip, not the trigger.** The handler writes each completed
chunk's part to scratch, records it in a content-keyed manifest, and on entry skips every chunk
the manifest already holds. That makes a batch run resumable the moment anything re-invokes it.

**The exit criterion is testable, and at the handler.** The frozen map
([`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md):509–510) already requires a
*"resumability test (kill mid-chunk, resume from the last committed chunk)"*. That test drives
the **handler** directly — invoke, interrupt, re-invoke with the same parameters — which is both
the level the manifest lives at and how `backend/tests/test_worker.py` already exercises
handlers. It must not go through `run_job`, whose `QUEUED` guard (§1) would refuse the second
call. An executor who concludes the criterion is untestable has tested it at the wrong level.

**The test must assert work not repeated.** A resumability test that only checks the final
output passes under (a) as well, which would make FR-RATE-37's *"resumable"* vacuous. It must
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

**Disposition.** FR-RATE-37 takes a dated clarification recording where resumability lives, what
the checkpoint is keyed on, and that the re-run trigger is outside its scope. Mints no id.

---

## Ruling 32 — `03` §5.2's "identical step evaluator" names an artifact that does not exist: the spec is wrong, the code is right

**The disagreement.** `03` §5.2:677–678 states: *"`score_one` and `score_batch` share the
identical step evaluator (FR-RATE-37); `score_batch` is a vectorised driver over the same
compiled graph, not a second engine."* Task 1.4 shipped, and **there is no shared step
evaluator.** `packages/pricing-core/src/pricing_core/rating/score.py:159` exports exactly
`__all__ = ["build_scoring_result", "score_one"]`; per-step evaluation happens inside the ZEN
engine (`bundle.decision`), which is not this repository's source. The module's own docstring
names the shared thing: `build_scoring_result`, *"the byte-identity Slice 3 proves is exactly
this function producing the same output from the same input, not two implementations that
happen to agree."*

The phrase is also inaccurate at the engine level: per Ruling 5, `score_one` reaches the engine
through `async_evaluate()` while `score_batch` stays plain `def` — different methods, not an
identical evaluator.

**Ruled: the spec is wrong, the code is right.** Under `CLAUDE.md` §0 this is a spec change, and
§5.2's sentence is corrected to name the shared tail. The second clause — *"a vectorised driver
over the same compiled graph, not a second engine"* — is accurate and is kept.

**Why this is not cosmetic.** The readiness document recorded that the frozen map's phrasing
*"invited the reading that a step-evaluation function would appear"*. The same wording in the
**specification** would send an implementer looking for a function that was never going to
exist, and FR-RATE-37's byte-identity proof is narrower and sharper than that reading suggests.
The frozen map carries the same phrasing at
[`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md):503 and is **not** edited — a filed
plan is frozen at its date (`CLAUDE.md` §2); the spec is the artifact that governs.

---

## Finding — D6 escaped because a filed record booked it as already ruled

Recorded because the mechanism, not the omission, is the reusable part. Two independent misses,
both checkable.

**1. A ruling record cited a ruling that says the opposite.**
[`2026-08-29-w11-slices-3-4-rulings.md`](2026-08-29-w11-slices-3-4-rulings.md):8–9 states:
*"Recovery items 1, 3 and 5 are already ruled (Rulings 10, 5 and 9 respectively)."* Recovery
item 3 is **Batch chunk/resume**
([`2026-08-29-w11-decision-points-recovery.md`](2026-08-29-w11-decision-points-recovery.md):106–108),
marked **"Status: recovered, unruled."** Ruling 5
(`2026-08-29-w11-prework-rulings.md`:431) is *"`score_one`'s real-time path:
`async_evaluate()`, not `evaluate()` + executor offload"*, and at `:472-476` it expressly
disclaims the scope it was cited for: *"`score_batch` (batch, Job-driven, no shared event loop
with concurrent requests to protect) is **not** ruled here."* The citation did not merely
mis-locate the ruling; the ruling it named refuses the question. Both records concern
`score_batch`, which is the likeliest route in.

**2. The catalogue built to prevent exactly this omits it.**
`2026-08-29-w11-slice1-rulings.md`:804–816 is a "Queued, not ruled" table enumerating
outstanding Slice 3 and 4 decision points. It carries the abort-threshold and batch-sampling
items that later became Rulings 24 and 25. **Batch resumability is not a row in it.**

**3. The sweep that later re-found it was narrower than it stated.** The readiness document
reports *"a narrower grep for `chunk` across the three W11 ruling records returns nothing at
all"*. The corpus is nine ruling records, not three, and `chunk` does occur in it exactly once —
at `2026-08-29-w11-prework-rulings.md`:475, inside Ruling 5's disclaimer, which is the very
ruling miscited in (1). The conclusion the document reached was right; the sweep behind it
covered a third of the corpus. Per `CLAUDE.md` §13, a reference carries its scope: *"the three
W11 ruling records"* named a corpus that was not the one that mattered.

**Not corrected in place** — those are filed plans, frozen at their date (`CLAUDE.md` §2). This
entry is the correction.

---

## Finding for the lead — nothing re-runs a crashed Job; it is specified, owned, and unbuilt

**Raised, not ruled — and it is not a new capability.** §1 establishes that a Job crashing
mid-run is abandoned in `RUNNING`. §2 establishes that the fix is already specified: FR-PLAT-64
(`07`:103) rules how a terminally failed Job's key is released so the next submission is a fresh
Job, and states its own owner — *"Owner: whichever workstream builds FR-PLAT-61."* FR-PLAT-11
carries the failure-and-retry half that FR-PLAT-9 does not. Neither is built.

**So the disposition is not an `OQ-`.** This is a specified requirement with a named owner that
has not been implemented — a roadmap and scheduling question, which `CLAUDE.md` §12 puts with
the lead, not a design question open to this role. Raising an open question would imply the
design is undecided, and it is not.

**Scope is wider than batch scoring.** The guard, the empty terminal transition sets and the
absent reaper are generic: `model.fit`, `data.validate` and `rating.compile` are in exactly the
same position. Only 9 of the 22 `JobKind` values have a registered handler at all, so the
exposure grows with each one added.

**Consequence for the W11 close, which is the part with a date.** FR-RATE-37's *"resumable"*
clause is **not fully discharged by Slice 3** even when Slice 3 is complete and its resumability
test passes: the manifest will exist and be proven, and nothing in production will invoke it.
Under `CLAUDE.md` §13 that clause takes **deferred with an owner** — the owner being whoever
builds FR-PLAT-61/64 — not *delivered*. Booking FR-RATE-37 as delivered would put a resumability
guarantee in the roadmap that the repository does not have.

The age-based sweep for orphaned scratch (§4) belongs with the same work.

---

## Verification

- **Tree:** `28ec778`; `git rev-parse HEAD` equal to `git rev-parse origin/main`, re-fetched
  immediately before filing rather than carried from the start of the session.
- **Every code citation was read at that tree**, not taken from the readiness document: the
  `QUEUED` guard and the `RUNNING` transition in `backend/src/app/worker/tasks.py`;
  `task_acks_late` in `celery_app.py`; the five routes in `backend/src/app/api/jobs.py`;
  `VALID_TRANSITIONS` in `model_schema/jobs.py`; `_MIN_WRITE_INTERVAL_S` and `update()`'s early
  return in `backend/src/app/worker/progress.py`; the `core-has-no-infrastructure` contract in
  `.importlinter`; `__all__` and the module docstring in `score.py`.
- **The reaper absence** was established with the marker class rather than one spelling
  (`reaper`, `reap_`) across `backend/`, `packages/` and `07-platform.md`; the single hit is a
  comment. The positive control is that the same style of sweep returns real implementations for
  every other mechanism cited here — `collect_garbage`, `retain`/`release`, `register_handler`.
- **FR-RATE-36/37/38, FR-PLAT-8/9/11/20/61/64 were read as whole rows**, including dated
  amendments, since an amendment can invert the clause before it. FR-RATE-37 carries none;
  FR-RATE-38 carries Ruling 24's; FR-PLAT-64 is itself an appended 2026-08-23 decision.
- **The ruling corpus was re-derived**, not taken from a record's own summary: nine files,
  Rulings 1–30, no gaps. Three unrelated pre-W11 ledger documents restart their own "Ruling N"
  numbering, so every citation here is filename-qualified.
- **Rulings 23, 24 and 25 were read in full before ruling**, so this contradicts none of them.
  Ruling 25's exclusion of a batch sampling policy is untouched — nothing here gives
  `score_batch` one. Ruling 23's referenced-blob finding was made for traces; §4 relies on the
  shipped GC code it cites, and says so rather than borrowing the ruling's scope.
- `python3 scripts/audit-docs.py` — run before commit.
- Mints no `FR-`/`NFR-`/`OQ-` id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row. **D6 is a decision point, not an open
  question** — the treatment DP1, DP2 and D2–D5 each received.

---

## Addendum to Ruling 31, filed 2026-08-29 after `9942800` — two citation errors in §1 and §6

**The decision is unchanged. Two of its citations were wrong, and the correction to one of
them strengthens the ruling rather than weakening it.** Raised by the lead as **F-W11-3-1**
(`2026-08-29-w11-3-batch-scoring.md`, merged `02679d0`), which caught the first; the second is
this role's own and was found while verifying the first. The original text above is left
standing — this addendum is the correction, per `CLAUDE.md` §2.

**Error 1 — the test precedent does not exist.** §6 says the resumability test drives the
handler directly, *"which is both the level the manifest lives at and how
`backend/tests/test_worker.py` already exercises handlers."* **It does not.** That file calls
`execute_job(database, job.id)` throughout — 17 call sites at `9942800` — and never invokes a
handler function itself. Its handlers are locally defined fakes registered into `HANDLERS` and
then driven through the lifecycle.

*How the error was made, since that is the reusable part.* The file's own docstring reads:
*"`execute_job` is exercised **directly** rather than through a broker: the lifecycle is the
behaviour worth testing."* **"Directly" there means without Celery and Redis — not at handler
level.** The word was read on the wrong axis. A qualifier like "directly" only means something
against a stated alternative, and that docstring states its alternative explicitly.

**Error 2 — the guard was attributed one level too high.** §1 says *"`run_job` transitions the
Job to `RUNNING` before calling the handler, and guards its own entry"*, and §6 says the test
*"must not go through `run_job`"*. Both should name **`execute_job`**
(`backend/src/app/worker/tasks.py:79`), which is where the `QUEUED` guard and the `RUNNING`
transition actually live.

`run_job` is not a phantom — it exists at `tasks.py:266`, but it is the **Celery task**,
`@celery.task(name=TASK_RUN_JOB)`, whose own docstring calls it *"Adapter: bind the trace, then
run the lifecycle"*, and the module docstring says *"the task is a five-line adapter and this is
where the behaviour lives."* So §1's described behaviour is correct and reaches the guard
transitively; only the attribution is wrong. **§6's instruction should read "must not go through
`execute_job`"**, because that — not the Celery task — is the level a test would realistically
call, and the level the existing suite does call.

*How this error was made.* The body was read with `sed -n '80,140p'`, starting one line below
the `def` at `:79`. **Reading a function's body without its signature line yields correct
behaviour attached to a guessed name** — the guard's code was quoted exactly and its owner
named wrongly in the same paragraph.

**Why Error 1's correction strengthens §1.** The claim that failed was a *precedent* claim, and
its failure is itself evidence. **There is no precedent in this repository for invoking a
handler directly, because nothing in this platform has ever needed to run the same Job twice** —
which is precisely what §1 ruled. The missing neighbour is corroboration, and by
[`README.md`](README.md)'s *"a missing neighbour is a scope finding"* it belongs in the Slice 3
plan's scope section: the resumability test is writing a new test shape, not following one.

**What an executor should take from this.** §6's operative instruction stands unchanged in
substance — the resumability test invokes the handler function itself, interrupts, and
re-invokes with the same parameters, and must not route either call through `execute_job`,
whose `QUEUED` guard would refuse the second. It is a new test shape for this suite. **The
override conditions in §7 are untouched.**
