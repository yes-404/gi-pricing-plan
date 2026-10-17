---
id: LG-1759
family: ledger
title: WK-1178 slice SL-1758 — FD-1754, a model_call refuses a GBM fitted on a banded or grouped Factor, slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-17 # original date 2026-10-16, set at the filing; minted 2026-10-17
owner: executor
phase: P2
work: WK-1178
slice: SL-1758
plans: []
corrected_by: []
relates: [SL-1758]
---

# LG-1759 — WK-1178 slice SL-1758: a model_call refuses a GBM on a banded or grouped Factor

*(Minted 2026-10-17 as LG-1759 from working id 8072, with SL-1758 (working id 8071), in the SL-1758 PR; FD-1754 was minted from working id 8073 in the D18 batch mint PR.)*

**GO:** the maintainer's (by delegation) entry "2026-10-16 10:59:28 BST — Maintainer: the GBM model_call defect — the reading is accepted; disposition fixed now, severity on the run", item 1, in `to-lead.md`; the probe evidence is the lead's entry "2026-10-16 10:59:07 BST" in `from-lead-2026-10-09.md`. The finding is FD-1754 (FD 1754 in D18, unmerged), HIGH on the probe run (case C red, a silent mispricing).
**Gate:** none granted. The box was held by an ALONE latency gate when this was written; every run is owed (below).
**MERGE-ACK:** not yet given.
**Audit:** written below (`auditor-8071`, 2026-10-17), on head `d3d03fbb`.

## Tasks

Branch `sl-8071-wk1178-gbm-banded-refusal-2026-10-16`, worktree `.claude/worktrees/sl-8071`, cut from `origin/main` `a2f77b2d`.

