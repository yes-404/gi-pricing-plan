"""A-3 (PL-1465, SL-1466) — a Peril Structure `model_call` compiles and scores.

Compile resolves each component model of the pinned structure, refuses one below
`approved` and embeds its payload, so the Bundle stays self-contained; the runtime then
assembles the risk premium. Covers FR-188, FR-189, FR-20, FR-237, FR-239, FR-240, NFR-491.

Every refusal test is red first by cause (PL-1465 §"Acceptance Standard"): see LG-9455.
"""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
import pytest
import xgboost as xgb
from test_rate_table_operations import _factor
from test_rating_compile_bundle import FakeResolver, _version, valid_algorithm_payload
from test_rating_compile_fr240 import _FactorsResolver
from test_rating_glm_model_call import GlmWorld, age_glm
from test_rating_runtime import _gbm_model_payload

from model_schema import PerilStructure
from model_schema.modelling import FactorIntent
from model_schema.perils import (
    TOLERANCE_QUANTUM,
    LargeLossKind,
    LargeLossTreatment,
    PerilComponent,
    PerilMethod,
)
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.modelling import perils as modelling_perils
from pricing_core.modelling.perils import PerilPrediction, assemble_risk_premium
from pricing_core.rating.compile import Bundle, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, load_bundle

STRUCTURE = "peril_structure:motor-perils@1"
AD_FREQ = "model:ad-freq@1"
AD_SEV = "model:ad-sev@1"
WS_BC = "model:ws-bc@1"
COMPONENTS = (AD_FREQ, AD_SEV, WS_BC)


def _booster(scale: float) -> bytes:
    """`test_rating_runtime._train_tiny_booster`'s data with the label scaled, so each
    component predicts a different, known amount (age 34 -> 1304.8 * scale for `scale` 1)."""
    x = [[20.0], [30.0], [40.0], [50.0], [60.0]]
    y = [v * scale for v in (1000.0, 1200.0, 1500.0, 1800.0, 2000.0)]
    dtrain = xgb.DMatrix(x, label=y, feature_names=["age_years"])
    booster = xgb.train({"objective": "reg:squarederror", "max_depth": 2}, dtrain, 3)
    return bytes(booster.save_raw(raw_format="json"))


#: Frequency about 0.1 to 0.2 (a count), severity and burning cost in minor units (DP-A3-5 (a)).
BOOSTERS = {AD_FREQ: _booster(0.0001), AD_SEV: _booster(1.0), WS_BC: _booster(0.05)}


def _gbm_predict(ref: str, age: float) -> float:
    """A component's prediction straight from xgboost, independent of the runtime."""
    booster = xgb.Booster()
    booster.load_model(bytearray(BOOSTERS[ref]))
    frame = xgb.DMatrix(np.array([[age]]), feature_names=["age_years"])
    return float(booster.predict(frame)[0])


def _structure_payload(
    *,
    ad_large_loss: LargeLossTreatment | None = None,
    ws_large_loss: LargeLossTreatment | None = None,
) -> dict[str, Any]:
    """An AD `frequency_severity` peril and a WS `burning_cost` peril (PL-1465 Task 1 Step 1)."""
    none = LargeLossTreatment(kind=LargeLossKind.NONE)
    structure = PerilStructure(
        id=uuid4(),
        slug="motor-perils",
        version=1,
        perils=(
            PerilComponent(
                peril="AD",
                method=PerilMethod.FREQUENCY_SEVERITY,
                frequency_model=ArtifactRef.model_validate(AD_FREQ),
                severity_model=ArtifactRef.model_validate(AD_SEV),
                large_loss=ad_large_loss or none,
            ),
            PerilComponent(
                peril="WS",
                method=PerilMethod.BURNING_COST,
                burning_cost_model=ArtifactRef.model_validate(WS_BC),
                large_loss=ws_large_loss or none,
            ),
        ),
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
    )
    return structure.model_dump(mode="json")


def _peril_algorithm(produces: list[str] | None = None) -> dict[str, Any]:
    """`valid_algorithm_payload` with its `s_rp` step naming the structure."""
    algorithm = valid_algorithm_payload()
    step = next(s for s in algorithm["steps"] if s["step_id"] == "s_rp")
    del step["model_ref"]
    step["peril_structure_ref"] = STRUCTURE
    step["feature_map"] = {"driver_age": "age_years"}
    step["consumes"] = ["driver_age"]
    step["produces"] = produces or ["risk_premium_minor"]
    return algorithm


