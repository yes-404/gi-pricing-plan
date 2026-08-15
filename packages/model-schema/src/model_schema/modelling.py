"""Modelling shapes: Factors, Model Specs, and what a fit returns (`02` §4).

Only the GLM spine lives here so far — `02` §4.4's tagged union has four arms and this
carries `glm`. The rest arrives with the workstream slice that implements it, because a
declared arm nothing can produce is a shape that will be wrong by the time anything does.

**Two rules from `02` §1.3 are structural rather than checked at the edges:**

* **R2 — a Model is immutable once fitted.** `frozen=True` everywhere, and refitting
  produces a new version with `parent_model_id` set. There is no operation that edits a
  coefficient, and none should be addable without noticing.
* **R5 — every estimate carries uncertainty.** `Coefficient` cannot be constructed without
  a standard error and an interval. A point estimate on its own is not a result here; it is
  half of one, and the half that reads as more certain than it is.

ADR-0003 is why `fit_result` is data rather than a pickled estimator: a Model must be
re-scorable without `glum`, by a process that never ran it.
"""

from __future__ import annotations

import enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "Coefficient",
    "Factor",
    "FactorIntent",
    "FactorType",
    "GlmFitResult",
    "GlmSpec",
    "Model",
    "ModelStatus",
    "MonotonicDirection",
    "OffsetSpec",
    "RelativityLevel",
    "WeightSpec",
]


class FactorType(enum.StrEnum):
    """`02` FR-MODEL-1's closed set. No other types exist without a spec change."""

    IDENTITY = "identity"
    BANDING = "banding"
    GROUPING = "grouping"
    INTERACTION = "interaction"
    SPLINE = "spline"
    POLYNOMIAL = "polynomial"
    OFFSET = "offset"
    EXPRESSION = "expression"


class FactorIntent(enum.StrEnum):
    """What a factor is *for* (FR-MODEL-3).

    `control` is the load-bearing one: a variable present to absorb variance but never to
    be rated on — year of account is the standard example. `03` refuses a `control` factor
    reaching a rate table, which only works because the intent is declared here rather than
    inferred later from a name.
    """

    RISK = "risk"
    CONTROL = "control"
    OFFSET = "offset"
    DIAGNOSTIC = "diagnostic"


