# 07 — Platform

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `PLAT`
**Prerequisites:** [`00-overview.md`](00-overview.md) §5 (API conventions), §9 (NFRs).

---

## 1. Purpose & scope

### 1.1 In scope

The substrate every other module stands on:

1. **Authentication** — how a Principal is established (users via OIDC, service accounts
   via API keys).
2. **Jobs** — the uniform lifecycle for every long-running operation (FR-OVR-10).
3. **Storage** — PostgreSQL metadata, content-addressed blob store, caches.
4. **Secrets** — how credentials for sources, webhooks, and service accounts are held.
5. **Environments** — `dev` / `uat` / `prod` as first-class platform objects.
6. **Deployment & operations** — packaging, local stack, scaling, backup/restore.
7. **Observability** — logging, tracing, metrics, and health.
8. **Configuration** — workspace settings and their precedence.
9. **API surface conventions** — the concrete implementation of `00` §5.

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Roles, permissions, approvals, audit | `06-governance.md` — this module authenticates; that module authorises |
| Pricing/monitoring semantics of environments | `03`, `05` |
| Actuarial computation of any kind | `pricing-core` (ADR-0001) |
| Choice of cloud provider | Deliberately none; the stack runs anywhere (NFR-OVR-9) |

### 1.3 Hard rules

> **R1 — Everything slow is a Job.** Any operation that can exceed 2 s returns `202` with
> a Job, has progress, is cancellable, and persists its result (FR-OVR-10, NFR-OVR-4).
>
> **R2 — The full stack runs locally with `docker compose up`**, with no cloud dependency
> (NFR-OVR-9). If a feature cannot run locally, it is not in the required stack.
>
> **R3 — Secrets never enter an artifact, a log, an audit event, or an API response.**
> They are referenced (`secret:<slug>`) and resolved only at the point of use.
>
> **R4 — Every request carries a `trace_id` from edge to worker to `pricing-core`**, and
> that id appears in every log line, error response, and audit event (`00` §5.3).

---

## 2. Concepts & glossary

| Term | Definition |
|---|---|
| **Workspace** | The top-level **organisational** container inside one tenant's deployment — a business unit or line of business (FR-OVR-13, ADR-0006). All artifacts belong to exactly one, and it scopes RBAC, settings and the audit chain. The tenancy boundary is the deployment, not this. |
| **Principal** | An authenticated identity: User or Service Account (`06` §2). |
| **Job** | A tracked asynchronous unit of work with a uniform lifecycle, progress, logs, cancellation, and a result reference. |
| **Job Kind** | The typed operation a Job performs (`dataset.ingest`, `dataset.validate`, `model.fit`, `objective.certify`, `rating.compile`, `score.batch`, `dislocation.run`, `optimisation.run`, `gipp.check`, `monitor.run`, `dossier.generate`, `export.regulatory`). |
| **Queue** | A named Celery queue with its own worker pool and resource profile (`default`, `compute`, `scoring`, `io`). |
| **Blob** | A content-addressed immutable object in the object store, keyed by sha256 (ID-4). |
| **Secret** | A named credential held in the platform's secret backend, referenced by slug. |
| **Setting** | A typed configuration value resolved by precedence: environment variable → workspace setting → platform default. |

---

## 3. Functional requirements

### 3.1 Authentication

| ID | Requirement |
|---|---|
| **FR-PLAT-1** | Users authenticate via **OIDC** against an external identity provider (Keycloak, Entra ID, Okta, Google). The platform stores no user passwords. A local development provider ships with the compose stack (R2). |
| **FR-PLAT-2** | Sessions use short-lived access tokens with refresh; the SPA holds tokens in memory, never in `localStorage`. |
| **FR-PLAT-3** | **Service Accounts** authenticate with API keys (prefix-identifiable, hashed at rest, never retrievable after creation). Keys carry an expiry, are rotatable with an overlap window, and are scoped to named environments and the scoring permission set only (`06` FR-GOV-6). |
| **FR-PLAT-4** | Identity provider claims map to platform users on first login; group-to-role mapping is configurable (`06` OQ-GOV-2). A user with no mapped role gets no access, not default access. |
| **FR-PLAT-5** | All API traffic is TLS 1.3; the platform refuses to start in `prod` mode without TLS termination configured (NFR-OVR-8). |
| **FR-PLAT-6** | Failed authentication, key creation/rotation/revocation, and session anomalies are audited (`06` FR-GOV-20). |
| **FR-PLAT-55** | The **browser** authenticates by OIDC **authorization code with PKCE** (OQ-PLAT-6, decided 2026-08-15), against the same provider and discovery document the API verifies against (FR-PLAT-1). The SPA is a *public* client: no client secret exists in it, the code verifier never leaves the browser, and the access token is held in memory only (FR-PLAT-2). Renewal is silent and failure to renew logs the session out rather than retrying indefinitely — an expired session that looks logged in is how a user comes to believe the platform lost their work. The API side is unchanged: it verifies a bearer token and knows nothing about how the browser obtained it. **The development identity headers (`x-dev-principal-id`, `x-dev-workspace-id`, injected by the frontend dev proxy) are not part of this flow and never authenticate anything outside `local`/`dev`** — they hang off `dev_auth_enabled`, which is `False` by default and refuses to start in a deployed environment. Owned by **W6b**. |

