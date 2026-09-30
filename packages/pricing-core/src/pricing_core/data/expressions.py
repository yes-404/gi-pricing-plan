"""The restricted expression grammar, in 02 §4.6's four profiles (FR-36, FR-144, FR-145).

`recipe` (`derive_expression`, `filter_rows`), `check` (the `expression` check), `factor`
and `objective`.

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
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

import polars as pl

__all__ = [
    "ExpressionError",
    "ExpressionSize",
    "GrammarProfile",
    "compile_expression",
    "measure_expression",
    "parse_expression",
    "referenced_columns",
]

class GrammarProfile(StrEnum):
    """02 §4.6's profile table. The context names which grammar an expression is parsed in."""

    OBJECTIVE = "objective"
    FACTOR = "factor"
    RECIPE = "recipe"
    CHECK = "check"


_STRICT: Final = frozenset({GrammarProfile.OBJECTIVE, GrammarProfile.FACTOR})
_COMPARISONS: Final = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)

#: `objective` and `factor`: §4.6's EBNF. Arithmetic, unary minus, calls, and comparisons
#: (which `_check_structure` then confines to where()'s condition).
_STRICT_NODES: Final[tuple[type[ast.AST], ...]] = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare, ast.Name, ast.Load, ast.Constant,
    ast.Call, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, *_COMPARISONS,
)
#: `recipe` and `check`: exactly the node set accepted before profiles (only-add).
_LENIENT_NODES: Final[tuple[type[ast.AST], ...]] = (
    *_STRICT_NODES, ast.BoolOp, ast.IfExp, ast.Mod, ast.UAdd, ast.Not, ast.And, ast.Or,
)
#: The ten in §4.6's `func`. `ceil coalesce floor round` are not differentiable, so they
#: are recipe and check only (the profile note). No statistical functions — FR-36 excludes
#: them, because a preparation step that could compute a mean over the column it is
#: deriving would make the result depend on which rows happened to be in the extract.
_STRICT_FUNCTIONS: Final = frozenset(
    {"log", "exp", "sqrt", "abs", "min", "max", "clip", "where", "log1p", "expm1"}
)
_LENIENT_FUNCTIONS: Final = _STRICT_FUNCTIONS | {"ceil", "coalesce", "floor", "round"}
#: Exact arity, in every profile (RL-1292, DP-S1-2 (b)). The seven legacy
#: single-argument functions no longer drop extra arguments silently. `min`, `max` and
#: `coalesce` are absent: they keep "at least one", which `_call`'s empty-args refusal holds.
_ARITY: Final = {
    "where": 3, "clip": 3, "log1p": 1, "expm1": 1,
    "abs": 1, "round": 1, "floor": 1, "ceil": 1, "log": 1, "exp": 1, "sqrt": 1,
}


def _nodes(profile: GrammarProfile) -> tuple[type[ast.AST], ...]:
    return _STRICT_NODES if profile in _STRICT else _LENIENT_NODES


def _functions(profile: GrammarProfile) -> frozenset[str]:
    return _STRICT_FUNCTIONS if profile in _STRICT else _LENIENT_FUNCTIONS


class ExpressionError(ValueError):
    """The expression is outside the grammar. The message names what was refused.

    It also names *where*, when the AST can say (NFR-483). `lineno` and `col_offset`
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


@dataclass(frozen=True, slots=True)
class ExpressionSize:
    """An expression's size under 02 §4.6's limits (FR-145).

    `nodes` and `depth` count `ast.expr` nodes only, the root at depth 1 (DP-S1-1 (a), RL-1291).
    `all_nodes` counts every node `ast.walk` yields (option (b)). It is carried so that the
    corpus measurement records both predicates, and nothing enforces it.
    """

    nodes: int
    depth: int
    all_nodes: int


def measure_expression(expression: str) -> ExpressionSize:
    """The size of `expression`, parsed but not checked against any profile."""
    return _measure(ast.parse(expression, mode="eval").body)[0]


def _measure(root: ast.expr) -> tuple[ExpressionSize, ast.expr]:
    """Count iteratively, so a deep tree cannot exhaust Python's own stack here."""
    nodes, depth, deepest = 0, 0, root
    stack: list[tuple[ast.expr, int]] = [(root, 1)]
    while stack:
        node, level = stack.pop()
        nodes += 1
        if level > depth:
            depth, deepest = level, node
        stack.extend(
            (child, level + 1)
            for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.expr)
        )
    all_nodes = sum(1 for _ in ast.walk(root))
    return ExpressionSize(nodes=nodes, depth=depth, all_nodes=all_nodes), deepest


