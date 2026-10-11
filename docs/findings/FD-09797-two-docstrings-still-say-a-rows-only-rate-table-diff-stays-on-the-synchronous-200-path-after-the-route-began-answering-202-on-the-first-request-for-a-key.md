---
id: FD-9797
family: finding
title: Two docstrings still say a rows-only rate-table diff stays on the synchronous 200 path, after the route began answering 202 on the first request for a key
status: active
created: 2026-10-11
owner: auditor
tree: 4af5997e14861bafda4685730180233db54dc243
corrected_by: []
relates: [WK-675, SL-1503, SL-1391, RL-1418, RL-1442, FR-232]
---

# FD-9797 — a docstring that describes the route before SL-1391

Found by SL-1503's gate classification. Filed from the lead's entries "2026-10-11 21:13:13 BST — SL-1503 gate @07830ca6 CLASSIFIED (executor) …" (`from-lead-2026-10-09.md`, a local channel file, cited by its header) and "2026-10-11 21:13:52 BST — SL-1503 Acc 10: a DISCLOSED DEVIATION in LG 9978 is sufficient (no RL) … FD 9797 (LOW, WK-675, D13) noted" (`to-lead.md`, local). Every line below was re-read at `origin/main` `4af5997e14861bafda4685730180233db54dc243` on 2026-10-11.

## Evidence

- `backend/src/app/platform/rate_tables.py:419-420` (`diff_needs_job`, `:408`): "Either version `storage: parquet` routes the request to a `rate_table.diff` Job; a rows-only pair stays on the synchronous 200 path."
- `backend/tests/test_rate_tables_service.py:491-492` (`test_diff_needs_job_flags_a_diff_touching_parquet`, `:488`): "the diff answers 202 with a Job where either version is `storage: parquet`; a rows-only pair stays on the synchronous 200 path."
- What the route does instead. `backend/src/app/api/rate_tables.py:398-401`: "**200** with the diff summary (FR-231) read from the stored artifact; **202** with a `rate_table.diff_cells` Job where this query's artifact is not yet stored, for either storage (FR-232, R1: an operation that can exceed 2 s returns 202)". The route calls `service.diff_from_artifact` (`api/rate_tables.py:422`) and branches on `DiffCellsJobNeeded` (`:426`). `backend/src/app/platform/rate_tables.py:761` (`diff_from_artifact`): "the first request for a key is the Job (rows pairs too), later ones are 200". The change is SL-1391, ruled in RL-1418 and amended by RL-1442, after the two docstrings were written.
- The consequence in a test: SL-1503's `test_wf699_e1` cross-check asserted `table_diff.status_code == 200` for a rows pair and was red; the lead's entry gives its cause as the route now answering 202 on the first request for a key.
- A third occurrence of the same stale claim, found by the author of this essay: `backend/src/app/platform/rate_tables.py:472`, in the docstring of `diff` (`:446`): "storage decides whether the API answers 200 or 202 with a Job (`diff_needs_job`)". `git grep -n diff_needs_job -- backend packages frontend/src docs/specs` at this tree prints the definition (`rate_tables.py:408`), that docstring mention (`:472`) and the test (`test_rate_tables_service.py:488`, `:524`, `:528`, `:532`); the route does not call it.

## Finding

**Severity LOW (the lead's, entry 21:13:52).** Behaviour is correct and the route's own docstring is right; only two docstrings (a third by the author's reading) describe a path that no longer exists, and `diff_needs_job` itself has no production caller at this tree, so its test asserts a contract nothing serves. A reader trusting the docstring writes a test that fails, as SL-1503's did.

## Disposition

**Owner: WK-675 (rate tables).** Decision: `fix before close with an owner: WK-675` or accept at the P2 close. The fix is a docstring correction at the three sites and a decision on `diff_needs_job` (delete it with its test, or keep it and say what calls it); that second choice is the owner's. Event that next confirms or discharges it: a merged slice whose diff leaves no occurrence of "stays on the synchronous 200 path" in `backend/`. Rides D13. Filed by the executor from the lead's entries, 2026-10-11; the lead gives the verdict.
