"""Modelling shapes: Factors, Model Specs, and what a fit returns (`02` §4).

`02` §4.4's tagged union has four declared arms and this carries two: `glm`, and the
gradient-boosting pair `xgboost`/`lightgbm`. `ebm` arrives with the slice that fits one,
because a declared arm nothing can produce is a shape that will be wrong by the time
anything does.

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
from decimal import Decimal
from typing import Annotated, Any, Final, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from model_schema.money import DecimalStr
from model_schema.profiles import OneWayRow
from model_schema.refs import BlobRef

__all__ = [
    "FIT_RESULT_ADAPTER",
    "MODEL_SPEC_ADAPTER",
    "TERMINAL_MODEL_STATUSES",
    "VALID_MODEL_TRANSITIONS",
    "AboveRangePolicy",
    "Banding",
    "BandingEvaluation",
    "BandingMethod",
    "BandingMinimums",
    "BandingProposal",
    "BelowRangePolicy",
    "Coefficient",
    "CredibilityModel",
    "EarlyStopping",
    "Factor",
    "FactorIntent",
    "FactorType",
    "FitResult",
    "GbmFitResult",
    "GbmFunctionRef",
    "GbmSpec",
    "GlmFitResult",
    "GlmSpec",
    "Grouping",
    "GroupingEvaluation",
    "GroupingEvidence",
    "GroupingMethod",
    "GroupingProposal",
    "LossTreatment",
    "Model",
    "ModelFlag",
    "ModelSpec",
    "ModelSpecCommon",
    "ModelStatus",
    "MonotonicDirection",
    "OffsetSpec",
    "RelativityLevel",
    "SpecProblem",
    "SpecProblemKind",
    "SpecValidation",
    "SplitRef",
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
    #: The dataset columns this factor reads. **Not** unconditionally non-empty since
    #: 2026-08-18: an `interaction` sources no columns of its own — its columns are its
    #: operands' — and listing them again would be a second statement of one fact. The
    #: requirement is re-imposed per type in the validator below, so every other arm is as
    #: strict as it was and the interaction arm is stricter.
    source_columns: tuple[str, ...] = ()
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
    #: `02` §4.1, added 2026-08-18. The Factors an `interaction` crosses, in the order they
    #: are crossed. **Factors, not columns**: every place the specification names an
    #: interaction it names factors — §4.4's `interaction_constraints`, §4.9's
    #: `top_interactions` — and an operand is usually itself a banding or a grouping, which
    #: a column reference cannot express. Pinned by id for the reason `banding_id` is.
    operand_factor_ids: tuple[UUID, ...] = ()
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
        self._the_interaction_arm()
        self._columns_match_the_type()
        return self

    def _the_interaction_arm(self) -> None:
        """`operand_factor_ids` is the interaction's transformation (`02` §4.1).

        Four refusals, and each is a design column that would otherwise be wrong rather
        than absent:

        * **no operands** — the same state as a `banding` factor with no Banding: a name
          with no transformation behind it;
        * **one operand** — a cross of one *is* that factor, so the model document would
          carry two names for one design column and the relativity table could not say
          which produced it;
        * **a repeated operand** — `age x age` is `age`, with every off-diagonal cell empty
          by construction;
        * **crossing itself** — a cycle, and the resolver would not terminate.
        """
        if self.type is not FactorType.INTERACTION:
            if self.operand_factor_ids:
                raise ValueError(
                    f"factor {self.slug!r} is of type {self.type.value!r} and names "
                    "operand_factor_ids. Nothing would cross them, and operands recorded "
                    "on an artifact that ignores them read as ones the model used."
                )
            return

        if len(self.operand_factor_ids) < 2:
            raise ValueError(
                f"factor {self.slug!r} is an interaction over "
                f"{len(self.operand_factor_ids)} operand(s). An interaction crosses **two "
                "or more** Factors (`02` §4.1); a cross of one is that factor under a "
                "second name, and a cross of none has no transformation behind it. The "
                "field is `operand_factor_ids`."
            )
        if len(set(self.operand_factor_ids)) != len(self.operand_factor_ids):
            raise ValueError(
                f"factor {self.slug!r} names an operand more than once. Crossing a factor "
                "with itself reproduces it, with every off-diagonal cell empty."
            )
        if self.id in self.operand_factor_ids:
            raise ValueError(
                f"factor {self.slug!r} names itself among its operands. Resolving it would "
                "not terminate."
            )

    def _columns_match_the_type(self) -> None:
        """Every arm but `interaction` reads at least one column of its own.

        This was `Field(min_length=1)` until the interaction arm arrived. Moved here rather
        than dropped: the interaction is the *only* type that sources nothing, and relaxing
        the field without re-imposing the rule would have let an `identity` factor over no
        column through — a factor that resolves to nothing and reports no error.
        """
        if self.type is FactorType.INTERACTION:
            if self.source_columns:
                raise ValueError(
                    f"factor {self.slug!r} is an interaction and names source_columns "
                    f"{list(self.source_columns)}. Its columns are its operands'; naming "
                    "them again is a second statement of one fact, and the two disagree "
                    "the first time an operand is re-versioned onto another column."
                )
        elif not self.source_columns:
            raise ValueError(
                f"factor {self.slug!r} is of type {self.type.value!r} and names no "
                "source_columns. Only an interaction sources none."
            )

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


class BandingMinimums(BaseModel):
    """FR-MODEL-11's thresholds, stored **on the artifact** (`banding.schema.json`).

    On the banding rather than passed to the check, because "configurable" means a reviewer
    can see what was configured. Held at the call site instead, the choice persists nowhere
    and two fits of the same banding could apply different floors.

    An empty band always fails regardless of these, which is why there is no setting for it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: An exposure, so an exact decimal on the wire and never a binary float (FR-OVR-7) —
    #: `banding.schema.json` types it as `Decimal` and the first implementation made it a
    #: float, which the money scan caught.
    min_exposure_per_band: DecimalStr = Decimal(0)
    min_claims_per_band: int = Field(default=0, ge=0)
    on_violation: Literal["warn", "fail"] = "warn"


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
    #: FR-MODEL-11's thresholds, as `banding.schema.json` declares them.
    minimums: BandingMinimums = BandingMinimums()
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


