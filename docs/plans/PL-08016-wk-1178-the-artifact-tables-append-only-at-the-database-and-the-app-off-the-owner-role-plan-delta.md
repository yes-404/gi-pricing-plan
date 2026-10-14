---
id: PL-8016
family: plan
kind: map
title: WK-1178 — the artifact tables append-only at the database (SL-8017) and the application off the owner role (SL-8041) — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — draft while DP-8 to DP-11 (SL-8017) and DP-15 to DP-20 (SL-8041) are open
created: 2026-10-14
owner: planner
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-8037, FD-8038, FD-8007, RL-8001, SL-8017, SL-8041, SL-1274, SL-1455, FR-43, FR-44, FR-70, FR-88, FR-96, FR-229, FR-240, FR-370, RL-1615]
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

## Goal

**S-a (SL-8017).** Every artifact table carries both of `FR-44`'s layers. That is `factors`
and the ten tables FD-8037 names (`rate_tables`, `rate_table_versions`, `rate_table_cells`,
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
   `FD-8037` (O-1) and `FD-8038` (the root cause) are being filed by the auditor on
   `fd-8036-failed-auth-audit-2026-10-14`, not pushed when this plan was written; they are
   cited by working id. FR-70 rides S-a (authority 1).

## Evidence, re-read at `a3fc2e8d` (not copied from the findings)

**E1 — the run (auditor-fr44).** `~/.claude/jobs/b6860f8f/tmp/fr44/out4.txt`, header line
`DB=gipricing_fr44_55d9c6a2 tree=8eaf6d5f9cd4204e1e077b44069d4afd395f1461`, alembic head
`d4e81b7a2c95`, query file `q.sql` in the same directory. Its catalog (`out4.txt:14-75`)
gives, for each of the ten tables and for `factors`, the owner `gipricing`, row trigger `-`
and truncate trigger `-`. `gip_app` holds `upd`/`del`/`ins` = `f`/`f`/`f` on the ten and
`t`/`f`/`t` on `factors`. The owner probes (`:95-473`) print `UPDATE n` and `DELETE n` on every
table probed. `TRUNCATE TABLE` succeeds except `regression_suites` (`:384-385`, *"Table
"regression_suite_versions" references "regression_suites""*) and `rating_versions` (`:420-421`,
outside this plan). **`reference_tables` has no probe section in `out4.txt`.** Its catalog row
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
entrance (FR-408)"), so it consumes both roles.

**E7 — the alembic head** at `a3fc2e8d` is `d4e81b7a2c95`: one head across 56 revisions. The
predicate: `git grep -hE '^(revision|down_revision)\b' a3fc2e8d -- backend/migrations/versions`,
then collect every quoted hex token of six or more characters, in either quote style, and
keep the revisions that no `down_revision` names.

## Slices

| Slice | Scope | Requirements | Depends on | Order and lane |
|---|---|---|---|---|
| **S-a = SL-8017** — the triggers | One Alembic migration. The `artifact_append_only()` pair goes on the nine append-only tables (`factors`, `rate_table_cells`, `rate_table_versions`, `rating_algorithms`, `reference_rows`, `reference_tables`, `regression_suite_versions`, `regression_suites`, `sub_graph_versions`). A column guard plus the `TRUNCATE` trigger go on `rate_tables` (W1) and `reference_table_versions` (W3). Layer 1 for all eleven: `factors` loses `UPDATE`; the ten get `SELECT, INSERT`, and the two guarded tables also get a column `UPDATE` on their allow-listed columns (DP-12). The append-only set is derived from a declaration on every mapped table (DP-8). W2 is removed in `rate_tables.py`. W4 to W6 are rewritten to insert. FD-8007's DP-1 `gip_app` test. `FR-44`, `FR-70` and `FR-229` dated lines. | `01` FR-43, FR-44, FR-70; `03` FR-229 and R1 (`03-rating-engine.md:41`); `06` FR-370 (the layer-1 form) | G2's merges on `main` (the maintainer's "right after the G2 merges"); `FD-8007`, `FD-8037` minted | first; lane: backend migrations. If `SL-1274` also adds a migration, DP-7 applies |
| **S-b = SL-8041** — least privilege | A login role that is a member of `gip_app`, provisioned for compose, CI and the shared container; `GIP_DATABASE_URL` is the application's DSN and a new `GIP_MIGRATION_DATABASE_URL` is the owner's, read only by `migrations/env.py` and owner-only tooling (DP-16). The test `database` fixture runs as the login role, and a new `owner_database` fixture is used for teardown, catalog checks and DDL (DP-18). The grants are found red first from that run and written as one migration, pinned by an exact grant map over every table (DP-20). A startup refusal when `current_user` owns the schema or is a superuser, in the API and the worker (DP-19). The tamper-resistance proof: the login role cannot `DISABLE TRIGGER` (DP-14). A compose run on a fresh volume. | `01` FR-43, FR-44; `06` FR-370 (*"the application role holds `INSERT` and `SELECT` only"*); NFR-458 | S-a merged (S-b's grant map includes S-a's grants); G2's merges; the `SL-1455` NFR session finished (it touches every DB path, so it must not move a measured baseline); `FD-8038` minted | second, and before the 4 Nov P2 code freeze. It runs the full gate **and** a compose run |

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
| DP-8 | (S-a) What is the append-only set **derived from**, now that grants are ruled out (authority 1 and 4)? | **(a) A declaration on every mapped table**, in the `test_approval_guard.py` form (E3): each `__table_args__` in `backend/src/app/db/models.py` carries `{"info": {"immutability": …}}`, one of `"append_only"`, `"guarded"` (with `"guard": "<trigger name>"` and `"reason"`) or `"mutable"` (with `"reason"`). The test derives the set from `Base.metadata`, **fails on any mapped table that declares nothing**, and cross-checks `pg_class` both ways (every public table but `alembic_version` is mapped). **(b) A closed written map in the test file** over every public table, with the same three classes and the same `pg_class` cross-check, and no change to `models.py`. **(c) Parse the `FR-44` list from the spec.** **(d) A structural proxy**: every table with `slug` and `version` columns, or named `*_versions`. | **(a).** It is the maintainer's "the ORM's artifact tables", and it puts the declaration where the next table's author writes the table. A new table fails until it is classified, so protection cannot be forgotten silently. The repo already derives the approval guard's set this way. Cost: 59 mapped classes edited in one hot file (`models.py`, 58 `__table_args__`); the edit is mechanical and S-a lands right after G2. **(b)** is the fallback if the GO finds `models.py` contended; it is equally closed but sits apart from the declaration. (c) couples a test to prose. (d) is a proxy that catches by name: `rate_tables` and `reference_tables` have no `version` column. | decision point | **yes** (S-a Task 2) | |
| DP-9 | (S-a, W1) `rate_tables.current_version` is updated on every new version, and it is also the version allocator (`rate_tables.py:214`, `version_number = table_row.current_version + 1`). How is `rate_tables` protected? | **(a) A column guard** `rate_tables_pointer_only()`: `DELETE` is refused; an `UPDATE` is allowed only when `NEW.current_version > OLD.current_version` and every other column except `updated_at` is unchanged, compared as `to_jsonb(NEW) - 'current_version' - 'updated_at'` against the same for `OLD`, so a column added later is guarded by default. Plus `rate_tables_no_truncate` (`artifact_append_only()`). Classified `guarded`. **(b) Remove the column**: derive the latest version as `max(version_number)` from `rate_table_versions` at each read (`:212`, `:214`, `:252`, `:262`, `diff_cache.py:97-112`), then make `rate_tables` plain append-only. **(c)** Leave `rate_tables` out. | **(a).** A pinned Rating Version names `slug@version` (`03` R1), so `current_version` is a pointer to the newest version, not a price input; moving it forward changes no approved price. (a) keeps it forward-only, so it can neither be rewound nor edited sideways. (b) changes the allocator and five readers in a G2-hot module, which is larger than S-a's "migration-only, low conflict" and is better as its own slice if wanted. (c) ignores a table the maintainer named. | decision point | **yes** (S-a Task 2) | |
| DP-10 | (S-a, W2) A parquet version's row is inserted, then `cells` is set and flushed again in the same transaction, which the database sees as an `UPDATE`. | **(a) Reorder**: in `_persist_new_version` (`rate_tables.py:1387-1481`), write the parquet blob **before** building `version_row`, and pass `cells=blob_ref.model_dump(mode="json")` to the constructor. The `rows` branch is unchanged. The row is then inserted complete and `rate_table_versions` is plain append-only. **(b)** A guard that allows `cells` to go from `NULL` to a value. | **(a).** (b) leaves a hole: a `rows`-storage version has `cells` `NULL` for ever, so (b) would let anyone attach a parquet body to an approved `rows` version. With (a), a duplicate version (`409`, `:1458-1464`) rolls back the blob's database row in the same transaction; the object store keeps the bytes, which are content-addressed and unreferenced. The executor states that consequence in the `LG-`. This is S-a's one `backend/src` change apart from `models.py`. | decision point | **yes** (S-a Task 2) | |
| DP-11 | (S-a, W3, FR-70) `publish_version` moves a reference table version `draft` → `published` in place. | **(a) A column guard** `reference_table_versions_publish_only()`: `DELETE` is refused; an `UPDATE` is allowed only when `OLD.status = 'draft' AND NEW.status = 'published'` and every other column is unchanged (`to_jsonb(NEW) - 'status'` against `OLD`'s). Plus the `TRUNCATE` trigger. Classified `guarded`. **(b) An append-only publication record** (a new table) with the status derived from it. | **(a).** It is the narrowest guard that keeps FR-70's "independently approvable" behaviour, and it is the `models_fit_immutable` and `blobs_content_immutable` precedent: one named transition, everything else frozen. (b) is a schema and service change outside "migration-only". | decision point | **yes** (S-a Task 2) | |
| DP-12 | (S-a) Layer 1 for the ten: `gip_app` holds **nothing** on them today (E1). Its grants are inert until S-b. Where do they land? | **(a) S-a**, in the same migration: `GRANT SELECT, INSERT` on all ten; `GRANT UPDATE (current_version, updated_at) ON rate_tables` and `GRANT UPDATE (status) ON reference_table_versions` (column privileges); `REVOKE UPDATE, DELETE … FROM PUBLIC` on all eleven. **(b) S-b**, inside the grant audit. | **(a).** It completes `FR-44`'s "both layers" for all eleven in one migration, it lets the existing exact-grant test (E3) pin them from S-a onwards, and it costs nothing at runtime until S-b. S-b's red run (DP-20) then confirms these grants are enough. | decision point | no (default (a)) | |
| DP-13 | (S-a, W5, W6) The test writers that shape a `rate_table_versions` row in place. | **(a)** Each test **inserts** a new version row carrying the shaped `definition` or `storage`, mirroring the seeded row's columns (`RateTableVersionRow`, `models.py:2073-2106`), and points the call under test at it. **(b)** `ALTER TABLE … DISABLE TRIGGER` around the write. | **(a)**, for the reason DP-2 (a) was ruled: a test that switches the guard off is the loophole under another name. If a test needs `rate_tables.current_version` to name the inserted version, it advances it forward, which DP-9 (a) allows. | decision point | no (default (a)) | |
| DP-14 | (S-a and S-b; FD-8038) The owner can `ALTER TABLE … DISABLE TRIGGER`, and a superuser can set `session_replication_role = replica`. How is tamper-resistance treated? | **(a)** State the dependency in FD-8038: S-a's triggers stop mistakes from every caller; they stop deliberate tampering only after S-b removes the owner's credential from the application and the worker. Residual risk: the migration credential and the superuser, which `06` FR-372's hash chain only detects. **(b)** (a), plus a **detective check** in S-b's startup refusal: no `pg_trigger` row on a declared `append_only` or `guarded` table has `tgenabled = 'D'`. **(c)** An event trigger that refuses `ALTER TABLE … DISABLE TRIGGER`. | **(b).** (a) is required (authority 1). The detective check costs one catalog query at startup and turns a silently disabled trigger into a refusal to start, which matches FR-372's "detectable rather than impossible". (c) needs a superuser to create, and the owner, a superuser today, can drop it, so it adds nothing once S-b lands and nothing before. S-b's red **R-b5** is the proof: the login role's `DISABLE TRIGGER` is refused with `must be owner of table`. | decision point | no for S-a; yes for S-b (Task 4) | |
| DP-15 | (S-b) How is the login role provisioned? | **(a) One idempotent SQL file**, `deploy/postgres/app-login-role.sql`: create `gip_app` `NOLOGIN` if absent (the migration tolerates it, `df53696a2682:66-73`), create the login role `NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS INHERIT` if absent, `GRANT gip_app TO` it. It is applied by compose's `/docker-entrypoint-initdb.d` mount on a fresh volume, by a new `scripts/provision-app-role.py` (asyncpg, owner DSN; the host has no `psql`, `dev-commands`) in CI, in `scripts/demo.py` and once on the shared container, and the password comes from `GIP_APP_DB_PASSWORD` (local default only, as compose's `gipricing` is). **(b)** A migration creates the login role. **(c)** The application keeps the owner's DSN and runs `SET ROLE gip_app` on each connection checkout. | **(a).** It is what `df53696a2682:61-63` already says deployment does. (b) puts a credential in a migration, which that migration's comment forbids. (c) leaves the owner's credential in the application, so `RESET ROLE` undoes it, and S-a stays switch-off-able by the application. Applying the file to the shared `gi-pricing-postgres-1` adds one cluster-wide role; the GO names it. | decision point | **yes** (S-b Task 1) | |
| DP-16 | (S-b) Which variable carries which role? `migrations/env.py:31` reads the same `database_url` as the application (E5). | **(a)** `GIP_DATABASE_URL` / `Settings.database_url` is the **application's** login role; a new `Settings.migration_database_url: SecretStr \| None` (`GIP_MIGRATION_DATABASE_URL`) is the owner's; `env.py` reads only the new one and **fails loudly** when it is unset. Defaults: `config.py:120` becomes the compose login role on `gipricing`, which also retires `dev-commands`' "the bare command does not work" trap for the application. **(b)** `GIP_DATABASE_URL` stays the owner (migrations unchanged) and a new `GIP_APP_DATABASE_URL` is the application's. | **(a).** Under (b) the owner's credential stays in the application's environment by default, which is FD-8038's cause. Under (a) the application process does not need the owner's credential at all. Cost: every migration command changes its variable (`dev-commands`, CI `python.yml:296`, `conftest_db.py:133-135`, the gate scripts); the census (S-b Task 0) lists each. | decision point | **yes** (S-b Task 2) | |
| DP-17 | (S-b) The login role's name. | **(a)** A separate login role `gip_app_login`, member of `gip_app`, so `current_user` is `gip_app_login` and the grants stay on `gip_app` where every migration writes them. **(b)** `ALTER ROLE gip_app LOGIN`. | **(a)**, per `df53696a2682:61-63` ("creates a login role and grants it membership"). It also keeps the grant tests (`grantee = 'gip_app'`) unchanged. | decision point | no (default (a)) | |
| DP-18 | (S-b) How do the tests connect? | **(a)** The `database` fixture (`conftest_db.py:171-200`) connects as the login role on the same per-worktree database; a new `owner_database` fixture connects as the owner, for teardown (W7 needs a superuser), catalog queries, `GRANT`/DDL inside a test (DP-1's) and the owner-connection tests in `test_artifact_immutability.py`. Each test that needs the owner names it. `GIP_TEST_APP_DATABASE_URL` overrides, as `GIP_TEST_DATABASE_URL` does. **(b)** Tests stay on the owner, and a small set of smoke tests runs as `gip_app`. | **(a).** Only (a) runs every application path the suite covers as the role production uses, which is what "red-first per refused path" needs (DP-20). (b) leaves every unexercised path unverified, and that is how FD-8038 lasted. | decision point | **yes** (S-b Task 3) | |
| DP-19 | (S-b) Where does the startup refusal apply? | **(a)** Every environment, `local` included: `Database.assert_least_privilege()` (new, `app/db/session.py`) is called from the API's startup (`main.py:75`) and the worker's (`worker/entrypoint.py:32`). It raises when `current_user` is a superuser or `pg_has_role(current_user, <owner of any public table>, 'USAGE')`, plus DP-14 (b)'s disabled-trigger check. The message names `scripts/provision-app-role.py`. **(b)** Refuse in `dev`, `uat` and `prod` only (the `require_startable` form, `config.py:204`), and warn in `local`. | **(a).** A local exemption is the path by which the owner connection survived; compose provisions the role (DP-15), so `local` can satisfy it. A process that uses `Database` without starting the API or the worker (the `scripts/bench-*` tools, E6) is classified by the census and gets the application DSN or the owner DSN explicitly. | decision point | **yes** (S-b Task 4) | |
| DP-20 | (S-b) How are the grants audited red-first? | **(a)** Run the backend suite once (the gate slot) with DP-18 (a) in place and **before** the grant migration. Every `permission denied for table <t>` / `for sequence <s>` failure is a refused path. Each becomes one grant line, cited to the failing test, in one migration. An exact map test, `test_every_table_grants_the_application_exactly_its_declared_privileges`, pins `gip_app`'s table and column privileges for every public table against a written map, which is red on any drift either way. The postgres-pro agent reviews the map, as evidence only. **(b)** Grant `SELECT, INSERT, UPDATE, DELETE` on every table that is not `append_only` or `guarded`, then trim. | **(a).** (b) grants first and audits later, which is the "decorative layer" the requirement forbids. Under (a), every grant has a failing test as its reason, and a table that no test writes gets no write grant. A path the suite does not exercise and the compose run (Task 6) finds is added the same way, red first. | decision point | **yes** (S-b Task 5) | |

## Write set

**S-a (SL-8017)**

| File | Change | Task |
|---|---|---|
| `backend/src/app/db/models.py` | `{"info": {"immutability": …}}` on every mapped table (DP-8 (a)) | 2 |
| `backend/migrations/versions/<rev>_artifact_tables_append_only.py` | **create**: one migration (triggers, two guard functions, grants, revokes) | 2 |
| `backend/src/app/platform/rate_tables.py` | `_persist_new_version`: blob before row (DP-10) | 2 |
| `backend/tests/test_artifact_immutability.py` | the declaration-derived tests (replacing the grants-derived one), the eleven rows, the guard tests, DP-1's `gip_app` test | 1, 2, 3 |
| `backend/tests/test_fr240_governance.py`, `test_model_jobs.py`, `test_model_jobs_gbm.py` | W4 (DP-2, DP-3) | 4 |
| `backend/tests/test_rate_table_diff_portfolio.py`, `test_rating_version_change_summary_route.py` | W5, W6 (DP-13) | 4 |
| `docs/specs/01-data-management.md` (`FR-44` `:106`, `FR-70` `:177`), `docs/specs/03-rating-engine.md` (`FR-229` `:122`) | dated lines (DP-5) | 5 |
| `docs/ledgers/LG-<id>.md`, `docs/roadmap.md` (SL-8017's status line) | the slice's paperwork (Lean P2 L1) | all |

**S-b (SL-8041)**

| File | Change | Task |
|---|---|---|
| `deploy/postgres/app-login-role.sql` (**create**), `deploy/docker-compose.yml` (initdb mount, `:9-21`), `deploy/README.md` | DP-15 | 1 |
| `scripts/provision-app-role.py` (**create**), `scripts/demo.py` | DP-15, DP-16 | 1, 2 |
| `backend/src/app/config.py` (`:120`; new `migration_database_url`), `backend/migrations/env.py` (`:31`) | DP-16 | 2 |
| `backend/src/app/db/session.py`, `backend/src/app/main.py`, `backend/src/app/worker/entrypoint.py` | DP-19, DP-14 (b) | 4 |
| `backend/tests/conftest.py`, `backend/tests/conftest_db.py`, and each test the red run moves to `owner_database` | DP-18 | 3 |
| `backend/migrations/versions/<rev>_application_role_grants.py` (**create**), `backend/tests/test_application_role.py` (**create**) | DP-20, R-b1 to R-b5 | 3, 4, 5 |
| `.github/workflows/python.yml` (`:290-306`), the `scripts/` consumers the census lists | DP-16 | 2 |
| `.claude/skills/dev-commands/SKILL.md` ("Migrations", `:932-949`), `.claude/skills/fastapi-service/SKILL.md` (the DSN post-mortem), `.claude/skills/README.md` | the new variables, same commit (`CLAUDE.md` §12) | 2 |
| `docs/specs/01-data-management.md` (`FR-44`), `docs/specs/07-platform.md` (wherever the census finds the DSN specified) | dated lines (DP-5) | 7 |
| `docs/ledgers/LG-<id>.md`, `docs/roadmap.md` (SL-8041's status line) | paperwork | all |

**Not in either write set:** `packages/**`, `docs/contracts/**`, the frontend.

## S-a (SL-8017) — tasks

### Task 1: the reds by cause, on the base tree (tests only)

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
- [ ] **Step 1.2:** Split the owner-connection test (`:346-393`) by class. The nine append-only
  tables keep the three statements and `"append-only" in str(refused.value)`. The `TRUNCATE`
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
  The guard's message is asserted verbatim from Task 2's functions.
- [ ] **Step 1.3:** Add the eleven to `APPEND_ONLY_TABLES` **only as a temporary red**, so the
  exact-grant test shows layer 1's state: `factors: ['INSERT', 'SELECT', 'UPDATE']` and, for
  each of the ten, `<t>: []`. Task 2 replaces the constant.
- [ ] **Step 1.4:** Run on the base, one file: `uv run pytest backend/tests/test_artifact_immutability.py -q`.
  Expected, **each by its cause**:
  - the exact-grant test fails at the first of the eleven, by its grant set (above);
  - the owner test fails `DID NOT RAISE` on the `UPDATE` for each of the nine;
  - the guarded test fails `DID NOT RAISE` on the first refused statement for both;
  - the grants-derived test (`:396-446`) fails at its guard `:439`, with the eleven only on
    the right-hand side.
  A failure for any other reason is a plan defect: stop and report. Paste the lines into the
  `LG-` with the tree. **This is the first owner-write observation on `reference_tables`**
  (E1 has none). Commit (test only).

### Task 2: the declaration, the migration, and W1 to W3

**Files:** `backend/src/app/db/models.py`; create `backend/migrations/versions/<rev>_artifact_tables_append_only.py`;
`backend/src/app/platform/rate_tables.py`; `backend/tests/test_artifact_immutability.py`.

- [ ] **Step 2.1:** Re-measure the head at the GO with E7's predicate (expected `d4e81b7a2c95`
  unless something merged since; DP-7). Record it.
- [ ] **Step 2.2: the declaration (DP-8 (a)).** On every mapped class, add a final dict to
  `__table_args__` (create the tuple where a class has none):
  `{"info": {"immutability": "append_only"}}`; or `{"info": {"immutability": "guarded", "guard":
  "<trigger name>", "reason": "<one line>"}}`; or `{"info": {"immutability": "mutable", "reason":
  "<one line>"}}`. Classify by the catalog **as it is**, not as it should be: the 13 of
  `APPEND_ONLY_TABLES` (`:38-52`) and the nine are `append_only`; `rate_tables` and
  `reference_table_versions` are `guarded` (Task 2.4); `custom_metrics`, `custom_objectives`,
  `models` and `peril_structures` are `guarded` by their existing narrower row triggers, each of
  which also has a `TRUNCATE` trigger (E1's catalog, `out4.txt:14-75`). `blobs` and the
  `approval_guard` tables have no `TRUNCATE` trigger, so they are `mutable`, and the reason
  names their narrower trigger (adding the `TRUNCATE` half is outside this slice and goes to
  the lead as an observation). The rest are `mutable` with the reason they are written (`jobs`,
  `outbox`, a lifecycle `status`, and so on). **A table that a spec calls
  immutable but the catalog leaves mutable is reported to the lead in the `LG-` as an
  observation, not fixed here.**
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
    """A table that declares nothing fails here on the day it is added (FD-8037)."""
    failures = []
    for table in Base.metadata.sorted_tables:
        kind = table.info.get("immutability")
        if kind not in {"append_only", "guarded", "mutable"}:
            failures.append(f"{table.name}: immutability={kind!r}")
        elif kind != "append_only" and not table.info.get("reason"):
            failures.append(f"{table.name}: {kind} without a reason")
        elif kind == "guarded" and not table.info.get("guard"):
            failures.append(f"{table.name}: guarded without a named guard trigger")
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
  `test_every_guarded_table_carries_its_named_guard_and_the_truncate_trigger`: for each
  `_declared("guarded")` table, the trigger its `guard` names exists with `tgtype & 1 = 1`, and
  at least one statement trigger exists.
  `_declared` is the one source; no tuple of table names remains in the file.
- [ ] **Step 2.4: the migration.** Generate it with the `dev-commands` DSN
  (`GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_<wt> uv run --directory <wt>/backend alembic revision -m "artifact tables append only"`)
  and replace the body. Its docstring states FD-8037 and FD-8007, why the ten had neither
  layer, why `factors` rode `models`' grant (`b2c3d4e5f6a7:89`), W1 to W3 and their treatments,
  and that **the grants are inert until SL-8041** (FD-8038).

```python
APP_ROLE = "gip_app"

#: No column changes, no row goes (`03` R1, FR-229; `01` FR-70; FD-8037, FD-8007).
APPEND_ONLY = (
    "factors", "rate_table_cells", "rate_table_versions", "rating_algorithms",
    "reference_rows", "reference_tables", "regression_suite_versions",
    "regression_suites", "sub_graph_versions",
)
#: Ten had no grant at all; `factors` had `UPDATE` beside `models` (`b2c3d4e5f6a7:89`).
NEWLY_GRANTED = tuple(t for t in APPEND_ONLY if t != "factors") + (
    "rate_tables", "reference_table_versions",
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
    for table in APPEND_ONLY + ("rate_tables", "reference_table_versions"):
        op.execute(f"""
            CREATE TRIGGER {table}_no_truncate
              BEFORE TRUNCATE ON {table}
              FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
        """)
    # Layer 1 (DP-12). Inert until SL-8041: the application connects as the owner (FD-8038).
    op.execute(f"REVOKE UPDATE, DELETE ON factors FROM {APP_ROLE}")
    for table in NEWLY_GRANTED:
        op.execute(f"GRANT SELECT, INSERT ON {table} TO {APP_ROLE}")
    op.execute(f"GRANT UPDATE (current_version, updated_at) ON rate_tables TO {APP_ROLE}")
    op.execute(f"GRANT UPDATE (status) ON reference_table_versions TO {APP_ROLE}")
    for table in APPEND_ONLY + ("rate_tables", "reference_table_versions"):
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM PUBLIC")


def downgrade() -> None:
    for table in APPEND_ONLY + ("rate_tables", "reference_table_versions"):
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
  owner test's `"append-only"` assertion holds for `TRUNCATE` on the guarded two as well. If
  DP-9 or DP-11 is ruled (b), this step changes and the plan's delta says how.
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
  eleven with their triggers and `gip_app`'s privileges.
- [ ] **Step 2.8: the downgrade (DP-6 (a)).** `downgrade -1`, the catalog, `upgrade head`, the
  catalog. All three outputs go into the `LG-`.
- [ ] **Step 2.9:** `uv run pytest backend/tests/test_artifact_immutability.py -q`: green.
  Commit.

### Task 3: FD-8007's `gip_app` test (DP-1 (a), the ADD)

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

### Task 4: the test writers (W4 to W6)

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

### Task 5: the spec lines (DP-5 (a)), in the migration's commit range

`<date>` is the commit date and `<rev>` Task 2's revision. Escape any `|` as `\|`.

- [ ] **Step 5.1: `FR-44`** (`01-data-management.md:106`), appended:
  `*(Amended <date>, WK-1178 SL-8017, on FD-8037 and FD-8007.)* **The set is declared, not derived from grants.** Eleven artifact tables were outside it: ten had no grant and no trigger, so a grants-derived set could not see them, and `factors` held `UPDATE` beside `models`. Every mapped table now declares `append_only`, `guarded` (a named narrower trigger and a reason) or `mutable` (a reason); a table that declares nothing fails a test. `<rev>` attaches both triggers to the nine new append-only tables, a forward-only guard to `rate_tables.current_version` and a `draft`-to-`published` guard to `reference_table_versions.status`. Layer 1 binds only once the application stops connecting as the owner (FD-8038, SL-8041).`
- [ ] **Step 5.2: `FR-70`** (`:177`), appended:
  `*(Amended <date>, WK-1178 SL-8017.)* Enforced in the database: `reference_table_versions` may move only `draft` to `published`, and `reference_tables` and `reference_rows` are append-only (`<rev>`).`
- [ ] **Step 5.3: `FR-229`** (`03-rating-engine.md:122`), appended:
  `*(Amended <date>, WK-1178 SL-8017, on FD-8037.)* Enforced in the database: `rate_table_versions` and `rate_table_cells` are append-only, and `rate_tables` may only move `current_version` forward (`<rev>`).`
- [ ] **Step 5.4:** `python3 scripts/audit-docs.py` as one gate-2 docs check, and
  `uv run python scripts/req-coverage.py`. Commit.

### Task 6: postgres-pro review and the gate

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

## S-b (SL-8041) — tasks

### Task 0: the census, before any edit

- [ ] **Step 0.1:** At the GO tree, run E6's predicate and
  `git grep -nE "Database\(|create_async_engine|alembic upgrade|GIP_TEST_DATABASE_URL" -- backend/src scripts deploy .github .claude/skills backend/tests/conftest*.py`.
  Classify every hit: **application** (gets `GIP_DATABASE_URL`, the login role) or **owner**
  (gets `GIP_MIGRATION_DATABASE_URL`: migrations, provisioning, test teardown and catalog
  fixtures). Put the table in the `LG-` before Task 1. An entry that fits neither is reported
  to the lead.

### Task 1: provisioning (DP-15 (a))

- [ ] **Step 1.1:** Create `deploy/postgres/app-login-role.sql`:

```sql
-- The application's login role (FD-8038; df53696a2682:61-63: "Deployment creates a login
-- role and grants it membership"). Idempotent. Never a superuser, never an owner.
DO $do$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gip_app') THEN
    CREATE ROLE gip_app NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gip_app_login') THEN
    CREATE ROLE gip_app_login LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS INHERIT;
  END IF;
END
$do$;
GRANT gip_app TO gip_app_login;
```

- [ ] **Step 1.2:** Create `scripts/provision-app-role.py`: it connects with
  `GIP_MIGRATION_DATABASE_URL` (asyncpg), executes the file, then `ALTER ROLE gip_app_login
  PASSWORD` from `GIP_APP_DB_PASSWORD`, whose default `gip_app_login` is for local use only, as
  compose's `gipricing` is (`docker-compose.yml:14`). Mount the SQL file in compose
  (`./postgres/app-login-role.sql:/docker-entrypoint-initdb.d/10-app-login-role.sql:ro`) for
  fresh volumes. A fresh volume still needs the password step: the compose run (Task 6) calls
  the script.
- [ ] **Step 1.3:** Apply the script once to the shared `gi-pricing-postgres-1`, as the GO
  names (DP-15). Read back `select rolname, rolsuper, rolcanlogin from pg_roles where rolname
  like 'gip_app%'` and `select pg_has_role('gip_app_login', 'gip_app', 'MEMBER')` into the
  `LG-`.

### Task 2: the two DSNs (DP-16 (a))

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

### Task 3: the fixtures, and the red run (DP-18 (a), DP-20 (a))

- [ ] **Step 3.1:** `conftest_db.py`: `test_database_url()` stays the owner (teardown and
  catalog); add `test_app_database_url()`, the same database with the login role's credentials
  (`GIP_TEST_APP_DATABASE_URL` overrides). The `database` fixture uses the app DSN. A new
  `owner_database` fixture uses the owner's. `empty_the_database` stays on the owner (W7 needs
  a superuser).
- [ ] **Step 3.2: the red run.** In a gate slot, with Task 2 and 3.1 in place and **no grant
  migration yet**, run the backend suite once. Record every failure whose message is
  `permission denied for table <t>`, `… for sequence <s>` or `must be owner of …`, grouped by
  table and statement, with the failing test's node id. Each group is one refused path. A
  `must be owner` failure inside a test's own setup (DDL, `GRANT`, catalog) moves that test to
  `owner_database`, with the reason in its docstring. A failure in application code is a grant
  (Task 5). The whole list goes into the `LG-`.

### Task 4: the startup refusal and the tamper-resistance reds (DP-19 (a), DP-14 (b))

- [ ] **Step 4.1:** Create `backend/tests/test_application_role.py` with the reds, first:
  - **R-b1** `test_the_application_does_not_connect_as_an_owner_or_a_superuser`: through the
    `database` fixture, `SELECT rolsuper FROM pg_roles WHERE rolname = current_user` is
    false, and no public table's owner is a role `current_user` has `USAGE` of
    (`pg_has_role(current_user, c.relowner, 'USAGE')`). Red on the base: `current_user` is
    `gipricing`, superuser and owner.
  - **R-b2** `test_the_api_refuses_to_start_as_the_owner`: `create_app` with an owner DSN
    raises at startup with the message naming `scripts/provision-app-role.py`; the same for
    the worker entrypoint. Red on the base: both start.
  - **R-b5** `test_the_application_role_cannot_disable_a_trigger`: through `database`,
    `ALTER TABLE factors DISABLE TRIGGER factors_no_modify` is refused with `must be owner of
    table factors`; and `SET session_replication_role = replica` is refused with `permission
    denied`. Red on the base: as the owner, both succeed (run in a transaction that rolls
    back). **This is the dependency the maintainer asked the FD to state, shown as a test.**
  - **DP-14 (b)** `test_a_disabled_artifact_trigger_refuses_startup`: through `owner_database`,
    in a transaction that rolls back, disable one declared trigger and call
    `Database.assert_least_privilege()` on that connection: it raises, naming the table.
- [ ] **Step 4.2:** Implement `Database.assert_least_privilege()` in `app/db/session.py` with
  the two catalog checks and DP-14 (b)'s `pg_trigger … tgenabled = 'D'` check over
  `_declared("append_only")` and `_declared("guarded")` (move `_declared` into `app/db` so the
  application and the test share it). Call it from `main.py`'s startup (`:75`) and
  `worker/entrypoint.py` (`:32`). Green. Commit.

### Task 5: the grants, from the red list (DP-20 (a))

- [ ] **Step 5.1:** One migration, `<rev>_application_role_grants.py`. Each `GRANT` line carries
  a comment naming the Task 3.2 test that needed it. Use column privileges where a red shows
  that only named columns are written. Use `USAGE` on a sequence only where a red names it.
  No grant without a red. Downgrade revokes exactly these.
- [ ] **Step 5.2:** `test_every_table_grants_the_application_exactly_its_declared_privileges`
  in `test_application_role.py`: a written map `{table: (table privileges, {column: column
  privileges})}` over **every** public table, compared both ways against
  `information_schema.role_table_grants` and `column_privileges` for `grantee = 'gip_app'`.
  An `append_only` table must map to exactly `SELECT, INSERT` (the existing exact-grant test
  stays and agrees). Red on the base for every table Task 5.1 changes.
- [ ] **Step 5.3:** The suite again, in the gate slot: no `permission denied` remains. Commit.

### Task 6: the compose run

- [ ] **Step 6.1:** On a **separate compose project and a fresh volume**, never the shared stack:
  `docker compose -p gip-sl8041 -f deploy/docker-compose.yml` with the ports remapped through
  an override file in the executor's worktree. Then: `scripts/provision-app-role.py`,
  `alembic upgrade head` as the owner, the API and the worker and `beat` started with the
  application DSN (`dev-commands` "Serving the API … by hand" and "Worker and outbox relay"),
  and the demo journey (`scripts/demo.py --rows 60000`, or the same steps by hand if `demo.py`
  cannot target the second project; the census says which). Record: the journey's end state,
  `select usename, count(*) from pg_stat_activity where datname = 'gipricing' group by 1`
  (expected `gip_app_login` for every application connection), and any `permission denied` in
  the API or worker logs. Each one is a refused path the suite missed: red first, grant,
  re-run. Then `docker compose -p gip-sl8041 down -v`, on **that project only**.

### Task 7: the spec line, review, gate

- [ ] **Step 7.1: `FR-44`**, appended:
  `*(Amended <date>, WK-1178 SL-8041, on FD-8038.)* **Layer 1 binds.** The application and the worker connect as `gip_app_login`, a member of `gip_app` that owns nothing and is not a superuser; only migrations use the owner (`GIP_MIGRATION_DATABASE_URL`). Startup refuses an owner, a superuser, or a disabled artifact trigger. Every `gip_app` grant is pinned by an exact map over every table. Until this, every grant and revoke here was inert, and the owner could disable the triggers.`
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
   nine owner `DID NOT RAISE`, both guarded `DID NOT RAISE`, the `:439` guard), Task 2.5 and
   2.6 (W1 to W3 refused by a strict trigger), Task 3.2 (both `gip_app` blocks) and Task 4.1
   (W4 to W6 refused by the trigger), each with the cause this plan predicts.
2. `uv run pytest backend/tests/test_artifact_immutability.py -q` is green on the merge tree,
   and `git grep -nE '^APPEND_ONLY_TABLES|HAVING string_agg' -- backend/tests/test_artifact_immutability.py`
   prints nothing (the set is declared, not written and not grant-derived).
3. `git grep -nE "UPDATE factors|factors SET|update\(RateTableVersionRow|version_row\.cells =" -- backend`
   prints nothing.
4. `uv run pytest backend/tests/test_fr240_governance.py backend/tests/test_rate_table_diff_portfolio.py backend/tests/test_rating_version_change_summary_route.py -q`
   is green, and Task 4.4's broken-input lines are in the `LG-`.
5. Exactly one new file under `backend/migrations/versions/`; `alembic heads` prints one head;
   the `LG-` carries Task 2.7 and 2.8's catalog outputs (upgrade, downgrade, upgrade).
6. `FR-44`, `FR-70` and `FR-229` carry Task 5's dated lines, in the same PR as the migration.
7. The postgres-pro review is in the `LG-`; the full gate rc table is all 0; `python3
   scripts/audit-docs.py` exits 0 on the merge tree.

**SL-8041 (S-b)**

8. The `LG-` carries Task 0's census, Task 3.2's red list, and R-b1, R-b2 and R-b5 red on the
   base by cause.
9. `uv run pytest backend/tests/test_application_role.py backend/tests/test_artifact_immutability.py -q`
   is green on the merge tree, and every `GRANT` in the new migration has a comment naming a
   test from the red list.
10. `git grep -nE "gipricing:gipricing" -- backend/src` prints nothing, and
    `git grep -n "migration_database_url" -- backend/migrations/env.py` prints a hit.
11. The `LG-` carries Task 6's compose run: the journey's end state, the `pg_stat_activity`
    read-back with only `gip_app_login` for the application, and no `permission denied` left
    in the logs.
12. The full gate rc table is all 0, and `dev-commands` documents both variables.
13. Both slices land **before the 4 Nov P2 code freeze** (the maintainer (by delegation),
    10:11:47 and 12:00:14).

## Activation needs

- **SL-8017:** G2's merges on `main`; `FD-8007` and `FD-8037` minted (the `LG-`, docstrings
  and migration cite minted ids); DP-8 to DP-11 resolved by a dated line, quoted in the `LG-`;
  a gate slot for Task 6.2.
- **SL-8041:** SL-8017 merged; the `SL-1455` NFR session finished; `FD-8038` minted, and it
  states that the owner can `DISABLE TRIGGER`, so S-b makes S-a tamper-resistant (authority 1
  and 2); DP-14 to DP-16 and DP-18 to DP-20 resolved; the GO names DP-15's one change to the
  shared container; a gate slot for Tasks 3.2, 5.3 and 7.3.
- This plan stays `draft` until every blocking row is resolved (`document-ids.md` §1.6, PL row).

## Self-review

- **Every ruled remedy item has a task.** S-a: owner reds on all eleven (T1.2, T1.4); row and
  `TRUNCATE` triggers (T2.4); the set derived from the artifact family (T2.2, T2.3, DP-8);
  mutable columns allow-listed with a reason (W1, W3; DP-9, DP-11); every legitimate write
  handled (E4's table, T2.5, T2.6, T4); FD-8007's revoke and ADD (T2.4, T3); FR-70 (T5.2).
  S-b: the login role (T1); DSNs and compose (T1, T2); `current_user` not the owner (R-b1,
  T4); grants red first (T3.2, T5); the `DISABLE TRIGGER` dependency (DP-14, R-b5); full gate
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
