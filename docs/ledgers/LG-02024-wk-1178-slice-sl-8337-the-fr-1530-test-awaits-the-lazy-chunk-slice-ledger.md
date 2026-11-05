---
id: LG-2024
family: ledger
title: WK-1178 slice SL-2023 — the FR-1530 test awaits the lazy chunk (FD-1748, FD-1800)
status: active
created: 2026-11-05
owner: executor
tree: c218fc5a07f49d03a8fc5ef74e61c78926710c5e
phase: P2
work: WK-1178
slice: SL-2023
plans: [PL-2022]
corrected_by: []
relates: [FD-1748, FD-1800, FR-1530]
---

# LG-2024 — the FR-1530 test awaits the lazy chunk

**GO:** to-lead "2026-11-05 10:36:35 GMT" (DP-F1 keep `findBy` after the chunk await; DP-F2 the 20 runs granted when F asks, never beside a timed gate stage).
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

PL-2022, SL-2023: add `await import("@/components/dag/DagDesigner.vue")` to the `beforeAll` of `frontend/src/views/__tests__/RatingDesignView.test.ts`. Requirement: FR-1530 (no spec change). Findings: FD-1748, FD-1800.

### Task list

- R1 red (injected, not committed), base c218fc5a, vitest single file, load1 4.74: `Test Files  1 failed (1)`, `Tests  1 failed | 6 passed (7)`; `× FR-1530: loads the algorithm the version pins, and draws one node per step 1015ms`; `TestingLibraryElementError: Unable to find a label with the text of: input step Driver age (s_in_age)`. The other tests awaiting "Algorithm version" stayed green. rc=1.
- R2 green under the same mock, load1 4.06: `Test Files  1 passed (1)`, `Tests  7 passed (7)`, rc=0.
- Mock removed; commit 3f1d7727 carries the `beforeAll` only. A4: grep for timeout|Timeout|setTimeout|sleep in added frontend lines prints nothing (grep rc=1).
- R3 (A5, 20 runs under load) and G (gate): owed, see Build log.

### Gate

GREEN set (item 29, import closure): changed source modules = `git diff --name-only origin/main...HEAD -- frontend/src` prints only `frontend/src/views/__tests__/RatingDesignView.test.ts`, a test file, no source module. Importers of it: `git grep -n -E "RatingDesignView.test" -- frontend` prints nothing. GREEN = that one file. (`git grep -l DagDesigner -- frontend/src` also lists DagDesigner.test.ts, DagDesignerMounts.test.ts, DagDesignerValidation.test.ts, DiffOverlay.test.ts; they import the component, which is not changed, so they are outside the closure.)

(owed: the lead's slot)

### Audit

(the auditor's)

### Build log

- 2026-11-05 11:34:48Z R1/R2 done; commit 3f1d7727.

- 2026-11-05 11:35:32Z Lead's TESTS HOLD reached the seat at 11:35:00; R1 and R2 ran at 11:34, before it: lag, not a breach (lead's reading). A5's 20 runs wait for the lead's RELEASE and written grant. GREEN set derived above.

- A5 (DP-F2; lead's written grant 'GO NOW' on to-lead "2026-11-05 11:43:09 GMT"), 20 consecutive single-file runs, 11:44:24Z to 11:48:35Z, load1 7.03 to 14.63 at each start (all >= 6), 0 failures of 20, every run `Test Files  1 passed (1)`, `Tests  7 passed (7)`, rc=0. Log (head=3640a1f3 first line):

```
head=3640a1f39e4eec4ee858b02d1241f809ba68dfa6
run=1 11:44:24 load1_start=7.03 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=2 11:44:42 load1_start=8.22 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=3 11:44:57 load1_start=9.58 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=4 11:45:09 load1_start=9.07 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=5 11:45:28 load1_start=9.58 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=6 11:45:57 load1_start=10.31 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=7 11:46:12 load1_start=14.63 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=8 11:46:23 load1_start=14.45 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=9 11:46:32 load1_start=14.26 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=10 11:46:43 load1_start=12.76 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=11 11:46:50 load1_start=11.50 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=12 11:46:58 load1_start=10.84 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=13 11:47:12 load1_start=10.21 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=14 11:47:26 load1_start=10.91 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=15 11:47:35 load1_start=10.59 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=16 11:47:48 load1_start=12.11 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=17 11:47:57 load1_start=12.32 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=18 11:48:12 load1_start=12.01 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=19 11:48:21 load1_start=12.31 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
run=20 11:48:35 load1_start=11.94 rc=0  Test Files 1 passed (1)  Tests 7 passed (7)
done
rc=0
```

## PRs

(none yet)
