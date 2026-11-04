---
id: FD-1652
family: finding
title: SL-1559 never recorded the stored-data check required before retyping rate-table rows and default_row
status: closed
created: 2026-10-12
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-675, SL-1559, PL-1558, LG-1635, RS-1649, FR-232]
---

# FD-1652 — the RL-1475 stored-data stop was not recorded

*(Minted 2026-10-12 as FD-1652 from working id 9714, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Filed by the retro audit RS-1649. Reads are at the squash-merge `372fa92a` (PR #1281).

## Evidence

- PL-1558 Acceptance 10: "The stored-data stop (RL-1475 *What it obliges*). Task 0 step 4's query output is pasted in the ledger. It shows no persisted non-`str` row or `default_row` value."
- LG-1635 at the merge sha: the Task 0 table says "step 4 OWED (no database on the box)"; the 2026-10-10 08:52 re-run says "Step 4 (the two `jsonb_typeof` counts) stays owed to the gate"; the gate-1 entry (25ede2d4) and the mint-turn entry do not mention it.
- The slice retyped `rows` and `default_row` to `RateTableCell` (`packages/model-schema/src/model_schema/rating.py`) and added the revision `d4e81b7a2c95`; CI on the PR head concluded `success` (pytest 5604 passed), which does not read any stored data.

## Finding

**Severity MEDIUM (proposed by the auditor):** the plan made this query a stop condition because a stored non-string value would fail validation after the retype. The merged record cannot show the stop was cleared. Verdict candidate: delivered but untested; exposure is likely nil (the dev database held no deployed rating), which the query would show.

## Disposition

**Owner: WK-675.** Decision: `fix before close with an owner: WK-675` — run the two read-only `jsonb_typeof` counts the plan names and record the output. Event that next confirms or discharges it: that output in a dated record. Filed by the auditor, 2026-10-11; the lead gives the verdict.

## Discharge path

Required by the maintainer's condition, `to-lead.md` "2026-10-11 20:17:38 BST" item 4: "each retro FD names its DISCHARGE PATH and date, not only an owner, so \"delivered-but-untested\" is closed by a TEST that runs, before the P2 close".

Measure on the dev database, read-only, `select count(*) … where jsonb_typeof(...) <> 'string'` over the stored `rows` and `default_row` values PL-1558 names, and record the count in this FD. If non-zero, it becomes a fix row under WK-675. Date, accepted by the lead: the first free window, no later than Fri 2026-10-23, and before the P2 exit demo, Thu 2026-11-12.

## 2026-10-26 15:00 UTC — the stored-data counts (window granted to-lead 14:44:23 (c))

Tree: `origin/main` = `7ed5c398333aa24432bd9917bd204f7b540fb39c`. Run on database `gipricing` in container `gi-pricing-postgres-1`, read-only (`PGOPTIONS='-c default_transaction_read_only=on'`), at `now()` = `2026-10-26 15:00:09.813219+00`. Log: `~/gi-pricing-plan.local/scratch/fd1652/window.log` (local, not in the repository).

**Finding: measured, denominators 0: VACUOUS, NOT a discharge.** Every count is 0, but the database holds no rate-table rows to count over.

Exact SQL, one transaction:

```sql
BEGIN;
SET TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '30s';
SELECT now(), current_database(), (SELECT version_num FROM alembic_version) AS alembic_head;
SELECT storage, count(*) FROM rate_table_versions GROUP BY storage ORDER BY storage;
SELECT count(*) AS cells FROM rate_table_cells;
SELECT count(*) AS q1_default_row_nonstring FROM rate_table_versions
 WHERE jsonb_typeof(definition->'default_row') = 'object'
   AND EXISTS (SELECT 1 FROM jsonb_each(definition->'default_row') e
               WHERE jsonb_typeof(e.value) <> 'string');
SELECT count(*) AS q1b_default_row_bad_shape FROM rate_table_versions
 WHERE definition ? 'default_row'
   AND jsonb_typeof(definition->'default_row') NOT IN ('object', 'null');
SELECT count(*) AS q2_cell_value_nonstring FROM rate_table_cells
 WHERE jsonb_typeof(value) <> 'string';
SELECT count(*) AS q3_cell_key_nonstring FROM rate_table_cells c
 WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(c.key) k
               WHERE jsonb_typeof(k) <> 'string');
ROLLBACK;
```

| Query | Result |
|---|---|
| `rate_table_versions` by `storage` | 0 rows (no versions at all) |
| `rate_table_cells` count | 0 |
| Q1 `default_row` non-string | 0 |
| Q1b `default_row` bad shape | 0 |
| Q2 cell value non-string | 0 |
| Q3 cell key element non-string (planner-added) | 0 |
| `alembic_version` | `d4e81b7a2c95` |

**Cause.** `gipricing` is the migrations-only template database, never seeded (`.claude/skills/dev-commands/SKILL.md:90` at `origin/main`): it carries no stored rate-table data, so 0 over 0 rows says nothing about the retype. The "dev database" this finding names with stored data does not exist on this stack.

**Alembic head mismatch.** The database is at `d4e81b7a2c95`; `origin/main` is ahead of it (`backend/migrations/versions/e7c3a9b15d82_blob_uploads.py` has `Revises: d4e81b7a2c95`). The plan's head check was meant to run before the queries; it ran after them. The order slip is read-only and disclosed here.

**Not reachable by this SQL.** Cells of Parquet-stored versions live in blobs, not in `rate_table_cells`. Here the `storage` denominator is empty, so there are none in this database; against any populated database those cells would not be covered by these counts.

Status unchanged. The discharge question is the auditor's and the maintainer's.

## 2026-10-26 15:05 UTC — step (1): every database enumerated, read-only (to-lead "2026-10-26 15:03:43 GMT")

*(Run by the lead under that heading's grant, in the conditions of to-lead 14:44:23 (c): one read-only transaction per database, `SET TRANSACTION READ ONLY`, `statement_timeout = '30s'`, SELECT only, `PGOPTIONS=-c default_transaction_read_only=on`. Log: `~/gi-pricing-plan.local/scratch/fd1652/enumerate.log`, `head=7ed5c398333aa24432bd9917bd204f7b540fb39c` first, `rc=0` last, load1 1.08, gate-1/1b/2 free.)*

- **Instances.** There is one PostgreSQL instance, the live stack's `gi-pricing-postgres-1` (postgres:16-alpine), on volume `gi-pricing_pgdata`. That is the only pgdata volume on the host (`docker volume ls`), so no other instance holds data.
- **Databases** (`SELECT datname FROM pg_database WHERE NOT datistemplate`): `gipricing`, `postgres`.
- **`postgres`** (now() 2026-10-26 15:04:32.201143+00): `to_regclass('public.rate_table_versions') IS NOT NULL` = false; `rate_table_cells` false; `alembic_version` false. It holds no rate tables.
- **`gipricing`** (now() 2026-10-26 15:04:32.104698+00): `rate_table_versions` and `rate_table_cells` exist; `SELECT count(*) FROM rate_table_versions` = **0**; `SELECT count(*) FROM rate_table_cells` = **0**; `SELECT version_num FROM alembic_version` = `d4e81b7a2c95`.
- **Result.** No database holds rows, so Q1–Q3 run nowhere beyond the 15:00 section's vacuous run. **No persisted pre-retype data exists in this environment.** The ruling's steps (2) (the instrument proved red on a planted JSON number) and (3) (a seeded throwaway, today's writers) follow in Tue 27's window. Status unchanged.
- *Disclosed:* the first run of the enumeration sent no stdin (`docker exec` without `-i`) and printed no rows; it was re-run with `-i`, and the log records both.

## 2026-10-26 15:35 UTC — step (2): the instrument proved red-first on a planted JSON number (to-lead "2026-10-26 15:03:43 GMT" (2); executor exec-fd1652b)

Tree: `origin/main` = `7ed5c398333aa24432bd9917bd204f7b540fb39c`, worktree `.claude/worktrees/fd1652b` (detached, `HEAD` = that sha). Throwaway: `fd1652b-pg`, container id `9e2414622ddfd9c49c6f529611ffb1816b3a8c7c66e41b3b063cedc43447209f` (`postgres:16-alpine`, local image, published `127.0.0.1:32819->5432`, anonymous volume). Login role provisioned (`scripts/provision-app-role.py --allow-default-password`), then `alembic upgrade head` as the owner: `alembic_version` = `b7e4c2a91d36`, `alembic heads` at the same tree = `b7e4c2a91d36 (head)` — equal. Log: `~/gi-pricing-plan.local/scratch/fd1652b/step2.log` (local, `head=` first, `rc=` last).

The SQL is the 15:00 section's, verbatim (`diff` of the file used against `scratch/fd1652/counts.sql`: identical), run in `BEGIN; SET TRANSACTION READ ONLY; …; ROLLBACK;`. The plant, as the owner, in one transaction (the tables carry no foreign keys, so the chain is a courtesy): one `rate_tables` row; two `rate_table_versions` rows, `storage='rows'`, `definition` = `{"default_row": {"rate": 1}}` (Q1's target) and `{"default_row": 7}` (Q1b's target); one `rate_table_cells` row, `key` = `[1]`, `value` = `5` (Q2 and Q3's target).

| Count | Before the plant (now() 15:35:06.360657+00) | After the plant (now() 15:35:06.56707+00) |
|---|---|---|
| `rate_table_versions` by `storage` | 0 rows | `rows` = 2 |
| `rate_table_cells` | 0 | 1 |
| Q1 `default_row` non-string | 0 | **1** |
| Q1b `default_row` bad shape | 0 | **1** |
| Q2 cell value non-string | 0 | **1** |
| Q3 cell key element non-string | 0 | **1** |

Every query that the plant targets sees it. The `jsonb_typeof` queries have now printed a failure.

**Removal of the plant.** `rate_table_cells`, `rate_table_versions` and `rate_tables` carry append-only triggers (`artifact_append_only`, `rate_tables_pointer_only`), so a plain `DELETE` is refused. As the owner, in the throwaway only: `BEGIN; SET LOCAL session_replication_role = replica; DELETE FROM rate_table_cells; DELETE FROM rate_table_versions; DELETE FROM rate_tables; COMMIT;` (`DELETE 1`, `DELETE 2`, `DELETE 1`). Counts back: `rate_tables|rate_table_versions|rate_table_cells` = `0|0|0`, and Q-cells/Q1/Q1b/Q2/Q3 all 0.

## 2026-10-26 15:36 UTC — step (3): today's writers, the WF-699 journey on the same throwaway (to-lead "2026-10-26 15:03:43 GMT" (3); executor exec-fd1652b)

Tree: `origin/main` = `7ed5c398333aa24432bd9917bd204f7b540fb39c`. Throwaways (all `--pull never`, `127.0.0.1` published ports, anonymous volumes): `fd1652b-pg` (id as above, port 32819), `fd1652b-redis` id `c31ba9ed08a014da7d85d45c6a96c5747517f4aa1dfd11a1a284ac71302ca18a` (`redis:7-alpine`, port 32820, db 11), `fd1652b-minio` id `dbdd8107f786549beb85aa209ea7bb0728985ad73be34d843b331bc6611d5f10` (`minio/minio:latest`, the compose's tag, port 32821, bucket `gip-blobs-fd1652b`, created by the app). Env: `GIP_DATABASE_URL`, `GIP_MIGRATION_DATABASE_URL`, `GIP_REDIS_URL`, `GIP_BLOB_ENDPOINT_URL`, `GIP_BLOB_BUCKET` pointed at those (`scratch/fd1652b/env.sh`).

**Run.** `scripts/demo.py --journey wf-699` (the gate's form: started beside a log poll, interrupted at "journey done" + "served page … answered 200"), under the `/tmp/slots/demo` lock, via `run-heavy.sh`. Start load1 1.85 (15:36:14 UTC). **rc = 0; 1015 s total; "journey done in 918s"; "served page: http://localhost:5173/ answered 200".** D7 line verbatim: `D7   ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576)`. Log: `scratch/fd1652b/demo.log` (`head=` first, `rc=0` last).

**One deviation from the gate's form, disclosed.** `demo.py` begins with `docker compose -f deploy/docker-compose.yml --profile auth up -d --wait`, which would recreate the shared `gi-pricing-*` stack (the very effect the gate's keycloak restore step exists to undo). A `docker` shim first on `PATH` (`scratch/fd1652b/shim/docker`) skipped every `docker compose …` call and passed anything else through; the log's line 5 records it: `shim: skipped docker compose -f deploy/docker-compose.yml --profile auth up -d --wait`. `demo.py` itself, the alembic step, the role provisioning, the seed, the API, the worker, the beat and the frontend ran unmodified. The local dev-auth path needed no keycloak. The four `gi-pricing-*` containers were listed up afterwards.

**Counts**, the SQL of the 15:00 section verbatim (`scratch/fd1652b/step3-q.log`), now() `2026-10-26 15:53:16.816352+00`, alembic `b7e4c2a91d36`:

| Count | Result |
|---|---|
| `rate_table_versions` by `storage` | `rows` = **16** |
| `rate_table_cells` | **140** |
| Q1 `default_row` non-string | 0 |
| Q1b `default_row` bad shape | 0 |
| Q2 cell value non-string | 0 |
| Q3 cell key element non-string | 0 |

Zero bad over non-zero denominators (16 versions, 140 cells). Not reachable by this SQL, as in the 15:00 section: the journey's versions are all `rows`; Parquet-stored versions keep their cells in blobs.

**Removal.** `docker rm -fv fd1652b-pg fd1652b-redis fd1652b-minio` printed the three names. `docker ps -a --filter name=fd1652b` afterwards: header only (no rows). Dangling volumes: 17 before, 17 after (`docker volume ls -qf dangling=true | wc -l`). Ports 8000 and 5173 free afterwards. Log: `scratch/fd1652b/removal.log`.

## 2026-10-26 15:55 UTC — Measured close (text per to-lead "2026-10-26 15:03:43 GMT" (3); the status is not flipped here)

No persisted pre-retype data exists in this environment (databases enumerated: gipricing, postgres; step (1), 15:05 UTC section); the instrument detects a planted non-string (counts, at `origin/main` `7ed5c398`: Q1 = 1, Q1b = 1, Q2 = 1, Q3 = 1 over 2 versions and 1 cell, against 0, 0, 0, 0 before the plant); today's writers produce strings (Q1 = 0, Q1b = 0, Q2 = 0, Q3 = 0 over 16 `rows` versions and 140 cells, after the WF-699 journey, rc 0). Nothing remains to remediate. The status change and the closing of the register row are the auditor's act (Tue 27, commit 7).

### The step (3) shim, verbatim (added 2026-10-26 by the lead, on to-lead "2026-10-26 15:56:23 GMT")

A shim that intercepts a production command is a test patch of a production path, so its exact text is recorded here. It was never run in or beside a gate. The file was `~/gi-pricing-plan.local/scratch/fd1652b/shim/docker`, placed first on `PATH` for the `scripts/demo.py --journey wf-699` run only:

```bash
#!/bin/bash
# fd1652b: demo.py's compose-up would touch the shared gi-pricing stack; skip every 'docker compose' call, pass the rest through.
if [ "${1:-}" = compose ]; then echo "shim: skipped docker $*" >&2; exit 0; fi
exec /usr/bin/docker "$@"
```

The lead checked after the run that the four `gi-pricing-*` containers were not recreated (Up 3 h / 12 h, healthy, at 15:55 UTC), and the maintainer's own check at 15:56 agrees. `scripts/demo.py`'s coupling to the shared stack is a process-backlog row (2026-10-26).
