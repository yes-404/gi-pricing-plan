# CLAUDE.md — Open Source General Insurance Pricing Platform

This file gives Claude Code the context, conventions, and roadmap to develop this project
continuously and consistently. Read it fully before making changes.

## 0. CURRENT PROJECT PHASE: DOCUMENTATION-FIRST (read this before anything else)

**The primary objective right now is NOT writing application code.** It is iterating a
complete specification suite in `docs/` until every module's functions, data contracts,
and cross-module workflows are defined in enough detail that implementation can start
without ambiguity. Treat documents as the product of this phase.

When asked to "add" a capability (a model type, a validation feature, a workflow), the
default deliverable is a **spec document update**, not code. Only write code when the
maintainer explicitly asks, or as small throwaway snippets inside specs to illustrate an
interface.

The maintainer's next step after this phase is to use these docs to research the skills
required for each part of the tech stack — so every spec must state clearly *which
technologies it depends on and what they are used for* (see the Tech Dependencies section
required in every spec, §5).

## 1. Project Mission

An open-source general insurance pricing platform for the UK/EU market — an alternative
to WTW Radar/Emblem. Full pricing lifecycle: data preparation → risk modelling (GLM/ML) →
rating algorithm design → deployment/scoring → monitoring → governance.

Primary users: pricing actuaries and analysts. Technical (Python/notebooks) but expect a
polished UI. All design decisions favour: reproducibility, auditability, transparency of
the maths.

## 2. Repository Layout (Monorepo)

```
/
├── docs/                     # ★ PRIMARY WORKSPACE THIS PHASE — see §4
├── frontend/                 # Vue 3 SPA (Vite + TypeScript + Pinia)      [later]
├── backend/                  # FastAPI application                        [later]
├── packages/
│   ├── pricing-core/         # Pure Python actuarial engine — no web/db deps
│   └── model-schema/         # Pydantic + JSON Schema shared contracts
├── pipelines/                # Ingestion, preparation, batch scoring (Dagster)
├── examples/                 # Synthetic + freMTPL2 demo datasets, notebooks
├── deploy/                   # docker-compose.yml, k8s/Helm later
└── .github/workflows/        # CI (path-filtered per component)
```

Standing architecture rules (already decided — do not reopen without an ADR):
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis deps.
- `model-schema` is the single source of truth for shared data shapes; frontend types
  are generated from it. Never define a shared shape anywhere else.
- Model and rating definitions are declarative JSON artifacts, never pickled objects.

## 3. Tech Stack (specs must be written against this stack)

### Backend
- Python 3.12+ with `uv` workspaces; FastAPI + Pydantic v2; SQLAlchemy 2.x (async) +
  Alembic; PostgreSQL 16; Celery + Redis for long-running jobs
- Data engine: Polars (dataframes) + DuckDB (ad-hoc aggregation). No pandas in new code
  except at unavoidable library boundaries.
- GLM fitting: `glum` (primary), `statsmodels` (fallback diagnostics)
- **Gradient boosting: XGBoost (primary GBM) and LightGBM (secondary), both with
  monotonic constraint support.** interpret/EBM for transparent ML.
- **Custom objectives are a first-class capability**: user-defined objective and eval
  functions for XGBoost/LightGBM (gradient + hessian interface), and custom loss
  specifications where the standard families don't fit (e.g. Tweedie variance-power
  tuning, capped/large-loss-adjusted losses, asymmetric pricing losses). Specs must
  define how a custom objective is declared, validated, versioned, and audited — an
  arbitrary-code objective is a governance risk, so the spec must cover sandboxing or
  a restricted expression form.
- Dataset validation: `pandera` schemas + a dedicated validation module (see §6)
- Rating execution: GoRules ZEN Engine (JSON decision graphs) wrapped by pricing-core
- Ruff (line 100), mypy --strict on packages/, pytest + hypothesis

### Frontend
- Vue 3 Composition API (`<script setup lang="ts">` only), Vite, TS strict, Pinia,
  Vue Router, pnpm, Tailwind
- ECharts via vue-echarts (diagnostics), TanStack Table (factor/rate tables),
  Vue Flow (rating DAG designer)
- API client generated from OpenAPI (`openapi-typescript`); never hand-written types
- Vitest + Vue Testing Library; Playwright E2E later

