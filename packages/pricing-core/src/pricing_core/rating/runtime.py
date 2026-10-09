"""`CompiledBundle`, `load_bundle`, and the JDM wire translation (03 §5.2, FR-243,
WK-671 Task 1.3).

**Two types, deliberately not one** (RL-867,
`docs/rulings/RL-00867-compiledbundle-is-spec-only-bundle-is-the-only-thing-that-exists-and-they-are-not-the-same-type.md`).
`Bundle` (`pricing_core.rating.compile`) is the record: a frozen, JSON-shaped, hashable,
Redis-cacheable `BaseModel`. `CompiledBundle` is what a warm worker holds after loading
one — a live `zen.ZenDecision` handle plus any GBM boosters deserialised into objects — and
it is never itself serialised. `load_bundle` is the hydration step between them, and per
RL-876 it is pure with respect to any cache: it consults none, registers itself in no
global, and starts no background task. Where a `CompiledBundle` is held across calls (a
per-worker slot, bounded, keyed by `Bundle.content_hash`) is Slice 2's Task 2.1 (RL-882)
— outside this module.

**The translation gap this module closes.** `to_jdm` (`compile.py`) produces a `JdmGraph`
keyed by `step_id`, with `produces`/`consumes` lists standing in for edges — pricing-core's
own intermediate form. The ZEN engine's Python binding consumes a different shape entirely:
a node **list** plus an explicit **edge list**, verified live against `zen.ZenEngine` rather
than assumed from any binding's docstring
(`docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`,
*Verified facts*). `to_wire` is that translation.

**What this module does not yet translate.** A `constraint` step's wire translation was
Task 1.3's own scope cut, resolved by Task 1.4 (`_constraint_node`, below) — the DAG-wide
disposition (decline vs. clamp vs. error, collecting reason codes) is `score_one`'s, read
from the `{step_id}__violated` flags this module computes, never decided inside the graph
itself. A `lookup` step's `as_at` window is translated per rule as a ZEN unary test,
`date($) >= date(from) and date($) < date(to)` (`_as_at_window`; the half-open interval of
`01` FR-69, open-ended when `to` is absent). ZEN's comparison operators refuse two strings
(verified live — `'b' > 'a'` raises `vmError: Opcode Compare: Unsupported type`), so both
sides go through `date()`. That function reads an offset as UTC, so the value it receives
must be a bare `YYYY-MM-DD`: `score.py`'s `_check_as_at_values` refuses anything else before
the engine runs (FR-221; PL 9688 DP-1). FD-1420 recorded the exact-key translation this
replaces.
"""

from __future__ import annotations

import heapq
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

import polars as pl
import zen

from model_schema.graph_errors import GraphCycleError
from model_schema.modelling import GbmFitResult
from model_schema.rating import RatingAlgorithm, RatingModelCallStep
from pricing_core.modelling.gbm import load_gbm_booster, predict_gbm
from pricing_core.rating.compile import Bundle, JdmGraph, check_step_refs_pinned
from pricing_core.rating.inline import inline_mounts, mounted_fragments
from pricing_core.safe_error import CodedError

__all__ = [
    "MODEL_CALL_ERROR_KEY",
    "CompiledBundle",
    "clamp_keys",
    "exact_key",
    "exact_read_names",
    "load_bundle",
    "to_wire",
]

_INPUT_ID = "input"
_OUTPUT_ID = "output"
#: The generated node that reads every reported name through `string()` (`RL-1329` §2), and
#: the result-key prefix of what it writes.
_EXACT_ID = "__exact_reads"
EXACT_PREFIX = "__exact__"

#: Reserved key a `model_call` handler uses to report a failure through normal engine data
#: flow rather than an exception (WK-671 Task 1.4, resolving the finding below). `$`-prefixed
#: to match the engine's own reserved `$nodes` key and stay clear of any user-declared
#: `produces` name.
MODEL_CALL_ERROR_KEY = "$model_call_error"

