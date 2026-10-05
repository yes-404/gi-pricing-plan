---
id: PL-1426
family: plan
kind: leaf
title: WK-1178 emergency — FD-1425, guard (c) at the entry, a quote input never overrides a produced value (FR-213): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: planner
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1374, RL-1263, SL-1391]
---

# PL-1426 — WK-1178 emergency: guard (c), a quote input never overrides a produced value, leaf plan

This is the leaf plan PL-1426. Its slice is SL-1427, an `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md) with status `draft`. The lead reserved both ids. The
finding is FD-1425. Everything below was measured at `origin/main`
`4d3be1414ad4dacdaa0c14ef49fb21853adbaed6` on 2026-10-05, unless a line says otherwise.

**Narrowed 2026-10-05, after 17:32:18 BST, pre-mint, on the maintainer's (by delegation)
17:27:55 and 17:30:02 BST entries (quoted under "Authority").** As first filed, this plan
carried the root in `score_one`'s path as well. The cause trace placed that root in `to_wire`'s
sink fan-in, and the 17:27:55 ruling sends it to PL-1426's sibling, PL 9567, as (R-b). This
plan is now **guard (c) alone**, with T2 applied in the same commit (17:30:02 item 2). If
auditor-fanin finds a wrong price with no caller key, (R-b) becomes a **second** emergency
slice after this one; it does not join this plan (the lead's relay of the maintainer's
correction to the 17:27:55 ruling).

**No decision point is open.** The maintainer (by delegation) has already made every decision
this plan carries, in the three entries quoted under "Authority". The plan adds none.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax
> for tracking. Also bound: `python-test` (the `req` markers, the negative tests),
> `python-package` (pricing-core's boundaries) and `dev-commands` (the gate's traps). The
> executor is a sonnet; one gate; the maintainer's (by delegation) ACK.

## Goal

A caller can no longer set a price by sending an input named like a value the algorithm
produces, on any path that scores a quote.

**Architecture:** One guard, at the entry. `score_one` and `_score_context_sync` build the
engine context as `{effective_date, purpose, **ctx.inputs}` (`score.py:910-912`, `:1066-1068`),
which relays every raw key to the engine. A new pre-check refuses an undeclared input key that
names any produced value, with `INPUT_CONTRACT_VIOLATION`; the declared inputs are subtracted
first. With the entry closed, no stale copy of a produced value can come from a caller, so the
caller exploit is closed on all four paths. The mechanism the copy rode, `to_wire`'s sink
fan-in, is (R-b) in PL 9567.

**Tech Stack:** Python 3.12, pricing-core, the ZEN binding, pytest; the backend's FastAPI test
client for the four path tests. No new dependency.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3 (FR-213, FR-255)
and §5.2 (`score_one`). The finding is FD-1425 (#1183). The ruling is quoted under "Authority".

## Acceptance Standard

Run each item from the worktree root after `uv sync --all-packages` (`dev-commands`). A
full-suite run takes the one gate slot.

1. `uv run pytest packages/pricing-core/tests/test_rating_shadowed_inputs.py -q` passes. The
   ledger records each red of Task 1 failing at the slice's base commit, for the cause Task 1
   Step 4 names.
2. **(3f)**: `test_the_3f_case_is_refused` raises `INPUT_CONTRACT_VIOLATION` naming
   `'instalment_loading_minor'`. At the base commit it quotes payable 777.
3. **Every produced name**: `test_an_undeclared_key_naming_a_produced_value_is_refused` is
   parametrised over every produced name of the score fixture, and each case is refused by name.
   The ledger carries auditor-premise's per-name table beside the run. That table shows
   `instalment_loading_minor` as the only name shadowed at the base commit, and (3f) is its red.
4. **Unchanged**: `test_the_ordered_no_key_quote_is_unchanged` gives payable 5250 with
   `min_premium_minor` 5000 and no extra key, and `test_the_bundle_hash_is_unchanged` pins the
   fixture's hash recorded at the base commit.
5. **Still allowed**: `test_a_declared_input_re_produced_in_place_is_not_a_shadow` passes.
6. **One red per path**, each failing at the base commit and passing at the head:
   - `/score`: `backend/tests/test_score.py::test_a_quote_input_naming_a_produced_value_is_refused_on_score`
   - `/score/compare`: `backend/tests/test_score_compare.py::test_a_context_input_naming_a_produced_value_is_a_422_on_compare`
   - trace reproduction: `backend/tests/test_score.py::test_a_pending_trace_whose_context_names_a_produced_value_is_not_reproduced_as_a_price`
   - batch: `backend/tests/test_scoring_handlers.py::test_a_dataset_column_named_like_a_produced_value_is_refused_per_row`

   Run each one alone: `OMP_NUM_THREADS=1 nice uv run pytest <file>::<test> -q`.
7. **T2**: the FR-213 row (`03` `:82`) carries RL-1423's T2 text byte-for-byte, in the same
   commit as guard (c).
8. `uv run pytest packages/pricing-core/tests/test_rating_score.py
   packages/pricing-core/tests/test_quote_input_raise_sites.py -q` passes, and no assert is
   edited.
9. The full gate (`CLAUDE.md` §11, both halves) passes on the slice head. The gate-runner runs
   it in the one gate slot, and the ledger names the tree.
10. `python3 scripts/audit-docs.py` fails only on check 31 until the mint, and is clean after it.

## Global Constraints

- Money is integer minor units, or `Decimal` in the rating path, never float (`CLAUDE.md` §7).
- `pricing-core` takes no FastAPI/SQLAlchemy/Redis dependency (`CLAUDE.md` §2;
  `.importlinter`'s `core-has-no-infrastructure`).
- A coded error names the field and the constraint, never the value (NFR-499, RL-917).
- `mypy --strict` and `ruff` cover `packages/`.
- One full gate at a time on this VM. A measurement runs as `OMP_NUM_THREADS=1 nice`, and never
  beside a held gate slot.

---

## Authority

The maintainer's (by delegation) entries in `channel/to-lead.md` (a local channel file, cited by
its header), quoted verbatim.

**"2026-10-05 17:25:07 BST — URGENT RULING: FD 9572's premise FALSE; OPTION (iii): a HOLD now,
and an EMERGENCY (c)-only slice FIRST in lane B (WK-1178); the wiring fix after"**:

> FACT (auditor-premise at 4d3be141, script sha256 b3448450a1fe4c5b9622ec15555fda8a5d983c0b82e1ca9bbb7b624df2fb501c, through score_one): a CORRECTLY ORDERED algorithm with min_premium=5000 and an extra input instalment_loading_minor=777 quotes payable=777 (ladder: risk 1305, office 1436, constraints 5000, instalment_loading 777, payable 777), against 5250 without the key. A caller key naming a produced name OVERRIDES that step's output in correct order: the shadow is in the engine's context merge. My 17:22:47 premise ("the correct order still gives 350") is FALSE for this shape, and the STOP did its job.
> EXPOSURE, my read at 17:24: gipricing `select count(*) from deployments` = 0; rating_versions = fremtpl2-demo@1, approved. So NO deployed version is serving, and no real quote is affected, but one approved version is one step from deployable, and the code path is open to any caller with score:execute (/score, /score/compare, trace reproduction, batch).
> RULING (the maintainer, by delegation): OPTION (iii).
>  1. HOLD, NOW, replacing the 17:10:08 interim hold (which did not cover this): NO Rating Version is DEPLOYED to any Environment, and no new Rating Version is approved, while /score (and compare, trace reproduce, batch) accepts an undeclared input key. This includes fremtpl2-demo@1. Record it in eta.md Holds and holds-2026-10-01.md, quoting this header; check it at every approval and deploy dispatch. It lifts at the emergency slice's merge.
>  2. EMERGENCY SLICE, its own tiny slice under WK-1178 (the standing maintenance Work, so it may run beside S7 (WK-673) under RL-1263's different-Works rule NOW, without waiting for RL 9620), FIRST in LANE B (free now; the FD 9707 fix waits behind it):
>    - scope = fix (c) ONLY: in the shared merge (score.py ~:911 score_one and ~:1067 _score_context_sync), refuse an UNDECLARED input key that names ANY produced value of the algorithm, with INPUT_CONTRACT_VIOLATION (per-quote 422, my 17:22:47 DP-1), declared inputs subtracted (DP-2: the in-place clamp of a declared input stays legal);
>    - red first: the auditor's (3f) case gives 777 today and must be refused; plus a case per path (/score, /score/compare, trace reproduce, batch with a dataset column so named); the ordered no-extra-key case unchanged (5250); the bundle hash unchanged;
>    - the minimal plan: a planner writes it NOW (a leaf plan plus its SL row, my rulings quoted as its authority; no new DPs: every decision is already made), minted at once, ahead of everything in the mint queue except the in-flight batch-1 merge; a sonnet executor; one gate; my ACK.
>  3. The WIRING fix (PL 9567, list order) follows as planned, after the emergency slice, rebased on it; its (c) part is then already delivered, so PL 9567 drops (c) by a dated delta and keeps (a)/(b).
>  4. FD 9572's essay gains this measured fact (an ordered algorithm is also exposed; the cause in the context merge) as a dated pre-mint amendment; the severity stays HIGH. The auditor finishes the cause trace (why base/premium are overridden by their producers in the [in,A,B,out] shape but instalment_loading is not: step kind or position), reported with the emergency slice's plan.

**"2026-10-05 17:25:23 BST — ADDENDUM to my 17:25:07 urgent ruling: the emergency slice fixes
the ROOT in score_one AND adds guard (c)"**:

> The final measurement (r1.py 8dea0ff6…, r2.py b3448450…) shows the ZEN wiring of an ORDERED graph is correct (350 for every extra key), and the wrong price arises in score_one's path (the context merge, or how the output/ladder READ produced values): instalment_loading_minor=777 → payable 777 vs 5250; the clamp's own name is not shadowed. So the emergency slice's scope is BOTH: (1) the ROOT, once the auditor's per-name table and cause line(s) land, e.g. if the output or ladder reads a produced value from the merged context instead of the producing step's result, it reads the step's result; and (2) guard (c), refusing an undeclared key naming a produced value with INPUT_CONTRACT_VIOLATION, kept as defence in depth. The red tests include the per-name table's shadowed cases. My 17:25:07 HOLD, lane B placement, WK-1178 and the "no new DPs" plan stand. If the root fix proves to need a design choice, it comes to me, and (c) alone ships first.

**"2026-10-05 17:22:47 BST — PL 9567 (the FD 9572 fix, #1193 @f4e4380b) DP-1..4 RULED;
CORRECTION of my error code; the unmeasured premise kept as a STOP"**. This plan takes the
code and the refusal rule from it, quoted:

> DP-1: (a) INPUT_CONTRACT_VIOLATION, and a CORRECTION of my 17:06:26 / 17:10:08 "VALIDATION_FAILED". Verified: backend/src/app/api/score.py `_PER_QUOTE_CODES` (:97) does not hold VALIDATION_FAILED, and :332 sends any other code to the caller as a 500. A refused key must be a per-quote 422-class error, as the _check_billing_surface precedent does.
> DP-2: (a) REFUSE, by name, never drop silently: a context key that names a PRODUCED value is refused, with the DECLARED inputs subtracted first. A clamp that re-produces a declared input in place is legitimate, so a declared input is never refused for sharing a name with its in-place clamp. A red test for that exception.
> DP-3: NOT decided here, per my order; the options stay recorded. (c) is exactly "an undeclared key naming a produced value"; FR-246's declared-inputs rule (FD-1374 / PL 9776) stays its own.
> DP-4: an RL adopts T1 (FR-212: "list order carries no meaning") and T2 (FR-213) BEFORE activation, as an added activation need. Reserve the id; a DM files it, quoting my 17:06:26 and 17:10:08 entries and this one.

**"2026-10-05 17:27:55 BST — FD 9572 CAUSE: the sink fan-in plus whole-context passThrough;
RULING: (c) ALONE is the emergency slice; (R-b) is the root, in PL 9567; one more case to
measure; A-2 readings"**, the cause and the ruling (its A-2 lines are omitted, being another
plan's):

> CAUSE (auditor-premise, read-only at 4d3be141; r3/r4/r5 sha256 0ee537bf…/ae53159a…/98aea5df…): runtime.py:495-499 (to_wire's sink rule wires every interior step whose produced names no other step consumes, INCLUDING produce-nothing steps such as the decline constraints, straight to the sink, so the sink has a fan-in) plus whole-context passThrough on every expressionNode (:174, :268, :353, :389; the docstring :428-432); at the fan-in the LAST-LISTED branch wins (inferred from 3 runs; zen's merge code not read); score.py:911/:1067 relay raw keys as the ENTRY point. The per-name table: only instalment_loading_minor (the last terminal producer) is shadowable in that fixture. Exposure: fremtpl2-demo@1 (never deployed) is a single path with no fan-in, so it is not exposed by this mechanism (inferred from topology). The HOLD stands regardless.
> RULING:
>  1. The EMERGENCY slice (SL 9561 / PL 9560) = guard (c) ALONE at the entry (score.py:911 and :1067): refuse an undeclared key naming any produced value, INPUT_CONTRACT_VIOLATION, declared inputs subtracted. It closes the CALLER exploit fully, and the hold lifts at its merge.
>  2. (R-b) is the ROOT and goes into PL 9567 (the wiring slice), red first with the fan-in case: no side branch may carry a stale copy of a produced name into the sink (one ordered merge at the sink, or produced names stripped from the relayed context; the planner proposes, and if it changes every bundle's hash that is stated and approved by me).
>  3. ONE MORE CASE TO MEASURE NOW (the same auditor, read-only, ≤20 min), because the same mechanism may misprice with NO caller key at all: an ORDERED algorithm in which a produce-nothing or terminal side branch forks BEFORE a step that RE-PRODUCES a name in place (a clamp), so the side branch carries the PRE-clamp value to the sink. If it is listed last, does the sink take the stale value? Run it through score_one with no extra key. If YES, that is an internal mispricing with no caller needed, (c) does NOT close it, and (R-b) moves INTO the emergency slice: report to me at once with the price. If NO (the clamp-in-place keeps every branch downstream, as in the fixture), (c) alone stands.
>  4. FD 9572's essay gains the cause lines and the per-name table as a dated pre-mint amendment.

**"2026-10-05 17:30:02 BST — Rulings: T2 routing (RL 9562 mints ahead of PL 9560); …"**,
items 1 and 2:

> 1. ROUTED 17:31: noted. A YES from auditor-fanin comes to me at once; PL 9560 does not mint until auditor-fanin has reported.
> 2. #1195 RL 9562, T2: your RECOMMENDATION is adopted. RL 9562 owns T1 and T2's text and mints right after batch 1, AHEAD of PL 9560. PL 9560 applies T2 (FR-213 :82) in the same commit as guard (c), citing RL 9562, with no paraphrase. T1 stays with PL 9567 / SL 9568. DP-3 stays OPEN in RL 9562 and is named as open. The mint ACK for #1195 follows my checklist at its mint head (it is not given by this line).

**"2026-10-05 17:34:25 BST — FD 9572 fan-in measurement accepted: (c) ALONE stands; A-2
create_sub_graph_version IN"**, items 1 and 2, verbatim (added after 17:37:04 BST):

> 1. auditor-fanin (fanin.py dc4958c0…, fanin2.py 758a08c7…, at 4d3be141): no wrong price. A decline side branch forked BEFORE the clamp makes the engine REFUSE with LADDER_RECONCILIATION_FAILED; every other order gives 5250, or 1507 with min_premium=0. ACCEPTED. PL 9560 = guard (c) + T2 and mints after RL 9562. The stated LIMITS (one fixture, decline branches only, no case without ladder reconciliation) go VERBATIM into FD 9572's mint text and into PL 9567's (R-b) red set as the cases it must cover: a produce-nothing side branch, and an algorithm with no ladder reconciliation. So (R-b) closes what this measurement could not reach, and the HOLD on deploy/approve stands until (c) merges (it is not lifted by this measurement).
> 2. #1196: "root in score_one" withdrawn in place, T2 added. Yes. #1193 (R-b) red-first plus the mechanism DP: noted; I rule it when it arrives with its hash impact. #1195's pre-mint T2 edit (dm-9562b): my mint ACK reads that head.

**auditor-fanin's result**, from the trace file `handover/trace-fd9572-premise-fanin-2026-10-05.md`
(a local handover file; fanin.py sha256 `dc4958c0…`, fanin2.py `758a08c7…`, at `4d3be141`),
verbatim:

> **NO wrong price.** Decline side branches forked BEFORE the clamp → `LADDER_RECONCILIATION_FAILED` (R3: clamp value 1435.5 is not its bound 5000; R4: the replay rounds to 8814 …), and no price is returned. Every other order → 5250. With min_premium=0, all orders → 1507. Because wiring is positional, a branch forked before the clamp is necessarily listed before s_instalment, so it cannot be the last edge into the sink. With the payable output reading X directly, compile refuses with LADDER_CLAMP_UNPLACEABLE.
> **Limits:** one fixture; decline-constraint side branches only; a case with no ladder reconciliation was not tested. So (c) ALONE stands (item 3's NO branch). (R-b)'s red in PL 9567 must still cover the fan-in case.

So 17:27:55 item 3 answered NO and (c) alone stands. The limits named there are covered in
PL 9567's (R-b) reds, per 17:34:25 item 1.

**DP-3 is open**, and named as open: FR-246's general declared-inputs rule (FD-1374, PL 9776)
stays its own, in RL-1423 and PL 9567 (17:22:47 DP-3; 17:30:02 item 2). Guard (c) is exactly
"an undeclared key naming a produced value", and no more.

**The FR-213 text (T2), as first filed and now superseded by 17:30:02 item 2.** DP-4 ruled that a ruling adopts T2 before PL 9567 activates (RL-1423,
working id). Guard (c) now ships here, so T2 belongs with this slice. This plan applies T2 in
Task 3 Step 5 only if the dispatch record names RL-1423 as merged; otherwise T2 lands with
PL 9567. The lead decides which at dispatch. That is a dispatch-order question, not a new
decision point on the fix.

## Decision points

None open. Every decision this plan carries is the maintainer's (by delegation), quoted under
"Authority": the code (17:22:47 DP-1 (a)), refuse by name with the declared inputs subtracted
(DP-2 (a)), the scope, lane and Work (17:25:07 item 2), guard (c) alone (17:27:55 item 1), and
T2 in the same commit (17:30:02 item 2).
DP-3 (FR-246's general rule) stays open in RL-1423 and PL 9567, not here. (R-b) is PL 9567's
(17:27:55 item 2); a second emergency slice, if auditor-fanin answers YES, is the maintainer's
to order.

## Verified facts (at `4d3be141`)

- **Two context builders, one shape each:**
  `{"effective_date": ..., "purpose": ctx.purpose, **ctx.inputs}` in `score_one` (`score.py:876`;
  the merge at `:910-912`) and in `_score_context_sync` (`:1045`; the merge at `:1066-1068`).
  `score_batch` and `rating/testing.py`'s `evaluate_golden_quotes` reach the engine through
  `_score_context_sync`. No other `decision.evaluate` or `decision.async_evaluate` call exists
  under `packages/*/src` or `backend/src`
  (`grep -rn 'decision.evaluate\|decision.async_evaluate' packages/*/src backend/src`).
- **The four paths** come from the 17:15:09 entry (auditor-towire, at `137bc817`):
  - `/score` (`api/score.py:350-375`);
  - `/score/compare` (`:447`);
  - trace reproduction (`worker/trace_handlers.py:98`, `score_one(compiled, ctx, trace=True)`
    on `row.pending_quote_context`);
  - batch (`scoring_handlers` → `_score_context_sync`; every dataset column but the four
    reserved ones becomes `ctx.inputs`).

  Dislocation is safe: it selects declared inputs only (RL-1394).
- **`_validate_inputs`** (`score.py:333`) tolerates extra keys. The precedent for refusing a key
  by name is `_check_billing_surface` (`score.py:425-433`):
  `_raise_named("INPUT_CONTRACT_VIOLATION", ...)`, called in both paths right after
  `_check_purpose_mount`.
- **The raise-site census** in `packages/pricing-core/tests/test_quote_input_raise_sites.py`
  (`_INPUT_FREE`, `:62-79`) fails when a `_raise_named` site is added without an entry.
- **The score fixture** is `test_rating_score.py`'s `_algorithm_payload` (`:46`). Its declared
  inputs are `driver_age`, `channel`, `min_premium_minor`, `sanity_cap_minor` and
  `sanity_floor_minor`. Its produced names are `expense_factor` (`s_expense`),
  `risk_premium_minor` (`s_risk`), `office_premium_minor` (`s_office`, re-produced by
  `s_clamp`) and `instalment_loading_minor` (`s_instalment`). The two decline constraints
  produce nothing.
- **The backend fixture algorithm** is `_minimal_algorithm`
  (`backend/tests/test_rating_version_compile.py:50`). Its one declared input is `premium_in`,
  and `s_expr` produces `payable`.
- **The bundle hash does not read the context:**
  `compile_bundle` sets `content_hash=bundle_hash(graph, pins)` (`compile.py:641`).

## Write set, and its contention

| Path | This slice | Beside S7 (SL-1391, PL-1419, lane A) | FD 9707 fix (PL 9688) | Wiring fix (PL 9567) | Class |
|---|---|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/score.py` | added: `_check_no_shadowed_produced_names`; edited: `score_one` and `_score_context_sync` (one call each) | not in its write set | `score_one`, `_score_context_sync` | `score_one`, `_score_context_sync` | **name-disjoint from S7.** PL 9688 and PL 9567 follow this slice and rebase onto it |
| `packages/pricing-core/tests/test_rating_shadowed_inputs.py` | added | — | — | — | none |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | `_INPUT_FREE`: one entry added | — | one entry | one entry (dropped with (c), see its delta) | registry (append) |
| `backend/tests/test_score.py`, `test_score_compare.py`, `test_scoring_handlers.py` | appended: the four path reds | — | adds its own `test_score_as_at.py` | the same four reds (dropped with (c)) | append-only |
| `docs/specs/03-rating-engine.md` | T2 on the FR-213 row (`:82`), RL-1423's text | the FR-231 row, §4.2, §5.1, §5.2 | the FR-221 row | T1 on the FR-212 row | distinct rows |
| `docs/roadmap.md`, `docs/INDEX.md`, the ledger | the SL-1427 row; regenerated; added | — | — | — | registry / generated |

