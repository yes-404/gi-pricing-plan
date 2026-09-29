---
id: RL-1253
family: ruling
title: WK-674 Slice 1, DP-S1-1 to DP-S1-3 — the build marker, the store markers, and the tenant binding's shape
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: decision-maker
tree: f0c3d197f5d89863efc647a2d7c1a6994b74dd63
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1239, RL-1232]
---

# RL-1253 — WK-674 Slice 1, DP-S1-1 to DP-S1-3: the build marker, the store markers, and the tenant binding's shape

## Verified first, at f0c3d197f5d89863efc647a2d7c1a6994b74dd63

**The plan these rule on** is `PL-1239`, WK-674 Slice 1's leaf plan, which is on `main`. Its
Decision points table is at `:233-235`: DP-S1-1 blocks Task 3, and DP-S1-2 and DP-S1-3 block
Task 4. All three are technical (`delivery-process.md` §3; the maintainer's STRUCTURE entry
§1), so this role rules them, and none goes to the maintainer. **The plan is not edited**
(§1.6, the PL row). The planner applies this record.

Filed under working id 9690 (first filed as 9680, which PR #918 had taken 23 seconds earlier as a
plan id; 9690 was free on all 107 remote branches); minted `RL-1253` at its merge turn, 2026-09-29
(`doc-id.py next --ref origin/main` at `90675848`).

**The requirements, read at their rows:**
- `00` FR-18 (`00-overview.md:222`): *"Every Job records the platform version it ran on … a
  figure reproduced two years later must be attributable to the build that produced it."*
- `07` FR-436 (`07-platform.md:152`): *"the database carries the same identifier in a
  single-row marker written at first migration, and the application refuses to start when
  they disagree … The same check covers object storage and the broker where their
  configuration is per tenant."*
- `07` FR-422 (`07-platform.md:116`): *"Nothing durable lives only in Redis."*

**The mechanisms each option builds on.** Each line below was read with `sed -n` at this tree.
- **Settings** (`backend/src/app/config.py`):
  - `Environment` has `local`, `dev`, `uat` and `prod` (`:31-37`).
  - `Settings` reads `GIP_`-prefixed environment variables, with `extra="forbid"` and
    `frozen=True` (`:91-96`).
  - `version: str = "0.1.0"` is fixed for every build (`:100`).
  - `require_startable()` (`:191`) already refuses to start on environment-specific rules,
    for example *"environment=prod requires an OIDC issuer"*. `load_settings` calls it
    (`:261`).
- **The blob store** (`backend/src/app/platform/blobs.py`):
  - `BlobStore` (`:108`) holds a boto3 client.
  - Content keys are `blob/{sha256[:2]}/{sha256}` (`blob_key`, `:73-79`).
  - `read_scratch` (`:316`) already maps `NoSuchKey`/`404` to `None`, which is the read the
    marker needs.
  - GC deletes only keys it derives from `BlobRow` rows (`collect_garbage`, `:365`;
    `blob_key(blob.sha256)` at `:406`).
  - The scratch sweep lists and deletes only under `scratch/` (`:336-363`).
  - So a key outside `blob/` and `scratch/` is outside both deleting paths.
- **The broker:** `redis.asyncio` is already a dependency (`backend/src/app/platform/diff_cache.py:73-75`),
  and its keys are namespaced by purpose (`rate_table:diff:…`, `:88`). The compose Redis runs
  `--appendonly no` (`deploy/docker-compose.yml:26`), so **every Redis restart empties it**,
  and a broker marker is re-written on every restart as a matter of course.
- **The image:** `git ls-files` finds no `Dockerfile` at this tree. The image and its build
  are Slice 4's (`RL-1232` Part A).
