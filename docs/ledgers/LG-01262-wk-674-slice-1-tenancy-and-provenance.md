---
id: LG-1262
family: ledger
title: WK-674 Slice 1 — Tenancy and provenance (FR-436, FR-18)
status: active
created: 2026-09-29
owner: executor
tree: e537e50e92046732fc539f1916ee0fd7829be144
phase: P2
work: WK-674
plans: [PL-1239]
corrected_by: []
relates: [RL-1253, PL-1237, RL-1232]
---

# LG-1262 — WK-674 Slice 1 — Tenancy and provenance (FR-436, FR-18)

Executed from `PL-1239` (SL-1255) under `RL-1253`. Branch `wk674-s1-build`, from
`origin/main` `97b15726b1dd60ba407c6aba44735ad5cbe207ed` (#924).

**The mint.** This ledger was drafted under the working id 9830 and minted `LG-1262` at its
merge turn, 2026-09-29, on the lead's instruction (its mint queue: `#927` holds 1261 and
merges first). The entries below that quote check-31's gap `1260 to 9830`, and the
"takes 9830" line in Task 0, are numbers as measured at the heads they name and are left as
written. Until `#927` merges this branch shows a check-31 gap `1260 to 1262`.

## Tasks

### Task 0 — preconditions

Tree `e537e50e92046732fc539f1916ee0fd7829be144` (`git rev-parse HEAD^{tree}` at `97b15726`).
`uv sync --all-packages` rc 0.

| # | Premise | Result at this tree |
|---|---|---|
| a | No tenant id | `grep -rn -i -E 'tenant_id\|tenant_marker' backend/src packages/*/src \| wc -l` prints `0` |
| b | No build field on the Job | `grep -rn -E 'platform_version\|build_version\|platform_build\|build_sha' backend/src packages/*/src docs/contracts \| wc -l` prints `6` (the plan says 6, all `build_shap_summary`) |
| c | `Settings` frozen, `GIP_`, `extra="forbid"`, `version="0.1.0"` | `backend/src/app/config.py:84-100` read: holds |
| e | `ensure_bucket()` in the lifespan | `backend/src/app/main.py:92`: holds |
| f | No worker start-up signal | `grep -n -E 'worker_process_init\|worker_init' -r backend/src` prints nothing |
| g | Running transition in the worker | `backend/src/app/worker/tasks.py:134` `jobs.transition(session, job_id, JobStatus.RUNNING, actor=SYSTEM)`: holds |
| d, h, i, j | not re-read at Task 0 | re-read at the task that touches each |

Open PRs read (`gh pr list --state open`, 15 rows at this time): none rules on FR-436, FR-18,
the Job contract or `Settings` by title. Working ids in use on open PR titles: 9018 9021 9029
9030 9104 9601 9640 9650 9670 9680 9681 9690 9691 9692 9760 9811 9812 9820; this ledger takes
9830.

### Task 1 — spec, `07` §4.1

`docs/specs/07-platform.md`: `"platform_build": "0.1.0+97b15726b1dd60ba407c6aba44735ad5cbe207ed"`
added after `trace_id` in the §4.1 example, and a dated paragraph (WK-674 Slice 1, 2026-09-29,
FR-18) added after the `progress_at`/`stalled` note. FR-436 and FR-18 not reworded.
`python3 scripts/audit-docs.py`: rc 0, "All checks passed."

### Task 2 — model-schema `Job.platform_build` and contracts

