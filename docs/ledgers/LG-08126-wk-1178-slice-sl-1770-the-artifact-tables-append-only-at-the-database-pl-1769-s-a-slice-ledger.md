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

The plan's order, each task with the commit(s) that delivered it (`git log --no-merges --format='%h %s' origin/main..HEAD` at `dc0ff6ec`; the commit subjects name the task):

| PL-1769 task | Commit(s) |
|---|---|
| Task 1 — the reds by cause, on the base tree | `dda1aae9` (eleven tables and `dataset_versions`, reds by cause), `b0c58e96` (cast the seed slug; the 6 test-defect reds) |
| Task 2 — the declaration, the migration, W1 to W3 | `cbe27461` (migration `a4d1f08c3b97`), `0cc298a6` (declaration-derived tests, Tasks 2.3, 2.10), `fbbadef5` (snapshot guard treats a non-draft row as frozen) |
| Task 3 — FD-1704's `gip_app` test | `0cc298a6` |
| Task 4 — the test writers (W4 to W6) | `81a927cf`, `565f1e5d` (Task 4.4), `cc0b3068` |
| Task 5 — the spec lines | `0a39bd4f` (FR-44, FR-60, FR-70, FR-229 dated lines) |
| Task 6 — postgres-pro review and the gate | `c20673f1` (Step 6.1: snapshot-guard column pin), gate below; `4d85952e` (test fix after the gate) |
| Plan activation, ledger and audit records | `66bee3c7`, `d4de84ad`, `500ef639`, `5dd3abc7`, `dc0ff6ec` |

### Gate

**Gate v2 of record, Task 6.2 re-gate** (to-lead.md "2026-10-19 06:24:32 BST"): head `500ef63990956531be8a165f460ac46e2794a686`, tree `048b2fb1c0350022c29cb8b6a4df659a41f74cc9`, branch `sl-1770-wk1178-append-only-db`. Logs: `~/gi-pricing-plan.local/scratch/sl1770-regate/` (`gate.log`, `*.rc`, `pytest.log`, `demo.log`, `audit_docs.log`, `rt-schema-1.sql`, `rt-schema-2.sql`); script `~/gi-pricing-plan.local/scratch/sl1770-gate.sh` (v1 to v2: `sl1770-gate.v1-to-v2.diff`). START (`gate.log`:1) 2026-10-19T04:02:15+00:00; the END line, verbatim: `END 2026-10-19T05:23:33+00:00 2.85 2.11 1.94 (date l1 l5 l15)`.

