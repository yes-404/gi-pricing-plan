---
id: LG-8186
family: ledger
title: WK-1178 slice SL-8185 — FD-1852, a dataset-scoped grant reaches its three scoped writes (PL-8181) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: 40de35f5e74127c9ca6f21445c20088da5ba596b
phase: P2
work: WK-1178
slice: SL-8185
plans: [PL-8181]
corrected_by: []
relates: [PL-8181, SL-8185, FD-1852, FD-1853, RL-1849, SL-1736, FR-343, FR-345]
---

# LG-8186 — WK-1178 slice SL-8185: FD-1852, a dataset-scoped grant reaches its three scoped writes

Filed 2026-10-22 under working id 8186; executor seat `exec-8185`, branch `sl-8185-wk1178-fd8177-scoped-writes`, worktree `.claude/worktrees/sl-8185`, built from `origin/main` `71e481fa`. Every log path below is under `~/gi-pricing-plan.local/scratch/sl-8185/`. Times are BST unless a log line says otherwise.

**GO:** the maintainer's entry "2026-10-22 17:38:11 BST — Maintainer: PL 8181 (FD 8177 fix) DP-0..DP-3 RULED; GO (SL 8185 / LG 8186); my 17:36:24 FR-343 placement AMENDED to FR-345" (`to-lead.md`): "Tasks 1–6 as planned. Task 4 (rule-set) only after SL-1736 merges." Re-rated by "2026-10-22 17:46:43 BST — Maintainer: FD 8177 and FD 8184 RE-RATED MEDIUM (LATENT)": the slice continues as seated.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Plan: `PL-8181` (head `c6f93d5d` of `draft/pl-8181` when this ledger was opened), Tasks 1–6 and the Acceptance Standard. Requirements: `06` FR-345 (the dated order clause, DP-2), FR-343 (a one-line pointer), `01` FR-46 and FR-51 (the routes' own FRs, unchanged for a workspace-wide grant), `07` FR-452 (no `403` is counted, either kind).

### Task list

