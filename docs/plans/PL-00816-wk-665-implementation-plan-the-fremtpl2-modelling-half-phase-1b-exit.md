---
id: PL-816
family: plan
kind: leaf
title: WK-665 Implementation Plan — the freMTPL2 modelling half (Phase 1b exit)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-27
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-27-w7-fremtpl2-modelling.md
---

# WK-665 Implementation Plan — the freMTPL2 modelling half (Phase 1b exit)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fit a GLM and a GBM on the freMTPL2 demo dataset, compare them, approve one, create a rating version that references it, and drive `WF-698` end to end. This is the Phase 1b exit criterion.

**Architecture:** The WK-666 seed already produces a validated freMTPL2 dataset version. This plan extends the seed to create factors, fit a GLM and a GBM through the real Job path (`model.fit`), run the model comparison, submit and approve the selected model, and create a rating version. The exit demo runs the journey over HTTP and verifies its postconditions. The full 03 rating surface stays Phase 2.

**Tech Stack:** glum (via `fit_glm`), XGBoost or LightGBM (via `fit_gbm`), FastAPI + SQLAlchemy + Alembic, Polars, model-schema artefacts, the approval service, `scripts/demo.py`.

**Spec:** `07` FR-439 (the demo seed) · [`WF-698`](../workflows/WF-00698-dataset-to-approved-model.md) (the exit journey) · `01` FR-57/58/59/67 · `02` NFR-482. The carried-forward obligations come from the WK-664 close record (`W6B-CLOSE-RECORD-DRAFT-2026-08-27.md`).

**Highest ids:** This plan takes one new id. Next free: `FR-440`.

## Global Constraints

- The gate has two halves. Both must pass before a push (CLAUDE.md §11).
- Write prose in ASD-STE100. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date. The plan file commits on the branch, never copied back.
- Nobody hand-writes a shape that already exists in `model-schema`.
- Money is integer minor units or Decimal in the rating path, never float (CLAUDE.md §7).
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis deps.
- Do not build ahead of the phase. A later phase's capability is a spec change first (CLAUDE.md §0).
- Requirement ids are permanent. Append, never renumber (CLAUDE.md §5).
- Every spec change runs `python3 scripts/audit-docs.py` before commit (CLAUDE.md §0).
- The seed drives real Jobs through `execute_job`, the path a worker takes in production. This is the WK-666 pattern (`examples/fremtpl2/seed.py:469`).
- The demo fit uses the full 678 013-row dataset. If the seeded state exceeds the NFR-529 budget, sample with `--rows` and record the deviation.

---

## Scope

The manager's scope (2026-08-27): a fitted GLM on freMTPL2, a rating version, `WF-698` end to end. The five rulings (2026-08-27) set the breadth: the full journey, GLM and GBM, comparison, and one approved.

| Element | In WK-665 | Notes |
|---|---|---|
| The demo models: factors, GLM and GBM fits | In | Slice W7-1 |
| The demo comparison and approval | In | Slice W7-2 |
| The demo rating version | In | Slice W7-3 |
| The carried-forward obligations | In | Slice W7-4 |
| The exit demo and the guide | In | Slice W7-5 |
| FR-54 streaming half | Out | Deferred. Needs a 10 M-row dataset to design against |
| `pipelines/` scheduled ingestion | Out | Deferred. A `pipeline` Source kind is registrable without a scheduler |
| Playwright E2E | Out | Deferred. The demo journey is HTTP-driven (OD5) |
| The full 03 rating surface: compile, score, rate tables | Out | Phase 2 |

---

## Findings (verified 2026-08-27 against origin/main `ebba7de`)

**F1. The seed produces a validated freMTPL2 version and no model.** `examples/fremtpl2/seed.py` creates the workspace, a 13-column dataset, two versions through the Job path, and an approved 9-rule set. Version 1 fails validation on the exposure anomaly. Version 2 validates and promotes to `validated`. The seed proves fittability on `@2` and refuses `@1` (`seed.py:572-576`). It creates no factor, no ModelSpec, no model, and no rating version.

**F2. The fit path is built end to end, but nothing drives it on freMTPL2.** `POST /models` (`backend/src/app/api/models.py:489`) reserves the model, checks the fit gate, and submits `model.fit`. The worker handler (`backend/src/app/worker/model_handlers.py:170`) calls `fit_glm` (`packages/pricing-core/src/pricing_core/modelling/glm.py:523`), `fit_gbm` (`gbm.py:602`) and `fit_ebm` (`ebm.py:95`), stores the covariance blob, and records `draft → fitted`. `POST /models/{id}/submit` (`models.py:707`) moves the model to `review` and creates the approval request. `POST /approval-requests/{id}/decide` (`approvals.py:226`) carries the decision to `approved`. `POST /models/compare` (`models.py:802`) submits the comparison Job. The frontend `ModelSpecBuilderView.vue` validates a spec but does not call `POST /models`. No model runs on freMTPL2 today.