| Stage | rc / reading |
|---|---|
| alembic upgrade head; alembic heads | rc=0; 1 head, `a4d1f08c3b97` |
| round trip (down to `5c8e3b71d094`, up again) | each step rc=0; **`cmp rc=1`**. Raw `diff rt-schema-1.sql rt-schema-2.sql`: 4 `<`/`>` lines (diff output 8 lines): `5c5` and `4035c4035`, `\restrict` and `\unrestrict` keys only. With `grep -v '^\\\(un\)\?restrict '` applied to both dumps, the diff is 0 lines (re-run at the closing: that is the only reading I made of the dumps). Ruled PASS, the `cmp rc=1` an instrument false red (to-lead.md "06:24:32": *"The schema is identical"*) |
| ruff; mypy; import_linter | 0; 0; 0 |
| doc_index; req_coverage; contracts | 0; 0; 0 |
| audit_docs | **rc=1**: `check 31: gap in the full allocation between 1823 and 8126` — the working id of this ledger; clears at the mint (the log also carries a `check 32` line for `docs/REDIRECTS.csv:314: FD-1075`, which I did not trace; not found whether it is main's baseline) |
| pytest | **rc=1**: `14 failed, 6586 passed, 18 skipped, 132 warnings in 3261.50s (0:54:21)`. 13 are the working-id cascade (audit-docs-derived tests under `tests/`), all present as expected; the 14th, `backend/tests/test_model_lifecycle.py::test_a_model_whose_dataset_lost_its_standing_cannot_be_approved`, was a test defect, fixed in `4d85952e` |
| frontend: install, generate:api, lint, type-check, test (`--maxWorkers=2`), build | rc=0 each; `tree after gate: 0 changed path(s)` |
| demo `wf-699` | rc=0; **journey 1075 s** (`demo.log`:4576 `journey done in 1075s`), **demo seconds 1248**, **dislocation #1 453 s**; D7 `ok`, sum `+489842011` minor units |
| keycloak restore from tools-main | rc=0; bind source `/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local` (under tools-main) |
| cleanup | dropdb ×3 rc=0; redis db 1 and 3 FLUSHDB rc=0; both buckets removed rc=0; zeros: `own-DB count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0` |

**Ruling** (to-lead.md "06:24:32"): GREEN except one test-only fix, no re-gate. **Standing from it:** every round-trip stage compares with `grep -v '^\\\(un\)\?restrict '` and records the raw diff line count beside the verdict.

**Test fix** (to-lead.md "2026-10-19 06:27:12 BST", accepted): commit `4d85952e`; `run-small.sh … backend/tests/test_model_lifecycle.py` rc 0, `17 passed, 1 warning in 17.36s`; dropdb rc 0, `count(*) … datname like '%sl-1770%'` = 0 (the Build log entry of 06:26 has the detail). The accepted fix is the only non-docs change after `500ef639`. `ruff format --check` on that file was red before the fix (baseline, left by the maintainer).

### Audit

Pre-PR slice audit by `auditor-1770` (sonnet, medium), 2026-10-19 07:04 BST, range `origin/main...sl-1770-wk1178-append-only-db`;
`origin/main` = `aea6f160b3a50e9d38dc591713bd85e4daed4b8e` = merge-base (`git merge-base origin/main HEAD`, after `git fetch origin`).
**Tree audited:** HEAD `4d85952e03895ec631d71d31a6cd223fc740e4c5`, tree `4c0a1cfe8b7d20be1e164cf2ed4c14b0b6dbc452`. **Gate of record:**
head `500ef639` (to-lead.md "2026-10-19 06:24:32 BST", GREEN but one test fix), fix `4d85952e` accepted ("06:27:12 BST"). Post-gate predicate
`git log --no-merges --format= --name-only 500ef639..HEAD ^origin/main -- ':!docs' | sort -u` prints only `backend/tests/test_model_lifecycle.py`
(the accepted fix). This audit proposes; the verdict is the lead's. No `status:` line was changed. No test, gate or DB was run.

**Reachability.** `git merge-base --is-ancestor <sha> HEAD` rc 0 for all 14 SHAs this ledger and the log name (fbbadef5, dda1aae9, cc0b3068,
81a927cf, 565f1e5d, b0c58e96, 500ef639, 9661e89f, c13a32fc, 4d85952e, cbe27461, 0cc298a6, 0a39bd4f, c20673f1).

**Plan (PL-1769 Acceptance 1-7) to evidence.**

| Item | Evidence | Result |
|---|---|---|
| 1 reds on base | LG "Task 1.4": 70 failed / 44 passed at `dda1aae9`, by cause (64 DID NOT RAISE, 2 grant/trigger-set, 6 test defects fixed `b0c58e96`) | met in summary; per-table/per-statement node ids not itemised in the LG (F2) |
| 2 declared set, pin test, transitions | `git grep -nE '^APPEND_ONLY_TABLES\|HAVING string_agg' -- backend/tests/test_artifact_immutability.py` rc 1, no output; `test_a_dataset_version_status_follows_the_transition_table_exactly` (:917, imports `VALID_DATASET_TRANSITIONS`), `test_an_archived_dataset_version_takes_no_update_at_all` (:936), same-status (:948), FR-53 draft (:980), frozen data (:997), no re-profile (:1034); LG: 119 passed at `cc0b3068` | met; the back-filled `data_frozen_at` count the item requires is not in the LG (F2) |
| 3 | `git grep -nE "UPDATE factors\|factors SET\|update\(RateTableVersionRow\|version_row\.cells =" -- backend` prints 2 lines, not nothing (F1) | met in substance, not literally |
| 4 | LG: `test_fr240_governance` 9, `test_rate_table_diff_portfolio` 70, `test_rating_version_change_summary_route` 21 passed; Task 4.4 broken-input lines present | met |
| 5 one migration, one head | `git diff --name-status origin/main...HEAD -- backend/migrations/versions` = `A a4d1f08c3b97_artifact_tables_append_only.py` only; one head `a4d1f08c3b97`; LG down/up snapshot equality (diff 0, cmp rc 0) | met; Task 2.7/2.8 catalog outputs are summarised, not quoted (F2) |
| 6 spec lines | `git diff origin/main...HEAD -- docs/specs` adds the dated FR-44, FR-60, FR-70, FR-229 lines in the same range as the migration | met |
| 6b | `test_profile_refusal.py` 3 passed (LG); `git grep -n PROFILE_ALREADY_SET -- backend docs/specs` rc 1 (nothing); `DATASET_VERSION_IMMUTABLE` and `FR-60` both hit in `profiles.py` (:51, :35) | met; Step 2.8b back-fill red/green not in the LG (F2) |
| 7 review, gate, audit-docs | postgres-pro review in LG (Step 6.1); gate rc table only in to-lead.md "06:24:32" (ruff/mypy/lint-imports/doc_index/req_coverage/contracts 0, frontend 0, demo journey 1075 s, round trip a filtered-diff PASS, audit_docs rc 1 = the 8126 check-31 gap only); LG `### Gate` still reads "(to be filled ...)" (F2) | met in the channel; not yet in the ledger |

**DP-7 (migration chain).** `a4d1f08c3b97` has `down_revision = "5c8e3b71d094"` (`ingestion_runs_step_counts`, `backend/migrations/versions/5c8e3b71d094_ingestion_runs_step_counts.py` on `origin/main`);
`git grep -n "down_revision.*5c8e3b71d094" origin/main -- backend/migrations/versions` prints nothing (no other child on main);
`git diff --name-status <merge-base> origin/main -- backend/migrations/versions` is empty (merge-base = main tip). **No re-point needed.**

**Findings.**
- **F1 (low), acceptance 3 predicate.** `backend/tests/test_artifact_immutability.py:624` is the prohibition test that plants `UPDATE factors SET body` to prove the database refuses it (LG Step 4.5 says so); `backend/tests/test_rate_tables_service.py:198` is `assert version_row.cells == wire.cells.model_dump(...)`, a comparison, matched by the `version_row\.cells =` alternative. Neither writes an artifact row. Proposal: the lead records the predicate's two false positives in the LG; no code change.
- **F2 (low), the LG is thinner than the acceptance standard asks.** `### Gate` and `### Tasks` are placeholders; missing from the LG body: item 2's back-filled `data_frozen_at` count, item 5's Task 2.7/2.8 catalog outputs, item 6b's Step 2.8b red/green, item 1's per-node-id red list, the gate rc table. The channel entries carry the gate result. Proposal: before the PR, the executor copies the 06:24:32 rc table and the 06:27:12 fix into `### Gate`; the rest is delivered-but-undocumented-in-the-LG (verdict: delivered, evidence in the LG to be completed; not "not started").
- **F3 (info), `ruff format --check`.** The LG records `test_model_lifecycle.py` already red at 500ef639 (24 hunks, none from the fix); the maintainer left it as baseline (06:27:12). Not re-run here.
- **F4 (info), S-b carry-over.** postgres-pro (LG Step 6.1 (3)) notes `SELECT ... FOR UPDATE` on the nine `SELECT, INSERT` tables would be refused for the application role; `modelling.py` `with_for_update` at :1240 and :1452 to be checked in SL-1771. Not this slice's.
- **F5 (info), the mint.** `audit-docs.py` rc 1 is the 8126 check-31 gap (working id, per the gate entry); it clears at the mint. Not re-run here.

**Proposal:** CLEAN with F1 and F2 recorded (no finding changes code). Verdict, the closing acts and the mint are the lead's.

**Lead verdict lines on the audit** (from-lead "2026-10-19 07:05:22 BST", recorded by the executor; the verdict is the lead's):
- **F1 recorded.** The acceptance-3 predicate `git grep -nE "UPDATE factors|factors SET|update\(RateTableVersionRow|version_row\.cells =" -- backend` prints two lines at `dc0ff6ec`, both non-writes. `backend/tests/test_artifact_immutability.py:624`: `planted = text("UPDATE factors SET body = '{\"rewritten\": true}' WHERE id = :id")` plants the `UPDATE` to prove the database refuses it (Step 4.5; the line was `:622` at `cc0b3068`). `backend/tests/test_rate_tables_service.py:198`: `assert version_row.cells == wire.cells.model_dump(mode="json")` is a comparison that the `version_row\.cells =` alternative also matches. No code change.
- **F2 recorded.** `### Gate` and `### Tasks` filled from `to-lead.md` "06:24:32 BST", "06:27:12 BST", the gate's log directory and `git log`; the gate rc table is no longer only in the channel.
- **F4: deferred with an owner, SL-1771** (owner by the lead's verdict, 2026-10-19 (from-lead), not named in PL-1769). The basis is indirect. PL-1769:69 reads *"`FOR UPDATE` sites, the per-table privileges the application needs), built at `a3fc2e8d` by a"*, completing *"The census is the review's write-site table (about 140 application write sites, 19"* in the line before it, and assigns that census to S-b: *"S-b's executor copies it into its `LG-` at Task 0"*. SL-1771's job is moving the application off the owner role (`docs/roadmap.md` :2829, *"SL-1771 — WK-1178 fix slice (S-b) — FD-1729: the application connects as a login role with gip_app's grants, never as the owner"*). So the application role's refusal of `SELECT … FOR UPDATE` at `modelling.py:1240` and `:1452` (audit F4; the postgres-pro note of Step 6.1 (3)) is a consequence SL-1771 must verify. PL-1769 does not itself assign the refusal.

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

- **2026-10-19 06:26 BST — test-only fix, ruling of to-lead.md "2026-10-19 06:24:32 BST" (no re-gate):** `backend/tests/test_model_lifecycle.py::test_a_model_whose_dataset_lost_its_standing_cannot_be_approved` forced `validated → failed`, which the trigger rightly refuses. The setup now takes FR-53's own path in two legal steps, `validated → validating`, then `validating → draft`, through the same ORM write, each in its own unit of work; the assertion (`ARTIFACT_FLAGGED`, approval refused) is unchanged. Authority, `packages/model-schema/src/model_schema/datasets.py` `VALID_DATASET_TRANSITIONS`: `DatasetStatus.VALIDATED: frozenset(` `{DatasetStatus.VALIDATING, DatasetStatus.ARCHIVED}` `),` and `DatasetStatus.VALIDATING: frozenset(` `{DatasetStatus.VALIDATED, DatasetStatus.FAILED, DatasetStatus.DRAFT}` `),`. DB window (`gipricing_sl-1770_acf25688`, `-T template0`; alembic upgrade head rc 0, one head `a4d1f08c3b97`): `run-small.sh … backend/tests/test_model_lifecycle.py` rc 0, summary `17 passed, 1 warning in 17.36s`; dropdb rc 0; `count(*) … datname like '%sl-1770%'` = 0. Full log: `gi-pricing-plan.local/scratch/sl1770-testfix/`. ruff check rc 0, mypy rc 0; `ruff format --check` on the file was already red at 500ef639 (24 hunks, none from this edit).

## PRs

(none yet)
