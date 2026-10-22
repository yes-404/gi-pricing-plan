---
id: LG-8141
family: ledger
title: WK-675 slice SL-1554 — Slice 9, Designer III: sub-graph mounting (RL-1835) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: c35113b2
phase: P2
work: WK-675
slice: SL-1554
plans: [PL-1546, PL-1286]
corrected_by: []
relates: [PL-1546, PL-1286, SL-1554, SL-1551, SL-1341, RL-1835, RL-1344, RL-1309, RL-1628, FR-217, FR-218, FR-219, FR-237, NFR-463]
---

# LG-8141 — WK-675 slice SL-1554: Slice 9

Filed 2026-10-21 under working id 8141 (lead-reserved). Executor seat `exec-1554b`, base `origin/main` c35113b2, branch `sl-1554-wk675-s9`, worktree `.claude/worktrees/sl-1554`.

**GO:** the maintainer's entries in `to-lead.md`: "2026-10-21 15:10:53 BST" item 2 (GO SL-1554, build-order item D relaxed for building) and "2026-10-21 15:39:13 BST" with its 15:39:19 correction (RL-1835 adopted as drafted; whichever of S8, S10, S11 and S9 merges later re-merges `origin/main` and re-runs its checks). **MERGE-ACK:** not yet given.

## Scope and write set

Authority: `RL-1835` (no leaf plan; `PL-1546` row 8 and `PL-1286:312` give the scope). Write set: `frontend/` only — `frontend/src/components/dag/`, `frontend/src/views/RatingDesignView.vue`, a new `frontend/src/api/subGraphs.ts`, and their tests. Any change under `packages/model-schema/`, `backend/`, `docs/contracts/` or `docs/specs/` is a STOP to the lead.

Binding file conditions with `SL-1551` (S8), from the dispatch record "2026-10-21 15:56:11 BST": S9 does not edit `frontend/src/router/index.ts` or any dislocation file; S8 does not edit `RatingDesignView.vue`, the designer components or S9's api module. Checked at the first push.

## Tasks

Red-first; each cites RL-1835.

1. `frontend/src/api/subGraphs.ts`: `getSubGraph(ref)` over the generated `SubGraph` type ((i) item 5).
2. `graph.ts`: mounts as nodes in `edgesOf`, `graphOrder`, `layout`; edges flagged conditional for a purpose mount ((i) items 1, 3, 4).
3. `MountNode.vue` and the `mount` node type in `DagDesigner.vue`: `mount_point`, `slug@version`, purposes badge text, dashed border, issues by `mount_point`, the not-pinned warning ((i) items 2, 4; (ii) item 3).
4. `MountInspector.vue`: version select from `pins.sub_graphs`, `mount_point`, port rows from the fragment, the two purposes checkboxes with `purposes` omitted when none ((i) item 5; (iii) items 1, 2).
5. Add-mount control, disabled with a text reason when no sub-graph is pinned; `NodeNavigator` lists and removes mounts ((i) item 6; (iii) item 4).
6. Diff overlay marks a mount from `sub_graph_mounts` ((i) item 7).
7. `RatingDesignView.vue` passes `pins.sub_graphs`; no write to `/rating-versions` ((ii) item 2).

## Acceptance — each shown red once (RL-1835 "Acceptance")

Nine frontend tests, one per violation: two mount nodes by `mount_point`; the purpose badge on the cancellation-only mount only; a validate issue shown on its mount; input-port rows equal the fragment's; unchecking both purposes saves no `purposes` key; select options equal `pins.sub_graphs`; the not-pinned warning; one `sub_graph_mounts` entry marks that node only; `NodeNavigator` lists each mount.

## PRs

None yet.

## Record

Entries are appended below as the work lands.

### Entry 2026-10-22 — state of the pre-pause WIP commit e411c85a (recorded as owed since 2026-10-21)

