"""The save check refuses a `model_call` that pins a GBM fitted on a banded or grouped Factor
(SL 8071; FD 8073 (to be filed after the probe run); FR-222 as amended 2026-10-16).

`check_model_call_feature_maps` runs at `POST /api/v1/rating-algorithms`, `POST
/api/v1/sub-graphs` and `POST /api/v1/sub-graphs/{slug}/versions`; the three share it, so it is
tested once here, without a database: the Model row and its Factors are served by a stand-in
session, the way the check reads them. Case C (bands labelled "1", "2", "3" and an int raw 2)
and case A (a raw `driver_age`) are the probe's: see
`packages/pricing-core/tests/test_rating_gbm_banded_refusal.py` for the compile half.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

import app.platform.rating_algorithms as algorithms_module
from app.errors import RATING_ERROR_CODES, PlatformError
from model_schema import (
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    OffsetSpec,
    SplitRef,
)
from model_schema.rating import RatingModelCallStep
from model_schema.refs import ArtifactRef

DATASET = uuid4()
MODEL = "model:banded-gbm@1"
CODE = "MODEL_CALL_GBM_TRANSFORMED_FACTOR"


def _factor(slug: str, column: str, kind: FactorType) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=DATASET, version=1, type=kind,
        source_columns=(column,),
        banding_id=uuid4() if kind is FactorType.BANDING else None,
        grouping_id=uuid4() if kind is FactorType.GROUPING else None,
    )


def _gbm_row(factors: tuple[Factor, ...]) -> Any:
    spec = GbmSpec(
        model_type="xgboost", model_family_slug="banded-gbm", dataset_version_id=DATASET,
        split_ref=SplitRef(split_artifact_id=uuid4()), response_column="severity",
        offset=OffsetSpec(kind="none"),
        objective=GbmFunctionRef(kind="builtin", name="reg:gamma"),
        categorical_handling="native", hyperparameters={}, early_stopping=None,
        factors=tuple(factor.id for factor in factors),
    )
    return SimpleNamespace(
        spec=spec.model_dump(mode="json"),
        fit_result={"feature_order": [factor.slug for factor in factors]},
    )


def _glm_row(factors: tuple[Factor, ...]) -> Any:
    spec = GlmSpec(
        model_family_slug="banded-glm", dataset_version_id=DATASET,
        response_column="severity", offset=OffsetSpec(),
        factors=tuple(factor.id for factor in factors), family="gamma", link="log",
    )
    return SimpleNamespace(
        spec=spec.model_dump(mode="json"),
        fit_result={"feature_order": [factor.slug for factor in factors]},
    )


class _Session:
    """Serves the one Model row the check selects."""

    def __init__(self, row: Any) -> None:
        self._row = row

    async def scalar(self, statement: Any) -> Any:
        return self._row


def _serve(monkeypatch: pytest.MonkeyPatch, factors: tuple[Factor, ...]) -> None:
    async def load_factors(session: Any, **kwargs: Any) -> list[Factor]:
        return list(factors)

    monkeypatch.setattr(algorithms_module, "load_factors", load_factors)


def _step(feature_map: dict[str, str], **ref: str) -> RatingModelCallStep:
    return RatingModelCallStep.model_validate({
        "step_id": "s_risk", "type": "model_call", "label": "Risk", "mode": "exact",
        "feature_map": feature_map, "consumes": sorted(feature_map), "produces": ["risk"],
        "result_type": "decimal", **({"model_ref": MODEL} if not ref else ref),
    })


async def _check(row: Any, step: RatingModelCallStep) -> None:
    await algorithms_module.check_model_call_feature_maps(
        _Session(row), uuid4(), [step]  # type: ignore[arg-type]
    )


def test_the_code_is_a_rating_error_code() -> None:
    assert CODE in RATING_ERROR_CODES


@pytest.mark.req("FR-222")
async def test_case_c_a_gbm_on_numeric_looking_band_labels_is_refused_at_save(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case C: `veh_power` banded and labelled "1", "2", "3" (the SILENT case)."""
    band = _factor("veh_power_band", "veh_power", FactorType.BANDING)
    _serve(monkeypatch, (band,))
    with pytest.raises(PlatformError) as caught:
        await _check(_gbm_row((band,)), _step({"veh_power": "veh_power_band"}))
    assert caught.value.code == CODE
    assert caught.value.status_code == 422
    detail = caught.value.detail
    for named in ("s_risk", MODEL, "veh_power_band", "banding"):
        assert named in detail


