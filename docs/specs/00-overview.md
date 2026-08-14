# 00 — System Overview

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `OVR`

---

## 1. Purpose & scope

### 1.1 What the platform is

An open-source general insurance pricing platform for the UK/EU market, covering the full
pricing lifecycle:

```
data preparation → risk modelling → rating algorithm design → deployment/scoring
      → monitoring → governance
```

It is positioned as an alternative to WTW Radar/Emblem and comparable commercial suites.
Primary users are **pricing actuaries and analysts** who are technically capable
(Python/notebooks) but expect a polished, interactive UI for day-to-day work.

Three design values dominate every trade-off in this suite, in this order:

1. **Reproducibility** — any number the platform ever displayed can be recomputed from
   persisted, versioned inputs.
2. **Auditability** — every state change that affects a price is attributable to a user,
   a time, and a justification.
3. **Transparency of the maths** — the model and rating structure are inspectable
   artifacts, never opaque binaries. A black-box model may be *fitted*, but it may not be
   *deployed* without an accompanying transparency artifact (§2, "Transparency artifact").

### 1.2 What this document does

`00-overview.md` is the anchor of the specification suite. It defines:

- the system context and actors (§1.3–1.4),
- the authoritative shared vocabulary (§2) — every other document must use these names,
- system-level requirements that no single module owns (§3),
- the entity map that module data contracts hang off (§4),
- the cross-cutting API, error, and versioning conventions (§5),
- the module map and dependency rules (§7).

### 1.3 Out of scope (platform-wide)

The following are explicitly **not** built by this platform, in any phase:

| Not in scope | Rationale / expected source |
|---|---|
| Policy administration (PAS), quote & buy journeys | Consumes our scoring API; is not part of it |
| Claims handling, reserving, capital modelling | Adjacent actuarial domains with their own tooling |
| Reinsurance pricing and treaty structures | Different maths, different data model |
| General-purpose BI / ad-hoc reporting | DuckDB + notebook escape hatch is provided instead |
| An **embedded** notebook server | A client library is provided instead (OQ-OVR-5, decided 2026-08-14). Embedding JupyterLab would put arbitrary code execution inside the platform's security and audit boundary — the same problem custom objectives pose, and not one to solve twice. Revisited in Phase 4 once that sandboxing exists |
| Customer PII storage as a system of record | Datasets are pseudonymised snapshots (see FR-OVR-9) |
| Regulatory filing document *submission* | We generate documentation; humans file it |
| Broker/aggregator connectivity, panel management | Downstream of the scoring API |

### 1.4 Actors

Actors are used with these exact names in every workflow document.

| Actor | Description |
|---|---|
| **Analyst** | Prepares datasets, fits models, builds rating structures. Cannot approve. |
| **Pricing Actuary** | Everything an Analyst can do, plus acknowledges validation warnings and submits for approval. |
| **Approver** | Senior actuary / pricing manager. Approves models, custom objectives, and rating versions. Cannot approve own submissions. |
| **Deployer** | Promotes an approved rating version to an environment. Often the same person as Approver but a distinct permission. |
| **Auditor** | Read-only across everything, including the audit log and superseded artifacts. |
| **Admin** | Manages users, roles, environments, reference data, and system settings. |
| **Frontend** | The Vue 3 SPA. Never computes pricing numbers; renders what the backend returns. |
| **Backend** | The FastAPI application. Owns authorisation, persistence, orchestration. |
| **Worker** | Celery worker executing long-running jobs (validation, fitting, batch scoring). |
| **pricing-core** | Pure Python actuarial engine. No I/O, no web, no DB. Deterministic. |
| **Consumer System** | An external system (PAS, quote engine, aggregator feed) calling the scoring API. |

### 1.5 System context

