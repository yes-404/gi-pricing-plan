---
id: RL-1628
family: ruling
title: WK-1250 Slice 3 decided — a purpose mount re-produces a parent name through FR-212's chain, never reaching the risk premium, and each purpose evaluates its own graph and algorithm
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-11            # original date 2026-10-05, set at the draft; minted 2026-10-11
owner: decision-maker
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-1344, RL-1309, RL-1242, RL-1571, RL-1519, FD-1425, SL-1436, PL-1254, SL-1341, FR-212, FR-217, FR-218, FR-243, FR-248]
---

# RL-1628 — WK-1250 Slice 3: DP-S3-1 and DP-S3-2 decided

## How this was ruled

- **The decisions are not this record's.** They are the maintainer's, by delegation, in the
  entry headed *"2026-10-05 17:01:30 BST — Discrepancy CLOSED; PR triage accepted (4 closes, each
  after its absorber merges); A-3/A-4/S3 rulings; the to_wire defect: REPRODUCE NOW"* in
  `~/gi-pricing-plan.local/channel/to-lead.md`, its "WK-1250 S3 memo" line, verbatim:

  > WK-1250 S3 memo: DP-S3-1 option (d) (re-production via FR-212's chain rule, as the clamp does) with R1 (no route to risk_premium), one re-producer per name and author-placed X: ACCEPTED in principle for the RL draft, final at its ACK. DP-S3-2 (a) with the two conditions (a per-purpose algorithm and handler in CompiledBundle; C1 per purpose graph): ACCEPTED. S3 is not on G2's path, so its RL mints in the normal queue.

  **DP-S3-1 is accepted in principle and becomes final at this record's ACK.** DP-S3-2 is
  accepted.
- **The decision points** are PL-1629's (minted in the same D12 batch; #1173, branch `pl-9609-wk1250-s3-leaf` at
  `7c8736fd5c083fddf175d3a10a2e51b2cbcdc3d6`), §"Decision points", raised as `RL-1344` §3 requires
  (`RL-1344:180-181`). The memo the ruling names is
  `~/gi-pricing-plan.local/handover/dp-memo-wk1250-s3-2026-10-05.md` (a local file).
- **Written 2026-10-05 17:06 BST (by `date`)**, by the decision-maker session `dm-finals2`, on
  the lead's order. Every fact was first read at `origin/main`
  `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8`, by symbol with its line. **Every locator below is
  re-read at `d699a561d6a93f33b74beb9c07023f8e655bb8c7`** (§"Pre-mint refresh, 2026-10-11"). PL
  9609 was unminted when this refresh was written, and is now PL-1629 (minted in this batch, after this record). The
  Slice 2 ruling RL 9586 (#1180) was minted as `RL-1571` (D5, 2026-10-10) and is cited so.
- **This record rules a plan's decision points and never edits the plan** (`document-ids.md`
  §1.6, PL row). Its texts for PL-1629 (P1 to P5) are applied by the planner as a pre-mint edit.
- **Not ruled by this record:** the `to_wire` step-order question (`runtime.py` `to_wire` `:412`,
  `:461-492`). *(Dated clause, 2026-10-05 17:09 BST (by `date`), pre-mint, dm-finals2.)* It was
  reproduced as FD 9572 (working id; minted `FD-1425`, `closed`) and its fix ruled by the maintainer, by delegation, in the
  entry headed *"2026-10-05 17:06:26 BST — FD 9572 (to_wire wires by LIST order): reproduced;
  severity waits on (1)/(2); the FIX RULED now; RL 9588 / RL 9586 noted"*, which also accepted
  RL 9586's P5 (*"The WK-1250 S2 inliner uses the same topological order (RL 9586's P5, the DM's
  proposal: ACCEPTED, as it is the same rule)"*). Limit 4 below cites that ruling, and the code
  that now delivers it (`SL-1436`, `closed` 2026-10-06; `RL-1571` for the inliner).

## Locators — read at `d699a561` (refreshed 2026-10-11; first read at `137bc817`)

