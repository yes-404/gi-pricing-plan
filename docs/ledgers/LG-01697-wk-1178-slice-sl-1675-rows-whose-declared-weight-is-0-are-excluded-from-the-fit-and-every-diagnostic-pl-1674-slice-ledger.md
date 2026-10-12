---
id: LG-1697
family: ledger
title: WK-1178 slice SL-1675 — rows whose declared weight is 0 are excluded from the fit and every diagnostic (PL-1674 slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 2a81974184ee405536fb43d30f59a990b3953669
phase: P2
work: WK-1178
slice: SL-1675
plans: [PL-1674]
corrected_by: []
relates: [PL-1674, SL-1543, PL-1542, RL-1263, FD-1698, FR-111, FR-171, FR-183, FR-184, FR-187]
---

# LG-1697 — WK-1178 slice SL-1675: weight-0 rows excluded from the fit and every diagnostic

*(Minted 2026-10-12 as LG-1697 from working id 9900, at the mint turn.)* Executed by
`executor-sl1675` from PL-1674, base `origin/pl-9886-wk1178-zero-weight-2026-10-12`
`a83aeef11b104258639be062ef5623593fe88a44` (PR #1292, not yet on main at the start; `origin/main`
`604ea084c96efe93f521fb9ba17738e05241e61a`). Times are BST.

**GO:** the lead's from-lead entry "2026-10-12 06:06:16 BST — GO SL-1675 (WK-1178, zero-weight
exclusion; G2 critical path before SL-1543)", on the maintainer's (by delegation) entry
"2026-10-12 05:47:19 BST" (GO + early mint; the T-text correction; DP-Z1 = (a)) and the rule of
"2026-10-12 05:39:20 BST", (i).
**Audit:** written 2026-10-12 by `auditor-sl1675` (sonnet, medium) over `origin/main...origin/sl-1675-wk1178-zero-weight`, PR #1300 head `5a5c9e8f08cbbec689624cfab83874df1b676098`; scope derived from PL-1674's Acceptance Standard, then evidenced. **Verdicts are proposals; the lead's.** Ledger SHAs `893f96f5 ba89c87d 6aca576c c6bb0d95 a83aeef1 f1399e6d 12298bb9 4f31b6fc`: each `git merge-base --is-ancestor <sha> 5a5c9e8f` exits 0. **Not re-executed by this audit:** no pytest was run, because `gate-1` was held by another slice's full pytest (SL-1549) when I started and the auditor charter bars a heavy run beside a held slot. Test claims below are from reading each test's asserts at the head plus the LG's quoted reds and `~/gi-pricing-plan.local/scratch/sl1675/logs/` (run on `f1399e6d`, not on this head).

