---
id: LG-1841
family: ledger
title: WK-674 slice SL-1711 — the scripted WF-701 deployment-steps demo (PL-1710) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22  # original date 2026-10-21, set at the draft; minted 2026-10-22
owner: executor
tree: 03c6397f200868f1a0827c197ffbc6de0bf65eda
phase: P2
work: WK-674
slice: SL-1711
plans: [PL-1710]
corrected_by: []
relates: [PL-1710, PL-1237, PL-1537, PL-1620, PL-1544, SL-1711, SL-1258, SL-1259]
---

# LG-1841 — WK-674 slice SL-1711: the WF-701 deployment-steps demo

Disclosure: drafted under working id 8136; minted as LG-1841 on 2026-10-22 (the maintainer's (by delegation) entry "2026-10-22 11:46:33 BST", id order (a)), in the SL-1711 slice PR.

Filed 2026-10-21 under working id 8136 (lead-reserved in eta.md). Executor seat `exec-1711`, base `origin/main` 44c18e11ca028d25c8b4c9d92077cc0f3622ef8e, branch `sl-1711-wk674-wf701-demo`.

**GO:** the maintainer's (by delegation) entry "2026-10-21 15:03:33 BST — Maintainer: GOs on the 15:02:44 work queue", item 2. The build starts now; the gate waits for D27 (RL-1712 T1 and T2 on main, activation need 5); the compose window is SOLO in a quiet window. **MERGE-ACK:** not yet given.

## Scope

Quoted from PL-1710: the Tasks table row 2 and the section "SL-1711 — the slice" (step table, Tasks 0 and T1–T7, reds R1–R9, acceptance standard items 1–8). The plan is the scope; this ledger grows per task.

## Needs census (on main 44c18e11)

- Need 1, `SL-1259` merged with D5.6 in its `LG-`: roadmap row `status: closed`; LG-1824.
- Need 2, `SL-1258`: roadmap row `status: closed`.
- Need 5: UNMET at the GO (the maintainer's entry, item 2): `grep -cF RL-1712` on the 03 FR-259 row is 0. The gate waits for D27.

## Task 0 — readiness at main 44c18e11 (static limbs; the DB/compose limbs are owed)

- **0.1 guard:** `backend/src/app/config.py:204-213` (`Settings.require_startable`, refuses `dev_auth_enabled` for `UAT`/`PROD`) and `:287` (`settings.require_startable()`) are at this tree; test `backend/tests/test_api_jobs.py:120-127` is parametrised over both. **Owed:** the pass and the broken-input red (run-small takes whole files only and `test_api_jobs.py` is DB-backed: needs the lead's DB grant).
- **0.2 compose auth:** `deploy/docker-compose.yml:13` `GIP_ENVIRONMENT: dev`; `:19` `GIP_DEV_AUTH_ENABLED: ${GIP_DEV_AUTH_ENABLED:-true}`. DP-1 is ruled (a): the journey's first line prints both facts (`FIRST_LINE`).
- **0.3 `/score` rate limit:** `scoring.default_client_rate_limit_rps` default `None` (`backend/src/app/platform/settings.py:233-241`); `ServiceAccountCreate.rate_limit_rps` default `None` (`api/service_accounts.py:65`), and the journey creates its accounts without one. No limit applies: no pacing is needed. **Owed:** re-read at the run.
- **0.4 `trace_produce` queue:** `platform/jobs.py:80` `JobKind.SCORE_TRACE_PRODUCE: JobQueue.SCORING`; the merged compose has `worker-scoring` (`--queues scoring`, `deploy/docker-compose.yml:169`) beside `worker-compute`, `worker-io` and `worker-default`; `scripts/demo.py` `demo_queues()` consumes the derived set (DP-2, PL-1714 E4.5). The `scoring` consumer exists on both run modes.
- **0.5 frame, 0.6 S5's surface, 0.7 the seed over the compose ports:** owed to the DB and compose windows. From reading: the deploy response carries `switch` (`model_schema.SwitchReport`: `processes` name -> `committed | possibly_stale | pruned_stale`, process id `<hostname>:<pid>:<start epoch>`) and the audit event `deployment.switched` (entity `environment:<slug>`) carries the same set; the journey reads the COMMIT set from `GET /audit`, not the response, and compares it with `docker compose ps -q api`.
- **Auditor principal (11:14:40 ruling):** `AUDIT_READ` is in `READ_PERMISSIONS` (`packages/model-schema/src/model_schema/permissions.py:58,87`), and `approver`, `deployer`, `auditor` and `admin` are each built from that set (`BUILTIN_ROLES`), so the demo's `admin` reads the audit by derivation, not by an accident of the seed: no `auditor` principal is added.

## Tasks

- **T1-T4 (the journey module, K1 and K2 demo data, the in-process tests).** `examples/fremtpl2/journey_wf701.py`, `examples/fremtpl2/rating/fremtpl2-wf701.k1-min-premium.json`, `...k2-decline.json`, `backend/tests/test_wf701_journey.py`. **R1 red by cause:** `run-small` on the test file with the module moved aside: `ModuleNotFoundError: No module named 'journey_wf701'` at collection; then 11 passed. **Order disclosure:** the module was written before its first test run in the same session; the pure assertions (R4, R5, R6's band, the ruled-line rules) are each tested on broken input, but a red before the code existed was shown only for R1.
- **A5 draws K = 200 real freMTPL2 policies (the maintainer's ruling "2026-10-21 15:59:05 BST", item 1, which rejected the `contract_sample` deviation).** `portfolio_policies()` in `examples/fremtpl2/journey_wf701.py` reads the seed's portfolio rows (`seed.build_csv(seed.PORTFOLIO_ROWS)`, the sha256-pinned public file, after v2's `exposure_years <= MAX_EXPOSURE` step; 19 985 rows, measured). **Draw rule: the first 200 by ascending `IDpol`; no random number.** `policy_inputs` maps each contract field that has a dataset column of its name (`seed.RENAMES` applied) to the real value and keeps the template's for a field with none (`current_premium_minor`). A real value outside its contract makes A5 fail `REAL_POLICY_OUTSIDE_CONTRACT`: a finding to report, never replaced. K is fixed (the grow-until-A6-binds loop is removed). `contract_sample` and its two tests are removed; the new tests are pure and cover the mapping, the draw order and the failure on broken input.
- **Deviation 3, executor-recorded, ACCEPTED (maintainer, to-lead "2026-10-21 16:01:49 BST" item 1): K1 = rv3 plus an added 180 floor, not the "150 -> 180" change of PL-1710 DP-4 (a).** Evidence at sl-1711 head bcae10ea: rv3 is `build_version("RV3", ...)` (`examples/fremtpl2/journey.py:1031`), seeded from `save_demo_algorithm` -> `build_fremtpl2_algorithm` (`examples/fremtpl2/model.py:820-838`); `examples/fremtpl2/algorithm.py` has no floor. The v1/v2 JSON floors (`rating/fremtpl2-rate.rating-algorithm.v1.json:395` 15000, `v2.json:457` 18000) are a fixture: `examples/fremtpl2/rating/README.md:1-6` says "measurement only until the G2 exit-demo slice adopts it". Adopting the fixture as the demo algorithm is DECLINED (a G2 adoption plus a `seed.py` change).
- **Data copy (maintainer ruling "2026-10-21 16:05:17 BST"):** the worktree's gitignored `examples/fremtpl2/data` is a COPY (`cp -rL`) of the root checkout's, not a symlink (a symlink lets tools write through to the user's checkout). Verified `test ! -L` and the file count equal to the root's. Untracked; not committed.
- **K1 and K2 are Rating Versions of the live algorithm's slug (executor-recorded reading, accepted by the maintainer, "2026-10-21 15:59:05 BST", item 2)** (`fremtpl2-rate`, next versions), because the Regression Suite and the submit gate are bound to the algorithm slug (`current_suite_for_algorithm`) and no route creates a suite for a new slug. K1's golden quotes are updated deliberately (new suite version) only where the new value is exactly the 180 floor; K2's decline range (`bonus_malus` 141 to 150) is chosen to leave the existing goldens passing, so it adds no suite version.
- **T6 (`scripts/demo.py`).** `--journey wf-701`, `--target {local,compose}`, `check_compose_up` (R9), `prepare_world` (the seed and pre-flights extracted so the compose run shares them), `run_journey` takes the journey name. `backend/tests/test_demo_command.py`: `JOURNEYS` assertion updated, 4 new tests, the two source-order tests read `_effective_demo_source()` (the flow is unchanged, its text moved). **R8/R9 red by cause:** the new tests run against the pre-change `scripts/demo.py`: 6 failed (missing `prepare_world`, `compose_services`, `wf-701`); against the change: 24 passed, 2 errors (the two DB fixtures of existing tests: no test DB without a grant).
- **WF-701's two dated lines** (11:14:40 ruling items (1) and (2)) in `docs/workflows/WF-00701-deploy-and-monitor.md`: the §1 precondition row and the C2 note.
- **Owed to the DB lane (grant needed):** `backend/tests/test_wf701_journey.py` (the end-to-end test and R6), `backend/tests/test_demo_command.py` (its 2 DB tests), `backend/tests/test_api_jobs.py` (Task 0.1). **Owed to the compose window:** T5's A2/C4/replica C6 reds and greens, R5 on the stack, R7 (decline floor removed in a scratch copy), T7 and the rehearsal.

## Journey DB run 1 — exec-1711d, sl-1711 head 0476f3c2 (tree f1fcd69d), 2026-10-21 16:35-16:40 BST

- **Window:** own DB `gipricing_sl-1711_0476f3c2` from template0; ONE `alembic upgrade head` (rc 0, under `small-test`); `alembic heads` = `alembic current` = `a4d1f08c3b97` before the test. Redis db 12, load1 5.83. Run 1 of 4 (3 unused): `run-small` on `backend/tests/test_wf701_journey.py` + `backend/tests/test_demo_command.py`, rc 1, 39 passed, 2 failed in 85 s, log `~/gi-pricing-plan.local/scratch/sl1711d-1.log`. Cleanup: dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.
- **Failures:** `test_wf701_journey_runs_end_to_end` and `test_c7_fails_naming_the_band_when_the_sample_rate_is_zero`, both at A5: `REAL_POLICY_OUTSIDE_CONTRACT`, 416 field failures. A4 had passed. A5 onwards is unexercised.
- **Cause (read-only check, no DB):** not a missing base level. `_relativities` (`packages/pricing-core/src/pricing_core/modelling/glm.py:935`) emits the base first (`is_base=True`), and `model.py:987-990` takes every level of it. The test world is hand-built: `test_wf699_journey._world` uses `test_demo_rating_evidence._fit_result()` over `test_fremtpl2_algorithm._DOMAINS` (`:199-204`): `veh_brand` B1,B2; `veh_gas` Diesel,Regular; `area` A,B; `region` R11,R24. The contract domains are those two levels per factor.
- **Count (reproduced from `portfolio_policies()`, first 200 by IDpol, against those domains):** 416 field failures over 185 of 200 policies, exactly the logged 416. `area` 150 (C 49, D 53, E 37, F 11), `region` 123 (15 levels, R82 15), `veh_brand` 143 (B12 130, B3 4, B4 3, B5 2, B11 2, B13 1, B6 1), `veh_gas` 0. Against the real book's base by exposure (B1, Regular, C, R24): 49 failures are on a base level (`area` C) and 367 on other levels. The fixture's own bases (B1, Diesel, A, R11) never fail.
- **Fix site (not applied):** the fixture domains in `backend/tests/test_fremtpl2_algorithm.py`/`test_demo_rating_evidence.py`, shared with other tests, or a world built in `test_wf701_journey.py` from a full-level fit. PL-1710 item 8 write set (`PL-1710`:448-452) names `test_wf701_journey.py`, not those files. Needs a ruling.

## PRs

(none; the lead opens the PR)

## Journey DB run 1 under option (a) — exec-1711e, sl-1711 head 3d97bcbd (tree f76925b0), 2026-10-21 20:30-20:33 BST

- **Change:** `backend/tests/test_wf701_journey.py` gains `_full_level_world()`, a context manager that patches the shared `_DOMAINS` and `_ESTIMATES` (not edited on disk) for the `_world` build only, with the dataset's own levels (the shared two levels stay first, further levels sorted, fixed estimates; no refit). A no-DB check: the patched `_fit_result()` covers all 200 first policies (0 missing; 11/2/6/22 levels for `veh_brand`/`veh_gas`/`area`/`region`), the shared dicts are restored after it. **Added runtime:** about 9 s for the portfolio read and no fit; the run took 80 s against 85 s before.
- **Window:** own DB `gipricing_sl-1711_3d97bcbd` from template0; ONE `alembic upgrade head` (rc 0, under `small-test`); `alembic heads` = `alembic current` = `a4d1f08c3b97` before the test. Redis db 12, load1 5.57, gate-1 free. Run 1 of 4 (3 unused): `run-small` on `backend/tests/test_wf701_journey.py` + `backend/tests/test_demo_command.py`, rc 1, 39 passed, 2 failed in 80 s, log `~/gi-pricing-plan.local/scratch/sl1711e-1.log`.
- **Result:** `REAL_POLICY_OUTSIDE_CONTRACT` is gone. A5 now fails one step later: `INPUT_CONTRACT_VIOLATION (HTTP 422)`, `base: input 'exposure_years' must be numeric`. Cause: `_contract_value` (`examples/fremtpl2/journey_wf701.py`) returns the raw CSV string for a `decimal` field, and `pricing_core/rating/score.py:383-384` accepts only int, float or Decimal. A fix is outside this slice's brief (the file is `journey_wf701.py`, and `test_policy_inputs_map_real_columns…` asserts the string `"0.5"`); stopped and reported.
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## Decimal wire value and journey DB run 2 — exec-1711e, sl-1711 head 49c741b5, 2026-10-21 21:09-21:13 BST

- **Fix (49c741b5):** `_contract_value`'s decimal branch in `examples/fremtpl2/journey_wf701.py` returns `float(number)` after the Decimal min/max check. Reason (the maintainer's entry "2026-10-21 20:33:40 BST"): the journey posts with httpx `json=`, which cannot serialise a Decimal; `/score` takes int, float or Decimal; exposure is not money, so `CLAUDE.md` §7's Decimal rule does not apply. `test_policy_inputs_map_real_columns_and_keep_the_template_elsewhere` now expects `0.5`. Red-first: a standalone `python -I` check printed `'0.5' str` before and `0.5 float` after (run-small was refused at load1 11.56 to 20.7 beside SL-1275's gate until 21:08).
- **Run 2 of 4** (own DB `gipricing_sl-1711_49c741b5` from template0, one upgrade rc 0, heads = current = `a4d1f08c3b97`, redis db 12, load1 5.53, SL-1275's gate holding gate-1 and gate-1b): `run-small`, `test_wf701_journey.py` + `test_demo_command.py`, rc 1, 40 passed, 1 failed in 189 s, log `~/gi-pricing-plan.local/scratch/sl1711e-2.log`. **A5 and A6 now pass.** The failed test `test_wf701_journey_runs_end_to_end` stops at `DEP: DEPLOY_SWITCH_INCOMPLETE (HTTP 503)`, "1 of 2 subscribed processes acknowledged PREPARE", after `E9 ok`. `test_c7_fails_naming_the_band…` passed in the same run, so the switch worked there.
- **Cause read first as the environment:** the switch channels `gip:switch:local:local:<env>` are Redis pub/sub, which is not per-DB, and `redis-cli pubsub channels` listed `gip:switch:local:local:dev/uat/prod` and `env-*` channels held by another process (the SL-1275 gate beside this run), which counts as a second receiver that never acknowledges. Not a code finding; to be re-run when no other process holds those channels. Run 2 is spent.
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## Journey DB run 3 — exec-1711e, sl-1711 head 135c0b89 (tree 779602f4), 2026-10-21 22:06-22:13 BST

- **Switch rule (to-lead 21:13:34), checked immediately before the run:** gate-1 and gate-1b free (flock -n rc 0 each); `PUBSUB NUMSUB gip:switch:local:local:{dev,uat,prod}` = 0, 0, 0; load1 3.05.
- **Window:** own DB `gipricing_sl-1711_135c0b89` from template0, one upgrade (rc 0), `alembic heads` = `alembic current` = `a4d1f08c3b97`, redis db 12. Run 3 of 4: `run-small`, `test_wf701_journey.py` + `test_demo_command.py`, rc 1, 40 passed, 1 failed in 330 s, log `~/gi-pricing-plan.local/scratch/sl1711e-3.log`.
- **Result:** the deploy switch now passes (the run-2 blocker was the shared channel). The journey passes A5, A6, the deploys and C6, and fails at `C7(i)`: `TRACE_COUNT_0_OUTSIDE_BAND_3_45` after 2000 quoted `/score` calls on prod at the default `rating.trace_sample_rate` 0.01 (expected about 20; P(0) about 2e-9). `test_c7_fails_naming_the_band…` passed (it expects 0).
- **Read so far (no fix made):** `/score` always calls `_maybe_sample_trace` (`backend/src/app/api/score.py:467`); the log shows no `trace sampling failed` line and only two empty `score.trace_produce` queue reads (`drain_traces` found no queued job), so no pending trace row was written: the sampling decision was never true or the rate resolved to 0. `GET /traces` lists only rows with a blob (`traces.py:_filtered`), so a pending row would not show either. Cause not established; a diagnostic is needed, so it is not a fix inside the ruled write set (`journey_wf701.py` decimal branch). The order-independence run was not started (it follows a green run 3).
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## C7(i) static read and journey DB run 4 — exec-1711e, sl-1711 head 5722ad06, 2026-10-21 22:14-22:19 BST

- **Static read (to-lead ruling, step 1), no cause found:** `/score` calls `_maybe_sample_trace` unconditionally after `score_one` (`backend/src/app/api/score.py:467`); it resolves `rating.trace_sample_rate` through `settings_service.resolve` with `caller.environment` (`score.py:589-596`); `resolve` takes the ENV layer (`GIP_SETTING_RATING_TRACE_SAMPLE_RATE`, none set in the shell), then the Environment row, then the workspace row, then the registry default 0.01 (`settings.py:492-511`, `:381-411`); `decide_sampling` samples a quoted outcome when `roll < rate` (`traces.py:98`); a `None` environment would raise and be logged (`score.py:606`), and the run-3 log has no such line. The journey sets no setting before C7(i) (`examples/fremtpl2/journey_wf701.py` has no settings call). So nothing statically sets a rate of 0.
- **Run 4 of 4 (own DB `gipricing_sl-1711_5722ad06` from template0, single head `a4d1f08c3b97` = current, db 12; gate-1, gate-1b free; NUMSUB dev/uat/prod 0/0/0; load1 4.91):** `test_wf701_journey.py` with an uncommitted diagnostic hook, rc 1, 14 passed, 1 failed in 205 s, log `~/gi-pricing-plan.local/scratch/sl1711e-4.log`. **The run produced no evidence:** the hook itself raised `AttributeError: 'list' object has no attribute 'get'` (the settings route returns a list, which the seat did not check against the route before the run) before C7(i) scored a quote, so the `scoring_traces` count it then printed (no rows) was taken before any C7 quote and says nothing. The hook was reverted (`git status` clean). The 4-run budget is spent; a 5th needs the maintainer.
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## Journey DB run 5 (diagnostic) and the C7(i) diagnosis — exec-1711e, sl-1711 head e96eec7e + an uncommitted hook, 2026-10-21 22:20-22:27 BST

- **Run 5 of the diagnosis (the maintainer's "2026-10-21 22:20:10 BST" ASK A):** own DB `gipricing_sl-1711_e96eec7e` from template0, single head `a4d1f08c3b97` = current, db 12; gate-1 and gate-1b free (flock rc 0 each); `NUMSUB gip:switch:local:local:{dev,uat,prod}` 0/0/0; load1 5.68. `test_wf701_journey.py` with an uncommitted hook (its source kept at `~/gi-pricing-plan.local/scratch/sl1711e-run5-hooked-test.py`; reverted, `git status` clean), rc 1, 14 passed, 1 failed in 318 s, log `~/gi-pricing-plan.local/scratch/sl1711e-5.log`. The hook's shapes were read first: `GET /environments/{slug}/settings` declares `list[SettingResolution]` (`environment_settings.py:36-43`, `model_schema/settings.py:52-62`); `ScoringTraceRow.environment` `models.py:2663`, `.blob_sha256` `:2674`.
- **Evidence:** prod's `rating.trace_sample_rate` effective 0.01, `resolved_from` default; `environment_settings` rows for prod: none; `_maybe_sample_trace` calls by (caller.environment, outcome): (prod, quoted) 2073, (uat, quoted) 22; `scoring_traces` by (environment, pending, n): (prod, pending, 22). So sampling works (22 of 2073 is the 1 % rate) and the caller's environment is prod.
- **Cause:** the 22 sampled rows stay pending (`blob_sha256` null) because the in-process harness `_run_in_process` (`backend/tests/test_wf701_journey.py`) registers the rating, dislocation and rate-table handlers but not `register_trace_handlers()` (`backend/src/app/worker/trace_handlers.py:120`), so `drain_traces` runs queued `score.trace_produce` Jobs that have no handler; `GET /traces` excludes pending rows (`traces.py:_filtered`), hence 0. A harness gap, not a platform defect and not a journey-code defect; the worker entrypoint registers it (`entrypoint.py:82`) so the compose run is unaffected.
- **Fix (inside the write set):** `_run_in_process` calls `register_trace_handlers()`. Not yet run: a 6th run needs the maintainer's GO.
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## Journey DB runs 6 and 7 — exec-1711e, sl-1711 head 802ceda3 (tree 52b237e9), 2026-10-21 22:28-22:40 BST

- **Run 6 (the maintainer's "2026-10-21 22:28:30 BST" GO) — GREEN:** own DB `gipricing_sl-1711_802ceda3` from template0, one upgrade (rc 0), `alembic heads` = `alembic current` = `a4d1f08c3b97`, redis db 12. Before it: gate-1 and gate-1b free (flock rc 0 each), `NUMSUB gip:switch:local:local:{dev,uat,prod}` 0/0/0, load1 4.48. `run-small`, `test_wf701_journey.py` + `test_demo_command.py`: rc 0, **41 passed** in 312 s, log `~/gi-pricing-plan.local/scratch/sl1711e-6.log`. The whole WF-701 journey passed in process for the first time, C7(ii-iv) and A2/C4 T5 included, with the 8 mapped steps and the ruled lines asserted by the test.
- **Run 7 (the order-independence run, ruling 1(b)) — RED on a wf701 test:** same DB reused after run 6 (the seat did not create a new DB, which the run-6 terms did not forbid but the run-1 terms read as "one DB per window"), redis db 12 flushed, switch checks re-quoted at 22:34:26 (gate-1/1b free, NUMSUB 0/0/0, load1 4.43). `run-small`, `test_wf701_journey.py` then `test_fremtpl2_algorithm.py` then `test_demo_rating_evidence.py`: rc 1, 34 passed, 1 failed in 329 s, log `~/gi-pricing-plan.local/scratch/sl1711e-7-order.log`. Failed: `test_c7_fails_naming_the_band_when_the_sample_rate_is_zero`, `Failed: DID NOT RAISE` (the journey completed, 2021 `/score` calls after the rate was set to 0.0). The end-to-end test passed in the same run. The two other files run after the wf701 file, so they cannot have affected it; the failure is the wf701 file's own, on a reused DB, and it passed in run 6 on a fresh one.
- **Diagnosis, not settled:** with prod's rate at 0.0, C7(i) found 3 to 45 traces for `rating_version:fremtpl2-wf701-k1@1` in the workspace, so some traces did not come from this test's own sampling. Candidates, none proven: (a) traces left from the end-to-end test of the same session, which per-test cleanup does not remove (a trace is retention-protected) and which share the ref `fremtpl2-wf701-k1@1`; (b) rows left by run 6's session in the reused DB (the DB was empty when I looked after the run, so this cannot be shown now). Only (b) differs between run 6 and run 7; (a) held in both. A fresh-DB repeat of run 7 separates them.
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## C7(i) scoped to its own traces, and the order-independence runs (ruling 1(b)) — exec-1711e, sl-1711 head 6d6a0976 (tree 12be6446), 2026-10-21 22:43-23:10 BST

- **Fix (6d6a0976), the maintainer's "2026-10-21 22:42:33 BST":** C7(i)'s count was every K1 trace in the workspace, so a trace an earlier step had sampled (a decline is always sampled) moved the verdict. `c7()` in `examples/fremtpl2/journey_wf701.py` now settles and records the standing K1 trace ids before its 2000 quotes and counts only the rest (`traces_not_in`); unit test `test_c7_counts_only_the_traces_a_step_sampled`. The change is in `journey_wf701.py` (the journey's own code, where the count lives), not in `test_wf701_journey.py` only as the ruling's text said: a count cannot be scoped from the test file. Red-first: `traces_not_in` is absent at 802ceda3 (0 matches) and returns `['c']` / `[]` after, by a standalone `python -I` check. ruff check . rc 0, ruff format --check rc 0, mypy rc 0 (245 files). Note: `/traces` is filtered by workspace and the workspace is fresh per test (`conftest_db.py:323-326`), so a trace left by another test does not reach this count; the earlier-steps' traces do.
- **Run 7′:** ONE own DB `gipricing_sl-1711_6d6a0976` from template0, one upgrade (rc 0), `alembic heads` = `alembic current` = `a4d1f08c3b97`, redis db 12 flushed before each invocation, no DB reset between the two. Two invocations were refused by `run-small`'s load guard (rc 66, load1 8.1 and 10.6, from another project's jobs on the box), nothing ran; each real invocation re-quoted gate-1/gate-1b free (flock rc 0/0) and `NUMSUB gip:switch:local:local:{dev,uat,prod}` 0/0/0 immediately before (22:57:05 and 23:03:58; load1 5.12 at the reverse run).
  - **Forward (gate order: `test_wf701_journey.py`, `test_fremtpl2_algorithm.py`, `test_demo_rating_evidence.py`):** rc 0, 36 passed in 315 s, log `~/gi-pricing-plan.local/scratch/sl1711e-7f.log`.
  - **Reverse (`test_demo_rating_evidence.py`, `test_fremtpl2_algorithm.py`, `test_wf701_journey.py`), same DB:** rc 0, 36 passed in 367 s, log `~/gi-pricing-plan.local/scratch/sl1711e-7r.log`.
  - Both orders green, so the `_full_level_world()` patch of the shared `_DOMAINS`/`_ESTIMATES` does not change what the other two files see (ruling 1(b)); the full gate confirms it.
- **Cleanup:** dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.

## The compose SOLO run of the scripted WF-701 demo — exec-1711c, sl-1711 head 4b958a94 (T1 abcc70d2, fix 4b958a94), 2026-10-22 11:05-13:04 BST

**Result: PASS (the maintainer's "2026-10-22 13:04:37 BST" entry).** `demo.py --journey wf-701 --target compose` ran ALONE (no gate, no switch test; the `demo` slot held by one `setsid` holder, PID/PGID 461740, released at the end) against the shipped compose topology as tools-main `f3462d8f` defines it: `api` x2 behind `lb`, the four worker pools, the one-shot `migrate`. Host deviation, recorded as the maintainer's "2026-10-22 00:54:02 BST" entry asked: only the database name, the redis db and the blob bucket differ, through the untracked override `scratch/sl1711-compose-override.yml` (compose hard-codes `gipricing`, redis db 0 and `gip-blobs`).

- **rc 0, the demo's own closing lines verbatim** (`scratch/sl1711-compose-wf701.log`, lines 129, 155, 156 and 158):
  - `   WF-699 part done in 1335s`
  - `   WF-701 part done in 1165s: OVER the pre-registered 10 min target (recorded, not tuned)`
  - `   journey done in 2500s`
  - `   compose run done in 2573s`
- **The 600 s target is a recorded MISS, not a failure.** WF-701's part took 1165 s against the pre-registered 600 s. PL-1710 T7 and acceptance 4 say "a miss is recorded, not tuned away", and `demo.py` says the same; the maintainer's "2026-10-22 12:06:24 BST" entry ruled it so. Nothing was tuned in this slice.
- **Relay watcher:** `scratch/sl1711-relay-watch.log` has 0 KILL lines. The outbox relay (`compose run ... worker-default ... beat`) read `GIP_DATABASE_URL=postgres:5432/gipricing_sl1711_compose`, `GIP_REDIS_URL=redis://redis:6379/13`, `GIP_BLOB_BUCKET=gip-blobs-sl1711-compose` at every 5 s poll.
- **Window:** the demo started 12:20:58 BST (11:20:58Z) and ended 13:03:57 BST (12:03:57Z), `timeout 3600`.
- **Image:** `gi-pricing-app:4b958a940b668d4b9f59399d3553902b8a869d7b`, Id `sha256:81f7f6b0e9d4fe5eaacc218ca477a58446288da8ca1b74202b5be282f16a3e68`, Created `2026-10-22T10:47:28Z`; the build's own rc was 0 (`scratch/sl1711-compose-build-h2.log`, 0 ERROR lines). Both `up` and the `config --hash` pre-guard ran under `COMPOSE_FILE=<tools-main compose>:<override>` with no `-f`: postgres `aa63baa2`, redis `d34adc17` and minio `4847f5c0` equalled the running containers' config-hash labels, so `up` re-created none of them. `migrate` ended at `a4d1f08c3b97` in the run's own database.
- **End guards (re-read clean by the lead and by the maintainer):** the four infra containers the same IDs (postgres `8c11e046ebf2`, redis `a0091f369f6a`, minio `e8e55e262ec9`, keycloak `da16c49c2d82`), healthy; redis db 0 `DBSIZE` 56 and db 13 0; `gipricing` at `d4e81b7a2c95` with environments / tenant_marker / dataset_versions = 3 / 1 / 0; no `gipricing_sl1711_compose` database; the same six buckets with `gip-blobs` at 474 objects; NUMSUB on `gip:switch:local:local:{dev,uat,prod}` 0 / 0 / 0; no `-run-` container; `lslocks` 0; keycloak's bind source still under tools-main.

### The jobs table of the run (`scratch/sl1711-compose-jobs.txt`, 76 rows, all queues)

Per kind, durations are `finished_at - started_at` in seconds, from that file:

| kind | queue | n | status | total s | longest s |
|---|---|---|---|---|---|
| dataset.ingest | io | 3 | succeeded | 4.4 | 2.1 |
| dataset.validate | compute | 12 | succeeded | 1.5 | 0.2 |
| dataset.derive | compute | 2 | succeeded | 0.8 | 0.4 |
| model.fit | compute | 3 | succeeded | 37.1 | 19.7 |
| model.transparency | compute | 1 | succeeded | 25.0 | 25.0 |
| model.compare | compute | 1 | succeeded | 0.5 | 0.5 |
| peril_structure.reconcile | compute | 1 | succeeded | 0.4 | 0.4 |
| rate_table.diff_cells | compute | 1 | succeeded | 0.3 | 0.3 |
| rating.compile | default | 6 | succeeded | 1.4 | 0.3 |
| rating.compile | default | 2 | failed `PIN_NOT_APPROVED` | 0.3 | 0.2 |
| rating.regression | compute | 5 | succeeded | 8.6 | 2.1 |
| rating.regression | compute | 2 | failed `GOLDEN_QUOTE_MISMATCH` | 9.2 | 6.1 |
| score.trace_produce | scoring | 33 | succeeded | 6.0 | 0.3 |
| **dislocation.run** | compute | 4 | succeeded | **2326.9** | **718.2** |

The two failed kinds are the demo's own refusals (the unapproved GBM pin, step C4, and the golden-quote move, step D2), not faults. The four `dislocation.run` spans, in UTC, each on the one compute worker:

| started | finished | duration |
|---|---|---|
| 11:23:19 | 11:32:28 | 9 min 9 s |
| 11:32:29 | 11:44:27 | 11 min 58 s |
| 11:44:35 | 11:53:12 | 8 min 37 s |
| 11:54:46 | 12:03:48 | 9 min 2 s |

Together they are 2326.9 s of the 2573 s compose run, about 90 %. By their order the first two belong to the WF-699 part (its D8 and E4 steps name a dislocation run) and the last two to the WF-701 part; the part boundary is the demo's own timer, so this split is read from order, not from a per-job label. No other kind is above 25 s.

**Open question for the auditor:** is a 9 to 12 minute `dislocation.run` at the demo's volumes (678 013 freMTPL2 rows ingested; its `D7` line reports 19985 policies in the attribution sample) a product performance finding that needs an FD (owner, severity, and the NFR it breaches, if any)? This slice decides nothing beyond recording the numbers; its `D7` line cites FD-1576 (full-book attribution cost) as the known cost.

### Conditions

A shared box, in use by other seats (build seats editing only, per the lead's note of that window); **one compute worker at concurrency 2** (`GIP_WORKER_COMPUTE_CONCURRENCY` default 2, `deploy/docker-compose.yml` `worker-compute`), api x2 at `WEB_CONCURRENCY` 1, memory 31 GB total. load1 was 4.63 at the demo start (4.95 just after `up`) and 2.35 at the end. During the run `worker-compute` read 133 % CPU on a `dislocation.run`.

### Rulings (by header, in `~/gi-pricing-plan.local/channel/to-lead.md`)

- "2026-10-22 11:05:58 BST — Maintainer: SL-1711 compose SOLO Phase B GO, with one amendment to my own step 6" (the absolute `-f`; the seven-service `stop`, never a bare `--profile app stop`).
- "2026-10-22 11:10:17 BST — Maintainer: SL-1711 compose STOP ruling (A), and the order of SL-1275's DB window" (the dedicated bucket `gip-blobs-sl1711-compose`; `mc rb --force` of that bucket only).
- "2026-10-22 11:14:25 BST — Maintainer: SL-1711 relay BLOCKER ruled: option (1), a slice code fix in demo.py, with guards" (`compose_command` omits `-f` when `COMPOSE_FILE` is set; red-first; the live relay-env kill watcher).
- "2026-10-22 11:18:46 BST — Maintainer: RESUME for lead 27. Lead 26 stopped for handover at 236k; one ruling (SL-1711 test_demo_command GREEN is option (a))" (only its SL-1711 ruling was applied; its handover framing was superseded the same day).
- "2026-10-22 11:18:56 BST — Maintainer: lead 26's addendum (config proof at H2; the labels on the infra containers)" (the config-hash pre-guard before `up`).
- "2026-10-22 11:42:48 BST — Maintainer: SL-1711 test_demo_command ACCEPTED; the compose retry at H2 is GO, with the GIP_BUILD amendment".
- "2026-10-22 12:06:24 BST — Maintainer: SL-1711 compose retry runs to its END; the 600 s target is recorded per PL-1710, not ruled a fail".
- "2026-10-22 12:13:55 BST — Maintainer: SL-1711 retry timeout: (i) let it run; (ii) PRE-APPROVED on rc 124" (the re-run with `timeout 3600` as the only change).
- "2026-10-22 13:04:37 BST — Maintainer: SL-1711 compose SOLO PASSED; SL-1275 re-gate GO, effective on clean end guards".

### Code change that the run proved necessary (H2)

`scripts/demo.py::compose_command` always passed `-f deploy/docker-compose.yml`, so the override never reached the outbox relay's `compose run`, which would have run on `gipricing`, redis db 0 and `gip-blobs` and (through `migrate`) upgraded the shared database. T1 `abcc70d2` adds three tests to `backend/tests/test_demo_command.py` (the "set" pin red by name: `1 failed, 28 passed`, rc 1, 0 errors, 0 skipped, on a per-worktree database `gipricing_sl-1711_118c2dd0`); the fix `4b958a94` (+7 / -2 in `scripts/demo.py`) makes `compose_command` omit `-f` when `COMPOSE_FILE` is set, with `-p` and `--profile app` unchanged. Green at `4b958a94`: `29 passed, 1 warning`, rc 0, 0 failed, 0 errors, 0 skipped. That window's database was dropped (`pg_database` count 0); redis db 0 stayed 56.

### Disclosed deviations

- **Try 1 STOPPED at `up` on `TenantMismatchError`** (`app/platform/tenancy.py:69`): the shared minio's `gip-blobs` carries tenant `local`, the compose stack is configured for `compose-reference` (FR-436). Nothing was written to the shared bucket beyond `ensure_bucket`'s lifecycle-rule merge; ruling (A) of 11:10:17 gave the run its own bucket. The build had no rc captured that time (the log had 0 ERROR lines); every later build captured its rc.
- **The relay `-f` blocker and its fix H2** (above): found by the lead and the maintainer at the retry's pre-check, before any relay existed.
- **Run 1 of the retry ended rc 124**: the demo's own `timeout 1800` expired at about 11:19:50Z, during the WF-701 part, after the WF-699 part had taken 1376 s. **Its jobs dump was LOST**: the run's database was dropped at cleanup about 11:19Z, before the 12:06 instruction to dump it first reached the seat. The partial record is the lead's 12:07 BST snapshot, `scratch/sl1711-compose-jobs-lead-snapshot.txt` (run 1's first `dislocation.run` 10:51:34Z to 11:00:48Z, 9 min 14 s; a second `dislocation.run` was still `running` when taken). The maintainer pre-approved the re-run with `timeout 3600` (12:13:55); run 2 above is that re-run.
- **The relay container was left running after run 1's timeout kill** (`gi-pricing-worker-default-run-03621ab1587b`, up 28 min): the demo died before its own relay stop. The seat stopped it by its full name; it carries `--rm`.
- **The watcher script's loop check failed in the re-run's first start** (`ps -eo pgid=` pads a six-digit PGID with a space, so `grep -qx` never matched and the watcher exited at once); the seat fixed it with `tr -d " "` and restarted it about 4 s after the demo began, before the relay appeared (`scratch/sl1711-relay-watch.sh`, untracked).
- **The absolute `-f`:** the build and `up` name `deploy/docker-compose.yml` by its absolute tools-main path, `docker build -f <sl-1711>/deploy/Dockerfile ... <sl-1711 root>`; the maintainer accepted it at 11:05:58 (the Dockerfile is byte-identical between `f3462d8f` and `3ac2e499`).
- **The `GIP_BUILD` amendment:** the demo's own env also carries `GIP_BUILD=<H2>`, because `compose run` resolves `image: gi-pricing-app:${GIP_BUILD:-unset}` from it (the lead's amendment, accepted at 11:42:48).
- **tools-main moved during the first Phase B:** a re-audit seat had committed its branch inside tools-main (HEAD `51f1c261`, on a branch). The seat stopped before starting anything; the lead restored `f3462d8f` detached, and the maintainer's "2026-10-22 11:48:11 BST" entry closed the incident with the rule that no seat runs `git checkout` or `git switch` in tools-main.
- **`ruff format --check scripts/demo.py` exits 1**: the file already fails it on `origin/main` (CI runs `ruff check .` only, `python.yml:199`); the maintainer accepted it as is at 11:18:46.
