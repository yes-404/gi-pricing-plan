"""The custom-objective contract's invariants (`02` §3.7, §4.5, §4.7).

Four of these are the reason the module exists rather than a dict of parameters:

* **A template takes exactly its own parameters.** An unknown key is almost always a
  misspelling of a real one, and a misspelled `w_over` leaves the real parameter at its
  default — a loss asymmetric in the wrong direction, which fits and converges.
* **Money is integer minor units** (`CLAUDE.md` §7). A cap of `25000.0` beside claim
  amounts in pence is wrong by a factor of a hundred and looks entirely reasonable.
* **Applicability narrows and never widens.** The template says where `pricing-core`'s
  analytic derivatives are valid; an author may restrict that and may not extend it.
* **A certificate's verdict is the one its checks imply.** Submission reads the verdict and
  an approver reads the checks, so the artifact must make them impossible to disagree.
"""

from __future__ import annotations

import datetime as _datetime

import pydantic
import pytest

from model_schema import (
    OBJECTIVE_CERTIFICATE_CHECKS,
    TEMPLATE_APPLICABILITY,
    TEMPLATE_PARAMETERS,
    VALID_OBJECTIVE_TRANSITIONS,
    Applicability,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    CustomObjective,
    HessianStrategy,
    ObjectiveBackend,
    ObjectiveCertificate,
    ObjectiveKind,
    ObjectiveStatus,
    ObjectiveTemplate,
    ResponseKind,
    SamplingSpec,
    YDomain,
    new_uuid7,
)

SAMPLING = SamplingSpec(
    n_points=1000, seed=20260818, y_range=(0.0, 1e7), f_range=(-20.0, 20.0),
    w_range=(1e-3, 1e4),
)


def _battery(names: tuple[str, ...] = OBJECTIVE_CERTIFICATE_CHECKS) -> tuple[CertificateCheck, ...]:
    """A passing check per name — §4.7's nine unless a test asks for something else."""
    return tuple(
        CertificateCheck(name=name, status=CheckStatus.PASS, detail=f"{name} ran")
        for name in names
    )


def _certificate(checks: tuple[CertificateCheck, ...]) -> ObjectiveCertificate:
    return ObjectiveCertificate(
        id=new_uuid7(),
        custom_objective_id=new_uuid7(),
        objective_version=3,
        certified_at=_datetime.datetime(2026, 8, 18, tzinfo=_datetime.UTC),
        result=CertificateResult(
            checks=checks,
            sampling=SAMPLING,
            overall=CertificateResult.outcome_of(checks),
            library_versions={"numpy": "2.3.0"},
        ),
    )


