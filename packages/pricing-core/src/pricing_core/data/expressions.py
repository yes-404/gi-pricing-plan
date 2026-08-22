"""The restricted expression grammar for `derive_expression` (FR-DATA-10).

> It cannot call out to the network, filesystem, or Python builtins.

The safety property is not "we validated the string" — it is that **nothing outside the
allow-list is ever evaluated**. The expression is parsed to a Python AST, every node type
is checked against a permitted set, and the tree is then *translated* into a Polars
expression. Python never executes it, so there is no `__builtins__` to escape from and no
attribute access to walk.

That is deliberately stricter than sandboxing `eval`. A sandbox is a list of things you
remembered to forbid; a translator can only produce what it knows how to build.
"""

from __future__ import annotations

import ast
from collections import deque
from collections.abc import Iterator
from typing import Final

import polars as pl

__all__ = ["ExpressionError", "compile_expression", "referenced_columns"]

#: Node types the grammar admits. Everything else — attribute access, subscripts, lambdas,
#: comprehensions, f-strings, walrus — is refused, because each is a route to something
#: this grammar has no business reaching.
_ALLOWED_NODES: Final[tuple[type[ast.AST], ...]] = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Call,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)

#: The only callable names. No statistical functions — FR-DATA-10 excludes them, because a
#: preparation step that could compute a mean over the column it is deriving would make the
#: result depend on which rows happened to be in the extract.
_FUNCTIONS: Final[frozenset[str]] = frozenset(
    {"abs", "min", "max", "round", "floor", "ceil", "coalesce", "log", "exp", "sqrt"}
)


class ExpressionError(ValueError):
    """The expression is outside the grammar. The message names what was refused.

    It also names *where*, when the AST can say (NFR-MODEL-8). `lineno` and `col_offset`
    are exactly what `ast` reports — 1-based and 0-based respectively — so a caller can
    underline the offending token without re-parsing.

    They are `None` when nothing in the tree above the refusal has a position: `ast` gives
    `lineno` only to `expr` and `stmt` subclasses, and the refusals below are often handed
    an `operator` or a `cmpop`, which are neither. Those sites thread the nearest
    **enclosing** expression node for that reason, so `None` means "the parser could not
    know", never "nobody threaded it".
    """

    def __init__(self, message: str, *, node: ast.AST | None = None) -> None:
        super().__init__(message)
        self.lineno: int | None = getattr(node, "lineno", None)
        self.col_offset: int | None = getattr(node, "col_offset", None)
        self.end_col_offset: int | None = getattr(node, "end_col_offset", None)


def _walk_positioned(node: ast.AST) -> Iterator[tuple[ast.AST, ast.AST | None]]:
    """`ast.walk`, pairing each node with the nearest node that knows where it is.

    `ast` gives `lineno`/`col_offset` to `expr` and `stmt` subclasses only, so an
    `operator`, `cmpop`, `boolop` or `unaryop` can never say where it is — and those are
    exactly the nodes a grammar refusal most often names (`FloorDiv`, `Is`, `In`). The
    enclosing expression can say, and its span is what a caller should underline
    (NFR-MODEL-8): for `exposure + premium // 2` that is `premium // 2`, not the whole
    string.

    Breadth-first, in `ast.walk`'s own order, so which node is refused first is unchanged
    by adding positions.
    """
    queue: deque[tuple[ast.AST, ast.AST | None]] = deque([(node, None)])
    while queue:
        current, inherited = queue.popleft()
        position = current if hasattr(current, "lineno") else inherited
        queue.extend((child, position) for child in ast.iter_child_nodes(current))
        yield current, position


def _check(node: ast.AST) -> None:
    for child, position in _walk_positioned(node):
        if not isinstance(child, _ALLOWED_NODES):
            raise ExpressionError(
                f"{type(child).__name__} is not permitted in a derive_expression "
                "(FR-DATA-10). The grammar admits arithmetic, comparison, conditionals and "
                f"a fixed function list: {sorted(_FUNCTIONS)}.",
                node=position,
            )
        if isinstance(child, ast.Call):
            if not isinstance(child.func, ast.Name):
                raise ExpressionError(
                    "only plain function calls are permitted", node=child
                )
            if child.func.id not in _FUNCTIONS:
                raise ExpressionError(
                    f"{child.func.id!r} is not an allowed function; permitted: "
                    f"{sorted(_FUNCTIONS)}",
                    node=child,
                )
            if child.keywords:
                raise ExpressionError(
                    "keyword arguments are not permitted", node=child.keywords[0]
                )