- **Premises re-read:** d (`main.py` lifespan hosts FR-273's `assert_integer_minor_round_trip()`; `test_startup_self_check.py:23-45` has the negative test), h (`backend/migrations/env.py:19,31` reads `load_settings()`), i (`tests/test_repository_invariants.py` exists), j (`docs/roadmap.md` `### WK-680`: `phase: P3`, FR-376 in its scope line). All hold.
- **Red first:** `packages/model-schema/tests/test_jobs.py` (new; `test_job_platform_build_defaults_to_none`, `test_job_platform_build_round_trips`, both `FR-18`). `uv run pytest packages/model-schema/tests/test_jobs.py -q` rc 1, 2 failed: `AttributeError: 'Job' object has no attribute 'platform_build'` and `platform_build  Extra inputs are not permitted [type=extra_forbidden`. That is the predicted cause.
- **Green:** field added to `class Job` in `packages/model-schema/src/model_schema/jobs.py`, before `progress_at`. Same tests: 2 passed, rc 0.
- **Contracts:** `uv run python scripts/generate-contracts.py` rc 0 regenerated `docs/contracts/openapi/generated.json` and `docs/contracts/schemas/generated/job.schema.json`; `--check` rc 0.
- **Contract guard (`backend/tests/test_contracts.py`):** first run failed `test_generated_and_authored_agree_on_field_names[job]` (the generated `Job` had a property the authored `docs/contracts/schemas/job.schema.json` lacked). The authored file is hand-authored, not generated, so `platform_build` was added there by hand, beside `progress_at`. Re-run: 144 passed, 2 skipped, rc 0.
- `uv run ruff check packages/model-schema` rc 0; `uv run mypy` "Success: no issues found in 207 source files".
- `python3 scripts/audit-docs.py`: only check 31 (working-id gap 1260 to 9830).
- Acceptance 2 count on `packages/model-schema/src` (`git grep -n -E 'platform_build *:'`): exactly one line, `jobs.py:231`. The backend/frontend count is checked at Task 3.

### Task 3 — the build setting and the Job column (FR-18)

- **Test database:** `gipricing_executor-674s1_78b10d1e`, created with the `dev-commands` `createdb -T` block; `alembic upgrade head` rc 0.
- **Setting, red first:** `backend/tests/test_config.py` gained `test_a_strict_environment_refuses_a_missing_or_malformed_build` (3 environments x 6 values: unset, `local`, `latest`, uppercase, 39 chars, 41 chars; asserts `GIP_BUILD` in the message and `code == "SETTING_INVALID"`; `FR-18`) and `test_local_starts_with_the_local_build_marker`. `test_prod_with_tls_and_an_identity_provider_starts` now supplies `build`. Run before the field existed: 5 failed, 27 passed, rc 1 (`DID NOT RAISE ConfigInvalidError` for the unset cases, `AttributeError: 'Settings' object has no attribute 'build'`, and the prod start test refused by `extra="forbid"`). After: `Settings.build` (default `local`) and the check in `require_startable()`, placed after the TLS and OIDC refusals so `:67` and `:87` keep their own causes: 32 passed, rc 0.
- **Provenance, red first:** `backend/tests/test_job_platform_build.py` (new, `FR-18`): `test_a_job_the_worker_runs_records_the_workers_version_and_build`, `test_a_queued_job_has_no_platform_build`, `test_the_job_endpoint_returns_platform_build`. Red: 3 failed, rc 1: `TypeError: execute_job() got an unexpected keyword argument 'settings'` (x2) and `AttributeError: 'JobRow' object has no attribute 'platform_build'`. The `settings` keyword is the executor's seam (see deviation below).
- **Green:** `JobRow.platform_build` (`String(128)`, nullable); `jobs.transition(..., build=...)` sets it on `running`; row-to-shape mapping passes `platform_build=`; `execute_job(..., *, settings=None)` passes `f"{settings.version}+{settings.build}"` and `create_worker` passes its own settings. `test_job_platform_build.py` + `test_config.py` + `test_worker.py`: 59 passed, rc 0.
- **Migration:** `backend/migrations/versions/c4d1e8a7b302_jobs_platform_build.py`, down_revision `a71c3e95d204`. `alembic upgrade head`, `downgrade -1`, `upgrade head` all rc 0; `alembic heads` prints one head, `c4d1e8a7b302`.
- **Acceptance 2:** `git grep -n -E 'platform_build *:' -- backend/src frontend/src` prints exactly one line, `backend/src/app/db/models.py:119`; the model-schema count is still one.
- **Other:** ruff "All checks passed"; mypy "no issues found in 207 source files"; `backend/tests/test_contracts.py` and `test_api_jobs.py` pass; `tests/test_repository_invariants.py`: the FR-417 single-head guard passes, and two tests (`test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`) fail only because `audit-docs.py` exits 1 on check 31 (the working-id gap 1260 to 9830, expected until the mint).
- **Deviations, named:** (1) the column has its own revision here rather than sharing Task 4's; the plan allows either. (2) `execute_job` gained a keyword-only `settings` (default `load_settings()`), so "the worker's own Settings" is passed explicitly; existing callers are unchanged. `BlobStore(load_settings())` in the same function now uses that same `settings`.

### Task 4 — the tenant binding (FR-436)

- **Setting, red first:** `test_config.py` gained `test_a_strict_environment_refuses_a_missing_or_default_tenant_id` (dev/uat/prod x unset/empty/`local`; `FR-436`) and `test_local_starts_with_the_local_tenant_id`; the two existing `prod`/`build` tests now also supply `tenant_id`. Before the field: 23 failed, 19 passed, rc 1 (`DID NOT RAISE`, `'Settings' object has no attribute 'tenant_id'`, and `extra="forbid"` for the supplied cases). After `Settings.tenant_id` (default `local`) and the check in `require_startable()`, placed after the build check: 42 passed, rc 0.
- **Binding, red first:** `backend/tests/test_tenant_binding.py` (new; every test `FR-436`), run with `TenantMismatchError` present but no checks and no table: 9 failed, 5 passed, rc 1. Causes: `DID NOT RAISE TenantMismatchError` (database, blob, broker mismatch; not-migrated), `UndefinedTableError: relation "tenant_marker" does not exist` (the two tests that need the table), `assert None == 'local'` (fresh deployment, the plan's predicted red: no marker written), and the worker entrypoint importing with returncode 0. Tests: `test_matching_markers_start_the_app`, `test_a_database_marker_for_another_tenant_stops_startup`, `test_the_database_is_checked_before_any_other_store_is_written`, `test_an_empty_marker_table_stops_startup`, `test_a_database_not_migrated_to_this_revision_stops_startup`, `test_the_migration_writes_the_configured_tenant_and_refuses_a_second_row`, `test_a_blob_marker_for_another_tenant_stops_startup`, `test_a_broker_marker_for_another_tenant_stops_startup`, `test_a_fresh_deployment_starts_and_arms_both_markers`, `test_a_celery_signal_handler_cannot_stop_a_worker`, `test_the_worker_entrypoint_refuses_to_import_on_a_database_mismatch`, `test_the_worker_entrypoint_imports_when_the_markers_match`. The stores are real (PostgreSQL, MinIO, Redis); each test has its own bucket and a random Redis database index 1 to 15; the two database-absent cases use a scratch database (the `scratch_database` fixture and `_upgrade` helper are imported from `test_migration_dataset_owner.py`, not copied).
- **Green:** `app/platform/tenancy.py` (`TenantMismatchError`, `check_database`, `check_blob`, `check_broker`, `require_tenant_binding`, keys `_platform/tenant` and `gip:tenant`); `TenantMarkerRow` appended to `db/models.py`; `BlobStore.read_object`/`write_object` (`read_scratch` now delegates); the lifespan calls `require_tenant_binding` after the FR-273 check and before the probes, and `ensure_bucket` moved into it; migration `d7e2a9b5c418_tenant_marker.py` (down_revision `c4d1e8a7b302`; `smallint` primary key, `CHECK (id = 1)`, inserts `load_settings().tenant_id`, prints the id stamped). 14 passed in that file, rc 0.
- **Migration round trip:** `alembic downgrade -1`, `upgrade head`, `downgrade -1`, `upgrade head` all rc 0; `alembic heads` prints one head, `d7e2a9b5c418`.
- **Deviation 1, the worker hook is not a signal handler** *(accepted by the maintainer, by delegation, 2026-09-29: the real worker exits rc=2 on database and broker mismatch with the queue unchanged and nothing consumed, and on a match it consumes (auditor-933's subprocess run at 7a63809d), so it is fail-closed in behaviour; also accepted by the lead 2026-09-29 as plan-conforming: the plan asked for the abort behaviour to be proved first, and `test_a_celery_signal_handler_cannot_stop_a_worker` proves a handler cannot stop the worker)*. The plan's Task 4 says a Celery start-up signal handler, and says to prove abort-on-raise first. `test_a_celery_signal_handler_cannot_stop_a_worker` proves the opposite on Celery 5.6.3: `worker_init.send()` catches a raising receiver and returns `[(receiver, exc)]`, so a handler would not stop the worker. The check is instead a plain `asyncio.run(...)` at import in `worker/entrypoint.py`, which `celery -A app.worker.entrypoint worker` imports before consuming; the subprocess tests show an import failure (rc != 0, `TenantMismatchError` naming `database` and both ids) on mismatch and rc 0 when matching. The same function, `require_tenant_binding`, serves both processes.
- **Deviation 2, existing tests changed** *(accepted by the lead 2026-09-29)*. Four tests entered the lifespan with a bare `Settings(...)` (default `gip:gip` DSN) and passed only because startup touched no database before: `test_api_jobs.py::test_routes_refuse_when_no_identity_provider_is_configured`, `test_api_settings.py::test_settings_require_authentication`, `test_api_service_accounts.py::test_service_account_routes_require_authentication`, `test_demo_guide.py::test_the_entrance_is_absent_where_development_identity_is`. They now take the file's `api_settings` (test database and bucket) with `dev_auth_enabled` turned off, so each still asserts the same refusal. Found by running them with `GIP_DATABASE_URL` unset, the gate's environment (4 failed with `InvalidPasswordError ... "gip"` before the change; 51 passed after).
- **Deviation 3, `conftest_db._EMPTY_THE_DATABASE`** *(accepted by the lead 2026-09-29)* now also spares `tenant_marker` (beside `alembic_version`): it is the database's identity, written by a migration, and the session-end truncation would otherwise leave every later startup refused. `test_conftest_db.py` passes.
- **Known limits, as ruled:** the blob and broker markers are written when absent, so the stamp trusts configuration (the migration prints the id it stamps); after a Redis restart the first process to connect arms the broker key (RL-1253, DP-S1-2, note N1). An unreadable-but-existing bucket stops startup with S3's own `ClientError`, not `TenantMismatchError`, as the plan predicted.
- **Checks:** ruff, mypy (208 files) and lint-imports clean. One run of `test_tenant_binding`, `test_demo_guide`, `test_config`, `test_job_platform_build`, `test_conftest_db`, `test_contracts`, `test_worker`, `test_migration_dataset_owner`, `tests/test_repository_invariants.py`: 266 passed, 2 failed, 2 skipped, rc 1; the 2 failures are the two `audit-docs`-backed invariants, which fail on check 31 (the working-id gap, until the mint). `req-coverage.py` lists FR-436 (14 test files) and FR-18 (7).

## PRs

None opened yet; the draft PR is opened after Task 1's commit is pushed.
