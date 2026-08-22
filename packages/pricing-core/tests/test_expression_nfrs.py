"""NFR-MODEL-8's `eval`/`exec` clause, attempted rather than asserted.

`02` §4.6 puts one grammar behind four callers — `expression` custom objectives
(FR-MODEL-40), `expression` factors (FR-MODEL-6), preparation `derive_expression`
(`01` FR-DATA-10) and `expression` validation checks (`01` §4.5). Only the third is built,
so this is where the shared parser can be tried.

**These are new tests rather than a second marker on `test_prepare.py`.** That file's
hostile-input list (FR-DATA-10) asks *is this string refused*; it catches
`(ExpressionError, SyntaxError)` interchangeably, so it cannot say which parser did the
refusing, and a blacklist that passes is silent about whether `eval` was reached on the way
to the refusal. NFR-MODEL-8 asks the other question — **is `eval`/`exec` ever called** —
and the only test that answers it is one that removes them and watches the accept path
still work. So the two tests below are the clause, and the overlap in the input strings is
incidental.

**The requirement's second clause was met on 2026-08-22.** `ExpressionError` was a bare
`ValueError` with no `lineno` or `col_offset`, so "the parser rejects out-of-grammar input
with a position-accurate error" was untrue; `test_out_of_grammar_input_carries_no_position`
pinned that absence under FR-DATA-10 so the gap was visible in the suite rather than only
in a report. That test is now inverted rather than deleted — the two below assert the
position instead, and the second exists because a position that merely repeats the
expression's own start would satisfy the first without being accurate.

Its third clause — compiled objectives bounded in memory and per-round time (FR-MODEL-48) —
is **half built and owned elsewhere**. Template objectives *are* compiled, on fixed-size
NumPy arrays with no unbounded intermediates, and FR-MODEL-48's NaN/inf abort naming the
round is implemented and carries four markers in `test_objectives.py`. The **per-round
wall-clock budget** is not implemented anywhere; nothing here can test it, and a marker on
this file would claim it.
"""

from __future__ import annotations

import builtins

import polars as pl
import pytest

from pricing_core.data.expressions import (
    ExpressionError,
    compile_expression,
    referenced_columns,
)

FRAME = pl.DataFrame({"premium": [100.0, 250.0], "exposure": [1.0, 0.5]})


@pytest.mark.req("NFR-MODEL-8")
def test_a_valid_expression_compiles_with_eval_and_exec_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NFR-MODEL-8: user-supplied expressions never reach `eval`/`exec`.

    The property is not that hostile strings are refused — a sandbox that refuses ten
    known attacks and evaluates the eleventh passes that test. It is that the accept path
    contains no call to either builtin, and the way to show that is to take them away and
    watch a legitimate expression still compile and still produce the right number.

    Both builtins are replaced, not merely watched, so a call fails the test loudly at the
    call site instead of leaving an assertion at the end that someone can forget to make.
    """

    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError(
            "the expression grammar called eval/exec on user input (NFR-MODEL-8)"
        )

    monkeypatch.setattr(builtins, "eval", refuse)
    monkeypatch.setattr(builtins, "exec", refuse)

    expression = "round(premium / exposure) + abs(premium - 100)"
    assert referenced_columns(expression) == {"premium", "exposure"}
    frame = FRAME.with_columns(compile_expression(expression).alias("derived"))
    assert frame["derived"].to_list() == [100.0, 650.0]


@pytest.mark.req("NFR-MODEL-8")
@pytest.mark.parametrize(
    "expression",
    [
        "eval('1')",
        "exec('x = 1')",
        "__import__('os').system('ls')",
        "compile('1', '<s>', 'eval')",
        "globals()",
        "premium.__class__.__mro__",
        "(lambda: eval('1'))()",
        "[eval(x) for x in premium]",
    ],
)
def test_a_route_to_eval_is_refused_by_the_parser_not_by_python(expression: str) -> None:
    """NFR-MODEL-8: every syntactically valid route to `eval` fails in *this* parser.

    `ExpressionError` specifically, never `SyntaxError`. The distinction is the point:
    a `SyntaxError` means CPython's parser refused the string and this grammar was never
    consulted, which proves nothing about the grammar. Each of these is valid Python — the
    interpreter would run every one of them — and each is refused before a Polars
    expression is built, because the translator has no node type that could build it.
    """
    with pytest.raises(ExpressionError):
        compile_expression(expression)


@pytest.mark.req("FR-DATA-10")
@pytest.mark.req("NFR-MODEL-8")
def test_out_of_grammar_input_carries_its_position() -> None:
    """NFR-MODEL-8's position-accurate clause, which was unmet until 2026-08-22.

    This assertion is the inverse of the one it replaces. `ExpressionError` was a bare
    `ValueError`, so no caller could underline the offending token; the old test pinned
    that absence deliberately rather than leaving it unstated.

    The span is the refused `Subscript` node's own — `premium[0]`, columns 0 to 10 — not
    the enclosing expression's. `ast` reports `lineno` 1-based and the columns 0-based,
    and `ExpressionError` passes both through unchanged.
    """
    with pytest.raises(ExpressionError) as excinfo:
        compile_expression("premium[0] + 1")

    error = excinfo.value
    assert "Subscript" in str(error)
    assert error.lineno == 1
    assert error.col_offset == 0
    assert error.end_col_offset == 10


@pytest.mark.req("NFR-MODEL-8")
def test_the_position_names_the_offending_operator_not_the_whole_expression() -> None:
    """An operator node carries no position of its own, so the parent is what is threaded.

    `ast` gives `lineno`/`col_offset` to `expr` and `stmt` subclasses only — `operator`
    and `cmpop` get none. A refusal that reported the expression's own start would be
    position-*shaped* without being position-*accurate*, which is the failure this test
    exists to catch.
    """
    with pytest.raises(ExpressionError) as excinfo:
        compile_expression("exposure + premium // 2")

    error = excinfo.value
    assert "FloorDiv" in str(error)
    assert error.lineno == 1
    # The `premium // 2` sub-expression starts at column 11, not the expression's 0.
    assert error.col_offset == 11
    assert error.end_col_offset == 23
