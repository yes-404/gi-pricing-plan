# WF-01 — Dataset to approved Model

**Modules:** `01-data-management` · `02-modelling` · `06-governance` · `07-platform`
**Primary actors:** Analyst, Pricing Actuary, Approver
**Trigger:** New or refreshed experience data is available for a line of business.
**Outcome:** An `approved` Model (or set of Models) that a Rating Version may reference.

---

## 1. Preconditions

| Condition | Owner |
|---|---|
| A Dataset exists with a Data Dictionary and a Validation Rule Set | `01` FR-DATA-29, §4.1 |
| The actor holds `dataset:create_version` and `model:fit` in scope | `06` FR-GOV-2/4 |
| A Reference Dataset Version is pinned on the Rule Set for distributional checks | `01` FR-DATA-55 |
| Reference Table Versions used by referential rules are `approved` | `01` FR-DATA-30 |

---

## 2. Main sequence

### Phase A — Ingestion (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| A1 | Analyst | Selects a registered Source, or registers one. Credentials are a `secret:` reference, entered once and never displayed again. | `01` FR-DATA-1, `07` FR-PLAT-25 |
| A2 | Analyst | `POST /sources/{id}/preview` — sees the first 1 000 rows and the **inferred schema**: dtypes, nullability, candidate keys, detected date formats. | `01` FR-DATA-4 |
| A3 | Analyst | Corrects the inference where it is wrong (a numeric-looking policy id is a string; a date is `DD/MM/YYYY`, not `MM/DD/YYYY`). | `01` FR-DATA-4 |
| A4 | Analyst | Builds or reuses the **Preparation Recipe**: casts, date parsing, `explode_period` for mid-term changes, `attach_claims`, `pseudonymise` on the policy key. | `01` FR-DATA-9..13 |
| A5 | Frontend → Backend | `POST /datasets/{slug}/versions` → `202` + Job (`dataset.ingest`, queue `io`). | `07` FR-PLAT-7/13 |
| A6 | Worker → pricing-core | `apply_recipe()` streams the source into parquet; unparseable rows go to `_rejected`, not to the floor. | `01` FR-DATA-7, FR-DATA-14 |
| A7 | Worker | Writes content-addressed parquet blobs; creates Dataset Version `v13`, status `draft`. | `01` FR-DATA-2, ID-4 |
| A8 | Worker → pricing-core | `profile_frame()` runs automatically: per-column stats, one-way frequency/severity/burning cost with confidence intervals. | `01` FR-DATA-25/26 |
| A9 | Analyst | Reviews the profile. This is the first honest look at the data — a 40 % null rate on `annual_mileage` is visible here, before anything is fitted. | `01` §5.3 |

**Checkpoint:** `dataset:motor-gb-quote-bind@13`, status `draft`, profiled, with a
rejected-row count of 17 out of 4.8 M.

### Phase B — Validation (Analyst → Pricing Actuary)

| # | Actor | Action | Refs |
|---|---|---|---|
| B1 | Analyst | `POST /dataset-versions/{id}/validate` → `202` + Job (`dataset.validate`). | `01` FR-DATA-15 |
| B2 | Worker → pricing-core | Runs all four layers. Structural first so a broken feed fails in two minutes rather than ten. | `01` FR-DATA-16/24, NFR-DATA-2 |
| B3 | Worker | Persists the **Validation Report**: 41 pass, 3 warn, 1 fail, 1 skipped. | `01` FR-DATA-20, §4.6 |
| B4 | Analyst | Opens the validation view. The fail is `VR-ACT-5 claim-date-in-exposure`: 1 204 claims fall outside their linked exposure period. | `01` §5.3 |
| B5 | Analyst | Investigates via the offending sample — the cause is mid-term adjustments not exploded into separate exposure rows. | `01` FR-DATA-20 |
| B6 | Analyst | Fixes the Preparation Recipe (adds `explode_period`), returns to A5. **This loop is the normal case, not an exception.** | `01` FR-DATA-11 |
| B7 | — | Re-ingested as `v14`; revalidation gives 0 fail, 3 warn. | `01` FR-DATA-2 |
| B8 | Pricing Actuary | Reviews each warn. `VR-DST-1` PSI 0.148 on `driver_age`; `VR-ACT-10` flags 41 large losses; `VR-ACT-14` flags the last 4 months as immature. | `01` §4.4 |
| B9 | Pricing Actuary | Acknowledges each with a justification ("young-driver telematics product launched 2026-04"). An Analyst attempting this gets `ACKNOWLEDGE_FORBIDDEN_ROLE`. | `01` FR-DATA-17/18, `06` FR-GOV-2 |
| B10 | Pricing Actuary | `POST /dataset-versions/{id}/transition {"to":"validated"}`. | `01` FR-DATA-17 |
| B11 | Backend | Verifies invariants, transitions to `validated`, emits Audit Events in the same transaction. | `06` FR-GOV-20, R2 |

