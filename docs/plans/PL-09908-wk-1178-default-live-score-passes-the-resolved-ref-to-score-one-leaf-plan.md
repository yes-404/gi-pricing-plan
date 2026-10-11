---
id: PL-9908
family: plan
kind: leaf
title: WK-1178 — a default-live POST /score passes the resolved Rating Version to score_one: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-11
owner: planner
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1544, PL-1454, PL-1392, SL-9937]
---

# PL-9908 — WK-1178: default-live `/score` passes the resolved ref to `score_one`, leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development (recommended) or
> executing-plans. The executor also binds `test-driven-development`, `python-test`,
> `fastapi-service`, `dev-commands` (the two-half gate) and `git-hygiene`. It is spawned from
> `.claude/roles/executor.md` and reads [`README.md`](README.md)'s five unchecked conventions.

Filed under working id 9908, for slice `SL 9937` (its `draft` row under `### WK-1178` in
[`../roadmap.md`](../roadmap.md)) and ledger `LG 9909` (the executor's). The lead reserved all
three (from-lead "2026-10-11 11:26:33 BST — Lead: default-live fix IS on the G2 path …", "IDS
RESERVED"). Written 2026-10-11 by the planner (planner-wk690). Read at `origin/main` `d699a561`.
**Form:** this is a one-page leaf plan on the lead's and the maintainer's ruling ("Plan as a 1-page
leaf delta under WK-1178"). WK-1178 has no single Work plan, and its fix slices each carry their
own leaf plan (`PL-1602`, `SL-1603`).

## Goal

A default-live `POST /api/v1/score` (no `rating_version_ref`) scores against the caller's
Environment's live Deployment and answers 200, instead of 422 `INPUT_CONTRACT_VIOLATION`. The
resolved version is recorded, an explicit ref is untouched, and no price moves.

## Authority and the defect

- **Scope, ruled:** to-lead "2026-10-11 11:25:16 BST — DEFAULT-LIVE /score: CONFIRMED by reading
  (no wait for a run); FD + fix slice NOW; SL-1526's demo script checked before its window", item
  3, verbatim: *"in score(), pass score_one a ctx whose options carry the resolved ref (an
  immutable copy, e.g. ctx.model_copy with the options updated; never mutate the request). Check
  that the returned result and trace record the RESOLVED version, and that an explicit
  rating_version_ref is never overridden. NFR-499 unaffected. No bundle or price changes (ruling
  X: the money fixtures and pinned hash unchanged)."* Item 1 makes this slice's red-first test the
  confirmation of the defect.
- **The defect**, read at `d699a561`. `score()` (`backend/src/app/api/score.py:351`) resolves
  the live ref at `:369` (`ref, deployment_id = await _serving_ref(database, caller, ctx)`;
  `_serving_ref` is `:169-206`). It then calls `score_one(compiled, ctx, trace=trace)` at `:375`
  with `ctx` **unchanged**. `score_one` refuses a missing ref at
  `packages/pricing-core/src/pricing_core/rating/score.py:945-952`
  (`INPUT_CONTRACT_VIOLATION`, *"ctx.options.rating_version_ref is required"*). Every
  default-live `/score` that reaches `score_one` is therefore refused. The default-live tests
  (`backend/tests/test_score.py`, from `:1325`, "WK-674 Slice 2, Task 6") stub `score_one`
  (`:1374`), which is why none of them saw it. `_serving_ref` has no other caller
  (`git grep -n '_serving_ref\|_required_ref(' -- backend/src`), so batch and compare are not
  affected.
- **G2 link:** `PL-1544:377`, exit demo (b) step S1: *"`POST /score` with its key and no ref |
  200; bundle hash = C6's"*. That is default-live, so this slice is on the G2 path (from-lead
  11:26:33). **Relation to SL-1455:** `PL-1544:129` quotes PL 9728 DP-6 (b), *"the remedy slice
  measures and fixes the default-live /score arm"*. That is `PL-1454` Acceptance 2's measurement.
  This slice is separate and lands first (the 11:25:16 item 3). SL-1455's untimed default-live
  probe stays an independent second check (item 1).

## Acceptance Standard

The maintainer's GO, verbatim: to-lead "2026-10-11 11:29:37 BST — DISPATCH GO: SL 9937 (default-live
/score fix, PL 9908, LG 9909), effective when PL 9908 is pushed with the acceptance below; the
trace limb IN scope", item 2: *"PL 9908 acceptance must carry, each red on base (shown in the slot,
src-only revert, Redis/DB up)"*. **(a)–(e) are each shown red on the base in the gate slot** by a
src-only revert of `backend/src/app/api/score.py`, with Redis and the DB up, then green at the head.
The `LG-` quotes each command, its rc and its red line. The tests are additions to
`backend/tests/test_score.py`, as authored at `origin/sl-9937-default-live-score` `0b46672a` and
`7ec284f9`; no existing test is edited. `uv run pytest backend/tests/test_score.py -q` runs them.

