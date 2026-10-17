"""Money crosses a boundary as `decimal`, and the output step rounds it once (SL-1563).

PL-1562 item 12 (b) and PL-1627 section A2 (item 12 (c), owed by this slice because SL-1340 merged
first and built no mounted test). FD-1424's rulings of 2026-10-05, 17:36:28 and 17:50:43 BST:
`decimal` -> `money_minor` stays legal AT AN OUTPUT STEP (FR-226's rounding point), and a Sub-graph
port carries money as `decimal`. These are controls: green at the base, and green after the rule
closes `money_minor`. Money here is `Decimal` or integer minor units, never `float` (CLAUDE.md
section 7): the inputs are `int`, the literals are exact decimals, and the served value is an `int`.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any

import pytest
from test_rating_ladder_exact import _chain_algorithm, _compile_payload, _context
from test_rating_score import _FakeResolver, _version

from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import load_bundle
from pricing_core.rating.score import score_one

_FRAGMENT_REF = "sub_graph:decimal-money-port@1"


def _rounded(value: Decimal) -> Decimal:
    return value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN)


def _decimal_expressions(payload: dict[str, Any]) -> dict[str, Any]:
    """Declare every expression step `decimal`: money is a decimal until the output step."""
    for step in payload["steps"]:
        if step["type"] == "expression":
            step["result_type"] = "decimal"
    return payload


@pytest.mark.req("FR-226")
def test_a_second_rounding_would_differ_from_the_single_one() -> None:
    """The premise of the two tests below, shown in `Decimal`: `10 * 123.44 = 1234.4`, and
    `1234.4 * 1.1 = 1357.84` rounds to 1358, whereas rounding `1234.4` first gives `1234 * 1.1 =
    1357.4`, which rounds to 1357. So 1358 can only come from one rounding at the end."""
    exact = Decimal(10) * Decimal("123.44") * Decimal("1.1")
    assert exact == Decimal("1357.840")
    assert _rounded(exact) == Decimal(1358)
    assert _rounded(_rounded(Decimal(10) * Decimal("123.44")) * Decimal("1.1")) == Decimal(1357)


@pytest.mark.req("FR-226")
@pytest.mark.req("FR-227")
async def test_a_decimal_into_a_money_minor_output_step_rounds_once() -> None:
    """PL-1562 item 12 (b): a `decimal` chain (`10 * 123.44`, then `* 1.1`, exact 1357.84) feeds
    an `output` declared `money_minor` with `half_even`, dp 0. It saves (A2) and serves 1358, an
    `int`. Green at the base and after the change."""
    payload = _decimal_expressions(_chain_algorithm(factors=[
        ("office_premium", "{prev} * 123.44", "half_even"),
        ("instalment_loading", "{prev} * 1.1", "half_even"),
    ]))
    assert payload["outputs"][0]["type"] == "money_minor"  # the payable output step is the sink
    bundle = await _compile_payload(payload)  # compile_bundle runs the save-time type check
    result = await score_one(bundle, _context(risk_premium_minor=10))

    served = result.outputs["payable_premium_minor"]
    assert served == 1358
    assert type(served) is int  # integer minor units, never a float


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-226")
async def test_a_mounted_decimal_port_rounds_once_at_the_parent_output() -> None:
    """PL-1627 item 12 (c): the fragment of item 12 (a) is mounted, its `decimal` port feeds the
    parent's `money_minor` output step, and the served value is (b)'s single rounding, 1358.
    Green at the base and after: the mount-port check (`_refuse_mount_port_type_mismatch`)
    compares the parent's `decimal` value with a `decimal` port, and the output step is the one
    place `decimal` becomes `money_minor`."""
    fragment = {
        "slug": "decimal-money-port", "version": 1,
        "inputs": [{"name": "base", "type": "decimal"}],
        "outputs": [{"name": "scaled", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_scale", "type": "expression", "label": "Scale",
             "expr": "base * 1.1", "result_type": "decimal",
             "consumes": ["base"], "produces": "scaled"},
        ],
        "change_note": "first cut",
    }
    # No intermediate rung output: the ladder (R3/R4) would replay a rounded rung, and the point
    # is that nothing rounds before the parent's output step.
    payload = _chain_algorithm(factors=[])
    payload["steps"] = [s for s in payload["steps"] if s["step_id"] != "s_out_risk"]
    payload["steps"].insert(-1, {
        "step_id": "s_office", "type": "expression", "label": "Office premium",
        "expr": "risk_premium_minor * 123.44", "result_type": "decimal",
        "consumes": ["risk_premium_minor"], "produces": "office_premium",
    })
    payload["sub_graphs"] = [{
        "ref": _FRAGMENT_REF, "mount_point": "m_port",
        "inputs": {"base": "office_premium"}, "outputs": {"scaled": "mounted_total"},
    }]
    next(s for s in payload["steps"] if s["step_id"] == "s_out_payable")["consumes"] = [
        "mounted_total"
    ]

    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = payload
    resolver._payloads[_FRAGMENT_REF] = fragment
    version = _version()
    assert version.pins is not None
    version = version.model_copy(update={"pins": version.pins.model_copy(
        update={"sub_graphs": [ArtifactRef.parse(_FRAGMENT_REF)]}
    )})

    bundle = load_bundle(await compile_bundle(version, resolver))
    result = await score_one(bundle, _context(risk_premium_minor=10))

    served = result.outputs["payable_premium_minor"]
    assert served == 1358
    assert type(served) is int
