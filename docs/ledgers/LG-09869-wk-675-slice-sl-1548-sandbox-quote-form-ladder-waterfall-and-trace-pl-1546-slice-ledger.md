---
id: LG-9869
family: ledger
title: WK-675 slice SL-1548 — Sandbox, quote form, ladder waterfall and trace (PL-1546), slice ledger
status: active
created: 2026-10-12
owner: executor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-675
slice: SL-1548
plans: [PL-1546, PL-1286]
corrected_by: []
relates: [PL-1546, PL-1286, RL-1459, OQ-1460, FD-1335, SL-1367, FR-213, FR-247, FR-248, FR-249, FR-251, FR-252, FR-255, FR-256, FR-258, FR-25, NFR-463]
---

# LG-9869 — WK-675 slice SL-1548: Sandbox, quote form, ladder waterfall and trace

**GO:** the maintainer's (by delegation) entry in `to-lead.md`: "2026-10-12 02:53:52 BST — Readiness rulings: GO S6 SL-1548 (swap planner-wk673-c out); FD 9862 LOW, owner WK-677; PL 9864 + PL 9865 deltas OK; FD 9860 (ii)", item 1: "GO SL-1548 (WK-675 S6), executor-sl1548 (sonnet) … R6.1: the per-peril components render ABSENT, with a test, while OQ-1460 is open. The S5 `ordered` drift is recorded in eta: whichever of S5/S6 merges second re-merges and re-gates its quote-form tests." The lead's readiness record of 2026-10-12 02:53:18 BST: `SL-1367` closed (`13a02bba`, #1282), the only activation need.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoted from `PL-1546`'s order table, row 2: "SL-1548 — S6: Sandbox: form, waterfall, trace | `PL-1286` S6 row, plus R6.1–R6.2 | `03` §3.1: FR-213; §3.6: FR-247, FR-248, FR-249 (shown absent, R6.1); §3.7: FR-251, FR-252, FR-255, FR-256; §3.8: FR-258; FR-25; NFR-463 | S1 (closed, met); **`SL-1367` merged** (FD-1335 hold)". Requirements: FR-213, FR-247, FR-248, FR-249 (view limb carried under `OQ-1460`, below), FR-251, FR-252, FR-255, FR-256, FR-258, FR-25, NFR-463.

Branch `sl-1548-wk675-s6-sandbox`, worktree `.claude/worktrees/sl-1548`, cut from `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9`. Row: `SL-1548` in `docs/roadmap.md`.

**R6.1 — FR-249's view limb is carried under `OQ-1460`.** `RL-1459`: FR-249's per-peril limb has no producer yet, so S6 builds no view for it; the per-peril components render absent, with a test that asserts their absence while `OQ-1460` is open.

### Task list

(filled per task)

### Gate

(not yet; the full gate runs only on the lead's "gate slot granted" for that head)

### Audit

(written by an auditor seat; not by the executor)

### Build log

- 2026-10-12 — Activation commit: `SL-1548` `draft → active` with a dated line citing the 02:53:52 BST GO; `PL-1546` `draft → active` (status line only); this ledger opened under working id 9869.

## PRs

(none yet)
