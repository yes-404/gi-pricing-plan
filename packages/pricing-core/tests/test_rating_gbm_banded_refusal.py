"""A `model_call` may not pin a GBM fitted on a banded or grouped Factor (SL 8071; FD 8073 (to be
filed after the probe run); FR-222 and FR-240 as amended 2026-10-16).

The defect, by reading at `a2f77b2d` (the maintainer's (by delegation) entry headed
"2026-10-16 10:59:28 BST"): `fit_gbm` bands the raw column and encodes the label ordinally into
`categorical_maps`, but a GBM pin carries no Bandings into the Bundle (`_carry_glm_inputs`) and
the runtime scores with `factors=()`. A raw value is therefore looked up as if it were the band
label. Case A: a raw `driver_age` is no label, so scoring raises `GbmFitError` (loud). Case C:
bands labelled "1", "2", "3" and a raw int 2 is another band's label, so it prices the wrong band
with no error (silent). The interim rule is to refuse the pin at compile with
`MODEL_CALL_GBM_TRANSFORMED_FACTOR`, and to turn a `GbmFitError` raised while scoring into the
named `MODEL_CALL_FAILED` failure rather than the engine's generic `NodeError`.

Fixtures: the fitted-GBM world and the `model_call` graph are the recipe of the probe's scratch
test, rebuilt here from the neighbouring modules' helpers; none is imported from the probe.
"""

from __future__ import annotations

from functools import cache
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest
from test_rating_glm_model_call import age_glm
from test_rating_runtime import _compiled as compiled_runtime_world

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    OffsetSpec,
    SplitRef,
)
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.modelling.gbm import GbmFitError, fit_gbm
from pricing_core.rating import runtime
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY

DATASET = uuid4()
MODEL_REF = "model:banded-gbm@1"
BACKENDS = ["xgboost", "lightgbm"]
CODE = r"^MODEL_CALL_GBM_TRANSFORMED_FACTOR: "


class GbmWorld:
    """A GBM really fitted on one banded Factor, as the worker persists it."""

    def __init__(self, backend: str, *, column: str, labels: tuple[str, ...],
                 boundaries: tuple[float, ...], lo: int, hi: int) -> None:
        self.column = column
        self.banding = Banding(
            id=uuid4(), slug=f"{column}-bands", dataset_id=DATASET, version=1, column=column,
            method=BandingMethod.MANUAL, boundaries=boundaries, labels=labels,
        )
        self.factor = Factor(
            id=uuid4(), slug=f"{column}_band", dataset_id=DATASET, version=1,
            type=FactorType.BANDING, source_columns=(column,), banding_id=self.banding.id,
        )
        spec = GbmSpec(
            model_type=backend, model_family_slug="banded-gbm", dataset_version_id=DATASET,
            split_ref=SplitRef(split_artifact_id=uuid4()), response_column="severity",
            offset=OffsetSpec(kind="none"),
            objective=GbmFunctionRef(kind="builtin", name="reg:gamma"),
            categorical_handling="native",
            hyperparameters={"max_depth": 3, "eta": 0.3, "num_boost_round": 20},
            early_stopping=None, factors=(self.factor.id,),
        )
        rng = np.random.default_rng(20261016)
        raw = rng.integers(lo, hi, 2_000)
        step = np.searchsorted(np.array(boundaries[1:-1]), raw, side="right")
        book = pl.DataFrame({
            column: raw.astype(float),
            "severity": 100.0 * (1.0 + 2.0 * step) * rng.uniform(0.95, 1.05, 2_000),
            "claim_count": np.ones(2_000),
        })
        fit = fit_gbm(book, spec, [self.factor], bandings={self.banding.id: self.banding})
        self.payload: dict[str, Any] = {
            "model_family_slug": "banded-gbm", "version": 1, "status": "approved",
            "spec": spec.model_dump(mode="json"),
            "fit_result": {
                **fit.result.model_dump(mode="json"),
                "booster_content": fit.booster_bytes.decode("utf-8"),
            },
        }


