---
id: FD-8011
family: finding
title: FR-259's "100 % of declines and errors" is not met for errors, and the spec and the code disagree on what a trace of an error is
status: active
created: 2026-10-14
owner: auditor
tree: 1e260c1553acf39844939fe12da685ccfb835e54
corrected_by: []
relates: [WK-1178, WK-674, WF-701, FR-259, FR-258, FR-250, FR-256, RL-862, RL-890, RL-1434, FD-1433, NFR-459, NFR-499, P2]
---

# FD-8011 — FR-259's "100 % of errors" is not met

*(Filed under working id 8011, the next free working id after the lead's free-check, because the
maintainer's (by delegation) id correction put the first-offered 8007 on FD-8007. A minter folds it
into the docs batch. Every `file:line` below was read at `origin/main`
`1e260c1553acf39844939fe12da685ccfb835e54`. The design memo is
`handover/memo-wf701-deploy-demo-2026-10-14.md`, section C7, in the local tree.)*

## Finding

**MEDIUM, owner WK-1178, to be resolved before the 12 Nov exit demo.** Authority: the maintainer's (by
delegation) entry "2026-10-14 10:00:17 BST — RULED: WF-701 demo DP-W0..W5", item (A) DP-W5, and its
id correction "2026-10-14 10:00:28 BST" (`channel/to-lead.md`). DP-W5 (a), verbatim:

> FD now (FD 8007 in D15), limb shown `KNOWN GAP C7-errors: FD-<id>`. Verified: in
> `backend/src/app/api/score.py` at origin/main, the `except ValueError` block raises the
> PlatformError before `_maybe_sample_trace` runs, and none of FR-259's three dated clarifications
> (2026-08-29, -08-30, -10-05) narrows "errors". **The FD must state the §0 question in full:**
> FR-259's 2026-10-05 clarification (RL-1434) defines a trace body as a re-score compared with the
> SERVED result, and an errored quote has none. So "a trace of an error" is undefined, not merely
> unsampled. Proposed severity MEDIUM, owner WK-1178. **Its resolution (a spec clarification or code)
> must land BEFORE the 12 Nov exit demo**: C7 is inside row 2, so the exit demo cannot carry a KNOWN
> GAP on it.

The first sentence's "FD 8007" was corrected by the 10:00:28 entry: *"The C7-errors FD takes the NEXT
free working id, after a free-check in its own call, never 8007."* Everything else in 10:00:17 stands.

The requirement says errors are sampled at 100 %. **No production error is ever sampled**, because
`POST /api/v1/score` turns every per-quote failure into an HTTP error before the sampling decision, and
the sampler is the only thing that writes a trace. The `decide_sampling` function carries the 100 %
floor for `outcome == "error"` and nothing on the live path can produce that outcome. That is the code
half. The spec half is deeper: even if the sampler were reached, **a trace of an error is not a thing
the spec defines**, so the code cannot simply be made to match the spec, and the spec cannot be read as
already describing the code. That is the `CLAUDE.md` §0 case, and it is stated in full below.

## Evidence

### 1. The requirement

`docs/specs/03-rating-engine.md:180`, **FR-259**, opening clause, verbatim: *"In production, traces are
**sampled** (default 1 %, configurable, plus 100 % of declines and errors) and persisted for ≥ 13
months (NFR-459), feeding `05-monitoring.md`."* It then carries three dated clarifications, which I read
to the end:

- **2026-08-29** (WK-671 Slices 3 and 4, `RL-890`): batch scoring contributes nothing to the sampled
  stream; the stream is the production real-time path.
- **2026-08-30** (WK-671 Task 4B, `RL-916`): what the environment on a sampled trace means.
- **2026-10-05** (WK-1178, `RL-1434`): *"A sampled real-time trace's body is produced off the serving
  request by a deterministic re-score of the pinned bundle, and that re-score is compared with the result
  actually served (`RL-862`, condition (b)). Each item of `GET /api/v1/traces` therefore carries
  `status`: `complete` when the re-score reproduced the served result, `mismatch` when it did not."*

None of the three narrows or defines "errors". The first clarification removes batch from the stream, so
a batch row with `outcome == "error"` is not an answer either (below).

### 2. The route raises before it samples

`backend/src/app/api/score.py`, `score` (decorated for `POST /api/v1/score`):

```python
    421    except ValueError as exc:
    422        problem = _as_platform_error(exc)
    423        if problem is None:
    424            raise
    425        if problem.code == _LADDER_REFUSAL_CODE:
    426            _record_ladder_refusal(caller, compiled, ref, problem)
    427        raise problem from exc
    428
    429    await _maybe_sample_trace(database, settings, caller, ctx, result, deployment_id)
```

