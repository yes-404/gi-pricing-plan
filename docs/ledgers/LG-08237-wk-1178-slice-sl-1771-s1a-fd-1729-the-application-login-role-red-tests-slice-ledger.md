---
id: LG-8237
family: ledger
title: WK-1178 slice SL-1771 — S1a of FD-1729, the application connects as a login role, not the owner; the red tests and their red table, slice ledger
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-25   # working id 8237, unminted
owner: executor
tree: d1d96465b05728e617482b5e88a2d56a984c4746                  # the head the red table was measured on; the commit that adds this file is its child
phase: P2
work: WK-1178
slice: SL-1771
plans: [PL-1769]
corrected_by: []
relates: [PL-1769, SL-1771, FD-1729, FR-44]
---

# LG-8237 — WK-1178 slice SL-1771 (S1a of FD-1729): the red tests and their red table

**GO:** none yet. The GO request follows S1a's code, one line, with the maintainer's confirmation. Pre-GO ruling this ledger records: to-lead "2026-10-25 21:05:20 GMT", item (2) "S1a (FD-1729, SL-1771 draft @d1d96465) RULED".
**MERGE-ACK:** none yet.

## Tasks

### Scope

S1a is the first half of the `SL-1771` re-cut in plan `PL 8227` (working id, unminted; the plan is on branch `draft/pl-8227`, section "FD-1729 split into S1a and S1b"). It builds on the `SL-1771` row of `PL-1769` (`docs/INDEX.md` at `origin/main`: "WK-1178 fix slice (S-b) — FD-1729: the application connects as a login role with gip_app's grants, never as the owner"). Finding: `FD-1729`. Requirement: `FR-44` (the privilege layer).

This ledger holds the **red** half only: four test files drafted at `d1d96465` (`test(backend): draft the S1a reds for FD-1729 …`) and the table of what each one fails on. S1a's code (`deploy/postgres/app-login-role.sql`, `scripts/provision-app-role.py`, the `Settings.migration_database_url` field, `migrations/env.py`, the compose mount, the CI env, `conftest_db`) does not exist yet.

### Task list

1. Red tests drafted at `d1d96465` — done (four files).
2. Classify DB-free versus DB-backed, run the DB-free ones red — done, this ledger.
3. Fix the docstring of `test_alembic_refuses_without_the_migration_dsn_and_never_falls_back` — done in the commit that adds this file (docstring only; the asserts are unchanged; item 13 of the common brief is not engaged).
4. S1a code, green — **owed**.
5. The four DB tests of `test_application_login_role.py` run, in a no-gate gap — **owed**, after step 4.

### Gate

Not run. Every heavy check is owed after S1a's code.

#### Classification (to-lead "2026-10-25 21:05:20 GMT", item (2), accepted)

| File | DB-free? | State at `d1d96465` |
|---|---|---|
| `backend/tests/test_application_dsns.py` | yes | 6 red, 1 green control |
| `backend/tests/test_provision_app_role.py` | yes | 6 red |
| `backend/tests/test_conftest_db_login_role.py` | yes | 6 red |
| `backend/tests/test_application_login_role.py` | mixed | 2 file-text tests DB-free; 4 `database` tests need a scratch DB and the cluster-wide roles `gip_app` and `gip_app_login`, which `deploy/postgres/app-login-role.sql` and `scripts/provision-app-role.py` do not yet create. They stay red until S1a's code. Not run. |

#### Red table

Command, run via `run-heavy.sh` at load1 below 3 (2.82 at start): `run-heavy.sh -- run-small.sh <s1a-draft worktree> backend/tests/test_application_dsns.py backend/tests/test_provision_app_role.py backend/tests/test_conftest_db_login_role.py`. The first run (exec-s1a) and this re-run agree. Log: `~/gi-pricing-plan.local/scratch/s1a-draft/red-run.log`, first line `head=d1d96465b05728e617482b5e88a2d56a984c4746`, last line `rc=1`. Summary line: `18 failed, 1 passed, 2 warnings in 1.81s`.

