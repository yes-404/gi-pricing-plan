---
id: LG-8139
family: ledger
title: WK-674 slice SL-1260 — Slice 6, date-based routing and shadow scoring (PL-1537 R6.1 to R6.3) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: 44c18e11
phase: P2
work: WK-674
slice: SL-1260
plans: [PL-1537]
corrected_by: []
relates: [PL-1537, PL-1237, PL-1620, SL-1260, SL-1259, RL-1311, RL-1232]
---

# LG-8139 — WK-674 slice SL-1260: Slice 6

Filed 2026-10-21 under working id 8139 (lead-reserved in eta.md 15:04:27). Executor seat `exec-1260`, base `origin/main` 44c18e11, branch `sl-1260-wk674-s6`.

**GO:** the maintainer's (by delegation) entry "2026-10-21 15:03:33 BST — Maintainer: GOs on the 15:02:44 work queue", item 5. **MERGE-ACK:** not yet given.

## Scope

No leaf plan (`PL-1620` :26): the scope is `PL-1237` Task 6 as changed by `PL-1537` R6.1 to R6.3 (the SL-1260 row of `PL-1537`; write-set its S6 row). Cut-ladder rung 5, lowest priority: it takes a gate only when no row-2 slice waits.

## Needs census (on main 44c18e11)

- `SL-1259`: roadmap row `status: closed`.

## Tasks

Task rows are appended here as each task starts. The order follows `RL-1834`'s "What it obliges"
and its Acceptance list. Resume under `RL-1834` by exec-1260c, 2026-10-22 (the maintainer's
(by delegation) entry "2026-10-22 11:44:34 BST", SL-1260 RESUME GO).

| Task | What | State |
|---|---|---|
| T2 | `03` FR-270 clarification, §4.13, §5.1 routing row | done, `5f406245` |
| T3 | `model-schema` routing and shadow shapes, generated schemas | done, `2720bcce` |
| T4 | `routing_rules`, `shadow_configs`, `shadow_results`: models, migration `9b3e7c15d4a2`, immutability seed rows, `DEPLOY_DATE_RANGE_OVERLAP`, the two Environment-only flags | written unrun in `c53d75f0`; reviewed 2026-10-22 (below) |
| T5 | routing write: `platform/routing.py`, `PUT .../routing`, tests first | tests `1f119659`, code `9b154031`; unrun |
| T6 | selection in `/score` (flag, pin check, flag-off unchanged), `test_routing.py` | tests then code (`routing.select`, `_routed` in `api/score.py`; `_serving_ref` untouched); unrun |
| T7 | `PUT .../shadow` route, `deployment.shadow_configured`, tests | tests then code (`platform/shadow.py`); unrun; OpenAPI regeneration owed |
| T8 | shadow scoring after the response, `shadow_results` writes, tests | tests then code (`_shadow_task` in `api/score.py`); unrun |
| T9 | settings tests (R6.1), migration test; then contracts and INDEX regeneration, ruff format, the gate | tests written, unrun; regeneration and checks owed after the SL-1711 END |

