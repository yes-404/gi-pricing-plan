---
id: RL-9573
family: ruling
title: WK-1250 Slice 3 decided — a purpose mount re-produces a parent name through FR-212's chain, never reaching the risk premium, and each purpose evaluates its own graph and algorithm
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1344, RL-1309, RL-1242, PL-1254, SL-1341, FR-212, FR-217, FR-218, FR-243, FR-248]
---

# RL 9573 (working id) — WK-1250 Slice 3: DP-S3-1 and DP-S3-2 decided

## How this was ruled

- **The decisions are not this record's.** They are the maintainer's, by delegation, in the
  entry headed *"2026-10-05 17:01:30 BST — Discrepancy CLOSED; PR triage accepted (4 closes, each
  after its absorber merges); A-3/A-4/S3 rulings; the to_wire defect: REPRODUCE NOW"* in
  `~/gi-pricing-plan.local/channel/to-lead.md`, its "WK-1250 S3 memo" line, verbatim:

  > WK-1250 S3 memo: DP-S3-1 option (d) (re-production via FR-212's chain rule, as the clamp does) with R1 (no route to risk_premium), one re-producer per name and author-placed X: ACCEPTED in principle for the RL draft, final at its ACK. DP-S3-2 (a) with the two conditions (a per-purpose algorithm and handler in CompiledBundle; C1 per purpose graph): ACCEPTED. S3 is not on G2's path, so its RL mints in the normal queue.

  **DP-S3-1 is accepted in principle and becomes final at this record's ACK.** DP-S3-2 is
  accepted.
- **The decision points** are PL 9609's (working id, #1173, branch `pl-9609-wk1250-s3-leaf` at
  `7c8736fd5c083fddf175d3a10a2e51b2cbcdc3d6`), §"Decision points", raised as `RL-1344` §3 requires
  (`RL-1344:180-181`). The memo the ruling names is
  `~/gi-pricing-plan.local/handover/dp-memo-wk1250-s3-2026-10-05.md` (a local file).
- **Written 2026-10-05 17:06 BST (by `date`)**, by the decision-maker session `dm-finals2`, on
  the lead's order. Every fact below was read at `origin/main`
  `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8`, by symbol with its line. PL 9609 and the Slice 2
  ruling RL 9586 (#1180) are unminted, so they are cited in working-id form and kept out of
  `relates:` (check 32).
- **This record rules a plan's decision points and never edits the plan** (`document-ids.md`
  §1.6, PL row). Its texts for PL 9609 (P1 to P5) are applied by the planner as a pre-mint edit.
- **Not ruled by this record:** the `to_wire` step-order question (`runtime.py` `to_wire` `:412`,
  `:461-492`). *(Dated clause, 2026-10-05 17:09 BST (by `date`), pre-mint, dm-finals2.)* It was
  reproduced as FD 9572 (working id) and its fix ruled by the maintainer, by delegation, in the
  entry headed *"2026-10-05 17:06:26 BST — FD 9572 (to_wire wires by LIST order): reproduced;
  severity waits on (1)/(2); the FIX RULED now; RL 9588 / RL 9586 noted"*, which also accepted
  RL 9586's P5 (*"The WK-1250 S2 inliner uses the same topological order (RL 9586's P5, the DM's
  proposal: ACCEPTED, as it is the same rule)"*). Limit 4 below cites that ruling.

## Locators — read at `137bc817`