(`:421` `except ValueError as exc:`, `:427` `raise problem from exc`, `:429` the sampling call; read with
`git -C /home/puzhenhao1989/gi-pricing-plan show origin/main:backend/src/app/api/score.py | sed -n '419,430p'`.)
The only call of `_maybe_sample_trace` in `backend/src` is that one at `:429`
(`git grep -n '_maybe_sample_trace' origin/main -- backend/src` prints `:429` and the definition at
`:509`). A `ValueError` that `_as_platform_error` (`:348-375`) maps is re-raised as a `PlatformError`
and the function never reaches `:429`. The mapped codes are `_PER_QUOTE_CODES` (`:100-107`):
`INPUT_CONTRACT_VIOLATION`, `RATE_TABLE_MISS`, `REFERENCE_LOOKUP_MISS`, `MODEL_CALL_FAILED`, with
status 422 (`_PER_QUOTE_STATUS`, `:117`), plus `LADDER_RECONCILIATION_FAILED` as a 500
(`_LADDER_REFUSAL_*`, `:110-115`; `RL-1346`). The ladder refusal is logged and counted
(`_record_ladder_refusal`, `:434`) and never traced. Any other `ValueError` re-raises at `:424` as a
500 and is likewise never sampled.

### 3. The sampler's 100 % floor is dead code on this route

`backend/src/app/platform/traces.py:78-99`, `decide_sampling`: `outcome == "declined"` returns
`(True, "decline")`, `outcome == "error"` returns `(True, "error")`, anything else is sampled iff
`roll < rate`. `SampleReason = Literal["rate", "decline", "error"]` (`:68`). So the code does hold the
floor, and the `error` branch is reachable by a call but not by the route: the model's contract says so
in a comment at `packages/model-schema/src/model_schema/scoring.py:70-74`: *"`error` is not produced by
`score_one` today — a per-quote refusal is a raised, code-named `ValueError` (RL-877), mapped to a
`PlatformError` at the backend boundary in Slice 2 — but the member is kept because the contract already
declares it"* (the enum is `:75`, `ScoringOutcome = Literal["quoted", "declined", "error"]`).

`outcome == "error"` is produced only by the **batch** path (`packages/pricing-core/src/pricing_core/rating/score.py:141-146`, the
batch output-row docstring, `_score_batch_row` at `:1175`; consumed at
`backend/src/app/worker/scoring_handlers.py:132`, `chunk.filter(pl.col("outcome") == "error")`), which `FR-259`'s
2026-08-29 clarification excludes from the sampled stream. The decline half of the floor is live: a decline
is a 200 with `outcome = "declined"` (`score.py:406-407` docstring, `FR-256`), reaches the sampler, and is
persisted at 100 %. (Whether a seeded quote can be declined is the demo's separate question, memo C7
limb 1; the `examples/fremtpl2` algorithm has no decline step.) The finding is the errors half only.

### 4. The §0 question: which side is wrong?

`CLAUDE.md` §0: *"When code and spec disagree, stop and resolve it rather than quietly making either
match the other. Which one is wrong is a real question."* There are three readings, and they give three
different remedies:

**(a) The code is wrong.** FR-259 says errors are traced at 100 %, and the route drops them. Remedy: sample
before raising.

**(b) The spec is wrong, or over-broad.** "Errors" in FR-259 was written when `ScoringOutcome` already
carried `"error"` as a possible result (it does, `scoring.py:75`), before `RL-877` made a per-quote
refusal a raised exception. On this reading the 100 % floor describes an outcome the real-time path does
not have, and FR-259 should say so.

**(c) Neither is wrong, because the term is undefined.** This is the reading the maintainer's (by
delegation) entry puts, and it is the one that makes (a) not simply implementable. `RL-1434`'s
clarification, which is now part of FR-259, fixes what a trace *is*:

- the body is **a deterministic re-score of the pinned bundle** (`backend/src/app/worker/trace_handlers.py:98`,
  `result = await score_one(compiled, ctx, trace=True)`);
- the re-score is **compared with the result actually served** (`traces.py:257`,
  `status = "complete" if reproduced_summary == row.served_summary else "mismatch"`), where the served
  side is `summarise_result(result)` (`traces.py:143-157`), a function **of a `ScoringResult`**
  (`outcome`, `decline_reasons`, `premium_ladder`, `outputs`);
- `RL-862` condition (b), which the clarification adopts: *"The persisted trace must be checked against
  the premium actually served … A trace that silently does not match the quote it purports to explain is
  worse than no trace"*.

An errored quote **has no served result**: the customer received a 422 problem document, not a
`ScoringResult`. So (i) there is nothing for `summarise_result` to summarise on the served side, and
`write_pending_trace` takes one as `served_summary`; (ii) the re-score `score_one(compiled, ctx,
trace=True)` is deterministic and fails the same way (the repo says so of the ladder refusal,
`_LADDER_REFUSAL_NOTE`, `score.py:113-115`: *"a retry fails the same way"*), so the trace job would
raise instead of returning a `Trace`; (iii) the `status` vocabulary is `complete` or `mismatch`, and
neither describes a trace of a refusal. **"A trace of an error" is therefore undefined by the spec as it
now stands, not merely unsampled by the code.** Making the code sample first would write a pending row
whose body cannot be produced under RL-862 (b) and whose status has no value.

