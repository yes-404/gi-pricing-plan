---
id: LG-9917
family: ledger
title: WK-675 slice SL-9916 — the DagDesigner F39 fix, stub /rating-algorithms/validate and flush the debounce (FD-9914)
status: active                 # active → closed (§1.2a)
created: 2026-10-11
owner: executor
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-675
slice: SL-9916
plans: [PL-1546]
corrected_by: []
relates: [FD-9914]
---

# LG-9917 — WK-675 slice SL-9916, the DagDesigner F39 fix

Executed by `executor-dagfix`. Working ids: slice 9916, ledger 9917, finding 9914. Stamps are UTC.

**GO:** `to-lead.md` "2026-10-11 10:38:57 BST — DagDesigner F39 reds: an FD against WK-675 at D10 ADOPTED, with a small fix slice queued" item 3, and "2026-10-11 10:41:41 BST — CORRECTION to my 10:41:33 item 2c: the DagDesigner fix gets the FULL two-half gate". The dispatch is the lead's brief `brief-wave1b-2026-10-11.md` (executor-dagfix section).
**MERGE-ACK:** added at merge.

## Tasks

### Scope

Row SL 9916 in `docs/roadmap.md` and its Work-plan delta PL 9918 (cherry-picked from the planner's commit `e434f71f`), quoted there. Defect (FD 9914): S3's live-validation debounce (`useGraphValidation.ts:14`, 400 ms) can fire an un-stubbed `/rating-algorithms/validate` fetch inside a `DagDesigner.test.ts` test body, which `frontend/src/test-setup.ts` fails by name (register row F39); seen in two loaded gates (SL-1526 @e00c71c1, SL-1600 @8f674476). Write set: `DagDesigner.test.ts` only. DP-1 (a) adopted at the GO: the unmount cancel (`useGraphValidation.ts:52–54`) is proven, with no extra flush and no source change. Requirements: FR-1607 (unchanged), register row F39 (guard held).

### Task list

- Task 1 — the regression test, red on base (PL 9918 Acceptance 1).
- Task 2 — the file-wide `vi.mock("@/api/ratingAlgorithms")`, green ×3 (2) and the stub's broken-input proof (3).
- Task 3 — the unmount test and its broken-input proof (4).
- Task 4 — diff, closing acts, the full two-half gate on the lead's grant (5–7).

### Gate

Pending the lead's grant.

### Audit

Written by the auditor.

### Build log

**2026-10-11 09:47 UTC — an earlier attempt, superseded.** A first version (commit `6eb206a4`) used an `afterEach` that advanced fake timers 500 ms, plus a module mock. The lead ruled at the GO that the flush is not the ruled form (DP-1 (a)); this version replaces it. Its red was rc=1, 4 of 4 failed with the F39 line, and it is not the evidence below.

**2026-10-11 10:5x BST — Task 1, red on base `99f22479`.** Added to the unmodified file only a test that renders `DagDesigner`, finds the step list, then waits 450 ms. `flock -w 300 /tmp/slots/small-test pnpm --dir <wt>/frontend exec vitest run src/components/dag/__tests__/DagDesigner.test.ts` → rc=1, `1 failed | 4 passed (5)`; the new test fails with `Error: F39: this test called fetch without stubbing it: http://localhost:3000/api/v1/rating-algorithms/validate` (`src/test-setup.ts:22`).

**Task 2, green.** Sibling pattern (`DagDesignerValidation.test.ts:9–10`): `vi.hoisted` object with `validateRatingAlgorithm` and `saveRatingAlgorithm` as `vi.fn()`, `vi.mock("@/api/ratingAlgorithms", () => api)`, and a `beforeEach` resolving the validate mock to `{ issues: [] }`. The same command ×3 → `Tests 6 passed (6)`, `Type Errors no errors`, each time. `eslint` on the file rc=0.
Broken input (3), uncommitted: the `vi.mock` line replaced by a comment → `1 failed | 5 passed (6)`, the regression test fails with the same F39 line; restored.

**Task 3, the unmount test.** Renders, `unmount()`, waits 450 ms, expects the mocked `validateRatingAlgorithm` not called; it passes in the three green runs.
Broken input (4), uncommitted and reverted at once: `cancel();` at `useGraphValidation.ts:54` commented out → `1 failed | 5 passed (6)`; the unmount test fails with `AssertionError: expected "vi.fn()" to not be called at all, but actually been called 1 times`. `git status` after the revert shows the source file unmodified.

## PRs

The slice PR (number added at open): "SL-9916: the DagDesigner F39 fix" (merge commit added at merge).
