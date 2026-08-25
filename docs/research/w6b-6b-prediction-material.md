# W6b-6b — verified material for the prediction view

**This is not a brief.** It is the prediction-side material verified at `origin/main`
`8d0dcf4` while W6b-6 was still a two-view slice, parked here on the 2026-08-25 split so
W6b-6b does not pay to re-derive it. **Re-verify against `origin/main` before writing the
brief** — this is a dated snapshot, not a live read, and the frontend moves.

**Scope:** the prediction view, `/models/:slug/predict`, registered in `02` §5.3 on
2026-08-23 (`02-modelling.md:2598`). Frontend-only.

## Requirements that moved here on the split

Six, all with backend test evidence:

| Requirement | Markers | Note |
|---|---|---|
| FR-MODEL-63 | 13 | Expectation plus uncertainty |
| FR-MODEL-99 | 12 | Penalised GLM states its basis |
| FR-MODEL-77 | 10 | The first three unavailability reasons |
| FR-MODEL-124 | 6 | EBM → `model_type_has_no_interval`; evidenced over HTTP |
| FR-MODEL-93 | 3 | `covariance_not_stored` |
| FR-MODEL-98 | 1 | See below |

**FR-MODEL-98's single marker is not a gap.** It sits on
`backend/tests/test_prediction.py:268` and asserts the substantive half —
`prediction.uncertainty.kind is UncertaintyKind.CONFIDENCE_INTERVAL_MEAN`, with
non-degenerate bounds. Its other half — *"adds a process-variance prediction interval only
when a named consumer asks for one"* — has no failing case and cannot be tested until
something builds it. Book it as such; do not book it unevidenced.

## Endpoint

| Method | Path | Requirement |
|---|---|---|
| `POST` | `/api/v1/models/{model_id}/predict` | FR-MODEL-63 |

**200 synchronously, not 202** — the only compute route in `02` that is not a Job. The
contract's own reason: every other compute route reads a whole dataset version, while this
reads at most `prediction_service.MAX_PREDICT_ROWS` rows the caller sent. *"Nothing is
persisted, so there is nothing to `GET` afterwards."*

## Contract shapes at `8d0dcf4`

```
PredictRows    rows        array of free-form objects (additionalProperties: true), MAX 1000
                           "one record per risk to score, each carrying the model's factor
                           source columns and its offset column … dev/debug scale and a
                           portfolio re-rate is 03's batch scoring"
Prediction     model_id, model_family_slug, version, model_type, uncertainty, rows
               model_type ∈ glm | xgboost | lightgbm | ebm
PredictedRow   expected  (required)   lower, upper  ← OPTIONAL and nullable
Uncertainty    kind (required); basis, level, reason, interval_models all nullable
UncertaintyKind      confidence_interval_mean | quantile_pair_interval | unavailable
UncertaintyBasis     information_matrix | unpenalised_information_matrix
UnavailableReason    no_interval_models_fitted | interval_models_not_approved
                     interval_models_stale | covariance_not_stored
                     model_type_has_no_interval
IntervalModels       lower_model_id, upper_model_id, lower_alpha, upper_alpha (all required)
```

All five `UnavailableReason` members must render **by name** — three from FR-MODEL-77, the
fourth from FR-MODEL-93, the fifth from FR-MODEL-124. FR-MODEL-99 requires the **basis** be
stated wherever an interval or standard error is shown; `unpenalised_information_matrix`
means the interval is the one an unpenalised fit would earn, and is **wider than the shrunk
estimate warrants** — a caveat the view has to say, not just a label.

## Traps carried over

1. **Slug vs id addressing.** The view routes on `:slug` but `/models/{model_id}/predict`
   takes a **uuid**, so it must resolve slug → `model_id` via `getModel`. W6b-1b never had
   to; W6b-6 hits the same trap.
2. **`lower`/`upper` are per-row optional** *and* the top-level `uncertainty` explains why. A
   row with no interval is **normal, not an error** — read the reason from `uncertainty`,
   never infer it from the nulls.
3. **1000-row cap** on `PredictRows`. State it in the UI before the request, not after a 422.
4. **§5.3's "uploaded batch" is non-binding prose.** Under FR-OVR-21 the Prediction Contents
   cell is prose that binds nothing, and it is **not** among the seven carve-outs;
   `PredictRows` carries only inline `rows`. So a file-upload affordance is not owed — and if
   the view is judged to need one, OQ-MODEL-15's floor rule makes that a **new requirement
   raised at build time**, brought to the manager, never a silent addition.

## Not in scope for W6b-6b

- Any backend change — all six requirements are evidenced.
- File/batch upload — see trap 4; portfolio re-rate is `03`'s batch scoring.
- A second interval kind — FR-MODEL-98 admits one, and adding one needs a named consumer.
