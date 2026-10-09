---
id: LG-9442
family: ledger
title: WK-1178 slice SL-1462 — FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch (PL-1461), slice ledger
status: active
created: 2026-10-09
owner: executor
tree: 8af8a9b48e459c159666bd4e468d743719ade84c
phase: P2
work: WK-1178
slice: SL-1462
plans: [PL-1461]
corrected_by: []
relates: [PL-1461, RL-1457, FD-1456, RL-1445, RL-1263, FR-20, FR-191, FR-237, FR-255, FR-351, FR-355, FR-363, WK-1178]
---

# LG-9442 — WK-1178 slice SL-1462: FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-09 15:22:26 BST — USER: 'worrying only one executor runs'. FILL THE VM NOW …", items 1–4, in `to-lead.md`, a local file): code and tests are written on a branch from S4's pushed head `8af8a9b4`; only small tests run (one file, no database), nothing merges before the GO, the full gate and the MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `SL-1462` in `docs/roadmap.md` (WK-1178, Option A, A-1): *"FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch"*. Its scope is `PL-1461` §"Scope" (requirement coverage table) and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: FR-20, FR-190, FR-191, FR-237, FR-255, FR-351, FR-355, FR-363. The ruling is `RL-1457` (DP-1 (a), DP-2 (a), DP-3 (b), and T1, the `06` §4.2 note).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1461`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1462`'s roadmap row at its head.

Write set: `PL-1461` §"Write set" only. Any other path is a stop to the lead.

**Serial with S4 on the resolver.** `PL-1461` was written against `_Resolver.resolve`. This branch is cut from S4's head, where S4's Task 3 has already lifted the class to module-level `WorkspaceResolver` (`rating_versions.py`). The peril branch goes into that class, re-anchored by symbol (Q1 (a) of planner-g2's GO request).

### Task list

Order and acceptance checks are `PL-1461` §"Tasks" and §"Acceptance Standard" (items 1 to 14). Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run while S3's Task 7 holds gate-1; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1462`, branch `sl-1462-a1-peril-approval`, from `8af8a9b48e459c159666bd4e468d743719ade84c` (S4's pushed head). Stamps are BST (`TZ=Europe/London date`).

- Commit 1: `PL-1461`'s `status:` line `draft` to `active` (the Q1 ruling, `L1 (a')`), and this file.
- **Red-first proof is OWED for every database-backed test.** The tests of items 1 to 9 need Postgres (`GIP_TEST_DATABASE_URL`), which the small-test rule bars; each is written before its code, and its red (by cause) is shown at the first gate-slot window. Item 10 (`packages/pricing-core/tests/test_rating_runtime.py`) needs no database and is run red then green here.

## PRs
