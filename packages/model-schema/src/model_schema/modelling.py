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

from model_schema.profiles import OneWayRow

__all__ = [
    "AboveRangePolicy",
    "Banding",
    "BandingMethod",
    "BandingProposal",
    "BelowRangePolicy",
    "Coefficient",
    "CredibilityStandard",
    "Factor",
    "FactorIntent",
    "FactorType",
    "GlmFitResult",
    "GlmSpec",
    "Grouping",
    "GroupingEvidence",
    "GroupingMethod",
    "GroupingProposal",
    "Model",
    "ModelStatus",
    "MonotonicDirection",
    "OffsetSpec",
    "RelativityLevel",
    "UnseenLevelBehaviour",
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
    #: `02` §4.1. The transformation a `banding` or `grouping` factor *is* — pinned by id,
    #: because both are versioned artifacts (FR-MODEL-12) and a factor that named a slug
    #: would change meaning the next time someone re-cut a boundary.
    banding_id: UUID | None = None
    grouping_id: UUID | None = None
    #: The level relativities are expressed against. Null until the fit picks one, because
    #: `largest_exposure` cannot be known without the data (FR-MODEL-21).
    base_level: str | None = None
    base_level_method: str = "largest_exposure"

    @model_validator(mode="after")
    def _the_type_and_its_transformation_agree(self) -> Factor:
        """A `banding` factor carries a Banding, and only a `banding` factor does.

        Both halves matter. Without the first, a banding factor resolves to its raw
        column and the fit is one nobody can tell from a correct one — the failure
        `resolve_factors` was written to refuse. Without the second, a `banding_id` sits on
        an `identity` factor reading as a transformation that is never applied.
        """
        required = {
            FactorType.BANDING: ("banding_id", self.banding_id),
            FactorType.GROUPING: ("grouping_id", self.grouping_id),
        }.get(self.type)
        if required is not None and required[1] is None:
            raise ValueError(
                f"factor {self.slug!r} is of type {self.type.value!r} and names no "
                f"{required[0]} (`02` §4.1). The transformation is what the factor *is*; "
                "without it the factor is its raw column under another name."
            )
        for field, value, owner in (
            ("banding_id", self.banding_id, FactorType.BANDING),
            ("grouping_id", self.grouping_id, FactorType.GROUPING),
        ):
            if value is not None and self.type is not owner:
                raise ValueError(
                    f"factor {self.slug!r} is of type {self.type.value!r} and names a "
                    f"{field}. Nothing would apply it, and a transformation recorded on an "
                    "artifact that ignores it reads as one the model used."
                )
        return self

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


class BandingMethod(enum.StrEnum):
    """How a Banding's boundaries were arrived at (`02` §2, FR-MODEL-9).

    Recorded on the artifact because the method *is* the judgement. Two bandings with
    identical boundaries, one hand-drawn and one from exposure quantiles, are different
    claims about the same numbers, and a reviewer needs to know which one they are reading.
    """

    MANUAL = "manual"
    EQUAL_WIDTH = "equal_width"
    QUANTILE = "quantile"
    EXPOSURE_QUANTILE = "exposure_quantile"
    TREE = "tree"
    CREDIBILITY = "credibility"


class BelowRangePolicy(enum.StrEnum):
    """What a value below the first boundary does (FR-MODEL-8).

    Explicit rather than defaulted: silently clamping a driver age of 3 into the 17-20 band
    is how a data defect becomes a price.
    """

    ERROR = "error"
    CLAMP_TO_FIRST = "clamp_to_first"
    NULL_LEVEL = "null_level"


class AboveRangePolicy(enum.StrEnum):
    """What a value at or above the last boundary does (FR-MODEL-8)."""

    ERROR = "error"
    CLAMP_TO_LAST = "clamp_to_last"
    NULL_LEVEL = "null_level"


class Banding(BaseModel):
    """A continuous column mapped to ordered, exhaustive, non-overlapping bands (§4.2).

    The invariants below are `02` §4.2's, at the type. They are not tidiness: a banding
    with overlapping intervals assigns one row to two levels, and a label list one short
    does not drop the last band — it renames every band after the gap. Both produce a model
    that fits, reads correctly, and is wrong.

    **Versioned, never edited** (FR-MODEL-12). A Model pins the Banding version it was
    fitted with, so re-cutting a boundary allocates a new version and leaves every existing
    model describing what it actually did.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    dataset_id: UUID
    version: int = Field(ge=1)
    column: str
    method: BandingMethod
    method_params: dict[str, float] = Field(default_factory=dict)
    #: The version the boundaries and `band_stats` were derived on (FR-MODEL-10). `None`
    #: for a `manual` banding authored from an actuary's judgement rather than from data.
    derived_on_dataset_version_id: UUID | None = None
    #: `n + 1` cut points for `n` bands. The outer two are the range's ends, so a value
    #: outside them is governed by `below_range` / `above_range` rather than lost.
    boundaries: tuple[float, ...] = Field(min_length=2)
    #: `left` means `[lower, upper)` — the actuarial convention for ages and years.
    closed: Literal["left", "right"] = "left"
    labels: tuple[str, ...] = Field(min_length=1)
    #: The label nulls map to. `None` means a null is a resolution error, which is the
    #: honest default: a missing driver age is not a band, it is a missing value.
    null_level: str | None = None
    below_range: BelowRangePolicy = BelowRangePolicy.ERROR
    above_range: AboveRangePolicy = AboveRangePolicy.ERROR
    #: FR-MODEL-10's evidence, as of derivation. `OneWayRow` rather than a second shape
    #: holding the same numbers: `01` FR-DATA-26 already computes exposure, claims,
    #: frequency, severity and burning cost by level with intervals, and a band is a level.
    band_stats: tuple[OneWayRow, ...] = ()

    @model_validator(mode="after")
    def _boundaries_and_labels_describe_the_same_bands(self) -> Banding:
        if any(
            later <= earlier
            for earlier, later in zip(self.boundaries, self.boundaries[1:], strict=False)
        ):
            raise ValueError(
                f"banding {self.slug!r} has boundaries {list(self.boundaries)}, which do "
                "not strictly increase (`02` §4.2). Equal cut points make an empty band and "
                "a decreasing pair makes an overlapping one; both send rows to a band the "
                "reader cannot predict."
            )
        expected = len(self.boundaries) - 1
        if len(self.labels) != expected:
            raise ValueError(
                f"banding {self.slug!r} has {len(self.labels)} labels for {expected} bands "
                "(`02` §4.2). A label list one short does not drop the last band — it "
                "renames every band after the gap."
            )
        if len(set(self.labels)) != len(self.labels):
            raise ValueError(
                f"banding {self.slug!r} repeats a label. Two bands sharing a name are one "
                "level to every fit, table and chart downstream, which is a grouping nobody "
                "declared."
            )
        if self.null_level is not None and self.null_level in self.labels:
            raise ValueError(
                f"banding {self.slug!r} sends nulls to {self.null_level!r}, which is also a "
                "band. 'Missing' and 'in this range' would then be indistinguishable in "
                "every relativity table."
            )
        return self

    @property
    def levels(self) -> tuple[str, ...]:
        """Every level a resolved column can take, the null level included."""
        return self.labels if self.null_level is None else (*self.labels, self.null_level)


class GroupingMethod(enum.StrEnum):
    """How Levels were merged (`02` §2, FR-MODEL-14)."""

    MANUAL = "manual"
    CREDIBILITY_WEIGHTED = "credibility_weighted"
    HIERARCHICAL_CLUSTERING = "hierarchical_clustering"
    TREE = "tree"
    REFERENCE_HIERARCHY = "reference_hierarchy"


class CredibilityStandard(enum.StrEnum):
    """Which credibility theory `credibility_weighted` merging applies (OQ-MODEL-5).

    Named on the artifact rather than fixed in the code because it is a modelling
    judgement, not a platform constant — and because the two standards disagree on thin
    cells, which is the only place the choice changes anything.
    """

    LIMITED_FLUCTUATION = "limited_fluctuation"
    BUHLMANN_STRAUB = "buhlmann_straub"


class UnseenLevelBehaviour(enum.StrEnum):
    """What scoring does with a Level the Grouping has never seen (FR-MODEL-13).

    Mandatory — the field carries no default anywhere in this module. A grouping that
    silently drops an unseen level prices it as the base, which is the cheapest cell by
    construction, and nobody finds out before the loss ratio does.
    """

    ERROR = "error"
    MAP_TO_DEFAULT = "map_to_default"
    MAP_TO_BASE = "map_to_base"


class GroupingEvidence(BaseModel):
    """The change in fit a Grouping implies (FR-MODEL-15).

    Grouping is a modelling decision and must be defensible as one, so the artifact carries
    what it cost: deviance before and after, the degrees of freedom saved, and the
    likelihood-ratio p-value that says whether the collapse was affordable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_level_count: int = Field(ge=0)
    target_level_count: int = Field(ge=0)
    deviance_before: float | None = None
    deviance_after: float | None = None
    df_saved: int = 0
    chi2_p_value: float | None = Field(default=None, ge=0.0, le=1.0)
    #: The resulting target levels, carrying the statistics a source level carries — so
    #: "what did merging these four into G1 do to the frequency?" is a comparison rather
    #: than a re-run.
    target_level_stats: tuple[OneWayRow, ...] = ()


class Grouping(BaseModel):
    """Source Levels mapped to target Levels (`02` §4.3, FR-MODEL-13..17).

    Exhaustive over the Levels observed when it was derived, and explicit about the ones it
    was not: `unseen_level_behaviour` has no default, because the three answers price an
    unknown vehicle group very differently and none of them is obviously right.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    dataset_id: UUID
    version: int = Field(ge=1)
    column: str
    method: GroupingMethod
    method_params: dict[str, float] = Field(default_factory=dict)
    #: Set only by `credibility_weighted` (OQ-MODEL-5).
    credibility_standard: CredibilityStandard | None = None
    derived_on_dataset_version_id: UUID | None = None
    #: Source level → target level. Keys are source levels as strings, because that is what
    #: a column cast to text yields and what a relativity table shows.
    mapping: dict[str, str] = Field(min_length=1)
    unseen_level_behaviour: UnseenLevelBehaviour
    default_target_level: str | None = None
    #: FR-MODEL-17: a chain applied in order (outcode → area → region), so the finer level
    #: stays available for diagnostics while rating happens on the coarser one.
    parent_grouping_id: UUID | None = None
    evidence: GroupingEvidence | None = None

    @model_validator(mode="after")
    def _the_declared_behaviour_is_reachable(self) -> Grouping:
        targets = set(self.mapping.values())
        if self.unseen_level_behaviour is UnseenLevelBehaviour.MAP_TO_DEFAULT:
            if not self.default_target_level:
                raise ValueError(
                    f"grouping {self.slug!r} maps unseen levels to a default and names no "
                    "default (FR-MODEL-13). The behaviour is mandatory precisely so it "
                    "cannot be half-declared."
                )
            if self.default_target_level not in targets:
                raise ValueError(
                    f"grouping {self.slug!r} defaults unseen levels to "
                    f"{self.default_target_level!r}, which is not one of its target levels. "
                    "An unseen level would land on a level no fitted model has a "
                    "coefficient for."
                )
        elif self.default_target_level is not None:
            raise ValueError(
                f"grouping {self.slug!r} names a default target level while its unseen "
                f"behaviour is {self.unseen_level_behaviour.value!r}. A default nothing "
                "consults reads as protection that is not there."
            )
        if (
            self.credibility_standard is not None
            and self.method is not GroupingMethod.CREDIBILITY_WEIGHTED
        ):
            raise ValueError(
                f"grouping {self.slug!r} names a credibility standard with method "
                f"{self.method.value!r}, which does not use one."
            )
        return self

    @property
    def target_levels(self) -> tuple[str, ...]:
        """The levels a resolved column can take, in first-seen order."""
        seen: dict[str, None] = {}
        for target in self.mapping.values():
            seen.setdefault(target, None)
        return tuple(seen)


class BandingProposal(BaseModel):
    """What `POST /bandings/propose` asks for (FR-MODEL-9, `02` §5.2).

    A proposal, never a persisted artifact: the boundaries come back editable, and what is
    stored is what the actuary accepted. Hence a separate shape — a `Banding` carries an id
    and a version, and neither exists yet.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID
    column: str
    method: BandingMethod
    n_bands: int = Field(default=10, ge=1, le=200)
    #: Method-specific knobs: `min_claims_per_band` for `credibility`, and the exposure /
    #: claim-count column names where the dataset does not use the `01` conventions.
    method_params: dict[str, float] = Field(default_factory=dict)
    exposure_column: str = "exposure_years"
    claim_count_column: str = "claim_count"
    claim_amount_column: str = "claim_amount_minor"
    closed: Literal["left", "right"] = "left"
    null_level: str | None = None
    below_range: BelowRangePolicy = BelowRangePolicy.ERROR
    above_range: AboveRangePolicy = AboveRangePolicy.ERROR


class GroupingProposal(BaseModel):
    """What `POST /groupings/propose` asks for (FR-MODEL-14, `02` §5.2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID
    column: str
    method: GroupingMethod
    #: The number of target levels to collapse to. Ignored by `credibility_weighted`, which
    #: merges until the standard is met rather than to a count.
    n_groups: int = Field(default=8, ge=1, le=200)
    method_params: dict[str, float] = Field(default_factory=dict)
    credibility_standard: CredibilityStandard = CredibilityStandard.LIMITED_FLUCTUATION
    exposure_column: str = "exposure_years"
    claim_count_column: str = "claim_count"
    claim_amount_column: str = "claim_amount_minor"
    unseen_level_behaviour: UnseenLevelBehaviour
    default_target_level: str | None = None


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
    def _a_tweedie_power_lies_between_the_two_families_it_spans(self) -> GlmSpec:
        """`CLAUDE.md` §7: burning cost is Tweedie with 1 < p < 2.

        Outside that it is a different family — Poisson at 1, Gamma at 2 — not a
        differently-tuned one. Checked here rather than at fit time because it is a fact
        about the specification, and a spec that cannot be fitted should not be storable.
        """
        if self.family == "tweedie":
            power = float(self.family_params.get("power", 1.5))
            if not 1.0 < power < 2.0:
                raise ValueError(
                    f"tweedie power {power} is outside (1, 2). At 1 it is Poisson and at 2 "
                    "it is Gamma; between them it is the compound-Poisson-Gamma that "
                    "burning cost needs."
                )
        return self

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
    #: `None` where the link is not multiplicative. A relativity is `exp(β)` — meaningful
    #: under a log link and nothing under `logit` or `identity`, where the level's effect
    #: is additive on the link scale. Reporting 1.0 there said "no effect" for a factor
    #: spanning eighteen log-odds, which is worse than reporting nothing.
    relativity: float | None = None
    #: The coefficient itself, which every link has.
    estimate: float | None = None
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
    #: The scale parameter φ. Estimated for Gamma, Gaussian, inverse-Gaussian and
    #: Tweedie; fixed at 1 for Poisson and binomial, where it is not a free parameter.
    #: `None` only if the estimator could not supply one.
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
