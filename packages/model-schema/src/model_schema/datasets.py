"""Datasets and their versions (`01` §4.1, §4.2).

> **`01` §1.3 — the single most important rule.** A Model may only be fitted on a Dataset
> Version whose status is `validated`. There is no override, no "force fit", and no admin
> bypass. If an actuary believes a failing rule is wrong, the rule is changed — and that
> change is reviewed and audited — the gate is not skipped.

Everything here exists to make that sentence enforceable rather than aspirational. The
status enum is closed, the transitions are data, and `validated` is reachable only through
a transition that demands a passing report with every warning acknowledged.

A Dataset Version is a **full snapshot** (FR-DATA-40, OQ-DATA-2 decided 2026-08-14): a
complete, independently validatable body of data, never a delta against its predecessor.
That is what lets a version be validated on its own terms years later.
"""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Annotated, Any, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.money import Currency, DecimalStr, MoneyMinor
from model_schema.profiles import SemanticType
from model_schema.refs import BlobRef

__all__ = [
    "TERMINAL_DATASET_STATUSES",
    "VALID_DATASET_TRANSITIONS",
    "DataDictionaryEntry",
    "Dataset",
    "DatasetKind",
    "DatasetLineage",
    "DatasetSplit",
    "DatasetStatus",
    "DatasetTable",
    "DatasetVersion",
    "LineageBuiltFrom",
    "LineageDependsOn",
    "LineageDerivedVersion",
    "LineageModel",
    "PiiClass",
    "RecordGrain",
    "SourceKind",
    "VersionTotals",
]


class SourceKind(enum.StrEnum):
    """Where data comes from (FR-DATA-1). Credentials are always a `secret:<slug>`
    reference, never a value (`07` FR-PLAT-25)."""

    UPLOAD = "upload"
    OBJECT_STORE = "object_store"
    SQL = "sql"
    PIPELINE = "pipeline"


class DatasetStatus(enum.StrEnum):
    DRAFT = "draft"
    VALIDATING = "validating"
    VALIDATED = "validated"
    FAILED = "failed"
    ARCHIVED = "archived"


class DatasetKind(enum.StrEnum):
    INGESTED = "ingested"
    DERIVED = "derived"


#: The lifecycle, as data rather than as scattered conditionals.
#:
#: `validated → validating` is the unusual edge and it is deliberate: FR-DATA-23 makes
#: validation re-runnable on an already-validated version, because a Rule Set can change
#: after the fact. If the new report fails, the version goes to `failed` — a dataset that
#: *was* good under an older rule set is not good now, and models fitted on it are the
#: reason anyone would want to know.
VALID_DATASET_TRANSITIONS: Final[dict[DatasetStatus, frozenset[DatasetStatus]]] = {
    DatasetStatus.DRAFT: frozenset({DatasetStatus.VALIDATING, DatasetStatus.ARCHIVED}),
    DatasetStatus.VALIDATING: frozenset(
        {DatasetStatus.VALIDATED, DatasetStatus.FAILED, DatasetStatus.DRAFT}
    ),
    DatasetStatus.VALIDATED: frozenset(
        {DatasetStatus.VALIDATING, DatasetStatus.ARCHIVED}
    ),
    DatasetStatus.FAILED: frozenset({DatasetStatus.VALIDATING, DatasetStatus.ARCHIVED}),
    DatasetStatus.ARCHIVED: frozenset(),
}

#: `archived` is the only end state. A `failed` version can be re-validated after the rule
#: set is corrected, which is the whole point of FR-DATA-23.
TERMINAL_DATASET_STATUSES: Final[frozenset[DatasetStatus]] = frozenset(
    {DatasetStatus.ARCHIVED}
)


class PiiClass(enum.StrEnum):
    """How sensitive a column is (`01` §4.1, FR-OVR-9, FR-DATA-13).

    The two strongest classes are not a warning label. A `direct_identifier` or
    `special_category` column is **refused for modelling use** — rating on a special
    category is unlawful in the UK/EU, and a direct identifier in a model is a
    re-identification risk that no amount of care downstream removes.
    """

    NONE = "none"
    PSEUDONYMOUS_KEY = "pseudonymous_key"
    QUASI_IDENTIFIER = "quasi_identifier"
    DIRECT_IDENTIFIER = "direct_identifier"
    SPECIAL_CATEGORY = "special_category"


#: The classes FR-OVR-9 and FR-DATA-13 refuse for modelling.
MODELLING_FORBIDDEN_PII: Final[frozenset[PiiClass]] = frozenset(
    {PiiClass.DIRECT_IDENTIFIER, PiiClass.SPECIAL_CATEGORY}
)


class RecordGrain(enum.StrEnum):
    """What one row of the dataset *is*.

    Recorded because every actuarial check downstream depends on it: "exposure > 0 and
    period-consistent" means something different per policy-year than per claim.
    """

    POLICY_EXPOSURE = "policy_exposure"
    POLICY_TERM = "policy_term"
    CLAIM = "claim"
    QUOTE = "quote"


