# WF-03 — Rate change impact: optimisation, dislocation, GIPP, decision

**Modules:** `04-optimisation` · `03-rating-engine` · `06-governance`
**Primary actors:** Pricing Actuary, Approver
**Trigger:** A commercial decision to change prices — a loss-ratio target, a volume target, a competitive response, or a scheduled review.
**Outcome:** An evidenced decision: either an approved rate change, or a recorded decision not to make one.

---

## 1. Preconditions

| Condition | Refs |
|---|---|
| `approved` Demand Models for conversion and retention, each declaring its price term | `04` FR-OPT-1 |
| A live Rating Version as the baseline | `03` FR-RATE-23 |
| A portfolio Dataset Version | `01` §7.2 |
| A renewal-population Dataset Version, declared as such | `04` FR-OPT-18 |
| The actor holds `optimisation:run` and `optimisation:materialise` | `06` FR-GOV-4 |

---

## 2. Main sequence

### Phase A — Is the demand model usable? (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| A1 | Pricing Actuary | `GET /demand-models/{id}/price-variation` — how much genuine price variation exists per segment. | `04` FR-OPT-2 |
| A2 | Backend | Reports 7 of 384 segments with price CV < 0.03: elasticity there is weakly identified. This is stated up front, not buried. | `04` FR-OPT-2 |
| A3 | Pricing Actuary | `POST /demand-models/{id}/elasticity` → elasticity surface with confidence intervals. | `04` FR-OPT-3/4 |
| A4 | Backend | Flags two segments with **positive** point elasticity. These are blocked from optimisation as model defects until resolved. | `04` FR-OPT-6 |
| A5 | Pricing Actuary | Investigates: the two segments are a channel where price and risk are confounded. Excludes them from the decision variable set and records why. | `04` FR-OPT-6 |

> **This phase is the one most often skipped in practice and the one that most often makes
> an optimisation result wrong.** The specification puts it first deliberately.

### Phase B — Optimisation run (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| B1 | Pricing Actuary | Configures the run: objective `blend(w_profit=0.7, w_volume=0.3)`, profit defined explicitly, decision variable `segment_factor` over age × area × channel (384 segments), bounds ±10 %. | `04` FR-OPT-8..10 |
| B2 | Pricing Actuary | Declares constraints: portfolio premium change −1 % to +3 %, expected volume ≥ 1.2 M, expected loss ratio ≤ 0.72, smoothness ≤ 3 pp between adjacent age bands, minimum premium £280, **GIPP as a hard constraint**. | `04` FR-OPT-11/21 |
| B3 | Frontend → Backend | `POST /optimisation-runs` → `202` + Job (`optimisation.run`, queue `compute`). | `07` FR-PLAT-13 |
| B4 | Worker → pricing-core | `optimise()` with SLSQP; Monte Carlo over demand parameters (2 000 samples, seed persisted) for uncertainty. | `04` FR-OPT-13, NFR-OPT-1 |
| B5 | Worker | First attempt returns `CONSTRAINT_SET_INFEASIBLE` within 40 s, naming the culprits: volume ≥ 1.2 M and loss ratio ≤ 0.72 cannot both hold at the current mix. | `04` NFR-OPT-4 |
| B6 | Pricing Actuary | Relaxes the loss-ratio constraint to 0.74 and re-runs. **The infeasibility was itself the finding** — the current book cannot hit both targets, which is worth knowing before proposing a rate change. | `04` FR-OPT-11 |
| B7 | Worker | Converges in 187 iterations. Expected: −3.2 % policies, +2.1 % premium, +8.4 % profit, each with a 90 % interval. | `04` FR-OPT-13 |

### Phase C — Reading the result honestly (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| C1 | Pricing Actuary | Opens the **binding-constraint panel**: loss ratio binds at 0.7399 with a shadow price of £1.42 m profit per 0.01 relaxation; 41 of 384 segments sit at the ±10 % movement cap. | `04` FR-OPT-12 |
| C2 | Pricing Actuary | Understands that the headline "+8.4 % profit" is a *constrained* answer, and that the unconstrained answer would move 41 segments further. | `04` R2 |
| C3 | Pricing Actuary | Reviews the efficient frontier: at `w_profit = 1.0`, profit is +12 % but volume falls 8 %. The chosen point is a deliberate position on that curve, not an optimum in the abstract. | `04` FR-OPT-14 |
| C4 | Pricing Actuary | Reviews warnings: 3 segments' proposed prices sit more than 10 % outside the observed price range — extrapolation the demand model cannot support. | `04` FR-OPT-5 |
| C5 | Pricing Actuary | Re-runs with tighter bounds on those segments; `GET /optimisation-runs/compare` shows exactly what the constraint change did. | `04` FR-OPT-15 |

