"""FR-240's completeness clause at compile (`PL-1540`, SL-1541; `RL-1523`).

`compile_bundle` refuses a `model_call` whose `feature_map` does not map every input its
pinned model requires: its Factors, or its `feature_order` when it has none, and for a
`peril_structure_ref` step each component model's. Membership (a mapped name the model does
not take) is the save check's (A-2); this is completeness only. The helpers are the
neighbouring modules' (`test_rating_compile_bundle`, `test_rating_peril_scoring`).
"""

from __future__ import annotations

from typing import Any

import pytest
from test_rate_table_operations import _factor
from test_rating_compile_bundle import FakeResolver, _version, valid_algorithm_payload
from test_rating_compile_fr240 import _FactorsResolver
from test_rating_peril_scoring import (
    AD_FREQ,
    AD_SEV,
    STRUCTURE,
    WS_BC,
    _peril_algorithm,
    _peril_version,
)
from test_rating_peril_scoring import _resolver as _peril_resolver

from pricing_core.modelling import factors as factors_module
from pricing_core.rating import compile as compile_module
from pricing_core.rating.compile import compile_bundle

MODEL = "model:motor-ad-frequency@7"
CODE = r"^MODEL_CALL_FEATURE_MAP_INVALID: "

#: The `s_rp` step of `valid_algorithm_payload` consumes these two graph names.
FULL_MAP = {"driver_age": "driver_age_band", "rating_area": "area_group"}


def _set_map(step: dict[str, Any], feature_map: dict[str, str]) -> None:
    """Set the map and declare what it reads (FR-246: a step reads only what it consumes)."""
    step["feature_map"] = feature_map
    step["consumes"] = sorted({*step["consumes"], *feature_map})


def _algorithm(feature_map: dict[str, str]) -> dict[str, Any]:
    algorithm = valid_algorithm_payload()
    step = next(s for s in algorithm["steps"] if s["step_id"] == "s_rp")
    _set_map(step, feature_map)
    return algorithm


def _glm_world(feature_map: dict[str, str]) -> FakeResolver:
    """A model with two Factors (a GLM's required inputs) and the step's map set."""
    payloads: dict[str, Any] = {
        "rating_algorithm:motor-gb@14": _algorithm(feature_map),
        "rate_table:motor-expense@3": {"rateable": True, "rows": []},
        "model:motor-ad-frequency@7": {"model_type": "glm", "status": "approved"},
        "reference_table:ons-postcode-directory@7": {"rows": []},
    }
    return _FactorsResolver(
        FakeResolver(payloads),
        {MODEL: (_factor("driver_age_band"), _factor("area_group"))},
    )


def _gbm_world(feature_map: dict[str, str]) -> FakeResolver:
    """A GBM with no Factors: its `feature_order` is the required inputs."""
    world = _glm_world(feature_map)
    world._payloads[MODEL] = {
        "model_type": "gbm",
        "status": "approved",
        "fit_result": {"model_type": "xgboost", "feature_order": ["age_years", "vehicle_power"]},
    }
    world._factors = {}
    return world


def _peril_world(feature_map: dict[str, str]) -> FakeResolver:
    """AD frequency needs `driver_age_band`; AD severity also `vehicle_group`."""
    algorithm = _peril_algorithm()
    step = next(s for s in algorithm["steps"] if s["step_id"] == "s_rp")
    _set_map(step, feature_map)
    base = _peril_resolver(algorithm=algorithm)
    band, group = _factor("driver_age_band"), _factor("vehicle_group")
    return _FactorsResolver(
        base, {AD_FREQ: (band,), AD_SEV: (band, group), WS_BC: (band,)}
    )


@pytest.mark.req("FR-240")
async def test_a_glm_model_call_missing_a_factor_is_refused_at_compile() -> None:
    world = _glm_world({"driver_age": "driver_age_band"})
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), world)
    message = str(caught.value)
    assert "'s_rp'" in message
    assert MODEL in message
    assert "area_group" in message
    assert "driver_age_band" not in message  # a mapped feature is never named as missing


@pytest.mark.req("FR-240")
async def test_a_gbm_model_call_missing_a_feature_order_entry_is_refused_at_compile() -> None:
    world = _gbm_world({"driver_age": "age_years"})
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), world)
    message = str(caught.value)
    assert "'s_rp'" in message
    assert "vehicle_power" in message
    assert "age_years" not in message


@pytest.mark.req("FR-240")
async def test_a_peril_model_call_starving_one_component_is_refused_at_compile() -> None:
    world = _peril_world({"driver_age": "driver_age_band"})
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_peril_version(), world)
    message = str(caught.value)
    assert "'s_rp'" in message
    assert STRUCTURE in message
    assert "AD" in message
    assert "severity_model" in message
    assert AD_SEV in message
    assert "vehicle_group" in message
    assert AD_FREQ not in message  # the frequency component is complete


@pytest.mark.req("FR-240")
async def test_an_empty_feature_map_is_refused_when_the_model_has_inputs() -> None:
    """R-a (RL-1445's 19:03:24 ruling, item 4): `{}` maps nothing, so it is not an identity map."""
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _gbm_world({}))
    message = str(caught.value)
    assert "age_years" in message
    assert "vehicle_power" in message


@pytest.mark.req("FR-240")
@pytest.mark.parametrize(
    ("world", "version"),
    [
        (lambda: _glm_world(FULL_MAP), _version),
        (lambda: _gbm_world({"driver_age": "age_years", "rating_area": "vehicle_power"}), _version),
        (
            lambda: _peril_world(
                {"driver_age": "driver_age_band", "channel": "vehicle_group"}
            ),
            _peril_version,
        ),
        # extra entries beyond the required inputs are never refused (membership is A-2's)
        (lambda: _glm_world({**FULL_MAP, "channel": "not_a_factor"}), _version),
    ],
    ids=["glm", "gbm", "peril", "surplus"],
)
async def test_a_complete_feature_map_compiles(world: Any, version: Any) -> None:
    bundle = await compile_bundle(version(), world())
    assert bundle.content_hash.startswith("sha256:")


@pytest.mark.req("FR-240")
async def test_an_unmapped_offset_column_is_not_a_completeness_failure() -> None:
    """The offset column is not a Factor (A-2's R2): a GLM with a `log_column` offset on
    `exposure`, every Factor mapped, `exposure` not in the map, compiles."""
    world = _glm_world(FULL_MAP)
    world._payloads[MODEL]["spec"] = {"offset": {"kind": "log_column", "column": "exposure"}}
    bundle = await compile_bundle(_version(), world)
    assert bundle.content_hash.startswith("sha256:")


@pytest.mark.req("FR-240")
async def test_the_compile_check_calls_the_one_required_inputs_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []
    real = factors_module.required_model_inputs

    def spy(factors: Any, feature_order: Any) -> tuple[str, ...]:
        result = real(factors, feature_order)
        calls.append(result)
        return result

    monkeypatch.setattr(compile_module, "required_model_inputs", spy)
    await compile_bundle(_version(), _glm_world(FULL_MAP))
    assert calls == [("driver_age_band", "area_group")]
