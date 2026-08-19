"""The approximating Model's spec and the artifact block that references it.

FR-MODEL-96 makes the GLM approximation a Model; FR-MODEL-102 makes it one a reader can
recognise without holding anything else. Every test here is a prohibition, for the reason
`test_gbm_spec.py` gives: a shape that can represent a nonsense model eventually holds one.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    Coefficient,
    GlmApproximation,
    GlmSpec,
    OffsetSpec,
    RelativityLevel,
    new_uuid7,
)

EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")


def _surrogate(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency-approx",
        "dataset_version_id": new_uuid7(),
        "response_column": SURROGATE_RESPONSE_COLUMN,
        "approximates_model_id": new_uuid7(),
        "family": "gamma",
        "link": "log",
        "offset": EXPOSURE,
    }
    return GlmSpec.model_validate(base | over)


@pytest.mark.req("FR-MODEL-102")
def test_a_surrogate_declares_both_halves() -> None:
    """The pair is what makes a surrogate recognisable — neither half alone does."""
    spec = _surrogate()
    assert spec.approximates_model_id is not None
    assert spec.response_column == SURROGATE_RESPONSE_COLUMN


@pytest.mark.req("FR-MODEL-102")
def test_a_spec_naming_a_source_model_over_an_observed_response_is_refused() -> None:
    """It would be a model fitted on claims that every reader takes for a surrogate."""
    with pytest.raises(pydantic.ValidationError, match=SURROGATE_RESPONSE_COLUMN):
        _surrogate(response_column="claim_count")


@pytest.mark.req("FR-MODEL-102")
def test_a_spec_fitting_the_surrogate_column_with_no_source_model_is_refused() -> None:
    """A model of a prediction, with nothing saying whose prediction it is."""
    with pytest.raises(pydantic.ValidationError, match="approximates_model_id"):
        _surrogate(approximates_model_id=None)


@pytest.mark.req("FR-MODEL-96")
def test_the_artifact_block_references_the_model_that_holds_the_table() -> None:
    block = GlmApproximation(
        approximating_model_id=new_uuid7(), r_squared=0.97, deviance_explained=0.96
    )
    assert block.coefficients == ()


@pytest.mark.req("FR-MODEL-96")
def test_a_legacy_artifact_block_still_validates() -> None:
    """The other half of the compatibility guarantee the option-A decision rests on.

    Every other test in this module proves *refusal* — both eras together, neither era at
    all. None of them prove the thing the maintainer actually decided to keep: an artifact
    written before 2026-08-19, carrying its coefficients and relativities inline with
    `approximating_model_id` unset, still validates today. A suite that only proves refusal
    cannot protect that guarantee — deleting `coefficients`/`relativities` tomorrow would
    leave every existing test here green.
    """
    block = GlmApproximation(
        r_squared=0.97,
        deviance_explained=0.96,
        coefficients=(
            Coefficient(
                term="intercept", estimate=-2.4, std_error=0.01, z=-199.8,
                p_value=0.0, ci_95=(-2.44, -2.39),
            ),
        ),
        relativities={
            "region": (RelativityLevel(level="north", relativity=1.0, is_base=True),)
        },
    )
    assert block.approximating_model_id is None
    assert block.coefficients != ()
    assert block.relativities


@pytest.mark.req("FR-MODEL-96")
def test_an_artifact_block_carrying_both_eras_is_refused() -> None:
    """A reference *and* an inline table are two answers to "where is the table?"."""
    with pytest.raises(pydantic.ValidationError, match="exactly one"):
        GlmApproximation(
            approximating_model_id=new_uuid7(),
            r_squared=0.97,
            deviance_explained=0.96,
            coefficients=(
                Coefficient(
                    term="intercept", estimate=-2.4, std_error=0.01, z=-199.8,
                    p_value=0.0, ci_95=(-2.44, -2.39),
                ),
            ),
        )


@pytest.mark.req("FR-MODEL-96")
def test_an_artifact_block_carrying_neither_era_is_refused() -> None:
    """A fidelity score with no table behind it says the approximation was good without
    saying what it was — the module docstring's own reason for holding the table."""
    with pytest.raises(pydantic.ValidationError, match="exactly one"):
        GlmApproximation(r_squared=0.97, deviance_explained=0.96)