RL-1263's different-Works rule covers S7 (WK-673) and this slice (WK-1178) running together.
Neither consumes the other's output.

---

## Activation needs

- RL-1423 minted (it owns T2's text and mints right after batch 1, ahead of this plan;
  17:30:02 item 2).
- auditor-fanin has reported. This plan does not mint until then (17:30:02 item 1; 17:28:27).
- FD-1425 and this plan minted, at once.
- The plan made `active` by a dated line.
- The maintainer's (by delegation) GO, then the activation PR, then the executor (17:26:16).

## Tasks

### Task 1: The reds

**Files:**
- Create: `packages/pricing-core/tests/test_rating_shadowed_inputs.py`
- Modify (append only): `backend/tests/test_score.py`, `backend/tests/test_score_compare.py`,
  `backend/tests/test_scoring_handlers.py`

**Interfaces:**
- Consumes: `compile_bundle` (`pricing_core.rating.compile`); `load_bundle`
  (`pricing_core.rating.runtime`); `score_one`, `score_batch` (`pricing_core.rating.score`);
  `_FakeResolver`, `_version`, `_ctx`, `_algorithm_payload` (`test_rating_score`).
- Produces: the test names the Acceptance Standard cites.

- [ ] **Step 1: The pricing-core module.** Mirror `test_rating_score.py`'s imports and markers
  (async tests with no explicit asyncio marker, `@pytest.mark.req(...)`). Import its fixtures;
  do not copy them.

