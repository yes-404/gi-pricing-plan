---
id: WF-701
family: workflow
title: Deploy and monitor
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-08-14
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the Works that deliver this journey's steps
was: docs/workflows/wf-04-deploy-and-monitor.md
---

# WF-701 — Deploy and monitor

**Modules:** `03-rating-engine` · `05-monitoring` · `06-governance` · `07-platform`
**Primary actors:** Deployer, Pricing Actuary, Consumer System
**Trigger:** An `approved` Rating Version is ready to go live.
**Outcome:** Live scoring, continuous monitoring, and a closed feedback loop back into modelling or pricing.

---

## 1. Preconditions

| Condition | Refs |
|---|---|
| An `approved` Rating Version with a complete evidence bundle | `03` FR-257, `06` §3.3 |
| A compiled bundle with a content hash | `03` FR-239 |
| The actor holds `rating_version:deploy_uat` / `deploy_prod` | `06` FR-345, FR-428 |
| Service Accounts exist for the Consumer Systems, scoped per environment | `07` FR-389/430 |

---

## 2. Main sequence

### Phase A — UAT deployment (Deployer)

| # | Actor | Action | Refs |
|---|---|---|---|
| A1 | Deployer | `POST /environments/uat/deployments` with the rating version reference and a reason. | `03` FR-267 |
| A2 | Backend | Pre-warms the bundle into the cache on every replica, then switches atomically. No request sees a mixed state. | `03` FR-268, NFR-494 |
| A3 | Backend | Emits an Audit Event and a deployment notification to the configured channel. | `03` FR-272 |
| A4 | Consumer System (UAT) | Scores test quotes. The response carries the ladder, outputs, and the bundle hash. | `03` FR-250, §4.4 |
| A5 | Pricing Actuary | Uses the quote sandbox to score real historical quotes against the new version, side by side with live, with a step-level diff. | `03` FR-262 |
| A6 | Pricing Actuary | Investigates a quote whose premium moved 14 %. The trace shows the cause at `s_minprem`: the minimum premium now binds for this risk. | `03` FR-258 |

### Phase B — Shadow scoring (optional, Deployer)

| # | Actor | Action | Refs |
|---|---|---|---|
| B1 | Deployer | `PUT /environments/prod/shadow` — 5 % of live traffic is additionally scored against the candidate. | `03` FR-271 |
| B2 | Backend | Shadow results are recorded and never returned to the caller. Customers see only the live price. | `03` FR-271 |
| B3 | Pricing Actuary | After a week, compares the shadow price distribution against live on **real live traffic mix**, not on the fixed historical portfolio the dislocation run used. | `05` FR-330 |
| B4 | Pricing Actuary | Finds the shadow average is 0.6 pp above the dislocation prediction — because the live new-business mix has shifted toward aggregator since the portfolio snapshot. Better to learn this now than after deployment. | `05` FR-330 |

### Phase C — Production deployment (Deployer)

| # | Actor | Action | Refs |
|---|---|---|---|
| C1 | Deployer | `POST /environments/prod/deployments`. | `03` FR-267 |
| C2 | Backend | Checks promotion order: a prior successful `uat` deployment is required, else `PROMOTION_ORDER_VIOLATION` — unless the workspace policy permits skipping with a recorded reason. | `07` FR-429 |
| C3 | Backend | Checks **the Rating Version's** approval record is complete, including both required approvers. | `06` §3.3 for the evidence, FR-354 for the count |
| C4 | Backend | Pre-warms, switches atomically, emits the Audit Event and notification. Total elapsed under 30 s. | `03` NFR-494 |
| C5 | Backend | **Auto-creates the template Monitors** for the new deployment, so the structure is never live and unmonitored. | `05` FR-310 |
| C6 | Consumer System | Live quoting proceeds against the new bundle. | `03` FR-250 |
| C7 | Backend | Samples 1 % of traces, plus 100 % of declines and errors, and persists them. | `03` FR-259 |

### Phase D — The first 48 hours (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| D1 | Pricing Actuary | Watches the operational dashboard: p99 latency 31 ms (budget 50), error rate flat, decline rate flat. | `05` FR-331, `03` NFR-489 |
| D2 | Pricing Actuary | Checks bundle health: every replica reports the same bundle hash. A divergence would be an immediate breach. | `05` FR-333 |
| D3 | Pricing Actuary | Watches constraint activation: minimum premium binds on 0.4 % of quotes against the 0.9 % predicted. A real signal — the live mix differs from the dislocation portfolio. | `05` FR-329 |
| D4 | Backend | Reference lookup miss rate stays at zero. A rise here would be the earliest warning that reference data has gone stale. | `05` FR-332 |

### Phase E — Ongoing monitoring (system, then Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| E1 | Worker (scheduled) | Daily: input drift against the modelling baseline **and** against the prior period. | `05` FR-312/314, OQ-631 |
| E2 | Worker | Weekly: price and portfolio metrics, including **rate achieved vs rate intended**. | `05` FR-326, OQ-631 |
| E3 | Worker | Weekly: realised conversion and retention against the demand models and against the optimisation run's expectations. | `05` FR-323, `04` FR-306, OQ-631 |
| E4 | Worker | Monthly: A/E by peril, factor, and cohort — with maturity, never without. | `05` FR-317/318, R4, OQ-631 |
| E5 | Backend | Evaluates thresholds, including consecutive-breach logic so one noisy day pages nobody. | `05` FR-338 |

