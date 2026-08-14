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
from typing import Annotated, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.money import DecimalStr, MoneyMinor
from model_schema.refs import BlobRef

__all__ = [
    "TERMINAL_DATASET_STATUSES",
    "VALID_DATASET_TRANSITIONS",
    "DatasetKind",
    "DatasetStatus",
    "DatasetTable",
    "DatasetVersion",
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