| PL-1674 Acceptance | Evidence | Proposed verdict |
|---|---|---|
| 1 docs checks | `audit_docs.log`: `FAILED (2)`, both check 31 (1675→9900, 9900→9902); both closed by the mint. On the merge tree the gap is now 1680→1697 until #1296–#1299 merge; CI is NOT green on this head and is not called green here. | delivered; merge-tree run owed |
| 2 no requirement range | unchanged since the mint; no new plan edit in the range | delivered |
| 3 spec first | `6aca576c` (FR-111 clause) precedes `ba89c87d` (code); `grep -n 'excluded from the fit and from every diagnostic' docs/specs/02-modelling.md` hits row 143. T-text carries the 05:47:19 replacement ("which is intended: a row with no information should not shape them" 1 hit; "leaves every estimate unchanged" 0 hits) | delivered (see F2) |
| 4 severity full-book fit | `test_glm.py::test_a_weight_zero_row_never_reaches_the_family_domain_check[response-0/response-null]` asserts coefficients, std errors at `abs=1e-10` and dispersion, GLM without CV only (stated in the docstring); red quoted in LG is `GLM_FIT_FAILED`, glum "out of the valid range for familyGammaDistribution" (the domain cause) and "Input y contains NaN" | delivered, red by cause (quoted, not re-run) |
| 5 diagnostics | R2 `test_a_weight_zero_row_is_not_counted_in_a_partitions_rows_or_ae` (LG red `2000 == 1714`); R3 `_walk` descends `model_fields` and dataclass fields, final assert `counts == {path: (removed, 0)}`, one test each for GLM, GBM, EBM, and `test_a_backtest_excludes_weight_zero_rows_and_reports_the_count` (`req FR-187`) = all four entry points. Source: `drop_zero_weight_rows` at the entry of `compute_diagnostics`, `backtest_model`, `compute_gbm_diagnostics`, `compute_ebm_diagnostics`; `_partition` takes `excluded_zero_weight` from the caller | delivered |
| 6 refusals loud | one code `DECLARED_WEIGHT_INVALID` for GLM, XGBoost, LightGBM, EBM (`weights.py` `require_usable_weights`, negative / null / non-finite); tests `test_an_unusable_weight_is_refused_by_the_weight_code*` on all four arms; reds quoted by cause in the LG (LightGBM "DID NOT RAISE", XGBoost raw `XGBoostError`, EBM `EBM_MONOTONE_CONSTRAINT_INCOMPLETE`, GLM wrong code); guard `OFFSET_REQUIRED_FOR_FREQUENCY` and exact-zero guard (`1e-300` is a row) present | delivered |
| 7 contract | `PartitionDiagnostics.rows_excluded_zero_weight: int \| None = Field(default=None, ge=0)`; `model-schema/tests/test_partition_zero_weight_count.py` (stored partition without the field validates; `None` is not `0`; negative refused); hand-authored `diagnostics.schema.json` gains the property; `contracts.log` "48 generated contracts match the models" | delivered |
| 8 gate on the merge tree | gate ran on `f1399e6d`: 13 pytest failures, every one in the lead-read list, all check-31 allocation gaps; frontend half green; `ruff`, `mypy`, `import_linter` (4 kept, 0 broken), `req_coverage`, `contracts` rc 0. Spot-check: 13 `FAILED` lines in `pytest.log`; `audit_docs.log` names only check 31. Not run on `5a5c9e8f` | delivered at `f1399e6d`; merge-tree run owed (F3) |

**Reds by cause (read from the LG; not re-measured):** R1 GLM = Gamma domain / NaN y; R1-GBM LightGBM RED (max rel diff 12.86%), XGBoost correctly labelled GUARD; R1-EBM premise correction recorded (interpret refuses a zero weight outright on main, so the red is the refusal, not differing predictions); R2 `2000 == 1714`; R3 four entry points, each with its first diffs quoted; Acceptance 6 red on all four arms; non-finite reds disclosed as measured by emulation (helper patched to a no-op), all-zero reds on the real base (`893f96f5`).

**Spec = code:** FR-111 row contains the 06:37:28 sentence verbatim ("A negative, null or non-finite weight is refused (`DECLARED_WEIGHT_INVALID`), and so is a weight column that is 0 on every row, which would leave nothing to fit."), with a dated note that it replaces the 6aca576c sentence. `02` §5.1 code list (line 2111) and the dated `DECLARED_WEIGHT_INVALID` note (line 2187) present. §4.12 example carries `"rows_excluded_zero_weight": 0` and the null-on-old-artifact sentence (line 1717).
**pricing-core standalone:** `weights.py` imports only `model_schema`, `numpy`, `polars`, stdlib; `lint-imports` 4 kept per the gate log. **backend/src:** `git diff --stat origin/main...HEAD -- backend/src frontend` = one file, `backend/src/app/errors.py`, 7 insertions (the one registered code plus its comment), accepted at the 06:17:27 maintainer (by delegation) entry and the lead's 06:17:07; `model_handlers.py` and `frontend/` untouched. **Write set:** 24 files; every one is in PL-1674's write set or an accepted widening (errors.py; `docs/findings` and `docs/ledgers` for FD-1698/LG-1697; generated contracts). `test_backtests.py` listed in the plan is unused by design (walker shared in `test_diagnostics.py`, stated in the LG). **Register:** `git diff origin/main...HEAD -- docs/findings/register.md` = exactly 1 added row, 0 removed. **Barred word:** 0 hits in the range diff.