- **The tests:** ~~9 places in `backend/tests`~~ *(corrected 2026-09-29, auditor-b-2's note N2. The first count's command was not the predicate
  stated here: it added a `|GIP_ENVIRONMENT` alternative, which matched two more lines,
  `test_demo_command.py:36` and `:44`, so 7 + 2 = 9. `deploy` and `.github` give 0 either way.
  The cause first given, that the predicate ran over `deploy` and `.github`, was itself wrong,
  and is corrected here.)* **3 places** in `backend/tests` construct settings
  with `environment` set to `dev`, `uat` or `prod`: `test_config.py:67`, `:73` and `:87`, each a
  `load_settings(environment=Environment.PROD, …)`. They were found with
  `git grep -nE 'environment\s*=\s*("|Environment\.)(dev|uat|prod|DEV|UAT|PROD)' -- backend/tests`,
  which gives 7 lines. The 4 further matches are not settings: `test_score.py:1070`,
  `test_traces.py:395` and `test_traces_api.py:172` are trace-write arguments, and
  `test_score.py:1139` is a `Caller` field.
  - `:67` and `:87` assert other refusals, TLS and the OIDC issuer. The executor keeps their
    order, so each test still fails for its own reason.
  - `:73` expects startup to succeed, so it must supply both new values.
  - That is a fixture cost, and it is not a reason against either option.

## Ruled

### DP-S1-1: what identifies "the platform version it ran on" (FR-18): **(b), amended**

**The ruling.**
- A `build` setting (`GIP_BUILD`) carries the full commit SHA of the image.
- In `dev`, `uat` and `prod` it is **required, and must be 40 lowercase hex characters**. A
  missing or malformed value is a startup failure in `require_startable()`, citing FR-18.
- In `local` it defaults to the fixed marker `local`.
- The Job records `"{version}+{build}"`, for example `0.1.0+local` or
  `0.1.0+3f7bddda…` in full.

**The amendment** is the format check. The plan's (b) requires a value, and any value would
satisfy it. A deployment that sets `GIP_BUILD=latest` or `unknown` then records the same string
for every build, which is (a)'s failure again, in a different spelling. Requiring a full SHA
makes the recorded value name exactly one build. The `local` marker is refused outside
`local`, because the format check rejects it.

**Why not the others.**
- (a) records `0.1.0` for every build, so it names nothing (`config.py:100`).
- (c) needs `.git` at runtime, and an image carries none.

**Where it is set:** by Slice 4's image build (a build argument passed into the environment).
Until Slice 4 there is no `dev`, `uat` or `prod` deployment to require it of, apart from tests,
which supply it.

### DP-S1-2: the blob and broker markers (FR-436): **(a), as recommended**

**The ruling.**
- **Blob:** a marker object in the configured bucket. Read it. If it is absent, write the
  configured `tenant_id`. If it is present and different, stop.
- **Broker:** a marker key, written with set-if-absent, then read and compared. If it is
  different, stop.
- The order is the plan's: the database check first, which is read-only, then
  `ensure_bucket`, the blob marker, and the broker marker.

**Why (a).**
- FR-436 names *"a copied `.env`"*, which points every store at the other tenant, and the
  database check alone misses a configuration split across stores.
- Both markers sit outside every deleting path: the blob key is outside `blob/` and
  `scratch/`, and the Redis key is outside every existing namespace.
- The broker marker never makes Redis a source of truth, because losing it loses nothing
  (FR-422).
- (b) would need the broker's configuration never to be per tenant. `redis_url` is
  per-deployment configuration (`config.py`), so (b)'s premise does not hold.
- (c) leaves the split-configuration case open.

**The known limit, stated rather than hidden.** Redis is emptied on every restart
(`--appendonly no`), so the broker check detects a mismatch only while the key exists. After a
restart, the first process to connect writes its own id. If that process is misconfigured and
connects first, it arms the key with the wrong id, and the correctly configured process that
follows stops. ~~That is still a refusal to start, visible and named, so it is detection
delayed by one process, not a silent pass.~~ *(Corrected 2026-09-29, auditor-b-2's note N1: that understated
the limit.)* The misconfigured process starts and serves until the correctly configured process
reaches the broker. If it never does, the mismatch is not detected. In that case the process
has the right database and blob marker and is pointed at another tenant's emptied Redis, so it
writes its own id, starts, and may enqueue or consume on the wrong broker. The database check runs first and stops a process
pointed at the wrong database before it reaches the broker at all. That covers only the wrong-database case, and not the one
above.

