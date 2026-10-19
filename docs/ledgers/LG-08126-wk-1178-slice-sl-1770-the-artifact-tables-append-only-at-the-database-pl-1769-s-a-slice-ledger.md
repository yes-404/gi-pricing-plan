---
id: LG-8126
family: ledger
title: WK-1178 slice SL-1770 — S-a, the artifact tables append-only at the database (PL-1769), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-19
owner: executor
tree: fbbadef54adcd247a2d59cc86861c19c376a495c
phase: P2
work: WK-1178
slice: SL-1770
plans: [PL-1769]
corrected_by: []
relates: [PL-1769, SL-1770, FD-1704, FD-1728]
---

# LG-8126 — WK-1178 slice SL-1770: S-a, the artifact tables append-only at the database

*(Working id 8126, reserved by the lead; not yet minted.)*

**GO:** to-lead.md "2026-10-18 22:50:32 BST — Maintainer: the duplicate-mint anomaly ruled; GO SL-1259, SL-1770, SL-1738, SL-1575 (with conditions)".
**MERGE-ACK:** not yet given.

## Tasks

Base: `origin/main` `84b0ff5765e55bc8edd139cd22bb57cd474de807`. Branch `sl-1770-wk1178-append-only-db`, worktree `.claude/worktrees/sl-1770`.

### Scope

`PL-1769` S-a (Tasks 1–6): the artifact tables append-only or guarded at the database, from the classification table of `PL-1769` ("Table classification (plan review R3)") plus its dated row 60.

### Task list

