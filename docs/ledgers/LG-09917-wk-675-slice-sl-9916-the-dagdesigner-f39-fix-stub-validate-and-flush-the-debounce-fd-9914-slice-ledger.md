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

Row SL 9916 in `docs/roadmap.md` (cherry-picked from the planner's commit). Defect (FD-9914): S3's live-validation debounce in `useGraphValidation` can fire an un-stubbed `/rating-algorithms/validate` fetch inside a `DagDesigner.test.ts` test, which `frontend/src/test-setup.ts` fails by name (register row F39). Seen in two loaded gates (SL-1526 @e00c71c1, SL-1600 @8f674476). Write set: `frontend/src/components/dag/__tests__/DagDesigner.test.ts` only; any source change stops to the lead. No FR-/NFR- id.

### Task list

- Task 1 — red first on base: advance fake timers past the debounce after each test.
- Task 2 — stub `validateRatingAlgorithm` for the file and keep the debounce flush in teardown.
- Task 3 — the full two-half gate on the lead's grant, closing acts.

### Gate

Pending the lead's grant.

### Audit

Written by the auditor.

### Build log

**2026-10-11 09:47 UTC — Task 1, red (base `99f22479`).** The debounce is `delayMs = 400` at `frontend/src/components/dag/useGraphValidation.ts:14` (`setTimeout(…, delayMs)` at :34). With `beforeEach` `vi.useFakeTimers({ shouldAdvanceTime: true })` and `afterEach` `await vi.advanceTimersByTimeAsync(500)`, no stub: `flock -w 300 /tmp/slots/small-test pnpm --dir <wt>/frontend exec vitest run src/components/dag/__tests__/DagDesigner.test.ts` → rc=1, `4 failed (4)`; each: `Error: F39: this test called fetch without stubbing it: http://localhost:3000/api/v1/rating-algorithms/validate` (`src/test-setup.ts:22`).

**2026-10-11 09:49 UTC — Task 2, green.** `vi.mock("@/api/ratingAlgorithms", …)` with `validateRatingAlgorithm: async () => ({ issues: [] })` over `importOriginal`; the `afterEach` flush stays and restores real timers. The same command ×3 → `Tests 4 passed (4)` each time, `Type Errors no errors`. `eslint` on the file rc=0.

## PRs

The slice PR (number added at open): "SL-9916: the DagDesigner F39 fix" (merge commit added at merge).
