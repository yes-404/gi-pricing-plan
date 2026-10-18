"""A model_call MOUNTED under a purpose is refused by the compile checks too (SL-1341, WK-1250).

`compile_bundle` runs the model_call checks on the base graph AND on every purpose graph
(`every_inlined`). A check called on `inlined` alone passes a model_call that only a purpose
mount carries, and the cancellation quote then scores it unchecked. Each test puts the
offending model_call in a fragment mounted for `cancellation` only; the base graph is clean.
"""

from __future__ import annotations

from typing import Any

import pytest
from test_rating_column_collision import algorithm as collision_algorithm
from test_rating_column_collision import two_factors_one_column_world
from test_rating_gbm_banded_refusal import (
    CODE as GBM_CODE,
)
from test_rating_gbm_banded_refusal import (
    _age_world,
)
from test_rating_gbm_banded_refusal import _algorithm as gbm_algorithm
from test_rating_gbm_banded_refusal import (
    _Resolver as _GbmResolver,
)
from test_rating_gbm_banded_refusal import _version as gbm_version
from test_rating_glm_model_call import GlmResolver
from test_rating_glm_model_call import version as glm_version

from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle

_FRAGMENT_REF = "sub_graph:risk-probe@1"


def _split(algorithm: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Move the algorithm's one model_call into a `cancellation` fragment.

    The base keeps a constant-free stand-in producing the same `risk`, so it is valid alone and
    the mount re-produces `risk` (reading it first, as a re-production must) for the
    cancellation purpose only.
    """
    call = next(s for s in algorithm["steps"] if s["type"] == "model_call")
    names = sorted(call["feature_map"])
    stand_in = {
        "step_id": "s_risk_base",
        "type": "expression",
        "label": "Base risk",
        "expr": f"{names[0]} * 1",
        "result_type": "decimal",
        "consumes": [names[0]],
        "produces": "risk",
    }
    base = {
        **algorithm,
        "steps": [stand_in if s is call else s for s in algorithm["steps"]],
        "sub_graphs": [
            {
                "ref": _FRAGMENT_REF,
                "mount_point": "m_risk",
                "purposes": ["cancellation"],
                "inputs": {**{n: n for n in names}, "risk_in": "risk"},
                "outputs": {"risk_m": "risk"},
            }
        ],
    }
    types = {c["name"]: c["type"] for c in algorithm["input_contract"]}
    fragment = {
        "slug": "risk-probe",
        "version": 1,
        "inputs": [
            *({"name": n, "type": types.get(n, "int")} for n in names),
            {"name": "risk_in", "type": "decimal"},
        ],
        "outputs": [{"name": "risk_m", "type": "decimal", "required": True}],
        "steps": [{**call, "consumes": [*names, "risk_in"], "produces": ["risk_m"]}],
        "change_note": "first cut",
    }
    return base, fragment


class _Mounting:
    """Serves the split algorithm and the fragment; every other ref goes to the inner resolver."""

    def __init__(self, inner: Any, algorithm: dict[str, Any], fragment: dict[str, Any]) -> None:
        self._inner, self._algorithm, self._fragment = inner, algorithm, fragment

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if ref.type == "rating_algorithm":
            return ResolvedArtifact(status="no_maturity_concept", payload=self._algorithm)
        if ref.type == "sub_graph":
            return ResolvedArtifact(status="no_maturity_concept", payload=self._fragment)
        return await self._inner.resolve(ref)


def _pinned(version: Any) -> Any:
    pins = version.pins
    return version.model_copy(
        update={
            "pins": pins.model_copy(update={"sub_graphs": [ArtifactRef.parse(_FRAGMENT_REF)]}),
        }
    )


@pytest.mark.req("FR-222", "FR-240", "FR-218")
async def test_a_mounted_banded_gbm_model_call_is_refused_at_compile() -> None:
    world = _age_world("xgboost")
    base, fragment = _split(gbm_algorithm(world))
    resolver = _Mounting(_GbmResolver(world), base, fragment)
    with pytest.raises(ValueError, match=GBM_CODE) as caught:
        await compile_bundle(_pinned(gbm_version()), resolver)
    assert world.factor.slug in str(caught.value)


@pytest.mark.req("FR-222", "FR-240", "FR-218")
async def test_a_mounted_column_collision_is_refused_at_compile() -> None:
    world = two_factors_one_column_world()
    fmap = {"driver_age": "age_fine", "driver_age_adj": "age_coarse"}
    base, fragment = _split(collision_algorithm(fmap))
    resolver = _Mounting(GlmResolver(world), base, fragment)
    with pytest.raises(ValueError, match=r"^MODEL_CALL_FEATURE_MAP_INVALID: ") as caught:
        await compile_bundle(_pinned(glm_version()), resolver)
    assert "age_fine" in str(caught.value)
    assert "age_coarse" in str(caught.value)
