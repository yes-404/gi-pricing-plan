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
orchestrated by the **scheduler tick** (`07` FR-PLAT-61), with the pipeline code it
submits living in `pipelines/`, which calls the same backend APIs and
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
| **FR-OVR-7** | Monetary values are integer minor units (pence/cents) or `Decimal` throughout the rating path and all persisted rate tables. Floats are permitted only inside model fitting and diagnostics, never in a quoted premium. **One workspace, one currency** (OQ-OVR-3, decided 2026-08-14): the code is a workspace setting and is carried on every artifact's envelope, so multi-currency in Phase 4 adds FX effective-dating rather than migrating every monetary column. *(Scope, recorded 2026-08-24 — W6b-13b.)* The rule above is scoped to the rating path and persisted rate tables, and its carve-out permits floats in model fitting and diagnostics, so a diagnostic **payload** is textually outside it — while the platform does not behave that way: `OneWayRow` (`packages/model-schema/src/model_schema/profiles.py:141`) is a diagnostic artifact that still types `claim_amount_minor` as strict `MoneyMinor`, and `packages/pricing-core/src/pricing_core/data/validate.py:918` casts with `int(...)`. *(Boundary, recorded 2026-08-24 — OQ-OVR-11.)* The carve-out reaches **statistics, not amounts**, and the test is **what a quantity denominates, not how it was computed**. A quantity that denominates money stays integer minor units or `Decimal` **wherever it appears**: inside a diagnostic payload, inside one published through an untyped `dict[str, Any]`, and in a threshold or bound on a monetary quantity. Being added to another amount, compared against one, or quoted is **indicative of a money denomination and is not the test** — the same demotion division gets below, and for the same reason: each is something done *to* a quantity, and the test is what the quantity is. Two corollaries, because the first drafting of this sentence got both wrong. **A bound takes its kind from the quantity it bounds, and the direction never reverses** — comparison is **dimensional**: money-per-claim compared against a band in money-per-claim is a statistic against a statistic, and comparing a statistic against a bound does not make the statistic money, it makes the bound a statistic's bound. Of the three, only *compared against one* was load-bearing here: *added to another amount* is dimensional already, and *quoted* inherits the **quoted premium** of this requirement's first sentence. And **a bound's name is not evidence of its kind**, since the `..._minor` marker is exactly what is under test in the names released below — `_severity_range` (`packages/pricing-core/src/pricing_core/data/validate.py:1071-1076`) compares `mean_severity`, the exemplar statistic named in the next sentence, against `min_severity_minor` and `max_severity_minor`, and reading those names as making mean severity monetary would invert the one classification this requirement is surest of. It is not coerced to float at a read site. A quantity that denominates a rate, ratio, share or fraction is a statistic — it may be a float wherever it appears, and by FR-OVR-20 it may not be named `..._minor`. **Division is evidence of the second kind, never the test**: money divided by a count is still money, so a boundary resolving on division alone would make a per-instalment or apportioned premium a statistic and license a float one, which the sentence above already forbids. This states the line the platform already held without writing it down — `OneWayRow` (`packages/model-schema/src/model_schema/profiles.py:156`) types `claim_amount_minor` as strict `MoneyMinor` though it is a diagnostic artifact, while `mean_severity` beside it is `float \| None`, which is the same line OQ-OVR-7 drew from the other side on 2026-08-17: the mean keeps its float **and** loses the suffix, being a statistic on both counts. One consequence is not mechanical and is recorded so it is not discovered as a regression: a money-denominated value obtained by interpolation needs a **stated rounding direction**, because rounding moves the value. `_large_loss`'s quantile branch (`packages/pricing-core/src/pricing_core/data/validate.py:960-967`) interpolates linearly and the result is the cut in `values.filter(pl.col(column) >= absolute)`, so rounding it down admits more rows and up admits fewer — the check's own verdict changes with the direction. Its other branch takes a threshold already declared in minor units and the `float(...)` there is pure loss. Which side of this line **burning cost** falls on is **OQ-OVR-12**, open: the repository currently classifies it both ways, and the test above makes that divergence inexpressible without saying which standing changes. This requirement governs **values**; the reservation of the `_minor` *name* is FR-OVR-20, which is not scoped. |
| **FR-OVR-8** | Determinism: given identical inputs and pinned artifact versions, model fitting and scoring reproduce identical outputs. All stochastic operations take an explicit persisted `random_seed`. |
| **FR-OVR-9** | Datasets are treated as pseudonymised. The platform stores no direct identifiers (name, address line, email, exact DOB) as modelling columns; ingestion rejects columns tagged `direct_identifier` ~~unless explicitly configured as a passthrough key that is excluded from all Factors~~. *(amended 2026-08-24 (W6b): the struck exemption names a mechanism that does not exist, and the need behind it is met by classification instead. The refusal itself is unchanged and is delivered.)* *(i)* **There is no passthrough configuration, and there is no evidence there ever was one.** Outside this sentence, no specification, schema field, enum member, ingestion argument or database column names such a thing — the only other occurrences of the word in the repository are ordinary English in unrelated prose. The exemption the platform actually enforces is `01` FR-DATA-13's, appended as FR-DATA-41: a `direct_identifier` column must be **dropped or pseudonymised**, checked at ingestion before any row is written, with `DIRECT_IDENTIFIER_PRESENT` naming FR-DATA-13 as the rule it applies. This row was the sole outlier, so the disagreement is resolved in favour of the three artifacts that agree (`CLAUDE.md` §0). *(ii)* **A key column reaches modelling by being classified, not by being exempted.** `pii_class` has a `pseudonymous_key` member, which `MODELLING_FORBIDDEN_PII` does not contain, and `01` §4.1's canonical dictionary classifies `policy_id` exactly that way — so a stable join key is carried by declaring what it is, while a column classified `direct_identifier` has no route through at all. That is the stronger rule and the reason the struck clause is not worth rebuilding: an exemption applied to a direct identifier keeps the identifier and moves the risk downstream, whereas classification asserts there is no identifier left to keep. *(iii)* **The second half is struck as wording only, and the gap it named is real, wider than this row, and owned elsewhere.** Nothing excludes a column from Factor construction on its `pii_class` today, for any class — `Factor.prohibited` is an author-set boolean that no code derives from the dictionary. That is recorded at [`../roadmap.md`](../roadmap.md)'s "The modelling PII guard is unenforced" finding, whose §14 disposition proposes a new unit with its own id and owner and is awaiting a maintainer acceptance line. Striking the clause here removes a promise this requirement never kept; it neither closes that gap nor claims custody of it. |
| **FR-OVR-10** | Every long-running operation (validate, fit, score-batch, optimise, monitor) is a **Job** with a uniform lifecycle, progress, cancellation, log, and result reference (see `07-platform.md`). |
| **FR-OVR-11** | The platform exposes a documented OpenAPI 3.1 surface; the SPA is a pure client of it. Any action possible in the UI is possible via the API. |
| **FR-OVR-12** | Time is stored as UTC `timestamptz`. All business-effective dating (reference data, rating versions) uses explicit `effective_from` / `effective_to` half-open intervals `[from, to)`. |
| **FR-OVR-13** | **One tenant, one deployment — permanently, not for Phases 0–4** (OQ-OVR-1, decided 2026-08-15 by [ADR-0006](../adr/0006-tenant-isolation-is-a-deployment-boundary.md)). All schemas carry a `workspace_id`, and a **Workspace is an organisational container inside one tenant** — a business unit or line of business, and the scope for RBAC (`06` FR-GOV-4), settings (`07` §3.8) and the audit chain (`06` FR-GOV-24). **It is not an isolation boundary and no document may describe it as one**: the isolation is the deployment (FR-OVR-15), and a `workspace_id` believed to be a security boundary is the belief under which someone writes the cross-workspace query that nothing prevents. |
| **FR-OVR-15** | **No running component that carries tenant data is reachable from more than one tenant's deployment** — application instances, database, cache and broker, object storage, encryption keys, and the audit chain are per tenant (ADR-0006). What may be shared is what carries no tenant data: container images, infrastructure code, CI, and public reference data (`01` FR-DATA-32). A shared managed database or bucket satisfies this only if no tenant's credentials can reach another's data; "separate schema, same connection" does not. |
| **FR-OVR-16** | **Provenance names the build.** Every Job records the platform version it ran on, and every generated dossier (`06` FR-GOV-27) states it alongside the artifacts it assembled. Under ADR-0006 each tenant runs its own deployment, so version skew between tenants is normal and permanent: "the platform computed this" stops being a single, knowable thing, and a figure reproduced two years later must be attributable to the build that produced it. Owned by **W14**; any earlier `Job` migration should carry the column rather than wait. |
| **FR-OVR-17** | **Each workflow journey (`docs/workflows/wf-01…05`) is evidenced twice, and a marker on an existing test is not one of them** (OQ-OVR-6, decided 2026-08-15). **(i)** A mechanical citation audit, running in CI on every docs change, asserts that every endpoint path and `pricing-core` function a journey step cites is declared by the owning module's §5.1 or §5.2 — the `scope-audit.py --endpoints` idea one level up, catching the class of drift that a spec and a journey disagreeing produces. **(ii)** One end-to-end test per journey, driving it through the platform, written by the workstream that completes the last module the journey touches — which in every case is the phase whose exit criterion names it (`roadmap.md` §12), so `wf-01` is **W5**'s. Marking an existing test with a journey id claims a journey where one slice is covered, which is the failure this requirement exists to refuse. **(i) delivered 2026-08-17 (W5)** as `scripts/audit-docs.py` check 21, run by `docs.yml` on every `docs/**` change and marked in `tests/test_repository_invariants.py` so it is visible to `req-coverage.py` rather than enforced invisibly. It found drift on its first run — wf-01 cited a `profile_version()` that `01` §5.2 renamed to `profile_frame` / `profile_parquet` on 2026-08-15 without the journey following. Making it mechanical required a citation **form**, recorded in `docs/workflows/README.md`: an endpoint is `` `METHOD /path` `` and a `pricing-core` function is `` `name()` ``, the parentheses being what distinguishes a citation from a column name or a parameter in the same cell. **(ii) delivered *partially* for `wf-01` on 2026-08-17 (W5)** as `backend/tests/test_wf01_journey.py`: one test walking A→E2 and E6→E10 through the same Jobs and services a caller reaches — ingest, the failure loop, validation, split, bandings, groupings, a GLM and an XGBoost fit, diagnostics, the transparency artifact, the comparison, submission, the self-approval refusal, and approval. **Steps of that journey the platform could not execute were named rather than skipped**, each pinned as an **inverted assertion** — one that passes while the capability is absent and fails the day it lands. **All three fired as designed and are now driven, so (ii) is delivered for `wf-01` (2026-08-18).** E4 and E5 went red when `PerilStructure` landed and the peril-structure slice drove them: the journey composes a structure over the selected model, reconciles it through the real worker, and submits and approves it alongside the model. **D7** went red the same day when `interaction` became resolvable (FR-MODEL-91) and the interaction slice drove it. The pinned test is deleted rather than emptied — assertions that stood in for journey steps, with the journey now containing the steps. Two divergences are recorded in the test rather than pinned, because both are limits of that fixture and not of the platform: E4 composes AD as burning cost where the journey says frequency × severity (severity responds to cost *per claim*, and every claim-free row in the book carries a zero a Gamma refuses), and D7 crosses banded age with vehicle group where the journey names `annual_mileage × driver_age` (the book has no mileage column). `packages/pricing-core/tests/test_perils.py` and `test_interactions.py` drive both shapes directly. The other four journeys' (ii) remains outstanding, each with the phase whose exit criterion names it. |
| **FR-OVR-14** | An artifact may only reference artifacts that are in a state at least as mature as its own (a `live` Rating Version cannot reference a `draft` Model). Enforced at transition time, not just at creation. |
| **FR-OVR-18** | **The exact-decimal types refuse a `float` at validation** (`OQ-OVR-8`, decided 2026-08-19). FR-OVR-7 makes exactness a rule about *storage*; this makes it a rule about *input*, which is where the precision is actually lost. `DecimalStr` and `Relativity` reject a `float` outright — `12.0` as firmly as `0.1 + 0.2`, for the reason `MoneyMinor` already rejects `250.0`: a whole-valued float coerces cleanly, and accepting it teaches the next caller that a float is fine here. `int`, `str` and `Decimal` remain valid, the string form being what every contract round-trip carries. **A caller that legitimately computes in float quantises explicitly before the boundary** — `pricing_core.data.profile._stored_exposure` is the precedent — which puts the choice of decimal places in reviewable code rather than in whatever binary expansion the hardware produced. Delivered 2026-08-19 in `model_schema.money`; the JSON Schema was already `type: string`, so a JSON *number* was contract-violating before this and is now refused rather than silently coerced. |
| **FR-OVR-19** | **The audit cross-checks every module's §5.1 error-code table against the registry that makes a code raisable** (OQ-OVR-9, decided 2026-08-21). `audit-docs.py` check 10 already parses each spec's §5.1 ownership block for the ownership-exclusivity check; it gains a second comparison, against `backend/src/app/errors.py`'s module frozensets (`DATA`, `MODELLING`, `GOVERNANCE`, `PLATFORM`). The two lists must agree in both directions: a declared code absent from its module's frozenset fails, because the spec is promising a code no caller can branch on; a registered code no spec declares fails, because a code with no owner is a code nobody audited. Re-raised codes stay excluded, exactly as the ownership check excludes them. A module that declares owned codes while no frozenset exists (`03`, `04`, `05`) is reported in the audit's notes with its count rather than failed — its codes are declared for a phase whose backend cannot raise them yet — and the agreement rule applies automatically the day a frozenset appears. The check lands with the six discrepancies that exist today resolved, each with a verdict rather than a silence: `OBJECTIVE_GRAMMAR_VIOLATION`, `OBJECTIVE_NONFINITE_DERIVATIVE` and `OBJECTIVE_NOT_CERTIFIED` are declared-and-unbuilt for Phase 2's `expression` objectives (OQ-MODEL-1) and are marked as such in place; `PICKLE_PERSISTENCE_REFUSED` and `TRANSPARENCY_ARTIFACT_REQUIRED` are declared and never raised — the type refuses `pickle` by having no spelling for it, and FR-MODEL-89 checks R3 by query — and are struck with dated notes; `MODEL_SPLIT_REQUIRED` is registered and raised and gains its `02` §5.1 declaration. Per `CLAUDE.md` §13.4 the check is proven to fail on a deliberately introduced divergence before it is trusted. **Owner: the maintainer; the trigger is Phase 1a's exit demo**, because the gate the demo is checked against is the thing this check strengthens. |
| **FR-OVR-20** | **The `_minor` suffix is reserved for integer minor units** (`OQ-OVR-7`, decided 2026-08-17). FR-OVR-7 governs *values* and is scoped to the rating path and persisted rate tables; this governs *names*, and it is **not** scoped — a diagnostic may hold a float, but it may not call one `..._minor`. The two do not conflict, and separating them is what makes a mean severity expressible: keep the float, drop the suffix. *Written down 2026-08-24, not introduced then* — `01` FR-DATA-46 was specified to act on it, and `scripts/audit-docs.py` check 12 has enforced it all along while citing FR-OVR-7, a requirement whose text does not contain it; a reader narrowing FR-OVR-7 to its stated scope would have left that check appealing to an authority that, as written, permitted what the check rejects. Enforcement reaches markdown and schema files only, matching a reserved name against a fractional literal, so it sees neither Python source nor a runtime payload: `validate.py` publishes the suffix on a mean severity, a ratio, at `:1072`–`:1073`, `:1077` and `:1078`, and the read site coerces with `float(...)` so the integers W6b-13b's catalogue writes do not constrain it. Those names pre-date FR-DATA-46's rename (`989308b` is an ancestor of `667c8fe`), so the rename never reached them rather than half-applying; correcting them changes a published validation-report payload and is scheduled with **OQ-OVR-11**. `claim_amount_minor` is a dataset column name and `total_negative_minor` (`:918`) is `int(...)`-cast: both conform. |
| **FR-OVR-21** | **A Contents cell in a module spec's §5.3 Frontend views table is prose and binds nothing** (OQ-OVR-10, decided 2026-08-24). What a view must show is stated in a numbered requirement or in the generated contract; a cell that appears to add an obligation adds none. A cell may instead declare its own kind, inside the cell: *declared-exhaustive*, meaning the view shows what the cell names and nothing further, or *declared-prose*, meaning no binding list may be derived from it. Only a declared-exhaustive cell binds. The affordance is not invented here — `02` §5.3's Diagnostics cell already declared itself prose and forbade deriving a chart set from it, which is why the rule names both halves rather than exhaustiveness alone. **The rule is in force now, and its carve-out is per-cell rather than suspensive.** It binds every §5.3 Contents cell except the seven named below, each of which carries an obligation held in no requirement and no contract and so **remains binding until it is discharged** — discharged meaning raised as a numbered requirement or declared exhaustive. It is put this way round because the alternative reading, that the whole rule stays inert until all seven discharge, would leave every *other* cell binding an obligation this requirement has just found to be unwritten, which is the state the requirement exists to end; and because a per-cell carve-out is what makes the seven safe — none is repealed by a rule that has not reached it. The seven: `01` Validation report's blocked/unblocked banner, and `01` §5.3's own unnumbered *Interaction requirement* ordering paragraph, which is not a cell and which a cell-scoped sweep does not reach; `02` Diagnostics (declared-prose, discharged with this requirement) and `02` Objective certificate's `violated`-as-a-finding presentation rule; `03` DAG designer's on-node live validation; `05` Drift's importance-weighted ordering; `07` Jobs' SSE live updates. They are enumerated rather than described because a migration clause that misses one repeals it exactly as silently as ruling every cell non-binding would, which `CLAUDE.md` §0 forbids. Two of the seven cite a requirement that does not carry their obligation — FR-MODEL-43 governs non-convex objectives and says nothing about presentation, and FR-MON-10 requires importance be reported *alongside* drift, never as an *ordering* — so a discharge is checked by reading the cited requirement's predicate, not by confirming its id exists — and an id-matching sweep across the seven will report all of them green. **Each discharge is owned by the slice that builds the view carrying it, and falls due at that slice's plan**, stated as a rule rather than as slice ids because ids are re-cut and an id written here would age into a wrong owner. The `03`, `05` and `07` cells belong to no Phase 1b slice: under `CLAUDE.md` §0 they are a spec change only, and building against them ahead of their phase is forbidden whether or not this rule has reached them. The contract-is-the-floor half is OQ-MODEL-15's decided rule of 2026-08-21; OQ-MODEL-15 says nothing about a cell being prose, and that half rests on the `02` §5.3 Peril structure library precedent alone. |

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

