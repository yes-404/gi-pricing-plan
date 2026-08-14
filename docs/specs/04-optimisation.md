# 04 — Optimisation

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `OPT`
**Prerequisites:** [`00-overview.md`](00-overview.md) §2.4; [`02-modelling.md`](02-modelling.md) (demand models are fitted there); [`03-rating-engine.md`](03-rating-engine.md) §3.9 (dislocation).

---

## 1. Purpose & scope

### 1.1 In scope

Everything that turns a *technical* price into a *commercial* price, and everything that
proves the result is defensible:

1. **Demand models** — conversion (new business) and retention (renewal) as functions of
   price and risk characteristics, fitted in `02` and *used* here.
2. **Price elasticity** — derived from demand models, with uncertainty, at the granularity
   the optimiser needs.
3. **Optimisation runs** — constrained search over candidate price adjustments maximising a
   declared objective (volume, profit, or a blend) subject to business, regulatory, and
   fairness constraints.
4. **Scenario analysis** — what-if comparison of several optimisation configurations and
   their efficient frontier.
5. **GIPP checks** — automated **ICOBS 6B** evidence that renewal pricing is not worse than
   equivalent new business. (PS21/5 and PS21/11 announced those rules; ICOBS 6B is the
   binding text, and it is what a supervisor holds the firm to.)
6. **Proposal materialisation** — turning an accepted optimisation result into concrete
   rate table edits or an adjustment step in a Rating Version.

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Fitting the demand model itself | `02-modelling.md` — a Demand Model is a Model with response `conversion`/`retention` |
| Executing prices, rate tables, deployment | `03-rating-engine.md` — this module proposes, that module prices |
| Measuring realised conversion/retention after deployment | `05-monitoring.md` |
| Marketing spend allocation, channel mix, media buying | Out of platform |
| Competitor price data collection | Out of platform; competitor position can be *ingested* as a dataset column and used as a factor |

### 1.3 Hard rules

> **R1 — Optimisation proposes; it never deploys.** Every output is a proposal that must
> go through the `03` rating-version path with its normal approval and dislocation
> evidence. There is no direct line from an optimiser to a live price.
>
> **R2 — Every optimisation run declares its constraints explicitly and records which
> bound.** A run whose result sits on a constraint boundary must say so; "unconstrained
> optimum" is an answer that requires evidence, not an assumption.
>
> **R3 — Demand model uncertainty propagates.** An optimised price presented without an
> uncertainty range around its expected volume and profit is incomplete (FR-OVR-5 spirit,
> `02` R5).
>
> **R4 — GIPP compliance is a gate, not a report.** Where the workspace enables it, a
> Rating Version cannot be approved without a passing GIPP check (`03` FR-RATE-40).

---

## 2. Concepts & glossary

Terms from `00-overview.md` §2.4 are used unchanged. Additional terms owned here:

| Term | Definition |
|---|---|
| **Demand Curve** | For a given risk (or segment), expected conversion or retention probability as a function of price, derived from a Demand Model by varying the price input. |
| **Elasticity** | `∂ log(demand) / ∂ log(price)`, evaluated at a point on the demand curve. Negative by construction; a positive fitted elasticity is a modelling defect, not a finding. |
| **Optimisation Objective** | The declared quantity being maximised: `expected_profit`, `expected_volume`, `expected_premium`, or `blend(w_profit, w_volume)`. |
| **Decision Variable** | What the optimiser is allowed to move: a multiplicative adjustment per segment, per rate-table cell, or a small set of global levers. Declared per run. |
| **Constraint** | A restriction on the search: business (max ±x % movement, min premium, target volume), portfolio (loss ratio, total premium change), regulatory (GIPP), or fairness (no segment worse than y %). |
| **Segment** | The granularity at which the optimiser acts, defined by a set of Factors (e.g. `driver_age_band × rating_area × channel`). Must be coarse enough to be credible and fine enough to be useful. |
| **Efficient Frontier** | The set of non-dominated (volume, profit) outcomes across a sweep of objective weights. |
| **Price Adjustment Proposal** | The optimiser's output for one segment: current price, proposed price, adjustment factor, expected volume and profit change, and which constraints bound it. |
| **Equivalent New Business Price (ENBP)** | The price a renewing customer would be quoted as a new customer through the same channel, computed by re-scoring the renewal risk with `purpose = new_business`. |

