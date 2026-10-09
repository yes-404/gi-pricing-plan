---
id: LG-9444
family: ledger
title: WK-675 slice SL-1557 — Designer II, live validation and diff (PL-1556), task ledger
status: active
created: 2026-10-09
owner: executor
tree: 8b9d12c7dac1c0272b1109c9c1d2e295847dd575
phase: P2
work: WK-675
slice: SL-1557
plans: [PL-1556]
corrected_by: []
relates: [PL-1556, RL-1555, RL-1474, RL-1438, FD-1437, RL-1445, SL-1477, WK-675]
---

# LG-9444 — WK-675 slice SL-1557: Designer II, live validation and diff

*(LG-9444 is a working id reserved by the lead; the lead mints it. Authored ahead of the GO at the user's order of 2026-10-09 15:22:26 BST.)*

**GO:** not yet given. This slice is authored ahead of its GO at the user's order ("2026-10-09 15:22:26 BST — USER: 'worrying only one executor runs'. FILL THE VM NOW …", items 1–4 of `to-lead.md`). Nothing merges without its GO, its full gate and the maintainer's MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Executed from `PL-1556` (WK-675 Slice 3, leaf plan) by `executor-wk675s3` (sonnet). Branch
`sl-1557-wk675-s3`, worktree `.claude/worktrees/sl-1557`, cut from `origin/batch-d3-2026-10-09`
at `8b9d12c7dac1c0272b1109c9c1d2e295847dd575` (the D3 mint batch; it must merge before this slice;
`origin/main` is ahead by one commit, `61e2a8d9`, which is merged at the merge turn, never rebased).
Row: `SL-1557` in `docs/roadmap.md` (minted from working id 9581), plan `PL-1556` (from 9578),
ruling `RL-1555` (from 9543). Requirements: FR-24, FR-212, FR-214, FR-215, FR-219, FR-223, FR-227,
FR-240, FR-244, FR-403, NFR-463, and the FR that RL-1474 T1 creates. FR-246 is not delivered here
(PL-1556 *Scope*).

### Task list

| Task | Plan step | Acceptance | Status |
|---|---|---|---|
| 0 | Task 0 preconditions | Task 0 rows re-run at the dispatch tree | open |
| 0A | diff route typed, contract regenerated | Acceptance 21 | open |
| 1 | `graph_invariant_issues` and types in model-schema | Acceptance 2, 4 | open |
| 2 | mode mismatch named at compile | Acceptance 16–19 | open |
| 3 | bare-`ValueError` sweep | Acceptance 20 | open |
| 4 | validate route and spec texts | Acceptance 1, 3, 5–11 | open |
| 6 | live validation in the designer | Acceptance 12–15, 23 | open |
| 7 | diff overlay | Acceptance 22 | open |
| 8 | accessibility check | NFR-463 | open |
| 9 | gate and ledger | Acceptance 24 | open (waits for the gate slot) |

### Gate

Not run. Full gates, builds, whole-tree mypy, audit-docs and `migrate --verify` wait for the gate
slot after S3's Task 7 (the lead's brief, small-test rule).

### Audit

Not yet. The auditor writes it.

### Build log

#### 2026-10-09 15:25 BST — worktree and first commit

- Worktree cut from `origin/batch-d3-2026-10-09` = `8b9d12c7` (the brief's head, confirmed by
  `git rev-parse`). The brief's Section C head matches.
- First commit: `PL-1556` status `draft` → `active`, `SL-1557` row `draft` → `active`, this ledger.
- Activation needs (PL-1556 *Activation needs, in order*), read at this tree:
  1. RL-1474 minted: file `RL-01474-…` present. Met.
  2. RL-1438 and FD-1437 minted: both files present. Met.
  3. S2 (SL-1477) merged: `frontend/src/components/dag/` carries `DagDesigner.vue`, `StepNode.vue`,
     `NodeNavigator.vue`; `RatingAlgorithmDraft` at `rating.py:423`. Met.
  4. DP-S3-1 and DP-S3-2 decided: RL-1555 (in this batch). Met.
  5. No slice editing `compile.py` in flight: **to be named in Task 0** (SL-1340, a sibling seat of
     this overnight wave, may edit `compile_bundle`; the brief's order is merge-ordered, so the
     conflict is a merge-turn matter, but the lead should read it).
  6. Task 0 re-run: Task 0 below.
  7. Maintainer's agreement and the lead's go: not given; this slice is authored ahead of it.

## PRs

None yet.
