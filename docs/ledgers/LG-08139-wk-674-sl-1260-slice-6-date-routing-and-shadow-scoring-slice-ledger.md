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

Two readings. (1) **Corrected below (V2b/V2c):** this note first said that skipping the audit write
would stay green. That was an unmeasured inference and it was wrong; see the two skip runs below.
V2 itself (swallowing a failed audit write) is the control for the same-transaction limb. (2) For V3's uncompiled limb
the run returned 500, not a stored row: the database CHECK `ck_shadow_configs_bundle_hash_format`
refused the insert. The test fails by name all the same (it expects 409), and the database
constraint is a second line behind the application check.

**The maintainer's ruling, `to-lead.md` entry "2026-10-22 17:34:47 BST", item 2, verbatim:** "**V2 is NOT sufficient.** By the lead's own report, "literally skipping the call stays green, because the test makes it raise". So **a routing change that never calls `audit.record` passes the test**, and that is exactly RL-1834's "a change committing without its Audit Event". **Required:** add an assertion that **a successful routing write (and a shadow write) produces exactly one Audit Event row**, of the expected type, in the same unit of work. Then a NEW control, "skip the `audit.record` call entirely" (routing.py:131, and the shadow equivalent), must FAIL BY NAME. Red-first on the added assertion. This is a test addition in the slice, not a weakened test."

**Measured result:** the premise was an unmeasured inference of the seat's and it was false: the existing positive tests already assert exactly one event, so no assertion was added and the new control fails by name at the head. The maintainer accepted the correction (the lead's relay, 2026-10-22: "Measurement beats inference"). **V2b/V2c, the audit call skipped entirely.** Mutation:
`await audit.record(` became `(lambda *a, **k: None)(`, one line each. The logs 24 and 25 hold `git diff --stat`
only (`routing.py | 2 +-` and `shadow.py | 2 +-`), not the diff text, so the exact edits are:

```diff
--- backend/src/app/platform/routing.py  (line 131)
-    await audit.record(
+    (lambda *a, **k: None)(
--- backend/src/app/platform/shadow.py   (line 129)
-    await audit.record(
+    (lambda *a, **k: None)(
```

The arguments that follow the call line are unchanged and still evaluated. Both fail by name with no new test, because each positive test already
unpacks `(event,) = await _events(...)`, exactly one event of the write's action with its
`entity_ref`, `before` and `after`. Reverted, `git status --short` empty, never committed.

| Control | Log | rc | Summary line, verbatim | Failing by name |
|---|---|---|---|---|
| V2b routing skip | `24-nv4-routing-audit-skipped.log` | 1 | `3 failed, 11 passed, 1 warning in 7.51s` | `test_a_rule_naming_a_deployed_version_is_written_and_audited`, `test_a_second_write_appends_and_records_the_previous_rule_as_before`, `test_a_routing_change_cannot_commit_without_its_audit_event` |
| V2c shadow skip | `25-nv5-shadow-audit-skipped.log` | 1 | `3 failed, 9 passed, 4 warnings in 5.60s` | `test_a_compiled_candidate_is_configured_and_audited`, `test_a_second_write_appends_and_records_the_first_as_before`, `test_a_shadow_change_cannot_commit_without_its_audit_event` |

