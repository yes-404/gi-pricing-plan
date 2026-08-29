"""Save-time validation of a `RatingAlgorithm` (03 §5.2, slice W9-2).

`validate_algorithm` returns a list of `ValidationIssue`s for everything the shape
itself cannot refuse: result-type compatibility (FR-RATE-13), deterministic evaluation
(FR-RATE-5) and the four W8-confirmed boundary guards — integer minor units
(FR-RATE-56), guarded division (FR-RATE-57), the decimal scale cap (FR-RATE-58) and
the engine vocabulary (FR-RATE-59).

The graph invariants (acyclic, fully connected, every `consumes` resolved) are enforced
by the `RatingAlgorithm` shape's own validator (W9-1); the API maps those refusals to
`RATING_GRAPH_CYCLIC` / `RATING_GRAPH_UNRESOLVED_REF`. This module adds the checks that
need the expression text and the engine.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, NoReturn, Protocol

import zen
from pydantic import BaseModel, ConfigDict

from model_schema.rating import (
    Pins,
    RatingAlgorithm,
    RatingExpressionStep,
    RatingInputStep,
    RatingOutputStep,
    RatingVersion,
    check_model_reference_mode,
)
from model_schema.refs import ArtifactRef

_NON_DETERMINISTIC: tuple[str, ...] = ("now(", "random(", "rand(", "today(", "clock(")
#: FR-RATE-30: a quote timestamp is an input; `now()` does not exist.
_GUARD_MARKERS: tuple[str, ...] = ("!= 0", "> 0", "== 0", "< 0", "?:", "coalesce(", "if(", "guard")
#: FR-RATE-58 / W8 S1: `rust_decimal` caps the scale at 28.
_SCALE_CAP = 28
_DECIMAL_LITERAL = re.compile(r"\b\d+\.\d+\b")
#: The numeric family — values that may legitimately cross where a number is expected.
_NUMERIC = frozenset({"int", "decimal", "money_minor", "relativity", "percentage", "count"})


class ValidationIssue(BaseModel):
    """One named problem found at save time.

    `code` is the stable machine code the API maps to a problem response; `step_id` and
    `field` locate the offending part of the algorithm.
    """

    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    step_id: str | None = None
    field: str | None = None


def _as_list(value: str | list[str]) -> list[str]:
    return value if isinstance(value, list) else [value]


def assert_integer_minor_round_trip() -> None:
    """FR-RATE-56: money crosses the engine boundary as integer minor units.

    Integers up to 2^53 are exactly representable in the engine's `float64` binding
    (≈ £90 trillion in pence), so the integer form survives the crossing where the
    fractional form does not. This is the startup self-check the requirement names:
    it asserts the round-trip for a representative range, and a machine on which it
    fails must not start.
    """
    for value in (1, 36120, 999_999_999, 2**53 - 1):
        assert int(float(value)) == value, (
            f"integer minor unit {value} does not round-trip through the engine's "
            "float64 binding (FR-RATE-56)"
        )


def _producer_types(algo: RatingAlgorithm) -> dict[str, str]:
    """The statically-known result type of each produced value.

    `input` steps take their type from the input contract; `expression` steps from
    their declared `result_type`. Lookup/table/model_call outputs depend on the pinned
    artifacts, which save-time validation cannot resolve — those stay unknown here and
    are checked at bundle time (W9-3).
    """
    types: dict[str, str] = {}
    input_by_name = {field.name: field for field in algo.input_contract}
    for step in algo.steps:
        if isinstance(step, RatingInputStep):
            contract = input_by_name.get(step.input_name)
            if contract is not None:
                for name in _as_list(step.produces):
                    types[name] = contract.type.value
        elif isinstance(step, RatingExpressionStep):
            for name in _as_list(step.produces):
                types[name] = step.result_type
    return types


def _compatible(producer: str, declared: str) -> bool:
    if producer == declared:
        return True
    # Numeric values are interchangeable at save time; the bundle compilation resolves
    # the exact unit. A string produced into a money_minor output is a clear mismatch.
    return producer in _NUMERIC and declared in _NUMERIC


def _check_result_types(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-RATE-13: every declared output's type is compatible with its producing step."""
    issues: list[ValidationIssue] = []
    types = _producer_types(algo)
    output_by_name = {output.name: output for output in algo.outputs}
    for step in algo.steps:
        if not isinstance(step, RatingOutputStep):
            continue
        declared = output_by_name.get(step.output_name)
        consumed = _as_list(step.consumes)
        if declared is None or not consumed:
            continue
        producer_type = types.get(consumed[0])
        if producer_type is not None and not _compatible(producer_type, declared.type):
            issues.append(
                ValidationIssue(
                    code="RATING_TYPE_MISMATCH",
                    message=(
                        f"output {step.output_name!r} is declared {declared.type!r} but "
                        f"its producing step yields {producer_type!r} (FR-RATE-13)"
                    ),
                    step_id=step.step_id,
                    field="outputs",
                )
            )
    return issues


