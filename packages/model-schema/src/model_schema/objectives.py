"""Custom objectives — the artifact, its template catalogue, and its certificate.

`02` §3.7 (FR-MODEL-38…48, 68…70, 75/76), §4.5 the catalogue, §4.7 the certificate.

**Phase 1 ships `template` objectives only** (FR-MODEL-75, OQ-MODEL-1 decided 2026-08-15).
A template is a parameterised standard loss whose gradient and hessian `pricing-core`
implements analytically; it carries no user code, and the artifact carries no expression.
`ObjectiveKind.EXPRESSION` exists here because `POST /custom-objectives` must be able to
*name* what it is refusing (`OBJECTIVE_KIND_NOT_ENABLED`) — but `CustomObjective` refuses to
be constructed with it, because the fields an expression objective needs (`loss`, the
derived gradient and hessian, the parameter declarations of §4.6) are not built. FR-MODEL-87
forbids declaring a shape and leaving it structurally empty: a null that can never be
anything else teaches that null means *nothing* rather than *not yet*.

Three shapes here are worth reading before using them.

* **The catalogue is data, not code.** `TEMPLATE_PARAMETERS` and `TEMPLATE_APPLICABILITY`
  are what §4.5's table says, in a form both `model-schema` and `pricing-core` read. A
  template whose valid `p` range lived in the fitting code could be persisted invalid and
  fail a phase later, at the fit, where the message is about NumPy.

* **Applicability may be narrowed by the author and never widened.** FR-MODEL-44 makes
  applicability the artifact's declaration, and §4.5 makes it the *template's*. Both are
  true: the template states where its derivatives are valid, and an author may restrict a
  particular objective further. Widening would claim validity `pricing-core` never
  established, so `_applicability_is_within_the_template` refuses it.

* **The certificate splits the way every other computed artifact here splits.**
  `pricing-core` computes a `CertificateResult`; the platform gives it an identity and
  attaches it to an objective version as an `ObjectiveCertificate`. `BacktestSummary` /
  `Backtest` and `ComparisonSummary` / `ModelComparison` are the same split, for ADR-0001's
  reason: `pricing-core` does not allocate ids, read a clock, or know about database rows.
  §4.7 shows the certificate flat, with `custom_objective_id` beside `checks`; it is
  composed here instead, and §4.7 carries a dated note saying so.
"""

from __future__ import annotations

import datetime as _datetime
import enum
from typing import Final, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.modelling import ResponseKind
from model_schema.refs import Slug

__all__ = [
    "FITTABLE_OBJECTIVE_STATUSES",
    "TEMPLATE_APPLICABILITY",
    "TEMPLATE_PARAMETERS",
    "TERMINAL_OBJECTIVE_STATUSES",
    "VALID_OBJECTIVE_TRANSITIONS",
    "Applicability",
    "CertificateCheck",
    "CertificateOutcome",
    "CertificateResult",
    "CheckStatus",
    "CustomObjective",
    "HessianStrategy",
    "ObjectiveBackend",
    "ObjectiveCertificate",
    "ObjectiveKind",
    "ObjectiveStatus",
    "ObjectiveTemplate",
    "SamplingSpec",
    "TemplateParameter",
    "YDomain",
]


class ObjectiveKind(enum.StrEnum):
    """FR-MODEL-38's two kinds. Only `template` is constructible in Phase 1."""

    TEMPLATE = "template"
    #: FR-MODEL-75: Phase 2, behind `expression_objectives_enabled`. Declared so the API can
    #: refuse it by name rather than as a malformed body.
    EXPRESSION = "expression"


class ObjectiveTemplate(enum.StrEnum):
    """§4.5's shipped catalogue — the whole of Phase 1's custom-objective surface."""

    POISSON = "poisson"
    GAMMA = "gamma"
    TWEEDIE = "tweedie"
    CAPPED_GAMMA = "capped_gamma"
    SPLICED_SEVERITY = "spliced_severity"
    ASYMMETRIC_SQUARED = "asymmetric_squared"
    ASYMMETRIC_POISSON = "asymmetric_poisson"
    HUBER = "huber"
    PSEUDO_HUBER = "pseudo_huber"
    QUANTILE = "quantile"
    ZERO_INFLATED_POISSON = "zero_inflated_poisson"
    FOCAL_BINOMIAL = "focal_binomial"


