"""The approximating Model's spec and the artifact block that references it.

FR-MODEL-96 makes the GLM approximation a Model; FR-MODEL-102 makes it one a reader can
recognise without holding anything else. Every test here is a prohibition, for the reason
`test_gbm_spec.py` gives: a shape that can represent a nonsense model eventually holds one.
"""

from __future__ import annotations

import datetime

import pydantic
import pytest

from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    Coefficient,
    GlmApproximation,
    GlmSpec,
    OffsetSpec,
    RelativityLevel,
    TransparencyArtifact,
    TransparencyKind,
    new_uuid7,
)
from model_schema.transparency import EbmShapeFunctions

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


@pytest.mark.req("FR-MODEL-37")
def test_an_ebm_artifact_names_the_kind() -> None:
    """`kinds` is derived from which blocks are present, never stored beside them.

    §4.9 once declared `kinds` as a stored field and wrote the agreement between it and
    the blocks as an invariant note — two statements of one fact. The property removes
    the second statement, so the third kind is just another block to notice.
    """
    ebm_only = TransparencyArtifact(
        id=new_uuid7(),
        model_id=new_uuid7(),
        created_at=datetime.datetime.now(datetime.UTC),
        fidelity_statement="the EBM is the model, and its shape functions are its tables",
        ebm_shape_functions=EbmShapeFunctions(terms_blob="{}"),
    )
    assert ebm_only.kinds == (TransparencyKind.EBM_SHAPE_FUNCTIONS,)

    both = TransparencyArtifact(
        id=new_uuid7(),
        model_id=new_uuid7(),
        created_at=datetime.datetime.now(datetime.UTC),
        fidelity_statement="the GLM approximation reproduces the GBM's predictions",
        glm_approximation=GlmApproximation(
            approximating_model_id=new_uuid7(), r_squared=0.97, deviance_explained=0.96
        ),
        ebm_shape_functions=EbmShapeFunctions(terms_blob="{}"),
    )
    assert both.kinds == (
        TransparencyKind.GLM_APPROXIMATION,
        TransparencyKind.EBM_SHAPE_FUNCTIONS,
    )


@pytest.mark.req("FR-MODEL-33")
def test_an_ebm_artifact_needs_no_approximation_or_shap() -> None:
    """The EBM export alone is FR-MODEL-33's "at least one form".

    This is the whole of "transparent by construction": an EBM's shape functions ARE
    the model, exported directly as rateable tables — there is nothing to approximate,
    and no SHAP summary over a booster that does not exist.
    """
    artifact = TransparencyArtifact(
        id=new_uuid7(),
        model_id=new_uuid7(),
        created_at=datetime.datetime.now(datetime.UTC),
        fidelity_statement="the EBM's shape functions are the model, exported as tables",
        ebm_shape_functions=EbmShapeFunctions(terms_blob="{}"),
    )
    assert artifact.kinds == (TransparencyKind.EBM_SHAPE_FUNCTIONS,)


@pytest.mark.req("FR-MODEL-33")
def test_an_artifact_with_no_block_is_still_refused() -> None:
    """The third kind does not weaken "at least one": no block is still no explanation.

    An artifact with no block would satisfy R3's presence check while explaining
    nothing — the one state this shape must not be able to represent. The match pins
    the three-form message, so a revert to the two-form list fails here.
    """
    with pytest.raises(pydantic.ValidationError, match="EBM shape-functions export"):
        TransparencyArtifact(
            id=new_uuid7(),
            model_id=new_uuid7(),
            created_at=datetime.datetime.now(datetime.UTC),
            fidelity_statement="looks fine to me",
        )
