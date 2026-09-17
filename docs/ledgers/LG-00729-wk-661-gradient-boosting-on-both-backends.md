---
id: LG-729
family: ledger
title: WK-661 — gradient boosting on both backends
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-17
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — gradient boosting on both backends, 2026-08-17 *(in progress, not closed)*

The ninth slice, and the largest: `02` §3.5 stood at **0 of 12**. Shipped as two PRs, because
one carrying a discriminated-union migration, two heavy dependencies, a per-backend scoring
path and TreeSHAP is not reviewable — **A** the contract, the fit and the platform seam,
**B** the transparency artifact.

| Delivered | Evidence |
|---|---|
| `GbmSpec`, `GbmFitResult`, and `ModelSpec`/`FitResult` as real discriminated unions | §4.4 has called `ModelSpec` a tagged union since Phase 0; the tag existed and the union did not, so `GlmSpec.model_validate` was the only reader. 19 tests, every one a prohibition |
| `fit_gbm` / `predict_gbm` on XGBoost **and** LightGBM | 36 tests, every backend-independent one parametrized over both. One `GbmSpec` fits either; the objective, the metric names and the interaction-constraint form are translated here so the contract does not fork |
| **FR-129's per-backend offset**, the requirement that shaped the module | Doubling exposure must exactly double the prediction, asserted on each backend. **Proven by breaking it:** removing `raw + margin` from the LightGBM branch fails both LightGBM tests and neither XGBoost one |
| FR-174 in full — six things, not "eval curves and importances" | Evaluation curve on train and holdout, gain/cover/frequency, permutation importance on the holdout, partial dependence with each point's exposure share, monotonicity verified against the fitted response, tree/depth summary |
| The universal diagnostics are the **same code** for both arms | `_partition` takes `mu` and the family rather than a `GlmFitResult`, so a GBM and a GLM on one holdout report A/E, lift and calibration computed identically — which is what makes FR-186's comparison a comparison |
| One Job kind fits either arm | A second `model.gbm_fit` would have made every caller, status screen and audit query ask which of two names to look for |
| The booster stored in the model row's own transaction | `pricing-core` computes the content-addressed reference and cannot store the payload (ADR-703), so the failure to exclude is a committed model pointing at an object nobody wrote. The test reads the bytes back |
| FR-153's *objective applicability* half | An objective outside FR-120's set, or a Custom Objective while FR-142 is unbuilt, is a `200 ok:false` before a Job exists. The set is exported from `pricing-core` and read by both the validator and the fit |
| §3.6's transparency artifact, both forms | GLM approximation with R², deviance explained and worst regions named by factor level with their exposure share; TreeSHAP mean \|contribution\| on a persisted sample and seed; a generated fidelity statement that says *where* the approximation fails. 19 tests |
| `GET /models/{id}/transparency` — **FR-139, appended** | §5.1 declared the `POST` and no read: a 202 whose artifact nothing can fetch, invisible to the endpoint audit because that compares the spec against the contract and this was in neither |

**Five spec corrections, all resolved in `02` rather than diverged from** (`CLAUDE.md` §0):

1. `GbmSpec.backend` removed — `model_type` *is* the backend. Two fields carried the same two
   strings and nothing downstream could say which to believe.
2. `GbmSpec.base_margin` removed — FR-121 says the platform *constructs* it from the
   declared offset, so a second declaration was a second source of truth for the one number
   the fit silently depends on.
3. `loss_treatment` sits on the **common block**, not the GBM arm: capping applies to the
   response, not the learner. `spec_hash` went to **v3** for it, paid visibly as v1→v2 was.
4. `predict_gbm` took a `Model` — the third instance of the ADR-703 defect, now the third
   fixed. `fit_gbm` also gains `factors`, `holdout` and a `GbmFit` return.
5. The evaluation curve belongs in **diagnostics**, not on the fit result. Here the *code* was
   wrong: `diagnostics.schema.json` has had it under `gbm` since Phase 0 and FR-174 asks
   for train *and* holdout, which is FR-183's shape. The curve moved and gained its train
   series.

**`shap` is not a dependency** (`02` §8 amended). XGBoost's `pred_contribs` and LightGBM's
`pred_contrib` are the same TreeSHAP on the same trees, already linked against the booster —
and `shap` would have pulled scikit-learn into the package ADR-703 keeps importable
standalone, for plotting the frontend does and aggregation that is fifteen lines. The cost is
reported rather than hidden: LightGBM has no interaction-value equivalent, so
`ShapSummary.interactions_available` is a capability flag, because an empty list with no flag
reads as "this model has no interactions" — a finding that backend cannot make.

**The defect this slice found is not in this slice.** `PlatformError` refuses a code it does
not know and the fit handler maps `pricing-core`'s codes straight across, so **eleven** GBM and
transparency codes would have turned a named refusal into `ValueError: unknown error code` from
inside the error path. Second occurrence: `GLM_SEPARATION_DETECTED` was unregistered from the
spine until diagnostics tripped it. `tests/test_repository_invariants.py` now ASTs the source
for every code `pricing-core` raises and asserts each is registered *and* declared — proven
against a deliberately unregistered one. Five refusals reuse codes §5.1 already declared rather
than getting parallel names.

**Environment, worth recording:** LightGBM's Linux wheel links the OpenMP runtime and does not
vendor it, so `import lightgbm` fails on a host without `libgomp1` while XGBoost — which does
vendor one — imports fine. A suite exercising only the primary backend would have called the
pair healthy. Declared as a step in `python.yml` rather than left to the runner image, and
written into `.claude/skills/python-package`.

**Numbers.** `scope-audit MODEL --sections 3.5,3.6` reads **17 of 19**; `--endpoints` reads
**20 of 30**, up from 18 of 29 (FR-139 added one declared and two published). Suite: 952
Python tests, 105 frontend.

**Not delivered, with verdicts:**

| Requirement | Verdict |
|---|---|
| **FR-128** — reconciliation accounts for the loss treatment | **Reassigned.** Its other half is FR-190's peril-structure reconciliation, which does not exist. Owner: the peril structure slice |
| **FR-140** — EBM shape functions | **Delivered 2026-08-21 (WK-661, the EBM slice).** `interpret-core==0.7.8`; term shape functions exported verbatim as additive lookup tables; transparency artifact built from the export with no approximation; universal diagnostics through the shared partition; scoring from the tables alone (ADR-705). The third heavy dependency is now installed, so the 'one requirement for a model type nothing fits' objection is discharged |
| `loss_treatment` `spliced` / `excess` | **Declared and refused by name.** Narrowing the enum would have cost a `spec_hash` version to widen later; applying them as `none` would fit an uncapped model under a spec that records a treatment |
| **R3 enforcement** | **Deferred to `03`, by the requirement's own wording.** FR-132 binds at the point a *Rating Version* references the model, which is a later phase. This slice provides the artifact that check will read, and `02` R3 is where the obligation stays |
| Frontend | **WK-664.** §5.3's model spec builder, the diagnostics view's GBM eval curves and FR-135's interaction suggestions are view work. `ModelDetailView.vue` is narrowed to the GLM arm so `vue-tsc` keeps naming the GBM view as missing |
| **OQ-577** raised | Whether the GLM approximation is a Model in its own right. Bound to OQ-575 — it needs an independent identity only if something may rate on it — and recommended to wait rather than build an artifact nothing references |
