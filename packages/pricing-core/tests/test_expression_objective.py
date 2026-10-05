"""FR-144: an expression objective's gradient and hessian, derived at authoring time."""

from __future__ import annotations

import ast
import builtins
import sys

import numpy as np
import pytest
import sympy

from pricing_core.data.expression_sympy import to_sympy
from pricing_core.data.expressions import GrammarProfile, parse_expression
from pricing_core.modelling.expression_objective import DERIVED_LIMITS, compile_kernel, derive

EXAMPLE = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
PARAMS = ("w_under", "w_over")
y, f, w, w_under, w_over = (
    sympy.Symbol(n, real=True) for n in ("y", "f", "w", "w_under", "w_over")
)


def _same(text: str, expected: sympy.Expr) -> bool:
    got = to_sympy(text, parameters=PARAMS)
    return bool(sympy.simplify(sympy.piecewise_fold(got - expected)) == 0)


@pytest.mark.req("FR-144")
def test_the_spec_example_derives_to_the_printed_gradient_and_hessian() -> None:
    """§4.6's `derived` block, compared as expressions (premise j): the text differs in
    form from §4.6's, and the maths must not."""
    d = derive(EXAMPLE, parameters=PARAMS)
    e = sympy.exp(f)
    assert _same(
        d.gradient,
        sympy.Piecewise(
            (2 * w * w_under * (e - y) * e, y > e), (2 * w * w_over * (e - y) * e, True)
        ),
    )
    assert _same(
        d.hessian,
        sympy.Piecewise(
            (2 * w * w_under * (2 * e - y) * e, y > e),
            (2 * w * w_over * (2 * e - y) * e, True),
        ),
    )


@pytest.mark.req("FR-144")
@pytest.mark.parametrize(
    "loss",
    [
        EXAMPLE,
        "w * abs(y - f)",
        "w * clip(f, 0, y) ** 2",
        "w * (exp(f) - y * f)",
        "w * log1p(exp(f)) - w * y * f",
    ],
)
def test_derived_text_is_in_the_objective_grammar(loss: str) -> None:
    """The printer's output is text Slice 1's parser accepts: no sign, Heaviside or
    DiracDelta survives (DP-S2-2 (a))."""
    d = derive(loss, parameters=PARAMS)
    for text in (d.gradient, d.hessian):
        parse_expression(
            text,
            GrammarProfile.OBJECTIVE,
            symbols=frozenset({"y", "f", "w", *PARAMS}),
            limits=DERIVED_LIMITS,
        )
        assert "sign" not in text
        assert "Heaviside" not in text
        assert "DiracDelta" not in text


@pytest.mark.req("FR-144")
def test_the_derivation_version_is_read_from_sympy(monkeypatch: pytest.MonkeyPatch) -> None:
    """RL-1289's second violation: a patched version must be what is recorded."""
    monkeypatch.setattr(sympy, "__version__", "9.9.9")
    d = derive("w * (exp(f) - y * f)")
    assert (d.derivation_tool, d.derivation_version) == ("sympy", "9.9.9")


@pytest.mark.req("FR-144")
def test_derivation_is_deterministic() -> None:
    """The text a reviewer approves must be reproducible: two derivations are identical."""
    assert derive(EXAMPLE, parameters=PARAMS) == derive(EXAMPLE, parameters=PARAMS)


RNG = np.random.default_rng(20260930)
N = 4096
Y = RNG.uniform(0.1, 50.0, N)
F = RNG.uniform(-3.0, 4.0, N)
W = RNG.uniform(0.5, 2.0, N)
VALUES = {"w_under": 2.0, "w_over": 1.0}


def _sympy_values(text: str) -> np.ndarray:
    """SymPy's own numeric evaluation, point by point: slow, and the reference."""
    e = to_sympy(text, parameters=PARAMS).subs({w_under: 2.0, w_over: 1.0})
    return np.array(
        [
            float(e.subs({y: a, f: b, w: c}).evalf())
            for a, b, c in zip(Y[:64], F[:64], W[:64], strict=True)
        ]
    )


@pytest.mark.req("FR-144")
@pytest.mark.req("FR-165")
def test_a_kernel_agrees_with_sympy_and_keeps_the_input_length() -> None:
    d = derive(EXAMPLE, parameters=PARAMS)
    for text in (EXAMPLE, d.gradient, d.hessian):
        out = compile_kernel(text, parameters=VALUES)(Y, F, W)
        assert out.shape == Y.shape
        assert out.dtype == np.float64
        np.testing.assert_allclose(out[:64], _sympy_values(text), rtol=1e-12)


@pytest.mark.req("FR-144")
def test_a_constant_expression_still_has_the_input_length() -> None:
    """FR-165: every intermediate and the result are the input's length."""
    out = compile_kernel("2 + w_under", parameters=VALUES)(Y, F, W)
    assert out.shape == Y.shape
    assert bool(np.all(out == 4.0))


@pytest.mark.req("NFR-483")
def test_a_kernel_is_built_without_a_string_evaluator(monkeypatch: pytest.MonkeyPatch) -> None:
    """Warm first (PL-1295 F7): Python's import machinery calls `exec`, so the patched build
    must import nothing new and give the same numbers.

    `compile` is replaced too, but `ast.parse` calls it with `PyCF_ONLY_AST`: that flag
    builds a tree and runs nothing, and is the one use allowed. Anything else, a string
    compiled to code, trips the raiser.
    """
    warm = compile_kernel(EXAMPLE, parameters=VALUES)(Y, F, W)
    real_compile = builtins.compile

    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError("a string reached a code evaluator (NFR-483)")

    def compile_only_to_a_tree(*args: object, **kwargs: object) -> object:
        flags = args[3] if len(args) > 3 else kwargs.get("flags", 0)
        if not isinstance(flags, int) or not flags & ast.PyCF_ONLY_AST:
            raise AssertionError("a string was compiled to code (NFR-483)")
        return real_compile(*args, **kwargs)  # type: ignore[call-overload]

    import sympy.parsing.sympy_parser as sympy_parser

    loaded = set(sys.modules)
    monkeypatch.setattr(builtins, "eval", refuse)
    monkeypatch.setattr(builtins, "exec", refuse)
    monkeypatch.setattr(builtins, "compile", compile_only_to_a_tree)
    monkeypatch.setattr(sympy, "lambdify", refuse)
    monkeypatch.setattr(sympy_parser, "parse_expr", refuse)
    np.testing.assert_array_equal(compile_kernel(EXAMPLE, parameters=VALUES)(Y, F, W), warm)
    assert set(sys.modules) == loaded
    # The positive controls: each raiser is live.
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy.lambdify(y, y + 1)
    with pytest.raises(AssertionError, match="NFR-483"):
        sympy_parser.parse_expr("y + 1")
    with pytest.raises(AssertionError, match="NFR-483"):
        builtins.compile("1 + 1", "<s>", "eval")


@pytest.mark.req("FR-146")
def test_certify_inverse_link_follows_the_applicability_responses() -> None:
    """One function names the link for certification (and the fit): logit for a probability."""
    from model_schema import ResponseKind
    from pricing_core.modelling.expression_objective import inverse_link_for

    assert inverse_link_for([ResponseKind.CONVERSION, ResponseKind.RETENTION]) == "logistic"
    assert inverse_link_for([ResponseKind.CLAIM_SEVERITY, ResponseKind.BURNING_COST]) == "exp"
    assert inverse_link_for([ResponseKind.CLAIM_COUNT]) == "exp"
