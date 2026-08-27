# W7 Implementation Plan — the freMTPL2 modelling half (Phase 1b exit)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fit a GLM on the freMTPL2 demo dataset, approve it, create a rating version that references it, and drive `wf-01` end to end. This is the Phase 1b exit criterion.

**Architecture:** The W7a seed already produces a validated freMTPL2 dataset version. This plan extends the seed to create factors, fit a GLM through the real Job path (`model.fit`), submit and approve it, and create a rating version. The exit demo runs the journey and verifies its postconditions. The full 03 rating surface stays Phase 2.

**Tech Stack:** glum (via `fit_glm`), FastAPI + SQLAlchemy + Alembic, Polars, model-schema artefacts, the approval service, `scripts/demo.py`.

**Spec:** `07` FR-PLAT-37 (the demo seed) · [`wf-01`](../workflows/wf-01-dataset-to-model.md) (the exit journey) · `01` FR-DATA-55/56/57/52 · `02` NFR-MODEL-7. The carried-forward obligations come from the W6b close record (`W6B-CLOSE-RECORD-DRAFT-2026-08-27.md`).

**Highest ids:** No new requirement id is minted in this draft. The rating-version slice mints an id after the decision-maker rules on OD1.

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
- The seed drives real Jobs through `execute_job`, the path a worker takes in production. This is the W7a pattern (`examples/fremtpl2/seed.py:469`).

---

## Scope

The manager's scope (2026-08-27): a fitted GLM on freMTPL2, a rating version, `wf-01` end to end.

| Element | In W7 | Notes |
|---|---|---|
| Seed the demo GLM: factors, spec, fit, submit, approve | In | Slice W7-1 |
| The demo rating version | In, gated on OD1 | Slice W7-2 |
| The carried-forward obligations | In | Slice W7-3 |
| The exit demo and the guide | In | Slice W7-4 |
| GBM fit and model comparison in the demo | Open | OD3 |
| FR-DATA-24 streaming half | Out | Deferred. Needs a 10 M-row dataset to design against |
| `pipelines/` scheduled ingestion | Out | Deferred. A `pipeline` Source kind is registrable without a scheduler |
| Playwright E2E | Out | Deferred. The demo journey is HTTP-driven (OD5) |
| The full 03 rating surface: compile, score, rate tables | Out | Phase 2 |

---

## Findings (verified 2026-08-27 against origin/main `ebba7de`)

**F1. The seed produces a validated freMTPL2 version and no model.** `examples/fremtpl2/seed.py` creates the workspace, a 13-column dataset, two versions through the Job path, and an approved 9-rule set. Version 1 fails validation on the exposure anomaly. Version 2 validates and promotes to `validated`. The seed proves fittability on `@2` and refuses `@1` (`seed.py:572-576`). It creates no factor, no ModelSpec, no model, and no rating version.

**F2. The GLM fit path is built end to end, but nothing drives it on freMTPL2.** `POST /models` (`backend/src/app/api/models.py:489`) reserves the model, checks the fit gate, and submits `model.fit`. The worker handler (`backend/src/app/worker/model_handlers.py:170`) calls `fit_glm` (`packages/pricing-core/src/pricing_core/modelling/glm.py:523`), stores the covariance blob, and records `draft → fitted`. `POST /models/{id}/submit` (`models.py:707`) moves the model to `review` and creates the approval request. `POST /approval-requests/{id}/decide` (`approvals.py:226`) carries the decision to `approved`. The frontend `ModelSpecBuilderView.vue` validates a spec but does not call `POST /models`. No GLM runs on freMTPL2 today.

**F3. The rating version is absent.** No `RatingVersion` shape exists in `model-schema`. No `rating-versions` route exists in the backend. No `rating.compile` worker handler is registered. The approvals resolver fails closed for a `rating_version` reference (`approvals.py:405`). `03-rating-engine` is Phase 2. FR-PLAT-37 requires the demo to seed a rating version.

**F4. The four carried-forward obligations hold.** FR-DATA-55 is delivered as to the never-inferred half and untested at the seam. FR-DATA-56 has no broken-input enforcement proof. FR-DATA-57 is spec-only and not started. FR-DATA-52 is a decided deferral with no owner. NFR-MODEL-7 is out of Phase 1 scope by the 2026-08-22 maintainer verdict. Each is detailed in the table below.

