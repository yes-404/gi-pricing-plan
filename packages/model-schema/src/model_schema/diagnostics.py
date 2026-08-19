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
    "FeatureImportance",
    "GbmDiagnostics",
    "GbmEvalPoint",
    "GlmDiagnostics",
    "LiftBin",
    "MonotonicityCheck",
    "PartialDependence",
    "PartialDependencePoint",
    "PartitionDiagnostics",
    "PermutationImportance",
    "QuantileCrossing",
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

    At fit time one of these describes train and another describes holdout, and neither is
    meaningful without the other — which is why a *fit* only ever holds them together
    (`UniversalDiagnostics`).

    A backtest holds exactly one (`backtests.BacktestSummary`, FR-MODEL-57), and that is not
    the same defect: its population was never split, so there is no counterpart to withhold,
    and what it is read against is the model's own fit-time holdout on a different artifact.
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


class GbmEvalPoint(BaseModel):
    """One row of the evaluation curve FR-MODEL-52 requires (FR-MODEL-30 persists it).

    Both partitions on one row rather than two series, because the pair is the point: a
    metric still improving on train while flat on holdout is the shape early stopping
    exists to catch, and two separately-stored series can be joined wrongly.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    iteration: int = Field(ge=0)
    metric: str
    train: float | None = None
    holdout: float | None = None

    @model_validator(mode="after")
    def _a_point_reports_at_least_one_part(self) -> GbmEvalPoint:
        if self.train is None and self.holdout is None:
            raise ValueError("an evaluation point reports neither train nor holdout")
        return self


class FeatureImportance(BaseModel):
    """One feature's importance under the three measures a booster already knows.

    All three, because they disagree and the disagreement is the information: `gain` says
    how much a split improved the objective, `cover` how much data it improved it over, and
    `frequency` merely how often the feature was chosen. A feature that is frequent and
    low-gain is one the model reaches for and learns little from — invisible if only one
    measure is stored.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    feature: str
    gain: float = Field(ge=0.0)
    #: `None` on LightGBM, which exposes `split` and `gain` and **no cover at all**.
    #: Optional rather than zero-filled: a zero would read as "this feature covered no
    #: rows", which is a measurement, and the truth is that the backend does not report it.
    cover: float | None = Field(default=None, ge=0.0)
    frequency: float = Field(ge=0.0)


class PermutationImportance(BaseModel):
    """How much the holdout metric degrades when one feature is shuffled (FR-MODEL-52).

    On the **holdout**, and stated as a degradation rather than a score, because that is
    the question an actuary is asking: what would this model lose if this variable were
    noise. Split importance answers a different question — how the trees were built — and
    a feature can be split on constantly while carrying no predictive weight.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    feature: str
    baseline: float
    permuted: float
    #: `permuted - baseline` for a metric where lower is better. Negative means shuffling
    #: the feature *improved* the holdout metric, which is a real finding and not clipped
    #: away: it is what an overfitted or leaked feature looks like.
    degradation: float
    repeats: int = Field(ge=1)
    seed: int


class PartialDependencePoint(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    value: str
    mean_prediction: float
    exposure_share: float = Field(ge=0.0, le=1.0)


class PartialDependence(BaseModel):
    """The fitted response to one factor, averaged over the book (FR-MODEL-52).

    `exposure_share` rides with every point because a partial dependence curve is most
    dramatic exactly where the book is thinnest, and a plot without it invites reading a
    spike over 0.2 % of exposure as a rating signal.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    factor: str
    points: tuple[PartialDependencePoint, ...] = ()


