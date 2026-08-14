# 05 — Monitoring

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `MON`
**Prerequisites:** [`00-overview.md`](00-overview.md) §2.4; [`01-data-management.md`](01-data-management.md) §3.4 (profiles/PSI); [`03-rating-engine.md`](03-rating-engine.md) §3.8 (traces).

---

## 1. Purpose & scope

### 1.1 In scope

Everything that answers "is the thing we deployed still working?":

1. **Input drift** — has the live population's factor distribution moved away from the
   modelling population?
2. **Model performance** — actual vs expected claims experience, by factor, cohort, and
   time; discrimination decay.
3. **Demand performance** — realised conversion and retention against demand-model
   expectations and against optimisation targets.
4. **Price and portfolio monitoring** — premium distribution, average premium, mix, rate
   achieved vs rate intended, loss ratio development.
5. **Operational monitoring** — scoring latency, error and decline rates, bundle
   deployment health, constraint activation rates.
6. **Alerting** — thresholds, notification routing, alert lifecycle.
7. **Dashboards** — the standing views a pricing team looks at weekly, and the
   investigation paths from a red number to the evidence behind it.

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Pre-deployment validation and dislocation | `01-data-management.md`, `03-rating-engine.md` |
| Fitting or refitting models in response to drift | `02-modelling.md` — monitoring *triggers* a refit, it does not perform one |
| Deciding a new price | `04-optimisation.md` |
| Infrastructure monitoring (CPU, disk, pod health) | `07-platform.md` — standard observability, not pricing monitoring |
| Claims reserving and IBNR development | Out of platform; developed claims are ingested (`01` OQ-DATA-4) |

### 1.3 Hard rules

> **R1 — Monitoring reuses the same statistics as validation and diagnostics.** PSI is
> `pricing-core.data.compare_profiles`; A/E is `pricing-core.modelling.compute_diagnostics`'
> A/E. A drift number on a dashboard and the same number in a validation report must be
> the same computation, or the platform is lying somewhere (`01` §7.3, `02` §7.3).
>
> **R2 — Every alert links to its evidence.** An alert that says "PSI 0.31 on driver_age"
> and cannot show the two distributions and the affected exposure is noise.
>
> **R3 — Monitoring never blocks scoring.** All aggregation is asynchronous and off the
> latency path; a monitoring outage degrades visibility, never availability.
>
> **R4 — Claims experience is reported with its maturity.** An A/E ratio quoted without
> the development maturity of the underlying period is misleading, and the platform
> refuses to display one (`01` VR-ACT-14).

---

## 2. Concepts & glossary

Terms from `00-overview.md` §2.4 are used unchanged. Additional terms owned here:

| Term | Definition |
|---|---|
| **Monitoring Baseline** | The reference distribution and expected performance a live population is compared against: normally the modelling Dataset Version's Profile plus the model's fit-time diagnostics. Pinned explicitly on the Monitor. |
| **Monitor** | A named, configured, scheduled comparison: what is measured, over what population, against which baseline, at what cadence, with what thresholds. The unit of configuration in this module. |
| **Monitoring Run** | One execution of a Monitor, producing a Monitoring Result artifact. |
| **Monitoring Result** | The persisted metrics from one run, with per-metric status (`ok` / `warn` / `breach`) and links to the evidence. |
| **Cohort** | A slice of live business by underwriting period (quote month, inception quarter), used so that experience is compared like with like. |
| **Maturity** | How developed a cohort's claims experience is, expressed as months of development and an expected development factor (R4). |
| **Rate Achieved** | The realised average premium change across the live book, versus **Rate Intended** — the change the dislocation run predicted. The gap is the single most-asked question after a rate change. |
| **Alert** | A raised, routed, acknowledgeable notification produced when a metric breaches a threshold. Has a lifecycle, not just a webhook. |
| **Shadow Comparison** | Comparison of live prices against a candidate Rating Version scored in shadow (`03` FR-RATE-54). |

---

## 3. Functional requirements

### 3.1 Monitors and runs

