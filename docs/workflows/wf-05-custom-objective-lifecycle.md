# WF-05 — Custom objective lifecycle

**Modules:** `02-modelling` · `06-governance` · `07-platform`
**Primary actors:** Pricing Actuary (author), Approver, Admin
**Trigger:** A standard loss function does not fit the pricing problem — large losses distort a Gamma severity fit, or under-pricing costs more than over-pricing.
**Outcome:** An `approved`, certified, versioned Custom Objective usable across models, with a complete audit trail — or a documented decision that the objective is unsound.

> This is the most governance-heavy journey in the platform, because an arbitrary-code
> objective is a governance risk and a mis-specified objective is a mispricing risk. The
> whole point of this workflow is that neither can happen quietly.

> **What of this is built — 2026-08-18 (W5, custom objectives).** **Route A is real**, and
> Route B is not. The twelve-template catalogue, the nine §4.7 checks, the certificate, the
> FR-MODEL-46 lifecycle and the fit path (Phase C) are built and tested; the `expression`
> kind is Phase 2 behind `expression_objectives_enabled`, and `POST /custom-objectives/{id}/derive` refuses with
> `OBJECTIVE_KIND_NOT_ENABLED` rather than 404 — the route exists so that the refusal has
> somewhere to happen. Four steps in Route A and Phase C read differently now:
>
> * **The precondition permission is superseded.** `custom_objective:author` does not exist;
>   the built surface checks `model:read` / `model:fit` / `model:submit`. `06` §4.1 carries
>   the resolution and OQ-GOV-8 carries the Phase 2 question.
> * **A3 is not built** (`02` §5.3, owner W6b) — and the *"implied restoration loading"* it
>   shows is computed nowhere. `capped_gamma` is the Gamma loss on `min(y, cap)` and carries
>   no loading: restoring the uncapped mean is a rating-side decision, not part of the loss
>   (`02` §4.5's 2026-08-18 amendment).
> * **A7 overstates the common case.** All nine checks are emitted for every template, and a
>   template can legitimately warn — `certified_with_findings` is the ordinary outcome for a
>   pricing loss, not the exceptional one. Only `failed` blocks.
> * **C3's compiled tree is Phase 2's.** In Phase 1 `compile_objective` selects an analytic
>   gradient and hessian from the catalogue; there is no user text to compile, which is why
>   the sandbox question could be deferred rather than answered.

---

## 1. Preconditions

| Condition | Refs |
|---|---|
| The actor holds `custom_objective:author` | `06` §4.1 |
| For `expression` objectives, the `expression_objectives_enabled` feature flag is on — it is off for the whole of Phase 1, so **Route B is a Phase 2 journey** and Route A is the whole of Phase 1's | `07` FR-PLAT-45/46, `02` FR-MODEL-75 |
| A `validated` Dataset Version exists for the smoke fit and dry-run | `01` §1.3 |

---

## 2. Route A — Template objective (the common case)

| # | Actor | Action | Refs |
|---|---|---|---|
| A1 | Pricing Actuary | Opens the objective library, chooses `capped_gamma` from the shipped template catalogue. | `02` §4.5 |
| A2 | Pricing Actuary | Sets `cap = £25 000`, declares applicability: response `claim_severity`, backends `xgboost` and `lightgbm`. | `02` FR-MODEL-39/44 |
| A3 | Frontend | Shows the loss curve at the chosen parameters, and the implied restoration loading needed to recover the uncapped mean. | `02` §5.3 |
| A4 | Backend | Validates parameters against the template's declared ranges (`cap > 0`). No user code exists anywhere in this route. | `02` FR-MODEL-39 |
| A5 | Pricing Actuary | `POST /custom-objectives/{id}/certify` → `202` + Job. | `02` FR-MODEL-42 |
| A6 | Worker → pricing-core | Runs the certificate checks even though the derivatives are the platform's own analytic implementations — because the *parameterisation* still has to be sound at these values. | `02` §4.7 |
| A7 | Worker | All checks pass; `overall: certified`. | `02` §4.7 |
| A8 | Pricing Actuary | Submits; one Approver approves. | `06` §4.2 |

Route A completes in under an hour and involves no novel mathematics. **Most real needs
should land here** — which is why the template catalogue is 12 entries, not 3.

---

## 3. Route B — Expression objective (the governed case)

### Phase B1 — Authoring

| # | Actor | Action | Refs |
|---|---|---|---|
| B1.1 | Pricing Actuary | Needs an asymmetric burning-cost loss: under-pricing penalised twice as hard as over-pricing. No template fits. | `02` FR-MODEL-40 |
| B1.2 | Pricing Actuary | Writes the **loss** only: `w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2`. They never write a gradient, a hessian, or any code. | `02` FR-MODEL-40, §4.6 |
| B1.3 | Pricing Actuary | Declares parameters with types, defaults, and valid ranges: `w_under ∈ [1, 10]` default 2.0; `w_over ∈ [0.1, 10]` default 1.0. | `02` §4.6 |
| B1.4 | Frontend → Backend | Parses on every keystroke via a restricted AST walk against an allow-list. `eval` is never called. | `02` FR-MODEL-41, NFR-MODEL-8 |
| B1.5 | Backend | An earlier attempt using `numpy.where(...)` is rejected with `OBJECTIVE_GRAMMAR_VIOLATION` and a position-accurate error: attribute access is not in the grammar. | `02` FR-MODEL-41 |
| B1.6 | Pricing Actuary | Declares applicability: responses `burning_cost` and `claim_severity`, backends `xgboost`/`lightgbm`, `y ≥ 0`, offset not required. | `02` FR-MODEL-44 |

### Phase B2 — Derivation

| # | Actor | Action | Refs |
|---|---|---|---|
| B2.1 | Pricing Actuary | `POST /custom-objectives/{id}/derive`. | `02` FR-MODEL-40 |
| B2.2 | Backend → pricing-core | SymPy differentiates the loss with respect to `f` twice; `where` becomes `Piecewise`. | `02` §8 |
| B2.3 | Backend | Stores gradient and hessian **as expressions in the artifact**, with the derivation tool and version recorded. | `02` §4.6 |
| B2.4 | Frontend | Displays both derivatives in readable form. This is what the Approver will actually review — not opaque code. | `02` §5.3 |
| B2.5 | Pricing Actuary | Reads the hessian: `2*w*where(...)*exp(f)*(2*exp(f) - y)`. It is negative when `exp(f) < y/2`. The objective is **non-convex**, and the platform has made that visible before any fitting happened. | `02` FR-MODEL-43 |
| B2.6 | Pricing Actuary | Declares `hessian_strategy: clip_to_min` with `hessian_min: 1e-6`. | `02` FR-MODEL-43 |

### Phase B3 — Certification

| # | Actor | Action | Refs |
|---|---|---|---|
| B3.1 | Pricing Actuary | `POST /custom-objectives/{id}/certify` → `202` + Job. | `02` FR-MODEL-42 |
| B3.2 | Worker → pricing-core | Samples 10 000 `(y, f, w)` points with a persisted seed over the declared domain. | `02` §4.7 |
| B3.3 | Worker | **Symbolic vs numeric gradient**: max relative error 3.1e-9 → pass. | `02` §4.7 |
| B3.4 | Worker | **Symbolic vs numeric hessian**: 7.4e-8 → pass. | `02` §4.7 |
| B3.5 | Worker | **Finiteness**: no NaN/inf over `y ∈ [0, 1e7]`, `f ∈ [-20, 20]` → pass. | `02` §4.7 |
| B3.6 | Worker | **Convexity**: hessian negative on 12.3 % of the sampled domain → `violated`, mitigated by the declared strategy. | `02` FR-MODEL-43 |
| B3.7 | Worker | **Minimum at truth**: with `w_under = w_over`, loss is minimised at `f = log(y)` → pass. | `02` §4.7 |
| B3.8 | Worker | **Scale behaviour**: gradient magnitude spans six orders over the observed `y` range → `warn`, suggesting a log-scale variant. | `02` §4.7 |
| B3.9 | Worker | **Smoke fit**: 200 k synthetic rows, known relativities recovered within 1.2 % in 300 rounds → pass. | `02` §4.7 |
| B3.10 | Worker | `overall: certified_with_findings`. A `failed` certificate would block submission entirely. | `02` §4.7 |

### Phase B4 — Approval

| # | Actor | Action | Refs |
|---|---|---|---|
| B4.1 | Pricing Actuary | Submits with the certificate attached — required evidence for this artifact type. | `06` §3.3 |
| B4.2 | Backend | Escalates: convexity `violated` triggers the two-approver rule from the Approval Policy. | `02` FR-MODEL-43, `06` §4.2 |
| B4.3 | Approver #1 | Reviews the loss, the derived gradient and hessian, the certificate, and the convexity heat map over the sampled domain. Approves. | `06` FR-GOV-16 |
| B4.4 | Approver #2 | Asks why `w_under = 2.0` rather than 1.5 — a question about *judgement*, which is exactly where an approver's time should go, because the platform has already answered every question about correctness. | `06` FR-GOV-13 |
| B4.5 | Pricing Actuary | Adds the rationale (a claims-cost-of-under-pricing analysis) as a Commentary Block; resubmits. | `06` FR-GOV-28 |
| B4.6 | Approver #2 | Approves. Objective status → `approved`. | `02` FR-MODEL-46 |

---

## 4. Phase C — Use in a model

| # | Actor | Action | Refs |
|---|---|---|---|
| C1 | Analyst | Builds a GbmSpec with `objective: {kind: "custom", ref: "custom_objective:asymmetric-burning-cost@1"}`. | `02` §4.4 |
| C2 | Backend | Spec validation checks applicability: response `burning_cost` is declared, backend `xgboost` is declared, `y ≥ 0` holds. A `claim_count` response would fail `OBJECTIVE_NOT_APPLICABLE` **before any compute is spent**. | `02` FR-MODEL-44 |
| C3 | Worker → pricing-core | `compile_objective()` builds vectorised NumPy gradient/hessian functions from the stored expression tree. **The user's text is never executed** — only the platform's compiled tree. | `02` FR-MODEL-40, NFR-MODEL-8 |
| C4 | Worker | Fits. Each round: computes gradient and hessian, checks finiteness, applies `clip_to_min`. | `02` FR-MODEL-48 |
| C5 | Worker | On a later fit with different data, a NaN gradient appears at round 412; the fit aborts with `OBJECTIVE_NONFINITE_DERIVATIVE`, naming the round and the offending input range. It does not silently produce a degenerate model. | `02` FR-MODEL-48 |
| C6 | Analyst | Traces it to a single row with `y = 0` and an extreme offset; fixes the data issue, refits. | — |
| C7 | Analyst | Model reaches `approved`, which is only possible because the objective is itself `approved`. | `02` R4, FR-OVR-14 |

---

## 5. Phase D — Change and blast radius

| # | Actor | Action | Refs |
|---|---|---|---|
| D1 | Pricing Actuary | Six months on, wants `w_under = 2.5`. | — |
| D2 | Backend | Editing an `approved` objective is refused; the change creates version `@2` needing fresh certification and approval. | `02` FR-MODEL-46 |
| D3 | Pricing Actuary | `GET /custom-objectives/{id}/usage` — `@1` is used by 4 Models, 2 Peril Structures, and 1 live Rating Version. | `02` FR-MODEL-47 |
| D4 | Pricing Actuary | Understands that adopting `@2` means refitting those models and a new Rating Version. Existing models keep `@1` pinned and keep working. | FR-OVR-1 |
| D5 | Pricing Actuary | Certifies and approves `@2`; refits one model with it and compares against the `@1` model on the shared holdout. | `02` FR-MODEL-56 |
| D6 | Admin | Marks `@1` `deprecated`: existing pinned uses continue, new specs cannot select it. | `02` FR-MODEL-46 |

---

## 6. Phase E — Defect response (exception path)

| # | Actor | Action | Refs |
|---|---|---|---|
| E1 | Analyst | Discovers that the objective mis-weights when `w` (exposure) is very small — an interaction the certification sampling did not reach. | `02` §4.7 |
| E2 | Pricing Actuary | `GET /custom-objectives/{id}/usage` gives the blast radius immediately: which models, which rating versions, which live deployments. | `02` FR-MODEL-47 |
| E3 | Pricing Actuary | Assesses live pricing impact using the affected model's diagnostics and current monitoring. | `05` FR-MON-11 |
| E4 | Deployer | If material, rolls back the affected Rating Version (WF-04 phase H). | `03` FR-RATE-52 |
| E5 | Pricing Actuary | Authors `@3` with a corrected loss, and **extends the certification sampling range** so this class of defect is caught next time. | `02` §4.7 |
| E6 | Admin | The whole sequence — discovery, blast radius, rollback, correction — is in the audit log with actors and timestamps. | `06` FR-GOV-20 |

---

## 7. Failure and exception paths

| Situation | Behaviour | Refs |
|---|---|---|
| Out-of-grammar expression | `OBJECTIVE_GRAMMAR_VIOLATION` with a position-accurate error; never `eval`ed | `02` FR-MODEL-41 |
| AST exceeds node/depth limits | Rejected at parse | `02` FR-MODEL-41 |
| Division by a sub-expression that can be zero over the declared domain | Certification failure, not a runtime surprise | `02` §4.6 |
| Certificate `failed` | Submission blocked entirely | `02` FR-MODEL-42 |
| Convexity violated without a declared hessian strategy | Submission blocked | `02` FR-MODEL-43 |
| Submitted with one approver when two are required | `EVIDENCE_INCOMPLETE` / policy escalation | `06` §4.2 |
| Objective used with an inapplicable response | `OBJECTIVE_NOT_APPLICABLE` at spec validation, before compute | `02` FR-MODEL-44 |
| Model with an unapproved objective submitted for approval | `OBJECTIVE_NOT_APPROVED` | `02` R4 |
| NaN/inf gradient during fitting | Fit aborts with the round and input range named | `02` FR-MODEL-48 |
| Objective exceeds its per-round time budget | Fit aborts with a typed error | `02` FR-MODEL-48 |

---

## 8. Postconditions

- An `approved`, versioned Custom Objective with its loss, platform-derived derivatives,
  parameters, applicability, and hessian strategy.
- An Objective Certificate that a reviewer can read and an auditor can rely on.
- Two approval decisions with comments, plus the rationale Commentary Block.
- A complete usage index enabling blast-radius assessment at any time.
- No user-supplied code anywhere in the fitting path — only expressions parsed against an
  allow-list, differentiated by the platform, and compiled by the platform.

---

## 9. Traceability

| Phase | Requirements exercised |
|---|---|
| A — Template | `02` FR-MODEL-38, 39, 42, 44, 46 |
| B1 — Authoring | `02` FR-MODEL-40, 41, 44; NFR-MODEL-8 |
| B2 — Derivation | `02` FR-MODEL-40, 43 |
| B3 — Certification | `02` FR-MODEL-42, 43; NFR-MODEL-5 |
| B4 — Approval | `02` FR-MODEL-46; `06` FR-GOV-10..19, 28 |
| C — Use | `02` FR-MODEL-44, 48; R4; FR-OVR-14 |
| D — Change | `02` FR-MODEL-46, 47, 56 |
| E — Defect | `02` FR-MODEL-47; `03` FR-RATE-52; `06` FR-GOV-20 |

## 10. Timing

| Phase | Elapsed |
|---|---|
| Route A (template) | < 1 hour end to end |
| B1–B2 authoring + derivation | hours |
| B3 certification | < 3 min compute (NFR-MODEL-5) |
| B4 approval | 1–5 days |
| C first fit | as any GBM fit, +≤ 25 % for a custom objective (NFR-MODEL-2) |
| E defect response | hours to rollback, days to corrected version |