### DP-S1-3: requiredness, the single-row mechanism, and the key names: **(i-a) amended, (ii-a), (iii-a)**

**(i-a), amended.**
- `tenant_id` (`GIP_TENANT_ID`) is **required in `dev`, `uat` and `prod`**. There it must be
  non-empty and must not equal the local default. The check is a startup failure in
  `require_startable()`, citing FR-436.
- In `local` it defaults to the fixed id `local`.
- This matches DP-S1-1's environment split. The amendment refuses a strict environment
  configured with the local default, which would otherwise pass as "supplied" while carrying
  no tenant.
- (i-b) adds a required value to every local and test configuration and buys no protection
  there. One developer's stack holds one tenant's throwaway data.

**(ii-a).**
- The marker table's primary key is `smallint` with `CHECK (id = 1)`, and it holds the tenant
  id column. The database refuses a second row.
- It is the most readable of three equivalent mechanisms, and PostgreSQL 16 (FR-416)
  enforces a `CHECK` on insert. (ii-b) and (ii-c) refuse the same second row less legibly.

**(iii-a).**
- The blob marker object is `_platform/tenant`, holding the id as plain text.
- The Redis key is `gip:tenant`.
- Both names are fixed. They sit outside `blob/` and `scratch/` and outside every existing
  Redis namespace. New settings for them, (iii-b), would be configuration for a fixed value,
  and they would add two more places a copied `.env` could disagree.

## What it obliges

- **The planner:** applies this record to `PL-1239`, with the `Resolved by` cells citing it
  and Task 1's example value per DP-S1-1. Then it sets the plan `active`.
- **Slice 1, Task 3:**
  - adds the `build` setting with DP-S1-1's validation in `require_startable()`;
  - records `"{version}+{build}"` on the Job as the plan's `platform_build`, set at the
    `running` transition from the worker's settings.
- **Slice 1, Task 4:**
  - adds the `tenant_id` setting with DP-S1-3 (i)'s validation;
  - adds the marker table per (ii-a);
  - adds the markers per DP-S1-2 and (iii-a), in the plan's order.
- **Slice 4:** its image build sets `GIP_BUILD` to the full commit SHA.
- **Not decided here:** the tenant id's format beyond "non-empty, not the local default". No
  requirement specifies one, and the markers store it as opaque text.

## Acceptance — the violation that must become detectable

The violation: **a Job whose recorded platform version does not name one build, or a process
that starts while any store is bound to a different tenant.** Slice 1's tests carry the
checks, each shown red on deliberately broken input:

- **DP-S1-1.**
  - *Violation: `environment=prod`, `uat` or `dev` starts with `GIP_BUILD` unset, set to
    `local`, or set to a value that is not 40 lowercase hex characters.* It must refuse at
    startup with `SETTING_INVALID`.
  - *Violation: a Job reaching `running` records a platform version other than
    `"{version}+{build}"` from the worker's settings.*
- **DP-S1-2.**
  - *Violation: the blob marker holds another tenant's id, and startup succeeds.*
  - *Violation: the broker key holds another tenant's id, and startup succeeds.*
  - *Violation: on a fresh deployment (no markers), startup fails, or does not write both
    markers.*
- **DP-S1-3.**
  - *Violation: a second marker row is inserted and the database accepts it.*
  - *Violation: `environment=prod` starts with `GIP_TENANT_ID` unset or set to the local
    default.*
  - *Violation: the database marker disagrees with the configured id, and startup
    succeeds.*