| ID | Requirement |
|---|---|
| **FR-MON-1** | A **Monitor** declares: the metric family (`input_drift`, `model_ae`, `demand`, `price_portfolio`, `operational`, `shadow`), the live population source (traces, a batch dataset, or both), the Monitoring Baseline, the segment breakdown, the cadence (`daily`, `weekly`, `monthly`), the thresholds, and the alert routing. |
| **FR-MON-2** | Monitors run on schedule as Jobs (Dagster-orchestrated), and can also be run on demand. Each run produces an immutable Monitoring Result (FR-OVR-1). |
| **FR-MON-3** | Monitoring Baselines are pinned to specific artifact versions, never "the current model". Rebaselining is an explicit, audited act with a required reason — because a silently moving baseline is how drift stops being detected. |
| **FR-MON-4** | A Monitor is automatically created (from a template) when a Rating Version is first deployed to `prod`, so a deployed structure is never unmonitored by default. The auto-created Monitor is editable and deletable, but deleting it is audited. |
| **FR-MON-5** | Monitoring Results retain their metric values indefinitely at aggregate level (they are small) and their supporting evidence for ≥ 13 months (NFR-OVR-6). |

### 3.2 Input drift

| ID | Requirement |
|---|---|
| **FR-MON-6** | Input drift compares the live population's factor distributions against the Monitoring Baseline's Profile using **the same PSI implementation as `01`** (R1), reporting per-factor PSI, the contributing bins, new and vanished levels, and null-rate shift. |
| **FR-MON-7** | Drift is reported **exposure-weighted and count-weighted**, since a shift in mix by exposure and a shift in quote volume mix are different problems with different causes. |
| **FR-MON-8** | Drift is computed against both the modelling baseline (has the world moved since we fitted?) and the prior period (what changed this week?), because the two answer different questions and teams need both. |
| **FR-MON-9** | Default thresholds are PSI > 0.10 `warn`, > 0.25 `breach`, configurable per factor — a factor known to be seasonal can carry a higher threshold with a recorded rationale. |
| **FR-MON-10** | Drift on a factor is reported alongside that factor's importance in the model, so a large shift in an unimportant factor does not generate the same urgency as a small shift in the dominant one. |

### 3.3 Model performance (A/E)

| ID | Requirement |
|---|---|
| **FR-MON-11** | **Actual vs Expected** is computed per model, per peril, by factor level, by cohort, and over time, using the same A/E computation as fit-time diagnostics (R1). Expected comes from the deployed model's predictions as recorded in traces or recomputed on the exposure dataset; actual comes from the claims data ingested through `01`. |
| **FR-MON-12** | Every A/E figure is displayed with its cohort maturity and the development assumption applied, or is not displayed at all (R4). Immature cohorts are visually distinct and excluded from threshold evaluation by default. |
| **FR-MON-13** | A/E is reported with confidence intervals reflecting claim-count volume, so a 1.4 A/E on 12 claims is not presented with the same weight as a 1.05 on 4 000. |
| **FR-MON-14** | Discrimination decay is tracked: Gini / normalised Gini and lift-curve shape on live cohorts versus at fit time, once a cohort is sufficiently mature. |
| **FR-MON-15** | A/E breaches produce a drill-down path: overall → peril → factor → level → individual policies with their traces, so an actuary can go from a red cell to actual quotes in a few clicks (R2). |
| **FR-MON-16** | Where a model was deployed in `approximation` mode (`03` FR-RATE-10), monitoring additionally reports the realised approximation error against the exact model on a sample, closing the loop on the fidelity statement (`02` FR-MODEL-36). |

### 3.4 Demand performance

| ID | Requirement |
|---|---|
| **FR-MON-17** | Realised conversion and retention are measured by segment and compared with (a) the demand model's predictions and (b) the expectations declared in the Optimisation Run that motivated the current prices (`04` FR-OPT-28). |
| **FR-MON-18** | Realised price elasticity is estimated from live variation where sufficient variation exists, and compared with the demand model's fitted elasticity — with the identifiability caveat from `04` FR-OPT-2 shown alongside, never hidden. |
| **FR-MON-19** | Conversion monitoring is broken down by channel and by competitive position where that data is available, because an aggregate conversion drop usually has a channel-specific cause. |