```python
"""FD-1425 (the emergency slice): a quote input never overrides a produced value (FR-213).

(3f) and the per-name cases are auditor-premise's measurements at 4d3be141."""

from __future__ import annotations

from typing import Any

import polars as pl
import pytest
from test_rating_score import _FakeResolver, _ctx, _version

from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch, score_one

_BASE_INPUTS: dict[str, Any] = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 5000,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}
#: Every name a non-`input` step of the score fixture produces (`_algorithm_payload`).
_PRODUCED = ["expense_factor", "risk_premium_minor", "office_premium_minor",
             "instalment_loading_minor"]


async def _compiled() -> CompiledBundle:
    return load_bundle(await compile_bundle(_version(), _FakeResolver()))


@pytest.mark.req("FR-213")
async def test_the_ordered_no_key_quote_is_unchanged() -> None:
    result = await score_one(await _compiled(), _ctx(inputs=dict(_BASE_INPUTS)))
    assert result.outputs["payable_premium_minor"] == 5250


@pytest.mark.req("FR-213")
async def test_the_3f_case_is_refused() -> None:
    """auditor-premise (3f): payable 777 against 5250, on the CORRECTLY ordered fixture."""
    ctx = _ctx(inputs={**_BASE_INPUTS, "instalment_loading_minor": 777})
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION.*'instalment_loading_minor'"):
        await score_one(await _compiled(), ctx)


@pytest.mark.req("FR-213")
@pytest.mark.parametrize("name", _PRODUCED)
async def test_an_undeclared_key_naming_a_produced_value_is_refused(name: str) -> None:
    ctx = _ctx(inputs={**_BASE_INPUTS, name: 777})
    with pytest.raises(ValueError, match=f"INPUT_CONTRACT_VIOLATION.*'{name}'"):
        await score_one(await _compiled(), ctx)


@pytest.mark.req("FR-213")
@pytest.mark.parametrize("name", _PRODUCED)
async def test_an_undeclared_key_naming_a_produced_value_is_refused_in_a_batch(
    name: str,
) -> None:
    """The same refusal on `_score_context_sync`. The row's shape is
    `test_quote_input_raise_sites.py`'s `_row` (`:221-228`)."""
    options = _ctx(inputs=dict(_BASE_INPUTS)).options
    assert options is not None and options.rating_version_ref is not None
    row = {"quote_id": "Q1", "purpose": "new_business", "effective_date": "2026-09-01",
           "rating_version_ref": str(options.rating_version_ref), **_BASE_INPUTS, name: 777}
    out = score_batch(await _compiled(), pl.DataFrame([row]).lazy()).collect().to_dicts()[0]
    assert out["outcome"] == "error"
    assert out["error_code"] == "INPUT_CONTRACT_VIOLATION", out
    assert f"'{name}'" in out["error_message"]


#: Recorded at the slice's base commit in Task 1 Step 4, before any code change.
_SCORE_FIXTURE_HASH = "<the 64-hex value Task 1 Step 4 prints>"


@pytest.mark.req("FR-213")
async def test_the_bundle_hash_is_unchanged() -> None:
    bundle = await compile_bundle(_version(), _FakeResolver())
    assert bundle.content_hash == _SCORE_FIXTURE_HASH
```

  The ladder and output reads (`result.outputs[...]`) are FD-1425's script 2 reads, which ran
  at `137bc817`. If the shipped `ScoringResult` has moved, mirror the shipped form.

