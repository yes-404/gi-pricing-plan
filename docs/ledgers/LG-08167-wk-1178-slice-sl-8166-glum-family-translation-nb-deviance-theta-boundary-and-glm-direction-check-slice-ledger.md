---
id: LG-8167
family: ledger
title: WK-1178 slice SL-8166 — PL-8162 slice A, the glum family translation, the NB deviance, the θ boundary and the GLM direction check, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: b08fbef6a915deb3710d43964ed7733d0726ef06
phase: P2
work: WK-1178
slice: SL-8166
plans: [PL-8162]
corrected_by: []
relates: [PL-8162, SL-8166, FD-1723, FR-89, FR-110]
---

# LG-8167 — WK-1178 slice SL-8166: PL-8162 slice A

*(Working ids SL 8166 and LG 8167, reserved by lead 26 on 2026-10-22; unminted.)*

**GO:** to-lead.md "2026-10-22 16:02:49 BST — Maintainer: PL 8162 (FD-1723's residual limbs) ACCEPTED; …" (slices C, then A, then B).
**MERGE-ACK:** not yet given. Slice A merges after slice C (its FR-110 clauses).

## Tasks

Base: `origin/main` `f3462d8f`. Branch `sl-8166-wk1178-pl8162-a`, worktree `.claude/worktrees/sl-8166`.

### Scope

`PL-8162` slice A: FR-110 (glum family-name translation for all seven `GlmSpec.family` members; the NB θ declared and required; the NB deviance) and FR-89 (the GLM direction check, `GlmDiagnostics.monotonicity` and `monotonicity_omitted`), the builder's θ input. **Where the rulings of to-lead.md "2026-10-22 16:02:49 BST" differ from the plan draft @6b1de3a9, the rulings govern:** θ is R/MASS `glm.nb`'s (variance μ + μ²/θ, ruling 3), converted once to glum's α = 1/θ_R; the plan's DP-T (a)/A-R3 text states glum's form and is brought into line by exec-c at its activation (lead 26, 2026-10-22). `power(k)` is struck in slice C (ruling 1): no DP-K build. DP-M (b) adopted as recommended. FR-110 θ/NB spec text is slice C's; FR-89 text is here.

**NB-fits-today (ruling 2), by code reading only:** no path. Only `ModelRow(...)` constructor in `backend/src` is `platform/modelling.py:561` (`reserve_model`, status draft, no `fit_result`); `fit_result` is written only at `worker/model_handlers.py:573` (after `fit_glm`), `:1146` (surrogate; `approximation_spec` hardcodes `family="gamma"`, `pricing_core/modelling/transparency.py:113`) and `platform/modelling.py:947`; readers refuse an unfitted row (`_resolve_candidate` `model_handlers.py:691`, backtest `:1232` `MODEL_NOT_FITTED`); migrations only `UPDATE models SET status/diagnostics_id`; no import route in `api/models.py`; no NB in `examples/` or `scripts/`. At the base glum raised for the underscore names (`glum._glm.get_family` accepts `negative.binomial`, `inverse.gaussian` only). A draft NB spec can be stored. **Owed (DB window):** the read-only count of stored draft NB rows.

### Task list

| Task | Commit(s) |
|---|---|
| A1 reds (A-R1, A-R2, A-R3, A-R4, builder) | `c885191c`, `b44f8d3c`, `7a379e25`, `fc9107a8`, `2cb4ab3b`; banded test `9e5cf93d` (after the code: negative control below); fixture fix `b08fbef6` |
| A2 spec (FR-89 dated amendment) | `db41422c` |
| A3 model-schema | `e29cefcc` |
| A4/A5 pricing-core, A6 builder | `53d0433f` |
| static fixes; contracts regenerated | `cd9b3a9a`, then the `chore(contracts)` commit |

### Gate

All runs `run-small.sh` / the single-file vitest guard, under the `small-test` flock; whole files, no `-k`. Logs in `/tmp/exec-a-*.log`, each opening with `HEAD=`.

**Static at head `cd9b3a9a`→`b08fbef6`:** `ruff check` on the 9 changed `.py` files: `All checks passed!`; `mypy`: `Success: no issues found in 244 source files`; `lint-imports`: `Contracts: 4 kept, 0 broken.`; `generate-contracts.py --check`: rc 0, `54 generated contracts match the models`; `pnpm install --frozen-lockfile` and `generate:api` rc 0.

