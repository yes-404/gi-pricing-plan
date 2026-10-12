---
id: FD-9902
family: finding
title: LightGBM fits silently on a negative or null declared weight, XGBoost raises a raw library error with no platform code, and the EBM names it with an unrelated code
status: active
created: 2026-10-12
owner: auditor
tree: bf8d7929eaa440def943f002538d02270ff09d22
corrected_by: []
relates: [WK-1178, SL-1675, PL-1674, FR-111, FR-115, FR-140, FR-171, OQ-1672]
---

# FD-9902 — a declared weight that cannot be fitted on is not refused uniformly

*(FD-9902 is a working id reserved by the lead; the lead mints it at the merge turn. Filed by
`executor-sl1675` from the maintainer's (by delegation) entry "2026-10-12 06:10:04 BST" and the
lead's from-lead entries "2026-10-12 06:10:29 BST" and "2026-10-12 06:17:07 BST".)*

Found by SL-1675 (LG 9900), PL-1674 Task 0 Step 2: the base behaviour of the refusals, run on a
600-row severity frame with ONE row at weight `-1` and, separately, ONE row at weight null.
Measured at `origin/main` `604ea084` and again at `a83aeef1`.

## Evidence

| Arm | Negative weight | Null weight |
|---|---|---|
| `fit_glm` | `GlmFitError` `GLM_FIT_FAILED` ("Sample weights must be non-negative") | `GLM_FIT_FAILED` ("Input contains NaN") |
| `fit_gbm`, XGBoost | raw `XGBoostError` ("Weights must be positive values"), no `GbmFitError`, no platform code | same |
| `fit_gbm`, **LightGBM** | **no refusal; the fit returns** | **no refusal; the fit returns** |
| `fit_ebm` | `EbmFitError`, code `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` ("illegal negative sample_weight value") | same code ("sample_weight cannot contain missing values or infinites") |

`gbm._weights` (`gbm.py:235`) casts the column to `Float64` and hands it to the backend as it
stands, so a null reaches LightGBM as NaN and a negative as a negative. The reds in LG 9900
(`893f96f5`) reproduce each row of the table by its cause.

## The validation check the maintainer asked for

*Does a validated Dataset Version already refuse a negative or null value in a column a model
declares as its weight?* Partly, and not where it matters:

- `01`'s Layer 3 table, `VR-ACT-8` `claim-count-non-negative` (`fail`; `packages/model-schema/src/model_schema/validation.py:372-375`,
  check kind `range`), whose check text reads verbatim "`claim_count >= 0, integer`" (`01`: "`claim_count ≥ 0`, integer"), refuses a negative `claim_count`, when the rule is in the Dataset's rule set.
  The check (`packages/pricing-core/src/pricing_core/data/validate.py:671-703`) selects
  `offending = frame.filter(pl.col(column).is_not_null() & predicate)`: **a null is never an
  offender.** A null `claim_count` passes `VR-ACT-8`.
- `VR-ACT-1` (`exposure-positive`, `fail`) refuses a zero or negative `exposure_years`, with the
  same `is_not_null()` exclusion. That covers burning cost's `weight = exposure` when the column is
  `exposure_years` and the rule is present.
- Nothing refuses a negative or null value in **any other** column a spec declares as its weight:
  `ModelSpecCommon.weight` takes any column name, and the rules are bound to named columns, not to
  "whatever a model later declares as its weight".
- The rules are a versioned, editable Rule Set per Dataset (FR-51). `VR-ACT-8` is in the
  seeded set and is not mandatory in a Dataset's own.

So a negative `claim_count` is stopped at validation if the rule is present; a **null** weight, and a
negative or null value in a weight column other than the two named, reach the fit.

## Finding

**Severity HIGH, PROVISIONAL (the maintainer's (by delegation) entry "2026-10-12 06:10:04 BST", limb 1;
the validation check above is the one condition that entry set for lowering it to MEDIUM).** Limb 1,
LightGBM fitting silently on a negative or null weight, is a silently wrong model: a mispricing path.
The check does not clear it: it protects one column and not nulls. The lead rules the final
severity; the executor's reading is that the check supports **HIGH** (nulls and non-`claim_count`
weights are unprotected, and the one rule that is present is optional).

Limbs 2 and 3 are **LOW**: XGBoost refuses, with a raw library error and no platform code; the EBM
refuses, with a code that names monotone constraints.

## Disposition

**Owner: WK-1178. Discharged by SL-1675.** `pricing-core`'s one weight helper
(`pricing_core/modelling/weights.py`) refuses a negative, null or non-finite declared weight before
any backend sees it, for GLM, XGBoost, LightGBM and the EBM, with one code, `DECLARED_WEIGHT_INVALID`
(`02` §5.1, dated note citing the 06:10:04 entry; registered in `backend/src/app/errors.py`).
Acceptance 6 of PL-1674 is red-first on all four arms. The event that discharges this record is the
merge of SL-1675. Dataset validation is **not** changed by this slice: a rule that covers nulls and
whichever column a model declares is a `01` change, and is not filed here.
