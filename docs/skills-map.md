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
| Alembic | 07 FR-PLAT-35 | ★★ | Autogenerate limits, data migrations, migrating JSONB artifact `schema_version`, **forward-compatible migrations so a rolling deploy runs the previous app version against the new schema** | [Alembic docs](https://alembic.sqlalchemy.org/) |
| OIDC / OAuth2 for SPAs | 07 FR-PLAT-1..4 | ★★ | Authorisation code + PKCE, refresh handling, why tokens stay out of `localStorage`, claim-to-role mapping, running Keycloak locally | [OAuth 2.0 for browser apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps), [Keycloak docs](https://www.keycloak.org/documentation) |
| Server-sent events (SSE) | 07 FR-PLAT-8, §5.1 | ★ | Streaming job progress from FastAPI, reconnection semantics, proxy buffering pitfalls | [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) |
| S3 presigned uploads | 07 FR-PLAT-21 | ★ | Multipart presigned URLs, expiry and scope, keeping large dataset bytes out of the API process | [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html) |
| PostgreSQL 16 | FR-OVR-4, ID-1..ID-5, FR-DATA-29 | ★★ | JSONB indexing (GIN), `timestamptz` and half-open ranges, **exclusion constraints with `daterange` for reference-table effective dating**, append-only tables via privileges/triggers, partitioning the trace table | [PostgreSQL 16 docs](https://www.postgresql.org/docs/16/), [Exclusion constraints](https://www.postgresql.org/docs/16/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION) |
| Celery + Redis | FR-OVR-10, 07 FR-PLAT-7..16 | ★★ | Queue routing by job kind, **revocation and cooperative cancellation**, progress reporting, result backends, idempotency keys, worker memory limits for large fits, and the enqueue-vs-transaction failure mode driving OQ-PLAT-1 | [Celery docs](https://docs.celeryq.dev/), [procrastinate](https://procrastinate.readthedocs.io/) (the Postgres-queue alternative) |
| OpenTelemetry | 00 §5.3, NFR-OVR-5 | ★ | Trace propagation API→worker, span attributes for job/artifact ids, OTLP export | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) |

## 2. Data engine

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Polars | ADR-0005; 01, 02 | ★★★ | Lazy frames & query plans, expression API, strict dtypes, `group_by` aggregation idioms, joins at scale, memory profiling, Arrow interop | [Polars user guide](https://docs.pola.rs/) |
| DuckDB | ADR-0005; 01 FR-DATA-27/28, §4.5 `sql` check | ★★ | Querying parquet directly, `read_parquet` globbing, window functions for one-ways, `QUALIFY`, **read-only connections and disabling extension/filesystem access for user-supplied SQL (NFR-DATA-9)**, statement parsing to reject non-`SELECT` | [DuckDB docs](https://duckdb.org/docs/), [Securing DuckDB](https://duckdb.org/docs/operations_manual/securing_duckdb/overview) |
| Apache Parquet / Arrow | ADR-0005, ID-4, 01 §4.2 | ★★ | Schema evolution, row groups & predicate pushdown, dictionary encoding, **`decimal128` logical types for money (FR-OVR-7) and exposure**, content-hashing a multi-part dataset deterministically | [Parquet format](https://parquet.apache.org/docs/), [Arrow Python](https://arrow.apache.org/docs/python/) |
| Object storage (S3 / MinIO) | ID-4, NFR-OVR-9 | ★ | Content-addressed layout, presigned URLs, multipart upload, lifecycle rules | [MinIO docs](https://min.io/docs/minio/linux/index.html) |
| Dagster | `pipelines/`; 05 FR-MON-2 | ★★ | Assets vs ops, partitioned assets by dataset version and by monitoring period, **backfilling a Monitor created after the fact (NFR-MON-8)**, schedules & sensors (deployment-triggered monitor creation), resource configuration | [Dagster docs](https://docs.dagster.io/), [Partitions & backfills](https://docs.dagster.io/guides/build/partitions-and-backfills) |

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

## 3b. Optimisation & monitoring

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| SciPy `optimize` | 04 FR-OPT-8..17 | ★★★ | Formulating segment adjustments as a bounded vector problem, SLSQP vs trust-constr, supplying Jacobians, **diagnosing infeasible constraint sets and naming the culprits (NFR-OPT-4)**, reading termination reasons honestly | [scipy.optimize](https://docs.scipy.org/doc/scipy/reference/optimize.html), [Constrained minimization](https://docs.scipy.org/doc/scipy/tutorial/optimize.html#constrained-minimization-of-multivariate-scalar-functions) |
| cvxpy (contingency) | 04 OQ-OPT-1 | ★ | Convex reformulation of the pricing objective, conic solvers, dual values as shadow prices | [cvxpy docs](https://www.cvxpy.org/) |
| Price elasticity estimation | 04 FR-OPT-1..7, OQ-OPT-4 | ★★★ | Demand modelling in GI, price terms (absolute vs relative to technical vs market position), **endogeneity and why naive elasticity is biased**, identifiability from observational price variation, extrapolation limits | Ohlsson & Johansson (demand chapter); CAS/IFoA pricing-optimisation papers; econometrics texts on IV estimation |
| FCA PS21/5 (GIPP) | 04 FR-OPT-18..22 | ★★ | What the rules actually require, equivalent-new-business-price definition and channel treatment, price-walking, what evidence a supervisor expects to see retained | [FCA PS21/5](https://www.fca.org.uk/publications/policy-statements/ps21-5-general-insurance-pricing-practices-market-study), FCA finalised guidance on fair value |
| Claims development / maturity | 05 R4, FR-MON-12; 01 VR-ACT-14 | ★★ | Development factors and patterns, earned vs written basis, why an immature A/E is misleading, applying a supplied pattern without doing reserving | IFoA GI reserving material (for the pattern concepts only — reserving itself is out of scope) |
| Alerting design | 05 FR-MON-28..32 | ★ | Alert lifecycle (raise/ack/resolve/suppress), deduplication keys, consecutive-breach logic, escalation vs repetition, detecting mis-thresholded monitors | [Google SRE — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) |

## 4. Rating execution

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| GoRules ZEN Engine | ADR-0004, 03 FR-RATE-1..13 | ★★★ | JDM graph format, decision tables, expression language and its numeric semantics (**OQ-RATE-1**), custom node / loader extension points for rate-table lookup and `model_call`, Python binding overhead at 200 rps, native trace output | [ZEN Engine docs](https://gorules.io/docs/), [zen-engine-py](https://github.com/gorules/zen) |
| Decimal arithmetic | FR-OVR-7, 03 FR-RATE-29/32 | ★★ | `decimal.Decimal` contexts, `ROUND_HALF_EVEN` for money, integer minor units and their exact float64 range, avoiding float contamination through JSON serialisation, proving a premium ladder reconciles to the penny | [Python decimal](https://docs.python.org/3/library/decimal.html), [What Every Computer Scientist Should Know About Floating-Point](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) |
| **Redis (cache semantics)** | 03 FR-RATE-51, NFR-RATE-6 | ★★ | Cache warming before an atomic bundle switchover, content-hash keying, memory sizing for 500 MB bundles, eviction policy that must never evict the live bundle | [Redis docs](https://redis.io/docs/latest/) |
| **Low-latency Python serving** | 03 NFR-RATE-1 | ★★★ | Where a 50 ms p99 budget actually goes: Pydantic validation cost on the hot path, single-row GBM inference, thread pinning and BLAS contention, async vs sync endpoints for CPU-bound work, GIL behaviour under 200 rps | [FastAPI concurrency](https://fastapi.tiangolo.com/async/), [XGBoost inference notes](https://xgboost.readthedocs.io/en/stable/prediction.html) |

## 5. Frontend

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Vue 3 Composition API | 00 §5.6 | ★★ | `<script setup lang="ts">`, composables, provide/inject, suspense for async views | [Vue 3 docs](https://vuejs.org/guide/introduction.html) |
| Pinia | frontend state | ★ | Store composition, persisting selected dataset/model context, typed stores | [Pinia docs](https://pinia.vuejs.org/) |
| Vite + TS strict | frontend build | ★ | Strict-mode config, path aliases, env handling, build splitting for heavy chart bundles | [Vite docs](https://vite.dev/) |
| Tailwind | frontend styling | ★ | Design tokens, dark mode, component extraction discipline | [Tailwind docs](https://tailwindcss.com/docs) |
| ECharts / vue-echarts | 02 diagnostics, 05 dashboards | ★★ | Large-dataset rendering, dual-axis A/E charts, custom tooltips, accessible tabular fallback (NFR-OVR-10) | [Apache ECharts](https://echarts.apache.org/en/index.html), [vue-echarts](https://github.com/ecomfe/vue-echarts) |
| TanStack Table | 03 rate table editor | ★★ | Virtualised rows, editable cells, column pinning, diffing edits against a baseline version | [TanStack Table](https://tanstack.com/table/latest) |
| Vue Flow | 03 §5.3 DAG designer | ★★★ | Custom node components per step type, showing validation errors *on the node*, edge derivation from produces/consumes names rather than hand-drawn arrows, auto-layout, undo/redo, structural diff overlay | [Vue Flow docs](https://vueflow.dev/), [Custom nodes](https://vueflow.dev/guide/node.html) |
| openapi-typescript | FR-OVR-6 | ★ | Generation pipeline, `paths`/`components` typing, keeping generation in CI | [openapi-typescript](https://openapi-ts.dev/) |

## 5b. Governance & security

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Append-only tables in PostgreSQL | 06 FR-GOV-22, NFR-OVR-5 | ★★ | Revoking `UPDATE`/`DELETE` from the application role, `BEFORE UPDATE` triggers as a second line, partitioning an audit table by month while keeping it append-only | [PostgreSQL privileges](https://www.postgresql.org/docs/16/ddl-priv.html), [Row-level triggers](https://www.postgresql.org/docs/16/plpgsql-trigger.html) |
| Hash-chained audit logs | 06 FR-GOV-24, OQ-GOV-1 | ★★ | Canonical JSON serialisation so hashes are stable, chain verification cost over 100 M events, what tamper-*evidence* does and does not prove, external anchoring options | [RFC 8785 JSON Canonicalization](https://datatracker.ietf.org/doc/html/rfc8785), [Certificate Transparency](https://certificate.transparency.dev/) as a design reference |
| Separation-of-duties enforcement | 06 R1, NFR-GOV-8 | ★★ | Enforcing in the service layer rather than the UI, negative testing (proving a submitter *cannot* approve), scoped permission checks as a FastAPI dependency | [OWASP ASVS — access control](https://owasp.org/www-project-application-security-verification-standard/) |
| Deterministic document generation | 06 FR-GOV-29/30, NFR-GOV-5 | ★ | HTML→PDF with embedded fonts, byte-reproducible output, rendering charts server-side from the same artifacts the UI uses, point-in-time regeneration | [WeasyPrint](https://weasyprint.org/), [Typst](https://typst.app/docs/) |

## 6. Quality & operations

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| pytest + hypothesis | all Python; 03 FR-RATE-44 | ★★ | Property-based testing of actuarial invariants (monotonicity, additivity, decimal exactness), **building strategies from a declarative input contract**, shrinking counterexamples into something an actuary can read, fixtures for artifact round-trips | [Hypothesis docs](https://hypothesis.readthedocs.io/), [Composite strategies](https://hypothesis.readthedocs.io/en/latest/data.html#composite-strategies) |
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
7. **Low-latency Python serving** — the 50 ms p99 budget (NFR-RATE-1) is the one NFR
   that cannot be fixed later by adding hardware alone.
