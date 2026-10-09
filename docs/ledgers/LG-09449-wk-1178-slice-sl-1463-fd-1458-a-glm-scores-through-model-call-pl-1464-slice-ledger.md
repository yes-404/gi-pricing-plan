---
id: LG-9449
family: ledger
title: WK-1178 slice SL-1463 — FD-1458, a GLM scores through model_call (PL-1464), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: f03792056c347429d0c2278cdbcec6208ee58921
phase: P2
work: WK-1178
slice: SL-1463
plans: [PL-1464]
corrected_by: []
relates: [PL-1464, FD-1458, RL-1263, FR-222, FR-193, FR-255, FR-239, NFR-489, NFR-491, WK-1178]
---

# LG-9449 — WK-1178 slice SL-1463: FD-1458, a GLM scores through `model_call`

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-10 00:10:36 BST — USER: more than 10% of the weekly allowance is left … USE IT, up to 6 seats …", item A.5, in `to-lead.md`, a local file): code and tests are written on a branch from A-1's pushed head `f03792056c347429d0c2278cdbcec6208ee58921`; only small tests run (one file, no database), nothing merges before the GO, the full gate and the MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `SL-1463` in `docs/roadmap.md` (WK-1178, Option A, A-2). Its scope is `PL-1464` §"Scope" and §"Write set, and its contention", read at this branch's tree. Ruling record: the dated notes inside `PL-1464` (DP-1 to DP-5).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1464`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1463`'s roadmap row at its head.

Write set: `PL-1464` §"Write set" only. Any other path is a stop to the lead.

**Serial after A-1.** This branch is cut from A-1's head (which sits on S4's head); the resolver is `WorkspaceResolver`, re-anchored by symbol.

### Task list

Order and acceptance checks are `PL-1464` §"Tasks" and §"Acceptance Standard". Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run during the authoring phase; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10, authoring phase.** Branch `sl-1463-a2-glm-model-call`, from `f03792056c347429d0c2278cdbcec6208ee58921`. Stamps are BST.

- Commit 1: `PL-1464`'s `status:` line `draft` to `active` and this file.

## PRs
