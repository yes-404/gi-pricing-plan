---
id: CR-823
family: closure
kind: review
title: Plan review 5 — at WK-664's close
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-27
owner: lead
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/plan-reviews.md
---

### Plan review 5 — at WK-664's close, 2026-08-27

`CLAUDE.md` §14 requires a plan review at **each workstream close**. This is the fifth; the
procedure is `.claude/skills/phase-review`. **The output is a proposal, never a change** —
every recommendation below needs a dated maintainer acceptance line before it binds. Findings
about Phase 2 or later are **spec changes only** (§0's table). Evidence derived at
`8b0977f` (#260).

#### Question 1 — Completion

Fresh audit evidence, derived at `8b0977f` by a delegated collector. Both inputs are
documents, so the answer does not depend on who ran it. All slices shipped at close
(#243–#263); the manager's close audit counts 245/320 evidenced across the WK-664 scope.

- Requirements: 531 specified, 274 marked (51.6%) repo-wide.
- Phase 1b modules: DATA 61/67 (91%), MODEL 127/143 (89%), GOV 27/53 (51%),
  PLAT 47/77 (61%), OVR 10/33 (30%).
- Endpoints: DATA 39/39, MODEL 44/44, GOV 13/23, PLAT 19/22.
- Catalogue: DATA validation rules 38/38.
- RATE 2/78, OPT 0/37, MON 0/43: zero evidence is expected. These are Phase 2/3.

The roadmap's closure records carry counts that no longer match the derived numbers.
Example: the MODEL closure record states 125 in scope and 111 evidenced. Today the audit
derives 143 in scope and 127 evidenced. `req-coverage.py` read 495/248 at WK-661 close. It
reads 531/274 today. The drift is consistent with append-only requirement ids
(CLAUDE.md §5). A reader cannot tell an at-close count from a current count unless the
reader re-runs the audit.

**Proposal 1.1:** each closure record names the tree it derived its counts from, as the
WK-692 closure record already does. No re-derivation is owed. The record states its snapshot.
**No change** to the phase's completion claim otherwise. The WK-664 close runs the audit
again after Groups B and C land. This review's numbers are the pre-close baseline.

#### Question 2 — Omission

What does Phase 1b need that no row names?

**(a) The role routes declared in 06 §5.1 have no HTTP route.** The spec declares
`GET/POST /api/v1/roles`, `POST /api/v1/role-assignments`, and `POST /api/v1/break-glass`
(06:436-438). No backend route serves any of them. The machinery exists at the service
layer (rbac.py, RoleRow, RoleAssignmentRow). The WK-659 closure record claims RBAC delivered.
A caller who copies §5.1 gets a 404. The §5.3 `/admin/access` view is Phase 3. The
resolution must decide: these routes are Phase 1b scope owned by nobody, or Phase 3
surface declared ahead of the phase. **Recommendation:** record them as spec-ahead-of-phase
with a dated note in 06 §5.1, which matches the FR-344 class. Do not build them at the
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
record the limitation in the close-workstream skill before the WK-664 close counts GOV
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
  `source_model_version` in code. Neither appears in the spec. The OQ-604 ruling
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
- **GOV 06 §5.1, FR-344 class:** attestations, dossiers, change control, audit/anchor.
  Declared with no route, all Phase 3 by the roadmap. This is spec-ahead-of-phase, not
  drift. No change.
- **RATE 03 §5.1 and PLAT 07 §5.1 Phase 2 surfaces:** declared, no code. Expected.
  No change.
- **Checked and agreed:** the list below. All 39 DATA endpoints and their params. All 44
  MODEL endpoints. The bulk of 02 §5.2 signatures. The built half of 06 §5.1. The built
  half of 07 §5.1. The §5.3 routes. The named catalogues. The money rule.

#### Question 5 — Shape

WK-664 is the last Phase 1b workstream. It now spans a Vue view, an OIDC flow, a workspace
selector, lineage, route reachability, rule versioning, and the model workbench. Review 4
named this smell: a row that crosses many kinds cannot be audited as one thing. The close
audit answers it. It derives scope from merged commits, filed plans, and the handover
set. It never derives scope from the frozen slice-map. Keep that mechanism.

The phase exit criterion, `WF-698` end to end on freMTPL2 through the UI, is still not met
at `8b0977f`. The work that remains is WK-665's modelling half and the demo.py auth-profile
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
- `docs/roadmap.md`: plan reviews 1-4, the WK-664 and WK-665 rows.
- W6B-CLOSE-RECORD-SKELETON-2026-08-26.md.

---
