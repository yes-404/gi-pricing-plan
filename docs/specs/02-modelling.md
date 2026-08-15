# 02 — Modelling

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `MODEL`
**Prerequisites:** [`00-overview.md`](00-overview.md) §2 and §4; [`01-data-management.md`](01-data-management.md) §1.3 (the validation gate).

---

## 1. Purpose & scope

### 1.1 In scope

Everything between "a `validated` Dataset Version exists" and "an `approved` Model is ready
to be referenced by a Rating Version":

1. **Factors** — declaring rating variables as named transformations of dataset columns.
2. **Bandings and groupings** — first-class, versioned, auditable transformations, with
   assisted derivation (quantile, tree-based, credibility-weighted) and manual override.
3. **Model fitting** — GLM (`glum`), gradient boosting (XGBoost, LightGBM), and transparent
   ML (EBM), each with actuarially correct defaults for insurance responses.
4. **Custom objectives** — declaring, validating, approving, versioning, and auditing
   non-standard losses; a first-class capability, not an escape hatch.
5. **Diagnostics** — the persisted evidence an actuary and an Approver judge a model by.
6. **Transparency artifacts** — the mandatory explanation of any non-GLM model.
7. **Peril structure** — composing per-peril frequency × severity (or burning cost) models
   into a Risk Premium.
8. **Model lineage, comparison, and versioning.**

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Data cleaning, exposure derivation, claim linkage | `01-data-management.md` — modelling consumes a `validated` version and never mutates it |
| Rate tables, loadings, expenses, commission, DAG assembly | `03-rating-engine.md` — a Model produces a technical estimate, not a price |
| Demand/elasticity *use* in price setting | `04-optimisation.md` (demand models are fitted **here**, used there) |
| Live monitoring of a deployed model | `05-monitoring.md` |
| Approval mechanics (roles, inbox, decision records) | `06-governance.md` — this spec states *what* must be approved and *what evidence* accompanies it |

### 1.3 Hard rules

> **R1 — Fitting requires a `validated` Dataset Version.** No override (`01` §1.3).
>
> **R2 — A Model is immutable once fitted.** Refitting produces a new version with
> `parent_model_id` set. There is no "update the coefficients" operation.
>
> **R3 — A non-GLM Model cannot be referenced by a Rating Version without a
> Transparency Artifact** (FR-MODEL-33). Fitting a black box is allowed; pricing with an
> unexplained one is not.
>
> **R4 — A Model using a Custom Objective can only reach `approved` if that objective is
> itself `approved`** (FR-OVR-14).
>
> **R5 — Every estimate carries uncertainty.** Coefficients carry standard errors;
> predictions carry an interval or an explicit statement of why one is unavailable
> (`CLAUDE.md` §7).

---

## 2. Concepts & glossary

Terms from `00-overview.md` §2.2 are used unchanged. Additional terms owned here:

| Term | Definition |
|---|---|
| **Model Family** | The named lineage a Model belongs to (`motor-ad-frequency`). Model versions increment within a family; the family is what a Rating Version conceptually references, pinned to a specific version. |
| **Model Spec** | The complete, declarative, pre-fit description of a model: dataset version, response, weights/offset, factor list, model type, hyperparameters, objective, seed. Hashing the Model Spec gives a `spec_hash` that identifies "the same fit". |
| **Fit Result** | What fitting produced: coefficients or booster reference, convergence information, timings, library versions. |
| **Offset** | A known additive term on the linear predictor scale (log exposure for frequency). Distinct from a weight. |
| **Weight** | A per-row observation weight (claim counts for severity, exposure for burning cost). |
| **Relativity** | `exp(coefficient)` for a log-link GLM — the multiplicative effect of a Level relative to the Base Level. |
| **Banding Method** | How interval boundaries were derived: `manual`, `equal_width`, `quantile`, `exposure_quantile`, `tree`, `credibility`. Recorded so a reviewer sees the judgement. |
| **Grouping Method** | How Levels were merged: `manual`, `credibility_weighted`, `hierarchical_clustering`, `tree`, `reference_hierarchy`. |
| **Objective Certificate** | The persisted evidence that a Custom Objective passed its mathematical checks (§4.7): derivative agreement, convexity, boundary behaviour, and a fitted smoke test. Required for approval. |
| **Holdout** | The named split (from `01` FR-DATA-36) not used for fitting, on which reported performance is measured. |
| **Backtest** | Evaluation of a Model on a Dataset Version other than the one it was fitted on — typically a later period. |

---

## 3. Functional requirements

### 3.1 Factors

| ID | Requirement |
|---|---|
| **FR-MODEL-1** | A **Factor** is a named, versioned transformation over one or more columns of a Dataset Version, of exactly one type: `identity`, `banding`, `grouping`, `interaction`, `spline`, `polynomial`, `offset`, `expression`. No other types exist without a spec change. |
| **FR-MODEL-2** | Factors are defined against a Dataset (not a version) and are *resolved* against a specific version at fit time; resolution fails loudly if a required column is absent or has changed dtype. |
| **FR-MODEL-3** | A Factor declares its **actuarial intent**: `risk` (a genuine rating variable), `control` (present to absorb variance but not to be rated on, e.g. year-of-account), `offset`, or `diagnostic`. Rating Versions may only use `risk` factors; a `control` factor reaching a rate table is a validation error in `03`. |
| **FR-MODEL-4** | A Factor may declare a **monotonic direction** (`increasing`, `decreasing`, `none`) with a written rationale. The direction is enforced as a constraint in GBM fitting (FR-MODEL-20) and checked (not enforced) for GLMs, where a violation is reported as a diagnostic. |
| **FR-MODEL-5** | A Factor may declare a **prohibited** flag with a reason (e.g. a protected characteristic or a proxy the insurer has decided not to use). Prohibited factors cannot be added to any Model Spec; the attempt is refused and audited. |
| **FR-MODEL-82** | **Proxy detection is a Phase 3 deliverable, and never an automated block** (OQ-MODEL-7, decided 2026-08-15). Through Phases 1–2 the platform's only treatment of a protected characteristic is FR-MODEL-5's `prohibited` flag, which refuses direct use and audits the attempt; the platform holds no protected characteristics of its own (`00` FR-OVR-9). From Phase 3 an optional **proxy assessment** consumes an insurer-supplied reference table that does carry the characteristic, measures each candidate Factor's association with it — mutual information, and the AUC of the factor predicting it, exposure-weighted, with the reference population and its date recorded — and attaches the result to the approval request as evidence. It never refuses a Factor: whether an association amounts to unlawful discrimination is a legal judgement, not a statistical one, and a platform that answered it automatically would be answering a different question from the one asked. `04` FR-OPT-24 applies the same principle to price change. |
| **FR-MODEL-6** | `expression` factors use the restricted grammar of §4.6 — the same grammar as custom objectives and preparation recipes — evaluated over dataset columns only. |
| **FR-MODEL-7** | Factor definitions are reusable across Models and Model Families and are versioned independently; a Model Spec pins the exact Factor version it used. |

### 3.2 Bandings

| ID | Requirement |
|---|---|
| **FR-MODEL-8** | A **Banding** maps a continuous column to ordered, exhaustive, non-overlapping intervals with explicit boundaries, plus explicit handling of nulls and out-of-range values (`null_level`, `below_range`, `above_range`). |
| **FR-MODEL-9** | The platform can *propose* boundaries by `equal_width`, `quantile`, `exposure_quantile`, `tree` (a single shallow decision tree on the response, exposure-weighted), or `credibility` (merge until each band meets a minimum claim count). The proposal is always editable; the final boundaries are what is stored. |
| **FR-MODEL-10** | Every Banding stores its method, parameters, the Dataset Version it was derived on, and a per-band summary (exposure, claim count, observed frequency/severity/burning cost with confidence intervals) as of derivation — the evidence a reviewer needs without re-running anything. |
| **FR-MODEL-11** | A Banding validates against the Dataset Version at fit time: every band must meet configurable minimum exposure and minimum claim count, or fitting warns (default) or fails (if configured). Empty bands always fail. |
| **FR-MODEL-12** | Bandings are versioned artifacts with lineage; editing a banding creates a new version and does not alter any Model already fitted with the old one. |

### 3.3 Groupings