class ObjectiveBackend(enum.StrEnum):
    """FR-MODEL-44's backend vocabulary.

    `glm` is declared and no shipped template names it: a custom objective on the GLM arm
    needs `GlmSpec.custom_objective_ref`, which FR-MODEL-87 records as absent entirely and
    owned by Phase 1b. The member exists because FR-MODEL-44 names it and an author
    narrowing applicability should not be able to name a backend the enum has never heard
    of — not because anything reaches it today.
    """

    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    GLM = "glm"


class HessianStrategy(enum.StrEnum):
    """FR-MODEL-43's three declared treatments of a negative hessian.

    Always declared, never inferred: boosting divides by the hessian, so what happens where
    it is negative decides what the fit *is*, and a default chosen inside the fitting code
    would be a modelling decision made where no reviewer reads it.
    """

    #: `max(h, hessian_min)` — the treatment both backends' own objectives use.
    CLIP_TO_MIN = "clip_to_min"
    #: `|h|` — keeps the step size, discards the direction of the curvature.
    ABS = "abs"
    #: Replace the hessian with its Gauss-Newton approximation, which is non-negative by
    #: construction.
    GAUSS_NEWTON = "gauss_newton"


class ObjectiveStatus(enum.StrEnum):
    """FR-MODEL-46's lifecycle."""

    DRAFT = "draft"
    CERTIFIED = "certified"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


#: FR-MODEL-46's lifecycle as data, following `VALID_MODEL_TRANSITIONS`. Two edges are not
#: in the requirement's arrow chain and are here for stated reasons:
#:
#: * **`certified → draft`.** `POST /{id}/certify` may be run again — after a library
#:   upgrade, or on a wider sampling grid — and a re-run that comes back `failed` must not
#:   leave the objective claiming a certification it no longer has.
#: * **`review → certified`, never `review → draft`.** `06` FR-GOV-13 returns a
#:   `changes_requested` artifact to `draft`; here that would claim the certificate had been
#:   withdrawn, which a review decision does not do. The pre-submission state of a
#:   certified objective is `certified`, exactly as a Model's is `fitted`.
VALID_OBJECTIVE_TRANSITIONS: Final[dict[ObjectiveStatus, frozenset[ObjectiveStatus]]] = {
    ObjectiveStatus.DRAFT: frozenset({ObjectiveStatus.CERTIFIED, ObjectiveStatus.DEPRECATED}),
    ObjectiveStatus.CERTIFIED: frozenset(
        {ObjectiveStatus.REVIEW, ObjectiveStatus.DRAFT, ObjectiveStatus.DEPRECATED}
    ),
    ObjectiveStatus.REVIEW: frozenset({ObjectiveStatus.APPROVED, ObjectiveStatus.CERTIFIED}),
    ObjectiveStatus.APPROVED: frozenset({ObjectiveStatus.DEPRECATED}),
    ObjectiveStatus.DEPRECATED: frozenset(),
}

TERMINAL_OBJECTIVE_STATUSES: Final[frozenset[ObjectiveStatus]] = frozenset(
    {ObjectiveStatus.DEPRECATED}
)

#: The statuses a Model Spec may *fit* with. Not the same set as the one R4 requires for the
#: model to reach `approved` — that is `approved` alone. A `draft` objective has no
#: certificate, so its derivatives are unproven and FR-MODEL-42 has not been satisfied; a
#: `deprecated` one has been withdrawn. Everything between is fittable, and the model that
#: results simply cannot be approved until the objective is.
FITTABLE_OBJECTIVE_STATUSES: Final[frozenset[ObjectiveStatus]] = frozenset(
    {ObjectiveStatus.CERTIFIED, ObjectiveStatus.REVIEW, ObjectiveStatus.APPROVED}
)