#: The engine node `type` each `RatingAlgorithm` step type translates to (Task 1.3 Step 3,
#: rules 3/5/6, widened by Task 1.4 for `constraint`). `input` and `output` are handled
#: separately — see `to_wire` — because the engine wants exactly one of each, not one per
#: declared step (Step 3, rule 2).
_ENGINE_NODE_TYPE: Mapping[str, str] = {
    "expression": "expressionNode",
    "lookup": "decisionTableNode",
    "table": "decisionTableNode",
    "model_call": "customNode",
    "constraint": "expressionNode",
}

#: A rate/reference table key's declared type, rendered as a ZEN literal (exact-match
#: only — see the module docstring's `interpolation` gap). `string`/`date` are quoted;
#: `int`/`bool` are already bare ZEN literals once read from the cell's own string form.
_QUOTED_KEY_TYPES = frozenset({"string", "date"})


def _model_call_failure(
    step: RatingModelCallStep, message: str, context: Mapping[str, Any]
) -> dict[str, Any]:
    """Resolves the Task 1.3 finding: report a `model_call` failure through data flow, not
    an exception.

    **The finding, verified live in Task 1.3 and not repeated here.** A `customHandler`'s
    raised exception is swallowed by the `zen` binding: whatever a handler raises — a bare
    `ValueError`, a custom exception subclass, any message — surfaces from
    `ZenDecision.evaluate()`/`async_evaluate()` as the *same* generic
    `RuntimeError: {"type":"NodeError","source":"Failed to run custom node handler",
    "nodeId":"<id>"}`, with the original type, message and code all discarded. `score_one`
    cannot recover *why* a `model_call` failed by catching and reading that exception.

    **Design chosen: a sentinel in the handler's own returned `output`** — the finding named
    two candidate channels, this one and a mutable side-channel the handler and `score_one`
    would share. **The side-channel is rejected, not merely left aside.** `CompiledBundle`
    is held once and scored many times, including *concurrently* — `async_evaluate`'s own
    throughput gain (RL-868) comes from releasing the GIL during native execution, and
    Task 1.4's own concurrency smoke test runs many `score_one` calls against one shared
    `CompiledBundle` via `asyncio.gather`. A mutable slot captured in this closure would be
    shared by every one of those calls; nothing in this codebase has verified which OS
    thread a `customHandler` callback actually runs on, so a slot written by one quote's
    failing `model_call` could be read back by a different quote's `score_one` before its
    own call completes — exactly the "corruption or cross-talk" that smoke test exists to
    catch, and building a channel that could fail it would be reckless rather than merely
    unverified. A sentinel key in the handler's returned `output` carries no such risk: it
    travels through the identical mechanism every other produced value already uses
    (`passThrough`, verified live in Task 1.3 and re-verified for this exact shape in Task
    1.4 — a handler returning `{"output": {..., MODEL_CALL_ERROR_KEY: ...}}` puts that key
    straight into `async_evaluate()`'s own `result`, no exception at all), which the engine
    already isolates per call — the same isolation that keeps two concurrent quotes' own
    computed values from crossing.

    Also returns a zero for every name `step` declares in `produces`, so a downstream
    `expression`/`constraint` step referencing this step's output does not hit the engine's
    own *undefined variable* failure on top of this one — `score_one` checks
    `MODEL_CALL_ERROR_KEY` before trusting any computed value, so the zero is never read as
    a real prediction.
    """
    output: dict[str, Any] = {**context, **{str(name): 0 for name in _as_list(step.produces)}}
    output[MODEL_CALL_ERROR_KEY] = f"MODEL_CALL_FAILED: {message}"
    return {"output": output}


def _as_list(value: Any) -> list[Any]:
    """Match `compile.py`'s own `_as_list`: an already-list value is returned as-is."""
    return value if isinstance(value, list) else [value]


def _edge(source: str, target: str) -> dict[str, str]:
    return {"id": f"e_{source}_{target}", "type": "edge", "sourceId": source, "targetId": target}


def _quote(value: str, key_type: str) -> str:
    """One rate/reference table cell's raw string value, as a ZEN equality literal."""
    if key_type in _QUOTED_KEY_TYPES:
        return "'" + value.replace("'", "\\'") + "'"
    return value