| Fact | Where |
|---|---|
| FR-212 allows several producers of one name only as a re-production chain: each later producer consumes the name; the last in topological order is the effective one. *"This is what lets a `constraint` clamp a value in place"* | `packages/model-schema/src/model_schema/rating.py` `graph_invariant_issues` `:616`, chain check `:733-755` (an unchained second producer is `VALIDATION_FAILED`); `RatingAlgorithm._graph_invariants` `:564` raises from it |
| A step consuming a name depends on every producer of it except itself, so two re-producers of one name, or a step consuming `X` beside a different step re-producing `X`, form a cycle | same, dependencies `:676-694` (self-edge excluded `:693`); Kahn's algorithm `:696-708`; `RATING_GRAPH_CYCLIC` `:709-728` |
| The engine honours re-production: `to_wire` lays every interior step on **one path in `_dependency_order`'s stable topological order, never the list order** (FD-1425, fixed by `SL-1436`), so a name's final producer writes it after every earlier copy, and a later node's `passThrough` output for a key survives (verified live, per the docstrings) | `packages/pricing-core/src/pricing_core/rating/runtime.py` `_dependency_order` `:458`; `to_wire` `:500`, docstring `:513-521`; `_constraint_node` `:327`, docstring `:339-342` |
| The Slice 2 inliner orders a mounted fragment's steps by the same rule | `packages/pricing-core/src/pricing_core/rating/inline.py` `_stable_topological` `:161`; `inline_mounts` `:229` (`RL-1571` P5) |
| At save, a `GraphCycleError` maps to `RATING_GRAPH_CYCLIC`, a `GraphUnresolvedRefError` to `RATING_GRAPH_UNRESOLVED_REF`, any other `ValueError` to `VALIDATION_FAILED` | `backend/src/app/platform/rating_algorithms.py` `graph_validation_error` `:54`, mapping `:68-83` |
| The ladder is the fixed `RUNG_ORDER`, read from the declared outputs `f"{rung}_minor"`, first `risk_premium` | `pricing_core/rating/ladder.py` `RUNG_ORDER` `:52-63`, `rung_output_name` `:76` (unchanged since `137bc817`) |
| `MoneyMinor` is a strict `int` with no sign bound | `packages/model-schema/src/model_schema/money.py` `MoneyMinor` `:69-73` (unchanged) |
| `build_scoring_result` reads `bundle.algorithm` for lookup misses, constraints, ladder inputs, outputs and the trace; `score_one`, `_score_context_sync` and the batch row path read `bundle.algorithm` / `bundle.decision` | `pricing_core/rating/score.py` `build_scoring_result` `:873`, `:887-902`; `score_one` `:919`, `:938`, `:961`; `_score_context_sync` `:1090`, `:1106`, `:1117-1118`; batch `_score_batch_row` `:1128`, `:1142` |
| `_check_purpose_mount` (`RL-1242`'s interim refusal) and its two call sites | `score.py` `:391`; calls `:941` (`score_one`), `:1108` (`_score_context_sync`) |
| `_model_call_handler` routes `model_call` nodes on one algorithm's `steps_by_id` | `runtime.py` `_model_call_handler` `:712`, `steps_by_id` `:739-746` |
| `CompiledBundle` holds one `decision` and one `algorithm` | `runtime.py` `CompiledBundle` `:941`, fields `:956-959` |
| C1, `RL-1571` DP-S2-1: at load, the stored graph's node ids must equal the re-inlined algorithm's step ids, else `BUNDLE_COMPILE_FAILED` | `runtime.py` `_check_graph_matches_inlined_algorithm` `:962`, called by `load_bundle` `:974` at `:1001` |
| `bundle_hash` hashes the canonical JSON of `{"graph", "pins"}`, and omits `pins.sub_graphs` when it is empty so every earlier `content_hash` is unchanged (the Slice 2 precedent DP-S3-2's hash rule follows) | `compile.py` `Bundle` `:632` (`graph` `:642`, `pins` `:644`); `bundle_hash` `:661`, the omission `:670` |
| `SubGraphRef` has `ref`, `mount_point`, `inputs`, `outputs`, and **no `purposes`**; `RatingAlgorithm.sub_graphs` lists them | `model_schema/rating.py` `SubGraphRef` `:444` (fields `:456-459`); `sub_graphs` `:540` |

## Ruled

**DP-S3-1 accepted in principle by the maintainer, by delegation, 2026-10-05 17:01:30 BST, final
at this record's ACK; DP-S3-2 accepted (quoted above).**

| DP | Ruling |
|---|---|
| **DP-S3-1** | **(d) re-production.** A purpose mount maps an input port and an output port to the **same** parent name `X`. In that purpose's graph the mount consumes the parent's `X` and re-produces `X`, as FR-212's re-production chain allows and as a clamping `constraint` already does. Every parent step downstream of `X` reads the re-produced value, so the ladder (FR-248) and the payable are the adjusted figures. Nothing is pruned. The base graph is the version without the mount (`RL-1344` acceptance 2) |
| **R1 — one risk price** | In a purpose graph, no step of a purpose mount may reach the `output` step whose `output_name` is `risk_premium_minor` (FR-218, *"One risk price"*). Refused at save with `VALIDATION_FAILED`, naming the mount and `risk_premium_minor`. Vacuous for an algorithm with no such output |
| **Limit 2 — one re-producer per name** | A mount may re-produce `X` only where the parent has no other re-producer of `X`. Inside the fragment, only the step producing the output port mapped to `X` consumes the input port mapped to `X`. Either violation is a cycle, refused at save by FR-212 as it stands with `RATING_GRAPH_CYCLIC` |
| **Limit 3 — author-placed `X`** | Where `X` sits is the author's choice. Every parent step downstream of `X` runs on the adjusted value; a minimum-premium clamp downstream of `X` clamps a refund. The mount and its `purposes` are in FR-219's diff (`RL-1344` acceptance 5) and in the trace |
| **Limit 4 — order** | The re-producing step is evaluated after the parent's producer of `X` and before every downstream consumer. It holds by the stable topological order the maintainer, by delegation, ruled at 2026-10-05 17:06:26 BST for `to_wire` and for the Slice 2 inliner (RL 9586's P5, ACCEPTED; FD 9572, working id): *"wires every consumed name to its PRODUCER by name through the graph, over a STABLE topological order computed from the dependency edges (Kahn with list order as the tie-break …)"*. **That order is now delivered**: `to_wire` lays the interior steps on one path in `_dependency_order`'s order (`runtime.py` `:458`, `:500`; FD-1425, fixed by `SL-1436`, `closed` 2026-10-06), and the inliner uses `_stable_topological` (`inline.py` `:161`; `RL-1571` P5). A re-producer depends on the earlier producer of `X`, and every downstream consumer depends on the re-producer, so that order puts each where (d) needs it. Slice 3 adds no ordering code; its red-first test 1 (Acceptance below) shows the order holds for a purpose graph |
| **Codes (DP-S3-1)** | A step that runs for every purpose consuming a purpose-only name → `RATING_GRAPH_UNRESOLVED_REF` (PL-1629 acceptance 3; `RL-1344` acceptance 4). R1 → `VALIDATION_FAILED`. Limit 2 → `RATING_GRAPH_CYCLIC`. No new code |
| **DP-S3-2** | **(a) one graph per purpose that has a mount.** `Bundle` gains `purpose_graphs: dict[str, JdmGraph]`, holding only the purposes some mount selects, so it is empty for a version with no purpose mount. `bundle_hash` covers it only when it is non-empty, so every existing `content_hash` is unchanged. Scoring chooses the graph by `ctx.purpose` and falls back to the base graph |
| **DP-S3-2, condition 1** | `CompiledBundle` holds, per purpose graph, its **decision, algorithm and `model_call` handler**; boosters stay shared and keyed by ref. One selector returns the pair for `ctx.purpose`, and every read of `bundle.algorithm` or `bundle.decision` in the Locators' scoring rows goes through it. Red first: a cancellation mount containing a clamping `constraint` step, whose clamp appears in the cancellation quote's ladder |
| **DP-S3-2, condition 2** | `RL-1571`'s C1 (DP-S2-1; `runtime.py` `_check_graph_matches_inlined_algorithm` `:962`) runs per purpose graph: `load_bundle` re-inlines with the purpose for each key of `purpose_graphs` and refuses with `BUNDLE_COMPILE_FAILED` when that graph's node ids differ from the re-inlined algorithm's `step_id`s |

## The spec texts

**T1 to T3 do not land in this PR.** They describe behaviour, so they land in one commit with
the code (`CLAUDE.md` §2), applied by WK-1250 Slice 3 (`SL-1341`) in its Task 1. **Counted at
`d699a561` (the refresh base):** T1's find string has exactly one hit (`03:340`) and its insertion
anchor exactly one (`03:349`); T2's insertion anchor has exactly one hit (`03:943`); T3's find
string has exactly one hit (`03:1154`). The executor re-counts at its own base and stops on any
count other than one.

### T1 — `03` §4.1, the invariants. The invariants paragraph contains `` and unreferenced by an `output` (FR-212). `` (`03:340`). Slice 2 appended the paragraph beginning `` *(Amended 2026-10-09, WK-1250 Slice 2, `RL-1309` DP-3 items 2 to 4: a mount is a node. `` (`03:349`). Insert after that Slice 2 paragraph, as a new paragraph

```markdown
*(Added <date>, WK-1250 Slice 3, RL-1628; `RL-1344` §3.)* **Per purpose.** FR-212 holds for each purpose's graph: the algorithm with its unconditional mounts, and the algorithm with the mounts selected for `mid_term_adjustment`, and for `cancellation`. A step that runs for every purpose cannot consume a name only a purpose mount produces (`RATING_GRAPH_UNRESOLVED_REF`). **A purpose mount re-produces a parent name.** It maps an input port and an output port to the same parent name, and in that purpose's graph it consumes the parent's value and re-produces it, as a clamping `constraint` re-produces its value; every step downstream reads the adjusted value, so the premium ladder and the payable of an MTA or cancellation are the adjusted figures. Its steps never reach the `risk_premium_minor` output: one risk price (FR-218; `VALIDATION_FAILED`). A name has at most one re-producer, and inside the fragment only the step producing the re-produced name consumes it (otherwise `RATING_GRAPH_CYCLIC`). Where the mount re-produces is the author's choice: a step downstream of it, a minimum-premium clamp included, runs on the adjusted value.
```

### T2 — `03` §4.11, a purpose mount's shape. Find `` revisit if an algorithm needs it *(ruled 2026-10-09, WK-1250 Slice 2)*. `` (the last sentence of the "Inlining and namespacing" bullet, `03:943`) and insert after that bullet, as a new bullet

```markdown
- **Purpose mounts** *(added <date>, WK-1250 Slice 3, RL-1628; DP-S3-1 (d))*. A mount's `purposes` selects the purposes it is inlined for; with none, it is unconditional. A purpose mount maps an input port and an output port to the **same** parent name, so in that purpose's graph it re-produces the name (§4.1). The shape, as an entry of `sub_graphs`:

  ```json
  {"ref": "sub_graph:motor-cancellation@1", "mount_point": "s_cancel",
   "purposes": ["cancellation"],
   "inputs": {"annual_payable": "payable_premium_pre_round", "days_on_risk": "days_on_risk"},
   "outputs": {"refund_payable": "payable_premium_pre_round"}}
  ```

  The mount re-produces `payable_premium_pre_round`, which §4.1's example computes after its minimum-premium clamp (`s_minprem`), so the refund is not clamped. A mount placed above the clamp would be (RL-1628 Limit 3). `days_on_risk` has no producer in §4.1's example, and `sub_graph:motor-cancellation@1` is illustrative: this shows the shape, not a complete FR-212 graph.
```

*(Re-pointed 2026-10-11, pre-mint refresh.)* T2 first replaced a mount in §4.1's example that
RL 9586's T1 wrote. That mount is gone: `RL-1519` (FD-1374, 2026-10-09) corrected the example to
mount no sub-graph (`03:344-347`), so the original find string has no hit at `d699a561`. The
content is unchanged. Only its place moves to §4.11, where a mount's shape is specified.

### T3 — `03` §5.2, the bundle per purpose. Find `` def load_bundle(bundle: Bundle) -> CompiledBundle     # FR-243's hydration step `` and insert after that line

```python
# Bundle.purpose_graphs: dict[str, JdmGraph]          # one graph per purpose a mount selects; empty
#                                                       # otherwise, and hashed only when non-empty
#                                                       # (RL-1628, DP-S3-2 (a))
# CompiledBundle: per purpose graph, its decision, algorithm and model_call handler; load_bundle's
#                 node-id check (RL-1571 C1) runs per purpose graph   # added <date>, WK-1250 Slice 3
```

## The texts for PL-1629 (applied by the planner, pre-mint)

Each find string has exactly one hit in PL-1629 at `7c8736fd`.

- **P1 — acceptance 3, the code.** Find `` naming the step and the purpose, with the code DP-S3-1's ruling names. `` and replace it with
  `` naming the step and the purpose, with `RATING_GRAPH_UNRESOLVED_REF` (RL-1628). Also red first (RL-1628, DP-S3-1 (d)): a purpose mount whose steps reach the `risk_premium_minor` output is refused with `VALIDATION_FAILED` (R1); a second re-producer of a name already re-produced is refused with `RATING_GRAPH_CYCLIC` (Limit 2). ``
- **P2 — Task 2, Step 1, the cases.** Find `` consuming a purpose-only name; DP-S3-1's override cases. `` and replace it with
  `` consuming a purpose-only name; DP-S3-1's re-production cases (RL-1628): a mount re-producing a parent name is accepted per purpose graph; R1's route to `risk_premium_minor` is refused; a second re-producer and a fragment step consuming `X` beside the re-producer are each refused as a cycle. ``
- **P3 — Task 3, Step 1, the inliner case.** Find `` adds the cancellation mounts and applies DP-S3-1's override; `` and replace it with
  `` adds the cancellation mounts, whose re-producing step reads the parent's value and re-produces it (RL-1628, DP-S3-1 (d)); ``
- **P4 — Task 3, Steps 1 and 3, the per-purpose load.** Find `` - `load_bundle` gives one decision per purpose graph. `` and replace it with
  `` - `load_bundle` gives one decision, algorithm and `model_call` handler per purpose graph, and refuses with `BUNDLE_COMPILE_FAILED` when a purpose graph's node ids differ from its re-inlined algorithm's (RL-1628, DP-S3-2 conditions 1 and 2). ``
  Then find `` - `bundle_hash` covers `purpose_graphs` only when it is non-empty. `` and insert after it
  `` - `CompiledBundle` holds the per-purpose decision, algorithm and handler; boosters stay shared (RL-1628, condition 1). ``
- **P5 — Task 4, Step 3, the selector.** Find `` The trace is built from the algorithm that was evaluated. `` and replace it with
  `` One selector returns the purpose's decision and algorithm, and every read of `bundle.algorithm` or `bundle.decision` in `build_scoring_result`, `score_one`, `_score_context_sync` and the batch row path goes through it: lookup misses, constraints, ladder inputs, outputs and the trace all use the algorithm that was evaluated (RL-1628, condition 1). Red first: a clamping `constraint` inside a cancellation mount appears in the cancellation quote's ladder. ``

## What it obliges

- **PL-1629's planner** applies P1 to P5 as a pre-mint edit to #1173. The plan's DP-S3-1 and
  DP-S3-2 rows then cite this record. Activation need 2 is met at this record's mint, with
  DP-S3-1 final only if the ACK accepts it.
- **WK-1250 Slice 3 (`SL-1341`)** applies T1 to T3 verbatim in its Task 1 spec commit, with its
  code (`CLAUDE.md` §2). It also strikes FR-218's `RL-1242` clause, and sets `RL-1242` `retired`
  in its final commit, as the maintainer accepted on 2026-10-05 at 16:43:57 BST. That is the plan's
  acceptance 9, and is not changed by this record.
- **Who writes `RL-1242`'s `active → retired` (acceptance 9)** *(added 2026-10-11, pre-mint
  refresh)*. The decision is the decision-maker's (`document-ids.md` §1.6, RL row, `:162`:
  *"`retired` when overridden with no successor"*), and **this record makes it**: `RL-1242` is
  retired, with no successor, by the commit in which Slice 3 strikes FR-218's interim clause. The
  **writer** is Slice 3's executor. It changes `RL-1242`'s `status:` line only, from `active` to
  `retired`, in that same final commit, and the commit message cites this record. The
  decision-maker cannot write it: it has no write access to a code worktree (its charter's
  *Never* line). `RL-1242`'s body is frozen and takes no note (`document-ids.md` §1.5). The lead's
  dispatch record names this bullet.

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

