"""FR-144: an expression objective's gradient and hessian, derived at authoring time."""

from __future__ import annotations

import pytest
import sympy

from pricing_core.data.expression_sympy import to_sympy
from pricing_core.data.expressions import GrammarProfile, parse_expression
from pricing_core.modelling.expression_objective import DERIVED_LIMITS, derive

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
