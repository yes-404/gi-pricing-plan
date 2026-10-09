"""The pure sub-graph inliner (FR-217; `RL-1309` DP-3; RL 9586 DP-S2-2, DP-S2-1, P5).

`inline_mounts` replaces each of an algorithm's sub-graph mounts by the pinned fragment's steps
and returns an ordinary `RatingAlgorithm` with `sub_graphs == []`. It is the one inliner:
`compile_bundle` calls it to validate and hash, `load_bundle` calls it to score, so the two
cannot disagree about what the mount became.

* **Namespacing.** Every fragment `step_id`, and every fragment name that is not a mapped port,
  becomes `<mount_point>__<name>`. The separator is `__` and not `/`, because `/` is FR-244's
  division operator. A mapped input port becomes the parent value it is mapped to, and a mapped
  output port the parent name it is mapped to.
* **By token.** Names inside an authored string are renamed by FR-244 token
  (`vocabulary.rename_tokens`), never by substring.
* **Isolation.** A namespaced name or step id that equals a parent name, a parent `step_id` or a
  key `to_wire` derives from one is refused, never merged. A fragment that re-produces one of its
  own input ports is refused: the port IS the parent's value, so the write would reach the parent.
* **Order.** The steps are in a stable topological order of their dependency edges, Kahn's
  algorithm with list order as the tie-break (the parent's steps, then each mount's), so an
  already-ordered list is unchanged and a parent step that consumes a mount output is listed after
  the fragment's steps (RL 9586 P5).

Pure: no I/O. The input-port TYPE check needs the producers' result types and lives in
`compile.py`, which imports this module, so this module imports nothing from it.
"""

from __future__ import annotations

import heapq
from collections.abc import Mapping, Sequence
from typing import Any, NoReturn

from pydantic import ValidationError

from model_schema.graph_errors import GraphUnresolvedRefError
from model_schema.rating import (
    RatingAlgorithm,
    RatingConstraintStep,
    RatingExpressionStep,
    RatingLookupStep,
    RatingModelCallStep,
    RatingStep,
    RatingTableStep,
    SubGraphRef,
)
from model_schema.sub_graphs import SubGraph
from pricing_core.rating.vocabulary import rename_tokens
from pricing_core.safe_error import CodedError

#: The namespace separator: `<mount_point>__<name>`.
SEPARATOR = "__"

#: The engine keys `to_wire` derives from a `step_id` (RL 9586 Locators): `<id>_e` and the four
#: `<id>__...` suffixes. A namespaced name may equal none of them for a parent step id, nor a
#: parent name any of them for a namespaced step id.
_DERIVED_SUFFIXES = ("_e", "__violated", "__before", "__min", "__max")


def _raise_named(code: str, message: str) -> NoReturn:
    raise CodedError(f"{code}: {message}") from None


def _as_list(value: str | list[str]) -> list[str]:
    return value if isinstance(value, list) else [value]


def _derived(step_id: str) -> set[str]:
    return {step_id, *(step_id + suffix for suffix in _DERIVED_SUFFIXES)}


def _rename_names(value: str | list[str], mapping: Mapping[str, str]) -> str | list[str]:
    if isinstance(value, list):
        return [mapping.get(name, name) for name in value]
    return mapping.get(value, value)


def _rename_text(text: str, mapping: Mapping[str, str], step_id: str) -> str:
    try:
        return rename_tokens(text, mapping)
    except ValueError:
        _raise_named(
            "VALIDATION_FAILED",
            f"step {step_id!r} of the sub-graph has an authored string outside FR-244's allow-list",
        )


def _port_mapping(mount: SubGraphRef, fragment: SubGraph) -> dict[str, str]:
    """The fragment name to parent name map for its ports, refusing a map that does not fit."""
    point = mount.mount_point
    ports = {port.name for port in fragment.inputs}
    declared = {out.name for out in fragment.outputs}
    unmapped = sorted(ports - set(mount.inputs))
    if unmapped:
        _raise_named(
            "RATING_GRAPH_UNRESOLVED_REF",
            f"mount {point!r} leaves input port(s) {unmapped} unmapped (FR-217)",
        )
    undeclared = sorted((set(mount.inputs) - ports) | (set(mount.outputs) - declared))
    if undeclared:
        _raise_named(
            "RATING_GRAPH_UNRESOLVED_REF",
            f"mount {point!r} maps port(s) {undeclared} the sub-graph does not declare (FR-217)",
        )
    if not mount.outputs:
        _raise_named(
            "RATING_GRAPH_UNRESOLVED_REF",
            f"mount {point!r} maps no output port, so it contributes nothing (FR-217)",
        )
    if len(set(mount.outputs.values())) != len(mount.outputs):
        _raise_named(
            "VALIDATION_FAILED",
            f"mount {point!r} maps two output ports to one parent name (FR-212)",
        )
    return {**mount.inputs, **mount.outputs}