**F3. The rating version is absent.** No `RatingVersion` shape exists in `model-schema`. No `rating-versions` route exists in the backend. No `rating.compile` worker handler is registered. The approvals resolver fails closed for a `rating_version` reference (`approvals.py:405`). `03-rating-engine` is Phase 2. FR-439 requires the demo to seed a rating version.

**F4. The carried-forward obligations hold.** FR-57 is delivered as to the never-inferred half and untested at the seam. FR-58 has no broken-input enforcement proof. FR-59 is spec-only and not started. FR-67 is a decided deferral with no owner. NFR-482 is out of Phase 1 scope by the 2026-08-22 maintainer verdict. Each is detailed in the table below.

**F5. The demo command starts the full stack.** `scripts/demo.py` now starts the `auth` profile (`demo.py:210`), so the compose stack includes keycloak. The seed runs `fetch.py` then `seed.py`. The demo waits on the API and the frontend, and prints `Open http://localhost:5173/demo`. NFR-529 (seeded state in less than 5 minutes) was delivered in WK-664 with `demo.py --profile auth` as evidence.

---

## Carried-forward obligations (named, with owners)

The WK-664 close record carries five findings that this plan folds in as obligations. Each has a named owner. The decision-maker's rulings set the owners on 2026-08-27.

| Id | The obligation | Owner |
|---|---|---|
| FR-58 | Prove the fit gate on deliberately broken input: a privileged caller fitting on a non-validated version is refused, with no override. | WK-665 (Slice W7-1, T4) |
| FR-57 | Test the reference-pin seam: the pinned path, the `None` path, and the pinned-but-unprofiled fallback. No Python test sets `reference_dataset_version_id` today. | WK-665 (Slice W7-4, T1) |
| FR-59 | Record the carry-forward to the Phase 2 validation-report successor. Do not build the projection in Phase 1b. | Phase 2 (validation-report successor) |
| FR-67 | Do the trigger-check: confirm the factor workbench does not ask for exposure-ordered levels. Keep the deferral unowned. Record the check. | WK-665 (Slice W7-4, T2) |
| NFR-482 | Deliver the model round-trip test and reverse the 2026-08-22 out-of-scope verdict with a dated note. | WK-665 (Slice W7-4, T4) |

---

## Decisions (ruled 2026-08-27)

**OD1 — The rating version boundary. Ruled (a).** Build a Phase 1b-minimal rating version: a `RatingVersion` shape in `model-schema`, a seed-time creation and approval path, and one read route. The plan takes the new 07 requirement for this (Highest ids). Add a dated `03` amendment that scopes the Phase 1b subset. The full `03` surface stays Phase 2.

**OD2 — The NFR-482 verdict. Ruled (a).** Reverse the 2026-08-22 verdict with a dated maintainer note in `02` §9. Deliver the round-trip test in WK-665. The demo models are the natural subjects.

**OD3 — The WF-698 demo breadth. Ruled (b).** The full journey: fit a GLM and a GBM, compare them, select one, approve it. The demo mirrors the roadmap's demo-able outcome.

**OD4 — The seed-time fit budget. Ruled (a).** Fit at seed time on the full dataset with a reduced factor set. Measure the total against NFR-529. If the total exceeds the budget, sample with `--rows` and record the deviation.

**OD5 — The exit-demo mechanism. Ruled (a).** A scripted, HTTP-driven run that verifies `WF-698`'s postconditions. The UI shows the seeded results.

---

## Slice inventory

| Slice | Deliverable | Gated on |
|---|---|---|
| W7-1 | The demo models and the FR-58 enforcement proof | none |
| W7-2 | The demo comparison and approval | OD3 |
| W7-3 | The demo rating version | OD1 |
| W7-4 | The carried-forward obligations | OD2 |
| W7-5 | The exit demo and the guide | OD4, OD5 |

---

## Tasks

### Slice W7-1 — the demo models

**T1. The seed creates factors.**

**Files:**
- Modify: `examples/fremtpl2/seed.py` (after the `validated` promotion)
- Create: `examples/fremtpl2/model.py`

**Interfaces:**
- Consumes: the workspace, the validated version id, the `analyst` and `actuary` principals (`seed.py:310-311`)
- Produces: a set of `Factor` rows on the freMTPL2 dataset

