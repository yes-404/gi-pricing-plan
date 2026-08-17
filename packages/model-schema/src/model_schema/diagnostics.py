"""Model quality evidence (`02` §3.8, §4 — `diagnostics.schema.json`).

What this module owes its caller, in the spec's own terms:

* **FR-MODEL-49** — diagnostics are computed **once, at fit time**, and read thereafter.
  Nothing here recomputes; the UI reads what the fit recorded. A number the screen derives
  is a number nobody can cite in an approval.
* **FR-MODEL-54** — every metric is reported for train **and** holdout, side by side. That
  is enforced at the type: `UniversalDiagnostics` requires both partitions, so a
  diagnostic without its holdout counterpart cannot be constructed, let alone persisted.
  The spec calls a one-sided diagnostic a defect, and a defect that can be represented
  eventually is.
* **FR-MODEL-55** — a metric carries its weighting scheme. `weighting` has **no default**:
  an exposure-weighted A/E and an unweighted one are different numbers, and guessing which
  was meant is precisely the mistake the requirement names.
* **FR-MODEL-81** — complexity is a diagnostic, always recorded, and a gate only where a
  workspace sets one. The thresholds in force are stored *beside* the measurements, so a
  reader can see what the numbers were judged against rather than inferring today's
  settings onto a fit from six months ago.
"""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.money import DecimalStr

__all__ = [
    "AeCell",
    "CalibrationBin",
    "ComplexityDiagnostic",
    "Diagnostics",
    "GlmDiagnostics",
    "LiftBin",
    "PartitionDiagnostics",
    "ResidualSummary",
    "TypeIIITest",
    "UniversalDiagnostics",
    "Weighting",
]


class Weighting(enum.StrEnum):
    """How a metric was weighted (FR-MODEL-55).

    `EXPOSURE` for frequency and burning cost, `CLAIM_COUNT` for severity, `COUNT` where
    the metric genuinely counts rows. The UI labels an unweighted metric on an
    exposure-weighted problem *as such* — which it can only do if the fit said which.
    """

    EXPOSURE = "exposure"
    COUNT = "count"
    CLAIM_COUNT = "claim_count"


class AeCell(BaseModel):
    """Actual versus expected for one level of one factor (FR-MODEL-50).

    `ci_95` is on the **ratio**, not on the actual: an A/E of 1.19 whose interval excludes
    1.0 is a finding, and one whose interval spans it is noise. Without the interval the
    two render identically, which is how a thin cell becomes a rating decision.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    factor: str
    level: str
    actual: float
    expected: float
    ae: float
    ci_95: tuple[float, float] | None = None
    exposure_years: DecimalStr | None = None

    @model_validator(mode="after")
    def _the_interval_is_ordered(self) -> AeCell:
        if self.ci_95 is not None and self.ci_95[0] > self.ci_95[1]:
            raise ValueError(
                f"A/E interval for {self.factor}[{self.level}] is inverted: "
                f"{self.ci_95[0]} > {self.ci_95[1]}."
            )
        return self


class LiftBin(BaseModel):
    """One predicted-decile bin of a lift/gains curve (FR-MODEL-50)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    bin: int = Field(ge=1)
    rows: int = Field(ge=0)
    predicted: float
    actual: float
    exposure_years: DecimalStr | None = None


class CalibrationBin(BaseModel):
    """Predicted against observed within a predicted-decile bin (FR-MODEL-50)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    bin: int = Field(ge=1)
    rows: int = Field(ge=0)
    predicted: float
    actual: float


class ResidualSummary(BaseModel):
    """Distribution summary of the working residuals (FR-MODEL-50)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mean: float
    std: float
    minimum: float
    maximum: float
    p01: float
    p99: float