class TemplateParameter(BaseModel):
    """One template parameter and the range §4.5 gives it.

    `kind` exists because two of these are **money**. `capped_gamma.cap` and
    `spliced_severity.threshold` are amounts on the response scale, and `CLAUDE.md` §7 makes
    money integer minor units and never a float — a cap that arrives as `25000.0` and is
    compared against integer minor-unit claim amounts is off by a factor of a hundred, and
    nothing about the number says so.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    kind: Literal["float", "money_minor"] = "float"
    minimum: float | None = None
    maximum: float | None = None
    minimum_exclusive: bool = False
    maximum_exclusive: bool = False
    #: `None` means the parameter is required — §4.5 gives no default for a cap or a
    #: threshold, because there is no amount that is right by default.
    default: float | int | None = None

    def check(self, value: float | int) -> None:
        """Raise `ValueError` unless `value` is a valid setting of this parameter.

        One implementation, read by the contract that persists an objective and by the
        `pricing-core` code that compiles one, so a parameter cannot be valid on one side of
        the boundary and invalid on the other.
        """
        if isinstance(value, bool):
            raise ValueError(f"parameter {self.name!r} is {value!r}; a boolean is not a number")
        if self.kind == "money_minor" and not isinstance(value, int):
            raise ValueError(
                f"parameter {self.name!r} is money and must be integer minor units, not "
                f"{value!r} (`CLAUDE.md` §7)."
            )
        low, high = self.minimum, self.maximum
        if low is not None and (value <= low if self.minimum_exclusive else value < low):
            edge = "greater than" if self.minimum_exclusive else "at least"
            raise ValueError(f"parameter {self.name!r} is {value!r}; it must be {edge} {low}")
        if high is not None and (value >= high if self.maximum_exclusive else value > high):
            edge = "less than" if self.maximum_exclusive else "at most"
            raise ValueError(f"parameter {self.name!r} is {value!r}; it must be {edge} {high}")


class YDomain(BaseModel):
    """The valid range of the response for an objective (FR-MODEL-44).

    §4.6's example writes `{"min_inclusive": 0}`; the exclusive bounds are added here
    because the Gamma family needs `y > 0` and an inclusive zero is the one value at which
    its loss is undefined. At most one bound per side.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    min_inclusive: float | None = None
    min_exclusive: float | None = None
    max_inclusive: float | None = None
    max_exclusive: float | None = None

    @model_validator(mode="after")
    def _one_bound_per_side(self) -> Self:
        if self.min_inclusive is not None and self.min_exclusive is not None:
            raise ValueError("y_domain declares both min_inclusive and min_exclusive")
        if self.max_inclusive is not None and self.max_exclusive is not None:
            raise ValueError("y_domain declares both max_inclusive and max_exclusive")
        return self

    @property
    def lower(self) -> float | None:
        """The lower bound, whichever kind it is — for range checks that ignore the edge."""
        return self.min_inclusive if self.min_inclusive is not None else self.min_exclusive

    @property
    def upper(self) -> float | None:
        return self.max_inclusive if self.max_inclusive is not None else self.max_exclusive

    def contains(self, value: float) -> bool:
        if self.min_inclusive is not None and value < self.min_inclusive:
            return False
        if self.min_exclusive is not None and value <= self.min_exclusive:
            return False
        if self.max_inclusive is not None and value > self.max_inclusive:
            return False
        return not (self.max_exclusive is not None and value >= self.max_exclusive)

    def is_within(self, other: YDomain) -> bool:
        """Is every `y` this domain admits also admitted by `other`?

        Used by `CustomObjective` to refuse an author who widened the template's domain. A
        missing bound is unbounded, so `other` having one where this has none is a
        narrowing that fails.
        """
        if other.lower is not None and (self.lower is None or self.lower < other.lower):
            return False
        if (
            other.min_exclusive is not None
            and self.min_exclusive is None
            and self.lower == other.lower
        ):
            return False
        if other.upper is not None and (self.upper is None or self.upper > other.upper):
            return False
        return not (
            other.max_exclusive is not None
            and self.max_exclusive is None
            and self.upper == other.upper
        )


