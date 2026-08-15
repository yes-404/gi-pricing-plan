# Skills Map

**Purpose.** The maintainer's next step after Phase 0 is to research the skills this
project requires. This file is the index for that, across **two axes**:

| Axis | Sections | Question it answers |
|---|---|---|
| **Build** — stack component → skills | §1–§6 | "What must I know to write this code?" |
| **Run** — practice → skills | §8–§9 | "What must I know to keep the project on track, and to prove it was done properly?" |

The second axis exists because this platform's hard problems are not all technical. It is
a governed system in a regulated domain, specified across 417 permanent requirement IDs — and the ways a project like this fails are as often about traceability,
phase discipline, and evidence as about Polars or XGBoost.

**Maintenance rules.**
- *(CLAUDE.md §10)* Whenever a spec adds or changes a tech dependency, update §1–§6 in the
  same PR. Every row's "Used in" column must cite at least one spec section or requirement
  ID.
- Whenever a working practice changes — a new gate, a new audit, a new standard the output
  must satisfy — update §8–§9 in the same PR, citing the artifact that changed.

**Verified rows.** Entries marked **✔** were checked against a real library version during
Track A research on 2026-08-14 ([`research/track-a-findings.md`](research/track-a-findings.md)),
not inferred from documentation. Unmarked rows remain assumptions.

**Depth key.** `★` working familiarity · `★★` competent, can debug · `★★★` deep, this is
where the project's hard problems live.

---

