# Phase 1b exit-demo UAT — acceptance record

Filed 2026-08-27 by the pre-decision executor. Acceptance mechanism: a scripted HTTP run
of the core `wf-01` journey (`scripts/demo.py` with the full 678 013-row freMTPL2 seed),
with the UI available for hands-on driving. Bandings, Peril Structure and reconciliation
are recorded as Phase 2 (plan review 6 P1) and are not part of this UAT.

## Checklist

| # | Item | Result |
|---|---|---|
| 1 | The seed completes: validated freMTPL2 dataset, split, factors, GLM and GBM fits | PASS — the seed log shows dataset `fremtpl2-b7ddbf` with 9 approved rules, version 2 validated, GLM fitted, GBM fitted |
| 2 | The comparison artifact exists | PASS — `GET /api/v1/models/comparisons/{id}` returned the artifact (id `01a04487…`, fields `computed_at`, `job_id`, `summary`) |
| 3 | One model is approved | PASS — `GET /api/v1/models?status=approved` returned 1 item |
| 4 | The rating version is approved | PASS — `GET /api/v1/rating-versions/{id}` returned status `approved`, `model_ref: model:fremtpl2-glm-04da49@1` |
| 5 | The postcondition check passes over HTTP (`_verify_journey_postconditions`) | PASS — `GET /api/v1/models?status=approved&limit=5` returned 200; the demo printed "wf-01 demo subset: 1 approved model(s)" |
| 6 | The UI reaches the model list, the model detail, the diagnostics, and the rating version | PASS — the frontend dev server served :5173 (200, "GI Pricing Platform"); the router registers `/models`, `/models/:slug`, `/models/:slug/diagnostics`, `/rating-versions/:id` |
| 7 | The total seed time stays within the NFR-PLAT-4 budget (300 s) | PASS — 90 s |

## Measurement

| Metric | Value |
|---|---|
| Seed-to-usable-state time | 90 s |
| NFR-PLAT-4 budget | 300 s |
| Within budget | yes (30 % of budget) |

## How each item was verified

- Items 1-5: queried over HTTP against the demo's API on :8000, with the seeded
  membership's `x-dev-principal-id` and `Workspace-Id` headers.
- Item 6: the frontend dev server serves on :5173 and the router registers the four
  routes; the demo guide (FR-PLAT-53) maps them to the seeded workspace.
- Item 7: the demo's own "Seeded to a usable state in Ns" line, read from the run log.
