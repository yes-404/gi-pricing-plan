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
from typing import Annotated, Any, Final, Literal
from uuid import UUID

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    model_validator,
)

from model_schema.refs import ArtifactRef, BlobRef, Slug


class RatingVersionStatus(StrEnum):
    """The lifecycle of a rating version (03 §3.4, FR-RATE-23).

    W9-3 builds through `approved`; `live` and `retired` are declared here because they
    are part of the lifecycle (DP3), but their transitions belong to the deployment
    slice W14 — `live` is a property of a Deployment, not of the version.
    """

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    LIVE = "live"
    RETIRED = "retired"


#: The lifecycle, as data rather than scattered `if` statements. `draft` may skip review
#: straight to `approved` only where the caller is an approver deciding in one step; the
#: normal path goes through `review`. `live` and `retired` are unreachable here — their
#: transitions are W14's, because FR-RATE-23 makes `live` a property of a Deployment.
VALID_RATING_VERSION_TRANSITIONS: dict[
    RatingVersionStatus, frozenset[RatingVersionStatus]
] = {
    RatingVersionStatus.DRAFT: frozenset(
        {RatingVersionStatus.REVIEW, RatingVersionStatus.APPROVED}
    ),
    RatingVersionStatus.REVIEW: frozenset({RatingVersionStatus.APPROVED}),
    RatingVersionStatus.APPROVED: frozenset(),
    RatingVersionStatus.LIVE: frozenset(),
    RatingVersionStatus.RETIRED: frozenset(),
}


