"""An `expression` objective's middle layer: derivation and the compilation target (FR-144).

`derive` differentiates the SymPy tree Slice 1's `to_sympy` builds, and prints the result in
02 §4.6's `objective` grammar, so that one parser (`parse_expression`) reads the loss and
its derivatives alike. No string reaches `eval`, `exec`, `compile`, `sympify` or `lambdify`
(NFR-483; 02 §8): the printer walks SymPy nodes, and a later step walks the validated `ast`.

`pricing-core` reads no clock (ADR-703), so `derive` returns the tool and its version and
not a `derived_at`: the backend stamps that.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Any, Final

import sympy
from sympy.codegen.cfunctions import expm1, log1p

from pricing_core.data.expression_sympy import to_sympy
from pricing_core.data.expressions import ExpressionError, ExpressionLimits

__all__ = ["DERIVED_LIMITS", "Derived", "derive", "to_grammar"]

#: DP-S2-2 / DP-S2-7: derived text is parsed under its own limits. Set from the Task 1 spike
#: (RS-, WK-690 S2): the largest derived text measured was 9081 nodes at depth 40 (the
#: hessian of a 19-deep `log1p` chain), and the rule is the maximum times 2, rounded up to a
#: multiple of 100 nodes and 10 depth.
DERIVED_LIMITS: Final = ExpressionLimits(max_nodes=18200, max_depth=80)

_RELATIONS: Final[dict[type, str]] = {
    sympy.Lt: "<",
    sympy.Le: "<=",
    sympy.Gt: ">",
    sympy.Ge: ">=",
    sympy.Eq: "==",
    sympy.Ne: "!=",
}
_CALLS: Final[tuple[tuple[type[sympy.Basic], str], ...]] = (
    (sympy.exp, "exp"),
    (sympy.log, "log"),
    (sympy.Abs, "abs"),
    (log1p, "log1p"),
    (expm1, "expm1"),
    (sympy.Min, "min"),
    (sympy.Max, "max"),
)


@dataclass(frozen=True, slots=True)
class Derived:
    """A loss's gradient and hessian with respect to `f`, as canonical grammar text."""

    gradient: str
    hessian: str
    derivation_tool: str
    derivation_version: str


def derive(loss: str, *, parameters: Collection[str] = ()) -> Derived:
    """Differentiate `loss` twice with respect to `f` (FR-144).

    Each result has its branches lifted outward by `piecewise_fold`, then is printed in the
    objective grammar. The version is read from SymPy at call time (RL-1289).
    """
    tree = to_sympy(loss, parameters=parameters)
    score = sympy.Symbol("f", real=True)
    gradient = sympy.piecewise_fold(sympy.diff(tree, score))
    hessian = sympy.piecewise_fold(sympy.diff(gradient, score))
    return Derived(
        gradient=to_grammar(gradient),
        hessian=to_grammar(hessian),
        derivation_tool="sympy",
        derivation_version=sympy.__version__,
    )


def to_grammar(expr: sympy.Expr) -> str:
    """Print `expr` as text the `objective` profile accepts (DP-S2-2 (a)).

    `DiracDelta` is the almost-everywhere derivative, `0`: the kink stays visible as the
    `where` condition of the function it came from. `sign` and `Heaviside` become `where`.
    A node outside the list raises `ExpressionError` naming its type.
    """
    return _print(expr.replace(sympy.DiracDelta, lambda *_: sympy.Integer(0)))


def _print(e: Any) -> str:
    if isinstance(e, sympy.Symbol):
        return str(e.name)
    if isinstance(e, sympy.Integer):
        return f"({int(e)})" if e < 0 else str(int(e))
    if isinstance(e, sympy.Rational):
        return f"({int(e.p)} / {int(e.q)})" if e.p >= 0 else f"(-{-int(e.p)} / {int(e.q)})"
    if isinstance(e, sympy.Float):
        value = float(e)
        return f"({value!r})" if value < 0 else repr(value)
    if isinstance(e, sympy.Add):
        return " + ".join(f"({_print(a)})" for a in e.args)
    if isinstance(e, sympy.Mul):
        return " * ".join(f"({_print(a)})" for a in e.args)
    if isinstance(e, sympy.Pow):
        base, power = e.args
        return f"({_print(base)}) ** ({_print(power)})"
    for cls, name in _CALLS:
        if isinstance(e, cls):
            return f"{name}({', '.join(_print(a) for a in e.args)})"
    if isinstance(e, sympy.sign):
        x = _print(e.args[0])
        return f"where(({x}) > 0, 1, where(({x}) < 0, -1, 0))"
    if isinstance(e, sympy.Heaviside):
        return f"where(({_print(e.args[0])}) > 0, 1, 0)"
    if isinstance(e, sympy.DiracDelta):
        return "0"
    if isinstance(e, sympy.Piecewise):
        return _piecewise(list(e.args))
    raise ExpressionError(
        f"{type(e).__name__} cannot be printed in the objective grammar"
    )


def _piecewise(pairs: list[Any]) -> str:
    (value, condition), rest = pairs[0], pairs[1:]
    if condition == sympy.true:
        return _print(value)
    if not rest:
        raise ExpressionError("a Piecewise without a final otherwise cannot be printed")
    return _branch(condition, _print(value), _piecewise(rest))


def _branch(condition: Any, then: str, otherwise: str) -> str:
    """`where(condition, then, otherwise)`, one `where` per relation."""
    if isinstance(condition, sympy.And):
        for part in reversed(condition.args):
            then = _branch(part, then, otherwise)
        return then
    if isinstance(condition, sympy.Or):
        for part in reversed(condition.args):
            otherwise = _branch(part, then, otherwise)
        return otherwise
    if isinstance(condition, sympy.Not):
        return _branch(condition.args[0].negated, then, otherwise)
    symbol = _RELATIONS.get(type(condition))
    if symbol is None:
        raise ExpressionError(f"{type(condition).__name__} is not a relation")
    return (
        f"where(({_print(condition.lhs)}) {symbol} ({_print(condition.rhs)}), "
        f"{then}, {otherwise})"
    )
