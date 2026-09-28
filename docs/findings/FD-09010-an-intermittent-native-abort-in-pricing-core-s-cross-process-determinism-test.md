---
id: FD-9010
family: finding
title: An intermittent native abort in pricing-core's cross-process determinism test
status: active
created: 2026-09-28
owner: auditor
tree: 2bff3c9f6fe6dbc64ad27db8f95b2ac95a8cbed2
corrected_by: []
relates: [WK-1178]
---

# FD-9010 — An intermittent native abort in pricing-core's cross-process determinism test

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the lead's
instruction, with the deputy's framing from his entry in the lead's local channel file
`to-lead.md`.

## Finding

`packages/pricing-core/tests/test_rating_score.py::test_scoring_is_deterministic_across_a_subprocess`
(NFR-495) starts a fresh interpreter, which compiles a bundle and scores it with `score_one`.
In one CI run, that child process **aborted natively**. It did not fail an assertion. The
change under test touched no code. The deputy's framing is that this **may be a production
scoring thread-safety defect**, not only a flaky test, because the aborting process is the real
scoring path.

## Evidence

- **The run.** It is #830's `python` workflow run `36436160310`, attempt 1, at `2bff3c9f`. The
  run's current conclusion reads `success` because a later attempt passed. Attempt 1's log
  (`gh run view 36436160310 --attempt 1 --log`) records:
  - `E       AssertionError: Fatal Python error: PyGILState_Release: thread state
    0x7ff240000f70 must be current when releasing`;
  - `E       assert -6 == 0`, where the child's `returncode` is -6 (SIGABRT);
  - the location `packages/pricing-core/tests/test_rating_score.py:576: AssertionError`,
    which is `assert proc.returncode == 0, proc.stderr`;
  - the summary `1 failed, 3464 passed, 3 skipped, 1 xfailed, 43 warnings in 644.34s`.
- **No code changed.** `git diff --name-only f7ee8829 2bff3c9f` lists 10 files under `docs/`
  and 2 under `.claude/`, and nothing else.
- **Frequency, the lead's measurement.** A grep for `PyGILState_Release` in the logs of the last
  40 failed `python` runs finds this one occurrence only. The auditor did not re-run that sweep.

## Disposition

**Deferred with an owner — the lead**, until triaged, under WK-1178. The event is the triage:
reproduce the abort under load with N repeats. It is on plan review 15's risk list (the deputy).
**If WK-672 Slice 2's N=5 gate run aborts this way, the triage moves ahead of Slice 2.**
