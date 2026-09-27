"""Dataset profiles and their comparison (`01` §4.7, FR-60/61/63).

A Profile is computed **once**, after ingestion, and read many times: by the validation
engine's distributional layer, by the factor workbench in `02`, and by anyone asking what
is in a dataset. FR-62 is explicit that the UI never recomputes one — two answers to
"what is the mean claim severity?" is one too many.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.money import DecimalStr, MoneyMinor

__all__ = [
    "ColumnComparison",
    "ColumnProfile",
    "Histogram",
    "LevelCount",
    "OneWayRow",
    "OneWaySummary",
    "Profile",
    "ProfileComparison",
    "SemanticType",
]


class SemanticType(enum.StrEnum):
    """What a column *means*, inferred separately from its dtype (FR-60).

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


class Histogram(BaseModel):
    """The binned distribution of a numeric column (`01` §4.7, FR-65).

    Bin *edges* rather than a bin width, because the last bin is closed and the others are
    half-open: `[e0, e1) … [e(n-1), en]`. A reader given only a width has to guess which
    end carries the maximum, and the two profiling engines would guess differently.

    `exposure` is optional and, when present, holds one exact decimal weight per bin
    (FR-10). A count histogram of an exposure-weighted book overstates the tail: a bin
    of 200 policies each on risk a fortnight is not the same risk as 200 policies on risk a
    year, and pricing reads the second.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    edges: tuple[float, ...] = ()
    counts: tuple[Annotated[int, Field(ge=0)], ...] = ()
    exposure: tuple[DecimalStr, ...] = ()

    @model_validator(mode="after")
    def _edges_bound_the_bins(self) -> Histogram:
        if len(self.edges) != len(self.counts) + 1:
            raise ValueError(
                "a histogram needs one more edge than it has bins "
                f"({len(self.edges)} edges, {len(self.counts)} counts)"
            )
        if any(b <= a for a, b in zip(self.edges, self.edges[1:], strict=False)):
            raise ValueError("histogram edges must be strictly increasing")
        if self.exposure and len(self.exposure) != len(self.counts):
            raise ValueError(
                "a histogram with exposure needs one exposure weight per bin "
                f"({len(self.exposure)} weights, {len(self.counts)} bins)"
            )
        return self


class LevelCount(BaseModel):
    """One level of `ColumnProfile.top_levels` (FR-60, FR-66).

    The authored contract (`docs/contracts/schemas/profile.schema.json`) has declared this
    shape since Phase 0 — `{level, count, exposure_years}`, only `level` and `count`
    required — while the model carried an unnamed `(str, int)` pair with no exposure
    weight. FR-66 closes that gap on the model-schema side.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: `None` is a genuine top-level category — a SQL NULL, not the string `"null"`. The
    #: contract declares `["string", "null"]`; collapsing a missing level to the literal
    #: string, as the engines' current `str(level)` coercion does, would make a real gap
    #: in the data indistinguishable from a level someone actually recorded as "null".
    level: str | None
    count: Annotated[int, Field(ge=0)]
    #: Absent means the version carried no exposure column at all; zero means this level
    #: carries no exposure. A profile that cannot tell those two apart cannot be read for
    #: a pricing decision — so this is optional, never defaulted to zero.
    #: Refusing a float is `DecimalStr`'s own behaviour since `OQ-547` was decided
    #: (2026-08-19). This field carried a hand-written validator doing it alone until then;
    #: the type now does it for all 11 of them, so the validator is gone rather than
    #: duplicated.
    exposure_years: DecimalStr | None = None


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
    #: Present for a numeric, non-identifier column only (FR-65). A histogram of a
    #: policy id is five million bars, and a histogram of a categorical column is what
    #: `top_levels` already is.
    histogram: Histogram | None = None
    #: Top levels by count, for a categorical column. Capped at 20 (FR-60) — a
    #: high-cardinality column would otherwise put its whole domain in an artifact. The
    #: cap is enforced here, in the model, not only honoured by the engines that populate
    #: it (FR-66) — a limit declared in one of two places is not actually enforced.
    top_levels: Annotated[tuple[LevelCount, ...], Field(max_length=20)] = ()


class OneWayRow(BaseModel):
    """One level of a one-way summary (FR-61).

    Money is integer minor units and exposure a decimal string (FR-10). Frequency,
    `mean_severity` and `mean_burning_cost` are ratios and stay floats: they are
    statistics, not amounts, and rounding them to minor units would lose the precision
    the confidence interval is expressing (FR-64).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: str
    exposure_years: DecimalStr
    claim_count: Annotated[int, Field(ge=0)] = 0
    claim_amount_minor: MoneyMinor = 0

    frequency: float | None = None
    frequency_ci: tuple[float, float] | None = None
    mean_severity: float | None = None
    severity_ci: tuple[float, float] | None = None
    mean_burning_cost: float | None = None


class OneWaySummary(BaseModel):
    """A candidate rating column summarised by level (FR-61).

    Computed here, once, because `02`'s factor workbench and the pricing actuary looking at
    a dataset must see the same numbers — and because recomputing per request is the
    difference between an interactive screen and a spinner.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    column: str
    banding: str = "levels"
    rows: tuple[OneWayRow, ...] = ()


class Profile(BaseModel):
    """The profile artifact for one Dataset Version (`01` §4.7, FR-60/61/62)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    dataset_version_id: UUID
    computed_at: datetime
    #: The Job that produced this Profile (FR-6's `produced_by_job_id`), matching the
    #: convention every other per-Job artifact in this repository carries directly —
    #: `Diagnostics`, `Backtest`, `ModelComparison` and `TransparencyArtifact` all declare
    #: their own `job_id: UUID | None`. `None` for a profile built outside a Job (a test
    #: fixture, a notebook).
    job_id: UUID | None = None
    row_count: Annotated[int, Field(ge=0)]
    columns: tuple[ColumnProfile, ...] = ()
    one_ways: tuple[OneWaySummary, ...] = ()
    #: The column the one-ways in `one_ways` were weighted by (FR-61). Recorded on the
    #: artifact so a reader of `one_ways` alone — without the Job that produced it — can
    #: tell what "exposure" meant for this profile.
    weight_column: str = "exposure_years"
    library_versions: dict[str, str] = Field(default_factory=dict)

    def column(self, name: str) -> ColumnProfile | None:
        return next((c for c in self.columns if c.name == name), None)


class ColumnComparison(BaseModel):
    """How one column moved between two versions (FR-63)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    column: str
    psi: float | None = None
    mean_shift: float | None = None
    null_rate_shift: float | None = None
    new_levels: tuple[str, ...] = ()
    vanished_levels: tuple[str, ...] = ()


class ProfileComparison(BaseModel):
    """The comparison the distributional validation layer consumes (FR-63).

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
