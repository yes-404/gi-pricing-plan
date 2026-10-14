---
id: RL-1712
family: ruling
title: FR-259's "errors" on the real-time path — the term was undefined and the code is not wrong; Option A, a refused quote is not traced, with the FR-259 and WF-701 C7 texts and the C7 assertion that follows
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-14
owner: decision-maker
tree: 1e260c1553acf39844939fe12da685ccfb835e54
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1706, FR-259, FR-255, FR-256, FR-258, FR-248, FR-331, NFR-459, NFR-499, RL-862, RL-877, RL-890, RL-1346, RL-1434, WF-701, WK-1178, WK-674, PL-1544]
---

# RL-1712 — FR-259's "100 % of errors" against `POST /api/v1/score`: the §0 question ruled

*(Minted 2026-10-14 as RL-1712 from working id 8019, in the D16 batch mint PR.)*

*Disclosure: drafted under **working id RL 8019**, reserved by the lead (team-lead) on
2026-10-14 (`~/gi-pricing-plan.local/handover/eta.md`, the line stamped "2026-10-14 10:12:07
BST": "RESERVED working id RL 8019 = FD 8011's §0 ruling (A/B/C: FR-259 "100% of errors" vs
/score raising before the sampler), for D16"). The finding is FD-1706 (working id 8011),
filed on `origin/fd-8007-8011-2026-10-14` @`3d6e0f0a67575e71eae3162566275ef8042be1c1` and folded
into D15, which minted it as FD-1706; the D16 mint sweep replaced both working ids below with
their minted ids.*

*Confirmed: dated 2026-10-14, on the maintainer's (by delegation) entry "2026-10-14 10:26:21 BST
— RL 8019 (FD 8011, FR-259 "errors") CONFIRMED as drafted; (i)–(iii) accepted (re lead 10:25:44)"
(`to-lead.md`): "RL 8019 @b26af93f: CONFIRMED, reading (c), option A′."*

## How this was ruled

- **The question is the maintainer's (by delegation), who orders this record.** The entry
  "2026-10-14 10:11:47 BST — FD 8007 severity: MEDIUM + re-rate trigger CONFIRMED; FD 8011: seat
  a decision-maker (re lead 10:11:23)" in `~/gi-pricing-plan.local/channel/to-lead.md`,
  verbatim in the part relied on: *"The question is §0's (code wrong / spec over-broad / term
  undefined), it binds the exit demo (C7 is in row 2), and its resolution lands before 12 Nov.
  The DM rules A/B/C as a working-id RL. That RL rides D16, and any fix gets its own slice row.
  If it is ruled "spec over-broad" or "term undefined", the spec clarification text is the RL's
  T-text."*
- **The finding's framing is the same author's**, the entry "2026-10-14 10:00:17 BST — RULED:
  WF-701 demo DP-W0..W5 …", item (A) DP-W5, verbatim in the part relied on: *"FR-259's
  2026-10-05 clarification (RL-1434) defines a trace body as a re-score compared with the
  SERVED result, and an errored quote has none. So "a trace of an error" is undefined, not
  merely unsampled. … Its resolution (a spec clarification or code) must land BEFORE the 12 Nov
  exit demo: C7 is inside row 2, so the exit demo cannot carry a KNOWN GAP on it."* Its id
  correction "2026-10-14 10:00:28 BST" moves the finding off the first-offered id and changes
  nothing else.
