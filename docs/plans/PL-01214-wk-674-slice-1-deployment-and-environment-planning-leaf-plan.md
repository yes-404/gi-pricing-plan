---
id: PL-1214
family: plan
kind: leaf
title: WK-674 Slice 1 — Deployment & Environment Planning: leaf plan
status: draft                     # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: ~
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, RL-918, RL-921, RL-1172, ADR-710, FD-1197, FD-1199]
---

# WK-674 Slice 1 — Deployment & Environment Planning: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–3), and `dev-commands` (the gate).

## Goal

Build the foundational infrastructure for WK-674's deployment lifecycle: the **Environment** and **Deployment** models, the database schema for multi-environment state, Service Account environment scoping, tenant isolation at the deployment boundary, and the core API routes skeleton. No shadow scoring, no date-based routing, no rollback in Slice 1 — those are Slices 2–4. This slice establishes the shape all others build on.

**Architecture:** Following `RL-921` and `RL-918` (the architectural rulings on NFR-489 and WK-671's production lesson), deployment changes are recorded as Audit Events (FR-272) and routed through the governance gate (06 §3.3 evidence). Environments are Settings (FR-431, `07` §3.8); Service Account scopes are environment-keyed to enforce tenant isolation (FR-430, FR-436). The schema adds no new tables beyond `Environment`, `Deployment`, and schema changes to pin `Job.build` (FR-18, from OQ-540). `model-schema` holds all Pydantic shapes; the backend routes call the governance approver and record Audit Events.

**Tech Stack:** Pydantic v2, FastAPI, SQLAlchemy 2.x async, Alembic, pytest. No new dependency.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) and [`../specs/07-platform.md`](../specs/07-platform.md):
- `03` §3.8: FR-267, FR-268, FR-272; §5.1 (Deployment endpoints skeleton); §5.2 (Deployment/Environment shapes, database schema); §9 (NFR-489, NFR-502).
- `07` §3.2, §3.3: FR-429, FR-436; §3.8: FR-428, FR-430, FR-431; §5 (Environment and Deployment API routes); §9 (FR-18).
- `06-governance.md` §3.3: approval gate for prod deployments.

## Status

**Draft filed 2026-09-29**, frozen at `origin/main` (current HEAD to be stated by executor at tree read). No decisions yet pending; all referenced rulings (RL-918, RL-921) are decided. Slice order from `PL-930` is S1 → S2 → S3 → S4; this plan is Slice 1.

**Open questions placed in §9:**
- Monitoring backend for deployment observability (ELK vs. Prometheus)?
- Blue-green vs. canary strategy for atomic switchover?
- Shadow scoring sample rate configuration (per-environment or global)?

These do not block Slice 1 implementation; they are answered before Slice 2 (shadow scoring) and Slice 3 (routing) start.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the failing run is quoted in the ledger with its failing assert or error line.

1. **Spec.** `03` and `07` change as follows:
   - `03` §5.2 adds `Deployment` and `Environment` data model definitions, including the state machine for `Deployment.status` (draft → approved → deployed → rolled_back).
   - `03` §5.1 adds the four deployment routes (skeleton): `POST /api/v1/environments/{env}/deployments`, `GET /api/v1/environments/{env}/deployments`, `GET /api/v1/environments/{env}/deployments/{id}`, and a placeholder for rollback.
   - `07` §3.2–§3.3 clarifies that `Deployment` is subject to the approval gate; `prod` promotion requires approval (FR-429).
   - `07` §5 adds the four Environment management routes: `GET /api/v1/environments`, `GET /api/v1/environments/{name}`, `POST /api/v1/environments`, and `PUT /api/v1/environments/{name}`.
   - `07` §3.8 names Service Account's `granted_environments` field (a list of `(name, key_id)` pairs, per FR-430 amendment `RL-1184`).
   - `03` §3.2 adds one sentence: FR-18 — `Job.build_version` records the Git commit SHA of the Platform at the time the scoring bundle was compiled.

   `python3 scripts/audit-docs.py` adds no failure row.