### Phase D — GIPP (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| D1 | Pricing Actuary | `POST /gipp-checks` on the renewal population against the candidate structure. The channel basis is **not** a choice — ICOBS 6B.2.5R fixes it to the customer's original purchase channel, so the population must carry that column. | `04` FR-OPT-18, FR-OPT-29 |
| D2 | Worker → pricing-core | Scores every renewal risk **twice through the same production bundle** — once as renewal, once as new business **through the original purchase channel**. No formula approximates the ENBP. Policies falling to the 6B.2.5R(2) fallback are counted and reported. | `04` §5.2, FR-OPT-29 |
| D3 | Worker | Distribution of `renewal / ENBP`: worst case 0.998, zero policies above 1.0 → verdict `pass`. | `04` FR-OPT-19 |
| D4 | Worker | Price-walking report by tenure: margin rises 1.4 pp from tenure 1 to 10. Within tolerance, but trending — surfaced as a finding even though the point-in-time check passes. | `04` FR-OPT-22 |
| D5 | Pricing Actuary | Records the price-walking finding as a Commentary Block for the committee. A passing check with a trend is exactly the thing a supervisor asks about later. | `06` FR-GOV-28 |

### Phase E — Materialisation and impact (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| E1 | Pricing Actuary | `POST /optimisation-runs/{id}/materialise` — sees the cell-level diff before anything is created. | `04` FR-OPT-25/26 |
| E2 | Pricing Actuary | Accepts per segment: takes the movements for aggregator business, rejects the direct-channel movements pending a marketing conversation. **Partial acceptance is a first-class action**, and who accepted what is audited. | `04` FR-OPT-26, NFR-OPT-5 |
| E3 | Backend | Creates new Rate Table Versions citing the optimisation run in each change note. | `04` FR-OPT-25 |
| E4 | Pricing Actuary | Enters WF-02 phase C: new Rating Version, compile, regression, dislocation. | WF-02 |
| E5 | Worker | Dislocation attribution separates the optimisation effect from the model-refit effect from the minimum-premium effect. | `03` FR-RATE-49 |
| E6 | Pricing Actuary | Notes that dislocation (+1.95 % actual movement on the book) differs from the optimiser's +2.1 % expected premium, because the optimiser assumed volume response and dislocation holds the book fixed. **These two numbers answer different questions and both are needed.** | `03` FR-RATE-46, `04` FR-OPT-13 |

### Phase F — Decision (Approver)

| # | Actor | Action | Refs |
|---|---|---|---|
| F1 | Pricing Actuary | Submits the Rating Version with the optimisation run, GIPP check, and dislocation attached. | `06` FR-GOV-10 |
| F2 | Approver | Reviews the *binding constraints* alongside the headline numbers — `04` FR-OPT-12 reports each constraint's binding state and shadow price in the run result. | `04` FR-OPT-12 |
| F3 | Approver | Approves, or requests changes, or the committee decides not to proceed. | `06` FR-GOV-9/13 |
| F4 | Backend | Records the decision either way. **A decision not to change prices is recorded with its evidence**, which matters when the same question is asked next quarter. | `06` FR-GOV-20 |

---

## 3. Failure and exception paths

| Situation | Behaviour | Refs |
|---|---|---|
| Demand model has no declared price term | `DEMAND_MODEL_MISSING_PRICE_TERM` — cannot be used for optimisation | `04` FR-OPT-1 |
| Insufficient price variation in a segment | Warned per segment; the actuary decides, with the number in front of them | `04` FR-OPT-2 |
| Positive elasticity | `POSITIVE_ELASTICITY_DETECTED` — segment blocked pending resolution | `04` FR-OPT-6 |
| Proposed price outside observed range beyond the limit | `EXTRAPOLATION_REFUSED` | `04` FR-OPT-5 |
| Constraint set infeasible | Named culprits within 60 s, not after a full failed solve | `04` NFR-OPT-4 |
| Solver hits the iteration limit | Run marked non-converged; materialisation refused without acknowledgement | `04` FR-OPT-17 |
| GIPP check fails | `GIPP_CHECK_FAILED`; with GIPP as a hard constraint, such proposals are never generated | `04` FR-OPT-19/21 |
| Optimisation output pushed straight to production | Impossible — no write path exists from this module to a Deployment | `04` R1, NFR-OPT-7 |

---

## 4. Postconditions

- An immutable Optimisation Run with its constraint set, binding analysis, frontier, and
  uncertainty.
- A GIPP evidence artifact retained for the audit period, plus a price-walking finding.
- Rate Table Versions citing the run, or a recorded decision not to proceed.
- A traceable line from any deployed price back through the run, the constraints, the
  elasticities, and the demand models behind it (`04` FR-OPT-27).

---

## 5. Traceability

| Phase | Requirements exercised |
|---|---|
| A — Demand readiness | `04` FR-OPT-1..7 |
| B — Run | `04` FR-OPT-8..13, 17 |
| C — Interpretation | `04` FR-OPT-12, 14, 15 |
| D — GIPP | `04` FR-OPT-18..23 |
| E — Materialisation | `04` FR-OPT-25..27; `03` FR-RATE-46..49 |
| F — Decision | `06` FR-GOV-9..21 |

## 6. Timing

| Phase | Elapsed |
|---|---|
| A — Demand readiness | hours (and days if a demand model needs refitting) |
| B — Optimisation run | 15 min compute per run; several runs is normal |
| C — Interpretation | hours |
| D — GIPP check | 20 min compute (two full scoring passes) |
| E — Materialisation + WF-02 | 1–2 days |
| F — Committee decision | days to weeks |