class PartitionDiagnostics(BaseModel):
    """Every universal metric, for one partition (FR-MODEL-50).

    One of these describes train and another describes holdout; neither is meaningful
    without the other, which is why they are only ever held together
    (`UniversalDiagnostics`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: No default — FR-MODEL-55 makes this the metric's meaning, not its metadata.
    weighting: Weighting
    rows: int = Field(ge=0)
    ae_overall: float = Field(ge=0.0)
    ae_by_factor: tuple[AeCell, ...] = ()
    lift: tuple[LiftBin, ...] = ()
    #: **`double_lift` was here and is gone (2026-08-17).** FR-MODEL-50 listed "double lift
    #: vs a comparison model" among *universal* diagnostics, and nothing ever populated the
    #: field — nothing could. Double lift is pairwise, the comparison model is unknown at fit
    #: time, and FR-MODEL-49 makes diagnostics computed once and read thereafter, so the
    #: field could not be filled later either. It lives on the comparison artifact
    #: (`comparison.DoubleLift`), and FR-MODEL-50 carries the amendment.
    gini: float
    gini_normalised: float
    calibration: tuple[CalibrationBin, ...] = ()
    residual_summary: ResidualSummary | None = None


class UniversalDiagnostics(BaseModel):
    """Train and holdout, side by side (FR-MODEL-54).

    Both fields are required. The requirement says a diagnostic reported without its
    holdout counterpart *is a defect*, and the cheapest way to honour that is to make the
    defective shape unrepresentable rather than to check for it later.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    train: PartitionDiagnostics
    holdout: PartitionDiagnostics

    @model_validator(mode="after")
    def _both_partitions_are_weighted_the_same_way(self) -> UniversalDiagnostics:
        """Comparing an exposure-weighted train A/E to an unweighted holdout A/E is
        comparing two different quantities and reading the difference as deterioration.

        Refused rather than warned about: the numbers render side by side, and side by side
        is exactly where the reader assumes they are commensurable.
        """
        if self.train.weighting is not self.holdout.weighting:
            raise ValueError(
                f"train is weighted by {self.train.weighting.value} and holdout by "
                f"{self.holdout.weighting.value}; side-by-side metrics must share a "
                "weighting scheme (FR-MODEL-55)."
            )
        return self


class TypeIIITest(BaseModel):
    """A factor's type-III deviance test (FR-MODEL-51).

    `deviance_delta` is the increase in deviance when the factor is dropped, on `df`
    degrees of freedom — a likelihood-ratio statistic, so the p-value means what a reader
    expects it to mean.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    factor: str
    deviance_delta: float
    df: int = Field(ge=0)
    p_value: float = Field(ge=0.0, le=1.0)


class GlmDiagnostics(BaseModel):
    """GLM-specific evidence (FR-MODEL-51)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    deviance: float
    null_deviance: float
    #: `None` where the family has no closed-form likelihood this platform evaluates —
    #: Tweedie's density needs a series expansion. An absent AIC is a fact about the
    #: family; a deviance-based stand-in would differ from every other tool's AIC by an
    #: additive constant, which reads as a disagreement between two correct numbers.
    aic: float | None = None
    bic: float | None = None
    dispersion: float
    degrees_of_freedom: int = Field(ge=0)
    type_iii_tests: tuple[TypeIIITest, ...] = ()
    #: Terms dropped as collinear. Named rather than counted: "2 terms aliased" tells a
    #: reader something is wrong and not which factor to fix.
    aliasing: tuple[str, ...] = ()
    vif: dict[str, float] = Field(default_factory=dict)
    residual_blob: str | None = None
    leverage_blob: str | None = None


class ComplexityDiagnostic(BaseModel):
    """Factor and parameter counts against whatever thresholds are in force (FR-MODEL-81).

    Recorded on **every** fit. The thresholds are stored with the measurements because they
    are workspace settings that change: a fit judged against no limit and a fit judged
    against a limit of 40 are different events, and a diagnostic that stored only the
    counts would render them identically a year later.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    factor_count: int = Field(ge=0)
    parameter_count: int = Field(ge=0)
    exposure_per_parameter: float | None = None
    claims_per_parameter: float | None = None
    #: `None` means the workspace sets no limit — FR-MODEL-81's default. Distinct from 0,
    #: which would be a limit nothing could satisfy.
    max_factor_count: int | None = None
    min_exposure_per_parameter: float | None = None


class Diagnostics(BaseModel):
    """The persisted artifact (`02` §4, `diagnostics.schema.json`).

    Immutable: computed at fit time and read thereafter (FR-MODEL-49). `gbm`,
    `cross_validation` and `backtest` are declared and always `None` in this slice — the
    fields exist because the contract the frontend generates from declares them, and their
    producers (FR-MODEL-52, 53, 57) are owned by later slices.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    model_id: UUID
    computed_at: datetime
    job_id: UUID | None = None
    universal: UniversalDiagnostics
    complexity: ComplexityDiagnostic
    glm: GlmDiagnostics | None = None
    gbm: None = None
    cross_validation: None = None
    backtest: None = None
