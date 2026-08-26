"""The Peril Structure and its reconciliation (`02` §3.9, §4.10, FR-MODEL-58..61, 74).

A Model answers one question about one peril. A **Peril Structure** is the declarative
composition that turns a set of them into a risk premium — and it is what
`03-rating-engine.md` references, precisely so that a Rating Version cites one auditable
object rather than a scatter of individual models (FR-MODEL-61).

Four things §4.10's example does not say, decided here and recorded in the spec with the
same date:

* **`status` and `ratio` on the reconciliation are derived, not stored.** §4.10 prints both
  beside the numbers they follow from. Two statements of one fact disagree eventually, and
  this one is the evidence an approval cites — the same correction §4.9's `kinds` already
  carries.
* **The total is the sum of the per-peril figures, and that is checked.** FR-MODEL-58 sums
  over perils; a total that is not the sum is a third number nobody can source. The
  per-peril breakdown is also where FR-MODEL-74's treatment is stated, which is why it is
  required rather than decorative.
* **Every treatment but `none` carries its calibration evidence.** FR-MODEL-59 says
  "whatever is chosen is recorded with its calibration evidence"; a restoration loading of
  1.043 with nothing behind it asks an approver to accept a number because it is written
  down.
* **A structure has a lifecycle of its own**, and `draft → review` is not an edge in it.
  FR-MODEL-61 makes the structure approvable and FR-MODEL-60 makes the reconciliation its
  evidence, so a structure reaching an approver without one is not a state to refuse later —
  it is a state with no edge into it. `VALID_MODEL_TRANSITIONS` reached the same shape from
  the same argument about diagnostics.

**`separate_model` and `flat_loading` are contract-level from the start and computed by
nothing yet** (`pricing_core.modelling.perils` refuses them by name). FR-MODEL-59 names all
four kinds, and an enum admitting two of them would be a second contract change the day an
excess-layer model exists.
"""

from __future__ import annotations

import datetime as _datetime
import enum
from decimal import Decimal
from typing import Annotated, Any, Final, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from model_schema.money import DecimalStr, MoneyMinor
from model_schema.refs import ArtifactRef, BlobRef, Slug

__all__ = [
    "TOLERANCE_QUANTUM",
    "VALID_PERIL_STRUCTURE_TRANSITIONS",
    "ExcludedPeril",
    "LargeLossKind",
    "LargeLossTreatment",
    "PerilComponent",
    "PerilMethod",
    "PerilStructure",
    "PerilStructureStatus",
    "ReconciledPeril",
    "Reconciliation",
    "ReconciliationStatus",
]

#: `ratio` is quantised so that two runs of the same reconciliation render identically and a
#: stored artifact compares equal to a recomputed one. Six places is well inside the
#: precision any declared tolerance is written to.
TOLERANCE_QUANTUM: Final[Decimal] = Decimal("0.000001")

#: A peril code as it appears in the dataset. Upper snake case rather than a slug: these are
#: the dataset's own column values (`AD`, `TP_BI`, `WINDSCREEN`), not platform artifacts.
PerilCode = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]{0,31}$")]


class PerilMethod(enum.StrEnum):
    """FR-MODEL-58's two routes to a peril's cost."""

    FREQUENCY_SEVERITY = "frequency_severity"
    BURNING_COST = "burning_cost"


class LargeLossKind(enum.StrEnum):
    """FR-MODEL-59's four treatments."""

    NONE = "none"
    CAPPED = "capped"
    SEPARATE_MODEL = "separate_model"
    FLAT_LOADING = "flat_loading"


class ReconciliationStatus(enum.StrEnum):
    PASS = "pass"
    FAIL = "fail"


class PerilStructureStatus(enum.StrEnum):
    """The structure's own lifecycle (FR-MODEL-61).

    `reconciled` is this artifact's `fitted`: the state in which its evidence exists.
    """

    DRAFT = "draft"
    RECONCILED = "reconciled"
    REVIEW = "review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


