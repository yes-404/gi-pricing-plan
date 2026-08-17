"""Model comparison (`02` FR-MODEL-56, §4.11 — `model-comparison.schema.json`).

The artifact `wf-01` E1 produces and E2 decides on, and what an approval request cites when
a predecessor existed (`06` §3.3).

**Designed here rather than transcribed.** `02` §5.2 named `ModelComparison` as a return type
from Phase 0 and no document defined it: no §4 subsection, no type, no contract. So each
invariant below is a choice, and the reason is stated where the choice was made.

Three shape decisions carry most of the meaning:

* **The shared holdout is a `SplitRef`, not a promise.** FR-MODEL-56 says "fitted on the same
  holdout", and FR-DATA-36 recorded the split on the parent version precisely so that
  "the same split" is *one artifact two models cite*. The comparison stores the ref it
  verified, so a reader can check the claim rather than take it.
* **Double lift is pairwise, and says so.** FR-MODEL-50 listed it among universal diagnostics,
  where it could never be computed — the comparison model is unknown at fit time and
  FR-MODEL-49 makes diagnostics computed once. Here it is one series per challenger against a
  named baseline. Averaging several challengers into one curve would erase what the chart is
  for: where two specific models disagree, and which one the data supports there.
* **A value may be absent without the model being absent.** `None` means "this metric does not
  apply to this model" — a relativity under a non-multiplicative link, most often. Dropping
  the model from the list instead would read as a model that scored nothing.
"""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.diagnostics import Weighting
from model_schema.modelling import SplitRef
from model_schema.money import DecimalStr

__all__ = [
    "ComparisonMetric",
    "ComparisonSummary",
    "ComparisonValue",
    "DoubleLift",
    "DoubleLiftBin",
    "MetricDirection",
    "ModelComparison",
    "RelativityDifference",
]


class MetricDirection(enum.StrEnum):
    """Which way is better, declared with the metric rather than assumed by the reader.

    `CLOSER_TO_ONE_IS_BETTER` exists for A/E, and it is the reason this enum is not a
    boolean: an A/E of 1.4 and one of 0.6 are equally wrong, and every "higher is better"
    table this repository could have written would have ranked 1.4 above 1.0.

    `NOT_ORDERED` is for the metrics that are context rather than score — the holdout row
    count is the same number for every model on a shared split, and a winner on it would be
    an artefact of tie-breaking.
    """

    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"
    CLOSER_TO_ONE_IS_BETTER = "closer_to_one_is_better"
    NOT_ORDERED = "not_ordered"


class ComparisonValue(BaseModel):
    """One model's reading of one quantity.

    `value` is nullable and the model is always present — see the module docstring. The ref is
    the canonical `{type}:{slug}@{version}` string (ID-3), so a comparison read years later
    still names exactly which model versions it held.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_ref: str
    value: float | None = None


class ComparisonMetric(BaseModel):
    """One metric, aligned across every model in the comparison (FR-MODEL-56)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: str
    #: FR-MODEL-55: a metric carries its weighting. No default, for the reason
    #: `PartitionDiagnostics` gives — an exposure-weighted A/E and an unweighted one are
    #: different numbers and guessing which was meant is the mistake the requirement names.
    weighting: Weighting
    direction: MetricDirection
    values: tuple[ComparisonValue, ...] = Field(min_length=2)
    #: The winning model, or `None` where the metric does not order or no model has a value.
    leader: str | None = None

    @model_validator(mode="after")
    def _the_leader_is_one_of_the_models_measured(self) -> ComparisonMetric:
        if self.leader is None:
            return self
        if self.leader not in {v.model_ref for v in self.values}:
            raise ValueError(
                f"metric {self.metric!r} names {self.leader!r} as leader, which is not among "
                "the models it measured. A leader outside the comparison is a claim about a "
                "model that was not in it."
            )
        return self

    @model_validator(mode="after")
    def _an_unordered_metric_has_no_leader(self) -> ComparisonMetric:
        if self.direction is MetricDirection.NOT_ORDERED and self.leader is not None:
            raise ValueError(
                f"metric {self.metric!r} is not ordered and names a leader "
                f"({self.leader!r}). Declaring a winner on a metric with no order invents "
                "one from whatever the tie-break happened to be."
            )
        return self


