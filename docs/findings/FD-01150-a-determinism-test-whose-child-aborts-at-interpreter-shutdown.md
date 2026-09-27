---
id: FD-1150
family: finding
title: A determinism test whose child aborts at interpreter shutdown
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [PL-1144]
---

# FD-1150 — A determinism test whose child aborts at interpreter shutdown

Filed by the auditor at 2026-09-27 14:24:50 BST, as part of the first commit of PL-1144's docs PR
(PL-1144 Task 11 step 0). This is face 16 of PL-1144 Scope B. The title is the deputy's
wording of 2026-09-27 11:21:57 BST. The face label is PL-1144's own and is **not** a
register finding id: the register's row of that number is a different, older finding.

## Finding

`packages/pricing-core/tests/test_rating_score.py::test_scoring_is_deterministic_across_a_subprocess`
spawns a child `python -c` interpreter, which imports scikit-learn under `asyncio`, and
it asserts `proc.returncode == 0`. On one CI run the child aborted at interpreter
teardown with SIGABRT (return code −6). So the test failed on a docs-only change, before
any premium or hash was compared. The deputy's ruling gives the ground for filing: *"a
test that can abort on teardown is a defect of the test's shape regardless of
frequency"*. This is a defect in the test, not in the scoring path.

## Evidence

Read by the auditor with `gh api` at the time of filing:

- **Run `36311605268`, attempt 1:** conclusion `failure`, head
  `0cbdbf4e7ae7a557e8943f5ab56f024f69976b90` (#819). Job `108598494214`'s log shows
  `E       AssertionError: Fatal Python error: PyGILState_Release: thread state 0x7f01dc000f70 must be current when releasing`,
  `where -6 = CompletedProcess(args=[…/.venv/bin/python', '-c', "import asyncio, js…`, and
  the summary line `1 failed, 3457 passed, 3 skipped, 1 xfailed, 43 warnings in 618.21s (0:10:18)`.
- **Run `36311605268`, attempt 2:** conclusion `success`, at the same head, with no commit
  between the attempts.
- **The change was docs-only.** #819 changes three docs paths, so its code tree equals
  `271088b0`'s. The same test passed on `main`'s python run `36310860551` at that tree
  (the deputy's ruling, 2026-09-27 11:21:57 BST, and PL-1144 Scope B face 16).

The deputy's diagnosis is *"an interpreter-teardown race in a native extension (the child
imports sklearn under asyncio)"*. This record gives that diagnosis as the deputy's. The
auditor did not reproduce the abort locally.

## Disposition

**Deferred with an owner — the lead**, as the deputy ruled at 2026-09-27 11:21:57 BST:
*"an `FD-` register row **deferred with the lead as owner**, event: the create-read-retire
audit's first slice (or earlier if it recurs today, when it becomes a named item). It is
outside PL-1144's scope; no executor is spawned on it under S-8."* PL-1144 Scope B face 16
gives the event in the same terms: *"Event: the first slice of the create-read-retire
audit, or a named item if the failure recurs on 2026-09-27."* A likely fix shape, not
chosen here: the child exits without interpreter finalisation after it has written its
result, or the test checks the result the child emitted and not a clean teardown. Both
remove the test's dependence on the native extension's shutdown order.