| ID | Requirement |
|---|---|
| **FR-MODEL-13** | A **Grouping** maps source Levels to target Levels, is exhaustive over observed Levels, and declares behaviour for unseen Levels at scoring time (`error`, `map_to_default`, `map_to_base`). Unseen-level behaviour is mandatory — there is no implicit default. |
| **FR-MODEL-14** | The platform can propose groupings by `credibility_weighted` (merge Levels whose credibility-adjusted relativities are within a tolerance), `hierarchical_clustering` (on relativity with exposure weights), `tree`, or `reference_hierarchy` (roll up via a Reference Table, e.g. outcode → rating area → region). Manual override is always available. |
| **FR-MODEL-80** | A `credibility_weighted` Grouping declares `credibility_model` ∈ `limited_fluctuation` (**default**) \| `buhlmann_straub` (OQ-MODEL-5, decided 2026-08-15). Limited fluctuation is the default because it is what a UK reviewer expects to see in a grouping justification: a full-credibility standard expressed in claim counts, stored with the `(p, k)` pair it was derived from (1 082 claims for ±5 % at 90 % confidence), and partial credibility `Z = sqrt(n / n_full)`. Bühlmann–Straub is selectable and persists its variance components — EVPV, VHM and the resulting `k` — in the grouping evidence, so a reviewer can re-derive `Z` rather than take it. The choice is recorded **per grouping** in `method_params` and stated in the model document: it is a modelling judgement, not a platform constant. |
| **FR-MODEL-15** | Every Grouping stores its method, parameters, source Level statistics, the resulting target Level statistics, and the *change in fit* (deviance delta, degrees of freedom saved) it implies — grouping is a modelling decision and must be defensible as one. |
| **FR-MODEL-16** | Groupings are first-class auditable operations: creation, edit, and use in a Model each emit Audit Events (FR-OVR-4), and a generated model document lists every grouping with its method and rationale. |
| **FR-MODEL-17** | A Grouping may be **hierarchical** — a chain of groupings applied in order (outcode → area → region) — so an actuary can retain the finer level for diagnostics while rating on the coarser one. |

### 3.4 GLM fitting

| ID | Requirement |
|---|---|
| **FR-MODEL-18** | GLMs are fitted with `glum`. Supported families: `poisson`, `negative_binomial`, `gamma`, `inverse_gaussian`, `tweedie(p)`, `binomial`, `gaussian`. Supported links: `log`, `logit`, `identity`, `inverse`, `power(k)`. |
| **FR-MODEL-19** | Actuarial defaults are applied unless explicitly overridden, and any override is recorded with a justification: **frequency** → Poisson, log link, `offset = log(exposure)`; **severity** → Gamma, log link, `weight = claim_count`; **burning cost** → Tweedie with `1 < p < 2`, log link, `weight = exposure`; **conversion/retention** → binomial, logit link. |
| **FR-MODEL-20** | Regularisation (L1, L2, elastic net) is supported with a documented path and a cross-validated selection option. The selected penalty and the full CV path are persisted as diagnostics. |
| **FR-MODEL-21** | Fitting returns, for every coefficient: estimate, standard error, z/t statistic, p-value, and confidence interval; and for every categorical Factor: the relativity table with the base level marked. These are persisted in the Model artifact (ADR-0003) and are re-scorable without `glum`. |
| **FR-MODEL-22** | The Tweedie power `p` may be estimated by profile likelihood over a grid, with the profile curve persisted. Estimated `p` is recorded as an estimate with its own uncertainty, not silently baked in as a constant. |
| **FR-MODEL-23** | Non-convergence, separation, rank deficiency, and aliased columns are surfaced as explicit, named fit errors with the offending factors identified — never as a silently returned degenerate fit. |
| **FR-MODEL-24** | An **offset from another model** is supported (`offset_model_ref`), enabling residual modelling and "fit on top of the current rating structure" workflows. The referenced model version is pinned. |

### 3.5 Gradient boosting (XGBoost / LightGBM)

| ID | Requirement |
|---|---|
| **FR-MODEL-25** | XGBoost is the primary GBM backend, LightGBM the secondary. Both are configured through one common `GbmSpec` contract; backend-specific parameters live in a namespaced `backend_params` block so the contract does not fork. |
| **FR-MODEL-26** | Insurance objectives are supported directly: `count:poisson`, `reg:gamma`, `reg:tweedie` (with `tweedie_variance_power`), `binary:logistic`, or a reference to an approved Custom Objective. |
| **FR-MODEL-27** | **Exposure is handled via `base_margin` (XGBoost) / `init_score` (LightGBM) set to `log(exposure)`**, never by passing exposure as a feature and never by weighting when the objective is a count. The platform constructs this automatically from the declared offset and refuses a frequency GBM spec that has neither an offset nor an explicit acknowledgement of why not. The raw score handed to a custom objective **already includes** the offset on **both** backends (verified against XGBoost 3.4.0 and LightGBM 4.7.0 — [`research`](../research/track-a-findings.md) F5, F13), so an objective must not add it again. The *scoring* side is not symmetric — see FR-MODEL-72. |
| **FR-MODEL-28** | **Monotone constraints** are derived automatically from Factor monotonic directions (FR-MODEL-4) and passed to the backend, with the resulting constraint vector persisted alongside the feature order so it is reproducible and reviewable. |
| **FR-MODEL-29** | Interaction constraints are supported, allowing an actuary to permit interactions only within declared groups of factors — the practical tool for keeping a GBM's structure explainable. |
| **FR-MODEL-30** | Early stopping requires a declared holdout or CV scheme; the chosen iteration count, the full evaluation curve, and the metric used are persisted. Early stopping on the training set is refused. |
| **FR-MODEL-31** | The booster is exported in the backend's JSON/text model format, stored content-addressed, and accompanied by feature order, dtype expectations, categorical encoding maps, `base_margin` construction, and pinned library version (ADR-0003). Pickling is refused at the persistence layer, not merely discouraged. |
| **FR-MODEL-71** | The `base_margin` / `init_score` construction is persisted with the booster and **asserted at load time**, because omitting it at scoring time fails *silently* on **both** backends — differently. Loading a GBM artifact whose offset cannot be reconstructed is a hard failure, never a warning. Verified empirically for XGBoost (F5) and LightGBM (F13). |
| **FR-MODEL-73** | **Large-loss treatment is a modelling decision applied at fit time, not a property baked into the dataset** (OQ-DATA-1, decided 2026-08-14). A Model Spec carries a `loss_treatment` — `none`, `capped` (cap plus the restoration loading that restores the mean), `spliced`, or `excess` — which is applied to the response as the model is fitted, and which forms part of `spec_hash`. Dataset Versions stay assumption-free, so one validated dataset serves many capping assumptions without re-ingestion or re-validation. `01` VR-ACT-10 flags large losses in the data but never removes them. |
| **FR-MODEL-74** | Because the dataset is uncapped and the model is not, **reconciliation must account for the treatment**: the Peril Structure's reconciliation (FR-MODEL-60) compares modelled burning cost *after* restoration against observed uncapped burning cost, and the generated dossier states the treatment alongside the reconciliation. Without this, a capped model reconciling to uncapped data looks like a modelling error rather than an intended adjustment. |
| **FR-MODEL-72** | **The offset is symmetric at fit time and asymmetric at scoring time; the scoring path must be implemented per backend.** Both backends include the offset in the raw score handed to a custom objective, so FR-MODEL-27 holds for both. But at prediction time: XGBoost re-applies the offset when it is set on the prediction `DMatrix`, whereas **LightGBM's `Booster.predict()` has no offset parameter at all** — it returns tree contributions only, and the caller must add `init_score` back to the raw score itself. A single "apply the offset" implementation written against XGBoost's API would **silently do nothing** on LightGBM and under-predict by exactly the offset. `pricing-core` therefore implements the scoring-side offset per backend, and a round-trip test asserts that `predict(fit_data)` reproduces the fitted raw score on **each** backend independently (F13). |
| **FR-MODEL-32** | Categorical handling is explicit: either the Factor supplies a grouping/encoding, or the backend's native categorical support is used with its parameters recorded. Silent label-encoding of an unordered categorical is refused. |

### 3.6 Transparency (non-GLM models)

| ID | Requirement |
|---|---|
| **FR-MODEL-33** | Every non-GLM Model must carry at least one **Transparency Artifact** before it can be referenced by a Rating Version (R3). Two forms are supported and both may be present. |
| **FR-MODEL-34** | **GLM approximation** — a GLM fitted to the GBM's own predictions over the modelling population, with the same factor set (optionally banded), reporting R² / deviance explained against the GBM, and the residual pattern where the approximation is worst. This is the artifact that turns a GBM into something rateable as a table. |
| **FR-MODEL-35** | **SHAP factor summary** — TreeSHAP mean absolute contribution per factor, per-factor dependence summaries (contribution vs factor value, exposure-weighted), and the top interaction pairs. Computed on a reproducible sample with a persisted seed and sample size. |
| **FR-MODEL-79** | **Interaction candidates found in TreeSHAP interaction values are suggestions, never additions** (OQ-MODEL-4, decided 2026-08-15). The transparency artifact ranks the top pairs (FR-MODEL-35) and the factor workbench surfaces each with its exposure share and its holdout lift, so an actuary sees what a suggestion is worth and over how much of the book. The platform never writes a Factor into a Model Spec: an interaction becomes rateable only as an explicit `interaction` Factor (FR-MODEL-1) carrying an intent and a written rationale (FR-MODEL-3), and the generated model document names it as an authored decision. Auto-detected structure entering a rating basis unreviewed is precisely the overfitting route this refuses. |
| **FR-MODEL-36** | The transparency artifact records an explicit **fidelity statement**: how well the approximation reproduces the model, where it does not, and the exposure share of the region where it does not. A Rating Version referencing the model surfaces this at approval time. |
| **FR-MODEL-37** | EBM (`interpret`) models are treated as transparent by construction: their term shape functions are exported directly as tables and require no approximation, but they still carry the fidelity/diagnostic sections in the same contract shape. |

