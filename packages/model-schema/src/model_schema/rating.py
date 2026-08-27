"""The Phase 1b rating version (OD1, W7-3) — the smallest artifact 03's approval can pin.

The full 03 surface — compile, score, rate tables, deployment — stays Phase 2. This is
the artifact the exit demo needs: a slugged, versioned, draft → review → approved rating
version that pins an approved Model, so `wf-01`'s journey ends with something a rating
version can be approved against and the demo can display.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from itertools import pairwise
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from model_schema.refs import ArtifactRef, Slug


class RatingVersionStatus(StrEnum):
    """The three states a minimal rating version passes through (OD1)."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"


#: The lifecycle, as data rather than scattered `if` statements. `draft` may skip review
#: straight to `approved` only where the caller is an approver deciding in one step; the
#: normal path goes through `review`.
VALID_RATING_VERSION_TRANSITIONS: dict[
    RatingVersionStatus, frozenset[RatingVersionStatus]
] = {
    RatingVersionStatus.DRAFT: frozenset(
        {RatingVersionStatus.REVIEW, RatingVersionStatus.APPROVED}
    ),
    RatingVersionStatus.REVIEW: frozenset({RatingVersionStatus.APPROVED}),
    RatingVersionStatus.APPROVED: frozenset(),
}


class RatingVersion(BaseModel):
    """A Phase 1b-minimal rating version that pins an approved Model (OD1, W7-3).

    The envelope is inline (00 §4.3), like `DatasetVersion`. `model_ref` is the pinned
    approved Model as an `ArtifactRef` (`model:{slug}@{version}`), so the approval trail
    names the exact model a version of rating logic would be approved against.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    slug: Slug
    version: int = Field(ge=1)
    status: RatingVersionStatus
    dataset_version_id: UUID
    model_ref: ArtifactRef
    created_at: datetime
    created_by: UUID
    updated_at: datetime


# ---------------------------------------------------------------------------
# Rating Algorithm (03 §4.1) — the declarative graph of rating steps.
#
# W9-1. The shape carries the seven step types (§3.2), the typed input contract
# (FR-RATE-2), the typed outputs (FR-RATE-3), the sub-graph references (FR-RATE-6),
# and the graph invariants the spec states beside the §4.1 example. The strict
# save-time validation and the bundle compilation are W9-2 / W9-3.
# ---------------------------------------------------------------------------

class RatingInputType(StrEnum):
    """The six Rating Input types (FR-RATE-2)."""

    INT = "int"
    DECIMAL = "decimal"
    STRING = "string"
    DATE = "date"
    BOOL = "bool"
    ENUM = "enum"


class InputContractField(BaseModel):
    """One Rating Input (FR-RATE-2): name, type, nullability, range or domain, description."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    type: RatingInputType
    nullable: bool = False
    min: Decimal | int | None = None
    max: Decimal | int | None = None
    pattern: str | None = None
    domain: list[str] | None = None
    description: str | None = None


def _reject_float_type(value: str) -> str:
    """FR-RATE-13: a monetary result is `decimal` or `money_minor`, never float.

    The whole rating path is integer minor units or Decimal (`CLAUDE.md` §7), so
    `float` is refused in every declared result type, not just the monetary ones.
    """
    if "float" in value:
        raise ValueError(
            "a rating result type is never float (FR-RATE-13); a monetary result is "
            f"decimal or money_minor (got {value!r})"
        )
    return value


#: A declared result type. `decimal`/`money_minor` carry money; `float` is refused.
RatingResultType = Annotated[str, AfterValidator(_reject_float_type)]


class AlgorithmOutput(BaseModel):
    """A declared output (FR-RATE-3): name, type, required flag."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    type: RatingResultType
    required: bool = True


class RoundSpec(BaseModel):
    """Explicit rounding for an `output` step (FR-RATE-12) — never implicit, never twice."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: Literal["half_even", "half_up", "ceiling", "floor"]
    dp: int = Field(ge=0)