| File | Test | Red reason | sha | rc |
|---|---|---|---|---|
| test_application_dsns.py | test_the_application_dsn_defaults_to_the_login_role | assert: default DSN is `postgresql+asyncpg://gip:gip@localhost:5432/gip`, not `gip_app_login:` | d1d96465 | 1 |
| test_application_dsns.py | test_the_migration_dsn_is_a_separate_optional_secret | AttributeError: `'Settings' object has no attribute 'migration_database_url'` | d1d96465 | 1 |
| test_application_dsns.py | test_the_migration_dsn_gets_the_same_scheme_validator | regex `postgresql\+asyncpg` did not match: `migration_database_url` "Extra inputs are not permitted" | d1d96465 | 1 |
| test_application_dsns.py | test_alembic_refuses_without_the_migration_dsn_and_never_falls_back | assert `'RuntimeError' in stderr` fails: offline run exits rc != 0 but ends "No literal value renderer is available …", not a refusal | d1d96465 | 1 |
| test_application_dsns.py | test_migrations_env_reads_the_migration_dsn | assert: `'migration_database_url'` absent from `migrations/env.py` text | d1d96465 | 1 |
| test_application_dsns.py | test_ci_migrates_as_the_owner_and_runs_the_suite_as_the_login_role | assert: `GIP_MIGRATION_DATABASE_URL: postgresql+asyncpg://gipricing:gipricing@` absent from the python workflow | d1d96465 | 1 |
| test_provision_app_role.py | test_the_scram_verifier_matches_the_rfc_7677_vector | assert: `scripts/provision-app-role.py` does not exist | d1d96465 | 1 |
| test_provision_app_role.py | test_the_verifier_salt_is_random_per_call | assert: `scripts/provision-app-role.py` does not exist | d1d96465 | 1 |
| test_provision_app_role.py | test_the_script_refuses_the_default_password_without_the_flag | assert: `--allow-default-password` absent; python "can't open file" `scripts/provision-app-role.py` | d1d96465 | 1 |
| test_provision_app_role.py | test_the_script_refuses_when_the_migration_dsn_is_unset_and_leaks_no_secret | assert: `GIP_MIGRATION_DATABASE_URL` absent; python "can't open file" `scripts/provision-app-role.py` | d1d96465 | 1 |
| test_provision_app_role.py | test_the_login_role_sql_converges_and_carries_no_password | FileNotFoundError: `deploy/postgres/app-login-role.sql` | d1d96465 | 1 |
| test_provision_app_role.py | test_compose_mounts_the_login_role_sql_for_fresh_volumes | assert: the `app-login-role.sql` mount line absent from the compose file | d1d96465 | 1 |
| test_conftest_db_login_role.py | test_database_url_is_the_login_role_on_the_owner_databases_name | assert: URL is `gipricing:gipricing@h:5432/wt_db`, expected `gip_app_login:gip_app_login@…` | d1d96465 | 1 |
| test_conftest_db_login_role.py | test_app_database_url_override_wins | assert: override `x:y@z/explicit` ignored; got `gipricing:gipricing@h:5432/wt_db` | d1d96465 | 1 |
| test_conftest_db_login_role.py | test_owner_database_url_keeps_the_meaning_of_gip_test_database_url | AttributeError: `conftest_db` has no attribute `test_owner_database_url` | d1d96465 | 1 |
| test_conftest_db_login_role.py | test_owner_database_url_is_called_only_inside_conftest_db | assert: `backend/tests/conftest_db.py` absent from the call-site list | d1d96465 | 1 |
| test_conftest_db_login_role.py | test_owner_fixture_users_is_a_closed_labelled_tuple | AttributeError: `conftest_db` has no attribute `OWNER_FIXTURE_USERS` | d1d96465 | 1 |
| test_conftest_db_login_role.py | test_the_owner_database_fixture_exists | assert: `hasattr(conftest_db, 'owner_database')` is False | d1d96465 | 1 |

Green control (the 1 pass): `test_no_backend_source_names_the_owner_credentials`, green at main as well; it guards S1a against reintroducing an owner credential.

Environment note: the venv needed `uv sync --all-packages --frozen` (rc 0) before this run.

#### Role-DDL rule (to-lead "2026-10-25 21:05:20 GMT", item (2), (a) and (b))

- No role DDL until S1a's code exists. A red there would prove only "missing", already shown above.
- When the DB tests run: only in a no-gate gap; roles scratch-prefixed (`s1a_<sha>_gip_app…`) and dropped afterwards; `GIP_TEST_DATABASE_URL` never the shared `gipricing`, because conftest TRUNCATEs its target.

