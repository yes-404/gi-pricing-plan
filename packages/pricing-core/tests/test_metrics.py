"""FR-MODEL-103/104/105 — evaluating and certifying a Custom Metric."""

from __future__ import annotations

import uuid

import numpy as np
import pytest
from pydantic import ValidationError

from model_schema.metrics import CustomMetric, MetricDirection
from model_schema.objectives import (
    TEMPLATE_APPLICABILITY,
    TEMPLATE_PARAMETERS,
    Applicability,
    CertificateOutcome,
    CheckStatus,
    ObjectiveTemplate,
    TemplateParameter,
    YDomain,
)
from pricing_core.modelling.metrics import certify_metric, evaluate_metric
from pricing_core.modelling.objectives import resolve_template_params, template_loss


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


# --------------------------------------------------------------------------------------
# FR-MODEL-103 — §4.5's defaults, across the **whole** template catalogue
#
# Every fixture in this suite, in `test_gbm.py` and in
# `backend/tests/test_custom_metrics_api.py` supplied a complete parameter set for a zero-
# or one-parameter template, so the single input shape that works was the only one anything
# exercised. `evaluate_metric` handed the template `dict(metric.params)` as stored, and
# `CustomMetric.params` holds only what the **author** chose — so 10 of the 12 templates
# raised `KeyError` and the whole suite saw none of it. These iterate the catalogue rather
# than name a template, which is the property that makes them hold for a template added
# after them.
# --------------------------------------------------------------------------------------

_CATALOGUE = list(ObjectiveTemplate)
_TEMPLATE_IDS = [t.value for t in _CATALOGUE]
_REQUIRED = {
    t: tuple(p for p in TEMPLATE_PARAMETERS[t] if p.default is None) for t in _CATALOGUE
}


def _a_valid_value(parameter: TemplateParameter) -> float | int:
    """Some value inside §4.5's declared range — enough to construct, not a recommendation.

    Derived from the parameter rather than tabulated against a list of names, so a template
    added to §4.5 tomorrow is covered by these tests on the day it lands instead of being
    silently skipped by a table nobody updated.
    """
    if parameter.kind == "money_minor":
        return 25_000
    low = 0.0 if parameter.minimum is None else parameter.minimum
    high = low + 2.0 if parameter.maximum is None else parameter.maximum
    return (low + high) / 2.0


def _catalogue_metric(template: ObjectiveTemplate) -> CustomMetric:
    """A metric carrying **only** what §4.5 gives no default for — the author's own choice."""
    return _metric(
        template,
        slug="cat-" + template.value.replace("_", "-"),
        params={p.name: _a_valid_value(p) for p in _REQUIRED[template]},
        applicability=TEMPLATE_APPLICABILITY[template],
    )


@pytest.mark.req("FR-MODEL-103")
@pytest.mark.parametrize("template", _CATALOGUE, ids=_TEMPLATE_IDS)
def test_every_template_evaluates_with_only_its_required_parameters(
    template: ObjectiveTemplate,
) -> None:
    """The metric path resolves §4.5's defaults exactly as the objective path does.

    Both halves are asserted. The value must be the one the *resolved* parameters give — a
    metric path that quietly substituted its own default would still evaluate, and would
    mean something other than the objective compiled from the same template. And the
    artifact must be unchanged by evaluation: `params` still holds the author's choice
    alone, which is why the defaults have to be resolved at use in the first place.
    """
    metric = _catalogue_metric(template)
    author_chose = dict(metric.params)

    y = np.array([0.5, 1.0, 3.0])
    f = np.array([-0.4, 0.1, 0.8])
    w = np.array([1.0, 2.0, 4.0])
    value = evaluate_metric(metric, y, f, w)

    resolved = resolve_template_params(template, author_chose)
    expected = float(np.average(template_loss(template)(y, f, resolved), weights=w))
    assert value == pytest.approx(expected)
    assert np.isfinite(value)
    assert dict(metric.params) == author_chose


@pytest.mark.req("FR-MODEL-103")
@pytest.mark.parametrize("template", _CATALOGUE, ids=_TEMPLATE_IDS)
def test_every_template_certifies_with_only_its_required_parameters(
    template: ObjectiveTemplate,
) -> None:
    """`certify_metric` resolves through the same call.

    It evaluates the template twice more directly — the `finiteness` grid and the
    `smoke_evaluation` hand-computable — and both of those sites were unresolved too.
    """
    result = certify_metric(_catalogue_metric(template), seed=20260819)
    assert {c.name for c in result.checks} == {
        "finiteness",
        "direction_holds",
        "scale_behaviour",
        "smoke_evaluation",
    }


@pytest.mark.req("FR-MODEL-103")
@pytest.mark.parametrize(
    "template",
    [t for t in _CATALOGUE if _REQUIRED[t]],
    ids=[t.value for t in _CATALOGUE if _REQUIRED[t]],
)
def test_a_metric_missing_a_parameter_with_no_default_is_refused(
    template: ObjectiveTemplate,
) -> None:
    """The half of `_the_parameters_are_the_templates_own` that `CustomMetric` was missing.

    `CustomObjective` has refused this since the objectives slice; `CustomMetric` copied
    only the unknown-key half, so `POST /api/v1/custom-metrics` answered 201 for a
    `capped_gamma` with no `cap` and certification then died on a bare `KeyError` naming
    nothing. A template that cannot be evaluated at all must not be storable.
    """
    with pytest.raises(ValidationError) as raised:
        _metric(
            template,
            slug="bare-" + template.value.replace("_", "-"),
            params={},
            applicability=TEMPLATE_APPLICABILITY[template],
        )
    message = str(raised.value)
    assert "no default" in message
    for parameter in _REQUIRED[template]:
        assert repr(parameter.name) in message
