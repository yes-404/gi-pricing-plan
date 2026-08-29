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

**Maintainer acceptance:** _pending — no recommendation above binds until this line carries a
date and a decision._

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
> **Maintainer acceptance:** _pending on FR-RATE-63's ownership; F-W9-2 needs no acceptance
> line to bind, since it was never this review's proposal to make._

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
> **Maintainer acceptance:** _pending._

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

**Maintainer acceptance:** _pending — no recommendation above binds until this line carries
a date and a decision._

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
> **Maintainer acceptance:** _pending._

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
> **Maintainer acceptance:** _pending on the mechanical-fix proposal; the two individual
> corrections are already live and need no acceptance line to bind._
>
> **A second mechanism, distinct from the range omission and with a different fix.** The
> same period produced corrections to a *measured figure* — NFR-RATE-14 (#314) and
> OQ-RATE-2 across six locations (#317). The executor, who swept them, named why they were
> never caught together: **a fact copied into free prose is corrected only where the
> tooling structurally links the copy back to its source.** This repository has exactly one
> such link — the OQ mirror pair, enforced by `audit-docs` check 15 — and it worked: the
> two OQ-RATE-2 copies could not diverge. Everywhere the same figure was merely *quoted in
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
> **Maintainer acceptance:** _pending._

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

> **Maintainer acceptance:** _pending._

#### Proposals, consolidated — review 8

| # | Proposal | Kind |
|---|---|---|
| 3.1 | A short ZEN-evaluate-side concurrency spike, run at W11 evaluator-slice start | research |
| 4.1 | W11's roadmap row corrected for FR-RATE-64 | docs — **landed, PR #314** |
| 4.2 | Workstream rows cite the spec section as the row of record, range as gloss only | tool or convention |
| 4.3 | NFR-RATE-14 gains a dated amendment reconciling the 1.09 ms / 1.626 ms figures | spec — **landed, PR #314** |
| 4.4 | A distinct mechanism (a measured figure copied into free prose, not mirrored) — extend the OQ-mirror pattern (`audit-docs` check 15) to it, or make a `docs/`-wide grep a standing correction step (executor's finding, credited) | tool or convention |
| 5.1 | **No re-cut** of Phase 2's W11-W14 boundaries; FR-RATE-34/40 get named deferrals inside W11's own plan | plan — no change |

**Maintainer acceptance:** _pending — no recommendation above binds until this line carries
a date and a decision._

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
