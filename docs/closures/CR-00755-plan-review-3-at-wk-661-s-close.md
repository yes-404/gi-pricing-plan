---
id: CR-755
family: closure
kind: review
title: Plan review 3 — at WK-661's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-22
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 3 — at WK-661's close, 2026-08-22

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
Four found. **(a) `NFR-482` has no owner at all** — there is no Model export or import
path anywhere in the repository, and its parent FR-5 carries zero markers. It is a
capability nobody has been asked to build, and it is not a WK-661 defect: no row ever named it.
**(b) The constraint-level contract-drift guard** (`minLength`, `additionalProperties`,
`required`-set drift, and arm-level attribution inside `if`/`then`) is still unbuilt after
this slice closed the field-existence and nullability halves. **(c) `06` §3.3's "per-peril
model approvals"** is enforced nowhere and cannot be, while the models sit in JSONB.
**(d) `FR-107`'s `source_level_stats`** is in the contract and not in the Python.
**Proposal:** (b) and (d) to **WK-664** as the first consumer of these contracts; (c) to **WK-677**
as the workstream that owns evidence enforcement; **(a) needs a maintainer verdict before it
can have an owner** — it may simply be out of Phase 1 scope, in which case NFR-482 should
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
`contract-guard` skill, or a section in `contract-schema`, owned by WK-664.

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
or workstream boundaries is proposed**: WK-661's cut held, and the audit found defects *inside*
it rather than at its edges.

**Two answers of "no change", recorded because a silent question is indistinguishable from
one nobody asked:** the Phase 1b workstream rows need no re-cut, and no requirement needs
superseding beyond `transparency_artifact_id`, which this slice struck with its reason.

**Maintainer acceptance: accepted as proposed, 2026-08-22.** Each proposal below binds from
that date. Recorded per line rather than as one blanket sentence, because a single "accepted"
over five proposals leaves no way to tell later which of them anyone actually read.

- **Question 2, the owner assignments — accepted 2026-08-22.** (b) the constraint-level
  contract-drift guard and (d) `FR-107`'s `source_level_stats` are **WK-664's**, as the
  first consumer of these contracts; (c) `06` §3.3's per-peril model approvals are **WK-677's**,
  as the workstream that owns evidence enforcement.
- **Question 2 (a), `NFR-482` — accepted 2026-08-22 at the option the proposal named:
  out of Phase 1 scope.** The review said it "may simply be out of Phase 1 scope, in which
  case NFR-482 should say so"; it now does, in `02` §9. There is no Model export path and
  no import path anywhere — not a route, not a CLI, not a bundle schema — and its parent
  FR-5 carries zero markers. It is a capability nobody has been asked to build, and no row
  ever named it, so it was never a WK-661 defect. Saying so is the verdict §13 rule 1 requires;
  leaving it "unassigned" was the one row in the audit-remediation slice's verdict table that
  stated an absence of a verdict rather than a verdict.
- **Question 3, the `contract-guard` skill — accepted 2026-08-22, owned by WK-664**, as either a
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
