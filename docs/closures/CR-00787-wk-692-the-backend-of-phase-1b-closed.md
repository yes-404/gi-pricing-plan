---
id: CR-787
family: closure
kind: work
title: WK-692 — the backend of Phase 1b: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-24
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-692 — the backend of Phase 1b: closed 2026-08-24

<!-- GATE — DISCHARGED 2026-08-24 at 60f6e46, when this heading was written.
     Preserved rather than deleted: the pattern's design rationale outlives the gate it
     guarded, and the next person to write a workstream-closure tripwire needs it. What
     follows described the check while it was armed; it is now a record of how it was built.
     Check, two parts (validated on deliberately broken input, 2026-08-24 at c024f3e;
     re-validated 2026-08-24 on an 11-line fixture: 4 intended positives all fire, 7
     negatives all hold; re-run at 60f6e46 immediately before this record was written —
     live 0, positive control 1, negative control 0).
     BOTH PARTS READ origin/main, NOT THE WORKING TREE. The claim being made is about
     main; a grep of `docs/roadmap.md` reads whatever tree it happens to run in, and
     parallel sessions here run in worktrees that are routinely a commit apart. That
     exact confusion misread the W32-2 attribution line on 2026-08-24. Pin the source,
     not just the command.
     PIPES ARE AT LINE ENDS, NOT LINE STARTS, AND MUST STAY THERE. audit-docs.py's
     table check does NOT skip HTML comments: a continuation line beginning `|` is
     parsed as a table row, and `| grep ... \` reads as a 0-cell row under a 1-cell
     header. It failed exactly that way when this record was first written.
     PART 1 - TRIPWIRE, loose and fail-safe, fires on ANY WK-692 heading:
       git show origin/main:docs/roadmap.md |
         grep -nE '^#+ WK-692[a-z]?([ :—]|$)' |
         grep -vF "the closure proposal's decisions"
       EMPTY     => gate holds, WK-692 not closed.
       NON-EMPTY => READ THE LINE. It does NOT mean closed: it fires on
                    "### WK-692 - the workspace slice *(in progress, not closed)*" just as
                    readily. It is a summons to read, never a verdict.
     PART 2 - AFFIRMATIVE, strict and date-anchored, only after Part 1 fires:
       git show origin/main:docs/roadmap.md |
         grep -nE '^#+ WK-692[a-z]?([ —].*)?: closed [0-9]{4}-[0-9]{2}-[0-9]{2}'
     Both empty at c024f3e and at 6cb9297; Part 2 fires on this heading, as intended.
```
     WHY [a-z]? RATHER THAN \b, and why the reason matters. `W32a` is how a split
     remainder would be named - split-then-letter is exactly how WK-692 came out of WK-664 -
     and \b MISSES `### W32a - split remainder: closed ...`, a false NEGATIVE on the
     case the pattern exists to catch. \b ALSO produces a false POSITIVE: the
     proposed form was `^#+ WK-692\b.*: closed <date>` - PERMISSIVE body - and on the
     fixture it fires on W32-7, W32-11 and W32-1b. CORRECTION, 2026-08-24: this
     paragraph previously recorded the opposite, that the false-positive charge did not
     reproduce. That test substituted the CONSTRAINED body `^#+ WK-692\b([ —].*)?: closed`
     into the proposal - a pattern nobody put forward - and the constrained separator,
     not \b, is what excluded the slices. The original charge was correct; the
     retraction was the defective write, and it was checked by the party it absolved.
     Both faults of \b therefore stand: it misses W32a AND, in the form actually
     proposed, admits every slice. Recorded because a gate whose rationale is false
     teaches the next reader something untrue even while it works.
     WHAT IS ACTUALLY LOAD-BEARING - DO NOT SIMPLIFY ([ —].*)? TO .*
     The separator group is the ONLY thing excluding slice headings. The letter class
     does none of that work: `^#+ WK-692[a-z]?.*: closed …` fires on W32-7 AND W32-11 AND
     W32a, exactly as `^#+ WK-692\b.*: closed …` fires on W32-7 and W32-11. Both letter
     classes are safe ONLY in company with the constrained separator. The final control
     run at 60f6e46 measured exactly this: the permissive form scores 2 on an input the
     real pattern scores 0 on, so the separator's necessity is a number, not an argument.
     So the two pieces do different jobs and neither substitutes for the other:
       ([ —].*)?  excludes slices   - SAFETY. Relaxing it opens the gate.
       [a-z]?     admits W32a       - COVERAGE. Dropping it makes the gate go quiet.
     A future reader trimming the separator to `.*` as over-engineering would believe
     [a-z]? still keeps slices out. It does not, and the gate would then report the
     workstream closed when a slice closed - releasing the whole WK-664 chain.