| Fact | Where |
|---|---|
| FR-212 allows several producers of one name only as a re-production chain: each later producer consumes the name; the last in topological order is the effective one. *"This is what lets a `constraint` clamp a value in place"* | `packages/model-schema/src/model_schema/rating.py` `RatingAlgorithm._graph_invariants` `:395`, chain check `:445-459` |
| A step consuming a name depends on every producer of it except itself, so two re-producers of one name, or a step consuming `X` beside a different step re-producing `X`, form a cycle | same, `:424-426`; Kahn's algorithm `:428-440` |
| The engine honours re-production: `to_wire` wires a re-producer's incoming edge to the earlier producer, and a later node's `passThrough` output for a key survives (verified live, per the docstring) | `packages/pricing-core/src/pricing_core/rating/runtime.py` `to_wire` `:412`, `:461-492`; `_constraint_node` docstring `:291-301` |
| At save, a `GraphCycleError` maps to `RATING_GRAPH_CYCLIC`, a `GraphUnresolvedRefError` to `RATING_GRAPH_UNRESOLVED_REF`, any other `ValueError` to `VALIDATION_FAILED` | `backend/src/app/platform/rating_algorithms.py` `graph_validation_error` `:30-64` |
| The ladder is the fixed `RUNG_ORDER`, read from the declared outputs `f"{rung}_minor"`, first `risk_premium` | `pricing_core/rating/ladder.py` `RUNG_ORDER` `:52-63`, `rung_output_name` `:76` |
| `MoneyMinor` is a strict `int` with no sign bound | `packages/model-schema/src/model_schema/money.py` `MoneyMinor` `:69-73` |
| `build_scoring_result` reads `bundle.algorithm` for lookup misses, constraints, ladder inputs, outputs and the trace; `score_one`, `_score_context_sync` and the batch row path read `bundle.algorithm` / `bundle.decision` | `pricing_core/rating/score.py` `build_scoring_result` `:830`, `:844-859`; `score_one` `:895`, `:916`; `_score_context_sync` `:1061`, `:1070-1071`; batch `:1095` |
| `_model_call_handler` routes `model_call` nodes on one algorithm's `steps_by_id` | `runtime.py` `_model_call_handler` `:512-532` |
| `CompiledBundle` holds one `decision` and one `algorithm` | `runtime.py` `CompiledBundle` `:625-643` |
| `bundle_hash` hashes the canonical JSON of `{"graph", "pins"}` | `compile.py` `bundle_hash` `:522-535` |

## Ruled

**DP-S3-1 accepted in principle by the maintainer, by delegation, 2026-10-05 17:01:30 BST, final
at this record's ACK; DP-S3-2 accepted (quoted above).**

| DP | Ruling |
|---|---|
| **DP-S3-1** | **(d) re-production.** A purpose mount maps an input port and an output port to the **same** parent name `X`. In that purpose's graph the mount consumes the parent's `X` and re-produces `X`, as FR-212's re-production chain allows and as a clamping `constraint` already does. Every parent step downstream of `X` reads the re-produced value, so the ladder (FR-248) and the payable are the adjusted figures. Nothing is pruned. The base graph is the version without the mount (`RL-1344` acceptance 2) |
| **R1 — one risk price** | In a purpose graph, no step of a purpose mount may reach the `output` step whose `output_name` is `risk_premium_minor` (FR-218, *"One risk price"*). Refused at save with `VALIDATION_FAILED`, naming the mount and `risk_premium_minor`. Vacuous for an algorithm with no such output |
| **Limit 2 — one re-producer per name** | A mount may re-produce `X` only where the parent has no other re-producer of `X`. Inside the fragment, only the step producing the output port mapped to `X` consumes the input port mapped to `X`. Either violation is a cycle, refused at save by FR-212 as it stands with `RATING_GRAPH_CYCLIC` |
| **Limit 3 — author-placed `X`** | Where `X` sits is the author's choice. Every parent step downstream of `X` runs on the adjusted value; a minimum-premium clamp downstream of `X` clamps a refund. The mount and its `purposes` are in FR-219's diff (`RL-1344` acceptance 5) and in the trace |
| **Limit 4 — order** | The re-producing step is evaluated after the parent's producer of `X` and before every downstream consumer. It holds by the stable topological order the maintainer, by delegation, ruled at 2026-10-05 17:06:26 BST for `to_wire` and for the Slice 2 inliner (RL 9586's P5, ACCEPTED; FD 9572, working id): *"wires every consumed name to its PRODUCER by name through the graph, over a STABLE topological order computed from the dependency edges (Kahn with list order as the tie-break …)"*. A re-producer depends on the earlier producer of `X`, and every downstream consumer depends on the re-producer, so that order puts each where (d) needs it |
| **Codes (DP-S3-1)** | A step that runs for every purpose consuming a purpose-only name → `RATING_GRAPH_UNRESOLVED_REF` (PL 9609 acceptance 3; `RL-1344` acceptance 4). R1 → `VALIDATION_FAILED`. Limit 2 → `RATING_GRAPH_CYCLIC`. No new code |
| **DP-S3-2** | **(a) one graph per purpose that has a mount.** `Bundle` gains `purpose_graphs: dict[str, JdmGraph]`, holding only the purposes some mount selects, so it is empty for a version with no purpose mount. `bundle_hash` covers it only when it is non-empty, so every existing `content_hash` is unchanged. Scoring chooses the graph by `ctx.purpose` and falls back to the base graph |
| **DP-S3-2, condition 1** | `CompiledBundle` holds, per purpose graph, its **decision, algorithm and `model_call` handler**; boosters stay shared and keyed by ref. One selector returns the pair for `ctx.purpose`, and every read of `bundle.algorithm` or `bundle.decision` in the Locators' scoring rows goes through it. Red first: a cancellation mount containing a clamping `constraint` step, whose clamp appears in the cancellation quote's ladder |
| **DP-S3-2, condition 2** | RL 9586's C1 runs per purpose graph: `load_bundle` re-inlines with the purpose for each key of `purpose_graphs` and refuses with `BUNDLE_COMPILE_FAILED` when that graph's node ids differ from the re-inlined algorithm's `step_id`s |

