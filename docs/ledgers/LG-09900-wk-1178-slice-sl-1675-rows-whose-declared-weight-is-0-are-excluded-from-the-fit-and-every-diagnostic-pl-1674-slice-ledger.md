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

## PRs

(none yet; the slice's one PR carries this ledger.)
