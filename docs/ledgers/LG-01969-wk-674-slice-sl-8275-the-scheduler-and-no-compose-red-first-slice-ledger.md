---
id: LG-1969
family: ledger
title: WK-674 slice SL-1968 — the scheduler service and the demo's --no-compose switch, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29               # drafted 2026-10-29 under working id 8276
owner: executor
tree: 7ceff4a16829c63f20f0cdbb56fafae22657c1ab   # origin/main at the branch cut
slice: SL-1968
phase: P2
work: WK-674
plans: [PL-1688]
corrected_by: []
relates: [FD-1661, PL-1688]
---

# LG-1969 — WK-674 slice SL-1968: the scheduler service and `--no-compose`, red first

Drafted under working ids **SL 8275** (this slice), **LG 8276** (this ledger) and **FD 8280** (the finding filed in the slice), minted
as **SL-1968**, **LG-1969** and **FD-1970** on 2026-10-29. Plan of record: `PL-1688` row 2 (accepted at `7e3555eb`). Executor seat `exec-beatreds`.

**GO:** the lead's grant "2026-10-29 17:27:16 GMT" ("The reds may start now"). **MERGE-ACK:** pending.

## Tasks

### Scope

`PL-1688` row 2, items R0 to R2, G and A1 to A8. Tonight: R0 (starting hunks) and the reds of R1.a to R1.d and R2.a to R2.c only.

### Task list

- [x] R0 plan row merged; premises re-checked (see "Reds" below).
- [x] R1 shape tests red by cause; R2 tests red by cause (R2.c a green control).
- [ ] Compose `scheduler` block, `--no-compose` flag, runtime tests and `beat_fixture` rewiring, gate, audit, mint: not started.

### Gate

Not run. No full gate tonight.

### Audit

Not started.

### Build log

- 2026-10-29: reds only, below.

## PRs

None yet.

## Reds (2026-10-29)

Tonight is the reds only: tests, no production edit (no `deploy/docker-compose.yml`, no
`scripts/demo.py`), no database, no docker.

### The plan row merged

`git merge --no-ff origin/draft/pl-8281` onto `draft/sl-8275` (cut from `origin/main`
`7ceff4a16829c63f20f0cdbb56fafae22657c1ab`): no conflict, merge commit `06caa8b9`, one file added
(`docs/plans/PL-01688-…`, 167 insertions).

### Premises re-checked at `7ceff4a1`

| Premise | At `7ceff4a1` |
|---|---|
| no `scheduler` service in `deploy/docker-compose.yml` | holds (`git grep -n scheduler -- deploy/docker-compose.yml` prints nothing) |
| `check_compose_up` at `scripts/demo.py:317` | holds |
| the local demo's compose call at `scripts/demo.py:478-486` | holds (command list opens at `:481`) |
| `beat_fixture` definition and callers (R1.e list) | holds (`deploy_stack_helpers.py:270`; `test_deploy_stack_runtime.py:45,311,457,503,582`; `test_deploy_switch_runtime.py:5,38,174`) |
| `app.conf.beat_schedule` in `backend/src/app/worker/entrypoint.py` | holds (`:60`) |
| S1c-5 setup fault 2 in `LG-1964` (`Permission denied: 'celerybeat-schedule'`) | holds (`LG-1964` line 396) |

No premise differs.

### Ported hunks (tests only; the sl-1689 branch was read with `git show`, never checked out)

