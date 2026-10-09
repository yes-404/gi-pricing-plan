---
id: LG-9441
family: ledger
title: WK-1178 slice SL-1536 — FD-1374, a rating step reads only the names it declares, FR-246 enforced (PL-1535), slice ledger
status: active
created: 2026-10-09
owner: executor
tree: d471a43bdc4ed123258a7398bbcf30c62605aa27
phase: P2
work: WK-1178
slice: SL-1536
plans: [PL-1535]
corrected_by: []
relates: [PL-1535, PL-1520, RL-1519, FD-1374, FD-1534, FR-246, FR-212, WK-1178]
---

# LG-9441 — WK-1178 slice SL-1536: FD-1374, FR-246 enforced

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-09 13:17:43 BST — USER: parallel …" item 2, in `to-lead.md`, a local file): code and tests are written on a branch from `origin/main` `d471a43bdc4ed123258a7398bbcf30c62605aa27`; no heavy run while S3's Task 7 holds gate-1; nothing merges before the GO and the gate.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1535` (single-row Work plan for WK-1178), slice `SL-1536`: *"WK-1178 fix slice — FD-1374: a rating step reads only the names it declares (FR-246 enforced)"*. Its tasks are `PL-1520` Task 1A, Steps 1–8, as ruled by `RL-1519` (DP-F35-1 (ii) (a)/(a)/(a), (iii-a) (b), (iii-b) (b)), with the plan's deviations D1 (tokenizer, no Spike S1), D2 (no Task 1 Step 6) and D3. Requirement ids: FR-246, FR-212 (fixtures gain producers); register FD-1374.

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1535`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1536`'s roadmap row at its head.

Write set: `PL-1535` §Tasks / `PL-1520` Task 1A "Files" only. **FD-1534's remedy (a)** (the extractor in `packages/pricing-core/tests/test_rating_committed_strings.py` skips an empty literal) is the lead's 2026-10-09 brief item for this slice, but that path is not in that write set; it waits on a ruling (build log).

### Task list

Added with each commit.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run while S3's Task 7 holds gate-1) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1536`, branch `sl-1536-fd1374-dp-f35-1`, from `origin/main` `d471a43bdc4ed123258a7398bbcf30c62605aa27`.

- Commit 1: `PL-1535`'s `status:` line `draft` to `active`, and this file.

## PRs

(none yet)
