---
id: RL-9983
family: ruling
title: PL-1342 DP-S3-1 decided — a ladder that does not reconcile refuses the quote with LADDER_RECONCILIATION_FAILED on every scoring path, and the refusal is logged and counted
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 36b2a121662b9d69a309fee0e8023fbfff3a71ea
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1342, SL-1257, RL-1329, RL-1343, FD-1336, FD-1330, FR-248, FR-254, FR-255, FR-259, FR-261, NFR-495, NFR-496, NFR-497, NFR-499]
---

# RL-9983 — PL-1342 DP-S3-1 decided: a ladder that does not reconcile refuses the quote with `LADDER_RECONCILIATION_FAILED` on every scoring path, and the refusal is logged and counted

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-s3dp`, which also ruled DP-S3-2
(the ruling filed under working id 9984, draft PR #1024). Its first command, `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`, printed
`CLAUDE_EFFORT=high`. The lead spawned it on the maintainer's spawn order (`to-lead.md`, a
local channel file outside the repository, the entry "2026-09-30 22:31:50 BST", as the lead's
brief relays it; this session did not read that entry). PL-1342's row asks for "the
decision-maker at medium effort". The charter's Model / effort line
(`.claude/roles/decision-maker.md:13`) allows high "for a decision-maker ruling … on the
maintainer's raise". The lead has flagged the difference to the maintainer.

**Working id 9983**, hand-assigned by the lead, who is the only allocator (`FD-1338`). Not minted.

**The question, as filed.** `PL-1342:405`, DP-S3-1, *"What does a failed ladder reconciliation do
at scoring?"*, blocking Task 6. The options are (a) refuse the quote with
`LADDER_RECONCILIATION_FAILED` (500, a platform fault), and record it; (b) serve the quote,
record the failure on the trace (when there is one) and in the log, and alert. Option (c),
refuse outside `prod` and serve in `prod`, was withdrawn on 2026-09-30 (auditor-close1255 N4),
because it brings back the `prod` special case that the maintainer's decision removed. The
row recommends (a). `RL-1329` leaves the question here three times (`RL-1329:378`, `:452`,
`:699`: "What a failure does is DP-S3-1's"). The WK-674 Slice 3 dispatch record
(`~/gi-pricing-plan.local/handover/DISPATCH-WK-674-S3-2026-09-30.md`, a local file) holds
Task 6's failure behaviour until this ruling mints (its "Delta 1", 2026-09-30 23:38:06 BST).

## Verified first, at 36b2a121662b9d69a309fee0e8023fbfff3a71ea

`origin/main` was `36b2a121` when this session fetched it (2026-09-30, about 23:30 BST, and
again at 23:52 BST). Every citation below was re-read there with `git show origin/main:<path>`.

**What a failure of `RL-1329`'s predicate means.** `RL-1329` §5 checks the ladder against inputs
read from the evaluated result and the algorithm, never from the ladder: each rung's engine value
`E(rung)`, its declared rounding `D(rung)`, the priced payable, and each clamp step's reads. A
failure is one of these:
- **R1–R4.** The recorded ladder does not explain the price. A rung's value is not the engine's
  value, a display is not its value rounded once, an operation does not explain its rung, or the
  replay does not reach the priced payable to the penny.
- **R0, a clamp whose comparison and disposition disagree.** The authored `condition` and
  `clamp_bounds` contradict each other, and "the platform cannot say which one priced the quote"
  (`RL-1329:374-378`). Here the price itself is in doubt, not only its explanation. `RL-1329`
  (S5) says this "can fail every binding quote of a valid version".
- **A bundle compiled before Slice 3** with a clamp that the new save-time check refuses. Live
  scoring does not recompile, so "on a quote where its clamp binds, R0 fails at runtime, and
  DP-S3-1 decides what that does" (`RL-1329:450-452`).
- **The residual risk.** A recovered operation can flip the payable penny only at an exact tie
  within about 10⁻²² (`RL-1329:692-699`). "If it ever happens, the check fails loudly and
  truthfully."

A failure is **deterministic**. The same bundle and the same Quote Context give the same result
(`03` NFR-495), so a failing quote fails every time it is scored.

**The one evaluator.** `build_scoring_result` (`packages/pricing-core/src/pricing_core/rating/score.py:747-789`)
is the shared tail of `score_one` (`:791`) and of `score_batch`'s sync path (`_score_context_sync`,
`:960`, "the shared `build_scoring_result` tail (RL-858)"). It calls the check at `:769` and passes
the verdict only to `_build_trace` (`:771-776`). The `ScoringResult` it returns has no
reconciliation field (`:778-789`; `model_schema/scoring.py:171`). `Trace.ladder_reconciled` is the
only place the verdict is recorded (`scoring.py:168`), and `/score` builds a `Trace` only when the
caller asks for one.

**How each path treats a coded refusal today.**
- **`pricing-core`'s convention** is `_raise_named(code, message)`, a `CodedError` (a `ValueError`),
  because `pricing-core` cannot import `PlatformError` (`score.py:309-315`).
- **`POST /api/v1/score`** calls `score_one` at `backend/src/app/api/score.py:312` and maps a
  `CodedError` through `_as_platform_error` (`:255-273`). That maps only the four codes in
  `_PER_QUOTE_CODES` (`:93-101`), to 422 (`:103`). Any other code returns `None`, and the route
  re-raises it (`:313-317`), so it reaches the caller as a 500 **without its code**. A refusal is
  raised before `_maybe_sample_trace` (`:319`), so no pending trace row is written for it.
- **`POST /api/v1/score/compare`** uses the same mapping and names the failing side (`:361-367`).
- **Batch.** `_score_batch_row` catches `ValueError` per row (`score.py:1010`) and writes an
  `"error"` row whose `error_code` is parsed from the coded message (`_batch_error_code`,
  `:921-933`). The run continues, and FR-255 counts the row by its type.
- **Golden quotes.** `_evaluate_one` catches `ValueError` and records the quote as `fail`, "never an
  abort of the rest" (`packages/pricing-core/src/pricing_core/rating/golden.py:43-58`).
- **The FR-261 property.** `make_scorer` turns a `ValueError` into `None`
  (`packages/pricing-core/src/pricing_core/rating/properties.py:105-117`), and `case_holds` returns
  `False` for a `None` result (`:289-290`), so the case is a counterexample.
- **The trace producer.** `score.trace_produce` re-scores a pending trace with `score_one`
  (`backend/src/app/worker/trace_handlers.py:98`). A `ValueError` there fails the Job.

**The code.** `LADDER_RECONCILIATION_FAILED` is registered (`backend/src/app/errors.py:339`) and
owned by `03` §5.1 (`03:783`), with no status stated. It is raised nowhere. The worker census
lists it among the codes that a quote input can reach (`backend/tests/test_worker_raise_sites.py:36-39`).

**The requirements.**
- **`03` FR-248** (`03:155`): "the ladder reconciles exactly"; as amended by `RL-1329`, the replay
  "gives `payable_premium` to the penny".
- **`03` NFR-496** (`03:1165`): "the ladder reconciles to the penny in 100 % of scored quotes".
- **`03` NFR-497** (`03:1166`): availability "targets 99.95 % monthly".
- **`03` FR-255** (`03:167`): "Scoring errors are typed and per-quote".
- **`03` FR-259** (`03:176`): traces are sampled "plus 100 % of declines and errors".
- **`CLAUDE.md` §1**: every design decision favours "transparency of the maths". **`FD-1336`**'s
  disposition: "The stored flag must never read `true` for a ladder that has not been checked."
  The dispatch record's D1 item 4: an exceedance is reported "with no looser fallback".

## Options, weighed

- **(b), serve and record: rejected.**
  - **On the default path, nobody who receives the quote would know.** `/score` scores untraced
    unless the caller asks (`score.py:4-13`), and `ScoringResult` has no reconciliation field. So
    under (b) a Consumer System receives a Premium Ladder that the platform knows is false, with
    nothing in the response to say so. The ladder carries amounts that a Consumer System may show
    or book, such as the IPT and fees rung. Adding a flag to `ScoringResult` would be a contract
    change that no requirement asks for, and every consumer would have to read it.
  - **In the R0 case the price is in doubt,** not only the ladder. Serving it may be a
    mispricing, which `CLAUDE.md` §2 names as the failure a governed platform must not allow.
  - **NFR-496 would become false** for each served failing quote, and it would be recorded after
    the fact. A requirement that the platform knowingly breaks at serve time is not being met.
  - **"Alert" has nowhere to go in Phase 2.** Alert routing is `07` FR-453's, owned by WK-688 in
    Phase 4 (`OQ-1233`, `RL-1252`). Under (b), "alert" would be a log line and a counter. That is
    the same signal that (a) gives, but after a false quote has been served.
- **(a), refuse: adopted.**
  - **Every served quote's ladder reconciles.** NFR-496's "100 % of scored quotes" then holds for
    every quote the platform answers, and the counter below measures how often a quote is refused.
    The check still runs on every quote. The refusal is its outcome, not a replacement for it.
  - **The signal reaches the caller, untraced or not.** The plan's reason stands: "a refusal is
    also the one signal that surfaces an untraced failure without a log search".
  - **The availability cost is bounded.** A failure is deterministic (NFR-495). So it shows up
    in `uat` before `prod`, because `07` FR-429 needs a `uat` deployment first. It also shows up in
    a Rating Version's golden quotes and FR-261 properties before approval. `RL-1329` makes Slice 3
    count, and stop on, any fixture, committed suite or reachable stored bundle that would fail.
    There is no production tenant. What is left is a version that fails on some quotes in `prod`
    only. Refusing those quotes is the correct outcome, because its prices cannot be explained.
  - **One behaviour on every path.** `build_scoring_result` is the one evaluator (FR-254). A
    refusal raised there gives the same verdict on `/score`, `/score/compare`, batch, golden
    quotes, the FR-261 property and the trace producer, and no path needs a policy of its own.
- **500, not 422.** The existing 422 means "the quote is well-formed but cannot be priced as
  given" (`score.py:102-103`). That tells the caller to change the input. Here the input is valid
  and the fault is the platform's, or the Rating Version's. The plan's option (a) says 500 for
  this reason. A 500 **without** its code, which is what the route does today with an unmapped
  code, would hide the reason. So the 500 carries the code.
- **No retry advice.** The failure is deterministic, so a retry fails the same way. The problem
  response says so, and it carries no `Retry-After`.

## Ruled

### 1. Option (a): a ladder that does not reconcile refuses the quote

**When `RL-1329` §5's predicate is false for a scored quote, that quote is not served.** This
holds for a `quoted` and for a `declined` outcome (a declined quote's ladder reconciles too,
FR-256), in every Environment, whatever the trace-sampling rate. The check runs on every scored
quote, as the maintainer decided on 2026-09-30 (the entry headed "2026-09-30 15:17:54 BST — audit
round-up: decisions", as `PL-1342` quotes it). An empty ladder, which `RL-1329` §5 names as the one
case that returns True, is not refused.

### 2. Where it is raised: once, in the shared evaluator

- **`build_scoring_result` raises it**, through `_raise_named("LADDER_RECONCILIATION_FAILED", …)`,
  after it computes the verdict and before it builds a `Trace` or a `ScoringResult`. There is
  one raise site. No caller decides the policy again.
- **`reconcile_ladder` stays a predicate.** It returns a bool, and its unit tests call it directly.
  Only `build_scoring_result` turns False into the refusal.
- **So every `Trace` that `score_one` builds has `ladder_reconciled: true` and
  `ladder_check_version: 2`.** A version-2 trace with `ladder_reconciled: false` cannot be
  produced. The field stays in the contract: stored pre-Slice 3 traces carry it with a version
  that is absent or 1, and it records the verdict explicitly. This meets `FD-1336`'s rule that
  the stored flag never reads `true` for a ladder that has not been checked.

### 3. The message: input-free

The message is `LADDER_RECONCILIATION_FAILED: <clause>: <rungs>: <difference>`, as the executor
spells it. It carries only:
- the clause of `RL-1329` §5 that failed (`R0`–`R4`);
- the name of each rung involved, and for R0 the clamp step's id;
- for R1–R4, the difference in minor units as a positional decimal string (`PositionalDecimalStr`
  rendering, `RL-1329` §3), for example `replay 70725 != payable 70726`.

It carries **no quote input**: no input name with its value, and no `quote_id` (NFR-499,
`RL-917`). Rung names, step ids and derived minor-unit amounts are not quote inputs. The census
tests cover the new raise site (below).

### 4. The response on each path

- **`POST /api/v1/score`: 500, a problem with code `LADDER_RECONCILIATION_FAILED`**, title
  "Ladder reconciliation failed", and the message as `detail`. The backend maps this code
  explicitly. It is not added to `_PER_QUOTE_CODES`, which are 422. The mapping is a second,
  named case beside `_as_platform_error`'s, so no other unmapped code gains a status. The detail
  also says the failure is deterministic for this Rating Version and quote, and there is no
  `Retry-After`. The route's OpenAPI `responses` adds 500, and the contract is regenerated
  (FR-451).
- **`POST /api/v1/score/compare`: the same 500, naming the failing side** (`base` or
  `comparison`), through `_naming_side`, as for the per-quote codes.
- **Batch (`score_batch`): an `"error"` row** with `error_code` `LADDER_RECONCILIATION_FAILED` and
  the input-free message. The run continues, and FR-255 counts the row by its type. The run
  aborts only past the declared threshold, as for any other error type. This is what the existing
  per-row catch already does with a coded error, so batch needs no new code, only a test.
- **Golden quotes and the FR-261 property:** the refusal is a failed case. `make_scorer` already
  maps it to `None`, and `case_holds` returns False. So the `LadderReconciles` property fails on a
  quote whose ladder does not reconcile, which FR-261 asks for. `RL-1329`'s false-positive control
  stops Slice 3 if any committed suite has such a case.
- **`score.trace_produce`:** a re-score that fails ends the Job with the code. This can happen only
  to a pending row served before Slice 3 and completed after it (`RL-1329` §4 discloses that
  window). No production tenant exists, so the window is empty today.

### 5. What is recorded

- **The caller's problem response**, above.
- **One `ERROR` log line per refusal on `/score`**, from the route. It holds the code, the
  message, `rating_version_ref`, `bundle_hash`, the workspace id and the Environment, and nothing
  from the Quote Context. **`/score/compare` logs nothing**, because its route says "Nothing is
  persisted or logged (NFR-499)" (`backend/src/app/api/score.py:345`). Its caller is the analyst
  who asked, and that caller receives the refusal.
- **A Prometheus counter, `gip_ladder_reconciliation_failed_total`**, with one label,
  `environment` (an empty string for a caller with none). It is incremented once per refusal on
  `/score` (`backend/src/app/observability/metrics.py`; the label set is bounded, `:3-9`). Batch
  refusals are counted in the Job's own per-type counts (FR-255), not here.
- **No alert routing is built.** The counter is what an operator's alert rule reads. Routing
  belongs to WK-688 in Phase 4 (`07` FR-453), and building it now would build ahead of the phase
  (`CLAUDE.md` §9).
- **Error traces: unchanged, and not ruled here.** This ruling leaves `/score`'s `scoring_traces`
  behaviour as it is at `36b2a121` (FR-259's error floor on `/score` is an open question; see
  "Observed, not ruled").

## What it obliges

WK-674 Slice 3, Task 6 (`PL-1342:458-469`), with `RL-1329`:
- `build_scoring_result` raises the refusal of rule 2, with the message of rule 3.
- `backend/src/app/api/score.py`: the explicit 500 mapping on `/score` and `/score/compare`, the
  `ERROR` log line on `/score` only, 500 in both routes' OpenAPI `responses`, and the contract regenerated.
- `backend/src/app/observability/metrics.py`: the counter. **This file is not in `PL-1342`'s
  write set or in the dispatch record's.** The DP-S3-2 ruling (working id 9984) also adds it, for Task 5. The lead adds it for
  Task 6 too, with the RL-1263 check.
- The census: the new raise site is added to
  `packages/pricing-core/tests/test_quote_input_raise_sites.py`, with a sentinel case driven
  through `score_one` **and** `score_batch`, and the worker census stays green (`PL-1342`
  Acceptance 10, "the raise site's message").
- Two docstrings. `score.py`'s "Ladder construction" section (`:62-103`, which says the ladder
  "reconciles **by construction**") is rewritten under `RL-1329`; the rewrite also states this
  refusal. `_PER_QUOTE_CODES`'s comment (`backend/src/app/api/score.py:90-92`) says a code outside
  the set "reaches the caller as a 500". It gains the named exception of rule 4.
- `03`: the spec changes below are this ruling's. Slice 3 does not reword them.

## Acceptance — the violation that must become detectable

Each case is red first on the slice's base, before the refusal is added. The ladders are built
by Slice 3's real builder. "Planted" means a test-only mutation of the builder's output, recorded
in the ledger with its red run.
1. **Through `score_one`, traced and untraced.** On a ladder with one rung planted one minor unit
   off, `score_one` raises `CodedError` with code `LADDER_RECONCILIATION_FAILED`, with
   `trace=True` **and** with `trace=False`. Red first: it returns a result.
2. **An authored R0 case, not planted.** A clamp step whose `condition` and `clamp_bounds` disagree
   on a binding quote (`RL-1329` S5) is refused through `score_one`. Red first: it is served.
3. **Through the route.** `POST /api/v1/score` on case 1's quote answers 500 with an RFC 9457 body
   whose `code` is `LADDER_RECONCILIATION_FAILED`. The body and the log line do not contain a
   sentinel planted in a quote input. This case's `scoring_traces` behaviour is unchanged from
   `36b2a121` and is not asserted here (FR-259's error floor on `/score` is an open question).
   `gip_ladder_reconciliation_failed_total` rises by 1 for that Environment. Red first: 200.
4. **Never sampled.** With `rating.trace_sample_rate` set to 0, case 3 is refused the same way.
5. **Compare.** `POST /api/v1/score/compare`, with the failing version on either side, answers 500
   with the code, and the detail names that side.
6. **Batch.** `score_batch` over a frame holding case 1's quote and a good quote writes one
   `"error"` row with `error_code` `LADDER_RECONCILIATION_FAILED` and one scored row. The Job's
   per-type counts show one. The message does not contain the sentinel.
7. **The FR-261 property.** A Regression Suite whose `LadderReconciles` property meets case 1's
   quote records it as a counterexample. Red first: the property holds (the check was vacuous).
8. **The census.** The raise site is in the pricing-core census, and a message that carries an
   input value fails it (red on broken input).
9. **Controls.** A correct ladder is served (200) with `ladder_reconciled: true` and
   `ladder_check_version: 2` on its trace, and an empty ladder is not refused. `RL-1329`'s
   false-positive control over every fixture and committed suite has **no** refusals. A count
   above 0 stops the slice for the lead.

## Spec changes in this commit

- **`03` FR-248** gains a dated clause: a quote whose ladder does not reconcile is refused with
  `LADDER_RECONCILIATION_FAILED` on every path, and the refusal is logged and counted.
- **`03` §5.1**, the owned-code list: `LADDER_RECONCILIATION_FAILED` gains its status and meaning
  (500; 500 naming the side on `/score/compare`; an error row in batch; input-free). Its route
  table's `/score/compare` row gains the same 500 (added on audit, M2).
- **Not edited here:** NFR-496 and FR-259. `PL-1342` Task 1 gives FR-248 and NFR-496 their
  "never sampled" clauses on the slice branch. This commit's FR-248 clause is on the same table row,
  so whichever lands second keeps both clauses when it merges (a one-row textual conflict).
  `PL-1342`, `RL-1329` and `FD-1336` are frozen and are not edited.

## Observed, not ruled (for the lead)

- **FR-259's error floor on `/score`.** `decide_sampling` persists every `error` outcome
  (`backend/src/app/platform/traces.py:94-97`), but on `/score` a per-quote error is raised before
  sampling (`backend/src/app/api/score.py:312-319`). So no error outcome reaches it on that path,
  for any code. Whether that meets FR-259's "100 % of … errors" is not ruled here. It predates
  this ruling and applies to all four per-quote codes too.
- **A refused case in a Regression Run is recorded without its code.** `make_scorer` turns any
  refusal into `None` (`properties.py:113-114`), so every property in the suite fails on that case,
  and the counterexample does not say which code refused it. This predates this ruling.
- **The write set.** `observability/metrics.py` joins Task 6's write set (above).
