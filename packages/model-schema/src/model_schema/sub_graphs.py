"""The Sub-graph (03 §4.11, FR-217's artifact limb): a stored, versioned fragment of a
Rating Algorithm with typed input and output ports.

A Sub-graph Version is not a Governed Artifact (`RL-1309` DP-1): it has no status, and
every version carries a required change note. It mounts nothing (DP-4): there is no
`sub_graphs` field and the shapes forbid extras. The result-type check of the output
ports (FR-227) is `pricing-core`'s; this module owns the shape and the graph invariants.
"""

from __future__ import annotations

from itertools import pairwise

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from model_schema.graph_errors import GraphCycleError, GraphUnresolvedRefError
from model_schema.input_free import InputFreeError
from model_schema.rating import (
    AlgorithmOutput,
    RatingAlgorithm,
    RatingInputStep,
    RatingOutputStep,
    RatingResultType,
    RatingStep,
    _as_list,
    _consumed_by,
    _produced_by,
)
from model_schema.refs import Slug


class SubGraphInputPort(BaseModel):
    """A declared input of a fragment: a name and a result type (never float, FR-227)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    type: RatingResultType


class SubGraphBody(BaseModel):
    """A fragment's content: ports, steps and the required change note.

    The graph invariants are FR-212's, restated with the input ports as the first
    producers and the output ports as the consumers. Output ports reuse `AlgorithmOutput`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    inputs: list[SubGraphInputPort]
    outputs: list[AlgorithmOutput]
    steps: list[RatingStep]
    change_note: str = Field(min_length=1)

    @field_validator("change_note")
    @classmethod
    def _change_note_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise InputFreeError("a change note is required and is not blank (RL-1309 DP-1)")
        return value

    @model_validator(mode="after")
    def _graph_invariants(self) -> SubGraphBody:
        steps = self.steps
        ids = [s.step_id for s in steps]
        if len(ids) != len(set(ids)):
            raise InputFreeError("every step_id is unique (FR-215)")
        if any(isinstance(s, RatingInputStep | RatingOutputStep) for s in steps):
            raise InputFreeError("a sub-graph has no input or output steps: the ports replace them")
        ports = [p.name for p in self.inputs]
        if len(ports) != len(set(ports)):
            raise InputFreeError("every input port name is unique")
        outs = [o.name for o in self.outputs]
        if len(outs) != len(set(outs)):
            raise InputFreeError("every output port name is unique")

        produced = _produced_by(steps)
        consumed = _consumed_by(steps)
        port_names = set(ports)

        for out in self.outputs:
            if out.name not in produced:
                raise GraphUnresolvedRefError(
                    f"output port {out.name!r} is an undefined value: no step produces it (FR-212)"
                )

        dependencies: dict[str, set[str]] = {s.step_id: set() for s in steps}
        for step in steps:
            for name in _as_list(step.consumes):
                producers = produced.get(name)
                if not producers and name not in port_names:
                    raise GraphUnresolvedRefError(
                        f"step {step.step_id!r} consumes undefined value {name!r} (FR-212)"
                    )
                dependencies[step.step_id].update(
                    pid for pid in producers or [] if pid != step.step_id
                )

        order = _topological_order(steps, dependencies)
        position = {sid: i for i, sid in enumerate(order)}
        step_by_id = {s.step_id: s for s in steps}

        # A re-produced value is a chain whose first producer is the input port, when the
        # name is one. Each later producer must consume the name.
        for name, producers in produced.items():
            ordered = sorted(producers, key=lambda pid: position[pid])
            if name in port_names and name not in _as_list(step_by_id[ordered[0]].consumes):
                raise ValueError(
                    f"value {name!r} is an input port and step {ordered[0]!r} produces it "
                    "without consuming it: they do not form a single re-production chain (FR-212)"
                )
            for _prev, nxt in pairwise(ordered):
                if name not in _as_list(step_by_id[nxt].consumes):
                    raise ValueError(
                        f"value {name!r} is produced by {len(producers)} steps that do "
                        "not form a single re-production chain (FR-212)"
                    )

        from_inputs = RatingAlgorithm._reachable(
            {sid for name in port_names for sid in consumed.get(name, [])},
            step_by_id, produced, consumed,
        )
        feeds_output = RatingAlgorithm._reaches_output(
            {sid for out in self.outputs for sid in produced[out.name]},
            step_by_id, produced, consumed,
        )
        for step in steps:
            if step.step_id not in from_inputs and step.step_id not in feeds_output:
                raise ValueError(
                    f"step {step.step_id!r} is unreachable from any input port and "
                    "contributes to no output port (FR-212)"
                )
        return self


def _topological_order(
    steps: list[RatingStep], dependencies: dict[str, set[str]]
) -> list[str]:
    """Kahn's algorithm; a cycle raises `GraphCycleError` (FR-212)."""
    order: list[str] = []
    pending = {s.step_id: len(dependencies[s.step_id]) for s in steps}
    ready = [sid for sid, n in pending.items() if n == 0]
    while ready:
        sid = ready.pop()
        order.append(sid)
        for other in steps:
            if sid in dependencies[other.step_id]:
                pending[other.step_id] -= 1
                if pending[other.step_id] == 0:
                    ready.append(other.step_id)
    if len(order) != len(steps):
        raise GraphCycleError("the sub-graph contains a cycle (FR-212)")
    return order


class SubGraphCreate(SubGraphBody):
    """The request body of `POST /api/v1/sub-graphs`: a body plus its slug."""

    slug: Slug


class SubGraph(SubGraphCreate):
    """A stored, immutable Sub-graph Version (`sub_graph:<slug>@<version>`)."""

    version: int = Field(ge=1)
