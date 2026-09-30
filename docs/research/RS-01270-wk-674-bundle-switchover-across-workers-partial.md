---
id: RS-1270
family: research
kind: spike
title: WK-674 bundle switchover across workers — mixed and dropped responses and switch time (spike F1, partial, written from its salvage)
status: active
created: 2026-09-29
owner: executor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-674
corrected_by: []
relates: [FR-268, NFR-494]
---

# RS-1270 — WK-674 bundle switchover across workers (spike F1, partial)

First filed 2026-09-28; `created` re-dated so the id sequence stays non-decreasing (check 31).

Minted as RS-1270 on 2026-09-30; it was filed under working id 9802.

Spike F1 of Track F was run on 2026-09-28 by the executor `spike-f1`. **It was stopped
after three load-guardrail breaches, 2026-09-28**, before it filed a record. **This record
is written from its salvage by a different executor, `spike-f4`.** It reports only what
the salvaged harness, result files and log contain. The verdict below is a proposal; the
deputy decides on this record.

## Question

**The deputy's F1 item.** Quoted verbatim from the entry "2026-09-28 11:33:12 BST · deputy
· THE OQ STREAM" in the lead's channel file (`~/gi-pricing-plan.local/channel/to-lead.md`):

```text
## 2026-09-28 11:33:12 BST · deputy · THE OQ STREAM: 15 items that could block Phase 2, each RULED by delegation or sent to a spike. Two new tracks: E (file the decisions) and F (timeboxed spikes)
[extract: the entry's F1 item only, quoted whole; the entry's other items concern other tracks]
- **F1 · WK-674 bundle switchover across workers:** N workers at 200 rps with a push-at-deploy switch (RL-876/RL-882). Pass: zero mixed or dropped responses (bundle hash asserted on every response) and switch ≤ 30 s including warm-up (NFR-494). If 3 h is not enough, the RS reports the partial measurement and what remains.
```

## Criteria

**The requirements it measures.** Both are quoted from `docs/specs/03-rating-engine.md` at
this record's `tree:`.

- **FR-268:** "Deployment is atomic per environment: a scoring call sees either the old or
  the new bundle, never a mix. Bundles are pre-warmed into cache before the switch."
- **NFR-494:** "Deployment switchover is atomic with no dropped or mixed-bundle requests,
  and completes within 30 s of the deploy command including cache warming."

**The pass condition, as applied here:**
- 0 mixed responses;
- 0 dropped responses;
- a switch of at most 30 s, measured from the deploy command and including warm-up.

The spike brief requires N runs, not one, for a verdict.

## Method

Everything below is read from the salvage ref `refs/salvage/2026-09-28/spike-f1` =
`73a6d3fdc16352febdbbdd97240e66b5b94675c4`, by `git show <ref>:<path>`. That is one commit
(authored 2026-09-28T11:00:17Z), directly on `df8e5811a151a99c7317690faf9278a6dc3400be`.

- **The engine is real.** `spike/f1/fixtures.py` builds two ~200-step GBM bundles, A and
  B, with `scripts/bench-rating.py`, and records a reference result signature for each in
  `spike/f1/refs.json`. The build path is `compile_bundle`, then `load_bundle`, then
  `score_one` from `pricing_core`. A and B differ in graph length, so they differ in hash
  and in premium: `payable_premium` `value_minor` is 17538 for A and 17350 for B.
- **Workers** (`spike/f1/app.py`). Each worker is a uvicorn process that holds its
  environment's live bundle.
  - A deploy is two-phase over a Redis channel.
  - **PREPARE** fetches and hydrates the target bundle off the event loop (the warm-up),
    then acknowledges.
  - **COMMIT** swaps the one `live` reference, then acknowledges.
  - `/score` reads `live` once, at request start. It returns the engine-stamped hash
    (`h`), the held object's hash (`held`), the result signature (`sig`), the worker `pid`,
    and the start and end times (`ts`, `te`).
- **Deploy command** (`spike/f1/deploy.py`): it writes the bundle into the cache, then
  publishes PREPARE and waits for every worker's acknowledgement. It then sets the
  environment pointer, publishes COMMIT, and waits for every commit acknowledgement.
  **`switch_s` = t_all_committed − t_cmd**, so it includes the warm-up.
- **Load and analysis** (`spike/f1/run.py`): open-loop load at 200 rps for 40 s, with the
  deploy A → B at 10 s. Function `analyse()` computes every figure below:
  - **drops:** responses whose status is not 200, exceptions included;
  - **mixed:** a 200 response whose `h` is not A or B, whose `h` differs from `held`, or
    whose `sig` differs from the reference signature for `h`;
  - **stale_own_worker:** an A response that *started* after its own worker committed;
  - **stale_cross_worker:** an A response that started after some B response had
    *completed*. These are FR-268's two readings of "never a mix", per worker and across
    workers;
  - **overlap_window_ms:** the start of the last A response minus the start of the first
    B response. A negative value means no overlap.
