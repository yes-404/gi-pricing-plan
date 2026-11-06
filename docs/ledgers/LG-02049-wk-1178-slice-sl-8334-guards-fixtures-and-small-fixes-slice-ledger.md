---
id: LG-2049
family: ledger
title: WK-1178 slice SL-2048 — guards, fixtures and small fixes (FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-06   # original date 2026-11-05, working id 8335, minted 2026-11-06
owner: executor
tree: ec4c4240c6c20d3b75490a9cdeb9a88fe05efab4   # sl-8334-h-guards, the code head this was written against (base e8a597700687aff394e13da0035f10d2419ce893)
slice: SL-2048
phase: P2
work: WK-1178
plans: [PL-2047]
corrected_by: []
relates: [FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493, PL-2047, FR-11, FR-140, NFR-499]
---

# LG-2049 — WK-1178 slice SL-2048: guards, fixtures and small fixes

*(Minted 2026-11-06 as LG-2049 from working id 8335, with the plan PL-2047 (working id 8333) and the slice SL-2048 (working id 8334), in the SL-2048 PR.)*

**GO:** to-lead "2026-11-05 10:31:31 GMT" (plans C and H accepted; DP-H1 to DP-H5 ruled: stop by name with no auto-upgrade; a database ahead of the branch passes with a warning; no widening of sink shapes; the rest declared outside mypy; `check=True`, no prune; FD-1507's rule is handler-bound or a parameter named `exc`; FD-1662 re-measured at 2 errors, no carry), on the order of "2026-11-05 09:58:58 GMT".
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2047 (a dated Work-plan delta), "SL-2048 — guards, fixtures and small fixes". Seven findings, seven independent commits pairs (G5): FD-1488 (R1), FD-1507 (R2), FD-1509 (R3), FD-1749 (R4), FD-1228 (R5), FD-1662 (R6), FD-1493 (R7). Requirements touched: NFR-499 (the census and the oidc handler), FR-11 and FR-140 (R5), FR-428 (R3's tests keep their markers). Write set as the plan states; the only product files are `backend/src/app/auth/oidc.py` and `scripts/demo.py`'s annotation.

### Task list

1. **R1, FD-1488** — red `b96ea7da` (stub `migration_problem` returns `None`), green `970d4b62`: `backend/tests/conftest_db.py` (`migration_problem`, `_script_revisions` cached once, `_check_migrations_once`, a once-a-session flag in `database`), new `backend/tests/test_conftest_db_migration.py` (T1 four cases, T2 read-once, plus the exit/warn behaviour). A3's stamped proof: see Build log (owed until the DB window).
2. **R2, FD-1507** — red `2636dd39`, green `d849da2a`: `_sinks` keeps a set of enclosing `except … as` names and a parameter named `exc`; `_SINKS` gains six rows (A5, A6 below).
3. **R3, FD-1509** — red `846e71b0`, green `c896d015`: `route_class_problems` over the live app's routes (`body_field`, `response_model`; a `Page[Item]` through `__pydantic_generic_metadata__`), T5 on a minimal app with a local same-named class.
4. **R4, FD-1749** — red `626cb503`, green `3e1fc07b`: teardown extracted to `_remove_worktree`, `check=True`, `rmtree` in an inner `finally`; T6 on a throwaway `git init` repo.
5. **R5, FD-1228** — `b1140b0f`: `test_ebm.py` seed-reproducibility marker `FR-140` to `FR-11`.
6. **R6, FD-1662** — `48b745f6` (code), `8f3f537b` (DP-H4's line in `.claude/skills/repo-architecture/SKILL.md`): `check_environment` takes a `Mapping`; `scripts/demo.py` added to `pyproject.toml`'s `files`.
7. **R7, FD-1493** — red `aec3f2ea`, green `ec4c4240`: `except (DecodeError, RecursionError)` before the broad catch in `oidc.py`; T7 random bytes, T8 a signed 50 000-deep payload under the valid `kid`, T9 unknown `kid` control.

### Gate

Not run by the executor: the SOLO full gate at the re-merged head, after R's and A's (A12), is the lead's. Owed. Small runs below ran on the executor's own tree (`sl-8334`), `run-small.sh`, one file per call, dead-port DB and redis URLs, load1 under 6 at each start.

| Run (file) | rc | Summary line |
|---|---|---|
| `backend/tests/test_conftest_db_migration.py` | 0 | `6 passed, 3 warnings in 0.16s` |
| `backend/tests/test_error_sinks.py` | 1 | `9 passed, 2 warnings, 4 errors in 13.01s` — the 4 errors are DB-backed tests on the dead port (`ConnectionRefusedError`); not the census |
| `backend/tests/test_deployment_route_types.py` | 1 | `19 passed, 2 warnings, 1 error in 9.14s` — the error is `test_the_two_changed_approval_routes_return_exactly_the_declared_keys` (DB-backed), dead port |
| `tests/test_doc_id_migrate.py` | 0 | `306 passed in 153.69s (0:02:33)` (no gate slot held at the time) |
| `backend/tests/test_auth_oidc.py` | 0 | `13 passed, 2 warnings in 0.95s` |
| `test_error_sinks.py` + `packages/pricing-core/tests/test_quote_input_raise_sites.py` (ONE call, two files: a breach of the brief's one-file-per-call rule, reported to the lead; both files DB-free apart from the same 4 dead-port errors) | 1 | `28 passed, 2 warnings, 4 errors in 18.43s` |

`uv run mypy`: rc 0, `Success: no issues found in 253 source files`. `ruff check` on every touched Python file: rc 0 (`conftest_db.py`, `test_error_sinks.py`, `test_deployment_route_types.py` were already unformatted at the base; format was not applied to them).

### Audit

(The auditor's, with the lead's adoption, in the audit's own commit.)

### Build log

**Reds, by cause, each committed alone before its green** (A2; the logs' first lines name the run, quotes are verbatim):

- **R1** (`b96ea7da`): `assert None is not None` at `test_conftest_db_migration.py:22` and `:35`; `2 failed, 2 passed`. Cause: the stub returns `None` for a database one revision behind.
- **R2** (`2636dd39`): `AssertionError: assert {} == {('renamed.py..., '{exc}'): 1}`; `FAILED backend/tests/test_error_sinks.py::test_the_census_sees_an_injected_sink`; `1 failed, 8 passed, 2 warnings, 4 errors`. Cause: `except ValueError as problem: return str(problem)` is missed by the name tuple. Census delta with the new rule: exactly the six new rows, no sink lost (`_census()` against `_SINKS`, `/tmp/sl8334-census.py`).
- **R3** (`846e71b0`, a mutation proof: `route_class_problems` stubbed to `[]`, the essay's `openapi_problems` blindness): `FAILED …::test_a_same_named_local_class_is_refused_by_the_class_check`; `1 failed, 18 passed, 2 warnings, 1 error`.
- **R4** (`626cb503`, a mutation proof: removal left at `check=False`): `Failed: DID NOT RAISE CalledProcessError`; `1 failed, 305 passed in 116.11s`.
- **R6**: `scripts/demo.py:77: error: Incompatible types in assignment (expression has type "_Environ[str] | dict[str, str]", variable has type "dict[str, str] | None")  [assignment]` and `scripts/demo.py:78: error: Item "None" of "dict[str, str] | None" has no attribute "get"  [union-attr]`; `Found 2 errors in 1 file (checked 253 source files)`, rc 1, with `scripts/demo.py` in `files` and the base `demo.py`. Exactly two, so the CARRY fallback is not taken.
- **R7** (`aec3f2ea`): `AssertionError: assert 'signing key ...: DecodeError' == 'malformed token'` for T7 and T8; `2 failed, 11 passed`. T9 passed at the base and after (control).

**A5.** `git grep -n '("exc", "e", "err")' -- backend/tests/test_error_sinks.py` prints nothing (rc 1). **A6.** No site can hold a quote input. `runtime.py:822` was read first: `_ModelCallRefusal` is raised once, `_predict_model`'s last statement, with the step id (authored in the graph) and the model_type (from the artifact). The other five: a `SwitchIncompleteError` (process ids), two `consumed_features` `ValueError`s on a stored model's fit result (fixed texts), a Custom Objective's `ObjectiveError` at compile, and a smoke fit over seeded synthetic rows.

**A7.** The live-route class check and T5 are in. With the import kept and a local same-named class appended, `ast_problems` reports nothing for the four Environment rows (the AST half checks only the imported set), so it is the live check that catches that variant; the existing import-removed variant still fails the AST half (`test_a_body_class_defined_in_the_api_module_is_refused`). Reported to the lead as a reading of A7, who accepted it: the live-route class check is what catches that case.

**A8.** `git diff e8a59770...HEAD -- tests/test_doc_id_migrate.py | grep -ci prune` prints `0`.

**A9.** `scripts/req-coverage.py` before and after `b1140b0f` (it counts markers): `FR-11 1 → 2`, `FR-140 36 → 35`, no other line differs. FR-11 (00-overview) is determinism: identical inputs and pinned versions reproduce identical outputs, with an explicit persisted seed. The moved test is that. The remaining FR-140 markers in `packages/pricing-core/tests/test_ebm.py`, for the auditor's own read against FR-140's text (the transparent-by-construction export of term shape functions as tables, no approximation, with the fidelity/diagnostic sections): `:193` `test_fit_returns_the_expected_tables`; `:223` `test_the_exported_tables_reproduce_interpret_predict`; `:255` `test_an_interaction_fit_exports_a_rectangular_grid`; `:294` `test_scoring_matches_interpret_on_a_held_out_frame`; `:333` `test_a_scored_term_resolves_from_the_artifact_alone`; `:391` `test_a_monotone_constraint_on_a_categorical_feature_is_refused_by_name`; `:398` `test_a_monotone_constraint_naming_an_unknown_slug_is_refused_by_name`; `:448` `test_fit_seconds_and_library_versions_are_recorded` (the essay "notes and does not decide": left as FR-140).

**A10.** `uv run mypy` rc 0 with `scripts/demo.py` in `files`; `.claude/skills/repo-architecture/SKILL.md` declares `scripts/` and `backend/tests/` outside the gate (DP-H4), its Verified line carrying the tree `b4f4f7e24efeea0ebfc84282fe8e94c88492a943`.

**A11.** T7, T8 and T9 green (`13 passed`); the new handler logs the type only and the census still passes with no new row.

**A3 (run, DB window granted by the lead, START 2026-11-05 11:01:49 GMT, END 11:06:48 GMT).** Tree `ec4c4240c6c20d3b75490a9cdeb9a88fe05efab4` (code head). Template guard before createdb and at END: `alembic_version=1 environments=3 tenant_marker=1`. Copy `gipricing_sl8334a3` (`createdb -T gipricing`), every URL (`GIP_DATABASE_URL`, `GIP_MIGRATION_DATABASE_URL`, `GIP_TEST_DATABASE_URL`) on the copy, redis `-n 11`; load1 4.40 and 8 GB available at start. One DB-backed file, `backend/tests/test_workspaces.py`, through run-small:
- stamped one back (`b7e4c2a91d36 -> 9b3e7c15d4a2`): rc 1 in 25 s, `_pytest.outcomes.Exit: the test database is at ['9b3e7c15d4a2'], the scripts' heads are ['b7e4c2a91d36']: run `uv run alembic upgrade head` against this database (FD-1488)`;
- restamped to head: rc 0 in 23 s, `2 passed, 2 warnings in 2.08s`;
- a revision the scripts do not know (set by SQL on the copy only, DP-H2): rc 0, `UserWarning: the test database is ahead of this checkout: ['zz_unknown_ahead'] is not a revision of these migration scripts (DP-H2)`, `2 passed, 3 warnings in 3.43s`.
END: `redis-cli -n 11 FLUSHDB` then `-n 11/12/13 dbsize` = 0, 0, 0; `-n 0 dbsize` = 56 before and after; copy dropped, `select count(*) from pg_database where datname='gipricing_sl8334a3'` = 0; datnames `gipricing postgres template0 template1`.

## PRs

(Added at the PR.)
