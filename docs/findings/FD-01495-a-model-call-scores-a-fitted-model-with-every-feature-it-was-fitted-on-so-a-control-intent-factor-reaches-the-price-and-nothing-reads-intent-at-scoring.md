---
id: FD-1495
family: finding
title: A model_call scores a fitted model with every feature it was fitted on, so a control-intent factor reaches the price and nothing reads intent at scoring
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
corrected_by: []
relates: [WK-673, WK-1178, FR-88, FR-240, FR-230]
---

# FD-1495 — a `model_call` applies a model's `control` factor

*Disclosure: drafted under working id 9639; minted as FD-1495 on 2026-10-08, in the T2 batch mint PR. Note: in the quoted channel entries, FD 9639, PL 9649 and FD 9641 stand as the channel wrote them (minted FD-1495, PL-1471 and FD-1479).*

## Finding

**Severity: HIGH — measured 2026-10-05 13:54 UTC (§Evidence): the premium input changes with the control value.** Per the maintainer's (by delegation) rule (below), APPLIED is HIGH and
neutralised-and-untested is LOW. **Owner: WK-673.** **Confirmed HIGH, final**, by the maintainer (by delegation) in the entry headed *"2026-10-05 15:00:28 BST — FD 9639 HIGH CONFIRMED by measurement; owed items accepted; CAPACITY: 2 live of 8, so fill the slots"* (`to-lead.md`, the lead's channel). The
maintainer's (by delegation) decision is the entry headed *"2026-10-05 14:21:22 BST — DECISIONS 35–38 (PL 9649, the FR-240
family fix); file the model_call candidate; FD 9641 noted"*, "CANDIDATE (c)" (`to-lead.md`,
the lead's channel): *"does scoring apply the control factor's coefficient to the quote … or neutralise it
(e.g. at the base level)? … if scoring applies it, HIGH (a price depends on a factor declared not to
price); if it is neutralised and only untested, LOW."*

