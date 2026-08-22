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

**The requirement's second clause is not met and carries no marker here.** `ExpressionError`
is a bare `ValueError` with no `lineno` or `col_offset`, so "the parser rejects
out-of-grammar input with a position-accurate error" is untrue today:
`test_out_of_grammar_input_carries_no_position` below records what the parser does instead,
under FR-DATA-10, so the gap is visible in the suite rather than only in a report.

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
def test_out_of_grammar_input_carries_no_position() -> None:
    """What the parser does today, pinned so the gap is visible in the suite.

    NFR-MODEL-8 also asks for a *position-accurate* error. `ExpressionError` is a bare
    `ValueError`: it names what was refused and where in the *grammar*, never where in the
    string. A caller cannot underline the offending token, and a UI cannot put a caret
    under it.

    Deliberately **not** marked `NFR-MODEL-8`. A marker on this test would report the
    requirement as evidenced when half of it is unbuilt, which is the failure mode
    `CLAUDE.md` §13 rule 1 calls "a marker is a claim, not a proof". It is marked
    FR-DATA-10 — the requirement the behaviour it pins actually belongs to.
    """
    with pytest.raises(ExpressionError) as excinfo:
        compile_expression("premium + missing[0]")
    error = excinfo.value
    assert getattr(error, "lineno", None) is None
    assert getattr(error, "col_offset", None) is None
    assert "Subscript" in str(error)
