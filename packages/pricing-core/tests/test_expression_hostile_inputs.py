"""NFR-483 in every profile of 02 §4.6: each route to eval is refused by this parser.

The strings are `test_expression_nfrs.py`'s hostile set and `test_prepare.py`'s, joined.
That file runs them through `recipe` only, and it stays unmodified (only-add). Each is
valid Python, so an `ExpressionError` with a position proves that this grammar refused
it, and not CPython's parser.
"""

from __future__ import annotations

import pytest

from pricing_core.data.expressions import ExpressionError, GrammarProfile, parse_expression

HOSTILE = [
    "eval('1')",
    "exec('x = 1')",
    "__import__('os').system('ls')",
    "compile('1', '<s>', 'eval')",
    "globals()",
    "open('/etc/passwd').read()",
    "premium.__class__",
    "premium.__class__.__mro__",
    "(lambda: 1)()",
    "(lambda: eval('1'))()",
    "[x for x in premium]",
    "[eval(x) for x in premium]",
    "premium[0]",
    "f'{premium}'",
]


@pytest.mark.req("NFR-483")
@pytest.mark.parametrize("profile", list(GrammarProfile))
@pytest.mark.parametrize("expression", HOSTILE)
def test_every_profile_refuses_every_route_to_eval(
    profile: GrammarProfile, expression: str
) -> None:
    with pytest.raises(ExpressionError) as excinfo:
        parse_expression(expression, profile, symbols=frozenset({"premium", "x"}))
    assert excinfo.value.lineno == 1  # refused with a position, by this grammar


@pytest.mark.req("NFR-483")
@pytest.mark.parametrize("profile", list(GrammarProfile))
def test_the_same_parser_accepts_a_legitimate_expression(profile: GrammarProfile) -> None:
    """The positive control: every profile's refusals above are refusals of the input,
    not of everything."""
    parse_expression("abs(premium - x) / 2", profile, symbols=frozenset({"premium", "x"}))