> **Measurement status.** Drafted at 13:22–13:44 UTC with the script unrun (both gate slots were held, and the
> lead's rule bars a probe during a held gate); **run 2026-10-05 13:54:02–13:54:13 UTC with both slots free and
> `pgrep` empty**, and amended here. §What the code does is read from the source at `83ea5090`; §Reproduction
> is measured.

## What the specs say

- **`02` FR-88** (`docs/specs/02-modelling.md:89`): *"Rating Versions may only use `risk` factors; a `control` factor
  reaching a rate table is a validation error in `03`."* Its 2026-08-22 amendment (OQ-595): `risk` and
  `control` both enter the design matrix with a **free coefficient** and differ only in rateability; `rateable()`
  implements it.
- **`03` FR-240** (`docs/specs/03-rating-engine.md:137`): bundle compilation refuses "no `control`-intent factor in a
  rateable path (`02` FR-88)". The 2026-09-30 amendment (RL-1329) adds only the `LADDER_CLAMP_UNPLACEABLE` check;
  none of its dated text narrows the control clause or says what a `model_call` must do.
- The spec names the rejection **code** `CONTROL_FACTOR_IN_RATEABLE_PATH` (`03:933`), and no code or test
  contains the string (`grep -rn CONTROL_FACTOR --include=*.py packages backend` prints nothing).

So the spec requires a control factor to **not reach a price**, and says nothing of a model that was *fitted*
with one and is then *called*.

## What the code does (trace, at `83ea5090`)

1. **Fit.** `resolve_factors` (`packages/pricing-core/src/pricing_core/modelling/factors.py:156-170`) refuses only
   the intents in `REFUSED_FACTOR_INTENTS` (`offset`, `diagnostic`). `control` is fitted with a free
   coefficient or, for a booster, as an ordinary feature. `GbmFitResult` carries `feature_order` and no intent.
2. **Compile.** `rating/compile.py` contains no read of `Factor.intent` (the only `control`/`rateable` hit is an
   unrelated FR-274 docstring). The FR-240 clause is **not implemented**, for rate tables or for models.
3. **Score.** `_model_call_handler` (`rating/runtime.py:512`) builds `feature_row` from the step's `feature_map`
   and calls `predict_gbm(gbm_result, booster, frame, factors=(), nthread=1)` (`runtime.py:565`). With
   `factors=()`, `predict_gbm` (`modelling/gbm.py:1290-1297`) **requires every slug in `result.feature_order`
   to be on the frame** and raises `SCORING_FEATURES_MISMATCH` otherwise. A booster is positional (`:1311`).
   It therefore cannot hold a control feature at a base level: the feature is supplied and the trees split on it,
   or the call fails. **Nothing on this path reads `intent`.** The handler's result is the premium input
   (`value = round(prediction)`).
4. **GLM pin.** A `glm` model is refused at scoring (`runtime.py:569-580`, `_model_call_failure`), so the GLM
   arm is not reachable today and the question is moot for it until that is built.

**Neutralisation does not exist**: there is no code that holds a control feature at a base level, drops it, or
excludes it from `feature_map`. The scoring path is intent-blind.

## Evidence

### Reproduction

Scratch script (pricing-core only; it calls the same `predict_gbm(..., factors=(), nthread=1)` as the handler):
`$CLAUDE_JOB_DIR/tmp/fd9639_repro.py`. It fits xgboost and lightgbm on 6 000 rows whose response depends on a
`control`-intent factor (`year`, +0.25 per year in the linear predictor) beside a `risk` factor (`age`), then scores
`age=40` at `year=2010` and `year=2020`. The script lives in the job's scratch directory, not the repository;
its sha256 is `f647de417dbca8be8eae23dd636f468129d72497150b724025ce7bcfd9deab33`, run at tree `83ea5090` with
`uv run python <script>` (`uv sync --all-packages` first), 2026-10-05 13:54:06–13:54:13 UTC. Output, verbatim:

```
xgboost feature_order: ('age', 'year')
  control year=2010 -> prediction 0.172311
  control year=2020 -> prediction 0.501202
lightgbm feature_order: ('age', 'year')
  control year=2010 -> prediction 0.171648
  control year=2020 -> prediction 0.505089
```

**The prediction rises about 2.9x (xgboost) and 2.9x (lightgbm) when only the control value moves from 2010 to
2020, `age` held at 40.** So scoring **APPLIES** the control factor. (The ratio is below the generating
`exp(2.5)` because 40 shrunken depth-3 rounds do not fit the tail fully; the direction and size are not in
doubt.) The call is `predict_gbm` as the handler makes it; the handler's full path through `load_bundle` was
not run.

## Whether the seed or any golden quote has a control factor

**No.** `examples/fremtpl2/model.py:162` authors every factor as `FactorIntent.RISK`, and no other `intent=` appears
in `examples/fremtpl2/`. `grep -rln 'FactorIntent.CONTROL\|"control"' examples packages backend` finds only
`packages/pricing-core/tests/test_factor_resolution.py`, `test_glm.py`, `backend/tests/test_api_transformations.py`
and the model-schema definition — none a golden quote or a `model_call`. So today **no shipped price depends on a
control factor**; the defect is reachable by a user-authored model, and untested.

## Disposition

**Fix before close with an owner: WK-673**, red first. Deadline, the measurement having confirmed APPLIED: before the
P2 exit demo (the maintainer's (by delegation) rule).

Remedy shape (not a design; the maintainer's (by delegation) decisions 36–38 are adjacent):

Either (a) refuse at compile a `model_call` whose pinned model's feature set contains a `control`-intent factor
(`CONTROL_FACTOR_IN_RATEABLE_PATH`, as decision 37 does for rate tables), which needs the model's factor intents
at compile, which `GbmFitResult` does not carry; or (b) record intent on the fit result and neutralise at scoring.
The choice is open and is the lead's to put in `open-questions.md`; the audit does not pick.
