---
id: RS-1884
family: research
kind: audit
title: SL-1554 (WK-675 Slice 9, Designer III) re-audit of the graph.test.ts regression fix and its derived GREEN set
status: draft
created: 2026-10-25   # drafted 2026-10-22 under working id 8159; minted 2026-10-25 as RS-1884
owner: auditor
tree: ed8d65a7d8c17a5fe302f632281f142ce5dc9b17
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1554, PL-1546, RL-1835, RS-1882, RS-1883]
---

# RS-1884 — SL-1554 re-audit of the regression-fix delta

*(Working id 8159, reserved by the lead. Written by `aud-1554c`, 2026-10-22 13:4x BST. Check 31 on this id is expected until the mint.)*

## Question

RS-1883's CLEAN is void: `graph.test.ts` (main's file) was red at the slice head. Does the delta `ab48b63e..ada287f3` fix it, and is the GREEN set the LG now claims derived completely? Read-only: no test, gate or DB was run; vitest results are read from the logs.

## Method

Range `origin/main` (`f3462d8fc1336dc4583fe8a7af92fed399993a55`)`...origin/sl-1554-wk675-s9` (`ada287f3a1fba7fc1a4faa51c3e16846b755d1a4`, tree `ed8d65a7d8c17a5fe302f632281f142ce5dc9b17`). Delta since RS-1883: `git diff --stat ab48b63e origin/sl-1554-wk675-s9` = 2 files (the LG; `frontend/src/components/dag/graph.ts`, 5 lines).

## 1. The regression and the fix: MET

- `graph-bd236e3b.log`: `Test Files  1 failed (1)`, `Tests  2 failed | 5 passed (7)`, rc=1, HEAD bd236e3b. `graph-f3462d8f.log`: `7 passed (7)`, rc=0, HEAD f3462d8f.
- `git diff --stat origin/main origin/sl-1554-wk675-s9 -- frontend/src/components/dag/__tests__/graph.test.ts` is empty: the test is unchanged.
- The fix is `graph.ts` only: `FlowEdge.conditional?: true`, spread only when `node.conditional || byId.get(source)?.conditional`. `DagDesigner.vue:117-119` still maps `conditional` to `strokeDasharray: "6 4"`, and `DagDesignerMounts.test.ts:67` (N1) is in batch b2, which passed 3/3.

## 2. The derivation: NOT MET — two importers of `graph.ts` missing

My method: `git diff --name-only origin/main...origin/sl-1554-wk675-s9 -- frontend/src` gives 13 files (equal to the LG's list). Then `git grep -n` of every import of a changed module, and one level up through the components that import it. `graph.ts` is imported by `DagDesigner`, `MountInspector`, `MountNode`, `NodeNavigator`, `StepInspector`, `StepNode`, `QuoteSandboxView`, `RatingDesignView`.

The LG's rule is a text grep over test files (`dag/graph|…|RatingDesignView|mountFixtures`). It reproduces its 10 files exactly (run at the head), but a test that reaches `graph.ts` through a component whose name is not in the pattern is invisible to it. Two such tests exist:

| Test file | Reaches the changed `graph.ts` through | In LG's 10 |
|---|---|---|
| `frontend/src/components/dag/__tests__/StepInspector.test.ts` | `StepInspector.vue:18` `import { names } from "./graph"` | no |
| `frontend/src/views/__tests__/QuoteSandboxView.test.ts` | `QuoteSandboxView.vue:21` `import { parseRef } from "@/components/dag/graph"` | no |

**Blocking item B1 (the brief's rule: any missing file is blocking).** Neither `names` nor `parseRef` is edited in the diff (`graph.ts` diff touches imports, `FlowEdge`, `edgesOf`, `graphOrder`, `layout`, adds `isPurposeMount`), so I expect both to pass; that is an expectation, not evidence. They have not been run at the head. Remedy: run both through the guarded single-file path (batch ≤ 3, `Test Files  N`, load1 < 6) and add the lines to the LG; or restate the rule as "tests that reach a changed module through an import, one level up" with these two named.

Not blocking, noted: `router/__tests__/index.test.ts` and `views/__tests__/DiagnosticsView.test.ts` import `@/router`, which reaches `RatingDesignView.vue` only through a lazy `import()` (`router/index.ts:247`), so the changed code is not loaded there. `StepNode.vue` has no test file. `useGraphValidation.test.ts` does not reach `graph.ts` (`useGraphValidation.ts` imports only `vue` and `@/api/ratingAlgorithms`).

## 3. The four batch logs: MET

Each `regfix-b1..b4.log` starts with `a91bff432542f7f60f4748fb5ed13acb20c1155e`, carries a `files:` line naming the batch, and shows load1 1.69–1.80:

| Batch | Files | `Test Files` | `Tests` | rc |
|---|---|---|---|---|
| b1 | graph, graphMounts, MountInspector | 3 passed (3) | 20 passed | 0 |
| b2 | DagDesignerMounts, RatingDesignViewMounts, NodeNavigator | 3 passed (3) | 24 passed | 0 |
| b3 | DagDesigner, DiffOverlay, RatingDesignView | 3 passed (3) | 18 passed | 0 |
| b4 | DagDesignerValidation | 1 passed (1) | 3 passed | 0 |

10 files, 65 passed, no failed or skipped; the LG quotes these lines verbatim. The fix head `a91bff43` differs from the audited head `ada287f3` only by the LG file (`git diff --stat`), so the runs stand for the code at the head.

## 4. Negative controls, disclosures, rev-parse rule: MET

- N1–N3 logs: HEAD `ab48b63e`, each rc=1 with the failing test named as in the LG (N1 1 failed of 12; N2 2 failed of 4; N3 1 failed of 8). The mutated lines still exist at the head (`DagDesigner.vue:119`). Load1 was 11.25 / 10.51 / 10.31, above the brief's < 6 line; the LG says so for N1.
- The first attempt's whole-suite run (3 × 826 tests, 2 `graph.test.ts` failures) is disclosed as a breach, and the LG's second entry names those two failures as this regression.
- The 13:26:06 rule (each log starts with `git rev-parse HEAD`) is followed by all 9 logs read.

## 5. audit-docs at the head: MET

`flock -w 900 /tmp/slots/gate-2 env -C <detached worktree at ada287f3> python3 scripts/audit-docs.py`: rc=1, `FAILED (1)`: `check 31: gap in the full allocation between 1838 and 8141`. No other check failed. (The worktree was removed afterwards.)

## Findings

B1 (blocking): the derived GREEN set omits two importers of the changed `graph.ts`. Items 1, 3, 4 and 5 above are met.

## Verdict (proposal; the lead's to issue)

**NOT-CLEAN, one blocking item (B1):** the derived GREEN set omits `StepInspector.test.ts` and `QuoteSandboxView.test.ts`, both of which load the changed `graph.ts`. Everything else in the delta is met. Process note for the lead: the LG's grep cannot see transitive importers; a derivation by import graph is the fix, and it is the same class of miss as the one that hid the regression.

## Breach disclosure (this seat)

One `cd /tmp` ran in a Bash call at the start of the log checks (the harness reset the shell cwd afterwards; no git write ran from it). No test, gate, DB or GitHub action was run. The tools-main worktree was only read.