- **Worker topology changed between runs.** The salvage holds one revision of `run.py`.
  Its `start_workers()` docstring says it "Replaces `uvicorn --workers N` after run
  m-n4-r1: kernel accept-sharing pinned keep-alive connections unevenly (one worker took
  ~50% of requests), overloading it". The current revision runs N independent uvicorn
  processes, one port each, and the client round-robins across them. So the three runs
  before `v2-n4-r1` used the earlier topology, and `v2-n4-r1` used this one.
  - **The per-worker shares, measured here from each run's `.jsonl`,** by counting the 200
    responses per `pid`:
    - m-n2-r1: 0.683 and 0.317;
    - m-n4-r1: 0.379, 0.319, 0.178 and 0.124;
    - v2-n4-r1: 0.25 for each worker.
  - The docstring's "~50%" does not match m-n4-r1's measured maximum of 0.379.
  - The two `summary` fields `server_ms` and `send_lag_p99_ms` appear only in
    `v2-n4-r1.json`.
  - The salvage shows nothing else about what changed.
- **Invocation.** `spike/f1/matrix.sh` runs `run.py <n> --duration 40 --deploy-at 10
  --tag m-n<n>-r<rep>` for n in {2, 4, 8} × 3 repeats. It waits up to 120 s for load < 12
  first. `spike/f1/matrix.log` holds only its first two runs (n=2 rep=1 and n=4 rep=1),
  with no end marker. The invocations of `smoke-n2` and `v2-n4-r1` are not in the salvage.

## Findings

The deploy start times below are converted to BST from each run's `deploy.t_cmd`. Load is
the 1-minute average, from each summary's `load1_before` and `load1`.

| Run | Workers | rps | Sent | OK | Drops | Mixed | stale own / cross | overlap_window_ms | switch_s | prepare_s | warm_s per worker | Deploy command | Load before → after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| smoke-n2 | 2 | 200 | 3000 | 3000 | 0 | 0 | 0 / 0 | −2.96 | 0.148 | 0.146 | 0.123, 0.129 | 11:45:26 | 17.95 → 14.19 |
| m-n2-r1 | 2 | 200 | 8000 | 8000 | 0 | 0 | 0 / 0 | −7.03 | 0.147 | 0.145 | 0.119, 0.128 | 11:46:18 | 10.32 → 12.82 |
| m-n4-r1 | 4 | 200 | 8000 | 7997 | **3** | 0 | 0 / 0 | −21.6 | 0.220 | 0.215 | 0.172, 0.173, 0.186, 0.19 | 11:49:16 | 15.54 → 19.54 |
| v2-n4-r1 | 4 | 200 | 8000 | 8000 | 0 | 0 | 0 / 0 | −5.06 | 0.306 | 0.303 | 0.184, 0.186, 0.224, 0.269 | 11:59:15 | 13.19 → 9.94 |

Every run's `deploy_abort` is `null`. Its `subscribers` equals the number of workers. Its
`pids_seen` equals the number of workers.

**The 3 drops in m-n4-r1.**
- All three `drop_samples` read "RemoteProtocolError: Server disconnected without sending
  a response."
- They were measured here from `m-n4-r1.jsonl`, with times relative to the run's first
  send; the deploy command was at +10.2 s:

| Request i | Sent | Error received |
|---|---|---|
| 2680 | +13.4 s (11:49:20 BST) | +39.9 s |
| 3794 | +19.1 s (11:49:25 BST) | +40.0 s |
| 4954 | +25.0 s (11:49:31 BST) | +65.2 s (11:50:11 BST) |

- All three were sent after the switch had completed, and all were received by
  11:50:11 BST.
- The salvage records no cause.
- The harness revision that followed, `v2-n4-r1`, had 0 drops, but it is one run.

**Latency.** It is reported because it bounds how far the load was actually delivered.
- m-n4-r1's client latency was:
  - pre-deploy: p50 421.76 ms, p99 107 685.22 ms;
  - post-switch: p50 62 080.62 ms, p99 109 839.06 ms.
- m-n2-r1's post-switch p99 was 9 630.57 ms.
- v2-n4-r1's was:
  - pre: p50 16.77 ms, p99 60.26 ms;
  - post: p50 12.32 ms, p99 27.73 ms;
  - server-side: p50 9.81 ms, p99 21.7 ms;
  - send lag p99: 5.67 ms.

**Other runs.** `spike/f1/sigguard.py`'s docstring says two further runs were SIGTERMed
from outside, at 11:52 and 11:57 BST. The salvage holds no result file for either.

## Verdict against the criteria (proposal)

**Partial.** A pass is not possible here, because there is **one run per configuration**
and the brief requires N runs.

- **n=2**, over 2 runs (the smoke run and m-n2-r1), both on the earlier topology: 0 mixed,
  0 dropped, 0 stale by either reading. Switch 0.147–0.148 s.
- **n=4:**
  - m-n4-r1, on the earlier topology, had **3 drops**. It therefore fails NFR-494's "no
    dropped" clause for that run, with 0 mixed and a 0.220 s switch.
  - v2-n4-r1, on the revised topology, had 0 mixed and 0 dropped, with a 0.306 s switch.
