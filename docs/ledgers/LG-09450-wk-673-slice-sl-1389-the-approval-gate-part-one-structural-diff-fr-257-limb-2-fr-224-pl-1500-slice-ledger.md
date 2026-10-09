---
id: LG-9450
family: ledger
title: WK-673 slice SL-1389 — the approval gate, part one — structural_diff, FR-257 limb (2), FR-224 (PL-1500), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: 8af8a9b48e459c159666bd4e468d743719ade84c
phase: P2
work: WK-673
slice: SL-1389
plans: [PL-1500]
corrected_by: []
relates: [PL-1500, RL-1504, RL-1264, RL-1184, RL-1445, RL-1263, RL-1524, SL-1388, FR-219, FR-224, FR-257, FR-364, WK-673]
---

# LG-9450 — WK-673 slice SL-1389: the approval gate, part one

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-10 00:10:36 BST — USER: more than 10% of the weekly allowance is left … USE IT, up to 6 seats …" item A.6, in `to-lead.md`, a local file): code and tests are written on a branch from S4's head `8af8a9b48e459c159666bd4e468d743719ade84c`; heavy runs wait for the gate slot; nothing merges before the GO and the gate.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1500`, slice `SL-1389`, WK-673 Slice 5: *"the approval gate, part one — structural_diff, FR-257 limb (2), FR-224"*. Its scope is `PL-1500` §"Scope" and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: `06` FR-364 (the `structural_diff` amendment), FR-219, FR-257 limb (2), FR-224, `02` FR-136 (the pre-check), FR-242 (the submitted summary, Task 7). Decision points DP-S5-1 to DP-S5-5 are ruled by `RL-1504` items 6 to 10; T3 to T5 and T7 are the spec texts Task 1 applies.

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1500`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1389`'s roadmap row at its head.

Write set: `PL-1500` §"Write set, and its contention" only. Any other path is a stop to the lead. It does not include `scripts/measure-attribution-cost.py`.

### Task list

Order and acceptance checks are `PL-1500` §"Tasks" and §"Acceptance Standard" (items 1 to 19). The plan orders Task 7 before Task 6. Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no gate yet; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10, authoring phase.** Worktree `.claude/worktrees/sl-1389`, branch `sl-1389-wk673-s5-approval-gate-1`, from `8af8a9b48e459c159666bd4e468d743719ade84c` (`origin/sl-1388-wk673-s4-backend-job-routes`, verified by `git rev-parse`). `origin/main` is `61e2a8d9d06087cadd3760e9668b3caff881b85c`. Stamps are BST (`TZ=Europe/London date`).

- Commit 1: `PL-1500`'s `status:` line `draft` to `active` (the 2026-10-09 13:29:49 BST ruling, item 3, `L1 (a')`), and this file.
- **Activation needs read at this tree.** Need 4 (the DP ruling): `RL-1504` is on `origin/main` (`docs/rulings/RL-01504-…`). Need 5 (the submit-route ruling): the plan's "RL 9614" is minted as `RL-1524` (on `origin/main`). Need 3 (`SL-1256` closed): per the plan, met at `137bc817`. Need 2 (`SL-1388` closed): NOT met, S4 is unmerged; this branch is built on S4's head, and where S4's merged code differs the merged code governs.
- **Acceptance 20's S-limb discharge** (to-lead 2026-10-09 22:56:40) goes to the first WK-673 slice whose write set takes `scripts/measure-attribution-cost.py`; `PL-1500`'s write set does not, so it is not this slice's.
- **Small-test and red-first rules** as the 2026-10-09 15:22:26 BST entry: one test file per run under `flock -w 300 /tmp/slots/small-test`, `nice -n 19`, `timeout 150`, load1 ≤ 4.0, no DB module. Tests that need Postgres are written and marked OWED.

## PRs

None yet. The PR is not opened during the authoring phase.