def _inline_one(mount: SubGraphRef, fragment: SubGraph) -> tuple[list[RatingStep], set[str]]:
    """The fragment's steps renamed under `mount`, and the new value names they introduce."""
    point = mount.mount_point
    mapping = _port_mapping(mount, fragment)
    ports = {port.name for port in fragment.inputs}

    names: set[str] = set(ports)
    for step in fragment.steps:
        names.update(_as_list(step.produces))
        names.update(_as_list(step.consumes))
        if isinstance(step, RatingModelCallStep):
            names.update(step.feature_map.values())
    reproduced = sorted(ports & {n for s in fragment.steps for n in _as_list(s.produces)})
    if reproduced:
        _raise_named(
            "VALIDATION_FAILED",
            f"the sub-graph at mount {point!r} re-produces its input port(s) {reproduced}, "
            "which would write to the parent's value (FR-217)",
        )
    for name in sorted(names - set(mapping)):
        mapping[name] = f"{point}{SEPARATOR}{name}"
    new_names = {mapping[name] for name in names if name not in ports} - set(mount.outputs.values())

    steps: list[RatingStep] = []
    for step in fragment.steps:
        update: dict[str, Any] = {
            "step_id": f"{point}{SEPARATOR}{step.step_id}",
            "consumes": _rename_names(step.consumes, mapping),
            "produces": _rename_names(step.produces, mapping),
        }
        if isinstance(step, RatingLookupStep):
            update["key_expr"] = [_rename_text(t, mapping, step.step_id) for t in step.key_expr]
            update["as_at"] = _rename_text(step.as_at, mapping, step.step_id)
        elif isinstance(step, RatingTableStep):
            update["key_expr"] = [_rename_text(t, mapping, step.step_id) for t in step.key_expr]
        elif isinstance(step, RatingExpressionStep):
            update["expr"] = _rename_text(step.expr, mapping, step.step_id)
        elif isinstance(step, RatingConstraintStep):
            update["condition"] = _rename_text(step.condition, mapping, step.step_id)
            if step.clamp_bounds is not None:
                update["clamp_bounds"] = {
                    key: _rename_text(text, mapping, step.step_id)
                    for key, text in step.clamp_bounds.items()
                }
        elif isinstance(step, RatingModelCallStep):
            update["feature_map"] = {
                feature: mapping.get(name, name) for feature, name in step.feature_map.items()
            }
        steps.append(step.model_copy(update=update))
    return steps, new_names


def _stable_topological(steps: Sequence[RatingStep]) -> list[RatingStep]:
    """Kahn's algorithm over the dependency edges, list order as the tie-break (RL 9586 P5).

    Edge A -> B when B consumes a name A produces; a step never depends on itself (the clamp
    pattern). A cycle returns the list unchanged, so `RatingAlgorithm`'s own check reports it.
    """
    producers: dict[str, list[int]] = {}
    for index, step in enumerate(steps):
        for name in _as_list(step.produces):
            producers.setdefault(name, []).append(index)
    dependencies = [
        {p for name in _as_list(step.consumes) for p in producers.get(name, []) if p != index}
        for index, step in enumerate(steps)
    ]
    waiting = [len(deps) for deps in dependencies]
    ready = [i for i, count in enumerate(waiting) if count == 0]
    heapq.heapify(ready)
    order: list[int] = []
    while ready:
        index = heapq.heappop(ready)
        order.append(index)
        for other, deps in enumerate(dependencies):
            if index in deps:
                waiting[other] -= 1
                if waiting[other] == 0:
                    heapq.heappush(ready, other)
    return [steps[i] for i in order] if len(order) == len(steps) else list(steps)


def inline_mounts(
    algorithm: RatingAlgorithm, fragments: Mapping[str, SubGraph]
) -> RatingAlgorithm:
    """The algorithm with every mount replaced by its fragment's namespaced steps.

    `fragments` is keyed by `str(ArtifactRef)`, the key `resolved_payloads` uses. An algorithm
    with no mounts is returned as it is.
    """
    if not algorithm.sub_graphs:
        return algorithm

    inlined: list[RatingStep] = []
    new_names: set[str] = set()
    for mount in algorithm.sub_graphs:
        fragment = fragments.get(str(mount.ref))
        if fragment is None:
            _raise_named(
                "RATING_VERSION_UNPINNED",
                f"mount {mount.mount_point!r} names {mount.ref}, which no pinned sub-graph "
                "supplies (FR-237)",
            )
        steps, introduced = _inline_one(mount, fragment)
        inlined.extend(steps)
        new_names |= introduced

    reserved: set[str] = set()
    for step in algorithm.steps:
        reserved |= _derived(step.step_id)
        reserved.update(_as_list(step.consumes))
        reserved.update(_as_list(step.produces))
    for mount in algorithm.sub_graphs:
        reserved.update(mount.inputs.values())
        reserved.update(mount.outputs.values())
    new_ids = {step.step_id for step in inlined}
    clash = sorted((new_names | {d for i in new_ids for d in _derived(i)}) & reserved)
    if clash:
        _raise_named(
            "VALIDATION_FAILED",
            f"a namespaced sub-graph name equals a parent name or an engine key: {clash} (FR-217)",
        )

    ordered = _stable_topological([*algorithm.steps, *inlined])
    try:
        return RatingAlgorithm(
            slug=algorithm.slug,
            version=algorithm.version,
            input_contract=algorithm.input_contract,
            outputs=algorithm.outputs,
            steps=ordered,
            sub_graphs=[],
        )
    except ValidationError as exc:
        causes = [e.get("ctx", {}).get("error") for e in exc.errors()]
        unresolved = any(isinstance(c, GraphUnresolvedRefError) for c in causes)
        detail = next((str(c) for c in causes if c is not None), "its graph invariants")
        _raise_named(
            "RATING_GRAPH_UNRESOLVED_REF" if unresolved else "VALIDATION_FAILED",
            f"the algorithm with its sub-graphs inlined breaks {detail}",
        )
