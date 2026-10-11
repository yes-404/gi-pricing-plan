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

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **Red first, on a real `score_one`.** The new file is
   `backend/tests/test_score_default_live.py`, a DB test with `score_one` **not** stubbed and a
   Deployment of a compiled Rating Version in the caller's Environment. Its default-live request
   carries no `rating_version_ref`. It runs once with no `options` at all, and once with `options`
   present but no ref. The `LG-` quotes it on the base answering 422 `INPUT_CONTRACT_VIOLATION`, one of the route's per-quote
   codes (`score.py` `responses=` comment), with *"rating_version_ref is required"* in its
   detail, then 200 after the fix.
   The command is `uv run pytest backend/tests/test_score_default_live.py -q`.
2. **The resolved version is recorded.** In that 200, the result's `rating_version_ref` equals
   the deployed version, and so does the sampled trace's when tracing is on (`:384`,
   `_maybe_sample_trace`). Each is asserted.
3. **An explicit ref is never overridden.** A test supplies an explicit `rating_version_ref` that
   differs from the live Deployment's. The result names the explicit one, and the request object
   the route received is unchanged. The test asserts both.
4. **The request is not mutated.** The fix builds the copy with `model_copy` (or a new
   `QuoteContextOptions`, `packages/model-schema/src/model_schema/scoring.py:82`) and never
   assigns to `ctx`. `QuoteContext` is frozen (`scoring.py:99`), so an assignment raises.
5. **No bundle or price change.** The diff touches no file under `packages/` or `examples/`, and
   no fixture: `git diff --stat origin/main...<branch>` lists only
   `backend/src/app/api/score.py`, the new test file, the `LG-` and the roadmap row. The existing
   money fixtures and pinned hashes pass unchanged:
   `uv run pytest backend/tests/test_score.py backend/tests/test_demo_rating_evidence.py -q`.
6. **Both gate halves pass on the merge tree** (`CLAUDE.md` §11). This is the full two-half gate,
   queued in the background on the lead's grant.

## Task (one, red first)

1. Write `test_score_default_live.py` (Acceptance 1–3) and run it on the base. It is red on 1–2
   and green on 3. Quote both in `LG 9909`.
2. In `score()`, after `:369`, build `scored_ctx` as `ctx` with its options carrying `ref`. Do
   this only when `ctx.options` is `None` or its ref is `None`; an explicit ref passes through
   as it is. Pass `scored_ctx` to `score_one` at `:375`. Keep `ctx` for everything else, and
   change no other call.
3. Run the file green, then Acceptance 5's two files, then the gate. Closing acts per
   `executor.md`: the `LG-` and the SL row go `closed` in the slice PR.

## Self-review

Every clause of the 11:25:16 item 3 maps to an acceptance item: immutable copy → 4; result and
trace record the resolved version → 2; explicit not overridden → 3; no bundle or price change →
5. NFR-499 is unaffected because this is the same `score_one` call with one more option field. No
decision point is open: the scope is ruled. Status goes `active` at the lead's GO (the PL row of
`document-ids.md` §1.6).
