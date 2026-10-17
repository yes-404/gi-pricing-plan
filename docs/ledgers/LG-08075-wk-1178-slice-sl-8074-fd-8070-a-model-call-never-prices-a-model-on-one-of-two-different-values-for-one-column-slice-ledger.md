---
id: LG-8075
family: ledger
title: WK-1178 slice SL-8074 — FD-8070, a model_call never prices a Model on one of two different values for one column, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
phase: P2
work: WK-1178
slice: SL-8074
plans: []
corrected_by: []
relates: [SL-8074]
---

# LG-8075 — WK-1178 slice SL-8074: a model_call never prices a Model on one of two different values for one column

**GO:** the maintainer's (by delegation) entries "2026-10-16 10:52:08 BST" and "2026-10-17 11:08:04 BST" (lane A) in `to-lead.md`. The finding is FD 8070 (`origin/fd-8070-slug-column-collision-2026-10-16`, HIGH by the run of 2026-10-16 11:08:14 BST).
**Gate:** none granted to this seat; the full gate is owed and is the lead's to grant.
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Branch `sl-8074-wk1178-fd8070-column-collision-2026-10-16`, worktree `.claude/worktrees/sl-8074`, cut from `origin/main` `a2f77b2d`, re-merged with `origin/main` `055b5e6b`.

- **Red-first commit (tests only):** `packages/pricing-core/tests/test_rating_column_collision.py`, four tests. Two of them were red for the wrong reason (compile's completeness check refused first, or the bundle could not be built); corrected in the fix commit, the assertions unchanged: a third graph name covers the second Factor, and the score-time tests build their bundle with the compile guard bypassed.
- **Fix commit:** `_GlmScorer.predict` in `pricing_core/rating/runtime.py` (SL-1274's `MODEL_CALL_FEATURE_COLLISION` guard, verbatim); `check_model_call_columns` in `pricing_core/rating/compile.py`, called after `check_model_call_coverage`; its raise site is listed in `_INPUT_FREE` of `test_quote_input_raise_sites.py`.
- **Spec:** `03` FR-222 and FR-240 dated amendments and the owned-codes entry for `MODEL_CALL_FEATURE_COLLISION`.
- **Open decision points (the lead's):** `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl8074-dps.md`, Q1 (the `input`-step pair) and Q2 (peril components grouped per model). The unimplemented branches are named in the roadmap block.

## PRs

Not opened yet; the lead opens the PR.
