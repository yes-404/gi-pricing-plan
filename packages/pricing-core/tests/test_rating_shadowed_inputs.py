"""FD-1425 (the emergency slice): a quote input never overrides a produced value (FR-213).

(3f) and the per-name cases are auditor-premise's measurements at 4d3be141."""

from __future__ import annotations

from typing import Any

import polars as pl
import pytest
from test_rating_score import _ctx, _FakeResolver, _version

from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch, score_one

_BASE_INPUTS: dict[str, Any] = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 5000,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}
#: Every name a non-`input` step of the score fixture produces (`_algorithm_payload`).
_PRODUCED = ["expense_factor", "risk_premium_minor", "office_premium_minor",
             "instalment_loading_minor"]


async def _compiled() -> CompiledBundle:
    return load_bundle(await compile_bundle(_version(), _FakeResolver()))


@pytest.mark.req("FR-213")
async def test_the_ordered_no_key_quote_is_unchanged() -> None:
    result = await score_one(await _compiled(), _ctx(inputs=dict(_BASE_INPUTS)))
    assert result.outputs["payable_premium_minor"] == 5250


@pytest.mark.req("FR-213")
async def test_the_3f_case_is_refused() -> None:
    """auditor-premise (3f): payable 777 against 5250, on the CORRECTLY ordered fixture."""
    ctx = _ctx(inputs={**_BASE_INPUTS, "instalment_loading_minor": 777})
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'instalment_loading_minor'"):
        await score_one(await _compiled(), ctx)


@pytest.mark.req("FR-213")
@pytest.mark.parametrize("name", _PRODUCED)
async def test_an_undeclared_key_naming_a_produced_value_is_refused(name: str) -> None:
    ctx = _ctx(inputs={**_BASE_INPUTS, name: 777})
    with pytest.raises(ValueError, match=f"INPUT_CONTRACT_VIOLATION.*'{name}'"):
        await score_one(await _compiled(), ctx)


@pytest.mark.req("FR-213")
@pytest.mark.parametrize("name", _PRODUCED)
async def test_an_undeclared_key_naming_a_produced_value_is_refused_in_a_batch(
    name: str,
) -> None:
    """The same refusal on `_score_context_sync`. The row's shape is
    `test_quote_input_raise_sites.py`'s `_row` (`:221-228`)."""
    options = _ctx(inputs=dict(_BASE_INPUTS)).options
    assert options is not None
    assert options.rating_version_ref is not None
    row = {"quote_id": "Q1", "purpose": "new_business", "effective_date": "2026-09-01",
           "rating_version_ref": str(options.rating_version_ref), **_BASE_INPUTS, name: 777}
    out = score_batch(await _compiled(), pl.DataFrame([row]).lazy()).collect().to_dicts()[0]
    assert out["outcome"] == "error"
    assert out["error_code"] == "INPUT_CONTRACT_VIOLATION", out
    assert f"'{name}'" in out["error_message"]


#: Recorded at the slice's base commit (4f9c19c2) in Task 1 Step 4, before any code change;
#: two runs gave the same value.
_SCORE_FIXTURE_HASH = "sha256:86abdb81dc16d2075956aa11e05f2e9c87fe191d4a3397574e5a82520039073d"


@pytest.mark.req("FR-213")
async def test_the_bundle_hash_is_unchanged() -> None:
    bundle = await compile_bundle(_version(), _FakeResolver())
    assert bundle.content_hash == _SCORE_FIXTURE_HASH
