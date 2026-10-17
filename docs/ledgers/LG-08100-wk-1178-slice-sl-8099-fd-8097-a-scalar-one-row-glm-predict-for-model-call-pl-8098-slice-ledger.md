---
id: LG-8100
family: ledger
title: WK-1178 slice SL-8099 — FD 8097, a scalar one-row GLM predict for model_call, bit-identical to the polars path (PL-8098), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
tree: c62f1ff67b45022fde947ff67cd01be5ffe89fc5
phase: P2
work: WK-1178
slice: SL-8099
plans: [PL-8098]
corrected_by: []
relates: [PL-8098, SL-8099, FD-8097, FR-193, FR-222]
---

# LG-8100 — WK-1178 slice SL-8099: the scalar one-row GLM predict

**GO:** the maintainer's "plan + GO now" (~20:48 BST 2026-10-17, ruling item 2), relayed in the lead's brief `brief-executor-8099-2026-10-17.md` (2026-10-17 20:54:33 BST).
**MERGE-ACK:** not yet given.

## Tasks

Branch `sl-8099-glm-scalar-predict` (local) pushed to `pl-8098-glm-scalar-predict-2026-10-17`, worktree `.claude/worktrees/sl-8099`, cut from `c62f1ff67b45022fde947ff67cd01be5ffe89fc5`. Row: `SL-8099` in `docs/roadmap.md`. Plan: `PL-8098`.

| Task | What | Status |
|---|---|---|
| T1 | Red first: the parity test and a scalar entry point that raises `NotImplementedError` | below |
| T2 | The scalar path, exact equality | |
| T3 | The wiring in `_GlmScorer`, the load-time choice, the wiring test | |
| T4 | The diagnostic timing (ms/quote, both paths) | |
| T5 | Census re-run and the gate (the lead's grant) | |

## Build log
