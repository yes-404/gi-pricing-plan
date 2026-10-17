---
id: FD-1754
family: finding
title: A GBM model_call on a banded or grouped Factor scores with factors=() over the graph's raw value
status: active
created: 2026-10-17 # original date 2026-10-16, set at the filing; minted 2026-10-17
owner: auditor
tree: a2f77b2dcad5aaec41a5f10aa664383caf421e8b
corrected_by: []
relates: [WK-1178, WK-673]
---

# FD-1754 — a GBM `model_call` prices a banded or grouped Factor on the wrong value, silently

*(Minted 2026-10-17 as FD-1754 from working id 8073, in the D18 batch mint PR.)*

*(Filed under working id 8073 (written "FD 8073" in prose), reserved by the lead. Authority: the
maintainer's entries "2026-10-16 10:59:28 BST" (reading accepted, disposition, severity rule) and
"2026-10-16 11:11:03 BST" item 4 (HIGH by run), `channel/to-lead.md`. Reads at `origin/main`
`a2f77b2dcad5aaec41a5f10aa664383caf421e8b`; the run is the one reported in the lead's entry
"2026-10-16 11:10:37 BST", `from-lead-2026-10-09.md`, probe (3), run 11:08:14 to 11:09:20 BST in the small slot.)*

## Finding

**Severity: HIGH, by the 10:59:28 rule (case C red, a silent mispricing), on the run of 2026-10-16
11:08:14 to 11:09:20 BST.** A `model_call` to a pinned GBM whose Factors include a banded or
grouped one scores with `factors=()` over whatever the graph supplies, and the GBM's encoding of
the banded slug is looked up against that raw value. The run, case C (labels "1","2","3" and an
integer raw value 2, no error key):

| Backend | `model_call` result | `predict_gbm(factors=<the model's factors>)` |
|---|---|---|
| xgboost | 300.3575744628906 | 99.8523941040039 |
| lightgbm | 300.3562076051003 | 99.84995096284597 |

About three times the correct price, with no error. Case A (raw `driver_age` 25, both backends)
fails loudly: `RuntimeError: {"type":"NodeError","source":"Failed to run custom node handler","nodeId":"s_risk"}`.
Case B (the graph supplies the band label, the control) and the fixture sanity test pass.

## Evidence

All reads at `origin/main` `a2f77b2d`.

1. A GBM with banded or grouped Factors fits, is approved and is pinned: `fit_gbm` resolves and
   encodes bandings ordinally into `categorical_maps` (`gbm.py:636`, `:639`, `:264-355`, `:723`;
   worker `model_handlers.py:350-358`); WF-699 approves it (`journey.py:742-745`, `:755`+); it is
   pinned via `pins.models` `gbm_ref` (`:664`, `:737`).
2. Nothing refuses it: the save check checks slug membership only (`rating_algorithms.py:119-150`,
   `:184-210`); compile checks completeness only (`compile.py:933-975`); the engine has no banding
   step (`algorithm.py:12-15`).
