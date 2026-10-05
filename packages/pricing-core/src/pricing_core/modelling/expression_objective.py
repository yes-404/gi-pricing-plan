"""An `expression` objective's middle layer: derivation and the compilation target (FR-144).

`derive` differentiates the SymPy tree Slice 1's `to_sympy` builds, and prints the result in
02 §4.6's `objective` grammar, so that one parser (`parse_expression`) reads the loss and
its derivatives alike. No string reaches `eval`, `exec`, `compile`, `sympify` or `lambdify`
(NFR-483; 02 §8): the printer walks SymPy nodes, and a later step walks the validated `ast`.

`pricing-core` reads no clock (ADR-703), so `derive` returns the tool and its version and
not a `derived_at`: the backend stamps that.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass
from typing import Any, Final, Literal

import numpy as np
import sympy
from numpy.typing import NDArray
from sympy.codegen.cfunctions import expm1, log1p

from model_schema import (
    CertificateResult,
    HessianStrategy,
    ResponseKind,
    SamplingSpec,
    YDomain,
)
from pricing_core.data.expression_sympy import OBJECTIVE_SYMBOLS, to_sympy
from pricing_core.data.expressions import (
    DEFAULT_LIMITS,
    ExpressionError,
    ExpressionLimits,
    GrammarProfile,
    parse_expression,
)
from pricing_core.modelling.errors import ObjectiveError
from pricing_core.modelling.objectives import (
    BranchCondition,
    Denominator,
    ExpressionKernels,
    ObjectiveFns,
    certify_compiled,
)
from pricing_core.progress import ProgressCallback

__all__ = [
    "DERIVED_LIMITS",
    "Derived",
    "Kernel",
    "certify_expression_objective",
    "compile_expression_objective",
    "compile_kernel",
    "derive",
    "to_grammar",
]

_Arr = NDArray[np.float64]

#: A compiled expression: `(y, f, w)` in, one array of the same length out.
Kernel = Callable[[_Arr, _Arr, _Arr], _Arr]

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


_ARITHMETIC: Final[Mapping[type[ast.operator], Callable[[Any, Any], Any]]] = {
    ast.Add: np.add,
    ast.Sub: np.subtract,
    ast.Mult: np.multiply,
    ast.Div: np.divide,
    ast.Pow: np.power,
}
_COMPARISONS: Final[Mapping[type[ast.cmpop], Callable[[Any, Any], Any]]] = {
    ast.Lt: np.less,
    ast.LtE: np.less_equal,
    ast.Gt: np.greater,
    ast.GtE: np.greater_equal,
    ast.Eq: np.equal,
    ast.NotEq: np.not_equal,
}
_UNARY: Final[Mapping[str, Callable[[Any], Any]]] = {
    "log": np.log,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "log1p": np.log1p,
    "expm1": np.expm1,
}


def compile_kernel(
    text: str,
    *,
    parameters: Mapping[str, float],
    limits: ExpressionLimits = DERIVED_LIMITS,
) -> Kernel:
    """Compile `text` into a vectorised NumPy kernel, through the platform's own tree.

    The text is parsed by the one parser, in the `objective` profile; the validated `ast` is
    walked into NumPy calls on the caller's arrays. No string becomes code (NFR-483), and a
    kernel works elementwise, so every array it makes is the input's length (FR-165).
    Non-finite values are not warned about here: the boosting adapter aborts on them.
    """
    return _kernel(_parse(text, parameters, limits), parameters)


def _parse(text: str, parameters: Mapping[str, float], limits: ExpressionLimits) -> ast.expr:
    return parse_expression(
        text,
        GrammarProfile.OBJECTIVE,
        symbols=OBJECTIVE_SYMBOLS | frozenset(parameters),
        limits=limits,
    ).body


def _kernel(body: ast.expr, parameters: Mapping[str, float]) -> Kernel:
    constants = {name: np.float64(value) for name, value in parameters.items()}

    def kernel(y: _Arr, f: _Arr, w: _Arr) -> _Arr:
        with np.errstate(all="ignore"):
            result = _evaluate(body, {"y": y, "f": f, "w": w} | constants)
        shape = np.broadcast_shapes(y.shape, f.shape, w.shape)
        return np.asarray(np.broadcast_to(result, shape), dtype=np.float64)

    return kernel


def _evaluate(node: ast.expr, values: Mapping[str, Any]) -> Any:
    match node:
        case ast.Constant(value=int() | float() as value):
            return np.float64(value)
        case ast.Name(id=name):
            return values[name]
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return np.negative(_evaluate(operand, values))
        case ast.UnaryOp(op=ast.UAdd(), operand=operand):
            return _evaluate(operand, values)
        case ast.BinOp(left=left, op=op, right=right) if type(op) in _ARITHMETIC:
            return _ARITHMETIC[type(op)](_evaluate(left, values), _evaluate(right, values))
        case ast.Call(func=ast.Name(id="where"), args=[ast.Compare() as test, then, otherwise]):
            relation = _COMPARISONS[type(test.ops[0])]
            condition = relation(
                _evaluate(test.left, values), _evaluate(test.comparators[0], values)
            )
            return np.where(condition, _evaluate(then, values), _evaluate(otherwise, values))
        case ast.Call(func=ast.Name(id=name), args=args):
            built = [_evaluate(a, values) for a in args]
            if name in _UNARY:
                return _UNARY[name](built[0])
            if name == "min":
                return _reduce(np.minimum, built)
            if name == "max":
                return _reduce(np.maximum, built)
            if name == "clip":
                return np.minimum(np.maximum(built[0], built[1]), built[2])
    raise ExpressionError(f"{type(node).__name__} cannot be compiled", node=node)


def _reduce(op: Callable[[Any, Any], Any], arguments: list[Any]) -> Any:
    result = arguments[0]
    for argument in arguments[1:]:
        result = op(result, argument)
    return result


def compile_expression_objective(
    *,
    ref: str,
    loss: str,
    parameters: Mapping[str, float],
    y_domain: YDomain,
    hessian_strategy: HessianStrategy,
    hessian_min: float,
    inverse_link: Literal["exp", "logistic"] = "exp",
    derived: Derived | None = None,
) -> ObjectiveFns:
    """An `expression` objective as the same `ObjectiveFns` a template compiles to (FR-144).

    The arguments are the artifact's fields as primitives (DP-S2-1 (c)); the domain and the
    strategy are `model-schema`'s own types. `inverse_link` is an argument until the
    artifact's applicability supplies it. The gradient and hessian are `derived`'s, or are
    derived here from `loss`.
    """
    if hessian_strategy is HessianStrategy.GAUSS_NEWTON:
        raise ObjectiveError(
            "OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED",
            f"objective {ref} declares hessian_strategy=gauss_newton, and an expression "
            "objective has no Gauss-Newton hessian to drop a term from. Use clip_to_min "
            "or abs.",
            terms=[ref],
        )
    texts = derived if derived is not None else derive(loss, parameters=parameters.keys())
    bodies = (
        _parse(loss, parameters, DEFAULT_LIMITS),
        _parse(texts.gradient, parameters, DERIVED_LIMITS),
        _parse(texts.hessian, parameters, DERIVED_LIMITS),
    )
    conditions, denominators = _found_branches_and_divisors(bodies, parameters)
    return ObjectiveFns(
        ref=ref,
        template=None,
        params=dict(parameters),
        hessian_strategy=hessian_strategy,
        hessian_min=hessian_min,
        y_domain=y_domain,
        _template=None,
        _expression=ExpressionKernels(
            loss=_kernel(bodies[0], parameters),
            grad=_kernel(bodies[1], parameters),
            hess=_kernel(bodies[2], parameters),
            inverse_link=inverse_link,
            conditions=conditions,
            denominators=denominators,
        ),
    )


def _found_branches_and_divisors(
    bodies: tuple[ast.expr, ...], parameters: Mapping[str, float]
) -> tuple[tuple[BranchCondition, ...], tuple[Denominator, ...]]:
    """Every `where()` condition and every divisor in the loss and its derived text.

    Found, not declared (FR-147, FR-148; §4.6's division rule), because an expression
    declares neither. A divisor is the right operand of `/` (a bare constant is not one), or
    the base of a negative constant power, which is how SymPy writes `1/x` and so how the
    printer prints it. Duplicates are the same source text.
    """
    conditions: dict[str, BranchCondition] = {}
    divisors: dict[str, Denominator] = {}
    for body in bodies:
        for node in ast.walk(body):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "where"
                and isinstance(node.args[0], ast.Compare)
            ):
                test = node.args[0]
                text = ast.unparse(test)
                if text not in conditions:
                    lhs = _kernel(test.left, parameters)
                    rhs = _kernel(test.comparators[0], parameters)
                    relation = _COMPARISONS[type(test.ops[0])]
                    conditions[text] = BranchCondition(
                        text=text,
                        test=_test_of(relation, lhs, rhs),
                        gap=_gap_of(lhs, rhs),
                    )
            divisor = _divisor_of(node)
            if divisor is not None:
                text = ast.unparse(divisor)
                if text not in divisors:
                    divisors[text] = Denominator(text=text, value=_kernel(divisor, parameters))
    return tuple(conditions.values()), tuple(divisors.values())


def _test_of(
    relation: Callable[[Any, Any], Any], lhs: Kernel, rhs: Kernel
) -> Callable[[_Arr, _Arr, _Arr], NDArray[np.bool_]]:
    def test(y: _Arr, f: _Arr, w: _Arr) -> NDArray[np.bool_]:
        return np.asarray(relation(lhs(y, f, w), rhs(y, f, w)), dtype=np.bool_)

    return test


def _gap_of(lhs: Kernel, rhs: Kernel) -> Kernel:
    def gap(y: _Arr, f: _Arr, w: _Arr) -> _Arr:
        return np.asarray(lhs(y, f, w) - rhs(y, f, w), dtype=np.float64)

    return gap


def _divisor_of(node: ast.AST) -> ast.expr | None:
    if not isinstance(node, ast.BinOp):
        return None
    if isinstance(node.op, ast.Div):
        return None if isinstance(node.right, ast.Constant) else node.right
    if isinstance(node.op, ast.Pow) and _is_negative_constant(node.right):
        return node.left
    return None


def _is_negative_constant(node: ast.expr) -> bool:
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return isinstance(node.operand, ast.Constant)
    return isinstance(node, ast.Constant) and isinstance(node.value, int | float) and node.value < 0


#: What `ObjectiveFns` is certified against for each kind of inverse link (FR-146): the
#: synthetic response the smoke fit draws. Severity for a log link, conversion for a logistic.
_SMOKE_RESPONSES: Final[Mapping[str, ResponseKind]] = {
    "exp": ResponseKind.CLAIM_SEVERITY,
    "logistic": ResponseKind.CONVERSION,
}


#: Responses whose mean is a probability, so the margin is a logit. Every other response is a
#: positive mean on a log link. `platform/objectives.py`'s `default_sampling` draws its grid
#: from the same split.
_PROBABILITY_RESPONSES: Final = frozenset({ResponseKind.CONVERSION, ResponseKind.RETENTION})


def inverse_link_for(responses: Collection[ResponseKind]) -> Literal["exp", "logistic"]:
    """The inverse link an `expression` objective's applicability implies (`RL-1362` DP-S3-1).

    One function, so that certification and the fit cannot disagree about it.
    """
    return "logistic" if set(responses) <= _PROBABILITY_RESPONSES else "exp"


def certify_expression_objective(
    *,
    ref: str,
    loss: str,
    parameters: Mapping[str, float],
    y_domain: YDomain,
    hessian_strategy: HessianStrategy,
    hessian_min: float,
    inverse_link: Literal["exp", "logistic"] = "exp",
    sampling: SamplingSpec,
    derived: Derived | None = None,
    progress: ProgressCallback | None = None,
) -> CertificateResult:
    """§4.7's nine checks over an `expression` objective (FR-146, FR-151).

    The first two are `symbolic_vs_numeric_gradient` and `_hessian`: the SymPy-derived
    derivatives against a Richardson-extrapolated numeric derivative of the loss, with the
    points near a found `where()` boundary excluded (FR-147, FR-149). The certificate
    records `sympy.__version__`, read at the call (RL-1289). Persistence, the id and
    `certified_at` are the backend's (ADR-703).
    """
    fns = compile_expression_objective(
        ref=ref,
        loss=loss,
        parameters=parameters,
        y_domain=y_domain,
        hessian_strategy=hessian_strategy,
        hessian_min=hessian_min,
        inverse_link=inverse_link,
        derived=derived,
    )
    return certify_compiled(
        fns,
        sampling=sampling,
        smoke_response=_SMOKE_RESPONSES[inverse_link],
        versions={"numpy": str(np.__version__), "sympy": sympy.__version__},
        progress=progress,
    )