```
                       ┌──────────────────────────────────────────┐
   Analyst /            │  Frontend — Vue 3 SPA                    │
   Actuary  ──────────► │  workbench · DAG designer · dashboards   │
                       └───────────────┬──────────────────────────┘
                                       │ HTTPS / JSON (OpenAPI-generated client)
                                       ▼
   Consumer   ────────► ┌──────────────────────────────────────────┐
   System               │  Backend — FastAPI                       │
   (scoring)            │  auth · RBAC · orchestration · audit     │
                       └───┬───────────┬───────────────┬──────────┘
                           │           │               │
            ┌──────────────▼──┐   ┌────▼─────┐   ┌─────▼───────────────┐
            │ PostgreSQL 16   │   │ Redis    │   │ Object store (S3)   │
            │ metadata, audit │   │ queue &  │   │ dataset parquet,    │
            │ artifacts (JSONB)│  │ cache    │   │ boosters, reports   │
            └─────────────────┘   └────┬─────┘   └─────────────────────┘
                                       │
                              ┌────────▼─────────┐
                              │ Celery Workers   │
                              │ validate · fit · │
                              │ score · monitor  │
                              └────────┬─────────┘
                                       │ imports
                              ┌────────▼─────────────────────────────┐
                              │ pricing-core (pure Python)           │
                              │ Polars · glum · XGBoost · LightGBM · │
                              │ pandera · ZEN Engine                 │
                              └──────────────────────────────────────┘
```

Batch/scheduled data movement (ingestion, nightly re-rates, monitoring aggregation) is
orchestrated by **Dagster** in `pipelines/`, which calls the same backend APIs and
`pricing-core` functions rather than reimplementing logic.

---

## 2. Concepts & glossary

This is the authoritative vocabulary. It restates and extends `CLAUDE.md` §7. **A new
term must be added here before it is used in any other document.**

### 2.1 Data layer

| Term | Definition |
|---|---|
| **Dataset** | A named, logical container for one body of policy/claims/exposure data (e.g. "Motor GB — quote & bind"). Holds no data itself; holds Dataset Versions. |
| **Dataset Version** | An **immutable** snapshot of data for a Dataset, identified by `dataset_id + version` (monotonic integer). Carries its schema, validation report, profile, and status. All modelling references a Dataset Version, never a Dataset. |
| **Dataset status** | `draft → validated → archived`. Fitting is permitted only on `validated`. `archived` is terminal and read-only but never deleted. |
| **Record grain** | The row meaning of a dataset table: `policy_exposure` (one row per policy × exposure period), `claim` (one row per claim), or `reference` (lookup table). |
| **Exposure** | Time-on-risk for a record, in years (`Decimal`, > 0). The offset/weight in frequency and burning-cost models. |
| **Reference Table** | Effective-dated lookup data used for validation and rating (postcode → rating area, vehicle → group, occupation codes). Versioned like datasets. |
| **Validation Rule** | A single named check with a severity (`fail`/`warn`/`info`), belonging to one of four layers: structural, referential, actuarial sanity, distributional. |
| **Validation Report** | The persisted, versioned result of running a Validation Rule Set against a Dataset Version: per-rule outcome, counts, sample offending keys. |
| **Acknowledgement** | An audited record of a Pricing Actuary accepting a `warn` outcome, with a mandatory justification. Required before a `warn`-carrying Dataset Version reaches `validated`. |
| **Profile** | Computed descriptive statistics for a Dataset Version: per-column distributions, missingness, cardinality, one-way exposure/claim summaries. |
| **PSI** | Population Stability Index — distributional distance of a column between two Dataset Versions (or a live population vs a reference). |

### 2.2 Modelling layer