**Above `Workspace` sits the deployment, and it is not drawn here because it is not an
entity** — one tenant, one deployment, nothing shared (FR-OVR-13, FR-OVR-15, ADR-0006). A
Workspace is an organisational container *inside* a tenant, and a diagram that showed two
tenants would show two of these trees in two systems.

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
  a repeat returns the original result. *Amended 2026-08-23 (`07` OQ-PLAT-8): the
  **24-hour window this line used to state is withdrawn** — it was never implemented, and
  the late duplicate a window forgives is exactly the one a key exists to catch. Keys are
  permanent, with one release: a Job that failed terminally frees its key so the work can
  be attempted again, while success and cancellation do not. `07` FR-PLAT-64 is the
  authority, and FR-PLAT-47 binds the API to this section as amended.*

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
| Model list / detail / diagnostics | `/models`, `/models/:slug?version=` | 02 |
| Custom objective library | `/objectives` | 02 |
| Custom metric library | `/metrics` | 02 |
| Peril structure library / detail | `/peril-structures`, `/peril-structures/:id` | 02 |
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
| **OQ-OVR-1** | ~~Is the workspace the tenancy boundary, or do we also need per-workspace physical isolation for hosted use?~~ **DECIDED 2026-08-15: neither — the tenancy boundary is the deployment.** One tenant, one deployment; schema-per-tenant rejected rather than deferred; `workspace_id` stays as an organisational scope. [ADR-0006](../adr/0006-tenant-isolation-is-a-deployment-boundary.md), FR-OVR-13/15. |
| **OQ-OVR-2** | Project licence: Apache-2.0 (permissive, adoption) vs AGPL-3.0 (protects against closed SaaS forks). |
| ~~**OQ-OVR-3**~~ ✔ | ~~Do we support multiple currencies in one workspace in Phase 2, or defer multi-currency to Phase 4? |~~ **Decided 2026-08-14: deferred to Phase 4; one currency per workspace, recorded on every artifact envelope now (FR-OVR-7, §4.3).**
| **OQ-OVR-6** | ~~How are the five workflow journeys (`workflows/wf-01…05`) evidenced?~~ **DECIDED 2026-08-15: a mechanical citation audit now, one end-to-end test per journey as its last module lands, and never a marker on an existing test.** Specified as FR-OVR-17. Raised by plan review 2, 2026-08-15, when the "workflow coverage" figure turned out to measure whether a journey *mentions* a requirement id. |
| ~~**OQ-OVR-7**~~ ✔ | ~~Should `01` FR-DATA-26's one-way row rename `severity_minor` and `burning_cost_minor`? They are means, and therefore floats, while `_minor` is reserved for integer minor units (FR-OVR-7).~~ **DECIDED 2026-08-17: rename to `mean_severity` and `mean_burning_cost`, in the slice that next changes the profile contract — not as a change of its own, and not never.** Specified as `01` FR-DATA-46, which carries the trigger and the owner. ~~Until then the two names are excluded by name from the money scan, and the exclusion may not grow: a money-discipline allow-list is exactly the kind of exception nobody revisits.~~ **Corrected 2026-08-24: delivered 2026-08-18.** The exclusion was deleted rather than grown, and post-rename `mean_severity` carries no `_minor` for the money scan to exclude, so the condition above was discharged rather than breached. See **OQ-OVR-11** for the names in `pricing-core`'s `validate.py` that the rename never reached. Raised 2026-08-15 by generating the `banding` and `grouping` schemas, which embed the row. |
| ~~**OQ-OVR-4**~~ ✔ | ~~Is `pricing-core` published to PyPI as a standalone library from Phase 1, which would constrain its API stability earlier than otherwise needed? |~~ **Decided 2026-08-14: editable install in Phase 1, publish as `0.x` from Phase 2 with a no-stability notice.**
| ~~**OQ-OVR-5**~~ ✔ | ~~Where does the notebook escape hatch live — an embedded JupyterLab in the platform, or a documented client library only? |~~ **Decided 2026-08-14: client library in Phase 1; embedded notebooks revisited in Phase 4 (§1.2).**
| ~~**OQ-OVR-8**~~ ✔ | ~~`DecimalStr` silently accepts a `float`: `OneWayRow(exposure_years=0.1+0.2)` yields `Decimal('0.30000000000000004')`, binary error preserved inside a field FR-OVR-7 calls exact. Should it refuse floats outright?~~ **DECIDED 2026-08-19: yes — refuse at validation, and put the rule on the type rather than on the field.** Specified as FR-OVR-18 and delivered the same day. The audit the decision turned on found **no caller passing a float**: the one path that computes exposure in float already quantised at the boundary (`_stored_exposure`), so the change cost nothing to adopt and the hole was open only to callers not yet written. `LevelCount.exposure_years`'s hand-written validator is deleted, not duplicated — 11 fields across 6 modules now get the guarantee one field had — the question said 26 across 7, which counted every line mentioning `DecimalStr` rather than every field using it. Raised 2026-08-19 (W5). |
| ~~**OQ-OVR-9**~~ ✔ | ~~Nothing cross-checks a spec's declared error codes (each module's §5.1 table) against `backend/src/app/errors.py`, the registry that makes a code raisable — verified on the FR-MODEL-96 branch that `02` §5.1's `MODEL_APPROXIMATION_INVALID` is registered while no test, script or audit compares the two lists at all; `audit-docs.py`'s error-code check only tests exclusivity between spec documents. The gap is structural and applies to every module. Should a check exist, and where — a standalone script, folded into `audit-docs.py`'s existing error-code pass, or a parametrised test in `backend/tests/test_errors.py`?~~ **DECIDED 2026-08-21: fold the comparison into `audit-docs.py`'s existing error-code pass — FR-OVR-19**, owner the maintainer, before Phase 1a's exit demo. Raised 2026-08-19 (W5, the GLM-approximation-as-a-Model slice). |
| ~~**OQ-OVR-10**~~ ✔ | ~~What is a Contents cell in each module spec's §5.3 Frontend views table — an enumeration of what the view must show, or a prose summary of its character — and how does a cell declare which kind it is? Raised 2026-08-24 (W6b): a filed slice map read `02` §5.3's Diagnostics cell as an enumeration and derived from it a chart count that then bound a slice. The cell was wrong in both directions — it still named double-lift a week after FR-MODEL-50 struck it, and it named none of the further fields `GbmDiagnostics` and `GlmDiagnostics` carry in the generated contract. Cells in the same table do three different things: the Model detail and Diagnostics rows are category-noun summaries, the Objective certificate row enumerates all four `CheckStatus` values with a presentation rule, and the Peril structure library row enumerates its *negative* space. Nothing distinguishes them. Mirrored in `docs/open-questions.md`.~~ **DECIDED 2026-08-24: a §5.3 Contents cell is prose and binds nothing, with a declared-exhaustive and a declared-prose affordance — FR-OVR-21.** In force now, with a **per-cell** carve-out rather than a suspensive one: it binds every cell except the seven carrying an obligation held in no requirement and no contract, each of which stays binding until discharged, because ruling them non-binding retroactively would repeal all seven with no record. *(Clarified 2026-08-24: the original wording read as suspensive — that the whole rule was inert until all seven discharged — which is not what was decided and would have made both slices below unplannable.)* *Consequences:* `W6b-1b` becomes plannable on the rule; `W6b-9` additionally waits on `02` §5.3 Diagnostics being declared prose, which is discharged in this change; `W6b-1a` was never affected. |
| ~~**OQ-OVR-11**~~ ✔ | ~~What governs a monetary value carried inside a `dict[str, Any]` that the generated contract publishes as an unconstrained object, and how far does FR-OVR-7's guarantee reach? `RuleResult.measured` and `RuleResult.threshold` reach the published validation report with `additionalProperties` true, so the purpose-built type check (`test_generated_and_authored_agree_on_scalar_types`, which *does* compare `validation-report`) cannot see them — it compares only paths present on both sides — the money scan walks property names, so dict keys are unreachable, and `audit-docs.py` check 12 reads only markdown and schemas. FR-OVR-7's positive rule is scoped to the rating path and rate tables and permits floats in diagnostics, so nothing is textually breached; yet `OneWayRow`, itself a diagnostic, types its amount strictly. Options: type the payload; extend the scan to dict keys; or write the boundary down only. Recommendation: type the payload, and amend FR-OVR-7's scope alongside it.~~ **DECIDED 2026-08-24 — option (c), write the boundary down: FR-OVR-7 now states it.** The carve-out reaches statistics, not amounts, and the test is **what a quantity denominates, not how it was computed**; money stays integer minor units or `Decimal` *wherever it appears*, including inside an untyped `dict[str, Any]`, which is what closes this row's actual gap — a boundary scoped to *declared* fields would have left the untyped payload exactly where it was. *Consequences:* option (a), typing the payload, becomes the mechanism that lets the existing checks see the value rather than the thing that creates the obligation, and is now specified rather than guessed at; it is **not** wholly mechanical, because `threshold_minor`'s quantile branch needs a rounding direction that moves the check's own verdict. `audit-docs.py` check 12's appeal to FR-OVR-7 for a `_minor` naming rule FR-OVR-7 does not state is **not** fixed here and must not be read as fixed — FR-OVR-20 records it. **This decision releases work explicitly deferred onto it.** `d2a4773` recorded three `..._minor` names published on floats by `_large_loss` and `_severity_range` (`packages/pricing-core/src/pricing_core/data/validate.py`) and scheduled their correction *with this row* rather than inline, because they are rendered verbatim as user-visible labels by `RuleResultRow.vue`. The boundary above settles all three, and **it settles them in two opposite directions** — so a sweep treating them as one population corrects two of them wrongly. `mean_severity_minor` (`:1077`) denominates a statistic, already settled as one by OQ-OVR-7 on 2026-08-17: the float is correct and **the name is the defect**, so it is renamed and its type left alone. `threshold_minor` and `largest_minor` (`:971,978,982`) denominate money — a claim-amount cut and a largest claim amount — so **the name is correct and the type is the defect**, and renaming them would destroy the marker while leaving the float. The fix inverts between the two groups, and the `..._minor` suffix cannot tell them apart because it is the thing under test in one group and the evidence in the other. |
| **OQ-OVR-12** | Burning cost — claim amount divided by exposure — is classified **two opposite ways in the same repository**, and FR-OVR-7's boundary (OQ-OVR-11, decided above) forbids both standings at once. `Reconciliation.observed_burning_cost_minor` and `ReconciledPeril.modelled_burning_cost_minor` (`packages/model-schema/src/model_schema/perils.py:290,306-307`) are strict `MoneyMinor` integers carrying the `..._minor` suffix; `OneWayRow.mean_burning_cost` (`packages/model-schema/src/model_schema/profiles.py:162`) is `float \| None` with no suffix, and that class's own docstring (`:145-148`) states the rule as *"they are statistics, not amounts"*. Same quantity, same arithmetic shape, opposite verdicts. FR-OVR-7 now tests **what a quantity denominates**, and what these denominate is identical, so the divergence is no longer expressible. *Recommendation: (b), burning cost is a statistic, with the integer kept — the `..._minor` suffix is the defect FR-OVR-20 governs, not the type FR-OVR-7 only permits. Open; filed by the change that made it visible rather than decided inside it.* **Two objections this row has already drawn, answered here so they are not re-run.** *That they are different quantities — a per-level mean against a part-level total.* The perils figure is not a total: `perils.py:192` computes `_to_minor(float(np.sum(observed)) / exposure_total)`, a weighted mean per exposure-year across the part, and `Reconciliation.ratio` (`:337-338`) divides modelled by observed so the exposure denominators cancel — which is a thing that works because both sides are rates. The two therefore differ in **grouping**, part against level, not in kind. *That `OneWayRow`'s float is deliberate rather than an oversight.* It is, and the row does not claim otherwise: the docstring states the reason and cites FR-DATA-46 for it, which is why option (a) is the expensive one. A stated reason on one side of a divergence settles that side, not the divergence. **The naming half is FR-OVR-20's territory and the typing half FR-OVR-7's**; this row is filed against the pair because the recommendation splits between them. **One side of this has a decision of record, found after filing.** OQ-OVR-7 — maintainer-accepted 2026-08-17 and specified as `01` FR-DATA-46 — decided that `01` FR-DATA-26's one-way row renames `severity_minor` and `burning_cost_minor`, *"which are **means** and therefore floats"*, to `mean_severity` and `mean_burning_cost`. So the `profiles.py` side is not an unresolved standing but a decided one, and its basis — a mean per unit is a statistic — reaches `perils.py`'s figures too, since `:192` and `:217` both divide by `exposure_total`. That makes **`perils.py` the divergent side**, and narrows this row from *which of the two changes* to *whether an aggregate reconciliation figure is exempt from the basis OQ-OVR-7 already decided on*. Recommendation (b) is unchanged and now rests on a precedent rather than only an argument. Raised by `w6b-planner` as evidence rather than as a verdict, after it had been wrong twice on this row. |