| # | Task | Commit | Result |
|---|---|---|---|
| 1 | Spec first: the FR-345 clause and the FR-343 pointer, plus the two sentences of the maintainer's 17:46:43 entry | `40015b55`, `9b6c21bd`, `f1454fc1` | `audit-docs` rc 0 "All checks passed"; `doc-index --check` rc 0 |
| 2 | 13 red tests for the three routes | `a5c49742` | 13 failed, 10 passed at base (below) |
| 3 | `requires(held_anywhere=True)`; dictionary and acknowledge; DP-3 | `5c77f030` | 19 passed, 4 failed (the 4 are Task 4's) |
| 4 | The rule-set route | **carried to SL 8192 / LG 8193** | blocked until SL-1736 merges; `validation_rules.py` untouched; ruled by the maintainer "2026-10-22 18:16:19 BST" (a): gate and merge SL-8185 without it |
| 5 | The permanent guard | `40de35f5` | red at base naming the 3 routes; 9 passed at head; 5 mutations red |
| 6 | GREEN by import closure | derivation only, see Build log | the slice's full code gate is the decisive green |

### Gate

The full two-half gate: **not yet run** (the lead's grant is owed; queue SL-1260, SL-1551, FD 8169, then this slice). Table empty.

Static checks at `40de35f5`: `ruff check` clean on the five changed `backend/src` files and the two new tests; `mypy` "Success: no issues found in 245 source files" (run once on the whole project at `5c77f030` while FD-1838's code gate was held: a heavy check beside a gate, disclosed here as a deviation; from then on static checks ran on changed files only). `ruff format --check` flags four of the five source files on code this slice did not touch (pre-existing on `origin/main`); the hunks this slice edits are formatted.

### Audit

Not yet written (the auditor's).

### Build log

**2026-10-22, Task 1** (`40015b55`, corrected `9b6c21bd`, `f1454fc1`). The FR-345 clause is `PL-8181`'s DP-2 wording; the FR-343 cell gained one separate appended dated sentence, no existing text edited (the maintainer's rule on the row both this slice and the RL 8176 batch touch). Two sentences from the 17:46:43 entry follow the clause: no Phase 2 API creates a scoped role assignment; `MODEL_FAMILY` and `RATING_ALGORITHM` are declared, not yet enforced (WK-676).

**2026-10-22, Task 2** (`a5c49742`). Own database `gipricing_sl-8185_215125e7`: `createdb -T gipricing` rc 0; `alembic upgrade head` rc 0 (`d4e81b7a2c95` to `a4d1f08c3b97`); `alembic current` `a4d1f08c3b97 (head)`. Red run, tree `f1454fc1` plus the new file, `GIP_GATE_SLOT` unset, `PUBSUB NUMSUB gip:switch` 0, load1 3.72, log `task2-red-base.log`: `13 failed, 10 passed, 1 warning in 20.57s`, rc=1. The 13 FAILED, each by its cause: `test_a_grant_scoped_to_one_dataset_reaches_that_datasets_write[dictionary|rule-set|acknowledge]` (`assert 403 == 200` / `201`, `PERMISSION_DENIED`); `test_the_same_grant_on_another_dataset_is_refused_by_the_handler_as_scope_denied[…]` ×3 and `test_the_scoped_refusal_is_a_scope_denied_and_is_not_counted[…]` ×3 (`assert 'PERMISSION_DENIED' == 'SCOPE_DENIED'`); `test_a_scoped_holder_asking_for_an_unknown_id_gets_not_found[…]` ×3 (`assert 403 == 404`); `test_acknowledge_by_an_actuary_scoped_to_another_dataset_is_scope_denied` (`assert 'ACKNOWLEDGE_FORBIDDEN_ROLE' == 'SCOPE_DENIED'`). Green at base: the workspace-wide holder ×3, no-grant with an unknown id ×3, the route gate's refusal not counted ×3, and the analyst keeping `ACKNOWLEDGE_FORBIDDEN_ROLE`.

**2026-10-22, Task 3** (`5c77f030`). Run on `a5c49742` plus the Task 3 working tree (committed unchanged as `5c77f030`), load1 4.69, log `task3-green.log`: `4 failed, 19 passed, 1 warning in 21.92s`, rc=1; the 4 FAILED are exactly the rule-set tests (in-scope, out-of-scope, scoped-unknown-id, count-scoped). Adjacent, log `task3-adjacent.log`: `test_api_authorisation_sweep.py`, `test_management_429_declared.py`, `test_api_acknowledge.py` rc=0, `15 passed, 1 warning in 23.38s`. The two sweep files have no diff.

**2026-10-22, Task 5** (`40de35f5`). Red at base: detached worktree `sl-8185-redbase` at `a5c49742`, the guard file with the rule-set gap row removed and the attribute read by name, log `task5-red-base.log`: `2 failed, 7 passed`, rc=1; the app-wide test names exactly `PUT /api/v1/datasets/{slug}/dictionary`, `PUT /api/v1/datasets/{slug}/rule-set` and `POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge`. The second failure is the injection test, `TypeError: requires() got an unexpected keyword argument 'held_anywhere'`, expected at base. At head, log `task5-head1.log`: `9 passed, 1 warning in 2.12s`. Mutations at head, log `task5-mutations.log`, each rc=1 and red by the intended test: M1 predicate 1 disabled (the predicate-1 injection test), M2 predicate 2 disabled (the predicate-2 injection and stale-gap tests), M3 resolver depth 0 (app-wide, negative control, injection and coverage tests), M4 a `ROUTE_SCOPES` row removed (the completeness test), M5 a fixed route listed as a gap (the stale-gap test). Counts: `ROUTE_SCOPES` 47 rows; `KNOWN_SCOPE_GAPS` 26 rows (1 owned by SL-8185 Task 4, 20 by RL-1849, 5 by FD-1853).

**2026-10-22, decisions with reasons (Tasks 3 and 5).**
- `requires(held_anywhere=True, management_counted=True)` raises **`TypeError`** at construction, as `PL-8181` DP-1 says (first built as `ValueError`; changed on the lead's note; test `test_held_anywhere_with_a_counted_gate_is_a_type_error`). `management_counted` now defaults to `None`, meaning "counted unless `held_anywhere`".
- Covered permissions are `DATASET_*` and `DEPLOYMENT_PROMOTE`. No Environment-scoped `admin:*` route exists (no `admin:*` check names a resource), so none is covered; the table's completeness rule extends when one is built.
- Every route holding a covered permission has a `ROUTE_SCOPES` row (the completeness test forces it), including the other `WriteDatasets` / `ReadDatasets` users: `POST /sources`, `POST /datasets`, `POST /sources/{source_id}/preview`, `GET /sources`, `GET /datasets` and `PATCH /datasets/{dataset_id}` are WORKSPACE (they name no Dataset; the owner change is decided by `admin:manage_roles`); the rule dry-run and submit routes and the rule list and create are WORKSPACE (a rule is not a Dataset); `POST /datasets/{slug}/versions` (ingest), `PATCH …/versions/{version}/schema`, `GET /datasets/{slug}`, the two version reads and the eleven `dataset_versions.py` routes act on one Dataset or Dataset Version and are DATASET gap rows owned by RL-1849 (as are `GET /validation-reports/{report_id}` and `GET /datasets/{slug}/rule-set`). `GET /blobs/{sha256}` is a DATASET gap (scoped through the owning Dataset Version, RL-1849); blob upload-url and complete are WORKSPACE (held under any scope, the scope check at ingest, RL-1849); the four reference-table reads are WORKSPACE (not a Dataset, outside FR-345, RL-1849). Five rows (`dislocation-runs` ×3, `rate-tables/…/diff` and `…/diff/cells`) are DATASET gap rows owned by FD-1853 (`03` §5.1 :1080/:1083 name `dataset:read` on the portfolio Dataset Version; the code passes no resource).
- `KNOWN_SCOPE_GAPS` has 26 rows: 1 owned by SL 8192 (rule-set), 20 by RL-1849, 5 by FD-1853. `ROUTE_SCOPES` has 47 rows.

**2026-10-22, Task 4 carried (the maintainer, "2026-10-22 18:16:19 BST", (a)).** The four rule-set tests of `test_dataset_scoped_writes.py` are `pytest.mark.xfail(strict=True)` with the reason "FD 8177 rule-set limb: owned by SL 8192 (SL 8185 Task 4 follow-on), activates when SL-1736 merges"; the rule-set `KNOWN_SCOPE_GAPS` row names owner SL 8192. Strict xfail means the fix makes them XPASS and fail the run, so the mark and the row leave together. Follow-on: **SL 8192 / LG 8193**, activation need SL-1736 merged. Re-run at `5c77f030` plus this change (tree `40de35f5` + the working tree; log `task4carry-rerun.log`, load1 4.52, `GIP_GATE_SLOT` unset, `NUMSUB gip:switch` 0): `test_dataset_scoped_writes.py` and `test_route_scope_guard.py`, rc=0, `29 passed, 4 xfailed, 1 warning in 23.70s`.

**2026-10-22, Task 6, the import-closure derivation (common brief item 29).** Command: `python3 ~/gi-pricing-plan.local/scratch/sl-8185/closure.py <worktree>`. It takes the changed modules from `git -C <wt> diff --name-only origin/main...HEAD -- backend/src` (`app.api.authz`, `app.api.datasets`, `app.api.validation`, `app.platform.datasets`, `app.platform.validation`), adds every `backend/src` module that imports one (level 1: 40 modules), and one more level of importers (level 2: **48 modules**, `app.main` among them), then lists every `backend/tests/test_*.py` importing any of the 48: **113 files** (`green-set.txt`, in `~/gi-pricing-plan.local/scratch/sl-8185/`). Because the closure reaches `app.main`, it is in effect the whole backend suite. The batches run through `run-small.sh`, three files each (the lead stopped the loop after batch 4, "stop the closure batches after the current one finishes"), at `5c77f030`/`8d7f1c5c`, summary lines verbatim from `green-summary.txt` and `green-batch-4.log`:
- batch 1, rc=0: `114 passed, 3 warnings in 67.73s (0:01:07)` (`test_api_acknowledge.py`, `test_api_approvals.py`, `test_api_audit.py`)
- batch 2, rc=0: `22 passed, 1 warning in 28.18s` (`test_api_auth.py`, `test_api_authorisation_sweep.py`, `test_api_blob_uploads.py`)
- batch 3, rc=0: `63 passed, 2 warnings in 51.02s` (`test_api_blobs.py`, `test_api_datasets.py`, `test_api_jobs.py`)
- batch 4, `94 passed, 21 warnings in 75.97s (0:01:15)`, no failures (`test_api_me.py`, `test_api_models.py`, `test_api_rate_tables.py`; this batch's summary line was lost when the loop was stopped, so its rc is read from the log, which ends with that line and no `failed`).
The remaining 101 files are covered by the slice's full code gate, the decisive green (the closure includes `app.main`).

**2026-10-22, DP-3 (b): a load 404 is counted (the maintainer, "2026-10-22 18:21:15 BST").** FR-452 exempts only 401 and 403, so the count-after-the-scoped-check pattern was wrong for a load 404. Red first (commit before the code): `test_a_not_found_after_the_route_gate_is_counted[dictionary|rule-set|acknowledge]` (limit 2: the 404 spends one, the first `/me` the second, the next `/me` is 429). Run at the test-only commit, log `dp3b-red.log`, load1 4.3, `GIP_GATE_SLOT` unset: rc=1, `2 failed, 19 passed, 5 xfailed, 1 warning in 25.16s`; FAILED `…[dictionary]` and `…[acknowledge]`, each `AssertionError: assert 200 == 429` (the 404 was not counted); the rule-set case is among the 5 xfailed. The change: `platform/datasets.update_dictionary` awaits `count_management` on the `NOT_FOUND` it catches from `load_dataset`, and `platform/validation.acknowledge` awaits it before the report 404; a 403 stays uncounted. Green, log `dp3b-green.log`, `test_dataset_scoped_writes.py` + `test_route_scope_guard.py` + `test_api_acknowledge.py`: rc=0, `35 passed, 5 xfailed, 1 warning in 29.05s`. `ruff check` clean and `mypy` on the two files "Success: no issues found in 2 source files".

**2026-10-22, housekeeping.** The scratch worktree `sl-8185-redbase` was removed after `docker inspect` of the four shared containers showed no bind source under it (postgres `/var/lib/docker/volumes/gi-pricing_pgdata/_data`, redis `/var/lib/docker/volumes/4ca9d2df…/_data`, minio `/var/lib/docker/volumes/gi-pricing_miniodata/_data`, keycloak `/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/fix-1838/deploy/keycloak-local`).

The small-run database `gipricing_sl-8185_215125e7` was dropped by the lead in the maintainer's disk clean-up of 2026-10-22 18:32 (0 connections first, rc 0). A later small run recreates it, so it is dropped again before the gate starts. Batch 4 of the closure run: its summary line was lost when the loop was stopped (94 passed by count, no failures seen).

## PRs

None yet.
