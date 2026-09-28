---
id: FD-9022
family: finding
title: The shared test-database template gipricing holds a whole abandoned test session and a stale schema
status: active
created: 2026-09-28
owner: auditor
tree: 7f5b4ea7c2990e7a5aa96f43a922f5f89e8bc8bf
corrected_by: []
relates: [WK-1178]
---

# FD-9022 — The shared test-database template gipricing holds a whole abandoned test session and a stale schema

**Severity: medium.** The auditor filed this finding on 2026-09-28, on the lead's instruction and executor-s1's
report of about 23:03 BST that the template `gipricing` held five leftover `users` rows. The auditor read the
database, read-only, and found the leftover is larger than the report: the whole of one abandoned test
session, plus a schema behind head. It is medium because every per-tree database made from the template
starts non-empty and out of date, and the tests it breaks fail by collision, not by any assertion about
the code under test. Nothing in production reads this database.

## Finding

The per-tree test database procedure (`backend/tests/conftest_db.py:124`–`:127`, and the `dev-commands`
skill) creates each tree's database with `createdb … -T gipricing`. The template `gipricing` is not empty and not
at head. It holds the rows one pytest session wrote on 2026-09-17 and never removed.

## Evidence

Read at 2026-09-28 in read-only transactions (`SET TRANSACTION READ ONLY` through asyncpg's
`transaction(readonly=True)`) on the `gipricing` database. Nothing was written to it.

- **`users`:** 5 rows, `subject` from `user-616a18b5ded4` to `user-f790b4b16724`, all `created_at`
  2026-09-17 between 09:59:49.426 and 09:59:49.997 UTC. That matches executor-s1's report.
- **The whole session, not five rows.** 28 tables are non-empty, among them `workspaces` (28),
  `audit_events` (401), `jobs` (66), `outbox` (66), `validation_rules` (542), `roles` (150),
  `role_assignments` (37), `dataset_versions` (36), `datasets` (10), `models` (16), `blobs` (24),
  `api_keys` (8) and `workspace_members` (29). `workspaces.created_at` runs from
  2026-09-17T09:59:49.834 to 10:00:41.062 UTC, `datasets` from 09:59:50 to 10:00:10 and `models`
  from 09:59:51 to 10:00:40: about **52 seconds of one run**.
- **The rows are test-fixture rows, not the demo's.** Workspace slugs are `ws-<uuid7 hex>` with the name
  `Workspace 01a0aece`, and dataset slugs are `ds-<8 hex>`; the demo seeds freMTPL2 by name.
- **The schema is behind head.** `alembic_version` in `gipricing` reads `d3b955a63d6a`. `origin/main` at
  `7f5b4ea7` has later revisions (`fb705749c5d9` and `02d24f580752`, both read in `backend/migrations`).
  A tree that copies the template must run `alembic upgrade head` itself, which the skill says.
- **Nothing else was writing.** `pg_stat_activity` showed one connection to `gipricing` (this query's).

**What could have written there.** Before W37-6 an unset `GIP_TEST_DATABASE_URL` fell back to the shared
`gipricing` database (`conftest_db.py`'s own comment at `:100`–`:108` says so), and the session-scoped
teardown `_empty_the_database_after_the_session` (`:381`) empties the database at the end of a session.
The timestamps (2026-09-17, about 10:00 UTC) predate W37-6's merge (the migration merged that evening), and
`users` is not the whole of what survived, so the likeliest cause is a pytest session that ran against
`gipricing` under the old fallback and was killed or failed before its teardown ran. **Not established:**
the run's identity. This record did not search shell history or the channel files for it, and the teardown's
exclusions were not read for `users` in particular.

## Proposed fix, as ruled

The deputy ruled on 2026-09-28 (relayed by the lead), owner **WK-1178**:

1. **A clean `gipricing_template` at alembic head**, created once with `createdb` and `alembic upgrade head`,
   holding no rows outside `alembic_version`, and used only by `-T`.
2. **An emptiness and revision check wherever a tree creates its database:** every table other than
   `alembic_version` empty, and the revision the migration head. It is named in the `dev-commands` skill and in
   S-14's `createdb -T` block (`.claude/roles/executor.md`, merged in #884 at `633c6f34`); the template naming in
   S-14 comes later, in this finding's fix PR.
3. **`gipricing` is not dropped.** The dev app and demo may use it. Once a grep shows nothing references it, and the
   grep is quoted in the fix PR, it is **renamed `gipricing_dirty_20260917`**.

## Disposition

**Deferred with an owner — WK-1178**, by the deputy's ruling. Event: the clean template exists with its check,
`dev-commands` and S-14 name it, and `gipricing` is renamed after the reference grep.

The amendment PR that names the template in S-14 also carries `FD-9018`'s S-13 extension (a targeted run inside an exclusive
window), per the deputy's entry of 23:30:16 BST. That extension is tracked in `FD-9018`, not here.
