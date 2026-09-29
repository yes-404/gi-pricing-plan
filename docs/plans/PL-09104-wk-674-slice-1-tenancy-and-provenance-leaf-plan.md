---
id: PL-9104
family: plan
kind: leaf
title: WK-674 Slice 1 — Tenancy and provenance (FR-436, FR-18): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: bb2aa935dbdf207a7073df85f8fde143e1cee77b
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-710]
---

# WK-674 Slice 1 — Tenancy and provenance (FR-436, FR-18): leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–5), `python-test` (every task), `fastapi-service` (Task 4) and `dev-commands` (the gate), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make a deployment **bound to one tenant, and loud about it**, and make every Job **name the
build it ran on** — the two WK-674 obligations that ADR-710's one-tenant-one-deployment
decision creates and that every later WK-674 slice runs on top of.

**Architecture.** A tenant identifier becomes deployment configuration (`Settings`). A new
migration creates a single-row marker table and writes that identifier into it. The API
lifespan and the Celery worker both compare the configured identifier with the marker, and
with the equivalent markers in the blob bucket and the broker (DP-S1-2), **before** serving
anything; a mismatch is an exception that stops the process. Separately, `JobRow` gains a
`platform_build` column that the worker writes when it moves a Job to `running`, and the
`Job` shape carries it.

**Tech Stack:** Pydantic v2 (`pydantic-settings`), FastAPI lifespan, Celery signals,
SQLAlchemy 2.x async, Alembic, pytest. No new dependency.

**Spec:**
- [`../specs/07-platform.md`](../specs/07-platform.md) §3.6 — **FR-436** (`07:152` at the
  tree above).
- [`../specs/00-overview.md`](../specs/00-overview.md) §3 — **FR-18** (`00:222`).
- [`../specs/07-platform.md`](../specs/07-platform.md) §4.1 — the `Job` data contract,
  which gains the FR-18 field (Task 1).
- [`../specs/06-governance.md`](../specs/06-governance.md) — **FR-376**, the dossier that
  must state the build. Read-only here: its generator is WK-680's (Phase 3).
- [`../adrs/ADR-00710-tenant-isolation-is-a-deployment-boundary.md`](../adrs/ADR-00710-tenant-isolation-is-a-deployment-boundary.md)
  — why the check exists.

**What this plan implements.** WK-674's map plan (PR #843, branch
`p2-wk674-map` read at `ae0d398bdee49e3272303f2240a7f2694d67eec6`), **Task 1 — "Slice 1:
tenancy and provenance (FR-436, FR-18)"**, whose Sequencing block reads *"Slice 1 tenancy +
provenance ─→ Slice 2 Environment + Deployment record"*. The decision-maker's ruling on
that map plan (PR #848, branch `p2-wk674-rl` read at
`9e175017c950d80b857f283e09fbe938be337a27`) lists the same Slice 1 at its `:35`. Both are
unminted, so they are cited by PR number, not by id, and not in `relates:`; the minting
PR for this plan replaces those citations with the minted ids.

## Status

**Draft**, filed 2026-09-29 against the tree above. It replaces the Slice 1 draft that
PR #892 carried until this commit (commit
`0d1c83bf9eaa00a4149c2bcf051d0448672d8c14`), which scoped Slice 2 and Slice 3 work under
the Slice 1 label and took its slice order from WK-672's map plan (`PL-930`); that file is
deleted here, and its number is not this plan's. The id above is a **working id**: it is
minted at this PR's turn in the merge queue, never before.

