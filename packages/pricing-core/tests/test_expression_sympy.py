"""The `objective` profile to SymPy (FR-144's 2026-09-28 amendment; NFR-483)."""

from __future__ import annotations

import builtins
import sys

import pytest
import sympy
from sympy.codegen.cfunctions import expm1, log1p

from pricing_core.data.expression_sympy import to_sympy
from pricing_core.data.expressions import ExpressionError

y, f, w, w_under, w_over, lo, hi = (
    sympy.Symbol(n, real=True) for n in ("y", "f", "w", "w_under", "w_over", "lo", "hi")
)


@pytest.mark.req("FR-144")
def test_the_spec_example_translates_with_where_as_piecewise() -> None:
    loss = to_sympy(
        "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
        parameters=("w_under", "w_over"),
    )
    expected = w * sympy.Piecewise((w_under, sympy.exp(f) < y), (w_over, True)) * (
        y - sympy.exp(f)
    ) ** 2
    assert loss == expected
    assert loss.has(sympy.Piecewise)


@pytest.mark.req("FR-144")
@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("log(y) + exp(f) - sqrt(w)", sympy.log(y) + sympy.exp(f) - sympy.sqrt(w)),
        ("abs(f) / 2", sympy.Abs(f) / 2),
        ("min(y, f) + max(y, f, w)", sympy.Min(y, f) + sympy.Max(y, f, w)),
        ("clip(f, lo, hi)", sympy.Min(sympy.Max(f, lo), hi)),
        ("log1p(f) - expm1(f)", log1p(f) - expm1(f)),
        ("-y ** 2", -(y**2)),
    ],
)
def test_each_function_maps_to_its_sympy_form(source: str, expected: sympy.Expr) -> None:
    assert to_sympy(source, parameters=("lo", "hi")) == expected


@pytest.mark.req("FR-144")
def test_the_strict_refusals_hold_on_the_sympy_path() -> None:
    with pytest.raises(ExpressionError, match="comparison"):
        to_sympy("y > f")


@pytest.mark.req("FR-144")
def test_every_objective_symbol_is_real() -> None:
    """RL-1293 (DP-S1-3 (a)): y, f, w and every parameter are real."""
    loss = to_sympy("w_under * abs(y - f) + w", parameters=("w_under",))
    assert loss.free_symbols
    assert all(s.is_real is True for s in loss.free_symbols)


@pytest.mark.req("FR-144")
def test_the_abs_derivative_is_the_real_one() -> None:
    """RL-1293: with real symbols, d|f|/df has no re, im or unevaluated Derivative.
    Red first: build the symbols without `real=True` and this fails (premise g's complex
    form). The ledger quotes that red."""
    derivative = sympy.diff(to_sympy("w * abs(y - f)"), f)
    assert not derivative.has(sympy.re, sympy.im, sympy.Derivative)
    # The assertion above alone passes vacuously when the symbols are not real: `f` here is
    # real, so it would differentiate with respect to a symbol absent from the loss and
    # return 0. Pin the value too (found by the mutation run, ledger Task 5).
    assert derivative == w * sympy.sign(f - y)


@pytest.mark.req("FR-144")
def test_the_spec_example_gradient_and_hessian_are_reproduced() -> None:
    """RL-1293's third violation. §4.6's printed gradient and hessian are
    algebraically what SymPy derives from this translation. It is compared as expressions,
    not text: Slice 2 owns the canonical text. Spiked on sympy 1.14.0: both differences
    simplify to 0 after `piecewise_fold`."""
    loss = to_sympy(
        "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
        parameters=("w_under", "w_over"),
    )
    e = sympy.exp(f)
    gradient = sympy.Piecewise(
        (2 * w * w_under * (e - y) * e, y > e), (2 * w * w_over * (e - y) * e, True)
    )
    hessian = sympy.Piecewise(
        (2 * w * w_under * (2 * e - y) * e, y > e), (2 * w * w_over * (2 * e - y) * e, True)
    )
    assert sympy.simplify(sympy.piecewise_fold(sympy.diff(loss, f) - gradient)) == 0
    assert sympy.simplify(sympy.piecewise_fold(sympy.diff(loss, f, 2) - hessian)) == 0


def test_a_parameter_cannot_shadow_a_bound_symbol() -> None:
    with pytest.raises(ValueError, match="y, f or w"):
        to_sympy("y", parameters=("y",))


@pytest.mark.req("NFR-483")
def test_the_translation_never_reaches_eval_or_a_string_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The tree is built node by node. With every string-to-code route replaced by a raiser,
    the spec example still translates.

    **The warm-up is required, and the test must pass in isolation** (F7). Python's import
    machinery calls the builtin `exec`, and SymPy imports modules lazily on first use: in a
    fresh process the spec example imports modules such as `sympy.sets.setexpr` on its first
    call. Patching `exec` before that call makes the import itself trip the raiser, and the
    test would then pass only when an earlier test had warmed the imports. So the same
    translation runs once unpatched, and the patched run must import nothing new and give
    the same result. Checked with `uv run pytest <this file> -k never_reaches` in a fresh
    process (Step 5).
    """
    source = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
    warm = to_sympy(source, parameters=("w_under", "w_over"))  # imports SymPy's lazy modules

    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError("user text reached eval/exec/parse_expr (NFR-483)")

    import sympy.parsing.sympy_parser as sympy_parser

    loaded = set(sys.modules)
    monkeypatch.setattr(builtins, "eval", refuse)
    monkeypatch.setattr(builtins, "exec", refuse)
    monkeypatch.setattr(sympy_parser, "parse_expr", refuse)
    assert to_sympy(source, parameters=("w_under", "w_over")) == warm
    assert set(sys.modules) == loaded  # nothing imported under the patch
    # The positive control (F3; CLAUDE.md §13): the raisers are live. A string route
    # through SymPy's own parser trips them. So the translation above passing means it
    # took no such route, not that the patch missed.
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy.sympify("y + 1")
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy_parser.parse_expr("y + 1")


@pytest.mark.req("NFR-483")
@pytest.mark.parametrize(
    "expression",
    ["eval('1')", "__import__('os').system('ls')", "y.__class__", "(lambda: 1)()", "y[0]"],
)
def test_the_sympy_path_refuses_every_route_to_eval(expression: str) -> None:
    """NFR-483 on the objective path itself (F2): `to_sympy` goes through the one parser."""
    with pytest.raises(ExpressionError) as excinfo:
        to_sympy(expression)
    assert excinfo.value.lineno == 1