**Checkpoint:** `dataset:motor-gb-quote-bind@14`, status `validated`. Model fitting is now
possible. Before this point it was not, and there was no way to make it so.

### Phase C — Factors, bandings, groupings (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| C1 | Analyst | Creates a named **split** on `v14`: temporal, cutoff 2025-07-01, seed persisted. Both candidate models will use provably identical holdout rows. | `01` FR-DATA-33/36 |
| C2 | Analyst | Opens the factor workbench. One-ways come from the stored Profile — the same numbers as the validation report, because it is the same computation. | `01` FR-DATA-27, `02` §7.3 |
| C3 | Analyst | Proposes a banding on `driver_age` by `exposure_quantile`, 10 bands, minimum 200 claims per band; drags the 21/25 boundary to align with the licensing effect. | `02` FR-MODEL-9 |
| C4 | Frontend | Recomputes band stats live as the boundary moves — exposure, claim count, frequency with CI. The consequence of the edit is visible before saving. | `02` §5.3 |
| C5 | Analyst | Saves `banding:driver-age-actuarial-v2@1`, which stores the method, parameters, and per-band evidence automatically. | `02` FR-MODEL-10/12 |
| C6 | Analyst | Groups 50 ABI vehicle groups to 8 rating groups by `credibility_weighted`; reviews the deviance/df trade-off (deviance +166.7 for 42 df saved, χ² p = 0.31 — the simplification is not rejected). | `02` FR-MODEL-14/15 |
| C7 | Analyst | Declares Factors: intent `risk`, monotonic direction `decreasing` on age above 25 with a written rationale. | `02` FR-MODEL-1/3/4 |
| C8 | Analyst | Attempts to add `postcode_full` as a factor; it is `prohibited` with a recorded reason, and the attempt is refused and audited. | `02` FR-MODEL-5 |

### Phase D — Fitting and diagnostics (Analyst)

| # | Actor | Action | Refs |
|---|---|---|---|
| D1 | Analyst | Builds a Model Spec: AD peril, `claim_count` response, Poisson, log link, `offset = log(exposure_years)`, 32 factors, seed. | `02` FR-MODEL-19, §4.4 |
| D2 | Frontend → Backend | `POST /model-specs/validate` — factors resolve, offset present, no prohibited factor, objective applicable. Errors are caught before any compute is spent. | `02` FR-MODEL-44 |
| D3 | Frontend → Backend | `POST /models` → `202` + Job (`model.fit`, queue `compute`). | `07` FR-PLAT-13 |
| D4 | Worker → pricing-core | `fit_glm()` via glum; converged in 23 iterations, 184 s. | `02` FR-MODEL-18, NFR-MODEL-1 |
| D5 | Worker → pricing-core | `compute_diagnostics()` on train **and** holdout: A/E by factor, lift, calibration, Gini, type-III deviance tests, residuals. *(Amended 2026-08-24, W6b. **Double lift is struck from this step.** FR-MODEL-50 removed it on 2026-08-17 — it is pairwise, the comparison model is unknown at fit time, and `PartitionDiagnostics.double_lift` was structurally always null. It is not a `compute_diagnostics()` output; it lives on the comparison artifact, FR-MODEL-56, which step E1 below already carries correctly. This step cited FR-MODEL-50 while naming the instrument that same requirement struck, which is why the error survived a week of reading: the citation was right and the content it vouched for was not.)* | `02` FR-MODEL-50/51/54 |
| D6 | Analyst | Reviews diagnostics. Holdout A/E on `driver_age_band 17-20` is 1.19 with a CI excluding 1.0 — the band is under-predicting. | `02` FR-MODEL-50 |
| D7 | Analyst | Iterates: adds an `annual_mileage × driver_age` interaction factor, refits as `@2` with `change_reason: respecified`. | `02` FR-MODEL-65 |
| D8 | Analyst | Also fits an XGBoost model on the same factors: `count:poisson`, `base_margin = log(exposure)`, monotone constraints derived from the factor declarations, early stopping on the declared holdout. | `02` FR-MODEL-25..30 |
| D9 | Worker | Refuses a first attempt that had no offset and no acknowledgement: `OFFSET_REQUIRED_FOR_FREQUENCY`. | `02` FR-MODEL-27 |
| D10 | Analyst | `POST /models/{gbm_id}/transparency` → GLM approximation (R² 0.973) + SHAP summary, with a fidelity statement naming where the approximation fails and its exposure share. | `02` FR-MODEL-33..36 |

