"""Save-time validation of a `RatingAlgorithm` (03 §5.2, slice W9-2).

`validate_algorithm` returns a list of `ValidationIssue`s for everything the shape
itself cannot refuse: result-type compatibility (FR-227), deterministic evaluation
(FR-216) and the four WK-668-confirmed boundary guards — integer minor units
(FR-273), guarded division (FR-274), the decimal scale cap (FR-275) and
the engine vocabulary (FR-276).

The graph invariants (acyclic, fully connected, every `consumes` resolved) are enforced
by the `RatingAlgorithm` shape's own validator (W9-1); the API maps those refusals to
`RATING_GRAPH_CYCLIC` / `RATING_GRAPH_UNRESOLVED_REF`. This module adds the checks that
need the expression text and the engine.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, NoReturn, Protocol

import zen
from pydantic import BaseModel, ConfigDict, SerializationInfo, field_serializer

from model_schema.modelling import Banding, Factor, FactorIntent, Grouping
from model_schema.perils import LargeLossKind, PerilStructure
from model_schema.rating import (
    AlgorithmOutput,
    Pins,
    RatingAlgorithm,
    RatingConstraintStep,
    RatingExpressionStep,
    RatingInputStep,
    RatingInputType,
    RatingLookupStep,
    RatingModelCallStep,
    RatingOutputStep,
    RatingStep,
    RatingTableStep,
    RatingVersion,
    check_model_reference_mode,
)
from model_schema.refs import ArtifactRef
from model_schema.sub_graphs import SubGraph, SubGraphInputPort
from pricing_core.rating.authored import authored_expression_fields
from pricing_core.rating.inline import inline_mounts, mounted_fragments
from pricing_core.rating.ladder import RUNG_ORDER, output_steps_by_name, rung_output_name
from pricing_core.rating.vocabulary import check_allow_list
from pricing_core.safe_error import CodedError

_NON_DETERMINISTIC: tuple[str, ...] = ("now(", "random(", "rand(", "today(", "clock(")
#: FR-246: a quote timestamp is an input; `now()` does not exist.
_GUARD_MARKERS: tuple[str, ...] = ("!= 0", "> 0", "== 0", "< 0", "if(", "guard")
#: FR-275 / WK-668 S1: `rust_decimal` caps the scale at 28.
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
    """FR-273: money crosses the engine boundary as integer minor units.

    Integers up to 2^53 are exactly representable in the engine's `float64` binding
    (≈ £90 trillion in pence), so the integer form survives the crossing where the
    fractional form does not. This is the startup self-check the requirement names:
    it asserts the round-trip for a representative range, and a machine on which it
    fails must not start.
    """
    for value in (1, 36120, 999_999_999, 2**53 - 1):
        assert int(float(value)) == value, (
            f"integer minor unit {value} does not round-trip through the engine's "
            "float64 binding (FR-273)"
        )


def producer_types(
    steps: Sequence[RatingStep], typed_names: Mapping[str, str]
) -> dict[str, str]:
    """The statically-known result type of each produced value.

    `input` steps take their type from `typed_names`, keyed by the input's name (an
    algorithm's input contract); `expression` and `model_call` steps from their declared
    `result_type` (a `model_call`'s is `decimal` or `money_minor`, FD-1458 / `PL-1464`
    item 15). Lookup and table outputs depend on the pinned artifacts, which save-time
    validation cannot resolve — those stay unknown here and are checked at bundle time
    (W9-3). A later producer of a name overrides an earlier one.
    """
    types: dict[str, str] = {}
    for step in steps:
        if isinstance(step, RatingInputStep):
            declared = typed_names.get(step.input_name)
            if declared is not None:
                for name in _as_list(step.produces):
                    types[name] = declared
        elif isinstance(step, (RatingExpressionStep, RatingModelCallStep)):
            declared_type = step.result_type
            if declared_type is not None:  # a model_call's None is the legacy default
                for name in _as_list(step.produces):
                    types[name] = declared_type
    return types


def _money_model_call_names(steps: Sequence[RatingStep]) -> set[str]:
    """Names whose latest producer is a `money_minor` `model_call` (a later producer wins)."""
    money: set[str] = set()
    for step in steps:
        is_money_call = isinstance(step, RatingModelCallStep) and step.result_type == "money_minor"
        for name in _as_list(step.produces):
            if is_money_call:
                money.add(name)
            else:
                money.discard(name)
    return money


def model_call_money_issues(
    steps: Sequence[RatingStep], outputs: Sequence[tuple[str, str, str, str]]
) -> list[ValidationIssue]:
    """FR-227 (`PL-1464` item 15): a `money_minor` value produced by a `model_call` that feeds
    an output declared other than `decimal` or `money_minor` is refused.

    Scoped to the `model_call` producer on purpose: `_compatible` still treats every numeric
    type as interchangeable, so an `expression` producer keeps today's behaviour. Same
    `(step_id, output name, declared type, feeding name)` rows as `output_type_issues`.
    """
    money = _money_model_call_names(steps)
    return [
        ValidationIssue(
            code="RATING_TYPE_MISMATCH",
            message=(
                f"output {output_name!r} is declared {declared_type!r} but its producing "
                "step is a model_call declared money_minor; a money_minor model_call feeds "
                "a decimal or money_minor output (FR-227)"
            ),
            step_id=step_id,
            field="outputs",
        )
        for step_id, output_name, declared_type, fed_by in outputs
        if fed_by in money and declared_type not in ("decimal", "money_minor")
    ]


def _producer_types(algo: RatingAlgorithm) -> dict[str, str]:
    """`producer_types` over an algorithm: its input contract types its input steps."""
    return producer_types(algo.steps, {f.name: f.type.value for f in algo.input_contract})


def _compatible(producer: str, declared: str) -> bool:
    if producer == declared:
        return True
    # Numeric values are interchangeable at save time; the bundle compilation resolves
    # the exact unit. A string produced into a money_minor output is a clear mismatch.
    return producer in _NUMERIC and declared in _NUMERIC


def output_type_issues(
    types: Mapping[str, str], outputs: Sequence[tuple[str, str, str, str]]
) -> list[ValidationIssue]:
    """FR-227: each declared output's type is compatible with its producing step's.

    Each output is `(step_id to report, output name, declared type, name that feeds it)`.
    An output whose feeding name has no statically-known type is not checked here.
    """
    issues: list[ValidationIssue] = []
    for step_id, output_name, declared_type, fed_by in outputs:
        producer_type = types.get(fed_by)
        if producer_type is not None and not _compatible(producer_type, declared_type):
            issues.append(
                ValidationIssue(
                    code="RATING_TYPE_MISMATCH",
                    message=(
                        f"output {output_name!r} is declared {declared_type!r} but "
                        f"its producing step yields {producer_type!r} (FR-227)"
                    ),
                    step_id=step_id,
                    field="outputs",
                )
            )
    return issues


def _check_result_types(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-227: every declared output's type is compatible with its producing step."""
    output_by_name = {output.name: output for output in algo.outputs}
    outputs: list[tuple[str, str, str, str]] = []
    for step in algo.steps:
        if not isinstance(step, RatingOutputStep):
            continue
        declared = output_by_name.get(step.output_name)
        consumed = _as_list(step.consumes)
        if declared is None or not consumed:
            continue
        outputs.append((step.step_id, step.output_name, declared.type, consumed[0]))
    return [
        *output_type_issues(_producer_types(algo), outputs),
        *model_call_money_issues(algo.steps, outputs),
    ]