- [ ] **Step 2: Put auditor-premise's per-name table in the ledger** (r3/r4/r5, sha256
  `0ee537bf…`, `ae53159a…`, `98aea5df…`, read-only at `4d3be141`; the 17:27:55 entry). It shows
  `instalment_loading_minor` alone as shadowed in this fixture. `test_the_3f_case_is_refused`
  is that name's red. Every other produced name is refused too, by the parametrised test,
  because guard (c) refuses a name whether or not it shadows today.

- [ ] **Step 3: The four path reds**, appended to the modules that hold each path's fixtures.
  No existing test is edited. Check every fixture and helper name against the shipped module
  before relying on the sample (`docs/plans/README.md` convention 1). In `test_score.py` these
  are `compiled_version`, `scoring_headers`, `_quote`, `SCORED_REF`, `SCORE_URL`, `_rows_for`,
  `_trace_produce_jobs`, `_set_trace_sample_rate` and `execute_job`. In `test_score_compare.py`
  they are `two_versions`, `reader_headers`, `_body` and `COMPARE_URL`. In
  `test_scoring_handlers.py` they are `_compiled_version`, `_scoring_frame`,
  `_dataset_version`, `_parameters`, `_run_handler` and `_summary`. Add any missing import
  (`sqlalchemy.update`, `JobStatus`, `ScoringTraceRow`, `register_trace_handlers`) the way that
  module's neighbours import it.

  `backend/tests/test_score.py`:

