"""The response vocabulary an EBM prediction needs (W32-4).

An EBM is additive by construction and carries no covariance matrix and no quantile pair,
so the honest answer to "what is the uncertainty" is a typed absence with a reason of its
own. These tests pin the two shape changes that answer costs.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import (
    PredictedRow,
    Prediction,
    UnavailableReason,
    Uncertainty,
    UncertaintyKind,
    new_uuid7,
)


def _prediction(**over: object) -> Prediction:
    base: dict[str, object] = {
        "model_id": new_uuid7(),
        "model_family_slug": "freq-ebm",
        "version": 1,
        "model_type": "ebm",
        "uncertainty": Uncertainty(
            kind=UncertaintyKind.UNAVAILABLE,
            reason=UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
        ),
        "rows": (PredictedRow(expected=0.25),),
    }
    base.update(over)
    return Prediction(**base)  # type: ignore[arg-type]


def test_a_prediction_can_declare_the_ebm_model_type() -> None:
    """`model_type` is a closed `Literal`, so an EBM response was unrepresentable until
    this change — the endpoint could not have returned one even with the arm built."""
    assert _prediction().model_type == "ebm"


def test_the_no_interval_reason_names_the_model_type_rather_than_a_missing_pair() -> None:
    """The value is the wire form the frontend's generated union will carry."""
    assert UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL == "model_type_has_no_interval"


def test_the_new_reason_still_obeys_the_kind_and_evidence_validator() -> None:
    """A reason beside anything but `unavailable` is evidence for a claim the response is
    not making — the rule the other four members obey, checked once for the new one.

    `match=` pins which clause fired: `level` is supplied so the validator gets past its
    own earlier check, leaving the reason clause as the only thing this can be failing on.
    """
    with pytest.raises(ValidationError, match="A reason explains an absence"):
        Uncertainty(
            kind=UncertaintyKind.CONFIDENCE_INTERVAL_MEAN,
            reason=UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
            level=0.95,
        )


def test_an_ebm_response_carries_no_bounds_on_any_row() -> None:
    """`Prediction`'s own cross-check, exercised on the new arm: an `unavailable` verdict
    beside a row carrying bounds is two answers to one question."""
    with pytest.raises(ValidationError):
        _prediction(rows=(PredictedRow(expected=0.25, lower=0.2, upper=0.3),))


def test_an_unknown_model_type_is_still_refused() -> None:
    """Widening a `Literal` by one member must not turn it into `str`."""
    with pytest.raises(ValidationError):
        _prediction(model_type="random_forest")