def fragment_output_type_issues(
    steps: Sequence[RatingStep],
    input_ports: Sequence[SubGraphInputPort],
    output_ports: Sequence[AlgorithmOutput],
) -> list[ValidationIssue]:
    """FR-227 at create for a Sub-graph: each output port against its producing step.

    Known types are the input ports' declared types, overridden by `expression` steps'
    `result_type` (the rule of `producer_types`). The step reported is the one whose type
    was compared: the last `expression` step producing the port, else the last step
    producing it. An output port no step produces is skipped: the shape refuses it.
    """
    types = {port.name: port.type for port in input_ports}
    types.update(producer_types(steps, {}))
    typed_by: dict[str, str] = {}
    produced_by: dict[str, str] = {}
    for step in steps:
        for name in _as_list(step.produces):
            produced_by[name] = step.step_id
            if isinstance(step, RatingExpressionStep):
                typed_by[name] = step.step_id
    outputs = [
        (typed_by.get(port.name) or produced_by[port.name], port.name, port.type, port.name)
        for port in output_ports
        if port.name in produced_by
    ]
    return [*output_type_issues(types, outputs), *model_call_money_issues(steps, outputs)]


def _check_clamp_placement(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-240 (`RL-1329` §2 step 5, W-c): a clamp the Premium Ladder cannot place is refused.

    A clamp overwrites the name it produces in place, and the ladder states it once, on the
    `constraints` rung, after `optimisation_adjustment` (FR-247). That is truthful only when
    the clamp's produced name is the source of the **last rung present before
    `constraints`**, and the clamp produces the name it consumes. A clamp on the source of
    any other rung (an earlier rung whose later rungs consume the clamped value, or a rung
    after `constraints`) cannot be stated at the `constraints` position without breaking the
    chain; nor can a clamp that produces a rung's source under a different name from the one
    it consumes. Both are decidable from the algorithm alone.

    Reads only `on_violation`, `consumes` and `produces` of a constraint step and the output
    steps' `output_name` and `consumes`, never `expr`, `condition`, `clamp_bounds` or
    `key_expr` (#967's closure 3c (i)).
    """
    output_steps = output_steps_by_name(algo)
    sources: dict[str, str] = {}
    for rung in RUNG_ORDER:
        output_step = output_steps.get(rung_output_name(rung))
        consumed = _as_list(output_step.consumes) if output_step is not None else []
        if rung != "constraints" and consumed:
            sources[rung] = str(consumed[0])
    before = [rung for rung in RUNG_ORDER[: RUNG_ORDER.index("constraints")] if rung in sources]
    placeable = before[-1] if before else None
    issues: list[ValidationIssue] = []
    for step in algo.steps:
        if not (isinstance(step, RatingConstraintStep) and step.on_violation == "clamp"):
            continue
        produced = [str(name) for name in _as_list(step.produces) if name]
        if not produced:
            continue
        consumed_names = [str(name) for name in _as_list(step.consumes) if name]
        for rung_name, source in sources.items():
            if source != produced[0]:
                continue
            if rung_name != placeable:
                reason = (
                    f"rung {rung_name!r} is not the last rung before constraints ({placeable!r})"
                )
            elif not consumed_names or consumed_names[0] != produced[0]:
                reason = f"it produces {produced[0]!r} but consumes {consumed_names[:1]!r}"
            else:
                continue
            issues.append(
                ValidationIssue(
                    code="LADDER_CLAMP_UNPLACEABLE",
                    message=(
                        f"clamp step {step.step_id!r} cannot be placed on the premium "
                        f"ladder: {reason} (FR-240, FR-247)"
                    ),
                    step_id=step.step_id,
                    field="produces",
                )
            )
    return issues


def _check_determinism(text: str) -> tuple[str, str] | None:
    """FR-216/246: evaluation is deterministic — no wall-clock, no randomness."""
    lowered = text.lower()
    for marker in _NON_DETERMINISTIC:
        if marker in lowered:
            return (
                "EXPRESSION_NON_DETERMINISTIC",
                f"expression calls non-deterministic {marker.strip('(')!r} "
                "(FR-216/246); a quote timestamp is an input",
            )
    return None


def _check_division_guards(text: str) -> tuple[str, str] | None:
    """FR-274: every division in a rateable path carries an explicit zero guard.

    WK-668 S1 found the engine returns `null` on division by zero and raises a `vmError`
    only when the null is used — so an unguarded division is a silent hazard. This is
    the save-time heuristic: a string containing `/` must also carry a guard
    construct. `??` and `!= null` are not guards: they mask the null (RL-1312 item 2). The
    authoritative check is re-run at bundle compilation (W9-3).
    """
    if "/" in text and not any(marker in text for marker in _GUARD_MARKERS):
        return (
            "EXPRESSION_UNGUARDED_DIVISION",
            "expression divides without an explicit zero guard (FR-274); "
            "the engine returns null on division by zero and raises only on use",
        )
    return None


def _check_scale_cap(text: str) -> tuple[str, str] | None:
    """FR-275: no literal needs a decimal scale beyond 28."""
    for match in _DECIMAL_LITERAL.finditer(text):
        fraction = match.group(0).split(".", 1)[1]
        if len(fraction) > _SCALE_CAP:
            return (
                "EXPRESSION_SCALE_OVERFLOW",
                f"literal {match.group(0)!r} needs {len(fraction)} decimal "
                f"places, beyond rust_decimal's cap of {_SCALE_CAP} (FR-275)",
            )
    return None


def _check_allow_list(text: str) -> tuple[str, str] | None:
    """FR-244: only the enforced allow-list of operators and functions (RL-1312)."""
    refused = check_allow_list(text)
    if refused is None:
        return None
    return "EXPRESSION_INVALID_VOCABULARY", f"{refused} (FR-244)"


def _check_vocabulary(text: str) -> tuple[str, str] | None:
    """FR-276: the string compiles against the engine's real vocabulary.

    WK-668 S1 verified the engine directly; this check does the same thing on every authored
    string — `zen.compile_expression` fails on a function the engine does not have
    (including the two-argument `min`/`max` forms the spec's own list names).
    """
    try:
        zen.compile_expression(text)
    except Exception as exc:
        return (
            "EXPRESSION_INVALID_VOCABULARY",
            f"expression does not compile against the engine: {exc} (FR-276)",
        )
    return None


def _check_input_bound_scale(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-275: no input bound needs a decimal scale beyond 28."""
    issues: list[ValidationIssue] = []
    for field in algo.input_contract:
        for bound_name, bound in (("min", field.min), ("max", field.max)):
            exponent = bound.as_tuple().exponent if isinstance(bound, Decimal) else None
            if isinstance(exponent, int) and -exponent > _SCALE_CAP:
                issues.append(
                    ValidationIssue(
                        code="EXPRESSION_SCALE_OVERFLOW",
                        message=(
                            f"input {field.name!r} {bound_name} needs more than "
                            f"{_SCALE_CAP} decimal places (FR-275)"
                        ),
                        field=f"input_contract.{bound_name}",
                    )
                )
    return issues


#: The date `score_one` and `score_batch` stamp into every engine context (`score.py`).
STAMPED_DATE = "effective_date"


def _check_lookup_as_at(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-221 (PL-1447 DP-1): a lookup's `as_at` names `effective_date` or a declared `date`
    input. A declared `effective_date` must itself be date-typed, because a declared input
    replaces the stamped date in the engine context. Read through the enumerator (FR-274)."""
    declared = {field.name: field.type for field in algo.input_contract}
    issues: list[ValidationIssue] = []
    for authored in authored_expression_fields(algo):
        if authored.field != "as_at":
            continue
        name = authored.text
        if name not in declared:
            if name == STAMPED_DATE:
                continue
            code = "RATING_GRAPH_UNRESOLVED_REF"
            why = "is neither effective_date nor a declared input"
        elif declared[name] == RatingInputType.DATE:
            continue
        else:
            code = "RATING_TYPE_MISMATCH"
            why = f"is a declared {declared[name].value!s} input, not a date"
        issues.append(
            ValidationIssue(
                code=code,
                message=(
                    f"as_at of lookup step {authored.step_id!r} names {name!r}, "
                    f"which {why} (FR-221)"
                ),
                step_id=authored.step_id,
                field="as_at",
            )
        )
    return issues


#: Each check is a function of ONE string, so it cannot choose which fields it reads
#: (FD-1317). `validate_algorithm` applies every one of these to every authored string.
STRING_CHECKS: tuple[Callable[[str], tuple[str, str] | None], ...] = (
    _check_determinism,
    _check_division_guards,
    _check_scale_cap,
    _check_allow_list,
    _check_vocabulary,
)
#: Checks that read something other than an authored string (an output's type, an input bound).
ALGORITHM_CHECKS: tuple[Callable[[RatingAlgorithm], list[ValidationIssue]], ...] = (
    _check_result_types,
    _check_input_bound_scale,
    _check_clamp_placement,
    _check_lookup_as_at,
)


def validate_algorithm(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """Save-time validation of a `RatingAlgorithm` (03 §5.2, FR-227/216/244/273/274/275/276).

    The graph invariants (FR-212) are enforced by the `RatingAlgorithm` shape's own
    validator; the API maps those refusals to `RATING_GRAPH_CYCLIC` and
    `RATING_GRAPH_UNRESOLVED_REF`. This function returns every issue the authored text
    and the engine can name: every check in `STRING_CHECKS` over every string
    `authored_expression_fields` enumerates (an `expr`, a `condition`, a clamp bound, a
    `key_expr`), then every check in `ALGORITHM_CHECKS`.
    """
    issues: list[ValidationIssue] = []
    for authored in authored_expression_fields(algo):
        for check in STRING_CHECKS:
            found = check(authored.text)
            if found is not None:
                code, message = found
                issues.append(
                    ValidationIssue(
                        code=code,
                        message=f"{authored.field} of step {authored.step_id!r}: {message}",
                        step_id=authored.step_id,
                        field=authored.field,
                    )
                )
    for algorithm_check in ALGORITHM_CHECKS:
        issues.extend(algorithm_check(algo))
    return issues


# ---------------------------------------------------------------------------
# Bundle compilation (03 §4.3, FR-239/240, slice W9-3).
#
# DP1 (ruled 2026-08-27): the Bundle is the JDM graph plus the pinned artifacts'
# resolved payloads, wrapped by the pricing-core facade. The content hash covers the
# graph and the pinned artifact refs, so it is reproducible from the pins (FR-239).
# The Bundle is self-contained: sufficient to score with no database access.
# ---------------------------------------------------------------------------

_APPROVED_OR_BETTER = frozenset({"approved", "live", "retired"})

# RL-856 (2026-08-29,
# `docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-
# declared-and-self-invalidating.md`):
# `rate_table` has no status column to read a real maturity from at all —
# `RateTableVersionRow` carries none — while `06` §2's Governed Artifact row still calls a
# Rate Table Version approval-bearing and FR-20 requires every pin to be at least as
# mature as the referencing artifact's own state. Exempting the type from the floor below,
# rather than inventing an "approved" the row cannot back, is declared rather than silent,
# and it is provisional: OQ-620 asks whether `06`'s governance claim or the rate-table
# lifecycle (`03` §3.3, the schema) is the side that needs to change. Membership is
# expected to be temporary — `test_rate_table_version_row_has_no_status_column`
# (`backend/tests/test_rating_version_compile.py`) fails the day a `status` column is
# added to `RateTableVersionRow`, and names this record for revisiting.
# RL-859 (2026-08-29, `docs/rulings/RL-00859-the-remainder-splits-and-the-split-is-the-answer.md`):
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
# RL-1309 DP-1 item 5 (2026-10-09, WK-1250 Slice 2): `sub_graph` joins the exemption. A Sub-graph
# Version has no status and no approval lifecycle of its own; its change reaches approval inside
# the Rating Version that pins it. `test_sub_graph_version_row_has_no_status_column`
# (`backend/tests/test_rating_version_compile.py`) fails the day a `status` column is added to
# `sub_graph_versions`, and names `RL-1309` for revisiting.
_MATURITY_CHECK_EXEMPT = frozenset({"rate_table", "rating_algorithm", "sub_graph"})


class ResolvedArtifact(BaseModel):
    """An artifact resolved by a bundle compiler: its maturity and its payload."""

    model_config = ConfigDict(frozen=True)

    status: str
    payload: dict[str, Any]
    #: A pinned model's Factors, read at compile and not carried into the Bundle (`PL-1471`
    #: DP-7); a resolver that has none leaves the default.
    factors: tuple[Factor, ...] = ()
    #: A GLM pin's Bandings and Groupings (`PL-1464` DP-1 (a)), loaded beside its Factors.
    #: Unlike `factors` these are written into the Bundle, with the Factors, for a GLM pin
    #: only (FR-239, NFR-491): `predict_glm` needs all three and the runtime has no database.
    bandings: tuple[Banding, ...] = ()
    groupings: tuple[Grouping, ...] = ()
    #: The Model a GLM's `offset.kind == "model"` reads (FR-116, `PL-1464` DP-3 (a)), resolved
    #: the same way, so the runtime computes its linear predictor per quote as `/predict` does.
    offset_source: ResolvedArtifact | None = None


class ArtifactResolver(Protocol):
    """Resolves a pinned artifact to its payload and maturity (the DB-backed half).

    `compile_bundle` never touches a database; the caller supplies a resolver that
    does. This keeps `pricing-core` standalone (ADR-703).
    """

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact: ...


class JdmGraph(BaseModel):
    """The algorithm translated to pricing-core's own intermediate graph shape (ADR-706,
    DP1) — **not** the engine's wire shape (corrected WK-671 Task 1.3, `runtime.py`'s
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
    """Translate a `RatingAlgorithm` to pricing-core's own `JdmGraph` (ADR-706) — the
    step towards the engine's wire shape, not that shape itself. See `JdmGraph`'s own
    docstring: `pricing_core.rating.runtime.to_wire` is what a live `zen.ZenEngine` call
    actually needs, verified rather than assumed (WK-671 Task 1.3)."""
    nodes: dict[str, dict[str, Any]] = {}
    for step in algo.steps:
        step_dump = step.model_dump()
        if step_dump.get("type") == "model_call" and step_dump.get("result_type") is None:
            # The legacy default is not part of the graph: a bundle compiled before the field
            # existed keeps its bytes, its hash and its prices (FR-239; 2026-10-10 00:40:31).
            del step_dump["result_type"]
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
    """A self-contained compiled rating bundle (03 §4.3, FR-239).

    `graph` and `resolved_payloads` are sufficient to score with no database access
    (NFR-491); `content_hash` is reproducible from the pins and the graph.
    """

    model_config = ConfigDict(frozen=True)

    algorithm_ref: str
    graph: JdmGraph
    resolved_payloads: dict[str, Any]
    pins: Pins
    content_hash: str
    compiled_at: datetime

    @field_serializer("pins")
    def _pins_without_an_empty_sub_graphs(
        self, pins: Pins, info: SerializationInfo
    ) -> dict[str, Any]:
        """`Pins` had four lists before WK-1250 Slice 2. A version that pins no sub-graph
        serialises as it always did, so recompiling an existing algorithm gives byte-identical
        bundle bytes, as `bundle_hash` already gives an identical hash (FR-239, ruling X)."""
        dumped = pins.model_dump(mode=info.mode)
        if not dumped["sub_graphs"]:
            del dumped["sub_graphs"]
        return dumped


def bundle_hash(graph: JdmGraph, pins: Pins) -> str:
    """A reproducible content hash from the graph and the pins (FR-239).

    The hash covers the graph and the pinned artifact references, excluding `compiled_at`
    and any prior `content_hash` — hashing a timestamp would break reproducibility. Per
    DP1 and FR-239, the hash is reproducible from the pins and the graph (03 §5.2,
    corrected 2026-08-27, F-W9-3-2).
    """
    pins_dump = pins.model_dump()
    if not pins_dump["sub_graphs"]:
        # `Pins` had four lists before WK-1250 Slice 2. A version that pins no sub-graph hashes
        # as it always did, so every stored `content_hash` stays reproducible from its pins.
        del pins_dump["sub_graphs"]
    canonical = json.dumps(
        {"graph": graph.model_dump(), "pins": pins_dump},
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def _raise_named(code: str, message: str) -> NoReturn:
    raise CodedError(f"{code}: {message}") from None


def _refuse_mount_port_type_mismatch(
    algorithm: RatingAlgorithm, fragments: Mapping[str, SubGraph]
) -> None:
    """FR-227 at compile (`RL-1309` DP-3 item 5): each mapped input port against its producer.

    The parent value a port is mapped to has a statically-known result type only where its
    producer is an `input` or an `expression` step (`producer_types`); any other producer is
    not checked here, as for an output. A port the fragment does not declare is `inline_mounts`'.
    """
    types = _producer_types(algorithm)
    for mount in algorithm.sub_graphs:
        ports = {port.name: port.type for port in fragments[str(mount.ref)].inputs}
        for port, value in mount.inputs.items():
            declared, produced = ports.get(port), types.get(value)
            if declared is None or produced is None:
                continue
            if not _compatible(produced, declared):
                _raise_named(
                    "RATING_TYPE_MISMATCH",
                    f"mount {mount.mount_point!r} maps {value!r}, which yields {produced!r}, to "
                    f"input port {port!r}, declared {declared!r} (FR-227)",
                )


def check_step_refs_pinned(algorithm: RatingAlgorithm, pins: Pins) -> None:
    """Refuse a step ref the pins do not carry at that exact version (FR-237).

    A `table` step's ref must be in `pins.rate_tables`, a `lookup` step's in
    `pins.reference_tables`, and a `model_call` step's `model_ref` or `peril_structure_ref`
    in `pins.models`. The first mismatch in step order raises `RATING_VERSION_UNPINNED`,
    naming the step and the ref. A pin no step names is allowed (FD-1297, DP-F3 (a)).
    """
    for step in algorithm.steps:
        if isinstance(step, RatingTableStep):
            ref, pinned = step.rate_table_ref, pins.rate_tables
        elif isinstance(step, RatingLookupStep):
            ref, pinned = step.reference_table_ref, pins.reference_tables
        elif isinstance(step, RatingModelCallStep):
            model_ref = step.model_ref or step.peril_structure_ref
            assert model_ref is not None  # exactly one is set (FR-222)
            ref, pinned = model_ref, pins.models
        else:
            continue
        if ref in pinned:
            continue
        other = next((p for p in pinned if (p.type, p.slug) == (ref.type, ref.slug)), None)
        _raise_named(
            "RATING_VERSION_UNPINNED",
            f"step {step.step_id!r} names {ref}, which the rating version's pins do not "
            "carry at that exact version"
            + (f" (pinned at {other} instead)" if other is not None else "")
            + " (FR-237)",
        )


async def _refuse_unapproved_objectives(
    version: RatingVersion,
    payloads: dict[str, Any],
    resolver: ArtifactResolver,
    component_refs: Sequence[ArtifactRef] = (),
) -> None:
    """FR-240's "transitively reachable": a pinned model's own custom objective (`PL-1471`).

    One hop: a GBM's `spec.objective` with `kind: custom` is resolved and held to the same
    floor as a direct pin, `deprecated` included (`02` OQ-609, DP-5). A payload with no
    `spec` names no objective. The objective is checked and not embedded, so `bundle_hash`
    is unchanged (FR-239). A pinned Peril Structure's component models are walked as a pinned
    model is (`component_refs`, `RL-1459` DP-A3-3 (a)); the structure itself has no `spec`.
    """
    assert version.pins is not None
    for model_ref in (*version.pins.models, *component_refs):
        spec = payloads[str(model_ref)].get("spec")
        objective = spec.get("objective") if isinstance(spec, dict) else None
        if not isinstance(objective, dict) or objective.get("kind") != "custom":
            continue
        objective_ref = ArtifactRef.model_validate(objective["ref"])
        status = (await resolver.resolve(objective_ref)).status
        if status not in _APPROVED_OR_BETTER:
            _raise_named(
                "PIN_NOT_APPROVED",
                f"{model_ref} uses {objective_ref}, which is {status!r}, not approved or "
                "better (FR-240, FR-20)",
            )


async def _refuse_control_factor_keys(
    version: RatingVersion, payloads: dict[str, Any], resolver: ArtifactResolver
) -> None:
    """FR-88 / FR-240: no pinned rate table has a key bound to a `control`-intent Factor.

    Every pinned table's `factor_ref` keys, whatever its `rateable` flag (DP-4: the flag is
    declarative, so the check does not trust it). A payload with no `keys` binds no factor.
    """
    assert version.pins is not None
    for table_ref in version.pins.rate_tables:
        for key in payloads[str(table_ref)].get("keys", ()):
            factor_ref = key.get("factor_ref") if isinstance(key, dict) else None
            if factor_ref is None:
                continue
            factor = (await resolver.resolve(ArtifactRef.model_validate(factor_ref))).payload
            if factor.get("intent") == FactorIntent.CONTROL.value:
                _raise_named(
                    "CONTROL_FACTOR_IN_RATEABLE_PATH",
                    f"{table_ref} key {key.get('name')!r} is bound to {factor_ref}, a "
                    "`control`-intent Factor, which cannot be rated on (FR-88, FR-240)",
                )


def _refuse_control_factor_model_calls(
    algorithm: RatingAlgorithm, resolved_pins: dict[str, ResolvedArtifact]
) -> None:
    """FD 9639 (DP-7): a `model_call` over a model fitted on a `control`-intent Factor.

    Scoring applies every fitted feature's effect and `02` FR-88 lets Rating Versions use
    only `risk` factors, so a pinned model whose `feature_order` holds a `control` Factor's
    slug is refused. A payload with no `fit_result` or `feature_order` binds no factor. A
    `peril_structure_ref` step is checked on each of its component models (`RL-1459`
    DP-A3-3 (a)), which `resolved_pins` holds beside the pins once compile has resolved them.
    """
    for step in algorithm.steps:
        if not isinstance(step, RatingModelCallStep):
            continue
        if step.model_ref is not None:
            models = [step.model_ref]
        else:
            assert step.peril_structure_ref is not None  # exactly one is set (FR-222)
            structure = PerilStructure.model_validate(
                resolved_pins[str(step.peril_structure_ref)].payload
            )
            models = peril_component_refs(structure)
        for model_ref in models:
            pin = resolved_pins[str(model_ref)]
            fit_result = pin.payload.get("fit_result")
            features = fit_result.get("feature_order", ()) if isinstance(fit_result, dict) else ()
            by_slug = {factor.slug: factor for factor in pin.factors}
            for feature in features:
                factor = by_slug.get(feature)
                if factor is not None and factor.intent is FactorIntent.CONTROL:
                    _raise_named(
                        "CONTROL_FACTOR_IN_RATEABLE_PATH",
                        f"{model_ref} was fitted on feature {feature!r}, the "
                        f"`control`-intent Factor {factor.slug}@{factor.version}, which "
                        "cannot be rated on (FR-88, FR-240)",
                    )


def _carry_glm_inputs(payloads: dict[str, Any], resolved: ResolvedArtifact) -> None:
    """Write a GLM pin's Factors, Bandings and Groupings into the Bundle (`PL-1464` DP-1 (a)).

    Each travels under its own `ArtifactRef` string as its `model-schema` class's dump, so the
    Bundle's shape and `bundle_hash` are unchanged: the inputs are fixed by the pinned model
    version. A GBM pin adds nothing (`predict_gbm` reads its features off the frame). A model
    offset's source model is carried the same way, under its own ref (DP-3 (a)).
    """
    if (resolved.payload.get("fit_result") or {}).get("model_type") != "glm":
        return
    for kind, items in (
        ("factor", resolved.factors),
        ("banding", resolved.bandings),
        ("grouping", resolved.groupings),
    ):
        for item in items:
            payloads[str(ArtifactRef(type=kind, slug=item.slug, version=item.version))] = (
                item.model_dump(mode="json")
            )
    source = resolved.offset_source
    if source is not None:
        offset = resolved.payload["spec"]["offset"]
        payloads[str(offset["offset_model_ref"])] = source.payload
        _carry_glm_inputs(payloads, source)


def peril_component_refs(structure: PerilStructure) -> list[ArtifactRef]:
    """A structure's distinct component model refs, in peril order (FR-188)."""
    refs: list[ArtifactRef] = []
    for peril in structure.perils:
        for ref in (peril.frequency_model, peril.severity_model, peril.burning_cost_model):
            if ref is not None and ref not in refs:
                refs.append(ref)
    return refs


def _check_peril_model_calls(algorithm: RatingAlgorithm) -> None:
    """A Peril Structure `model_call` declares exactly one produced name (`RL-1459` DP-A3-1 (c)).

    The step yields the structure's risk premium, one value (FR-188). A second name would
    receive the same value although `03` §4's example declares it a per-peril map, which no
    runtime serves yet (FR-249 is `OQ-1460`), so the step is refused rather than served wrong.
    """
    for step in algorithm.steps:
        if not isinstance(step, RatingModelCallStep) or step.peril_structure_ref is None:
            continue
        names = [step.produces] if isinstance(step.produces, str) else list(step.produces)
        if len(names) > 1:
            _raise_named(
                "BUNDLE_COMPILE_FAILED",
                f"step {step.step_id!r} on {step.peril_structure_ref} declares {len(names)} "
                f"produced names {names}; a Peril Structure model_call yields one value, "
                "the risk premium (FR-222, FR-249)",
            )


async def _resolve_peril_components(
    structure_ref: ArtifactRef,
    payload: dict[str, Any],
    resolver: ArtifactResolver,
    resolved_pins: Mapping[str, ResolvedArtifact],
) -> dict[str, ResolvedArtifact]:
    """Resolve and maturity-check a pinned Peril Structure's component models (FR-240, FR-20).

    Each distinct component ref of `frequency_model`, `severity_model` and
    `burning_cost_model` is resolved once, in peril order, and returned under `str(ref)`; a
    component that is also pinned directly reuses the pin loop's result. A `separate_model`
    peril is refused first (`RL-1459` DP-A3-2 (a)): `assemble_risk_premium` cannot restore it.
    """
    structure = PerilStructure.model_validate(payload)
    for peril in structure.perils:
        if peril.large_loss.kind is LargeLossKind.SEPARATE_MODEL:
            _raise_named(
                "LOSS_TREATMENT_UNIMPLEMENTED",
                f"{structure_ref} peril {peril.peril!r} uses a `separate_model` large-loss "
                "treatment, which no scorer applies yet (FR-189, FR-240)",
            )
    components: dict[str, ResolvedArtifact] = {}
    for peril in structure.perils:
        for ref in (peril.frequency_model, peril.severity_model, peril.burning_cost_model):
            if ref is None or str(ref) in components:
                continue
            resolved = resolved_pins.get(str(ref)) or await resolver.resolve(ref)
            if resolved.status not in _APPROVED_OR_BETTER:
                _raise_named(
                    "PIN_NOT_APPROVED",
                    f"{ref}, the component of peril {peril.peril!r} in {structure_ref}, is "
                    f"{resolved.status!r}, not approved or better (FR-20, FR-240)",
                )
            components[str(ref)] = resolved
    return components


async def compile_bundle(version: RatingVersion, resolver: ArtifactResolver) -> Bundle:
    """Compile a pinned `RatingVersion` to a self-contained Bundle (FR-239/240).

    Validates the whole structure: the algorithm's DAG, references, types, constraints
    and boundary guards (re-checked via `validate_algorithm`), the pins resolve to
    `approved` or better (FR-20), every `model_call` mode equals the version's
    `model_reference_mode` (FR-223), and no custom objective is unapproved, pinned or
    reached through a pinned model (FR-240).
    Every `table`, `lookup` and `model_call` step's ref is pinned at its exact version
    (FR-237, `check_step_refs_pinned`).
    Each sub-graph mount is resolved from the version's pins (`RL-1309` G1) and inlined at its
    mount point (FR-217, `inline_mounts`), and every check above runs over the **inlined**
    algorithm, so a fragment's steps, references and expressions are checked as the parent's.
    Raises `ValueError` named with the first failure's code.
    """
    if version.algorithm_ref is None:
        _raise_named(
            "RATING_VERSION_UNPINNED",
            "the rating version has no algorithm_ref (FR-237)",
        )
    if version.pins is None:
        _raise_named(
            "RATING_VERSION_UNPINNED",
            "the rating version has no pins (FR-237)",
        )

    resolved_algorithm = await resolver.resolve(version.algorithm_ref)
    algorithm = RatingAlgorithm.model_validate(resolved_algorithm.payload)

    # RL-859: FR-240 clause (2) ("all references resolvable and at a sufficient
    # maturity") named four of five pin kinds — the loop below — and left the algorithm
    # itself unchecked. Checked here, at the point it is already resolved, rather than
    # added to `all_refs`: that list is resolved a second time below, and
    # `version.algorithm_ref` must not be fetched twice.
    algorithm_exempt = version.algorithm_ref.type in _MATURITY_CHECK_EXEMPT
    if not algorithm_exempt and resolved_algorithm.status not in _APPROVED_OR_BETTER:
        _raise_named(
            "PIN_NOT_APPROVED",
            f"{version.algorithm_ref} is {resolved_algorithm.status!r}, not approved or "
            "better (FR-20)",
        )

    # Each mounted sub-graph is resolved once, here, and kept for the pin loop below (the same
    # reason as above). A mount whose ref is not pinned is not resolved: `mounted_fragments`
    # refuses it (`RL-1309` G1).
    pins = version.pins
    mounted: dict[str, ResolvedArtifact] = {}
    for mount in algorithm.sub_graphs:
        if mount.ref in pins.sub_graphs and str(mount.ref) not in mounted:
            mounted[str(mount.ref)] = await resolver.resolve(mount.ref)
    fragments = mounted_fragments(
        algorithm, pins, {key: artifact.payload for key, artifact in mounted.items()}
    )
    inlined = inline_mounts(algorithm, fragments)
    _refuse_mount_port_type_mismatch(algorithm, fragments)

    issues = validate_algorithm(inlined)
    if issues:
        _raise_named(issues[0].code, issues[0].message)
    check_model_reference_mode(version, inlined)
    check_step_refs_pinned(inlined, pins)
    _check_peril_model_calls(inlined)

    payloads: dict[str, Any] = {str(version.algorithm_ref): resolved_algorithm.payload}
    all_refs: list[ArtifactRef] = [
        *pins.rate_tables,
        *pins.models,
        *pins.reference_tables,
        *pins.custom_objectives,
        *pins.sub_graphs,
    ]
    resolved_pins: dict[str, ResolvedArtifact] = {}
    for ref in all_refs:
        resolved = mounted.get(str(ref)) or await resolver.resolve(ref)
        exempt = ref.type in _MATURITY_CHECK_EXEMPT
        if not exempt and resolved.status not in _APPROVED_OR_BETTER:
            _raise_named(
                "PIN_NOT_APPROVED",
                f"{ref} is {resolved.status!r}, not approved or better (FR-20)",
            )
        payloads[str(ref)] = resolved.payload
        _carry_glm_inputs(payloads, resolved)
        resolved_pins[str(ref)] = resolved
    component_refs: list[ArtifactRef] = []
    for ref in version.pins.models:
        if ref.type != "peril_structure":
            continue
        components = await _resolve_peril_components(
            ref, resolved_pins[str(ref)].payload, resolver, resolved_pins
        )
        for component_ref, component in components.items():
            payloads[component_ref] = component.payload
            _carry_glm_inputs(payloads, component)
            resolved_pins.setdefault(component_ref, component)
            component_refs.append(ArtifactRef.model_validate(component_ref))
    await _refuse_unapproved_objectives(version, payloads, resolver, component_refs)
    await _refuse_control_factor_keys(version, payloads, resolver)
    _refuse_control_factor_model_calls(inlined, resolved_pins)

    graph = to_jdm(inlined)
    return Bundle(
        algorithm_ref=str(version.algorithm_ref),
        graph=graph,
        resolved_payloads=payloads,
        pins=pins,
        content_hash=bundle_hash(graph, pins),
        compiled_at=datetime.now(UTC),
    )


__all__ = [
    "ALGORITHM_CHECKS",
    "STRING_CHECKS",
    "ArtifactResolver",
    "Bundle",
    "JdmGraph",
    "ResolvedArtifact",
    "ValidationIssue",
    "assert_integer_minor_round_trip",
    "bundle_hash",
    "check_step_refs_pinned",
    "compile_bundle",
    "fragment_output_type_issues",
    "output_type_issues",
    "peril_component_refs",
    "producer_types",
    "to_jdm",
    "validate_algorithm",
]