### 3.2 Jobs

| ID | Requirement |
|---|---|
| **FR-PLAT-7** | A **Job** has the lifecycle `queued → running → (succeeded \| failed \| cancelled)`, with `queued_at`, `started_at`, `finished_at`, the submitting Principal, the Job Kind, its input parameters, and a result reference. |
| **FR-PLAT-8** | Jobs report **structured progress**: a fraction complete, a current-stage label, and optional counters (rows processed, rules evaluated, boosting rounds). `pricing-core` reports through the injected `ProgressCallback` (ADR-0001); the worker translates it into Job state. |
| **FR-PLAT-9** | Jobs are **cancellable**. Cancellation is cooperative: the callback signals cancellation and `pricing-core` returns at the next checkpoint. A cancelled Job leaves no partially-visible artifact (`01` NFR-DATA-10). |
| **FR-PLAT-10** | Job logs are captured, retained with the Job, and viewable in the UI with the `trace_id` (R4). Logs never contain secrets or full quote inputs (R3, `06` FR-GOV-26). |
| **FR-PLAT-11** | Failed Jobs record a typed error code, a human message, and — where the failure is deterministic (bad spec, invalid rule) — the field-level cause. Infrastructure failures are retried with exponential backoff; deterministic failures are not retried. |
| **FR-PLAT-12** | Jobs are **idempotent by key**: a submission carrying an `Idempotency-Key` that matches a Job from the last 24 h returns the original Job (`00` §5.4). |
| **FR-PLAT-13** | Jobs are routed to queues by Kind, with per-queue worker pools sized independently: `compute` (fitting, certification, optimisation — few, large workers), `scoring` (batch scoring — many, moderate), `io` (ingestion, exports), `default` (everything else). |
| **FR-PLAT-51** | **Job enqueue is transactionally safe.** Celery is the chosen broker (OQ-PLAT-1, decided 2026-08-14), which does **not** enlist in the database transaction — a task can be published to Redis and the surrounding transaction then roll back, leaving a worker acting on state that was never committed. Since audit writes share the caller's transaction (`06` R2), this would produce work with no audit record. Jobs are therefore enqueued through a **transactional outbox**: the job row is written in the same transaction as the domain change and the audit event, and a relay publishes to Celery only after commit. Publishing directly from inside a request transaction is refused at the service layer, not left to convention. |
| **FR-PLAT-52** | Every metric label is drawn from a bounded set — route **template**, method, status class, Job kind. No label carries an identifier. A resolved path as a label creates one time series per entity, and the failure is silent: the counter keeps working while the monitoring system runs out of memory. |
| **FR-PLAT-53** | **A demo entrance**, reachable in one documented command from a clean checkout: the compose stack, the API, the frontend and a seeded freMTPL2 workspace, with a browser session already authenticated against it. It extends FR-PLAT-37 rather than adding a surface — "one command to a working system" is the same requirement, and a person driving it is the evidence a passing test is not. The whole path hangs off `dev_auth_enabled` (FR-PLAT-1), which is `False` by default and refuses to start in a deployed environment; there is no second switch. A page that lists routes and pre-authenticates a session is a genuine hole if it ever ships. |
| **FR-PLAT-54** | **The entrance carries a guide** to what is testable: each route, its current state, and — the half that matters — what is present but **not** yet functional. It is **derived, never hand-written**: routes from the published contract (`docs/contracts/`, FR-PLAT-48) and state from the roadmap's status table. The guide's purpose is telling a person what to trust, so a stale one is worse than none; keeping it current is a workstream closure step (`CLAUDE.md` §13 step 7). Nothing here restates a capability from memory — the same rule as the generated client, for the same reason. |
| **FR-PLAT-14** | Job history is retained ≥ 13 months with its parameters and result reference — a Job is part of the provenance chain (FR-OVR-3). |
| **FR-PLAT-15** | Scheduled Jobs (monitoring runs, recurring ingestion) are defined as Dagster schedules/sensors and appear in the same Jobs UI as user-submitted work, with `source: system` (`06` FR-GOV-25). |
| **FR-PLAT-16** | A Job that would exceed a configured resource budget (memory, wall clock) is terminated with a typed error naming the budget, not silently OOM-killed. |

