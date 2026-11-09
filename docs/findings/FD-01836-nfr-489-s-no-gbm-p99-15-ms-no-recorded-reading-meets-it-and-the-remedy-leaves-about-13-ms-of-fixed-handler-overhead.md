---
id: FD-1836
family: finding
title: NFR-489's no-GBM p99 < 15 ms: no recorded reading meets it, and the remedy leaves about 13 ms of fixed handler overhead
status: active
created: 2026-10-21
owner: auditor
tree: 11bddecb9bcafd315617c2d5d198598c6ecfad33
corrected_by: []
relates: [WK-674, SL-1455, RL-1685, FD-1411, LG-1760]
---

# FD-1836 — NFR-489's no-GBM p99 < 15 ms: no recorded reading meets it

## Finding

**HIGH; owner WK-674** (SL-1455's remedy; `docs/roadmap.md` §12 row 2, "meeting NFR-489"). Filed on
the maintainer's (by delegation) entry "2026-10-21 15:31:24 BST" (`to-lead.md`), item (1): "A HIGH FD
against NFR-489 / WK-674 (SL-1455 remedy; §12 row 2 "meeting NFR-489"): GO", on the lead's escalation
"2026-10-21 15:27:13 BST" (`channel/from-lead-2026-10-09.md`).

The no-GBM arm of NFR-489 (`docs/specs/03-rating-engine.md` §9: "Without a GBM call, p99 < 15 ms") is
over budget by a fixed amount of work outside scoring. **No recorded reading of this arm has ever been
under 15 ms. This is not a regression:** it is a budget the design has not been shown to meet. The remedy
(RL-1685's one request session) appears to have shrunk the overage (p50 from roughly 36–78 ms to about
21 ms) but did not close it; the earlier readings were taken on other hosts and loads, so that comparison
is indicative only (see History).

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

**The warm request path** (diagnosis §2; counted from the code, not measured): about 12 serial database round trips (9 statements plus the
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

**Narrower than first drafted.** The maintainer's (by delegation) ruling, "2026-10-21 15:31:24 BST" item
(3), says: "NFR-489 says "server-side". The per-request auth, rate-limit and DB reads are server work, so
they are inside the 15 ms and are not open. OQ-1453 put caller-requested inline traces outside NFR-489, but
did not decide the background 1 % FR-259 sampling. That is the only open point." So the per-request
authentication, rate-limit and database reads are **not** an open question: they count against the 15 ms.
The one open point is whether NFR-489's no-GBM 15 ms includes the default 1 % background trace sampling
(FR-259). It is a spec question, not a tuning knob, because 1 % is the production default. The same
entry sends it to a decision-maker seat, which writes it as an OQ with options and a recommendation,
after H2 has a reading so the options carry measured costs.

## Disposition

Open, owner WK-674. This record gives no verdict and no remedy: `docs/roadmap.md` §12 row 2's date is held
pending the H1 and H2 readings (the maintainer, "2026-10-21 15:31:24 BST", item (4)). If H1 or H2 brings
the no-GBM p99 under 15 ms through configuration or deployment topology, the ETA stands; if not, a remedy
slice or a budget change is the user's decision (row 2's scope is the user's, set 14 Oct), put to the user
with measured options. Filed as working id 8144; minted FD-1836 on 2026-10-21, in the D29 batch mint PR.

*(Dated line, 2026-11-05, docs batch 11, by the auditor, on the staged S1 item C reading of 2026-11-05 10:30:13 GMT (record: LG-1760 addendum, nfr-bench-1 session 1): NFR-489 is UNMET: without GBM p99 37.5 to 41.2 ms against the budget of under 15 ms (OVER in 4 of 4 runs, both arms, at the first rung); with GBM marginal at 25 rps and OVER by 50 to 100 rps; at 25 rps the handler means per run are, with GBM, explicit-ref 25.3 to 26.7 ms and default-live 29.9 to 32.2 ms, and, without GBM, explicit-ref 23.2 to 24.2 ms and default-live 27.8 to 28.5 ms: the no-GBM arm is about 2.5 ms faster in both arms (FD-1836's 2.76 ms of 21 Oct again), so the GBM's own cost is small and the rest is fixed handler overhead. (CORRECTED on to-lead "2026-11-05 11:23:52 GMT", from itemC-run.log: this replaces the staged wording "handler mean about 27 to 31 ms; the no-GBM arm is no faster than the GBM arm", which was wrong.))*

*(Dated line, 2026-11-05, docs batch 11, by the auditor, on to-lead "2026-11-05 10:44:00 GMT" (S1 item D, mounted bundle): the mounted bundle adds about 2 ms over the plain path at every rung; the miss is the handler's. Explicit-ref at 25 rps read 42.975 ms against item C's 40.775 ms. NFR-489 on the composed path is carried by FD-1836 under WK-674; there is no separate finding for WK-1250.)*

*(Dated line, 2026-11-06, CR-2071's PR, by the executor, on to-lead "2026-11-05 12:02:53 GMT", candidate D, no FD: the no-GBM handler mean at 25 rps rose about 5 ms between `44c18e11` (18.378 ms, 21 Oct) and `dae9637e` (explicit-ref 23.2 to 24.2 ms). It is unattributed; FD-1729's role change and SL-1992's reconcile are candidates only, and S2's item N names it.)*

*(Dated line, 2026-11-06, CR-2071's PR, by the executor, on to-lead "2026-11-05 11:23:52 GMT" (3)(b) and "2026-11-06 09:54:01 GMT" (1): the event as written, the H1 + H2 readings and the decision-maker's ruling, no longer applies: OQ-1906 decided the ruling on 2026-10-25, and H1 and H2 never ran as a session. The event is now S2's item N, S3's D5.12 exit reading, and the user's remedy-or-budget word at the §14 review.)*

*(Dated line, 2026-11-07, docs batch 15, by the executor, on to-lead "2026-11-07 19:37:24 GMT" (N): S2 item N's py-spy profile of the 25 rps no-GBM handler is read as the cause reading. About half the active samples sit in asyncpg and SQLAlchemy, and `score_one` holds 2 of 522. The sampled arm was perturbed (p99 145 ms against 45 ms). AMD EPYC 7B12; not like-for-like with S1; 8 vCPU; lower bound on a non-spec host. The remedy-or-budget decision stays the maintainer's after S3, as delegated; S3's item C control runs first so that its exit reading can speak to this finding on that platform.)*

*(Dated line, 2026-11-09, docs batch 32, by the executor, on the maintainer's (by delegation) entry "2026-11-09 16:27:43 GMT" (D-3): FD-1836 is carried by name to P3-A. NFR-489's budgets stand; the P2 exit reading is UNMET on the 8-vCPU non-spec host (D5.12 at an offered 100 rps, n = 1, N = 4: p99 101.915 ms against 15 ms), accepted for the P2 close as an interim under the user's delegation of 2026-11-07 17:30:49, and the remedy question is re-opened on the spec host in P3-A (D-2). FD-1836, FD-1411 and F38 are carried together; the owner on the P3 row is the maintainer's to name at the P2 close. The amendment line is on NFR-489 in `docs/specs/03-rating-engine.md`.)*

*(Dated line, 2026-11-09, docs batch 32, by the planner (plan-s3fill), on the maintainer's (by delegation) entry "2026-11-09 18:38:40 GMT" (1), the diagnosis on this finding's carry to P3-A: the in-process scorer p99 13.6 / 9.2 ms pass (S3 `NFR490.log:27`, `:32`) while the HTTP-path p99 reads about 100 ms, so NFR-489's gap sits in the HTTP path.)*
