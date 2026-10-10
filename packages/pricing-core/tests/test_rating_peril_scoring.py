"""A-3 (PL-1465, SL-1466) — a Peril Structure `model_call` compiles and scores.

Compile resolves each component model of the pinned structure, refuses one below
`approved` and embeds its payload, so the Bundle stays self-contained; the runtime then
assembles the risk premium. Covers FR-188, FR-189, FR-20, FR-237, FR-239, FR-240, NFR-491.

Every refusal test is red first by cause (PL-1465 §"Acceptance Standard"): see LG-9455.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from test_rating_compile_bundle import FakeResolver, _version, valid_algorithm_payload
from test_rating_runtime import _gbm_model_payload, _train_tiny_booster

from model_schema import PerilStructure
from model_schema.perils import LargeLossKind, LargeLossTreatment, PerilComponent, PerilMethod
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import compile_bundle

STRUCTURE = "peril_structure:motor-perils@1"
AD_FREQ = "model:ad-freq@1"
AD_SEV = "model:ad-sev@1"
WS_BC = "model:ws-bc@1"
COMPONENTS = (AD_FREQ, AD_SEV, WS_BC)


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
    booster = _train_tiny_booster()
    payloads: dict[str, Any] = {
        "rating_algorithm:motor-gb@14": algorithm or _peril_algorithm(),
        "rate_table:motor-expense@3": {"rateable": True, "rows": []},
        "reference_table:ons-postcode-directory@7": {"rows": []},
        STRUCTURE: structure or _structure_payload(),
    }
    for ref in COMPONENTS:
        payloads[ref] = _gbm_model_payload(booster)
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
