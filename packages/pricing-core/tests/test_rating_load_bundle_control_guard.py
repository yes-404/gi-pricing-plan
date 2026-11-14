"""WK-2113 S3, condition (1): `load_bundle` refuses a STORED bundle pricing on a `control` operand.

A bundle compiled before S1's compile guard keeps pricing after the fix, because nothing between
compile and price re-reads a Factor's intent (aud-intent2 cell B1). The bundle already carries a
GLM pin's Factors (`_carry_glm_inputs`), so `load_bundle` can run the same closure test
(`control_factor_in`) over them and refuse with `CONTROL_FACTOR_IN_RATEABLE_PATH` (FR-88, FR-240).

The pre-fix bundle is built by turning S1's compile guard OFF, for the construction only
(`_compile_without_the_control_guard`): the patch is loud, named, scoped to one `with`, and covers
no app caller (a test patch of a production function must be loud).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest
from test_rating_glm_model_call import MODEL_REF, GlmWorld, compiled_bundle

from model_schema import Factor, FactorIntent, FactorType, GlmSpec, OffsetSpec
from pricing_core.modelling import fit_glm
from pricing_core.rating import compile as compile_module
from pricing_core.rating.runtime import load_bundle

_DS = uuid4()


def _factor(slug: str, cols: tuple[str, ...], **kw: Any) -> Factor:
    return Factor(id=uuid4(), slug=slug, dataset_id=_DS, version=1, source_columns=cols, **kw)


def _world(
    *, carried_yoa_intent: FactorIntent, fitted_yoa_intent: FactorIntent = FactorIntent.CONTROL
) -> GlmWorld:
    """A GLM fitted on `region`, `yoa` and their cross; the bundle carries `yoa` as given."""
    region = _factor("region", ("region",), type=FactorType.IDENTITY)
    yoa = _factor("yoa", ("yoa",), type=FactorType.IDENTITY, intent=fitted_yoa_intent)
    cross = _factor(
        "region_x_yoa", (), type=FactorType.INTERACTION, operand_factor_ids=(region.id, yoa.id)
    )
    rng = np.random.default_rng(7)
    n = 4000
    reg = rng.choice(["A", "B"], n)
    yr = rng.choice(["2010", "2011"], n)
    lam = np.where(yr == "2010", 0.10, 0.25) * np.where(reg == "A", 1.0, 1.5)
    book = pl.DataFrame(
        {
            "region": reg,
            "yoa": yr,
            "exposure_years": np.ones(n),
            "claim_count": rng.poisson(lam).astype(float),
        }
    )
    spec = GlmSpec(
        model_family_slug="probe",
        dataset_version_id=_DS,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=(region.id, yoa.id, cross.id),
        family="poisson",
        link="log",
    )
    fit = fit_glm(book, spec, [region, yoa, cross]).result
    carried = yoa.model_copy(update={"intent": carried_yoa_intent})
    return GlmWorld(spec, fit, (region, carried, cross), (), ())


def _world_risk() -> GlmWorld:
    """The clean risk x risk case: every Factor is `risk`, so a normal compile accepts it."""
    return _world(carried_yoa_intent=FactorIntent.RISK, fitted_yoa_intent=FactorIntent.RISK)


def _algorithm() -> dict[str, Any]:
    contract = [
        {"name": "region", "type": "enum", "domain": ["A", "B"], "nullable": False},
        {"name": "yoa", "type": "enum", "domain": ["2010", "2011"], "nullable": False},
        {
            "name": "region_x_yoa",
            "type": "enum",
            "nullable": False,
            "domain": ["A:2010", "A:2011", "B:2010", "B:2011"],
        },
        {"name": "exposure_years", "type": "decimal", "nullable": False},
    ]
    names = [str(c["name"]) for c in contract]
    inputs = [
        {
            "step_id": f"s_{n}",
            "type": "input",
            "label": n,
            "input_name": n,
            "on_missing": "error",
            "produces": n,
        }
        for n in names
    ]
    call = {
        "step_id": "s_risk",
        "type": "model_call",
        "label": "Risk",
        "model_ref": MODEL_REF,
        "mode": "exact",
        "consumes": names,
        "produces": ["risk"],
        "result_type": "decimal",
        "feature_map": {
            "region": "region",
            "yoa": "yoa",
            "region_x_yoa": "region_x_yoa",
            "exposure_years": "exposure_years",
        },
    }
    return {
        "slug": "glm-golden",
        "version": 1,
        "input_contract": contract,
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            *inputs,
            call,
            {
                "step_id": "s_out",
                "type": "output",
                "label": "Risk",
                "output_name": "risk_out",
                "rounding": {"mode": "half_even", "dp": 6},
                "consumes": ["risk"],
            },
        ],
        "sub_graphs": [],
    }


@contextmanager
def _compile_without_the_control_guard() -> Iterator[None]:
    """LOUD TEST PATCH: S1's compile-time control guard is a no-op inside this `with` only.

    It builds the bundle a pre-S1 build would have stored. No app caller runs inside it, and
    `test_the_construction_patch_is_restored` proves the guard is back afterwards.
    """
    real = compile_module._refuse_control_factor_features
    compile_module._refuse_control_factor_features = lambda *_a, **_k: None  # type: ignore[assignment]
    try:
        yield
    finally:
        compile_module._refuse_control_factor_features = real  # type: ignore[assignment]


async def _stored_bundle(*, carried_yoa_intent: FactorIntent) -> Any:
    with _compile_without_the_control_guard():
        return await compiled_bundle(_world(carried_yoa_intent=carried_yoa_intent), _algorithm())


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_the_construction_patch_is_restored() -> None:
    before = compile_module._refuse_control_factor_features
    await _stored_bundle(carried_yoa_intent=FactorIntent.CONTROL)
    assert compile_module._refuse_control_factor_features is before


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_without_the_patch_the_same_construction_is_refused_at_compile() -> None:
    """The patch, not the fixture, is what lets the bundle through S1's compile guard."""
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        await compiled_bundle(_world(carried_yoa_intent=FactorIntent.CONTROL), _algorithm())


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_stored_bundle_pricing_on_a_control_operand_is_refused_at_load() -> None:
    """RED at S1's head: `load_bundle` has no intent test, so it returns a CompiledBundle."""
    bundle = await _stored_bundle(carried_yoa_intent=FactorIntent.CONTROL)
    carried = [p for ref, p in bundle.resolved_payloads.items() if ref.startswith("factor:yoa@")]
    assert [p["intent"] for p in carried] == ["control"]  # the bundle really carries the operand
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        load_bundle(bundle)
    message = str(refused.value)
    assert "yoa" in message  # names the operand
    assert "region_x_yoa" in message  # and the interaction it was reached through


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_the_same_bundle_with_a_risk_operand_loads() -> None:
    """Instrument-red cell: the guard must not fire on everything. rc 0 today and after the fix."""
    bundle = await _stored_bundle(carried_yoa_intent=FactorIntent.RISK)
    carried = [p for ref, p in bundle.resolved_payloads.items() if ref.startswith("factor:yoa@")]
    assert carried, "the bundle must carry the operand's payload"
    assert all(p["intent"] == "risk" for p in carried)
    assert load_bundle(bundle) is not None
