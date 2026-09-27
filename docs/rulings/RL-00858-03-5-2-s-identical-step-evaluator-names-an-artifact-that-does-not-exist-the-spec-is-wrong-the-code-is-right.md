---
id: RL-858
family: ruling
title: `03` §5.2's "identical step evaluator" names an artifact that does not exist: the spec is wrong, the code is right
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

## RL-858 — `03` §5.2's "identical step evaluator" names an artifact that does not exist: the spec is wrong, the code is right

**The disagreement.** `03` §5.2:677–678 states: *"`score_one` and `score_batch` share the
identical step evaluator (FR-254); `score_batch` is a vectorised driver over the same
compiled graph, not a second engine."* Task 1.4 shipped, and **there is no shared step
evaluator.** `packages/pricing-core/src/pricing_core/rating/score.py:159` exports exactly
`__all__ = ["build_scoring_result", "score_one"]`; per-step evaluation happens inside the ZEN
engine (`bundle.decision`), which is not this repository's source. The module's own docstring
names the shared thing: `build_scoring_result`, *"the byte-identity Slice 3 proves is exactly
this function producing the same output from the same input, not two implementations that
happen to agree."*

The phrase is also inaccurate at the engine level: per RL-868, `score_one` reaches the engine
through `async_evaluate()` while `score_batch` stays plain `def` — different methods, not an
identical evaluator.

**Ruled: the spec is wrong, the code is right.** Under `CLAUDE.md` §0 this is a spec change, and
§5.2's sentence is corrected to name the shared tail. The second clause — *"a vectorised driver
over the same compiled graph, not a second engine"* — is accurate and is kept.

**Why this is not cosmetic.** The readiness document recorded that the frozen map's phrasing
*"invited the reading that a step-evaluation function would appear"*. The same wording in the
**specification** would send an implementer looking for a function that was never going to
exist, and FR-254's byte-identity proof is narrower and sharper than that reading suggests.
The frozen map carries the same phrasing at
[`../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`](../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md):503 and is **not** edited — a filed
plan is frozen at its date (`CLAUDE.md` §2); the spec is the artifact that governs.

---

## Finding — D6 escaped because a filed record booked it as already ruled

Recorded because the mechanism, not the omission, is the reusable part. Two independent misses,
both checkable.

**1. A ruling record cited a ruling that says the opposite.**
[`RL-00890-d5-fr-258-259-are-not-silent-about-batch-and-no-open-question-is-raised.md`](RL-00890-d5-fr-258-259-are-not-silent-about-batch-and-no-open-question-is-raised.md):8–9 states:
*"Recovery items 1, 3 and 5 are already ruled (Rulings 10, 5 and 9 respectively)."* Recovery
item 3 is **Batch chunk/resume**
([`../plans/PL-00851-wk-671-five-decision-points-recovered.md`](../plans/PL-00851-wk-671-five-decision-points-recovered.md):106–108),
marked **"Status: recovered, unruled."** RL-868
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
reports *"a narrower grep for `chunk` across the three WK-671 ruling records returns nothing at
all"*. The corpus is nine ruling records, not three, and `chunk` does occur in it exactly once —
at `2026-08-29-w11-prework-rulings.md`:475, inside RL-868's disclaimer, which is the very
ruling miscited in (1). The conclusion the document reached was right; the sweep behind it
covered a third of the corpus. Per `CLAUDE.md` §13, a reference carries its scope: *"the three
WK-671 ruling records"* named a corpus that was not the one that mattered.

**Not corrected in place** — those are filed plans, frozen at their date (`CLAUDE.md` §2). This
entry is the correction.

---

## Finding for the lead — nothing re-runs a crashed Job; it is specified, owned, and unbuilt

**Raised, not ruled — and it is not a new capability.** §1 establishes that a Job crashing
mid-run is abandoned in `RUNNING`. §2 establishes that the fix is already specified: FR-414
(`07`:103) rules how a terminally failed Job's key is released so the next submission is a fresh
Job, and states its own owner — *"Owner: whichever workstream builds FR-413."* FR-403
carries the failure-and-retry half that FR-401 does not. Neither is built.

**So the disposition is not an `OQ-`.** This is a specified requirement with a named owner that
has not been implemented — a roadmap and scheduling question, which `CLAUDE.md` §12 puts with
the lead, not a design question open to this role. Raising an open question would imply the
design is undecided, and it is not.

**Scope is wider than batch scoring.** The guard, the empty terminal transition sets and the
absent reaper are generic: `model.fit`, `data.validate` and `rating.compile` are in exactly the
same position. Only 9 of the 22 `JobKind` values have a registered handler at all, so the
exposure grows with each one added.

**Consequence for the WK-671 close, which is the part with a date.** FR-254's *"resumable"*
clause is **not fully discharged by Slice 3** even when Slice 3 is complete and its resumability
test passes: the manifest will exist and be proven, and nothing in production will invoke it.
Under `CLAUDE.md` §13 that clause takes **deferred with an owner** — the owner being whoever
builds FR-413/414 — not *delivered*. Booking FR-254 as delivered would put a resumability
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
- **FR-253/254/255, FR-400/401/403/420/413/414 were read as whole rows**, including dated
  amendments, since an amendment can invert the clause before it. FR-254 carries none;
  FR-255 carries RL-889's; FR-414 is itself an appended 2026-08-23 decision.
- **The ruling corpus was re-derived**, not taken from a record's own summary: nine files,
  Rulings 1–30, no gaps. Three unrelated pre-WK-671 ledger documents restart their own "Ruling N"
  numbering, so every citation here is filename-qualified.
- **Rulings 23, 24 and 25 were read in full before ruling**, so this contradicts none of them.
  RL-890's exclusion of a batch sampling policy is untouched — nothing here gives
  `score_batch` one. RL-888's referenced-blob finding was made for traces; §4 relies on the
  shipped GC code it cites, and says so rather than borrowing the ruling's scope.
- `python3 scripts/audit-docs.py` — run before commit.
- Mints no `FR-`/`NFR-`/`OQ-` id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row. **D6 is a decision point, not an open
  question** — the treatment DP1, DP2 and D2–D5 each received.

---

## Addendum to RL-857, filed 2026-08-29 after `9942800` — two citation errors in §1 and §6

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
[`../plans/README.md`](../plans/README.md)'s *"a missing neighbour is a scope finding"* it belongs in the Slice 3
plan's scope section: the resumability test is writing a new test shape, not following one.

**What an executor should take from this.** §6's operative instruction stands unchanged in
substance — the resumability test invokes the handler function itself, interrupts, and
re-invokes with the same parameters, and must not route either call through `execute_job`,
whose `QUEUED` guard would refuse the second. It is a new test shape for this suite. **The
override conditions in §7 are untouched.**
