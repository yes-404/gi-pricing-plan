---
id: RS-1864
family: research
kind: audit
title: SL-1260 (WK-674 Slice 6, date-based routing and shadow scoring) slice audit against PL-1537 R6.1 to R6.3 and RL-1834, at c55410d6
status: draft
created: 2026-10-22   # drafted 2026-10-22 under working id 8180; minted 2026-10-23 as RS-1864
owner: auditor
tree: c0d01474490b326aba32be97bc843f66e825dead
phase: P2
work: WK-674
corrected_by: []
relates: [SL-1260, LG-8139, PL-1537, PL-1237, RL-1834, RL-1301, RL-8176]
---

# RS-1864 — SL-1260 slice audit

*Minted 2026-10-23 as RS-1864 from working id 8180, in the SL-1260 audit-records docs PR. Prose below that calls this record or another id "unminted" or names a working id describes the draft state at filing, not the tree at the mint.*

*(Working id 8180, reserved by the lead. Written by `aud-1260`, 2026-10-22, from `brief-aud-1260-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. The ledger is cited as `LG-8139`, its working id, and `RL 8176` is an unminted draft. Verdicts below are proposals; the lead adopts, amends or rejects them.)*

## Question

Does `origin/main...sl-1260-wk674-s6` meet the acceptance standard of `PL-1537` R6.1 to R6.3 and `RL-1834` (D1, D2, "Acceptance"), and what does `LG-8139` fail to evidence?

## Method

Range `origin/main` (`71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5`)`...sl-1260-wk674-s6` (`c55410d6f9866e1d8549385b29eab8b25e2e75d2`, tree `c0d01474490b326aba32be97bc843f66e825dead`), 30 files, +3117 −12 (`git diff --stat origin/main...c55410d6`). Read by `git show c55410d6:<path>` only. Scope was derived first from `RL-1834` (its Acceptance list and "What it obliges"), `PL-1537` R6.1 to R6.3 and `03` FR-270, FR-271, FR-272, NFR-498; evidence was then looked for. Logs: `~/gi-pricing-plan.local/scratch/sl1260-db/` (00 to 14). **I ran no test, no DB window and no gate**; every red/green line below is read from a log and each log's first line was read for its tree.

Ledger SHAs: all twelve SHAs checked (`5f406245`, `2720bcce`, `c53d75f0`, `1f119659`, `9b154031`, `9cfddde9`, `0093de4b`, `bfe16607`, `2592edc2`, `3d175af3`, `6aa350c7`, `899e957e`) exit 0 under `git merge-base --is-ancestor <sha> c55410d6`.

## Scope against evidence

| # | Item (source) | Evidence found | Proposed verdict |
|---|---|---|---|
| 1 | FR-270 dated clarification, verbatim (`RL-1834` D1 (a)) | `03` line 205 carries it; the ruling's text is a verbatim substring (checked by script). | delivered |
| 2 | `03` §4.13, §5.1 routing row and shadow row body (RL-1834 "What it obliges") | `03` lines 1041 to 1063, 1112, 1113 present, with the refusal order and the two flags. | delivered |
| 3 | `model-schema` shapes `RoutingRange`, `RoutingRuleUpdate`, `RoutedRange`, `RoutingRule`, `ShadowConfigUpdate`, `ShadowConfig`; contracts regenerated | `packages/model-schema/src/model_schema/routing.py` (+88) and four generated schemas, `generated.json` +492. Contract regeneration is checked by the gate (`generate-contracts.py --check`), not by me. | delivered; regeneration check owed to the gate |
| 4 | Three tables, append-only, SELECT/INSERT only; one migration (D1 item 1, D2 items 3 and 5) | Migration `9b3e7c15d4a2` (below, item 11). `test_artifact_immutability.py` +19, `test_migration_routing_shadow.py` 7 passed at both windows (logs 06, 14). | delivered |
| 5 | Routing write: route, `deployment:promote` with the Environment as resource, refusal order, `DEPLOY_DATE_RANGE_OVERLAP`, Audit Event in the same transaction (D1 items 2 to 4) | `routing.write_rule` calls `_authorised_environment` (`platform/deployments.py:131` permission, then retired check), then reference type, range order, deployment pins, overlap, then `session.add`, `flush`, `audit.record` in the one unit of work (`api/deployments.py` opens it). `errors.py` +2. 11 tests in `test_routing_write.py` incl. overlap, unknown env, no-permission and `..._cannot_commit_without_its_audit_event`; green at log 11 (155 passed with two other files). | delivered; see broken-input gap, item 8 |
| 6 | Selection in `/score`: flag, pin check, `_serving_ref` unedited (D1 item 5, (b), (c)) | `_routed` is entered only for a default-live quote with an Environment and the per-request flag true; `routing.select_range` re-checks that the pinned `deployment_id` is a Deployment of this Environment for that ref (`routing.py:216-223`). Diff of `api/score.py` has no hunk in `_serving_ref`. 7 tests in `test_routing.py`; green at log 12 (36 passed). | delivered |
| 7 | Shadow write and shadow scoring after the response; results never returned; no quote input stored (D2 items 3 to 6) | `shadow.write_config` (permission `admin:manage_settings`, retired, type, draft/missing 422, no bundle `BUNDLE_COMPILE_FAILED`, audit); `_shadow_task` returns a Starlette `BackgroundTask` or `None`; `shadow_results` rows hold `live_result` and `candidate_result` only. 9 and 8 tests; green at logs 11 and 12. | delivered |
| 8 | Acceptance: each violation shown red first on deliberately broken input (RL-1834 "Acceptance") | See "Red/green" below. Shown red: unpromoted version selected (N-T6), flag-off (RED 1), shadow result reaching the caller (N-T8). **Not shown red:** overlap stored, Audit Event missing, draft or uncompiled candidate stored. | **delivered but untested** for those three (a broken-implementation run is owed) |
| 9 | R6.1 flags Environment-only, default off, workspace write refused (`RL-1311:275`) | `settings.py` +25; `test_settings.py` +50 (`..._environment_only_and_off_by_default`, `..._workspace_level_write_of_either_flag_is_refused`, `..._environment_write_enables_the_flag_in_that_environment_only`); green at logs 12 and 14. | delivered |
| 10 | R6.2 audit action names fixed: `deployment.routing_changed`, `deployment.shadow_configured` | `routing._ACTION` and the shadow equivalent are used by `audit.record`; the tests above assert the events. For a flag, `setting.updated` serves as the event (D2 item 1). | delivered |
| 11 | Migration `9b3e7c15d4a2` | `down_revision = "a4d1f08c3b97"`; `git grep` over `backend/migrations` at the head finds no other file naming either id as `down_revision`, so it is the single head (the window's own `alembic heads` = `9b3e7c15d4a2 (head)`, logs 00 and 10); `downgrade()` drops the three indexes and tables in reverse order (their triggers go with the tables); upgrade REVOKEs UPDATE/DELETE and GRANTs `SELECT, INSERT`. | delivered; the downgrade is **not exercised by any logged run** (reassign to the gate's migration round trip, if it has one) |
| 12 | R6.3 nothing waits on it; NFR for flag-read latency | Not measured here; `RL-1834` leaves the p99 to the gate item `PL-1237:1010-1011`. | deferred with owner: the code gate, on Slice 4's harness |
| 13 | `06` FR-343 order rule (`RL 8176` (A), the maintainer's adoption of 2026-10-22 17:21:38 BST) | Not this slice's: the rule is `RL 8176`'s own change to `06`. The slice's behaviour (load the Environment, then check the permission, 404 before 403) is the order that ruling accepts. | reassigned: `RL 8176`'s mint carries the `06` edit |

## Red/green (LG-8139 against the logs)

Every first line of 01 to 08 and 10 to 14 names the tree the ledger names (`9cfddde9`, `bfe16607`, `7b9f2684` plus "scratch edit, uncommitted" for 07 and 08, `6aa350c7`).

| Run | Ledger quotes | Log summary line, read | Match |
|---|---|---|---|
| RED 1 (`9cfddde9`) | `2 failed, 5 passed, 1 warning in 10.49s` | same; FAILED: `..._range_inside_its_dates_selects...`, `..._flag_off_scoring_is_unchanged_and_the_selector_is_not_ente...` | yes |
| RED 2 (`bfe16607`) | `4 failed, 4 passed ... in 9.45s` | same; four FAILED named as the ledger names them | yes |
| window 1 GREEN a, b, c, migration | `1 failed, 154 passed`; `36 passed`; `2 failed, 77 passed`; `7 passed` | same four lines | yes |
| N-T6 | `2 failed, 5 passed ... in 8.07s` | same; the two named tests failed | yes |
| N-T8 | `2 failed, 6 passed ... in 8.90s` | same; the two named tests failed | yes |
| window 2 a, b, c, migration (`6aa350c7`) | `155 passed`; `36 passed`; `79 passed`; `7 passed` | same four lines | yes |

- **Vacuous passes are disclosed by name** in `LG-8139` for both red runs: RED 1's one pass (`..._promoted_only_to_another_environment_is_never_selected`) and RED 2's four passes (flag off, no configuration, draw at the fraction, explicit ref).
- **Negative controls land on the claimed lines.** `routing.py:223` at the head is `if pinned is None:`; `score.py:615` is the `content=` argument of the final `Response(`. N-T6 fails the two tests that hold the pin check; N-T8 fails the two that hold "the candidate is never in the response".
- **Disclosure that matters most.** `LG-8139` states that no test of T5 to T9 was run at its test commit, so RED exists only for `test_routing.py` and `test_shadow_scoring.py`. `test_routing_write.py` and `test_shadow_write.py` have **no red run at all**, and the overlap, audit-atomicity and draft/uncompiled-candidate checks have no negative control. `LG-8139` says these runs are owed; no log shows them done.

## The window-1 failures and their fix (`3d175af3`, test-only)

`git show --stat 3d175af3`: `test_api_authorisation_sweep.py` 2 lines, `test_deployment_route_types.py` 8, `test_shadow_write.py` 5; no `src/` file. Checked:

- **Sweep pin.** At the head, `platform/shadow.py` line 66 is `env = await environments._load(session, environment)` and **line 67** is `await rbac.require_permission(`, so the pin at :67 is right. `LG-8139` writes "line 65 is `env = ...`" and "`platform/shadow.py:65-67`" for the load-first observation; both are one line low at the head (66 and 66-67). Prose only, no test depends on it.
- **Route counts 10 and 12.** The routing and shadow `PUT` rows are in `03` §5.1 (lines 1112, 1113), and the diff adds exactly those two routes; the counts moved by 2. Green at log 13.
- **404 slug.** The one-character slug `x` was refused at request validation (422); the test change keeps the intent (unknown Environment is 404). Green at log 11.
- **Guard order (`RL 8176` (A) accepts load-first).** `shadow.write_config` and `routing._authorised_environment` both load the Environment first and check the permission second, as `deploy` already does. Consistent with the adopted ruling; the unminted draft `draft/rl-8176` @`aab1b741` is the source and is not yet in `main`.

## Security reading (item 5 of the brief)

- **Permission and scope.** Routing: `deployment:promote`; shadow: `admin:manage_settings`; both with `ResourceRef(ScopeType.ENVIRONMENT, env.id)`. Both are inside the handler, after the Environment load, before any write, and `count_management` runs only after the permission passes (a 403 is never counted, `RL-1687` (1a)).
- **Audit.** `audit.record` is called on the same session, after `flush`, with `before` the previous rule (or `None`) and `after` the new one, actor the Principal. The atomicity test (`..._cannot_commit_without_its_audit_event`) injects a raising audit write.
- **The candidate is never in the response.** The response is built from the live `result` (`Response(content=result.model_dump_json(), ..., background=shadow)`); the candidate is scored in the background task and only its `shadow_results` row is written. The task carries the quote only in memory; `shadow_results` stores no `QuoteContext` (NFR-499), and failures are logged through `safe_job_exc_info`. Evidence: N-T8 and `test_a_shadow_result_holds_no_quote_input`.
- **Flag off.** Routing: `_routed` returns `None` before `select_range`; shadow: `_shadow_task` returns `None` before any configuration read. `_serving_ref` is untouched. **Observation:** with both flags off a default-live quote now runs two `settings.resolve` reads (routing in `_routed`, shadow in `_shadow_task`) that did not exist before. The response is unchanged (`RL-1834` (c) asks for byte equality, not zero reads); the latency of those reads is the gate's measurement (item 12).
- **A routing flag read is not guarded by a try.** `_routed` lets a settings-read error propagate (a 500), while `_shadow_task` swallows its own. The ruling does not specify; no test covers a failing flag read. Not a defect against the spec; named so the lead can decide whether it is a finding.

## Disclosures in LG-8139 (item 7)

All present in the ledger, none hidden: the chain that did not halt on a nonzero run (window 1 header, "06 ran after 05 failed"); `PUBSUB NUMSUB` not quoted (window 2 (a)); two `cd` slips (window 2 (b) "a second breach ... the first was at the start of the seat"). The first `cd` is only referred to, not described, in the ledger. Each is a charter breach by the executor, not a defect of the product.

## Merged-head note (item 4)

`LG-8139` last paragraph: **"Merged-head tests: owed to the code gate at the head the lead names (the full suite, ruff, mypy and import-linter at the merge of `origin/main` 71e481fa, head `899e957ec99df16022933ae1a1fd808a054986d1` when written); no further DB window is run before it (the lead, 2026-10-22)."** The line exists and `899e957e` is an ancestor of `c55410d6`. The window-2 GREEN is at `6aa350c7`, before the merge of `71e481fa` (which brought objectives and error sinks), so **nothing in this record is evidence at the merged head**. The code gate is the proof, as the lead ruled; its "Test Files N passed" and pytest summary lines are what the MERGE-ACK must quote.

## Findings

1. **Not shown red on broken input (blocking for the RL-1834 acceptance list, three items):** (a) overlapping ranges stored; (b) a routing or shadow change committing without its Audit Event (the test exists and injects a raising audit write, but it was never run against an implementation without the transactional guard); (c) a draft or uncompiled candidate stored. `RL-1834` requires each "shown red first on deliberately broken input"; `CLAUDE.md` §13 says enforcement is proven on broken input. Proposed verdict: **delivered but untested** for these three; the cheapest closure is one DB window with three scratch edits (drop the overlap check; move `audit.record` out of the transaction or skip it; drop the draft/bundle check), each reverted, the failing test names quoted. Alternative: the lead rules them accepted with the tests-pass-only evidence, in a dated line.
2. **No red-first for `test_routing_write.py` and `test_shadow_write.py` at all** (disclosed by the ledger). Same remedy as 1; same verdict.
3. **Migration downgrade is not exercised by any logged run.** Proposed verdict: **reassigned** to the code gate if it runs a downgrade round trip, otherwise **deferred with owner** the executor, for a one-off `alembic downgrade -1` / `upgrade head` in the next window.
4. **Merged-head tests owed** to the code gate (disclosed; not evidence here).
5. **Ledger prose slips, non-blocking:** shadow.py line numbers one low (above); `status: active`, `MERGE-ACK: not yet given`, and no Audit section are all still open (the closing acts of `LG-8139` and the `SL-1260` row are the auditor's after a clean audit, `auditor.md`; this record is the audit text to place there).
6. **Observation, not a finding:** two extra flag reads per default-live quote with both flags off (latency: gate item `PL-1237:1010-1011`); `_routed`'s flag read is not exception-guarded.

## Verdict proposals (the lead's to adopt, amend or reject)

**NOT-CLEAN, one blocking limb: findings 1 and 2** (broken-input proofs for overlap, audit atomicity and draft/uncompiled candidate, and the missing red-first runs of the two write-route test files). Everything else in scope is delivered with evidence; findings 3 and 4 are owed to the gate and do not block the audit if the lead assigns them. If the lead accepts finding 1 and 2 by a dated line (or they are run in a DB window and logged), this audit becomes **CLEAN** subject to the code gate at the merged head. No product defect is found, so no `FD-` is proposed.

## Next step

The lead rules on findings 1 to 3. If a DB window is granted, one re-audit of exactly the three scratch-edit runs, at the tree named in their logs, closes the limb.
