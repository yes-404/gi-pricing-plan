---
id: FD-1728
family: finding
title: Ten artifact tables declared immutable can be updated, deleted and truncated in place by the owner, with no row or TRUNCATE trigger, so an approved Rating Version's cells and algorithm change with no new version
status: closed
created: 2026-10-14
owner: auditor
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
corrected_by: []
relates: [WK-1178, FD-1704, FD-1729, FR-44, FR-70, FR-229, FR-43, P2]
---

# FD-1728 — ten immutable artifact tables carry no trigger

*(Minted 2026-10-14 as FD-1728 from working id 8037, in the D17 batch mint PR.)*

*(Filed under working id 8037, reserved by the lead. The raising run is the auditor-fr44 seat's, at `origin/main`
`8eaf6d5f9cd4204e1e077b44069d4afd395f1461`, on a scratch database migrated to `head` (`d4e81b7a2c95`) and dropped
afterwards; its record is `~/.claude/jobs/b6860f8f/tmp/fr44/out4.txt`, with `q.sql` and `run2.sh` beside it. Every extract
below was read from that file, not recalled. The catalog and the owner writes are that run's, at `8eaf6d5f`, and were not re-run. `APPEND_ONLY_TABLES` was re-read
at `origin/main` `a3fc2e8dd384de6abf909f662f43011b8078fb4e` (`backend/tests/test_artifact_immutability.py:38-52`): thirteen
names, none of the eleven tables named in this finding.)*

## Authority

