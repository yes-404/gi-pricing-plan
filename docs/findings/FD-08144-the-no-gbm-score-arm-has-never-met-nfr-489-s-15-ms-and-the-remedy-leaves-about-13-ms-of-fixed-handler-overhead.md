---
id: FD-8144
family: finding
title: The no-GBM /score arm has never met NFR-489's 15 ms, and the remedy leaves about 13 ms of fixed handler overhead
status: active
created: 2026-10-21
owner: auditor
tree: 11bddecb9bcafd315617c2d5d198598c6ecfad33
corrected_by: []
relates: [WK-674, SL-1455, RL-1685, FD-1411, LG-1760]
---

# FD-8144 — The no-GBM /score arm has never met NFR-489's 15 ms

## Finding

**HIGH; owner WK-674** (SL-1455's remedy; `docs/roadmap.md` §12 row 2, "meeting NFR-489"). Filed on
the maintainer's (by delegation) entry "2026-10-21 15:31:24 BST" (`to-lead.md`), item (1): "A HIGH FD
against NFR-489 / WK-674 (SL-1455 remedy; §12 row 2 'meeting NFR-489'): GO", on the lead's escalation
"2026-10-21 15:27:13 BST" (`handover/from-lead-2026-10-09.md`).

The no-GBM arm of NFR-489 (`docs/specs/03-rating-engine.md` §9: "Without a GBM call, p99 < 15 ms") is
over budget by a fixed amount of work outside scoring. **It has never been under 15 ms anywhere. This is
not a regression:** it is a budget the design has not met. The remedy (RL-1685's one request session)
shrank the overage but did not close it.

The diagnosis is read-only and nothing was run on a host for it:
`~/gi-pricing-plan.local/handover/perf-nfr489-diagnosis-2026-10-21.md` (seat perf-nfr489, 2026-10-21
15:25:52 BST). The line numbers below are that file's, and each holds at `origin/main` 11bddecb
(`git diff --stat 44c18e11 origin/main -- backend/src scripts/bench-rating.py packages` is empty, so they
hold at the measured head 44c18e11 too).

## Evidence

**Readings** (nfr-bench-1, LG-1760 at `origin/nfr1-sl1455-task4-2026-10-21` @53b1ceb7, `inv01-r25.out`):

- No-GBM `score_one` in process: p50 5.040 ms, **p99 6.863 ms** (diagnosis §1, `inv01-r25.out` :16–18).
- No-GBM handler: mean 18.378 ms, **p99 23.060 ms** (bench arm, :83–84); default-live arm handler p99
  21.640 ms (:87–88). Both are over 15 ms server-side, not only the client p99.
- The handler mean minus the `score_one` mean is **13.11 ms** without a GBM (18.378 − 5.267) and
  **13.93 ms** with one (21.141 − 7.210) (:84, :16, :67, :11). The two arms' handler means differ by
  2.76 ms, close to the `score_one` difference of 1.94 ms, so removing the GBM removes only the model's
  own cost. About 13 ms is fixed overhead, whatever `score_one` costs.
- The 17 ms "cold bundle fetch" is **per worker, not per request.** It is a side measurement that hands
  `_fetch_bundle` a fresh slot (`scripts/bench-rating.py:877-878`, `_slot()` returning `BundleSlot()` when
  not warm); the served path returns on a slot hit before the blob (`backend/src/app/api/score.py:304-308`).
  FD-1411:91-97 already corrected this attribution.

**The warm request path** (diagnosis §2): about 12 serial database round trips (9 statements plus the
pre-ping `pool_pre_ping=True` at `backend/src/app/db/session.py:42`, plus BEGIN and ROLLBACK) and 1 Redis
pipeline round trip (`backend/src/app/platform/rate_limit.py:97-100`), all awaited one after another and
all crossing the docker-proxy userland relay (`.rec:31`: `docker-proxy … -host-port 5432 -container-ip
172.18.0.4`).

**The bench runs at the default trace sample rate.** `rating.trace_sample_rate` defaults to 0.01
(`backend/src/app/platform/settings.py:217-219`) and `bench-rating.py` never sets it (`_seed`, :715-835,
writes no Setting). About 1 % of requests therefore also close the read session, take a second checkout
and write a trace INSERT with a job, an audit record and a commit (`score.py:598-638`). The RL-1685 guard
counts its `MAX_STATEMENTS = 9` only with the rate pinned at 0
(`backend/tests/test_score_request_cost.py:3-8`), so **the bench measures a path the guard does not count.**

**History** (diagnosis §3): FD-1411:121-125 (p99 67.0 / 323.6 / 63.7 ms, handler p99 60.6 / 320.4 /
58.6 ms) and LG-1760:437 (server total p50 78.12, p99 116.43 ms) were taken on the shared VM and on the
pre-remedy shape. LG-1760:308 says no bench invocation existed for the remedy head, so 2026-10-21's is the
first timed reading of the remedy. The hosts and loads differ, so the readings are not like for like.

## In flight

A short H1 + H2 diagnosis session on nfr-bench-1 (N = 4, no code change, about 30 min) is authorised
(the maintainer, "2026-10-21 15:31:24 BST", item (2)) and **has no readings yet.** H1 is the serial round
trips through the port proxy; H2 is the 1 % sampling setting the p99. H3 to H5 (framework overhead, a cold
slot, GC) are ranked below and not scheduled. Its readings are labelled "diagnosis, not a verdict".

## Open question

Whether NFR-489's no-GBM 15 ms includes the default 1 % trace sampling (FR-259), and the per-request
authentication, rate-limit and database reads, is a spec question. It goes to a decision-maker as an OQ
after H2 has a reading; it is not a tuning knob, because 1 % is the production default.

## Disposition

Open, owner WK-674. This record gives no verdict and no remedy: `docs/roadmap.md` §12 row 2's date is held
pending the H1 and H2 readings (the maintainer, "2026-10-21 15:31:24 BST"). Filed under working id 8144.