### Phase F — Rate achieved vs intended (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| F1 | Worker | Rate intended +1.95 %; rate achieved +1.12 %; gap −0.83 pp. | `05` FR-326 |
| F2 | Worker | Decomposition: pure rate +1.94 pp (the structure is doing exactly what was designed), mix shift −0.79 pp (aggregator share up 4.1 pp, and that channel skews cheaper), constraint activation −0.03 pp. | `05` §4.3 |
| F3 | Pricing Actuary | Reports to committee that the rate change landed as designed and the shortfall is a mix effect, not a pricing failure. **This is the question every pricing team is asked after a rate change and usually cannot answer within a month.** | `05` FR-326 |

### Phase G — A breach and its resolution (Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| G1 | Worker | Monthly A/E run: `AD × driver_age_band 17-20` is 1.312, CI [1.108, 1.554], second consecutive breach. Cohort maturity 7 months, above the 6-month floor (`05` OQ-631). | `05` FR-317, FR-318, FR-319, OQ-631 |
| G2 | Backend | Raises an Alert with the trend [1.18, 1.24, 1.312], affected exposure 1.7 %, and links to the evidence. Routes to the in-app inbox and the team webhook. | `05` FR-334, FR-335, FR-336 |
| G3 | Pricing Actuary | Opens the alert, drills overall → peril → factor → level → individual policies → their traces. No hand-written query anywhere. | `05` FR-321, R2 |
| G4 | Pricing Actuary | Cross-checks drift: PSI 0.148 on `annual_mileage`, and that factor is third by importance in the AD frequency model — so the drift is material, not incidental. | `05` FR-312/316 |
| G5 | Pricing Actuary | Acknowledges the alert with a note. Acknowledgement records who and why. | `05` FR-334 |
| G6 | Pricing Actuary | Raises a **Refit Recommendation** on `model:motor-ad-frequency@7`, citing the monitoring results and alerts. The platform does not refit anything by itself. | `05` FR-340 |
| G7 | Approver | Sees the recommendation in the inbox alongside approvals; accepts it. | `05` §4.5, `06` FR-358 |
| G8 | Analyst | Re-enters **WF-698** with a newer Dataset Version. | WF-698 |
| G9 | Pricing Actuary | Resolves the alert, recording the action taken and linking the refit recommendation. | `05` FR-334 |

### Phase H — Rollback (exception path, Deployer)

| # | Actor | Action | Refs |
|---|---|---|---|
| H1 | Consumer System | Reports that 3 % of quotes now return `RATE_TABLE_MISS`. | `03` FR-255 |
| H2 | Pricing Actuary | The operational dashboard confirms it; traces show a vehicle-group value absent from the new rate table. | `05` FR-331 |
| H3 | Deployer | `POST /environments/prod/deployments/rollback` — a single audited operation, no re-approval needed. | `03` FR-269 |
| H4 | Backend | Pre-warms the previous bundle, switches atomically, emits an Audit Event and a notification. | `03` FR-268/272 |
| H5 | Pricing Actuary | Roots the cause: the rate table was seeded from a model fitted before three new vehicle groups appeared, and `VR-REF-5 code-list-drift` had warned about exactly this — a warning that was acknowledged as immaterial. | `01` VR-REF-5 |
| H6 | Pricing Actuary | Adds a golden quote covering the new vehicle groups so this class of defect cannot recur silently. | `03` FR-260 |

---

## 3. Failure and exception paths

| Situation | Behaviour | Refs |
|---|---|---|
| Deploy to `prod` without `uat` | `PROMOTION_ORDER_VIOLATION` | `07` FR-429 |
| Deploy without complete approval | `DEPLOY_REQUIRES_APPROVAL` | `03` FR-267 |
| Replicas serving different bundle hashes | Immediate `breach` alert | `05` FR-333 |
| Metadata store unavailable | Scoring continues on the cached bundle (degraded, not down) | `03` NFR-497 |
| Monitoring worker outage | Visibility degrades; scoring is unaffected; missed runs are backfillable | `05` R3, NFR-517 |
| A/E computed on an immature cohort | Excluded from alerting and visually marked; never silently shown | `05` R4, FR-318 |
| A monitor fires every single run | Flagged as mis-thresholded rather than escalated | `05` FR-337 |
| Rate table miss in production | Typed per-quote error, visible in operational monitoring, rollback available | `03` FR-255, FR-269 |

---

## 4. Postconditions

- A live Deployment with a recorded actor, reason, and bundle hash.
- Monitors created automatically and running on their cadences.
- A monitoring history that answers "did the rate change land as intended?" with a
  decomposition rather than an opinion.
- An alert lifecycle from raise through acknowledgement to resolution, linked to the refit
  recommendation it produced.
- If rolled back: a complete record of what went live, what broke, when it was reverted,
  and the regression test that now prevents a recurrence.

---

## 5. Traceability

| Phase | Requirements exercised |
|---|---|
| A — UAT | `03` FR-RATE-45, 50, 51, 55 |
| B — Shadow | `03` FR-271; `05` FR-330 |
| C — Production | `03` FR-RATE-42, 50, 51; `05` FR-310; `07` FR-429 |
| D — First 48 h | `05` FR-MON-23, 25, 26, 27 |
| E — Ongoing | `05` FR-MON-1..3, 6..13, 17, 20, 32 |
| F — Rate achieved | `05` FR-326 |
| G — Breach | `05` FR-MON-15, 28..34; `06` FR-358 |
| H — Rollback | `03` FR-RATE-38, 43, 52 |

## 6. Timing

| Phase | Elapsed |
|---|---|
| A — UAT deployment | minutes; testing takes days |
| B — Shadow | a week, to accumulate a representative mix |
| C — Production switchover | < 30 s (NFR-494) |
| D — First 48 h watch | 48 h |
| E — Monitoring cadences | daily / weekly / monthly by family (`05` OQ-631) |
| G — Breach to refit decision | days; the refit itself re-enters WF-698 |
| H — Rollback | < 30 s once decided; deciding takes longer than doing |