## 4. Documentation Suite (the deliverable of this phase)

```
docs/
├── adr/                        # Architecture decision records (numbered)
├── specs/
│   ├── 00-overview.md          # System context, module map, glossary
│   ├── 01-data-management.md   # Ingestion, datasets, versioning, VALIDATION
│   ├── 02-modelling.md         # GLM, XGBoost/LightGBM, custom objectives,
│   │                           #   factors/bandings/groupings, diagnostics
│   ├── 03-rating-engine.md     # Rating DAG, rate tables, scoring APIs
│   ├── 04-optimisation.md      # Demand models, optimisation, GIPP checks
│   ├── 05-monitoring.md        # Drift, PSI, A/E monitoring, dashboards
│   ├── 06-governance.md        # RBAC, approvals, audit, model documentation
│   └── 07-platform.md          # Auth, jobs, deployment, environments
├── workflows/                  # ★ Cross-module, end-to-end user journeys
│   ├── wf-01-dataset-to-model.md
│   ├── wf-02-model-to-rating-version.md
│   ├── wf-03-rate-change-impact.md
│   ├── wf-04-deploy-and-monitor.md
│   └── wf-05-custom-objective-lifecycle.md
├── contracts/                  # Draft API + schema definitions (OpenAPI stubs,
│                               #   JSON Schema for model/rating artifacts)
├── skills-map.md               # Tech stack → skills/knowledge needed (see §8)
└── open-questions.md           # Unresolved design questions, owner, status
```

## 5. Spec Document Standard (every spec must contain these sections)

1. **Purpose & scope** — what the module does and explicitly does not do
2. **Concepts & glossary** — domain terms (must match §7 vocabulary)
3. **Functional requirements** — numbered `FR-<module>-<n>` for traceability
4. **Data contracts** — entities, fields, types, invariants; reference or define the
   JSON Schema in `docs/contracts/`
5. **Interfaces** — API endpoints (method, path, request/response shape), pricing-core
   function signatures, frontend views touched
6. **Workflows** — sequence of steps with actors (user / frontend / backend / worker /
   pricing-core); link to the relevant `docs/workflows/` journey
7. **Cross-module dependencies** — what this module consumes from and provides to others
8. **Tech dependencies** — which stack components it uses and for what (feeds
   `skills-map.md`)
9. **Non-functional requirements** — performance, audit, security where relevant
10. **Open questions** — mirrored into `docs/open-questions.md`

Requirement IDs are permanent: never renumber, only append or mark superseded.

## 6. Dataset Validation (spec priorities for 01-data-management.md)

Validation is a gate between ingestion and modelling: a dataset version must reach status
`validated` before any model can be fitted on it. The spec must define these layers:

- **Structural**: column presence, dtypes, encodings, key uniqueness (policy id ×
  exposure period), date parsing — expressed as pandera schemas stored with the dataset.
- **Referential**: values resolve against reference tables (postcodes, vehicle groups,
  occupation codes) with effective-date awareness.
- **Actuarial sanity**: exposure > 0 and reasonable (period-consistent), claim dates
  inside exposure periods, no negative claim counts, severity outliers flagged against
  configurable thresholds, claim–policy linkage completeness.
- **Distributional / stability**: one-way distributions and PSI vs a reference dataset
  version, to catch mix shifts and broken feeds before they poison a model.
- **Outcome model**: every run produces a persisted, versioned validation report
  (pass / warn / fail per rule) attached to the dataset version and visible in the UI;
  fails block modelling, warns require an actuary's explicit acknowledgement (audited).
- **Extensibility**: users can define custom validation rules declaratively; the spec
  must define that rule format and its governance (same review/audit trail as models).

## 7. Domain Model (shared vocabulary — use these names in every doc)

- **Dataset**: immutable versioned snapshot of policy/claims/exposure data; carries its
  validation report and status (`draft → validated → archived`).
- **Factor / Level / Banding / Grouping**: rating variables and their transformations;
  groupings are first-class auditable operations.
- **Model**: fitted statistical model for one peril/response. Types: `glm`, `xgboost`,
  `lightgbm`, `ebm`. Stores family/objective (including custom objective reference),
  link, offset, weights, factors, coefficients or booster artifact + GLM approximation,
  diagnostics, dataset reference, parent model (lineage).
