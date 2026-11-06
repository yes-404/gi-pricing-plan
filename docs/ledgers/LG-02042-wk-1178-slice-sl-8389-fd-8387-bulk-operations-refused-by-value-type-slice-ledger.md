---
id: LG-2042
family: ledger
title: WK-1178 SL-2041 — FD-2032, a bulk operation is refused by value type — slice ledger
status: closed   # closed by the audit commit of this PR, 2026-11-06
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8390, minted 2026-11-06
owner: executor
tree: b987349621936656fdd73f7f7a1a7dfb989d586f
phase: P2
work: WK-1178
slice: SL-2041
plans: [PL-2040]
corrected_by: []
relates: [PL-2040, FD-2032, SL-2041, FR-233]
---

# LG-2042 — WK-1178 SL-2041: a bulk operation is refused by value type

**GO:** to-lead "2026-11-05 17:46:39 GMT" — "Maintainer: exec-sl8389 GO, brief 18705d626d4e, PL-2040 @d00c155c, new branch and worktree from R2 @cda3c0dc, unpushed; displaces nothing."
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2040 (`docs/plans/PL-2040-…`), SL-2041: T0–T5 (FR-233 amended; FR-228 and FR-234 read). Matrix: 16 cells, 5 refused (`uplift_table` and `uplift_by_filter` on `count`; `rebase_to_level` on `percentage`, `money_minor`, `count`), 11 allowed. Branch `sl-8389-refusal-by-type` from R2 `cda3c0dc326d4313add551693e3180d3b1e05a11` (`sl-8345-r2-cell-hard-error`, no origin ref), plan draft head `d00c155cf4af810e721a79b1e781a0c8c91031db` merged at T0.

### Task list

- T0 — worktree and merge `97518eea`; one conflict, `docs/INDEX.md`, taken theirs (INDEX regenerates at the mint, the lead's).
- T1 + T2 — tests-only commit `0b718b91`.
- T3 — spec and code, one commit `b9873496`.
- T4 — route runs in the DB window: **OWED**, see Build log.
- T5 — this ledger.

### Gate

The pytest reading of record is the paired gate, `scratch/sl8389-gate/gate/gate.log`, on `94cd3e9f` (tree `23408d64`), paired with M: `pytest summary: 13 failed, 7268 passed, 27 skipped, 5 xfailed, 146 warnings in 5270.77s (1:27:50)`; skipped 27 = the baseline; the 13 failed are all in the eight docs-audit files (the item-31 set: `test_audit_docs_finding_citations`, `test_audit_docs_ids`, `test_audit_docs_process_core_digest`, `test_audit_docs_w37_11_ceiling`, `test_doc_index`, `test_register_lint`, `test_register_owed`, `test_repository_invariants`), "failing files outside the eight docs-audit files: [none]"; audit-docs rc 1 on check 31 and 32 of this slice's own working ids only. This gate's own demo stage was **NOT RUN**: OpenML `IncompleteRead(11270521 bytes read, …)` on the freMTPL2 fetch, the journey never started (to-lead "2026-11-06 01:24:04 GMT"); a third-party fetch failure is NOT RUN, not red.

The demo reading is `scratch/sl8389-gate/demo-run2/gate.log`, a demo-only re-run at the same head `94cd3e9f` seeded from the digest cache: `seeded, digests equal (freq a45363e0…, sev 04763201…)`; `END … rc=0 verdict=PASS`; demo 1522 s; dislocation #1 527 s (29 Oct passes 422 / 387 / 383 s). D7: "ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units". **D7's total and both attribution limbs equal on the 19985-policy sample** (the two limbs sum to the total); that is the reading, and it is not a statement that no price moved. That END's python and fe parts read 0 only because the run was demo-only; they are not the gate's.

Worktree data dir: no `.arff` file under `examples/fremtpl2/data` at the mint head (`find`, checked at the mint). R2's cover: R2 rides the same pair (`LG-2039`).

### Audit

*(Filed 2026-11-06 in the audit's commit from the draft `scratch/aud-sl8389/` (the LG 8390 audit-section draft), sha256 prefix `8b8cb5ba97f9`, by aud-sl8389, 2026-11-05, proposals only; adopted by the lead: `from-lead-2026-10-09.md` "2026-11-05 23:50:37 GMT". Object: `94cd3e9f24dfad2f0e0c97dd527505b21a621c11`, tree `23408d64ee6592967bc69bed5b7f404b61eb684d`, SL-2041's own delta `git diff f89963ac..94cd3e9f`. R2 not re-audited.)*

**Scope, from FR-233's dated clause and PL-2040 first.** Refuse a bulk operation when the column's value type gives its result no meaning: `rebase_to_level` only on `relativity`; `uplift_table` and `uplift_by_filter` refused on `count`; `floor_and_cap` on all four. 422 `BULK_OPERATION_NOT_APPLICABLE`, naming operation, value type and table; no version created.

**Matrix, my own enumeration** (`RateTableValueType` = relativity, money_minor, percentage, count; `model_schema/rating.py:1178`; 4 types × 4 operations = 16). `_OPERATION_VALUE_TYPES` (`operations.py:757`) = uplift_table, uplift_by_filter: all but count; floor_and_cap: all; rebase_to_level: relativity. Refused = 5, allowed = 11, equal to the spec row and to the tests' separate literal `_REFUSED_CELLS` / `_ROUTE_REFUSED`. Absence refuses (a fifth type is refused until said otherwise; the tests' `_ALL_CELLS` enumerates the enum, so a fifth type fails the allowed branch).

