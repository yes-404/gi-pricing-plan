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