def _objective(
    template: ObjectiveTemplate = ObjectiveTemplate.TWEEDIE,
    params: dict[str, int | float] | None = None,
    **kwargs: object,
) -> CustomObjective:
    return CustomObjective(
        id=new_uuid7(),
        slug="burning-cost-tweedie",
        version=1,
        template=template,
        params={"p": 1.4} if params is None else params,
        applicability=TEMPLATE_APPLICABILITY[template],
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.mark.req("FR-MODEL-38")
def test_a_template_objective_is_the_artifact_a_model_can_reference() -> None:
    objective = _objective()
    assert objective.kind is ObjectiveKind.TEMPLATE
    assert objective.status is ObjectiveStatus.DRAFT
    assert objective.hessian_strategy is HessianStrategy.CLIP_TO_MIN


@pytest.mark.req("FR-MODEL-75")
def test_an_expression_objective_cannot_be_constructed_in_phase_1() -> None:
    """The second door behind the API's `OBJECTIVE_KIND_NOT_ENABLED`.

    The artifact carries no `loss` field, so an `expression` objective persisted through
    any other route would be one whose loss is nowhere written down.
    """
    with pytest.raises(pydantic.ValidationError, match="templates only"):
        _objective(kind=ObjectiveKind.EXPRESSION)


@pytest.mark.req("FR-MODEL-39")
def test_every_shipped_template_has_a_parameter_row_and_an_applicability_block() -> None:
    """§4.5's table, checked against the enum rather than trusted to match it."""
    assert set(TEMPLATE_PARAMETERS) == set(ObjectiveTemplate)
    assert set(TEMPLATE_APPLICABILITY) == set(ObjectiveTemplate)


@pytest.mark.req("FR-MODEL-39")
@pytest.mark.parametrize("template", list(ObjectiveTemplate))
def test_every_template_builds_from_its_own_defaults_where_it_has_them(
    template: ObjectiveTemplate,
) -> None:
    params = {
        parameter.name: parameter.default
        for parameter in TEMPLATE_PARAMETERS[template]
        if parameter.default is not None
    }
    required = [p for p in TEMPLATE_PARAMETERS[template] if p.default is None]
    for parameter in required:
        params[parameter.name] = 100_000 if parameter.kind == "money_minor" else 0.5
    objective = _objective(template, params)  # type: ignore[arg-type]
    assert objective.template is template


@pytest.mark.req("FR-MODEL-39")
def test_a_parameter_the_template_does_not_take_is_refused_by_name() -> None:
    with pytest.raises(pydantic.ValidationError, match="does not take w_overs"):
        _objective(ObjectiveTemplate.ASYMMETRIC_SQUARED, {"w_overs": 2.0})


@pytest.mark.req("FR-MODEL-39")
def test_a_required_parameter_with_no_default_cannot_be_omitted() -> None:
    with pytest.raises(pydantic.ValidationError, match="requires 'delta'"):
        _objective(ObjectiveTemplate.HUBER, {})


@pytest.mark.req("FR-MODEL-39")
def test_a_parameter_outside_its_declared_range_is_refused() -> None:
    """`tweedie.p ∈ (1, 2)` **exclusive** — §4.5 says so, and `p = 2` is Gamma."""
    with pytest.raises(pydantic.ValidationError, match=r"less than 2\.0"):
        _objective(ObjectiveTemplate.TWEEDIE, {"p": 2.0})
    with pytest.raises(pydantic.ValidationError, match=r"greater than 1\.0"):
        _objective(ObjectiveTemplate.TWEEDIE, {"p": 1.0})


@pytest.mark.req("FR-MODEL-39")
def test_a_money_parameter_given_as_a_float_is_refused() -> None:
    """`CLAUDE.md` §7. A cap in pounds beside amounts in pence is wrong by a hundred."""
    with pytest.raises(pydantic.ValidationError, match="integer minor units"):
        _objective(ObjectiveTemplate.CAPPED_GAMMA, {"cap": 25_000.0})
    assert _objective(ObjectiveTemplate.CAPPED_GAMMA, {"cap": 2_500_000}).params["cap"] == 2_500_000


@pytest.mark.req("FR-MODEL-44")
def test_an_author_may_narrow_applicability() -> None:
    template = TEMPLATE_APPLICABILITY[ObjectiveTemplate.HUBER]
    narrowed = Applicability(
        responses=frozenset({ResponseKind.BURNING_COST}),
        backends=frozenset({ObjectiveBackend.XGBOOST}),
        y_domain=YDomain(min_inclusive=0.0, max_inclusive=1e7),
    )
    assert narrowed.is_within(template)
    objective = CustomObjective(
        id=new_uuid7(), slug="robust-bc", version=1, template=ObjectiveTemplate.HUBER,
        params={"delta": 500_000}, applicability=narrowed,
    )
    assert objective.applicability.responses == frozenset({ResponseKind.BURNING_COST})


@pytest.mark.req("FR-MODEL-44")
def test_an_author_may_not_widen_applicability_beyond_the_template() -> None:
    """Gamma's loss is `y/μ + f`. On a count response that is `inf` most rows."""
    wider = Applicability(
        responses=frozenset({ResponseKind.CLAIM_SEVERITY, ResponseKind.CLAIM_COUNT}),
        backends=frozenset({ObjectiveBackend.XGBOOST}),
        y_domain=YDomain(min_exclusive=0.0),
    )
    with pytest.raises(pydantic.ValidationError, match="wider than template"):
        CustomObjective(
            id=new_uuid7(), slug="gamma-everywhere", version=1,
            template=ObjectiveTemplate.GAMMA, applicability=wider,
        )


@pytest.mark.req("FR-MODEL-44")
def test_relaxing_an_exclusive_bound_to_an_inclusive_one_is_a_widening() -> None:
    """`y ≥ 0` admits the one value `y > 0` excludes, and it is the value Gamma diverges at."""
    assert not YDomain(min_inclusive=0.0).is_within(YDomain(min_exclusive=0.0))
    assert YDomain(min_exclusive=0.0).is_within(YDomain(min_inclusive=0.0))


@pytest.mark.req("FR-MODEL-44")
def test_an_applicability_naming_nothing_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="names no responses"):
        Applicability(responses=frozenset(), backends=frozenset({ObjectiveBackend.XGBOOST}))
    with pytest.raises(pydantic.ValidationError, match="names no backends"):
        Applicability(responses=frozenset({ResponseKind.CLAIM_COUNT}), backends=frozenset())


