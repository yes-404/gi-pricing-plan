# Roadmap

**Status:** draft · **Derived from:** the Phase 0 specification suite, not from `CLAUDE.md`
§9 alone. Where this document and `CLAUDE.md` §9 differ, §9 is authoritative and the
difference is flagged as a recommendation for the maintainer to accept or reject.

---

## 1. How to read this

`CLAUDE.md` §9 fixes five phases. This roadmap adds what the specs now make computable:
the **build order forced by module dependencies**, the **things that cannot be retrofitted**
and therefore must land earlier than their owning phase, the **decisions that gate each
phase**, and where the **effort is actually concentrated**.

Three things this document deliberately does not do:

- It does not re-order or rename the phases. That is `CLAUDE.md` §9's call.
- It does not give dates. Sizing is relative and the assumption is stated in §10.
- It does not resolve open questions. It says *which* ones block *what*, so you can answer
  them in the order that unblocks work, rather than all 45 at once.

---

## 2. Where the project is

| | |
|---|---|
| **Phase 0 (Specification)** | Effectively complete — 8 specs, 5 workflows, 5 ADRs, 31 contracts, 400 requirements |
| **Blocking Phase 1** | 45 open questions, 2 spikes, and the skills research in `skills-map.md` §7 |
| **Code written** | None, by design (`CLAUDE.md` §0) |

The remaining Phase 0 work is a **decision backlog, not a writing backlog**. Every open
question already carries options, trade-offs, and a recommendation.

---

## 3. Before Phase 1 — the on-ramp

Three tracks that can run concurrently and mostly do not need each other.

### Track A — Skills research (the maintainer's stated next step, `CLAUDE.md` §8)

[`skills-map.md`](skills-map.md) covers two axes. **Build** (§1–§6) is ordered by
risk × unfamiliarity in its §7:

1. Custom objectives end to end — restricted AST parsing, SymPy derivation, certification,
   XGBoost/LightGBM `base_margin`
2. ZEN Engine JDM and its numeric semantics
3. glum GLM API and standard errors
4. Polars lazy execution at 10 M+ rows
5. Pydantic v2 discriminated unions → JSON Schema
6. Vue Flow custom nodes
7. Low-latency Python serving

**Run** (§8–§9) covers delivery practice and audit. Three of those items are not
sequenceable after the build list because they shape first-sprint decisions:
**requirement traceability**, the **walking skeleton** (§5 below is literally its output),
and **reproducibility auditing**. Start them in parallel.

### Track B — Two spikes that need code

| Spike | Question | Why it cannot wait |
|---|---|---|
| **S1 — ZEN decimal semantics** | OQ-RATE-1 | If JDM evaluates money in binary float, FR-OVR-7 breaks on the p99 path and **ADR-0004 is reopened**. This changes Phase 2's foundation. Highest-risk unknown in the suite. |
| **S2 — `exact`-mode GBM latency** | OQ-RATE-2 | Determines whether production rating can ever call the model directly, which silently resolves OQ-MODEL-3. Changes what the DAG designer must offer. |

Both are small — days, not weeks — and both are cheap insurance against a Phase 2 rewrite.

### Track C — The decision backlog, sequenced

You do not need to answer 45 questions. You need to answer **7 before Phase 1 starts**:

| Question | Why it blocks Phase 1 |
|---|---|
| **OQ-OVR-2** licence | Blocks nothing technically; blocks every external contribution and the public repo story |
| **OQ-PLAT-1** Celery vs Postgres queue | Job submission is in the first sprint; transactional enqueue interacts with the audit rule (`06` R2) |
| **OQ-MODEL-1** expression objectives in Phase 1? | Decides whether the AST parser and SymPy derivation are Phase 1 or Phase 2 scope — a material slice of work |
| **OQ-DATA-1** large-loss capping: dataset or model? | Sits on the boundary between the two biggest Phase 1 workstreams; changing it later is a contract change |
| **OQ-MODEL-5** credibility standard | Needed to implement `credibility_weighted` grouping |
| **OQ-DATA-2** append ingestion | Only if the first real dataset is large enough that full snapshots hurt |
| **OQ-OVR-5** notebook escape hatch | Affects whether a client library is Phase 1 scope |

The other 38 can wait for the phase that needs them (§9).

---

## 4. Build order, and why it is not negotiable

`00-overview.md` DEP-1 fixes the dependency direction:

```
PLAT ──▸ GOV ──▸ DATA ──▸ MODEL ──▸ RATE ──┬─▸ OPT
                                            └─▸ MON
```

A module never imports from a module to its right. Two consequences worth internalising:

- **`MON` cannot be built before `RATE`**, because it consumes production traces. Any
  attempt to start monitoring early produces a system monitoring nothing.
- **`OPT` needs both `MODEL` (demand models) and `RATE` (batch scoring, baseline pricing)**,
  which is why it sits in Phase 4 despite being conceptually independent.

---

## 5. What cannot be retrofitted

**This is the most important section of this document.** Several capabilities belong to
later phases by ownership but must be built into Phase 1's foundations, because
retrofitting them is a rewrite rather than an addition.

| Must land in Phase 1 | Owning spec | Why retrofitting fails |
|---|---|---|
| **Append-only audit log, written in the caller's transaction** | `06` R2, FR-GOV-20 | Every write path must call it. Adding audit later means revisiting every mutation in the codebase and still having no history for anything already done. |
| **Artifact immutability + versioning + `parent_id`** | FR-OVR-1, ID-2 | If entities are mutable in v1, every artifact table needs a data migration and the historical record is simply gone. |
| **`model-schema` as the single source of truth** | ADR-0002 | Generated OpenAPI and TS types are trivial from day one and a large refactor once shapes exist in three places. |
| **The Job model with progress and cancellation** | FR-OVR-10, FR-PLAT-7..16 | Synchronous endpoints that later become jobs change every caller, including the frontend's whole interaction model. |
| **Decimal money discipline** | FR-OVR-7, `03` R2 | Retrofitting is a data migration *plus* a correctness audit of every computed figure ever displayed. |
| **`trace_id` propagation API → worker → core** | FR-OVR-3, `07` R4 | Cheap to thread through from the start; invasive afterwards. |
| **RBAC checks in the backend from the first endpoint** | `06` FR-GOV-2 | "We'll add auth later" reliably produces endpoints that assume no caller identity. |
| **Content-addressed blob store** | ID-4 | Changing storage layout later invalidates every stored reference. |

None of these require the *full* module. Phase 1 needs the audit **write path**, not the
audit explorer UI; the approval **state machine**, not the inbox. The user-facing surface
is Phase 3's job.

---

## 6. Phase 1 — Modelling Workbench

**Goal (`CLAUDE.md` §9):** dataset upload + validation + profiling, GLM and XGBoost fitting
(incl. custom objectives), factor management, diagnostics, model versioning. Demo on
freMTPL2.

**Demo-able outcome:** an actuary loads freMTPL2, watches validation fail on a real
problem, fixes it, acknowledges a warning, bands and groups factors, fits a GLM and an
XGBoost model, compares them, and gets one approved — i.e. **`wf-01` executed end to end**.

### Workstreams

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| **W1** | Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-0001), docker compose | — | Must be first; everything else assumes it |
| **W2** | Platform core: jobs, blobs, settings, OIDC auth, health, tracing | W1 | ~35 of 60 `PLAT` requirements |
| **W3** | Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | W1, W2 | §5 — skeleton only, no governance UI |
| **W4** | Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | W2, W3 | All 49 `DATA` requirements |
| **W5** | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates | W4 | All 78 `MODEL` requirements — the largest single workstream |
| **W6** | Frontend: app shell, dataset views, **validation report view**, **factor workbench**, model detail, diagnostics | W4, W5 | The two bolded views are where `01` §5.3 and `02` §5.3 place their interaction requirements |
| **W7** | freMTPL2 demo seed | W4, W5, W6 | `07` FR-PLAT-37 — one command to a working system |

W4 and W5 are sequential in contract terms but their *frontend* work (W6) can start as soon
as the contracts are frozen, which is a Phase 1 parallelisation opportunity worth taking.

### Requirement coverage

≈ **177 of 375** module requirements — **roughly 47 % of the entire platform's requirement
surface sits in Phase 1.**

> ### Recommendation: split Phase 1
>
> Phase 1 as scoped is nearly half the platform and has no intermediate demo. Consider:
>
> - **Phase 1a — Data Workbench.** W1–W4 + the dataset half of W6. Exit: a dataset reaches
>   `validated` on freMTPL2, with the validation report and profile visible.
> - **Phase 1b — Modelling Workbench.** W5 + the modelling half of W6 + W7. Exit: `wf-01`
>   end to end.
>
> This costs nothing — the split falls on the existing module boundary — and buys a real
> demo months earlier, plus an honest checkpoint on whether the validation design survives
> contact with real data. **This is a recommendation; §9's phasing stands unless you
> accept it.**