def _peril_version() -> RatingVersion:
    version = _version()
    pins = version.pins
    assert pins is not None
    return version.model_copy(
        update={
            "pins": pins.model_copy(update={"models": [ArtifactRef.model_validate(STRUCTURE)]})
        }
    )


def _resolver(
    *,
    statuses: dict[str, str] | None = None,
    structure: dict[str, Any] | None = None,
    algorithm: dict[str, Any] | None = None,
) -> FakeResolver:
    payloads: dict[str, Any] = {
        "rating_algorithm:motor-gb@14": algorithm or _peril_algorithm(),
        "rate_table:motor-expense@3": {"rateable": True, "rows": []},
        "reference_table:ons-postcode-directory@7": {"rows": []},
        STRUCTURE: structure or _structure_payload(),
    }
    for ref in COMPONENTS:
        payloads[ref] = _gbm_model_payload(BOOSTERS[ref])
    return FakeResolver(payloads, {STRUCTURE: "approved", **(statuses or {})})


@pytest.mark.req("FR-237", "FR-240")
async def test_a_peril_structure_pin_compiles_with_its_component_models_embedded() -> None:
    """Items 1 and 7: the three component refs are embedded under `str(ref)`."""
    bundle = await compile_bundle(_peril_version(), _resolver())
    for ref in COMPONENTS:
        assert ref in bundle.resolved_payloads, f"{ref} is not embedded in the Bundle"


@pytest.mark.req("FR-240", "FR-20")
@pytest.mark.parametrize("status", ["draft", "fitted", "review", "superseded", "archived"])
async def test_a_peril_component_below_approved_is_refused_at_compile(status: str) -> None:
    """Item 2: the message names the component, the structure and the peril."""
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED") as caught:
        await compile_bundle(_peril_version(), _resolver(statuses={WS_BC: status}))
    message = str(caught.value)
    assert WS_BC in message
    assert STRUCTURE in message
    assert "WS" in message


@pytest.mark.req("FR-240", "FR-20")
async def test_an_approved_component_compiles() -> None:
    """Item 2's control: passes on both trees."""
    bundle = await compile_bundle(_peril_version(), _resolver(statuses={WS_BC: "approved"}))
    assert bundle.content_hash.startswith("sha256:")


@pytest.mark.req("FR-239")
async def test_the_peril_bundle_hash_is_reproducible_from_the_pins() -> None:
    """Item 7: embedding components leaves the hash a function of the pins."""
    from pricing_core.rating.compile import bundle_hash

    first = await compile_bundle(_peril_version(), _resolver())
    second = await compile_bundle(_peril_version(), _resolver())
    assert first.content_hash == second.content_hash
    assert first.content_hash == bundle_hash(first.graph, first.pins)


@pytest.mark.req("FR-222")
async def test_a_peril_model_call_with_two_produced_names_is_refused_at_compile() -> None:
    """Item 8 (DP-A3-1 (c)): the §4 example's two names, `BUNDLE_COMPILE_FAILED`."""
    algorithm = _peril_algorithm(["risk_premium_minor", "peril_risk_premium"])
    with pytest.raises(ValueError, match="BUNDLE_COMPILE_FAILED") as caught:
        await compile_bundle(_peril_version(), _resolver(algorithm=algorithm))
    message = str(caught.value)
    assert "s_rp" in message
    assert "peril_risk_premium" in message


FRAGMENT = "sub_graph:peril-premium@1"


def _mounted_peril(produces: list[str]) -> tuple[RatingVersion, FakeResolver]:
    """OP-A3-M1: `_peril_algorithm()` with its peril `model_call` moved into a mounted sub-graph.

    The parent keeps the input step for `driver_age` and every consumer of `risk_premium_minor`;
    the fragment holds the `peril_structure_ref` step, so only the INLINED algorithm shows it.
    """
    algorithm = _peril_algorithm()
    step = next(s for s in algorithm["steps"] if s["step_id"] == "s_rp")
    algorithm["steps"].remove(step)
    algorithm["sub_graphs"] = [{
        "ref": FRAGMENT, "mount_point": "m_peril",
        "inputs": {"driver_age": "driver_age"},
        "outputs": {"risk_premium_minor": "risk_premium_minor"},
    }]
    fragment_step = {**step, "produces": produces}
    resolver = _resolver(algorithm=algorithm)
    resolver._payloads[FRAGMENT] = {
        "slug": "peril-premium", "version": 1,
        "inputs": [{"name": "driver_age", "type": "int"}],
        "outputs": [{"name": "risk_premium_minor", "type": "decimal", "required": True}],
        "steps": [fragment_step],
        "change_note": "first cut",
    }
    version = _peril_version()
    pins = version.pins
    assert pins is not None
    version = version.model_copy(update={
        "pins": pins.model_copy(update={"sub_graphs": [ArtifactRef.parse(FRAGMENT)]})
    })
    return version, resolver