### 3.3 Storage

| ID | Requirement |
|---|---|
| **FR-PLAT-17** | **PostgreSQL 16** holds all metadata, artifact bodies (JSONB), the audit log, and job records. Schema changes go through Alembic; every migration is reversible or explicitly marked irreversible with a reason. |
| **FR-PLAT-18** | The **blob store** is S3-compatible (MinIO locally, any S3 in production), content-addressed at `blob/{sha256[:2]}/{sha256}`, with size, media type, and reference count tracked in PostgreSQL. |
| **FR-PLAT-19** | Blobs are immutable and deduplicated: writing identical content is a no-op returning the existing reference (ID-4). |
| **FR-PLAT-20** | Blob garbage collection is **reference-counted and conservative**: a blob is deletable only when no artifact references it and it is older than a configurable grace period (default 30 days). GC runs are audited and dry-runnable. |
| **FR-PLAT-21** | Large uploads use presigned multipart URLs so dataset files do not transit the API process. |
| **FR-PLAT-22** | **Redis** provides the Celery broker, the compiled rating bundle cache (`03` FR-RATE-51), and short-lived response caches. Nothing durable lives only in Redis — every cached value is reconstructible from PostgreSQL and the blob store. |
| **FR-PLAT-23** | Backups: PostgreSQL continuous archiving with PITR (RPO ≤ 15 min, NFR-OVR-7); blob store versioning and replication. A documented, tested restore procedure is part of the deliverable, not an afterthought. |

### 3.4 Secrets

| ID | Requirement |
|---|---|
| **FR-PLAT-24** | Secrets are stored in a pluggable backend: environment variables (local), or an external manager (Vault, AWS/GCP secret managers) in production. The platform never stores a secret value in PostgreSQL. |
| **FR-PLAT-25** | Secrets are referenced as `secret:<slug>` in Source configs, webhook routes, and service configuration, and resolved only at the moment of use (R3). |
| **FR-PLAT-26** | A secret value is never returned by any API, written to any log, included in any artifact, or recorded in any audit event — only its slug and the fact of its use (R3, `06` FR-GOV-26). |
| **FR-PLAT-27** | Secret creation, rotation, and deletion are audited by slug; secret *reads* by the platform at point of use are audited at a summary level (which secret, by which job), not per access. |

### 3.5 Environments

| ID | Requirement |
|---|---|
| **FR-PLAT-28** | An **Environment** is a first-class object with a name, a description, a promotion order, and its own live Rating Version deployments (`03` FR-RATE-50). The shipped set is `dev → uat → prod`; additional environments are configurable. |
| **FR-PLAT-29** | Promotion order is enforced: a Rating Version cannot deploy to `prod` without a prior successful deployment to `uat` (`06` §3.3 evidence table), unless the workspace policy explicitly permits skipping with a recorded reason. |
| **FR-PLAT-30** | Environments have independent Service Account scopes, rate limits, and monitoring configuration. A `uat` key can never score against `prod`. |
| **FR-PLAT-31** | Environment configuration (rate limits, sampling rates, feature flags) is a Setting resolved by the precedence in §3.8 and is audited on change. |

### 3.6 Deployment and packaging

| ID | Requirement |
|---|---|
| **FR-PLAT-32** | The platform ships as container images: `api`, `worker`, `scheduler` (Dagster), `frontend`, plus dependencies (PostgreSQL, Redis, MinIO, an OIDC provider for local use). `deploy/docker-compose.yml` brings up a working stack with seeded demo data (R2). |
| **FR-PLAT-33** | A Helm chart / Kubernetes manifests are provided for production, with independently scalable API, scoring, and compute worker pools. |
| **FR-PLAT-34** | The scoring API is independently deployable and horizontally scalable, and can run **without** the compute workers present — a pricing outage must not be caused by a modelling workload. |
| **FR-PLAT-35** | Database migrations run as an explicit pre-deploy step, never automatically on application start, and are forward-compatible with the previous application version so a rolling deploy is safe. |
| **FR-PLAT-56** | **A deployment is bound to one tenant, and says so out loud.** The tenant identifier is deployment configuration, the database carries the same identifier in a single-row marker written at first migration, and the application **refuses to start when they disagree** — a startup failure, not a warning and not a log line. Pointing one tenant's application at another tenant's database is the one operational mistake ADR-0006's guarantee cannot survive, and it is exactly the mistake a restore, a copied `.env` or a misedited Helm value makes easy. The same check covers object storage and the broker where their configuration is per tenant. Owned by **W14**. |
| **FR-PLAT-36** | CI runs path-filtered per component (`.github/workflows/`), and every merge produces reproducible, tagged, signed images with an SBOM. |
| **FR-PLAT-37** | The demo stack seeds a freMTPL2-based example workspace end to end — dataset, validation, models, rating version — so a new user sees a working system in one command (`examples/`). |

