"""One enumerator of authored rating strings, and the tests that keep it the only one.

WK-1178 code slice (PL-1314 acceptance 3a-3c; FD-1317, RL-1313 DP-G2 as decided by the
maintainer on 2026-09-30 at 10:55:40 BST, DP-G5). Four checks once picked their own fields, and
each picked only an `expression` step's `expr`. The class is fixed structurally:

- the matrix (3a): every registered string check against every authored field;
- closure 1 (3b): a new string field on a step model must be classified in one registry;
- closure 2 (3c): a new check, or a check that reads step text itself, fails a test.
"""

from __future__ import annotations

import ast
import inspect
import itertools
import types
import typing
from pathlib import Path
from typing import Annotated, Any, Literal, get_args, get_origin

import pytest
from test_rating_compile import valid_algorithm

import pricing_core.rating.authored as authored_module
import pricing_core.rating.compile as compile_module
import pricing_core.rating.vocabulary as vocabulary_module
from model_schema import rating as rating_schema
from model_schema.rating import RatingAlgorithm, RatingExpressionStep, RatingStep
from pricing_core.rating.authored import (
    EXPRESSION_FIELDS,
    NON_EXPRESSION_FIELDS,
    authored_expression_fields,
)
from pricing_core.rating.compile import (
    ALGORITHM_CHECKS,
    STRING_CHECKS,
    validate_algorithm,
)

# ---------------------------------------------------------------------------
# 3a. The matrix: generated from the two registries, so a new check or field adds its cells.
# ---------------------------------------------------------------------------

#: Each check's planted violation, shaped as a value (no names, so it fits any field), and the
#: code it must return. A registered check missing here fails `test_every_check_has_a_violation`.
_VIOLATIONS: dict[str, tuple[str, str]] = {
    "_check_determinism": ("now()", "EXPRESSION_NON_DETERMINISTIC"),
    "_check_scale_cap": ("0." + "1" * 31, "EXPRESSION_SCALE_OVERFLOW"),
    "_check_division_guards": ("1 / 2", "EXPRESSION_UNGUARDED_DIVISION"),
    "_check_vocabulary": ("(((", "EXPRESSION_INVALID_VOCABULARY"),
    "_check_allow_list": ("1 % 2", "EXPRESSION_INVALID_VOCABULARY"),
}


def _field_id(entry: tuple[type, str]) -> str:
    return f"{entry[0].__name__}.{entry[1]}"


def _plant(entry: tuple[type, str], text: str) -> tuple[RatingAlgorithm, str]:
    """`valid_algorithm()` with `text` planted in the field; returns it and the step's id."""
    cls, name = entry
    data = valid_algorithm()
    step = next(s for s in data["steps"] if s["type"] == _STEP_TYPE[cls])
    current = step[name]
    step[name] = [text] if isinstance(current, list) else (
        {"min": text} if isinstance(current, dict) else text
    )
    return RatingAlgorithm.model_validate(data), step["step_id"]


_STEP_TYPE = {
    cls: cls.model_fields["type"].annotation.__args__[0]  # type: ignore[union-attr]
    for cls, _ in EXPRESSION_FIELDS
}


@pytest.mark.req("FR-274")
def test_every_check_has_a_planted_violation() -> None:
    assert {check.__name__ for check in STRING_CHECKS} <= set(_VIOLATIONS)


@pytest.mark.req("FR-274")
@pytest.mark.parametrize(
    ("check", "entry"),
    [
        pytest.param(check, entry, id=f"{check.__name__}-{_field_id(entry)}")
        for check, entry in itertools.product(STRING_CHECKS, EXPRESSION_FIELDS)
    ],
)
def test_every_check_refuses_its_violation_in_every_authored_field(
    check: Any, entry: tuple[type, str]
) -> None:
    text, code = _VIOLATIONS[check.__name__]
    algorithm, step_id = _plant(entry, text)
    found = [(i.step_id, i.field) for i in validate_algorithm(algorithm) if i.code == code]
    assert any(sid == step_id and (field or "").startswith(entry[1]) for sid, field in found), (
        f"{check.__name__} did not refuse {text!r} in {_field_id(entry)}: {found}"
    )


@pytest.mark.req("FR-274")
def test_the_enumerator_yields_every_authored_string_with_its_field() -> None:
    found = [
        (s.step_id, s.field, s.text)
        for s in authored_expression_fields(RatingAlgorithm.model_validate(valid_algorithm()))
    ]
    assert found == [
        ("s_area", "key_expr[0]", "channel"),
        ("s_area", "as_at", "effective_date"),
        ("s_expense", "key_expr[0]", "channel"),
        ("s_office", "expr", "risk_premium_minor * expense_factor"),
        ("s_minprem", "condition", "office_premium_minor >= 100"),
        ("s_minprem", "clamp_bounds.min", "100"),
        # SL-1345: the payable's own expression step, so the clamp above is placeable
        ("s_payable", "expr", "office_premium_minor * 1"),
    ]


# ---------------------------------------------------------------------------
# 3b. Closure 1: a new authored field cannot escape the enumerator.
# ---------------------------------------------------------------------------


