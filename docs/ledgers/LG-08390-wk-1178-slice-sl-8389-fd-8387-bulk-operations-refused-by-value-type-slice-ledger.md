---
id: LG-8390
family: ledger
title: WK-1178 SL 8389 — FD 8387, a bulk operation is refused by value type — slice ledger
status: active
created: 2026-11-05
owner: executor
tree: b987349621936656fdd73f7f7a1a7dfb989d586f
phase: P2
work: WK-1178
slice: SL-8389
plans: [PL-8388]
corrected_by: []
relates: [PL-8388, FD-8387, SL-8389, FR-233]
---

# LG-8390 — WK-1178 SL 8389: a bulk operation is refused by value type

**GO:** to-lead "2026-11-05 17:46:39 GMT" — "Maintainer: exec-sl8389 GO, brief 18705d626d4e, PL 8388 @d00c155c, new branch and worktree from R2 @cda3c0dc, unpushed; displaces nothing."
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL 8388 (`docs/plans/PL-08388-…`), SL 8389: T0–T5 (FR-233 amended; FR-228 and FR-234 read). Matrix: 16 cells, 5 refused (`uplift_table` and `uplift_by_filter` on `count`; `rebase_to_level` on `percentage`, `money_minor`, `count`), 11 allowed. Branch `sl-8389-refusal-by-type` from R2 `cda3c0dc326d4313add551693e3180d3b1e05a11` (`sl-8345-r2-cell-hard-error`, no origin ref), plan draft head `d00c155cf4af810e721a79b1e781a0c8c91031db` merged at T0.

### Task list

