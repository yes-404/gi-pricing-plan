---
id: LG-8155
family: ledger
title: WK-1178 slice SL-1736 — the P2 NFR measurement sweep (NFR-467, 468, 470, 485, 1443 DIAGNOSTIC; NFR-472 red-first) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-1736
plans: [PL-1735]
corrected_by: []
relates: [PL-1735, SL-1736, SL-1259, RL-1441, LG-1444, RL-1614, FD-1745, FD-1746]
---

# LG-8155 — WK-1178 slice SL-1736: the P2 NFR measurement sweep

Filed 2026-10-22 under working id 8155 (lead-reserved); executed by seat `exec-1736`, base
`origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`.

**GO:** the maintainer's entry "2026-10-22 11:53:15 BST — Maintainer: SL-1569 and SL-1736 slice GO; D1–D4 and the two orders ruled"; for this slice, verbatim: "**SL-1736** (WK-1178, PL-1735). Its non-ALONE prep may start now on a seat. **ORDER:** its 4 ALONE grants run after SL-1275 and SL-1711 merge, with the build seats parked. Each grant is requested from me with the exact commands. **D2:** Task 4's dated line goes under the row that owns the measurements now (roadmap :1278), not the closed SL-1259 row. **D3:** five runs. The plan's "six" is a miscount, and LG records the correction. **D4:** Task 0's load1 < 1.0 start allows up to 10 min to settle. Then record the reading and STOP to the lead, who brings it to me. I then rule: proceed at the reading, or move the grant to nfr-bench-1."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoted from the slice's Work-plan row, `docs/roadmap.md` `#### SL-1736` (`PL-1735` is the plan; WK-1178 has no Work plan, so the row is the slice's Work-plan row):

> NFR-468 (`01`: the one-way read, p95 < 300 ms, never computed), NFR-470 (`01`: storage ≤ 1.2× the parquet payload; dedup by content hash), NFR-485 (`02`: 5 M × 60 fit within 32 GB) and NFR-1443 (`03`: the cells-diff page p95 ≤ 300 ms, and the 2× property) are each measured on the shared VM with a committed instrument (`scripts/measure-p2-nfr-sweep.py`; `scripts/bench-model.py --peak hwm`), labelled DIAGNOSTIC, latency figures also "server-side, in-process, excludes network". Thresholds and reading rules are committed before the first run. […] **A reading that comes out OVER goes to the lead for an `FD-`. Its requirement's text is not changed.**

Requirements: NFR-467, NFR-468, NFR-470, NFR-472 (red-first test + fix), NFR-485, NFR-1443 (`PL-1735` "Scope and requirements").

**Activation commit (L1):** this ledger, the `SL-1736` row `status: active` with its dated line, and `PL-1735` `status: draft` → `active` ride the slice PR (the #1286 `cad75a7e` and #1331 `2bc4dc8c` precedent, as the GO entry's preamble confirms for PL-1735).

**Rulings of the GO entry that bind this ledger**
- **D2:** Task 4, Step 4's dated line goes under the roadmap row that owns the nfr-bench-1 measurements now (`docs/roadmap.md`, the "Dated 2026-10-19 … `nfr-bench-1` … owner row" line at `:1278`, in the `SL-1259` block's tail), not on the closed `SL-1259` row's own fields. `PL-1735` Task 4 Step 4 and its write set say "under `SL-1259`'s row"; the GO ruling changes the placement, and this ledger records the delta.
- **D3 — correction to the plan.** `PL-1735` says "Six runs" for NFR-1443 (NFR-1443 section, Instrument). The runs it lists are five: rows 10 000, rows 250 000, parquet 10 000, parquet 250 000, parquet 1 000 000. **The sweep runs five.** `LG-1444` Hold B is cited by the plan as "six" with the same list; the list, not the count, is followed.
- **D4:** Task 0's ALONE start requires load1 < 1.0. The executor may let it settle for up to 10 minutes; if it is still ≥ 1.0 it records the reading and STOPS to the lead, who brings it to the maintainer, who rules: proceed at the reading, or move the grant to nfr-bench-1.

### Task list