**F5. The demo command starts the full stack.** `scripts/demo.py` now starts the `auth` profile (`demo.py:210`), so the compose stack includes keycloak. The seed runs `fetch.py` then `seed.py`. The demo waits on the API and the frontend, and prints `Open http://localhost:5173/demo`. NFR-PLAT-4 (seeded state in less than 5 minutes) was delivered in W6b with `demo.py --profile auth` as evidence.

---

## Carried-forward obligations (named, with owners)

The W6b close record carries four findings that this plan folds in as obligations. Each has a named owner. A verdict on OD2 can move the NFR-MODEL-7 owner.

| Id | The obligation | Owner |
|---|---|---|
| FR-DATA-56 | Prove the fit gate on deliberately broken input: a privileged caller fitting on a non-validated version is refused, with no override. | W7 (Slice W7-1, T4) |
| FR-DATA-55 | Test the reference-pin seam: the pinned path, the `None` path, and the pinned-but-unprofiled fallback. No Python test sets `reference_dataset_version_id` today. | W7 (Slice W7-3, T1) |
| FR-DATA-57 | Record the carry-forward to the Phase 2 validation-report successor. Do not build the projection in Phase 1b. | Phase 2 (validation-report successor) |
| FR-DATA-52 | Do the trigger-check: confirm the factor workbench does not ask for exposure-ordered levels. Keep the deferral unowned. Record the check. | W7 (Slice W7-3, T2) |
| NFR-MODEL-7 | Deliver the model round-trip test, or keep the 2026-08-22 out-of-scope verdict and name a Phase 2 owner. | W7, if OD2 rules in-scope |

---

## Open decisions for the decision-maker

**OD1 — The rating version boundary.** FR-PLAT-37 (Phase 1b) requires the demo to seed a rating version. `03` is Phase 2 with no schema, no route, and no compile handler. Options:

- **(a)** Build a Phase 1b-minimal rating version: a `RatingVersion` shape in `model-schema` (slug, version, status, pinned model ref), a seed-time creation and approval path, and one read route for the frontend. Gate it with a dated `03` spec amendment that scopes the Phase 1b subset. **Recommendation.** It satisfies FR-PLAT-37 without building the 03 module.
- **(b)** Record the demo's rating version as a declared placeholder, deferred to Phase 2. Rejected: FR-PLAT-37 requires a real one.
- **(c)** Build the full `03` compile, submit, approve, score surface. Rejected: that is a Phase 2 build in Phase 1b, which CLAUDE.md §0 forbids.

**OD2 — The NFR-MODEL-7 verdict.** The 2026-08-22 verdict marks it out of Phase 1 scope because no export or import path exists. W7 fits a real GLM on freMTPL2, which makes the round-trip testable. The W5 remediation named an achievable option: serialise Model and Diagnostics and blobs to JSON, reload in a clean process, score twice, compare bit-for-bit. Options:

- **(a)** Reverse the verdict with a dated maintainer note in `02` §9, and deliver the round-trip test in W7. **Recommendation.** The demo model is the natural subject, and the serialise-reload path already exists in the test suite (`test_scoring_without_the_fitting_stack.py`).
- **(b)** Keep the verdict and name a Phase 2 owner. The W7 plan records the obligation but does not build it.

**OD3 — The wf-01 demo breadth.** The manager's scope names a fitted GLM. The roadmap's demo-able outcome names a GLM, an XGBoost model, a comparison, and one approved. Options:

- **(a)** GLM-only journey: factors, GLM fit, diagnostics, approval, rating version. **Recommendation.** It satisfies the exit criterion with the manager's stated scope.
- **(b)** Full journey: GLM and GBM, comparison, peril structure. Larger. The roadmap names it, but the exit criterion does not require it.

**OD4 — The seed-time fit budget.** A full GLM fit on 678 013 rows takes about 184 seconds (`wf-01` §6). NFR-PLAT-4 sets the seeded state at less than 5 minutes. Options:

- **(a)** Fit at seed time on the full dataset with a reduced factor set. Measure the total against NFR-PLAT-4. **Recommendation.**
- **(b)** Fit on a sampled row count with `--rows`. The demo model then differs from the full dataset.
- **(c)** Fit lazily when a user drives the UI. More moving parts in the demo.

**OD5 — The exit-demo mechanism.** Phase 1a's exit demo was exercised over HTTP. Plan review 5 says the close must state how the exit demo runs and how it is accepted. Options:

- **(a)** A scripted, HTTP-driven run that verifies `wf-01`'s postconditions. The UI shows the seeded results. **Recommendation.**
- **(b)** A UI-driven journey. Requires the fit submission in `ModelSpecBuilderView.vue` and a rating version view.