class RatingStepBase(BaseModel):
    """Common step fields (FR-RATE-4): stable id, label, optional note, produces/consumes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str = Field(min_length=1)
    label: str
    note: str | None = None
    consumes: str | list[str] = Field(default_factory=list)
    produces: str | list[str] = Field(default_factory=list)


class RatingInputStep(RatingStepBase):
    type: Literal["input"]
    input_name: str
    on_missing: Literal["error", "default", "null"]


class RatingLookupStep(RatingStepBase):
    type: Literal["lookup"]
    reference_table_ref: ArtifactRef
    key_expr: list[str] = Field(default_factory=list)
    as_at: str
    on_miss: Literal["error", "default"]


class RatingTableStep(RatingStepBase):
    type: Literal["table"]
    rate_table_ref: ArtifactRef
    key_expr: list[str] = Field(default_factory=list)
    on_miss: Literal["error", "default"] = "error"
    interpolation: Literal["none", "linear"] = "none"


class RatingExpressionStep(RatingStepBase):
    type: Literal["expression"]
    expr: str
    result_type: RatingResultType


class RatingModelCallStep(RatingStepBase):
    type: Literal["model_call"]
    model_ref: ArtifactRef | None = None
    peril_structure_ref: ArtifactRef | None = None
    mode: Literal["exact", "approximation"]
    feature_map: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _exactly_one_ref(self) -> RatingModelCallStep:
        if (self.model_ref is None) == (self.peril_structure_ref is None):
            raise ValueError(
                "a model_call step declares exactly one of model_ref or "
                "peril_structure_ref (FR-RATE-10)"
            )
        return self


class RatingConstraintStep(RatingStepBase):
    type: Literal["constraint"]
    condition: str
    on_violation: Literal["clamp", "decline", "error"]
    clamp_bounds: dict[str, str] | None = None
    reason_code: str


class RatingOutputStep(RatingStepBase):
    type: Literal["output"]
    output_name: str
    rounding: RoundSpec


RatingStep = Annotated[
    RatingInputStep
    | RatingLookupStep
    | RatingTableStep
    | RatingExpressionStep
    | RatingModelCallStep
    | RatingConstraintStep
    | RatingOutputStep,
    Field(discriminator="type"),
]


class SubGraphRef(BaseModel):
    """A versioned sub-graph referenced by a parent algorithm (FR-RATE-6).

    The sub-graph is a versioned artifact (`sub_graph:slug@version`) mounted at a named
    point in the parent's DAG; it is inlined at bundle time (W9-3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ref: ArtifactRef
    mount_point: str


def _as_list(value: str | list[str]) -> list[str]:
    return value if isinstance(value, list) else [value]


def _produced_by(steps: list[RatingStep]) -> dict[str, list[str]]:
    produced: dict[str, list[str]] = {}
    for step in steps:
        for name in _as_list(step.produces):
            produced.setdefault(name, []).append(step.step_id)
    return produced


def _consumed_by(steps: list[RatingStep]) -> dict[str, list[str]]:
    consumed: dict[str, list[str]] = {}
    for step in steps:
        for name in _as_list(step.consumes):
            consumed.setdefault(name, []).append(step.step_id)
    return consumed


