"""02 §4.6's `objective` profile, translated to a SymPy expression (FR-144).

Translation, not evaluation: the tree is `parse_expression`'s validated `ast`, and each node
becomes the SymPy object it names. No string reaches `sympify`, `parse_expr`, `lambdify` or
`eval` (NFR-483; 02 §8). The symbols are real (DP-S1-3, RL-1293), so `Abs` differentiates to
`sign`, and the canonical text Slice 2 records is the real-variable one.

A separate module so that the Polars path (`recipe`, `check`) never imports sympy.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Collection, Mapping
from typing import Final

import sympy
from sympy.codegen.cfunctions import expm1, log1p

from pricing_core.data.expressions import (
    DEFAULT_LIMITS,
    ExpressionError,
    ExpressionLimits,
    GrammarProfile,
    parse_expression,
)

__all__ = ["OBJECTIVE_SYMBOLS", "to_sympy"]

#: 02 §4.6: an objective's bound symbols are the label, the raw score and the weight.
OBJECTIVE_SYMBOLS: Final = frozenset({"y", "f", "w"})

_BINARY: Final[Mapping[type[ast.operator], Callable[[sympy.Expr, sympy.Expr], sympy.Expr]]] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
}
_RELATIONS: Final = {
    ast.Eq: sympy.Eq, ast.NotEq: sympy.Ne, ast.Lt: sympy.Lt,
    ast.LtE: sympy.Le, ast.Gt: sympy.Gt, ast.GtE: sympy.Ge,
}


def to_sympy(
    expression: str,
    *,
    parameters: Collection[str] = (),
    limits: ExpressionLimits = DEFAULT_LIMITS,
) -> sympy.Expr:
    """Parse `expression` in the `objective` profile and build its SymPy expression."""
    shadowed = OBJECTIVE_SYMBOLS & set(parameters)
    if shadowed:
        raise ValueError(f"a parameter may not be named y, f or w: {sorted(shadowed)}")
    names = OBJECTIVE_SYMBOLS | frozenset(parameters)
    tree = parse_expression(
        expression, GrammarProfile.OBJECTIVE, symbols=names, limits=limits
    )
    table = {name: sympy.Symbol(name, real=True) for name in names}
    return _build(tree.body, table)


def _build(node: ast.expr, table: Mapping[str, sympy.Symbol]) -> sympy.Expr:
    match node:
        case ast.Constant(value=bool()):
            pass  # refused by the parser; unreachable, and falls through to the raise
        case ast.Constant(value=int() as value):
            return sympy.Integer(value)
        case ast.Constant(value=float() as value):
            return sympy.Float(value)  # sympy.sympify's own mapping of a Python float
        case ast.Name(id=name):
            return table[name]
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return -_build(operand, table)
        case ast.BinOp(left=left, op=op, right=right) if type(op) in _BINARY:
            return _BINARY[type(op)](_build(left, table), _build(right, table))
        case ast.Call(func=ast.Name(id=name), args=args):
            return _call(name, args, table, node)
    raise ExpressionError(f"{type(node).__name__} is not translatable", node=node)


def _call(
    name: str, args: list[ast.expr], table: Mapping[str, sympy.Symbol], node: ast.expr
) -> sympy.Expr:
    if name == "where":
        condition, then, otherwise = args
        assert isinstance(condition, ast.Compare)  # the parser guarantees one comparison
        relation = _RELATIONS[type(condition.ops[0])](
            _build(condition.left, table), _build(condition.comparators[0], table)
        )
        return sympy.Piecewise(
            (_build(then, table), relation), (_build(otherwise, table), True)
        )
    built = [_build(a, table) for a in args]
    match name:
        case "log":
            return sympy.log(built[0])
        case "exp":
            return sympy.exp(built[0])
        case "sqrt":
            return sympy.sqrt(built[0])
        case "abs":
            return sympy.Abs(built[0])
        case "min":
            return sympy.Min(*built)
        case "max":
            return sympy.Max(*built)
        case "clip":
            return sympy.Min(sympy.Max(built[0], built[1]), built[2])
        case "log1p":
            return log1p(built[0])
        case "expm1":
            return expm1(built[0])
    raise ExpressionError(f"{name!r} is not an allowed function", node=node)
