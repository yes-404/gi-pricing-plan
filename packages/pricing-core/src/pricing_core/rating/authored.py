"""The one enumerator of authored rating strings (WK-1178, FD-1317, RL-1313 DP-G5).

Four save-time checks once picked their own fields, and each picked only an `expression` step's
`expr`, so a constraint's `condition`, its `clamp_bounds` and a `table` or `lookup` step's
`key_expr` were never checked (FD-1317). The class is fixed structurally, in three parts:

- `EXPRESSION_FIELDS` declares every field whose text the engine evaluates. It is the only place
  that names them, and `authored_expression_fields` is the only code that reads them off a step;
- `NON_EXPRESSION_FIELDS` lists every other string field of every step model, with its reason;
- `test_rating_authored_fields.py` walks the step schemas so that a new string field must land in
  exactly one registry, and asserts that no check module reads a field off a step itself.

`to_jdm` and `runtime.py` read these fields to wire them into the engine. That is the
platform's translation, not a check, and it is out of scope here.
"""

from __future__ import annotations

from dataclasses import dataclass

from model_schema.rating import (
    RatingAlgorithm,
    RatingConstraintStep,
    RatingExpressionStep,
    RatingInputStep,
    RatingLookupStep,
    RatingModelCallStep,
    RatingOutputStep,
    RatingStepBase,
    RatingTableStep,
)


@dataclass(frozen=True)
class AuthoredString:
    """One authored string: step, field (`expr`, `clamp_bounds.min`, `key_expr[0]`), text."""

    step_id: str
    field: str
    text: str


#: Every field whose text the engine evaluates, as (the class that defines it, the field name).
EXPRESSION_FIELDS: tuple[tuple[type, str], ...] = (
    (RatingLookupStep, "key_expr"),
    (RatingLookupStep, "as_at"),
    (RatingTableStep, "key_expr"),
    (RatingExpressionStep, "expr"),
    (RatingConstraintStep, "condition"),
    (RatingConstraintStep, "clamp_bounds"),
)

#: Every other string-bearing field of every step model, each with why it is not evaluated.
NON_EXPRESSION_FIELDS: dict[tuple[type, str], str] = {
    (RatingStepBase, "step_id"): "an identifier",
    (RatingStepBase, "label"): "display text",
    (RatingStepBase, "note"): "display text",
    (RatingStepBase, "consumes"): "names of upstream values, resolved by the graph invariants",
    (RatingStepBase, "produces"): "names of values this step defines",
    (RatingInputStep, "input_name"): "names a declared input",
    (RatingExpressionStep, "result_type"): (
        "the step's declared result type (FR-227), read by the result-type check and never "
        "evaluated by the engine"
    ),
    (RatingModelCallStep, "feature_map"): "graph value names mapped to model feature names",
    (RatingModelCallStep, "result_type"): (
        "the step's declared result type (FR-227), read by the result-type check and never "
        "evaluated by the engine"
    ),
    (RatingConstraintStep, "reason_code"): "a code recorded on violation",
    (RatingOutputStep, "output_name"): "names a declared output",
}


def authored_expression_fields(algorithm: RatingAlgorithm) -> list[AuthoredString]:
    """Every authored string of every step, in step order, each with its field."""
    found: list[AuthoredString] = []
    for step in algorithm.steps:
        for cls, name in EXPRESSION_FIELDS:
            if not isinstance(step, cls):
                continue
            value = getattr(step, name)
            if isinstance(value, str):
                found.append(AuthoredString(step.step_id, name, value))
            elif isinstance(value, list):
                found.extend(
                    AuthoredString(step.step_id, f"{name}[{i}]", text)
                    for i, text in enumerate(value)
                )
            elif isinstance(value, dict):
                found.extend(
                    AuthoredString(step.step_id, f"{name}.{key}", text)
                    for key, text in value.items()
                )
    return found
