"""FR-MODEL-24: `offset_model_ref` on `OffsetSpec` — the declared shape, and what is
refused. Negative tests first: a staged contract admits only what a slice has built."""

import pydantic
import pytest

from model_schema import GlmSpec, OffsetSpec, new_uuid7


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": new_uuid7(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-24")
def test_a_model_offset_names_its_model() -> None:
    with pytest.raises(pydantic.ValidationError, match="offset_model_ref"):
        _spec(offset=OffsetSpec(kind="model"))


@pytest.mark.req("FR-MODEL-24")
def test_a_model_ref_declares_the_model_kind() -> None:
    with pytest.raises(pydantic.ValidationError, match=r"kind.*model"):
        _spec(offset=OffsetSpec(offset_model_ref="model:base@1"))


@pytest.mark.req("FR-MODEL-24")
def test_the_ref_must_name_a_model_not_any_artifact() -> None:
    with pytest.raises(pydantic.ValidationError, match="model:"):
        _spec(offset=OffsetSpec(kind="model", offset_model_ref="dataset:thing@1"))


@pytest.mark.req("FR-MODEL-24")
def test_a_model_offset_spec_constructs_and_round_trips() -> None:
    spec = _spec(offset=OffsetSpec(kind="model", offset_model_ref="model:base@7"))
    dumped = spec.model_dump(mode="json")["offset"]
    assert dumped["offset_model_ref"] == "model:base@7"
    assert dumped["kind"] == "model"