2. **Shapes in `model-schema`.** `uv run python scripts/generate-contracts.py --check` exits 0.
   - `Environment` shape: `name`, `description`, `promotion_order` (an integer), `live_rating_version_ref` (nullable).
   - `Deployment` shape: `id`, `environment`, `rating_version_ref`, `status` (enum: draft, approved, deployed, rolled_back), `deployed_by`, `deployed_at`, `bundle_hash`, `reason_for_deployment`.
   - `DeploymentRequest` shape: `rating_version_ref`, `reason`.
   - Request and response shapes are pinned by the OpenAPI contract.

3. **Database schema.** `uv run alembic upgrade head` succeeds against a test database.
   - `environments` table: `id`, `name` (unique), `description`, `promotion_order`, `live_rating_version_ref` (foreign key to `rating_versions`, nullable).
   - `deployments` table: `id`, `environment_id` (foreign key), `rating_version_id` (foreign key), `status` (enum), `deployed_by` (user id), `deployed_at` (timestamp), `bundle_hash` (string), `reason` (text).
   - `jobs` table adds `build_version` (VARCHAR, nullable initially; non-nullable after FR-18 activation).
   - `service_accounts` table adds `granted_environments` (JSONB, list of `{"name": "uat", "key_id": "..."}` per FR-430/RL-1184).

