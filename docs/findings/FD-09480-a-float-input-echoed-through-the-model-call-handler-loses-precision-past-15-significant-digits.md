---
id: FD-9480
family: finding
title: A float input echoed through the model_call handler loses precision past 15 significant digits
status: active
created: 2026-10-06
owner: auditor
tree: 23af6997161789887d26f2868a6022a0738e44e6
corrected_by: []
relates: [WK-673, SL-1436, FD-1425, RL-1423, LG-9482]
---

# A float input echoed through the model_call handler loses precision past 15 significant digits

**Filed** by the auditor on the lead's brief of 2026-10-06, from the maintainer's (by delegation) entry headed
"2026-10-05 23:51:14 BST — RL-1423 Condition B STOP (SL-1436 replay): (A) ACCEPTED ON CONDITIONS (the cause PROVEN first); a LOW FD; the
overlap disclosure accepted" in `to-lead.md` (a local channel file, cited by its header): *"A LOW FD (WK-673, by an auditor) records the
proven mechanism and proposes a cheap guard if one exists; the guard is not decided now."*

**Severity: LOW (proposed by the auditor; the lead gives the verdict). Owner: WK-673.**

## Finding

**Source of the proof.** The ledger LG-9482 on `origin/sl-1436-fd-1425-to-wire-dependency-order` at `a67f46ce465f9a17b4fea1f224714058ec0f3373`
(the entry added at `d6cca8e9`), under "The two conditions on ruling (A)", item (1). One single-file experiment (`echo_experiment.py`, a
scratch file that is not committed), one process, `OMP_NUM_THREADS=1 nice -n 19`: the same float, bench-rating-gbm context 0's `f0`, through
(i) an expression node only and (ii) a `customNode` whose handler returns `request.input` unchanged. Echoed verbatim by the ledger:

```
input         : 0.08487199515892163
(i)  expression: 0.08487199515892163
(ii) handler in : 0.08487199515892163
(ii) handler out: 0.0848719951589216
```

The handler **receives** the exact value; the same value returned unchanged leaves the engine cut to 15 significant digits. The expression
path keeps all 17. So the loss is on the handler's return path into the zen engine, not in any pricing-core arithmetic.

**Where it surfaces.** At that head `_model_call_handler` (`packages/pricing-core/src/pricing_core/rating/runtime.py:535`; the inner
`handler` closure at :556) ends with `return {"output": {**context, **{str(name): value ...}}}`: the context passes through, because FD-1425's
fix wires the interior steps as one path and a node that drops the context drops it for every later step. The engine is built at `:697`
(`zen.ZenEngine({"customHandler": handler})`). The golden replay of SL-1436 (ledger, "Task 2c, Steps 2 and 4 — the head replay"): 450 differing lines, all `raw`
lines of the `model_call` cases (bench-rating-gbm 200, bench-trace-size 5 x 50); the float inputs `f0`..`f7` cut to 15 significant digits;
maximum relative difference `1.17e-15`; no `score` or `score_trace` line differs and every `content_hash` is identical, so every served
`ScoringResult` is equal.

## Evidence

The brief's candidate guard is "the handler returns only the produced keys, merged over the original context on the Python side". Whether
zen merges a `customNode` handler's return over the node's input cannot be read from source (the binding is a compiled wheel), so it was
probed, 2026-10-06, one niced process, both gate slots read free before the run, against `origin/main` `23af6997`: a graph
`inputNode -> customNode(kind "model_call", config {}) -> outputNode` evaluated on `{"f0": 0.08487199515892163, "k": 2}`, with the node's
`passThrough` absent (the shape `runtime.py` emits) and present:

```
no passThrough echo {'f0': 0.0848719951589216, 'k': 2}
no passThrough produced_only {'p': 1}
passThrough echo {'f0': 0.0848719951589216, 'k': 2}
passThrough produced_only {'p': 1}
```