class Applicability(BaseModel):
    """Where an objective may be used (FR-MODEL-44).

    A Model Spec pairing an objective with a response outside `responses`, a backend outside
    `backends`, or no offset where one is required, is refused **at spec validation** —
    before any compute is spent, and with a `SpecProblem` naming which of the three it was.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    responses: frozenset[ResponseKind]
    backends: frozenset[ObjectiveBackend]
    #: `true` where the loss is a rate and the exposure rides in `base_margin`. A Poisson
    #: objective fitted without one silently models claims per record.
    offset_required: bool = False
    y_domain: YDomain = YDomain()

    @model_validator(mode="after")
    def _an_objective_applies_somewhere(self) -> Self:
        if not self.responses:
            raise ValueError("applicability names no responses, so nothing may use it")
        if not self.backends:
            raise ValueError("applicability names no backends, so nothing may fit it")
        return self

    def is_within(self, template: Applicability) -> bool:
        """Is this declaration no wider than the template's? See the module docstring."""
        return (
            self.responses <= template.responses
            and self.backends <= template.backends
            and self.offset_required >= template.offset_required
            and self.y_domain.is_within(template.y_domain)
        )


_GBM: Final[frozenset[ObjectiveBackend]] = frozenset(
    {ObjectiveBackend.XGBOOST, ObjectiveBackend.LIGHTGBM}
)
_NON_NEGATIVE: Final[YDomain] = YDomain(min_inclusive=0.0)
_POSITIVE: Final[YDomain] = YDomain(min_exclusive=0.0)

#: §4.5's `Params` column, with the validity ranges the same section requires each template
#: to declare. Read by `CustomObjective` when it validates `params`, and by `pricing-core`
#: when it compiles one — one table, so a `p` the artifact accepts is a `p` the derivative
#: was written for.
TEMPLATE_PARAMETERS: Final[dict[ObjectiveTemplate, tuple[TemplateParameter, ...]]] = {
    ObjectiveTemplate.POISSON: (),
    ObjectiveTemplate.GAMMA: (),
    ObjectiveTemplate.TWEEDIE: (
        TemplateParameter(
            name="p", minimum=1.0, maximum=2.0,
            minimum_exclusive=True, maximum_exclusive=True, default=1.5,
        ),
    ),
    ObjectiveTemplate.CAPPED_GAMMA: (
        TemplateParameter(name="cap", kind="money_minor", minimum=0.0, minimum_exclusive=True),
    ),
    ObjectiveTemplate.SPLICED_SEVERITY: (
        TemplateParameter(
            name="threshold", kind="money_minor", minimum=0.0, minimum_exclusive=True
        ),
        TemplateParameter(name="tail_shape", minimum=0.0, minimum_exclusive=True, default=1.5),
    ),
    ObjectiveTemplate.ASYMMETRIC_SQUARED: (
        TemplateParameter(name="w_under", minimum=0.0, minimum_exclusive=True, default=2.0),
        TemplateParameter(name="w_over", minimum=0.0, minimum_exclusive=True, default=1.0),
    ),
    ObjectiveTemplate.ASYMMETRIC_POISSON: (
        TemplateParameter(name="w_under", minimum=0.0, minimum_exclusive=True, default=2.0),
        TemplateParameter(name="w_over", minimum=0.0, minimum_exclusive=True, default=1.0),
    ),
    ObjectiveTemplate.HUBER: (
        TemplateParameter(name="delta", kind="money_minor", minimum=0.0, minimum_exclusive=True),
    ),
    ObjectiveTemplate.PSEUDO_HUBER: (
        TemplateParameter(name="delta", kind="money_minor", minimum=0.0, minimum_exclusive=True),
    ),
    ObjectiveTemplate.QUANTILE: (
        TemplateParameter(
            name="alpha", minimum=0.0, maximum=1.0,
            minimum_exclusive=True, maximum_exclusive=True, default=0.5,
        ),
    ),
    ObjectiveTemplate.ZERO_INFLATED_POISSON: (
        TemplateParameter(
            name="pi", minimum=0.0, maximum=1.0, minimum_exclusive=True, maximum_exclusive=True
        ),
    ),
    ObjectiveTemplate.FOCAL_BINOMIAL: (
        TemplateParameter(name="gamma", minimum=0.0, default=2.0),
    ),
}