### Top risks

| Risk | Mitigation |
|---|---|
| Validation engine is under-estimated — 48 built-in rules across four layers with sandboxing | Build layers 1 and 3 first (they gate fitting); layers 2 and 4 can follow |
| Custom objectives are a research task, not a coding task | Answer OQ-MODEL-1; if templates-only, Phase 1 shrinks materially |
| Polars/DuckDB performance at 10 M rows discovered late | Test against a realistic dataset in W4, not at the end |
| Diagnostics scope creep — `02` lists a lot of them | FR-MODEL-50 (universal) is the gate; 51/52 can land incrementally |

---

## 7. Phase 2 — Rating Engine

**Goal:** DAG designer, rate tables, reference data, real-time + batch scoring, dislocation.

**Demo-able outcome:** **`wf-02` end to end** plus the deployment half of `wf-04` — an
approved model becomes rate tables, becomes a rating version, passes regression and
dislocation, and serves a live quote inside the latency budget.

### Workstreams

| # | Workstream | Notes |
|---|---|---|
| **W8** | **Spike S1/S2 resolution and ADR-0004 confirmation** | Must complete before W9. If S1 fails, this phase is re-planned |
| **W9** | Rating algorithm contract, validation, bundle compilation | `03` FR-RATE-1..13, 22..27 |
| **W10** | Rate tables incl. seeding from models, diffs, bulk operations, import/export | FR-RATE-14..21 |
| **W11** | Scoring: real-time, batch, trace, one shared evaluator | FR-RATE-34..42; NFR-RATE-1 is the hard target |
| **W12** | Testing: golden quotes, property assertions, regression runs | FR-RATE-43..45 |
| **W13** | Dislocation with attribution | FR-RATE-46..49 |
| **W14** | Deployment: environments, atomic switchover, rollback, shadow | FR-RATE-50..55; `07` FR-PLAT-28..31 |
| **W15** | Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views | The DAG designer is the single largest frontend effort in the project |

### Requirement coverage

≈ **67 `RATE` + ~25 remaining `PLAT`** requirements.

### Top risks

| Risk | Mitigation |
|---|---|
| **OQ-RATE-1** — ZEN decimal semantics invalidates ADR-0004 | S1 spike before any W9 work. Design toward integer minor units so the engine's numeric type is a non-issue |
| NFR-RATE-1 (p99 < 50 ms) missed and expensive to recover | Build the latency harness in W11 alongside the evaluator, not after |
| DAG designer is under-estimated | It is a graph editor with live validation — treat as its own project with its own spike |
| Rate table scale (vehicle × area = millions of cells) | OQ-RATE-3; the recommendation already sets a spill threshold |

---

## 8. Phase 3 — Governance

**Goal:** RBAC, approvals, audit UI, model documentation generation.

**Demo-able outcome:** **`wf-05` end to end** — a custom objective authored, certified,
two-approver reviewed, used, and audited — plus a generated dossier that would survive
external review.

### Workstreams

| # | Workstream | Notes |
|---|---|---|
| **W16** | Full scoped RBAC, custom roles, break-glass | `06` FR-GOV-1..8 |
| **W17** | Approval policies, escalation, evidence enforcement, attestations | FR-GOV-9..19 |
| **W18** | **Approvals inbox with inline evidence** | FR-GOV-16 — "the screen where the platform earns its keep" |
| **W19** | Audit explorer, chain verification, export | FR-GOV-20..26 |
| **W20** | Dossier generation, commentary blocks, PDF, point-in-time regeneration | FR-GOV-27..31 |
| **W21** | Regulatory evidence export | FR-GOV-32 |
| **W22** | Model risk tiering, if OQ-GOV-4 is accepted | Small addition to Approval Policy |

Much of the *write path* already exists from Phase 1 (§5). Phase 3 is largely the
**surfacing** of it — which is why it is comparatively low-risk despite being 43
requirements.

---

## 9. Phase 4 — Optimisation & Monitoring

**Goal:** demand models, constrained optimisation, drift monitoring, GIPP consistency.