@pytest.mark.req("FR-MODEL-42")
def test_a_status_past_draft_without_a_certificate_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="with no certificate"):
        _objective(status=ObjectiveStatus.CERTIFIED)
    assert _objective(
        status=ObjectiveStatus.CERTIFIED, certificate_id=new_uuid7()
    ).status is ObjectiveStatus.CERTIFIED


@pytest.mark.req("FR-MODEL-42")
def test_an_objective_deprecated_from_draft_needs_no_certificate() -> None:
    """`draft → deprecated` is an edge: an objective abandoned before certification."""
    assert _objective(status=ObjectiveStatus.DEPRECATED).certificate_id is None


@pytest.mark.req("FR-MODEL-46")
def test_the_lifecycle_has_no_edge_that_skips_certification_or_review() -> None:
    assert ObjectiveStatus.APPROVED not in VALID_OBJECTIVE_TRANSITIONS[ObjectiveStatus.DRAFT]
    assert ObjectiveStatus.APPROVED not in VALID_OBJECTIVE_TRANSITIONS[ObjectiveStatus.CERTIFIED]
    assert VALID_OBJECTIVE_TRANSITIONS[ObjectiveStatus.DEPRECATED] == frozenset()


@pytest.mark.req("FR-MODEL-46")
def test_a_review_decision_returns_an_objective_to_certified_not_to_draft() -> None:
    """A review does not withdraw a certificate, so it cannot return one to `draft`.

    The same reasoning `VALID_MODEL_TRANSITIONS` records for `review → fitted`.
    """
    back = VALID_OBJECTIVE_TRANSITIONS[ObjectiveStatus.REVIEW]
    assert ObjectiveStatus.CERTIFIED in back
    assert ObjectiveStatus.DRAFT not in back


@pytest.mark.req("FR-MODEL-42")
def test_a_certificate_verdict_its_checks_contradict_is_refused() -> None:
    checks = (
        CertificateCheck(name="analytic_vs_numeric_gradient", status=CheckStatus.PASS,
                         detail="max relative error 8.9e-7"),
        CertificateCheck(name="finiteness", status=CheckStatus.FAILED,
                         detail="NaN gradient at y=0"),
    )
    with pytest.raises(pydantic.ValidationError, match="cannot be allowed to say different"):
        CertificateResult(
            checks=checks, sampling=SAMPLING, overall=CertificateOutcome.CERTIFIED
        )
    assert CertificateResult(
        checks=checks, sampling=SAMPLING, overall=CertificateOutcome.FAILED
    ).overall is CertificateOutcome.FAILED


@pytest.mark.req("FR-MODEL-43")
def test_a_violated_convexity_check_is_a_finding_and_not_a_failure() -> None:
    """FR-MODEL-43: a non-convex loss is legitimate, flagged, and carried to an approver."""
    checks = (
        CertificateCheck(name="convexity", status=CheckStatus.VIOLATED,
                         detail="hessian < 0 wherever exp(f) < y/2"),
    )
    assert CertificateResult.outcome_of(checks) is CertificateOutcome.CERTIFIED_WITH_FINDINGS