## 1. Backend core

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Python 3.12+ / `uv` workspaces | Whole monorepo; `CLAUDE.md` §11 | ★★ | Workspace layout, lockfile & sync semantics, per-package deps, editable installs, `uv run` in CI | [uv docs — workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) |
| FastAPI | 00 §5, all module Interfaces sections | ★★ | Async endpoints, dependency injection for auth/session, `202 Accepted` + job pattern, OpenAPI customisation, streaming responses | [FastAPI docs](https://fastapi.tiangolo.com/), [Advanced OpenAPI](https://fastapi.tiangolo.com/advanced/extending-openapi/) |
| Pydantic v2 ✔ | ADR-0002, FR-OVR-6 | ★★★ | **Verified on 2.13.4:** discriminated unions emit `oneOf` + `discriminator` (not the `if`/`then` shape in the hand-drafted contracts), a two-value `Literal` maps both tags to one branch, and `Decimal` renders as a permissive `anyOf: [number, string]` that **must be constrained to string** or FR-OVR-7 is satisfiable by a lossy payload. | Discriminated unions for artifact polymorphism, `model_json_schema()` output shaping, validators vs serialisers, `Decimal` handling, schema versioning & migration | [Pydantic v2 docs](https://docs.pydantic.dev/latest/), [JSON Schema generation](https://docs.pydantic.dev/latest/concepts/json_schema/) |
| SQLAlchemy 2.x (async) | FR-OVR-4, 07-platform | ★★ | 2.0 style `select()`, async sessions & unit of work, JSONB columns, transactional audit writes, optimistic locking with version counters | [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/) |
| Alembic | 07 FR-PLAT-35 | ★★ | Autogenerate limits, data migrations, migrating JSONB artifact `schema_version`, **forward-compatible migrations so a rolling deploy runs the previous app version against the new schema** | [Alembic docs](https://alembic.sqlalchemy.org/) |
| OIDC / OAuth2 for SPAs | 07 FR-PLAT-1..4, **FR-PLAT-55** | ★★ | Authorisation code + PKCE (**decided** OQ-PLAT-6, 2026-08-15; W6b implements it), refresh handling, why tokens stay out of `localStorage`, claim-to-role mapping, running Keycloak locally. **Library choice is W6b's** — `oidc-client-ts` is the default candidate, and hand-rolling PKCE is defensible only if silent renewal comes with it. Until W6b ships, only the frontend dev proxy reaches the API from a browser | [OAuth 2.0 for browser apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps), [Keycloak docs](https://www.keycloak.org/documentation) |
| Server-sent events (SSE) | 07 FR-PLAT-8, §5.1 | ★ | Streaming job progress from FastAPI, reconnection semantics, proxy buffering pitfalls | [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) |
| S3 presigned uploads | 07 FR-PLAT-21 | ★ | Multipart presigned URLs, expiry and scope, keeping large dataset bytes out of the API process | [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html) |
| PostgreSQL 16 | FR-OVR-4, ID-1..ID-5, FR-DATA-29 | ★★ | JSONB indexing (GIN), `timestamptz` and half-open ranges, **exclusion constraints with `daterange` for reference-table effective dating**, append-only tables via privileges/triggers, partitioning the trace table | [PostgreSQL 16 docs](https://www.postgresql.org/docs/16/), [Exclusion constraints](https://www.postgresql.org/docs/16/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION) |
| Celery + Redis | FR-OVR-10, 07 FR-PLAT-7..16 | ★★ | Queue routing by job kind, **revocation and cooperative cancellation**, progress reporting, result backends, idempotency keys, worker memory limits for large fits, and the enqueue-vs-transaction failure mode driving OQ-PLAT-1 | [Celery docs](https://docs.celeryq.dev/), [procrastinate](https://procrastinate.readthedocs.io/) (the Postgres-queue alternative) |
| OpenTelemetry | 00 §5.3, NFR-OVR-5 | ★ | Trace propagation API→worker, span attributes for job/artifact ids, OTLP export | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) |
| prometheus-client | 07 §5.1, FR-PLAT-40, FR-PLAT-52 | ★ | Label cardinality — a resolved path as a label is one time series per entity, and the failure is silent; a per-app `CollectorRegistry` rather than the process-global default; histogram buckets chosen around the budgets actually being watched | [prometheus-client](https://prometheus.github.io/client_python/); [metric naming](https://prometheus.io/docs/practices/naming/) |

## 2. Data engine

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Polars ✔ | ADR-0005; 01, 02 | ★★★ | Lazy frames & query plans, expression API, strict dtypes, joins at scale, memory profiling, Arrow interop. **Caveat found:** the new streaming engine has an *open* group-by memory regression ([#25607](https://github.com/pola-rs/polars/issues/25607)) — which is precisely why ADR-0005 routes aggregation to DuckDB. Treat a new heavy `group_by` in Polars as requiring justification | [Polars user guide](https://docs.pola.rs/), [Streaming engine](https://deepwiki.com/pola-rs/polars/5.2-streaming-engine) |
| DuckDB | ADR-0005; 01 FR-DATA-27/28, §4.5 `sql` check | ★★ | Querying parquet directly, `read_parquet` globbing, window functions for one-ways, `QUALIFY`, **read-only connections and disabling extension/filesystem access for user-supplied SQL (NFR-DATA-9)**, statement parsing to reject non-`SELECT` | [DuckDB docs](https://duckdb.org/docs/), [Securing DuckDB](https://duckdb.org/docs/operations_manual/securing_duckdb/overview) |
| Apache Parquet / Arrow | ADR-0005, ID-4, 01 §4.2 | ★★ | Schema evolution, row groups & predicate pushdown, dictionary encoding, **`decimal128` logical types for money (FR-OVR-7) and exposure**, content-hashing a multi-part dataset deterministically | [Parquet format](https://parquet.apache.org/docs/), [Arrow Python](https://arrow.apache.org/docs/python/) |
| Object storage (S3 / MinIO) | ID-4, NFR-OVR-9 | ★ | Content-addressed layout, presigned URLs, multipart upload, lifecycle rules | [MinIO docs](https://min.io/docs/minio/linux/index.html) |
| Dagster | `pipelines/`; 05 FR-MON-2 | ★★ | Assets vs ops, partitioned assets by dataset version and by monitoring period, **backfilling a Monitor created after the fact (NFR-MON-8)**, schedules & sensors (deployment-triggered monitor creation), resource configuration | [Dagster docs](https://docs.dagster.io/), [Partitions & backfills](https://docs.dagster.io/guides/build/partitions-and-backfills) |

## 3. Actuarial / ML

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| glum ✔ | 02 FR-MODEL-18..24 | ★★★ | **Verified:** `std_errors()` and `covariance_matrix()` (non-robust / robust HC-1 / clustered) plus a coefficient table with CIs and p-values exist and satisfy FR-MODEL-21 directly. | `GeneralizedLinearRegressor` API, Tweedie/Poisson/Gamma families, log link, offsets vs weights (they are not interchangeable), elastic-net CV paths, categorical handling, **extracting the covariance matrix for standard errors (FR-MODEL-21)**, detecting rank deficiency and separation | [glum docs](https://glum.readthedocs.io/), [glum GLM tutorial](https://glum.readthedocs.io/en/latest/tutorials/glm_intro_tutorial/glm_intro.html) |
| statsmodels | 02 FR-MODEL-51 fallback diagnostics | ★ | GLM summary output, type-III deviance tests, residual types (deviance/Pearson/standardised), leverage and Cook's distance, cross-checking glum coefficients | [statsmodels GLM](https://www.statsmodels.org/stable/glm.html) |
| XGBoost ✔ | 02 FR-MODEL-25..32, ADR-0003 | ★★★ | **Verified on 3.4.0:** `predt` in a custom objective **does** include `base_margin`, and `base_margin` *replaces* `base_score` rather than adding to it — so omitting it at predict time silently substitutes `base_score` and returns a wrong number with no error (FR-MODEL-71). | Custom objective `(grad, hess)` signature and its exact shape contract, `base_margin` for exposure offsets (FR-MODEL-27), `monotone_constraints` and `interaction_constraints`, `count:poisson`/`reg:gamma`/`reg:tweedie`, JSON model export, `DMatrix` vs `QuantileDMatrix` memory behaviour | [Custom objective tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/custom_metric_obj.html), [Model IO](https://xgboost.readthedocs.io/en/stable/tutorials/saving_model.html), [Monotonic constraints](https://xgboost.readthedocs.io/en/stable/tutorials/monotonic.html) |
| LightGBM ✔ | 02 FR-MODEL-25..32, 72 | ★★ | **Verified on 4.7.0 (spike S3):** `init_score` *is* included in the raw score passed to a custom objective, like XGBoost's `base_margin` — but **`Booster.predict()` has no offset parameter at all**, so the caller must add `init_score` back manually. A scoring path ported from XGBoost silently omits it. Also: no implicit intercept under a custom objective (iteration 0 is `0.0`, not XGBoost's `base_score`). | `fobj`/`feval` interface, `init_score` as the exposure offset, monotone constraint methods (`basic`/`intermediate`/`advanced`) and how they differ from XGBoost's, native categorical handling, text model dump | [LightGBM docs](https://lightgbm.readthedocs.io/), [Parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html) |
| interpret (EBM) | 02 FR-MODEL-37 | ★ | `ExplainableBoostingRegressor`, term contributions as an additive structure, exporting shape functions directly as rateable tables | [InterpretML docs](https://interpret.ml/docs/) |
| SHAP | 02 FR-MODEL-35 transparency artifact | ★★ | TreeSHAP for GBMs, interaction values and their cost, exposure-weighted dependence summaries, turning SHAP output into a factor summary an actuary will actually sign | [SHAP docs](https://shap.readthedocs.io/), [TreeSHAP paper](https://arxiv.org/abs/1802.03888) |
| **SymPy** ✔ | 02 FR-MODEL-40 objective derivation | ★★★ | **Verified on 1.14.0:** `diff` handles `Piecewise` twice over and lifts the branch *outward*, so the canonical derived form differs from a hand-written one — reviewers must see the canonical text. The real difficulty is downstream: a piecewise loss has a **kink**, and finite-difference validation is invalid across it at any step size (FR-MODEL-68..70). Learn `Piecewise` semantics, `simplify` behaviour on branches, and Richardson extrapolation | [SymPy docs](https://docs.sympy.org/latest/index.html), [Piecewise](https://docs.sympy.org/latest/modules/functions/elementary.html#piecewise) |
| **Python `ast` / restricted parsing** | 02 §4.6 grammar; 01 FR-DATA-10 | ★★★ | Allow-list node walking, depth/size limits, why `eval`/`compile`/`literal_eval` on user input is not acceptable, position-accurate error reporting, sandbox threat modelling | [ast module](https://docs.python.org/3/library/ast.html), [Green Tree Snakes](https://greentreesnakes.readthedocs.io/) |
| **NumPy (numerics discipline)** | 02 FR-MODEL-48 objective evaluation | ★★ | Vectorised allocation-conscious gradient/hessian evaluation, `np.errstate` around log/exp edges, detecting NaN/inf early, float64 vs float32 in boosting | [NumPy docs](https://numpy.org/doc/stable/) |
| **Credibility theory** | 02 FR-MODEL-14, OQ-MODEL-5 | ★★ | Limited fluctuation (full/partial credibility standards) vs Bühlmann–Straub variance components; what a UK reviewer expects to see in a grouping justification | Klugman, Panjer & Willmot, *Loss Models*; CAS credibility study notes |
| ~~pandera~~ | 01 §4.4 (amended 2026-08-15) | — | **Not adopted.** The structural layer is implemented directly over Polars in `pricing_core.data.validate`; the version stores its schema as a `DatasetTableSchema`, so pandera would restate a shape `model-schema` already owns. It is a dependency of nothing in this repository — the row previously read ★★ **Verified**, which was true of the library and false of this codebase. NFR-DATA-2's structural budget is met without it. | — | — |
| SciPy (stats) | 01 FR-DATA-26 one-way CIs | ★ | Exact Poisson and Gamma confidence intervals at low claim counts (not normal approximations) | [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html) |
| PSI / KS / stability metrics | 01 VR-DST-*, 05-monitoring | ★★ | PSI binning choices and their sensitivity, exposure-weighted vs count-weighted PSI, KS for continuous columns, thresholds that mean something in a pricing book | Siddiqi, *Credit Risk Scorecards* (PSI); [Evidently drift docs](https://docs.evidentlyai.com/) as a reference implementation to compare against |
| Actuarial GLM practice | 02, 07 (§7 defaults) | ★★★ | Frequency/severity vs Tweedie burning cost, offsets for exposure, base level choice, credibility-weighted grouping, one-way vs multivariate distortion, lift/gains and Gini for pricing | Ohlsson & Johansson, *Non-Life Insurance Pricing with GLMs*; CAS monographs; Institute & Faculty of Actuaries GI pricing material |

## 3b. Optimisation & monitoring

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| SciPy `optimize` | 04 FR-OPT-8..17 | ★★★ | Formulating segment adjustments as a bounded vector problem, SLSQP vs trust-constr, supplying Jacobians, **diagnosing infeasible constraint sets and naming the culprits (NFR-OPT-4)**, reading termination reasons honestly | [scipy.optimize](https://docs.scipy.org/doc/scipy/reference/optimize.html), [Constrained minimization](https://docs.scipy.org/doc/scipy/tutorial/optimize.html#constrained-minimization-of-multivariate-scalar-functions) |
| cvxpy (contingency) | 04 OQ-OPT-1 | ★ | Convex reformulation of the pricing objective, conic solvers, dual values as shadow prices | [cvxpy docs](https://www.cvxpy.org/) |
| Price elasticity estimation | 04 FR-OPT-1..7, OQ-OPT-4 | ★★★ | Demand modelling in GI, price terms (absolute vs relative to technical vs market position), **endogeneity and why naive elasticity is biased**, identifiability from observational price variation, extrapolation limits | Ohlsson & Johansson (demand chapter); CAS/IFoA pricing-optimisation papers; econometrics texts on IV estimation |
| **ICOBS 6B** (GIPP rules) | 04 FR-OPT-18..30 | ★★ | **The binding rule text — cite this, not PS21/5, which is the policy statement announcing it.** ENBP definition and the first-purchase channel assumption (6B.2.5R), price-walking, scope limit to home and motor, and what evidence a supervisor expects retained. Full treatment in §9.2 | [ICOBS 6B](https://handbook.fca.org.uk/handbook/icobs6b), [PS21/5](https://www.fca.org.uk/publications/policy-statements/ps21-5-general-insurance-pricing-practices-market-study) |
| Claims development / maturity | 05 R4, FR-MON-12; 01 VR-ACT-14 | ★★ | Development factors and patterns, earned vs written basis, why an immature A/E is misleading, applying a supplied pattern without doing reserving | IFoA GI reserving material (for the pattern concepts only — reserving itself is out of scope) |
| Alerting design | 05 FR-MON-28..32 | ★ | Alert lifecycle (raise/ack/resolve/suppress), deduplication keys, consecutive-breach logic, escalation vs repetition, detecting mis-thresholded monitors | [Google SRE — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) |

## 4. Rating execution

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| GoRules ZEN Engine ✔ | ADR-0004, 03 FR-RATE-1..13, 56..58 | ★★★ | **Verified: `Variable::Number` is `rust_decimal::Decimal`, so engine arithmetic is exact — OQ-RATE-1 resolved.** Remaining study is the boundaries: the `arbitrary_precision` serde feature and where it is *not* default, and `maths-nopanic` returning `0` on invalid input instead of raising. | JDM graph format, decision tables, expression language and its numeric semantics (**OQ-RATE-1**), custom node / loader extension points for rate-table lookup and `model_call`, Python binding overhead at 200 rps, native trace output | [ZEN Engine docs](https://gorules.io/docs/), [zen-engine-py](https://github.com/gorules/zen) |
| Decimal arithmetic | FR-OVR-7, 03 FR-RATE-29/32 | ★★ | `decimal.Decimal` contexts, `ROUND_HALF_EVEN` for money, integer minor units and their exact float64 range, avoiding float contamination through JSON serialisation, proving a premium ladder reconciles to the penny | [Python decimal](https://docs.python.org/3/library/decimal.html), [What Every Computer Scientist Should Know About Floating-Point](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) |
| **Redis (cache semantics)** | 03 FR-RATE-51, NFR-RATE-6 | ★★ | Cache warming before an atomic bundle switchover, content-hash keying, memory sizing for 500 MB bundles, eviction policy that must never evict the live bundle | [Redis docs](https://redis.io/docs/latest/) |
| **Low-latency Python serving** ✔ | 03 NFR-RATE-1, NFR-RATE-13/14 | ★★★ | **Measured (spike S2):** a 500-tree × 60-feature single-row GBM call is p99 **1.09 ms** — 2 % of budget — and **`nthread=1` beats all-cores at the tail** (max 4.5 ms vs 19.9 ms), because thread-pool spin-up dominates one row. | **Measured elsewhere:** Pydantic validation costs ~1 ms/request — 2 % of the budget before any pricing work — and `response_model` forces outbound validation across 3–5 transformations. Hence NFR-RATE-13: validate inbound, never outbound, and encode with `ORJSONResponse`. | Where a 50 ms p99 budget actually goes: Pydantic validation cost on the hot path, single-row GBM inference, thread pinning and BLAS contention, async vs sync endpoints for CPU-bound work, GIL behaviour under 200 rps | [FastAPI concurrency](https://fastapi.tiangolo.com/async/), [XGBoost inference notes](https://xgboost.readthedocs.io/en/stable/prediction.html) |

## 5. Frontend

> **Vendored skills cover the first four rows** as of 2026-08-15 (`CLAUDE.md` §12):
> `vue-best-practices`, `vue-router-best-practices`, `vue-pinia-best-practices`,
> `vue-testing-best-practices`, `vue-debug-guides` and `create-adaptable-composable`, from
> `yes-404/vue3-skills` (MIT). What they do **not** cover is anything specific to this
> platform — the generated-client seam, how money and exact decimals cross into TypeScript,
> the RFC 9457 error shape, cursor pagination, the 202-plus-Job model. That is
> `.claude/skills/vue-frontend`, and the two are meant to be read together.
>
> `vue-jsx-best-practices` and `vue-options-api-best-practices` were deliberately **not**
> taken: §3 fixes `<script setup lang="ts">` and the Composition API, and a skill teaching
> a rejected approach is worse than a missing one.

| Component | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| Vue 3 Composition API ✔ | 00 §5.6 | ★★ | **Skill vendored** (`vue-best-practices`, `create-adaptable-composable`). Remaining project-specific: composables over the generated client, suspense for async views | [Vue 3 docs](https://vuejs.org/guide/introduction.html) |
| Pinia ✔ | frontend state | ★ | **Skill vendored** (`vue-pinia-best-practices`). Remaining: persisting the selected dataset/model context across routes | [Pinia docs](https://pinia.vuejs.org/) |
| Vue Router ✔ | 01/02/03 §5.3 views | ★ | **Skill vendored** (`vue-router-best-practices`). Remaining: guards against the permission set `GET /me` returns | [Vue Router docs](https://router.vuejs.org/) |
| Vite + TS strict | frontend build | ★ | Strict-mode config, path aliases, env handling, build splitting for heavy chart bundles | [Vite docs](https://vite.dev/) |
| Tailwind | frontend styling | ★ | Design tokens, dark mode, component extraction discipline | [Tailwind docs](https://tailwindcss.com/docs) |
| ECharts / vue-echarts | 02 diagnostics, 05 dashboards | ★★ | Large-dataset rendering, dual-axis A/E charts, custom tooltips, accessible tabular fallback (NFR-OVR-10) | [Apache ECharts](https://echarts.apache.org/en/index.html), [vue-echarts](https://github.com/ecomfe/vue-echarts) |
| TanStack Table | 03 rate table editor | ★★ | Virtualised rows, editable cells, column pinning, diffing edits against a baseline version | [TanStack Table](https://tanstack.com/table/latest) |
| Vue Flow ✔ | 03 §5.3 DAG designer | ★★★ | **Verified:** `isValidConnection` (per-handle or global) is the mechanism behind FR-RATE-1's "invalid before save"; large graphs need memoised node components, and Web Workers are the escape hatch for layout at ~200 steps. | Custom node components per step type, showing validation errors *on the node*, edge derivation from produces/consumes names rather than hand-drawn arrows, auto-layout, undo/redo, structural diff overlay | [Vue Flow docs](https://vueflow.dev/), [Custom nodes](https://vueflow.dev/guide/node.html) |
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
| Vitest / Vue Testing Library / Playwright ✔ | frontend | ★ | **Skill vendored** (`vue-testing-best-practices`). Remaining: mocking against the *generated* API types so a contract change breaks the test rather than the runtime | [Vitest](https://vitest.dev/), [Playwright](https://playwright.dev/) |
| Docker Compose / Helm | `deploy/` | ★ | Local full-stack parity (NFR-OVR-9), worker scaling, MinIO wiring | [Compose docs](https://docs.docker.com/compose/) |

---

## 7. Research priority

Ordered by *risk × unfamiliarity*, not by build order:

> **Updated 2026-08-14 after Track A research.** Items 1–3 and 5 have been partially or
> fully discharged; the ordering below now reflects what is *left*, with the settled parts
> struck through. See [`research/track-a-findings.md`](research/track-a-findings.md).

1. **Custom objectives end-to-end** — ~~SymPy derivation~~ ✔ and ~~XGBoost `base_margin`
   mechanics~~ ✔ are settled. What remains is the **restricted AST parser** (untouched, and
   the only place user input reaches the numerical core) and the **certification checks**,
   which research showed were specified wrongly and are now FR-MODEL-68..70. **LightGBM's
   `init_score` remains unverified** — the assumption of symmetry with XGBoost is exactly
   the kind that F5 showed can hide a silent failure.
2. **~~ZEN Engine decimal semantics~~ ✔ resolved — study the boundaries instead.** Engine
   arithmetic is exact `rust_decimal`. The remaining risk is `arbitrary_precision` across
   the binding and `maths-nopanic` returning `0` (FR-RATE-56/57).
3. **~~glum standard errors~~ ✔ confirmed** — the API exists. Remaining: reconciling its
   numbers against Emblem, which is a domain task, not a library one.
4. **Polars lazy execution at 10 M+ rows** — everything downstream inherits its
   performance.
5. **~~Pydantic v2 discriminated unions~~ ✔ confirmed**, with one gap to close: `Decimal`
   generates a permissive `anyOf` that must be constrained to string, or FR-OVR-7 is
   satisfiable by a lossy payload.
6. **Vue Flow custom nodes** — the highest-effort frontend surface.
7. **Low-latency Python serving** — the 50 ms p99 budget (NFR-RATE-1) is the one NFR
   that cannot be fixed later by adding hardware alone.

**Do not sequence §8–§9 after this list.** Three of those practice items — requirement
traceability, the walking skeleton, and reproducibility auditing — shape decisions taken in
the very first sprint and become expensive to introduce afterwards, exactly like the
retrofit list in [`roadmap.md`](roadmap.md) §5. Start them alongside item 1, not after item 7.

---

## 8. Project delivery & management

Practices that keep a 417-requirement, phase-gated project moving.
"Used in" cites the artifact each practice operates on, so none of these is generic advice
detached from the repo.

| Practice | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| **Requirement traceability** | 417 permanent IDs across [`specs/`](specs/); `CLAUDE.md` §5 | ★★★ | Building an FR → contract → test → code matrix; coverage reporting that proves no requirement was silently dropped; handling `SUPERSEDED BY` without renumbering; deciding what granularity of test satisfies an FR. The hardest part is not building the matrix but keeping it honest once code moves faster than docs | [ISO/IEC/IEEE 29148](https://www.iso.org/standard/72089.html) (requirements engineering); [INCOSE traceability guidance](https://www.incose.org/) |
| **Specification review** | [`specs/`](specs/), [`workflows/`](workflows/) | ★★ | Reading a spec for ambiguity rather than for agreement; testing whether an FR is falsifiable; Fagan-style inspection with defined roles; spotting requirements no workflow reaches (usually infrastructure — or genuinely unwanted) | Gilb & Graham, *Software Inspection*; Wiegers, *Software Requirements* (review chapters) |
| **Decision records & decision hygiene** | [`adr/`](adr/), [`open-questions.md`](open-questions.md) | ★★ | When a choice earns an ADR versus an open question; superseding rather than editing an accepted ADR; writing consequences honestly, including the negative ones; closing a question with evidence rather than fatigue | [Nygard, *Documenting Architecture Decisions*](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions); [adr.github.io](https://adr.github.io/) |
| **Phase gating & acceptance criteria** | [`roadmap.md`](roadmap.md) §12; the five [workflow docs](workflows/) | ★★ | Defining "done" as an executable journey rather than a requirement checklist — this project already does it, and the skill is holding the line; writing a definition of done that survives schedule pressure; recognising phase creep early | Cohn, *Agile Estimating and Planning* (release planning); [Basecamp, *Shape Up*](https://basecamp.com/shapeup) (appetite and circuit breakers) |
| **Work breakdown under uncertainty** | [`roadmap.md`](roadmap.md) §11 — Phase 1 is ~47 % of the surface | ★★★ | Deriving a WBS from requirement surface rather than intuition; splitting a phase on an existing module boundary; reference-class forecasting; why velocity/points mislead across a 417-requirement surface; tracking by demo-able outcome instead of percent-complete | Kahneman & Lovallo on reference-class forecasting; [Shape Up](https://basecamp.com/shapeup) on appetite; McConnell, *Software Estimation* |
| **Walking skeleton / architectural runway** | [`roadmap.md`](roadmap.md) §5 "What cannot be retrofitted" | ★★★ | Identifying what must exist in v1 because retrofitting is a rewrite; building a thin vertical slice through every layer before broadening any of them; deferring breadth, never depth. **This is the single most valuable practice skill for Phase 1** — the retrofit list is exactly its output | [Cockburn, *Walking Skeleton*](https://wiki.c2.com/?WalkingSkeleton); Nygard, *Architecture Without an End State* |
| **Risk register & spike discipline** | [`phase-0-status.md`](phase-0-status.md) §5 — spikes S1, S2 | ★★ | Distinguishing a risk from an issue; sizing a spike to answer exactly one question; pre-mortems; being willing to let spike evidence kill an accepted ADR (S1 can invalidate ADR-0004) | DeMarco & Lister, *Waltzing with Bears*; Klein on the pre-mortem |
| **Open-source project operations** | Public repo; licence pending OQ-OVR-2 | ★★ | Issue triage and labelling that scales past the maintainer; `CONTRIBUTING`, `CODEOWNERS`, security disclosure policy; DCO versus CLA and why the choice is hard to reverse; release process, semver for `pricing-core` (OQ-OVR-4), changelog discipline | [opensource.guide](https://opensource.guide/); [Semantic Versioning](https://semver.org/); [Keep a Changelog](https://keepachangelog.com/) |
| **Commit and PR hygiene** | `CLAUDE.md` §10 — Conventional Commits, squash-merge | ★ | Commit granularity that maps to a reviewable unit of work; writing a body that survives archaeology two years later; PR descriptions that state known gaps rather than hiding them; automated changelog generation from commit trailers | [Conventional Commits](https://www.conventionalcommits.org/) |
| **Stakeholder reporting** | Pricing committee; [`phase-0-status.md`](phase-0-status.md) | ★★ | Reporting progress by exit criteria rather than percent-complete; communicating a re-plan without losing credibility; presenting a decision backlog so it gets decided rather than admired | Any credible project-communication text; the practice matters more than the source |

---

## 9. Audit & assurance

Two distinct things share the word "audit" on this project, and conflating them causes
real confusion:

- **§9.1 — auditing the project.** Is the work actually done, and does the code match the
  specification?
- **§9.2 — assurance the platform's *output* must withstand.** When an insurer's internal
  audit, an external reviewer, or a regulator examines a price this platform produced, what
  do they test for?

The platform's own audit-log *engineering* (append-only tables, hash chaining,
separation-of-duties enforcement) is a build-axis skill and lives in §5b.

### 9.1 Auditing the project

| Practice | Used in | Depth | Skills to research | Resources |
|---|---|---|---|---|
| **Documentation audit automation** | [`scripts/audit-docs.py`](../scripts/audit-docs.py) | ★★ | Extending the existing script as the suite grows — requirement coverage, contract-to-spec drift, orphaned artifacts; gating CI on it so docs drift fails the build rather than accumulating; writing checks that fail for the right reason (verify a new check against a deliberately broken input before trusting it) | The script itself is the reference; treat it as production code |
| **Spec-to-implementation conformance** | Phase 1 onward; FR-PLAT-48 | ★★★ | Marking tests with the requirement IDs they satisfy (`pytest` markers) and generating a coverage report from them; failing CI when a generated contract drifts from `model-schema`; periodic reconciliation of "what the spec says" against "what the code does" — the gap opens silently and only ever widens | [pytest markers](https://docs.pytest.org/en/stable/example/markers.html); OpenAPI diff tooling |
| **Review for a governed system** | `06` NFR-GOV-8; FR-OVR-4 | ★★★ | **Negative testing as a first-class discipline** — the suite must prove a submitter *cannot* approve, not merely that an approver can; reviewing every write path for a co-located audit write; adversarial review of anything touching money, permissions, or immutability | [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) (access-control chapter) |
| **Reproducibility audit** | FR-OVR-8; NFR-MODEL-6/7; NFR-RATE-7 | ★★ | Verifying determinism claims rather than asserting them: byte-identical artifact round-trips, identical `spec_hash` producing identical coefficients, bundle-hash-to-premium stability across machines; pinning library versions per artifact and testing what happens when they move | Reproducible-builds practice; the NFRs name the exact tolerances |
| **Dependency, licence & supply-chain audit** | NFR-OVR-11; NFR-PLAT-8 | ★★ | SBOM generation and — the part usually skipped — actually reading one; CVE triage and what "no HIGH/CRITICAL at release" costs to sustain; licence compatibility, including why a copyleft transitive dependency would break the Apache-2.0 recommendation in OQ-OVR-2 | [`pip-audit`](https://pypi.org/project/pip-audit/), [Syft](https://github.com/anchore/syft), [Trivy](https://trivy.dev/), [SPDX licence list](https://spdx.org/licenses/) |
| **Performance regression auditing** | NFR-RATE-1; NFR-MODEL-1/2 | ★★ | Benchmarks as CI gates rather than one-off measurements; distinguishing a regression from noise on shared runners; tracking p99 rather than mean, because the NFR is written on p99 | [pytest-benchmark](https://pytest-benchmark.readthedocs.io/); latency-measurement literature on coordinated omission |

### 9.2 Assurance the platform's output must withstand

The specs already encode most of what follows — this is the reading that explains *why*
those requirements are shaped as they are, and what a reviewer will actually ask for.

The UK actuarial standards are a **two-layer stack**: TAS 100 applies to all technical
actuarial work; TAS 200 adds insurance-specific requirements on top of it. Read them in
that order.

| Standard / practice | Relates to | Depth | Skills to research | Resources |
|---|---|---|---|---|
| **TAS 100 — Principles for Technical Actuarial Work** *(general)* | `06` dossiers §4.4; `02` diagnostics | ★★★ | The FRC's **general** standard, applying to all technical actuarial work regardless of domain. Requirements on judgement, data, assumptions, models and communications; what "sufficient documentation for another actuary to understand the work" means in practice — precisely what the generated dossier is trying to be. Read it *against* the §4.4 section list and check for gaps | [FRC — TAS 100 and TAG](https://www.frc.org.uk/library/standards-codes-policy/actuarial/tas-100/) |
| **TAS 200 — Insurance** *(sector-specific)* | `01` assumptions & data; `02` model build; `06` dossiers | ★★★ | The **insurance-specific** standard that sits on top of TAS 100 — one of three Specific TASs (200 Insurance, 300 Pensions, 400 Funeral Plans) applying where public-interest risk is highest. **v2.0, published 20 Sep 2024, effective 1 Jan 2025.** The revision closed gaps in **assumption setting**, insurance transformations and audit, and added material to help practitioners consider the implications of the FCA's **Consumer Duty** — which makes it the standard that ties this platform's assumption/documentation trail to the fair-value work in `04`. **Scope caveat below.** | [FRC — TAS 200](https://www.frc.org.uk/library/standards-codes-policy/actuarial/tas-200/), [FRC revision announcement](https://www.frc.org.uk/news-and-events/news/2024/09/frc-publishes-revised-technical-actuarial-standards-for-the-insurance-sector/) |
| **APS X2 — Review of Actuarial Work** | `06` approval workflow; FR-GOV-11 | ★★ | The IFoA's standard on independent peer review: when it is required, what independence means, and how the reviewer's work is itself evidenced. Maps directly onto separation of duties and the evidence bundle | [IFoA — APS X2](https://actuaries.org.uk/standards/) |
| **Model risk management principles** | `06` governance; OQ-GOV-4 risk tiering | ★★★ | Model identification and **tiering**, governance and ownership, development/implementation/use controls, independent validation, and an MRM policy. **Caveat worth knowing: PRA SS1/23 is written for banks, not insurers** — it does not apply to a GI insurer directly, but it is the clearest articulation of these principles in UK regulation and insurers commonly align to it voluntarily. Its five principles map almost one-to-one onto spec `06`, and it is the strongest argument for OQ-GOV-4 | [PRA SS1/23](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks) (read with the applicability caveat above) |
| **Three lines of defence** | `06` §1.4 actors; FR-GOV-4/5 | ★★ | Who owns what: the pricing team owns the model (first line), model risk and compliance challenge it (second), internal audit assures the whole framework (third). This is the organisational shape the RBAC roles must be able to express — particularly the read-everything, write-nothing **Auditor** role, which exists for the third line | [IIA — Three Lines Model (2020)](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model/) |
| **Solvency II data quality** | `01` validation layers; FR-DATA-16 | ★★ | The accuracy / completeness / appropriateness triad for data used in technical provisions, and the expectation of a documented data-quality process. The four validation layers in spec `01` are effectively an implementation of it, and framing them that way makes them far easier to defend | Solvency II Delegated Regulation (EU) 2015/35, Art. 19; EIOPA data-quality guidance |
| **ICOBS — Insurance: Conduct of Business Sourcebook** | `04` FR-OPT-18..30; `03` renewal path | ★★★ | The FCA Handbook sourcebook governing conduct for non-investment insurance. **ICOBS 6B (Home and motor insurance pricing) is the binding text behind everything this platform calls "GIPP"** — PS21/5 and PS21/11 are the policy statements that announced it, not the rules themselves. Learn: 6B.2.1R (renewal price must not exceed ENBP, tested when the renewal notice is prepared), **6B.2.5R (which channel to assume — first-purchase, with a defined fallback; this corrected a defect in our design)**, and the scope limit to home and motor. Also worth knowing: 6A.3 renewal transparency (last year's premium on the notice) and PROD 4 product governance / fair value, which sit next to Consumer Duty | [ICOBS 6B](https://handbook.fca.org.uk/handbook/icobs6b), [ICOBS 6B.2](https://handbook.fca.org.uk/handbook/icobs6b/icobs6bs2), [PS21/5](https://www.fca.org.uk/publications/policy-statements/ps21-5-general-insurance-pricing-practices-market-study), [PS21/11 amendments](https://www.fca.org.uk/publications/policy-statements/ps21-11-general-insurance-pricing-practices-amendments) |
| **FCA Consumer Duty — price and value** | `04` GIPP and fairness constraints | ★★ | Fair value assessments, what evidence supports one, and how pricing decisions must be justified in outcome terms rather than technical ones. Sits alongside **ICOBS 6B** (§3b and above — the binding pricing rules, of which PS21/5 was merely the announcement), and **TAS 200 v2.0 added material specifically to help actuaries reason about Consumer Duty implications** — so read the two together rather than separately | [FCA PS22/9 — A new Consumer Duty](https://www.fca.org.uk/publications/policy-statements/ps22-9-new-consumer-duty) |
| **Audit engagement practice** | `06` FR-GOV-32 regulatory export | ★★ | What an auditor *tests* versus what they *read*; preparing a walkthrough; control design versus operating effectiveness; sampling; assembling an evidence pack that answers the question asked rather than the one you prepared for. The regulatory export exists to make this a retrieval task rather than an archaeology project | IIA practice guides; ISAE 3402 / SOC 2 control-testing concepts as a mental model |

#### Scope caveat on TAS 200 — resolve this before relying on it

**TAS 100 applies to this platform's output regardless** — it is the general standard and
covers all technical actuarial work. TAS 200 is narrower, and whether **pricing and premium
rating** fall inside its scope could not be established from the FRC's public summaries;
the scope statement lives in the standard text itself.

This is not a detail. If pricing is in scope, TAS 200's assumption-setting requirements
bear directly on `02`'s factor, banding and grouping rationale and on `01`'s validation
evidence, and the generated dossier (`06` §4.4) has to satisfy them. If it is not, TAS 100
alone governs and the dossier's bar is lower.

**Read the standard and record the determination** — in `06` if it changes the dossier's
required sections, otherwise here. Do not cite TAS 200 as binding on pricing work until
someone has confirmed it is.

### 9.3 The one thing to internalise

Every one of these standards asks the same question in different words: **can you show
what you did, why, on what data, who checked it, and reproduce it now?** The specification
suite already answers it — immutable artifacts, evidence-gated approvals, in-transaction
audit, generated dossiers, determinism NFRs.

The risk in Phase 1 is not that the platform fails to satisfy these standards. It is that
the answers get *implemented as features* rather than *held as invariants*, and quietly
erode under delivery pressure — one un-audited write path, one mutable artifact, one
float in the rating path. §9.1 exists to catch that while it is still cheap.