- **Custom Objective**: named, versioned definition of a non-standard loss (declarative
  parameters or reviewed code), reusable across models, with its own approval status.
- **Peril structure → Risk Premium**: frequency × severity (or burning cost) per peril.
- **Rating Algorithm / Rate Table / Rating Version**: DAG of calculation steps; rating
  versions are immutable deployable bundles moving `draft → review → approved → live →
  retired`.
- **Scoring**: real-time (single quote, target p99 < 50 ms) and batch (portfolio
  re-rate, dislocation analysis).

Actuarial correctness defaults (specs must not contradict these):
- Frequency: Poisson (or NB), log link, exposure offset. Severity: Gamma, log link,
  claim-count weights. Burning cost: Tweedie (1 < p < 2), log link, exposure weights.
- XGBoost/LightGBM insurance use: `count:poisson` / `reg:gamma` / `reg:tweedie` (or
  custom objective) with exposure handled via `base_margin` (log-exposure offset);
  monotonic constraints where actuarially required; always accompanied by a
  transparency artifact (GLM approximation or SHAP-based factor summary).
- Standard errors / uncertainty surfaced with every estimate; money is integer
  pence/cents or Decimal in the rating path, never float.

## 8. skills-map.md (supports the maintainer's next step)

Maintain `docs/skills-map.md` as a living table: **stack component → where it is used
(spec/FR references) → skills to research → learning resources**. Whenever a spec adds
or changes a tech dependency, update this file in the same PR. Example rows: glum (GLM
API, formula interface, regularisation), XGBoost (custom objective gradient/hessian
interface, base_margin, monotone constraints), ZEN Engine (JDM graph format, Python
bindings), Vue Flow (custom nodes/edges, validation), pandera (schema definition,
lazy validation reports).

## 9. Roadmap

- **Phase 0 — Specification (CURRENT)**: iterate `docs/` until every module spec meets
  the §5 standard, all five workflow docs are complete, contracts drafted, and
  open-questions is empty or explicitly deferred. Exit criteria: an engineer could start
  Phase 1 from docs alone.
- **Phase 1 — Modelling Workbench**: dataset upload + validation + profiling, GLM and
  XGBoost fitting (incl. custom objectives), factor management, diagnostics, model
  versioning. Demo on freMTPL2.
- **Phase 2 — Rating Engine**: DAG designer, rate tables, reference data, real-time +
  batch scoring, dislocation.
- **Phase 3 — Governance**: RBAC, approvals, audit UI, model documentation generation.
- **Phase 4 — Optimisation & Monitoring**: demand models, constrained optimisation,
  drift monitoring, GIPP consistency.

## 10. How You (Claude) Work in This Phase

- Deliverable of almost every task = updated/new documents in `docs/`. Ask before
  writing application code.
- Before editing any doc, read `00-overview.md`, the target spec, and any workflow docs
  that reference it. After editing, check cross-references in both directions and update
  `skills-map.md` and `open-questions.md` in the same PR.
- Keep terminology exactly consistent with §7; if a new term is needed, add it to the
  glossary in `00-overview.md` first.
- Prefer precise, implementation-ready language: named entities, typed fields, numbered
  requirements, explicit status enums, sequence-of-steps workflows. Avoid vague phrases
  ("the system should handle…") — say who does what, with what data, and what changes.
- When a design choice is genuinely open, do not silently pick one: record options,
  trade-offs, and a recommendation in `open-questions.md` (or an ADR if it must be
  decided now).
- Small illustrative snippets (an XGBoost custom objective signature, a pandera schema,
  a JSON contract example) inside specs are encouraged; full implementations are not.
- Docs PRs follow the same conventions: Conventional Commits (`docs:` prefix),
  short-lived branches, squash-merge, branch auto-delete.

## 11. Commands Reference (for when coding phases begin)

```bash
uv sync && pnpm install --dir frontend      # deps
docker compose up                            # full local stack
uv run ruff check . && uv run mypy packages/ && uv run pytest
pnpm --dir frontend lint && pnpm --dir frontend test && pnpm --dir frontend type-check
pnpm --dir frontend generate:api             # regenerate TS types from OpenAPI
uv run alembic upgrade head
```