```
*Fenced 2026-09-04 under RL-1044 §5.1; value unchanged.*
     WHY IT IS SHAPED THIS WAY. Hash depth is not stable in this file and cannot be keyed on:
     WK-661's slice records are ### while WK-692's are ####, so depth varies by WORKSTREAM, not by
     kind of record. And a keyword filter is worse than useless - `grep -i closed` over WK-661
     returns 11 hits of which exactly ONE (:546) is a real closure, because ten slice records
     carry the literal string "(in progress, not closed)".
     THE HEADING USED, matching all five prior closure records (:546 WK-661, :801 WK-667, :988 WK-663,
     :1093 WK-666, :1146 WK-660) - three hashes, em-dash, ": closed YYYY-MM-DD".
     The filter on :3685 is a LITERAL string; rewording that heading makes Part 1 fire on it.
     That is the safe direction, and whoever rewords it owns the filter.

     CORRECTION, 2026-08-25: the second validation point above cites `6cb9297`, which
     is not an ancestor of origin/main — a pre-squash branch tip that never landed (it
     resolves in no clone). `c024f3e` and the re-run point `60f6e46` are both on main,
     and the two-part check was re-run at the latter immediately before this record
     was written; the discharge rests on those two valid states. -->

**Every `:NNNN` citation in this record is against this file at `60f6e46`, the last feature SHA. The closing commit is `e2ae7c6` (#165).**

**And the delta rule this record states is applied to itself — by refusing to state a
resulting line number at all.** Writing this record inserts several hundred lines above
`:546`, so in any tree containing it every citation below `:546` is offset by that insertion
and every citation above is unchanged. **The offset is deliberately not written down.** Two
attempts to write it were made and both were wrong within one edit: the first measured the
insertion before the paragraph recording it existed, and the correction was falsified the
same way by its own five lines. **A number that changes when you write it down cannot be
written down** — it is a fixed point, not a fact, and the two failed attempts are left
recorded because the shape is worth more than the number. Re-derive instead:

```
git show 60f6e46:docs/roadmap.md | grep -n '<the phrase>'   # the cited tree
grep -n '<the phrase>' docs/roadmap.md                       # the tree you are in
```

The difference must equal `git show --stat` for the commit that added this record. If it
does not, you have found a real disagreement rather than drift — which is the entire reason
the rule is stated instead of the offset.
Stated once rather than repeated, because this record's own method finding is that a locator
without a tree is not a citation — W32-7 moved the rows below `:4380` by 63 lines while this
record was being drafted, and several draft citations were stale by the time it was written.

**Preconditions, all four discharged at `60f6e46`:**

| # | Precondition | Discharge |
|---|---|---|
| 1 | W32-7 merged | ✔ `60f6e46` (#164), all three workflows green |
| 2 | Every merged slice has a `#### WK-692-` record | ✔ **12** slice headings — W32-1 … W32-11 plus W32-1b (#159, back-filled separately) |
| 3 | Counts re-taken after the last dependent merge, SHA cited | ✔ every count below taken at `60f6e46` |
| 4 | Full gate run locally, both halves | ✔ see the gate table at the foot of this record |

**Scope**, derived from spec/roadmap/plan assignment rather than from the build log
(§13 rule 1): **27 requirements across 12 slices** — W32-1 … W32-11, plus W32-1b.

W32-1b adds no requirement id (its plan's Global Constraints: "No new requirement ids and
no spec change"), independently confirmed by the executing session. It moved evidence under
FR-451; it did not move membership.

**This is a strict subset of five modules and is not a module-wide figure.** A module-wide
coverage table was produced during this audit and is deliberately excluded: it answers a
different question, and presenting it as WK-692's coverage would report scope WK-692 never had.

#### The 26 delivered and evidenced by a marker

FR-451 · FR-107 · FR-9 · FR-68 · FR-55 · FR-82 · FR-140 ·
FR-180 · FR-207 · FR-174 · FR-175 · FR-181 · FR-187 ·
FR-94 · FR-166 · FR-150 · FR-4 · FR-167 · FR-136 ·
FR-135 · FR-193 · FR-158 · FR-157 · FR-395 · FR-396 ·
FR-397

**The last three moved into this list when W32-7 merged, and the count moved with them.**
Before `60f6e46` all three were *not started* with owner W32-7, and this record was drafted
that way. Marker counts at `60f6e46`: FR-395 **2**, FR-396 **5**, FR-397 **3**,
alongside FR-372's **8**. Three carry a qualification already on the record, stated here
so the count is not read as uniform:

- **FR-181's marker predates the evidence that bears on it** (W32-10's slice record).
- **FR-4's three marker files do not include `test_artifact_immutability.py`**, the file
  W32-6 actually changed. Its W32-6 evidence is the `artifact_append_only` triggers and the
  narrowed `SELECT, INSERT` grant — a **database constraint, not a marker**. The closure
  skill's §0a is explicit that evidence is not only markers; this is that case.
- **FR-396 has five markers and one of its four obligations is undischarged.** A marker
  count is not a completeness proof, and this is the case in this workstream that shows it
  most sharply. Its own subsection is below.

