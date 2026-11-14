---
id: FD-2043
family: finding
title: A Decimal NaN reaching a banded GLM input panics the engine where a float NaN is a clean FactorResolutionError
status: closed
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8354, minted 2026-11-06
owner: lead
tree: 23408d64ee6592967bc69bed5b7f404b61eb684d   # the gated tree of sl-8389-refusal-by-type (R2 and SL-2041)
corrected_by: []
relates: [WK-1178, SL-2020, SL-2038, FR-87, FR-97, FD-1780]
---

# FD-2043 — a Decimal NaN reaching a banded GLM input panics the engine

*(Minted 2026-11-06 as FD-2043 from working id 8354, born closed, in the PR of R2 and SL-2041. No essay or register row existed before: the finding was filed only in the maintainer's entry "2026-11-05 11:16:36 GMT" (2).)*

## Finding

**Severity MEDIUM (the maintainer, entry "2026-11-05 11:16:36 GMT" (2), `to-lead.md`): a crash on a scoring path, never a mispricing; one worker request, contained by the process.** Found by SL-2020's audit and its executor: `pl.DataFrame` built from a row holding `Decimal('NaN')` raised `pyo3_runtime.PanicException` (`PyDataFrame.from_dicts`, `polars/_utils/construction/dataframe.py:719`), where `float('nan')` passed. Read at `369c43c7`: `modelling/predict.py` `linear_predictor_row` built `pl.DataFrame([dict(row)])`.

## Evidence

Base `662867bb`: a `pl.DataFrame` built from a row holding `Decimal('NaN')` raised `pyo3_runtime.PanicException` (`PyDataFrame.from_dicts`), where `float('nan')` passed. See `LG-2039`'s Build log for the reds by cause; the fix is `_row_frame` in `pricing_core/modelling/predict.py`.

## Disposition

***Resolved 2026-11-06*** — closed in place 2026-11-06 by the executor, as the closing act of the mint of SL-2038 (WK-1178, LG-2039, PL-2019; this PR; its number, squash commit and merge date are written at the merge's date-of-record), on the lead's adoption of the SL-2038 audit. Delivered remedy: `_row_frame` (`pricing_core/modelling/predict.py`) carries a non-finite `Decimal` as the float it equals (a signaling NaN, which `float()` refuses, as a quiet NaN), the one site both GLM scoring paths and the offset source reach, so the value reaches `apply_banding`'s coded refusal (FR-97). Red first, by cause, at base: `PanicException` (LG-2039); a second red for the maintainer's owed item ("2026-11-05 14:18:33 GMT" (2)), `a72dbe7e` `decimal_snan` `ValueError: cannot convert signaling NaN to float`, `Decimal('Infinity')` and `Decimal('-Infinity')` already refused; green `d6d5ffa0`. `test_a_nan_banded_input_is_a_factor_resolution_refusal_on_both_paths` (float NaN, `Decimal('NaN')`, `sNaN`, `Infinity`, `-Infinity`) green, `test_glm_scalar_predict.py` 39 passed, 4 skipped (the auditor's re-run at `369c43c7`). **Not traced and not claimed:** a non-finite `Decimal` at a non-banded numeric input now reaches the linear predictor as a float; the test covers a banded input only.
