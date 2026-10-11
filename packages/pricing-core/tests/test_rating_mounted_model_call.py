"""A `model_call` inside a mounted sub-graph scores as the same step unmounted (FR-217, FR-222).

`feature_map` KEYS are graph value names and are renamed on inlining; its VALUES are the
model's feature names (FR-222) and are never renamed (the maintainer's ruling, `to-lead.md`
"2026-10-10 23:46:57 BST — RULING (mispricing) …"). One key is a mapped input port, one is
a fragment-internal name; one VALUE equals a fragment-internal name and must stay as written.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
import xgboost as xgb
from test_rating_runtime import _gbm_model_payload

from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, load_bundle

FRAGMENT = "sub_graph:risk-call@1"
MODEL = "model:two-feature@1"
#: The second feature is named `power`: the same word as the fragment's internal value.
FEATURES = ["age_years", "power"]


def _booster() -> bytes:
    x = [[20.0, 40.0], [30.0, 60.0], [40.0, 80.0], [50.0, 100.0], [60.0, 120.0]]
    y = [1000.0, 1200.0, 1500.0, 1800.0, 2000.0]
    dtrain = xgb.DMatrix(x, label=y, feature_names=FEATURES)
    booster = xgb.train({"objective": "reg:squarederror", "max_depth": 2}, dtrain, 3)
    return bytes(booster.save_raw(raw_format="json"))


_STEPS: list[dict[str, Any]] = [
    {"step_id": "s_power", "type": "expression", "label": "Power", "expr": "driver_age * 2",
     "result_type": "decimal", "consumes": ["driver_age"], "produces": "power"},
    {"step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": MODEL,
     "mode": "exact", "feature_map": {"driver_age": "age_years", "power": "power"},
     "result_type": "decimal", "consumes": ["driver_age", "power"], "produces": ["risk"]},
]


def _algorithm(*, mounted: bool) -> dict[str, Any]:
    steps: list[dict[str, Any]] = [
        {"step_id": "s_age", "type": "input", "label": "Age", "input_name": "driver_age",
         "on_missing": "error", "produces": "driver_age"},
        *([] if mounted else _STEPS),
        {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
         "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
    ]
    return {
        "slug": "mounted-call", "version": 1,
        "input_contract": [{"name": "driver_age", "type": "int", "nullable": False}],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": steps,
        "sub_graphs": (
            [{"ref": FRAGMENT, "mount_point": "m_call",
              "inputs": {"driver_age": "driver_age"}, "outputs": {"risk": "risk"}}]
            if mounted else []
        ),
    }


def _fragment() -> dict[str, Any]:
    return {
        "slug": "risk-call", "version": 1,
        "inputs": [{"name": "driver_age", "type": "int"}],
        "outputs": [{"name": "risk", "type": "decimal", "required": True}],
        "steps": _STEPS, "change_note": "first cut",
    }


class _Resolver:
    def __init__(self, *, mounted: bool) -> None:
        model = _gbm_model_payload(_booster())
        model["fit_result"]["feature_order"] = FEATURES
        self._payloads = {
            "rating_algorithm:mounted-call@1": _algorithm(mounted=mounted),
            FRAGMENT: _fragment(),
            MODEL: model,
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        exempt = ref.type in {"rating_algorithm", "sub_graph"}
        return ResolvedArtifact(
            status="no_maturity_concept" if exempt else "approved",
            payload=self._payloads[str(ref)],
        )


def _version(*, mounted: bool) -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "mounted-call", "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": MODEL,
        "created_at": "2026-10-10T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-10-10T12:00:00Z", "algorithm_ref": "rating_algorithm:mounted-call@1",
        "pins": {"rate_tables": [], "models": [MODEL], "reference_tables": [],
                 "custom_objectives": [], "sub_graphs": [FRAGMENT] if mounted else []},
        "model_reference_mode": "exact",
    })


async def _risk(*, mounted: bool, age: int) -> Any:
    bundle = await compile_bundle(_version(mounted=mounted), _Resolver(mounted=mounted))
    out = await load_bundle(bundle).decision.async_evaluate({"driver_age": age})
    result = out["result"]
    assert MODEL_CALL_ERROR_KEY not in result, result
    return result["risk"]


@pytest.mark.req("FR-217", "FR-222")
@pytest.mark.parametrize("age", [25, 34, 61])
async def test_a_mounted_model_call_prices_the_same_as_the_unmounted_step(age: int) -> None:
    """Keys: the mapped port `driver_age` and the internal `power`; value: `power` itself."""
    assert await _risk(mounted=True, age=age) == await _risk(mounted=False, age=age)
