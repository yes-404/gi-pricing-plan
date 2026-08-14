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
  them in the order that unblocks work, rather than all 46 at once.

---

## 2. Where the project is

| | |
|---|---|
| **Phase 0 (Specification)** | Effectively complete — 8 specs, 5 workflows, 5 ADRs, 31 contracts, 408 requirements |
| **Blocking Phase 1** | **7 decisions** (§3). Spike S3 closed 2026-08-14. Track A research **closed**; 45 of 46 open questions remain but only 7 gate Phase 1 |
| **Code written** | None, by design (`CLAUDE.md` §0) |

The remaining Phase 0 work is a **decision backlog, not a writing backlog**. Every open
question already carries options, trade-offs, and a recommendation.

---

## 3. Before Phase 1 — the on-ramp

Three tracks that can run concurrently and mostly do not need each other.

### Track A — Skills research · **CLOSED 2026-08-14**

Track A is closed. **Not because every question was answered** — three were not — but
because **nothing left in it belongs in it**. Each unfinished fragment turned out to be
build work, an acceptance test, or a spike, and has been re-homed to where it will actually
get done. A research track that keeps items it cannot discharge is a parking lot.

Evidence: [`research/track-a-findings.md`](research/track-a-findings.md).

| # | Item (`skills-map.md` §7) | Outcome |
|---|---|---|
| 1 | Custom objectives end to end | **Partly closed.** SymPy derivation ✔ (F2) and XGBoost `base_margin` ✔ (F5) verified empirically; the certification design was found *wrong* and rewritten (F3 → FR-MODEL-68..70). Two fragments re-homed ↓ |
| 2 | ZEN Engine decimal semantics | **Closed** ✔ — `rust_decimal`, ADR-0004 confirmed, OQ-RATE-1 decided (F1) |
| 3 | glum standard errors | **Closed** ✔ — `std_errors()`/`covariance_matrix()` confirmed to exist (F8) |
| 4 | Polars at 10 M+ rows | **Partly closed.** Streaming-engine status and an open group-by memory regression found (F10), validating ADR-0005's split. Benchmark re-homed ↓ |
| 5 | Pydantic v2 → JSON Schema | **Closed** ✔ — discriminated unions confirmed, and a `Decimal` gap found that would let a lossy payload satisfy the contract (F6/F7) |
| 6 | Vue Flow custom nodes | **Documentation only.** `isValidConnection`, node memoisation, Web Workers (F12). Re-homed ↓ |
| 7 | Low-latency Python serving | **Documentation only**, but actionable: Pydantic costs ~1 ms of the 50 ms budget → NFR-RATE-13 (F11). Re-homed ↓ |

#### Re-homed, not dropped

| Fragment | New home | Why there |
|---|---|---|
| Restricted AST parser for the expression grammar | **Phase 1, W5** | Nothing left to research — `02` §4.6 specifies the grammar. This is build work, and the only place user input reaches the numerical core |
| LightGBM `init_score` symmetry | ~~Spike S3~~ **run 2026-08-14** | Symmetric at fit, **asymmetric at scoring** — `predict()` has no offset parameter. Now FR-MODEL-72 (F13) |
| Polars 10 M-row benchmark | **Phase 1, W4 acceptance** | It is NFR-DATA-1/3, measured against real data — an acceptance test, not reading |
| Vue Flow depth | **Phase 2 on-ramp, W15** | Does not block Phase 1; belongs with the DAG designer it serves |
| Low-latency measurement | **Spike S2** / Phase 2 W11 | Already partly discharged into NFR-RATE-13; the rest is measurement |

#### What Track A cost and returned

Four executable spikes. It closed one open question, **found two specification defects**
that would otherwise have surfaced in Phase 1 as confusing failures, and **corrected one
fabricated figure** presented as a measurement. That last one is the strongest argument for
running research against a spec rather than reading about it.

**Practice items** (`skills-map.md` §8–§9) were never in scope for Track A as *research* —
they are working habits, several already exercised: requirement traceability, audit
automation, and the walking-skeleton framing that produced §5 below. They stay live as
practice, not as an open task.

### Track B — Spikes that need code

**Track A research (2026-08-14) has already run four spikes** and closed the substance of
S1 — see [`research/track-a-findings.md`](research/track-a-findings.md). Remaining:

| Spike | Question | Why it cannot wait |
|---|---|---|
| **S1 (re-scoped)** | FR-RATE-56/57 | ~~Does the engine do decimal?~~ **It does** — `rust_decimal`, ADR-0004 stands. Now: does arbitrary precision survive the Python binding in both directions, and can a rateable path reach a `maths-nopanic` sink that returns `0` instead of raising? Both failure modes are **silent**. |
| **S2 — `exact`-mode GBM latency** | OQ-RATE-2 | Now the highest-risk remaining unknown. Determines whether production rating can ever call the model directly, which silently resolves OQ-MODEL-3. |
| ~~**S3 — LightGBM `init_score`**~~ ✔ **CLOSED 2026-08-14** | FR-MODEL-72 | The assumption was **half wrong**: symmetric at fit time, but `Booster.predict()` has no offset parameter at all, so a scoring path ported from XGBoost silently omits the offset entirely. Fixed as FR-MODEL-72 (F13). |

