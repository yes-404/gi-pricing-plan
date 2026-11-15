"""The rating path refuses a dummy term its input's numeric type cannot produce (FR-193, FR-222).

A GLM fitted on a text column has a dummy `veh_count[3+]`. A quote supplies `veh_count` as an
INT, so the column the scorer reads is an `Int64` and `3+` is a level it can never produce: that
term has an indicator of 0 on every row, wherever it is listed among the coefficients. The
`model_call` fails `MODEL_CALL_FAILED` carrying `MODEL_TERM_UNRESOLVED` for every quote on that
path, and the text names no value.
"""

from __future__ import annotations

import math
from typing import Any
from uuid import uuid4

import pytest
from test_rating_glm_model_call import GlmWorld, _value, algorithm_payload, compiled_bundle

from model_schema import (
    Coefficient,
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    OffsetSpec,
    RelativityLevel,
)
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, load_bundle

B0 = 0.5


def _coefficient(term: str, estimate: float) -> Coefficient:
    return Coefficient(
        term=term, estimate=estimate, std_error=0.1, z=1.0, p_value=0.5,
        ci_95=(estimate - 0.2, estimate + 0.2),
    )


def _world() -> GlmWorld:
    dataset = uuid4()
    factor = Factor(
        id=uuid4(), slug="veh_count", dataset_id=dataset, version=1, type=FactorType.IDENTITY,
        source_columns=("veh_count",),
    )
    spec = GlmSpec(
        model_family_slug="motor-freq-glm", dataset_version_id=dataset, response_column="claims",
        offset=OffsetSpec(), factors=(factor.id,), family="gamma", link="log",
    )
    fit = GlmFitResult(
        converged=True, iterations=1, fit_seconds=0.0, rows=100,
        coefficients=(
            _coefficient("intercept", B0),
            _coefficient("veh_count[1]", 0.2),  # a term the INT column can produce, listed first
            _coefficient("veh_count[3+]", 0.7),  # one it cannot, listed second
        ),
        relativities={
            "veh_count": (
                RelativityLevel(level="0", is_base=True),
                RelativityLevel(level="1"),
                RelativityLevel(level="3+"),
            )
        },
    )
    return GlmWorld(spec, fit, (factor,), (), ())


def _algorithm() -> dict[str, Any]:
    payload = algorithm_payload(feature_map={"veh_count": "veh_count"})
    payload["input_contract"] = [{"name": "veh_count", "type": "int", "nullable": False}]
    payload["steps"] = [
        {"step_id": "s_veh", "type": "input", "label": "Vehicles", "input_name": "veh_count",
         "on_missing": "error", "produces": "veh_count"},
        next(s for s in payload["steps"] if s["type"] == "model_call"),
        next(s for s in payload["steps"] if s["type"] == "output"),
    ]
    payload["steps"][1]["consumes"] = ["veh_count"]
    return payload


@pytest.mark.req("FR-193", "FR-222")
async def test_a_quote_on_a_term_its_int_input_cannot_produce_is_refused() -> None:
    compiled = load_bundle(await compiled_bundle(_world(), _algorithm()))
    result = await _value(compiled, veh_count=4)

    assert MODEL_CALL_ERROR_KEY in result, (
        f"scored {result.get('risk')!r} (exp(b0) is {math.exp(B0)!r}): the quote must be refused"
    )
    message = result[MODEL_CALL_ERROR_KEY]
    assert "MODEL_TERM_UNRESOLVED" in message
    assert "4" not in message.replace("MODEL_TERM_UNRESOLVED", "")  # no quote value in the text
