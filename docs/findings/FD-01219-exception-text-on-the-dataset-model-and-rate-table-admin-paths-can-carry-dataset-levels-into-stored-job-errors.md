---
id: FD-1219
family: finding
title: Exception text on the dataset, model and rate-table admin paths can carry dataset levels into stored Job errors
status: active
created: 2026-09-28
owner: auditor
tree: 633c6f34b7e841e09c7f108cd4696658c524fcfc
corrected_by: []
relates: [FD-1217, WK-1178]
---

# FD-1219 — Exception text on the dataset, model and rate-table admin paths can carry dataset levels into stored Job errors

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

### Does GbmFitError level text reach a sink today? Traced by reading, then measured

**The path, read at `origin/main`:** `fit_gbm` (`gbm.py:603`) encodes the **holdout** with the training encoding maps
(`gbm.py:675`, `_encode(holdout_matrix, factors, maps=encodings, bandings=bandings)`). A holdout that carries a
category level the training frame lacked reaches the raise at `gbm.py:322`–`:326`, whose message is
`factor 'x' carries level(s) [<the levels>] that the fitted model never saw …`, and which also keeps the levels in
`GbmFitError.terms` (`gbm.py:154`). The model-fit handler catches it at `backend/src/app/worker/model_handlers.py:394`
and raises `PlatformError(exc.code, "The … model could not be fitted", 409, str(exc))` from it (`:397`–`:399`), so the
detail is the message with the levels. The worker's `PlatformError` clause (`backend/src/app/worker/tasks.py:182`) stores
that detail as `JobError.message` and logs the exception with its traceback to the process log. Two sinks follow from
the code: **the stored `JobError.message`, and the process log.** The persisted `job_logs` do not carry it, because
`JobLogCapture.emit` keeps only `record.getMessage()` (`worker/logs.py:45`–`:47`).

**Measured 2026-09-29 00:12 BST at `origin/main` `633c6f34`,** with a throw-away test through `execute_job` at `nice -n 10`, on a
per-tree database recreated from the template and migrated to head (S-14). It ingests a 400-row book whose `area` column
holds one row with the sentinel level `zz99sentinel9zz`, splits it through the real derive Jobs, and fits an XGBoost GBM
through the real `MODEL_FIT` job. The first sentinel position that landed alone in the holdout was row 12; the fit
failed:

| Sink | Sentinel level present |
|---|---|
| stored `JobError.message` (code `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`) | **yes** |
| any field of the stored `JobError` | yes |
| persisted `job_logs` | no |
| process log (the captured log records with tracebacks) | **yes** |

**Disclosure: the database was made from the dirty template.** The per-tree database was created `TEMPLATE gipricing`,
the template `FD-1218` describes (28 non-empty tables left by an abandoned session of 2026-09-17, at revision
`d3b955a63d6a`), then migrated with `alembic upgrade head`. The run does not depend on those inherited rows: the test
used its own fresh workspace (the suite's `workspace_id` fixture), created its own dataset, rules, ingest, derive Jobs
and model, and the sentinel `zz99sentinel9zz` was invented for this run and appears only in the book the test built.
The message in the stored error was produced by that fit's own holdout, so the template's rows could not have supplied
the sentinel. This is a reading of the test's construction; the template's blobs were not searched for the string.

The stored message read: `factor 'area' carries level(s) ['zz99sentinel9zz'] that the fitted model never saw, so they have no
code in its persisted encoding map (FR-131).` So the answer to "is `GbmFitError` level text persisted today" is **yes, in
`JobError.message` and in the process log, and not in the persisted job logs**, which confirms the trace above. The level
belongs to the fitter's own dataset, so the person who ran the job already knows it, but the stored error is readable by
anyone with `job:read` in the workspace. The throw-away test is kept outside the repository, as
`trees/auditor-b-883.demo-fd9023.py`. The other `str(exc)` sites listed above were not each read for their exception
classes, and were not run.

## Why it is still a question

A category level can be personal data (a postcode district, an occupation, a vehicle description), and a stored Job
error is readable by anyone with `job:read` in the workspace. No requirement in the suite names dataset content in
error text. This finding does not decide whether one should.

## Disposition

**Deferred with an owner — WK-1178**, confirmed by the deputy. The fix is the same sanitiser `FD-1217` adds in `pricing-core`,
with the level given **by position, not by value** (for example "level 3 of factor `x`"). It is not in #889's scope.
Event: that sanitiser applied to these paths.
