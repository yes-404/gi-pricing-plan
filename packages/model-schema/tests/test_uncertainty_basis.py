"""What a penalised GLM may claim about its own uncertainty (FR-MODEL-99, OQ-MODEL-14).

`glum` returns the **unpenalised** information matrix for a penalised fit and warns that it
is incorrect. FR-MODEL-21's standard errors and FR-MODEL-63's interval are both read off
that one matrix, which is why the question could not be answered for the interval alone —
and the answer is a qualification carried with the numbers rather than a refusal that would
have had to take the standard errors with it.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    EarlyStopping,
    GbmFunctionRef,
    GbmSpec,
    GlmFitResult,
    GlmSpec,
    Model,
    ModelStatus,
    OffsetSpec,
    SplitRef,
    Uncertainty,
    UncertaintyBasis,
    UncertaintyKind,
    new_uuid7,
)

#: FR-MODEL-19: a Poisson frequency model must declare its exposure offset, and the spec
#: refuses one that does not — so every spec here carries it rather than dodging the family.
EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")


def _glm(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": new_uuid7(),
        "response_column": "claim_count",
        "offset": EXPOSURE,
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-99")
def test_the_basis_follows_alpha_and_nothing_else() -> None:
    """The single derivation. `alpha` is the only thing that makes a fit penalised.

    `l1_ratio` is the *mix* between L1 and L2 and scales nothing on its own: at `alpha = 0`
    there is no penalty to mix, so a spec carrying `l1_ratio=1.0` alone is unpenalised and
    its matrix is exact. Reading the basis off `l1_ratio` would label every elastic-net
    default as approximate.
    """
    assert _glm().uncertainty_basis is UncertaintyBasis.INFORMATION_MATRIX
    assert _glm(l1_ratio=1.0).uncertainty_basis is UncertaintyBasis.INFORMATION_MATRIX
    assert (
        _glm(alpha=25.0).uncertainty_basis
        is UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
    )
    #: Any penalty at all, not a threshold. A "small" alpha shrinks the estimates and the
    #: matrix still does not know it, so there is no size below which the label is untrue.
    assert (
        _glm(alpha=1e-9).uncertainty_basis
        is UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
    )


@pytest.mark.req("FR-MODEL-99")
def test_a_gbm_has_no_basis_because_it_has_no_matrix() -> None:
    """`None` is the right answer here, and it is not the same as "unknown".

    FR-MODEL-77 refuses a GBM interval outright rather than qualifying one, so there is no
    covariance matrix to describe. A basis invented for a GBM would be describing an
    interval the platform declines to produce.
    """
    gbm = GbmSpec(
        model_type="xgboost",
        model_family_slug="motor-ad-frequency",
        dataset_version_id=new_uuid7(),
        split_ref=SplitRef(split_artifact_id=new_uuid7()),
        response_column="claim_count",
        offset=EXPOSURE,
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 5, "eta": 0.05, "num_boost_round": 500},
        early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=50),
    )
    assert not hasattr(gbm, "uncertainty_basis")

    model = Model(
        id=new_uuid7(),
        model_family_slug="motor-ad-frequency",
        version=1,
        status=ModelStatus.DRAFT,
        spec=gbm,
        spec_hash="v3:sha256:" + "c" * 64,
        dataset_version_id=gbm.dataset_version_id,
    )
    assert model.uncertainty_basis is None


@pytest.mark.req("FR-MODEL-99")
def test_a_model_reports_the_basis_of_the_spec_it_was_fitted_from() -> None:
    """The reader for FR-MODEL-21's half: a coefficient surface asks the Model, not `alpha`.

    Derived rather than stored on the fit result, so the two can never disagree — the spec
    is pinned to the fit by `spec_hash` and both are immutable, so a stored copy could only
    ever agree or be wrong.
    """
    spec = _glm(alpha=25.0)
    model = Model(
        id=new_uuid7(),
        model_family_slug=spec.model_family_slug,
        version=1,
        status=ModelStatus.DRAFT,
        spec=spec,
        spec_hash="v3:sha256:" + "d" * 64,
        fit_result=GlmFitResult(converged=True, iterations=8, fit_seconds=1.0),
        dataset_version_id=spec.dataset_version_id,
    )
    assert model.uncertainty_basis is UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX


@pytest.mark.req("FR-MODEL-99")
def test_an_interval_with_no_stated_basis_cannot_be_serialised() -> None:
    """Negative: the qualification is not optional on a response that carries an interval.

    This is the defect OQ-MODEL-14 names, at the type: an interval whose basis is unstated
    is one every reader takes for exact inference, and for a penalised fit that reading is
    wrong in a direction nothing on the page discloses.
    """
    with pytest.raises(pydantic.ValidationError, match="no basis"):
        Uncertainty(kind=UncertaintyKind.CONFIDENCE_INTERVAL_MEAN, level=0.95)


@pytest.mark.req("FR-MODEL-99")
def test_an_absent_interval_cannot_carry_a_basis() -> None:
    """Negative, the other way: a basis describes a matrix an interval was read off.

    `unavailable` means there is no interval, so a basis beside it describes nothing — and
    a client matching on `basis` would find one on a response whose bounds are null.
    """
    from model_schema import UnavailableReason

    with pytest.raises(pydantic.ValidationError, match="basis"):
        Uncertainty(
            kind=UncertaintyKind.UNAVAILABLE,
            reason=UnavailableReason.NO_INTERVAL_MODELS_FITTED,
            basis=UncertaintyBasis.INFORMATION_MATRIX,
        )
