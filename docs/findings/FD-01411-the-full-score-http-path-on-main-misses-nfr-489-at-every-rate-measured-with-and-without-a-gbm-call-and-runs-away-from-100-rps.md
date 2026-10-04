---
id: FD-1411
family: finding
title: The full /score HTTP path on main misses NFR-489 at every rate measured, with and without a GBM call, and runs away from 100 rps
status: active
created: 2026-10-04
owner: auditor
tree: 4eb1364428a2861fbc8014957e89924f631dd1ff
corrected_by: []
relates: [WK-674, WK-1178, SL-1259, NFR-489, NFR-454, NFR-490, RL-921, RL-1263, LG-1405, PL-1237]
---

# FD-1411 — the full `/score` HTTP path misses NFR-489 at 25, 50, 100 and 200 rps

**Filed** by auditor-fd489 on the lead's order of 2026-10-04 (`to-lead.md`, the entry headed
"2026-10-04 19:18:54 BST — NFR-489 ON MAIN (c08a48e5, uncontended): the FD is FILED NOW at severity
HIGH, not in the batch; its remedy is pulled forward ahead of other WK-1178 items; the no-GBM anomaly is
re-measured", amended by the entry of 19:42:49 BST). Working id 9729, minted as FD-1411 on 2026-10-04. **Every
figure below is copied from the measurement record `nfr489-main-baseline-2026-10-04.md`** (a local
handover file, not in the repository) and from `LG-1405` Task 7; **no benchmark was run for this finding.**
`tree:` is `origin/main` at filing; the measurements ran on `c08a48e5de4b48929e979361105eff49ddeb3df4`
(first table) and `4eb1364428a2861fbc8014957e89924f631dd1ff` (re-run), and
`git diff --stat c08a48e5 4eb13644 -- backend packages scripts` was empty (the record's statement).

## Finding

**Severity HIGH** (the deputy's, confirmed by the lead on main). A P2 NFR fails by 2× to 70× at the rates
measured. It is not CRITICAL: no correctness or security is lost, and the journey still functions.
**Owner of the measurement: SL-1259** (WK-674 Slice 5, `docs/roadmap.md`, `#### SL-1259`, whose title lists
NFR-489). **Remedy: a WK-1178 leaf plan (PL 9728, working id), dispatched on lane B after the FD-1356 fix**,
whose acceptance is NFR-489's own predicate at 25, 50, 100 and 200 rps with at least three runs per rate.

**The predicate.** `docs/specs/03-rating-engine.md:1330` (at `4eb13644`), no dated amendment on the row:

> "| **NFR-489** | Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call (NFR-454). Without a GBM call, p99 < 15 ms. |"

(`LG-1405` Task 7 cites the same row at `:1258`, a line at an earlier tree.) The harness budgets are
`BUDGET_WITH_GBM_P99_MS=50` and `BUDGET_WITHOUT_GBM_P99_MS=15`.

**What was measured is the path the exit demo scores through.** The lead's order states that the exit
demo's scoring path is the one measured: the `/score` route end to end (auth, bundle fetch, `score_one`,
response) behind a single uvicorn process. Roadmap G2 (`docs/roadmap.md`, "**G2.**") ends the demo at a
served page after deployment to `uat` and `prod`. I did not trace the demo's calls to the route myself. **The exit demo is therefore "at risk, untraced"**: PL 9728 (working id)'s Task 0 traces the demo's `/score` calls.

**The component half passes; the HTTP half does not.** `score_one` alone: p99 11.329 ms against 50 with
a GBM call, 7.758 ms against 15 without (the record, same invocation as the 25 rps pass). `LG-1405` Task 7
measured the same split at an earlier head: 10.964 / 9.634 ms. The over-budget figures therefore belong to the
route path, not the evaluator.

## Evidence

### Replica and client configuration (quoted from the record)

- Server: one process, no `--workers`: `uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --log-level warning --no-access-log` (`_serve`, "one replica"); each arm gets its own server.
- DB pool: `create_async_engine(url, pool_pre_ping=True, hide_parameters=True, future=True)`, no `pool_size` or `max_overflow`, so SQLAlchemy's defaults, 5 plus 10 overflow.
- Client: open loop on the clock (`_drive`), `httpx.Limits(max_connections=1024, max_keepalive_connections=1024)`, timeout 60 s. Rung 20 s, 4 s discarded warmup at 25 rps.
- Command, one rate per invocation: `GIP_TEST_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_wt-perf489_c9aad119 timeout 1500 uv run --directory $W python $W/scripts/bench-rating.py --http --rates R --port 8000`, R in 25, 50, 100, 200 (scratch database cloned with `createdb -T`, migrated, dropped after).

### First pass, tree `c08a48e5`, one run per rate (p99 is client-side from the open-loop generator; "handler" is the server log)

| rate | arm | issued rps | p50 ms | p99 ms | budget | handler p99 | errors | verdict |
|---|---|---|---|---|---|---|---|---|
| 25 | GBM | 25.0 | 47.4 | 112.9 | 50 | 106.0 | 0 | OVER |
| 25 | no GBM | 25.0 | 67.2 | 1017.5 | 15 | 887.9 | 0 | OVER |
| 50 | GBM | 50.0 | 2126.5 | 6846.0 | 50 | 6826.4 | 0 | OVER |
| 50 | no GBM | 50.0 | 65.5 | 934.1 | 15 | 801.7 | 0 | OVER |
| 100 | GBM | 81.5 | 21666.9 | 39043.2 | 50 | 23052.1 | 5 | OVER, runaway |
| 100 | no GBM | 80.4 | 18532.5 | 32872.2 | 15 | 18782.0 | 1 | OVER, runaway |
| 200 | GBM | 64.2 | 311290.2 | 334860.4 | 50 | 21842.9 | 1721 of 2279 | OVER, runaway (generator behind; void rung per the harness) |
| 200 | no GBM | 53.2 | 335289.4 | 565497.2 | 15 | 17110.1 | 2074 of 1926 | OVER, runaway |

At 100 and 200 rps, in both arms, the issued rate stays under the offered rate and the queue grows. At 200
the error count exceeds `n`. The 200 rps pass took 18 min 16 s inside the 1500 s bound. **This is a
saturation finding: the single process sustains roughly 15 to 38 rps by the record's reading.**

### Per-pass times and load (UTC, London is +1 h BST; `uptime` 1-min load; `pgrep` count of competing processes was 0 at every start and end)

| pass | start UTC | end UTC | load at start | load at end |
|---|---|---|---|---|
| 25 rps | 17:44:55 | 17:48:57 | 0.66 | 2.71 |
| 50 rps | 17:49:01 | 17:52:55 | 2.57 | 1.70 |
| 100 rps | 17:52:57 | 17:57:37 | 1.70 | 2.84 |
| 200 rps | 17:57:39 | 18:15:55 | 2.69 | 1.75 |

Load inside the harness never exceeded 2.9 on the 8-vCPU box, nothing else ran (the 2.57 at the 50 rps start
is the 25 rps pass's tail), so contention does not explain the result. Raw output: `/tmp/perf489_out_{25,50,100,200}.txt`.

### `_fetch_bundle` is paid by every request

Measured alone, 200 sequential calls (the record): with a GBM call mean 78.0 ms (p99 92.3); without a GBM call
mean 33.9 ms (p50 30.7, p99 342.7). Every request pays it. **Leading suspect, not proven:** the bundle is
fetched or deserialised on each request, and the `BundleSlot` memo does not take effect across requests on
this path. Task 0 of the remedy plan tests it. The attribution is a side measurement (`_measure_fetch`), not
a profile of the served request.

### The first no-GBM figure (1017.5 ms at 25 rps) did not reproduce

In the first pass the no-GBM arm was slower than the GBM arm at 25 rps (p99 1017.5 against 112.9), which
cannot be a property of removing work. The lead ordered three repeats on a quiet box. Tree `4eb13644`,
`--rates 25`, same command form, runs started 18:20:10, 18:23:57 and 18:27:37 UTC, load 0.36 to 1.71 at the
pass boundaries, nothing else running (record, "Re-run ×3"). The HTTP rung prints mean, p50 and p99 only, not
p95 or max.

| run | arm | mean | p50 | p99 client | handler p99 | n | err | fetch alone p50 / p99 / max |
|---|---|---|---|---|---|---|---|---|
| 1 | GBM | 40.1 | 39.1 | 55.7 | 51.9 | 500 | 0 | 75.1 / 86.3 / 90.7 |
| 1 | no GBM | 38.2 | 36.7 | 67.0 | 60.6 | 500 | 0 | 18.4 / 227.1 / 240.5 |
| 2 | GBM | 38.4 | 37.3 | 58.2 | 54.9 | 500 | 0 | 72.0 / 253.0 / 268.7 |
| 2 | no GBM | 42.8 | 36.3 | 323.6 | 320.4 | 500 | 0 | 17.9 / 23.6 / 210.1 |
| 3 | GBM | 52.0 | 51.7 | 76.8 | 72.3 | 500 | 0 | 79.3 / 99.8 / 296.6 |
| 3 | no GBM | 45.2 | 44.1 | 63.7 | 58.6 | 500 | 0 | 21.3 / 234.2 / 236.7 |

- **The 1017.5 ms tail does not reproduce:** the no-GBM p99s are 67.0, 323.6 and 63.7 ms. All six runs are over
  budget (50 and 15 ms) regardless. No-GBM p99 exceeds GBM p99 in runs 1 and 2 and is below it in run 3, so
  there is no systematic inversion. The inversion in the first table was a single-rung tail, not a property
  of the arm. One run per rate cannot establish a no-GBM figure.
- **Stalls of about 200 to 300 ms appear in both arms.** In 5 of 6 `_fetch_bundle` blocks a single outlier of
  about 210 to 297 ms appears (max about 10 to 13 times the p50). In run 2's no-GBM rung the client p99 was
  323.6 ms with handler p99 320.4 ms and queue plus loopback only 3.2 ms, so the delay is inside the server
  handler, not in the generator or loopback.
- **Cause of the stalls: unproven inference.** The record suggests a periodic stall independent of the GBM
  (garbage collection, a connection open or `pool_pre_ping` reconnect, or a storage-blob read). The harness
  prints nothing that identifies the cause, and the output does not show where in each 200-call block the
  outlier falls. Task 0 of the remedy plan must attribute them before a fix is chosen.
- Mean latency also shifts run to run (run 3 about 10 ms higher in both arms): a load or noise factor, not a
  bundle factor.

### Earlier measurement, `LG-1405` Task 7 (WK-674 Slice 2, head `4304748898ed56b8db29f5a2c2ef7f1c2f47c544`)

At 25 rps the full HTTP path was over budget in most runs with and without the Deployment read: with a GBM
call p99 45.3 to 59.1 ms (budget 50); without a GBM call 45.2 to 71.2 ms (budget 15). Its 50 rps rung had p99
between 67 and 2405 ms, and its 100 and 150 rps rungs ran away to p99 above 30 s; **the 200 rps rung was
never reached.** That record's own reading: the over-budget figures belong to the route path, not the
evaluator, and the saturation owner was left open ("SL-1259 or F35, not checked here"). Its bench harness
call to `_fetch_bundle` was stale at that head (a `TypeError` for a missing `slot` argument) and needed a
scratch fix there; the baseline above ran on `c08a48e5` and `4eb13644` without a reported harness patch.
This finding is the main-tree confirmation, now at all four rates.

## Limits of this finding

- **The host caveat binds the verdict, not the finding.** `docs/roadmap.md` G4 carries a maintainer line of
  2026-09-29: NFR-489 is "measured, diagnostic" on the shared VM, and "No near-bound pass or fail is claimed
  from the shared VM", the verdict being carried until a dedicated host exists. These results are not
  near-bound: the 25 rps GBM p99 is 1.1 to 2.3 times the budget, the no-GBM p99 is 4.2 to 67.8 times, the
  50 rps GBM arm is 137 times, and the 100 and 200 rps passes run away. Host noise on
  an 8-vCPU box with load under 3 does not reach those margins. This finding claims "fails by a margin the host
  cannot explain", not a near-bound verdict.
- Each rate is measured once, except 25 rps (once, plus three re-runs). The 50, 100 and 200 rps figures are
  therefore single runs; the acceptance requires at least three per rate.
- The 200 rps GBM rung is void under the harness's own rule (generator behind), so no valid 200 rps p99 exists.
- The 78 ms and 34 ms `_fetch_bundle` figures are a side measurement. They show the cost is large; they do
  not show it is the cause of the 25 rps p99 or of the saturation.

## Disposition

**Proposed by the auditor; the lead gives the verdict.**

1. **Measurement owner: SL-1259.** The final verdict on NFR-489 is that slice's, on the exit tree.
2. **Remedy: a WK-1178 leaf plan (PL 9728, working id)**, dispatched on lane B after the FD-1356 fix. Its
   Task 0 attributes the stalls and the per-request cost on main before a fix is chosen. Acceptance is
   NFR-489's predicate at 25, 50, 100 and 200 rps with at least three runs per rate, per-pass times and load
   recorded.
3. **Event that discharges this row:** the remedy merges and SL-1259 records the NFR-489 verdict on its
   measurement, or the maintainer amends or carries NFR-489 by a dated line.
