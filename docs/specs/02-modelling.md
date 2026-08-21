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
| **FR-MODEL-91** | **An `interaction` Factor crosses two or more other Factors, named by id in `operand_factor_ids`, and resolves to the combined levels of their resolved values.** Added 2026-08-18 (W5, the interaction slice): FR-MODEL-1 has listed the type since Phase 0 and §4.1 carried no field to express one, so the type was selectable and unresolvable — FR-MODEL-88's position for five arms, now four. **Operands are Factors rather than columns** because every other place the specification names an interaction names factors (§4.4's `interaction_constraints`, §4.9's `top_interactions`), and because an operand is usually itself a banding or a grouping: crossing raw `driver_age` with raw `region` gives one cell per policy, while crossing `driver_age_banded` with `vehicle_group_rated` gives a table an actuary can rate on. Three consequences the implementation forced, each a defect if left implicit: **(i)** only *observed* combinations become levels, because a cell with no exposure would carry a coefficient fitted on nothing and on any real cross most cells are empty; **(ii)** an operand contributes **no design column of its own** — a full cross spans every cell, so its operands' main effects are collinear with it and a design carrying both is rank-deficient; **(iii)** FR-MODEL-51's Type III test therefore compares the interaction against the **main-effects** model rather than against no term at all, which is the question an actuary means by "does this interaction earn its place". A **continuous** operand is refused by name (OQ-MODEL-12), and FR-MODEL-5's prohibition reaches through the cross: a prohibited Factor that could enter a spec crossed with something else would not be prohibited. |
| **FR-MODEL-97** | **Every operand of an `interaction` Factor must resolve to levels: a continuous operand is refused by name, and no product term is offered at any intent.** (OQ-MODEL-12, decided 2026-08-18, ratifying what the interaction slice built.) The refusal names the operand and the remedy — band or group it, then cross the result — so the actuary is left with a rateable structure by construction. A product term is legitimate GLM practice and is refused anyway, because `03`'s rating DAG is a graph of *tables* and a varying slope has no cell: allowing one moves the failure from the factor, where it is a message, to the rating slice, where it is a model somebody has already fitted. **The narrower third option — a product term for `diagnostic`-intent factors only (FR-MODEL-3), never rated on — is the likely eventual answer and is deliberately not taken now**: it needs no contract change, only a widened refusal, and it should be decided against a rate table that exists rather than one that is specified. Revisit when `03`'s rate-table shape is built; owner the maintainer. Refusing is additive to undo and impossible to undo the other way round, which is the whole of why the order is this one. |
| **FR-MODEL-92** | **A backtest is readable.** `GET /api/v1/models/backtests/{id}` returns the stored artifact, or a 404 naming it. Added 2026-08-18 (W5, the backtest slice): §5.1 declared the `POST` and no read, which is a 202 whose artifact nothing can fetch — complete to the endpoint audit, since that compares the spec against the contract and an endpoint missing from both is in neither, and unusable to every caller. **The fourth time**: FR-MODEL-84 repaired it for the transparency artifact, FR-MODEL-56 for the comparison, FR-MODEL-90 for the peril structure. By backtest id rather than by model, because unlike `Diagnostics` a model has many — one per period it has been measured against — and the Job's result names the one just produced (`backtest:{id}`). A **list** by model is what `05-monitoring.md` will read and is deliberately not built here: nothing consumes it yet, and `CLAUDE.md` §0 puts a later phase's capability in the spec rather than the code. |
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
| **FR-MODEL-83** | A Banding or Grouping can be **evaluated against a Dataset Version without being persisted**: the platform recomputes FR-MODEL-10's per-band statistics, or FR-MODEL-15's deviance/df evidence, for boundaries or a mapping the actuary has edited by hand. Added 2026-08-15 (W5), and numbered 83 rather than 75 because OQ-MODEL-1..7's decisions took 75..82 while this was in review — ids are permanent, so the later claimant moves (`CLAUDE.md` §5). §5.3's interaction requirement — that an edit's consequence is visible *before* it is saved — is otherwise unmeetable, because `/propose` derives a mapping from a *method* and has no way to accept one. Without it "the proposal is always editable" (FR-MODEL-9, FR-MODEL-14) means editable but unmeasurable, which is the state that makes an actuary fit a model to find out whether a grouping was sensible. |

| **FR-MODEL-85** | **`tree` banding (FR-MODEL-9) and `tree` grouping (FR-MODEL-14) fit a single depth-limited CART regression tree, and are named for the instrument they use** (OQ-MODEL-9, decided 2026-08-17). Both fit `sklearn.tree.DecisionTreeRegressor` with `max_leaf_nodes` set from `n_bands` / `n_groups`, on the observed response — claim frequency for a banding, the Level's own rate for a grouping — weighted by exposure, so a cut is trusted in proportion to the exposure behind it. `scikit-learn` is declared in `pricing-core`'s dependencies rather than relied on transitively through `glum` (§8). Each artifact records the **effective** `min_samples_leaf` and `random_state` in `method_params`, not only what the caller named, because an artifact that cannot reproduce its own fit is not evidence. A one-tree booster on the XGBoost this package already depends on was rejected: it selects splits under `lambda`, `min_child_weight` and `gamma` rather than as CART does, so its cut points are not the ones the method is named for — the same objection, in subtler form, that refused returning quantile boundaries under the label `tree`. A `tree` banding refuses a Dataset Version with no claim-count column (nothing to split on) or no exposure column (an unweighted tree is a different method); a `tree` grouping refuses a column no Level of which carries exposure. |

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

> **The `inverse` link was declared here, accepted by `GlmSpec`, implemented in the scorer,
> and could not be fitted — corrected 2026-08-18 (W5, the prediction slice).** `spec.link`
> reached `glum` as the string `"inverse"`, which is not in that library's link vocabulary
> (`identity`, `log`, `logit`, `cloglog`, `tweedie`), so every attempt died on a bare
> `ValueError` raised from inside `_glm.py` — not a named `GlmFitError`, and nothing
> FR-MODEL-23 would recognise as a surfaced failure. **The spec was right and the code was
> wrong**, which is worth stating because the cheap repair was to delete `inverse` from
> this row: it is the canonical Gamma link, and the platform could already *score* a model
> on it. `glum`'s `TweedieLink(p)` is `mu**(1-p)`, so `TweedieLink(2)` **is** `1/mu`, and
> the gap was one line of translation. `power(k)` remains declared and unbuilt — `GlmSpec`
> has no spelling for it and no slice has needed one — and is named here under
> FR-MODEL-87's staging rule rather than quietly dropped.
| **FR-MODEL-19** | Actuarial defaults are applied unless explicitly overridden, and any override is recorded with a justification: **frequency** → Poisson, log link, `offset = log(exposure)`; **severity** → Gamma, log link, `weight = claim_count`; **burning cost** → Tweedie with `1 < p < 2`, log link, `weight = exposure`; **conversion/retention** → binomial, logit link. |
| **FR-MODEL-20** | Regularisation (L1, L2, elastic net) is supported with a documented path and a cross-validated selection option. The selected penalty and the full CV path are persisted as diagnostics. |
| **FR-MODEL-21** | Fitting returns, for every coefficient: estimate, standard error, z/t statistic, p-value, and confidence interval; and for every categorical Factor: the relativity table with the base level marked. These are persisted in the Model artifact (ADR-0003) and are re-scorable without `glum`. |
| **FR-MODEL-22** | The Tweedie power `p` may be estimated by profile likelihood over a grid, with the profile curve persisted. Estimated `p` is recorded as an estimate with its own uncertainty, not silently baked in as a constant. |

