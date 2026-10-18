---
id: LG-8127
family: ledger
title: WK-674 slice SL-1259 — Slice 5, atomic switchover, rollback and the measurements (PL-1766) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-18
owner: executor
tree: 3421b26b4cb7b622f9af55ca3e32ba8383e8ea4d
phase: P2
work: WK-674
slice: SL-1259
plans: [PL-1766]
corrected_by: []
relates: [PL-1766, PL-1710, PL-1620, PL-1537, PL-1237, SL-1259, SL-1258, SL-1455]
---

# LG-8127 — WK-674 slice SL-1259: Slice 5

Filed 2026-10-18 under working id 8127 (lead-reserved in eta.md). Executor seat `exec-1259`, base `origin/main` 84b0ff5765e55bc8edd139cd22bb57cd474de807, branch `sl-1259-wk674-s5`.

**GO:** the maintainer's (by delegation) entry "2026-10-18 22:50:32 BST — Maintainer: the duplicate-mint anomaly ruled; GO SL-1259, SL-1770, SL-1738, SL-1575 (with conditions)". **MERGE-ACK:** not yet given.

## Needs census (on main 84b0ff57)

- `SL-1258`: roadmap row `status: closed`; merged #1337 (eea416ca).
- `SL-1455`: merged #1323 (9c602fec); its roadmap row still reads `status: active`. The need is read as "merged" (PL-1766 :222).
- `PL-1766` and `PL-1710`: front matter `status: active`.
- Rulings, each in `to-lead.md`: DP-S5-Q1, Q2 and Q7 in "2026-10-17 11:22:47 BST — Maintainer: SL-1259 (S5) DPs ruled; CORRECTION of my 16 Oct 22:22:44 item 2" (Q7 conditional: moot under DP-E1 (a)); DP-S5-Q8 in "2026-10-17 13:06:07 BST — Maintainer: DP-S5-Q8 → (a) for BOTH DP-E1 branches".
- `PL-1710` DP-3's pre-build statement: below, in this ledger.

## PL-1710 DP-3 pre-build statement (D5.9)

**Status: submitted to the decision-maker; NOT ruled. No code for D5.6, the switch, PREPARE, COMMIT or REVERT is written until it is.**

Facts: today `deploy()` (`backend/src/app/platform/deployments.py:455-577`) flushes the `DeploymentRow`, then `audit.record(deployment.created, after=Deployment)` in the SAME session; the route's commit is after return. No PREPARE/COMMIT mechanism exists (`git grep` at 84b0ff57). Proposed order in the deploy transaction: flush row → PREPARE round (every process hydrates the bundle off-loop and acks; nothing swapped) → COMMIT round (every process swaps its one `live` ref, acks) → `audit.record` with `after.commit_acks` = the per-process set {container, process} → transaction commit.

Failure cases, all loud, none silent:

- **F1 — PREPARE short or timeout:** nothing swapped; raise a 5xx problem naming the missing processes; the transaction rolls back (no row, no event); processes drop prepared bundles.
- **F2 — COMMIT round partial or timeout:** the coordinator runs a REVERT round restoring each swapped process's previous `live` (the predecessor ref is known from `previous`); the transaction rolls back; the 5xx problem names per process {committed, reverted, unacknowledged}.
- **F3 — DB commit fails after COMMIT acks (or REVERT incomplete in F2):** no Deployment row exists, so the DB says old version while some processes run new. Recorded: the 5xx problem body carries the per-process state; the coordinator logs it at ERROR; the DB stays the source of truth — each process re-reads the latest committed Deployment on its next startup AND the switch message carries the DB ref, so a process whose `live` differs from the latest committed Deployment ref reconciles to it on its next /score-adjacent heartbeat (mechanism to be pinned in Task 1 with a test). NO new audit action is added (03 :1024 closes the catalogue; a switch-failed event would be a spec change not made without a ruling). The audit after-state therefore only ever carries a COMMIT set from a switch whose transaction committed; "all switched" is never written for a failed transaction.

**Residual risk, stated:** F3 with an unreachable process leaves a window of mixed versions until reconcile; it cannot be made atomic without two-phase commit against Postgres. If that is unsafe, the decision-maker rules (b) or (c) per DP-3's condition (`PL-1710` :477).

**Lead's note (2026-10-18):** the lead does not OK this; whether F3 is "safe" is the decision-maker's. Until ruled: no code for D5.6, no switch/PREPARE/COMMIT/REVERT path, no new reconcile mechanism.

## Tasks

Per PL-1766 (§"Slice 5 (`SL-1259`) — changes since `PL-1710`", D5.6 to D5.14) and `PL-1620` D5.1 to D5.5. **Held pending the DP-3 ruling:** D5.6, D5.9 and everything on the switch/rollback path. Task rows are appended here as each task starts.

## PRs

None yet. The slice stops at PR-READY; the lead opens the PR.