| Cell | Function (T1) | Route (T2) |
|---|---|---|
| uplift_table × count | red `DID NOT RAISE` (`t1-red.log`), green | red `assert 201 == 422` (`win-red.log`), green (`win-green.log`) |
| uplift_by_filter × count | same | same |
| rebase_to_level × percentage / money_minor / count | same (3 cells) | same (3 cells) |
| the 11 allowed cells | green at base by design; red under plant P (`t1-plantP.log`, `50 failed, 60 passed`, the 11 allowed matrix cells among them) | red under plant P: `win-plantP.log` `11 failed, 5 passed`; the failed set read by me = floor_and_cap ×4, rebase_to_level-relativity, uplift_by_filter ×3, uplift_table ×3 = exactly the 11 allowed cells |

Route red: 5 failed, each `assert 201 == 422` (read from `win-red.log`, `head=0b718b91`). Route green: `16 passed` at `14ea6467`; the only diff `14ea6467..94cd3e9f` is this ledger.

**Plan items.** A1 write set: met for the delta read (errors.py, operations.py, two test files, 03, 04, LG, plan, INDEX); the roadmap SL row, FD-2032's essay and the register row are not in the tree at the object or at origin/main: they are the mint's (see A13). `backend/src/app/api/`, `platform/`, `frontend/`, `docs/contracts/`, `deploy/`, `examples/`, `pricing_core/rating`: no diff. A2: the FR-233 clause and the code are one commit (`b9873496`) after the tests-only `0b718b91`; the code is in `03` §5.1's owned list (:1150) and `04` §4.4 (:276). A6: `_check_value_type` is the first statement of each operation; two ordering tests (filter-key, parquet) added in `b9873496`. A7: no line removed from either existing test file in the delta; `_format_value`, `_transform_rows`, `_new_version` outside the diff of `operations.py`. A8: the clause carries "moves premiums unless the base rate offsets it"; no behaviour added. A9: `merge-base --is-ancestor d00c155c HEAD` rc 0; `9bd52e2c` (R2) rc 0.

**Replay and re-derive (FR-239).** `created_by_operation` is written (`operations.py:688`) and returned (`platform/rate_tables.py:1350`, `:1464`); nothing reads it back to re-run an operation, and the only dispatcher is the request path (`_dispatch_operation`, `platform/rate_tables.py:1516`). A stored bulk version keeps its cells (FR-233 clause, `00` FR-4); so a stored operation of a now-refused pair has no replay path: same hash, same result. No existing caller applies a refused pair: the one operation in `examples/fremtpl2/journey.py:420` is `uplift_table` on a seeded table, and the only writer of a new table (`seed_from_model`, `operations.py:249`) sets `relativity`; import inherits the table's type. So FD-2032's "latent behind an unbuilt path" reads true: no route creates a non-relativity table (the route tests insert rows directly, `_insert_typed_table`).