(`passThrough` is `{"passThrough": true}` on the node's `content.config`; `echo` returns `dict(request.input)`, `produced_only` returns
`{"p": 1}`; the script is a 20-line `zen.ZenEngine({"customHandler": h})` over that three-node graph, not committed. It ran in the repo's
`.venv` at the root checkout, `uv.lock` at `23af6997`.) **A handler's return REPLACES the node's context; the engine does not merge it.** A produced-only return therefore drops `f0`
and `k` from the result, which is the FD-1425 failure the pass-through exists to prevent, and a handler that wants a value to survive the node
must return it, through the engine's serialiser, which cuts it. Inside the engine the handler cannot avoid the round trip.
(The probe is one engine build; the zen version is whatever `uv.lock` resolves at that tree and was not pinned in the probe.)

## The exposure

A step that computes with, or bands on, a float input, or a float produced before the call, **after** a `model_call` sees the 15-digit
value, and a band edge within about 1e-15 flips. Money is integer or Decimal (`CLAUDE.md` §7), so a price is not directly at stake; a banding
input is. **None exists in the committed sets.** The ledger's downstream-reader check, predicate verbatim:

```
grep -rnE "\"type\": *\"model_call\"|type: *model_call|'type': *'model_call'" examples scripts packages backend docs/contracts --include=*.py --include=*.json --include=*.yaml --include=*.yml -l
git ls-files | grep -E "\.(json|ya?ml)$" | xargs grep -lE "\"model_call\""
grep -rnE "RatingModelCallStep\(" --include=*.py packages backend examples scripts      # non-src/ hits: none
```

then the steps after the call that read a float. In every scored case the steps after `s_risk` read `risk_premium_minor` (an `int`),
`driver_age` (an `int`), `expense_factor` (a rate-table float produced before the call, `1.1` and `1.25`, exact in 15 digits) and, in
`scripts/bench-rating.py`, `v000`.. (produced after); `f0`..`f7` are consumed only by `s_risk` itself; `examples/` has no `model_call` step.
**The auditor did not re-run that sweep**: the finding rests on the ledger's reading, and the first confirming event is the re-run in the
discharge below.

## Options for a guard (listed, not decided)

| # | Option | What it fixes | Cost / trade-off |
|---|---|---|---|
| 1 | **Accept and disclose.** Keep the ledger's limit (C) in the spec's `model_call` text as one dated sentence. | Nothing; names the bound. | Zero code. A future algorithm with a banding input past 15 digits is silently affected. |
| 2 | **A characterisation test** in `packages/pricing-core/tests/test_rating_wire_order.py` or `test_rating_runtime.py`: a float with 17 significant digits through a `model_call`, asserting the 15-digit cut (a pin, it passes today) or `xfail(strict=True)` on byte-for-byte survival (it goes red when the engine is fixed or a workaround lands). | The bound becomes executable; a zen upgrade that changes it is noticed. | One test, no behaviour change. It pins a defect rather than removing it. |
| 3 | **Overlay on the Python side, in `score_one`'s raw result:** after `evaluate`, restore the original request value for every key that no step `produces` (inputs only). | The served `raw` dict and anything read from it after evaluate. | Does **not** reach a downstream step inside the engine (the cut value is already what the next node receives), so the exposure in §3 is unchanged; adds an overlay rule that must exclude every produced name, including a clamp that overwrites an input name (`runtime.py`'s clamp comment: a produced value overrides the pre-clamp one). A second place that knows which names are inputs. |
| 4 | **Save-time check:** refuse, or warn on, a `model_call` followed by a step that consumes a float input or earlier-produced float. | The exposure, at the algorithm. | New validation on a declared algorithm shape, a spec change (`03` FR-212's neighbourhood) for a case with no committed instance; the most code of the four. |
| 5 | **Engine-side:** a zen build or binding option that preserves f64 across the handler return. | The cause. | Not investigated: no such option was looked for. Needs a spike under `library-spike`, and a pin change is a tech-dependency change (`skills-map.md`, same PR). |

**The "handler returns only the produced keys" guard is not available** (§2): it is not an option in the table because the probe refutes it.

## Disposition

**Carry forward with an owner: WK-673 (proposed; the lead's verdict).** Discharged when the maintainer (by delegation) picks one option above
and the pick lands as a merged artifact (a ruling, or the test of option 2). The next event that confirms or retires it: the first algorithm
committed or seeded with a float input, or a float produced before a `model_call`, read by a step after that call, which the sweep in §3
(re-run at that tree) finds.