#: §4.5's "each template declares its `applicability` block". The template states where its
#: analytic derivatives are valid; an author may narrow this for a particular objective and
#: may not widen it.
TEMPLATE_APPLICABILITY: Final[dict[ObjectiveTemplate, Applicability]] = {
    ObjectiveTemplate.POISSON: Applicability(
        responses=frozenset({ResponseKind.CLAIM_COUNT}), backends=_GBM,
        offset_required=True, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.GAMMA: Applicability(
        responses=frozenset({ResponseKind.CLAIM_SEVERITY}), backends=_GBM, y_domain=_POSITIVE,
    ),
    ObjectiveTemplate.TWEEDIE: Applicability(
        responses=frozenset({ResponseKind.BURNING_COST}), backends=_GBM,
        offset_required=True, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.CAPPED_GAMMA: Applicability(
        responses=frozenset({ResponseKind.CLAIM_SEVERITY}), backends=_GBM, y_domain=_POSITIVE,
    ),
    ObjectiveTemplate.SPLICED_SEVERITY: Applicability(
        responses=frozenset({ResponseKind.CLAIM_SEVERITY}), backends=_GBM, y_domain=_POSITIVE,
    ),
    ObjectiveTemplate.ASYMMETRIC_SQUARED: Applicability(
        responses=frozenset({ResponseKind.BURNING_COST, ResponseKind.CLAIM_SEVERITY}),
        backends=_GBM, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.ASYMMETRIC_POISSON: Applicability(
        responses=frozenset({ResponseKind.CLAIM_COUNT}), backends=_GBM,
        offset_required=True, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.HUBER: Applicability(
        responses=frozenset({ResponseKind.BURNING_COST, ResponseKind.CLAIM_SEVERITY}),
        backends=_GBM, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.PSEUDO_HUBER: Applicability(
        responses=frozenset({ResponseKind.BURNING_COST, ResponseKind.CLAIM_SEVERITY}),
        backends=_GBM, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.QUANTILE: Applicability(
        responses=frozenset(
            {ResponseKind.BURNING_COST, ResponseKind.CLAIM_SEVERITY, ResponseKind.CLAIM_COUNT}
        ),
        backends=_GBM, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.ZERO_INFLATED_POISSON: Applicability(
        responses=frozenset({ResponseKind.CLAIM_COUNT}), backends=_GBM,
        offset_required=True, y_domain=_NON_NEGATIVE,
    ),
    ObjectiveTemplate.FOCAL_BINOMIAL: Applicability(
        responses=frozenset({ResponseKind.CONVERSION, ResponseKind.RETENTION}),
        backends=_GBM, y_domain=YDomain(min_inclusive=0.0, max_inclusive=1.0),
    ),
}


class CustomObjective(BaseModel):
    """A named, versioned, reusable objective (FR-MODEL-38, §4.5).

    Versioned rather than edited: FR-MODEL-46 makes editing an approved objective a new
    version requiring fresh certification, and a Model referencing
    `custom_objective:<slug>@<version>` must keep meaning the loss it was fitted under.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: Slug
    version: int = Field(ge=1)
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE
    template: ObjectiveTemplate | None = None
    params: dict[str, int | float] = Field(default_factory=dict)
    applicability: Applicability
    hessian_strategy: HessianStrategy = HessianStrategy.CLIP_TO_MIN
    #: The floor `clip_to_min` clips to, and the minimum both backends need to avoid a
    #: divide-by-zero step. Positive: a zero floor is not a floor.
    hessian_min: float = Field(default=1e-6, gt=0.0)
    status: ObjectiveStatus = ObjectiveStatus.DRAFT
    description: str | None = None
    #: The certificate this objective's current status rests on (FR-MODEL-42). Set when a
    #: certification run comes back anything but `failed`, and enforced below: a status past
    #: `draft` without one would be a claim with no evidence behind it.
    certificate_id: UUID | None = None
    #: The open approval request, set when the objective enters `review` and left in place
    #: afterwards — the trail from an approved objective to the decision behind it.
    approval_request_id: UUID | None = None

    @model_validator(mode="after")
    def _only_templates_are_built(self) -> Self:
        """FR-MODEL-75, at the type.

        The API refuses `kind: expression` with `OBJECTIVE_KIND_NOT_ENABLED` before it gets
        here; this is the second door, so that no other caller — a fixture, a migration, a
        service constructing an artifact directly — can persist an objective whose loss is
        nowhere written down.
        """
        if self.kind is not ObjectiveKind.TEMPLATE:
            raise ValueError(
                f"custom objective {self.slug}@{self.version} is kind {self.kind.value!r}. "
                "Phase 1 ships templates only (FR-MODEL-75); the fields an expression "
                "objective needs are not built, so the artifact would carry no loss."
            )
        if self.template is None:
            raise ValueError(
                f"custom objective {self.slug}@{self.version} is a template objective and "
                "names no template."
            )
        return self

    @model_validator(mode="after")
    def _the_parameters_are_the_templates_own(self) -> Self:
        """Exactly §4.5's parameters for this template, each inside its declared range.

        Both halves matter. An unknown key is almost always a misspelling of a real one —
        `w_over` written `w_overs` leaves the real parameter at its default and the loss
        asymmetric in the wrong direction, which fits, converges and prices wrongly. A
        missing key with no default is a template that cannot be evaluated at all.
        """
        if self.template is None:  # pragma: no cover — the validator above has refused it
            return self
        declared = {parameter.name: parameter for parameter in TEMPLATE_PARAMETERS[self.template]}
        unknown = sorted(set(self.params) - set(declared))
        if unknown:
            raise ValueError(
                f"template {self.template.value!r} does not take {', '.join(unknown)} "
                f"(§4.5 gives it {', '.join(declared) or 'no parameters'})."
            )
        for name, parameter in declared.items():
            if name not in self.params:
                if parameter.default is None:
                    raise ValueError(
                        f"template {self.template.value!r} requires {name!r} and it is "
                        "missing; §4.5 gives it no default."
                    )
                continue
            parameter.check(self.params[name])
        return self

    @model_validator(mode="after")
    def _applicability_is_within_the_template(self) -> Self:
        """An author may narrow §4.5's applicability and may not widen it.

        Widening claims the analytic derivatives are valid somewhere `pricing-core` never
        established — a Gamma loss declared applicable to `claim_count` is `y/μ + f` on a
        response that is zero most of the time, which is `inf`.
        """
        if self.template is None:  # pragma: no cover — refused above
            return self
        if not self.applicability.is_within(TEMPLATE_APPLICABILITY[self.template]):
            raise ValueError(
                f"custom objective {self.slug}@{self.version} declares an applicability "
                f"wider than template {self.template.value!r}'s (§4.5, FR-MODEL-44). An "
                "objective may be restricted further than its template and never extended "
                "beyond it."
            )
        return self

    @model_validator(mode="after")
    def _a_status_past_draft_rests_on_a_certificate(self) -> Self:
        """FR-MODEL-42: certification is the condition of leaving `draft`.

        `deprecated` is excluded with `draft` because it is reachable from `draft` — an
        objective abandoned before it was ever certified is withdrawn, not certified.
        """
        past_draft = self.status not in {ObjectiveStatus.DRAFT, ObjectiveStatus.DEPRECATED}
        if past_draft and self.certificate_id is None:
            raise ValueError(
                f"custom objective {self.slug}@{self.version} is {self.status.value} with no "
                "certificate (FR-MODEL-42). Certification is what `certified` means, and "
                "submission requires it."
            )
        return self


class CheckStatus(enum.StrEnum):
    """One certificate check's verdict.

    §4.7's example shows `pass`, `warn` and `violated`. `failed` is the fourth, and the
    distinction it draws is the one FR-MODEL-43 turns on: `violated` is a *stated property
    breach the platform tolerates with a declared mitigation* — a non-convex loss is a
    legitimate pricing loss — where `failed` is a check that cannot pass at all, and an
    objective whose derivatives disagree with the numeric ones is not usable at any
    approval level. `02` §4.7 carries a dated note adding it to the vocabulary.
    """

    PASS = "pass"
    WARN = "warn"
    VIOLATED = "violated"
    FAILED = "failed"


class CertificateOutcome(enum.StrEnum):
    """§4.7's `overall`. A `failed` certificate blocks submission entirely (FR-MODEL-42)."""

    CERTIFIED = "certified"
    CERTIFIED_WITH_FINDINGS = "certified_with_findings"
    FAILED = "failed"


class CertificateCheck(BaseModel):
    """One named check and what it found.

    `detail` is prose and is required — FR-MODEL-69 makes a branch discontinuity a
    *reported finding* rather than an exclusion, and a `warn` with no sentence beside it is
    exactly the finding nobody acts on.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    status: CheckStatus
    detail: str = Field(min_length=1)


class SamplingSpec(BaseModel):
    """The grid the checks ran over (§4.7).

    Part of the certificate rather than a run parameter thrown away afterwards: §4.7's own
    note says the convexity share "is strongly dependent on `y_range`/`f_range`, so the
    share is only meaningful alongside the sampling block". A finding without its grid is
    a percentage of nothing.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    n_points: int = Field(ge=1)
    seed: int
    y_range: tuple[float, float]
    f_range: tuple[float, float]
    w_range: tuple[float, float]

    @model_validator(mode="after")
    def _every_range_is_ordered_and_non_empty(self) -> Self:
        for name, (low, high) in (
            ("y_range", self.y_range),
            ("f_range", self.f_range),
            ("w_range", self.w_range),
        ):
            if low >= high:
                raise ValueError(
                    f"{name} is [{low}, {high}], which samples nothing. A certificate over "
                    "an empty grid passes every check."
                )
        return self


class CertificateResult(BaseModel):
    """What certification found, before the platform gives it an identity (ADR-0001).

    `overall` is **derived from the checks and enforced**, not asserted: a certificate whose
    verdict its own checks contradict is the one artifact in this module that must be
    impossible, since submission reads the verdict and an approver reads the checks.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    checks: tuple[CertificateCheck, ...] = Field(min_length=1)
    sampling: SamplingSpec
    overall: CertificateOutcome
    #: Every library whose version changes the numbers above (§4.7). A certificate that does
    #: not say which XGBoost produced its smoke fit cannot be re-run.
    library_versions: dict[str, str] = Field(default_factory=dict)

    @staticmethod
    def outcome_of(checks: tuple[CertificateCheck, ...]) -> CertificateOutcome:
        """The verdict these checks imply — the one place the rule is written.

        Any `failed` fails the certificate. Any `warn` or `violated` is a finding, and
        FR-MODEL-43 makes a `violated` convexity check something an approver must see rather
        than something that blocks: `certified_with_findings` is what carries it to them.
        """
        statuses = {check.status for check in checks}
        if CheckStatus.FAILED in statuses:
            return CertificateOutcome.FAILED
        if statuses & {CheckStatus.WARN, CheckStatus.VIOLATED}:
            return CertificateOutcome.CERTIFIED_WITH_FINDINGS
        return CertificateOutcome.CERTIFIED

    @model_validator(mode="after")
    def _the_verdict_is_the_one_the_checks_imply(self) -> Self:
        implied = self.outcome_of(self.checks)
        if self.overall is not implied:
            raise ValueError(
                f"certificate reports overall={self.overall.value!r} over checks implying "
                f"{implied.value!r}. Submission reads the verdict and an approver reads the "
                "checks; they cannot be allowed to say different things."
            )
        return self


class ObjectiveCertificate(BaseModel):
    """The persisted certificate (§4.7, FR-MODEL-42).

    Immutable, for the reason `Backtest` is: it is what an approval argues from, and
    evidence that can change after the decision is not evidence. Attached to one objective
    *version* — re-certifying produces another row rather than editing this one, so the
    history of what was believed when survives a library upgrade.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    custom_objective_id: UUID
    objective_version: int = Field(ge=1)
    certified_at: _datetime.datetime
    job_id: UUID | None = None
    result: CertificateResult
