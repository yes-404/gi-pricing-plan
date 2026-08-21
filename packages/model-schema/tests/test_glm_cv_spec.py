"""FR-MODEL-20/FR-MODEL-53: the documented penalty path and CV selection on `GlmSpec`."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema import GlmCvSpec, GlmSpec, OffsetSpec


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-20")
def test_a_fixed_alpha_spec_needs_no_cv_block() -> None:
    spec = _spec(alpha=0.1, l1_ratio=0.5)
    assert spec.select_by == "fixed"
    assert spec.cv is None


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_declares_its_cv_spec() -> None:
    spec = _spec(select_by="cv", cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.1, 1.0)))
    assert spec.cv is not None
    assert spec.cv.folds == 4
    assert spec.alpha == 0.0


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_without_a_cv_block_is_refused() -> None:
    """Negative: `select_by='cv'` names a scan with nothing to scan."""
    with pytest.raises(ValidationError, match="cv is not set"):
        _spec(select_by="cv")


@pytest.mark.req("FR-MODEL-53")
def test_a_cv_block_under_fixed_selection_is_refused() -> None:
    """Negative: a scanned path with nothing selecting from it describes a fit that was
    never asked to run it — silently ignoring `cv` would let a caller believe their model
    was cross-validated when `select_by` never asked for that."""
    with pytest.raises(ValidationError, match="select_by='fixed'"):
        _spec(cv=GlmCvSpec())


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_with_a_nonzero_fixed_alpha_is_refused() -> None:
    """Negative: two answers to "how penalised is this fit" — a fixed `alpha` and a
    scanned `cv.alphas` — and only one of them is ever read under CV selection."""
    with pytest.raises(ValidationError, match="alpha is non-zero"):
        _spec(select_by="cv", alpha=0.2, cv=GlmCvSpec())


@pytest.mark.req("FR-MODEL-20")
def test_a_path_with_fewer_than_two_alphas_is_refused() -> None:
    """Negative: one alpha is a fixed fit, not a path to select from."""
    with pytest.raises(ValidationError, match="at least 2"):
        GlmCvSpec(alphas=(0.1,))


@pytest.mark.req("FR-MODEL-20")
def test_a_path_with_a_repeated_alpha_is_refused() -> None:
    with pytest.raises(ValidationError, match="repeats"):
        GlmCvSpec(alphas=(0.1, 0.1, 0.5))


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_cv_needs_its_key_column() -> None:
    with pytest.raises(ValidationError, match="key_column"):
        GlmCvSpec(method="grouped_by_key")


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_cv_needs_its_time_column() -> None:
    with pytest.raises(ValidationError, match="time_column"):
        GlmCvSpec(method="temporal")


@pytest.mark.req("FR-MODEL-99")
def test_cv_selection_uses_the_naive_uncertainty_basis() -> None:
    """FR-MODEL-99's `uncertainty_basis` reads `alpha`, and CV pins `alpha` to 0.0 — so
    without this, a CV-selected (near-certainly penalised) fit would report the plain
    information-matrix basis a genuinely unpenalised fit gets. Recorded in this plan's
    header as an interaction FR-MODEL-99 does not itself cover."""
    from model_schema import UncertaintyBasis

    spec = _spec(select_by="cv", cv=GlmCvSpec())
    assert spec.uncertainty_basis is UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
