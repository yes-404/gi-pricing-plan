---
id: CR-820
family: closure
kind: work
title: WK-665 — freMTPL2 modelling half: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-27
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-665 — freMTPL2 modelling half: closed 2026-08-27

Evidence pins: close-time origin/main = `a9b0326` (#271). WK-665 shipped as three batches:
#267 (Batch A), #268 (Batch B), #271 (Batch C). The auditor's evidence is
W6B-AUDITOR-HANDOVER.md §23–§26; the §13 verdicts are the manager's, quoted verbatim in
§3–§4.

#### 1. Scope

WK-665 is the freMTPL2 demo seed — the modelling half (roadmap §6 row). The plan is
`docs/plans/PL-00816-wk-665-implementation-plan-the-fremtpl2-modelling-half-phase-1b-exit.md`. The scope: a fitted GLM on freMTPL2,
a rating version, and `WF-698` end to end. The manager's OD rulings (2026-08-27) set the
boundaries: full GLM+GBM journey with comparison (OD3 b), a minimal Phase 1b rating
version minted as FR-440 (OD1 a), the NFR-482 verdict reversed (OD2 a), seed-time
fit with a sample fallback on budget breach (OD4 a+b), and a scripted HTTP exit run
(OD5 a).

Slices: W7-1 (demo models, carried-forward obligations), W7-2 (comparison and approval),
W7-3 (the Phase 1b rating version), W7-4 (obligation checks), W7-5 (the exit demo).

#### 2. Delivery — batches and PRs

| Batch | PR | Squash | Content |
|---|---|---|---|
| A | #267 | `836b417` | freMTPL2 demo models (GLM+GBM), split, factors, the carried-forward obligations (FR-57/58, NFR-482 tests) |
| B | #268 | `4493f80` | the demo comparison and approval; the Phase 1b rating version (FR-440, `RatingVersion`, `GET /rating-versions/{id}`) |
| C | #271 | `a9b0326` | the exit demo: journey timing, postcondition check, demo guide links, acceptance statement |

#### 3. The WK-665 requirement set — verdicts (manager, 2026-08-27)

| Requirement | Verdict | Evidence (markers cited) |
|---|---|---|
| FR-439 | DELIVERED | 2 markers, examples/fremtpl2/test_seed.py :34, :47 |
| FR-440 | DELIVERED | 7 markers, test_rating_versions.py (3) + test_rating.py (4) |
| FR-57 | DELIVERED | 1 marker, test_reference_pin.py (the pinned, None, and pinned-but-unprofiled paths) |
| FR-58 | DELIVERED | 1 marker, test_api_models.py (HTTP 409 broken-input proof) |
| NFR-482 | DELIVERED | 2 markers, test_model_round_trip.py |
| FR-59 | DEFERRED | Phase 2 validation-report successor; not built in Phase 1b |
| FR-67 | DEFERRED | trigger = named exposure-ordered reader; unowned by design |

5 of 7 evidenced. The two unevidenced are deliberate deferrals with named successors.

#### 4. Not delivered — verdicts (manager, 2026-08-27)

| ID | Verdict | Owner / trigger |
|---|---|---|
| FR-59 | DEFERRED | Phase 2 validation-report successor (`unrun_layers` projection) |
| FR-67 | DEFERRED | trigger = a named exposure-ordered reader; unowned by design |

The full `03` rating surface (compile, score, rate tables, deployment) stays Phase 2. The
rating version built here is the Phase 1b subset scoped by the dated `03` §4.3 note.

#### 5. Exit criterion

The core `WF-698` journey is delivered and postcondition-checked: validated freMTPL2
dataset → split → factors → GLM and GBM fits through the real Job path → comparison →
approved model → approved rating version. `demo.py _verify_journey_postconditions`
asserts an approved model over HTTP and refuses to start the browser otherwise.

The full `WF-698` §4 surface (versioned bandings and groupings, approved Peril Structure
with reconciliation) is **not** seeded; those surfaces stay Phase 2 (auditor W7-5 drift
1). The roadmap's Exit demo row reads "pending"; the acceptance mechanism is stated
(scripted HTTP run, UI available for hands-on driving).

#### 6. Module delta (vs `ebba7de`, pre-WK-665)

| Module | In scope | Evidenced | Note |
|---|---|---|---|
| PLAT | 78 | 48 (62%) | FR-440 added and evidenced |
| DATA | 67 | 63 (94%) | FR-57/58 evidenced; FR-59/67, NFR-465/466 unevidenced |
| MODEL | 143 | 128 (90%) | NFR-482 evidenced |

WK-665 closed three previously unevidenced WK-664 focus items (FR-57, FR-58,
NFR-482) and added FR-440 evidenced.

#### 7. Residue and carry-forward

- The full-seed NFR-529 measurement (678 013 rows, GLM+GBM fit) ran end to end in
  **131 s — 43.7% of the 300 s budget** — with one approved model, the rating version
  approved, and the postcondition banner reached. The v1 failure is the deliberate
  validation step, not a defect.
- `GET /rating-versions/{id}` and the new list route have no direct test; the service and
  resolver are tested. The RatingVersionView has no test file (structural gap).
- Batch C's change set has no test files; the demo postcondition check is exercised by
  the W7-5 exit demo run, not by pytest.
- Carry-forward into Phase 2: FR-59 (`unrun_layers`), FR-67 (trigger), the full
  `03` surface, and WF-698's remaining §4 postconditions (bandings, Peril Structure,
  reconciliation).

#### 8. Sources

- W6B-AUDITOR-HANDOVER.md §23–§26 (WK-665 audit records, the §13 evidence pass at `a9b0326`).
- W6B-CLOSE-RECORD-DRAFT-2026-08-27.md (the WK-664 close, carry-forward to WK-665).
- `docs/plans/PL-00816-wk-665-implementation-plan-the-fremtpl2-modelling-half-phase-1b-exit.md` (the plan).
- origin/main `a9b0326` (#271); roadmap §6 (the WK-665 row).
