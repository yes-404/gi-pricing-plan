"""FR-145 and 02 §4.6: node count ≤ 200 and depth ≤ 20, in all four profiles.

The counts are over `ast.expr` nodes, with the root at depth 1. That is DP-S1-1's
(a), ruled by RL-1291. `all_nodes` is option (b), measured beside
it so the corpus table shows both predicates (F8). The
figures below are premise h's, from the spike at fb90d381.
"""

from __future__ import annotations

import pytest

from pricing_core.data.expressions import ExpressionSize, measure_expression


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