def referenced_columns(expression: str) -> frozenset[str]:
    """Column names an expression reads, for lineage and for pre-flight checks."""
    tree = ast.parse(expression, mode="eval")
    _check(tree)
    return frozenset(
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id not in _FUNCTIONS
    )


def compile_expression(expression: str) -> pl.Expr:
    """Translate a restricted expression into a Polars expression.

    Translation, not evaluation. The result is a Polars expression object built node by
    node — Python never runs the user's text, so there is nothing for it to reach out of.
    """
    tree = ast.parse(expression, mode="eval")
    _check(tree)
    return _translate(tree.body)


def _translate(node: ast.AST) -> pl.Expr:
    match node:
        case ast.Constant(value=value):
            return pl.lit(value)
        case ast.Name(id=name):
            return pl.col(name)
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return -_translate(operand)
        case ast.UnaryOp(op=ast.UAdd(), operand=operand):
            return _translate(operand)
        case ast.UnaryOp(op=ast.Not(), operand=operand):
            return ~_translate(operand)
        case ast.BinOp(left=left, op=op, right=right) as binop:
            return _binary(op, _translate(left), _translate(right), node=binop)
        case ast.BoolOp(op=op, values=values):
            translated = [_translate(v) for v in values]
            result = translated[0]
            for other in translated[1:]:
                result = result & other if isinstance(op, ast.And) else result | other
            return result
        case ast.Compare(left=left, ops=[op], comparators=[right]) as comparison:
            return _compare(op, _translate(left), _translate(right), node=comparison)
        case ast.Compare() as chained:
            raise ExpressionError(
                "chained comparisons are not permitted; use `and`", node=chained
            )
        case ast.IfExp(test=test, body=body, orelse=orelse):
            return (
                pl.when(_translate(test))
                .then(_translate(body))
                .otherwise(_translate(orelse))
            )
        case ast.Call(func=ast.Name(id=name), args=args) as call:
            return _call(name, [_translate(a) for a in args], node=call)
    raise ExpressionError(f"{type(node).__name__} is not translatable", node=node)


def _binary(op: ast.operator, left: pl.Expr, right: pl.Expr, *, node: ast.AST) -> pl.Expr:
    match op:
        case ast.Add():
            return left + right
        case ast.Sub():
            return left - right
        case ast.Mult():
            return left * right
        case ast.Div():
            return left / right
        case ast.Mod():
            return left % right
        case ast.Pow():
            return left**right
    raise ExpressionError(f"{type(op).__name__} is not a permitted operator", node=node)


def _compare(op: ast.cmpop, left: pl.Expr, right: pl.Expr, *, node: ast.AST) -> pl.Expr:
    match op:
        case ast.Eq():
            return left == right
        case ast.NotEq():
            return left != right
        case ast.Lt():
            return left < right
        case ast.LtE():
            return left <= right
        case ast.Gt():
            return left > right
        case ast.GtE():
            return left >= right
    raise ExpressionError(f"{type(op).__name__} is not a permitted comparison", node=node)


def _call(name: str, args: list[pl.Expr], *, node: ast.AST) -> pl.Expr:
    if not args:
        raise ExpressionError(f"{name}() needs at least one argument", node=node)
    match name:
        case "abs":
            return args[0].abs()
        case "round":
            digits = 0
            return args[0].round(digits)
        case "floor":
            return args[0].floor()
        case "ceil":
            return args[0].ceil()
        case "log":
            return args[0].log()
        case "exp":
            return args[0].exp()
        case "sqrt":
            return args[0].sqrt()
        case "min":
            return pl.min_horizontal(args)
        case "max":
            return pl.max_horizontal(args)
        case "coalesce":
            return pl.coalesce(args)
    raise ExpressionError(f"{name!r} is not an allowed function", node=node)
