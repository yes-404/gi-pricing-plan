"""Dataset profiles and their comparison (`01` §4.7, FR-DATA-25/26/28).

A Profile is computed **once**, after ingestion, and read many times: by the validation
engine's distributional layer, by the factor workbench in `02`, and by anyone asking what
is in a dataset. FR-DATA-27 is explicit that the UI never recomputes one — two answers to
"what is the mean claim severity?" is one too many.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from model_schema.money import DecimalStr, MoneyMinor

__all__ = [
    "ColumnComparison",
    "ColumnProfile",
    "OneWayRow",
    "OneWaySummary",
    "Profile",
    "ProfileComparison",
    "SemanticType",
]


class SemanticType(enum.StrEnum):
    """What a column *means*, inferred separately from its dtype (FR-DATA-25).

    A dtype says `int32`; a semantic type says whether that is a policy id, a vehicle
    group, or an age. The distinction decides whether a one-way summary is meaningful —
    banding a policy id produces a chart with five million bars.
    """

    IDENTIFIER = "identifier"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    CONTINUOUS = "continuous"
    DATE = "date"
    MONEY = "money"
    BOOLEAN = "boolean"


class ColumnProfile(BaseModel):
    """Per-column statistics (`01` §4.7)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    dtype: str
    semantic_type: SemanticType
    row_count: Annotated[int, Field(ge=0)]
    null_count: Annotated[int, Field(ge=0)]
    null_rate: Annotated[float, Field(ge=0.0, le=1.0)]
    distinct_count: Annotated[int, Field(ge=0)]

    minimum: float | None = None
    maximum: float | None = None
    mean: float | None = None
    std: float | None = None
    quantiles: dict[str, float] = Field(default_factory=dict)
    #: Top levels by count, for a categorical column. Capped at 20 (FR-DATA-25) — a
    #: high-cardinality column would otherwise put its whole domain in an artifact.
    top_levels: tuple[tuple[str, int], ...] = ()


class OneWayRow(BaseModel):
    """One level of a one-way summary (FR-DATA-26).

    Money is integer minor units and exposure a decimal string (FR-OVR-7). Frequency and
    severity are ratios and stay floats: they are statistics, not amounts, and rounding
    them to minor units would lose the precision the confidence interval is expressing.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: str
    exposure_years: DecimalStr
    claim_count: Annotated[int, Field(ge=0)] = 0
    claim_amount_minor: MoneyMinor = 0

    frequency: float | None = None
    frequency_ci: tuple[float, float] | None = None
    severity_minor: float | None = None
    severity_ci: tuple[float, float] | None = None
    burning_cost_minor: float | None = None


class OneWaySummary(BaseModel):
    """A candidate rating column summarised by level (FR-DATA-26).

    Computed here, once, because `02`'s factor workbench and the pricing actuary looking at
    a dataset must see the same numbers — and because recomputing per request is the
    difference between an interactive screen and a spinner.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    column: str
    banding: str = "levels"
    rows: tuple[OneWayRow, ...] = ()


class Profile(BaseModel):
    """The profile artifact for one Dataset Version (`01` §4.7)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    dataset_version_id: UUID
    computed_at: datetime
    row_count: Annotated[int, Field(ge=0)]
    columns: tuple[ColumnProfile, ...] = ()
    one_ways: tuple[OneWaySummary, ...] = ()
    library_versions: dict[str, str] = Field(default_factory=dict)

    def column(self, name: str) -> ColumnProfile | None:
        return next((c for c in self.columns if c.name == name), None)


class ColumnComparison(BaseModel):
    """How one column moved between two versions (FR-DATA-28)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    column: str
    psi: float | None = None
    mean_shift: float | None = None
    null_rate_shift: float | None = None
    new_levels: tuple[str, ...] = ()
    vanished_levels: tuple[str, ...] = ()


class ProfileComparison(BaseModel):
    """The comparison the distributional validation layer consumes (FR-DATA-28).

    The same computation serves an on-demand UI comparison and the `VR-DST-*` rules, so a
    rule's verdict and the screen an actuary is looking at cannot disagree.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    current_version_id: UUID
    reference_version_id: UUID
    columns: tuple[ColumnComparison, ...] = ()
    row_count_ratio: float | None = None

    def column(self, name: str) -> ColumnComparison | None:
        return next((c for c in self.columns if c.column == name), None)