@pytest.mark.req("FR-222")
async def test_case_a_a_raw_value_into_a_banded_gbm_is_refused_at_save(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case A: the graph's raw `driver_age` is mapped onto the banded Factor's slug."""
    band = _factor("driver_age_band", "driver_age", FactorType.BANDING)
    _serve(monkeypatch, (band,))
    with pytest.raises(PlatformError) as caught:
        await _check(_gbm_row((band,)), _step({"driver_age": "driver_age_band"}))
    assert caught.value.code == CODE


@pytest.mark.req("FR-222")
async def test_a_grouped_factor_is_refused_at_save(monkeypatch: pytest.MonkeyPatch) -> None:
    group = _factor("area_group", "area", FactorType.GROUPING)
    _serve(monkeypatch, (group,))
    with pytest.raises(PlatformError) as caught:
        await _check(_gbm_row((group,)), _step({"area": "area_group"}))
    assert caught.value.code == CODE
    assert "grouping" in caught.value.detail


@pytest.mark.req("FR-222")
async def test_each_component_of_a_peril_structure_is_checked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    band = _factor("driver_age_band", "driver_age", FactorType.BANDING)
    _serve(monkeypatch, (band,))

    async def components(session: Any, workspace_id: Any, ref: Any) -> list[ArtifactRef]:
        return [ArtifactRef.model_validate(MODEL)]

    monkeypatch.setattr(algorithms_module, "_component_model_refs", components)
    step = _step({"driver_age": "driver_age_band"}, peril_structure_ref="peril_structure:own@1")
    with pytest.raises(PlatformError) as caught:
        await _check(_gbm_row((band,)), step)
    assert caught.value.code == CODE


@pytest.mark.req("FR-222")
async def test_a_gbm_on_identity_factors_saves(monkeypatch: pytest.MonkeyPatch) -> None:
    """The control: the refusal is on the Factor's type."""
    plain = _factor("vehicle_age", "vehicle_age", FactorType.IDENTITY)
    _serve(monkeypatch, (plain,))
    await _check(_gbm_row((plain,)), _step({"vehicle_age": "vehicle_age"}))


@pytest.mark.req("FR-222")
async def test_a_glm_on_a_banded_factor_saves(monkeypatch: pytest.MonkeyPatch) -> None:
    """The control: a GLM carries its Bandings into the Bundle, so it is not refused."""
    band = _factor("driver_age_band", "driver_age", FactorType.BANDING)
    _serve(monkeypatch, (band,))
    await _check(_glm_row((band,)), _step({"driver_age": "driver_age_band"}))


@pytest.mark.req("FR-222")
async def test_a_model_that_does_not_exist_yet_saves(monkeypatch: pytest.MonkeyPatch) -> None:
    """R1: an algorithm saves before its models do; compile refuses a missing pin."""
    _serve(monkeypatch, ())
    await _check(None, _step({"driver_age": "driver_age_band"}))


@pytest.mark.req("FR-222")
async def test_a_banded_gbm_with_no_model_call_step_saves(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The refusal is keyed on a `model_call` step, never on a pin: an algorithm with no such
    step saves whatever the version pins (WF-699 pins the banded demo GBM at C1)."""
    band = _factor("driver_age_band", "driver_age", FactorType.BANDING)
    _serve(monkeypatch, (band,))
    other = SimpleNamespace(step_id="s_in", type="input")
    await algorithms_module.check_model_call_feature_maps(
        _Session(_gbm_row((band,))), uuid4(), [other]  # type: ignore[arg-type,list-item]
    )