#### The 1 accountable without a marker — with its §13 verdict

| ID | Verdict | Owner |
|---|---|---|
| **NFR-488** | **Delivered but untested** | booked forward |

**NFR-488 — delivered and measured; the marker is what is missing.** W32-5's slice
record (`:3970`) lists it under that slice's evidenced requirements, but W32-5 produced no
measurement. The measurement it rests on is a **WK-661** bench added 2026-08-22 under
OQ-572, *before W32-5 existed*: `diagnostics.py:814` records 0.0480 fits per pass
against a ≤ 0.06 budget, **met at 1.25×**. W32-5 changed how `exposure_share` is computed at
each partial-dependence grid point (summed exposure, not a row count): per-pass arithmetic
that does not change the ~625 scoring passes the budget is set against, so the bound
plausibly still holds. **Plausibly is not measured**, and §13 rule 3 does not accept an
asserted NFR. Re-running a 75 000 × 60 × 500 GBM bench is out of scope for a closure record
and W32-5 is merged, so this is **booked forward with an owner rather than held against the
close**.

**A delegated report claimed this requirement had "no mention found anywhere in the tracked
tree". That is false and was not adopted.** Verified directly: `02-modelling.md` **7** hits,
plus `diagnostics.py`, `packages/pricing-core/tests/test_gbm.py` and `scripts/bench-model.py`
(4), plus its origin at `open-questions.md:79`/`:81`. The same report was also internally
inconsistent — it gave a marker total that could not be reconciled with its own unmarked
list. **Both halves were discarded and every count in this record was re-taken in the main
thread.** This is `CLAUDE.md` §12 doing work rather than being quoted: evidence is delegated,
verdicts are not, and **a delegated *count* is evidence like any other**.

**One caution for whoever discharges it.** `test_gbm.py:1879` mentions NFR-488, and it
is a **docstring line, not a `@pytest.mark.req` marker**. A grep for the id finds it and it
does not bind a test to the requirement. That is the same shape as the method finding below,
met while checking the very requirement the finding was being written around.

#### FR-396 — the fourth obligation: *deferred with an owner*, owner `W6b-11`

`:3705` wrote this verdict as **a rule with both branches stated in advance**, to be
instantiated against fact at close rather than written ahead of it. Stated in the spec's own
words (`07-platform.md:79`), obligation 4 is *"a switch is audited into both chains"*; the
roadmap's shorthand "the request-path trigger" names the **residual**, not the obligation,
and this record uses the spec's wording. **Both branches, as `:3705` set them:**

> If W32-7 ships **`record_switch`**, **the both-chains audit**, *and* files the trigger
> question as a **new `OQ-PLAT` question, whatever its number** — then obligation 4 is
> **deferred with an owner**, owner W6b-11, and the other three are delivered.
> **If either half is missing, all four obligations are *not started*, owner W32-7.**
> Two of three is not three-quarters delivered.

**The first branch fires; the second is spent and is recorded as spent.** W32-7 ships
`platform/workspace_switch.py`, which writes one audit event into each workspace's chain, and
files the trigger question as **OQ-652**. The second branch would have left an owner
clause naming W32-7, and **no owner clause may name a slice of a closed workstream** — that
branch is discharged here rather than left for a later reader to find pointing at nothing.

**Stated as a rule, not as a symptom**, per the convention adopted below: the rule *"a switch
is audited into both chains"* is **delivered as a mechanism and tested, and unenforced on the
request path**. The cause, which is more useful than the symptom: **`require_caller` runs once
per request and cannot observe that a selection *changed***. No component in the request path
observes a change of selection, so there is nothing for the mechanism to hang off. One
*visible symptom* is that `record_switch` has no call site outside its own module and its two
tests — but a record stating only the symptom **would go green the moment anyone added any
call site at all**, which is the failure mode this record exists to avoid.

**`60f6e46` must not read as this obligation met.** The slice says so itself in three places
rather than letting a green suite imply otherwise, and `OQ-652` carries the three options.

**Adjacency worth stating, because the two are easy to merge:** FR-397 (out of OQ-648)
settles the **transport** — the verified `Workspace-Id` header. FR-396 obligation 4 is
the **audit into both chains**. Adjacent, not identical; delivering one is not evidence for
the other.

**A decision W32-7 took, recorded with its reason rather than as a non-action.** The slice
plan told it to add `workspace` to the `ARTIFACT_TYPES` frozenset so `entity_ref` would
parse. It measured first — **20 of the 39 `entity_ref` spellings the backend writes already
fail to parse, 13 of them on a type outside the frozenset** — and declined, on the grounds
that fixing one case in twenty makes the other nineteen harder to see. The measurement and
the three options are **`OQ-653`**. Widening the frozenset to admit one string is the
option that row exists to refuse.

#### §5 — the retrofit-impossible foundations: **preserved, not delivered**

