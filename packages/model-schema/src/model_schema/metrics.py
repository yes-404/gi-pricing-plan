"""Custom eval metrics — FR-154, FR-155/156/157, `02` §4.13.

Parallel to `CustomObjective` and deliberately not the same class: the two share a
catalogue and a lifecycle, but a metric is never differentiated, so `hessian_strategy` and
`hessian_min` would be fields meaningful for only one of two uses.

`direction` reuses `model_schema.comparison.MetricDirection` rather than a second enum with
the same two members: that enum's own docstring already declares the concept FR-156
needs — "which way is better, declared with the metric rather than assumed by the reader" —
and duplicating it under a second name would only reintroduce the ambiguity `CLAUDE.md` §2
warns a shape defined twice creates. `CustomMetric` refuses the two members comparison
needs that an early-stopping loop cannot use: see `_direction_is_usable_for_stopping`.
"""

from __future__ import annotations

import datetime as _datetime
import enum
from typing import Final, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.comparison import MetricDirection
from model_schema.objectives import (
    TEMPLATE_APPLICABILITY,
    TEMPLATE_PARAMETERS,
    Applicability,
    CertificateResult,
    ObjectiveKind,
    ObjectiveTemplate,
    battery_is_exactly,
)
from model_schema.refs import Slug

__all__ = [
    "FITTABLE_METRIC_STATUSES",
    "METRIC_CERTIFICATE_CHECKS",
    "TERMINAL_METRIC_STATUSES",
    "VALID_METRIC_TRANSITIONS",
    "CustomMetric",
    "MetricCertificate",
    "MetricDirection",
    "MetricStatus",
]


class MetricStatus(enum.StrEnum):
    """FR-154's "same lifecycle as objectives"."""

    DRAFT = "draft"
    CERTIFIED = "certified"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


#: The same two non-arrow edges `VALID_OBJECTIVE_TRANSITIONS` carries, for the same reasons:
#: re-certification must be able to withdraw a claim, and a review decision does not
#: withdraw a certificate.
VALID_METRIC_TRANSITIONS: Final[dict[MetricStatus, frozenset[MetricStatus]]] = {
    MetricStatus.DRAFT: frozenset({MetricStatus.CERTIFIED, MetricStatus.DEPRECATED}),
    MetricStatus.CERTIFIED: frozenset(
        {MetricStatus.REVIEW, MetricStatus.DRAFT, MetricStatus.DEPRECATED}
    ),
    MetricStatus.REVIEW: frozenset({MetricStatus.APPROVED, MetricStatus.CERTIFIED}),
    MetricStatus.APPROVED: frozenset({MetricStatus.DEPRECATED}),
    MetricStatus.DEPRECATED: frozenset(),
}

TERMINAL_METRIC_STATUSES: Final[frozenset[MetricStatus]] = frozenset({MetricStatus.DEPRECATED})

#: A `draft` metric has no certificate, so `direction_holds` is unproven and early stopping
#: would rest on an unchecked claim. A `deprecated` one has been withdrawn.
FITTABLE_METRIC_STATUSES: Final[frozenset[MetricStatus]] = frozenset(
    {MetricStatus.CERTIFIED, MetricStatus.REVIEW, MetricStatus.APPROVED}
)


