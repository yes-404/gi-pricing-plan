---
id: RL-922
family: ruling
title: the remediation is ruled **into** the reopen, and NFR-489's verdict is ruled **out** of it: they are two different things and the record must not merge them
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-reopen-scope-and-batch-frame-contract-rulings.md
---

# NFR-489's remediation, and `score_batch`'s frame contract (2026-08-30)

**What this is.** Two rulings. The first was assigned to the decision-maker by the maintainer
by name, after the lead put three scope shapes to them and was told *"let decision maker to
make decision"*: does NFR-489's remediation belong inside the WK-671 reopen. The second is a
decision point the executor hit inside WK-671 Task 3A and flagged rather than let pass: it
designed `score_batch`'s input/output row schema itself, because `03` §5.2 fixes the
function's signature and nothing anywhere fixes a row shape, and it recorded that schema in a
module docstring.

**Numbering continues at 42, 43.** Rulings 1–30 are catalogued in
[`RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md`](RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md);
31–32 there, 33 in
[`RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md`](RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md),
34 in
[`RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md`](RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md),
35 in
[`RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`](RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md),
36 in
[`RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md`](RL-00917-the-clause-reaches-persistence-and-nfr-499-is-the-defective-one.md),
37 in
[`RL-00915-option-c-the-compiled-bundle-s-blob-key-becomes-part-of-the-version-s-own-metadata.md`](RL-00915-option-c-the-compiled-bundle-s-blob-key-becomes-part-of-the-version-s-own-metadata.md),
38 in
[`RL-00924-option-b-one-computation-taught-to-answer-the-question-it-already-claims-to-answer.md`](RL-00924-option-b-one-computation-taught-to-answer-the-question-it-already-claims-to-answer.md),
39–41 in
[`RL-00921-a-ref-may-not-be-served-from-the-memo-without-a-metadata-read-and-it-does-not-need-to-be-the-content-hash-is-already-in-hand-after-the-first-read-and-is-discarded.md`](RL-00921-a-ref-may-not-be-served-from-the-memo-without-a-metadata-read-and-it-does-not-need-to-be-the-content-hash-is-already-in-hand-after-the-first-read-and-is-discarded.md).
**RL-921 was verified as the highest existing** by enumerating every `## Ruling N` heading
under `docs/plans/`, not taken from the dispatch.

**Read against `origin/main` at `5c1a6a0`** for docs and backend code, re-fetched at
2026-08-30T12:20Z in the same command that read the clock; and against commit `7b88d0d` on
branch `feat/w11-3a-score-batch` for RL-923's subject, which is not on `main`. The branch
is one commit ahead of `8fd48b7` and its change set is
`packages/pricing-core/src/pricing_core/rating/score.py` (+279/−15) and
`packages/pricing-core/tests/test_rating_score_batch.py` (+250), listed with
`git diff --stat origin/main...feat/w11-3a-score-batch` rather than inferred from the message.

**Mints no `FR-`/`NFR-`/`OQ-` id.** RL-923 *requires* one `docs/specs/` edit and says
explicitly why this record does not carry it.

**Nothing here was taken from the lead's relay.** The dispatch's account of RL-921's
load-bearing claim was re-verified at source before either ruling was drafted — see
§Verification.

---

## 0. Two constraints the dispatch offered that do not hold, checked before they were weighed

**`CLAUDE.md` §0's "do not build ahead of the phase" does not bear on RL-922.** The
dispatch named it as a constraint. **WK-674 is in Phase 2, the same phase as WK-671** —
`docs/roadmap.md` §7's workstream table lists WK-668 through WK-675 and WK-690 under *"Phase 2 — Rating
Engine"*, with WK-674 as *"Deployment: environments, atomic switchover, rollback, shadow"*. Moving
work between WK-671 and WK-674 is therefore a **workstream-scope** question, not a phase-boundary
one, and §0's later-phase row is not engaged in either direction. Recorded because a rule
cited on the wrong side of a decision is worse than no rule: it makes the cautious answer look
compelled when it is only cautious.

**Shape (c) — remediate but defer the re-measurement — is not open, and is not refused here
either.** It was already foreclosed by a standing ruling. RL-921 §5: *"the re-measurement
belongs with it, since a change made for latency that is not re-measured is an assertion."*
The lead reached the same answer by a different route (`CLAUDE.md` §13 forbids booking an
unmeasured optimisation) and both are right, but the point is that (c) required no new
decision. RL-922 treats the live question as the one RL-921 §5 actually left open:
whether the change belongs *"to the reopened WK-671 or to whichever slice next touches the
scoring path"*.

---

## RL-922 — the remediation is ruled **into** the reopen, and NFR-489's verdict is ruled **out** of it: they are two different things and the record must not merge them

**Ruled.** Neither (a) nor (b) as put. The **code change** of RL-921 §2 lands inside the
reopen, carried by Slice 3's Task 3B. The **NFR-489 re-measurement** that would settle the
requirement does **not** land inside the reopen, is not attempted, and stays owned by WK-674.
NFR-489's verdict does not move: it remains *measured and FAILING*.

