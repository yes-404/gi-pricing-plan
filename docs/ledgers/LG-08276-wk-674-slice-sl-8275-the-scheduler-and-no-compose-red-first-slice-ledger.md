---
id: LG-8276
family: ledger
title: WK-674 slice SL 8275 — the scheduler service and the demo's --no-compose switch, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29
owner: executor
tree: 7ceff4a16829c63f20f0cdbb56fafae22657c1ab   # origin/main at the branch cut
slice: SL-8275
phase: P2
work: WK-674
plans: [PL-1688]
corrected_by: []
relates: [FD-1661, PL-1688]
---

# LG-8276 — WK-674 slice SL 8275: the scheduler service and `--no-compose`, red first

Working ids (space form in prose): **SL 8275** (this slice), **LG 8276** (this ledger). Plan of
record: `PL-1688` row 2 (accepted at `7e3555eb`). Executor seat `exec-beatreds`. Nothing is minted here.

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

## F2 — the compose runtime tests never provisioned the application login role (found 2026-10-29 in the build window; ruled (A) by the maintainer at to-lead "2026-10-29 19:19:28 GMT"; finding FD 8280, MEDIUM, owner WK-674, drafted by the auditor from these lines)

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
  which brings up no `lb`/`api`/worker and has no `down` fixture (its docstring: "UNPROVEN … no stack was run for it"). See the F3 line below once ruled.
