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
`docs/notes/`, and `d4bc394` (#314) touched only the two lines review 8 names.

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

### Plan review 9 — at W11's close, 2026-08-30 — **FILED, with its drafting history intact**

> **Status header, added on filing 2026-08-30.** This review was drafted against `origin/main`
> at `19eaabc` **while W11's close was in doubt** — the maintainer had stopped the run at the
> end of Slice 2, and for several hours no close was going to happen. The planner's own verdict
> at that point was *abandon, do not land it*, on the sound ground that filing a §14 review of a
> workstream that never closed would misstate the record.
>
> **W11 then closed**, at `1da81cd`, under a delegation from the maintainer to the lead. That
> voids the reason for abandoning it, so it is filed rather than discarded.
>
> **Two things a reader must hold, and they are not the same.** The **operative** §14 review for
> W11's close is the closure record's §7 (`docs/audit/work/W11/README.md`) — short, and written
> against the closed state. **This is the fuller working analysis**, kept for its evidence and
> its derivations, several of which the closure record cites rather than repeats.
>
> **Its forward-looking statements are superseded by the close.** Where it says Slices 2–4 have
> not landed, or that a tally cannot yet be final: Slice 2 landed in full, Slices 3 and 4 never
> ran, and the final verdicts are in the closure record. Nothing here is edited to hide that —
> a review is a dated artifact, and rewriting its predictions after the fact destroys the record
> of what was believed when the plan was being tested, which is the whole point of §14.

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
large-fraction scale still being re-measured — this draft deliberately does not quote the exact
count, since it moved once already between two of this evidence base's own passes and is not
load-bearing to anything below) was **withdrawn before filing** because it duplicates `F36`
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
**fourteen, enumerated rather than left as arithmetic** (the arithmetic below is shown once, as
the derivation, not as a substitute for the list — restating only "sixteen minus four plus two"
is exactly the kind of bare count Candidate B warns against, and was not enough for this figure
to be checked without a second round-trip):

> `FR-RATE-63, FR-RATE-65` (two) · `NFR-RATE-2, 3, 4, 5, 7, 8, 9, 10, 11, 12` (ten) ·
> `NFR-OVR-5, NFR-OVR-6` (two). **2 + 10 + 2 = 14.**

That is Question A's sixteen, minus four `FR-` ids *also* named by **W9's** row
(`docs/roadmap.md:374`, `FR-RATE-1..13, 22..27, 56/57/58/59`) through a bare-number continuation a
per-id search does not match, plus two ids (`NFR-RATE-10`, `NFR-OVR-5`) that sit **outside**
Question A entirely, because no W11 plan claims them either — a worse gap than the other twelve's
"claimed by a plan, absent from the row," and the reason the addition is not optional:

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
- `NFR-RATE-10` and `NFR-OVR-5` are the two ids named above that sit outside Question A entirely
  (see question 2 for both).

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
- **Two fresh defects on `F-W9-3`'s own row, found by the same kind of limb-level audit that
  produced it — verified directly, both concrete claims.** `docs/audit/work/W9/README.md:27`
  verdicts `FR-RATE-22..27` "delivered" as one row on a bare marker count (22: 3, 23: 1, 24: 4,
  25: 1, 26: 1, 27: 1); opening the tests shows three of those six markers are the *same* test
  (`packages/model-schema/tests/test_rating_version.py:44-47` stacks `@pytest.mark.req` for
  `FR-RATE-22`, `26`, `27` on one pydantic parse-and-round-trip, `test_the_full_43_contract_parses`).
  A limb-level decomposition of four of the six (22, 23, 24, 26) found 21 limbs, 7 enforced and
  14 with nothing enforcing them (2/6, 1/4, 3/5, 1/6 respectively) — **not evenly bad**:
  `FR-RATE-24`'s three of five limbs (self-containment, content hash, zero-DB-access with a
  positive control) are solidly built and tested, and only its caching/distribution tail is weak
  and already known to be. Two limbs are new, unregistered gaps: **`FR-RATE-22`'s
  pins-completeness gap** — `compile.py:431-434` refuses only total absence of `algorithm_ref` or
  `pins`, verified directly, with nothing cross-checking that `pins.rate_tables` covers every
  table the algorithm's own steps reference, so a partial under-pin compiles clean and surfaces
  later as a missing key at hydration rather than a named refusal — and **`FR-RATE-26` is
  near-totally unenforced**: `rating.py:131` declares `effective_from: datetime | None = None`
  (verified directly) and no path to `approved` requires it be set. **Same treatment as `F27(c)`
  and `F-W9-3` above, and for the identical reason**: this is a missing check against what a
  closed workstream declared delivered, not a defect in what W9 built — reopening W9's close is
  the maintainer's alone (`CLAUDE.md` §13) — and these two need a verdict this review does not
  give.

**3. Skills and research — one shape, seven instances, reframed by an eighth.**

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
  **four times, after a remedy for it had been formally adopted** — not merely observed as broken
  once. That is a sharper claim than "the rule was breached": adopting a remedy is not the same as
  the remedy holding, which bears directly on how much confidence this section's own
  "adopt a mechanical check" recommendations should carry if any of them stop short of mechanical.
  Nothing checked it at the point of sending, before or after adoption; each breach was caught by a
  different teammate reading the message, never by the author and never by a check.
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
- **A sixth instance, self-reported, and the strongest of the six because it controls for
  knowledge and motivation, which the other five do not.** In one night, and immediately after
  diagnosing this exact class, the lead broke three rules it had itself just written down: the
  50-word message rule (above — by then already a case of a formally adopted remedy breached
  anyway); the elided-prefix continuation trap
  (`w11-scope-derivation.md`'s own "Method notes" — "before reporting any id as absent, search the
  range and slash forms," which is precisely what a first pass over `FR-RATE-22/24/25/56` skipped);
  and the rule that a bare count is not load-bearing (Candidate B, question 5 — restating "sixteen"
  and then "ten NFRs and six FRs" without the enumerated list underneath either figure, corrected
  above under question 1). Each was caught by a different teammate reading the artifact, none by a
  check. Where the other five instances leave room to read the gap as an execution shortfall, this
  one does not: the person with the most reason to comply, right after writing the rule down, still
  needed a second reader to catch it.
- **A seventh instance, and a different failure inside the same family: a control that was
  adopted and followed, aimed at the wrong property.** §8's own justification for serialising gate
  runs is CPU/load contention — "two suites at once drove load average past 11 and both read as
  stalled agents" (`delivery-process.md:166`). But `backend/tests/conftest_db.py`'s
  `_empty_the_database_after_the_session` fixture (`scope="session", autouse=True`,
  `conftest_db.py:251-252`) truncates the whole shared Postgres at teardown **regardless of
  load** — so two pytest sessions running at the same time against it can mutually destroy each
  other's fixtures with zero CPU contention at all. Following §8's own stated reasoning (avoid
  contending for CPU) does not by itself prevent this, because the hazard the rule argues from and
  the hazard that actually bites are different properties — compliance and safety came apart, not
  because anyone was careless but because the rule's own justification pointed at the wrong thing.
  **This was not a fresh discovery — it was already documented**, `.claude/skills/python-test/
  SKILL.md:284-319`, "That teardown makes two concurrent runs mutually destructive," measured
  2026-08-24 across three overlapping runs, six days before this workstream re-hit it. The skill
  gives two remedies, and the first shares this section's own instance 2's defect: *"Serialise…
  `pgrep -af 'pytest'` before starting"* is the identical self-matching check, so retrieving this
  documented remedy would not by itself have helped. The second — **"give each session its own
  database"** (`test_database_url()` already reads `GIP_TEST_DATABASE_URL` before falling back to
  a shared default, `conftest_db.py:35,39`; `createdb gipricing_$USER_$SLOT` and point at that) —
  sidesteps the coordination problem entirely rather than requiring a working check.
  **Recommendation 3.1 is therefore not to build anything**: adopt the already-documented,
  already-scoped per-session-database remedy the skill names, rather than design a new lock file
  against a hazard whose fix already exists and does not need one.
- **These are one shape, not six unrelated notes**: a rule stated in prose with nothing making
  compliance visible at the moment of the action it governs, or (this section's seventh instance)
  visible but aimed at a proxy for the real hazard rather than the hazard itself.
  **Recommendation (3.2), no design proposed here:** either
  the §14 trigger, the 50-word rule and §5a's condition-artifact check get an equivalent mechanical
  check, or the maintainer accepts that all three remain enforced only by memory and says so rather
  than leaving the gap implicit.
- **An eighth item that is not an eighth instance — it reframes the seven above, and the lead
  called it the strongest input of the night.** Raised by the decision-maker, of its own work:
  *"Every ruling that improved on its own first draft did so by finding something already in the
  repository… The failure mode wasn't insufficient thinking; it was answering before reading the
  artifact that already had the answer."* Three of its eight tabled instances are independently
  verifiable from this document alone: the `F42`/`F36` duplicate this draft's own opening already
  corrects; the elided-prefix trap this draft's question 1 re-derived, which (per the
  decision-maker's finding) the lead had already written down on 2026-08-25 before repeating it on
  `roadmap.md:374` five days later; and this section's own seventh instance, whose remedy —
  per-session databases — was sitting in `python-test/SKILL.md` the whole time. **The claim that
  matters is sharper than §A's**: §A says rules exist and nothing enforces them, which argues for
  building enforcement. This says the *answer* already existed, indexed and searchable, for every
  instance checked — so a new control would not have helped where a `git grep` before writing
  would have. **The proposal explicitly warns against the obvious response**: "read more before
  writing" is §A-shaped and fails the same way, because a general intention is exactly what these
  instances show does not survive the moment of writing. What worked instead, every time (per the
  same finding), was **one grep command attached to a specific act** — before allocating a finding
  id, before writing a literal into a spec, before filing a defect as new. **Recommendation
  (3.5):** wherever this review has proposed a mechanical check above (3.1's per-session database
  aside, since that removes the need to check anything), consider whether a one-command grep tied
  to the specific writing act would catch more of this class more cheaply than a general
  enforcement mechanism — this review flags the question rather than answering it for each case.
  **One caution carried forward rather than dropped**: every instance in this class was caught, by
  a second person reading the artifact — so the table is a *lower bound*, and says nothing about
  how many were not caught.
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
- **A distinct measurement-practice gap: five instances tonight of a figure labelled with a tree
  it was not taken on** — self-named by the batch executor after producing one, having caught two
  others earlier the same session; three of the five are the lead's own, by the lead's own count.
  One is this draft's own opening correction above (the withdrawn-finding's scale, first quoted
  from a figure re-measured on a moving tree, now stated without the number rather than repeated).
  **Why this earns its own entry rather than folding into question 4's citation-error discussion**:
  every instance is *correctly formatted* by `CLAUDE.md` §13's own standard — each names a tree, a
  PR state, or a file, which is exactly what makes a citation survive review on a first read.
  **Naming a tree is not the same as having measured on it**, and nothing in the current standard
  distinguishes the two: a figure taken on a working tree and labelled with the branch's base SHA,
  a `gh` read reported as current after a push landed behind it, a gate's own stale result file
  from three hours earlier read as the current run's — caught only by an `mtime` check. **The
  fifth is the sharpest of the five because no reasoning error was involved at all**: correct
  extraction, correct arithmetic, wrong source file. **Recommendation (3.6), mechanical rather
  than a discipline reminder:** a figure quoted in a durable artifact is produced by a command that
  prints its own tree in the same invocation — `git rev-parse HEAD` beside the number, so the
  label cannot drift from the measurement because both come from one run; a file read as evidence
  is quoted with its `mtime` beside it. Both are one flag each, and both fail loudly rather than
  silently — the same "true by construction" standard 3.1's per-session-database fix meets, applied
  to citation rather than coordination.