3. The Bundle carries no Bandings for a GBM pin: `compile.py:832-840` ("A GBM pin adds nothing
   (`predict_gbm` reads its features off the frame)"), and the runtime scores with `factors=()`
   (`runtime.py:626`; `:615`).
4. In `predict_gbm`, `if factors:` (`gbm.py:1292`) resolves the Factors; the `else` arm (`:1303-1319`)
   reads the frame's columns as the features. `gbm.py` around `:1263` says passing the factors "is what
   a banded or grouped factor needs, since the transformation is part of the feature and not of the frame".
5. **Loud arm (case A).** The raw value is cast to a string and looked up in `categorical_maps`
   (`gbm.py:314-329`); a value not in the map raises `GbmFitError("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED")`
   (`:322-330`), a `RuntimeError` subclass (`gbm.py:144`) that the handler does not catch
   (`runtime.py:771` catches `ModellingError` and `PredictionError` only), so the zen binding returns a
   generic NodeError and no price.
6. **Silent arm (case C).** Banding labels are free strings (`model_schema/modelling.py:370`). A
   banding labelled "1","2","3" and a raw integer 2 gives "2", which is band 2's code whatever band 2
   holds. Grouped Factors: the same, with a raw level equal to a group name. The convention that the
   graph supplies the label under the slug (`examples/fremtpl2/algorithm.py:60-77`, `:136-138`) is not
   enforced anywhere.
7. The demo GBM has banded Factors (`model.py:81-85`, `:283-289`, `:314`), is pinned, approved and
   compiled, but no `model_call` reaches it (`journey.py:78-79` skips B4 and C1').
8. **G2 (SL-1543) is not blocked:** B4 is a `model_call` on the Peril Structure (`PL-1542:98`), the
   frequency and severity GLMs, which carry their Bandings (`_GlmScorer`).

Scratch: `~/gi-pricing-plan.local/scratch/probe_gbm_banded_test.py` (A loud, B control, C silent,
fixture sanity).

**Re-run by the auditor, 2026-10-16 22:22:42 BST (Europe/London), against `origin/main`
`a2f77b2d`'s code (this worktree changes docs only), once through `run-small.sh`** (the probe
copied to `packages/pricing-core/tests/test_probe_gbm_banded.py`, deleted after, not committed):
`4 failed, 3 passed in 6.75s`, rc 1. The 4 failures are case A (both backends: `RuntimeError:
{"type":"NodeError","source":"Failed to run custom node handler","nodeId":"s_risk"}`) and case C
(both backends: `assert 300.3575744628906 == 99.8523941040039` for xgboost, `assert
300.3562076051003 == 99.84995096284597` for lightgbm, no error key); the 3 passes are case B
(control, both backends) and the fixture sanity test. **It agrees with the relayed lines to the
last digit.** No raw log of the 11:08:14 run survived in `scratch/`, which is why the run was
repeated.

## Severity: the reasoning

The maintainer's rule at 10:59:28 was: C red is HIGH; only A red is MEDIUM (a loud failure, a pinned
model that cannot score). C is red on both backends, so HIGH. It is not CRITICAL on this reading
because it needs a banded or grouped GBM that a graph reaches through a `model_call`, which no shipped
demo or P2 exit path does today (Evidence 7, 8), and a graph that supplies the label is correct.

## Disposition

1. **Fast fix, its own slice: SL 8071 (WK-1178), branch `sl-8071-wk1178-gbm-banded-refusal-2026-10-16`
   at `481db4c0` (tree `7f0f31cb`).** Refuses any `model_call` to a GBM with a banded or grouped Factor,
   code `MODEL_CALL_GBM_TRANSFORMED_FACTOR`, at compile (`compile.py` `check_model_call_gbm_factors`,
   peril components included), and at save (`rating_algorithms.py` `_refuse_gbm_transformed_factors`, all
   three save routes). **Keyed on the `model_call` step, never on the pin:** the demo pins the banded GBM
   at C1 and recompiles at C5, which a pin-keyed refusal would fail. Built and unrun at filing.
2. **GbmFitError escaping the handler** is fixed in the same slice: the runtime catches it by name and
   returns `MODEL_CALL_FAILED` with its code and no quote value (NFR-499).
3. **Real support is a DESIGN decision for the decision-maker (DP), deferred with owner WK-673.**
   Options: (a) carry the GBM's Factors, Bandings and Groupings in the Bundle and call
   `predict_gbm(factors=...)` through a renamer like `_GlmScorer.columns` (DP-2 (b), `PL-1464:768`:
   "feature_map values are Factor slugs for both kinds"); (b) keep the refusal and have the actuary use
   a GLM or the GLM approximation (FR-222, FR-230). The requirement it serves: `03` FR-222 (`:110`),
   `02` FR-193 (`:306`) and `02` section 4.8. **A P2 need: NO** (`~/gi-pricing-plan.local/scratch/gbm-banded-p2-need-2026-10-16.md`
   at `a2f77b2d`: roadmap section 12 row 2 names no model class; WF-701 A1-A6, C1-C7 name no GBM or
   Banding; WF-699 B4 calls the Peril Structure). Recommendation: (b) for P2, (a) when a requirement
   needs a banded GBM in a `model_call`.
4. **Open limb, for the planner and the maintainer:** interaction, spline, polynomial and expression
   Factors on a GBM may carry the same latent defect (the transformation is part of the feature, not of
   the frame). SL 8071's scope is banded and grouped only; this has not been read or run.

**Proof on broken input (CLAUDE.md section 13):** SL 8071's red-first pair, with case C refused at
compile, case A refused at compile, and GbmFitError at runtime giving the named error; the negative
test that a pinned banded GBM with no `model_call` still saves and compiles.

**The event that next discharges this finding:** the merge of SL 8071 with its proof recorded in its
ledger (items 1 and 2); items 3 and 4 stay open with their owners.