### 3.7 Observability

| ID | Requirement |
|---|---|
| **FR-PLAT-38** | Structured JSON logging everywhere with `trace_id`, `workspace_id`, `principal_id`, `job_id`, and the entity reference where applicable (R4). |
| **FR-PLAT-39** | OpenTelemetry tracing spans the API request, the queue hop, the worker, and `pricing-core` calls, with span attributes carrying artifact references. |
| **FR-PLAT-40** | Metrics exposed in Prometheus format: request rate/latency/error by route, scoring latency percentiles by environment and rating version, job queue depth and duration by kind, cache hit rate, and blob store usage. |
| **FR-PLAT-41** | Health endpoints: `/healthz` (liveness), `/readyz` (readiness including database, Redis, and blob store reachability), and `/version` (image tag, commit, schema version). The scoring service's readiness additionally requires a compiled bundle in cache. |
| **FR-PLAT-42** | Errors are reported with the `trace_id` visible to the user, so a support conversation starts with an identifier rather than a screenshot. |

### 3.8 Configuration

| ID | Requirement |
|---|---|
| **FR-PLAT-43** | Settings resolve by precedence: **environment variable → workspace setting → platform default**. The effective value and its source are inspectable by an Admin. |
| **FR-PLAT-44** | Settings are typed and validated at startup; an invalid setting prevents startup with a clear message rather than failing at first use. |
| **FR-PLAT-45** | Workspace settings include: currency, locale/timezone for display, default validation thresholds, trace sampling rate, approval policy reference, retention windows, model complexity thresholds (`modelling.max_factor_count`, `modelling.min_exposure_per_parameter` — both unset by default, `02` FR-MODEL-81), and feature flags (e.g. `sql_validation_check_enabled`, `expression_objectives_enabled`). |
| **FR-PLAT-46** | Feature flags gate genuinely optional or risk-bearing capabilities (`01` §4.5, `02` FR-MODEL-75) and default to the safe value. `expression_objectives_enabled` stays off for the whole of Phase 1, because the capability behind it does not exist until Phase 2 (OQ-MODEL-1, decided 2026-08-15). |

### 3.9 API surface

| ID | Requirement |
|---|---|
| **FR-PLAT-47** | The API implements `00` §5 exactly: `/api/v1`, cursor pagination, RFC 9457 problem responses with stable `code`s, `If-Match` optimistic concurrency, and `Idempotency-Key` support. |
| **FR-PLAT-48** | OpenAPI 3.1 is generated from the Pydantic models (ADR-0002) and published at `/openapi.json`; the committed copy in `docs/contracts/openapi/` is regenerated in CI and a drift fails the build. |
| **FR-PLAT-49** | Rate limiting is applied per Principal and per environment, with scoring limits configured separately from management-API limits, and `429` responses carrying `Retry-After`. |
| **FR-PLAT-50** | Webhooks (alert routing, deployment notifications) are signed with an HMAC over the payload, delivered with retries and exponential backoff, and their delivery status is observable. |

---

## 4. Data contracts

### 4.1 `Job`

```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "kind": "model.fit",
  "status": "queued | running | succeeded | failed | cancelled",
  "queue": "compute",
  "submitted_by": {"kind": "user", "id": "uuid"},
  "source": "ui | api | schedule | system",
  "idempotency_key": "…",
  "parameters": {"model_spec_id": "uuid", "seed": 20260814},
  "progress": {"fraction": 0.62, "stage": "boosting round 1240/2000",
               "counters": {"rows": 4_821_904, "rounds": 1240}},
  "result": {"kind": "artifact", "ref": "model:motor-ad-frequency@7"},
  "error": null,
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "progress_at": "2026-08-14T09:03:11Z",
  "stalled": false,
  "queued_at": "2026-08-14T09:00:00Z",
  "started_at": "2026-08-14T09:00:04Z",
  "finished_at": null,
  "resource_budget": {"memory_gb": 32, "wall_clock_s": 3600},
  "retries": {"attempted": 0, "max": 3, "policy": "infrastructure_only"}
}
```

