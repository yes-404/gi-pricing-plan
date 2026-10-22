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

All runs `run-small.sh` / the single-file vitest guard, under the `small-test` flock; whole files, no `-k`. Logs are copied to `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/` (originals `/tmp/exec-a-*.log`, which a reboot clears); each opens with `HEAD=`. The closure list is `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-closure.txt`, the pricing-core part `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-pk.txt`.

**Static at head `cd9b3a9a`→`b08fbef6`:** `ruff check` on the 9 changed `.py` files: `All checks passed!`; `mypy`: `Success: no issues found in 244 source files`; `lint-imports`: `Contracts: 4 kept, 0 broken.`; `generate-contracts.py --check`: rc 0, `54 generated contracts match the models`; `pnpm install --frozen-lockfile` and `generate:api` rc 0.

**RED, Python** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-red2.log`): `HEAD=fc9107a803c0bf7012364abdbd91de500b643a18` plus an uncommitted overlay of `test_diagnostics.py` and `test_glm.py` from `b08fbef6`; files `test_diagnostics.py`, `test_glm.py`, `test_glm_spec_theta.py`: `21 failed, 78 passed, 1 warning in 10.66s`. By cause: `TypeError: unit_deviance() got an unexpected keyword argument 'theta'` (1); `AttributeError: 'GlmDiagnostics' object has no attribute 'monotonicity'` (5, one is the banded test: "absence red"); `GlmFitError: glum refused the fit: The family must be an instance of class ExponentialDispersionModel` and the same `ValueError` for `negative_binomial` and `inverse_gaussian` (6); `ImportError: cannot import name 'glum_family'` (2); `Failed: DID NOT RAISE ValueError` (1) and `DID NOT RAISE ValidationError` (9). The five other families' fit tests and every pre-existing test pass. *First run (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-red1.log`, `HEAD=fc9107a8`, no overlay): 25 failed, 73 passed; five of the 25 were `KeyError: 'area[urban]'`, a defect in the new test (the base level is the most-exposed one, and `urban` was sometimes it), fixed in `b08fbef6` by making `rural` the majority.*

**Property red, negative control** (test written after the code; `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-nc.log`): `HEAD=b08fbef6a915deb3710d43964ed7733d0726ef06`, scratch mutation `for label in sorted(bandings[factor.banding_id].labels)` in `_glm_monotonicity` (`diagnostics.py | 2 +-`), `test_diagnostics.py`: `1 failed, 30 passed in 8.76s`, `FAILED …::test_a_banded_glm_factor_is_swept_in_band_order_not_label_order`, `AssertionError: assert False is True … holds=False, worst_violation=0.12444261908499157`; restored with `git checkout -- .`, porcelain 0.

**RED, frontend** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-fe-red.log`): `HEAD=2cb4ab3bf4359488315b44390e877ea1a2cf2a71`, load1 4.91, `src/views/__tests__/ModelSpecBuilderView.test.ts` alone: `Test Files  1 failed (1)`, `Tests  1 failed | 10 passed (11)`, `Unable to find a label with the text of: /theta/i`.

**GREEN at `b08fbef6a915deb3710d43964ed7733d0726ef06`:** `test_diagnostics.py`+`test_glm.py`+`test_glm_spec_theta.py` `99 passed, 1 warning in 10.01s`; frontend file `Test Files  1 passed (1)`, `Tests  11 passed (11)`; import-closure set (`grep -lE "GlmSpec|GlmDiagnostics|fit_glm|compute_diagnostics|compare_models|backtest_model|unit_deviance|deviance|from pricing_core.modelling|import pricing_core.modelling|DiagnosticsResult" -r packages/*/tests backend/tests`, 75 files; 45 under `packages/`, 30 under `backend/tests` DB-backed): model-schema 9 files `54 passed`, `36 passed`, `30 passed`; `test_backtests`+`test_bandings`+`test_comparison` `47 passed in 7.68s`. **Pricing-core closure, all 45 files (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/green-closure3.log` for files 13-45, run after W2 END at `HEAD=44be7b58877c93d6a9ac5aeb85e29af746a344fe`, whose only changes since `b08fbef6` are under `docs/ledgers`; load1 2.21-4.97 printed per batch):** `60 passed`, `51 passed`, `227 passed, 4 warnings`, `72 passed, 4 skipped`, `47 passed`, `136 passed`, `73 passed`, `29 passed`, `53 passed`, `21 passed`, `53 passed`, each `rc=0`, 0 failed. **DB window, 2026-10-22T16:14:19Z to 16:31:01Z** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/db-window.log`; script `db-window-commands.sh` v3; `HEAD=08bbecac01e8e75e2b394aa3f7841f294f3832ac`; `GIP_GATE_SLOT=unset`; redis `PUBSUB CHANNELS 'gip:switch*'` = `gip:switch:local:local:{prod,uat,dev}`, each NUMSUB 2, under the maintainer's extension of the switch exception, to-lead 17:12:17, while FD-1838's gate ran). `createdb gipricing_sl-8166_1c95b45f` (hyphenated) rc=0; `alembic upgrade head` rc=0. **A0 (read-only):** `gipricing` 0; `gip` database absent; the fresh slice DB 0 (fresh DB, 0 by construction, not evidence). `gipricing` is the migrations-only template, so its 0 shows no NB row in the template and says nothing of other deployments. **Backend closure, 30 files, 10 `run-small.sh` runs, every rc=0, nothing failed:** `94 passed, 21 warnings`; `187 passed, 2 skipped, 1 warning`; `62 passed, 1 warning`; `35 passed, 10 warnings`; `49 passed, 1 warning`; `41 passed, 8 warnings`; `46 passed, 1 warning`; `60 passed, 11 warnings`; `41 passed, 1 warning`; `30 passed, 2 warnings`. `dropdb rc=0`; leftover databases like `sl-8166`: 0. No failure, so no read against the switch overlap was needed.

### Audit

Not yet.

### Build log

- **2026-10-22 — design.** `glm_family` / `r_theta_from_glum_theta` in `glm.py` are the only place the family names and θ conversion are written; `unit_deviance`/`deviance` take `theta` and raise for NB without it; `_theta_of` threads it to the partition, type-III, backtest and comparison call sites. `_glm_monotonicity` reuses `_resolved_axis`, `_representatives` and `_skipped_ids`; a numeric identity factor is swept over its 5th–95th percentile grid and a banding in its own `labels` order; operands, expression factors and unordered factors are recorded as omissions. A GBM-style `_sweep` reuse was not taken: it is bound to `predict_gbm` and sorts labels.
- **2026-10-22 — DEVIATION, disclosed (lead 26):** the executor's small-test pytest (pid 1798645, `sl-8166`, the loop batch `test_demo_b4_premium.py test_diagnostics.py test_ebm.py`) held `/tmp/slots/small-test` at 16:22 BST, during W2's ALONE window and after the lead's "W2 START". The loop had started the batch before the message was read, and the executor then stopped the loop; the lead reports W2 is a functional red, so no harm. Nothing of the executor's ran after.
- **2026-10-22 — `pkill -f <pattern>` was used to stop that loop** and also ended the executor's own shell; a pattern kill can hit other seats' processes and is not to be used (lead 26): only own PIDs are stopped. The batch re-runs after W2 END.

## PRs

(none yet)