**Registered code.** `app/errors.py:375` in `RATING_ERROR_CODES`; one owner line (03 §5.1 :1150); `REBASE_NO_MATCH`'s siblings are likewise not in `00` §5.3 (grep: `03` only), so no `00` row is owed. The route maps it by `_map_operation_error` (`platform/rate_tables.py:129`: an upper-case code with `_` → 422 under that code). No request shape moved (no `api/` diff); the sweep `backend/tests/test_api_authorisation_sweep.py` is the gate's.

**Observations (none a defect).** (a) Parameter validation (`model_validate`) precedes the value-type refusal at the route, so a refused pair with malformed parameters answers `VALIDATION_FAILED`, not the refusal; both 422, no version; A6 does not claim otherwise. (b) The two ordering tests have no red-at-base line: they were added with the fix in `b9873496`; the plant P shows the matrix, not the ordering. (c) Build log has no `ruff format --check` pass for the two test files (pre-existing unformatted, stated in the LG).

**Docs conflict at the merge.** `03` FR-234 row at the object is byte-identical to origin/main's (sha256 prefix `7bf858ef763a` both); FR-233 row is the slice's clause on the base text.

**My runs at 94cd3e9f (run-heavy, DB-free dead-port form, logs `~/gi-pricing-plan.local/scratch/aud-sl8389/logs/`, `head=` first, `rc=` last):** `packages/pricing-core/tests/test_rate_table_bulk_ops.py` `119 passed in 8.02s` rc=0 (`bulk2.log`; the first attempt, `bulk.log`, rc=2 was a collection error `No module named 'openpyxl'` from a venv without `--all-packages`, fixed by `uv sync --all-packages --frozen` in my own worktree). `audit-docs.py` (run-heavy --light) rc=1, `FAILED (20)` (`audit.log`): check 31 gaps 2021->8345, 8346->8388, 8388->8390; check 32 on SL-2041 / FD-2032 / PL-2019 (working ids, pre-mint) **and one that is not a working id: `LG-2042...:82: padded id (the five-digit form of PL-2019) outside a link target`** (RFC-937 §1.1 rule 2), to be written as the integer `PL-2019` before the PR.

**Verdicts proposed.** MET: matrix, refusal order, registration, route 422, red-first on the 5 cells at both levels, plant P on the 11 allowed cells at both levels, FR-239/replay, FD-2032 latent as filed, A7, A8, A9. NOT MET (fix before PR): the padded five-digit `PL-2019` at LG-2042 :82.
- OWED-TO-GATE: the DB-backed closure members not run in the window (`test_diff_cache`, `test_nfr498_audit_events`, `test_rate_table_diff_portfolio`, `test_rate_tables_service`, `test_rating_version_change_summary_route`, `test_worker_rate_tables`, `test_api_authorisation_sweep.py`); `generate-contracts --check`, `req-coverage`, `audit-docs` (pre-mint working ids) from the gate.
- OWED-TO-MINT: SL row (read at origin/main and at the object: no `SL-2041` row in `docs/roadmap.md`; it must read closed by the close commit, item 42), FD-2032 essay + register row, INDEX.

**Status at filing (2026-11-06).** The one NOT MET, the five-digit padded form of `PL-2019` at :82, is written `PL-2019` in the mint commit (`git grep -c` for the padded form over this file after the edit: 0). OWED-TO-GATE is discharged by the paired gate under Gate below: the closure's DB-backed members ran inside its pytest (13 failed, every one of the eight docs-audit files, the item-31 set; 7268 passed; 27 skipped, the baseline), `generate-contracts --check` rc 0 and `req-coverage` rc 0 are the gate's own rows. **Item 43, this slice's request-shape reading:** no `backend/src/app/api/` diff, so no request shape moved; `backend/tests/test_api_authorisation_sweep.py` sits in the gate's pytest with no `FAILED` line and no `SKIPPED` line (`grep -c` of the file name over the quiet-mode `pytest.log` = 0), stated as a pass by absence, not a count. **Item 42, the `SL-` row:** read at `origin/main` (`695ad9059e66`): `docs/roadmap.md` has no row for `SL-2038` or `SL-2041` (0 hits for either id or for working ids 8345 and 8389); both rows are added by this PR and read `closed` at this audit commit, as C's `SL-2026` was.