#: FR-MODEL-61's lifecycle, as data. Mirrors `VALID_MODEL_TRANSITIONS` deliberately — the
#: two artifacts are approved by the same machine (`06` FR-GOV-9), and a lifecycle that
#: differed without a reason would be a second set of rules to learn.
#:
#: * **`draft → review` does not exist** — see the module docstring.
#: * **`review → reconciled`, never `review → draft`.** `06` FR-GOV-13 returns a
#:   `changes_requested` artifact to `draft`; here that would claim the reconciliation had
#:   been withdrawn, when what was questioned is the composition it measured.
#: * **`approved → archived` does not exist.** An approved structure is a Rating Version's
#:   referent (FR-MODEL-61); archiving it removes the referent while naming no replacement.
VALID_PERIL_STRUCTURE_TRANSITIONS: Final[
    dict[PerilStructureStatus, frozenset[PerilStructureStatus]]
] = {
    PerilStructureStatus.DRAFT: frozenset(
        {PerilStructureStatus.RECONCILED, PerilStructureStatus.ARCHIVED}
    ),
    PerilStructureStatus.RECONCILED: frozenset(
        {PerilStructureStatus.REVIEW, PerilStructureStatus.ARCHIVED}
    ),
    PerilStructureStatus.REVIEW: frozenset(
        {PerilStructureStatus.APPROVED, PerilStructureStatus.RECONCILED}
    ),
    PerilStructureStatus.APPROVED: frozenset({PerilStructureStatus.SUPERSEDED}),
    PerilStructureStatus.SUPERSEDED: frozenset({PerilStructureStatus.ARCHIVED}),
    PerilStructureStatus.ARCHIVED: frozenset(),
}

#: `archived` is the only end state, for the reason it is the Model's.
TERMINAL_PERIL_STRUCTURE_STATUSES: Final[frozenset[PerilStructureStatus]] = frozenset(
    {PerilStructureStatus.ARCHIVED}
)


class LargeLossTreatment(BaseModel):
    """FR-MODEL-59 — how large losses are handled for one peril.

    Modelled as one type with a `kind` discriminator and per-kind requirements rather than
    four types in a union: the four share `evidence_blob`, every caller reads `kind` first,
    and a union would put the shared requirement in four places.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: LargeLossKind

    #: `capped`
    cap_minor: MoneyMinor | None = None
    restoration_loading: DecimalStr | None = Field(
        default=None,
        description="Multiplier restoring the capped mean. Never below 1 (FR-MODEL-59).",
    )

    #: `separate_model`
    excess_model: ArtifactRef | None = None
    attachment_minor: MoneyMinor | None = None

    #: `flat_loading`
    loading_factor: DecimalStr | None = None

    #: FR-MODEL-59's "recorded with its calibration evidence". Required for every kind that
    #: has something to calibrate.
    evidence_blob: BlobRef | None = None

    @model_validator(mode="after")
    def _fields_match_the_kind(self) -> Self:
        required: dict[LargeLossKind, tuple[str, ...]] = {
            LargeLossKind.NONE: (),
            LargeLossKind.CAPPED: ("cap_minor", "restoration_loading", "evidence_blob"),
            LargeLossKind.SEPARATE_MODEL: (
                "excess_model",
                "attachment_minor",
                "evidence_blob",
            ),
            LargeLossKind.FLAT_LOADING: ("loading_factor", "evidence_blob"),
        }
        parameters = (
            "cap_minor",
            "restoration_loading",
            "excess_model",
            "attachment_minor",
            "loading_factor",
            "evidence_blob",
        )
        needed = required[self.kind]
        for name in needed:
            if getattr(self, name) is None:
                raise ValueError(
                    f"a {self.kind.value!r} large-loss treatment requires {name!r} "
                    "(FR-MODEL-59)"
                )
        for name in parameters:
            if name not in needed and getattr(self, name) is not None:
                raise ValueError(
                    f"{name!r} has no meaning for a {self.kind.value!r} large-loss "
                    "treatment; a parameter that is read by nothing reads as one that is"
                )
        if self.restoration_loading is not None and self.restoration_loading < 1:
            raise ValueError(
                f"restoration_loading {self.restoration_loading} is below 1. Restoration "
                "puts the capped mean back (FR-MODEL-59); below 1 it caps a second time"
            )
        if self.loading_factor is not None and self.loading_factor <= 0:
            raise ValueError("loading_factor must be positive (FR-MODEL-59)")
        return self


class PerilComponent(BaseModel):
    """One peril's route to a cost (FR-MODEL-58).

    Model references are pinned by version because `ArtifactRef` carries `@version` (ID-3)
    and artifacts are immutable (FR-OVR-1) — which is what makes FR-MODEL-58's "pinned by
    version" structural rather than a rule someone has to remember.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    peril: PerilCode
    method: PerilMethod
    frequency_model: ArtifactRef | None = None
    severity_model: ArtifactRef | None = None
    burning_cost_model: ArtifactRef | None = None
    large_loss: LargeLossTreatment

    @model_validator(mode="after")
    def _models_match_the_method(self) -> Self:
        required: dict[PerilMethod, tuple[str, ...]] = {
            PerilMethod.FREQUENCY_SEVERITY: ("frequency_model", "severity_model"),
            PerilMethod.BURNING_COST: ("burning_cost_model",),
        }
        needed = required[self.method]
        for name in needed:
            if getattr(self, name) is None:
                raise ValueError(
                    f"peril {self.peril}: a {self.method.value!r} peril requires "
                    f"{name!r} (FR-MODEL-58)"
                )
        for name in ("frequency_model", "severity_model", "burning_cost_model"):
            if name not in needed and getattr(self, name) is not None:
                raise ValueError(
                    f"peril {self.peril}: {name!r} has no meaning for a "
                    f"{self.method.value!r} peril. Two routes to one peril's cost is two "
                    "answers to what it costs"
                )
        for name in needed:
            ref: ArtifactRef = getattr(self, name)
            if ref.type != "model":
                raise ValueError(
                    f"peril {self.peril}: {name!r} references a {ref.type!r}, not a model"
                )
        return self