S1 and S2 remain — small, days not weeks, and cheap insurance against a Phase 2 rewrite. S3 is done.

### Track C — The decision backlog, sequenced

You do not need to answer 46 questions. You need to answer **7 before Phase 1 starts**:

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

### Outstanding work — consolidated

Everything still open before Phase 1 can start, in one place. Tracks A–C above explain
*why*; this is the list.

| # | Task | Kind | Owner | Blocks |
|---|---|---|---|---|
| **1** | **OQ-OVR-2** — project licence | decision | maintainer | Public contribution, not code |
| **2** | **OQ-OVR-5** — notebook escape hatch | decision | maintainer | Phase 1 scope |
| **3** | **OQ-PLAT-1** — Celery vs a transactional Postgres queue | decision | maintainer | W2, first sprint |
| **4** | **OQ-DATA-1** — where large-loss capping lives | decision | maintainer | W4/W5 boundary; contract change if deferred |
| **5** | **OQ-DATA-2** — append ingestion vs full snapshots | decision | maintainer | W4, only if the first dataset is large |
| **6** | **OQ-MODEL-1** — do expression objectives ship in Phase 1? | decision | maintainer | W5 scope, materially |
| **7** | **OQ-MODEL-5** — credibility standard | decision | maintainer | W5 grouping implementation |
| ~~8~~ | ~~**S3** — LightGBM `init_score` symmetry~~ ✔ **done 2026-08-14** | spike | — | Closed. Found a real asymmetry → FR-MODEL-72 |
| **9** | **Phase 1 split** — accept or reject 1a/1b (§5 recommendation) | decision | maintainer | How Phase 1 is planned |

**Not blocking Phase 1, but do not lose them:**

| Task | Kind | Due |
|---|---|---|
| **S1 (re-scoped)** — precision across the ZEN binding; `maths-nopanic` reachability | spike | Before Phase 2 |
| **S2** — `exact`-mode GBM latency at 200 rps | spike | Before Phase 2 — highest-risk remaining unknown |
| 6 Phase-2 decisions (OQ-RATE-2/3/4/6, OQ-MODEL-3, OQ-PLAT-3) | decisions | Before Phase 2 |
| 7 Phase-3 decisions · 12 Phase-4 decisions · 12 any-time | decisions | Per gate (§10) |
| Vue Flow depth · Polars benchmark · AST parser | re-homed from Track A | Within their phases |

**Nothing in the document suite is outstanding.** Specs, workflows, ADRs, contracts and the
audit are complete and passing; the remaining Phase 0 work is entirely decisions and
spikes — eight items, of which **seven are decisions only the maintainer can make** — the spike backlog for Phase 1 is now empty.

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
| ~~OQ-RATE-1 — ZEN decimal semantics invalidates ADR-0004~~ **retired 2026-08-14**: the engine uses `rust_decimal`, so this risk did not materialise. Replaced by two silent-failure risks at the boundary (FR-RATE-56/57) | Re-scoped S1 before W9; integer-minor-units is no longer needed as a mitigation |
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
| **Before Phase 2** | ~~OQ-RATE-1~~ ✔ *decided 2026-08-14*, **OQ-RATE-2**, OQ-RATE-3, OQ-RATE-4, OQ-RATE-6, OQ-MODEL-3, OQ-PLAT-3 | 7 (6 open) |
| **Before Phase 3** | OQ-GOV-1..6, OQ-OVR-1, OQ-MODEL-7 | 8 |
| **Before Phase 4** | OQ-OPT-1..6, OQ-MON-1..5, OQ-DATA-4 | 12 |
| **Deferred / any time** | OQ-OVR-3, OQ-OVR-4, OQ-DATA-3, OQ-DATA-5, OQ-DATA-6, OQ-MODEL-2, OQ-MODEL-4, OQ-MODEL-6, OQ-RATE-5, OQ-PLAT-2, OQ-PLAT-4, OQ-PLAT-5 | 12 |

**OQ-RATE-1 was the one question able to invalidate an accepted ADR. It has been answered**
— by a spike, not an opinion — and ADR-0004 survived
([`research/track-a-findings.md`](research/track-a-findings.md) F1).

The successor is **OQ-RATE-2**: whether an `exact`-mode GBM call fits the 50 ms p99 budget.
It cannot invalidate an ADR, but it decides OQ-MODEL-3 by force rather than by choice, and
it is likewise only answerable with code.

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