- [ ] Create `examples/fremtpl2/model.py` with a `fit_demo_models` entry point that the seed calls.
- [ ] Create a small factor set: `driv_age`, `veh_age`, `veh_power` as continuous risk factors, and `veh_brand`, `veh_gas`, `area`, `region` as categorical risk factors. Use the platform factor service or the `POST /factors` path.
- [ ] Grant each factor the `risk` intent and a written rationale. Do not declare a prohibited factor.
- [ ] Verify with `GET /factors` that the factors exist in the workspace.

**T2. The seed builds a GLM spec and fits the GLM.**

- [ ] Build a `GlmSpec` in `model.py`: family `poisson`, link `log`, response column `claim_count`, offset `log(exposure_years)`, the created factor ids, a fixed seed.
- [ ] Submit `JobKind.MODEL_FIT` with `job_service.submit` and run it with `execute_job`, the same path the seed uses for ingestion (`seed.py:460-469`).
- [ ] Verify the model reaches status `fitted`.
- [ ] Verify `GET /models/{slug}/diagnostics` returns the fit diagnostics.

**T3. The seed builds a GBM spec and fits the GBM.**

- [ ] Build a `GbmSpec` in `model.py`: objective `count:poisson`, the same factors, the exposure offset, monotone constraints derived from the factor declarations, early stopping on the holdout.
- [ ] Build the spec without an offset first. Verify the spec validation refuses it and names the acknowledgement, the FR-121 refusal.
- [ ] Rebuild the spec with the exposure offset declared. Submit and execute the fit Job.
- [ ] Verify the model reaches status `fitted` and its diagnostics exist.

**T4. FR-58 enforcement proof.**

**Files:**
- Create: a new backend test under `backend/tests/`

- [ ] Write a broken-input test: a caller holding `model:fit` calls `POST /models` against a non-validated version.
- [ ] Use a `draft` or `failed` version, for example the seed's version 1.
- [ ] Expect `DATASET_NOT_VALIDATED` in the response. The test fails the day an override appears.
- [ ] Mark the test `@pytest.mark.req("FR-58")`.
- [ ] Run the test and confirm it passes. Run it once against a broken mutation to prove it fails without the gate.

**Gate for the slice:** both models reach `fitted` in the seeded workspace, and the enforcement test is green.

---

### Slice W7-2 — the demo comparison and approval

**T1. The seed runs the comparison.**

- [ ] Submit `JobKind.MODEL_COMPARE` over the GLM and the GBM and execute it. The comparison reads the shared holdout.
- [ ] Verify `GET /models/comparisons/{comparison_id}` returns the comparison artifact.
- [ ] Record the selection reason in the plan or the close record. The comparison output decides the approved model.

**T2. The seed submits and approves the selected model.**

- [ ] Add an `approver` principal to the seed. The `approver` role holds `approval:decide` (`permissions.py:128`). The `pricing_actuary` role does not.
- [ ] Submit the selected model as the actuary with `POST /models/{id}/submit`.
- [ ] Decide the approval request as the approver with `POST /approval-requests/{id}/decide`.
- [ ] Verify the model reaches status `approved`.

**Gate for the slice:** one model is `approved` and the comparison artifact exists.

---

### Slice W7-3 — the demo rating version

**T1. Spec change: file the new 07 requirement and amend 03.**

- [ ] Next free: `FR-440`. Add the requirement row to `07` §3: the demo seed creates and approves a minimal Rating Version that pins an approved Model. The full `03` surface stays Phase 2.
- [ ] Add a dated note to `03-rating-engine.md`: the Phase 1b rating version is a draft-to-approved artifact with a slug, a version, a status, and a pinned Model reference. Compile, score, rate tables, and deployment stay Phase 2.
- [ ] Run `python3 scripts/audit-docs.py`.

**T2. model-schema: the RatingVersion shape.**

- [ ] Add a minimal `RatingVersion` to `model-schema`: `slug`, `version`, `status` (`draft → review → approved`), `workspace_id`, `dataset_version_id`, a pinned `model` reference, `created_at`.
- [ ] Mirror the `DatasetVersion` envelope conventions. Do not hand-write a shape that already exists.
- [ ] Add model-schema tests for the shape and its status transitions.

**T3. Backend: the seed-time creation and approval path.**

- [ ] Add a service path that creates a draft `RatingVersion` pinned to the approved model.
- [ ] Add the approval wiring: a `rating_version` reference must resolve through the approvals resolver (`approvals.py:405` currently fails closed).
- [ ] Add one read route, for example `GET /rating-versions/{id}`, and register it in the router.
- [ ] Extend the seed to create the rating version and approve it after the model approval (Slice W7-2 T2).
- [ ] Add backend tests for the creation, the approval, and the failed-closed behaviour before the wiring exists.

**T4. Frontend: the rating version display.**

