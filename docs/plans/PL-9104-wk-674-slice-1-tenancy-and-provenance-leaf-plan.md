---
id: PL-9104
family: plan
kind: leaf
title: WK-674 Slice 1 — Tenancy and provenance: leaf plan
status: draft                     # draft → active → superseded | retired (§1.2a)
owner: planner
tree: ~
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-9102, RL-9202, RL-9203, FR-436, FR-18]
---

# WK-674 Slice 1 — Tenancy and provenance: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–3), `python-test`, `fastapi-service` (Task 3) and `dev-commands` (the gate).

## Goal

Implement tenancy and provenance infrastructure to prevent deployment of a version against the wrong tenant's database, and to record the platform build version in Job records. This establishes the foundation for multi-tenant deployment safety in WK-674.

**Architecture:** This is the leaf plan for Slice 1 of the map plan PL-9102, the first slice of WK-674. It covers two requirements:
- **FR-436** (a deployment refuses to start against another tenant's database): validation layer enforcement at deployment route entry
- **FR-18** (a Job records the platform build, because version skew between tenants is now permanent): added to Job schema and populated at Job creation

**Tech Stack:** Pydantic v2, FastAPI, SQLAlchemy 2.x async, pytest. No new dependency.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) and [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md):
- `07` §3.6: FR-436 (tenancy validation)
- `03` §5 and beyond: FR-18 (platform build in Job)
- Data contracts for the build version field

Line numbers are at `origin/main`. Re-read them at the executor's tree.

## Status

**Draft.** This plan awaits the planner's drafting completion and activation by the lead.

This slice is the first of WK-674's six slices, establishing the tenancy safety perimeter before any deployment changes. The work is ordered before Slice 2 (Environment and Deployment record) because those changes depend on knowing that a deployment cannot violate tenant boundaries.

## Acceptance Standard

Every command runs in the executor's worktree (`env -C <worktree> …`), over `origin/main...HEAD`. "Red first" means the failing run is quoted in the ledger with its failing assert line; a failure for another cause is a plan defect.

### 1. Spec and contracts

- **Tenancy validation (FR-436):** `07` §3.6 declares the requirement that a deployment route refuses to start when the target database belongs to a different tenant than the deployment's provenance context. The spec names the error type and status code.
- **Build version in Job (FR-18):** `03` and `07` are amended to include a `platform_build` or `build_version` field in the Job record, capturing the version of the platform executable at Job creation time.
- `python3 scripts/audit-docs.py` exits 0 with no FR-436 or FR-18 gaps.

### 2. Schema and contracts proof

- `uv run python scripts/generate-contracts.py --check` exits 0.
- The Job schema includes the build version field and it is marked `required: true`.
- `grep -rn 'class.*Job\|platform_build\|build_version' packages/pricing-core/src backend/src` shows the Job model carries the field exactly once in `model-schema`.

### 3. Tenancy validation route

- `uv run pytest backend/tests/test_deployment_tenancy.py -q` passes; all tests are red first:
  - A deployment against the correct tenant's database succeeds (200).
  - A deployment against a different tenant's database returns 403 with the tenancy-violation error.
  - A deployment with no tenant context in the request returns 400 (malformed).
  - A deployment with a tenant mismatch returns the error with the expected status code per spec.

### 4. Build version population

- `uv run pytest backend/tests/test_job_build_version.py -q` passes; all tests are red first:
  - A Job created with a known platform build version stores and returns that version.
  - Two Jobs created at different times (simulating different builds) record different build versions.
  - The build version is never null for a created Job.
  - When fetching a Job, the build version is included in the response model.

### 5. Integration with scoring flow

- `uv run pytest backend/tests/test_score_with_tenancy.py -q` passes:
  - The `/score` endpoint accepts a tenancy context in the request.
  - A tenancy mismatch is caught before the scoring logic runs.
  - Jobs created as a result of scoring include the platform build version.

### 6. Gate

- The full two-half gate exits 0, with every rc and `HEAD` in the ledger.
- `uv run pytest backend/tests/ -k tenancy -q` (tenancy-specific tests) runs and all pass.
- `uv run python scripts/req-coverage.py` shows FR-436 and FR-18 rows with attached tests, both typed as delivered and tested.

## Decisions the plan does not give

None at this stage. All dependencies on WK-674's DP-1–DP-7 are upstream; this slice executes within the constraints they establish.

## Global Constraints

- No new external dependency.
- All tenancy state is read from the request context; no new configuration or environment variable is required.
- The build version is immutable once a Job is created; it is recorded but not amended.
- Tenancy validation must run **before** any Job is created, to prevent orphaned Jobs.

## What changed from the map plan

The map plan (PL-9102) names this slice broadly as "Tenancy and provenance." This leaf plan unpacks the two concrete FRs and their acceptance criteria.
