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
| **FR-MODEL-1** | A **Factor** is a named, versioned transformation over one or more columns of a Dataset Version, of exactly one type: `identity`, `banding`, `grouping`, `interaction`, `spline`, `polynomial`, `offset`, `expression`. No other types exist without a spec change. **Amended 2026-08-22 (OQ-MODEL-23 decided).** The list above is left exactly as Phase 0 declared it, because it records what was believed; the set is still eight. What changed is the standing of three arms. `offset` is **superseded** — FR-MODEL-114, which keeps it in the published contract and makes its FR-MODEL-88 refusal permanent rather than pending. `spline` and `polynomial` stay declared and stay refused, **gated on FR-MODEL-115**; the order between them is decided when that gate closes and not before, because the evidence that would order them is what the gate produces. |
| **FR-MODEL-116** | **`offset` is superseded as a Factor *intent*, on a layer argument and not a duplication one, and the arm stays in the published contract.** Offsetness is a property of **one fit** — is this term's coefficient held at 1 in *this* model — whereas `Factor.intent` is a property of the **Factor**, which is defined against a Dataset (FR-MODEL-2) and reused by every Model Spec that names it. A Factor marked `offset` could therefore never carry a free coefficient in a second model without being re-declared, which is the wrong layer rather than a second spelling of the right one; §4.4's `OffsetSpec` sits on the spec, the layer that varies per fit. **The grounds are deliberately not the duplication argument.** FR-MODEL-114 superseded the Factor *type* `offset` as a second mechanism for a solved problem, and that claim does **not** transfer here, because the two mechanisms are **incomparable — neither subsumes the other**. `OffsetSpec`'s `column` is a single **raw dataset column**, validated against the version's schema, so it can express neither a banded or grouped offset column nor two offset terms at once, and an offset column receives none of the versioning, lineage or prohibition a Factor carries. A `Factor` in turn carries no model reference and forbids extra fields, so it cannot express `OffsetSpec`'s `model` kind — FR-MODEL-24's offset-from-another-model — at all. A duplicate mechanism is one that does the same work twice; these two each do work the other cannot. Superseding on a duplication claim that fails checking would have recorded a reason the repository could later discover to be false. Nothing in `docs/workflows/` asks for either missing capability today; if one is asked for, the answer is to extend `OffsetSpec` at the layer that owns offsets, not to revive a mis-layered enum arm. **Superseded means permanently refused, never removed**, on the grounds FR-MODEL-87 sets and FR-MODEL-114 already applied to the type arm: the arm stays in `model-schema` and in the generated OpenAPI, because artifacts are immutable and `Factor.model_validate` on read would turn a stored `offset` row into a `ValidationError` failing the whole workspace's factor list rather than the one row. This repository's fixtures and seed hold **no such row** — stated because §13 rule 6 requires it to be stated — and no user could have created one either: the factor workbench has no intent control at all, so every factor made through the UI takes `FactorCreate`'s `risk` default. *(That §5.3 claims an intent control the built view does not have is a separate §14 question-4 finding, recorded in the roadmap rather than fixed here.)* The arm stays regardless. The refusal is sited in `resolve_factors` beside FR-MODEL-88's type refusals: one place, which every fit, predict, diagnostics and transparency path already reaches. (OQ-MODEL-25, decided 2026-08-22.) |
| **FR-MODEL-117** | **`diagnostic` is refused as a Factor intent pending OQ-MODEL-27, and its refusal said "not yet" where FR-MODEL-116's said "never" — until OQ-MODEL-27 was decided and FR-MODEL-120 made it "never" too; the dated amendment closing this row records the reversal, and the test carrying this requirement's marker now asserts `"yet"` is absent from the message.** *(Tense corrected 2026-08-22 by the W5 closure slice: the row was internally correct but its opening sentence, read alone, stated the opposite of what the code does — `CLAUDE.md` §14 question 4.)* It carries the identical defect OQ-MODEL-25 raised for `offset` — declared in FR-MODEL-3, selectable through `POST /api/v1/factors`, read by neither fit path, and therefore fitted with a free coefficient — and a decision that refused one arm while leaving an identically-shaped one live would have fixed half a defect. It is **not** superseded alongside it, because the two fail differently: `offset` names a mechanism that exists at another layer, while `diagnostic` names one that exists **nowhere** and duplicates nothing, so the supersession argument has nothing to point at. FR-MODEL-3 gives it no gloss, so what it should mean — a factor resolved and reported but held out of the linear predictor, or merely `control` under a second name — is a design choice this specification has never made, and settling it inside a refusal would be the silent resolution `CLAUDE.md` §10 forbids. Refused now because a silent mis-fit is the one outcome worse than a loud refusal, and gated rather than closed. Owner W30. (OQ-MODEL-25, decided 2026-08-22.) *(Amended 2026-08-22, OQ-MODEL-27 decided: the gate is closed by FR-MODEL-120, and the ground this requirement gave for keeping it open was wrong. It declined to supersede because the supersession argument "has nothing to point at" for an arm naming a mechanism that exists nowhere — but that is the **duplication** argument, which OQ-MODEL-25 had already refuted and did not decide on. The argument it decided on was a layer one, and a layer argument needs no mechanism elsewhere to point at. The refusal itself stands unchanged in behaviour and changes only its word: "not yet" becomes "never".)* |
| **FR-MODEL-120** | **`diagnostic` is superseded as a Factor *intent*, on the same layer argument FR-MODEL-116 turns on, and the arm stays in the published contract.** **It is not redundant with `control`**, which is the reading that would have made it cheap to delete and is the one this decision rejects first: the enum answers two questions at once — does the term enter the linear predictor, and may it be rated on — and `risk` (both), `control` (fitted, never rateable) and a `diagnostic` meaning *resolved and reported but held out of the linear predictor* occupy three distinct cells of that pair. So the arm names a real capability rather than a synonym, and FR-MODEL-117 is right that FR-MODEL-3 never says which. What fails is not the meaning but its **siting**: whether a term is held out of *this* linear predictor is a property of one fit, while `Factor.intent` is a property of a Factor reused by every Model Spec that names it, so a Factor marked `diagnostic` could never be fitted in a second model — the identical error FR-MODEL-116 rejects, reached without inventing the meaning FR-MODEL-3 omits, because **both candidate readings fail**: the distinct one is mis-sited, and the redundant one is `control` already. **Where the capability lives if a caller asks for it is a Model Spec field, not a Factor one.** `ModelSpecCommon.factors` is a flat `tuple[UUID, ...]` carrying no per-factor, per-spec attribute, so there is nowhere on a spec today to say "resolve this one and report it, do not fit it"; that field is what an asking caller gets, gated and owned by W30 rather than foreclosed by the supersession or left ownerless by it. **Blast radius, measured rather than asserted**: the arm is read in `REFUSED_FACTOR_INTENTS`, `Factor.intent`, the generated contract and the `factor.created` audit event; `rateable()` tests `risk` alone and has no production caller anywhere in the repository, the factor workbench contains the string `intent` zero times so no actuary can select the arm through the UI at all, and `03` FR-RATE-25 names `control` by itself, so the one cross-module obligation on this enum needs no edit. The arm stays in `FactorIntent` because artifacts are immutable and a stored row must stay loadable, exactly as FR-MODEL-114 and FR-MODEL-116 leave theirs. `risk` and `control` survive **because both are genuine Factor-level properties**: that is the test this enum is held to, and it is the one both superseded arms fail. (OQ-MODEL-27, decided 2026-08-22.) |
| **FR-MODEL-2** | Factors are defined against a Dataset (not a version) and are *resolved* against a specific version at fit time; resolution fails loudly if a required column is absent or has changed dtype. |
| **FR-MODEL-3** | A Factor declares its **actuarial intent**: `risk` (a genuine rating variable), `control` (present to absorb variance but not to be rated on, e.g. year-of-account), `offset`, or `diagnostic`. Rating Versions may only use `risk` factors; a `control` factor reaching a rate table is a validation error in `03`. *(Amended 2026-08-22, OQ-MODEL-25 decided — this requirement said what an intent means at **rating** time and nothing about **fit** time, which is the whole of the defect that question found. Stated now for every arm: `risk` and `control` both enter the design matrix with a **free coefficient** and differ only in rateability, which is what `control`'s own gloss — "present to absorb variance" — already meant and what `rateable()` implements; `offset` is superseded by FR-MODEL-116; `diagnostic` is refused by FR-MODEL-117 and superseded by FR-MODEL-120, so **the enum has two live arms and two that a stored artifact may still carry**. When the question was raised **no arm of this enum was read by either fit path**, so the two arms this requirement never glossed were fitted freely — a silent mis-fit rather than a refusal.)* |
| **FR-MODEL-4** | A Factor may declare a **monotonic direction** (`increasing`, `decreasing`, `none`) with a written rationale. The direction is enforced as a constraint in GBM fitting (FR-MODEL-20) and checked (not enforced) for GLMs, where a violation is reported as a diagnostic. |
| **FR-MODEL-5** | A Factor may declare a **prohibited** flag with a reason (e.g. a protected characteristic or a proxy the insurer has decided not to use). Prohibited factors cannot be added to any Model Spec; the attempt is refused and audited. |
| **FR-MODEL-82** | **Proxy detection is a Phase 3 deliverable, and never an automated block** (OQ-MODEL-7, decided 2026-08-15). Through Phases 1–2 the platform's only treatment of a protected characteristic is FR-MODEL-5's `prohibited` flag, which refuses direct use and audits the attempt; the platform holds no protected characteristics of its own (`00` FR-OVR-9). From Phase 3 an optional **proxy assessment** consumes an insurer-supplied reference table that does carry the characteristic, measures each candidate Factor's association with it — mutual information, and the AUC of the factor predicting it, exposure-weighted, with the reference population and its date recorded — and attaches the result to the approval request as evidence. It never refuses a Factor: whether an association amounts to unlawful discrimination is a legal judgement, not a statistical one, and a platform that answered it automatically would be answering a different question from the one asked. `04` FR-OPT-24 applies the same principle to price change. |
| **FR-MODEL-91** | **An `interaction` Factor crosses two or more other Factors, named by id in `operand_factor_ids`, and resolves to the combined levels of their resolved values.** Added 2026-08-18 (W5, the interaction slice): FR-MODEL-1 has listed the type since Phase 0 and §4.1 carried no field to express one, so the type was selectable and unresolvable — FR-MODEL-88's position for five arms, now four. **Operands are Factors rather than columns** because every other place the specification names an interaction names factors (§4.4's `interaction_constraints`, §4.9's `top_interactions`), and because an operand is usually itself a banding or a grouping: crossing raw `driver_age` with raw `region` gives one cell per policy, while crossing `driver_age_banded` with `vehicle_group_rated` gives a table an actuary can rate on. Three consequences the implementation forced, each a defect if left implicit: **(i)** only *observed* combinations become levels, because a cell with no exposure would carry a coefficient fitted on nothing and on any real cross most cells are empty; **(ii)** an operand contributes **no design column of its own** — a full cross spans every cell, so its operands' main effects are collinear with it and a design carrying both is rank-deficient; **(iii)** FR-MODEL-51's Type III test therefore compares the interaction against the **main-effects** model rather than against no term at all, which is the question an actuary means by "does this interaction earn its place". A **continuous** operand is refused by name (OQ-MODEL-12), and FR-MODEL-5's prohibition reaches through the cross: a prohibited Factor that could enter a spec crossed with something else would not be prohibited. |
| **FR-MODEL-97** | **Every operand of an `interaction` Factor must resolve to levels: a continuous operand is refused by name, and no product term is offered at any intent.** (OQ-MODEL-12, decided 2026-08-18, ratifying what the interaction slice built.) The refusal names the operand and the remedy — band or group it, then cross the result — so the actuary is left with a rateable structure by construction. A product term is legitimate GLM practice and is refused anyway, because `03`'s rating DAG is a graph of *tables* and a varying slope has no cell: allowing one moves the failure from the factor, where it is a message, to the rating slice, where it is a model somebody has already fitted. **The narrower third option — a product term for `diagnostic`-intent factors only (FR-MODEL-3), never rated on — is the likely eventual answer and is deliberately not taken now**: it needs no contract change, only a widened refusal, and it should be decided against a rate table that exists rather than one that is specified. Revisit when `03`'s rate-table shape is built; owner the maintainer. Refusing is additive to undo and impossible to undo the other way round, which is the whole of why the order is this one. |
| **FR-MODEL-92** | **A backtest is readable.** `GET /api/v1/models/backtests/{id}` returns the stored artifact, or a 404 naming it. Added 2026-08-18 (W5, the backtest slice): §5.1 declared the `POST` and no read, which is a 202 whose artifact nothing can fetch — complete to the endpoint audit, since that compares the spec against the contract and an endpoint missing from both is in neither, and unusable to every caller. **The fourth time**: FR-MODEL-84 repaired it for the transparency artifact, FR-MODEL-56 for the comparison, FR-MODEL-90 for the peril structure. By backtest id rather than by model, because unlike `Diagnostics` a model has many — one per period it has been measured against — and the Job's result names the one just produced (`backtest:{id}`). A **list** by model is what `05-monitoring.md` will read and is deliberately not built here: nothing consumes it yet, and `CLAUDE.md` §0 puts a later phase's capability in the spec rather than the code. **Evidenced 2026-08-23 (W32-6).** The prior marker sat on an OpenAPI-presence assertion (`test_backtests.py`'s "both backtest routes are in the published contract"), which asserts the two paths are spelled correctly and would have stayed green against a route returning 500 on every call. The cross-workspace 404 and the "naming it" clause are now tested over HTTP in `backend/tests/test_api_backtests.py`, and the fold was proven load-bearing by removing it and watching the test return 200 (§13 rule 4). |
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
| **FR-MODEL-15** | Every Grouping stores its method, parameters, source Level statistics, the resulting target Level statistics, and the *change in fit* (deviance delta, degrees of freedom saved) it implies — grouping is a modelling decision and must be defensible as one.  **Amended 2026-08-22 (W5, the audit-remediation slice): partly unmet, and the requirement keeps the obligation rather than being edited down to what was built.** `GroupingEvidence` carries `target_level_stats` and **no `source_level_stats`** (`model_schema/modelling.py:482`), so of the five things this requirement names — method, parameters, source Level statistics, target Level statistics, change in fit — four are stored and one is not. `grouping.schema.json` declares `source_level_stats`, so the published contract has promised it since Phase 0 while nothing populates it. **The spec is the side that is right**: a reviewer asked to accept a merge needs the levels as they were, not only as they ended up, and the deviance delta alone does not show which thin cells were absorbed into which. The marker on `test_grouping_evidence_reports_what_the_merge_cost` therefore **overstates its coverage** — it evidences the target half and the change in fit, and is not proof of this requirement whole. **Owner: W6b**, the factor-workbench slice, because the source statistics exist to be *read* beside the proposal and the workbench is the first thing that reads them; until then the field stays declared-and-unbuilt in FR-MODEL-87's sense. |
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
| **FR-MODEL-19** | Actuarial defaults are applied unless explicitly overridden, and any override is recorded with a justification: **frequency** → Poisson, log link, `offset = log(exposure)`; **severity** → Gamma, log link, `weight = claim_count`; **burning cost** → Tweedie with `1 < p < 2`, log link, `weight = exposure`; **conversion/retention** → binomial, logit link. *(Amended 2026-08-22, W5.* **Built for GBMs.** *Until this date `fit_gbm` accepted `spec.weight` and never read it, while `fit_glm`, `fit_ebm` and `compute_diagnostics` all honoured it — so a severity GBM declaring this requirement's own default fitted unweighted, and FR-MODEL-55 then labelled its diagnostics claim-count-weighted on the strength of a spec the fit had ignored: the label true of the metric and false of the model that produced it. The roadmap's EBM slice record states a dated note to this effect was written on 2026-08-21; no such note existed — `git log -S` shows the phrase entering the repository only in `c2c54a6`, and only in `docs/roadmap.md`. FR-MODEL-87's obligation is discharged here by building the field rather than by staging it: both backends now weight the training and holdout datasets, and the custom objective and custom eval metric paths — whose `get_weight()` readbacks had existed unfed since the GBM slice — receive the declared column. Measured on a closed-form severity book, the same Gamma fit moves from an unweighted mean of 5.0 to a claim-count-weighted 1.80 on both backends. The interpretation change moves `spec_hash` `v9` to `v10` (FR-MODEL-86).)* |
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
| **FR-MODEL-24** | An **offset from another model** is supported (`offset_model_ref`), enabling residual modelling and "fit on top of the current rating structure" workflows. The referenced model version is pinned. **Amended 2026-08-21 (W5 slice 4).** The ref is the canonical `model:slug@version` string (ID-3). v1 builds the offset for GLM specs only: the referenced model must be a fitted GLM, and the offset is its linear predictor (η, including its own offset) on the training data — the two links must be equal, refused by name otherwise (`MODEL_OFFSET_REF_INVALID`). Refused by name, not built: a `GbmSpec` whose offset is `kind: "model"`; a ref naming a GBM or EBM model; the peril-reconciliation scoring path (it fails named, `MODEL_OFFSET_MISSING`, until W5 wires the resolver there). The fit records what was constructed: `GlmFitResult.offset_model_ref` carries the resolved pinned ref. Diagnostic weighting for a model-offset fit follows `spec.weight` (COUNT default) — the exposure-weighting convention is never inferred from the offset. The Phase-0 scaffold's `model_ref: str` is renamed `offset_model_ref` with the artifact-ref pattern: the spec and the hand-authored contract have always named and typed it that way, and the scaffold field was read by nothing. **Amended 2026-08-22 (W5, the closure slice): the peril-reconciliation refusal is now pinned by a named test, and making that test pass required fixing the code rather than the sentence.** The clause above says the path "fails named, `MODEL_OFFSET_MISSING`". It failed, but **not named**: `PredictionError` is a bare `RuntimeError` from `pricing-core` — a sibling of `ModellingError`, not an `app.errors.PlatformError` — so `execute_job`'s OQ-PLAT-7 clause did not catch it and the Job stored `code="JOB_HANDLER_FAILED"`, with the string `MODEL_OFFSET_MISSING` absent even from the message. A caller could not branch on the refusal, and a named refusal was indistinguishable from a handler crash — the exact failure OQ-PLAT-7 exists to remove. **The specification was the correct side and the code was behind** (`CLAUDE.md` §0), so `_reconcile` now catches `(ModellingError, PredictionError)` around its scoring pass and re-raises with `exc.code`, which is what `backend/src/app/platform/prediction.py` already does for the synchronous path. Proven, not assumed (§13 rule 4): narrowing the catch back to `ModellingError` alone fails the test with `assert 'JOB_HANDLER_FAILED' == 'MODEL_OFFSET_MISSING'`. **Two further instances of the same gap are recorded rather than fixed**, because a closure slice must not ship an unproven claim: `_quantile_crossing` scores twice outside any handler, and `_compare` catches `ModellingError` only, so a `PredictionError` raised inside `compare_models` escapes it. Both lose the code the same way. Neither has a test that would show it, and writing the fix without one would assert enforcement rather than prove it — **owner: the slice that next touches either handler, or a PLAT slice taking the root cause**, which is that `execute_job` knows `PlatformError` and nothing of `pricing-core`'s hierarchy. |
| **FR-MODEL-112** | **Offsets-from-model widen in this order: GBM-referenced offsets, then the peril-reconciliation scoring path** (OQ-MODEL-22, decided 2026-08-21). FR-MODEL-24's GLM-to-GLM slice is not the whole capability. (a) The next slice extends the reference to a fitted GBM — the referenced raw score minus its own `base_margin`, as η on the link scale — when a workflow needs it, as its own slice in Phase 1b. (c) The peril-reconciliation scoring path is then wired to the resolver; its owner is already W5 per the offsets slice's "not delivered, with owners" list. (b) A `GbmSpec` declaring the offset itself is **not scheduled**. (d) If residual modelling stays GLM-shaped in practice, GLM-to-GLM remains the whole capability rather than any of this — the fallback is a statement about practice, not an abandonment. |
| **FR-MODEL-113** | Bühlmann–Straub's variance components are **estimated or refused, never clamped** (FR-MODEL-80, built 2026-08-22, W5). A non-positive VHM estimate is the ordinary outcome on a column whose levels differ by no more than Poisson noise: it gives every level `Z = 0` and leaves `k = EVPV / VHM` unbounded, and `grouping.schema.json` gives `k` `exclusiveMinimum: 0` precisely so no artifact can carry a credibility nobody computed. The proposal is refused with `CREDIBILITY_VARIANCE_NOT_ESTIMABLE`, naming the condition — non-positive VHM, fewer than two levels carrying exposure, no claims, or one level holding effectively all the exposure — and stating that `limited_fluctuation` needs no between-level estimate and remains available on the same version. Substituting limited fluctuation's answer under Bühlmann–Straub's name is forbidden: the model is a recorded property of the grouping. |

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
| **FR-MODEL-33** | Every non-GLM Model must carry at least one **Transparency Artifact** before it can be referenced by a Rating Version (R3). Three forms are supported and may be present in any combination. Amended 2026-08-21 (W5, the EBM slice): the third form joined the artifact. |
| **FR-MODEL-34** | **GLM approximation** — a GLM fitted to the GBM's own predictions over the modelling population, with the same factor set (optionally banded), reporting R² / deviance explained against the GBM, and the residual pattern where the approximation is worst. This is the artifact that turns a GBM into something rateable as a table. |
| **FR-MODEL-35** | **SHAP factor summary** — TreeSHAP mean absolute contribution per factor, per-factor dependence summaries (contribution vs factor value, exposure-weighted), and the top interaction pairs. Computed on a reproducible sample with a persisted seed and sample size. *Amended 2026-08-23 (OQ-MODEL-31): the pairs are ranked on the training sample and the same statistic is recomputed on the holdout — one seed and one row cap applied to each partition, so the two numbers are comparable rather than merely adjacent (FR-MODEL-128).* |
| **FR-MODEL-79** | **Interaction candidates found in TreeSHAP interaction values are suggestions, never additions** (OQ-MODEL-4, decided 2026-08-15). The transparency artifact ranks the top pairs (FR-MODEL-35) and the factor workbench surfaces each with its exposure share and its holdout lift, so an actuary sees what a suggestion is worth and over how much of the book. The platform never writes a Factor into a Model Spec: an interaction becomes rateable only as an explicit `interaction` Factor (FR-MODEL-1) carrying an intent and a written rationale (FR-MODEL-3), and the generated model document names it as an authored decision. Auto-detected structure entering a rating basis unreviewed is precisely the overfitting route this refuses. *Amended 2026-08-23 (W6b slice-map backlog item 3): the clause "with its exposure share and its holdout lift" is **withdrawn**. A candidate carried its SHAP interaction strength alone while OQ-MODEL-31 was open, because neither withdrawn number was ever a measurement.* **Decided 2026-08-23 (OQ-MODEL-31): what stands beside a candidate is its holdout strength ratio** — the same statistic recomputed on the holdout and published against the in-sample value, so a pair that is a fitting artefact shows as a collapse (FR-MODEL-128). Until that lands the artifact publishes strength alone, which is truthful and is not a resting place. **A per-pair exposure share is `1.0` by construction**: every row of the frame has a value for both features of a pair, so the cross of their observed cells is the whole book — `ShapInteraction.exposure_share` is a literal `1.0` at its construction site and a default of `1.0` on its type, and it could not have been anything else. The disanalogy with a partial-dependence point (FR-MODEL-125) or a worst region (FR-MODEL-36) is structural rather than incidental: those are *per level* and their shares partition exposure, while a candidate is one object covering the entire frame. **Holdout lift is defined in no section of this suite**, has no field on any shape and no computation anywhere; it has been an unbacked promise since 2026-08-15. What OQ-MODEL-4 decided is untouched — candidates are suggestions, never additions, and the detection stays. Removing the constant field from `ShapInteraction` is **W32**'s, and until it lands the artifact publishes a number that means nothing. *Landed 2026-08-24 (W32-9): `ShapInteraction.exposure_share` is deleted from the shape, its producer, the hand-authored contract and the drift guard's reached-path list, so the artifact now publishes `strength` alone; the withdrawn clause above is satisfied by removal, not by computation. FR-MODEL-128 remains unbuilt.* |
| **FR-MODEL-36** | The transparency artifact records an explicit **fidelity statement**: how well the approximation reproduces the model, where it does not, and the exposure share of the region where it does not. A Rating Version referencing the model surfaces this at approval time. *Amended 2026-08-23 (W6b slice-map backlog item 3): the region's share is a share of **exposure** — the same quantity FR-MODEL-125 names — and the implementation counts rows (`mask.sum() / rows` at the `worst_regions` construction site). The spec is the correct side and the code is the wrong one; this is the site FR-MODEL-125's sweep of the same defect did not reach, one file away from the four it did.* **Declared and unfixed, owner W32.** On a motor book a level held for a fortnight then reads as a region of the same size as one held for a year, and stating how much of the book the approximation is wrong over is the whole purpose of the sentence the share appears in. |
| **FR-MODEL-96** | **The GLM approximation of a GBM is persisted as a Model in its own right; the transparency artifact references it by `approximating_model_id` and stops carrying its coefficients inline.** (OQ-MODEL-10, decided 2026-08-18; **owner Phase 1b, and before anything references a transparency artifact by identifier**.) The argument is `03` FR-RATE-60's: an `approximation`-mode Rating Version pins what it rates on, FR-OVR-14 requires every pin to resolve to an artifact whose status is `approved` or better, and a `TransparencyArtifact` carries `model_id` and **no status at all** — so the thing that is rated on must be an artifact that has one, and only a Model does. Three obligations follow, and they are the work the answer creates rather than reasons against it: (i) the approximating Model's spec records `approximates_model_id`, and its `dataset_version_id` is the population the approximation was fitted over, so a reader can tell a surrogate from a model fitted on observed claims; (ii) that field joins the `spec_hash` payload and increments `n` with it (FR-MODEL-86); (iii) §4.8's `status ≥ fitted ⟹ diagnostics_id` is met by diagnostics **of the surrogate against the source model's predictions** — the quantity FR-MODEL-36 already measures — recorded as such, never presented as diagnostics against observed claims. Until it is built, `approximating_model_id` stays `None` and the artifact carries the coefficients: declared-and-unbuilt in FR-MODEL-87's sense, with this requirement as the trigger. *(Amended 2026-08-19, W5, building FR-MODEL-96.* **Built.** The trailing sentence above and the **owner Phase 1b** parenthetical describe the state before this date and no longer describe the platform. The three obligations are discharged: (i) `approximates_model_id` lives on `GlmSpec`, and FR-MODEL-102 makes a surrogate identifiable from its spec alone; (ii) the field joins the `spec_hash` payload, which moves `v4` to `v5` with it (FR-MODEL-86); (iii) §4.8's `status ≥ fitted ⟹ diagnostics_id` is met by the surrogate's diagnostics against the source model's predictions. The artifact's inline `coefficients` and `relativities` survive as a legacy era for artifacts written before this date, exclusive at the type with `approximating_model_id`, rather than as the current state.)* |
| **FR-MODEL-110** | **On a rebuild, the transparency Job reuses the surrogate's stored numbers instead of recomputing them** (OQ-MODEL-17, decided 2026-08-21). `model.transparency` branches on `reserve_model`'s `should_fit` before `build_glm_approximation` and `compute_diagnostics`; on `False` it loads the existing surrogate's `Diagnostics` and the latest `TransparencyArtifact`'s `glm_approximation` block (`r_squared`, `deviance_explained`, `worst_regions`) rather than paying a full GLM fit plus one type-III refit per factor for numbers it then discards. No new invariant is needed: the source Model and the surrogate's own spec are both immutable once fitted, so `spec_hash` (FR-MODEL-66) already guarantees the numbers a rebuild would recompute are identical to the ones stored at the first build — and FR-MODEL-36's fidelity argument for recomputing only bites if the source model could change between builds, which it cannot. ~~**Owner: Phase 1b, and the trigger is its measurement of the transparency Job's cost against `07`'s job-latency NFRs**, before which this is the kind of cost a measurement would attribute to the wrong cause.~~ **Built 2026-08-22 (W5, the closure slice), and amended in one clause by building it.** *(i)* **Discharged early**, because the closure audit found the gap rather than a measurement triggering it: the requirement was specified 2026-08-21 and the branch it describes was never built, while the roadmap recorded it as "Delivered but untested — a marker is owed, not a feature". That verdict was false on both counts; a call-counting test on the pre-change handler shows **`build_glm_approximation` and `compute_diagnostics` both running** on the rebuild. *(ii)* **The `Diagnostics` clause is amended: the branch *skips* that compute, it does not *load* it.** The `glm_approximation` half is exactly as specified and is implemented — all three named numbers are carried by the stored block. The `Diagnostics` half is not implementable as a load: `compute_diagnostics`' result is consumed at exactly one place in the handler, the `Diagnostics(...)` argument to `record_fit`, which is itself inside the `should_fit` branch. On the reuse path nothing downstream reads it, so loading it would be a query whose result is discarded — the same defect this requirement exists to remove, one table smaller. The surrogate's stored `Diagnostics` are already correct, already persisted and already reachable; nothing in this Job needs to read them. *(iii)* **A rebuild is cheaper, not free.** This requirement names two calls and gates only those: `build_shap_summary` still runs on every build, and the load still reads both split frames and the booster blob. "Reuses stored numbers" must not be read as "a rebuild is free". *(iv)* **It removed a correctness argument as well as a cost.** Before the branch, the artifact's numbers came from the fit just computed while the Model it cited held the first one, and the two agreed only because `fit_glm` is deterministic under `spec.seed`. The numbers are now literally the stored ones, so the artifact cannot disagree with the Model it names even if that determinism ever broke — which is a stronger property than the cost saving this requirement was raised for. *(v)* **Two guards the requirement does not mention and the code needs**: `should_fit=False` says the surrogate is fitted, not that an artifact exists carrying its numbers, nor that the latest artifact for the source model names that same surrogate. The handler refuses to reuse in both cases and fits instead. Neither should be reachable, since the fit and the artifact are written in one transaction — but "should be unreachable" is not a licence to cite whatever is there. |
| **FR-MODEL-84** | **A transparency artifact is readable.** `GET /api/v1/models/{id}/transparency` returns the model's most recent artifact, or a 404 naming the model. Added 2026-08-17 (W5, the transparency slice): §5.1 declared the `POST` and no read, which is a 202 whose artifact nothing can fetch — complete to the endpoint audit, since that compares the spec against the contract and an endpoint missing from both is invisible to it, and unusable to every caller. The same omission `01`'s reference publish lifecycle made, and the one the comparison artifact carried until FR-MODEL-56 was built. A model may hold several artifacts (FR-MODEL-33 allows several forms, and a re-sampled SHAP summary is a second artifact rather than a correction); the route returns the latest, and an approval citing a specific one resolves it by id. |
| **FR-MODEL-37** | EBM (`interpret`) models are treated as transparent by construction: their term shape functions are exported directly as tables and require no approximation, but they still carry the fidelity/diagnostic sections in the same contract shape. |
| **FR-MODEL-102** | **A surrogate is identifiable from its spec alone.** Added 2026-08-19 (W5, building FR-MODEL-96). `GlmSpec.approximates_model_id` is set **if and only if** `response_column` is the reserved surrogate column `__gbm_prediction__`, refused at the type in both directions. A spec that named a source model while pointing at an observed response column would describe a model fitted on claims and read as a surrogate; one that fitted the reserved column while naming no source would be a model of a prediction nobody can identify. This is also what makes FR-MODEL-96(iii) enforceable without a second field: the A/E in the surrogate's `Diagnostics` is against the source model's predictions because the spec the diagnostics were computed under says so, and `CLAUDE.md` §2's rule against a fact stated twice keeps it there rather than copied onto the diagnostics document. Two consequences are stated rather than left to be discovered: a surrogate Model **carries no `covariance_blob`**, so FR-MODEL-93's typed absence is what a prediction against it reports — an interval computed from a surrogate's coefficients describes the surrogate and would be read as the GBM's uncertainty; and a surrogate **appears in `GET /api/v1/models`** like any other Model, which is the point of FR-MODEL-96 rather than a side effect. **The name it appears under is fixed too, added 2026-08-19 (fix round, W5):** the surrogate's `model_family_slug` is the source model's own family slug with `-approx` appended, and `models.model_family_slug` is a `String(64)` column — a source slug that leaves no room for that suffix within the 64-character limit is refused by name, naming the slug and the length it would have produced, before the transparency Job spends any compute fitting it. |

### 3.7 Custom objectives

| ID | Requirement |
|---|---|
| **FR-MODEL-38** | A **Custom Objective** is a named, versioned artifact of `kind` ∈ `template` \| `expression`. It is defined once and reusable across Models, Model Families, and backends. |
| **FR-MODEL-39** | `template` objectives are parameterised standard forms with analytic gradients and hessians implemented and unit-tested in `pricing-core`. The shipped catalogue is in §4.5. A template objective carries no user code at all. |
| **FR-MODEL-40** | `expression` objectives let the user write the **per-observation loss** `L(y, f, w)` (where `f` is the raw score / linear predictor) in the restricted grammar of §4.6. The gradient and hessian are derived **symbolically at authoring time** (SymPy), stored as expressions in the artifact, reviewed as part of approval, and compiled to vectorised NumPy/Polars at fit time. User code is never executed at fit time; only the platform's own compiled expression tree is. **Unevidenced, and correctly so — verdict recorded 2026-08-23 (W32-6): deferred, owner Phase 2.** Nothing in the repository derives a gradient symbolically, because FR-MODEL-75 gates the whole `expression` kind off for Phase 1; the only code path naming this requirement is the `/derive` route, which exists to *refuse*, and that refusal is FR-MODEL-75's evidence rather than this requirement's. Recorded because W32-6's plan named FR-MODEL-40 as "backtest results" and would have hung the new backtest endpoint tests on it — a marker on a requirement no line of this repository satisfies, which reads as coverage and is the "a marker is a claim, not a proof" failure `CLAUDE.md` §13 names. The backtest requirement is FR-MODEL-57. |
| **FR-MODEL-41** | The restricted grammar admits only: numeric literals, the bound symbols `y`, `f`, `w`, declared parameters, arithmetic (`+ - * / **`), and the whitelisted functions `log`, `exp`, `sqrt`, `abs`, `min`, `max`, `clip`, `where`, `log1p`, `expm1`. No names, attributes, calls, comprehensions, loops, conditionals, or indexing beyond `where`. AST nodes are capped (default 200). Parsing is by explicit AST walk with an allow-list, never `eval`. |
| **FR-MODEL-42** | Every objective must pass the **Objective Certificate** checks of §4.7 before it can be submitted for approval: symbolic-vs-numeric derivative agreement, hessian non-negativity over the sampled domain, boundary/finiteness behaviour, and a smoke fit on a synthetic dataset that recovers known parameters. The certificate is persisted and attached to the approval request. |
| **FR-MODEL-68** | The derivative-agreement check must **exclude sampled points within the finite-difference step `h` of a `Piecewise` branch boundary**, and report the excluded count. A central difference straddling a kink is invalid, so without this exclusion the check fails every `where()`-based objective for a reason that has nothing to do with correctness (verified empirically — see [`research/track-a-findings.md`](../research/track-a-findings.md) F3). |
| **FR-MODEL-69** | Branch boundaries are themselves a **reported finding**, not merely an exclusion: the certificate records where the gradient or hessian is discontinuous and over what share of the sampled domain. A discontinuous hessian affects boosting stability and an approver must see it. |
| **FR-MODEL-70** | Derivative-agreement tolerances are **step-aware**. Truncation error alone reaches ~4e-04 at `h = 1e-6` on a steeply-curved loss, so a fixed tight tolerance is not meaningful. Richardson extrapolation is used where the loss is smooth; the achieved tolerance and the method are recorded on the certificate. |
| **FR-MODEL-75** | **Phase 1 ships `template` objectives only; `expression` objectives ship in Phase 2** (OQ-MODEL-1, decided 2026-08-15). The `expression` kind is gated by the `expression_objectives_enabled` feature flag (`07` FR-PLAT-45/46), which defaults to off and stays off for the whole of Phase 1: `POST /custom-objectives` with `kind: expression` and `POST /custom-objectives/{id}/derive` are refused with `OBJECTIVE_KIND_NOT_ENABLED` rather than accepted and left uncertifiable. Nothing in §4.6 is withdrawn — the grammar is specified, and its parser is already built and in use for `01` FR-DATA-10 — so what Phase 2 adds is the symbolic derivation, a **second compilation target** (vectorised gradient and hessian kernels, where the existing parser emits Polars expressions), and the review path for a user-authored loss. **Evidenced 2026-08-23 (W32-6), and the prior evidence corrected.** The test claiming this requirement asserted `status_code in (403, 409)` while granting the caller nothing. `FitModels` is a route dependency, resolved before the handler body, so the 409 arm was unreachable — and a disjunctive assertion cannot fail when the wrong one of the two statuses arrives. The requirement's actual subject, *what this platform will and will not derive*, was therefore untested while reading as covered. Split into two tests, each observing one refusal: the 403 for a caller without `model:fit`, and the 409 `OBJECTIVE_KIND_NOT_ENABLED` for one who has it. Proven load-bearing by changing the raised code and watching the second test fail on `["code"]` while the status stayed 409 (§13 rule 4). The create path's `kind: expression` refusal is covered beside it, with the accepted-kind permit alongside. |
| **FR-MODEL-76** | **The certification machinery of §4.7 is built in Phase 1, against templates** (OQ-MODEL-1). FR-MODEL-42 is not weakened for templates: every Custom Objective version carries an `ObjectiveCertificate` before submission whatever its `kind`. One check substitutes — for `kind: template` the derivative-agreement check compares `pricing-core`'s **analytic** gradient and hessian against the numeric derivative (`analytic_vs_numeric`), where an `expression` objective compares the SymPy-derived form (`symbolic_vs_numeric`). Finiteness, convexity, branch discontinuity (FR-MODEL-68/69), step-aware tolerance (FR-MODEL-70) and the smoke fit are identical for both kinds. Expressions therefore arrive in Phase 2 as a new front end onto proven machinery, not as a new subsystem certified for the first time by its riskiest input. |
| **FR-MODEL-43** | A non-convex objective (hessian negative anywhere in the sampled domain) is not refused outright — some legitimate pricing losses are non-convex — but is flagged `convexity: violated`, requires the hessian clipping strategy to be declared (`clip_to_min`, `abs`, `gauss_newton`), and requires an additional Approver. |
| **FR-MODEL-44** | Objectives declare their **applicability**: which responses (`claim_count`, `claim_severity`, `burning_cost`, …), which backends (`xgboost`, `lightgbm`, `glm`), whether an offset is required, and the valid range of `y`. A Model Spec pairing an objective with an inapplicable response is refused at spec validation, before any compute is spent. |
| **FR-MODEL-45** | Custom eval metrics (`feval`) follow the same lifecycle and grammar as objectives, declared separately so that a metric can be reused across objectives. |
| **FR-MODEL-103** | A **Custom Metric** is its own versioned artifact (`custom_metric:<slug>@<version>`), declared separately from objectives so one metric can be evaluated across many. In Phase 1 it is templates-only, on OQ-MODEL-1's rule: a metric names an `ObjectiveTemplate` and its parameters, and its value is that template's loss evaluated as an exposure-weighted mean. It carries no `hessian_strategy` and no `hessian_min` — a metric is never differentiated, and a field that is structurally meaningless is worse than an absent one. |
| **FR-MODEL-104** | A Custom Metric declares its `direction` — `lower_is_better` or `higher_is_better` — and early stopping reads it rather than inferring one. A metric whose direction is guessed stops the fit at the wrong round in exactly half of cases, and produces a fitted model rather than an error. |
| **FR-MODEL-105** | A Custom Metric carries a `MetricCertificate` before submission, on FR-MODEL-42's argument: a metric that early-stops a fit decides when boosting halts and therefore changes the model. Its checks are `finiteness`, `direction_holds`, `scale_behaviour` and `smoke_evaluation`. §4.7's derivative and convexity checks are **absent, not `not_applicable`** — a metric has no gradient or hessian to compare, so the question is not askable rather than unanswered. The check vocabulary (`CheckStatus`, `SamplingSpec`, `CertificateOutcome`, and `CertificateResult.outcome_of`'s derivation of `overall`) is shared with §4.7 unchanged. |
| **FR-MODEL-126** | *(appended 2026-08-23, OQ-MODEL-30)* **The check count is the artifact's obligation, not the container's.** `CertificateResult` is shared by `ObjectiveCertificate` and `MetricCertificate` and stays **unbounded** — a floor on the shared type is either wrong for one artifact or wrong for both. The counts belong where the artifacts are declared: an objective certificate carries **all nine** §4.7 checks, always, including `branch_discontinuity` (FR-MODEL-69), and a metric certificate carries the **four** of FR-MODEL-105 — each enforced on its own type, so a certificate that is short of its battery cannot be constructed rather than being caught by a reviewer. The published contract states the same floor it enforces: `objective-certificate.result.checks` is `minItems: 9`. *Its `minItems: 8` was a pre-amendment count that the 2026-08-18 amendment left behind while adding the ninth check to the same file's `name` enum — stale, not a second opinion.* **A short battery is a failure of the run, never a silently smaller certificate**: nine checks are what an approver is told they are reading, so if one cannot be evaluated the certificate does not exist. |
| **FR-MODEL-106** | `GbmSpec.eval_metrics` is **honoured**: `kind: builtin` names are passed to the backend's own metric vocabulary, and `kind: custom` refs are resolved by the backend and handed to `pricing-core` as artifacts (ADR-0001). A ref that does not resolve, names a metric whose applicability excludes the spec's response or backend, or names one whose status is outside `FITTABLE_METRIC_STATUSES`, refuses the fit before any boosting round. *(Recorded 2026-08-19: the field was declared from Phase 0 and read by nothing — a spec accepted, silently ignored, and reported to the caller as configured.)* *(Amended 2026-08-20: honouring the field put a second metric beside the stopping one for the first time, and LightGBM's `first_metric_only=False` then halted the fit as soon as **any** of them stalled — a stricter rule than the spec states, reached by omission. What early stopping binds to is FR-MODEL-107's.)* |
| **FR-MODEL-107** | Early stopping on a **Custom Metric** is supported under a custom objective. `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` narrows to its true scope: a **builtin** metric under a callable objective, where both backends hand the metric the raw score rather than the transformed prediction, so the metric it stops on is not the metric it names. *(Amended 2026-08-20: early stopping binds **explicitly** to the metric the spec names, on both backends and whether that metric is builtin or custom — XGBoost through `EarlyStopping(metric_name=, data_name=)`, LightGBM by ordering the stopping metric first and narrowing to `first_metric_only`. Both libraries' shorthands choose positionally, so a spec naming a builtin stopped on a declared Custom Metric under XGBoost and on whichever metric stalled first under LightGBM: one spec, two backends, two answers. One consequence is pinned rather than hidden — LightGBM evaluates builtin metrics before `feval`'s, so a spec that stops on a Custom Metric **and** declares a builtin for the curve does not get the builtin reported, because reporting it would put it at position 0 and drive the stop.)* *(Amended 2026-08-21, OQ-MODEL-21 decided: the pinned consequence is no longer merely named — the drop is recorded on the fit result, FR-MODEL-111.)* |
| **FR-MODEL-111** | **A declared eval metric that a backend could not evaluate is recorded on the fit rather than silently absent** (OQ-MODEL-21, decided 2026-08-21). When LightGBM early-stops on a Custom Metric, its builtin metrics are evaluated before `feval`'s and a declared builtin is dropped; the fit now says so: `GbmFit` and the persisted `GbmFitResult` gain `dropped_eval_metrics`, naming each declared metric that was not evaluated and why — the one reason that exists today: the backend evaluates builtin metrics before the stopping metric (FR-MODEL-107). The spec stays accepted: FR-MODEL-106's objection is to a spec "reported to the caller as configured" when it was not, and the cheapest honest fix is to tell the caller rather than refuse a fit that is otherwise valid, or punish a portable spec for one backend's evaluation ordering. **Owner: W5**, as the custom-metrics slice record already assigns; the field and its contract change land before W5 closes. *(Amended 2026-08-22, W5, building this requirement.* **Built.** *`DroppedEvalMetric` (`name`, and `reason` from a closed set whose one member is `builtin_evaluated_before_custom_stopping_metric`) and `GbmFitResult.dropped_eval_metrics` carry it; `_fit_lightgbm` populates it from the same `_builtin_eval_metric_names` list the non-stopping arm passes to `params["metric"]`, and `_fit_xgboost` returns empty because it evaluates both lists. One correction to the wording above: the field is on `GbmFitResult` and **not** additionally on `GbmFit`. `GbmFit.result` is the `GbmFitResult`, so callers reach it as `fit.result.dropped_eval_metrics`; a second copy on the wrapper would be a field that can disagree with itself. `eval_curve` sits on `GbmFit` for the opposite reason — FR-MODEL-52 makes it a diagnostic and it is deliberately not persisted — which is what made "both" look symmetric when this requirement was written. The persisted shape is the generated contract's `DroppedEvalMetric` definition in `docs/contracts/schemas/generated/model.schema.json`; §4.8 carries `fit_result` examples for GLM and EBM but has never carried one for a GBM, so there was no example to extend.)* |
| **FR-MODEL-108** | A Custom Metric is readable and governable over the API: create, read, certify, read the certificate, submit for approval, and list usage — FR-MODEL-95's argument applied to metrics, since an approver who cannot fetch the certificate is being asked to approve a verdict they cannot see. |
| **FR-MODEL-46** | Custom Objective lifecycle is `draft → certified → review → approved → deprecated`. Approval is by an Approver who is not the author; `expression` objectives with `convexity: violated` need two Approvers (FR-MODEL-43). Editing an `approved` objective creates a new version requiring fresh certification and approval. |
| **FR-MODEL-47** | Objective usage is fully traceable: for any objective version, the platform lists every Model, Rating Version, and live Deployment using it — the blast-radius query needed when a defect is found. |
| **FR-MODEL-48** | Objective execution is resource-bounded: compiled expressions are evaluated on fixed-size NumPy arrays with no allocation of unbounded intermediates, wall-clock is budgeted per boosting round, and NaN/inf appearing in a gradient or hessian aborts the fit with a named error identifying the round and the offending input range. |
| **FR-MODEL-95** | **A Custom Objective and its certificate are readable.** `GET /api/v1/custom-objectives/{id}` returns the objective with its status, its certificate outcome and its `approval_request_id`; `GET /api/v1/custom-objectives/{id}/certificate` returns the latest `ObjectiveCertificate` for that version, or a 404 naming it. Added 2026-08-18 (W5), because §5.1 declared five write endpoints and no way to read what they wrote: FR-MODEL-42 makes a certificate the condition of submission and FR-MODEL-46 puts an Approver in front of it, and an approver who cannot fetch the certificate is being asked to approve a verdict they cannot see. Certification is a **202** job (FR-MODEL-42), so a caller that cannot read the result back has no completion signal either. **Evidenced 2026-08-23 (W32-6).** The prior evidence was one OpenAPI-presence assertion over all seven routes — the paths are spelled correctly. `backend/tests/test_custom_objectives_api.py` now covers the create/get/usage/certify/submit permits, both workspace boundaries, four permission refusals and the three conflicts. **Three things the slice's plan expected are not what the code does, and the code is the correct side in all three:** *(a)* **there is no list route** — seven routes and none of them lists, so the boundary is proven on `GET /{id}` and on `GET /{id}/usage`, the latter being the one whose leak would be a set of another workspace's models; *(b)* **re-certifying an objective already `certified` does not conflict** — `certifiable_or_refuse` admits `{draft, certified}` deliberately, because re-certification after a library upgrade is how a finding is found, and the conflict is `review` and past, where a certificate an approver is reading would move under a live decision; *(c)* **`_require_evidence` guards `submit`, not `certify`** — certification *produces* the evidence, so requiring it beforehand would be circular. **Corrected 2026-08-24 (W32-8).** Point *(a)* went false at commit `799ef78`: `GET /api/v1/custom-objectives` lists the library, so there are **eight** routes and one of them lists. FR-MODEL-127 is what added it — this sentence is the observation that requirement was written to cure, and it is left standing rather than rewritten (`CLAUDE.md` §5), because it records what was true on 2026-08-23 and is the reason FR-MODEL-127 exists. **The evidence the sentence cites is unaffected**: the workspace boundary is still proven on `GET /{id}` and on `GET /{id}/usage`, and `test_the_library_stops_at_the_workspace_boundary` now proves it a third time on the list route, which is the one whose leak would be a page of another workspace's artifacts. Points *(b)* and *(c)* are untouched and still hold. |
| **FR-MODEL-127** | *(appended 2026-08-23, W6b slice-map backlog item 4)* **The three artifact libraries §5.3 renders are listable.** `GET /custom-objectives`, `GET /custom-metrics` and `GET /peril-structures` each return the workspace's artifacts, cursor-paginated, filterable by `status` and by `slug`. Until this date all three had create, detail, certify, submit and usage routes and **no route that lists** — FR-MODEL-95's 2026-08-23 amendment recorded "seven routes and none of them lists" as an observation and cured nothing — so `02` §5.3 asked for three screens whose data no endpoint could supply. This is the same shape as the omissions FR-MODEL-84, FR-MODEL-56, FR-MODEL-90 and FR-MODEL-92 each repaired, and it stayed invisible for the same reason: **an endpoint absent from both §5.1 and the implementation is absent from the audit that compares them.** The `slug` filter is load-bearing beyond the list itself — it is what makes §5.3's `slug@version` addresses resolvable against UUID-only detail routes, so this requirement is a precondition of those views and not only of the library screens. **`usage_count` is on the row**, as §5.3 asks: the count of Model Specs referencing that artifact. `GET /models`' refusal to carry per-row `flags` is a real precedent and it does not reach here — a flag needed a per-row evaluation, a usage count is one grouped aggregate. **The budget is part of the requirement: one aggregate per page, never one per row.** It is stated because the query reads a JSONB spec column with no index today and the metric side needs a lateral expansion, so an implementation that quietly becomes N+1 would be indistinguishable from a correct one until a workspace has a few hundred artifacts. *(amended 2026-08-24, W32 closure proposal Part D items 3 and 4.)* Three clauses above were counterfactual when this row was written; they are corrected here rather than deleted, because which side was wrong is the record. **First**, §5.3 rendered **one** artifact library and not three — the Custom metric library and the Peril structure library were the missing rows, and both were added to §5.3 on this date against routes §5.1 already declared, so the opening sentence now describes §5.3 as it stands rather than as it was. **Second**, the peril side never had a certify route or a usage route: §5.1's peril block is create, list, detail, reconcile and submit, so "all three had create, detail, certify, submit and usage routes" is withdrawn as to Peril Structures and holds for Custom Objectives and Custom Metrics only. **Third**, `usage_count` holds for those same two libraries and not for the peril list. The quantity is defined in this row as the count of Model Specs referencing that artifact, and a Model Spec cannot reference a Peril Structure — the reference runs the other way, a Peril Structure pinning models per §4.10 — so the count is undefinable on a peril row rather than merely unimplemented. §5.1's peril list row omitting it is correct as written, and an implementation must not invent a peril usage count to make the three shapes symmetric. *(A Peril Structure does have a blast radius — `03` FR-RATE-22 pins one per `model_call` — so the absent `/usage` route is a separate question and not evidence for this one.)* Owner: **W32** — backend only, three routes and one shared aggregate. |
| **FR-MODEL-128** | *(appended 2026-08-23, OQ-MODEL-31)* **An interaction candidate carries a holdout strength ratio, and that is the only evidence beside it.** The ranker's `strength` — the mean absolute sum of the pair's off-diagonal TreeSHAP entries — is recomputed on the holdout partition named by the Model Spec's `split_ref` (`01` FR-DATA-36) and published as `holdout_strength_ratio`: the holdout value over the in-sample one. A ratio near `1` says the structure survives out of sample; a collapse toward `0` says the pair is a fitting artefact, which is the one thing an actuary needs before spending a Factor on it. **The two passes are one code path run twice** — the same seed, the same row cap and the same encoding on each partition (FR-MODEL-35) — so the numerator and the denominator are comparable rather than merely adjacent, and the cost is bounded by that cap rather than by book size. The holdout frame is already loaded beside the training frame wherever the summary is built, so this adds a second pass over a capped sample and no new data path. It is **XGBoost-only**, like the candidates themselves — LightGBM computes no interaction values, and `ShapSummary.interactions_available` already reports that as a capability rather than as an empty list (§8) — and on a rebuild it is reused rather than recomputed, with the rest of the surrogate's stored numbers (FR-MODEL-110). **No threshold is attached to it and nothing else stands beside a candidate**: a ratio is ranked evidence, never an admission test, so FR-MODEL-79's refusal to write a Factor is untouched, and the withdrawn exposure share stays withdrawn because it is `1.0` by construction. "Over how much of the book" is not answerable per pair at all and is not asked here. Owner: the slice that builds the factor workbench's suggestion panel; until it lands the artifact publishes `strength` alone and `holdout_strength_ratio` is absent rather than defaulted, which is the interim OQ-MODEL-31 names and not a resting place. |

### 3.8 Diagnostics

| ID | Requirement |
|---|---|
| **FR-MODEL-49** | Every fit produces a persisted **Diagnostics** artifact. Diagnostics are computed once at fit time and read thereafter; the UI never recomputes them. |
| **FR-MODEL-50** | Universal diagnostics (all model types): actual-vs-expected by factor level and by banded continuous factor (exposure-weighted, with CIs); lift/gains curves by predicted decile; Gini / normalised Gini; calibration by predicted decile; residual summaries; overall A/E ratio on train and holdout. *(Amended 2026-08-17, W5. **Double lift is removed from this list** and lives on the comparison artifact, FR-MODEL-56 and §4.11. It was listed here and `PartitionDiagnostics.double_lift` was populated by nothing — nothing could populate it: double lift is pairwise, the comparison model is unknown at fit time, and FR-MODEL-49 makes diagnostics computed once at fit time and read thereafter, so it could not be filled later either. A field that is structurally always null is worse than an absent one, because a reader takes it for a measurement that came out empty.)* |
| **FR-MODEL-51** | GLM-specific diagnostics: deviance, null deviance, AIC/BIC, dispersion estimate, degrees of freedom, per-factor type-III deviance test with p-value, relativity plots with confidence bands, standardised deviance and Pearson residual plots, leverage/Cook's distance on a sample, and a VIF/aliasing report. |
| **FR-MODEL-109** | **An `aliasing` entry is the bare name of a collinear term, and the contract says so** (OQ-MODEL-15, decided 2026-08-21). `GlmDiagnostics.aliasing` stays `tuple[str, ...]`: the field is read by a human deciding which factor to drop, and a name is what they act on — `aliased_with` is recoverable from the VIF report beside it, and the reason for a rank-deficient term is always the same reason. The hand-authored `diagnostics.schema.json` declares the array of strings the model always produced; the divergence pin (`test_the_diagnostics_divergence_is_exactly_the_known_one`) is deleted rather than relaxed, and `diagnostics` joins `COMPARED_SLUGS` so the field is compared like every other. **Delivered 2026-08-21.** The object form `{term, aliased_with, reason}` is not shipped; if W6b's diagnostic view needs those fields, that is a new requirement raised at that point, when the answer stops being a guess about what a reader wants. |
| **FR-MODEL-52** | GBM-specific diagnostics: evaluation curve per iteration for train and holdout, gain/cover/frequency importance, permutation importance on the holdout, partial dependence for declared factors, monotonicity verification (that the fitted response actually respects declared constraints), and tree-count/depth summary. *(Amended 2026-08-22, OQ-MODEL-26 decided — two clarifications, the first of which withdraws half of that question.* ***Scope:*** *"declared factors" means the factors the Model Spec declares, and the sweep already covers exactly those — the worker loads `spec.factors` and passes that list, so "covers every factor where the spec says declared ones" names no gap, because the two sets are the same set. That half is withdrawn rather than fixed.* ***Grid:*** *the per-level grid is bounded by FR-MODEL-118, and neither per-factor block may assume one source column per factor — FR-MODEL-119.)* |
| **FR-MODEL-118** | **A categorical partial-dependence grid is bounded to the most-exposed `max_partial_dependence_levels` levels, defaulting to 20, and the artifact records what it left out. The bound truncates; it cannot pool.** Partial dependence holds a column at one value across the whole book and scores it, so each bar costs a full-population pass and an uncapped categorical costs one pass per distinct level — 10 000 of them for the 10 000-level column NFR-MODEL-3 measures proposals against and this repository has benchmarked, a cost NFR-MODEL-14 prices honestly and does not bound. **Pooling the remainder into an "other" bar is not available, and that is a requirement rather than an omission**: the held value has to be scored, and scoring refuses a level absent from the fitted model's persisted encoding map with `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` because FR-MODEL-32 forbids inventing a code for an unseen level — it would score as whichever level happens to share the number. A synthetic "other" is exactly such a level, so **there is no value the column can be held at** to represent the levels the cap drops. They are therefore named as unswept rather than summarised: `PartialDependence` carries the count of omitted levels, the exposure they hold and the reason, so a reader sees that a curve covers 94 % of the book instead of inferring it from bars that are not there. **20 is not a chart convention.** NFR-MODEL-14 measured 0.0480 fits per scoring pass, so 20 passes is 0.96 of one fit — putting the GBM's per-factor block at the same order as NFR-MODEL-13's budget for the GLM's, one fit wall-clock per tested factor, and leaving a numeric factor's ten quantile points already inside it. **This default binds, where `modelling.max_factor_count` is deliberately unset**: that setting has no platform-wide constant because a large book legitimately supports a large model, whereas no reader legitimately wants 10 000 bars — this cap bounds a chart, not a fit, and changes no fitted coefficient. A workspace-level override is **not built**, and is a requirement to append if a book ever asks for one. **What the cap counts is the levels of the factor's *source column***, because that is what the sweep holds a value in — which for a `banding` or `grouping` factor is not the same as the factor's own levels, and the mismatch is a defect recorded in the roadmap with an owner rather than settled inside this requirement. The measurement behind 20 holds at `permutation_repeats = 1`, its default and the only value anything passes; a higher one multiplies the permutation term and the pass accounting behind that figure does not carry the multiplier. (OQ-MODEL-26, decided 2026-08-22.) |
| **FR-MODEL-119** | **FR-MODEL-91's `interaction` arm was delivered for the GLM path only: between 2026-08-18 and 2026-08-22 no GBM could fit a cross at all.** `resolve_factors` **requires** a cross's operands to be supplied — it refuses a cross missing a side — and then gives them no term of their own, because the cross spans every cell and designing on both it and its operands is a rank deficiency dressed up as a richer model. One root cause, in a single line of difference: `fit_glm` builds its design by iterating the resolved **terms**, so operands never reach it, while the GBM encoder iterated the **factor list** and so raised `KeyError` on the first operand. Two further sites sat behind that one, masked by it: permutation importance and the partial-dependence sweep each open by taking `factor.source_columns[0]`, which an `interaction` — required to name none — makes an `IndexError`. The operands are always there to be tripped over: the backend appends an interaction's operands to the spec's factor list transitively before loading them. And the failure was **unmapped as well as fatal** — a bare `KeyError` is none of the fit errors the model job handler catches, so the job died carrying no platform error code for a reader to look up. All three went unseen because **only the GLM suite ever fitted a cross**; the GBM suite covers `interaction_constraints`, a backend feature-grouping parameter of a similar name and no relation. **Resolved in the direction the GLM path already ran**: the encoder skips a factor with no term of its own, which makes FR-MODEL-91 true on both paths and is the smaller change; and until OQ-MODEL-28 settles what a cross should report, the two per-factor blocks skip it and **record the skip** — partial dependence emits the factor with no points and the omission reason FR-MODEL-118 adds, permutation importance omits it as it already omits a factor whose column the holdout lacks. Skipping is the interim and not the answer: a cross that no per-factor diagnostic describes is a gap a reviewer must be able to see, which is why it is recorded rather than silent. Owner W30. (Found 2026-08-22 while deciding OQ-MODEL-26.) *(Amended 2026-08-22, OQ-MODEL-28 decided: **the interim recorded here does not hold on a sparse cross, and skipping the cross was the smaller half of what had to be skipped.** Skipping the cross stops the `IndexError`, but its operands stay in the list and are permuted and swept *individually*, which recombines them into cells the fit never saw — so the diagnostics raise instead. FR-MODEL-122 measures it and states the remedy; FR-MODEL-121 states what the cross itself reports.)* |
| **FR-MODEL-121** | **An `interaction` Factor's permutation importance and partial dependence are measured on the cross itself, through a *joint* operation over its operands' source columns — the operands being the only path to a term that has no column of its own.** Permutation shuffles every operand source column **under one shared order**; partial dependence holds them **together at one observed cell**. This is measured, not argued: a joint shuffle leaves the observed cell set identical — `{(coastal, hybrid), (rural, petrol), (urban, diesel)}` before and after — because permuting the operands as a unit permutes the *pairs*, which is exactly a permutation of the resolved cross column, and it moved 67.8 % of holdout predictions, so what it yields is a real degradation and not a null one. Checked a second way, the **encoded design matrix** a joint shuffle produces is element-wise identical to the fitted one re-indexed by the same permutation, on a dense cross and a sparse one alike — and it stays **one column wide**, so a joint shuffle re-introduces no operand main effect and FR-MODEL-91's collinearity argument does not reach it. That argument reaches only a *refit* carrying operand columns, which is a third operation this requirement does not perform. **The grid is the cross's observed cells and never the operands' Cartesian product.** FR-MODEL-91 makes only observed combinations levels, and a pair the fit never saw has no code in the persisted encoding map: on a book carrying the diagonal alone, holding `(rural, diesel)` is refused `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` where `(rural, petrol)` scores — FR-MODEL-32's wall, met the second time after FR-MODEL-118's pooled `other` bar died against it. So the two candidate readings are **not** alternatives on the permutation half and are on the sweep half: a joint shuffle and "permute the combined column" are the *same operation*, because `predict_gbm` re-resolves the cross from raw columns on every call and there is no combined column to reach directly, while "the grid of operand pairs" and "the cross's own cells" differ by exactly the unobserved cells FR-MODEL-32 refuses. FR-MODEL-118's cap applies unchanged and earns no special case: it bounds the most-exposed *observed* levels and does not care how a level arose, and the count it bounds is the observed one, which FR-MODEL-91 already holds far below the product of the operands' level counts — three cells of nine on the book measured here. Owner W30. (OQ-MODEL-28, decided 2026-08-22.) |
| **FR-MODEL-122** | **An interaction's operands are skipped by both per-factor GBM diagnostics blocks with the skip recorded — and until they are, a GBM declaring a *sparse* cross cannot produce diagnostics at all.** FR-MODEL-119 left the cross skipped and its operands swept, on the reading that an operand costs a full scoring pass for a term the booster has no column for. **The cost is not the defect.** Measured 2026-08-22: a cross of two three-level columns populated on the diagonal only — 3 observed cells of 9, which FR-MODEL-91 says is what a real cross looks like — fits cleanly, reports `('area_x_fuel',)` as the booster's entire feature order, and then dies inside `compute_gbm_diagnostics` with `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` naming all six cells it never saw. The mechanism is the one FR-MODEL-121 turns to the platform's advantage, run the wrong way round: permutation shuffles an operand's column **alone**, which recombines the operands into pairs the fit never saw — three observed cells become nine — and the sweep does the same by holding one operand while the other varies. Both are refused at encoding by FR-MODEL-32. It reaches production, because `load_factors` returns `ordered + operands`, so every spec naming a cross carries its operands into diagnostics; and the raise lands at the `compute_gbm_diagnostics` call, **outside** the block that maps a `GbmFitError` to a platform error code, so the job dies uncoded — the same reader-facing failure FR-MODEL-119 recorded for the bare `KeyError` and believed it had removed. It survived a second time for the reason it survived the first: the only cross in the suite is drawn from two independent columns, so every cell is populated and no shuffle there can produce an unseen pair. Skipping the operands aligns the GBM path with FR-MODEL-51's type-III block, which already excludes an operand (FR-MODEL-91), and it removes a raise rather than merely saving a pass. **The alignment is only half of one, and the remaining half runs the other way**: the type-III block says why it skips in a code comment and in FR-MODEL-91, and records nothing — `TypeIIITest` is frozen with `factor`, `deviance_delta`, `df` and `p_value` and has no field an omission could occupy — so a reviewer reading a GLM's diagnostics cannot see that operands were excluded at all, where FR-MODEL-118 gave the GBM's sweep a `PartialDependenceOmission` precisely so that a reader would. A skip that only the source states is the silence the omission model was added to end, and it is now the GLM path carrying it. Owner W30, with the rest of this slice. (Found 2026-08-22 while deciding OQ-MODEL-28.) |
| **FR-MODEL-123** | **`spec.seed` is the only seed a fitter reads, and no fitting function takes a `seed` argument** (OQ-MODEL-29, decided 2026-08-22 at option (b)). `fit_glm` and `fit_ebm` each declared `seed: int = 0` and neither read it: `fit_glm` constructs `GeneralizedLinearRegressor` with no `random_state` and passes `spec.seed` — not the argument — into the CV path, and `fit_ebm`'s estimator takes `random_state=spec.seed`. `fit_gbm` never had the parameter and already read `spec.seed` directly, so two of the four fitters carried a knob that did nothing while the other two did not. **The reason it must be the spec's seed and not an argument is NFR-MODEL-6**: the seed is part of what `spec_hash` pins (FR-MODEL-66), so the spec alone must reproduce the fit. An argument-supplied seed would sit *outside* the digest, and two fits with identical `spec_hash` could then differ — which is the precise thing NFR-MODEL-6 forbids, and the ground on which `GlmCvSpec` had already refused to carry a second seed of its own. **Removed rather than documented**, which was the interim option: the parameter had no reading under which it was correct, `02` §5.2 published it, and twenty call sites passed it — **seven of them outside tests**: both fitter calls in the platform's own worker (`fit_glm` and `fit_ebm`), the type-III reduced refit in `diagnostics`, the GBM surrogate fit in `transparency`, and three in `bench-model.py` — so every one of them believed in a knob that did nothing. Five test sites passed `seed=1` against a spec seed of `0`, a disagreement silently discarded and unobservable only because none of the five enabled CV; the first caller to pass a divergent seed *and* turn CV on would have got a silently different fit. **The removal is a breaking change to a published signature and is recorded as one** — it is not a tidy-up. Pinned by a negative test asserting that `seed=` is refused with `TypeError`, because a parameter that has been deleted and a parameter that is ignored are indistinguishable to a caller until one of them raises. |
| **FR-MODEL-124** | An EBM prediction is served, and states `model_type_has_no_interval` as its reason for carrying no interval. Added 2026-08-23 (W32-4). FR-MODEL-37 made an EBM storable and §5.2's `predict_ebm` made it scoreable; between 2026-08-21 and this date the endpoint refused every EBM with `MODEL_TYPE_UNSUPPORTED`, a decision recorded in a docstring and in the roadmap and in no requirement. The reason is a fifth member of `UnavailableReason` rather than a reuse of the four FR-MODEL-77 and FR-MODEL-93 define, because each of the four states something false of an EBM: the three interval-model reasons all presuppose a quantile pair, which `EbmSpec` cannot declare because `interval_for` lives on `GbmSpec`, so a reader told that no interval models were fitted is told to do something the schema forbids; and `covariance_not_stored` says inputs that existed were not kept, where an EBM has no covariance matrix at any point in its life and no refit produces one. R5 is satisfied by an explicit statement of why, and a reason that misdescribes the cause is not one. The blanket refusal is narrowed rather than deleted: `MODEL_TYPE_UNSUPPORTED` still fires where an EBM spec is paired with a fit result of another type, which R2 forbids and which the two independent validating adapters cannot rule out, and it is refused rather than asserted so that it survives `-O`. |
| **FR-MODEL-125** | A partial-dependence point's `exposure_share` is a share of exposure, and the ranking FR-MODEL-118's cap applies is the same quantity. Added 2026-08-23 (W32-5). Between the diagnostics slice and this date all four computations were row counts: the level ranking, the omission record's share, the categorical point's share, and the numeric point's share — the last of which was the constant `1.0 / len(labels)` and so not a measurement of anything. A row-count share on a motor book ranks a level held for a fortnight beside one held for a year, and an actuary reading the chart has no way to see that it did. Exposure means the weight column the spec declares, or a vector of ones where it declares none, taken from the frame the sweep runs over — which is the holdout, because a curve computed on the holdout must report the holdout's profile. Where the weights sum to zero every share is zero rather than `nan`. The ranking and the emitted share are required to be the same quantity because a chart ordered by one measure and labelled with another cannot be read, and that requirement is the reason all four sites move together rather than only the two a reader would notice. |
| **FR-MODEL-53** | Cross-validation is supported with declared fold construction (`random`, `temporal`, `grouped_by_key`) and a persisted seed; per-fold metrics and their dispersion are persisted, not just the mean. |
| **FR-MODEL-54** | Diagnostics are computed on **train and holdout separately and always reported side by side**. A diagnostic reported without its holdout counterpart is a defect. *(Scope, recorded 2026-08-24 — W6b.* The universal above is honoured where it is expressible and reaches no further, which had been written down nowhere. `UniversalDiagnostics` requires `train` and `holdout` as separate `PartitionDiagnostics`, so a one-sided universal diagnostic is unrepresentable — the strongest form this rule can take. The other four members of the persisted `Diagnostics` artifact — `complexity`, `glm`, `gbm` and `cross_validation` — are **unpartitioned at member level**: each is one object rather than a train/holdout pair. That is a claim about the member and not about everything beneath it, and `gbm` is where the difference bites, since it **partitions internally** at `GbmEvalPoint` as the sentence below sets out. Read instead as *`gbm` has no train and holdout*, it would delete the train-versus-holdout eval curve — the overfitting chart FR-MODEL-52 names, and the one GBM diagnostic that requires the split. The enumeration that settles it, rather than a count: `train` and `holdout` are declared at exactly two sites in the whole contract — `UniversalDiagnostics` (`packages/model-schema/src/model_schema/diagnostics.py:179-180`) and `GbmEvalPoint` (`:272-273`, with a validator at `:277-278` refusing a point that reports neither). `GlmDiagnostics`, `ComplexityDiagnostic` and `CrossValidationDiagnostics` declare neither field. So a view builds **two** partitioned surfaces, not one. **A diagnostic partitions when it measures the fitted model against a population of rows; it does not partition when it is a property of the fit itself** — which terms aliased, variance inflation, Type III tests, split importances, monotonicity, partial dependence, the complexity counts and the cross-validation fold path each hold one value because there was one fit, not because a holdout was omitted. The line is drawn inside a family block and not only between them: `GbmEvalPoint` carries `train` and `holdout` per boosting iteration while the importances beside it carry neither, which is this predicate already applied by the contract. **A third kind is neither of the two**: `permutation_importances` is measured on the holdout by definition — its `degradation` is degradation of the holdout metric — so it is single-valued because a train counterpart would answer a different question, and it is **labelled as holdout** rather than rendered opposite an empty train column. Note that it *is* computed over rows, so the predicate above is about what a diagnostic measures, not about whether rows were touched. A view that renders a holdout column for any of these shows a column nothing can fill, and that hazard is why this was written down.)* |
| **FR-MODEL-55** | Metrics are recorded with their weighting scheme explicit (exposure-weighted vs unweighted vs claim-count-weighted). An unweighted metric on an exposure-weighted problem is labelled as such in the UI. |
| **FR-MODEL-81** | **Model complexity is a diagnostic by default, and a gate only where a workspace asks for one** (OQ-MODEL-6, decided 2026-08-15). Every fit records its factor count, its fitted-parameter count, and its exposure-per-parameter and claims-per-parameter ratios in the diagnostics, beside whatever thresholds are in force. The workspace settings `modelling.max_factor_count` and `modelling.min_exposure_per_parameter` (`07` FR-PLAT-45) are **unset by default**; where a workspace sets one, `POST /model-specs/validate` and `POST /models` refuse a breaching spec with `MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT` before any compute is spent, and the refusal is audited. There is no platform-wide constant: a large book legitimately supports a large model, and whether *this* model is overfitted is a judgement for the Approver with the diagnostic in front of them (`06`), not for a number chosen here. |
| **FR-MODEL-56** | Model comparison is a first-class operation: two or more Models fitted on the same holdout can be compared on aligned metrics, double-lift, and factor-by-factor relativity differences, producing a persisted comparison artifact citable in an approval request. |
| **FR-MODEL-57** | A **backtest** on a later Dataset Version is supported and produces the same diagnostic shapes, marked with the version it ran against. Backtests are the evidence bridge into `05-monitoring.md`. *(Amended 2026-08-18, W5, the backtest slice, with what building it settled.* **A backtest is its own artifact — §4.12 — and `Diagnostics.backtest` is removed.** That field was declared from Phase 0 and typed `null`, and nothing could ever have filled it: FR-MODEL-49 computes diagnostics once at fit time, while a backtest runs later and again for every period after that. It is the same defect FR-MODEL-50's `double_lift` had, found the same way. **"The same diagnostic shapes" means one `PartitionDiagnostics`, not a `UniversalDiagnostics`:** the backtested population was never split, so FR-MODEL-54's both-partitions rule does not apply and calling the single partition a holdout would claim a split nobody made. **"Other than the one it was fitted on" reaches the split parts**, which are Dataset Versions in their own right (`01` FR-DATA-36) — the refusal the type cannot see and the platform must, and it runs *before* the validated gate for the reason §4.12 gives. Both model types are backtested through one path; FR-MODEL-57 says nothing about model type, and a backtest that worked only for GLMs would leave the GBM an actuary trusts least as the one nothing re-measures.)* **Evidenced over HTTP 2026-08-23 (W32-6).** The prior evidence was all platform-layer: `test_backtests.py` never builds a request, so the 202-and-`Location` contract, the read-back shape and both permission gates were unproven. `backend/tests/test_api_backtests.py` covers them. *(The plan for that slice named FR-MODEL-40 as "backtest results" and it is not — see FR-MODEL-40's own row. The markers were corrected to this requirement before the tests were committed.)* |

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
| **FR-MODEL-87** | **§4 is a staged contract: a field is shown live only once a slice populates it, and anything else is named in place with a dated note saying it is declared-and-unbuilt and which workstream owns it** (OQ-MODEL-8, decided 2026-08-17). The alternative — declaring the eventual shape and letting the reader discover which fields are always null — teaches that null means *nothing* rather than *not yet*, and the frontend generates from this contract. At the decision date the residuals are, with verdicts: **absent entirely** — `filter` on `ModelSpec` and `custom_objective_ref` on `GlmSpec`, all owned by Phase 1b; **declared and unbuilt, as §4.8 already says of them** — `transparency_artifact_id` and `custom_objective_ref` on `Model`, owned by W5 and Phase 1b respectively; **present under a different shape** — §4.4's nested `regularisation` block, corrected to `GlmSpec`'s flat fields by this change. Six fields have gone live under this rule already (`banding_id`, `grouping_id`, `split_ref`, `diagnostics_id`, `loss_treatment`, `approval_request_id`); **`interval_for` is the seventh, live 2026-08-19** on `GbmSpec` rather than on `Model` (FR-MODEL-100), and it leaves the absent-entirely list above with this change rather than being quietly dropped from it. **`select_by` and `cv` are the eighth, live 2026-08-21** (the regularisation-and-CV slice), on `GlmSpec` — `select_by: "fixed" \| "cv"` and the nested `cv: GlmCvSpec` block, the shape the FR-MODEL-20/FR-MODEL-53 CV path built rather than the flat `select_by`/`cv_folds` fields the decision date named — and they leave the absent-entirely list above with this change rather than being quietly dropped from it. **Tweedie power estimation — live 2026-08-21 (FR-MODEL-22)**; the estimation × CV-selection pair is refused by name, not built. **`offset_model_ref` is the ninth, live 2026-08-21** (the offset-from-another-model slice), on `OffsetSpec` — `kind: "model"` with the canonical `model:slug@version` ref, GLM-to-GLM only; `GbmSpec` naming it, and refs naming non-fitted, non-GLM or link-mismatched models, are refused by name (`MODEL_OFFSET_REF_INVALID`). **`dropped_eval_metrics` is the tenth, live 2026-08-22** (FR-MODEL-111), on `GbmFitResult` — a tuple of `DroppedEvalMetric`, empty on every fit that evaluated everything it was asked for and on every artifact written before that date, populated only where LightGBM early-stops on a Custom Metric and its declared builtins are suppressed so they cannot take position 0 and drive the stop. **Amended 2026-08-22 (W5, the audit-remediation slice): `transparency_artifact_id` is superseded rather than owed.** It has sat on the residual list as declared-and-unbuilt "owned by W5" since 2026-08-17, and W5 cannot honestly close while owing a field it should not build. **FR-MODEL-96 settled the direction on 2026-08-19**: the link runs artifact → model, `TransparencyArtifact.model_id`, and `02` R3 is enforced by query at the approval transition (FR-MODEL-89) rather than by a column on this side. **The deciding fact is cardinality, not tidiness.** `ix_transparency_model` is `(workspace_id, model_id, created_at)` and is **not unique** — a Model accumulates transparency artifacts as it is re-derived, so a single `transparency_artifact_id` could name only one of them and would be wrong the first time a second was written. A back-pointer that cannot express the relationship it names is not an unbuilt field; it is a **second, lossy source of truth** for a link already stored, which is the defect `GbmSpec.backend` and the duplicated `base_margin` were both refused for on 2026-08-17. It is therefore **struck from the residual list**, the way `PICKLE_PERSISTENCE_REFUSED` was struck from `02` §5.1 on the same day and for the same reason — a declaration nothing should ever satisfy. `custom_objective_ref` is untouched by this and remains declared-and-unbuilt, owned by Phase 2's W30. **The contract keeps the property with a dated note rather than dropping it**, because external consumers have read it since Phase 0 and a silently vanished field is worse than a documented dead one. |
| **FR-MODEL-88** | **The unimplemented arms of FR-MODEL-1's closed set are refused by name at resolution, never approximated.** Four of the eight — `spline`, `polynomial`, `offset` and `expression` — do not resolve, and `resolve_factors` raises naming the type rather than returning the raw column, because a fit built on the raw column is one nobody could tell from a correct one. **`expression` is the sharper case and its verdict is stated rather than implied:** `FactorType.EXPRESSION` is selectable while `Factor` carries no field to hold the expression, so a factor of that type can be *created* and can never be *resolved*. That is contained rather than corrected — the refusal is at the boundary where it would matter — and the field plus its validator arm are owned by Phase 1b with the rest of §4.7's expression work. (OQ-MODEL-8, decided 2026-08-17.) **Amended 2026-08-22 (W5, the audit-remediation slice): the refusals were contained and unowned, which is containment rather than a plan.** Two corrections. **First, `expression`'s owner was stale.** This requirement sent the field and its validator arm to "Phase 1b with the rest of §4.7's expression work" on 2026-08-17, two days after OQ-MODEL-1 had already put expressions in **Phase 2**; FR-MODEL-6's reassignment to **W30** was corrected on 2026-08-19 and accepted by the maintainer on 2026-08-22, so W30 owns it and "Phase 1b" is superseded. **Second, `spline`, `polynomial` and `offset` had no owner at all** — not a deferral, not a workstream, nothing — while a test marking the refusal let all three count among the evidenced. Scheduling them is a change to a set FR-MODEL-1 declared closed in Phase 0, which §14 makes the maintainer's rather than a closing workstream's, so it is raised as **OQ-MODEL-23** with options and a recommendation rather than decided here. Until that question is answered the three are **not started, with the open question as their owner** — which is a verdict §13 rule 1 admits, and silence is not. **Amended 2026-08-22 (OQ-MODEL-23 decided): the three no longer share one verdict.** `offset` is **superseded** (FR-MODEL-114) — its refusal is now permanent rather than pending, and the refusal *message* should say so: `resolve_factors` reads "this build does not resolve yet", which is a promise, and a superseded arm never resolves. `spline` and `polynomial` are **gated on FR-MODEL-115 and owned by W30**, and stay refused meanwhile. The opening count is unaffected: superseding a type does not make it resolve, so four of the eight still do not. |
| **FR-MODEL-114** | **`offset` is superseded as a Factor *type*, and the arm stays in the published contract.** An offset is already declared where a fit declares it: §4.4's `OffsetSpec` carries `none`, `log_column`, `column` and `model`; FR-MODEL-19 makes `log(exposure)` the frequency default; FR-MODEL-24 pins the model-referenced case. A Factor *type* meaning "this column is the offset" would be a second mechanism for something the spec already owns at the layer that owns it — the defect FR-GOV-36's resolver registry was rejected for on 2026-08-22. **The grounds are `OffsetSpec` as a whole, not FR-MODEL-24 alone**, which covers only the model-referenced kind and could never substitute for a column offset. **Superseded means permanently refused, never removed.** `FactorType.OFFSET` stays in `model-schema` and in the generated OpenAPI, following FR-MODEL-87's 2026-08-22 ruling that the contract keeps a property with a dated note rather than dropping it: external consumers have read the enum since Phase 0, artifacts are immutable, and `to_factor`'s `Factor.model_validate` on read turns a stored `offset` row into a `ValidationError` that fails the whole workspace's factor list rather than the one row. This repository's fixtures and seed hold **no such row** — stated because §13 rule 6 requires it to be stated — and the arm stays regardless, because immutability means a deployed one could never be rewritten. **This supersedes `FactorType.OFFSET` and not `FactorIntent.OFFSET`**: two distinct enums spell the same word, and the intent arm is live, selectable and consumed by nothing, which is OQ-MODEL-25 and deliberately not decided here. (OQ-MODEL-23, decided 2026-08-22.) |
| **FR-MODEL-115** | **A continuous Factor must be rateable and reviewable before any continuous basis type is scheduled.** FR-MODEL-21 promises a relativity table for every *categorical* Factor and `03` FR-RATE-16 seeds a rate table from that table, so a continuous term yields a coefficient with no relativity surface: nothing FR-RATE-16 can seed from, nothing §5.3's relativity plot can draw, and nothing FR-MODEL-4's declared direction can be checked against. **This is already live for an `identity` Factor over a numeric column**, which resolves today — it is a gap in what is built, not a property of the unbuilt arms, and it is why neither `spline` nor `polynomial` is scheduled: either would ship a Factor an actuary can fit and cannot price. Before either is scheduled this requirement must deliver: an effect or relativity surface for a non-categorical Factor, evaluated on a stated grid with the derivation Dataset Version recorded, to the standard FR-MODEL-9, FR-MODEL-10, FR-MODEL-83 and FR-MODEL-85 hold a banding's boundaries to; the seeding path `03` uses for it, given that FR-RATE-8 keys a continuous input through a **stored banding artifact** and `03` offers `interpolation: linear` as its only smoothing; a reconciliation with FR-MODEL-97, which on 2026-08-18 refused a continuous product term because the rating DAG is a graph of tables and a varying slope has no cell — a spline main effect is a varying slope, so committing one while that refusal stands would be an unreconciled contradiction inside one spec; and the multi-column consequence FR-MODEL-91 stated for interactions, since `FactorMatrix.terms` maps a slug to one column today and a monotonic direction declared over a multi-column basis is not enforceable by a per-column constraint. Owner **W30**, which already owns `expression`, the third refused arm. (OQ-MODEL-23, decided 2026-08-22.) |
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

> **Amended 2026-08-22 (W5, the audit-remediation slice).** Bühlmann–Straub is now built —
> OQ-MODEL-5 decided on 2026-08-15 that W5 builds *two* methods, and until this date one was
> refused at runtime. Three things the implementation settled:
>
> * **`credibility_components` is `{evpv, vhm, k}` on claim frequency**, with each Level one
>   risk weighted by its exposure years — the same rate limited fluctuation shrinks, so the
>   two theories differ in `Z` and nowhere else. A one-way summary gives **one observation
>   per risk**, so the textbook within-risk estimator of `s²` is `0/0`; the Poisson process
>   variance supplies it instead, `s² = E[λ(Θ)] = μ`, and VHM is the standard unbiased
>   between-risk estimator. That identity is *why* Bühlmann–Straub is estimable from a
>   `OneWaySummary` at all. The components are re-derived from the same source rows the merge
>   shrank on, so the recorded `k` is the one that produced the mapping — which is what makes
>   FR-MODEL-80's "re-derive `Z` rather than take it" literally true, and a test does exactly
>   that from the artifact alone.
> * **`credibility_pk` and `credibility_standard_claims` are limited fluctuation's alone.**
>   Bühlmann–Straub derives no full-credibility standard, and writing the request's untouched
>   `(0.90, 0.05)` defaults onto a `buhlmann_straub` artifact would record a standard that did
>   not run.
> * **A book that cannot support the estimate is refused, not silently shrunk** — FR-MODEL-113.

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

> **The `spec_hash` version lineage, assembled 2026-08-22 and corrected the same day
> (FR-MODEL-86; W5, the closure slice).** This section recorded `v4 → v5` and `v8 → v9`
> beside the fields that caused them and skipped the three transitions between;
> `backend/src/app/platform/modelling.py`'s comment block carried all of them. Recorded here
> so the two agree, in the order they happened.
>
> **The list as first assembled skipped `v3 → v4` itself**, and that is this note's own
> failure mode one level up: a list written to reconcile two records against each other
> omitted a transition *both* of them held — `modelling.py:113` and FR-MODEL-100's row in §3
> each carry it. It is restored to its chronological place below rather than appended, so
> the sequence reads without a gap and nobody infers from the ordering that `v4` arrived
> before `v3`.
>
> - **`v3 → v4`** (2026-08-19, FR-MODEL-100) — `interval_for` joined the payload: a bound's
>   link to the model it bounds is part of that model's identity, so two bounds taken
>   against different central versions must not collide on one digest and be answered for
>   each other by FR-MODEL-66's dedup.
> - **`v5 → v6`** (2026-08-21, FR-MODEL-20/53) — `select_by` and `cv` joined the payload:
>   how a fit is selected, one alpha or a CV scan of `cv.alphas`, is part of the fitted
>   question, and two specs differing there must not share a digest.
> - **`v6 → v7`** (2026-08-21, FR-MODEL-22) — `tweedie` joined the payload: a power
>   estimated over `tweedie.p_grid` is a different fitted question than a fixed one.
> - **`v7 → v8`** (2026-08-21, FR-MODEL-24) — `offset_model_ref` joined the payload: the
>   offset a fit names is part of what that fit means, so a fit against another model's
>   structure must not dedup onto one with no offset.
> - **`v9 → v10`** (2026-08-22, FR-MODEL-19) — **the first bump for an interpretation
>   change rather than a payload one.** `weight` had been in the payload since this block
>   was written; what changed is that `fit_gbm` began honouring it. A `v9:` digest over a
>   weighted GBM spec therefore names a fit this build produces differently, and
>   FR-MODEL-66's dedup would otherwise answer the next caller with an unweighted fit for a
>   weighted spec. Every `v9:` digest is stale and findable with `LIKE 'v9:%'` — including
>   an unweighted GLM's, which the change cannot have affected. That over-invalidation is
>   accepted: a targeted invalidation has no mechanism here, and inventing one is larger
>   than the defect it would spare.
>
> A reader should not conclude from `v1`..`v9` that the tag tracks *fields*. It tracks what
> a digest promises, and `v10` is the case that distinguishes the two.

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

`EbmSpec` adds (`model_type` is `"ebm"`):

```json
{
  "objective": "rmse",
  "interactions": 0,
  "max_bins": 64,
  "max_rounds": 50000,
  "monotone_constraints": {"driver_age_banded": -1, "vehicle_group_rated": 1}
}
```

> **Added 2026-08-21 (W5, the EBM slice, FR-MODEL-37).** The common block is inherited
> unchanged (factors, split, response, weight, seed, loss treatment). `objective` is
> `"rmse" | "mae"`, default `"rmse"`; `interactions` is `0 | 1`, default `0` — `2`
> (triples) is **declared-and-unbuilt** (FR-MODEL-87); `max_bins` defaults to 64 and must
> be a power of two in `[16, 32768]`; `max_rounds` defaults to 50000;
> `monotone_constraints` maps factor slugs to `{-1, 0, 1}`, default `null` — coverage of
> every factor is checked at fit time, not here, because factor slugs resolve at fit time.
>
> **Refused by name, 2026-08-21 (FR-MODEL-87):** §7's families and binomial `log_loss` are
> **declared-and-refused by name** as `objective` values; custom objectives do not apply
> to EBM; `offset` kinds other than `none` are refused by name (offsets stay GLM-only).
> **FR-MODEL-86:** the EBM fields join the `spec_hash` payload and the tag moves `8 → 9`.

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

> **§4.6 measured against the implementation 2026-08-22 (W5, the audit-remediation slice),
> and it diverges in three ways — none previously recorded, and the third is the one that
> matters.** The parser being described is `pricing_core.data.expressions`, built in **W4**
> for `01` FR-DATA-10; §4.6 was written for the Phase 2 `expression` objective grammar and
> has never been checked against it. All three are stated rather than resolved: this is a
> §0 case, and which side is wrong is **OQ-MODEL-1's slice (W30)** to decide, since it owns
> the grammar this section specifies.
>
> * **Neither AST limit is implemented.** No node-count and no depth check exists anywhere.
>   Measured: an expression of **1 599 nodes** is accepted against a stated limit of 200
>   (8× over), and one nested **60 deep** against a stated 20 (3× over). Whether the limits
>   are wanted at all is open — nothing has needed them, and `01`'s expressions are
>   author-written column derivations rather than user-submitted input.
> * **The function sets share only six of ten names each.** §4.6 declares
>   `abs clip exp expm1 log log1p max min sqrt where`; `_FUNCTIONS` provides
>   `abs ceil coalesce exp floor log max min round sqrt`. Spec-only: `clip`, `expm1`,
>   `log1p`, `where`. Code-only: `ceil`, `coalesce`, `floor`, `round`.
> * **The implemented grammar is *wider* in operators and *narrower* in functions, and the
>   one construct §4.6 singles out by name does not exist.** §4.6 states that comparison
>   operators exist "only inside `where(cond, a, b)`", and its EBNF has no production for
>   comparison, boolean, ternary or modulo. The implementation does the opposite:
>   `where(premium > 100, 1, 0)` is **refused** (`'where' is not an allowed function`), while
>   bare `premium > 100`, `premium if exposure > 0 else 0`, `a and b`, `not (…)` and
>   `premium % 7` are all **accepted**. So the sentence §4.6 uses to bound where comparisons
>   may appear is enforced by nothing, and the safety property it was written to express —
>   comparisons confined to a single reviewed construct — is **not in force**.


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

> **The invariants are about presence; R2 is about stability, and it covers
> `diagnostics_id`** *(amended 2026-08-22, W5's audit-remediation slice).* `status ≥ fitted
> ⟹ diagnostics_id` says a fitted Model **has** evidence. It does not say it keeps the
> *same* evidence, and the database guard read the same way: `b2c3d4e5f6a7` froze
> `fit_result`, `spec`, `spec_hash` and `dataset_version_id` and left the pointer writable,
> so a raw `UPDATE models SET diagnostics_id = …` swapped the A/E, lift and calibration
> under an approved Model with the trigger raising nothing. The numbers were immutable; the
> reason to believe them was not.
>
> **§1.3 R2 was always the wider rule — the code was the side that was wrong**, and
> `9e4c7b21fa08` adds `diagnostics_id` to the frozen set. The guard stays conditional on
> `OLD.fit_result IS NOT NULL` because `record_fit` writes the fit result, the pointer and
> the status in **one `UPDATE`** (`backend/src/app/platform/modelling.py:793-797`), so the
> pointer is frozen from the statement that sets it rather than from some later one;
> `status`, `flags` and `approval_request_id` stay writable, because a Model still has a
> lifecycle after it is fitted.
>
> **The evidence is traced to `00` FR-OVR-1, not to a §4.8 requirement id, because §4.8 has
> none for immutability.** R2 is a §1.3 hard rule with no id of its own, and the ids §4.8
> cites are about presence, transparency and lineage. FR-OVR-1 — *"every Artifact is
> immutable once it leaves `draft`"* — is the requirement R2 instantiates for a Model, and
> is what the new tests carry alongside FR-MODEL-65, which the existing raw-`UPDATE`
> trigger test already uses.

`fit_result` for an EBM carries the shape functions themselves:

```json
{
  "model_type": "ebm",
  "objective": "rmse",
  "link": "identity",
  "intercept": -2.4181,
  "feature_order": ["driver_age_banded", "vehicle_group_rated", "annual_mileage"],
  "bins": [
    {"kind": "categorical", "levels": ["0-1", "2-4", "5-9", "10-49", "50-99"]},
    {"kind": "categorical", "levels": ["1-9", "10-19", "20-29", "30-39", "40-50"]},
    {"kind": "numeric", "cuts": [0, 5000, 10000, 20000]}
  ],
  "terms": [
    {"term_name": "driver_age_banded", "term_features": [0],
     "scores": [0.0, 0.112, 0.054, -0.021, 0.083, 0.041, 0.0],
     "standard_deviations": [0.0, 0.008, 0.006, 0.005, 0.007, 0.005, 0.0],
     "bin_weights": [0.0, 38214.4, 52110.8, 60452.1, 33489.0, 42117.6, 0.0]}
  ],
  "best_iteration": 412,
  "rows": 480000,
  "fit_seconds": 92.4,
  "library_versions": {"interpret-core": "0.7.8", "polars": "1.x"}
}
```

*Corrected 2026-08-24 (W6b-1a). As printed since 2026-08-21 this example was not a valid
`EbmFitResult`: `bins` was an object keyed by feature name where the type declares an array
positional against `feature_order`, and `term_features` held feature names where the type
declares indices into it. `EbmFitResult` forbids extra fields, so a fixture copied from this
page was rejected outright — the defect surfaced when a frontend slice went to build one. The
type was the correct side and the example was behind it (`CLAUDE.md` §0): the positional join
is enforced by a named validator that states its own reason, and `model-schema` is the
generated contract's source while this block was checked by nothing. The object form also hid
a gap a positional array cannot: `feature_order` names three features and the object defined
two, so `vehicle_group_rated` is given its bins here. The `kind` discriminator defaults and
was therefore legal to omit; it is printed because an array of a discriminated union is only
readable positionally when each entry says which arm it is.*

`fit_result` for a GBM carries what a scorer needs and no booster bytes — **added
2026-08-22 (W5, the audit-remediation slice)**. §4.8 has carried a GLM example since Phase 0
and an EBM one since 2026-08-21, and never a GBM one, which is why FR-MODEL-111's
`dropped_eval_metrics` amendment had no example to join and had to point readers at the
generated contract instead. This example is **validated against `GbmFitResult` rather than
hand-written**, and it names every field the type declares — nothing is elided, because a
field absent from the only example on the page is a field a reader concludes is optional:

```json
{
  "model_type": "xgboost",
  "booster_blob": {
    "sha256": "3f786850e387550fdab836ed7e6dc881de23001b4c2f45c7d0e6a1d1a0b9c2e7",
    "bytes": 184320,
    "media_type": "application/json"
  },
  "booster_format": "xgboost_json",
  "feature_order": ["driver_age_banded", "vehicle_group_rated", "region_grouped"],
  "feature_dtypes": {
    "driver_age_banded": "category",
    "vehicle_group_rated": "category",
    "region_grouped": "category"
  },
  "categorical_maps": {"region_grouped": {"north": 0, "midlands": 1, "south": 2}},
  "monotone_constraints": [0, 1, 0],
  "base_margin": {"kind": "log_column", "column": "exposure_years"},
  "best_iteration": 184,
  "inverse_link": "exp",
  "rows": 542410,
  "fit_seconds": 41.7,
  "library_versions": {"xgboost": "3.4.1", "numpy": "2.5.2"},
  "dropped_eval_metrics": [
    {"name": "rmse", "reason": "builtin_evaluated_before_custom_stopping_metric"}
  ]
}
```

Four of those fields are **required and were absent from the hand-authored contract until
2026-08-22** — `booster_format`, `base_margin`, `best_iteration` and the two feature maps —
and each is required for the same reason: a booster loaded without them scores, and scores
wrongly. `booster_format` is ADR-0003 (`pickle` is not a refused value, it is not a value);
`base_margin` is FR-MODEL-71, and omitting the offset at scoring fails **silently** on both
backends; `best_iteration` is what `predict_gbm` passes as `iteration_range` /
`num_iteration`, and diagnostics are not loaded at scoring time.

> **The fit result IS the model (2026-08-21, W5, the EBM slice, FR-MODEL-37).** An EBM is
> its additive shape functions: scoring reproduces `intercept + Σ term scores` exactly,
> each term a lookup — the value's bin index against the feature's `cuts` (numeric, by
> `searchsorted(cuts, v, side="right") + 1`) or `levels` (categorical: `levels[i]` →
> index `i + 1`), then the term's `scores` at that index. Index 0 is the unused base slot,
> and a categorical term carries `len(levels) + 2` slots — the base slot, one per level,
> and a trailing slot for missing values. There is **no booster blob and no serialised
> estimator**: the declarative artifact alone is enough to rescore the model (ADR-0003).
>
> `feature_order` is the order the features were handed to `interpret`; a term with two
> `term_features` is an interaction and carries a two-dimensional `scores` table.

### 4.9 `TransparencyArtifact`

```json
{
  "model_id": "uuid",
  "kinds": ["glm_approximation", "shap_summary", "ebm_shape_functions"],
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
    "top_interactions": [{"pair": ["driver_age_banded", "ncd"], "strength": 0.041,
                          "holdout_strength_ratio": 0.83}]
  },
  "ebm_shape_functions": {
    "terms_blob": "blob:sha256:…"
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

> **`ebm_shape_functions` is the third kind, added 2026-08-21 (W5, the EBM slice).** An
> EBM's term shape functions export directly as rateable tables — no approximation — while
> the artifact still carries the fidelity and diagnostic sections in the same contract
> shape (FR-MODEL-37's requirement text stays as the contract). The block is `terms_blob`
> (`blob:sha256:…`), the bytes of §4.8's `EbmFitResult` shape functions. **The contract
> schema declared this block before the type did; the EBM slice aligns them — the type
> becomes the source.**

> **`holdout_strength_ratio` in the example above is declared ahead of the code, 2026-08-23
> (FR-MODEL-128, OQ-MODEL-31).** No build produces it yet: `build_shap_summary` publishes
> `strength` alone, and the field is absent rather than defaulted until the factor workbench's
> suggestion panel lands. It is flagged here because `ShapInteraction` sets `extra="forbid"`, so
> the example as printed is **not** a valid instance of the shape that validates the artifact
> today — a fixture copied from it would be rejected. *(Noted 2026-08-24, W32 closure proposal
> Part D item 1: the requirement was dated and owned when appended, but neither this example nor
> §5.2's signature said so, which is the whole of the defect.)*

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
the measurement and the invariant that now checks it. *(Amended 2026-08-23, W32-6:
`backtests` carried both layers and was **absent from the one list that makes a trigger
actually fire** in `backend/tests/test_artifact_immutability.py` — every other locked table
had its refusal observed and this one did not. The entry is added and the trigger shown to
refuse `UPDATE`, `DELETE` and `TRUNCATE`.)*

**`uq_backtests_model_version` is not workspace-scoped** (recorded 2026-08-23, W32-6). The
constraint above is on `(model_id, dataset_version_id)` and carries no `workspace_id`, so the
same pair cannot be backtested twice **even in two different workspaces** — the one place the
backend suite's fresh-workspace isolation does not hold, and it surfaces as an `IntegrityError`
that reads like a defect in the route. Whether it is wrong depends on whether model ids may
collide across workspaces at all, which is a governance question rather than a test-fixture
problem: narrowing the constraint is a migration, and widening the isolation is a policy.
**Recorded rather than fixed** — W32-6 is a test slice. **Owner: unassigned; raise before the
next slice that writes a backtest test or touches this table.** Until then, a test seeding
backtests must mint a fresh `(model, version)` pair per test, which
`backend/tests/test_api_backtests.py` does and says why.

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
| `GET` | `/api/v1/factors?dataset_id=` | List factors with intent, monotonic direction, prohibited flag. Filters by Dataset **id**, as its two siblings below do; an unrecognised query parameter is a 422 naming it, never an unfiltered list |
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
| `GET` | `/api/v1/models` | List models, filtered by `family` and `status`, cursor-paginated newest first (`00` §5.2). Every listed model reports `flags: []` — FR-MODEL-67's flag is a per-model read, so a page of 50 would be 51 round trips to decorate rows the caller is about to narrow; `GET /models/{slug}` answers it, and is the only place it gates anything |
| `GET` | `/api/v1/models/{slug}?version=` | Model artifact — latest, or a named version |
| `GET` | `/api/v1/models/{slug}/diagnostics?version=` | Diagnostics artifact — latest version, or a named one, exactly as `GET /models/{slug}` selects |
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
| `GET` | `/api/v1/custom-objectives` | The workspace's objectives, cursor-paginated, filterable by `status` and `slug`, each row carrying `usage_count` (FR-MODEL-127) |
| `GET` | `/api/v1/custom-objectives/{id}` | The objective, its status and its certificate outcome (FR-MODEL-95) |
| `POST` | `/api/v1/custom-objectives/{id}/derive` | Symbolically derive gradient/hessian from `loss` (FR-MODEL-40) — Phase 2, refused with `OBJECTIVE_KIND_NOT_ENABLED` (FR-MODEL-75) |
| `POST` | `/api/v1/custom-objectives/{id}/certify` | **202** Run the certificate checks (FR-MODEL-42) |
| `GET` | `/api/v1/custom-objectives/{id}/certificate` | The latest `ObjectiveCertificate` for that version (FR-MODEL-95) |
| `POST` | `/api/v1/custom-objectives/{id}/submit` | Submit for approval (FR-MODEL-46) |
| `GET` | `/api/v1/custom-objectives/{id}/usage` | Blast radius: models, rating versions, deployments (FR-MODEL-47) |
| `POST` | `/api/v1/custom-metrics` | **201** Create → `draft` (FR-MODEL-45, FR-MODEL-103) |
| `GET` | `/api/v1/custom-metrics` | The workspace's metrics, cursor-paginated, filterable by `status` and `slug`, each row carrying `usage_count` (FR-MODEL-127) |
| `GET` | `/api/v1/custom-metrics/{id}` | The metric, its status and its certificate outcome (FR-MODEL-108) |
| `POST` | `/api/v1/custom-metrics/{id}/certify` | **202** Run §4.7's metric checks (FR-MODEL-105) |
| `GET` | `/api/v1/custom-metrics/{id}/certificate` | The latest `MetricCertificate` for that version (FR-MODEL-108) |
| `POST` | `/api/v1/custom-metrics/{id}/submit` | Submit for approval (FR-MODEL-45's lifecycle) |
| `GET` | `/api/v1/custom-metrics/{id}/usage` | Blast radius: models using this metric version (FR-MODEL-108) |
| `POST` | `/api/v1/peril-structures` | **201** Create/version a Peril Structure (FR-MODEL-58) |
| `GET` | `/api/v1/peril-structures` | The workspace's peril structures, cursor-paginated, filterable by `status` and `slug` (FR-MODEL-127) |
| `GET` | `/api/v1/peril-structures/{id}` | The structure and its reconciliation (FR-MODEL-90) |
| `POST` | `/api/v1/peril-structures/{id}/reconcile` | **202** Recompute reconciliation (FR-MODEL-60) |
| `POST` | `/api/v1/peril-structures/{id}/submit` | Submit for approval, `reconciled → review` (FR-MODEL-90) |

> **Amended 2026-08-22 (W5, the audit-remediation slice): three interface rows, and §5.2
> checked in both directions for the first time.** §5.1's *endpoint* table matched the code
> on all 40 rows, which is how the parameters went unexamined — `scope-audit --endpoints`
> compares method and path, and a wrong *parameter* is invisible to it.
>
> * **`GET /factors` took `?dataset={slug}` and the code takes `dataset_id: UUID`. The page
>   was wrong, and the failure mode was the worst on the list**: FastAPI drops a query
>   parameter no handler declares, so the slug form was not refused — it was *nothing*, and
>   the caller got **200 with every factor in the workspace**. Measured before the fix, two
>   factors on two datasets: `status=200 rows=2`. A 404 is visible and a 422 is visible; an
>   unfiltered list is the one wrong answer indistinguishable from a right one. The code is
>   right — `Factor.dataset_id` is a `uuid` in §4.1, and both sibling rows already read
>   `dataset_id` — so the page is corrected to it. **The silent-ignore is closed at the
>   class, not the instance**: all three transformation list routes now take an
>   `extra="forbid"` query model, because the defect is FastAPI's default rather than one
>   route's, and fixing only the audited route would make strictness a property of what
>   somebody happened to look at.
> * **`GET /models/{id}/diagnostics` is `{slug}` + `?version=`.** The sibling row got
>   exactly this amendment on 2026-08-15 and this one did not. All 23 `{id}` rows in §5.1
>   were then checked against the live routes: the other 22 really do take a `model_id`,
>   `objective_id`, `metric_id`, `structure_id`, `backtest_id` or `comparison_id`, so `{id}`
>   is honest for every one of them and **this was the only wrong row**.
> * **`GET /api/v1/models` did not exist.** Factors, bandings and groupings each publish a
>   list route and models published none — so "40 of 40 endpoints, 100 %" was true and
>   measured the spec against itself, since a route absent from both the table and the
>   contract is invisible to the audit that compares them. Sharper still: **`00` §5.2
>   illustrates the platform's own pagination convention with**
>   **`GET /api/v1/models?limit=50&cursor=<opaque>&status=approved`** — an example route
>   nothing implemented. Two places had already routed around the gap rather than reporting
>   it: `flags_for`'s docstring ("which is why it is not called on the list path") and a
>   lifecycle test reading a family slug straight from the database.
>
> **§5.2's signatures had drifted further than the audit found**, and the page is now
> checked function by function rather than row by row. `model_offset` was missing from
> `fit_glm`, `linear_predictor`, `predict_glm`, `predict_glm_interval` and
> `backtest_model`, leaving FR-MODEL-24 documented at length in §3.4 and unreachable from
> the page a caller copies; `metrics` was missing from `fit_gbm`; and
> **`compute_gbm_diagnostics` was never declared at all**, though it is exported, in
> `__all__`, and called from the worker.
>
> Four the audit did not name: **`compare_models` was declared under the wrong module**
> (`comparison.py`, not `diagnostics.py`); `build_shap_summary`'s `sample` has a default and
> there is a `seed`; and `compile_objective`/`certify_objective` take `objective`, not `obj`.
>
> **And one correction the audit got wrong, which is the reason to check code rather than
> transcribe a finding:** `compute_diagnostics` does **not** take `model_offset`. It takes
> `model_offset_train` *and* `model_offset_holdout`, and must — it scores both partitions,
> and an offset-from-another-model array is per row, so one array cannot serve two frames.
> Writing the single parameter onto the page would have been a *new* defect, published as a
> correction.
>
> **`check_banding`'s stated defaults did not merely mis-describe the fallback — they
> inverted the outcome.** The page said `min_exposure: float = 0.0, min_claims: float = 0.0,
> fail_on_thin: bool = False`; the code takes `None` sentinels that fall back to the
> banding's own stored `minimums` (FR-MODEL-11). Measured on a banding declaring
> `(5000, 100, "fail")`: the real call **raises** `BandingError`, while the page's explicit
> `0.0/0.0/False` returns `()` — clean. The page is accidentally right for a banding with no
> `minimums` block, which is why nobody noticed. `check_banding(df=...)` also raises
> `TypeError`: the first argument is `frame` in every one of these functions, never `df`.

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
`GROUPING_NOT_EXHAUSTIVE`, `CREDIBILITY_VARIANCE_NOT_ESTIMABLE`,
`UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`, `GLM_CV_FOLD_EMPTY`,
`GLM_TWEEDIE_POWER_GRID_EDGE`, `GLM_DID_NOT_CONVERGE`, `GLM_RANK_DEFICIENT`,
`GLM_SEPARATION_DETECTED`, `GLM_FIT_FAILED`,
`OFFSET_REQUIRED_FOR_FREQUENCY`,
`MONOTONE_CONSTRAINT_CONFLICT`, `EARLY_STOPPING_REQUIRES_HOLDOUT`,
`OBJECTIVE_NOT_APPROVED`, `OBJECTIVE_NOT_APPLICABLE`,
`OBJECTIVE_NOT_CERTIFIED` (declared, Phase 2),
`OBJECTIVE_KIND_NOT_ENABLED`, `MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT`,
`OBJECTIVE_GRAMMAR_VIOLATION` (declared, Phase 2),
`OBJECTIVE_NONFINITE_DERIVATIVE` (declared, Phase 2),
~~`TRANSPARENCY_ARTIFACT_REQUIRED`~~, `MODEL_IMMUTABLE`,
~~`PICKLE_PERSISTENCE_REFUSED`~~,
`PERIL_STRUCTURE_RECONCILIATION_FAILED`, `MODELS_NOT_COMPARABLE`,
`OFFSET_NOT_RECONSTRUCTABLE`, `GBM_NO_FEATURES`, `SCORING_FEATURES_MISMATCH`,
`INTERACTION_FEATURE_UNKNOWN`, `LOSS_TREATMENT_UNIMPLEMENTED`, `MODEL_NOT_FITTED`,
`MODEL_SPLIT_REQUIRED`,
`MODEL_ALREADY_TRANSPARENT`, `MODEL_TYPE_UNSUPPORTED`, `APPROXIMATION_TARGET_NOT_POSITIVE`,
`SHAP_SAMPLE_EMPTY`, `OBJECTIVE_NOT_SUPPLIED`, `OBJECTIVE_REF_MISMATCH`,
`OBJECTIVE_RESPONSE_UNDECLARED`, `OBJECTIVE_REQUIRES_OFFSET`,
`OBJECTIVE_EARLY_STOPPING_UNSUPPORTED`, `OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED`,
`MODEL_TERM_UNRESOLVED`, `MODEL_LINK_UNSUPPORTED`, `MODEL_OFFSET_MISSING`,
`MODEL_OFFSET_REF_INVALID`,
`MODEL_INTERVAL_UNAVAILABLE`, `MODEL_INTERVAL_PAIR_INVALID`, `MODEL_APPROXIMATION_INVALID`,
`METRIC_REF_UNRESOLVED`, `METRIC_NOT_APPLICABLE`, `METRIC_NOT_FITTABLE`,
`EBM_MONOTONE_CONSTRAINT_INCOMPLETE`, `EBM_MONOTONE_CONSTRAINT_UNKNOWN`.

> **The catalogue reconciled against `errors.py`, 2026-08-22 (W5, the audit-remediation
> slice), applying `00` FR-OVR-19's own six verdicts rather than inventing new ones.**
> OQ-OVR-9 decided this on 2026-08-21 and FR-OVR-19 lists exactly these six; what had not
> happened was anyone doing them. Until now the page and the registry disagreed in **both**
> directions and nothing could see it — `audit-docs.py` check 10 tests ownership
> *exclusivity*, not existence, and `tests/test_repository_invariants.py`'s registry test
> deliberately excludes `02` because §5.1 declares codes whose slices are unbuilt.
>
> * **`MODEL_SPLIT_REQUIRED` was live and uncatalogued** — registered, and raised from two
>   sites in `worker/model_handlers.py` (the ordinary fit path and the transparency-surrogate
>   path), appearing on this page only as prose inside a §4.12 blockquote. It is now declared.
> * **`TRANSPARENCY_ARTIFACT_REQUIRED` and `PICKLE_PERSISTENCE_REFUSED` are struck**: declared
>   here since Phase 0 and never registered, so raising either would have died inside the
>   error path with `ValueError: unknown error code`. Neither is a gap. R3 is enforced by
>   query and re-raises `06`'s `EVIDENCE_INCOMPLETE` (FR-MODEL-89), and pickle is refused by
>   `booster_format` having no spelling for it — `GlmFitResult`'s docstring still names the
>   code, and that reference is now the only thing left of it.
> * **`OBJECTIVE_NOT_CERTIFIED`, `OBJECTIVE_GRAMMAR_VIOLATION` and
>   `OBJECTIVE_NONFINITE_DERIVATIVE` are marked declared-and-unbuilt in place**, owned by
>   Phase 2's `expression` objectives (OQ-MODEL-1). They are not struck because the slice that
>   raises them is scheduled. `submit_for_review` stands in with `VALIDATION_FAILED` today.
>
> **The machine check that would keep this true is FR-OVR-19's and the maintainer's**, with
> Phase 1a's exit demo as its trigger. This slice did the reconciliation it names and
> deliberately did not build the check, because a check landing before its owner's decision
> is the kind of thing that then has to be un-built.

> **`GLM_FIT_FAILED` added 2026-08-22 (W5, FR-MODEL-23's remainder).** `fit_glm` caught
> only `np.linalg.LinAlgError` around `estimator.fit`, so rank deficiency was the only
> library failure it named and every other refusal `glum` raises reached the Job as a bare
> `ValueError`. Measured against glum 3.4.1 rather than assumed, those are: a response
> outside the family's domain (`Some value(s) of y are out of the valid range for
> familyGammaDistribution.` — a nil-settlement row in a Gamma severity table), a negative
> or all-zero weight vector, an all-zero response, and non-finite inputs. **Not folded into
> `GLM_RANK_DEFICIENT`:** that code's message names collinear terms, which sends the reader
> to drop a factor that was never the problem. One code rather than one per cause, for the
> reason `MODELS_NOT_COMPARABLE` covers four — telling them apart means pattern-matching
> `glum`'s prose, which would pin a permanent code (§5) to a library's message text, so the
> cause is carried verbatim in the detail instead.
>
> **The clause order is load-bearing and is pinned by a test.** `np.linalg.LinAlgError` is
> a *subclass* of `ValueError`, so the two clauses are not siblings: putting the wider one
> first turns every singular design into `GLM_FIT_FAILED`, leaving the fit correctly refused
> and only the diagnosis wrong — which is exactly the tidy-up a later reader would make.

> **Added 2026-08-22 (W5, the EBM slice).** `ebm_monotonicity_verified` refuses to
> check a constraint naming a feature the fitted tables do not contain: reporting
> `True` or `False` for a constraint nothing in the tables can evidence would be a
> made-up monotonicity verdict.

> **Added 2026-08-21 (W5, the EBM slice).** `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` refuses an
> EBM fit whose `monotone_constraints` name a slug that is not among the fitted factors, or
> declare a direction on a categorical (non-ordinal) feature — `interpret` 0.7.8 accepts
> the second and silently zeroes the constrained term — a silent model change; named here
> so the refusal arrives as a code, not a wrong model. (Amended 2026-08-21, the W5 EBM
> fit task: the original note claimed `interpret` raises a bare `ValueError`; the pinned
> library does not.)

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

> **Amended 2026-08-23 (W32-6, the endpoint-test slice).** Endpoint tests against the seven
> `custom-objectives` routes found three things the spec had wrong about them, each resolved
> in favour of the code (`CLAUDE.md` §0):
>
> * **`/derive` answers 409, not the 422 the bullet above states.** The status was written
>   before the refusal was built. 409 is the correct one and the code is right: the request
>   is well-formed and the *capability* is disabled, which is a conflict with the platform's
>   state and not a fault in the body. A caller branching on 422 would file it with the
>   malformed-request handling and retry after "fixing" a body that was never wrong.
>   `backend/tests/test_custom_objectives.py` now pins the status **and** the code.
> * **`/derive` publishes a `200 CustomObjective` response it can never return.** The handler
>   is typed `-> CustomObjective` and its only reachable statement raises. A generated client
>   therefore offers a success shape no call can produce. **Recorded, not fixed** — the
>   return type is what Phase 2 will answer with, and correcting the published response
>   without changing the handler's contract is a `model-schema`-adjacent change that a test
>   slice must not make. **Owner: the Phase 2 slice that enables `expression_objectives`, or
>   an earlier contract-accuracy slice if a client is generated before then.**
> * **The read routes are single-layer RBAC.** `GET /{id}`, `/{id}/certificate` and
>   `/{id}/usage` are gated by the route dependency and reach a `database.session()` that
>   applies no second check, unlike the write paths where `require_permission` runs inside
>   the transaction as well. The workspace fold in `_get_or_404` is what stops a cross-tenant
>   read, and it is now tested in both directions. **Recorded, not fixed** — adding a second
>   layer to read paths is a decision about the whole module's read surface, not this
>   endpoint's. **Owner: unassigned; raise with the next `06` RBAC slice.**

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
def resolve_factors(frame: pl.DataFrame, factors: Sequence[Factor], *,
                    bandings: Mapping[UUID, Banding] | None = None,
                    groupings: Mapping[UUID, Grouping] | None = None) -> FactorMatrix

# pricing_core/modelling/bandings.py
def propose_banding(frame: pl.DataFrame, proposal: BandingProposal, *,
                    dataset_id: UUID, slug: str) -> Banding
def apply_banding(series: pl.Series, banding: Banding) -> pl.Series
def check_banding(frame: pl.DataFrame, banding: Banding, *,
                  min_exposure: float | None = None,
                  min_claims: float | None = None,
                  exposure_column: str = "exposure_years",
                  claim_count_column: str = "claim_count",
                  fail_on_thin: bool | None = None) -> tuple[str, ...]
                  # None ⇒ fall back to banding.minimums (FR-MODEL-11)

# pricing_core/modelling/groupings.py
def propose_grouping(frame: pl.DataFrame, proposal: GroupingProposal, *,
                     dataset_id: UUID, slug: str) -> Grouping
def apply_grouping(series: pl.Series, grouping: Grouping) -> pl.Series
def grouping_evidence(frame: pl.DataFrame, mapping: dict[str, str], *,
                      column: str,
                      exposure_column: str = "exposure_years",
                      claim_count_column: str = "claim_count",
                      claim_amount_column: str = "claim_amount_minor",
                      source: tuple[OneWayRow, ...] | None = None,
                      credibility_model: CredibilityModel | None = None,
                      ) -> GroupingEvidence

# pricing_core/modelling/glm.py
def fit_glm(data: pl.DataFrame, spec: GlmSpec, factors: Sequence[Factor], *,
            model_offset: np.ndarray | None = None,
            bandings: Mapping[UUID, Banding] | None = None,
            groupings: Mapping[UUID, Grouping] | None = None,
            progress: ProgressCallback | None = None) -> GlmFit   # .result, .covariance_bytes, .cv

# pricing_core/modelling/predict.py
def linear_predictor(fit: GlmFitResult, data: pl.DataFrame, factors: Sequence[Factor],
                     spec: GlmSpec, *,
                     model_offset: np.ndarray | None = None,
                     bandings: Mapping[UUID, Banding] | None = None,
                     groupings: Mapping[UUID, Grouping] | None = None) -> NDArray[float64]
def predict_glm(fit: GlmFitResult, data: pl.DataFrame, factors: Sequence[Factor],
                spec: GlmSpec, *,
                model_offset: np.ndarray | None = None,
                bandings: Mapping[UUID, Banding] | None = None,
                groupings: Mapping[UUID, Grouping] | None = None) -> NDArray[float64]
def predict_glm_interval(fit: GlmFitResult, data: pl.DataFrame, factors: Sequence[Factor],
                         spec: GlmSpec, *, covariance_bytes: bytes, level: float = 0.95,
                         model_offset: np.ndarray | None = None,
                         bandings: Mapping[UUID, Banding] | None = None,
                         groupings: Mapping[UUID, Grouping] | None = None
                         ) -> tuple[NDArray[float64], NDArray[float64], NDArray[float64]]
def predict_ebm(fit: EbmFitResult, data: pl.DataFrame, factors: Sequence[Factor], *,
                bandings: Mapping[UUID, Banding] | None = None,
                groupings: Mapping[UUID, Grouping] | None = None) -> NDArray[float64]
def score_fitted(fit: FitResult, spec: ModelSpec, data: pl.DataFrame,
                 factors: Sequence[Factor], *,
                 model_offset: np.ndarray | None = None,
                 bandings: Mapping[UUID, Banding] | None = None,
                 groupings: Mapping[UUID, Grouping] | None = None,
                 booster: bytes | None = None) -> NDArray[float64]
def detect_quantile_crossing(lower: NDArray[float64],
                             upper: NDArray[float64]) -> tuple[int, float]

# pricing_core/modelling/glm.py — the covariance blob's own codec
def encode_covariance(terms: Sequence[str], matrix: NDArray[float64]) -> bytes
def decode_covariance(payload: bytes, terms: Sequence[str]) -> NDArray[float64]

# pricing_core/modelling/gbm.py
def fit_gbm(data: pl.DataFrame, spec: GbmSpec, factors: Sequence[Factor], *,
            holdout: pl.DataFrame | None = None,
            bandings: Mapping[UUID, Banding] | None = None,
            groupings: Mapping[UUID, Grouping] | None = None,
            objective: CustomObjective | None = None,
            metrics: Mapping[str, CustomMetric] | None = None,
            progress: ProgressCallback | None = None) -> GbmFit   # .result, .booster_bytes
def predict_gbm(result: GbmFitResult, booster: bytes, data: pl.DataFrame,
                factors: Sequence[Factor] = (), *,
                bandings: Mapping[UUID, Banding] | None = None,
                groupings: Mapping[UUID, Grouping] | None = None) -> pl.Series
def apply_loss_treatment(response: NDArray[float64], treatment: LossTreatment
                         ) -> NDArray[float64]

# pricing_core/modelling/ebm.py
def fit_ebm(data: pl.DataFrame, spec: EbmSpec, factors: Sequence[Factor], *,
            bandings: Mapping[UUID, Banding] | None = None,
            groupings: Mapping[UUID, Grouping] | None = None,
            progress: ProgressCallback | None = None) -> EbmFitResult

# pricing_core/modelling/objectives.py
def parse_expression(text: str, bound: Sequence[str], params: Sequence[Parameter]) -> ExprTree
def derive_derivatives(loss: ExprTree, wrt: str = "f") -> tuple[ExprTree, ExprTree]
def compile_objective(objective: CustomObjective) -> ObjectiveFns
    # .loss/.grad/.hess(y,f,w), .stabilise(y,f,w), .inverse_link
def certify_objective(objective: CustomObjective, *, sampling: SamplingSpec,
                      progress: ProgressCallback | None = None) -> CertificateResult
def make_xgb_objective(fns: ObjectiveFns) -> Callable[[NDArray[float64], xgb.DMatrix],
                                                      tuple[NDArray[float64], NDArray[float64]]]
def make_lgb_objective(fns: ObjectiveFns) -> Callable[[NDArray[float64], lgb.Dataset],
                                                      tuple[NDArray[float64], NDArray[float64]]]

# pricing_core/modelling/diagnostics.py
def compute_diagnostics(fit: GlmFitResult, spec: GlmSpec, factors: Sequence[Factor], *,
                        train: pl.DataFrame, holdout: pl.DataFrame,
                        model_offset_train: np.ndarray | None = None,
                        model_offset_holdout: np.ndarray | None = None,
                        bandings: Mapping[UUID, Banding] | None = None,
                        groupings: Mapping[UUID, Grouping] | None = None,
                        max_factor_count: int | None = None,
                        min_exposure_per_parameter: float | None = None,
                        type_iii: bool = True,
                        progress: ProgressCallback | None = None) -> DiagnosticsResult
def compute_gbm_diagnostics(result: GbmFitResult, booster: bytes, spec: GbmSpec,
                            factors: Sequence[Factor], *,
                            train: pl.DataFrame, holdout: pl.DataFrame,
                            eval_curve: Sequence[GbmEvalPoint] = (),
                            bandings=None, groupings=None,
                            max_factor_count: int | None = None,
                            min_exposure_per_parameter: float | None = None,
                            permutation_repeats: int = 1,
                            max_partial_dependence_levels: int = 20,
                            progress: ProgressCallback | None = None) -> DiagnosticsResult
def compute_ebm_diagnostics(result: EbmFitResult, spec: EbmSpec, factors: Sequence[Factor], *,
                            train: pl.DataFrame, holdout: pl.DataFrame,
                            bandings=None, groupings=None,
                            max_factor_count: int | None = None,
                            min_exposure_per_parameter: float | None = None,
                            progress: ProgressCallback | None = None) -> DiagnosticsResult
def unit_deviance(y, mu, *, family: str, power: float = 1.5) -> NDArray[float64]
def deviance(y, mu, *, family: str, power: float = 1.5, weights=None) -> float

# pricing_core/modelling/comparison.py
def compare_models(candidates: Sequence[ComparisonCandidate], holdout: pl.DataFrame, *,
                   baseline: str | None = None) -> ComparisonSummary

# pricing_core/modelling/diagnostics.py

def backtest_model(fit: FitResult, spec: ModelSpec, factors: Sequence[Factor],
                   data: pl.DataFrame, *, model_ref: str, dataset_version_ref: str,
                   fitted_on_ref: str, period_from: date | None = None,
                   period_to: date | None = None,
                   model_offset: np.ndarray | None = None,
                   booster: bytes | None = None,
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
                       factors: Sequence[Factor], data: pl.DataFrame, *,
                       holdout: pl.DataFrame,
                       sample: int = 200_000, seed: int | None = None,
                       bandings=None, groupings=None,
                       progress: ProgressCallback | None = None) -> ShapSummary
def build_ebm_shape_functions(result: EbmFitResult) -> EbmShapeFunctions
def ebm_fidelity_statement() -> str
def ebm_monotonicity_verified(result: EbmFitResult, spec: EbmSpec) -> bool | None

# pricing_core/modelling/perils.py
def assemble_risk_premium(predictions: Sequence[PerilPrediction]) -> pl.DataFrame
def reconcile(assembled: pl.DataFrame, *, observed: NDArray[float64],
              exposure: NDArray[float64], tolerance: Decimal,
              treatments: Mapping[str, LargeLossKind]) -> ReconciliationResult
```

> **Two functions were missing from this block until 2026-08-23 (W32-4).** `score_fitted`
> and `detect_quantile_crossing` have existed in `predict.py` since the prediction slice and
> are both called from the platform's own scoring service, so a reader working from this page
> alone would have concluded that the type dispatch lived in the backend and that a crossing
> pair was detected there. The code was right and this block was incomplete; it is completed
> rather than the functions being moved to match it.
> **`max_partial_dependence_levels` was missing from this signature until 2026-08-23
> (W32-5).** It is how FR-MODEL-118's cap is spelled, it has existed since the cap did,
> and a caller working from this page alone could not have known the sweep was bounded
> at all. The code was right and this block was incomplete. The default is
> `DEFAULT_PARTIAL_DEPENDENCE_LEVELS`, which is 20.

> **`holdout` on `build_shap_summary` is declared ahead of the code, 2026-08-23
> (FR-MODEL-128, OQ-MODEL-31).** Unlike the two notes above, this block is **not** behind the
> code here — it is in front of it. The built signature takes no `holdout`; the kwarg was added
> with FR-MODEL-128, whose owner is the slice that builds the factor workbench's suggestion
> panel, and until that lands the function publishes `strength` alone. The sibling
> `build_glm_approximation` above genuinely does take a `holdout`, which is what makes this one
> easy to misread as built. *(Noted 2026-08-24, W32 closure proposal Part D item 1. The
> requirement was dated and owned when it was appended, so this is not spec drift — but nothing
> at this signature or at §4.9's example said so, and §5.1:1697 shows the convention this change
> should have followed: an inline requirement citation on the unbuilt declaration.)*

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
| Factor workbench | `/factors/:datasetVersionId` | Column list with profile one-ways (`01` FR-DATA-26), banding editor with draggable boundaries and live band stats, grouping editor with relativity-ordered levels and merge tolerance slider, monotonic-direction and intent controls, interaction suggestions ranked by SHAP interaction strength which the actuary adds as explicit Factors or ignores (FR-MODEL-79) *(the exposure-share and holdout-lift columns are withdrawn, 2026-08-23; what stands beside a candidate is its holdout strength ratio, FR-MODEL-128)* |
| Model spec builder | `/models/new` | Dataset/split pickers, response & offset/weight, factor multi-select, model-type tabs, objective picker (builtin or approved custom), hyperparameters, live spec validation (FR-MODEL-44) |
| Model detail | `/models/:slug` | Spec summary, coefficient/relativity tables with CI bars, fit metadata, lineage strip, flags. `?version=` selects one; the latest by default |
| Diagnostics | `/models/:slug/diagnostics?version=` | Train/holdout side-by-side throughout; A/E by factor, lift, calibration, residuals, GBM eval curves and importances, CV fold dispersion. *(Amended 2026-08-24, W6b. **Double lift is struck from this cell.** FR-MODEL-50 removed it on 2026-08-17 — it is pairwise, the comparison model is unknown at fit time, and `PartitionDiagnostics.double_lift` was structurally always null — and it lives on the comparison artifact, FR-MODEL-56, which the Model comparison row below already carries. The struck instrument survived here for a week and was then transcribed into a load-bearing chart count in a filed plan, which is how it was found. **This cell is prose, not an enumeration**, and it is non-exhaustive in the other direction too: it names none of `partial_dependence`, `permutation_importances`, `monotonicity` or `quantile_crossing` from `GbmDiagnostics`, nor `type_iii_tests`, `vif`, `aliasing` or `leverage_blob` from `GlmDiagnostics`, all of which the generated contract carries. **Derive no binding chart set from this cell** — under FR-OVR-21 this is a *declared-prose* cell, the affordance OQ-OVR-10's decision of 2026-08-24 named after finding it already invented here; the binding enumeration is the generated contract.)* |
| Model comparison | `/models/compare?ids=` | Aligned metric table, double-lift chart, factor-by-factor relativity diff |
| Custom objective library | `/objectives` | List with status, applicability, usage count; editor with live parse errors (expression authoring is gated by `expression_objectives_enabled` and off throughout Phase 1 — FR-MODEL-75), derived gradient/hessian display, loss-curve preview at chosen parameter values |
| Objective certificate | `/objectives/{id}/certificate` | Per-check `pass` / `warn` / `violated` / `failed` (§4.7) — `violated` presented as a **finding**, never as a failure, since it is the ordinary result for a legitimate non-convex pricing loss (FR-MODEL-43) — convexity heatmap over the sampled `(y, f)` domain, smoke-fit result |
| Custom metric library | `/metrics` | *(registered 2026-08-24, W32 closure proposal Part D item 3)* List with status, applicability and usage count, the mirror of the objective library above; editor with live parse errors and a link to the metric certificate (FR-MODEL-108). Backed by `GET /custom-metrics` (FR-MODEL-127), which this table asked for before it named the screen that consumes it |
| Peril structure library | `/peril-structures` | *(registered 2026-08-24, W32 closure proposal Part D item 3)* List with status and slug, each row linking into the per-structure detail view below. Backed by `GET /peril-structures` (FR-MODEL-127). **No usage count** — that requirement's count is of Model Specs referencing the artifact, and the reference runs the other way for a Peril Structure (§4.10), so the column is absent by specification rather than pending |
| Peril structure | `/peril-structures/{id}` | Per-peril model pins, large-loss treatment, reconciliation panel |
| Backtest | `/models/:slug/backtests/:backtestId` | *(registered 2026-08-23)* Period-by-period A/E and lift against the held-out window, the backtest's own definition (split, periods, exposure basis) shown beside its results, and the fit it was run against. Addressed by backtest id, not by model — a model has many (FR-MODEL-92) |
| Prediction | `/models/:slug/predict` | *(registered 2026-08-23)* Ad-hoc scoring against a fitted Model: input row or uploaded batch, the prediction with its interval where the model type offers one, and the refusal by name where it does not (FR-MODEL-124) |

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

> **Addressing corrected, and two rows registered — 2026-08-23 (slice-map §4 items 5, 9 and 10).**
> Three route cells in this table addressed an artifact as `:slug@:version`: Diagnostics,
> Objective certificate and Peril structure. **The spec was the wrong side.** `@version` in a
> path was removed from §5.1 by the 2026-08-15 amendment, and FR-MODEL-90 and FR-MODEL-95 —
> both appended 2026-08-18 and both built — declare `{id}`. These cells were written in Phase 0
> and never revisited when those landed, so they contradicted their own document rather than
> the implementation. Diagnostics keeps `:slug` with `?version=`, the form Model detail already
> uses and the router already carries; the other two take the id their routes actually serve.
> **What id addressing cannot express is a governance deep link** — "the certificate as it stood
> at version 3" needs a read arm that resolves `(slug, version)`, and there is none. That is a
> read to add when the governance UI needs it (Phase 3), not a frontend route the platform has
> nothing to serve; it is written here so the cost is recorded rather than discovered.
>
> **Backtest and Prediction are registered rows as of today, not new requirements.** A roadmap
> closure record owed "a backtest view (`02` §5.3)" against a table that had no such row — the
> record named an obligation the spec did not carry. Both capabilities are specified and built
> (FR-MODEL-92, FR-MODEL-57, FR-MODEL-124); what was missing was the registry entry.
>
> **And the rule those two items assumed is not this project's:** a view is an obligation
> because it has a row in a §5.3 table, not because a requirement names it. Forty-seven of the
> fifty-one registered views have no FR; the demo guide (`07` FR-PLAT-54) parses these tables as
> the list of what is owed; and `req-coverage.py` scans backend tests only, so a frontend-only FR
> could never be evidenced and would arrive permanently unbacked. Adding one for Model detail or
> Diagnostics would imply the other forty-seven rows are not obligations — the opposite of what
> asking for it was trying to protect.

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
| **interpret (EBM)** | Transparent ML (FR-MODEL-37) | Exporting term shape functions as tables; treating an EBM as a set of additive lookups — resolved 2026-08-21 (W5, the EBM slice): pin `interpret-core==0.7.8`, installed with the slice |
| ~~**SHAP**~~ **The backends' own TreeSHAP** | Transparency artifacts (FR-MODEL-35) | **Amended 2026-08-17 (W5, transparency): the `shap` package is not a dependency.** XGBoost's `pred_contribs` and LightGBM's `pred_contrib` are the same TreeSHAP algorithm on the same trees, already linked against the booster `pricing-core` holds — and `shap` would have added a dependency of its own — for plotting the frontend does (§5.3) and aggregation that is fifteen lines — to the package ADR-0001 keeps importable standalone. *(Corrected 2026-08-17, same day: this row first gave the cost as "would have pulled scikit-learn and its transitive weight in". The scikit-learn half was wrong when written — `glum` 3.4.1 requires it, so it was already installed in every environment this package has ever had, as OQ-MODEL-9 found the next hour. The row's conclusion is unaffected: `shap` itself is still a dependency added for work already done elsewhere.)* What is genuinely lost is **interaction values on LightGBM**: XGBoost computes them (`pred_interactions`, feeding FR-MODEL-79's suggestions and never a Factor), LightGBM does not compute them at all, and `ShapSummary.interactions_available` reports that as a capability rather than as an empty list. Revisit if a third backend or kernel SHAP for a non-tree model is ever needed |
| **SymPy** | Symbolic gradient/hessian derivation (FR-MODEL-40) — **Phase 2**, with `expression` objectives (FR-MODEL-75) | Differentiation of `Piecewise` (from `where`), simplification, lambdify-free code generation into our own expression tree |
| **NumPy** | Compiled objective evaluation | Vectorised, allocation-conscious gradient/hessian evaluation; `np.errstate` discipline for log/exp edges |
| **Python `ast`** | Restricted grammar parsing (§4.6) | Allow-list node walking, depth/size limits, why `eval`/`compile` on user input is never acceptable |
| **Polars** | Factor resolution, banding/grouping application, diagnostic aggregation | `replace_strict` for grouping maps (it refuses an unmapped level rather than dropping it, which is FR-MODEL-13's whole point). **Banding is `numpy.searchsorted`, not `pl.cut`** — the artifact's `closed`, `null_level`, `below_range` and `above_range` policies decide where a value lands, and `cut` implements one fixed convention (added 2026-08-15, W5) |
| **SciPy** | CIs, profile likelihood for Tweedie `p`, numeric derivative checks in certification, limited fluctuation's credibility standard for `credibility_weighted` groupings (FR-MODEL-80) — Bühlmann–Straub's EVPV/VHM estimators are pure NumPy and use no SciPy | `scipy.optimize` for the profile grid, `scipy.stats` for CIs, plus `scipy.cluster.hierarchy` (Ward linkage + `fcluster`) for FR-MODEL-14's `hierarchical_clustering` — exposure weighting by observation repetition, since the clusterer takes no sample weights (added 2026-08-15, W5) |
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
| **NFR-MODEL-4** | Diagnostics computation adds no more than **50 %** to fit wall-clock, at or below **5 M rows × 60 factors**, **excluding the per-factor block that NFR-MODEL-13 and NFR-MODEL-14 bound**. *(Amended 2026-08-22, OQ-MODEL-24 decided — three changes, each because the first measurement contradicted the requirement as written.* ***Scope:*** *FR-MODEL-51's type-III tests drop each factor and refit, so a diagnostic containing F refits cannot cost 30 % of one fit for any F above zero; that block moves to NFR-MODEL-13 and the GBM path's per-factor passes to NFR-MODEL-14.* ***Denominator:*** *fit wall-clock means the elapsed fit call including factor resolution and design-matrix construction — **not** `GlmFitResult.fit_seconds`, which is the solve alone and reads the same arm 1.7× higher, 55.2 % against 32.1 %.* ***Number and scale:*** *30 % was a Phase-0 estimate covering all diagnostics. Re-scoped, the block measures 8.9 %, 9.5 % and 32.1 % across the measured range and projects 34.1 % at 5 M × 60, so the ratio is **not scale-free** — diagnostics are roughly linear in rows while the fit is measured at n^0.837 — and a bare percentage with no stated scale is not a budget. 50 % is 1.47× the worst projection, the headroom this repository carries wherever a budget is met against a measurement at its stated scale (NFR-MODEL-2 at 1.25×, NFR-MODEL-10 at 2×, NFR-DATA-3 at 3.3×) rather than the 50–2000× residue of its unmeasured Phase-0 guesses.* ***This is not option (d):*** *(d) would have raised the ceiling to accommodate F extra model fits — 1 388 % and climbing with the factor count, which is not a budget. This sets a first ceiling for a quantity that has never carried one, and the 30 % it replaces is preserved above and in OQ-MODEL-24's options.)* |
| **NFR-MODEL-5** | Objective certification completes in < 3 min including the synthetic smoke fit. |
| **NFR-MODEL-6** | Determinism: identical `spec_hash` + seed reproduces identical coefficients to 1e-10 (GLM) and an identical booster hash (GBM), on the same library versions (FR-OVR-8). |
| **NFR-MODEL-7** | A stored Model round-trips: export → import into a clean instance → predictions identical to the last representable digit (FR-OVR-2). |
| **NFR-MODEL-8** | Security: user-supplied expressions never reach `eval`/`exec`; the parser rejects out-of-grammar input with a position-accurate error; compiled objectives cannot allocate unbounded memory or exceed their per-round time budget (FR-MODEL-48). |
| **NFR-MODEL-9** | Audit: factor/banding/grouping creation and edit, fit start and completion, objective derivation/certification/approval, and every status transition emit Audit Events with before/after state. |
| **NFR-MODEL-10** | Memory: fitting a 5 M × 60 dataset stays within 32 GB, using `QuantileDMatrix`/streaming construction rather than duplicating the design matrix. |
| **NFR-MODEL-11** | Diagnostics artifacts stay under 50 MB per model; larger evidence (SHAP dependence, residual scatter) goes to content-addressed blobs referenced from the artifact. |
| **NFR-MODEL-13** | **The GLM per-factor diagnostic block — FR-MODEL-51's type-III tests — costs no more than one fit wall-clock per *tested* factor.** The unit is one element of `type_iii_tests`, **not** one element of `factors`: interaction operands carry no design column and are skipped (FR-MODEL-91), a spec with fewer than two factors yields none, and a refit that will not converge is skipped rather than reported. The denominator is a **warm** fit of the same spec at the same scale, for the reason §9's measurement note records. The bound is the mechanism rather than a target: each iteration runs one full `fit_glm` over the remaining factors plus one full `predict_glm`, so a refit of a strictly smaller model that costs more than the fit it is a refit of names a defect rather than a scale. (Added 2026-08-22, OQ-MODEL-24 decided.) |
| **NFR-MODEL-14** | **The GBM per-factor diagnostic block costs no more than 0.06 of one fit per full-population scoring pass.** The unit is a scoring pass, **not** a factor, because the driver is the sum of grid points and not the factor count: partial dependence runs one pass per grid point — ten quantiles for a numeric factor, and **every distinct level for a categorical, uncapped** — so a single 10 000-level column, the scale NFR-MODEL-3 itself names, costs 10 000 passes that a per-factor budget would record as one factor. Permutation importance is the smaller half by an order of magnitude: at the measured shape it is 61 passes against partial dependence's 560. That the sweep is uncapped, and that it covers every factor where FR-MODEL-52 says declared ones, is raised as OQ-MODEL-26 rather than tuned here. (Added 2026-08-22, OQ-MODEL-24 decided.) |

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


> **NFR-MODEL-3 re-measured 2026-08-22 (W5, the audit-remediation slice), and the record
> above named the wrong cause.** It is now missed by **all three** grouping methods rather
> than one. 678 013 rows with a 10 000-level categorical, on the development machine
> (Intel Xeon @ 2.20 GHz, 4 cores, 16.4 GB, 1-minute load average **1.6** — the machine is
> shared between concurrent sessions, and the same proposal measured **20.01 s at load
> 8.4**, so every figure here is quoted with the load it was taken at), budget 5 s:
>
> | Proposal | Measured | Verdict |
> |---|---|---|
> | `propose_banding`, all five methods, 20 bands | 0.10 – 1.07 s | **met**, an order of magnitude of headroom |
> | `propose_grouping`, `tree` | 5.15 s | **not met**, by 3 % |
> | `propose_grouping`, `credibility_weighted` | 5.31 s | **not met**, by 6 % — 4.24 s on 2026-08-15 |
> | `propose_grouping`, `hierarchical_clustering` | 8.58 s | **not met**, by 72 % — 6.52 s on 2026-08-15 |
>
> **The shortfall is not Ward.** Broken down: the source one-way summary costs **5.22 s**,
> Ward linkage **2.38 s**, and `grouping_evidence` with the summary supplied **0.22 s**.
> **The summary alone exceeds the 5 s budget before any clustering runs** — which is why all
> three methods now breach, and why `tree` and `credibility_weighted` miss by so little:
> they are the summary and almost nothing else.
>
> That makes the record above's two routes out a **dependency rather than a choice**.
> Replacing Ward with a contiguous 1-D partition is **not sufficient**: measured at 0.03 s
> against Ward's 2.38 s — an 87× speedup, with peak RSS falling from 1 017 MB to ~330 MB,
> because Ward's condensed distance matrix is 400 MB at 10 000 levels — the proposal still
> costs **5.47 s and is still over**. It also moves the answer: **8 461 of the 10 000 levels
> land in a different group**, and cluster sizes go from Ward's uneven (19, 77, 103, 148, …)
> to near-equal (495, 495, 495, 496, …), because Ward follows rate structure while an
> exposure quantile equalises exposure. **Computing from the stored Profile is sufficient on
> its own**: 2.60 s, 52 % of budget. It is a signature change rather than an algorithm
> change — `Profile.one_ways` already holds `tuple[OneWayRow, …]`, the same type
> `propose_grouping` computes internally, and `grouping_evidence` already accepts `source=`.
> Two limits travel with it: `01` FR-DATA-26 stores one-ways only for the columns the
> profiler selected, so the compute path must remain as a fallback, and a *derived* version
> (a train part, a filtered version) has no Profile of its own. Doing both leaves 0.25 s.
>
> **Owner: the slice that builds the factor workbench** — unchanged from 2026-08-15, but the
> requirement it must satisfy is now the Profile, not the clusterer.
>
> One fact for whoever takes it: **Ward's exposure weighting is not in force at this scale.**
> `max(1, round(100 × exposure_share))` is 1 for every level holding under 0.5 % of exposure,
> so at 10 000 near-equal levels every level weighs the same, and the property the method's
> own docstring claims is silently absent at exactly the scale this requirement names.

---

> **NFR-MODEL-4 measured 2026-08-22 (W5), and it is not met — because of another requirement
> inside it.** Synthetic motor books on the development machine (Intel Xeon @ 2.20 GHz,
> 4 cores, 16.4 GB; CPU seconds reported beside wall-clock because the machine is shared),
> budget 30 % of fit wall-clock:
>
> | Fit | Fit wall-clock | Diagnostics without type-III | Diagnostics as the platform runs them | Verdict |
> |---|---|---|---|---|
> | GLM, 50 000 × 12 factors | 2.82 s | 0.25 s — **9.0 %** | 14.37 s, 12 refits — **510 %** | **not met** |
> | GLM, 50 000 × 24 factors | 3.05 s | 0.29 s — **9.5 %** | 42.33 s, 24 refits — **1 388 %** | **not met** |
> | GLM, 678 013 × 60 factors | 24.90 s | 8.00 s — **32.1 %** | did not finish inside 40 minutes | **not met** |
> | GBM, 75 000 × 60 × 500 trees | 14.45 s | — | 433.81 s — **3 002 %** | **not met** |
>
> Everything `compute_diagnostics` does *except* FR-MODEL-51 fits the budget: 9.0 % and
> 9.5 % at the small scales, 32.1 % at 678 013 × 60 — 2.1 points over, which is tuning. The
> rest is FR-MODEL-51's type-III tests, which **drop each factor and refit**. That is one
> extra GLM fit per factor, so the ratio is a function of the **factor count**, not of the
> data: doubling 12 factors to 24 took the cost from 5.1× the fit to 13.9×, because each
> added refit is also over a wider design matrix. On the GBM path there is no type-III, and
> the 3 002 % is permutation importance and partial dependence over 60 factors.
>
> **The budget and FR-MODEL-51 cannot both hold as written.** A diagnostic containing *F*
> refits of the model cannot cost 30 % of one fit for any *F* above zero, and FR-MODEL-49
> requires diagnostics computed once at fit time, so there is no later pass to move them to.
> This is a contradiction **between two numbered requirements**, not a slow function, and it
> is raised as **OQ-MODEL-24** with three options rather than settled here — §14 makes a
> requirement's scope the maintainer's, and tuning either number quietly would destroy the
> record of which was believed.
>
> The measurement is now repeatable rather than one-off: `app.worker.model` emits
> `diagnostics_seconds` and `diagnostics_over_fit` beside `fit_seconds` on every fit. Note
> the two denominators disagree — `fit_seconds` (14.48 s at 678 013 × 60) is the solve and
> excludes the factor resolution and design-matrix construction the caller also waits for
> (24.90 s). **Against `fit_seconds` the no-type-III figure is 55.2 % rather than 32.1 %**,
> so OQ-MODEL-24 must also say which denominator the budget means.
> 
> **Amended 2026-08-22 (OQ-MODEL-24 decided — option (a), denominator settled as fit wall-clock).** Every number above stands: it is what was measured, and its verdict column records what was believed on the day. What changed is the requirements the numbers are read against.
> 
> | Fit | Block | Read against | Measured | Verdict |
> |---|---|---|---|---|
> | GLM, 50 000 × 12 | all but type-III | NFR-MODEL-4, ≤ 50 % | 8.9 % | **met** |
> | GLM, 50 000 × 24 | all but type-III | NFR-MODEL-4, ≤ 50 % | 9.5 % | **met** |
> | GLM, 678 013 × 60 | all but type-III | NFR-MODEL-4, ≤ 50 % | 32.1 % | **met**, 1.56× |
> | GLM, 5 M × 60 | all but type-III | NFR-MODEL-4, ≤ 50 % | 34.1 %, *projected* | **met**, 1.47× — projected, never measured |
> | GLM, 50 000 × 12 | type-III | NFR-MODEL-13, ≤ 1.0× per tested factor | 0.417× cold, 0.95× warm-corrected | **met** |
> | GLM, 50 000 × 24 | type-III | NFR-MODEL-13, ≤ 1.0× per tested factor | 0.574× cold, 0.98× warm-corrected | **met** |
> | GLM, 678 013 × 60 | type-III | NFR-MODEL-13, ≤ 1.0× per tested factor | **> 1.61×**, censored | **not met** |
> | GBM, 75 000 × 60 × 500 | permutation + partial dependence | NFR-MODEL-14, ≤ 0.06 fits per pass | 0.0480 fits per pass | **met**, 1.25× |
> 
> **Three things the re-read turned up that the original note did not.**
> 
> **The "9.0–9.5 %" that justified keeping 30 % is the two small arms only.** The third GLM arm is 32.1 %, so the non-type-III ratio *triples* across the measured range rather than sitting flat, and it projects to 34.1 % at 5 M × 60 — NFR-MODEL-1's own scale. It is not scale-free because diagnostics are roughly linear in rows while the fit is measured at n^0.837, so a percentage stated without a scale is not a budget. NFR-MODEL-4 now names one.
> 
> **The per-factor multiple is an artefact of a cold denominator; corrected, it is flat at ≈ 1.0.** Each type-III iteration calls the full `fit_glm` plus a full `predict_glm`, so a refit over one fewer factor *ought* to cost about one fit — yet the raw multiples are 0.417× and 0.574×. That is only possible if the denominator carries fixed cost the refits do not: the bench's first fit runs cold, one row-and-factor pair per process. Solving the two refit costs for a fixed term gives 1.59 s and 1.26 s against denominators of 2.82 s and 3.05 s — two independent estimates agreeing that **41–56 % of each denominator is one-time cost**. Corrected, the multiples are 0.95× and 0.98×, which is exactly what the mechanism predicts. **Those two figures are derived, not measured**, and a warm-denominator run is owed before NFR-MODEL-13 is called met at any scale. The original note's "growth is super-linear because each refit is over a wider design matrix" does not survive the third point: a two-point law fitted to F = 12 and F = 24 predicts 1 307 s at F = 60, and the run exceeded 2 400 s — under-predicting by at least 1.84×. Two points cannot evidence a growth exponent, and the only other observation falsifies the one they give.
> 
> **The GBM's 3 002 % is not "over 60 factors".** It is over roughly 625 full-population scoring passes, and 90 % of them are partial dependence: one pass per partition, 61 for permutation importance at one repeat, and 560 for partial dependence — 20 categorical factors × 8 levels plus 40 numeric × 10 quantiles. That is 0.694 s per pass, or 0.0480 of a fit, which is what NFR-MODEL-14 is set against. Per *factor* it is 0.500 fits, a number that means nothing outside this exact factor mix. Permutation importance and partial dependence are not equal partners in the cost; they split roughly 1 to 9.
> 
> **What is still not met, and who owns it.** NFR-MODEL-13 is breached at 678 013 × 60 — more than 1.61× per tested factor against a 1.0× bound — and the observation is **censored**, so the true figure is unknown rather than large. The excess is diagnosable rather than mysterious: every refit re-resolves the factors and rebuilds the design matrix from scratch, and each adds a full-frame `predict_glm` that the original fit never pays. **Owner: Phase 1b**, together with the warm-denominator run the corrected multiples depend on. NFR-MODEL-4 and NFR-MODEL-14 are met at every arm measured.

---

> **NFR-MODEL-5 measured 2026-08-22 (W5), and it is met with fifty times the headroom.** All
> twelve §4.5 templates certified at the **default 2 000-point grid the platform actually
> uses** — not the suite's 300- and 1 000-point grids — including §4.7's synthetic smoke fit,
> on the development machine (Intel Xeon @ 2.20 GHz, 4 cores, 16.4 GB), budget 180 s:
>
> | Certification | Measured | Verdict |
> |---|---|---|
> | Fastest — `asymmetric_poisson` | 0.42 s | **met** |
> | Median across the twelve templates | ~1.2 s | **met** |
> | Slowest — `focal_binomial` | 3.56 s | **met**, at 2.0 % of budget |
>
> There is no shortfall to explain. The number worth recording is the ratio: the budget is
> 50× the slowest template, so **certification density could rise by an order of magnitude**
> — §4.7's convexity and scale checks report a share of sampled points, and a denser grid is
> the only thing that makes those shares mean more — before the budget became the
> constraint. **Owner: none required.** If a Phase 2 `expression` objective (FR-MODEL-40)
> brings symbolic differentiation into the certification path, this measurement is the
> baseline to re-read it against: that is the one change that could plausibly consume the
> margin.

---

> **NFR-MODEL-11 measured 2026-08-22 (W5), and it is met by nearly three orders of
> magnitude.** The serialised `DiagnosticsRow.payload` — one JSONB document, so its encoded
> length *is* its size — on the development machine, budget 50 MB per model:
>
> | Artifact | Measured | Verdict |
> |---|---|---|
> | GLM, 678 013 rows × 60 factors | 0.07 MB | **met**, at 0.1 % of budget |
> | GBM, 75 000 rows × 60 factors × 500 trees | 0.13 MB | **met**, at 0.3 % of budget |
> | Largest single block — `universal` | 0.068 MB | — |
>
> The GBM arm is measured deliberately rather than the GLM alone: this requirement names
> SHAP dependence and residual scatter, and **a GLM has neither**, so a GLM-only measurement
> would report the budget met on the path that was never the risk.
>
> One consequence worth stating: **the blob spill this requirement provides for is not yet
> load-bearing.** `Diagnostics.residual_blob` and `leverage_blob` exist and nothing has
> needed them, so the mechanism is untested against the case it was designed for.
> **Owner: the slice that first stores a per-row residual series** — a full-population
> residual scatter at 5 M rows is 40 MB of float64 before encoding, which is where this
> measurement stops predicting the answer.

---

> **NFR-MODEL-1 and NFR-MODEL-10 measured 2026-08-22 (W5) at four scales below the one they
> state, and both are met by extrapolation rather than by measurement.** The requirements
> name 5 M rows × 60 factors on a **16-core** worker; the development machine is a **4-core**
> Intel Xeon @ 2.20 GHz with 16.4 GB, and a 5 M × 60 dense design matrix is ~7 GB before
> `glum` allocates anything — so the stated scale cannot be reached here, and building a
> fixture for it would have bought hours of compute for a number this curve gives more
> honestly. Measured at 100 000 / 200 000 / 400 000 / 678 013 rows × 60 factors (20
> categorical × 8 levels + 40 numeric, ~180 design columns), budgets 600 s and 32 GB:
>
> | Quantity | Fitted curve | At 678 013, measured | Extrapolated to 5 M | Verdict |
> |---|---|---|---|---|
> | Wall-clock | `t = 4.31e-4 · n^0.837` (R² = 0.9933) | 31.14 s | **173 s** of 600 s | **met**, at 29 % |
> | CPU seconds | `t = 1.30e-3 · n^0.779` (R² = 0.9864) | 45.38 s | 215 s | — |
> | Peak RSS | `m = 0.101 · n^0.777` (R² = 0.9960) | 3 516 MB | **16.0 GB** of 32 GB | **met**, at 50 % |
>
> **The extrapolation is stated rather than hidden, and its weakest point is memory.** Both
> time exponents are **sub-linear** (0.78–0.84), which is the fixed cost of factor resolution
> and design-matrix setup being amortised as rows grow — an effect that stops helping, since
> IRLS is at least O(n·p²) per iteration asymptotically. Projected **linearly** from the
> largest measured point instead, the GLM takes **230 s** (38 % of budget) and peak RSS
> reaches **25.9 GB — 81 % of NFR-MODEL-10's budget**, on a machine that cannot hold it to
> check. **Memory is the clause that fails first, and the one nothing here can falsify.**
> Two further caveats pointing in opposite directions: the 4-core machine measured only 1.5×
> parallelism (45.38 s CPU against 31.14 s wall), so a 16-core worker helps *less* than
> linearly; and none of this exercises the streaming construction NFR-MODEL-10 names — the
> curve above is the dense GLM design matrix, precisely the path `QuantileDMatrix` does not
> apply to.
>
> **NFR-MODEL-2 is measured once and its growth is not.** A GBM at 75 000 rows × 60 factors
> × 500 trees took **14.45 s wall / 48.57 s CPU / 458 MB**; projected linearly in rows that
> is **963 s at 5 M against a 1 200 s budget — 80 %**, on 4 cores, with memory following
> `m = 0.417 · n^0.645` (R² = 0.9902) to 8.7 GB, sub-linear as histogram binning predicts.
> **The linearity is assumed, not shown**: a three-scale run intended to measure it returned
> a 400 000-row point *faster* than its 200 000-row point in both clocks (R² = 0.18) under a
> load average of 12.9. That is contention, and the honest statement is that the GBM path's
> row exponent is **unmeasured on this machine**. At 80 % of budget resting on an assumption,
> this is the requirement most likely to be wrong. **Owner: the slice that first has a worker
> resembling the 16-core machine these three requirements name** — a dedicated run there
> settles all three, and nothing short of it does.
>
> NFR-MODEL-2's second clause — an `expression` objective adding no more than 25 % — is
> **Phase 2 and confirmed unbuildable today**: `refuse_expression_kind` refuses the kind with
> the feature flag on as well as off, so there is no expression objective to time against its
> builtin equivalent.

---

> **NFR-MODEL-6, -7, -8 and -9 given verdicts 2026-08-22 (W5), two of them correcting what
> the plan believed.**
>
> * **NFR-MODEL-9 — evidenced** for every act that has a before: `backend/tests/test_model_nfrs.py`
>   asserts an Audit Event carrying `before` and `after` for model status transitions and for
>   objective certification, submission and approval. **Five create events carry no `before`** —
>   `factor.created`, `banding.created`, `grouping.created`, `model.reserved`, `model.fitted`
>   pass `after=` alone. **That is left as it is, and pinned by a test, rather than filled with
>   an empty dict to satisfy a grep.** These artifacts are versioned and never edited: an
>   "edit" allocates the next version of a slug, and the predecessor stays readable at its own
>   version — so a create has **no before by construction**, and `before={}` would assert the
>   artifact previously existed in an empty state, which is false. The obligation is on this
>   requirement's *wording*: it should read "…carrying after state, and before state wherever a
>   prior state exists". Objective *derivation* is confirmed out of scope — `refuse_expression_kind`
>   refuses `expression` with the flag on and off, and no `*.derived` audit action exists.
> * **NFR-MODEL-8 — half met, and the half that is met is now tested.** The `eval`/`exec`
>   clause is evidenced at `packages/pricing-core/tests/test_expression_nfrs.py`: the accept
>   path compiles and evaluates correctly with `builtins.eval` and `builtins.exec` **removed**,
>   and eight syntactically-valid routes to `eval` raise `ExpressionError` **specifically,
>   never `SyntaxError`** — a distinction `test_prepare.py` conflates by catching both
>   interchangeably. **~~The position-accurate clause is not met~~ — met 2026-08-22 (W5, the
>   closure slice).** It was true as written: `ExpressionError` was a bare `ValueError` with no
>   `lineno`/`col_offset`, so no caller could underline the offending token, and the suite
>   pinned that absence deliberately rather than leaving it unstated. `ExpressionError` now
>   carries `lineno`, `col_offset` and `end_col_offset` exactly as `ast` reports them — 1-based
>   line, 0-based columns — taken from the refused node where it has a position and from the
>   **nearest enclosing positioned ancestor** where it does not. `None` therefore remains
>   correct, and means "the parser could not know" rather than "nobody threaded it"; under
>   `mode="eval"` the only node it can happen for is the bare `ast.Expression` root.
>
>   **The ancestor is load-bearing, and threading the refused child alone does not work.**
>   `ast` gives `lineno`/`col_offset` to `expr` and `stmt` subclasses only — `operator`,
>   `cmpop`, `boolop`, `unaryop`, `comprehension` and `arguments` carry none. The grammar check
>   walks the tree and refuses a disallowed node *before* translation is reached, so an
>   out-of-grammar **operator** such as `FloorDiv` is refused at a node that has no position of
>   its own; reporting the enclosing expression's start instead would be position-*shaped*
>   without being position-*accurate*. The walk therefore pairs each node with its nearest
>   positioned ancestor, preserving `ast.walk`'s order so no refusal changes which message it
>   emits. Proven rather than assumed (§13 rule 4): with the ancestor pairing removed and the
>   child threaded directly, the operator case fails while the subscript case still passes —
>   which is the whole distinction.
>
>   **The per-round objective time budget is not implemented anywhere**; FR-MODEL-48's NaN/inf
>   abort is, with four markers. ~~**Owner: W5** for the error position~~ — **delivered**; the
>   per-round budget travels with FR-MODEL-48 and is unchanged by this.
> * **NFR-MODEL-7 — out of Phase 1 scope. Maintainer verdict 2026-08-22**, on plan review 3's
>   question 2(a); until that date the row read "Owner: unassigned", which is a stated absence
>   of a verdict rather than a verdict, and §13 rule 1 does not admit one. The finding it rests
>   on is unchanged: the repository has **no Model export path and no import path** — not a
>   route (22 model-family routes, none an export; the only `export` in the HTTP surface is the
>   audit log's), not a CLI (`[project.scripts]` is empty), not a bundle schema. Its parent
>   **FR-OVR-2 carries zero markers**, and its serialisability half is evidenced only
>   incidentally by `model-schema` round-trip tests naming other requirements.
>
>   **It is not a W5 defect and never was**: no workstream row has ever named a Model export
>   path, so there is nothing W5 failed to build. The requirement is **not superseded** — ids
>   are permanent (`CLAUDE.md` §5) and the capability is a real one the platform will want; it
>   is out of *this phase's* scope, and the phase that adopts it inherits the requirement as
>   written. Recording that is what lets W5 close honestly: an unevidenced requirement with no
>   owner would otherwise read as W5 owing a feature it was never asked for.
> * **NFR-MODEL-6 — ~~half evidenced, and the roadmap called it evidenced~~ both halves now
>   carry markers, 2026-08-22 (W5, the closure slice).** It asks for identical GLM coefficients
>   to 1e-10 **and** an identical booster hash. Until this date the single marker it carried was
>   the **booster half** (`test_gbm.py:270`); nothing anywhere refitted a GLM and compared
>   coefficients. The GLM half is now
>   `packages/pricing-core/tests/test_glm.py::test_two_fits_of_one_spec_reproduce_identical_coefficients`,
>   beside the code it is about. It fits **one `GlmSpec` object twice** over one frame and
>   asserts term-order equality plus `abs(Δestimate) <= 1e-10` per coefficient — the
>   requirement's own **absolute** tolerance, not `pytest.approx`'s relative default, which a
>   solver gone non-deterministic would still pass. **`spec_hash` itself does not appear in the
>   test**, and cannot: the digest is the *platform's* (`backend/src/app/platform/modelling.py`,
>   `v10`) and the DEP-3 import contract forbids `pricing-core` importing it. Holding one spec
>   object constant satisfies the "identical `spec_hash`" clause by construction — the digest is
>   a function of that object — and holding it constant also pins `spec.seed`, which is the seed
>   the fit actually honours. **Proven able to fail** rather than merely observed passing
>   (§13 rule 4): refitting on one row fewer of 20 000 moves the intercept by 5.8e-05, roughly
>   six orders of magnitude above the gate.
>
>   **A defect found while evidencing it, raised as OQ-MODEL-29 and since resolved: `fit_glm`'s
>   `seed` keyword was inert.** The requirement's own wording is "identical `spec_hash` **+
>   seed**", and the parameter a caller would reach for to supply that seed was read by nothing;
>   `spec.seed` is the live one, and it is the one inside the digest. Raised rather than quietly
>   deleted because `02` §5.2 published the parameter and twenty call sites passed it.
>   **Decided 2026-08-22 at option (b) and removed** — `fit_glm` and `fit_ebm` no longer accept a
>   seed argument, and `spec.seed` is the single seed for every fitter (FR-MODEL-123). This
>   verdict's own clause is therefore now literally true rather than true by construction: there
>   is exactly one seed, it is in the spec, and the spec is what the digest covers.

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-MODEL-1** | ~~Should `expression` custom objectives ship in Phase 1 at all, or only the `template` catalogue (§4.5)?~~ **DECIDED 2026-08-15: templates in Phase 1, expressions in Phase 2 — and the certification machinery is built in Phase 1 regardless.** Specified as FR-MODEL-75 and FR-MODEL-76. The restricted parser is not the deferred part and never was: it already exists for `01` FR-DATA-10. What Phase 2 adds is symbolic derivation, a second compilation target, and the review path for a loss a user wrote. |
| **OQ-MODEL-2** | ~~GBM prediction intervals: paired quantile models, "uncertainty unavailable", or a variance-model approximation?~~ **DECIDED 2026-08-15: `uncertainty: unavailable` with a typed reason by default, opt-in paired quantile models, and the variance approximation is never shipped.** Specified as FR-MODEL-77 and FR-MODEL-78. |
| **OQ-MODEL-3** | ~~Is the GLM approximation of a GBM a *transparency artifact* only, or should it be directly rateable — i.e. can a Rating Version rate on the approximation instead of calling the GBM, trading fidelity for a fully tabular rating structure?~~ **DECIDED 2026-08-17: both modes, and the mode belongs to the Rating Version rather than to the step.** Specified as `03` FR-RATE-60, which pins every `model_call` step's `mode` to `RatingVersion.model_reference_mode` and refuses a disagreement at save time; `03` FR-RATE-10 was ahead of its question rather than wrong and stands as written. What an approximation must *prove* before deploying in that mode is carved out as **OQ-MODEL-11**, and **OQ-MODEL-10** is unblocked. |
| **OQ-MODEL-4** | ~~Interactions as explicit Factors only, or also automatically-detected candidates from SHAP interaction values?~~ **DECIDED 2026-08-15: detected candidates are surfaced as suggestions with their exposure share and holdout lift; only an explicit Factor with a rationale can enter a Model Spec.** Specified as FR-MODEL-79. *Amended 2026-08-23: the two named numbers are withdrawn — a per-pair exposure share is `1.0` by construction and holdout lift was never defined anywhere in the suite — and what replaces them is OQ-MODEL-31, decided the same day: a holdout strength ratio (FR-MODEL-128). The decision itself stands: suggestions, never additions.* |
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
| ~~**OQ-MODEL-15**~~ ✔ | ~~`GlmDiagnostic.aliasing` is `tuple[str, ...]` — collinear terms named — while `docs/contracts/schemas/diagnostics.schema.json` declares an array of untyped `object`. Should an aliasing entry be a bare term name, or a record such as `{term, aliased_with, reason}`? Neither side is obviously wrong — a name is what a reader acts on, an object entry says strictly more, and FR-MODEL-51 asks only for "a VIF/aliasing report".~~ **DECIDED 2026-08-21: bare term names — FR-MODEL-109**, delivered the same day (contract corrected, pin deleted); the object form waits for W6b's diagnostic view. Found 2026-08-19 by widening the contract type comparison. |
| **OQ-MODEL-16** | ~~A paired quantile interval covers `Y` while `UncertaintyKind.confidence_interval_mean` covers `E[Y\|x]`, and FR-MODEL-98 fixes the platform at exactly one kind — what does a quantile-pair response call itself?~~ **DECIDED 2026-08-19: a third member, `quantile_pair_interval` — FR-MODEL-101**, which takes neither existing value and leaves FR-MODEL-98's reserved `prediction_interval` waiting for the aggregate consumer that triggers it. FR-MODEL-98 is amended by addendum rather than edited. |
| ~~**OQ-MODEL-17**~~ ✔ | ~~On a rebuild (`should_fit=False`), `model.transparency` pays a full GLM fit plus a full type-III diagnostics pass — one refit per factor — for numbers it then discards, because the surrogate Model already exists; nobody has costed it. Should the Job skip that compute and reuse the surrogate's already-fitted numbers, keep recomputing for a fresh fidelity measurement, or make it conditional?~~ **DECIDED 2026-08-21: skip the compute on `should_fit=False` and reuse the stored numbers — FR-MODEL-110**, owned by Phase 1b, before its measurement of the Job's cost against `07`'s job-latency NFRs. Found 2026-08-19 in the final whole-branch review of FR-MODEL-96 (fix round). |
| **OQ-MODEL-18** | ~~Should a Custom Metric's certificate run §4.7's full nine-check `ObjectiveCertificate` battery (each derivative/convexity check reporting `not_applicable`, since a metric has no gradient or hessian), or a reduced, metric-specific check set?~~ **DECIDED 2026-08-19: a reduced certificate — `finiteness`, `direction_holds`, `scale_behaviour`, `smoke_evaluation` — FR-MODEL-105**, sharing §4.7's `CheckStatus`, `SamplingSpec`, `CertificateOutcome` and `outcome_of` unchanged rather than its check list. |
| **OQ-MODEL-19** | ~~Does a Custom Metric define its own value computation — a metric-specific template catalogue or `expression` grammar — or does it name an existing `ObjectiveTemplate` (§4.5) and reuse that template's loss?~~ **DECIDED 2026-08-19: a metric names an `ObjectiveTemplate` and reuses its loss, evaluated as an exposure-weighted mean — FR-MODEL-103**, on OQ-MODEL-1's Phase-1-templates-only rule. |
| **OQ-MODEL-20** | ~~§5.1 declared one `POST /custom-metrics` row, not built and deferred to Phase 1b (FR-MODEL-45). Now that a metric gates early stopping (FR-MODEL-107), should this slice ship create only, or the full six-endpoint set FR-MODEL-95 built for `custom-objectives`?~~ **DECIDED 2026-08-19: all six — FR-MODEL-108**, the same argument FR-MODEL-95 made for objectives: an approver who cannot fetch a certificate is being asked to approve a verdict they cannot see. |
| ~~**OQ-MODEL-21**~~ ✔ | ~~LightGBM evaluates builtin metrics before `feval`, so a spec that declares a builtin in `eval_metrics` and early-stops on a Custom Metric never gets the builtin reported (FR-MODEL-107's 2026-08-20 amendment), even though `GbmFit` says nothing about the drop. Does a documented silent drop satisfy FR-MODEL-106's "honoured"?~~ **DECIDED 2026-08-21: record the drop on the fit — FR-MODEL-111**, owned by W5, before W5 closes; FR-MODEL-107 gains a dated addendum. Found 2026-08-20 in the final branch review, before merge. |
| ~~**OQ-MODEL-22**~~ ✔ | ~~Which offsets-from-model come after the GLM-to-GLM slice? Open, gated on W5: FR-MODEL-24's 2026-08-21 amendment builds offset-from-another-model for GLM specs referencing fitted GLMs only — GBM-referenced offsets, `GbmSpec`-declared offsets and the peril-reconciliation scoring path each wait for a workflow that needs them.~~ **DECIDED 2026-08-21: (a) then (c), each as its own slice; (d) only if residual modelling stays GLM-shaped — FR-MODEL-112.** (a) GBM-referenced offsets are the next slice, in Phase 1b, when a workflow needs one; (c) the peril-reconciliation scoring path follows, already owned by W5; (b) `GbmSpec`-declared offsets are not scheduled. |
| ~~**OQ-MODEL-23**~~ ✔ | ~~**`spline`, `polynomial` and `offset` Factors are refused by name with no owner and no schedule. Which of the three, if any, does the platform commit to — and when?** FR-MODEL-88 contains them correctly (a refusal beats a raw column silently substituted) but containment is not a plan, and W5 closes with three arms of FR-MODEL-1's closed set counted among the evidenced because a test marks the refusal. Raised 2026-08-22 (W5, the audit-remediation slice).~~ **DECIDED 2026-08-22: none of the three is committed to a slice, and they no longer share a verdict.** `offset` is superseded as a Factor type, the arm kept in the published contract and its refusal made permanent — FR-MODEL-114. `spline` and `polynomial` stay declared and stay refused, gated on FR-MODEL-115 and owned by W30, because the blocker is neither of them: no continuous Factor can be rated or reviewed today, including the `identity`-over-numeric one that already resolves. |
| ~~**OQ-MODEL-24**~~ ✔ | ~~**NFR-MODEL-4's "diagnostics ≤ 30 % of fit wall-clock" and FR-MODEL-51's type-III likelihood-ratio tests cannot both hold as written. Which moves?** Measured 2026-08-22: diagnostics cost **510 %** of fit wall-clock at 12 factors and **1 388 %** at 24, and **3 002 %** on the GBM path. Everything `compute_diagnostics` does *except* type-III fits the budget, at 9.0–9.5 %. The arithmetic is not a slow function: type-III **drops each factor and refits**, so a diagnostic containing *F* refits of the model cannot cost 30 % of one fit for any *F* above zero — and FR-MODEL-49 requires diagnostics computed once at fit time, so there is no later pass to move them to. A second question rides along: **which denominator the budget means**, since `fit_seconds` (the solve) excludes the factor resolution and design-matrix construction the caller also waits for, and the no-type-III figure is 32.1 % against wall-clock but 55.2 % against `fit_seconds`. Raised 2026-08-22 (W5, the audit-remediation slice), from the first measurement of §9's NFR-MODEL-4.~~ **DECIDED 2026-08-22: option (a), denominator settled as fit wall-clock.** NFR-MODEL-4 is re-scoped to exclude the per-factor block and re-set to 50 % at a named scale; the type-III block becomes NFR-MODEL-13, one fit wall-clock per *tested* factor; the GBM path becomes NFR-MODEL-14, priced per scoring pass rather than per factor because the driver is grid points. The uncapped categorical sweep it exposed is OQ-MODEL-26. |
| ~~**OQ-MODEL-25**~~ ✔ | ~~**`FactorIntent.OFFSET` is live, selectable and consumed by nothing — a Factor an actuary declares as an offset is fitted with a free coefficient.** FR-MODEL-3 declares the intent; `rateable()` tests `risk` only, and neither the GLM nor the GBM fit path reads intent at all. So the declaration is accepted through the API and changes nothing about the fit, which is a silent mis-fit rather than a refusal. Surfaced 2026-08-22 while deciding OQ-MODEL-23, and deliberately not decided inside it: FR-MODEL-114 supersedes the Factor *type* `offset`, and this is the *intent* enum — a different arm of a different enum with a different remedy.~~ **DECIDED 2026-08-22: `offset` superseded as an intent (FR-MODEL-116), `diagnostic` refused pending OQ-MODEL-27 (FR-MODEL-117), and FR-MODEL-3 amended to state what every arm means at fit time.** Not at the recommendation's grounds: `OffsetSpec` is strictly *less* expressive than a per-factor intent, so "duplicate mechanism" is false — the arm goes because offsetness is per-fit and `Factor.intent` is per-Dataset, which is a layer error. The question's own framing understates the defect: `intent` is read in exactly one place in the repository, and `diagnostic` was fitted freely for the same reason `offset` was. |
| ~~**OQ-MODEL-26**~~ ✔ | ~~**The GBM partial-dependence sweep caps nothing and covers every factor, where FR-MODEL-52 says declared ones. What bounds it?** Partial dependence runs one full-population scoring pass per grid point — ten quantiles for a numeric factor, but **every distinct level** for a categorical. At the 10 000 levels NFR-MODEL-3 itself names, one column costs 10 000 passes, roughly 1.9 hours, which a per-factor budget records as a single factor. Raised 2026-08-22 from OQ-MODEL-24's measurement, which attributed 90 % of the GBM diagnostics cost to this sweep.~~ **DECIDED 2026-08-22: the grid is capped at the 20 most-exposed levels and the omission recorded (FR-MODEL-118); the "covers every factor" half is withdrawn.** The sweep already covers exactly the declared factors — the worker passes `spec.factors` — so that half named no gap. The recommendation's pooled bar is **not implementable**: a pooled "other" is an unseen level and FR-MODEL-32 refuses scoring one, so the cap truncates and names what it dropped. A live `IndexError` on interaction factors was found in the same two functions — FR-MODEL-119, OQ-MODEL-28. |
| ~~**OQ-MODEL-27**~~ ✔ | ~~**What does `FactorIntent.DIAGNOSTIC` mean, now that FR-MODEL-117 refuses it?** FR-MODEL-3 lists the arm and glosses only `risk` and `control`, so the arm has never had a stated meaning at either fit or rating time. Raised 2026-08-22 out of OQ-MODEL-25, whose remedy could not be applied to it without inventing the meaning the specification omits.~~ **DECIDED 2026-08-22: superseded — FR-MODEL-120**, on FR-MODEL-116's layer argument and without inventing the missing meaning, because both candidate readings fail: the distinct one is a per-fit property mis-sited on a Factor, and the redundant one is `control` already. The capability it named is real and is re-sited on the Model Spec, gated and owned by W30. FR-MODEL-117's ground for keeping it open is corrected in place. |
| ~~**OQ-MODEL-28**~~ ✔ | ~~**What should permutation importance and partial dependence report for an `interaction` Factor?** A cross sources no column of its own, so neither block has a column to permute or to hold; FR-MODEL-119 makes both skip it and record the skip, having first made a GBM able to fit a cross at all. Permuting or sweeping the operands jointly is the obvious candidate and is not obviously the right one — the operands' own main effects are collinear with the cross by FR-MODEL-91's argument. **The operands raise a second half of the same question**: they carry source columns, so each is swept and reported as though it were a model factor, at full scoring cost, for a term the booster has no column for — while the GLM's type-III block skips exactly those operands and says why. The two paths disagree, and this question owns the disagreement. Raised 2026-08-22 while deciding OQ-MODEL-26.~~ **DECIDED 2026-08-22: the cross is measured jointly through its operands — FR-MODEL-121 — and the operands themselves are skipped — FR-MODEL-122.** A joint shuffle *is* a permutation of the resolved cross column, so the two candidate mechanisms are one on that half; they differ only on the sweep grid, where the observed cells are scoreable and the Cartesian product is refused by FR-MODEL-32. The second half was understated: an operand swept alone is not a wasted pass but a **live crash** on any sparse cross. |
| ~~**OQ-MODEL-29**~~ ✔ | ~~**`fit_glm`'s `seed` keyword is read by nothing, and §5.2 publishes it.** NFR-MODEL-6 asks for reproducibility under "identical `spec_hash` + seed", and the parameter a caller would supply that seed through is inert; `spec.seed` is the live one. Six non-test callers pass it, five test sites pass a value that disagrees with their spec's, and `fit_ebm`'s docstring already records the fact for its own copy of the same dead parameter. Raised 2026-08-22 while evidencing NFR-MODEL-6's GLM half.~~ **DECIDED 2026-08-22: option (b) — removed from `fit_glm` and `fit_ebm` and from §5.2; `spec.seed` is the single seed. FR-MODEL-123.** |
| **OQ-MODEL-30** | ~~`objective-certificate.result.checks` publishes `minItems: 8`; `CertificateResult` requires `1`.~~ **DECIDED 2026-08-23: option (a) — the shared container stays unbounded and each artifact enforces its own count, specified as `FR-MODEL-126`; the contract is corrected to `minItems: 9`.** Original text: **`objective-certificate.result.checks` publishes `minItems: 8`; `CertificateResult` requires `1`. Neither number was right, and the shared type is why.** Found 2026-08-22 by W32-1's scalar-constraint guard on its first run. §4.7's dated 2026-08-18 amendment says **"All nine checks are emitted for every template, always"**, and the authored contract's own `$comment` from that amendment calls `branch_discontinuity` a **ninth** named check (FR-MODEL-69) and adds it to the `name` enum — while leaving `minItems: 8` untouched, so **8 is a stale count contradicted by the file it sits in**. The model's `1` cannot simply become `9` either: `CertificateResult` is **shared** between `ObjectiveCertificate` and `MetricCertificate`, and FR-MODEL-105 gives a metric certificate **four** checks — `min_length=9` would refuse every metric certificate the spec requires. Options and a recommendation ((a) a per-artifact obligation, leaving the shared container unbounded) are in [`../open-questions.md`](../open-questions.md). Scoped out of the guard meanwhile by `UNRESOLVED_CONSTRAINT_DISAGREEMENTS`, whose companion test fails the moment the disagreement is settled. |
| **OQ-MODEL-31** | ~~**What evidence stands beside an interaction candidate, now that its exposure share is vacuous and its holdout lift is defined nowhere?**~~ **DECIDED 2026-08-23: option (b) — a holdout strength ratio, specified as FR-MODEL-128.** FR-MODEL-79 promised an actuary two numbers saying "whether a suggestion is worth taking and over how much of the book", and neither exists: the share is `1.0` for every pair by construction, and holdout lift has no definition, no field and no computation. Raised 2026-08-23 by the W6b slice-map backlog (item 3), which found the constant. The "over how much of the book" half of the question is not answerable per pair at all — a pair spans the whole frame — so what is open is the *worth taking* half. Options and the reasoning are in [`../open-questions.md`](../open-questions.md). The surviving half of the question — *worth taking* — is answered by recomputing the statistic the ranker already computes on the holdout the pipeline already loads; the *over how much of the book* half was withdrawn as unanswerable per pair rather than redefined. Until the suggestion panel is built the artifact publishes strength alone. |
| **OQ-MODEL-32** | ~~Does §5.3 render one artifact library or three?~~ **DECIDED 2026-08-24: option (a), by the W32 closure proposal's Part D item 3 — the two missing §5.3 rows were added.** FR-MODEL-127 opens "The three artifact libraries §5.3 renders are listable", but when W32-8 built the three list endpoints §5.3 had one library view (`Custom objective library`, `/objectives`), a Peril structure *detail* view, and no custom-metric view. The alternative was amending FR-MODEL-127 to "the three libraries §5.1 exposes, of which §5.3 renders one". `Custom metric library` (§5.3) and `Peril structure library` (§5.3) are now registered. Watch item: `00-overview.md` §5.6 carried the identical gap and must move with it. Raised 2026-08-24 by W32-8. |
| **OQ-MODEL-33** | ~~Which artifact rows carry `usage_count`?~~ **DECIDED 2026-08-24: option (a), by the W32 closure proposal's Part D item 4 — the prose is qualified to two libraries.** FR-MODEL-127's prose was unqualified while §5.1 omits the field from peril structures; W32-8 built §5.1's reading and asserted the absence. The ground: a Model Spec cannot reference a Peril Structure — the reference runs the other way (`perils.py:214-228`) — so "the count of Model Specs referencing that artifact" is `0` by construction on a peril row. The guard rail that decision rests on, and does **not** rest on: not the peril block's missing `/usage` route, because FR-RATE-22 pins a peril structure per `model_call` and it does have a real blast radius. Raised 2026-08-24 by W32-8. |
| **OQ-MODEL-34** | **Does FR-MODEL-102's `-approx` slug rule bind every surrogate, or only the ones the transparency Job builds?** The requirement asserts it unconditionally while its own enforcement clause is scoped to the transparency Job, and the platform holds the narrow reading: `reserve_model` persists a caller-supplied `model_family_slug` verbatim and its approximation guard compares three fields, where the sibling `interval_for` guard compares four and leads with the slug. Options: enforce on the create path, scope the sentence to the Job, or derive the slug server-side. Recommendation: derive — its cost is a moved length refusal, not a new lookup — with the missing source-*version* field raised as its own question. |
| **OQ-MODEL-35** | Should `GET /api/v1/custom-objectives` filter by **applicability** server-side? FR-MODEL-44 makes an objective applicable to particular responses and backends, and a spec pairing them wrongly is refused at validation, so a picker offering inapplicable objectives manufactures the error the requirement prevents. `CustomObjective` carries `applicability` on the row, so a client can filter — but the query is `status`, `slug`, `cursor`, `limit` only, and the list is cursor-paginated (`DEFAULT_LIMIT` 50, `MAX_LIMIT` 200). A picker filtering the page it holds renders "no applicable objectives" while applicable ones sit on a later page, **silently**: an empty picker is indistinguishable from a workspace owning none, which makes it invisible in every fixture and worst in the largest workspace. Options are a bounded client-side fetch-all that **states when it stopped paging with `next_cursor` still non-null** (a visible truncation being a different artifact from a silent one), a single large page with the same disclosure, or an `applicable_to` parameter on the route. Recommendation is split: the bounded client fetch as the interim, owned by `W6b-4b`; the route parameter as the durable answer. **That durable answer has no owner** — it is a `02` §5.1 change plus backend work, `W6b` is a frontend workstream, and `W32`, which owned Phase 1b's backend half and built this route under FR-MODEL-127, is closed. It therefore needs a new workstream or a later phase, which is a maintainer's decision about the plan. Raised 2026-08-25 by `W6b-4a`'s derivation, filed a cycle before `W6b-4b` needs it. **Open**, owned by the maintainer; options and evidence are in `docs/open-questions.md`. |
