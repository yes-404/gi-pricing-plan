---
id: FD-8264
family: finding
title: The regression-run typed cursor has only a red by absence of the route, so its refusal has never been shown failing
status: active
created: 2026-10-26   # drafted 2026-10-26 under working id 8264
owner: auditor
tree: 1e0a8abbc90723ae9c887a901f700b72f6f94cc1
corrected_by: []
relates: [WK-675, CR-8261, SL-1553, LG-1933]
---

# FD-8264 — The regression-run typed cursor has only a red by absence of the route, so its refusal has never been shown failing

## Finding

**MEDIUM (proposed; the lead decides); owner the lead, through the lane-C docs PR of Tue 27 Oct 2026.** A §13 defect ("enforcement is proven on deliberately broken input"): the check's test may be unable to fail. No product code is shown wrong. Authority: to-lead "2026-10-26 10:54:44 GMT". Filed under working id FD 8264, from CR 8261 §3.

The typed cursor of the regression-run list (SL-1553) is red-first at backend `892a2f74` with `4 failed, 1 passed, 13 deselected`, because "the four list tests answer 405" (LG-1933:114). The route was absent. That red is by absence of the route, not by the cursor check.

## Evidence

- `backend/tests/test_regression_runs.py:607` `test_a_cursor_that_is_not_a_run_of_this_version_is_a_400` has never been shown failing with the route present and the cursor check broken.
- Model-schema `c07ad757`: "1 failed, 26 passed" (ImportError, by absence). Frontend `bb564bdb` plus the uncommitted test, committed `da819fde`: `Tests 1 failed | 15 passed (16)`. The truncated branch of `listRegressionRuns` (`REGRESSION_RUN_PAGE_CAP`, `api/regressionRuns.ts:16`) has no test.
- All three reds reach `e6f8292c` (CR 8261 §3).

## Severity

MEDIUM, by the register's usage and the precedent of FD-1945: a check that has not been shown to fail can read green over a broken cursor, a false green letting a wrong merge through.

## Remedy

CR 8261 §5e owed row (1): re-run the proof on genuinely broken input in the Tue 27 Oct 2026 docs PR's run: break the `(finished_at, id)` check or the version filter at `platform/regression_runs.py`, show `:607` red, restore. It needs a DB window, which is the lead's to grant. Add a test for the truncated branch if the run shows it unproven.

## Disposition

Open, owner the lead; **fix before close**, by Tue 27 Oct 2026. Filed under working id FD 8264.