`progress_at` and `stalled` were added in W2 (2026-08-14). NFR-PLAT-3 requires a running
Job with no progress for the configured window to be *treated as stalled and flagged*, and
§4.1 had nowhere for that flag to live. `progress_at` is the time of the last progress
report — not `started_at`, which cannot answer "is it still saying anything" for a Job that
has legitimately run for an hour. `stalled` is derived from it on read rather than stored,
because a stored flag needs a sweeper to clear it and would be wrong between sweeps.

Failure shape:

```json
{
  "error": {
    "code": "GLM_DID_NOT_CONVERGE",
    "message": "GLM failed to converge after 200 iterations.",
    "retryable": false,
    "detail": {"factors_suspected": ["vehicle_group_rated"], "max_gradient": 4.1e-3},
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
  }
}
```

### 4.2 `Environment`

```json
{
  "name": "prod",
  "description": "Production quoting",
  "promotion_order": 3,
  "requires_prior_environment": "uat",
  "live_deployments": [{"rating_version_ref": "rating_version:motor-gb@27",
                        "deployed_at": "2026-10-01T06:00:00Z", "bundle_hash": "sha256:…"}],
  "settings": {"trace_sampling_rate": 0.01, "rate_limit_rps": 500,
               "shadow": {"enabled": true, "candidate_ref": "rating_version:motor-gb@28",
                          "traffic_fraction": 0.05}}
}
```

### 4.3 `ServiceAccount` / API key

```json
{
  "slug": "quote-engine-prod",
  "environments": ["prod"],
  "permissions": ["score:execute"],
  "key": {"prefix": "gip_prod_7f2a", "created_at": "2026-01-05T09:00:00Z",
          "expires_at": "2027-01-05T09:00:00Z", "last_used_at": "2026-11-30T22:14:03Z",
          "rotation": {"successor_prefix": null, "overlap_until": null}},
  "rate_limit_rps": 500
}
```

The key value itself appears exactly once, in the creation response (FR-PLAT-3).

### 4.4 `Setting` resolution

