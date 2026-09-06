---
id: WF-698
family: workflow
title: Dataset to approved Model
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-08-14
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the Works that deliver this journey's steps
was: docs/workflows/wf-01-dataset-to-model.md
---

# WF-698 — Dataset to approved Model

**Modules:** `01-data-management` · `02-modelling` · `06-governance` · `07-platform`
**Primary actors:** Analyst, Pricing Actuary, Approver
**Trigger:** New or refreshed experience data is available for a line of business.
**Outcome:** An `approved` Model (or set of Models) that a Rating Version may reference.

---

## 1. Preconditions

| Condition | Owner |
|---|---|
| A Dataset exists with a Data Dictionary and a Validation Rule Set | `01` FR-69, §4.1 |
| The actor holds `dataset:create_version` and `model:fit` in scope | `06` FR-343/345 |
| A Reference Dataset Version is pinned on the Rule Set for distributional checks | `01` FR-57 |
| Reference Table Versions used by referential rules are `approved` | `01` FR-70 |

---

## 2. Main sequence

### Phase A — Ingestion (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| A1 | Analyst | Selects a registered Source, or registers one. Credentials are a `secret:` reference, entered once and never displayed again. | `01` FR-26, `07` FR-425 |
| A2 | Analyst | `POST /sources/{id}/preview` — sees the first 1 000 rows and the **inferred schema**: dtypes, nullability, candidate keys, detected date formats. | `01` FR-29 |
| A3 | Analyst | Corrects the inference where it is wrong (a numeric-looking policy id is a string; a date is `DD/MM/YYYY`, not `MM/DD/YYYY`). | `01` FR-29 |
| A4 | Analyst | Builds or reuses the **Preparation Recipe**: casts, date parsing, `explode_period` for mid-term changes, `attach_claims`, `pseudonymise` on the policy key. | `01` FR-35, FR-36, FR-37, FR-38, FR-39 |
| A5 | Frontend → Backend | `POST /datasets/{slug}/versions` → `202` + Job (`dataset.ingest`, queue `io`). | `07` FR-399/405 |
| A6 | Worker → pricing-core | `apply_recipe()` streams the source into parquet; unparseable rows go to `_rejected`, not to the floor. | `01` FR-32, FR-41 |
| A7 | Worker | Writes content-addressed parquet blobs; creates Dataset Version `v13`, status `draft`. | `01` FR-27, ID-4 |
| A8 | Worker → pricing-core | `profile_frame()` runs automatically: per-column stats, one-way frequency/severity/burning cost with confidence intervals. | `01` FR-60/61 |
| A9 | Analyst | Reviews the profile. This is the first honest look at the data — a 40 % null rate on `annual_mileage` is visible here, before anything is fitted. | `01` §5.3 |

**Checkpoint:** `dataset:motor-gb-quote-bind@13`, status `draft`, profiled, with a
rejected-row count of 17 out of 4.8 M.

### Phase B — Validation (Analyst → Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| B1 | Analyst | `POST /dataset-versions/{id}/validate` → `202` + Job (`dataset.validate`). | `01` FR-42 |
| B2 | Worker → pricing-core | Runs all four layers. Structural first so a broken feed fails in two minutes rather than ten. | `01` FR-45/54, NFR-466 |
| B3 | Worker | Persists the **Validation Report**: 41 pass, 3 warn, 1 fail, 1 skipped. | `01` FR-49, §4.6 |
| B4 | Analyst | Opens the validation view. The fail is `VR-ACT-5 claim-date-in-exposure`: 1 204 claims fall outside their linked exposure period. | `01` §5.3 |
| B5 | Analyst | Investigates via the offending sample — the cause is mid-term adjustments not exploded into separate exposure rows. | `01` FR-49 |
| B6 | Analyst | Fixes the Preparation Recipe (adds `explode_period`), returns to A5. **This loop is the normal case, not an exception.** | `01` FR-37 |
| B7 | — | Re-ingested as `v14`; revalidation gives 0 fail, 3 warn. | `01` FR-27 |
| B8 | Pricing Actuary | Reviews each warn. `VR-DST-1` PSI 0.148 on `driver_age`; `VR-ACT-10` flags 41 large losses; `VR-ACT-14` flags the last 4 months as immature. | `01` §4.4 |
| B9 | Pricing Actuary | Acknowledges each with a justification ("young-driver telematics product launched 2026-04"). An Analyst attempting this gets `ACKNOWLEDGE_FORBIDDEN_ROLE`. | `01` FR-46/47, `06` FR-343 |
| B10 | Pricing Actuary | `POST /dataset-versions/{id}/transition {"to":"validated"}`. | `01` FR-46 |
| B11 | Backend | Verifies invariants, transitions to `validated`, emits Audit Events in the same transaction. | `06` FR-368, R2 |