This widens the scope RL-919 §1 fixed. **Said plainly, as the dispatch asked: yes, this
adds work your predecessor's ruling did not include.** §5 below states exactly what it adds
and what it does not, because the difference is the whole ruling.

### 1. Why (b) as posed is not buildable, on the record's own numbers

(b) was *"remediate and re-measure inside the reopen"*. The re-measurement it means cannot be
performed here. RL-921 §4, verified at source: *"It does not establish 200 rps.
NFR-489's budget is at 200 rps per replica; the measurement never reached it, on a shared
box. **A re-run needs a dedicated host**, and one pass will not establish a verdict near a
bound."* The original measurement's own record carries the same two limits — one pass, and a
shared 4-core box with 1-minute load rising to 10.76 during the run — and voids its own 200 rps
rungs because the generator issued 149.5 and 142.1.

Nothing about the host has changed. A re-measurement run inside the reopen would reproduce the
void condition and hand the re-close a number that reads like a verdict and is not one. That is
the failure `CLAUDE.md` §13 names — *"NFRs are measured, not asserted"* — arriving through a
measurement rather than through an assertion, which is harder to spot.

### 2. Why (a) is not the honest answer either

Deferring the whole thing leaves four things standing at the re-close, and they compound:

- **A hard target failing, with a known, cheap, correct-by-construction removal of about 60 %
  of its measured cost, deliberately not taken.** RL-921 §4: `_fetch_bundle` is 36.574 ms of
  a 60.959 ms mean handler at the cleanest rung.
- **Two register rows carried forward *unowned*.** `docs/findings/register.md` gives both F50 and
  F51 the resolution *"carry forward, unowned"*. `CLAUDE.md` §14 admits three resolutions for
  an open finding — the close fixes it, it is carried forward **with a named owner**, or it is
  accepted. *Unowned* is none of them. Two WK-671 findings therefore currently lack a
  §14-conforming resolution, and the reopen is the last moment at which WK-671 can give them one.
- **F50's own filed disposition says the consequence out loud**: *"NFR-489 remediation
  (RL-921 §2, which would touch this same module) is explicitly not part of the WK-671 reopen
  … so **nobody is currently positioned to fix it as a side effect of other work**."* That
  sentence was written as a description of a state. It is also an argument, and (a) makes it
  permanent.
- **The next author of that module reads the false sentence while writing against it.** F50 is
  a docstring at `backend/src/app/platform/bundle_slot.py:28-31` arguing that a ref's mapping
  *"cannot change under the memo"*. RL-921 §3 established it is false and safe only because
  `hash_for` is read solely on the degradation branch. Task 3B is being written now and must
  resolve a `rating_version_ref` to a `CompiledBundle`; the only implementation of that in the
  repository is `_compiled_for`/`_fetch_bundle` in `backend/src/app/api/score.py`, whose
  neighbour is that docstring.

### 3. The positive reason: the reopen already has to touch this seam

`docs/plans/PL-00849-wk-671-slice-3-batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md` describes Task 3B's *"Interfaces — Consumes"*
as *"3A's `score_batch`; `BlobStore.put` for the final output; `ProgressCallback` plumbing per
FR-400."* **It names no bundle-resolution interface at all**, and grepping that plan for
`load_bundle`, `_compiled_for`, `_fetch_bundle` and `resolve_rating_version_ref` returns
nothing — the only `CompiledBundle` hits are the three copies of `score_batch`'s signature.

That is a gap in the plan, not evidence of separation. A batch handler receives a Rating
Version reference and must end up holding a `CompiledBundle`; `CompiledBundle` is not
serialisable (FR-243) and cannot arrive as a Job argument. So 3B will either **reuse**
`api/score.py`'s resolution — touching the module RL-921 §2 changes — or **write a second
resolver**, which is the shape `CLAUDE.md` §2 forbids in its own words: *"A shape defined twice
will diverge, and in a pricing platform a diverged shape is a mispricing."*

**Ruled: 3B reuses it, and reuses it in the form RL-921 §2 specifies.** That is why the
remediation belongs to this slice rather than to a later one: the slice has to arrive at this
code regardless, and the only choice is whether it arrives before or after the fix.

### 4. What is measured, and what that measurement may and may not be called

The change lands with a **component-level delta measurement of its own predicate**, not with an
NFR verdict. Concretely:

- `_compiled_for` p99 on a slot **hit** against `_compiled_for` p99 on the **current** full
  path, same tree, same host, same harness, both conditions in the same run.
- The report **names its tree, its host, its pass count and its ref cardinality**
  (`CLAUDE.md` §13: *"A reference carries its scope and its measurement"*). Ref cardinality is
  not optional detail: RL-921 §4 records that `backend/src/app/config.py:172` defaults
  `bundle_slot_capacity` to 1, so *"with capacity 1 and more than one ref in play the slot
  thrashes and every request pays the full path"*. A delta measured over one ref is a
  measurement of a single-ref workload and must say so.