## The spec texts

**T1 to T3 do not land in this PR.** They describe behaviour, so they land in one commit with
the code (`CLAUDE.md` §2), applied by WK-1250 Slice 3 (`SL-1341`) in its Task 1. T1's and T3's
find strings have exactly one hit at `137bc817`. T2's find string is written by RL 9586's T1,
so it has one hit at Slice 2's merge tree and none at `137bc817`.

### T1 — `03` §4.1, the invariants. Find `` and unreferenced by an `output` (FR-212). `` and insert after that paragraph (after any text Slice 2 appended there), as a new paragraph

```markdown
*(Added <date>, WK-1250 Slice 3, RL 9573 (working id); `RL-1344` §3.)* **Per purpose.** FR-212 holds for each purpose's graph: the algorithm with its unconditional mounts, and the algorithm with the mounts selected for `mid_term_adjustment`, and for `cancellation`. A step that runs for every purpose cannot consume a name only a purpose mount produces (`RATING_GRAPH_UNRESOLVED_REF`). **A purpose mount re-produces a parent name.** It maps an input port and an output port to the same parent name, and in that purpose's graph it consumes the parent's value and re-produces it, as a clamping `constraint` re-produces its value; every step downstream reads the adjusted value, so the premium ladder and the payable of an MTA or cancellation are the adjusted figures. Its steps never reach the `risk_premium_minor` output: one risk price (FR-218; `VALIDATION_FAILED`). A name has at most one re-producer, and inside the fragment only the step producing the re-produced name consumes it (otherwise `RATING_GRAPH_CYCLIC`). Where the mount re-produces is the author's choice: a step downstream of it, a minimum-premium clamp included, runs on the adjusted value.
```

### T2 — `03` §4.1, the example's purpose mount. Find `` "inputs": {"ncd_years": "ncd_years"}, "outputs": {"ncd_factor": "ncd_factor"}}] `` (written by RL 9586's T1) and replace it with

```json
"inputs": {"ncd_years": "ncd_years"}, "outputs": {"ncd_factor": "ncd_factor"}},
                 {"ref": "sub_graph:motor-cancellation@1", "mount_point": "s_cancel",
                  "purposes": ["cancellation"],
                  "inputs": {"annual_payable": "payable_premium_pre_round", "days_on_risk": "days_on_risk"},
                  "outputs": {"refund_payable": "payable_premium_pre_round"}}]
```

Like the rest of the example, it shows the shape, not a complete FR-212 graph:
`payable_premium_pre_round` and `days_on_risk` have no producer in the example as it stands, and
`sub_graph:motor-cancellation@1` is illustrative. The mount re-produces
`payable_premium_pre_round`, which sits below the minimum-premium clamp, so the refund is not
clamped (Limit 3).

### T3 — `03` §5.2, the bundle per purpose. Find `` def load_bundle(bundle: Bundle) -> CompiledBundle     # FR-243's hydration step `` and insert after that line

```python
# Bundle.purpose_graphs: dict[str, JdmGraph]          # one graph per purpose a mount selects; empty
#                                                       # otherwise, and hashed only when non-empty
#                                                       # (RL 9573, DP-S3-2 (a))
# CompiledBundle: per purpose graph, its decision, algorithm and model_call handler; load_bundle's
#                 node-id check (RL 9586 C1) runs per purpose graph   # added <date>, WK-1250 Slice 3
```