4. **API routes (skeleton, no business logic yet).** `uv run pytest backend/tests/test_deployment_api.py -q` passes. Each test is red first:
   - `GET /api/v1/environments` returns 200 with a list of Environment shapes.
   - `POST /api/v1/environments/{env}/deployments` accepts a `DeploymentRequest` and returns 202 with a `Deployment` shape in draft status.
   - `GET /api/v1/environments/{env}/deployments` returns 200 with a list of Deployments for that environment.
   - `GET /api/v1/environments/{env}/deployments/{id}` returns 200 or 404 (if id doesn't exist).
   - Deployer role can call the route; non-Deployer gets 403.
   - Deployment to prod requires an approval record (test uses a mock approval gate that always passes for this slice).

5. **Service Account scoping.** `uv run pytest backend/tests/test_service_account_env_scope.py -q` passes. Tests verify:
   - A Service Account granted `["uat", "prod"]` cannot score against `dev` (403).
   - A leaked key for `uat` cannot score against `prod`.
   - Key creation mints one key per granted environment.

6. **Audit Events.** `uv run pytest backend/tests/test_deployment_audit.py -q` passes:
   - Each deployment state change emits an Audit Event with type `DEPLOYMENT_CREATED`, `DEPLOYMENT_APPROVED`, `DEPLOYMENT_DEPLOYED`, etc. (FR-272).
   - The audit trail is queryable and includes `who`, `when`, `what`, and `reason`.

7. **Tenant isolation at deployment boundary (FR-436).** `uv run pytest backend/tests/test_deployment_tenant_isolation.py -q` passes:
   - A deployment request against a `rating_version_ref` from another tenant raises a 403 `TENANT_MISMATCH` error.
   - The error is caught before any database write.

8. **The gate.**
   - The full two-half gate exits 0, with every rc and `HEAD` in the ledger.
   - `uv run python scripts/req-coverage.py` shows FR-267, FR-268, FR-272, FR-429, FR-436, FR-18 rows with implementation tests attached.

## Global Constraints

- **Requirement IDs are permanent.** FR-267–272, FR-428–431, FR-436, FR-18 are already defined in specs and are not invented in this plan.
- **Money is integer minor units.** No Deployment/Environment shape holds money; this constraint does not apply.
- **ADR-710 (Tenancy mechanics)** — read before implementation. Deployment refuses to start against another tenant's database (FR-436).
- **Service Account key rotation happens after this slice.** Key rotation is Slice 2 or later; Slice 1 creates keys only.
- **Rate limits per environment are configuration, not code.** FR-430 is a Setting (FR-431); no rate limiter is built in Slice 1, only the configuration shape.

---

## Files Changed

| File | Reason |
|------|--------|
| `backend/src/app/models/environment.py` | Create — Environment ORM model |
| `backend/src/app/models/deployment.py` | Create — Deployment ORM model |
| `backend/src/app/models/service_account.py` | Modify — Add `granted_environments` field and env-scoping logic |
| `backend/src/app/models/job.py` | Modify — Add `build_version` field (nullable initially) |
| `backend/src/app/api/environments.py` | Create — Environment CRUD routes |
| `backend/src/app/api/deployments.py` | Create — Deployment routes (skeleton) |
| `backend/src/app/services/deployment_service.py` | Create — Deployment business logic (approve, deploy state transitions) |
| `packages/model-schema/src/model_schema/__init__.py` | Modify — Add Environment, Deployment, DeploymentRequest shapes |
| `backend/migrations/versions/XXX_add_deployment_environment_tables.py` | Create — Alembic migration |
| `backend/tests/test_deployment_api.py` | Create — API route tests |
| `backend/tests/test_service_account_env_scope.py` | Create — Tenant isolation tests |
| `backend/tests/test_deployment_audit.py` | Create — Audit Event tests |
| `backend/tests/test_deployment_tenant_isolation.py` | Create — FR-436 tests |
| `docs/specs/03-rating-engine.md` | Modify — Add Deployment/Environment to §5.2, routes to §5.1 |
| `docs/specs/07-platform.md` | Modify — Add Environment management routes, clarify approval gate |
| `scripts/generate-contracts.py` | Modify — Ensure Deployment shapes are published to OpenAPI contract |

## Milestones

**S1 (This Slice):** Environment and Deployment models, schema, API skeleton, Service Account scoping, Audit Events, tenant isolation.

**S2 (Following):** Shadow scoring configuration and route integration.

**S3 (Following):** Date-based routing.

**S4 (Following):** Rollback implementation and production deployment workflow.

---

## Task 1: Specification Change — Update `03-rating-engine.md` and `07-platform.md`

**Files:**
- Modify: `docs/specs/03-rating-engine.md:§5.1, §5.2, §9`
- Modify: `docs/specs/07-platform.md:§3.2, §3.3, §3.8, §5, §9`

**Interfaces:**
- Consumes: None (spec change)
- Produces: Defined requirement ids (FR-267–272, FR-428–431, FR-436, FR-18) and API routes

- [ ] **Step 1: Read `03` §5 (Endpoints and Data Contracts) and `07` §3, §5**

Read the current spec sections to understand the structure. Locate where Deployment/Environment routes will fit.

- [ ] **Step 2: Add to `03` §5.2 — Deployment and Environment data model definitions**

Add under "Data Contracts":

```markdown
| **Environment** | A first-class object representing a deployment target (dev, uat, prod). Fields: `name` (string, unique), `description` (string), `promotion_order` (integer, enforced by approval gate), `live_rating_version_ref` (string, nullable). Created once, configuration is a Setting (FR-431). |
| **Deployment** | Records the binding of an approved Rating Version to an Environment. Fields: `id` (uuid), `environment` (foreign key), `rating_version_ref` (string), `status` (enum: draft, approved, deployed, rolled_back), `deployed_by` (string, user id), `deployed_at` (timestamp, nullable), `bundle_hash` (string), `reason_for_deployment` (string). FR-268 guarantees atomicity: switching bundles pre-warms the new one before updating `live_rating_version_ref`. |
```

- [ ] **Step 3: Add to `03` §5.1 — Deployment API routes**

Add four rows to the endpoint table (after the existing scoring routes):

```markdown
| `POST` | `/api/v1/environments/{env}/deployments` | Deploy an approved version (FR-267) |
| `GET` | `/api/v1/environments/{env}/deployments` | List deployments for an environment |
| `GET` | `/api/v1/environments/{env}/deployments/{id}` | Fetch one deployment |
| `POST` | `/api/v1/environments/{env}/deployments/rollback` | [Placeholder for Slice 3] |
```

- [ ] **Step 4: Add FR-18 clarification to `03` §3.2 (Concepts)**

After the `Bundle` definition, add:

```markdown
| **Build Version** | The Git commit SHA of the platform repository at the time a scoring bundle was compiled. Recorded in `Job.build_version` (FR-18) and used to detect version skew between tenants in a shared environment. Multi-tenant deployments must have compatible platform builds or refuse the deployment (FR-436). |
```

- [ ] **Step 5: Update `03` §9 (NFRs) to note FR-18 dependency**

Find NFR-489 or the deployment NFR section and add: "FR-18 (`Job.build_version`) is a prerequisite for FR-436 tenant isolation."

- [ ] **Step 6: Update `07` §3 (Concepts) to clarify Deployment approval**

Add a subsection under §3.2 (Authorization):

```markdown
**Deployment Approval Gate:** Deployment to `prod` requires a completed approval record (`06-governance.md` §3.3). Deployment to non-prod environments (`dev`, `uat`) may skip approval at workspace policy discretion. The approval gates promotion order (FR-429): a Rating Version cannot deploy to `prod` without prior successful deployment to `uat` unless explicitly waived.
```

- [ ] **Step 7: Add to `07` §3.8 (Settings) — Environment Configuration**

Add a row:

```markdown
| **Environment** | Scope: workspace. Fields: `name`, `description`, `promotion_order`, `live_rating_version_ref`. Immutable: `name`. Used to configure promotion rules, rate limits (FR-430), and monitoring per environment (FR-431). |
```

- [ ] **Step 8: Clarify Service Account's granted_environments in `07` §3.2**

Update the Service Account definition to name the new field:

```markdown
**Amended 2026-09-29 (WK-674 S1):** A Service Account granted multiple environments holds one API key per environment (FR-430). The `granted_environments` field is a list of `(name, key_id)` tuples; creation mints one key per environment. Scope enforcement: a key for `uat` cannot score against `prod` (FR-436).
```

- [ ] **Step 9: Add to `07` §5 (API Endpoints) — Environment Management Routes**

Add a new subsection for Environment management:

```markdown
| `GET` | `/api/v1/environments` | List all environments |
| `GET` | `/api/v1/environments/{name}` | Fetch one environment |
| `POST` | `/api/v1/environments` | Create environment (admin only) |
| `PUT` | `/api/v1/environments/{name}` | Update environment configuration |
```

- [ ] **Step 10: Run the audit and verify**

```bash
python3 scripts/audit-docs.py
```

Expect: no new failures (all ids FR-267–272, FR-428–431, FR-436, FR-18 are already defined).

- [ ] **Step 11: Commit**

```bash
git add docs/specs/03-rating-engine.md docs/specs/07-platform.md
git commit -m "docs(specs): Deployment & Environment planning — FR-267, FR-268, FR-272, FR-429, FR-436, FR-18

Add Deployment and Environment data models, API routes, and approval gate clarification.
Scope tenant isolation at deployment boundary.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SwSJvYSswgPp1HGD2qn1pR"
```

---

## Task 2: Create Pydantic Shapes in `model-schema`

**Files:**
- Modify: `packages/model-schema/src/model_schema/__init__.py`

**Interfaces:**
- Consumes: Task 1 (spec definitions)
- Produces: `Environment`, `Deployment`, `DeploymentRequest` Pydantic v2 models

- [ ] **Step 1: Add imports**

At the top of `model_schema/__init__.py`:

```python
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
```

- [ ] **Step 2: Define DeploymentStatus enum**

```python
class DeploymentStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
```

- [ ] **Step 3: Define Environment shape**

```python
class Environment(BaseModel):
    name: str = Field(..., description="Unique environment name (dev, uat, prod, etc.)")
    description: str = Field(..., description="Human-readable description")
    promotion_order: int = Field(..., description="Order in promotion sequence (0=dev, 1=uat, 2=prod)")
    live_rating_version_ref: Optional[str] = Field(default=None, description="Currently deployed Rating Version ref")
```

- [ ] **Step 4: Define Deployment shape**

```python
class Deployment(BaseModel):
    id: str = Field(..., description="Deployment UUID")
    environment: str = Field(..., description="Environment name")
    rating_version_ref: str = Field(..., description="Rating Version reference")
    status: DeploymentStatus = Field(..., description="Deployment status")
    deployed_by: str = Field(..., description="User ID of deployer")
    deployed_at: Optional[datetime] = Field(default=None, description="Deployment timestamp")
    bundle_hash: str = Field(..., description="Content hash of the compiled bundle")
    reason_for_deployment: str = Field(..., description="Reason for deployment")
```

- [ ] **Step 5: Define DeploymentRequest shape**

```python
class DeploymentRequest(BaseModel):
    rating_version_ref: str = Field(..., description="Rating Version to deploy")
    reason: str = Field(..., description="Reason for this deployment")
```

- [ ] **Step 6: Export shapes in `__all__`**

Ensure `Environment`, `Deployment`, `DeploymentRequest`, and `DeploymentStatus` are in the module's `__all__` list.

- [ ] **Step 7: Regenerate contracts**

```bash
uv run python scripts/generate-contracts.py
```

Verify `docs/contracts/openapi/generated.json` includes the three new shapes.

- [ ] **Step 8: Commit**

```bash
git add packages/model-schema/src/model_schema/__init__.py docs/contracts/
git commit -m "feat(model-schema): Add Environment, Deployment shapes

Environment, DeploymentRequest, Deployment, and DeploymentStatus.
Regenerated OpenAPI contract.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SwSJvYSswgPp1HGD2qn1pR"
```

---

## Task 3: Create ORM Models and Database Schema

**Files:**
- Create: `backend/src/app/models/environment.py`
- Create: `backend/src/app/models/deployment.py`
- Modify: `backend/src/app/models/service_account.py` (add `granted_environments`)
- Modify: `backend/src/app/models/job.py` (add `build_version`)
- Create: `backend/migrations/versions/XXX_add_deployment_environment_tables.py`

**Interfaces:**
- Consumes: Task 2 (Pydantic shapes)
- Produces: SQLAlchemy ORM models and Alembic migration

- [ ] **Step 1: Create `backend/src/app/models/environment.py`**

```python
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Environment(Base):
    __tablename__ = "environments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    promotion_order = Column(Integer, nullable=False)
    live_rating_version_ref = Column(String, nullable=True)
    
    deployments = relationship("Deployment", back_populates="environment")
```

- [ ] **Step 2: Create `backend/src/app/models/deployment.py`**

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base
import uuid

class DeploymentStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"

class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    environment_id = Column(String, ForeignKey("environments.id"), nullable=False)
    rating_version_id = Column(String, nullable=False)
    status = Column(SQLEnum(DeploymentStatus), default=DeploymentStatus.DRAFT, nullable=False)
    deployed_by = Column(String, nullable=False)
    deployed_at = Column(DateTime, nullable=True)
    bundle_hash = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    
    environment = relationship("Environment", back_populates="deployments")
```

- [ ] **Step 3: Update `backend/src/app/models/service_account.py`**

Add import and field (at the top, after existing imports):

```python
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
```

Add to the `ServiceAccount` model:

```python
granted_environments = Column(
    JSON, 
    nullable=False, 
    default=list,
    comment="List of {name, key_id} tuples for environments this account can access"
)
```

- [ ] **Step 4: Update `backend/src/app/models/job.py`**

Add column to the `Job` model:

```python
build_version = Column(String, nullable=True, comment="Git commit SHA of platform at bundle compile time (FR-18)")
```

- [ ] **Step 5: Generate Alembic migration**

```bash
cd backend
alembic revision --autogenerate -m "add deployment environment tables and job.build_version"
```

Verify the generated migration file includes the new tables and columns.

- [ ] **Step 6: Review and edit migration if needed**

Open `backend/migrations/versions/XXX_add_deployment_environment_tables.py` and ensure:
- `environments` table is created with correct columns.
- `deployments` table is created with correct foreign keys.
- `service_accounts.granted_environments` column is added.
- `jobs.build_version` column is added as nullable.

- [ ] **Step 7: Test the migration**

```bash
alembic upgrade head
```

Verify no errors.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/models/ backend/migrations/
git commit -m "feat(backend): Add Environment and Deployment ORM models, schema migration

Add Environment, Deployment tables.
Add Service Account granted_environments and Job.build_version.
Alembic migration prepared.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SwSJvYSswgPp1HGD2qn1pR"
```

---

## Open Questions (for Phase 2 closure or Slice 2/3/4)

1. **DP-S1-1: Service Account key rotation scope** — Is key cycling per environment (one rotation per granted env) in Slice 2 or later?
2. **DP-S1-2: Bundle pre-warming timing** — Do we pre-warm bundles in Slice 1 or defer to Slice 2 (shadow scoring)?
3. **DP-S1-3: Approval gate testing** — Should Slice 1 mock the governance service, or call the real approval gate?
4. **Open: Monitoring backend** — ELK stack vs. Prometheus + Grafana for deployment observability?
5. **Open: Blue-green vs. canary** — Which deployment pattern for atomic switchover (FR-268)?
6. **Open: Shadow scoring sample rate** — Per-environment or global configuration (FR-271)?

---

## Cross-Module Dependencies

- **Depends on `03-rating-engine.md`:** Requires the `RatingVersion` model and the scoring route `/api/v1/score` (shared scoring path).
- **Depends on `06-governance.md`:** Approval gate for prod deployments (§3.3 evidence).
- **Depends on `07-platform.md`:** Service Account and Setting models.
- **Used by Slice 2 (WK-674 S2):** Environment and Deployment models are the foundation for shadow scoring configuration.
- **Used by WK-675 (Frontend):** API contract changes from this slice regenerate the frontend OpenAPI client.

---

## Implementation Notes

**Executor checklist at tree read:**
1. Re-read `03-rating-engine.md` §5.1–5.2 and `07-platform.md` §3.2–3.3, §5 at your tree (spec may have drifted since plan filing date).
2. Verify `RatingVersion`, `AuditEvent`, `Setting`, and `Workspace` models exist and match the shapes assumed in this plan.
3. Confirm the approval gate service endpoint is available (mock it for Slice 1 if needed).
4. Coordinate with WK-672 closure and WK-675 on API contract timing — Slice 1's routes must regenerate the OpenAPI contract for the frontend to consume.
5. Check `origin/main` for any new rulings on FR-436, FR-429, or tenant isolation between plan filing date (2026-09-29) and execution start.

**What's NOT in Slice 1:**
- Date-based routing (Slice 3, FR-270).
- Shadow scoring configuration (Slice 2, FR-271).
- Rollback implementation (Slice 4, FR-269).
- Key rotation (Slice 2 or later).
- Production deployment workflow with approval (Slice 4).

**What IS in Slice 1:**
- Environment CRUD.
- Deployment draft creation and state machine skeleton.
- Audit Events on state changes.
- Service Account environment scoping.
- Tenant isolation check (FR-436).
- `Job.build_version` schema column.
- API routes skeleton (no complex business logic).