### 3.5 Price and portfolio monitoring

| ID | Requirement |
|---|---|
| **FR-MON-20** | **Rate achieved vs rate intended**: the realised average premium change on live business is compared with the dislocation run's prediction for the same population, decomposed into the pure rate effect and the mix effect. A gap between the two is the most common post-rate-change question and must be answerable directly. |
| **FR-MON-21** | Premium distribution, average premium, and portfolio mix are tracked over time by segment, against baseline and prior period. |
| **FR-MON-22** | Loss ratio is tracked by cohort with development, on both an earned and a written basis, with the maturity treatment of R4. |
| **FR-MON-23** | Constraint activation rates are tracked: how often minimum premium binds, how often a cap applies, how often a decline fires. A constraint that suddenly binds on 30 % of quotes is a structural signal, not a footnote. |
| **FR-MON-24** | Where shadow scoring is enabled (`03` FR-RATE-54), the shadow candidate's price distribution is compared against live continuously, giving pre-deployment confidence beyond a point-in-time dislocation run. |

### 3.6 Operational monitoring

| ID | Requirement |
|---|---|
| **FR-MON-25** | Scoring latency (p50/p95/p99), throughput, error rate by error code, and decline rate by reason code are tracked per environment and per Rating Version, with the deployment timeline overlaid so a change in shape is attributable to a deployment. |
| **FR-MON-26** | Reference lookup misses and rate table misses are tracked as first-class metrics — they are the early warning that reference data has gone stale (`01` FR-DATA-30). |
| **FR-MON-27** | Bundle health is tracked: which bundle hash is serving in each environment, cache hit rate, and any divergence between replicas. Divergence is an immediate `breach`. |

### 3.7 Alerting

| ID | Requirement |
|---|---|
| **FR-MON-28** | An **Alert** has a lifecycle: `raised → acknowledged → resolved` (or `suppressed` with an expiry and a reason). Acknowledgement records who and why; resolution records what was done. |
| **FR-MON-29** | Alerts carry their evidence: the metric, the threshold, the trend, the affected segment and exposure, and links to the underlying Monitoring Result and drill-down (R2). |
| **FR-MON-30** | Alert routing is configurable per Monitor: in-app inbox, email, and webhook (Slack/Teams/PagerDuty-compatible). Routing failures are themselves logged and surfaced. |
| **FR-MON-31** | Alert fatigue is designed against: alerts deduplicate on `(monitor, metric, segment)`, escalate rather than repeat, and a Monitor that has fired every run for N runs is flagged as mis-thresholded. |
| **FR-MON-32** | Breach thresholds can be **absolute** (PSI > 0.25) or **relative** (A/E outside the CI implied by claim volume), and a Monitor may require **N consecutive breaches** before alerting, so a single noisy day does not page anyone. |

### 3.8 Reporting and feedback into the lifecycle

| ID | Requirement |
|---|---|
| **FR-MON-33** | A scheduled **monitoring pack** can be generated per portfolio: a document assembling the standing metrics, breaches, and commentary for a pricing committee, produced from persisted artifacts only (`06-governance.md` generation rules). |
| **FR-MON-34** | Monitoring can raise a **refit recommendation** on a Model — a structured record citing the drift/A-E evidence — which appears on the model and in the Approvals inbox as a prompt. It never triggers an automated refit. |
| **FR-MON-35** | Monitoring results are linked bidirectionally to the artifacts they concern: from a Model or Rating Version, "how is this performing live?" is one navigation step. |

---

## 4. Data contracts

### 4.1 `Monitor`