- [x] Activation commit (L1): this ledger, the row, the plan status (`4d38616a`).
- [x] Task 0 Step 2 (P0): the `contention` subcommand, its constants and the pure decision logic, with unit tests (`157d327e`). Written, **not yet run**.
- [ ] Task 0 Step 3: the factor runs (grants 1 to 3 below, with the B runs between them).
- [ ] Task 0 Step 4 (P1): the commit that sets `NEAR_BOUND_FRACTION` to the measured band (constant only), before any sweep run. **Until Step 3 lands, `NEAR_BOUND_FRACTION = 0.43` stands, as committed in P0.** Every sweep constant other than the fraction is already in P0 (`157d327e`); P1 is therefore one later commit that changes one number, or, if the factor reading never lands, none (the maintainer's D4 ruling decides).
- [ ] Task 1: NFR-472 red-first test, then the fix. **Not started: it is a DB-backed test (`backend/tests/test_api_datasets.py`) and needs the lead's written DB lane (executor.md, line 88); the plan's Step 2 expects it red by cause.**
- [x] Tasks 2, 3, 5, 5a written, **not yet run**: `one-way`, `storage`, `cells-diff`, `profile` subcommands (`9a350904`). The database-backed phases are wiring only until their first smoke in a granted window; see "Owed".
- [x] Task 3 Step 4: NFR-470's dated clarification on the row (`docs/specs/01-data-management.md`), minted ids substituted (SL-1736, PL-1735, RL-1724). `audit-docs` owed.
- [x] Task 4 Steps 1 and 3 (instrument): `bench-model.py --peak hwm` (`9a350904`); Step 4's dated line, at D2's placement (below). The shared-VM curve itself is not run.
- [ ] Task 6: gate, per-NFR rows, hand-off.

### Gate

Not yet run.

### Audit

Not yet written (auditor seat).

### Build log

#### 2026-10-22 — activation (tree `f3462d8fc1336dc4583fe8a7af92fed399993a55`)

Phase restriction in force: the SL-1711 compose retry is ALONE; edits and git only, no measurement and no test run until the lead releases it.

#### 2026-10-22 — prep commits (base `f3462d8f`)

| Commit | What |
|---|---|
| `4d38616a` | activation: this ledger, `SL-1736` row `active` with its dated line, `PL-1735` `active` |
| `157d327e` | **P0**: `scripts/measure-p2-nfr-sweep.py` constants, pure decision logic and `contention`; `tests/test_measure_p2_nfr_sweep.py` |
| `9a350904` | the `one-way`, `storage`, `cells-diff`, `profile` subcommands; `bench-model.py --peak hwm` |
| (next) | NFR-470's dated clarification; the D2 run-list line at `docs/roadmap.md` under the nfr-bench-1 owner row |

**Deviation from the plan, recorded:** the plan puts the thresholds in P1 and the contention subcommand in P0. The thresholds and bands are ruled values and carry no run-dependent number except `NEAR_BOUND_FRACTION`, so they are in P0 with it at the interim 0.43; P1 is the commit that replaces that one number by Task 0's band. Every sweep run's start stamp must still be later than the P1 `%aI` (or, if D4 sends the grant to nfr-bench-1 and the factor never lands, than P0's).

**Disclosed deviation: not test-first (lead 26, 2026-10-22).** `157d327e` wrote the harness code before its tests existed, so Task 0 and the harness are not test-first as `test-driven-development` and the plan require. No red run was taken before the code. The red runs still possible are shown at the first `run-small` of `tests/test_measure_p2_nfr_sweep.py`, and any red there is recorded here by cause. The same applies to the later subcommands (`9a350904`), which have no unit test of their own.

**Rule for Grant 4 (lead 26):** the Redis db, the MinIO alias and the bucket removal in the Grant 4 block are guesses. They are replaced by lines copied verbatim from `scratch/gate-template-demostop.sh` and the compose-retry file before any grant request is sent.

**Dependency to know:** `cells-diff` imports two seeding helpers from `backend/tests/test_rate_tables_service.py` (`_seed_approved_model`, `_set_threshold`), because the plan says to mirror the test fixtures rather than reinvent them; `one-way` and `storage` drive `examples/fremtpl2/seed.py` (`run`, `grant_demo_principals`, `build_csv`, `recipe`). A change to any of those names breaks the harness.

**D3 correction applied:** `CELLS_DIFF_RUNS` in the harness lists five runs.

#### 2026-10-22 13:0x BST — static checks and the harness unit test, beside SL-1275's gate (tree: this branch, base `f3462d8f`; every command under `nice -n 19 ionice -c3`, load1 3.5 to 4.5 < 6)

| Check | rc | Result |
|---|---|---|
| `ruff check` on the three changed Python files | 0 | first run: 10 findings (3 auto-fixed import order; SIM115, B023, PT018 ×2, PT011 ×3 fixed by hand); re-run "All checks passed!" |
| `ruff format --check` on the harness and its test | 0 | formatted. `scripts/bench-model.py` is NOT format-clean at `f3462d8f` (checked on the original blob, rc 1), so it was not reformatted: only my edit is in its diff |
| `mypy tests/test_measure_p2_nfr_sweep.py` | 0 | first run 8 errors (missing annotations), annotated; "Success: no issues found in 1 source file". `scripts/` is not in mypy's `files` list, so the harness itself is not type-checked by the gate |
| `run-small.sh <wt> tests/test_measure_p2_nfr_sweep.py` | 0 | `42 passed in 0.33s` (first run `42 passed in 1.14s`). **No red was seen**: the code predated its tests (disclosed above), so no failure by cause was observed |
| `doc-index.py` regen, then `--check` (gate-2) | 0, 0 | `docs/INDEX.md: OK (byte-stable)`; 4 insertions, 3 deletions |
| `audit-docs.py` (gate-2) | 1 | one FAILED: `check 31: gap in the full allocation between 1838 and 8155` — the working id, cleared by the mint. No line names SL-1736's files |
| idsweep (`origin/sl-1736-wk1178-nfr-sweep`) | — | `main: 1838 pairs; duplicate numbers:` and an empty CROSS-BRANCH list; no COLLISION line |

#### 2026-10-22 13:16 BST — the harness unit test, re-run once to save its output (tree `6b4a4a1c0233dbfbb69eee9a1a645b0514678f1a`, load1 4.67)

Command: `nice -n 19 ionice -c3 bash $W/scripts/run-small.sh $W tests/test_measure_p2_nfr_sweep.py`, rc 0, log `~/gi-pricing-plan.local/scratch/sl1736/harness-run-small.log`, verbatim:

```
run-small: waiting for /tmp/slots/small-test at 13:16:24 (load 4.67)
..........................................                               [100%]
42 passed in 0.18s
```

(The 13:06 run, `42 passed in 0.33s`, was not saved to a log; this re-run replaces it as the record.)

#### 2026-10-22 — the DB-lane smoke (`cells-diff --only rows-10000 --seeded-jobs 500`): WIRING TEST, NOT A READING; ended rc 1 on a harness defect (tree `40d4ac2883be313c292b5eb3086148789a3e8da6`)

GO: the lead's "GO for the SL-1736 smoke now" (lead 26), on the maintainer's "2026-10-22 13:11:48 BST — Maintainer: SL-1554 build NOTED; SL-1736 smoke GO; the gap order". Command, in the foreground: `timeout 1200 flock -w 900 /tmp/slots/gate-1 bash ~/gi-pricing-plan.local/scratch/sl1736/smoke.sh`; wrapper rc 0, script's smoke line `| smoke | rc=1 |`. Logs under `~/gi-pricing-plan.local/scratch/sl1736/`: `smoke-wrapper.log` (all of the below), `smoke.out` (empty: the failure came before any output), `smoke.err`, `smoke-alembic.log`. Load1 at the start 2.23; available memory 23 GB. The run touched neither the deployment switch nor a gate slot beyond gate-1 itself.

Summary and zeros lines, verbatim from `smoke-wrapper.log`:

```
| head | 40d4ac2883be313c292b5eb3086148789a3e8da6 |
| load1 | 2.23 |
| bucket gip-test-blobs-gate-1 reset (start) | rc=0 |
| createdb gipricing_sl1736_smoke | rc=0 |
| alembic upgrade | rc=0 |
| redis db 1 FLUSHDB (start) | rc=0 |
| smoke | rc=1 |
  File ".../scripts/measure-p2-nfr-sweep.py", line 780, in _cells_diff
    from backend.tests.test_rate_tables_service import _seed_approved_model, _set_threshold
ModuleNotFoundError: No module named 'backend'
| dropdb gipricing_sl1736_smoke (end) | rc=0 |
| redis db 1 FLUSHDB (end) | rc=0 |
| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |
| zeros | own-DB count=0 redis db 1 dbsize=0 |
```

`mc ls g/` after the run: `aud933-bucket/`, `gip-bench-compiled-for/`, `gip-bench-score-batch/`, `gip-blobs/`, `gip-test-blobs/`, `gip-test-blobs-1711/`; no `gip-test-blobs-gate-1`.

**Cause (a harness defect, not a platform finding):** `_cells_diff` imports `backend.tests.test_rate_tables_service` at its top, before `_Env()` calls `_bootstrap_paths()`, so the repository root is not yet on `sys.path`. The failure is before any seeding, so the seeded-Job shape, the helper signatures and the 202 flow are **still untested**. **Proposed fix** (not made; awaiting the lead): call `_bootstrap_paths()` first in `_cells_diff`, then re-run the same smoke. The unit test cannot see this: it never runs a subcommand.

#### 2026-10-22 — smoke run 2 (head `e971196af1acaaade98a619e1403827f62fb77cb`, load1 3.85, 23 GB available): rc 1, a second harness defect

Fix for run 1 (commit `e971196a`): `_bootstrap_paths()` is now the first statement of `_cells_diff`, and of `_one_way`, which had the same ordering defect (it imported `pricing_core`, `app` and `model_schema` before bootstrapping; `_storage`, `_profile`, `_profile_child` and `contention` import nothing from the repo before they bootstrap or at all). Run 2 got past the imports and seeded 500 Jobs through `job_service.submit`, then failed at the harness's own bulk `UPDATE jobs SET status = 'succeeded'`:

```
| smoke | rc=1 |
sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.CheckViolationError'>: new row for relation "jobs" violates check constraint "ck_jobs_terminal_iff_finished"
| dropdb gipricing_sl1736_smoke (end) | rc=0 |
| redis db 1 FLUSHDB (end) | rc=0 |
| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |
| zeros | own-DB count=0 redis db 1 dbsize=0 |
```

Wrapper rc 0 over smoke rc 1. Logs: `~/gi-pricing-plan.local/scratch/sl1736/smoke-wrapper.log` (run 2; run 1's copy is `smoke-run1-wrapper.log`, `smoke-run1.err`), `smoke.err`, `smoke.out` (144 B). **Why the wrapper exited 0:** `smoke.sh` ended with `echo` and `tail` commands, and its EXIT trap `fin()` ended with `mc ls`, so its exit code was the last command's, not the smoke's. It was not designed to propagate; that is a flaw, fixed below.

**Every check constraint on `jobs`** (model `backend/src/app/db/models.py:191-205`, migration `backend/migrations/versions/df53696a2682_platform_core_jobs_audit_events_outbox.py:148-150`), verbatim:

- `ck_jobs_terminal_iff_finished`: `(status IN ('succeeded','failed','cancelled')) = (finished_at IS NOT NULL)`
- `ck_jobs_finished_after_started`: `finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at`
- `ck_jobs_trace_id_is_w3c_hex`: `trace_id IS NULL OR trace_id ~ '^[0-9a-f]{32}$'`

**Fix for run 2 (next commit):** the seeded Jobs now move to `succeeded` through the platform's own lifecycle, `jobs.transition` (`queued -> running -> succeeded`, with `result=JobResult(kind="none")`), which sets `started_at`, `finished_at` and writes the audit event by construction (`backend/src/app/platform/jobs.py:199-264`), so no constraint is hand-satisfied and the bulk UPDATE is gone. `smoke.sh` now saves the smoke's rc and `exit`s with it at the end of `fin()`, after the clean-up; its last printed line is `| exit | smoke_rc=<n> |`. Proof is required of run 3: the wrapper rc must equal the smoke rc, both quoted.

#### 2026-10-22 — smoke run 3 (head `c4f7f80ea9ab8c6cb73e9105d588ec61fc0d6714`, tree `fcf268e67e45a6b90a05edaf1c49914dff483988`, load1 3.83, 22 GB available): PASSED as a wiring test; **not a reading**

Command: `timeout 1700 flock -w 900 /tmp/slots/gate-1 bash ~/gi-pricing-plan.local/scratch/sl1736/smoke.sh`, foreground. **Smoke rc 0 and wrapper rc 0** (both quoted: `| smoke | rc=0 |` in the log, `wrapper_rc=0` from the shell). Logs under `~/gi-pricing-plan.local/scratch/sl1736/`: `smoke-wrapper.log`, `smoke.out`, `smoke.err`; run 2's copies are `smoke-run2-wrapper.log`, `smoke-run2.err`. Verbatim from `smoke-wrapper.log`:

```
| createdb gipricing_sl1736_smoke | rc=0 |
| alembic upgrade | rc=0 |
| redis db 1 FLUSHDB (start) | rc=0 |
| smoke | rc=0 |
| dropdb gipricing_sl1736_smoke (end) | rc=0 |
| redis db 1 FLUSHDB (end) | rc=0 |
| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |
| zeros | own-DB count=0 redis db 1 dbsize=0 |
[mc ls g/] aud933-bucket/ gip-bench-compiled-for/ gip-bench-score-batch/ gip-blobs/ gip-test-blobs/ gip-test-blobs-1711/
| exit | smoke_rc=0 |
```

What it proved, by the code path it reached: 500 seeded Jobs completed through `jobs.transition`; the rows-10000 table seeded, its two versions asserted `storage: rows`; the first diff request answered 202; the Job ran to `succeeded` with its artifact present; 100 later pages at `limit=50` all answered 200. The one reading line it printed, kept here only to show the output shape and **not read as a measurement** (500 seeded Jobs not 10 000, load1 3.4, one run, no quiet window): `{"reading": "NFR-1443", "run": "rows-10000", "storage": "rows", "cells": 10000, "n": 100, "p50_ms": 39.03, "p95_ms": 45.64, "p99_ms": 47.19, "max_ms": 48.69, "band": "DIAGNOSTIC-PASS", "seeded_jobs": 500}`.

**Not exercised by this smoke** (still unrun code): the other four `cells-diff` runs (parquet storage, 250 000 and 1 000 000 cells, the cell-threshold setting for parquet), the ratio line, and the `one-way`, `storage` and `profile` subcommands. The smoke also did not seed 10 000 Jobs; the cost of 500 Jobs through `jobs.transition` was not timed, so the seeding time of the full 10 000 is unknown (it writes two audit events per Job).

**Negative check of the wrapper's rc propagation** (no slot, no real docker: `PATH` points at a stub `docker` that exits 1, `scratch/sl1736/stub/docker`; log `smoke-negative.log`): `smoke.sh` failed at `createdb` after its 3 retries and the shell reported **`negative_wrapper_rc=1`**, with the last line `| exit | smoke_rc=unset |` (an early failure with no smoke rc exits 1). So the wrapper's rc is the script's own failure rc, not the last cleanup command's.

#### 2026-10-22 — timing smoke at `--seeded-jobs 10000` (head `83d6072d4448f4533025b838fee9d99a9d9bc9d9`, tree `c0a0dda78b9e4caa637ea3e2fd89b20f347631ad`): **timing-only observation, not an NFR reading**

GO: lead 26, "GO for one timing smoke at `--seeded-jobs 10000`". Command: `SMOKE_ARGS='--only rows-10000 --seeded-jobs 10000' SMOKE_TIMEOUT=2400 timeout 2600 flock -w 900 /tmp/slots/gate-1 bash ~/gi-pricing-plan.local/scratch/sl1736/smoke.sh`; the smoke itself ran under `timeout 2400`, which was not hit. **Smoke rc 0, wrapper rc 0.** Whole script 16:03:59 to 16:08:17 UTC (4 min 18 s); script-start load1 2.19. Logs: `scratch/sl1736/smoke-wrapper.log`, `smoke.out`, `smoke.err` (run 3's copies: `smoke-run3-wrapper.log`, `smoke-run3.out`, `smoke-run3.err`).

The seed phase, verbatim from the harness's own `seed-jobs` line in `smoke.out`: `{"reading": "seed-jobs", "label": null, "jobs": 10000, "started": "2026-10-22T16:04:05+00:00", "ended": "2026-10-22T16:08:09+00:00", "wall_s": 243.4, "load_start": 2.41, "load_end": 3.17}`. So **the 10 000-Job seed through `jobs.transition` took 243.4 s (4.1 min)**, load1 2.41 to 3.17, well under the 15 min line the lead set. Clean-up, verbatim: `| dropdb gipricing_sl1736_smoke (end) | rc=0 |`, `| redis db 1 FLUSHDB (end) | rc=0 |`, `| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |`, `| zeros | own-DB count=0 redis db 1 dbsize=0 |`, `| exit | smoke_rc=0 |`.

**Grant 4's budget:** the seed (about 4 min at this load) happens once per `cells-diff` invocation, before the five table runs, so it adds about 4 min to the derived 9.7 min window of `windows-sl1569-sl8035-2026-10-16.md` and is part of it unless the seed is moved outside the measured window. Proposed: keep it in one command and ask for about 20 min, since the seed does not time anything (the timed phase is the pages, after the seed) and moving it would need a second invocation that reuses the seeded workspace, which the harness does not support. The lead decides.

#### 2026-10-22 — the timing accepted; the settle guard; the Grant 4 request (head `a78051b031a931bb698c2d700f2bb3a2ed7f07a9`)

The lead accepted the timing smoke (seed `wall_s` 243.4, rc 0 = rc 0, zeros) and ordered the seed kept inside the window as one command. Non-measurement work done: (1) the harness now **settles load1 below 2.0 before each timed latency phase** (`NFR-468` per corpus, `NFR-1443` per run; wait up to 600 s outside the timed phase, else `STOP:` and no run), because PL-1735 Tasks 2 and 5 require the load "settled below 2.0 immediately before each run" and the harness only recorded it; `settle_load()` is pure and has four unit tests (already below, at the limit, falls below, gives up); `tests/test_measure_p2_nfr_sweep.py` now `46 passed in 0.32s` via `run-small.sh`, ruff, ruff format and mypy rc 0; commit `a78051b0`. This is a change to a harness not yet used for any reading, so it is not a post-run amendment. Its cost to Grant 4: a settle that waits is part of the window (the derivation counts 6 x 18.4 s). (2) The Grant 4 request is `~/gi-pricing-plan.local/scratch/sl1736/grant4-request.md`: one ALONE window of 20 min (seed 4.1 measured + five runs 9.7 derived + set-up and clean-up 2 estimated + 25 % margin), run capped at `timeout 1500`; the 250 000 and 1 000 000-cell set-up time of this harness is an estimate from LG-1444, and a `--only parquet-250000 --seeded-jobs 500` smoke is recommended before the window. Not done, awaiting a grant: tiny-size smokes of `one-way`, `storage` and `profile` (`profile` has no size override).

#### 2026-10-22 — disclosure: the harness runs the app's LIFESPAN, so every DB-lane run subscribes to the deployment switch (head `ce495ef2724ffe158c0d1441c30d49a798e2bf0d`)

Asked by the lead (FD-1838's gate is running), the answer from `scripts/measure-p2-nfr-sweep.py` at this head: the client is `httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://measure")` (`_Env.client`, :466-467), and the subcommands enter the app's lifespan explicitly: `async with env.app.router.lifespan_context(env.app), env.client() as client:` (`one-way` :578, `cells-diff` :841) and `async with env.app.router.lifespan_context(env.app):` (`storage` :715). `ASGITransport` does not run a lifespan by itself; the harness does, because the app's routes need its state (rate limiter, bundle slot). `backend/src/app/main.py:124-156` (the lifespan) builds `build_switch_client(settings.redis_url...)` and `RedisSwitch(switch_client, f"{environment}:{tenant_id}")` and subscribes. **So the harness is switch-touching:** Redis pub/sub channels are not scoped by database number, so `GIP_REDIS_URL=redis://localhost:6379/1` isolates keys but not the channel `gip:switch:<env>:<tenant>`; that is FD-1838's finding.

**What this means for the runs already made (this ledger's earlier entries):** smoke run 1 failed at an import, before the lifespan; **smoke runs 2 and 3 and the 10 000-Job timing smoke entered the lifespan**, so each subscribed to the switch channel of the default environment and tenant for its duration (run 2 about the seed phase; run 3 about 20 s; the timing smoke about 4 min 18 s, 16:03:59 to 16:08:17 UTC). Nothing published to the channel from the harness: it ran no deployment. Whether another process was disturbed is not established here; the lead had said to stop if the smoke touched the switch, and this was not known when those runs were requested. The next DB-lane run (the `parquet-250000` smoke) is therefore held for the gate's END unless the maintainer extends the overlap exception.

#### 2026-10-22 — the parquet-250000 DB-lane smoke (head `94ae36b785c160a8db5c6a6b4b531537595ae2eb`): ended rc 1 at the settle guard; **wiring test, not a reading**

GO: the lead's "GO now", on the maintainer's to-lead 17:12:17 with the switch conditions. Command: `SMOKE_ARGS='--only parquet-250000 --seeded-jobs 500' SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash ~/gi-pricing-plan.local/scratch/sl1736/smoke.sh`. Conditions applied (new lines in `smoke.sh`): `| GIP_GATE_SLOT | unset |`; `PUBSUB CHANNELS` and `NUMSUB` before (`2026-10-22T16:13:05+00:00`, `(channels listed: 1)`) and after (`2026-10-22T16:23:44+00:00`, `(channels listed: 1)`); the run `16:13:06Z` to `16:23:44Z`. Load1 at start 5.14 (other sessions' work). **Smoke rc 1, wrapper rc 1** (`| exit | smoke_rc=1 |`), so the wrapper's rc propagation holds on a real failure too. Cause, from the harness's own line: `{"settle": "NFR-1443 parquet-250000", "settled": false, "waited_s": 600.0, "load1": 4.18}` then `STOP: load1 4.18 not below 2.0 after 600.0 s before NFR-1443 parquet-250000; report to the lead (no run taken)`. That is the settle guard working as designed on a box at load 4 to 6; no switch-touching failure and no traceback. Clean-up verbatim: `| dropdb gipricing_sl1736_smoke (end) | rc=0 |`, `| redis db 1 FLUSHDB (end) | rc=0 |`, `| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |`, `| zeros | own-DB count=0 redis db 1 dbsize=0 |`. Logs: `scratch/sl1736/smoke-wrapper.log`, `smoke.out`, `smoke.err` (the timing smoke's copies: `smoke-timing-*`).

What it proved: the **parquet path through setup and the Job**: both versions `storage: parquet` at threshold 5 000 (the assertion passed), the first request 202, the Job `succeeded` with its artifact present (the guard that follows it ran before the settle). Timings from the script's own timestamps (whole seconds): 500-Job seed `wall_s` 12.0; table setup about 10 s; Job about 11 s (details and the 1M estimate in `grant4-request.md`, which is updated). The pages of the parquet path were **not** reached.

Commit `2ddf4537`: Task 1's red-first test added (`backend/tests/test_api_datasets.py`, `test_replacing_a_rule_set_is_audited_with_before_and_after`, `req("NFR-472")`), **committed before any run and before the fix**, so the red run to come is on this commit; the same commit carries a harness line `run-setup` that prints each run's setup and Job seconds. Task 1 has not been run.

#### 2026-10-22 — Task 1 (NFR-472), RED: red by its cause (head `c3d94b1779b0f98bceefee982bb0bbbe6b952fa2`, product code as at the test-only commit `2ddf4537`, no fix)

GO: the lead's "Task 1 GO now" under the maintainer's generalised exception (to-lead 17:23:23). Command: `STAGE=red SMOKE_TIMEOUT=1500 timeout 1700 bash ~/gi-pricing-plan.local/scratch/sl1736/task1.sh`, which creates its own database `gipricing_sl1736_t1` from the template, runs `alembic upgrade head` on it, and runs `scripts/run-small.sh <wt> backend/tests/test_api_datasets.py` (one file, the whole file; run-small's command line is fixed, so the new test cannot be selected alone). `| GIP_GATE_SLOT | unset |`; `PUBSUB CHANNELS` listed 1 channel before (2026-10-22T16:26:15+00:00) and after (16:26:54+00:00); run 16:26:15Z to 16:26:54Z; load1 3.51. Logs: `scratch/sl1736/task1-red-wrapper.log` (starts with the head and the `diff --stat origin/main...HEAD`), `task1-red.out`, `task1-red.err`. Wrapper rc 1 = pytest rc 1. Verbatim:

```
FAILED backend/tests/test_api_datasets.py::test_replacing_a_rule_set_is_audited_with_before_and_after
1 failed, 31 passed, 1 warning in 25.82s
>       assert v2.before == v1.after
E       AssertionError: assert None == {'version': 1, 'disabled': [], 'rule_ids': ['01a1646f-764c-779d-83f2-45732a5b6c6e'], 'overridden': {}}
E        +  where None = <app.db.models.AuditEventRow object at 0x7fb0bff1ec90>.before
backend/tests/test_api_datasets.py:248: AssertionError
```

This is the plan's expected red (Acceptance 1: `v2.before == v1.after` failing with `None` on its left, and on no other line); the 31 others pass. Clean-up verbatim: `| dropdb gipricing_sl1736_t1 (end) | rc=0 |`, `| redis db 1 FLUSHDB (end) | rc=0 |`, `| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |`, `| zeros | own-DB count=0 redis db 1 dbsize=0 |`, `| exit | smoke_rc=1 |`.

The fix, commit `c93ced5a47aa0b60cedaeeb49e4eb58616490591` (`backend/src/app/platform/validation_rules.py` only): a module-level `_audit_state(version, body)` builds both `before` and `after` from a stored rule-set body, and `replace_rule_set` loads the latest existing version (replacing the `max(version)` query: `version = 1 + latest.version`, same value) and passes `before=_audit_state(latest.version, latest.body)` (None for the first version) and `after=_audit_state(version, row.body)`. `after` has the same keys and values as before for the same input (ids as strings in member order, `disabled` the members with `enabled` false, `overridden` the severity overrides as their `.value`). ruff and mypy rc 0 on the file. GREEN is not yet run.

#### 2026-10-22 — Task 1 (NFR-472), GREEN (head `ef1d0efb04b5499ac21139bfa2aaf9827cd2a119`, fix `c93ced5a`)

GO: the lead's "GO for GREEN" (same exception, FD-1838's gate running on gate-1b). Same command as RED with `STAGE=green`; load1 4.93; run `2026-10-22T16:29:08+00:00` to `16:30:25+00:00`. Wrapper rc 0 = pytest rc 0. Verbatim: `| task1 green | rc=0 |`, `32 passed, 1 warning in 45.06s`, `| exit | smoke_rc=0 |`. This one run is GREEN for the new test and the FILE run of `backend/tests/test_api_datasets.py` in one (run-small runs the whole file): the 31 tests that passed at RED pass again, so the fix broke none of them. `| GIP_GATE_SLOT | unset |`. `PUBSUB CHANNELS`: 1 channel before (16:29:08Z); after (16:30:24Z) 8 channels, all `gip:switch:local:local:gate-1b:<env>` (`uat`, `env-c03ac6cb`, `env-c9c9b2a9`, `env-31a4732c`, `dev` numsub 0, `prod`, `env-07b5be16`, `env-f1318118`; numsub 1 each otherwise), the concurrent gate-1b run's channels, not channels this run published on; nothing failed, so there is no failure to read against the overlap. Clean-up verbatim: `| dropdb gipricing_sl1736_t1 (end) | rc=0 |`, `| redis db 1 FLUSHDB (end) | rc=0 |`, `| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |`, `| zeros | own-DB count=0 redis db 1 dbsize=0 |`. Logs: `scratch/sl1736/task1-green-wrapper.log`, `task1-green.out`, `task1-green.err`. Plan Acceptance 1 (red run before the fix on `v2.before == v1.after` with `None` on the left; green after) and 2 (`git grep -n 'req("NFR-472")' backend/tests/test_api_datasets.py` lists the new test) are met for Task 1; Task 1's step 5 commits are `2ddf4537` (test) and `c93ced5a` (fix). A planner (PL 8181, FD 8177) will sequence a separate fix around the route's scope-less `requires()` at `api/validation.py:68`; not this slice's.

#### 2026-10-22 — Grant 4: NFR-1443, the cells-diff page, DIAGNOSTIC reading (head `d235c8a69bf910baf28da95534c72157108cb0a3`, tree `fa26642d9198280582ad81758e8939f508f911e0`)

GO: the lead's "WINDOW OPEN", 2026-10-22T21:32:25Z, on the maintainer's approval of Grant 4 (to-lead 21:12:04), `grant4.sh` sha256 prefix `1692d6f1928a8630` (its diff against `smoke.sh` is `scratch/sl1736/grant4-vs-smoke.diff`, made by the lead). Command, foreground: `SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash ~/gi-pricing-plan.local/scratch/sl1736/grant4.sh`. **Wrapper rc 0 = run rc 0** (`| grant4 | rc=0 |`, `| exit | smoke_rc=0 |`); `2026-10-22T21:32:55+00:00` to `21:39:53+00:00`. Pre-guards from the log: gate-1b free, gate-2 free, `pgrep pytest|vitest` count 0, MemAvailable 23.7 GB, keycloak, minio, postgres and redis healthy, load1 0.90 at start, `| GIP_GATE_SLOT | unset |`, `PUBSUB CHANNELS` 1 channel before and after. Logs: `scratch/sl1736/grant4-wrapper.log`, `grant4.out`, `grant4.err`. Clean-up verbatim: `| dropdb gipricing_sl1736_smoke (end) | rc=0 |`, `| redis db 1 FLUSHDB (end) | rc=0 |`, `| bucket gip-test-blobs-gate-1 removed (end) | rc=0 |`, `| zeros | own-DB count=0 redis db 1 dbsize=0 |`.

**Reading.** Every figure is **server-side, in-process, excludes network** (DP-2), DIAGNOSTIC on the shared VM. page size (`limit`) 50, 10 000 seeded `rate_table.diff_cells` Jobs (seed `wall_s` 233.4, 21:33:02Z to 21:36:56Z), `near_bound_fraction` 0.43 (interim, P0 `157d327e`; Task 0's factor has not been measured), budget 300 ms, DP-1 bands (<= 129 ms DIAGNOSTIC-PASS, <= 300 ms NEAR-BOUND, above DIAGNOSTIC-OVER). Nearest-rank percentiles, one request at a time, load1 settled below 2.0 before each run (waited 15.0 s once, 0 s otherwise):

| Run | Storage | Cells | n | load1 (start, end) | p50 ms | p95 ms | p99 ms | max ms | cpu s | Band |
|---|---|---|---|---|---|---|---|---|---|---|
| rows-10000 | rows | 10000 | 100 | 1.61, 1.61 | 41.73 | 48.06 | 50.38 | 53.01 | 2.962 | DIAGNOSTIC-PASS |
| rows-250000 | rows | 250000 | 100 | 1.47, 1.35 | 41.60 | 47.72 | 49.50 | 51.99 | 2.975 | DIAGNOSTIC-PASS |
| parquet-10000 | parquet | 10000 | 100 | 1.35, 1.35 | 42.24 | 46.84 | 48.36 | 49.05 | 2.952 | DIAGNOSTIC-PASS |
| parquet-250000 | parquet | 250000 | 100 | 1.41, 1.46 | 41.30 | 48.04 | 50.46 | 58.05 | 2.897 | DIAGNOSTIC-PASS |
| parquet-1000000 | parquet | 1000000 | 100 | 1.37, 1.37 | 40.66 | 47.40 | 54.35 | 54.65 | 2.893 | DIAGNOSTIC-PASS |

The 2x property (`NFR-1443-ratio` lines, p95(250 000) / p95(10 000), bands 1.5 / 2.0): rows path **0.9929** DIAGNOSTIC-PASS; parquet path **1.0255** DIAGNOSTIC-PASS. Per-run set-up and Job time (the harness's own `run-setup` lines, replacing the estimates): rows-10000 1.9 s / 0.5 s; rows-250000 44.2 s / 12.4 s; parquet-10000 0.3 s / 0.2 s; parquet-250000 7.2 s / 6.3 s; parquet-1000000 32.0 s / 36.2 s. Each run asserted both versions' `storage`, the first request 202, and the Job `succeeded` with its artifact present before any page was timed.

**Band and next step:** all five page p95s (46.8 to 48.1 ms) and both ratios are DIAGNOSTIC-PASS; **none is NEAR-BOUND or OVER, so no named nfr-bench-1 session 2 extra reading and no `FD-` follows from NFR-1443** (DP-7 (a); the OVER section of PL-1735). **Caveat to carry (in the maintainer's terms, "2026-10-22 22:41:04 BST", Grant 4 ACCEPTED):** load1 at the timed phases was 1.35 to 1.61. That meets RL-1441's bar (< 2.0) but not D4's (< 1.0), so these readings are **DIAGNOSTIC (shared box, in-process), not the NFR verdict of record**. The plan's Acceptance 5 row for NFR-1443 is these lines. The NFR-1443 limb "on both storage paths" and "at 250 000 cells with both versions `storage: rows` and at 1 000 000 cells with both versions `storage: parquet`" are the `rows-250000` and `parquet-1000000` runs.

**The harness's own output lines, verbatim from `scratch/sl1736/grant4.out`** (the `seed-jobs`, `run-setup`, `settle` and `NFR-1443`/`NFR-1443-ratio` lines, in file order; the `session` block of each `NFR-1443` line is the host snapshot):

```
{"reading": "seed-jobs", "label": null, "jobs": 10000, "started": "2026-10-22T21:33:02+00:00", "ended": "2026-10-22T21:36:56+00:00", "wall_s": 233.4, "load_start": 0.99, "load_end": 2.17}
{"reading": "run-setup", "label": null, "run": "rows-10000", "cells": 10000, "setup_s": 1.9, "job_s": 0.5}
{"settle": "NFR-1443 rows-10000", "settled": true, "waited_s": 15.0, "load1": 1.61}
{"reading": "NFR-1443", "label": "server-side, in-process, excludes network", "run": "rows-10000", "storage": "rows", "cells": 10000, "limit": 50, "seeded_jobs": 10000, "load_before": 1.61, "load_after": 1.61, "cpu_s": 2.962, "band": "DIAGNOSTIC-PASS", "near_bound_fraction": 0.43, "session": {"head": "d235c8a69bf910baf28da95534c72157108cb0a3", "tree": "fa26642d9198280582ad81758e8939f508f911e0", "nproc": 8, "loadavg": "1.61 1.60 1.93 1/1064 781569", "meminfo_available_gb": 23.54, "pgrep": "774669 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774671 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774672 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh\n774673 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh", "at": "2026-10-22T21:37:17+00:00"}, "n": 100, "p50_ms": 41.733845, "p95_ms": 48.058407, "p99_ms": 50.376356, "max_ms": 53.009356}
{"reading": "run-setup", "label": null, "run": "rows-250000", "cells": 250000, "setup_s": 44.2, "job_s": 12.4}
{"settle": "NFR-1443 rows-250000", "settled": true, "waited_s": 0.0, "load1": 1.47}
{"reading": "NFR-1443", "label": "server-side, in-process, excludes network", "run": "rows-250000", "storage": "rows", "cells": 250000, "limit": 50, "seeded_jobs": 10000, "load_before": 1.47, "load_after": 1.35, "cpu_s": 2.975, "band": "DIAGNOSTIC-PASS", "near_bound_fraction": 0.43, "session": {"head": "d235c8a69bf910baf28da95534c72157108cb0a3", "tree": "fa26642d9198280582ad81758e8939f508f911e0", "nproc": 8, "loadavg": "1.35 1.55 1.89 1/1055 783058", "meminfo_available_gb": 23.37, "pgrep": "774669 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774671 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774672 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh\n774673 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh", "at": "2026-10-22T21:38:18+00:00"}, "n": 100, "p50_ms": 41.603795, "p95_ms": 47.719365, "p99_ms": 49.503977, "max_ms": 51.986436}
{"reading": "run-setup", "label": null, "run": "parquet-10000", "cells": 10000, "setup_s": 0.3, "job_s": 0.2}
{"settle": "NFR-1443 parquet-10000", "settled": true, "waited_s": 0.0, "load1": 1.35}
{"reading": "NFR-1443", "label": "server-side, in-process, excludes network", "run": "parquet-10000", "storage": "parquet", "cells": 10000, "limit": 50, "seeded_jobs": 10000, "load_before": 1.35, "load_after": 1.35, "cpu_s": 2.952, "band": "DIAGNOSTIC-PASS", "near_bound_fraction": 0.43, "session": {"head": "d235c8a69bf910baf28da95534c72157108cb0a3", "tree": "fa26642d9198280582ad81758e8939f508f911e0", "nproc": 8, "loadavg": "1.35 1.55 1.89 1/1090 783209", "meminfo_available_gb": 23.29, "pgrep": "774669 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774671 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774672 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh\n774673 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh", "at": "2026-10-22T21:38:23+00:00"}, "n": 100, "p50_ms": 42.241655, "p95_ms": 46.843745, "p99_ms": 48.358445, "max_ms": 49.047246}
{"reading": "run-setup", "label": null, "run": "parquet-250000", "cells": 250000, "setup_s": 7.2, "job_s": 6.3}
{"settle": "NFR-1443 parquet-250000", "settled": true, "waited_s": 0.0, "load1": 1.41}
{"reading": "NFR-1443", "label": "server-side, in-process, excludes network", "run": "parquet-250000", "storage": "parquet", "cells": 250000, "limit": 50, "seeded_jobs": 10000, "load_before": 1.41, "load_after": 1.46, "cpu_s": 2.897, "band": "DIAGNOSTIC-PASS", "near_bound_fraction": 0.43, "session": {"head": "d235c8a69bf910baf28da95534c72157108cb0a3", "tree": "fa26642d9198280582ad81758e8939f508f911e0", "nproc": 8, "loadavg": "1.46 1.56 1.89 1/1091 783587", "meminfo_available_gb": 23.06, "pgrep": "774669 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774671 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774672 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh\n774673 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh", "at": "2026-10-22T21:38:41+00:00"}, "n": 100, "p50_ms": 41.301584, "p95_ms": 48.038036, "p99_ms": 50.464406, "max_ms": 58.053386}
{"reading": "run-setup", "label": null, "run": "parquet-1000000", "cells": 1000000, "setup_s": 32.0, "job_s": 36.2}
{"settle": "NFR-1443 parquet-1000000", "settled": true, "waited_s": 0.0, "load1": 1.37}
{"reading": "NFR-1443", "label": "server-side, in-process, excludes network", "run": "parquet-1000000", "storage": "parquet", "cells": 1000000, "limit": 50, "seeded_jobs": 10000, "load_before": 1.37, "load_after": 1.37, "cpu_s": 2.893, "band": "DIAGNOSTIC-PASS", "near_bound_fraction": 0.43, "session": {"head": "d235c8a69bf910baf28da95534c72157108cb0a3", "tree": "fa26642d9198280582ad81758e8939f508f911e0", "nproc": 8, "loadavg": "1.37 1.51 1.84 1/1113 786014", "meminfo_available_gb": 23.12, "pgrep": "774669 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774671 /bin/bash -c source /home/puzhenhao1989/.claude/shell-snapshots/snapshot-bash-1792666504045-q55fkn.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && { \\builtin unalias -- 'unsetenv'; \\builtin unset -f -- 'unsetenv'; } >/dev/null 2>&1 || true && eval 'O=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; rm -f $O/grant4-wrapper.log; (SMOKE_TIMEOUT=1500 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash $O/grant4.sh > $O/grant4-wrapper.log 2>&1; echo wrapper_rc=$? >> $O/grant4-wrapper.log)' < /dev/null && pwd -P >| /tmp/claude-9d61-cwd\n774672 timeout 1700 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh\n774673 flock -w 900 /tmp/slots/gate-1 bash /home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736/grant4.sh", "at": "2026-10-22T21:39:53+00:00"}, "n": 100, "p50_ms": 40.655334, "p95_ms": 47.401086, "p99_ms": 54.349336, "max_ms": 54.645766}
{"reading": "NFR-1443-ratio", "label": "server-side, in-process, excludes network", "path": "rows", "ratio": 0.9929452093574388, "band": "DIAGNOSTIC-PASS"}
{"reading": "NFR-1443-ratio", "label": "server-side, in-process, excludes network", "path": "parquet", "ratio": 1.0254952075245052, "band": "DIAGNOSTIC-PASS"}
```

**Clause check: does anything in PL-1735 / SL-1736 need a verdict-of-record reading from this sweep? (executor's finding, 2026-10-22; the verdict on it is the lead's and the maintainer's.)** Checked, with what each says:

- `PL-1735` **Goal**: "one recorded **DIAGNOSTIC** reading on the shared VM in the slice's `LG-`" for each NFR; a NEAR-BOUND latency reading and NFR-485 at 5 M are "named extra readings" for nfr-bench-1's second session; "A reading that comes out OVER is reported to the lead for an `FD-`". No verdict of record is asked of the shared VM.
- `PL-1735` **DP-7 (a)** (ruled 2026-10-14 12:07:40): the shared-VM reading, taken in an RL-1441 quiet window with the load settled below 2.0 before each run, "is the reading, **unless it is NEAR-BOUND per DP-1**, when it joins nfr-bench-1 session 2 as a named extra reading". None of the five NFR-1443 runs is NEAR-BOUND (p95 46.8 to 48.1 ms against the 129 ms line; the factor-2.3 contention figure, 2.3 x 48.1 = 111 ms, is still below 129 ms), so the DP-7 (a) clause sends nothing to nfr-bench-1.
- `PL-1735` **DP-1** and the roadmap **G4** amendment of 2026-09-29: "No near-bound pass or fail is claimed from the shared VM" and the verdicts it names (F1, NFR-489, NFR-502, NFR-493's linearity limb, NFR-494) are carried to a dedicated host. NFR-1443 is not in that list, and no NFR-1443 reading is near-bound.
- `PL-1735` **Acceptance 5**: "each labelled DIAGNOSTIC". Met. **Acceptance 6** (an OVER is reported): none occurred.
- `PL-1735` **DP-4** and **Acceptance 7**: NFR-485's stated-scale (5 M x 60) reading is a verdict taken on nfr-bench-1 session 2, "one per arm", under `MemoryMax=30G`; the shared-VM curve is "a DIAGNOSTIC projection, never a verdict". **This is the one clause in this slice that needs a verdict-of-record reading, and it is not part of Grant 4.** It is already carried: the dated line under the nfr-bench-1 owner row in `docs/roadmap.md` (commit `cbcc6a97`, D2 placement) adds the two runs to session 2's list, and the LG's PLANNED section names their commands. nfr-bench-1 needs the user's notice of at least 2 h, which is the lead's.
- `PL-1735` **NFR-467's** 10 M run and **NFR-468 / NFR-470** readings: the shared VM holds them (guards in `NFR_467_RULE`); only a NEAR-BOUND latency reading or a failed guard moves one to nfr-bench-1. Not yet taken, so not yet decidable.
- **One open point for the lead/maintainer, not a PL-1735 clause:** roadmap G4 reads "Every P2 NFR is measured **on the exit tree** or carried with an owner". These readings are on this branch's tree (`d235c8a6`), not the exit tree. If G4's "measured" is to be satisfied for NFR-1443 by this reading, the exit tree must be measured again or the slice's tree stated as the measured one; otherwise it is carried with an owner. I do not decide it.

So, by the clauses checked: **no clause requires a verdict-of-record reading of NFR-1443 from this sweep, and none of the five readings sends a named extra reading to nfr-bench-1.** The sweep's nfr-bench-1 content is NFR-485's two 5 M runs (already carried) and any NEAR-BOUND readings the Tasks 2, 3, 5a and 4 windows may yet produce.

#### 2026-10-22 — the Grant 5 request written (head `8853f8fbf56e1618d711b326cdb70cc9bbe821e5` plus this entry); no runs

`~/gi-pricing-plan.local/scratch/sl1736/grant5-request.md`: three ALONE windows of 13, 14 and 17 min (44 min), each an A run of Task 0 plus one task (5a, 2, 4), with non-ALONE lanes for the generation prep (P1), Task 3 (L3) and the B runs; the ALONE bar of every window is D4's load1 < 1.0 at the A run, and the tasks after it are held to < 2.0 by the harness. Harness change committed for it (`8853f8fb`): `profile --mode generate-only|pregenerated` and a load1 < 2.0 settle before each profile size (the plan's Task 5a Step 3 asked for the settle; the first version had none). The unit-test file was **not** re-run for that commit (`run-small` refused at load1 6.47); the change is in `_profile`, which no unit test reaches; ruff passes. The freMTPL2 `.arff` files were copied into this worktree's git-ignored `examples/fremtpl2/data/` from the root checkout (needed by Tasks 2 and 3). No window script exists yet.

#### PLANNED — the four ALONE grants and their non-ALONE companions (not run; each grant is requested from the lead with these exact commands)

Common to every block. `W=/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1736`, `OUT=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736` (outside the repository; `mkdir -p $OUT`). The tree is the branch head at the grant (`git -C $W rev-parse HEAD`), which must be unchanged from the head named in the request. Every block starts by printing, and the seat quotes: `git -C $W rev-parse HEAD`, `cut -d" " -f1 /proc/loadavg`, `free -g`, `nproc`, `pgrep -af '[p]ytest|[v]itest|[f]lock'`, and `flock -n /tmp/slots/gate-1 true; echo $?` for both gate slots. A window starts only inside its conditions (seat brief item 15): load1 and available memory are read at the start and printed; above the limit the seat waits (re-check every 60 s, up to the D4 limit) or aborts and reports. Foreground, `timeout` on each stage, no detach (S-11, S-12).

**Grant 1, 2 and 3: one Task 0 ALONE run (A) each** (≤ 2.4 min + U_fix each; U_fix is `bench-model.py --only proposals`'s whole process, unmeasured). One block, repeated with `A1`, `A2`, `A3`:

```bash
W=/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1736
OUT=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; mkdir -p "$OUT"
git -C "$W" rev-parse HEAD; cut -d" " -f1 /proc/loadavg; free -g
flock -w 900 /tmp/slots/gate-1 -c "export GIP_GATE_SLOT=/tmp/slots/gate-1 LOKY_MAX_CPU_COUNT=2; \
  timeout 1200 uv run --directory $W python scripts/measure-p2-nfr-sweep.py \
    contention run --role A --out $OUT/contention.jsonl"; echo "rc=$?"
```

The `run` subcommand settles load1 below 1.0 for up to `ALONE_SETTLE_MAX_S` = 600 s, polling every 15 s (before the timed run, never during it). If it is still at or above 1.0 it prints `STOP: …` and exits 3 without running: **that is D4's stop to the lead**; the seat records the reading and ends its turn. A run that completes appends one JSON line (role, tree, load at start and end, wall, CPU, validity and reason) to `contention.jsonl`.

**Between grants: B runs (contended), outside any ALONE window** (the regime the sweep itself meets: load1 in [1.0, 2.0) at start and below 2.0 at end). They are measurements too, so each needs the lead's explicit OK when load1 is read to be in that range; they are not run on the seat's own initiative:

```bash
flock -w 900 /tmp/slots/gate-1 -c "export GIP_GATE_SLOT=/tmp/slots/gate-1 LOKY_MAX_CPU_COUNT=2; \
  timeout 1200 uv run --directory $W python scripts/measure-p2-nfr-sweep.py \
    contention run --role B --out $OUT/contention.jsonl"; echo "rc=$?"
```

A B run whose load1 is outside the regime is recorded as invalid and re-run (the file keeps it, with its reason). The order is A1, B1, A2, B2, A3, B3. After B3: `uv run --directory $W python scripts/measure-p2-nfr-sweep.py contention summarize $OUT/contention.jsonl` (no timing; rc 0 with the factor, band and spread, or rc 1 with fewer than 3 pairs). The seat quotes the whole file and the summary into this ledger, then commits **P1** (the band, if the factor landed and the lead or the maintainer rules it applies).

**Grant 4: Task 5, NFR-1443 cells-diff in an `RL-1441` quiet window** (≤ 9.7 min derived, 4.9 min measured at LG-1444). It needs its own database, bucket and Redis db, so the DB lane is part of the grant (seat brief items 15, 18, 22, 23):

```bash
W=/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1736
OUT=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1736; mkdir -p "$OUT"
DB=gipricing_sl1736; BUCKET=gip-blobs-sl1736
git -C "$W" rev-parse HEAD; cut -d" " -f1 /proc/loadavg; free -g
docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing "$DB"; echo "createdb rc=$?"
export GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/$DB"
uv run --directory "$W" alembic upgrade head; echo "alembic rc=$?"
# the timed window; load1 settled below 2.0 before each run is printed by the subcommand
flock -w 900 /tmp/slots/gate-1 -c "export GIP_GATE_SLOT=/tmp/slots/gate-1 LOKY_MAX_CPU_COUNT=2 \
    GIP_DATABASE_URL=$GIP_DATABASE_URL GIP_REDIS_URL=redis://localhost:6379/1 GIP_BLOB_BUCKET=$BUCKET; \
  timeout 1500 uv run --directory $W python scripts/measure-p2-nfr-sweep.py cells-diff" \
  > "$OUT/cells-diff.jsonl" 2> "$OUT/cells-diff.err"; echo "rc=$?"
# cleanup, then the quoted zeros (items 18, 22, 23)
docker exec gi-pricing-redis-1 redis-cli -n 1 flushdb
docker exec gi-pricing-minio-1 sh -c 'mc alias set g http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null && mc rb --force g/'"$BUCKET"; docker exec gi-pricing-minio-1 mc ls g/
docker exec gi-pricing-postgres-1 dropdb -U gipricing "$DB"
docker exec gi-pricing-redis-1 redis-cli -n 1 dbsize
docker exec gi-pricing-postgres-1 psql -U gipricing -Atc "select count(*) from pg_database where datname = '$DB'"
```

**Grant 4's Redis, MinIO and database lines are superseded (2026-10-22, lead 26's rule).** The block above is the first draft and its Redis db, MinIO alias and bucket removal were guesses. The corrected lines are in `~/gi-pricing-plan.local/scratch/sl1736/smoke.sh`, where `rmb()` and `mkdb()` are copied verbatim from `scratch/gate-template-demostop.sh:30` and `:32`, the Redis db is the gate-1 pytest db (`RT=1`, with the never-db-0 guard of `:22-:24`), the bucket is `gip-test-blobs-gate-1` (`:28`), and the end block and zeros line follow `:47-:51`. Grant 4 is that script with the `cells-diff` arguments changed to the full five runs (no `--only`, default `--seeded-jobs`), in the ALONE window. The smoke is the same script with `--only rows-10000 --seeded-jobs 500` and is not a reading.

**Before Grant 4 the executor reads and corrects this block against `scratch/gate-template-demostop.sh`** (the Redis db number, the MinIO alias line and the bucket-removal call are copied from it, item 18), and reports any change as a delta. The `cells-diff` subcommand has never been run: **its first execution is a smoke at `--only rows-10000 --seeded-jobs 500`** inside a non-ALONE DB lane the lead grants, so that wiring errors (a helper's signature, the Job shape the seeded rows need) cost minutes of a smoke and not the quiet window. That smoke is not a reading and is not recorded as one.

**Owed, not in these four grants** (gate-1 windows of the plan, not ALONE): Task 2 `one-way` (≤ 6.7 min + U_gen), Task 3 `storage` (≤ 1.7 min), Task 4's shared-VM `--peak hwm` curve (≤ 7.7 min + 6 × U_build), Task 5a `profile` (≤ 6.9 min + generation; guards MemAvailable ≥ 16 GB, disk ≥ 12 GB; `--tmpdir` the job's directory, never `/tmp`). Their exact commands are written when the lead grants those windows. Also owed: Task 1 (the NFR-472 red-first test and fix, a DB lane), and the checks the phase restriction deferred: `ruff check .`, `ruff format --check` on the changed files, `uv run mypy`, `tests/test_measure_p2_nfr_sweep.py` through `scripts/run-small.sh`, `python3 scripts/audit-docs.py` and `doc-index.py` (INDEX regeneration for the new ledger and the status changes), `python3 scripts/idsweep` (seat brief item 26).

## PRs

None yet.
