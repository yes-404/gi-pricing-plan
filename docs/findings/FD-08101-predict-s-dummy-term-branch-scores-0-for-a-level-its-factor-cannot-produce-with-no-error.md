---
id: FD-8101
family: finding
title: Predict's dummy-term branch scores 0 for a level its factor cannot produce, with no error
status: active
created: 2026-10-17
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, SL-1543, SL-8099, FR-222]
---

# FD-8101 — Predict's dummy-term branch scores 0 for a level its factor cannot produce, with no error

## Finding

**LOW, hardening; owner WK-1178; verdict deferred with an owner.** Unreachable via the API
today (the chain is cited below). The maintainer's entry "2026-10-17 20:56:36 BST — Maintainer:
banded-term trace → TEST-WORLD-ONLY accepted; SL-1543 (A) fix GO; residual → a LOW FD
(hardening)" (`to-lead.md`) names it: "predict.py's dummy-term branch scores 0 for an
unproducible level with no error; unreachable via the API today; option: a load-time domain
check → a named error. Not in SL 8099's scope."

When a fitted GLM carries a dummy term `slug[level]` whose `level` the term's resolved factor
column can never produce, `_term_vectors` yields an all-zero indicator for every row. The term
contributes nothing to the linear predictor, silently. Only a *missing factor* raises
`MODEL_TERM_UNRESOLVED`; a *missing level* does not.

## Evidence

At `origin/main` 9469721d (read by the author, not taken from the trace note):

- `packages/pricing-core/src/pricing_core/modelling/predict.py:52` `_DUMMY` matches `slug[level]`;
  `:117` `match = _DUMMY.match(term)`; `:129`
  `indicator = (matrix.frame[column].cast(pl.String) == level).cast(pl.Float64)`.
  `:119-128` raise `MODEL_TERM_UNRESOLVED` only when `matrix.terms.get(slug)` is `None`.
- `packages/pricing-core/src/pricing_core/modelling/factors.py:193-194` an `IDENTITY` factor
  returns `frame[source]` unchanged; `:196-198` a `BANDING` factor applies `apply_banding`. A raw
  integer `25` cast to String is `"25"`, never the band label `"25-39"`.
- Probe (executor trace, scratch `glm-banded-trace.md`, no DB, hand-built coefficients
  `driv_age[25-39]=.5`, `driv_age[40+]=.9`): with an `IDENTITY` factor the indicators are 0 for
  all of raw 18/25/40/80; with a `BANDING` factor and the Banding pinned they are 18→0,0;
  25→1,0; 40→0,1; 80→0,1.

## Why it is unreachable via the API today

- `fit_result` is written only by the `model.fit` job (`worker/model_handlers.py:374` `fit_glm`
  → `:557` `record_fit(fit_result=result)`); no route accepts a client `fit_result`, and the job
  derives coefficients from the spec's own Factors.
- Compile carries a GLM's Factors, Bandings and Groupings into the Bundle
  (`compile.py:836`); the scorer refuses `RATING_VERSION_UNPINNED` when a Factor's `banding_id`
  is not carried. `compile.py:982`'s `check_model_call_gbm_factors` skips GLMs deliberately
  (`03-rating-engine.md:110`, FR-222: a GLM carries its Bandings and Groupings and is not
  affected).
- The only way to the zero effect is a direct DB insert of a fabricated fit over an `IDENTITY`
  factor, which is the test world (`backend/tests/test_demo_rating_evidence.py`
  `_approved_model`), judged mis-wired, not a product path (SL-1543 option A).

## Options (none picked)

1. **Load-time domain check** (the maintainer's named option): at model load, every dummy term's
   level must be producible by its Factor (a `BANDING` factor's band labels, a `GROUPING`'s
   groups, a categorical column's observed levels); otherwise a named error.
2. **Per-call guard in `_term_vectors`**: refuse when a dummy term meets an `IDENTITY` numeric
   column. Smaller, but pays per quote on the hot path FD-8097 is cutting.
3. **Leave, record only**: rely on the API's closed write path. Cheapest; defence in depth stays absent.

## Disposition

Deferred with an owner: WK-1178. **Not in SL 8099's scope** (that slice is FD-8097's timing
fix). Decision on the option belongs to the lead or an RL; this record picks none. The event
that next discharges it: a merged change adding the domain check, or a dated ruling accepting
the absence.