> **Amendment 2026-08-21 (FR-MODEL-22 slice):** "Profile likelihood" means the profile
> log-likelihood `L(p) = Σᵢ log f(yᵢ; μ̂ᵢ(p), φ̂(p), p)`, and the estimate is the argmax of
> `L` over `tweedie.p_grid`. `μ̂(p)` is the GLM fit at power `p`; `φ̂(p) = D(p)/n` is the
> mean-deviance dispersion estimate (Dunn & Smyth's saddlepoint route); `f` is the
> Tweedie series density (Dunn & Smyth 2005): `f(0) = exp(−μ^(2−p)/((2−p)φ))` and, for
> `y > 0`, `f = (1/y)·exp(−y/τ − λ)·Σⱼ exp(r·j)/(Γ(1+j)·Γ(−αj))` with `α = (2−p)/(1−p)`,
> `r = −α·log y + α·log(p−1) − (1−α)·log φ − log(2−p)`, `τ = φ(p−1)μ^(p−1)`,
> `λ = μ^(2−p)/((2−p)φ)`. "Its own uncertainty" is the 95% profile-likelihood interval
> `{p : 2(L_max − L(p)) ≤ χ²₀.95(1) = 3.841}`, linearly interpolated between scanned
> points and persisted as `ci_lower`/`ci_upper`; the profile curve (power,
> log-likelihood) is persisted on `fit_result.tweedie`. A maximum at a scan edge is
> refused with `GLM_TWEEDIE_POWER_GRID_EDGE`; estimation and `select_by="cv"` are refused
> together (the profile is penalty-dependent); `family_params.power` beside the grid is
> refused. *(2026-08-21 correction: the planning-time deviance-argmin design is replaced.
> The deviance profile `D(p) = 2φ(ℓ_sat(p) − ℓ(p, μ̂))` is not a likelihood profile for
> Tweedie — `ℓ_sat(p)` and the p-dependent normaliser do not cancel out of the argmin —
> and the deviance-argmin estimator was measured biased (argmin ≈ truth + 0.25, grid-edge
> at every pinned seed) during the slice.)*
| **FR-MODEL-23** | Non-convergence, separation, rank deficiency, and aliased columns are surfaced as explicit, named fit errors with the offending factors identified — never as a silently returned degenerate fit. |
| **FR-MODEL-24** | An **offset from another model** is supported (`offset_model_ref`), enabling residual modelling and "fit on top of the current rating structure" workflows. The referenced model version is pinned. **Amended 2026-08-21 (W5 slice 4).** The ref is the canonical `model:slug@version` string (ID-3). v1 builds the offset for GLM specs only: the referenced model must be a fitted GLM, and the offset is its linear predictor (η, including its own offset) on the training data — the two links must be equal, refused by name otherwise (`MODEL_OFFSET_REF_INVALID`). Refused by name, not built: a `GbmSpec` whose offset is `kind: "model"`; a ref naming a GBM or EBM model; the peril-reconciliation scoring path (it fails named, `MODEL_OFFSET_MISSING`, until W5 wires the resolver there). The fit records what was constructed: `GlmFitResult.offset_model_ref` carries the resolved pinned ref. Diagnostic weighting for a model-offset fit follows `spec.weight` (COUNT default) — the exposure-weighting convention is never inferred from the offset. The Phase-0 scaffold's `model_ref: str` is renamed `offset_model_ref` with the artifact-ref pattern: the spec and the hand-authored contract have always named and typed it that way, and the scaffold field was read by nothing. |

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
| **FR-MODEL-94** | **The fit artifact records *who applies the inverse link*, and scoring reads it rather than assuming one.** Added 2026-08-18 (W5, custom objectives), and the second half of FR-MODEL-72's asymmetry — the requirement above states the offset half and is silent on this one. Three cases, all reachable: XGBoost under a builtin objective transforms in `predict`; XGBoost under a **custom** objective was handed gradients and no link, so `predict` returns the raw margin; LightGBM is always asked for the raw score, because FR-MODEL-72's offset has to be added before the transform. `GbmFitResult.inverse_link` therefore names the transform *the platform* must apply, or `None` where the library already has — not the model's link, which is the same value in all three cases and so cannot distinguish them. |
| **FR-MODEL-32** | Categorical handling is explicit: either the Factor supplies a grouping/encoding, or the backend's native categorical support is used with its parameters recorded. Silent label-encoding of an unordered categorical is refused. |

### 3.6 Transparency (non-GLM models)

| ID | Requirement |
|---|---|
| **FR-MODEL-33** | Every non-GLM Model must carry at least one **Transparency Artifact** before it can be referenced by a Rating Version (R3). Two forms are supported and both may be present. |
| **FR-MODEL-34** | **GLM approximation** — a GLM fitted to the GBM's own predictions over the modelling population, with the same factor set (optionally banded), reporting R² / deviance explained against the GBM, and the residual pattern where the approximation is worst. This is the artifact that turns a GBM into something rateable as a table. |
| **FR-MODEL-35** | **SHAP factor summary** — TreeSHAP mean absolute contribution per factor, per-factor dependence summaries (contribution vs factor value, exposure-weighted), and the top interaction pairs. Computed on a reproducible sample with a persisted seed and sample size. |
| **FR-MODEL-79** | **Interaction candidates found in TreeSHAP interaction values are suggestions, never additions** (OQ-MODEL-4, decided 2026-08-15). The transparency artifact ranks the top pairs (FR-MODEL-35) and the factor workbench surfaces each with its exposure share and its holdout lift, so an actuary sees what a suggestion is worth and over how much of the book. The platform never writes a Factor into a Model Spec: an interaction becomes rateable only as an explicit `interaction` Factor (FR-MODEL-1) carrying an intent and a written rationale (FR-MODEL-3), and the generated model document names it as an authored decision. Auto-detected structure entering a rating basis unreviewed is precisely the overfitting route this refuses. |
| **FR-MODEL-36** | The transparency artifact records an explicit **fidelity statement**: how well the approximation reproduces the model, where it does not, and the exposure share of the region where it does not. A Rating Version referencing the model surfaces this at approval time. |
| **FR-MODEL-96** | **The GLM approximation of a GBM is persisted as a Model in its own right; the transparency artifact references it by `approximating_model_id` and stops carrying its coefficients inline.** (OQ-MODEL-10, decided 2026-08-18; **owner Phase 1b, and before anything references a transparency artifact by identifier**.) The argument is `03` FR-RATE-60's: an `approximation`-mode Rating Version pins what it rates on, FR-OVR-14 requires every pin to resolve to an artifact whose status is `approved` or better, and a `TransparencyArtifact` carries `model_id` and **no status at all** — so the thing that is rated on must be an artifact that has one, and only a Model does. Three obligations follow, and they are the work the answer creates rather than reasons against it: (i) the approximating Model's spec records `approximates_model_id`, and its `dataset_version_id` is the population the approximation was fitted over, so a reader can tell a surrogate from a model fitted on observed claims; (ii) that field joins the `spec_hash` payload and increments `n` with it (FR-MODEL-86); (iii) §4.8's `status ≥ fitted ⟹ diagnostics_id` is met by diagnostics **of the surrogate against the source model's predictions** — the quantity FR-MODEL-36 already measures — recorded as such, never presented as diagnostics against observed claims. Until it is built, `approximating_model_id` stays `None` and the artifact carries the coefficients: declared-and-unbuilt in FR-MODEL-87's sense, with this requirement as the trigger. *(Amended 2026-08-19, W5, building FR-MODEL-96.* **Built.** The trailing sentence above and the **owner Phase 1b** parenthetical describe the state before this date and no longer describe the platform. The three obligations are discharged: (i) `approximates_model_id` lives on `GlmSpec`, and FR-MODEL-102 makes a surrogate identifiable from its spec alone; (ii) the field joins the `spec_hash` payload, which moves `v4` to `v5` with it (FR-MODEL-86); (iii) §4.8's `status ≥ fitted ⟹ diagnostics_id` is met by the surrogate's diagnostics against the source model's predictions. The artifact's inline `coefficients` and `relativities` survive as a legacy era for artifacts written before this date, exclusive at the type with `approximating_model_id`, rather than as the current state.)* |
| **FR-MODEL-84** | **A transparency artifact is readable.** `GET /api/v1/models/{id}/transparency` returns the model's most recent artifact, or a 404 naming the model. Added 2026-08-17 (W5, the transparency slice): §5.1 declared the `POST` and no read, which is a 202 whose artifact nothing can fetch — complete to the endpoint audit, since that compares the spec against the contract and an endpoint missing from both is invisible to it, and unusable to every caller. The same omission `01`'s reference publish lifecycle made, and the one the comparison artifact carried until FR-MODEL-56 was built. A model may hold several artifacts (FR-MODEL-33 allows both forms, and a re-sampled SHAP summary is a second artifact rather than a correction); the route returns the latest, and an approval citing a specific one resolves it by id. |
| **FR-MODEL-37** | EBM (`interpret`) models are treated as transparent by construction: their term shape functions are exported directly as tables and require no approximation, but they still carry the fidelity/diagnostic sections in the same contract shape. |
| **FR-MODEL-102** | **A surrogate is identifiable from its spec alone.** Added 2026-08-19 (W5, building FR-MODEL-96). `GlmSpec.approximates_model_id` is set **if and only if** `response_column` is the reserved surrogate column `__gbm_prediction__`, refused at the type in both directions. A spec that named a source model while pointing at an observed response column would describe a model fitted on claims and read as a surrogate; one that fitted the reserved column while naming no source would be a model of a prediction nobody can identify. This is also what makes FR-MODEL-96(iii) enforceable without a second field: the A/E in the surrogate's `Diagnostics` is against the source model's predictions because the spec the diagnostics were computed under says so, and `CLAUDE.md` §2's rule against a fact stated twice keeps it there rather than copied onto the diagnostics document. Two consequences are stated rather than left to be discovered: a surrogate Model **carries no `covariance_blob`**, so FR-MODEL-93's typed absence is what a prediction against it reports — an interval computed from a surrogate's coefficients describes the surrogate and would be read as the GBM's uncertainty; and a surrogate **appears in `GET /api/v1/models`** like any other Model, which is the point of FR-MODEL-96 rather than a side effect. **The name it appears under is fixed too, added 2026-08-19 (fix round, W5):** the surrogate's `model_family_slug` is the source model's own family slug with `-approx` appended, and `models.model_family_slug` is a `String(64)` column — a source slug that leaves no room for that suffix within the 64-character limit is refused by name, naming the slug and the length it would have produced, before the transparency Job spends any compute fitting it. |

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
| **FR-MODEL-103** | A **Custom Metric** is its own versioned artifact (`custom_metric:<slug>@<version>`), declared separately from objectives so one metric can be evaluated across many. In Phase 1 it is templates-only, on OQ-MODEL-1's rule: a metric names an `ObjectiveTemplate` and its parameters, and its value is that template's loss evaluated as an exposure-weighted mean. It carries no `hessian_strategy` and no `hessian_min` — a metric is never differentiated, and a field that is structurally meaningless is worse than an absent one. |
| **FR-MODEL-104** | A Custom Metric declares its `direction` — `lower_is_better` or `higher_is_better` — and early stopping reads it rather than inferring one. A metric whose direction is guessed stops the fit at the wrong round in exactly half of cases, and produces a fitted model rather than an error. |
| **FR-MODEL-105** | A Custom Metric carries a `MetricCertificate` before submission, on FR-MODEL-42's argument: a metric that early-stops a fit decides when boosting halts and therefore changes the model. Its checks are `finiteness`, `direction_holds`, `scale_behaviour` and `smoke_evaluation`. §4.7's derivative and convexity checks are **absent, not `not_applicable`** — a metric has no gradient or hessian to compare, so the question is not askable rather than unanswered. The check vocabulary (`CheckStatus`, `SamplingSpec`, `CertificateOutcome`, and `CertificateResult.outcome_of`'s derivation of `overall`) is shared with §4.7 unchanged. |
| **FR-MODEL-106** | `GbmSpec.eval_metrics` is **honoured**: `kind: builtin` names are passed to the backend's own metric vocabulary, and `kind: custom` refs are resolved by the backend and handed to `pricing-core` as artifacts (ADR-0001). A ref that does not resolve, names a metric whose applicability excludes the spec's response or backend, or names one whose status is outside `FITTABLE_METRIC_STATUSES`, refuses the fit before any boosting round. *(Recorded 2026-08-19: the field was declared from Phase 0 and read by nothing — a spec accepted, silently ignored, and reported to the caller as configured.)* *(Amended 2026-08-20: honouring the field put a second metric beside the stopping one for the first time, and LightGBM's `first_metric_only=False` then halted the fit as soon as **any** of them stalled — a stricter rule than the spec states, reached by omission. What early stopping binds to is FR-MODEL-107's.)* |
| **FR-MODEL-107** | Early stopping on a **Custom Metric** is supported under a custom objective. `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` narrows to its true scope: a **builtin** metric under a callable objective, where both backends hand the metric the raw score rather than the transformed prediction, so the metric it stops on is not the metric it names. *(Amended 2026-08-20: early stopping binds **explicitly** to the metric the spec names, on both backends and whether that metric is builtin or custom — XGBoost through `EarlyStopping(metric_name=, data_name=)`, LightGBM by ordering the stopping metric first and narrowing to `first_metric_only`. Both libraries' shorthands choose positionally, so a spec naming a builtin stopped on a declared Custom Metric under XGBoost and on whichever metric stalled first under LightGBM: one spec, two backends, two answers. One consequence is pinned rather than hidden — LightGBM evaluates builtin metrics before `feval`'s, so a spec that stops on a Custom Metric **and** declares a builtin for the curve does not get the builtin reported, because reporting it would put it at position 0 and drive the stop.)* |
| **FR-MODEL-108** | A Custom Metric is readable and governable over the API: create, read, certify, read the certificate, submit for approval, and list usage — FR-MODEL-95's argument applied to metrics, since an approver who cannot fetch the certificate is being asked to approve a verdict they cannot see. |
| **FR-MODEL-46** | Custom Objective lifecycle is `draft → certified → review → approved → deprecated`. Approval is by an Approver who is not the author; `expression` objectives with `convexity: violated` need two Approvers (FR-MODEL-43). Editing an `approved` objective creates a new version requiring fresh certification and approval. |
| **FR-MODEL-47** | Objective usage is fully traceable: for any objective version, the platform lists every Model, Rating Version, and live Deployment using it — the blast-radius query needed when a defect is found. |
| **FR-MODEL-48** | Objective execution is resource-bounded: compiled expressions are evaluated on fixed-size NumPy arrays with no allocation of unbounded intermediates, wall-clock is budgeted per boosting round, and NaN/inf appearing in a gradient or hessian aborts the fit with a named error identifying the round and the offending input range. |
| **FR-MODEL-95** | **A Custom Objective and its certificate are readable.** `GET /api/v1/custom-objectives/{id}` returns the objective with its status, its certificate outcome and its `approval_request_id`; `GET /api/v1/custom-objectives/{id}/certificate` returns the latest `ObjectiveCertificate` for that version, or a 404 naming it. Added 2026-08-18 (W5), because §5.1 declared five write endpoints and no way to read what they wrote: FR-MODEL-42 makes a certificate the condition of submission and FR-MODEL-46 puts an Approver in front of it, and an approver who cannot fetch the certificate is being asked to approve a verdict they cannot see. Certification is a **202** job (FR-MODEL-42), so a caller that cannot read the result back has no completion signal either. |

### 3.8 Diagnostics

| ID | Requirement |
|---|---|
| **FR-MODEL-49** | Every fit produces a persisted **Diagnostics** artifact. Diagnostics are computed once at fit time and read thereafter; the UI never recomputes them. |
| **FR-MODEL-50** | Universal diagnostics (all model types): actual-vs-expected by factor level and by banded continuous factor (exposure-weighted, with CIs); lift/gains curves by predicted decile; Gini / normalised Gini; calibration by predicted decile; residual summaries; overall A/E ratio on train and holdout. *(Amended 2026-08-17, W5. **Double lift is removed from this list** and lives on the comparison artifact, FR-MODEL-56 and §4.11. It was listed here and `PartitionDiagnostics.double_lift` was populated by nothing — nothing could populate it: double lift is pairwise, the comparison model is unknown at fit time, and FR-MODEL-49 makes diagnostics computed once at fit time and read thereafter, so it could not be filled later either. A field that is structurally always null is worse than an absent one, because a reader takes it for a measurement that came out empty.)* |
| **FR-MODEL-51** | GLM-specific diagnostics: deviance, null deviance, AIC/BIC, dispersion estimate, degrees of freedom, per-factor type-III deviance test with p-value, relativity plots with confidence bands, standardised deviance and Pearson residual plots, leverage/Cook's distance on a sample, and a VIF/aliasing report. |
| **FR-MODEL-52** | GBM-specific diagnostics: evaluation curve per iteration for train and holdout, gain/cover/frequency importance, permutation importance on the holdout, partial dependence for declared factors, monotonicity verification (that the fitted response actually respects declared constraints), and tree-count/depth summary. |
| **FR-MODEL-53** | Cross-validation is supported with declared fold construction (`random`, `temporal`, `grouped_by_key`) and a persisted seed; per-fold metrics and their dispersion are persisted, not just the mean. |
| **FR-MODEL-54** | Diagnostics are computed on **train and holdout separately and always reported side by side**. A diagnostic reported without its holdout counterpart is a defect. |
| **FR-MODEL-55** | Metrics are recorded with their weighting scheme explicit (exposure-weighted vs unweighted vs claim-count-weighted). An unweighted metric on an exposure-weighted problem is labelled as such in the UI. |
| **FR-MODEL-81** | **Model complexity is a diagnostic by default, and a gate only where a workspace asks for one** (OQ-MODEL-6, decided 2026-08-15). Every fit records its factor count, its fitted-parameter count, and its exposure-per-parameter and claims-per-parameter ratios in the diagnostics, beside whatever thresholds are in force. The workspace settings `modelling.max_factor_count` and `modelling.min_exposure_per_parameter` (`07` FR-PLAT-45) are **unset by default**; where a workspace sets one, `POST /model-specs/validate` and `POST /models` refuse a breaching spec with `MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT` before any compute is spent, and the refusal is audited. There is no platform-wide constant: a large book legitimately supports a large model, and whether *this* model is overfitted is a judgement for the Approver with the diagnostic in front of them (`06`), not for a number chosen here. |
| **FR-MODEL-56** | Model comparison is a first-class operation: two or more Models fitted on the same holdout can be compared on aligned metrics, double-lift, and factor-by-factor relativity differences, producing a persisted comparison artifact citable in an approval request. |
| **FR-MODEL-57** | A **backtest** on a later Dataset Version is supported and produces the same diagnostic shapes, marked with the version it ran against. Backtests are the evidence bridge into `05-monitoring.md`. *(Amended 2026-08-18, W5, the backtest slice, with what building it settled.* **A backtest is its own artifact — §4.12 — and `Diagnostics.backtest` is removed.** That field was declared from Phase 0 and typed `null`, and nothing could ever have filled it: FR-MODEL-49 computes diagnostics once at fit time, while a backtest runs later and again for every period after that. It is the same defect FR-MODEL-50's `double_lift` had, found the same way. **"The same diagnostic shapes" means one `PartitionDiagnostics`, not a `UniversalDiagnostics`:** the backtested population was never split, so FR-MODEL-54's both-partitions rule does not apply and calling the single partition a holdout would claim a split nobody made. **"Other than the one it was fitted on" reaches the split parts**, which are Dataset Versions in their own right (`01` FR-DATA-36) — the refusal the type cannot see and the platform must, and it runs *before* the validated gate for the reason §4.12 gives. Both model types are backtested through one path; FR-MODEL-57 says nothing about model type, and a backtest that worked only for GLMs would leave the GBM an actuary trusts least as the one nothing re-measures.)* |

> **Amendment, 2026-08-21 (the regularisation-and-CV slice).** Neither this requirement
> nor `01` FR-DATA-33 defined K-fold `temporal` semantics — FR-DATA-33 only defines a
> two-part cutoff split. Resolved as **contiguous time-ordered blocks**: sort ascending by
> `time_column`, cut the sorted row order into `folds` equal-count blocks. Implemented in
> `pricing_core.data.splits.assign_folds`.

### 3.9 Peril structure and risk premium

| ID | Requirement |
|---|---|
| **FR-MODEL-58** | A **Peril Structure** declaratively composes Models into a Risk Premium: per peril, either `frequency × severity` or `burning_cost`, summed over perils, with per-peril model references pinned by version. |
| **FR-MODEL-59** | The structure declares how large losses are handled per peril: `none`, `capped` (with the cap and the loading applied to restore the mean), `separate_model` (an excess-layer model), or `flat_loading`. Whatever is chosen is recorded with its calibration evidence. |
| **FR-MODEL-60** | The structure is validated for coherence: every peril present in the dataset is either modelled or explicitly excluded with a reason; total modelled burning cost reconciles to observed burning cost within a declared tolerance on the holdout, and the reconciliation is persisted. |
| **FR-MODEL-61** | A Peril Structure is an approvable artifact in its own right and is what `03-rating-engine.md` references — a Rating Version references a Peril Structure, not a scatter of individual models. |
| **FR-MODEL-90** | **A Peril Structure is readable and submittable.** `GET /api/v1/peril-structures/{id}` returns the structure with its reconciliation, or a 404 naming it; `POST /api/v1/peril-structures/{id}/submit` moves `reconciled → review` and creates the approval request FR-MODEL-61 makes it eligible for. Added 2026-08-18 (W5, the peril-structure slice): §5.1 declared a create and a reconcile and neither of these, which is a `POST` whose artifact nothing can fetch and an approvable artifact with no way to submit it. The same omission FR-MODEL-84 repaired for the transparency artifact and FR-MODEL-56 for the comparison — and invisible to the endpoint audit for the same reason each time, since it compares the spec against the contract and an endpoint missing from both is in neither. FR-MODEL-61 additionally needed a `peril_structure` entry in `06` §4.2's `DEFAULT_POLICY`: the approval machine is fully generic and `peril_structure` has been a valid artifact type since Phase 0, but with no policy entry a submission is refused with "no approval policy for this artifact type" — a correct refusal of an artifact nobody could ever approve. Its evidence kind is `reconciliation`, which is what FR-MODEL-60 makes it. |

### 3.10 Prediction and lifecycle

| ID | Requirement |
|---|---|
| **FR-MODEL-62** | `pricing-core` can score any persisted Model from its declarative artifact alone (ADR-0003), with no dependency on the fitting session. GLM scoring requires no `glum`; GBM scoring loads the JSON booster. |
| **FR-MODEL-63** | Prediction returns the expectation plus an uncertainty measure: GLM prediction intervals from the covariance matrix; GBM either quantile-model-based intervals or an explicit `uncertainty: unavailable` with the reason (R5). |
| **FR-MODEL-93** | **A GLM fitted before the covariance matrix was stored reports `uncertainty: unavailable` with reason `covariance_not_stored`, and still returns the expectation.** Added 2026-08-18 (W5, the prediction slice). FR-MODEL-63's interval needs `V`, which is `p x p`; the Model artifact holds `p` coefficients and cannot have it reconstructed from them, so for a model fitted before `covariance_blob` existed the only honest answers are a typed absence and a refit. It is a fourth reason beside FR-MODEL-77's three and it is **not** one of them: nothing about a GLM makes an interval impossible, the inputs to one were simply not kept. **A blob that should exist and does not is a platform fault and surfaces as one** — this reason is reachable only when the artifact itself records no blob, never when the store fails to resolve one, because a missing-blob incident reported as a modelling limitation is an incident nobody investigates. |
| **FR-MODEL-98** | **The platform offers exactly one interval kind on a prediction — `UncertaintyKind.confidence_interval_mean` — and adds a process-variance prediction interval only when a named consumer asks for one.** (OQ-MODEL-13, decided 2026-08-18. FR-MODEL-63 stands as amended by the note below this table; this requirement states the boundary that note left implicit.) `UncertaintyKind` is an enum a client matches on, so a second member is a contract change, and shipping one before anything consumes it puts two numbers on a screen that differ by an order of magnitude with nothing on the page saying which to trust. **The trigger is named so the decision cannot decay into a habit:** the first consumer of an aggregate predictive interval — `05-monitoring.md`'s portfolio work, or a capital or reserving reader — unblocks it. At that point the second kind is `prediction_interval`, computed as `φ·V(μ)` from `GlmFitResult.dispersion`, which is already stored, and it is offered **for aggregate predictions first**, because that is where the process variance averages away and the interval means something. `confidence_interval_mean` is never silently widened to become it. The case against the per-policy version is not cost: for a frequency model on one policy the honest interval is very nearly "0 or 1 claims", which is true, prices nothing, and reads as a malfunction to whoever asked for uncertainty. |
| **FR-MODEL-99** | **A penalised GLM (`alpha > 0`) reports its standard errors and its interval as now, and every response carrying them states the basis they were computed on: `UncertaintyBasis.unpenalised_information_matrix` rather than `information_matrix`.** (OQ-MODEL-14, decided 2026-08-18.) `glum` warns on every penalised fit that the covariance matrix *"will be incorrect"*, and it is right: what it returns is the information matrix of the **unpenalised** problem, which knows nothing about the shrinkage that produced the coefficients beside it. The error has a known direction — the interval is the one an unpenalised fit of the same design would earn, so it is **wider** than the shrunk estimate warrants — and conservative is not the same as right, which is why the qualification is carried rather than the number quietly kept. **FR-MODEL-21 and FR-MODEL-63 are answered together and could not be answered apart**: both are read off the same `V`, so refusing the interval would have had to take the coefficient standard errors with it, leaving a penalised fit with no uncertainty at all, and qualifying one without the other would describe a matrix that does not exist. **The basis is derived from `GlmSpec.alpha` in one place and never stored on the fit result** (`CLAUDE.md` §2): the spec is pinned to the fit by `spec_hash` and both are immutable, so a stored copy could only ever agree or be wrong. It is derived from `alpha` rather than from the library's warning text, which the fit swallows inside `catch_warnings` and which a patch release may reword. `l1_ratio` alone does not make a fit penalised — at `alpha = 0` there is no penalty to mix — though where the penalty is L1 the matrix additionally ignores that it *selected* the terms; the basis value is the same because the remedy is. **The exact answer is named with a trigger rather than deferred to nowhere:** a bootstrap (or a penalty-aware sandwich) over ~200 refits, which is a different cost class from a fit and therefore a Job rather than a fit-time step, is built when the first consumer needs valid penalised inference — a surface that renders coefficient intervals on a penalised fit, or an approval that cites them. Neither exists today: regularisation has no UI and nothing in §4.11's comparison reads the intervals. Owner: the slice that builds the first of them. |

> **Amendment, 2026-08-21 (the regularisation-and-CV slice).** This requirement predates
> `select_by == "cv"` and says nothing about it. Under CV selection, `GlmSpec.alpha` is
> pinned to `0.0` (the effective penalty comes from `cv.alphas` instead), so
> `uncertainty_basis` cannot read the selected alpha from the spec alone. Resolved as:
> every `select_by == "cv"` fit is treated as using the naive (penalised-fit) information
> matrix unconditionally, regardless of which alpha the scan selects. Conservative rather
> than exact — the elastic-net grid FR-MODEL-20 scans starts at zero and moves away from
> it, so a fit landing back on exactly zero is the rare point on the path, and the
> cautious label costs a display caveat rather than a wrong number on the common one.

> **FR-MODEL-98 addendum, 2026-08-19 (W5, the paired-quantile slice) — the boundary
> holds and gains a second door.** FR-MODEL-98 says the platform offers exactly one
> interval kind and names `prediction_interval` as the only future second. Building
> FR-MODEL-78 found a third case it did not anticipate: a paired-quantile interval
> covers `Y`, so it is not `confidence_interval_mean`, and it is produced by a
> different estimator at a different granularity from the `φ·V(μ)` computation
> FR-MODEL-98 reserves that name for. **Neither existing value is widened and the
> reserved name is not taken** — FR-MODEL-101 adds `quantile_pair_interval` beside
> them, and FR-MODEL-98's trigger still has its name waiting when its consumer
> appears. The requirement's *reason* is what admits this: it refused a second kind
> shipped before a consumer existed, and FR-MODEL-78's pair is opt-in at 2–3× the fit
> cost, so nobody receives one without having asked. Recorded as an addendum rather
> than an edit, per `CLAUDE.md` §14.

| **FR-MODEL-77** | **A GBM prediction states `uncertainty: unavailable` with a typed `reason` unless interval models were fitted for it** (OQ-MODEL-2, decided 2026-08-15) — `no_interval_models_fitted`, `interval_models_not_approved`, or `interval_models_stale` (fitted against a superseded Model version). **The variance-model approximation is not offered at all**, at any setting: it is cheap, it renders as a predictive interval, and it is not one — and a wrong interval on a price is worse than no interval. R5 is satisfied by the explicit statement of absence, never by an approximation that reads like a measurement. |

> **FR-MODEL-63 says "prediction intervals" and delivers a confidence interval on the
> expectation — the requirement is amended rather than the code renamed, 2026-08-18 (W5,
> the prediction slice).** They are two quantities and the covariance matrix yields only
> the first: `x'Vx` is the sampling variance of the estimated linear predictor, so
> `g⁻¹(η̂ ± z·√(x'Vx))` says how precisely the fit located `E[Y|x]`. A **prediction**
> interval for an individual outcome adds the process variance `φ·V(μ)`, which `V` does not
> contain — and for a frequency model on one policy that term dominates so completely that
> the honest interval is very nearly "0 or 1 claims", which is true and prices nothing.
>
> Pricing reads the expectation, so the useful interval is the one on the expectation, and
> the contract names it what it is: `UncertaintyKind.confidence_interval_mean`, never
> `prediction_interval`. **FR-MODEL-77 already refuses a GBM approximation on exactly this
> reasoning** — *it renders as a predictive interval and is not one* — and a correctly
> computed interval carrying the wrong name fails the same test one step later, in the
> reader rather than in the arithmetic. The level is fixed at 0.95, matching
> `Coefficient.ci_95`: an interval on a prediction and an interval on the coefficient it
> came from, reported at two different levels, is a comparison nobody can make.

> **All four `UnavailableReason` values are reachable from 2026-08-19 (W5, the
> paired-quantile slice).** FR-MODEL-87's staging rule required the two unreachable ones to
> be named in place; they were, in `UnavailableReason`'s docstring, and that note is removed
> with this slice rather than left describing a state the code has left. What the reasons
> *mean* was not decided by FR-MODEL-77 and is decided by FR-MODEL-100 — a requirement
> rather than an implementation choice, because "not approved" and "stale" each had two
> defensible readings, and the one built is the one a reader will assume was specified.

| **FR-MODEL-78** | **Paired quantile models are the supported route to a GBM prediction interval, opt-in and explicit** (OQ-MODEL-2). Each bound is a Model in its own right — same Model Family, same dataset version, split and factor set, fitted with the `quantile` template (§4.5) at a declared `alpha` — carrying `interval_for`, which names the central Model version and the alpha it estimates, so the 2–3× fit cost is a choice the actuary makes and can see. Crossing quantiles (a lower bound above its upper at any prediction) are **detected, reported in the diagnostics, and never silently reordered**: crossing means the pair does not describe one distribution, which the reader must be told rather than protected from. Whether §4.8 carries `interval_for` before the slice that fits one exists is OQ-MODEL-8's question, not this one. |
| **FR-MODEL-100** | **`interval_for` lives on `GbmSpec` and joins the `spec_hash` payload; the two readings FR-MODEL-77 left open are fixed here.** Added 2026-08-19 (W5, the paired-quantile slice), building FR-MODEL-78. **(i) The link is a spec field, not a Model column** — FR-MODEL-96 set the precedent for a Model that exists relative to another Model (`approximates_model_id` on the approximating Model's spec), and the reason is the same: the pairing is part of what the model *is*, so two bounds against different central versions must not collide under one `spec_hash`. `SPEC_HASH_VERSION` moves `v3` to `v4` in the same commit (FR-MODEL-86). **(ii) `interval_models_not_approved` means the bounds are less advanced than the model they bound**, not that they are unapproved outright — the strict reading would make the feature unusable before approval, which is exactly when an actuary is deciding whether the bounds are any good. The bounds must be at a lifecycle status at least as advanced as their central Model's; an `approved` Model quoting a `fitted` bound would put an unreviewed number beside a reviewed one. **(iii) `interval_models_stale` means the central Model is `superseded`** — the literal reading of FR-MODEL-77's "fitted against a superseded Model version". `SCOREABLE_MODEL_STATUSES` admits `superseded`, so a bound on a retired version is quotable and would otherwise be quoted with nothing saying the family has moved past it. **(iv) Exactly one bound per side.** A central Model carries at most one alpha below 0.5 and one above it; a second on either side is refused with `MODEL_INTERVAL_PAIR_INVALID`. Widening to a set of nested bands is additive; shipping an ambiguous set is not, because the response carries one `level` and nothing would say which pair produced it. |
| **FR-MODEL-101** | **A paired-quantile interval is reported as `UncertaintyKind.quantile_pair_interval`, a third member that is neither of the two FR-MODEL-98 names** (OQ-MODEL-16, decided 2026-08-19). FR-MODEL-98 fixed the platform at exactly one interval kind and reserved `prediction_interval` for a `φ·V(μ)` computation over aggregates; FR-MODEL-78's deliverable is neither of those and had no legal name in the enum. It is **not** `confidence_interval_mean`, which covers `E[Y\|x]`: a quantile pair covers `Y` itself, and FR-MODEL-98 says that value is never silently widened. It is **not** `prediction_interval`, which names a different estimator at a different granularity — taking it would leave FR-MODEL-98's named trigger with no name to fire into when its consumer appears. **FR-MODEL-98's boundary holds and is amended by addendum rather than edited** (`CLAUDE.md` §14): its argument was that a second kind must not ship *before a consumer exists*, and here the consumer is explicit — FR-MODEL-78 makes the pair opt-in at 2–3× the fit cost, so nobody receives one without having asked for it. The value names the **estimator** as well as the quantity, because a reader comparing a GBM's bound with a GLM's must be able to see they are not the same kind of claim. `basis` is forbidden on it — `UncertaintyBasis` describes a covariance matrix and a pair of quantile fits has none — and `interval_models` is required, naming the two Models the bounds came from. |
| **FR-MODEL-64** | Model lifecycle is `draft → fitted → review → approved → superseded → archived`. `fitted` requires diagnostics; `review` requires diagnostics, a transparency artifact where applicable, and a completed model-document draft; `approved` is by an Approver who is not the author (`06-governance.md`). |
| **FR-MODEL-65** | Model lineage records `parent_model_id` and a typed `change_reason` (`refit_new_data`, `respecified`, `rebanded`, `regrouped`, `hyperparameter_change`, `objective_change`, `bug_fix`) so a family's history reads as a narrative. |
| **FR-MODEL-66** | The `spec_hash` (§2, Model Spec) is computed over the canonicalised spec including pinned versions and seed. Submitting an identical spec returns the existing Model instead of refitting, unless `force_refit` is set — which then requires the two fits to be compared for reproducibility (FR-OVR-8). |
| **FR-MODEL-67** | A Model whose Dataset Version was invalidated (`01` FR-DATA-23) is flagged `dataset_invalidated` and cannot advance to `approved`; if already `approved`, the flag propagates to every Rating Version referencing it and to the Approvals inbox. |
| **FR-MODEL-86** | **`spec_hash` carries the version of the algorithm that produced it, inside the hashed payload.** The digest is `v<n>:sha256:<64 hex>` where `n` is `SPEC_HASH_VERSION`, and the same `n` is one of the hashed fields — a prefix alone would let a reader strip it and compare across versions, which is exactly the comparison that is not meaningful. **Any change to the set of fields entering the payload increments `n` in the same commit as the field**, and `spec_hash_is_current` reports every older digest as stale so the affected rows are findable (`LIKE 'v1:%'`). Without this, one added field silently changes every stored digest and FR-MODEL-66's dedup ends with no error to see. The rule has been exercised twice: `split_ref` moved the digest `v1 → v2` (2026-08-16) and `loss_treatment` moved it `v2 → v3` (2026-08-17). (OQ-MODEL-8, decided 2026-08-17.) |
| **FR-MODEL-87** | **§4 is a staged contract: a field is shown live only once a slice populates it, and anything else is named in place with a dated note saying it is declared-and-unbuilt and which workstream owns it** (OQ-MODEL-8, decided 2026-08-17). The alternative — declaring the eventual shape and letting the reader discover which fields are always null — teaches that null means *nothing* rather than *not yet*, and the frontend generates from this contract. At the decision date the residuals are, with verdicts: **absent entirely** — `filter` on `ModelSpec` and `custom_objective_ref` on `GlmSpec`, all owned by Phase 1b; **declared and unbuilt, as §4.8 already says of them** — `transparency_artifact_id` and `custom_objective_ref` on `Model`, owned by W5 and Phase 1b respectively; **present under a different shape** — §4.4's nested `regularisation` block, corrected to `GlmSpec`'s flat fields by this change. Six fields have gone live under this rule already (`banding_id`, `grouping_id`, `split_ref`, `diagnostics_id`, `loss_treatment`, `approval_request_id`); **`interval_for` is the seventh, live 2026-08-19** on `GbmSpec` rather than on `Model` (FR-MODEL-100), and it leaves the absent-entirely list above with this change rather than being quietly dropped from it. **`select_by` and `cv` are the eighth, live 2026-08-21** (the regularisation-and-CV slice), on `GlmSpec` — `select_by: "fixed" \| "cv"` and the nested `cv: GlmCvSpec` block, the shape the FR-MODEL-20/FR-MODEL-53 CV path built rather than the flat `select_by`/`cv_folds` fields the decision date named — and they leave the absent-entirely list above with this change rather than being quietly dropped from it. **Tweedie power estimation — live 2026-08-21 (FR-MODEL-22)**; the estimation × CV-selection pair is refused by name, not built. **`offset_model_ref` is the ninth, live 2026-08-21** (the offset-from-another-model slice), on `OffsetSpec` — `kind: "model"` with the canonical `model:slug@version` ref, GLM-to-GLM only; `GbmSpec` naming it, and refs naming non-fitted, non-GLM or link-mismatched models, are refused by name (`MODEL_OFFSET_REF_INVALID`). |
| **FR-MODEL-88** | **The unimplemented arms of FR-MODEL-1's closed set are refused by name at resolution, never approximated.** Four of the eight — `spline`, `polynomial`, `offset` and `expression` — do not resolve, and `resolve_factors` raises naming the type rather than returning the raw column, because a fit built on the raw column is one nobody could tell from a correct one. **`expression` is the sharper case and its verdict is stated rather than implied:** `FactorType.EXPRESSION` is selectable while `Factor` carries no field to hold the expression, so a factor of that type can be *created* and can never be *resolved*. That is contained rather than corrected — the refusal is at the boundary where it would matter — and the field plus its validator arm are owned by Phase 1b with the rest of §4.7's expression work. (OQ-MODEL-8, decided 2026-08-17.) |
| **FR-MODEL-89** | **§4.8 R3 is enforced artifact→model, because that is the direction the link runs.** The `TransparencyArtifact` carries `model_id` and the `Model` carries no back-reference that anything writes, so "`model_type ≠ glm` and `status = approved` ⟹ a transparency artifact exists" is checked by querying for an artifact naming the model at the approval transition, not by reading a column on the model. Stating it as a field-set invariant made it unenforceable — the same shape as §4.8's `status ≥ fitted ⟹ diagnostics_id`, which OQ-MODEL-8 was written around. (OQ-MODEL-8, decided 2026-08-17.) |

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
  "operand_factor_ids": [],
  "expression": null,
  "base_level": "36-45",
  "base_level_method": "largest_exposure"
}
```

**Amended 2026-08-18 (W5, the interaction slice).** `operand_factor_ids` is new, and it is
what makes FR-MODEL-1's `interaction` type expressible: the field carries the Factors being
crossed, by id, for the reason `banding_id` carries a Banding by id — a slug changes meaning
the next time someone re-cuts a boundary. FR-MODEL-91 has the design and its consequences.

Two things about the example above, so a reader does not take either for a promise:

- **`source_columns` is empty for an interaction and required for everything else.** An
  interaction's columns are its operands'; listing them again is a second statement of one
  fact, and the two disagree the first time an operand is re-versioned onto another column.
  The rule is per type in the validator rather than on the field, so relaxing it here did
  not relax it anywhere else.
- **`expression` is still printed here and still does not exist on the type.** That is
  FR-MODEL-88's recorded verdict (OQ-MODEL-8, 2026-08-17) and not an oversight this slice
  introduced; it is named again only so the next reader does not "fix" one divergence while
  believing they fixed both.

### 4.2 `Banding`

```json
{
  "id": "uuid",
  "slug": "driver-age-actuarial-v2",
  "dataset_id": "uuid",
  "version": 2,
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
`labels` length = `len(boundaries) - 1`; labels unique; `null_level`, where set, is not also
a band; no empty band (FR-MODEL-11).

The first five are enforced on the type and answer `422` at the edge. The **last is not**,
and cannot be: emptiness is a fact about a Dataset Version, not about the artifact, so
`check_banding` answers it at fit time and a banding that is fine on one version can be
empty on the next.

> **Two corrections to this section's own contract, 2026-08-15 (W5), both found by
> implementing it.**
>
> * **`band_stats` is keyed by `level`, not `label`.** `banding.schema.json` said `label`
>   while `profile.schema.json` said `level` — for the same statistics, from the same
>   requirement (`01` FR-DATA-26). A band *is* a level, so the banding schema now points at
>   the one-way row shape and `Banding.band_stats` is `01`'s `OneWayRow`. Two definitions of
>   "the frequency of this cell" would disagree in the fourth digit with nothing to say
>   which screen was right.
> * **`minimums` lives on the Banding**, as this schema always declared and the
>   implementation first did not — it took the thresholds as arguments to the fit-time
>   check. FR-MODEL-11 says *configurable*, and configuration a reviewer cannot read is a
>   default with extra steps: two fits of the same banding could apply different floors and
>   the artifact would record neither.

> **Where the last band ends (added 2026-08-15, W5).** Under `closed: "left"` band *i* is
> `[bᵢ, bᵢ₊₁)` **except the last, which is `[bₙ₋₁, bₙ]`** — closed at both ends;
> `closed: "right"` is the mirror image. Without that a banding derived from the observed
> range declares its own maximum out of range, and every `exposure_quantile` proposal fails
> on the data it was proposed from. The example's `999` upper bound is a sentinel chosen for
> headroom, not a requirement.

### 4.3 `Grouping`

```json
{
  "id": "uuid",
  "slug": "vehicle-group-to-rating-group",
  "dataset_id": "uuid",
  "version": 1,
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

> **Amended 2026-08-15 (W5).** Three corrections the implementation forced, and one it
> **got wrong**:
>
> * **The credibility standard lives in `method_params` as `credibility_model`** — as
>   this schema always said. The implementation first added a top-level
>   `credibility_standard` field, contradicting `grouping.schema.json`, which had
>   carried `method_params.credibility_model` since Phase 0. Corrected here rather than
>   in the code alone: a hand-authored contract is not a draft, and not reading one
>   before adding a field beside it is how a shape gets defined twice.
> * **`band_stats` and `target_level_stats` are `01`'s `OneWayRow`**, not a second shape
>   of the same numbers. A band is a level, `01` FR-DATA-26 already defines a level's
>   statistics with its intervals, and two implementations of "the frequency of this
>   cell" would disagree in the fourth digit with nothing to say which screen was right.
>   The example's `relativity` on a target level is therefore **not** a stored field — it
>   is `claim_count / exposure_years`, derived where it is shown.
> * **`deviance_before` and `deviance_after` are row-level Poisson deviances** of two
>   one-factor fits against the same saturated model, so their difference is the
>   likelihood-ratio statistic on `df_saved`. They are a *marginal* statement about this
>   factor alone, not the deviance the eventual multi-factor model reports.

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

> **`offset_model_ref` — declared 2026-08-21 (W5 slice 4, FR-MODEL-24).** The common
> block's `offset` gains the field: a canonical `model:slug@version` string, valid only
> with `kind: "model"`, naming the fitted GLM whose linear predictor is the offset
> (FR-MODEL-24 as amended). **Live 2026-08-21** (the offset-from-another-model slice). A `GbmSpec`
> naming it is refused by name, and a ref naming a non-fitted, non-GLM, or
> link-mismatched model is refused at fit time (`MODEL_OFFSET_REF_INVALID`).

`loss_treatment` is part of the spec — and therefore of `spec_hash` — because capping is
applied to the **response at fit time** (FR-MODEL-73). Two models differing only in their
cap are different models, and must not collide on `spec_hash`.

`GlmSpec` adds:

```json
{
  "family": "poisson",
  "family_params": {},
  "link": "log",
  "alpha": 0.001, "l1_ratio": 0.0,
  "select_by": "fixed", "cv": null,
  "tweedie": null,
  "max_iter": 200, "tolerance": 1e-8,
  "approximates_model_id": null
}
```

> **Corrected 2026-08-17 (W5, OQ-MODEL-8).** This block used to show a nested
> `regularisation: {"kind": "elastic_net", "alpha": …, "l1_ratio": …, "select_by": "cv",
> "cv_folds": 5}` and a `custom_objective_ref`. `GlmSpec` implements the two penalty
> parameters **flat**, as `glum` takes them, and carries neither the selection fields nor
> the objective reference. **The spec was the wrong side here**: the nested shape was
> written in Phase 0 and nothing was ever built to it, so a caller copying this page would
> have sent a body the contract rejects — a divergence rather than a field awaiting a slice.
> `select_by` / `cv_folds` (penalty selection by cross-validation) and `custom_objective_ref`
> on the GLM arm are **absent entirely** and owned by Phase 1b (FR-MODEL-87). *(Amended
> 2026-08-21, the regularisation-and-CV slice.* **The selection fields landed this date
> and are no longer absent** — under a nested `cv: GlmCvSpec` block rather than the flat
> fields this note names: `GlmSpec.select_by: "fixed" | "cv"` (default `"fixed"`), and
> `cv: GlmCvSpec | null` carrying the scan, `null` under `"fixed"` selection. The shape
> is the one the FR-MODEL-20/FR-MODEL-53 CV path built, mirroring `GbmSpec`'s nested
> `early_stopping`. **The seed is not duplicated on the block**: the seed that makes fold
> assignment reproducible is `ModelSpecCommon.seed` — the one seed the spec already
> carries and already versions into `spec_hash` — and a second seed field would let the
> two disagree. `custom_objective_ref` on the GLM arm remains absent entirely.)*

`GlmCvSpec` is the block `cv` carries when `select_by` is `"cv"`:

```json
{
  "method": "random | temporal | grouped_by_key",
  "folds": 5,
  "alphas": [0.0, 0.001, 0.01, 0.1, 1.0],
  "key_column": null,
  "time_column": null
}
```

> **Added 2026-08-21 (the regularisation-and-CV slice).** `cv` carries the cross-validated
> penalty path when `select_by` is `"cv"` and is `null` under `"fixed"` selection. The
> selection fields the correction note above listed as absent entirely landed this date
> under this **nested shape** rather than as the flat `select_by`/`cv_folds` fields the
> note named — the shape the FR-MODEL-20/FR-MODEL-53 CV path built, mirroring `GbmSpec`'s
> nested `early_stopping`. **`method` is `01` FR-DATA-33's three fold-construction
> methods**, generalised from its two-part cutoff split to K folds by
> `pricing_core.data.splits.assign_folds`: `random` reuses the same seeded draw as `01`'s
> split; `temporal` sorts ascending by `time_column` and cuts the sorted order into
> contiguous equal-count blocks; `grouped_by_key` keeps `key_column`'s groups whole
> across folds. The last two name their column, required when that method is chosen.
> `alphas` is the elastic-net penalty path scanned (two or more distinct non-negative
> points, `l1_ratio` fixed by `GlmSpec.l1_ratio` for every point). **The seed is not
> duplicated on this block**: the seed that makes fold assignment reproducible is
> `ModelSpecCommon.seed`, the one the spec already carries and already versions into
> `spec_hash`, and a second seed field would let the two disagree.

`TweediePowerSpec` is the block `tweedie` carries when estimation is requested:

```json
{
  "p_grid": [1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95]
}
```

> **Added 2026-08-21 (FR-MODEL-22).** `tweedie` carries the profile-likelihood grid when
> `p` is to be estimated, and is `null` under a fixed-power spec — estimation is opt-in,
> and a fixed-power spec is today's spec, unchanged. **The estimate is fit-time and
> never a spec constant**: the estimated power and its uncertainty are facts of the fit
> and ride on `fit_result.tweedie` (§4.8), which is why this block declares only the
> scan. The grid is the scan's boundary — a scan, not a choice: one point would be a
> fixed fit, and a maximum at either edge of the scan is refused at fit time with
> `GLM_TWEEDIE_POWER_GRID_EDGE`, because it would report the scan's boundary as the
> answer. The default is a ten-point scan strictly inside the family `(1, 2)`; the grid
> must have at least two points, strictly increasing, each finite and strictly inside
> the family.

`GbmSpec` adds (`model_type` is `xgboost` or `lightgbm` — see the amendment below):

```json
{
  "objective": {"kind": "builtin", "name": "count:poisson"},
  "monotone_constraints": "derived_from_factors",
  "interaction_constraints": [["driver_age_banded", "vehicle_group_rated"], ["ncd", "annual_mileage"]],
  "hyperparameters": {"max_depth": 5, "eta": 0.05, "subsample": 0.8,
                      "colsample_bytree": 0.8, "min_child_weight": 200,
                      "lambda": 1.0, "alpha": 0.0, "num_boost_round": 2000},
  "early_stopping": {"on": "holdout", "metric": "poisson-nloglik", "rounds": 50},
  "categorical_handling": "native",
  "backend_params": {"tree_method": "hist"},
  "eval_metrics": [{"kind": "builtin", "name": "poisson-nloglik"},
                   {"kind": "custom", "ref": "custom_metric:capped-gamma-nll@2"}],
  "interval_for": {"model_id": "uuid", "model_version": 7, "alpha": 0.05}
}

> **`interval_for` is live from 2026-08-19 (W5, the paired-quantile slice)** —
> FR-MODEL-87's staging rule, and the last of the fields OQ-MODEL-8 listed as
> absent-entirely on this arm. `null` on every GBM that is not itself a bound, which is
> almost all of them: it is the declaration that *this* model is one side of another
> model's interval, and FR-MODEL-78 makes that an opt-in the actuary pays 2–3× a fit
> for. On the spec rather than on `Model` because it changes the model's identity —
> FR-MODEL-100(i) has the argument and the FR-MODEL-96 precedent it rests on.
```

`objective.kind = "custom"` replaces `name` with `ref: "custom_objective:<slug>@<version>"`.

> **Amended 2026-08-17 (W5, the GBM arm).** Three corrections, made by building the union.
>
> * **`backend` is removed; `model_type` is the backend.** This arm declared
>   `backend: "xgboost" | "lightgbm"` beside a `model_type` carrying the same two strings.
>   Two fields holding one fact can disagree, and nothing downstream could say which to
>   believe — so the discriminator the union already turns on is the one that survives.
>   `GbmSpec.model_type` is therefore `Literal["xgboost", "lightgbm"]`, and a payload still
>   carrying `backend` is refused rather than ignored.
> * **`base_margin` is removed from the spec; the common block's `offset` is the single
>   declaration.** FR-MODEL-27 says the platform *constructs* `base_margin` from the
>   declared offset, so a second declaration here was a second source of truth for the one
>   number the fit silently depends on. What was actually constructed is recorded on the
>   **fit result** (`GbmFitResult.base_margin`), which is where FR-MODEL-71's load-time
>   assertion needs it.
> * **`loss_treatment` sits on the common block, not on this arm.** FR-MODEL-73 applies it
>   to the *response*, which is not a property of the learner. It is `{kind, cap_minor,
>   restoration_loading, evidence_blob}`, with `cap_minor` in integer minor units
>   (`CLAUDE.md` §7). `spliced` and `excess` are declared and **refused by the fit path**
>   until a slice implements them: narrowing the enum now would cost a `spec_hash` version
>   to widen later, and the digest algorithm went to **v3** for this field alone.
>
> Two constraints the built contract adds, neither of which the JSON above implied:
>
> * `categorical_handling` has **no default** — a default would be FR-MODEL-32's silence.
> * `early_stopping.on` has **no `train` value**, and `on: "holdout"` requires `split_ref`.
>   FR-MODEL-30 refuses training-set early stopping; reaching it by omitting the split is
>   the same defect arrived at more quietly.

> **Amended 2026-08-17 (W5, found by the `wf-01` journey test).** **A banded Factor is
> ordinal, and `categorical_handling: "native"` does not apply to it.** Its levels are
> coded in the Banding artifact's own `labels` order — boundary order, which is the order
> of the underlying values — and the feature is handed to the backend as an ordered
> integer, not as a categorical.
>
> Both halves were wrong before, and the example above is the one that failed. Coded
> alphabetically, `"10-49"` sorts second, between `"0-1"` and `"2-4"`, so a monotone
> constraint on `driver_age_banded` would hold in the alphabet — and it would still fit,
> still persist `-1`, and still read as an actuarial judgement. Declared categorical it
> cannot hold at all: **LightGBM refuses monotone constraints on a categorical feature and
> does so by aborting the process** (`[LightGBM] [Fatal] The output cannot be monotone with
> respect to categorical features`, verified on 4.7.0), so the constraint this very example
> declares was unreachable on the secondary backend.
>
> FR-MODEL-32 is unaffected: it refuses the silent label-encoding of an **unordered**
> categorical, and a band is ordered with its map persisted. FR-MODEL-31's dtype
> expectations carry the distinction — `f64` numeric, `ord` ordered codes, `cat` native
> categorical — because scoring must declare exactly what fitting declared, and the
> encoding maps alone cannot say which a coded feature is.

> **Amended 2026-08-18 (W5, the custom-objectives slice).** **`response` is required
> whenever `objective.kind` is `custom`.** The common block has declared it beside
> `response_column` since Phase 0 and nothing read it, because a builtin objective names
> its own family and the column carries the numbers. A Custom Objective names **no**
> family, so `response` becomes the only thing FR-MODEL-44's applicability check and the
> diagnostics deviance can be read from. `ModelSpecCommon.response` is therefore
> `ResponseKind | None` — optional, so that specs written before this slice stay valid —
> and `fit_gbm` refuses a custom objective on a spec that leaves it unset, with
> `OBJECTIVE_RESPONSE_UNDECLARED`. Guessing it would produce a `capped_gamma` severity
> model whose A/E was computed as a Poisson deviance and reported without comment.
>
> `ResponseKind` is `claim_count | claim_severity | burning_cost | conversion | retention`.
> The last two are `04-optimisation.md`'s demand responses, present because `focal_binomial`
> (§4.5) exists for exactly them: a catalogue entry whose applicability could not be
> written would be one nothing could use.

> **`approximates_model_id` is live from 2026-08-19 (W5, FR-MODEL-96)**, on `GlmSpec`
> rather than on the common block: only a GLM approximates another model, and a field
> defined on the union rather than on the arm that uses it is a field the other arm will
> eventually be asked to spell.
>
> **It is a bare `UUID`, and that is a deliberate divergence from `interval_for`.**
> FR-MODEL-100 gave the paired-quantile link a block carrying the central model's id *and*
> version, because `motor-ad-frequency@7` is what a human reads in a review and a UUID is
> not. This field is a bare id because FR-MODEL-96 names it that way and a block under a
> different name would contradict the requirement — and because `interval_for` needed a
> block regardless, carrying `alpha`, while this carries nothing else. A reviewer resolves
> one id to get the version.
>
> **`spec_hash` moves `v4` to `v5` with it** (FR-MODEL-86): the model a surrogate
> approximates is part of what that surrogate *is*, and two approximations of two different
> GBMs over one population would otherwise share a digest — which FR-MODEL-66 would answer
> by handing the second caller the first caller's model.

### 4.5 Custom objective — `template` catalogue

Shipped templates, each with analytic gradient/hessian in `pricing-core` (FR-MODEL-39):

| Template | Params | Loss (per observation, `f` = raw score, `μ = exp(f)` for log-link forms) | Typical use |
|---|---|---|---|
| `poisson` | — | `μ − y·f` | Frequency baseline |
| `gamma` | — | `y/μ + f` | Severity baseline |
| `tweedie` | `p ∈ (1,2)` | `−y·μ^(1−p)/(1−p) + μ^(2−p)/(2−p)` | Burning cost; `p` tunable and CV-selectable |
| `capped_gamma` | `cap` (minor units) | Gamma loss on `min(y, cap)` | Large-loss-adjusted severity |
| `spliced_severity` | `threshold` (minor units), `tail_shape` = α | Gamma below the threshold; above it a Pareto negative log-likelihood **scaled by μ**, `−α·f + (α+1)·log y − log α` | Attritional vs large split in one model |
| `asymmetric_squared` | `w_under`, `w_over` | `w_under·(y−μ)²` if `μ < y` else `w_over·(y−μ)²` | Under-pricing penalised harder than over-pricing |
| `asymmetric_poisson` | `w_under`, `w_over` | Poisson deviance with side-dependent weights | Same intent, count response |
| `huber` | `delta` | Quadratic within `delta`, linear beyond | Outlier-robust burning cost |
| `pseudo_huber` | `delta` | Smooth Huber (twice differentiable everywhere) | Preferred where hessian smoothness matters |
| `quantile` | `alpha` | Pinball loss | Paired quantile models — the only supported GBM prediction interval (FR-MODEL-63, FR-MODEL-78) |
| `zero_inflated_poisson` | `pi ∈ (0,1)` | ZIP negative log-likelihood | Very low-frequency perils |
| `focal_binomial` | `gamma` | Focal loss on logistic | Heavily imbalanced conversion models |

Each template declares its `applicability` block (FR-MODEL-44) and its own parameter
validity ranges (e.g. `tweedie.p ∈ (1, 2)` exclusive, `cap > 0`).

**This catalogue is the whole of Phase 1's custom-objective surface** (FR-MODEL-75,
OQ-MODEL-1 decided 2026-08-15): `expression` objectives ship in Phase 2, behind a flag that
is off until they do. A template still certifies (§4.7, FR-MODEL-76) — the machinery is
built here, on losses whose derivatives `pricing-core` already knows, so that the first
user-authored loss meets a certification path that has been running for a phase.

> **Amended 2026-08-18 (W5), three cells corrected by building the catalogue.**
>
> * **`zero_inflated_poisson` takes `pi`, not `pi_link`.** `pi` is the zero-inflation
>   probability itself, on `(0, 1)` exclusive, declared by the author and held fixed. A
>   *link* would imply a second linear predictor the booster fits alongside the count one,
>   which is a two-part model rather than a template — and nothing in Phase 1 fits one.
> * **`capped_gamma` carries no loading.** Restoring the uncapped mean is
>   `loss_treatment: {kind: "capped", cap_minor, restoration_loading, evidence_blob}` on the
>   Model Spec (§4.4, FR-MODEL-73/74), where it is part of `spec_hash` and demands its
>   evidence. The objective is the loss and nothing else: an objective that quietly
>   re-inflated its own predictions would make two models with the same `spec_hash` price
>   differently. The two are used together — the cap in the objective, the loading in the
>   treatment — and the catalogue cell said so in a way that read as one artifact.
> * **`spliced_severity`'s tail is scaled by μ, not by the threshold.** "Pareto-style" left
>   the scale parameter unstated, and the two readings are different models: a
>   threshold-scaled tail has no dependence on `f` above the threshold, so its gradient is
>   zero there and the booster learns nothing from a single large claim. Tying the scale to
>   `μ = exp(f)` keeps the tail responsive to the covariates, which is the reason to splice
>   rather than to truncate.
>
> **`asymmetric_poisson` was already right, and the code was wrong.** The cell says *unit
> deviance*, and the first implementation used the log-likelihood term `μ − y·f`. §4.7's
> `minimum_at_truth` check reported that stepping away from the stationary point *lowered*
> the loss: the likelihood term is negative over most of the domain and does not vanish at
> `μ = y`, so a `w_under > 1` multiplying a negative number penalises under-prediction by
> making it cheaper. The deviance `2(y·log(y/μ) − y + μ)` is non-negative and zero exactly
> at `μ = y`, so the branches meet, the minimum stays at `f = log y`, and only the slopes
> differ — which is what an asymmetric pricing loss is for. Recorded here because it is the
> certification machinery catching a defect in the thing it certifies, on the day it was
> built.

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

> **Amended 2026-08-18 (W5), built.** Six corrections, all in the code's favour bar the
> last, which is in the contract's.
>
> * **The certificate is two objects, not one.** `ObjectiveCertificate` carries the
>   identity — `id`, `custom_objective_id`, `objective_version`, `certified_at`, `job_id` —
>   and wraps a `result: CertificateResult` holding `checks`, `sampling`, `overall` and
>   `library_versions`. The JSON above shows them flat. The split is ADR-0001: `certify_objective`
>   computes the findings in `pricing-core`, which may not allocate an id, read a clock or
>   know a Job exists, so what it returns is the `CertificateResult` and the backend stamps
>   the rest. The same split as `compute_diagnostics`/`DiagnosticsResult`.
> * **`overall` is derived, never supplied.** `CertificateResult.outcome_of(checks)` is the
>   single place the rule lives, and a validator refuses a result whose stated `overall`
>   disagrees with its own checks: any `failed` ⇒ `failed`; otherwise any `warn` or
>   `violated` ⇒ `certified_with_findings`; otherwise `certified`. A certificate that could
>   be written with a verdict its findings do not support is not evidence.
> * **`CheckStatus` is `pass | warn | violated | failed`** — four values, and `failed` is
>   spelled in full. The published schema said `fail`; a reader deserialising against it
>   would have rejected every certificate this platform produces.
> * **All nine checks are emitted for every template, always**, in this order:
>   `analytic_vs_numeric_gradient`, `analytic_vs_numeric_hessian`, `finiteness`,
>   `convexity`, `branch_discontinuity`, `minimum_at_truth`, `monotone_loss`,
>   `scale_behaviour`, `smoke_fit`. A check omitted because it had nothing to report is
>   indistinguishable from one that was never run, so a template with no branch reports
>   `branch_discontinuity: pass` with "no branch boundary to exclude near" rather than
>   dropping the row.
> * **The step is `h = 1e-4`, not the `1e-6` the illustrative details show.** `1e-6` is
>   below the point where central-difference cancellation dominates truncation for losses on
>   this scale, so it makes correct derivatives look wrong. The detail strings report the
>   step they actually used, which is the reason FR-MODEL-70 asks for it.
> * **`sampling.n_points` has a floor of 1 000, and it is enforced at the type**
>   (`SamplingSpec`), not at the API. The floor came from the published schema — the one
>   place the contract was right and the model was not: `convexity` and `scale_behaviour`
>   report a *share of sampled points*, and over a coarse grid every check passes by not
>   looking. It sits on the type because `record_certificate` is not the only door; a
>   certificate is evidence wherever it is made.
>
> **The derivative comparison's tolerance was found wrong by raising that floor**, and the
> fix is recorded here because the check is the spec's own instrument. `_agreement`
> subtracts the finite-difference noise from the difference as well as flooring the
> denominator with it. Flooring alone is not enough where the derivative is orders of
> magnitude smaller than the quantity being differenced: a Gamma hessian of `5.5e-07`
> against a gradient of `0.33` carries `6e-12` of cancellation noise, so an agreement to
> `9e-13` — inside what the method can resolve — divided out as a relative error of
> `1.6e-06` and warned. Three of the twelve templates warned on exactly correct derivatives
> at 1 000 points. Loosening a tolerance is how a check stops checking, so the other side is
> pinned by test: an absolute error of `1e-08` in the Gamma hessian — two hundred times the
> noise where that hessian is smallest — is still `failed`.

> **`MetricCertificate` (FR-MODEL-105), added 2026-08-19.** Same two-object split as
> `ObjectiveCertificate` and for the same ADR-0001 reason: `certify_metric` computes a
> `CertificateResult` in `pricing-core`, which may not allocate an id, read a clock or know
> a Job exists, and the backend stamps `id`, `custom_metric_id`, `metric_version`,
> `certified_at` and `job_id` around it. The four checks:
>
> * **`finiteness`** — no NaN or inf over the sampled `(y, f, w)` domain, the same check
>   §4.7 already runs for objectives.
> * **`direction_holds`** — the metric is better at `f = log(y)` than at a perturbed `f`, in
>   the direction the metric declares (FR-MODEL-104). This is the metric's analogue of
>   `minimum_at_truth`, and it is the check that catches a `direction` declared backwards —
>   the defect that silently halves the value of early stopping.
> * **`scale_behaviour`** — how the value moves with the magnitude of `y`, reported so a
>   reader can tell a metric that spans six orders from one that does not.
> * **`smoke_evaluation`** — on synthetic data whose answer is computable by hand, the
>   metric returns that value within tolerance.
>
> `overall` is derived by the same `CertificateResult.outcome_of` and never supplied.

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
    "tweedie": {
      "estimated_power": 1.47,
      "ci_lower": 1.36, "ci_upper": 1.58, "level": 0.95,
      "curve": [
        {"power": 1.05, "log_likelihood": -33142.7},
        {"power": 1.35, "log_likelihood": -33051.2},
        {"power": 1.65, "log_likelihood": -33180.4}
      ]
    },
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

> **`tweedie` is live from 2026-08-21 (FR-MODEL-22)** — the estimated Tweedie power,
> persisted as an estimate with its own uncertainty, never a constant. `null` under a
> fixed-power spec: estimation is opt-in (§4.4). When `spec.tweedie` requested
> estimation, `estimated_power` is the argmax of the **profile log-likelihood** over
> the scanned grid, and `curve` carries the profile log-likelihood at each scanned
> power — each point scored with the Tweedie series density (Dunn & Smyth 2005) at the
> mean-deviance dispersion estimate, the dispersion profiled rather than jointly
> maximised. The 95% interval (`ci_lower`/`ci_upper`, `level: 0.95`) is read from the
> likelihood ratio at the χ²₀.95(1) cutoff, linearly interpolated between scanned
> points. **Diagnostics, type-III refits and backtest deviance reads use the estimate**
> (via `_power_of`), so a refit reproduces the same deviance figures — the estimated
> power is a property of the fit, not of the spec.

> **`split_ref` and `diagnostics_id` are live from 2026-08-16 (W5, diagnostics).** Both
> were among the fields OQ-MODEL-8 named as declared-and-dead, and `diagnostics_id` was its
> own worked example: §4.8's `status ≥ fitted ⟹ diagnostics_id` could not be met because
> diagnostics did not exist, so the spine enforced `fitted ⟹ fit_result` instead. The
> invariant now holds at the type, at a database CHECK, and in the fit path, which writes
> both in one transaction.
>
> This is the recommendation on file — "re-widen it as the slices land" — not a decision
> taken ahead of the maintainer. `loss_treatment` landed with the GBM slice on 2026-08-17;
> `expression` and `filter` stay unimplemented, and OQ-MODEL-8 was **decided 2026-08-17**
> on exactly that staging rule — FR-MODEL-87 carries it, and names them with their owners.
>
> **`split_ref` is required to reach `fitted`**, though the field itself is optional: a
> spec may be explored without one, but FR-MODEL-54 makes a diagnostic without its holdout
> counterpart a defect and FR-MODEL-64 makes diagnostics the condition of `fitted`, so a
> fit with no split is refused with `MODEL_SPLIT_REQUIRED` before any compute is spent.
> The obligation sits on `Model`, where the status is, rather than on the spec.
>
> **`spec_hash` is now `v2`.** Adding a field to `GlmSpec` changes the digest, which the
> algorithm version exists to make legible: every `v1:` digest is findable with
> `LIKE 'v1:%'` and reported stale by `spec_hash_is_current`.

> **`covariance_blob` is live from 2026-08-18 (W5, the prediction slice)** — FR-MODEL-87's
> staging rule, and the first field to go live where the *absence* also needed a spelling.
> It is a blob rather than a field because it is `p x p`: a model with 150 terms carries
> ~250 KB that every read of the Model row would otherwise pay for, and only the prediction
> path needs it. The bytes are canonical JSON carrying the term order **inside** the
> payload, so a matrix decoded against a different coefficient set is refused rather than
> silently transposed into a plausible interval.
>
> **It is optional, and every Model fitted before this date has none.** That is what
> FR-MODEL-93 exists for: the artifact holds `p` numbers where the matrix is `p x p`, so no
> migration can backfill it and a refit is the only route to an interval. The typed reason
> is the difference between saying so and an interval quietly missing from the response.

> **A surrogate Model reaches `fitted` on diagnostics against another model's predictions**
> (FR-MODEL-96(iii), built 2026-08-19). §4.8's `status ≥ fitted ⟹ diagnostics_id` is met
> the same way every other model meets it, and the quantity is different: the A/E, lift and
> calibration are the surrogate against the source GBM's predictions over the same split —
> FR-MODEL-36's quantity, on both partitions. Nothing on the `Diagnostics` document says so,
> and nothing needs to: FR-MODEL-102 makes the spec say it, and a fact stated in two places
> diverges.
>
> **It carries no `covariance_blob`.** The bytes exist at fit time and are deliberately
> dropped, so a prediction against a surrogate reports FR-MODEL-93's typed absence rather
> than an interval. The interval would be a correct statement about the surrogate's
> coefficients and would be read as the GBM's uncertainty; FR-MODEL-77 already refuses a
> GBM approximation on exactly this ground.

> **`flags` and `approval_request_id` are live from 2026-08-17 (W5, the lifecycle).** Both
> were on OQ-MODEL-8's list of fields declared and dead; the slice that creates an approval
> request is the one that can populate the second, which is that question's own "re-widen it
> as the slices land".
>
> **`flags` is computed, not stored, and that is a decision rather than an implementation
> detail.** `01` FR-DATA-23 makes validation re-runnable on an already-validated version, so
> a dataset that passed under an older rule set can reach `failed` long after a model was
> fitted on it. A column written at fit time would then answer `[]` for exactly the model
> FR-MODEL-67 exists to stop. It is derived from the Dataset Version's *current* status on
> every read that gates on it, and recorded in the audit event at submission so that "was it
> flagged when it was submitted?" survives the dataset moving again.
>
> `transparency_artifact_id` and `custom_objective_ref` stay declared and unbuilt. That is
> now a stated verdict with an owner rather than an open question: OQ-MODEL-8 was decided
> 2026-08-17 and FR-MODEL-87 lists them, while FR-MODEL-89 restates R3 in the direction the
> link actually runs.

**Invariants** — `status ≥ fitted` ⟹ `diagnostics_id` set; `model_type ≠ glm` and
`status = approved` ⟹ a `TransparencyArtifact` naming this model exists (R3);
`custom_objective_ref` set and `status = approved` ⟹ that objective version is
`approved` (R4); `booster_blob` present iff `model_type ∈ {xgboost, lightgbm}`.

> **R3 restated 2026-08-17 (W5, OQ-MODEL-8) — FR-MODEL-89.** It used to read
> `⟹ transparency_artifact_id set`, which cannot be enforced: the artifact landed on
> 2026-08-17 carrying `model_id`, so the link runs artifact→model and nothing writes the
> column on this side. The obligation is unchanged and the direction of the check is
> now the one the data supports — a query for an artifact naming the model, run at the
> approval transition. `transparency_artifact_id` itself stays declared and unbuilt
> (FR-MODEL-87).

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

> **`approximating_model_id` is live from 2026-08-19 (W5, FR-MODEL-96).** The block holds
> the *measurements* — R², deviance explained, worst regions, the relativity-table blob —
> and the table itself is the approximating Model's `fit_result`, reachable by that id like
> any other Model's.
>
> **Artifacts written before this date carry the table inline and no id, and stay
> readable.** `coefficients` and `relativities` remain on the block as a legacy era, and
> the two are exclusive at the type: an artifact carries a model reference or an inline
> table, never both and never neither. The alternative — dropping the fields — would make
> every artifact written before today fail validation on read, and those artifacts are the
> evidence a Rating Version's approval was granted against (FR-MODEL-36). This is the shape
> `covariance_blob` already has: an absence with a stated meaning rather than a contract
> that pretends the earlier era did not happen.

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
    "perils": [{"peril": "AD", "large_loss_kind": "capped",
                "modelled_burning_cost_minor": 15_000},
               {"peril": "TP_BI", "large_loss_kind": "separate_model",
                "modelled_burning_cost_minor": 2_337},
               {"peril": "WINDSCREEN", "large_loss_kind": "none",
                "modelled_burning_cost_minor": 1_000}],
    "observed_burning_cost_minor": 18_412, "modelled_burning_cost_minor": 18_337,
    "ratio": "0.995927", "tolerance": "0.02", "status": "pass",
    "computed_at": "2026-08-18T09:14:02Z"
  },
  "status": "approved"
}
```

**Six corrections, 2026-08-18 (W5, the peril-structure slice).** §4.10 printed an example
and defined no contract; `peril-structure.schema.json` is generated from the built type, and
building it settled six things the example left open:

- **`ratio` and `status` are derived, never stored.** The example prints both beside the
  numbers they follow from, and two statements of one fact disagree eventually — this one is
  the evidence an approval cites. They are computed from `modelled`, `observed` and the
  declared `tolerance`, and any incoming value for either is **dropped and recomputed**
  rather than refused, so a hand-edited ratio has no way to be believed. (§4.9's `kinds`
  reached the same conclusion and became a plain property; these stay serialised because a
  caller reading a reconciliation should not have to reimplement the rounding rule.)
- **The reconciliation carries a per-peril breakdown**, which is new. It is where
  FR-MODEL-74's treatment is stated beside the number it produced, and the total is checked
  to be the sum of those figures. A total that is not the sum is a third number nobody can
  source. The per-peril figures are rounded to minor units first and the total is their sum
  — rounding both independently drifts by a penny and the invariant would then reject a
  correct reconciliation.
- **Every large-loss treatment but `none` carries its `evidence_blob`**, which is
  FR-MODEL-59's "recorded with its calibration evidence" made structural. A restoration
  loading of 1.043 with nothing behind it asks an approver to accept a number because it is
  written down. `restoration_loading` is refused below 1: restoration puts the capped mean
  back, and below 1 it caps a second time.
- **`evidence_blob` is a `BlobRef` object, not the string `"blob:sha256:…"`** the example
  prints. Every other blob reference in the contract is the object (`01` §4.x,
  `02` §4.9); the string form appears nowhere in `model-schema`.
- **Money is integer minor units and `ratio`/`tolerance` are exact decimals rendered as
  strings** (FR-OVR-7), which the example's bare `0.9959` did not show.
- **A structure has a lifecycle**: `draft → reconciled → review → approved → superseded →
  archived`. `draft → review` is **not** an edge — FR-MODEL-60 makes the reconciliation the
  evidence FR-MODEL-61's approval reads, so a structure reaching an approver without one is
  not a state to refuse later but a state with no edge into it. `VALID_MODEL_TRANSITIONS`
  reached the same shape from the same argument about diagnostics, and `approved → archived`
  is absent here for the same reason it is absent there: an approved structure is a Rating
  Version's referent, and archiving would remove it while naming no replacement.

Submission additionally refuses a reconciliation whose status is `fail`. FR-MODEL-60 makes
reconciling within the declared tolerance part of the coherence check, and the tolerance is
the submitter's own number — a structure that misses it has failed a test it set itself.

### 4.11 `ModelComparison`

*Added 2026-08-17 (W5, the comparison slice).* §5.2 has named `ModelComparison` as a return
type since Phase 0 and **no section defined it** — so this is the shape's first written form
rather than a description of an existing one, and `model-comparison.schema.json` is generated
from it.

```json
{
  "id": "uuid",
  "computed_at": "2026-08-17T15:20:11Z",
  "job_id": "uuid|null",
  "summary": {
    "model_refs": ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"],
    "baseline_ref": "model:motor-ad-frequency@7",
    "split_ref": {"split_artifact_id": "uuid", "train_part": "train", "holdout_part": "test"},
    "holdout_rows": 169_503,
    "metrics": [
      {"metric": "gini_normalised", "weighting": "exposure", "direction": "higher_is_better",
       "values": [{"model_ref": "model:motor-ad-frequency@7", "value": 0.412},
                  {"model_ref": "model:motor-ad-frequency-gbm@2", "value": 0.430}],
       "leader": "model:motor-ad-frequency-gbm@2"},
      {"metric": "ae_overall", "weighting": "exposure",
       "direction": "closer_to_one_is_better",
       "values": [{"model_ref": "model:motor-ad-frequency@7", "value": 1.001},
                  {"model_ref": "model:motor-ad-frequency-gbm@2", "value": 0.994}],
       "leader": "model:motor-ad-frequency@7"},
      {"metric": "rows", "weighting": "exposure", "direction": "not_ordered",
       "values": [{"model_ref": "model:motor-ad-frequency@7", "value": 169503.0},
                  {"model_ref": "model:motor-ad-frequency-gbm@2", "value": 169503.0}],
       "leader": null}
    ],
    "double_lift": [
      {"baseline_ref": "model:motor-ad-frequency@7",
       "challenger_ref": "model:motor-ad-frequency-gbm@2",
       "weighting": "exposure",
       "bins": [{"bin": 1, "rows": 16_950, "actual": 0.0491,
                 "baseline_predicted": 0.0523, "challenger_predicted": 0.0447,
                 "exposure_years": "14203.400000"}]}
    ],
    "relativity_differences": [
      {"factor": "driver_age_banded", "level": "17-20",
       "values": [{"model_ref": "model:motor-ad-frequency@7", "value": 1.718},
                  {"model_ref": "model:motor-ad-frequency-gbm@2", "value": 1.902}],
       "max_abs_difference": 0.184}
    ]
  }
}
```

**Invariants** — `|model_refs| ≥ 2` (FR-MODEL-56 compares *two or more*; one model measured
against nothing is a diagnostics read); `baseline_ref ∈ model_refs`; every metric carries a
value for **every** model, null where the metric does not apply, because a missing model
reads as one that scored nothing rather than one nobody measured; `leader ∈` the metric's own
model refs, and null where the metric does not order **or the models tie** — a winner chosen
by tie-break is one the data did not choose; a `double_lift` series' `baseline_ref` equals the
comparison's, and no series has a model as its own challenger.

**`direction` is part of the metric, not the reader's assumption.** `closer_to_one_is_better`
exists because A/E has no better direction: 1.4 and 0.6 are equally wrong, and every
higher-is-better table would rank 1.4 first.

**The shared holdout is stored, not promised.** `01` FR-DATA-36 records the split on the
parent version precisely so "the same holdout" is one artifact two models cite; keeping the
`SplitRef` here makes the claim checkable by a reader rather than something taken on trust.

**Double-lift bins are ordered by the *ratio* of the two predictions.** Sorting by either
model's prediction gives two lift curves side by side, which answers "does each model order
risk?"; the ratio answers "where they disagree, which one does the data support?" — the
question a selection decision (`wf-01` E2) actually turns on.

**Immutable, and enforced at the privilege layer** (FR-DATA-42): `06` §3.3 makes a comparison
required evidence for a Model approval where a predecessor exists.

### 4.12 `Backtest`

*Added 2026-08-18 (W5, the backtest slice).* FR-MODEL-57 has named the operation since Phase
0 and **no section defined what it produces** — so this is the shape's first written form,
and `backtest.schema.json` is generated from it.

```json
{
  "id": "uuid",
  "model_id": "uuid",
  "dataset_version_id": "uuid",
  "computed_at": "2026-08-18T12:41:07Z",
  "job_id": "uuid|null",
  "summary": {
    "model_ref": "model:motor-ad-frequency@7",
    "dataset_version_ref": "dataset_version:motor-gb-2025h2@4",
    "fitted_on_ref": "dataset_version:motor-gb-2024@1",
    "period_from": "2025-07-01",
    "period_to": "2025-12-31",
    "partition": {
      "weighting": "exposure",
      "rows": 182_447,
      "ae_overall": 1.074,
      "ae_by_factor": [
        {"factor": "driver_age_banded", "level": "17-20", "actual": 0.1912,
         "expected": 0.1655, "ae": 1.155, "ci_95": [1.061, 1.258],
         "exposure_years": "9184.300000"}
      ],
      "lift": [{"bin": 1, "rows": 18_244, "predicted": 0.0421, "actual": 0.0468,
                "exposure_years": "15203.100000"}],
      "gini": 0.301,
      "gini_normalised": 0.398,
      "calibration": [{"bin": 1, "rows": 18_244, "predicted": 0.0421, "actual": 0.0468}]
    }
  }
}
```

**Three shape decisions, each made when this was built rather than transcribed:**

**A backtest is its own artifact, not a field on `Diagnostics`.** `Diagnostics.backtest` was
declared from Phase 0 and typed `null`, and nothing could ever have populated it: FR-MODEL-49
makes diagnostics computed once at fit time and read thereafter, while a backtest runs later —
and again for every subsequent period, which one field on one immutable artifact has no room
for. **That field is removed with this slice**, for the reason
`PartitionDiagnostics.double_lift` was removed before it (FR-MODEL-50, 2026-08-17): a field
that is structurally always null reads as a measurement that came out empty. `cross_validation`
stays: FR-MODEL-53 computes it *at fit time*, so `Diagnostics` is where it will land.

**One `PartitionDiagnostics`, and it is not called a holdout.** FR-MODEL-54's "train and
holdout, side by side" is a statement about a *fit*; a backtest population was never split, so
there is no counterpart being withheld and naming the single partition a holdout would claim a
split nobody made. The fit-time counterpart is not copied in either — it lives on the model's
own diagnostics, which `model_id` reaches, and a second immutable copy of an immutable number
buys only a second thing to keep true.

**The version it was fitted on is stored, not merely differed from.** `fitted_on_ref` is
derivable, and it is stored for the reason §4.11 stores the `split_ref` it verified: the
artifact's defining claim is *this is not the data it learned on*, and an approval or a
monitoring review that cites a backtest should be able to check that claim without
re-deriving it.

**Invariants** — `dataset_version_ref ≠ fitted_on_ref`, refused at the type, because a model
measured on its own training data reports how well it memorised and that number renders
identically to out-of-time performance; `period_from ≤ period_to` where both are present, and
both may be absent because a version need not declare a period.

**The platform refuses more than the type can see.** A split's `train` and `holdout` parts are
themselves Dataset Versions (`01` FR-DATA-36) with ids the contract has never been shown, so
backtesting "the holdout" satisfies every invariant here and reproduces the fit-time holdout
figure under a heading that says later period. `backtests.request_backtest` refuses them, and
**refuses them before `01` §1.3's validated gate** — the parts are derived versions and stay
`draft`, so the gate would otherwise answer "that version is not validated", which is an
instruction to go and validate the holdout, after which the request would be allowed.

**Not one per model.** Unlike `Diagnostics`, a model has as many backtests as periods it has
been measured against; that series is what `05-monitoring.md` reads. Uniqueness is on
`(model_id, dataset_version_id)`: re-running one pair would be a second answer to one
question, with nothing to say which of the two a review cited.

**Immutable, at both layers** (FR-DATA-42) — privileges narrowed to `SELECT, INSERT` *and* the
`artifact_append_only` triggers, because revoking `UPDATE` from the owner does nothing.
Every artifact table in this module now carries both — `diagnostics`, `model_comparisons`,
`transparency_artifacts`, `objective_certificates`, `bandings` and `groupings` had the
privileges and not the row trigger until `e1f2a3b4c5d6` (2026-08-18); `01` FR-DATA-47 has
the measurement and the invariant that now checks it.

### 4.13 `CustomMetric`

```json
{
  "id": "uuid", "slug": "capped-gamma-nll", "version": 2,
  "kind": "template", "template": "capped_gamma",
  "params": {"cap": 250000},
  "applicability": {"responses": ["claim_severity"], "backends": ["xgboost", "lightgbm"],
                    "offset_required": false, "y_domain": {"min_exclusive": 0.0}},
  "direction": "lower_is_better",
  "status": "approved",
  "certificate_id": "uuid", "approval_request_id": "uuid",
  "description": "Gamma NLL with losses capped at 250k, for early stopping on large-loss-heavy severity fits"
}
```

**Invariants.** `template` is required while `kind` is `template`, and Phase 1 admits no
other kind (FR-MODEL-75's rule, applied to metrics). `params` must be exactly the named
template's own parameters — an unknown key is refused rather than ignored, because a
misspelled `cap` that is silently dropped produces an uncapped metric under a name that
says capped. A status past `draft` requires a `certificate_id` (FR-MODEL-105). `direction`
has no default (FR-MODEL-104). `applicability` must be no wider than §4.5's own applicability
for `template` — an author may narrow it further, never extend it, because widening claims
the analytic loss is valid somewhere `pricing-core` never established for it (FR-MODEL-103).

**Why the shape is not `CustomObjective`'s.** No `hessian_strategy`, no `hessian_min`: both
describe what happens where the curvature is negative, and a metric is never
differentiated. `Applicability`, `ObjectiveTemplate`, `TemplateParameter` and `YDomain` are
imported from §4.5 rather than restated — the same catalogue, read two ways.

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/factors` | Create/version a Factor (FR-MODEL-1) |
| `GET` | `/api/v1/factors?dataset={slug}` | List factors with intent, monotonic direction, prohibited flag |
| `POST` | `/api/v1/bandings/propose` | Propose boundaries by method against a dataset version (FR-MODEL-9) |
| `POST` | `/api/v1/bandings/evaluate` | Recompute band statistics for **edited** boundaries, persisting nothing (FR-MODEL-83) |
| `POST` | `/api/v1/bandings` | **201** Persist a Banding (with editable boundaries) |
| `GET` | `/api/v1/bandings?dataset_id=` | List bandings, latest version first |
| `POST` | `/api/v1/groupings/propose` | Propose a grouping by method (FR-MODEL-14) |
| `POST` | `/api/v1/groupings/evaluate` | Recompute the deviance/df evidence for an **edited** mapping (FR-MODEL-83) |
| `POST` | `/api/v1/groupings` | **201** Persist a Grouping |
| `GET` | `/api/v1/groupings?dataset_id=` | List groupings, latest version first |
| `POST` | `/api/v1/model-specs/validate` | **200** with `SpecValidation` — `ok` plus every problem, never only the first. A spec that merely cannot be fitted is not a bad *request*, so it is not a 4xx; a spec naming a version that does not exist is a 404 (FR-MODEL-44, FR-MODEL-81) |
| `POST` | `/api/v1/models` | **202** Fit → Job; returns existing model on `spec_hash` match (FR-MODEL-66) |
| `GET` | `/api/v1/models/{slug}?version=` | Model artifact — latest, or a named version |
| `GET` | `/api/v1/models/{id}/diagnostics` | Diagnostics artifact |
| `POST` | `/api/v1/models/{id}/transparency` | **202** Build a transparency artifact (FR-MODEL-33) |
| `GET` | `/api/v1/models/{id}/transparency` | The model's most recent artifact (FR-MODEL-84) |
| `POST` | `/api/v1/models/{id}/backtest` | **202** Backtest against another dataset version (FR-MODEL-57) |
| `GET` | `/api/v1/models/backtests/{id}` | The stored backtest artifact (§4.12, FR-MODEL-92) |
| `POST` | `/api/v1/models/compare` | **202** Comparison artifact for 2+ models on a shared holdout (FR-MODEL-56) |
| `GET` | `/api/v1/models/comparisons/{id}` | The stored comparison artifact (§4.11) |
| `POST` | `/api/v1/models/{id}/predict` | **200** Score rows with FR-MODEL-63's uncertainty (dev/debug scale, row-capped; production scoring is `03`) |
| `POST` | `/api/v1/models/{id}/submit` | Submit for approval (`06`) — `fitted → review`, `If-Match` required |
| `POST` | `/api/v1/models/{id}/archive` | `draft \| fitted \| superseded → archived` (FR-MODEL-64), `If-Match` required |
| `POST` | `/api/v1/custom-objectives` | **201** Create → `draft` (FR-MODEL-38) |
| `GET` | `/api/v1/custom-objectives/{id}` | The objective, its status and its certificate outcome (FR-MODEL-95) |
| `POST` | `/api/v1/custom-objectives/{id}/derive` | Symbolically derive gradient/hessian from `loss` (FR-MODEL-40) — Phase 2, refused with `OBJECTIVE_KIND_NOT_ENABLED` (FR-MODEL-75) |
| `POST` | `/api/v1/custom-objectives/{id}/certify` | **202** Run the certificate checks (FR-MODEL-42) |
| `GET` | `/api/v1/custom-objectives/{id}/certificate` | The latest `ObjectiveCertificate` for that version (FR-MODEL-95) |
| `POST` | `/api/v1/custom-objectives/{id}/submit` | Submit for approval (FR-MODEL-46) |
| `GET` | `/api/v1/custom-objectives/{id}/usage` | Blast radius: models, rating versions, deployments (FR-MODEL-47) |
| `POST` | `/api/v1/custom-metrics` | **201** Create → `draft` (FR-MODEL-45, FR-MODEL-103) |
| `GET` | `/api/v1/custom-metrics/{id}` | The metric, its status and its certificate outcome (FR-MODEL-108) |
| `POST` | `/api/v1/custom-metrics/{id}/certify` | **202** Run §4.7's metric checks (FR-MODEL-105) |
| `GET` | `/api/v1/custom-metrics/{id}/certificate` | The latest `MetricCertificate` for that version (FR-MODEL-108) |
| `POST` | `/api/v1/custom-metrics/{id}/submit` | Submit for approval (FR-MODEL-45's lifecycle) |
| `GET` | `/api/v1/custom-metrics/{id}/usage` | Blast radius: models using this metric version (FR-MODEL-108) |
| `POST` | `/api/v1/peril-structures` | **201** Create/version a Peril Structure (FR-MODEL-58) |
| `GET` | `/api/v1/peril-structures/{id}` | The structure and its reconciliation (FR-MODEL-90) |
| `POST` | `/api/v1/peril-structures/{id}/reconcile` | **202** Recompute reconciliation (FR-MODEL-60) |
| `POST` | `/api/v1/peril-structures/{id}/submit` | Submit for approval, `reconciled → review` (FR-MODEL-90) |

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

> **Amended 2026-08-15 (W5, bandings and groupings).** The four banding and grouping routes
> are now built, plus two the table did not declare:
>
> * `GET /api/v1/bandings?dataset_id=` and `GET /api/v1/groupings?dataset_id=` — **added to
>   the table above.** The factor workbench (§5.3) has to list what already exists before it
>   can offer to reuse one, and a surface that can only create is one every screen works
>   around. This is the omission `01`'s reference lifecycle made in the other direction: an
>   endpoint present in neither the spec nor the contract is invisible to the endpoint audit.
> * `POST /bandings` and `POST /groupings` answer **201**, not 200. They allocate a version
>   (FR-MODEL-12), which is a creation whatever the slug already was.
>
> Still declared and unbuilt after this slice: spec validation, diagnostics, transparency,
> backtests, comparison, prediction, custom objectives, metrics and peril structures.

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
>   **Closed 2026-08-15 (W5):** `fit_glm` takes `progress` again and reports six stages;
>   `pricing_core.ScaledProgress` gives the handler a window to place them in, so the core
>   reports its own `0..1` without knowing it is the middle of something.
>
> `02` §4's field sets (§4.1, §4.4, §4.8) still declare more than the spine implements —
> `split_ref`, `loss_treatment`, `diagnostics_id` and others. That is a **larger divergence
> awaiting a decision**, not an oversight: whether the spine grows to meet §4 or §4 narrows
> to a staged contract is a design choice, recorded in `docs/open-questions.md` as
> OQ-MODEL-8 rather than settled here. *(Decided 2026-08-17 — the staged contract, as
> FR-MODEL-87. All four fields named in this paragraph are now live.)*
>
> **Narrowed 2026-08-15 (W5):** §4.1's `banding_id` and `grouping_id` are now live fields
> on `Factor`, because their slice landed — which is what OQ-MODEL-8's recommendation
> ("re-widen it as the slices land") describes. `expression` remains declared and unbuilt,
> and FR-MODEL-88 states its verdict: selectable, unresolvable, and refused by name.
> The `spec_hash` precondition the same question named is delivered: the digest now reads
> `v1:sha256:…` and `spec_hash_is_current` answers whether a stored one is still matchable.

> **Amended 2026-08-17 (W5, the comparison slice).** `POST /models/compare` is built, and one
> route is **added to the table above**:
>
> * `GET /api/v1/models/comparisons/{id}` — the table declared the `POST` and no read. A 202
>   whose artifact nothing can fetch is complete to the endpoint audit and unusable to a
>   caller; `01`'s reference publish lifecycle made the same omission from the other side.
>
> And **§5.2's `compare_models` signature is corrected — the third instance of one defect.**
> It was declared `compare_models(models: Sequence[Model], holdout)`, which cannot be written:
> a `Model` carries *references* — factor ids, banding ids, a dataset version — and resolving
> one needs a database that ADR-0001 forbids `pricing-core`. `predict_glm` and
> `compute_diagnostics` were corrected the same way on 2026-08-16. It now takes
> `ComparisonCandidate`s, which are that resolution, and returns a `ComparisonSummary` — the
> identity-free body of §4.11's artifact, because `pricing-core` allocates no ids and reads no
> clock. The pattern is `compute_diagnostics` → `DiagnosticsResult`, deliberately.
>
> Two other decisions the building settled:
>
> * **The comparison recomputes its metrics on the shared holdout** rather than reading each
>   model's stored diagnostics. Two models' diagnostics came from two Jobs; the point of a
>   comparison is that every figure in the table came from the same rows in the same run, an
>   alignment nothing downstream can verify once the numbers are copied out of two artifacts.
> * **Candidates must agree on their weighting scheme** (FR-MODEL-55), refused with
>   `MODELS_NOT_COMPARABLE`. An exposure-weighted A/E beside a claim-count-weighted one is two
>   quantities in one column. A frequency model and a severity model are not rivals.
>
> Still declared and unbuilt after this slice: transparency, backtests, prediction, custom
> objectives, metrics and peril structures.

> **Amended 2026-08-17 (W5, the model lifecycle).** `POST /models/{id}/submit` is built, and
> one route is **added to the table above**:
>
> * `POST /api/v1/models/{id}/archive` — FR-MODEL-64 names `archived` and no endpoint reached
>   it. Leaving one state of a six-state machine unreachable is how a partial machine gets
>   recorded as complete, and an endpoint present in neither the spec nor the contract is
>   invisible to the endpoint audit — the omission `01`'s reference lifecycle made.
>
> Three decisions the building settled, recorded here rather than left in the code:
>
> * **Both lifecycle routes take `{id}`, not `{slug}?version=`.** Every *read* route in this
>   module defaults the version to the latest, which the 2026-08-15 amendment above made
>   deliberate. For a **mutation** that default is the race `If-Match` exists to catch:
>   "submit the latest" resolves its own target below the precondition. The spec's original
>   `{id}` is therefore kept, against the module's own read convention.
> * **`If-Match` is required on both** (`00` §5.4, FR-PLAT-47), and what it guards is stated
>   rather than assumed: a precondition on the **caller's view**, not a lost update to a
>   field — `02` R2 makes a Model's numbers immutable and the transition table already
>   refuses every unsafe move under a row lock. Its contribution is that a stale client is
>   told "what you read is stale" instead of "your transition is invalid", which are the same
>   409 and only one of them is actionable. W4 deferred the header for being the second kind
>   of guard; that reading was right about the mechanism and wrong about the value.
> * **A submission returns 200, not 202.** No Job is queued: the transition, the approval
>   request and the audit events are one transaction. `POST /models` answers 202 because a
>   fit is work; a submission is a decision that has already completed by the time the
>   response is written.
>
> Still declared and unbuilt after this slice: transparency, backtests, comparison,
> prediction, custom objectives, metrics and peril structures.

> **Amended 2026-08-17 (W5, the GBM arm).** No route is added or removed. `POST /models`
> and `POST /model-specs/validate` now take **either arm** of §4.4's union, and one Job kind
> fits both — a second `model.gbm_fit` would have made every caller, status screen and
> audit query ask which of two names to look for.
>
> Two things the building settled, neither of which the table could state:
>
> * **FR-MODEL-44's *objective applicability* half is now built for the GBM arm.**
>   `SpecProblemKind` gains `objective_unsupported`, and a spec naming an objective outside
>   FR-MODEL-26's set — or a Custom Objective while FR-MODEL-38 is unbuilt — comes back as a
>   **200 with `ok: false`** rather than a queued Job that fails three minutes later. The set
>   is exported from `pricing-core` and read by both the validator and the fit, because two
>   hand-written lists would eventually disagree about what the platform supports.
> * **`Diagnostics.gbm` is populated (FR-MODEL-52), and the evaluation curve lives there.**
>   The code briefly put the curve on `GbmFitResult`; `diagnostics.schema.json` has had it
>   under `gbm` since Phase 0 and FR-MODEL-52 calls it a diagnostic asking for **train and
>   holdout**, which is FR-MODEL-54's shape. The **code was wrong and moved**. Only
>   `best_iteration` stays on the fit result, because scoring needs it and diagnostics are
>   not loaded to score.
>
> A GBM's `ComplexityDiagnostic.parameter_count` is its **leaf count** (FR-MODEL-81). A
> boosted model has no coefficient vector, and counting factors would report a stump and a
> thousand deep trees as equally complex — the comparison exposure-per-parameter exists to
> make. The *pre-fit* estimate in `POST /model-specs/validate` remains the factor-level
> proxy, which for a GBM is a bound rather than an estimate; it is already documented as
> deliberately conservative, and it only gates where a workspace sets a limit.

> **Amended 2026-08-18 (W5, the backtest slice).** `POST /models/{id}/backtest` is built, and
> one route is **added to the table above**:
>
> * `GET /api/v1/models/backtests/{id}` — FR-MODEL-92. The table declared the `POST` and no
>   read, the fourth artifact in this module to need the repair. An endpoint missing from
>   both the spec and the contract is invisible to the endpoint audit, which is why the
>   surface kept reading complete.
>
> Three decisions the building settled, recorded here rather than left in the code:
>
> * **`backtest_model` lives in `diagnostics.py` and reuses `_partition`.** FR-MODEL-57's
>   "the same diagnostic shapes" is only true if it is the same arithmetic; a second
>   implementation that agreed today would drift. The test that proves it is the degenerate
>   one — backtest a model against its own training frame and every figure equals the fit's
>   train partition.
> * **The refusals are ordered, and the order is load-bearing.** The definitional refusal
>   runs before `01` §1.3's validated gate, because a split's parts are derived versions that
>   stay `draft`: the gate would answer a request to backtest the holdout with "that version
>   is not validated", which is an instruction to go and validate it, after which the request
>   would be allowed. Found by a test that expected the other message.
> * **A missing column is refused from the version's declared `arrow_schema`**, not
>   discovered inside `resolve_factors` twenty seconds later. A later period that renamed a
>   field is the ordinary way a backtest fails, and `request_comparison` set both the
>   precedent and the reason.
>
> Still declared and unbuilt after this slice: prediction, custom objectives and custom
> metrics.

**Error codes owned by this module:** `DATASET_NOT_VALIDATED` (re-raised from `01`),
`FACTOR_PROHIBITED`, `FACTOR_RESOLUTION_FAILED`, `BAND_EMPTY`, `BAND_BELOW_MIN_EXPOSURE`,
`GROUPING_NOT_EXHAUSTIVE`, `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`, `GLM_CV_FOLD_EMPTY`,
`GLM_TWEEDIE_POWER_GRID_EDGE`, `GLM_DID_NOT_CONVERGE`, `GLM_RANK_DEFICIENT`,
`GLM_SEPARATION_DETECTED`,
`OFFSET_REQUIRED_FOR_FREQUENCY`,
`MONOTONE_CONSTRAINT_CONFLICT`, `EARLY_STOPPING_REQUIRES_HOLDOUT`,
`OBJECTIVE_NOT_APPROVED`, `OBJECTIVE_NOT_APPLICABLE`, `OBJECTIVE_NOT_CERTIFIED`,
`OBJECTIVE_KIND_NOT_ENABLED`, `MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT`,
`OBJECTIVE_GRAMMAR_VIOLATION`, `OBJECTIVE_NONFINITE_DERIVATIVE`,
`TRANSPARENCY_ARTIFACT_REQUIRED`, `MODEL_IMMUTABLE`, `PICKLE_PERSISTENCE_REFUSED`,
`PERIL_STRUCTURE_RECONCILIATION_FAILED`, `MODELS_NOT_COMPARABLE`,
`OFFSET_NOT_RECONSTRUCTABLE`, `GBM_NO_FEATURES`, `SCORING_FEATURES_MISMATCH`,
`INTERACTION_FEATURE_UNKNOWN`, `LOSS_TREATMENT_UNIMPLEMENTED`, `MODEL_NOT_FITTED`,
`MODEL_ALREADY_TRANSPARENT`, `MODEL_TYPE_UNSUPPORTED`, `APPROXIMATION_TARGET_NOT_POSITIVE`,
`SHAP_SAMPLE_EMPTY`, `OBJECTIVE_NOT_SUPPLIED`, `OBJECTIVE_REF_MISMATCH`,
`OBJECTIVE_RESPONSE_UNDECLARED`, `OBJECTIVE_REQUIRES_OFFSET`,
`OBJECTIVE_EARLY_STOPPING_UNSUPPORTED`, `OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED`,
`MODEL_TERM_UNRESOLVED`, `MODEL_LINK_UNSUPPORTED`, `MODEL_OFFSET_MISSING`,
`MODEL_OFFSET_REF_INVALID`,
`MODEL_INTERVAL_UNAVAILABLE`, `MODEL_INTERVAL_PAIR_INVALID`, `MODEL_APPROXIMATION_INVALID`,
`METRIC_REF_UNRESOLVED`, `METRIC_NOT_APPLICABLE`, `METRIC_NOT_FITTABLE`.

> **`MODEL_INTERVAL_PAIR_INVALID` added 2026-08-19 (W5, the paired-quantile slice).**
> It refuses a quantile bound whose spec disagrees with the Model its `interval_for`
> names — a different dataset version, split or factor set — or a second bound on a
> side that already has one (FR-MODEL-78, FR-MODEL-100). Its own code rather than
> `VALIDATION_FAILED` because the request is well formed and the model is real: what
> fails is the pairing of the two, and an interval fitted on a different design
> renders identically to a correct one.

> **`MODEL_APPROXIMATION_INVALID` added 2026-08-19 (W5, FR-MODEL-96).** It refuses a spec
> whose `approximates_model_id` names a Model the surrogate cannot be an approximation of —
> one that is not fitted, one that is itself a GLM (FR-MODEL-33 applies to non-GLM models,
> and a GLM approximating a GLM reports 100 % fidelity that looks like evidence), or one
> whose dataset version, split or factor set disagrees with the surrogate's. Its own code
> rather than `VALIDATION_FAILED` for `MODEL_INTERVAL_PAIR_INVALID`'s reason: the request is
> well formed and both models are real, and what fails is the relation between them. The
> three fields compared — `dataset_version_id`, `split_ref`, `factors` — are the
> design-matrix identity and are deliberately not all six `approximation_spec` (`02` §5.2)
> copies from the source: `offset`, `weight` and `seed` are copied by the platform's own
> builder but never compared, so a hand-written surrogate spec differing from its source
> only in one of those three is accepted today.

> **`MODEL_OFFSET_REF_INVALID` added 2026-08-21 (W5, the offset-from-another-model slice).**
> It refuses a spec whose `offset_model_ref` names a model that cannot serve as the
> offset — not a model at all, not fitted, not a GLM, or fitted with a link that is not
> the new spec's (FR-MODEL-24). Its own code rather than `NOT_FOUND` because the request
> is well formed: what fails is what the ref names.

> **Added 2026-08-17 (W5, the GBM and transparency slices).** The ten codes above are new;
> five *existing* ones are now raised for the first time by the GBM path rather than being
> given parallel names — `MONOTONE_CONSTRAINT_CONFLICT`, `EARLY_STOPPING_REQUIRES_HOLDOUT`,
> `OBJECTIVE_NOT_APPLICABLE`, `OBJECTIVE_NOT_APPROVED` and
> `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`. A second spelling for a refusal already named is how a
> screen ends up branching on one and not the other.
>
> `OFFSET_NOT_RECONSTRUCTABLE` is the one that earns its own code rather than joining
> `SCORING_FEATURES_MISMATCH`: FR-MODEL-71 exists because omitting the offset at scoring
> time fails *silently* on both backends, so "this frame cannot rebuild the offset" must be
> distinguishable from "this frame is missing a column" by anything reading the code.

> **Added 2026-08-18 (W5, custom objectives).** Six `OBJECTIVE_*` codes arrive with the
> path that raises them. Each one is a *refusal to fit*, and they are separate codes rather
> than one because the workbench branches on them differently: `OBJECTIVE_NOT_SUPPLIED` and
> `OBJECTIVE_REF_MISMATCH` are the caller's wiring (ADR-0001 — `pricing-core` is handed the
> artifact and never resolves a reference, so "you named one and passed none" is not the
> same fault as "you passed a different one"); `OBJECTIVE_RESPONSE_UNDECLARED` and
> `OBJECTIVE_REQUIRES_OFFSET` are FR-MODEL-44's applicability, refused before any boosting
> round; `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` is the honest edge of what is built, since a
> custom eval metric is FR-MODEL-45 and deferred; `OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED`
> is FR-MODEL-43 meeting a template with no Gauss-Newton form to drop a term from.
>
> **And four codes that were live and unregistered.** `MODEL_TERM_UNRESOLVED`,
> `MODEL_LINK_UNSUPPORTED`, `MODEL_OFFSET_MISSING` and `MODEL_INTERVAL_UNAVAILABLE` have
> been raised by `predict.py` since the prediction slice and mapped straight into a
> `PlatformError` by `_unscoreable` — which refuses a code it does not know, so each was a
> `ValueError: unknown error code` waiting inside the error path. The repository invariant
> written to make exactly this impossible could not see them: it scanned for a **hand-listed
> set of exception names**, and neither `PredictionError` nor `ObjectiveError` was on it. The
> list is now derived from the classes `pricing_core.modelling` actually defines, which is
> the only version of that check that stays true as the module grows.
>
> **Added 2026-08-21 (W5):** FR-MODEL-24 also raises it when a `kind="model"` spec reaches
> fit or scoring without the resolved offset array.

An **invalid lifecycle transition** (FR-MODEL-64) is `VALIDATION_FAILED` at `409`, not a code
of its own — the same answer `01` gives for a Dataset Version's transitions, and for the same
reason: the request was well formed, the artifact's state is what makes it impossible, and a
caller branching on the code should not have to tell a malformed body from a stale view of a
lifecycle. `EVIDENCE_INCOMPLETE` and `ARTIFACT_FLAGGED` are `06`'s and are raised from this
module's submission and approval paths (FR-GOV-19 R4, FR-MODEL-67).

> **Amended 2026-08-18 (W5, the custom-objectives slice).** Five of the six
> `custom-objectives` routes are built, and **two are added to the table above** —
> `GET /custom-objectives/{id}` and `GET /custom-objectives/{id}/certificate`, under
> FR-MODEL-95. The fifth artifact in this module to declare its writes and no read, and the
> sharpest case of it: certification is a **202**, so without the read there was no way to
> learn its verdict, and FR-MODEL-46 puts an Approver in front of a certificate they could
> not fetch.
>
> Three further corrections to the rows themselves:
>
> * **`POST /custom-objectives` answers 201**, not 200 — it allocates a version.
> * **`POST /custom-objectives/{id}/derive` is refused for the whole of Phase 1**, with
>   `OBJECTIVE_KIND_NOT_ENABLED`. It is the `expression` path, and FR-MODEL-75 gates it
>   behind `expression_objectives_enabled`, off by default. The route exists and answers
>   `422` with that code rather than `404`, so a caller learns the capability is not enabled
>   rather than that the platform has never heard of it.
> * ~~**`POST /custom-metrics` (FR-MODEL-45) is not built, and is deferred to Phase 1b with
>   this slice.**~~ **Built 2026-08-19.** The reasoning below held exactly as written — a
>   custom metric does not gate the fitting path — and it stopped holding when early
>   stopping under a custom objective turned out to need one (FR-MODEL-107). A custom
>   *metric* is `feval` — it changes what early stopping optimises
>   and what the diagnostics report, not what the model fits, so it does not gate the
>   fitting path this slice exists to open. It shares the objective's lifecycle,
>   certification and approval machinery, which is now built and is what it was waiting for.
>   Stated here rather than left silent: an endpoint declared and not built reads as
>   delivered to anyone auditing the table.

> **Amended 2026-08-19 (W5, the custom-metrics slice).** Three `METRIC_*` codes arrive
> with the Custom Metric endpoints (FR-MODEL-108). `METRIC_REF_UNRESOLVED` is
> `resolve_ref`'s refusal — a `custom_metric:<slug>@<version>` reference that names no
> row in the workspace — kept distinct from the generic `NOT_FOUND` the objectives'
> `resolve_ref` still raises, because a caller resolving a reference embedded in a
> `GbmSpec.eval_metrics` entry needs to tell "this reference is malformed or stale"
> from "this id does not exist", and the two paths that call `resolve_ref` are not the
> same failure mode. `METRIC_NOT_APPLICABLE` and `METRIC_NOT_FITTABLE` are declared here
> ahead of the code that raises them: they belong to FR-MODEL-106's refusals from the
> GBM fit path once `eval_metrics` is wired in, and registering them with this slice
> — the one that owns the artifact — means that slice finds them already known rather
> than repeating the `MODEL_TERM_UNRESOLVED` history two sections above, where four
> codes were live and unregistered because nothing declared them when they were added.

> **`GLM_CV_FOLD_EMPTY` added 2026-08-21 (the regularisation-and-CV slice).** Raised by
> the CV path when a fold has no held-out rows (or no training rows) at some alpha on
> the scanned path (FR-MODEL-20, FR-MODEL-53) — the `key_column`/`time_column` skew
> that a fold count chosen against the whole book does not guarantee against, per fold.
> A fold cannot be scored, or trained, on nothing.

> **`GLM_TWEEDIE_POWER_GRID_EDGE` added 2026-08-21 (FR-MODEL-22).** Raised by the
> profile-likelihood path when the profile over `tweedie.p_grid` is maximised at a scan
> edge: the scan found no interior maximum, so the estimate would report the scan's
> boundary as the answer. Widen the grid towards the maximum, or reconsider the model.

> **Corrected 2026-08-21 (the regularisation-and-CV slice).** `fit_glm`'s return comment
> below now reads `.result, .covariance_bytes, .cv` — the slice added the `cv` field to
> `GlmFit` (glm.py's dataclass, FR-MODEL-20/FR-MODEL-53) and the interface comment lagged
> it, so a caller copying the signature would have missed the cross-validation
> diagnostics the fit carries when `spec.select_by == "cv"`.

### 5.2 `pricing-core` interfaces

```python
# pricing_core/modelling/factors.py
def resolve_factors(df: pl.DataFrame, factors: Sequence[Factor], *,
                    bandings: Mapping[UUID, Banding] | None = None,
                    groupings: Mapping[UUID, Grouping] | None = None) -> FactorMatrix

# pricing_core/modelling/bandings.py
def propose_banding(df: pl.DataFrame, proposal: BandingProposal, *,
                    dataset_id: UUID, slug: str) -> Banding
def apply_banding(series: pl.Series, banding: Banding) -> pl.Series
def check_banding(df: pl.DataFrame, banding: Banding, *, min_exposure: float = 0.0,
                  min_claims: float = 0.0, fail_on_thin: bool = False) -> tuple[str, ...]

# pricing_core/modelling/groupings.py
def propose_grouping(df: pl.DataFrame, proposal: GroupingProposal, *,
                     dataset_id: UUID, slug: str) -> Grouping
def apply_grouping(series: pl.Series, grouping: Grouping) -> pl.Series
def grouping_evidence(df: pl.DataFrame, mapping: dict[str, str], *,
                      column: str) -> GroupingEvidence

# pricing_core/modelling/glm.py
def fit_glm(data: pl.DataFrame, spec: GlmSpec, factors: Sequence[Factor], *,
            seed: int = 0,
            bandings: Mapping[UUID, Banding] | None = None,
            groupings: Mapping[UUID, Grouping] | None = None,
            progress: ProgressCallback | None = None) -> GlmFit   # .result, .covariance_bytes, .cv

# pricing_core/modelling/predict.py
def linear_predictor(fit: GlmFitResult, data: pl.DataFrame, factors: Sequence[Factor],
                     spec: GlmSpec, *,
                     bandings: Mapping[UUID, Banding] | None = None,
                     groupings: Mapping[UUID, Grouping] | None = None) -> NDArray[float64]
def predict_glm(fit: GlmFitResult, data: pl.DataFrame, factors: Sequence[Factor],
                spec: GlmSpec, *,
                bandings: Mapping[UUID, Banding] | None = None,
                groupings: Mapping[UUID, Grouping] | None = None) -> NDArray[float64]
def predict_glm_interval(fit: GlmFitResult, data: pl.DataFrame, factors: Sequence[Factor],
                         spec: GlmSpec, *, covariance_bytes: bytes, level: float = 0.95,
                         bandings: Mapping[UUID, Banding] | None = None,
                         groupings: Mapping[UUID, Grouping] | None = None
                         ) -> tuple[NDArray[float64], NDArray[float64], NDArray[float64]]

# pricing_core/modelling/glm.py — the covariance blob's own codec
def encode_covariance(terms: Sequence[str], matrix: NDArray[float64]) -> bytes
def decode_covariance(payload: bytes, terms: Sequence[str]) -> NDArray[float64]

# pricing_core/modelling/gbm.py
def fit_gbm(data: pl.DataFrame, spec: GbmSpec, factors: Sequence[Factor], *,
            holdout: pl.DataFrame | None = None,
            objective: CustomObjective | None = None,
            bandings: Mapping[UUID, Banding] | None = None,
            groupings: Mapping[UUID, Grouping] | None = None,
            progress: ProgressCallback | None = None) -> GbmFit   # .result, .booster_bytes
def predict_gbm(result: GbmFitResult, booster: bytes, data: pl.DataFrame,
                factors: Sequence[Factor] = (), *,
                bandings: Mapping[UUID, Banding] | None = None,
                groupings: Mapping[UUID, Grouping] | None = None) -> pl.Series
def apply_loss_treatment(response: NDArray[float64], treatment: LossTreatment
                         ) -> NDArray[float64]

# pricing_core/modelling/objectives.py
def parse_expression(text: str, bound: Sequence[str], params: Sequence[Parameter]) -> ExprTree
def derive_derivatives(loss: ExprTree, wrt: str = "f") -> tuple[ExprTree, ExprTree]
def compile_objective(obj: CustomObjective) -> ObjectiveFns
    # .loss/.grad/.hess(y,f,w), .stabilise(y,f,w), .inverse_link
def certify_objective(obj: CustomObjective, *, sampling: SamplingSpec,
                      progress: ProgressCallback | None = None) -> CertificateResult
def make_xgb_objective(fns: ObjectiveFns) -> Callable[[NDArray[float64], xgb.DMatrix],
                                                      tuple[NDArray[float64], NDArray[float64]]]
def make_lgb_objective(fns: ObjectiveFns) -> Callable[[NDArray[float64], lgb.Dataset],
                                                      tuple[NDArray[float64], NDArray[float64]]]

# pricing_core/modelling/diagnostics.py
def compute_diagnostics(fit: GlmFitResult, spec: GlmSpec, factors: Sequence[Factor], *,
                        train: pl.DataFrame, holdout: pl.DataFrame,
                        bandings: Mapping[UUID, Banding] | None = None,
                        groupings: Mapping[UUID, Grouping] | None = None,
                        max_factor_count: int | None = None,
                        min_exposure_per_parameter: float | None = None,
                        type_iii: bool = True,
                        progress: ProgressCallback | None = None) -> DiagnosticsResult
def unit_deviance(y, mu, *, family: str, power: float = 1.5) -> NDArray[float64]
def deviance(y, mu, *, family: str, power: float = 1.5, weights=None) -> float
def compare_models(candidates: Sequence[ComparisonCandidate], holdout: pl.DataFrame, *,
                   baseline: str | None = None) -> ComparisonSummary

def backtest_model(fit: FitResult, spec: ModelSpec, factors: Sequence[Factor],
                   data: pl.DataFrame, *, model_ref: str, dataset_version_ref: str,
                   fitted_on_ref: str, period_from: date | None = None,
                   period_to: date | None = None, booster: bytes | None = None,
                   bandings=None, groupings=None,
                   progress: ProgressCallback | None = None) -> BacktestSummary

# pricing_core/modelling/transparency.py
def approximation_spec(spec: GbmSpec, *, source_model_id: UUID) -> GlmSpec
def build_glm_approximation(result: GbmFitResult, booster: bytes, spec: GbmSpec,
                            factors: Sequence[Factor], data: pl.DataFrame, *,
                            holdout: pl.DataFrame, source_model_id: UUID,
                            bandings=None, groupings=None,
                            progress: ProgressCallback | None = None
                            ) -> GlmApproximationFit
def build_shap_summary(result: GbmFitResult, booster: bytes, spec: GbmSpec,
                       factors: Sequence[Factor], data: pl.DataFrame, *, sample: int,
                       bandings=None, groupings=None,
                       progress: ProgressCallback | None = None) -> ShapSummary

# pricing_core/modelling/perils.py
def assemble_risk_premium(predictions: Sequence[PerilPrediction]) -> pl.DataFrame
def reconcile(assembled: pl.DataFrame, *, observed: NDArray[float64],
              exposure: NDArray[float64], tolerance: Decimal,
              treatments: Mapping[str, LargeLossKind]) -> ReconciliationResult
```

> **Both corrected 2026-08-19 (W5, FR-MODEL-96)** — the correction the 2026-08-16 note
> predicted for every function declared as taking a `Model`. `build_shap_summary` had
> already been built to this shape and the spec had not caught up; `build_glm_approximation`
> additionally returns `GlmApproximationFit`, because the fitted surrogate is now persisted
> as a Model and a function that returned only its summary threw away the artifact.

> **Two signatures corrected, 2026-08-16 (W5, diagnostics).** `predict_glm` and
> `compute_diagnostics` were declared taking a `Model`. They cannot: a `Model` carries
> *references* — factor ids, banding ids, a dataset version — and resolving one needs a
> database, which ADR-0001 forbids this package. This is the same correction already
> recorded for `fit_glm`, and it was always going to recur for every function the spec
> declared the same way; `compare_models`, `build_glm_approximation`, `build_shap_summary`
> and `predict_gbm` still carry it and will need it when their slices land.
>
> `predict_glm` returns the expectation as an array rather than a `DataFrame`, and takes no
> `with_interval`: FR-MODEL-63's interval comes from the covariance matrix, which the fit
> stores as a blob this signature does not receive. A half-interval derived from the
> coefficient standard errors alone would read as a prediction interval and not be one,
> so the parameter is absent until the slice that can honour it.
>
> > **That slice landed 2026-08-18, and the deferred parameter is a second function rather
> > than a flag.** `predict_glm_interval` takes the `covariance_bytes` the caller fetched
> > (ADR-0001 keeps the blob store out of this package) and returns
> > `(expected, lower, upper)`. Two entry points, not one with a flag, because they have
> > genuinely different costs: `predict_glm` accumulates the linear predictor one term at a
> > time and never holds a design matrix, while `x'Vx` needs the whole `n x p` design at
> > once — 542 MB on the 678k-row book the backtest path scores, which is why that path
> > must keep the streaming version and why `/predict` is row-capped. The standard-error
> > shortcut the note refuses is still refused, and now demonstrably wrong rather than
> > merely suspect: `test_the_off_diagonal_terms_change_the_interval_materially` fits a
> > model whose diagonal-only interval is *narrower* than the truth, so the shortcut does
> > not even err on the safe side.
> >
> > `fit_glm` returns `GlmFit` — `.result` plus `.covariance_bytes` — the same split
> > `fit_gbm` already made for the booster, and for the same ADR-0001 reason: `pricing-core`
> > computes the digest and the caller stores the bytes.
>
> `compute_diagnostics` returns `DiagnosticsResult` — the computed numbers — rather than
> the persisted `Diagnostics` artifact, which carries an id, a `model_id` and a
> `computed_at` that only the platform can supply.

> **Corrected again, 2026-08-17 (W5, the GBM arm).** `predict_gbm` was the third instance
> of the same defect, and it is now the third one fixed: it took a `Model`, whose
> references need a database ADR-0001 forbids this package. It takes the `GbmFitResult` and
> the booster **bytes**.
>
> Three further departures from the declared signature, each forced by something the
> declaration did not know:
>
> * **`fit_gbm` returns a `GbmFit`, not a `GbmFitResult`.** The artifact holds a `BlobRef`
>   to the booster (FR-MODEL-31) and this package cannot store a blob (ADR-0001). Content
>   addressing resolves it: the digest is a pure function of the payload, so `fit_gbm`
>   computes the complete reference and hands back the bytes for the caller to store. A
>   caller that forgets has a reference resolving to nothing, rather than a model that half
>   exists.
> * **`factors` is a parameter, as it is on `fit_glm`.** Same reason, same correction.
> * **`holdout` is a parameter.** FR-MODEL-30's early stopping needs the rows, and
>   `split_ref` names them without carrying them. Passing none while declaring a holdout is
>   refused: both backends fall back to the training set, which is the requirement's
>   prohibition arrived at by omission.
>
> `apply_loss_treatment` is new and was declared nowhere — FR-MODEL-73's cap is applied to
> the response at fit time, and it belongs beside the fit rather than inside it, because
> the GLM path will need the same function.
>
> > **A defect in this function, found and fixed 2026-08-18 (W5, custom objectives).**
> > `predict_gbm`'s LightGBM branch applied `np.exp` to the raw score unconditionally,
> > though `_OBJECTIVES` carried the inverse link as its third element and its own comment
> > said the raw-score path needed it. Correct for three of the four supported objectives
> > and wrong for `binary:logistic`, which returned `exp(f)` where the model means
> > `1 / (1 + exp(-f))` — a "probability" above 1 for every row the model thought likely,
> > and the two agree to within 1% at `f = 0`, so a book with a weak signal would not have
> > shown it. Nothing had asked a LightGBM binomial model for a prediction; the custom
> > objectives slice needed the link recorded anyway (FR-MODEL-94), and the defect was
> > visible the moment it was. The regression test is
> > `test_a_binomial_model_is_scored_through_its_own_link`, parametrized over both backends
> > and over builtin/custom, and the fix is `_apply_inverse_link` reading
> > `GbmFitResult.inverse_link`.
> >
> > **Artifacts fitted before that field existed carry `None`**, and the LightGBM branch
> > reads that as `exp` — exactly what those artifacts have always been scored with. The
> > default is the *old* behaviour rather than the correct one on purpose: `None` there
> > means "nobody recorded it", and silently changing what a stored model predicts is a
> > worse failure than the one it would fix. `fit_gbm` sets the field explicitly on every
> > path, so nothing fitted from here on relies on the fallback.

> **Corrected a fifth time, 2026-08-18 (W5, peril structures).** `assemble_risk_premium`
> and `reconcile` were declared taking a `PerilStructure`. They cannot, for the reason four
> earlier signatures could not take a `Model`: a structure carries model *references*
> (`model:motor-ad-frequency@7`), and resolving one needs the database ADR-0001 forbids
> this package. `PerilPrediction` is that resolution — one peril's arrays plus the treatment
> to apply — and it carries the ref only as a label.
>
> Three further departures, each forced by something the declaration did not know:
>
> * **`reconcile` returns a `ReconciliationResult`, not the persisted `Reconciliation`**,
>   which carries a `dataset_version_id`, a `part` and a `computed_at` only the platform
>   can supply. Exactly the `compute_diagnostics` / `DiagnosticsResult` split.
> * **`observed`, `exposure` and `tolerance` are parameters.** FR-MODEL-60 compares modelled
>   burning cost to *observed* burning cost and does not say where the observed figure comes
>   from — and it cannot be derived: a severity model responds to its own peril's cost, not
>   the total, and the exposure a frequency model offsets by is not necessarily the exposure
>   the burning cost is expressed per. The caller declares both columns, with **no default**;
>   a default would reconcile against whichever column happened to match and report a ratio
>   for it.
> * **`treatments` is a parameter rather than read from the frame.** The assembled frame
>   carries numbers and not their provenance, and FR-MODEL-74 requires the treatment to be
>   stated beside the number. A peril whose treatment nobody supplied would be recorded as
>   `none`, which is a claim about how the number was produced.
>
> **`separate_model` is refused by name** with `LOSS_TREATMENT_UNIMPLEMENTED`, in
> `pricing-core` *and* before the Job is queued. It needs an excess-layer model's own
> predictions; reconciling it as though it were `none` would under-state the premium by
> exactly the excess layer, in silence. `capped` and `flat_loading` are both computed —
> they are the same multiplication from different provenance, so computing one and refusing
> the other would have been an arbitrary line.

Sketch of the compiled objective handed to XGBoost — note the platform, not the user,
owns this function; the user only ever supplied `loss` (§4.6):

```python
def make_xgb_objective(fns: ObjectiveFns):
    def objective(preds: np.ndarray, dtrain: xgb.DMatrix):
        y = dtrain.get_label()
        w = dtrain.get_weight() if dtrain.get_weight().size else np.ones_like(y)
        f = preds                       # base_margin is already in preds (verified, research F5)
        g, h = fns.grad(y, f, w), fns.stabilise(y, f, w)   # FR-MODEL-43 strategy
        _finite_or_abort(fns, g, h, y, f, round_index)     # FR-MODEL-48
        return g, h
    return objective
```

> **Four corrections to this section, 2026-08-18 (W5, custom objectives).** Each is the
> code being right and the sketch being wrong; none changes a requirement.
>
> * **`make_xgb_objective` takes no `base_margin`.** The sketch's own comment says the
>   margin is already in `preds`, so a parameter for it can only be added a second time —
>   which under a log link doubles the exposure and fits plausibly.
> * **The hessian strategy is `fns.stabilise(y, f, w)`, not `np.maximum(h, hessian_min)`.**
>   That expression is `clip_to_min` and only that; `abs` reflects a different number and
>   `gauss_newton` computes one. Leaving the choice at the call site would have meant each
>   backend adapter re-implementing FR-MODEL-43, and two of the three strategies silently
>   becoming the third.
> * **`make_lgb_objective` is `(preds, dataset)`, not `(y_true, y_pred, weight)`.** The
>   three-argument form is the scikit-learn wrapper's. `lgb.train` calls
>   `fobj(inner_predict(0), self.train_set)` — lightgbm 4.7.0, `basic.py:4276` — and the
>   sklearn shape raises `TypeError` on the first boosting round. Weights come off the
>   dataset, so the case weights the three-argument form was chosen for are still there.
>   Both adapters therefore read `get_label`/`get_weight` off their backend's own object,
>   and `preds` carries the offset on both.
> * **`certify_objective` returns `CertificateResult` and takes no `seed`.** The
>   certificate carries an id, a job and a `certified_at` that ADR-0001 forbids this package
>   to allocate — the same `compute_diagnostics`/`DiagnosticsResult` split, arrived at for
>   the same reason. The seed is already in `SamplingSpec`; a second one would let a caller
>   record a certificate whose stated sampling does not reproduce it.
>
> `parse_expression` and `derive_derivatives` above are **declared and unbuilt**, and are
> the whole of `ObjectiveKind.EXPRESSION` (FR-MODEL-40/41). They are gated behind
> `expression_objectives_enabled`, off throughout Phase 1 (FR-MODEL-75), and W5 shipped the
> twelve templates only. `compile_objective` refuses a non-template objective by name.

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

> **Built 2026-08-15 (W5).** The factor workbench is routed at `/factors/:datasetVersionId`
> and reachable from a `validated` version's detail view — only a validated one, because
> `02` R1 means a link on a draft leads to a `409` the screen cannot explain.
>
> The interaction requirement is met through **FR-MODEL-75's `/evaluate` routes**, which
> this view is the reason for: every edit is recomputed by the platform, on the same code
> path a fit would use, and nothing is approximated in the browser. Building it is what
> found that the requirement was unmeetable — `/propose` derives from a *method* and cannot
> accept an edited one.
>
> **Two departures from the Contents column, both stated rather than quietly dropped:**
>
> * **Boundaries are numeric inputs, not drag handles.** The requirement they serve is that
>   the consequence is visible before saving, and an input meets it — while also expressing
>   a cut point the mouse cannot land on. Drag is polish, and it is not built.
> * **No merge-tolerance slider on the grouping editor.** Tolerance is a parameter of
>   `credibility_weighted` *proposal*, and re-proposing on every drag would re-derive the
>   mapping and discard the actuary's edits. The editor moves levels between targets
>   instead, which is the operation §5.3's "relativity-ordered levels" is really about.
>
> Also not built: the column list's inline profile one-ways (the `/profile` view has them),
> and the monotonic-direction and intent controls — those belong with creating the Factor
> that *pins* a banding, which is the next slice.

> **Not built, 2026-08-18 (W5, custom objectives).** Neither `/objectives` nor
> `/objectives/:slug@:version/certificate` has a view, and both stay owned by **W6b** with
> the rest of `02` §5.3. The slice built the API and the certification behind them
> (FR-MODEL-95 added the two reads a certificate screen needs), so what is missing is the
> screen and only the screen.
>
> Two Contents items are worth flagging before W6b starts, because both are harder than the
> column implies:
>
> * **"Per-check pass/warn/fail" is four statuses, not three.** `CheckStatus` is
>   `pass | warn | violated | failed` (§4.7), and `violated` is the ordinary result for a
>   legitimate non-convex pricing loss (FR-MODEL-43) — rendering it as a failure would tell
>   an approver to reject the objectives this platform exists to support.
> * **"Editor with live parse errors" has nothing to parse in Phase 1.** Template objectives
>   are a picker and a parameter form; the expression editor arrives with the `expression`
>   kind in Phase 2 (FR-MODEL-75).

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
| ~~**SHAP**~~ **The backends' own TreeSHAP** | Transparency artifacts (FR-MODEL-35) | **Amended 2026-08-17 (W5, transparency): the `shap` package is not a dependency.** XGBoost's `pred_contribs` and LightGBM's `pred_contrib` are the same TreeSHAP algorithm on the same trees, already linked against the booster `pricing-core` holds — and `shap` would have added a dependency of its own — for plotting the frontend does (§5.3) and aggregation that is fifteen lines — to the package ADR-0001 keeps importable standalone. *(Corrected 2026-08-17, same day: this row first gave the cost as "would have pulled scikit-learn and its transitive weight in". The scikit-learn half was wrong when written — `glum` 3.4.1 requires it, so it was already installed in every environment this package has ever had, as OQ-MODEL-9 found the next hour. The row's conclusion is unaffected: `shap` itself is still a dependency added for work already done elsewhere.)* What is genuinely lost is **interaction values on LightGBM**: XGBoost computes them (`pred_interactions`, feeding FR-MODEL-79's suggestions and never a Factor), LightGBM does not compute them at all, and `ShapSummary.interactions_available` reports that as a capability rather than as an empty list. Revisit if a third backend or kernel SHAP for a non-tree model is ever needed |
| **SymPy** | Symbolic gradient/hessian derivation (FR-MODEL-40) — **Phase 2**, with `expression` objectives (FR-MODEL-75) | Differentiation of `Piecewise` (from `where`), simplification, lambdify-free code generation into our own expression tree |
| **NumPy** | Compiled objective evaluation | Vectorised, allocation-conscious gradient/hessian evaluation; `np.errstate` discipline for log/exp edges |
| **Python `ast`** | Restricted grammar parsing (§4.6) | Allow-list node walking, depth/size limits, why `eval`/`compile` on user input is never acceptable |
| **Polars** | Factor resolution, banding/grouping application, diagnostic aggregation | `replace_strict` for grouping maps (it refuses an unmapped level rather than dropping it, which is FR-MODEL-13's whole point). **Banding is `numpy.searchsorted`, not `pl.cut`** — the artifact's `closed`, `null_level`, `below_range` and `above_range` policies decide where a value lands, and `cut` implements one fixed convention (added 2026-08-15, W5) |
| **SciPy** | CIs, profile likelihood for Tweedie `p`, numeric derivative checks in certification, credibility standards for `credibility_weighted` groupings (FR-MODEL-80) | `scipy.optimize` for the profile grid, `scipy.stats` for CIs, plus `scipy.cluster.hierarchy` (Ward linkage + `fcluster`) for FR-MODEL-14's `hierarchical_clustering` — exposure weighting by observation repetition, since the clusterer takes no sample weights (added 2026-08-15, W5) |
| **scikit-learn** | FR-MODEL-9's `tree` banding and FR-MODEL-14's `tree` grouping (FR-MODEL-85) | `DecisionTreeRegressor` with `max_leaf_nodes` and `sample_weight`; cut points read off `tree_.threshold` where `tree_.feature >= 0`. Splits are midpoints between adjacent observed values, so no threshold coincides with a value in the data and a banding's `closed` convention moves no row. Declared rather than relied on transitively — it arrives with `glum`, but a package that *imports* it and does not declare it is the pandera state `01` §4.4 found in reverse (added 2026-08-17, W5) |
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
| **NFR-MODEL-12** | A grouping proposal's evidence (FR-MODEL-15) is computed without summarising the source levels twice. Stated as a requirement rather than left as an implementation detail because it is where NFR-MODEL-3's budget actually goes: at 10 000 levels a one-way summary costs ~4 s in per-level interval quantiles, and doing it once instead of twice is most of the difference between meeting the budget and missing it. (Added 2026-08-15, W5.) |
| **NFR-MODEL-4** | Diagnostics computation adds no more than 30 % to fit wall-clock. |
| **NFR-MODEL-5** | Objective certification completes in < 3 min including the synthetic smoke fit. |
| **NFR-MODEL-6** | Determinism: identical `spec_hash` + seed reproduces identical coefficients to 1e-10 (GLM) and an identical booster hash (GBM), on the same library versions (FR-OVR-8). |
| **NFR-MODEL-7** | A stored Model round-trips: export → import into a clean instance → predictions identical to the last representable digit (FR-OVR-2). |
| **NFR-MODEL-8** | Security: user-supplied expressions never reach `eval`/`exec`; the parser rejects out-of-grammar input with a position-accurate error; compiled objectives cannot allocate unbounded memory or exceed their per-round time budget (FR-MODEL-48). |
| **NFR-MODEL-9** | Audit: factor/banding/grouping creation and edit, fit start and completion, objective derivation/certification/approval, and every status transition emit Audit Events with before/after state. |
| **NFR-MODEL-10** | Memory: fitting a 5 M × 60 dataset stays within 32 GB, using `QuantileDMatrix`/streaming construction rather than duplicating the design matrix. |
| **NFR-MODEL-11** | Diagnostics artifacts stay under 50 MB per model; larger evidence (SHAP dependence, residual scatter) goes to content-addressed blobs referenced from the artifact. |

> **NFR-MODEL-3 measured 2026-08-15 (W5), and it is met for three of the four methods
> built.** 678 013 rows — freMTPL2's row count — with a 10 000-level categorical, on the
> development machine, budget 5 s:
>
> | Proposal | Measured | Verdict |
> |---|---|---|
> | `propose_banding`, all four methods, 20 bands | 0.11 – 0.24 s | **met**, with two orders of magnitude of headroom |
> | `propose_grouping`, `credibility_weighted`, 10 000 levels | 4.24 s | **met**, and only after NFR-MODEL-12 — it was 8.59 s while the source summary was computed twice |
> | `propose_grouping`, `hierarchical_clustering`, 10 000 levels | 6.52 s | **not met** |
>
> The shortfall is Ward linkage, which is O(n²) in the level count and spends ~2.4 s of
> those 6.52. It is stated rather than rounded away: at the 10 000 levels this requirement
> names, the method is over budget by 30 %, and a proposal endpoint that takes six seconds
> is one the factor workbench has to put a spinner on.
>
> Two routes out, neither taken here because both are design changes rather than tuning:
> compute from the stored Profile, which this requirement's own wording already suggests
> (`01` FR-DATA-26 holds the one-way summaries), or replace Ward with a contiguous 1-D
> partition — legitimate, since the clusters are contiguous in rate order by construction,
> but a different method under the same name. **Owner: the slice that builds the factor
> workbench** (`00` §5.6's `/factors/:datasetVersionId`), which is the first caller that
> will feel it.

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-MODEL-1** | ~~Should `expression` custom objectives ship in Phase 1 at all, or only the `template` catalogue (§4.5)?~~ **DECIDED 2026-08-15: templates in Phase 1, expressions in Phase 2 — and the certification machinery is built in Phase 1 regardless.** Specified as FR-MODEL-75 and FR-MODEL-76. The restricted parser is not the deferred part and never was: it already exists for `01` FR-DATA-10. What Phase 2 adds is symbolic derivation, a second compilation target, and the review path for a loss a user wrote. |
| **OQ-MODEL-2** | ~~GBM prediction intervals: paired quantile models, "uncertainty unavailable", or a variance-model approximation?~~ **DECIDED 2026-08-15: `uncertainty: unavailable` with a typed reason by default, opt-in paired quantile models, and the variance approximation is never shipped.** Specified as FR-MODEL-77 and FR-MODEL-78. |
| **OQ-MODEL-3** | ~~Is the GLM approximation of a GBM a *transparency artifact* only, or should it be directly rateable — i.e. can a Rating Version rate on the approximation instead of calling the GBM, trading fidelity for a fully tabular rating structure?~~ **DECIDED 2026-08-17: both modes, and the mode belongs to the Rating Version rather than to the step.** Specified as `03` FR-RATE-60, which pins every `model_call` step's `mode` to `RatingVersion.model_reference_mode` and refuses a disagreement at save time; `03` FR-RATE-10 was ahead of its question rather than wrong and stands as written. What an approximation must *prove* before deploying in that mode is carved out as **OQ-MODEL-11**, and **OQ-MODEL-10** is unblocked. |
| **OQ-MODEL-4** | ~~Interactions as explicit Factors only, or also automatically-detected candidates from SHAP interaction values?~~ **DECIDED 2026-08-15: detected candidates are surfaced as suggestions with their exposure share and holdout lift; only an explicit Factor with a rationale can enter a Model Spec.** Specified as FR-MODEL-79. |
| **OQ-MODEL-5** | ~~Which credibility standard for `credibility_weighted` grouping — limited fluctuation or Bühlmann–Straub?~~ **DECIDED 2026-08-15: both, limited fluctuation as the default, recorded per grouping.** Specified as FR-MODEL-80, with `credibility_model`, its `(p, k)` pair and Bühlmann–Straub's variance components persisted in §4.3. |
| **OQ-MODEL-6** | ~~Hard gate on factor count / exposure-per-parameter, or a diagnostic warning?~~ **DECIDED 2026-08-15: a diagnostic always, and a gate only where a workspace configures one — unset by default.** Specified as FR-MODEL-81; the judgement belongs to the Approver (`06`), not to a constant chosen here. |
| **OQ-MODEL-7** | ~~How are protected-characteristic proxies detected, and what happens when detection fires?~~ **DECIDED 2026-08-15: the `prohibited` flag is the whole of Phases 1–2; a Phase 3 proxy assessment produces evidence for the approval request and never a block.** Specified as FR-MODEL-82; delivery is a Phase 3 deliverable, so the decision is made and the work is not now. |
| **OQ-MODEL-8** | ~~Does the GLM spine grow to meet §4's field sets, or does §4 narrow to a staged contract? §4.1, §4.4 and §4.8 declare fields the spine does not implement, and §4.8's `status ≥ fitted ⟹ diagnostics_id set` cannot be met while diagnostics do not exist.~~ **DECIDED 2026-08-17: §4 is a staged contract, re-widened as each slice lands — decided by demonstration, after the pattern ran six times.** Specified as FR-MODEL-87, which names every remaining residual with a verdict and an owner; the standing `spec_hash` versioning rule the question set as its own precondition is now FR-MODEL-86; `expression`'s verdict is FR-MODEL-88 and §4.8's R3 is restated enforceably by FR-MODEL-89. §4.4's nested `regularisation` block was a divergence rather than a staged field and is corrected in place. |
| **OQ-MODEL-9** | ~~Do `tree` banding boundaries (FR-MODEL-9) and `tree` grouping (FR-MODEL-14) justify adding a tree learner to `pricing-core`'s dependencies?~~ **DECIDED 2026-08-17: declare `scikit-learn` and fit a CART tree in both — the label `tree` must name the instrument.** Specified as FR-MODEL-85, with the dependency in §8; a one-tree booster would have cost no dependency at all and was rejected because its splits are not CART's. |
| **OQ-MODEL-10** | ~~Is the GLM approximation of a GBM (FR-MODEL-34) a **Model** in its own right, or a block inside the transparency artifact?~~ **DECIDED 2026-08-18: a Model in its own right — FR-MODEL-96**, owned by Phase 1b and due before anything references a transparency artifact by identifier. **Built 2026-08-19 (W5).** The deciding argument was supplied by OQ-MODEL-3's answer rather than by this row: an `approximation`-mode Rating Version pins what it rates on, and FR-OVR-14 requires a pin to resolve to an artifact with a status, which a `TransparencyArtifact` does not have. |
| **OQ-MODEL-11** | ~~What must a GLM approximation prove before a Rating Version may **deploy** in `approximation` mode?~~ **DECIDED 2026-08-18: a dislocation run against the same version in `exact` mode, within a workspace-declared premium-deviation threshold, with FR-MODEL-36's fidelity statement kept as the cheap pre-check — `03` FR-RATE-61**, Phase 2, with the deployment path it gates. R² answers a question about coefficients; the approval question is how different the prices will be. |
| **OQ-MODEL-12** | ~~May an `interaction` Factor cross a **continuous** operand?~~ **DECIDED 2026-08-18: no — refused by name, and no product term at any intent — FR-MODEL-97**, which ratifies what the interaction slice built and names the `diagnostic`-intent variant as the likely eventual answer, to be decided against a rate table that exists. |
| **OQ-MODEL-13** | ~~Should the platform ever offer a **true prediction interval** — one carrying the process variance `φ·V(μ)` — and under what name?~~ **DECIDED 2026-08-18: not until a named consumer asks — FR-MODEL-98**, which fixes the trigger (the first aggregate consumer), the name (`prediction_interval`) and the shape (aggregate first, and `confidence_interval_mean` never silently widened). |
| **OQ-MODEL-14** | ~~What uncertainty should a **penalised** GLM (`alpha > 0`) report, given that `glum` warns its covariance matrix "will be incorrect"?~~ **DECIDED 2026-08-18: report both, and state the basis — FR-MODEL-99**, which answers FR-MODEL-21 and FR-MODEL-63 together because one matrix produces both, and names the bootstrap as the exact answer with the consumer that triggers it. |
| **OQ-MODEL-15** | `GlmDiagnostic.aliasing` is `tuple[str, ...]` — collinear terms named — while `docs/contracts/schemas/diagnostics.schema.json` declares an array of untyped `object`. Should an aliasing entry be a bare term name, or a record such as `{term, aliased_with, reason}`? Neither side is obviously wrong — a name is what a reader acts on, an object entry says strictly more, and FR-MODEL-51 asks only for "a VIF/aliasing report". Found 2026-08-19 by widening the contract type comparison; pinned meanwhile so a new divergence still fails. Recommendation on file: keep the names, correct the contract, and decide when W6b renders the diagnostic. |
| **OQ-MODEL-16** | ~~A paired quantile interval covers `Y` while `UncertaintyKind.confidence_interval_mean` covers `E[Y\|x]`, and FR-MODEL-98 fixes the platform at exactly one kind — what does a quantile-pair response call itself?~~ **DECIDED 2026-08-19: a third member, `quantile_pair_interval` — FR-MODEL-101**, which takes neither existing value and leaves FR-MODEL-98's reserved `prediction_interval` waiting for the aggregate consumer that triggers it. FR-MODEL-98 is amended by addendum rather than edited. |
| **OQ-MODEL-17** | On a rebuild (`should_fit=False`), `model.transparency` pays a full GLM fit plus a full type-III diagnostics pass — one refit per factor — for numbers it then discards, because the surrogate Model already exists; nobody has costed it. Should the Job skip that compute and reuse the surrogate's already-fitted numbers, keep recomputing for a fresh fidelity measurement, or make it conditional? Found 2026-08-19 in the final whole-branch review of FR-MODEL-96 (fix round). Recommendation on file: skip the compute on `should_fit=False` and reuse the stored numbers — `spec_hash` (FR-MODEL-66) already guarantees a rebuild's numbers are identical to the ones stored at the first build, because both the source Model and the surrogate's own spec are immutable once fitted, so recomputing buys nothing; decide before Phase 1b measures the Job's cost against `07`'s job-latency NFRs. |
| **OQ-MODEL-18** | ~~Should a Custom Metric's certificate run §4.7's full nine-check `ObjectiveCertificate` battery (each derivative/convexity check reporting `not_applicable`, since a metric has no gradient or hessian), or a reduced, metric-specific check set?~~ **DECIDED 2026-08-19: a reduced certificate — `finiteness`, `direction_holds`, `scale_behaviour`, `smoke_evaluation` — FR-MODEL-105**, sharing §4.7's `CheckStatus`, `SamplingSpec`, `CertificateOutcome` and `outcome_of` unchanged rather than its check list. |
| **OQ-MODEL-19** | ~~Does a Custom Metric define its own value computation — a metric-specific template catalogue or `expression` grammar — or does it name an existing `ObjectiveTemplate` (§4.5) and reuse that template's loss?~~ **DECIDED 2026-08-19: a metric names an `ObjectiveTemplate` and reuses its loss, evaluated as an exposure-weighted mean — FR-MODEL-103**, on OQ-MODEL-1's Phase-1-templates-only rule. |
| **OQ-MODEL-20** | ~~§5.1 declared one `POST /custom-metrics` row, not built and deferred to Phase 1b (FR-MODEL-45). Now that a metric gates early stopping (FR-MODEL-107), should this slice ship create only, or the full six-endpoint set FR-MODEL-95 built for `custom-objectives`?~~ **DECIDED 2026-08-19: all six — FR-MODEL-108**, the same argument FR-MODEL-95 made for objectives: an approver who cannot fetch a certificate is being asked to approve a verdict they cannot see. |
| **OQ-MODEL-21** | LightGBM evaluates builtin metrics before `feval`, so a spec that declares a builtin in `eval_metrics` and early-stops on a Custom Metric never gets the builtin reported (FR-MODEL-107's 2026-08-20 amendment), even though `GbmFit` says nothing about the drop. Does a documented silent drop satisfy FR-MODEL-106's "honoured"? Found 2026-08-20 in the final branch review, before merge. Recommendation on file: record the drop on `GbmFit` rather than refuse the fit or leave the caller uninformed. |
| **OQ-MODEL-22** | Which offsets-from-model come after the GLM-to-GLM slice? Open, gated on W5: FR-MODEL-24's 2026-08-21 amendment builds offset-from-another-model for GLM specs referencing fitted GLMs only — GBM-referenced offsets, `GbmSpec`-declared offsets and the peril-reconciliation scoring path each wait for a workflow that needs them. |
