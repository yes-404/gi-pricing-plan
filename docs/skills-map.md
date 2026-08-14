# Skills Map

**Purpose.** The maintainer's next step after Phase 0 is to research the skills each part
of the stack requires. This file is the index for that: *stack component → where it is
used → what to learn → where to learn it.*

**Maintenance rule (CLAUDE.md §8).** Whenever a spec adds or changes a tech dependency,
update this file in the same PR. Every row's "Used in" column must cite at least one spec
section or requirement ID.

**Depth key.** `★` working familiarity · `★★` competent, can debug · `★★★` deep, this is
where the project's hard problems live.

---

## 1. Backend core

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Python 3.12+ / `uv` workspaces | Whole monorepo; `CLAUDE.md` §11 | ★★ | Workspace layout, lockfile & sync semantics, per-package deps, editable installs, `uv run` in CI | [uv docs — workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) |
| FastAPI | 00 §5, all module Interfaces sections | ★★ | Async endpoints, dependency injection for auth/session, `202 Accepted` + job pattern, OpenAPI customisation, streaming responses | [FastAPI docs](https://fastapi.tiangolo.com/), [Advanced OpenAPI](https://fastapi.tiangolo.com/advanced/extending-openapi/) |
| Pydantic v2 | ADR-0002, FR-OVR-6 | ★★★ | Discriminated unions for artifact polymorphism, `model_json_schema()` output shaping, validators vs serialisers, `Decimal` handling, schema versioning & migration | [Pydantic v2 docs](https://docs.pydantic.dev/latest/), [JSON Schema generation](https://docs.pydantic.dev/latest/concepts/json_schema/) |
| SQLAlchemy 2.x (async) | FR-OVR-4, 07-platform | ★★ | 2.0 style `select()`, async sessions & unit of work, JSONB columns, transactional audit writes, optimistic locking with version counters | [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/) |
| Alembic | 07-platform | ★ | Autogenerate limits, data migrations, migrating JSONB artifact `schema_version` | [Alembic docs](https://alembic.sqlalchemy.org/) |
| PostgreSQL 16 | FR-OVR-4, ID-1..ID-5, FR-DATA-29 | ★★ | JSONB indexing (GIN), `timestamptz` and half-open ranges, **exclusion constraints with `daterange` for reference-table effective dating**, append-only tables via privileges/triggers, partitioning the trace table | [PostgreSQL 16 docs](https://www.postgresql.org/docs/16/), [Exclusion constraints](https://www.postgresql.org/docs/16/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION) |
| Celery + Redis | FR-OVR-10, 07-platform | ★★ | Task routing & queues, revocation/cancellation, progress reporting, result backends, idempotency, worker memory limits for large fits | [Celery docs](https://docs.celeryq.dev/) |
| OpenTelemetry | 00 §5.3, NFR-OVR-5 | ★ | Trace propagation API→worker, span attributes for job/artifact ids, OTLP export | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) |

## 2. Data engine

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Polars | ADR-0005; 01, 02 | ★★★ | Lazy frames & query plans, expression API, strict dtypes, `group_by` aggregation idioms, joins at scale, memory profiling, Arrow interop | [Polars user guide](https://docs.pola.rs/) |
| DuckDB | ADR-0005; 01 FR-DATA-27/28, §4.5 `sql` check | ★★ | Querying parquet directly, `read_parquet` globbing, window functions for one-ways, `QUALIFY`, **read-only connections and disabling extension/filesystem access for user-supplied SQL (NFR-DATA-9)**, statement parsing to reject non-`SELECT` | [DuckDB docs](https://duckdb.org/docs/), [Securing DuckDB](https://duckdb.org/docs/operations_manual/securing_duckdb/overview) |
| Apache Parquet / Arrow | ADR-0005, ID-4, 01 §4.2 | ★★ | Schema evolution, row groups & predicate pushdown, dictionary encoding, **`decimal128` logical types for money (FR-OVR-7) and exposure**, content-hashing a multi-part dataset deterministically | [Parquet format](https://parquet.apache.org/docs/), [Arrow Python](https://arrow.apache.org/docs/python/) |
| Object storage (S3 / MinIO) | ID-4, NFR-OVR-9 | ★ | Content-addressed layout, presigned URLs, multipart upload, lifecycle rules | [MinIO docs](https://min.io/docs/minio/linux/index.html) |
| Dagster | `pipelines/` | ★★ | Assets vs ops, partitioned assets by dataset version, schedules & sensors, resource configuration | [Dagster docs](https://docs.dagster.io/) |

## 3. Actuarial / ML

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| glum | 02 FR-MODEL-18..24 | ★★★ | `GeneralizedLinearRegressor` API, Tweedie/Poisson/Gamma families, log link, offsets vs weights (they are not interchangeable), elastic-net CV paths, categorical handling, **extracting the covariance matrix for standard errors (FR-MODEL-21)**, detecting rank deficiency and separation | [glum docs](https://glum.readthedocs.io/), [glum GLM tutorial](https://glum.readthedocs.io/en/latest/tutorials/glm_intro_tutorial/glm_intro.html) |
| statsmodels | 02 FR-MODEL-51 fallback diagnostics | ★ | GLM summary output, type-III deviance tests, residual types (deviance/Pearson/standardised), leverage and Cook's distance, cross-checking glum coefficients | [statsmodels GLM](https://www.statsmodels.org/stable/glm.html) |
| XGBoost | 02 FR-MODEL-25..32, ADR-0003 | ★★★ | Custom objective `(grad, hess)` signature and its exact shape contract, `base_margin` for exposure offsets (FR-MODEL-27), `monotone_constraints` and `interaction_constraints`, `count:poisson`/`reg:gamma`/`reg:tweedie`, JSON model export, `DMatrix` vs `QuantileDMatrix` memory behaviour | [Custom objective tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/custom_metric_obj.html), [Model IO](https://xgboost.readthedocs.io/en/stable/tutorials/saving_model.html), [Monotonic constraints](https://xgboost.readthedocs.io/en/stable/tutorials/monotonic.html) |
| LightGBM | 02 FR-MODEL-25..32 | ★★ | `fobj`/`feval` interface, `init_score` as the exposure offset, monotone constraint methods (`basic`/`intermediate`/`advanced`) and how they differ from XGBoost's, native categorical handling, text model dump | [LightGBM docs](https://lightgbm.readthedocs.io/), [Parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html) |
| interpret (EBM) | 02 FR-MODEL-37 | ★ | `ExplainableBoostingRegressor`, term contributions as an additive structure, exporting shape functions directly as rateable tables | [InterpretML docs](https://interpret.ml/docs/) |
| SHAP | 02 FR-MODEL-35 transparency artifact | ★★ | TreeSHAP for GBMs, interaction values and their cost, exposure-weighted dependence summaries, turning SHAP output into a factor summary an actuary will actually sign | [SHAP docs](https://shap.readthedocs.io/), [TreeSHAP paper](https://arxiv.org/abs/1802.03888) |
| **SymPy** | 02 FR-MODEL-40 objective derivation | ★★★ | Symbolic differentiation, differentiating `Piecewise` (what `where()` compiles to), simplification that keeps expressions reviewable, code generation into our own expression tree rather than `lambdify` | [SymPy docs](https://docs.sympy.org/latest/index.html), [Piecewise](https://docs.sympy.org/latest/modules/functions/elementary.html#piecewise) |
| **Python `ast` / restricted parsing** | 02 §4.6 grammar; 01 FR-DATA-10 | ★★★ | Allow-list node walking, depth/size limits, why `eval`/`compile`/`literal_eval` on user input is not acceptable, position-accurate error reporting, sandbox threat modelling | [ast module](https://docs.python.org/3/library/ast.html), [Green Tree Snakes](https://greentreesnakes.readthedocs.io/) |
| **NumPy (numerics discipline)** | 02 FR-MODEL-48 objective evaluation | ★★ | Vectorised allocation-conscious gradient/hessian evaluation, `np.errstate` around log/exp edges, detecting NaN/inf early, float64 vs float32 in boosting | [NumPy docs](https://numpy.org/doc/stable/) |
| **Credibility theory** | 02 FR-MODEL-14, OQ-MODEL-5 | ★★ | Limited fluctuation (full/partial credibility standards) vs Bühlmann–Straub variance components; what a UK reviewer expects to see in a grouping justification | Klugman, Panjer & Willmot, *Loss Models*; CAS credibility study notes |
| pandera | 01-data-management FR-DATA-16, VR-STR-* | ★★ | Polars-backed schemas, lazy validation to collect all errors in one pass, custom checks, serialising a schema to store with a Dataset Version | [pandera docs](https://pandera.readthedocs.io/), [Polars backend](https://pandera.readthedocs.io/en/stable/polars.html) |
| SciPy (stats) | 01 FR-DATA-26 one-way CIs | ★ | Exact Poisson and Gamma confidence intervals at low claim counts (not normal approximations) | [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html) |
| PSI / KS / stability metrics | 01 VR-DST-*, 05-monitoring | ★★ | PSI binning choices and their sensitivity, exposure-weighted vs count-weighted PSI, KS for continuous columns, thresholds that mean something in a pricing book | Siddiqi, *Credit Risk Scorecards* (PSI); [Evidently drift docs](https://docs.evidentlyai.com/) as a reference implementation to compare against |
| Actuarial GLM practice | 02, 07 (§7 defaults) | ★★★ | Frequency/severity vs Tweedie burning cost, offsets for exposure, base level choice, credibility-weighted grouping, one-way vs multivariate distortion, lift/gains and Gini for pricing | Ohlsson & Johansson, *Non-Life Insurance Pricing with GLMs*; CAS monographs; Institute & Faculty of Actuaries GI pricing material |

## 4. Rating execution

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| GoRules ZEN Engine | ADR-0004, 03-rating-engine | ★★★ | JDM graph format, decision tables, expression language & its limits, custom node/loader extension points, Python bindings & performance, tracing output | [ZEN Engine docs](https://gorules.io/docs/), [zen-engine-py](https://github.com/gorules/zen) |
| Decimal arithmetic | FR-OVR-7 | ★★ | `decimal.Decimal` contexts, rounding modes (half-even for money), integer minor units, avoiding float contamination through JSON | [Python decimal](https://docs.python.org/3/library/decimal.html) |

## 5. Frontend

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Vue 3 Composition API | 00 §5.6 | ★★ | `<script setup lang="ts">`, composables, provide/inject, suspense for async views | [Vue 3 docs](https://vuejs.org/guide/introduction.html) |
| Pinia | frontend state | ★ | Store composition, persisting selected dataset/model context, typed stores | [Pinia docs](https://pinia.vuejs.org/) |
| Vite + TS strict | frontend build | ★ | Strict-mode config, path aliases, env handling, build splitting for heavy chart bundles | [Vite docs](https://vite.dev/) |
| Tailwind | frontend styling | ★ | Design tokens, dark mode, component extraction discipline | [Tailwind docs](https://tailwindcss.com/docs) |
| ECharts / vue-echarts | 02 diagnostics, 05 dashboards | ★★ | Large-dataset rendering, dual-axis A/E charts, custom tooltips, accessible tabular fallback (NFR-OVR-10) | [Apache ECharts](https://echarts.apache.org/en/index.html), [vue-echarts](https://github.com/ecomfe/vue-echarts) |
| TanStack Table | 03 rate table editor | ★★ | Virtualised rows, editable cells, column pinning, diffing edits against a baseline version | [TanStack Table](https://tanstack.com/table/latest) |
| Vue Flow | 03 DAG designer | ★★★ | Custom node/edge components, validation of graph edits, layout algorithms, undo/redo, mapping the canvas to our `RatingAlgorithm` contract | [Vue Flow docs](https://vueflow.dev/) |
| openapi-typescript | FR-OVR-6 | ★ | Generation pipeline, `paths`/`components` typing, keeping generation in CI | [openapi-typescript](https://openapi-ts.dev/) |

## 6. Quality & operations

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| pytest + hypothesis | all Python | ★★ | Property-based testing of actuarial invariants (monotonicity, additivity, decimal exactness), fixtures for artifact round-trips | [Hypothesis docs](https://hypothesis.readthedocs.io/) |
| mypy --strict | `packages/` | ★★ | Strict-mode idioms with Pydantic v2 and Polars, typed protocols for callbacks | [mypy docs](https://mypy.readthedocs.io/) |
| Ruff | all Python | ★ | Rule selection, line length 100, import sorting, import-linter-style layering (ADR-0001) | [Ruff docs](https://docs.astral.sh/ruff/) |
| Vitest / Vue Testing Library / Playwright | frontend | ★ | Component testing with generated API types mocked, E2E for the DAG designer | [Vitest](https://vitest.dev/), [Playwright](https://playwright.dev/) |
| Docker Compose / Helm | `deploy/` | ★ | Local full-stack parity (NFR-OVR-9), worker scaling, MinIO wiring | [Compose docs](https://docs.docker.com/compose/) |

---

## 7. Research priority

Ordered by *risk × unfamiliarity*, not by build order:

1. **Custom objectives end-to-end** — the restricted AST parser, SymPy derivation of
   gradients/hessians, and the certification checks (02 §4.6–4.7), plus XGBoost/LightGBM
   `base_margin`/`init_score` mechanics. The platform's headline differentiator, the
   easiest place to be subtly and expensively wrong, and the only place user input
   reaches the numerical core.
2. **ZEN Engine JDM + decimal semantics** — an external format on the p99-latency path
   (ADR-0004, OQ-RATE-1).
3. **glum GLM API and standard errors** — actuaries will check these numbers against
   Emblem.
4. **Polars lazy execution at 10 M+ rows** — everything downstream inherits its
   performance.
5. **Pydantic v2 discriminated unions + JSON Schema** — the contract layer that all
   generation depends on.
6. **Vue Flow custom nodes** — the highest-effort frontend surface.
