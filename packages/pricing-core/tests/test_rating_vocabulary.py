"""FR-244's enforced allow-list (RL-1312 item 1, RL-1313 DP-G3): the tokenizer's unit tests.

The lists the tokenizer enforces are held as data in `vocabulary.py` and compared, item for item,
with FR-244's amended cell in `docs/specs/03-rating-engine.md` (acceptance 1a).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from pricing_core.rating import vocabulary
from pricing_core.rating.vocabulary import check_allow_list

_SPEC = Path(__file__).resolve().parents[3] / "docs" / "specs" / "03-rating-engine.md"


@pytest.mark.req("FR-244")
@pytest.mark.parametrize("text", [
    "a + b - c * d / e",
    "-a",
    "(a + b) * c",
    "a == b and c != d or not e",
    "a < b",
    "a <= b",
    "a > b",
    "a >= b",
    "a ? b : c",
    "a ?? 0",
    "a ?? b ?? 1.5",
    "true",
    "false",
    "null",
    "channel == 'direct'",
    "min([a, b])",
    "max([a, 0, c + 1])",
    "min([max([x, 0]), 1])",
    "abs(x - 1)",
    "x != null ? x : 0",
    "1.05",
    "number(a)",
    "a * number(b ?? '1.0')",
    "number('1e3') + abs(number(x))",
])
def test_the_ruled_constructs_are_accepted(text: str) -> None:
    assert check_allow_list(text) is None


@pytest.mark.req("FR-244")
@pytest.mark.parametrize(("text", "construct"), [
    ("a % b", "%"),
    ("a ^ b", "^"),
    ("!a", "!"),
    ("a in [1, 2]", "in"),
    ("a not in [1, 2]", "in"),
    ("a[0]", "["),
    ("a.b", "."),
    ("{a: 1}", "{"),
    ("len('x')", "len"),
    ("sum([a, b])", "sum"),
    ("round(a, 2)", "round"),
    ("floor(a)", "floor"),
    ("ceil(a)", "ceil"),
    ("coalesce(a, b)", "coalesce"),
    ("min(a, b)", "min"),
    ("max(a, b)", "max"),
    ("min([[a], b])", "["),
    ("abs([a])", "["),
    ("[a, b]", "["),
    ("abs(a, b)", ","),
    ('"double"', '"'),
    ("'unterminated", "'"),
    ("a = b", "="),
    ("a & b", "&"),
    ("a | b", "|"),
    ("a $ b", "$"),
    ("date('2020-01-01')", "date"),
    ("number()", "number"),
    ("number(a, b)", ","),
    ("1.2.3", "."),
    ("x.5", "."),
])
def test_a_construct_off_the_list_is_refused_and_named(text: str, construct: str) -> None:
    refused = check_allow_list(text)
    assert refused is not None
    assert construct in refused


@pytest.mark.req("FR-244")
def test_a_decimal_point_inside_a_number_is_not_member_access() -> None:
    assert check_allow_list("1.5 + 2.25") is None
    assert check_allow_list("a.5") is not None


# ---------------------------------------------------------------------------
# Acceptance 1a: the tokenizer's lists equal FR-244's text.
# ---------------------------------------------------------------------------


def _fr_244_cell() -> str:
    line = next(
        text for text in _SPEC.read_text(encoding="utf-8").splitlines()
        if text.startswith("| **FR-244** |")
    )
    return line[line.index("**Amended 2026-09-30, `RL-1265` DP-5 and `RL-1312`:**"):]


def _clause(cell: str, start: str, end: str) -> str:
    return cell[cell.index(start) + len(start): cell.index(end)]


def _spans(clause: str) -> list[str]:
    return re.findall(r"`([^`]*)`", clause)


def _spec_lists(cell: str) -> tuple[set[str], set[str], set[str]]:
    """(operators, literal words, functions) read from the amended cell's three clauses."""
    operators: set[str] = set()
    for span in _spans(_clause(cell, "**Operators:**", "**Literals:**")):
        if span == "c ? a : b":
            operators |= {"?", ":"}
        elif "(" in span:  # prose naming the struck `coalesce(a, b)`, not an operator
            continue
        else:
            operators |= {token for token in span.split() if not token.isalpha() or token in
                          {"and", "or", "not"}}
    words = set(_spans(_clause(cell, "**Literals:**", "**Functions:**")))
    listed = _clause(cell, "**Functions:**", "**No rounding function**").split(". ")[0]
    functions = {re.match(r"[a-z]+", span)[0] for span in _spans(listed)}  # type: ignore[index]
    return operators, words, functions


@pytest.mark.req("FR-244")
def test_the_tokenizer_lists_equal_the_amended_spec_text() -> None:
    operators, words, functions = _spec_lists(_fr_244_cell())
    assert set(vocabulary.OPERATORS) == operators
    assert set(vocabulary.LITERAL_WORDS) == words
    assert set(vocabulary.FUNCTIONS) == functions
    assert functions == {"min", "max", "abs", "number"}
    assert {"round", "floor", "ceil"}.isdisjoint(functions)


@pytest.mark.req("FR-244")
def test_a_list_that_differs_from_the_spec_text_fails_the_comparison() -> None:
    """Broken-input proof: an operator added to the tuple and not to the text is detected."""
    operators, _, _ = _spec_lists(_fr_244_cell())
    assert {*vocabulary.OPERATORS, "%"} != operators
    assert {*vocabulary.FUNCTIONS, "round"} != _spec_lists(_fr_244_cell())[2]