```json
{
  "slug": "motor-gb-prod-weekly",
  "environment": "prod",
  "metric_family": "model_ae",
  "population": {"kind": "traces_plus_claims",
                 "trace_sample_rate": 0.01,
                 "claims_dataset_id": "uuid"},
  "baseline": {"kind": "model_fit",
               "model_ref": "peril_structure:motor-gb-2026h2@2",
               "profile_dataset_version_id": "uuid",
               "pinned_at": "2026-10-01T00:00:00Z",
               "rebaseline_reason": null},
  "segments": ["peril", "driver_age_band", "rating_area_group", "distribution_channel"],
  "cadence": "weekly",
  "maturity_policy": {"min_development_months": 6, "development_pattern_ref": "uuid",
                      "exclude_immature_from_alerts": true},
  "thresholds": [
    {"metric": "ae_ratio", "kind": "relative_ci", "confidence": 0.95,
     "warn_outside": 0.90, "breach_outside": 0.99, "consecutive_required": 2},
    {"metric": "gini_delta", "kind": "absolute", "warn_below": -0.02, "breach_below": -0.05}
  ],
  "routing": [{"channel": "in_app", "to": "pricing-team"},
              {"channel": "webhook", "url_secret_ref": "secret:slack-pricing"}],
  "enabled": true
}
```

### 4.2 `MonitoringResult`

```json
{
  "monitor_id": "uuid", "run_id": "uuid",
  "period": {"from": "2026-11-01", "to": "2026-11-30"},
  "population": {"quotes": 412_884, "policies": 84_120, "exposure_years": "7018.4",
                 "claims": 1_204, "maturity_months": 7},
  "metrics": [
    {"name": "ae_ratio", "segment": {"peril": "AD"}, "value": 1.042,
     "expected": 1.0, "ci_95": [0.981, 1.106], "status": "ok",
     "actual": {"claim_count": 892, "claim_amount_minor": 3_884_100_00},
     "expected_values": {"claim_count": 856.1, "claim_amount_minor": 3_728_400_00}},
    {"name": "ae_ratio", "segment": {"peril": "AD", "driver_age_band": "17-20"},
     "value": 1.312, "ci_95": [1.108, 1.554], "status": "breach",
     "actual": {"claim_count": 118}, "expected_values": {"claim_count": 89.9},
     "evidence": {"drill_down_query": "…", "trace_sample_blob": "blob:sha256:…"}},
    {"name": "psi", "segment": {"factor": "annual_mileage"}, "value": 0.148,
     "status": "warn", "weighting": "exposure",
     "evidence": {"distribution_blob": "blob:sha256:…", "top_contributing_bins": ["<5000", "5000-8000"]}}
  ],
  "summary": {"ok": 84, "warn": 3, "breach": 1},
  "alerts_raised": ["uuid"]
}
```

### 4.3 `RateAchievedResult`

```json
{
  "rating_version_ref": "rating_version:motor-gb@27",
  "deployed_at": "2026-10-01T06:00:00Z",
  "period": {"from": "2026-10-01", "to": "2026-11-30"},
  "rate_intended_pct": 1.95,
  "rate_achieved_pct": 1.12,
  "gap_pct": -0.83,
  "decomposition": [
    {"effect": "pure_rate", "contribution_pct": 1.94,
     "note": "Matches dislocation prediction; the structure is doing what was expected."},
    {"effect": "mix_shift", "contribution_pct": -0.79,
     "note": "Aggregator share of new business rose 4.1pp; that channel skews to cheaper risks."},
    {"effect": "constraint_activation", "contribution_pct": -0.03,
     "note": "Minimum premium bound on 0.4% of quotes vs 0.9% predicted."}
  ],
  "dislocation_run_id": "uuid"
}
```

### 4.4 `Alert`

```json
{
  "monitor_id": "uuid", "monitoring_result_id": "uuid",
  "metric": "ae_ratio", "segment": {"peril": "AD", "driver_age_band": "17-20"},
  "severity": "breach",
  "value": 1.312, "threshold": "outside 95% CI for 2 consecutive runs",
  "trend": [1.18, 1.24, 1.312],
  "affected": {"policies": 8_412, "exposure_years": "7104.2", "exposure_share": 0.017},
  "status": "raised | acknowledged | resolved | suppressed",
  "raised_at": "2026-12-01T07:00:00Z",
  "acknowledged": {"user_id": "uuid", "at": "2026-12-01T09:14:00Z",
                   "note": "Consistent with the telematics launch mix; investigating whether the AD frequency model needs a refit."},
  "resolution": {"at": "2026-12-18T16:02:00Z", "action": "refit_recommended",
                 "refit_recommendation_id": "uuid",
                 "note": "Refit AD frequency on data including 2026H2; young-driver band under-predicting."},
  "suppression": null,
  "evidence_links": ["/monitoring/prod/results/uuid#ae-AD-17-20"]
}
```

