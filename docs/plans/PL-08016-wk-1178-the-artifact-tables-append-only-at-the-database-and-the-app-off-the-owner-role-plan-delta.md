---
id: PL-8016
family: plan
kind: map
title: WK-1178 — the artifact tables append-only at the database (SL-8017) and the application off the owner role (SL-8041) — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — DP-1 to DP-7 ruled at 10:29:14, DP-8 to DP-20 at 12:18:57, DP-21 and DP-22 (plan review, 2026-10-14) at 12:42:33, DP-21b at 13:21:41, refined at 13:27:39 and 15:14:52; activation is the lead's
created: 2026-10-14
owner: planner
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-8007, RL-8001, SL-8017, SL-8041, SL-1274, SL-1455, FR-43, FR-44, FR-70, FR-88, FR-96, FR-229, FR-240, FR-370, RL-1615]  # forward-cites kept out until D17 mints them: FD 8037, FD 8038
---

# PL-8016 — WK-1178: the artifact tables append-only at the database (SL-8017), and the application off the owner role (SL-8041)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667`, this delta `relates:` the records it builds on. It
> carries **two slice rows** under `### WK-1178` in [`../roadmap.md`](../roadmap.md): **S-a =
> SL-8017** (the triggers) and **S-b = SL-8041** (least privilege). Each slice is its own PR and
> its own `LG-`, which quotes its row in the *Slices* table below as its scope.
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (every acceptance item is seen red **by its cause** before the code that turns it green),
> `python-test` (the `req` marker; negative tests; `SKILL.md:279`'s downgrade proof),
> `python-package`, `fastapi-service` (S-b's settings and startup check), `spec-change` (the
> FR text), `dev-commands` (`uv sync --all-packages`; the alembic DSN; both gate halves) and
> `git-hygiene`. Read [`README.md`](README.md)'s conventions before the first step. Each
> executor is spawned from `.claude/roles/executor.md`.

## Re-cut record

Filed under **working id 8016**, re-cut in place while unminted and undated. The first cut
(seat planner-fd8007, tree `1e260c15`, one slice SL-8017 over `factors` only) is at
`origin/pl-8016-wk1178-fd8007-remedy-2026-10-14` @`e29de1bc`; this commit replaces it. Its
DP-1 to DP-7 keep their numbers and their rulings (Decision points); DP-4 is superseded by
DP-8. **SL-8017** is re-cut to S-a. **SL-8041** is new, reserved by the lead (`eta.md` entry
"2026-10-14 12:02:15 BST", item (1): *"SL 8041 = PL 8016 re-cut S-b (least privilege)"*).
Re-cut 2026-10-14 by the planner (seat planner-pl8016r). **Tree read:** `origin/main`
`a3fc2e8dd384de6abf909f662f43011b8078fb4e`. Every `file:line` below was read at that tree
unless it names another.

## Plan review (2026-10-14)

**Authority.** The maintainer (by delegation), `to-lead.md` entry "2026-10-14 12:27:51 BST",
which orders an independent written plan review of this plan and says *"Findings go in the
plan's review section (the planner amends pre-merge)"*. **The review:** auditor-pl8016, over
`origin/main...origin/pl-8016-wk1178-fd8007-remedy-2026-10-14` (main `a3fc2e8d`, tip
`689d2dc5`), read-only against the head database `gipricing_sl-1695_dfe5cf59` (alembic
`d4e81b7a2c95`), with a write-site census built separately at `a3fc2e8d` (the census, below).
**The lead's verdicts:** R1 to R11 accepted as findings to fix in this plan, as proposed; R12
a pass. **Confirmed by the maintainer (by delegation), `to-lead.md` "2026-10-14 12:42:33 BST"**:
*"The review's findings, all accepted as you ruled; R1 is the critical one"*, with R2, R3, R5,
R6 and R9 *"REQUIRED before P2's ACK"*; the same entry rules DP-21 (guarded) and DP-22 (not
granted) and adds the compose binds to `127.0.0.1` (Step 1.5). **The entry "2026-10-14 13:21:41 BST"** then
rules DP-21b (guard by state, then refined by "2026-10-14 13:27:39 BST": the data frozen from the
first validation, FR-53's status and report moves allowed), accepts the `owner-subject` label with each user listed by node
id, and splits `seed.py` (login role; only its bootstrap on the owner connection). Each amended site below carries *"plan review R<n>, 2026-10-14"*. Plan line numbers in
the review are those of `689d2dc5`, which differs from this file's base only in id spelling.

**The census** is the review's write-site table (about 140 application write sites, 19
`FOR UPDATE` sites, the per-table privileges the application needs), built at `a3fc2e8d` by a
read-only agent with its `git grep` commands verbatim at its head. It is in the review's job
directory (`~/.claude/jobs/b6860f8f/tmp/rv-writes.md`); S-b's executor copies it into its `LG-`
at Task 0, so the slice record does not depend on a scratch path.

| R | Finding (the review's one line, shortened) | Fixed at (this plan) |
|---|---|---|
| R1 | 37 test files build their own owner connection with `test_database_url()`, so the red run cannot see their application paths | Task 3.1 (the default flips to the login role; an owner connection is named); Task 0's predicate; Task 3.2's refusal classes; acceptance 8 |
| R2 | Six tables guarded by a row trigger were classed `mutable`, so the detective check skipped them; `rating_versions` can be emptied by `TRUNCATE` | *Table classification*; S-a row; Step 2.2; Step 2.4 (six new `TRUNCATE` triggers); Step 1.2; E1; Task 4.2 |
| R3 | No 59-table classification; 23 mutable tables had no reason; 14 are INSERT-only or read-only; `dataset_versions` is updated in place | *Table classification* (59 rows, class and reason each); **DP-21** (`dataset_versions`), ruled guarded 12:42:33, and **DP-21b**, ruled 13:21:41, refined 13:27:39 (*DP-21's guard*) |
| R4 | The ownership predicate was `USAGE` in DP-19 and R-b1, "member" in Task 4.2 and R-b6, and blind to superuser membership | **P-own** (Decision points, after the table), used verbatim by DP-19, R-b1, R-b6 and Task 4.2; the `INHERIT FALSE` red |
| R5 | The trigger check tested only `tgenabled = 'D'` | DP-14 (b) as amended; Task 4.2 (the named triggers exist, `tgenabled IN ('O','A')`, and the function-body hash, **adopted**); a red per route |
| R6 | No grant set to check the red run against; five write paths have no application caller | Task 5.1 (the census diff into the `LG-`); **DP-22**, ruled not granted 12:42:33 |
| R7 | Provisioning skipped an existing role without resetting it; `NOREPLICATION` absent | Step 1.1 (unconditional `ALTER ROLE`); Step 1.3 (applied twice, both rc 0) |
| R8 | No rollback; the role is cluster-wide and 5432 is published on `0.0.0.0`; the password could be logged | Step 1.4 (rollback, rehearsed in Task 6); Step 1.2 (a pre-hashed SCRAM verifier; the default refused unless named); activation needs |
| R9 | Existing excess grants were not audited | Task 5.1 and 5.2 (`jobs` `DELETE` and `outbox` `DELETE` revoked unless a caller is found) |
| R10 | Only the owner `UPDATE` red was observed per table | Step 1.2 (parametrised over table × statement); Step 1.4; acceptance 1 |
| R11 | `approval_guard` and `UPDATE … RETURNING` need implicit `SELECT`s; `tenant_marker`; the worker check's place; `examples/` is a DSN consumer; function, schema and database ownership | E6; Task 0; P-own; Task 3.2; Task 4.2; Task 5.1 |
| R12 | Every ruling of 10:29:14, 12:00:14 and 12:18:57 is carried; the gaps were R9 and R10 | a pass; R9 and R10 fixed above |

## Goal

**S-a (SL-8017).** Every artifact table carries both of `FR-44`'s layers. That is `factors`
and the ten tables FD 8037 names (`rate_tables`, `rate_table_versions`, `rate_table_cells`,
`rating_algorithms`, `sub_graph_versions`, `regression_suites`, `regression_suite_versions`,
`reference_tables`, `reference_table_versions`, `reference_rows`). The trigger refuses an
**owner** `UPDATE`, `DELETE` and `TRUNCATE` on each one, and each refusal is seen red on the
base first. The append-only set is **derived from a declaration on every mapped table**, never
from grants, so a new artifact table that is not protected fails a test on the day it lands.
The three legitimate in-place writes are each removed or declared with a reason.

**S-b (SL-8041).** The application and the worker connect as a login role that holds
`gip_app`'s grants, and only migrations connect as the owner. The process refuses to start
when `current_user` owns the schema or is a superuser. Every grant the application needs is
found **red first**, by running the suite as that role. Only S-b makes S-a tamper-resistant,
because the owner can `ALTER TABLE … DISABLE TRIGGER` and the application today holds the
owner's credential.

## Authority — every entry named with its author, quoted

1. **The maintainer (by delegation), `to-lead.md` entry "2026-10-14 12:00:14 BST — O-1 → NEW
   FD, HIGH; a SECOND root-cause FD, HIGH: the app connects as the table OWNER, so FR-44's
   privilege layer is inert everywhere; PL 8016/8017 re-cut (re lead 11:58:53 / 11:59:23)"**,
   the remedy, verbatim:
   *"**Remedy, re-cut (PL 8016/SL 8017's planner re-plans; one plan, two slices):**
   - **S-a, triggers first** (effective even for the owner, so it closes the live risk fastest):
   row + TRUNCATE `artifact_append_only` triggers on `factors` AND the 10 tables (mutable
   columns, if any, allow-listed explicitly with a reason). APPEND_ONLY_TABLES DERIVED from the
   artifact family (the ORM's artifact tables or the FR-44 list), never from grants. Reds: an
   OWNER UPDATE/DELETE/TRUNCATE on each table is refused by the trigger, red on main. Schedule:
   right after the G2 merges, before the freeze; it is migration-only, low conflict.
   - **S-b, least privilege:** the app connects as a login role with gip_app's grants (DSN,
   compose provisioning, migrations still run as the owner); a startup/test assert that
   `current_user` is NOT the owner of the artifact tables; the existing grants audited so the
   app can still do every write it legitimately does (red-first per refused path). Higher blast
   radius: it lands AFTER G2 and the SL-1455 NFR session (it touches every DB path), before the
   freeze, with a full gate + compose run.
   - FD 8007 becomes a limb of S-a/S-b (its revoke matters only after S-b). FR-70 rides S-a.
   - A DECISION POINT for the planner: the owner can still `ALTER TABLE … DISABLE TRIGGER`, so
   S-b is what makes the trigger layer tamper-resistant; state that dependency in the FD."*
   The same entry's (A) and (B) agree FD 8037 (O-1) and FD 8038 (the root cause), both
   *"proposed HIGH"*, owner WK-1178, P2.
2. **The lead, `from-lead-2026-10-09.md` entry "2026-10-14 12:01:11 BST"**, which reserves
   FD 8037 and FD 8038 and orders the re-cut: *"FD 8038 = the ROOT CAUSE: the app never runs as
   gip_app … HIGH, WK-1178, P2; states the owner can DISABLE TRIGGER, so S-b makes S-a
   tamper-resistant."* *"S-b least privilege (… after G2 + the NFR session, before the freeze;
   full gate + compose run) = a second SL id, reserved at the re-cut."*
3. **The lead, `from-lead-2026-10-09.md` entry "2026-10-14 11:59:23 BST"**, item (2): O-1
   confirmed by run, *"As the OWNER (gipricing) UPDATE/DELETE succeed on all, TRUNCATE on all
   but two (FK only)"*, and *"LEAD-VERIFIED: production connects as the OWNER"*.
4. **The maintainer (by delegation), `to-lead.md` entry "2026-10-14 10:29:14 BST — READ-BACK
   VERIFIED #1298; PL 8016 DP-1..3 RULED; O-1 pre-ruled (re lead 10:28:14)"**: DP-1 → (a);
   DP-2 → as recommended; DP-3 → accepted; *"DP-4..DP-7 defaults: accepted"*; and on O-1:
   *"The append-only set must be derived from the ARTIFACT FAMILY (the FR-44 list or the ORM's
   artifact tables), so a new artifact table without protection fails the test."*
5. **The maintainer (by delegation), `to-lead.md` entries "2026-10-14 10:01:11 BST" and
   "2026-10-14 10:11:47 BST"**: FD-8007's remedy (*"revoke + `artifact_append_only` triggers +
   APPEND_ONLY_TABLES + `_make_control` rewrite"*), due before the 4 Nov P2 code freeze, red
   first, with the ADD: *"the planted-UPDATE red must be shown failing against the NEW trigger
   at the DB layer (`gip_app` UPDATE → refused)"*.
6. **The findings.** `FD-8007` at `origin/docs-d15-2026-10-14` @`56b5a8e1` (the factors limb).
   `FD 8037` (O-1) and `FD 8038` (the root cause) are being filed by the auditor on
   `fd-8036-failed-auth-audit-2026-10-14`, not pushed when this plan was written; they are
   cited by working id. FR-70 rides S-a (authority 1), as the maintainer (by delegation) placed it
   at "2026-10-14 11:06:52 BST", item 2: *"FR-70 is NOT in that FD: immutability by route absence
   only is FD 8007/O-1's class. It joins that finding's table set (the artifact-family derivation),
   with one remedy."*
7. **The maintainer (by delegation), `to-lead.md` entry "2026-10-14 12:18:57 BST — PL 8044/SL
   8045 (failed-auth fix) and PL 8016 re-cut DPs RULED by me directly (no DM needed); superuser
   finding folded into FD 8038 / S-b (re lead 12:18:08)"**, item (2), verbatim:
   *"**(2) PL 8016 RE-CUT @39613d21 (S-a = SL 8017, S-b = SL 8041):** its pending audit must be
   WRITTEN before the plans batch ACK.
   - DP-1..3 keep my 10:29:14 rulings.
   - **DP-8 → the ORM declaration on all 59 tables, closed both ways vs pg_class** (rec). S-a is
   scheduled AFTER the G2 merges, so models.py's G2 heat is not a conflict at its build time. The
   fallback (a test-file map) only if G2 slips past S-a's window; the planner states that switch.
   - DP-9 (forward-only guard on rate_tables.current_version), DP-10 (blob before row,
   rate_tables.py:1480), DP-11 (publish-only guard, reference.py:229), DP-14 (FD 8038 states the
   DISABLE TRIGGER dependency + a startup check): as recommended.
   - **DP-15:** one idempotent provisioning SQL; my GO will NAME the target (the shared DB
   container), applied once, with before/after `\du` and grant read-backs in the LG.
   - DP-16 (the DSN split: GIP_MIGRATION_DATABASE_URL = owner, used by env.py only), DP-18 (tests
   run as the login role), DP-19 (the refusal applies everywhere), DP-20 (grants red-first, never
   grant-then-trim): as recommended. DP-12, 13, 17: as recommended.
   - **NEW, from your 12:07:50 measurement (the owner `gipricing` is SUPERUSER, rolsuper = t):**
   the app today can bypass ALL triggers via `session_replication_role`, not only DISABLE
   TRIGGER. **S-b's startup refusal and test MUST assert the app's login role is NOT superuser,
   NOT the table owner, has NOBYPASSRLS, and cannot SET session_replication_role** (a red: the SET
   attempted as the login role → refused). FD 8038's text states the superuser fact, measured by
   auditor-failauth with the query and output, and its HIGH stands."*
   This entry is the record for every DP it rules; no decision-maker `RL-` is written. The
   superuser item is S-b's **R-b6** (Task 4).

## Evidence, re-read at `a3fc2e8d` (not copied from the findings)

**E1 — the run (auditor-fr44).** `~/.claude/jobs/b6860f8f/tmp/fr44/out4.txt`, header line
`DB=gipricing_fr44_55d9c6a2 tree=8eaf6d5f9cd4204e1e077b44069d4afd395f1461`, alembic head
`d4e81b7a2c95`, query file `q.sql` in the same directory. Its catalog (`out4.txt:14-75`)
gives, for each of the ten tables and for `factors`, the owner `gipricing`, row trigger `-`
and truncate trigger `-`. `gip_app` holds `upd`/`del`/`ins` = `f`/`f`/`f` on the ten and
`t`/`f`/`t` on `factors`. The owner probes (`:95-473`) print `UPDATE n` and `DELETE n` on every
table probed. `TRUNCATE TABLE` succeeds except `regression_suites` (`:384-385`, *"Table
"regression_suite_versions" references "regression_suites""*) and `rating_versions` (`:420-421`,
blocked by a foreign key only, so a `TRUNCATE` naming it with its referencing tables empties
it; S-a closes it with `rating_versions_no_truncate`, plan review R2, 2026-10-14). **`reference_tables` has no probe section in `out4.txt`.** Its catalog row
shows no trigger and no grant, but the owner writes on it are not observed there; S-a's
Task 1 red is the first observation. The run's tree is `8eaf6d5f`, not `a3fc2e8d`; Task 1
re-observes everything at the GO tree.

**E2 — the trigger pattern.** `artifact_append_only()` is
`backend/migrations/versions/a1b2c3d4e5f6_artifact_append_only.py:43-52`, message
`'% is append-only: % rejected (01 FR-42, FR-43)'`, `ERRCODE = 'insufficient_privilege'`. The
pair form is `a1b2c3d4e5f6:77-92` and `e1f2a3b4c5d6_artifact_row_triggers.py:51-67`
(`{table}_no_modify` `BEFORE UPDATE OR DELETE … FOR EACH ROW`, `{table}_no_truncate` `BEFORE
TRUNCATE … FOR EACH STATEMENT`, both `EXECUTE FUNCTION artifact_append_only()`; downgrade
`DROP TRIGGER IF EXISTS`, `e1f2a3b4c5d6:70-74`). Layer 1 is `a1b2c3d4e5f6:90-92` (`GRANT
SELECT, INSERT`, `REVOKE UPDATE, DELETE … FROM gip_app`, `… FROM PUBLIC`). A narrower guard
that lets one column move is `blobs_content_immutable()` (`a1b2c3d4e5f6:55-69`).

**E3 — the tests.** `backend/tests/test_artifact_immutability.py`: `APPEND_ONLY_TABLES`
`:38-52` (13 tables, written out); the exact-grant test `:266-294`; `_APPEND_ONLY_ROWS`
`:303-343`; the owner-connection test `:346-393` (the `deployments, scoring_traces` TRUNCATE
form for a referenced table, `:372-376`); the **grants-derived** trigger test `:396-446`,
whose `HAVING … = 'INSERT,SELECT'` (`:425-426`) is why a table with **no** grant cannot enter
its set, and its guard `:439`. The precedent for a set derived from ORM declarations is
`backend/tests/test_approval_guard.py:1-7` and `:137-160` (every `status` column declares
`info={"status_vocabulary": …}` or `info={"approval_capable": False}`; an undeclared column
fails).

**E4 — every in-place write to the eleven tables.** The sweep, verbatim and runnable, with
`G="git -C <repo>"; T=a3fc2e8d; P='(factors|rate_tables|rate_table_versions|rate_table_cells|rating_algorithms|sub_graph_versions|regression_suites|regression_suite_versions|reference_tables|reference_table_versions|reference_rows)'; C='(ReferenceTableRow|ReferenceTableVersionRow|ReferenceRowRow|FactorRow|RatingAlgorithmRow|RateTableRow|RateTableVersionRow|RateTableCellRow|RegressionSuiteRow|RegressionSuiteVersionRow|SubGraphVersionRow)'`:
(i) `$G grep -nE "\b(update|delete)\($C|on_conflict_do_update|\.delete\(|\bsession\.delete|TRUNCATE|UPDATE +[a-z_]+|DELETE +FROM" $T -- backend/src 'packages/*/src' scripts`
(no hit on these tables); (ii) `$G grep -nwE "$P" $T -- backend/src 'packages/*/src' scripts`
(no raw SQL names them); (iii) `$G grep -nE '\.(current_version|cells|definition|storage|status|body|effective_to)\s*=[^=]' $T -- backend/src/app/platform`
(ORM attribute writes; the hits on these classes are listed below); (iv)
`$G grep -niE "(UPDATE|DELETE FROM|TRUNCATE)( TABLE)? +$P\b|\b(update|delete)\($C\b" $T -- backend/tests scripts`
(the test writers). (iii) is line-scoped: an assignment split over lines would be missed, so
**Task 6's full gate is the backstop**, and any refusal it finds is a missed row of this table.
Foreign keys: only `regression_suite_versions.suite_id` → `regression_suites.id`
(`fb705749c5d9_regression_suite_versions.py:55`, no `ondelete`); no `ON DELETE` and no ORM
`cascade=` anywhere in `backend/migrations` or `backend/src`.

| # | Table | Where | The write | Kind | Treatment (DP) |
|---|---|---|---|---|---|
| W1 | `rate_tables` | `backend/src/app/platform/rate_tables.py:1465` (flushed `:1481`) | `table_row.current_version = version_number`; the ORM `onupdate` also sets `updated_at` (`models.py:2055`) | src, every new version | **declared exception**: a guard lets `current_version` move forward and `updated_at` change, nothing else (DP-9) |
| W2 | `rate_table_versions` | `rate_tables.py:1480` (row inserted `:1455-1457`, second flush `:1481`) | `version_row.cells = blob_ref.model_dump(mode="json")`, parquet storage only, in the same transaction as the `INSERT` | src, parquet versions | **removed**: the blob is written first and the row is inserted complete (DP-10) |
| W3 | `reference_table_versions` | `backend/src/app/platform/reference.py:229` (flush `:230`) | `row.status = PUBLISHED` (`DRAFT, PUBLISHED = "draft", "published"`, `:57`) | src, publish | **declared exception**: a guard lets `status` go `draft` → `published` only, nothing else (DP-11; FR-70) |
| W4 | `factors` | `backend/tests/test_fr240_governance.py:248-256` (`_make_control`, `UPDATE factors SET body = jsonb_set(…)` `:252`), called `:270`, `:299`, `:344` | flips a pinned Factor's intent in place | test | **removed** (DP-2, DP-3, ruled) |
| W5 | `rate_table_versions` | `backend/tests/test_rate_table_diff_portfolio.py:380`, `:489`, `:830`, `:1810` | `update(RateTableVersionRow)…values(definition=definition)`, which strips or rewrites a key's `factor_ref` to set up a refusal | test | **removed**: the shaped version is inserted, never updated (DP-13) |
| W6 | `rate_table_versions` | `backend/tests/test_rating_version_change_summary_route.py:360` | `version.storage = "parquet"` inside `unit_of_work` | test | **removed**: as W5 (DP-13) |
| W7 | all eleven | `backend/tests/conftest_db.py:370-387` (`_EMPTY_THE_DATABASE`) | session teardown `TRUNCATE … RESTART IDENTITY CASCADE` under `set_config('session_replication_role', 'replica', true)` | test | **unchanged in S-a**: `replica` suspends every trigger, so the new triggers do not fire. It needs a superuser, so in S-b it stays on the owner connection (DP-18) |

No `DELETE` or `TRUNCATE` of these tables exists in `backend/src`, `packages/*/src` or
`scripts`. `rating_algorithms.updated_at` has `onupdate=func.now()` (`models.py:2026`) and no
path updates the row, so it is dead and stays as it is.

**E5 — who connects as what.** `backend/src/app/config.py:120` `database_url: SecretStr =
SecretStr("postgresql+asyncpg://gip:gip@localhost:5432/gip")`; `backend/src/app/db/session.py:41`
builds the one engine from it; `backend/src/app/main.py:75` and
`backend/src/app/worker/entrypoint.py:32` construct `Database(settings)`;
`backend/migrations/env.py:31` sets `sqlalchemy.url` from the **same** `load_settings().database_url`.
`deploy/docker-compose.yml:13` `POSTGRES_USER: gipricing`. `gip_app` is created `NOLOGIN` by
`df53696a2682_platform_core_jobs_audit_events_outbox.py:61-73`, whose comment reads *"Deployment
creates a login role and grants it membership."* No deployment does:
`git grep -nE 'gip_app|APP_ROLE|SET (LOCAL )?ROLE' a3fc2e8d -- backend/src deploy` prints
nothing. Tests: `backend/tests/conftest_db.py:46` `DEFAULT_TEST_DSN =
"postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"`, `:104-138` the
per-worktree DSN with the same credentials, and the `database` fixture `:171-200`. CI:
`.github/workflows/python.yml:296` (migrate) and `:304-305` (tests), all `gipricing`. The
one test that acts as `gip_app` does `SET LOCAL ROLE gip_app` from the owner's session
(`backend/tests/test_transformations.py:523-551`). **The owner is a superuser:** measured
2026-10-14 12:07:50 BST on the shared container, `docker exec gi-pricing-postgres-1 psql -U
gipricing -d gipricing -Atc "select rolname, rolsuper, rolcanlogin from pg_roles where
rolname in ('gipricing','gip_app')"` → `gipricing|t|t`, `gip_app|f|f`. A superuser can also
bypass every trigger with `session_replication_role = replica`, as W7 does
(`df53696a2682:21-25` records the same).

**E6 — other DSN consumers** (S-b's census input):
`git grep -nE "GIP_DATABASE_URL|gipricing:gipricing|database_url" a3fc2e8d -- scripts deploy backend/src backend/migrations .github`
hits `scripts/bench-compiled-for.py`, `bench-rating.py`, `bench-score-batch.py`,
`check-rule-sets-runnable.py`, `check-seed-record.py`, the CI lines above, `config.py` and
`session.py`. `scripts/demo.py` starts compose, migrates and serves (`dev-commands` "The demo
entrance (FR-408)"), so it consumes both roles. **`examples/` is a consumer too** (plan review
R11, 2026-10-14): `examples/fremtpl2/seed.py:421` builds `Database(settings)` from
`load_settings()`, that is `GIP_DATABASE_URL`, and it is the only caller of the seed paths
(`roles`, `workspaces`, `workspace_members`; DP-22). **And 37 test files** build a connection
from `test_database_url()` rather than the `database` fixture (plan review R1):
`git grep -lE 'test_database_url\(\)' a3fc2e8d -- backend/tests | wc -l` prints `37`; the forms
are `database_url=SecretStr(test_database_url())` (`api_settings`, `backend/tests/conftest.py:52`,
feeds `api_client`), `Database(Settings(database_url=test_database_url()))`, and
`GIP_DATABASE_URL` set to it.

**E7 — the alembic head** at `a3fc2e8d` is `d4e81b7a2c95`: one head across 56 revisions. The
predicate: `git grep -hE '^(revision|down_revision)\b' a3fc2e8d -- backend/migrations/versions`,
then collect every quoted hex token of six or more characters, in either quote style, and
keep the revisions that no `down_revision` names.

## Slices

| Slice | Scope | Requirements | Depends on | Order and lane |
|---|---|---|---|---|
| **S-a = SL-8017** — the triggers | One Alembic migration. The `artifact_append_only()` pair goes on the nine append-only tables (`factors`, `rate_table_cells`, `rate_table_versions`, `rating_algorithms`, `reference_rows`, `reference_tables`, `regression_suite_versions`, `regression_suites`, `sub_graph_versions`). A column guard plus the `TRUNCATE` trigger go on `rate_tables` (W1) and `reference_table_versions` (W3). `dataset_versions` gets a guard that freezes its data from the first validation, with a `data_frozen_at` marker column, plus the `TRUNCATE` trigger (DP-21, ruled guarded 12:42:33; DP-21b, 13:21:41, refined 13:27:39). The `TRUNCATE` trigger also goes on the six tables that carry only a row guard (`approval_requests`, `blobs`, `deployment_requests`, `rating_versions`, `validation_rule_sets`, `validation_rules`), which are classed `guarded` (plan review R2, 2026-10-14). Every table's class and reason is the *Table classification* below (plan review R3). Layer 1 for all eleven: `factors` loses `UPDATE`; the ten get `SELECT, INSERT`, and the two guarded tables also get a column `UPDATE` on their allow-listed columns (DP-12). The append-only set is derived from a declaration on every mapped table (DP-8). W2 is removed in `rate_tables.py`. W4 to W6 are rewritten to insert. FD-8007's DP-1 `gip_app` test. `FR-44`, `FR-70` and `FR-229` dated lines. | `01` FR-43, FR-44, FR-70; `03` FR-229 and R1 (`03-rating-engine.md:41`); `06` FR-370 (the layer-1 form) | G2's merges on `main` (the maintainer's "right after the G2 merges"); `FD-8007`, `FD 8037` minted | first; lane: backend migrations. If `SL-1274` also adds a migration, DP-7 applies |
| **S-b = SL-8041** — least privilege | A login role that is a member of `gip_app`, provisioned for compose, CI and the shared container; `GIP_DATABASE_URL` is the application's DSN and a new `GIP_MIGRATION_DATABASE_URL` is the owner's, read only by `migrations/env.py` and owner-only tooling (DP-16). The test `database` fixture runs as the login role, and a new `owner_database` fixture is used for teardown, catalog checks and DDL (DP-18); every test connection built from `test_database_url()` moves to the login role with it, and a test keeps the owner only by name, with a reason (plan review R1, 2026-10-14). The grants are found red first from that run, diffed against the census, and written as one migration that also revokes every grant no census row or red needs, pinned by an exact grant map over every table (DP-20; plan review R6, R9). A startup refusal under the one membership predicate P-own (owner, superuser or `BYPASSRLS` role) and when a declared trigger is missing, not enabled or has a changed function body, in the API and the worker (DP-19, DP-14; plan review R4, R5). The tamper-resistance proof: the login role cannot `DISABLE TRIGGER` (DP-14). A convergent provisioning script with a stated rollback (plan review R7, R8). A compose run on a fresh volume. | `01` FR-43, FR-44; `06` FR-370 (*"the application role holds `INSERT` and `SELECT` only"*); NFR-458 | S-a merged (S-b's grant map includes S-a's grants); G2's merges; the `SL-1455` NFR session finished (it touches every DB path, so it must not move a measured baseline); `FD 8038` minted | second, and before the 4 Nov P2 code freeze. It runs the full gate **and** a compose run |

**Why two slices, in this order** (the maintainer's cut, restated as dependencies): the
trigger binds every caller, the owner included, so S-a closes the silent-price risk without
changing who connects. S-a is one migration plus test rewrites and one small reorder in
`rate_tables.py`. S-b changes the identity of every database connection, so its blast radius
is the whole suite. FD-8007's `REVOKE` and every grant are inert until S-b, because the owner
holds implicit privileges (E5). The triggers can be switched off by the owner until S-b:
`ALTER TABLE … DISABLE TRIGGER` needs only ownership, and `session_replication_role` needs only
superuser, and today the application holds a credential that is both (E5).

## Decision points

DP-1 to DP-7 are the first cut's, with their rulings. DP-8 onwards are the re-cut's.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | (S-a, factors.) The ADD asks for a `gip_app` `UPDATE` "refused by the NEW trigger". After the `REVOKE`, PostgreSQL refuses `gip_app` at the privilege check, before any trigger, and both refusals are SQLSTATE `42501`. How is the ADD met? | **(a)** Two observations in one test: (i) `SET LOCAL ROLE gip_app; UPDATE factors …` → `permission denied for table factors`; (ii) in one owner transaction `GRANT UPDATE ON factors TO gip_app`, `SET LOCAL ROLE gip_app`, the same `UPDATE` → `factors is append-only: UPDATE rejected (01 FR-42, FR-43)`, then `has_table_privilege` is false after rollback. **(b)** Only (i). **(c)** Only the owner test. | **(a)** | decision point | yes (S-a Task 3) | the maintainer (by delegation), `to-lead.md` "2026-10-14 10:29:14 BST", *"DP-1 → (a)"* |
| DP-2 | (S-a, factors.) `_make_control`'s callers flip a Factor after a Model or table pins it; every reader resolves by id or `slug@version`. What does the rewrite do? | **(a)** Arrange before pin: insert the control version first; `:299` builds its state by **inserting** a new rate-table version whose key's `factor_ref` names the control version. **(b)** Wrap the `UPDATE` in `DISABLE TRIGGER`. **(c)** Delete caller `:299`. | **(a)** | decision point | yes (S-a Task 4) | the same entry, *"DP-2 → as recommended"* |
| DP-3 | (S-a, factors.) Where does the control intent enter for caller `:344`? | **(a)** `_factor` (`test_model_jobs.py:193-204`) gains `intent: FactorIntent = FactorIntent.RISK`; `_fitted_gbm` (`test_model_jobs_gbm.py:88-115`) gains `area_intent`. **(b)** A copied local fixture. | **(a)** | decision point (write set) | yes (S-a Task 4) | the same entry, *"DP-3 → accepted"* |
| DP-4 | (first cut) A written `PINNED_BODY_TABLES = ("bandings", "factors", "groupings")` both-layers assertion. | — | **Superseded by DP-8**: the declaration-derived set covers every artifact table, so a separate three-table list would be a second, narrower copy. | scope | no | accepted as a default by the same entry; superseded by this re-cut, DP-8 |
| DP-5 | Who authors the FR text? | **(a)** This plan drafts it verbatim (S-a Task 5, S-b Task 7); the executor applies it through `spec-change`; the lead's GO adopts it. **(b)** A decision-maker writes it as an `RL-` T-text. | **(a)**, now covering `FR-44`, `FR-70`, `FR-229` (S-a) and `FR-44` again (S-b). The `FR-44` text changes what the invariant is derived from, which is more than a clarification, so the lead may route (b) at the GO. | decision point | no (default (a)) | the same entry, defaults accepted |
| DP-6 | How is each `downgrade()` proved? | **(a)** A recorded `downgrade -1` / `upgrade head` round trip with the catalog query printed before, between and after, in the `LG-`. **(b)** A standing `scratch_database` round-trip test. | **(a)** for both slices | decision point | no (default (a)) | the same entry, defaults accepted |
| DP-7 | Two slices chaining from one head make two heads. | The slice that merges **second** re-points its `down_revision` to the first one's revision and re-measures the head (E7's predicate) before its ACK request. No merge migration. Applies to S-a against `SL-1274` and to S-b against S-a and anything merged between. | as stated | fact (ordering) | no | the same entry, defaults accepted |
| DP-8 | (S-a) What is the append-only set **derived from**, now that grants are ruled out (authority 1 and 4)? | **(a) A declaration on every mapped table**, in the `test_approval_guard.py` form (E3): each `__table_args__` in `backend/src/app/db/models.py` carries `{"info": {"immutability": …}}`, one of `"append_only"`, `"guarded"` (with `"guards": [<every row-trigger name>]` and `"reason"`; *the list form, plan review R2 and R5, 2026-10-14: `models` has three row guards, and the startup check needs every name*) or `"mutable"` (with `"reason"`). The test derives the set from `Base.metadata`, **fails on any mapped table that declares nothing**, and cross-checks `pg_class` both ways (every public table but `alembic_version` is mapped). **(b) A closed written map in the test file** over every public table, with the same three classes and the same `pg_class` cross-check, and no change to `models.py`. **(c) Parse the `FR-44` list from the spec.** **(d) A structural proxy**: every table with `slug` and `version` columns, or named `*_versions`. | **(a).** It is the maintainer's "the ORM's artifact tables", and it puts the declaration where the next table's author writes the table. A new table fails until it is classified, so protection cannot be forgotten silently. The repo already derives the approval guard's set this way. Cost: 59 mapped classes edited in one hot file (`models.py`, 58 `__table_args__`); the edit is mechanical and S-a lands right after G2. **(b)** is the fallback if the GO finds `models.py` contended; it is equally closed but sits apart from the declaration. (c) couples a test to prose. (d) is a proxy that catches by name: `rate_tables` and `reference_tables` have no `version` column. | decision point | **yes** (S-a Task 2) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"DP-8 → the ORM declaration on all 59 tables, closed both ways vs pg_class"*; the fallback only if G2 slips past S-a's window (Task 2.2) |
| DP-9 | (S-a, W1) `rate_tables.current_version` is updated on every new version, and it is also the version allocator (`rate_tables.py:214`, `version_number = table_row.current_version + 1`). How is `rate_tables` protected? | **(a) A column guard** `rate_tables_pointer_only()`: `DELETE` is refused; an `UPDATE` is allowed only when `NEW.current_version > OLD.current_version` and every other column except `updated_at` is unchanged, compared as `to_jsonb(NEW) - 'current_version' - 'updated_at'` against the same for `OLD`, so a column added later is guarded by default. Plus `rate_tables_no_truncate` (`artifact_append_only()`). Classified `guarded`. **(b) Remove the column**: derive the latest version as `max(version_number)` from `rate_table_versions` at each read (`:212`, `:214`, `:252`, `:262`, `diff_cache.py:97-112`), then make `rate_tables` plain append-only. **(c)** Leave `rate_tables` out. | **(a).** A pinned Rating Version names `slug@version` (`03` R1), so `current_version` is a pointer to the newest version, not a price input; moving it forward changes no approved price. (a) keeps it forward-only, so it can neither be rewound nor edited sideways. (b) changes the allocator and five readers in a G2-hot module, which is larger than S-a's "migration-only, low conflict" and is better as its own slice if wanted. (c) ignores a table the maintainer named. | decision point | **yes** (S-a Task 2) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"* |
| DP-10 | (S-a, W2) A parquet version's row is inserted, then `cells` is set and flushed again in the same transaction, which the database sees as an `UPDATE`. | **(a) Reorder**: in `_persist_new_version` (`rate_tables.py:1387-1481`), write the parquet blob **before** building `version_row`, and pass `cells=blob_ref.model_dump(mode="json")` to the constructor. The `rows` branch is unchanged. The row is then inserted complete and `rate_table_versions` is plain append-only. **(b)** A guard that allows `cells` to go from `NULL` to a value. | **(a).** (b) leaves a hole: a `rows`-storage version has `cells` `NULL` for ever, so (b) would let anyone attach a parquet body to an approved `rows` version. With (a), a duplicate version (`409`, `:1458-1464`) rolls back the blob's database row in the same transaction; the object store keeps the bytes, which are content-addressed and unreferenced. The executor states that consequence in the `LG-`. This is S-a's one `backend/src` change apart from `models.py`. | decision point | **yes** (S-a Task 2) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"* |
| DP-11 | (S-a, W3, FR-70) `publish_version` moves a reference table version `draft` → `published` in place. | **(a) A column guard** `reference_table_versions_publish_only()`: `DELETE` is refused; an `UPDATE` is allowed only when `OLD.status = 'draft' AND NEW.status = 'published'` and every other column is unchanged (`to_jsonb(NEW) - 'status'` against `OLD`'s). Plus the `TRUNCATE` trigger. Classified `guarded`. **(b) An append-only publication record** (a new table) with the status derived from it. | **(a).** It is the narrowest guard that keeps FR-70's "independently approvable" behaviour, and it is the `models_fit_immutable` and `blobs_content_immutable` precedent: one named transition, everything else frozen. (b) is a schema and service change outside "migration-only". | decision point | **yes** (S-a Task 2) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"* |
| DP-12 | (S-a) Layer 1 for the ten: `gip_app` holds **nothing** on them today (E1). Its grants are inert until S-b. Where do they land? | **(a) S-a**, in the same migration: `GRANT SELECT, INSERT` on all ten; `GRANT UPDATE (current_version, updated_at) ON rate_tables` and `GRANT UPDATE (status) ON reference_table_versions` (column privileges); `REVOKE UPDATE, DELETE … FROM PUBLIC` on all eleven. **(b) S-b**, inside the grant audit. | **(a).** It completes `FR-44`'s "both layers" for all eleven in one migration, it lets the existing exact-grant test (E3) pin them from S-a onwards, and it costs nothing at runtime until S-b. S-b's red run (DP-20) then confirms these grants are enough. | decision point | no (default (a)) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"DP-12, 13, 17: as recommended"* |
| DP-13 | (S-a, W5, W6) The test writers that shape a `rate_table_versions` row in place. | **(a)** Each test **inserts** a new version row carrying the shaped `definition` or `storage`, mirroring the seeded row's columns (`RateTableVersionRow`, `models.py:2073-2106`), and points the call under test at it. **(b)** `ALTER TABLE … DISABLE TRIGGER` around the write. | **(a)**, for the reason DP-2 (a) was ruled: a test that switches the guard off is the loophole under another name. If a test needs `rate_tables.current_version` to name the inserted version, it advances it forward, which DP-9 (a) allows. | decision point | no (default (a)) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"DP-12, 13, 17: as recommended"* |
| DP-14 | (S-a and S-b; FD 8038) The owner can `ALTER TABLE … DISABLE TRIGGER`, and a superuser can set `session_replication_role = replica`. How is tamper-resistance treated? | **(a)** State the dependency in FD 8038: S-a's triggers stop mistakes from every caller; they stop deliberate tampering only after S-b removes the owner's credential from the application and the worker. Residual risk: the migration credential and the superuser, which `06` FR-372's hash chain only detects. **(b)** (a), plus a **detective check** in S-b's startup refusal: no `pg_trigger` row on a declared `append_only` or `guarded` table has `tgenabled = 'D'`. *Amended, plan review R5, 2026-10-14: the check as written misses `ENABLE REPLICA TRIGGER` (`'R'`), `DROP TRIGGER` and a replaced function body; it now asserts that every declared trigger exists with `tgenabled IN ('O','A')` and that its function's `md5(prosrc)` equals a pinned value (Task 4.2).* **(c)** An event trigger that refuses `ALTER TABLE … DISABLE TRIGGER`. | **(b).** (a) is required (authority 1). The detective check costs one catalog query at startup and turns a silently disabled trigger into a refusal to start, which matches FR-372's "detectable rather than impossible". (c) needs a superuser to create, and the owner, a superuser today, can drop it, so it adds nothing once S-b lands and nothing before. S-b's red **R-b5** is the proof: the login role's `DISABLE TRIGGER` is refused with `must be owner of table`. | decision point | no for S-a; yes for S-b (Task 4) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"*; widened by the same item's superuser ruling (R-b6) |
| DP-15 | (S-b) How is the login role provisioned? | **(a) One idempotent SQL file**, `deploy/postgres/app-login-role.sql`: create `gip_app` `NOLOGIN` if absent (the migration tolerates it, `df53696a2682:66-73`), create the login role `NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS INHERIT` if absent, `GRANT gip_app TO` it. It is applied by compose's `/docker-entrypoint-initdb.d` mount on a fresh volume, by a new `scripts/provision-app-role.py` (asyncpg, owner DSN; the host has no `psql`, `dev-commands`) in CI, in `scripts/demo.py` and once on the shared container, and the password comes from `GIP_APP_DB_PASSWORD` (local default only, as compose's `gipricing` is). **(b)** A migration creates the login role. **(c)** The application keeps the owner's DSN and runs `SET ROLE gip_app` on each connection checkout. | **(a).** It is what `df53696a2682:61-63` already says deployment does. (b) puts a credential in a migration, which that migration's comment forbids. (c) leaves the owner's credential in the application, so `RESET ROLE` undoes it, and S-a stays switch-off-able by the application. Applying the file to the shared `gi-pricing-postgres-1` adds one cluster-wide role; the GO names it. | decision point | **yes** (S-b Task 1) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2): one idempotent provisioning SQL; *"my GO will NAME the target (the shared DB container), applied once, with before/after `\du` and grant read-backs in the LG"* |
| DP-16 | (S-b) Which variable carries which role? `migrations/env.py:31` reads the same `database_url` as the application (E5). | **(a)** `GIP_DATABASE_URL` / `Settings.database_url` is the **application's** login role; a new `Settings.migration_database_url: SecretStr \| None` (`GIP_MIGRATION_DATABASE_URL`) is the owner's; `env.py` reads only the new one and **fails loudly** when it is unset. Defaults: `config.py:120` becomes the compose login role on `gipricing`, which also retires `dev-commands`' "the bare command does not work" trap for the application. **(b)** `GIP_DATABASE_URL` stays the owner (migrations unchanged) and a new `GIP_APP_DATABASE_URL` is the application's. | **(a).** Under (b) the owner's credential stays in the application's environment by default, which is FD 8038's cause. Under (a) the application process does not need the owner's credential at all. Cost: every migration command changes its variable (`dev-commands`, CI `python.yml:296`, `conftest_db.py:133-135`, the gate scripts); the census (S-b Task 0) lists each. | decision point | **yes** (S-b Task 2) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"* |
| DP-17 | (S-b) The login role's name. | **(a)** A separate login role `gip_app_login`, member of `gip_app`, so `current_user` is `gip_app_login` and the grants stay on `gip_app` where every migration writes them. **(b)** `ALTER ROLE gip_app LOGIN`. | **(a)**, per `df53696a2682:61-63` ("creates a login role and grants it membership"). It also keeps the grant tests (`grantee = 'gip_app'`) unchanged. | decision point | no (default (a)) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"DP-12, 13, 17: as recommended"* |
| DP-18 | (S-b) How do the tests connect? | **(a)** The `database` fixture (`conftest_db.py:171-200`) connects as the login role on the same per-worktree database; a new `owner_database` fixture connects as the owner, for teardown (W7 needs a superuser), catalog queries, `GRANT`/DDL inside a test (DP-1's) and the owner-connection tests in `test_artifact_immutability.py`. Each test that needs the owner names it. `GIP_TEST_APP_DATABASE_URL` overrides, as `GIP_TEST_DATABASE_URL` does. **(b)** Tests stay on the owner, and a small set of smoke tests runs as `gip_app`. | **(a).** Only (a) runs every application path the suite covers as the role production uses, which is what "red-first per refused path" needs (DP-20). (b) leaves every unexercised path unverified, and that is how FD 8038 lasted. | decision point | **yes** (S-b Task 3) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"* |
| DP-19 | (S-b) Where does the startup refusal apply? | **(a)** Every environment, `local` included: `Database.assert_least_privilege()` (new, `app/db/session.py`) is called from the API's startup (`main.py:75`) and the worker's (`worker/entrypoint.py:32`). It raises when the membership predicate **P-own** (below the table) returns a row, plus DP-14 (b)'s trigger check. *Amended, plan review R4, 2026-10-14: the predicate was `current_user` a superuser or `pg_has_role(current_user, <owner of any public table>, 'USAGE')`; `USAGE` misses a membership held `WITH INHERIT FALSE`, which can still `SET ROLE` to the owner, and `rolsuper` on `current_user` misses membership in a superuser role.* The message names `scripts/provision-app-role.py`. **(b)** Refuse in `dev`, `uat` and `prod` only (the `require_startable` form, `config.py:204`), and warn in `local`. | **(a).** A local exemption is the path by which the owner connection survived; compose provisions the role (DP-15), so `local` can satisfy it. A process that uses `Database` without starting the API or the worker (the `scripts/bench-*` tools, E6) is classified by the census and gets the application DSN or the owner DSN explicitly. | decision point | **yes** (S-b Task 4) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"*; widened by the superuser ruling (R-b6) |
| DP-20 | (S-b) How are the grants audited red-first? | **(a)** Run the backend suite once (the gate slot) with DP-18 (a) in place and **before** the grant migration. Every `permission denied for table <t>` / `for sequence <s>` failure is a refused path. Each becomes one grant line, cited to the failing test, in one migration. An exact map test, `test_every_table_grants_the_application_exactly_its_declared_privileges`, pins `gip_app`'s table and column privileges for every public table against a written map, which is red on any drift either way. The postgres-pro agent reviews the map, as evidence only. **(b)** Grant `SELECT, INSERT, UPDATE, DELETE` on every table that is not `append_only` or `guarded`, then trim. | **(a).** (b) grants first and audits later, which is the "decorative layer" the requirement forbids. Under (a), every grant has a failing test as its reason, and a table that no test writes gets no write grant. A path the suite does not exercise and the compose run (Task 6) finds is added the same way, red first. *Amended, plan review R6 and R9, 2026-10-14: the red-run list is diffed against the census in the `LG-` (a census row with no red is a test gap, closed red first; a red with no census row is a census miss, recorded), and every existing privilege that neither a census row nor a red needs is revoked in the same migration (Task 5.1).* | decision point | **yes** (S-b Task 5) | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (2), *"as recommended"* |
| DP-21 | (S-a; plan review R3, 2026-10-14; the lead's "DP-A") `dataset_versions` is "the immutable snapshot" of `CLAUDE.md` §7 and `00` §2, yet the application updates **11 columns in place** (census, `rv-writes.md` lines 109-117; each column's sites are in *DP-21's column classification* below). How is it classed? | **(a) `mutable`** with a reason, and a finding. **(b) `guarded`**: a column-guard trigger in S-a, in DP-9's form, enforcing a class per column. **(c) Restructure** so the row is inserted complete and lifecycle state moves to an append-only record, as DP-10 did for W2. | The planner recommended (a) with (b) as the finding's remedy, because (b) rests on each update site's status precondition. **Superseded by the ruling.** | decision point (spec vs code) | **yes** (S-a Task 2) | **RULED (b), GUARDED**: the maintainer (by delegation), `to-lead.md` "2026-10-14 12:42:33 BST": *"**DP-A → GUARDED, not mutable.** `dataset_versions` is "an immutable snapshot" (00 §2/§7 …). The planner classifies each of the 11 in-place-updated columns as (i) a LIFECYCLE column (`status`: only `draft → validated → archived` per the spec, forward-only), (ii) SET-ONCE (null → value exactly once, e.g. a report/profile ref), or (iii) FORBIDDEN after insert (data/hash/schema columns). A column-guard trigger enforces exactly that, like rate_tables.current_version (DP-9), with a red per class. Any column that fits none of the three comes to me with its code site; no "mutable with a reason" for this table."* Five columns fit none of the three; the planner listed them as **DP-21b**, **RULED** by the maintainer (by delegation), `to-lead.md` "2026-10-14 13:21:41 BST": *"**PL 8016 DP-21b → GUARD BY STATE, as proposed.** … My 12:42:33 three-class rule is superseded for this table by this state rule."* **REFINED** at "2026-10-14 13:27:39 BST" (*"(c), REFINED, which supersedes my 13:21:41 DP-21b wording for this table"*): the data frozen from the first `draft → validating`, forever; `status` per `VALID_DATASET_TRANSITIONS`; the report id only out of `validating`; no re-profiling after the freeze. See *DP-21's guard* |
| DP-22 | (S-b; plan review R6, 2026-10-14; the lead's "DP-B") Write paths with **no production caller** (census, `rv-writes.md` lines 77, 95-96, 119, 191, 322-325): (1) blob GC, `blobs` `DELETE` (`blobs.py:422`, `collect_garbage`); (2) `delete_trace`, `scoring_traces` `DELETE` (`traces.py:332`); (3) `purge_subject`, `subject_purges` `INSERT` (`datasets.py:1043`); (4) `grant_role` and (5) `grant_break_glass`, `role_assignments` `INSERT` (`rbac.py:366`, `:451`). Which get a grant? | **(a) Grant all.** **(b) Grant none**: owner and operations only; each test that exercises one uses the listed owner-only fixture; a path that gains a caller gets its grant red first in that slice. **(c) Split by kind** (grant the INSERT-only governance writes, not `blobs` `DELETE`). | The planner recommended (c). **Superseded by the ruling.** | decision point | **yes** (S-b Task 5) | **RULED (b), NOT GRANTED**: the maintainer (by delegation), `to-lead.md` "2026-10-14 12:42:33 BST": *"**DP-B → NOT granted to gip_app_login.** The five paths with no application caller (blob GC, delete_trace, purge_subject, grant_role, grant_break_glass) stay OWNER/ops-only: least privilege grants only what a caller uses (R6/R9's own rule). **The grant ships in the slice that adds the caller,** with its own red. grant_role/grant_break_glass are privilege-escalation paths and are never granted without a spec'd caller and my ruling. Tests that exercise them use the listed owner-only fixture (R1), labelled."* `scoring_traces` `DELETE` is still granted, for the live `complete_pending_trace` path (`traces.py:274-276`), not for `delete_trace`. `examples/fremtpl2/seed.py`: **RULED** at "2026-10-14 13:21:41 BST", *"**seed.py: NOT owner-wholesale.** The seed exercises the governed demo path (fits, approvals, rating versions), so it runs as the LOGIN role, with ONLY its bootstrap step (workspace, built-in roles, memberships: what no public route creates) through the owner connection."* Task 0 and Task 6 apply it; the bootstrap's `roles`, `workspaces`, `workspace_members`, `role_assignments` and its `users` writes go through the owner, and get no grant for that reason |

**P-own — the one membership predicate** (plan review R4 and R11, 2026-10-14). DP-19, R-b1,
R-b6 and Task 4.2 use this query **verbatim**, from one constant in `app/db` that the test
imports; no restatement. It returns every role the connected role is a member of (itself
included, `INHERIT` or not) that is a superuser, bypasses RLS, or owns a public relation, a
public function, the `public` schema or the current database. Any row is a refusal.

```sql
SELECT r.rolname
FROM pg_roles r
WHERE pg_has_role(current_user, r.oid, 'MEMBER')
  AND (r.rolsuper
       OR r.rolbypassrls
       OR EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                  WHERE n.nspname = 'public' AND c.relowner = r.oid)
       OR EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
                  WHERE n.nspname = 'public' AND p.proowner = r.oid)
       OR EXISTS (SELECT 1 FROM pg_namespace n WHERE n.nspname = 'public' AND n.nspowner = r.oid)
       OR EXISTS (SELECT 1 FROM pg_database d
                  WHERE d.datname = current_database() AND d.datdba = r.oid))
ORDER BY 1
```

`'MEMBER'` is true for a membership granted `WITH INHERIT FALSE` or held by a `NOINHERIT` role,
which `'USAGE'` is not, and such a membership can still `SET ROLE` to the owner. The
`pg_database_owner` role that owns `public` (`{pg_database_owner=UC, =U, gip_app=U}` at the head)
is matched only by a member of the database owner, which the `datdba` clause also catches.

### DP-21's guard: the data frozen at the first validation (ruled 12:42:33, 13:21:41, 13:27:39)

**The ruling in force**, the maintainer (by delegation), `to-lead.md` "2026-10-14 13:27:39 BST
— DP-21b §0 collision RULED: (c), REFINED; the DATA freezes at the FIRST validation and stays
frozen forever; FR-53's status/report changes are allowed", which *"supersedes my 13:21:41
DP-21b wording for this table"*, verbatim:
*"1. **The DATA is frozen from the FIRST `draft → validating` onward, FOREVER**: the `tables`,
schema, content-hash, row-count and identity columns, INCLUDING after FR-53 sends the version
back to `draft`. Models were fitted on that data (FR-53 flags them; it does not let the data
change under them). The `tables` writes the planner found ("up to 3 times while draft") are
allowed only BEFORE the first validation begins. A red: a version returned to `draft` by FR-53
refuses an UPDATE to `tables`.
2. **status** follows VALID_DATASET_TRANSITIONS (model_schema/datasets.py:86-96), including
FR-53's `validated → validating → (validated | draft)`; `archived` is terminal. A red per
illegal transition (the 12 stand).
3. **validation_report_id** may change ONLY on a transition out of `validating` (a new report per
run). The prior report rows are retained as records, never updated or deleted; the planner
confirms they are separate rows, and any overwrite is a STOP to me.
4. **profile_id:** the planner reads 01 for a requirement allowing RE-PROFILING of a validated
version. If one exists (cite it), allow the re-point only on the profiling Job's path (the same
transition discipline). If none exists, the guard REFUSES it, and `store_profile` re-pointing a
validated version (profiles.py:58) becomes a §0 item to me (code without spec), not silently
allowed.
5. `updated_at`: free. DELETE / TRUNCATE: refused."*
The 13:21:41 state rule of the previous commit (`2162b197`) is replaced by what follows, and its
refusal of `validated → validating` is gone.

**The 11 columns updated in place, with their write sites** (census, `rv-writes.md` lines
109-117, re-read at `a3fc2e8d`): `tables` (`data/ingestion.py:213`, `:462` `correct_schema`;
`platform/datasets.py:910` `derive_version`; `worker/data_handlers.py:358` the split);
`source_fingerprint` (`ingestion.py:214`); `derived_from` (insert, `datasets.py:495`; merged at
`ingestion.py:224-226`); `library_versions` (`ingestion.py:227`); `ingestion_run_id`
(`ingestion.py:253`); `totals` (`ingestion.py:254`); `status` (`datasets.py:582`,
`_transition`); `validation_report_id` (set on `validating → validated`, `datasets.py:644`;
cleared on `validating → draft` by FR-53, `:715`); `archived_at` (`datasets.py:740`);
`profile_id` (`platform/profiles.py:58`); `updated_at` (ORM `onupdate`, `models.py:862`).

**Finding for item 3 — the report rows are separate and never overwritten (no STOP).** Each
validation run inserts its own `validation_reports` row: `store_report` builds
`ValidationReportRow(id=report.id, …)` and `session.add(row)`s it
(`backend/src/app/platform/validation.py:77-118`), called once per run by the validation
handler (`worker/data_handlers.py:292`, dry runs included); the table's only index on the
version is non-unique, `ix_validation_reports_version (dataset_version_id, created_at)`
(`models.py:1072`); the census finds no `UPDATE` or `DELETE` of it (INS only, `rv-writes.md`
line 125); and it carries both append-only triggers (`a1b2c3d4e5f6:41` lists it in
`APPEND_ONLY`; the head catalog shows `validation_reports_no_modify` and `_no_truncate`).
`dataset_versions.validation_report_id` only re-points between those rows. Both of its writes
are transitions out of `validating`, which is item 3's rule.

**Finding for item 4 — no requirement allows re-profiling a validated version; a §0 item.**
`01` says profiling *"runs automatically after successful ingestion"* (FR-60, `:161`); the
profile is read through `GET /api/v1/dataset-versions/{id}/profile` (`:867`) and there is no
profile-producing route; the journey runs `profile_version` once, automatically (`01` §6 step
5, `:1113`). FR-61 to FR-67 (`:162-167`) specify what a profile contains, not when it is
recomputed. Searched: `git show origin/main:docs/specs/01-data-management.md | grep -niE
're-?profil|profile.*(validated|re-run|recomput|again|supersed)|profil.*version'`. **None
exists, so the guard refuses the re-point**, and `store_profile`'s re-point
(`platform/profiles.py:58`, its comment: *"Re-profiling adds a row and re-points"*) is **reported
to the maintainer as a `CLAUDE.md` §0 item (code without spec)**, via the lead, by this plan's
report and again in S-a's `LG-`. It is not allowed and not removed here.
*(Ruled 2026-10-14 by the maintainer (by delegation), `to-lead.md` "2026-10-14 15:14:52 BST",
item (4): "§0, re-profiling a validated version → REMOVE, not spec", on `00` :127, FR-60 `:161`,
the GET-only route `:867` and the journey `:1113`: (a) the guard allows `profile_id` only `NULL →
value` after the freeze, as planned; (b) **in this slice** the application path refuses a re-point
on a data-frozen version with a named problem code, `PROFILE_ALREADY_SET` (`409`), never a raw
trigger exception: Step 2.10; (c) a dated clarification on `01` FR-60, Steps 5.4 and 5.5. Item (3) is
confirmed in the same entry: "confirmed as separate, never overwritten … No STOP.")*

**The freeze marker.** "The first `draft → validating`" has to survive FR-53's return to
`draft`, and no column records it today (`status` returns to `draft`; `validation_report_id` is
cleared; a report row cannot stand for it, since a dry run inserts one against a `draft`
version without starting a validation, `data_handlers.py:283-296`). **Chosen: a new column
`dataset_versions.data_frozen_at timestamptz NULL`**, set by the guard itself (`NEW.data_frozen_at
:= now()`) on the first `draft → validating`, and never changed after; the application never
writes it. *Alternative considered:* the trigger looks for a `→ validating` row in
`audit_events`. Refused: it couples a guard to the audit log's action strings and costs a query
on every `UPDATE`. The column is in `models.py` (S-a's write set) as a read-only mapped column.
The migration back-fills it before the trigger exists: `status <> 'draft'`, or a `draft` row
whose audit chain records a transition to `validating` (the executor reads the action name from
`_transition`'s `audit.record`, `datasets.py:584` onwards), gets `COALESCE(updated_at,
created_at)`; the `LG-` prints the back-filled count. If a contract or schema-drift test demands
the column in `model-schema`, that is outside S-a's write set: the executor reports it to the lead
**before widening**. *(ACKed 2026-10-14, the maintainer (by delegation), "2026-10-14 15:14:52
BST", (B): "`dataset_versions.data_frozen_at`, set by the guard at the first `draft → validating`,
back-filled by the migration … models.py maps it read-only … A red: back-fill correctness on a
seeded FR-53 returned-to-draft row. If a contract test needs it in model-schema, report it before
widening." The red is Step 2.8b.)*

**The guard, `dataset_versions_snapshot_guard()`**, `BEFORE UPDATE OR DELETE … FOR EACH ROW`,
plus `dataset_versions_no_truncate`:
1. `DELETE` is refused in every state (item 5).
2. **Identity, in every state** (item 1): `to_jsonb(NEW)` minus the 11 and `data_frozen_at`
   must equal the same for `OLD` (DP-9's form; `id`, `workspace_id`, `dataset_id`, `version`,
   `kind`, `source_id`, `slug`, and any column added later).
3. **`status`** (item 2): `(OLD.status, NEW.status)` must be a pair of
   `VALID_DATASET_TRANSITIONS`, or unchanged; `archived` has no `UPDATE` at all. The table, in
   the guard as a `VALUES` list:

   | From (`OLD.status`) | Allowed `NEW.status` |
   |---|---|
   | `draft` | `validating`, `archived` |
   | `validating` | `validated`, `failed`, `draft` |
   | `validated` | `validating`, `archived` |
   | `failed` | `validating`, `archived` |
   | `archived` | none, terminal |

   A pin test asserts the guard's set equals `VALID_DATASET_TRANSITIONS` exactly, with no
   exception.
4. **The data** (item 1): once `OLD.data_frozen_at IS NOT NULL`, every change to `tables`,
   `source_fingerprint`, `totals`, `derived_from`, `library_versions` and `ingestion_run_id` is
   refused, in every state, `draft` included. The ruling names the `tables`, schema
   (inside `tables`' `arrow_schema`), content-hash (`source_fingerprint`), row-count (`totals`)
   and identity columns. **The planner adds `derived_from`, `library_versions` and
   `ingestion_run_id`** as the data's provenance: each is written only at ingestion, before any
   validation, so freezing them breaks no path. *(ACKed 2026-10-14, the maintainer (by delegation),
   "2026-10-14 15:14:52 BST", (A): "derived_from, library_versions and ingestion_run_id are frozen
   with the data".)* Before the
   freeze, all six may change (ingestion, `correct_schema`, derivation, split).
5. **`validation_report_id`** (item 3): it may change only when `OLD.status = 'validating'` and
   `NEW.status <> 'validating'`.
6. **`profile_id`** (item 4): before the freeze, it may change freely. After it, only `NULL →
   value`, once: a profiling Job that finishes after validation began records the profile of
   the frozen data. A re-point from one profile to another after the freeze is refused.
7. **`archived_at`**: `NULL → value`, only in the same `UPDATE` that moves `status` to `archived`.
8. **`updated_at`** is free (item 5). **`data_frozen_at`** is set only by rule (marker) and never
   changed.

**The reds**, owner connection, each in a transaction that rolls back, red on the base (the
write succeeds), one case each:
- **The illegal transitions** (item 2): the 12 of `2162b197` less `validated → validating`,
  which item 2 makes legal, so 11: `draft → validated`, `draft → failed`; `validating →
  archived`; `failed → validated`, `failed → draft`; `validated → draft`, `validated → failed`;
  `archived → draft`, `archived → validating`, `archived → validated`, `archived → failed`.
  Plus `archived` terminal: any `UPDATE` of an archived row, `updated_at` alone included.
- **The FR-53 data red** (item 1, the ruling's own): a version moved `draft → validating →
  draft` refuses an `UPDATE` of `tables`. The same case for each of the other five data columns.
- **Frozen in every later state:** an `UPDATE` of `tables` on a `validating`, a `validated` and
  a `failed` row.
- **`validation_report_id`** (item 3): a change on `draft → draft` and on `validated → validated`
  is refused.
- **`profile_id`** (item 4): a re-point on a `validated` row is refused (the guard); and
  `store_profile` on a data-frozen version with a profile refuses with `PROFILE_ALREADY_SET`
  (`409`) before any `UPDATE` (Step 2.10, 15:14:52 (4)(b)).
- **The back-fill** (15:14:52 (B)): Step 2.8b's seeded rows.
- **Identity:** `UPDATE … SET slug = slug || 'x'` is refused on a `draft` row.
- `DELETE` and `TRUNCATE` are refused.
- **Allowed (green before and after):** every pair of the transition table; FR-53's
  `validated → validating → validated` and `→ draft` with the report id moving on the way out
  of `validating`; a `tables` write on a never-validated `draft` row; `profile_id` `NULL →
  value` on a frozen row.

**Step 6.2's expectation** (13:27:39: *"Step 6.2 confirms no route/test breaks except any
re-profiling path under item 4"*): the full gate shows no refusal except a test or route that
re-profiles a frozen version. Each such failure goes to the lead with its node id, as the §0
item above; any other refusal is a plan defect, reported before any fix.

## Table classification (plan review R3, 2026-10-14)

All 59 mapped tables. `models.py`'s `__tablename__` values and the head database's public tables
are equal but for `alembic_version` (the review's diff: `git -C <repo> grep -hoE
'__tablename__ *= *"[a-z_0-9]+"' a3fc2e8d -- backend/src/app/db/models.py` against `pg_class`,
`relkind IN ('r','p')`, schema `public`). **Writes** is the census's application use at
`a3fc2e8d`: **INS**, **UPD(cols)**, **DEL**; **INSERT-only** and **read-only** are marked. **Row
guards** are the row-trigger names the declaration's `"guards"` lists; every `append_only` and
`guarded` table also carries `<table>_no_truncate`, and an `append_only` table carries
`<table>_no_modify`. *new* = added by S-a. Counts: **22 `append_only`, 13 `guarded`, 24 `mutable`**
(of the 24: 13 INSERT-only, 1 read-only, 10 updated in place).

| # | Table | Class | Row guards | Writes (census) | Reason |
|---|---|---|---|---|---|
| 1 | `api_keys` | mutable | — | INS; UPD(`expires_at`, `revoked_at`, `last_used_at`) | rotation, revocation and last-use stamping update the key row (`api/service_accounts.py:301`, `:363`; `auth/service.py:238`) |
| 2 | `approval_decisions` | mutable — **INSERT-only** | — | INS (`approvals.py:453`) | a governance record, never updated; append-only enforcement deferred (below) |
| 3 | `approval_policies` | mutable | — | INS; UPD(`policy`, `updated_at`) | `set_policy` replaces a workspace's policy in place (`approvals.py:221-226`) |
| 4 | `approval_requests` | guarded | `approval_guard` (+ `_no_truncate` *new*) | INS; UPD(`status`, `decided_at`, `withdrawn_reason`) | the request's lifecycle moves under `approval_guard`'s `flag_only` mode (`a9f3c6d21b87:100`) |
| 5 | `audit_events` | append_only | — | INS | `06` FR-370 |
| 6 | `backtests` | append_only | — | INS | an artifact (`test_artifact_immutability.py:38-52`) |
| 7 | `bandings` | append_only | — | INS | as 6 |
| 8 | `blobs` | guarded | `blobs_content_immutable` (+ `_no_truncate` *new*) | INS; UPD(`ref_count`); DEL (GC, no caller; DP-22) | only `ref_count` may move (`a1b2c3d4e5f6:55-69`) |
| 9 | `custom_metrics` | guarded | `approval_guard`, `custom_metrics_definition_immutable`, `custom_metrics_undeletable` | INS; UPD(`status`, `certificate_id`, `approval_request_id`) | the definition is frozen, the lifecycle moves |
| 10 | `custom_objectives` | guarded | `approval_guard`, `custom_objectives_definition_immutable`, `custom_objectives_undeletable` | INS; UPD(`derived`, `status`, `certificate_id`, `approval_request_id`) | as 9 |
| 11 | `dataset_splits` | mutable — **INSERT-only** | — | INS (`datasets.py:1096`) | the record of a split; deferred (below) |
| 12 | `dataset_versions` | guarded *new* (DP-21, ruled 12:42:33) | `dataset_versions_snapshot_guard` (+ `_no_truncate` *new*) | INS; UPD(11 columns, *DP-21's guard*) | "the immutable snapshot" (`00` §2, `CLAUDE.md` §7): the data frozen from the first `draft → validating`, forever; `status` per `VALID_DATASET_TRANSITIONS`; the report id moves only out of `validating` (13:27:39) |
| 13 | `datasets` | mutable | — | INS; UPD(`data_dictionary`, `owner_id`, `validation_rule_set_id`) | a named container that holds no data (`CLAUDE.md` §7); its dictionary, owner and rule set change (`datasets.py:291`, `:352`; `validation_rules.py:892`) |
| 14 | `deployment_requests` | guarded | `approval_guard` (+ `_no_truncate` *new*) | INS; UPD(`approval_request_id`, `status`) | lifecycle under `approval_guard` (`c4a81f6d2e95`) |
| 15 | `deployments` | append_only | — | INS | as 6 |
| 16 | `diagnostics` | append_only | — | INS | as 6 |
| 17 | `dislocation_runs` | mutable — **INSERT-only** | — | INS (`dislocation_runs.py:103`) | a run record; deferred (below) |
| 18 | `environment_settings` | mutable | — | INS; UPD(`value`, `updated_by`, `updated_at`) | a setting's value is replaced (`settings.py:603-611`) |
| 19 | `environments` | mutable | — | INS; UPD(`name`, `description`, `retired_at`) | renamed and retired in place (`environments.py:262-373`) |
| 20 | `factors` | append_only *new* | — | INS | FD-8007; S-a |
| 21 | `groupings` | append_only | — | INS | as 6 |
| 22 | `ingestion_runs` | mutable — **INSERT-only** | — | INS (`data/ingestion.py:252`) | a run record; deferred (below) |
| 23 | `job_logs` | mutable — **INSERT-only** | — | INS (`worker/logs.py:86`; `seq` is an identity) | a log; deferred (below) |
| 24 | `jobs` | mutable | — | INS; UPD(status, progress and the other lifecycle columns) | the Job's lifecycle (`jobs.py:214-287`; `worker/progress.py:200`) |
| 25 | `metric_certificates` | append_only | — | INS | as 6 |
| 26 | `model_comparisons` | append_only | — | INS | as 6 |
| 27 | `models` | guarded | `approval_guard`, `models_fit_immutable`, `models_fitted_undeletable` | INS; UPD(`fit_result`, `diagnostics_id`, `status`, `job_id`, `approval_request_id`) | the fit is frozen once recorded, the lifecycle moves |
| 28 | `objective_certificates` | append_only | — | INS | as 6 |
| 29 | `outbox` | mutable | — | INS; UPD(`attempts`, `last_error`, `status`, `published_at`) | the relay marks each row (`outbox.py:112-134`) |
| 30 | `peril_structures` | guarded | `approval_guard`, `peril_structures_composition_immutable`, `peril_structures_reconciled_undeletable` | INS; UPD(`reconciliation`, `job_id`, `status`, `approval_request_id`) | the composition is frozen, the lifecycle moves |
| 31 | `profiles` | append_only | — | INS | as 6 |
| 32 | `rate_table_cells` | append_only *new* | — | INS | FD 8037; `03` FR-229 |
| 33 | `rate_table_versions` | append_only *new* | — | INS (W2 removed, DP-10) | FD 8037; `03` FR-229 |
| 34 | `rate_tables` | guarded *new* | `rate_tables_pointer_only` | INS; UPD(`current_version`, `updated_at`) | DP-9 |
| 35 | `rating_algorithms` | append_only *new* | — | INS | FD 8037; `03` R1 |
| 36 | `rating_versions` | guarded | `approval_guard` (+ `_no_truncate` *new*) | INS; UPD(`bundle`, `evidence`, `change_summary`, `status`, `approval_request_id`, `updated_at`) | lifecycle and compiled bundle under `approval_guard`; the `TRUNCATE` gap (E1) closed |
| 37 | `reference_rows` | append_only *new* | — | INS | FD 8037; `01` FR-70 |
| 38 | `reference_table_versions` | guarded *new* | `reference_table_versions_publish_only` | INS; UPD(`status`) | DP-11 |
| 39 | `reference_tables` | append_only *new* | — | INS | FD 8037; `01` FR-70 |
| 40 | `regression_runs` | mutable — **INSERT-only** | — | INS (`regression_runs.py:46`) | a run record; deferred (below) |
| 41 | `regression_suite_versions` | append_only *new* | — | INS | FD 8037 |
| 42 | `regression_suites` | append_only *new* | — | INS | FD 8037 |
| 43 | `role_assignments` | mutable — **INSERT-only** | — | INS (`rbac.py:366`, `:451`; no production caller, DP-22) | revocation is not built; deferred (below) |
| 44 | `roles` | mutable — **INSERT-only** | — | INS (`rbac.py:136`; seed only, DP-22) | deferred (below) |
| 45 | `scoring_traces` | mutable | — | INS; DEL (`complete_pending_trace` replaces a pending row by `DELETE` + `INSERT`, `traces.py:274-276`; `delete_trace` no caller) | a pending trace is replaced |
| 46 | `service_accounts` | mutable — **INSERT-only** | — | INS (`api/service_accounts.py:220`) | deferred (below) |
| 47 | `sources` | mutable — **INSERT-only** | — | INS (`datasets.py:130`) | deferred (below) |
| 48 | `sub_graph_versions` | append_only *new* | — | INS | FD 8037 |
| 49 | `subject_purges` | mutable — **INSERT-only** | — | INS (`datasets.py:1043`; no production caller, DP-22) | a governance record; deferred (below) |
| 50 | `tenant_marker` | mutable — **read-only** | — | none; `SELECT` at startup (`platform/tenancy.py:52`) | written only by migration `d7e2a9b5c418`; the application needs `SELECT` (Task 5.1) |
| 51 | `transparency_artifacts` | append_only | — | INS | as 6 |
| 52 | `users` | mutable | — | INS; UPD(`email`, `display_name`, `last_login_at`) | the OIDC login upserts the user (`auth/service.py:166-170`) |
| 53 | `validation_acknowledgements` | append_only | — | INS | as 6 |
| 54 | `validation_reports` | append_only | — | INS | as 6 |
| 55 | `validation_rule_sets` | guarded | `approval_guard` (+ `_no_truncate` *new*) | INS (`validation_rules.py:884`) | under `approval_guard` |
| 56 | `validation_rules` | guarded | `approval_guard` (+ `_no_truncate` *new*) | INS; UPD(`dry_run_report_id`, `status`, `approved_by`) | lifecycle under `approval_guard` |
| 57 | `workspace_members` | mutable — **INSERT-only** | — | INS (`workspaces.py:115`; seed only, DP-22) | deferred (below) |
| 58 | `workspace_settings` | mutable | — | INS; UPD(`value`) | a setting's value is replaced (`settings.py:549-551`) |
| 59 | `workspaces` | mutable — **INSERT-only** | — | INS (`workspaces.py:44`; seed only, DP-22) | deferred (below) |

**The 13 INSERT-only tables and `tenant_marker`: deferred, with an owner.** Their declaration
is `mutable` because the catalog leaves them so and none is in the maintainer's ruled set
(`factors` and the ten). Each `reason` reads *"INSERT-only (read-only for `tenant_marker`) in
application code at `a3fc2e8d`; append-only enforcement deferred (plan review R3)"*, so the
class states no false reason. **Owner of the deferral: the lead (WK-1178)**, to whom S-a's `LG-`
reports the list as an FD candidate; `approval_decisions` and `subject_purges`, governance
records, are named first. Making them `append_only` is the same loop in a later migration.
S-b's exact grant map gives none of the 14 an `UPDATE` or `DELETE` (Task 5.2), so the privilege
layer holds the line until then.

## Write set

**S-a (SL-8017)**

| File | Change | Task |
|---|---|---|
| `backend/src/app/db/models.py` | `{"info": {"immutability": …}}` on every mapped table (DP-8 (a)); `DatasetVersionRow.data_frozen_at`, a read-only mapped column the guard sets (DP-21, 13:27:39) | 2 |
| `backend/migrations/versions/<rev>_artifact_tables_append_only.py` | **create**: one migration (triggers, three guard functions (`dataset_versions`' by DP-21), the six row-guarded tables' `TRUNCATE` triggers (plan review R2), grants, revokes) | 2 |
| `backend/src/app/platform/rate_tables.py` | `_persist_new_version`: blob before row (DP-10) | 2 |
| `backend/src/app/platform/profiles.py`, `backend/src/app/errors.py`, `backend/tests/test_profile_refusal.py` (**create**) | `store_profile` refuses a re-point on a data-frozen version with `PROFILE_ALREADY_SET` (`409`); the code registered (15:14:52 (4)(b)) | 2 |
| `backend/tests/test_artifact_immutability.py` | the declaration-derived tests (replacing the grants-derived one), the eleven rows, the guard tests, DP-1's `gip_app` test | 1, 2, 3 |
| `backend/tests/test_fr240_governance.py`, `test_model_jobs.py`, `test_model_jobs_gbm.py` | W4 (DP-2, DP-3) | 4 |
| `backend/tests/test_rate_table_diff_portfolio.py`, `test_rating_version_change_summary_route.py` | W5, W6 (DP-13) | 4 |
| `docs/specs/01-data-management.md` (`FR-44` `:106`, `FR-60` `:161` (15:14:52 (4)(c)), `FR-70` `:177`, §5.1's error-code list `:931-937`), `docs/specs/03-rating-engine.md` (`FR-229` `:122`) | dated lines (DP-5) | 5 |
| `docs/ledgers/LG-<id>.md`, `docs/roadmap.md` (SL-8017's status line) | the slice's paperwork (Lean P2 L1) | all |

**S-b (SL-8041)**

| File | Change | Task |
|---|---|---|
| `deploy/postgres/app-login-role.sql` (**create**), `deploy/docker-compose.yml` (initdb mount, `:9-21`; every `ports:` entry bound to `127.0.0.1`, `:16`, `:27`, `:42`, `:68`), `deploy/README.md` (provisioning, rollback, the binds), `backend/tests/test_compose_binds.py` (**create**) | DP-15; the 12:42:33 host-exposure item | 1 |
| `scripts/provision-app-role.py` (**create**), `backend/tests/test_provision_app_role.py` (**create**: the SCRAM verifier and no-secret-in-output test, plan review R8), `scripts/demo.py` | DP-15, DP-16 | 1, 2 |
| `backend/src/app/config.py` (`:120`; new `migration_database_url`), `backend/migrations/env.py` (`:31`) | DP-16 | 2 |
| `backend/src/app/db/session.py`, `backend/src/app/db/immutability.py` (**create**: `_declared`, P-own, the pinned function-body hashes), `backend/src/app/main.py`, `backend/src/app/worker/entrypoint.py` | DP-19, DP-14 (b); plan review R4, R5 | 4 |
| `backend/tests/conftest.py`, `backend/tests/conftest_db.py` (`OWNER_FIXTURE_USERS`), and each listed user of `owner_database` (plan review R1; 12:42:33) | DP-18 | 3 |
| `backend/migrations/versions/<rev>_application_role_grants.py` (**create**), `backend/tests/test_application_role.py` (**create**) | DP-20, R-b1 to R-b5 | 3, 4, 5 |
| `.github/workflows/python.yml` (`:290-306`), the `scripts/` consumers the census lists | DP-16 | 2 |
| `.claude/skills/dev-commands/SKILL.md` ("Migrations", `:932-949`), `.claude/skills/fastapi-service/SKILL.md` (the DSN post-mortem), `.claude/skills/README.md` | the new variables, same commit (`CLAUDE.md` §12) | 2 |
| `docs/specs/01-data-management.md` (`FR-44`), `docs/specs/07-platform.md` (wherever the census finds the DSN specified) | dated lines (DP-5) | 7 |
| `docs/ledgers/LG-<id>.md`, `docs/roadmap.md` (SL-8041's status line) | paperwork | all |

`examples/fremtpl2/seed.py` (`run`, `:420-427`: the owner `Database` for `grant_demo_principals`
only), its README, and `backend/tests/test_wf699_journey.py` (`:227`, `:518`: `owner_database`
for the bootstrap call) are in S-b's write set (plan review R11; 13:21:41 P2 (2)).

**Not in either write set:** `packages/**`, `docs/contracts/**`, the frontend.

## Tasks

### S-a (SL-8017)

#### Task 1: the reds by cause, on the base tree (tests only)

**Files:** `backend/tests/test_artifact_immutability.py`.

- [ ] **Step 1.1:** Add the eleven to `_APPEND_ONLY_ROWS` (`:303-343`), one insertable row each.
  Read each table's `NOT NULL` columns from its creating migration (E4's table of classes; for
  example `factors` is `3ab4db71d0e8_modelling_factors_and_models.py:33-45`). Do not copy column
  lists from this plan. `factors`, in the `bandings` form:

```python
    #: **Added 2026-10-14 (WK-1178, SL-8017, FD-8007).** A Model pins its Factors by row id,
    #: so an edited row re-prices every pinned fitted Model with the pin unchanged.
    "factors": (
        "INSERT INTO factors (id, workspace_id, dataset_id, slug, version, body) "
        "VALUES (:id, :ws, gen_random_uuid(), :slug, 1, :body)"
    ),
```

  `regression_suite_versions` needs its parent row: insert a `regression_suites` row with
  the same `:id` first in that entry's SQL (a two-statement entry runs as two `execute`s; the
  test loops over a `tuple[str, ...]` for that one key).
- [ ] **Step 1.2:** Split the owner-connection test (`:346-393`) by class, and **parametrise it
  over (table, statement)**, one case per pair, so that one `DID NOT RAISE` cannot hide the
  others: the existing loop over `UPDATE`, `DELETE` and `TRUNCATE` inside one test ends at its
  first failure (plan review R10, 2026-10-14; the ruling, 12:00:14: *"an OWNER
  UPDATE/DELETE/TRUNCATE on each table is refused by the trigger, red on main"*). The nine
  append-only tables keep the three statements and `"append-only" in str(refused.value)`. The `TRUNCATE`
  for `regression_suites` names `regression_suites, regression_suite_versions`, in the
  `deployments, scoring_traces` form (`:372-376`), because of E4's one foreign key. For the
  two guarded tables, add `test_a_guarded_artifact_moves_only_forward_from_the_owner_connection`,
  parametrised over two cases, each asserting four things as the owner:
  - **`rate_tables`:** `UPDATE … SET slug = slug || 'x'` is refused; `DELETE` is refused;
    `TRUNCATE` is refused; `UPDATE … SET current_version = current_version + 1` succeeds and
    `UPDATE … SET current_version = current_version - 1` is refused.
  - **`reference_table_versions`:** an edit to a non-status column is refused; `DELETE` and
    `TRUNCATE` are refused; `status` `draft` → `published` succeeds; `published` → `draft` is
    refused.
  The guard's message is asserted verbatim from Task 2's functions. Its four statements are
  also one case each.
  **The six row-guarded tables** (plan review R2): add
  `test_a_row_guarded_table_refuses_truncate_from_the_owner_connection`, one case per table
  (`approval_requests`, `blobs`, `deployment_requests`, `rating_versions`,
  `validation_rule_sets`, `validation_rules`), in a transaction that rolls back. A table that
  another table references by foreign key is truncated together with every referencing table,
  read from `pg_constraint` (`contype = 'f'`) at the GO, in the `deployments, scoring_traces`
  form. Expected after S-a: refused with `append-only`; the red prints which table the message
  names, and the catalog test of Step 2.3 (`<table>_no_truncate` present) is the
  table-specific proof.
- [ ] **Step 1.3:** Add the eleven to `APPEND_ONLY_TABLES` **only as a temporary red**, so the
  exact-grant test shows layer 1's state: `factors: ['INSERT', 'SELECT', 'UPDATE']` and, for
  each of the ten, `<t>: []`. Task 2 replaces the constant.
- [ ] **Step 1.4:** Run on the base, one file: `uv run pytest backend/tests/test_artifact_immutability.py -q`.
  Expected, **each by its cause**:
  - the exact-grant test fails at the first of the eleven, by its grant set (above);
  - the owner test fails `DID NOT RAISE` on **each** of `UPDATE`, `DELETE` and `TRUNCATE` for
    each of the nine, 27 cases (plan review R10);
  - the guarded test fails `DID NOT RAISE` on each refused statement for both, and the forward
    `current_version` and `draft → published` cases pass;
  - the row-guarded `TRUNCATE` test: each of the six fails `DID NOT RAISE`, or, where an
    existing referencing table's `TRUNCATE` trigger already refuses, the case prints that
    message, and the executor records it as such (plan review R2);
  - the `dataset_versions` reds of *DP-21's guard*: the 11 illegal transitions and the
    archived case, the FR-53 data red and its five siblings, the later-state `tables` cases, the
    report-id and profile cases, identity, `DELETE` and `TRUNCATE`, each `DID NOT RAISE`; the
    allowed cases pass (DP-21b as refined, 13:27:39);
  - the grants-derived test (`:396-446`) fails at its guard `:439`, with the eleven only on
    the right-hand side.
  A failure for any other reason is a plan defect: stop and report. Paste the lines into the
  `LG-` with the tree, every case's outcome (the run does not stop at the first). **This is the first owner-write observation on `reference_tables`**
  (E1 has none). Commit (test only).

#### Task 2: the declaration, the migration, and W1 to W3

**Files:** `backend/src/app/db/models.py`; create `backend/migrations/versions/<rev>_artifact_tables_append_only.py`;
`backend/src/app/platform/rate_tables.py`; `backend/tests/test_artifact_immutability.py`.

- [ ] **Step 2.1:** Re-measure the head at the GO with E7's predicate (expected `d4e81b7a2c95`
  unless something merged since; DP-7). Record it.
- [ ] **Step 2.2: the declaration (DP-8 (a), ruled 12:18:57).** **The switch:** if, at S-a's
  GO, G2's merges have not all landed on `main` (G2 slipped past S-a's window), the GO names
  DP-8 (b) instead: the same three classes as a closed map in `test_artifact_immutability.py`,
  checked against `pg_class` both ways, and `models.py` is not touched. Otherwise (a), as
  follows. On every mapped class, add a final dict to
  `__table_args__` (create the tuple where a class has none):
  `{"info": {"immutability": "append_only"}}`; or `{"info": {"immutability": "guarded", "guards":
  ["<row-trigger name>", …], "reason": "<one line>"}}`; or `{"info": {"immutability": "mutable",
  "reason": "<one line>"}}`. **Each table's class, guards and reason are the *Table
  classification* above, row by row** (plan review R3, 2026-10-14); the executor transcribes,
  it does not classify. The rule that table applies is the catalog **as it will be after S-a's
  migration**: the 13 of `APPEND_ONLY_TABLES` (`:38-52`) and the nine are `append_only`; the
  thirteen with a named row guard plus a `TRUNCATE` trigger are `guarded`, which after S-a
  includes `dataset_versions` (DP-21) and the six row-guarded tables whose `TRUNCATE` trigger Step 2.4 adds (plan review R2:
  under the first cut they were `mutable`, so the startup check skipped their triggers);
  everything else is `mutable` with the reason the table gives. `dataset_versions` is `guarded`
  (DP-21, 12:42:33; DP-21b, 13:21:41 as refined 13:27:39) by `dataset_versions_snapshot_guard`,
  written to *DP-21's guard*. **Any other table
  that a spec calls immutable but the catalog leaves mutable is reported to the lead in the
  `LG-` as an observation, not fixed here**; the 14 INSERT-only and read-only tables are
  reported as the classification's deferral says.
- [ ] **Step 2.3: the derived tests** replace `APPEND_ONLY_TABLES` and the grants-derived
  test. Keep the exact-grant test, now over the derived set:

```python
def _declared(kind: str) -> tuple[str, ...]:
    """The tables whose ORM declaration says `kind` (DP-8): derived, never restated."""
    return tuple(
        sorted(t.name for t in Base.metadata.sorted_tables if t.info.get("immutability") == kind)
    )


@pytest.mark.req("FR-44")
def test_every_mapped_table_declares_its_immutability() -> None:
    """A table that declares nothing fails here on the day it is added (FD 8037)."""
    failures = []
    for table in Base.metadata.sorted_tables:
        kind = table.info.get("immutability")
        if kind not in {"append_only", "guarded", "mutable"}:
            failures.append(f"{table.name}: immutability={kind!r}")
        elif kind != "append_only" and not table.info.get("reason"):
            failures.append(f"{table.name}: {kind} without a reason")
        elif kind == "guarded" and not table.info.get("guards"):
            failures.append(f"{table.name}: guarded without its named guard triggers")
    assert failures == []


@pytest.mark.req("FR-44")
async def test_the_declarations_cover_every_table_in_the_database(database: Database) -> None:
    async with database.session() as session:
        public = {
            row[0]
            for row in (
                await session.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                )
            ).all()
        }
    assert public - {"alembic_version"} == {t.name for t in Base.metadata.sorted_tables}
```

  Then `test_every_declared_append_only_table_carries_both_triggers`: the `:396-446` query
  with its `FROM` set taken from `_declared("append_only")` (a `= ANY(:tables)` filter), the same
  `missing == []` assertion, and its guard rewritten as
  `assert {row[0] for row in rows} == set(_declared("append_only"))`. Add
  `test_every_guarded_table_carries_its_named_guards_and_the_truncate_trigger`: for each
  `_declared("guarded")` table, **every** trigger its `guards` names exists as a row trigger
  (`tgtype & 1 = 1`), and `<table>_no_truncate` exists as a statement trigger (plan review R2:
  red on the base for the six row-guarded tables).
  `_declared` is the one source; no tuple of table names remains in the file.
- [ ] **Step 2.4: the migration.** Generate it with the `dev-commands` DSN
  (`GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_<wt> uv run --directory <wt>/backend alembic revision -m "artifact tables append only"`)
  and replace the body. Its docstring states FD 8037 and FD-8007, why the ten had neither
  layer, why `factors` rode `models`' grant (`b2c3d4e5f6a7:89`), W1 to W3 and their treatments,
  and that **the grants are inert until SL-8041** (FD 8038).

```python
APP_ROLE = "gip_app"

#: No column changes, no row goes (`03` R1, FR-229; `01` FR-70; FD 8037, FD-8007).
APPEND_ONLY = (
    "factors", "rate_table_cells", "rate_table_versions", "rating_algorithms",
    "reference_rows", "reference_tables", "regression_suite_versions",
    "regression_suites", "sub_graph_versions",
)
#: Ten had no grant at all; `factors` had `UPDATE` beside `models` (`b2c3d4e5f6a7:89`).
NEWLY_GRANTED = tuple(t for t in APPEND_ONLY if t != "factors") + (
    "rate_tables", "reference_table_versions",
)
#: A row guard already, and no `TRUNCATE` half until now (plan review R2, 2026-10-14):
#: `TRUNCATE rating_versions, <referencing tables>` emptied the approved price artifact.
ROW_GUARDED = (
    "approval_requests", "blobs", "deployment_requests", "rating_versions",
    "validation_rule_sets", "validation_rules",
)

RATE_TABLES_GUARD = """
CREATE OR REPLACE FUNCTION rate_tables_pointer_only() RETURNS trigger AS $fn$
BEGIN
  IF TG_OP = 'DELETE'
     OR NEW.current_version <= OLD.current_version
     OR (to_jsonb(NEW) - 'current_version' - 'updated_at')
        IS DISTINCT FROM (to_jsonb(OLD) - 'current_version' - 'updated_at') THEN
    RAISE EXCEPTION
      'rate_tables: only current_version may change, and only forward: % rejected (03 FR-229)', TG_OP
      USING ERRCODE = 'insufficient_privilege';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""

REFERENCE_VERSIONS_GUARD = """
CREATE OR REPLACE FUNCTION reference_table_versions_publish_only() RETURNS trigger AS $fn$
BEGIN
  IF TG_OP = 'DELETE'
     OR NOT (OLD.status = 'draft' AND NEW.status = 'published')
     OR (to_jsonb(NEW) - 'status') IS DISTINCT FROM (to_jsonb(OLD) - 'status') THEN
    RAISE EXCEPTION
      'reference_table_versions: only draft -> published: % rejected (01 FR-70)', TG_OP
      USING ERRCODE = 'insufficient_privilege';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    for table in APPEND_ONLY:
        op.execute(f"""
            CREATE TRIGGER {table}_no_modify
              BEFORE UPDATE OR DELETE ON {table}
              FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
        """)
    op.execute(RATE_TABLES_GUARD)
    op.execute(REFERENCE_VERSIONS_GUARD)
    op.execute("""
        CREATE TRIGGER rate_tables_pointer_only
          BEFORE UPDATE OR DELETE ON rate_tables
          FOR EACH ROW EXECUTE FUNCTION rate_tables_pointer_only();
    """)
    op.execute("""
        CREATE TRIGGER reference_table_versions_publish_only
          BEFORE UPDATE OR DELETE ON reference_table_versions
          FOR EACH ROW EXECUTE FUNCTION reference_table_versions_publish_only();
    """)
    # A row trigger does not fire on `TRUNCATE`, which is why every table also gets this.
    for table in APPEND_ONLY + ("rate_tables", "reference_table_versions") + ROW_GUARDED:
        op.execute(f"""
            CREATE TRIGGER {table}_no_truncate
              BEFORE TRUNCATE ON {table}
              FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
        """)
    # Layer 1 (DP-12). Inert until SL-8041: the application connects as the owner (FD 8038).
    op.execute(f"REVOKE UPDATE, DELETE ON factors FROM {APP_ROLE}")
    for table in NEWLY_GRANTED:
        op.execute(f"GRANT SELECT, INSERT ON {table} TO {APP_ROLE}")
    op.execute(f"GRANT UPDATE (current_version, updated_at) ON rate_tables TO {APP_ROLE}")
    op.execute(f"GRANT UPDATE (status) ON reference_table_versions TO {APP_ROLE}")
    for table in APPEND_ONLY + ("rate_tables", "reference_table_versions"):
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM PUBLIC")


def downgrade() -> None:
    for table in APPEND_ONLY + ("rate_tables", "reference_table_versions") + ROW_GUARDED:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_truncate ON {table}")
    op.execute("DROP TRIGGER IF EXISTS reference_table_versions_publish_only ON reference_table_versions")
    op.execute("DROP TRIGGER IF EXISTS rate_tables_pointer_only ON rate_tables")
    for table in APPEND_ONLY:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_modify ON {table}")
    op.execute("DROP FUNCTION IF EXISTS reference_table_versions_publish_only()")
    op.execute("DROP FUNCTION IF EXISTS rate_tables_pointer_only()")
    op.execute(f"REVOKE UPDATE (status) ON reference_table_versions FROM {APP_ROLE}")
    op.execute(f"REVOKE UPDATE (current_version, updated_at) ON rate_tables FROM {APP_ROLE}")
    for table in NEWLY_GRANTED:
        op.execute(f"REVOKE SELECT, INSERT ON {table} FROM {APP_ROLE}")
    # Exactly `b2c3d4e5f6a7`'s state on `factors`: `UPDATE` granted, `DELETE` never was.
    op.execute(f"GRANT UPDATE ON factors TO {APP_ROLE}")
```

  The guard functions are new; the `TRUNCATE` trigger reuses `artifact_append_only()`, so the
  owner test's `"append-only"` assertion holds for `TRUNCATE` on the guarded two and the six
  row-guarded tables as well. No application path truncates any of the six (census: no
  `TRUNCATE` in application code), and the test teardown (W7) runs under `replica`, which
  suspends it. The docstring states R2 and the six. If
  DP-9 or DP-11 is ruled (b), this step changes and the plan's delta says how.
  **`dataset_versions` (DP-21, 12:42:33; DP-21b, 13:21:41 as refined 13:27:39).** The same
  migration adds the column `data_frozen_at` and back-fills it, then
  `dataset_versions_snapshot_guard()` and its row trigger (`BEFORE UPDATE OR DELETE … FOR EACH
  ROW`) plus `dataset_versions_no_truncate`, exactly as *DP-21's guard* lists its eight rules, with the transition table as a `VALUES` list in the body and a
  message naming the state, the column or transition, and `00` §2. The downgrade drops both
  triggers, the function and the column. `dataset_versions` gets no grant here (it has none at the head;
  S-b's red run finds its column `UPDATE`s).
- [ ] **Step 2.5: W2 (DP-10 (a)).** In `_persist_new_version`, move the parquet branch's
  `blob_store.put` (`rate_tables.py:1474-1479`) above the `RateTableVersionRow(...)` constructor
  (`:1426`) and pass `cells=blob_ref.model_dump(mode="json") if blob_ref is not None else None`.
  The `rows` branch (`:1467-1473`) stays after the flush, since it needs `version_row.id`.
  `:1480` is deleted. Before the change, after the migration, run the parquet-storage tests
  (`uv run pytest backend/tests/test_rate_tables_service.py -q -k parquet`; if the `-k`
  selects nothing, the executor names the test that creates a parquet version). Expected red:
  `rate_table_versions is append-only: UPDATE rejected`. Paste it, then make the change.
- [ ] **Step 2.6: W1 and W3, red first.** With a temporary migration edit that makes
  `rate_tables` and `reference_table_versions` plain `append_only`, run the new-version and
  the publish tests. Expected red: `rate_tables is append-only: UPDATE rejected` and
  `reference_table_versions is append-only: UPDATE rejected`. This is the evidence that W1 and
  W3 are real paths. Revert to step 2.4's guards and see them green. Both outputs go into the
  `LG-`.
- [ ] **Step 2.7:** `alembic upgrade head`, then `alembic heads` (one head). The catalog after
  upgrade, printed into the `LG-` with E1's own query (`~/.claude/jobs/b6860f8f/tmp/fr44/q.sql:1-14`,
  run through `docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing_<wt>`): the
  eleven with their triggers and `gip_app`'s privileges, and the six row-guarded tables with
  their new `_no_truncate` (plan review R2).
- [ ] **Step 2.8: the downgrade (DP-6 (a)).** `downgrade -1`, the catalog, `upgrade head`, the
  catalog. All three outputs go into the `LG-`.
- [ ] **Step 2.8b: the back-fill red** (the maintainer (by delegation), "2026-10-14 15:14:52
  BST", (B): *"A red: back-fill correctness on a seeded FR-53 returned-to-draft row"*). At the
  previous revision (`downgrade -1`), seed three `dataset_versions` rows **through the
  services**, so their audit chains are real: (i) a version moved `draft → validating → draft`
  by `begin_validation` and `conclude_failed_validation` (FR-53's return, `datasets.py:674-716`);
  (ii) a never-validated `draft` version; (iii) a `validated` version. Then `upgrade head` and
  read `data_frozen_at`: expected (i) set, (ii) `NULL`, (iii) set. **Red first:** with the
  migration's back-fill `UPDATE` removed in a scratch edit, (i) reads `NULL` (and an `UPDATE`
  of its `tables` then succeeds). Restore it and see it green. The seeding script, the red line
  and the green read-back go into the `LG-`. Kept as a test too:
  `test_the_back_fill_freezes_a_version_fr53_returned_to_draft` in
  `test_artifact_immutability.py`, which runs the back-fill's own SQL (imported from the
  migration module as a constant) against rows it seeds the same way, in a transaction that
  rolls back.
- [ ] **Step 2.9:** `uv run pytest backend/tests/test_artifact_immutability.py -q`: green.
  Commit.
- [ ] **Step 2.10: the re-profiling refusal in the application** (the maintainer (by
  delegation), "2026-10-14 15:14:52 BST", (4)(b): *"the application path (profiles.py:58
  "Re-profiling adds a row and re-points") is changed IN THIS SLICE to refuse a re-point on a
  data-frozen version with a NAMED problem code (e.g. `PROFILE_ALREADY_SET`, 409), so the user
  never sees a raw trigger exception (a 500). The write set widens by profiles.py + its test,
  red first"*).
  - **The red first**, `backend/tests/test_profile_refusal.py` (**create**), through the
    `database` fixture and `store_profile` itself: on a version whose `data_frozen_at` is set
    and whose `profile_id` is already set, `store_profile` raises `PlatformError` with code
    `PROFILE_ALREADY_SET` and status `409`, adds no `profiles` row, and leaves `profile_id`
    unchanged. Red on the Task 2 tree before this step **by its cause**: the trigger's raw
    refusal (a database error, which the API would turn into a 500) instead of the named code.
    Two companion cases stay green: a frozen version with `profile_id` `NULL` takes its first
    profile, and a never-validated `draft` version may be re-profiled (before the freeze,
    rule 6).
  - **The change**, `backend/src/app/platform/profiles.py`: after the version lookup
    (`:36-43`) and before the `ProfileRow` is built (`:45`), when `version.data_frozen_at is
    not None and version.profile_id is not None`, raise `PlatformError("PROFILE_ALREADY_SET",
    "This version's profile is already recorded", 409, <detail citing 01 FR-60 and 00 §2>)`.
    The comment at `:55-57` (*"Re-profiling adds a row and re-points"*) is rewritten to say
    re-profiling is allowed only before the data freezes.
  - **The code is registered** in `backend/src/app/errors.py`'s `DATA_ERROR_CODES` (`:83-111`),
    and in `01` §5.1's list (Step 5.5). The existing per-artifact code
    `DATASET_VERSION_IMMUTABLE` (`errors.py:86`, `409`) is an alternative to a new code. The
    ruling's example name is used; the lead may choose the existing code at the ACK.
  - The full gate (Step 6.2) shows whether a route or Job re-profiles a frozen version (the
    profiling Job, `worker/data_handlers.py`). Each one now gets the `409`, and each goes into
    the `LG-` with its node id.

#### Task 3: FD-8007's `gip_app` test (DP-1 (a), the ADD)

- [ ] **Step 3.1:** Write `test_a_gip_app_update_on_factors_is_refused_by_the_trigger_not_only_the_grant`
  as the first cut drafted it (two `pytest.raises` blocks; messages `permission denied for
  table factors` and `factors is append-only: UPDATE rejected (01 FR-42, FR-43)`; then
  `has_table_privilege('gip_app', 'factors', 'UPDATE')` is `False` and the body is unchanged).
  The code is at `e29de1bc`, `docs/plans/PL-08016-…-plan-delta.md:227-274`; copy it from there
  and do not retype it. Before running, confirm that `database.session()` leaves a failed
  transaction uncommitted (`test_transformations.py:538-551` relies on it); if not, STOP.
- [ ] **Step 3.2:** On the Task 1 commit (before the migration), the test is red at the first
  block with `DID NOT RAISE`; with the first block removed in a scratch edit, red at the
  second, `DID NOT RAISE`. On the Task 2 tree, green. All three lines go into the `LG-`.
  Commit.

#### Task 4: the test writers (W4 to W6)

- [ ] **Step 4.1:** After Task 2, run `uv run pytest backend/tests/test_fr240_governance.py -q -k control`,
  `backend/tests/test_rate_table_diff_portfolio.py -q` and
  `backend/tests/test_rating_version_change_summary_route.py -q`, one at a time. Expected: the
  W4 to W6 tests fail with `<table> is append-only: UPDATE rejected`. This is the proof that
  the trigger refuses the owner connection the application uses. Paste them.
- [ ] **Step 4.2: W4, as ruled (DP-2 (a), DP-3 (a)).** `_make_control` (`:248-256`) becomes a
  helper that **inserts** a `control` version at `max(version) + 1` and returns its number,
  built like `_ensure_factor` (`test_api_rate_tables.py:164-194`). Caller `:270`: insert, then
  `_seed_approved_model(..., factor_versions={"driver_age_band": <n>})`; still `422`
  `CONTROL_FACTOR_IN_RATEABLE_PATH`. Caller `:344`: `_fitted_gbm(..., area_intent=FactorIntent.CONTROL)`;
  the fit still `SUCCEEDED` and compile still `FAILED` with that code. If the fit refuses a
  control Factor, STOP: DP-2's premise is false. Caller `:299`: insert a control version, then
  **insert** a new rate-table version whose key's `factor_ref` names it, and pin that version.
  Advance `rate_tables.current_version` forward if the call under test reads it (DP-9 allows
  it).
- [ ] **Step 4.3: W5 and W6 (DP-13 (a)).** Each of `test_rate_table_diff_portfolio.py:380`,
  `:489`, `:830`, `:1810` and `test_rating_version_change_summary_route.py:360` inserts a new
  version row carrying the shaped `definition` or `storage`, and points its call at that
  version. Read the row shape from `RateTableVersionRow` and the seeded row; do not invent
  columns.
- [ ] **Step 4.4: broken-input proof.** For each rewritten test, a scratch edit that inserts
  the unshaped value (a `risk` Factor; an intact `factor_ref`; `rows` storage) makes it fail by
  its cause (the refusal is absent). Revert, and record in the `LG-`.
- [ ] **Step 4.5:** `git grep -nE "UPDATE factors|factors SET|update\(RateTableVersionRow" -- backend`
  prints nothing. The three files are green. Commit.

#### Task 5: the spec lines (DP-5 (a)), in the migration's commit range

`<date>` is the commit date and `<rev>` Task 2's revision. Escape any `|` as `\|`.

- [ ] **Step 5.1: `FR-44`** (`01-data-management.md:106`), appended:
  `*(Amended <date>, WK-1178 SL-8017, on FD 8037 and FD-8007.)* **The set is declared, not derived from grants.** Eleven artifact tables were outside it: ten had no grant and no trigger, so a grants-derived set could not see them, and `factors` held `UPDATE` beside `models`. Every mapped table now declares `append_only`, `guarded` (a named narrower trigger and a reason) or `mutable` (a reason); a table that declares nothing fails a test. `<rev>` attaches both triggers to the nine new append-only tables, a forward-only guard to `rate_tables.current_version` and a `draft`-to-`published` guard to `reference_table_versions.status`. Layer 1 binds only once the application stops connecting as the owner (FD 8038, SL-8041).`
- [ ] **Step 5.2: `FR-70`** (`:177`), appended:
  `*(Amended <date>, WK-1178 SL-8017.)* Enforced in the database: `reference_table_versions` may move only `draft` to `published`, and `reference_tables` and `reference_rows` are append-only (`<rev>`).`
- [ ] **Step 5.3: `FR-229`** (`03-rating-engine.md:122`), appended:
  `*(Amended <date>, WK-1178 SL-8017, on FD 8037.)* Enforced in the database: `rate_table_versions` and `rate_table_cells` are append-only, and `rate_tables` may only move `current_version` forward (`<rev>`).`
- [ ] **Step 5.4: `FR-60`** (`01-data-management.md:161`), a dated clarification, through the
  `spec-change` skill (the maintainer (by delegation), "2026-10-14 15:14:52 BST", (4)(c): *"it
  decides refuse/allow, so it goes in the spec, per my 12:07:40 rule"*), appended:
  `*(Clarified <date>, WK-1178 SL-8017, on the maintainer's (by delegation) "2026-10-14 15:14:52 BST" ruling.)* **The profile is computed once per Dataset Version; a frozen version is never re-profiled.** A version's data freezes at its first `draft → validating` (`00` §2: the version is an immutable snapshot that carries its profile). A profile may still be recorded once after that if none was, and a second one is refused with `PROFILE_ALREADY_SET` (`409`).`
- [ ] **Step 5.5:** `01` §5.1's *"Error codes owned by this module"* list (`:931-937`) gains
  `PROFILE_ALREADY_SET`, in the same commit as `errors.py` (Step 2.10). If `spec-change` or the
  audit requires the code's row elsewhere (an error-code table, `00` §5's catalogue), it goes
  there in the same commit.
- [ ] **Step 5.6:** `python3 scripts/audit-docs.py` as one gate-2 docs check, and
  `uv run python scripts/req-coverage.py`. Commit.

#### Task 6: postgres-pro review and the gate

- [ ] **Step 6.1:** Delegate the migration to `postgres-pro`, read-only, as evidence. The
  brief names: the `dev-commands` DSN trap; one head (DP-7); the downgrade restores exactly
  the prior grants and triggers; the `to_jsonb(NEW) - …` comparison in both guards (a column
  of a type `to_jsonb` cannot compare would be a defect); the column `GRANT UPDATE` form; the
  `TRUNCATE` foreign-key order for `regression_suites`. Findings go into the `LG-`; one that
  changes the migration is a dated delta line there.
- [ ] **Step 6.2:** The full gate, both halves, in a gate slot. Any new `append-only` refusal is
  a write path E4 missed: add it to the `LG-` as a row of E4's table, red first, with its
  treatment, and report it to the lead before fixing (a fix outside DP-9 to DP-13 needs a
  ruling). Record the rc table.

### S-b (SL-8041)

#### Task 0: the census, before any edit

- [ ] **Step 0.1:** At the GO tree, run E6's predicate and
  `git grep -nE "Database\(|create_async_engine|alembic upgrade|GIP_TEST_DATABASE_URL|test_database_url\(|load_settings\(" -- backend/src backend/tests scripts deploy examples .github .claude/skills`
  (*widened, plan review R1 and R11, 2026-10-14: the first cut's predicate did not match
  `test_database_url(` and did not search `backend/tests` beyond the conftests or `examples/`*).
  Classify every hit: **application** (gets `GIP_DATABASE_URL`, the login role) or **owner**
  (gets `GIP_MIGRATION_DATABASE_URL`: migrations, provisioning, test teardown and catalog
  fixtures). `examples/fremtpl2/seed.py` is **split** (the maintainer (by delegation), "2026-10-14 13:21:41
  BST", P2 (2)): its `Database(settings)` at `:421` stays the **application** connection for
  every governed step, and only `grant_demo_principals` (`:318-381`; workspace, built-in roles,
  members and their role assignments) receives a second, **owner** `Database` built from
  `settings.migration_database_url` (DP-16). The split is possible inside the write set:
  `grant_demo_principals` already takes its `database` as a parameter (`:318`), so `run`
  (`:420-427`) passes the owner one there and the application one everywhere else; no
  platform module changes. `run` refuses to start when `migration_database_url` is unset,
  naming the variable. The WF-699 journey test calls the same function
  (`backend/tests/test_wf699_journey.py:227`, `:518`) and passes `owner_database` there,
  listed with the label `bootstrap`. Put the table in
  the `LG-` before Task 1. An entry that fits neither is reported to the lead.
- [ ] **Step 0.2:** Copy the census (`rv-writes.md`, with its commands and its tree) into the
  `LG-`, re-run its write-site predicate (its command 2) at the GO tree, and record any new
  site since `a3fc2e8d` as a census row. Task 5.1 diffs against this copy (plan review R6).

#### Task 1: provisioning (DP-15 (a))

- [ ] **Step 1.1:** Create `deploy/postgres/app-login-role.sql`:

```sql
-- The application's login role (FD 8038; df53696a2682:61-63: "Deployment creates a login
-- role and grants it membership"). Idempotent. Never a superuser, never an owner.
DO $do$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gip_app') THEN
    CREATE ROLE gip_app NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gip_app_login') THEN
    CREATE ROLE gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
      NOBYPASSRLS INHERIT;
  END IF;
END
$do$;
-- Converge, not only create (plan review R7, 2026-10-14): a role that already exists with
-- CREATEROLE, CREATEDB or REPLICATION is reset here on every run.
ALTER ROLE gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
  NOBYPASSRLS INHERIT;
GRANT gip_app TO gip_app_login;
```

  The file carries no password. A repeated `GRANT gip_app TO gip_app_login` prints a NOTICE
  in PostgreSQL 16 and is not an error; the second application of Step 1.3's proof run shows it.
- [ ] **Step 1.2:** Create `scripts/provision-app-role.py`: it connects with
  `GIP_MIGRATION_DATABASE_URL` (asyncpg), executes the file, then sets the password from
  `GIP_APP_DB_PASSWORD` **as a pre-hashed SCRAM-SHA-256 verifier** (plan review R8, 2026-10-14):
  the script computes `SCRAM-SHA-256$<iterations>:<salt>$<StoredKey>:<ServerKey>` client-side
  (RFC 5802 / RFC 7677, `hashlib.pbkdf2_hmac` and `hmac`, 4096 iterations, a random 16-byte
  salt) and sends `ALTER ROLE gip_app_login PASSWORD '<verifier>'`. PostgreSQL stores a
  verifier as given, so the plain password never reaches the server, its log under
  `log_statement`, or an error message; the script never prints it or the verifier. **Chosen
  over `\password`** because the host has no `psql` (`dev-commands`) and the step must run
  unattended in CI and compose. A unit test checks the verifier against a known RFC 7677 vector
  and that the script's output contains neither value. The default `gip_app_login` is for a
  fresh local volume only, as compose's `gipricing` is (`docker-compose.yml:14`): **the script
  refuses the default unless `--allow-default-password` is passed**, which CI and the
  separate compose project of Task 6 pass explicitly, and which the shared container's
  application does not. Mount the SQL file in compose
  (`./postgres/app-login-role.sql:/docker-entrypoint-initdb.d/10-app-login-role.sql:ro`) for
  fresh volumes. A fresh volume still needs the password step: the compose run (Task 6) calls
  the script.
- [ ] **Step 1.3:** Apply the script to the target the maintainer's GO names (the shared DB
  container, DP-15 as ruled 12:18:57), **with a non-default `GIP_APP_DB_PASSWORD`** (plan
  review R8: roles are cluster-wide, so `gip_app_login` exists in every database there and can
  connect to each, `datacl` being NULL; port 5432 is published on `0.0.0.0` and `[::]`). The
  password is held outside the repository in the file the GO names, mode `0600`; the `LG-`
  records that it was set and where, **never the value**. Every worktree that runs the suite on
  the shared container then exports `GIP_APP_DB_PASSWORD` from that file (Task 3.1); the gate
  scripts and `dev-commands` say so. It is applied **once** to the shared container, as ruled.
  **The idempotence and convergence proof runs first, on Task 6's separate compose project**
  (`gip-sl8041`, fresh volume), never on the shared container (plan review R7): there, create
  `gip_app_login` by hand `WITH CREATEROLE CREATEDB REPLICATION`, apply the script **twice**,
  and record both exit codes (both 0) and `select rolname, rolsuper, rolcreaterole,
  rolcreatedb, rolreplication, rolbypassrls, rolinherit from pg_roles where rolname =
  'gip_app_login'` after each run (identical, and every attribute reset). That run precedes
  this step. **Before and after** the shared-container application, record in the `LG-`
  `docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -c '\du'` and the grant
  read-back `select grantee, table_name, string_agg(privilege_type, ',' order by
  privilege_type) from information_schema.role_table_grants where grantee in ('gip_app',
  'gip_app_login') group by 1, 2 order by 1, 2`. Read back `select rolname, rolsuper, rolcanlogin from pg_roles where rolname
  like 'gip_app%'` and `select pg_has_role('gip_app_login', 'gip_app', 'MEMBER')` into the
  `LG-`.
- [ ] **Step 1.4: the rollback, stated and rehearsed** (plan review R8, 2026-10-14).
  - **Provisioning.** First `select count(*) from pg_shdepend where refobjid = (select oid from
    pg_roles where rolname = 'gip_app_login') and deptype <> 'a'` in each database of the
    cluster must be 0, and `pg_stat_activity` must show no `gip_app_login` session; then
    `REVOKE gip_app FROM gip_app_login; DROP ROLE gip_app_login;`. This works because every
    table grant goes to `gip_app` (DP-17), so the login role owns nothing and holds no direct
    privilege; `DROP ROLE` itself refuses if that ever stops being true. `gip_app` is left as
    the migrations made it.
  - **S-b's code.** Reverting the slice's PR restores the owner DSN default and the single
    `GIP_DATABASE_URL`; `downgrade -1` of the grant migration revokes exactly its grants and
    re-grants exactly what it revoked (Task 5.1); the role can stay, harmless, or be dropped as
    above. On the shared container a revert affects every worktree on the reverted code, which
    goes back to the owner connection; the `LG-` says so.
  - **Rehearsal:** on `gip-sl8041` at the end of Task 6, run the provisioning rollback and
    record `\du` before and after (role gone, rc 0). It is not run on the shared container
    unless the lead orders it.
  - The rollback SQL goes into `deploy/README.md` beside the provisioning step.
- [ ] **Step 1.5: compose binds to `127.0.0.1`** (the maintainer (by delegation), `to-lead.md`
  "2026-10-14 12:42:33 BST", *"R8 + host exposure"*: *"postgres (5432, superuser `gipricing`),
  redis (6379), minio (9000–9001) and keycloak (8080) all listen on 0.0.0.0 and [::] … **Project-side,
  P2/S-b adds:** compose binds every port to 127.0.0.1 (a dated deploy line), plus the
  non-default GIP_APP_DB_PASSWORD gate R8 names, with the literal never logged. Do NOT change the
  RUNNING containers' bindings now (a recreate would kill gates); that is the user's call or
  S-b's window."*).
  - **The red first:** `backend/tests/test_compose_binds.py` parses `deploy/docker-compose.yml`
    (`yaml.safe_load`; `pyyaml` is in `uv.lock` at `a3fc2e8d`, the executor confirms it is
    importable from the backend tests) and asserts every entry of every service's `ports:` is
    `127.0.0.1:<host>:<container>`, one parametrised case per entry. Red on the base for each of
    the five: `postgres` `"5432:5432"` (`:16`), `redis` `"6379:6379"` (`:27`), `minio`
    `"9000:9000"` and `"9001:9001"` (`:42`), `keycloak` `"8080:8080"` (`:68`). A future service
    published without the bind fails the same test.
  - **The change:** each entry becomes `"127.0.0.1:<port>:<port>"`. `deploy/README.md` gets a
    dated line saying so and that a host outside the machine reaches none of them.
  - **The check on a running stack:** Task 6's separate project prints `docker port` for each
    service, and every line shows `127.0.0.1` (no `0.0.0.0`, no `[::]`).
  - **The shared stack is not recreated by this plan.** Applying the new binds to the running
    shared containers (`gi-pricing-postgres-1` and its siblings) needs a recreate, which would
    kill running gates: it is a GO-time act that the maintainer names, with its window, never
    a step an executor takes on its own. Until then the shared stack keeps its `0.0.0.0` binds,
    and the non-default password (Step 1.3) is its gate. The `LG-` records which was done.
  - *(Dated 2026-10-14, on the maintainer's (by delegation) entry "2026-10-14 14:59:13 BST —
    Host exposure CLOSED": the user's read-only GCP check shows 5432, 6379, 9000, 9001 and 8080
    *"reachable only from inside the VPC (10.128.0.0/9)"*, and *"S-b's Step 1.5 (compose binds
    every port to 127.0.0.1, red first) STAYS as defence in depth … together with the
    non-default GIP_APP_DB_PASSWORD gate (R8)"*. No running container is recreated.)*

#### Task 2: the two DSNs (DP-16 (a))

- [ ] **Step 2.1:** `config.py`: `database_url`'s default becomes
  `postgresql+asyncpg://gip_app_login:gip_app_login@localhost:5432/gipricing`; add
  `migration_database_url: SecretStr | None = None` with the same scheme validator (`:189-200`).
  `migrations/env.py:31` reads `migration_database_url` and raises a `RuntimeError` naming
  `GIP_MIGRATION_DATABASE_URL` when it is `None`. It never falls back to the application DSN.
- [ ] **Step 2.2:** Apply the census: CI `python.yml` (`:296` becomes
  `GIP_MIGRATION_DATABASE_URL`; `:304-305` gain the login DSN and keep the owner one where the
  census says so; a step runs `scripts/provision-app-role.py` after the service starts),
  `scripts/demo.py`, each `scripts/` consumer, `dev-commands` "Migrations" (`SKILL.md:932-949`),
  `fastapi-service`'s DSN post-mortem, and `.claude/skills/README.md`, all in the same commit.

#### Task 3: the fixtures, and the red run (DP-18 (a), DP-20 (a))

- [ ] **Step 3.1: the default flips** (*amended, plan review R1, 2026-10-14*: the first cut kept
  `test_database_url()` as the owner, and 37 test files build their own connection from it,
  `api_settings` → `api_client` among them, so their application paths would never have run as
  the login role). In `conftest_db.py`:
  - `test_database_url()` **returns the application DSN**: the same per-worktree database with
    the login role's credentials, password from `GIP_APP_DB_PASSWORD` (default
    `gip_app_login`; Step 1.3); `GIP_TEST_APP_DATABASE_URL` overrides it.
  - A new `test_owner_database_url()` returns the owner DSN, overridden by
    `GIP_TEST_DATABASE_URL`, whose meaning (the owner, as CI sets it,
    `.github/workflows/python.yml:304-305`) is unchanged. The docstring states the asymmetry.
  - Every caller of `test_database_url()` therefore moves to the login role **with no edit**:
    the `SecretStr(test_database_url())` forms (`api_settings` at `conftest.py:52` included),
    the `Database(Settings(database_url=test_database_url()))` forms and the environment forms
    (the review's grouping: 20, 14 and 3, over the 37 files of E6's count). **The only
    exception is one explicit, listed owner-only fixture** (the maintainer (by delegation),
    `to-lead.md` "2026-10-14 12:42:33 BST": *"S-b must route EVERY test DB connection (including
    api_settings → api_client) through the login role, with an explicit, LISTED owner-only
    fixture used only by migration/provisioning tests. Otherwise S-b either reds the suite or
    certifies nothing."*). It is enforced by construction, not by review: `owner_database` reads
    `request.node.nodeid` and **fails the test** unless the node is in `OWNER_FIXTURE_USERS`, a
    closed tuple in `conftest_db.py` of `(node id, label, reason)`. `test_owner_database_url()`
    is called only inside `conftest_db.py` (by that fixture and the infrastructure below), and a
    test asserts that `git grep -n 'test_owner_database_url(' -- backend/tests` hits only that
    file. The labels:
    - **`migration`, `provisioning`**: the migration round-trip and provisioning tests, the
      ruling's named class (`test_provision_app_role.py`'s database cases among them).
    - **`DP-22`**: tests of the five caller-less paths (12:42:33: *"Tests that exercise them use
      the listed owner-only fixture (R1), labelled"*).
    - **`owner-subject`**: only tests that **prove the owner is refused or that tamper**: S-a's
      owner `UPDATE`/`DELETE`/`TRUNCATE` reds, DP-21's state reds, the DP-1 `GRANT … SET LOCAL
      ROLE gip_app` test, R-b1b and the trigger-tamper tests. **ACCEPTED** by the maintainer (by
      delegation), "2026-10-14 13:21:41 BST", P2 (1): *"the "owner-subject" label: ACCEPTED,
      with EACH user listed in OWNER_FIXTURE_USERS (node ids), and only tests that PROVE the
      owner is refused or that tamper."* Each parametrised case is listed by its full node id.
    - **`bootstrap`**: the WF-699 journey test's call of the seed's `grant_demo_principals`
      (`test_wf699_journey.py:227`, `:518`), the one step 13:21:41 P2 (2) puts on the owner
      connection (*"workspace, built-in roles, memberships: what no public route creates"*).
  - `conftest_db.py`'s own internals (per-worktree database creation, the migration it runs,
    `empty_the_database`, which W7 needs as a superuser) call `test_owner_database_url()`.
  - The `database` fixture uses the application DSN; a new `owner_database` fixture uses the
    owner's.
  - Record in the `LG-` every entry of `OWNER_FIXTURE_USERS` with its label and reason, its
    count, and the predicate `git grep -nE 'test_owner_database_url\(|owner_database\b' -- backend/tests`
    verbatim with its output (acceptance 8).
- [ ] **Step 3.2: the red run.** In a gate slot, with Task 2 and 3.1 in place and **no grant
  migration yet**, run the backend suite once. Expect `tenant_marker` first: the lifespan's
  `require_tenant_binding` reads it (`main.py:100`; `platform/tenancy.py:52`) and it has no
  grant, so every API and worker start is refused until Task 5 (plan review R11). Classify
  **every** failure into exactly one class (*the classes, plan review R1, 2026-10-14*), grouped
  by table and statement, with the failing test's node id:
  1. `permission denied for table <t>` / `… for sequence <s>` **in application code** → a
     refused path, one grant (Task 5), checked against the census (Task 5.1). A `permission
     denied for table approval_requests` raised inside `approval_guard` on another table's
     `UPDATE` is this class: the trigger runs as the invoker and reads `approval_requests`
     (`a9f3c6d21b87:69-74`), so the grant is `SELECT` on `approval_requests` (plan review R11).
  2. The same message **in a test's own setup** (DDL, `GRANT`, a seed the application never
     does) → if the test fits a label of `OWNER_FIXTURE_USERS`, it is listed there; otherwise
     it is reported to the lead, never moved to the owner on the executor's judgement.
  3. `must be owner of …` → as class 2.
  4. `<table> is append-only` or a guard message → a write path S-a's E4 missed: reported to
     the lead before any fix (S-a Step 6.2's rule).
  5. `password authentication failed for user "gip_app_login"` or `role … does not exist` →
     provisioning is not applied on this database (Step 1.3); stop and fix the environment,
     never re-route the test.
  6. After Task 4 lands (the re-run of Step 5.3): the least-privilege startup refusal (its
     message names `scripts/provision-app-role.py`) → a connection built from the owner DSN that
     Step 3.1 missed; it moves to the application DSN, or, under a label, to the listed fixture.
  7. Anything else → reported to the lead, unclassified.

  The whole list, with its class per line, goes into the `LG-`.

#### Task 4: the startup refusal and the tamper-resistance reds (DP-19 (a), DP-14 (b))

- [ ] **Step 4.1:** Create `backend/tests/test_application_role.py` with the reds, first:
  - **R-b1** `test_the_application_does_not_connect_as_an_owner_or_a_superuser`: through the
    `database` fixture, **P-own returns no row** (the imported constant; *amended, plan review
    R4, 2026-10-14: was `rolsuper` on `current_user` and `pg_has_role(current_user,
    c.relowner, 'USAGE')`*). Red on the base: `current_user` is `gipricing`, and P-own returns
    `gipricing`, a superuser and the owner.
  - **R-b1b** `test_an_inherit_false_membership_of_the_owner_is_refused` (plan review R4): through
    `owner_database`, in a transaction that rolls back, `CREATE ROLE gip_scratch_r4 NOLOGIN`,
    `GRANT <the owner role> TO gip_scratch_r4 WITH INHERIT FALSE`, `SET LOCAL ROLE
    gip_scratch_r4`, then P-own returns the owner role and `assert_least_privilege()` on that
    connection raises. A second case grants a non-owner role that has `rolbypassrls` instead,
    and is refused the same way. Shown red first against the first cut's `USAGE` predicate in
    a scratch edit (it passes the `INHERIT FALSE` role), and that line goes into the `LG-`.
  - **R-b2** `test_the_api_refuses_to_start_as_the_owner`: `create_app` with an owner DSN
    raises at startup with the message naming `scripts/provision-app-role.py`; the same for
    the worker entrypoint. Red on the base: both start.
  - **R-b5** `test_the_application_role_cannot_disable_a_trigger`: through `database`,
    `ALTER TABLE factors DISABLE TRIGGER factors_no_modify` is refused with `must be owner of
    table factors`; and `SET session_replication_role = replica` is refused with `permission
    denied`. Red on the base: as the owner, both succeed (run in a transaction that rolls
    back). **This is the dependency the maintainer asked the FD to state, shown as a test.**
  - **R-b6** `test_the_application_role_is_not_superuser_not_owner_and_cannot_bypass_triggers`
    (the maintainer's 12:18:57 item (2), "NEW"): through `database`, `SELECT rolsuper,
    rolbypassrls FROM pg_roles WHERE rolname = current_user` is `(false, false)`; P-own returns
    no row (the same constant as R-b1, plan review R4); and
    `SET session_replication_role = replica` raises `permission denied to set parameter
    "session_replication_role"` (the wording is printed by the red before the green relies on
    it). **Red on `main`:** as `gipricing` the first query returns `(true, true)`, the owner check
    finds every table, and the `SET` succeeds (inside a transaction that rolls back).
  - **DP-14 (b)** `test_a_tampered_artifact_trigger_refuses_startup`, parametrised over the four
    routes (*plan review R5, 2026-10-14*: the first cut tested only `DISABLE`): through
    `owner_database`, in a transaction that rolls back, on one declared table, (i) `ALTER TABLE
    … DISABLE TRIGGER <name>` (`tgenabled = 'D'`); (ii) `ALTER TABLE … ENABLE REPLICA TRIGGER
    <name>` (`'R'`, silent in every normal session); (iii) `DROP TRIGGER <name>`; (iv) `CREATE
    OR REPLACE FUNCTION` of that trigger's function with a body that only `RETURN NEW`s. Each
    time, `Database.assert_least_privilege()` on that connection raises, naming the table and
    the trigger. Red first against the first cut's `tgenabled = 'D'` check in a scratch edit:
    (ii), (iii) and (iv) pass it, and those three lines go into the `LG-`.
- [ ] **Step 4.2:** Implement `Database.assert_least_privilege()` in `app/db/session.py`, from
  `backend/src/app/db/immutability.py`, which holds `_declared` (moved from the test so the
  application and the test share it), **P-own** and the pinned hashes. It refuses when:
  1. **P-own** returns a row (plan review R4, 2026-10-14). This one query covers superuser,
     `BYPASSRLS` and ownership, of relations, public functions, the `public` schema and the
     database (plan review R11), through any membership, `INHERIT` or not.
  2. `SET session_replication_role = replica` succeeds (attempted inside a `SAVEPOINT` and
     rolled back; success is a refusal to start).
  3. **The trigger check** (DP-14 (b) as amended, plan review R5): for every table in
     `_declared("append_only")` and `_declared("guarded")`, the expected trigger names, which are
     `<t>_no_modify` and `<t>_no_truncate` for `append_only` and every name in `guards` plus
     `<t>_no_truncate` for `guarded`, each **exist** in `pg_trigger` on that relation with
     `tgenabled IN ('O','A')`. **The function-body hash: adopted.** For each such trigger, the
     function it calls (`pg_trigger.tgfoid` → `pg_proc`) has `md5(prosrc)` equal to the value
     pinned for that function name in `immutability.py` (`PINNED_GUARD_FUNCTION_MD5`). The
     reason: a `CREATE OR REPLACE` with a no-op body keeps every trigger present and enabled,
     and only the body shows it. The cost is that a migration that changes a guard function
     must update the pin in the same commit; `test_the_pinned_guard_function_hashes_match_the_head`
     fails until it does, which is the wanted tripwire. Values are read from the head database
     at Task 4, never typed. These are owner actions, so the check stays detective, as `06`
     FR-372 frames it.

  **Where it is called.** The API's lifespan, beside `require_tenant_binding` (`main.py:75`,
  `:100`). The worker: **inside `_require_tenant_binding`, which runs under the plain
  `asyncio.run(...)` at import in `worker/entrypoint.py:31-44`, never in a Celery signal
  handler** (plan review R11): the comment at `:39-43` records that `Signal.send` swallows what
  a receiver raises, so a refusal there would let the worker carry on. R-b2's worker case
  imports the entrypoint with an owner DSN and asserts the import raises. Green. Commit.

#### Task 5: the grants, from the red list (DP-20 (a))

- [ ] **Step 5.1: the census diff, then one migration** (*plan review R6 and R9, 2026-10-14*).
  - **The diff, into the `LG-` first.** Set Task 3.2's class-1 list beside the census copy
    (Step 0.2), table by table and privilege by privilege. A census row with no red is a test
    gap: write a red for it first, then grant. A red with no census row is a census miss:
    record the site. **The five no-production-caller paths are not granted** (DP-22, ruled
    12:42:33): their tests use the listed owner-only fixture, labelled `DP-22`, and their census
    rows are recorded as "owner and operations only, 12:42:33". The seed-only paths follow
    Task 0's owner class for `seed.py`.
  - **The migration** `<rev>_application_role_grants.py`. Each `GRANT` line carries a comment
    naming the Task 3.2 test that needed it and its census row. Use column privileges where only
    named columns are written. Use `USAGE` on a sequence only where a red names it (`job_logs.seq`
    is an identity; the census expects none). Two implicit reads are named in their comments
    (plan review R11): `SELECT` on `approval_requests` for every table under `approval_guard`,
    which reads it as the invoker; and `SELECT` on `blobs`' `sha256` and `ref_count`, which
    `update(BlobRow)…returning(ref_count)` needs (`blobs.py:455`). `tenant_marker` gets
    `SELECT` only.
  - **Revoke the excess** (plan review R9): every privilege `gip_app` holds at the GO that
    neither a census row nor a red needs is revoked in the same migration, red first by Step
    5.2's map. At `a3fc2e8d` that is `jobs` `DELETE` and `outbox` `DELETE` (census, "migration
    grant" column: *"SIUD (DELETE unused)"*), unless the diff finds a caller, which is then
    recorded and the grant kept. (`factors` `UPDATE` is already gone in S-a.) No grant without
    a red. Downgrade revokes exactly what it granted and re-grants exactly what it revoked.
- [ ] **Step 5.2:** `test_every_table_grants_the_application_exactly_its_declared_privileges`
  in `test_application_role.py`: a written map `{table: (table privileges, {column: column
  privileges})}` over **every** public table, compared both ways against
  `information_schema.role_table_grants` and `column_privileges` for `grantee = 'gip_app'`.
  An `append_only` table must map to exactly `SELECT, INSERT` (the existing exact-grant test
  stays and agrees), and none of the 14 INSERT-only and read-only tables of the *Table
  classification* maps to `UPDATE` or `DELETE`. Red on the base for every table Task 5.1
  changes, `jobs` and `outbox` included (they hold `DELETE` there).
- [ ] **Step 5.3:** The suite again, in the gate slot: no `permission denied` remains. Commit.

#### Task 6: the compose run

- [ ] **Step 6.1:** On a **separate compose project and a fresh volume**, never the shared stack:
  `docker compose -p gip-sl8041 -f deploy/docker-compose.yml` with the ports remapped through
  an override file in the executor's worktree, each remapped port also bound to `127.0.0.1`
  (compose merges `ports:` lists, so the override replaces them, `!override`, rather than
  adding to the base's; the `docker port` read-back below is the proof). Then: `scripts/provision-app-role.py`,
  `alembic upgrade head` as the owner, the API and the worker and `beat` started with the
  application DSN (`dev-commands` "Serving the API … by hand" and "Worker and outbox relay"),
  and the demo journey (`scripts/demo.py --rows 60000`, or the same steps by hand if `demo.py`
  cannot target the second project; the census says which). Record: the journey's end state,
  `select usename, count(*) from pg_stat_activity where datname = 'gipricing' group by 1`
  (expected `gip_app_login` for every application connection), and any `permission denied` in
  the API or worker logs. Each one is a refused path the suite missed: red first, grant,
  re-run. Step 1.3's idempotence and convergence proof (the script applied twice, both rc 0)
  runs on this project before the shared container is touched, and the journey runs
  `examples/fremtpl2/seed.py` with both variables set: the application DSN for the seed and
  the owner DSN for its bootstrap only; `pg_stat_activity` during the seed shows
  `gip_app_login` for the governed steps (13:21:41 P2 (2)) (plan review R7,
  R11, 2026-10-14). Last, the provisioning rollback of Step 1.4 is rehearsed here, `\du` before
  and after (plan review R8). `docker compose -p gip-sl8041 port <service> <port>` for each of the five
  published ports prints `127.0.0.1:…` only (Step 1.5). Then `docker compose -p gip-sl8041 down -v`, on **that project only**.

#### Task 7: the spec line, review, gate

- [ ] **Step 7.1: `FR-44`**, appended:
  `*(Amended <date>, WK-1178 SL-8041, on FD 8038.)* **Layer 1 binds.** The application and the worker connect as `gip_app_login`, a member of `gip_app` that owns nothing and is not a superuser; only migrations use the owner (`GIP_MIGRATION_DATABASE_URL`). Startup refuses an owner, a superuser, or a disabled artifact trigger. Every `gip_app` grant is pinned by an exact map over every table. Until this, every grant and revoke here was inert, and the owner could disable the triggers.`
  The census decides whether `07-platform.md` also names the DSN. If it does, that clause gets
  a dated line in the same commit.
- [ ] **Step 7.2:** postgres-pro reviews the grant map and the provisioning file (evidence).
- [ ] **Step 7.3:** The full gate, both halves, in a gate slot; `audit-docs` and
  `req-coverage`. Record the rc table.

## Acceptance Standard

Each item can be checked by a fresh reviewer at the slice PR's merge tree, with the range
`origin/main...<slice branch>` named.

**SL-8017 (S-a)**

1. The `LG-` carries, at the named base tree, every red of S-a Task 1.4 (the exact-grant line,
   27 owner `DID NOT RAISE` cases, one per table and statement of the nine (plan review R10,
   2026-10-14), each guarded table's refused cases, the six row-guarded `TRUNCATE` cases and
   the guarded-triggers catalog red for them (plan review R2), the `dataset_versions` reds of
   *DP-21's guard*, the FR-53 data red among them (13:27:39), the `:439` guard), Task 2.5 and
   2.6 (W1 to W3 refused by a strict trigger), Task 3.2 (both `gip_app` blocks) and Task 4.1
   (W4 to W6 refused by the trigger), each with the cause this plan predicts.
2. `uv run pytest backend/tests/test_artifact_immutability.py -q` is green on the merge tree,
   and `git grep -nE '^APPEND_ONLY_TABLES|HAVING string_agg' -- backend/tests/test_artifact_immutability.py`
   prints nothing (the set is declared, not written and not grant-derived). Every mapped
   table's declared class and `guards` equal the *Table classification*'s row (plan review R3),
   checked by reading `models.py` against it, `dataset_versions` `guarded` (DP-21). The guard's transition set equals
   `VALID_DATASET_TRANSITIONS` exactly (the pin test, green; 13:27:39 item 2). Step 6.2's gate
   shows no refusal but a re-profiling path (13:27:39 item 4), each in the `LG-` with its node id
   and the lead's disposition; the back-filled `data_frozen_at` count is in the `LG-`.
3. `git grep -nE "UPDATE factors|factors SET|update\(RateTableVersionRow|version_row\.cells =" -- backend`
   prints nothing.
4. `uv run pytest backend/tests/test_fr240_governance.py backend/tests/test_rate_table_diff_portfolio.py backend/tests/test_rating_version_change_summary_route.py -q`
   is green, and Task 4.4's broken-input lines are in the `LG-`.
5. Exactly one new file under `backend/migrations/versions/`; `alembic heads` prints one head;
   the `LG-` carries Task 2.7 and 2.8's catalog outputs (upgrade, downgrade, upgrade).
6. `FR-44`, `FR-60` (the 15:14:52 clarification), `FR-70` and `FR-229` carry Task 5's dated
   lines, and `01` §5.1 lists `PROFILE_ALREADY_SET`, in the same PR as the migration.
6b. `uv run pytest backend/tests/test_profile_refusal.py -q` is green, its red (the raw trigger
   refusal) is in the `LG-`, and `git grep -n PROFILE_ALREADY_SET -- backend/src/app/errors.py
   backend/src/app/platform/profiles.py docs/specs/01-data-management.md` prints a hit in each
   (15:14:52 (4)(b), (c)). Step 2.8b's back-fill red and green are in the `LG-` (15:14:52 (B)).
7. The postgres-pro review is in the `LG-`; the full gate rc table is all 0; `python3
   scripts/audit-docs.py` exits 0 on the merge tree.

**SL-8041 (S-b)**

8. The `LG-` carries Task 0's census table and the census copy (Step 0.2), Task 3.2's red list
   with its class per line, **Task 5.1's census diff** (plan review R6), Task 1.3's
   before/after `\du` and grant read-backs, **the proof run's two exit codes, both 0, and the
   reset role attributes** (plan review R7), **the rollback rehearsal's `\du`** (plan review R8),
   a line that a non-default `GIP_APP_DB_PASSWORD` was set on the shared container and where it
   is held, with no value (plan review R8), and R-b1, R-b1b, R-b2, R-b5, R-b6 and the four
   trigger-tamper routes red on the base by cause, and the compose-bind red (Step 1.5). **The
   owner connections left in `backend/tests`**: `OWNER_FIXTURE_USERS` in full, **each user by its
   full node id** with its label (`migration`, `provisioning`, `DP-22`, `owner-subject`,
   `bootstrap`; 13:21:41 P2 (1)), and `git grep -nE 'test_owner_database_url\(|owner_database\b' -- backend/tests`
   with its output, in the `LG-` (plan review R1; 12:42:33). `api_settings` is not among them.
   `examples/fremtpl2/seed.py` builds an owner `Database` only for `grant_demo_principals`
   (13:21:41 P2 (2)), and Task 6's `pg_stat_activity` read-back during the seed shows
   `gip_app_login` for the governed steps.
9. `uv run pytest backend/tests/test_application_role.py backend/tests/test_artifact_immutability.py backend/tests/test_provision_app_role.py -q`
   is green on the merge tree, and every `GRANT` in the new migration has a comment naming a
   test from the red list and its census row. R-b6 asserts, through the application's own
   connection, `rolsuper` false, `rolbypassrls` false, P-own empty, and `SET
   session_replication_role` refused; `Database.assert_least_privilege()` refuses startup on
   each (the maintainer (by delegation), 12:18:57 item (2)). **P-own is defined once**:
   `git grep -n "pg_has_role" -- backend/src` prints exactly one hit, in `app/db/immutability.py`,
   with `'MEMBER'` (plan review R4). The trigger check refuses all four tamper routes, and the
   pinned-hash test is green (plan review R5). The exact grant map grants no `DELETE` on `jobs`
   or `outbox` unless the `LG-` records a caller (plan review R9).
10. `git grep -nE "gipricing:gipricing" -- backend/src` prints nothing, and
    `git grep -n "migration_database_url" -- backend/migrations/env.py` prints a hit.
11. The `LG-` carries Task 6's compose run: the journey's end state, the `pg_stat_activity`
    read-back with only `gip_app_login` for the application, and no `permission denied` left
    in the logs.
12. The full gate rc table is all 0, and `dev-commands` documents both variables.
13. Both slices land **before the 4 Nov P2 code freeze** (the maintainer (by delegation),
    10:11:47 and 12:00:14).

## Activation needs

- **SL-8017:** G2's merges on `main`; `FD-8007` and `FD 8037` minted (the `LG-`, docstrings
  and migration cite minted ids); DP-8 to DP-13 ruled (`to-lead.md` "2026-10-14 12:18:57 BST" item (2)), quoted in the `LG-`, with DP-8's switch read at the GO (Task 2.2);
  DP-21 ruled guarded (`to-lead.md` "2026-10-14 12:42:33 BST") and DP-21b ruled ("2026-10-14 13:21:41 BST", refined
  "2026-10-14 13:27:39 BST"), quoted in the `LG-`; a gate slot for Task 6.2.
- **SL-8041:** SL-8017 merged; the `SL-1455` NFR session finished; `FD 8038` minted, and it
  states that the owner can `DISABLE TRIGGER`, so S-b makes S-a tamper-resistant (authority 1
  and 2); DP-14 to DP-20 ruled (the same entry); DP-22 ruled not granted (12:42:33); the
  maintainer's GO names DP-15's target, the shared container, **and requires a
  non-default `GIP_APP_DB_PASSWORD` there, naming the file outside the repository that holds it**
  (plan review R8: 5432 is published on `0.0.0.0`); a gate slot for Tasks 3.2, 5.3 and 7.3.
- **The plan is minted on `main` before either slice's GO**: it rides plans batch P2 (the
  maintainer (by delegation), "2026-10-14 12:31:22 BST": *"P2 = PL 8016/SL 8017/SL 8041 after
  auditor-pl8016's review: OK"*), and "2026-10-14 12:16:37 BST", condition 2: *"A plan is minted
  (on main) before its slice's GO, an activation need as always."*
- Every blocking row carries its resolver (the Decision points table); none is open. Moving it to `active` is the lead's
  act at activation, not this file's (`document-ids.md` §1.6, PL row).

## Self-review

- **Every ruled remedy item has a task.** S-a: owner reds on all eleven (T1.2, T1.4); row and
  `TRUNCATE` triggers (T2.4); the set derived from the artifact family (T2.2, T2.3, DP-8);
  mutable columns allow-listed with a reason (W1, W3; DP-9, DP-11); every legitimate write
  handled (E4's table, T2.5, T2.6, T4); FD-8007's revoke and ADD (T2.4, T3); FR-70 (T5.2).
  S-b: the login role (T1); DSNs and compose (T1, T2); `current_user` not the owner, not a superuser, no `BYPASSRLS`, no `session_replication_role`
  (R-b1, R-b6, T4); grants red first (T3.2, T5); the `DISABLE TRIGGER` dependency (DP-14, R-b5); full gate
  and compose run (T6, T7.3).
- **Literals checked at `a3fc2e8d`:** the trigger function and message (`a1b2c3d4e5f6:43-52`);
  the pair form (`e1f2a3b4c5d6:51-67`); `test_artifact_immutability.py:38-52`, `:266-294`,
  `:303-343`, `:346-393`, `:396-446`; the approval-guard precedent; W1 to W7's lines;
  `DRAFT, PUBLISHED` (`reference.py:57`); `config.py:120`, `env.py:31`, `docker-compose.yml:13`,
  `df53696a2682:61-73`, `conftest_db.py:46`, `:171-200`, `:370-387`; CI `python.yml:296`,
  `:304-305`; the head `d4e81b7a2c95`. **Not checked, and named instead of supplied:** each
  table's insertable-row columns (T1.1); the parquet test's name (T2.5); PostgreSQL 16's exact
  `must be owner of table` and `permission denied to set parameter` wording, which R-b5's red
  prints before the green relies on it; whether `to_jsonb` handles every column type of the two
  guarded tables (T6.1 asks).
- **The plan review's amendments (2026-10-14), re-checked at `a3fc2e8d` by this seat:** the
  37-file count (`git grep -lE 'test_database_url\(\)' a3fc2e8d -- backend/tests | wc -l` →
  `37`); `test_database_url()` at `conftest_db.py:141-145` and its uses at `:184` and `:397`;
  `api_settings` at `conftest.py:52`; the worker's `asyncio.run(_require_tenant_binding(...))`
  and its signal comment (`worker/entrypoint.py:31-44`); `seed.py:421`; `approval_guard`'s read
  of `approval_requests` (`a9f3c6d21b87:70`); no test `TRUNCATE`s any of the six row-guarded
  tables outside the `replica` teardown (`git grep -nE 'TRUNCATE' a3fc2e8d -- backend/tests`);
  no `pg_has_role` in `backend/src` (`git grep -n pg_has_role a3fc2e8d -- backend/src` prints
  nothing). The trigger names in the *Table classification* are the review's catalog output
  (`rv-catalog.txt`, head database at `d4e81b7a2c95`), not re-queried. **Not checked:** that
  PostgreSQL stores a pre-hashed SCRAM verifier unchanged (Step 1.2's unit test and the proof
  run show it); which table a multi-table `TRUNCATE`'s refusal names (Step 1.2 prints it).
- **DP-21's guard, its sites read at `a3fc2e8d` by this seat:** each write site by
  `git show a3fc2e8d:<file> | grep -nE 'version\.(tables|source_fingerprint|derived_from|library_versions|ingestion_run_id|totals) *='`
  (`data/ingestion.py:213`, `:214`, `:224`, `:227`, `:253`, `:254`, `:462`), and the same for
  `datasets.py` (`:582`, `:644`, `:715`, `:740`, `:910`), `worker/data_handlers.py:358` and
  `platform/profiles.py:58`; `VALID_DATASET_TRANSITIONS` at
  `packages/model-schema/src/model_schema/datasets.py:86-96`; `_transition`'s check
  `datasets.py:568-574`; `conclude_failed_validation` `:674-716`. The seed's bootstrap
  `examples/fremtpl2/seed.py:318-381` (`grant_demo_principals(database, workspace_id)`), its
  call `:427` and its other callers `backend/tests/test_wf699_journey.py:227`, `:518`. The compose `ports:` lines
  `deploy/docker-compose.yml:16`, `:27`, `:42`, `:68`. **Not checked:** whether `new_version`
  leaves `library_versions` and `derived_from` null for an ingested version (not material: they freeze
  at the first validation either way); whether any test re-profiles a frozen version (Step 6.2
  shows it). **Read for 13:27:39:** `store_report` `validation.py:77-118`, its caller
  `data_handlers.py:283-296`, `ValidationReportRow` `models.py:1031-1079`; `01` FR-60 `:161`,
  FR-61 to FR-67 `:162-167`, the profile route `:867` and journey step 5 `:1113`.
- **The 15:14:52 ruling, its sites read at `a3fc2e8d` by this seat:** `store_profile`'s lookup
  `platform/profiles.py:36-43`, `ProfileRow` `:45`, the comment `:55-57`, the re-point `:58`;
  `DATA_ERROR_CODES` `errors.py:83-112` with `DATASET_VERSION_IMMUTABLE` at `:86`; `01` §5.1's
  list `:931-937` (at `origin/main`). **Not checked:** whether the profiling Job ever profiles a
  version after its first validation began (Step 6.2 shows it).