@pytest.mark.req("FR-MODEL-69")
def test_a_check_must_say_what_it_found() -> None:
    """FR-MODEL-69 makes a discontinuity a reported finding; an empty detail reports none."""
    with pytest.raises(pydantic.ValidationError):
        CertificateCheck(name="branch_discontinuity", status=CheckStatus.WARN, detail="")


@pytest.mark.req("FR-MODEL-42")
def test_a_certificate_over_a_coarse_grid_is_refused() -> None:
    """The published contract's floor of 1 000 points, at the type (2026-08-18).

    An empty grid is refused above because every check passes over no points. A grid of
    ten fails the same way more quietly: §4.7's convexity and scale checks report a share
    of sampled points, and a share of ten is a number that looks like evidence.
    """
    with pytest.raises(pydantic.ValidationError, match="greater than or equal to 1000"):
        SamplingSpec(
            n_points=10, seed=1, y_range=(0.0, 1e7), f_range=(-20.0, 20.0),
            w_range=(1e-3, 1e4),
        )


@pytest.mark.req("FR-MODEL-42")
def test_a_certificate_over_an_empty_grid_is_refused() -> None:
    """Every check passes over no points, and the certificate would say `certified`."""
    with pytest.raises(pydantic.ValidationError, match="samples nothing"):
        SamplingSpec(
            n_points=1000, seed=1, y_range=(0.0, 0.0), f_range=(-20.0, 20.0),
            w_range=(1e-3, 1e4),
        )


@pytest.mark.req("FR-MODEL-42")
def test_the_persisted_certificate_pins_the_objective_version_it_certified() -> None:
    certificate = _certificate(_battery())
    assert certificate.objective_version == 3
    assert certificate.result.overall is CertificateOutcome.CERTIFIED


@pytest.mark.req("FR-MODEL-126")
def test_the_full_nine_check_battery_is_accepted() -> None:
    """The positive control for the two refusals below — nine names, each once."""
    certificate = _certificate(_battery())
    assert len(certificate.result.checks) == 9
    assert {check.name for check in certificate.result.checks} == set(
        OBJECTIVE_CERTIFICATE_CHECKS
    )


@pytest.mark.req("FR-MODEL-126")
def test_an_objective_certificate_short_of_its_battery_is_refused() -> None:
    """FR-MODEL-126: a short battery is a failure of the run, not a smaller certificate.

    Before 2026-08-24 this passed. `CertificateResult` carried `min_length=1` and nothing
    above it counted, so a certificate of one check was a well-formed artifact an approver
    would read as §4.7's nine.
    """
    with pytest.raises(pydantic.ValidationError, match="missing"):
        _certificate(_battery(("finiteness",)))


@pytest.mark.req("FR-MODEL-126")
def test_nine_checks_with_one_name_wrong_is_refused() -> None:
    """The count is right and the evidence is not — which is why the *names* are asserted.

    `branch_discontinuity` is dropped and `finiteness` run twice: nine rows, and FR-MODEL-69's
    discontinuity scan never ran.
    """
    names = tuple(
        "finiteness" if name == "branch_discontinuity" else name
        for name in OBJECTIVE_CERTIFICATE_CHECKS
    )
    assert len(names) == 9
    with pytest.raises(pydantic.ValidationError) as raised:
        _certificate(_battery(names))
    assert "branch_discontinuity" in str(raised.value)
    assert "duplicated ['finiteness']" in str(raised.value)


@pytest.mark.req("FR-MODEL-126")
def test_a_check_name_outside_the_battery_is_refused() -> None:
    """A misspelling is not a tenth check; nine names is a closed set."""
    names = (*OBJECTIVE_CERTIFICATE_CHECKS[:8], "smoke_fitt")
    with pytest.raises(pydantic.ValidationError, match=r"unexpected \['smoke_fitt'\]"):
        _certificate(_battery(names))
