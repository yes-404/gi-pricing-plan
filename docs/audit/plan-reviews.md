# Plan reviews

> Moved from `docs/roadmap.md` by the roadmap slim (NT-0009, accepted 2026-08-27).
> Each review is the §14 output at its date; the proposals and acceptance lines are
> the record.

### Plan review 2 — at W7b's close and before Phase 1a's exit demo, 2026-08-15

`CLAUDE.md` §14's second run. Both triggers fire at the same moment: W7b closed, and the
exit demo is the next milestone. Five questions, in order, each answered — **including the
ones whose answer is "no change"**.

This review is short on questions 1 and 4 on purpose. The independent audit that ran hours
earlier is the evidence for both, and repeating its work would be re-deriving from the same
sources rather than testing the plan.

**1. Completion — derived, not recalled.**

| Module | §5.1 endpoints published | Requirements evidenced |
|---|---|---|
| `DATA` | **34 / 34** | 48 / 52 |
| `PLAT` | 18 / 21 | 40 / 65 |
| `GOV` | 11 / 20 | 23 / 43 |
| `OVR` | — | 8 / 25 |

423 requirements specified, 121 marked (28.6 %) — the phase covers `DATA` and the `PLAT`
and `GOV` foundations under it, which is what Phase 1a's rows claim and no more. `DATA`'s
four unevidenced requirements each carry a verdict: NFR-DATA-1/2 measured rather than
tested, FR-DATA-41 and FR-DATA-42 appended this morning and owned by W6b. `PLAT`'s three
unpublished endpoints are W14's environments routes.

**The plan and the derivation now agree** — because the audit made them agree this morning,
not because they always did. Three closure records claimed more than they established and
were rewritten; that reconciliation is recorded above and is not repeated here.

**2. Omission — what the phase needs that no row names.**

*The workflow journeys are evidenced by nothing.* `docs/workflows/wf-01…05` are the
cross-module contracts — a module spec says what one module does, a workflow says what
actually happens — and **no test in the repository cites one**. Phase 1a's exit criterion is
a slice of `wf-01`, covered by `test_data_jobs.py::test_the_failure_loop_then_validated`,
which does not name it. `audit-docs.py` check 14 reports "workflow coverage: DATA 50 %",
which measures whether the workflow *documents mention* a requirement id — not whether the
journey runs. No workstream row owns "the journeys work", and none of the five has been
read against the code since it was written.

This is the same shape as the audit's other findings: a number exists, it is not measuring
the thing its name suggests, and nobody had looked.

> **Recorded as OQ-OVR-6** *(2026-08-15)*, with a recommendation: a mechanical audit that
> every journey step cites an endpoint, requirement or artifact that exists — the
> `--endpoints` idea one level up — **now**; one end-to-end journey test per workflow as its
> modules land; and explicitly **not** a marker on an existing test, which would claim a
> journey where one slice is covered. A journey belongs to the workstream that completes
> the last module it touches, so `wf-01` is W5's to finish. Phase 1a's exit demo walks its
> data half and is that half's first evidence.
>
> **Accepted 2026-08-15**, unchanged, as **FR-OVR-17**. Writing it down sharpened two things:
> the audit's real content is **endpoint and `pricing-core` function** citations, because
> requirement ids and `§` references are already checked; and the ownership rule needs no
> new machinery, since "the workstream that completes the last module" is in every case the
> phase whose exit criterion names that journey (§12).

*Two model/contract divergences have no owner.* `Dataset` carries no status, validated-at or
owner while `01` §5.3 asks the dataset list to display all three; `ColumnProfile` has no
`histogram` while `01` §4.4 **and** `docs/contracts/schemas/profile.schema.json` both define
one. W6b cannot build those view items until someone says which side is wrong, and no row
owns the deciding.

*Not omissions:* Playwright E2E is deferred with a stated reason, `pipelines/` is W7's, and
the six `PLAT` endpoints remain W14's.

**3. Skills and research — re-run, not appended to.**

`docs/skills-map.md`'s pandera row was retired this morning (it read ★★ **Verified** for a
library this repository depends on nowhere). Nothing else in the map is now ahead of or
behind the code. No new external skill is proposed, and none would be installed without the
maintainer's approval.

One gap, from this week rather than from the map: **`close-workstream` does not warn that a
proof can pass for the wrong reason.** §13 rule 4 requires a check be shown to fail on
deliberately broken input. The catalogue check was shown exactly that — and the injection
deleted an id from a *docstring*, so it proved the counter could count while the counter was
counting prose. The skill should say that the injection must break the thing the check
*claims* to measure, not merely something the check happens to read.

`close-workstream` also carries no `Verified` date, alone among the eleven written here.

**4. Document drift.**

Repaired this morning across three commits: the specs now describe what was built, the three
closure records say what the audits establish, and `CLAUDE.md` §2's tree is accurate. What
remains unchecked is `docs/workflows/` — see question 2 — along with `docs/README.md` and
`docs/phase-0-status.md`, neither of which has been read against the repository since Phase
0 closed.

**5. Shape — two proposals.**

*Proposal A — Phase 1a cannot exit as its criterion is written.* §6's exit reads: "a
freMTPL2 dataset version reaches `validated`, including at least one deliberate round
through the failure loop. **The retrofit list (§5) is fully in place by the end of 1a** —
that is the phase's other, quieter deliverable." The first half holds and is now drivable by
hand. The second does not: FR-DATA-42, artifact immutability, is on that list and is
enforced by nothing — `frozen=True` is a rule about one process, and an audit rewrote 190
stored reports in a single statement. It is owned by W6b, in Phase 1b.

> **Recommendation:** land **FR-DATA-41 and FR-DATA-42 before the exit demo**, keeping the
> criterion as written. They are small — a check at ingestion and four append-only triggers
> with their broken-input proofs — and everything Phase 1b builds sits on artifacts that
> nothing currently protects. The alternative, amending the criterion to exclude
> immutability enforcement, is coherent but should be chosen deliberately and with the risk
> stated, not arrived at by the demo happening first.
>
> **Maintainer accepted 2026-08-15.** FR-DATA-41 and FR-DATA-42 are a **gate on Phase 1a's
> exit demo**: the criterion stands as written, and the demo does not run until artifact
> immutability is enforced in the database rather than asserted in Python.
>
> The bookkeeping is stated rather than tidied away: **W6b's row still names both
> requirements**, and W6b is a Phase 1b row. The work therefore lands in Phase 1a while its
> nominal owner sits in 1b. That is the maintainer's decision, taken twice; recording it
> this way keeps the record honest about where the work happened, which matters more than
> which row it hangs from.

*Proposal B — W6b is now three workstreams in one row.* It carries `02` §5.3's factor
workbench, model detail and diagnostics — a full frontend workstream on its own — plus
browser authentication (FR-PLAT-55), accessibility beyond semantics (NFR-OVR-10), workspace
selection, the audit's six missing `01` §5.3 Contents items, threshold editing, and the two
enforcement gaps. **The last two are not frontend work at all**, and a row whose scope spans
a Vue view, an OIDC flow and a database trigger is a row nothing can be said to have closed.

> **Recommendation:** split the non-frontend half out under its own id when Phase 1b is
> planned, leaving W6b the views and the browser. No id is proposed here — naming one is
> the maintainer's, and the last two attempts at it cost two corrections.
>
> **Maintainer accepted 2026-08-15.** The non-frontend half splits out when Phase 1b is
> planned; W6b keeps the views and the browser. The id is assigned at that point, not here.

*No change* to the phase boundaries, to W5, to W7's remaining modelling half, or to Phases
2–4. Nothing this review found argues for re-cutting them.


### Plan review 3 — at W5's close, 2026-08-22

`CLAUDE.md` §14 requires a plan review at **each workstream close**. This is the third; the
procedure is `.claude/skills/phase-review`. **The output is a proposal, never a change** —
every recommendation below needs a dated maintainer acceptance line before it binds.

**1. Completion — derived, then evidenced, never recalled.**
`scope-audit.py MODEL`: **125 in scope, 111 evidenced (89 %), 14 without**; **41 of 41
endpoints**; catalogues clean. `req-coverage.py`: 495 specified, 248 marked repo-wide.
**Three disagreements with the roadmap, all corrected today**: the slice count said
twenty-two against a file whose own newest record called itself the twenty-seventh; the
buildable-slice counter said "one" with all five rows beneath it struck; and six verdicts in
the diagnostics table said "Not started" for requirements delivered between 2026-08-17 and
08-19. **No change proposed** — the machinery worked once it was run; what failed is that
nothing runs it between closes, which is question 5.

**2. Omission — what the phase needs that no row names.**
Four found. **(a) `NFR-MODEL-7` has no owner at all** — there is no Model export or import
path anywhere in the repository, and its parent FR-OVR-2 carries zero markers. It is a
capability nobody has been asked to build, and it is not a W5 defect: no row ever named it.
**(b) The constraint-level contract-drift guard** (`minLength`, `additionalProperties`,
`required`-set drift, and arm-level attribution inside `if`/`then`) is still unbuilt after
this slice closed the field-existence and nullability halves. **(c) `06` §3.3's "per-peril
model approvals"** is enforced nowhere and cannot be, while the models sit in JSONB.
**(d) `FR-MODEL-15`'s `source_level_stats`** is in the contract and not in the Python.
**Proposal:** (b) and (d) to **W6b** as the first consumer of these contracts; (c) to **W17**
as the workstream that owns evidence enforcement; **(a) needs a maintainer verdict before it
can have an owner** — it may simply be out of Phase 1 scope, in which case NFR-MODEL-7 should
say so rather than sit unevidenced.

**3. Skills and research — the gap analysis re-run, not appended to.**
Two skills updated **and their index rows with them**: `fastapi-service` gained the alembic
credential mismatch, `python-test` gained the shared-machine load caveat. `docs/skills-map.md`
needs **no change** — this slice added no tech dependency; Bühlmann–Straub's estimators are
pure NumPy, and the §8 SciPy row was corrected to say so rather than to claim more.
**One gap the re-run found and this slice did not fill:** no skill covers *writing a schema
guard*, and the three defects found inside the existing guards (a clobbering
`properties.update`, an invisible `const`, an `ENVELOPE_FIELDS` wrong in both directions)
are exactly the kind of knowledge that is expensive to rediscover. **Proposal:** a
`contract-guard` skill, or a section in `contract-schema`, owned by W6b.

**4. Specification accuracy — the review's main target.**
This is where the slice spent most of its effort, and the answer is that **`02` had drifted
further than the audit found**. §5.1's endpoint table matched on all 40 rows *in both
directions* — which is precisely how the parameters escaped scrutiny, since `--endpoints`
compares method and path. Underneath it: one `{id}` row wrong of 23, `?dataset={slug}`
returning **200 with the whole workspace**, nine §5.2 signatures drifted, and
`compute_gbm_diagnostics` never declared at all. §4.6 diverges from its parser in three ways.
Six hand-authored schemas disagreed with `model-schema` on ~150 points, including a
`fit_result` block no GBM or EBM fit could satisfy. **All resolved by amendment with the
losing side named, never by editing the spec down to what was built.**
**Proposal:** `scope-audit.py` gains a `--params` axis. Three axes exist and a wrong
*parameter* is invisible to all three — that is not an oversight in this audit, it is a hole
in the instrument, and it is the single change most likely to prevent a repeat.

**5. Shape — are the cuts still right?**
**One proposal, and it is the substantive one.** Three separate staleness defects had a
single cause: **a slice updates the row that describes itself, and every other place that
counts or judges slices is unowned.** #116 did it, #124 and #125 did it again, and the
diagnostics table has been wrong since August 17. Naming the mechanism in the roadmap (done)
does not fix it, because it depends on the next author reading a note. **Proposal:** the
derived counts stop living in prose. `CLAUDE.md` §0 already forbids writing counts into it
for exactly this reason — *"counts that change are not written here"* — and the roadmap is
the file that kept doing it. Either the slice count and the coverage figures are generated,
or they are deleted and the reader is pointed at `scope-audit.py`. **No change to the phase
or workstream boundaries is proposed**: W5's cut held, and the audit found defects *inside*
it rather than at its edges.

**Two answers of "no change", recorded because a silent question is indistinguishable from
one nobody asked:** the Phase 1b workstream rows need no re-cut, and no requirement needs
superseding beyond `transparency_artifact_id`, which this slice struck with its reason.

**Maintainer acceptance: accepted as proposed, 2026-08-22.** Each proposal below binds from
that date. Recorded per line rather than as one blanket sentence, because a single "accepted"
over five proposals leaves no way to tell later which of them anyone actually read.

- **Question 2, the owner assignments — accepted 2026-08-22.** (b) the constraint-level
  contract-drift guard and (d) `FR-MODEL-15`'s `source_level_stats` are **W6b's**, as the
  first consumer of these contracts; (c) `06` §3.3's per-peril model approvals are **W17's**,
  as the workstream that owns evidence enforcement.
- **Question 2 (a), `NFR-MODEL-7` — accepted 2026-08-22 at the option the proposal named:
  out of Phase 1 scope.** The review said it "may simply be out of Phase 1 scope, in which
  case NFR-MODEL-7 should say so"; it now does, in `02` §9. There is no Model export path and
  no import path anywhere — not a route, not a CLI, not a bundle schema — and its parent
  FR-OVR-2 carries zero markers. It is a capability nobody has been asked to build, and no row
  ever named it, so it was never a W5 defect. Saying so is the verdict §13 rule 1 requires;
  leaving it "unassigned" was the one row in the audit-remediation slice's verdict table that
  stated an absence of a verdict rather than a verdict.
- **Question 3, the `contract-guard` skill — accepted 2026-08-22, owned by W6b**, as either a
  skill of its own or a section in `contract-schema`. The author's discretion which; the
  binding part is that the schema-drift knowledge stops being rediscovered.