### 3.7 Custom objectives

| ID | Requirement |
|---|---|
| **FR-MODEL-38** | A **Custom Objective** is a named, versioned artifact of `kind` ∈ `template` \| `expression`. It is defined once and reusable across Models, Model Families, and backends. |
| **FR-MODEL-39** | `template` objectives are parameterised standard forms with analytic gradients and hessians implemented and unit-tested in `pricing-core`. The shipped catalogue is in §4.5. A template objective carries no user code at all. |
| **FR-MODEL-40** | `expression` objectives let the user write the **per-observation loss** `L(y, f, w)` (where `f` is the raw score / linear predictor) in the restricted grammar of §4.6. The gradient and hessian are derived **symbolically at authoring time** (SymPy), stored as expressions in the artifact, reviewed as part of approval, and compiled to vectorised NumPy/Polars at fit time. User code is never executed at fit time; only the platform's own compiled expression tree is. |
| **FR-MODEL-41** | The restricted grammar admits only: numeric literals, the bound symbols `y`, `f`, `w`, declared parameters, arithmetic (`+ - * / **`), and the whitelisted functions `log`, `exp`, `sqrt`, `abs`, `min`, `max`, `clip`, `where`, `log1p`, `expm1`. No names, attributes, calls, comprehensions, loops, conditionals, or indexing beyond `where`. AST nodes are capped (default 200). Parsing is by explicit AST walk with an allow-list, never `eval`. |
| **FR-MODEL-42** | Every objective must pass the **Objective Certificate** checks of §4.7 before it can be submitted for approval: symbolic-vs-numeric derivative agreement, hessian non-negativity over the sampled domain, boundary/finiteness behaviour, and a smoke fit on a synthetic dataset that recovers known parameters. The certificate is persisted and attached to the approval request. |
| **FR-MODEL-68** | The derivative-agreement check must **exclude sampled points within the finite-difference step `h` of a `Piecewise` branch boundary**, and report the excluded count. A central difference straddling a kink is invalid, so without this exclusion the check fails every `where()`-based objective for a reason that has nothing to do with correctness (verified empirically — see [`research/track-a-findings.md`](../research/track-a-findings.md) F3). |
| **FR-MODEL-69** | Branch boundaries are themselves a **reported finding**, not merely an exclusion: the certificate records where the gradient or hessian is discontinuous and over what share of the sampled domain. A discontinuous hessian affects boosting stability and an approver must see it. |
| **FR-MODEL-70** | Derivative-agreement tolerances are **step-aware**. Truncation error alone reaches ~4e-04 at `h = 1e-6` on a steeply-curved loss, so a fixed tight tolerance is not meaningful. Richardson extrapolation is used where the loss is smooth; the achieved tolerance and the method are recorded on the certificate. |
| **FR-MODEL-75** | **Phase 1 ships `template` objectives only; `expression` objectives ship in Phase 2** (OQ-MODEL-1, decided 2026-08-15). The `expression` kind is gated by the `expression_objectives_enabled` feature flag (`07` FR-PLAT-45/46), which defaults to off and stays off for the whole of Phase 1: `POST /custom-objectives` with `kind: expression` and `POST /custom-objectives/{id}/derive` are refused with `OBJECTIVE_KIND_NOT_ENABLED` rather than accepted and left uncertifiable. Nothing in §4.6 is withdrawn — the grammar is specified, and its parser is already built and in use for `01` FR-DATA-10 — so what Phase 2 adds is the symbolic derivation, a **second compilation target** (vectorised gradient and hessian kernels, where the existing parser emits Polars expressions), and the review path for a user-authored loss. |
| **FR-MODEL-76** | **The certification machinery of §4.7 is built in Phase 1, against templates** (OQ-MODEL-1). FR-MODEL-42 is not weakened for templates: every Custom Objective version carries an `ObjectiveCertificate` before submission whatever its `kind`. One check substitutes — for `kind: template` the derivative-agreement check compares `pricing-core`'s **analytic** gradient and hessian against the numeric derivative (`analytic_vs_numeric`), where an `expression` objective compares the SymPy-derived form (`symbolic_vs_numeric`). Finiteness, convexity, branch discontinuity (FR-MODEL-68/69), step-aware tolerance (FR-MODEL-70) and the smoke fit are identical for both kinds. Expressions therefore arrive in Phase 2 as a new front end onto proven machinery, not as a new subsystem certified for the first time by its riskiest input. |
| **FR-MODEL-43** | A non-convex objective (hessian negative anywhere in the sampled domain) is not refused outright — some legitimate pricing losses are non-convex — but is flagged `convexity: violated`, requires the hessian clipping strategy to be declared (`clip_to_min`, `abs`, `gauss_newton`), and requires an additional Approver. |
| **FR-MODEL-44** | Objectives declare their **applicability**: which responses (`claim_count`, `claim_severity`, `burning_cost`, …), which backends (`xgboost`, `lightgbm`, `glm`), whether an offset is required, and the valid range of `y`. A Model Spec pairing an objective with an inapplicable response is refused at spec validation, before any compute is spent. |
| **FR-MODEL-45** | Custom eval metrics (`feval`) follow the same lifecycle and grammar as objectives, declared separately so that a metric can be reused across objectives. |
| **FR-MODEL-46** | Custom Objective lifecycle is `draft → certified → review → approved → deprecated`. Approval is by an Approver who is not the author; `expression` objectives with `convexity: violated` need two Approvers (FR-MODEL-43). Editing an `approved` objective creates a new version requiring fresh certification and approval. |
| **FR-MODEL-47** | Objective usage is fully traceable: for any objective version, the platform lists every Model, Rating Version, and live Deployment using it — the blast-radius query needed when a defect is found. |
| **FR-MODEL-48** | Objective execution is resource-bounded: compiled expressions are evaluated on fixed-size NumPy arrays with no allocation of unbounded intermediates, wall-clock is budgeted per boosting round, and NaN/inf appearing in a gradient or hessian aborts the fit with a named error identifying the round and the offending input range. |

### 3.8 Diagnostics

| ID | Requirement |
|---|---|
| **FR-MODEL-49** | Every fit produces a persisted **Diagnostics** artifact. Diagnostics are computed once at fit time and read thereafter; the UI never recomputes them. |
| **FR-MODEL-50** | Universal diagnostics (all model types): actual-vs-expected by factor level and by banded continuous factor (exposure-weighted, with CIs); lift/gains curves by predicted decile; double lift vs a comparison model; Gini / normalised Gini; calibration by predicted decile; residual summaries; overall A/E ratio on train and holdout. |
| **FR-MODEL-51** | GLM-specific diagnostics: deviance, null deviance, AIC/BIC, dispersion estimate, degrees of freedom, per-factor type-III deviance test with p-value, relativity plots with confidence bands, standardised deviance and Pearson residual plots, leverage/Cook's distance on a sample, and a VIF/aliasing report. |
| **FR-MODEL-52** | GBM-specific diagnostics: evaluation curve per iteration for train and holdout, gain/cover/frequency importance, permutation importance on the holdout, partial dependence for declared factors, monotonicity verification (that the fitted response actually respects declared constraints), and tree-count/depth summary. |
| **FR-MODEL-53** | Cross-validation is supported with declared fold construction (`random`, `temporal`, `grouped_by_key`) and a persisted seed; per-fold metrics and their dispersion are persisted, not just the mean. |
| **FR-MODEL-54** | Diagnostics are computed on **train and holdout separately and always reported side by side**. A diagnostic reported without its holdout counterpart is a defect. |
| **FR-MODEL-55** | Metrics are recorded with their weighting scheme explicit (exposure-weighted vs unweighted vs claim-count-weighted). An unweighted metric on an exposure-weighted problem is labelled as such in the UI. |
| **FR-MODEL-81** | **Model complexity is a diagnostic by default, and a gate only where a workspace asks for one** (OQ-MODEL-6, decided 2026-08-15). Every fit records its factor count, its fitted-parameter count, and its exposure-per-parameter and claims-per-parameter ratios in the diagnostics, beside whatever thresholds are in force. The workspace settings `modelling.max_factor_count` and `modelling.min_exposure_per_parameter` (`07` FR-PLAT-45) are **unset by default**; where a workspace sets one, `POST /model-specs/validate` and `POST /models` refuse a breaching spec with `MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT` before any compute is spent, and the refusal is audited. There is no platform-wide constant: a large book legitimately supports a large model, and whether *this* model is overfitted is a judgement for the Approver with the diagnostic in front of them (`06`), not for a number chosen here. |
| **FR-MODEL-56** | Model comparison is a first-class operation: two or more Models fitted on the same holdout can be compared on aligned metrics, double-lift, and factor-by-factor relativity differences, producing a persisted comparison artifact citable in an approval request. |
| **FR-MODEL-57** | A **backtest** on a later Dataset Version is supported and produces the same diagnostic shapes, marked with the version it ran against. Backtests are the evidence bridge into `05-monitoring.md`. |