@cache
def _age_world(backend: str) -> GbmWorld:
    """Case A's model: bands over `driver_age`, labelled as ranges."""
    return GbmWorld(
        backend, column="driver_age", labels=("17-37", "38-57", "58+"),
        boundaries=(17.0, 38.0, 58.0, 100.0), lo=17, hi=99,
    )


@cache
def _numeric_label_world(backend: str) -> GbmWorld:
    """Case C's model: bands over `veh_power` labelled "1", "2", "3" (the band index)."""
    return GbmWorld(
        backend, column="veh_power", labels=("1", "2", "3"),
        boundaries=(0.0, 5.0, 10.0, 20.0), lo=1, hi=19,
    )


def _algorithm(world: GbmWorld) -> dict[str, Any]:
    """One RAW input (`world.column`) -> a `model_call` mapping it onto the Factor slug."""
    column, slug = world.column, world.factor.slug
    return {
        "slug": "banded-gbm-probe", "version": 1,
        "input_contract": [
            {"name": column, "type": "int", "nullable": False, "min": 0, "max": 999}
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": column,
             "on_missing": "error", "produces": column},
            {"step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": MODEL_REF,
             "mode": "exact", "feature_map": {column: slug}, "consumes": [column],
             "produces": ["risk"], "result_type": "decimal"},
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


def _algorithm_without_a_call(world: GbmWorld) -> dict[str, Any]:
    """The same pinned graph with NO `model_call`: the banded GBM is pinned and never scored."""
    column = world.column
    return {
        "slug": "banded-gbm-probe", "version": 1,
        "input_contract": [
            {"name": column, "type": "int", "nullable": False, "min": 0, "max": 999}
        ],
        "outputs": [{"name": "premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": column,
             "on_missing": "error", "produces": column},
            {"step_id": "s_x", "type": "expression", "label": "X", "expr": f"{column} * 100",
             "result_type": "money_minor", "consumes": [column], "produces": "x_minor"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["x_minor"]},
        ],
        "sub_graphs": [],
    }


def _version() -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "banded-gbm-probe",
        "version": 1, "status": "draft", "dataset_version_id": str(uuid4()),
        "model_ref": MODEL_REF, "created_at": "2026-10-16T12:00:00Z",
        "created_by": str(uuid4()), "updated_at": "2026-10-16T12:00:00Z",
        "algorithm_ref": "rating_algorithm:banded-gbm-probe@1",
        "pins": {"rate_tables": [], "models": [MODEL_REF], "reference_tables": [],
                 "custom_objectives": []},
        "model_reference_mode": "exact",
    })


class _Resolver:
    """As the backend resolver does for a GBM pin: Factors loaded, nothing else carried."""

    def __init__(
        self, world: GbmWorld, *, factor: Factor | None = None, call: bool = True
    ) -> None:
        self._call = call
        self._world = world
        self._factor = factor or world.factor

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if ref.type == "rating_algorithm":
            payload = (
                _algorithm(self._world) if self._call
                else _algorithm_without_a_call(self._world)
            )
            return ResolvedArtifact(status="no_maturity_concept", payload=payload)
        assert str(ref) == MODEL_REF, ref
        return ResolvedArtifact(
            status="approved", payload=self._world.payload, factors=(self._factor,),
            bandings=(self._world.banding,),
        )


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
async def test_case_c_numeric_looking_band_labels_are_refused_at_compile(backend: str) -> None:
    """Case C, the SILENT one: bands labelled "1", "2", "3" and a raw int 2 (which belongs to
    band "1") used to price band "2"'s code with no error. It is now refused before it can be
    pinned into a rating, naming the step, the model and the Factor."""
    world = _numeric_label_world(backend)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _Resolver(world))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert MODEL_REF in message
    assert world.factor.slug in message


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
async def test_case_a_a_raw_value_into_a_banded_gbm_is_refused_at_compile(backend: str) -> None:
    """Case A, the LOUD one: a raw `driver_age` into a GBM fitted on its band raised
    `GbmFitError` on every quote. It is now refused at compile, not discovered per quote."""
    world = _age_world(backend)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _Resolver(world))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert world.factor.slug in message
    assert "banding" in message