**Demo-able outcome:** **`wf-03` end to end** plus the monitoring half of `wf-04` — a rate
change proposed by the optimiser with GIPP evidence, deployed, then measured against what
it promised.

### Workstreams

| # | Workstream | Notes |
|---|---|---|
| **W23** | Demand models, price-variation reporting, elasticity with CIs | `04` FR-OPT-1..7 |
| **W24** | Optimisation runs, constraints, binding analysis, frontier | FR-OPT-8..17 |
| **W25** | GIPP checks, price-walking, disparity reporting | FR-OPT-18..24 |
| **W26** | Materialisation into rate tables | FR-OPT-25..28 |
| **W27** | Monitoring: monitors, drift, A/E, demand, rate achieved, operational | `05` FR-MON-1..27 |
| **W28** | Alerting lifecycle and routing | FR-MON-28..32 |
| **W29** | Dashboards and monitoring packs | FR-MON-33..35 |

**Sequencing note:** W27 (monitoring) delivers value the moment Phase 2 is live and does
**not** depend on W23–W26. If Phase 4 is long, **pull monitoring forward** — a deployed
rating structure with no monitoring is the least comfortable state the platform can be in.

---

## 10. Decision gates

Which open questions must be answered before which phase. Answer them in this order and
you never block on a decision you have not reached.

| Gate | Questions | Count |
|---|---|---|
| **Before Phase 1** | OQ-OVR-2, OQ-OVR-5, OQ-PLAT-1, OQ-DATA-1, OQ-DATA-2, OQ-MODEL-1, OQ-MODEL-5 | 7 |
| **Before Phase 2** | **OQ-RATE-1**, OQ-RATE-2, OQ-RATE-3, OQ-RATE-4, OQ-RATE-6, OQ-MODEL-3, OQ-PLAT-3 | 7 |
| **Before Phase 3** | OQ-GOV-1..5, OQ-OVR-1, OQ-MODEL-7 | 7 |
| **Before Phase 4** | OQ-OPT-1..6, OQ-MON-1..5, OQ-DATA-4 | 12 |
| **Deferred / any time** | OQ-OVR-3, OQ-OVR-4, OQ-DATA-3, OQ-DATA-5, OQ-DATA-6, OQ-MODEL-2, OQ-MODEL-4, OQ-MODEL-6, OQ-RATE-5, OQ-PLAT-2, OQ-PLAT-4, OQ-PLAT-5 | 12 |

Only **OQ-RATE-1** has the power to invalidate an accepted ADR.

---

## 11. Sizing

Effort is expressed relative to the requirement surface and the number of independently
parallelisable workstreams. **No dates, because team size is unknown.**

| Phase | Requirement share | Parallelisable streams | Relative size | Shape |
|---|---|---|---|---|
| 0 — Specification | — | — | done | — |
| On-ramp (§3) | — | 3 | XS | Research + 2 spikes + 7 decisions |
| 1 — Modelling Workbench | ~47 % | 3–4 after W1 | **XL** | Broad; recommend splitting (§6) |
| 2 — Rating Engine | ~24 % | 2–3 | **L** | Deep; one large frontend, one hard NFR |
| 3 — Governance | ~11 % | 3 | **M** | Mostly surfacing Phase 1 foundations |
| 4 — Optimisation & Monitoring | ~18 % | 2 independent halves | **L** | Two loosely-coupled halves; monitoring can come early |

The distribution is worth absorbing: **Phase 1 is not "the first phase", it is nearly half
the platform.** Planning it as one undifferentiated block is the most likely way this
project stalls.

---

## 12. What "done" looks like, per phase

Each phase is complete when its workflow document executes end to end against real data —
not when its requirements are individually ticked off.

| Phase | Exit criterion |
|---|---|
| 0 | An engineer could start Phase 1 from the docs alone (`CLAUDE.md` §9) |
| 1 | [`wf-01`](workflows/wf-01-dataset-to-model.md) end to end on freMTPL2, including the validation-failure loop |
| 2 | [`wf-02`](workflows/wf-02-model-to-rating-version.md) end to end, plus `wf-04` phases A–D, meeting NFR-RATE-1 |
| 3 | [`wf-05`](workflows/wf-05-custom-objective-lifecycle.md) end to end, plus a dossier that survives external review |
| 4 | [`wf-03`](workflows/wf-03-rate-change-impact.md) end to end, plus `wf-04` phases E–H |

The workflow documents were written with timing tables for exactly this purpose.