def _single_produced_name(node: dict[str, Any], step_id: str) -> str:
    names = _as_list(node["produces"])
    if len(names) != 1:
        raise NotImplementedError(
            f"expression step {step_id!r} produces {names!r}; to_wire only supports "
            "exactly one produced name per expression step."
        )
    return str(names[0])


def _expression_node(step_id: str, node: dict[str, Any]) -> dict[str, Any]:
    """Step 3, rule 3: every `expressionNode` sets `passThrough`, or the premium ladder's
    intermediate rungs never reach the terminal result (Verified facts item 3)."""
    key = _single_produced_name(node, step_id)
    return {
        "id": step_id,
        "type": "expressionNode",
        "name": step_id,
        "position": {"x": 0, "y": 0},
        "content": {
            "expressions": [{"id": f"{step_id}_e", "key": key, "value": node["expr"]}],
            "passThrough": True,
        },
    }


def _rate_table_rows(
    payload: Mapping[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], str]:
    """A `RateTableVersion` payload's rows, as `to_wire` needs them.

    Returns `(rows, keys, value_column_name)`. `rows` are the raw cell dicts
    (`dict[str, str]`, `rate_tables.py::_wire_rows`); `keys` are `RateTableKey` dumps.
    """
    if payload is None:
        return [], [], ""
    keys = list(payload.get("keys") or [])
    value_column = str(payload["value"]["name"])
    rows = list(payload.get("rows") or [])
    return rows, keys, value_column