### Phase E — Selection, structure, approval (Pricing Actuary → Approver)

| # | Actor | Action | Refs |
|---|---|---|---|
| E1 | Pricing Actuary | `POST /models/compare` across the GLM and GBM candidates on the shared holdout — aligned metrics, double lift, factor-by-factor relativity differences. | `02` FR-MODEL-56 |
| E2 | Pricing Actuary | Selects the GLM: the GBM's 1.8 % Gini advantage does not justify the transparency cost for this peril. **The comparison artifact records the decision's evidence.** | `02` FR-MODEL-56 |
| E3 | Pricing Actuary | Repeats phases C–E for the remaining perils and for severity models. | — |
| E4 | Pricing Actuary | Assembles the **Peril Structure**: AD and TP_BI as frequency × severity, windscreen as burning cost, large losses capped at £25 k with a restoration loading. | `02` FR-MODEL-58/59 |
| E5 | Worker → pricing-core | Reconciliation on the holdout: modelled burning cost 18 337 vs observed 18 412 (ratio 0.9959, tolerance 0.02) → pass. | `02` FR-MODEL-60 |
| E6 | Pricing Actuary | `POST /models/{id}/submit` for each model and the structure. The evidence bundle assembles automatically: diagnostics, transparency, comparison, banding/grouping rationale, dataset lineage. | `06` FR-GOV-10/19 |
| E7 | Backend | Pins the evidence bundle; notifies eligible Approvers; emits Audit Events. | `06` FR-GOV-14 |
| E8 | Approver | Reviews in the inbox — diagnostics and diffs render inline; no other module needs opening. | `06` FR-GOV-16 |
| E9 | Approver | Approves with a comment. Attempting to approve their own submission returns `SUBMITTER_CANNOT_APPROVE`. | `06` R1, FR-GOV-11 |
| E10 | Backend | Transitions models and structure to `approved`; they become referenceable by a Rating Version. | `02` FR-MODEL-64, FR-OVR-14 |

---

## 3. Failure and exception paths

| Situation | Behaviour | Refs |
|---|---|---|
| Ingestion fails midway | Version marked `failed`, blobs garbage-collected, version number consumed not reused; no partially-visible data | `01` FR-DATA-2, NFR-DATA-10 |
| Reject rate exceeds threshold | `VR-STR-9` fails validation; the version cannot become `validated` | `01` FR-DATA-7 |
| A validation rule times out | Recorded as `error`, which **blocks** validation — an unrun rule is never treated as a pass | `01` FR-DATA-19 |
| Analyst tries to acknowledge a warn | `ACKNOWLEDGE_FORBIDDEN_ROLE` | `01` FR-DATA-17 |
| Analyst tries to fit on a `draft` version | `DATASET_NOT_VALIDATED` — no override exists | `01` §1.3 |
| GLM fails to converge | `GLM_DID_NOT_CONVERGE` with suspect factors named; not retried (deterministic failure) | `02` FR-MODEL-23, `07` FR-PLAT-11 |
| GBM early stopping without a holdout | `EARLY_STOPPING_REQUIRES_HOLDOUT` | `02` FR-MODEL-30 |
| GBM submitted without a transparency artifact | `TRANSPARENCY_ARTIFACT_REQUIRED` at submission | `02` R3 |
| A rule set change later fails the version | Version returns to `draft`; every model fitted on it is flagged `dataset_invalidated` and cannot advance to `approved` | `01` FR-DATA-23, `02` FR-MODEL-67 |
| Fit exceeds its memory budget | Job terminated with `JOB_RESOURCE_BUDGET_EXCEEDED` naming the budget, not an opaque OOM kill | `07` FR-PLAT-16 |

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
| B — Validation | `01` FR-DATA-15..24; `06` FR-GOV-2, 20 |
| C — Factors | `01` FR-DATA-33..36; `02` FR-MODEL-1..17 |
| D — Fitting | `02` FR-MODEL-18..37, 49..57, 62..67 |
| E — Approval | `02` FR-MODEL-56, 58..61, 64; `06` FR-GOV-9..21 |

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