- T0 — worktree and merge `97518eea`; one conflict, `docs/INDEX.md`, taken theirs (INDEX regenerates at the mint, the lead's).
- T1 + T2 — tests-only commit `0b718b91`.
- T3 — spec and code, one commit `b9873496`.
- T4 — route runs in the DB window: **OWED**, see Build log.
- T5 — this ledger.

### Gate

Not the slice's own (A12): rides R2's gate or a gate after R2.

### Audit

(The auditor's, A14.)

### Build log

All logs: `~/.claude/jobs/69e9fd00/tmp/logs/`, `head=` first, `rc=` last. DB-free env (`GIP_DATABASE_URL`, `GIP_TEST_DATABASE_URL`, `GIP_REDIS_URL` all on 127.0.0.1:1) via `run-heavy.sh --over-load`. Written 2026-11-05 17:50:44 GMT.

**A3 — red first, T1, at `0b718b91` (tests-only), `t1-red.log`:** 5 failed by `DID NOT RAISE ValueError`, 103 passed, rc=1:
```
FAILED …::test_the_matrix[uplift_table-count]
FAILED …::test_the_matrix[uplift_by_filter-count]
FAILED …::test_the_matrix[rebase_to_level-money_minor]
FAILED …::test_the_matrix[rebase_to_level-percentage]
FAILED …::test_the_matrix[rebase_to_level-count]
5 failed, 103 passed in 10.90s    rc=1
```
The 11 allowed cells are green at base by design (they assert today's behaviour).

**A4 — plant P, T1 file, at `b9873496` (`t1-plantP.log`):** every value of `_OPERATION_VALUE_TYPES` set to `frozenset()`: `50 failed, 60 passed`, rc=1. Of the 16 matrix tests, exactly the 11 allowed cells failed (`floor_and_cap` ×4, `rebase_to_level-relativity`, `uplift_by_filter` ×3, `uplift_table` ×3) and the 5 refused cells and the 2 ordering tests passed; the other 39 failures are the file's existing relativity tests, refused by the planted break. Reverted with `git checkout -- operations.py`; `git diff --stat` empty. P never committed.

**A5/A6 — green, T1 file + `test_rate_table_operations.py`, at `b9873496` (`t1-green.log`):** `170 passed in 4.30s`, rc=0 (16 matrix cells + 2 ordering tests, every existing test unedited).

**A10 —** `ruff check .` rc=0 at `b9873496`. `ruff format --check` on the two changed test files is rc=1, and was before this slice: the files' existing code is unformatted (e.g. `_value`, :61); the slice's hunks are the plan's text, left as written. Second set (`a10b.log`): `31 passed, 4 errors`, rc=1; the 4 errors are `backend/tests/test_error_sinks.py` tests using `api_client`, `ConnectionRefusedError 127.0.0.1:1` — they need the DB, so they are **owed to the window**, not a pass. `test_worker_raise_sites.py` and `test_quote_input_raise_sites.py` passed.

**A11 — GREEN set by import closure.** Changed src: `operations.py`, `errors.py`. `git grep -l -E 'rate_tables\.operations|from pricing_core\.rate_tables import|rate_tables import operations' -- '*.py'` gives level 1: `backend/src/app/platform/rate_tables.py`, `pricing_core/rate_tables/weights.py`, tests `test_rate_table_bulk_ops`, `test_rate_table_operations`, `test_rate_table_weights`, `test_rating_compile_fr240`. Level 2 importers of `platform.rate_tables`: `api/rate_tables.py`, `platform/rating_versions.py`, `worker/rate_table_handlers.py`, tests `test_api_rate_tables`, `test_diff_cache`, `test_nfr498_audit_events`, `test_rate_table_diff_portfolio`, `test_rate_tables_service`, `test_rating_version_change_summary_route`, `test_worker_rate_tables`, plus `examples/fremtpl2/model.py` and `scripts/measure-p2-nfr-sweep.py`. `errors.py`'s closure is the whole backend; the gate's full suite is the decisive green. DB-free ones run: `test_rate_table_weights` + `test_rating_compile_fr240`: `56 passed`, rc=0 (`a11-free.log`). The backend files are DB-backed: owed.

**A7 —** see the report (diff checks).

**audit-docs (run-heavy --light, at 39b49133, `audit3.log`):** rc=1, `FAILED (9)`: check 31 gaps 2010→8321, 8323→8345, 8346→8388, 8388→8390 and check 32 on FD-8387 / SL-8389 / LG-8390 / PL-8388 (working ids, pre-mint). Nothing else in the block.

**Spec-reading tests (item 39), `grep -l 'docs/specs' backend/tests tests` lists 12:** DB-free, run at 39b49133 (`spec-readers.log`): `tests/test_audit_docs_ids.py`, `test_doc_id_history_input.py`, `test_doc_id_migrate.py`, `test_doc_id_verify.py`, `test_doc_index.py`, `test_file_census.py`, `test_scope_audit.py`, `backend/tests/test_lineage_census_carveout.py`, `test_severity_population_golden.py`: `3 failed, 695 passed, 1 skipped`, rc=1. The 3 failed are the docs-audit set on the working ids (`test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`, `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`: "live allocation is not contiguous" 2010/8321, 8323/8345, 8346/8388, 8388/8390); clear at the mint. **OWED (DB-backed, window):** `backend/tests/test_objective_submission.py`, `test_rating_version_create_pins.py`, `test_settings_environment.py`.

**Spec-reading tests, wider predicate (lead, HOLD):** `git grep -lE 'docs/specs|"docs" */ *"specs"' -- backend/tests tests` lists 18 files; the 6 not yet run are **OWED** until the lead lifts the HOLD: `backend/tests/test_contracts.py`, `backend/tests/test_demo_guide.py`, `backend/tests/test_route_scope_guard.py`, `tests/test_doc_id.py`, `tests/test_permission_parity.py`, `tests/test_repository_invariants.py` (the DB-free / DB-backed split is read at the run). No pytest or audit-docs started since the HOLD.

**Six owed spec-readers, run under the lead's side-run word (to-lead "2026-11-05 18:11:52 GMT" (2)), one file per call, DB-free, at e3644fc7 (`sr-*.log`):** `test_contracts.py` 177 passed, 2 skipped rc=0; `test_route_scope_guard.py` 10 passed rc=0; `tests/test_doc_id.py` 145 passed rc=0; `tests/test_permission_parity.py` 16 passed rc=0; `tests/test_repository_invariants.py` 2 failed, 9 passed rc=1 (`test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`: both assert `audit-docs.py` is clean on the real tree, so they carry its pre-mint failures; item 31's docs-audit set, clear at the mint); `backend/tests/test_demo_guide.py` 1 failed, 10 passed, 1 error rc=1, both `ConnectionRefusedError 127.0.0.1:1` (needs PostgreSQL): **OWED to the window**, not a pass.

**Re-merge onto R1 + R2 (2026-11-05, lead's order 22:30:30):** R1 landed on main as a squash (`5e5c83f7`); R2 (`sl-8345`) was re-merged by R1's final head `9c558846` (equal trees to main, `-s ours` with main) and is now `9bd52e2c`. SL 8389 merged it as `982dafa5` (tree `3f91f82fbf0085d6833158e35ae89f5a121e7a2f`); the only conflicts were docs: `docs/INDEX.md` (theirs, regenerated) and `docs/specs/03-rating-engine.md` (FR-233 row ours, FR-234 row theirs, which differs from the base only in R1's re-spelled working ids). `operations.py`, `errors.py` and both test files auto-merged. No test was run on the merged head (HOLD); the red/green lines above are at `0b718b91` / `b9873496` and are to be re-read at the merged head: **OWED**.

**T4 / DB window: OWED.** The window `sl8389` is queued behind LAST-1, FD 8366's, G and SL 8377 (brief). Three runs of `-k bulk_operation_value_type_matrix_at_the_route`: red at `0b718b91` (expect 5 failed with 201, 11 passed), green at `b9873496` (16 passed), plant P (11 red, 5 green). Lines to be appended.

## PRs

(None yet: ends unpushed.)