class CustomMetric(BaseModel):
    """A named, versioned, reusable eval metric (FR-154, §4.13)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: Slug
    version: int = Field(ge=1)
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE
    template: ObjectiveTemplate | None = None
    params: dict[str, int | float] = Field(default_factory=dict)
    applicability: Applicability
    #: FR-156: required, because there is no safe default. `comparison.MetricDirection`
    #: is reused rather than restated; `_direction_is_usable_for_stopping` refuses the two
    #: members (`closer_to_one_is_better`, `not_ordered`) an early-stopping loop cannot use.
    direction: MetricDirection
    status: MetricStatus = MetricStatus.DRAFT
    description: str | None = None
    certificate_id: UUID | None = None
    approval_request_id: UUID | None = None

    #: How many Model Specs reference this metric version (FR-167) — the library
    #: row's count, and `CustomObjective.usage_count`'s field exactly: **derived per request
    #: and stored on no row**. A stored counter would be a second answer to FR-162's
    #: blast radius, free to disagree with the query that derives it.
    #:
    #: `None` and `0` are different facts and are reported differently. The list route
    #: computes one aggregate per page and supplies `0` for a metric nothing references;
    #: every other route leaves this `None`, meaning *not asked*, because a `0` there would
    #: read as "nothing uses this" on a page that never counted.
    usage_count: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _only_templates_are_built(self) -> Self:
        """FR-150's rule, at the type — the second door behind the API's refusal."""
        if self.kind is not ObjectiveKind.TEMPLATE or self.template is None:
            raise ValueError(
                "Phase 1 admits only `kind: template` metrics, and a template metric needs "
                "a `template` (FR-155)."
            )
        return self

    @model_validator(mode="after")
    def _the_parameters_are_the_templates_own(self) -> Self:
        """Exactly §4.5's parameters for this template, each inside its declared range.

        Both halves matter, and this carried only the first until 2026-08-20. An unknown
        key that is silently ignored produces an uncapped metric under a name that says
        capped, and nothing downstream can tell. A missing key with no default is a
        template that **cannot be evaluated at all** — `POST /api/v1/custom-metrics`
        returned 201 for a `capped_gamma` metric with no `cap`, and certification then
        died on a bare `KeyError` naming nothing, where `CustomObjective` had refused the
        same input at construction (`objectives.py`'s sibling validator).
        """
        if self.template is None:  # pragma: no cover — the validator above ran first
            return self
        declared = {p.name: p for p in TEMPLATE_PARAMETERS[self.template]}
        unknown = sorted(set(self.params) - set(declared))
        if unknown:
            raise ValueError(
                f"metric params {unknown} are not parameters of template "
                f"{self.template.value!r}; it declares {sorted(declared)} (FR-155)."
            )
        for name, parameter in declared.items():
            if name not in self.params:
                if parameter.default is None:
                    raise ValueError(
                        f"template {self.template.value!r} requires {name!r} and it is "
                        "missing; §4.5 gives it no default (FR-155)."
                    )
                continue
            parameter.check(self.params[name])
        return self

    @model_validator(mode="after")
    def _applicability_is_within_the_template(self) -> Self:
        """An author may narrow §4.5's applicability and may not widen it.

        Widening claims the analytic loss is valid somewhere `pricing-core` never
        established for it — a `capped_gamma` metric declared applicable to `claim_count`
        evaluates a Gamma loss, `y/μ + f`, on a response that is zero most of the time,
        which is `inf`. `evaluate_metric` (Task 3) computes exactly that loss, and Task 6's
        applicability check compares a metric against the *model spec* it is attached to —
        it never checks the metric against its own template, so this is the only place a
        widened claim is caught before it reaches a fit.
        """
        if self.template is None:  # pragma: no cover — refused above
            return self
        if not self.applicability.is_within(TEMPLATE_APPLICABILITY[self.template]):
            raise ValueError(
                f"metric {self.slug}@{self.version} declares an applicability wider than "
                f"template {self.template.value!r}'s (§4.5, FR-155). A metric may be "
                "restricted further than its template and never extended beyond it."
            )
        return self

    @model_validator(mode="after")
    def _direction_is_usable_for_stopping(self) -> Self:
        """FR-156 — only the two members an early-stopping loop can compare.

        Early stopping compares successive values and halts when they stop improving.
        `not_ordered` has no "better" to compare at all — it exists for context values like
        a holdout row count, not a score. `closer_to_one_is_better` is not the monotone
        comparison a backend's early-stopping loop can consume either: neither "lower" nor
        "higher" is always the improving direction for it, and a loop that only knows how
        to compare two floats one way cannot be handed a target to converge toward.
        """
        refused = {MetricDirection.CLOSER_TO_ONE_IS_BETTER, MetricDirection.NOT_ORDERED}
        if self.direction in refused:
            raise ValueError(
                f"metric direction {self.direction.value!r} is not usable for early "
                "stopping (FR-156); only lower_is_better and higher_is_better compare "
                "successive values monotonically."
            )
        return self

    @model_validator(mode="after")
    def _a_status_past_draft_rests_on_a_certificate(self) -> Self:
        """FR-157 — a claim with no evidence behind it is refused at the type.

        `deprecated` is excluded alongside `draft` because it is reachable from `draft`
        (`VALID_METRIC_TRANSITIONS[MetricStatus.DRAFT]` includes it): a metric abandoned
        before it was ever certified is withdrawn, not certified, and withdrawing it must
        not require inventing a certificate for a metric nobody ever ran. Mirrors
        `CustomObjective._a_status_past_draft_rests_on_a_certificate` (`objectives.py`).
        """
        past_draft = self.status not in {MetricStatus.DRAFT, MetricStatus.DEPRECATED}
        if past_draft and self.certificate_id is None:
            raise ValueError(
                f"metric status {self.status.value!r} without a certificate_id; every "
                "status past `draft` (other than `deprecated` reached directly from it) "
                "rests on one (FR-157)."
            )
        return self


#: FR-157's four metric checks, sharing §4.7's vocabulary unchanged and in the order
#: `pricing_core.modelling.metrics.certify_metric` emits them. Four, not §4.7's nine: a
#: metric is never differentiated, so the two derivative checks, convexity, the branch scan
#: and the shape pair have nothing to run against — which is why FR-158 puts the count
#: on the artifact rather than on the shared `CertificateResult`.
METRIC_CERTIFICATE_CHECKS: Final[tuple[str, ...]] = (
    "finiteness",
    "direction_holds",
    "scale_behaviour",
    "smoke_evaluation",
)


class MetricCertificate(BaseModel):
    """The identity around `CertificateResult` — the ADR-703 split §4.7 already uses."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    custom_metric_id: UUID
    metric_version: int = Field(ge=1)
    certified_at: _datetime.datetime
    job_id: UUID | None = None
    result: CertificateResult

    @model_validator(mode="after")
    def _the_battery_is_all_four_named_checks(self) -> Self:
        """FR-157's four, enforced here for FR-158's reason.

        The names are asserted rather than the count: `direction_holds` is the check that
        catches a `direction` declared backwards, and a certificate missing it while
        carrying `finiteness` twice is four checks long and proves nothing about direction.
        """
        battery_is_exactly(
            self.result.checks, METRIC_CERTIFICATE_CHECKS, artifact="metric certificate"
        )
        return self
