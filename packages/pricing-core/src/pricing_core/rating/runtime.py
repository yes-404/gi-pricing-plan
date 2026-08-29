"""`CompiledBundle`, `load_bundle`, and the JDM wire translation (03 §5.2, FR-RATE-65,
W11 Task 1.3).

**Two types, deliberately not one** (Ruling 4, `docs/plans/2026-08-29-w11-prework-rulings.md`).
`Bundle` (`pricing_core.rating.compile`) is the record: a frozen, JSON-shaped, hashable,
Redis-cacheable `BaseModel`. `CompiledBundle` is what a warm worker holds after loading
one — a live `zen.ZenDecision` handle plus any GBM boosters deserialised into objects — and
it is never itself serialised. `load_bundle` is the hydration step between them, and per
Ruling 10 it is pure with respect to any cache: it consults none, registers itself in no
global, and starts no background task. Where a `CompiledBundle` is held across calls (a
per-worker slot, bounded, keyed by `Bundle.content_hash`) is Slice 2's Task 2.1 (Ruling 16)
— outside this module.

**The translation gap this module closes.** `to_jdm` (`compile.py`) produces a `JdmGraph`
keyed by `step_id`, with `produces`/`consumes` lists standing in for edges — pricing-core's
own intermediate form. The ZEN engine's Python binding consumes a different shape entirely:
a node **list** plus an explicit **edge list**, verified live against `zen.ZenEngine` rather
than assumed from any binding's docstring (`docs/plans/2026-08-29-w11-1-evaluator-core.md`,
*Verified facts*). `to_wire` is that translation.

**What this module does not yet translate.** A `constraint` step's wire translation was
Task 1.3's own scope cut, resolved by Task 1.4 (`_constraint_node`, below) — the DAG-wide
disposition (decline vs. clamp vs. error, collecting reason codes) is `score_one`'s, read
from the `{step_id}__violated` flags this module computes, never decided inside the graph
itself. A `lookup` step's `as_at` effective-dating window is
translated as an **exact key match only**: ZEN's comparison operators refuse non-numeric
operands (verified live — `'b' > 'a'` raises `vmError: Opcode Compare: Unsupported type`),
so an ISO date string cannot be range-compared inside a decision table rule without first
converting it to a numeric ordinal, which no step in this algorithm shape does today. A
lookup with more than one effective-dated row sharing a key returns whichever row's rule
comes first, not the one whose window contains the quote's `as_at` value. Both gaps are
named here rather than shipped silently; see the PR description for the recommended owner.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import polars as pl
import zen

from model_schema.modelling import GbmFitResult
from model_schema.rating import RatingAlgorithm, RatingModelCallStep
from pricing_core.modelling.gbm import load_gbm_booster, predict_gbm
from pricing_core.rating.compile import Bundle, JdmGraph

__all__ = ["MODEL_CALL_ERROR_KEY", "CompiledBundle", "load_bundle", "to_wire"]

_INPUT_ID = "input"
_OUTPUT_ID = "output"

#: Reserved key a `model_call` handler uses to report a failure through normal engine data
#: flow rather than an exception (W11 Task 1.4, resolving the finding below). `$`-prefixed
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


def _model_call_failure(step: RatingModelCallStep, message: str) -> dict[str, Any]:
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
    throughput gain (Ruling 5) comes from releasing the GIL during native execution, and
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
    output: dict[str, Any] = {str(name): 0 for name in _as_list(step.produces)}
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
        inputs = [{"id": "i0", "name": "key", "field": key_exprs[0] if key_exprs else "key"}]
        rules = [
            {"_id": f"r{i}", "i0": _quote(str(row["key"]), "string"), "o0": json.dumps(
                str(row.get("payload", {}).get(output_name, ""))
            )}
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


def _constraint_node(step_id: str, node: dict[str, Any]) -> dict[str, Any]:
    """A `constraint` step becomes an `expressionNode` (W11 Task 1.4, Ruling 9).

    Resolves the scope cut this module's own docstring named: `on_violation`'s three modes
    and `clamp_bounds`' semantics were left untranslated pending `score_one`'s design
    (Ruling 9's decline representation). Two things are computed here, and nothing more —
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
    exactly FR-RATE-39's "the ladder stays fully populated" for a declined quote.
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


def to_wire(graph: JdmGraph, payloads: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Translate pricing-core's `JdmGraph` into the JDM shape zen's binding consumes.

    `JdmGraph` is pricing-core's own intermediate form: a dict keyed by `step_id` with
    `produces`/`consumes` lists standing in for edges. The engine wants a node *list* plus
    an explicit edge list — verified against a live `ZenEngine().create_decision(...)`
    call, never a docstring (see this module's own docstring and
    `docs/plans/2026-08-29-w11-1-evaluator-core.md`'s *Verified facts*).

    `input`/`output`-typed steps are **not** translated 1:1 — the engine wants exactly one
    `inputNode` and one `outputNode` (Step 3, rule 2), so every input step collapses into
    the single `inputNode` and every output step's declared name is reached by wiring its
    producer directly to the single `outputNode`. Concretely: any name an interior step
    consumes that no *other interior step* produces is sourced from `inputNode` — which
    covers a name produced by an `input` step and, just as correctly, a name that is simply
    a raw context key nothing computes (`inputNode` relays the whole evaluate() context
    verbatim; verified live — an unreferenced context key still appears in the terminal
    result). Any interior step whose produced names are consumed by no other interior step
    is wired directly to `outputNode`; every other interior step's produced values still
    reach the result, because `passThrough` (rule 3) carries a node's entire received
    context forward along whatever path it is on and edges carry the whole merged dict, not
    one named value (verified live — a diamond of two independent producers converging on a
    third both survive into the final result with no direct edge to the sink).

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

    interior_ids = [
        step_id for step_id, node in graph.nodes.items() if node["type"] in _ENGINE_NODE_TYPE
    ]

    consumed_by_someone: set[str] = set()
    wire_nodes: list[dict[str, Any]] = [
        {"id": _INPUT_ID, "type": "inputNode", "name": "Request", "position": {"x": 0, "y": 0}}
    ]
    edges: list[dict[str, Any]] = []

    # `produced_by` is built **incrementally**, not as a full pre-pass, so that a step
    # consuming a name it also produces (the "clamp in place" re-production chain
    # `RatingAlgorithm._graph_invariants` already names and permits — `rating.py`'s own
    # comment: "a step never depends on itself, even when it re-produces a name it
    # consumed") resolves its *incoming* edge to whichever step produced that name
    # *before* this one runs, never to itself. A full pre-pass (Task 1.3's original
    # shape) would have every re-producer's own name already pointing at itself by the
    # time its consumed-edge is computed, wiring a self-loop the engine refuses at
    # decision-creation time (`cyclicGraph`) — verified live, not assumed. Every existing
    # (non-reproducing) step type is unaffected: a name produced exactly once resolves
    # identically whether `produced_by` is built all at once or incrementally.
    produced_by: dict[str, str] = {}
    for step_id in interior_ids:
        node = graph.nodes[step_id]
        kind = node["type"]

        for name in _as_list(node["consumes"]):
            name = str(name)
            consumed_by_someone.add(name)
            edges.append(_edge(produced_by.get(name, _INPUT_ID), step_id))

        if kind == "expression":
            wire_nodes.append(_expression_node(step_id, node))
        elif kind in ("table", "lookup"):
            wire_nodes.append(_decision_table_node(step_id, node, payloads))
        elif kind == "constraint":
            wire_nodes.append(_constraint_node(step_id, node))
        else:
            wire_nodes.append(_model_call_node(step_id))

        for name in _as_list(node["produces"]):
            produced_by[str(name)] = step_id

    for step_id in interior_ids:
        produced_names = {str(n) for n in _as_list(graph.nodes[step_id]["produces"])}
        if not produced_names & consumed_by_someone:
            edges.append(_edge(step_id, _OUTPUT_ID))

    wire_nodes.append(
        {"id": _OUTPUT_ID, "type": "outputNode", "name": "Response", "position": {"x": 0, "y": 0}}
    )
    return {"nodes": wire_nodes, "edges": edges}


def _model_call_handler(
    algorithm: RatingAlgorithm, payloads: Mapping[str, Any], boosters: Mapping[str, object]
) -> Callable[[Any], dict[str, Any]]:
    """Build the `customHandler` `load_bundle` wires into the `ZenEngine` it constructs.

    Ruling 7: the handler routes on `request.node["id"]` (the step id) against the
    algorithm and the resolved payloads already inside the `Bundle` — no I/O, no resolver.
    Ruling 8: a GBM pin scores through the pre-loaded `boosters[ref]` object, never through
    raw bytes, so N quotes against one `CompiledBundle` deserialise the booster once, not N
    times. Money-minor rounding here is a documented, provisional convention (`round()` to
    the nearest whole unit, on the assumption the pinned model was itself fitted to predict
    on the money-minor scale already) — Task 1.4's FR-RATE-34 golden test is where the
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
        ref = step.model_ref if step.model_ref is not None else step.peril_structure_ref
        if ref is None:  # pragma: no cover — schema-refused (FR-RATE-10)
            return _model_call_failure(step, f"model_call step {step.step_id!r} pins nothing.")
        ref_str = str(ref)
        payload = payloads[ref_str]
        fit_result = dict(payload["fit_result"])
        context = {k: v for k, v in request.input.items() if k != "$nodes"}
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
            # NFR-RATE-14: nthread=1 per request (F-W11-1-2). For LightGBM this is a
            # genuine per-call argument (safe under concurrency). For XGBoost this call is
            # a no-op by design — `booster` is already loaded (Ruling 8), and
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
            )

        return {"output": {str(name): value for name in _as_list(step.produces)}}

    return handler


def _load_boosters(
    algorithm: RatingAlgorithm, payloads: Mapping[str, Any]
) -> dict[str, object]:
    """Deserialise every pinned GBM's booster once (Ruling 8). Not a cache: this runs once
    per `load_bundle` call, and `load_bundle` itself consults no cache (Ruling 10).

    **`nthread=1` (NFR-RATE-14, F-W11-1-2) is baked in here, once, and nowhere else for
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
    """A loaded, executable bundle (FR-RATE-65). Never serialised (Ruling 4).

    `Bundle` is the record: hashable, distributable, cacheable. This is what a warm worker
    holds after loading one, and it owns an engine handle and live booster objects that
    have no serialised form at all — a `dataclass`, deliberately not a `BaseModel`, because
    a Pydantic model would give it a `model_dump_json()` that appears to work and silently
    drops the engine handle (Ruling 4's option (c), rejected for exactly this confusion).

    `content_hash` is the `Bundle.content_hash` this was loaded from (Ruling 10, clause i):
    every candidate deployment-switch mechanism compares a held hash against a current one,
    and a `CompiledBundle` that forgot its provenance would make FR-RATE-51's "either the
    old or the new bundle, never a mix" unverifiable at runtime.
    """

    content_hash: str
    decision: Any  # zen.ZenDecision — the binding exports no importable type for it
    algorithm: RatingAlgorithm
    boosters: Mapping[str, object]


def load_bundle(bundle: Bundle) -> CompiledBundle:
    """Hydrate a `Bundle` into a `CompiledBundle` (FR-RATE-65, Ruling 7).

    **Pure with respect to any cache** (Ruling 10, clause ii): consults no cache, registers
    itself in no global, starts no background task. Calling this twice on the same `Bundle`
    returns two independent `CompiledBundle`s holding two independent engine handles — the
    per-worker holding tier above this (Slice 2, Ruling 16) is what makes repeated calls
    unnecessary; it is not this function's job to notice that on its own.

    Performs no I/O: every pinned artifact's content already travels *inside* `bundle`
    (Ruling 7) — `resolved_payloads`, never a blob reference — so nothing here reaches a
    database, a blob store, or the network (NFR-RATE-3).
    """
    algorithm = RatingAlgorithm.model_validate(bundle.resolved_payloads[bundle.algorithm_ref])
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
