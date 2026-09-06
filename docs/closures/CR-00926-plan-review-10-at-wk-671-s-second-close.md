---
id: CR-926
family: closure
kind: review
title: Plan review 10 — at WK-671's second close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-30
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 10 — at WK-671's second close, 2026-08-30

`CLAUDE.md` §14's tenth run, triggered by the close of WK-671's reopened scope. **Base tree:
`origin/main` at `b749acb`**, confirmed equal to `origin/main` when this was written; every
claim below was checked at that tree or names the commit it was checked at.

**Three §14 outputs now exist for one workstream, and a reader needs to know which does what.**
The closure record's §7 (`work/WK-671/README.md`) is the short review written against the
**first**, reduced-scope close. [Plan review 9](#plan-review-9--at-w11s-close-2026-08-30) is the
fuller working analysis drafted at `19eaabc` while that close was in doubt, filed with its
drafting history intact and its acceptance still pending. **This is the review of the second
close**, and it does three things and no more: it answers the five questions against the
completed workstream, it carries what is genuinely new since `19eaabc`, and it says what has
happened to review 9's own preconditions. **It does not restate review 9's twenty-five
proposals**, which stand as filed and are not re-argued here.

---

**1. Completion — reused from the §13 audit, not re-derived.**

`.claude/skills/phase-review` says that where a fresh audit has just covered this, say so and
move on, because re-deriving would look like work and confirm nothing. The §13 closure audit
for the second close ran against this same tree and is filed as `work/WK-671/README.md` §10 (PR
#503). Its scope came from `scope-audit.py RATE --sections 3.7,3.8 --extra
FR-253,FR-254,FR-259,NFR-500`, run against the spec rather than against
recollection.

**The three requirements the first close recorded as never started are delivered and tested**
— FR-253 (`3dc8d6b`), FR-254 (`59407f2`, `eda70d6`), FR-259 (`25c5688`, `003f9d4`,
`87dd4b7`). That is the completion answer, and it is not this review's to re-verify.

**What the review adds to it is the shape of what remains, which the audit reports per
requirement and nobody has yet read as one picture:**

| Requirement | Verdict at `b749acb` | Where |
|---|---|---|
| NFR-489 (p99 < 50 ms) | measured and **failing** | first close, §4–§5; RL-921 discharged the architectural question without making the target reachable |
| NFR-500 (< 200 GB/year) | measured and **failing**, 516.07 GB/year, ~2.58x | §10.3, Task 4D |
| NFR-490 (trace overhead) | measured and **failing**, F35 | register |
| NFR-493 (batch throughput) | **passing** at 5.09x; its linearity clause **not measured**, F52, unowned | §10.4 |
| NFR-502 | **owed, not delivered** | first close |

**Every functional requirement WK-671 owns is delivered; three of its numbered non-functional
budgets are measured and failing, and a fourth is half-measured with no owner.** Neither close
states it that way, because each verdict is correct in its own row. Question 5 takes up what
follows from it.

---

**2. Omission — one class closed, one opened.**

**Closed: the unclaimed-NFR class did not recur in the reopen.** The closure record's §7
question 3 found five NFRs worked inside WK-671 while claimed by no roadmap row, and proposed that
rows name NFRs explicitly. The reopen honoured it without being told to — `../roadmap.md`'s WK-671
row names **NFR-500** in its reopen text, by id, as riding with FR-259. Recorded as a
result rather than passed over: a proposal from the previous review changed the next thing that
was written.

**Opened: `NFR-500` names a condition that cannot be resolved, and the failing measurement
turns on it.** Its text (`../specs/03-rating-engine.md` §9) reads *"1 % sampling of 50 M annual
quotes stays under 200 GB/year **with the sampled-trace schema**"*. The budget is therefore
conditional on a schema — and **F55**, filed the same day, finds that the schema actually
shipped stores each `TraceStep`'s full accumulated engine context rather than its own declared
inputs and outputs. So the 2.58x overage is not straightforwardly a budget failure: it is a
measurement of a schema the requirement's author may never have contemplated, against a number
chosen for one they did.

**Nothing in the requirement lets a reader tell which schema is meant** — no version, no
artifact path, no `04.5` reference. This is the failure `RFC-777` names: a reference that
resolves only for its writer. **This review does not decide which side is wrong** (§0 forbids
resolving it silently, and the choice is a real one), but it insists somebody does, because the
two branches lead to different work: trim the schema under F55 and re-measure, or amend
NFR-500 to state the encoding it actually budgets for. See proposal 2.1.

**No new instance of the `WF-698…05`-evidenced-by-nothing class** was looked for in this pass and
none is claimed; review 9's answer stands and is not re-checked. Stated rather than left silent,
per this skill's own rule.

---

**3. Skills and research — one finding of real consequence, and three convention findings.**

**3a. A skill and a test both assert a check that does not exist, and the test cannot fail.**
This is the review's principal finding and it was not on anyone's list.

`.claude/skills/fastapi-service` states: *"`PlatformError.__init__` refuses any code not in
`_KNOWN_CODES`, and **a conformance test asserts each module's registry equals its spec's
declared list**."* Verified at `b749acb`: **no such test exists.** `git grep -ln
"_KNOWN_CODES\|RATING_ERROR_CODES" -- backend/tests` returns nothing, and no test in the
repository opens a spec file to read an owned-code block.

**What does exist is worse than nothing, because it reads as the missing check.**
`backend/tests/test_errors.py:107-111`, `test_spec_error_codes_are_all_constructible`, carries
the docstring *"The registry must match `07` §5.1 — a code in the spec but not here cannot be
raised"* and then iterates `PLATFORM_ERROR_CODES` asserting each is constructible. Its body
**cannot detect the case its docstring names**: a code present in `07` §5.1 and absent from the
registry is never iterated, so it is invisible to the loop. And since `PLATFORM_ERROR_CODES` is
a member of the union that forms `_KNOWN_CODES` (`errors.py:348`), every element it iterates is
constructible by construction — **the assertion is a tautology and the test is guaranteed
green.** A check that has never printed a failure has not been tested (`CLAUDE.md` §13).

**This is `F29`'s substance with its cause named for the first time.** F29 records that nothing
checks error-code registration in either direction; what it does not record is *why the gap
survived* — a skill and a test docstring both told every reader that the spec-to-code direction
was covered. **Proposal 3.1**, and it is the one item in this review that `CLAUDE.md` §12
already binds someone to: a skill known to be wrong is fixed in the same session, `Verified`
refreshed. This review proposes, it does not edit — `fastapi-service` is a backend-conventions
skill and not the planner's (`.claude/roles/planner.md`).

**3b. The "registers no new error code" sentence was wrong every time it was written: 0
predicted, 4 actual.** Measured across the two plans that used it, at `b749acb`:

| Plan | Predicted | Actually registered |
|---|---|---|
| WK-671 Slice 3 | none | `BATCH_ABORT_THRESHOLD_ABOVE_SETTING`, `BATCH_ABORTED` (`eda70d6`) |
| WK-671 Slice 4 | none | `TRACE_RETENTION_FLOOR` (`25c5688`), `TRACE_NOT_PENDING` (`003f9d4`) |

**Four codes, two plans, both predicting none.** That is not two coincidences; in this
workstream the claim's error rate is total. **The sentence is prescribed by nothing** —
`git grep` over `.claude/skills/` and `../plans/README.md` finds no template requiring it. It
is an author-invented clause that has been copied plan to plan while riding on the `Next free:`
id block, which is mandated and which `audit-docs.py` enforces. **Error codes have no
reservation mechanism at all**, so the clause borrows the authority of a machinery that does not
cover it.

**Its disposition split matters and collapsing it would mislead.** After the Slice 4 plan's
correction merged (`c8d9c55`, 17:31), Task 4B merged 2h07m later (`003f9d4`, 19:38) registering
`TRACE_NOT_PENDING`. So the **prediction** recurred after being named. The **registration
discipline** did not fail: 4B registered the code in `errors.py` and in `03`'s owned-code block
and declared it in its commit body. **The correction worked; the sentence was simply never a
rule.** Recorded at this strength because an earlier reading of the same facts — that no further
code appeared — was drawn from the two tasks under discussion rather than from every task merged
in the window, and 4B was in the window.

**Proposal 3.2**: a plan's id block speaks only to ids it can reserve. A claim about error codes
either goes into the register-rows section as an expectation with an owner, or is not made.

**3c. A correction filed in a sibling record is only found by a reader who knows siblings
exist.** The Slice 4 plan carries two correction channels — an in-plan `Corrections after
filing` section and
[`../plans/PL-00901-wk-671-slice-4-the-always-capture-design-pins-the-traced-fraction-at-1-and-nfr-489-fails-on-all-real-time-traffic-2026-08-30.md`](../plans/PL-00901-wk-671-slice-4-the-always-capture-design-pins-the-traced-fraction-at-1-and-nfr-489-fails-on-all-real-time-traffic-2026-08-30.md),
which holds RL-862's binding constraint on Task 4B. A dispatch that names the plan does not
thereby name the sibling. **Proposal 3.3**: a filed plan names its own correction records where
a reader enters it, or the dispatch that sends someone to a plan enumerates them.

**3d. A precedent carried between rulings must be split before it is reused.** RL-910 found
that RL-906's *conclusion* **inverts** for the register: 46 declined to red-gate a corpus
because that corpus may not be edited, and editing a register row is that file's normal
operation. Same principle, opposite disposition, visible only because someone re-checked 46's
premise instead of reusing its answer. **Proposal 3.4**: a ruling citing an earlier one states
which of mechanism, conclusion and principle it is carrying, and re-checks the earlier ruling's
premise against the new corpus. Home is the decision-maker's conventions, not this review's to
place.

**3e. A turn that ends while waiting on a delegated agent cannot receive that agent's report,
and this review is one of the occurrences.** Recorded against itself rather than about others,
because it is the reason question 4 above has a gap.

Two agents were dispatched for this review's evidence. Both were sent a direct request to
report; **the turn then ended while they were outstanding**, which is precisely the state in
which their reports could not arrive. The endpoint axis was recovered by re-running the command
directly — three seconds of work — after fifty minutes of waiting produced nothing. The
signature axis was not.

**The finding is not "the agents failed."** It is that the waiting party had a cheap
non-delegated route to the same answer and did not take it, and that ending a turn is what
made the wait unrecoverable rather than merely slow. This is reported as the **sixth occurrence
today across five mechanisms**, the earlier ones against executors; **this one is against a
role**, which is why it did not pattern-match to the same failure while it was happening.
**Proposal 3.5**: a delegated evidence request states, at dispatch, the direct command that
answers the same question, and the dispatcher runs that command rather than waiting once the
delegation is outstanding and the work is cheap. `CLAUDE.md` §10's delegate-noisy-investigation
rule is about **context cost**, not latency; a three-second command is not noisy investigation
and delegating it buys nothing.

---

**4. Document drift.**

**4a. `FR-241` still cites `FR-247` where it means `FR-270`.** Verified at
`b749acb`, `../specs/03-rating-engine.md:137`: *"unless the deployment explicitly uses
date-based routing (FR-247)"*. FR-247 is the Premium Ladder; FR-270 is date-based
routing. The closure record's §7 recorded this as outstanding and owed at the next docs pass;
**it is still outstanding two closes later**. Two characters, and it has now survived being
named once. **Proposal 4.1**: fix it in the next docs commit and give it an owner rather than a
queue.

**4b. `NFR-500`'s unresolvable schema condition** — question 2 above; it is a drift finding
as much as an omission, in the direction §14 cares about most (the spec describing something the
code does not implement, rather than the reverse).

**4c. The §5.1 endpoint axis is clean for WK-671's scope; the §5.2 signature axis is unrun.** The
two are separate questions and this review answers only one of them.

`uv run python scripts/scope-audit.py RATE --endpoints`, run for this review on this branch
(`7fa1326`, a docs-only commit on `b749acb`) and independently at `7b490b3` with identical
figures: **22 declared, 14 published, 8 not published.** All eight belong to later
workstreams — `GET`/`POST /api/v1/dislocation-runs` and `/{}` (WK-673, FR-263–49),
`POST /api/v1/environments/{}/deployments` and `/rollback` plus
`PUT /api/v1/environments/{}/shadow` (WK-674, FR-267–55),
`POST /api/v1/rate-tables/{}/versions`,
`POST /api/v1/rating-versions/{}/regression-runs` (WK-672, FR-260–45), and
`POST /api/v1/score/compare`. **None is a WK-671 gap**, and the published count moved 13 → 14 with
Task 4C's `GET /api/v1/traces`, which is the direction this workstream should have moved it.

**One relay check that changed nothing and is recorded because it could have.** An
intermediate enumeration of this same result listed seven paths under a count of eight; the
omitted one was `PUT /api/v1/environments/{}/shadow`. Re-run here rather than transcribed, and
its owner checked (`FR-271`, named by WK-674's row), which is what confirms the conclusion
rather than assuming the missing item was harmless.

**The signature axis — `03` §5.2 shapes with no implementation, and implemented shapes `03`
does not declare — remains unrun.** It was delegated and the delegation did not return. Stated
as an open gap with a named owner rather than left silent, because a silent question cannot be
told apart from one nobody asked. **Proposal 4.2**: run the §5.2 direction before WK-672 opens,
since WK-672 builds against those shapes.

---

**5. Shape — the cut held; the requirement set is where the problem is.**

**5a. The workstream cut: the reopen tested the closure record's proposal and supports it.** §7
of the first close proposed that batch scoring and trace sampling should each have been their
own workstream. The reopen is the experiment: eight tasks ran as two chains (3A→3D, 4A→4D) that
never interacted, delivered on the same day, and were audited separately. **Nothing about
running them under one id helped, and the single id is what produced two closes of one
workstream and three §14 outputs for it.** Recommendation stands, and this review adds the
evidence the first one could only predict. It is a recommendation about *future* cuts; WK-671 is
not re-cut retrospectively.

**5b. The requirement set is the real finding: WK-671 delivers its functional surface with three
numbered budgets failing.** Question 1's table is the evidence. This is the skill's named smell
— *a phase exit criterion the phase cannot meet* — and the review's job is to make somebody
choose rather than to choose. The three are not one problem:

- **NFR-489** — failing, architectural question ruled (RL-921) without the target becoming
  reachable. Carried to WK-674.
- **NFR-500** — failing against a schema the requirement may not have meant (question 2).
  **Its remedy has a named lever, F55.**
- **NFR-490** — failing, F35. **Its blocking precondition, RL-862's off-path capture,
  landed today in Task 4B**, so the remedy is unblocked. The measured clause itself does not
  move, because F35 measured the explicit `ctx.options.trace=True` path that 4B leaves
  untouched.

**5c. F35 and F55 converge on one lever, and neither row says so.** Both turn on what a
`TraceStep` carries and what producing one costs; F55 is NFR-500's largest remediation lever
and trimming the same structure is the obvious candidate for F35's 97.2 % reduction target.
**Proposal 5.1**: treat trace-payload trimming as one piece of work serving both rows rather
than two independently-owned findings, and say so on both rows. Whether it becomes a slice is
the lead's and the maintainer's, not this review's.

**5d. Review 9's preconditions are now met, and it should be put to the maintainer.** Its
acceptance line is pending and its own stated bar was: Slices 2–4 land, the §13 closure audit
completes, review 8's binding condition is met, and the lead rules the gate-coverage decision
point. **The first two are now true at `b749acb`.** Review 9 is a large evidence base whose
findings do not depend on the unbuilt slices, and leaving it pending indefinitely is how
twenty-five proposals become nobody's. **Proposal 5.2**: put review 9 to the maintainer with
this one, as two acceptances, not one.

**5e. The gate-coverage cluster is still undecided and this review does not decide it.**
`F27(c)` and `F29` remain open; `F33` was materially advanced by `c8d3c81`. It was pre-designated
by RL-860 to be decided at a §14 review, was carried past review 9, and the RFC-895 adoption
record explicitly left it. **It is a decision, the lead's, not a proposal** — but finding 3a
above changes its terms, because F29 is now known to have been masked by a skill and a
tautological test rather than merely unaddressed.

---

#### Proposals, consolidated — review 10

| # | Proposal | Kind |
|---|---|---|
| 2.1 | Decide `NFR-500`'s branch: trim the trace schema under F55 and re-measure, or amend the requirement to state the encoding it budgets for. It may not stay conditional on an unresolvable "the sampled-trace schema" | spec change or work — maintainer to place |
| 3.1 | Correct `.claude/skills/fastapi-service`'s claim that a conformance test compares each registry to its spec list, and either fix or retire `test_spec_error_codes_are_all_constructible`, whose body cannot fail for the reason its docstring gives | skill + test correction — `CLAUDE.md` §12 already binds it to this session |
| 3.2 | A plan's id block speaks only to ids it can reserve; an error-code expectation goes in the register-rows section with an owner, or is not stated | convention (`writing-plans`) |
| 3.3 | A filed plan names its own correction records where a reader enters it; a dispatch to a plan enumerates them | convention (`writing-plans` / dispatch) |
| 3.4 | A ruling citing an earlier one states whether it carries its mechanism, its conclusion or its principle, and re-checks the earlier premise against the new corpus | convention — decision-maker's records |
| 3.5 | A delegated evidence request names, at dispatch, the direct command answering the same question; the dispatcher runs it rather than waiting once the delegation is outstanding and the work is cheap | convention — dispatch discipline |
| 4.1 | Fix `FR-241`'s `FR-247` → `FR-270` citation, with an owner rather than a queue | spec change (two characters) |
| 4.2 | Run the `03` §5.2 signature direction before WK-672 opens, since WK-672 builds against those shapes | evidence — owner needed |
| 5.1 | Record on both `F35` and `F55` that they share one remediation lever, and scope trace-payload trimming as one piece of work | register amendment — the auditor's |
| 5.2 | Put plan review 9 to the maintainer alongside this one, as a separate acceptance | process |
| DP-1 | The gate-coverage cluster (`F27(c)`, `F29`, `F33`) is still undecided, now in changed terms — see 3a | **decision, the lead's — not a proposal** |

#### What this review did not do

- **It did not re-derive question 1**, by design; the §13 audit at the same tree is its source.
- **It answered the `03` §5.1 endpoint axis and not the §5.2 signature axis** (question 4c).
  The endpoint result is clean for WK-671's scope with its command and tree named; the signature
  direction is unrun and carried as proposal 4.2 rather than reported as absent drift.
- **It did not re-argue review 9's proposals**, which stand as filed.
- **It did not edit the Slice 4 plan again.** All four of its tasks have merged, so it is a
  finished record; its correction section was written while three tasks were unrun and was
  correct at its date. `TRACE_NOT_PENDING` is carried here instead.

**Maintainer acceptance:** _pending._ Nothing above binds until this line carries a date. The
`RFC-895 … RFC-898` reconciliation triggered at this same close is a **separate document with
its own acceptance line** ([`../plans/PL-00900-rfc-895-rfc-898-the-joint-reconciliation-2026-08-30.md`](../plans/PL-00900-rfc-895-rfc-898-the-joint-reconciliation-2026-08-30.md)) —
accepting this review accepts none of its four dispositions.

> **Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 9 and
> 11 under review 11's proposal 11.1.** The `_pending._` sentence above is kept as the record;
> the reconciliation it names is accepted separately, this same date, by its own line.

#### Sources

- `docs/closures/CR-00927-work-item-record-wk-671-scoring.md` §10, at `origin/docs/audit-w11-second-close` (PR #503) — the
  §13 closure audit reused for question 1.
- `docs/roadmap.md` WK-671 row and §7, read in full at `b749acb`.
- `docs/specs/03-rating-engine.md:137` (FR-241), `:175` (FR-259), `:906` (NFR-500),
  and the owned error-code block at `:628`/`:634` — read directly at `b749acb`.
- `backend/src/app/errors.py:332,339,348,378` and `backend/tests/test_errors.py:100-111` — read
  directly at `b749acb`.
- `git grep -ln "_KNOWN_CODES\|RATING_ERROR_CODES" -- backend/tests` — run at `b749acb`, zero
  hits; and `git grep` for the same over `packages`, `scripts`.
- `git log --oneline 25c5688..b749acb -- backend/src/app/errors.py` — run at `b749acb`, one
  commit (`003f9d4`).
- `uv run python scripts/scope-audit.py RATE --endpoints` — run for question 4c on this branch
  (`7fa1326`), and independently at `7b490b3`, with identical figures.
- `docs/specs/03-rating-engine.md:197,602` (FR-271 and the shadow endpoint row) and
  `docs/roadmap.md`'s WK-674 row (`FR-267, FR-268, FR-269, FR-270, FR-271, FR-272`) — read directly, to place the eighth
  unpublished endpoint.
- `docs/findings/register.md` rows F29, F35, F52, F55 — read directly at `b749acb`.
- `docs/rulings/RL-00910-q2-rl-906-s-mechanism-does-not-transfer-its-principle-does-and-the-answer-here-is-to-conform-the-corpus-and-red-gate-from-day-one.md` RL-910 §1–§2 — read directly.
- `.claude/skills/fastapi-service/SKILL.md:328-338`, `.claude/skills/phase-review/SKILL.md` —
  read directly.

---
