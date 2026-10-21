---
id: LG-8136
family: ledger
title: WK-674 slice SL-1711 — the scripted WF-701 deployment-steps demo (PL-1710) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: 03c6397f200868f1a0827c197ffbc6de0bf65eda
phase: P2
work: WK-674
slice: SL-1711
plans: [PL-1710]
corrected_by: []
relates: [PL-1710, PL-1237, PL-1537, PL-1620, PL-1544, SL-1711, SL-1258, SL-1259]
---

# LG-8136 — WK-674 slice SL-1711: the WF-701 deployment-steps demo

Filed 2026-10-21 under working id 8136 (lead-reserved in eta.md). Executor seat `exec-1711`, base `origin/main` 44c18e11ca028d25c8b4c9d92077cc0f3622ef8e, branch `sl-1711-wk674-wf701-demo`.

**GO:** the maintainer's (by delegation) entry "2026-10-21 15:03:33 BST — Maintainer: GOs on the 15:02:44 work queue", item 2. The build starts now; the gate waits for D27 (RL-1712 T1 and T2 on main, activation need 5); the compose window is SOLO in a quiet window. **MERGE-ACK:** not yet given.

## Scope

Quoted from PL-1710: the Tasks table row 2 and the section "SL-1711 — the slice" (step table, Tasks 0 and T1–T7, reds R1–R9, acceptance standard items 1–8). The plan is the scope; this ledger grows per task.

## Needs census (on main 44c18e11)

- Need 1, `SL-1259` merged with D5.6 in its `LG-`: roadmap row `status: closed`; LG-1824.
- Need 2, `SL-1258`: roadmap row `status: closed`.
- Need 5: UNMET at the GO (the maintainer's entry, item 2): `grep -cF RL-1712` on the 03 FR-259 row is 0. The gate waits for D27.

## Tasks

(appended per task)

## PRs

(none; the lead opens the PR)
