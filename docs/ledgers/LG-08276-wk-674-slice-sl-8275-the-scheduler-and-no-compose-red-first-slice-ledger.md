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

**The two ERRORs are not reds.** `test_the_seed_record_pre_flight_refuses_a_workspace_the_database_lost` and `…_an_analyst_who_is_not_a_member` take the `database` fixture, which refuses without a per-worktree test database: `RuntimeError: GIP_TEST_DATABASE_URL is not set, and the per-worktree test database 'gipricing_sl-8275_cae0e2f1' does not exist yet.` The DB-free lane has no database by design; both tests are untouched by this slice.

Checks: `ruff check` on the two files rc 0. `ruff format --check`: `test_demo_command.py` clean; `test_deploy_stack.py` reports one hunk at line 71, in code the slice did not touch (`origin/main`'s copy gives rc 1 too with ruff 0.17.1); the slice's own hunks are clean.