@pytest.mark.req("FR-222", "FR-217")
async def test_a_peril_model_call_inside_a_mounted_sub_graph_is_checked_at_compile() -> None:
    """OP-A3-M1 (a): the peril checks run over the inlined algorithm, so a step inside a pinned
    sub-graph does not escape them. Invalid: refused naming the namespaced step; valid: the
    component models are embedded."""
    version, resolver = _mounted_peril(["risk_premium_minor", "peril_risk_premium"])
    with pytest.raises(ValueError, match="BUNDLE_COMPILE_FAILED") as caught:
        await compile_bundle(version, resolver)
    assert "m_peril__s_rp" in str(caught.value)
    version, resolver = _mounted_peril(["risk_premium_minor"])
    bundle = await compile_bundle(version, resolver)
    for ref in COMPONENTS:
        assert ref in bundle.resolved_payloads


@pytest.mark.req("FR-188", "NFR-499")
async def test_an_invalid_structure_payload_is_refused_at_compile_coded_and_input_free(
) -> None:
    """Row 3 (b'): `PerilStructure.model_validate` at compile is wrapped, so a structure whose
    payload does not validate raises the existing `BUNDLE_COMPILE_FAILED` naming only the
    structure ref and the fields at fault, never a payload value (a raw pydantic error would
    carry the input). Replaces A-1's stub-refusal test in `test_rating_runtime.py`."""
    sentinel = "SENTINEL-7c1e"
    payload = {"slug": sentinel, "version": 1, "perils": [], "excluded_perils": []}
    with pytest.raises(ValueError, match="BUNDLE_COMPILE_FAILED") as caught:
        await compile_bundle(_peril_version(), _resolver(structure=payload))
    message = str(caught.value)
    assert STRUCTURE in message
    assert sentinel not in message


@pytest.mark.req("FR-189")
async def test_a_separate_model_large_loss_is_refused_at_compile() -> None:
    """Item 9 (DP-A3-2 (a)): `LOSS_TREATMENT_UNIMPLEMENTED` naming structure and peril."""
    structure = _structure_payload()
    ad = structure["perils"][0]
    ad["large_loss"] = {
        "kind": "separate_model",
        "excess_model": "model:ad-excess@1",
        "attachment_minor": 100000,
        "evidence_blob": {"sha256": "b" * 64, "bytes": 10, "media_type": "application/json"},
    }
    resolver = _resolver(structure=structure)
    with pytest.raises(ValueError, match="LOSS_TREATMENT_UNIMPLEMENTED") as caught:
        await compile_bundle(_peril_version(), resolver)
    message = str(caught.value)
    assert STRUCTURE in message
    assert "AD" in message


OBJECTIVE = "custom_objective:asym-loss@1"


@pytest.mark.req("FR-88", "FR-240")
async def test_a_control_factor_in_a_peril_component_is_refused() -> None:
    """Item 10 (DP-A3-3 (a)): PL-1471's control-factor clause reaches a component."""
    resolver = _resolver()
    controlled = _factor("age_years").model_copy(update={"intent": FactorIntent.CONTROL})
    reaching = _FactorsResolver(resolver, {AD_SEV: (controlled,)})
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as caught:
        await compile_bundle(_peril_version(), reaching)
    message = str(caught.value)
    assert AD_SEV in message
    assert "age_years" in message
    assert "age_years@1" in message


@pytest.mark.req("FR-88", "FR-240")
async def test_a_peril_component_over_a_risk_factor_compiles() -> None:
    """Item 10's control: the same component with a `risk` Factor compiles."""
    resolver = _resolver()
    risk = _factor("age_years").model_copy(update={"intent": FactorIntent.RISK})
    await compile_bundle(_peril_version(), _FactorsResolver(resolver, {AD_SEV: (risk,)}))