```python
@pytest.mark.req("FR-213")
def test_a_quote_input_naming_a_produced_value_is_refused_on_score(
    client: TestClient, scoring_headers: dict[str, str], compiled_version: Any
) -> None:
    """FD-1425, `/score`: `s_expr` produces `payable`; an input so named is refused by name."""
    body = _quote({"rating_version_ref": SCORED_REF})
    body["inputs"]["payable"] = 1
    response = client.post(SCORE_URL, json=body, headers=scoring_headers)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'payable'" in response.json()["detail"]


@pytest.mark.req("FR-213")
def test_a_pending_trace_whose_context_names_a_produced_value_is_not_reproduced_as_a_price(
    client: TestClient,
    scoring_headers: dict[str, str],
    compiled_version: Any,
    database: Any,
    blob_store: Any,
    workspace_id: Any,
) -> None:
    """FD-1425, trace reproduction (`trace_handlers.py:98`). After the fix `/score` refuses
    such a context before a trace is pended, so the case is a row pended before the fix."""
    register_trace_handlers()
    _run(_set_trace_sample_rate(database, workspace_id, 1.0))
    served = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )
    assert served.status_code == 200, served.text
    (row,) = _run(_rows_for(database, workspace_id))
    (job,) = _run(_trace_produce_jobs(database, workspace_id))
    planted = dict(row.pending_quote_context)
    planted["inputs"] = {**planted["inputs"], "payable": 1}

    async def _plant_and_run() -> tuple[JobStatus, ScoringTraceRow]:
        async with database.unit_of_work() as session:
            await session.execute(
                update(ScoringTraceRow)
                .where(ScoringTraceRow.id == row.id)
                .values(pending_quote_context=planted)
            )
        status = await execute_job(database, job.id, blob_store)
        async with database.session() as session:
            after = await session.get(ScoringTraceRow, row.id)
        assert after is not None
        return status, after

    status, after = _run(_plant_and_run())
    assert status is JobStatus.FAILED
    assert after.status == "pending"
```

  **What the trace assert expects:** the Job fails on the refusal and completes nothing. No
  ruling fixes the handler's behaviour on a refusal. If the shipped `execute_job` records it
  differently, mirror the shipped form and record that in the ledger. The invariant that must
  hold is that no completed trace carries a price built on the planted key. Also read the failed
  Job's recorded error, the way this module's neighbours read a Job row, and assert that it
  carries `INPUT_CONTRACT_VIOLATION`.

  `backend/tests/test_score_compare.py`:

```python
@pytest.mark.req("FR-213")
def test_a_context_input_naming_a_produced_value_is_a_422_on_compare(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    """FD-1425, `/score/compare` (`api/score.py:447`)."""
    body = _body()
    body["context"]["inputs"]["payable"] = 1
    response = client.post(COMPARE_URL, json=body, headers=reader_headers)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'payable'" in response.json()["detail"]
```

  Check that both of `two_versions`' algorithms produce `payable`. If one does not, plant a
  name that both produce, and say which in the ledger.

  `backend/tests/test_scoring_handlers.py`:

```python
@pytest.mark.req("FR-213")
async def test_a_dataset_column_named_like_a_produced_value_is_refused_per_row(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    """FD-1425, batch: a dataset column named `payable` becomes a `ctx.inputs` key on every
    row, and every row is refused. Per-row isolation (FR-255) keeps the Job running."""
    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )
    frame = _scoring_frame(4).with_columns(pl.lit(1).alias("payable"))
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    result, _ = await _run_handler(
        database, blob_store, workspace_id, principal, _parameters(dataset_version_id)
    )
    summary = await _summary(database, blob_store, result)
    ref_result = summary["results"][0]
    assert ref_result["error_counts"] == {"INPUT_CONTRACT_VIOLATION": 4}
    assert ref_result["outcome_counts"]["error"] == 4
    assert "payable" in ref_result["error_samples"]["INPUT_CONTRACT_VIOLATION"][0]
```

  These four tests need the database stack. If it is down, record that and do not substitute a
  mock: the path is the thing under test.

- [ ] **Step 4: Record the hash, then run at the base commit and read each failure's cause.**

