---
id: LG-1762
family: ledger
title: WK-1178 slice SL-1761 — FD-1753, a model_call never prices a Model on one of two different values for one column, slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-17 # original date 2026-10-17, set at the filing; minted 2026-10-17
owner: executor
phase: P2
work: WK-1178
slice: SL-1761
plans: []
corrected_by: []
relates: [SL-1761]
---

# LG-1762 — WK-1178 slice SL-1761: a model_call never prices a Model on one of two different values for one column

*(Minted 2026-10-17 as LG-1762 from working id 8075, with SL-1761 (working id 8074), in the SL-1761 PR; FD-1753 was minted from working id 8070 in the D18 batch mint PR.)*

**GO:** the maintainer's (by delegation) entries "2026-10-16 10:52:08 BST" and "2026-10-17 11:08:04 BST" (lane A) in `to-lead.md`. The finding is FD-1753 (`origin/fd-8070-slug-column-collision-2026-10-16`, HIGH by the run of 2026-10-16 11:08:14 BST).
**Gate:** none granted to this seat; the full gate is owed and is the lead's to grant.
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Branch `sl-8074-wk1178-fd8070-column-collision-2026-10-16`, worktree `.claude/worktrees/sl-8074`, cut from `origin/main` `a2f77b2d`, re-merged with `origin/main` `055b5e6b`.

- **Red-first commit (tests only):** `packages/pricing-core/tests/test_rating_column_collision.py`, four tests. Two of them were red for the wrong reason (compile's completeness check refused first, or the bundle could not be built); corrected in the fix commit, the assertions unchanged: a third graph name covers the second Factor, and the score-time tests build their bundle with the compile guard bypassed.
- **Fix commit:** `_GlmScorer.predict` in `pricing_core/rating/runtime.py` (SL-1274's `MODEL_CALL_FEATURE_COLLISION` guard, verbatim); `check_model_call_columns` in `pricing_core/rating/compile.py`, called after `check_model_call_coverage`; its raise site is listed in `_INPUT_FREE` of `test_quote_input_raise_sites.py`.
- **Spec:** `03` FR-222 and FR-240 dated amendments and the owned-codes entry for `MODEL_CALL_FEATURE_COLLISION`.
- **Decision points, ruled:** Q1 (b) precised and Q2 (b), the entry headed "2026-10-17 11:15:37 BST" in `to-lead.md`. The compile guard exempts only `input` steps with one `input_name` and `on_missing`, and groups a Peril Structure step per component Model with its offset Model. Tests: three Q1 cases and two Q2 cases in `test_rating_column_collision.py`. `test_rating_compile_completeness.py`'s helper-spy test now accepts the second reader of `required_model_inputs`.

## PRs

Not opened yet; the lead opens the PR.

## Red proof, 2026-10-17

Each new test of `test_rating_column_collision.py` shown able to fail by cause: one temporary break of `pricing_core/rating/compile.py` at a time, run through `run-small.sh`, the file restored by `git checkout` after each (the tree clean against the head).

| Break | rc | Red test(s) |
|---|---|---|
| (a) `_same_input` drops the `on_missing` comparison | 1 | `test_two_input_steps_with_one_input_name_and_different_on_missing_are_refused` (`DID NOT RAISE ValueError`); 1 failed, 8 passed |
| (b) any two `input` steps are one value | 1 | the `different_on_missing` test and `test_two_input_steps_with_different_input_names_are_refused` (`DID NOT RAISE ValueError`); 2 failed, 7 passed |
| (c) a Peril Structure grouped over the union of its components | 1 | `test_frequency_and_severity_banding_one_column_differently_compile` and `test_a_collision_inside_one_component_is_refused` (the message names the structure, not the component); 2 failed, 7 passed |
| (d) no grouping inside a component | 1 | `test_a_collision_inside_one_component_is_refused` (`DID NOT RAISE ValueError`); 1 failed, 8 passed |

`test_the_compile_check_calls_the_one_required_inputs_helper` now asserts the exact list `[x, x]`: `check_model_call_coverage`, then `check_model_call_columns`; a third call fails it.