```json
{
  "key": "validation.psi_warn_threshold",
  "effective_value": 0.10,
  "resolved_from": "workspace",
  "candidates": [
    {"source": "env", "value": null},
    {"source": "workspace", "value": 0.10},
    {"source": "default", "value": 0.10}
  ],
  "type": "float", "constraints": {"min": 0.0, "max": 1.0}
}
```

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/jobs?status=&kind=&submitted_by=` | List jobs |
| `GET` | `/api/v1/jobs/{id}` | Job detail with progress and result |
| `GET` | `/api/v1/jobs/{id}/logs` | Job logs (paged, streamable) |
| `POST` | `/api/v1/jobs/{id}/cancel` | Cooperative cancellation (FR-PLAT-9) |
| `GET` | `/api/v1/jobs/{id}/events` | SSE stream of progress updates |
| `GET`/`POST` | `/api/v1/environments` | List / create environments |
| `PUT` | `/api/v1/environments/{name}/settings` | Update environment settings (audited) |
| `POST` | `/api/v1/service-accounts` | Create a service account + key (key shown once) |
| `POST` | `/api/v1/service-accounts/{id}/rotate` | Rotate with an overlap window |
| `DELETE` | `/api/v1/service-accounts/{id}/keys/{prefix}` | Revoke |
| `GET`/`PUT` | `/api/v1/settings` | Read effective settings with sources; update workspace settings |
| `POST` | `/api/v1/blobs/upload-url` | Presigned multipart upload (FR-PLAT-21) |
| `GET` | `/api/v1/blobs/{sha256}` | Download (permission-checked, redirect to presigned URL) |
| `GET` | `/healthz`, `/readyz`, `/version` | Health and version (FR-PLAT-41) |
| `GET` | `/openapi.json` | Generated OpenAPI 3.1 (FR-PLAT-48) |
| `GET` | `/metrics` | Prometheus metrics (FR-PLAT-40) |
| `GET` | `/api/v1/demo/guide` | What is testable today, derived (FR-PLAT-54). **404 unless `dev_auth_enabled`** |

> **`/metrics` scope, 2026-08-15 (W4).** FR-PLAT-40 names five families. Three are emitted:
> request rate/latency/error by route template, job queue depth and duration by kind, and
> blob store usage. Two are **not**, because what they measure does not exist yet —
> scoring latency by environment and rating version arrives with the scoring path (W11),
> and there is no cache to report a hit rate for.
>
> They are absent rather than exposed as zero. A dashboard panel reading zero because
> nothing reports is indistinguishable from one reading zero because nothing is wrong, and
> the second reading is the one an operator will make at three in the morning.

**Error codes owned by this module:** `UNAUTHENTICATED`, `TOKEN_EXPIRED`,
`API_KEY_INVALID`, `API_KEY_EXPIRED`, `ENVIRONMENT_SCOPE_DENIED`, `JOB_NOT_CANCELLABLE`,
`JOB_RESOURCE_BUDGET_EXCEEDED`, `JOB_HANDLER_NOT_REGISTERED`, `JOB_HANDLER_FAILED`,
`IDEMPOTENCY_KEY_CONFLICT`,
`RATE_LIMITED`, `BLOB_NOT_FOUND`, `SECRET_NOT_FOUND`, `SETTING_INVALID`,
`PROMOTION_ORDER_VIOLATION`, `MIGRATION_REQUIRED`, `CONFLICT_STALE_WRITE`.

`CONFLICT_STALE_WRITE` was declared in `00` §5.4 from Phase 0 and belonged to no module's
list until 2026-08-17. It is `07`'s because FR-PLAT-47 owns "the API implements `00` §5
exactly" — the convention is platform-wide, not one module's. Two workstreams recorded it as
still absent from the error registry (W2, then W4) before the first routes that require the
header arrived with the model lifecycle in W5, which is the only reason it was findable
rather than forgotten.

`JOB_HANDLER_NOT_REGISTERED` and `JOB_HANDLER_FAILED` were added in W2 (2026-08-14). The worker dispatches on Job
kind, and the platform is deployable before every kind has an implementation — the scoring
service runs without the compute pool (FR-PLAT-34), and Phase 1a ships the Job machinery
before the `model.*` handlers exist. A kind with no handler is a deployment error and must
fail the Job with a code naming it, rather than leaving the Job `queued` for ever with
nothing to explain why.

### 5.2 Backend interfaces

```python
# backend/app/platform/jobs.py
async def submit(kind: JobKind, params: BaseModel, principal: Principal,
                 *, idempotency_key: str | None = None,
                 queue: str | None = None) -> Job
async def cancel(job_id: UUID, principal: Principal) -> Job

# The worker-side contract that bridges to pricing-core (ADR-0001)
class JobProgress(ProgressCallback):
    def update(self, fraction: float, stage: str, **counters: int) -> None: ...
    def check_cancelled(self) -> None: ...        # raises JobCancelled

# backend/app/platform/blobs.py
async def put(content: bytes | AsyncIterator[bytes], media_type: str) -> BlobRef
async def presign_upload(media_type: str, parts: int) -> PresignedUpload
async def open(ref: BlobRef) -> AsyncIterator[bytes]

# backend/app/platform/secrets.py
async def resolve(ref: str) -> SecretValue        # never logged, never returned (R3)