**Checkpoint:** `dataset:motor-gb-quote-bind@14`, status `validated`. Model fitting is now
possible. Before this point it was not, and there was no way to make it so.

### Phase C — Factors, bandings, groupings (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| C1 | Analyst | Creates a named **split** on `v14`: temporal, cutoff 2025-07-01, seed persisted. Both candidate models will use provably identical holdout rows. | `01` FR-73/76 |
| C2 | Analyst | Opens the factor workbench. One-ways come from the stored Profile — the same numbers as the validation report, because it is the same computation. | `01` FR-62, `02` §7.3 |
| C3 | Analyst | Proposes a banding on `driver_age` by `exposure_quantile`, 10 bands, minimum 200 claims per band; drags the 21/25 boundary to align with the licensing effect. | `02` FR-98 |
| C4 | Frontend | Recomputes band stats live as the boundary moves — exposure, claim count, frequency with CI. The consequence of the edit is visible before saving. | `02` §5.3 |
| C5 | Analyst | Saves `banding:driver-age-actuarial-v2@1`, which stores the method, parameters, and per-band evidence automatically. | `02` FR-99/101 |
| C6 | Analyst | Groups 50 ABI vehicle groups to 8 rating groups by `credibility_weighted`; reviews the deviance/df trade-off (deviance +166.7 for 42 df saved, χ² p = 0.31 — the simplification is not rejected). | `02` FR-105/107 |
| C7 | Analyst | Declares Factors: intent `risk`, monotonic direction `decreasing` on age above 25 with a written rationale. | `02` FR-83/88/89 |
| C8 | Analyst | Attempts to add `postcode_full` as a factor; it is `prohibited` with a recorded reason, and the attempt is refused and audited. | `02` FR-90 |

### Phase D — Fitting and diagnostics (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| D1 | Analyst | Builds a Model Spec: AD peril, `claim_count` response, Poisson, log link, `offset = log(exposure_years)`, 32 factors, seed. | `02` FR-111, §4.4 |
| D2 | Frontend → Backend | `POST /model-specs/validate` — factors resolve, offset present, no prohibited factor, objective applicable. Errors are caught before any compute is spent. | `02` FR-153 |
| D3 | Frontend → Backend | `POST /models` → `202` + Job (`model.fit`, queue `compute`). | `07` FR-405 |
| D4 | Worker → pricing-core | `fit_glm()` via glum; converged in 23 iterations, 184 s. | `02` FR-110, NFR-475 |
| D5 | Worker → pricing-core | `compute_diagnostics()` on train **and** holdout: A/E by factor, lift, calibration, Gini, type-III deviance tests, residuals. *(Amended 2026-08-24, WK-664. **Double lift is struck from this step.** FR-171 removed it on 2026-08-17 — it is pairwise, the comparison model is unknown at fit time, and `PartitionDiagnostics.double_lift` was structurally always null. It is not a `compute_diagnostics()` output; it lives on the comparison artifact, FR-186, which step E1 below already carries correctly. This step cited FR-171 while naming the instrument that same requirement struck, which is why the error survived a week of reading: the citation was right and the content it vouched for was not.)* | `02` FR-171/172/183 |
| D6 | Analyst | Reviews diagnostics. Holdout A/E on `driver_age_band 17-20` is 1.19 with a CI excluding 1.0 — the band is under-predicting. | `02` FR-171 |
| D7 | Analyst | Iterates: adds an `annual_mileage × driver_age` interaction factor, refits as `@2` with `change_reason: respecified`. | `02` FR-203 |
| D8 | Analyst | Also fits an XGBoost model on the same factors: `count:poisson`, `base_margin = log(exposure)`, monotone constraints derived from the factor declarations, early stopping on the declared holdout. | `02` FR-119, FR-120, FR-121, FR-122, FR-123, FR-124 |
| D9 | Worker | Refuses a first attempt that had no offset and no acknowledgement: `OFFSET_REQUIRED_FOR_FREQUENCY`. | `02` FR-121 |
| D10 | Analyst | `POST /models/{gbm_id}/transparency` → GLM approximation (R² 0.973) + SHAP summary, with a fidelity statement naming where the approximation fails and its exposure share. | `02` FR-132, FR-133, FR-134, FR-136 |

### Phase E — Selection, structure, approval (Pricing Actuary → Approver)

