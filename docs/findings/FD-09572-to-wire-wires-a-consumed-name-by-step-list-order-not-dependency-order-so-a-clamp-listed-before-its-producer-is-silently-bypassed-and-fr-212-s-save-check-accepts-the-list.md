---
id: FD-9572
family: finding
title: `to_wire` wires a consumed name by step-list order, not dependency order: a clamp listed before its producer is silently bypassed, and FR-212's save check accepts the list
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
corrected_by: []
relates: [WK-673, WK-1178, FR-212, FR-243]
---

# FD-9572 — `to_wire` resolves each consumed name to the producer seen so far in LIST order; a valid saved algorithm whose list order differs from its dependency order prices wrongly, silently

**Filed** by auditor-towire on the lead's order of 2026-10-05, from the maintainer's (by delegation) entry headed "2026-10-05 17:01:30 BST — Discrepancy CLOSED; PR triage accepted (4 closes, each after its absorber merges); A-3/A-4/S3 rulings; the to_wire defect: REPRODUCE NOW" (`to-lead.md`, a local channel file, so cited by its header), and the lead's follow-up order for the two severity checks. The defect was first reported in dm-finals2's WK-1250 S2 addendum (`handover/dp-memo-wk1250-s2-2026-10-05.md`, a local file). Working id 9572 (reserved in the lead's `eta.md`). `tree:` is `origin/main` at filing; every measurement below ran at that tree.

## Finding

**Severity: HIGH (proposed by the auditor); owner: WK-673; deadline: before the Phase 2 exit demo (the maintainer's proposal in the 17:01:30 entry). Ruled by the maintainer (by delegation), 2026-10-05 17:06:26 BST entry (see Disposition); HIGH final per its condition, confirmed at the ACK.** Severity is HIGH because the reproduction below shows a **silent wrong price with no error and no extra request key**: a `constraint` clamp (the minimum-premium floor) listed before the step that produces the value it clamps is wired to the raw input, so the floor is never applied. The quote returns `quoted`, 1507 where the topologically ordered list returns 5250. (CLAUDE.md §2: a diverged shape in a pricing platform is a mispricing; §7: the rating path's correctness defaults are numbered requirements.)

`runtime.py` `to_wire` builds `produced_by` incrementally, in `graph.nodes` order, which is the algorithm's `steps` list order (`to_jdm` is `for step in algo.steps`). A name consumed by a step listed before its producer therefore resolves to the `inputNode`, not to the producer. Nothing earlier reorders or refuses such a list, so the defect is reachable from any saved algorithm.

## Evidence

### 1. Nothing reorders or refuses the list (code read at the tree above)

- `packages/model-schema/src/model_schema/rating.py`, `RatingAlgorithm._graph_invariants`: builds `dependencies` from consumes to producers by name, regardless of list position; runs Kahn's algorithm into a **local** `order` used only to detect a cycle (`GraphCycleError`) and to check re-production chains. `self.steps` is never reordered and no rule says a step must be listed after its producer. FR-212 (`03` §3) says "directed acyclic graph … Cycles, orphaned steps, and references to undefined Derived Values are rejected at save time": acyclic, not ordered.
- `packages/pricing-core/src/pricing_core/rating/compile.py`, `to_jdm`: `for step in algo.steps` fills `nodes` in list order. `compile_bundle` calls `to_jdm(algorithm)` and nothing in the module sorts steps (`grep -n -i 'sort\|topolog' packages/pricing-core/src/pricing_core/rating/compile.py` finds no reordering of steps).
- `packages/pricing-core/src/pricing_core/rating/runtime.py`, `to_wire` (:412; the incremental `produced_by` at :461-492): `edges.append(_edge(produced_by.get(name, _INPUT_ID), step_id))` runs before the step's own `produced_by[...]` assignment and before any later step's. The comment justifying the incremental build covers only the clamp-in-place self-edge; it does not consider a producer listed later.
- `packages/pricing-core/src/pricing_core/rating/score.py`, `score_one`: `context = {"effective_date": ..., "purpose": ..., **ctx.inputs}`, so **extra `ctx.inputs` keys are forwarded verbatim into the ZEN context** (`_validate_inputs` tolerates them, :333-340). This makes the "raw input" a caller-controlled value for any produced name.

### 2. The pure form, through compile and ZEN (script 1)

Script `au-towire-repro.py`, sha256 `6690fa733680b3a4e32578d71a3510de12da4dca61ef76c39bebf65661114ae0`. It was run as `OMP_NUM_THREADS=1 nice -n 10 uv run --directory <worktree at 137bc817> python au-towire-repro.py`. It is not committed.

```python
import asyncio, json
from uuid import uuid4
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import load_bundle, to_wire

IN = {"step_id": "s_in", "type": "input", "label": "x", "input_name": "x",
      "on_missing": "error", "produces": "x"}
A = {"step_id": "s_a", "type": "expression", "label": "A: base = x*100",
     "expr": "x * 100", "result_type": "money_minor", "consumes": ["x"], "produces": "base"}
B = {"step_id": "s_b", "type": "expression", "label": "B: premium = base + 50",
     "expr": "base + 50", "result_type": "money_minor", "consumes": ["base"], "produces": "premium"}
OUT = {"step_id": "s_out", "type": "output", "label": "out", "output_name": "premium_out",
       "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["premium"]}

def algo(steps):
    return {"slug": "order-test", "version": 1,
            "input_contract": [{"name": "x", "type": "int", "nullable": False, "min": 0, "max": 1000}],
            "outputs": [{"name": "premium_out", "type": "money_minor", "required": True}],
            "steps": steps, "sub_graphs": []}

def version():
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "order-test", "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": "model:none@1",
        "created_at": "2026-08-29T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-08-29T12:00:00Z",
        "algorithm_ref": "rating_algorithm:order-test@1",
        "pins": {"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []},
        "model_reference_mode": "exact"})

class R:
    def __init__(self, a): self.a = a
    async def resolve(self, ref: ArtifactRef):
        return ResolvedArtifact(status="approved", payload=self.a)

async def run(label, steps, ctx):
    bundle = await compile_bundle(version(), R(algo(steps)))   # real save-time validation + compile
    wire = to_wire(bundle.graph, bundle.resolved_payloads)
    edges = [(e["sourceId"], e["targetId"]) for e in wire["edges"]]
    c = load_bundle(bundle)
    print(f"--- {label}\n list order: {[s['step_id'] for s in steps]}\n edges: {edges}\n ctx: {ctx}")
    try:
        out = await c.decision.async_evaluate(ctx)
        print(f" result: {json.dumps(out['result'], sort_keys=True)}")
    except Exception as e:
        print(f" RAISED: {e}")

async def main():
    await run("TOPOLOGICAL order, ctx={x:3}", [IN, A, B, OUT], {"x": 3})
    await run("LIST order != topological (B before A), ctx={x:3}", [IN, B, A, OUT], {"x": 3})
    await run("LIST order != topological (B before A), ctx={x:3, base:7}  (raw key named like the produced name)", [IN, B, A, OUT], {"x": 3, "base": 7})
asyncio.run(main())
```

Output, verbatim:

```
--- TOPOLOGICAL order, ctx={x:3}
 list order: ['s_in', 's_a', 's_b', 's_out']
 edges: [('input', 's_a'), ('s_a', 's_b'), ('s_b', '__exact_reads'), ('__exact_reads', 'output')]
 ctx: {'x': 3}
 result: {"__exact__premium": "350", "base": 300, "premium": 350, "x": 3}
--- LIST order != topological (B before A), ctx={x:3}
 list order: ['s_in', 's_b', 's_a', 's_out']
 edges: [('input', 's_b'), ('input', 's_a'), ('s_b', '__exact_reads'), ('__exact_reads', 'output')]
 ctx: {'x': 3}
 RAISED: {"type":"NodeError","source":"Failed to evaluate expression: \"base + 50\"","nodeId":"s_b"}
--- LIST order != topological (B before A), ctx={x:3, base:7}  (raw key named like the produced name)
 list order: ['s_in', 's_b', 's_a', 's_out']
 edges: [('input', 's_b'), ('input', 's_a'), ('s_b', '__exact_reads'), ('__exact_reads', 'output')]
 ctx: {'x': 3, 'base': 7}
 result: {"__exact__premium": "57", "base": 7, "premium": 57, "x": 3}
```

The three runs: topological, 350; list order B before A with no raw `base`, a `NodeError` (loud); list order B before A with a raw `base` of 7, 57 (silent). The edges show the cause: `s_b` is wired from `input`, and the A to B edge does not exist.

### 3. Through `score_one`, on the real score fixture (script 2) — the silent forms

Script `au-towire-repro2.py`, sha256 `fc02caa44480752d587d9fad3e5aa75166f79a9bb9c40e73a94142572335228d`. It imports the helpers of `packages/pricing-core/tests/test_rating_score.py` (its algorithm, rate table and booster fixtures; no test is run) and only **permutes the `steps` list**. Run as `OMP_NUM_THREADS=1 nice -n 10 uv run --directory <worktree> python au-towire-repro2.py <worktree>/packages/pricing-core/tests`. Not committed.

```python
# Reuses the real score fixture (tests/test_rating_score.py helpers) and only PERMUTES the step list.
import asyncio, copy, json, sys
sys.path.insert(0, sys.argv[1])  # <worktree>/packages/pricing-core/tests
import test_rating_score as T
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import load_bundle, to_wire
from pricing_core.rating.score import score_one

def permute(steps, move, before):
    steps = list(steps)
    s = next(x for x in steps if x["step_id"] == move); steps.remove(s)
    i = next(i for i, x in enumerate(steps) if x["step_id"] == before); steps.insert(i, s)
    return steps

async def run(label, move=None, before=None, extra=None, min_premium=0):
    r = T._FakeResolver()
    a = copy.deepcopy(r._payloads["rating_algorithm:score-fixture@1"])
    if move: a["steps"] = permute(a["steps"], move, before)
    r._payloads["rating_algorithm:score-fixture@1"] = a
    bundle = await compile_bundle(T._version(), r)
    wire = to_wire(bundle.graph, bundle.resolved_payloads)
    into = {e["targetId"]: e["sourceId"] for e in wire["edges"]}
    print(f"--- {label}\n list: {[s['step_id'] for s in a['steps']]}")
    print(f" wired in: s_clamp<-{into.get('s_clamp')} s_office<-{into.get('s_office')} s_instalment<-{into.get('s_instalment')}")
    inputs = dict(T._ctx().inputs, min_premium_minor=min_premium, **(extra or {}))
    ctx = T._ctx(inputs=inputs)
    try:
        res = await score_one(load_bundle(bundle), ctx)
        print(f" outcome={res.outcome} payable={res.outputs.get('payable_premium_minor')} ladder={[(l.rung, l.value_minor) for l in res.premium_ladder]}")
    except Exception as e:
        print(f" RAISED {type(e).__name__}: {str(e)[:300]}")

async def main():
    # clamp chain: min premium 5000 makes the clamp bite (office is ~1.5k)
    await run("C0 baseline (topological), min_premium=5000", min_premium=5000)
    await run("C1 clamp LISTED BEFORE its producer s_office, min_premium=5000", "s_clamp", "s_office", min_premium=5000)
    await run("C1b same, clamp bites not (min_premium=0)", "s_clamp", "s_office")
    # extra-key forwarding: a consumer listed before its producer, caller sends the produced name
    await run("E0 baseline, extra key sent", extra={"office_premium_minor": 1})
    await run("E1 s_instalment LISTED BEFORE s_office, no extra key", "s_instalment", "s_office")
    await run("E2 s_instalment LISTED BEFORE s_office, caller sends office_premium_minor=1000", "s_instalment", "s_office", extra={"office_premium_minor": 1000})
asyncio.run(main())
```

Output, verbatim:

```
--- C0 baseline (topological), min_premium=5000
 list: ['s_in_age', 's_in_channel', 's_expense', 's_risk', 's_out_risk', 's_office', 's_clamp', 's_decl_cap', 's_decl_floor', 's_out_office', 's_instalment', 's_out_instalment', 's_out_payable']
 wired in: s_clamp<-s_office s_office<-s_expense s_instalment<-s_clamp
 outcome=quoted payable=5250 ladder=[('risk_premium', 1305), ('office_premium', 1436), ('constraints', 5000), ('instalment_loading', 5250), ('payable_premium', 5250)]
--- C1 clamp LISTED BEFORE its producer s_office, min_premium=5000
 list: ['s_in_age', 's_in_channel', 's_expense', 's_risk', 's_out_risk', 's_clamp', 's_office', 's_decl_cap', 's_decl_floor', 's_out_office', 's_instalment', 's_out_instalment', 's_out_payable']
 wired in: s_clamp<-input s_office<-s_expense s_instalment<-s_office
 outcome=quoted payable=1507 ladder=[('risk_premium', 1305), ('office_premium', 1436), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)]
--- C1b same, clamp bites not (min_premium=0)
 list: ['s_in_age', 's_in_channel', 's_expense', 's_risk', 's_out_risk', 's_clamp', 's_office', 's_decl_cap', 's_decl_floor', 's_out_office', 's_instalment', 's_out_instalment', 's_out_payable']
 wired in: s_clamp<-input s_office<-s_expense s_instalment<-s_office
 outcome=quoted payable=1507 ladder=[('risk_premium', 1305), ('office_premium', 1436), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)]
--- E0 baseline, extra key sent
 list: ['s_in_age', 's_in_channel', 's_expense', 's_risk', 's_out_risk', 's_office', 's_clamp', 's_decl_cap', 's_decl_floor', 's_out_office', 's_instalment', 's_out_instalment', 's_out_payable']
 wired in: s_clamp<-s_office s_office<-s_expense s_instalment<-s_clamp
 outcome=quoted payable=1507 ladder=[('risk_premium', 1305), ('office_premium', 1436), ('constraints', 1436), ('instalment_loading', 1507), ('payable_premium', 1507)]
--- E1 s_instalment LISTED BEFORE s_office, no extra key
 list: ['s_in_age', 's_in_channel', 's_expense', 's_risk', 's_out_risk', 's_instalment', 's_office', 's_clamp', 's_decl_cap', 's_decl_floor', 's_out_office', 's_out_instalment', 's_out_payable']
 wired in: s_clamp<-s_office s_office<-s_expense s_instalment<-input
 RAISED CodedError: RATING_EVALUATION_FAILED: the engine failed evaluating step 's_instalment' (FR-255); the failure is not a table or lookup miss; the engine error was a RuntimeError
--- E2 s_instalment LISTED BEFORE s_office, caller sends office_premium_minor=1000
 list: ['s_in_age', 's_in_channel', 's_expense', 's_risk', 's_out_risk', 's_instalment', 's_office', 's_clamp', 's_decl_cap', 's_decl_floor', 's_out_office', 's_out_instalment', 's_out_payable']
 wired in: s_clamp<-s_office s_office<-s_expense s_instalment<-input
 outcome=quoted payable=1050 ladder=[('risk_premium', 1305), ('office_premium', 1000), ('constraints', 1000), ('instalment_loading', 1050), ('payable_premium', 1050)]
```

Reading it:

- **C0 against C1 (the clamp chain).** With `min_premium_minor` 5000 the topological list clamps the office premium (1436) to 5000 and prices 5250. The same steps with `s_clamp` listed before `s_office` are wired `s_clamp<-input` and `s_instalment<-s_office`, so the clamp is **bypassed**: outcome `quoted`, payable 1507, ladder `constraints` 1436, no error, **no extra request key**. The minimum premium is silently not charged.
- **E1 against E2 (a plain consumer listed early).** With `s_instalment` listed before `s_office` and no extra key, `score_one` refuses with `RATING_EVALUATION_FAILED` (loud). A caller that sends `office_premium_minor=1000` in `inputs` gets `quoted`, payable 1050, a price built from the caller's own number (topological: 1507).

### 4. What was not measured

- **Exposure was not measured.** This essay did not scan stored algorithms, seeds or fixtures for a list whose order differs from its dependency order. Exposure is at least the next algorithm authored, by hand or through the authoring API; G2's algorithm (WK-1178 A-1..A-4) is the near-term one.
- The ZEN-level failure of E1 and of script 1's run 2 depends on the engine's error on an undefined name; a different expression (one that tolerates `null`) could turn the loud form silent. Not measured.
- No HTTP path was run; `api/score.py` was not read. `score_one` is the function that path calls.

## Disposition

Open. Filed by the auditor, 2026-10-05. **Severity HIGH, owner WK-673 and the deadline before the Phase 2 exit demo are ruled by the maintainer (by delegation)** in the entry headed "2026-10-05 17:06:26 BST — FD 9572 (to_wire wires by LIST order): reproduced; severity waits on (1)/(2); the FIX RULED now; RL 9588 / RL 9586 noted" (`to-lead.md`, a local channel file, so cited by its header). That entry set the severity as provisional HIGH, "final when (1) … and (2) … are answered. HIGH if either gives a silent wrong price on a reachable path; MEDIUM only if every reachable misorder raises." Evidence §3 answers both: (1) extra `ctx.inputs` keys reach ZEN, and (2) the clamp chain gives a silent wrong price with no extra key, so the condition for HIGH is met. The final HIGH is the maintainer's (by delegation) to confirm at the ACK.

**Remedy: RULED** (same entry, "THE FIX, RULED (root, not symptom): FR-212 makes a Rating Algorithm a DAG, so LIST ORDER CARRIES NO MEANING and must never decide wiring."):

- **(a)** `to_wire` (and `to_jdm`, if it emits edges by order) wires every consumed name to its PRODUCER by name through the graph, over a STABLE topological order computed from the dependency edges: Kahn's algorithm with list order as the tie-break, so an already-ordered list is unchanged and every existing bundle hash is stable. A test asserts the hash of a topologically listed algorithm is unchanged. (Reading at this tree: `to_jdm` emits no edges, only `produces`/`consumes` lists in `steps` order; the ordering belongs where `to_wire` iterates `interior_ids`.)
- **(b)** No save-time refusal of a misordered list: authors may list steps in any order.
- **(c)** Separately, a quote input must never shadow a produced value. Evidence §1 shows extra `ctx.inputs` keys reach ZEN, so a context key that names a step's produced value is refused (`VALIDATION_FAILED`, naming the key) or dropped per the `input_contract`. It has its own red test: ctx `{x:3, base:7}` on the CORRECTLY ordered algorithm still gives 350, never 57.
- The WK-1250 S2 inliner uses the same topological order (the entry: "RL 9586's P5 … ACCEPTED, as it is the same rule").

**Red first:** script 1's `[in, B, A, out]` scoring 350; script 2's clamp case C1 scoring 5250; and the shadowing case above.

**Placement** is not ruled here: "its own small WK-673 slice (or folded into the FD 9707 fix if that plan's write set already covers runtime.py's to_wire and the planner shows no scope creep). The planner proposes which." Owner of the fix plan: the planner.

Event that next confirms or discharges it: the fix PR merging with all three tests red first on the unfixed tree.

## Amendment (pre-mint), 2026-10-05 17:27 BST — the (c) premise measured on a correctly ordered algorithm: it FAILS at `score_one`

Added by auditor-premise on the lead's order, from the maintainer's (by delegation) ruling entries of 17:25:07 and 17:25:23 BST (`to-lead.md`, a local channel file, cited by header) and the "UNMEASURED premise" note on remedy (c) above. **Severity stays HIGH.** Tree: `origin/main` at `4d3be141`, detached worktree, `OMP_NUM_THREADS=1 nice -n 10 uv run`, no suite. Scripts (local, sha256): `r1.py` `8dea0ff6e301fed1b72a1f4a593a01ba10113ba8ca0124233f6dbd04cce66c95`, `r2.py` `b3448450a1fe4c5b9622ec15555fda8a5d983c0b82e1ca9bbb7b624df2fb501c`, `r3.py` `0ee537bf93e6c07fb548fec520321dd32a460a50283e6dd799e595558e897fac`, `r4.py` `ae53159a1ec39c51c1350b6f623907d106ad7b711e784f482ae7aa6ea5ca580c`, `r5.py` `98aea5df46d7df8e5fe8bc2a16f5e90e1bc35b32104b49fbc2f731157b7837d6`; `r1`–`r5` are copies of the §2/§3 scripts with `main()` replaced.

**Measured.**

- **ZEN, ordered `[in, A, B, out]`:** ctx `{x:3}` → `{"__exact__premium": "350", "base": 300, "premium": 350, "x": 3}`; ctx `{x:3, base:7}` → the same result, 350; ctx `{x:3, base:7, premium:9}` → 350. The premise holds at ZEN level for a linear chain.
- **`score_one`, score fixture in topological order, `min_premium_minor=5000`:** reference payable 5250. An extra input `instalment_loading_minor=777` gives **payable 777** (ladder `instalment_loading` 777, `payable_premium` 777). **Wrong; the correct price is 5250.** `office_premium_minor` (1, 777, 999999), `expense_factor`, `risk_premium_minor` and `payable_premium_minor` as extra keys leave 5250, and so do the `__exact__` names.
- **Cause (to the extent measured):** `runtime.py:495-499` wires every interior step whose produced names no other interior step consumes, including a step that produces nothing (the decline constraints `s_decl_cap`, `s_decl_floor`), straight to the sink; they fan in beside `s_instalment` and, via `passThrough` (`runtime.py:428-432`), carry the raw caller key. Moving `s_instalment` before the decline steps gives 5250; listing them after it gives 777 again, so the merge at the fan-in depends on list order. The last-listed branch winning is inferred from three runs; zen-engine's merge code was not read. `score.py:911` and `:1067` relay `**ctx.inputs` unfiltered.
- **Exposure in the gipricing DB:** one Rating Version, `fremtpl2-demo` v1 (`approved`, algorithm `demo-fixture-motor@1`), no `deployments` and no `deployment_requests` rows. That algorithm has one interior step and no fan-in, so it is not exposed by this mechanism by topology; not run.

**Consequence for the ruled remedy.** Remedy (c)'s red test ("ctx `{x:3, base:7}` on the CORRECTLY ordered algorithm still gives 350") passes at ZEN level and does not catch this; a red test must run `score_one` with an extra key naming a produced name that sits on a fan-in branch. Remedy (a) alone does not close it: a stable topological order does not remove the raw key from the sibling branches, so (c) is a guard that is needed on an ordered algorithm, not a belt for the misordered case only. Ordered algorithms are exposed.

**Not measured:** two terminal producers of the same name; zen-engine's merge rule in isolation; the HTTP path.