class RatingAlgorithm(BaseModel):
    """A Rating Algorithm: the declarative DAG of rating steps (03 §4.1).

    Invariants (spec §4.1): the DAG is acyclic; every `consumes` name is produced by
    exactly one upstream step; every declared output has an `output` step; no step is
    unreachable from an `input` and unreferenced by an `output` (FR-RATE-1). Enforced
    here at the shape level; the strict save-time validation (types, determinism) is
    W9-2.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    version: int = Field(ge=1)
    input_contract: list[InputContractField]
    outputs: list[AlgorithmOutput]
    steps: list[RatingStep]
    sub_graphs: list[SubGraphRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def _graph_invariants(self) -> RatingAlgorithm:
        steps = self.steps
        ids = [s.step_id for s in steps]
        if len(ids) != len(set(ids)):
            raise ValueError("every step_id is unique (FR-RATE-4)")

        produced = _produced_by(steps)
        consumed = _consumed_by(steps)

        # FR-RATE-3: every declared output has an output step.
        output_steps = {s.output_name for s in steps if isinstance(s, RatingOutputStep)}
        for out in self.outputs:
            if out.name not in output_steps:
                raise ValueError(
                    f"declared output {out.name!r} has no output step (FR-RATE-3)"
                )

        # Build the dependency graph: edge A -> B when B consumes a name A produces.
        # A step never depends on itself, even when it re-produces a name it consumed
        # (the clamp pattern) — the self-edge is excluded.
        dependencies: dict[str, set[str]] = {s.step_id: set() for s in steps}
        for step in steps:
            for name in _as_list(step.consumes):
                producers = produced.get(name)
                if not producers:
                    raise ValueError(
                        f"step {step.step_id!r} consumes undefined value {name!r} "
                        "(FR-RATE-1)"
                    )
                dependencies[step.step_id].update(
                    pid for pid in producers if pid != step.step_id
                )

        # Kahn's algorithm — a cycle fails (FR-RATE-1).
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
            raise ValueError("the rating DAG contains a cycle (FR-RATE-1)")
        position = {sid: i for i, sid in enumerate(order)}
        step_by_id = {s.step_id: s for s in steps}

        # A value may be re-produced only as a chain: each producer after the first
        # consumes the name, so the value has exactly one *effective* producer (the last
        # in topological order). Two unrelated producers of the same name are ambiguous
        # (FR-RATE-1). This is what lets a `constraint` clamp a value in place: it
        # consumes the value and re-produces it, ordered after the original producer.
        for name, producers in produced.items():
            if len(producers) < 2:
                continue
            ordered = sorted(producers, key=lambda pid: position[pid])
            for _prev, nxt in pairwise(ordered):
                if name not in _as_list(step_by_id[nxt].consumes):
                    raise ValueError(
                        f"value {name!r} is produced by {len(producers)} steps that do "
                        "not form a single re-production chain (FR-RATE-1)"
                    )

        # No orphan: a step unreachable from an `input` AND unreferenced by an `output`.
        reachable_from_input = self._reachable(
            {s.step_id for s in steps if isinstance(s, RatingInputStep)},
            step_by_id, produced, consumed,
        )
        feeds_output = self._reaches_output(
            {s.step_id for s in steps if isinstance(s, RatingOutputStep)},
            step_by_id, produced, consumed,
        )
        for step in steps:
            if step.step_id not in reachable_from_input and step.step_id not in feeds_output:
                raise ValueError(
                    f"step {step.step_id!r} is unreachable from any input and referenced "
                    "by no output (FR-RATE-1)"
                )
        return self

    @staticmethod
    def _reachable(
        start: set[str],
        step_by_id: dict[str, RatingStep],
        produced: dict[str, list[str]],
        consumed: dict[str, list[str]],
    ) -> set[str]:
        """Steps reachable from `start`, following produces -> consumes edges."""
        seen: set[str] = set()
        queue = list(start)
        while queue:
            sid = queue.pop()
            if sid in seen:
                continue
            seen.add(sid)
            for name in _as_list(step_by_id[sid].produces):
                for consumer in consumed.get(name, []):
                    queue.append(consumer)
        return seen

    @staticmethod
    def _reaches_output(
        start: set[str],
        step_by_id: dict[str, RatingStep],
        produced: dict[str, list[str]],
        consumed: dict[str, list[str]],
    ) -> set[str]:
        """Steps that feed (transitively) an output step, walking consumers -> producers."""
        seen: set[str] = set()
        queue = list(start)
        while queue:
            sid = queue.pop()
            if sid in seen:
                continue
            seen.add(sid)
            for name in _as_list(step_by_id[sid].consumes):
                for producer in produced.get(name, []):
                    queue.append(producer)
        return seen


class AlgorithmStepChange(BaseModel):
    """One changed field on a step that exists in both versions (FR-RATE-7)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str
    field: str
    before: Any = None
    after: Any = None


