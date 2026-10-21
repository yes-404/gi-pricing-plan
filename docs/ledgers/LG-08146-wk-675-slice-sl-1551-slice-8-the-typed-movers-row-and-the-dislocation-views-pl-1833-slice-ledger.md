---
id: LG-8146
family: ledger
title: WK-675 slice SL-1551 — Slice 8, the typed movers row and the dislocation views (PL-1833) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: 57adb9e2
phase: P2
work: WK-675
slice: SL-1551
plans: [PL-1833, PL-1546, PL-1286]
corrected_by: []
relates: [PL-1833, PL-1546, PL-1286, SL-1551, SL-1388, SL-1369, SL-1260, SL-1275, SL-1554]
---

# LG-8146 — WK-675 slice SL-1551: Slice 8

Filed 2026-10-21 under working id 8146 (lead-reserved). Executor seat `exec-1551`, base `origin/main` 57adb9e2, branch `sl-1551-wk675-s8`, worktree `.claude/worktrees/sl-1551`.

**GO:** the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-21 15:10:53 BST" items 1 and 2, and "2026-10-21 15:50:30 BST" ("GO SL-1551 (S8) per 15:10:53 — census its remaining needs first"). Dispatch: the lead's DISPATCH RECORD — SL-1551, `from-lead-2026-10-09.md`, "2026-10-21 15:56:11 BST". Census: `handover/census-planner-1551-2026-10-21.md`. **MERGE-ACK:** not yet given.

## Scope

`PL-1833` (active, #1355): Task 1 (the typed movers row, spec first, then `model-schema`, route, contracts, tests red-first), then Task 2 (the views at `/rating/:slug/v/:version/dislocation`). DP-S8-1 (a) and DP-S8-2 (a) are ruled. Acceptance 5 (order gate) holds the movers row before any frontend read of `/movers`.

## Binding file conditions (dispatch record)

- S8 does not edit `frontend/src/views/RatingDesignView.vue`, the designer components, or any sub-graph api module (those are `SL-1554`'s, S9).
- Shared files, append only, no existing entry edited: `frontend/src/router/index.ts` (with `SL-1275`), `docs/specs/03-rating-engine.md` §5.1 (with `SL-1260`). Whichever of each pair merges later re-merges `origin/main` and re-runs its generators and checks. Both are recorded here; the exact appended entries are listed under Shared-file edits below.

## Needs census (on main 57adb9e2)

`SL-1369` (S1) closed; `SL-1388` closed; `PL-1833` active; `SL-1550` (S7) closed. The typed movers row is in-slice (Task 1), not an activation need.

## Tasks

Task rows are appended here as each task starts.

## Shared-file edits

None yet.

## PRs

None. The slice stops at PR-READY; the lead opens the PR.