# backend/app/platform/settings.py
def get(key: str, workspace_id: UUID) -> SettingResolution
```

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Jobs | `/jobs` | Filterable list with kind, status, progress bars, submitter, duration; live updates via SSE |
| Job detail | `/jobs/:id` | Parameters, progress stages, logs with `trace_id`, result link, cancel action, error detail |
| Environments | `/admin/environments` | Live deployments per environment, settings, shadow configuration, promotion order |
| Service accounts | `/admin/service-accounts` | Keys with prefix, expiry, last used; create/rotate/revoke with one-time key display |
| Settings | `/admin/settings` | Effective values with their resolution source and constraints |
| System status | `/admin/status` | Component health, queue depths, cache hit rates, blob store usage, schema version |
| **Demo entrance** | `/demo` | What is testable today: views built against those a spec declares, endpoints published against those declared, workstream state, and the routes that can be opened without an id. Derived on every request (FR-PLAT-53, FR-PLAT-54); absent where `dev_auth_enabled` is false |

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | User | Triggers a long operation in the UI |
| 2 | Backend | Validates, authorises (`06`), creates a Job, returns `202` + `Location` (R1) |
| 3 | Frontend | Subscribes to `/jobs/{id}/events`; shows progress inline where the action was taken |
| 4 | Worker | Picks the Job from its queue, sets `running`, calls `pricing-core` with a `JobProgress` callback |
| 5 | Worker | Persists result artifacts and blobs; sets `succeeded` with the result reference |
| 6 | Backend | Emits the Audit Event for the resulting state change (`06` R2) |
| 7 | Frontend | Navigates to the produced artifact |

Cancellation, retry, and failure paths follow FR-PLAT-9/11.

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What |
|---|---|
| `06-governance` | Authorisation decisions and the audit sink for platform-level actions (key rotation, settings changes, GC runs) |

### 7.2 Provides

| To | What |
|---|---|
| All modules | Jobs, blob storage, secrets, settings, environments, authentication, tracing, health |
| `03-rating-engine` | The bundle cache, environment objects, service-account scoping, and rate limiting on the scoring path |
| `05-monitoring` | Scheduling (Dagster), notification channels, operational metrics |

### 7.3 Contract note

`pricing-core` never imports anything from this module (ADR-0001, DEP-3). The bridge is
the `ProgressCallback` protocol, defined in `pricing-core` and *implemented* here.

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **FastAPI** | The API surface, dependency-injected auth, `202`+Job pattern, SSE progress streams | Router organisation at ~200 endpoints; SSE in FastAPI; failing closed on auth by default |
| **Pydantic v2** | Settings validation, request/response models, OpenAPI generation | `pydantic-settings` for typed configuration with sources |
| **SQLAlchemy 2.x + Alembic** | Metadata persistence, migrations | Forward-compatible migrations for rolling deploys (FR-PLAT-35); reversibility discipline |
| **PostgreSQL 16** | All metadata, JSONB artifacts, audit, jobs | Connection pooling for async workloads, partitioning, PITR configuration |
| **Celery + Redis** | Job execution, queue routing, cancellation | Queue routing by kind, revocation semantics, worker memory limits, result backends, and the **transactional outbox** pattern that FR-PLAT-51 requires because Celery cannot enlist in the database transaction |
| **Dagster** | Scheduled pipelines surfaced as Jobs | Schedules/sensors, backfills, resource configuration, integrating with the platform Job model |
| **MinIO / S3** | Content-addressed blobs, presigned multipart | Presigned URL security, lifecycle rules, versioning, reference-counted GC |
| **OIDC (Keycloak or similar)** | User authentication | Authorisation code + PKCE for an SPA, token refresh, claim mapping, running a local provider in compose |
| **OpenTelemetry** | Distributed tracing across API → queue → worker | Context propagation through Celery, span attributes, sampling |
| **Prometheus / Grafana** | Metrics and dashboards | Histogram buckets for p99 latency, queue-depth alerting |
| **Docker Compose / Helm** | Local stack and production packaging | Compose parity with production (R2), independently scalable pools, image signing and SBOM generation |
| **GitHub Actions** | CI with path filters | Per-component pipelines, generated-artifact drift checks (FR-PLAT-48) |

New skills this spec adds to `skills-map.md`: Celery cancellation and resource budgeting;
SSE progress streaming in FastAPI; presigned multipart uploads; OIDC PKCE for SPAs;
forward-compatible migrations for rolling deploys; reference-counted blob GC.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-PLAT-1** | API metadata reads p95 < 300 ms (NFR-OVR-4); the scoring path is specified separately in `03` (NFR-RATE-1). |
| **NFR-PLAT-2** | Job submission to `running` in < 5 s when a worker slot is free; queue depth and wait time are observable. |
| **NFR-PLAT-3** | Progress updates arrive at least every 5 s for a running Job, or the Job is treated as stalled and flagged. |
| **NFR-PLAT-4** | The compose stack starts to a usable seeded state in < 5 min on a developer laptop (R2, FR-PLAT-37). |
| **NFR-PLAT-5** | RPO ≤ 15 min, RTO ≤ 4 h (NFR-OVR-7), with a restore procedure exercised in CI against a synthetic backup at least monthly. |
| **NFR-PLAT-6** | Rolling deploys cause no failed requests; the previous application version runs against the migrated schema (FR-PLAT-35). |
| **NFR-PLAT-7** | Secrets never appear in logs, artifacts, audit events, API responses, or error messages — verified by an automated scan in CI over test-run log output (R3). |
| **NFR-PLAT-8** | Container images have no `HIGH`/`CRITICAL` CVEs at release, are signed, and ship an SBOM (NFR-OVR-8). |
| **NFR-PLAT-9** | The scoring service runs and serves with the compute worker pool entirely absent (FR-PLAT-34). |
| **NFR-PLAT-11** | **A Model scores in a process where the libraries that *fit* models cannot be imported — proven by scoring in a subprocess with `glum`, `scikit-learn`, `celery` and `dagster` made unimportable, not by review.** (OQ-PLAT-3, decided 2026-08-18.) One image with a role flag ships through Phases 1–2 and a separate scoring image from Phase 3, and the only thing that can make that split cheap later is that the scoring path never grew a fitting dependency in between. NFR-PLAT-9 states the runtime property against the *worker pool*; this states it against the *dependency set*, which is what a second image would actually have to shed. `xgboost` and `lightgbm` are deliberately **not** on the forbidden side: `02` FR-MODEL-62 scores a GBM by loading its JSON booster, so a boosting library is a scoring dependency by design — what the split sheds is the libraries that fit. **An import-linter contract is the wrong instrument here, and was tried first.** `glum` and `sklearn` are already imported at their call sites rather than at module scope — inside `fit_glm`, `propose_banding` and `propose_grouping` — which is exactly the discipline this requirement wants; import-linter reads the AST and counts a function-scope import like any other, so a contract over `pricing_core.modelling.predict` reports four violations against code that is already correct, and the only ways to green it are to weaken it or to move modules that have no other reason to move. The property is a runtime one, so the check creates the runtime. The slice that builds the scoring API (Phase 2) extends the same test to that entry point rather than adding a second mechanism. |
| **NFR-PLAT-10** | Trace context propagates end to end for ≥ 99 % of requests, verified by a CI check that asserts a `trace_id` appears in worker logs for a traced API call (R4). |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-PLAT-1** | ~~Celery or a Postgres-backed queue?~~ **DECIDED 2026-08-14: Celery.** The maintainer chose Celery over the Postgres-queue prototype this spec had recommended. That is a reasonable call — Celery is mature, Redis is already in the stack, and the throughput headroom is real. It does, however, mean the transactional-enqueue property a Postgres queue would have given for free must now be built: `FR-PLAT-51` requires a transactional outbox, because `06` R2 makes an un-audited job a correctness problem rather than an inconvenience. |
| **OQ-PLAT-2** | Does Dagster earn its place, or should scheduled work be Celery beat plus a thin scheduler? Dagster brings partitioned assets and backfills that `05` genuinely wants (NFR-MON-8), and a substantial operational surface. |
| **OQ-PLAT-3** | ~~Should the scoring service be a separate deployable *application*, rather than the same image run with a different role?~~ **DECIDED 2026-08-18: one image with a role flag through Phases 1–2, a separate scoring image from Phase 3** — and the thing that makes the later split cheap is specified now as `NFR-PLAT-11`, which scores a Model in a process where the fitting stack cannot be imported, and so stops that path growing a dependency the split would later have to shed. *An import-linter contract was tried first and is the wrong instrument — the requirement records why.* The image itself is Phase 3 (W14's successor); the boundary is enforced from today. |
| **OQ-PLAT-4** | How are workspace-level resource quotas expressed (concurrent compute jobs, total storage)? **Half of this question is now answered:** ADR-0006 makes every deployment single-tenant, so a quota never protects one insurer from another — it protects a tenant's own scoring path from its own modelling workload. What remains open is whether that needs expressing per workspace at all, or whether the worker pool split (FR-PLAT-34) already does it. |
| **OQ-PLAT-6** | ~~How does the browser authenticate to the API — authorization-code + PKCE in the SPA, or a BFF session cookie?~~ **DECIDED 2026-08-15: PKCE in the SPA for Phases 1–2**, specified as FR-PLAT-55 and owned by W6b. Revisit at Phase 3 if a deployment requires that no token exist in the browser at all. |
| **OQ-PLAT-5** | Do we ship a bundled OIDC provider (Keycloak) in the production compose stack as a supported deployment, or is an external IdP always required outside local development? Bundling lowers the barrier for a small insurer and makes us responsible for an identity provider. |
| **OQ-PLAT-7** | A `PlatformError` raised inside a Job handler loses its `.code` before it reaches storage — `worker/tasks.py`'s generic `except Exception` stores `JobError(code="JOB_HANDLER_FAILED", message=f"{type(exc).__name__}: {exc}")` for every unexpected exception, `PlatformError` included, and `str(exc)` carries the error's title/detail rather than its code. No test going through `execute_job` can assert on a specific handler-raised error code today. Should the generic handler special-case `PlatformError` to preserve `.code`? Raised 2026-08-19 (W5, the GLM-approximation-as-a-Model slice): Task 4's negative tests had to invoke the handler directly to work around it. Recommendation on file: yes — add a dedicated `except PlatformError` clause before the generic one, storing the handler's own code. |
