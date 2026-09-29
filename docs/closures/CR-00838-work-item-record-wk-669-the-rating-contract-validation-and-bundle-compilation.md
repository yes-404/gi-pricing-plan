---
id: CR-838
family: closure
kind: work
title: Work-item record — WK-669 (the rating contract, validation, and bundle compilation)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-28
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W9/README.md
---

# Work-item record — WK-669 (the rating contract, validation, and bundle compilation)

Closed 2026-08-27. Scope and evidence audited against origin/main `3a4958a` (all three
WK-669 slices merged: #291, #292, #293).

## Scope

Derived from `03-rating-engine.md` first, then evidenced. WK-669's scope is the rating
contract and its validation: FR-212, FR-213, FR-214, FR-215, FR-216, FR-217, FR-219, FR-220, FR-221, FR-222, FR-225, FR-226, FR-227 (the algorithm shape, invariants, result
types), FR-237, FR-238, FR-239, FR-240, FR-241, FR-242 (the RatingVersion pins, lifecycle, bundle, change summary),
FR-273/274/275/276 (the WK-668-confirmed boundary guards), and the design constraints
NFR-502/501.

## Evidence mapped to the three slices

| Slice | PR | Requirements delivered | Evidence |
|---|---|---|---|
| W9-1 — the RatingAlgorithm contract | #291 | FR-212 (DAG invariants), 2 (input contract), 3 (outputs), 4 (stable step_id), 6 (sub-graphs), 7 (structural diff), 8 (table steps), 9 (lookup steps), 10 (model_call mode), 11 (constraint steps), 12 (output rounding), 13 (money types) | `model-schema/rating.py` + `test_rating_algorithm.py` (12 tests, markers traced to the FR-RATEs); spec-reconciled vs `03` §4.1 |
| W9-2 — save-time validation + boundary guards | #292 | FR-212 (refused at save), 5 (deterministic), 13 (result types at save), 56 (integer minor units), 57 (guarded division), 58 (scale cap), 59 (vocabulary) | `pricing-core/rating/compile.py` + `test_rating_compile.py` (8 guard tests); `POST /rating-algorithms` validates-before-persist with `RATING_ERROR_CODES`; spec-reconciled vs `03` §5.2 |
| W9-3 — bundle compilation | #293 | FR-237 (pins), 23 (lifecycle), 24 (self-contained Bundle + hash), 25 (compilation validates), 26 (effective dates), 27 (change summary), 60 (model_reference_mode), + NFR-502/501 as design constraints | widened `RatingVersion` (spec-reconciled vs `03` §4.3); `compile_bundle`/`to_jdm`/`bundle_hash` (spec-reconciled vs `03` §5.2); `ArtifactResolver` protocol keeps pricing-core standalone; `POST /rating-versions/{id}/compile` |

## Requirement verdicts

| Requirement | Verdict | Evidence |
|---|---|---|
| FR-212, FR-213, FR-214, FR-215, FR-216, FR-217, FR-219, FR-220, FR-221, FR-222, FR-225, FR-226, FR-227 | delivered | marker-evidenced (req-coverage: FR-212 6 files, 2-13 at least 1 each) |
| FR-237, FR-238, FR-239, FR-240, FR-241, FR-242 | delivered | marker-evidenced (22: 3, 23: 1, 24: 4, 25: 1, 26: 1, 27: 1) |
| FR-273/274/275/276 | delivered | marker-evidenced (56: 1, 57: 3, 58: 1, 59: 1) |
| FR-223 | delivered | marker-evidenced (3 files) |
| NFR-502 (validate inbound, never outbound) | deferred with an owner — the WK-670 scoring workstream | the compiler respects the constraint (the Bundle is constructed by pricing-core, no outbound validation); the premise was measured in WK-668 (p99 0.070 ms) and recorded in `03` NFR-502's amendment; no marker — the scoring endpoint is WK-670+ |
| NFR-501 (`nthread=1` per model_call) | deferred with an owner — the WK-670 scoring workstream | measured in WK-668's S2 spike (nthread=1 p99 1.09/1.626 ms, 3.3 % of the 50 ms budget); the constraint is recorded in `03` NFR-501; no marker — the `model_call` execution is WK-670+ |

> **Dated correction, 2026-09-29 (the auditor), on the maintainer's decision.** The verdict table above types `FR-217` "delivered" (line 39). Evidence at `origin/main` `49604a31785c8e7709e9b87c3926e27ea1c0f7f2`: **guard delivered; `sub_graphs` inlining NOT delivered → FD-1241.** The reference shape `SubGraphRef` is built (`packages/model-schema/src/model_schema/rating.py:340-351`) and `FR-218`'s fail-closed guard is built (`packages/pricing-core/src/pricing_core/rating/score.py:393-410`); `compile_bundle` never reads `sub_graphs`, a sub-graph is not a stored or pinned artifact, and no record defers the inlining. The verdict text above is not rewritten, and the other twelve requirements in that row are unaffected. The maintainer's entry "2026-09-29 16:25:49 BST · maintainer (acting on the maintainer's behalf) · BLOCKER DECISIONS by delegation: #882, the Dependabot merges, the Actions majors, FR-217, FD-1238, and the WK-672/PR16 acceptance" (`~/gi-pricing-plan.local/channel/to-lead.md`, §4) decided **not to reopen the closed Work** and routes the remedy through plan review 16 to the Work that takes `FR-218`'s authoring half.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W9-1 | NFR-502 and NFR-501 carry no marker — they are design constraints whose measurement belongs to the WK-670 scoring workstream | carry forward with an owner (WK-670) — the WK-668 measurements and the `03` amendments are the recorded evidence | closed (carried to `docs/findings/register.md`) |

## Sign-off

Owner: the maintainer. Auditor close-confirmation: 2026-08-27. WK-669 is happy-to-close; the
two deferred constraints carry to WK-670 with their recorded measurements.