- `frontend/src/components/dag/MountInspector.vue` at `e411c85a` was an **empty stub** (`<script setup lang="ts"></script>` and `<template><form /></template>`, 6 lines). It implements none of (i) item 5 or (iii) items 1–2. The tests that name it (`MountInspector.test.ts`, `DagDesignerMounts.test.ts`) were written, never run, and are red by construction.
- The body of `e411c85a` carries the line "The migration has not been applied to any DB." That line is **misplaced**: the commit changes `frontend/` only and no migration exists in this slice. The commit is left as pushed (no rewrite); this entry is the correction.
- Also at `e411c85a`: `graph.ts` (`edgesOf`, `graphOrder`, `layout`) does not yet take mounts, there is no `MountNode.vue`, and `DagDesigner.vue` has no `subGraphPins` prop; `getSubGraph` is `(slug, version)` where Task 1 above writes `getSubGraph(ref)` (the tests use `(slug, version)`; Task 1 is read that way).

### Entry 2026-10-22 — test defect found at GREEN: DagDesignerMounts "shows a validate-route issue … on that node"

At head 0916a2a5 this test failed with `Error: no node m_refund` (test line 72). Cause confirmed, not assumed: the test called `node("m_refund")` synchronously after `render`, before Vue Flow had put its nodes in the DOM. With `await screen.findByLabelText(/sub-graph mount m_refund/)` first, the file passed (11 passed (11)). With that await and the issue dropped from the fixture (`issues: []`), the issue assertion failed (`Unable to find an element with the text: m_refund closes a cycle`, 1 failed | 10 passed (11)), so it still bites. A test defect, not a component defect; the assertion is unchanged. Fixed in its own commit.

### Entry 2026-10-22 — RED/GREEN record (RS 8156 B1) and the N1–N3 tests

RS 8156 (branch `aud-1554-2026-10-22`) found this ledger held no RED or GREEN run; the numbers relayed earlier (24 failures at `7576489f`, 8 files green) were chat only. **They are superseded by the runs below**, each one file per run through the small-test slot, stdout and stderr captured to the log named, `rc` appended by the wrapper. Nothing here is a gate; the full gate is still owed.

**N1–N3, one test commit `ab405217`, written before this entry and with no code change.** Each passes at the current code, so each **pins existing behaviour; no red is possible** (run once each, pass):
- N1 `DagDesignerMounts.test.ts`: the conditional mount's edges carry `stroke-dasharray: 6 4`, the unconditional mount's edge none (`DagDesigner.vue:119`).
- N2 `RatingDesignViewMounts.test.ts`: with `pins.sub_graphs` omitting `m_refund`'s version, the not-pinned warning shows, the save control has `aria-disabled="false"`, and a click saves once (RL-1835 (ii) 3 "Testable as").
- N3 `MountInspector.test.ts`: picking a pin with a different slug resets `inputs` and `outputs` to `{}`; picking another version of the same slug keeps both.

**The slug-change reset (RS 8156 (v)) is ruled implementation within RL-1835's intent; no open question** (the maintainer's to-lead entry "2026-10-22 13:15:28 BST", relayed by lead 26). Reason: a different fragment has different ports, so the old `inputs` and `outputs` maps would point at ports that do not exist, which compile refuses. `MountInspector.vue` `setRef` resets both maps when the slug changes and keeps them for another version of the same slug. N3 pins it.

**Observation, no change:** clearing an input-port field saves `""` as the parent name (`setInput`), so an empty parent name can be saved for an input the ruling says is required. Not changed in this slice.

RED, at `7576489f` (detached checkout in the slice worktree; its test files, before N1–N3), vitest summary lines verbatim:

| File | Summary | rc | Log |
|---|---|---|---|
| `graphMounts.test.ts` | `Test Files  1 failed (1)` / `Tests  4 failed \| 1 passed (5)` (the pipe is escaped for the table; the log line has none) | 1 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/red-graphMounts.log` |
| `MountInspector.test.ts` | `Test Files  1 failed (1)` / `Tests  6 failed (6)` | 1 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/red-MountInspector.log` |
| `DagDesignerMounts.test.ts` | `Test Files  1 failed (1)` / `Tests  11 failed (11)` | 1 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/red-DagDesignerMounts.log` |
| `RatingDesignViewMounts.test.ts` | `Test Files  1 failed (1)` / `Tests  3 failed (3)` | 1 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/red-RatingDesignViewMounts.log` |

