"""The Dislocation Run's spec and result (03 §4.6, §5.2; FR-263, FR-264).

WK-673 Slice 2 defines the run without its attribution part; Slice 3 adds `derived_changes`,
`change_groups`, `attribution` and `attribution_summary` (PL-1267, "Deviation from the adopted
cut"). Money is integer minor units; percentages and shares are derived views (03 §4.6), so
they are floats here and null where their denominator is zero (RL-1402 S5).
"""

from __future__ import annotations

from datetime import date
from itertools import pairwise
from typing import Annotated, Final, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.money import DecimalStr, MoneyMinor
from model_schema.refs import ArtifactRef
from model_schema.scoring import LadderRungName

_FROZEN = ConfigDict(frozen=True, extra="forbid")

#: The fixed quantile set of a run's `abs_change_pct_quantiles` (03 §4.6, RL-1504 T7): the keys
#: are these strings, "1" the largest absolute change. The `rating_version` policy entry's
#: `approximation_deviation.quantile` must be one of them (06 §4.2).
ABS_CHANGE_PCT_QUANTILE_KEYS: Final = ("0.5", "0.9", "0.95", "0.99", "0.999", "1")
_Share = Annotated[float, Field(ge=0, le=1)]
_Count = Annotated[int, Field(ge=0)]


class ChangeGroup(BaseModel):
    """One analyst group of derived changes (FR-1399); partition-checked by Slice 3."""

    model_config = _FROZEN
    name: str
    changes: Annotated[list[str], Field(min_length=1)]


class DislocationSpec(BaseModel):
    """What a run compares and how it reports (03 §5.2's types paragraph, RL-1394 T7)."""

    model_config = _FROZEN
    baseline_ref: ArtifactRef
    candidate_ref: ArtifactRef
    portfolio_dataset_version_id: UUID
    purpose: Literal["new_business", "renewal"]
    as_at: date
    segments: list[str] = []
    band_edges_pct: Annotated[list[DecimalStr], Field(min_length=1)]
    mover_threshold_pct: DecimalStr
    change_groups: Annotated[list[ChangeGroup], Field(max_length=6)] | None = None
    #: FR-224's exact-mode baseline (RL-1504 item 8): when `"exact"`, the run's baseline is
    #: the candidate's own Rating Version compiled in `exact` mode (ephemeral, FR-1398), so
    #: `baseline_ref` and `candidate_ref` name one version and no attribution is run.
    baseline_mode_override: Literal["exact"] | None = None

    @model_validator(mode="after")
    def _exact_override_names_one_version(self) -> Self:
        if self.baseline_mode_override is not None and self.baseline_ref != self.candidate_ref:
            raise ValueError(
                "baseline_mode_override applies to one version: baseline_ref and candidate_ref "
                "must be equal (FR-224, RL-1504 item 8)"
            )
        return self

    @model_validator(mode="after")
    def _edges_increase_and_threshold_positive(self) -> Self:
        if len(set(self.segments)) != len(self.segments):
            raise ValueError("segments must be distinct")  # DP-S2-6
        edges = self.band_edges_pct
        if any(b <= a for a, b in pairwise(edges)):
            raise ValueError("band_edges_pct must be strictly increasing")
        if self.mover_threshold_pct <= 0:
            raise ValueError("mover_threshold_pct must be positive")
        return self


class DislocationTotals(BaseModel):
    model_config = _FROZEN
    baseline_premium_minor: MoneyMinor
    candidate_premium_minor: MoneyMinor
    change_pct: float | None  # required, null when the denominator is 0 (DP-S2-3)


class DislocationOutcomes(BaseModel):
    """Each policy once by its two outcomes; the first five sum to policy_count (DP-S2-2)."""

    model_config = _FROZEN
    quoted_both: _Count
    quoted_to_declined: _Count
    declined_to_quoted: _Count
    declined_both: _Count
    error: _Count
    zero_baseline: _Count
    negative_baseline: _Count


class DislocationBand(BaseModel):
    model_config = _FROZEN
    band: str
    policies: _Count
    exposure_share: _Share | None
    mean_change_pct: float | None


class SegmentSlice(BaseModel):
    model_config = _FROZEN
    factor: str
    level: str | None  # required; null is a level (DP-S2-6)
    policies: _Count
    mean_change_pct: float | None
    exposure_share: _Share | None = None


class RungContribution(BaseModel):
    model_config = _FROZEN
    rung: LadderRungName
    contribution_pct: float | None


class ErrorSample(BaseModel):
    model_config = _FROZEN
    quote_id: str


class ErrorTally(BaseModel):
    model_config = _FROZEN
    code: str
    count: Annotated[int, Field(ge=1)]
    sample: Annotated[list[ErrorSample], Field(max_length=10)] | None = None


DeltaKind = Literal[
    "pin",
    "step_added",
    "step_removed",
    "step_changed",
    "table_repointed",
    "input_field",
    "output",
]


class BundleDelta(BaseModel):
    """One derived change between baseline and candidate (FR-1399)."""

    model_config = _FROZEN
    id: str
    kind: DeltaKind
    description: str