---

## Slice inventory

| Slice | Deliverable | Gated on |
|---|---|---|
| W7-1 | The demo GLM fit and the FR-DATA-56 enforcement proof | none |
| W7-2 | The demo rating version | OD1 |
| W7-3 | The carried-forward obligations | OD2 (NFR-MODEL-7 half) |
| W7-4 | The exit demo and the guide | OD3, OD5 |

---

## Tasks

### Slice W7-1 — the demo GLM fit

**T1. The seed creates factors.**

**Files:**
- Modify: `examples/fremtpl2/seed.py` (after the `validated` promotion)
- Create: `examples/fremtpl2/model.py`

**Interfaces:**
- Consumes: the workspace, the validated version id, the `analyst` and `actuary` principals (`seed.py:310-311`)
- Produces: a set of `Factor` rows on the freMTPL2 dataset

- [ ] Create `examples/fremtpl2/model.py` with a `fit_demo_model` entry point that the seed calls.
- [ ] Create a small factor set: `driv_age`, `veh_age`, `veh_power` as continuous risk factors, and `veh_brand`, `veh_gas`, `area`, `region` as categorical risk factors. Use the platform factor service or the `POST /factors` path.
- [ ] Grant each factor the `risk` intent and a written rationale. Do not declare a prohibited factor.
- [ ] Verify with `GET /factors` that the factors exist in the workspace.

**T2. The seed builds a ModelSpec and fits a GLM.**

- [ ] Build a `GlmSpec` in `model.py`: family `poisson`, link `log`, response column `claim_count`, offset `log(exposure_years)`, the created factor ids, a fixed seed.
- [ ] Submit `JobKind.MODEL_FIT` with `job_service.submit` and run it with `execute_job`, the same path the seed uses for ingestion (`seed.py:460-469`).
- [ ] Verify the model reaches status `fitted`.
- [ ] Verify `GET /models/{slug}/diagnostics` returns the fit diagnostics.

**T3. The seed submits and approves the model.**

- [ ] Add an `approver` principal to the seed. The `approver` role holds `approval:decide` (`permissions.py:128`). The `pricing_actuary` role does not.
- [ ] Submit the model as the actuary with `POST /models/{id}/submit`.
- [ ] Decide the approval request as the approver with `POST /approval-requests/{id}/decide`.
- [ ] Verify the model reaches status `approved`.

**T4. FR-DATA-56 enforcement proof.**

**Files:**
- Create: a new backend test under `backend/tests/`

- [ ] Write a broken-input test: a caller holding `model:fit` calls `POST /models` against a non-validated version.
- [ ] Use a `draft` or `failed` version, for example the seed's version 1.
- [ ] Expect `DATASET_NOT_VALIDATED` in the response. The test fails the day an override appears.
- [ ] Mark the test `@pytest.mark.req("FR-DATA-56")`.
- [ ] Run the test and confirm it passes. Run it once against a broken mutation to prove it fails without the gate.

**Gate for the slice:** the model reaches `approved` in the seeded workspace, and the enforcement test is green.

---

### Slice W7-2 — the demo rating version

**Gated on OD1.** The tasks assume OD1 rules (a). If the decision-maker rules otherwise, rewrite this slice before building.

**T1. Spec change: scope the Phase 1b rating version.**

- [ ] Add a dated note to `03-rating-engine.md` that scopes the Phase 1b demo rating version: a draft-to-approved artifact that pins an approved Model, created and approved by the demo seed. The full `03` surface (compile, score, rate tables, deployment) stays Phase 2.
- [ ] If a requirement id is needed, mint it with a `Next free:` marker. Next free: `FR-PLAT-67` (or the family the decision-maker names).
- [ ] Run `python3 scripts/audit-docs.py`.

**T2. model-schema: the RatingVersion shape.**

- [ ] Add a minimal `RatingVersion` to `model-schema`: `slug`, `version`, `status` (`draft → review → approved`), `workspace_id`, `dataset_version_id`, a pinned `model` reference, `created_at`.
- [ ] Mirror the `DatasetVersion` envelope conventions. Do not hand-write a shape that already exists.
- [ ] Add model-schema tests for the shape and its status transitions.

**T3. Backend: the seed-time creation and approval path.**