## Pre-mint refresh, 2026-10-11

Written 2026-10-11 11:30 BST (by `date`) by the decision-maker seat `dm-wk690`, on the
maintainer's (by delegation) entry headed *"2026-10-11 11:21:02 BST — DP-F (WK-1250 S3 plan
form): (a); DP-W-1 (a): confirmed; dm-wk690 seated: OK"* in `to-lead.md`, item 1: *"Refresh both
forward to current main and mint them together"*. Its three conditions, as applied:
- **The refresh base:** `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7` (#1272,
  2026-10-11T11:12:28+01:00). Every locator, and every find-string count, was re-read there.
- **This section is the dated record of every change.** Nothing below changed silently.
- **The ACK diff:** old draft tip `fc05b0f722511cf9ac63e189d26a05e8624d93f9`, refreshed tip
  = this branch's head (`git diff fc05b0f7..<head>`).

**Not changed: what was decided.** DP-S3-1 (d), R1, Limits 2 to 4, the codes, DP-S3-2 (a) and
both its conditions read as they did. DP-S3-1 is still final only at this record's ACK. Each
locator change is a moved line, not a changed premise. At `d699a561`:
- FR-212's chain and dependency rules hold as stated.
- `CompiledBundle` still holds one decision and one algorithm.
- `SubGraphRef` still has no `purposes`.
- No `purpose_graphs` exists.

