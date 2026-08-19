"""Custom eval metrics — FR-MODEL-45, FR-MODEL-103/104/105, `02` §4.13.

Parallel to `CustomObjective` and deliberately not the same class: the two share a
catalogue and a lifecycle, but a metric is never differentiated, so `hessian_strategy` and
`hessian_min` would be fields meaningful for only one of two uses.
"""

from __future__ import annotations

import enum
from typing import Final, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.objectives import (
    TEMPLATE_PARAMETERS,
    Applicability,
    CertificateResult,
    ObjectiveKind,
    ObjectiveTemplate,
)
from model_schema.refs import Slug

__all__ = [
    "FITTABLE_METRIC_STATUSES",
    "TERMINAL_METRIC_STATUSES",
    "VALID_METRIC_TRANSITIONS",
    "CustomMetric",
    "MetricCertificate",
    "MetricDirection",
    "MetricStatus",
]


class MetricDirection(enum.StrEnum):
    """FR-MODEL-104. Declared, never inferred.

    Early stopping compares successive values and halts when they stop improving; which
    comparison "improving" is cannot be read off the arithmetic. A metric whose direction
    is guessed stops at the wrong round in half of cases, and returns a fitted model rather
    than an error — the failure that leaves no trace.
    """

    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class MetricStatus(enum.StrEnum):
    """FR-MODEL-45's "same lifecycle as objectives"."""

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
    """A named, versioned, reusable eval metric (FR-MODEL-45, §4.13)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: Slug
    version: int = Field(ge=1)
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE
    template: ObjectiveTemplate | None = None
    params: dict[str, int | float] = Field(default_factory=dict)
    applicability: Applicability
    #: FR-MODEL-104: required, because there is no safe default.
    direction: MetricDirection
    status: MetricStatus = MetricStatus.DRAFT
    description: str | None = None
    certificate_id: UUID | None = None
    approval_request_id: UUID | None = None

    @model_validator(mode="after")
    def _only_templates_are_built(self) -> Self:
        """FR-MODEL-75's rule, at the type — the second door behind the API's refusal."""
        if self.kind is not ObjectiveKind.TEMPLATE or self.template is None:
            raise ValueError(
                "Phase 1 admits only `kind: template` metrics, and a template metric needs "
                "a `template` (FR-MODEL-103)."
            )
        return self

    @model_validator(mode="after")
    def _the_parameters_are_the_templates_own(self) -> Self:
        """An unknown key is refused, never dropped.

        A misspelled `cap` that is silently ignored produces an uncapped metric under a
        name that says capped — and nothing downstream can tell.
        """
        if self.template is None:  # pragma: no cover — the validator above ran first
            return self
        declared = {p.name: p for p in TEMPLATE_PARAMETERS[self.template]}
        unknown = sorted(set(self.params) - set(declared))
        if unknown:
            raise ValueError(
                f"metric params {unknown} are not parameters of template "
                f"{self.template.value!r}; it declares {sorted(declared)} (FR-MODEL-103)."
            )
        for name, parameter in declared.items():
            if name in self.params:
                parameter.check(self.params[name])
        return self

    @model_validator(mode="after")
    def _a_status_past_draft_rests_on_a_certificate(self) -> Self:
        """FR-MODEL-105 — a claim with no evidence behind it is refused at the type."""
        if self.status is not MetricStatus.DRAFT and self.certificate_id is None:
            raise ValueError(
                f"metric status {self.status.value!r} without a certificate_id; every "
                "status past `draft` rests on one (FR-MODEL-105)."
            )
        return self


class MetricCertificate(BaseModel):
    """The identity around `CertificateResult` — the ADR-0001 split §4.7 already uses."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    custom_metric_id: UUID
    metric_version: int = Field(ge=1)
    certified_at: str
    job_id: UUID | None = None
    result: CertificateResult