@pytest.mark.req("FR-222", "FR-240", "NFR-499")
async def test_the_gbm_factor_refusal_message_is_exactly_its_structural_fields() -> None:
    """The raise site is `_INPUT_FREE` in test_quote_input_raise_sites.py: the text is the step id,
    the pinned model ref and the Factor slug and kind, so no quote-row value can appear in it."""
    world = _age_world("xgboost")
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _Resolver(world))
    assert str(caught.value) == (
        f"MODEL_CALL_GBM_TRANSFORMED_FACTOR: step 's_risk': {MODEL_REF} is a GBM fitted on banded "
        f"or grouped Factors [{world.factor.slug} (banding)], which a model_call cannot score: "
        "the Bundle carries no Bandings or Groupings for a GBM (FR-222, FR-240)"
    )


@pytest.mark.req("FR-222", "FR-240")
async def test_a_grouped_factor_is_refused_too() -> None:
    """The same defect for a grouped Factor (a raw level equal to a group name)."""
    world = _age_world("xgboost")
    grouped = world.factor.model_copy(
        update={"type": FactorType.GROUPING, "banding_id": None, "grouping_id": uuid4()}
    )
    resolver = _Resolver(world, factor=grouped)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), resolver)
    assert "grouping" in str(caught.value)


@pytest.mark.req("FR-222", "FR-240")
async def test_a_banded_gbm_pinned_but_never_called_still_compiles() -> None:
    """The refusal is keyed on a `model_call` STEP, never on a pin: WF-699 pins the banded demo
    GBM (C1) and recompiles it (C5) with no `model_call` reaching it (journey.py skips B4/C1')."""
    bundle = await compile_bundle(_version(), _Resolver(_age_world("xgboost"), call=False))
    assert bundle.content_hash


@pytest.mark.req("FR-222", "FR-240")
async def test_a_gbm_on_plain_factors_still_compiles() -> None:
    """The control: the refusal is on the Factor's type. A GBM whose Factors are `identity`
    pins as before (the runtime fixture's GBM has none, and `compiled_runtime_world` builds it
    through the real `compile_bundle`)."""
    compiled = await compiled_runtime_world()
    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    assert MODEL_CALL_ERROR_KEY not in out["result"]


@pytest.mark.req("FR-222", "FR-240")
async def test_a_glm_on_a_banded_factor_still_compiles() -> None:
    """The control: a GLM carries its Bandings into the Bundle, so a banded GLM is not
    refused (`age_glm`'s one Factor is a banding)."""
    glm = age_glm()
    assert any(factor.type is FactorType.BANDING for factor in glm.factors)
    compiled = await compiled_runtime_world(glm=True)
    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    assert MODEL_CALL_ERROR_KEY not in out["result"]


@pytest.mark.req("FR-222", "FR-255", "NFR-499")
async def test_a_gbm_fit_error_while_scoring_is_the_named_model_call_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`GbmFitError` is neither a `ModellingError` nor a `PredictionError`, so it escaped the
    `model_call` handler and surfaced as the zen binding's generic `NodeError`, with no code.
    It is now the `MODEL_CALL_FAILED` failure naming the error's own code, and the error's text
    (which can carry a quote's value) is never passed on."""

    def _failing(*args: Any, **kwargs: Any) -> Any:
        raise GbmFitError("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED", "level 'SENTINEL-3c9d' unseen")

    monkeypatch.setattr(runtime, "predict_gbm", _failing)
    compiled = await compiled_runtime_world()

    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    message = out["result"][MODEL_CALL_ERROR_KEY]
    assert message.startswith("MODEL_CALL_FAILED: UNSEEN_LEVEL_BEHAVIOUR_REQUIRED")
    assert "SENTINEL" not in message
