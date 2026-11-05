---
id: LG-8338
family: ledger
title: WK-1178 slice SL-8337 — the FR-1530 test awaits the lazy chunk (FD-1748, FD-1800)
status: active
created: 2026-11-05
owner: executor
tree: c218fc5a07f49d03a8fc5ef74e61c78926710c5e
phase: P2
work: WK-1178
slice: SL-8337
plans: [PL-8336]
corrected_by: []
relates: [FD-1748, FD-1800, FR-1530]
---

# LG-8338 — the FR-1530 test awaits the lazy chunk

**GO:** to-lead "2026-11-05 10:36:35 GMT" (DP-F1 keep `findBy` after the chunk await; DP-F2 the 20 runs granted when F asks, never beside a timed gate stage).
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

PL 8336, SL 8337: add `await import("@/components/dag/DagDesigner.vue")` to the `beforeAll` of `frontend/src/views/__tests__/RatingDesignView.test.ts`. Requirement: FR-1530 (no spec change). Findings: FD-1748, FD-1800.

### Task list

- R1 red (injected, not committed), base c218fc5a, vitest single file, load1 4.74: `Test Files  1 failed (1)`, `Tests  1 failed | 6 passed (7)`; `× FR-1530: loads the algorithm the version pins, and draws one node per step 1015ms`; `TestingLibraryElementError: Unable to find a label with the text of: input step Driver age (s_in_age)`. The other tests awaiting "Algorithm version" stayed green. rc=1.
- R2 green under the same mock, load1 4.06: `Test Files  1 passed (1)`, `Tests  7 passed (7)`, rc=0.
- Mock removed; commit 3f1d7727 carries the `beforeAll` only. A4: grep for timeout|Timeout|setTimeout|sleep in added frontend lines prints nothing (grep rc=1).
- R3 (A5, 20 runs under load) and G (gate): owed, see Build log.

### Gate

(owed: the lead's slot)

### Audit

(the auditor's)

### Build log

- 2026-11-05 11:34:48Z R1/R2 done; commit 3f1d7727.

## PRs

(none yet)
