---
id: FD-1815
family: finding
title: Existing rate tables may hold non-finite values saved before FR-234 refused them, and nothing has counted them
status: active
created: 2026-10-18   # filed 2026-10-18 under working id 8118; minted 2026-10-18
owner: auditor
tree: 79f1dede2d24d2c21871372fcc53515bd2c532a5
corrected_by: []
relates: [WK-1178, FD-1803, SL-1810, PL-1809]
---

# FD-1815 — Existing rate tables may hold non-finite values saved before FR-234 refused them

## Finding

**Severity MEDIUM, owner auditor, work item WK-1178, due before the P2 code freeze (Wed 4 Nov 2026)** (the maintainer, to-lead "2026-10-18 15:22:32 BST", Q1). MEDIUM and not HIGH because in P2 the only stores are dev/demo databases and #1341 stops new writes.
Source: the maintainer's entry "2026-10-18 12:18:08 BST" (`to-lead.md`), item 2: "The live-DB census of
existing rate tables for non-finite values: ONE FD, owner auditor, in D22. It needs a live database,
not a slice gate."

FD-1803 closed the write side: SL-1810 (#1341, merge commit `c1a9c430`) makes `_value_issue` refuse
NaN, sNaN and infinities as a named `OUT_OF_BOUNDS` issue. It does not touch rows already saved. Until
`c1a9c430` any non-finite value passed `validate_rate_table` (FD-1803), so a database that held rate
tables before that merge may hold a stored `NaN` or `Infinity` in a value column. A rate table's value
is a rating relativity; a stored non-finite value reaches the rating path. **No query has counted such
rows in any database.** This finding records that the count is owed; it does not claim any row exists.

## Evidence

At `c1a9c430` (tree `79f1dede`), read by the author:

- The refusal is write-side only: `packages/pricing-core/src/pricing_core/rate_tables/operations.py`
  `_value_issue` (new `is_finite()` branch) and `_index_rows`, which now raises a named
  `ValueError("OUT_OF_BOUNDS: …")` for a stored non-finite cell. The slice's test
  `test_a_diff_over_a_stored_non_finite_cell_is_named` shows the slice itself expects such rows.
- Cells are stored in two modes (`backend/src/app/platform/rate_tables.py`, `RateTableStorageMode`):
  `rows` (database) and `parquet` (a blob above the storage threshold). A census covers both.

## What the census must do

Count, per rate table version, value cells whose text does not parse to a finite `Decimal`
(`NaN`, `sNaN`, `Infinity`, `-Infinity`, in any case), over every database that has run a build from
before `c1a9c430` that still exists (a gate or demo database is dropped at its END, so those are
not reachable; which databases qualify is the census runner's to list and quote). Report table slug, version, storage mode and cell count; a
parquet version needs its blob read. It reads; it writes nothing. It needs a live database and is not a slice gate.

## Escalation (ruled, 15:22:32 BST Q1)

- If the census finds ANY stored non-finite rate-table value, this finding becomes **HIGH** (a NaN premium is a silent mispricing), and a remedy (refuse at load, or a data migration with a dated note) is owed before the P2 close.
- If it finds none, the finding closes with the census query, its count and the databases it ran on quoted.

## Disposition

Deferred with an owner: auditor (WK-1178), due before the code freeze. The event that next discharges it: the census run against a live database with its query, count and databases quoted, then the Escalation above. Filed under working id 8118.

*(Dated line, 2026-11-09, docs batch 27, by the executor, on to-lead "2026-11-09 10:00:22 GMT" item (2) (a) and (e) and the lead's verdict in from-lead "2026-11-09 10:08" (FD-1815 entry); draft: aud-fd1815, `scratch/aud-fd1815/fd1815-dated-line-draft.md`. **Closed by the census, window START 2026-11-09 10:05:40 GMT, END 10:07:08 GMT; code and schema read at origin/main `40ba57f4b320`. The zero is VACUOUS.** Read and accepted by the maintainer, to-lead "2026-11-09 10:08:27 GMT" ("FD-1815 CENSUS READ"): the verdict is that FD-1815 closes by this dated line. **The corpus is every persistent store P2 has on this server, the two databases named below. It holds no rate-table row, so no value stored before #1341 (`c1a9c430`) exists to be non-finite. Every store seeded since (demo copies, gate copies, nfr-bench-1's) was written by post-#1341 code, which refuses a non-finite value at FR-234, and is dropped after its run.** Server `gi-pricing-postgres-1`, every non-template database: `gipricing`, `postgres`. Result: 0 hits over an EMPTY corpus. It shows that no rate-table row exists in any database on this server; it says nothing about the finite or non-finite character of any stored value, because none is stored. No database that held rate tables from a build before `c1a9c430` still exists on this server.

| Database | Locus | Hits | Denominator |
|---|---|---|---|
| gipricing | rate_table_cells.value, named non-finite | 0 | 0 |
| gipricing | rate_table_cells.value, not a finite decimal | 0 | 0 |
| gipricing | rate_table_versions.definition default_row value, named non-finite | 0 | 0 |
| gipricing | rate_table_versions, quoted non-finite token in definition, seeded_from, created_by_* | 0 | 0 |
| gipricing | rate_table_versions storage=parquet (blob read owed if > 0) | 0 | 0 |
| postgres | no rate_tables, rate_table_versions or rate_table_cells table (to_regclass NULL) | n/a | n/a |

Row denominators in gipricing: rate_tables 0, rate_table_versions 0, rate_table_cells 0; datasets, dataset_versions, models and rating_versions also 0 (alembic b7e4c2a91d36). No parquet version exists, so no blob was owed. Instrument proven red first on a planted copy (`aud_fd1815_copy`, `createdb -T gipricing`, dropped, pg_database count 0): 10 cells with NaN, sNaN, Infinity, -inf, nan, NaN123, abc and 3 finite controls read named 6 of 10 and not-finite 7 of 10; default_row 1 of 1; token 2 of 2; parquet 1 of 2. Disclosed against condition (b): the login was superuser `gipricing` with effective role `pg_read_all_data` (no low-privilege login exists; creating one is a cluster write the grant does not name), so "no write grant" holds for the effective role only; the maintainer accepted this disclosure (b) at "2026-11-09 10:08:27 GMT". Guards read: `has_table_privilege` showed the effective role read-only on the three rate-table relations; the plant and the `createdb`/`dropdb` ran on the copy only, each under a `current_database()` guard; `pg_stat_activity` was sampled three times over the 90-second window (accepted for a window that short).

SQL verbatim (psql; run under `PGOPTIONS "-c default_transaction_read_only=on -c role=pg_read_all_data"`):

```sql
\set finite '''^[[:space:]]*[+-]?([0-9]+(\\.[0-9]*)?|\\.[0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'''
\set named '''^[[:space:]]*[+-]?(s?nan[0-9]*|inf(inity)?)[[:space:]]*$'''
\set token '''"[[:space:]]*[+-]?(s?nan[0-9]*|inf(inity)?)[[:space:]]*"'''
select current_database() db, current_user, current_setting('default_transaction_read_only') ro;
\echo == census: db | locus | hits | denominator
select current_database() db, 'rate_table_cells.value named non-finite' locus, count(*) filter (where value #>> '{}' ~* :named) hits, count(*) denominator from rate_table_cells
union all select current_database(), 'rate_table_cells.value not a finite decimal', count(*) filter (where value #>> '{}' is null or value #>> '{}' !~ :finite), count(*) from rate_table_cells
union all select current_database(), 'rate_table_versions.definition default_row value named non-finite', count(*) filter (where definition->'default_row'->>(definition->'value'->>'name') ~* :named), count(*) filter (where jsonb_typeof(definition->'default_row')='object') from rate_table_versions
union all select current_database(), 'rate_table_versions quoted non-finite token in definition/seeded_from/created_by_*', count(*) filter (where concat_ws(' ',definition::text,seeded_from::text,created_by_operation::text,created_by_import::text,created_by_edit::text) ~* :token), count(*) from rate_table_versions
union all select current_database(), 'rate_table_versions storage=parquet (blob read owed if > 0)', count(*) filter (where storage='parquet'), count(*) from rate_table_versions
order by 2;
\echo == per version (rows mode), hits only: slug | version | storage | named hits | cells
select t.slug, v.version_number, v.storage, count(*) filter (where c.value #>> '{}' ~* :named), count(*) from rate_table_cells c left join rate_table_versions v on v.id=c.version_id left join rate_tables t on t.id=v.rate_table_id group by 1,2,3 having count(*) filter (where c.value #>> '{}' ~* :named) > 0 order by 1,2;
```
)*