class MonotonicDirection(enum.StrEnum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    NONE = "none"


class Factor(BaseModel):
    """A named, versioned transformation over dataset columns (FR-MODEL-1, FR-MODEL-7).

    Defined against a **Dataset**, resolved against a specific **version** at fit time
    (FR-MODEL-2) — so a factor outlives the version it was first used on, and a column that
    changed dtype fails loudly at resolution rather than quietly changing the model.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    dataset_id: UUID
    version: int = Field(ge=1)
    type: FactorType
    source_columns: tuple[str, ...] = Field(min_length=1)
    intent: FactorIntent = FactorIntent.RISK
    monotonic_direction: MonotonicDirection = MonotonicDirection.NONE
    monotonic_rationale: str | None = None
    #: FR-MODEL-5. A prohibited factor cannot enter any Model Spec; the attempt is refused
    #: and audited. The reason is required with the flag — "prohibited because someone once
    #: said so" is the state this field exists to prevent.
    prohibited: bool = False
    prohibited_reason: str | None = None
    #: The level relativities are expressed against. Null until the fit picks one, because
    #: `largest_exposure` cannot be known without the data (FR-MODEL-21).
    base_level: str | None = None
    base_level_method: str = "largest_exposure"

    @model_validator(mode="after")
    def _reasons_accompany_their_flags(self) -> Factor:
        if self.prohibited and not (self.prohibited_reason or "").strip():
            raise ValueError(
                f"factor {self.slug!r} is prohibited with no reason. FR-MODEL-5 requires "
                "one: a prohibition nobody can explain is one nobody can lift."
            )
        if self.monotonic_direction is not MonotonicDirection.NONE and not (
            self.monotonic_rationale or ""
        ).strip():
            raise ValueError(
                f"factor {self.slug!r} declares a monotonic direction with no rationale "
                "(FR-MODEL-4). The direction is an actuarial judgement, and the next "
                "person needs to know whose and why."
            )
        return self


class OffsetSpec(BaseModel):
    """`02` §4.4. `log_column` is the frequency default: `offset = log(exposure)`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["none", "log_column", "column", "model"] = "none"
    column: str | None = None
    model_ref: str | None = None

    @model_validator(mode="after")
    def _a_column_offset_names_its_column(self) -> OffsetSpec:
        if self.kind in {"log_column", "column"} and not self.column:
            raise ValueError(f"offset kind {self.kind!r} requires a column")
        return self


class WeightSpec(BaseModel):
    """Severity weights by claim count, burning cost by exposure (FR-MODEL-19)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["none", "column"] = "none"
    column: str | None = None

    @model_validator(mode="after")
    def _a_column_weight_names_its_column(self) -> WeightSpec:
        if self.kind == "column" and not self.column:
            raise ValueError("weight kind 'column' requires a column")
        return self


class GlmSpec(BaseModel):
    """`02` §4.4's common block plus the `glm` arm.

    The spec is what `spec_hash` is taken over, so every field here changes the identity of
    the model. That is why `loss_treatment` belongs in the spec rather than beside it, and
    why two models differing only in a cap must not collide (FR-MODEL-66).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_type: Literal["glm"] = "glm"
    model_family_slug: str
    dataset_version_id: UUID
    peril: str | None = None
    response_column: str
    offset: OffsetSpec = OffsetSpec()
    weight: WeightSpec = WeightSpec()
    factors: tuple[UUID, ...] = ()
    #: FR-MODEL-18's supported families. `tweedie` carries its power in `family_params`.
    family: Literal[
        "poisson", "negative_binomial", "gamma", "inverse_gaussian",
        "tweedie", "binomial", "gaussian",
    ] = "poisson"
    family_params: dict[str, float] = Field(default_factory=dict)
    link: Literal["log", "logit", "identity", "inverse"] = "log"
    alpha: float = Field(default=0.0, ge=0.0)
    l1_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    max_iter: int = Field(default=200, ge=1)
    tolerance: float = Field(default=1e-8, gt=0.0)
    seed: int = 0

    @model_validator(mode="after")
    def _frequency_declares_its_exposure(self) -> GlmSpec:
        """FR-MODEL-19: a Poisson frequency model without an offset is a rate model that
        thinks it is a count model.

        Refused at the type rather than warned about downstream: the coefficients of a
        frequency GLM fitted without `log(exposure)` are wrong in a way that looks
        perfectly reasonable on the screen.
        """
        if self.family == "poisson" and self.offset.kind == "none":
            raise ValueError(
                "a Poisson model must declare an offset (FR-MODEL-19: frequency → Poisson, "
                "log link, offset = log(exposure)). Fitting counts without exposure "
                "silently models 'claims per policy-record' instead of 'claims per year'."
            )
        return self


class RelativityLevel(BaseModel):
    """One level of a categorical factor, as an actuary reads it (FR-MODEL-21)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: str
    relativity: float
    is_base: bool = False
    exposure: float | None = None


class Coefficient(BaseModel):
    """One fitted term, with the uncertainty `02` R5 requires of every estimate."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    term: str
    estimate: float
    std_error: Annotated[float, Field(ge=0.0)]
    z: float
    p_value: Annotated[float, Field(ge=0.0, le=1.0)]
    ci_95: tuple[float, float]
    #: `exp(estimate)` for a log link — the number an actuary actually reads. Stored rather
    #: than derived in the UI so the model artifact and the screen cannot disagree.
    relativity: float | None = None

    @model_validator(mode="after")
    def _the_interval_contains_the_estimate(self) -> Coefficient:
        low, high = self.ci_95
        if not low <= self.estimate <= high:
            raise ValueError(
                f"{self.term}: estimate {self.estimate} lies outside its interval "
                f"[{low}, {high}] — an interval that excludes its own point estimate is a "
                "transcription error, not a result."
            )
        return self


class GlmFitResult(BaseModel):
    """What a fit returns and the Model stores (ADR-0003).

    Data, never a pickled estimator: `PICKLE_PERSISTENCE_REFUSED` is an error code this
    module owns, and a Model must be re-scorable by a process that never ran `glum`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_type: Literal["glm"] = "glm"
    converged: bool
    iterations: int = Field(ge=0)
    fit_seconds: float = Field(ge=0.0)
    coefficients: tuple[Coefficient, ...] = ()
    relativities: dict[str, tuple[RelativityLevel, ...]] = Field(default_factory=dict)
    dispersion: float | None = None
    deviance: float | None = None
    rows: int = Field(default=0, ge=0)
    library_versions: dict[str, str] = Field(default_factory=dict)

    @property
    def intercept(self) -> Coefficient | None:
        return next((c for c in self.coefficients if c.term == "intercept"), None)


class ModelStatus(enum.StrEnum):
    DRAFT = "draft"
    FITTED = "fitted"
    REVIEW = "review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class Model(BaseModel):
    """A fitted model for one peril and response (`02` §4.8).

    Immutable once fitted (R2). Refitting produces a **new version** with
    `parent_model_id` set; there is no operation that edits a coefficient, which is what
    makes a Rating Version's reference to a model version mean something.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    model_family_slug: str
    version: int = Field(ge=1)
    status: ModelStatus = ModelStatus.DRAFT
    spec: GlmSpec
    spec_hash: str
    fit_result: GlmFitResult | None = None
    dataset_version_id: UUID
    parent_model_id: UUID | None = None
    change_reason: str | None = None
    flags: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _a_fitted_model_has_a_fit(self) -> Model:
        """`02` §4.8's invariant, at the type.

        A model at `fitted` or beyond without a `fit_result` would be a version something
        could be referenced by, carrying no numbers — which is worse than absent, because
        it is discoverable.
        """
        beyond_draft = self.status not in {ModelStatus.DRAFT, ModelStatus.ARCHIVED}
        if beyond_draft and self.fit_result is None:
            raise ValueError(
                f"model {self.model_family_slug}@{self.version} is {self.status.value} "
                "with no fit result (`02` §4.8)."
            )
        return self
