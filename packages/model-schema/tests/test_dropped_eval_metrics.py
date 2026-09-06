"""FR-161: a declared eval metric a backend could not evaluate is recorded."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema.modelling import DroppedEvalMetric, GbmFitResult, OffsetSpec
from model_schema.refs import BlobRef

EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")


def _result(**over: object) -> GbmFitResult:
    base: dict[str, object] = {
        "model_type": "xgboost",
        "booster_blob": BlobRef(sha256="a" * 64, bytes=2048, media_type="application/json"),
        "booster_format": "xgboost_json",
        "feature_order": ("driver_age_banded", "vehicle_group_rated"),
        "feature_dtypes": {"driver_age_banded": "i32", "vehicle_group_rated": "i32"},
        "monotone_constraints": (1, 0),
        "base_margin": EXPOSURE,
        "best_iteration": 312,
        "rows": 678_013,
        "fit_seconds": 41.2,
        "library_versions": {"xgboost": "3.4.1"},
    }
    base.update(over)
    return GbmFitResult(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-161")
def test_a_dropped_metric_names_a_reason_from_the_closed_set() -> None:
    """One reason exists today (FR-160). A free-text field would let a second be
    invented at a call site instead of declared in the contract the frontend generates
    from, which is how a status enum turns into prose."""
    with pytest.raises(ValidationError):
        DroppedEvalMetric(name="poisson-nll", reason="because")  # type: ignore[arg-type]


@pytest.mark.req("FR-161")
def test_the_same_metric_cannot_be_dropped_twice() -> None:
    """A name appearing twice is a bug in the producer, not two facts about the fit."""
    dropped = DroppedEvalMetric(
        name="poisson-nll", reason="builtin_evaluated_before_custom_stopping_metric"
    )
    with pytest.raises(ValidationError, match="named once"):
        _result(dropped_eval_metrics=(dropped, dropped))


@pytest.mark.req("FR-161")
def test_a_fit_result_drops_nothing_by_default() -> None:
    """The overwhelmingly common case, and the one every artifact written before this
    field existed is in: no metric was dropped, and the tuple says so rather than being
    absent."""
    assert _result().dropped_eval_metrics == ()