| Test or check | Source |
|---|---|
| `_beat_words`, `scheduler_runs_beat_from_the_one_image` (split: profile limb became `scheduler_is_under_the_app_profile`, the `--schedule` limb became R1.c), test `test_the_scheduler_runs_beat_from_the_one_image` | `c80009ad`, `backend/tests/test_deploy_stack.py` |
| `scheduler_is_one_process`, `test_the_scheduler_is_one_process` | `c80009ad` |
| `scheduler_starts_after_its_dependencies`, `test_the_scheduler_waits_for_migrate_and_redis` | `c80009ad` |
| `test_the_scheduler_exists_under_the_app_profile` (R1.a), `test_the_scheduler_keeps_its_beat_schedule_file_under_tmp` (R1.c) | new here (R1.c cites S1c-5 setup fault 2) |
| every `frontend` hunk, the `_break_scheduler_*` breaker rows, `1cc2fe80`, `32257078` | not taken tonight (breakers would fail by `KeyError` at the base, not by cause; the runtime tests and `beat_fixture` are the build window's) |

R2 (`backend/tests/test_demo_command.py`) is new here.

### The red run

Tree: `draft/sl-8275` at `06caa8b9` plus the two test files (committed after as `e09a212e`, `9cfb408f`).
Command: `~/gi-pricing-plan.local/handover/run-small.sh <wt> backend/tests/test_deploy_stack.py backend/tests/test_demo_command.py`, rc=1.

```
FAILED backend/tests/test_deploy_stack.py::test_the_scheduler_exists_under_the_app_profile
FAILED backend/tests/test_deploy_stack.py::test_the_scheduler_runs_beat_from_the_one_image
FAILED backend/tests/test_deploy_stack.py::test_the_scheduler_keeps_its_beat_schedule_file_under_tmp
FAILED backend/tests/test_deploy_stack.py::test_the_scheduler_is_one_process
FAILED backend/tests/test_deploy_stack.py::test_the_scheduler_waits_for_migrate_and_redis
FAILED backend/tests/test_demo_command.py::test_no_compose_runs_no_compose_up
FAILED backend/tests/test_demo_command.py::test_no_compose_refuses_before_migrations_naming_the_service_that_is_down[postgres]
FAILED backend/tests/test_demo_command.py::test_no_compose_refuses_before_migrations_naming_the_service_that_is_down[redis]
FAILED backend/tests/test_demo_command.py::test_no_compose_refuses_before_migrations_naming_the_service_that_is_down[minio]
FAILED backend/tests/test_demo_command.py::test_no_compose_refuses_before_migrations_naming_the_service_that_is_down[keycloak]
ERROR backend/tests/test_demo_command.py::test_the_seed_record_pre_flight_refuses_a_workspace_the_database_lost
ERROR backend/tests/test_demo_command.py::test_the_seed_record_pre_flight_refuses_an_analyst_who_is_not_a_member
10 failed, 48 passed, 2 warnings, 2 errors in 3.48s
```

Each new test's E-line:

| Test | E-line |
|---|---|
| `test_the_scheduler_exists_under_the_app_profile` | `AssertionError: assert ['no service named scheduler'] == []` |
| `test_the_scheduler_runs_beat_from_the_one_image` | `AssertionError: assert ['no service named scheduler'] == []` |
| `test_the_scheduler_keeps_its_beat_schedule_file_under_tmp` | `AssertionError: assert ['no service named scheduler'] == []` |
| `test_the_scheduler_is_one_process` | `AssertionError: no service named scheduler` |
| `test_the_scheduler_waits_for_migrate_and_redis` | `AssertionError: assert ['scheduler d...o be healthy'] == []` (left has: does not wait for migrate to complete; does not wait for redis to be healthy) |
| `test_no_compose_runs_no_compose_up` | `SystemExit: 2` (argparse: the flag is absent) |
| `test_no_compose_refuses_before_migrations_naming_the_service_that_is_down[postgres,redis,minio,keycloak]` | `SystemExit: 2` each |

**Control (green at the base, as planned):** `test_without_no_compose_the_infrastructure_is_still_started_by_compose` (R2.c) passed.

**Not run: DB-backed, lane is DB-free (excluded from the red count by node id).** Two existing tests ERROR in `database` fixture setup, identically with and without this slice's test edits:

- `backend/tests/test_demo_command.py::test_the_seed_record_pre_flight_refuses_a_workspace_the_database_lost`
- `backend/tests/test_demo_command.py::test_the_seed_record_pre_flight_refuses_an_analyst_who_is_not_a_member`

E-line (`backend/tests/conftest_db.py:143`): `RuntimeError: GIP_TEST_DATABASE_URL is not set, and the per-worktree test database '<name>' does not exist yet. Refused rather than silently falling back to the shared 'gipricing' database …`.

Control (lead's order, 2026-10-29): `backend/tests/test_demo_command.py` alone, via run-small, on a clean detached throwaway worktree at `06caa8b99cf50725e7d69c654ad6fb836776cef7` (no test edits; run-small refuses node ids, so the whole file ran): `27 passed, 2 warnings, 2 errors in 2.10s`, rc=1, the same two ERROR node ids, the same `RuntimeError`, database name `gipricing_sl-8275-base_a3cf631f` (the red run's: `gipricing_sl-8275_cae0e2f1`). So the errors are the lane, not the change.

Checks: `ruff check` on the two files rc 0. `ruff format --check`: `test_demo_command.py` clean; `test_deploy_stack.py` reports one hunk at line 71, in code the slice did not touch (`origin/main`'s copy gives rc 1 too with ruff 0.17.1); the slice's own hunks are clean.

## Build log — Phase 1 (2026-10-29, exec-beatgreen)

- Base: draft/sl-8275 `75938ac8` re-merged with origin/main `1e17ec63` (merge `90ef474d`, docs-only, no conflicts).
- Taken from SL-1689 (read-only, `git show`): `c80009ad` `scheduler` block of `deploy/docker-compose.yml`
  only; `1cc2fe80` the runtime test `test_the_scheduler_service_is_what_moves_a_job_out_of_the_outbox`;
  `32257078` `one_beat_problems`, the rewired `beat_fixture` and its 5 one-beat tests. No `frontend` hunk.
- `scripts/demo.py`: `--no-compose` and `check_infrastructure_up` (the four-service check; `check_compose_up`
  would also demand `lb`/`api`, which the flag's R2.a green forbids). `deploy/README.md` and
  dev-commands SKILL.md gain their lines.
- Shape greens via run-small at `e7d6e69f`: `63 passed, 2 errors`, rc=1; the 2 errors are the existing DB-fixture
  tests `test_the_seed_record_pre_flight_*` (no per-worktree DB; Phase 1 is DB-free), not slice tests.
- Format-only commit: `ruff format backend/tests/test_deploy_stack.py` alone; script `ast.dump` sha256, before
  = after = `f8528fa3ac4e566dbcd714d39445791cae175506976d4c421daf9bb9813e8a50` (3 lines changed).
- `ruff check .` rc=0; `mypy` rc=0 (Success, 251 files).

## Deviation — R2.b, `check_infrastructure_up` (2026-10-29, exec-beatgreen; accepted by the lead pending the maintainer's word)

- **What R2.b says:** with the flag the demo "reuses `check_compose_up` (`scripts/demo.py:317`)".
- **Why reuse fails:** `check_compose_up` refuses on `compose_services() - running.keys() - {"api"}`, and
  `compose_services()` (`scripts/demo.py`, the function of that name) returns
  `{"postgres", "redis", "minio", "lb", "api", *{f"worker-{queue.value}" for queue in DEFAULT_QUEUE_FOR_KIND.values()}}`.
  It names `lb`, `api` (x2) and the worker pools, which `--no-compose` does not start, and it does not name
  `keycloak`, which R2.b requires. With only the four infrastructure services up, as in R2.a, it would refuse
  and R2.a's green (`alembic upgrade` reached) could not hold.
- **What was done instead:** `INFRASTRUCTURE_SERVICES = {postgres, redis, minio, keycloak}` and
  `check_infrastructure_up(running)`, which raises `DemoRefusedError` naming each missing one. It takes the
  same `compose_running()` input as `check_compose_up`. `check_compose_up` is unchanged.
- **Acceptance:** the maintainer accepted this deviation at `to-lead.md` entry "2026-10-29 18:52:58 GMT". The reason
  given: DP-3's object was "any of the four shared services that is down", and `check_compose_up` checks the app
  services, not keycloak.

(Recorded 2026-10-29 by the lead, on to-lead "2026-10-29 18:57:05 GMT": the gate script's template-guard red-proof (exec-beatgate; disposable copy scratch_beatgate_guard from gipricing: exact list rc 0; one planted environments row → environments=4, rc 1; dropdb rc 0; template re-read exact) ran inside S1d's DB window (18:53 → ≤ 19:53), between 18:54 and 18:56, under the lead's brief, which wrongly allowed it there. A DB window is single-tenant. The proof STANDS; the breach is recorded, not repeated. The maintainer's read at 18:57:05: template alembic_version=1 environments=3 tenant_marker=1; no beatgate database left. Script: scratch/sl8275-gate/sl8275-gate.sh sha256 7fbaa097f0c92e7083a3a2e1b189cb40d8b91a5b165acec85327974fdaa84d98.)

## Build window — 2026-10-29 19:05 GMT onward (exec-beatgreen; project `gip-s4-runtime`, own volumes; never the shared stack)

Image `gi-pricing-app:125779310f8528a300480357d050792ea3bcada2`, built with `docker build` from a `git archive` of that head.
Drivers (scratch, not committed): `~/gi-pricing-plan.local/scratch/sl-8275-exec/{reds,onebeat}.py`; logs `reds2.log`, `onebeat.log`, `caller1-red.log`.
The project's own Postgres was provisioned by hand (`scripts/provision-app-role.py --allow-default-password`, rc 0) — see F2.

- **A3 (rc 0 for the driver):** RED1, no scheduler: `RED1 job 01a18914-867a-7ab3-b230-d2506b0b7a4c status queued | outbox: pending|1`.
  RED2, scratch override without `--schedule` (never committed): `scheduler exited exit=1 Exited (1) 14 seconds ago`, log
  `_gdbm.error: [Errno 13] Permission denied: 'celerybeat-schedule'`. GREEN: `GREEN job status succeeded scheduler: running | outbox: published|1`.
- **F1 (found in the window; fixed in its own commit):** `docker compose ps --format json` truncates `Command` (`"celery -A app.worke…"`), so the
  ported `one_beat_problems` saw no ` beat` in any row. RED, before the fix, on a correct single scheduler:
  `ONE problems: ['0 beat containers running, not exactly 1']`. The fix is `--no-trunc` in `beat_fixture`'s `ps` call.
  GREEN after it: `ONE problems: []`; RED against a real double beat (`worker-default run -d … beat`): `DOUBLE problems: ['2 beat containers running, not exactly 1']`;
  after removing the extra: `AFTER-RM problems: []` (rc 0).
- **F2 (base defect, not this slice's; held for the maintainer's ruling):** since S1c the compose `api` exits 3
  (`password authentication failed for user "gip_app_login"`) unless `provision-app-role.py` has run on the stack's Postgres after `migrate`;
  the owner seed also needs `GIP_TEST_DATABASE_URL`. An unprovisioned role also kills beat on its first relay tick (`scheduler exited`).
  The unchanged caller `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker` at head `1a3a8483463b42eee4a877068b9d8fe743b9b5f2`
  under `GIP_DEPLOY_TESTS=1`: `1 failed, 2 warnings in 46.16s`, rc=1 (`CalledProcessError` from `docker compose … up`, then the conftest_db `GIP_TEST_DATABASE_URL is not set` warning).

## F2 — the compose runtime tests never provisioned the application login role (found 2026-10-29 in the build window; ruled (A) by the maintainer at to-lead "2026-10-29 19:19:28 GMT"; finding FD-1970, MEDIUM, owner WK-674, drafted by the auditor from these lines)

- **The defect, proven at `origin/main` `1e17ec6382de5919b6e3011242b584a59bb880e7`** (condition (iii); a throwaway detached checkout
  `.claude/worktrees/exec-beatgreen-main`, not the slice worktree): `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker`
  under `GIP_DEPLOY_TESTS=1` → `1 failed, 2 warnings in 42.28s`, rc=1. The `api` container: `exited exit=3`, log
  `password authentication failed for user "gip_app_login"`. Cause: `gip_app_login` exists on a fresh volume with no password until
  `scripts/provision-app-role.py --allow-default-password` runs (`deploy/docker-compose.yml`, the postgres volume comment: "the compose run calls
  scripts/provision-app-role.py"); no runtime test calls it. This record does not say since when; only that it holds at `1e17ec63`.
  A second effect: an unprovisioned role kills beat on its first relay tick (`scheduler exited`).
- **The fix (A)**, `backend/tests/deploy_stack_helpers.py`: on a project's first `up`, `compose()` brings up the project's own postgres, then
  builds the owner URL from the mapped port, then runs `migrate`, then `provision-app-role.py --allow-default-password` against it, then sets
  `GIP_TEST_DATABASE_URL` to that URL; `down` resets both.
- **(i) the refusal, red then green.** `own_postgres_owner_url(port)` raises on the shared 5432 *before* any DDL. Test
  `test_provisioning_refuses_the_shared_postgres_port_and_names_the_projects_own` (`backend/tests/test_deploy_stack.py`), run-small:
  RED on a stub with no guard: `Failed: DID NOT RAISE ValueError`, `1 failed, 30 passed`, rc=1 (head `d72b064e` + the stub);
  GREEN with the guard: `31 passed`, rc=0.
- **(ii) the env does not leak.** `envcheck.py` at `c6716e04`: `before: None`; `after up: postgresql+asyncpg://gipricing:gipricing@127.0.0.1:32833/gipricing`
  (the project's own ephemeral port) with `provisioned: ['gip-s4-runtime']`; `after down: None` with `provisioned: []`; and in the shell after the run
  `env | grep GIP_TEST_DATABASE_URL` is empty, `grep` rc=1.
- **The five `beat_fixture` callers under `GIP_DEPLOY_TESTS=1` at `c6716e048dc4bd98babeca0a4c7a709a7c17f2c5`:** `test_a_submitted_job_reaches_a_terminal_state_…` and
  `test_a_dataset_ingest_job_succeeds_…`: `2 passed in 132.40s`, rc=0; `test_a_score_batch_job_succeeds_…` and `test_a_sampled_trace_is_produced_…` with the switch test:
  `1 failed, 2 passed in 174.26s`, rc=1 — the failure is `test_deploy_switch_runtime.py::test_a_deploy_switches_every_api_process_and_a_default_live_quote_is_served`,
  which brings up no `lb`/`api`/worker and has no `down` fixture (its docstring: "UNPROVEN … no stack was run for it"). See the F3 section below.

## F3 — the switch test started no stack (found 2026-10-29 in the build window; ruled (A) by the maintainer at to-lead "2026-10-29 19:31:32 GMT")

- **Red, the present failure** (head `c6716e04`, `GIP_DEPLOY_TESTS=1`): `FAILED backend/tests/test_deploy_switch_runtime.py::test_a_deploy_switches_every_api_process_and_a_default_live_quote_is_served`,
  `subprocess.CalledProcessError` from `docker compose … port postgres 5432` inside `governed_workspace` → `compose_settings` → `mapped` (the stack was never started), and the run left
  `gip-s4-runtime` postgres, redis and the exited migrate and scheduler containers up (4 containers, removed by project label).
- **The edit**, its own commit (`870d08f5`): the test takes `down` and runs `up -d --wait lb <workers>` (`_worker_services`, as the other four callers do). Write-set amendment: PL-1688 row 2's dated line of 19:31:32.
- **Green at `870d08f5ce68c06ef4ba345b55114ca29208e477`, `GIP_DEPLOY_TESTS=1`:** `1 passed, 2 warnings in 71.75s`, rc=0; 0 containers left by project label. The "UNPROVEN" docstring sentence is replaced by a dated one naming this run.
- **All five `beat_fixture` callers are therefore green under `GIP_DEPLOY_TESTS=1`:** the four of F2 at `c6716e04` (`2 passed` + `2 passed`) and this one at `870d08f5`.

## Build window END — 2026-10-29 19:36 GMT (exec-beatgreen)

- Project `gip-s4-runtime`: 0 containers, 0 volumes (`down -v`, by project label). `docker ps -a` after = the four shared containers (Up, healthy) plus the two pre-existing exited ones; before = the same.
- The four shared containers' `docker inspect -f '{{.Name}} {{.Id}} {{.State.StartedAt}}'` before vs after: `diff` rc 0.
- Images removed by explicit tag, each `rmi` rc 0: `gi-pricing-app:` `870d08f5ce68…`, `c6716e048dc4…`, `1e17ec6382de…`, `1a3a8483463b…`, `125779310f85…` (full tags in the transcript); 0 `gi-pricing-app` images remain.
- `env | grep GIP_TEST_DATABASE_URL`: empty (rc 1). `df -h /`: `/dev/sda1 59G 49G 7.7G 87% /`.
- Throwaway worktree `exec-beatgreen-main`: porcelain 0, no shared container bound to it, `git worktree remove` rc 0.

## Audit (auditor, 2026-10-29)

Auditor seat aud-beat, read-only. **Range:** `origin/main...origin/draft/sl-8275`; head read `67284ea12daab613b67353e3eb8b728a35ca5023` (`git ls-remote` equal before and after the audit). 12 files, 812 insertions, 21 deletions; the code and test files are all inside PL-1688 row 2's Write set plus its 19:31:32 amendment (`test_deploy_switch_runtime.py`, the `down` fixture + the up line + the docstring only: confirmed by `git diff`). No spec edit, no new requirement id. Ledger SHAs: every commit sha the LG cites is an ancestor of the head (`git merge-base --is-ancestor <sha> origin/draft/sl-8275`), except `c80009ad`, `1cc2fe80`, `32257078`, which are SL-1689's source commits, ported by hand and never merged (R0's method), so non-ancestry is the design; `01a18914` and `d2506b0b7a4c` are Job-uuid fragments, not commits.
Not run by the auditor (bans: no tests, DB, docker): everything marked "LG" is read from the ledger and logs, not reproduced.

### Scope (derived from the plan and FD-1661 before the evidence)

FR-432 scheduler limb (`scheduler` service, `app` profile); FR-406 (outbox relay is a beat schedule entry); FR-413 (the beat process, one copy); FR-408 (demo entrance, optional flag). FD-1661 limbs: worker (closed, #1337), scheduler (this slice), `frontend` (SL-1689, stays open). R0 starting hunks; R1.a-e; R2.a-c; G; A1-A8.

### Items

| Item | Evidence | Proposed verdict |
|---|---|---|
| R0 hunks taken from sl-1689 | LG "Ported hunks", "Build log - Phase 1": scheduler block, `1cc2fe80` runtime test, `32257078` one-beat + `beat_fixture`; no `frontend` hunk (diff has none) | delivered |
| R1.a-d shape tests | `test_deploy_stack.py:331,338,345,351` (+`:357` migrate/redis), each `req("FR-432")`, beat ones also FR-406/413; red E-lines LG "Reds" (`assert ['no service named scheduler'] == []` x3, `no service named scheduler`, wait-for limb); compose block read: profile `app`, command `celery -A app.worker.entrypoint beat --schedule /tmp/celerybeat-schedule`, `depends_on` migrate+redis, no replicas/scale | delivered |
| R1 runtime (A3) | LG "Build window": RED1 `queued | outbox: pending|1`; RED2 `Exited (1)`, `_gdbm.error: [Errno 13] Permission denied: 'celerybeat-schedule'`; GREEN `succeeded`, `published|1`; project `gip-s4-runtime`, image `gi-pricing-app:125779310f85…`; driver rc 0. Drivers in `scratch/sl-8275-exec/` (reds2.log) | delivered (project, tag, rc present) |
| R1.e `beat_fixture` + `one_beat_problems` | code read: rewired not deleted, `up -d --wait scheduler`, `ps -a --no-trunc --format json`, asserts one beat, teardown `stop scheduler`; callers unchanged | delivered |
| A1 docs checks | gate `audit_docs.rc`=1 at the head: exactly two FAILED lines, `check 31: gap in the full allocation between 1965 and 8276` and `check 32: …LG-1969…:9: SL-1968 does not resolve in docs/INDEX.md`, both on the slice's own working ids; `req_coverage.rc`=0, `contracts.rc`=0 | delivered, pending the mint: the post-mint `audit-docs.py` and `doc-index.py --check` at rc 0 |
| A2 | `scheduler` in services: read from the YAML at the head (python `yaml`, not `docker compose config`): services list includes `scheduler`; `-k scheduler` >= 4 tests: 5 shape tests present; their green is LG "63 passed" at `e7d6e69f` and the gate's pytest. The literal `docker compose config --services | grep -x` line is NOT quoted in the LG | delivered-untested for the literal command (the YAML read stands in); the gate's pytest completes it |
| A3 | see R1 runtime | delivered |
| A4 one-beat red/green + 5 callers | F1: RED `ONE problems: ['0 beat containers running, not exactly 1']` (truncated `Command`), GREEN `[]`; double beat RED `2 beat containers running`; after-rm `[]`. Callers under `GIP_DEPLOY_TESTS=1`: two at `c6716e04` `2 passed in 132.40s` rc 0; score_batch + sampled trace `2 passed` inside a `1 failed, 2 passed in 174.26s` run (the failure was the switch test), the switch test alone at `870d08f5` `1 passed in 71.75s` rc 0. Between `c6716e04` and the head only the switch test and ledger/plan text changed (`git diff --stat`) | delivered. Note: score_batch and sampled-trace share one summary line, not one each (A4 asks "each summary line"); accepted as sufficient since the one failing node is named |
| R2.a-c / A5 | tests at `test_demo_command.py:553,566,579`; reds `SystemExit: 2` x5 (flag absent), R2.c control green; code read: flag, `check_infrastructure_up` raising `DemoRefusedError` naming each missing one, before migrations, compose call unchanged in the `else` branch | delivered. Green at the head: 0 `test_demo_command.py` failures in the gate's `pytest.log` (the 13 FAILED are the docs-audit set only) |
| R2.b deviation | LG "Deviation": `check_compose_up` names lb/api/workers and omits keycloak; accepted at 18:52:58 | delivered with an accepted deviation |
| A6 | gate script stage reads infra before/after `--no-compose`, `diff` printed (script lines 150-151); the **red** (without the switch, a line differs) is quoted nowhere in the LG, and no existing gate log with both readings was found by the auditor | green delivered: gate `infra inspect before/after demo (A6) | diff rc=0 (A6 wants 0)`, 4 lines (`infra-before.txt`: postgres, redis, minio, keycloak with Id and StartedAt), `rc_infra=0`, demo `rc 0` (`journey done in 1010s`, `served page … answered 200`); the red: **in progress, a granted run** (the lead sends its END) |
| A7 / G | `dev-commands` shows the `--no-compose` paragraph. Its `Verified` line reads "the tree of sl-8275 at 90ef474d plus its uncommitted edits": a tree that is neither the head nor committed (git-hygiene / CLAUDE.md §13 "a Verified date carries the tree") | G delivered, pending the mint: gate END `2026-10-29T21:02:28+00:00 … rc=1`, head 67284ea1, range line `origin/main...draft/sl-8275` and `range files rc=0` printed first; ruff 0, mypy 0, import_linter 0, req_coverage 0, contracts 0, frontend 0, demo 0, rc_kc 0, rc_role 0, rc_infra 0, rc_tg 0; pytest `13 failed, 7023 passed, 22 skipped, 5 xfailed`, the 13 FAILED are exactly the 8 docs-audit files of item 31 (1f) (finding_citations, ids x2, process_core_digest x2, w37_11_ceiling, doc_index, register_lint x3, register_owed, repository_invariants x2), none in a slice file; audit-docs fails only checks 31/32 on SL-1968/LG-1969. The extra skip (22 vs 21, `rc_skip=1`) is `test_the_scheduler_service_is_what_moves_a_job_out_of_the_outbox` (`test_deploy_stack_runtime.py:366/:369`, skipped without `GIP_DEPLOY_TESTS`; the lead's `-rs` count: 9 deploy skips vs 8 at main), named and accepted. The gate STANDS under 1(f) (the maintainer, to-lead "2026-10-29 21:03:39 GMT"). **Finding for the executor**: re-state the Verified tree as the committed head before the mint |
| A8 | merge by Tue 3 Nov (`date -d 2026-11-03 +%A` = Tuesday, to be re-printed at close); no window of the slice overlaps nfr-bench-1 (Mon 2 - Tue 3 Nov): all windows 29 Oct | delivered so far; closes at merge |

### F1, F2, F3 and the deviation

- **F1** (`--no-trunc`): found by the window, fixed in its own commit `1a3a8483`, red and green quoted. Delivered.
- **F2** (provisioning): see FD-1970 (drafted). Code read: `own_postgres_owner_url` refuses 5432 before `migrate` and before `provision-app-role.py`; env set in `_provision_once`, popped in `down`. Conditions (i) refusal red/green, (ii) env before/after/down, (iii) proof at `1e17ec63` api exit 3 and the password line: all in the LG. Delivered. Minor, not a finding: `_provisioned.add(PROJECT)` precedes the DDL, so a failed `migrate` in `_provision_once` leaves the project marked for the rest of the process.
- **F3** (switch test): red and green quoted, Write-set amendment cited. Delivered.
- **R2.b deviation:** accepted. Delivered.
- **Recorded breach** (LG, template-guard red-proof inside S1d's window): recorded by the lead, proof stands; nothing for the auditor to add.

### Owed (open at this draft)

1. The post-mint `audit-docs.py` and `doc-index.py --check` at rc 0 (A1, A7).
2. A6 red: in progress, a granted run; the lead sends its END, then the row becomes delivered.
3. Ledger SHA reachability: done (see the header). Re-run at the final pass only if the head moves.
4. The ledger's "Gate", "Audit" and "MERGE-ACK" placeholders still read "Not run" / "Not started": filled by the mint seat from this section and the END lines.
5. dev-commands `Verified` tree.
6. (Closed by the gate END: the demo passed under `--no-compose`, `rc_infra=0`, so keycloak counted.) Was a caution: `compose_running()` uses `--profile app` in `docker compose ps`; whether keycloak (profile `auth`) is listed for `check_infrastructure_up` is proven only by the gate's demo stage passing with `--no-compose`; a refusal naming keycloak there would be this.

### A6 red — the granted run (lead 29, 2026-10-29; to-lead "2026-10-29 19:43:24 GMT")

One run, seat exec-a6red, at the gated head `67284ea12daab613b67353e3eb8b728a35ca5023`, after the gate's END (21:02:28Z), in a no-gate gap: START 21:05:21Z, END 21:06:50Z (`date -u`; the start was 39 s before the lead's named minute 21:06 — recorded as a slip, no effect: every slot was free and the gate had ended). Logs: `~/gi-pricing-plan.local/scratch/a6red/{precheck.log,before.txt,after.txt,restored.txt,demo.log}`.

- **Pre-checks:** gate-1 / gate-1b / gate-2 free; load1 0.69; `df -h /` 7.7G avail; the template guard `alembic_version=1 environments=3 tenant_marker=1`; datnames `gipricing postgres template0 template1`; redis db 0 dbsize 56; condition (4) `diff -r sl-8275/deploy/keycloak-local tools-main/deploy/keycloak-local` rc 0 (the compose diff is only the added `scheduler` service, profile app; the keycloak service block identical).
- **The run:** `createdb -T gipricing scratch_a6red_demo` rc 0; `scripts/demo.py --journey wf-699` WITHOUT `--no-compose`, its DBs on `scratch_a6red_demo`, redis db 3; stopped by INT when "── migrations" appeared (the compose call had returned) at 21:06:01Z; demo rc 0. Compose: "Container gi-pricing-minio-1 Running / redis-1 Running / keycloak-1 Recreate / postgres-1 Recreate / postgres-1 Recreated / keycloak-1 Recreated / … all four Healthy".
- **The red** (`docker inspect -f '{{.Name}} {{.Id}} {{.State.StartedAt}}'` of the four, `diff before.txt after.txt` rc 1):
  - `< /gi-pricing-postgres-1 e779af18e11efa94653ede8498771f85ef1970b50ca20a9ede7427880b92f501 2026-10-29T14:25:21.109259294Z` → `> /gi-pricing-postgres-1 076819d6ccdb1461ec8da72d532e63ae579020e7e828388f01c9d90f04dcde14 2026-10-29T21:05:24.688524312Z`
  - `< /gi-pricing-keycloak-1 f4f284e0d769b46c672deae7c58f98239a3962a76cf7255e4a236102b69dc86b 2026-10-29T14:25:21.100409881Z` → `> /gi-pricing-keycloak-1 31fdffa8a140e312869078128620605cdb93a020c0d2bb47b043d277790aeb89 2026-10-29T21:05:24.689469118Z`
  - redis and minio unchanged. Without the switch the demo's compose call recreated 2 of the 4 shared containers — the red R2 asks for. The green is the gate's `--no-compose` demo stage: the four inspect lines equal, `rc_infra=0`.
- **Restore** (from tools-main at main `5707373e9cd9304a9ce78c737ed92bc0e8aec5c2`): `docker compose -f tools-main/deploy/docker-compose.yml --profile auth up -d --no-deps --wait postgres redis minio keycloak` rc 0; all four healthy (postgres `be0a78af…` and keycloak `8756f138…` recreated at 21:06:13Z; redis and minio unchanged); keycloak's bind source back under tools-main; no scheduler or app container was started (profile app), none to remove. redis db 0 dbsize 56; demo db 3 flushed (0); `dropdb scratch_a6red_demo` rc 0; datnames the four; the template list after = the guard list. The lead's read at 21:07:20: the same, and minio holds no `gip-blobs-demo-a6red` bucket.

### Verdicts (lead 29, from-lead "2026-10-29 21:07:48 GMT")

A1–A8 DELIVERED: A1 and A7 (G) by the full gate at `67284ea1` (END 21:02:28Z; every non-docs rc 0; rc_tg 0, rc_infra 0, demo 0, rc_kc 0, rc_role 0; the FAILED set = the 1(f) reference md5 3de106a9…, STANDS on to-lead 2026-10-29 21:05:13 GMT) and this mint's post-mint docs checks at 0 failed; A2 and A5 by the shape tests green in the gate; A3 and A4 by the build window (to-lead 2026-10-29 19:38:49 GMT); A6 by the gate's green and the granted red run above; A8 by the write set as amended (19:31:32). The R2.b deviation (18:52:58), F1, F2 (A) (19:19:28) and F3 (19:31:32) delivered. FD-1970 closed by this PR; FD-1661 annotated, its frontend limb staying with SL-1689.

Skip baseline 22 from this slice (lead 29, on to-lead 2026-10-29 21:05:13 GMT): the 22nd skip is backend/tests/test_deploy_stack_runtime.py:369 test_the_scheduler_service_is_what_moves_a_job_out_of_the_outbox (A3's runtime test, deploy-gated; GIP_DEPLOY_TESTS unset in the gate); -rs over the four deploy files: 9 at 67284ea1 vs 8 at main 5707373e.