class ExcludedPeril(BaseModel):
    """A peril present in the data and deliberately not modelled (FR-MODEL-60).

    The reason is required and non-blank. "Every peril is either modelled or explicitly
    excluded with a reason" is the requirement; an exclusion with an empty reason satisfies
    its letter and none of its purpose.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    peril: PerilCode
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def _reason_is_not_blank(self) -> Self:
        if not self.reason.strip():
            raise ValueError(
                f"peril {self.peril}: an exclusion reason of whitespace is an exclusion "
                "with no reason (FR-MODEL-60)"
            )
        return self


class ReconciledPeril(BaseModel):
    """One peril's contribution to the modelled total, with its treatment (FR-MODEL-74)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    peril: PerilCode
    large_loss_kind: LargeLossKind
    modelled_burning_cost: MoneyMinor = Field(ge=0)


class Reconciliation(BaseModel):
    """FR-MODEL-60's persisted coherence check, FR-MODEL-74's treatment statement.

    The modelled figure is **after** restoration: a capped model reconciled against uncapped
    observed data without restoring its mean looks like a modelling error rather than an
    intended adjustment, which is the whole of FR-MODEL-74.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID
    part: str = Field(min_length=1)
    perils: tuple[ReconciledPeril, ...] = Field(min_length=1)
    observed_burning_cost: MoneyMinor
    modelled_burning_cost: MoneyMinor = Field(ge=0)
    tolerance: DecimalStr = Field(
        description="Declared fractional tolerance on |ratio - 1| (FR-MODEL-60)."
    )
    computed_at: _datetime.datetime

    @model_validator(mode="before")
    @classmethod
    def _drop_derived(cls, data: Any) -> Any:
        """Discard any incoming `ratio` or `status` rather than refusing them.

        They are `computed_field`s, so they **are** serialised — a caller reading a
        reconciliation gets the verdict without reimplementing the rounding rule, and
        `02` §4.10 shows both. That makes them appear in any payload round-tripped back
        through this type, which `extra="forbid"` would otherwise reject.

        Dropping rather than comparing is deliberate: a stored or hand-edited `ratio` then
        has no way to be believed, which is the same guarantee as never storing it, without
        making every consumer derive it. `TransparencyArtifact.kinds` reached the other
        answer — a plain property — because nothing needs it on the wire.
        """
        if isinstance(data, dict):
            data = {k: v for k, v in data.items() if k not in {"ratio", "status"}}
        return data

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ratio(self) -> Decimal:
        """Modelled over observed. Derived, so it cannot disagree with its own inputs."""
        return (
            Decimal(self.modelled_burning_cost)
            / Decimal(self.observed_burning_cost)
        ).quantize(TOLERANCE_QUANTUM)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status(self) -> ReconciliationStatus:
        """FR-MODEL-60's verdict, derived from the ratio and the *declared* tolerance."""
        return (
            ReconciliationStatus.PASS
            if abs(self.ratio - 1) <= self.tolerance
            else ReconciliationStatus.FAIL
        )

    @model_validator(mode="after")
    def _coherent(self) -> Self:
        if self.observed_burning_cost <= 0:
            raise ValueError(
                "observed_burning_cost must be positive: a ratio needs a "
                "denominator, and a holdout with no observed cost reconciles nothing "
                "(FR-MODEL-60)"
            )
        if self.tolerance <= 0:
            raise ValueError(
                "tolerance must be positive; a tolerance of zero passes only an exact "
                "match, which no fitted model produces (FR-MODEL-60)"
            )
        total = sum(p.modelled_burning_cost for p in self.perils)
        if total != self.modelled_burning_cost:
            raise ValueError(
                f"modelled_burning_cost {self.modelled_burning_cost} is not "
                f"the sum of the per-peril figures ({total}). FR-MODEL-58 sums over "
                "perils; a total that is not the sum is a third number"
            )
        seen = {p.peril for p in self.perils}
        if len(seen) != len(self.perils):
            raise ValueError("a peril appears twice in the reconciliation")
        return self