### 3.9 Peril structure and risk premium

| ID | Requirement |
|---|---|
| **FR-MODEL-58** | A **Peril Structure** declaratively composes Models into a Risk Premium: per peril, either `frequency × severity` or `burning_cost`, summed over perils, with per-peril model references pinned by version. |
| **FR-MODEL-59** | The structure declares how large losses are handled per peril: `none`, `capped` (with the cap and the loading applied to restore the mean), `separate_model` (an excess-layer model), or `flat_loading`. Whatever is chosen is recorded with its calibration evidence. |
| **FR-MODEL-60** | The structure is validated for coherence: every peril present in the dataset is either modelled or explicitly excluded with a reason; total modelled burning cost reconciles to observed burning cost within a declared tolerance on the holdout, and the reconciliation is persisted. |
| **FR-MODEL-61** | A Peril Structure is an approvable artifact in its own right and is what `03-rating-engine.md` references — a Rating Version references a Peril Structure, not a scatter of individual models. |

### 3.10 Prediction and lifecycle

| ID | Requirement |
|---|---|
| **FR-MODEL-62** | `pricing-core` can score any persisted Model from its declarative artifact alone (ADR-0003), with no dependency on the fitting session. GLM scoring requires no `glum`; GBM scoring loads the JSON booster. |
| **FR-MODEL-63** | Prediction returns the expectation plus an uncertainty measure: GLM prediction intervals from the covariance matrix; GBM either quantile-model-based intervals or an explicit `uncertainty: unavailable` with the reason (R5). |
| **FR-MODEL-77** | **A GBM prediction states `uncertainty: unavailable` with a typed `reason` unless interval models were fitted for it** (OQ-MODEL-2, decided 2026-08-15) — `no_interval_models_fitted`, `interval_models_not_approved`, or `interval_models_stale` (fitted against a superseded Model version). **The variance-model approximation is not offered at all**, at any setting: it is cheap, it renders as a predictive interval, and it is not one — and a wrong interval on a price is worse than no interval. R5 is satisfied by the explicit statement of absence, never by an approximation that reads like a measurement. |
| **FR-MODEL-78** | **Paired quantile models are the supported route to a GBM prediction interval, opt-in and explicit** (OQ-MODEL-2). Each bound is a Model in its own right — same Model Family, same dataset version, split and factor set, fitted with the `quantile` template (§4.5) at a declared `alpha` — carrying `interval_for`, which names the central Model version and the alpha it estimates, so the 2–3× fit cost is a choice the actuary makes and can see. Crossing quantiles (a lower bound above its upper at any prediction) are **detected, reported in the diagnostics, and never silently reordered**: crossing means the pair does not describe one distribution, which the reader must be told rather than protected from. Whether §4.8 carries `interval_for` before the slice that fits one exists is OQ-MODEL-8's question, not this one. |
| **FR-MODEL-64** | Model lifecycle is `draft → fitted → review → approved → superseded → archived`. `fitted` requires diagnostics; `review` requires diagnostics, a transparency artifact where applicable, and a completed model-document draft; `approved` is by an Approver who is not the author (`06-governance.md`). |
| **FR-MODEL-65** | Model lineage records `parent_model_id` and a typed `change_reason` (`refit_new_data`, `respecified`, `rebanded`, `regrouped`, `hyperparameter_change`, `objective_change`, `bug_fix`) so a family's history reads as a narrative. |
| **FR-MODEL-66** | The `spec_hash` (§2, Model Spec) is computed over the canonicalised spec including pinned versions and seed. Submitting an identical spec returns the existing Model instead of refitting, unless `force_refit` is set — which then requires the two fits to be compared for reproducibility (FR-OVR-8). |
| **FR-MODEL-67** | A Model whose Dataset Version was invalidated (`01` FR-DATA-23) is flagged `dataset_invalidated` and cannot advance to `approved`; if already `approved`, the flag propagates to every Rating Version referencing it and to the Approvals inbox. |

---

## 4. Data contracts

Schemas in `docs/contracts/schemas/`. All entities carry `ArtifactEnvelope` (`00` §4.3).

### 4.1 `Factor`

```json
{
  "slug": "driver_age_banded",
  "dataset_id": "uuid",
  "version": 3,
  "type": "banding",
  "source_columns": ["driver_age"],
  "intent": "risk",
  "monotonic_direction": "decreasing",
  "monotonic_rationale": "Claim frequency falls with age above 25; enforced to prevent noise-driven reversals in thin bands.",
  "prohibited": false,
  "prohibited_reason": null,
  "banding_id": "uuid",
  "grouping_id": null,
  "expression": null,
  "base_level": "36-45",
  "base_level_method": "largest_exposure"
}
```

### 4.2 `Banding`

```json
{
  "slug": "driver-age-actuarial-v2",
  "column": "driver_age",
  "method": "exposure_quantile",
  "method_params": {"n_bands": 10, "min_claims_per_band": 200},
  "derived_on_dataset_version_id": "uuid",
  "boundaries": [17, 21, 25, 30, 36, 46, 56, 66, 76, 999],
  "closed": "left",
  "labels": ["17-20", "21-24", "25-29", "30-35", "36-45", "46-55", "56-65", "66-75", "76+"],
  "null_level": "unknown",
  "below_range": "error",
  "above_range": "clamp_to_last",
  "band_stats": [
    {"label": "17-20", "exposure_years": "38214.4", "claim_count": 5120,
     "frequency": 0.1340, "frequency_ci": [0.1304, 0.1377],
     "severity_minor": 412_800, "burning_cost_minor": 55_315}
  ]
}
```

**Invariants** — boundaries strictly increasing; bands exhaustive over the observed range;
`labels` length = `len(boundaries) - 1`; no empty band (FR-MODEL-11).

### 4.3 `Grouping`

```json
{
  "slug": "vehicle-group-to-rating-group",
  "column": "abi_vehicle_group",
  "method": "credibility_weighted",
  "method_params": {"credibility_model": "limited_fluctuation",
                    "credibility_standard_claims": 1082, "credibility_pk": {"p": 0.90, "k": 0.05},
                    "merge_tolerance_relativity": 0.05},
  "derived_on_dataset_version_id": "uuid",
  "mapping": {"1": "G1", "2": "G1", "3": "G1", "4": "G2", "…": "…"},
  "unseen_level_behaviour": "map_to_default",
  "default_target_level": "G4",
  "parent_grouping_id": null,
  "evidence": {
    "source_level_count": 50, "target_level_count": 8,
    "credibility_components": null,
    "deviance_before": 184221.4, "deviance_after": 184388.1,
    "df_saved": 42, "chi2_p_value": 0.31,
    "target_level_stats": [{"level": "G1", "exposure_years": "180422.1", "claim_count": 19204, "relativity": 0.78}]
  }
}
```

`credibility_model` defaults to `limited_fluctuation` and is recorded per grouping
(FR-MODEL-80). `credibility_pk` is the `(p, k)` pair the standard was derived from — 1 082
claims is ±5 % at 90 % confidence, and a reviewer who cannot see `(p, k)` cannot tell 1 082
from a house number. `credibility_components` carries Bühlmann–Straub's EVPV, VHM and `k`
and is `null` under limited fluctuation.

### 4.4 `ModelSpec` (tagged union on `model_type`)

Common block:

```json
{
  "model_family_slug": "motor-ad-frequency",
  "dataset_version_id": "uuid",
  "split_ref": {"split_artifact_id": "uuid", "train_part": "train", "holdout_part": "test"},
  "peril": "AD",
  "response": "claim_count",
  "response_column": "ad_claim_count",
  "offset": {"kind": "log_column", "column": "exposure_years"},
  "weight": {"kind": "none"},
  "factors": [{"factor_id": "uuid", "factor_version": 3}],
  "filter": null,
  "loss_treatment": {"kind": "capped", "cap_minor": 2_500_000,
                     "restoration_loading": 1.043, "evidence_blob": "blob:sha256:…"},
  "seed": 20260814,
  "model_type": "glm | xgboost | lightgbm | ebm"
}
```

`loss_treatment` is part of the spec — and therefore of `spec_hash` — because capping is
applied to the **response at fit time** (FR-MODEL-73). Two models differing only in their
cap are different models, and must not collide on `spec_hash`.

`GlmSpec` adds:

```json
{
  "family": "poisson",
  "family_params": {},
  "link": "log",
  "regularisation": {"kind": "elastic_net", "alpha": 0.001, "l1_ratio": 0.0,
                     "select_by": "cv", "cv_folds": 5},
  "custom_objective_ref": null,
  "max_iter": 200, "tolerance": 1e-8
}
```

`GbmSpec` adds:

```json
{
  "backend": "xgboost",
  "objective": {"kind": "builtin", "name": "count:poisson"},
  "base_margin": {"kind": "log_column", "column": "exposure_years"},
  "monotone_constraints": "derived_from_factors",
  "interaction_constraints": [["driver_age_banded", "vehicle_group_rated"], ["ncd", "annual_mileage"]],
  "hyperparameters": {"max_depth": 5, "eta": 0.05, "subsample": 0.8,
                      "colsample_bytree": 0.8, "min_child_weight": 200,
                      "lambda": 1.0, "alpha": 0.0, "num_boost_round": 2000},
  "early_stopping": {"on": "holdout", "metric": "poisson-nloglik", "rounds": 50},
  "categorical_handling": "native",
  "backend_params": {"tree_method": "hist"},
  "eval_metrics": [{"kind": "builtin", "name": "poisson-nloglik"},
                   {"kind": "custom", "ref": "custom_metric:capped-gamma-nll@2"}]
}
```

`objective.kind = "custom"` replaces `name` with `ref: "custom_objective:<slug>@<version>"`.

### 4.5 Custom objective — `template` catalogue

Shipped templates, each with analytic gradient/hessian in `pricing-core` (FR-MODEL-39):

| Template | Params | Loss (per observation, `f` = raw score, `μ = exp(f)` for log-link forms) | Typical use |
|---|---|---|---|
| `poisson` | — | `μ − y·f` | Frequency baseline |
| `gamma` | — | `y/μ + f` | Severity baseline |
| `tweedie` | `p ∈ (1,2)` | `−y·μ^(1−p)/(1−p) + μ^(2−p)/(2−p)` | Burning cost; `p` tunable and CV-selectable |
| `capped_gamma` | `cap` (minor units) | Gamma loss on `min(y, cap)`, plus a recorded loading to restore the uncapped mean | Large-loss-adjusted severity |
| `spliced_severity` | `threshold`, `tail_shape` | Gamma below threshold, Pareto-style tail above | Attritional vs large split in one model |
| `asymmetric_squared` | `w_under`, `w_over` | `w_under·(y−μ)²` if `μ < y` else `w_over·(y−μ)²` | Under-pricing penalised harder than over-pricing |
| `asymmetric_poisson` | `w_under`, `w_over` | Poisson deviance with side-dependent weights | Same intent, count response |
| `huber` | `delta` | Quadratic within `delta`, linear beyond | Outlier-robust burning cost |
| `pseudo_huber` | `delta` | Smooth Huber (twice differentiable everywhere) | Preferred where hessian smoothness matters |
| `quantile` | `alpha` | Pinball loss | Paired quantile models — the only supported GBM prediction interval (FR-MODEL-63, FR-MODEL-78) |
| `zero_inflated_poisson` | `pi_link` | ZIP negative log-likelihood | Very low-frequency perils |
| `focal_binomial` | `gamma` | Focal loss on logistic | Heavily imbalanced conversion models |

Each template declares its `applicability` block (FR-MODEL-44) and its own parameter
validity ranges (e.g. `tweedie.p ∈ (1, 2)` exclusive, `cap > 0`).

**This catalogue is the whole of Phase 1's custom-objective surface** (FR-MODEL-75,
OQ-MODEL-1 decided 2026-08-15): `expression` objectives ship in Phase 2, behind a flag that
is off until they do. A template still certifies (§4.7, FR-MODEL-76) — the machinery is
built here, on losses whose derivatives `pricing-core` already knows, so that the first
user-authored loss meets a certification path that has been running for a phase.

### 4.6 Restricted expression grammar

Shared by `expression` custom objectives (FR-MODEL-40), `expression` factors
(FR-MODEL-6), preparation `derive_expression` (`01` FR-DATA-10), and `expression`
validation checks (`01` §4.5). One grammar, one parser, one security review.

```ebnf
expr      = term , { ("+" | "-") , term } ;
term      = factor , { ("*" | "/") , factor } ;
factor    = unary , [ "**" , factor ] ;
unary     = [ "-" ] , primary ;
primary   = number | symbol | func "(" arglist ")" | "(" expr ")" ;
func      = "log" | "exp" | "sqrt" | "abs" | "min" | "max"
          | "clip" | "where" | "log1p" | "expm1" ;
symbol    = bound_symbol | parameter ;
```

Rules enforced by the parser (FR-MODEL-41):

- Bound symbols are context-fixed: objectives get `y`, `f`, `w`; factors get the declared
  dataset columns; nothing else resolves.
- Parameters must be declared in the artifact with a type, a default, and a valid range.
- Comparison operators exist **only** inside `where(cond, a, b)`, whose condition is
  restricted to a single comparison between two sub-expressions.
- No attribute access, subscripting, calls to undeclared names, lambdas, comprehensions,
  loops, or assignment. Parsing is a Python `ast` walk against an allow-list of node types;
  `eval` is never called on user input.
- AST node count ≤ 200 (configurable); nesting depth ≤ 20.
- Division by a sub-expression that can be zero over the declared domain of `y`/`f` is a
  certification failure, not a runtime surprise.

Example `expression` objective — under-pricing penalised twice as hard, on a log link:

```json
{
  "slug": "asymmetric-burning-cost",
  "kind": "expression",
  "bound_symbols": ["y", "f", "w"],
  "parameters": [
    {"name": "w_under", "type": "float", "default": 2.0, "min": 1.0, "max": 10.0},
    {"name": "w_over",  "type": "float", "default": 1.0, "min": 0.1, "max": 10.0}
  ],
  "loss": "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
  "derived": {
    "gradient": "where(y > exp(f), 2*w*w_under*(exp(f) - y)*exp(f), 2*w*w_over*(exp(f) - y)*exp(f))",
    "hessian":  "where(y > exp(f), 2*w*w_under*(2*exp(f) - y)*exp(f), 2*w*w_over*(2*exp(f) - y)*exp(f))",
    "derivation_tool": "sympy", "derivation_version": "1.14.0",
    "derived_at": "2026-08-14T11:02:00Z"
  },
  "hessian_strategy": "clip_to_min",
  "hessian_min": 1e-6,
  "applicability": {
    "responses": ["burning_cost", "claim_severity"],
    "backends": ["xgboost", "lightgbm"],
    "offset_required": false,
    "y_domain": {"min_inclusive": 0}
  }
}
```

The `derived` block is generated by the platform, never hand-written, and is what a
reviewer reads. The form shown is the **canonical** one SymPy produces — the branch is
lifted outside the arithmetic. An algebraically equivalent form with the branch as an inner
factor is *not* what the tool emits, and the certificate records the canonical form so that
two reviewers reading the same objective read the same text.

Note this example's hessian is negative wherever `exp(f) < y/2` — it is non-convex, so it
needs `hessian_strategy` and a second Approver (FR-MODEL-43). It also has a **kink** at
`exp(f) = y`, which FR-MODEL-68/69 exist to handle.

### 4.7 `ObjectiveCertificate`

Produced by `POST /custom-objectives/{id}/certify`; required for submission (FR-MODEL-42).

```json
{
  "custom_objective_id": "uuid", "objective_version": 1,
  "checks": [
    {"name": "symbolic_vs_numeric_gradient", "status": "pass",
     "detail": "max relative error 8.9e-7 over 9,959 sampled (y,f,w) points (41 excluded near the branch boundary); h=1e-6, Richardson-extrapolated"},
    {"name": "symbolic_vs_numeric_hessian", "status": "pass",
     "detail": "max relative error 3.8e-4, within the step-aware tolerance for h=1e-6 on a loss of this curvature (FR-MODEL-70)"},
    {"name": "finiteness", "status": "pass",
     "detail": "no NaN/inf for y ∈ [0, 1e7], f ∈ [-20, 20], w ∈ (0, 1e4]"},
    {"name": "convexity", "status": "violated",
     "detail": "hessian < 0 wherever exp(f) < y/2 — 63.9% of this sampling grid; strongly dependent on y_range/f_range, so the share is only meaningful alongside the sampling block below. Mitigated by hessian_strategy=clip_to_min"},
    {"name": "branch_discontinuity", "status": "warn",
     "detail": "gradient and hessian are discontinuous at the branch boundary exp(f) = y; 41 of 10,000 sampled points fell within h of it and were excluded from the derivative comparison (FR-MODEL-68/69)"},
    {"name": "minimum_at_truth", "status": "pass",
     "detail": "loss minimised at f = log(y) for w_under=w_over"},
    {"name": "monotone_loss", "status": "pass", "detail": "loss increases with |exp(f) − y|"},
    {"name": "scale_behaviour", "status": "warn",
     "detail": "loss scales quadratically with y; gradient magnitude spans 6 orders over the observed y range — consider a log-scale variant"},
    {"name": "smoke_fit", "status": "pass",
     "detail": "recovered known relativities on synthetic data (n=200k) within 1.2%; 300 rounds, 41s"}
  ],
  "sampling": {"n_points": 10000, "seed": 20260814,
               "y_range": [0, 10000000], "f_range": [-20, 20], "w_range": [0.001, 10000]},
  "overall": "certified_with_findings",
  "_note": "Figures above are illustrative of the shape of a real certificate. The convexity share and error magnitudes are those measured for this objective on this sampling grid (research/track-a-findings.md F3/F4); they are not constants.",
  "library_versions": {"sympy": "1.13.x", "numpy": "2.x", "xgboost": "2.x"}
}
```

