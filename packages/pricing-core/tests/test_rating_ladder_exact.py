"""The exact Premium Ladder (`RL-1329`, FD-1336, FD-1330): WK-674 Slice 3, Task 6.

Each test names the `RL-1329` Acceptance item it carries. The realistic-scale cases run
through a real ZEN evaluation and `score_one(trace=True)`, never a reimplementation.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pytest
from test_rating_score import _RATING_VERSION_REF, _FakeResolver, _version

from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

_HALF_EVEN = {"mode": "half_even", "dp": 0}


def _out(step_id: str, name: str, consumes: str, mode: str = "half_even") -> dict[str, Any]:
    return {
        "step_id": step_id, "type": "output", "label": name, "output_name": name,
        "rounding": {"mode": mode, "dp": 0}, "consumes": [consumes],
    }


def _chain_algorithm(
    *, factors: list[tuple[str, str, str]], extra_outputs: tuple[str, ...] = ()
) -> dict[str, Any]:
    """`risk_premium_minor` is an input; each `(rung, expression, mode)` is one expression
    step followed by its output step; the last rung present is `payable_premium`."""
    steps: list[dict[str, Any]] = [
        {"step_id": "s_in_risk", "type": "input", "label": "Risk premium",
         "input_name": "risk_premium_minor", "on_missing": "error",
         "produces": "risk_premium_minor"},
        _out("s_out_risk", "risk_premium_minor", "risk_premium_minor"),
    ]
    previous = "risk_premium_minor"
    outputs = [{"name": "payable_premium_minor", "type": "money_minor", "required": True}]
    for rung, expression, mode in factors:
        name = f"{rung}_minor"
        steps.append({
            "step_id": f"s_{rung}", "type": "expression", "label": rung,
            "expr": expression.replace("{prev}", previous), "result_type": "money_minor",
            "consumes": [previous], "produces": name,
        })
        steps.append(_out(f"s_out_{rung}", name, name, mode))
        previous = name
    steps.append(_out("s_out_payable", "payable_premium_minor", previous))
    for extra in extra_outputs:
        outputs.append({"name": extra, "type": "money_minor", "required": True})
    return {
        "slug": "score-fixture", "version": 1,
        "input_contract": [{"name": "risk_premium_minor", "type": "decimal", "nullable": False}],
        "outputs": outputs, "steps": steps, "sub_graphs": [],
    }


async def _compile_payload(payload: dict[str, Any]) -> CompiledBundle:
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = payload
    return load_bundle(await compile_bundle(_version(), resolver))


def _context(**inputs: Any) -> QuoteContext:
    return QuoteContext.model_validate({
        "purpose": "new_business", "quoted_at": datetime(2026, 8, 29, 12, 0, 0),
        "effective_date": date(2026, 9, 1), "inputs": inputs,
        "options": QuoteContextOptions(rating_version_ref=_RATING_VERSION_REF),
    })


@pytest.mark.req("FR-248")
async def test_the_realistic_scale_case_reconciles_and_prices_70726() -> None:
    """Acceptance 1 (`RL-1329`): risk 61234.5, office = risk x 1.1, instalment = office x 1.05.
    Red on `origin/main`: `ladder_reconciled` is True while the ladder replays to 70725
    against a payable of 70726, and office is 67357."""
    payload = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("instalment_loading", "{prev} * 1.05", "half_even"),
        ],
        extra_outputs=("office_premium_minor",),
    )
    bundle = await _compile_payload(payload)
    result = await score_one(bundle, _context(risk_premium_minor=61234.5), trace=True)

    ladder = {r.rung: r for r in result.premium_ladder}
    assert [r.value_minor for r in result.premium_ladder] == [
        61234, 67358, 67358, 70726, 70726,
    ]
    assert ladder["office_premium"].operation is not None
    assert ladder["office_premium"].operation.factor == Decimal("1.1")
    assert ladder["office_premium"].unrounded_minor == Decimal("67357.95")
    assert result.outputs["office_premium_minor"] == 67358
    assert result.outputs["payable_premium_minor"] == 70726
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True


@pytest.mark.req("FR-248")
async def test_the_auditors_case_at_unit_level() -> None:
    """Acceptance 1, second half: 60000.4 -> 66000.44 -> 69402.0."""
    payload = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("instalment_loading", "{prev} + 3401.56", "half_even"),
        ],
    )
    result = await score_one(
        await _compile_payload(payload), _context(risk_premium_minor=60000.4), trace=True
    )
    assert [r.value_minor for r in result.premium_ladder] == [60000, 66000, 66000, 69402, 69402]
    assert result.premium_ladder[1].unrounded_minor == Decimal("66000.44")
    assert result.premium_ladder[3].unrounded_minor == Decimal("69402")
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True
