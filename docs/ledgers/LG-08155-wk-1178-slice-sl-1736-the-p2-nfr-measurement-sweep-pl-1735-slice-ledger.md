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