4 files, 24 failed (4 + 6 + 11 + 3), the figure the brief relayed.

**A first RED attempt was discarded.** It ran at the branch head, not at `7576489f`, because the commit-msg hook rejected a `Claude-Session` trailer on the N1–N3 commit, so that commit did not happen and the checkout to `7576489f` aborted on the uncommitted test edits. Its 4 logs were deleted; the RED was re-run at `7576489f` after the commit, and only the logs above remain. The test counts prove which commit the kept logs ran at: `DagDesignerMounts.test.ts` has 11 tests in the RED log against 12 in the GREEN log, and `MountInspector.test.ts` 6 against 8 (N1 and N3 add 1 and 2), so the RED logs ran on the pre-N1–N3 test files.

GREEN, at `ab405217` (the branch head with N1–N3):

| File | Summary | rc | Log |
|---|---|---|---|
| `graphMounts.test.ts` | `Test Files  1 passed (1)` / `Tests  5 passed (5)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-graphMounts.log` |
| `MountInspector.test.ts` | `Test Files  1 passed (1)` / `Tests  8 passed (8)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-MountInspector.log` |
| `DagDesignerMounts.test.ts` | `Test Files  1 passed (1)` / `Tests  12 passed (12)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-DagDesignerMounts.log` |
| `NodeNavigator.test.ts` | `Test Files  1 passed (1)` / `Tests  8 passed (8)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-NodeNavigator.log` |
| `DagDesigner.test.ts` | `Test Files  1 passed (1)` / `Tests  6 passed (6)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-DagDesigner.log` |
| `DiffOverlay.test.ts` | `Test Files  1 passed (1)` / `Tests  5 passed (5)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-DiffOverlay.log` |
| `RatingDesignViewMounts.test.ts` | `Test Files  1 passed (1)` / `Tests  4 passed (4)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-RatingDesignViewMounts.log` |
| `RatingDesignView.test.ts` | `Test Files  1 passed (1)` / `Tests  7 passed (7)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/green-RatingDesignView.log` |

8 files, 55 passed, 0 failed. One run each: this is not a verdict on flakiness (the :72 race above was one).

### Negative controls (2026-10-22, exec-1554e; the lead's condition on RS 8158)