- **(a)** A default-live request, with the **real** `score_one` (not stubbed) and a Deployment
  in the caller's Environment, answers **200**, and the result's `rating_version_ref` is the
  deployed version. On the base it is 422 `INPUT_CONTRACT_VIOLATION` (*"rating_version_ref is
  required"*, `packages/pricing-core/src/pricing_core/rating/score.py:945-952`).
- **(b)** The no-options variant. For a request with no `options` at all, the created options
  carry the **same defaults as absent options** (`trace` off, and every other field at its
  `QuoteContextOptions` default, `packages/model-schema/src/model_schema/scoring.py:82`), plus
  the resolved ref. The test asserts this field by field.
- **(c)** A default-live **sampled** trace job runs to `SUCCEEDED`. The trace worker re-scores
  the stored `pending_quote_context` (`backend/src/app/worker/trace_handlers.py:79`
  `QuoteContext.model_validate(row.pending_quote_context)`, then `:98` `score_one(compiled, ctx,
  trace=True)`). On the base the stored context has no ref, so the job is refused with
  `INPUT_CONTRACT_VIOLATION`. The fix passes the resolved-ref copy to `_maybe_sample_trace` as
  well, so the stored context carries the resolved ref (the GO's item 1: "the trace limb IN
  scope").
- **(d)** An explicit `rating_version_ref` that differs from the live Deployment's **wins**: the
  result names the explicit one.
- **(e)** A unit test of the helper (`_with_resolved_ref(ctx, ref)` as authored). It shows that
  an explicit ref is returned untouched, that the options are created when absent, and that the
  input object is never mutated (`QuoteContext` is frozen, `scoring.py:99`).

Also, each a line in the `LG-` (the GO's item 2, "quoted with file:line in the LG"):

1. **One caller.** `_serving_ref` has one caller, `score()` (`backend/src/app/api/score.py:369`
   at `d699a561`; predicate `git grep -n '_serving_ref\|_required_ref(' -- backend/src`).
   **Compare and batch build explicit refs, so they have no gap.** `/score/compare` builds
   `QuoteContextOptions(trace=True, rating_version_ref=ref)` (`score.py:443-445` at
   `d699a561`). The batch worker stamps "the **resolved** ref into each frame it builds"
   (`backend/src/app/worker/scoring_handlers.py:33`).
2. **No bundle or money change.** The money fixtures and the pinned bundle hash are unchanged.
   `git diff --stat origin/main...<branch>` lists only `backend/src/app/api/score.py`,
   `backend/tests/test_score.py`, the `LG-` and the roadmap row. Nothing under `packages/`,
   `examples/` or a fixture appears, and `backend/tests/test_demo_rating_evidence.py` passes
   unchanged.
3. **NFR-499 is unaffected.** The trace store already holds the full quote input, which is
   access-controlled (FR-259), so adding the ref changes nothing there (the GO's item 1).
4. **The gate.** The full two-half gate (`CLAUDE.md` §11) runs **after SL-1529** in the G2 order
   (the GO's item 3; from-lead 11:26:33). The 13 audit-on-tree tests clear at the minted-head CI.
5. **The finding.** The FD (the auditor proposes the severity; HIGH is expected) names **both
   instances**, `score()` → `score_one` and the sampled-trace re-score, and is discharged by
   SL 9937 (the GO's item 4). It rides the next docs batch. It is not this slice's write.

## Tasks

One task, red first. The executor has authored it at `0b46672a` and `7ec284f9`.

1. Add the (a)–(e) tests to `backend/tests/test_score.py`.
2. In `score()`, after `_serving_ref` (`:369`), build the resolved-ref copy with
   `_with_resolved_ref(ctx, ref)` (an immutable `model_copy`; options created if absent; an
   explicit ref is returned untouched). Pass the copy to `score_one` and to
   `_maybe_sample_trace`. The request object is never mutated.
3. In the gate slot: run the src-only revert of `score.py` to show (a)–(e) red, restore it,
   run them green, then run the full two-half gate. Write the `LG 9909` lines 1–5. Closing acts
   per `executor.md`: the `LG-` and the SL row go `closed` in the slice PR.

## Decision points

None. The scope is ruled (to-lead 11:25:16 item 3), and nothing in it is left open.

## Self-review

Every clause of the 11:25:16 item 3 and the 11:29:37 GO maps to an acceptance item. The immutable
copy is (e). The result and the trace record the resolved version: (a) and (c). An explicit ref is
not overridden: (d). No bundle or price change: line 2. NFR-499: line 3. The one-caller and
compare/batch claims: line 1. The gate order: line 4. The FD: line 5. No decision point is open,
because the scope is ruled. Status goes `active` at the GO's effect, when this plan is pushed
with this acceptance (the PL row of `document-ids.md` §1.6).

*(Revised 2026-10-11 before its first merge, on the lead's relay of the 11:29:37 GO. The first
draft named a new test file, `test_score_default_live.py`, and said "`test_score.py`
unchanged". The tests were authored in `test_score.py`, as additions only, and the trace
limb was added to scope.)*
