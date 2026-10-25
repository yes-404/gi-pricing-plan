---
id: RL-8218
family: ruling
title: "FD-1836's spec question decided — NFR-489's no-GBM p99 < 15 ms includes the requests FR-259's background sampling writes on the response path (the 1 % default rate and the decline and error floor); readings stay at the production default rate; the budget is not changed"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; DRAFT until the maintainer adopts it and it is minted
created: 2026-10-25
owner: decision-maker
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-674
slice: SL-1455
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1836, RL-1837, RL-1685, OQ-1453, NFR-489, NFR-490, FR-258, FR-259, WK-674, SL-1455, LG-1760]
---

# RL-8218 — FD-1836: NFR-489's no-GBM 15 ms includes the background-sampled requests

**DRAFT — binds nothing until the maintainer adopts it.** Drafted 2026-10-25 by the
decision-maker (seat dm-1836) on lead 28's brief `brief-dm-1836-2026-10-25.md`. The working ids
in prose (OQ 8145 and this record's 8218) are not minted.

## Authority and scope

- **The ask.** The maintainer's message to lead 28 of about 11:32 GMT on 2026-10-25, as the
  brief quotes it: *"FD-1836: send me its one-line question and your recommendation and I rule
  on it today"*. This seat did not find the message in a channel file. The brief is its only
  source here.
- **The finding.** FD-1836 (register row `docs/findings/register.md:408` at ff976406) names the
  event that next discharges it: *"the H1 + H2 readings and the decision-maker's ruling on the
  spec question"*. The H1 and H2 readings exist (LG-1760, below). This record is the ruling.
- **The question is narrower than "is the 15 ms the handler's or `score_one`'s".** The
  maintainer's (by delegation) entry "2026-10-21 15:31:24 BST" in `to-lead.md`, item (3),
  verbatim: *"NFR-489 says "server-side". The per-request auth, rate-limit and DB reads are
  server work, so they are inside the 15 ms and are not open. OQ-1453 put caller-requested
  inline traces outside NFR-489, but did not decide the background 1 % FR-259 sampling. That
  is the only open point."* So the handler is the measured span, and the ~13 ms of fixed
  handler overhead is inside the budget. Neither is ruled here again.
- **Already decided, and not reopened here.** RL-1837 (the user's decision of 2026-10-21,
  16:03:00 superseding 16:00:01) settles three things. The full ladder is measured first. The
  remedy is built off the row-2 path. The budget is not changed now and is reviewed in P3
  through an OQ (RL-1837 items 1, 3 and 4).
- **The open question, as drafted.** OQ 8145 on `origin/oq-8145-nfr489-sampling-2026-10-21`
  @abb13d5b (`docs/open-questions.md` and `docs/specs/03-rating-engine.md` §10, one row each),
  written by seat dm-8145 on 2026-10-21 after H2. It recommends (a). It is not on `main`, so this
  record decides it before it mints. Both mint together (see "For the lead").
- **Trees read.** `origin/main` ff976406 (the code and spec facts), LG-1760 at
  `origin/nfr1-sl1455-task4-2026-10-21` @cb83e4e1 (the H1 and H2 readings; cb83e4e1 is an
  ancestor of that branch's tip f1958b8f), and OQ 8145 @abb13d5b.

## The question

**Does NFR-489's no-GBM p99 < 15 ms include the requests that FR-259's background sampling
writes on the response path? These are the 1 % `rating.trace_sample_rate` default and the
100 % decline and error floor.**

## Facts

**The spec (ff976406).**
- NFR-489, `docs/specs/03-rating-engine.md:1559`: *"Real-time scoring p99 < 50 ms server-side at
  200 rps per replica … Without a GBM call, p99 < 15 ms. (Clarified 2026-10-05, OQ-1453: the
  ceiling governs untraced requests; a request served with an inline FR-258 trace is bounded by
  NFR-490.)"*
- OQ-1453, `03:1602`: *"NFR-489's p99 ceiling … governs UNTRACED real-time requests. A traced
  request (a caller-requested FR-258 inline trace) is bounded by NFR-490 instead (tracing adds
  ≤ 20 % to scoring latency)."* A background sample is not a caller-requested trace. The
  `/score` result stays untraced (`score.py:717`, below). So OQ-1453 neither includes nor
  excludes it.

**The code path (ff976406, `backend/src/app/api/score.py`).**
- `/score` awaits `_maybe_sample_trace(…)` at `:610-612`, **before** it returns the response
  at `:614-616`. The write is on the response path, not in the response's `background=`. At
  this tree only the shadow task runs there (`:603-609`).
- `_maybe_sample_trace` (`:706-760`) reads the rate through the request's session. It decides
  with `traces_service.decide_sampling`. On a sampled outcome it closes the read session and
  opens the write's own `unit_of_work`. The trace body is produced later by
  `score.trace_produce` (`:718-719`).
- `decide_sampling` (`backend/src/app/platform/traces.py:78-100`) samples every `declined` and
  `error` outcome *"regardless of `rate`"*. It samples a `quoted` one iff `roll < rate`.
- The rate defaults to `0.01` (`backend/src/app/platform/settings.py:217-219`). The caller of
  `/score` cannot turn it off per request.
- The RL-1685 guard counts **one warm, quoted request with `rating.trace_sample_rate` pinned
  at 0** (`backend/tests/test_score_request_cost.py:3-8`). So it counts no sampled request.

**The readings** (LG-1760 @cb83e4e1, "Readings — H1 and H2 diagnosis session, 2026-10-21
("diagnosis, not a verdict")", `:660`; nfr-bench-1, N = 4, 25 rps, no-GBM arms, n = 500 per
cell, one run each).
- Rate 0 removed the persisted traces: +24 rows at the default rate, +0 at rate 0 (`:683`).
- Handler p99 at the default rate (invocation A): 27.350 ms (bench arm) and 21.600 ms
  (default-live arm). At rate 0 (C): 21.580 and 21.270 ms. Client p99: A 29.905 and 24.438 ms;
  C 24.077 and 23.930 ms (`:677`, `:679`).
- *"Neither route brings the no-GBM p99 under 15 ms. The lowest no-GBM p99 across the three
  invocations is 21.270 ms server-side (handler) and 23.930 ms client-side."* (`:688`)
- The ledger's own caveat on H2: *"This is **not** a clean decisive result: n = 500 per arm and
  a single repeat each."* (`:687`)
- The fixed overhead outside `score_one`: handler mean 18.378 ms minus `score_one` mean
  5.267 ms = **13.11 ms** (`~/gi-pricing-plan.local/handover/perf-nfr489-diagnosis-2026-10-21.md:39`,
  from `inv01-r25.out` :84 and :16). The `score_one` p99 alone is 6.863 ms (the diagnosis
  file, `:18`, `:27`).

## Options

**(a) Include.** The 15 ms governs every untraced real-time request at the production default
rate, sampled ones included. OQ-1453's carve-out stays limited to caller-requested FR-258
traces.
- *Obliges:* OQ 8145 closed (a). One dated clarification clause on NFR-489 (`03:1559`). The
  pre-registered ladder protocol is unchanged, because it already runs at the default rate. In
  WK-674's off-path remedy (RL-1837 item 3): a sampled counted unit in the RL-1685 guard, and a
  plan for where the sampled write runs (moving it after the response is a design change under
  FR-259). No new slice now.
- *Effect on the 12 Nov exit demo and G4:* none. The no-GBM limb is missed under either
  reading, and RL-1837 carries it in FD-1836.

**(b) Exclude.** The ceiling governs only requests that FR-259 did not sample. Readings are
taken at rate 0, or with the sampled requests removed.
- *Obliges:* OQ 8145 closed (b). A **new NFR** that bounds sampled requests, because NFR-490
  bounds only caller-requested inline traces. A statement on declined and errored quotes, which
  are always sampled: if they are excluded, a product that declines often has no bounded
  declines. Also an amendment to the pre-registered ladder protocol, to measure at rate 0. All of
  this spec work must land before the 5 Nov docs freeze. Under (b), an operator who raises the
  rate (settings allow up to 1.0) breaches nothing, however slow the sampled path becomes.
- *Effect on the demo and G4:* the same carry. Rate 0 still reads 21.270 ms or more
  (LG-1760 `:688`).

**(c) Defer to P3,** to the budget-review OQ that RL-1837 item 4 already names.
- *Obliges:* OQ 8145 mints open, with a "Before Phase 3" gate row. The nfr-bench-1 ladder
  session must measure both rates, which roughly doubles its no-GBM half. FD-1836 stays without
  its spec answer. WK-674's remedy is planned without knowing whether the sampled write counts.
- *Effect on the demo and G4:* none on the date. The session takes longer.

## Ruled

*Proposed: the maintainer adopts.*

**(a) Include.** NFR-489's no-GBM p99 < 15 ms, like its GBM limb, governs every untraced
real-time `/score` request at the production default `rating.trace_sample_rate`. Requests
that FR-259 samples (by rate, or by the decline and error floor) are included. OQ-1453's
exclusion stays limited to caller-requested FR-258 inline traces, which NFR-490 bounds.

**Why.**
1. **NFR-489 measures what the caller waits for, server-side, and the caller waits for the
   sampled write.** It is awaited before the response is returned (`score.py:610-612`), on a
   default the caller cannot turn off (`settings.py:217-219`).
2. **OQ-1453's ground for excluding traces is absent here.** It excluded inline traces because
   the caller asked for them and NFR-490 bounds them (`03:1602`). A background sample has
   neither property. Excluding it would leave it unbounded, or need a new NFR (option (b)).
3. **(b) buys no compliance on the evidence.** At rate 0 the lowest no-GBM p99 is still
   21.270 ms handler and 23.930 ms client (LG-1760 `:688`). Excluding the sampled requests would
   narrow what is measured without closing the gap. That is the "change a target because it was
   missed" that RL-1837 item 4 refuses.
4. **Deciding now costs nothing in P2 and saves a session's worth of rungs.** The P2 verdict
   on the no-GBM limb is the same under all three options. But (c) makes the ladder session
   measure two rates, and it leaves the remedy's counted unit undefined.

**What this does not decide.**
- The 15 ms figure itself. It is reviewed in P3 through an OQ, on the 200 rps readings
  (RL-1837 item 4).
- How large the sampled write's cost is. H2 is one run per rate (LG-1760 `:687`), so its 5.8 ms
  p99 difference on one arm and 0.5 ms on the other size nothing. A repeat at both rates is
  needed before a remedy is sized on it.
- Where the sampled write should run. That is WK-674's to plan under FR-259.

## What it obliges

- **NFR-489** (`03:1559`) gains one dated clause at this record's mint, in the same commit as
  this record (a spec edit is never made without its ruling in the same commit):
  *"(Clarified <mint date>, OQ 8145 / RL 8218: the ceiling includes requests FR-259's
  background sampling persists, at the production default `rating.trace_sample_rate`, and the
  decline and error floor; OQ-1453's exclusion is limited to caller-requested FR-258
  traces.)"* The ids are written in their minted form at the mint.
- **OQ 8145**, in both mirrors (`docs/open-questions.md` and `03` §10), mints as decided (a),
  citing this record as the resolver. It gets a `docs/roadmap.md` §10 decision-gate row in the
  same commit. The branch @abb13d5b adds no gate row.
- **The ladder protocol** (LG-1760, pre-registered) is unchanged. Every NFR-489 reading of
  record runs at the default rate and states the rate in its output header beside N.
- **WK-674's off-path remedy** (RL-1837 item 3), when it is cut, has two more obligations:
  - the RL-1685 guard gains a second counted unit, one sampled request, red first;
  - the remedy's plan says where the sampled write runs.

  Nothing is cut by this record.
- **FD-1836**'s register row: its discharge event "the decision-maker's ruling on the spec
  question" is met at this record's mint. The finding stays open as the carried no-GBM limb,
  owner WK-674, under RL-1837.

## For the lead (not ruled here)

1. **The Mon 26 Oct date.** RL-1837 items 1 and 2 put the carry-forward on Mon 26 Oct, naming
   *"whichever limbs miss, at which rates"* after a full-ladder session. That session was
   cancelled (to-lead "2026-10-21 16:46:50 BST", *"CANCELLED: the 18:05 NFR-489 full-ladder
   session"*). No 50–200 rps reading exists for either arm. The date is the user's to move,
   through the maintainer. This record does not move it.
2. **Minting.** This record and OQ 8145 mint together, in one records PR. The OQ comes first in
   merge order, because this record resolves it. The NFR-489 clause and the §10 gate row go in
   the same commit. OQ 8145's working id is not in `relates:` here, so check 31/32 flags only
   this record's own id. Add it to `relates:` at the mint.
3. **Record form.** This binds beyond one slice (an NFR's scope), so it is an `RL-` under Lean
   P2 L1, not an LG line.

## Acceptance — the violation that must become detectable

- *Violation: an NFR-489 reading of record is taken at `rating.trace_sample_rate` 0, or its
  header omits the rate.* Caught by reading the session's output header against LG-1760's
  pre-registration, at the session's audit.
- *Violation: the off-path remedy merges with the RL-1685 guard still counting only a
  rate-0 request.* Caught at that slice's audit: the guard file has no sampled unit.
- *Violation: a later record excludes background samples from NFR-489 without superseding this
  ruling.* Caught by `supersedes:` and the NFR-489 clause history at review.

No check can fail on broken input for this record's own text. It decides what a measurement
counts. The checks above are the ones that enforce it.