- **Question 4, `scope-audit.py` gains a `--params` axis — accepted 2026-08-22.** Three axes
  exist and a wrong *parameter* is invisible to all three. Accepted as the review argues: a
  hole in the instrument rather than an oversight in one audit.
- **Question 5, the derived counts stop living in prose — accepted 2026-08-22.** Either
  generated or deleted with the reader pointed at `scope-audit.py`; not left as prose to go
  stale a fourth time. This is the only structural proposal of the five and the only one that
  would have prevented the staleness that prompted it. **It does not bind retroactively**: the
  counts already written into this file stay as written, struck and corrected in place where a
  later slice re-derived them, because a roadmap row states what was known when it was written.
- **The two "no change" answers stand**, and needed no acceptance: the Phase 1b workstream
  rows are not re-cut, and no requirement is superseded beyond `transparency_artifact_id`.

### Plan review 4 — at W32's close, 2026-08-24

`CLAUDE.md` §14 requires a plan review at **each workstream close**. This is the fourth; the
procedure is `.claude/skills/phase-review`. **The output is a proposal, never a change** —
every recommendation below needs a dated maintainer acceptance line before it binds. Findings
about Phase 2 or later are **spec changes only** (§0's table).

**1. Completion — not re-derived, because a fresh audit already covers it.**
The W32 closure record immediately below is hours old and derived its scope from the
specification before opening a source file: **27 requirement ids across 12 slices**, of which
**26 are delivered with a marker** and **1 carries a §13 verdict** (NFR-MODEL-14, *delivered
but untested*). The full gate ran clean at `60f6e46` — thirteen commands, all exit 0. The
skill is explicit that re-deriving the same numbers from the same sources *"would have looked
like work and confirmed nothing"*, and review 2 set that precedent. **No change proposed.**

**2. Omission — the workstream boundary was drawn by subject matter, and remainders are now
booked by screen.** The W32 row describes the workstream as *"everything in Phase 1b that is
not a browser"*. Each later slice booked what it could not finish onto the row that owns the
**screen**, because that is the row a reader looking for "thresholds" would search. **`W6b-13`
— a W6b slice titled "Rule set threshold editing" — now carries four booked items, three of
them backend.** No single booking was wrong; the sentence aged into a false partition, the
same mechanism as a frozen dependency column ageing into a false *ready*. **The sentence and
the 27-id table disagree in both directions** — `W6b-13` is work the sentence disclaims and a
W6b row owns, and the modelling PII guard is work the sentence claims and the table does not.
Neither is a safe restatement of the other. **Proposed:** the W32 row is *not* amended in that
respect — it records what the split intended on 2026-08-22 and rewriting it destroys that —
but the phase plan should state that **the slice map determines slices and the scope sentence
only describes them**. Separately, **W30 owns four requirements while its scope row describes
one capability**; W30 is Phase 2, so that is a **spec change only**.

**3. Skills and research — the gap analysis re-run; both indexes complete.** All 43 skill
directories have a README row and all 7 agent files are named; the two README names with no
directory are §12's required refusal records, not defects. Three gaps were found, and per §12
a known-wrong or missing skill is fixed in the same session — precedent set by review 3's own
Q3, and §14's "proposal, never a change" governs **the plan**, not the skills.

| Gap | State |
|---|---|
| (a) Validating a gate whose passing state is **empty output** — stated nowhere; the nearest cousin was `contract-guard`'s two-empty-maps case | **Fixed in this commit** — `close-workstream` gains the control-script procedure and its four rules, verified against the run that gated this record |
| (b) *"A delegated gate must report the tree it ran in"* existed as a **finding** and never as a **procedure** | **Fixed earlier** (`caa5bee`) — `gate-runner` now carries it |
| (c) The shared git stash stack, stated only in a *domain* skill and contradicted by a vendored one | **Fixed earlier** — `git-hygiene` now carries it. The vendored `testing-strategy` is **not** edited: it is not wrong upstream, only wrong in this repository's conditions, so §12 makes it a recorded caveat |

**Two further candidates, booked rather than fixed**, because fixing them at a close is the
scope creep the standard warns against: concurrent slices needing a database each, absent from
`python-test`, `dev-commands` and `reproducing-ci-locally`; and *a slice that moves a measured
figure owes a re-read to every skill quoting it*, stated inside the one skill it protects and
nowhere general.

**4. An accepted proposal that was never built — and the reason it drifted is question 5.**
**`scope-audit.py --params` was accepted 2026-08-22 and does not exist.** Review 3's own words
were that *"a wrong parameter is invisible to all three axes — that is not an oversight in this
audit, it is a hole in the instrument, and it is the single change most likely to prevent a
repeat"*, and it was accepted per-line the same day. Verified at this close: the argument
parser declares `module`, `--sections`, `--extra`, `--endpoints`, `--catalogue`, and
**`grep -c params scripts/scope-audit.py` returns 0**. **Proposed:** give it an owner. The
change review 3 called the single most valuable one was accepted into no row at all.

**5. Shape — an acceptance is not an assignment, and that is the recurrence.**
Review 3 had five accepted proposals; **W32-1 delivered three of them in one commit, all three
assigned to W6b**, verified by file-addition and `-S` history rather than recollection. Read
one way that is a slice being helpful. Read as a pattern it is the same defect as (4): **an
accepted proposal with no owning row is executed by whoever happens to touch the area next, or
by nobody, and both outcomes look identical in the plan.** One produced three early
deliveries; the other produced `--params`. **Proposed:** every accepted §14 proposal gets an
owning row in the same edit that accepts it, or is explicitly marked unowned.

**Three instrument findings from the same review, each verified against an artifact:**

- **Corrections are unreviewed writes.** A correction reads as already-checked and receives
  *less* scrutiny than the text it replaces; one commit here fixed three rows and broke a
  fourth. The sharpest form: **an exoneration is the one correction its recipient has no
  incentive to check**, and two of the eight instances in the closure record below are
  corrections of corrections.
- **The §0 correction convention manufactures its own false positives.** Dated correction
  prose accumulates inside rows that later readers grep as current assertions, and a struck
  sentence keeps living in any code comment that quoted it verbatim. Raised as an instrument
  question, **not** a request to stop recording corrections.
- **An accidental gap in a permanent-id sequence is a collision invitation, and §5 does not
  forbid it.** `9ab14d6` filed `OQ-PLAT-10`, `-11` and `-13`, skipping **12** with no
  reservation and no note; §5 forbids renumbering and says nothing about holes. **This one is
  mine.** It closed harmlessly — W32-7 filed `OQ-PLAT-12` and no duplicate exists in history —
  but by luck, not by rule. **It survived only because the FR-PLAT-63 verdict rule refused to
  pin a number**, requiring *"a new `OQ-PLAT` question, whatever its number"*: an unnumbered
  condition tolerated a sequence defect that a numbered one would have turned into a false
  failure on a correct slice.

**No change** is proposed to the phase boundaries, to Phase 1b's exit criterion, or to
Phases 2–4. Nothing this review found argues for re-cutting them; every finding is an
ownership or instrument defect inside the existing shape.

**Maintainer acceptance: accepted as proposed, 2026-08-29.** Each proposal below binds from
that date. Recorded per proposal rather than as one blanket sentence, on review 3's own
reasoning at line 214 — *"a single 'accepted' over five proposals leaves no way to tell later
which of them anyone actually read."* Review 4 has three proposals and no consolidated table,
so they are enumerated here from the questions that raised them.

- **Question 2, the W32 row — accepted 2026-08-29.** The row is **not** amended: it records
  what the split intended on 2026-08-22, and rewriting it destroys that. What binds is the
  accompanying statement that **the slice map determines slices and the scope sentence only
  describes them**. The separate W30 observation — four requirements against a scope row
  describing one capability — is Phase 2 and remains a **spec change only** (§0's table), not
  a roadmap edit made here. **Owner: unowned**; the phase-plan sentence is a `docs/roadmap.md`
  edit and naming who makes it is not a planner's call.
- **Question 4, `scope-audit.py --params` gets an owner — accepted 2026-08-29, and still
  unowned as of this date.** Re-verified at `3edd75a`: the parser declares five arguments and
  `grep -c -- --params scripts/scope-audit.py` returns 0, so the axis review 3 accepted on
  2026-08-22 has now gone un-built through two further reviews. Accepting the proposal does
  not build it and does not name its owner — **unowned**, and recorded as such deliberately,
  because that is exactly the state question 5 below is about.
- **Question 5, every accepted §14 proposal gets an owning row — accepted 2026-08-29, and it
  binds this edit first.** *"Every accepted §14 proposal gets an owning row in the same edit
  that accepts it, or is explicitly marked unowned."* This is the only proposal here that
  changes how acceptance itself is written, and today's edit is the first to fall under it:
  every item accepted below — in reviews 7 and 8 as well as this one — therefore carries an
  owner or is marked **unowned**. Marking unowned is not a lesser outcome; it is the escape
  the proposal itself names, and it is used wherever naming an owner would be a
  `docs/roadmap.md` edit, which `CLAUDE.md` §12 does not put in a planner's hands.
- **The three instrument findings needed no acceptance line and did not wait on one** —
  corrections are unreviewed writes; the §0 correction convention manufactures its own false
  positives; an accidental gap in a permanent-id sequence is a collision invitation. Each is a
  finding about the instrument, not a proposal to the maintainer.
- **The "no change" answer stands** on the phase boundaries, Phase 1b's exit criterion and
  Phases 2–4, and needed no acceptance.

### Plan review 5 — at W6b's close, 2026-08-27

`CLAUDE.md` §14 requires a plan review at **each workstream close**. This is the fifth; the
procedure is `.claude/skills/phase-review`. **The output is a proposal, never a change** —
every recommendation below needs a dated maintainer acceptance line before it binds. Findings
about Phase 2 or later are **spec changes only** (§0's table). Evidence derived at
`8b0977f` (#260).

#### Question 1 — Completion

Fresh audit evidence, derived at `8b0977f` by a delegated collector. Both inputs are
documents, so the answer does not depend on who ran it. All slices shipped at close
(#243–#263); the manager's close audit counts 245/320 evidenced across the W6b scope.

- Requirements: 531 specified, 274 marked (51.6%) repo-wide.
- Phase 1b modules: DATA 61/67 (91%), MODEL 127/143 (89%), GOV 27/53 (51%),
  PLAT 47/77 (61%), OVR 10/33 (30%).
- Endpoints: DATA 39/39, MODEL 44/44, GOV 13/23, PLAT 19/22.
- Catalogue: DATA validation rules 38/38.
- RATE 2/78, OPT 0/37, MON 0/43: zero evidence is expected. These are Phase 2/3.

The roadmap's closure records carry counts that no longer match the derived numbers.
Example: the MODEL closure record states 125 in scope and 111 evidenced. Today the audit
derives 143 in scope and 127 evidenced. `req-coverage.py` read 495/248 at W5 close. It
reads 531/274 today. The drift is consistent with append-only requirement ids
(CLAUDE.md §5). A reader cannot tell an at-close count from a current count unless the
reader re-runs the audit.

**Proposal 1.1:** each closure record names the tree it derived its counts from, as the
W32 closure record already does. No re-derivation is owed. The record states its snapshot.
**No change** to the phase's completion claim otherwise. The W6b close runs the audit
again after Groups B and C land. This review's numbers are the pre-close baseline.

#### Question 2 — Omission

What does Phase 1b need that no row names?

**(a) The role routes declared in 06 §5.1 have no HTTP route.** The spec declares
`GET/POST /api/v1/roles`, `POST /api/v1/role-assignments`, and `POST /api/v1/break-glass`
(06:436-438). No backend route serves any of them. The machinery exists at the service
layer (rbac.py, RoleRow, RoleAssignmentRow). The W3 closure record claims RBAC delivered.
A caller who copies §5.1 gets a 404. The §5.3 `/admin/access` view is Phase 3. The
resolution must decide: these routes are Phase 1b scope owned by nobody, or Phase 3
surface declared ahead of the phase. **Recommendation:** record them as spec-ahead-of-phase
with a dated note in 06 §5.1, which matches the FR-GOV-3 class. Do not build them at the
close. The decision is the maintainer's.

**(b) `scope-audit.py --params` remains unbuilt.** Plan review 4 proposed it. The
maintainer never accepted it, so it never gained an owner. This is the recurrence review 4
predicted: an accepted proposal with no owning row is executed by nobody, and the result
looks identical to a decision not to do it. **Recommendation:** accept review 4's
proposals with owners, or decline them explicitly. Do not leave a pending line.

**(c) The `\|` blind spot in `scope-audit.py`.** The endpoint parser stops at an escaped
pipe inside a path cell. It under-counts declared GOV endpoints: 10 published versus 12
found by direct comparison. The two missed rows carry `format=html|pdf|bundle` and
`direction=up|down`. The close audit uses this tool. **Recommendation:** fix the parser or
record the limitation in the close-workstream skill before the W6b close counts GOV
endpoints.

**(d) Two routes are undeclared.** `GET /readyz` and `GET /version` exist in code and
appear in no §5.1 table. Minor. **Recommendation:** add them to 07 §5.1 or record the
reverse-direction gap as known.

#### Question 3 — Skills and research

The index is complete: 43 skill directories, 43 README rows, 8 agent files. No new gap
found in this review's evidence.

Two candidates from review 4 remain booked, not fixed: concurrent slices that each need a
database, and a slice that moves a measured figure and owes a re-read to every skill that
quotes it. Review 4 booked them at a close to avoid scope creep. They stay booked.

**No change** to the skills set this review. If proposal 2(c) is not fixed, the
close-workstream skill must state the `\|` limitation.

#### Question 4 — Document drift

The spec-reconciler found real drift, in both directions. The code is right in each case
below. The spec must be amended with a dated note that names which side was wrong.

- **01 §5.2 signatures cannot be called as written.** `explode_period` and
  `attach_claims` take a `spec:` object in the spec. The code takes column-name kwargs.
  `ExplodePeriodSpec` and `AttachClaimsSpec` do not exist. `run_validation` names
  `time_budget_s` (default 300). The code has `rule_budget_s` (default 60) and takes
  `reference_tables` of raw DataFrames, not `ReferenceTableVersion`. `profile_frame`
  takes `tables:` in the spec and `frame:` in code. `one_way_columns` defaults to
  `"auto"` in the spec and `()` in code. A caller who copies §5.2 gets a TypeError.
  The 2026-08-15 correction fixed the module names but not these signatures.
  **Proposal:** amend 01 §5.2 with the actual signatures.
- **02 §5.2 approximation functions are missing two required parameters.**
  `approximation_spec` and `build_glm_approximation` require `source_model_slug` and
  `source_model_version` in code. Neither appears in the spec. The OQ-MODEL-34 ruling
  (#246) changed reservation to derive the slug, but §5.2 was not updated.
  **Proposal:** amend 02 §5.2.
- **02 §5.3 view cells over-promise.** Model detail names a lineage strip. The view
  renders none. No build note records the departure. Metric library names an editor with
  live parse errors and a certificate link. The view is list-only. Its header comment
  records the certificate gap but not the editor. Objective library names a
  gradient/hessian display and loss-curve preview. Neither renders. The cell's
  Phase-gating note covers the editor only. Factor workbench names draggable boundaries
  and a merge-tolerance slider. The view uses numeric inputs and has no slider. The build
  note records both departures.
  **Proposal:** amend the three cells without build notes with dated notes. The cells
  with build notes are recorded. Leave them.
- **06 §5.1 role routes:** see question 2(a). The same decision governs the spec text.
- **GOV 06 §5.1, FR-GOV-3 class:** attestations, dossiers, change control, audit/anchor.
  Declared with no route, all Phase 3 by the roadmap. This is spec-ahead-of-phase, not
  drift. No change.
- **RATE 03 §5.1 and PLAT 07 §5.1 Phase 2 surfaces:** declared, no code. Expected.
  No change.
- **Checked and agreed:** the list below. All 39 DATA endpoints and their params. All 44
  MODEL endpoints. The bulk of 02 §5.2 signatures. The built half of 06 §5.1. The built
  half of 07 §5.1. The §5.3 routes. The named catalogues. The money rule.

#### Question 5 — Shape

W6b is the last Phase 1b workstream. It now spans a Vue view, an OIDC flow, a workspace
selector, lineage, route reachability, rule versioning, and the model workbench. Review 4
named this smell: a row that crosses many kinds cannot be audited as one thing. The close
audit answers it. It derives scope from merged commits, filed plans, and the handover
set. It never derives scope from the frozen slice-map. Keep that mechanism.

The phase exit criterion, `wf-01` end to end on freMTPL2 through the UI, is still not met
at `8b0977f`. The work that remains is W7's modelling half and the demo.py auth-profile
fix (#28). The criterion is still the right test of the phase. **No change** to the
criterion. The close must state whether the exit demo will run and how it will be
accepted.

Review 4's acceptance line is still pending. Its proposals bind nobody. The close must
accept or decline each of them. Proposal 2(b) covers the mechanism.

**No change** is proposed to the phase boundaries or to Phases 2-4. Every finding is an
ownership, instrument, or drift defect inside the existing shape.

#### Proposals, consolidated

| # | Proposal | Kind |
|---|---|---|
| 1.1 | Closure records name their snapshot tree | docs, convention |
| 2.1 | Role routes recorded as spec-ahead-of-phase, not built | spec + decision |
| 2.2 | Review 4's proposals accepted with owners, or declined | decision |
| 2.3 | `scope-audit.py` `\|` blind spot fixed or recorded | tool or skill |
| 2.4 | `/readyz` and `/version` declared or recorded | docs |
| 4.1 | 01 §5.2 amended to actual signatures | spec |
| 4.2 | 02 §5.2 amended with the two approximation params | spec |
| 4.3 | 02 §5.3 cells without build notes amended with dated notes | spec |

**Maintainer accepted 2026-08-27** — all eight proposals accepted.

#### Sources

- evidence-collector run at `8b0977f`: req-coverage, scope-audit all axes.
- spec-reconciler run at `8b0977f`: 01/02/03/06/07 §5.1/§5.2/§5.3 vs code.
- `docs/roadmap.md`: plan reviews 1-4, the W6b and W7 rows.
- W6B-CLOSE-RECORD-SKELETON-2026-08-26.md.

---

### Plan review 6 — at W7's close, before the Phase 1b exit demo, 2026-08-27

`CLAUDE.md` §14's sixth run. Both triggers fire at once: W7 closed, and the exit demo is
the next milestone. Five questions, in order, each answered — including the ones whose
answer is "no change". The W7 close record below carries the completion evidence.

**1. Completion.** W7 was the last Phase 1b workstream; its close record below carries
the delivery, the verdicts and the module delta. The only row left in the Phase 1b status
table is the Exit demo.

**2. Omission.** The surfaces the core journey does not seed — versioned bandings and
groupings, approved Peril Structure with reconciliation — are named in P1 and recorded as
Phase 2, so no row is left unnamed.

**3. Skills and research.** **No change** — P2.

**4. Document drift.** **No change** — P2.

**5. Shape.** The Phase 1b exit criterion is restated as the **core `wf-01` journey** —
dataset → factors → GLM + GBM fits → comparison → approval → rating version — with
bandings, Peril Structure and reconciliation recorded as Phase 2.

#### Proposals, consolidated

| # | Proposal | Kind |
|---|---|---|
| 1 | Phase 1b exit criterion restated as the core `wf-01` journey — dataset → factors → GLM + GBM fits → comparison → approval → rating version — exercised over HTTP; bandings, Peril Structure and reconciliation recorded as Phase 2 | plan |
| 2 | No change on questions 3 and 4 | plan |

**Maintainer accepted 2026-08-27.**

---

### Plan review 7 — at W9's close, 2026-08-27

`CLAUDE.md` §14's seventh run, filed retroactively on 2026-08-29 together with review 8:
W9 closed 2026-08-27 and W10 closed 2026-08-28, and `CLAUDE.md` §14's trigger is fixed —
"at each workstream close" — so both were owed and neither had been filed before W11 was
next in line. **The output is a proposal, never a change** — every recommendation below
needs a dated maintainer acceptance line before it binds. Evidence derived at `origin/main`
`07ae047`, rebased onto `d4bc394` while this PR was open (see review 8, Question 4: `d4bc394`
is in fact one of this pair's own recommendations, landed independently before either review
was filed). Nothing else moved underneath this review — `07ae047` (#313) touched only
`.claude/notes/`, and `d4bc394` (#314) touched only the two lines review 8 names.

**1. Completion — reused, not re-derived.** W9's own closure record already carries fresh
completion evidence for its scope (`docs/audit/work/W9/README.md:26-29`), so it is cited
rather than repeated: FR-RATE-1..13, FR-RATE-22..27 and FR-RATE-56/57/58/59 delivered, and —
outside W9's own row's stated numeric range — **FR-RATE-60**, marker-evidenced (3 files),
correctly caught the same way W10 later caught FR-RATE-62. No change proposed to W9's
completion claim.

**2. Omission — what the phase needs that no row names.**

**FR-RATE-61 and FR-RATE-63 have no workstream row.** (Verifying the hypothesis this review
was handed: it named FR-RATE-60 alongside FR-RATE-61. FR-RATE-60 is not part of this gap —
see Question 1 — it was verdicted in W9; its own roadmap-row text simply omits it from the
literal range, a wording correction rather than a coverage gap.) Both 61 and 63 were decided
2026-08-18 — OQ-MODEL-11 into FR-RATE-61 (`03-rating-engine.md:110`, §3.2), OQ-RATE-4 into
FR-RATE-63 (`:87`, §3.1). Neither appears in any `W_` row's stated scope: a full-file grep of
`docs/roadmap.md` for both ids returns exactly two hits, both inside OQ-RATE-4's and
OQ-MODEL-11's own decided-narrative text (`:536`, `:567`), never inside a workstream row.

**The two are not the same shape of gap, and the lead's own verdicts on this evidence (issued
2026-08-29, `CLAUDE.md` §12 — verdicts stay in the main thread) say so precisely; this review
carries that finding rather than re-deriving a competing one.** FR-RATE-63 is a **W9 close
gap**, not an orphan: nothing blocked it — FR-RATE-6 (sub-graphs) was W9-1's own delivery,
and FR-RATE-63 is a `RatingVersion` pins-extension structurally identical to what W9-3 built
for FR-RATE-60 in the *same* PR (#293). It was decided 2026-08-18, nine days before W9
closed (2026-08-27) — not the one-day window first reported (`git log`, UTC: #291 at
2026-08-27T21:48Z, #292 at 22:42Z, #293 at 23:44Z, and W9's close commit `eb9b6a1` at 23:47Z
the same day). A week-plus window, not a same-day scramble: FR-RATE-60,
decided one day *before* FR-RATE-63, rode into #293 on that same merge, so the
identical-shape sibling requirement had every opportunity to ride in beside it and did not.
W9's own scope prose
names four sections totalling 26 requirements; it verdicted 24. **W9's closure record
reports a completeness the repository does not have** — `CLAUDE.md` §13's own stated failure
mode, on work already closed. FR-RATE-61, by contrast, genuinely could not have been built
by W9: its own text needs a Dislocation Run (FR-RATE-46), which is W13's, so it is orphaned
at birth rather than missed at a close.

Why it matters going forward, not only as a retrospective correction: **FR-RATE-61
specialises FR-RATE-40's approval gate for the approximation-mode case** — W11 builds the
general gate, and W13 already owns the Dislocation Run that both need, making W13 the
natural single owner of the specialisation rather than splitting one gate's logic across two
workstreams. **FR-RATE-63 bears directly on W11's evaluator regardless of who owns the id,
and it itself splits in two.** `purpose` is not a hypothetical extension point — it is
already a fully-typed `QuoteContext` field every scoring call reads unconditionally
(`03-rating-engine.md:63` glossary: `new_business | renewal | mid_term_adjustment |
cancellation | what_if`; `:389` shows it live in the request JSON example), so both halves
below are properties of code W11 slice 1 is building regardless of FR-RATE-63's ownership:

- **The refusal guard** — when `purpose ∈ {mid_term_adjustment, cancellation}` and the
  Rating Version has no matching mounted sub-graph, `score_one` must refuse rather than
  silently price as new business (`03:87`: "it is silent" is the failure named). This is a
  `score_one` correctness property with the same universal shape as FR-RATE-57's
  null-output guard — provable only by a slice-1 test on deliberately broken input — and has
  no dependency on anything W9 did or did not build: even before any Rating Version can
  mount such a sub-graph, the guard is meaningful, because it turns an unbuildable feature
  into a loud, correct refusal instead of a silent wrong price. **Recommend: W11 slice 1,
  unconditionally.**
- **Sub-graph mounting and refund/pro-rata authoring** — declaring the separately-versioned
  sub-graph itself, version-pinning it, and mounting it on a Rating Version — is algorithm
  *definition* work, the same kind as W9's own scope (§3.1), not scoring/evaluation work.
  Folding it into W11 would blur W11's boundary into authoring territory the same way pulling
  Environment/Deployment forward would (Question 5, review 8) — for a capability nothing in
  W11 needs in order to build the guard above. **Recommend: a small, separately-owned
  catch-up slice, landing with or before W11 but not part of its plan** — matching the shape
  of W9-3's own delivery of FR-RATE-60, since FR-RATE-63 is that requirement's structural
  twin. This review does not name a workstream id for it; that is the maintainer's, the same
  restraint plan review 2's Proposal B applied to naming W6b's split.

> **Recommendation:** FR-RATE-61 gets a register row with owner **W13** — it never depended
> on this review, since W11 was never a candidate owner for it, and it has since landed as
> `docs/audit/register.md`'s F-W9-2 (PR #319), recorded here as confirmation rather than an
> open ask. FR-RATE-63's id-level ownership (a corrected W9 closure note, or a new row) is
> this review's to propose and the maintainer's to accept — deliberately held out of the
> register until this line carries a date, so a row does not pre-empt the acceptance that
> names its owner. Its build obligation does not wait on that answer either way and splits
> as above — the refusal guard in W11 slice 1 unconditionally, the authoring half in its own
> small slice separate from W11. Not a roadmap edit on this review's own authority.
>
> **Maintainer acceptance: accepted 2026-08-29 — the split binds; the owner is still not
> named.** What is accepted is the *shape*: FR-RATE-63's refusal guard is W11 slice 1's
> unconditionally, and the sub-graph mounting and refund/pro-rata authoring half is a separate
> small catch-up slice, W9-shaped, landing with or before W11 but not part of its plan.
>
> **What acceptance does not do is name the workstream.** This review deliberately declined to
> name one — *"that is the maintainer's, the same restraint plan review 2's Proposal B
> applied"* — and the acceptance relayed today carries no id either. So FR-RATE-63's id-level
> ownership (a corrected W9 closure note, or a new row) is **accepted as owed and explicitly
> unowned**, per review 4's question-5 rule above. Verified at `3edd75a`: `FR-RATE-63` appears
> in `docs/audit/register.md` only inside F27's prose about `scoring.schema.json`'s `purpose`
> enum, and in `docs/roadmap.md` only at the OQ-RATE-6 decision prose — no register row and no
> workstream row owns the id. The register row this recommendation was held out of is now
> released to be written, and writing it is not this document's to do.
>
> **F-W9-2 needed no acceptance line to bind**, since it was never this review's proposal to
> make; that half is unchanged by this date.

**3. Skills and research — re-run, not appended to.**

One gap found, self-referential: **the `phase-review` skill's own "Output" section was
stale.** It named `docs/roadmap.md` as where a review's proposals land; the location moved
to `docs/audit/plan-reviews.md` on 2026-08-27 (NT-0009), two days before this skill was next
read. **Fixed in this commit** (`CLAUDE.md` §12: a skill found wrong is fixed in the same
session, `Verified` date refreshed) — the file this review is filed into is the proof the fix
is correct.

No other skill or research gap found against W9's own scope. Carried into review 8's
Question 3, not repeated here: no spike or research artifact covers the ZEN engine's
*evaluate*-side behaviour — W9 never needed it, W11 will be the first to.

**4. Document drift.** Two disagreements found, both inside code W9 itself shipped, both
routed to the decision-maker rather than ruled here (`CLAUDE.md` §0: stop and resolve, never
quietly make either side match — this review's job is to name the disagreement precisely,
not to rule it):

- **The compile endpoint is specified 202 and implemented 200.** `03-rating-engine.md:513`
  specifies `POST /rating-versions/{id}/compile` as `**202** Compile + validate the bundle`;
  the shipped route (`backend/src/app/api/models.py:1139-1161`, wired to
  `compile_rating_version`, `backend/src/app/platform/rating_versions.py:226-288`) returns
  200 synchronously. Bears directly on W11: today the route persists only
  `{content_hash, bytes, compiled_at}` and discards the full compiled Bundle
  (`rating_versions.py:283-287`) — the slice that fixes that and persists the Bundle proper
  may push the operation past a synchronous-response budget, which is a reason to rule
  before that slice starts, not after. Two further code-vs-spec items surfaced since this
  review began, queued to the same decision-maker ruling rather than re-litigated here:
  `compile_bundle` is async in code (`compile.py:387`) against a synchronous §5.2 signature,
  and `CompiledBundle` — the type every §5.2 scoring/dislocation/regression signature
  takes — has no code definition anywhere; the shipped class is `Bundle`, and whether that is
  a rename or `CompiledBundle` must become a distinct loaded-runtime wrapper is an
  architecture question for W11 slice 1, not a spelling one.
- **`POST /api/v1/rating-versions` (`03:512`) cites no requirement.** Every other §5.1 row
  names the FR- it implements; this one reads only "Create a draft Rating Version with
  pins." Two readings are both live: a capability the spec never got around to numbering
  (needs an appended FR), or a Phase-1b-era row (`03` §4.3's own OD1/W7-3 scoping note
  describes exactly this kind of provisional minimal shape) never tombstoned when Phase 2
  widened the contract. Which reading is correct changes what the register owes it.

> **Recommendation:** all four items go to the decision-maker's queue before W11's plan is
> filed — the compile 202/200 divergence, the async/sync mismatch and the
> `Bundle`/`CompiledBundle` question before any slice touches `compile_rating_version` or
> starts the evaluator, the missing citation whenever convenient since nothing currently
> depends on its answer. None is resolved in this review — that queue reports itself
> complete as of this filing, which this review notes rather than duplicates: the rulings
> themselves are a decision-maker record, not a plan-review one.
>
> **Maintainer acceptance: accepted 2026-08-29 — and all four items have since been ruled, so
> this line confirms rather than releases them.** Verified at `3edd75a`, each against the
> artifact that discharged it rather than against recollection: the compile-endpoint 202/200
> divergence is `docs/plans/2026-08-29-w11-prework-rulings.md` Ruling 2; the async/sync
> `compile_bundle` mismatch is Ruling 3; the `Bundle`/`CompiledBundle` question is Ruling 4;
> and the missing citation on `POST /api/v1/rating-versions` is now on the row itself —
> `docs/specs/03-rating-engine.md:513` reads *"Create a draft Rating Version with pins
> (FR-RATE-22)"*, landed with W11 Task 1.1 (PR #371). **Owner: discharged, none owed.** The
> recommendation was that these reach the decision-maker's queue before W11's plan was filed;
> they did, and the acceptance records that the route taken was the route proposed.

**5. Shape.** No change proposed to W9's own scope or boundary — it closed against a
coherent, single-subject row and nothing in this review's evidence argues otherwise. The
shape question that matters is about the workstreams *after* W9, visible only once W10's
close is reached and W11 is next — carried into review 8 immediately below, where it belongs.

#### Proposals, consolidated — review 7

| # | Proposal | Kind |
|---|---|---|
| 2.1 | FR-RATE-61: register row, owner **W13** (specialises FR-RATE-40 for approximation mode; never depended on this review) | decision — **landed, F-W9-2, PR #319** |
| 2.2 | FR-RATE-63: id-level ownership (corrected W9 note, or a new row) is this review's to propose | decision |
| 2.3 | FR-RATE-63 splits: the refusal guard is W11 slice 1's, unconditionally; sub-graph mounting/authoring is a separate small catch-up slice, W9-shaped, not part of W11 | decision |
| 3.1 | `phase-review` skill's Output section corrected to `docs/audit/plan-reviews.md` | skill (fixed in this commit) |
| 4.1 | Compile-endpoint 202/200 divergence, the async/sync `compile_bundle` mismatch, and the `Bundle`/`CompiledBundle` question ruled by the decision-maker before W11 touches `compile_rating_version` or the evaluator | decision — queue reports complete as of this filing |
| 4.2 | `POST /api/v1/rating-versions`'s missing FR- citation ruled | decision |

**Maintainer acceptance: accepted as proposed, 2026-08-29.** All six rows bind from that date.
Per row, with the owner review 4's question-5 rule now requires — and where no owner can be
named without a `docs/roadmap.md` edit, the row says **unowned** rather than leaving it to be
inferred:

- **2.1 — accepted, and already landed.** F-W9-2, PR #319. Never depended on this review.
  **Owner: W13**, as the row states.
- **2.2 — accepted as owed, owner not named. Unowned.** See the per-item line above: the
  review declined to name a workstream and today's acceptance names none either.
- **2.3 — accepted.** The refusal guard is **W11 slice 1's**; the authoring half is its own
  small catch-up slice, **unowned** until 2.2's owner is named.
- **3.1 — accepted, and landed. Owner: discharged** — but not on the date the table claims,
  and the divergence is recorded rather than smoothed. The row reads *"fixed in this commit"*,
  i.e. review 7's own filing on 2026-08-27; `.claude/skills/phase-review/SKILL.md`'s `Verified`
  block dates the Output correction to **2026-08-29** and says it was *"caught while filing
  plan reviews 7 and 8"* — caught then, applied two days later. The skill now reads
  *"Proposals land in `docs/audit/plan-reviews.md`"* (`:110`), so the proposal is discharged
  either way; what was wrong was the parenthetical, checked here rather than restated on the
  table's word.
- **4.1 — accepted, and discharged** by prework Rulings 2, 3 and 4. **Owner: discharged.**
- **4.2 — accepted, and discharged**: the FR-RATE-22 citation is on `03` §5.1's row at
  `:513`. **Owner: discharged.**

---

### Plan review 8 — at W10's close, 2026-08-28

`CLAUDE.md` §14's eighth run, filed retroactively on 2026-08-29 alongside review 7 — see
review 7's opening for why both were owed. **The output is a proposal, never a change.**
Findings about a later phase are spec changes only (§0's table). Evidence as review 7:
derived at `origin/main` `07ae047`, rebased onto `d4bc394` — see review 7's opening.

**1. Completion — reused, not re-derived.** W10's own closure record already covers its
scope in full (`docs/audit/work/W10/README.md:29-37`): FR-RATE-14..21 and FR-RATE-62, all
"delivered and tested." Module-wide, current: **78 `RATE` requirements in scope, 34
evidenced (44 %)** (`scope-audit.py RATE`, run this session at `main@74b1b10`, confirmed
unchanged through `07ae047` and `d4bc394` — both touched only prose (working notes; the
FR-RATE-64/NFR-RATE-14 correction this review's own Question 4 discusses), no code, no
markers). §3.7/§3.8's eleven W11 requirements are 0/11 evidenced — expected, W11 has not
started. No
disagreement between the roadmap's completion claim and the derived numbers.

**2. Omission.** No new omission beyond what the register already carries with named
owners: **F-W10-2** (FR-RATE-17 exposure-weight wiring, owner: portfolio-dataset
integration) and **F-W10-3** (`POST /rate-tables/{slug}/versions` has no route, owner: the
W15 rate-table editor) — both `docs/audit/register.md:26,29`, neither W11's. This review's
actual findings are research and shape gaps, Questions 3 and 5 below, not requirement-
ownership gaps, which is why they sit there instead of here.

**3. Skills and research — re-run, not appended to.** Carried from review 7: **no spike or
research artifact has ever exercised the ZEN engine's evaluate-side (Decision/graph
execution) behaviour.** Spike S1 (`docs/research/track-a-findings.md` F1/F14) tested
decimal-semantics correctness through the engine's expression path; spike S2 tested a bare
XGBoost booster's latency (`nthread=1`) in a Python loop, with no ZEN graph involved at all —
confirmed directly: `packages/pricing-core/src/pricing_core/rating/compile.py` is the only
file anywhere that imports `zen`, and only for `zen.compile_expression`'s syntax check.
Nothing anywhere calls the engine's `Decision`/evaluate API. W11's evaluator will be the
first code in this repository to do so, under real concurrency (NFR-OVR-1's 200 rps
sustained per replica), and nobody has verified the Python binding's behaviour under
concurrent async calls — whether it blocks the event loop, whether it is thread-safe.

> **Recommendation:** a short, targeted spike on the ZEN binding's evaluate-side concurrency
> behaviour, in the shape of S1/S2 (a dated finding in `docs/research/`, not a full skill),
> run at the *start* of W11's evaluator slice rather than discovered mid-slice. This is
> research, not a workstream deliverable in itself — it gates an architecture choice
> (whether `score_one` needs `run_in_executor` thread-pool offload) rather than adding a
> requirement.
>
> **Maintainer acceptance: accepted 2026-08-29 — and already discharged, so this line confirms
> the route rather than authorising it.** The spike ran and landed as
> `docs/research/zen-evaluate-concurrency.md` (PR #321), in exactly the shape proposed: a dated
> finding under `docs/research/`, not a skill, run at the start of the evaluator slice rather
> than discovered mid-slice. It answered the architecture question the recommendation named —
> sync `evaluate()` blocks the event loop, thread-offloaded `evaluate()` is worse than
> sequential, `async_evaluate()` is both non-blocking and faster — and that answer is now
> prework Ruling 5. **Owner: discharged.** One limit worth recording where the acceptance is,
> because it is the kind of thing a "discharged" mark otherwise hides: the spike measured an
> expression-only graph, and Ruling 5 carries a named follow-up to repeat it once a
> `model_call` custom node exists. Accepting 3.1 does not accept that follow-up as done.

**4. Document drift.** **The requirement-range omission has now fired twice, and it is a
finding about how rows are written, not two coincidences.** W10's own row read
`FR-RATE-14..21` and omitted FR-RATE-62 (added mid-workstream, corrected at W10's close,
`docs/roadmap.md:375`). W11's row reads `FR-RATE-34..42` and omits **FR-RATE-64**
(`03-rating-engine.md:162`, §3.7, decided 2026-08-18 with OQ-RATE-6, sitting between
FR-RATE-35 and FR-RATE-36 in the spec's own document order) — the same mechanism: an
append-only id landed inside a section after the roadmap row naming that section's range was
already written, and the row was never re-checked against the section's current membership.

> **Recommendation — landed while this review was being filed.** W11's row and NFR-RATE-14
> both needed exactly the correction this review was about to propose, and PR #314
> (`d4bc394`) shipped both before this PR opened: the row now reads `FR-RATE-34..42,
> FR-RATE-64 (added 2026-08-18 with OQ-RATE-6 — the row's original "FR-RATE-34..42" omitted
> it); NFR-RATE-1 is the hard target` (`docs/roadmap.md:376`), mirroring W10's own
> correction exactly as recommended; and NFR-RATE-14 now carries a dated amendment
> (`03-rating-engine.md:788`, amended 2026-08-27, W8) reconciling it to the 1.626 ms
> figure the register already cited, the same treatment NFR-RATE-13 got. Recorded here as
> confirmation, not as an open recommendation — updated in this branch after rebasing onto
> the fix, so this document does not assert something main had already made false. No
> action remains on either point.
>
> **The mechanical fix is still open, and is this review's actual proposal:** a numeric
> range in a workstream row is a derived summary of a spec section's membership, and it
> silently rots every time that section gains an append-only id — which is guaranteed to
> keep happening, since append-only is the rule (`CLAUDE.md` §5). The row should name the
> **section** (`§3.7`, `§3.8`) as the citation of record, with the numeric range kept only
> as a human-readable gloss beside it, never as the sole scope statement — so a check as
> cheap as "does every bolded FR- id in this section appear in the row it maps to" can catch
> the omission mechanically instead of at the next close. Whether that check belongs in
> `audit-docs.py` or `scope-audit.py` is an implementation choice for whoever owns it, not
> decided here. Landing the two individual fixes (above) does not close this half — the same
> mechanism will fire a third time on some future row unless the check exists.
>
> **Maintainer acceptance: the mechanical fix is accepted 2026-08-29. Unowned, and the
> mechanism has since fired a third time.** What binds is the shape: a workstream row cites
> the spec **section** as its scope of record, with any numeric range kept only as a
> human-readable gloss beside it, never as the sole scope statement.
>
> **Acceptance does not choose where the check lives.** The recommendation left that open —
> *"whether that check belongs in `audit-docs.py` or `scope-audit.py` is an implementation
> choice for whoever owns it, not decided here"* — and nothing in today's acceptance closes
> it. **Owner: unowned**, per review 4's question-5 rule.
>
> **The third firing, verified at `3edd75a` rather than predicted.** `docs/roadmap.md`'s W11
> row still reads `FR-RATE-34..42, FR-RATE-64`, and **FR-RATE-65 sits outside that range** —
> it is the requirement that defines `CompiledBundle` as a distinct runtime type, `03` §3.4,
> discharged by W11 Slice 1 Task 1.3, and `git grep -n "FR-RATE-65" -- docs/roadmap.md`
> returns nothing. So the recommendation's own prediction — *"the same mechanism will fire a
> third time on some future row unless the check exists"* — is now an observation. Recorded
> here rather than fixed here: correcting the row is a `docs/roadmap.md` edit and this is a
> review document.
>
> **The two individual corrections remain live and needed no acceptance line to bind.**
>
> **A second mechanism, distinct from the range omission and with a different fix.** The
> same period produced corrections to a *measured figure* — NFR-RATE-14 (#314) and
> OQ-RATE-2 across six locations (#317). The executor, who swept them, named why they were
> never caught together: **a fact copied into free prose is corrected only where the
> tooling structurally links the copy back to its source.** This repository has exactly one
> such link — the OQ mirror pair, enforced by `audit-docs` checks 4 and 23 — and it worked:
> the two OQ-RATE-2 copies could not diverge. Everywhere the same figure was merely *quoted in
> passing* — a requirement's rationale (FR-RATE-61's body), a roadmap cell, a
> `skills-map.md` row, and another module's open question (OQ-MODEL-11) — nothing but a
> literal-text grep could find it. So each correction event fixed the one location that
> prompted it, and every other copy survived until someone ran that grep.
>
> **Recommendation:** extend the pattern this repository has already built rather than
> invent a new check — the OQ mirror pair is the working precedent. The cheaper floor, if
> extending the structural link is too costly: make *"grep the figure or range across all
> of `docs/`"* a standing step in the correction procedure itself, so the sweep is not left
> to whoever happens to think of it. Credit: found and articulated by the executor while
> sweeping OQ-RATE-2.
>
> **A worked instance found while filing this review, in the tool that catches this
> everywhere else.** `scripts/audit-docs.py`'s own module docstring enumerates checks 1
> through 22; the code also runs check 23 (`:821`, the open-question mirror status this
> paragraph cites) and check 24 (`:760`, the §5.3/§5.6 route-column agreement), neither
> listed there; `.claude/skills/docs-audit/SKILL.md` separately states "twenty-three
> checks." Three artifacts, three counts, and nothing links them — the same mechanism this
> question names, surviving inside the instrument built to prevent it.
>
> **Maintainer acceptance: accepted 2026-08-29 — the proposal binds, the limb is not chosen,
> and the worked instance is fixed.** The recommendation is a disjunction — *extend the
> OQ-mirror pattern (`audit-docs` checks 4 and 23) to a measured figure,* **or** *make
> "grep the figure or range across all of `docs/`" a standing step in the correction
> procedure.* Accepting the proposal accepts that one of them must happen; it does not pick
> which, and satisfying either limb is what discharges it. Naming that explicitly, because
> declining one limb of a disjunction is not satisfying it, and a later reader checking only
> the mirror half would read a satisfied proposal as open. **Owner: unowned.**
>
> **The worked instance is resolved, verified at `3edd75a` rather than assumed from its age.**
> `scripts/audit-docs.py`'s module docstring now enumerates checks 1 through **24**, so 23 and
> 24 are no longer unlisted; and `.claude/skills/docs-audit/SKILL.md` no longer states a count
> at all, saying instead that *"the script's own module docstring is the numbered list, kept
> current there rather than counted here."* Three artifacts with three counts became one
> artifact with the count and two pointing at it — which is the structural half of this
> proposal applied to the instrument, arrived at independently of this line. **The general
> proposal is not discharged by it**: one instance being fixed is not the standing step, and
> the credit to the executor who found and articulated the mechanism stands as recorded.

**5. Shape — is the cut still right?**

**Yes, this review has a shape finding, and it is the one this pair of reviews exists to
raise.** The roadmap's workstream table numbers Phase 2 linearly — W11 (scoring), W12
(testing), W13 (dislocation), W14 (deployment) — and that numbering describes an execution
order the requirements themselves do not support:

- **FR-RATE-34** (`03:160`, W11) scores against "the Rating Version currently live in the
  target environment." FR-RATE-23 (`03:134`) is explicit that "live is a property of a
  **Deployment**, and the same Rating Version can be live in `uat` and not in `prod`."
  Deployment (FR-RATE-50, §3.10) and the Environment domain entity itself (FR-PLAT-28, `07`)
  are both **W14**'s (`docs/roadmap.md:379`) — three workstreams after W11. No Environment or
  Deployment class exists in code today (confirmed: only an unrelated app-config
  `Environment` enum in `backend/src/app/config.py`, and a bare `environment: str | None`
  field on an unrelated model in `packages/model-schema/src/model_schema/approvals.py`).
  `docs/workflows/wf-04-deploy-and-monitor.md` confirms the intended sequence directly: its
  Phase A step A4 has a Consumer System scoring test quotes *after* a Deployment (step A1)
  already exists — the workflow was never written assuming W11 alone reaches a live quote.
- **FR-RATE-40** (`03:172`, W11) refuses `approved` without a passing Regression Suite
  (FR-RATE-44, **W12**) and a Dislocation Run (FR-RATE-46, **W13**) — both unbuilt when W11
  starts. `docs/workflows/wf-02-model-to-rating-version.md` steps D1/D6/E2/E3 confirm this is
  load-bearing, not incidental: step E3 names a concrete failure (`EVIDENCE_INCOMPLETE`, a
  stale dislocation run) that cannot be produced before W13 ships.

Neither dependency is a defect in the *spec* — FR-RATE-23 and FR-RATE-40 read exactly as
intended. The defect, if it is one, is in treating W11 → W12 → W13 → W14's numbering as an
*execution* order, when the actual dependency graph has W11 needing pieces of W14 and
W12/W13 before W11's own two requirements can be *completed* — not merely started.

**Recommendation: no re-cut of the workstream boundaries.** Three reasons:

1. **The mechanism that handles this already exists and already works.** F-W9-1
   (NFR-RATE-13/14, carried to W11), F-W10-2 (FR-RATE-17 exposure weighting, carried to
   portfolio-dataset integration) and F-W10-3 (the rate-table-version route, carried to W15)
   are the same shape of problem at smaller scale — a workstream ships what it can and
   defers the rest to a named owner in the register. FR-RATE-34's live default path and
   FR-RATE-40's two preconditions are larger instances of the identical pattern, not a new
   one.
2. **The dependency is domain-inherent, not an artifact of the cut.** No renumbering of
   W11-W14 changes the fact that "live" cannot mean anything before a Deployment exists, or
   that a Dislocation Run cannot run before W13 builds it. Moving code between workstream
   numbers does not make Deployment exist sooner; only building it does.
3. **Re-cutting has a real cost the deferral does not.** Pulling a piece of
   FR-PLAT-28/FR-RATE-50 forward into W11 would blur W11's boundary into W14's territory for
   a shape (`Environment`'s promotion-order behaviour, `wf-04` step C2) that is not actually
   separable into a cheap shell — it would mean partially building W14 under W11's name.
   Holding W11 back until W12-W14 land first would idle the evaluator work — the thing at
   the most schedule risk per this same roadmap's own risk row (`docs/roadmap.md:392`) —
   behind three workstreams that do not touch it.

The precedent this leans on is Phase 1a's own: no single workstream (W9, bundle compilation;
W10, rate tables) was independently demo-able either, and neither was held to that bar. The
phase's demo-able outcome (`docs/roadmap.md:365-367`) already names the full
W11-through-W14 sequence as what is demonstrable, not any one workstream — consistent with
treating this as a completion-ordering fact about two specific requirements, not a mis-cut
of the workstreams that carry them.

**What this recommendation does not excuse:** FR-RATE-34 and FR-RATE-40 must each get an
explicit, named, dated deferral in the register when W11 closes — not silence, and not a
plan that quietly ships a stub and calls the requirement done. That is W11's own plan's job
(its DP1 and DP2), not this review's; this review's job is only to say the boundaries
holding it are the right ones.

> **Maintainer acceptance: accepted 2026-08-29 — no re-cut of Phase 2's W11–W14 boundaries.**
> The completion-ordering reading binds: FR-RATE-34's default-live path and FR-RATE-40's
> approval gate are not separable into a cheap shell, and neither pulling W14 forward nor
> holding W11 behind W12–W14 is worth its cost.
>
> **Acceptance makes the paragraph above binding. It does not meet it.** The clause is a
> condition on W11's close, not a recommendation that acceptance discharges: FR-RATE-34 and
> FR-RATE-40 must **each** get an explicit, named, dated deferral in
> [`register.md`](register.md) when W11 closes — not silence, and not a stub shipped and
> called done. Approving the no-re-cut recommendation is what puts that obligation in force;
> it is the price of the boundaries being held, and reading this date as having satisfied it
> would invert the clause.
>
> **Unmet as of 2026-08-29, verified rather than assumed.** `git grep -n
> "FR-RATE-34\|FR-RATE-40" docs/audit/register.md` at `3edd75a` returns exactly one line, and
> it is F-W9-2's prose about FR-RATE-61 — *"specialises FR-RATE-40's general approval-evidence
> gate, which W11 builds"* — a mention of the requirement inside another row, not a deferral
> of it. Neither id has a row of its own. **Two rows are owed at W11's close, and DP1 and DP2
> having since been ruled does not write them**: a ruling settles what the code does, a
> register row records what the workstream did not deliver, and those are different artifacts.
> **Owner: W11's close** — an owner this acceptance can name without a roadmap edit, because
> the review already named when the obligation falls due rather than who would carry it.

#### Proposals, consolidated — review 8

| # | Proposal | Kind |
|---|---|---|
| 3.1 | A short ZEN-evaluate-side concurrency spike, run at W11 evaluator-slice start | research |
| 4.1 | W11's roadmap row corrected for FR-RATE-64 | docs — **landed, PR #314** |
| 4.2 | Workstream rows cite the spec section as the row of record, range as gloss only | tool or convention |
| 4.3 | NFR-RATE-14 gains a dated amendment reconciling the 1.09 ms / 1.626 ms figures | spec — **landed, PR #314** |
| 4.4 | A distinct mechanism (a measured figure copied into free prose, not mirrored) — extend the OQ-mirror pattern (`audit-docs` checks 4 and 23) to it, or make a `docs/`-wide grep a standing correction step (executor's finding, credited) | tool or convention |
| 5.1 | **No re-cut** of Phase 2's W11-W14 boundaries; FR-RATE-34/40 get named deferrals inside W11's own plan | plan — no change |

**Maintainer acceptance: accepted as proposed, 2026-08-29.** All six rows bind from that date,
recorded per row with the owner review 4's question-5 rule now requires:

- **3.1 — accepted, and discharged** by `docs/research/zen-evaluate-concurrency.md` (PR #321).
  **Owner: discharged**, with Ruling 5's `model_call` follow-up expressly not covered.
- **4.1 — accepted, and already landed** (PR #314). **Owner: discharged.**
- **4.2 — accepted. Unowned**, and the mechanism has fired a third time on FR-RATE-65; see the
  per-item line above. Where the check lives is not decided by this acceptance.
- **4.3 — accepted, and already landed** (PR #314). **Owner: discharged.**
- **4.4 — accepted. Unowned**, and it is a disjunction: either limb discharges it, and this
  line picks neither. The worked instance inside `audit-docs.py` is separately resolved.
- **5.1 — accepted: no re-cut.** **Owner: W11's close**, which owes FR-RATE-34 and FR-RATE-40 a
  named dated register deferral each. **Binding from today and unmet today** — see the per-item
  line above for the verification.

**What is still owed, enumerated rather than counted** — because the first draft of this
sentence carried a tally and got it wrong, which is the defect questions 4 and 5 of this very
review are about. **Open: 4.2** (unowned, and now fired a third time), **4.4** (unowned, limb
unchosen), and **5.1's condition** (two register rows at W11's close). **Not open: 3.1**
discharged by the spike, **4.1** and **4.3** landed in PR #314 before this date. What this
acceptance mostly does is make the record say what the repository already did; a reader looking
for what is still owed should read the three named above and derive no total from them.

#### Sources — reviews 7 and 8

- `docs/audit/work/W9/README.md`, `docs/audit/work/W10/README.md` — closure records, reused
  per the skill's own guidance rather than re-derived.
- `docs/specs/03-rating-engine.md` §3.1-§3.11, §4.3, §5.1 — read directly at `07ae047`;
  NFR-RATE-14's amendment confirmed at `d4bc394` after rebasing.
- `docs/workflows/wf-02-model-to-rating-version.md`, `wf-04-deploy-and-monitor.md` — read
  directly.
- `docs/roadmap.md` §7 (workstream table, risk table) — read directly, plus a full-file grep
  for FR-RATE-60/61/63.
- `docs/audit/register.md` — rows F-W9-1, F-W10-2, F-W10-2-1, F-W10-2-2, F-W10-3.
- `scope-audit.py RATE` / `--endpoints`, run this session at `main@74b1b10`.
- Codebase, read directly: `backend/src/app/platform/rating_versions.py`,
  `backend/src/app/config.py`, `packages/model-schema/src/model_schema/approvals.py`,
  `packages/pricing-core/src/pricing_core/rating/compile.py`.

---

### Plan review 1 — at W6a's close, 2026-08-15

The first run of `CLAUDE.md` §14, raised as `NT-0001`. §13 asks whether a workstream did
what it said; this asks whether the plan still says the right thing. Five questions, in
order, each with a written answer — **"no change" included**, because a silent question is
indistinguishable from one nobody asked.

**1. Completion — what is actually done, derived from the specs.**

`scope-audit.py` and `req-coverage.py`, not recollection. Phase 1a's workstreams W1, W2,
W3, W4, W7a and W6a are closed with records on this page. `DATA` stands at 48/50
requirements (the two are measured NFRs), **33/33** endpoints and **38/38** catalogue
rules; `PLAT` is unchanged since W2 at ~35 of 61 with six endpoints owned by W14.

One disagreement with the plan, and it is the finding: the W6a row said "app shell,
dataset views, validation report view" — three items — while `01` §5.3 names **seven**
views. The row was written before the spec's view table was read against it. All seven
shipped, so the plan under-described the work rather than the work under-delivering; the
row is left as written and the closure record carries the correction, as W2's and W4's do.

**2. Omission — what the phase needs that no row names.**

*Browser authentication.* No workstream row mentions it. `07` §3.7 specifies the API side
completely and the client side not at all, and the gap was invisible from either end: the
backend's tests authenticate through dependency overrides, the frontend's stub `fetch`.
A real browser got 401 on everything. Raised as **OQ-PLAT-6** with a recommendation
(PKCE), fixed for the dev loop only.

*The pattern behind it.* Three of this workstream's six API findings — the version
timeline, the approve route, the reference read routes — were endpoints the spec's §5.1
table never declared. `scope-audit.py --endpoints` compares that table against the
published contract, so **an endpoint missing from both reads as complete coverage**. This
is the same shape as §13's "requirement coverage is not interface coverage", one level up,
and the honest mitigation is the one used here: derive the surface from what §5.3's views
must *do*, not from what §5.1 lists.

*Not an omission:* `pipelines/` remains correctly assigned to W7, and Playwright E2E is
deferred to W7 for a stated reason rather than forgotten.

**3. Skills and research — re-run, not appended to.**

`docs/skills-map.md`'s frontend rows survive contact with the code: Vue 3, Router, Pinia,
Tailwind, ECharts, openapi-typescript and Vitest are all cited and all still accurate.
`.claude/skills/vue-frontend` gains the development-identity procedure, which is exactly
the kind of non-obvious dev-loop step §12 exists to capture — it cost an entire workstream
before anyone noticed.

Two rows are now *ahead* of the code rather than behind it: TanStack Table and Vue Flow
are declared and not installed, which is right for their phases. One is behind: Pinia is
installed and registered with no store, because nothing has yet needed to outlive a route.
No skill has gone stale. No new external skill is proposed — and none would be installed
without the maintainer's approval in any case.

**4. Document drift.**

`CLAUDE.md` §2's `frontend/` mark and its "add with the code" note on `frontend.yml` were
both stale and are corrected in this PR. `01` §5.1 now carries four dated amendments from
W6a's findings. `open-questions.md` gains OQ-PLAT-6. The roadmap's own Phase 1a percentage
("~26 %") is an estimate from before any code existed and is left alone: it is a planning
figure, and re-deriving it per workstream would make it a second progress table
disagreeing with the one above it.

**5. Shape — are the remaining phases still cut in the right place?**

Yes, with one proposal.

*No change* to the 1a/1b split, to W5–W7, or to any phase boundary. Taking W7a (the data
seed) before W6a was the right call and the reason W6a rendered real data from day one;
nothing suggests a second such reordering is needed.

*Proposal — three items name `W6b` as their owner and W6b's row does not cover them.*
NFR-OVR-10's tabular chart fallback, browser authentication once OQ-PLAT-6 is decided, and
the frontend half of governance surfacing all point at W6b in closure records, while the
row itself reads "factor workbench, model detail, diagnostics" — modelling views only. An
owner naming a scope that does not include the work is how work becomes nobody's.

> **Correction, 2026-08-15.** As first written this said W6b "is not yet a row and should
> be". It is a row, at Phase 1b, and had been since the 1a/1b split; the review missed it.
> The substance survives — the three items still had no owner — but the change is to
> **extend** W6b, not to create it. Recorded rather than edited away, because a review that
> quietly fixes its own premise leaves nobody able to tell what was believed.

> **Recommendation:** extend `W6b` to `Frontend: factor workbench, model detail,
> diagnostics — **and the frontend platform**: browser authentication (FR-PLAT-55),
> accessibility beyond semantics (NFR-OVR-10), workspace selection`. It gains a dependency
> on OQ-PLAT-6 being decided. Spec and plan only; no code follows from a review
> (`CLAUDE.md` §14 rule 3).
>
> **Maintainer accepted 2026-08-15**, together with OQ-PLAT-6's recommendation (PKCE in the
> SPA for Phases 1–2, now FR-PLAT-55). Applied to W6b's row and to the Phase 1b table
> below.

---

## Pending proposals — for the §14 review at W11's close (drafted 2026-08-29)

**This is not a plan review and binds nothing.** It has no review number, no five questions
and no maintainer acceptance line, because the §14 trigger — a workstream close — has not
fired. It exists because two rule proposals had no durable home: one lived only in the
comments of [`#370`](https://github.com/yes-404/gi-pricing-plan/pull/370), now merged and
closed, and the other was never written down at all.
[`../../CLAUDE.md`](../../CLAUDE.md) §12 requires a decision to land as a dated artifact
rather than in chat, and a comment on a closed pull request is nearer to chat than to a
record. The review at W11's close folds these in, numbers them, and takes them to the
maintainer.

**Deliberately unnumbered — and that is the first finding.** Both candidates below had been
referred to as "rule 6". Read at `97fcb16`,
`docs/audit/work/nt-0010-0011-adoption/pilot-findings.md`'s P7 disposition read *"the
writer's half … is drafted as rule 6 and deliberately **not landed**"*, and P13's read
*"Rides with rule 6 into the §14 review"* — while the only text actually drafted under that
number, in `#370`'s comments, was candidate B. **Candidate A was promised, not drafted**, so
the number attached to whichever proposal a reader had in mind. A rule number is an
identifier, and an identifier assigned before the thing exists is the same defect as a count
written before the list is closed. **Numbering happens at acceptance.**

> **Corrected upstream while this entry was open.** PR #390 (`e9f9fa5`) fixed both
> dispositions: P7 now records the writer's half as filed unnumbered here, and P13 is marked
> **fixed** because its clause is already in rule 5 on `main`. The quotations above are
> therefore historical, and are kept with the tree they were read at rather than deleted —
> the collision was real and is why both candidates are unnumbered. Reporting it rather than
> editing another role's tree was the disposition; the owning role made the correction.

### Candidate A — do not move a branch someone is reading *(P7's writer's half; drafted here for the first time)*

> Rule 4's second half tells a **reader** to name the commit they read. The **writer's** half
> is cheaper and was missing: while a branch is under review or audit, do not push to it. A
> reviewer's finding is written against a tree, and moving that tree turns a correct finding
> into an apparently wrong one — the reviewer pays for a cost the author created, and pays it
> invisibly, because a stale finding reads exactly like a careless one. On 2026-08-29 the head
> of `#370` moved three times during an audit; the auditor filed a finding true of the tree
> they read and false by the time they wrote it. Freeze on request, name the frozen SHA where
> the reviewer will see it, and when a change genuinely cannot wait, say what moved and why
> rather than letting the reviewer discover it.

### Candidate B — declare up front that a count is not load-bearing *(recovered verbatim from `#370`)*

> Rules 1–5 each guard a *claim* you wrote. This one guards a claim's *form*. A count of items
> in a plan — prerequisites, findings, divergences, sites — is the first thing to age, because
> the items are discovered incrementally while the total is written once, and every later
> discovery silently falsifies it. The retrospective fix works and is expensive:
> [`../plans/2026-08-29-w11-scoring.md`](../plans/2026-08-29-w11-scoring.md) removed *"every
> bare count in this section … rather than corrected a third time, replaced by the enumerated
> list above"* — after the figure had already moved twice within an hour, in opposite
> directions, for unrelated reasons.
>
> The prospective form costs one clause and cannot go stale. The same plan's prerequisites
> heading reads *"named individually, because … a bare count of them is not load-bearing
> anywhere in this document"* — written before any count was wrong, and never corrected
> since. **Prefer the heading to the retraction.**
>
> Where a total is genuinely wanted, it carries the granularity it was counted at. Two readers
> who split the same list differently get different totals and each believes the other wrong —
> which is not hypothetical: one enumeration of the same divergences was filed as two, then
> four, then six, then none, and every one of those figures was correct at the granularity
> that produced it.

### Also carried, and not a new rule

**P13 sharpens rule 5 rather than adding to it.** The sweep's unit is every obligation the
record imposes, not every heading matching a pattern — an addendum to an existing ruling
never gets a new numbered heading, so a heading-keyed index is blind to precisely the changes
that arrive late. That clause is already in rule 5 as merged (`#370`), and P13's disposition
now reads **fixed** for that reason (PR #390). Nothing rides with a rule-6 proposal.

**Why both candidates are proposals and not edits.** [`../../CLAUDE.md`](../../CLAUDE.md)
§14: a review's output is a proposal with a dated maintainer acceptance line, never a change.
Landing either rule now would decide the thing the review exists to test — and the planner
does not rule its own proposals.

---

### Plan review 9 — at W11's close, drafted 2026-08-30 — **DRAFT, not filed**

`CLAUDE.md` §14's ninth run, triggered by W11's close (`docs/roadmap.md` §7). **This section is
not the filed review.** Slice 1 is complete (`c1a0dde`, all five tasks merged), but Slices 2–4 are
not: Slice 2 Task 2A is delivered as PR #435 with a second PR (#436, register row `F41`) open
behind it, both gate-in-flight as of this draft's base tree, and Slices 3–4 have plans but no code.
The §13 closure audit this review would normally reuse for question 1 has not itself finished.
Written now, at the lead's request, so it can be reviewed and extended as the remaining slices land
rather than started from nothing once they do. **Nothing below binds anything** until a maintainer
acceptance line is dated (§14's own rule); the status table after question 5 says which findings
are already stable and which need reconfirming.

**Base tree:** `origin/main` at `19eaabc` (this branch's parent, confirmed identical to
`origin/main` at the time of writing). Every citation below is to a file at that tree, a commit
reachable from it, or a reproducible command — not to the session-local working notes that first
surfaced several of these findings (`~/w11-handover-2026-08-29/*.md`), which will not outlive this
session (handover directories are not repository artifacts here). Where one of those notes first
found something, it is credited by name in prose; the finding itself is restated with its own
durable citation so this review does not depend on a path a future reader cannot open.

One correction made while drafting, recorded beside the finding rather than instead of it, per this
skill's own guidance for when a review's inputs turn out wrong: the evidence handed to this draft
reported a finding as **"Registered F42."** Verified directly against `docs/audit/register.md` at
`19eaabc`: no F42 exists. The finding itself (`req-coverage.py`'s occurrence-count mislabel, at a
scale of 238 of 326 rows wrong) was **withdrawn before filing** because it duplicates `F36`
(`register.md:42`) and will amend that row instead of opening a new one — not yet landed as of this
tree. Question 3 below cites `F36` as it stands today, not the amendment.

**Re-read after the evidence base itself changed mid-draft**, per the lead's note. Two changes:
a new §I (a leaf-plan Files-block gap, verified at `7952f76`, taken up under question 3 below), and
a correction to §F's own headline figure ("sixteen requirements, all on the NFR side" corrected to
"ten NFRs and six FRs"). The second one is not simply adopted — question 1 below re-derives it
directly against the row and the leaf plans, because the corrected figure and this draft's own
independent first pass disagreed with each other in a way neither fully explained, and both turn
out right for differently-scoped questions rather than one being simply wrong.

---

**1. Completion — reused where a fresh derivation exists, and provisional as a whole.**

Two independent, same-night derivations exist, and this review reuses rather than re-runs them:
`scope-audit.py RATE --sections 3.7,3.8 --extra 'FR-RATE-64,NFR-RATE-1,NFR-RATE-13,NFR-RATE-14'`
(pinned `6e548f8`), and a full read of `03` §3.7, §3.8 and §9 against every W11 leaf plan's own
coverage table (pinned `28ec778`). Both recorded the exact commands that produced them; re-running
now would confirm, not discover.

The row (`docs/roadmap.md:376`) names **13 ids**: `FR-RATE-34..42, 64` and `NFR-RATE-1, 13, 14`.
The section sweep returns 16 in scope, over-including three W12 ids (`FR-RATE-43/44/45`, confirmed
excluded by name in every W11 leaf plan) — net of that, section and row agree at 13.

**Beyond that 13, two different questions each have a correct, different-sized answer — kept
separate here because this draft's own first pass, and the evidence base it drew on, both
collapsed them into one number and disagreed with each other as a result (`phase-review-inputs.md`
§F was itself corrected mid-session, from "sixteen, all NFR" to "ten NFRs and six FRs," while this
draft's own first pass had independently reached fourteen — neither of those two prior numbers was
wrong so much as each answered a different question without saying so).**

**Question A — what does a W11 leaf plan claim that the row's text never says?** **Sixteen ids**,
matching the evidence base's corrected figure exactly: `FR-RATE-22, 24, 25, 56, 63, 65` (six —
each with markers in a W11 leaf plan's own Requirement Coverage table, enumerated per-id in the
scope-derivation pass) and `NFR-RATE-2, 3, 4, 5, 7, 8, 9, 11, 12` plus `NFR-OVR-6` (ten), none of
which appear inside the row's `FR-RATE-34..42, 64`.

**Question B — what is claimed by no row anywhere in `docs/roadmap.md`, full stop?** A narrower
**fourteen**, because four of Question A's six `FR-` ids are *also* named by **W9's** row
(`docs/roadmap.md:374`, `FR-RATE-1..13, 22..27, 56/57/58/59`) — just through a bare-number
continuation that a per-id search does not match, not through any text a naive reader would
recognise:

- `FR-RATE-22, 24, 56` are W9's, and W11's own tests re-exercise rather than newly discharge them
  — except `FR-RATE-56` is a deeper case than the other two: per independent corroboration, W11
  Task 1.4's test is *"the first proving the check is wired into the running service,"* i.e. real
  completion work on a requirement W9 had booked on weaker evidence. That is exactly why Question
  A, not Question B, is the one that should decide whether W11's own row mentions it — the row
  can be silent about *owning* `FR-RATE-56` while still being wrong to hide that W11's own plan
  did something to it.
- `FR-RATE-25` is also W9's by the same continuation, and **already tracked in full** as `F-W9-3`
  (`register.md:25`) — not a new finding under either question.
- `FR-RATE-63` (`03:87`, §3.1) and `FR-RATE-65` (`03:139`, §3.4) are claimed by **no** row at all.
  `FR-RATE-65` is already ruled W11's (Ruling 30,
  `docs/plans/2026-08-29-w11-fr-rate-65-attribution.md:33-47`, 2026-08-29; the mechanical row edit
  is outstanding, see question 5). `FR-RATE-63` is not yet ruled by anyone — see question 2.
- `NFR-RATE-10` and `NFR-OVR-5` sit **outside Question A's sixteen entirely** — no W11 plan claims
  either of them, which is a worse gap than "claimed by a plan, absent from the row" (see question
  2 for both). Question B's fourteen is Question A's sixteen, minus the four `FR-` ids W9's row
  already covers, plus these two.

**Both totals are correct, for the question each answers, and neither replaces the other** — the
practice this review's own Candidate B recommends below (a count states the granularity it was
taken at), applied to its own headline number rather than only proposed for someone else's.

**Since the pinned derivation (`28ec778`), Slice 1 Task 1.5 has merged (`c1a0dde`)**, converting
three of the above from a leaf plan's stated intent into register rows: `NFR-RATE-2`'s correctness
limb tested-but-mismarked and latency limb measured failing (`F35`, `register.md:41`),
`NFR-RATE-1`'s without-GBM half not established across five runs (`F38`, `register.md:44`),
`NFR-RATE-12`'s missing storage format (`F37`, `register.md:43`). Slice 1 is complete in the sense
this review can check today, not merely planned complete.

**What this question cannot yet answer:** a final tally for the close, because Slices 2–4 have not
landed and the §13 closure audit that owns the final verdict-per-id has not run. `FR-RATE-37`
(three limbs) and `NFR-RATE-9` (`F41`, PR #436, open) are named only to flag that this review has
deliberately not analysed them — both depend on Slice 2 outcomes not yet on `main`.

**Two PRs are moving under this review as it is written.** PR #435 (Slice 2 Task 2A) and PR #436
(`F41`, `NFR-RATE-9`) are both open at this base SHA, gate reported in flight. If either merges
before this draft is finalised, the list above should be re-checked against the new tree before
filing — deliberately not re-checked here, rather than guess at an outcome not yet on `main`.

**2. Omission — beyond the row-naming gap already covered under question 1.**

- **`NFR-RATE-10`** (`03` §9: audit events on "algorithm edits, rate table versions, bulk
  operations, **compilations**, approvals, deployments, rollbacks, and routing changes") is engaged
  by name — W11 Task 1.2 built the `RATING_COMPILE` Job — and built without the audit event:
  `backend/src/app/worker/rating_handlers.py`'s `_rating_compile` calls `compile_rating_version`
  then `blob_store.put`, no `audit.record`; every other rating platform module returns zero calls
  to it, against a positive control of 20 `platform/*` modules that do call it
  (`app/platform/audit.py:52`). Named in no plan, ruling or register row before this evidence pass.
  This is a real gap, not a deferred-and-tracked one, and needs one of the four verdicts at the
  close — which this review does not give; §13's verdicts are the lead's (`CLAUDE.md` §12).
- **`NFR-OVR-5`**, as under question 1: recorded inside `F22`'s range, owner-clause resolving to
  nothing. Distinct from `NFR-RATE-10` — `F22` carries no `RATE` ids at all (`register.md:13`), so
  the two are separate gaps that happen to share a shape.
- **`FR-RATE-63`**, as under question 1: evidenced, unclaimed, and — unlike `FR-RATE-65` — not yet
  put in front of anyone to rule. Recommend the same treatment Ruling 30 gave `FR-RATE-65` (a
  short, dated attribution ruling) before the close; this review does not make that call itself.
- **No new instance of `wf-01…05` evidenced by nothing** (review 2's finding): `wf-02` and `wf-04`
  are both cited by name in W11 rulings and register rows this pass touched. Not re-checked
  exhaustively; flagged "no change" per this skill's own rule that a silent question cannot be
  told apart from one nobody asked.
- **The gate-coverage cluster** (`F27(c)` + `F29` + `F33`) and `F-W9-3`'s clauses (4), (5), (6) are
  a different kind of omission — not undiscovered, but pre-designated by Ruling 29
  (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md:156-225`) to be decided **at this review**,
  and still undecided. See the decision point after question 5.

**3. Skills and research — one shape, five instances of it now.**

- **`delivery-process.md` §8's gate-in-flight control** ("announce an expensive verification…and
  check for one already in flight before starting," `delivery-process.md:170-172`) has no live
  mechanism carrying its announce half: `watcher.md:11-24`'s roster-state publication was meant to
  be the visible, shared state the rule itself says coordination needs ("coordination state must be
  visible, not relayed pairwise," `delivery-process.md:173`), and the one script that attempted it
  was a heredoc emitting a constant with a live timestamp, now withdrawn (`F31`, `register.md:37`).
  Three real contention incidents resulted, one producing a spurious `403 UNAUTHENTICATED` against
  the shared Postgres that did not reproduce on a quiet re-run. The compensating manual check
  (`pgrep -af 'bin/pytest'`) could not return a negative — it matches its own invocation string —
  and was not a discipline failure so much as a check broken from the moment it was written and
  never run against a quiet box to notice. The corrected form
  (`ps -eo pid,args | grep -E '[b]in/pytest'`) is known; **no mechanical replacement for the
  announce half has been built.**
- **The 50-word message rule** (`delivery-process.md:310-314`, landed 2026-08-29) was breached
  within hours of landing, by two different authors, each self-caught — nothing checked it at the
  point of sending.
- **The §14 trigger itself** has fired on time for none of the three workstream closes it has been
  due at: W9 and W10 were both reviewed retroactively, together, after the fact (reviews 7 and 8,
  both filed 2026-08-29 for closes on 2026-08-27 and 2026-08-28); this review, for W11, exists only
  because the lead explicitly tasked it, not because anything noticed the close and asked for it.
- **A fifth instance, and it is the sharpest one, because it is the fix for the other four.**
  `close-workstream` §5a (`.claude/skills/close-workstream/SKILL.md:340-368`) was written hours
  before this draft, by the same person who had just diagnosed this whole shape, to catch exactly
  it — a binding plan-review condition (review 8's 5.1, the `FR-RATE-34`/`FR-RATE-40` register
  rows discussed under question 5) whose demanded artifact nobody was checking for. §5a is
  **prose plus a suggested `grep`**: nothing in `audit-docs.py` verifies that an accepted
  condition's artifact actually exists. The remedy for "a rule with no check" was itself a rule
  with no check. Not worthless — a checklist step inside a procedure read start-to-finish is
  stronger than a rule floating loose in a process document — but the weaker of the two available
  instruments, chosen without the stronger one being ruled out.
- **These are one shape, not four unrelated notes**: a rule stated in prose with nothing making
  compliance visible at the moment of the action it governs. **Recommendation (3.1):** for the
  gate-in-flight control specifically, a lock file or equivalent wrapper around any full-gate
  invocation, written to a path every role can read, so the state is true by construction rather
  than announced and trusted. **Recommendation (3.2), same shape, no design proposed here:** either
  the §14 trigger, the 50-word rule and §5a's condition-artifact check get an equivalent mechanical
  check, or the maintainer accepts that all three remain enforced only by memory and says so rather
  than leaving the gap implicit.
- **A measurement-methodology gap, distinct from the process-control shape above.** `F38`
  (`register.md:44`, `NFR-RATE-1`'s without-GBM half) shows a single quiet run can pass while five
  runs under varied load reveal the true verdict is *not established* (two of five breach a 15 ms
  bound) — and shows why printing that one run's own distribution would not have caught it: a
  single run's spread is necessarily narrow near its own mean, so the criterion as written was
  satisfiable by exactly the run that got the verdict wrong. **Recommendation (3.3):** an NFR
  acceptance criterion measured near its bound should require repetition under varied load, not a
  reported distribution from one run — the leaf plan asked for the distribution and got exactly
  that, correctly, and it was not enough. This is a convention gap (a testing or `dev-commands`
  skill, or the leaf-plan-writing convention itself), not a spec gap; this review does not pick
  which document carries it.
- **A leaf-plan convention gap, found by the process working rather than failing.** Every W11
  route-adding leaf plan (Task 2B's `w11-2`; Slice 3's `w11-3-batch-scoring`; Slice 4's
  `w11-4-trace-sampling-persistence`) omits the regenerated OpenAPI contract
  (`docs/contracts/openapi/generated.json`) from its own **Files** block, despite adding a route
  that forces its regeneration (`scripts/generate-contracts.py:163`, `FR-PLAT-48`) — verified
  directly: `docs/plans/2026-08-29-w11-2-realtime-scoring-endpoint.md` has four `**Files**`
  headings and none names it. Two of the three plans do name `generate-contracts.py --check`
  inside a boilerplate gate-block, which is worse than silence in one respect — it reads as
  coverage while naming the detector, not the deliverable. The knock-on a plan reader would not
  predict: `frontend.yml`'s path filter includes `docs/contracts/openapi/**`
  (`.github/workflows/frontend.yml:21,29`, confirmed), so a route-adding backend PR arms a
  **second** CI workflow, and a red frontend job on it is a real failure, not a stray. Caught by
  the executor surveying integration points *before* writing any code (`delivery-process.md` §6's
  own ordering) — an instance of the process paying for itself, not the reverse.
  **Recommendation (3.4):** a plan step that adds or changes a route states the regenerated
  contract as a deliverable in its own Files block, and names the second CI workflow it arms —
  `writing-plans` is this charter's own mandatory skill and the natural home for the convention,
  but this review proposes rather than lands it, consistent with how it has treated every other
  skill-amendment finding above.
- **No change** on review 8's ZEN-evaluate-side research recommendation (its 3.1) — discharged,
  with its own named follow-up (the `model_call` node re-test) not yet due.

**4. Document drift.**

- **Three `03` §9 requirements leave their deciding variable unstated, found together because W11
  is the first workstream chartered to *measure* rather than build against them** (`03:797-798,
  807-808`):
  - `NFR-RATE-2` ("Tracing adds ≤ 20 % to scoring latency…") names no statistic — mean, p99, or
    otherwise. Its neighbour, `NFR-RATE-1`, states "p99" twice in the same table. Measured failing
    regardless of which statistic is meant (`F35`), but the margin depends on it.
  - `NFR-RATE-11` — **resolved.** Ruling 36 (`03:807`, 2026-08-30) settled what "logged" reaches
    (persistence, not only log lines) and reconciled it against `FR-RATE-43`'s Golden Quote store.
    No further action.
  - `NFR-RATE-12` — no storage format named, and format is what decides the verdict (2.6× over
    budget uncompressed, 4 % of budget under gzip). Already registered (`F37`, `register.md:43`)
    with its own remedy (a spec amendment plus a Slice 4 measurement obligation). No new action
    beyond what `F37` already carries.
  - **Recommendation (4.1):** state the statistic, the population it is measured over, and — where
    storage is involved — the encoding, in the same sentence as any numbered NFR's budget. Ruling
    34 (`docs/plans/2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md:112-130`) already states
    the population-scoping half directly for `NFR-RATE-1` ("if [the population] is ever narrowed…
    the narrowing must be written into the requirement"); `F37`'s own remedy is the encoding half
    for `NFR-RATE-12`. The statistic half has no precedent yet; this review adds it. **Predicted,
    not asserted:** every other module's §9 table has been read but not yet measured against —
    expect the same yield when each module's turn comes.
- **`lead.md`'s self-description is contradicted by this workstream's own record.** It states the
  lead is "the only role that mostly relays rather than derives." Self-reported or caught in flight
  this workstream: the planner (four citation errors, self-caught), the scope-derivation pass (a
  range false-zero it had just warned about, and an overstated contract finding, self-corrected),
  the decision-maker (two citation errors from reading a fragment), and the lead (five, by its own
  count). **Recommendation (4.2):** correct or drop the parenthetical — the charter is a document
  like any other, and this is drift between what it claims and what the record shows, even though
  the artifact is a role file rather than a spec.
- **No role file names the specific trigger this workstream's evidence names for the authority
  boundary**: a correctly-proved finding is exactly when choosing the remedy too is hardest to
  resist, evidenced twice each by the planner and the lead, and by the clean counter-example (the
  decision-maker's refusal to rule the Quote Context governance question, which is why a second
  viewpoint caught the `NFR-RATE-11` access-control question at all). **Recommendation (4.3):**
  name that trigger explicitly in every role file rather than a generic "stay in your lane." This
  review does not draft the wording — role-file edits are outside this charter's grant
  (`planner.md`'s Tools line names `docs/plans/` and `docs/audit/plan-reviews.md`, not
  `.claude/roles/`).
- **`docs/roadmap.md`'s W11 row is missing `FR-RATE-65`** (Ruling 30, mechanical edit outstanding)
  **and the sixteen ids question 1's Question A enumerates** — what W11's own plans claim that the
  row's text does not. See question 5 for the recurring mechanism this instantiates.
- **W12's row (`docs/roadmap.md:377`, `FR-RATE-43..45`) disagrees with its own charter text in both
  directions.** The charter names "regression runs"; no requirement defines one as such —
  `FR-RATE-44` presupposes a Regression Suite defined elsewhere, and the run itself exists only as
  a route (`03` §5.1:519) and a `pricing-core` signature (§5.2), neither cited by any requirement's
  own text. `FR-RATE-45` (the Quote Sandbox, `03` §5.1:518) is in the range and outside the
  three-item charter, and is separately claimed by W15's row ("quote sandbox + ladder
  waterfall") — double-homed. `RegressionRun` is documented only in the hand-authored contract tier
  (`docs/contracts/schemas/regression-suite.schema.json`), not in `03` §4's own text — a drift
  between the spec and its own contract, on the side `contract-guard`'s drift check does not reach.
  `GOLDEN_QUOTE_MISMATCH` is declared at `03` §5.1 (error codes owned by this module) and confirmed
  absent from `backend/src/app/errors.py`'s `RATING_ERROR_CODES` — not yet a live defect (nothing
  raises it today) but the same shape as `F29`, one workstream early. See question 5 for whether
  any of this should hold up W12's start.

**5. Shape.**

- **No re-cut of the W11–W14 boundary.** Review 8 already asked this and answered it (accepted
  2026-08-29): `FR-RATE-34`'s live-default path and `FR-RATE-40`'s two preconditions are
  domain-inherent dependencies on W13/W14, not artifacts of the cut. Nothing in this pass's
  evidence disturbs that finding; this review reaffirms it rather than reopening it.
- **Review 8's own binding condition on this boundary is still unmet.** Its 5.1 acceptance bound
  W11's close to a named, dated register deferral each for `FR-RATE-34` and `FR-RATE-40` — "not
  silence, and not a plan that quietly ships a stub and calls the requirement done" (review 8,
  question 5). Verified directly at this review's own base SHA: `git grep -n
  "FR-RATE-34\|FR-RATE-40" docs/audit/register.md` at `19eaabc` returns exactly one line,
  `F-W9-2`'s prose mention of `FR-RATE-40` inside a different row — **neither id has a row of its
  own.** Not a new finding; review 8 already found it and gave it an owner ("W11's close").
  Restated because §14's own rule is that nothing proceeds while an earlier review's finding lacks
  a resolution, and this one is still open at the moment this draft is written. `FR-RATE-34`'s own
  limb split (explicit-ref path delivered; live-default path deferred to W14, the 409
  `NO_LIVE_RATING_VERSION` standing in as the interim refusal) has reportedly been ruled since this
  evidence was gathered; the register row itself is not yet written, and this review does not write
  it — that is the closure record's artifact, not this one's.
- **W12 is not ready to build as currently scoped, independent of the W11–W14 boundary question.**
  Its row and its own charter text disagree in both directions (question 4), and two spec-level
  gaps sit under it (`RegressionRun` undeclared in `03` §4's own text; `GOLDEN_QUOTE_MISMATCH`
  unregistered). None of this is a boundary problem — the row's text is wrong about what W12 is,
  discoverable and fixable now, independent of anything W11 still owes. **Recommendation (4.4):**
  correct W12's row and close the two spec-level gaps before or as part of its opening slice.
  `CLAUDE.md` §0's table already treats "a capability not yet specified" as spec-change-first work;
  this is that case for the workstream about to start, not a later phase, and this review surfaces
  it rather than mandating a specific slice shape.
- **Review 8's proposal 4.2** (a workstream row cites the spec section as its scope of record, a
  numeric range only as a human-readable gloss) **was accepted 2026-08-29, left unowned, and has
  since fired on `FR-RATE-65` alone and now on this review's own Question-A sixteen under
  question 1** — a repeat firing at a much larger scale than either single-id instance it has
  already been checked against. Ruling 30 additionally found the proposal needs a temporal
  qualifier before it can be built as a mechanical check: "the section is the row of record as of
  the owning workstream's close; a requirement appended after that workstream closed belongs to
  whoever builds it" (`docs/plans/2026-08-29-w11-fr-rate-65-attribution.md:63-66`) — recorded here
  for whoever eventually owns 4.2, since nothing in that acceptance line disturbs it.
  **Recommendation (5.1):** given four firings (`FR-RATE-60`→W9 and `FR-RATE-64`→W11, both already
  fixed; `FR-RATE-65`→W11, ruled; this review's sixteen-id gap, six `FR` and ten `NFR`) at a
  growing and now much larger cost each time, 4.2 needs an assigned owner rather than continuing
  unowned — this review does not choose who.
- **A related, narrower proposal, its own owner already named.** Ruling 30 separately proposed
  that `.claude/skills/spec-change` require a new `FR-`/`NFR-` to name its workstream row in the
  same commit that mints it, symmetric with the existing rule for a new `OQ-`
  (`docs/plans/2026-08-29-w11-fr-rate-65-attribution.md:75-91`), naming "the same §14 review that
  owns 4.2" as its owner. **Recommendation (5.2):** adopt it — the preventive form of 5.1's
  reactive check, costing one sentence in an existing skill, within any role's standing grant to
  write a skill (`CLAUDE.md` §12). This review proposes the wording exist before W13 or W14 mint
  their own first append; it does not draft the sentence itself, on the same logic review 8 used
  for its own unowned proposals.
- **`F31`'s charter correction is drafted and ready, not decided here.** `watcher.md:11-24`'s
  roster-derivation clause has no live implementation; the withdrawal notice already states the
  honest replacement text in full. **Recommendation (5.3):** apply it — a role-file edit outside
  this charter's grant to make directly, but costing nothing further to draft.
- **No new instance of "a row nothing can be said to have closed"** (review 8's own smell) for W11
  itself — it spans several features but one technology layer, unlike W6b's Vue-view/OIDC/
  database-trigger span. W12's row, on today's evidence, is heading toward the same smell before it
  has even started (three named deliverables, a range that both under- and over-counts them) —
  flagged under question 4, not asserted here as a re-cut.
- **No new instance of "a phase exit criterion the phase cannot meet."** Phase 2's exit criterion
  (`docs/roadmap.md:365-367`) needs a live quote inside the latency budget; `NFR-RATE-1`'s
  without-GBM half is *not established*, not *failing*, and its own remedy is already scheduled
  (Slice 2 Task 2D, per `F38`'s register row) — the roadmap's own risk mitigation
  (`docs/roadmap.md:392`, "build the latency harness in W11 alongside the evaluator") did exactly
  what it was for. Worth watching at Phase 2's exit demo, not a finding now.
- **Candidates A and B, from the unnumbered "Pending proposals" section above, formally taken up
  here** — that section's own text anticipated this ("the review at W11's close folds these in").
  **Candidate A** (do not push to a branch someone is reading while reviewing or auditing it) and
  **Candidate B** (a count is not load-bearing unless stated at the granularity it was counted at)
  are both **recommended for adoption (5.4)** into `delivery-process.md` §15, alongside its
  existing five rules. Per that section's own stated rule, **numbering happens at acceptance** —
  this review does not assign either a rule number; that is the maintainer's action alongside the
  acceptance line, as it was left.

---

**Decision point, not a recommendation — Ruling 29 named this review as where it is decided, and
`CLAUDE.md` §12 reserves the decision itself to the lead.** The gate-coverage cluster (`F27(c)` +
`F29` + `F33`, `register.md:33,35,39`) and `F-W9-3`'s clauses (4), (5) and (6) (`register.md:25`) —
one mechanism comparing a spec-declared shape against its implementation on four separate axes —
are due a placement now: "decide whether it becomes a workstream row or a maintainer task"
(Ruling 29). Options, not a pick:

(a) **A dedicated slice**, bundled as Ruling 29's own author argued (one mechanism answers all
    four; a partial fix on any single row is not the target shape), landing inside a Phase 2
    workstream still to open (W12's own spec-change slice, or W15/W30).
(b) **A maintainer task outside the workstream ladder**, since none of the four blocks any
    requirement's own delivery today.
(c) **Split by cost** — the `mypy` `files` widening (`F33`) is closer to a config change than the
    other three; taking it alone first and bundling the remaining three later trades the "one
    mechanism" argument for faster partial progress.

This review's own reading favours (a), for the reason Ruling 29 already gave — but the choice, and
which workstream if (a), is the lead's to rule, not this document's.

---

#### Status of this draft, by question

| Question | Status | What would change it |
|---|---|---|
| 1. Completion | **Provisional** | Final per-id tally needs Slices 2–4 landed and the §13 closure audit run; PRs #435/#436 may also land before filing |
| 2. Omission | **Settled**, except the gate-coverage cluster (open, see decision point) | Slices 2–4 could surface more; none expected to remove what is listed here |
| 3. Skills and research | **Settled** | Process-control findings do not depend on the unbuilt slices |
| 4. Document drift | **Settled** for what is found; more likely once Slices 2–4's own spec sections get read as closely as Slice 1's was here | A fresh drift pass once Slices 2–4's plans exist on `main` |
| 5. Shape | **Mostly settled** — no-re-cut and W12-readiness stand on their own; the gate-coverage placement and `F31`'s charter fix are open by design (the lead's and a role-file owner's, respectively) | The lead's ruling on the decision point; Slices 2–4 landing does not itself change this question |

#### Proposals, consolidated — review 9 (draft)

| # | Proposal | Kind |
|---|---|---|
| 2.1 | `FR-RATE-63` gets a Ruling-30-style attribution ruling before the close | ruling needed |
| 3.1 | A lock-file/wrapper mechanism for the gate-in-flight control, replacing the announce-and-trust pattern §8 currently relies on | process/tooling |
| 3.2 | Either the §14 trigger, the 50-word rule and `close-workstream` §5a's condition-artifact check get a mechanical check, or the maintainer accepts and states that all three are enforced only by memory | process — maintainer to weigh |
| 3.3 | NFR acceptance criteria measured near their bound require repetition under varied load, not a one-run distribution alone | convention (skill or leaf-plan template) |
| 3.4 | A route-adding plan states the regenerated OpenAPI contract as a Files-block deliverable and names the second CI workflow it arms | convention (`writing-plans`) |
| 4.1 | A numbered NFR budget states its statistic, population, and (where storage is involved) encoding, in the same sentence as the number | spec-writing convention |
| 4.2 | Correct or drop `lead.md`'s "only role that relays" parenthetical | role-file correction |
| 4.3 | Name the authority-boundary trigger (question 4's shape) explicitly in every role file | role-file amendment |
| 4.4 | Correct W12's row against its own charter; declare `RegressionRun` in `03` §4; register `GOLDEN_QUOTE_MISMATCH` before or at W12's opening slice | docs + spec-change |
| 5.1 | Assign review 8's proposal 4.2 an owner, now that it has fired a fourth time at a much larger scale, carrying Ruling 30's temporal-qualifier refinement | tool or convention — unowned since 2026-08-29 |
| 5.2 | Amend `.claude/skills/spec-change` so a new `FR-`/`NFR-` names its workstream row in the same commit that mints it, symmetric with the existing `OQ-` rule (Ruling 30's own proposal) | skill amendment |
| 5.3 | Apply `F31`'s charter correction to `watcher.md` — text already drafted in the withdrawal notice | role-file edit |
| 5.4 | Adopt Candidates A and B (branch-freeze while under review; a count states its own granularity) into `delivery-process.md` §15 | process rule — numbered at acceptance |
| DP-1 | Decide the gate-coverage cluster's placement (options a/b/c above) | **decision, the lead's — not a proposal** |

**Maintainer acceptance:** _pending._ This is a draft circulated to the lead ahead of the
maintainer, not yet presented for acceptance. Before it can be filed: Slices 2–4 land (or are far
enough along that question 1's tally is real rather than provisional), the §13 closure audit
completes, review 8's still-open binding condition (the `FR-RATE-34`/`FR-RATE-40` register rows)
is met, and the decision point above is ruled by the lead. Everything in questions 2 through 5 is
not expected to change on those events, but will be re-read against whatever tree is current
before filing, per this document's own rule that a claim names the tree it was checked at.

#### Sources

- `docs/roadmap.md` §7 (workstream table, risk table, Phase 2 demo-able outcome) — read directly at
  `19eaabc`.
- `docs/audit/register.md`, in full — read directly at `19eaabc`.
- `docs/specs/03-rating-engine.md` §3.1, §3.4, §3.7–§3.9, §5.1, §9 — read directly at `19eaabc`.
- `docs/process/delivery-process.md` §8, §15 — read directly at `19eaabc`.
- `backend/src/app/errors.py` — read directly to confirm `GOLDEN_QUOTE_MISMATCH`'s absence from
  `RATING_ERROR_CODES`.
- `.claude/roles/watcher.md`, `.claude/roles/planner.md` — read directly.
- `.claude/skills/close-workstream/SKILL.md:340-368` (§5a) — read directly at `19eaabc`.
- `.github/workflows/frontend.yml:10,18-29` — read directly to confirm the `docs/contracts/
  openapi/**` path filter.
- `docs/plans/2026-08-29-w11-2-realtime-scoring-endpoint.md` — read directly (`grep -c
  '\*\*Files\*\*'` returns 4, none naming `generated.json`), at `19eaabc`.
- Rulings 29, 30, 34, 36 — `docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`,
  `2026-08-29-w11-fr-rate-65-attribution.md`,
  `2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md` — read directly; Ruling 36 as amended
  into `03-rating-engine.md:807`.
- `git log`, `git grep`, `git merge-base --is-ancestor` against `origin/main` at `19eaabc` — run
  this session to confirm the ancestry and absence claims above, not assumed from the working notes
  that first reported them.
- `gh pr view 436` — run this session to confirm `F41`'s content and open status.
- Review 8 and the unnumbered "Pending proposals" section, both above in this document — read
  directly here rather than re-derived.
- Session-local working notes that first surfaced several of the above, credited by name in prose
  and not cited as resolvable paths: `phase-review-inputs.md`, `w11-scope-derivation.md`,
  `close-audit-baseline.md`, `register-rows-owed.md`, `eta.md` (all
  `~/w11-handover-2026-08-29/`, 2026-08-30). None of this review's findings depends on a reader
  having access to them.
