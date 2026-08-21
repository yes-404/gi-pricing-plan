"""The EBM arm of `ModelSpec` (`02` §4.4, §3.5).

Every test here is a **prohibition**, for the reason `test_gbm_spec.py` gives: a shape
that can represent a nonsense model eventually holds one, and a Model is what a Rating
Version references.

The refusals are the spec's own, by name (FR-MODEL-87's staging rule, dated note in
`02` §4.4): `interpret`'s objectives are `rmse` and `mae`, so §7's families and binomial
`log_loss` are refused rather than translated; `interactions=2` (triples) is
declared-and-unbuilt, so it is refused rather than stored; and offsets stay GLM-only, so
an EBM that declares one is refused rather than silently fitted without it.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    MODEL_SPEC_ADAPTER,
    GlmFitResult,
    Model,
    ModelStatus,
    OffsetSpec,
    SplitRef,
    WeightSpec,
    new_uuid7,
)
from model_schema.modelling import EbmSpec


def _spec(**over: object) -> EbmSpec:
    base: dict[str, object] = {
        "model_type": "ebm",
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": new_uuid7(),
        "response_column": "ad_claim_count",
        "offset": OffsetSpec(kind="none"),
    }
    base.update(over)
    return EbmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-37")
def test_the_objective_vocabulary_is_rmse_and_mae() -> None:
    with pytest.raises(pydantic.ValidationError, match="poisson"):
        _spec(objective="poisson")


@pytest.mark.req("FR-MODEL-87")
@pytest.mark.parametrize(
    "objective",
    ["poisson", "gamma", "tweedie", "inverse_gaussian", "negative_binomial", "log_loss"],
)
def test_the_families_and_binomial_log_loss_are_refused_by_name(objective: str) -> None:
    with pytest.raises(pydantic.ValidationError, match=objective):
        _spec(objective=objective)


@pytest.mark.req("FR-MODEL-37")
def test_max_bins_is_a_power_of_two_between_16_and_32768() -> None:
    assert _spec(max_bins=32).max_bins == 32
    for bad in (50, 8, 65536):
        with pytest.raises(pydantic.ValidationError, match="max_bins"):
            _spec(max_bins=bad)


@pytest.mark.req("FR-MODEL-37")
def test_the_interaction_grid_stays_in_the_jsonb_envelope() -> None:
    with pytest.raises(pydantic.ValidationError, match="interactions"):
        _spec(interactions=1, max_bins=512)
    assert _spec(interactions=1, max_bins=256).max_bins == 256


@pytest.mark.req("FR-MODEL-87")
def test_interactions_are_zero_or_one() -> None:
    with pytest.raises(pydantic.ValidationError, match="interactions"):
        _spec(interactions=2)


@pytest.mark.req("FR-MODEL-28")
def test_monotone_constraints_are_directions() -> None:
    with pytest.raises(pydantic.ValidationError, match="direction"):
        _spec(monotone_constraints={"age": 2})
    assert _spec(monotone_constraints={"age": 1, "area": 0}).monotone_constraints == {
        "age": 1,
        "area": 0,
    }
    assert _spec(monotone_constraints={}).monotone_constraints == {}


@pytest.mark.req("FR-MODEL-37")
def test_an_ebm_declares_no_offset() -> None:
    with pytest.raises(pydantic.ValidationError, match="GLM-only"):
        _spec(offset=OffsetSpec(kind="log_column", column="exposure_years"))


@pytest.mark.req("FR-MODEL-25")
def test_an_ebm_spec_round_trips_through_the_adapter() -> None:
    """`ebm` discriminates to `EbmSpec` — the sibling of the gbm test that used to name
    it as the unknown model type."""
    payload = _spec().model_dump(mode="json")
    assert isinstance(MODEL_SPEC_ADAPTER.validate_python(payload), EbmSpec)


@pytest.mark.req("FR-MODEL-37")
def test_the_common_block_flows_into_the_ebm_arm() -> None:
    spec = _spec(
        weight=WeightSpec(kind="column", column="n_claims"),
        seed=7,
        split_ref=SplitRef(split_artifact_id=new_uuid7()),
    )
    assert spec.weight == WeightSpec(kind="column", column="n_claims")
    assert spec.seed == 7
    assert spec.split_ref is not None


@pytest.mark.req("FR-MODEL-25")
def test_an_ebm_spec_cannot_hold_a_glm_fit() -> None:
    """Both unions are on one artifact, so the pairing has to be stated.

    An `EbmSpec` beside a `GlmFitResult` would be a model whose coefficient table
    describes a fit nobody made with the spec it sits beside.
    """
    spec = _spec()
    with pytest.raises(pydantic.ValidationError, match="model_type"):
        Model(
            id=new_uuid7(),
            model_family_slug=spec.model_family_slug,
            version=1,
            status=ModelStatus.FITTED,
            spec=spec,
            spec_hash="v3:sha256:" + "b" * 64,
            fit_result=GlmFitResult(converged=True, iterations=8, fit_seconds=1.0),
            diagnostics_id=new_uuid7(),
            dataset_version_id=spec.dataset_version_id,
        )