*Adoption: the lead's line, `from-lead-2026-10-09.md` "2026-11-05 23:50:37 GMT": "aud-sl8389 FINAL adopted, released: MET all; one fix at the mint: LG 8390 :82 padded [five-digit form of PL-2019, elided so check 32 does not read the quote] → PL-2019 (not now: gate reads the worktree); item 42 + FD 8387 closing after batch 12 mints it; drafts scratch/aud-sl8389 8b8cb5ba97f9, 4b0d2b82a872." The MERGE-ACK is written at the merge.*

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

**audit-docs (run-heavy --light, at 39b49133, `audit3.log`):** rc=1, `FAILED (9)`: check 31 gaps 2010→8321, 8323→8345, 8346→8388, 8388→8390 and check 32 on FD-2032 / SL-2041 / LG-2042 / PL-2040 (working ids, pre-mint). Nothing else in the block.

**Spec-reading tests (item 39), `grep -l 'docs/specs' backend/tests tests` lists 12:** DB-free, run at 39b49133 (`spec-readers.log`): `tests/test_audit_docs_ids.py`, `test_doc_id_history_input.py`, `test_doc_id_migrate.py`, `test_doc_id_verify.py`, `test_doc_index.py`, `test_file_census.py`, `test_scope_audit.py`, `backend/tests/test_lineage_census_carveout.py`, `test_severity_population_golden.py`: `3 failed, 695 passed, 1 skipped`, rc=1. The 3 failed are the docs-audit set on the working ids (`test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`, `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`: "live allocation is not contiguous" 2010/8321, 8323/8345, 8346/8388, 8388/8390); clear at the mint. **OWED (DB-backed, window):** `backend/tests/test_objective_submission.py`, `test_rating_version_create_pins.py`, `test_settings_environment.py`.

**Spec-reading tests, wider predicate (lead, HOLD):** `git grep -lE 'docs/specs|"docs" */ *"specs"' -- backend/tests tests` lists 18 files; the 6 not yet run are **OWED** until the lead lifts the HOLD: `backend/tests/test_contracts.py`, `backend/tests/test_demo_guide.py`, `backend/tests/test_route_scope_guard.py`, `tests/test_doc_id.py`, `tests/test_permission_parity.py`, `tests/test_repository_invariants.py` (the DB-free / DB-backed split is read at the run). No pytest or audit-docs started since the HOLD.

**Six owed spec-readers, run under the lead's side-run word (to-lead "2026-11-05 18:11:52 GMT" (2)), one file per call, DB-free, at e3644fc7 (`sr-*.log`):** `test_contracts.py` 177 passed, 2 skipped rc=0; `test_route_scope_guard.py` 10 passed rc=0; `tests/test_doc_id.py` 145 passed rc=0; `tests/test_permission_parity.py` 16 passed rc=0; `tests/test_repository_invariants.py` 2 failed, 9 passed rc=1 (`test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`: both assert `audit-docs.py` is clean on the real tree, so they carry its pre-mint failures; item 31's docs-audit set, clear at the mint); `backend/tests/test_demo_guide.py` 1 failed, 10 passed, 1 error rc=1, both `ConnectionRefusedError 127.0.0.1:1` (needs PostgreSQL): **OWED to the window**, not a pass.