class CredibilityModel(enum.StrEnum):
    """Which credibility theory `credibility_weighted` merging applies (FR-MODEL-80).

    Recorded per grouping rather than fixed in the code because it is a modelling
    judgement, not a platform constant — and because the two disagree on thin cells, which
    is the only place the choice changes anything.

    It lives in `method_params` under `credibility_model`, which is where
    `grouping.schema.json` has carried it since Phase 0. It was briefly a top-level
    `credibility_standard` field on `Grouping`; that contradicted the committed contract,
    and the contract was right.
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
    #: FR-MODEL-80: EVPV, VHM and `k`, so a reviewer can re-derive `Z` rather than take it.
    #: `None` under limited fluctuation, which has no variance components to report.
    credibility_components: dict[str, float] | None = None
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
    #: `Any` rather than `float` because the contract's own params are not all numbers:
    #: `credibility_model` is a string and `credibility_pk` an object (FR-MODEL-80).
    method_params: dict[str, Any] = Field(default_factory=dict)
    derived_on_dataset_version_id: UUID | None = None
    #: Source level → target level. Keys are source levels as strings, because that is what
    #: a column cast to text yields and what a relativity table shows.
    mapping: dict[str, str] = Field(min_length=1)
    unseen_level_behaviour: UnseenLevelBehaviour
    default_target_level: str | None = None
    #: FR-MODEL-17: a chain applied in order (outcode → area → region), so the finer level
    #: stays available for diagnostics while rating happens on the coarser one.
    parent_grouping_id: UUID | None = None
    #: FR-MODEL-16: the generated model document lists every grouping with its method **and
    #: rationale**, and `grouping.schema.json` says it appears verbatim in the dossier
    #: (`06` §4.4 §4). Declared by the contract since Phase 0 and missed by the first
    #: implementation of this shape; a merge nobody can explain is one nobody can defend.
    rationale: str | None = None
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
        declared = self.method_params.get("credibility_model")
        if declared is not None:
            if self.method is not GroupingMethod.CREDIBILITY_WEIGHTED:
                raise ValueError(
                    f"grouping {self.slug!r} names a credibility model with method "
                    f"{self.method.value!r}, which does not use one."
                )
            if declared not in tuple(CredibilityModel):
                raise ValueError(
                    f"grouping {self.slug!r} names credibility model {declared!r}, which "
                    f"is not one of {[m.value for m in CredibilityModel]} (FR-MODEL-80)."
                )
        return self

    @property
    def credibility_model(self) -> CredibilityModel | None:
        """The credibility theory this grouping applied, or `None` (FR-MODEL-80).

        Read through a property so callers get the enum without every one of them knowing
        the key it is stored under — and so the storage stays exactly what the contract
        describes.
        """
        declared = self.method_params.get("credibility_model")
        return CredibilityModel(declared) if declared is not None else None

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
    method_params: dict[str, Any] = Field(default_factory=dict)
    #: FR-MODEL-80's default, and what a UK reviewer expects to see. Written into the
    #: resulting grouping's `method_params`, never kept beside them.
    credibility_model: CredibilityModel = CredibilityModel.LIMITED_FLUCTUATION
    #: The `(p, k)` pair the full-credibility standard is derived from. 1 082 claims is
    #: ±5 % at 90 % confidence; a reviewer who cannot see `(p, k)` cannot tell 1 082 from a
    #: house number (FR-MODEL-80).
    credibility_p: float = Field(default=0.90, gt=0.0, lt=1.0)
    credibility_k: float = Field(default=0.05, gt=0.0)
    exposure_column: str = "exposure_years"
    claim_count_column: str = "claim_count"
    claim_amount_column: str = "claim_amount_minor"
    unseen_level_behaviour: UnseenLevelBehaviour
    default_target_level: str | None = None


class BandingEvaluation(BaseModel):
    """What `POST /bandings/evaluate` asks for (FR-MODEL-75).

    A whole `Banding` rather than a list of boundaries, because the answer depends on all
    of it — `closed`, `null_level` and the two range policies each decide where rows land,
    and evaluating boundaries alone would report statistics for a banding nobody could save.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID
    banding: Banding
    exposure_column: str = "exposure_years"
    claim_count_column: str = "claim_count"
    claim_amount_column: str = "claim_amount_minor"