- [ ] Add a service path that creates a draft `RatingVersion` pinned to the approved model.
- [ ] Add the approval wiring: a `rating_version` reference must resolve through the approvals resolver (`approvals.py:405` currently fails closed).
- [ ] Add one read route, for example `GET /rating-versions/{id}`, and register it in the router.
- [ ] Extend the seed to create the rating version and approve it after the model approval (Slice W7-1 T3).
- [ ] Add backend tests for the creation, the approval, and the failed-closed behaviour before the wiring exists.

**T4. Frontend: the rating version display.**

- [ ] Add a minimal rating version display, or list the rating version in the demo guide. The frontend `generate:api` must regenerate after the backend change.
- [ ] Verify the frontend gate half passes.

**Gate for the slice:** the seeded workspace contains an `approved` rating version that references the approved GLM.

---

### Slice W7-3 — the carried-forward obligations

**T1. FR-DATA-55: the reference-pin seam test.**

- [ ] Write a Python test that sets `reference_dataset_version_id` on a Rule Set.
- [ ] Exercise the pinned path, the `None` path, and the pinned-but-unprofiled fallback. The read sits at `backend/src/app/worker/data_handlers.py:249`.
- [ ] Mark the test `@pytest.mark.req("FR-DATA-55")`.
- [ ] Verify the distributional rules still pass when the reference is pinned.

**T2. FR-DATA-52: the trigger-check.**

- [ ] Confirm the factor workbench (W6b) does not ask for exposure-ordered levels. Grep the factor workbench and the monitoring views.
- [ ] Record the check as a dated note in the plan or the close record. Keep the deferral unowned.
- [ ] Verify the exposure-ordered top-20 is not scheduled anywhere.

**T3. FR-DATA-57: the Phase 2 handoff.**

- [ ] Record the carry-forward in the roadmap or the close record: `unrun_layers` is a Phase 2 validation-report projection.
- [ ] Name the successor owner: the Phase 2 validation-report workstream.
- [ ] Do not build the projection in W7.

**T4. NFR-MODEL-7: the round-trip test (if OD2 rules in-scope).**

- [ ] Serialise the demo GLM and its diagnostics and blobs to JSON.
- [ ] Reload the JSON in a clean process where the fitting stack cannot import. Mirror `test_scoring_without_the_fitting_stack.py`.
- [ ] Score the reloaded model twice and compare to the last representable digit.
- [ ] Mark the test `@pytest.mark.req("NFR-MODEL-7")`.
- [ ] Add a dated maintainer reversal note to `02` §9 if the verdict is reversed.

**Gate for the slice:** the two tests are green, the trigger-check is recorded, and the Phase 2 handoff is named.

---

### Slice W7-4 — the exit demo

**Gated on OD3 and OD5.** The tasks assume OD3 rules (a) and OD5 rules (a).

**T1. The demo drives the journey end to end.**

- [ ] Extend `scripts/demo.py` or the seed flow so one command produces the full journey: validated dataset, factors, approved GLM, approved rating version.
- [ ] Verify each of `wf-01` §4's postconditions after the run.
- [ ] Measure the total time and compare it to NFR-PLAT-4. Report the number in the close record.

**T2. The guide shows the model and the rating version.**

- [ ] Update `frontend/src/views/DemoView.vue` or the guide so it links the fitted model, its diagnostics, and the rating version.
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
- The FR-DATA-56 test fails on a broken mutation. The FR-DATA-55 test covers all three reference paths.
- The exit demo runs end to end on freMTPL2 and the `wf-01` §4 postconditions hold.

---

## Sources

- `docs/roadmap.md` §6: the W7 row, the W7a and W7b closure records, the Phase 1b exit.
- `docs/specs/07-platform.md`: FR-PLAT-37, FR-PLAT-53/54, NFR-PLAT-4.
- `docs/specs/01-data-management.md`: FR-DATA-55, FR-DATA-56, FR-DATA-57, FR-DATA-52.
- `docs/specs/02-modelling.md`: NFR-MODEL-7 and its §9 verdict.
- `docs/specs/03-rating-engine.md` §5.1: the Phase 2 rating surface.
- `docs/workflows/wf-01-dataset-to-model.md`: the exit journey.
- `W6B-CLOSE-RECORD-DRAFT-2026-08-27.md` and `W6B-PLAN-REVIEW-5-DRAFT-2026-08-27.md` (handover directory): the carried-forward findings.
- `scripts/demo.py`, `examples/fremtpl2/seed.py`, `backend/src/app/api/models.py`, `backend/src/app/worker/model_handlers.py`, `packages/pricing-core/src/pricing_core/modelling/glm.py`: verified at `ebba7de`.
