"""A ladder that does not reconcile is refused (`RL-1346`, PL-1348 Acceptance 5 items 1, 2, 6, 9).

"Planted" is a test-only mutation of the real builder's output (`_build_ladder`), one rung one
minor unit off. Item 2 is authored, not planted: a clamp whose `condition` and `clamp_bounds`
disagree on a binding quote. The route cases (3, 4, 5) are in `backend/tests/test_score.py`.
"""

from __future__ import annotations

from typing import Any

import polars as pl
import pytest
from test_rating_ladder_exact import (
    _CLAMP_INPUTS,
    _chain_algorithm,
    _clamp_variant,
    _compile_payload,
    _context,
    _score_fixture,
)
from test_rating_score import _RATING_VERSION_REF

from model_schema.scoring import LadderRung
from pricing_core.rating import score as score_module
from pricing_core.rating.score import score_batch, score_one

_CODE = "LADDER_RECONCILIATION_FAILED"
_SENTINEL = "SENTINEL-quote-input-5e21c4"


def _plant_one_unit_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """The builder's real ladder with the second rung's displayed value one minor unit off."""
    real = score_module._build_ladder

    def off_by_one(inputs: Any, codes: Any) -> list[LadderRung]:
        ladder = real(inputs, codes)
        ladder[1] = ladder[1].model_copy(update={"value_minor": ladder[1].value_minor + 1})
        return ladder

    monkeypatch.setattr(score_module, "_build_ladder", off_by_one)


@pytest.mark.req("FR-248")
@pytest.mark.parametrize("trace", [True, False])
async def test_a_planted_one_unit_off_ladder_is_refused_traced_and_untraced(
    monkeypatch: pytest.MonkeyPatch, trace: bool
) -> None:
    bundle = await _compile_payload(_score_fixture())
    ctx = _context(**{**_CLAMP_INPUTS, "min_premium_minor": 0})
    assert (await score_one(bundle, ctx, trace=trace)).outcome == "quoted"  # the control
    _plant_one_unit_off(monkeypatch)
    with pytest.raises(ValueError, match=_CODE) as caught:
        await score_one(bundle, ctx, trace=trace)
    assert type(caught.value).__name__ == "CodedError"
    assert str(caught.value).startswith(f"{_CODE}: ")


@pytest.mark.req("FR-248")
async def test_an_authored_r0_case_is_refused_through_score_one() -> None:
    """A clamp whose condition says the quote is fine while its bound binds (`RL-1329` S5)."""
    always_ok = _clamp_variant({"min": "min_premium_minor"}, "office_premium_minor >= 0")
    bundle = await _compile_payload(always_ok)
    with pytest.raises(ValueError, match=_CODE) as caught:
        await score_one(bundle, _context(**_CLAMP_INPUTS))
    assert "R0" in str(caught.value)
    assert "s_clamp" in str(caught.value)


@pytest.mark.req("FR-248")
async def test_the_message_names_the_clause_the_rungs_and_the_difference_never_an_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = await _compile_payload(_chain_algorithm(
        factors=[("office_premium", "{prev} * 1.1", "half_even")]
    ))
    ctx = _context(risk_premium_minor=61234.5).model_copy(update={"quote_id": _SENTINEL})
    _plant_one_unit_off(monkeypatch)
    with pytest.raises(ValueError, match=_CODE) as caught:
        await score_one(bundle, ctx)
    message = str(caught.value)
    assert _SENTINEL not in message
    assert "office_premium" in message
    assert any(clause in message for clause in ("R1", "R2", "R3", "R4"))


@pytest.mark.req("FR-255")
async def test_batch_writes_one_error_row_and_one_scored_row_and_no_sentinel() -> None:
    always_ok = _clamp_variant({"min": "min_premium_minor"}, "office_premium_minor >= 0")
    bundle = await _compile_payload(always_ok)
    base = {
        "purpose": "new_business", "effective_date": "2026-09-01",
        "rating_version_ref": str(_RATING_VERSION_REF), **_CLAMP_INPUTS,
    }
    frame = pl.DataFrame([
        {**base, "quote_id": _SENTINEL},                          # the clamp binds: R0 fails
        {**base, "quote_id": "good", "min_premium_minor": 0},      # it does not: reconciles
    ]).lazy()
    rows = {r["quote_id"]: r for r in score_batch(bundle, frame).collect().to_dicts()}
    bad, good = rows[_SENTINEL], rows["good"]
    assert (bad["outcome"], bad["error_code"]) == ("error", _CODE)
    assert _SENTINEL not in str(bad["error_message"])
    assert good["outcome"] == "quoted"
    assert good["error_code"] in (None, "")


@pytest.mark.req("FR-248")
async def test_controls_a_correct_ladder_is_served_with_version_2_and_an_empty_one_is_not() -> None:
    bundle = await _compile_payload(_score_fixture())
    unclamped = _context(**{**_CLAMP_INPUTS, "min_premium_minor": 0})
    result = await score_one(bundle, unclamped, trace=True)
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True
    assert result.trace.ladder_check_version == 2

    only = _chain_algorithm(factors=[])
    dropped = ("s_out_risk", "s_out_payable")
    only["steps"] = [s for s in only["steps"] if s["step_id"] not in dropped]
    only["outputs"] = []
    empty = await score_one(await _compile_payload(only), _context(risk_premium_minor=1000))
    assert empty.premium_ladder == []
