---
id: LG-1957
family: ledger
title: WK-675 slice FD-1585 — the diff routes answer NOT_FOUND (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29               # drafted 2026-10-26 under working id 8271
owner: executor
tree: 7ed5c398333aa24432bd9917bd204f7b540fb39c   # origin/main at the branch cut (#1401)
slice: SL-1956
phase: P2
work: WK-675
plans: [PL-1546]
corrected_by: []
relates: [FD-1585, PL-1546, FR-231, FR-232]
---

# LG-1957 — WK-675 slice FD-1585: the diff routes answer NOT_FOUND

Working ids SL-1956 (slice) and LG-1957 (ledger), reserved by the lead. Plan: `PL-1546` delta row 9
(branch `docs/pl1546-fd1585-delta-2026-10-26` @`67adc216`, PR #1402, unmerged when this was opened).
Grant: to-lead "2026-10-26 15:32:26 GMT" (reds only today); throwaway rule: "2026-10-26 14:44:23 GMT" (d).

**GO:** reds only (15:32:26 GMT). **MERGE-ACK:** pending — the code, greens and gate follow #1402's merge.

## Tasks

Row 9 of the delta: R-0 and R-1 (reds) and R-2 (controls) today; R-3 to R-6 (the two
`with spec_not_found():` wraps, the docstring, greens, gate) are a later brief.

## Gate

Pending (not today).

## Audit

Pending.

## PRs

None yet (reds only; no PR today).

## Build log

### 2026-10-26 — R-0 and R-1: base, tests-only commit

- Branch `fix/fd1585-diff-not-found`, worktree `.claude/worktrees/fd1585`, base `head=7ed5c398333aa24432bd9917bd204f7b540fb39c`.
- Re-located at the base (`backend/tests/test_api_rate_tables.py`): R1 `test_diff_404s_for_unknown_table_and_version` :487 (assert :506), R2 `test_diff_seed_without_a_seed_origin_404s` :547 (assert :601, docstring :552), R3 `test_import_preview_creates_nothing` :1097 (assert :1121), R4 `test_import_confirm_cannot_override_the_verdict` :1164 (assert :1184), C1 `test_bulk_operation_on_a_missing_version_is_refused` :919 (assert :929, unedited, `RATE_TABLE_MISS`), C2 `test_diff_rejects_an_unknown_baseline` :524.
- Tests-only commit `84f41899382bed0a30e41391f75856fc704511bd` (tree `e0558994d7857ff21ea09f0be3356f04fac76feb`): R1 re-pointed to `NOT_FOUND` plus code asserts on `@9` and `against=previous` on v1, plus an explicit `against=7`; R2 re-pointed and docstring corrected; R3, R4 re-pointed; R5 new `test_diff_cells_404s_not_found_for_unknown_table_version_and_against` (req FR-231, FR-232). No production code touched. `ruff check` on the file: rc 0.

### 2026-10-26 — R-1 / R-2: the reds and the controls on a throwaway (rc and failure lines)

Throwaway, all on `127.0.0.1` with ephemeral ports and anonymous volumes: `fd1585-pg` (`postgres:16-alpine`, container `fbf1ed84a319`, port 32822), `fd1585-redis` (`redis:7-alpine`, `f449234254c7`, redis db 0 of its own container), `fd1585-minio` (`minio/minio:latest`, `29644408d135`, bucket `gip-test-blobs-fd1585`). BEFORE: `docker ps -a --filter name=fd1585` empty, dangling images 0. Migrated as the owner (`alembic upgrade head`, rc 0), login role provisioned (`scripts/provision-app-role.py --allow-default-password`, rc 0). Every run through `run-heavy.sh --grant "2026-10-26 15:32:26 GMT"`; logs in `~/gi-pricing-plan.local/scratch/fd1585/{reds,controls}.log`, `head=` first, `rc=` last.

**Reds** — `head=84f41899382bed0a30e41391f75856fc704511bd`, `pytest -q -p no:cacheprovider --tb=line` on the five test ids: `5 failed, 1 warning in 3.85s`, `rc=1`. Each by cause (the diff routes answer `RATE_TABLE_MISS`, the test asserts `NOT_FOUND`):

| red | failure line |
|---|---|
| R1 `test_diff_404s_for_unknown_table_and_version` | `test_api_rate_tables.py:506: AssertionError: assert 'RATE_TABLE_MISS' == 'NOT_FOUND'` (first assert; the later `@9`, `previous`, `7` asserts are not reached at the base) |
| R2 `test_diff_seed_without_a_seed_origin_404s` | `test_api_rate_tables.py:640: AssertionError: assert 'RATE_TABLE_MISS' == 'NOT_FOUND'` |
| R3 `test_import_preview_creates_nothing` | `test_api_rate_tables.py:1160: AssertionError: assert 'RATE_TABLE_MISS' == 'NOT_FOUND'` |
| R4 `test_import_confirm_cannot_override_the_verdict` | `test_api_rate_tables.py:1223: AssertionError: assert 'RATE_TABLE_MISS' == 'NOT_FOUND'` |
| R5 `test_diff_cells_404s_not_found_for_unknown_table_version_and_against` | `test_api_rate_tables.py:547: AssertionError: assert 'RATE_TABLE_MISS' == 'NOT_FOUND'` (first GET, unknown table on `…/diff/cells`) |

A first attempt of the same command timed out in `run-heavy.sh`'s wait for the `seat-heavy` flock (held by another seat's demo run), `rc=124`; no test ran and it is not a red.

**Controls** — `head=84f41899382bed0a30e41391f75856fc704511bd`: C1 `test_bulk_operation_on_a_missing_version_is_refused` (unedited, `RATE_TABLE_MISS`), C2 `test_diff_rejects_an_unknown_baseline` (`against=banana` 422), C3 `test_rate_table_diff_portfolio.py`, C4 `test_worker_raise_sites.py`, one run: `75 passed, 2 warnings in 63.00s (0:01:03)`, `rc=0`.

**Removal.** `docker rm -fv fd1585-pg fd1585-redis fd1585-minio` rc 0, all three names echoed; AFTER: `docker ps -a --filter name=fd1585` empty, dangling images 0 (before: 0).

Not run today (reds-only grant): the two `with spec_not_found():` wraps, the `spec_not_found` docstring, the greens R-5 and the gate R-6.

### 2026-10-26 — docs checks on this ledger's commit

`doc-index.py --root docs --check`: `docs/INDEX.md: OK (byte-stable)`, rc 0 (regenerated first). `audit-docs.py` via `run-heavy.sh --light`: rc 1, only the two lints on this slice's own working ids: `check 31: gap in the full allocation between 1955 and 8271` and `check 32: …LG-1957…:9: SL-1956 does not resolve in docs/INDEX.md`. Both clear at the mint (the ids are working ids until then).

- 2026-10-26 15:59 GMT (lead): `ruff format --check backend/tests/test_api_rate_tables.py` reports "1 file would be reformatted" on this branch, and the SAME on origin/main's copy (tools-main @a9ffc22c). The drift is pre-existing at main, not this slice's; `.github/workflows/python.yml` runs no `ruff format` step. No reformat in this slice (to-lead "2026-10-26 15:58:34 GMT").

### 2026-10-26 — R-0 re-merge, R-3/R-4 the code, R-5 the greens (exec-fd1585code; grant "2026-10-26 16:00:41 GMT")

- **Re-merge.** `git merge --no-ff origin/main` (main `a9ffc22c9de4f9adee39f782e65a27d016d004c8`) into `b6f47e6f`: clean, rc 0, one file in (`PL-01546-wk-675-slices-5-to-11-work-plan-delta.md`, +122), no conflict; merge commit `768e3b64a799f39b6412c009a2215e17f4dbaa47` (tree `3e3ef67fcfd221d24b8acabf56e214e0d61aea27`), pushed.
- **The code**, commit `5b1464ecab1bc3f7df2d1f3670b2b500973a0632` (`backend/src/app/api/rate_tables.py` only, +13/−10): `answer = await service.diff_from_artifact(…)` (`:439` at the merge head, after the portfolio `require_permission` block, before `if isinstance(answer, service.DiffCellsJobNeeded)`) and `answer = await service.diff_cells_page(…)` (`:537`, same neighbours) each wrapped in `with spec_not_found():`; `_parse_against` (422), the permission check (403) and `_cells_job_response` are outside the wrap. `spec_not_found`'s docstring (`:72-76`) gains "The two diff routes' unknown table, version or `against` take the same mapping (FD-1585)."
- **Throwaway** (names `fd1585c-*`, `127.0.0.1` ephemeral ports, anonymous volumes): `fd1585c-pg` `99a411820e6a` (`postgres:16-alpine`, :32828), `fd1585c-redis` `4b4527e560fc` (`redis:7-alpine`, db 11), `fd1585c-minio` `7af92fa1ea91` (bucket `gip-test-blobs-fd1585c`). BEFORE: no `fd1585*` container, dangling 0. `scripts/provision-app-role.py --allow-default-password` rc 0; `alembic upgrade head` (owner DSN, `uv run --directory <wt>`) rc 0.
- **Greens**, `head=5b1464ecab1bc3f7df2d1f3670b2b500973a0632` (log `~/gi-pricing-plan.local/scratch/fd1585c/greens.log`): R1–R5 + C1 (`test_bulk_operation_on_a_missing_version_is_refused`) + C2 (`test_diff_rejects_an_unknown_baseline`) + C3 (`test_rate_table_diff_portfolio.py`) + C4 (`test_worker_raise_sites.py`): `80 passed, 2 warnings in 71.27s (0:01:11)`, `rc=0` (reds-day controls were 75; +5 = R1–R5). A first launch timed out in `run-heavy.sh`'s wait for `seat-heavy` (`rc=124`, no test ran).
- **Full backend suite on the login role**, same throwaway, same head (`pytest -q backend/tests`, `…/full.log`): `2974 passed, 13 skipped, 5 xfailed, 136 warnings in 1713.73s (0:28:33)`, `rc=0`. The 13 skips are below the END row's baseline of 21.
- **Removal.** `docker rm -fv fd1585c-pg fd1585c-redis fd1585c-minio` rc 0, three names echoed (redis db 11 held 42 keys at removal; its container is gone); AFTER: `docker ps -a --filter name=fd1585` empty, dangling images 0.
- **Checks** at `5b1464ec` (each via `run-heavy.sh --grant`, `…/checks.log`): `ruff check .` rc 0 ("All checks passed!"); `mypy` rc 0 ("no issues found in 251 source files"); `req-coverage.py` rc 0; `generate-contracts.py --check` rc 0 ("58 generated contracts match the models"); `ruff format --check backend/src/app/api/rate_tables.py` rc 1, **pre-existing**: origin/main's copy of the file reports the same rc 1, the `--diff` hunks lie at `:173`, `:246`, `:275` and later and none in this slice's lines, and CI runs no `ruff format` step (see the lead's 15:59 line above); not reformatted here.
- **Acceptance 9–13** at `5b1464ec`: 9 `git grep -n 'with spec_not_found():' 5b1464ec -- backend/src/app/api/rate_tables.py` → 6 lines (`:169`, `:174`, `:440`, `:462`, `:483`, `:539`); 10 `git grep -c '"RATE_TABLE_MISS"' 5b1464ec -- backend/tests/test_api_rate_tables.py` → `1`, and `git grep -n 'RATE_TABLE_MISS' … backend/src/app/platform/rate_tables.py` → the same six lines as at `7ed5c398` (`:305 :1004 :1106 :1139 :1167 :1557`); 11 the reds-day rows above (R1–R5 red by cause) and the greens here (R1–R5, C1–C4 green); 12 `git diff --name-only origin/main...5b1464ec` → `backend/src/app/api/rate_tables.py`, `backend/tests/test_api_rate_tables.py`, `docs/INDEX.md`, this LG; 13 `generate-contracts.py --check` rc 0 and `req-coverage.py` rc 0. 14 (the gate) is the lead's on gate-1b; 15 and 16 are the mint and merge.
- **Docs checks at the head before this commit** (`env -C <wt> python3 scripts/…` via `run-heavy.sh --light`): `doc-index.py --check` rc 0 (`OK (byte-stable)`); `audit-docs.py` rc 1, `FAILED (4)`, all on this slice's own working ids: `check 31` gap between 1955 and 8271; `check 32` at the LG's `:9` and `:74` (`SL-1956` does not resolve) and `:74` (the padded form of the ledger's own id, inside the reds-day line quoting the lint). The same command on tools-main `a9ffc22c` is rc 0, so the 849 other `  - ` lines it prints are baseline notes, not failures. All four clear at the mint.

- 2026-10-26 (exec-fd1585code, after the lead's 16:57:37 GMT pause order and the queue note): the lock-wait `rc=124` above is not a result. The greens and the full suite had already finished and the containers were already removed before those messages were read (uptime not quoted: the `fd1585c-*` containers were up about 1 h 5 min, from the 16:03 provisioning to the removal after the full suite).

head=5b1464ecab1bc3f7df2d1f3670b2b500973a0632; remaining: the gate (lead, gate-1b Tue 27 Oct 08:00 GMT), the mint (SL-1956 / LG-1957 ids), FD-1585 discharge lines, the PR.

### 2026-10-29 — Gate (gate-1b, SOLO) and the cover (exec-fd1585gate; grant "2026-10-29 10:17:01 GMT", cover "2026-10-29 10:55:25 GMT")

- **Gate** `head=d666a4051c036ae588a5c96dec4be88b8c5bdfb9` (tree `923c5642460691fdaab57a40a20d9d9cc14f0645`, main `a9ffc22c` already an ancestor, no merge), script `~/gi-pricing-plan.local/scratch/fd1585-gate/fd1585-gate.sh` (derived from `s1b-gate.sh` by substitution only), log `…/fd1585-gate/gate/gate.log`. START 2026-10-29T10:21:57+00:00, `END 2026-10-29T12:14:44+00:00 rc=1`.
- **rc files:** `audit_docs.rc` 1, `contracts.rc` 0, `import_linter.rc` 0, `mypy.rc` 0, `pytest.rc` 1, `req_coverage.rc` 0, `ruff.rc` 0. END rc parts: `python max=1 fe max=0 demo=0 restore rc_kc=0 role rc_role=0 skip rc_skip=0`.
- **Pytest summary (whole):** `13 failed, 6983 passed, 21 skipped, 5 xfailed, 146 warnings in 4731.29s (1:18:51)`; skipped 21 (<= 21).
- **FAILED, by file (all eight docs-audit files of common item 31):** `test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`; `test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `::test_the_committed_digest_currently_matches_the_committed_spec`; `test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`; `test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line`, `::test_phase1b_residue_count_matches_check_29s_own_count`; `test_register_owed.py::test_check_29_wiring_is_undisturbed`; `test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`, `::test_journey_citations_are_audited_in_ci`.
- **audit-docs `FAILED (5)`, only this slice's own working ids:** `check 31: gap in the full allocation between 1955 and 8271`; `check 32` at this LG's lines 9, 74, 88 (`SL-1956 does not resolve in docs/INDEX.md` ×3) and line 74 (`padded id LG-1957 outside a link target`).
- **Verdict (lead 29, item 31): STANDS pending mint** — conditions (mint, audit-docs rc 0, the eight files re-run on the minted head, CI) are not this seat's.
- **Frontend half:** install, generate:api, lint, type-check, test (`--maxWorkers=2`), build all rc 0; tree after gate 0 changed paths.
- **Demo (wf-699):** lock wait start 2026-10-29T11:46:49+00:00, acquired 11:46:49; quiet window `load1 < 2.0 after 350 s`; demo start 11:52:42 (load1 1.94); designed stop 12:13:53 (both lines seen); `--journey wf-699` rc 0; 1276 s; D7 ok.
- **Shared stack/cleanup:** restore from tools-main rc 0; keycloak bind source `/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local`; buckets `gip-test-blobs-gate-1b` and `gip-blobs-demo-gate-1b` removed rc 0; `dropdb gipricing_fd1585_gate` and `…_demo` rc 0; zeros: own-DB count 0, redis db 2 dbsize 0, db 4 dbsize 0 (re-read after END: 0, 0, `select count(*) from pg_database where datname like 'gipricing_fd1585%'` 0).
- **Cover (a), main moved twice** (#1380 `550d2c9b`, #1381 `20a36ca3ce1118501f3210693a75df1efb0ba4e5`): `git merge --no-ff origin/main` clean, merge commit `69853e0c536f5dc130dce4a63d97c72fcf19c54b` (tree `036a941a6ad08df1c999a17c8efeef9e16b2ef05`). `git diff --stat 923c5642460691fdaab57a40a20d9d9cc14f0645 HEAD^{tree}`: `frontend/package.json | 14`, `frontend/pnpm-lock.yaml | 648`, `uv.lock | 8` (+4/−4); 3 files changed, 361 insertions(+), 309 deletions(-) — exactly the three expected, nothing else.
- **Cover (b)** at `69853e0c536f5dc130dce4a63d97c72fcf19c54b`: `pnpm --dir …/frontend install --frozen-lockfile` rc 0 (vite 8.3.5); `uv sync --all-packages --frozen` rc 0 (opentelemetry-api 1.45.0 → 1.45.1); `uv run lint-imports` rc 0 (`Contracts: 4 kept, 0 broken.`). Fresh throwaway `fd1585d-{pg,redis,minio}` (`postgres:16-alpine`, `redis:7-alpine`, `minio/minio:latest`, 127.0.0.1 ephemeral ports, redis db 11, bucket `gip-test-blobs-fd1585d`), `alembic upgrade head` rc 0, `provision-app-role.py --allow-default-password` rc 0. Selection R1–R5 (`test_diff_404s_for_unknown_table_and_version`, `test_diff_seed_without_a_seed_origin_404s`, `test_import_preview_creates_nothing`, `test_import_confirm_cannot_override_the_verdict`, `test_diff_cells_404s_not_found_for_unknown_table_version_and_against`) + C1 + C2 + C3 (`test_rate_table_diff_portfolio.py`) + C4 (`test_worker_raise_sites.py`), log `~/gi-pricing-plan.local/scratch/fd1585-cover/greens.log`: `80 passed, 2 warnings in 78.20s (0:01:18)`, `rc=0`. Removal: `docker rm -fv` of the three rc 0; `docker ps -a --filter name=fd1585` before 3 names, after 0; dangling images 0; shared redis db 11/12/13 dbsize 0/0/0; `gipricing_fd1585%` databases 0. (c) is the PR's python CI, the lead's.

head=69853e0c536f5dc130dce4a63d97c72fcf19c54b at this section's parent; remaining: the audit, the mint (SL-1956 / LG-1957 ids), FD-1585 discharge lines, the PR.

### 2026-10-29 — Additions to the gate section (exec-fd1585gate, at the lead's request after the maintainer's 12:16:21 verification)

- **FAILED-set fingerprint.** `grep '^FAILED' ~/gi-pricing-plan.local/scratch/fd1585-gate/gate/pytest.log | sed 's/ - .*//' | sort -u | md5sum` → `3de106a917346a44197bdbaf5db31b82`, `sort -u | wc -l` = 13. Skipped cell: `| pytest skipped | 21 (<= 21) |`.
- **Two demo durations, two different clocks.** `demo.log` line 4854: `   journey done in 1125s` — demo.py's own timer for the WF-699 journey. `gate.log` line 58: `| demo seconds | 1276 |` — the gate script's `$((SECONDS - t0))` (script lines 136 and 158), t0 taken when the demo process was launched, read after the designed stop, so it also holds the server start-up, the frontend start and the stop; it is not the journey's duration. Designed stop, `gate.log` line 56: `| demo | designed stop at 2026-10-29T12:13:53+00:00 (both lines seen) |`; the two lines are `demo.log` 4854 (`journey done in 1125s`) and 4862 (`   served page: http://localhost:5173/ answered 200`). `gate.log` line 57: `| demo.py --journey wf-699 | rc=0 |`.
- **Quiet window and start.** `gate.log` lines 46–55: `| demo lock wait start | 2026-10-29T11:46:49+00:00 |`, `| demo lock acquired | 2026-10-29T11:46:49+00:00 |`, `| quiet window | load1 < 2.0 after 350 s |`, `| demo start load1 | 1.94 at 2026-10-29T11:52:42+00:00 |`.
- **Shared postgres and keycloak recreated at the demo start.** `demo.log` lines 5–12: `Container gi-pricing-postgres-1 Recreate`, `Container gi-pricing-keycloak-1 Recreate`, `… Recreated` (both), `… Starting` (both), `… Started` (both); minio and redis `Running`. The log lines carry no timestamp; the lead's reading of the recreate is 11:52:44Z and I have not verified it from a timestamped source.