class AttributionItem(BaseModel):
    """One change group's Shapley part of record and its isolated and cumulative views (FR-266)."""

    model_config = _FROZEN
    group: str
    shapley_minor: MoneyMinor | None
    isolated_minor: MoneyMinor
    cumulative_minor: MoneyMinor
    mean_change_pct: float | None
    cumulative_change_pct: float | None = None


class AttributionSummary(BaseModel):
    """Method, totals, S and R, and the subset bundles compiled (FR-266, FR-1397, FR-1398)."""

    model_config = _FROZEN
    method: Literal["shapley", "order_dependent"]
    total_change_minor: MoneyMinor
    residual_minor: MoneyMinor
    order_sensitivity_lower_bound: DecimalStr | None
    residual_share: DecimalStr | None
    orders_sampled: Annotated[int, Field(ge=2)] | None
    subset_bundle_count: _Count
    subset_bundle_hashes: list[str]
    subset_valuation: Literal["rerate", "ladder_replay"]
    replay_fell_back: bool


class Attribution(BaseModel):
    """What `attribute` returns: the four attribution fields of a Dislocation Run (03 §5.2)."""

    model_config = _FROZEN
    derived_changes: list[BundleDelta]
    change_groups: Annotated[list[ChangeGroup], Field(max_length=6)]
    attribution: list[AttributionItem]
    attribution_summary: AttributionSummary


class DislocationRun(BaseModel):
    """03 §4.6; the four attribution fields are present together or not at all."""

    model_config = _FROZEN
    baseline_ref: ArtifactRef
    candidate_ref: ArtifactRef
    portfolio_dataset_version_id: UUID
    job_id: UUID | None = None
    policy_count: _Count
    exposure_years: DecimalStr
    totals: DislocationTotals
    outcomes: DislocationOutcomes
    distribution: Annotated[list[DislocationBand], Field(min_length=1)]
    by_segment: list[SegmentSlice] = []
    by_ladder_rung: list[RungContribution] = []
    largest_movers_blob: str | None = None
    errors: list[ErrorTally] = []
    derived_changes: list[BundleDelta] | None = None
    change_groups: Annotated[list[ChangeGroup], Field(max_length=6)] | None = None
    attribution: list[AttributionItem] | None = None
    attribution_summary: AttributionSummary | None = None
    #: FR-224's observed figure (03 §4.6, RL-1504 T7): nearest-rank quantiles of the banded
    #: set's absolute percentage changes, decimal strings rounded once to 6 places toward +inf,
    #: every key null for an empty banded set. All six keys or none (a run before this field).
    abs_change_pct_quantiles: dict[str, DecimalStr | None] | None = None

    @model_validator(mode="after")
    def _quantile_keys_are_the_fixed_set(self) -> Self:
        # A set, not a sequence: the run is stored as JSONB, which returns an object's keys
        # shortest first ("1" before "0.5"), and a JSON object has no key order to hold.
        if self.abs_change_pct_quantiles is not None and (
            set(self.abs_change_pct_quantiles) != set(ABS_CHANGE_PCT_QUANTILE_KEYS)
        ):
            raise ValueError(
                "abs_change_pct_quantiles must hold exactly the keys "
                f"{list(ABS_CHANGE_PCT_QUANTILE_KEYS)} (03 §4.6)"
            )
        return self

    @model_validator(mode="after")
    def _attribution_is_all_or_none(self) -> Self:
        four = (
            self.derived_changes,
            self.change_groups,
            self.attribution,
            self.attribution_summary,
        )
        if any(f is None for f in four) and any(f is not None for f in four):
            raise ValueError(
                "attribution fields must be present together: derived_changes, "
                "change_groups, attribution, attribution_summary"
            )
        return self

    @model_validator(mode="after")
    def _outcomes_are_consistent(self) -> Self:
        o = self.outcomes
        five = (
            o.quoted_both + o.quoted_to_declined + o.declined_to_quoted + o.declined_both + o.error
        )
        if five != self.policy_count:
            raise ValueError("outcomes must sum to policy_count")
        if sum(e.count for e in self.errors) != o.error:
            raise ValueError("errors counts must sum to outcomes.error")
        banded = o.quoted_both - o.zero_baseline - o.negative_baseline
        if sum(b.policies for b in self.distribution) != banded:
            raise ValueError(
                "distribution policies must equal quoted_both - zero_baseline - negative_baseline"
            )
        return self


class DislocationEstimate(BaseModel):
    """What a run with a `DislocationSpec` would cost, before launch (`RL-1264`'s feasibility
    rule; `RL-1504` item 4; 03 §5.1 `POST /api/v1/dislocation-runs/estimate`).

    `estimated_ratings` is `estimate_attribution_ratings` (03 §5.2); `estimated_worker_hours`
    is that count over the worker throughput the run's guard uses, so the number shown is the
    number the guard compares.
    """

    model_config = _FROZEN
    derived_changes: _Count
    policies: _Count
    estimated_ratings: _Count
    estimated_worker_hours: Annotated[float, Field(ge=0)]
    method: Literal["shapley", "order_dependent"]
