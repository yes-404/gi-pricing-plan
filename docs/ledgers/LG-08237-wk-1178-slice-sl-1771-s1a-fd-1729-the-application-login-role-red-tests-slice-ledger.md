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

## PRs

None yet.
