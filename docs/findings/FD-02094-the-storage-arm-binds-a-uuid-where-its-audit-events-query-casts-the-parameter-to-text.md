---
id: FD-2094
family: finding
title: the P2 sweep's storage arm binds a UUID where its audit_events query casts the parameter to text, so asyncpg refuses the bind and NFR-470 cannot be measured
status: closed
created: 2026-11-08   # original date 2026-11-07, draft under working id 8404; minted 2026-11-08 as FD-2094
owner: auditor
tree: bfeedd9a282ee0180be54bf201b17930fc4bd2d0   # origin/main at the draft; the S2 run was at 6f958137, and the instrument is the same file at both
corrected_by: []
relates: [WK-1178, SL-1736, LG-2003, PL-1735, FD-2093, NFR-470]
---

# FD-2094 — the P2 sweep's storage arm binds a UUID where its audit_events query casts the parameter to text, so asyncpg refuses the bind and NFR-470 cannot be measured

*Disclosure: drafted under working id 8404; minted as FD-2094 on 2026-11-08, in the SL-2096 mint (WK-1178).*

*(Draft under working id 8404, on `draft/pl-fd8403-2026-11-07`. It is filed with PL-2095's mint, not before. The severity, the owner and the title's subject (the UUID binding) are the maintainer's, to-lead "2026-11-07 18:54:18 GMT" item (1).)*

## Finding

`_storage` (`scripts/measure-p2-nfr-sweep.py:766`) defines one helper for its per-version queries:

```python
async def scalar(query: str, version_id: Any = version_id) -> int:
    return int((await session.execute(text(query), {"v": version_id})).scalar_one())
```

(`:814-815`). It always binds `v` to the `uuid.UUID` of a `dataset_versions` row. Five of its six queries
compare `:v` with a `uuid` column (`id = :v`, `dataset_version_id = :v`). From that comparison asyncpg
infers `$1` as `uuid` and encodes the `UUID`. The sixth, `excluded["audit_events_rows"]` (`:841-844`), does
not:

```sql
select coalesce(sum(pg_column_size(t.*)), 0) from audit_events t
where entity_ref like '%' || cast(:v as text) || '%'
```

`cast($1 as text)` makes the server type `$1` as `text`. asyncpg's text encoder accepts only `str`, so the
bind fails before the query runs: `DataError: invalid input for query argument $1: UUID(…) (expected str, got UUID)`.
`audit_events.entity_ref` is a `String(512)` (`backend/src/app/db/models.py:234`). The text match is what the
query means, so the bind's type is the defect, not the query.

**This defect is not FD-2093.** It is independent of the role: the owner gets the same error, because the
type is decided at bind. The storage arm never ran before S2: `LG-2003` lists `storage` under "Owed", not
exercised. No test reaches it, because `tests/test_measure_p2_nfr_sweep.py` is DB-free.

**Sibling binds, read whole-file** at `bfeedd9a`: `git grep -n -E 'cast\(:|::text|as text' -- scripts/measure-p2-nfr-sweep.py`
prints only `:843`. Every other `text()` bind in the file is typed by a column comparison: `:700-704`
(`profiles.dataset_version_id = :v`), `:790-794` (`dataset_id = :d`), `:804-805`
(`sha256 = any(:d)`, a list of `str` digests) and the five other `scalar` queries at `:818-840`. **One site.**

**Not a mispricing.** The arm stops after the third ingest and before any reading. The cost is that NFR-470
(storage ≤ 1.2× the parquet payload, dedup by content hash) **could not be measured in S2**.

## Evidence

`~/gi-pricing-plan.local/scratch/nfr-bench-1/s2/J-storage.log`, first line `head=6f958137b227f1a9499a4ab00caf40f79ba2439c`,
last line `rc=1`. It ran as `gip_app_login` with the owner as `GIP_MIGRATION_DATABASE_URL` (`db-window.sh:16`), on
`gipricing_nfrs2_<suffix>`, `-T gipricing`, migrated to `b7e4c2a91d36` (`J-storage-prep.log`):

- `:205` `File "/home/puzhenhao1989/gi/scripts/measure-p2-nfr-sweep.py", line 841, in _storage`
- `:211` `File "/home/puzhenhao1989/gi/scripts/measure-p2-nfr-sweep.py", line 815, in scalar`
- `:126` `TypeError: expected str, got UUID`
- `:149` `asyncpg.exceptions.DataError: invalid input for query argument $1: UUID('01a1b75a-840f-7909-9e9f-70ec5b8b94... (expected str, got UUID)`
- `:302-303` `sqlalchemy.exc.DBAPIError: … [SQL: select coalesce(sum(pg_column_size(t.*)), 0) from audit_events t where entity_ref like '%' || cast($1 as text) || '%']`

The run had passed `_fremtpl2` (`:604`, on a workspace `seed.run` had just created: see FD-2093) and the
third ingest (`:775-785`) before it failed.

## Disposition

MEDIUM, owner WK-1178 (to-lead "2026-11-07 18:54:18 GMT"). **Fixed in the same instrument slice as FD-2093**
(SL-2096 under PL-2095), after the pin, red first against a `-T` copy. J storage then runs in S3 on Fri
13 Nov with I.

***Resolved 2026-11-08*** — closed in place 2026-11-08 by the executor, as the closing act of the mint of SL-2096 (WK-1178, LG-2097, PL-2095; this PR, its number, squash commit and merge date are written at the merge's date-of-record), on the GO to-lead "2026-11-07 19:10:01 GMT", from the audit of SL-2096 adopted by the lead (from-lead "2026-11-08 00:13:01 GMT"; the audit section is in LG-2097). Delivered remedy: `audit_events_rows` is `… cast(cast(:v as uuid) as text) …` (one site: `git grep -n -E 'cast\(:|::text|as text'` finds none left); red `expected str, got UUID` at R1 on `audit_events_rows` only, green at R2; `backend/tests/test_measure_p2_nfr_sweep_storage.py` holds it. Gate evidence: LG-2097.