**The maintainer's ruling, same entry, item 4, verbatim:** "**`_routed`'s unguarded flag read (api/score.py:365, caller :579): DECLARE it, not an FD.** Fail-closed is the right default for PRICING: a routing failure must never silently fall back to the default-live version, because that could quote from the wrong version. Shadow is best-effort by design and guarded. **SL-1260 amends its own 03 routing clause in place** (the slice's FR from T2; SL-1260 is not merged, so in place is fine): "a routing selection failure fails the quote (5xx, problem code named) and never falls back; a shadow failure never affects the response". **Plus a test pinning it** (select_range raises → the quote fails, never default-live). LG-8139 records it."

**`_routed` fails closed, declared.** Spec first: `03` §4.13
Selection gains the sentence "a routing selection failure fails the quote and never falls back" (500
`INTERNAL_ERROR`; commit before the test). Test `test_routing.py::test_a_routing_selection_failure_fails_the_quote_and_never_falls_back`
(selector healthy: 200 and the live version scored; selector raises: 500, `code` `INTERNAL_ERROR`, no
version scored). It passes on the current code, `26-b-routing-green.log` rc 0, `8 passed, 1 warning in 8.82s`. The
red control, `27-nv6-routed-falls-back.log`: `api/score.py:579` `routed = await _routed(...)` wrapped in
`try/except Exception: routed = None`, rc 1, `1 failed, 7 passed, 1 warning in 9.28s`, failing
`test_a_routing_selection_failure_fails_the_quote_and_never_falls_back` (`assert 200 == 500`). Reverted,
`git status --short` empty, never committed. `ruff check .` rc 0 and `ruff format --check` on the test file rc 0.

**`_routed` test extended (RS 8187 gaps).** `test_a_routing_selection_failure_fails_the_quote_and_never_falls_back`
is now parametrised on what raises: `select_range` and the routing flag read (`settings_service.resolve`
for `features.date_routing_enabled`), and it asserts the log names the cause: one ERROR `request failed`
record whose sanitised exception text begins `RuntimeError` (the class is the stand-in `SanitisedError`, the
text is `describe(exc)`) and whose traceback frames include the failing function. Green at the head:
`28-b2-routing-green.log` rc 0, `9 passed, 1 warning in 9.63s`. Red controls, both scratch, reverted
with `git checkout`, `git status --short` showing only the test file, never committed:

| Control | Log | rc | Summary line, verbatim | Failing by name |
|---|---|---|---|---|
| `_routed`'s flag read (`api/score.py:365`) guarded with `except Exception: return None` | `29-nv7-flag-read-falls-back.log` | 1 | `1 failed, 8 passed, 1 warning in 9.60s` | `...never_falls_back[resolve]` (`assert 200 == 500`) |
| the caller (`api/score.py:579`) re-raises `RuntimeError("masked") from None`, so status, code and "nothing scored" hold but the cause is lost | `30-nv8-cause-masked.log` | 1 | `2 failed, 7 passed, 1 warning in 10.65s` | `...never_falls_back[select_range]`, `...never_falls_back[resolve]` (`assert 'select_range' in [... frames ...]`) |

**`INTERNAL_ERROR` catalogued (the maintainer's ruling (a), relayed by the lead).** `03` §4.13's new clause is the first spec text to name
it, and `errors.py` lists it in `_GENERIC_ERROR_CODES` ("Codes raised by the shared request machinery rather than owned by one module"). No spec's
"Error codes owned by this module" block listed it; `07` §5.1 is its owner, as for `CONFLICT_STALE_WRITE`, because `FR-450` makes the
platform implement `00` §5.3's error model for every module. Its own commit (`07-platform.md` only) adds it to that list with a paragraph
from `errors.py` `unexpected_problem`: unhandled exception, 500, the fixed detail, the `trace_id`, no exception text. `audit-docs.py` after the
change: `181 error codes, ownership exclusive`, and the only FAILED line is check 31.

**Migration round trip** (`20-migration-roundtrip.log`, same database, 16:30:51 to 16:30:59 UTC).
Before: `routing_rules`, `shadow_configs`, `shadow_results` present, `alembic_version` = `9b3e7c15d4a2`.
`alembic downgrade -1` rc 0 (`9b3e7c15d4a2 -> a4d1f08c3b97`); `alembic current` and `alembic_version`
= `a4d1f08c3b97`, the three tables absent from `information_schema.tables` (`alembic heads` still
prints the script head `9b3e7c15d4a2`, as it reads the scripts). `alembic upgrade head` rc 0, `alembic current`
= `9b3e7c15d4a2 (head)`, the three tables present again.

**Deviation: the round trip ran beside the FD-1838 gate.** The lead's brief placed the round trip in this window; `RL-1626` (d) puts migrations in a no-gate gap, after the gate's END. It ran 16:30:51 to 16:30:59 UTC (17:30:51 to 17:30:59 BST) beside the FD-1838 gate (gate-1b held), on the seat's own per-worktree database `gipricing_sl-1260_nv3`; the gate's database was untouched. The maintainer's split ruling (relayed at about 17:31 BST) arrived after the run, so the run followed the brief it was given. The fault is the brief's, not the seat's. Whether it re-runs in the gap is the maintainer's to decide. After the downgrade the log quotes `alembic_version` (`a4d1f08c3b97`); after the upgrade it quotes `alembic current` only, not a `SELECT` on `alembic_version`.

**`_routed` observation (resolved above).** It was unguarded (`api/score.py:365`, caller `:579`) while `_shadow_task` is guarded (`:275-290`); the maintainer declared fail-closed for routing and best-effort for shadow, and the spec and a test now say so.

Cleanup: `dropdb` rc 0; `pg_database` count for the window's database 0; redis db 12 `FLUSHDB`, `DBSIZE` 0
(it held 1 key at V2's start, from a test run); db 0 was 59 at setup and 62 at the end,
not 56: it carries other sessions' keys and this window wrote none to it.

**Migration round trip re-run in the no-gate gap (the lead's "GATE END + A GO", FD-1838's gate ended 17:32:38Z).** Tree
`eaf045d2c2c1e95c6360256ce439416700b385dd`; own fresh database `gipricing_sl-1260_nv3`; `GIP_GATE_SLOT` unset; `lslocks` showed no
gate-1 or gate-1b holder (only a gate-2 docs flock). `30-migration-roundtrip-gap.log`, 17:33:59 to 17:34:05 UTC, load1 2.18,
`PUBSUB NUMSUB` 0 for the three unsuffixed channels. After each step, `SELECT version_num FROM alembic_version` and the
routing/shadow table check:

| Step | rc | `version_num` | Tables (`routing_rules`, `shadow_configs`, `shadow_results`) |
|---|---|---|---|
| 1 `createdb` then `alembic upgrade head` | 0 and 0 | `9b3e7c15d4a2` | all three present |
| 2 `alembic downgrade -1` (`9b3e7c15d4a2 -> a4d1f08c3b97`) | 0 | `a4d1f08c3b97` | `(none)` |
| 3 `alembic upgrade head` | 0 | `9b3e7c15d4a2` | all three present |

This clean record supersedes the beside-the-gate run above (the Deviation stands as history). Cleanup: `dropdb` rc 0, `pg_database`
count 0, redis db 12 `DBSIZE` 0, db 0 is 83 (other sessions' keys; none written here).

## Gate-red fixes (the lead's diagnosis of the SL-1260 gate, `pytest.log`: `19 failed, 6702 passed, 19 skipped, 147 warnings in 2926.38s`)

Thirteen of the 19 are the docs-audit set (check 31 on this ledger's working id). Six were guards catching the slice's own additions.
Small runs, beside SL-1551's gate, `GIP_GATE_SLOT` unset, one to two DB-free files each, logs under `scratch/sl1260-db/`, tree
`57b7fa04`-descendant `605fae23` plus the working-tree edit named in each log's `git diff --stat`:

| # | Guard | Fix (commit "test(guards)" unless noted) | Run | Result |
|---|---|---|---|---|
| 1 | `test_contracts.py::test_every_one_sided_slug_is_declared` | four `ONE_SIDED_SLUGS` entries (`routing-rule`, `routing-rule-update`, `shadow-config`, `shadow-config-update`), the Slice 5 form | `31-i1-i2-contracts-demoguide.log` | `182 passed, 2 skipped, 2 warnings, 2 errors in 10.75s`: the guard passes; the 2 errors are `test_demo_guide.py`'s DB-backed `test_the_entrance_is_absent_where_development_identity_is` and `test_the_guide_is_served_where_the_demo_runs`, a missing-database setup error, held for a DB lane |
| 2 | `test_demo_guide.py::test_the_guide_names_the_endpoints_a_spec_declares...` | asserts `{"OPT"}` instead of `{"RATE"}`, with a dated comment; OPT chosen because its whole endpoint axis (optimisation runs, demand models, GIPP checks) is a later phase, so it stays unbuilt longest | same log | passes (not among the failures) |
| 3 | `test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for` | two `_SINKS` entries for `_shadow_task` and `_shadow_score`; new `test_shadow_log_sanitised.py` (two DB-free sentinel tests, commit "test(shadow)") | `33-i3-sentinel-green.log`, `35-i3-error-sinks.log` | sentinels `2 passed, 2 warnings in 0.32s`; error sinks `9 passed, 2 warnings, 4 errors in 1.53s` (census passes; the 4 errors are DB-fixture setup errors, held) |
| 4 | `test_settings_environment.py::test_scope_defaults_to_workspace_only_and_three_keys_...` | the three-key set now selects `WORKSPACE_OR_ENVIRONMENT`; sibling `test_the_routing_and_shadow_flags_are_environment_only` asserts the two flags are the only `ENVIRONMENT` keys | not run: the file mixes DB tests | held for a DB lane |
| 5 | `test_repository_invariants.py::test_the_error_code_registry_matches_the_specs` | waiting on the maintainer's A or B | | open |
| 6 | `test_audit_docs_ids.py::test_widening_the_scope_roots_...` | 89 became 93 with a dated line citing the four schemas | `32-i6-audit-docs-ids.log` | `2 failed, 116 passed in 57.59s`; the two failures are `test_the_real_tree_passes_all_ten_checks` and `test_doc_id_check_exits_0_on_the_real_tree`, the check-31 class; the widening test passes |

**Red-first for item 3** (`34-i3-sentinel-red-raw-exc.log`): in a scratch edit of `api/score.py`, both `exc_info=safe_job_exc_info(exc)` in
`_shadow_task` and `_shadow_score` became `exc_info=exc`; rc 1, `2 failed, 2 warnings in 0.60s`, failing
`test_a_shadow_decision_failure_logs_no_quote_input` and `test_a_shadow_scoring_failure_logs_no_quote_input` by name. Reverted with
`git checkout -- backend/src/app/api/score.py`; `git status --short` showed only the test files; never committed.

`ruff check .` is clean on `backend/tests` and `tests`. `ruff format --check` reports drift in four of the edited files that this
change did not cause (lines far from the edits), so the new file was formatted and the others left as the repository has them.