---

## 3. Functional requirements

### 3.1 Demand models and elasticity

| ID | Requirement |
|---|---|
| **FR-OPT-1** | A **Demand Model** is a Model (`02`) with response `conversion` or `retention`, whose factor set **must** include a price term — either the quoted premium, the price relative to a reference (e.g. price/technical premium), or the price relative to a market position. The price term is declared explicitly so the optimiser knows what to vary. |
| **FR-OPT-2** | Demand models must be fitted on data containing genuine price variation. The platform computes and reports the effective price variation available (coefficient of variation of the price term within segment) and **warns loudly** where it is too low for the elasticity estimate to be identified. |
| **FR-OPT-3** | Elasticity is derived from the demand model by analytic differentiation where the model form permits (GLM with a log-price term) and by finite difference otherwise, with the method recorded. |
| **FR-OPT-4** | Elasticity is reported **with a confidence interval** derived from the demand model's parameter covariance (GLM) or from bootstrap/quantile methods (GBM), and never as a bare point estimate (R3). |
| **FR-OPT-5** | Elasticity is computed at declared segment granularity and at the current price point; the platform surfaces how far the optimiser is extrapolating beyond observed price range and refuses to extrapolate beyond a configurable limit (default: ±20 % of the observed range). |
| **FR-OPT-6** | A positive point elasticity (demand rising with price) in any segment is flagged as a **model defect** and blocks that segment from optimisation until resolved or explicitly overridden with a justification. |
| **FR-OPT-7** | Where new-business conversion and renewal retention behave differently (they always do), they are separate Demand Models and the optimiser uses the correct one per `purpose`. |

### 3.2 Optimisation runs

