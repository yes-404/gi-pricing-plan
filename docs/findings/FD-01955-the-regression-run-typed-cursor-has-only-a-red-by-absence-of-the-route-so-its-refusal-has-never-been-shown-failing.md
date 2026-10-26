---
id: FD-1955
family: finding
title: The regression-run typed cursor has only a red by absence of the route, so its refusal has never been shown failing
status: active
created: 2026-10-26   # drafted 2026-10-26 under working id 8264
owner: auditor
tree: 1e0a8abbc90723ae9c887a901f700b72f6f94cc1
corrected_by: []
relates: [WK-675, CR-1952, SL-1553, LG-1933]
---

# FD-1955 — The regression-run typed cursor has only a red by absence of the route, so its refusal has never been shown failing

## Finding

**MEDIUM (to-lead "2026-10-26 11:04:42 GMT"); owner WK-675, through the lane-C docs PR of Tue 27 Oct 2026.** A §13 defect ("enforcement is proven on deliberately broken input"): the check's test may be unable to fail. No product code is shown wrong. Authority: to-lead "2026-10-26 10:54:44 GMT". Filed under working id FD-1955, from CR-1952 §3.

The typed cursor of the regression-run list (SL-1553) is red-first at backend `892a2f74` with `4 failed, 1 passed, 13 deselected`, because "the four list tests answer 405" (LG-1933:114). The route was absent. That red is by absence of the route, not by the cursor check.

## Evidence

- `backend/tests/test_regression_runs.py:607` `test_a_cursor_that_is_not_a_run_of_this_version_is_a_400` has never been shown failing with the route present and the cursor check broken.
- Model-schema `c07ad757`: "1 failed, 26 passed" (ImportError, by absence). Frontend `bb564bdb` plus the uncommitted test, committed `da819fde`: `Tests 1 failed | 15 passed (16)`. The truncated branch of `listRegressionRuns` (`REGRESSION_RUN_PAGE_CAP`, `api/regressionRuns.ts:16`) has no test.
- All three reds reach `e6f8292c` (CR-1952 §3).

## Severity

MEDIUM, by the register's usage and the precedent of FD-1945: a check that has not been shown to fail can read green over a broken cursor, a false green letting a wrong merge through.

## Remedy

CR-1952 §5e owed row (1): re-run the proof on genuinely broken input in the Tue 27 Oct 2026 docs PR's run: break the `(finished_at, id)` check or the version filter at `platform/regression_runs.py`, show `:607` red, restore. It needs a DB window, which is the lead's to grant. Add a test for the truncated branch if the run shows it unproven.

## Disposition

Open, owner WK-675; **fix before close**, by Tue 27 Oct 2026. Filed under working id FD-1955.

## Re-proof on broken input, 2026-10-26

Run 2026-10-26 (16:3x UTC) by exec-tue27a under the lead's grant `to-lead.md` "2026-10-26 16:00:41 GMT", on the executor branch `docs/tue27-lanec-exec` at head `e6e7f7eda536a0d505de23c91dc34766f4f7f563`, tree `0c9acf57ace372f364530e253280243fc65f3715`. The target is `backend/tests/test_regression_runs.py` (18 tests). The mutations were scratch edits, each asserted to apply exactly once, never committed. The date is the day the runs happened; the register row's "Tue 27 Oct" deadline is not moved by it.

**The instrument.** A throwaway `postgres:16-alpine` container `t27b-pg` (127.0.0.1, ephemeral port 32831, anonymous volume), and `redis:7-alpine` `t27b-redis` (port 32832, db 12). The login role `gip_app_login` was provisioned by `scripts/provision-app-role.py --allow-default-password` (rc 0). Alembic upgraded to head `b7e4c2a91d36` (rc 0). Each log's first line is `head=<sha>` and its last line is `rc=<n>`; the logs are local (`scratch/t27b/`, not in the repository).

| Run | Edit | Summary line | rc | Failing assertion |
|---|---|---|---|---|
| R0 control | none | `18 passed, 1 warning in 19.18s` | 0 | none |
| M1 | `regression_runs.py:112`: `select(RegressionRunRow).where(*scope, RegressionRunRow.id == after)` → `select(RegressionRunRow).where(RegressionRunRow.id == after)` (the version and workspace scope dropped from the cursor anchor lookup) | `1 failed, 17 passed, 1 warning in 17.01s` | 1 | `FAILED backend/tests/test_regression_runs.py::test_a_cursor_that_is_not_a_run_of_this_version_is_a_400`, at `test_regression_runs.py:616`: `assert 200 == 400` (`where 200 = <Response [200 OK]>.status_code`) |
| M2 | `regression_runs.py:124-129`: the row-value `tuple_(finished_at, id) < tuple_(…)` → `finished_at < literal(anchor.finished_at, …)` (the id tie-break dropped) | `1 failed, 17 passed, 1 warning in 17.70s` | 1 | `FAILED backend/tests/test_regression_runs.py::test_equal_finished_at_orders_by_id_descending_and_paging_returns_each_run_once`, at `test_regression_runs.py:603`: `assert [...] == [...]`, "At index 1 diff", "Right contains 2 more items" (the equal-`finished_at` runs are skipped on the second page) |
| R1 restore | `git -C <wt> checkout -- backend/src/app/platform/regression_runs.py` | `18 passed, 1 warning in 17.06s` | 0 | none |

`git diff --quiet -- backend/src/app/platform/regression_runs.py` printed rc 0 after the restore, and `git status --short` was empty. So the typed cursor's 400 is held by the scope filter at `:112` (M1 turns it into a 200), and the `(finished_at, id)` resume by the tie-break (M2 loses runs).

**Cleanup.** `docker rm -fv t27b-pg t27b-redis`; `docker ps -a -q | wc -l` was 9 before and 9 after; dangling volumes 17 before and 17 after; `docker ps -a` names containing `t27b`: 0; redis db 12 `dbsize` 0 after `flushdb`; the shared `gi-pricing-postgres-1` holds 0 databases named `t27b%`. The frontend branch of `REGRESSION_RUN_PAGE_CAP` (`api/regressionRuns.ts:16`) is not shown by a backend run either way; DP-T27-6 carries it under CR-1952 §5.
