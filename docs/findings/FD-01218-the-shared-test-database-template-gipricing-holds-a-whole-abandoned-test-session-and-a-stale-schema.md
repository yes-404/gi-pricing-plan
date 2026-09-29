---
id: FD-1218
family: finding
title: The shared test-database template gipricing holds a whole abandoned test session and a stale schema
status: active
created: 2026-09-28
owner: auditor
tree: 7f5b4ea7c2990e7a5aa96f43a922f5f89e8bc8bf
corrected_by: []
relates: [WK-1178]
---

# FD-1218 — The shared test-database template gipricing holds a whole abandoned test session and a stale schema

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

The amendment PR that names the template in S-14 also carries `FD-1214`'s S-13 extension (a targeted run inside an exclusive
window), per the deputy's entry of 23:30:16 BST. That extension is tracked in `FD-1214`, not here.

## Progress — 2026-09-29: the template and its check are built; the rename is not done

The fix PR for this finding (WK-1178, with `FD-1214`'s hold hook) adds `deploy/setup-template-db.sh`
(creates `gipricing_template` at head and empty; `--check` reads it back) and points the
`dev-commands` `createdb -T` block, `conftest_db.py`'s refusal message and S-14 at it. **Step 3 is
not done, and the finding stays open on it:** its own condition, "once a grep shows nothing
references it", is not met. Run at `ce9303b3dcf1007c6d97bf8e73e5b3e3f3174d1d` (all tracked files, minus
`docs/findings`, `docs/plans`, `docs/closures`), the command

```text
git grep -n -E '(/gipricing($|[^_[:alnum:]-])|POSTGRES_DB: gipricing|datname=.gipricing.|-d gipricing|-T gipricing($|[^_]))' ce9303b3dcf1007c6d97bf8e73e5b3e3f3174d1d -- . ':!docs/findings' ':!docs/plans' ':!docs/closures'
```

printed these 32 lines (the `ce9303b3…:` prefix and text past column 150 are cut):

```text
.claude/skills/dev-commands/SKILL.md:71:docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing "gipricing_${WT}"
.claude/skills/dev-commands/SKILL.md:72:GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_${WT}" \
.claude/skills/dev-commands/SKILL.md:129:export GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_'"$WT"'
.claude/skills/dev-commands/SKILL.md:888:GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \
.claude/skills/dev-commands/SKILL.md:894:while `deploy/docker-compose.yml` provisions `gipricing:gipricing@…/gipricing`, and Alembic
.claude/skills/dev-commands/SKILL.md:1121:`createdb -T gipricing gipricing_<leaf>_<hash>` costs nothing; only the one shared `gipricing`
.claude/skills/fastapi-service/SKILL.md:268:provisions **`gipricing:gipricing@…/gipricing`**. Alembic reads `Settings`, so it inherits
.claude/skills/fastapi-service/SKILL.md:272:GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \
.claude/skills/python-test/SKILL.md:265:export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
.claude/skills/python-test/SKILL.md:277:export GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
.claude/skills/python-test/SKILL.md:415:      WHERE datname='gipricing' AND pid <> pg_backend_pid();"
.claude/skills/python-test/SKILL.md:418:export GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
.claude/skills/python-test/SKILL.md:425:docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -tAc \
.github/workflows/python.yml:118:          POSTGRES_DB: gipricing
.github/workflows/python.yml:296:          GIP_DATABASE_URL: postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing
.github/workflows/python.yml:304:          GIP_DATABASE_URL: postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing
.github/workflows/python.yml:305:          GIP_TEST_DATABASE_URL: postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing
backend/tests/conftest_db.py:46:DEFAULT_TEST_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
backend/tests/conftest_db.py:133:            f"`PGPASSWORD=gipricing createdb -h localhost -U gipricing -T gipricing "
backend/tests/conftest_db.py:134:            f"{name}`, then `GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@"
backend/tests/conftest_db.py:138:    return f"postgresql+asyncpg://gipricing:gipricing@localhost:5432/{name}"
backend/tests/test_conftest_db.py:100:    assert url == f"postgresql+asyncpg://gipricing:gipricing@localhost:5432/{name}"
deploy/docker-compose.yml:15:      POSTGRES_DB: gipricing
docs/ledgers/LG-01148-w37-11-prove-it-the-instrument-pr.md:329:with `docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing gipricing_co
docs/ledgers/LG-01148-w37-11-prove-it-the-instrument-pr.md:331:`GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_cod
scripts/bench-compiled-for.py:34:    GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \\
scripts/bench-compiled-for.py:68:    "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
scripts/bench-rating.py:911:            "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
scripts/bench-score-batch.py:26:    GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \
scripts/bench-score-batch.py:63:    "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
scripts/demo.py:192:            "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
scripts/revalidate-artifacts.py:36:DEFAULT_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
```

`deploy/docker-compose.yml:15` and `.github/workflows/python.yml:118` provision it as the database,
and four scripts default to it. The lead ruled on 2026-09-29 (reported to the maintainer) that it
is not renamed: it stays the compose and CI database and stops being the template source.
Dropping and recreating the dirty `gipricing` is not in that PR.
