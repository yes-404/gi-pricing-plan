# NFR-RATE-1 at the full HTTP path and under offered load — W11 Slice 2 Task 2D

`docs/research/w11-task-1-5-nfr-rate-1-2.md` measured `score_one` directly: no HTTP, no
FastAPI, no database, sequential calls on one event loop. It said so, and it named what it
was not covering — *"NFR-RATE-1's sustained-200-rps and full-path halves remain entirely
unmeasured here, by design (Slice 2's)."* This is that measurement.

**NFR-RATE-1, verbatim** (`docs/specs/03-rating-engine.md:797`):

> Real-time scoring p99 < 50 ms **server-side** at **200 rps per replica** for a ~200-step
> motor structure with one `exact` GBM call (NFR-OVR-1). **Without a GBM call, p99 < 15 ms.**

Three claims, of which Task 1.5 could reach one. The other two — *server-side*, meaning the
endpoint rather than the function, and *at 200 rps*, meaning under offered load — were
untested **by construction**: a harness that never enters the route and never offers a rate
cannot fail either clause.

**The headline, stated before the tables, because it is not a matter of degree.** On the real
fixture, resolving *which bundle to score* costs **p99 66.294 ms** for the with-GBM condition.
The budget for the entire request is 50 ms. **The fetch alone exceeds the whole budget before
a single rating step executes**, and the without-GBM fetch (p99 44.283 ms) exceeds its own
15 ms budget by nearly threefold. Every rung of the offered-rate sweep is over budget, from
10 rps upward — a twentieth of the required rate — and at the lowest rung queueing is
negligible, so this is not a capacity result.

---

## Method

- **Code under test.** `backend/src/app/api/score.py` (`score`, `_compiled_for`,
  `_fetch_bundle`), `backend/src/app/platform/rating_versions.py`
  (`resolve_rating_version_ref`), `packages/pricing-core/src/pricing_core/rating/score.py`
  (`score_one`).
- **Harness.** `scripts/bench-rating.py --http`, extending Task 1.5's script rather than
  adding a second — the leaf plan is explicit that two scripts measuring one thing is how two
  numbers start disagreeing. Ruling 6 reserved `asyncio` + `httpx` for this measurement and
  draws its forbidden line at load-generation dependencies (`locust`/`k6`/`hey`/`wrk`);
  `httpx` is already a workspace dependency. **Not a CI gate**, per the same ruling.
- **Shape.** `uvicorn app.main:create_app --factory` in **its own process** — NFR-RATE-1
  measures a *replica*, and an in-process ASGI transport would put the load generator's own
  work on the server's event loop and inside the latency it is trying to measure. Client and
  server communicate over loopback, which adds ~0.1 ms against a 50 ms budget.
- **Fixture.** The same ~200-step motor structure Task 1.5 used — 2 scalar inputs, 8 numeric
  rating factors, one `table` lookup, one `exact` `model_call` against a real XGBoost booster
  (8 features, 5,000 rows, 300 rounds), 187 chained `expression` steps, one `output` step.
  **200 steps with GBM, 199 without.** Serialised: **2,039,114 B** with GBM, **63,283 B**
  without.
- **Warm slot, no hydration in the steady state.** A measured-and-discarded warmup rung
  precedes each sweep, so the reported rungs read a populated `BundleSlot` and do not pay
  `load_bundle`. Bundle hydration is *not* included in any figure below.
- **Open loop, and this is load-bearing.** Requests are scheduled on the clock at the offered
  rate, not on completions. A closed-loop generator throttles itself when the server slows —
  it issues fewer requests, and the ones that would have been slowest are never sent — which
  is coordinated omission, and its effect is to make a saturating system return a *passing*
  p99. NFR-RATE-1 also says *"at 200 rps"*, an **offered** rate, so scheduling on the clock is
  the literal reading as well as the honest one.
- **Server-side timing comes from the app's own instrumentation.** The request middleware
  already emits `duration_ms` per completed request; parsing its JSON log needs no production
  change. **Client round-trip minus handler time is queue wait plus loopback**, which is what
  separates a slow handler from a saturated one.
- **Every figure carries its 1-minute load average.** F38 is the standing reason: the same
  harness returned both PASS and OVER against the same bound on this machine, and load is the
  variable that moved. A figure without its condition is not a measurement.
- **Machine.** Intel Xeon @ 2.20GHz, **4 cores**, 16.4 GB RAM — a shared development machine,
  not a dedicated benchmark host. 1-minute load 1.65 at startup, rising to 10.76 during the
  run, much of it self-inflicted.
- **Tree.** Branch `w11-2d-latency` off `origin/main` at `5d99042`. Run 2026-08-30, one pass.

---

## Result — `_fetch_bundle` alone, the cost every request pays

`_compiled_for` (`api/score.py:181`) consults the `BundleSlot` **only after** `_fetch_bundle`
has returned, and it must: the slot is keyed on `content_hash`, and the only way to learn a
ref's content hash is to fetch the bundle. So every happy-path request performs two SELECTs,
a full MinIO object read, and `Bundle.model_validate_json` over the whole payload — booster
included — and the slot saves `load_bundle` and nothing upstream of it.

| condition | bundle | mean | stdev | p50 | p99 | max | 1-min load |
|---|---|---|---|---|---|---|---|
| with GBM | 2,039,114 B | **36.574 ms** | 10.938 | 33.894 | **66.294** | 107.760 | 4.90 → 4.83 |
| without GBM | 63,283 B | **16.548 ms** | 4.477 | 15.117 | **44.283** | 44.677 | 10.76 → 10.70 |

200 calls each, sequential, warm slot.

**The with-GBM fetch p99 is 1.33× the entire 50 ms request budget. The without-GBM fetch p99
is 2.95× its entire 15 ms budget.** For comparison, `score_one` on the same with-GBM bundle
has mean 12.326 ms — so **resolving the bundle costs about three times what scoring it
costs**.

**This is a deliberate correctness choice with an unmeasured cost, not a broken cache.** The
`slot.hash_for(ref)` memo that would skip the fetch exists (Task 2A) and is wired into the
`except Exception` degradation branch for NFR-RATE-9. It is not on the happy path because a
ref that had been re-pointed would then serve a stale bundle — trading correctness for latency
silently. The design is correct. What this measurement establishes is that it is also
expensive enough that **NFR-RATE-1 may be unreachable without revisiting it**, and that is a
question above a measurement task.

---

## Result — NFR-RATE-1 at the full path, by offered rate

Client-observed round trip over loopback. `handler` is the app's own `duration_ms`.
`queue+loopback` is the difference at p99. `ceiling` is capacity implied by **that rung's
own** measured mean at the 2.10× concurrent speedup `zen-evaluate-concurrency.md:65` measured
on this box — recomputed per rung because a ceiling fixed from a prior quiet run is circular.

**With GBM — budget p99 < 50 ms**

| offered | issued | 1-min load | mean | p50 | **p99** | handler p99 | queue@p99 | ceiling | errors | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 10.1 | 5.39 → 5.04 | 65.928 | 61.296 | **146.319** | 139.140 | 7.179 | 31.9 | 0 | 100 |
| 25 | 25.1 | 5.04 → 4.72 | 697.967 | 898.648 | **1 515.247** | 1 470.990 | 44.257 | 3.0 | 0 | 250 |
| 50 | 50.1 | 4.72 → 5.25 | 11 798.227 | 10 782.710 | **24 649.241** | 24 298.990 | 350.251 | 0.2 | 0 | 500 |
| 100 | 99.6 | 5.25 → 6.12 | 26 050.823 | 28 119.482 | **44 052.657** | 41 817.100 | 2 235.557 | 0.1 | 33 | 967 |
| 200 | **149.5** | 6.12 → 10.76 | 58 937.599 | 60 246.963 | **111 924.786** | 47 589.520 | 64 335.266 | 0.0 | 140 | 1 860 |

**Without GBM — budget p99 < 15 ms**

| offered | issued | 1-min load | mean | p50 | **p99** | handler p99 | queue@p99 | ceiling | errors | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 10.1 | 9.68 → 8.34 | 54.534 | 41.669 | **237.421** | 233.230 | 4.191 | 38.5 | 0 | 100 |
| 25 | 25.1 | 8.34 → 8.22 | 55.852 | 42.398 | **203.651** | 191.400 | 12.251 | 37.6 | 0 | 250 |
| 50 | 50.1 | 8.22 → 8.15 | 6 877.564 | 6 599.214 | **17 145.881** | 16 895.430 | 250.451 | 0.3 | 0 | 500 |
| 100 | 98.4 | 8.15 → 7.61 | 22 859.648 | 23 152.271 | **38 647.124** | 35 733.800 | 2 913.324 | 0.1 | 6 | 994 |
| 200 | **142.1** | 7.61 → 6.28 | 41 407.721 | 36 554.650 | **75 694.581** | 35 644.370 | 40 050.211 | 0.1 | 32 | 1 968 |

**Every rung is over budget in both conditions**, by between 2.9× and 2 239× at p99.

**The 200 rps rungs are void as server measurements.** The generator issued 149.5 and 142.1
rps against 200 offered — it fell behind, so those rows measure the generator as much as the
server. They are kept because deleting a failed rung would misrepresent what was attempted,
not because they evidence anything about the platform.

**The lowest rung is the informative one, and it is not a capacity result.** At 10 rps —
5 % of the required rate — queue wait at p99 is **7.179 ms** (with GBM) and **4.191 ms**
(without). The server is not queueing; it is slow per request. Of the with-GBM handler's
60.959 ms mean, `_fetch_bundle` accounts for **36.574 ms (60 %)** and `score_one` for
**12.326 ms (20 %)**, leaving ~12 ms of framework, auth, dependency injection and
serialisation.

---

## Result — the component half re-measured (F38)

F38 records NFR-RATE-1's without-GBM half as *"measured; verdict unstable across runs — not
established"*, on 2 of 5 runs breaching. This run is a sixth observation of the same committed
harness, and it breaches.

| | mean | stdev | p50 | p99 | max | 1-min load | budget | verdict |
|---|---|---|---|---|---|---|---|---|
| with GBM, 200 steps | 12.326 | 4.973 | 10.923 | **33.468** | 62.103 | 2.48 → 3.34 | 50 ms | PASS |
| without GBM, 199 steps | 9.315 | 3.377 | 8.582 | **23.027** | 48.073 | 3.23 → 3.05 | 15 ms | **OVER** |

1,000 measured calls after 200 discarded, sequential.

**F38's tally becomes 3 of 6 breaching.** The with-GBM half remains PASS in 6 of 6, but its
margin has narrowed again — 33.468 ms is **1.49×** inside the budget where the original note
recorded ~4.0×.

---

## Result — NFR-RATE-2 (trace overhead), incidental to this task

Not this task's deliverable; recorded because the run produced it and F35 tracks it.

| metric | traced | untraced | overhead | budget |
|---|---|---|---|---|
| p99, with GBM, 200 steps | 553.629 ms | 33.468 ms | **+1 554.2 %** | ≤ 20 % |
| mean (informational) | 125.204 ms | 12.326 ms | +915.8 % | — |

Traced block at load 3.21 → 7.07, untraced at 2.48 → 3.34 — **not comparable conditions**, and
the overhead figure inherits that. The prior note's five runs spanned +497 % to +723 % at
loads 0.39–8.50; this run is higher than all of them and was taken at a rising load.

The A/B/C decomposition (200 interleaved rounds, load 5.70 → 5.24, medians) puts
**engine-side at 50.757 ms (76.2 %)** and **ours — `_build_trace`'s copying — at 15.882 ms
(23.8 %)** of the 66.639 ms added. That sits inside the prior note's "our share is 12–25 %
depending on how it is cut" and does not move it.

---

## What this does not cover

- **NFR-RATE-13 is not isolated.** The plan's acceptance asked for it re-measured on the real
  path against W8's synthetic p99 0.070 ms. This run bounds it but does not isolate it: the
  ~12 ms residual after subtracting fetch and `score_one` from the handler mean contains
  framework, routing, authentication, dependency injection **and** response serialisation
  together. An upper bound containing four other things is not a measurement of the one, and
  reporting it as such is the substitution this note exists to avoid. **Owed, not delivered.**
- **NFR-RATE-11's rate limit is not exercised, deliberately.** `rate_limit_rps` exists as a
  column (`db/models.py:394`), a request and response field (`api/service_accounts.py:65`,
  `:90`, `:113`, `:175`), an error code `RATE_LIMITED` (`errors.py:58`) and a 429 title
  (`api/responses.py:34`) — and is **enforced nowhere**. A load test against an absent rate
  limit returns "no requests rejected", which is indistinguishable from "the limit is
  generous". That figure would read as a pass and mean nothing, so it was not generated. This
  is a finding, not a measurement.
- **One pass.** F38's own lesson is that repetition under varied load establishes a verdict and
  a single run does not. This is a single run. Its *direction* is not in doubt — a fetch p99 of
  66.294 ms against a 50 ms whole-request budget is not a margin that repetition reverses —
  but its *figures* are one observation each.
- **The two conditions were measured under different load**, 4.7–6.1 for with-GBM and 7.6–9.7
  for without-GBM, because the with-GBM sweep drove the box up before the without-GBM sweep
  ran. **They are not comparable to each other.** Each is comparable to its own budget, which
  is what the requirement asks.
- **No bundle hydration**, no cold start, no cache miss, no multi-ref slot thrash
  (`bundle_slot_capacity` defaults to 1).
- **A synthetic fixture**, with an arbitrarily-sized booster rather than a production model,
  and a without-GBM structure that reuses the same 187-step expression chain rather than an
  independently designed no-GBM algorithm.

---

## Reading — what the measurement forces, what it merely suggests

**Forced (measured, not inferred):**

- **NFR-RATE-1 fails at the full path in both conditions, at every offered rate tested,
  starting at 10 rps.** The requirement asks for 200.
- **The dominant cost is `_fetch_bundle`, not scoring.** 36.574 ms mean against `score_one`'s
  12.326 ms on the same bundle; ~60 % of handler time at the cleanest rung.
- **It is not saturation and not the box.** At 10 rps, queue wait at p99 is 7.179 ms and
  4.191 ms. The four-way attribution — code, box, queue, fetch — resolves to fetch.
- **The without-GBM component half breaches again**, making F38 3 of 6.

**Suggested, not proven:**

- That the fetch cost scales with serialised bundle size. Two points (2,039,114 B → 36.574 ms;
  63,283 B → 16.548 ms) are consistent with it, but they were taken at different loads and two
  points do not establish a curve.
- That the ~12 ms residual is mostly serialisation. It is mostly *something* other than fetch
  and scoring; which part is not measured here.

**Not decided here, and not this document's place to decide:**

- **Whether NFR-RATE-1 is achievable with the present design.** If fetch dominates, the
  requirement's with-GBM half is a statement about object-store throughput rather than about
  scoring speed — at 200 rps it implies ~400 MB/s of object reads and 200 full booster parses
  per second — and the remedy is architectural rather than an optimisation. Moving
  `slot.hash_for(ref)` onto the happy path is the obvious candidate and is **not** safe as-is:
  it would serve a stale bundle when a ref is re-pointed. That trade belongs to a ruling.
- **Whether NFR-RATE-1's numbers are right.** A requirement measured only now, at the end of
  the workstream that implements it, may be describing a machine nobody has. That is a §14
  question.
