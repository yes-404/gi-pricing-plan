---
id: LG-1995
family: ledger
title: WK-690 slice SL-1994 — FD-1842, the FR-145 bound before the recursive structure walk, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-03               # drafted 2026-11-03 under working id 8300
owner: executor
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe   # origin/main at the branch cut (base 7db485bf)
slice: SL-1994
phase: P2
work: WK-690
plans: [PL-1996]
corrected_by: []
relates: [FD-1842, PL-1996]
---

# LG-1995 — WK-690 slice SL-1994: FD-1842, the bound before the structure walk

**GO:** to-lead "2026-11-03 16:13:51 GMT": option (ii), SL-1994 = FD-1842 alone; DP-8301-1 (a); DP-8301-2 (a); full SOLO gate; merge by Fri 6 Nov 2026.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-1996 as amended by the 16:13:51 entry (limb 1, FD-1751, struck). Requirements: FR-145, §4.6 (FR-150 and FR-95 for the two callers' codes).

### Task list

- **T-1** (`9e1c4288`): limb 1 struck in PL-1996 and the roadmap SL-1994 row.
- **T0**, re-read at base 7db485bf; no line moved: `expressions.py`: `parse_expression` :288-304 (`_check` :299, `_check_structure` :300, `_check_limits` :303), `_measure` iterative; `objectives.py` `grammar_refusal` :295-318, `_require_the_grammar` :321, call :240; `modelling.py` :295 (`_require_a_creatable_expression` :276); `02-modelling.md` §4.6 depth ≤ 20, ≤ 200 nodes; `ExpressionLimits` 200 / 20.
  **Correction to the lead's relay:** the relay said both callers answer `OBJECTIVE_GRAMMAR_VIOLATION`. The factor caller (`POST /factors`, `modelling.py`) answers 422 `VALIDATION_FAILED` on `expression`; only create answers `OBJECTIVE_GRAMMAR_VIOLATION`. Accepted by the lead; `modelling.py` is unchanged.
- **T1** reds (`84e9ad34`): pricing-core `test_expression_limits.py` (4 tests × 2 profiles) and `backend/tests/test_custom_objectives_expression.py` (objectives and factor callers by direct call, DB-free; create route, DB-backed).
- **T2** fix: `_check_limits` moved ahead of `_check_structure` in `parse_expression`.
- **T3** spec: FR-145 / §4.6 clarification in `02-modelling.md`.

### Gate

Grant for the DB-free single-file runs: to-lead "2026-11-03 17:19:47 GMT". Logs are under `~/gi-pricing-plan.local/scratch/sl8299/` (head= first line, rc= last).

| file | head | result |
|---|---|---|
| `packages/pricing-core/tests/test_expression_limits.py` | 84e9ad34 | **red:** 8 failed, 19 passed, rc=1. Cause: `RecursionError` at `expressions.py:259` in `_check_structure` from `parse_expression:300` (6 tests); `AssertionError: _check_structure ran before the FR-145 bound refused` (2 tests). |
| same | fix commit | 2 failed, 25 passed: my own expectation was wrong (the 2000-character chain trips the 200-node bound first), not the fix. |
| same | after the expectation fix | **green:** 27 passed, rc=0. |

ruff check packages/pricing-core rc=0; mypy `expressions.py` rc=0 (head cdfceea5 or its parent).

Pre-grep for the run (file and its conftest chain `packages/pricing-core/tests/conftest.py`, `conftest.py`): `grep -n -i "postgres|redis|database|DATABASE_URL|psycopg|asyncpg|autouse|localhost"` printed nothing, rc=1.

**Backend runs (DB window 2026-11-04 03:07:49Z to 03:09:12Z; own database `gipricing_sl-8299_91c667a0`, Redis db 11, template never written; END zeros: Redis db 11 `dbsize` 0, `pg_database` count for the own DB 0).** Every file under `backend/tests/` is behind `backend/tests/conftest.py`, which re-exports `conftest_db`'s autouse `_seed_through_the_owner_seam` (conftest_db.py:1447) and session-autouse `_empty_the_database_after_the_session` (:1632), so even the direct-call tests needed the window. Logs are under `~/gi-pricing-plan.local/scratch/sl8299/`:

| log | head= | result | rc= |
|---|---|---|---|
| `backend-prefix-84e9ad34.log` (`-k "over_bound or deep or grammar_refusal"`, `expressions.py` as of 84e9ad34, worktree c6d4d2b1) | 84e9ad34 | 3 failed, 6 passed, 23 deselected | 1 |
| `backend-c6d4d2b13bf001dcddc05515401305824804b914.log` (all of `backend/tests/test_custom_objectives_expression.py`) | c6d4d2b1 | 32 passed, 1 warning | 0 |
| `green-limits3-c6d4d2b13bf001dcddc05515401305824804b914.log` (`packages/pricing-core/tests/test_expression_limits.py`, run 3 Nov 18:21 UTC, DB-free) | c6d4d2b1 | 27 passed | 0 |

The pre-fix reds, by cause. **Real reds (3):** `test_an_over_bound_loss_is_422_grammar_violation_on_create[2000-character unary chain]` answered 500 `INTERNAL_ERROR` (log: `SanitisedError: RecursionError`, `ast.py:274`); `test_grammar_refusal_does_not_raise_recursion_error_on_a_deep_loss` and `test_a_deep_factor_expression_is_422_not_recursion_error` each raised `RecursionError`. **Characterisation passes (6), already 422 before the fix:** the create route at depth 21 and at 201 nodes (`OBJECTIVE_GRAMMAR_VIOLATION`); `grammar_refusal` at depth 21 and 201 nodes; the factor caller at depth 21 and 201 nodes (`VALIDATION_FAILED`). So "never a 500" was a real defect only for the deep-chain case at both callers.

DB-free check for the `test_expression_limits.py` run, quoted: `grep -n -i "postgres|redis|database|DATABASE_URL|psycopg|asyncpg|autouse|localhost"` over that file, `packages/pricing-core/tests/conftest.py` and `conftest.py` prints nothing (rc=1); the run set dead-port `GIP_TEST_DATABASE_URL` and `GIP_TEST_APP_DATABASE_URL`.

### Audit

(The auditor's.)

### Build log

- 2026-11-03: T-1, T0, T1, T2, T3 as above.
- 2026-11-04: DB window 03:07:49Z to 03:09:12Z; the backend red and green lines are in the Gate section above. The full SOLO gate is a separate seat.

## PRs

(Added at the PR.)