**WIP review of `c53d75f0`, 2026-10-22.** Right: the three tables, columns, `ck_`/`fk_` names
(they match the model's naming convention), the indexes, the `artifact_append_only()` trigger
pair and the `SELECT, INSERT`-only grants follow `c4a81f6d2e95`'s `deployments` exactly; the
revision chains onto `a4d1f08c3b97`, the one head; the two flags are Environment-scoped with
`SAFE_DEFAULT` False (RL-1834 D2 item 1); `DEPLOY_DATE_RANGE_OVERLAP` is registered once; the
immutability seed rows satisfy each table's one foreign key. Missing or unverified, none run:
the migration has not been applied; `ruff format` has not been run on the new files;
`test_migration_deployments.py`'s pattern (grants, triggers, downgrade) has no counterpart for
the three tables; `test_settings.py` has no test of the two flags (R6.1, RL-1311:275).

## PRs

None yet. The slice stops at PR-READY; the lead opens the PR.

## Disclosure — the new tests' RED was never shown (2026-10-22)

The tests of T5 to T9 were written and committed before the code they cover (`1f119659`, `9cfddde9`,
`0093de4b`, `bfe16607`, `2592edc2`), but none was run at its test commit: the database lane was closed
(the SL-1711 compose retry, then SL-1275's code gate). So no test's failing state before its code, and no
"red first on deliberately broken input" the RL-1834 acceptance list asks for, has been observed. Each
test is also still unrun against its code. The red-first runs and the green runs are owed in the DB window.

## DB window 1, 2026-10-22 (ENDed 17:10:55 BST) — red, green and negative-control lines

Own database `gipricing_sl-1260_028cded7`, redis db 12, `scripts/run-small.sh`, logs under
`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1260-db/` (each starts with the tree and
`git diff --stat`). Setup `00-setup.log`: `createdb` rc 0, `alembic upgrade head` rc 0 (first
application of `9b3e7c15d4a2`), `alembic heads` = `9b3e7c15d4a2 (head)`. The window's chain did not
halt on a nonzero run; 06 ran after 05 failed (the executor's error, noted by the lead).

| Run | Tree | Log | rc | Summary line, verbatim |
|---|---|---|---|---|
| RED 1: `test_routing.py` | `9cfddde9` | `01-red-t6-9cfddde9.log` | 1 | `2 failed, 5 passed, 1 warning in 10.49s` |
| RED 2: `test_shadow_scoring.py` | `bfe16607` | `02-red-t8-bfe16607.log` | 1 | `4 failed, 4 passed, 1 warning in 9.45s` |
| GREEN a | `7b9f2684` | `03-green-a.log` | 1 | `1 failed, 154 passed, 5 warnings in 22.69s` |
| GREEN b | `7b9f2684` | `04-green-b.log` | 0 | `36 passed, 1 warning in 16.76s` |
| GREEN c | `7b9f2684` | `05-green-c.log` | 1 | `2 failed, 77 passed, 3 warnings in 74.89s (0:01:14)` |
| GREEN migration | `7b9f2684` | `06-green-migration.log` | 0 | `7 passed, 11 warnings in 18.57s` |
| N-T6 (scratch edit) | `7b9f2684` | `07-nt6-skip-pin-check.log` | 1 | `2 failed, 5 passed, 1 warning in 8.07s` |
| N-T8 (scratch edit) | `7b9f2684` | `08-nt8-candidate-in-response.log` | 1 | `2 failed, 6 passed, 1 warning in 8.90s` |

**Vacuous passes at the test commits, by name.** RED 1: `test_a_version_promoted_only_to_another_environment_is_never_selected`
passed (nothing is routed before the feature, so nothing unpromoted is selected). The two RED 1
failures were `test_a_range_inside_its_dates_selects_its_promoted_version` and
`test_with_the_flag_off_scoring_is_unchanged_and_the_selector_is_not_entered`. RED 2: the four
passes were the flag-off, no-configuration, draw-at-the-fraction and explicit-ref cases, which hold
with no feature; the four failures were `test_a_sampled_quote_is_also_scored_by_the_candidate_and_both_results_are_recorded`
(it holds the "candidate never in the response" assert), `test_a_shadow_result_holds_no_quote_input`,
`test_a_failure_of_the_candidate_never_reaches_the_caller` and
`test_the_response_is_the_same_with_and_without_shadow_scoring`.

**Negative controls** (the maintainer's "a vacuous pass proves nothing"; scratch edits, never
committed, reverted with `git checkout -- <file>`, `git status --short` empty after each).
N-T6: `backend/src/app/platform/routing.py:223` `if pinned is None:` became `if False:`;
`test_a_version_promoted_only_to_another_environment_is_never_selected` and
`test_a_pin_naming_a_deployment_of_a_different_version_is_ignored` failed. N-T8:
`backend/src/app/api/score.py:615` built the response from the live result with
`rating_version_ref` replaced by the shadow candidate's (`shadow.args[-1]`);
`test_a_sampled_quote_is_also_scored_by_the_candidate_and_both_results_are_recorded` and
`test_the_response_is_the_same_with_and_without_shadow_scoring` failed.

**The three stale pins in GREEN a and c, all test-side** (production code unchanged):
`test_shadow_write.py::test_an_unknown_environment_is_404` sent the one-character slug
`rating_version:x@1`, refused at request validation (422) before the handler's 404;
`test_api_authorisation_sweep.py::test_the_handler_guarded_routes_still_check_at_their_site` pinned
`platform/shadow.py` line 66 and the guard sits at line 67 (`await rbac.require_permission(`; line 65 is
`env = await environments._load(session, environment)`); the routing write's row cites
`platform/deployments.py:131` (`await rbac.require_permission(`, after `:130` `env = await
environments._load(session, slug, lock=lock)`), which is correct;
`test_deployment_route_types.py::test_the_route_set_is_pinned` held 8 rows and a union of 10, and
Slice 6 adds `PUT /api/v1/environments/{env}/routing` (`docs/specs/03-rating-engine.md:1112`) and
`PUT /api/v1/environments/{env}/shadow` (`:1113`), both already in section 5.1, so the counts
became 10 and 12. Fix commit `3d175af3774a260e382a4548d0fa24f5178d79b3` (tests only).

**Observation, not fixed (FD candidate for the lead).** 404 before 403: `deploy`, `rollback`, the
deployment-request submit (`platform/deployments.py:130-131` via `_authorised_environment`), the
routing write (same) and the shadow write (`platform/shadow.py:66-67`) load the Environment before
checking the permission, so an unauthorised caller can tell whether an Environment exists. The
settings write (`api/environment_settings.py`, `ManageSettings` dependency) and Environment retire
and update check the permission first (403 before 404).

## DB window 2, 2026-10-22 (ENDed 17:20:28 BST) — GREEN at the fix head

Tree `6aa350c7ce7f764b745ae5db3a36f8834d10eb17` (the fix `3d175af3` plus the ledger commit), clean;
own database `gipricing_sl-1260_028cded7`, redis db 12, beside FD-1838's gate under the maintainer's
exception, `GIP_GATE_SLOT` unset. `scratch/sl1260-db/window2.sh` halts on the first nonzero rc.
Setup `10-w2-setup.log`: `createdb` rc 0, `alembic upgrade head` rc 0, `alembic heads` = `9b3e7c15d4a2 (head)`.
Each log's header carries `date -Is` start and end (UTC) and `PUBSUB CHANNELS 'gip:switch*'`.

| Run | Log | rc | Summary line, verbatim | Start, end (UTC) | Channels at start |
|---|---|---|---|---|---|
| a: `test_routing_write.py`, `test_shadow_write.py`, `test_artifact_immutability.py` | `11-w2-green-a.log` | 0 | `155 passed, 4 warnings in 21.80s` | 16:13:06, 16:13:36 | none |
| b: `test_routing.py`, `test_shadow_scoring.py`, `test_settings.py` | `12-w2-green-b.log` | 0 | `36 passed, 1 warning in 16.37s` | 16:13:36, 16:14:00 | `gip:switch:local:local:dev` |
| c: `test_api_authorisation_sweep.py`, `test_deployment_route_types.py`, `test_score.py` | `13-w2-green-c.log` | 0 | `79 passed, 3 warnings in 71.34s (0:01:11)` | 16:14:00, 16:15:22 | `gip:switch:local:local:dev` |
| migration: `test_migration_routing_shadow.py` | `14-w2-green-migration.log` | 0 | `7 passed, 11 warnings in 20.67s` | 16:15:22, 16:20:21 | `gip:switch:local:local:prod` |

Each run has 0 failed, 0 errors and 0 skipped (`grep -c -i "skipped\|error"` is 0 in each log). The
channels listed are unsuffixed subscribers that were not this window's; no run failed, so no overlap
reading was needed. Cleanup: `FLUSHDB` on db 12 gives `DBSIZE` 0, db 0 is 56, `dropdb` rc 0, the
`pg_database` count for the window's database is 0 and no `gip_scratch_*` database is left.
The negative controls of window 1 stand: the lines they edited are unchanged by `3d175af3`.

**Disclosures for window 2.** (a) `PUBSUB NUMSUB` was not quoted alongside the channel listing, only
`PUBSUB CHANNELS`; harmless here because every run passed. (b) The executor typed `cd /tmp` in a
no-op command during the window, a second breach of the no-`cd` rule (the first was at the start of
the seat); the harness reset the working directory and no repository state changed.


**Merged-head tests:** owed to the code gate at the head the lead names (the full suite, ruff, mypy and import-linter at the merge of `origin/main` 71e481fa, head `899e957ec99df16022933ae1a1fd808a054986d1` when written); no further DB window is run before it (the lead, 2026-10-22).

## Negative controls (RS 8180 B1/B2) and the migration round trip, 2026-10-22 (window 3)

Tree `c55410d6f9866e1d8549385b29eab8b25e2e75d2` at every run's start (each log opens with
`git rev-parse HEAD` and `git diff --stat`, which shows the mutation). Own database
`gipricing_sl-1260_nv3`, redis db 12, beside FD-1838's gate (gate-1b still held) under the
maintainer's exception; `GIP_GATE_SLOT` unset; one test file per run via `run-small.sh`;
`scratch/sl1260-db/window3.sh`. RL-1834's Acceptance, "shown red first on deliberately broken
input", for the three violations RS 8180 B1/B2 found unrun. Every mutation is a scratch edit,
reverted with `git checkout -- <file>`, never committed; `git status --short` was empty after each.

| Control | Mutation (file:line at the tree above) | Log | rc | Summary line, verbatim | Failing by name |
|---|---|---|---|---|---|
| V1 overlapping ranges stored | `platform/routing.py:97` `if _overlaps(a, b):` became `if False and _overlaps(a, b):` | `21-nv1-overlap.log` | 1 | `3 failed, 11 passed, 1 warning in 7.25s` | `test_routing_write.py::test_overlapping_ranges_are_refused_and_nothing_is_written` [straddles-the-end], [inside], [open-ended] |
| V2 change commits without its Audit Event | `platform/routing.py:131` the `audit.record(...)` call wrapped in `try/except Exception: pass` | `22-nv2-audit-swallowed.log` | 1 | `1 failed, 13 passed, 1 warning in 7.15s` | `test_routing_write.py::test_a_routing_change_cannot_commit_without_its_audit_event` (`assert failed.status_code == 500`) |
| V3 draft or uncompiled candidate stored | `platform/shadow.py:88` `or candidate.status == "draft"` removed, and `:98` `if not content_hash:` became `if False and not content_hash:` | `23-nv3-draft-uncompiled.log` | 1 | `2 failed, 10 passed, 4 warnings in 5.40s` | `test_shadow_write.py::test_a_draft_candidate_is_refused` (got 200), `test_an_uncompiled_candidate_is_refused` (got 500) |

Start/end (UTC): V1 16:31:04 to 16:31:20; V2 16:31:24 to 16:31:38; V3 16:31:38 to 16:31:51.
load1 at start 4.96, 4.66, 4.40. Each log lists the unsuffixed and `gate-1b` `gip:switch*`
channels and `PUBSUB NUMSUB` for the three unsuffixed ones, none of which this window created.

Two readings. (1) V2 is not "skip the audit write": the test replaces `audit.record` with a
raiser, so removing the call would leave it green. The mutation that commits the violation is
swallowing the audit failure, which is what the test then catches. (2) For V3's uncompiled limb
the run returned 500, not a stored row: the database CHECK `ck_shadow_configs_bundle_hash_format`
refused the insert. The test fails by name all the same (it expects 409), and the database
constraint is a second line behind the application check.

**Migration round trip** (`20-migration-roundtrip.log`, same database, 16:30:51 to 16:30:59 UTC).
Before: `routing_rules`, `shadow_configs`, `shadow_results` present, `alembic_version` = `9b3e7c15d4a2`.
`alembic downgrade -1` rc 0 (`9b3e7c15d4a2 -> a4d1f08c3b97`); `alembic current` and `alembic_version`
= `a4d1f08c3b97`, the three tables absent from `information_schema.tables` (`alembic heads` still
prints the script head `9b3e7c15d4a2`, as it reads the scripts). `alembic upgrade head` rc 0, `alembic current`
= `9b3e7c15d4a2 (head)`, the three tables present again.

**Observation, not fixed: `_routed` is not exception-guarded.** `_shadow_task` wraps its flag
read and its decision in `try/except Exception` that logs and returns `None` (`api/score.py:275-290`,
`:276` the `settings_service.resolve` call). `_routed` reads its flag at `api/score.py:365` with no
guard, and its caller does not guard it either (`api/score.py:579`, `routed = await _routed(...)`).
An exception from the flag read or from `routing_service.select_range` therefore propagates and fails the live
quote. Routing is a pricing decision, so failing closed is defensible, but the asymmetry with the
shadow path is undeclared. Raised for the lead.

Cleanup: `dropdb` rc 0; `pg_database` count for the window's database 0; redis db 12 `FLUSHDB`, `DBSIZE` 0
(it held 1 key at V2's start, from a test run); db 0 was 59 at setup and 62 at the end,
not 56: it carries other sessions' keys and this window wrote none to it.
