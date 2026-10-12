---
id: LG-9637
family: ledger
title: WK-673 slice SL-1695 — Stage A, FD-1660 the loud guard; attribution refuses a sub-graph mount difference with a coded error, and WF-699 D6 asserts it (PL-1694), slice ledger
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-12
owner: executor
tree: 18803f1d074276052bfe74ee14196b2b0d531697
phase: P2
work: WK-673
slice: SL-1695
plans: [PL-1694]
corrected_by: []
relates: [PL-1694, PL-1267, SL-1695, SL-1696, FD-1660, RL-1686, FR-264, FR-1399]
---

# LG-9637 — WK-673 slice SL-1695: Stage A, the FD-1660 loud guard

*(Working id 9637, reserved by the lead; it is minted at the slice's mint turn. Until then a citation of this ledger names "working id 9637". Quoted entries keep the working ids they were written with: "SL 9850" is SL-1696, "FD 9804" is FD-1660, "RL 9852" is RL-1686, resolved by `PL-1694`'s header paragraph.)*

**GO:** the lead's `from-lead` entry "2026-10-12 08:15:37 BST" (GO for SL-1695; ledger working id 9637), on the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-12 07:44:13 BST" item (1) (DP-G's consequence (A), conditions (a), (b), (c)) and "2026-10-12 08:09:39 BST" (ACK; the two fixed reason clauses; item 4, the interim `03` line in the same commit as the guard).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1694`'s SL-1695 row, "Stage A, the guard": `03` FR-1399 (existing refusal, no text change), FR-264 and §4.6 (the 08:09:39 interim line only), FR-266 and FR-1398 (read), FR-217 (read), `WF-699` D6 (asserted refusal), NFR-499 (the refusal text is input-free). Closes FD-1660's silent limb by a named refusal; FD-1660 stays open until SL-1696.

Branch `sl-1695-wk673-fd1660-guard`, worktree `.claude/worktrees/sl-1695`, cut from `origin/pl-9807-recut-2026-10-12` `18803f1d074276052bfe74ee14196b2b0d531697` (PR #1299's branch; `origin/main` was `2a81974184ee405536fb43d30f59a990b3953669`). Row: `SL-1695` in `docs/roadmap.md`.

### Task list

- **T1 — fixtures and reds on the base, by cause** (PL-1694 Task 1; Acceptance 1–4): the mounted fixture and G1–G4, GT in `packages/pricing-core/tests/test_rating_attribution.py`.
- **T2 — the guard, coded** (Task 2; Acceptance 1–6, 10): `_MountNotYetAttributable` in `analysis.py`, the guard in `attribute`, the raise-site case, and the two interim `03` lines in the same commit.
- **T3 — the journey asserts the refusal** (Task 3; Acceptance 7, 8): `journey.py`, `test_wf699_journey.py`, the README sentence; condition (b)'s grep.
- **T4 — gate, LG, PR** (Task 4; Acceptance 9, 10): the full two-half gate only on the lead's grant for the head.

### Gate

Not yet run. The full gate starts only on the lead's explicit "gate slot granted" for the head (S-13).

### Audit

Not yet given.

### Build log

- 2026-10-12 08:17 BST — activation: `SL-1695` and `PL-1694` set `active`, this ledger opened (working id 9637), by the executor on the GO above. Base `18803f1d`.

## PRs

None yet.
