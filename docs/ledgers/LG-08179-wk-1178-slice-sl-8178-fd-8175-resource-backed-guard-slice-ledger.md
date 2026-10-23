---
id: LG-8179
family: ledger
title: WK-1178 slice SL-8178 — FD-1851 close vehicle, the RESOURCE_BACKED guard test (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
slice: SL-8178
plans: []
corrected_by: []
relates: [SL-8178, FD-1851, RL-1848]
---

# LG-8179 — WK-1178 slice SL-8178: FD-1851 close, the RESOURCE_BACKED guard

Working ids 8178 (SL) and 8179 (LG), unminted. Executed by `exec-8178`, base `origin/main` `71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5`, branch `fix/fd-8175-resource-backed-guard`.

**GO:** the maintainer's entry "2026-10-22 17:21:38 BST", item 2: "The guard 'RESOURCE_BACKED may hold only /environments/{env}/ paths': YES, as a test, red-first via an injected non-env path. It goes in the FD-1851 close vehicle, a WK-1178 delta row (test-only, small), NOT in SL-1260. If it fails on main today, STOP and report."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

FD-1851 (LOW) closes as accepted, citing `RL-1848` (Environment-scoped writes keep load-first). This slice adds the guard `RL-1848` obliges: `backend/tests/test_api_authorisation_sweep_scope.py`. **Owed, not on this branch:** FD-1851's own close (status closed-as-accepted citing RL-1848) happens in the docs batch, where FD-1851 and RL-1848 live.

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
- 2026-10-22, after merging `origin/main` `75f5f401` (merge-tree rc 0, clean) and re-pointing `FD 8175`→`FD-1851`, `RL 8176`→`RL-1848` (`git grep -nE '8175|8176'` before: 3 test-file hits, ledger, roadmap; after: only the branch name, a commit hash and the unminted SL/LG ids remain), via `scripts/run-small.sh`, no database: `2 passed, 2 warnings in 0.08s`, rc=0, run on the committed head `3661a20302dbf5870578cb43a9e25892fc363632` (superseded by the next line) (`~/gi-pricing-plan.local/scratch/fix-8175/rerun-3661a203-run.log`, first line the sha). Superseded earlier run on an uncommitted tree (`rerun-merged-run.log`, `0.36s`, rc=0). The red and green runs above stand; the weakened-guard mutation was made in the then-untracked guard file (copy `guard.bak`) and restored by `cmp`.
- 2026-10-22, after merging `origin/main` `6753c495` (merge-tree rc 1, `docs/INDEX.md` only; main's taken and regenerated, `doc-index --check` rc 0), via `scripts/run-small.sh`, no database, on the committed head `9d279c167e6bd874f3fda408ab70f8ec7a0e3c74`: `2 passed, 2 warnings in 0.09s`, rc=0 (`~/gi-pricing-plan.local/scratch/fix-8175/rerun-9d279c16-run.log`, first line the sha). audit-docs: check 31 only (gap between 1855 and 8178, the slice's own ids).
- 2026-10-23, after merging `origin/main` `4e399fd0` (merge-tree rc 1, `docs/INDEX.md` only; main's taken and regenerated, `doc-index --check` rc 0; `docs/roadmap.md` auto-merged with no conflict), committed head `8435ab45e3af7802d4a3ef4af3ff1987fa047a32`. Import closure (item 29): `git diff --name-only origin/main...HEAD -- backend/src packages` is empty (the slice changes one test file, `backend/tests/test_api_authorisation_sweep_scope.py`); its only project import is `RESOURCE_BACKED` from `backend/tests/test_api_authorisation_sweep.py`, which main changed (`git grep -lE "test_api_authorisation_sweep\b" -- backend packages` names only the guard file and a docstring mention in `test_management_429_declared.py`, not an importer). `test_api_authorisation_sweep.py`'s own tests use the `membership` and `database` fixtures (`conftest_db.py`), so they are DB-backed and wait for the slice gate (item 32); the guard file is the DB-free GREEN set. Via `scripts/run-small.sh` with `GIP_REDIS_URL=redis://localhost:6379/12` (load1 3.38 at start, redis db 12 dbsize 0 afterwards): `2 passed, 2 warnings in 0.34s`, rc=0 (`~/gi-pricing-plan.local/scratch/fix-8175/rerun-8435ab45-run.log`, first line the sha). audit-docs (gate-2 flock, `scratch/fix-8175/audit-0935.log`): `FAILED (1)`: `check 31: gap in the full allocation between 1859 and 8178`, the slice's own ids only. Gate scripts re-derived (`scratch/fix-8175/fd8175-gate-g1.sh` for gate-1, `fd8175-gate-1b.sh` for gate-1b), not launched.

## PRs

(none yet)

## Corrections and strict red run (exec-8178r, 2026-10-23 11:58 BST, appended; earlier lines unchanged)

Per RS 8214 (`aud-8178-2026-10-23` @8cae3a0f) lines B1–B4, adopted by the lead, and the strict reading of the maintainer's "2026-10-22 17:21:38 BST" item 2.

- **B1.** The GO line's quotation above reads "It goes in the FD-1851 close vehicle", a re-point made inside quotation marks. The verbatim form is "It goes in the FD 8175 close vehicle" [FD 8175 = FD-1851 at the mint].
- **B2.** "FD-1851's own close is owed" is stale: FD-1851 is `status: retired` on main (`docs/findings/FD-01851-environment-scoped-writes-order-404-before-403-inconsistently-the-existence-oracle-is-accepted-within-a-workspace.md`, front matter, `git show origin/main:` at `4e399fd0`+).
- **B3.** The "2 warnings" are two different things, not both teardown notices. From `strict-red-8178r.log`: (1) `StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.` (`fastapi/testclient.py:1`, raised by importing the sweep module); (2) `UserWarning: could not empty the test database (RuntimeError: GIP_TEST_DATABASE_URL is not set, and the per-worktree test database … does not exist yet. …)` (`conftest_db.py:437`, the teardown notice).
- **B4.** "The three entries" was the count at the slice's base. `RESOURCE_BACKED` on main (`origin/main:backend/tests/test_api_authorisation_sweep.py`) has five, all under `/api/v1/environments/{env}/`: `POST …/deployments`, `POST …/deployment-requests`, `POST …/deployments/rollback`, `PUT …/routing`, `PUT …/shadow`. The guard passes on all five.
- **Strict red (scratch, never committed).** On head `1d06b46b497bec8fd9c9a052b3f39ca82433ddeb`, one non-environment key was injected into the REAL mapping (`("POST", "/api/v1/datasets/{dataset_id}/versions"): ({"dataset_id": "x"}, {})` as the first entry of `RESOURCE_BACKED` in `backend/tests/test_api_authorisation_sweep.py`; diff pasted in the log). `scripts/run-small.sh` on `backend/tests/test_api_authorisation_sweep_scope.py` alone, `GIP_REDIS_URL=redis://localhost:6379/11` (load1 3.74 at start; db 11 dbsize 0 after), DB-free: rc=1, `FAILED backend/tests/test_api_authorisation_sweep_scope.py::test_resource_backed_holds_only_environment_scoped_paths`, `1 failed, 1 passed, 2 warnings in 0.86s`; the assert line: `AssertionError: assert [('POST', '/a...d}/versions')] == []`. Log: `~/gi-pricing-plan.local/scratch/fix-8175/strict-red-8178r.log` (first line the sha). Restored with `git checkout -- backend/tests/test_api_authorisation_sweep.py`; restored, `git status --short` empty (porcelain 0).