### Audit

Not yet.

### Build log

- 2026-10-25 — `d1d96465`: the four red test files drafted, unrun.
- 2026-10-25 — red run of the three DB-free files at `d1d96465`: 18 failed, 1 passed, rc 1 (table above). The docstring of the alembic test corrected in the same commit as this ledger.
- **Owed: green after S1a's code** — the 18 reds above, the 2 file-text tests and the 4 DB tests of `test_application_login_role.py`, and the full gate.
- 2026-10-25 (executor `exec-s1abuild`, DRAFT build, no DB, no heavy run: `run-heavy.sh` refused every attempt with rc 76, gate-1 held) — S1a code against the reds:
  - S1a-1 `6baac46b`: `deploy/postgres/app-login-role.sql`, `scripts/provision-app-role.py`, the compose initdb mount (PL-1769 Steps 1.1, 1.2). Run owed (rc 76 at `6baac46b`): `test_provision_app_role.py`.
  - S1a-2 `8f8952ac`: `Settings.database_url` default = the login role, `migration_database_url` with the same scheme validator; `migrations/env.py` reads it and raises naming `GIP_MIGRATION_DATABASE_URL`; `python.yml` Migrate/Provision/Tests env; `scripts/demo.py` (owner migration DSN, provisioning step); `examples/fremtpl2/seed.py` split (`grant_demo_principals` on a second, owner `Database`; `run` refuses without the migration DSN); `deploy/docker-compose.yml` `migrate` gets the owner DSN; `dev-commands` "Migrations" (Steps 2.1, 2.2). Run owed (rc 76 at `8f8952ac`): `test_application_dsns.py`.
  - S1a-3 `d8ab3889`, `c3650a57`: `conftest_db.py` (`test_database_url()` = login role on the owner database's name, `GIP_TEST_APP_DATABASE_URL` override, `test_owner_database_url()`, `OWNER_FIXTURE_USERS`, `owner_database`; the `database` fixture FAILS rather than skips when the login role cannot connect); the three scratch-database migration files, `test_migration_routing_shadow.py`, `test_migration_environment_settings.py`, `test_migration_env_logging.py` and the two `bootstrap` WF-699 tests moved to `owner_database` / `GIP_MIGRATION_DATABASE_URL` (Step 3.1). Run owed (rc 76 at `d8ab3889`): `test_conftest_db_login_role.py`.
  - S1a-4 `bcc0eeb4`: `b7e4c2a91d36_application_role_grants.py`, the one grants migration, from the *Table classification* map (`_TARGET`), not yet from a red list (Steps 5.1, 5.3 owed to the DB gap). Run owed (rc 76): `test_application_login_role.py` (file-text tests).
- **Not done, owed to a lead disposition or the DB gap:** (a) `test_conftest_db.py` is unedited: its cases assert `test_database_url()` returns the `GIP_TEST_DATABASE_URL` override; after the flip they describe `test_owner_database_url()`, which that file may not call (`test_owner_database_url_is_called_only_inside_conftest_db`); (b) users of a scratch database not yet moved to `owner_database`: `test_approval_guard_trigger.py` (own `scratch_database`, `:314`), `test_tenant_binding.py` (`:144`, `:182`, `:201`, imports the fixture; `:295`, `:321` set `GIP_DATABASE_URL` to the login role, correct for the worker, but the import-time `require_tenant_binding` needs `tenant_marker` `SELECT`, granted by `bcc0eeb4`), `test_approval_guard_decision.py`; they fail loudly (class 2) at the Step 3.2 red run and are listed then; (c) Step 3.2/5.3 red runs, the census diff, S1a-0's census table, S1a-5 (compose run on a separate project and a fresh volume; the compose `api`/`worker-*` services still carry the owner `GIP_DATABASE_URL` and need the provisioning step), the scripts that build `Database(…)` from an owner DEFAULT_DSN (`bench-*`, `check-*`, `reset-unbacked-rule-approvals.py`, `revalidate-artifacts.py`).

- 2026-10-25 22:05–22:40 GMT, executor `exec-s1arun`, under the grant to-lead "2026-10-25 22:04:36 GMT" (items i, ii, iii and dispositions 1, 2, 4, 5). Tree and branch: worktree `s1a-draft`, branch `draft/s1a-fd1729`, start head `4b712879`.
  - **(i) DB-free reds, `run-small` via `run-heavy --grant`, at `4b712879`:** `test_application_dsns.py` + `test_provision_app_role.py` + `test_conftest_db_login_role.py`: `1 failed, 18 passed`, rc 1. The one red was the code's fault: `deploy/postgres/app-login-role.sql:19` was a comment containing the word the no-secret assert forbids. Comment reworded, assert unchanged (`52bb1faf`). Re-run, same three files: `19 passed, 2 warnings`, rc 0. The 2 file-text tests of `test_application_login_role.py` are reported from (ii): they passed in both (ii) runs.
  - **Disposition (1), item 13, `test_conftest_db.py`, own commit `7423ac54`, re-shaped by `97c60f4f`.** Old oracle: with only `GIP_TEST_DATABASE_URL=postgresql+asyncpg://x:y@z/explicit` set, `assert conftest_db.test_database_url() == "postgresql+asyncpg://x:y@z/explicit"`; and in `test_database_url_derives_the_per_worktree_url_when_the_database_exists`, `url == postgresql+asyncpg://gipricing:gipricing@localhost:5432/{name}`. New oracle: the same input yields the login-role DSN `postgresql+asyncpg://gip_app_login:gip_app_login@z/explicit`, and `GIP_TEST_APP_DATABASE_URL=postgresql+asyncpg://a:b@c/app` returns exactly that; the derived case yields `postgresql+asyncpg://gip_app_login:gip_app_login@localhost:5432/{name}`. The autouse fixture also clears `GIP_TEST_APP_DATABASE_URL` and `GIP_APP_DB_PASSWORD`. The file does not call the owner-DSN function (`test_owner_database_url_is_called_only_inside_conftest_db`); the first form of the commit did, and `97c60f4f` removes it. Run: `test_conftest_db.py` + `test_conftest_db_login_role.py` + `test_provision_app_role.py`, `22 passed`, rc 0, at `97c60f4f`. `ruff check .` rc 0 (one E501 in `scripts/provision-app-role.py:14` was fixed in `4a9376e6`).
  - **(ii) Throwaway Postgres.** Container `s1a-pg-7423ac54` (`postgres:16-alpine`, local image, no pull; `-p 127.0.0.1::5432`; port read with `docker port`: `127.0.0.1:32768`; anonymous volume; scratch password in `~/gi-pricing-plan.local/scratch/draft-s1a-fd1729/pgpw.txt`, not recorded here). Every DSN pointed at `127.0.0.1:32768`; the shared stack was not touched.
    - **Step 1.3** (idempotence and convergence): `gip_app_login` created by hand `WITH CREATEROLE CREATEDB REPLICATION`; `scripts/provision-app-role.py --allow-default-password` unmodified, run twice at `7423ac54`: rc 0 and rc 0. After each run `select rolname, rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls, rolinherit from pg_roles where rolname='gip_app_login'` printed `gip_app_login | f | f | f | f | f | t` (identical both times; every attribute reset).
    - **`alembic upgrade head`** with `GIP_MIGRATION_DATABASE_URL` on that container: rc 0, head `b7e4c2a91d36`.
    - **First pytest** (`test_application_login_role.py` and the 7 moved files `test_migration_dataset_owner.py`, `_dataset_version_envelope.py`, `_deployments.py`, `_env_logging.py`, `_environment_settings.py`, `_routing_shadow.py`, `test_wf699_journey.py`) at `7423ac54`: `1 failed, 33 passed, 38 warnings, 20 errors in 45.73s`, rc 1. **Permission denied list: all 20 errors and the 4 DB tests of `test_application_login_role.py` were `permission denied for table alembic_version` (SELECT), from `conftest_db.py:359` `SELECT count(*) FROM alembic_version` run as the login role.**
    - **Grant added (disposition 5), the narrowest:** `alembic_version: READ` (`SELECT` only; no `UPDATE`) in `_TARGET` of `b7e4c2a91d36_application_role_grants.py`, commit `61f5b5a9`. `downgrade -1` revokes it (`_PREVIOUS` has no row). Read-back: `has_table_privilege('gip_app','alembic_version','SELECT')` t, `'UPDATE'` f. `alembic downgrade -1` rc 0, `upgrade head` rc 0.
    - **Second pytest** (same 8 files) at `61f5b5a9`: `3 failed, 51 passed, 38 warnings in 41.55s`, rc 1 (`test_application_login_role.py`: all 6 passed). The 3 left are NOT grants to add, and are reported to the lead:
      1. `test_migration_dataset_version_envelope.py::test_the_backfill_falls_back_to_the_earliest_member`: `permission denied for table workspaces` (`INSERT INTO workspaces`), a test seeding a seed-only table (DP-22: the five seed-only tables are READ for `gip_app` by design) through the application `database` fixture. Fix is on the test side (take `owner_database`, add the node to `OWNER_FIXTURE_USERS`, label `DP-22`), not a grant: an application `INSERT` on `workspaces` would widen the production role for a test.
      2. `test_wf699_journey.py::test_wf699_journey_runs_end_to_end`: `permission denied for table role_assignments` (`INSERT`), from `test_rating_versions._principal` -> `rbac.seed_builtin_roles` run on the `database` fixture, in a test already listed in `OWNER_FIXTURE_USERS` as `bootstrap`. The listing is not honoured by the helper chain (`_approved_model` -> `_principal` takes the app `database`). Same class, same recommendation; an application `INSERT` on `role_assignments` would be a privilege-escalation path and is not added.
      3. `test_migration_deployments.py::test_the_application_role_cannot_update_or_delete_a_deployment` (line 399): `assert await privilege("environments", "UPDATE")` is False. Not a "permission denied" line: the test asserts `has_table_privilege('gip_app','environments','UPDATE')`, which is table-level, while the census row grants `UPDATE (name, description, retired_at)` by column, and `has_table_privilege` is False for a column-only grant. The next assert (`deployment_requests`, `UPDATE (approval_request_id, status)`) is the same shape. Either the test moves to `has_any_column_privilege` or the census returns the table-level `UPDATE`; both are the lead's (a test is not weakened without a ruling, item 13 of the common brief).
  - **Disposition (2), the three unconverted scratch-DB users, run in the container at `61f5b5a9` (`9 failed, 114 passed, 3 warnings, 5 errors`, rc 1):**
    - `test_approval_guard_trigger.py`: **convert to `owner_database`** (label `migration`/`owner-subject`): its `scratch_database` runs `CREATE DATABASE` (`permission denied to create database`) and the seven `test_the_ref_the_trigger_composes_is_the_one_artifactref_renders[*]` cases and `test_with_the_evidence_condition_replaced_by_the_flag_the_forgery_succeeds` do DDL on the real tables (`permission denied for schema public`).
    - `test_tenant_binding.py`: **convert the scratch-database fixtures (`migrated_scratch` and its callers) to `owner_database`**; the worker/start-up paths at `:295` and `:321` stay on the login role (correct, `tenant_marker` is READ). `test_the_database_is_checked_before_any_other_store_is_written` also fails on `assert 'local' is None` (a tenant row left in the container's marker by the migration, not a privilege: the test expects an empty marker and needs the owner fixture to truncate it).
    - `test_approval_guard_decision.py`: **leave** -- it ran green as the login role (no failure, rolled-back transactions on the real tables through `test_database_url()`), which is the application path it exists to test.
  - **Disposition (4):** the owner `DEFAULT_DSN` fallbacks are listed in one row of `docs/process/process-backlog.md` (owner WK-1178, no `FD-`): `scripts/bench-compiled-for.py:66`, `bench-score-batch.py:61`, `bench-rating.py:1100`, `check-rule-sets-runnable.py:32`, `check-seed-record.py:34`, `reset-unbacked-rule-approvals.py:38`, `revalidate-artifacts.py:36`.
  - **(iii) Teardown:** `docker rm -fv s1a-pg-7423ac54` rc 0; `docker ps -a --filter name=s1a-pg` printed nothing; `docker volume ls -q --filter dangling=true | wc -l` 16 before and 16 after (the container's anonymous volume `2599a358a72e...` went with it; the 16 are not this seat's). Redis db 12: `DBSIZE` 0 after `FLUSHDB`.


## PRs

None yet.