| ID | Requirement |
|---|---|
| **FR-OPT-8** | An **Optimisation Run** declares: the portfolio Dataset Version, the baseline Rating Version, the objective, decision variables and their granularity, the demand models to use, the constraint set, and a seed. It executes as a Job and produces an immutable artifact. |
| **FR-OPT-9** | Supported objectives: `expected_profit`, `expected_volume`, `expected_premium`, and `blend(w_profit, w_volume)` with declared weights. The profit definition (premium − expected claims − expenses − commission) is declared explicitly per run, not assumed. |
| **FR-OPT-10** | Decision variables are one of: `segment_factor` (a multiplicative adjustment per segment), `rate_table_cells` (direct adjustment to named cells of named rate tables), or `global_levers` (a small declared set, e.g. overall uplift + young-driver uplift). The choice determines how the proposal materialises in `03`. |
| **FR-OPT-11** | Supported constraint types, each with a declared bound and each recorded as binding or slack in the result: max/min adjustment per segment; max/min portfolio premium change; minimum expected volume; maximum expected volume; minimum expected loss ratio; maximum expected loss ratio; minimum premium; smoothness (adjacent segments' adjustments differ by ≤ x); monotonicity (adjustment monotone in a declared factor); GIPP; and custom linear constraints over segment adjustments. |
| **FR-OPT-12** | The optimiser reports, for every constraint, whether it is **binding** at the optimum and the shadow price / sensitivity where meaningful — because "the optimiser said +3 %" is useless without "and it would have said +7 % if the movement cap allowed" (R2). |
| **FR-OPT-13** | Expected outcomes are reported with uncertainty ranges derived from demand model uncertainty, propagated by Monte Carlo over the demand parameter distribution with a persisted seed and sample count (R3). |
| **FR-OPT-14** | A run produces an **Efficient Frontier** when configured to sweep objective weights, showing the volume/profit trade-off with the chosen point marked. |
| **FR-OPT-15** | Runs are comparable: two runs over the same portfolio and baseline can be diffed segment-by-segment, so an actuary can see what changing a constraint actually did. |
| **FR-OPT-16** | Optimisation never modifies any artifact. Its output is a set of Price Adjustment Proposals plus evidence (R1). |
| **FR-OPT-17** | The optimiser is deterministic given its seed; the solver, its version, its tolerance, and its termination reason are recorded. A run that terminated on iteration limit rather than convergence is marked as such and cannot be materialised without acknowledgement. |

### 3.3 Fairness and regulatory constraints

| ID | Requirement |
|---|---|
| **FR-OPT-18** | **GIPP check**: for a declared renewal population, the platform computes each risk's actual renewal price and its **Equivalent New Business Price**, and reports the distribution of `renewal_price / ENBP`. ENBP is obtained by re-scoring with `purpose = new_business` through **the channel the customer used when they first purchased the policy** — not the channel they are renewing through (ICOBS 6B.2.5R(1)). |
| **FR-OPT-29** | Where the original purchase channel is **no longer available or not identifiable**, ENBP is computed through **the channel most commonly used by new-business customers** (ICOBS 6B.2.5R(2)). Which limb was applied is recorded per policy, and the check reports how many policies fell to the fallback — a large fallback share is a data-quality finding, not a compliance result. |
| **FR-OPT-30** | The GIPP check records the **product scope** it was run for. ICOBS 6B applies to home and motor insurance, including combined packages and connected add-ons; running the check outside that scope is permitted as voluntary good practice but is labelled as such, so evidence is never presented as discharging a rule that does not apply. |
| **FR-OPT-19** | The GIPP verdict is `pass` when no renewing customer's price exceeds their ENBP beyond a declared tolerance (default: zero tolerance, i.e. renewal ≤ ENBP), and `fail` otherwise, with the failing population quantified by count, exposure, and worst-case ratio. |
| **FR-OPT-20** | GIPP evidence is a persisted artifact attached to the Rating Version's approval request and retained for the audit period (NFR-OVR-6) — the platform's answer to "show me how you evidenced compliance in October 2026" (R4). |
| **FR-OPT-21** | The optimiser can take GIPP as a **hard constraint**, so proposals that would breach it are never generated, rather than generated and then rejected. |
| **FR-OPT-22** | **Price walking detection**: the platform reports, per renewal cohort by tenure, the trend in `price / technical_premium`. A systematically increasing margin with tenure is surfaced as a finding regardless of whether the point-in-time GIPP check passes. |
| **FR-OPT-23** | Fairness constraints are supported as first-class declared constraints (e.g. "no segment's adjustment exceeds +10 %", "the adjustment must be monotone in the technical loss ratio"), each carrying a written rationale that appears in the generated documentation. |
| **FR-OPT-24** | Where an insurer supplies a reference dataset containing protected characteristics (which the platform never stores as modelling data — FR-OVR-9), an optional **outcome disparity report** compares proposed price changes across groups. It produces evidence for human judgement and never an automated block (see `02` OQ-MODEL-7). |

### 3.4 Materialisation

| ID | Requirement |
|---|---|
| **FR-OPT-25** | An accepted Optimisation Run materialises into `03` in exactly one of two forms, declared on the run: **rate table edits** (proposals applied as a new Rate Table Version with the run cited in the change note), or an **adjustment step** (a dedicated rate table consumed by an `optimisation_adjustment` ladder rung). |
| **FR-OPT-26** | Materialisation is a proposal-review step: the actuary sees the exact cell-level diff before it creates any version, and may accept per segment rather than wholesale. |
| **FR-OPT-27** | The resulting Rating Version records `optimisation_run_id` in its evidence, so any deployed price traces back to the run, the demand models, the constraints, and the elasticities behind it. |
| **FR-OPT-28** | After deployment, `05-monitoring.md` compares realised conversion/retention against the optimisation's expectations, and that comparison is linked back to the run — closing the loop that makes the next run better. |

---

## 4. Data contracts

### 4.1 `OptimisationRun`

```json
{
  "slug": "motor-gb-2026q4-profit-lean",
  "portfolio_dataset_version_id": "uuid",
  "baseline_rating_version_ref": "rating_version:motor-gb@26",
  "objective": {"kind": "blend", "w_profit": 0.7, "w_volume": 0.3,
                "profit_definition": "premium - expected_claims - expenses - commission"},
  "decision_variable": {
    "kind": "segment_factor",
    "segment_factors": ["driver_age_band", "rating_area_group", "distribution_channel"],
    "segment_count": 384,
    "bounds": {"min_factor": "0.90", "max_factor": "1.10"}
  },
  "demand_models": {
    "conversion": "model:motor-gb-conversion@5",
    "retention": "model:motor-gb-retention@4",
    "price_term": "price_over_technical"
  },
  "constraints": [
    {"kind": "portfolio_premium_change", "min_pct": -1.0, "max_pct": 3.0},
    {"kind": "segment_adjustment", "min_pct": -10.0, "max_pct": 10.0},
    {"kind": "expected_volume", "min_policies": 1_200_000},
    {"kind": "expected_loss_ratio", "max": 0.72},
    {"kind": "smoothness", "over_factor": "driver_age_band", "max_adjacent_diff_pct": 3.0},
    {"kind": "gipp", "mode": "hard", "tolerance_pct": 0.0,
     "rationale": "ICOBS 6B.2.1R — a firm must not set a renewal price higher than the equivalent new business price."},
    {"kind": "minimum_premium", "value_minor": 28_000}
  ],
  "solver": {"name": "scipy.optimize.minimize", "method": "SLSQP",
             "tolerance": 1e-8, "max_iter": 500},
  "uncertainty": {"method": "monte_carlo", "samples": 2000, "seed": 20260814},
  "seed": 20260814,
  "status": "queued | running | completed | failed",
  "termination": {"reason": "converged", "iterations": 187, "seconds": 412.8}
}
```

### 4.2 `OptimisationResult`

```json
{
  "optimisation_run_id": "uuid",
  "expected": {
    "policies": {"point": 1_243_118, "ci_90": [1_198_402, 1_288_940]},
    "premium_minor": {"point": 43_112_800_00, "ci_90": [41_884_200_00, 44_402_100_00]},
    "profit_minor": {"point": 4_218_900_00, "ci_90": [3_402_100_00, 5_041_800_00]},
    "loss_ratio": {"point": 0.708, "ci_90": [0.688, 0.729]},
    "vs_baseline": {"policies_pct": -3.2, "premium_pct": 2.1, "profit_pct": 8.4}
  },
  "binding_constraints": [
    {"kind": "expected_loss_ratio", "bound": 0.72, "at_optimum": 0.7199, "binding": true,
     "shadow_price": "£1.42m profit per 0.01 loss-ratio relaxation"},
    {"kind": "segment_adjustment", "binding": true, "segments_at_bound": 41,
     "note": "41 of 384 segments sit at the +10% cap; the unconstrained optimum would move them further."}
  ],
  "proposals": [
    {"segment": {"driver_age_band": "17-20", "rating_area_group": "A", "distribution_channel": "aggregator"},
     "policies": 8_412, "exposure_years": "8102.4",
     "current_price_minor": 118_400, "proposed_price_minor": 112_480,
     "adjustment_pct": -5.0,
     "elasticity": {"point": -2.84, "ci_90": [-3.41, -2.27]},
     "expected_volume_change_pct": 14.2, "expected_profit_change_minor": 41_200_00,
     "bound_by": ["smoothness"]}
  ],
  "efficient_frontier": [
    {"w_profit": 1.0, "policies": 1_142_800, "profit_minor": 4_884_200_00},
    {"w_profit": 0.7, "policies": 1_243_118, "profit_minor": 4_218_900_00},
    {"w_profit": 0.3, "policies": 1_361_400, "profit_minor": 3_104_800_00}
  ],
  "warnings": [
    {"code": "PRICE_VARIATION_LOW", "detail": "Segment (76+, D, direct) has price CV 0.02; elasticity is weakly identified.", "segments": 7},
    {"code": "EXTRAPOLATION", "detail": "3 segments' proposed prices sit outside the observed price range by >10%."}
  ]
}
```

### 4.3 `GippCheck`

```json
{
  "rating_version_ref": "rating_version:motor-gb@27",
  "renewal_population_dataset_version_id": "uuid",
  "policy_count": 842_118,
  "method": "rescore_as_new_business",
  "product_scope": {"in_icobs_6b_scope": true, "products": ["motor"]},
  "channel_basis": {
    "rule": "icobs_6b_2_5r",
    "primary": "original_purchase_channel",
    "fallback": "most_common_new_business_channel",
    "fallback_channel": "aggregator",
    "policies_on_fallback": 4_182,
    "fallback_share": 0.0050
  },
  "tolerance_pct": 0.0,
  "distribution": [
    {"band": "renewal < 0.90 × ENBP", "policies": 212_884, "exposure_share": 0.253},
    {"band": "0.90–1.00 × ENBP", "policies": 629_234, "exposure_share": 0.747},
    {"band": "> 1.00 × ENBP", "policies": 0, "exposure_share": 0.0}
  ],
  "worst_case_ratio": 0.998,
  "verdict": "pass",
  "failing_population": {"policies": 0, "exposure_years": "0", "max_ratio": null},
  "price_walking": [
    {"tenure_years": 1, "mean_price_over_technical": 1.142},
    {"tenure_years": 3, "mean_price_over_technical": 1.148},
    {"tenure_years": 5, "mean_price_over_technical": 1.151},
    {"tenure_years": 10, "mean_price_over_technical": 1.156}
  ],
  "price_walking_finding": "Margin rises 1.4pp from tenure 1 to 10 — within tolerance but trending; review at next rate change.",
  "evidence_blob": "blob:sha256:…"
}
```

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/demand-models/{id}/elasticity` | **202** Compute elasticity surface with CIs (FR-OPT-3/4) |
| `GET` | `/api/v1/demand-models/{id}/price-variation` | Identifiability report per segment (FR-OPT-2) |
| `POST` | `/api/v1/optimisation-runs` | **202** Launch a run → Job (FR-OPT-8) |
| `GET` | `/api/v1/optimisation-runs/{id}` | Run + result artifact |
| `GET` | `/api/v1/optimisation-runs/{id}/frontier` | Efficient frontier points (FR-OPT-14) |
| `GET` | `/api/v1/optimisation-runs/compare?ids=` | Segment-level diff between runs (FR-OPT-15) |
| `POST` | `/api/v1/optimisation-runs/{id}/materialise` | Preview cell-level diff; accept per segment (FR-OPT-25/26) |
| `POST` | `/api/v1/gipp-checks` | **202** Run a GIPP check → Job (FR-OPT-18) |
| `GET` | `/api/v1/gipp-checks/{id}` | GIPP evidence artifact |
| `POST` | `/api/v1/disparity-reports` | **202** Outcome disparity report against a supplied reference (FR-OPT-24) |

**Error codes owned by this module:** `DEMAND_MODEL_MISSING_PRICE_TERM`,
`PRICE_VARIATION_INSUFFICIENT`, `POSITIVE_ELASTICITY_DETECTED`, `EXTRAPOLATION_REFUSED`,
`CONSTRAINT_SET_INFEASIBLE`, `SOLVER_DID_NOT_CONVERGE`, `GIPP_CHECK_FAILED`,
`MATERIALISATION_REQUIRES_CONVERGED_RUN`, `SEGMENT_TOO_THIN`.

### 5.2 `pricing-core` interfaces

```python
# pricing_core/optimisation/demand.py
def demand_curve(model: Model, risk: pl.DataFrame, prices: Sequence[Decimal]) -> pl.DataFrame
def elasticity(model: Model, data: pl.DataFrame, *, at_price_column: str,
               method: Literal["analytic", "finite_difference"]) -> ElasticitySurface
def price_variation_report(data: pl.DataFrame, segments: Sequence[str],
                           price_column: str) -> PriceVariationReport

# pricing_core/optimisation/optimise.py
def optimise(portfolio: pl.LazyFrame, spec: OptimisationSpec,
             *, seed: int, progress: ProgressCallback | None = None) -> OptimisationResult
def efficient_frontier(portfolio: pl.LazyFrame, spec: OptimisationSpec,
                       weights: Sequence[float], *, seed: int) -> list[FrontierPoint]

# pricing_core/optimisation/gipp.py
def gipp_check(renewal_population: pl.LazyFrame, bundle: CompiledBundle,
               spec: GippSpec) -> GippCheck
def price_walking(renewal_population: pl.LazyFrame,
                  by_tenure: str) -> PriceWalkingReport
```

`gipp_check` scores each renewal risk twice through the same compiled bundle from `03`
(once with `purpose = renewal`, once with `purpose = new_business`) — it does not
approximate the ENBP with a formula. The new-business pass uses the **original purchase
channel** per policy (FR-OPT-18), falling back per FR-OPT-29 where that is unavailable, so
the renewal population dataset must carry that column.

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Optimisation studio | `/optimisation/:runId` | Objective and constraint builder, segment granularity picker with per-segment volume preview, run launcher, live progress |
| Results | `/optimisation/:runId/results` | Expected outcomes with CI bands, binding-constraint panel with shadow prices, proposal grid sortable by impact, segment heat map |
| Frontier | `/optimisation/:runId/frontier` | Volume/profit scatter with the chosen point marked and hover detail per weight |
| Elasticity explorer | `/demand/:modelId/elasticity` | Demand curves per segment with CI ribbons, observed price range shaded, extrapolation warnings |
| GIPP | `/compliance/gipp/:checkId` | Renewal-vs-ENBP distribution, failing population drill-down, price-walking trend by tenure, downloadable evidence |
| Materialisation | `/optimisation/:runId/materialise` | Cell-level diff preview, per-segment accept/reject, resulting rate table version preview |

**Interaction requirement:** the binding-constraint panel is the screen that stops an
optimiser being a black box. Every headline number must be one click from "which
constraint held this back, and by how much" (FR-OPT-12).

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | Pricing Actuary | Confirms demand models exist and are `approved`; reviews the price-variation report (FR-OPT-2) |
| 2 | Pricing Actuary | Reviews the elasticity surface; investigates any positive elasticity (FR-OPT-6) |
| 3 | Pricing Actuary | Configures the run: objective, segment granularity, constraints (incl. GIPP as hard) |
| 4 | Worker → pricing-core | `optimise` over the portfolio against the baseline bundle |
| 5 | Pricing Actuary | Reviews expected outcomes with CIs, binding constraints, frontier |
| 6 | Pricing Actuary | Re-runs with adjusted constraints; compares runs (FR-OPT-15) |
| 7 | Pricing Actuary | Materialises accepted proposals into rate table edits (FR-OPT-25/26) |
| 8 | — | `03` takes over: new Rating Version, dislocation, regression, GIPP check, approval |
| 9 | `05-monitoring` | Post-deployment, realised conversion/retention is compared against the run's expectations (FR-OPT-28) |

Full journey: [`wf-03-rate-change-impact.md`](../workflows/wf-03-rate-change-impact.md).

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What |
|---|---|
| `02-modelling` | Demand Models (conversion, retention) and their parameter covariance for elasticity CIs; risk models for expected claims in the profit definition |
| `03-rating-engine` | Compiled bundles for baseline pricing and ENBP re-scoring; batch scoring; rate tables as materialisation targets |
| `01-data-management` | Portfolio and renewal-population Dataset Versions |
| `06-governance` | Approval and audit for runs cited as evidence; RBAC on who may optimise |
| `07-platform` | Jobs, seeds, blob storage |

### 7.2 Provides

| To | What |
|---|---|
| `03-rating-engine` | Price Adjustment Proposals materialised as rate table versions or an adjustment rung; GIPP evidence required for approval |
| `05-monitoring` | Expected volume/profit/loss-ratio targets that live performance is measured against |
| `06-governance` | Optimisation runs, constraint rationales, and GIPP evidence for generated documentation and regulatory response |

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **SciPy `optimize`** | Constrained optimisation (SLSQP / trust-constr) | Formulating segment adjustments as a bounded vector problem, Jacobians, constraint feasibility diagnosis, reading termination reasons honestly |
| **NumPy** | Objective/constraint evaluation over segment vectors; Monte Carlo uncertainty | Vectorisation so a 2000-sample MC over 400 segments is seconds, not minutes |
| **Polars / DuckDB** | Portfolio aggregation to segment level; joining demand predictions to exposure | Segment definition as a group-by; keeping the optimisation problem small while the portfolio stays large |
| **`03` compiled bundles** | Baseline pricing and ENBP re-scoring | Reusing the exact production pricing path so GIPP evidence is about the real price |
| **glum / XGBoost (via `02`)** | Demand model prediction and covariance extraction | Parameter covariance for elasticity CIs; bootstrap for GBM demand models |
| **ECharts (frontend)** | Demand curves with CI ribbons, efficient frontier scatter, segment heat maps, GIPP distribution | Ribbon/band series; linked brushing between frontier and proposal grid |

New skills this spec adds to `skills-map.md`: constrained optimisation formulation and
feasibility diagnosis; price elasticity estimation and its identifiability problems;
**ICOBS 6B** — the binding pricing rules (PS21/5 and PS21/11 are the policy statements
announcing them) and what evidence a reviewer expects.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-OPT-1** | An optimisation run over a 1.3 M-policy portfolio at 400 segments completes in < 15 min including Monte Carlo uncertainty. |
| **NFR-OPT-2** | A GIPP check over an 850 k renewal population completes in < 20 min (it is two full batch scoring passes — NFR-RATE-5). |
| **NFR-OPT-3** | Determinism: identical run spec + seed reproduces identical proposals to 1e-9 (FR-OVR-8). |
| **NFR-OPT-4** | Infeasible constraint sets are detected and explained — naming the mutually exclusive constraints — within 60 s, not after a full failed solve. |
| **NFR-OPT-5** | Audit: run creation, materialisation acceptance (per segment), and GIPP check results emit Audit Events. Materialisation records exactly which proposals were accepted and which rejected, and by whom. |
| **NFR-OPT-6** | GIPP evidence is retained for ≥ 7 years and is exportable as a self-contained document (NFR-OVR-6). |
| **NFR-OPT-7** | No optimisation output can reach a live price without passing through `03`'s approval path; enforced by the absence of any write path from this module to a Deployment (R1). |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-OPT-1** | Which solver family? SLSQP is simple and adequate for smooth segment-factor problems but struggles at scale and with non-smooth constraints; a dedicated conic/LP formulation (via `cvxpy`) is far more robust for linear constraints but restricts the objective forms we can express. |
| **OQ-OPT-2** | Does the platform ship a competitor-position capability (rank in market, price vs cheapest) as a first-class concept, or is it just another dataset column? First-class means modelling market response; a column means the user does the work. |
| **OQ-OPT-3** | Is `expected_profit` computed with the platform's own risk models, or should it accept an externally-supplied expected loss cost? Insurers often have a separate reserving-derived view that will not match our models, and the mismatch will be noticed. |
| **OQ-OPT-4** | How is the demand model's endogeneity problem handled? Historic prices were set by a rating structure that already conditioned on risk, so a naive elasticity estimate is biased. Do we specify instrumental variables, a randomised price-test capability, or simply document the caveat prominently? |
| **OQ-OPT-5** | Should the platform support **price testing** (randomised price variation on a slice of live traffic) to generate the variation FR-OPT-2 needs? It is the correct answer to OQ-OPT-4 and is operationally and ethically loaded. |
| **OQ-OPT-6** | ~~For GIPP, what is the correct treatment of channel differences?~~ **RESOLVED 2026-08-14 — the rule prescribes it.** ICOBS 6B.2.5R(1) requires the channel the customer used when they *first purchased* the policy, with 6B.2.5R(2) falling back to the channel most commonly used by new-business customers. This is now FR-OPT-18/29, and it corrected a design that keyed off the *renewal* channel. |