class PerilStructure(BaseModel):
    """FR-MODEL-58..61 — the composition, its coherence and its lifecycle."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: Slug
    version: int = Field(ge=1)
    perils: tuple[PerilComponent, ...] = Field(min_length=1)
    excluded_perils: tuple[ExcludedPeril, ...] = ()
    reconciliation: Reconciliation | None = None
    status: PerilStructureStatus = PerilStructureStatus.DRAFT
    created_at: _datetime.datetime

    @property
    def ref(self) -> ArtifactRef:
        """The canonical `peril_structure:{slug}@{version}` (ID-3)."""
        return ArtifactRef(type="peril_structure", slug=self.slug, version=self.version)

    @model_validator(mode="after")
    def _coherent(self) -> Self:
        modelled = [p.peril for p in self.perils]
        duplicates = {p for p in modelled if modelled.count(p) > 1}
        if duplicates:
            raise ValueError(
                f"peril(s) {sorted(duplicates)} appear more than once. Each peril has one "
                "route to its cost (FR-MODEL-58)"
            )
        excluded = [p.peril for p in self.excluded_perils]
        duplicate_exclusions = {p for p in excluded if excluded.count(p) > 1}
        if duplicate_exclusions:
            raise ValueError(f"peril(s) {sorted(duplicate_exclusions)} are excluded twice")
        both = sorted(set(modelled) & set(excluded))
        if both:
            raise ValueError(
                f"peril(s) {both} are both modelled and excluded. FR-MODEL-60 asks for "
                "each peril to be one or the other; being both leaves the reader unable "
                "to say whether its cost is in the total"
            )
        if (
            self.status
            in {
                PerilStructureStatus.RECONCILED,
                PerilStructureStatus.REVIEW,
                PerilStructureStatus.APPROVED,
            }
            and self.reconciliation is None
        ):
            raise ValueError(
                f"a {self.status.value!r} structure carries its reconciliation "
                "(FR-MODEL-60). It is the evidence the approval policy names, so a "
                "structure in review without one is an approval with nothing to read"
            )
        return self