### 4.5 `RefitRecommendation`

```json
{
  "model_ref": "model:motor-ad-frequency@7",
  "raised_by_monitor_id": "uuid",
  "reason": "A/E 1.31 (CI 1.11–1.55) for driver_age_band 17-20 over two consecutive monthly runs; PSI 0.15 on annual_mileage; Gini down 0.03 vs fit.",
  "evidence": {"monitoring_result_ids": ["uuid", "uuid"], "alert_ids": ["uuid"]},
  "suggested_dataset_version_id": "uuid",
  "status": "open | accepted | rejected | superseded",
  "decision": {"user_id": "uuid", "at": "2026-12-19T11:00:00Z", "note": "Accepted; refit scheduled for January."}
}
```

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/monitors` | Create a Monitor (FR-MON-1) |
| `GET` | `/api/v1/monitors?environment=` | List monitors with last run status |
| `POST` | `/api/v1/monitors/{id}/run` | **202** Run on demand → Job |
| `POST` | `/api/v1/monitors/{id}/rebaseline` | Rebaseline with a required reason (FR-MON-3) |
| `GET` | `/api/v1/monitoring-results/{id}` | Result artifact with metrics and evidence links |
| `GET` | `/api/v1/monitoring/drift?environment=&from=&to=` | Drift time series by factor (FR-MON-6..10) |
| `GET` | `/api/v1/monitoring/ae?model=&segment=&cohort=` | A/E with CIs and maturity (FR-MON-11..13) |
| `GET` | `/api/v1/monitoring/rate-achieved?rating_version=` | Rate achieved vs intended with decomposition (FR-MON-20) |
| `GET` | `/api/v1/monitoring/demand?segment=` | Realised vs expected conversion/retention (FR-MON-17) |
| `GET` | `/api/v1/monitoring/operational?environment=` | Latency, errors, declines, bundle health (FR-MON-25..27) |
| `GET` | `/api/v1/alerts?status=` | Alert inbox |
| `POST` | `/api/v1/alerts/{id}/acknowledge` | Acknowledge with a note (FR-MON-28) |
| `POST` | `/api/v1/alerts/{id}/resolve` | Resolve with an action and note |
| `POST` | `/api/v1/alerts/{id}/suppress` | Suppress with expiry and reason |
| `POST` | `/api/v1/refit-recommendations` | Raise a refit recommendation (FR-MON-34) |
| `POST` | `/api/v1/monitoring-packs` | **202** Generate a committee pack (FR-MON-33) |

**Error codes owned by this module:** `BASELINE_NOT_PINNED`, `INSUFFICIENT_MATURITY`,
`INSUFFICIENT_CLAIM_VOLUME`, `MONITOR_POPULATION_EMPTY`, `REBASELINE_REASON_REQUIRED`,
`ALERT_ALREADY_RESOLVED`, `SUPPRESSION_EXPIRY_REQUIRED`.

### 5.2 `pricing-core` interfaces

```python
# pricing_core/monitoring/drift.py — thin wrappers over the data module (R1)
def drift_report(live: Profile, baseline: Profile, *,
                 weighting: Literal["exposure", "count"]) -> DriftReport
   # delegates to pricing_core.data.profile.compare_profiles

# pricing_core/monitoring/performance.py
def actual_vs_expected(actuals: pl.LazyFrame, expected: pl.LazyFrame,
                       *, segments: Sequence[str],
                       maturity: MaturityPolicy) -> AeReport
   # delegates to pricing_core.modelling.diagnostics for the A/E kernel