def _check_determinism(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-RATE-5/30: evaluation is deterministic — no wall-clock, no randomness."""
    issues: list[ValidationIssue] = []
    for step in algo.steps:
        if not isinstance(step, RatingExpressionStep):
            continue
        lowered = step.expr.lower()
        for marker in _NON_DETERMINISTIC:
            if marker in lowered:
                issues.append(
                    ValidationIssue(
                        code="EXPRESSION_NON_DETERMINISTIC",
                        message=(
                            f"expression calls non-deterministic {marker.strip('(')!r} "
                            "(FR-RATE-5/30); a quote timestamp is an input"
                        ),
                        step_id=step.step_id,
                        field="expr",
                    )
                )
                break
    return issues


def _check_division_guards(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-RATE-57: every division in a rateable path carries an explicit zero guard.

    W8 S1 found the engine returns `null` on division by zero and raises a `vmError`
    only when the null is used — so an unguarded division is a silent hazard. This is
    the save-time heuristic: an expression containing `/` must also carry a guard
    construct. The authoritative check is re-run at bundle compilation (W9-3).
    """
    issues: list[ValidationIssue] = []
    for step in algo.steps:
        if not isinstance(step, RatingExpressionStep):
            continue
        expr = step.expr
        if "/" not in expr:
            continue
        if not any(marker in expr for marker in _GUARD_MARKERS):
            issues.append(
                ValidationIssue(
                    code="EXPRESSION_UNGUARDED_DIVISION",
                    message=(
                        "expression divides without an explicit zero guard (FR-RATE-57); "
                        "the engine returns null on division by zero and raises only on use"
                    ),
                    step_id=step.step_id,
                    field="expr",
                )
            )
    return issues


def _check_scale_cap(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-RATE-58: no literal, constant, or bound needs a decimal scale beyond 28."""
    issues: list[ValidationIssue] = []
    for step in algo.steps:
        if not isinstance(step, RatingExpressionStep):
            continue
        for match in _DECIMAL_LITERAL.finditer(step.expr):
            fraction = match.group(0).split(".", 1)[1]
            if len(fraction) > _SCALE_CAP:
                issues.append(
                    ValidationIssue(
                        code="EXPRESSION_SCALE_OVERFLOW",
                        message=(
                            f"literal {match.group(0)!r} needs {len(fraction)} decimal "
                            f"places, beyond rust_decimal's cap of {_SCALE_CAP} (FR-RATE-58)"
                        ),
                        step_id=step.step_id,
                        field="expr",
                    )
                )
    for field in algo.input_contract:
        for bound_name, bound in (("min", field.min), ("max", field.max)):
            exponent = bound.as_tuple().exponent if isinstance(bound, Decimal) else None
            if isinstance(exponent, int) and -exponent > _SCALE_CAP:
                issues.append(
                    ValidationIssue(
                        code="EXPRESSION_SCALE_OVERFLOW",
                        message=(
                            f"input {field.name!r} {bound_name} needs more than "
                            f"{_SCALE_CAP} decimal places (FR-RATE-58)"
                        ),
                        field=f"input_contract.{bound_name}",
                    )
                )
    return issues


def _check_vocabulary(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-RATE-59: every expression compiles against the engine's real vocabulary.

    W8 S1 verified the engine directly; this check does the same thing on every saved
    expression — `zen.compile_expression` fails on a function the engine does not have
    (including the two-argument `min`/`max` forms the spec's own list names).
    """
    issues: list[ValidationIssue] = []
    for step in algo.steps:
        if not isinstance(step, RatingExpressionStep):
            continue
        try:
            zen.compile_expression(step.expr)
        except Exception as exc:
            issues.append(
                ValidationIssue(
                    code="EXPRESSION_INVALID_VOCABULARY",
                    message=(
                        f"expression does not compile against the engine: {exc} "
                        "(FR-RATE-59)"
                    ),
                    step_id=step.step_id,
                    field="expr",
                )
            )
    return issues


def validate_algorithm(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """Save-time validation of a `RatingAlgorithm` (03 §5.2, FR-RATE-13/5/56/57/58/59).

    The graph invariants (FR-RATE-1) are enforced by the `RatingAlgorithm` shape's own
    validator; the API maps those refusals to `RATING_GRAPH_CYCLIC` and
    `RATING_GRAPH_UNRESOLVED_REF`. This function returns every issue the expression text
    and the engine can name.
    """
    issues: list[ValidationIssue] = []
    issues.extend(_check_result_types(algo))
    issues.extend(_check_determinism(algo))
    issues.extend(_check_division_guards(algo))
    issues.extend(_check_scale_cap(algo))
    issues.extend(_check_vocabulary(algo))
    return issues


# ---------------------------------------------------------------------------
# Bundle compilation (03 §4.3, FR-RATE-24/25, slice W9-3).
#
# DP1 (ruled 2026-08-27): the Bundle is the JDM graph plus the pinned artifacts'
# resolved payloads, wrapped by the pricing-core facade. The content hash covers the
# graph and the pinned artifact refs, so it is reproducible from the pins (FR-RATE-24).
# The Bundle is self-contained: sufficient to score with no database access.
# ---------------------------------------------------------------------------

_APPROVED_OR_BETTER = frozenset({"approved", "live", "retired"})

# Ruling 22 (2026-08-29, `docs/plans/2026-08-29-w11-1-2-rate-table-maturity-ruling.md`):
# `rate_table` has no status column to read a real maturity from at all —
# `RateTableVersionRow` carries none — while `06` §2's Governed Artifact row still calls a
# Rate Table Version approval-bearing and FR-OVR-14 requires every pin to be at least as
# mature as the referencing artifact's own state. Exempting the type from the floor below,
# rather than inventing an "approved" the row cannot back, is declared rather than silent,
# and it is provisional: OQ-RATE-7 asks whether `06`'s governance claim or the rate-table
# lifecycle (`03` §3.3, the schema) is the side that needs to change. Membership is
# expected to be temporary — `test_rate_table_version_row_has_no_status_column`
# (`backend/tests/test_rating_version_compile.py`) fails the day a `status` column is
# added to `RateTableVersionRow`, and names this record for revisiting.
# Ruling 28 (2026-08-29, `docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`):
# `rating_algorithm` joins the exemption for the same shape of reason as `rate_table` —
# `RatingAlgorithmRow` (`backend/src/app/db/models.py`) carries no `status` column, so
# the resolver has nothing real to report and now returns the `"no_maturity_concept"`
# sentinel rather than an invented `"approved"`. Unlike `rate_table`, this one carries no
# open question: `06-governance.md` never lists a Rating Algorithm in its Governed
# Artifact enumeration (§2) or its evidence table (§3.3) — it names Rating Algorithm only
# as a role-assignment scope and a dossier section, never as approval-bearing — so the
# exemption is simply true rather than provisional, and there is no `OQ-` to point at.
# `test_rating_algorithm_row_has_no_status_column`
# (`backend/tests/test_rating_version_compile.py`) is the tripwire: it fails the day a
# `status` column is added to `rating_algorithms`, and names this record for revisiting.
_MATURITY_CHECK_EXEMPT = frozenset({"rate_table", "rating_algorithm"})


class ResolvedArtifact(BaseModel):
    """An artifact resolved by a bundle compiler: its maturity and its payload."""

    model_config = ConfigDict(frozen=True)

    status: str
    payload: dict[str, Any]


class ArtifactResolver(Protocol):
    """Resolves a pinned artifact to its payload and maturity (the DB-backed half).

    `compile_bundle` never touches a database; the caller supplies a resolver that
    does. This keeps `pricing-core` standalone (ADR-0001).
    """

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact: ...


class JdmGraph(BaseModel):
    """The algorithm translated to pricing-core's own intermediate graph shape (ADR-0004,
    DP1) — **not** the engine's wire shape (corrected W11 Task 1.3, `runtime.py`'s
    `to_wire`).

    Each step becomes one entry in `nodes`, keyed by `step_id`, carrying its ZEN-usable
    expression and its `produces`/`consumes` lists standing in for edges. This is close to
    what the engine executes, but not it: the real `zen-engine` Python binding wants a node
    *list* plus an explicit *edge* list, with exactly one `inputNode` and one `outputNode`
    — verified live against `zen.ZenEngine().create_decision(...)`, never assumed from this
    docstring's earlier, unqualified claim. `pricing_core.rating.runtime.to_wire` is the
    translation from this shape to that one; trust a live engine call over any prose here,
    this docstring's own history included.
    """

    model_config = ConfigDict(frozen=True)

    slug: str
    version: int
    input_contract: list[dict[str, Any]]
    outputs: list[dict[str, Any]]
    nodes: dict[str, dict[str, Any]]


def to_jdm(algo: RatingAlgorithm) -> JdmGraph:
    """Translate a `RatingAlgorithm` to pricing-core's own `JdmGraph` (ADR-0004) — the
    step towards the engine's wire shape, not that shape itself. See `JdmGraph`'s own
    docstring: `pricing_core.rating.runtime.to_wire` is what a live `zen.ZenEngine` call
    actually needs, verified rather than assumed (W11 Task 1.3)."""
    nodes: dict[str, dict[str, Any]] = {}
    for step in algo.steps:
        step_dump = step.model_dump()
        nodes[step.step_id] = {
            "type": step.type,
            "label": step.label,
            "produces": _as_list(step.produces),
            "consumes": _as_list(step.consumes),
            **{
                k: v
                for k, v in step_dump.items()
                if k not in ("step_id", "label", "produces", "consumes")
            },
        }
    return JdmGraph(
        slug=algo.slug,
        version=algo.version,
        input_contract=[field.model_dump() for field in algo.input_contract],
        outputs=[output.model_dump() for output in algo.outputs],
        nodes=nodes,
    )


class Bundle(BaseModel):
    """A self-contained compiled rating bundle (03 §4.3, FR-RATE-24).

    `graph` and `resolved_payloads` are sufficient to score with no database access
    (NFR-RATE-3); `content_hash` is reproducible from the pins and the graph.
    """

    model_config = ConfigDict(frozen=True)

    algorithm_ref: str
    graph: JdmGraph
    resolved_payloads: dict[str, Any]
    pins: Pins
    content_hash: str
    compiled_at: datetime


def bundle_hash(graph: JdmGraph, pins: Pins) -> str:
    """A reproducible content hash from the graph and the pins (FR-RATE-24).

    The hash covers the graph and the pinned artifact references, excluding `compiled_at`
    and any prior `content_hash` — hashing a timestamp would break reproducibility. Per
    DP1 and FR-RATE-24, the hash is reproducible from the pins and the graph (03 §5.2,
    corrected 2026-08-27, F-W9-3-2).
    """
    canonical = json.dumps(
        {"graph": graph.model_dump(), "pins": pins.model_dump()},
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def _raise_named(code: str, message: str) -> NoReturn:
    raise ValueError(f"{code}: {message}")


async def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle:
    """Compile a pinned `RatingVersion` to a self-contained Bundle (FR-RATE-24/25).

    Validates the whole structure: the algorithm's DAG, references, types, constraints
    and boundary guards (re-checked via `validate_algorithm`), the pins resolve to
    `approved` or better (FR-OVR-14), every `model_call` mode equals the version's
    `model_reference_mode` (FR-RATE-60), and no pinned custom objective is unapproved.
    Raises `ValueError` named with the first failure's code.
    """
    if version.algorithm_ref is None:
        _raise_named(
            "RATING_VERSION_UNPINNED",
            "the rating version has no algorithm_ref (FR-RATE-22)",
        )
    if version.pins is None:
        _raise_named(
            "RATING_VERSION_UNPINNED",
            "the rating version has no pins (FR-RATE-22)",
        )

    resolved_algorithm = await resolver.resolve(version.algorithm_ref)
    algorithm = RatingAlgorithm.model_validate(resolved_algorithm.payload)

    # Ruling 28: FR-RATE-25 clause (2) ("all references resolvable and at a sufficient
    # maturity") named four of five pin kinds — the loop below — and left the algorithm
    # itself unchecked. Checked here, at the point it is already resolved, rather than
    # added to `all_refs`: that list is resolved a second time below, and
    # `version.algorithm_ref` must not be fetched twice.
    algorithm_exempt = version.algorithm_ref.type in _MATURITY_CHECK_EXEMPT
    if not algorithm_exempt and resolved_algorithm.status not in _APPROVED_OR_BETTER:
        _raise_named(
            "PIN_NOT_APPROVED",
            f"{version.algorithm_ref} is {resolved_algorithm.status!r}, not approved or "
            "better (FR-OVR-14)",
        )

    issues = validate_algorithm(algorithm)
    if issues:
        _raise_named(issues[0].code, issues[0].message)
    check_model_reference_mode(version, algorithm)

    payloads: dict[str, Any] = {str(version.algorithm_ref): resolved_algorithm.payload}
    all_refs: list[ArtifactRef] = [
        *version.pins.rate_tables,
        *version.pins.models,
        *version.pins.reference_tables,
        *version.pins.custom_objectives,
    ]
    for ref in all_refs:
        resolved = await resolver.resolve(ref)
        exempt = ref.type in _MATURITY_CHECK_EXEMPT
        if not exempt and resolved.status not in _APPROVED_OR_BETTER:
            _raise_named(
                "PIN_NOT_APPROVED",
                f"{ref} is {resolved.status!r}, not approved or better (FR-OVR-14)",
            )
        payloads[str(ref)] = resolved.payload

    graph = to_jdm(algorithm)
    pins = version.pins
    return Bundle(
        algorithm_ref=str(version.algorithm_ref),
        graph=graph,
        resolved_payloads=payloads,
        pins=pins,
        content_hash=bundle_hash(graph, pins),
        compiled_at=datetime.now(UTC),
    )


__all__ = [
    "ArtifactResolver",
    "Bundle",
    "JdmGraph",
    "ResolvedArtifact",
    "ValidationIssue",
    "assert_integer_minor_round_trip",
    "bundle_hash",
    "compile_bundle",
    "to_jdm",
    "validate_algorithm",
]