(entries follow; the order is the plan's)

### Gate

(to be filled at the slice PR's head)

### Audit

(written by the auditor)

### Build log

- **2026-10-19 — `blob_uploads` classed `mutable`, condition verified.** The maintainer (by delegation) confirmed `mutable` in to-lead.md "2026-10-18 23:27:47 BST" on one condition: no artifact row derives its identity from `blob_uploads` after promotion. Verified at `fbbadef5`:
  - `BlobUploadRow` (`backend/src/app/db/models.py:3030`, `__tablename__` `:3047`) is referenced by no foreign key: `grep -rn "blob_uploads" backend/src packages --include=*.py` finds the table name only at `models.py:3047` and in `backend/tests/test_api_blob_uploads.py`; the one migration naming it is `e7c3a9b15d82_blob_uploads.py`, which creates it. The only foreign key on the table points outward: `sha256 … ForeignKey("blobs.sha256")` (`models.py:3061`), beside `job_id` (`:3060`, no foreign key).
  - The promotion consumer reads the row once and returns the blob digest: `_promote` (`backend/src/app/worker/data_handlers.py:168-184`) takes `upload_id`, calls `promote_upload` (`backend/src/app/platform/blobs.py:337`) and returns `JobResult(kind="blob", ref=digest)`; `upload_id` is not stored anywhere after that.
  - `DatasetVersionRow` (`models.py:971`) carries no upload field: its blob references are inside `tables` (`models.py:985`, JSONB), written by `blob_store.put` in `backend/src/app/data/ingestion.py:308`, i.e. by sha256 / `BlobRow` (`models.py:347`).
  - `upload_id` elsewhere is the S3 multipart id of the presign response (`backend/src/app/platform/blobs.py:102`, `packages/model-schema/src/model_schema/uploads.py:39`), an API field, not an artifact.
  - Nothing keys on `upload_id` after promotion, so the condition holds and the table is not `guarded`. The `reason` in `models.py` and `PL-1769` row 60 (dated addition below the table) carry this text.
- **2026-10-19 — single alembic head at the branch head `fbbadef5`**, derived from `backend/migrations/versions/*.py` (revisions that no file names as a `down_revision`): `a4d1f08c3b97`, whose `down_revision` is `f2b6d90a4c17`, the head at base.
- **2026-10-19 — DB window, own database `gipricing_sl-1770_acf25688`** (`createdb -T template0`, then `alembic upgrade head` with `GIP_DATABASE_URL` and `-c alembic.ini`: rc 0, `alembic_version` `a4d1f08c3b97`). Every run through `run-small.sh`, one file at a time, gate-1 free and load1 < 6 and available memory >= 8 GiB printed at each start. No fixture or `conftest*.py` under `backend/tests` touches redis (`grep -n -i redis backend/tests/conftest.py backend/tests/conftest_db.py` prints nothing).
- **2026-10-19 — Task 1.4, the reds on the base.** A separate detached worktree at `dda1aae9` (scratch, `uv sync --all-packages --frozen`), its own database `gipricing_wt-base_1dd6e7d0` at `f2b6d90a4c17`: `test_artifact_immutability.py` **70 failed, 44 passed**. By cause: 64 `DID NOT RAISE` (the owner connection rewrote, deleted or truncated an artifact row, or moved a `dataset_versions` row against the transition table), 2 assertion reds on the grant and trigger sets (`factors: ['INSERT', 'SELECT', 'UPDATE']`; the set of tables carrying both triggers), and **6 `AmbiguousParameterError`** (`'alg-' || $3` against a varchar column: a defect of the test, not a missing guard) fixed in `b0c58e96`. At head `cc0b3068`: 119 passed; 69 of the 70 red node ids exist at head and pass, the 70th (`test_every_table_the_grants_call_append_only_carries_both_triggers`) is the grants-derived test the plan replaces with the declaration-derived one.
- **2026-10-19 — Task 4 (W4 to W6), Step 4.1 proof then the rewrite.** At the migrated head, before Task 4, `test_fr240_governance.py` 3 failed (`factors is append-only: UPDATE rejected`), `test_rate_table_diff_portfolio.py` 18 failed (13 `rate_table_versions is append-only: UPDATE rejected`, 5 `dataset_versions: status draft -> validated is not a valid transition`), `test_rating_version_change_summary_route.py` 1 failed (`rate_table_versions is append-only`). Rewritten in `81a927cf`: a control Factor is a new version and the GBM is fitted on one (`area_intent`, DP-2 (a), DP-3 (a)); a shaped definition or storage is a new rate-table version the call names (DP-13 (a)); the two `draft -> validated` shortcuts go through `validating`. **Not in E4 (a write path the plan missed):** forcing `dataset_versions.status` to `validated` from `draft` (`test_rate_table_diff_portfolio.py` two sites, `test_datasets.py::test_a_validated_version_cannot_exist_without_a_report`). The treatment is the legal path through `validating`; reported to the lead, no production code change.
- **2026-10-19 — Task 4.4 broken-input proofs** (scratch edits, reverted by `git checkout`): W4 with a `risk` Factor in place of the `control` one, and with the GBM area `risk`: the 3 tests fail by cause (`assert 201 == 422`; `JobStatus.SUCCEEDED is JobStatus.FAILED` twice). W6 with `rows` storage in place of `parquet`: `assert False is True` (the entry is not pending). W5 with the shaping removed: 13 of 70 fail; the first run failed 12 and showed one assertion, `"age_banded" in detail`, passing on the unshaped table too (`no portfolio row maps to a cell of the table (keys 'age_banded')`), so `565f1e5d` makes it name `portfolio column 'age_banded' is absent`; the re-run is 13 failed.
- **2026-10-19 — heads, files run at `cc0b3068`** (each a separate `run-small.sh` run): `test_artifact_immutability.py` 119 passed; `test_profile_refusal.py` 3 passed; `test_rate_tables_service.py` 15 passed; `test_fr240_governance.py` 9 passed; `test_rate_table_diff_portfolio.py` 70 passed; `test_rating_version_change_summary_route.py` 21 passed; `test_model_jobs_gbm.py` 19 passed; `test_model_jobs.py` 16 passed; `test_api_rate_tables.py` 76 passed; `test_rate_table_route_codes.py` 4 passed; `test_worker_rate_tables.py` 3 passed; `test_datasets.py` 17 passed; `test_api_datasets.py` 31 passed; `test_api_blob_uploads.py` 10 passed. Step 4.5's `git grep -nE "UPDATE factors|factors SET|update\(RateTableVersionRow" -- backend` prints one line, `test_artifact_immutability.py:622`, the prohibition test that plants the `UPDATE` to prove the database refuses it.
- **2026-10-19 — migration down and up** on the slice's database: `alembic downgrade f2b6d90a4c17` rc 0, and the grants, column grants, non-internal triggers and `md5(prosrc)` of the public functions are identical to the base database's (`diff` 0 lines); `alembic upgrade head` rc 0, and the snapshot equals the one taken before the downgrade (`cmp` rc 0).
- **2026-10-19 — Step 6.1, the `postgres-pro` review of `a4d1f08c3b97`** (read-only, evidence; it ran no SQL). No defect changes the migration. (1) Downgrade: every created object is dropped, triggers before functions; `artifact_append_only()` comes from `a1b2c3d4e5f6` and stays; `GRANT UPDATE ON factors` matches `b2c3d4e5f6a7`; nothing is owned, commented or sequenced here. The measured snapshot equality (previous entry) covers the rest. (2) `to_jsonb(NEW) - cols`: no column of the compared tables is unstable under `to_jsonb`. One soft spot: `MOVING_COLUMNS` and `FROZEN_DATA_COLUMNS` match by name, so a renamed column removes nothing from either side and the guard passes where it should refuse. **Treatment: `test_the_snapshot_guard_names_only_columns_that_exist` (no database), which holds both lists to `DatasetVersionRow`'s columns.** (3) Column `GRANT UPDATE (...)`: valid; the table-level `REVOKE` cannot remove `gip_app`'s column grants. For S-b: `SELECT … FOR UPDATE` on the nine `SELECT, INSERT` tables would be refused for the application role; `modelling.py:1240` and `:1452` use `with_for_update`, to be checked there. (4) `regression_suites` `TRUNCATE`: the tests name parent and child together and both statement triggers fire; a bare parent `TRUNCATE` fails on the foreign key first, as the plan records. (5) Minor, accepted: no `lock_timeout` on the `ADD COLUMN` (ACCESS EXCLUSIVE) and the `CREATE TRIGGER`s on `dataset_versions`; the `CREATE TRIGGER`s are not `IF NOT EXISTS` (moot under transactional DDL); the application can set `data_frozen_at` on a draft row, which only freezes it earlier. The guards read `NEW` only after `TG_OP = 'DELETE' OR …`; every `DELETE` case in the rewrite test passes.
- **2026-10-19 — redis.** No fixture in `conftest.py` or `conftest_db.py` touches redis, but the app's lifespan does (`main.py:110`, `build_redis_client(settings.redis_url)`, default db 0), so the API-backed files run before this entry (`test_api_datasets`, `test_api_rate_tables`, `test_api_blob_uploads`, the diff and summary route files, `test_fr240_governance`) used db 0 until `GIP_REDIS_URL=redis://localhost:6379/14` was set for the last run. State of db 0 read at 01:32 BST: the 41 `rate_table:diff:*` keys have no TTL and an idle time of 138,589 s each, so they predate this session; the only keys idle under 2,200 s are `gip:tenant` (149 s) and three `gip:ratelimit:score:*` keys (about 1,670 s), the score keys written by no file run here.

- **2026-10-19 — rulings of to-lead.md "2026-10-19 01:37:35 BST" item 2(a) and 2(b).** (a) The `validating` step needs no ruling: *"model-schema `datasets.py:87` VALID_DATASET_TRANSITIONS allows DRAFT → {VALIDATING, ARCHIVED} only, so the tests now follow the defined lifecycle (01 FR-52)."* Verified at `7fd0fa73`: `packages/model-schema/src/model_schema/datasets.py:87` reads `DatasetStatus.DRAFT: frozenset({DatasetStatus.VALIDATING, DatasetStatus.ARCHIVED})`. (b) The redis db-0 breach (the entry "redis" above) is accepted as disclosed, recorded here and not as an FD: *"Nothing was flushed, and the keys predate the session."* The standing instruction that follows: every API-backed seat run sets `GIP_REDIS_URL` to its assigned db, because `main.py:110` defaults to /0.
- **2026-10-19 01:54:17 BST — re-merge of `origin/main` 7fd0fa7374a562293494bc44a1e91d362968ea04 (#1347, SL-1738), a merge commit, not a rebase** (the rule of to-lead.md "2026-10-18 05:30:04 BST", refined "2026-10-18 12:56:18 BST"; ruling item 2(d) of "2026-10-19 01:37:35 BST"). `git merge-tree --write-tree` rc 1; the two-sided files (changed on both sides since merge-base `84b0ff57`): `backend/src/app/db/models.py` (auto-merged), `docs/INDEX.md` (the only conflict), `docs/roadmap.md`, `docs/specs/01-data-management.md`, `docs/specs/03-rating-engine.md` (all auto-merged). `docs/INDEX.md` resolved as main's rows plus this ledger's `LG-8126` row. `models.py` is a two-sided LOGIC file, so under the 05:30:04 rule this head needs the maintainer's written exception or a re-gate; none is claimed here, and the gate is owed.
- **2026-10-19 01:54:17 BST — re-point (PL-1769 DP-7):** `a4d1f08c3b97`'s `down_revision` and its `Revises:` line changed from `f2b6d90a4c17` to `5c8e3b71d094` (main's #1347 head). `alembic heads` shows one head, `a4d1f08c3b97`; `alembic history` reads `a4d1f08c3b97 -> 5c8e3b71d094 -> f2b6d90a4c17`. The earlier single-head entry above (`down_revision` `f2b6d90a4c17`) was true at its head and is superseded by this one.

- **2026-10-19 04:33:40 BST — re-merge of `origin/main` aea6f160b3a50e9d38dc591713bd85e4daed4b8e, a merge commit (no rebase), merge sha `9661e89fded4e425be29e2956516ea96aa748026`**, parent 1 `c13a32fc1650a77f8d3c721b53ee80b929fb4738`. Merge-base `7fd0fa73`; two-sided = `docs/INDEX.md` only (the maintainer's check in to-lead.md "2026-10-19 04:32:51 BST"); the only conflict was `docs/INDEX.md`, regenerated by `python3 scripts/doc-index.py` (`--check`: OK, byte-stable), never marker-stripped. The Task 6.2 re-gate on the head after this entry is owed.

## PRs

(none yet)
