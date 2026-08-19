"""FR-MODEL-103/104/105 — evaluating and certifying a Custom Metric."""

from __future__ import annotations

import uuid

import numpy as np
import pytest

from model_schema.metrics import CustomMetric, MetricDirection
from model_schema.objectives import (
    Applicability,
    CertificateOutcome,
    CheckStatus,
    ObjectiveTemplate,
    YDomain,
)
from pricing_core.modelling.metrics import certify_metric, evaluate_metric


def _metric(template: ObjectiveTemplate = ObjectiveTemplate.POISSON, **kw: object) -> CustomMetric:
    kwargs: dict[str, object] = {
        "id": uuid.uuid4(),
        "slug": "poisson-nll",
        "version": 1,
        "template": template,
        "params": {},
        "applicability": Applicability(
            responses=("claim_count",),
            backends=("xgboost",),
            offset_required=True,
            y_domain=YDomain(min_inclusive=0.0),
        ),
        "direction": MetricDirection.LOWER_IS_BETTER,
    }
    kwargs.update(kw)
    return CustomMetric(**kwargs)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-103")
def test_the_metric_is_the_weighted_mean_of_the_templates_loss() -> None:
    """Reuses the objective catalogue's arithmetic — no second implementation."""
    from pricing_core.modelling.objectives import template_loss

    y = np.array([0.0, 1.0, 3.0])
    f = np.array([-0.2, 0.1, 1.0])
    w = np.array([1.0, 2.0, 4.0])
    expected = float(np.average(template_loss(ObjectiveTemplate.POISSON)(y, f, {}), weights=w))
    assert evaluate_metric(_metric(), y, f, w) == pytest.approx(expected)


@pytest.mark.req("FR-MODEL-103")
def test_weights_are_honoured_not_ignored() -> None:
    """An exposure-weighted metric that ignores weights is a different metric.

    `f` must differ between the two rows: the Poisson loss is `exp(f) - y*f`, and at
    `f = 0` the `y`-dependent term vanishes, so both rows would score identically and no
    choice of weights could distinguish "honoured" from "ignored" — a false pass either
    way, not evidence of anything.
    """
    y = np.array([0.0, 5.0])
    f = np.array([0.0, 1.0])
    flat = evaluate_metric(_metric(), y, f, np.array([1.0, 1.0]))
    tilted = evaluate_metric(_metric(), y, f, np.array([1.0, 99.0]))
    assert flat != pytest.approx(tilted)


@pytest.mark.req("FR-MODEL-104")
def test_certification_catches_a_direction_declared_backwards() -> None:
    """The check that exists because the defect is otherwise invisible."""
    backwards = _metric(direction=MetricDirection.HIGHER_IS_BETTER)
    result = certify_metric(backwards, seed=20260819)
    direction = next(c for c in result.checks if c.name == "direction_holds")
    assert direction.status is CheckStatus.FAILED
    assert result.overall is CertificateOutcome.FAILED


@pytest.mark.req("FR-MODEL-105")
def test_a_correctly_declared_metric_certifies() -> None:
    result = certify_metric(_metric(), seed=20260819)
    assert result.overall in (
        CertificateOutcome.CERTIFIED,
        CertificateOutcome.CERTIFIED_WITH_FINDINGS,
    )
    assert {c.name for c in result.checks} == {
        "finiteness",
        "direction_holds",
        "scale_behaviour",
        "smoke_evaluation",
    }


@pytest.mark.req("FR-MODEL-105")
def test_no_derivative_check_appears_on_a_metric_certificate() -> None:
    """Absent, not `not_applicable` — the question is not askable of a metric."""
    result = certify_metric(_metric(), seed=20260819)
    names = {c.name for c in result.checks}
    assert not {n for n in names if "gradient" in n or "hessian" in n or n == "convexity"}


@pytest.mark.req("FR-MODEL-105")
def test_certification_is_deterministic_under_its_seed() -> None:
    first = certify_metric(_metric(), seed=20260819)
    second = certify_metric(_metric(), seed=20260819)
    assert [(c.name, c.status, c.detail) for c in first.checks] == [
        (c.name, c.status, c.detail) for c in second.checks
    ]
