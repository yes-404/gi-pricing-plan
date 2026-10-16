---
id: LG-8072
family: ledger
title: WK-1178 slice SL-8071 — FD-8073, a model_call refuses a GBM fitted on a banded or grouped Factor, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-16
owner: executor
phase: P2
work: WK-1178
slice: SL-8071
plans: []
corrected_by: []
relates: [SL-8071]
---

# LG-8072 — WK-1178 slice SL-8071: a model_call refuses a GBM on a banded or grouped Factor

**GO:** the maintainer's (by delegation) entry "2026-10-16 10:59:28 BST — Maintainer: the GBM model_call defect — the reading is accepted; disposition fixed now, severity on the run", item 1, in `to-lead.md`; the probe evidence is the lead's entry "2026-10-16 10:59:07 BST" in `from-lead-2026-10-09.md`. The finding is FD 8073 (to be filed after the probe run, with the run's result quoted; no severity on a reading).
**Gate:** none granted. The box was held by an ALONE latency gate when this was written; every run is owed (below).
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Branch `sl-8071-wk1178-gbm-banded-refusal-2026-10-16`, worktree `.claude/worktrees/sl-8071`, cut from `origin/main` `a2f77b2d`.

- **Red-first commit (tests only):** `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py` (compile: case C, case A, grouped, controls, the negative "pinned but never called" test, the runtime `GbmFitError`) and `backend/tests/test_rating_gbm_banded_save.py` (save: cases A and C, grouped, peril component, controls, the no-`model_call` negative).
- **Fix commit:** `gbm_transformed_factors` and `GBM_MODEL_TYPES` in `pricing_core/modelling/factors.py` (the one definition); `check_model_call_gbm_factors` in `pricing_core/rating/compile.py`, called after `check_model_call_coverage`; `_refuse_gbm_transformed_factors` in `app/platform/rating_algorithms.py`, called from `check_model_call_feature_maps`; the code in `RATING_ERROR_CODES`; `GbmFitError` in the `model_call` handler's except tuple (`rating/runtime.py`).
- **Why `GbmFitError` is caught by name rather than made a `ModellingError`:** `GbmFitError`, `PredictionError` and `ModellingError` are three direct `RuntimeError` subclasses. Re-parenting would change what `except ModellingError` catches in `backend/src/app/platform/prediction.py`, `transformations.py` and the worker handlers, which catch and map it on their own terms.
- **Spec:** `03` FR-222 (dated "Known gap" amendment, owner WK-673) and FR-240 (pointer), and the owned-codes list entry.
- **Scope checks by reading:** the refusal is keyed on the `model_call` step, never on the pin (WF-699 pins the banded GBM at `examples/fremtpl2/journey.py:664`, recompiles at `:743-745`, and skips B4 and C1' at `:78-79`); NFR-489's bench GBM (`scripts/bench-rating.py`, raw `f0..f7`, no Factors) has an empty `pin.factors`, so it is not refused.

## PRs

Not opened yet; the lead opens the PR.

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
