---
id: LG-8186
family: ledger
title: WK-1178 slice SL-8185 — FD 8177, a dataset-scoped grant reaches its three scoped writes (PL-8181) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: 40de35f5e74127c9ca6f21445c20088da5ba596b
phase: P2
work: WK-1178
slice: SL-8185
plans: [PL-8181]
corrected_by: []
relates: [PL-8181, SL-8185, FD-8177, FD-8184, RL-8182, SL-1736, FR-343, FR-345]
---

# LG-8186 — WK-1178 slice SL-8185: FD 8177, a dataset-scoped grant reaches its three scoped writes

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
| 4 | The rule-set route | **OWED** | blocked until SL-1736 merges; `validation_rules.py` untouched |
| 5 | The permanent guard | `40de35f5` | red at base naming the 3 routes; 9 passed at head; 5 mutations red |
| 6 | GREEN by import closure | see Gate | |

### Gate

The full two-half gate: **not yet run** (the lead's grant is owed). Table empty.

Static checks at `40de35f5`: `ruff check` clean on the five changed `backend/src` files and the two new tests; `mypy` "Success: no issues found in 245 source files". `ruff format --check` flags four of the five source files on code this slice did not touch (pre-existing on `origin/main`); the hunks this slice edits are formatted.

### Audit

Not yet written (the auditor's).

### Build log

**2026-10-22, Task 1** (`40015b55`, corrected `9b6c21bd`, `f1454fc1`). The FR-345 clause is `PL-8181`'s DP-2 wording; the FR-343 cell gained one separate appended dated sentence, no existing text edited (the maintainer's rule on the row both this slice and the RL 8176 batch touch). Two sentences from the 17:46:43 entry follow the clause: no Phase 2 API creates a scoped role assignment; `MODEL_FAMILY` and `RATING_ALGORITHM` are declared, not yet enforced (WK-676).

**2026-10-22, Task 2** (`a5c49742`). Own database `gipricing_sl-8185_215125e7`: `createdb -T gipricing` rc 0; `alembic upgrade head` rc 0 (`d4e81b7a2c95` to `a4d1f08c3b97`); `alembic current` `a4d1f08c3b97 (head)`. Red run, tree `f1454fc1` plus the new file, `GIP_GATE_SLOT` unset, `PUBSUB NUMSUB gip:switch` 0, load1 3.72, log `task2-red-base.log`: `13 failed, 10 passed, 1 warning in 20.57s`, rc=1. The 13 FAILED, each by its cause: `test_a_grant_scoped_to_one_dataset_reaches_that_datasets_write[dictionary|rule-set|acknowledge]` (`assert 403 == 200` / `201`, `PERMISSION_DENIED`); `test_the_same_grant_on_another_dataset_is_refused_by_the_handler_as_scope_denied[…]` ×3 and `test_the_scoped_refusal_is_a_scope_denied_and_is_not_counted[…]` ×3 (`assert 'PERMISSION_DENIED' == 'SCOPE_DENIED'`); `test_a_scoped_holder_asking_for_an_unknown_id_gets_not_found[…]` ×3 (`assert 403 == 404`); `test_acknowledge_by_an_actuary_scoped_to_another_dataset_is_scope_denied` (`assert 'ACKNOWLEDGE_FORBIDDEN_ROLE' == 'SCOPE_DENIED'`). Green at base: the workspace-wide holder ×3, no-grant with an unknown id ×3, the route gate's refusal not counted ×3, and the analyst keeping `ACKNOWLEDGE_FORBIDDEN_ROLE`.

**2026-10-22, Task 3** (`5c77f030`). Run on `a5c49742` plus the Task 3 working tree (committed unchanged as `5c77f030`), load1 4.69, log `task3-green.log`: `4 failed, 19 passed, 1 warning in 21.92s`, rc=1; the 4 FAILED are exactly the rule-set tests (in-scope, out-of-scope, scoped-unknown-id, count-scoped). Adjacent, log `task3-adjacent.log`: `test_api_authorisation_sweep.py`, `test_management_429_declared.py`, `test_api_acknowledge.py` rc=0, `15 passed, 1 warning in 23.38s`. The two sweep files have no diff.

**2026-10-22, Task 5** (`40de35f5`). Red at base: detached worktree `sl-8185-redbase` at `a5c49742`, the guard file with the rule-set gap row removed and the attribute read by name, log `task5-red-base.log`: `2 failed, 7 passed`, rc=1; the app-wide test names exactly `PUT /api/v1/datasets/{slug}/dictionary`, `PUT /api/v1/datasets/{slug}/rule-set` and `POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge`. The second failure is the injection test, `TypeError: requires() got an unexpected keyword argument 'held_anywhere'`, expected at base. At head, log `task5-head1.log`: `9 passed, 1 warning in 2.12s`. Mutations at head, log `task5-mutations.log`, each rc=1 and red by the intended test: M1 predicate 1 disabled (the predicate-1 injection test), M2 predicate 2 disabled (the predicate-2 injection and stale-gap tests), M3 resolver depth 0 (app-wide, negative control, injection and coverage tests), M4 a `ROUTE_SCOPES` row removed (the completeness test), M5 a fixed route listed as a gap (the stale-gap test). Counts: `ROUTE_SCOPES` 47 rows; `KNOWN_SCOPE_GAPS` 26 rows (1 owned by SL-8185 Task 4, 20 by RL-8182, 5 by FD-8184).

## PRs

None yet.