These landed in Phase 1a. WK-692's obligation to them is *non-regression*: `CLAUDE.md` §9 —
"invariants to preserve, not work to schedule: regressing one is the same rewrite that
deferring it would have been." Framing them as delivered by WK-692 would claim credit for
Phase 1a's work; omitting them would leave the most important section of the roadmap
unaddressed at a close.

| Foundation | WK-692's relationship | Status |
|---|---|---|
| Append-only audit log, in the caller's transaction | W32-6 hardened it at the database; W32-7 chains a switch into two logs at once | preserved, strengthened |
| Artifact immutability + versioning + `parent_id` | W32-6: `artifact_append_only` triggers, narrowed `SELECT, INSERT` grant | preserved, strengthened |
| `model-schema` as the single source of truth | **WK-692's central axis** — FR-451, the contract guards, W32-1/-1b/-11 | preserved, materially strengthened |
| The Job model with progress and cancellation | untouched | **preserved** (verified) |
| Decimal money discipline | untouched | **preserved** (verified) |
| `trace_id` propagation API → worker → core | untouched | **preserved** (verified), with a pre-existing gap below |
| RBAC checks in the backend from the first endpoint | **W32-7's territory** — `deps.py`'s `_single_workspace` replaced by a verified selection | preserved, strengthened |
| Content-addressed blob store | untouched | **preserved** (verified) |

**How the four "untouched" rows were verified, 2026-08-24 at `c024f3e`.** Not asserted: for
each, the enforcing mechanism was located and checked to be something that would *fail*, and
then every WK-692 commit was tested against the files that mechanism lives in.

- **Job model** — `JobRow` at `backend/src/app/db/models.py:89`, with three DB `CheckConstraint`s
  at `:147-159`; cancellation is a live code path, not a column (`worker/progress.py:209` polls
  `cancellation_requested_at`, `:117`/`:124` raise `JobCancelled`).
- **Decimal money** — two independent arms: `model_schema/money.py:68-80` `_reject_float`, and
  `scripts/audit-docs.py:546-553` check 12. `test_money.py:28` proves it rejects `250.0` as
  firmly as `361.20`. Worth recording: **there are no money columns in the backend ORM at all**
  — money crosses only as model-schema types inside JSONB.
- **`trace_id`** — edge at `observability/middleware.py:41-42,61,65`, hand-off at
  `platform/jobs.py:123,156`, plus a DB `CheckConstraint` on the W3C hex shape at
  `models.py:156-159`.
- **Blob store** — the address is computed and never supplied: `platform/blobs.py:148`
  `hashlib.sha256(body).hexdigest()`, key at `:63-70`, dedup at `:147-164`; `test_blobs.py:62`
  asserts identical content stores exactly one row.