class MonotonicityCheck(BaseModel):
    """Whether the **fitted** response respects a declared constraint (FR-MODEL-52).

    Verified rather than assumed. A constraint is a parameter passed to a library, and the
    thing that makes it true of this model is that someone swept the factor and looked —
    which is also what `TransparencyArtifact.monotonicity_verified` reports upward (R3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    factor: str
    declared: str
    holds: bool
    #: The largest move against the declared direction, on the mean scale. `0.0` when the
    #: constraint holds; present when it does not, because "violated" without a magnitude
    #: cannot be told from floating-point noise.
    worst_violation: float = Field(ge=0.0, default=0.0)


class GbmDiagnostics(BaseModel):
    """GBM-specific evidence (FR-MODEL-52), all six things the requirement names.

    The evaluation curve is here rather than on `GbmFitResult` because FR-MODEL-52 calls it
    a diagnostic and asks for **train and holdout** — which is FR-MODEL-54's shape, and the
    shape `diagnostics.schema.json` has carried since Phase 0. `fit_gbm` produces it and
    hands it back for the caller to place here; only `best_iteration` stays on the fit,
    because scoring needs it and diagnostics are not loaded to score.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    eval_curve: tuple[GbmEvalPoint, ...] = ()
    importances: tuple[FeatureImportance, ...] = ()
    permutation_importances: tuple[PermutationImportance, ...] = ()
    partial_dependence: tuple[PartialDependence, ...] = ()
    monotonicity: tuple[MonotonicityCheck, ...] = ()
    tree_count: int = Field(ge=0)
    #: The deepest tree and the mean depth. Two numbers because a forest of stumps with one
    #: deep tree and a forest of uniformly middling trees have the same mean.
    max_depth: int = Field(ge=0)
    mean_depth: float = Field(ge=0.0)
    #: FR-MODEL-78. Set on the second bound of a paired-quantile interval and `None`
    #: on every other model — including the first bound, which had nothing to cross.
    quantile_crossing: QuantileCrossing | None = None


class QuantileCrossing(BaseModel):
    """Whether this bound contradicts its counterpart, over the fit population (FR-MODEL-78).

    On the **second** bound's diagnostics. The first has no counterpart to cross when it is
    fitted, and FR-MODEL-49 computes diagnostics once at fit time and reads them thereafter
    — so the moment both boosters exist is the moment the second one is fitted, and there is
    no later pass in which to fill this in.

    `counterpart_model_id` names the model it was compared against, so a reader is not left
    inferring it from the alpha.

    **Crossing is reported, never repaired.** A pair whose lower bound exceeds its upper at
    some rows does not describe one distribution, and reordering the two would produce an
    interval that looks well formed and means nothing (OQ-MODEL-2).

    `None` on every model that is not the second bound of a pair.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    counterpart_model_id: UUID
    rows_checked: int = Field(ge=0)
    rows_crossing: int = Field(ge=0)
    #: The largest `lower - upper` over the crossing rows, on the response scale. `0.0` when
    #: nothing crosses. Beside the count because one row crossing by a factor of ten and a
    #: thousand rows crossing in the sixth decimal are different findings, and a count
    #: describes them identically.
    worst_gap: float = Field(ge=0.0)

    @model_validator(mode="after")
    def _the_two_numbers_describe_the_same_comparison(self) -> QuantileCrossing:
        """Three ways the pair of figures can disagree, each meaning a wrong array.

        A count above the rows checked, a gap with no crossing rows, or crossing rows with
        no gap: each is one of the two numbers computed from something other than the
        comparison the other one describes.
        """
        if self.rows_crossing > self.rows_checked:
            raise ValueError(
                f"{self.rows_crossing} crossing rows out of {self.rows_checked} checked."
            )
        if (self.rows_crossing == 0) != (self.worst_gap == 0.0):
            raise ValueError(
                f"rows_crossing={self.rows_crossing} and worst_gap={self.worst_gap} "
                "disagree: a gap with no crossing rows, or crossing rows with no gap, is "
                "one of the two computed from the wrong array."
            )
        return self


class Diagnostics(BaseModel):
    """The persisted artifact (`02` §4, `diagnostics.schema.json`).

    Immutable: computed at fit time and read thereafter (FR-MODEL-49).

    `gbm` is populated from the GBM slice on (FR-MODEL-52) and is `None` for a GLM, which
    is the honest reading of "GBM-specific".

    `cross_validation` is still declared and always `None`: FR-MODEL-53 computes it **at fit
    time**, so this artifact is where it will land, and its producer is a later slice.

    **`backtest` was here and is gone (2026-08-18).** It was declared from Phase 0 and typed
    `None`, and nothing could ever have populated it. FR-MODEL-49 makes these diagnostics
    computed once at fit time and read thereafter, while FR-MODEL-57's backtest runs against
    a *later* Dataset Version — after this artifact is written, and again for every period
    after that, which one field has no room for. It is its own artifact (`backtests.Backtest`,
    `02` §4.12), and FR-MODEL-57 carries the amendment. The same removal, for the same
    reason, that `PartitionDiagnostics.double_lift` got.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    model_id: UUID
    computed_at: datetime
    job_id: UUID | None = None
    universal: UniversalDiagnostics
    complexity: ComplexityDiagnostic
    glm: GlmDiagnostics | None = None
    gbm: GbmDiagnostics | None = None
    cross_validation: None = None
