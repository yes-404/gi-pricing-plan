---
id: LG-9900
family: ledger
title: WK-1178 slice SL-1675 — rows whose declared weight is 0 are excluded from the fit and every diagnostic (PL-1674 slice ledger)
status: active
created: 2026-10-12
owner: executor
tree: a83aeef11b104258639be062ef5623593fe88a44
phase: P2
work: WK-1178
slice: SL-1675
plans: [PL-1674]
corrected_by: []
relates: [PL-1674, SL-1543, PL-1542, RL-1263, FR-111, FR-171, FR-183, FR-184, FR-187]
---

# LG-9900 — WK-1178 slice SL-1675: weight-0 rows excluded from the fit and every diagnostic

*(LG-9900 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1675` from PL-1674, base `origin/pl-9886-wk1178-zero-weight-2026-10-12`
`a83aeef11b104258639be062ef5623593fe88a44` (PR #1292, not yet on main at the start; `origin/main`
`604ea084c96efe93f521fb9ba17738e05241e61a`). Times are BST.

**GO:** the lead's from-lead entry "2026-10-12 06:06:16 BST — GO SL-1675 (WK-1178, zero-weight
exclusion; G2 critical path before SL-1543)", on the maintainer's (by delegation) entry
"2026-10-12 05:47:19 BST" (GO + early mint; the T-text correction; DP-Z1 = (a)) and the rule of
"2026-10-12 05:39:20 BST", (i).
**MERGE-ACK:** not yet given.

## Tasks

### Activation (2026-10-12 06:07 BST)

SL-1675 `draft` → `active` (`docs/roadmap.md`); PL-1674 `draft` → `active` (its status line), both
in this commit, as PL-1674's "Hand-off" and the SL-1675 row's activation needs require.

### Task 0 (2026-10-12, base `a83aeef1`)

**Step 1, the site list.** `git grep -n -E 'def (fit_glm|fit_gbm|fit_ebm|compute_diagnostics|compute_gbm_diagnostics|compute_ebm_diagnostics|backtest_model|_partition)\b' -- packages/pricing-core/src` prints `diagnostics.py:338/604/739/1267/1416`, `ebm.py:95`, `gbm.py:603`, `glm.py:523`; `git grep -n '_partition(' -- packages/pricing-core/src` prints the def and the seven calls `diagnostics.py:634/645/790/1300/1309/1443/1452`. That is PL-1674's table with no site beyond it. The two weight readers are `diagnostics._weights` (`:132`) and `gbm._weights` (`gbm.py:235`); `fit_glm` reads the column inline (`glm.py:591-593`) and `fit_ebm` inline (`ebm.py:201-202`).

**Step 2, the refusals at the base** (one severity frame, 600 rows, ONE row with weight `-1` / `null`; scratch script, not committed):

| Arm | negative | null |
|---|---|---|
| `fit_glm` | `GlmFitError` `GLM_FIT_FAILED` ("Sample weights must be non-negative") | `GLM_FIT_FAILED` ("Input contains NaN") |
| `fit_gbm`, xgboost | raw `XGBoostError` ("Weights must be positive values"), no named code | same |
| `fit_gbm`, lightgbm | **no refusal, the fit returns** | **no refusal, the fit returns** |
| `fit_ebm` | `EbmFitError` `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` ("illegal negative sample_weight value") | same code ("sample_weight cannot contain missing values or infinites") |

The LightGBM row is PL-1674 Task 0 Step 2's stop condition; reported to the lead, ruling pending.

**Step 3, the shared-path census** (`git diff --name-only origin/main...origin/<branch>`): `docs/contracts/openapi/generated.json` is touched by `sl-1549-wk675-s7b-compare-backend` and `sl-1669-wk1178-bulk-op-typing`; `docs/roadmap.md` and `docs/INDEX.md` by every branch. `sl-1622-wk690-fix-row` touches `modelling/objectives.py` (not a site of this slice); `sl-1678-wk673-fd1679-guard` touches no code. The later PR re-runs `generate-contracts.py` after the earlier merges.

**Plan discrepancy.** Task 1 says to add `"rows_excluded_zero_weight": 0` to "§4's Diagnostics example (`:1700-1711`, the `train` partition)". `02` §4 has no train-partition example; the only `PartitionDiagnostics` example is §4.12's backtest `partition` (`:1698-1711`), so the field is added there.

### Task 1, the spec (2026-10-12)

FR-111's row gains the T-text of PL-1674 Task 1, copied by script from the plan's blockquote (so verbatim, including the 05:47:19 correction), and §4.12's partition example gains `rows_excluded_zero_weight` with the sentence under it. `audit-docs` fails only check 31.

### Ruling on Task 0 Step 2 and what it changed (2026-10-12)

The maintainer's (by delegation) entry "2026-10-12 06:10:04 BST — SL-1675 STOP: (A) ACCEPTED, as ONE refusal for ALL four arms; the LightGBM silent fit is an FD, HIGH PROVISIONAL, discharged by SL-1675" (relayed by the lead, from-lead "2026-10-12 06:10:29"): the weight helper "refuses a negative or null declared weight BEFORE any backend sees it, for GLM, XGBoost, LightGBM and EBM alike", one code; "the executor first greps the 02 error catalogue for an existing code meaning "declared weight invalid" and reuses it if one fits; else it adds ONE new code". "(C) is refused". "Acceptance 6 becomes red-first on all four arms".

- **The catalogue grep.** `grep -n -E "[A-Z]+_(WEIGHT|WEIGHTS)[A-Z_]*|WEIGHT_[A-Z_]+"` over `docs/specs`, `packages`, `backend/src` finds only `CREDIBILITY_WEIGHTED`; `02`'s "Error codes owned by this module" list (`02-modelling.md`) names no weight code. None fits, so ONE new code is added: **`DECLARED_WEIGHT_INVALID`**.
- **The code is registered in `backend/src/app/errors.py` (`MODELLING_ERROR_CODES`).** This is one line in `backend/src`, which PL-1674's Global Constraints keep unchanged, and the 06:10:04 write set names only "the catalogue line and those test updates". It is not optional: `model_handlers.py:395` maps `exc.code` into a `PlatformError`, and `errors.py:137`'s own comment records that an unregistered code raises `ValueError: unknown error code` from inside the error path; `backend/tests/test_spec_hash.py:158` asserts every code `pricing-core` raises is registered. Reported to the lead.
- **Tests that assert a bad weight under `GLM_FIT_FAILED`** (the 06:10:04 list-them clause): `git grep -n "non-negative\|malformed_weight\|Sample weights" -- packages backend/tests` prints one, `packages/pricing-core/tests/test_glm.py` `test_a_malformed_weight_column_is_named_rather_than_a_stack_trace`. It is updated to `DECLARED_WEIGHT_INVALID`. `test_a_response_outside_the_family_domain_is_named_rather_than_a_stack_trace` keeps `GLM_FIT_FAILED` (a response, not a weight).
- **All-zero book.** PL-1674 Task 2 says each arm refuses "with its existing code". The helper now owns the weight refusals, so the all-zero refusal uses the same one code, with a message saying every row was excluded for weight 0. No second code is added.

### Reds, on `a83aeef1` + the spec commit (tests only, no source change) — 2026-10-12

Command: `uv run pytest -q packages/pricing-core/tests/<file> -k <names> -p no:cacheprovider`.

**R1, GLM, by cause** (`test_a_weight_zero_row_never_reaches_the_family_domain_check`):
- `[response-0]`: `pricing_core.modelling.glm.GlmFitError: glum refused the fit: Some value(s) of y are out of the valid range for familyGammaDistribution. The response, the weights or the offset are outside what this family and link can …` (code `GLM_FIT_FAILED`, the Gamma domain; the cause PL-1674 requires).
- `[response-null]`: `GlmFitError: glum refused the fit: Input y contains NaN. …` (`GLM_FIT_FAILED`; a null response is NaN to `glum`).

**R1-GBM:** LightGBM RED, `test_a_weight_zero_row_does_not_shape_the_boosters_bins[lightgbm]`: `AssertionError: lightgbm: max rel diff 0.1285983078301599` (the full-book fit's predictions on the claims-only rows differ from the claims-only fit's by up to 12.9%). **XGBoost is a GUARD, green on main** (`[xgboost]` PASSED): XGBoost's weighted quantile sketch already gives zero-weight rows no say in the bins, so that arm's test records the property, not a red.

**R1-EBM RED:** `test_a_weight_zero_row_does_not_shape_the_ebms_bins` FAILED on main (the full-book EBM's predictions differ from the claims-only fit's).

**Acceptance 6, red first on all four arms, by cause** (`DECLARED_WEIGHT_INVALID` expected; one row at weight `-1` or null):
- GLM `[negative]`, `[null]`: `AssertionError: assert 'GLM_FIT_FAILED' == 'DECLARED_WEIGHT_INVALID'`.
- XGBoost `[negative-xgboost]`, `[null-xgboost]`: `xgboost._c_api.XGBoostError: … Check failed: valid: Weights must be positive values.` (raw library error, no `GbmFitError`).
- LightGBM `[negative-lightgbm]`, `[null-lightgbm]`: `Failed: DID NOT RAISE GbmFitError`.
- EBM `[negative]`, `[null]`: failing on main with `EbmFitError` code `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` ("illegal negative sample_weight value" / "sample_weight cannot contain missing values or infinites").
- All-zero book: GLM `AssertionError: assert 'GLM_FIT_FAILED' == 'DECLARED_WEIGHT_INVALID'`; XGBoost `XGBoostError … weights must contain at least one non-zero value`; LightGBM `DID NOT RAISE GbmFitError`; EBM fails likewise.

**Guards, green on main:** `test_only_an_exact_zero_weight_is_excluded` (a weight of `1e-300` is a row: the nil settlement is read, `GLM_FIT_FAILED` "out of the valid range"); `test_a_zero_exposure_offset_is_still_refused_it_is_not_a_weight` (`OFFSET_REQUIRED_FOR_FREQUENCY`).

**R2** (`test_a_weight_zero_row_is_not_counted_in_a_partitions_rows_or_ae`): `AssertionError: assert 2000 == 1714` (`rows` counts the 286 weight-0 train rows).

**R3, the `model_fields` parity walk, all four entry points** (train 2,000 rows losing 286 and holdout losing a different number; `walk` descends `model_fields` and dataclass fields, floats at `rel 1e-9`):
- `compute_diagnostics`: `.universal.train.rows: 2000 != 1714`, `.universal.train.ae_overall: 1.008835425205613 != 0.9999999879620569`, `.universal.train.ae_by_factor[0].actual: 55.0 != 46.0`, `…exposure_years: Decimal('629.000396') != Decimal('544.631899')`, and onward through every cell.
- `compute_gbm_diagnostics` (XGBoost): `.universal.train.rows: 2000 != 1714`, `ae_overall: 0.6363711049707501 != …`.
- `compute_ebm_diagnostics`: `.universal.train.rows: 1500 != 1285`.
- `backtest_model` (`req("FR-187")`): `.partition.rows: 1000 != 667`.
- The count assertion (`rows_excluded_zero_weight` equals the rows removed per partition and is 0 on the claims-only run) cannot be reached on main, where the field does not exist.

**Write-set note.** The backtest R3 case sits in `test_diagnostics.py` with the shared walker, not in `test_backtests.py`, so the walker is not duplicated.

## PRs

(none yet; the slice's one PR carries this ledger.)