class GroupingEvaluation(BaseModel):
    """What `POST /groupings/evaluate` asks for (FR-MODEL-75)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID
    grouping: Grouping
    exposure_column: str = "exposure_years"
    claim_count_column: str = "claim_count"
    claim_amount_column: str = "claim_amount_minor"


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


class SplitRef(BaseModel):
    """The named split a model was fitted and judged on (`02` §4.4, `01` FR-DATA-36).

    A *reference*, not a description. FR-DATA-36 records the split on the **parent**
    version precisely so that "trained on the same split" is one artifact two models cite,
    rather than two derivations that were believed to match. Naming the part versions
    directly here would reintroduce the belief.

    `train_part` and `holdout_part` are keys into the split's `parts` map; that they name
    two *different* parts is checked here, because a model whose holdout is its training
    set reports a flawless fit and no diagnostic downstream can tell.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    split_artifact_id: UUID
    train_part: str = "train"
    holdout_part: str = "test"

    @model_validator(mode="after")
    def _the_holdout_is_not_the_training_set(self) -> SplitRef:
        if self.train_part == self.holdout_part:
            raise ValueError(
                f"train and holdout are both {self.train_part!r}. A model measured on the "
                "rows it was fitted on reports its own memory, and FR-MODEL-54's "
                "side-by-side comparison would then show two copies of one number."
            )
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


