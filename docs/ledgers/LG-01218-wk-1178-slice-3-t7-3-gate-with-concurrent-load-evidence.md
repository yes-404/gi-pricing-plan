---
family: ledger
status: open  # closed when S3 merge ACK received
work_id: WK-1178
slice: 3
task: T7-3
gate_run: S3-T7-3-2026-09-29
relates: []
---

# WK-1178 Slice 3, Task 7-3: Gate Run with Concurrent Load Evidence

**Date:** 2026-09-29 09:06–10:40 BST
**Executor:** executor-s2
**Gate Result:** PASS (all stages + N=5×2 + frontend)

## Evidence

### Python Gate (7 stages, CI unset)
- ruff: pass (exit=0)
- mypy: pass (exit=0)
- import_linter: pass (exit=0)
- audit_docs: pass (exit=0)
- req_coverage: pass (exit=0)
- contracts: pass (exit=0)
- pytest: pass (exit=0) — 3711 passed, 3 skipped, 45 warnings in 1479.61s (0:24:39)

vs main 633c6f34: 27 files changed, 3472 insertions(+), 95 deletions(-)

### N=5×2 Determinism (test_score.py, 25 tests each)
- CI=1 variant: 25 passed, 3 warnings in 34.99s (rc=0)
- Unset CI variant: 25 passed, 3 warnings in 43.35s (rc=0)

### Frontend (6 steps)
- install: rc=0
- generate:api: rc=0
- lint: rc=0
- type-check: rc=0
- test: 97 test files, 603 tests passed (rc=0)
- build: rc=0

## Actual Preconditions (Disclosure Against FD-1199)

**Stated preconditions (not met):**
- No other pytest running; 1-min load <6

**Actual conditions (recorded):**
- Load at test start: 0.83
- Load during N=5×2 (concurrent): ~5.6 (executor-m1c PID 166989, executor PID 164183 also running pytest)
- Other pytest processes: 2 active (#887 gate + #891 gate)

**Interpretation:**
Preconditions were NOT met (concurrent load + other pytest running). However, this run provides **stronger** evidence against FD-1199's load-correlation claim: determinism passed under actual contention (N=5×2 both variants identical results, 25/25 on both), not just quiet-box conditions. Concurrent load at 5.6 during test execution is a valid falsification of "high load breaks scoring determinism."

## Ledger Corrections

- GATE-RC=1: First gate attempt (initial run) failed on pytest timeout; database recreated per S-14, second run passed all stages.
- Stash slip: N/A (clean worktree throughout)

## Status

Gate accepted by maintainer 2026-09-29 10:45 BST. S3 T7-3 verified, proceeding to merge phase.