class DataDictionaryEntry(BaseModel):
    """What one column means (`01` §4.1).

    The dictionary is authored, not inferred. A Profile says a column is 98 % distinct
    integers; only a person can say it is a policy id rather than a very granular rating
    factor, and only a person can say it is a special category.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    description: str = ""
    semantic_type: SemanticType | None = None
    pii_class: PiiClass = PiiClass.NONE
    unit: str | None = None
    reference_table: str | None = None


class Dataset(BaseModel):
    """A named body of data with versions (`01` §4.1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    slug: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")]

    #: The accountable party (FR-DATA-51). Non-null and with no default, so a projection
    #: that forgets it fails loudly rather than reporting a plausible null — and **not**
    #: derived from `workspace_id`, which would make every Dataset in a workspace equally
    #: owned and leave `06`'s review trails with no named subject to address.
    owner_id: UUID

    name: str = ""
    description: str | None = None

    line_of_business: str | None = None
    territory: str | None = None
    currency: Currency = "GBP"
    default_record_grain: RecordGrain | None = None

    data_dictionary: dict[str, DataDictionaryEntry] = Field(default_factory=dict)
    validation_rule_set_id: UUID | None = None
    latest_version: int | None = None

    #: The status of the version `latest_version` names (FR-DATA-50). Derived per request
    #: and stored on no row: a status column on `datasets` would be a second answer to
    #: "can I fit on this?", free to disagree with `DatasetVersion.status`, which §1.3
    #: makes the only one.
    latest_version_status: DatasetStatus | None = None

    #: When the most recently `validated` version finished validating — **not necessarily
    #: `latest_version`**. The badge answers *what state is the newest version in*; this
    #: answers *when was this Dataset last usable*, and FR-DATA-50 scopes them differently
    #: on purpose.
    last_validated_at: datetime | None = None

    #: Which version `last_validated_at` describes. FR-DATA-50: "where the two refer to
    #: different versions the list states which, so the pair cannot be read as one fact".
    last_validated_version: int | None = None

    created_at: datetime
    archived_at: datetime | None = None

    @property
    def modelling_forbidden_columns(self) -> tuple[str, ...]:
        """Columns FR-OVR-9 / FR-DATA-13 refuse to model on, in declaration order.

        A property rather than a stored field: it is a *consequence* of the dictionary,
        and storing it would let the two disagree after an edit.
        """
        return tuple(
            column
            for column, entry in self.data_dictionary.items()
            if entry.pii_class in MODELLING_FORBIDDEN_PII
        )

    @model_validator(mode="after")
    def _the_latest_version_and_its_status_travel_together(self) -> Dataset:
        if (self.latest_version is None) != (self.latest_version_status is None):
            raise ValueError(
                "latest_version and latest_version_status are one fact: a version with no "
                "status renders a blank badge, and a status with no version describes "
                "nothing"
            )
        return self

    @model_validator(mode="after")
    def _the_validation_date_and_its_version_travel_together(self) -> Dataset:
        if (self.last_validated_at is None) != (self.last_validated_version is None):
            raise ValueError(
                "last_validated_at and last_validated_version are one fact (FR-DATA-50): a "
                "date with no version cannot be distinguished from the latest version's"
            )
        return self



class DatasetTable(BaseModel):
    """One table within a version (`01` §4.2).

    `_rejected` is a table like any other — the quarantine FR-DATA-7 requires, stored with
    the version rather than discarded. A row that could not be parsed is evidence about the
    feed, and throwing it away is how a broken upstream export goes unnoticed for a quarter.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(pattern=r"^_?[a-z][a-z0-9_]*$")
    record_grain: str
    primary_key: tuple[str, ...] = ()
    row_count: Annotated[int, Field(ge=0)]
    blob: BlobRef | None = None
    pandera_schema_ref: str | None = None
    arrow_schema: dict[str, str] = Field(default_factory=dict)
    source_names: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Normalised column name to the header it came from (FR-DATA-5). Kept because "
            "normalisation is lossy and occasionally surprising: freMTPL2's `IDpol` "
            "becomes `i_dpol`, since the splitter reads it as `I` + `Dpol` — the same rule "
            "that correctly gives `HTTPServer` → `http_server`. Without the original, a "
            "user cannot tell which of their columns a rule is talking about."
        ),
    )


class VersionTotals(BaseModel):
    """The headline numbers, checked by validation and shown everywhere.

    Money is integer minor units and exposure is a decimal string (FR-OVR-7): a float
    exposure total silently disagrees with the sum of its parts, and the disagreement is
    exactly the kind of thing an actuary is asked to explain.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    exposure_years: DecimalStr
    claim_count: Annotated[int, Field(ge=0)] = 0
    claim_amount_minor: MoneyMinor = 0


class DatasetVersion(BaseModel):
    """An immutable versioned snapshot of policy, claims and exposure data (`01` §4.2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    dataset_id: UUID
    workspace_id: UUID
    version: Annotated[int, Field(ge=1)]
    status: DatasetStatus
    kind: DatasetKind = DatasetKind.INGESTED

    tables: tuple[DatasetTable, ...] = ()
    source_id: UUID | None = None
    source_fingerprint: dict[str, str] | None = None
    ingestion_run_id: UUID | None = None
    preparation_recipe_id: UUID | None = None

    period_from: date | None = None
    period_to: date | None = None
    totals: VersionTotals | None = None

    validation_report_id: UUID | None = None
    profile_id: UUID | None = None
    derived_from: dict[str, object] | None = None

    library_versions: dict[str, str] = Field(default_factory=dict)
    created_at: datetime

    @model_validator(mode="after")
    def _validated_requires_a_report(self) -> DatasetVersion:
        """`01` §4.2's first invariant, and §1.3's rule in shape form.

        A version cannot *claim* `validated` without naming the report that made it so.
        Whether that report passed and its warnings were acknowledged is checked by the
        service against the stored report — a shape cannot see another row — but a version
        with no report at all is refused here, at the cheapest possible point.
        """
        if self.status is DatasetStatus.VALIDATED and self.validation_report_id is None:
            raise ValueError(
                "a validated dataset version must name its validation report "
                "(`01` §4.2, FR-DATA-17)"
            )
        return self

    @model_validator(mode="after")
    def _derived_versions_name_their_parent(self) -> DatasetVersion:
        if self.kind is DatasetKind.DERIVED and not self.derived_from:
            raise ValueError("a derived version must set derived_from (`01` §4.2)")
        return self

    @model_validator(mode="after")
    def _period_is_ordered(self) -> DatasetVersion:
        if self.period_from and self.period_to and self.period_to < self.period_from:
            raise ValueError("period_to precedes period_from")
        return self

    @property
    def is_fittable(self) -> bool:
        """`01` §1.3: the only question the modelling module needs to ask.

        Exposed as a property so no caller has to remember which statuses count. There is
        exactly one, and it is not a judgement call.
        """
        return self.status is DatasetStatus.VALIDATED


class LineageBuiltFrom(BaseModel):
    """The version this one was built from, and the operation that built it (`01` §4.9).

    `None` on the wire when the version has no parent — a version an Ingestion Run
    created from a Source, and any `direction=down` response (§4.9's invariants).
    `parameters` is the derivation's parameters, read back from the parent's
    `derived_from["params"]`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    parent_version_id: UUID
    operation: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class LineageDerivedVersion(BaseModel):
    """A version derived from this one (`01` §4.9's `derived_versions` arm)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version_id: UUID
    version: int
    operation: str


class LineageModel(BaseModel):
    """A Model fitted on this version (`01` §4.9's `models` arm).

    Any status: a draft Model still references the version it was fitted on, and the
    blast radius FR-DATA-35 exists to compute (FR-DATA-23) does not stop at approval.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: UUID
    slug: str
    status: str


class LineageDependsOn(BaseModel):
    """What depends on this version (`01` §4.9).

    `rating_versions` and `monitoring_baselines` are declared and always empty — W9's
    and W27's arms, kept on the wire so a blast radius that silently omits two of the
    three downstream kinds cannot read as a blast radius of one (FR-DATA-35).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    derived_versions: list[LineageDerivedVersion] = Field(default_factory=list)
    models: list[LineageModel] = Field(default_factory=list)
    rating_versions: list[Any] = Field(default_factory=list)
    monitoring_baselines: list[Any] = Field(default_factory=list)


class DatasetLineage(BaseModel):
    """The lineage graph for one Dataset Version (`01` §4.9, FR-DATA-35)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version_id: UUID
    built_from: LineageBuiltFrom | None
    depends_on_this: LineageDependsOn


class DatasetSplit(BaseModel):
    """A named train/test split, recorded on the parent version (`01` FR-DATA-36).

    On the **parent**, not the parts, so that "trained on the same split" is one artifact
    two models cite rather than two derivations believed to match. `parts` maps a part name
    to the Derived Dataset Version holding its rows.

    At least two parts, always: a one-part split is a filter, and recording it as a split
    would let a model claim a holdout it never had.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    parent_version_id: UUID
    name: str
    method: str
    seed: int
    params: dict[str, Any] = Field(default_factory=dict)
    parts: dict[str, UUID] = Field(default_factory=dict)
    created_at: datetime | None = None

    @model_validator(mode="after")
    def _a_split_has_at_least_two_parts(self) -> DatasetSplit:
        if len(self.parts) < 2:
            raise ValueError(
                f"split {self.name!r} has {len(self.parts)} part(s). A one-part split is a "
                "filter; recorded as a split it would let a model claim a holdout it never "
                "had (FR-DATA-36)."
            )
        return self