class LossTreatment(BaseModel):
    """How large losses are treated **as the model is fitted** (FR-MODEL-73).

    A modelling decision, not a property of the data: `01` VR-ACT-10 flags large losses and
    never removes them, so one validated Dataset Version serves many capping assumptions
    without re-ingestion. That is only true while the assumption lives here, inside the
    spec — and therefore inside `spec_hash`, so two models differing only in their cap are
    two models rather than a collision (FR-MODEL-66).

    `cap_minor` is **integer minor units** (`CLAUDE.md` §7). A cap is a money threshold
    compared against a money column, and a float one compares unequal to itself at the
    boundary — which decides whether the largest claim in the book was capped.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: `spliced` and `excess` are declared by FR-MODEL-73 and refused by the fit path until
    #: a slice implements them (`02` §3.5, noted 2026-08-17). Declared-and-refused rather
    #: than omitted: narrowing the enum now would cost a `spec_hash` version to widen later.
    kind: Literal["none", "capped", "spliced", "excess"] = "none"
    cap_minor: int | None = Field(default=None, ge=0)
    #: The loading that restores the mean after capping. Required with a cap because
    #: FR-MODEL-74 reconciles a capped model against **uncapped** experience: without it
    #: the reconciliation reports a modelling error where there was an intended adjustment.
    restoration_loading: float | None = Field(default=None, gt=0.0)
    evidence_blob: BlobRef | None = None

    @model_validator(mode="after")
    def _a_treatment_carries_exactly_the_parameters_it_needs(self) -> LossTreatment:
        if self.kind == "none" and (self.cap_minor is not None
                                    or self.restoration_loading is not None):
            raise ValueError(
                "loss treatment 'none' carries a cap or a restoration loading. A reader "
                "cannot then tell whether the response was capped, and the answer is "
                "inside `spec_hash` for ever."
            )
        if self.kind != "none" and self.cap_minor is None:
            raise ValueError(f"loss treatment {self.kind!r} requires cap_minor")
        if self.kind == "capped" and self.restoration_loading is None:
            raise ValueError(
                "a capped response requires restoration_loading (FR-MODEL-74: the "
                "reconciliation compares restored burning cost against uncapped observed)."
            )
        return self


class ModelSpecCommon(BaseModel):
    """`02` §4.4's common block — every arm of the tagged union carries these.

    A base class rather than a copied field list, for the reason `CLAUDE.md` §2 gives:
    a shape defined twice diverges, and a diverged spec field is a mispricing.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_family_slug: str
    dataset_version_id: UUID
    #: `02` §4.4's `split_ref`, live from the diagnostics slice. Optional because a model
    #: may be explored without a holdout; **required to reach `fitted`**, since FR-MODEL-54
    #: makes a diagnostic without its holdout counterpart a defect and FR-MODEL-64 makes
    #: diagnostics the condition of `fitted`. The obligation therefore sits on `Model`,
    #: where the status is, rather than here.
    split_ref: SplitRef | None = None
    peril: str | None = None
    response_column: str
    offset: OffsetSpec = OffsetSpec()
    weight: WeightSpec = WeightSpec()
    factors: tuple[UUID, ...] = ()
    loss_treatment: LossTreatment = LossTreatment()
    seed: int = 0


class GlmSpec(ModelSpecCommon):
    """`02` §4.4's common block plus the `glm` arm.

    The spec is what `spec_hash` is taken over, so every field here changes the identity of
    the model. That is why `loss_treatment` belongs in the spec rather than beside it, and
    why two models differing only in a cap must not collide (FR-MODEL-66).
    """

    model_type: Literal["glm"] = "glm"
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


class GbmFunctionRef(BaseModel):
    """A builtin objective or eval metric by name, or an approved artifact by reference.

    One shape for both because FR-MODEL-26 and FR-MODEL-45 declare the same choice twice —
    a builtin the backend already implements, or a Custom Objective / Custom Metric that
    carries its own approval status (R4). Two classes with identical fields would be a
    shape defined twice.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["builtin", "custom"]
    #: FR-MODEL-26's insurance objectives: `count:poisson`, `reg:gamma`, `reg:tweedie`,
    #: `binary:logistic`. Not an enum — the eval-metric vocabulary is the backend's and
    #: differs between them, and a closed set here would refuse a metric XGBoost supports.
    name: str | None = None
    #: `custom_objective:<slug>@<version>` / `custom_metric:<slug>@<version>`.
    ref: str | None = None

    @model_validator(mode="after")
    def _the_kind_decides_which_field_is_meaningful(self) -> GbmFunctionRef:
        if self.kind == "builtin":
            if not self.name:
                raise ValueError("a builtin objective or metric needs a name")
            if self.ref:
                raise ValueError(
                    "a builtin objective or metric carries a ref as well as a name. The "
                    "fit path would have to choose, and two runs could choose differently."
                )
        else:
            if not self.ref:
                raise ValueError("a custom objective or metric needs a ref")
            if self.name:
                raise ValueError("a custom objective or metric carries a name as well as a ref")
        return self


class EarlyStopping(BaseModel):
    """When to stop boosting, and against what (FR-MODEL-30).

    **There is no `train` value**, and that is the requirement rather than an oversight:
    a stopping rule read off the data being fitted stops when the model has finished
    memorising. Refusing it by construction means no validator can be relaxed into
    allowing it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    on: Literal["holdout", "cv"]
    metric: str
    rounds: int = Field(ge=1)
    #: Required for `on='cv'`; meaningless otherwise.
    cv_folds: int | None = Field(default=None, ge=2)

    @model_validator(mode="after")
    def _cross_validation_declares_its_folds(self) -> EarlyStopping:
        if self.on == "cv" and self.cv_folds is None:
            raise ValueError("early stopping on cv requires cv_folds")
        if self.on == "holdout" and self.cv_folds is not None:
            raise ValueError("early stopping on a holdout does not take cv_folds")
        return self


