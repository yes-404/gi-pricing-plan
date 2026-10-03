"""The scale sweep of `RL-1329` Acceptance 2, through a real ZEN evaluation.

Every decade from 1e3 to 1e7 minor units; 0 to 6 optional rungs; float32 risk values; 4 dp
table factors; one gross-up rung; one `add` rung; one mixed-operation run; 200 quotes per
cell; two recorded seeds. The same sweep over `origin/main`'s builder
(`baseline_ladder.py`) is shown to fail, which proves the sweep can print a failure
(CLAUDE.md §13).
"""

from __future__ import annotations

import random
from decimal import Decimal
from typing import Any

import numpy as np
import pytest
from baseline_ladder import _build_ladder as baseline_build_ladder
from test_rating_ladder_exact import _chain_algorithm, _compile_payload

from pricing_core.rating import score as score_module
from pricing_core.rating.ladder import ladder_violations, round_once
from pricing_core.rating.runtime import CompiledBundle, exact_key

SEEDS = (20260930, 7)
QUOTES_PER_CELL = 200
DECADES = (3, 4, 5, 6, 7)

#: the six optional rungs a chain can carry, each with a 4 dp table factor
_OPTIONAL = (
    ("expense_loading", "1.15"),
    ("commission", "1.131"),
    ("profit_loading", "1.07"),
    ("office_premium", "0.9601"),
    ("optimisation_adjustment", "1.05"),
    ("instalment_loading", "1.12"),
)


def _config(kind: str, count: int) -> tuple[list[tuple[str, str, str]], dict[str, Decimal]]:
    """`(factors, single-operation operands by rung)` for one sweep configuration."""
    factors: list[tuple[str, str, str]] = []
    operands: dict[str, Decimal] = {}
    for index, (rung, factor) in enumerate(_OPTIONAL[:count]):
        if kind == "grossup" and index == 1:
            factors.append((rung, "0.875 > 0 ? {prev} / 0.875 : 0", "half_even"))
        elif kind == "mixed" and index == 2:
            factors.append((rung, "{prev} * 1.05 + 12.345", "half_even"))
        else:
            factors.append((rung, f"{{prev}} * {factor}", "half_even"))
            operands[rung] = Decimal(factor)
    if kind == "add":
        factors.append(("ipt_and_fees", "{prev} + 38.4", "half_even"))
    return factors, operands


def _quotes(seed: int, decade: int, n: int) -> list[float]:
    rng = random.Random(seed * 1000 + decade)
    return [
        float(np.float32(10 ** (decade + rng.uniform(0.0, 0.99999))))  # float32 risk values
        for _ in range(n)
    ]


def _engine(bundle: CompiledBundle, risk: float) -> dict[str, Any]:
    context = {"effective_date": "2026-09-01", "purpose": "new_business",
               "risk_premium_minor": risk}
    return bundle.decision.evaluate(context)["result"]  # type: ignore[no-any-return]


def _exact_of(result: dict[str, Any], source: str) -> Decimal:
    return Decimal(result[exact_key(source)])


async def _sweep(kind: str, count: int, seed: int, decade: int, n: int) -> None:
    factors, operands = _config(kind, count)
    payload = _chain_algorithm(factors=factors)
    bundle = await _compile_payload(payload)
    sources = {
        s["output_name"]: s["consumes"][0] for s in payload["steps"] if s["type"] == "output"
    }
    for risk in _quotes(seed, decade, n):
        result = _engine(bundle, risk)
        ladder_inputs = score_module._ladder_inputs(bundle.algorithm, result, [])
        ladder = score_module._build_ladder(ladder_inputs, [])
        where = f"{kind}/{count} seed={seed} decade={decade} risk={risk!r}"
        assert ladder_violations(ladder, ladder_inputs) == [], where
        for rung in ladder:
            if rung.rung == "constraints":
                continue
            exact = _exact_of(result, sources[f"{rung.rung}_minor"])
            assert rung.value_minor == round_once(exact, rung.rounding), where  # type: ignore[arg-type]
            operand = operands.get(rung.rung)
            if operand is not None and rung.operation is not None:
                assert rung.operation.kind == "multiply", where
                assert rung.operation.factor == operand, f"{where} {rung.rung}"


_CONFIGS = (
    *(("plain", k) for k in range(7)),
    ("grossup", 3),
    ("add", 3),
    ("mixed", 4),
)


@pytest.mark.req("NFR-496")
@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("decade", DECADES)
async def test_the_scale_sweep_reconciles_every_quote(seed: int, decade: int) -> None:
    for kind, count in _CONFIGS:
        await _sweep(kind, count, seed, decade, QUOTES_PER_CELL)


@pytest.mark.req("NFR-496")
async def test_the_same_sweep_over_mains_builder_fails() -> None:
    """Acceptance 2: the baseline's displayed rungs drift from the engine's value rounded
    once (the 4 dp factor it derives from the previous *rounded* rung), so the sweep's
    `value_minor` assertion has something to print."""
    failures = 0
    checked = 0
    for kind, count in (("plain", 4), ("plain", 6)):
        factors, _ = _config(kind, count)
        payload = _chain_algorithm(factors=factors)
        bundle = await _compile_payload(payload)
        sources = {
            s["output_name"]: s["consumes"][0] for s in payload["steps"] if s["type"] == "output"
        }
        for risk in _quotes(SEEDS[0], 7, 60):
            result = _engine(bundle, risk)
            old, _ = baseline_build_ladder(bundle.algorithm, result, [])
            for rung in old:
                if rung.rung == "constraints":
                    continue
                exact = _exact_of(result, sources[f"{rung.rung}_minor"])
                checked += 1
                if rung.value_minor != int(exact.quantize(Decimal(1), rounding="ROUND_HALF_EVEN")):
                    failures += 1
    assert checked > 0
    assert failures > 0, "the sweep must be able to fail over origin/main's builder"
