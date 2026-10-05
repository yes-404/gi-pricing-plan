---
id: PL-9567
family: plan
kind: leaf
title: WK-673 — FD 9572 fix, to_wire wires each consumed name to its producer over a stable topological order, and a quote input never shadows a produced value (FR-212, FR-213): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1374, RL-1263, SL-1391]
---

# PL 9567 (working id) — WK-673: the FD 9572 fix, wiring by dependency order and no shadowed produced value, leaf plan

Filed under working id 9567 (this plan) and slice working id 9568 (its `SL-` row under WK-673 in
[`../roadmap.md`](../roadmap.md), `draft`). The lead reserved both. The finding is FD 9572
(working id, draft PR #1183, branch `fd-9572-to-wire-list-order`). Everything below was measured
at `origin/main` `4d3be1414ad4dacdaa0c14ef49fb21853adbaed6` on 2026-10-05, unless a line says
otherwise.

## Delta, 2026-10-05 (after 17:30:13 BST, pre-mint): fix (c) moves to PL 9560; DP-1..DP-4 ruled

This plan is still an unmerged draft. This delta records three rulings and what each removes
from the plan. It does not rewrite the plan: each withdrawn part keeps its text and carries a
pointer back here.

1. **DP-1..DP-4 were ruled** by the maintainer (by delegation) in the entry headed
   "2026-10-05 17:22:47 BST — PL 9567 (the FD 9572 fix, #1193 @f4e4380b) DP-1..4 RULED;
   CORRECTION of my error code; the unmeasured premise kept as a STOP". The rulings:
   - DP-1 (a): `INPUT_CONTRACT_VIOLATION`.
   - DP-2 (a): refuse by name, with the declared inputs subtracted.
   - DP-3: not decided ("(c) is exactly 'an undeclared key naming a produced value'; FR-246's
     declared-inputs rule (FD-1374 / PL 9776) stays its own").
   - DP-4 (a): "an RL adopts T1 (FR-212 …) and T2 (FR-213) BEFORE activation". That ruling is
     RL 9562 (working id).
2. **The STOP fired, and (c) moved.** The maintainer's (by delegation) entry "2026-10-05
   17:25:07 BST — URGENT RULING: FD 9572's premise FALSE; OPTION (iii): a HOLD now, and an
   EMERGENCY (c)-only slice FIRST in lane B (WK-1178); the wiring fix after", item 3, verbatim:
   > The WIRING fix (PL 9567, list order) follows as planned, after the emergency slice, rebased on it; its (c) part is then already delivered, so PL 9567 drops (c) by a dated delta and keeps (a)/(b).

   Fix (c) and its reds are now **PL 9560** (working id; SL 9561 under WK-1178; #1196). PL 9560
   also fixes the root that auditor-premise found in `score_one`'s path.
3. **The premise, answered.** The maintainer's (by delegation) addendum, "2026-10-05 17:25:23
   BST — ADDENDUM to my 17:25:07 urgent ruling …", says: "the ZEN wiring of an ORDERED graph is
   correct (350 for every extra key)". So `test_a_misordered_algorithm_prices_as_its_topological_twin[ctx1]`
   (engine level, `{x: 3, base: 7}`) is expected to pass after Task 2. The shadow that was found
   sits in `score_one`'s path, and it is PL 9560's.

**What this removes from this plan:**
- Task 3, in full (the check, its calls, its `_INPUT_FREE` entry, the in-place clamp test, T2).
- Acceptance items 4 and 9.
- Task 1's (c) tests: `test_a_quote_input_naming_a_produced_value_is_refused`,
  `…_is_refused_in_a_batch`, and Step 1c's four backend reds.
- The write-set rows for `test_quote_input_raise_sites.py` and the three backend test files.
- The `score.py` row, so this plan no longer edits `score.py` at all.

**What the plan keeps:** (a) and (b). That is Tasks 1 and 2 without the (c) tests, Task 4,
the pins, and T1 (FR-212, adopted by RL 9562; applied in Task 2 as Step 6b below).

**Contention, now:**
- This plan's write set is `runtime.py` (`to_wire` and the new helper), its own test module,
  the `03` FR-212 row, the roadmap row and the INDEX.
- It no longer serialises with PL 9688 on `score_one` or `_score_context_sync`: its file set
  is name-disjoint from PL 9688's (`_decision_table_node` in `runtime.py`).
- It still serialises with PL 9776 on `to_wire`.

**Activation needs, replacing those in the SL 9568 row:**
- FD 9572 minted.
- RL 9562 minted (it adopts T1) before this plan.
- PL 9560 merged, and this slice rebased onto it.
- This plan made `active` by a dated line.
- A free build lane.

**Task 2, Step 6b (added by this delta):** apply T1, byte-for-byte as RL 9562 adopts it, at
the end of the FR-212 row's last cell (`03` `:81`). Then run `python3 scripts/audit-docs.py`:
only check 31 may fail before the mint.

## Delta 2, 2026-10-05 (after 17:35:05 BST, pre-mint): (R-b), the sink fan-in, is this plan's root

The maintainer's (by delegation) entry "2026-10-05 17:27:55 BST — FD 9572 CAUSE: the sink
fan-in plus whole-context passThrough; RULING: (c) ALONE is the emergency slice; (R-b) is the
root, in PL 9567; one more case to measure; A-2 readings", item 2, verbatim:

> 2. (R-b) is the ROOT and goes into PL 9567 (the wiring slice), red first with the fan-in case: no side branch may carry a stale copy of a produced name into the sink (one ordered merge at the sink, or produced names stripped from the relayed context; the planner proposes, and if it changes every bundle's hash that is stated and approved by me).

**The cause**, from the same entry (auditor-premise, read-only at `4d3be141`):
- The sink rule (`runtime.py:495-499`) wires every interior step whose produced names no other
  step consumes to the sink. That includes produce-nothing steps such as the decline
  constraints, so the sink has a fan-in.
- Every node carries the whole context forward (`passThrough`: `:174`, `:268`, `:353`, `:389`;
  the docstring at `:428-432`). So each branch reaching the sink holds a full copy of the
  context as that branch last saw it.
- At the fan-in, the last-listed branch wins. This was inferred from three runs; zen's merge
  code was not read.

**The mechanism: DP-R1, for the maintainer (by delegation).** Item 2 leaves the choice to the
planner and requires approval of any bundle-hash change.

| Option | What it does | Bundle hash | Cost and risk |
|---|---|---|---|
| **(i) One ordered path** | `to_wire` wires the interior steps as a single chain over the stable topological order of Task 2 (`_dependency_order`): input → the first step → … → the last step → the sink (or `__exact_reads` → output). Every node then has exactly one incoming edge. The dependency edges and the sink fan-in are gone, so no merge happens anywhere, and each name's final producer writes it after every earlier copy. The `model_call` handler (`_model_call_handler`, `runtime.py:512`) must pass the context through: today it returns only `{"output": {produced names}}` (`:581`), which a chain would turn into a dropped context. | **Unchanged.** `content_hash = bundle_hash(graph, pins)` (`compile.py:641`) hashes the `JdmGraph`, never the wire. | The wire changes for every algorithm with a branch; a purely linear one (`[in, A, B, out]`) wires exactly as today. It relies on whole-context `passThrough`, which **PL 9776 (#1051, F35 remedy) turns off** for `_constraint_node` and `_decision_table_node` (its plan `:503`). The two cannot both land as written. |
| (ii) Strip produced names from the relayed context | `inputNode` relays only the declared inputs. | Unchanged | It closes only caller copies, which guard (c) (PL 9560) already refuses at the entry. It cannot remove an internal stale copy (a branch that forks before an in-place clamp), which is the case auditor-fanin is measuring. |
| (iii) An ordered merge at the sink | Keep the DAG and order the sink's incoming edges so that the final producers merge last. | Unchanged | It rests on zen's fan-in merge order, which was inferred from three runs and never read. A dependency on unread engine behaviour is the class of defect this finding is. |

**Recommendation: (i).** It is the only option that does not depend on how zen merges a
fan-in, because it leaves no fan-in to merge. It keeps every bundle hash. It also subsumes
Task 2's per-name edge resolution: in a chain, list order is irrelevant once the topological
order is used, which is the FR-212 rule (a) states. **Its conflict with PL 9776 is the
maintainer's to settle**:
- PL 9776's `passThrough`-off is a cost remedy (its P1, "the engine copies the whole context
  into each node");
- (i) needs `passThrough` on every node;
- whichever lands second must be re-planned.

**What this adds:** Task 2b below (red first). Its activation need is DP-R1 decided by a dated
line. Under (ii) or (iii), Task 2b is rewritten before dispatch.

**If auditor-fanin answers YES** (a misprice with no caller key), (R-b) becomes a second
emergency slice after PL 9560, by the maintainer's correction to item 3 of the 17:27:55 entry.
Task 2b then moves out of this plan by a further delta.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax
> for tracking. Also bound: `python-test` (the `req` markers, the negative tests),
> `python-package` (pricing-core's boundaries) and `dev-commands` (the gate's traps).

## Goal

A saved Rating Algorithm prices the same whatever order its steps are listed in, and
a quote input can never stand in for a value a step produces.

**Architecture:** `to_wire` (`pricing_core/rating/runtime.py`) keeps its incremental
`produced_by` resolution unchanged, but iterates the interior steps in a stable topological
order computed by a new helper, `_dependency_order` (Kahn's algorithm with the list position as
the tie-break, through a heap). An already-ordered list therefore wires exactly as today. In
`score.py`, a new pre-check, `_check_no_shadowed_produced_names`, refuses a `ctx.inputs` key
that names a value a non-`input` step produces, on both engine paths (`score_one` and
`_score_context_sync`).

**Tech Stack:** Python 3.12, pricing-core, the ZEN engine binding (`zen`), pytest. No new
dependency (`heapq` is the standard library).

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3 (FR-212, FR-213,
FR-255) and §5.2 (`score_one`). The finding: FD 9572 (#1183; its essay carries the ruled fix
verbatim). The ruling: the maintainer's (by delegation) entries quoted under "Sources".

## Acceptance Standard

Each item is a command a fresh reviewer can run from the worktree root, after `uv sync
--all-packages` (`dev-commands`). Full-suite runs take the one gate slot (RL 9620, #1162).

1. `uv run pytest packages/pricing-core/tests/test_rating_wire_order.py -q` passes, and the
   ledger records the same file failing at the slice's base commit for the four reds of
   Task 1, each for the cause Task 1 Step 2 names (not merely "failed").
2. `test_a_misordered_algorithm_prices_as_its_topological_twin` gives 350 for
   `[in, B, A, out]` with ctx `{x: 3}` and with ctx `{x: 3, base: 7}` (never 57).
3. `test_a_clamp_listed_before_its_producer_still_binds` gives `payable_premium_minor` 5250
   and a `constraints` rung of 5000 with `s_clamp` listed before `s_office` and
   `min_premium_minor` 5000.
4. *(Withdrawn 2026-10-05 by the Delta: (c) is PL 9560's.)* `test_a_quote_input_naming_a_produced_value_is_refused` raises `INPUT_CONTRACT_VIOLATION`
   naming the key, through `score_one` and through `score_batch` (DP-1 and DP-2 as
   recommended; if decided otherwise, the dated decision line names the replacement assert).
5. `test_a_topologically_listed_algorithm_wires_exactly_as_listed` and
   `test_the_bundle_hash_is_unchanged` pass, and the ledger records each failing once on a
   deliberately broken helper (Task 2 Step 5).
6. `uv run pytest packages/pricing-core/tests/test_rating_score.py
   packages/pricing-core/tests/test_rating_runtime.py
   packages/pricing-core/tests/test_quote_input_raise_sites.py -q` passes with no edited
   assert.
7. The full gate (`CLAUDE.md` §11, both halves) passes on the slice head, run by the
   gate-runner inside the one gate slot, and the ledger names the tree it ran on.
8. `python3 scripts/audit-docs.py` fails only on check 31 until the mint, and is clean after.
9. *(Withdrawn 2026-10-05 by the Delta: the four path reds are PL 9560's.)* One red test **per reachable path** of fix (c), each recorded failing at the base commit
   for the cause Task 1 Step 2 names, and passing at the head (the 17:15:09 entry):
   - `/score`: `backend/tests/test_score.py::test_a_quote_input_naming_a_produced_value_is_refused_on_score`
   - `/score/compare`: `backend/tests/test_score_compare.py::test_a_context_input_naming_a_produced_value_is_a_422_on_compare`
   - trace reproduction: `backend/tests/test_score.py::test_a_pending_trace_whose_context_names_a_produced_value_is_not_reproduced_as_a_price`
   - batch: `backend/tests/test_scoring_handlers.py::test_a_dataset_column_named_like_a_produced_value_is_refused_per_row`

   Run: `uv run pytest <each file>::<each test> -q`, one file at a time, outside a gate window.
   *(Item added 2026-10-05, after 17:23:51 BST, on the 17:15:09 entry; the lead's order.)*

## Global Constraints

- Money is integer minor units, or `Decimal` in the rating path, never float (`CLAUDE.md` §7).
- `pricing-core` stays importable with zero FastAPI/SQLAlchemy/Redis dependencies (`CLAUDE.md`
  §2; `.importlinter`'s `core-has-no-infrastructure`).
- A coded error names the field and the constraint, never the value (NFR-499, RL-917;
  `test_quote_input_raise_sites.py`).
- `mypy --strict` and `ruff` cover `packages/` (`.claude/skills/repo-architecture`).
- One full gate at a time on this VM; up to three builds; targeted single-file runs are allowed
  outside a gate window (RL 9620, #1162, the maintainer's (by delegation) 15:27:25 BST entry).
- A measurement runs as `OMP_NUM_THREADS=1 nice` and never beside a held gate slot.

---

## Sources

The maintainer's (by delegation) two entries in `channel/to-lead.md` (a local channel file,
cited by its header), quoted verbatim.

**"2026-10-05 17:06:26 BST — FD 9572 (to_wire wires by LIST order): reproduced; severity waits
on (1)/(2); the FIX RULED now; RL 9588 / RL 9586 noted"**, the ruled fix and placement:

> THE FIX, RULED (root, not symptom): FR-212 makes a Rating Algorithm a DAG, so LIST ORDER CARRIES NO MEANING and must never decide wiring.
>  (a) to_wire (and to_jdm, if it emits edges by order) wires every consumed name to its PRODUCER by name through the graph, over a STABLE topological order computed from the dependency edges (Kahn with list order as the tie-break, so an already-ordered list is unchanged and every existing bundle hash is stable; a test asserts the hash of a topologically listed algorithm is unchanged).
>  (b) No save-time refusal of a misordered list: authors may list steps in any order; that is what a DAG means.
>  (c) SEPARATELY, a quote input must never SHADOW a produced value: if (1) shows extra ctx keys reach ZEN, then a context key that names a step's produced value is refused (VALIDATION_FAILED, naming the key) or dropped per the input_contract. Its own red test (ctx {x:3, base:7} on the CORRECTLY ordered algorithm still gives 350, never 57).
>  Red first: [in, B, A, out] asserting 350; the clamp case from (2); the shadowing case. The WK-1250 S2 inliner uses the same topological order (RL 9586's P5, the DM's proposal: ACCEPTED, as it is the same rule).
> PLACEMENT: its own small WK-673 slice (or folded into the FD 9707 fix if that plan's write set already covers runtime.py's to_wire and the planner shows no scope creep). The planner proposes which, after (1)/(2).

**"2026-10-05 17:10:08 BST — FD 9572: HIGH, FINAL; TOP planning priority; an exposure scan
now; RL 9573 noted"**, the severity, (c) made required, and the lane:

> FD 9572 (#1183 @7e9d38d7): HIGH, FINAL, owner WK-673, before the P2 exit demo. Both checks give a SILENT WRONG PRICE on reachable paths: (1) score_one (score.py ~:911) spreads `**ctx.inputs` into the ZEN context and _validate_inputs tolerates extras, so a CALLER sending office_premium_minor=1000 to a misordered algorithm gets 1050 against 1507: a caller-controlled price; (2) a clamp listed before its producer silently skips the minimum premium (1507 vs 5250, no error). The essay carries my 17:06:26 fix verbatim, and (c) (refuse or drop a context key naming a produced value) is now REQUIRED.

> 2. LANE: under my priority rule it takes the first build lane free once its plan is active, tied with the FD 9707 fix; on a tie, FD 9572 goes FIRST.

**Placement, decided by the planner and accepted by the lead (2026-10-05, after 17:11:35
BST): its own slice, not a fold into PL 9688.** PL 9688's write set (#1145, its "Write set"
table) edits `_decision_table_node`, the `runtime.py` docstring and `_as_at_window` in
`runtime.py`, never `to_wire`, so the ruling's fold condition is not met. PL 9688 also says of
an input carrying a produced or stamped name: "Whether an input may carry a stamped name at all
is FD-1374's class … **This plan does not decide it.**" Folding (c) in would reverse that.

**Added 2026-10-05, after 17:23:51 BST: "2026-10-05 17:15:09 BST — FD 9572 exposure: NONE
today; fix (c) placement confirmed"**, the exposure scan and the per-path reds, quoted verbatim:

> auditor-towire, read-only at 137bc817: gipricing holds 1 rating_algorithms row (demo-fixture-motor@1, list = topological); a static scan of 28 literal step lists (20 evaluable) plus a dynamic run of every named builder found none misordered (2 deliberate cycle fixtures); no step list in JSON/YAML/SQL/TS. Caveat: inline-assembled test-body algorithms not run. So no live mispricing; the interim hold stays until the fix merges. Extra-key reach: REACHABLE on /score (api/score.py:350-375), /score/compare (:447), trace reproduction (trace_handlers.py:98) and BATCH (every dataset column but four becomes ctx.inputs, set by the dataset owner); SAFE on dislocation (analysis.py _score_pass, RL-1394). The {**ctx.inputs} merge sits at score.py ~:911 (score_one) and ~:1067 (_score_context_sync), so fix (c) goes in that shared code and covers all four paths, with a red test per path (score, compare, trace reproduce, batch). #1183 final at 89ad846d.

So: no stored algorithm is misordered today (auditor-towire's scan at `137bc817`), and the
interim hold stays until this slice merges. Fix (c) sits where Task 3 already puts it, the two
context builders in `score.py`, and Task 1 Step 1c adds the four per-path reds.
Dislocation is left as it is, because it already selects declared inputs only (RL-1394).

## Verified facts (at `4d3be141`)

- **`to_wire`** is `packages/pricing-core/src/pricing_core/rating/runtime.py:412`.
  `interior_ids` (`:453-455`) is the list of interior step ids in `graph.nodes` order. The
  wiring loop (`:461-492`) builds `produced_by` incrementally: for each step it first appends
  one edge per consumed name from `produced_by.get(name, _INPUT_ID)`, then records the step's
  own produced names. The comment at `:463-473` explains why the build is incremental: a
  clamp that consumes and re-produces a name must resolve its incoming edge to the earlier
  producer, never to itself. The sink loop (`:496-499`) also iterates `interior_ids`.
- **`to_jdm`** is `compile.py:477`. It fills `nodes` with `for step in algo.steps`, in list
  order, and emits **no edges** (only `produces`/`consumes` lists). So the ruling's "and
  to_jdm, if it emits edges by order" does not apply, and `compile.py` is not in the write set.
- **The bundle hash does not read the wire.** `compile_bundle` sets
  `content_hash=bundle_hash(graph, pins)` (`compile.py:641`) over the `JdmGraph`, and
  `CompiledBundle.content_hash` is `Bundle.content_hash` (`runtime.py:673`). A change confined
  to `to_wire` cannot move a hash. The test the ruling asks for pins that.
- **The dependency rule to mirror** is `RatingAlgorithm._graph_invariants`
  (`packages/model-schema/src/model_schema/rating.py:395`): a step depends on every producer of
  each name it consumes, excluding itself (`:414-427`). Under that rule a re-production chain
  of three steps would be a cycle, refused at save. The helper below uses the same rule, so it
  cannot meet a cycle that `_graph_invariants` accepted. Its Kahn loop (`:430-440`) pops from
  the end of a list, so its order is not stable, and it is discarded: `self.steps` is never
  reordered.
- **Both engine paths build the context the same way:**
  `{"effective_date": ..., "purpose": ctx.purpose, **ctx.inputs}` at `score.py:910-912`
  (`score_one`, `:876`) and `:1066-1068` (`_score_context_sync`, `:1045`; `score_batch` and
  `rating/testing.py`'s `evaluate_golden_quotes` reach the engine through it). No other call to
  `decision.evaluate` or `decision.async_evaluate` exists under `packages/*/src` or
  `backend/src` (`grep -rn 'decision.evaluate\|decision.async_evaluate' packages/*/src
  backend/src`).
- **`_validate_inputs`** (`score.py:333`) tolerates extra keys (its docstring). The precedent
  for refusing a key by name is `_check_billing_surface` (`score.py:425-433`):
  `_raise_named("INPUT_CONTRACT_VIOLATION", ...)`, called in both paths after
  `_check_purpose_mount`. Its test is `test_a_billing_surface_request_is_refused`
  (`test_rating_score.py:523-533`), `pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION")`.
- **`INPUT_CONTRACT_VIOLATION` is the only per-quote input code the HTTP layer maps.**
  `backend/src/app/api/score.py` `_PER_QUOTE_CODES` holds `INPUT_CONTRACT_VIOLATION`,
  `RATE_TABLE_MISS`, `REFERENCE_LOOKUP_MISS` and `MODEL_CALL_FAILED`. Its comment: "A code
  outside this set is not a per-quote refusal … it reaches the caller as a 500". This is DP-1.
- **The raise-site census** (`packages/pricing-core/tests/test_quote_input_raise_sites.py`,
  `_INPUT_FREE`) fails when a `_raise_named` site is added without an entry. The new check's
  message names produced-value names, which the algorithm declares, never a value.
- **FD-1374** ([`../findings/FD-01374-fr-246-s-declared-inputs-rule-is-unenforced-for-names-and-03-s-own-example-declares-no-inputs.md`](../findings/FD-01374-fr-246-s-declared-inputs-rule-is-unenforced-for-names-and-03-s-own-example-declares-no-inputs.md))
  is the finding on undeclared names. Its remedy is PL 9776 (working id, `draft`, #1051,
  WK-1178). This is DP-3.
- **The reproduction** is FD 9572's Evidence §2 and §3 (script 1, sha256 `6690fa73…114ae0`;
  script 2, sha256 `fc02caa4…35228d`), run at `137bc817`. The values this plan asserts
  (350, 57, 1507, 5250, 1050) are copied from that essay's verbatim output.

## Decision points

*(Delta 2, 2026-10-05: DP-R1, the (R-b) mechanism, is open; it is set out in the Delta 2
section above and blocks Task 2b.)*

Three are open and block activation, so this plan stays `draft` until a dated decision line
settles them. Each is the decision-maker's (`delivery-process.md` §3), not the planner's.

| DP | Question | Options | Recommendation | Status | Tasks |
|---|---|---|---|---|---|
| **DP-1** | Which code refuses a shadowing key? The ruling names `VALIDATION_FAILED`. `score.py` raises `INPUT_CONTRACT_VIOLATION` for every per-quote input refusal, and `api/score.py`'s `_PER_QUOTE_CODES` maps only that one; another code from `score_one` reaches the caller as a 500 | (a) `INPUT_CONTRACT_VIOLATION`, as `_check_billing_surface` does; (b) `VALIDATION_FAILED`, which also needs `_PER_QUOTE_CODES`, `app.errors` and `03` §5.1 to take it (a wider write set into `backend/`); (c) a new code | (a): the ruled intent (a named, per-quote refusal) is met with no backend change, and the caller gets a 4xx, not a 500 | open | 3 |
| **DP-2** | Refuse or drop? The ruling allows "refused … or dropped per the input_contract" | (a) refuse a `ctx.inputs` key that a non-`input` step produces and that is not a declared input, naming the key; (b) drop every key not in `input_contract` before the engine call; (c) drop only the produced-name keys, silently | (a): a refusal tells the caller its request was wrong, and a silent drop hides it. (b) changes every caller that sends extras (the batch reader tolerates extra columns, `score.py:131-132`) and is FD-1374's class (DP-3). A declared input that a clamp re-produces in place (input `x`, a constraint consuming and producing `x`) is a legitimate key, which is why (a) subtracts the declared inputs | open | 3 |
| **DP-3** | Where does (c) end and FD-1374 begin? FD-1374 (FR-246: undeclared names are unenforced) is remedied by PL 9776 (#1051) | (a) this slice takes only the produced-name refusal of DP-2 (a); FD-1374 and PL 9776 keep the general undeclared-name rule, the stamped names (`effective_date`, `purpose`) and any engine-internal key (`{step_id}__violated`, `__exact__*`); (b) this slice also takes the stamped and engine-internal names; (c) fold (c) into PL 9776 and leave this slice (a) only | **Not decided here (the lead's order).** The planner notes that (a) keeps this slice's write set as written, and that (c) would leave the 1050-against-1507 caller-steered price open until PL 9776 runs, which is WK-1178's and serialises behind this slice on `to_wire` | open | 3 |
| **DP-4** | Does `03` take a text for the new behaviour? FR-212 says "directed acyclic graph" but not that list order carries no meaning; FR-213 says nothing on an input naming a produced value | (a) two T-texts below, adopted by a ruling before activation (as RL 9633 adopts PL 9649's); (b) no spec text: the fix makes code meet FR-212 as written, and (c) is a contract violation under FR-255 category 1 already | (a): (c) is a new refusal a caller can meet, and a capability not yet specified is a spec change first (`CLAUDE.md` §0) | open | 3, 4 |

**T1 (DP-4 (a)), appended to the FR-212 row as a dated amendment:** "*(Amended 2026-10-05,
FD 9572.)* The order in which an algorithm lists its steps carries no meaning: each consumed
name is wired to its producer through the graph, over a stable topological order of the
dependency edges. A misordered list is not refused at save."

**T2 (DP-4 (a)), appended to the FR-213 row:** "*(Amended 2026-10-05, FD 9572.)* A Quote
Context input whose name is a value some step produces, and is not itself a declared input, is
a contract violation, refused with a field-level error naming the key: a quote input never
stands in for a produced value."

## Write set, and its contention (`RL-1263`, RL 9620)

RL-1263: "Two concurrent build slices may not both change the same **existing** function,
class, method, spec section, or policy table … **Any other shared path serialises** unless the
lead's dispatch record names the path and the check showing that no existing definition is
edited by both." RL 9620 (#1162, working id) amends it: two slices from the same Work run at
once only when the dispatch record shows "(a) the file sets resolved by the existing contention
rules (exempt / one-sided / name-disjoint / serialise) and (b) NO plan dependency: neither slice
consumes the other's output (named, both ways)". The columns below were read on each plan's
branch at the head named in its header cell, on 2026-10-05.

| Path | This slice | FD 9707 fix (PL 9688, #1145 @`2f3269c8`) | S7 (PL-1419, #1127 @`305ffca9`) | FR-240 fix (PL 9649, #1152 @`df8ba756`) | F35 remedy (PL 9776, #1051 @`ecbb82ab`, WK-1178) | Class |
|---|---|---|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | added: `_dependency_order`, `import heapq`, the `GraphCycleError` import; edited: `to_wire` (`:453-499`: the iteration order and the comment at `:463-473`) | `_decision_table_node`, module docstring, `_as_at_window` | — | reads `_model_call_handler` only | **`to_wire`** (reference edges, `outputNode` wiring), `_decision_table_node`, `_constraint_node`, docstring rule 3 | **serialise with PL 9776** (the same existing function). Name-disjoint with PL 9688 |
| `packages/pricing-core/src/pricing_core/rating/score.py` | added: `_check_no_shadowed_produced_names`; edited: `score_one` (`:876`, one call), `_score_context_sync` (`:1045`, one call) | added `_check_as_at_values`; **`score_one` and `_score_context_sync`**, one call each | — | — | — | **serialise with PL 9688** (the same existing functions). This slice goes first (the 17:10:08 tie-break) |
| `packages/pricing-core/tests/test_rating_wire_order.py` | added (new module) | — | — | — | — | none |
| `backend/tests/test_score.py` | added (appended, no existing test edited): the `/score` and trace-reproduction reds | none. PL 9688 adds its own module `backend/tests/test_score_as_at.py` and does not edit this file | — | — | — | append-only; name-disjoint |
| `backend/tests/test_score_compare.py` | added (appended): the `/score/compare` red | — | — | — | — | append-only |
| `backend/tests/test_scoring_handlers.py` | added (appended): the batch red | — | — | — | — | append-only |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` | edited: `_INPUT_FREE` (`:62-79`, one entry added) | one entry added | — | — | — | registry (append); the second to merge re-gates |
| `docs/specs/03-rating-engine.md` | DP-4 (a) only: the FR-212 row (`:81`) and the FR-213 row (`:82`), a dated amendment each | the FR-221 row (`:107`) | the FR-231 row, §4.2, §5.1, §5.2 | adjacent `03` hunks (its T-texts) | — | shared file, distinct rows: the dispatch record names the path, the rows, and a trial `git merge-tree` rc between the heads |
| `docs/roadmap.md` | added: the SL 9568 row (plan PR only) | adds the SL 9685 row at the same place | — | adds its SL row | — | registry (append, distinct rows); the second to merge re-reads |
| `docs/INDEX.md`; the slice's ledger | regenerated; added | every PR | every PR | every PR | every PR | `generated` |

**Plan dependency, both ways.** None of PL 9688, PL-1419 or PL 9649 consumes this slice's
output, and this slice consumes none of theirs. PL 9776 edits `to_wire` and imports
`test_rating_score.py`'s `_algorithm_payload` (its plan `:509`), which this slice's clamp test
also imports: whichever merges second re-runs `test_rating_wire_order.py`. The WK-1250 S2
inliner (PL 9610, #1170) is ruled to use the same order (RL 9586's P5). `_dependency_order` is
private here; whether S2 imports it or its own inliner restates it is S2's plan's to say.

**Pairing for the dispatch record.** Beside S7 (lane A, the same Work): file sets
name-disjoint in code, `03` distinct rows, no plan dependency, so both RL 9620 conditions can
hold. Beside PL 9649: name-disjoint, no plan dependency. Beside PL 9688: **serialise**, this
slice first. Beside PL 9776: **serialise** (`to_wire`).

---

## Tasks

### Task 1: The reds

**Files:**
- Create: `packages/pricing-core/tests/test_rating_wire_order.py`

**Interfaces:**
- Consumes: `compile_bundle`, `ResolvedArtifact` (`pricing_core.rating.compile`);
  `load_bundle`, `to_wire` (`pricing_core.rating.runtime`); `score_one`, `score_batch`
  (`pricing_core.rating.score`); from `test_rating_score`: `_FakeResolver`, `_version`, `_ctx`.
- Produces: the test names the Acceptance Standard cites.

- [ ] **Step 1: Write the test module.** Mirror `test_rating_score.py`'s imports and markers
  (async tests with no explicit asyncio marker, `@pytest.mark.req(...)`). Do not reinvent its
  fixtures: import them, as `test_quote_input_raise_sites.py` does.

```python
"""FD 9572: wiring follows dependency order, never list order (FR-212); a quote input never
shadows a produced value (FR-213).

The algorithms and values are FD 9572's own reproduction (its Evidence §2 and §3)."""

from __future__ import annotations

import copy
from typing import Any
from uuid import uuid4

import polars as pl
import pytest
from test_rating_score import _FakeResolver, _ctx, _version

from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import Bundle, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import load_bundle, to_wire
from pricing_core.rating.score import score_batch, score_one

_IN = {"step_id": "s_in", "type": "input", "label": "x", "input_name": "x",
       "on_missing": "error", "produces": "x"}
_A = {"step_id": "s_a", "type": "expression", "label": "A: base = x*100",
      "expr": "x * 100", "result_type": "money_minor", "consumes": ["x"], "produces": "base"}
_B = {"step_id": "s_b", "type": "expression", "label": "B: premium = base + 50",
      "expr": "base + 50", "result_type": "money_minor", "consumes": ["base"],
      "produces": "premium"}
_D = {"step_id": "s_d", "type": "expression", "label": "D: fee = x + 1",
      "expr": "x + 1", "result_type": "money_minor", "consumes": ["x"], "produces": "fee"}
_OUT = {"step_id": "s_out", "type": "output", "label": "out", "output_name": "premium_out",
        "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["premium"]}
_OUT_FEE = {"step_id": "s_out_fee", "type": "output", "label": "fee", "output_name": "fee_out",
            "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["fee"]}


def _algo(steps: list[dict[str, Any]]) -> dict[str, Any]:
    outputs = [{"name": "premium_out", "type": "money_minor", "required": True}]
    if any(s["step_id"] == "s_out_fee" for s in steps):
        outputs.append({"name": "fee_out", "type": "money_minor", "required": True})
    return {"slug": "order-test", "version": 1,
            "input_contract": [{"name": "x", "type": "int", "nullable": False,
                                "min": 0, "max": 1000}],
            "outputs": outputs, "steps": steps, "sub_graphs": []}


def _order_version() -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "order-test", "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": "model:none@1",
        "created_at": "2026-08-29T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-08-29T12:00:00Z",
        "algorithm_ref": "rating_algorithm:order-test@1",
        "pins": {"rate_tables": [], "models": [], "reference_tables": [],
                 "custom_objectives": []},
        "model_reference_mode": "exact"})


class _OneAlgorithm:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payload)


async def _bundle(steps: list[dict[str, Any]]) -> Bundle:
    return await compile_bundle(_order_version(), _OneAlgorithm(_algo(steps)))


def _permute(steps: list[dict[str, Any]], move: str, before: str) -> list[dict[str, Any]]:
    steps = list(steps)
    step = next(s for s in steps if s["step_id"] == move)
    steps.remove(step)
    at = next(i for i, s in enumerate(steps) if s["step_id"] == before)
    steps.insert(at, step)
    return steps


async def _score_fixture(*, move: str | None = None, before: str | None = None) -> Any:
    resolver = _FakeResolver()
    key = "rating_algorithm:score-fixture@1"
    payload = copy.deepcopy(resolver._payloads[key])
    if move is not None and before is not None:
        payload["steps"] = _permute(payload["steps"], move, before)
    resolver._payloads[key] = payload
    return load_bundle(await compile_bundle(_version(), resolver))


_BASE_INPUTS: dict[str, Any] = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}


# --- (a) wiring follows dependency order -----------------------------------------------


@pytest.mark.req("FR-212")
@pytest.mark.parametrize("ctx", [{"x": 3}, {"x": 3, "base": 7}])
async def test_a_misordered_algorithm_prices_as_its_topological_twin(
    ctx: dict[str, Any],
) -> None:
    """FD 9572 Evidence §2: `[in, B, A, out]` raised a NodeError with ctx {x: 3} and gave 57
    with ctx {x: 3, base: 7}. Its topological twin gives 350."""
    compiled = load_bundle(await _bundle([_IN, _B, _A, _OUT]))
    out = await compiled.decision.async_evaluate(ctx)
    assert out["result"]["premium"] == 350


@pytest.mark.req("FR-212")
async def test_a_clamp_listed_before_its_producer_still_binds() -> None:
    """FD 9572 Evidence §3, C1: the clamp listed before `s_office` was wired to the input and
    skipped the minimum premium (payable 1507). Topological: 5250."""
    compiled = await _score_fixture(move="s_clamp", before="s_office")
    ctx = _ctx(inputs={**_BASE_INPUTS, "min_premium_minor": 5000})
    result = await score_one(compiled, ctx)
    assert result.outputs["payable_premium_minor"] == 5250
    rungs = {rung.rung: rung.value_minor for rung in result.premium_ladder}
    assert rungs["constraints"] == 5000


# --- (c) WITHDRAWN 2026-10-05 by the Delta (PL 9560's): do not add the tests in this block ---


@pytest.mark.req("FR-213")
@pytest.mark.parametrize("misordered", [False, True])
async def test_a_quote_input_naming_a_produced_value_is_refused(misordered: bool) -> None:
    """FD 9572 Evidence §3, E0 and E2: `office_premium_minor` sent as an input was ignored on
    the ordered list (payable 1507) and set the price on the misordered one (payable 1050).
    Either way the key is refused, by name (DP-1 (a), DP-2 (a))."""
    compiled = await (
        _score_fixture(move="s_instalment", before="s_office") if misordered
        else _score_fixture()
    )
    ctx = _ctx(inputs={**_BASE_INPUTS, "office_premium_minor": 1000})
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION.*'office_premium_minor'"):
        await score_one(compiled, ctx)


@pytest.mark.req("FR-213")
async def test_a_quote_input_naming_a_produced_value_is_refused_in_a_batch() -> None:
    """The same refusal on `_score_context_sync`, through `score_batch`. The row's shape is
    `test_quote_input_raise_sites.py`'s `_row` (`:221-228`): the reserved columns, then the
    inputs."""
    compiled = await _score_fixture()
    inputs = {**_BASE_INPUTS, "office_premium_minor": 1000}
    ref = _ctx(inputs=inputs).options
    assert ref is not None and ref.rating_version_ref is not None
    row = {"quote_id": "Q1", "purpose": "new_business", "effective_date": "2026-09-01",
           "rating_version_ref": str(ref.rating_version_ref), **inputs}
    out = score_batch(compiled, pl.DataFrame([row]).lazy()).collect().to_dicts()[0]
    assert out["outcome"] == "error"
    assert out["error_code"] == "INPUT_CONTRACT_VIOLATION", out
    assert "'office_premium_minor'" in out["error_message"]


# --- pins: an ordered list wires exactly as before --------------------------------------


@pytest.mark.req("FR-212")
async def test_a_topologically_listed_algorithm_wires_exactly_as_listed() -> None:
    """The tie-break is list position. `[in, A, B, D, out, out_fee]` is topological; a FIFO
    Kahn would emit D before B (both ready after A), a heap on list position does not."""
    bundle = await _bundle([_IN, _A, _B, _D, _OUT, _OUT_FEE])
    wire = to_wire(bundle.graph, bundle.resolved_payloads)
    interior = [n["id"] for n in wire["nodes"] if n["id"] in {"s_a", "s_b", "s_d"}]
    assert interior == ["s_a", "s_b", "s_d"]
    bundle_ab = await _bundle([_IN, _A, _B, _OUT])
    edges = [(e["sourceId"], e["targetId"])
             for e in to_wire(bundle_ab.graph, bundle_ab.resolved_payloads)["edges"]]
    assert edges == [("input", "s_a"), ("s_a", "s_b"), ("s_b", "__exact_reads"),
                     ("__exact_reads", "output")]


#: Recorded at the slice's base commit in Task 1 Step 2, before any code change.
_SCORE_FIXTURE_HASH = "<the 64-hex value Task 1 Step 2 prints>"


@pytest.mark.req("FR-212")
async def test_the_bundle_hash_is_unchanged() -> None:
    """The ruling: "a test asserts the hash of a topologically listed algorithm is unchanged"."""
    resolver = _FakeResolver()
    bundle = await compile_bundle(_version(), resolver)
    assert bundle.content_hash == _SCORE_FIXTURE_HASH
```

  - The batch test's row mirrors `test_quote_input_raise_sites.py`'s `_row` and its reads of
    `outcome`, `error_code` and `error_message` (`:250-254`). If that helper has moved, mirror
    the shipped one, not this sample.
  - **Not measured by FD 9572:** the topologically ordered algorithm with ctx
    `{x: 3, base: 7}`. The ruling asserts it "still gives 350, never 57". If Task 2 Step 4
    shows `…_topological_twin[ctx1]` giving anything but 350, STOP and report it: the
    shadowing would then sit in the engine's merge of a node's output over its received
    context, not in the wiring, and (a) alone would not close it.
  - The edge literal in `test_a_topologically_listed_algorithm_wires_exactly_as_listed` is
    FD 9572's verbatim output for the topological run. If it differs at the base commit, STOP:
    the essay's premise moved, and the lead hears it before any code changes.

- [ ] **Step 1c: (Withdrawn 2026-10-05 by the Delta: PL 9560's; do not add.)** The four per-path reds (the 17:15:09 entry). Each is appended to the
  module that already holds that path's fixtures; none edits an existing test. The algorithm
  is `_minimal_algorithm` (`backend/tests/test_rating_version_compile.py:50`): its `s_expr`
  produces `payable`, and its one declared input is `premium_in`. Its list is topological, so
  these four are reds for (c) alone. Before relying on a sample, check each fixture and
  helper name against the shipped module (`docs/plans/README.md` convention 1): `compiled_version`,
  `scoring_headers`, `_quote`, `SCORED_REF`, `SCORE_URL`, `_rows_for`, `_trace_produce_jobs`,
  `_set_trace_sample_rate`, `execute_job` (`test_score.py`); `two_versions`, `reader_headers`,
  `_body`, `COMPARE_URL` (`test_score_compare.py`); `_compiled_version`, `_scoring_frame`,
  `_dataset_version`, `_parameters`, `_run_handler`, `_summary` (`test_scoring_handlers.py`).
  Add any missing import (`sqlalchemy.update`, `JobStatus`, `ScoringTraceRow`) the way the
  module's neighbours import it.

  In `backend/tests/test_score.py`:

```python
@pytest.mark.req("FR-213")
def test_a_quote_input_naming_a_produced_value_is_refused_on_score(
    client: TestClient, scoring_headers: dict[str, str], compiled_version: Any
) -> None:
    """FD 9572 (c), `/score` (`api/score.py:350-375`): `s_expr` produces `payable`, so an
    input named `payable` is refused, by name, and never relayed to the engine."""
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
    """FD 9572 (c), trace reproduction (`trace_handlers.py:98`). After the fix `/score`
    refuses such a context before any trace is pended, so the case is a row pended before
    the fix: a served quote's pending context with `payable` planted in its inputs."""
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

  The trace assert states the behaviour this plan expects: the Job fails on the refusal and
  completes nothing. The ruling does not fix the handler's response to a refusal. If the shipped
  `execute_job` records the failure differently, mirror the shipped form and record it in the
  ledger. What must hold is that no completed trace carries a price built on the planted key.
  Also read the failed Job's recorded error the way `test_score.py`'s neighbours read a Job
  row, and assert it carries `INPUT_CONTRACT_VIOLATION`.

  In `backend/tests/test_score_compare.py`:

```python
@pytest.mark.req("FR-213")
def test_a_context_input_naming_a_produced_value_is_a_422_on_compare(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    """FD 9572 (c), `/score/compare` (`api/score.py:447`)."""
    body = _body()
    body["context"]["inputs"]["payable"] = 1
    response = client.post(COMPARE_URL, json=body, headers=reader_headers)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'payable'" in response.json()["detail"]
```

  Check that both of `two_versions`' algorithms still produce `payable` (`_with_adjustment`
  keeps `s_expr`). If one does not, plant a name that both produce, and say which in the ledger.

  In `backend/tests/test_scoring_handlers.py`:

```python
@pytest.mark.req("FR-213")
async def test_a_dataset_column_named_like_a_produced_value_is_refused_per_row(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    """FD 9572 (c), batch (`scoring_handlers` → `_score_context_sync`): every dataset column
    but the reserved four becomes `ctx.inputs`, so a column named `payable` is refused on
    every row. Per-row isolation (FR-255) keeps the Job itself running."""
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

  These need the database stack. Run each one alone. If the stack is down, record that and do
  not substitute a mock: the path is the thing under test.

- [ ] **Step 2: Record the hash, then run the module at the base commit and read each
  failure's cause.**

```bash
OMP_NUM_THREADS=1 nice uv run python -c "
import asyncio, sys; sys.path.insert(0, 'packages/pricing-core/tests')
import test_rating_score as T
from pricing_core.rating.compile import compile_bundle
print(asyncio.run(compile_bundle(T._version(), T._FakeResolver())).content_hash)"
```

  Run it twice. If the two values differ, STOP: the hash is not deterministic over this
  fixture and the hash assert is a plan defect. Otherwise paste the value into
  `_SCORE_FIXTURE_HASH`, then:

```bash
OMP_NUM_THREADS=1 nice uv run pytest packages/pricing-core/tests/test_rating_wire_order.py -q
```

  Expected, by cause (a matching FAIL with a different reason is a plan defect, reported):

  | Test | At the base commit | The cause that must show |
  |---|---|---|
  | `…_prices_as_its_topological_twin[ctx0]` | FAIL | `RuntimeError` from the engine: `NodeError` on `s_b`, "base + 50" |
  | `…_prices_as_its_topological_twin[ctx1]` | FAIL | `assert 57 == 350` |
  | `…_clamp_listed_before_its_producer_still_binds` | FAIL | `assert 1507 == 5250` |
  | `…_naming_a_produced_value_is_refused[False]` and `[True]` | FAIL | `DID NOT RAISE` |
  | `…_is_refused_in_a_batch` | FAIL | `assert 'quoted' == 'error'` |
  | `…_wires_exactly_as_listed` | PASS | — (a pin; Task 2 Step 5 proves it can fail) |
  | `…_bundle_hash_is_unchanged` | PASS | — (a pin; Task 2 Step 5 proves it can fail) |
  | `…_refused_on_score` (backend) | FAIL | `assert 200 == 422` |
  | `…_not_reproduced_as_a_price` (backend) | FAIL | `JobStatus.SUCCEEDED is JobStatus.FAILED` |
  | `…_is_a_422_on_compare` (backend) | FAIL | `assert 200 == 422` |
  | `…_refused_per_row` (backend) | FAIL | `assert {} == {'INPUT_CONTRACT_VIOLATION': 4}`, every row quoted |

  Run the four backend reds one file at a time:
  `OMP_NUM_THREADS=1 nice uv run pytest backend/tests/<file>::<test> -q`.

  Record the run's tail verbatim in the ledger, with the commit.

- [ ] **Step 3: Commit.**

```bash
git add packages/pricing-core/tests/test_rating_wire_order.py backend/tests/test_score.py \
  backend/tests/test_score_compare.py backend/tests/test_scoring_handlers.py
git commit -m "test(rating): FD 9572 reds — wiring by list order, a clamp bypassed, a shadowing input"
```

### Task 2: `to_wire` iterates a stable topological order

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/runtime.py` (imports `:37-51`; a new
  helper above `to_wire`; `to_wire` `:453-499`)

**Interfaces:**
- Consumes: `JdmGraph.nodes` (`step_id` → node dict with `produces`/`consumes`), `_as_list`
  (`runtime.py:137`), `GraphCycleError` (`model_schema.graph_errors`).
- Produces: `_dependency_order(graph: JdmGraph, interior_ids: Sequence[str]) -> list[str]`,
  private to `runtime.py`.

- [ ] **Step 1: Add the imports.** `import heapq` beside `import json`; and
  `from model_schema.graph_errors import GraphCycleError` beside the `model_schema.rating`
  import. Check the class name at `packages/model-schema/src/model_schema/graph_errors.py:11`.

- [ ] **Step 2: Add the helper, directly above `to_wire`.**

```python
def _dependency_order(graph: JdmGraph, interior_ids: Sequence[str]) -> list[str]:
    """The interior steps in a stable topological order (FR-212, FD 9572).

    A Rating Algorithm is a DAG, so the order its steps are listed in carries no meaning and
    must never decide wiring. The dependency rule is `RatingAlgorithm._graph_invariants`'s: a
    step depends on every other producer of each name it consumes, never on itself (the clamp
    that consumes and re-produces a name). Kahn's algorithm, always taking the ready step
    listed first: an already-ordered list comes back unchanged, so its wire is unchanged.
    """
    position = {step_id: i for i, step_id in enumerate(interior_ids)}
    producers: dict[str, list[str]] = {}
    for step_id in interior_ids:
        for name in _as_list(graph.nodes[step_id]["produces"]):
            producers.setdefault(str(name), []).append(step_id)
    dependents: dict[str, list[str]] = {step_id: [] for step_id in interior_ids}
    pending: dict[str, int] = {}
    for step_id in interior_ids:
        needs = {
            producer
            for name in _as_list(graph.nodes[step_id]["consumes"])
            for producer in producers.get(str(name), ())
            if producer != step_id
        }
        pending[step_id] = len(needs)
        for producer in needs:
            dependents[producer].append(step_id)
    ready = [position[step_id] for step_id in interior_ids if pending[step_id] == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        step_id = interior_ids[heapq.heappop(ready)]
        order.append(step_id)
        for other in dependents[step_id]:
            pending[other] -= 1
            if pending[other] == 0:
                heapq.heappush(ready, position[other])
    if len(order) != len(interior_ids):
        # Unreachable for a saved algorithm: `_graph_invariants` refused the cycle at save.
        raise GraphCycleError("the rating DAG contains a cycle (FR-212)")
    return order
```

- [ ] **Step 3: Iterate the order in `to_wire`.** Replace the assignment of `interior_ids`
  (`:453-455`) so the rest of the function reads it unchanged:

```python
    interior_ids = _dependency_order(
        graph,
        [step_id for step_id, node in graph.nodes.items() if node["type"] in _ENGINE_NODE_TYPE],
    )
```

  Amend the comment at `:463-473` with one sentence after its first: "It is built over
  `_dependency_order`'s topological order, never the list order (FD 9572): a producer listed
  after its consumer is still seen first." Leave the loop's body as it is: the incremental
  `produced_by` is what keeps the clamp-in-place edge off itself, and it is correct once the
  order is.

- [ ] **Step 4: Run the module.** `OMP_NUM_THREADS=1 nice uv run pytest
  packages/pricing-core/tests/test_rating_wire_order.py -q`. Expected: the two
  `…_topological_twin` cases and the clamp case now PASS; the three refusal cases still FAIL
  with `DID NOT RAISE` (Task 3's); the three pins PASS.

- [ ] **Step 5: Prove the two pins can fail.** Each change is made, run, recorded in the
  ledger with its output, and reverted before the next; `git diff` is empty after.
  - Replace the heap with a FIFO (`collections.deque`, `popleft`/`append`). Expected:
    `test_a_topologically_listed_algorithm_wires_exactly_as_listed` FAILS with
    `['s_a', 's_d', 's_b'] == ['s_a', 's_b', 's_d']`.
  - Change `_SCORE_FIXTURE_HASH`'s last character. Expected: `test_the_bundle_hash_is_unchanged`
    FAILS naming both values. (The hash cannot be moved from `to_wire`, by construction; this
    proves only that the assert reads it.)

- [ ] **Step 6: Run the neighbours.** `OMP_NUM_THREADS=1 nice uv run pytest
  packages/pricing-core/tests/test_rating_runtime.py
  packages/pricing-core/tests/test_rating_score.py -q`. Expected: PASS, no assert edited.

- [ ] **Step 7: Commit.**

```bash
git add packages/pricing-core/src/pricing_core/rating/runtime.py
git commit -m "fix(rating): to_wire wires each consumed name over a stable topological order (FD 9572)"
```

### Task 2b: (R-b) — one ordered path to the sink (DP-R1 (i); added by Delta 2)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/runtime.py`:
  - `to_wire`: replace the per-name edges (`:461-492`) and the sink loop (`:494-499`);
  - `_model_call_handler`: its success return (`:581`) and `_model_call_failure` (`:94`) pass
    the context through;
  - the module docstring's wiring rules.
- Modify: `packages/pricing-core/tests/test_rating_wire_order.py` (append).

- [ ] **Step 1: The red, appended to `test_rating_wire_order.py`.** It is engine-level, so it
  holds whatever guard (c) does at the entry. A raw context key named like a produced value
  must not reach the result through a side branch.

```python
@pytest.mark.req("FR-212")
async def test_no_side_branch_carries_a_stale_copy_into_the_sink() -> None:
    """(R-b): the score fixture, correctly ordered, evaluated at the engine with a raw
    `instalment_loading_minor` (the auditor's (3f) name). Through the sink fan-in the last
    branch's stale copy won; on one ordered path the producer's value is the last write."""
    compiled = await _score_fixture()
    context = {"effective_date": "2026-09-01", "purpose": "new_business",
               **_BASE_INPUTS, "min_premium_minor": 5000, "instalment_loading_minor": 777}
    out = await compiled.decision.async_evaluate(context)
    assert out["result"]["instalment_loading_minor"] == 5250
```

  At the base commit it must FAIL with `assert 777 == 5250`. If it fails for another reason,
  or passes, STOP and report it: the cause trace's premise has then moved. If auditor-fanin's
  no-key case is still in this plan, append it too, with the price it measured as the
  base-commit failure.

- [ ] **Step 2: Pass the context through `model_call`.** In `_model_call_handler`, return
  `{"output": {**context, **{str(name): value for name in _as_list(step.produces)}}}`. Here
  `context` is the `$nodes`-free copy the handler already builds (`:541`). Do the same for
  `_model_call_failure`'s output. Then run `test_rating_runtime.py` and `test_rating_score.py`:
  they must pass with no assert edited.

- [ ] **Step 3: One ordered path.** In `to_wire`, after `interior_ids = _dependency_order(...)`,
  build the edges as a chain and delete the per-name edges and the sink loop:

```python
    previous = _INPUT_ID
    for step_id in interior_ids:
        edges.append(_edge(previous, step_id))
        previous = step_id
    # (the wire-node construction per step stays as it is)
    exact_names = exact_read_names(graph)
    if exact_names:
        wire_nodes.append(_exact_read_node(exact_names))
        edges.append(_edge(previous, _EXACT_ID))
        edges.append(_edge(_EXACT_ID, _OUTPUT_ID))
    else:
        edges.append(_edge(previous, _OUTPUT_ID))
```

  Keep the per-step `wire_nodes.append(...)` dispatch exactly as it is. Read the shipped loop
  before editing: the sample shows the edges only. Rewrite the docstring's wiring rules
  (`:428-432`) to say that the interior steps form one path in topological order, so no merge
  happens. Delete the comment that justified the incremental `produced_by`: with no per-name
  edges, `produced_by` has no reader and goes too.

- [ ] **Step 4: Run.** Run `test_rating_wire_order.py`: the new red passes and every Task 1
  test still passes. `[in, A, B, out]`'s edge literal is unchanged, because a linear algorithm
  is already one path. Then run `test_rating_runtime.py`, `test_rating_score.py` and
  `test_rating_ladder_exact.py` with no assert edited. **If any test asserts a specific edge
  set and now fails, STOP:** list it in the ledger and report it. Editing that assert is the
  maintainer's to approve with DP-R1, not the executor's.

- [ ] **Step 5: Commit:** `fix(rating): to_wire wires one ordered path, so no branch carries
  a stale copy into the sink (FD 9572 R-b)`.

### Task 3: A quote input never shadows a produced value

**Withdrawn 2026-10-05 by the Delta above: (c) is PL 9560's. The executor does not run this
task.** Its text stays as filed.

**Blocked until DP-1, DP-2, DP-3 and DP-4 are decided.** The code below is DP-1 (a), DP-2 (a)
and DP-3 (a). A different decision rewrites this task before it starts.

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py` (a new check after
  `_check_billing_surface`, `:425-433`; one call in `score_one`, `:906`; one in
  `_score_context_sync`, `:1064`)
- Modify: `packages/pricing-core/tests/test_quote_input_raise_sites.py` (`_INPUT_FREE`,
  `:62-79`)
- Modify (DP-4 (a) only): `docs/specs/03-rating-engine.md` (the FR-212 row `:81` and the
  FR-213 row `:82`, the adopted texts byte-for-byte)

**Interfaces:**
- Consumes: `RatingAlgorithm.steps`, `RatingAlgorithm.input_contract`, `_as_list`
  (`score.py:320`), `_raise_named` (`score.py:311`).
- Produces: `_check_no_shadowed_produced_names(algorithm: RatingAlgorithm, inputs:
  Mapping[str, Any]) -> None`.

- [ ] **Step 1: Add the check after `_check_billing_surface`.**

```python
def _check_no_shadowed_produced_names(
    algorithm: RatingAlgorithm, inputs: Mapping[str, Any]
) -> None:
    """FR-213 (FD 9572 (c)): a quote input never stands in for a value a step produces.
    `inputNode` relays the whole context, so a key named like a produced value reaches the
    engine. A declared input that a step re-produces in place (a clamp on an input) is a
    legitimate key and is not refused."""
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

  Check against the shipped `model_schema.rating` step classes before relying on the sample:
  that every step class has `type`, which classes carry `produces`, and whether
  `getattr(..., None) or []` is needed or `step.produces` is always present. Mirror
  `score.py`'s own reads of `step.produces` (`:456`, `:463`) rather than the sample.

- [ ] **Step 1b: Add the guard for DP-2 (a)'s subtraction to `test_rating_wire_order.py`.**
  A declared input that a constraint re-produces in place is not a shadow. It calls the check
  directly, so it imports inside the test (the name does not exist before this task):

```python
_CLAMP_X = {"step_id": "s_clamp_x", "type": "constraint", "label": "Cap x",
            "condition": "x <= 10", "on_violation": "clamp", "clamp_bounds": {"max": "10"},
            "reason_code": "X_CAPPED", "consumes": ["x"], "produces": ["x"]}


@pytest.mark.req("FR-213")
def test_a_declared_input_re_produced_in_place_is_not_a_shadow() -> None:
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.score import _check_no_shadowed_produced_names

    algorithm = RatingAlgorithm.model_validate(_algo([_IN, _CLAMP_X, _A, _B, _OUT]))
    _check_no_shadowed_produced_names(algorithm, {"x": 3})  # no raise
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION.*'base'"):
        _check_no_shadowed_produced_names(algorithm, {"x": 3, "base": 7})
```

  If `RatingAlgorithm.model_validate` refuses this algorithm, mirror the clamp shape of
  `test_rating_score.py`'s `s_clamp` (`_algorithm_payload`) and record the difference; do not
  weaken the assert.

- [ ] **Step 2: Call it on both paths**, immediately after `_check_billing_surface(ctx)` in
  `score_one` (`:906`) and in `_score_context_sync` (`:1064`):
  `_check_no_shadowed_produced_names(algorithm, ctx.inputs)`.

- [ ] **Step 3: Register the raise site.** Add to `_INPUT_FREE`:
  `("rating/score.py", "_check_no_shadowed_produced_names"): 1,  # names declared step outputs, never a value`.

- [ ] **Step 4: Apply T1 and T2 (DP-4 (a) only)**, byte-for-byte as the adopting ruling
  states them, each appended at the end of its row's last cell. Run
  `python3 scripts/audit-docs.py`: only check 31 may fail before the mint.

- [ ] **Step 5: Run.** `OMP_NUM_THREADS=1 nice uv run pytest
  packages/pricing-core/tests/test_rating_wire_order.py
  packages/pricing-core/tests/test_quote_input_raise_sites.py
  packages/pricing-core/tests/test_rating_score.py -q`, then the four backend reds of Task 1
  Step 1c one file at a time. Expected: all PASS. Then remove the
  call from `score_one` only, run `test_rating_wire_order.py`, and record that
  `…_is_refused[False]` and `[True]` FAIL with `DID NOT RAISE` while the batch case passes;
  restore it. The same for `_score_context_sync`, the batch case failing alone. `git diff`
  shows both calls after.

- [ ] **Step 6: Commit.**

```bash
git add packages/pricing-core/src/pricing_core/rating/score.py \
  packages/pricing-core/tests/test_quote_input_raise_sites.py \
  packages/pricing-core/tests/test_rating_wire_order.py docs/specs/03-rating-engine.md
git commit -m "fix(rating): refuse a quote input that names a produced value (FD 9572 (c))"
```

### Task 4: The gate and the ledger

**Files:**
- Create: the slice's `LG-` ledger under `docs/ledgers/` (working id from the lead; minted at
  the merge).

- [ ] **Step 1:** Before any full run, check `pgrep -af 'pytest|vitest|flock'` and the gate
  slot; take it only on the lead's word (one full gate at a time, RL 9620).
- [ ] **Step 2:** The gate-runner runs `CLAUDE.md` §11's both halves on the slice head. The
  ledger names the tree, the per-command exit codes, and the failing excerpt if any.
- [ ] **Step 3:** `uv run python scripts/req-coverage.py` shows FR-212 and FR-213 carrying the
  new tests.
- [ ] **Step 4:** The ledger records, verbatim: Task 1 Step 2's base-commit run (the four
  backend reds included), Task 2 Step 5's two broken-pin runs, Task 3 Step 5's two
  removed-call runs, the four backend reds passing at the head, and the gate table.
- [ ] **Step 5:** FD 9572's discharge line ("the fix PR merging with all three tests red first
  on the unfixed tree") is answered in the ledger by the commit of Task 1 Step 2's run.

## What this plan does not cover

- **The exposure scan** of stored algorithms for a misordered list (the 17:10:08 entry, item
  3) was an auditor's, read-only, separate from this slice. It found none misordered (the
  17:15:09 entry, quoted under "Sources").
- **Dislocation** (`analysis.py` `_score_pass`) is not changed: it selects declared inputs
  only (RL-1394; the 17:15:09 entry).
- **The interim approval guard** (item 4: no new Rating Version approved or deployed in
  `gipricing` unless its list order equals its topological order) is a manual check the team
  performs until this slice merges. This slice removes the need for it; it does not build it.
- **A save-time refusal** of a misordered list is excluded by ruling (b).
- **Undeclared keys in general, the stamped names and the engine-internal keys** stay with
  FD-1374 and PL 9776 unless DP-3 decides otherwise.
- **The WK-1250 S2 inliner's** use of the same order is that slice's plan (PL 9610, #1170).

## Self-review (2026-10-05)

- **Spec and ruling coverage.** (a): Task 2, reds in Task 1. (b): no task adds a save-time
  check; none may. (c): Task 3, behind DP-1..DP-4. The hash assert: Task 1, proven in Task 2
  Step 5. `to_jdm`: not edited, because it emits no edges (Verified facts). Each red the
  ruling lists is a named test with a cause.
- **Placeholders.** `_SCORE_FIXTURE_HASH` is recorded by a command at Task 1 Step 2: a
  measurement of the shipped tree, not a choice left open. One premise is unmeasured and
  carries a STOP (the ordered algorithm with ctx `{x: 3, base: 7}`, Task 1 Step 1).
- **Names.** `_dependency_order`, `_check_no_shadowed_produced_names` and
  `test_rating_wire_order.py`'s test names match across the tasks, the Acceptance Standard and
  the write set.
- **Literals checked at `4d3be141`:** `_FakeResolver`, `_version`, `_ctx` and
  `_RATING_VERSION_REF` (`test_rating_score.py:103`, `:118`, `:143`, `:43`); `GraphCycleError`
  (`graph_errors.py:11`); `_PER_QUOTE_CODES` (`api/score.py`); `_INPUT_FREE`
  (`test_quote_input_raise_sites.py:62`); the context sites (`score.py:910-912`,
  `:1066-1068`); `content_hash=bundle_hash(graph, pins)` (`compile.py:641`).