class DoubleLiftBin(BaseModel):
    """One bin of a double-lift chart: what each model said, and what happened.

    Bins are ordered by the **ratio** of the two predictions, not by either prediction — that
    ordering is what makes the chart answer "where the models disagree, which one is right?".
    A chart binned by predicted value would show two lift curves side by side, which is a
    different and much weaker question.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    bin: int = Field(ge=1)
    rows: int = Field(ge=0)
    actual: float
    baseline_predicted: float
    challenger_predicted: float
    exposure_years: DecimalStr | None = None


class DoubleLift(BaseModel):
    """One challenger against the baseline (FR-MODEL-56, and FR-MODEL-50 as amended)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    baseline_ref: str
    challenger_ref: str
    weighting: Weighting
    bins: tuple[DoubleLiftBin, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _a_model_is_not_its_own_challenger(self) -> DoubleLift:
        if self.baseline_ref == self.challenger_ref:
            raise ValueError(
                f"double lift of {self.baseline_ref} against itself is a flat line at 1.0, "
                "which a reader will take for two models agreeing."
            )
        return self


class RelativityDifference(BaseModel):
    """How the models price one level of one factor differently (FR-MODEL-56).

    The comparison an actuary actually argues from: two models can score almost identically
    and disagree by 15 % on young drivers, and the aggregate metrics cannot show that.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    factor: str
    level: str
    values: tuple[ComparisonValue, ...] = Field(min_length=2)
    #: The widest gap between any two models at this level, for ranking the table. `None`
    #: where fewer than two models express a relativity here — a non-multiplicative link
    #: has none at all, and 0.0 would say the models agree about it.
    max_abs_difference: float | None = None


class ComparisonSummary(BaseModel):
    """What a comparison found, before the platform gives it an identity.

    The `DiagnosticsResult` split, for the same reason: `pricing-core` computes and does not
    allocate ids, know about rows, or read a clock (ADR-0001).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: In the order the caller asked for them. Two or more (FR-MODEL-56) — a comparison of
    #: one is a diagnostics read, and calling it a comparison would let an approval cite it
    #: as evidence that a candidate had been considered.
    model_refs: tuple[str, ...] = Field(min_length=2)
    baseline_ref: str
    #: The split every model was verified to share, stored so the claim is checkable.
    split_ref: SplitRef
    holdout_rows: int = Field(ge=1)
    metrics: tuple[ComparisonMetric, ...] = ()
    double_lift: tuple[DoubleLift, ...] = ()
    relativity_differences: tuple[RelativityDifference, ...] = ()

    @model_validator(mode="after")
    def _every_reference_belongs_to_this_comparison(self) -> ComparisonSummary:
        refs = set(self.model_refs)
        if len(refs) != len(self.model_refs):
            raise ValueError(
                f"{self.model_refs} repeats a model. Comparing a version with itself "
                "produces agreement it did not have to earn."
            )
        if self.baseline_ref not in refs:
            raise ValueError(
                f"baseline {self.baseline_ref!r} is not among the models compared "
                f"({sorted(refs)}). Double lift is measured against the baseline, so a "
                "reference line from outside the set is one the reader cannot look up."
            )
        for metric in self.metrics:
            measured = {v.model_ref for v in metric.values}
            if measured != refs:
                raise ValueError(
                    f"metric {metric.metric!r} measured {sorted(measured)}, not "
                    f"{sorted(refs)}. A missing model reads as one that scored nothing "
                    "rather than one nobody measured; where a metric does not apply, the "
                    "value is null and the model stays."
                )
        for series in self.double_lift:
            if series.baseline_ref != self.baseline_ref:
                raise ValueError(
                    f"double-lift series names baseline {series.baseline_ref!r} while the "
                    f"comparison's baseline is {self.baseline_ref!r}."
                )
            if series.challenger_ref not in refs:
                raise ValueError(
                    f"double-lift challenger {series.challenger_ref!r} is not among the "
                    f"models compared ({sorted(refs)})."
                )
        return self


class ModelComparison(BaseModel):
    """The persisted comparison artifact (`02` §4.11, FR-MODEL-56).

    Immutable, and enforced at the privilege layer as well as here (FR-DATA-42): an approval
    cites this, and evidence that can change after the approval is not evidence.

    It has no slug and no version of its own, for the reason `Diagnostics` has none — it is
    always reached by id, from the Job that produced it or the approval that cites it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    computed_at: datetime
    job_id: UUID | None = None
    summary: ComparisonSummary
