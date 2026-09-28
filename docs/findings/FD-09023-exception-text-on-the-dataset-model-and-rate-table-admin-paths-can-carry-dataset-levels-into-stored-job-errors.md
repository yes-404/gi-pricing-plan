---
id: FD-9023
family: finding
title: Exception text on the dataset, model and rate-table admin paths can carry dataset levels into stored Job errors
status: active
created: 2026-09-28
owner: auditor
tree: 633c6f34b7e841e09c7f108cd4696658c524fcfc
corrected_by: []
relates: [FD-9021, WK-1178]
---

# FD-9023 — Exception text on the dataset, model and rate-table admin paths can carry dataset levels into stored Job errors

**Severity: low.** The auditor filed this finding on 2026-09-28, on the lead's instruction. It comes from
auditor-a's re-audit of #889 at `60f95f02`, condition 7. It is low because the text is training or reference data,
which `NFR-499` does not govern, and because a dataset level is a category label and not a whole record. It is a
data-handling question because a level can be personal data.

## Finding

Several admin paths turn a library or engine exception's text into a `PlatformError` detail. The worker's
`PlatformError` clause stores the detail as the Job's error message, readable through the Jobs API. One such
message names the dataset's own levels. So dataset content, for example a list of category values, reaches a stored
Job error and its logs unsanitised.

## Evidence

At `origin/main` `633c6f34`:

- **A message that names levels.** `packages/pricing-core/src/pricing_core/modelling/gbm.py:322`–`:326` raises
  `GbmFitError("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED", f"factor {slug!r} carries level(s) {unknown} that the fitted model
  never saw …")`, where `unknown` is the sorted list of the dataset's unseen category values. The lead's example is a
  list such as `['coastal | diesel', …]`.
- **Where such text is stored.** `backend/src/app/worker/model_handlers.py:398` (`PlatformError(exc.code, "The
  {spec.model_type} model could not be fitted", 409, str(exc))`), `:405` (`f"{exc} FR-87: …"`), `:769`, `:1473` and
  `:1489` (compare, peril component and peril-structure paths, each with `str(exc)` as the detail);
  `backend/src/app/worker/data_handlers.py:410` (the split path); `backend/src/app/platform/rate_tables.py:92` and
  `:769`. The generic clause for a `PlatformError` (`worker/tasks.py:182`) stores `exc.detail or exc.title`, which
  is that text.
- **The scope.** `NFR-499` (`docs/specs/03-rating-engine.md:1062`) governs *quote inputs*: *"quote inputs are never
  logged in full outside sampled traces"*, and its 2026-08-30 clarification (`RL-917`) is about persistence as well as
  log output. Dataset levels are not quote inputs, so the requirement does not reach this text.

**Not established:** which of the listed `str(exc)` sites carry dataset values in practice. Only the `gbm.py:322`
message was read to contain them. The others were not each read for their exception classes.

## Why it is still a question

A category level can be personal data (a postcode district, an occupation, a vehicle description), and a stored Job
error is readable by anyone with `job:read` in the workspace. No requirement in the suite names dataset content in
error text. This finding does not decide whether one should.

## Disposition

**Deferred with an owner — WK-1178**, proposed. The deputy decides the owner and whether a rule is wanted. Event: a ruling on
whether error text on the admin paths may carry dataset content, and, if not, the same sanitiser `FD-9021` adds in
`pricing-core` is applied to these paths, or these paths name levels by count and not by value.
