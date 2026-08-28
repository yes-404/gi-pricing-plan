# Work-item record — W10 (Rate Tables)

Closed 2026-08-28. Scope and evidence audited against origin/main `f442387` (all
slices merged: #297, #302, #304, #307, #310, #311, with rulings #299, #300, #305,
#306, #308, #309).

## Scope

Derived from `docs/specs/03-rating-engine.md` first, then evidenced. W10's scope is
03 §3.3 Rate tables: **FR-RATE-14..21 and FR-RATE-62 — 9 requirements.**
Reconciliation with the roadmap: the W10 row listed "FR-RATE-14..21" (8) and omitted
FR-RATE-62, which was appended 2026-08-18 (OQ-RATE-3) marked **Phase 2, with the
rate-table slice**; the row is corrected to "FR-RATE-14..21, FR-RATE-62" in this
commit. No NFR is in W10's scope (NFR-RATE-13/14 are the W11 scoring workstream's
constraints, carried from W9 as F-W9-1).

## Evidence mapped to the slices

| Slice | PR(s) | Requirements delivered | Evidence |
|---|---|---|---|
| W10-1 — the contract shapes | #297 | FR-RATE-14 (Rate Table definition), 15 (immutability, shape half), 21 (rateable vs diagnostic), 62 (storage immutability, shape half) | `model-schema/rating.py` + `test_rate_tables.py` (15 tests); record `docs/audit/work/W10-1/README.md` |
| W10-2 — seeding, diffs, validation | #302 | FR-RATE-16 (seed from an approved model), 17 (cell diff with exposure weighting, core), 19 (named validation on save) | `pricing-core/rate_tables/operations.py` + API suite; record `docs/audit/work/W10-2/README.md` |
| W10-3 — bulk ops, import/export, storage spill | #304, #307, #310, #311 (+ rulings #305/#306/#308/#309) | FR-RATE-18 (bulk ops record parameters), 20 (CSV/XLSX round-trip import), 62 (threshold, parquet spill, 202-with-Job), 15 (write-path half), 16 (seed-lineage guard), 19 (validate-before-persist on every write path) | record `docs/audit/work/W10-3/README.md` |

## Requirement verdicts

| Requirement | Verdict | Evidence |
|---|---|---|
| FR-RATE-14 | delivered and tested | model-schema RateTable shape (typed keys, value column with type/unit, optional default row); 1 marker file |
| FR-RATE-15 | delivered and tested | immutable version, change_note required on every create path (seed, bulk, import-confirm); 2 marker files |
| FR-RATE-16 | delivered and tested | seed-from-model with approval gate (FR-OVR-14 → PIN_NOT_APPROVED), `seeded_from` lineage; DP4: lineage survives every derivation — save-time equality guard (RATE_TABLE_SEED_MISMATCH 422, direction-neutral); 11 marker files |
| FR-RATE-17 | delivered and tested at the core, with a carry-forward | `diff_vs_previous` / `diff_vs_seed`, changed cells, max-abs and exposure-weighted mean change (hand-computed weighting test), `against=previous\|seed\|N`; **carry-forward (F-W10-2):** the endpoint passes no exposure weights — the portfolio-dataset join is scheduled in no slice; owner: portfolio-dataset integration |
| FR-RATE-18 | delivered and tested | four bulk operations, parameters recorded (04 §4.4 `BulkOperation`), named refusals, validate-before-persist; 24 marker files |
| FR-RATE-19 | delivered and tested | complete key-domain coverage or explicit default row, no nulls, in-bounds values, no duplication — each failure named, checked before the version persists on every create path; 5 marker files |
| FR-RATE-20 | delivered and tested | export CSV/XLSX; import with strict round-trip (keys/types/completeness), presented as a diff, `confirm: true` creates the version on the same bytes (DP6); uploaded filename bounded ≤255, never a path (DP5); 26 marker files |
| FR-RATE-21 | delivered and tested | `rateable` boolean declared at seed, diagnostic tables never feed the premium ladder (shape-level); 1 marker file |
| FR-RATE-62 | delivered and tested | `storage` rows\|parquet decided against the workspace's `rate_tables.cell_threshold` (default 250 000) at write time, immutable with the version (DP2: threshold changes reach new versions only); rows → SQL join diff, parquet → content-addressed blob + 202-with-Job diff returning the same artifact (worker `JobResult(kind="blob")`); DP3 DiffCache on the 200 read path; 25 marker files |

