---
id: CR-754
family: closure
kind: work
title: WK-661 — Modelling: closed
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-22
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/closure-records.md
---

### WK-661 — Modelling: closed 2026-08-22

**Scope, derived from `02` with `scope-audit.py` before opening any source file:
136 requirements** — 122 `FR-MODEL` and 14 `NFR-MODEL`, across the
module's eight deliverables. WK-661 is the largest single workstream in the project and the first
Phase-1b workstream to close.

**The roadmap's own figures disagreed with the specification in three places, and that
disagreement is the finding.** WK-661's row at the "Original scope" table claims "All **124**
`MODEL` requirements"; plan review 3, written at this close, states "125 in scope, 111
evidenced (89 %), 14 without". The spec holds 136. Neither number was wrong when
written — OQ-571 through 28 have since appended FR-209 to FR-178, and
requirement ids only ever accumulate (`CLAUDE.md` §5), so a count written once goes stale by
construction rather than by error. The rows are left as written and this record carries the
correction. **This is the third time the same mechanism has bitten this workstream**, which is
why plan review 3's question 5 proposed that derived counts stop living in prose — accepted
2026-08-22, and it does not bind retroactively.

##### `CLAUDE.md` §13, rule by rule

1. **Scope derived from the specification first** — `scope-audit.py MODEL` run before any
   source file was opened; the three-way disagreement with the roadmap is recorded above as a
   finding rather than reconciled away. Every unevidenced requirement has one of the four
   verdicts, or a recorded measurement with the reason a test is the wrong instrument.
2. **Deliverables audited against the definition** — the roadmap row's eight, each checked to
   **exist** *and* **work**, in the table above.
3. **Gates green locally, both halves, each exit code read** — below.
4. **Enforcement proven on broken input** — four proofs, listed above, including one that
   showed the plan's own proposed implementation would have passed the wrong test.
5. **NFRs measured, not asserted** — fourteen, with the measurement and the budget beside it;
   two breached and said so.
6. **What was *not* delivered** — the three numbers, the sixteen verdicts, the items owned
   elsewhere, and the retrofit list.
7. **Documents updated in the same PR** — `02`, the roadmap, `open-questions.md` and
   `CLAUDE.md` §2's layout marks. The demo guide is derived (FR-409), so there is nothing
   to write; that it still derives is checked by `backend/tests/test_demo_guide.py` in the run
   below.
8. **Repository clean** — no tracked build artifacts, verified by content below.

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Factors | Four of FR-83's eight types resolve — `identity`, `banding`, `grouping`, `interaction`. The other four are **refused by name**, not missing: `spline`/`polynomial` gated on continuous-factor rateability (FR-210), `expression` on the Phase-2 grammar (FR-95), `offset` superseded by `OffsetSpec` (FR-209). `FactorIntent.OFFSET` and `.DIAGNOSTIC` are permanently refused on the layer argument (FR-84/86) |
| Bandings | **6 of 6 methods** — manual, equal-width, quantile, exposure-quantile, credibility, tree. `propose_banding` returns a complete *editable* `Banding` with per-band exposure, frequency, severity and burning cost with intervals (FR-99); `manual` is refused at the proposal call site because the boundaries are the actuary's |
| Groupings | **4 of 5 methods** — manual, credibility-weighted (both limited-fluctuation *and* Bühlmann–Straub, FR-106), hierarchical clustering, tree. `reference_hierarchy` is **refused by name**: it rolls levels up through a Reference Table, which ADR-703 forbids `pricing-core` from reading. `unseen_level_behaviour` is mandatory and type-enforced — there is no default, because a silent default is a mispricing |
| glum GLM | Poisson, Gamma and Tweedie with the power estimated by profile likelihood and its 95 % interval recorded (FR-114); regularisation and CV selection (FR-112/182); offsets including offset-from-another-model, GLM-to-GLM (FR-116). Every coefficient carries estimate, standard error, z, p and interval, with the base level marked (FR-113). Non-convergence, rank deficiency and separation are named errors, not silent results (FR-115) |
| XGBoost | One `GbmSpec`, two backends, two translation paths. Offsets are handled per backend — XGBoost `base_margin`, LightGBM `init_score` — and `test_a_prediction_scales_exactly_with_exposure` pins that they agree (FR-129). LightGBM is the declared secondary and is tested at parity; EBM via interpret-core exports terms and bins directly rather than a serialised estimator (FR-140, ADR-705) |
| Diagnostics | Always on **both** train and holdout with the weighting recorded (FR-183/184). GLM: type-III p-values, deviance, residuals. GBM: eval curve, permutation importance, partial dependence with exposure share, monotonicity. A/E, lift, calibration and Gini are computed identically for both model types so a comparison holds (FR-186), plus backtests (FR-187). Deviance is computed once at fit time and diagnostics are insert-only, immutable at three layers |
| Transparency artifacts | The GLM approximation of a GBM is a **Model in its own right** (FR-137), carrying R², deviance explained and worst regions named by factor level with exposure share. TreeSHAP comes from the backends' native implementations rather than the `shap` package (FR-134, amended 2026-08-17). A rebuild now reuses those stored numbers instead of refitting (FR-138, this slice) |
| Custom objectives — templates only | The template catalogue — **12 templates, each with a hand-written analytic gradient *and* hessian, so 24 analytic derivatives, every one checked against a Richardson-extrapolated numeric derivative of that template's own loss** (FR-149), plus the certification machinery (FR-150/151) built in Phase 1 as the 2026-08-15 decision required, and custom **metrics** on the same lifecycle and grammar (FR-154/155/157–108). `kind: expression` is refused at the Pydantic type boundary for both objectives and metrics — the absence of a `parse_expression` stub *is* the statement |