**RED, Python** (`/tmp/exec-a-red2.log`): `HEAD=fc9107a803c0bf7012364abdbd91de500b643a18` plus an uncommitted overlay of `test_diagnostics.py` and `test_glm.py` from `b08fbef6`; files `test_diagnostics.py`, `test_glm.py`, `test_glm_spec_theta.py`: `21 failed, 78 passed, 1 warning in 10.66s`. By cause: `TypeError: unit_deviance() got an unexpected keyword argument 'theta'` (1); `AttributeError: 'GlmDiagnostics' object has no attribute 'monotonicity'` (5, one is the banded test: "absence red"); `GlmFitError: glum refused the fit: The family must be an instance of class ExponentialDispersionModel` and the same `ValueError` for `negative_binomial` and `inverse_gaussian` (6); `ImportError: cannot import name 'glum_family'` (2); `Failed: DID NOT RAISE ValueError` (1) and `DID NOT RAISE ValidationError` (9). The five other families' fit tests and every pre-existing test pass. *First run (`/tmp/exec-a-red1.log`, `HEAD=fc9107a8`, no overlay): 25 failed, 73 passed; five of the 25 were `KeyError: 'area[urban]'`, a defect in the new test (the base level is the most-exposed one, and `urban` was sometimes it), fixed in `b08fbef6` by making `rural` the majority.*

**Property red, negative control** (test written after the code; `/tmp/exec-a-nc.log`): `HEAD=b08fbef6a915deb3710d43964ed7733d0726ef06`, scratch mutation `for label in sorted(bandings[factor.banding_id].labels)` in `_glm_monotonicity` (`diagnostics.py | 2 +-`), `test_diagnostics.py`: `1 failed, 30 passed in 8.76s`, `FAILED …::test_a_banded_glm_factor_is_swept_in_band_order_not_label_order`, `AssertionError: assert False is True … holds=False, worst_violation=0.12444261908499157`; restored with `git checkout -- .`, porcelain 0.

**RED, frontend** (`/tmp/exec-a-fe-red.log`): `HEAD=2cb4ab3bf4359488315b44390e877ea1a2cf2a71`, load1 4.91, `src/views/__tests__/ModelSpecBuilderView.test.ts` alone: `Test Files  1 failed (1)`, `Tests  1 failed | 10 passed (11)`, `Unable to find a label with the text of: /theta/i`.

**GREEN at `b08fbef6a915deb3710d43964ed7733d0726ef06`:** `test_diagnostics.py`+`test_glm.py`+`test_glm_spec_theta.py` `99 passed, 1 warning in 10.01s`; frontend file `Test Files  1 passed (1)`, `Tests  11 passed (11)`; import-closure set (`grep -lE "GlmSpec|GlmDiagnostics|fit_glm|compute_diagnostics|compare_models|backtest_model|unit_deviance|deviance|from pricing_core.modelling|import pricing_core.modelling|DiagnosticsResult" -r packages/*/tests backend/tests`, 75 files; 45 under `packages/`, 30 under `backend/tests` DB-backed): model-schema 9 files `54 passed`, `36 passed`, `30 passed`; `test_backtests`+`test_bandings`+`test_comparison` `47 passed in 7.68s`. *Remaining pricing-core batches and the backend set: see the build log when run.*

### Audit

Not yet.

### Build log

- **2026-10-22 — design.** `glm_family` / `r_theta_from_glum_theta` in `glm.py` are the only place the family names and θ conversion are written; `unit_deviance`/`deviance` take `theta` and raise for NB without it; `_theta_of` threads it to the partition, type-III, backtest and comparison call sites. `_glm_monotonicity` reuses `_resolved_axis`, `_representatives` and `_skipped_ids`; a numeric identity factor is swept over its 5th–95th percentile grid and a banding in its own `labels` order; operands, expression factors and unordered factors are recorded as omissions. A GBM-style `_sweep` reuse was not taken: it is bound to `predict_gbm` and sorts labels.
- **2026-10-22 — `pkill -f` killed the executor's own loop** during W2; no pytest was left running; batch 2 re-runs.

## PRs

(none yet)