class Pins(BaseModel):
    """The exact artifact pins of a Rating Version (03 §4.3, FR-RATE-22).

    Nothing is unpinned: every rate table a `table` step references, every model or peril
    structure a `model_call` references, every reference table a `lookup` references, and
    every custom objective reachable from a `model_call` is pinned by exact version.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rate_tables: list[ArtifactRef] = Field(default_factory=list)
    models: list[ArtifactRef] = Field(default_factory=list)
    reference_tables: list[ArtifactRef] = Field(default_factory=list)
    custom_objectives: list[ArtifactRef] = Field(default_factory=list)


class BundleMetadata(BaseModel):
    """The compiled Bundle's identity (03 §4.3, FR-RATE-24): a reproducible content hash,
    and the blob key the serialised bundle was stored under.

    **`content_hash` and `blob_sha256` are hashes of different things, and their patterns
    keep them apart on purpose.** `content_hash` is reproducible from the graph and pins
    (FR-RATE-24) and carries a `sha256:` prefix. `blob_sha256` is the blob store's content
    address for the serialised bundle and is bare hex, matching `BlobRef.sha256`. Neither
    value validates into the other's field, so passing one where the other belongs is
    refused loudly at the boundary rather than warned about in a comment (Ruling 37 §3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    content_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    bytes: int = Field(ge=0)
    compiled_at: datetime
    #: The blob store key for the serialised `Bundle`, so a Rating Version resolves to its
    #: compiled form through its own metadata rather than through Job history — which is an
    #: operational record with its own pruning, and would make the version unresolvable the
    #: day it is trimmed (Ruling 37 §2).
    #:
    #: **Nullable because of `to_schema`, not because legacy rows are tolerated**
    #: (Ruling 37 §3). `rating_versions.to_schema` runs
    #: `BundleMetadata.model_validate(row.bundle) if row.bundle else None` on *every* read of
    #: a rating version — the list and get routes, and the create and submit paths. A required
    #: field would turn one keyless row into a hard validation failure of all of them, not
    #: merely a failed scoring attempt. Nullable keeps the blast radius at the one thing that
    #: actually needs the key.
    #:
    #: That no such row exists is a *consequence*, not the reason: `row.bundle` has a single
    #: writer, the compile path, so no keyless-but-compiled row exists today and no migration
    #: or back-fill is owed. That does not license making the field required — a back-fill
    #: would empty today's population, not remove the failure mode above, which returns for
    #: any keyless row that ever appears.
    blob_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")] | None = None


class RatingVersionEvidence(BaseModel):
    """The evidence an `approved` version carries (03 §4.3, FR-RATE-40)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    regression_suite_run_id: UUID | None = None
    dislocation_run_id: UUID | None = None
    gipp_check_id: UUID | None = None
    structural_diff_blob: str | None = None


#: The model reference mode (FR-RATE-60): the version declares it, and every `model_call`
#: step's `mode` must equal it.
ModelReferenceMode = Literal["exact", "approximation"]


class RatingVersion(BaseModel):
    """A Rating Version (03 §4.3) — the artifact a rating algorithm approves against.

    W9-3 widens the Phase 1b subset with the full contract: `algorithm_ref`, the exact
    `pins` (FR-RATE-22), `model_reference_mode` (FR-RATE-60), the effective dates
    (FR-RATE-26), the compiled `bundle` (FR-RATE-24), the `change_summary`
    (FR-RATE-27), `evidence`, and `approval_request_id`. The Phase 1b fields stay:
    `model_ref` is the single pinned approved Model the exit demo carries.
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
    #: The widened §4.3 contract (W9-3). `None` means "not yet compiled/pinned" so the
    #: Phase 1b subset keeps parsing.
    algorithm_ref: ArtifactRef | None = None
    pins: Pins | None = None
    model_reference_mode: ModelReferenceMode = "exact"
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    bundle: BundleMetadata | None = None
    change_summary: str | None = None
    evidence: RatingVersionEvidence | None = None
    approval_request_id: UUID | None = None


def check_model_reference_mode(version: RatingVersion, algorithm: RatingAlgorithm) -> None:
    """FR-RATE-60: every `model_call` step's `mode` equals the version's declared mode.

    Raises `ValueError` on the first mismatch, so a version whose steps disagree with its
    `model_reference_mode` is refused before it can compile.
    """
    for step in algorithm.steps:
        if isinstance(step, RatingModelCallStep) and step.mode != version.model_reference_mode:
            raise ValueError(
                f"model_call step {step.step_id!r} declares mode {step.mode!r}, but the "
                f"version declares {version.model_reference_mode!r} (FR-RATE-60)"
            )


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


# ---------------------------------------------------------------------------
# Rate Tables (03 §3.3, FR-RATE-14..21, FR-RATE-62) — versioned typed tables
# of factors and constants that actuaries edit when making a rate change.
#
# W10-1 adds RateTable and RateTableVersion to model-schema: keys, value
# column, storage mode (rows vs parquet), immutability invariants, and
# seeding metadata. W10-2 adds SeededFrom and RateTableDiff. W10-3 reshapes
# RateTableVersion to the 03 §4.2 wire form and adds the BulkOperation record
# (04 §4.4) and the import verdict/preview (03 §5.2).
# ---------------------------------------------------------------------------


class RateTableKeyType(StrEnum):
    """Valid types for a rate table key."""

    INT = "int"
    STRING = "string"
    DATE = "date"
    BOOL = "bool"


class RateTableValueType(StrEnum):
    """Valid types for a rate table value (FR-RATE-14, 03 §3.3)."""

    RELATIVITY = "relativity"
    MONEY_MINOR = "money_minor"
    PERCENTAGE = "percentage"
    COUNT = "count"


class RateTableStorageMode(StrEnum):
    """Storage mode for rate table cells (FR-RATE-62, 03 §3.3).

    `rows` is the default for small tables (< 250k cells); `parquet` is used
    for larger tables. Once written, the storage mode is immutable with the version.
    """

    ROWS = "rows"
    PARQUET = "parquet"


class RateTableKey(BaseModel):
    """A key column declaration (FR-RATE-14): name, type, optional banding reference."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    type: RateTableKeyType
    banding_ref: ArtifactRef | None = None


class RateTableValue(BaseModel):
    """A value column declaration (FR-RATE-14): name, type, unit, optional bounds."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    type: RateTableValueType
    unit: str
    min: Decimal | int | None = None
    max: Decimal | int | None = None


class RateTable(BaseModel):
    """A Rate Table definition (FR-RATE-14, FR-RATE-21, 03 §3.3).

    A typed table with declared key columns (each bound to a Factor or banded input),
    a declared value column with type and unit, an optional default row, and a
    rateable/diagnostic flag.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    version: int = Field(ge=1)
    rateable: bool
    storage: RateTableStorageMode
    keys: list[RateTableKey]
    value: RateTableValue
    default_row: dict[str, Any] | None = None


class SeededFrom(BaseModel):
    """The seed origin of a rate table version (03 §4.2, FR-RATE-16).

    The pinned source model reference and the timestamp at which the relativities were
    imported, so "how far have we moved from the technical rate?" is answerable by
    diffing against this origin.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_ref: ArtifactRef
    seeded_at: datetime


class RateTableDiff(BaseModel):
    """A cell-level diff between two rate table versions (03 §4.2, FR-RATE-17).

    `changed_cells` is the number of cells whose value differs. The two percentages are
    `None` where there is nothing to compare (no cells, or no cell has a non-zero
    baseline); percentages are Decimals, serialised as strings, never JSON floats (R2).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    changed_cells: int = Field(ge=0)
    max_abs_change_pct: Decimal | None = None
    exposure_weighted_mean_change_pct: Decimal | None = None


#: The key filter of 03 §5.2: exact-value match over the table's declared keys.
KeyFilter = dict[str, list[str]]


class BulkOperationResult(BaseModel):
    """The outcome of a bulk operation (04 §4.4): what changed and what it created."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    changed_cells: int = Field(ge=0)
    new_version: ArtifactRef


class BulkOperationBase(BaseModel):
    """The fields every BulkOperation carries (04 §4.4): applied_to and result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    applied_to: ArtifactRef
    result: BulkOperationResult


class UpliftTableParameters(BaseModel):
    """`uplift_table`'s parameters (04 §4.4): the percentage, applied to every cell."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    percentage: Decimal


class UpliftByFilterParameters(BaseModel):
    """`uplift_by_filter`'s parameters (04 §4.4): the percentage plus the key filter."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    percentage: Decimal
    filter: KeyFilter


class FloorAndCapParameters(BaseModel):
    """`floor_and_cap`'s parameters (04 §4.4): the clamp bounds, decimal strings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    floor: Decimal
    cap: Decimal


class RebaseToLevelParameters(BaseModel):
    """`rebase_to_level`'s parameters (04 §4.4): the reference level that becomes 1.0."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    base_level: KeyFilter


class UpliftTableOperation(BulkOperationBase):
    kind: Literal["uplift_table"]
    parameters: UpliftTableParameters


class UpliftByFilterOperation(BulkOperationBase):
    kind: Literal["uplift_by_filter"]
    parameters: UpliftByFilterParameters


class FloorAndCapOperation(BulkOperationBase):
    kind: Literal["floor_and_cap"]
    parameters: FloorAndCapParameters


class RebaseToLevelOperation(BulkOperationBase):
    kind: Literal["rebase_to_level"]
    parameters: RebaseToLevelParameters


#: The BulkOperation record (04 §4.4), discriminated on `kind`. A version created by a
#: bulk operation carries it as `created_by_operation` (03 §4.2).
BulkOperation = Annotated[
    UpliftTableOperation
    | UpliftByFilterOperation
    | FloorAndCapOperation
    | RebaseToLevelOperation,
    Field(discriminator="kind"),
]

#: The wire-parse path for a BulkOperation payload — dict in, member out. An
#: `Annotated` union alias is not directly callable, so the boundary parses through
#: the adapter (the `MODEL_SPEC_ADAPTER` precedent in modelling.py).
BULK_OPERATION_ADAPTER: Final[TypeAdapter[BulkOperation]] = TypeAdapter(BulkOperation)


class ImportVerdict(BaseModel):
    """The source identity of a version created by import (03 §4.2, 03 §5.2).

    `round_trip` is the strict verdict: the file parsed back to exactly the cells it was
    exported from, so an import can never silently drop or re-type a cell. `applied_to`
    names the addressed baseline version (the import endpoint addresses `{slug}@{version}`),
    so the seed-lineage inheritance check (03 §4.2) is expressible at save time and
    auditable after.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    filename: str
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    round_trip: Literal["passed"]
    applied_to: ArtifactRef


class ImportPreview(BaseModel):
    """The import preview (03 §5.2): the would-be version's diff plus the verdict."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    diff: RateTableDiff
    created_by_import: ImportVerdict


class RateTableVersion(BaseModel):
    """A Rate Table Version (FR-RATE-15, FR-RATE-62, 03 §4.2).

    An immutable version of one rate table, in the §4.2 wire form: the definition
    (`keys`, `value`, `default_row`), the cells (`rows` for row storage, `cells` as a
    parquet BlobRef above the threshold), the seed origin, and the creation metadata.
    Editing produces a new version with a required change note. The storage mode is
    fixed when the version is written and immutable with it (FR-RATE-62), and a version
    is created by a seed, an operation or an import — never more than one.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    version: int = Field(ge=1)
    rateable: bool
    storage: RateTableStorageMode
    keys: list[RateTableKey]
    value: RateTableValue
    default_row: dict[str, Any] | None = None
    rows: list[dict[str, str | int]] | None = None
    cells: BlobRef | None = None
    change_note: str
    seeded_from: SeededFrom | None = None
    created_by_operation: BulkOperation | None = None
    created_by_import: ImportVerdict | None = None

    @model_validator(mode="after")
    def _cells_match_storage_mode(self) -> RateTableVersion:
        """Cells are inline rows under the threshold, a parquet BlobRef above it."""
        if self.storage == RateTableStorageMode.ROWS:
            if self.rows is None or self.cells is not None:
                raise ValueError(
                    "a rows-stored version carries inline rows and no blob (FR-RATE-62)"
                )
        elif self.rows is not None or self.cells is None:
            raise ValueError(
                "a parquet version addresses its cells by a BlobRef, never inline "
                "rows (FR-RATE-62)"
            )
        return self

    @model_validator(mode="after")
    def _one_creation_path(self) -> RateTableVersion:
        if self.created_by_operation is not None and self.created_by_import is not None:
            raise ValueError(
                "a version is created by an operation or by an import, never both "
                "(03 §4.2)"
            )
        return self