The reading is a sentence of the maintainer's (by delegation) own, quoted above, and the auditor has
checked every step of it against the files cited. The auditor does not rule on which of (a), (b) or (c)'s
remedies is right; that is the decision-maker's (`CLAUDE.md` §0 and §12).

### 5. What is, and is not, reachable today

`git -C /home/puzhenhao1989/gi-pricing-plan grep -nE 'outcome == "error"|outcome="error"' origin/main -- backend/src`
prints **one line**, `backend/src/app/platform/traces.py:96` (`if outcome == "error":` in
`decide_sampling`): the predicate is the two literal forms over `backend/src`, so it finds the floor
itself and no producer, and the batch consumer above is spelt differently (a polars column filter), which
is why it is cited by file and line. The only test that names the `error` outcome with sampling is
`backend/tests/test_traces.py:45-46`, a call of the pure function
(`decide_sampling("error", rate, roll=roll)` returns `(True, "error")`); the predicate was
`git grep -nE '"error"' origin/main -- backend/tests packages/pricing-core/tests | grep -iE 'sampl|trace|decide'`,
one hit. That is the trap in this finding: a green unit test on the pure function sits beside a
requirement the live path does not meet. *(Read, not measured: the auditor ran no test, the charter
forbids a suite run here.)*

### 6. Why the date matters

The WF-701 deployment-steps demo's step C7 (memo section C7, limb 2) reads FR-259's 100 % floors back
from the persisted traces. The memo (`handover/memo-wf701-deploy-demo-2026-10-14.md`, "C7's 100 % floor
limbs are not walkable today") found this limb: *"On `POST /score`, a per-quote error is **raised** as a
422 before `_maybe_sample_trace` runs (`api/score.py:420-427`, then `:429`) … This is a **code-versus-spec
question against FR-259** … Per CLAUDE.md §0, it is **stopped and resolved**, not quietly fixed and not
skipped."* Its recommendation was to file an FD and walk the limb as `KNOWN GAP C7-errors: FD-<id>`
(`PL-1544` Acceptance 2). The maintainer's (by delegation) ruling adopts that for the demo's rehearsals
and adds the bound: *"C7 is inside row 2, so the exit demo cannot carry a KNOWN GAP on it."* The decision
and its implementation must therefore land before the 12 Nov exit demo.

## Disposition

**Fix before close with an owner: WK-1178**, resolved **before the 12 Nov exit demo**; the finding needs a
resolution before any P3 start (`CLAUDE.md` §14). The resolution is one of the two the ruling names: *"a
spec clarification or code"*. The options below are for the decision-maker, who records them as an `OQ-`
with a recommendation (`CLAUDE.md` §0, last row; the auditor does not pick):

| | Option | What it needs | What it costs, as read |
|---|---|---|---|
| **A** | **Clarify FR-259**: errors are not traced. Say "declines and errors" means declines, and that a refused quote (a 422 or the ladder 500) is recorded by the audit log, the `ladder_reconciliation_failed` counter and the problem document, not by a trace | a dated FR-259 clarification, with an `RL-`; C7's errors limb is dropped from WF-701's demo with the spec as the reason | narrows a 100 % safeguard the spec author wrote, so it is the maintainer's to accept; monitoring (`05`) loses a quote-level error stream it may have counted on, which should be checked in `05` before choosing |
| **B** | **Define the trace of an error and implement it**: sample the refusal at 100 % with a served side of `{outcome: "error", code}`; the off-path job re-scores, expects the same code, and stores the trace up to the failing step; add a third `status` (for example `error`) to `GET /api/v1/traces` | a FR-259 clarification defining the error trace and its status, an `RL-1434` successor or amendment, a `Trace` shape that can end in a refusal, a contract change through `model-schema`, then code with the red first | persists the quote context of every rejected request at 100 % for 13 months (NFR-459); `NFR-499` keeps quote inputs out of error text, and this stores them in a row, so the retention and access reading needs a ruling; a caller sending bad input becomes a write per request (not measured) |
| **C** | **Option B for the system faults only** (the 500 ladder refusal and `MODEL_CALL_FAILED`) and A for caller errors (`INPUT_CONTRACT_VIOLATION`, the misses) | both of the above, with the split drawn on `_PER_QUOTE_CODES` | a split rule the spec does not yet have, but it keeps the 100 % floor where an actuary needs a trace (a platform fault) and not where the cause is the caller's input |

The auditor's observation, not a verdict: A is the smaller change and B/C honour the sentence as written;
whichever is chosen, the drift between the pure function's tested floor and the live route's reach should
get its own assertion (a test that drives `/score` to a refusal and asserts what the chosen option says
is persisted, red first on `main`).

**Event that next confirms or discharges it:** the decision-maker's `RL-` choosing A, B or C, the
FR-259 clarification it names landed in `docs/specs/03-rating-engine.md`, and (for B or C) a red-first
test that drives a refusal through `POST /api/v1/score` and observes the persisted trace, green on the
merged tree; WF-701's C7 errors limb then walks without a `KNOWN GAP`. Dated before 12 Nov 2026.