class AlgorithmTableRepoint(BaseModel):
    """A `table` or `lookup` step whose artifact reference changed (FR-RATE-7)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str
    field: str
    before: ArtifactRef
    after: ArtifactRef


class AlgorithmDiff(BaseModel):
    """The structural diff between two algorithm versions (FR-RATE-7)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    added_steps: list[str] = Field(default_factory=list)
    removed_steps: list[str] = Field(default_factory=list)
    changed_steps: list[AlgorithmStepChange] = Field(default_factory=list)
    repointed_tables: list[AlgorithmTableRepoint] = Field(default_factory=list)
    input_contract_changed: bool = False
    outputs_changed: bool = False

    @property
    def summary(self) -> str:
        parts: list[str] = []
        if self.added_steps:
            parts.append(f"{len(self.added_steps)} step(s) added")
        if self.removed_steps:
            parts.append(f"{len(self.removed_steps)} step(s) removed")
        if self.changed_steps:
            parts.append(f"{len(self.changed_steps)} field change(s)")
        if self.repointed_tables:
            parts.append(f"{len(self.repointed_tables)} table(s) re-pointed")
        if self.input_contract_changed:
            parts.append("input contract changed")
        if self.outputs_changed:
            parts.append("outputs changed")
        return ", ".join(parts) if parts else "no structural change"


def diff_algorithms(old: RatingAlgorithm, new: RatingAlgorithm) -> AlgorithmDiff:
    """The structural diff between two algorithm versions (FR-RATE-7).

    Names steps added, removed, or changed field-by-field, and tables re-pointed
    (a `table`/`lookup` step's artifact reference changed). The diff is attached to
    the approval request by the API slice (W9-2/W9-3); this function computes it.
    """
    old_by_id = {s.step_id: s for s in old.steps}
    new_by_id = {s.step_id: s for s in new.steps}

    added = sorted(set(new_by_id) - set(old_by_id))
    removed = sorted(set(old_by_id) - set(new_by_id))

    changes: list[AlgorithmStepChange] = []
    repoints: list[AlgorithmTableRepoint] = []
    for sid in sorted(set(old_by_id) & set(new_by_id)):
        o, n = old_by_id[sid], new_by_id[sid]
        if isinstance(o, RatingTableStep) and isinstance(n, RatingTableStep):
            o_ref: ArtifactRef | None = o.rate_table_ref
            n_ref: ArtifactRef | None = n.rate_table_ref
            field = "rate_table_ref"
        elif isinstance(o, RatingLookupStep) and isinstance(n, RatingLookupStep):
            o_ref = o.reference_table_ref
            n_ref = n.reference_table_ref
            field = "reference_table_ref"
        else:
            o_ref = n_ref = None
            field = ""
        if o_ref is not None and n_ref is not None and o_ref != n_ref:
            repoints.append(
                AlgorithmTableRepoint(step_id=sid, field=field, before=o_ref, after=n_ref)
            )
        o_dump, n_dump = o.model_dump(), n.model_dump()
        for key in sorted(set(o_dump) | set(n_dump)):
            if o_dump.get(key) != n_dump.get(key):
                changes.append(
                    AlgorithmStepChange(
                        step_id=sid, field=key, before=o_dump.get(key), after=n_dump.get(key)
                    )
                )

    return AlgorithmDiff(
        added_steps=added,
        removed_steps=removed,
        changed_steps=changes,
        repointed_tables=repoints,
        input_contract_changed=old.input_contract != new.input_contract,
        outputs_changed=old.outputs != new.outputs,
    )