- **n=8:** not run.
- **Switch time:** every measured switch, warm-up included, is between 0.147 and 0.306 s,
  against the 30 s bound. This is one run per configuration. The warm-up measured here is a
  ~2 MB bundle already in the spike's Redis.

## Decision

This is the deputy's decision on this record, given by the maintainer's delegation. The whole entry is quoted
verbatim from the lead's channel file (`~/gi-pricing-plan.local/channel/to-lead.md`):

```text
## 2026-09-28 12:34:09 BST · deputy · Spike F1 DECIDED on its RS record (#837): INCONCLUSIVE, not a pass. The two-phase PREPARE/COMMIT push is adopted as WK-674's design DIRECTION, and my 11:33:12 pass criterion becomes WK-674's acceptance test, unchanged

Given by the maintainer's delegation (28 Sep), on the record as I read it at `p2-f1-rs-exec` (salvage `73a6d3fd` on `df8e5811`). The record's "Partial" verdict is correct, and its reading of each run is honest (topology change disclosed, docstring "~50%" checked against 0.379, drop timings measured).

**What it shows:**
- **Mixed:** 0 of 27 000 sent across four runs. That holds for mixed and for stale on both FR-268 readings (own worker and cross worker), and every overlap window is negative.
- **Switch:** 0.147–0.306 s, warm-up included, against NFR-494's 30 s.
- **Drops:** **3 in m-n4-r1**, all `RemoteProtocolError`, all sent **after** the switch completed. That run was on the earlier topology, at load 15.54 → 19.54, with client p99 107 685 ms pre-deploy: the server was saturated before the deploy. v2-n4-r1, on the revised topology, had 0.
- **The limits:** one run per configuration; n=8 never run; every run started at load 10.32–17.95; a loopback, single-host Redis mirror, not WK-674's deployment path.

**The decision:**
1. **Not a pass, not a fail: inconclusive.** One run cannot establish a verdict, and the load invalidates the timings as evidence of the budget. The zero-mixed result across 27 000 responses and both FR-268 readings is **evidence for the design**. It is not proof.
2. **The design direction is adopted for WK-674:** the two-phase PREPARE (fetch and hydrate off the event loop, then acknowledge) and COMMIT (swap the one `live` reference, then acknowledge) over a push channel. `/score` reads `live` once at request start, and every response carries the engine-stamped bundle hash. WK-674's leaf plan may build on it. **It does not treat the 30 s bound or the zero-drop clause as met.**
3. **My 11:33:12 criterion becomes WK-674's acceptance test, unchanged:** 0 mixed and 0 dropped with the bundle hash asserted on every response, switch ≤ 30 s including warm-up. It is measured as:
   - **N ≥ 3 runs for each n ∈ {2, 4, 8}**, at 200 rps;
   - **on the deployment path WK-674 builds**, not a loopback mirror;
   - with load < 12 at the start of every run, recorded beside it;
   - worker affinity and the load-balancing topology stated.
4. **The 3 drops are carried, not explained away.** WK-674 either reproduces the m-n4 conditions to find their cause, or shows 0 drops at N ≥ 3 at n=4 and n=8. Until one of those, "dropped" is an open question on WK-674's row, not a pass.
5. **Filing:** #837 carries this entry whole, fenced, as its Decision section. The WK-674 obligation is written into WK-674's roadmap row when its first slice is planned (not by this goal). F1 blocks nothing in today's five Works.

All four spike decisions are now made: F4 (hypothesis, conditioned), F3 (exact Shapley), F2 (Vue Flow, PASS), F1 (inconclusive, criterion carried). Each is final on its RS record at merge.
```

## What remains

- **N ≥ 3 runs per configuration**, on the revised topology, for n=2 and n=4.
- **n=8.** It was not run.
- **A load-pinned re-run.** All four runs started with a 1-minute load between 10.32 and
  17.95. The spike was stopped after three load-guardrail breaches, 2026-09-28.
- **The m-n4-r1 drops.** Their cause is not established. A repeat on the earlier topology
  would show whether they belong to kernel accept-sharing, as `run.py`'s docstring implies,
  or to something else.
- **Scope of the prototype.** It is a single-host Redis push at loopback, not WK-674's
  deployment path. The environment pointer and the cache-write step are the spike's own
  mirror of RL-876 and RL-882.

## Salvage

`refs/salvage/2026-09-28/spike-f1` = `73a6d3fdc16352febdbbdd97240e66b5b94675c4`, on
origin.
- **Harness:** `spike/f1/{app,deploy,run,fixtures,sigguard}.py` and `spike/f1/matrix.sh`.
- **Fixture references:** `spike/f1/refs.json` and `spike/f1/fixtures.log`.
- **Results:** `spike/f1/results/{smoke-n2,m-n2-r1,m-n4-r1,v2-n4-r1}.json` (summaries) and
  `.jsonl` (every response), plus `spike/f1/matrix.log`.
