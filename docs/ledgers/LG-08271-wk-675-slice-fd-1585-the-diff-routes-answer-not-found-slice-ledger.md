---
id: LG-8271
family: ledger
title: WK-675 slice FD-1585 — the diff routes answer NOT_FOUND (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-26
owner: executor
tree: 7ed5c398333aa24432bd9917bd204f7b540fb39c   # origin/main at the branch cut (#1401)
slice: SL-8270
phase: P2
work: WK-675
plans: [PL-1546]
corrected_by: []
relates: [FD-1585, PL-1546, FR-231, FR-232]
---

# LG-8271 — WK-675 slice FD-1585: the diff routes answer NOT_FOUND

Working ids SL 8270 (slice) and LG 8271 (ledger), reserved by the lead. Plan: `PL-1546` delta row 9
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

`doc-index.py --root docs --check`: `docs/INDEX.md: OK (byte-stable)`, rc 0 (regenerated first). `audit-docs.py` via `run-heavy.sh --light`: rc 1, only the two lints on this slice's own working ids: `check 31: gap in the full allocation between 1955 and 8271` and `check 32: …LG-08271…:9: SL-8270 does not resolve in docs/INDEX.md`. Both clear at the mint (the ids are working ids until then).

- 2026-10-26 15:59 GMT (lead): `ruff format --check backend/tests/test_api_rate_tables.py` reports "1 file would be reformatted" on this branch, and the SAME on origin/main's copy (tools-main @a9ffc22c). The drift is pre-existing at main, not this slice's; `.github/workflows/python.yml` runs no `ruff format` step. No reformat in this slice (to-lead "2026-10-26 15:58:34 GMT").