**Findings (none blocks a merge):**
- **F1, LOW, `docs/roadmap.md` SL-1675 closing line, and the header of this ledger:** the roadmap line still reads "Audit: pending" and this ledger's "MERGE-ACK: not yet given" is still true; with this audit filed the roadmap line is stale. The lead updates it at the merge turn (a one-phrase edit; not made here, outside the brief's write set).
- **F2, LOW, spec-before-code order for the two added refusals:** the code refusing non-finite and all-zero weights is in `ba89c87d`; the FR-111 sentence naming them is in `12298bb9`, a later commit on the same unmerged branch. The 06:37:28 maintainer (by delegation) entry ordered exactly this forward commit, and the merged tree satisfies "spec = code" and "spec before or with code" for the squash. Recorded so the ordering is not read as accidental.
- **F3, LOW, gate tree:** the gate evidence is at `f1399e6d`; `5a5c9e8f` adds a main merge and the mint. The 13 failures are expected to pass once ids 1680–1696 are on main; not yet run on the merge tree. The lead's check-31-only acceptance (08:30:37) stands on the logs I read.
- **F4, observation, no defect claimed:** `fit_gbm` runs the helper on the holdout too, so an all-zero-weight holdout refuses the whole fit with `DECLARED_WEIGHT_INVALID` ("every row of the holdout was excluded"). I found no test naming that case. If intended it merits one line in FR-111; otherwise a follow-on.