**Coverage:** 9 of 9 in-scope requirements carry test evidence (100 %; scope-audit
§3.3, run at `f442387`), with the exposure-weight wiring carry-forward the one
delivered-with-owner item.

**Interface coverage (scope-audit --endpoints):** 03 §5.1 declares 7 rate-table rows;
6 are published in the generated OpenAPI (seed-from-model, bulk-operation, diff,
export/csv, export/xlsx, import) — FR-PLAT-48 satisfied for them, typed 200
`RateTableDiff` / 202 `Job` on diff. The 7th, `POST /api/v1/rate-tables/{slug}/versions`
(Phase-0 row, "New Rate Table Version with change note"), has no route: version
creation happens via the three create paths. **Deferred with an owner — the W15
rate-table editor slice** (the manual editing entry point); register row F-W10-3.
The other 13 un-published §5.1 rows belong to W11–W15 (scoring, dislocation,
deployment) — phase-boundary carries, already registered as F8.

## Not delivered by W10

| Item | Verdict |
|---|---|
| `POST /rate-tables/{slug}/versions` and the plan's W10-1 T3 create/GET/list endpoint tasks | deferred with an owner — W15 rate-table editor (F-W10-3); the plan-only tasks were never spec-declared and fold into the same row |
| FR-RATE-17 exposure-weight wiring at the endpoint | deferred with an owner — portfolio-dataset integration (F-W10-2, registered) |
| NFR-RATE-13/14 measurement | not W10's scope — carried to W11 with the W8 measurements recorded (F-W9-1, registered) |
| Roadmap §5 retrofit mapping | none of the three §5 rows touches rate tables; W10's own retrofit-impossible item — a change of storage threshold must never re-home existing versions (FR-RATE-62) — was delivered with DP2, and the W10-2 501 interim was superseded in place by 3D, the old blockquote standing as the record |

**Spec record notes (non-blockers):** 03 §4.2's example version shows
`diff_vs_previous`/`diff_vs_seed` keys — the diff endpoint's read model, not stored
fields; candidate annotation cleanup. `docs/contracts/schemas/rate-table.schema.json`
is an unreferenced Phase-0 hand-authored schema; cleanup candidate, owner: the
maintainer.

## Gate

Measured in audit at the final head `d6d05ad7` (= merged `f442387`): ruff clean ·
mypy clean (146 files, zero suppressions) · lint-imports 3 contracts kept, 0 broken ·
pytest 2233 passed / 2 skipped / 1 xfailed = 2236 collected (reconciled against
`--collect-only`, exact match with the executor's claim) · audit-docs all passed ·
req-coverage clean · generate-contracts --check 28/28 · scope-audit §3.3 9/9.
CI on the merge: docs success, frontend success, python in flight at filing time
(lead verifies terminal state). Slice-level gates are recorded in the per-slice
records with their measured numbers.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| F-W10-1 / F-W10-1-1 | W10-1 deferrals (FR-RATE-17/18/19/20; FR-RATE-16 marker) | resolved in W10-2 / W10-3 — all delivered and tested | closed (register updated in-slice) |
| F-W10-2 | FR-RATE-17 exposure-weight wiring — the portfolio-dataset join is scheduled in no slice | carry forward with an owner — portfolio-dataset integration | carried (register row) |
| F-W10-2-1 | DP3 diff cache unbuilt, deferral undeclared in #302 | resolved 2026-08-28 (PR #311) — DiffCache shipped with 3D | closed (register row updated) |
| FR-PLAT-48 (F-W10-2-2) | untyped diff 200 — the ADR-0002 divergence class | resolved 2026-08-28 (PR #311) — typed 200 in the contract; row filed with the discharge | closed (register row filed) |
| F-W10-3 | 03 §5.1 `POST /rate-tables/{slug}/versions` has no route | deferred with an owner — W15 rate-table editor | carried (register row filed) |

## Sign-off

Owner: the maintainer. Auditor close-confirmation: 2026-08-28. W10 is happy-to-close:
9/9 requirements delivered and tested (100 % coverage), the two open carries have
named owners (portfolio-dataset integration; W15), and the three register rows below
record the discharged deferrals. Closure acceptance is the maintainer's call; the
filed record and its open findings are presented for it.