- **A related but distinct pattern: a bounded query answers a narrower question than the one
  asked, and the answer looks complete.** Self-reported, four instances tonight: an ANSI-blind
  `grep FAILED` that missed escape-coded output, a grep for a phrase that had wrapped across a
  line break, a `head -5` that silently dropped the remainder, and a stability check against a
  guessed cutoff. **One shape, not four lessons** — each query was answered correctly for the
  literal scope it encoded, and each answer was then read as though it covered the broader
  question actually being asked. Distinct from this section's tree-mislabelling class (that names
  a real tree wrongly; this runs a real command too narrowly) and from §J's retrieval failures
  (nothing here was already known and skipped — each query was novel, just under-scoped).
  **Recommendation (3.9):** unlike 3.6, no single mechanical fix generalises across `grep`, `head`
  and a statistical cutoff the same way — this review names the shape and leaves whoever owns
  `dev-commands` or a testing skill to decide whether a query's own scope stated beside its result
  is worth a checklist item, or whether review density (§D's own finding about what that already
  buys) is the cheaper answer here.
- **Two smaller items, self-reported, each with its own remedy already applied.** A correction
  that states a new position without naming what it supersedes leaves both readings live until
  someone checks — three incidents tonight, one of which would have reverted work the executor had
  already correctly completed under the position being silently replaced; carried into Q5's
  Candidates A/B discussion below as a third, unnumbered candidate for the same rule set. And a
  3h22m stall from relying on notifications rather than a standing 15-minute check the lead's own
  rule already requires — self-diagnosed, and a background watcher is now armed rather than relied
  on to be remembered, which is this section's own recurring fix applied to itself.
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
- **A frozen leaf plan's line-number citations go stale under any insertion above them — and the
  repository already has the rule that would have prevented it, unfired.** Three forms of the same
  locator behave differently under edit: a **symbol** (`approvals.submit` inside
  `submit_for_review`) stays stable under any edit that does not rename it; a **line stated with
  its tree** (`:178` at `e16c459`) ages into a historical statement that still resolves, forever,
  with no maintenance; a **bare line** (`:178`, no tree) rots silently on the next edit above it and
  gives no signal when it does.

  **A controlled comparison, not an argument, settles which form to prefer.** The same fact was
  cited twice, hours apart. `docs/audit/register.md`'s `F44` row (confirmed directly at
  `origin/main`) writes: "at `e16c459`… `rating_versions.submit_for_review` (`:153`) calls
  `approvals.submit` at `:178`" — the tree is stated once and covers both numbers. The lead's own
  dispatch cited the same call as a bare `:178`, no tree. Verified directly, both sides: at
  `e16c459` the citation is exactly right; at `origin/main`'s current tip, `submit_for_review` is
  now at `:214` and the call to `approvals.submit(` at `:239` — a real 61-line shift from Task 2B's
  merge, landing between the two citations being written. F44's form still resolves correctly,
  unmaintained, because it never claimed to describe an undated present; the bare form now points
  at whatever else occupies `:178` today, silently.

  **The rule that would have caught this already exists.** `CLAUDE.md` §13: "a reference carries
  its scope and its measurement… a `Verified` date carries the tree"
  ([NT-0004](../../docs/notes/0004-a-reference-that-resolves-only-for-the-writer.md)). The
  auditor's F44 row followed it; the lead's dispatch did not, and the lead is the one who cites §13
  at other people. **Three instances tonight of an existing rule failing to fire on someone who
  already knew it**: this locator (§13's own scope rule, against its own author); the 3h22m
  notification stall two bullets above (the lead's own standing 15-minute check, not run); and the
  reporter's charter, which — independently, and now confirmed landed at `origin/main`
  (`.claude/roles/reporter.md`, "The Slack post: facts only, never inference") — went from silent
  on inference to an explicit two-sided rule: a named whitelist of permitted sources paired with
  the concrete violating lines as examples, which this review's own 4.6 below independently
  proposed and can now mark discharged rather than pending. **The recommendation this supports is
  not "add a rule."** All three rules already existed. It is that **a rule which can only be
  honoured by remembering fails precisely when the person invoking it is busy and confident — which
  is when it matters** — and the reporter's own fix is the model: it did not add a reminder, it
  changed the artifact from silent to enforcing, so the next reader inherits a structure rather
  than an absence.

  **Recommendation (3.10):** a frozen leaf plan (and, by the same rule, a dispatch or a register
  row) cites a locator as **symbol, or line stated with its tree** — never a bare line number — so
  the citation either survives the edit that would break it or names the point at which it stopped
  being current. A sweep across frozen leaf plans found **4 wrong across 88** such citations under
  the bare form. Squarely a `writing-plans` convention, proposed rather than landed, per this
  review's standing practice above. **Credit:** the auditor designed the F44-vs-dispatch comparison
  that settles the form; this review generalises it.

  **A related class, three instances tonight, only this one developed elsewhere in the review**:
  the locator above; a re-plan the lead performed around a quota constraint without first testing
  whether the constraint was removable (a rerun request — which a quota-exhausted repository
  refuses outright — resolved it in ten minutes, run last rather than first, after inverting §8
  for two agents and escalating a 40-minute infrastructure question to the maintainer); and an
  executor's own storage-bucket reasoning error, self-reported as the same shape. **The class, not
  any one instance, is what is worth naming**: an argument or inference stood in for a cheap,
  direct test that was available the whole time. This review does not attempt one mechanical fix
  for a class this varied — a locator, an infrastructure assumption and a storage error share no
  single instrument — and names the shape once so a future instance is recognised faster than
  these three were.
- **No change** on review 8's ZEN-evaluate-side research recommendation (its 3.1) — discharged,
  with its own named follow-up (the `model_call` node re-test) not yet due.
- **`CLAUDE.md` §13's four verdicts have no slot for what `NFR-RATE-2` actually produced: adverse
  evidence, not absent evidence.** All four verdicts ("delivered but untested," "deferred with an
  owner," "reassigned," "not started") presuppose a gap in evidence; `NFR-RATE-2` was measured
  properly and found failing, and "deferred with an owner" is the closest fit only by discarding
  the number, which is the most valuable thing Task 1.5 produced. Two further mismatches:
  a workstream can fully discharge its *own* scope (W11 committed to *measure* `NFR-RATE-2`, not
  meet it) while the requirement's own state is "failing" — both true at once, which §13 has no
  way to say without conflating them — and `NFR-RATE-2` itself needs two verdicts, one per limb
  (`FR-RATE-37` needs three), where §13 assumes one verdict per id. **Not an isolated case**:
  `NFR-RATE-1`'s without-GBM limb (`F38`) is in the identical state — measured, unstable, not
  established — and `FR-RATE-25`'s control-intent clause (`F-W9-3` above) is a fourth shape again:
  marked with a real test, and enforced nowhere the marker claims. Three W11-touched rows need a
  verdict this standard has no slot for, not one. **The perverse incentive this leaves in place**:
  an NFR nobody measures books cleanly as "delivered but untested," and an NFR someone measures and
  finds failing has no clean verdict at all — the standard rewards not looking.
  **Recommendation (3.7), not drafted here**: `CLAUDE.md` §13 needs a fifth verdict (or a
  qualifier on the existing four) for measured-and-failing, and an explicit rule for how many
  verdicts a multi-limb requirement takes. This is a `CLAUDE.md` §13 amendment — the maintainer's
  alone (`CLAUDE.md` §12) — and this review surfaces it rather than proposing wording.
- **The one constructive recommendation in this workstream's evidence: prefer the design whose
  safety property has a failing case.** This did not arrive by generalising it across everything
  above — that generalisation was tried and withdrawn as asserted rather than enumerated, twice,
  before this draft could adopt it. **Checked directly against this section's own bullets rather
  than carried from that count, and the corpus is stated because a count without one is the same
  defect a third time**: **two, within this section's own bullets** — not a claim about this
  document as a whole or about the wider evidence base — qualify as "a check that exists and is
  structurally incapable of reporting the failure it is asked about," as opposed to being merely
  related to that shape: the `pgrep` self-match (instance 2, duplicated verbatim inside instance
  7's "serialise" remedy, so one defect with two sightings rather than two instances) and the
  authorisation example below. **The rest of this section is a different, adjacent shape each
  time, worth telling apart rather than folding in**: the announce half, the §14 trigger and
  §5a's suggested `grep` are *absent* checks, not defective ones — there is no mechanism to be
  structurally blind, only none built yet. §8's CPU justification for the database-truncation
  hazard *measures correctly at the wrong target*, which is a different defect from measuring
  nothing. §J's table is explicitly, in its own words, a *retrieval* failure and "something
  cheaper and more damning" than "nothing enforces this," not a restatement of it. The
  tree-mislabelling class is a *provenance* defect on an otherwise correctly computed number.
  **Two named candidates sit outside that stated corpus, checked by neither this count nor its
  predecessor, and are left there rather than folded in without the same rigor**: `F31`'s roster
  freshness indicator (cited above under instance 1, but not previously examined from this
  angle) and Ruling 34's finding that sampling would hide `NFR-RATE-1`/`2`'s violation below the
  metric's own resolution. Both are already tied, by their own source documents, to
  [`NT-0007`](../../docs/notes/0007-context-bound-measures-cap-not-discipline.md)'s "a boundary metric
  reads zero by construction" — plausible third and fourth instances of this section's narrow
  shape, or possibly a related-but-distinct family of their own; this review does not decide
  which, only declines to count them before checking either with the care the six above got.
  **The proposal stands on the two instances it has been checked against**, arrived at from a live
  choice between two implementations of the same authorisation repair — re-derive a `Caller`'s
  permissions from its account row, or pass the authenticated set as a parameter. They
  behave identically today (`backend/src/app/auth/service.py:230` populates identity permissions
  straight from the account row — verified directly), so the choice looked cosmetic. **It is not**:
  a re-derived implementation cannot be made to fail the test that would separate them (*"a
  `Caller` whose permissions differ from its account row must be enforced on the `Caller`'s"*) —
  it has no way to disagree with the row it derives from. Its defining flaw is not being wrong
  today; it is that nothing could ever tell you when it became wrong. **Why this belongs in a plan
  review rather than only in the ruling it came from**: it lifts `CLAUDE.md` §13's existing
  enforcement standard — "proven on deliberately broken input" — from *checking a check* to
  *choosing a design*, which is a standing decision-making criterion, not a one-off fix. It also
  retires a weaker remedy this evidence base tried first: a prose tripwire proposed for this exact
  hazard, withdrawn once the acceptance test above was shown to do the same work mechanically —
  the general lesson being that "document the danger" should first be tested against "can the
  danger be given a failing case instead." **Recommendation (3.8), alongside 3.7 and for the
  same reason not drafted here**: extend `CLAUDE.md` §13's deliberately-broken-input standard, in
  words, to design selection as well as check verification — again the maintainer's call, since it
  reaches the same section.

**An open question, distinct from every recommendation above — no recommendation number, because
this review is not proposing a remedy.** `delivery-process.md` §6 step 2 requires the test
written first, red before green, before step 3's implementation (`delivery-process.md:107-109`,
verified directly). Task 1.2 (`docs/plans/2026-08-29-w11-1-evaluator-core.md:692-740`) built the
`_Resolver`'s new branches, `Bundle` persistence of `graph`/`resolved_payloads`, and a wholly new
`rating_handlers.py` Job-handler module (mirroring `rate_table_handlers.py`'s shape) — the types
and the module under test did not exist yet, so a test written first would not have imported. The
compensation was writing the tests immediately after, in the same PR, against the implementation
as built.

Two readings are both defensible and this review takes neither side:
- **§6 gains an explicit carve-out** for a slice task that introduces a wholly new type or module:
  red-green governs behaviour added to something that already exists, and a task that scaffolds
  the thing itself writes its test immediately after, same PR — a documented exception, not a
  silent deviation each time it recurs.
- **§6's general rule was already wrong and this is what it should have said from the start**:
  not "test before implementation" but "test in the same PR, never a later one" — satisfied by
  Task 1.2 as executed, and it would cover the ordinary case too without naming an exception.

**This is a maintainer decision, not a planner's**: choosing between them is re-planning a
governance document this charter does not extend to, and recording it as resolved either way here
would erase the record of which reading was open when the question was raised. It is written down
as the open question it is, for the maintainer to settle.

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
- **A spec cross-reference points at the wrong requirement, verified at source.** `FR-RATE-26`
  (`03:137`) ends "unless the deployment explicitly uses date-based routing (`FR-RATE-31`)."
  `FR-RATE-31` (`03:153`) is the **Premium Ladder** — confirmed directly. Date-based routing is
  `FR-RATE-53` (`03:196`), also confirmed directly, and it has **zero implementation hits**
  anywhere in `backend/` or `packages/` (`git grep -rn "FR-RATE-53"` returns nothing) — a wrong
  citation pointing at an unrelated requirement, whose correct target is itself unbuilt. This is
  ordinary spec-change territory (a citation fix), not a workstream finding; flagged here because
  nothing has filed it yet.
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
- **A sharper, distinct failure sits behind the authority-boundary material above, raised by the
  decision-maker against its own error, and it pairs with 4.3 rather than restating it.** 4.3 is
  about whether a role decides something outside its lane; this is about whether a **correctly
  named** rule was actually checked against the **specific act**, which can fail entirely inside a
  role's own lane. In the decision-maker's own words: *"Identifying a rule's interest is necessary
  but not sufficient; you still have to check whether the act is inside it."* Its own instance is
  self-refuting: Ruling 33's entire point was that a proposed test measured the wrong interest,
  yet the same author, having correctly named resource contention as §8's interest, then applied
  it to a merge — an act that starts no local process. Three more instances the same night, one
  self-reported by the lead: a parameters-carrier field checked against its stated purpose but not
  against whether *this* field is a returned API surface; a `test_worker.py` "directly" qualifier
  read without the alternative its own sentence names; and the lead's own "holding the merge until
  the gate clears," announced, then superseded by a merge three minutes later without correcting
  the announcement — during which the decision-maker cited the withdrawn rule back approvingly, so
  the wrong claim outran its own correction.

  **The datum that decides the remedy, not just illustrates it.** Minutes after naming this exact
  pattern for the third time in an hour, the decision-maker raised a scope objection to a table it
  had not seen, inferring from the lead's phrasing that its own observation had already been
  tabled there — the same tell, committed while describing the tell: *"Awareness of the pattern
  did not defeat the pattern. I had named it three times in the preceding hour. It still fired on
  the next assertion I made."* That rules out the obvious fix: "check the scope before asserting"
  is a remembered discipline, and a remembered discipline is what just failed under stated
  awareness. What worked, that same night, worked mechanically every time and required nobody to
  remember anything — `audit-docs.py` catching an unescaped pipe, a positive control catching a
  `GoldenQuote` zero, re-reading `origin/main` catching a tree that had moved, the memory file's
  own duplicate guard catching a repeat write. **Recommendation (4.8):** this pattern needs a
  mechanical check local to each act, not a restated instruction to check the scope — and this
  review does not propose one check to cover all four instances above, because a merge's
  disturbance, a field's API-surface status, a qualifier's alternative and a role's authority
  boundary (4.3) share no single instrument. Where 4.3 is landable as a role-file amendment now,
  this recommendation is narrower: a future instance of this shape gets a mechanical, act-local
  check before anyone proposes a reminder — a reminder is the thing this section's own evidence
  just falsified.
- **`delivery-process.md:310-315`'s own list of durable homes for reasoning is wrong for its
  stated audience — a document-drift finding that names itself while being written.** The rule
  names "a task" as an acceptable durable home for reasoning a 50-word message cannot carry. But
  members cannot read the lead's task board, so for the reader a dispatch actually addresses, a
  task id is inert — through this workstream the board silently accumulated the fourteen owed
  register rows, a whole correction batch and every input this review draws on, none of it
  reachable by whoever was meant to act on it. **The self-demonstration**: this review's own
  evidence-base file opens by calling one of its findings "itself one of the findings below," and
  that finding was not below when first read — the same rule's failure, caught in the act of
  citing it. What actually surfaced the trapped material was one member refusing to reconstruct
  five items from board access it did not have and asking for a filesystem artifact instead — the
  refusal produced exactly the documents this review has been citing throughout.
  **Recommendation (4.5):** the rule's list of durable homes should say a member-facing dispatch
  cites a **filesystem path**, not a task id — paths resolve between agents that cannot share a
  board, which is the audience the rule is written for.

  **A second gap the rule does not state: citing a path presumes the path already exists.** A
  compliant dispatch requires the artifact to be written **before** the dispatch that cites it, not
  after. Task #82's F42 quantification message ran to roughly 140 words because its durable home
  was that task itself, which the auditor cannot open; faced with a choice between breaching the
  50-word rule and stopping to write a file first, the author carried the reasoning inline instead.
  The rule should state the sequencing it currently only implies: the artifact exists first, the
  dispatch cites it second, or the dispatch waits.
- **The reporter published two wrong lines to the team's external Slack channel in one hour, both
  inferences presented as fact** — "a peak-hours pause was in effect" when the pause is
  weekday-scoped and it was Sunday, and "W11 close audit in progress" before it had started.
  Neither line was in the file the reporter's own brief says to publish verbatim; both were
  derived from partial signals, and the role corrected itself once told (not a discipline
  problem — its later cycles are clean). **The connection to the row above, and why it belongs
  with question 4's authority-boundary finding rather than beside it**: in both cases the
  information a role needed was unreachable by that role, and one of the two closed the gap by
  inference while the other refused and asked — the same contrast question 4's `NFR-RATE-11`
  counter-example already makes for a governance question, here for an information-access one.
  **Recommendation (4.6), narrower than 4.3 and specific to reporting roles — already landed,
  verified at `origin/main`, not merely proposed.** `.claude/roles/reporter.md`'s "The Slack post:
  facts only, never inference" section now states a positive whitelist of three named, verbatim
  sources ("What goes in") — the core of what this recommendation asked for, and checkable by the
  reader of the post in a way a list of forbidden inferences never is, because the next inference
  is always a new one nobody enumerated. It also keeps named violation examples ("What does NOT go
  in," quoting these exact two lines) rather than dropping them — an addition this recommendation's
  original framing did not call for but does not conflict with; the whitelist, not the examples, is
  what makes a future post checkable. **Owner: discharged**, by the reporter itself rather than by
  this review; recorded here because this review's own reconciliation caught it only on a fresh
  read of the current tree (cross-referenced from 3.10 above).
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
- **A planning artifact asserted a decision existed when it did not, verified directly against
  the ruling it cites.** `docs/plans/2026-08-29-w11-3-batch-readiness-and-d6.md:72` states
  "`score_batch` stays plain `def` (Ruling 5, restated in the module docstring)" — but Ruling 5
  (`docs/plans/2026-08-29-w11-prework-rulings.md:431-474`) rules `score_one`'s real-time path
  specifically, and its own text says so: "`score_batch`… is **not** ruled here and its own `def`
  signature… is untouched." The citation names a ruling that explicitly disclaims the thing it is
  cited for. **This is a stronger defect than an omission**, and the same document's own title —
  "W11 Slice 3 — still held, on one unruled decision; and D6, the decision that releases it" —
  shows the cost directly: `D6` (batch resumability) was the actual open decision, and it sat
  behind this false "already ruled" reading until a later, dedicated ruling addressed it. An
  omission gets noticed when someone goes looking for the answer; a false positive does not,
  because the reader has no reason to look again. **Recommendation (4.7):** a readiness or
  planning sweep that books an item as "ruled" reads the cited ruling's own scope clause before
  citing it, not merely confirms the ruling exists — the same discipline this document has
  applied throughout to its own citations, here proposed as a standing step rather than a
  one-off habit.

  **The same false claim has an earlier, compressed sighting, and its coverage was partial.**
  `docs/plans/2026-08-29-w11-slices-3-4-rulings.md:8-9` — the readiness sweep itself — already
  wrote "Recovery items 1, 3 and 5 are already ruled (Rulings 10, 5 and 9 respectively)." Item 3 is
  `docs/plans/2026-08-29-w11-decision-points-recovery.md:106`'s "Batch chunk/resume" — confirmed
  directly — the same D6 the leaf plan's own title later names as still open. The claim was not
  made once: it originated compressed in the sweep, then was carried forward and quoted, expanded,
  into the leaf plan, uncaught at either step. Per the decision-maker's own count (attributed, not
  re-derived here): the sweep consulted only **3 of the 9** ruling-record documents that existed —
  consistent with a sweep that never reached Ruling 5's own disclaiming sentence.

  **It also undercuts a conclusion filed outside this review's own sources.** A session-local
  working note (`process-instrumentation.md` — not a repository artifact, not otherwise cited in
  this review) draws a cross-task conclusion that fix-loop count correlates with whether a task
  was pre-resolved rather than with its size, counting Task 1.2 as pre-resolved on the strength of
  exactly the reading just shown false. This review does not edit that note — it is neither a
  repository file nor within this charter's grant (`docs/plans/`, `docs/audit/plan-reviews.md`) —
  but the conclusion should carry this qualification, or be re-checked against which inputs were
  genuinely pre-resolved, before anyone reads it as settled.

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
  **A further sighting, in a different kind of document, named rather than added to that count**:
  `docs/audit/work/W9/README.md:27`'s own verdict table compresses `FR-RATE-22..27` into one
  "delivered" row on a bare marker count (question 2 above) — the identical bare-continuation
  mechanism, reaching a closure record's verdict table rather than a roadmap workstream row.
  `NFR-RATE-13/14`'s own omission-then-correction (`docs/roadmap.md:376`'s own note) is a further
  data point of a related but distinct shape — carried forward but never transcribed, rather than
  compressed out of view — and is likewise not folded into the four above; the two counts answer
  different questions and this document does not merge them into a new one. **What both widen is
  the fix's reach, not its urgency**: whatever check 4.2 becomes needs to cover verdict tables
  under `docs/audit/work/*/README.md` as well as `docs/roadmap.md`'s own rows.
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
  **A third candidate for the same rule set, raised under question 3 above**: a correction states
  what it supersedes, not only what it asserts — a corrected claim without a named prior leaves
  both readings live until a reader checks, which is how a correction tonight nearly reverted work
  already correctly done under the position it silently replaced. Recommended for the same
  adoption, same unnumbered treatment, same reason.

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
| 2. Omission | **Settled** as a list; **open as verdicts** — the gate-coverage cluster (decision point) and the two fresh W9 defects (`FR-RATE-22` pins-completeness, `FR-RATE-26`) all need one this review does not give | Slices 2–4 could surface more; none expected to remove what is listed here |
| 3. Skills and research | **Settled** | Process-control findings do not depend on the unbuilt slices |
| 4. Document drift | **Settled** for what is found; more likely once Slices 2–4's own spec sections get read as closely as Slice 1's was here | A fresh drift pass once Slices 2–4's plans exist on `main` |
| 5. Shape | **Mostly settled** — no-re-cut and W12-readiness stand on their own; the gate-coverage placement and `F31`'s charter fix are open by design (the lead's and a role-file owner's, respectively) | The lead's ruling on the decision point; Slices 2–4 landing does not itself change this question |

#### Proposals, consolidated — review 9 (draft)

| # | Proposal | Kind |
|---|---|---|
| 2.1 | `FR-RATE-63` gets a Ruling-30-style attribution ruling before the close | ruling needed |
| 3.1 | Adopt `python-test`'s already-documented per-session-database remedy (not a new lock file) for the shared-database hazard | adopt existing doc, no new mechanism |
| 3.2 | Either the §14 trigger, the 50-word rule and `close-workstream` §5a's condition-artifact check get a mechanical check, or the maintainer accepts and states that all three are enforced only by memory | process — maintainer to weigh |
| 3.3 | NFR acceptance criteria measured near their bound require repetition under varied load, not a one-run distribution alone | convention (skill or leaf-plan template) |
| 3.4 | A route-adding plan states the regenerated OpenAPI contract as a Files-block deliverable and names the second CI workflow it arms | convention (`writing-plans`) |
| 3.5 | For each mechanical-check proposal above, ask whether a one-command grep tied to a specific act of writing would catch more, more cheaply, than a general enforcement mechanism | methodology — question posed, not answered |
| 3.6 | A figure quoted in a durable artifact prints `git rev-parse HEAD` in the same invocation; a file quoted as evidence carries its `mtime` | mechanical — citation discipline |
| 3.9 | Whoever owns `dev-commands`/testing-strategy decides whether a query's own scope stated beside its result is worth a checklist item | methodology — question posed, not answered |
| 3.7 | `CLAUDE.md` §13 gains a fifth verdict (or a qualifier) for measured-and-failing evidence, and a rule for multi-limb requirements | `CLAUDE.md` §13 amendment — maintainer's |
| 3.8 | `CLAUDE.md` §13's "proven on deliberately broken input" standard extended from checking a check to choosing a design | `CLAUDE.md` §13 amendment — maintainer's |
| 3.10 | A frozen leaf plan cites a symbol as its primary locator and a line number only as a hint | convention (`writing-plans`) |
| 4.1 | A numbered NFR budget states its statistic, population, and (where storage is involved) encoding, in the same sentence as the number | spec-writing convention |
| 4.2 | Correct or drop `lead.md`'s "only role that relays" parenthetical | role-file correction |
| 4.3 | Name the authority-boundary trigger (question 4's shape) explicitly in every role file | role-file amendment |
| 4.4 | Correct W12's row against its own charter; declare `RegressionRun` in `03` §4; register `GOLDEN_QUOTE_MISMATCH` before or at W12's opening slice | docs + spec-change |
| 4.5 | `delivery-process.md`'s durable-homes rule names a filesystem path, not a task id, for a member-facing dispatch — and states the sequencing: artifact first, dispatch second | process-rule correction |
| 4.6 | The reporter's brief states the positive rule — publish only what a named artifact says, and name it | role-file amendment (reporter) — **already landed**, `.claude/roles/reporter.md`, owner: discharged |
| 4.7 | A readiness or planning sweep reads a cited ruling's own scope clause before booking an item as "ruled" | methodology — standing step, proposed |
| 4.8 | A future instance of "is this act inside the interest I just named?" gets a mechanical, act-local check, not a restated reminder | methodology — question posed, not answered |
| 5.1 | Assign review 8's proposal 4.2 an owner, now that it has fired a fourth time at a much larger scale, carrying Ruling 30's temporal-qualifier refinement | tool or convention — unowned since 2026-08-29 |
| 5.2 | Amend `.claude/skills/spec-change` so a new `FR-`/`NFR-` names its workstream row in the same commit that mints it, symmetric with the existing `OQ-` rule (Ruling 30's own proposal) | skill amendment |
| 5.3 | Apply `F31`'s charter correction to `watcher.md` — text already drafted in the withdrawal notice | role-file edit |
| 5.4 | Adopt Candidates A, B and a third (branch-freeze while under review; a count states its own granularity; a correction names what it supersedes) into `delivery-process.md` §15 | process rule — numbered at acceptance |
| DP-1 | Decide the gate-coverage cluster's placement (options a/b/c above) | **decision, the lead's — not a proposal** |

**Maintainer acceptance:** _pending._ This is a draft circulated to the lead ahead of the
maintainer, not yet presented for acceptance. Before it can be filed: Slices 2–4 land (or are far
enough along that question 1's tally is real rather than provisional), the §13 closure audit
completes, review 8's still-open binding condition (the `FR-RATE-34`/`FR-RATE-40` register rows)
is met, and the decision point above is ruled by the lead. Everything in questions 2 through 5 is
not expected to change on those events, but will be re-read against whatever tree is current
before filing, per this document's own rule that a claim names the tree it was checked at.

> **Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 10 and
> 11 under review 11's proposal 11.1.** The `_pending._` paragraph above is kept as the record of
> the pre-acceptance state; the preconditions it names were met before this line was dated
> (review 10's §5d records the first two, at `b749acb`).

#### Sources

- `docs/roadmap.md` §7 (workstream table, risk table, Phase 2 demo-able outcome) — read directly at
  `19eaabc`.
- `docs/audit/register.md`, in full — read directly at `19eaabc`.
- `docs/specs/03-rating-engine.md` §3.1, §3.4, §3.6, §3.7–§3.9, §5.1, §9 — read directly at
  `19eaabc`, including `FR-RATE-26`, `FR-RATE-31` and `FR-RATE-53`'s own text for the
  cross-reference check.
- `docs/process/delivery-process.md` §8, §15 — read directly at `19eaabc`.
- `docs/audit/work/W9/README.md:27` — read directly for the `FR-RATE-22..27` verdict row.
- `packages/model-schema/tests/test_rating_version.py:44-47` — read directly to confirm the
  three stacked markers on one test.
- `packages/pricing-core/src/pricing_core/rating/compile.py:425-440` — read directly to confirm
  `FR-RATE-22`'s presence-only check.
- `packages/model-schema/src/model_schema/rating.py:131` — read directly to confirm
  `effective_from: datetime | None = None`.
- `git grep -rn "FR-RATE-53"` against `backend/` and `packages/` — run this session, zero hits.
- `backend/src/app/errors.py` — read directly to confirm `GOLDEN_QUOTE_MISMATCH`'s absence from
  `RATING_ERROR_CODES`.
- `.claude/roles/watcher.md`, `.claude/roles/planner.md` — read directly.
- `.claude/skills/close-workstream/SKILL.md:340-368` (§5a) — read directly at `19eaabc`.
- `backend/tests/conftest_db.py:12,35,39,251-252` — read directly to confirm the fixture's scope,
  autouse status, and the `GIP_TEST_DATABASE_URL` override.
- `.claude/skills/python-test/SKILL.md:284-319` — read directly to confirm the mutual-truncation
  finding, its 2026-08-24 measurement, and both remedies (serialise via `pgrep`; per-session
  database).
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
- `docs/plans/2026-08-29-w11-3-batch-readiness-and-d6.md:72` — read directly to confirm the
  "`score_batch` stays plain `def` (Ruling 5…)" citation.
- `docs/plans/2026-08-29-w11-prework-rulings.md:431-474` — read directly to confirm Ruling 5 rules
  `score_one` and its own text disclaims `score_batch`.
- `backend/src/app/platform/rating_versions.py` at `c1a98b1` (`git show c1a98b1:...`) — read
  directly to confirm `submit_for_review` (def at `:153`) calls `approvals.submit(` at `:178`.
- `docs/plans/2026-08-29-w11-1-evaluator-core.md:692-740` — read directly to confirm Task 1.2's
  scope (new `_Resolver` branches, `Bundle` persistence, a new `rating_handlers.py` module).
- `docs/process/delivery-process.md:107-109` (§6, steps 2-3) — read directly to confirm the
  red-before-green ordering the open question above turns on.
- `docs/audit/register.md`'s `F44` row — read directly at `origin/main` (`6f77abb`, fetched this
  session; the row itself states it was filed against `e16c459`) to confirm its tree-anchored
  locator and cross-check it against the bare-line citation in 3.10.
- `backend/src/app/platform/rating_versions.py` at `origin/main` (`6f77abb`) — read directly
  (`git show origin/main:...`) to confirm `submit_for_review` now at `:214` and `approvals.submit(`
  at `:239`, a 61-line shift from the `:153`/`:178` both F44 and this review's own earlier citation
  recorded at `e16c459`/`c1a98b1`.
- `.claude/roles/reporter.md` at `origin/main` (`6f77abb`) — read directly, "The Slack post: facts
  only, never inference," to confirm Recommendation 4.6 is already landed.
- `docs/plans/2026-08-29-w11-slices-3-4-rulings.md:8-9` and
  `docs/plans/2026-08-29-w11-decision-points-recovery.md:106` — read directly to confirm the
  readiness sweep's own compressed mis-citation and that its "item 3" is batch chunk/resume (D6).
- `CLAUDE.md` §13 — read directly (this file's own governing text, present in every session) for
  "a reference carries its scope and its measurement… a `Verified` date carries the tree," cited in
  3.10.
- Session-local working notes that first surfaced several of the above, credited by name in prose
  and not cited as resolvable paths: `phase-review-inputs.md`, `w11-scope-derivation.md`,
  `close-audit-baseline.md`, `register-rows-owed.md`, `eta.md` (all
  `~/w11-handover-2026-08-29/`, 2026-08-30). None of this review's findings depends on a reader
  having access to them.

---

### Plan review 10 — at W11's second close, 2026-08-30

`CLAUDE.md` §14's tenth run, triggered by the close of W11's reopened scope. **Base tree:
`origin/main` at `b749acb`**, confirmed equal to `origin/main` when this was written; every
claim below was checked at that tree or names the commit it was checked at.

**Three §14 outputs now exist for one workstream, and a reader needs to know which does what.**
The closure record's §7 (`work/W11/README.md`) is the short review written against the
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
for the second close ran against this same tree and is filed as `work/W11/README.md` §10 (PR
#503). Its scope came from `scope-audit.py RATE --sections 3.7,3.8 --extra
FR-RATE-36,FR-RATE-37,FR-RATE-42,NFR-RATE-12`, run against the spec rather than against
recollection.

**The three requirements the first close recorded as never started are delivered and tested**
— FR-RATE-36 (`3dc8d6b`), FR-RATE-37 (`59407f2`, `eda70d6`), FR-RATE-42 (`25c5688`, `003f9d4`,
`87dd4b7`). That is the completion answer, and it is not this review's to re-verify.

**What the review adds to it is the shape of what remains, which the audit reports per
requirement and nobody has yet read as one picture:**

| Requirement | Verdict at `b749acb` | Where |
|---|---|---|
| NFR-RATE-1 (p99 < 50 ms) | measured and **failing** | first close, §4–§5; Ruling 41 discharged the architectural question without making the target reachable |
| NFR-RATE-12 (< 200 GB/year) | measured and **failing**, 516.07 GB/year, ~2.58x | §10.3, Task 4D |
| NFR-RATE-2 (trace overhead) | measured and **failing**, F35 | register |
| NFR-RATE-5 (batch throughput) | **passing** at 5.09x; its linearity clause **not measured**, F52, unowned | §10.4 |
| NFR-RATE-13 | **owed, not delivered** | first close |

**Every functional requirement W11 owns is delivered; three of its numbered non-functional
budgets are measured and failing, and a fourth is half-measured with no owner.** Neither close
states it that way, because each verdict is correct in its own row. Question 5 takes up what
follows from it.

---

**2. Omission — one class closed, one opened.**

**Closed: the unclaimed-NFR class did not recur in the reopen.** The closure record's §7
question 3 found five NFRs worked inside W11 while claimed by no roadmap row, and proposed that
rows name NFRs explicitly. The reopen honoured it without being told to — `../roadmap.md`'s W11
row names **NFR-RATE-12** in its reopen text, by id, as riding with FR-RATE-42. Recorded as a
result rather than passed over: a proposal from the previous review changed the next thing that
was written.

**Opened: `NFR-RATE-12` names a condition that cannot be resolved, and the failing measurement
turns on it.** Its text (`../specs/03-rating-engine.md` §9) reads *"1 % sampling of 50 M annual
quotes stays under 200 GB/year **with the sampled-trace schema**"*. The budget is therefore
conditional on a schema — and **F55**, filed the same day, finds that the schema actually
shipped stores each `TraceStep`'s full accumulated engine context rather than its own declared
inputs and outputs. So the 2.58x overage is not straightforwardly a budget failure: it is a
measurement of a schema the requirement's author may never have contemplated, against a number
chosen for one they did.

**Nothing in the requirement lets a reader tell which schema is meant** — no version, no
artifact path, no `04.5` reference. This is the failure `NT-0004` names: a reference that
resolves only for its writer. **This review does not decide which side is wrong** (§0 forbids
resolving it silently, and the choice is a real one), but it insists somebody does, because the
two branches lead to different work: trim the schema under F55 and re-measure, or amend
NFR-RATE-12 to state the encoding it actually budgets for. See proposal 2.1.

**No new instance of the `wf-01…05`-evidenced-by-nothing class** was looked for in this pass and
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
| W11 Slice 3 | none | `BATCH_ABORT_THRESHOLD_ABOVE_SETTING`, `BATCH_ABORTED` (`eda70d6`) |
| W11 Slice 4 | none | `TRACE_RETENTION_FLOOR` (`25c5688`), `TRACE_NOT_PENDING` (`003f9d4`) |

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
[`../plans/2026-08-30-w11-4-always-capture-correction.md`](../plans/2026-08-30-w11-4-always-capture-correction.md),
which holds Ruling 35's binding constraint on Task 4B. A dispatch that names the plan does not
thereby name the sibling. **Proposal 3.3**: a filed plan names its own correction records where
a reader enters it, or the dispatch that sends someone to a plan enumerates them.

**3d. A precedent carried between rulings must be split before it is reused.** Ruling 50 found
that Ruling 46's *conclusion* **inverts** for the register: 46 declined to red-gate a corpus
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

**4a. `FR-RATE-26` still cites `FR-RATE-31` where it means `FR-RATE-53`.** Verified at
`b749acb`, `../specs/03-rating-engine.md:137`: *"unless the deployment explicitly uses
date-based routing (FR-RATE-31)"*. FR-RATE-31 is the Premium Ladder; FR-RATE-53 is date-based
routing. The closure record's §7 recorded this as outstanding and owed at the next docs pass;
**it is still outstanding two closes later**. Two characters, and it has now survived being
named once. **Proposal 4.1**: fix it in the next docs commit and give it an owner rather than a
queue.

**4b. `NFR-RATE-12`'s unresolvable schema condition** — question 2 above; it is a drift finding
as much as an omission, in the direction §14 cares about most (the spec describing something the
code does not implement, rather than the reverse).

**4c. The §5.1 endpoint axis is clean for W11's scope; the §5.2 signature axis is unrun.** The
two are separate questions and this review answers only one of them.

`uv run python scripts/scope-audit.py RATE --endpoints`, run for this review on this branch
(`7fa1326`, a docs-only commit on `b749acb`) and independently at `7b490b3` with identical
figures: **22 declared, 14 published, 8 not published.** All eight belong to later
workstreams — `GET`/`POST /api/v1/dislocation-runs` and `/{}` (W13, FR-RATE-46–49),
`POST /api/v1/environments/{}/deployments` and `/rollback` plus
`PUT /api/v1/environments/{}/shadow` (W14, FR-RATE-50–55),
`POST /api/v1/rate-tables/{}/versions`,
`POST /api/v1/rating-versions/{}/regression-runs` (W12, FR-RATE-43–45), and
`POST /api/v1/score/compare`. **None is a W11 gap**, and the published count moved 13 → 14 with
Task 4C's `GET /api/v1/traces`, which is the direction this workstream should have moved it.

**One relay check that changed nothing and is recorded because it could have.** An
intermediate enumeration of this same result listed seven paths under a count of eight; the
omitted one was `PUT /api/v1/environments/{}/shadow`. Re-run here rather than transcribed, and
its owner checked (`FR-RATE-54`, named by W14's row), which is what confirms the conclusion
rather than assuming the missing item was harmless.

**The signature axis — `03` §5.2 shapes with no implementation, and implemented shapes `03`
does not declare — remains unrun.** It was delegated and the delegation did not return. Stated
as an open gap with a named owner rather than left silent, because a silent question cannot be
told apart from one nobody asked. **Proposal 4.2**: run the §5.2 direction before W12 opens,
since W12 builds against those shapes.

---

**5. Shape — the cut held; the requirement set is where the problem is.**

**5a. The workstream cut: the reopen tested the closure record's proposal and supports it.** §7
of the first close proposed that batch scoring and trace sampling should each have been their
own workstream. The reopen is the experiment: eight tasks ran as two chains (3A→3D, 4A→4D) that
never interacted, delivered on the same day, and were audited separately. **Nothing about
running them under one id helped, and the single id is what produced two closes of one
workstream and three §14 outputs for it.** Recommendation stands, and this review adds the
evidence the first one could only predict. It is a recommendation about *future* cuts; W11 is
not re-cut retrospectively.

**5b. The requirement set is the real finding: W11 delivers its functional surface with three
numbered budgets failing.** Question 1's table is the evidence. This is the skill's named smell
— *a phase exit criterion the phase cannot meet* — and the review's job is to make somebody
choose rather than to choose. The three are not one problem:

- **NFR-RATE-1** — failing, architectural question ruled (Ruling 41) without the target becoming
  reachable. Carried to W14.
- **NFR-RATE-12** — failing against a schema the requirement may not have meant (question 2).
  **Its remedy has a named lever, F55.**
- **NFR-RATE-2** — failing, F35. **Its blocking precondition, Ruling 35's off-path capture,
  landed today in Task 4B**, so the remedy is unblocked. The measured clause itself does not
  move, because F35 measured the explicit `ctx.options.trace=True` path that 4B leaves
  untouched.

**5c. F35 and F55 converge on one lever, and neither row says so.** Both turn on what a
`TraceStep` carries and what producing one costs; F55 is NFR-RATE-12's largest remediation lever
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
by Ruling 29 to be decided at a §14 review, was carried past review 9, and the NT-0014 adoption
record explicitly left it. **It is a decision, the lead's, not a proposal** — but finding 3a
above changes its terms, because F29 is now known to have been masked by a skill and a
tautological test rather than merely unaddressed.

---

#### Proposals, consolidated — review 10

| # | Proposal | Kind |
|---|---|---|
| 2.1 | Decide `NFR-RATE-12`'s branch: trim the trace schema under F55 and re-measure, or amend the requirement to state the encoding it budgets for. It may not stay conditional on an unresolvable "the sampled-trace schema" | spec change or work — maintainer to place |
| 3.1 | Correct `.claude/skills/fastapi-service`'s claim that a conformance test compares each registry to its spec list, and either fix or retire `test_spec_error_codes_are_all_constructible`, whose body cannot fail for the reason its docstring gives | skill + test correction — `CLAUDE.md` §12 already binds it to this session |
| 3.2 | A plan's id block speaks only to ids it can reserve; an error-code expectation goes in the register-rows section with an owner, or is not stated | convention (`writing-plans`) |
| 3.3 | A filed plan names its own correction records where a reader enters it; a dispatch to a plan enumerates them | convention (`writing-plans` / dispatch) |
| 3.4 | A ruling citing an earlier one states whether it carries its mechanism, its conclusion or its principle, and re-checks the earlier premise against the new corpus | convention — decision-maker's records |
| 3.5 | A delegated evidence request names, at dispatch, the direct command answering the same question; the dispatcher runs it rather than waiting once the delegation is outstanding and the work is cheap | convention — dispatch discipline |
| 4.1 | Fix `FR-RATE-26`'s `FR-RATE-31` → `FR-RATE-53` citation, with an owner rather than a queue | spec change (two characters) |
| 4.2 | Run the `03` §5.2 signature direction before W12 opens, since W12 builds against those shapes | evidence — owner needed |
| 5.1 | Record on both `F35` and `F55` that they share one remediation lever, and scope trace-payload trimming as one piece of work | register amendment — the auditor's |
| 5.2 | Put plan review 9 to the maintainer alongside this one, as a separate acceptance | process |
| DP-1 | The gate-coverage cluster (`F27(c)`, `F29`, `F33`) is still undecided, now in changed terms — see 3a | **decision, the lead's — not a proposal** |

#### What this review did not do

- **It did not re-derive question 1**, by design; the §13 audit at the same tree is its source.
- **It answered the `03` §5.1 endpoint axis and not the §5.2 signature axis** (question 4c).
  The endpoint result is clean for W11's scope with its command and tree named; the signature
  direction is unrun and carried as proposal 4.2 rather than reported as absent drift.
- **It did not re-argue review 9's proposals**, which stand as filed.
- **It did not edit the Slice 4 plan again.** All four of its tasks have merged, so it is a
  finished record; its correction section was written while three tasks were unrun and was
  correct at its date. `TRACE_NOT_PENDING` is carried here instead.

**Maintainer acceptance:** _pending._ Nothing above binds until this line carries a date. The
`NT-0014 … NT-0017` reconciliation triggered at this same close is a **separate document with
its own acceptance line** ([`../plans/2026-08-30-nt-0014-0017-reconciliation.md`](../plans/2026-08-30-nt-0014-0017-reconciliation.md)) —
accepting this review accepts none of its four dispositions.

> **Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 9 and
> 11 under review 11's proposal 11.1.** The `_pending._` sentence above is kept as the record;
> the reconciliation it names is accepted separately, this same date, by its own line.

#### Sources

- `docs/audit/work/W11/README.md` §10, at `origin/docs/audit-w11-second-close` (PR #503) — the
  §13 closure audit reused for question 1.
- `docs/roadmap.md` W11 row and §7, read in full at `b749acb`.
- `docs/specs/03-rating-engine.md:137` (FR-RATE-26), `:175` (FR-RATE-42), `:906` (NFR-RATE-12),
  and the owned error-code block at `:628`/`:634` — read directly at `b749acb`.
- `backend/src/app/errors.py:332,339,348,378` and `backend/tests/test_errors.py:100-111` — read
  directly at `b749acb`.
- `git grep -ln "_KNOWN_CODES\|RATING_ERROR_CODES" -- backend/tests` — run at `b749acb`, zero
  hits; and `git grep` for the same over `packages`, `scripts`.
- `git log --oneline 25c5688..b749acb -- backend/src/app/errors.py` — run at `b749acb`, one
  commit (`003f9d4`).
- `uv run python scripts/scope-audit.py RATE --endpoints` — run for question 4c on this branch
  (`7fa1326`), and independently at `7b490b3`, with identical figures.
- `docs/specs/03-rating-engine.md:197,602` (FR-RATE-54 and the shadow endpoint row) and
  `docs/roadmap.md`'s W14 row (`FR-RATE-50..55`) — read directly, to place the eighth
  unpublished endpoint.
- `docs/audit/register.md` rows F29, F35, F52, F55 — read directly at `b749acb`.
- `docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md` Ruling 50 §1–§2 — read directly.
- `.claude/skills/fastapi-service/SKILL.md:328-338`, `.claude/skills/phase-review/SKILL.md` —
  read directly.

---

### Plan review 11 — completing the review sequence at W11's close, before W12 opens, 2026-08-31

**Base tree: `origin/main` at `567eea2`**, clean, confirmed by `git status --short` returning
nothing before this review was drafted. Every claim below was checked at that tree or names
the commit it was checked at.

**A premise this review was dispatched under was wrong, and the correction is recorded here
rather than silently acted on** (`.claude/skills/phase-review` §"When a review gets its own
premise wrong"). The dispatch stated "nobody has run a §14 review for W11's close." False:
[Plan review 9](#plan-review-9--at-w11s-close-2026-08-30) and
[Plan review 10](#plan-review-10--at-w11s-second-close-2026-08-30) both exist, both dated
2026-08-30, both drafted with real evidence against real trees. What is true, verified
directly against this document: **both still carry `Maintainer acceptance: pending` — neither
has ever been dated.** The corrected statement, endorsed by the lead in the same exchange that
authorised this filing: *the review sequence for W11's close was run but never closed out.*

**What this review is and is not.** It does not re-derive the five questions from a blank
sweep — review 9 and review 10 already did that, at `19eaabc` and `b749acb` respectively, and
re-deriving now would look like work and confirm nothing (`phase-review`'s own rule). Its job
is the agenda that decayed onto "the §14 review at W11's close" since those two were drafted:
eleven `docs/audit/register.md` rows that now name this review by that phrase, two residual
items inside a row (F28) that reviews 9 and 10 did not pick up, and the two items named
outside the register when this review was commissioned — the unnumbered rule candidates, and
NT-0015's unfiled impact-matrix row. **Per the lead's ruling on how this review may act:
every disposition below is a recommendation with a rationale, never a filed owner.** Assigning
an owner to a register row is re-planning, and re-planning was carved out of this review's
authority explicitly, the same way it is carved out of every workstream close
(`delivery-process.md` §3). Where the register text already proposes an owner, this review
says so and cites it; it does not adopt the proposal by repeating it as a decision.

---

#### Register rows decayed to this review

`python3 scripts/register-owed.py review`, run against the clean tree above, returns **eleven
owed rows** naming this review (one further row, F28, is excluded by the script as opening
with a resolution marker — its own text says "verify none carries a residual item," and §"F28
residuals" below is that verification, because it does carry two). Grouped by shape, not by id
order, because three of the eleven are one decision and listing them separately would suggest
three separate choices exist where Ruling 29 already found one mechanism.

**Decision point A (not new — reaffirmed, and explicitly excluded from W12).** `FR-RATE-25`
(`F-W9-3`) clauses (4)–(6), `F27(c)`, `F29` and `F33` are, per review 9's own framing
(`docs/audit/plan-reviews.md:1994-1997`), **one mechanism** — comparing a spec-declared shape
against its implementation on four axes (contract drift, error-code registration, transitive
maturity resolution, and `mypy` file coverage) — not four independent findings. Review 10
recorded it as **DP-1**, undecided, and the NT-0014/0017 reconciliation
(`docs/plans/2026-08-30-nt-0014-0017-reconciliation.md:64-69`) confirms it is still open:
*"this reconciliation records that it leaves them; plan review 10 carries them as an open
decision point."* **The lead has since ruled its relationship to W12, not its placement**:
the cluster stays **out** of W12's spec-change slice, because W12's job is to unblock W12's
own start and a cross-cutting, unbounded mechanism should not make that start conditional on
a decision nobody has made. This review carries that ruling forward and restates review 10's
three placement options for whoever decides the cluster's actual home — a dedicated slice
(inside a still-to-open Phase 2 workstream), a maintainer task outside the workstream ladder,
or a split by cost (`F33`'s `mypy` widening first, the rest bundled later) — without picking
one. **The one instance inside this cluster's shape that does sit in W12's own scope**,
`GOLDEN_QUOTE_MISMATCH` (`F29`'s pattern, one workstream early), **is scoped into W12's
spec-change slice directly** — a slice-scoping call the lead made explicitly, on the ground
that the instance is W12's even though the class is not. See the W12 map plan.

**F26 — still open, verified rather than assumed stale.** Register text: *"owner decided: W11
(Ruling 29)... to land before the charter amendments R6 is holding for the §14 review."* W11
closed (twice) without landing it. Verified directly: `.github/workflows/docs.yml:16,18`'s
`paths:` filter is `['docs/**', 'docs/notes/**', 'scripts/audit-docs.py', 'CLAUDE.md',
'.github/workflows/docs.yml']` — no `.claude/roles/**` or `.claude/skills/**`. The gap Ruling
29 named is exactly as open as it was at W11's close. **Recommendation**: name a fresh owner
now that W11 cannot discharge it — the fix is small and self-contained (a path-filter addition
plus a content check, per task #21's spawn-input constraints already read as a ready-made
spec) and could ride with whichever Work row eventually carries NT-0014/0015's own process
tooling, but this review does not pick that Work; it only confirms W11 is no longer a live
candidate.

**F31 — reaffirm review 10's own proposal 5.3, still pending.** Register text (amended
2026-08-31): *"review 10 ... drafted exactly this row's 'charter drops the claim' branch and
recommended applying it, but stated explicitly it is 'not decided here.'"* Verified directly:
`.claude/roles/watcher.md:11-24` still describes the roster-derivation clause. Nothing to add
— this review carries proposal 5.3 forward into the acceptance batch below rather than
re-arguing it.

**F48 — the register asks this review to confirm or overturn a provisional W14 placement;
this review confirms it, as a recommendation.** `NFR-RATE-11`'s per-client rate limit cannot
be an in-process limiter (a per-replica memory counter is not a limit on a multi-replica
deployment), so it needs shared state across replicas or a gateway in front of them. W14 is
where the `Environment`/`Deployment` domain entities and their shared-state infrastructure
land (`docs/roadmap.md:379`); building a cross-replica limiter before that infrastructure
exists would mean building a piece of W14 under another workstream's name, the same objection
review 8 raised against pulling `FR-RATE-34`/`FR-RATE-40`'s dependencies forward. **This
review's reading**: keep W14. It is a confirmation, not new evidence; the maintainer may still
prefer a platform-level workstream instead, since `NFR-RATE-11`'s clause is not itself
`Environment`/`Deployment`-shaped, only dependent on infrastructure that lives there.

**F58 and F61 — one register, two related loose ends, both explicitly asking this review for
an owner and neither getting one from this review.** F58: no process writes
`~/gi-pricing-plan.local/handover/runtime-state.json` on a cycle — verified directly, the file
does not exist and none of the three live watcher-class processes (`balance_watch.py`,
`reporter-cycle.sh`, `watch-external-prs.sh`) reference `write_runtime_state.py`. F61: the C2
retry-cap hook (`scripts/hooks/retry_cap_hook.py`) is disableable per-session
(`disableAllHooks`, or a gitignored `settings.local.json` override) with no CI-equivalent
backstop, unlike its dissolved sibling C3. Both are "needs the lead to name an owner" rows by
their own text. **Recommendation, not a pick**: F58's fix is wiring one of the three live
watcher processes (or a fourth) to call `write_runtime_state.py cycle` on a schedule — a small
task, no research needed; F61's two branches are build the reconciliation Ruling 47(b) assigns
to "a future watcher cycle," or the lead/maintainer accepts the residual gap as proportionate
in writing. Both fit naturally as one small follow-up to NT-0014 adoption slice G rather than
a new workstream, but this review does not schedule that follow-up — it only says the two
belong together if someone does.

**F62 — routed to the decision-maker, not decided here.** `03` §4.4's `timing_ms` example
names four keys; `score_one` emits two. This is a spec-vs-code disagreement, and
`CLAUDE.md` §0 and `delivery-process.md` §3 both give that call to the decision-maker, not to
a plan review. **Recommendation**: the decision-maker rules between extending
`score_one`/`build_scoring_result` to emit the full four-key breakdown, or correcting `03:419`'s
example to the two keys the engine actually emits. This review requests the ruling; it does
not attempt it.

**F63 — two readings, both already on the register row, the maintainer's to choose between.**
`register-owed.py W11` at `f99b55d` found ten register rows attributed to W11 that the closure
record's own findings sections never name, all filed before either close. The row states two
readings without choosing: **(a)** F41's own failure recurring at roughly 4x scale — a
hand-compiled closure-record sweep losing genuinely open, W11-attributed rows the same way F41
itself was lost; or **(b)** legitimate, undisclosed scoping — a narrower reading of "open
finding" nobody wrote down as a rule. **This review's own reading favours (a)**: F41 was
exactly this shape at one row, and the closure record's own §10.6 text ("None of these are in
the reopen's requirement scope... it revisits exactly the 4 items §6 already named") describes
a sweep scoped to what the closer already knew, which is the same mechanism F41 named, not a
disclosed rule. **The choice is the maintainer's alone**: reopening a Work close is
`CLAUDE.md` §13's exclusive maintainer act, and this review does not attempt it — it states a
reading and stops.

**F28 residuals — two of three carried items were never picked up, and this is new.** F28's
own row lists three items "carried to the §14 review as proposals": P7, P12, and P1b's
working-note half. Review 9 folded in **P7** (Candidate A, the writer's-half branch-freeze
rule) via its proposal 5.4. Verified directly (`grep` across review 9 and review 10's own
text, lines 1233–2472): **neither review mentions P12 or P1b.**
- **P12** (`docs/audit/work/nt-0010-0011-adoption/pilot-findings.md:643`): *"a correction is
  checked by a differently-shaped probe than the one that found the original, never by
  re-reading the passage just edited."* Distinct from review 9's own third candidate ("a
  correction states what it supersedes") — same family of correction-discipline rule, not a
  duplicate. **Recommendation**: fold P12 into the same `delivery-process.md` §15 candidate
  batch as Candidates A, B and the third, numbered together at acceptance rather than left to
  decay a second time.
- **P1b's working-note half** (`pilot-findings.md:632`): *"Still carried: a working note of
  its own, since the reasoning failure generalises past this repository."* The failure is
  diagnosing from a log you have been writing to yourself without subtracting your own
  attempts first — `watcher.md`'s operational fix landed, but the generalisable working note
  never did. Checked `docs/notes/` in full (eighteen notes, `0001`–`0018`): none covers
  this. **Recommendation**: write the note (a `docs/notes/0019-…` candidate); this review
  does not write it, since a role writes what its own charter names
  (`.claude/roles/planner.md`) and an NT-numbered working note is nobody's charter item by
  default — flagging it is as far as this review's grant reaches.

---

#### The two items named at commission

**(a) The unnumbered rule candidates.** Status, verified directly: Candidate A (branch-freeze
while under review) and the third candidate raised under review 9's question 3 (a correction
names what it supersedes) are **both already folded into review 9's proposal 5.4**
(`docs/audit/plan-reviews.md:1994-2006`), with numbering deliberately deferred to maintainer
acceptance — correct, per the "Pending proposals" section's own rule that "numbering happens
at acceptance." Candidate B (a count states its own granularity) is in the same proposal.
**P12, surfaced above, was not** — it belongs in the same batch and was missed until this
review re-checked F28's own row against what actually got folded in, rather than trusting that
"carried to the §14 review" had been discharged because a §14 review had since run.
**Recommendation**: the maintainer's acceptance of review 9 (see the bundling recommendation
below) numbers all four candidates — A, B, the third, and P12 — into `delivery-process.md` §15
in one pass, rather than three followed by a stray fourth later.

**(b) NT-0015's impact-matrix row 15.** Verified directly: `docs/notes/
0015-the-register-is-a-ledger-evidence-is-a-file.md:114` names row 15 as *"Adoption plan
`docs/plans/<date>-nt-0015-adoption.md`."* No such file exists in `docs/plans/` (checked by
listing), and `docs/roadmap.md:424` already records why: *"writing a plan today for work
already landed would record a sequencing that did not happen... the deviation is the next
§14 review's to dispose of."* This is that review. **Recommendation, endorsed by the lead
in the dispatch that commissioned this filing**: accept the deviation as deliberate and
dated — by this paragraph, 2026-08-31 — rather than file a plan that would misstate when the
work was sequenced, and close NT-0015's impact-matrix row 15 on that basis. This review
proposes the acceptance; it does not close the row itself, consistent with the same rule that
keeps every other disposition above a recommendation.

---

#### The five questions, in order

**1. Completion — no change, reused from review 10.** `git diff --stat b749acb..567eea2`
touches `.claude/roles/`, `.claude/skills/`, `docs/audit/`, `docs/plans/`,
`docs/process/`, `scripts/`, `tests/` and one line of `docs/roadmap.md` — no file under
`backend/`, `packages/` or `frontend/` changed. Nothing in the RATE requirement surface moved
since review 10's tally; its answer stands without re-derivation.

**2. Omission — one, and it is item (b) above.** NT-0015's row 15 is exactly the shape this
question asks for: a plan the impact matrix named that nobody would otherwise have noticed was
missing, because the work it would have described already landed. Disposed above. No further
omission found in this pass.

**3. Skills and research — the candidate-numbering gap (item (a) and P12) is this question's
finding**, disposed above. `F58`/`F61` (the watcher/NT-0014-adoption loose ends) are process
gaps of the same general kind and are cross-referenced there rather than repeated here.

**4. Document drift.**
- **`FR-RATE-26` still cites `FR-RATE-31` where it means `FR-RATE-53`** — verified directly,
  `docs/specs/03-rating-engine.md:137` unchanged since review 10's proposal 4.1. Two
  characters, still unfixed, still without an owner beyond "the next docs commit." Carried
  forward rather than re-argued.
- **W12's row disagrees with `FR-RATE-43..45` in both directions — reaffirmed, and this is
  what the maintainer's spec-change-slice direction for W12 already answers.** Verified
  directly against `docs/roadmap.md:377` and `docs/specs/03-rating-engine.md:176-178,596-597,
  611`: the charter's "regression runs" names an execution route
  (`POST /api/v1/rating-versions/{id}/regression-runs`) that no requirement's own text cites —
  `RegressionRun` is defined only in `docs/contracts/schemas/regression-suite.schema.json`,
  not in `03` §4 — while `FR-RATE-45` (Quote Sandbox) sits inside the id range but outside the
  three-item charter and is separately claimed by W15's row. `GOLDEN_QUOTE_MISMATCH` (`03:611`)
  is confirmed absent from `backend/src/app/errors.py`'s `RATING_ERROR_CODES`. This is review
  9's own proposal 4.4, unactioned until now; the W12 map plan filed alongside this review
  closes the two spec-level gaps and corrects the row's text, and raises `FR-RATE-45`'s
  ownership as a named decision point (DP1) in that plan rather than resolving it here — the
  planner's charter reserves decision points with options and recommendations to the plan, not
  the review.
- **`F62`** — disposed above (routed to the decision-maker).

**5. Shape.**
- **No re-cut.** Nothing in this pass disturbs review 8's or review 9's no-re-cut findings for
  the W11–W14 boundary.
- **DP-1's placement stays a decision, and stays outside W12** — the lead's ruling, recorded
  above, carried forward rather than reopened.
- **W12 readiness**: the map plan filed alongside this review closes the row-text and
  spec-declaration gaps before any build slice opens, per `CLAUDE.md` §0's table treating "a
  capability not yet specified" as spec-change-first work.

---

#### Recommendation: bundle reviews 9, 10 and 11 into one maintainer acceptance pass

Reviews 9 and 10 have sat with `Maintainer acceptance: pending` since 2026-08-30. The eleven
register rows above cannot be given a final disposition — even the recommended ones — while
the reviews that first surfaced most of them remain unaccepted, and three of the four
unnumbered candidates cannot be numbered without an acceptance line to number them at. **This
review recommends putting all three to the maintainer together, as three acceptances on one
occasion rather than a fourth wait.** The lead has stated this is accepted as a recommendation
and will be carried.

#### Proposals, consolidated — review 11

| # | Proposal | Kind |
|---|---|---|
| 11.1 | Bundle reviews 9, 10 and 11 for one maintainer acceptance pass | process |
| 11.2 | Name a fresh owner for F26 (the CI path-filter gap), now that W11 cannot discharge it | owner decision — maintainer/lead |
| 11.3 | Fold P12 into the same `delivery-process.md` §15 candidate batch as Candidates A, B and the third; number all four at acceptance | convention — numbered at acceptance |
| 11.4 | Write the working note P1b's carried half still owes (diagnosing from a self-written log without subtracting your own attempts, generalised past this repository) | working note — unowned |
| 11.5 | Accept NT-0015 impact-matrix row 15 as a deliberate, dated deviation (this section, 2026-08-31) rather than file a backdated plan; close the row on that basis | process acceptance — lead/maintainer |
| 11.6 | Confirm F48's provisional W14 placement (this review's reading), or overturn it for a platform-level workstream instead | confirm/overturn — maintainer |
| 11.7 | Give F58 and F61 one combined owner as a small NT-0014-adoption follow-up (wire a live cycle writer; decide C2's reconciliation-or-accept branch) | owner decision — lead |
| 11.8 | Rule F62 (spec-vs-code disagreement on `timing_ms`'s keys) | decision — decision-maker |
| 11.9 | Choose F63's reading (a) or (b); this review's own reading favours (a) | decision — maintainer alone (`CLAUDE.md` §13) |
| DP-1 | (Not new.) The gate-coverage cluster's placement — dedicated slice, maintainer task, or split by cost — stays undecided and stays outside W12, per the lead's ruling | decision — lead/maintainer |

#### What this review did not do

- **It did not re-derive questions 1–5 from scratch.** Review 10's completion tally is reused;
  no RATE-surface code changed since `b749acb`.
- **It did not assign an owner to any register row.** Every disposition above is a
  recommendation, per the lead's explicit carve-out for this filing.
- **It did not fold the gate-coverage cluster (DP-1) into W12.** The lead ruled that
  separately; this review records the ruling rather than re-arguing it.
- **It did not decide `FR-RATE-45`'s ownership.** That is named as a decision point in the W12
  map plan, not resolved here.
- **It did not close NT-0015's impact-matrix row 15 itself**, only recommends the acceptance
  that would.

**Maintainer acceptance:** _pending._ Nothing above binds until this line carries a date, and
per proposal 11.1 this review recommends it be dated alongside reviews 9 and 10 rather than
separately.

> **Maintainer acceptance: accepted as proposed, 2026-09-01 — dated together with reviews 9 and
> 10 under review 11's proposal 11.1.** The `_pending._` sentence above is kept as the record;
> the premise-correction sentence in the section above it ("neither has ever been dated") is
> likewise superseded by these datings and kept as the record of the state it was written
> against. **Applied with the dating:** the eleven register rows behind this review now pass to
> their named owners (this review's own table above lists which); the four unnumbered rule
> candidates — Candidate A, Candidate B, review 9's third, and P12 — are numbered in the same
> pass into `docs/process/delivery-process.md` §15, applied by the lead, not written here.

#### Sources

- `docs/audit/plan-reviews.md` — reviews 8, 9 and 10, read directly in full (lines 1–2472) for
  the premise correction, the DP-1 history, and the candidate-folding check.
- `python3 scripts/register-owed.py review`, run against `567eea2` — eleven owed rows, one
  excluded (F28).
- `docs/audit/register.md` rows FR-RATE-25/F-W9-3, F26, F27, F29, F31, F33, F48, F58, F61, F62,
  F63, F28 — read directly at `567eea2`.
- `docs/plans/2026-08-30-nt-0014-0017-reconciliation.md:40-69` — read directly, for DP-1's
  status and the gate-coverage cluster's disposition.
- `.github/workflows/docs.yml:16,18` — read directly, to confirm F26's path filter is
  unchanged.
- `.claude/roles/watcher.md:11-24` — read directly, to confirm F31's clause is unchanged.
- `docs/audit/work/nt-0010-0011-adoption/pilot-findings.md:600-650` — read directly, for F28's
  P7/P12/P1b dispositions and owners.
- `docs/notes/` (`0001`–`0018`), listed in full — to confirm no note covers P1b's carried
  half.
- `docs/notes/0015-the-register-is-a-ledger-evidence-is-a-file.md:114` and
  `docs/roadmap.md:424` — read directly, for NT-0015's row 15 and its own stated disposition
  owner.
- `docs/specs/03-rating-engine.md:137,176-178,596-597,611` — read directly.
- `docs/contracts/schemas/regression-suite.schema.json` — read directly, confirming
  `RegressionRun`'s shape and its absence from `03` §4's own text.
- `backend/src/app/errors.py` — read directly (`grep -n GOLDEN_QUOTE_MISMATCH`, zero hits),
  confirming the code is unregistered.
- `git diff --stat b749acb..567eea2` — run this session, to confirm no RATE-surface code
  changed since review 10.
- `git status --short` — run this session, confirming a clean tree at `567eea2` before
  drafting.

---

#### Correction appended 2026-09-01 — review 11's F31 paragraph misattributes proposal 5.3

**The paragraph above — "F31 — reaffirm review 10's own proposal 5.3" (this file, line 2549
at `43fd277`) — names the wrong review.** The only proposal numbered 5.3 in this file sits
inside plan review 9's section: its prose at `:1979-1981` ("Recommendation (5.3): apply it —
a role-file edit…") and its consolidated table row at `:2066` ("5.3 — Apply F31's charter
correction to `watcher.md` — text already drafted in the withdrawal notice"). Plan review 10's
section (`:2151-2476`) carries no 5.3 in prose or table — `sed -n '2151,2476p'` piped to
`grep '5\.3'` returns nothing. **What the paragraph *meant* is unchanged**: review 11 carries
proposal 5.3 forward into the acceptance batch; the review that first proposed it is review 9.

The same misattribution is shared by the register text the paragraph quotes —
`docs/audit/register.md`'s F31 row cites `plan-reviews.md:1979-1981` but labels it "review
10" — and is flagged here for the register's owner rather than edited: the register is the
auditor's file, not the planner's (`.claude/roles/planner.md`). The landing package's §1.2
(`docs/plans/2026-09-01-nt-0016-landing-package.md`) made the same error when written and is
corrected on its own branch, PR #549.