**Re-merge onto R1 + R2 (2026-11-05, lead's order 22:30:30):** R1 landed on main as a squash (`5e5c83f7`); R2 (`sl-8345`) was re-merged by R1's final head `9c558846` (equal trees to main, `-s ours` with main) and is now `9bd52e2c`. SL-2041 merged it as `982dafa5` (tree `3f91f82fbf0085d6833158e35ae89f5a121e7a2f`); the only conflicts were docs: `docs/INDEX.md` (theirs, regenerated) and `docs/specs/03-rating-engine.md` (FR-233 row ours, FR-234 row theirs, which differs from the base only in R1's re-spelled working ids). `operations.py`, `errors.py` and both test files auto-merged. No test was run on the merged head (HOLD); the red/green lines above are at `0b718b91` / `b9873496` and are to be re-read at the merged head: **OWED**.

**Greens at the merged heads (2026-11-05 23:21 word, run-heavy, DB-free dead-port form, one file per call; logs `r2-*.log`, `m-*.log`, `docs-*.log`, `head=` first, `rc=` last):**
- R2 `sl-8345` @9bd52e2c: `test_rate_table_bulk_ops` 101 passed rc=0; `test_rating_compile_fr240` 31 passed rc=0; `test_quote_input_raise_sites` 19 passed rc=0; `test_glm_scalar_predict` 39 passed, 4 skipped rc=0; `test_rating_score` 53 passed rc=0; `test_safe_error` 18 passed rc=0.
- SL-2041 @43156978: `test_rate_table_bulk_ops` 119 passed rc=0 (R2's 101 + SL-2041's 16 matrix + 2 ordering); `test_rate_table_operations` 60 passed rc=0; `test_rating_compile_fr240` 31 rc=0; `test_quote_input_raise_sites` 19 rc=0; `test_rating_score` 53 rc=0; `test_safe_error` 18 rc=0; `test_glm_scalar_predict` 39 passed, 4 skipped rc=0; `packages/model-schema/tests/test_money.py` 20 passed rc=0; `test_decimal_schema_pattern.py` 17 passed rc=0.
- Docs: `sl-8345` @9bd52e2c: `doc-index --check` rc=1 (INDEX stale, 2208 records), `audit-docs --light` rc=1, FAILED (12): check 32 on LG-2039 / SL-2038 / PL-2019 plus one padded `PL-2019` that was my LG line (fixed, `f89963ac`), check 39. `sl-8389` @fe586f35 (after the INDEX regeneration): `doc-index --check` rc=0; `audit-docs --light` rc=1, FAILED (15): check 31 gaps 2021→8345, 8346→8388, 8388→8390; check 32 on SL-2041 / FD-2032 (LG-2042, PL-2040) and `PL-2019` in LG-2039 (R1 re-minted PL-2019 as PL-2019; R2's LG still cites the working id, re-pointed at R2's mint). All working ids, pre-mint.

**T4 / DB window `sl8389` — 2026-11-05 23:27:33 GMT to 23:34:49 GMT (lead's word after sl8328f's END 23:24:46; no gate running, exec-mintf's DB-free files beside).** Driver `~/gi-pricing-plan.local/scratch/sl8389-win.sh`; copy `gipricing_sl8389`, redis db 12, bucket `gip-test-blobs-sl8389`, `GIP_GATE_SLOT=/tmp/slots/window-sl8389` read from the process environ in each log. START: load1 2.28, avail 18 G, template guard `alembic_version=1 environments=3 tenant_marker=1`, db 0 = 56, db 12 = 0, `PUBSUB gip:switch:*` empty. END: db 12 = 0, db 0 = 56, copy count 0, bucket removed, template guard `alembic_version=1 environments=3 tenant_marker=1` rc 0. No `test_deployment_switch*`. Logs `win-*.log`.
- **A3 route red @0b718b91 (tests-only), `-k bulk_operation_value_type_matrix_at_the_route`:** `5 failed, 11 passed, 81 deselected` rc=1; all 5 `assert 201 == 422` (uplift_table-count, uplift_by_filter-count, rebase_to_level-{percentage,money_minor,count}).
- **A5 route green @14ea6467:** `16 passed, 82 deselected` rc=0.
- **A4 plant P (route, @14ea6467, `_OPERATION_VALUE_TYPES` all `frozenset()`):** `11 failed, 5 passed, 82 deselected` rc=1; the 11 failed are exactly the allowed cells; `git checkout -- operations.py`, `git diff` empty, porcelain 0.
- **R2's owed route test @8e674265 (R2's red):** `test_bulk_operation_with_a_huge_percentage_is_a_coded_422_not_a_memory_fault` `1 failed` rc=1 (`assert 1000368 < 2000`: the 422 body is ~1 MB); @14ea6467: `1 passed` rc=0.
- **Whole `backend/tests/test_api_rate_tables.py` @14ea6467:** `98 passed` rc=0 in 135 s.
- **Owed files @14ea6467:** `test_error_sinks.py` 13 passed rc=0; `test_demo_guide.py` 12 passed rc=0; `test_objective_submission.py` 22 passed rc=0; `test_rating_version_create_pins.py` 15 passed rc=0; `test_settings_environment.py` 23 passed rc=0.
- Not run in the window (the gate's full suite is the decisive green for them, A11): the other DB-backed closure members (`test_diff_cache`, `test_nfr498_audit_events`, `test_rate_table_diff_portfolio`, `test_rate_tables_service`, `test_rating_version_change_summary_route`, `test_worker_rate_tables`).

## PRs

(None yet: ends unpushed.)
