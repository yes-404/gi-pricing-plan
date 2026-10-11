---
id: LG-9932
family: ledger
title: WK-1178 slice SL-1455 — NFR-489, the /score request path meets its p99 budget at 25 to 200 rps (PL-1454 slice ledger)
status: active
created: 2026-10-11
owner: executor
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-1178
slice: SL-1455
plans: [PL-1454]
corrected_by: []
relates: [PL-1454, FD-1411, SL-1259, RL-1263, RL-921, RL-1379, NFR-489]
---

# LG-9932 — WK-1178 slice SL-1455: the NFR-489 remedy for `/score`

*(LG-9932 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1455` from PL-1454, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`. Times are
BST (`TZ=Europe/London date`) unless marked. **This ledger covers Task 0 only** (the GO is "Task 0 only");
Tasks 1–6 wait on the DP-1…DP-4 ruling from Task 0's record.

**GO:** `to-lead.md` "2026-10-10 21:38:39 BST — DISPATCH GO: SL-1455 (Task 0; FD-1411's NFR-489 HTTP remedy) and WK-674 S3 (PL-1583); OP-1455-M1/M2/M3; the register :293 record", item 1: "GO SL-1455, Task 0 only (attribution, no fix). Tasks 1–6 wait on DP-1…DP-4, ruled from Task 0's record (need 5). Need 4: Task 0 re-derives bench-rating.py's cites and the model_call scoring path at its base, quoted in the record." Item 5: "MEASUREMENT WINDOW (need 3): the lead owns it. The sweep runs ALONE: both slots, no gate, no SL-1526 proving run, no migrate --verify. Task 0's own timing runs need the same. Book it in eta, with its start and end stamps in the LG." Corrected for Task 4 only by "2026-10-11 11:02:35 BST — DP-S5-a RULED (a) …" item 2 (SL-1455's Task 4 is the FD-1411 remedy proof; the NFR-489 exit verdict is SL-1259's). The timings are DIAGNOSTIC on this box: "2026-10-11 10:57:16 BST" item 3.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1454` (leaf plan, WK-1178), roadmap row `SL-1455` — "WK-1178 fix slice — NFR-489: the /score request path meets its p99 budget at 25 to 200 rps". Requirements: `03` NFR-489, `00` NFR-454 (held by the same measurement); preserved, not built: NFR-497, FR-243, FR-259; FR-268 not built. This ledger's part: PL-1454 Task 0 (attribution, no committed code) and Acceptance 1.

### Task list

- [x] Task 0, Step 0 — need 4 re-derived at the base (Build log).
- [x] Task 0, Steps 1–5 — AUTHORED as scratch scripts under `~/gi-pricing-plan.local/scratch/sl1455-t0/` (not in the repository; Task 0 commits "nothing but its ledger"). **Not run.**
- [x] Task 0, Steps 1, 3, 3b, 4 — the timings: RUN in the ALONE window 2026-10-11 23:41:11 – 2026-10-12 00:14:49 BST (Build log, last entry).
- [ ] Task 0, Step 5 — the tabulation: `results.md` is generated (path in the last Build log entry); the one-line (i)–(iii) statements and any rerun are the lead's ruling (asyncio debug mode swamps the run).
- [ ] Task 0, Step 6 — STOP; hand to the lead for DP-1…DP-4.
- Tasks 1–6 — not started (need 5).

### Gate

Not applicable to Task 0 (no code is committed). The two-half gate is Task 5's.

### Audit

(the auditor's)

### Build log

- **2026-10-11 11:2x — base and set-up.** Worktree `.claude/worktrees/sl-1455`, branch `sl-1455-wk1178-nfr489-http`, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7` (`git -C <wt> rev-parse HEAD` at creation); `uv sync --all-packages` ok. No ref matched the slice before (the planner's draft, `go-request-sl1455-2026-10-10.md` §1).
- **Task 0 Step 0 — need 4 re-derived at `d699a561`** (`git -C <wt> diff --name-only 47d770e8 origin/main -- backend/src/app/api/score.py backend/src/app/api/deps.py backend/src/app/api/authz.py backend/src/app/auth/service.py backend/src/app/db/session.py backend/src/app/main.py backend/src/app/platform/bundle_slot.py scripts/bench-rating.py` prints `backend/src/app/main.py` and `scripts/bench-rating.py`).
  - `main.py`: the diff is two added lines, the `dislocation_runs` import and `app.include_router(dislocation_runs.router, prefix=API_PREFIX)`; the lifespan and the slot construction are untouched. `score.py`, `deps.py`, `authz.py`, `auth/service.py`, `db/session.py` and `bundle_slot.py` are byte-identical to `47d770e8`.
  - `scripts/bench-rating.py` cites, PL-1454's line → the line at `d699a561` (each read at the line): `_ctx` `:1084` → `:473`; `QuoteContextOptions(rating_version_ref=_RATING_VERSION_REF)` `:347` → `:484` (the constant `:82`); the "every request pays this" label `:1075` → `:1253`; `_measure_fetch` (with its fresh `BundleSlot()` per call) `:709-722` → `:812-865` (`BundleSlot()` at `:851` and `:858`; its comment "a shared one would turn every call after the first into a hit" `:847`); the docstring claiming every request pays the miss `:678-688` → `:815-824`; `_serve` `:729-758` → `:866-896`; `Rung.implied_ceiling_rps` `:564-575` → `:701`; `_drive` `:776` → `:913` (`httpx.Limits(max_connections=1024…)` `:935`, `timeout=60.0` `:936`); the API key scoped to `uat` `:645-653` → `generate_key("uat")` `:784`, `environments=["uat"]` `:790`; `_seed` `:715`; the HTTP sweep `_run_http_sweep` `:1216`. The `--http` flow, the discarded 4 s warm-up rung at 25 rps, one server per GBM condition and the per-rung `_handler_ms` read are as the plan describes.
  - `score.py` handler cites (unchanged): `score` `:351`, `_serving_ref` `:169`, `_fetch_bundle` `:207`, `_maybe_sample_trace` `:464`, sampling resolve `:485`; `require_caller` `deps.py:201` with `unit_of_work` + `authenticate_api_key` at `:238-239`; `requires` `authz.py:54`; `Database.__init__` `db/session.py:40` (`pool_pre_ping=True`, no pool arguments).
  - **The `model_call` scoring path at the base** (the GO's second clause; A-2/A-3 changed it since FD-1411's tree): `score_one` `packages/pricing-core/src/pricing_core/rating/score.py:919` evaluates through `bundle.decision.async_evaluate(context, {"trace": trace})` (`:961`) with no I/O (NFR-491); each `model_call` step is a `customNode` (`runtime.py:440-454`) whose handler `_model_call_handler` (`runtime.py:712`) calls the one per-kind dispatch `_predict_model` (`runtime.py:594`): xgboost/lightgbm go to `predict_gbm(…, nthread=1)` (`:626`), a GLM to `glm_scorers[ref].predict(feature_row)` (`:628-629`), anything else is a `_ModelCallRefusal` (`:630`); a Peril Structure's components use the same dispatch (`:605-606`). `runtime.py` and `score.py` both changed since `47d770e8` (A-2, A-3), so Task 0's table re-baselines `score_one`'s share rather than reusing FD-1411's 11.3 / 7.8 ms.
- **Surprise found while authoring Step 3b (reported to the lead; no code touched).** `score()` (`backend/src/app/api/score.py:351-375`) passes the request's `ctx` to `score_one` unchanged after `_serving_ref` has resolved the live ref, and `score_one` refuses a `ctx` whose `options.rating_version_ref` is `None` with `INPUT_CONTRACT_VIOLATION` (`score.py:945-950` in pricing-core: "ctx.options.rating_version_ref is required — Slice 1 builds no default-live resolution"). The default-live tests (`backend/tests/test_score.py:1379` ff.) replace `score_one` with a stub that records the ref, so they do not exercise this. Read, not run: the default-live arm of Step 3b may answer 4xx on `main`. The driver therefore sends ONE untimed probe request per live arm against `main`'s handler unchanged (`T0_FILL_REF=0`) and records the answer, and the timed live passes run with the instrument injecting the resolved ref before `score_one` (`T0_FILL_REF=1`) — the path a corrected handler would run — each request recording `ref_filled`.
- **Task 0 Steps 1–5 authored — deviations from the plan's text, none changing what is attributed:**
  1. **Instruments are out-of-tree.** Step 2 describes a scratch patch to `score.py`, `deps.py`, `authz.py` and `session.py`. `t0_app.py` wraps the same functions at import time of the server process (`PYTHONPATH=<scratch> python -m uvicorn t0_app:create_app --factory`), so the repository is not edited and no second worktree is needed: this slice's worktree has the base's `backend/`, `packages/` and `scripts/` trees, which `run.sh` checks (HEAD guard: `git rev-parse HEAD:backend` = `b1619a4fb23b3a629c1b8cc8bb93e72039fb9a93`, `:packages` = `992973090a2b48e8a76eeda47934358349152ed6`, `:scripts` = `6a3e9185d3396863d6ee50186eb9df6e72481df3`, and those paths clean).
  2. **Phases timed:** `auth` (`authenticate_api_key`), `auth_scope` (the whole `unit_of_work`, commit included), `rbac` (`require_permission`), `rbac_scope`, `serving_ref`, `fetch_bundle`, `compiled_for`, `score_one`, `sample_trace`, `serialise` (`ScoringResult.model_dump_json`), `total`. Pool: `_ConnectionFairy._checkout` (includes `pool_pre_ping`) count, summed and longest milliseconds; statements and commits by SQLAlchemy engine events; slot hit/miss by wrapping `BundleSlot.get`; `gc.callbacks`; a 10 ms event-loop ticker recording overshoots of 50 ms or more; `PYTHONASYNCIODEBUG=1` with `slow_callback_duration = 0.05` (those lines land in the per-pass `server.log`).
  3. **py-spy's output is `--format raw`** (collapsed stacks; the analyser computes top frames by self time) rather than an SVG; Step 4's only exit stays as written: if `uvx py-spy --version` fails the script prints the error and skips the profile passes.
  4. **Passes:** four arms (`bench-gbm`, `bench-nogbm`, `live-gbm`, `live-nogbm` — Step 3b's default-live arm in both GBM conditions, seeded with a `uat` `DeploymentRow` in the scratch database only) × {25, 50} rps × 3 runs, each on a fresh server (cold slot) after the bench's discarded warm-up rung, plus one py-spy pass per arm at 25 rps: 24 + 4 passes, about 25–30 minutes.
- **The ALONE run, for the lead to book** (nothing on the box but the lead's held `gate-1`, `gate-2`, `small-test`): `bash ~/gi-pricing-plan.local/scratch/sl1455-t0/run.sh` — foreground, internal `timeout 5400`; it checks the head guard, `pgrep` for pytest/vitest (refuses if any, `T0_ALLOW_BUSY=1` for a rehearsal), records `uptime`, slot state and `df` at both ends, creates and drops a uniquely named scratch database (`createdb -T gipricing`, records the template's alembic version `e5b7d9f1a3c6` against the tree head `b8d2f4a6c0e1`, then `alembic upgrade head`), runs `t0_driver.py`, and writes `results.md` with `t0_analyse.py`. Subsets for a rehearsal: `T0_ARMS=… T0_RATES=… T0_RUNS=…`.
- **Not run yet, by design:** no instrument, driver or analyser has been run end to end. Checked statically: `bash -n`, `py_compile`; `t0_app.create_app()` imports and applies every patch against this tree (no server, no database); `t0_analyse.py` run on a hand-made fake tree. Untested until the window: the server start under the wrappers, the Step 3b seed, py-spy attach, and the pass-to-pass port reuse.
- **Barred word:** `git -C <wt> diff origin/main...HEAD | grep '^+' | grep -ciE 'dep''uty'` → 0 at the commit.
- **The ALONE run, 2026-10-11 23:41:11 – 2026-10-12 00:14:49 BST (diagnostic attribution, not an NFR-489 reading).** The lead's ALONE WINDOW OPEN is from-lead "2026-10-11 23:40:50 BST"; the wrapper was `flock -w 7200 /tmp/slots/gate-1 flock -w 600 /tmp/slots/gate-2 flock -w 600 /tmp/slots/small-test timeout 5700 bash ~/gi-pricing-plan.local/scratch/sl1455-t0/run.sh`, exit 0, `end 2026-10-12T00:14:49+01:00 rc=0`, driver rc 0, analyse rc 0.
  - **Objects.** Slice COMMIT `47cf560426a78f079a3fdf57cb935224dfd5ebcc` (parents slice `b00cde5e` and `origin/main` COMMIT `372fa92ae3ab306bc067c234487ce929dc0e2a04`; the head was pinned, not re-merged, by the lead's ruling). Pre-registered evidence COMMIT `c41475c2cae267bddf1e40dfe3ff654353eb518c` on `evidence/sl-1455-t0-2026-10-11` (parent `d87e354d`); blobs under `evidence/sl-1455-t0/`: `run.sh` `8b434dcb`, `t0_app.py` `cd6f6e69`, `t0_driver.py` `8991de25`, `t0_analyse.py` `37d7fe4f`; `run.sh` step 0 printed `prereg ok` for all four (byte-identical to the blobs) and the preflight printed `PREFLIGHT ok`. Earlier evidence commit `d87e354d` (t0_analyse.py blob `511c1e71`) was superseded before the run.
  - **Where.** Results: `~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261011T234111/results.md`; the log `~/gi-pricing-plan.local/scratch/sl1455-t0/wrapper-2026-10-11.out`; per-pass START/END (Europe/London) and steal in that log and in each pass's `client.json`. Not in the repository.
  - **Passes.** 28: 4 arms x {25, 50} rps x 3 runs, plus one 25 rps py-spy pass per arm. Per-pass `/proc/stat` steal 0.23% – 1.21% (highest: `live-gbm` 50 rps run1 1.20%, `live-gbm` py-spy 1.21%, `live-nogbm` py-spy 0.88%). Load average 3.36 at the start, 2.06 at the end. Probes (main's handler, no ref in the body) on both live arms: HTTP 200 `quoted`.
  - **Co-tenant.** Another seat's `gh run list` CI poller ran during the window (from-lead "2026-10-12 00:00:41 BST": about 118% CPU per poll, probably from about 23:41, stopped by the lead). It is in-guest CPU, so steal does not show it. Note: `out-20261011T234111/CO-TENANT-NOTE.md`. `bench-gbm` 25 rps run1 (23:41:29 – 23:42:48, the first pass) is the one pass that stands apart from its siblings (26 errors, client p99 48.7 s against 32.0 s and 30.1 s for runs 2 and 3) and may be disturbed; no other pass is separable.
  - **What the run shows (server-side request ms, p50 / p99, pooled):** total `bench-gbm` 25 rps 20338 / 46779, 50 rps 42251 / 59056; `bench-nogbm` 12477 / 24755, 38307 / 54517; `live-gbm` 17306 / 32532, 43393 / 61236; `live-nogbm` 16429 / 29036, 42110 / 58873. `score_one` p50 / p99 23–35 / 38–70 ms (max 839). Every request: 6 pool checkouts, 10 statements, 2 commits (p50); checkout wait p99 24–60 s, longest single 21–30 s. `rate_limit` (new, #1280) p50 1.5–3.3 s at 25 rps and 8.9–10.9 s at 50 rps, the largest p50 of the phases in every cell, and one of the 6 checkouts. Slot hits = all requests, misses 0 in the measured window. GC gen2 longest 420–937 ms; loop stalls of 50 ms or more: 16–71 per cell, longest 430–960 ms. Errors at 50 rps: 135–314 of about 1000 per pass.
  - **py-spy (3 of 4 passes usable; the `live-gbm` pass returned n=0, errors=500):** top self-time frames are `linecache.checkcache` 14.6–18%, `traceback` frame extraction (`traceback.__init__`, `walk_stack`, `_extract_from_extended_frame_gen`) about 15–20% together, `asyncio/runners.run`; `asyncpg execute` about 1%.
  - **Reading, the executor's and unruled.** Asyncio debug mode (Step 2 of the plan) records a stack for every Task and Future, and is the dominant cost in the profiles; the run is a saturated, instrumented process, so it does not give the un-instrumented per-request cost, the stall's cause (Step 5 (ii): unattributed) or whether one process serves 200 rps (iii: not answerable). Structural facts that do not depend on timing: 6 checkouts, 10 statements and 2 commits per scored request; `score_one` is about 25–35 ms; the slot is hit every time; the result does not depend on the GBM; default-live does the same per-request work as the bench path. Recommended to the lead: one more ALONE pass at 25 rps x3 on the two bench arms with asyncio debug mode off (about 12 minutes, a new pre-registered evidence commit). Awaiting the lead's ruling.

## PRs

(none yet; Task 0 is not a PR on its own — the slice's one PR carries this ledger at the slice's end.)
