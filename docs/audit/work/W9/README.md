# Work-item record — W9 (the rating contract, validation, and bundle compilation)

Closed 2026-08-27. Scope and evidence audited against origin/main `3a4958a` (all three
W9 slices merged: #291, #292, #293).

## Scope

Derived from `03-rating-engine.md` first, then evidenced. W9's scope is the rating
contract and its validation: FR-RATE-1..13 (the algorithm shape, invariants, result
types), FR-RATE-22..27 (the RatingVersion pins, lifecycle, bundle, change summary),
FR-RATE-56/57/58/59 (the W8-confirmed boundary guards), and the design constraints
NFR-RATE-13/14.

## Evidence mapped to the three slices

| Slice | PR | Requirements delivered | Evidence |
|---|---|---|---|
| W9-1 — the RatingAlgorithm contract | #291 | FR-RATE-1 (DAG invariants), 2 (input contract), 3 (outputs), 4 (stable step_id), 6 (sub-graphs), 7 (structural diff), 8 (table steps), 9 (lookup steps), 10 (model_call mode), 11 (constraint steps), 12 (output rounding), 13 (money types) | `model-schema/rating.py` + `test_rating_algorithm.py` (12 tests, markers traced to the FR-RATEs); spec-reconciled vs `03` §4.1 |
| W9-2 — save-time validation + boundary guards | #292 | FR-RATE-1 (refused at save), 5 (deterministic), 13 (result types at save), 56 (integer minor units), 57 (guarded division), 58 (scale cap), 59 (vocabulary) | `pricing-core/rating/compile.py` + `test_rating_compile.py` (8 guard tests); `POST /rating-algorithms` validates-before-persist with `RATING_ERROR_CODES`; spec-reconciled vs `03` §5.2 |
| W9-3 — bundle compilation | #293 | FR-RATE-22 (pins), 23 (lifecycle), 24 (self-contained Bundle + hash), 25 (compilation validates), 26 (effective dates), 27 (change summary), 60 (model_reference_mode), + NFR-RATE-13/14 as design constraints | widened `RatingVersion` (spec-reconciled vs `03` §4.3); `compile_bundle`/`to_jdm`/`bundle_hash` (spec-reconciled vs `03` §5.2); `ArtifactResolver` protocol keeps pricing-core standalone; `POST /rating-versions/{id}/compile` |

## Requirement verdicts

| Requirement | Verdict | Evidence |
|---|---|---|
| FR-RATE-1..13 | delivered | marker-evidenced (req-coverage: FR-RATE-1 6 files, 2-13 at least 1 each) |
| FR-RATE-22..27 | delivered | marker-evidenced (22: 3, 23: 1, 24: 4, 25: 1, 26: 1, 27: 1) |
| FR-RATE-56/57/58/59 | delivered | marker-evidenced (56: 1, 57: 3, 58: 1, 59: 1) |
| FR-RATE-60 | delivered | marker-evidenced (3 files) |
| NFR-RATE-13 (validate inbound, never outbound) | deferred with an owner — the W10 scoring workstream | the compiler respects the constraint (the Bundle is constructed by pricing-core, no outbound validation); the premise was measured in W8 (p99 0.070 ms) and recorded in `03` NFR-RATE-13's amendment; no marker — the scoring endpoint is W10+ |
| NFR-RATE-14 (`nthread=1` per model_call) | deferred with an owner — the W10 scoring workstream | measured in W8's S2 spike (nthread=1 p99 1.09/1.626 ms, 3.3 % of the 50 ms budget); the constraint is recorded in `03` NFR-RATE-14; no marker — the `model_call` execution is W10+ |

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W9-1 | NFR-RATE-13 and NFR-RATE-14 carry no marker — they are design constraints whose measurement belongs to the W10 scoring workstream | carry forward with an owner (W10) — the W8 measurements and the `03` amendments are the recorded evidence | closed (carried to `docs/audit/register.md`) |

## Sign-off

Owner: the maintainer. Auditor close-confirmation: 2026-08-27. W9 is happy-to-close; the
two deferred constraints carry to W10 with their recorded measurements.