def _walk_positioned(node: ast.AST) -> Iterator[tuple[ast.AST, ast.AST | None]]:
    """`ast.walk`, pairing each node with the nearest node that knows where it is.

    `ast` gives `lineno`/`col_offset` to `expr` and `stmt` subclasses only, so an
    `operator`, `cmpop`, `boolop` or `unaryop` can never say where it is — and those are
    exactly the nodes a grammar refusal most often names (`FloorDiv`, `Is`, `In`). The
    enclosing expression can say, and its span is what a caller should underline
    (NFR-483): for `exposure + premium // 2` that is `premium // 2`, not the whole
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


def _check(node: ast.AST, profile: GrammarProfile) -> None:
    functions = _functions(profile)
    allowed = _nodes(profile)
    for child, position in _walk_positioned(node):
        if not isinstance(child, allowed):
            raise ExpressionError(
                f"{type(child).__name__} is not permitted in the {profile} profile "
                "(02 §4.6). The grammar admits arithmetic, comparison, conditionals and "
                f"a fixed function list: {sorted(functions)}.",
                node=position,
            )
        if isinstance(child, ast.Call):
            if not isinstance(child.func, ast.Name):
                raise ExpressionError(
                    "only plain function calls are permitted", node=child
                )
            if child.func.id not in functions:
                raise ExpressionError(
                    f"{child.func.id!r} is not an allowed function; permitted: "
                    f"{sorted(functions)}",
                    node=child,
                )
            if child.keywords:
                raise ExpressionError(
                    "keyword arguments are not permitted", node=child.keywords[0]
                )
            arity = _ARITY.get(child.func.id)
            if arity is not None and len(child.args) != arity:
                raise ExpressionError(
                    f"{child.func.id}() takes exactly {arity} argument(s), "
                    f"got {len(child.args)}",
                    node=child,
                )


def _check_structure(
    node: ast.expr, profile: GrammarProfile, *, where_condition: bool = False
) -> None:
    """What the node-type walk cannot see: where a comparison may stand, and literals."""
    strict = profile in _STRICT
    if (
        isinstance(node, ast.Constant)
        and strict
        and (isinstance(node.value, bool) or not isinstance(node.value, int | float))
    ):
        raise ExpressionError(
            f"only numeric literals are permitted in the {profile} profile", node=node
        )
    if isinstance(node, ast.Compare):
        if len(node.ops) > 1:
            raise ExpressionError(
                "chained comparisons are not permitted; use `and`", node=node
            )
        if strict and not where_condition:
            raise ExpressionError(
                "a comparison is permitted only as the condition of where(cond, a, b) "
                f"in the {profile} profile",
                node=node,
            )
        for side in (node.left, *node.comparators):
            _check_structure(side, profile)
        return
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "where"
        and len(node.args) == 3
    ):
        condition = node.args[0]
        if not isinstance(condition, ast.Compare):
            raise ExpressionError(
                "where(cond, a, b) needs cond to be one comparison between two "
                "sub-expressions",
                node=condition,
            )
        _check_structure(condition, profile, where_condition=True)
        for arg in node.args[1:]:
            _check_structure(arg, profile)
        return
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.expr):
            _check_structure(child, profile)


def _check_symbols(tree: ast.AST, symbols: frozenset[str]) -> None:
    """Every name that is not a function's own must be bound or declared."""
    called = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and id(node) not in called and node.id not in symbols:
            raise ExpressionError(
                f"{node.id!r} is not a bound symbol or declared parameter", node=node
            )


def parse_expression(
    expression: str, profile: GrammarProfile, *, symbols: frozenset[str] | None = None
) -> ast.Expression:
    """Parse and validate `expression` in `profile`: the one allow-list walk (02 §4.6)."""
    if profile in _STRICT and symbols is None:
        raise ValueError("the objective and factor profiles need their bound symbols")
    tree = ast.parse(expression, mode="eval")
    _check(tree, profile)
    _check_structure(tree.body, profile)
    if symbols is not None:
        _check_symbols(tree, symbols)
    return tree


def referenced_columns(
    expression: str, *, profile: GrammarProfile = GrammarProfile.RECIPE
) -> frozenset[str]:
    """Column names an expression reads, for lineage and for pre-flight checks."""
    tree = parse_expression(expression, profile)
    functions = _functions(profile)
    return frozenset(
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id not in functions
    )


def compile_expression(
    expression: str,
    *,
    profile: GrammarProfile = GrammarProfile.RECIPE,
    symbols: frozenset[str] | None = None,
) -> pl.Expr:
    """Translate a restricted expression into a Polars expression.

    Translation, not evaluation. The result is a Polars expression object built node by
    node — Python never runs the user's text, so there is nothing for it to reach out of.
    """
    if profile is GrammarProfile.OBJECTIVE:
        raise ValueError(
            "the objective profile translates to SymPy: use "
            "pricing_core.data.expression_sympy.to_sympy"
        )
    return _translate(parse_expression(expression, profile, symbols=symbols).body)


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
        case "where":
            return pl.when(args[0]).then(args[1]).otherwise(args[2])
        case "clip":
            return args[0].clip(args[1], args[2])
        case "log1p":
            return args[0].log1p()
        case "expm1":
            # Polars has no `expm1` (premise f); the precision loss near 0 is a `recipe`
            # and `check` matter only, since `objective` compiles through SymPy.
            return args[0].exp() - 1
    raise ExpressionError(f"{name!r} is not an allowed function", node=node)