```bash
OMP_NUM_THREADS=1 nice uv run python -c "
import asyncio, sys; sys.path.insert(0, 'packages/pricing-core/tests')
import test_rating_score as T
from pricing_core.rating.compile import compile_bundle
print(asyncio.run(compile_bundle(T._version(), T._FakeResolver())).content_hash)"
```

  Run it twice. If the two values differ, STOP: the hash assert would then be a plan defect.
  Otherwise paste the value into `_SCORE_FIXTURE_HASH`. Then run the pricing-core module, and
  then each backend red alone. Expected, by cause (a FAIL with a different reason is a plan
  defect, and is reported):

  | Test | At the base commit | The cause that must show |
  |---|---|---|
  | `test_the_ordered_no_key_quote_is_unchanged` | PASS | — (a pin) |
  | `test_the_3f_case_is_refused` | FAIL | `DID NOT RAISE` (it quotes payable 777) |
  | `…_is_refused[<name>]`, each name | FAIL | `DID NOT RAISE` |
  | `…_is_refused_in_a_batch[<name>]`, each name | FAIL | `assert 'quoted' == 'error'` |
  | `test_the_bundle_hash_is_unchanged` | PASS | — (a pin) |
  | `…_refused_on_score` (backend) | FAIL | `assert 200 == 422` |
  | `…_not_reproduced_as_a_price` (backend) | FAIL | `JobStatus.SUCCEEDED is JobStatus.FAILED` |
  | `…_is_a_422_on_compare` (backend) | FAIL | `assert 200 == 422` |
  | `…_refused_per_row` (backend) | FAIL | `assert {} == {'INPUT_CONTRACT_VIOLATION': 4}` |

  Record each run's tail verbatim in the ledger, with the commit.

- [ ] **Step 5: Commit.**

```bash
git add packages/pricing-core/tests/test_rating_shadowed_inputs.py backend/tests/test_score.py \
  backend/tests/test_score_compare.py backend/tests/test_scoring_handlers.py
git commit -m "test(rating): FD-1425 emergency reds — an input overrides a produced value"
```

### Task 2 as first filed — "The root, in `score_one`'s path": WITHDRAWN

*(Withdrawn 2026-10-05, pre-mint, after 17:32:18 BST, on 17:27:55 item 1: the cause is not in
`score_one`'s path. It is `to_wire`'s sink fan-in (`runtime.py:495-499`) together with
whole-context `passThrough`, and it is PL 9567's (R-b). The withdrawn task's text, the
`_SHADOWED` list and the "guard (c) patched out → 5250" root test are at this plan's first
filed commit, `ff813792ad81d7cde2d8d79c099fb7b14beec08c`. The executor does not run them.)*

### Task 2: Guard (c) and T2, in one commit (was Task 3 as first filed)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py`. Add a check after
  `_check_billing_surface` (`:425-433`), and call it once in `score_one` and once in
  `_score_context_sync`, right after `_check_billing_surface(ctx)`.
- Modify: `packages/pricing-core/tests/test_quote_input_raise_sites.py` (`_INPUT_FREE`).
- Modify: `packages/pricing-core/tests/test_rating_shadowed_inputs.py` (append the in-place
  clamp test).
- Modify: `docs/specs/03-rating-engine.md`, the FR-213 row (`:82`): RL-1423's T2.

**Interfaces:**
- Produces: `_check_no_shadowed_produced_names(algorithm: RatingAlgorithm, inputs:
  Mapping[str, Any]) -> None`.

- [ ] **Step 1: The check.**

```python
def _check_no_shadowed_produced_names(
    algorithm: RatingAlgorithm, inputs: Mapping[str, Any]
) -> None:
    """FR-213 (FD-1425): an undeclared quote input never names a value a step produces. The
    declared inputs are subtracted first, so a declared input that a clamp re-produces in
    place is a legitimate key (the maintainer's (by delegation) 17:22:47 DP-2)."""
    declared = {field.name for field in algorithm.input_contract}
    produced = {
        str(name)
        for step in algorithm.steps
        if step.type not in ("input", "output")
        for name in _as_list(getattr(step, "produces", None) or [])
    }
    shadowing = sorted((produced - declared) & inputs.keys())
    if shadowing:
        _raise_named(
            "INPUT_CONTRACT_VIOLATION",
            f"inputs {shadowing} name values the algorithm produces (FR-213); a quote input "
            "never stands in for a produced value",
        )
```

  Check the sample against the shipped `model_schema.rating` step classes: `type` on every
  class, and which classes carry `produces`. Mirror `score.py`'s own reads of `step.produces`
  (`:456`, `:463`) rather than this sample.

- [ ] **Step 2: Call it on both paths**, right after `_check_billing_surface(ctx)`:
  `_check_no_shadowed_produced_names(algorithm, ctx.inputs)`.

- [ ] **Step 3: Register the raise site.** Add this entry to `_INPUT_FREE`:
  `("rating/score.py", "_check_no_shadowed_produced_names"): 1,  # names declared step outputs, never a value`.

- [ ] **Step 4: Add the exception's red** (DP-2: "A red test for that exception") to
  `test_rating_shadowed_inputs.py`. It calls the check directly and imports it inside the
  test:

