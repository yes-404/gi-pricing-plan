---
id: PL-1232
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
unminted, so they are cited by PR number, not by id, and not in `relates:`. They were
still unminted when this plan minted (2026-09-29), so the PR-number citations stand. Their
ids go into this plan's text and `relates:` once they mint, while this plan is still
`draft`.

## Status

**Draft**, filed 2026-09-29 against the tree above. It replaces the Slice 1 draft that
PR #892 carried until this commit (commit
`0d1c83bf9eaa00a4149c2bcf051d0448672d8c14`), which scoped Slice 2 and Slice 3 work under
the Slice 1 label and took its slice order from WK-672's map plan (`PL-930`); that file is
deleted here, and its number is not this plan's. **2026-09-29: working id 9104, minted
1232** at this PR's turn in the merge queue.

**Activation needs, in order:** the map plan (#843) minted and `active`; DP-S1-1, DP-S1-2 and DP-S1-3
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
   if the executor believes either needs a change, it stops and reports. The outcomes of
   DP-S1-1, DP-S1-2 and DP-S1-3 are written where their resolutions say.
   `python3 scripts/audit-docs.py` exits 0.
2. **Contract.** `uv run python scripts/generate-contracts.py --check` exits 0 after the
   regeneration, and the regenerated `Job` schema under `docs/contracts/` has a
   `platform_build` property. The field is declared once as a shape and once as a column,
   checked by count:
   - `git grep -n -E 'platform_build *:' -- packages/model-schema/src` prints **exactly one**
     line, in `packages/model-schema/src/model_schema/jobs.py`;
   - `git grep -n -E 'platform_build *:' -- backend/src frontend/src` prints **exactly one**
     line, the `JobRow` column in `backend/src/app/db/models.py`. (`frontend/src/api/generated`
     is VCS-ignored, so `git grep` does not see it.) Task 3 names the parameter that carries the
     value into `transition` `build`, not `platform_build`, so it does not count here; the
     row-to-shape mapping passes `platform_build=` with `=`, which the pattern does not match.
   Any other count fails this item.
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
   - database marker **absent**: two cases, each refused with an error naming `database` and
     saying the marker is missing. (i) The marker table exists and is empty. (ii) The
     database is not migrated to this slice's revision, so the table does not exist; the
     error tells the operator to run `alembic upgrade head`. Case (ii) cannot use the shared
     test database, which is a shared, already-migrated template (FD-1218,
     [`../findings/FD-01218-the-shared-test-database-template-gipricing-holds-a-whole-abandoned-test-session-and-a-stale-schema.md`](../findings/FD-01218-the-shared-test-database-template-gipricing-holds-a-whole-abandoned-test-session-and-a-stale-schema.md),
     records it holding a stale schema). It needs a
     scratch database upgraded only to this revision's `down_revision`: mirror the
     `scratch_database` fixture and `_upgrade(cfg, revision)` helper in
     `backend/tests/test_migration_dataset_owner.py:358-409`, and do not invent new ones. An absent database marker is
     **never** written by the application at startup: only the migration writes it (Task 4);
   - blob-bucket marker ≠ configured id → raises, naming `blob`;
   - broker marker ≠ configured id → raises, naming `broker` (per DP-S1-2's resolution);
   - **fresh deployment** (no bucket, no blob marker, no broker marker, database migrated):
     the app starts. After startup the bucket exists and both markers carry the configured id.
     A second `create_app` on the same stores starts too, and a third with a different
     configured id refuses, naming `database`. **Predicted red:** before Task 4 the app starts
     but writes no markers, so the test fails on its assertion that the blob marker holds the
     configured id after startup. A red from any other cause (the bucket missing, the app
     failing to start) is a plan defect;
   - the same database mismatch stops the **worker**: the worker-start hook raises before any
     task is consumed;
   - positive control: matching markers → the app starts.
   A test that goes red because the app failed to start for any **other** reason (a missing
   fixture, a connection refusal) has not proved FR-436 and is a plan defect.
5. **Provenance (FR-18), red first.** In `backend/tests/test_job_platform_build.py`, marked
   `@pytest.mark.req("FR-18")`: a Job moved to `running` by the worker path records the
   worker's configured build; a Job still `queued` has `platform_build` null; `GET` on the
   Job returns the field. (There is no re-run path to test: at the tree above
   `VALID_TRANSITIONS[RUNNING]` is `{SUCCEEDED, FAILED, CANCELLED}`
   (`packages/model-schema/src/model_schema/jobs.py:112-120`), and the worker ignores a
   redelivered Job that is not `queued` (`backend/src/app/worker/tasks.py:103-108`). A Job
   reaches `running` once, so it records one build. This slice builds no retry path.)
6. **Coverage.** `uv run python scripts/req-coverage.py` lists tests against FR-436 and FR-18.
   The **dossier half of FR-18** (`06` FR-376) is recorded in the slice ledger as *deferred
   with an owner — WK-680* (Phase 3; `docs/roadmap.md`'s WK-680 row lists FR-376), not
   claimed.
7. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree, with
   every command's rc, the `N passed` line and `HEAD` quoted in the ledger.
8. **Item 11.** Before the lead merges, the maintainer's **MERGE-ACK** entry, naming the
   PR's full head SHA, is recorded in the lead's channel file
   (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on the
   maintainer's behalf. That is step 6 of the maintainer's 2026-09-29 10:41:05 BST merge plan
   there, and `lead.md` rule 4 as amended by PR #893. (At the tree above rule 4 still reads
   "deputy's ACK"; #893 changes it.) **The ACK is never posted on the PR**: no teammate posts an
   ACK on GitHub. The slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean
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
| a | No tenant identifier exists in configuration or schema | Run on a `git archive` of the tree above: `grep -rn -i -E 'tenant_id\|tenant_marker' backend/src packages/*/src \| wc -l` prints `0`. The wider `grep -rn -i tenant backend/src packages/*/src` prints two lines, `backend/src/app/api/deps.py:26` and `:27`, a comment explaining ADR-710 |
| b | No build field exists on the Job | Run on the same export: `grep -rn -E 'platform_version\|build_version\|platform_build\|build_sha' backend/src packages/*/src docs/contracts` prints 6 lines, every one `build_shap_summary` (`build_sha` matches it as a substring) |
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
| DP-S1-3 | Three choices inside Task 4 that the spec leaves open: (i) is `tenant_id` required in every environment? (ii) how does the database refuse a second marker row? (iii) what are the blob and broker marker keys? | (i-a) Required in `dev`, `uat` and `prod`, with a fixed default in `local`; (i-b) required everywhere, with tests and the compose `.env` supplying it. (ii-a) A `smallint` primary key with `CHECK (id = 1)`; (ii-b) a boolean primary key with `CHECK (singleton)`; (ii-c) a unique index on a constant expression. (iii-a) Fixed names: blob object `_platform/tenant` holding the id as plain text, Redis key `gip:tenant`; (iii-b) names taken from new settings | **(i-a), (ii-a), (iii-a).** (i-a): in `dev`, `uat` and `prod` a check whose configured side is a default proves nothing, so the value must be supplied there; in `local` one developer's stack holds one tenant's throwaway data, so a fixed default costs no protection and no setup. (i-b) is stricter but adds a required value to every local and test configuration for no protection there. (ii-a) is the most readable of three equivalent mechanisms, and the database refuses the second row either way. (iii-b) is configuration for a fixed value | decision point | yes — Task 4 | |

All three are the decision-maker's (`delivery-process.md` §3). Tasks 1–2 do not depend on
any of them, except that Task 1's example value waits for DP-S1-1.

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

- [ ] Add `"platform_build"` to the §4.1 example, placed after `trace_id`. Its example value
  depends on DP-S1-1: under option (b), `"0.1.0+<commit sha>"`; under (a), `"0.1.0"`. Write
  the value only after DP-S1-1 is resolved.
- [ ] Add a dated paragraph after the `progress_at`/`stalled` note: the field, FR-18, that it
  is set when the Job moves to `running` and is null while `queued`.
- [ ] Write the resolutions of DP-S1-1, DP-S1-2 and DP-S1-3 where the ruling that resolves them says
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

- [ ] **First, the setting** per DP-S1-1, with its requiredness enforced by a validator in
  `Settings` so a missing value is a startup error (FR-447), and a `test_config.py` case for
  it, red then green. It comes before the tests below for the same `extra="forbid"` reason
  as Task 4's first step.
- [ ] **Red first:** the three Acceptance 5 tests. Predicted failure: the attribute does not
  exist on the row or the shape.
- [ ] Add the nullable `platform_build` column to `JobRow` and in the revision (the column
  shares the Task 4 revision if both land together; either way the chain keeps one head).
- [ ] Set it where `transition` moves a Job to `running`, from a keyword parameter named
  `build` that the worker passes (the worker's own `Settings`, not the API's). Name it
  `build`, not `platform_build`: Acceptance 2 counts `platform_build *:` declarations, and a
  parameter of that name would be a second one. Map the column into the `Job` shape.
- [ ] Green; commit.

### Task 4: The tenant binding (FR-436) — after DP-S1-2

**Files:** Modify `backend/src/app/config.py` (a `tenant_id` setting, required as DP-S1-3 resolves), `backend/src/app/main.py` (lifespan),
`backend/src/app/platform/blobs.py`, `backend/src/app/worker/celery_app.py`; create
`backend/src/app/platform/tenancy.py` (the check, one function per store, and a
`TenantMismatchError` naming store, configured id and found id); the Alembic revision;
`backend/tests/test_tenant_binding.py`; `backend/tests/conftest.py` if `api_settings` needs
the new setting.

- [ ] **First, the `tenant_id` setting** (per DP-S1-3), with its `test_config.py` case, red
  then green. It has to come before the tests below: `Settings` has `extra="forbid"`
  (`backend/src/app/config.py:91-96`), so a test that passes `tenant_id` before the field
  exists goes red on validation, which is the wrong cause.
- [ ] **Red first:** the Acceptance 4 tests. Before the checks exist, each negative test's
  predicted red is that startup does **not** raise (`pytest.raises` reports it did not);
  the fresh-deployment test's is the one Acceptance 4 names. Once green, each negative test
  gets `TenantMismatchError` naming its store; an absent database marker gives the same error
  with the found id reported as absent. A red or a startup failure of any other kind is not
  the proof.
- [ ] The revision: create a single-row marker table, with a second row refused by the
  database by the mechanism DP-S1-3 resolves. Insert the configured `tenant_id`, read through
  `load_settings()` as `env.py` already does (`backend/migrations/env.py:19,31`). Drop the
  table on downgrade. A database migrated before this revision gets its marker from this
  revision, which is the "first migration" FR-436 means for an existing deployment.
  **This stamp trusts configuration.** When the revision runs against a pre-existing
  database, it writes whatever `tenant_id` the migrating process was given. If that
  configuration is the "copied `.env`" FR-436 names, the wrong id is stamped, and the check
  then protects the wrong binding. This cannot be avoided: before this revision no database
  records its tenant, so nothing exists to check the configuration against. What the slice
  does instead: the revision prints the id it stamps, so the operator sees it in the
  migration output, and the stamp is written once, so any later drift is caught. The same
  holds for the blob and broker markers written when absent (DP-S1-2 (a)).
- [ ] The lifespan order, after `assert_integer_minor_round_trip()` and before the probes
  are registered:
  1. **Database check**, read-only. A mismatch or an absent marker stops startup. This runs
     before any write to any store, so a configuration pointing at another tenant's database
     stops before it touches object storage or the broker.
  2. **`blob_store.ensure_bucket()`**, moved up from its current place
     (`backend/src/app/main.py:92`). The bucket must exist before its marker can be read or
     written: `ensure_bucket` runs `head_bucket` and creates the bucket only when that fails
     (`backend/src/app/platform/blobs.py:119-128`). `_ensure` catches **any** `ClientError`
     from `head_bucket`, including a 403, and then calls `create_bucket`. So when the
     credentials cannot read a bucket that exists (another tenant's, or a permissions
     mistake), `create_bucket` raises its own `ClientError` and startup stops with an S3
     error, not a `TenantMismatchError`. That still refuses to start, which is what FR-436
     requires, and this slice does not change `ensure_bucket`. For a bucket the credentials
     *can* read, `head_bucket` succeeds and nothing is written.
  3. **Blob marker**, per DP-S1-2: read it; if absent, write the configured id; if present
     and different, stop. On a fresh deployment step 2 has just created the bucket, so the
     marker is absent and gets written.
  4. **Broker marker**, per DP-S1-2: set-if-absent, then read and compare.
  5. The existing probe registration, then `yield`.
  Acceptance 4's fresh-deployment case proves this order.
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
- **Open**: DP-S1-1, DP-S1-2 and DP-S1-3, all the decision-maker's. DP-S1-1 blocks Task 3
  (and Task 1's example value); DP-S1-2 and DP-S1-3 block Task 4.
- **No retry path is assumed**: a Job reaches `running` once (Acceptance 5's note).
