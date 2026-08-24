"""FR-MODEL-103/104/105 — the Custom Metric artifact."""

from __future__ import annotations

import datetime as _datetime
import uuid

import pytest
from pydantic import ValidationError

from model_schema.metrics import (
    FITTABLE_METRIC_STATUSES,
    METRIC_CERTIFICATE_CHECKS,
    VALID_METRIC_TRANSITIONS,
    CustomMetric,
    MetricCertificate,
    MetricDirection,
    MetricStatus,
)
from model_schema.objectives import (
    Applicability,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    ObjectiveKind,
    ObjectiveTemplate,
    SamplingSpec,
    YDomain,
)

#: `capped_gamma`'s own applicability (`TEMPLATE_APPLICABILITY`, objectives.py) declares
#: `y_domain=YDomain(min_exclusive=0.0)` — severity is strictly positive. The fixture must
#: match it or every `_metric()` call fails `_applicability_is_within_the_template` before
#: reaching whatever the test means to check.
SAMPLING = SamplingSpec(
    n_points=1000, seed=20260819, y_range=(0.0, 1e7), f_range=(-20.0, 20.0), w_range=(1e-3, 1e4),
)


def _applicability() -> Applicability:
    return Applicability(
        responses=("claim_severity",),
        backends=("xgboost",),
        offset_required=False,
        y_domain=YDomain(min_exclusive=0.0),
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


@pytest.mark.req("FR-MODEL-103")
def test_an_applicability_wider_than_the_template_is_refused() -> None:
    """A `capped_gamma` metric claiming `claim_count` would evaluate a Gamma loss on counts.

    That loss is `y/μ + f`, and `claim_count` is zero most of the time — `evaluate_metric`
    (Task 3) would compute `inf`. An author may narrow §4.5's applicability and may not
    widen it, the same rule `CustomObjective` enforces for the objective it evaluates.
    """
    with pytest.raises(ValidationError, match="wider than"):
        _metric(
            applicability=Applicability(
                responses=("claim_severity", "claim_count"),
                backends=("xgboost",),
                offset_required=False,
                y_domain=YDomain(min_exclusive=0.0),
            )
        )


@pytest.mark.req("FR-MODEL-104")
def test_direction_has_no_default() -> None:
    """A guessed direction stops the fit at the wrong round in half of cases."""
    assert CustomMetric.model_fields["direction"].is_required()


@pytest.mark.req("FR-MODEL-104")
def test_not_ordered_direction_is_refused() -> None:
    """`not_ordered` has no "better" for an early-stopping loop to compare toward."""
    with pytest.raises(ValidationError, match="FR-MODEL-104"):
        _metric(direction=MetricDirection.NOT_ORDERED)


@pytest.mark.req("FR-MODEL-104")
def test_closer_to_one_direction_is_refused() -> None:
    """Not the monotone lower/higher comparison a backend's stopping loop can consume."""
    with pytest.raises(ValidationError, match="FR-MODEL-104"):
        _metric(direction=MetricDirection.CLOSER_TO_ONE_IS_BETTER)


@pytest.mark.req("FR-MODEL-105")
def test_a_status_past_draft_needs_a_certificate() -> None:
    with pytest.raises(ValidationError, match="certificate"):
        _metric(status=MetricStatus.CERTIFIED, certificate_id=None)


@pytest.mark.req("FR-MODEL-105")
def test_a_metric_abandoned_before_certification_is_withdrawn_not_certified() -> None:
    """`draft -> deprecated` needs no certificate: withdrawing is not claiming proof.

    `VALID_METRIC_TRANSITIONS[MetricStatus.DRAFT]` reaches `deprecated` directly, so this
    object must be constructible with no `certificate_id` at all — a metric abandoned
    before anyone ever certified it was never given the chance to earn one.
    """
    metric = _metric(status=MetricStatus.DEPRECATED, certificate_id=None)
    assert metric.status is MetricStatus.DEPRECATED
    assert metric.certificate_id is None


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


def _battery(names: tuple[str, ...] = METRIC_CERTIFICATE_CHECKS) -> tuple[CertificateCheck, ...]:
    """A passing check per name — FR-MODEL-105's four unless a test asks otherwise."""
    return tuple(
        CertificateCheck(name=name, status=CheckStatus.PASS, detail=f"{name} ran")
        for name in names
    )


def _certificate(checks: tuple[CertificateCheck, ...]) -> MetricCertificate:
    return MetricCertificate(
        id=uuid.uuid4(),
        custom_metric_id=uuid.uuid4(),
        metric_version=2,
        certified_at=_datetime.datetime(2026, 8, 19, tzinfo=_datetime.UTC),
        result=CertificateResult(
            checks=checks,
            sampling=SAMPLING,
            overall=CertificateResult.outcome_of(checks),
        ),
    )


@pytest.mark.req("FR-MODEL-105")
def test_a_metric_certificate_round_trips_a_certificate_result() -> None:
    """`certified_at` is a real timestamp — Task 5 persists this object as a database row."""
    certificate = _certificate(_battery())
    assert certificate.metric_version == 2
    assert certificate.certified_at == _datetime.datetime(2026, 8, 19, tzinfo=_datetime.UTC)
    assert certificate.result.overall is CertificateOutcome.CERTIFIED


@pytest.mark.req("FR-MODEL-126")
def test_the_full_four_check_battery_is_accepted() -> None:
    """The positive control for the two refusals below — four names, each once."""
    certificate = _certificate(_battery())
    assert {check.name for check in certificate.result.checks} == set(METRIC_CERTIFICATE_CHECKS)


@pytest.mark.req("FR-MODEL-126")
def test_a_metric_certificate_short_of_its_battery_is_refused() -> None:
    """FR-MODEL-105's four are the artifact's obligation (FR-MODEL-126).

    Before 2026-08-24 the certificate above — one `finiteness` check — was accepted, which
    is how a metric could reach `certified` on evidence that never ran `direction_holds`.
    """
    with pytest.raises(ValidationError, match="missing"):
        _certificate(_battery(("finiteness",)))


@pytest.mark.req("FR-MODEL-126")
def test_four_checks_with_direction_holds_replaced_is_refused() -> None:
    """Right length, wrong evidence: `direction_holds` gone and `finiteness` run twice.

    That is the check catching a `direction` declared backwards, and a count-only floor
    admits a certificate without it.
    """
    names = tuple(
        "finiteness" if name == "direction_holds" else name for name in METRIC_CERTIFICATE_CHECKS
    )
    assert len(names) == 4
    with pytest.raises(ValidationError) as raised:
        _certificate(_battery(names))
    assert "direction_holds" in str(raised.value)
    assert "duplicated ['finiteness']" in str(raised.value)


@pytest.mark.req("FR-MODEL-126")
def test_an_objective_check_name_does_not_belong_in_a_metric_battery() -> None:
    """The two batteries share §4.7's vocabulary and are not interchangeable.

    `smoke_fit` is the objective's; a metric runs `smoke_evaluation`, which evaluates rather
    than fits. Four checks, one of them from the wrong artifact.
    """
    names = (*METRIC_CERTIFICATE_CHECKS[:3], "smoke_fit")
    with pytest.raises(ValidationError, match=r"unexpected \['smoke_fit'\]"):
        _certificate(_battery(names))
