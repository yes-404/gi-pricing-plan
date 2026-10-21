---
id: LG-8136
family: ledger
title: WK-674 slice SL-1711 — the scripted WF-701 deployment-steps demo (PL-1710) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: 03c6397f200868f1a0827c197ffbc6de0bf65eda
phase: P2
work: WK-674
slice: SL-1711
plans: [PL-1710]
corrected_by: []
relates: [PL-1710, PL-1237, PL-1537, PL-1620, PL-1544, SL-1711, SL-1258, SL-1259]
---

# LG-8136 — WK-674 slice SL-1711: the WF-701 deployment-steps demo

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
- **A5 draws K = 200 real freMTPL2 policies (the maintainer's ruling "2026-10-21 15:59:05 BST", Ruling 1, which rejected the `contract_sample` deviation).** `portfolio_policies()` in `examples/fremtpl2/journey_wf701.py` reads the seed's portfolio rows (`seed.build_csv(seed.PORTFOLIO_ROWS)`, the sha256-pinned public file, after v2's `exposure_years <= MAX_EXPOSURE` step; 19 985 rows, measured). **Draw rule: the first 200 by ascending `IDpol`; no random number.** `policy_inputs` maps each contract field that has a dataset column of its name (`seed.RENAMES` applied) to the real value and keeps the template's for a field with none (`current_premium_minor`). A real value outside its contract makes A5 fail `REAL_POLICY_OUTSIDE_CONTRACT`: a finding to report, never replaced. K is fixed (the grow-until-A6-binds loop is removed). `contract_sample` and its two tests are removed; the new tests are pure and cover the mapping, the draw order and the failure on broken input.
- **Deviation 3, executor-recorded, ACCEPTED (maintainer, to-lead "2026-10-21 16:01:49 BST" item 1): K1 = rv3 plus an added 180 floor, not the "150 -> 180" change of PL-1710 DP-4 (a).** Evidence at sl-1711 head bcae10ea: rv3 is `build_version("RV3", ...)` (`examples/fremtpl2/journey.py:1031`), seeded from `save_demo_algorithm` -> `build_fremtpl2_algorithm` (`examples/fremtpl2/model.py:820-838`); `examples/fremtpl2/algorithm.py` has no floor. The v1/v2 JSON floors (`rating/fremtpl2-rate.rating-algorithm.v1.json:395` 15000, `v2.json:457` 18000) are a fixture: `examples/fremtpl2/rating/README.md:1-6` says "measurement only until the G2 exit-demo slice adopts it". Adopting the fixture as the demo algorithm is DECLINED (a G2 adoption plus a `seed.py` change).
- **Data copy (maintainer ruling "2026-10-21 16:05:17 BST"):** the worktree's gitignored `examples/fremtpl2/data` is a COPY (`cp -rL`) of the root checkout's, not a symlink (a symlink lets tools write through to the user's checkout). Verified `test ! -L` and the file count equal to the root's. Untracked; not committed.
- **K1 and K2 are Rating Versions of the live algorithm's slug (executor-recorded reading, accepted by the maintainer, Ruling 2, "2026-10-21 15:59:05 BST")** (`fremtpl2-rate`, next versions), because the Regression Suite and the submit gate are bound to the algorithm slug (`current_suite_for_algorithm`) and no route creates a suite for a new slug. K1's golden quotes are updated deliberately (new suite version) only where the new value is exactly the 180 floor; K2's decline range (`bonus_malus` 141 to 150) is chosen to leave the existing goldens passing, so it adds no suite version.
- **T6 (`scripts/demo.py`).** `--journey wf-701`, `--target {local,compose}`, `check_compose_up` (R9), `prepare_world` (the seed and pre-flights extracted so the compose run shares them), `run_journey` takes the journey name. `backend/tests/test_demo_command.py`: `JOURNEYS` assertion updated, 4 new tests, the two source-order tests read `_effective_demo_source()` (the flow is unchanged, its text moved). **R8/R9 red by cause:** the new tests run against the pre-change `scripts/demo.py`: 6 failed (missing `prepare_world`, `compose_services`, `wf-701`); against the change: 24 passed, 2 errors (the two DB fixtures of existing tests: no test DB without a grant).
- **WF-701's two dated lines** (11:14:40 ruling items (1) and (2)) in `docs/workflows/WF-00701-deploy-and-monitor.md`: the §1 precondition row and the C2 note.
- **Owed to the DB lane (grant needed):** `backend/tests/test_wf701_journey.py` (the end-to-end test and R6), `backend/tests/test_demo_command.py` (its 2 DB tests), `backend/tests/test_api_jobs.py` (Task 0.1). **Owed to the compose window:** T5's A2/C4/replica C6 reds and greens, R5 on the stack, R7 (decline floor removed in a scratch copy), T7 and the rehearsal.

## Journey DB run 1 — exec-1711d, sl-1711 head 0476f3c2 (tree f1fcd69d), 2026-10-21 16:35-16:40 BST

- **Window:** own DB `gipricing_sl-1711_0476f3c2` from template0; ONE `alembic upgrade head` (rc 0, under `small-test`); `alembic heads` = `alembic current` = `a4d1f08c3b97` before the test. Redis db 12, load1 5.83. Run 1 of 4 (3 unused): `run-small` on `backend/tests/test_wf701_journey.py` + `backend/tests/test_demo_command.py`, rc 1, 39 passed, 2 failed in 85 s, log `~/gi-pricing-plan.local/scratch/sl1711d-1.log`. Cleanup: dropdb rc 0, `pg_database` count 0, db 12 `DBSIZE` 0.
- **Failures:** `test_wf701_journey_runs_end_to_end` and `test_c7_fails_naming_the_band_when_the_sample_rate_is_zero`, both at A5: `REAL_POLICY_OUTSIDE_CONTRACT`, 416 field failures. A4 had passed. A5 onwards is unexercised.
- **Cause (read-only check, no DB):** not a missing base level. `_relativities` (`packages/pricing-core/src/pricing_core/modelling/glm.py:935`) emits the base first (`is_base=True`), and `model.py:987-990` takes every level of it. The test world is hand-built: `test_wf699_journey._world` uses `test_demo_rating_evidence._fit_result()` over `test_fremtpl2_algorithm._DOMAINS` (`:199-204`): `veh_brand` B1,B2; `veh_gas` Diesel,Regular; `area` A,B; `region` R11,R24. The contract domains are those two levels per factor.
- **Count (reproduced from `portfolio_policies()`, first 200 by IDpol, against those domains):** 416 field failures over 185 of 200 policies, exactly the logged 416. `area` 150 (C 49, D 53, E 37, F 11), `region` 123 (15 levels, R82 15), `veh_brand` 143 (B12 130, B3 4, B4 3, B5 2, B11 2, B13 1, B6 1), `veh_gas` 0. Against the real book's base by exposure (B1, Regular, C, R24): 49 failures are on a base level (`area` C) and 367 on other levels. The fixture's own bases (B1, Diesel, A, R11) never fail.
- **Fix site (not applied):** the fixture domains in `backend/tests/test_fremtpl2_algorithm.py`/`test_demo_rating_evidence.py`, shared with other tests, or a world built in `test_wf701_journey.py` from a full-level fit. PL-1710 item 8 write set (`PL-01710`:448-452) names `test_wf701_journey.py`, not those files. Needs a ruling.

## PRs

(none; the lead opens the PR)
