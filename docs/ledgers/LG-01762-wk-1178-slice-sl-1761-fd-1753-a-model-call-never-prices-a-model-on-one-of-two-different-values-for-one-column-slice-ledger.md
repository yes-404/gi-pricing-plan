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
**Gate:** the STACKED gate at `69c682df` (tree `3f026830314aefebf722bf6563d784a9e59f9cc5`, SL-1758's code plus this slice's), 12:55:30-14:14:36 BST, ACCEPTED by the maintainer (by delegation), entry "2026-10-17 14:15:29 BST" in `to-lead.md`; logs `gi-pricing-plan.local/scratch/sl8074-gate/`.
**MERGE-ACK:** not yet given.
**Audit:** see `## Audit` below (proposed verdict only).

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

## Audit

*(Written by `auditor-1761`, 2026-10-17, on head `7881c884702600030bcce22ac54621adb3c00ca6`, range `origin/main...7881c884`, `origin/main` = `cf509df8` at fetch. Code read-only; no test run by the auditor; the gate is the lead's.)*

**1. Change set** (`git diff --stat origin/main...7881c884`, 9 paths, +467 -7): `compile.py` (+97), `runtime.py`, `03-rating-engine.md` (FR-222, FR-240, owned-codes), `roadmap.md`, `INDEX.md`, this ledger, and three test files (`test_rating_column_collision.py` new, `test_quote_input_raise_sites.py`, `test_rating_compile_completeness.py`). Nothing outside scope.

**2. Obligations, derived from FD-1753's Disposition and the entry "2026-10-17 11:15:37 BST" first, then evidenced:**
- **Item 1, compile grouping by source column, offset model included:** `check_model_call_columns` (`compile.py`, called after `check_model_call_gbm_factors` in `compile_bundle`); `_model_factors` adds the offset model's Factors recursively. Test `test_two_factors_on_one_column_fed_different_graph_names_is_refused_at_compile` asserts step, both names and the column named. **Met.**
- **Item 3, two graph names onto one slug:** same grouping (key = column or slug); `test_two_graph_names_onto_one_feature_is_refused_at_compile` asserts step and name. A name mapped to two slugs passes (set of names size 1). **Met.**
- **Item 2, predict-time guard:** `_GlmScorer.predict` raises `PredictionError("MODEL_CALL_FEATURE_COLLISION", ..., terms=(column,))` on unequal values; asserts: code, column named, `"25"`/`"45"` absent (NFR-499); equal values score and equal `predict_glm` within 1e-12. **Met.**
- **Q1 (b) precised:** `_same_input` exempts only `input` steps with one `(input_name, on_missing)`. Cases (i) same pair compiles, (ii) different `on_missing` refused, (iii) different `input_name` refused: the three tests at lines 181-202 assert accept / `ValueError` match / `ValueError` match. "Same default value where `on_missing="default"`": `RatingInputStep` (`model_schema/rating.py:352`) carries no default field, so the clause is vacuous at this tree; the `_same_input` docstring says so. **Met.**
- **Q2 (b) per component plus offset:** peril structure scored per `peril_component_refs`, `restrict` limits to the component's slugs; tests `test_frequency_and_severity_banding_one_column_differently_compile` (compiles) and `test_a_collision_inside_one_component_is_refused` (names the component, not the structure). **Met.**
- **Spec:** FR-222 and FR-240 dated amendments and `MODEL_CALL_FEATURE_COLLISION` owned-codes entry present in the diff. **Met.** Raise site registered `_INPUT_FREE` in `test_quote_input_raise_sites.py` (common brief item 11); the gate ran that file green (not in the FAILED set).
- **Red proof by cause:** four breaks (a)-(d) in the ledger, each tied to named tests; not re-run by the auditor.

**3. Stacked-gate argument, verified.** `git merge-base --is-ancestor 69c682df 7881c884` rc 0; `rev-parse 69c682df^{tree}` = `3f026830314aefebf722bf6563d784a9e59f9cc5`, the accepted tree. For every non-docs path of `origin/main...7881c884` (5: `compile.py`, `runtime.py`, the three tests) `git rev-parse HEAD:<p>` equals `69c682df:<p>` (checked by the auditor, 5/5 OK), matching `scratch/sl8074-blobproof.md` section B. Section A of that file (the 9 paths that differ between `69c682df` and the head equal `origin/main`'s) was read, not re-run. `compile.py` in the gated tree is the hand-resolved stacked merge (`e9a968d5`, "compile.py keeps both checks"): its blob is the one now at the head, so the gate ran exactly what is submitted; `compile_bundle` calls `check_model_call_gbm_factors` then `check_model_call_columns` (SL-1758's check is on main). `test_the_compile_check_calls_the_one_required_inputs_helper` asserts the exact two calls.

**4. Gate at `69c682df`.** ruff, mypy, import_linter, req_coverage, contracts rc 0; frontend 6/6 rc 0; `audit_docs` rc 1 with only the two check-31 lines (`gap ... between 1743 and 8070`; `id 8072 is created: 2026-10-16, earlier than id 1743's`: working-id artefacts); pytest rc 1, `13 failed, 5893 passed, 6 skipped`; the 13 FAILED names are the `test_audit_docs_*`/`test_doc_index`/`test_register_*`/`test_repository_invariants` cascade, and `sort -u` of them is identical to SL-1758's gate list (`scratch/sl8071-gate/pytest.log`, diff empty). Demo rc 124 is the designed stop (`journey done in 271s`); the one `FAIL` text is the designed `VALIDATION_HAS_FAILURES` refusal. Tree after gate: 0 changed paths.

**5. Findings.**
- **A1 (LOW, fixed here):** this ledger's Gate and Audit header lines were stale (`none granted`, `not yet`) after the gate was accepted; updated above. MERGE-ACK left "not yet given".
- **A2 (LOW, observation):** `predict` compares `row[column] != value`; two equal `NaN` floats on one column compare unequal and would raise `MODEL_CALL_FEATURE_COLLISION`. Not constructed or run; the sentinel and the named column make it visible, not silent. Owner: the lead decides whether to file; no test covers NaN.
- **A3 (disclosed, per FD-1753 item 3):** the predict guard cannot catch two graph names onto one slug (the dict collapses before `predict`); the compile refusal is its only guard, and it covers every bundle that went through `compile_bundle`.
- **A4:** status `closed` was set by the minter in `LG-1762`, `SL-1761`; the evidence above supports it as a slice close (clean audit; Gate accepted) with the lead's merge still to come.

**6. Proposed verdict:** all obligations delivered and evidenced; no requirement without evidence. Proposal only; the lead adopts, amends or rejects. MERGE-ACK: not yet given.

**Lead verdict (2026-10-17 14:33:41 BST, the lead, transcript 1b92c2a6):** the auditor's proposal ADOPTED — all obligations delivered and evidenced; the stacked-gate argument holds (5/5 slice blobs = 69c682df, the accepted gate); A1 fixed; A2 (NaN !=, LOW) → FD 8086 in D20; A3 disclosed in FD-1753 item 3; A4 the closed status stands. MERGE-ACK: not yet given.