def _carries_str(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is Annotated:
        return _carries_str(get_args(annotation)[0])
    if origin is Literal:
        return False  # a closed set, not authored text
    if origin in (typing.Union, types.UnionType, list, dict):
        return any(_carries_str(arg) for arg in get_args(annotation))
    return annotation is str


def _defining_class(cls: type, name: str) -> type:
    return next(base for base in cls.__mro__ if name in inspect.get_annotations(base))


def _string_fields(classes: list[type]) -> set[tuple[type, str]]:
    """Every (defining class, field) whose annotation carries `str`, over the step models."""
    return {
        (_defining_class(cls, name), name)
        for cls in classes
        for name, info in cls.model_fields.items()
        if _carries_str(info.annotation)
    }


def _unclassified(classes: list[type]) -> list[str]:
    expression = set(EXPRESSION_FIELDS)
    non_expression = set(NON_EXPRESSION_FIELDS)
    walked = _string_fields(classes)
    def ids(entries: set[tuple[type, str]]) -> list[str]:
        return [_field_id(entry) for entry in sorted(entries, key=_field_id)]

    missing = walked - expression - non_expression
    problems = [f"{name}: in neither registry" for name in ids(missing)]
    problems += [f"{name}: in both registries" for name in ids(expression & non_expression)]
    problems += [f"{name}: stale entry, no such string field"
                 for name in ids((expression | non_expression) - walked)]
    return problems


def _step_classes() -> list[type]:
    union = get_args(RatingStep)[0]
    return list(get_args(union))


@pytest.mark.req("FR-274")
def test_every_string_field_of_a_step_is_classified_in_exactly_one_registry() -> None:
    assert len(_step_classes()) == 7
    assert _unclassified(_step_classes()) == []


@pytest.mark.req("FR-274")
def test_a_new_string_field_is_reported_unclassified() -> None:
    """Broken-input proof: a step model gaining `formula: str` fails closure 1."""

    class _WithFormula(RatingExpressionStep):
        formula: str = ""

    problems = _unclassified([*_step_classes(), _WithFormula])
    assert problems == ["_WithFormula.formula: in neither registry"]


@pytest.mark.req("FR-274")
def test_every_non_expression_field_carries_a_reason() -> None:
    assert all(reason.strip() for reason in NON_EXPRESSION_FIELDS.values())
    assert (rating_schema.RatingLookupStep, "as_at") in EXPRESSION_FIELDS
    assert (rating_schema.RatingLookupStep, "as_at") not in NON_EXPRESSION_FIELDS


# ---------------------------------------------------------------------------
# 3c. Closure 2: a new check cannot bypass the enumerator.
# ---------------------------------------------------------------------------

_FIELD_NAMES = frozenset(name for _, name in EXPRESSION_FIELDS)


def _field_reads(source: str) -> list[str]:
    """Attribute reads of an authored field's name (`step.expr`), by line."""
    return [
        f"line {node.lineno}: .{node.attr}"
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Attribute) and node.attr in _FIELD_NAMES
    ]


def _unregistered_checks(source: str, registered: set[str]) -> list[str]:
    return [
        node.name
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith("_check_")
        and node.name not in registered
    ]


def _registered_names() -> set[str]:
    return {check.__name__ for check in (*STRING_CHECKS, *ALGORITHM_CHECKS)}


@pytest.mark.req("FR-274")
@pytest.mark.parametrize("module", [compile_module, vocabulary_module])
def test_no_check_module_reads_an_authored_field_off_a_step(module: types.ModuleType) -> None:
    """Only `authored.py`'s enumerator reads them. `to_jdm` and `runtime.py`, which read the
    fields to wire them into the engine, are the platform's translation and out of scope."""
    assert _field_reads(inspect.getsource(module)) == []


@pytest.mark.req("FR-274")
def test_the_enumerator_is_where_the_fields_are_read() -> None:
    assert Path(inspect.getsourcefile(authored_module) or "").name == "authored.py"
    assert "getattr" in inspect.getsource(authored_module)


@pytest.mark.req("FR-274")
def test_every_check_is_registered_and_validate_algorithm_iterates_the_registries() -> None:
    source = inspect.getsource(compile_module)
    assert _unregistered_checks(source, _registered_names()) == []
    validate = next(
        node for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "validate_algorithm"
    )
    names = {n.id for n in ast.walk(validate) if isinstance(n, ast.Name)}
    assert not {n for n in names if n.startswith("_check_")}
    assert {"STRING_CHECKS", "ALGORITHM_CHECKS", "authored_expression_fields"} <= names


_BROKEN_CHECK = '''
def _check_x(algo):
    return [s.expr for s in algo.steps]
'''


@pytest.mark.req("FR-274")
def test_a_new_check_that_reads_step_text_itself_is_reported_twice() -> None:
    """Broken-input proof: both closure 2 predicates fail on an unregistered `_check_x`."""
    assert _field_reads(_BROKEN_CHECK) == ["line 3: .expr"]
    assert _unregistered_checks(_BROKEN_CHECK, _registered_names()) == ["_check_x"]