**Changed:**
1. **Locators** re-read at `d699a561`, which moves `tree:`.
   - The FR-212 checks moved from `RatingAlgorithm._graph_invariants` into
     `graph_invariant_issues` (`rating.py:616`).
   - Three rows are added: the inliner's order, C1, and `SubGraphRef`.
   - The `_check_purpose_mount` row is added, as the code Slice 3 replaces.
2. **Limit 4.** It keeps the 17:06:26 BST ruling as its source, and adds the code that now
   delivers it: `to_wire`/`_dependency_order` (FD-1425, `SL-1436`) and the inliner's
   `_stable_topological` (`RL-1571` P5). The rule is unchanged.
3. **T2 re-pointed** from §4.1's example to a new bullet in §4.11. Its content is unchanged, and
   the reason is under T2. **Observed, not fixed here:** `RL-1571`'s landed §4.11 text (`03:943`)
   still says *"Mounted under §4.1's example, this fragment's step `s_ncd` becomes
   `s_ncd__s_ncd`"*, while §4.1's example has mounted nothing since `RL-1519`. That stale
   cross-reference is a §0 spec–spec disagreement for the lead to route. It is outside this
   record's decision points.
4. **T1's anchor made exact** (the Slice 2 paragraph at `03:349`).
5. **T1–T3's counts** re-taken at `d699a561`.
6. **Working ids now minted:**
   - RL 9586 → `RL-1571`, in condition 2 and T3's comment;
   - FD 9572 → `FD-1425`;
   - `relates:` gains `RL-1571`, `RL-1519`, `FD-1425` and `SL-1436`.
   PL-1629 was still unminted at this refresh; it is minted in the same D12 batch (2026-10-11) as PL-1629, after this record.
7. **Acceptance 9's writer is named** (§"What it obliges", last bullet). The decision is this
   record's. The writer is Slice 3's executor, in the final commit.

**Left to PL-1629's planner refresh, not ruled here:**
- P1 to P5's find strings were counted at `7c8736fd`, which is still that branch's tip at
  2026-10-11 11:29 BST. If the planner's refresh moves a find string, the replacement text still
  binds, and the planner re-quotes the anchor.
- planner-d11's readiness memo (`readiness-wk1250-s3-2026-10-11.md` §2) found acceptance 8 short
  by two Slice 2 interim tests (`test_rating_score.py:1023`, `:1036`). Adding them is PL-1629's
  edit.