@pytest.mark.req("FR-240", "FR-20")
async def test_an_unapproved_custom_objective_under_a_peril_component_is_refused() -> None:
    """Item 10 (DP-A3-3 (a)): PL-1471's objective clause reaches a component."""
    resolver = _resolver(statuses={OBJECTIVE: "review"})
    resolver._payloads[AD_FREQ]["spec"] = {
        "model_type": "gbm",
        "objective": {"kind": "custom", "ref": OBJECTIVE},
    }
    resolver._payloads[OBJECTIVE] = {"slug": "asym-loss", "version": 1}
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED") as caught:
        await compile_bundle(_peril_version(), resolver)
    message = str(caught.value)
    assert AD_FREQ in message
    assert OBJECTIVE in message


# -- Scoring: the runtime composes the structure's risk premium (FR-188, FR-189) -----------

AGES = (25.0, 34.0, 61.0)  # N = 3 quotes in the cross-check
_EVIDENCE = {"sha256": "b" * 64, "bytes": 10, "media_type": "application/json"}
CAPPED_AD = LargeLossTreatment.model_validate(
    {"kind": "capped", "cap_minor": 500000, "restoration_loading": "1.10",
     "evidence_blob": _EVIDENCE}
)
FLAT_WS = LargeLossTreatment.model_validate(
    {"kind": "flat_loading", "loading_factor": "1.25", "evidence_blob": _EVIDENCE}
)


def _scoring_algorithm(result_type: str | None = "decimal") -> dict[str, Any]:
    call: dict[str, Any] = {
        "step_id": "s_rp", "type": "model_call", "label": "Risk premium", "mode": "exact",
        "peril_structure_ref": STRUCTURE, "feature_map": {"driver_age": "age_years"},
        "consumes": ["driver_age"], "produces": ["risk"],
    }
    if result_type is not None:
        call["result_type"] = result_type
    return {
        "slug": "motor-gb", "version": 14,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_age", "type": "input", "label": "Age", "input_name": "driver_age",
             "on_missing": "error", "produces": "driver_age"},
            call,
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


class _ScoringResolver:
    """Serves the algorithm, the structure and its components; a GLM component with its Factors."""

    def __init__(
        self,
        *,
        structure: dict[str, Any] | None = None,
        algorithm: dict[str, Any] | None = None,
        glm: GlmWorld | None = None,
    ) -> None:
        self._glm = glm
        self._payloads: dict[str, Any] = {
            "rating_algorithm:motor-gb@14": algorithm or _scoring_algorithm(),
            STRUCTURE: structure or _structure_payload(),
            **{ref: _gbm_model_payload(BOOSTERS[ref]) for ref in COMPONENTS},
        }
        if glm is not None:
            self._payloads[AD_SEV] = glm.model_payload()

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        payload = self._payloads[str(ref)]
        if ref.type == "rating_algorithm":
            return ResolvedArtifact(status="no_maturity_concept", payload=payload)
        if self._glm is not None and str(ref) == AD_SEV:
            return ResolvedArtifact(
                status="approved", payload=payload, factors=self._glm.factors,
                bandings=self._glm.bandings, groupings=self._glm.groupings,
            )
        return ResolvedArtifact(status="approved", payload=payload)


def _scoring_version() -> RatingVersion:
    version = _peril_version()
    pins = version.pins
    assert pins is not None
    return version.model_copy(update={"pins": pins.model_copy(update={"rate_tables": [],
                                                                      "reference_tables": []})})


async def _bundle(resolver: _ScoringResolver) -> Bundle:
    return await compile_bundle(_scoring_version(), resolver)  # type: ignore[arg-type]


async def _risk(bundle: Bundle, age: float) -> Any:
    out = await load_bundle(bundle).decision.async_evaluate({"driver_age": int(age)})
    result = out["result"]
    assert MODEL_CALL_ERROR_KEY not in result, result
    return result["risk"]


def _expected(age: float, *, severity: float | None = None) -> Decimal:
    """The structure's risk premium, composed on `Decimal` by hand from independent
    predictions: `AD` capped (x1.10) frequency * severity, plus `WS` flat-loaded (x1.25)."""
    freq = Decimal(repr(_gbm_predict(AD_FREQ, age)))
    sev = Decimal(repr(_gbm_predict(AD_SEV, age) if severity is None else severity))
    ws = Decimal(repr(_gbm_predict(WS_BC, age)))
    return freq * sev * Decimal("1.10") + ws * Decimal("1.25")