- [ ] Add a minimal rating version display, or list the rating version in the demo guide. The frontend `generate:api` must regenerate after the backend change.
- [ ] Verify the frontend gate half passes.

**Gate for the slice:** the seeded workspace contains an `approved` rating version that references the approved model.

---

### Slice W7-4 — the carried-forward obligations

**T1. FR-57: the reference-pin seam test.**

- [ ] Write a Python test that sets `reference_dataset_version_id` on a Rule Set.
- [ ] Exercise the pinned path, the `None` path, and the pinned-but-unprofiled fallback. The read sits at `backend/src/app/worker/data_handlers.py:249`.
- [ ] Mark the test `@pytest.mark.req("FR-57")`.
- [ ] Verify the distributional rules still pass when the reference is pinned.

**T2. FR-67: the trigger-check.**

- [ ] Confirm the factor workbench (WK-664) does not ask for exposure-ordered levels. Grep the factor workbench and the monitoring views.
- [ ] Record the check as a dated note in the plan or the close record. Keep the deferral unowned.
- [ ] Verify the exposure-ordered top-20 is not scheduled anywhere.

**T3. FR-59: the Phase 2 handoff.**

- [ ] Record the carry-forward in the roadmap or the close record: `unrun_layers` is a Phase 2 validation-report projection.
- [ ] Name the successor owner: the Phase 2 validation-report workstream.
- [ ] Do not build the projection in WK-665.

**T4. NFR-482: the round-trip test and the verdict reversal.**

- [ ] Serialise the demo model and its diagnostics and blobs to JSON.
- [ ] Reload the JSON in a clean process where the fitting stack cannot import. Mirror `test_scoring_without_the_fitting_stack.py`.
- [ ] Score the reloaded model twice and compare to the last representable digit.
- [ ] Mark the test `@pytest.mark.req("NFR-482")`.
- [ ] Add a dated maintainer note to `02` §9: the verdict is reversed, and the round-trip test in WK-665 delivers the requirement.

**Gate for the slice:** the two tests are green, the trigger-check is recorded, and the Phase 2 handoff is named.

---

### Slice W7-5 — the exit demo

**T1. The demo drives the journey end to end.**

- [ ] Extend `scripts/demo.py` or the seed flow so one command produces the full journey: validated dataset, factors, GLM and GBM, comparison, one approved model, an approved rating version.
- [ ] Verify each of `WF-698` §4's postconditions after the run.
- [ ] Measure the total time and compare it to NFR-529. If the total exceeds 5 minutes, sample with `--rows` and record the deviation.

**T2. The guide shows the models and the rating version.**

- [ ] Update `frontend/src/views/DemoView.vue` or the guide so it links the fitted models, their diagnostics, and the rating version.
- [ ] Verify the demo links resolve to the built routes.

**T3. The exit-demo acceptance.**

- [ ] Run the journey over HTTP and capture the output. This is the Phase 1b exit demo evidence.
- [ ] State in the roadmap how the maintainer accepts the demo: scripted HTTP run, with the UI available for hands-on driving.

**Gate for the slice:** the exit demo completes end to end on freMTPL2 and the postconditions hold.

---

## Verification

- Both gate halves pass locally before a push:
  - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
  - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
  - `uv run python scripts/generate-contracts.py --check`
  - `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`
- The FR-58 test fails on a broken mutation. The FR-57 test covers all three reference paths. The NFR-482 test compares two scores.
- The exit demo runs end to end on freMTPL2 and the `WF-698` §4 postconditions hold.
- The seeded state stays within the NFR-529 budget, or the plan records the sample and the reason.

---

## Sources

- `docs/roadmap.md` §6: the WK-665 row, the WK-666 and WK-667 closure records, the Phase 1b exit.
- `docs/specs/07-platform.md`: FR-439, FR-408/409, NFR-529.
- `docs/specs/01-data-management.md`: FR-57, FR-58, FR-59, FR-67.
- `docs/specs/02-modelling.md`: NFR-482 and its §9 verdict.
- `docs/specs/03-rating-engine.md` §5.1: the Phase 2 rating surface.
- `docs/workflows/WF-00698-dataset-to-approved-model.md`: the exit journey.
- `W6B-CLOSE-RECORD-DRAFT-2026-08-27.md` and `W6B-PLAN-REVIEW-5-DRAFT-2026-08-27.md` (handover directory): the carried-forward findings.
- `scripts/demo.py`, `examples/fremtpl2/seed.py`, `backend/src/app/api/models.py`, `backend/src/app/worker/model_handlers.py`, `packages/pricing-core/src/pricing_core/modelling/glm.py`, `gbm.py`: verified at `ebba7de`.