**Proposed verdicts:** all eight Acceptance items delivered (6 and 8 with the F3 caveat); no requirement without evidence; F1 for the lead, F2/F3/F4 for the record; FD-1698 text conforms (HIGH, WK-1178, VR-ACT-8 and the `is_not_null()` gap cited, discharged by SL-1675's merge); SL-1675 closing acts present (status `closed` with dated line; LG-1697 `closed`; PL-1674 `active` as check 33 requires). Proposed: ACK-able once #1296–#1299 are on main and the merge-tree docs/pytest run is clean.
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

**Lead-accepted widening and plan citation error** (the lead's from-lead entry "2026-10-12 06:17:07 BST", accepting the reds at `893f96f5`): (1) the one-line registration in `backend/src/app/errors.py` is the code side of the catalogue line under the maintainer's (by delegation) 06:10:04 widening; the lead said YES to it. (2) PL-1674 Task 1's citation of "§4's Diagnostics example (`:1700-1711`, the `train` partition)" is a **plan citation error**: no such train-partition example exists in `02` §4, the only `PartitionDiagnostics` example is §4.12's backtest `partition`; the lead accepted the §4.12 placement.

**The tests that assert `GLM_FIT_FAILED` for a bad weight** (06:10:04's "list every test", stated command, run at `a83aeef1` and re-run at the green head): `git grep -n -E 'GLM_FIT_FAILED|non-negative|Sample weights' -- packages/pricing-core/tests backend/tests` prints `test_glm.py` `test_a_response_outside_the_family_domain_is_named_rather_than_a_stack_trace` (a nil *response*, not a weight; unchanged) and `test_glm.py` `test_a_malformed_weight_column_is_named_rather_than_a_stack_trace` (a negative weight; updated to `DECLARED_WEIGHT_INVALID`), plus `test_tweedie_density.py` `y must be non-negative` (a different function, unrelated). No `backend/tests` file asserts it. The new `test_only_an_exact_zero_weight_is_excluded` asserts `GLM_FIT_FAILED` for a **response** outside the Gamma domain (a weight of `1e-300` is a row), and is not a bad-weight test.

**FD-1698** (minted from working id 9902; limb 1 HIGH, limbs 2 and 3 LOW; owner WK-1178; discharged by this slice) is filed in this branch: `docs/findings/FD-01698-…md` and its row in `docs/findings/register.md`. The validation check it was conditioned on: `VR-ACT-8` refuses a negative `claim_count` when present in the Rule Set, but its `range` check excludes nulls (`validate.py:694`), and no rule covers another declared weight column; reported to the lead, whose reading of the severity governs.

### Reds, on `a83aeef1` + the spec commit (tests only, no source change) — 2026-10-12

Command: `uv run pytest -q packages/pricing-core/tests/<file> -k <names> -p no:cacheprovider`.

**R1, GLM, by cause** (`test_a_weight_zero_row_never_reaches_the_family_domain_check`):
- `[response-0]`: `pricing_core.modelling.glm.GlmFitError: glum refused the fit: Some value(s) of y are out of the valid range for familyGammaDistribution. The response, the weights or the offset are outside what this family and link can …` (code `GLM_FIT_FAILED`, the Gamma domain; the cause PL-1674 requires).
- `[response-null]`: `GlmFitError: glum refused the fit: Input y contains NaN. …` (`GLM_FIT_FAILED`; a null response is NaN to `glum`).

**R1-GBM:** LightGBM RED, `test_a_weight_zero_row_does_not_shape_the_boosters_bins[lightgbm]`: `AssertionError: lightgbm: max rel diff 0.1285983078301599` (the full-book fit's predictions on the claims-only rows differ from the claims-only fit's by up to 12.9%). **XGBoost is a GUARD, green on main** (`[xgboost]` PASSED): XGBoost's weighted quantile sketch already gives zero-weight rows no say in the bins, so that arm's test records the property, not a red.

**R1-EBM RED:** `test_a_weight_zero_row_does_not_shape_the_ebms_bins` FAILED on main. **Corrected at the green commit (the entry above this line said only "FAILED"):** the cause is not "predictions differ". On main `fit_ebm` over the full book never returns, because `interpret` refuses a zero weight outright: `pricing_core.modelling.ebm.EbmFitError: interpret refused the EBM fit: illegal sample_weight value of zero` (reproduced by running the test's body with `require_usable_weights` patched to a no-op, which is the base's behaviour; `ebm.py:231`). PL-1674's "binning sees the extra rows" premise does not hold for the EBM: there is no full-frame EBM fit to differ from. The test is still the claims-only equality the plan asks for, and is red on main by that refusal.

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

### Green (2026-10-12)

**The code.** `pricing_core/modelling/weights.py` (new): `require_usable_weights(data, spec, error)` for the fits (refuses negative, null and non-finite weights and an all-zero book with `DECLARED_WEIGHT_INVALID`, then drops `weight == 0.0` exactly) and `drop_zero_weight_rows(data, spec)` for the diagnostics (drops, refuses nothing). Called at the entry of `fit_glm`, `fit_gbm` (train and holdout) and `fit_ebm`, before `resolve_factors`, with FR-116's `model_offset` filtered by the same mask (`WeightExclusion.take`), and at the entry of `compute_diagnostics`, `compute_gbm_diagnostics`, `compute_ebm_diagnostics` and `backtest_model`. `_partition` takes `excluded_zero_weight` from its caller. `diagnostics._weights`, `gbm._weights` and `_weighting` are untouched, as are the A/E formulas. `PartitionDiagnostics.rows_excluded_zero_weight: int | None = Field(default=None, ge=0)`; `docs/contracts` regenerated (`openapi/generated.json`, `schemas/generated/{diagnostics,backtest}.schema.json`) and the hand-authored `schemas/diagnostics.schema.json` gains the property. `backend/src/app/errors.py`: the one registration line (above). `backend/src` is otherwise unchanged; `model_handlers.py` is not touched.

**Defect found by the full run and fixed.** `packages/pricing-core/tests/test_glm_model_offset.py::test_a_model_offset_of_the_wrong_length_is_refused` failed after the first green commit: `WeightExclusion.take` indexed a wrong-length `model_offset` with the row mask, so numpy raised before `_model_offset`'s own length check could refuse it by name. `take` now returns an unaligned array as it came. (The weaker rule, "excluded rows then make the check's message cite the filtered height", only applies when the offset is already wrong.)

**Evidence** (all through `run-small.sh`, own test DB `gipricing_sl-1675_99411a3e`, `alembic upgrade head`):
- `uv run pytest packages/pricing-core packages/model-schema`: **2364 passed**.
- The new tests: `test_glm.py` (R1 both variants, exact-zero guard, bad-weight code, all-zero, offset guard), `test_gbm.py` (R1-GBM on both backends, bad-weight code on both, all-zero), `test_ebm.py`, `test_diagnostics.py` (R2 and R3 on the four entry points, with different train and holdout counts), `model-schema/tests/test_partition_zero_weight_count.py` (a stored partition with no count validates, `None` is not `0`, a negative count is refused).
- `backend/tests/test_api_backtests.py test_backtests.py test_diagnostics.py test_ebm_model_jobs.py test_model_jobs_gbm.py test_model_jobs.py test_model_offset_jobs.py test_spec_hash.py test_model_comparison.py test_custom_objectives.py test_contracts.py test_prediction.py`: **310 passed, 2 skipped**. The new `backend/tests/test_diagnostics.py::test_a_severity_fit_over_a_book_with_weight_zero_rows_stores_their_count` runs the MODEL_FIT Job over a dataset version with 133 weight-0 rows and reads both stored partitions' counts back (each > 0, summing to 133, with `rows` plus counts accounting for all 400 rows).
- `uv run ruff check .` clean; `uv run mypy` "no issues found in 240 source files"; `uv run lint-imports` "Contracts: 4 kept, 0 broken"; `uv run python scripts/generate-contracts.py --check` "48 generated contracts match the models"; `uv run python scripts/req-coverage.py` rc 0; `python3 scripts/audit-docs.py` fails only check 31 (working-id gap, expected until minted).

**Acceptance (PL-1674), per item.** 1 docs checks: as above. 2 no requirement range in the plan: unchanged since the mint. 3 spec first: `6aca576c` (FR-111 clause) precedes `ba89c87d` (code); the clause is `grep -n 'excluded from the fit and from every diagnostic' docs/specs/02-modelling.md`. 4 R1: red `893f96f5`, green after. 5 R2/R3: same. 6 refusals: red then green on all four arms, one code. 7 contract: `--check` clean, `test_contracts.py` green, stored artifact without the field validates. 8 the full gate: not run; awaiting the lead's grant.

**The T-text amendment and a test per new refusal** (the maintainer's (by delegation) entry "2026-10-12 06:37:28 BST", relayed by the lead's "2026-10-12 06:37:42 BST"; the gate grant for `c6bb0d95` was withdrawn, so this is a new head). The code refuses two things the clause of `6aca576c` did not name: a non-finite weight and a weight column that is 0 on every row. The clause is amended on the branch by a forward commit (the original sentence is left in the commit history, and the amendment says so in the row): "A negative, null or non-finite weight is refused (`DECLARED_WEIGHT_INVALID`), and so is a weight column that is 0 on every row, which would leave nothing to fit." Each new refusal has a test per arm, and each is labelled by how it ran:
- **Non-finite** (`inf`, and NaN as a value, distinct from a null): `test_an_unusable_weight_is_refused_by_the_weight_code` (GLM, EBM) and `..._on_both_backends` (GBM) now also take `inf` and `nan`. **RED on all four arms at the base, by code — measured by emulation, not on a base checkout:** the same tests' frames were run with `require_usable_weights` patched to a no-op in `glm`, `gbm` and `ebm` (that is the base's behaviour, the helper not existing there). GLM `GLM_FIT_FAILED` ("Input contains infinity or a value too large", and "Input contains NaN"); XGBoost raw `XGBoostError` ("Weights must be positive values"); **LightGBM no refusal** (both); EBM `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` ("sample_weight cannot contain missing values or infinites"). Green with the one code after.
- **All-zero:** `test_a_book_of_only_weight_zero_rows_says_so` (GLM, EBM) and `..._on_both_backends` (GBM) were in the reds run (`893f96f5`, on the real base): **RED on all four arms**, GLM wrong code, XGBoost raw error ("weights must contain at least one non-zero value"), LightGBM no refusal, EBM wrong code. Green with the one code after.

**Defect found while doing this and fixed:** the previous push (`c6bb0d95`) left `uv run ruff check .` failing with I001 on `backend/tests/test_diagnostics.py` (the `WeightSpec` import added after the last ruff run). Fixed with `ruff check --select I001 --fix`; `uv run ruff check .` is clean at this head.

**Frontend.** None (DP-Z1 ruled (a) by the maintainer's (by delegation) entry "2026-10-12 05:47:19 BST"); `frontend/src` is untouched.

### The full gate (2026-10-12)

Run on head `f1399e6d8facc488a014ddf6dcfa9cf952f64b95` (on `origin/main` `bf8d7929`, before this mint merge) by `~/gi-pricing-plan.local/scratch/sl1675/slot.sh` under `flock /tmp/slots/gate-1`, 07:37:04 to 08:29:31 BST, own database recreated from the template, preflight ok (head guard, clean tree, slot held, upgrade rc 0, one head). The run is the harness-tracked background form the maintainer's (by delegation) entry "2026-10-12 06:44:25 BST" adopts for a run past the foreground cap, each stage under `timeout 3600`. Logs: `~/gi-pricing-plan.local/scratch/sl1675/`.

| stage | exit |
|---|---|
| ruff | 0 |
| mypy | 0 |
| import_linter | 0 |
| pytest | 1 |
| audit_docs | 1 |
| req_coverage | 0 |
| contracts | 0 |
| fe_install | 0 |
| fe_generate | 0 |
| fe_lint | 0 |
| fe_types | 0 |
| fe_test | 0 |
| fe_build | 0 |

`pytest`: **13 failed, 5766 passed, 6 skipped** in 50:09. The 13, every one a root `tests/` docs-audit, doc-id or doc-index test that runs on the real tree and fails on the same cause, **check 31's gaps in the allocation, 1675 to 9900 and 9900 to 9902** (the two working ids of this ledger and its finding), which the minting in this commit closes:
1. `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
2. `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`
3. `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree`
4. `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`
5. `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`
6. `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
7. `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` ("the live allocation is not contiguous: [(1675, 9900), (9900, 9902)]")
8. `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`
9. `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`
10. `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`
11. `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`
12. `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`
13. `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci`

`audit_docs` printed `FAILED (2)`: check 31, gap between 1675 and 9900, and between 9900 and 9902. Nothing else. The lead read the 13 failure bodies in `pytest.log` and accepted the gate as check-31-only (from-lead entry "2026-10-12 08:30:37 BST"). The frontend half is green and nothing under `frontend/` changed.

**Not re-run after the mint:** the 13 are expected to pass once the ids are contiguous on main, which also needs the ids `1681` to `1696` of the pull requests ahead of this one. They are recorded as not yet run on the merge tree.

### The mint turn (2026-10-12)

`origin/main` `2a819741` merged into the branch (merge commit). `docs/INDEX.md` conflicted and was regenerated. **`docs/findings/register.md` also conflicted**, which is more than the brief allowed for ("INDEX conflicts regenerate; anything else stop"): both sides appended one row at the end of the file (this slice's FD row, and main's FD-1679 row). Resolved by keeping both rows; checked with `git diff origin/main -- docs/findings/register.md`, which shows exactly one row added and none removed. Disclosed to the lead in the mint report. Working ids minted: LG 9900 to **LG-1697**, FD 9902 to **FD-1698** (allocated by the lead, reserved in eta); every occurrence renamed, files and register row included. `PL-1674` stays `active` (a plan is not retired while its slice is closed, `document-ids.md` check 33).

## PRs

(none yet; the slice's one PR carries this ledger.)