def _treated() -> dict[str, Any]:
    return _structure_payload(ad_large_loss=CAPPED_AD, ws_large_loss=FLAT_WS)


@pytest.mark.req("FR-188", "FR-191")
async def test_a_peril_structure_model_call_scores_its_assembled_risk_premium() -> None:
    """Item 3: red today by cause, the `$model_call_error` sentence A-1 left ("scoring a Peril
    Structure is slice A-3 ... not yet built"); green: the Decimal composition, carried at the
    engine's 15 significant digits."""
    bundle = await _bundle(_ScoringResolver(structure=_structure_payload()))
    for age in AGES:
        expected = (
            Decimal(repr(_gbm_predict(AD_FREQ, age))) * Decimal(repr(_gbm_predict(AD_SEV, age)))
            + Decimal(repr(_gbm_predict(WS_BC, age)))
        )
        assert await _risk(bundle, age) == pytest.approx(float(expected), rel=1e-14)


@pytest.mark.req("FR-188", "FR-193")
async def test_a_peril_structure_with_a_glm_component_scores() -> None:
    """Item 4 (after A-2): the AD severity component is a real GLM; its Factors, Bandings and
    Groupings travel in the Bundle beside it, and the value equals `predict_glm` composed."""
    glm = age_glm()
    bundle = await _bundle(_ScoringResolver(structure=_treated(), glm=glm))
    assert AD_SEV in bundle.resolved_payloads
    for age in AGES:
        severity = glm.predict(driver_age=age)
        assert await _risk(bundle, age) == pytest.approx(
            float(_expected(age, severity=severity)), rel=1e-14
        )


@pytest.mark.req("FR-189")
async def test_peril_scoring_restores_each_peril_before_the_sum() -> None:
    """Item 5: AD `capped` x1.10 and WS `flat_loading` x1.25 are applied per peril; the value
    differs from either loading applied to the total."""
    bundle = await _bundle(_ScoringResolver(structure=_treated()))
    age = 34.0
    value = await _risk(bundle, age)
    assert value == pytest.approx(float(_expected(age)), rel=1e-14)
    ad = Decimal(repr(_gbm_predict(AD_FREQ, age))) * Decimal(repr(_gbm_predict(AD_SEV, age)))
    ws = Decimal(repr(_gbm_predict(WS_BC, age)))
    for wrong_loading in (Decimal("1.10"), Decimal("1.25")):
        assert value != pytest.approx(float((ad + ws) * wrong_loading), rel=1e-9)


@pytest.mark.req("FR-193", "NFR-491")
async def test_a_peril_bundle_scores_after_a_json_round_trip_with_no_resolver() -> None:
    """Item 6: the Bundle carries the structure and its components, so it scores with no
    resolver and no database after a JSON round trip."""
    resolver = _ScoringResolver(structure=_treated())
    bundle = await _bundle(resolver)
    del resolver
    revived = Bundle.model_validate_json(bundle.model_dump_json())
    assert revived.content_hash == bundle.content_hash
    assert await _risk(revived, 34.0) == pytest.approx(float(_expected(34.0)), rel=1e-14)


@pytest.mark.req("FR-226")
async def test_a_peril_model_call_without_a_result_type_rounds_the_total_once() -> None:
    """OP-2 (a): one rule for every `model_call` (00:44:31). No `result_type` is the legacy
    `round()`; the explicit `decimal` of the tests above carries the value unrounded."""
    algorithm = _scoring_algorithm(result_type=None)
    bundle = await _bundle(_ScoringResolver(structure=_treated(), algorithm=algorithm))
    expected = _expected(34.0)
    assert await _risk(bundle, 34.0) == round(expected)
    assert expected != round(expected)  # the assertion cannot pass by an exact fixture