- **Red-first commit (tests only):** `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py` (compile: case C, case A, grouped, controls, the negative "pinned but never called" test, the runtime `GbmFitError`) and `backend/tests/test_rating_gbm_banded_save.py` (save: cases A and C, grouped, peril component, controls, the no-`model_call` negative).
- **Fix commit:** `gbm_transformed_factors` and `GBM_MODEL_TYPES` in `pricing_core/modelling/factors.py` (the one definition); `check_model_call_gbm_factors` in `pricing_core/rating/compile.py`, called after `check_model_call_coverage`; `_refuse_gbm_transformed_factors` in `app/platform/rating_algorithms.py`, called from `check_model_call_feature_maps`; the code in `RATING_ERROR_CODES`; `GbmFitError` in the `model_call` handler's except tuple (`rating/runtime.py`).
- **Why `GbmFitError` is caught by name rather than made a `ModellingError`:** `GbmFitError`, `PredictionError` and `ModellingError` are three direct `RuntimeError` subclasses. Re-parenting would change what `except ModellingError` catches in `backend/src/app/platform/prediction.py`, `transformations.py` and the worker handlers, which catch and map it on their own terms.
- **Spec:** `03` FR-222 (dated "Known gap" amendment, owner WK-673) and FR-240 (pointer), and the owned-codes list entry.
- **Scope checks by reading:** the refusal is keyed on the `model_call` step, never on the pin (WF-699 pins the banded GBM at `examples/fremtpl2/journey.py:664`, recompiles at `:743-745`, and skips B4 and C1' at `:78-79`); NFR-489's bench GBM (`scripts/bench-rating.py`, raw `f0..f7`, no Factors) has an empty `pin.factors`, so it is not refused.

## PRs

Not opened yet; the lead opens the PR.

## Gate red fixed, 2026-10-17 (the maintainer 00:07:43 BST ruling)

The SL-1758 gate's one real red was `test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case`: the new `_raise_named` site in `check_model_call_gbm_factors` was unregistered. The raise call, verbatim:

```python
_raise_named(
    "MODEL_CALL_GBM_TRANSFORMED_FACTOR",
    f"step {step.step_id!r}: {model_ref} is a GBM fitted on banded or grouped "
    f"Factors [{named}], which a model_call cannot score: the Bundle carries "
    "no Bandings or Groupings for a GBM (FR-222, FR-240)",
)
```

Form: an `_INPUT_FREE` entry, not a sentinel case. The site runs at compile time over the algorithm and its pins before any quote exists, and the text carries only the step id, the pinned model ref, and each Factor's slug and kind (`named` is `slug (type)`); no field comes from a quote row. `test_the_gbm_factor_refusal_message_is_exactly_its_structural_fields` pins the whole text.

## Owed after GATE END (item 10)

Still owed: the full gate on the lead's grant; the backend files that need the per-worktree database (`backend/tests/test_rating_algorithms.py`, `backend/tests/test_sub_graphs_api.py` and the DB-fixture tests of `backend/tests/test_rating_glm_model_call.py` error at fixture setup with "the per-worktree test database ... does not exist yet": not a test failure, not green, owed to the gate).

## Red-first proof by cause, 2026-10-16 (partial; run 2026-10-16 11:13:38 BST)

Detached worktree at `a26e9dfe` (red-first), `run-small.sh`, one file per run, load1 2.86 at start. Worktree removed afterwards.

- `run-small.sh <red-wt> packages/pricing-core/tests/test_rating_gbm_banded_refusal.py`: rc 1, `6 failed, 3 passed in 7.98s`. FAILED: case C [xgboost], case C [lightgbm], case A [xgboost], case A [lightgbm], `test_a_grouped_factor_is_refused_too` (each: `Failed: DID NOT RAISE ValueError`, at the test's own assert), `test_a_gbm_fit_error_while_scoring_is_the_named_model_call_failure` (`RuntimeError: {"type":"NodeError",...,"nodeId":"s_risk"}`, the GbmFitError escaping as a node error). Passed: the three controls (never-called pin, plain-factor GBM, GLM on banded). Red by cause.
- `run-small.sh <red-wt> backend/tests/test_rating_gbm_banded_save.py` (no DB fixtures used): rc 1, `5 failed, 4 passed, 2 warnings in 0.62s`. FAILED: `test_the_code_is_a_rating_error_code` (`'MODEL_CALL_GBM_TRANSFORMED_FACTOR'` not in RATING_ERROR_CODES), case C and case A at save and the grouped test (`DID NOT RAISE PlatformError`), `test_each_component_of_a_peril_structure_is_checked` (`AttributeError: ... has no attribute '_component_model_refs'`, a missing symbol the fix adds, not an import/fixture failure). Passed: four negatives and controls. Red by cause.

## Green and neighbours, 2026-10-16 (run 22:20-22:25 BST, tree = merge `9001b01e` of origin/main `6b25b9bc` into `481db4c0`+ledger)

`run-small.sh`, the worktree at the merge, load1 3.8-5.5:

- `backend/tests/test_rating_gbm_banded_save.py` + `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py`: rc 0, `18 passed, 2 warnings in 4.73s` (GREEN on both red-first files).
- `test_rating_compile.py` + `test_rating_runtime.py` + `test_rating_glm_model_call.py` (pricing-core): rc 0, `81 passed in 3.83s`.
- `test_rating_mounted_model_call.py` + `test_gbm.py` + `test_rating_score.py` (pricing-core): rc 0, `205 passed in 21.33s`.
- `backend/tests/test_rating_gbm_banded_save.py` + `test_rating_algorithms.py` + `test_rating_glm_model_call.py`: rc 1, `13 passed, 2 warnings, 23 errors in 10.58s`; every error is "ERROR at setup" of an `api_settings` fixture (per-worktree test database absent; createdb barred while a code gate holds gate-1). No FAILED line.
- `ruff check .` rc 1 on first run: one SIM212 at `backend/tests/test_rating_gbm_banded_save.py:96` (this slice's own line), fixed to `**(ref if ref else {"model_ref": MODEL})`; rc 0 after. `mypy` rc 0 (240 files); `lint-imports` rc 0 (4 kept, 0 broken). `ruff format --check .` rc 1 on 527 files repo-wide (not part of the CLAUDE.md gate; baseline, not this slice's).

## Audit

*(Written by `auditor-8071`, 2026-10-17, on head `d3d03fbbcded9e2a767386516c8d6d08865ca156`, tree `72fd9f6ca2b7acb92c99a2067b6468dd18047bc1`, range `origin/main...d3d03fbb`, `origin/main` = `055b5e6b74f9d4b10f6df54570e33ed2805ae9a8`, merged into the head by `d3d03fbb`. Code read-only; no test run by the auditor; the gate is the lead's, logs in `gi-pricing-plan.local/scratch/sl8071-gate/`.)*

**1. Change set** (`git diff --stat origin/main...d3d03fbb`, 12 paths, +756 −18): `errors.py`, `rating_algorithms.py`, `factors.py`, `compile.py`, `runtime.py`, `03-rating-engine.md`, `roadmap.md`, `INDEX.md`, this ledger, and three test files (`test_rating_gbm_banded_save.py`, `test_rating_gbm_banded_refusal.py`, `test_quote_input_raise_sites.py`). Nothing outside the slice's scope.

**2. Obligations, derived from FD-1754's Disposition items 1-2 and SL-1758's scope block, then evidenced** (verdict per row; the lead's to adopt):
- **(1) compile refusal, per component of a peril structure:** `compile.py` `check_model_call_gbm_factors`, called in `compile_bundle` after `check_model_call_coverage`; pins checked via `fit_result.model_type in GBM_MODEL_TYPES`. Tests: case C and A (xgboost, lightgbm), grouped, exact message. **Met.**
- **(1) save refusal at all three routes:** `rating_algorithms.py` `_refuse_gbm_transformed_factors`, called from `check_model_call_feature_maps`; that function is called from `rating_algorithms.py` (algorithm save) and `sub_graphs.py` (two calls: create and new version). **Met.** A non-existent model saves (R1; test `test_a_model_that_does_not_exist_yet_saves`).
- **(2) keyed on the step, never the pin:** both checks iterate `RatingModelCallStep` only; tests `test_a_banded_gbm_pinned_but_never_called_still_compiles`, `test_a_banded_gbm_with_no_model_call_step_saves`; GLM on banded and GBM on plain Factors still compile and save. **Met.**
- **(3) `GbmFitError` is the step's `MODEL_CALL_FAILED`:** `runtime.py` except tuple; test `test_a_gbm_fit_error_while_scoring_is_the_named_model_call_failure`. **Met.**
- **(4) FR-222 and FR-240 dated amendments, code in the owned-codes list:** `03` lines 110, 140 and the codes list; `RATING_ERROR_CODES` gains the code (test `test_the_code_is_a_rating_error_code`). **Met.**
- **One definition:** `gbm_transformed_factors` and `GBM_MODEL_TYPES` in `factors.py`, used by both checks. **Met.**
- **Raise-site rule (the maintainer 2026-10-17 00:07:43 BST):** the new `_raise_named` site is registered `_INPUT_FREE` (`test_quote_input_raise_sites.py`, `("rating/compile.py","check_model_call_gbm_factors"): 1`), justified by the text carrying only step id, model ref, Factor slug and kind; `test_the_gbm_factor_refusal_message_is_exactly_its_structural_fields` pins the whole text. **Met**, and proven by the gate (section 4).

**3. Red-first record.** All of `a26e9dfe`, `481db4c0`, `d15041b2`, `9001b01e`, `c18133e6`, `e2914d90`, `c5552a39`, `d3d03fbb` are ancestors of the head (`git merge-base --is-ancestor` rc 0 each). `a26e9dfe` (parent `a2f77b2d`) is tests-only (2 files, +482) and an ancestor of the fix `481db4c0`. The ledger's red-by-cause names (6 failed core, 5 failed backend) match the test names in that commit, and its green count (18 = 9 + 9 at `9001b01e`) matches. The red run itself was not re-run by the auditor.

**4. Gate at `d3d03fbb` (tree `72fd9f6c`, clean after: "0 changed path(s)").** From `scratch/sl8071-gate/gate.log`: preflight ok; ruff rc 0, mypy rc 0, import_linter rc 0, req_coverage rc 0, contracts rc 0; frontend install, generate:api, lint, type-check, test, build all rc 0; **audit_docs rc 1** (`audit_docs.log`: FAILED (1): `check 31: gap in the full allocation between 1740 and 8071` only: the working-id gap, expected while 8071/8072 are unminted); **pytest rc 1, `13 failed, 5886 passed, 4 skipped` (0:53:51)**. The 13 FAILED names are the audit-docs-on-the-real-tree cascade of that one check 31 gap (`test_audit_docs_*`, `test_doc_index`, `test_register_lint`, `test_register_owed`, `test_repository_invariants`), and are identical to the 16 Oct gate's (`sl8071-gate-e2914d90-2026-10-16/pytest.log`) except that run's 14th, `test_every_quote_input_raise_site_has_a_sentinel_case`, which is **absent** now: the raise-site red is fixed. Demo `wf-699`: rc 124 as designed (the timeout ends the stack), `journey done in 284s`; the only `FAIL` text in `demo.log` is line 41, a designed refusal (`VALIDATION_HAS_FAILURES`). The 23 backend DB fixture errors of the pre-gate small runs are not present: the gate had its database.

**5. Findings.**
- **F1 (fixed in this commit):** this ledger's GO paragraph and SL-1758's roadmap block said FD-1754 was "to be filed" with severity "the run's". It is HIGH, minted in D18 as FD 1754 (unmerged). Both unmerged slice records are corrected here, citing "FD-1754 (FD 1754 in D18, unmerged)".
- **F2 (owned, no new row):** interaction, spline, polynomial and expression Factors on a GBM may carry the same defect; FD-1754 Disposition item 4 owns it ("for the planner and the maintainer", not read or run). Not widened by this slice.
- **F3 (owned):** real support for a banded GBM in a `model_call` is FD-1754 Disposition item 3, owner WK-673.
- **F4 (disclosed, not this slice's):** the 13 pytest FAILED lines resolve when the working ids are minted at the PR; the re-check is `audit-docs` check 31 green after the mint.

**6. Proposed verdict:** all obligations delivered and evidenced; no requirement left without evidence. Proposal only: acceptance of the merge is the lead's, and the MERGE-ACK line stays pending until the maintainer's dated entry.

**Lead verdict (2026-10-17 13:21:31 BST, the lead, transcript 1b92c2a6):** the auditor's proposal ADOPTED — all obligations delivered and evidenced; spot-verified at d3d03fbb: compile.py:1130 calls check_model_call_gbm_factors; rating_algorithms.py:262 calls _refuse_gbm_transformed_factors; test_quote_input_raise_sites.py:106 registers the new site. MERGE-ACK: not yet given.
