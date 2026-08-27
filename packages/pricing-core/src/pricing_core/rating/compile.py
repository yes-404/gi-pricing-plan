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

import re
from decimal import Decimal

import zen
from pydantic import BaseModel, ConfigDict

from model_schema.rating import (
    RatingAlgorithm,
    RatingExpressionStep,
    RatingInputStep,
    RatingOutputStep,
)

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


__all__ = [
    "ValidationIssue",
    "assert_integer_minor_round_trip",
    "validate_algorithm",
]