**Only two WK-692 commits touched any of those files** as of that verification, both in
`db/models.py`, and both pure additions far from `JobRow`: `225a8b9` (W32-3) adds five lines
inside `DatasetRow`, `a23e16b` (W32-2) adds to `ValidationRuleRow`. `JobRow` spans `:89-159`.
**No WK-692 commit touches `money.py`, `blobs.py`, `worker/progress.py` or `observability/` at
all.** Non-regression is therefore evidenced by the change set, not by inspection alone.
**Re-checked after `60f6e46`:** W32-7 adds a `workspaces` table and touches `db/models.py`,
`deps.py`, `me.py`, `responses.py`, `errors.py` and `main.py` — none of the four mechanisms
above — so the finding stands at the last feature SHA and not merely at `c024f3e`. The closing commit is `e2ae7c6` (#165).

#### Two findings from that verification — both pre-date WK-692, both booked forward

Recorded because §13 rule 2 does not accept silence, and because a closure record that
reported only the clean result would hide what the verification actually found.

1. **R4's API→worker leg is delivered but untested, and its "→ core" clause is implicit.**
   `worker/tasks.py:266,275,289` binds and resets the id, but `grep -c trace_id
   backend/tests/test_worker.py` returns **0** — no test asserts the worker binds the payload's
   `trace_id`. And `grep -rn trace_id packages/pricing-core/src` returns nothing: `pricing-core`
   never references the id, inheriting it only via ContextVar. The edge and the DB constraint
   are well tested; the middle leg is asserted. **Not a WK-692 regression** — no WK-692 commit touches
   either file — so it is booked with an owner rather than held against the close.
2. **FR-414's code delta is outstanding and is not WK-692's.** The partial unique index at
   `models.py:135-143` has not gained the `status <> 'failed'` term the requirement specifies.
   `07-platform.md:102` names the owner in the requirement itself — **"Owner: whichever
   workstream builds FR-413"** — so this is neither a WK-692 obligation nor a WK-692 omission.
   Noted only so that a later reader does not discover it and assume WK-692 passed over it. The
   other half of that decision, removing the unreferenced `idempotency_window_hours` setting,
   *was* done, at `b019070` — a decisions commit, not a slice.

#### Unassigned, not reassigned

**NFR-465 and NFR-466** are out of W32-2's and W32-3's scope (their slice records at
`:3887` and `:3914`), and `:1029` names **no owner at all**. That is *genuinely unassigned*,
which is not one of §13's four verdicts and is not the same as reassigned. Booked forward
with an owner in the residual rather than left silent, because silence is precisely what
rule 2 refuses.

#### The open questions WK-692 booked forward

`OQ-649`, `OQ-650`, `OQ-651`, `OQ-567`, `OQ-568` (`:4149-4153`) from
W32-11, and **`OQ-652`** and **`OQ-653`** from W32-7 — **seven**. None carries a
requirement id, so none can appear in the table above. `:4145` states that **none of them
holds WK-692 open**, and this record quotes that rather than paraphrasing it.

**The drift guard's arm-level reach must be stated at the right granularity.** W32-1b
delivers arm-level **type and bound disagreement on paths shared *within* an arm**; arm-level
**existence** is `OQ-649` and remains open. **FR-451 is therefore not fully
discharged by W32-1b and this record does not claim it is.** The worked instance is in that
row, measured at `7e09eb4` and reproducible against it: moving `family` between arms of the
authored `model-spec` takes the comparison from **146 `(arm, path)` keys to 145, with
disagreements 0 before and 0 after** — the path does not disagree, *it stops being compared*,
and every check stays green. One key out of 146, which is also why a threshold expressed as a
fraction of the walker's own output can never catch this class: the denominator moves with
the numerator.

#### A convention adopted during this close

**Every verdict resting on a symptom states the rule and derives the symptom from it.**
Raised by the WK-664 lead. The form is *"the rule X is unenforced; one visible symptom is Y"*,
and it costs a clause. Without it, a verdict phrased as a symptom **goes green on its own
repair**: whoever fixes the symptom satisfies the record while the rule stays false, and the
probe that found it no longer fires.

**The stronger form, also adopted, because a test outlives a record:** *a regression test must
assert the rule, not reproduce the symptom the finding was reported as.* Applied here,
FR-396's eventual test must assert *"a workspace switch is audited into both chains"* and
not *"`record_switch` has a call site"* — otherwise the first call site anyone adds turns the
guarantee green.

**The exhibit originally offered for this convention was falsified during this audit** (see
the corrections below) and is cited here as a **narrowing**, not as a disarming. A convention
propped up by an example its own author has since disproved does not belong in a governed
record; the convention is adopted on its merits, and the weakened exhibit is the honest one.

#### Verified corrections made during this audit

Recorded because each is a case where the obvious reading was wrong, and a closure record
that reported only conclusions would hide the corrections that produced them.

1. **FR-398 is owned.** Reported as naming no owning workstream, against a roadmap block
   claiming every backlog item names one. `07-platform.md:81` ends **"Owned by WK-664."** The
   search had covered only `docs/roadmap.md`. **An owner is named in the requirement, not in
   the plan.**
2. **FR-40 / FR-43 do not contradict.** Reported as a conflict between `:245`
   ("delivered 2026-08-15") and the WK-664 row's naming them as open work. Both are true of
   different things: `01-data-management.md:97` and `:105` each end **"Delivered
   2026-08-15"**, and the WK-664 row carries stale *ownership* text overtaken the same day by
   the exit-gate decision and never restruck. **"Delivered" and "owned by" are different
   predicates; a stale owner is not a delivery dispute.** Routed to WK-664 as a docs defect, not
   held as a WK-692 blocker.
3. **A module-wide coverage table is not WK-692's coverage.** Excluded, per the scope note above.
4. **A correction of mine that was itself wrong, recorded because a retraction gets the least
   review.** I told a peer session that `plans/PL-00753-wk-664-and-wk-692-the-slice-map.md` contained no
   reference to FR-395/396/397. It does — **line 192**, and in `origin/main`, so concurrency
   was not available as an excuse; that was checked first. The error sat in the *second* half
   of a message whose first half was a correct retraction, which is the worst place for one:
   the correct half buys credibility for the wrong one. It was caught because the recipient
   re-opened an exoneration instead of accepting it.
5. **A finding of mine withdrawn before it entered this record.** I claimed that FR-40's
   regression test in `backend/tests/test_ingestion.py` "encodes the proxy" — that it asserted
   a caller count rather than the rule. Reading the test whole rather than its docstring's
   third line falsifies it: it is named
   `test_a_direct_identifier_column_is_refused_at_ingestion`, opens *"FR-39's other
   half, which nothing enforced until now"*, and asserts the error **code**, the offending
   column name, and that **refusal precedes the version row**. It is a good test, and better
   than either party credited — the ordering assertion is the part that would silently
   regress first. I had quoted a docstring line and inferred the assertion from it: a grep
   hit treated as a reading, which is the same defect as the method finding below, committed
   by its author while writing it.
6. **And the claim that rested on it, corrected.** `:245` — the Phase 1a **exit gate** —
   reads *"FR-40 (**ingestion refuses** a `direct_identifier` column) … ✔ delivered
   2026-08-15 — five injections, five caught."* **The gate names its own boundary, its
   closure is true, and its enforcement was proven on deliberately broken input** — §13
   rule 3 satisfied properly. Nothing was falsified by its own fix. **Struck: the claim that
   "the disarming happened twice, at two layers."** It happened once, in the record.
7. **What survives, restated correctly, and it is not WK-692's to resolve: FR-39 was a
   two-boundary rule closed by a one-boundary requirement, and the remainder was never given
   an id or an owner.** `:1253` diagnosed "FR-39's refusal" — the whole rule — and closed
   it as FR-40, which covers ingestion only. The test's own phrase *"FR-39's other
   half"* presupposes a first half that nothing tracks, and that presupposition is the
   evidence. **A narrowing without a recorded remainder** — not a disarming, and not a false
   closure. Same practical consequence; an entirely different claim about WK-660, and only one of
   them is true. Had `:1253` stated the rule — *"a modelling-forbidden column is not
   fittable"* — the narrowing would have been **visibly one boundary of two at the moment of
   closure**. The symptom framing did not disarm a detector; **it made the narrowing
   invisible.** The finding belongs to the WK-664 lead, who carries it as a §14 proposal with its
   own id and owner; it is recorded here only as the correction that produced this record's
   convention, and it did not hold this close open.

#### The method finding — worth more than any individual fix

**Eight instances in one week, all one shape: an ordinal, a pronoun, or a locator standing in
for the thing itself inside an enumeration.**

1. The W32-2 attribution — "W32-2 closed the first" inverted it; `validation-rule` is third.
   **Mine**, and since corrected in place.
2. The WK-692 scope row's dependency clause — "are blocked on it": two WK-664 sessions reached
   opposite readings of "it".
3. A filename-suppressing grep flag let two hits be confidently attributed to the wrong file.
4. A 400-character read of that same clause that stopped on the half agreeing with the reader.
5. FR-40/43 above — two predicates read as one.
6. The gate condition itself: "no WK-692 closure record heading" resolves correctly for a human
   and **wrongly for a grep**, because `:3685` is `#### WK-692 — the closure proposal's
   decisions` and differs from a closure heading by one `#` and one word.
7. **A line number cited without its tree.** The WK-692 scope row is `:4392` on the pre-merge
   `main` and `:4455` here, because W32-7 adds exactly 63 lines above it — `4392 + 63 = 4455`.
   Two sessions cited it correctly and read each other as disagreeing. The proposed
   explanation, *"the line number drifts depending on where you anchor"*, was **wrong in a
   checkable way**: the shift is deterministic and equals the diffstat. **That explanation is
   the dangerous artifact, not the discrepancy** — it would talk a future reader out of
   looking at a difference that *is* a disagreement. The exactness is itself the proof that
   all 63 added lines fall above the row; had any fallen below, the offset would have been
   smaller than the diffstat, and **that mismatch is the signal**. This record was itself
   caught by the rule while being written: several of its draft `:NNNN` citations had gone
   stale in the same merge, and were re-derived rather than carried.
8. **A docstring line read as an assertion** (correction 5 above). **Mine.**

**The rule, adopted with the WK-664 sessions:** *a citation must come from output that names its
own file, and a grep hit is a candidate until the whole row is read.* Its corollary, from
(6): a gate is a literal command with its expected output, not a sentence. Its corollary from
(7), which generalises the same shape past line numbers: **reproduce the citation against a
named tree, then check the delta against the diffstat** — it passes or it does not, and when
it does not you have a disagreement rather than a shrug. Its corollary from (8), the sharpest
because the check that missed it *was* performed: **a citation supporting a claim about what
a test asserts has to be read to the asserts.** One session quoted a docstring line; the other
ran `sed` over the same five lines, saw the quote was verbatim, and wrote "verified" — it
**verified the citation and not the claim it was cited for**, and the check could not tell
those apart because it stopped at the same line. A wrong locator fails when someone opens the
file; **this one passes when someone opens the file, as long as they open it to the same
line.** Nothing shorter than reading to the asserts is a check.

**And the pairing that matters more.** The W32-2 attribution was findable **only** because
`contract-guard/SKILL.md` states the same fact independently and disagreed with it. *A fact
written once is a fact nothing can contradict.* Every one of the eight was caught by a second
reader or a second statement — **none by the author re-reading their own work, mine included.**
Two of the eight are corrections of corrections, which is the case for reading a retraction
as carefully as the claim it retracts: **an exoneration is the one correction its recipient
has no incentive to check.**

**Wrong and superseded take opposite treatments, and only a timestamp separates them.** The
W32-2 attribution was wrong when written and was corrected. `:3704` booked two slugs as *not
started* and W32-11 then delivered them — but that verdict was **accurate when taken**, hours
before the merge, so it received a dated discharge line and was left standing. Editing it
would have destroyed the record of what was believed when the owner was assigned, which
`CLAUDE.md` §0 exists to prevent.

#### `docs/plans/` is frozen at its date, and its gate rows age by design

`CLAUDE.md` §2 binds: a filed plan is frozen, and **the WK-664 slice map was not corrected by
this close**. Two of its gate rows were accurate when written and are false now that W32-7 has
merged — **line 192** most consequentially, because it tells `W6b-11` it *"waits only on WK-692
building the header half"*, which misleads the one session it gates rather than merely a
reader.

**The reason is §0's.** An edit that makes a filed plan more accurate destroys the record of
what was believed at its date, and does so *invisibly*, because the improved text reads as
though it was always right. **The live correction lands on the WK-692 row at `:4455`**, which is
a living document. Stated explicitly so that no reader treats the frozen map as current.

#### Findings booked forward rather than held against the close

Per the maintainer's standing instruction: findings this workstream cannot resolve are booked
into later work with an owner, never held against WK-692's closing.

- **The modelling PII guard is unenforced.** Its own section is below — it is the most
  consequential finding of this close and is deliberately not buried in this list.
- NFR-488's unmeasured budget (above).
- NFR-465 / NFR-466, unassigned (above).
- The seven open questions (above).
- **`.claude/skills/secret-hygiene` states the shared-stash hazard as a secrets concern, not
  as a hazard about the stash stack itself.** The stack is shared across every worktree and
  the main checkout, so a bare restore can pick up another session's work. Booked, not fixed
  — a skill edit is not WK-692's to make at its close.
- **`test_auth_users.py` asserted only a status code**, so it could not detect the change it
  existed to guard. **Discharged in W32-7 and verified at merge**: it now asserts
  `exc.value.code == "WORKSPACE_SELECTION_REQUIRED"`, with a comment recording that an
  assertion on the status alone would go on passing if it regressed.

#### The modelling PII guard is unenforced — found during this close, and outside WK-692's scope

Verified at `f902e3a` and unchanged at `60f6e46`. `modelling_forbidden_columns`
(`packages/model-schema/src/model_schema/datasets.py:195`) has **exactly one runtime caller**,
`backend/src/app/data/ingestion.py:498`. `Factor.prohibited`
(`packages/model-schema/src/model_schema/modelling.py:148`) is an **author-set** boolean,
default `False`, refused without a reason at `:266` and enforced at
`pricing_core/modelling/factors.py:150`, `platform/model_specs.py:202` and
`platform/modelling.py:470` (FR-90). **Nothing derives `prohibited` from the column
classification.** So a column classified `direct_identifier` **is fittable today**.

**Severity, held at its true weight.** Not a raw-PII breach: ingestion still refuses, and
`pseudonymise` tokenises the values. It is (a) the platform breaking its own stated rule while
the column still carries the classification that states it, and (b) **per-customer leakage,
because a stable token is a perfect-fit feature**. In a pricing platform that is a modelling
defect, not only a governance one.

**A design point for whoever builds it**, so it is not scoped as a one-line boolean:
`prohibited` requires a non-empty `prohibited_reason`, so the derivation must *synthesise* the
sentence an actuary reads when the refusal arrives.

**Why this is not a §13 verdict.** It sits on FR-39 / FR-90, and **neither is among
WK-692's 27 ids** — a grep for those ids across all twenty-one WK-692 plan files returns nothing.
§13's four verdicts are instruments for the population rule 1 establishes; **a requirement
outside that population is not a §13 silence, it is simply not in the audit.** Two sessions
proposed booking it as *reassigned*. That would assert WK-692 held it and passed it on. **WK-692
never held it** — a false statement about custody, dressed as procedure, of the tidy kind that
is never challenged.

**Proposed disposition, requiring a maintainer acceptance line (§14): a new unit with its own
id and owner.** Routing work to a workstream that never scoped it is a plan change, and a
review proposes, never changes.

#### For the §14 phase review, triggered by this close

Not part of this record — §14's output is a proposal, never a change. **The review itself is
`Plan review 4`, immediately above this record**; what follows is the list this close handed
it, kept here because the evidence for each item is in this record and not in the review.

- **The workstream boundary was drawn by subject matter; remainders have since been booked by
  screen, and the two no longer coincide.** `:4455` describes WK-692 as *"everything in Phase 1b
  that is not a browser"*. Each later slice discharged what it could and booked its remainder
  onto the row that owns the **screen**, because that is the row a reader looking for
  "thresholds" finds. **`W6b-13` — a WK-664 slice titled "Rule set threshold editing" — now
  carries four booked items of which three are backend**: FR-68's dropped `catalogue_id`
  (`01-data-management.md:166`), FR-56's catalogue thresholds and the `params: {}` seed
  (`:118`), and §5.1's three lineage defects (`:844`). Only `:1029`'s hard-coded PSI bands is
  a browser. **No single booking was wrong.** The mechanism is the one named above running in
  its other direction: a frozen dependency column ages into a false *ready*; **a scope
  sentence ages into a false *partition***. Both are a line drawn once and read later as
  though it still described the world. The generalisation: **`:4455` describes the workstream;
  the slice map determines the slices — description is not constraint.** **The WK-692 row is not
  amended in that respect**: it accurately records what the split intended on 2026-08-22, and
  rewriting it destroys that. **The PII finding above is a third instance, arriving from the
  opposite side** — work the scope *sentence* claims and the 27-id *table* does not, where
  `W6b-13` is work the sentence *disclaims* and a WK-664 row nonetheless owns. **The sentence and
  the table disagree in both directions**, which is stronger than either instance alone:
  neither is a safe restatement of the other, and a reader who checks one and infers the other
  is wrong either way round.
- **An accidental gap in a permanent-id sequence is a collision invitation, and §5 does not
  forbid it.** `9ab14d6` filed OQ-649, -11 and -13, skipping **12** with no reservation and
  no note. §5 forbids renumbering; it says nothing about holes. **Mine.** The gap was closed
  harmlessly — W32-7 filed OQ-652 for the FR-396 trigger, and no second OQ-652
  exists anywhere in history — but it was closed by luck rather than by any rule. **It survived
  only because the verdict rule at `:3705` refused to pin a number**, requiring instead *"a new
  `OQ-PLAT` question, whatever its number"*. An unnumbered condition tolerated a sequence defect
  that a numbered one would have converted into a false failure — **a second instance of the
  deliberately-unnumbered gate condition, arguing the opposite way from the first**, which
  makes it worth more than a confirmation would have been.
- **FR-177 / FR-178 are orphaned between WK-690's rows and WK-690's scope.** Lead with
  the 2026-08-22 date collision; carry FR-176 as a candidate with a caveat. **WK-690 is
  Phase 2, so any finding here is a spec change only** (§0's table).
- **`diagnostics.py` contradicts itself 103 lines apart** about who owns FR-177 —
  `:861` "WK-690 owns the slice" against `:964` "owned by WK-664". **Deliberately left unfixed: it
  is the exhibit.** A review that quietly repairs the artifact it cites has destroyed its own
  evidence.
- **The ownerless backend lineage slice** — a workstream name without a row, in its third
  form. Declined for WK-692: adding work while writing a closure record reports scope the
  workstream never had.
- **`CLAUDE.md` §2's `docs/contracts/` sentence** — proposal with an acceptance line only. A
  peer's ask is not authority to edit the governed contract.
- **The §0 correction convention manufactures its own false positives.** Dated correction
  prose accumulates inside rows that later readers grep as though they were current
  assertions, and a struck sentence keeps living in any code comment that quoted it verbatim.
  Raised as an instrument question, not a request to stop recording corrections.

#### The gate, run in full at `60f6e46` — both halves

`CLAUDE.md` §11's rule is that the gate has two halves and both must pass locally before
pushing; a Python-only "gate" has been green here while the frontend was red. Delegated to
`gate-runner` and reported per-command, with the tree it ran in named — the rule that exists
because a delegated gate once reported a total from the wrong worktree.

| Half | Command | Exit |
|---|---|---|
| Python | `ruff check .` | 0 |
| Python | `mypy` | 0 |
| Python | `lint-imports` | 0 |
| Python | `pytest -q` | 0 |
| Docs | `scripts/audit-docs.py` | 0 |
| Docs | `scripts/req-coverage.py` | 0 |
| Contracts | `scripts/generate-contracts.py --check` | 0 |
| Frontend | `pnpm install --frozen-lockfile` | 0 |
| Frontend | `pnpm generate:api` | 0 |
| Frontend | `pnpm lint` | 0 |
| Frontend | `pnpm type-check` | 0 |
| Frontend | `pnpm test` | 0 |
| Frontend | `pnpm build` | 0 |

**Figures, with the reconciliation that makes the pytest total believable:** **1925 collected**
= **1923 passed + 1 skipped + 1 xfailed**, which balances — the check exists because a
delegated run can silently collect a different tree than the one under audit, and a bare
"all passed" cannot be told apart from that. `req-coverage.py`: **523 requirements specified,
269 marked** — repo-wide, and **not** WK-692's figure; that script cannot see the frontend, so an
unmarked id is not by itself an unevidenced requirement. `generate-contracts.py --check`: **26
contracts match**, which proves the generated artifacts agree with `model-schema` and proves
nothing about whether either is correct (§13 rule 3). Frontend: **21 test files, 131 tests**,
production build clean.

**What this table is not.** Every command exiting 0 is the *precondition* for closing, never
the argument for it. The one requirement in this workstream without a marker, and the one
obligation of FR-396 that is unenforced on the request path, are both invisible to all
thirteen commands — a green gate is exactly what an unenforced rule looks like.