**Gate (local, 2026-08-22, both halves, each command's own exit code read):** ruff 0 · mypy 131 source files · lint-imports **3 kept, 0 broken** (ADR-703/704/DEP-3) · `pytest -q` **1 720 passed, 1 xfailed** in 404 s · audit-docs all checks (506 requirements, 81 open questions all mirrored, 54 JSON schemas, 140 error codes with ownership exclusive) · req-coverage **506 specified / 257 marked** · `generate-contracts.py --check` **23 generated contracts match the models** · frontend install, `generate:api`, lint, type-check, **131 tests**, build — all 0. `alembic heads` is `9e4c7b21fa08`. The demo guide still derives (FR-409): `test_demo_guide.py` runs inside the suite above.

> **One honest qualification on the frontend half:** `pnpm install --frozen-lockfile` ran
> against an already-populated `node_modules`, which `CLAUDE.md` §11 warns can hide a missing
> dependency. The lockfile was unchanged and CI runs it clean, so this is a caveat on the
> local evidence rather than a known defect.

**Coverage, re-derivable from the documents rather than recalled:**

| Command | Result |
|---|---|
| `scope-audit.py MODEL` | 136 in scope, 120 with evidence (88 %), 16 without |
| `scope-audit.py MODEL --endpoints` | **41 declared, 41 published (100 %)** |
| `scope-audit.py MODEL --catalogue` | Nothing to run — MODEL declares no catalogue |
| `alembic heads` | `9e4c7b21fa08`, matching the migration this workstream's last slice added |

**Enforcement proven, not assumed** (§13 rule 4). Every check this slice introduced was shown
to fail on deliberately broken input before it was trusted:

- **NFR-483's position tests, in both directions.** Removing `node=` entirely fails both.
  More usefully, threading the *refused child* rather than its nearest positioned ancestor
  passes the subscript case and fails the operator case — which is precisely the distinction
  the second test exists to catch, and it means the ancestor walk is load-bearing rather than
  decorative.
- **NFR-481's determinism test.** It passed on the first run, which proves nothing until
  it is shown capable of failing: refitting on one row fewer of 20 000 moves the intercept by
  5.8e-05, roughly six orders of magnitude above the 1e-10 gate.
- **FR-138's call-count test.** Fails on the pre-change handler with both
  `build_glm_approximation` and `compute_diagnostics` recorded. Separately, swapping the
  probe's read session for `unit_of_work()` fails the leaves-no-reserved-surrogate test,
  proving the rollback is what keeps a failed build from leaving a surrogate behind.
- **A test that could not fail was deleted rather than kept.** A third FR-138 test
  counting surrogate rows on the happy path passed in both the good and the deliberately
  broken state. Two tests that bite beat three with one that cannot.

**Specification defects found by implementing it** (§0 — resolved, not quietly reconciled):

| Defect | Resolution |
|---|---|
| FR-138 said the branch **loads** the surrogate's `Diagnostics`. It is not implementable as a load — the result is consumed only inside the `should_fit` arm, so on the reuse path a load would be a query whose result is discarded | Requirement amended with a dated note: the branch **skips** that compute. The `glm_approximation` half was exactly right and is implemented as written |
| The roadmap's FR-138 verdict, "Delivered but untested — a marker is owed, not a feature", was false on both counts | Struck rather than overwritten, with what was found and when. The marker it called owed would have been a false claim |
| `02` §4.4's `spec_hash` lineage note — written to reconcile the spec with the code comment — omitted `v3 → v4`, a transition **both** of its source records held | Restored to its chronological place with the omission named. The same failure one level up as the note exists to fix |
| `fit_glm` **and `fit_ebm`** accept a `seed` neither reads, and §5.2 publishes both parameters. Twenty call sites pass it, seven outside tests | **OQ-599 — decided 2026-08-22 at option (b) and removed**, as FR-179, pinned by a negative test asserting `seed=` now raises. `spec.seed` is the single seed for every fitter, which is what `spec_hash` pins — an argument-supplied seed would sit outside the digest and let two fits with one `spec_hash` differ, the precise thing NFR-481 forbids. *(Original entry, kept:)* **OQ-599**, open, with options and a recommendation; not deleted here, because nineteen call sites and a published signature are a maintainer's change |
| NFR-482 carried "Owner: unassigned", which is a stated absence of a verdict rather than one of §13's four | Maintainer verdict 2026-08-22: **out of Phase 1 scope**. Not superseded — ids are permanent and the capability is real; it is out of *this phase's* scope |

#### The headline, as three numbers rather than one

`scope-audit.py` counts a requirement as evidenced when *any* test carries its marker, so
"120 of 136" means **declared-or-refused**, not built. Stated properly, at this close:

- **110 built** — implemented and evidenced by a test of the behaviour.
- **10 declared-and-refused-by-name.** Five where a capability is owed and the refusal stands
  in for it: FR-189 (`separate_model`, `LOSS_TREATMENT_UNIMPLEMENTED`), FR-207
  (whose subject *is* the staged contract), FR-208 (`spline`/`polynomial`/`expression`
  refused at resolution), FR-117 (the peril-reconciliation offset path), FR-178.
  Five where the capability is **permanently withheld and the refusal *is* the requirement**:
  FR-209 (`offset` as a Factor type), FR-84 (`FactorIntent.OFFSET`),
  FR-85 and FR-86 (`FactorIntent.DIAGNOSTIC`), FR-150 (`expression`
  objectives, gated off with the flag **on** as well as off).
- **16 unevidenced, each with a verdict** — every one below.

**The bucket grew from three to ten while `built` moved from 108 to 110**, because nine of
the eleven requirements appended since the last census are refusals or unbuilt. And this
slice's own FR-117 marker raised `evidenced` from 119 to 120 **without moving `built`
at all** — it lands in the refusal bucket. That is precisely the overstatement the
three-number split exists to catch, and it happened inside the slice that reports it.

> **The weakest evidence in the module, named rather than averaged away.** FR-178 is
> carried by a `@pytest.mark.xfail(strict=True)` — the only one in MODEL. That is not a
> refusal, it is a **pinned defect**: a GBM whose cross is sparse still dies inside
> `compute_gbm_diagnostics` with `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`, and it dies *uncoded*,
> outside the block that maps a `GbmFitError` to a platform code. Counted in the refusal
> bucket because the test does mark the boundary, but it is the one entry there that a
> reader should not take comfort from. Owner: **WK-690**.

> **Three requirements whose evidence is thinner than their marker suggests** — found by
> reading the tests rather than trusting the marks (§13 rule 1: a marker is a claim, not a
> proof). **FR-94** and **FR-166** are each evidenced only by a test asserting the
> route is *published in the OpenAPI document*; no test in `backend/tests/` ever calls
> `GET /api/v1/models/backtests/{id}` or any `/custom-objectives` route. The routes exist and
> the service layer is tested, but the endpoint behaviour — the 200 and the 404 FR-94
> names — is unproven, which is the failure FR-94 was itself written to fix, one layer
> up. **FR-173**'s only marker is a meta-test that every eligible schema is in the
> comparison list. These stay counted as built, because the capability is there and reachable;
> they are recorded so the next reader does not have to rediscover it. **Owner: WK-664**, as the
> first consumer of these endpoints.

**Not delivered by WK-661.** Every unevidenced requirement, with the verdict §13 rule 1 requires
— one of delivered-but-untested, deferred with an owner, reassigned, or not started, or a
recorded measurement where a test is the wrong instrument:

| Requirement | Verdict | Owner |
|---|---|---|
| FR-95 — `expression` factors | Not started | **WK-690**, accepted by the maintainer 2026-08-22 |
| FR-144 — `expression` objectives | Not started. Its gate, FR-150, *is* evidenced — as a refusal | **WK-690** (OQ-573) |
| FR-91 — proxy detection | Not started | **Phase 3 / WK-691** (OQ-581) |
| FR-210 — continuous Factor rateability | Not started. Gates `spline`/`polynomial`, which is why FR-208 refuses them | **WK-690** |
| FR-177 — an interaction measured jointly through its operands | Not started | **WK-690**. Its sibling FR-178 is the pinned defect above |
| NFR-475, -10 | **Measured by extrapolation** — 173 s of 600 s, 16.0 GB of 32 GB | The slice with a 16-core worker |
| NFR-476 | **Measured once, growth unmeasured** — 963 s of 1 200 s on an *assumed* linearity | Same |
| NFR-477 | **Measured and breached by all three grouping methods**; the cause is the one-way summary, not Ward. The remedy is to compute from the stored Profile — 2.60 s against a 5 s budget | The factor-workbench slice |
| NFR-479 | **Measured and met** — 32.1 % at the worst measured arm against 50 % | None required |
| NFR-480, -11 | **Measured and met**, 50× and 380× headroom | None required. NFR-486's blob spill belongs to the slice that first stores a per-row residual series |
| NFR-482 | **Out of Phase 1 scope** — maintainer verdict 2026-08-22, on plan review 3's question 2(a). No export path, no import path, no CLI, no bundle schema; parent FR-5 carries zero markers | **None in Phase 1.** Not superseded — the id is permanent and the capability is real |
| NFR-478 | **Measured and held** — 0.22 s against 5.22 s | None required |
| NFR-487 — the type-III per-factor block | **Measured and breached** at 678 013 × 60: more than 1.61× per tested factor against a 1.0× bound, and the observation is *censored* | **Phase 1b**, with the warm-denominator run the corrected multiples rest on |
| NFR-488 — the GBM block | **Measured and met** — 0.0480 fits per scoring pass against 0.06 | None required; FR-175's cap now bounds the sweep it prices |

**Also not delivered, and owned elsewhere rather than by WK-661** — listed so the boundary is
auditable rather than implied, each owner quoted from the document that assigns it:
`GroupingEvidence.source_level_stats` in the Python (FR-107), `_sweep`'s two
`exposure_share` defects, the sweep running over source columns rather than resolved levels
(FR-175 context), §5.3's absent intent controls and `rateable()`'s absence from §5.2
(FR-84 context), the five constraint-level contract-drift classes (FR-451,
FR-9) and every `02` §5.3 view — **all WK-664's**; the EBM predict arm was listed here as
WK-664's too and is **W32-4's**. Built 2026-08-23 (W32-4, the EBM predict arm). `custom_objective_ref`
on `Model`/`GlmSpec` (FR-207) is **WK-690's**. The evidence-bundle checklist and FR-364's
unenforced half are **WK-677's**. Valid penalised inference (FR-197) belongs to the slice
that builds the first of them.

**FR-117(c) is WK-661's by the offsets slice's own list and is deliberately still refused.**
FR-117 fixes the order — "(a) The next slice extends the reference to a fitted GBM … as
its own slice in Phase 1b. (c) The peril-reconciliation scoring path is **then** wired to the
resolver." Building (c) now would invert a recorded sequencing decision, and (a) is itself
demand-gated. It stays refused by name, which this slice made true in the code as well as the
sentence — that is a verdict, not a silence.

**Retrofit list (`docs/roadmap.md` §5) — where WK-661 leaves each item:**

| Item | State after WK-661 |
|---|---|
| **Append-only audit log, written in the caller's transaction** | **Delivered and used.** `audit.record(session, …)` takes the *caller's* `AsyncSession` — verified at the signature, not assumed — and the modelling write path calls it inside its own unit of work (`platform/modelling.py:248`, `:438`). WK-661 added the per-arm payload, because "what was fitted" is a different sentence per model type |
| **Artifact immutability + versioning + `parent_id`** | **Delivered and extended by WK-661.** Models, diagnostics and transparency artifacts are immutable once written, enforced by database trigger; the audit-remediation slice added `models.diagnostics_id` to that trigger by migration `9e4c7b21fa08`. Model lineage carries `parent_model_id` with a typed `change_reason` (FR-203) |
| **`model-schema` as the single source of truth** | **Delivered and load-bearing.** All 49 `02` shapes live there; the contracts are generated and CI fails on drift (FR-451). WK-661 hand-wrote no shared shape. The *constraint-level* drift guard remains unbuilt and is **WK-664's** — the field-existence and nullability halves are done |
| **The Job model with progress and cancellation** | **Delivered by WK-658, used throughout WK-661.** Every long modelling operation is a Job taking `ProgressCallback` — `_fit`, `_compare`, `_transparency`, `_reconcile`, `_quantile_crossing`. WK-661's own defect here was the reverse of missing: a fit sat at one fraction for its whole duration until `progress` was restored to `fit_glm`'s signature |
| **Decimal money discipline** | **Delivered by WK-658, honoured by WK-661.** `DecimalStr` and `MoneyMinor` carry every monetary field crossing the boundary; WK-661 added the exact-decimal refusal of a float, which is a whole slice of this workstream |
| **`trace_id` propagation API → worker → core** | **Delivered by WK-658, inherited by WK-661.** The Job row carries `trace_id` from `current_trace_id()` at submission and the outbox payload carries it to the worker (`platform/jobs.py:123`, `:156`, `:327`), so a modelling handler needs no code of its own to stay traceable |
| **RBAC checks in the backend from the first endpoint** | **Delivered and used.** `Perm.MODEL_READ` / `MODEL_FIT` / `MODEL_SUBMIT` are FastAPI dependencies on the model routes (`api/models.py:104-106`). WK-661 added `reserve_model`'s refusals, which this slice moved *before* the expensive compute rather than after it |
| **Content-addressed blob store** | **Delivered by WK-658, used by WK-661.** Booster artifacts and split frames are content-addressed blobs read by digest. `02`'s "declarative JSON artifacts, never pickled objects" holds — the EBM path exports terms and bins rather than a serialised estimator (ADR-705) |

**"WK-661 closed" must not be read as "the modelling module is finished."** It is not. Two NFRs
are measured and **breached** — NFR-477 by all three grouping methods, and NFR-487
at 678 013 × 60 on a *censored* observation, so the true multiple is unknown and worse than
1.61×. Three more are met only by extrapolation from a machine smaller than the one the
budget assumes. A sparse interaction still crashes the GBM diagnostics pass, uncoded. Every
`02` §5.3 view is unbuilt. What WK-661 closed is the **modelling engine and its API**: the maths,
the artifacts, the jobs, the lifecycle and the contracts — with 41 of 41 endpoints published,
and every remaining gap named above with an owner.

---