def discrimination(actuals: pl.LazyFrame, predictions: pl.LazyFrame) -> DiscriminationReport

# pricing_core/monitoring/rate.py
def rate_achieved(live_quotes: pl.LazyFrame, baseline_quotes: pl.LazyFrame,
                  dislocation: DislocationRun) -> RateAchievedResult   # FR-MON-20

# pricing_core/monitoring/demand.py
def realised_demand(quotes: pl.LazyFrame, outcomes: pl.LazyFrame,
                    demand_model: Model, *, segments: Sequence[str]) -> DemandPerformance

# pricing_core/monitoring/evaluate.py
def evaluate_thresholds(metrics: Sequence[Metric],
                        thresholds: Sequence[Threshold],
                        history: Sequence[MonitoringResult]) -> list[MetricStatus]
```

The delegation comments are load-bearing: this module owns *scheduling, thresholds,
alerting, and presentation*, not statistics (R1).

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Monitoring home | `/monitoring/:environment` | Status tiles per metric family, breach count, deployment timeline overlay, last-run freshness |
| Drift | `/monitoring/:environment/drift` | PSI heat map factor × period, distribution comparison chart per factor, importance-weighted ordering (FR-MON-10) |
| A/E | `/monitoring/:environment/ae` | A/E grid by factor level with CI shading and maturity badges, cohort development view, drill-down to policies and traces |
| Rate achieved | `/monitoring/:environment/rate` | Intended vs achieved with the decomposition waterfall (FR-MON-20) |
| Demand | `/monitoring/:environment/demand` | Conversion/retention realised vs expected by segment and channel, elasticity comparison |
| Operational | `/monitoring/:environment/ops` | Latency percentiles, error/decline rates by code, lookup miss rates, bundle health per replica |
| Alerts | `/monitoring/alerts` | Inbox with severity, trend sparkline, affected exposure, acknowledge/resolve/suppress actions |
| Monitor config | `/monitoring/monitors/:id` | Baseline pin, segments, thresholds, cadence, routing, mis-threshold warning (FR-MON-31) |

**Interaction requirement:** every red number is a link. The path from a breach tile to
the individual policies behind it must be traversable without leaving the module or
constructing a query by hand (R2, FR-MON-15).

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | Backend | On first `prod` deployment, auto-creates the template Monitors (FR-MON-4) |
| 2 | Worker (Dagster) | On cadence, aggregates traces and claims into the monitoring population |
| 3 | Worker → pricing-core | Computes drift, A/E, demand, rate-achieved, operational metrics |
| 4 | Backend | Evaluates thresholds with consecutive-breach logic; persists the Monitoring Result |
| 5 | Backend | Raises, deduplicates, and routes Alerts (FR-MON-30/31) |
| 6 | Pricing Actuary | Reviews the alert, drills through to affected policies and traces |
| 7 | Pricing Actuary | Acknowledges with a note; investigates |
| 8 | Pricing Actuary | Raises a Refit Recommendation (FR-MON-34) or a rate-change action, or resolves as noise |
| 9 | — | A refit re-enters `wf-01`; a rate change re-enters `wf-03` |

Full journey: [`wf-04-deploy-and-monitor.md`](../workflows/wf-04-deploy-and-monitor.md).

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What |
|---|---|
| `03-rating-engine` | Sampled production traces, deployment events, premium ladders, per-peril risk premium, constraint activations, dislocation runs (for rate-intended) |
| `01-data-management` | Claims and exposure Dataset Versions for actuals; Profiles as baselines; the PSI implementation (R1) |
| `02-modelling` | Fit-time diagnostics as the performance baseline; the A/E kernel (R1); factor importances for FR-MON-10 |
| `04-optimisation` | Expected volume/profit/loss-ratio targets from the Optimisation Run behind current prices |
| `07-platform` | Job scheduling (Dagster), notification channels, secrets for webhooks, time-series storage |

### 7.2 Provides

| To | What |
|---|---|
| `02-modelling` | Refit recommendations with evidence |
| `03-rating-engine` | Evidence that a rate change did or did not land as intended; shadow-scoring comparisons |
| `04-optimisation` | Realised elasticity and conversion/retention, closing the optimisation loop (`04` FR-OPT-28) |
| `06-governance` | Monitoring packs and ongoing-performance evidence for model documentation and regulatory response |

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **Dagster** | Scheduled monitoring pipelines, partitioned by period | Partitioned assets keyed by monitoring period; backfills when a Monitor is created late; sensors for deployment-triggered monitor creation |
| **DuckDB** | Aggregating sampled traces and claims into monitoring populations | Querying trace parquet at scale; window functions for cohort development |
| **Polars** | Metric computation, joins between quotes, policies, and claims | Reused `pricing-core` kernels (R1) |
| **PostgreSQL 16** | Monitors, results, alerts; time-series of aggregate metrics | Partitioning the results table by period; JSONB metric bodies with GIN indexes |
| **SciPy** | A/E confidence intervals at low claim counts; discrimination statistics | Exact Poisson CIs (`01` FR-DATA-26 reuse) |
| **Notification channels** | Webhook/email routing | Retry and failure surfacing (FR-MON-30); secret references for webhook URLs |
| **OpenTelemetry / metrics backend** | Operational metrics (latency, errors) | Deriving p99 from histogram buckets correctly; joining ops metrics to deployment events |
| **ECharts (frontend)** | PSI heat maps, A/E grids with CI shading, decomposition waterfalls, trend sparklines | Heat map performance at factor × period scale; linked drill-down interactions |

New skills this spec adds to `skills-map.md`: claims development/maturity treatment for
live monitoring; alert lifecycle and fatigue design; rate achieved vs intended
decomposition (pure rate vs mix); Dagster partitioned assets and backfills.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-MON-1** | A weekly monitoring run over 400 k quotes and 1 200 claims completes in < 10 min. |
| **NFR-MON-2** | Monitoring is fully asynchronous; no monitoring component sits on the scoring latency path (R3). |
| **NFR-MON-3** | Dashboard reads return in < 500 ms from persisted Monitoring Results; no dashboard computes a metric on request. |
| **NFR-MON-4** | Metric values are identical to those produced by the equivalent validation or diagnostic computation on the same data, verified by a shared test suite (R1). |
| **NFR-MON-5** | Alert delivery within 5 minutes of the run completing; routing failures are retried with backoff and surfaced in-app. |
| **NFR-MON-6** | Aggregate metric history is retained indefinitely; supporting evidence blobs for ≥ 13 months (NFR-OVR-6). |
| **NFR-MON-7** | Audit: monitor creation/edit, rebaselining, threshold changes, alert acknowledgement/resolution/suppression, and refit decisions all emit Audit Events. |
| **NFR-MON-8** | A monitoring outage does not lose data: traces and claims remain in their source stores and a missed run is backfillable (FR-MON-2, Dagster backfill). |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-MON-1** | Is a 1 % trace sample sufficient for segment-level A/E monitoring? At 1 % of 50 M quotes, thin segments have too few observations to say anything. Options: raise the sample rate, stratify sampling by segment, or compute A/E from a full batch re-score of the exposure dataset instead of from traces. |
| **OQ-MON-2** | Do we store monitoring time series in PostgreSQL or adopt a dedicated time-series store? Postgres is simpler and adequate at weekly cadence; daily operational metrics at per-replica granularity may outgrow it. |
| **OQ-MON-3** | Who owns the claims-development pattern used for maturity adjustment (R4) — is it supplied by the user as reference data, fitted by the platform from claim triangles, or out of scope (tied to `01` OQ-DATA-4)? |
| **OQ-MON-4** | Should the platform support automated **champion/challenger** — routing a slice of live traffic to a candidate Rating Version and comparing realised outcomes — or is shadow scoring (no customer impact) the ethical and practical limit? |
| **OQ-MON-5** | What is the right default cadence set? Weekly for A/E is too frequent to be meaningful on low-frequency perils but monthly is too slow to catch a broken feed. Likely different cadences per metric family — needs to be specified rather than left to the user. |
