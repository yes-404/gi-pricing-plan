---
id: CR-831
family: closure
kind: work
title: Work-item record — W10-1 (Rate Table Contract Shapes)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-28
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W10-1/README.md
---

# Work-item record — W10-1 (Rate Table Contract Shapes)

Audited 2026-08-28 against origin/main `3ff2cb3` (PR #297 merged), branch w10-1-rate-table-contract head `021ec40`.

## Scope

Derived from `docs/plans/PL-00829-wk-670-implementation-plan-rate-tables-seeding-diffs-bulk-operations-import-export.md` slice W10-1 first, then
evidenced. W10-1 defines the `RateTable` and `RateTableVersion` shapes in model-schema:
- RateTable (FR-228, FR-236): typed keys, value column, optional default row, rateable flag, storage mode
- RateTableVersion (FR-229, FR-232): immutable version, change_note required, storage mode fixed at write time
- RateTableKey, RateTableValue, RateTableStorageMode enums: type declarations with optional bounds, banding refs, storage mode enum
- Seeding metadata (FR-230): `seeded_from` artifact reference for lineage tracking

The slice gate (plan §4): the shapes parse, immutability invariants hold, storage mode is immutable with the version, and seeded_from metadata is captured.

## Evidence

**Scope-audit result:** 4 of 9 requirements evidenced (44%); 5 deferred per plan.

All 15 tests passing (15/15) in `packages/model-schema/tests/test_rate_tables.py`.

| Requirement | Verdict |
|---|---|
| FR-228 | ✓ delivered and tested — RateTable shape with keys, value, optional default, rateable flag |
| FR-229 | ✓ delivered and tested — immutable RateTableVersion, change_note required |
| FR-236 | ✓ delivered and tested — rateable boolean (price vs diagnostic) |
| FR-232 | ✓ delivered and tested (partial) — storage mode immutable at write time |
| FR-230 | ✓ delivered, marker incomplete — seeded_from lineage metadata present |
| FR-231 | deferred to W10-2 — cell-level diffs |
| FR-233 | deferred to W10-3 — bulk operations |
| FR-234 | deferred to W10-2 — validation |
| FR-235 | deferred to W10-3 — CSV/XLSX import/export |

**Gate:** ruff clean · mypy --strict clean · 0 contracts broken · 15 tests pass ·
docs audit clean · req-coverage 4/9 requirements

## Sign-off

Auditor verdict: slice verified. FR-230 test marker noted for W10-2 (finding F-W10-1-1).
