"""FR-145 and 02 §4.6: node count ≤ 200 and depth ≤ 20, in all four profiles.

The counts are over `ast.expr` nodes, with the root at depth 1. That is DP-S1-1's
(a), ruled by RL-1291. `all_nodes` is option (b), measured beside
it so the corpus table shows both predicates (F8). The
figures below are premise h's, from the spike at fb90d381.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator

import pytest

from pricing_core.data.expressions import (
    ExpressionError,
    ExpressionLimits,
    ExpressionSize,
    GrammarProfile,
    measure_expression,
    parse_expression,
)


def _min_of(n: int) -> str:
    return "min(" + ", ".join(["x"] * n) + ")"


def _nested_abs(n: int) -> str:
    return "abs(" * n + "x" + ")" * n


@pytest.mark.req("FR-145")
@pytest.mark.parametrize(
    ("expression", "size"),
    [
        ("a + b", ExpressionSize(nodes=3, depth=2, all_nodes=6)),
        (_min_of(198), ExpressionSize(nodes=200, depth=2, all_nodes=399)),
        (_min_of(199), ExpressionSize(nodes=201, depth=2, all_nodes=401)),
        (_nested_abs(19), ExpressionSize(nodes=39, depth=20, all_nodes=59)),
        (_nested_abs(20), ExpressionSize(nodes=41, depth=21, all_nodes=62)),
        (
            "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
            ExpressionSize(nodes=19, depth=6, all_nodes=34),
        ),
    ],
)
def test_the_counter_measures_expr_nodes_and_depth(expression: str, size: ExpressionSize) -> None:
    assert measure_expression(expression) == size


SYMBOLS = frozenset({"x"})
ALL_PROFILES = list(GrammarProfile)


def _parse(expression: str, profile: GrammarProfile, **kwargs: object) -> None:
    parse_expression(expression, profile, symbols=SYMBOLS, **kwargs)  # type: ignore[arg-type]


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", ALL_PROFILES)
def test_200_nodes_and_depth_20_are_accepted(profile: GrammarProfile) -> None:
    _parse(_min_of(198), profile)       # 200 nodes (premise h)
    _parse(_nested_abs(19), profile)    # depth 20


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", ALL_PROFILES)
def test_201_nodes_are_refused(profile: GrammarProfile) -> None:
    with pytest.raises(ExpressionError, match="201 nodes; the limit is 200"):
        _parse(_min_of(199), profile)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", ALL_PROFILES)
def test_depth_21_is_refused_at_the_deepest_node(profile: GrammarProfile) -> None:
    with pytest.raises(ExpressionError, match="depth 21; the limit is 20") as excinfo:
        _parse(_nested_abs(20), profile)
    assert excinfo.value.col_offset is not None  # NFR-483: positioned, not whole-string


@pytest.mark.req("FR-145")
def test_the_limits_are_configurable() -> None:
    small = ExpressionLimits(max_nodes=3, max_depth=2)
    _parse("x + x", GrammarProfile.RECIPE, limits=small)  # 3 nodes, depth 2
    with pytest.raises(ExpressionError, match="5 nodes; the limit is 3"):
        _parse("x + x + x", GrammarProfile.RECIPE, limits=small)


# --- FD-1842: the bound runs before the recursive structure walk (SL-1994) ---------------

_STRICT_PROFILES = [GrammarProfile.OBJECTIVE, GrammarProfile.FACTOR]
_SYMBOLS = frozenset({"x"})


@pytest.fixture
def lowered_recursion_limit() -> Iterator[None]:
    """Leave 70 frames of headroom above the frame this test runs in, then restore.

    A 99-deep unary chain parses (`ast.parse` is not what this limit stops) but a recursive
    walk needs 100 frames: the same `RecursionError` a 2000-character loss raises at the default
    limit, made deterministic and cheap.
    """
    saved = sys.getrecursionlimit()
    frame, depth = sys._getframe(), 0
    while frame is not None:
        frame, depth = frame.f_back, depth + 1
    sys.setrecursionlimit(depth + 70)
    try:
        yield
    finally:
        sys.setrecursionlimit(saved)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", _STRICT_PROFILES)
def test_an_over_depth_chain_is_refused_by_its_bound_not_by_the_stack(
    profile: GrammarProfile, lowered_recursion_limit: None
) -> None:
    with pytest.raises(ExpressionError, match="depth 100; the limit is 20"):
        parse_expression("-" * 99 + "x", profile, symbols=_SYMBOLS)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", _STRICT_PROFILES)
def test_a_2000_character_unary_chain_is_refused_by_its_bound(profile: GrammarProfile) -> None:
    with pytest.raises(ExpressionError, match="2000 nodes; the limit is 200"):
        parse_expression("-" * 1999 + "x", profile, symbols=_SYMBOLS)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", _STRICT_PROFILES)
def test_a_long_left_nested_sum_is_refused_by_its_node_bound(profile: GrammarProfile) -> None:
    with pytest.raises(ExpressionError, match="1999 nodes; the limit is 200"):
        parse_expression("x+" * 999 + "x", profile, symbols=_SYMBOLS)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize("profile", _STRICT_PROFILES)
def test_the_structure_walk_is_not_entered_for_an_over_bound_expression(
    profile: GrammarProfile, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pricing_core.data import expressions

    def entered(*args: object, **kwargs: object) -> None:
        raise AssertionError("_check_structure ran before the FR-145 bound refused")

    monkeypatch.setattr(expressions, "_check_structure", entered)
    with pytest.raises(ExpressionError, match="depth 21; the limit is 20"):
        parse_expression(_nested_abs(20), profile, symbols=_SYMBOLS)
    with pytest.raises(ExpressionError, match="201 nodes; the limit is 200"):
        parse_expression(_min_of(199), profile, symbols=_SYMBOLS)
