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
| **FR-PLAT-1** | Users authenticate via **OIDC** against an external identity provider (Keycloak, Entra ID, Okta, Google). The platform stores no user passwords. A local development provider ships with the compose stack (R2). *Amended 2026-08-23: the last sentence was written in the present indicative and read as a delivered fact, which it is not — `deploy/docker-compose.yml` runs postgres, redis and minio and no provider. The obligation is unchanged and is now stated with an owner as `FR-PLAT-58`. What is built is the verification half (`backend/src/app/auth/oidc.py`, asymmetric algorithms only) and the production half (a `prod` deployment refuses to start with no issuer); what is outstanding is the local container. `(R2)` cites §1's rule that the full stack runs locally, not a release.* |
| **FR-PLAT-2** | Sessions use short-lived access tokens with refresh; the SPA holds tokens in memory, never in `localStorage`. |
| **FR-PLAT-3** | **Service Accounts** authenticate with API keys (prefix-identifiable, hashed at rest, never retrievable after creation). Keys carry an expiry, are rotatable with an overlap window, and are scoped to named environments and the scoring permission set only (`06` FR-GOV-6). |
| **FR-PLAT-4** | Identity provider claims map to platform users on first login; group-to-role mapping is configurable (`06` OQ-GOV-2). A user with no mapped role gets no access, not default access. |
| **FR-PLAT-5** | All API traffic is TLS 1.3; the platform refuses to start in `prod` mode without TLS termination configured (NFR-OVR-8). |
| **FR-PLAT-6** | Failed authentication, key creation/rotation/revocation, and session anomalies are audited (`06` FR-GOV-20). |
| **FR-PLAT-55** | The **browser** authenticates by OIDC **authorization code with PKCE** (OQ-PLAT-6, decided 2026-08-15), against the same provider and discovery document the API verifies against (FR-PLAT-1). The SPA is a *public* client: no client secret exists in it, the code verifier never leaves the browser, and the access token is held in memory only (FR-PLAT-2). Renewal is silent and failure to renew logs the session out rather than retrying indefinitely — an expired session that looks logged in is how a user comes to believe the platform lost their work. The API side is unchanged: it verifies a bearer token and knows nothing about how the browser obtained it. **The development identity headers (`x-dev-principal-id`, `x-dev-workspace-id`, injected by the frontend dev proxy) are not part of this flow and never authenticate anything outside `local`/`dev`** — they hang off `dev_auth_enabled`, which is `False` by default and refuses to start in a deployed environment. Owned by **W6b**. |
| **FR-PLAT-62** | *(appended 2026-08-23, W6b slice-map backlog item 2)* **A Workspace is a named, addressable entity.** It exists today only as a `workspace_id` column: there is no `workspaces` table, so a workspace has no name, and every surface that would show one shows a UUID. A `workspaces` row carries `id`, `slug`, `name` and `created_at`; `workspace_members` and `workspace_settings` reference it; and the migration backfills a row for **every distinct `workspace_id` already stored anywhere**, not only the ones with a membership — an orphaned id is exactly the case a foreign key must not discover after the fact. This is the prerequisite the backlog item did not see: a selector with nothing to render is not a UI gap, and specifying the control before the entity would have specified something undeliverable. Owner: **W32** — a table and a migration, not a browser. |
| **FR-PLAT-63** | *(appended 2026-08-23, W6b slice-map backlog item 2)* **A principal with more than one workspace membership chooses which one it is acting in, and the platform verifies the choice.** The memberships are readable from the identity endpoint `06` §5.1 declares, each carrying FR-PLAT-62's name. Four obligations, all transport-independent: the selection is **checked against the principal's own memberships on every request**, never trusted — a value naming a workspace the principal does not belong to is refused with `WORKSPACE_SCOPE_DENIED`, and a principal with several memberships and no selection is refused with `WORKSPACE_SELECTION_REQUIRED` rather than defaulted into one; a principal with exactly **one** membership needs no selection and a Service Account, which has exactly one by construction, never sends one; and **a switch is audited into both chains** — `06` FR-GOV-24 chains audit events per workspace, so recording only the workspace entered leaves the workspace left with no record that the principal stopped acting there, which is the half an auditor reconstructing "who was acting where, and when did they stop" needs. The first selection after login has no chain to leave and writes one event. **How the choice reaches the API was deliberately not decided here** — `OQ-PLAT-9`, decided 2026-08-23 as FR-PLAT-65: a verified `Workspace-Id` request header. The invariant the code carries against the obvious answer (a header-supplied workspace "would make the scope a claim rather than a fact") was answered rather than overridden — it refuses *unverified* scope, and a choice among memberships the platform already holds is not unverified. Until that lands the API refuses rather than guesses, which is what it does today. *One code defect rode with this: that refusal's user-facing message named the workstream it was waiting for, and named the wrong one — it said the capability arrives with W3, which closed on 2026-08-14 without it. **Corrected 2026-08-23 with the transport decision**; the message now names the header and the workstream that builds it.* Owner: **W32** for the API half, `W6b-11` for the shell control, which stays blocked until it lands. |
| **FR-PLAT-65** | *(appended 2026-08-23, OQ-PLAT-9)* **The chosen workspace travels as a verified `Workspace-Id` request header.** A principal with several memberships names one per request; the request-scope dependency checks that value against the memberships the authenticated identity already carries and refuses anything else with `WORKSPACE_SCOPE_DENIED`. **This does not make the scope a claim.** The invariant the code states — that a header-supplied workspace "would make the scope a claim rather than a fact" — refuses *trusting* the caller, and a choice among facts the platform already holds is not a claim; what would break it is defaulting, which FR-PLAT-63 forbids and this row does not do. A principal with several memberships and **no** header is refused with `WORKSPACE_SELECTION_REQUIRED`, so a forgotten header is a refusal and never someone else's data — refusing rather than defaulting is what makes a header safe here. **The header is declared on the route, optional in the published contract and required in the handler**, which is the shape `If-Match` already uses (`00` §5.4): declaring it puts it in the generated client instead of behind the route's back, while enforcing it in the handler keeps the refusal a typed platform error rather than a `422` outside the error catalogue. A principal with exactly **one** membership sends nothing and is unaffected, and a Service Account, having one by construction, never sends it. The name is deliberately **not** `x-dev-workspace-id`, the development header FR-PLAT-55 confines to `local`/`dev` — a production selector one word away from a dev header is a footgun — and it is unprefixed like `Idempotency-Key` and `If-Match` rather than reviving the `X-` convention RFC 6648 retired. A switch is audited into both chains under FR-PLAT-63, which is otherwise unchanged. A path prefix (`/workspaces/{id}/…`) is the better design in the abstract and is refused here only on cost: every route in five specs plus a client regeneration, to carry what one verified header carries. Owner: **W32**; `W6b-11`'s shell control is unblocked by this decision and still waits on the backend half. |
| **FR-PLAT-58** | *(appended 2026-08-23 — decides `OQ-PLAT-5`'s local half)* **A local OIDC provider ships with the compose stack, behind an opt-in profile.** `FR-PLAT-1` has asserted since Phase 0 that one does, and none is there. That was a considered position rather than an oversight — `deploy/docker-compose.yml` carries its own rule, *"an unused container in the compose file is a claim the platform does not yet support"* — and it stops being tenable the moment `FR-PLAT-55` puts a real login in the browser. The provider therefore arrives **behind a compose profile** rather than in the default `docker compose up`: a contributor running the test suites starts the same three containers as today, and a contributor working on the browser login starts four. It imports a **checked-in realm** — a public client with PKCE and no secret, the dev-server redirect URIs, and an API audience equal to the configured `oidc_audience` — so the flow is reproducible rather than hand-configured, which is what turns an identity misconfiguration into a review comment instead of a support thread. **Its demo users must resolve into the seeded workspace, and today they cannot**: `examples/fremtpl2/seed.py` mints principals with fresh identifiers and grants them *role assignments*, while `authenticate_bearer` keys a user on `(issuer, subject)` and reads workspaces from the membership table — so a real login through the provider would authenticate successfully into **zero** workspaces. `FR-PLAT-4` makes that the correct refusal and it is still a broken demo, so the seed grants membership keyed on the realm's issuer and subject. This is an **alternative** to `dev_auth_enabled`, never a replacement: both test suites keep running with no container, because a test suite that needs an identity provider running is one that stops being run. Owned by **W6b**. |

### 3.2 Jobs

| ID | Requirement |
|---|---|
| **FR-PLAT-7** | A **Job** has the lifecycle `queued → running → (succeeded \| failed \| cancelled)`, with `queued_at`, `started_at`, `finished_at`, the submitting Principal, the Job Kind, its input parameters, and a result reference. |
| **FR-PLAT-8** | Jobs report **structured progress**: a fraction complete, a current-stage label, and optional counters (rows processed, rules evaluated, boosting rounds). `pricing-core` reports through the injected `ProgressCallback` (ADR-0001); the worker translates it into Job state. |
| **FR-PLAT-9** | Jobs are **cancellable**. Cancellation is cooperative: the callback signals cancellation and `pricing-core` returns at the next checkpoint. A cancelled Job leaves no partially-visible artifact (`01` NFR-DATA-10). |
| **FR-PLAT-10** | Job logs are captured, retained with the Job, and viewable in the UI with the `trace_id` (R4). Logs never contain secrets or full quote inputs (R3, `06` FR-GOV-26). |
| **FR-PLAT-11** | Failed Jobs record a typed error code, a human message, and — where the failure is deterministic (bad spec, invalid rule) — the field-level cause. Infrastructure failures are retried with exponential backoff; deterministic failures are not retried. |
| **FR-PLAT-12** | Jobs are **idempotent by key**: a submission carrying an `Idempotency-Key` that matches a Job from the last 24 h returns the original Job (`00` §5.4). *Amended 2026-08-23 (OQ-PLAT-8): the **"from the last 24 h" clause is withdrawn**. It was never implemented — `platform.jobs.submit()` has always applied no window — and a window is the one thing a key must not have, because the duplicate a key exists to prevent is precisely the one that arrives late. Keys are permanent, with a single release on terminal failure: the semantics are FR-PLAT-64, which supersedes this row's window and nothing else about it.* |
| **FR-PLAT-13** | Jobs are routed to queues by Kind, with per-queue worker pools sized independently: `compute` (fitting, certification, optimisation — few, large workers), `scoring` (batch scoring — many, moderate), `io` (ingestion, exports), `default` (everything else). |
| **FR-PLAT-51** | **Job enqueue is transactionally safe.** Celery is the chosen broker (OQ-PLAT-1, decided 2026-08-14), which does **not** enlist in the database transaction — a task can be published to Redis and the surrounding transaction then roll back, leaving a worker acting on state that was never committed. Since audit writes share the caller's transaction (`06` R2), this would produce work with no audit record. Jobs are therefore enqueued through a **transactional outbox**: the job row is written in the same transaction as the domain change and the audit event, and a relay publishes to Celery only after commit. Publishing directly from inside a request transaction is refused at the service layer, not left to convention. |
| **FR-PLAT-52** | Every metric label is drawn from a bounded set — route **template**, method, status class, Job kind. No label carries an identifier. A resolved path as a label creates one time series per entity, and the failure is silent: the counter keeps working while the monitoring system runs out of memory. |
| **FR-PLAT-53** | **A demo entrance**, reachable in one documented command from a clean checkout: the compose stack, the API, the frontend and a seeded freMTPL2 workspace, with a browser session already authenticated against it. It extends FR-PLAT-37 rather than adding a surface — "one command to a working system" is the same requirement, and a person driving it is the evidence a passing test is not. The whole path hangs off `dev_auth_enabled` (FR-PLAT-1), which is `False` by default and refuses to start in a deployed environment; there is no second switch. A page that lists routes and pre-authenticates a session is a genuine hole if it ever ships. |
| **FR-PLAT-54** | **The entrance carries a guide** to what is testable: each route, its current state, and — the half that matters — what is present but **not** yet functional. It is **derived, never hand-written**: routes from the published contract (`docs/contracts/`, FR-PLAT-48) and state from the roadmap's status table. The guide's purpose is telling a person what to trust, so a stale one is worse than none; keeping it current is a workstream closure step (`CLAUDE.md` §13 step 7). Nothing here restates a capability from memory — the same rule as the generated client, for the same reason. |
| **FR-PLAT-14** | Job history is retained ≥ 13 months with its parameters and result reference — a Job is part of the provenance chain (FR-OVR-3). |
| **FR-PLAT-15** | Scheduled Jobs (monitoring runs, recurring ingestion) are defined as **schedule rows that the scheduler tick submits** (FR-PLAT-61) and appear in the same Jobs UI as user-submitted work, with `source: system` (`06` FR-GOV-25). *Amended 2026-08-23 (OQ-PLAT-2): this read "are defined as Dagster schedules/sensors". Dagster is dropped. The id keeps its meaning because what it requires never depended on the orchestrator — a scheduled run is a Job in the Jobs UI with `source: system` — and only the mechanism moved, to FR-PLAT-61.* |
| **FR-PLAT-16** | A Job that would exceed a configured resource budget (memory, wall clock) is terminated with a typed error naming the budget, not silently OOM-killed. |
| **FR-PLAT-61** | *(appended 2026-08-23, OQ-PLAT-2)* **Scheduled work is a tick, not a second orchestrator.** A single periodic Celery beat task — the **scheduler tick** — wakes on a fixed interval, computes which schedules are *due*, and submits ordinary platform Jobs through the outbox (FR-PLAT-51). It executes no pricing work itself, so a scheduled run is indistinguishable from a user-submitted one everywhere downstream: the same Job record, queue routing, progress, logs, cancellation and audit (FR-PLAT-7..14). **Schedules are period-anchored, not "every N minutes since boot".** A schedule carries a period, an anchor, and the last period for which a Job was submitted; the tick submits one Job per whole period between that mark and now, so a tick that does not run — a restart, an outage, a stopped beat process — catches up on the next one rather than silently skipping. **The idempotency key is `(schedule_id, period)`** (FR-PLAT-12), which is what makes a duplicated tick, an overlapping tick or two beat processes harmless. It is also why re-ticking does **not** recover a period whose Job *failed*: an existing key returns the existing Job whatever its status, and the semantics of re-submission under a spent key were `OQ-PLAT-8`, decided 2026-08-23 as FR-PLAT-64: a period whose Job failed terminally **releases** its key, so the next tick re-submits that period as a fresh Job, while a period that succeeded or was cancelled stays done. **A schedule created after the fact has no implicit history** — the anchor defaults to creation time, so no earlier period is ever due by inference. Earlier periods come from an explicit, bounded **backfill request**: a range, one Job per period, keyed on the request so it cannot collide with the tick. That is the mechanism `05` NFR-MON-8 needs, and the only one. **Event-triggered runs are not polled**: where a platform event should start a Job — a deployment creating its monitors (`wf-04`) — the transaction recording the event submits the Job in the same outbox write, so there is no sensor watching the database for something the platform already knows. |
| **FR-PLAT-64** | *(appended 2026-08-23, OQ-PLAT-8)* **An idempotency key is permanent, and a terminally failed Job releases it.** FR-PLAT-12's 24-hour window is withdrawn: a key matching a Job that **succeeded or was cancelled** returns that Job however long ago it ran, so "has this period been done?" is answered by the key and never by a clock. A key whose Job reached `failed` is **released** — the next submission under it is a *fresh* Job rather than the failed one handed back — which is what makes a scheduled period retryable (FR-PLAT-61) without minting a second key that would defeat the first. **Cancellation does not release**: a human stopped that work, and a tick that re-submitted it would overrule them. That split is the whole point — "has it been done?" and "may it be attempted again?" become different questions, which is what a failed period needs and what neither a window nor a permanent key alone can express. **Uniqueness is enforced over surviving keys only**: the partial unique index on `(workspace_id, idempotency_key)` gains a `status <> 'failed'` term, so a failed Job keeps its key on the row as audit evidence of which attempt used it while no longer holding it — and the lookup that reads a key must filter failed Jobs out, or it finds several where it expects at most one. The same-key-different-parameters refusal (`IDEMPOTENCY_KEY_CONFLICT`) is unchanged, but is tested against the surviving Job alone, so an honest retry of a failed period passes it. This governs **every** keyed submission, including `01` FR-DATA-8's Ingestion Run, whose key is a different index over the same header and must not diverge from it. Owner: whichever workstream builds FR-PLAT-61. The code delta is the index predicate and a status filter on the lookup; the unreferenced `idempotency_window_hours` setting that asserted the withdrawn window is removed with this decision, and the Phase 0 draft stub `docs/contracts/openapi/gi-pricing.yaml` still describes that window in its `Idempotency-Key` parameter — it is superseded by the generated document and is not hand-edited (`CLAUDE.md` §2). |
| **FR-PLAT-60** | *(appended 2026-08-23, OQ-PLAT-4)* **The resource boundary is the Job and the queue; a Workspace is not one.** A Job that would exceed its budget is terminated by name (FR-PLAT-16), each queue's worker pool is sized independently (FR-PLAT-13), and the scoring pool runs without the compute pool at all (FR-PLAT-34). No limit is keyed on `workspace_id`, and none is specified. ADR-0006 is what makes that sufficient: every deployment holds one tenant, so the neighbour a quota was imagined to contain is a *different deployment*, and the contention that remains is a deployment's own workloads competing with each other — which is exactly what a per-Job budget and a per-queue pool bound. A third limit over the same contention adds a number to configure without adding a mechanism. **This rejects the quota, not the enforcement.** A budget that is configured and never read is worse than no budget, because the operator who set it believes a limit exists; FR-PLAT-16 requires *both* halves of the budget enforced, against a worker the deployed stack actually runs. Arming the memory half and shipping that worker service is **W14**'s, alongside the tenancy mechanics ADR-0006 requires. Reopened only on measurement, and the evidence is Job history (FR-PLAT-14), never a dashboard — FR-PLAT-52 forbids the identifier label that would make it one: two Workspaces in a single deployment where the delayed Jobs and the saturating Jobs belong to different ones. That reading is due at each phase-exit review (`CLAUDE.md` §14), which is the observer the original trigger never had. |

### 3.3 Storage

| ID | Requirement |
|---|---|
| **FR-PLAT-17** | **PostgreSQL 16** holds all metadata, artifact bodies (JSONB), the audit log, and job records. Schema changes go through Alembic; every migration is reversible or explicitly marked irreversible with a reason. |
| **FR-PLAT-57** | *(appended 2026-08-23, W32)* **The migration chain has exactly one head.** Alembic permits several, and two branches that each add a revision off the same parent produce two — a state that merges cleanly, passes every test, and then fails on the next deployment at `alembic upgrade head` with `Multiple head revisions are present`. It is a defect from the moment it lands and it is invisible until someone migrates, which is the worst combination a schema change can have. The invariant is therefore checked rather than asserted: `tests/test_repository_invariants.py` reads the chain through Alembic's own `ScriptDirectory` and fails when the head count is not 1, so a collision is caught in the pull request that creates it instead of in the deploy that trips over it. A *deliberate* divergence is resolved by an Alembic merge revision, which restores the single head and is the documented way to record that the branch was intended. Found on 2026-08-23, when W32-2 and W32-3 each added a revision parented on `9e4c7b21fa08` while executing concurrently and nothing in the repository objected. |
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
| **FR-PLAT-32** | The platform ships as container images: `api`, `worker`, `scheduler` (the beat tick, FR-PLAT-61), `frontend`, plus dependencies (PostgreSQL, Redis, MinIO, an OIDC provider for local use). `deploy/docker-compose.yml` brings up a working stack with seeded demo data (R2). |
| **FR-PLAT-33** | A Helm chart / Kubernetes manifests are provided for production, with independently scalable API, scoring, and compute worker pools. |
| **FR-PLAT-34** | The scoring API is independently deployable and horizontally scalable, and can run **without** the compute workers present — a pricing outage must not be caused by a modelling workload. |
| **FR-PLAT-35** | Database migrations run as an explicit pre-deploy step, never automatically on application start, and are forward-compatible with the previous application version so a rolling deploy is safe. |
| **FR-PLAT-56** | **A deployment is bound to one tenant, and says so out loud.** The tenant identifier is deployment configuration, the database carries the same identifier in a single-row marker written at first migration, and the application **refuses to start when they disagree** — a startup failure, not a warning and not a log line. Pointing one tenant's application at another tenant's database is the one operational mistake ADR-0006's guarantee cannot survive, and it is exactly the mistake a restore, a copied `.env` or a misedited Helm value makes easy. The same check covers object storage and the broker where their configuration is per tenant. Owned by **W14**. |
| **FR-PLAT-59** | *(appended 2026-08-23 — decides `OQ-PLAT-5`'s production half)* **No identity provider ships in the production stack; an external IdP is always required outside `local`/`dev`.** The code has been enforcing this unaided — a `prod` deployment already refuses to start with no configured issuer — so what this requirement adds is the decision, not the behaviour. `deploy/` carries a **reference** Keycloak deployment instead: documented, versioned, and marked in its own README as an example that the deployer operates, patches and is accountable for, explicitly **not** a platform component this project secures on their behalf. That distinction is the entire decision. Bundling would lower the barrier for a small insurer with no IdP, and would make this project responsible for operating the highest-consequence component in the stack — one unpatched CVE in a bundled identity provider is every deployment's credential breach, on a project whose release cadence is nobody's SLA. A reference deployment gives a deployer the same starting point and leaves accountability where the deployment boundary already puts it. Owned by **W14**, with the rest of `deploy/` beyond compose. |
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
`API_KEY_INVALID`, `API_KEY_EXPIRED`, `ENVIRONMENT_SCOPE_DENIED`, `WORKSPACE_SCOPE_DENIED`,
`WORKSPACE_SELECTION_REQUIRED`, `JOB_NOT_CANCELLABLE`,
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
| `05-monitoring` | Scheduling (FR-PLAT-61), notification channels, operational metrics |

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
| **OQ-PLAT-2** | ~~Does Dagster earn its place, or should scheduled work be Celery beat plus a thin scheduler?~~ **DECIDED 2026-08-23: it does not — Dagster is dropped, and scheduled work is the tick specified as `FR-PLAT-61`.** The recommendation on file was "keep it, but confine it to scheduling and partitioning", with a fallback to beat *if the boundary proves hard to hold*. Confining it to scheduling is what settles it: once Dagster may not execute pricing work, what remains of it is a clock and a table of which periods have run — and the platform must own both anyway, because a scheduled run has to be a Job (FR-PLAT-15) with the same audit, cancellation and outbox guarantees (FR-PLAT-51) as any other. Keeping Dagster buys a UI for state the Jobs UI must already show, and costs a second scheduler, a second operational surface and a second place a run can exist. **The two capabilities cited for it are specified directly rather than lost**: catch-up, because schedules are period-anchored rather than interval-timed, and backfill for a Monitor created late (`05` NFR-MON-8), as an explicit bounded request. Nothing is un-built by this — Dagster was never a dependency (absent from `pyproject.toml` and `uv.lock`), so the decision removes a plan, not code. |
| **OQ-PLAT-3** | ~~Should the scoring service be a separate deployable *application*, rather than the same image run with a different role?~~ **DECIDED 2026-08-18: one image with a role flag through Phases 1–2, a separate scoring image from Phase 3** — and the thing that makes the later split cheap is specified now as `NFR-PLAT-11`, which scores a Model in a process where the fitting stack cannot be imported, and so stops that path growing a dependency the split would later have to shed. *An import-linter contract was tried first and is the wrong instrument — the requirement records why.* The image itself is Phase 3 (W14's successor); the boundary is enforced from today. |
| **OQ-PLAT-4** | ~~How are workspace-level resource quotas expressed (concurrent compute jobs, total storage)?~~ **DECIDED 2026-08-23: they are not — no Workspace quota is specified or built, and `FR-PLAT-60` records the boundary that replaces it.** The recommendation on file was a *deferral* — skip quotas "until multi-tenancy is on the table (OQ-OVR-1)" — and that trigger cannot fire, because OQ-OVR-1 was itself decided on 2026-08-15 (ADR-0006, FR-OVR-13) as one tenant per deployment, permanently. A deferral whose trigger is already dead is a rejection nobody has written down, so it is written down here instead. What the ADR left genuinely open is answered the same way: a tenant's own scoring path is protected from its own modelling workload by the queue split (FR-PLAT-13, FR-PLAT-34), not by a per-workspace number. The half that stays open is *enforcement*, not expression — FR-PLAT-16's memory budget and a worker service for it to apply to are **W14**'s. Original text: **Half of this question was already answered:** ADR-0006 makes every deployment single-tenant, so a quota never protects one insurer from another — it protects a tenant's own scoring path from its own modelling workload. What remains open is whether that needs expressing per workspace at all, or whether the worker pool split (FR-PLAT-34) already does it. |
| **OQ-PLAT-6** | ~~How does the browser authenticate to the API — authorization-code + PKCE in the SPA, or a BFF session cookie?~~ **DECIDED 2026-08-15: PKCE in the SPA for Phases 1–2**, specified as FR-PLAT-55 and owned by W6b. Revisit at Phase 3 if a deployment requires that no token exist in the browser at all. |
| **OQ-PLAT-5** | ~~Do we ship a bundled OIDC provider (Keycloak) in the production compose stack as a supported deployment, or is an external IdP always required outside local development?~~ **DECIDED 2026-08-23: bundled for local development behind an opt-in compose profile (`FR-PLAT-58`), never in production (`FR-PLAT-59`).** The two halves are separate questions that the one word "bundle" hid. Locally there is a real hole — `FR-PLAT-1` said a provider runs in the local stack in the present indicative and none does, so the only way in is `dev_auth_enabled`, and the browser flow W6b must build (FR-PLAT-55) has nothing to authenticate against. In production the answer is the recommendation's: `deploy/` carries a *reference* Keycloak deployment the deployer operates and patches, and operating an identity provider on an insurer's behalf is not a responsibility this project takes. The local provider is an **alternative** to `dev_auth_enabled`, never a replacement — both test suites still run with no container. |
| **OQ-PLAT-7** | ~~A `PlatformError` raised inside a Job handler loses its `.code` before it reaches storage. Should the generic handler special-case `PlatformError` to preserve it?~~ **DECIDED 2026-08-22: yes — option (a), a dedicated `except PlatformError` clause before the generic one, storing `JobError(code=exc.code, message=exc.detail or exc.title, retryable=False, trace_id=…)`.** `JOB_HANDLER_FAILED` stays exactly where it belongs, as the code for a genuinely unexpected exception, and no retry behaviour changed — `retryable` is the same literal `False`, and the clause deliberately does not infer retryability from `status_code`. **The ordering that matters is not the one the question implied.** `PlatformError`, `JobCancelled` and `JobBudgetExceededError` are three independent direct subclasses of `Exception`, checked against the MRO rather than assumed, so the clauses already there are genuine siblings and their order is free; `except Exception` is a *base* of `PlatformError`, and a clause placed after it would never run while looking correct. FR-PLAT-11 is what this restores — the typed error code a failed Job records — and three tests in `backend/tests/test_model_jobs.py` carry that mark: a named-code test through `execute_job`, a `RuntimeError` control proving `JOB_HANDLER_FAILED` is still reached, and a 429 `RATE_LIMITED` case proving `retryable` is still `False`. **Not delivered, and not disguised:** `PlatformError.errors` still does not reach `JobError.detail`, so FR-PLAT-11's field-level-cause clause remains unmet for handler-raised errors. |
| **OQ-PLAT-8** | *(raised 2026-08-23 by OQ-PLAT-2)* ~~**What does an `Idempotency-Key` that names a Job which already finished mean, and does the 24-hour window in FR-PLAT-12 exist?**~~ **DECIDED 2026-08-23: option (c) — the window is withdrawn, keys are permanent, and a terminally failed Job releases its key. Specified as FR-PLAT-64.** FR-PLAT-12 says a key matching a Job "from the last 24 h" returns the original. `platform.jobs.submit()` applies **no** time window and returns the existing Job whatever its status — so a key whose Job *failed* is spent forever, and a key whose Job succeeded is honoured a year later. Both halves of the spec sentence are therefore unimplemented in opposite directions, and FR-PLAT-61 depends on the answer: `(schedule_id, period)` is exactly a key whose Job may have failed. Options: **(a)** implement the window as written — simple, but a period older than a day silently re-runs, which is the duplicate the key exists to prevent; **(b)** drop the window, keys permanent — safest against duplicates, leaves no way to retry a failed period except a new key; **(c)** keys permanent, but a **terminally failed** Job releases its key, so a retry under the same key is a fresh Job and a success or a cancellation is not. **(c) was the recommendation and is the decision** — it is the only one where "has this period been done?" and "may it be attempted again?" are different questions, which is what the failed-period case actually needs. The window's withdrawal reaches `00` §5.4, which stated it as a platform-wide convention, and `01` FR-DATA-8, whose Ingestion Run key is a second index over the same header; both are amended with the decision. Owner: whichever workstream builds FR-PLAT-61. |
| **OQ-PLAT-9** | ~~**How does a principal's chosen workspace reach the API?**~~ **DECIDED 2026-08-23: option (a) — a verified `Workspace-Id` header, specified as FR-PLAT-65.** FR-PLAT-63 requires the choice to be verified against membership on every request and deliberately does not say how it is carried. Raised 2026-08-23 by the W6b slice-map backlog (item 2). The obvious answer — a request header — is argued against by an invariant in the code itself, that a header-supplied workspace "would make the scope a claim rather than a fact". Options and the reasoning (a verified header, a `/workspaces/{id}/…` path prefix, or the workspace bound into the session at login) are in [`../open-questions.md`](../open-questions.md). The invariant that made the question live is satisfied rather than overridden: the header is checked against membership, and an absent one is refused rather than defaulted. `W6b-11` is unblocked as a decision and still waits on W32's backend half; nothing was unsafe meanwhile, because the API refuses a multi-membership principal. |
| **OQ-PLAT-10** | **Every layer of the contract guard is scoped to the intersection of its two sides, so a shape or keyword present on only one side is outside all of them by construction.** Raised 2026-08-24 (W32-11). The type comparison intersects paths, the constraint comparison intersects paths and then keywords, and the completeness check defines an eligible schema as one with both sides — so it is defined over the complement of the problem. The consequence is not that anything is wrong today but that nothing can tell it apart if it goes wrong: the guard is silent in the same way whether a shape is one-sided **on purpose** — a first written form, which five generated-only slugs are, each said so in a comment — comments nothing checks, and `peril-structure`'s has already gone stale, still denying an authored side that was added in #133 — or **by accident**, an authored side deleted or never written. Measured at `946725f`: 26 authored, 25 generated, 15 both-sided, 11 authored-only, 10 generated-only. Any published count must say which frame it means, because "100% of what is in scope is compared" and "21 of 36 shapes are out of scope" are both true of the same tree. The residual is bounded — all 11 authored-only slugs are later-phase and all 10 generated-only ones are first written forms — which is what makes this a question about keeping that knowable rather than a defect. **The blind spot also moves.** The intersection is recomputed each run and the guard keeps no memory of the previous one, so a path that leaves the shared set is indistinguishable from one never in it — coverage can shrink a path at a time, indefinitely, with every check green. An arm-granularity instance is measured on the unmerged W32-1b branch and will be recorded with its tree once that lands; W32-1b delivers arm-level **type disagreement on shared paths**, not arm-level **existence**, which is this question. The recommendation is to declare one-sidedness rather than infer it; options are in [`../open-questions.md`](../open-questions.md). Owner: maintainer. |
| **OQ-PLAT-11** | **When a shape is tightened, nothing revalidates the artifacts already stored under the looser one.** Raised 2026-08-24 (W32-11). An artifact is validated on write against the model of that day and parsed again on read against the model of today, so a narrowing that is correct going forward can make an existing row unreadable — and the failure appears at read time, to a user who did nothing, far from the commit that caused it. Two real instances: `OQ-OVR-8` moved decimals from accepting JSON numbers to refusing them, and the certificate battery moved from a count floor to an exact set of names (FR-MODEL-126). Both narrow, which is the direction that breaks reads. The recommendation is an on-demand revalidation sweep now — it does not prevent the break but moves its discovery onto the committer's clock — with per-version readers when artifacts outlive a release; options are in [`../open-questions.md`](../open-questions.md). The rule worth writing down either way is that a narrowing change to a stored shape is a migration event, not a model edit. Owner: maintainer. |
| **OQ-PLAT-13** | **`metric-certificate` has a model-side four-check floor and no authored contract at all**, so nothing compares it and no external reader is told what a metric certificate contains. Raised 2026-08-24 as finding F3 of W32-11. Unlike the nine other generated-only slugs it is not a first written form by design: its sibling `objective-certificate` has both sides, and FR-MODEL-105 and FR-MODEL-108 treat the two alike. **W32 goal borne on:** FR-PLAT-48. **Dispositioned, not delivered** — the floor is enforced model-side as FR-MODEL-105 asks; the comparison and the publication are what is outstanding. The recommendation is to author it in whichever workstream next touches certificates, and the warning worth carrying is that covering it by declaring it deliberately one-sided would record an oversight as a decision. Options are in [`../open-questions.md`](../open-questions.md). Owner: maintainer. |
| **OQ-PLAT-12** | **What tells the API that a workspace selection *changed*, so that a switch is audited once rather than never or on every request?** Raised 2026-08-24 by W32-7. FR-PLAT-63's fourth obligation says a switch is audited into both chains, and W32-7 built the mechanism — `platform.workspace_switch.record_switch` writes one event in the workspace left and one in the workspace entered, ordered by id so opposite-direction switches cannot deadlock on the per-workspace advisory lock. The call site is what is missing, and not for want of effort: `require_caller` runs once per request and holds no memory of the previous one, so "the selection changed" is not a fact it can observe. *(amended 2026-08-24, the day it was raised.)* **No mechanism is recommended**, because the choice is not derivable from the options: it turns on which reading of FR-PLAT-63's fourth obligation is correct — a switch as a human act, or a switch as any difference in effective scope between two consecutive requests — and the two readings select different options. Storing the previous selection **on the user row** is refused under both: a single principal-level "current workspace" cannot represent two open tabs, so every request from either is recorded as a switch, two audit events and two per-workspace advisory locks apiece, in exactly the two-tab case FR-PLAT-65 made the selection per-request to support. Auditing every selection is the option to refuse out loud under a human-act reading, because it needs no schema change and so is the one a later reader reaches for, and it turns the FR-GOV-24 chain into a request log. Options are in [`../open-questions.md`](../open-questions.md). **FR-PLAT-63's fourth obligation is deferred with an owner, not delivered**, and is consumed by `W6b-11`. Owner: maintainer. |
| **OQ-PLAT-14** | **20 of the 39 `entity_ref` spellings the backend writes into the audit chain do not parse as an `ArtifactRef`, and nothing notices.** Raised 2026-08-24 by W32-7, which set out to ask whether a switch event's `workspace:<slug>@1` should be admitted to `ARTIFACT_TYPES` and measured the column instead: 13 types besides `workspace` are already written and absent from the frozenset — `actor`, `approval_policy`, `backtest`, `blob`, `job`, `model_comparison`, `model_family`, `principal`, `profile`, `role`, `service_account`, `setting`, `validation_report` — and 5 more use a listed type with no `@version`. Only 19 of 39 parse. The column is typed as a plain `str` and nothing parses it, which is why a majority-unparseable column has been invisible. The question is therefore what `entity_ref` *is*: the code has held "a name for the subject of the event" while the type name says "an `ArtifactRef`". The recommendation is to declare and validate that first reading rather than widen `ARTIFACT_TYPES` to 13 new types, which would redefine the set as "things that appear in `entity_ref`" — and `00` §2 makes a Workspace, a Principal and a Role the scope and subjects artifacts exist under, not artifacts. Options are in [`../open-questions.md`](../open-questions.md). Carried either way: `ARTIFACT_TYPES` is never widened to make an existing string parse, and the 5 unversioned refs are a plain bug — `dataset:{slug}` records which dataset was touched but not which version, which is the fact an auditor came for. Owner: maintainer. |
| **OQ-PLAT-15** | **`req-coverage.py`'s three inflation modes are not the three that were reported.** Raised 2026-08-24 (W6b) against `e2ae7c6`, baseline `523 specified · 269 marked · 51.4%`. The denominator mode is already enforced by `audit-docs.py` checks 2 and 3; the numerator mode has one live instance, a marker in true decorator position on a helper pytest never collects, so a test lost its traceability link and the instrument credited the loss to the helper; and the mode that is actually firing is **clause-conflation**, which no cheap instrument change reaches, because the unit is the requirement id and the defect is inside the sentence. Six options are in [`../open-questions.md`](../open-questions.md), recommending an AST marker reader, a UI-clause warning and a truthful per-requirement count, with a standing reporting rule as their release note. Owner: maintainer. |
