"""FR-MODEL-103/104/105 — the Custom Metric artifact."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from model_schema.metrics import (
    FITTABLE_METRIC_STATUSES,
    VALID_METRIC_TRANSITIONS,
    CustomMetric,
    MetricDirection,
    MetricStatus,
)
from model_schema.objectives import Applicability, ObjectiveKind, ObjectiveTemplate, YDomain


def _applicability() -> Applicability:
    return Applicability(
        responses=("claim_severity",),
        backends=("xgboost",),
        offset_required=False,
        y_domain=YDomain(min_inclusive=0.0),
    )


def _metric(**overrides: object) -> CustomMetric:
    kwargs: dict[str, object] = {
        "id": uuid.uuid4(),
        "slug": "capped-gamma-nll",
        "version": 2,
        "template": ObjectiveTemplate.CAPPED_GAMMA,
        "params": {"cap": 250000},
        "applicability": _applicability(),
        "direction": MetricDirection.LOWER_IS_BETTER,
    }
    kwargs.update(overrides)
    return CustomMetric(**kwargs)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-103")
def test_a_template_metric_is_constructible() -> None:
    metric = _metric()
    assert metric.kind is ObjectiveKind.TEMPLATE
    assert metric.status is MetricStatus.DRAFT
    assert metric.certificate_id is None


@pytest.mark.req("FR-MODEL-103")
def test_a_metric_carries_no_hessian_fields() -> None:
    """A metric is never differentiated, so the fields cannot be set even by mistake."""
    assert "hessian_strategy" not in CustomMetric.model_fields
    assert "hessian_min" not in CustomMetric.model_fields
    with pytest.raises(ValidationError):
        _metric(hessian_strategy="clip_to_min")


@pytest.mark.req("FR-MODEL-103")
def test_an_unknown_parameter_is_refused_not_ignored() -> None:
    """A misspelled `cap` silently dropped is an uncapped metric named capped."""
    with pytest.raises(ValidationError, match="cap"):
        _metric(params={"capp": 250000.0})


@pytest.mark.req("FR-MODEL-103")
def test_phase_1_admits_no_expression_metric() -> None:
    with pytest.raises(ValidationError, match="template"):
        _metric(kind=ObjectiveKind.EXPRESSION, template=None)


@pytest.mark.req("FR-MODEL-104")
def test_direction_has_no_default() -> None:
    """A guessed direction stops the fit at the wrong round in half of cases."""
    assert CustomMetric.model_fields["direction"].is_required()


@pytest.mark.req("FR-MODEL-105")
def test_a_status_past_draft_needs_a_certificate() -> None:
    with pytest.raises(ValidationError, match="certificate"):
        _metric(status=MetricStatus.CERTIFIED, certificate_id=None)


@pytest.mark.req("FR-MODEL-105")
def test_draft_is_not_fittable_and_certified_is() -> None:
    """A draft metric has no certificate, so its behaviour is unproven."""
    assert MetricStatus.DRAFT not in FITTABLE_METRIC_STATUSES
    assert MetricStatus.CERTIFIED in FITTABLE_METRIC_STATUSES
    assert MetricStatus.DEPRECATED not in FITTABLE_METRIC_STATUSES


@pytest.mark.req("FR-MODEL-105")
def test_the_lifecycle_has_no_edge_out_of_deprecated() -> None:
    assert VALID_METRIC_TRANSITIONS[MetricStatus.DEPRECATED] == frozenset()
    assert MetricStatus.CERTIFIED in VALID_METRIC_TRANSITIONS[MetricStatus.REVIEW]
    assert MetricStatus.DRAFT not in VALID_METRIC_TRANSITIONS[MetricStatus.REVIEW]