The maintainer (by delegation), `to-lead.md`, "2026-10-14 12:00:14 BST", point (A), verbatim: *"**(A) O-1 → a NEW FD,
proposed HIGH: AGREED.** By run: 10 artifact tables declared immutable (03 R1 :41, FR-229 :122) have no row trigger, no
TRUNCATE trigger, no APPEND_ONLY_TABLES entry and no gip_app grant: rate_tables, rate_table_versions, rate_table_cells,
rating_algorithms, sub_graph_versions, regression_suites, regression_suite_versions, reference_tables,
reference_table_versions, reference_rows. An approved Rating Version's cells and algorithm can be changed in place, so the
price changes with no new version. That is the silent-price class. Separate from FD 8007 (different tables and cause, its
own derived test), as you propose."* The remedy as ruled is in the same entry, point (B), "S-a, triggers first": *"row +
TRUNCATE `artifact_append_only` triggers on `factors` AND the 10 tables (mutable columns, if any, allow-listed explicitly
with a reason). APPEND_ONLY_TABLES DERIVED from the artifact family (the ORM's artifact tables or the FR-44 list), never
from grants. Reds: an OWNER UPDATE/DELETE/TRUNCATE on each table is refused by the trigger, red on main."* FD-1704 and
FR-70 are limbs of this finding (below); FD-1704's body is not edited here.

## Finding

**Proposed severity: HIGH, owner WK-1178, fixed in P2** (the auditor proposes; the lead and the maintainer (by delegation)
rule; the 12:00:14 entry agreed HIGH). The immutability the specification declares for these tables is enforced by nothing
the schema owns. Three statements, each measured below:

1. `03-rating-engine.md` R1 (`:41`) says a `live` Rating Version fixes every model, rate table and reference table version
   it uses, and FR-229 (`:122`) says Rate Table Versions are immutable. Both are declarations; neither is enforced.
2. Ten tables that hold exactly that pinned content carry no row trigger, no `TRUNCATE` trigger, no grant to `gip_app`,
   and no entry in `APPEND_ONLY_TABLES` (`backend/tests/test_artifact_immutability.py:38`).
3. The test that polices FR-44's invariant is **blind to them by construction**: it derives its table list from
   `information_schema.role_table_grants` for `gip_app`, grouping tables whose privileges are exactly `INSERT,SELECT`
   (`test_artifact_immutability.py:~420-439`, ending `assert {row[0] for row in rows} == set(APPEND_ONLY_TABLES)`). A table
   with **no** `gip_app` grant appears in no group, so it is neither required to carry the triggers nor reported as missing.
   FR-44 (`01-data-management.md:106`) says the check "derives its table list from those grants … so the next artifact table
   built with the grants alone fails a test"; a table built with no grants passes it.

## Evidence

**The catalog extract** (`out4.txt`, query `q.sql`: owner, `has_table_privilege('gip_app', oid, …)`, and
non-internal triggers split by `tgtype`; `current_user` is `gipricing`). The ten tables, and `factors`, verbatim columns
`relname | owner | upd | del | ins | row_trig | trunc_trig`:

```
 rate_table_cells            | gipricing | f   | f   | f   | -   | -
 rate_table_versions         | gipricing | f   | f   | f   | -   | -
 rate_tables                 | gipricing | f   | f   | f   | -   | -
 rating_algorithms           | gipricing | f   | f   | f   | -   | -
 reference_rows              | gipricing | f   | f   | f   | -   | -
 reference_table_versions    | gipricing | f   | f   | f   | -   | -
 reference_tables            | gipricing | f   | f   | f   | -   | -
 regression_suite_versions   | gipricing | f   | f   | f   | -   | -
 regression_suites           | gipricing | f   | f   | f   | -   | -
 sub_graph_versions          | gipricing | f   | f   | f   | -   | -
 factors                     | gipricing | t   | f   | t   | -   | -
```

For contrast, a table that has both layers, `validation_reports | gipricing | f | f | t | validation_reports_no_modify |
validation_reports_no_truncate`. `information_schema.role_table_grants` lists `gip_app` UPDATE or DELETE on eleven tables
(`custom_metrics`, `custom_objectives`, `deployment_requests`, `environments`, `factors`, `jobs`, `models`, `outbox`,
`peril_structures`, `rating_versions`, `scoring_traces`); none of the ten is among them. Because they hold no `gip_app`
grant at all, `gip_app` cannot even `INSERT` into them (every `gip_app` write attempt below, bar `factors` and
`rating_versions`, is `permission denied`), which is also why the grants-derived test never sees them.

**The owner-write results** (`out4.txt`; each table seeded in a transaction with `session_replication_role = replica` for
the seed only, then, as `current_user` = the owner, `UPDATE`, then `DELETE`, then `TRUNCATE`, each inside a savepoint that
was rolled back):

| Table | Owner `UPDATE` | Owner `DELETE` | Owner `TRUNCATE` |
|---|---|---|---|
| `rate_tables` | `UPDATE 1` | `DELETE 1` | `TRUNCATE TABLE` |
| `rate_table_versions` | `UPDATE 1` | `DELETE 1` | `TRUNCATE TABLE` |
| `rate_table_cells` | `UPDATE 1` | `DELETE 1` | `TRUNCATE TABLE` |
| `rating_algorithms` | `UPDATE 2` | `DELETE 2` | `TRUNCATE TABLE` |
| `reference_table_versions` | `UPDATE 1` | `DELETE 1` | `TRUNCATE TABLE` |
| `reference_rows` | `UPDATE 1` | `DELETE 1` | `TRUNCATE TABLE` |
| `sub_graph_versions` | `UPDATE 1` | `DELETE 1` | `TRUNCATE TABLE` |
| `regression_suite_versions` | `UPDATE 2` | `DELETE 2` | `TRUNCATE TABLE` |
| `regression_suites` | `UPDATE 2` | `DELETE 2` | refused by a foreign key (`regression_suite_versions` references it), not by a guard |
| `factors` (FD-1704's table) | `UPDATE 19` | `DELETE 19` | `TRUNCATE TABLE` |

**What the run did not exercise: `reference_tables`.** Its ten-table membership rests on the catalog extract above (no
trigger, no grant, owner `gipricing`), the same shape as its neighbours, not on an owner-write result. The remedy's red
exercises it. `rating_versions` was also run (owner `UPDATE 2`, `DELETE 2`, `TRUNCATE` refused by the foreign key from
`regression_runs`); it carries `approval_guard` and is not one of the ten.

The `gip_app` attempts in the same file confirm the privilege layer would refuse these writes (`permission denied for table
…`) **if the application ran as `gip_app`**; it does not, which is FD-1729. The owner writes above are the ones the application
can make today.

## Why this is the silent-price class

An approved Rating Version pins rate table versions, reference table versions and a rating algorithm by id. `UPDATE
rate_table_cells SET value = …` changes what those ids resolve to, with the Rating Version row, its approval, its audit
event and its pins all unchanged: the price changes and no new version, no approval and no audit row exists to show it.
R1 ("Nothing resolves 'latest' at scoring time. Ever.") and FR-229 ("Rate Table Versions are immutable") hold only while
nobody writes the table.

## Limbs

- **FD-1704 (`factors`)** is limb 1: the same absence of a trigger on a table a Model pins by row id, with its own cause
  and its own derived test. Cross-cited; its body is untouched.
- **FR-70** ("Reference Table Versions are immutable and independently approvable", `01-data-management.md:177`) is limb 2.
  `reference_table_versions` and `reference_rows` are in the table above: owner `UPDATE` and `DELETE` succeed on both, so
  FR-70 is unmet at the database. It rides S-a.
- **The ten tables above** are limb 3. Their immutable columns are the rate cells, the algorithm content, the sub-graph
  definition, the reference rows and the regression suite versions; if any table has a column that is legitimately
  updated (a status, a `retired_at`), it is **allow-listed explicitly with a reason**, as the ruling states, not exempted
  by omission.

## The test that must hold

Red on `main` by cause, through a direct database connection as the owner and not through the application: for each of the
ten tables and `factors`, an `UPDATE` of an immutable column, a `DELETE` and a `TRUNCATE` are each refused by the
`artifact_append_only` trigger (a `RAISE`, not a `permission denied`, since the owner holds the privilege), and a legitimate
`INSERT` still succeeds. `APPEND_ONLY_TABLES` is **derived from the artifact family** (the ORM's artifact tables or the
FR-44 list) and not from grants, with a guard that the derivation is non-empty and covers all eleven names, so a new
artifact table with no grant fails on the day it is added. The grants-derived test stays as a second check and is no longer
the only one. The pattern is `backend/tests/test_backtests.py` (the first test in the repository to exercise a trigger).

## Disposition

Carry forward, owner WK-1178: fixed in P2 (D17), by PL-1769's slice S-a (SL-1770) (triggers first, effective even for the owner, so it
closes the live risk fastest; migration-only, low conflict), as ruled at "2026-10-14 12:00:14 BST". The trigger layer is
tamper-resistant only once S-b (FD-1729) lands: the owner can disable a trigger. It needs a resolution before any P3 start
(`CLAUDE.md` §14). The event that next confirms or discharges it is the fix's merge, with the owner-write red shown on the
base tree for each of the eleven tables by cause.