class GbmSpec(ModelSpecCommon):
    """`02` §4.4's common block plus the gradient-boosting arm (FR-MODEL-25).

    **One contract, two backends.** `model_type` is the backend — §4.4 also gave this arm a
    `backend` field carrying the same two strings, and two fields holding one fact can
    disagree with nothing downstream able to say which to believe. Backend-specific tuning
    lives in `backend_params`, which is what keeps the contract from forking.

    **The offset is declared once.** §4.4 also gave this arm a `base_margin` block of the
    same shape as the common `offset`. FR-MODEL-27 says the platform *constructs*
    `base_margin` from the declared offset, so a second declaration is a second source of
    truth for the one number the fit silently depends on. What was actually constructed is
    recorded on the fit result, where FR-MODEL-71 can assert it at load time.

    Both corrections are recorded in `02` §4.4, dated 2026-08-17.
    """

    model_type: Literal["xgboost", "lightgbm"]
    objective: GbmFunctionRef
    #: FR-MODEL-27's escape hatch. A frequency objective with no offset is refused unless
    #: this says why — a sentence a reviewer reads, rather than an omission nobody sees.
    offset_acknowledgement: str | None = None
    #: FR-MODEL-28. `derived_from_factors` reads each Factor's monotonic direction; the
    #: vector that results is persisted on the fit result, beside the feature order.
    monotone_constraints: Literal["derived_from_factors", "none"] = "derived_from_factors"
    #: FR-MODEL-29: interaction is permitted *within* each declared group and nowhere else.
    interaction_constraints: tuple[tuple[str, ...], ...] = ()
    #: §4.4's common tuning knobs — `max_depth`, `eta`, `subsample`, `num_boost_round` and
    #: the rest. A dict rather than fields because the two backends spell several of them
    #: differently and a fixed set would refuse a legitimate one.
    #:
    #: `int | float`, **not `float`**: declared as `float` this coerced `max_depth: 5` to
    #: `5.0`, and both libraries reject a float where they want an integer — XGBoost with
    #: "Invalid Parameter format for max_depth expect int but value='3.0'", LightGBM with
    #: its own wording. A contract that silently retypes a caller's integer is a contract
    #: that fails at the backend, one layer past where the mistake was made.
    hyperparameters: dict[str, int | float] = Field(default_factory=dict)
    early_stopping: EarlyStopping | None = None
    #: FR-MODEL-32, and **no default**: a default would be the silence the requirement
    #: exists to refuse. `native` uses the backend's categorical support; `factor_encoding`
    #: takes the mapping from the Factor's grouping.
    categorical_handling: Literal["native", "factor_encoding"]
    eval_metrics: tuple[GbmFunctionRef, ...] = ()
    #: The backend-specific escape hatch (`tree_method`, `boosting_type`, …), namespaced so
    #: FR-MODEL-25's single contract does not fork into two.
    backend_params: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _a_frequency_gbm_declares_its_exposure(self) -> GbmSpec:
        """FR-MODEL-27, and the GBM half of what `GlmSpec` refuses for the same reason.

        Exposure rides in `base_margin`/`init_score` as `log(exposure)`. Passed as a
        feature it is a variable the trees may split on; passed as a weight under a count
        objective it changes the loss rather than the mean. Both fit, neither errors, and
        the model has learned claims-per-record.
        """
        counting = self.objective.kind == "builtin" and (
            self.objective.name or ""
        ).startswith(("count:", "reg:tweedie"))
        if counting and self.offset.kind == "none" and not self.offset_acknowledgement:
            raise ValueError(
                f"objective {self.objective.name!r} counts events but the spec declares no "
                "offset (FR-MODEL-27). Set offset to log(exposure), or say in "
                "offset_acknowledgement why this data needs none."
            )
        return self

    @model_validator(mode="after")
    def _an_interaction_group_names_at_least_two_features(self) -> GbmSpec:
        """A group of one permits nothing and forbids nothing (FR-MODEL-29).

        Written by hand it is almost always a truncated list; read back it looks
        deliberate.
        """
        for group in self.interaction_constraints:
            if len(group) < 2:
                raise ValueError(
                    f"interaction group {list(group)} names fewer than two features. A "
                    "group of one constrains nothing, and reads as though it did."
                )
        return self

    @model_validator(mode="after")
    def _early_stopping_on_a_holdout_needs_one(self) -> GbmSpec:
        """FR-MODEL-30: early stopping requires a *declared* holdout or CV scheme.

        `split_ref` is where the holdout is declared (`01` FR-DATA-36). Stopping "on the
        holdout" with no split named would fall back to the training set, which is the one
        thing the requirement forbids.
        """
        if self.early_stopping and self.early_stopping.on == "holdout" and self.split_ref is None:
            raise ValueError(
                "early stopping on a holdout requires split_ref (FR-MODEL-30). Without a "
                "declared split there is no holdout, and the stopping metric would be read "
                "off the training rows."
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


class GbmFitResult(BaseModel):
    """What a GBM fit returns and the Model stores (ADR-0003, FR-MODEL-31).

    The booster is a **content-addressed blob in the backend's own JSON or text format**,
    never a pickle — `booster_format` has no spelling for one, so the persistence layer's
    refusal is not the only thing between a Model and an artifact that executes on load.

    Everything needed to score is here beside it: feature order, dtype expectations,
    categorical encoding maps, the monotone constraint vector, the pinned library version,
    and — required, not optional — the `base_margin` construction. FR-MODEL-71 is emphatic
    about the last one because omitting the offset at scoring time fails *silently* on both
    backends, and differently.

    The evaluation curve is **not** here. FR-MODEL-52 names it a GBM-specific *diagnostic*
    and asks for train and holdout side by side, which is FR-MODEL-54's shape; it lives on
    `GbmDiagnostics`, and `fit_gbm` returns it beside this artifact for the caller to place
    there. `best_iteration` stays, because scoring needs it and diagnostics are not loaded
    to score. (`diagnostics.schema.json` had it this way from Phase 0; this is the code
    agreeing with it rather than the schema being edited to match.)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_type: Literal["xgboost", "lightgbm"]
    booster_blob: BlobRef
    #: ADR-0003. `pickle` is not a refused value here — it is not a value.
    booster_format: Literal["xgboost_json", "lightgbm_text"]
    feature_order: tuple[str, ...]
    #: FR-MODEL-31's dtype expectations, one per feature — checked against `feature_order`
    #: below, because a scoring frame built from a partial map is a frame with a column
    #: whose type nobody declared.
    feature_dtypes: dict[str, str] = Field(default_factory=dict)
    #: FR-MODEL-32's encoding maps, per categorical feature.
    categorical_maps: dict[str, dict[str, int]] = Field(default_factory=dict)
    #: FR-MODEL-28, positionally aligned with `feature_order`. Empty when the spec asked
    #: for none.
    monotone_constraints: tuple[int, ...] = ()
    #: FR-MODEL-71. **Required**: the load-time assertion needs something to assert.
    base_margin: OffsetSpec
    #: Kept here and **not** in the diagnostics: `predict_gbm` needs it to score
    #: (`iteration_range` / `num_iteration`), and diagnostics are not loaded at scoring
    #: time. The evaluation *curve* went the other way — see `GbmDiagnostics`.
    best_iteration: int = Field(ge=0)
    rows: int = Field(default=0, ge=0)
    fit_seconds: float = Field(ge=0.0)
    library_versions: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _the_constraint_vector_is_aligned_with_the_feature_order(self) -> GbmFitResult:
        """FR-MODEL-28: the vector is persisted *alongside* the feature order.

        Positional data whose length is unchecked is positional data that will one day be
        off by one — and a monotone constraint applied to the wrong column is a model that
        is monotone in the wrong thing, which reads as correct on every screen.
        """
        if self.monotone_constraints and len(self.monotone_constraints) != len(self.feature_order):
            raise ValueError(
                f"{len(self.monotone_constraints)} monotone constraints for "
                f"{len(self.feature_order)} features in feature_order. The vector is "
                "positional; a mismatch silently constrains the wrong column."
            )
        return self

    @model_validator(mode="after")
    def _every_feature_declares_its_dtype(self) -> GbmFitResult:
        """FR-MODEL-31's dtype expectations, checked rather than hoped for.

        A scoring frame assembled from a partial map has a column whose type nobody
        declared, and the backends differ in what they infer for it.
        """
        if self.feature_dtypes and set(self.feature_dtypes) != set(self.feature_order):
            missing = sorted(set(self.feature_order) - set(self.feature_dtypes))
            extra = sorted(set(self.feature_dtypes) - set(self.feature_order))
            raise ValueError(
                f"feature_dtypes does not cover feature_order (missing {missing}, "
                f"unexpected {extra})."
            )
        return self


#: `02` §4.4's tagged union, as a union rather than as a promise. Until this existed the
#: tag was present and `GlmSpec.model_validate` was the only reader, so a GBM payload
#: failed on a literal mismatch rather than on anything a caller could act on.
ModelSpec = Annotated[GlmSpec | GbmSpec, Field(discriminator="model_type")]
MODEL_SPEC_ADAPTER: Final[TypeAdapter[ModelSpec]] = TypeAdapter(ModelSpec)

#: The same union over what a fit returns. Both are discriminated on `model_type`, and
#: `Model` checks that the two agree — see `_the_fit_matches_the_specification`.
FitResult = Annotated[GlmFitResult | GbmFitResult, Field(discriminator="model_type")]
FIT_RESULT_ADAPTER: Final[TypeAdapter[FitResult]] = TypeAdapter(FitResult)


class ModelStatus(enum.StrEnum):
    DRAFT = "draft"
    FITTED = "fitted"
    REVIEW = "review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ModelFlag(enum.StrEnum):
    """Conditions raised elsewhere that gate this model's approval (`06` FR-GOV-17).

    Named rather than free strings because two surfaces branch on them — `02` FR-MODEL-67's
    block on `approved`, and the approvals inbox — and a flag spelled two ways is a gate
    that holds on one screen and not the other.
    """

    DATASET_INVALIDATED = "dataset_invalidated"


#: FR-MODEL-64's lifecycle, as data rather than as conditionals spread over a service.
#: `01`'s `VALID_DATASET_TRANSITIONS` set the pattern; the reasons here are the model's own.
#:
#: Three edges are worth reading twice:
#:
#: * **`draft → review` does not exist.** FR-MODEL-64 makes diagnostics the condition of
#:   `fitted` and `fitted` the condition of `review`, so a model reaching an approver
#:   without coefficients is not a state to refuse later — it is a state with no edge into
#:   it.
#: * **`review → fitted`, never `review → draft`.** `06` FR-GOV-13 returns a
#:   `changes_requested` artifact to `draft`; for a Model that would claim the numbers had
#:   been withdrawn, which R2 makes impossible. The pre-submission state of a Model is
#:   `fitted`. Amended in `06` FR-GOV-13, 2026-08-17, rather than diverged from silently.
#: * **`approved → archived` does not exist.** An approved model is a Rating Version's
#:   referent; archiving it would remove the referent while naming no replacement.
#:   Supersession names one, which is why it is the only edge out.
VALID_MODEL_TRANSITIONS: Final[dict[ModelStatus, frozenset[ModelStatus]]] = {
    ModelStatus.DRAFT: frozenset({ModelStatus.FITTED, ModelStatus.ARCHIVED}),
    ModelStatus.FITTED: frozenset({ModelStatus.REVIEW, ModelStatus.ARCHIVED}),
    ModelStatus.REVIEW: frozenset({ModelStatus.APPROVED, ModelStatus.FITTED}),
    ModelStatus.APPROVED: frozenset({ModelStatus.SUPERSEDED}),
    ModelStatus.SUPERSEDED: frozenset({ModelStatus.ARCHIVED}),
    ModelStatus.ARCHIVED: frozenset(),
}

#: `archived` is the only end state. A model returned from review is `fitted` again and can
#: be resubmitted, which is what makes FR-GOV-13's loop a loop.
TERMINAL_MODEL_STATUSES: Final[frozenset[ModelStatus]] = frozenset({ModelStatus.ARCHIVED})


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
    spec: ModelSpec
    spec_hash: str
    fit_result: FitResult | None = None
    #: `02` §4.8. Unmeetable during the spine — diagnostics did not exist — and enforced
    #: below now that they do. OQ-MODEL-8 cited this field as its own example of a
    #: declared-but-dead contract field.
    diagnostics_id: UUID | None = None
    dataset_version_id: UUID
    parent_model_id: UUID | None = None
    change_reason: str | None = None
    #: FR-MODEL-67's flags, **computed from the referents rather than stored**. A stored
    #: flag goes stale the moment `01` re-validates the dataset version, and the whole
    #: point of the flag is that it tracks the dataset rather than a snapshot of it.
    flags: tuple[ModelFlag, ...] = ()
    #: `02` §4.8. The open approval request, set when the model enters `review` and left in
    #: place afterwards: it is how a reader gets from an approved model to the decision and
    #: the comment behind it, which is the trail FR-GOV-14's pinning exists to leave.
    approval_request_id: UUID | None = None

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

    @model_validator(mode="after")
    def _the_fit_matches_the_specification(self) -> Model:
        """Both unions are on one artifact, so the pairing has to be stated somewhere.

        A `GbmSpec` beside a `GlmFitResult` is a model whose coefficient table describes a
        booster nobody fitted — and the coefficient table is what a rating basis is read
        from. Neither discriminator can see the other, so nothing but this refuses it.
        """
        if self.fit_result is not None and self.fit_result.model_type != self.spec.model_type:
            raise ValueError(
                f"model_type disagrees: the spec says {self.spec.model_type!r} and the fit "
                f"result says {self.fit_result.model_type!r}."
            )
        return self

    @model_validator(mode="after")
    def _a_fitted_model_has_its_diagnostics(self) -> Model:
        """`02` §4.8's other invariant: `status ≥ fitted` ⟹ `diagnostics_id` set.

        The spine enforced `fitted ⟹ fit_result` and left this one unstated, because
        diagnostics did not exist to point at. It is the stronger of the two: coefficients
        say what the model *is*, diagnostics say whether it is any good, and FR-MODEL-64
        makes the second the condition of leaving `draft`. A model that reached `review`
        with no diagnostics would be an approval request with no evidence.

        `archived` is excluded with `draft` for the same reason as above — it is a
        terminal state a model can be put into from anywhere, including from `draft`.
        """
        beyond_draft = self.status not in {ModelStatus.DRAFT, ModelStatus.ARCHIVED}
        if beyond_draft and self.diagnostics_id is None:
            raise ValueError(
                f"model {self.model_family_slug}@{self.version} is {self.status.value} "
                "with no diagnostics (`02` §4.8, FR-MODEL-49). Diagnostics are computed at "
                "fit time and are what `fitted` means."
            )
        return self


class SpecProblemKind(enum.StrEnum):
    """Why a Model Spec cannot be fitted (`02` FR-MODEL-44, FR-MODEL-81).

    A closed set, because the frontend renders each differently and an open string would
    make that a guess about wording.
    """

    DATASET_NOT_VALIDATED = "dataset_not_validated"
    FACTOR_MISSING = "factor_missing"
    FACTOR_PROHIBITED = "factor_prohibited"
    FACTOR_UNRESOLVABLE = "factor_unresolvable"
    SPLIT_MISSING = "split_missing"
    SPLIT_INVALID = "split_invalid"
    RESPONSE_MISSING = "response_missing"
    OFFSET_MISSING = "offset_missing"
    COMPLEXITY_LIMIT = "complexity_limit"
    #: FR-MODEL-44's *objective applicability* half, live from the GBM slice. A GBM spec
    #: naming an objective outside FR-MODEL-26's set, or a Custom Objective while none can
    #: exist, is unfittable — and `wf-01` D2 says the caller learns that before a Job is
    #: queued rather than from a job that fails three minutes in.
    OBJECTIVE_UNSUPPORTED = "objective_unsupported"


class SpecProblem(BaseModel):
    """One reason a spec was refused, in terms the caller can act on."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: SpecProblemKind
    message: str
    #: What the problem is about — a factor slug, a column name, a setting key. Named
    #: rather than described: "a factor is prohibited" sends the reader hunting, and the
    #: form that pins the error to a field needs something to pin it to.
    subject: str | None = None


class SpecValidation(BaseModel):
    """The answer to "may this be fitted?", without fitting it (FR-MODEL-44).

    Reported as a list rather than raised as the first failure. A spec builder that
    surfaced one error at a time would make a ten-factor spec a ten-round conversation,
    and `02` §5.3 asks for live validation as the form is edited.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ok: bool
    problems: tuple[SpecProblem, ...] = ()
    #: What the complexity gate measured, whether or not it fired — so a caller near a
    #: limit can see it coming rather than discovering it by crossing it.
    factor_count: int = Field(default=0, ge=0)
    estimated_parameter_count: int = Field(default=0, ge=0)
    exposure_per_parameter: float | None = None
    max_factor_count: int | None = None
    min_exposure_per_parameter: float | None = None

    @model_validator(mode="after")
    def _ok_means_no_problems(self) -> SpecValidation:
        """`ok` is derived, and must not be able to disagree with the list beside it.

        A payload saying `ok: true` with three problems is the kind of thing a screen
        renders as a green tick above a list of errors.
        """
        if self.ok and self.problems:
            raise ValueError(
                f"validation says ok with {len(self.problems)} problem(s): "
                f"{[p.kind.value for p in self.problems]}"
            )
        if not self.ok and not self.problems:
            raise ValueError("validation says not ok and names no problem")
        return self