- **`bundle_slot_capacity` is not raised.** RL-921 §4 left it unset and its own code comment
  requires a latency-harness measurement to raise it. Raising it here would be the guess §0
  forbids.

**What this measurement is not.** It is not a re-measurement of NFR-489, it is not run at
200 rps, it is not run on a dedicated host, and it does **not** fire RL-921 §4's trigger —
*"if a re-measurement with the blob read removed still fails the 15 ms limb, that is the
trigger that puts NFR-489 itself in question"*. That trigger is armed by a **requirement**
re-measurement on a host that can carry one, and a component delta on a shared 4-core box is
not it. Reading the trigger as fired by this delta would answer the requirement's own question
from numbers that cannot support it.

### 5. The boundary that keeps this from being a scope widening in the sense that matters

**The reopen's requirement scope is unchanged.** It stays FR-253, FR-254, FR-259
and NFR-500 — RL-919 §1's list, restated in the closure record §9. **NFR-489 is not
added to it.** No `FR-`/`NFR-` id moves, no requirement gains an owner, and the §13 closure
audit's scope is the same set it was before this ruling.

What is added is a **code change that discharges a carried-forward finding**, plus owners for
two register rows. That is `CLAUDE.md` §14's own machinery for open findings, not a new
deliverable. The distinction is load-bearing at the re-close: the acceptance condition this
work joins is *"the code change and its delta measurement are complete"*, and it is **never**
*"NFR-489 passes"*.

**The 2026-08-30 amendment to `docs/rulings/RL-00918-wk-671-reopen-the-maintainer-s-direction-recorded-2026-08-30.md` §4 anticipated
this ruling and is engaged by it.** It records that *"if a further slice is ruled into the
reopen it joins this condition automatically … the condition is not met until it too is
complete."* Read against §5's boundary: what joins Condition 1 is the code change and its delta
measurement. Nothing in this ruling makes NFR-489's *passing* a precondition of the
re-close, and reading it that way would make WK-671 unclosable on the hardware available.

### 6. The sentence the record must not be able to produce

**Removing the blob read does not make NFR-489 pass, and no artifact produced under this
ruling may imply that it does.** The evidence, unchanged by anything here: the without-GBM limb
reads component p99 **23.027 ms against a 15 ms budget with the fetch already excluded**, and
the with-GBM component p99 is 33.468 ms, inside 50 ms by only 1.49×. RL-921 neither amended
NFR-489 nor showed it reachable, and this ruling does neither.

Three concrete prohibitions follow, so this is testable rather than hortatory:

- **`docs/closures/CR-00927-work-item-record-wk-671-scoring.md` §4's NFR-489 row and §6's carry-forward row are not
  edited.** They are the record as at the close (RL-919 §2). The remediation is reported in
  the appended reopen section, under the finding it discharges.
- **The re-close's NFR-489 verdict is the same verdict**: measured and failing. A close
  reporting it any other way has broken this ruling.
- **The delta measurement is published with its host and pass count attached**, so a later
  reader cannot lift the number out of its condition.

### 7. Disposition and owners

| Item | Owner | Applied where |
|---|---|---|
| RL-921 §2's code change (version-row read stays; blob PK lookup, ~2,039,114 B object read and full `model_validate_json` leave the hot path) | WK-671 Slice 3, Task 3B | `backend/src/app/api/score.py` `_compiled_for`/`_fetch_bundle` |
| The component delta measurement of §4, with tree, host, pass count and ref cardinality | WK-671 Slice 3, Task 3B | filed with the change |
| **F50** — the `bundle_slot.py:28-31` docstring correction | WK-671 Slice 3, Task 3B | the register row's *unowned* is superseded by this line |
| **F51** — the research note's false premise at `docs/research/w11-task-2d-nfr-rate-1-full-path.md:74-75` | WK-671 Slice 3, Task 3B, as a dated correcting annotation quoting what it supersedes | the register row's *unowned* is superseded by this line |
| NFR-489's requirement re-measurement, on a dedicated host, more than one pass | **WK-674** — unchanged | not WK-671 |
| `bundle_slot_capacity`, a TTL, a refresh/poll/pub-sub channel | **WK-674** — unchanged, RL-882 clause 4 | not WK-671 |

**F51's correction is an annotation, not an edit.** The register row already reasons that a
merged research note *"needs the same ruling-then-file path RL-921 itself came from, not a
register row alone"*. This ruling is that path. The note's **measurements are not in question**
and are not to be touched — RL-921 §1 re-read every one of them and each held; only the
premise sentence at `:74-75` is wrong.

### 8. Override conditions

This ruling is overridden if the delta measurement is reported without its host and pass
count; if any artifact describes NFR-489 as passing, improved to passing, or re-measured; if
RL-921 §4's 15 ms trigger is treated as fired; if `bundle_slot_capacity` is raised, or a TTL
or invalidation channel added, under cover of this work; or if the closure record's §§1–8 are
edited rather than appended to.

---