def _reference_rows(payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """A `ReferenceTableVersion`-shaped payload's rows (`{"rows": [ReferenceRow, ...]}`,
    `rating_versions.py::_Resolver.resolve`'s `reference_table` branch)."""
    if payload is None:
        return []
    return list(payload.get("rows") or [])


def _as_at_window(row: Mapping[str, Any]) -> str:
    """One reference row's validity as a ZEN unary test on the step's `as_at` value.

    `01` FR-69's half-open `[effective_from, effective_to)`; an absent `effective_to` is
    open-ended. ZEN refuses `<` between strings, so both sides go through `date()` (verified
    on zen-engine 0.53.0, PL-1447 Task 0 run 1). The bounds are re-rendered through
    `date.fromisoformat`, so a malformed row raises here, at load, never inside the graph.
    """
    lower = date.fromisoformat(str(row["effective_from"])).isoformat()
    window = f"date($) >= date('{lower}')"
    if row.get("effective_to") is not None:
        upper = date.fromisoformat(str(row["effective_to"])).isoformat()
        window += f" and date($) < date('{upper}')"
    return window


def _decision_table_node(
    step_id: str, node: dict[str, Any], payloads: Mapping[str, Any]
) -> dict[str, Any]:
    """Step 3, rule 5: a `table`/`lookup` step becomes a `decisionTableNode`.

    Real row data comes from `payloads` (`Bundle.resolved_payloads`), keyed by the ref
    string `to_jdm` already carries on the node (`ArtifactRef.__str__`'s canonical wire
    form — `ArtifactRef` serialises to that string in both Python and JSON mode). `to_wire`
    is called with `payloads={}` when nothing is resolvable yet (a structural-only call);
    that produces a `decisionTableNode` with no inputs/outputs/rules rather than raising,
    since a not-yet-hydrated graph is not this function's failure to report.
    """
    kind = node["type"]
    produced = _as_list(node["produces"])
    output_name = str(produced[0]) if produced else ""
    key_exprs = [str(k) for k in _as_list(node.get("key_expr") or [])]

    if kind == "table":
        interpolation = node.get("interpolation", "none")
        if interpolation != "none":
            raise NotImplementedError(
                f"table step {step_id!r} declares interpolation={interpolation!r}; "
                "to_wire only translates interpolation='none' (exact-match rows) — see "
                "this module's docstring."
            )
        ref = str(node["rate_table_ref"])
        rows, keys, value_column = _rate_table_rows(payloads.get(ref))
        key_names = [str(k["name"]) for k in keys]
        inputs = [
            {"id": f"i{i}", "name": name, "field": key_exprs[i] if i < len(key_exprs) else name}
            for i, name in enumerate(key_names)
        ]
        rules = [
            {
                "_id": f"r{i}",
                **{
                    f"i{j}": _quote(str(row[key_names[j]]), str(keys[j]["type"]))
                    for j in range(len(key_names))
                },
                "o0": str(row[value_column]),
            }
            for i, row in enumerate(rows)
        ]
    else:  # "lookup"
        ref = str(node["reference_table_ref"])
        rows = _reference_rows(payloads.get(ref))
        inputs = [
            {"id": "i0", "name": "key", "field": key_exprs[0] if key_exprs else "key"},
            {"id": "i1", "name": "as_at", "field": str(node["as_at"])},
        ]
        rules = [
            {
                "_id": f"r{i}",
                "i0": _quote(str(row["key"]), "string"),
                "i1": _as_at_window(row),
                "o0": json.dumps(str(row.get("payload", {}).get(output_name, ""))),
            }
            for i, row in enumerate(rows)
            if output_name in (row.get("payload") or {})
        ]

    return {
        "id": step_id,
        "type": "decisionTableNode",
        "name": step_id,
        "position": {"x": 0, "y": 0},
        "content": {
            "hitPolicy": "first",
            "inputs": inputs,
            "outputs": [{"id": "o0", "name": output_name, "field": output_name}],
            "rules": rules,
            "passThrough": True,
            "inputField": None,
            "outputPath": None,
            "executionMode": "single",
        },
    }


def clamp_keys(step_id: str) -> tuple[str, str, str]:
    """`(before, min, max)` result keys a clamp step's node writes (`RL-1329` §2 step 5)."""
    return f"{step_id}__before", f"{step_id}__min", f"{step_id}__max"


def _constraint_node(step_id: str, node: dict[str, Any]) -> dict[str, Any]:
    """A `constraint` step becomes an `expressionNode` (WK-671 Task 1.4, RL-875).

    Resolves the scope cut this module's own docstring named: `on_violation`'s three modes
    and `clamp_bounds`' semantics were left untranslated pending `score_one`'s design
    (RL-875's decline representation). Two things are computed here, and nothing more —
    the *disposition* (decline vs. clamp vs. error, and collecting reason codes) is
    `score_one`'s, read from these values after one full evaluation, never decided inside
    the graph:

    1. `{step_id}__violated`: `!(condition)` — verified live that `!` negates a boolean in
       this engine (`not(...)` also works; `!` is used for brevity).
    2. For `on_violation="clamp"` only: the clamped replacement for the single name the step
       `produces`, keyed to the *same* name so `passThrough` overrides the pre-clamp value
       for every downstream consumer — verified live that a later node's `passThrough`
       output for a key a prior node also produced is what survives to the terminal result.
       Built from `clamp_bounds` (`{"min"|"max": "<expr>"}`, either or both) using the
       ternary operator, **not** an `if(cond, a, b)` function — verified live that ZEN has
       no such function (`zen.compile_expression` / decision creation both fail on it; this
       is exactly `compile.py`'s `_check_vocabulary`'s own warning about functions the
       spec's prose names that the engine does not have) — `cond ? a : b` is the form that
       works.

    A `decline`/`error` step (or a `clamp` step declaring no `produces`) emits only the
    `__violated` flag; the pre-existing value it `consumes` is left untouched, which is
    exactly FR-256's "the ladder stays fully populated" for a declined quote.
    """
    violated_key = f"{step_id}__violated"
    expressions: list[dict[str, Any]] = [
        {"id": f"{step_id}_v", "key": violated_key, "value": f"!({node['condition']})"}
    ]

    produced = _as_list(node.get("produces") or [])
    if node["on_violation"] == "clamp" and produced:
        consumed = _as_list(node.get("consumes") or [])
        if not consumed:
            raise NotImplementedError(
                f"constraint step {step_id!r} declares on_violation='clamp' and produces "
                f"{produced!r} but consumes nothing — to_wire has no source value to clamp."
            )
        bounds = node.get("clamp_bounds") or {}
        if not bounds:
            raise NotImplementedError(
                f"constraint step {step_id!r} declares on_violation='clamp' but no "
                "clamp_bounds — nothing to clamp towards."
            )
        before_key, min_key, max_key = clamp_keys(step_id)
        # Exact reads, ahead of the clamp expression that overwrites the name in place
        # (`RL-1329` §2 step 5): the value before the clamp, and each bound present.
        expressions.append(
            {"id": f"{step_id}_b", "key": before_key, "value": f"string({consumed[0]})"}
        )
        if "min" in bounds:
            expressions.append(
                {"id": f"{step_id}_n", "key": min_key, "value": f"string({bounds['min']})"}
            )
        if "max" in bounds:
            expressions.append(
                {"id": f"{step_id}_x", "key": max_key, "value": f"string({bounds['max']})"}
            )
        value_expr = str(consumed[0])
        if "min" in bounds:
            value_expr = f"({value_expr} < ({bounds['min']}) ? ({bounds['min']}) : {value_expr})"
        if "max" in bounds:
            value_expr = f"({value_expr} > ({bounds['max']}) ? ({bounds['max']}) : {value_expr})"
        expressions.append({"id": f"{step_id}_c", "key": str(produced[0]), "value": value_expr})

    return {
        "id": step_id,
        "type": "expressionNode",
        "name": step_id,
        "position": {"x": 0, "y": 0},
        "content": {"expressions": expressions, "passThrough": True},
    }


def exact_key(name: str) -> str:
    """The result key under which the engine's exact `string()` value of `name` arrives."""
    return f"{EXACT_PREFIX}{name}"


def exact_read_names(graph: JdmGraph) -> list[str]:
    """The names an `output` step reports — the source of every ladder rung and declared
    output — in declaration order, each once (`RL-1329` §2 step 1)."""
    names: dict[str, None] = {}
    for node in graph.nodes.values():
        if node["type"] == "output":
            consumed = _as_list(node.get("consumes") or [])
            if consumed:
                names[str(consumed[0])] = None
    return list(names)


def _exact_read_node(names: Sequence[str]) -> dict[str, Any]:
    """One generated node, after every step, that reads each reported name through the
    engine's `string()`: the exact decimal, never the float that crosses the binding
    (`RL-1329` §1 departure 1, FR-273's string limb). Generated text, so RL-1312's
    authored-string check does not read it."""
    return {
        "id": _EXACT_ID,
        "type": "expressionNode",
        "name": _EXACT_ID,
        "position": {"x": 0, "y": 0},
        "content": {
            "expressions": [
                {"id": f"{_EXACT_ID}_{index}", "key": exact_key(name), "value": f"string({name})"}
                for index, name in enumerate(names)
            ],
            "passThrough": True,
        },
    }


def _model_call_node(step_id: str) -> dict[str, Any]:
    """Step 3, rule 6: a `model_call` step becomes a `customNode`.

    The engine requires `content` to be exactly `{"kind": ..., "config": ...}` (verified
    live — a `customNode` with any other content shape fails decision creation with
    `missing field 'kind'`/`'config'`). No routing data needs to live in `config`: the
    handler `load_bundle` installs closes over the algorithm and the resolved payloads,
    and looks the step up by `request.node["id"]`, which equals `step_id` here.
    """
    return {
        "id": step_id,
        "type": "customNode",
        "name": step_id,
        "position": {"x": 0, "y": 0},
        "content": {"kind": "model_call", "config": {}},
    }


def _dependency_order(graph: JdmGraph, interior_ids: Sequence[str]) -> list[str]:
    """The interior steps in a stable topological order (FR-212, FD-1425).

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


def to_wire(graph: JdmGraph, payloads: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Translate pricing-core's `JdmGraph` into the JDM shape zen's binding consumes.

    `JdmGraph` is pricing-core's own intermediate form: a dict keyed by `step_id` with
    `produces`/`consumes` lists standing in for edges. The engine wants a node *list* plus
    an explicit edge list — verified against a live `ZenEngine().create_decision(...)`
    call, never a docstring (see this module's own docstring and
    `docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`'s
    *Verified facts*).

    `input`/`output`-typed steps are **not** translated 1:1 — the engine wants exactly one
    `inputNode` and one `outputNode` (Step 3, rule 2), so every input step collapses into
    the single `inputNode` and every output step's declared name is reached through the
    single `outputNode`. The interior steps form **one path** from `inputNode` to the sink,
    in `_dependency_order`'s stable topological order, never the list order (FD-1425): each
    node has exactly one incoming edge, so no merge happens anywhere and a name's final
    producer writes it after every earlier copy. A name an interior step consumes that no
    other interior step produces is read off `inputNode`, which relays the whole evaluate()
    context verbatim (verified live — an unreferenced context key still appears in the
    terminal result). Every node carries its entire received context forward
    (`passThrough`, rule 3), so each produced value reaches the result along the path; a
    linear algorithm (`[in, A, B, out]`) wires exactly as the per-name edges did.

    `payloads` (`Bundle.resolved_payloads`) hydrates `table`/`lookup` steps with real row
    data; omitted, those steps produce a structurally valid but empty decision table.
    """
    payloads = payloads or {}
    unsupported = sorted(
        {
            f"{step_id} ({node['type']})"
            for step_id, node in graph.nodes.items()
            if node["type"] not in _ENGINE_NODE_TYPE and node["type"] not in ("input", "output")
        }
    )
    if unsupported:
        raise NotImplementedError(f"to_wire has no wire translation for step(s) {unsupported}.")

    interior_ids = _dependency_order(
        graph,
        [step_id for step_id, node in graph.nodes.items() if node["type"] in _ENGINE_NODE_TYPE],
    )

    wire_nodes: list[dict[str, Any]] = [
        {"id": _INPUT_ID, "type": "inputNode", "name": "Request", "position": {"x": 0, "y": 0}}
    ]
    edges: list[dict[str, Any]] = []

    previous = _INPUT_ID
    for step_id in interior_ids:
        node = graph.nodes[step_id]
        kind = node["type"]
        edges.append(_edge(previous, step_id))
        previous = step_id

        if kind == "expression":
            wire_nodes.append(_expression_node(step_id, node))
        elif kind in ("table", "lookup"):
            wire_nodes.append(_decision_table_node(step_id, node, payloads))
        elif kind == "constraint":
            wire_nodes.append(_constraint_node(step_id, node))
        else:
            wire_nodes.append(_model_call_node(step_id))

    exact_names = exact_read_names(graph)
    if exact_names:
        wire_nodes.append(_exact_read_node(exact_names))
        edges.append(_edge(previous, _EXACT_ID))
        edges.append(_edge(_EXACT_ID, _OUTPUT_ID))
    elif interior_ids:
        edges.append(_edge(previous, _OUTPUT_ID))

    wire_nodes.append(
        {"id": _OUTPUT_ID, "type": "outputNode", "name": "Response", "position": {"x": 0, "y": 0}}
    )
    return {"nodes": wire_nodes, "edges": edges}


def _model_call_handler(
    algorithm: RatingAlgorithm, payloads: Mapping[str, Any], boosters: Mapping[str, object]
) -> Callable[[Any], dict[str, Any]]:
    """Build the `customHandler` `load_bundle` wires into the `ZenEngine` it constructs.

    RL-873: the handler routes on `request.node["id"]` (the step id) against the
    algorithm and the resolved payloads already inside the `Bundle` — no I/O, no resolver.
    RL-874: a GBM pin scores through the pre-loaded `boosters[ref]` object, never through
    raw bytes, so N quotes against one `CompiledBundle` deserialise the booster once, not N
    times. Money-minor rounding here is a documented, provisional convention (`round()` to
    the nearest whole unit, on the assumption the pinned model was itself fitted to predict
    on the money-minor scale already) — Task 1.4's FR-250 golden test is where the
    actual monetary contract for a `model_call` output gets fixed; flagged in the PR
    description rather than asserted here as settled.
    """
    steps_by_id = {
        step.step_id: step
        for step in algorithm.steps
        if isinstance(step, RatingModelCallStep)
    }

    def handler(request: Any) -> dict[str, Any]:
        step = steps_by_id[request.node["id"]]
        context = {k: v for k, v in request.input.items() if k != "$nodes"}
        ref = step.model_ref if step.model_ref is not None else step.peril_structure_ref
        if ref is None:  # pragma: no cover — schema-refused (FR-222)
            return _model_call_failure(
                step, f"model_call step {step.step_id!r} pins nothing.", context
            )
        ref_str = str(ref)
        payload = payloads[ref_str]
        fit_result = dict(payload["fit_result"])
        feature_row = {
            feature_slug: context[graph_name]
            for graph_name, feature_slug in step.feature_map.items()
            if graph_name in context
        }

        model_type = fit_result.get("model_type")
        if model_type in ("xgboost", "lightgbm"):
            fit_result.pop("booster_content", None)
            gbm_result = GbmFitResult.model_validate(fit_result)
            booster = boosters[ref_str]
            frame = pl.DataFrame([feature_row]) if feature_row else pl.DataFrame(
                {slug: [context.get(slug)] for slug in gbm_result.feature_order}
            )
            # NFR-501: nthread=1 per request (F-W11-1-2). For LightGBM this is a
            # genuine per-call argument (safe under concurrency). For XGBoost this call is
            # a no-op by design — `booster` is already loaded (RL-874), and
            # `predict_gbm` refuses to `set_param` a shared, already-loaded `Booster` on
            # every call because that races a concurrent `predict()` on the same object
            # and crashes (verified live — see `predict_gbm`'s own docstring).
            # `_load_boosters`, below, is where nthread=1 is actually baked in for
            # XGBoost, once, before any concurrent scoring begins.
            prediction = float(
                predict_gbm(gbm_result, booster, frame, factors=(), nthread=1)[0]
            )
            value: int = round(prediction)
        else:
            return _model_call_failure(
                step,
                f"model_call step {step.step_id!r} pins a {model_type!r} model. "
                "Bundle.resolved_payloads carries the Model's own dump but not the "
                "Factor/Banding/Grouping objects predict_glm requires (ModelSpecCommon."
                "factors is bare UUIDs — resolve_factors builds zero design columns from "
                "an empty sequence, so every non-intercept coefficient's term goes "
                "unresolved). Scoring a GBM works because predict_gbm has a documented "
                "fallback for factors=() that reads each feature off the frame directly; "
                "predict_glm has no such fallback.",
                context,
            )

        # The one success return: the context passes through (FD-1425), because on the
        # ordered chain a node that drops it drops it for every later step. A branch added
        # for another model type returns through this expression, or `_model_call_failure`.
        return {"output": {**context, **{str(name): value for name in _as_list(step.produces)}}}

    return handler


def _load_boosters(
    algorithm: RatingAlgorithm, payloads: Mapping[str, Any]
) -> dict[str, object]:
    """Deserialise every pinned GBM's booster once (RL-874). Not a cache: this runs once
    per `load_bundle` call, and `load_bundle` itself consults no cache (RL-876).

    **`nthread=1` (NFR-501, F-W11-1-2) is baked in here, once, and nowhere else for
    XGBoost.** This runs synchronously, before `load_bundle` returns and before any
    concurrent scoring against the resulting `CompiledBundle` can begin — the only point in
    this object's life where mutating it (`Booster.set_param`) is safe. `predict_gbm`
    deliberately does *not* repeat this on every call against an already-loaded booster;
    see its own docstring for the crash that discipline avoids.
    """
    boosters: dict[str, object] = {}
    for step in algorithm.steps:
        if not isinstance(step, RatingModelCallStep):
            continue
        ref = step.model_ref if step.model_ref is not None else step.peril_structure_ref
        if ref is None:
            continue
        ref_str = str(ref)
        if ref_str in boosters:
            continue
        if ref_str not in payloads:
            raise CodedError(
                f"RATING_VERSION_UNPINNED: model_call step {step.step_id!r} names {ref_str}, "
                "which the bundle does not carry (FR-237)"
            )
        fit_result = payloads[ref_str].get("fit_result", {})
        model_type = fit_result.get("model_type")
        if model_type in ("xgboost", "lightgbm"):
            booster_text = fit_result["booster_content"]
            boosters[ref_str] = load_gbm_booster(
                model_type, booster_text.encode("utf-8"), nthread=1
            )
    return boosters


@dataclass(frozen=True)
class CompiledBundle:
    """A loaded, executable bundle (FR-243). Never serialised (RL-867).

    `Bundle` is the record: hashable, distributable, cacheable. This is what a warm worker
    holds after loading one, and it owns an engine handle and live booster objects that
    have no serialised form at all — a `dataclass`, deliberately not a `BaseModel`, because
    a Pydantic model would give it a `model_dump_json()` that appears to work and silently
    drops the engine handle (RL-867's option (c), rejected for exactly this confusion).

    `content_hash` is the `Bundle.content_hash` this was loaded from (RL-876, clause i):
    every candidate deployment-switch mechanism compares a held hash against a current one,
    and a `CompiledBundle` that forgot its provenance would make FR-268's "either the
    old or the new bundle, never a mix" unverifiable at runtime.
    """

    content_hash: str
    decision: Any  # zen.ZenDecision — the binding exports no importable type for it
    algorithm: RatingAlgorithm
    boosters: Mapping[str, object]


def _check_graph_matches_inlined_algorithm(graph: JdmGraph, algorithm: RatingAlgorithm) -> None:
    """C1 (RL 9586 DP-S2-1): the stored graph's node ids are the inlined algorithm's step ids."""
    in_graph = set(graph.nodes)
    in_algorithm = {step.step_id for step in algorithm.steps}
    if in_graph != in_algorithm:
        first = sorted(in_graph ^ in_algorithm)[0]
        raise CodedError(
            f"BUNDLE_COMPILE_FAILED: the bundle's graph and its re-inlined algorithm disagree "
            f"on node {first!r}"
        ) from None


def load_bundle(bundle: Bundle) -> CompiledBundle:
    """Hydrate a `Bundle` into a `CompiledBundle` (FR-243, RL-873).

    **Pure with respect to any cache** (RL-876, clause ii): consults no cache, registers
    itself in no global, starts no background task. Calling this twice on the same `Bundle`
    returns two independent `CompiledBundle`s holding two independent engine handles — the
    per-worker holding tier above this (Slice 2, RL-882) is what makes repeated calls
    unnecessary; it is not this function's job to notice that on its own.

    Performs no I/O: every pinned artifact's content already travels *inside* `bundle`
    (RL-873) — `resolved_payloads`, never a blob reference — so nothing here reaches a
    database, a blob store, or the network (NFR-491).

    Refuses with `RATING_VERSION_UNPINNED` a bundle whose step ref is not pinned at its exact
    version, so a bundle compiled before that check existed cannot price silently (FR-237).

    **Re-inlines each pinned sub-graph** (FR-217; RL 9586 DP-S2-1 (a)) with the same pure
    `inline_mounts` that `compile_bundle` used, from the payloads already in the bundle. The
    stored algorithm artifact stays what its ref names (RL-873), `Bundle`'s shape is unchanged,
    and the `CompiledBundle.algorithm` that scoring, the model-call handler and the trace read
    is the inlined one. A bundle with no mounts re-inlines to itself. Refuses with
    `BUNDLE_COMPILE_FAILED` a bundle whose graph and re-inlined algorithm disagree on their
    nodes (RL 9586 C1), before the engine is built.
    """
    stored = RatingAlgorithm.model_validate(bundle.resolved_payloads[bundle.algorithm_ref])
    fragments = mounted_fragments(stored, bundle.pins, bundle.resolved_payloads)
    algorithm = inline_mounts(stored, fragments)
    _check_graph_matches_inlined_algorithm(bundle.graph, algorithm)
    check_step_refs_pinned(algorithm, bundle.pins)
    boosters = _load_boosters(algorithm, bundle.resolved_payloads)
    handler = _model_call_handler(algorithm, bundle.resolved_payloads, boosters)
    wire = to_wire(bundle.graph, bundle.resolved_payloads)

    engine = zen.ZenEngine({"customHandler": handler})
    decision = engine.create_decision(json.dumps(wire))
    decision.validate()

    return CompiledBundle(
        content_hash=bundle.content_hash,
        decision=decision,
        algorithm=algorithm,
        boosters=boosters,
    )