Each control is a scratch edit at head `ab48b63e`, run through the small-test slot with one test file, then restored with `git checkout -- <file>`. Nothing mutated was committed; `git status --short` was empty after each restore. Each log starts with `git rev-parse HEAD` and `git diff --stat`. Each run also printed load1 before it; the logs show it (N1 11.25, above the brief's < 6 line).

| Control | Mutation (file:line, scratch) | Summary line (verbatim) | rc | Failing test(s) by name | Log |
|---|---|---|---|---|---|
| N1 | `frontend/src/components/dag/DagDesigner.vue:119`: removed the `strokeDasharray: "6 4"` conditional-edge style line | `Tests  1 failed \| 11 passed (12)` | 1 | `DagDesignerMounts.test.ts` > "draws the conditional mount's edges dashed and the unconditional mount's solid" | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/negctl-N1.log` |
| N2 | `frontend/src/views/RatingDesignView.vue:73`: `canSave` also required every mount's ref to be in `rating.pins.sub_graphs` | `Tests  2 failed \| 2 passed (4)` | 1 | `RatingDesignViewMounts.test.ts` > "warns of an unpinned mount yet leaves save enabled (RL-1835 (ii) 3)"; also "draws the loaded mounts and saves them, without any write to a Rating Version" | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/negctl-N2.log` |
| N3 | `frontend/src/components/dag/MountInspector.vue:46`: `setRef` no longer resets `inputs`/`outputs` (`edit({ ref: next })`) | `Tests  1 failed \| 7 passed (8)` | 1 | `MountInspector.test.ts` > "resets the port maps when the pick has another slug (the slice's choice, RS 8156 (v))" | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/negctl-N3.log` |

Disclosure: a first attempt had a shell argument slip. Its mutation step failed (nothing was edited) and vitest ran the whole frontend suite three times (826 tests each, 2 failed in `graph.test.ts`, unmutated tree). Those runs are not controls and have no log here. The 2 `graph.test.ts` failures at the unmutated head are unexplained and not investigated.

### Entry 2026-10-22 — graph.test.ts regression: red at the slice head, cause, miss, fix (exec-1554g; to-lead "2026-10-22 13:34:04 BST", maintainer "2026-10-22 13:36:57 BST")

**Regression.** `frontend/src/components/dag/__tests__/graph.test.ts` (main's file, unchanged by this slice) passes at `origin/main` f3462d8f (`Tests` all passed; log `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/graph-f3462d8f.log`) and fails only at the slice head bd236e3b: `Tests 2 failed | 5 passed (7)` (log `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/graph-bd236e3b.log`). The failures are the exact-shape assertions at `graph.test.ts` :11 and :33.

**Cause.** `edgesOf` in `frontend/src/components/dag/graph.ts` set `conditional: <boolean>` on every edge, so plain step edges gained a `conditional: false` key that main's `toEqual` shapes do not have.

**The miss.** `graph.test.ts` imports `graph.ts` but was outside the 8-file GREEN above, so the slice's GREEN never ran it. The earlier disclosure ("2 `graph.test.ts` failures … unexplained and not investigated") is this regression.

**Fix** (commit a91bff43; `graph.test.ts` not edited): `FlowEdge.conditional` is now `conditional?: true`, and `edgesOf` spreads `{ conditional: true }` only on an edge into or out of a purpose mount. Plain step edges and unconditional-mount edges keep main's shape. `DagDesigner.vue` already reads the flag as falsy = solid; no change.

**GREEN is now derived, not hand-picked.** Command (at the fix head a91bff43): `git diff --name-only origin/main...HEAD -- frontend/src` gave 13 files (`api/subGraphs.ts`; `components/dag/{DagDesigner,DiffOverlay,MountInspector,MountNode,NodeNavigator}.vue`, `graph.ts`, `__tests__/{DagDesignerMounts,MountInspector,graphMounts}.test.ts`, `__tests__/mountFixtures.ts`; `views/RatingDesignView.vue`, `views/__tests__/RatingDesignViewMounts.test.ts`). Rule applied: every test file under `frontend/src` whose text names a changed module or a component that wraps it: `grep -rlE "dag/graph|from \"\./graph\"|\.\./graph\"|subGraphs|DagDesigner|DiffOverlay|MountInspector|MountNode|NodeNavigator|RatingDesignView|mountFixtures" src --include=*.test.ts`. That is 10 files (the 9 of the brief plus `DagDesignerValidation.test.ts`, which mounts DagDesigner). Run in guarded batches of at most 3: `test -f` on each path, the vitest call naming exactly those paths, load1 quoted in each log (1.69–1.80, below 6), output showing `Test Files  N` equal to the batch size. Each log starts with `git rev-parse HEAD` = a91bff432542f7f60f4748fb5ed13acb20c1155e.

| Batch | Files | Summary lines (verbatim) | rc | Log |
|---|---|---|---|---|
| b1 | graph, graphMounts, MountInspector | `Test Files  3 passed (3)` / `Tests  20 passed (20)` | 0 | `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1554-vitest/regfix-b1.log` |
| b2 | DagDesignerMounts, RatingDesignViewMounts, NodeNavigator | `Test Files  3 passed (3)` / `Tests  24 passed (24)` | 0 | `…/regfix-b2.log` |
| b3 | DagDesigner, DiffOverlay, RatingDesignView | `Test Files  3 passed (3)` / `Tests  18 passed (18)` | 0 | `…/regfix-b3.log` |
| b4 | DagDesignerValidation | `Test Files  1 passed (1)` / `Tests  3 passed (3)` | 0 | `…/regfix-b4.log` |

10 files, 65 passed, 0 failed, 0 skipped. `eslint src/components/dag/graph.ts` rc 0; `vue-tsc --noEmit -p tsconfig.app.json` rc 0 (both niced). One run each: not a verdict on flakiness.