## The texts for PL 9609 (applied by the planner, pre-mint)

Each find string has exactly one hit in PL 9609 at `7c8736fd`.

- **P1 — acceptance 3, the code.** Find `` naming the step and the purpose, with the code DP-S3-1's ruling names. `` and replace it with
  `` naming the step and the purpose, with `RATING_GRAPH_UNRESOLVED_REF` (RL 9573). Also red first (RL 9573, DP-S3-1 (d)): a purpose mount whose steps reach the `risk_premium_minor` output is refused with `VALIDATION_FAILED` (R1); a second re-producer of a name already re-produced is refused with `RATING_GRAPH_CYCLIC` (Limit 2). ``
- **P2 — Task 2, Step 1, the cases.** Find `` consuming a purpose-only name; DP-S3-1's override cases. `` and replace it with
  `` consuming a purpose-only name; DP-S3-1's re-production cases (RL 9573): a mount re-producing a parent name is accepted per purpose graph; R1's route to `risk_premium_minor` is refused; a second re-producer and a fragment step consuming `X` beside the re-producer are each refused as a cycle. ``
- **P3 — Task 3, Step 1, the inliner case.** Find `` adds the cancellation mounts and applies DP-S3-1's override; `` and replace it with
  `` adds the cancellation mounts, whose re-producing step reads the parent's value and re-produces it (RL 9573, DP-S3-1 (d)); ``
- **P4 — Task 3, Steps 1 and 3, the per-purpose load.** Find `` - `load_bundle` gives one decision per purpose graph. `` and replace it with
  `` - `load_bundle` gives one decision, algorithm and `model_call` handler per purpose graph, and refuses with `BUNDLE_COMPILE_FAILED` when a purpose graph's node ids differ from its re-inlined algorithm's (RL 9573, DP-S3-2 conditions 1 and 2). ``
  Then find `` - `bundle_hash` covers `purpose_graphs` only when it is non-empty. `` and insert after it
  `` - `CompiledBundle` holds the per-purpose decision, algorithm and handler; boosters stay shared (RL 9573, condition 1). ``
- **P5 — Task 4, Step 3, the selector.** Find `` The trace is built from the algorithm that was evaluated. `` and replace it with
  `` One selector returns the purpose's decision and algorithm, and every read of `bundle.algorithm` or `bundle.decision` in `build_scoring_result`, `score_one`, `_score_context_sync` and the batch row path goes through it: lookup misses, constraints, ladder inputs, outputs and the trace all use the algorithm that was evaluated (RL 9573, condition 1). Red first: a clamping `constraint` inside a cancellation mount appears in the cancellation quote's ladder. ``

## What it obliges

- **PL 9609's planner** applies P1 to P5 as a pre-mint edit to #1173. The plan's DP-S3-1 and
  DP-S3-2 rows then cite this record. Activation need 2 is met at this record's mint, with
  DP-S3-1 final only if the ACK accepts it.
- **WK-1250 Slice 3 (`SL-1341`)** applies T1 to T3 verbatim in its Task 1 spec commit, with its
  code (`CLAUDE.md` §2). It also strikes FR-218's `RL-1242` clause, and sets `RL-1242` `retired`
  in its final commit, as the maintainer accepted on 2026-10-05 at 16:43:57 BST. That is the plan's
  acceptance 9, and is not changed by this record.

## Acceptance — the violation that must become detectable

Each is red first in Slice 3:
1. *An MTA or cancellation quote is priced at the annual payable.* A cancellation mount that
   re-produces `payable_premium_pre_round` changes `payable_premium_minor` on a cancellation
   quote and leaves a `new_business` quote's unchanged.
2. *A purpose mount changes the risk price.* A mount whose steps reach `risk_premium_minor` is
   refused at save with `VALIDATION_FAILED` (R1).
3. *A purpose mount's `model_call` or clamp is evaluated against the base algorithm.* The
   condition-1 test: a clamp inside a cancellation mount appears in the cancellation ladder.
4. *A purpose graph and its re-inlined algorithm disagree at load.* Condition 2's test expects
   `BUNDLE_COMPILE_FAILED`.
