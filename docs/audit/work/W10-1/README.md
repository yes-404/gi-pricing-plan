# Work-item record — W10-1 (Rate Table Contract Shapes)

Audited 2026-08-28 against origin/main `3ff2cb3` (PR #297 merged), branch w10-1-rate-table-contract head `021ec40`.

## Scope

Derived from `docs/plans/2026-08-28-w10-rate-tables.md` slice W10-1 first, then
evidenced. W10-1 defines the `RateTable` and `RateTableVersion` shapes in model-schema:
- RateTable (FR-RATE-14, FR-RATE-21): typed keys, value column, optional default row, rateable flag, storage mode
- RateTableVersion (FR-RATE-15, FR-RATE-62): immutable version, change_note required, storage mode fixed at write time
- RateTableKey, RateTableValue, RateTableStorageMode enums: type declarations with optional bounds, banding refs, storage mode enum
- Seeding metadata (FR-RATE-16): `seeded_from` artifact reference for lineage tracking

The slice gate (plan §4): the shapes parse, immutability invariants hold, storage mode is immutable with the version, and seeded_from metadata is captured.

## Evidence

**Scope-audit result:** 4 of 9 requirements evidenced (44%); 5 deferred per plan.

All 15 tests passing (15/15) in `packages/model-schema/tests/test_rate_tables.py`.

| Requirement | Verdict |
|---|---|
| FR-RATE-14 | ✓ delivered and tested — RateTable shape with keys, value, optional default, rateable flag |
| FR-RATE-15 | ✓ delivered and tested — immutable RateTableVersion, change_note required |
| FR-RATE-21 | ✓ delivered and tested — rateable boolean (price vs diagnostic) |
| FR-RATE-62 | ✓ delivered and tested (partial) — storage mode immutable at write time |
| FR-RATE-16 | ✓ delivered, marker incomplete — seeded_from lineage metadata present |
| FR-RATE-17 | deferred to W10-2 — cell-level diffs |
| FR-RATE-18 | deferred to W10-3 — bulk operations |
| FR-RATE-19 | deferred to W10-2 — validation |
| FR-RATE-20 | deferred to W10-3 — CSV/XLSX import/export |

**Gate:** ruff clean · mypy --strict clean · 0 contracts broken · 15 tests pass ·
docs audit clean · req-coverage 4/9 requirements

## Sign-off

Auditor verdict: slice verified. FR-RATE-16 test marker noted for W10-2 (finding F-W10-1-1).