| Term | Definition |
|---|---|
| **Factor** | A rating variable as used by a model or rating algorithm — a named transformation of one or more dataset columns (identity, banding, grouping, interaction, spline, offset). |
| **Level** | A discrete value a categorical Factor can take. |
| **Banding** | A Factor transformation mapping a continuous column to ordered intervals, defined by explicit boundaries. A first-class, versioned, auditable object. |
| **Grouping** | A Factor transformation mapping many Levels onto fewer Levels. First-class, versioned, auditable; carries the method used (manual, credibility-weighted, tree-derived) and the evidence for it. |
| **Base Level** | The reference Level of a categorical Factor against which relativities are expressed. Chosen by exposure (default: largest exposure) or set explicitly. |
| **Response** | The modelled quantity: `claim_count`, `claim_severity`, `burning_cost`, `retention`, `conversion`, `elasticity`. |
| **Peril** | A cause-of-loss partition of claims (e.g. `AD`, `TP_PD`, `TP_BI`, `THEFT`, `FIRE`, `WS`). |
| **Model** | A fitted statistical model for exactly one (peril, response) pair. Types: `glm`, `xgboost`, `lightgbm`, `ebm`. Immutable once fitted. |
| **Model Version** | Models are versioned within a Model Family; `parent_model_id` records lineage (refit, respecified, rebanded). |
| **Custom Objective** | A named, versioned definition of a non-standard loss, either *declarative* (parameterised template) or *expression* (restricted DSL). Reusable across models; has its own approval status. |
| **Transparency artifact** | The mandatory explanation attached to a non-GLM Model: a GLM approximation (fitted to the GBM's predictions) and/or a SHAP-based factor summary. Required before a Model can be referenced by a Rating Version. |
| **Peril structure** | The composition rule turning per-peril frequency × severity (or burning cost) predictions into a **Risk Premium**. |
| **Risk Premium** | Expected claims cost for a risk over the exposure period, before expenses, commission, profit loading, or optimisation. |
| **Diagnostics** | Persisted model quality evidence: deviance/AIC/BIC, dispersion, residual plots, lift/gains, actual-vs-expected by factor, Gini, calibration, cross-validation folds. |

### 2.3 Rating layer

| Term | Definition |
|---|---|
| **Rating Algorithm** | The declarative DAG of calculation steps that turns a quote's raw inputs into a final premium. |
| **Rating Step** | A node in the DAG. **Exactly seven types exist**: `input`, `lookup`, `expression`, `table`, `model_call`, `constraint`, `output`. |
| **Rate Table** | A versioned, typed table of rating factors/loadings keyed by one or more Factors. The unit an actuary edits when making a rate change. |
| **Rating Version** | An **immutable deployable bundle**: rating algorithm + all rate tables + referenced model artifacts + reference table pins. Lifecycle `draft → review → approved → live → retired`. |
| **Deployment** | The binding of a Rating Version to an Environment at a point in time. Recorded, reversible, audited. |
| **Environment** | A named runtime target: `dev`, `uat`, `prod`. Each owns its own live Rating Version deployments and service-account scopes. |
| **Scoring** | Evaluating a Rating Version for one or more risks. **Real-time** (single quote, target p99 < 50 ms) or **batch** (portfolio re-rate). |
| **Trace** | The per-step record of a single scoring call: step id, every intermediate value, table row matched, model output, and per-step timing. The backbone of explainability and dispute resolution. |
| **Dislocation** | The distribution of premium change between two Rating Versions over a fixed portfolio. |

### 2.4 Optimisation & monitoring layer

| Term | Definition |
|---|---|
| **Demand Model** | A model of customer behaviour (conversion or retention) as a function of price and risk characteristics. A `Model` with response `conversion`/`retention`. |
| **Price Elasticity** | ∂ log(demand) / ∂ log(price), derived from a Demand Model. |
| **Optimisation Run** | A constrained search over candidate price adjustments maximising an objective (volume, profit, or a blend) subject to business and regulatory constraints. |
| **GIPP** | General Insurance Pricing Practices. The binding rules are **ICOBS 6B** (in force 2022-01-01), announced by FCA PS21/5 and amended by PS21/11. ICOBS 6B.2.1R: a firm must not set a renewal price higher than the equivalent new business price. Scope is home and motor insurance. |
| **GIPP check** | An automated comparison of new-business and renewal price surfaces for equivalent risks, producing per-segment evidence and an overall verdict, attached to a Rating Version. |
| **Drift** | Change over time in the live population's factor distribution (input drift) or in model performance (concept drift). |
| **A/E** | Actual vs Expected — realised claims experience compared with model prediction, sliced by factor, cohort, and time. |

### 2.5 Governance layer

| Term | Definition |
|---|---|
| **Approval Request** | The submission of one Governed Artifact (Model, Custom Objective, Rating Version, Validation Rule, …) for review, carrying its evidence bundle, a required checklist, and a change summary. |
| **Audit Event** | An immutable, append-only record: `actor, at, action, entity_ref, before, after, justification, trace_id, source`. |
| **Model Documentation** | A generated, human-readable dossier for a Model, Peril Structure, or Rating Version, assembled from persisted artifacts — never hand-maintained. |
| **Artifact** | Any versioned, immutable, JSON-serialisable object the platform produces: Dataset Version, Validation Report, Model, Custom Objective, Rate Table, Rating Version, Optimisation Run. |

### 2.6 Terms deliberately avoided

To keep search and traceability clean, these words are **not** used as entity names:
"experiment" (use Model), "campaign" (use Optimisation Run), "ruleset" (use Rating
Algorithm, except "Validation Rule Set" which is explicitly qualified), "snapshot" (use
Dataset Version), "release" (use Rating Version or Deployment).

---

## 3. Functional requirements (system level)

System-level requirements that no single module owns. Module codes are defined in §7.1.

| ID | Requirement |
|---|---|
| **FR-OVR-1** | Every Artifact is immutable once it leaves `draft`. Corrections create a new version with `parent_id` set; nothing is edited in place or hard-deleted. |
| **FR-OVR-2** | Every Artifact is JSON-serialisable and round-trippable: export → import into a clean instance reproduces byte-identical scoring behaviour. Binary blobs (boosters, parquet) are referenced by content hash, never embedded as pickles. |
| **FR-OVR-3** | Every number displayed in the UI is traceable to the Artifact and computation that produced it, via a stable `provenance` reference (`{entity_type, entity_id, version, produced_by_job_id}`). |
| **FR-OVR-4** | Every state transition of a governed Artifact emits an Audit Event (see `06-governance.md`). Audit writes are in the same transaction as the state change. |
| **FR-OVR-5** | All pricing computation lives in `pricing-core` and is callable without the backend. The backend orchestrates and persists; it never contains actuarial maths. |
| **FR-OVR-6** | All shared data shapes are defined once in `packages/model-schema` and generated into (a) JSON Schema in `docs/contracts/schemas/`, (b) OpenAPI, (c) frontend TypeScript. No shape is hand-written twice. |
| **FR-OVR-7** | Monetary values are integer minor units (pence/cents) or `Decimal` throughout the rating path and all persisted rate tables. Floats are permitted only inside model fitting and diagnostics, never in a quoted premium. **One workspace, one currency** (OQ-OVR-3, decided 2026-08-14): the code is a workspace setting and is carried on every artifact's envelope, so multi-currency in Phase 4 adds FX effective-dating rather than migrating every monetary column. |
| **FR-OVR-8** | Determinism: given identical inputs and pinned artifact versions, model fitting and scoring reproduce identical outputs. All stochastic operations take an explicit persisted `random_seed`. |
| **FR-OVR-9** | Datasets are treated as pseudonymised. The platform stores no direct identifiers (name, address line, email, exact DOB) as modelling columns; ingestion rejects columns tagged `direct_identifier` unless explicitly configured as a passthrough key that is excluded from all Factors. |
| **FR-OVR-10** | Every long-running operation (validate, fit, score-batch, optimise, monitor) is a **Job** with a uniform lifecycle, progress, cancellation, log, and result reference (see `07-platform.md`). |
| **FR-OVR-11** | The platform exposes a documented OpenAPI 3.1 surface; the SPA is a pure client of it. Any action possible in the UI is possible via the API. |
| **FR-OVR-12** | Time is stored as UTC `timestamptz`. All business-effective dating (reference data, rating versions) uses explicit `effective_from` / `effective_to` half-open intervals `[from, to)`. |
| **FR-OVR-13** | Multi-tenancy is single-tenant-per-deployment in Phases 0–4. All schemas nonetheless carry a `workspace_id` so that a future tenancy split is not a data migration. |
| **FR-OVR-14** | An artifact may only reference artifacts that are in a state at least as mature as its own (a `live` Rating Version cannot reference a `draft` Model). Enforced at transition time, not just at creation. |

---

## 4. Data contracts — entity map

Detailed field-level contracts live in each module spec and in `docs/contracts/schemas/`.
This section fixes the relationships and the identity rules.

### 4.1 Entity relationship map

```
Workspace
 └── Dataset ──────< DatasetVersion ──< ValidationReport
                          │      └────< Profile
                          │
                          ├──────< Factor ──< Banding | Grouping
                          │
                          └──────< Model ──< Diagnostics
                                    │  └───< TransparencyArtifact
                                    ├── uses ▸ CustomObjective (optional)
                                    └── parent ▸ Model (lineage)

ReferenceTable ──< ReferenceTableVersion

RatingAlgorithm ──< RatingVersion ──< RatingStep
                          │      └──< RateTable (pinned versions)
                          ├── references ▸ Model (pinned)
                          ├── references ▸ ReferenceTableVersion (pinned)
                          └──< Deployment ──▸ Environment

RatingVersion ──< OptimisationRun ──< PriceAdjustmentProposal
RatingVersion ──< GippCheck
Deployment    ──< ScoringTrace (sampled) ──< MonitoringAggregate

* ──< ApprovalRequest ──< ApprovalDecision
* ──< AuditEvent
* ──< Job
```

### 4.2 Identity and versioning rules

| Rule | Detail |
|---|---|
| **ID-1** | Every entity has a `uuid` primary key (`UUIDv7`, time-ordered) plus a human-readable `slug` unique within its parent scope. |
| **ID-2** | Versioned entities carry `version: int` starting at 1, monotonically increasing per parent, and never reused — including after deletion of a draft. |
| **ID-3** | The canonical external reference to any artifact is `{type}:{slug}@{version}` (e.g. `model:motor-ad-freq@7`, `rating_version:motor-gb@27`). This string form appears in traces, documentation, and the audit log. The version is always the ID-2 integer — the earlier `motor-gb@2026-04` example contradicted ID-2 and the reference pattern, and was corrected 2026-08-14 when generation compared the two. |
| **ID-4** | Content-addressed blobs (parquet, booster JSON, report PDFs) are stored at `blob/{sha256}` and referenced by hash + size + media type. Identical content is stored once. |
| **ID-5** | Soft-delete only: entities gain `archived_at`; nothing is removed from the database. Physical purge is an Admin-only, audited, workspace-scoped operation used for GDPR erasure. |

### 4.3 Common field conventions

Every persisted entity carries the envelope below (defined once in `model-schema` as
`ArtifactEnvelope`, referenced by every module contract):

```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "slug": "string, ^[a-z0-9][a-z0-9-]{1,62}$",
  "version": 1,
  "status": "string (entity-specific enum)",
  "currency": "ISO 4217, e.g. GBP — the workspace's single currency (OQ-OVR-3)",
  "created_at": "timestamptz",
  "created_by": "uuid (user)",
  "updated_at": "timestamptz",
  "archived_at": "timestamptz|null",
  "parent_id": "uuid|null",
  "labels": {"string": "string"},
  "description": "string|null"
}
```

---

## 5. Interfaces — cross-cutting conventions

Module specs define their own endpoints; all of them obey the following.

### 5.1 URL and method conventions

- Base path `/api/v1`. Breaking changes bump to `/api/v2`; additive changes do not.
- Collections are plural nouns: `/api/v1/datasets`, `/api/v1/models`.
- Sub-resources nest one level maximum: `/api/v1/datasets/{id}/versions/{version}`.
- Actions that are not CRUD are `POST` to a verb sub-path:
  `POST /api/v1/dataset-versions/{id}/validate`, `POST /api/v1/models/{id}/submit`.
- Long-running actions return `202 Accepted` with a `Job` body and a `Location` header
  pointing at `/api/v1/jobs/{job_id}`.

### 5.2 Pagination, filtering, sorting

Cursor pagination everywhere (stable under concurrent writes):

```
GET /api/v1/models?limit=50&cursor=<opaque>&status=approved&sort=-created_at
→ 200 {"items": [...], "next_cursor": "<opaque>|null", "total_estimate": 1234}
```

### 5.3 Error model

A single RFC 9457 `application/problem+json` shape, with a stable machine `code`:

```json
{
  "type": "https://docs.gi-pricing.dev/errors/dataset-not-validated",
  "title": "Dataset version is not validated",
  "status": 409,
  "code": "DATASET_NOT_VALIDATED",
  "detail": "dataset:motor-gb@12 has status 'draft'; fitting requires 'validated'.",
  "instance": "/api/v1/models",
  "errors": [{"field": "dataset_version_id", "code": "INVALID_STATE", "message": "..."}],
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

Codes are namespaced per module and enumerated in each spec's Interfaces section.
`trace_id` is the OpenTelemetry trace id — **32 lowercase hexadecimal characters**, the
W3C `trace-id` form — and appears in every log line for the request, every problem
response, and every Audit Event (`07` R4).

The format is part of the contract, not a rendering detail: the value's whole purpose is
to join a problem response to a span in a trace backend, and an id in any other shape
correlates with nothing. Earlier examples in `06` and `07` showed a ULID; that was a
defect, corrected 2026-08-14 when W2 implemented the propagation.

### 5.4 Concurrency and idempotency

- Mutating requests on versioned entities require `If-Match: <etag>`; a mismatch yields
  `409 CONFLICT_STALE_WRITE`.
- All `POST` endpoints that create jobs or artifacts accept an `Idempotency-Key` header;
  a repeat within 24 h returns the original result.

### 5.5 pricing-core function conventions

`pricing-core` is the only place actuarial maths lives (FR-OVR-5). Its public API obeys:

- Pure functions or small immutable classes; no global state, no I/O, no logging side
  effects beyond an injected callback.
- Inputs and outputs are `model-schema` Pydantic models or Polars DataFrames — never
  loose dicts across a module boundary.
- Every function that can be stochastic takes `seed: int`.
- Signature style:

```python
def fit_glm(
    data: pl.DataFrame,
    spec: GlmSpec,
    *,
    seed: int = 0,
    progress: ProgressCallback | None = None,
) -> GlmFitResult: ...
```

### 5.6 Frontend view inventory (canonical names)

| View | Route | Owning spec |
|---|---|---|
| Dataset list / detail / version | `/data`, `/data/:slug`, `/data/:slug/v/:version` | 01 |
| Validation report | `/data/:slug/v/:version/validation` | 01 |
| Factor workbench (bandings, groupings) | `/factors/:datasetVersionId` | 02 |
| Model list / detail / diagnostics | `/models`, `/models/:slug@:version` | 02 |
| Custom objective library | `/objectives` | 02 |
| Rating DAG designer | `/rating/:slug/v/:version/design` | 03 |
| Rate table editor | `/rating/:slug/v/:version/tables/:tableSlug` | 03 |
| Quote sandbox & trace viewer | `/rating/:slug/v/:version/sandbox` | 03 |
| Dislocation analysis | `/rating/:slug/v/:version/dislocation` | 03 |
| Optimisation studio | `/optimisation/:runId` | 04 |
| Monitoring dashboards | `/monitoring/:environment` | 05 |
| Approvals inbox | `/approvals` | 06 |
| Audit explorer | `/audit` | 06 |
| Jobs | `/jobs` | 07 |
| Admin (users, roles, environments) | `/admin/*` | 07 |

---

## 6. Workflows

The five cross-module journeys, each specified in `docs/workflows/`:

| Workflow | Journey | Primary modules |
|---|---|---|
| `wf-01-dataset-to-model.md` | Raw file → validated Dataset Version → fitted, diagnosed, approved Model | 01, 02, 06 |
| `wf-02-model-to-rating-version.md` | Approved Models → peril structure → rating DAG + rate tables → approved Rating Version | 02, 03, 06 |
| `wf-03-rate-change-impact.md` | Proposed rate change → dislocation + optimisation + GIPP evidence → decision | 03, 04, 06 |
| `wf-04-deploy-and-monitor.md` | Approved Rating Version → deploy to environment → live scoring → drift/AE monitoring → alert | 03, 05, 07 |
| `wf-05-custom-objective-lifecycle.md` | Define custom objective → validate/sandbox → approve → use in model → audit | 02, 06, 07 |

---

## 7. Module map & cross-module dependencies

### 7.1 Module codes (used in requirement IDs)

| Code | Spec | Owns |
|---|---|---|
| `OVR` | 00-overview | Vocabulary, cross-cutting conventions |
| `DATA` | 01-data-management | Datasets, versions, validation, reference data, profiling |
| `MODEL` | 02-modelling | Factors, bandings, groupings, models, custom objectives, diagnostics |
| `RATE` | 03-rating-engine | Rating algorithms, rate tables, rating versions, scoring, dislocation |
| `OPT` | 04-optimisation | Demand models, optimisation runs, GIPP checks |
| `MON` | 05-monitoring | Drift, PSI, A/E, dashboards, alerts |
| `GOV` | 06-governance | RBAC, approvals, audit, generated documentation |
| `PLAT` | 07-platform | Auth, jobs, storage, environments, deployment, observability |

### 7.2 Dependency matrix

Rows *consume from* columns.

| ↓ consumes / provides → | DATA | MODEL | RATE | OPT | MON | GOV | PLAT |
|---|---|---|---|---|---|---|---|
| **DATA** | — | — | — | — | — | approvals, audit | jobs, storage, auth |
| **MODEL** | Dataset Versions, Factors' source columns, profiles | — | — | — | — | approvals, audit | jobs, storage, auth |
| **RATE** | Reference Table Versions | Models, transparency artifacts | — | *(OPT writes in; not a dependency — see `03` §7.1)* | — | approvals, audit | jobs, storage, auth, environments |
| **OPT** | Dataset Versions (portfolio) | Demand Models | Rating Versions, batch scoring | — | — | approvals, audit | jobs, auth |
| **MON** | Reference distributions | Models (expected) | Deployments, scoring traces | Optimisation targets | — | audit | jobs, alerting |
| **GOV** | *(pushed in)* | *(pushed in)* | *(pushed in)* | *(pushed in)* | *(pushed in)* | — | auth, users |
| **PLAT** | — | — | — | — | — | audit sink, permission check (DEP-1a) | — |

**Dependency rules:**

- **DEP-1** — No cycles. The order `PLAT → GOV → DATA → MODEL → RATE → OPT/MON` is the
  build order; a module never imports from a module to its right.
- **DEP-1a** — **Two `GOV` interfaces are cross-cutting and sit outside that order: the
  audit sink and the permission check.** Every module may call them, `PLAT` included —
  platform-level actions such as key rotation and settings changes must be audited like any
  other, and audit writes share the caller's transaction (`06` R2). This is an interface
  dependency, not a data dependency: nothing reads governance tables. `GOV`'s *approval
  workflow* and its *artifact reads* still respect DEP-1 strictly.

  Without this carve-out DEP-1 is simply false, because a cross-cutting audit obligation
  cannot be expressed as a position in a linear chain. Stating it explicitly is what stops
  the rule being quietly ignored the first time it is inconvenient.
- **DEP-2** — Cross-module reads happen through the owning module's public service
  interface (or its `model-schema` contract), never by reaching into another module's
  tables.
- **DEP-3** — `pricing-core` depends on nothing in the backend. `model-schema` depends on
  nothing at all except Pydantic.

---

## 8. Tech dependencies

Cross-cutting stack usage. Module specs list their own; all of it aggregates into
`docs/skills-map.md`.

| Component | Used for (system level) |
|---|---|
| **Python 3.12+ / `uv` workspaces** | Monorepo package management for `packages/*`, `backend`, `pipelines` |
| **FastAPI + Pydantic v2** | The single API surface (FR-OVR-11); Pydantic models are the contract source of truth (FR-OVR-6) |
| **SQLAlchemy 2.x async + Alembic** | Metadata persistence, transactional audit writes (FR-OVR-4), migrations |
| **PostgreSQL 16** | Entities, JSONB artifact bodies, audit log, row-level constraints for state machines |
| **Celery + Redis** | Job execution and queueing (FR-OVR-10); Redis also caches live rating bundles |
| **Polars** | All in-memory dataframe work in `pricing-core` and workers |
| **DuckDB** | Ad-hoc aggregation over parquet dataset versions (profiling, one-ways, dislocation) |
| **Object storage (S3-compatible/MinIO)** | Content-addressed blob store (ID-4) |
| **glum / statsmodels** | GLM fitting and fallback diagnostics |
| **XGBoost / LightGBM / interpret (EBM)** | Gradient boosting with monotone constraints; transparent ML |
| **pandera** | Structural dataset schemas stored with each Dataset Version |
| **GoRules ZEN Engine** | Execution of rating DAGs as JSON decision models |
| **Dagster** | Scheduled ingestion, batch re-rate, monitoring aggregation pipelines |
| **OpenTelemetry** | `trace_id` propagation across API → worker → pricing-core (§5.3) |
| **Vue 3 + Vite + TS + Pinia + Tailwind** | The SPA |
| **ECharts / TanStack Table / Vue Flow** | Diagnostics charts, rate-table grids, DAG designer |
| **openapi-typescript** | Generated API client types (FR-OVR-6) |
| **Ruff / mypy --strict / pytest / hypothesis / Vitest / Playwright** | Quality gates |

---

## 9. Non-functional requirements (system level)

| ID | Requirement |
|---|---|
| **NFR-OVR-1** | Real-time scoring: p99 < 50 ms server-side for a single quote against a live Rating Version, excluding network, at 200 rps sustained per replica. |
| **NFR-OVR-2** | Batch scoring throughput: ≥ 1 M risks/hour per worker for a typical motor rating structure (≈ 200 DAG steps). |
| **NFR-OVR-3** | GLM fitting: 5 M rows × 60 factors converges in < 10 min on a 16-core worker. GBM fitting: same data, 500 trees, < 20 min. |
| **NFR-OVR-4** | Interactive UI: p95 < 300 ms for metadata reads; any operation exceeding 2 s becomes a Job with progress. |
| **NFR-OVR-5** | Audit completeness: 100 % of governed state transitions produce an Audit Event; the audit log is append-only at the database privilege level. |
| **NFR-OVR-6** | Retention: artifacts and audit events retained ≥ 7 years (UK regulatory expectation); scoring traces sampled and retained ≥ 13 months. |
| **NFR-OVR-7** | Recoverability: RPO ≤ 15 min, RTO ≤ 4 h for the pricing metadata database; the blob store is versioned and replicated. |
| **NFR-OVR-8** | Security: all traffic TLS 1.3; secrets from environment/secret manager only; no credentials in artifacts; dependency and container scanning in CI. |
| **NFR-OVR-9** | Portability: the full stack runs locally via `docker compose up` with no cloud dependency, using MinIO for object storage. |
| **NFR-OVR-10** | Accessibility: the SPA meets WCAG 2.2 AA; all charts have an accessible tabular equivalent. |
| **NFR-OVR-11** | Licensing: every runtime dependency must be OSI-approved and compatible with the project licence; copyleft-incompatible or source-available-only dependencies are rejected (see `open-questions.md` OQ-OVR-2 for the licence choice). |

---

## 10. Open questions

Mirrored in `docs/open-questions.md`.

| ID | Question |
|---|---|
| **OQ-OVR-1** | Is the workspace the tenancy boundary, or do we also need per-workspace physical isolation for hosted use? |
| **OQ-OVR-2** | Project licence: Apache-2.0 (permissive, adoption) vs AGPL-3.0 (protects against closed SaaS forks). |
| ~~**OQ-OVR-3**~~ ✔ | ~~Do we support multiple currencies in one workspace in Phase 2, or defer multi-currency to Phase 4? |~~ **Decided 2026-08-14: deferred to Phase 4; one currency per workspace, recorded on every artifact envelope now (FR-OVR-7, §4.3).**
| ~~**OQ-OVR-4**~~ ✔ | ~~Is `pricing-core` published to PyPI as a standalone library from Phase 1, which would constrain its API stability earlier than otherwise needed? |~~ **Decided 2026-08-14: editable install in Phase 1, publish as `0.x` from Phase 2 with a no-stability notice.**
| ~~**OQ-OVR-5**~~ ✔ | ~~Where does the notebook escape hatch live — an embedded JupyterLab in the platform, or a documented client library only? |~~ **Decided 2026-08-14: client library in Phase 1; embedded notebooks revisited in Phase 4 (§1.2).**