`overall` ∈ `certified` | `certified_with_findings` | `failed`. A `failed` certificate
blocks submission entirely.

For `kind: template` the first two checks are named `analytic_vs_numeric_gradient` and
`analytic_vs_numeric_hessian` — the comparison is against `pricing-core`'s analytic
derivatives rather than a SymPy-derived form (FR-MODEL-76). Every other check, and the
`sampling` block that makes the findings interpretable, is identical for both kinds.

### 4.8 `Model`

```json
{
  "model_family_slug": "motor-ad-frequency",
  "version": 7,
  "status": "draft | fitted | review | approved | superseded | archived",
  "spec": { "…ModelSpec…" },
  "spec_hash": "sha256:…",
  "fit_result": {
    "model_type": "glm",
    "converged": true, "iterations": 23, "fit_seconds": 184.2,
    "coefficients": [
      {"term": "intercept", "estimate": -2.4181, "std_error": 0.0121, "z": -199.8, "p_value": 0.0,
       "ci_95": [-2.4418, -2.3944]},
      {"term": "driver_age_banded[17-20]", "estimate": 0.5412, "std_error": 0.0184,
       "z": 29.4, "p_value": 0.0, "ci_95": [0.5051, 0.5773], "relativity": 1.718,
       "exposure_years": "38214.4"}
    ],
    "dispersion": 1.042,
    "covariance_blob": "blob:sha256:…",
    "booster_blob": null,
    "library_versions": {"glum": "3.x", "polars": "1.x"}
  },
  "diagnostics_id": "uuid",
  "transparency_artifact_id": null,
  "custom_objective_ref": null,
  "parent_model_id": "uuid|null",
  "change_reason": "refit_new_data",
  "flags": ["dataset_invalidated"],
  "approval_request_id": "uuid|null"
}
```

**Invariants** — `status ≥ fitted` ⟹ `diagnostics_id` set; `model_type ≠ glm` and
`status = approved` ⟹ `transparency_artifact_id` set (R3); `custom_objective_ref` set and
`status = approved` ⟹ that objective version is `approved` (R4); `booster_blob` present
iff `model_type ∈ {xgboost, lightgbm}`.

### 4.9 `TransparencyArtifact`

```json
{
  "model_id": "uuid",
  "kinds": ["glm_approximation", "shap_summary"],
  "glm_approximation": {
    "approximating_model_id": "uuid",
    "target": "gbm_prediction",
    "r_squared": 0.973, "deviance_explained": 0.968,
    "worst_regions": [
      {"description": "driver_age < 21 AND annual_mileage > 20000",
       "exposure_share": 0.008, "mean_abs_error_pct": 11.4}
    ],
    "relativity_table_blob": "blob:sha256:…"
  },
  "shap_summary": {
    "sample_rows": 200000, "seed": 20260814, "algorithm": "tree_shap",
    "mean_abs_contribution": [{"factor": "vehicle_group_rated", "value": 0.181},
                              {"factor": "driver_age_banded", "value": 0.144}],
    "dependence_blob": "blob:sha256:…",
    "top_interactions": [{"pair": ["driver_age_banded", "ncd"], "strength": 0.041}]
  },
  "fidelity_statement": "The GLM approximation reproduces 97.3% of GBM prediction variance. Divergence concentrates in young high-mileage risks (0.8% of exposure, mean |error| 11.4%), where the GBM is materially higher. Rating on the approximation would under-price that cell.",
  "monotonicity_verified": true
}
```

### 4.10 `PerilStructure`

```json
{
  "slug": "motor-gb-2026h2",
  "version": 2,
  "perils": [
    {"peril": "AD", "method": "frequency_severity",
     "frequency_model": "model:motor-ad-frequency@7",
     "severity_model": "model:motor-ad-severity@5",
     "large_loss": {"kind": "capped", "cap_minor": 2_500_000, "restoration_loading": 1.043,
                    "evidence_blob": "blob:sha256:…"}},
    {"peril": "TP_BI", "method": "frequency_severity",
     "frequency_model": "model:motor-tpbi-frequency@4",
     "severity_model": "model:motor-tpbi-severity@3",
     "large_loss": {"kind": "separate_model", "excess_model": "model:motor-tpbi-excess@2",
                    "attachment_minor": 100_000_000}},
    {"peril": "WINDSCREEN", "method": "burning_cost",
     "burning_cost_model": "model:motor-ws-bc@2", "large_loss": {"kind": "none"}}
  ],
  "excluded_perils": [{"peril": "COURTESY_CAR", "reason": "Bundled service cost, loaded flat in the rating algorithm."}],
  "reconciliation": {
    "dataset_version_id": "uuid", "part": "holdout",
    "observed_burning_cost_minor": 18_412, "modelled_burning_cost_minor": 18_337,
    "ratio": 0.9959, "tolerance": 0.02, "status": "pass"
  },
  "status": "approved"
}
```

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/factors` | Create/version a Factor (FR-MODEL-1) |
| `GET` | `/api/v1/factors?dataset={slug}` | List factors with intent, monotonic direction, prohibited flag |
| `POST` | `/api/v1/bandings/propose` | Propose boundaries by method against a dataset version (FR-MODEL-9) |
| `POST` | `/api/v1/bandings` | Persist a Banding (with editable boundaries) |
| `POST` | `/api/v1/groupings/propose` | Propose a grouping by method (FR-MODEL-14) |
| `POST` | `/api/v1/groupings` | Persist a Grouping |
| `POST` | `/api/v1/model-specs/validate` | Validate a spec without fitting: factors resolve, offsets sane, objective applicable (FR-MODEL-44) |
| `POST` | `/api/v1/models` | **202** Fit → Job; returns existing model on `spec_hash` match (FR-MODEL-66) |
| `GET` | `/api/v1/models/{slug}?version=` | Model artifact — latest, or a named version |
| `GET` | `/api/v1/models/{id}/diagnostics` | Diagnostics artifact |
| `POST` | `/api/v1/models/{id}/transparency` | **202** Build a transparency artifact (FR-MODEL-33) |
| `POST` | `/api/v1/models/{id}/backtest` | **202** Backtest against another dataset version (FR-MODEL-57) |
| `POST` | `/api/v1/models/compare` | **202** Comparison artifact for 2+ models on a shared holdout (FR-MODEL-56) |
| `POST` | `/api/v1/models/{id}/predict` | Score rows (dev/debug scale; production scoring is `03`) |
| `POST` | `/api/v1/models/{id}/submit` | Submit for approval (`06`) |
| `POST` | `/api/v1/custom-objectives` | Create → `draft` (FR-MODEL-38) |
| `POST` | `/api/v1/custom-objectives/{id}/derive` | Symbolically derive gradient/hessian from `loss` (FR-MODEL-40) |
| `POST` | `/api/v1/custom-objectives/{id}/certify` | **202** Run the certificate checks (FR-MODEL-42) |
| `POST` | `/api/v1/custom-objectives/{id}/submit` | Submit for approval (FR-MODEL-46) |
| `GET` | `/api/v1/custom-objectives/{id}/usage` | Blast radius: models, rating versions, deployments (FR-MODEL-47) |
| `POST` | `/api/v1/custom-metrics` | Same lifecycle for eval metrics (FR-MODEL-45) |
| `POST` | `/api/v1/peril-structures` | Create/version a Peril Structure (FR-MODEL-58) |
| `POST` | `/api/v1/peril-structures/{id}/reconcile` | **202** Recompute reconciliation (FR-MODEL-60) |

> **Amended 2026-08-15 (W5, the GLM spine).** Two corrections, made by building it:
>
> * `GET /models/{slug}@{version}` becomes `GET /models/{slug}?version=`. An `@` in a path
>   segment is legal but must be percent-encoded by every client, and `model-family@7` then
>   arrives as `model-family%407` in logs, dashboards and support conversations. The
>   version is an optional query parameter, defaulting to the latest.
> * `POST /models` answers **202 with a Job** for a new fit and **200 with the Model** when
>   the specification has already been fitted (FR-MODEL-66). The table said 202; the second
>   case is not "work has started" and should not claim to be.
>
> What is built of this table as at 2026-08-15: `POST`/`GET /factors`, `POST /models`,
> `GET /models/{slug}`. The rest — bandings, groupings, spec validation, diagnostics,
> transparency, backtests, comparison, prediction, custom objectives, metrics and peril
> structures — is declared and unbuilt, and `scope-audit.py MODEL --endpoints` says so.

> **Amended 2026-08-15, after three independent audits of the spine.** Four corrections
> where the code was right and this document was not, and one where neither was:
>
> * **§4.1's `base_level_method: largest_exposure` is now what the code does.** It chose
>   the first level alphabetically. Every other level's relativity is expressed against the
>   base, so a base holding 5 % of the exposure gave every relativity the standard error of
>   a thin cell.
> * **A relativity does not exist under every link.** `RelativityLevel.relativity` is
>   `float | None`, with `estimate` beside it. Reporting `exp(β)` as 1.0 for a `logit`
>   model said "no effect" for a factor spanning eighteen log-odds.
> * **The Tweedie power is validated on the spec, not at fit time.** It is a fact about the
>   specification, and a spec that cannot be fitted should not be storable.
> * **§5.2's `fit_glm` signature takes `factors` explicitly.** `spec.factors` holds ids and
>   resolving them needs a database, which ADR-0001 forbids `pricing-core`. The spec's
>   signature is unimplementable as written; `00` §5.5 carries the same correction.
> * **`progress` was dropped from `fit_glm` and should not have been.** `00` §5.5 requires
>   the injected callback, and a long fit currently sits at 35 % for its whole duration.
>   Recorded as a gap rather than quietly removed from the interface.
>
> `02` §4's field sets (§4.1, §4.4, §4.8) still declare more than the spine implements —
> `split_ref`, `loss_treatment`, `diagnostics_id` and others. That is a **larger divergence
> awaiting a decision**, not an oversight: whether the spine grows to meet §4 or §4 narrows
> to a staged contract is a design choice, recorded in `docs/open-questions.md` as
> OQ-MODEL-8 rather than settled here.

**Error codes owned by this module:** `DATASET_NOT_VALIDATED` (re-raised from `01`),
`FACTOR_PROHIBITED`, `FACTOR_RESOLUTION_FAILED`, `BAND_EMPTY`, `BAND_BELOW_MIN_EXPOSURE`,
`GROUPING_NOT_EXHAUSTIVE`, `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`, `GLM_DID_NOT_CONVERGE`,
`GLM_RANK_DEFICIENT`, `GLM_SEPARATION_DETECTED`, `OFFSET_REQUIRED_FOR_FREQUENCY`,
`MONOTONE_CONSTRAINT_CONFLICT`, `EARLY_STOPPING_REQUIRES_HOLDOUT`,
`OBJECTIVE_NOT_APPROVED`, `OBJECTIVE_NOT_APPLICABLE`, `OBJECTIVE_NOT_CERTIFIED`,
`OBJECTIVE_KIND_NOT_ENABLED`, `MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT`,
`OBJECTIVE_GRAMMAR_VIOLATION`, `OBJECTIVE_NONFINITE_DERIVATIVE`,
`TRANSPARENCY_ARTIFACT_REQUIRED`, `MODEL_IMMUTABLE`, `PICKLE_PERSISTENCE_REFUSED`,
`PERIL_STRUCTURE_RECONCILIATION_FAILED`.

### 5.2 `pricing-core` interfaces

```python
# pricing_core/modelling/factors.py
def resolve_factors(df: pl.DataFrame, factors: Sequence[Factor]) -> FactorMatrix
def propose_banding(df: pl.DataFrame, spec: BandingProposalSpec) -> Banding
def propose_grouping(df: pl.DataFrame, spec: GroupingProposalSpec) -> Grouping

