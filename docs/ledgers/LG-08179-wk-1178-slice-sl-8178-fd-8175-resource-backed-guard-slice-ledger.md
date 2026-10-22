---
id: LG-8179
family: ledger
title: WK-1178 slice SL-8178 — FD 8175 close vehicle, the RESOURCE_BACKED guard test (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
slice: SL-8178
plans: []
corrected_by: []
relates: [SL-8178, FD-8175, RL-8176]
---

# LG-8179 — WK-1178 slice SL-8178: FD 8175 close, the RESOURCE_BACKED guard

Working ids 8178 (SL) and 8179 (LG), unminted. Executed by `exec-8178`, base `origin/main` `71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5`, branch `fix/fd-8175-resource-backed-guard`.

**GO:** the maintainer's entry "2026-10-22 17:21:38 BST", item 2: "The guard 'RESOURCE_BACKED may hold only /environments/{env}/ paths': YES, as a test, red-first via an injected non-env path. It goes in the FD 8175 close vehicle, a WK-1178 delta row (test-only, small), NOT in SL-1260. If it fails on main today, STOP and report."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

FD 8175 (LOW) closes as accepted, citing `RL-8176` (Environment-scoped writes keep load-first). This slice adds the guard `RL-8176` obliges: `backend/tests/test_api_authorisation_sweep_scope.py`. **Owed, not on this branch:** FD 8175's own close (status closed-as-accepted citing RL 8176) happens in the docs batch, where FD 8175 and RL 8176 live.

### Task list

1. Guard test (`test_resource_backed_holds_only_environment_scoped_paths`): every key of `RESOURCE_BACKED` (imported from `test_api_authorisation_sweep.py`) has a path starting `/api/v1/environments/{env}/`; asserts the mapping is non-empty. DB-free, app-free.
2. Injection test (`test_the_resource_backed_guard_rejects_an_injected_non_environment_path`): a copy of `RESOURCE_BACKED` with `/api/v1/datasets/{dataset_id}/versions` and `/api/v1/environments-extra/{env}/deployments` (a near-miss prefix) added; the guard function `_outside_the_environment_scope` must return exactly those two keys.
3. Separate file, not the sweep file: `scripts/run-small.sh` takes whole files and the sweep file's other tests need the app and the database. Sweep file unchanged.
4. GREEN scope (item 29): changed modules `git diff --name-only origin/main...HEAD -- backend/src` is empty (test-only); the new file imports only `RESOURCE_BACKED` from the sweep test module, nothing imports the new file. GREEN = the new file; the gate's full suite is decisive.

### Gate

(left empty for the lead's gate)

### Audit

(not yet)

### Build log

- 2026-10-22, tree `71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5` plus the new untracked file, via `scripts/run-small.sh`, `GIP_GATE_SLOT` unset, no database used, logs in `~/gi-pricing-plan.local/scratch/fix-8175/`:
  - **On main's list (the STOP condition):** `2 passed, 2 warnings in 0.19s`, rc=0 (`main-run.log`). The three entries (`POST …/environments/{env}/deployments`, `…/deployment-requests`, `…/deployments/rollback`) all pass; no STOP.
  - **Red-first, form used: a deliberately weakened guard** (scratch, never committed): the `startswith` test replaced by `if False`. The injection test failed, `assert [] == [('POST', '/a…deployments')]`, `1 failed, 1 passed`, rc=1 (`weakened-run.log`). This proves the injection case bites the guard function; the real-list test passes either way, which is why the injection test exists. Restored by `cmp`.
  - **Green** after restore: `2 passed`, rc=0 (`green-run.log`); `ruff check` rc 0 and `ruff format --check` clean on the new file.
  - The 2 warnings are the per-worktree test-database teardown notice from `conftest_db.py`; no database exists or was used.

## PRs

(none yet)
