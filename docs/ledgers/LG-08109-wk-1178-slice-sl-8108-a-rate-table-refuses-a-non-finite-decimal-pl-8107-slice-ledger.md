---
id: LG-8109
family: ledger
title: WK-1178 slice SL-8108 — a rate table refuses a non-finite decimal as a named FR-234 issue (PL-8107), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-18
owner: executor
tree: 4a53f19492ad73ebfb699cabcab19765c68a5a76
phase: P2
work: WK-1178
slice: SL-8108
plans: [PL-8107]
corrected_by: []
relates: [FR-234]
---

# LG-8109 — WK-1178 slice SL-8108: a rate table refuses a non-finite decimal

*(Working ids PL 8107, SL 8108 and LG 8109 are the lead's; cited by working id until minted.)*

**Base:** merge `e5e8cca2` of `origin/main` `4a53f19492ad73ebfb699cabcab19765c68a5a76` into the branch. Commit 1 is `0ac06deb`; commit 2 (the code) follows. The two are not squashed locally.

## Assumptions and build-time lines

- **DP-1 assumption.** No stored rate-table row holds a non-finite value, and the fix closes every write path (seed, manual edit, import, bulk). A diff over a legacy non-finite row raises the named `ValueError("OUT_OF_BOUNDS: …")` and is not mapped to a 422 (DP-1 (a)).
- **BUILD-TIME (f) pin and default traps.** Test (f) is replaced by the pin `test_a_bulk_operation_cannot_be_given_a_non_finite_percentage`. The default `Decimal` traps raise and do not yield ±Inf/NaN: `git grep -n "setcontext\|getcontext()\|localcontext\|traps" -- packages/pricing-core/src/pricing_core/rate_tables` printed nothing, and `git grep -n "setcontext\|getcontext()" -- packages backend/src` (tests excluded) printed nothing, rc 0, at the merged head.
- **Ordering deviation from PL 8107's "No change" row.** `uplift_table` and `uplift_by_filter` built the operation record *after* `_validate_result`. The record's `UpliftTableParameters` / `UpliftByFilterParameters` validate the parameters (`percentage` is a `DecimalStr` that refuses a non-finite value) and `_validate_result` computes on the result, so input validation belongs first. Both functions now build the operation record before `_validate_result`. The reason is input-validation order (the maintainer, to-lead "2026-10-18 08:33:40 BST"); this also makes the plan's row claim, that a NaN percentage never reaches `_validate_result`, true.

## Census — every `Decimal(` call in the rate-table code

Pattern: `git grep -n "Decimal(" -- packages/pricing-core/src/pricing_core/rate_tables backend/src/app/platform/rate_tables.py` (backend: no hit).

| Site | Verdict |
|---|---|
| `operations.py:166` (`str(Decimal(str(float)))`) | Covered: `seed_from_model` validates the result via `_value_issue`. |
| `operations.py:316` | **The fix**: `is_finite()` before the bounds compares. |
| `operations.py:414` (`_index_rows`) | **The fix (hardening)**: named `ValueError`. |
| `operations.py:451`, `weights.py:219-220` | Out of scope: exposure weights, not rate-table input. |
| `operations.py:502,504,735,757,844` | Constants / arithmetic, not a parse. |
| `operations.py:696,763,835,842` | Stored values, validated at save; results re-validated by `_validate_result`. |

## Red → green

- Red, `0ac06deb` plus the merge, run-small on `packages/pricing-core/tests/test_rate_table_operations.py`: `24 failed, 36 passed in 4.93s`.
- Green, the code commit, same file: `60 passed in 1.90s`. Also green: `test_rate_table_bulk_ops.py`, `test_rate_table_weights.py`, `test_demo_b4_premium.py` (73 passed) and `test_rating_compile_bundle.py`, `test_rating_runtime.py`, `test_rating_lookup_as_at.py` (67 passed).
- DB-backed rate-table tests (`backend/tests/test_rate_tables_service.py`, `test_api_rate_tables.py`) not run: no backend code changed; owed to the gate.

## Tasks

- Task 1 (commit `0ac06deb`): FR-234 amendment and class `TestEveryValueIsAFiniteDecimal` (24 red, the bounds pin green).
- Task 2 (commit 2): `_non_finite_message`, the `is_finite()` check in `_value_issue` before the bounds, the named `ValueError` in `_index_rows`, the operation record built before `_validate_result` in the two uplift functions.

## PRs

None opened by the executor; the lead opens the PR after the gate.