# pricing_core/modelling/glm.py
def fit_glm(data: pl.DataFrame, spec: GlmSpec, *, seed: int = 0,
            progress: ProgressCallback | None = None) -> GlmFitResult
def predict_glm(model: Model, data: pl.DataFrame, *,
                with_interval: bool = False) -> pl.DataFrame

# pricing_core/modelling/gbm.py
def fit_gbm(data: pl.DataFrame, spec: GbmSpec, *, seed: int = 0,
            progress: ProgressCallback | None = None) -> GbmFitResult
def predict_gbm(model: Model, data: pl.DataFrame) -> pl.DataFrame

# pricing_core/modelling/objectives.py
def parse_expression(text: str, bound: Sequence[str], params: Sequence[Parameter]) -> ExprTree
def derive_derivatives(loss: ExprTree, wrt: str = "f") -> tuple[ExprTree, ExprTree]
def compile_objective(obj: CustomObjective) -> ObjectiveFns   # .grad(y,f,w), .hess(y,f,w)
def certify_objective(obj: CustomObjective, *, sampling: SamplingSpec,
                      seed: int) -> ObjectiveCertificate

# pricing_core/modelling/diagnostics.py
def compute_diagnostics(model: Model, train: pl.DataFrame, holdout: pl.DataFrame,
                        *, weights: WeightSpec) -> Diagnostics
def compare_models(models: Sequence[Model], holdout: pl.DataFrame) -> ModelComparison

# pricing_core/modelling/transparency.py
def build_glm_approximation(model: Model, data: pl.DataFrame,
                            spec: GlmSpec) -> GlmApproximation
def build_shap_summary(model: Model, data: pl.DataFrame, *, sample: int,
                       seed: int) -> ShapSummary

# pricing_core/modelling/perils.py
def assemble_risk_premium(structure: PerilStructure, data: pl.DataFrame) -> pl.DataFrame
def reconcile(structure: PerilStructure, data: pl.DataFrame) -> Reconciliation
```

Sketch of the compiled objective handed to XGBoost — note the platform, not the user,
owns this function; the user only ever supplied `loss` (§4.6):

```python
def make_xgb_objective(fns: ObjectiveFns, base_margin: np.ndarray | None):
    def objective(preds: np.ndarray, dtrain: xgb.DMatrix):
        y = dtrain.get_label()
        w = dtrain.get_weight() if dtrain.get_weight().size else np.ones_like(y)
        f = preds                       # base_margin is already in preds (verified, research F5)
        g, h = fns.grad(y, f, w), fns.hess(y, f, w)
        if not (np.isfinite(g).all() and np.isfinite(h).all()):
            raise NonFiniteDerivative(...)                 # FR-MODEL-48
        return g, np.maximum(h, fns.hessian_min)           # FR-MODEL-43 strategy
    return objective