@pytest.mark.req("FR-188")
async def test_the_decimal_composition_matches_assemble_risk_premium_within_the_tolerance() -> None:
    """OP-1 (a), cross-check: on the golden of N = 3 quotes (ages 25, 34, 61) the rating
    path's Decimal composition and the float64 `assemble_risk_premium` agree to within
    `TOLERANCE_QUANTUM` (0.000001 minor units) absolute."""
    bundle = await _bundle(_ScoringResolver(structure=_treated()))
    for age in AGES:
        frame = assemble_risk_premium([
            PerilPrediction(
                peril="AD", method=PerilMethod.FREQUENCY_SEVERITY,
                frequency=np.array([_gbm_predict(AD_FREQ, age)]),
                severity=np.array([_gbm_predict(AD_SEV, age)]), large_loss=CAPPED_AD,
            ),
            PerilPrediction(
                peril="WS", method=PerilMethod.BURNING_COST,
                burning_cost=np.array([_gbm_predict(WS_BC, age)]), large_loss=FLAT_WS,
            ),
        ])
        modelling = Decimal(repr(float(frame["risk_premium"][0])))
        scored = Decimal(repr(await _risk(bundle, age)))
        assert abs(scored - modelling) <= TOLERANCE_QUANTUM


_RATING_SRC = Path(__file__).resolve().parents[1] / "src" / "pricing_core" / "rating"


def _float_assembly_uses(source: str) -> list[int]:
    """Line numbers where `source` imports or names `assemble_risk_premium` (or its module)."""
    lines = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom | ast.Import):
            module = getattr(node, "module", "") or ""
            names = [alias.name for alias in node.names]
            # `import a.b.c` has no `.module`; the dotted name is in the alias.
            if (
                "assemble_risk_premium" in names
                or module.endswith("modelling.perils")
                or any(name.endswith("modelling.perils") for name in names)
            ):
                lines.append(node.lineno)
        elif isinstance(node, ast.Name | ast.Attribute) and "assemble_risk_premium" in (
            ast.unparse(node)
        ):
            lines.append(node.lineno)
    return lines


@pytest.mark.req("FR-188")
def test_the_float_assembly_detector_fires_on_a_deliberately_broken_module() -> None:
    """The guard's positive control: the detector reports each way a module can reach it."""
    for broken in (
        "from pricing_core.modelling.perils import assemble_risk_premium\n",
        "from pricing_core.modelling import perils\nperils.assemble_risk_premium([])\n",
        "import pricing_core.modelling.perils as p\n",
    ):
        assert _float_assembly_uses(broken), broken
    assert not _float_assembly_uses("from decimal import Decimal\n")


@pytest.mark.req("FR-188")
def test_no_rating_module_imports_the_float_assembly() -> None:
    """OP-1 (a), guard 1: `assemble_risk_premium` is float64 and stays outside the rating path
    (CLAUDE.md §7: Decimal, never float), checked by AST over every `pricing_core/rating`
    module."""
    offenders = {
        path.name: lines
        for path in sorted(_RATING_SRC.rglob("*.py"))
        if (lines := _float_assembly_uses(path.read_text(encoding="utf-8")))
    }
    assert not offenders, f"the rating path reaches the float assembly: {offenders}"


@pytest.mark.req("FR-188")
async def test_scoring_a_peril_structure_never_calls_assemble_risk_premium(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OP-1 (a), guard 2: a monkeypatched `assemble_risk_premium` that raises is not called
    while a peril quote scores. Red today by cause: the step never reaches a value."""

    def _forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("the rating path called assemble_risk_premium (float64)")

    monkeypatch.setattr(modelling_perils, "assemble_risk_premium", _forbidden)
    bundle = await _bundle(_ScoringResolver(structure=_treated()))
    assert await _risk(bundle, 34.0) == pytest.approx(float(_expected(34.0)), rel=1e-14)


@pytest.mark.req("FR-255", "NFR-499")
async def test_a_component_failure_reports_its_code_and_never_the_models_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `PredictionError`'s text can carry a quote value (an unseen factor level, `predict.py`);
    the handler passes on the code and a static sentence only. Red today: the text is passed on."""
    from pricing_core.modelling.predict import PredictionError
    from pricing_core.rating import runtime

    def _failing(*args: Any, **kwargs: Any) -> float:
        raise PredictionError("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED", "level 'SENTINEL-3c9d' unseen")

    monkeypatch.setattr(runtime, "_predict_model", _failing)
    bundle = await _bundle(_ScoringResolver(structure=_treated()))
    out = await load_bundle(bundle).decision.async_evaluate({"driver_age": 34})
    message = out["result"][MODEL_CALL_ERROR_KEY]
    assert "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED" in message
    assert "SENTINEL" not in message
