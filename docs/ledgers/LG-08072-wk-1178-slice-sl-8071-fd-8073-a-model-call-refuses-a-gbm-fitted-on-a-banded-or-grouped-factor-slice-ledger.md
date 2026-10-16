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

None run. Each is NOT RUN, not green: the new pricing-core test file and the new backend test file through `run-small.sh` (red on the tests commit, green on the fix commit); the neighbouring `test_rating_runtime.py`, `test_rating_compile_completeness.py` and `test_rating_glm_model_call.py`; `ruff check`, `mypy`, `lint-imports`; `doc-index.py`, `audit-docs.py`, `doc-index.py --check`, `register-lint.py` under the gate-2 flock; worktree setup (`uv sync --all-packages`); the full gate on the lead's grant.