```

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Factor workbench | `/factors/:datasetVersionId` | Column list with profile one-ways (`01` FR-DATA-26), banding editor with draggable boundaries and live band stats, grouping editor with relativity-ordered levels and merge tolerance slider, monotonic-direction and intent controls, interaction suggestions with exposure share and holdout lift which the actuary adds as explicit Factors or ignores (FR-MODEL-79) |
| Model spec builder | `/models/new` | Dataset/split pickers, response & offset/weight, factor multi-select, model-type tabs, objective picker (builtin or approved custom), hyperparameters, live spec validation (FR-MODEL-44) |
| Model detail | `/models/:slug` | Spec summary, coefficient/relativity tables with CI bars, fit metadata, lineage strip, flags. `?version=` selects one; the latest by default |
| Diagnostics | `/models/:slug@:version/diagnostics` | Train/holdout side-by-side throughout; A/E by factor, lift & double-lift, calibration, residuals, GBM eval curves and importances, CV fold dispersion |
| Model comparison | `/models/compare?ids=` | Aligned metric table, double-lift chart, factor-by-factor relativity diff |
| Custom objective library | `/objectives` | List with status, applicability, usage count; editor with live parse errors (expression authoring is gated by `expression_objectives_enabled` and off throughout Phase 1 — FR-MODEL-75), derived gradient/hessian display, loss-curve preview at chosen parameter values |
| Objective certificate | `/objectives/:slug@:version/certificate` | Per-check pass/warn/fail, convexity heatmap over the sampled `(y, f)` domain, smoke-fit result |
| Peril structure | `/peril-structures/:slug@:version` | Per-peril model pins, large-loss treatment, reconciliation panel |

**Interaction requirement:** the banding/grouping editors must show the *consequence* of an
edit before it is saved — band stats and CI widths update live, and merging levels shows
the deviance/df trade-off (FR-MODEL-15). An actuary should never have to fit a model to
find out whether a grouping was sensible.

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | Analyst | Opens the factor workbench on a `validated` Dataset Version; reviews one-ways from the stored Profile |
| 2 | Analyst | Proposes bandings/groupings, edits them, saves as versioned artifacts (evidence captured automatically) |
| 3 | Analyst | Declares Factors with intent, monotonic direction, rationale |
| 4 | Analyst | Builds a Model Spec; `POST /model-specs/validate` catches errors before compute |
| 5 | Frontend → Backend | `POST /models` → `202` + Job (or an existing model on `spec_hash` match) |
| 6 | Worker → pricing-core | `fit_glm` / `fit_gbm`; then `compute_diagnostics` on train and holdout |
| 7 | Analyst | Reviews diagnostics; iterates from step 2 (each iteration a new Model version with `change_reason`) |
| 8 | Analyst | For a GBM: `POST /models/{id}/transparency` → GLM approximation + SHAP summary |
| 9 | Pricing Actuary | Compares candidate models (`POST /models/compare`), selects one |
| 10 | Pricing Actuary | Assembles/updates the Peril Structure; runs reconciliation |
| 11 | Pricing Actuary | `POST /models/{id}/submit` → approval request with diagnostics, transparency, and comparison attached |
| 12 | Approver | Approves (never own submission) → Model `approved`, available to `03-rating-engine.md` |

Full journey: [`wf-01-dataset-to-model.md`](../workflows/wf-01-dataset-to-model.md).
Custom objective path: [`wf-05-custom-objective-lifecycle.md`](../workflows/wf-05-custom-objective-lifecycle.md).

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What | Contract note |
|---|---|---|
| `01-data-management` | `validated` Dataset Versions; Profiles and one-way summaries; named splits; Reference Tables (for `reference_hierarchy` groupings) | One-ways are **read**, never recomputed (`01` §7.3) |
| `06-governance` | Approval workflow, RBAC, audit sink | Author ≠ approver; two approvers for non-convex objectives |
| `07-platform` | Jobs, blob storage, seeds/determinism support | Fitting and certification are Jobs |

### 7.2 Provides

| To | What |
|---|---|
| `03-rating-engine` | `approved` Models, Peril Structures, transparency artifacts, GLM relativity tables (the natural seed for a rate table) |
| `04-optimisation` | Demand Models (`conversion`, `retention` responses) and elasticity derived from them |
| `05-monitoring` | Expected values for A/E monitoring, factor distributions at fit time as the drift baseline, and the diagnostic shapes reused for live reporting |
| `06-governance` | Diagnostics, transparency, lineage, and grouping rationale for generated model documentation |

### 7.3 Contract notes

- `03` never re-implements model scoring; it calls `pricing-core` `predict_*` or the
  GLM approximation's relativity table, so a quoted premium and a diagnostic prediction
  cannot diverge.
- `05` reuses `compute_diagnostics`' A/E computation on live data so that "A/E at fit
  time" and "A/E in production" are the same statistic.

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **glum** | All GLM fitting (FR-MODEL-18..24) | `GeneralizedLinearRegressor`; `std_errors()` and `covariance_matrix()` (non-robust, robust HC-1, clustered) and the coefficient table with CIs and p-values satisfy FR-MODEL-21 directly — verified to exist, not assumed; Tweedie/Poisson/Gamma, native offset handling, elastic-net CV paths |
| **statsmodels** | Fallback/cross-check diagnostics (FR-MODEL-51) | Type-III deviance tests, residual diagnostics, coefficient cross-validation against glum |
| **XGBoost** | Primary GBM (FR-MODEL-25..32) | Custom objective `(grad, hess)` signature, `base_margin`, `monotone_constraints`, `interaction_constraints`, JSON model IO, `QuantileDMatrix` for memory |
| **LightGBM** | Secondary GBM | `fobj`/`feval`, `init_score` as the offset, monotone constraint methods (`basic`/`intermediate`/`advanced`), native categoricals |
| **interpret (EBM)** | Transparent ML (FR-MODEL-37) | Exporting term shape functions as tables; treating an EBM as a set of additive lookups |
| **SHAP** | Transparency artifacts (FR-MODEL-35) | TreeSHAP on boosted trees, interaction values (which feed FR-MODEL-79's suggestions and never a Factor), exposure-weighted dependence summaries, sampling cost |
| **SymPy** | Symbolic gradient/hessian derivation (FR-MODEL-40) — **Phase 2**, with `expression` objectives (FR-MODEL-75) | Differentiation of `Piecewise` (from `where`), simplification, lambdify-free code generation into our own expression tree |
| **NumPy** | Compiled objective evaluation | Vectorised, allocation-conscious gradient/hessian evaluation; `np.errstate` discipline for log/exp edges |
| **Python `ast`** | Restricted grammar parsing (§4.6) | Allow-list node walking, depth/size limits, why `eval`/`compile` on user input is never acceptable |
| **Polars** | Factor resolution, banding/grouping application, diagnostic aggregation | Expression API for banding (`cut`), joins for grouping maps |
| **SciPy** | CIs, profile likelihood for Tweedie `p`, numeric derivative checks in certification, credibility standards for `credibility_weighted` groupings (FR-MODEL-80) | `scipy.optimize` for the profile grid, `scipy.stats` for CIs |
| **ECharts (frontend)** | Relativity plots with CI bands, lift/gains, calibration, PD plots, convexity heatmap | Large-series performance; dual-axis A/E charts |
| **TanStack Table (frontend)** | Coefficient, relativity, banding, and grouping grids | Inline editing for boundaries and level merges |

New skills this spec adds to `skills-map.md`: SymPy differentiation of piecewise
expressions; XGBoost/LightGBM custom objective and `base_margin`/`init_score` mechanics;
TreeSHAP cost and interpretation; restricted-AST parser construction; credibility theory
for grouping.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-MODEL-1** | GLM: 5 M rows × 60 factors converges in < 10 min on a 16-core worker (NFR-OVR-3). |
| **NFR-MODEL-2** | GBM: 5 M rows × 60 factors × 500 trees fits in < 20 min; a custom `expression` objective adds no more than 25 % overhead versus the equivalent builtin. |
| **NFR-MODEL-3** | Banding/grouping proposals return in < 5 s for a column with ≤ 10 000 distinct levels, computed from the stored Profile where possible. |
| **NFR-MODEL-4** | Diagnostics computation adds no more than 30 % to fit wall-clock. |
| **NFR-MODEL-5** | Objective certification completes in < 3 min including the synthetic smoke fit. |
| **NFR-MODEL-6** | Determinism: identical `spec_hash` + seed reproduces identical coefficients to 1e-10 (GLM) and an identical booster hash (GBM), on the same library versions (FR-OVR-8). |
| **NFR-MODEL-7** | A stored Model round-trips: export → import into a clean instance → predictions identical to the last representable digit (FR-OVR-2). |
| **NFR-MODEL-8** | Security: user-supplied expressions never reach `eval`/`exec`; the parser rejects out-of-grammar input with a position-accurate error; compiled objectives cannot allocate unbounded memory or exceed their per-round time budget (FR-MODEL-48). |
| **NFR-MODEL-9** | Audit: factor/banding/grouping creation and edit, fit start and completion, objective derivation/certification/approval, and every status transition emit Audit Events with before/after state. |
| **NFR-MODEL-10** | Memory: fitting a 5 M × 60 dataset stays within 32 GB, using `QuantileDMatrix`/streaming construction rather than duplicating the design matrix. |
| **NFR-MODEL-11** | Diagnostics artifacts stay under 50 MB per model; larger evidence (SHAP dependence, residual scatter) goes to content-addressed blobs referenced from the artifact. |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-MODEL-1** | ~~Should `expression` custom objectives ship in Phase 1 at all, or only the `template` catalogue (§4.5)?~~ **DECIDED 2026-08-15: templates in Phase 1, expressions in Phase 2 — and the certification machinery is built in Phase 1 regardless.** Specified as FR-MODEL-75 and FR-MODEL-76. The restricted parser is not the deferred part and never was: it already exists for `01` FR-DATA-10. What Phase 2 adds is symbolic derivation, a second compilation target, and the review path for a loss a user wrote. |
| **OQ-MODEL-2** | ~~GBM prediction intervals: paired quantile models, "uncertainty unavailable", or a variance-model approximation?~~ **DECIDED 2026-08-15: `uncertainty: unavailable` with a typed reason by default, opt-in paired quantile models, and the variance approximation is never shipped.** Specified as FR-MODEL-77 and FR-MODEL-78. |
| **OQ-MODEL-3** | Is the GLM approximation of a GBM a *transparency artifact* only, or should it be directly rateable — i.e. can a Rating Version rate on the approximation instead of calling the GBM, trading fidelity for a fully tabular rating structure? |
| **OQ-MODEL-4** | ~~Interactions as explicit Factors only, or also automatically-detected candidates from SHAP interaction values?~~ **DECIDED 2026-08-15: detected candidates are surfaced as suggestions with their exposure share and holdout lift; only an explicit Factor with a rationale can enter a Model Spec.** Specified as FR-MODEL-79. |
| **OQ-MODEL-5** | ~~Which credibility standard for `credibility_weighted` grouping — limited fluctuation or Bühlmann–Straub?~~ **DECIDED 2026-08-15: both, limited fluctuation as the default, recorded per grouping.** Specified as FR-MODEL-80, with `credibility_model`, its `(p, k)` pair and Bühlmann–Straub's variance components persisted in §4.3. |
| **OQ-MODEL-6** | ~~Hard gate on factor count / exposure-per-parameter, or a diagnostic warning?~~ **DECIDED 2026-08-15: a diagnostic always, and a gate only where a workspace configures one — unset by default.** Specified as FR-MODEL-81; the judgement belongs to the Approver (`06`), not to a constant chosen here. |
| **OQ-MODEL-7** | ~~How are protected-characteristic proxies detected, and what happens when detection fires?~~ **DECIDED 2026-08-15: the `prohibited` flag is the whole of Phases 1–2; a Phase 3 proxy assessment produces evidence for the approval request and never a block.** Specified as FR-MODEL-82; delivery is a Phase 3 deliverable, so the decision is made and the work is not now. |
| **OQ-MODEL-8** | Does the GLM spine grow to meet §4's field sets, or does §4 narrow to a staged contract? §4.1, §4.4 and §4.8 declare fields the spine does not implement, and §4.8's `status ≥ fitted ⟹ diagnostics_id set` cannot be met while diagnostics do not exist. Found by auditing the spine, 2026-08-15. |