**Activation needs, in order:** the map plan (#843) minted and `active`; DP-S1-1 and DP-S1-2
below resolved; the lead's go. **Map-plan deviation, stated rather than folded in:** the
map's Task 1 says the platform-build column is *"set at submission"*; FR-18 says a Job
records *"the platform version it ran on"*. The spec is the contract, so this plan records
the build when the worker moves the Job to `running` (Task 3), and names the difference
here for the lead and the map-plan's reviewer.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the
step predicts**; a failure for any other cause is a plan defect, reported, not worked around.

1. **Spec.** `07` §4.1's `Job` example and prose carry `platform_build` with a dated note
   citing FR-18. `07` FR-436 and `00` FR-18 are **not** reworded (they are already right);
   if the executor believes either needs a change, it stops and reports. DP-S1-1's and
   DP-S1-2's outcomes are written where their resolutions say. `python3 scripts/audit-docs.py`
   exits 0.
2. **Contract.** `uv run python scripts/generate-contracts.py --check` exits 0 after the
   regeneration, and the regenerated `Job` schema under `docs/contracts/` has a
   `platform_build` property. `model_schema.jobs.Job` is the only hand-written definition of
   the field (`git grep -n platform_build -- packages backend/src frontend/src` shows one
   shape definition, plus the ORM column and its writers).
3. **Marker migration (FR-436, FR-417).** One new Alembic revision creates the marker table
   and writes the configured tenant id. `uv run alembic upgrade head`, `downgrade -1` and
   `upgrade head` again all exit 0 against a scratch database, and
   `uv run pytest tests/test_repository_invariants.py -q` (FR-417's single-head guard) passes.
   A migration test asserts the table holds exactly one row, carrying the configured id, and
   that a second insert is refused by a constraint (not by application code).
4. **Refusal to start (FR-436), one negative test per store, each red first.** In a new
   `backend/tests/test_tenant_binding.py`, every test marked `@pytest.mark.req("FR-436")`:
   - database marker ≠ configured id → entering `TestClient(create_app(...))` raises, and the
     exception names **both** identifiers and the word `database`;
   - blob-bucket marker ≠ configured id → raises, naming `blob`;
   - broker marker ≠ configured id → raises, naming `broker` (per DP-S1-2's resolution);
   - the same database mismatch stops the **worker**: the worker-start hook raises before any
     task is consumed;
   - positive control: matching markers → the app starts.
   A test that goes red because the app failed to start for any **other** reason (a missing
   fixture, a connection refusal) has not proved FR-436 and is a plan defect.
5. **Provenance (FR-18), red first.** In `backend/tests/test_job_platform_build.py`, marked
   `@pytest.mark.req("FR-18")`: a Job moved to `running` by the worker path records the
   worker's configured build; a Job still `queued` has `platform_build` null; a re-run after
   an infrastructure retry records the build of the run that produced the result; `GET` on
   the Job returns the field.
6. **Coverage.** `uv run python scripts/req-coverage.py` lists tests against FR-436 and FR-18.
   The **dossier half of FR-18** (`06` FR-376) is recorded in the slice ledger as *deferred
   with an owner — WK-680* (Phase 3; `docs/roadmap.md`'s WK-680 row lists FR-376), not
   claimed.
7. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree, with
   every command's rc, the `N passed` line and `HEAD` quoted in the ledger.
8. **Item 11.** The deputy's merge acknowledgement is recorded on the PR before the lead
   merges, and the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean
   audit and the lead's merge — no maintainer acceptance line is required for this slice, and
   none is to be waited on.

## Global Constraints

- **One tenant, one deployment** (ADR-710; `00` FR-16). A `workspace_id` is not a tenant and
  nothing in this slice treats it as one.
- **The refusal is a startup failure, "not a warning and not a log line"** (`07:152`). No
  flag, setting or environment disables it, in any environment.
- **Nothing durable lives only in Redis** (`07` FR-422). Any broker marker must be
  re-derivable, which is why DP-S1-2 exists.
- **The migration chain has exactly one head** (`07` FR-417).
- **Configuration errors surface at startup, never at first use** (`07` FR-447,
  `backend/src/app/config.py:75-83`).
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2): the `Job`
  field is declared once, in `packages/model-schema/src/model_schema/jobs.py`.
- **`pricing-core` gains no import** from this slice.

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `07` §3.6 | FR-436 | Whole: configured tenant id, DB marker at migration, refusal to start on mismatch, the same for blob storage and broker |
| `00` §3 | FR-18 | The Job half. The dossier half is carried to WK-680 (Acceptance 6) |

**Not in this slice**, each with where it goes:
- FR-267, FR-428, FR-429, FR-272 (audit limb), NFR-498 → Slice 2. FR-430, FR-431 → Slice 3.
  FR-268 → Slice 5. (Map plan scope table.)
- `07` FR-437's dated amendment moving FR-433 to Phase 3 (the #848 ruling's DP-1, which allows
  "Slice 1 or Slice 4") → **Slice 4**, whose scope is `deploy/`. Planner's slice-design
  choice: this slice changes nothing under `deploy/`, and the amendment belongs with the
  compose work it describes.
- Wiring the build identifier into container images → Slice 4 (the images do not exist yet).
  This slice reads it from configuration.

### Premises re-derived at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | No tenant identifier exists in configuration or schema | `git grep -n -i -E 'tenant_id\|tenant_marker'` over `backend/src packages/*/src` returns no code hit (two comment lines in `backend/src/app/api/deps.py:26-27` explaining ADR-710) |
| b | No build field exists on the Job | `git grep -n -E 'platform_version\|build_version\|platform_build\|build_sha'` over `backend/src packages/*/src docs/contracts` returns only `build_shap_summary` |
| c | `Settings` is frozen, `GIP_`-prefixed, `extra="forbid"`, and has `version: str = "0.1.0"` | `backend/src/app/config.py:84-100` |
| d | The API lifespan already hosts a startup refusal (FR-273), with a tested negative half | `backend/src/app/main.py:75-94`; `backend/tests/test_startup_self_check.py:23-45` |
| e | The blob bucket is ensured at startup | `main.py` lifespan calls `blob_store.ensure_bucket()`; `backend/src/app/platform/blobs.py:119` |
| f | The worker builds Celery from `Settings` and registers no start-up signal | `backend/src/app/worker/celery_app.py:30-54`; `git grep -n -E 'worker_process_init\|worker_init' backend/src` returns nothing |
| g | A Job becomes `running` in the worker, through `jobs.transition` | `backend/src/app/worker/tasks.py:133`; `backend/src/app/platform/jobs.py:226-227` sets `started_at` there |
| h | Alembic reads its URL from `Settings` | `backend/migrations/env.py:19,31` |
| i | FR-417's guard is a repository-invariant test | `tests/test_repository_invariants.py` |
| j | WK-680 (dossier) is Phase 3 and owns FR-376 | `docs/roadmap.md`, `### WK-680` row, `phase: P3` |

The executor re-reads each at its own tree and stops on any that no longer holds
([`README.md`](README.md) convention 4).

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S1-1 | What identifies "the platform version it ran on" (FR-18)? `Settings.version` defaults to `"0.1.0"` for every build, so it cannot attribute a figure "to the build that produced it" | (a) Record `Settings.version` as is; (b) add a `build` setting (the full commit SHA, set by the image build in Slice 4), required when `environment` is `dev`, `uat` or `prod` and defaulted to a fixed `local` marker otherwise, and record `"{version}+{build}"`; (c) derive it at runtime from git | **(b).** (a) records the same string for every build, which is the "not a single, knowable thing" FR-18 exists to prevent. (c) fails in an image, which carries no `.git`. (b) makes a missing build a startup error where attribution matters, and costs nothing locally | decision point | yes — Task 3 | |
| DP-S1-2 | FR-436's "the same check covers object storage and the broker where their configuration is per tenant": what is the marker in each? The spec says nothing more, and FR-422 forbids anything durable living only in Redis | (a) Blob: a marker object in the bucket, written when absent and compared when present. Broker: a marker key, written with set-if-absent and compared when present, so a flushed Redis re-arms rather than fails; (b) blob as (a), broker exempt on the grounds that its configuration is not per tenant; (c) neither — the database check alone | **(a).** The mistake the spec names — a restored backup, a copied `.env` — points a whole configuration at the other tenant, bucket and broker included, and the DB check alone misses a split configuration. (a)'s broker half never makes Redis a source of truth: losing the key loses nothing. (b) needs an argument that the broker's configuration is never per tenant, which `redis_url` being deployment configuration contradicts | decision point | yes — Task 4 | |

Both are the decision-maker's (`delivery-process.md` §3). Tasks 1–2 do not depend on either.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch.
- [ ] `uv sync --all-packages` (a fresh worktree without it reports hundreds of phantom mypy
  errors — `dev-commands`).
- [ ] Re-derive premises a–j; record the tree and each result in the ledger.
- [ ] `gh pr list --state open`, and read anything that rules on FR-436, FR-18, the Job
  contract or `Settings` ([`README.md`](README.md) convention 4). Name the SHA read.

### Task 1: Spec — `07` §4.1 `Job`

**Files:** Modify `docs/specs/07-platform.md` (§4.1 example and the prose after it).

- [ ] Add `"platform_build": "0.1.0+<commit sha>"` to the §4.1 example, placed after
  `trace_id`, in the form DP-S1-1 resolves.
- [ ] Add a dated paragraph after the `progress_at`/`stalled` note: the field, FR-18, that it
  is set when the Job moves to `running` and is null while `queued`, and that a retry records
  the build of the run that produced the result.
- [ ] Write DP-S1-1's and DP-S1-2's resolutions where the ruling that resolves them says
  (spec-change: a design choice is recorded, never silently picked).
- [ ] `python3 scripts/audit-docs.py`; quote the rc. Commit: `docs(specs): 07 §4.1 Job carries platform_build (FR-18, WK-674 S1)`.

### Task 2: `model-schema` — the `Job` field and the contract

**Files:** Modify `packages/model-schema/src/model_schema/jobs.py` (`class Job`, `:213`);
regenerate `docs/contracts/` with `scripts/generate-contracts.py`.

- [ ] **Red first:** a model-schema test that a `Job` round-trips `platform_build` and
  defaults it to `None`. Predicted failure: `extra="forbid"` rejects the unknown field — a
  different error is a plan defect.
- [ ] Add `platform_build: str | None = Field(default=None, description=…)` citing FR-18.
  Mirror the neighbouring `progress_at` field's form; do not invent a new idiom.
- [ ] Regenerate contracts; `generate-contracts.py --check` exits 0; run the contract guard
  (`contract-guard`) and quote its result.
- [ ] Commit.

### Task 3: The build setting and the Job column (FR-18) — after DP-S1-1

**Files:** Modify `backend/src/app/config.py` (`Settings`), `backend/src/app/db/models.py`
(`JobRow`, `:90`), `backend/src/app/platform/jobs.py` (`transition`, `:226`, and the
row-to-shape mapping near `:338`), `backend/src/app/worker/tasks.py` (`:133`); create one
Alembic revision; test `backend/tests/test_job_platform_build.py`.

- [ ] **Red first:** the four Acceptance 5 tests. Predicted failure: the attribute does not
  exist on the row or the shape.
- [ ] Add the setting per DP-S1-1, with its requiredness enforced by a validator in
  `Settings` so a missing value is a startup error (FR-447), and a `test_config.py` case for
  it.
- [ ] Add the nullable `platform_build` column to `JobRow` and in the revision (the column
  shares the Task 4 revision if both land together; either way the chain keeps one head).
- [ ] Set it where `transition` moves a Job to `running`, from the value the worker passes
  (the worker's own `Settings`, not the API's). Map it into the `Job` shape.
- [ ] Green; commit.

### Task 4: The tenant binding (FR-436) — after DP-S1-2

**Files:** Modify `backend/src/app/config.py` (a `tenant_id` setting: a constrained slug,
required when `environment` is `dev`, `uat` or `prod`, because a check whose configured side
is a default proves nothing there; in `local` a fixed default is acceptable), `backend/src/app/main.py` (lifespan),
`backend/src/app/platform/blobs.py`, `backend/src/app/worker/celery_app.py`; create
`backend/src/app/platform/tenancy.py` (the check, one function per store, and a
`TenantMismatchError` naming store, configured id and found id); the Alembic revision;
`backend/tests/test_tenant_binding.py`; `backend/tests/conftest.py` if `api_settings` needs
the new setting.

- [ ] **Red first:** the five Acceptance 4 tests. Each predicts `TenantMismatchError` naming
  its store; a startup failure of any other type is not the proof.
- [ ] The revision: create a single-row marker table (a primary key constrained to one
  value, so a second row is refused by the database), insert the configured `tenant_id`
  read through `load_settings()` as `env.py` already does, and drop the table on downgrade.
  A database migrated before this revision gets its marker from this revision, which is the
  "first migration" FR-436 means for an existing deployment.
- [ ] The lifespan runs the database, blob and broker checks after
  `assert_integer_minor_round_trip()` and **before** probes are registered or the bucket is
  ensured, so a mismatched process never reaches the other tenant's stores beyond reading
  their marker. The blob and broker markers follow DP-S1-2's resolution.
- [ ] The worker: a Celery start-up signal handler in `celery_app.py` runs the same checks
  and lets the exception stop the worker. Before relying on a specific signal's
  abort-on-raise behaviour, prove it with a failing test (or `library-spike`) — do not assume
  it.
- [ ] The migration test of Acceptance 3.
- [ ] Green; commit.

### Task 5: The gate and the ledger

- [ ] Run `tests/test_repository_invariants.py`, the migration round trip, then the full
  two-half gate on the committed tree. Quote every rc, the `N passed` line and `HEAD`
  against main's `N passed` (a total that did not move means the new tests were never
  collected).
- [ ] The ledger records: the tree, premises a–j, the red-first quotes, DP resolutions with
  their record ids, the FR-18 dossier carry to WK-680, and the map-plan deviation in Status.
- [ ] Item 11 (Acceptance 8).

## Hand-off

Slice 2 (the Environment and Deployment record) starts after this slice closes. Its leaf plan
also waits for the permission-catalogue ruling (#856), per the map plan's Task 2.

## Self-review

- **Scope against the map plan and the spec**: FR-436 and FR-18 are the only ids, both
  listed individually; the map's four gate items (per-store negative tests, reversible
  single-head migration, an FR-18 test, the full gate) are Acceptance 3, 4, 5 and 7.
- **FR-436 read to its clauses** (`07:152`): configuration, single-row marker at migration,
  refusal to start, "not a warning", blob and broker — each has a step and a test.
- **FR-18 read to its clauses** (`00:222`): "ran on" drives Task 3's recording point; the
  dossier clause is carried, not claimed; "any earlier `Job` migration should carry the
  column" — none has, premise b.
- **Literals** in this plan were checked against the tree above (premises); field and
  function names the executor adds are named as proposals, not as existing code.
- **Open**: DP-S1-1 and DP-S1-2, both the decision-maker's, both blocking only their own
  task.