- **The lead's relay**, read and not relied on for any fact below: "2026-10-14 10:11:23 BST" and
  "2026-10-14 10:12:07 BST" in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`. The
  lead's 10:13:05 entry there names a separate fact: `score.trace_produce` is routed to the
  `scoring` queue, which no worker consumes today. That is the maintainer's to rule, and this
  record does not rule it (see "What this record does not decide").
- **The effort condition** of the 10:11:47 entry ("effort high, a separate CLI, verified by
  transcript") is met: the lead's entry "2026-10-14 10:13:05 BST — Lead: dm-fd8011 EFFORT
  VERIFIED HIGH" in the same from-lead file.

## Verified first, at `1e260c15`

Every line is read in this record's worktree, which is checked out at
`origin/main` = `1e260c1553acf39844939fe12da685ccfb835e54`.

1. **The requirement.** `docs/specs/03-rating-engine.md:180`, FR-259, opens: *"In production,
   traces are **sampled** (default 1 %, configurable, plus 100 % of declines and errors) and
   persisted for ≥ 13 months (NFR-459), feeding `05-monitoring.md`."* Its three dated
   clarifications (2026-08-29 `RL-890`, batch is not in the stream; 2026-08-30 `RL-916`, the
   served environment; 2026-10-05 `RL-1434`, the reproduction status) are read to the row's end.
   None of them says what "errors" means.
2. **Where the word came from.** The row's text was written in commit `f8704bb9`
   (2026-08-14T09:38:17Z, "docs: specify the rating engine (03)"; `git log -S'100 % of declines
   and errors' -- docs/specs/03-rating-engine.md` prints only that commit). At that commit the
   scoring response's example shape carries `"outcome": "quoted | declined | error"` (`03` at
   `f8704bb9`, line 326). So the author's "errors" was **a served result with `outcome =
   "error"`**, the third member of what is now `ScoringOutcome`
   (`packages/model-schema/src/model_schema/scoring.py:75`).
3. **The real-time path stopped serving that outcome.** `RL-877` (created 2026-08-29) records
   that `score_one`'s refusals are code-named `ValueError`s *"and the mapping to `PlatformError`
   happens at the backend boundary in Slice 2"*. The model's own comment
   (`scoring.py:70-74`) says `"error"` *"is not produced by `score_one` today"*. In the route,
   `backend/src/app/api/score.py:421-427` maps the refusal and raises it, and `:429`, the only
   call of `_maybe_sample_trace`, is never reached. The mapped codes are `_PER_QUOTE_CODES`
   (`:100-107`) as 422, and `LADDER_RECONCILIATION_FAILED` as 500 (`:110-115`, `RL-1346`). An
   unmapped `ValueError` re-raises at `:424` as a 500.
4. **A trace is defined over a served result.** The glossary: *"**Trace** — The per-step record
   of a single scoring call … The backbone of explainability and dispute resolution."*
   (`docs/specs/00-overview.md:170`). FR-259's 2026-10-05 clarification: the body is *"a
   deterministic re-score of the pinned bundle, and that re-score is compared with the result
   actually served (`RL-862`, condition (b))"*, with `status` `complete` or `mismatch`. In code,
   the served side is `summarise_result(result)` over a `ScoringResult`
   (`backend/src/app/platform/traces.py:143-157`), and the mark is `traces.py:257`.
5. **A refusal leaves nothing to re-score into a body.** `score_one`
   (`packages/pricing-core/src/pricing_core/rating/score.py:920`) evaluates in one `try` around
   `bundle.decision.async_evaluate(context, {"trace": trace})` and re-raises an engine failure
   (`_reraise_engine_failure`). No partial trace is returned. Input-contract refusals are raised
   in `_validate_inputs` (`:330-375`), before evaluation. The trace job re-scores with
   `score_one(compiled, ctx, trace=True)` (`backend/src/app/worker/trace_handlers.py:98`), so it
   would raise the same code. The route says so of the ladder refusal (`_LADDER_REFUSAL_NOTE`,
   `score.py:113-115`: *"a retry fails the same way"*). A row with no body is not listed
   (FR-259, 2026-10-05 clarification: *"A trace still awaiting its re-score, or one whose pinned
   bundle could not be resolved, has no body and is not listed."*).
6. **`RL-862` assumed error traces and did not define them.** Its ruling sentence: *"Where FR-259
   requires a trace — every decline, every error, and the sampled fraction — the trace is
   produced by re-scoring the same Quote Context against the same pinned bundle"*. Its condition
   (b): *"The persisted trace must be checked against the premium actually served"*. `RL-862`
   and `RL-877` were both created 2026-08-29. Neither says what "the premium actually served"
   is for a refused quote.
7. **No consumer of an error trace is named in the suite.** `05-monitoring.md` FR-317's
   2026-08-26 note (`OQ-627`): *"trace sampling stays for quote-level metrics — conversion,
   declines, latency, constraint activation"*. Errors are not in that list. The error rate is
   FR-331's (`05:130`, *"error rate by error code, and decline rate by reason code are tracked
   per environment and per Rating Version"*), sourced from the metrics backend: `05` §8's
   OpenTelemetry row names *"Operational metrics (latency, errors)"* as its use, and `OQ-628`'s
   decision keeps operational metrics there. WF-701's own D1 reads *"error rate
   flat"* from FR-331 (`docs/workflows/WF-00701-deploy-and-monitor.md`, row D1).
8. **What records a refusal today.** `gip_http_requests_total` counts responses by route and
   status class (`backend/src/app/observability/metrics.py:51-56`). A ladder refusal is logged
   and counted per Environment (`gip_ladder_reconciliation_failed_total`, `metrics.py:74-79`;
   `_record_ladder_refusal`, `score.py:434-451`, `RL-1346` §5). No per-code counter exists for
   the 422s. That is FR-331's, in monitoring's phase, and this record does not build it ahead
   of that phase.
9. **The same promise in the journey.** `WF-00701-deploy-and-monitor.md:67`, C7: *"Samples 1 % of
   traces, plus 100 % of declines and errors, and persists them."* No other text in
   `docs/specs/`, `docs/workflows/`, `docs/open-questions.md` or `docs/roadmap.md` matches
   `grep -rniE '100 ?% of (declines|errors)|declines and errors|every error'` (two hits:
   `03:180`, and row C7 of WF-701 at line 67 of its file).

## Ruled

### 1. Which side is wrong (`CLAUDE.md` §0): reading (c), the term is undefined. The code is not wrong.

- **"Errors" in FR-259 named a served outcome that the real-time path no longer has.** The word
  was written against a response that could carry `outcome = "error"` (Verified 2). Since
  `RL-877`, a quote the real-time path cannot price is answered with a problem document and no
  `ScoringResult` (Verified 3). FR-259 never said which of the two it meant: a served
  `"error"` outcome, or a refused request. The two readings come apart exactly here. Under the
  first, the population on the real-time path is empty. Under the second, the spec has no
  definition of the thing it asks for (Verified 4–5). That is reading (c).
- **(a), "the code is wrong", fails because the code cannot be made to match.** Moving the
  sampling decision ahead of the raise gives `decide_sampling` no `outcome` and
  `summarise_result` no `ScoringResult`. The off-path re-score raises the same code, so the row
  is left pending, or it completes with no body as `mismatch`. In both cases it is never listed
  (Verified 5). The change would persist the quote input of every refusal for ≥ 13 months with
  no reader. `RL-862`'s own standard, *"A trace that silently does not match the quote it purports
  to explain is worse than no trace"*, refuses that.
- **(b), "the spec is over-broad", is the consequence of (c) once the term is defined, not a
  separate ground.** When "errors" is defined as the served outcome, the floor is over-broad on
  the real-time path, because it names an empty population there. The definition comes first,
  so the reading is (c).
- **`RL-862` is not corrected.** Its decision, which moves trace production off the request
  path, stands. Its words "every error" restate FR-259 as FR-259 then read, and it says *"no
  requirement is amended"*. The FR-259 clarification below governs what that restatement now
  means. `RL-862`'s body and front matter are not edited.

### 2. Option A, as the stated variant A′: define "errors" and say a refusal is not traced

**A′:** FR-259's "errors" is a scored result whose `outcome` is `"error"`. The floor stays in
force for any such result on the real-time path. Today the path serves none, so the 100 % floor
that operates there is the declines floor. A refused quote (422 with one of FR-255's per-quote
codes, or 500 `LADDER_RECONCILIATION_FAILED`) is not traced. It is observed through FR-331's
error rate by code and, for the ladder refusal, `RL-1346`'s log line and counter, none of which
holds a quote input. Tracing a refusal would be a new capability: it needs its own requirement
first. A′ differs from the finding's A in one respect only: it keeps the `"error"` floor as
defined, and does not delete it. `ScoringOutcome` still declares the member
(`scoring.py:70-75`), and a future real-time path that serves it then inherits the floor without
a further amendment.

**Why A′:**

- **It removes nothing that ever ran.** No refused quote has been traced on this route since the
  sampler was built (Verified 3). The clarification changes what the text promises, not what the
  platform does.
- **It is what the suite already relies on.** Monitoring takes errors from the metrics backend,
  not from traces (Verified 7). The journey's own D1 reads the error rate from FR-331.
- **A trace's purpose is a price.** The glossary names "explainability and dispute resolution".
  A refusal has no premium to explain or dispute, and `RL-862` (b) compares with *"the premium
  actually served"*.
- **It needs no contract change and no new store.** NFR-499 makes every quote-input store a
  named, access-controlled decision ("Any further store requires its own requirement"). A′
  writes none.

**Why B loses (define and implement the trace of an error):**

- It is a capability the spec does not define. B needs a served side for a problem document, a
  `Trace` that can end in a refusal (`score_one` keeps no partial trace today, Verified 5), a
  third `status`, a `model-schema` contract change, and a successor or amendment of
  `RL-1434`'s two-value mark. Under `CLAUDE.md` §0 that is spec first, then code, inside three
  weeks of the 4 Nov code freeze that the 10:11:47 entry names.
- It has no named consumer (Verified 7).
- It persists the full quote input of **every** refused request for ≥ 13 months, with a
  preservation floor (`TRACE_RETENTION_FLOOR`). An `INPUT_CONTRACT_VIOLATION` is by definition
  outside the contract, and a caller who sends bad input causes a durable write per request. Not
  measured; stated as a cost B would have to measure.

**Why C loses (B for platform faults, A for caller errors):**

- **Its split disagrees with the spec's own classification.** The finding's C puts
  `MODEL_CALL_FAILED` with the platform faults. The spec classes it as FR-255's fifth per-quote
  category, model failure (`RL-877`), and the route serves it as 422 (`score.py:100-107`,
  `_PER_QUOTE_STATUS` at `:117`). The only refusal the spec classes as a platform fault is
  `LADDER_RECONCILIATION_FAILED`, whose §5.1 annotation (`RL-1346`) reads *"A platform fault, not
  a per-quote 422"*. C therefore needs a reclassification before its own split exists.
- **The one platform fault is already recorded and guarded.** Each ladder refusal on `/score` is
  logged with the version, the bundle and the Environment, and counted (Verified 8). The
  reconciliation runs on every scored quote in every Environment (FR-248, `PL-1348`
  amendment). FR-261's property "the ladder reconciles" and the golden quotes are its
  pre-approval guards. A fault class can therefore be reproduced in `uat` with inputs the
  analyst holds.
- It carries all of B's definitional work for a population that should be zero in `prod`.
- Its demo limb cannot be walked as the demo is ruled. C7 would have to cause a platform fault in
  `prod`. Under DP-W4's standard for a demo candidate (*"the GOVERNED path only … no DB write, no
  status write"*), that means approving and deploying a deliberately broken version to `prod`.
- **What C gets right is noted and not ruled.** A deterministic platform fault in `prod` loses
  the quote input that would reproduce it. If the maintainer wants that input kept, that is a new
  requirement for a new access-controlled store (NFR-499's own rule), raised as an `OQ-` against
  `03` and owned by WK-1178. It is not FR-259's trace, and this record does not raise the `OQ-`,
  because no consumer is named anywhere in the suite.

### 3. The WF-701 C7 consequence: what the exit demo asserts for "errors"

C7's errors limb is **walked, not skipped, and is no longer a `KNOWN GAP`**. The demo slice
(DP-W0, WK-674) replaces the line `KNOWN GAP C7-errors: FD-<id>` (memo §4 acceptance item 2;
`PL-1544` Acceptance 2's form) with the assertion below, once the T-texts are on `main`:

1. With the prod key, `POST /api/v1/score` one quote that omits a declared non-nullable input
   (`_validate_inputs`, `pricing_core/rating/score.py:337-342`). Assert **422** and problem
   `code` = `INPUT_CONTRACT_VIOLATION`.
2. After C7's trace poll is stable, assert that **no** listed item of `GET /api/v1/traces`
   carries that quote's `quote_id`.
3. Print exactly one ruled line, `C7-errors: refused, not traced (FR-259, RL-1712)`, with the
   minted id, and assert it in the test as the memo asserts its other ruled lines.

Assertion 2 is an absence read through a route that lists only completed traces. It does not
prove by itself that no row was written. The proof that no row is written is the backend test
in "What it obliges" below, which reads `scoring_traces` directly. The demo cites that test by name.
**Nothing about errors at 100 % is asserted, and no fault is caused in `prod`.**

## What it obliges

### The texts and the minimal work they need (owner WK-1178)

The spec texts are proposed here and **are not edited into `docs/specs/` or `docs/workflows/`
by this record** (the brief and the 10:11:47 entry: "the spec clarification text is the RL's
T-text"). They are applied byte for byte under `.claude/skills/spec-change`, in **one commit**
with the test and the docstring below (`CLAUDE.md` §2). Where an applying plan's reading
differs from this text, this text wins.

Placeholders: `<date>` is the date of the applying commit. `RL-1712` and `FD-1706` were working ids
RL 8019 and FD 8011, replaced by their minted ids at the D16 mint. Nothing else is a placeholder.

**T1 — `03` FR-259, a fourth dated clarification.** File `docs/specs/03-rating-engine.md`.
Placement, read at `1e260c15`: in FR-259's row (`03:180`), insert immediately after the text
`` Ruled in `RL-1434`.)* `` that closes the 2026-10-05 clarification, before the row's
closing ` |`, separated by one space. The anchor: `` grep -cF 'Ruled in `RL-1434`.)* |'
docs/specs/03-rating-engine.md `` prints `1` at `1e260c15`. Insert:

```text
*(Clarified <date>, WK-1178 — what "errors" means in this row, written down because the real-time route refuses every quote it cannot price before the sampling decision, and the floor was read as unmet (FD-1706). "Errors" is a scored result whose `outcome` is `"error"`, and the 100 % floor applies to every such result on the real-time path. That path serves none today: a quote it cannot price is refused with a problem document and no `ScoringResult`, 422 with one of FR-255's per-quote codes or 500 `LADDER_RECONCILIATION_FAILED` (§5.1), so the floor that operates there is the declines floor. A refused quote is not traced. A trace's body is a re-score compared with the result actually served (`RL-862`, condition (b), and the clarification above), a refusal has no served result, and its re-score fails the same way. A refused quote is observed through the error rate by code (`05` FR-331) and, for a ladder refusal, through `RL-1346`'s log line and counter, none of which holds a quote input (NFR-499). Tracing a refused quote would be a new capability and needs its own requirement first. Ruled in `RL-1712`.)*
```

**T2 — `WF-701` C7, a dated amendment.** File `docs/workflows/WF-00701-deploy-and-monitor.md`.
Placement, read at `1e260c15`: in row C7 (`:67`), insert immediately after the text `plus
100 % of declines and errors, and persists them.`, before the cell's closing ` |`, separated by
one space. The anchor: `grep -cF 'plus 100 % of declines and errors, and persists them.'
docs/workflows/WF-00701-deploy-and-monitor.md` prints `1` at `1e260c15`. Insert:

```text
*(Amended <date>, `RL-1712`: "errors" is a served result whose `outcome` is `"error"`, and the real-time path serves none. A quote the platform cannot price is refused with a problem document and is not traced (`03` FR-259, the clarification of <date>). Its count is D1's error rate (`05` FR-331).)*
```

**The test and the docstring**, the rest of the write set:

- `backend/tests/test_score.py`: one test, `@pytest.mark.req("FR-259")`, parametrised over the
  five refusal codes. These are the four `_PER_QUOTE_CODES` (expect 422) and
  `LADDER_RECONCILIATION_FAILED` (expect 500). `score_one` is monkeypatched to raise
  `CodedError(f"{code}: …")` (the file's existing pattern, `:417`), and the trace sample rate is
  set to **1.0** (`_set_trace_sample_rate`). The test asserts the status, the problem `code`, and
  `_rows_for(database, workspace_id) == []`. At rate 1.0 a quoted result is sampled
  (`test_a_quoted_outcome_at_rate_one_is_sampled`), so an empty table here is the refusal's
  doing and not the roll's.
- `backend/src/app/platform/traces.py`: one sentence in `decide_sampling`'s docstring. The
  `"error"` floor is reached by no real-time path today, because a refusal is raised before
  sampling and is not traced (FR-259, `RL-1712`). The branch itself is unchanged.

**Reds by cause**, printed in the slice's `LG-` and then reverted:

- **R1.** A scratch edit in `score.py`'s `except ValueError` block that writes a pending
  `scoring_traces` row before `raise problem from exc` makes the new test fail with one row per
  code. Without such an edit the test is green on `main`, which is correct under A′: the test
  pins behaviour that already holds, and R1 is what proves it can fail.
- **R2.** The spec text, by anchor: after the commit, `grep -cF` of T1's first sentence in `03`
  prints `1` and of T2's in WF-701 prints `1`. `python3 scripts/audit-docs.py` passes except for
  the working-id checks the mint clears.

**The slice, as a planner can cut it.** It is one small row under WK-1178, red first as above,
with the write set exactly the four files named (`03`, WF-701, `test_score.py`, `traces.py`'s
docstring). It needs no contract regeneration and no migration. It lands **before the 4 Nov code
freeze**, because it carries a test, and in any case before the WF-701 demo slice's compose
rehearsal, which asserts §3 of Ruled against it. It discharges FD-1706 when merged. The planner may give
it its own slice or fold it into an open WK-1178 slice; that is the planner's call.

### What this record does not decide

- **The `scoring` queue that no worker consumes** (the lead's 10:13:05 entry). It affects C7's
  1 % limb and the declines limb, not this ruling's limb, which asserts an absence. It is the
  maintainer's to rule.
- **FR-331's per-code error counter.** It belongs to monitoring's phase. It is named here as
  where a refusal is counted, and it is not built ahead of its phase (`CLAUDE.md` §0).
- **The declines limb** (DP-W4 (a), the governed decline candidate). This ruling leaves it
  unchanged.
- **FD-1706's severity or closure.** The maintainer confirmed MEDIUM and owner WK-1178. The
  merge of the slice above discharges it, and the lead records that.
- **Whether to keep a platform fault's quote input** (§2, "Why C loses", last item). It is not
  raised here.

## Acceptance — the violation that must become detectable

The violation: **`POST /api/v1/score` refuses a quote and a `scoring_traces` row is written for
it**, or FR-259 is left saying "100 % of … errors" with no definition while the demo walks C7's
errors limb as a `KNOWN GAP`.

- *Violation: a refused quote writes a trace row.* The new `test_score.py` test, at sample rate
  1.0 over the five refusal codes, reds on the R1 scratch edit (a pending row written in the
  `except ValueError` block) with one row per code. This record cannot show that red itself,
  because the test is part of the slice's write set; the slice shows it red, with the scratch
  diff and the failure line in its `LG-`, before its merge.
- *Violation: the clarification is missing or altered.* At the applying commit, `grep -cF` of
  T1's first sentence in `03` and of T2's in WF-701 each print `1`, and each block is byte-equal
  to the text above with its placeholders filled. FR-259 still opens with *"plus 100 % of
  declines and errors"*: the text is clarified, not struck.
- *Violation: the demo still carries the gap.* `scripts/demo.py --journey wf-701` prints
  `C7-errors: refused, not traced (FR-259, RL-<minted>)` and no line containing
  `KNOWN GAP C7-errors`. With the T1 text absent from `main`, the demo slice keeps the
  `KNOWN GAP` line, so the exit demo cannot pass C7.

Drafted as working id RL 8019.
