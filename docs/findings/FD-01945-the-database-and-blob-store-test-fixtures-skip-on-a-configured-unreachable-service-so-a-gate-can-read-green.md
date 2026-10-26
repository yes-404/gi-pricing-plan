---
id: FD-1945
family: finding
title: The database and blob_store test fixtures skip on a configured-but-unreachable service, so a gate can read green with the tests unrun
status: active
created: 2026-10-26   # drafted 2026-10-26 under working id 8256
owner: executor
tree: 98a4ff195dc7f1da136686051549a4fe1350deb3
corrected_by: []
relates: [WK-1178, SL-1942, LG-1941, FD-1729]
---

# FD-1945 — The database and blob_store test fixtures skip on a configured-but-unreachable service, so a gate can read green with the tests unrun

## Finding

**MEDIUM; owner WK-1178. A test-harness defect: a false green lets a wrong merge through; no product code is wrong and no price is affected.** Authority: to-lead "2026-10-26 01:54:05 GMT" (B), scope ruled by to-lead "2026-10-26 01:56:43 GMT". Filed under working id FD-1945.

At `origin/main...draft/s1a-fd1729` c4a0c907, `backend/tests/conftest_db.py` has four paths that turn an unusable configured service into a pass:

1. **(i)** the `database` fixture, on any connect error that does not name `gip_app_login`, calls `pytest.skip(f"PostgreSQL not reachable at …")` (:1022), even when `GIP_TEST_DATABASE_URL` or `GIP_TEST_APP_DATABASE_URL` is set.
2. **(ii)** the same fixture skips when the database has no migrations applied (:1029), with the same configured URL.
3. **(iii)** the :1022 message renders `test_database_url()`, built with `hide_password=False` (:186–191), so the password (default `gip_app_login`) reaches the test report.
4. **(iv)** the `blob_store` fixture skips on "MinIO not reachable" (:1071) even when `GIP_TEST_BUCKET` or `GIP_BLOB_ENDPOINT_URL` is set.

A skipped test reads as not failed: a gate on an unreachable or mis-provisioned database ends rc 0 with the DB tests unrun. Only a connect error naming `gip_app_login` failed (:1015–1021, kept).

## Evidence

- **Red** (run-small.sh, `backend/tests/test_conftest_db_unreachable.py`, at c4a0c907 plus the red test = 4bc098a5): `5 failed, 1 passed, 2 warnings in 39.50s` rc 1. The four "configured" cases assert a failure and got `1 skipped`; the "nothing configured" database case found `gip_app_login:gip_app_login@…` in the skip reason (iii).
- **Green** at 2124a622: `6 passed, 2 warnings in 42.74s` rc 0. Also green, same head: `backend/tests/test_conftest_db_login_role.py` + `backend/tests/test_conftest_db.py`, `18 passed, 2 warnings in 0.43s` rc 0.
- Path (ii) needs a live, un-migrated database, so it is not driven DB-free; the gate covers it. The test drives the real fixtures in a child pytest run against 127.0.0.1 port 1.

## Severity

MEDIUM: the harm is a wrong merge on a false green, not a wrong price; every path is a test fixture.

## Remedy

`_unavailable(configured, message)` in `conftest_db.py`: configured → `pytest.fail`, else `pytest.skip`. "Configured" is `GIP_TEST_DATABASE_URL` or `GIP_TEST_APP_DATABASE_URL` (database, incl. no-migrations) or `GIP_TEST_BUCKET` or `GIP_BLOB_ENDPOINT_URL` (blob_store). Messages name host:port, user and database, or endpoint and bucket (`_safe_dsn`), never a password or key. Lands in SL-1942 / LG-1941 (`draft/s1a-fd1729`).

Skips left in `conftest_db.py`, all in the unconfigured branch of `_unavailable`: database not reachable, database has no migrations, MinIO not reachable (no environment names the service, so a developer without the compose stack still runs the unit tests).

## Disposition

Open, owner WK-1178; **fix before close**: SL-1942 / LG-1941. Closed in place citing the PR when that slice merges. Filed under working id FD-1945.
