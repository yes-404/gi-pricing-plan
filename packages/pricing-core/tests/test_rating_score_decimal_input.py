"""SL-1543 RED 1: a non-money `decimal` input reaches the engine (FR-273).

The binding refuses a `Decimal` (`TypeError: argument 'ctx': unsupported type Decimal`, RL-1312's
probe), which `_score_context_sync` does not catch. A non-money `decimal` input crosses as the
float the JSON path delivers, checked lossless; money stays integer minor units. Pure: no
database."""

from __future__ import annotations

from decimal import Decimal

import pytest
from test_rating_score import _ctx, _FakeResolver, _version

from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import _score_context_sync, score_one

_INPUTS = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 5000,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}


async def _compiled_with_a_decimal_input() -> CompiledBundle:
    """The score fixture plus a non-money `decimal` input, `exposure_years`."""
    resolver = _FakeResolver()
    algorithm = resolver._payloads["rating_algorithm:score-fixture@1"]
    algorithm["input_contract"].append(
        {"name": "exposure_years", "type": "decimal", "nullable": False}
    )
    algorithm["steps"].insert(
        0,
        {"step_id": "s_in_exposure", "type": "input", "label": "Exposure",
         "input_name": "exposure_years", "on_missing": "error", "produces": "exposure_years"},
    )
    return load_bundle(await compile_bundle(_version(), resolver))


@pytest.mark.req("FR-273")
async def test_a_decimal_input_reaches_the_engine_on_the_sync_path() -> None:
    ctx = _ctx(inputs={**_INPUTS, "exposure_years": Decimal("0.75")})
    assert ctx.options is not None and ctx.options.rating_version_ref is not None
    result = _score_context_sync(
        await _compiled_with_a_decimal_input(), ctx, ctx.options.rating_version_ref
    )
    assert result.outputs["payable_premium_minor"] == 5250


@pytest.mark.req("FR-273")
async def test_a_decimal_input_reaches_the_engine_on_the_async_path() -> None:
    result = await score_one(
        await _compiled_with_a_decimal_input(),
        _ctx(inputs={**_INPUTS, "exposure_years": Decimal("0.75")}),
    )
    assert result.outputs["payable_premium_minor"] == 5250


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("value", [Decimal("0.12345678901234567"), Decimal("NaN")])
async def test_a_decimal_input_that_is_not_lossless_as_a_float_is_refused_by_name(
    value: Decimal,
) -> None:
    bundle = await _compiled_with_a_decimal_input()
    ctx = _ctx(inputs={**_INPUTS, "exposure_years": value})
    assert ctx.options is not None and ctx.options.rating_version_ref is not None
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'exposure_years'") as info:
        _score_context_sync(bundle, ctx, ctx.options.rating_version_ref)
    assert str(value) not in str(info.value)  # NFR-499: no quote value in the message
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'exposure_years'"):
        await score_one(bundle, ctx)