| # | Actor | Action | Refs |
|---|---|---|---|
| E1 | Pricing Actuary | `POST /models/compare` across the GLM and GBM candidates on the shared holdout — aligned metrics, double lift, factor-by-factor relativity differences. | `02` FR-186 |
| E2 | Pricing Actuary | Selects the GLM: the GBM's 1.8 % Gini advantage does not justify the transparency cost for this peril. **The comparison artifact records the decision's evidence.** | `02` FR-186 |
| E3 | Pricing Actuary | Repeats phases C–E for the remaining perils and for severity models. | — |
| E4 | Pricing Actuary | Assembles the **Peril Structure**: AD and TP_BI as frequency × severity, windscreen as burning cost, large losses capped at £25 k with a restoration loading. | `02` FR-188/189 |
| E5 | Worker → pricing-core | Reconciliation on the holdout: modelled burning cost 18 337 vs observed 18 412 (ratio 0.9959, tolerance 0.02) → pass. | `02` FR-190 |
| E6 | Pricing Actuary | `POST /models/{id}/submit` for each model and the structure. The evidence bundle assembles automatically: diagnostics, transparency, comparison, banding/grouping rationale, dataset lineage. | `06` FR-352/363 |
| E7 | Backend | Pins the evidence bundle; notifies eligible Approvers; emits Audit Events. | `06` FR-356 |
| E8 | Approver | Reviews in the inbox — diagnostics and diffs render inline; no other module needs opening. | `06` FR-358 |
| E9 | Approver | Approves with a comment. Attempting to approve their own submission returns `SUBMITTER_CANNOT_APPROVE`. | `06` R1, FR-353 |
| E10 | Backend | Transitions models and structure to `approved`; they become referenceable by a Rating Version. | `02` FR-202, FR-20 |

---

## 3. Failure and exception paths

| Situation | Behaviour | Refs |
|---|---|---|
| Ingestion fails midway | Version marked `failed`, blobs garbage-collected, version number consumed not reused; no partially-visible data | `01` FR-27, NFR-474 |
| Reject rate exceeds threshold | `VR-STR-9` fails validation; the version cannot become `validated` | `01` FR-32 |
| A validation rule times out | Recorded as `error`, which **blocks** validation — an unrun rule is never treated as a pass | `01` FR-48 |
| Analyst tries to acknowledge a warn | `ACKNOWLEDGE_FORBIDDEN_ROLE` | `01` FR-46 |
| Analyst tries to fit on a `draft` version | `DATASET_NOT_VALIDATED` — no override exists | `01` §1.3 |
| GLM fails to converge | `GLM_DID_NOT_CONVERGE` with suspect factors named; not retried (deterministic failure) | `02` FR-115, `07` FR-403 |
| GBM early stopping without a holdout | `EARLY_STOPPING_REQUIRES_HOLDOUT` | `02` FR-124 |
| GBM submitted without a transparency artifact | `TRANSPARENCY_ARTIFACT_REQUIRED` at submission | `02` R3 |
| A rule set change later fails the version | Version returns to `draft`; every model fitted on it is flagged `dataset_invalidated` and cannot advance to `approved` | `01` FR-53, `02` FR-205 |
| Fit exceeds its memory budget | Job terminated with `JOB_RESOURCE_BUDGET_EXCEEDED` naming the budget, not an opaque OOM kill | `07` FR-412 |

---

## 4. Postconditions

- `dataset:motor-gb-quote-bind@14` — `validated`, with an immutable validation report and
  three acknowledged warnings, each with a justification and an actor.
- A named split artifact both candidate models were evaluated on.
- Versioned bandings and groupings carrying their derivation method and evidence.
- `approved` Models per peril and response, each with diagnostics and lineage.
- An `approved` Peril Structure with a passing reconciliation.
- An unbroken audit trail from the source file's sha256 to the approval comment.

---

## 5. Traceability

| Phase | Requirements exercised |
|---|---|
| A — Ingestion | `01` FR-DATA-1..14, 25..28; `07` FR-PLAT-7..14, 21, 25 |
| B — Validation | `01` FR-42, FR-45, FR-46, FR-47, FR-48, FR-49, FR-50, FR-51, FR-53, FR-54; `06` FR-GOV-2, 20 |
| C — Factors | `01` FR-73, FR-74, FR-75, FR-76; `02` FR-83, FR-87, FR-88, FR-89, FR-90, FR-95, FR-96, FR-97, FR-98, FR-99, FR-100, FR-101, FR-104, FR-105, FR-107, FR-108, FR-109 |
| D — Fitting | `02` FR-MODEL-18..37, 49..57, 62..67 |
| E — Approval | `02` FR-MODEL-56, 58..61, 64; `06` FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363, FR-368, FR-369 |

## 6. Timing (typical, 5 M-row motor dataset)

| Phase | Elapsed | Of which compute |
|---|---|---|
| A — Ingestion + profiling | 25 min | 20 min |
| B — Validation (per attempt) | 10 min | 8 min |
| B — Investigation and recipe fix | hours to days | — |
| C — Factor work | hours to days | seconds per proposal |
| D — Per model fit + diagnostics | 5–25 min | nearly all |
| E — Approval | hours to days | 2 min (dossier) |

The compute is not the bottleneck, and the specification should not optimise as if it
were. The bottleneck is B6 (diagnosing why validation failed) and D6 (deciding whether a
diagnostic is acceptable) — which is why `01` §5.3 and `02` §5.3 place their interaction
requirements exactly there.