```python
_IN_X = {"step_id": "s_in", "type": "input", "label": "x", "input_name": "x",
         "on_missing": "error", "produces": "x"}
_CLAMP_X = {"step_id": "s_clamp_x", "type": "constraint", "label": "Cap x",
            "condition": "x <= 10", "on_violation": "clamp", "clamp_bounds": {"max": "10"},
            "reason_code": "X_CAPPED", "consumes": ["x"], "produces": ["x"]}
_A = {"step_id": "s_a", "type": "expression", "label": "base = x*100", "expr": "x * 100",
      "result_type": "money_minor", "consumes": ["x"], "produces": "base"}
_OUT = {"step_id": "s_out", "type": "output", "label": "out", "output_name": "base_out",
        "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["base"]}


@pytest.mark.req("FR-213")
def test_a_declared_input_re_produced_in_place_is_not_a_shadow() -> None:
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.score import _check_no_shadowed_produced_names

    algorithm = RatingAlgorithm.model_validate({
        "slug": "clamp-x", "version": 1,
        "input_contract": [{"name": "x", "type": "int", "nullable": False, "min": 0, "max": 1000}],
        "outputs": [{"name": "base_out", "type": "money_minor", "required": True}],
        "steps": [_IN_X, _CLAMP_X, _A, _OUT], "sub_graphs": []})
    _check_no_shadowed_produced_names(algorithm, {"x": 3})  # a declared input: no raise
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION.*'base'"):
        _check_no_shadowed_produced_names(algorithm, {"x": 3, "base": 7})
```

  If `RatingAlgorithm.model_validate` refuses this algorithm, mirror the clamp shape of
  `test_rating_score.py`'s `s_clamp` and record the difference. Do not weaken the assert.

- [ ] **Step 5: T2.** Apply RL-1423's T2 text byte-for-byte, with no paraphrase, at the end
  of the FR-213 row's last cell (`03` `:82`), citing RL-1423 (17:30:02 item 2). Run
  `python3 scripts/audit-docs.py`: before the mint only check 31 may fail. If RL-1423 is not
  minted at dispatch, STOP: it is this plan's activation need.

- [ ] **Step 6: Run, and prove each call is load-bearing.** Run the pricing-core module,
  `test_quote_input_raise_sites.py` and `test_rating_score.py`, then the four backend reds
  one file at a time. Every test passes.
  - Remove the call from `score_one`, run the module, and record that the `score_one` cases
    fail with `DID NOT RAISE` while the batch cases pass. Restore the call.
  - Do the same for `_score_context_sync`: the batch cases fail alone. Restore the call.

  `git diff` must show both calls afterwards.

- [ ] **Step 7: Commit, guard (c) and T2 together** (17:30:02 item 2: "in the same commit"):

```bash
git add packages/pricing-core/src/pricing_core/rating/score.py \
  packages/pricing-core/tests/test_quote_input_raise_sites.py \
  packages/pricing-core/tests/test_rating_shadowed_inputs.py docs/specs/03-rating-engine.md
git commit -m "fix(rating): refuse an undeclared input naming a produced value (FD-1425 (c); FR-213 T2, RL-1423)"
```

### Task 3: The gate and the ledger (was Task 4 as first filed)

- [ ] **Step 1:** Before any full run, check `pgrep -af 'pytest|vitest|flock'` and the gate
  slot. Take the slot only on the lead's word.
- [ ] **Step 2:** The gate-runner runs `CLAUDE.md` §11, both halves, on the slice head. The
  ledger names the tree, the exit code of each command, and any failing excerpt.
- [ ] **Step 3:** `uv run python scripts/req-coverage.py` shows FR-213 carrying the new tests.
- [ ] **Step 4:** The ledger records these verbatim:
  - the per-name table;
  - Task 1 Step 4's base-commit runs;
  - Task 2 Step 6's two removed-call runs;
  - the four backend reds passing at the head;
  - the gate table.
- [ ] **Step 5:** The ledger states that the merge lifts the 17:25:07 hold. The lead records
  the lift in `eta.md` Holds and `holds-2026-10-01.md`.

## What this plan does not cover

- **The wiring fix** (list order; FR-212) and **(R-b)**, the sink fan-in root
  (`runtime.py:495-499`), are PL 9567 (#1193). It follows this slice and is rebased onto it.
  A dated delta on PL 9567 drops (c), because (c) is delivered here.
- **A no-caller-key misprice**, if auditor-fanin finds one, is a second emergency slice after
  this one (the maintainer's correction to 17:27:55 item 3), not this plan.
- **FR-246's declared-inputs rule in general** (FD-1374, PL 9776) stays its own (the 17:22:47
  entry, DP-3).
- **Dislocation** is not changed: it selects declared inputs only (RL-1394).
- **FD-1425's essay amendment** (the ordered algorithm is exposed too) belongs to the auditor
  (the 17:25:07 entry, item 4).

## Self-review (2026-10-05; re-run after the narrowing)

- **Ruling coverage:**
  - Guard (c) alone, at `score.py:911` and `:1067`, is Task 2, with
    `INPUT_CONTRACT_VIOLATION` and the declared inputs subtracted.
  - T2 lands in the same commit (Task 2 Steps 5 and 7).
  - Each red the ruling names is a named test:
    - (3f), the one shadowed name: `test_the_3f_case_is_refused`;
    - every produced name: the parametrised tests;
    - per path: the four backend tests;
    - 5250 unchanged, and the hash unchanged: the two pins;
    - the in-place clamp exception: Task 2 Step 4.
  - The root is not here; it is PL 9567's (R-b).
- **Placeholders:** `_SCORE_FIXTURE_HASH` is recorded by a command (Task 1 Step 4). Nothing
  else is left open.
- **Literals checked at `4d3be141`:**
  - `test_rating_score.py`: `_FakeResolver` (`:103`), `_version` (`:118`), `_ctx` (`:143`),
    the produced names in `_algorithm_payload` (`:46`);
  - `test_rating_version_compile.py`: `_minimal_algorithm` (`:50`);
  - `test_scoring_handlers.py`: `_scoring_frame` (`:51`);
  - `test_score.py`: `_quote` (`:123`), `SCORED_REF` (`:63`), `SCORE_URL` (`:59`);
  - `test_score_compare.py`: `COMPARE_URL` (`:36`);
  - `test_quote_input_raise_sites.py`: `_INPUT_FREE` (`:62`);
  - `score.py`: `_check_billing_surface` (`:425`).
