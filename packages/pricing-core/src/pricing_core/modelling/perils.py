"""Composing per-peril models into a risk premium, and reconciling it (`02` §3.9, §5.2).

`WF-698` E4 and E5. FR-188's sum of `frequency x severity` (or burning cost) over
perils, FR-189's large-loss restoration, FR-190's coherence check against the
observed data, and FR-128's requirement that the two be compared *on the same basis*.

**The declared signatures could not be written.** `02` §5.2 said:

    def assemble_risk_premium(structure: PerilStructure, data: pl.DataFrame) -> pl.DataFrame
    def reconcile(structure: PerilStructure, data: pl.DataFrame) -> Reconciliation

A `PerilStructure` carries model *references* — `model:motor-ad-frequency@7` — and turning
one into predictions needs the database ADR-703 forbids this package. That is the fifth
instance of one defect: `fit_glm`, `predict_glm`, `compute_diagnostics` and `compare_models`
were each corrected the same way. The caller resolves; this module computes. `02` §5.2 is
amended with the same date.

`reconcile` returns a `ReconciliationResult` rather than the persisted `Reconciliation`,
which carries a `dataset_version_id`, a `part` and a `computed_at` only the platform can
supply — `compute_diagnostics`/`DiagnosticsResult` set that precedent.

**Three of FR-189's four treatments are computed here.** `separate_model` is refused by
name with `LOSS_TREATMENT_UNIMPLEMENTED`: it needs an excess-layer model's own predictions,
and treating it as `none` would under-state the premium by exactly the excess layer, in
silence. `flat_loading` and `capped` are both a multiplication — different provenance, same
arithmetic — so refusing one and computing the other would be an arbitrary line.

**Burning cost is an exposure-weighted mean, not a portfolio total.** The reconciliation
compares like with like, so the choice only has to be consistent; it is stated because
"total modelled burning cost" in FR-190 could be read either way, and a per-policy mean
is what the term means and what §4.10's example shows.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal

import numpy as np
import numpy.typing as npt
import polars as pl

from model_schema import LargeLossKind, LargeLossTreatment, PerilMethod
from pricing_core.modelling.errors import ModellingError

__all__ = [
    "PerilPrediction",
    "ReconciledPerilResult",
    "ReconciliationResult",
    "assemble_risk_premium",
    "reconcile",
]

#: The column holding the summed premium. Named once, because the platform reads it back.
RISK_PREMIUM_COLUMN = "risk_premium"

_NO_TREATMENT = LargeLossTreatment(kind=LargeLossKind.NONE)


@dataclass(frozen=True)
class PerilPrediction:
    """One peril, resolved to the arrays that price it (ADR-703).

    `peril` labels the output column and is never resolved to anything. The arrays are
    per-row expectations for that row's own exposure — a frequency model fitted with a
    log-exposure offset already returns an expected *count*, not a rate, so multiplying by
    severity gives that row's expected cost and no exposure term appears here.
    """

    peril: str
    method: PerilMethod
    frequency: npt.NDArray[np.float64] | None = None
    severity: npt.NDArray[np.float64] | None = None
    burning_cost: npt.NDArray[np.float64] | None = None
    large_loss: LargeLossTreatment = field(default=_NO_TREATMENT)


@dataclass(frozen=True)
class ReconciledPerilResult:
    """One peril's contribution, with the treatment that produced it (FR-128)."""

    peril: str
    large_loss_kind: LargeLossKind
    modelled_burning_cost: int


@dataclass(frozen=True)
class ReconciliationResult:
    """FR-190's numbers. The platform stamps identity onto these and persists them."""

    perils: tuple[ReconciledPerilResult, ...]
    observed_burning_cost: int
    modelled_burning_cost: int
    tolerance: Decimal
    ratio: Decimal

    @property
    def status(self) -> str:
        """Derived here as it is derived on the artifact, from the same two numbers."""
        return "pass" if abs(self.ratio - 1) <= self.tolerance else "fail"


def assemble_risk_premium(
    predictions: Sequence[PerilPrediction],
) -> pl.DataFrame:
    """FR-188 — per-peril cost and the summed risk premium, one row per risk.

    Large-loss restoration is applied **per peril, before the sum** (FR-189,
    FR-128). Restoring the total instead would apply one peril's loading to every
    peril, which is the arithmetic the per-peril declaration exists to avoid.
    """
    if not predictions:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            "a structure with no perils assembles no risk premium (FR-188)",
        )

    seen = [p.peril for p in predictions]
    duplicates = sorted({p for p in seen if seen.count(p) > 1})
    if duplicates:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            f"peril(s) {duplicates} appear more than once; each peril has one route to "
            "its cost (FR-188)",
        )

    columns: dict[str, npt.NDArray[np.float64]] = {}
    rows: int | None = None
    for prediction in predictions:
        cost = _restore(_cost(prediction), prediction)
        if rows is None:
            rows = cost.size
        elif cost.size != rows:
            raise ModellingError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                f"peril {prediction.peril} predicts {cost.size} rows where an earlier "
                f"peril predicts {rows}. Perils are summed row by row, so a mismatch is "
                "a sum over two different books",
            )
        if np.any(cost < 0):
            raise ModellingError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                f"peril {prediction.peril} predicts a negative cost. A negative expected "
                "cost is not a risk premium, and summed with positives it disappears",
            )
        columns[f"peril_{prediction.peril}"] = cost

    total = np.sum(np.stack(list(columns.values())), axis=0)
    return pl.DataFrame({**columns, RISK_PREMIUM_COLUMN: total})


def reconcile(
    assembled: pl.DataFrame,
    *,
    observed: npt.NDArray[np.float64],
    exposure: npt.NDArray[np.float64],
    tolerance: Decimal,
    treatments: Mapping[str, LargeLossKind],
) -> ReconciliationResult:
    """FR-190 — modelled against observed burning cost, within a declared tolerance.

    `assembled` comes from `assemble_risk_premium`, so its per-peril columns are **already
    restored** — which is FR-128: the comparison is between restored modelled cost and
    uncapped observed cost, and a capped model compared before restoration reads as a
    modelling error rather than an intended adjustment.

    `treatments` is required rather than derived from the frame because the frame carries
    numbers and not their provenance. A peril whose treatment nobody supplied would be
    recorded as `none`, and that is a claim about how the number was produced.
    """
    if tolerance <= 0:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            "tolerance must be positive; a tolerance of zero passes only an exact match, "
            "which no fitted model produces (FR-190)",
        )

    exposure_total = float(np.sum(exposure))
    if exposure_total <= 0:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            "total exposure is zero, so a burning cost has no denominator (FR-190)",
        )
    if observed.size != assembled.height or exposure.size != assembled.height:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            f"observed ({observed.size}) and exposure ({exposure.size}) must have one "
            f"entry per assembled row ({assembled.height})",
        )

    observed_minor = _to_minor(float(np.sum(observed)) / exposure_total)
    if observed_minor <= 0:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            "observed burning cost is zero; a ratio needs a denominator, and a holdout "
            "with no observed cost reconciles nothing (FR-190)",
        )

    perils: list[ReconciledPerilResult] = []
    for column in assembled.columns:
        if column == RISK_PREMIUM_COLUMN:
            continue
        peril = column.removeprefix("peril_")
        if peril not in treatments:
            raise ModellingError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                f"no large-loss treatment supplied for peril {peril}. FR-128 states "
                "the treatment beside the number; defaulting it to 'none' would be a "
                "claim about how the number was produced",
            )
        modelled = float(assembled[column].sum()) / exposure_total
        perils.append(
            ReconciledPerilResult(
                peril=peril,
                large_loss_kind=treatments[peril],
                modelled_burning_cost=_to_minor(modelled),
            )
        )

    # The total is the **sum of the rounded parts**, never a separately rounded total.
    # Rounding three perils and their total independently disagrees by a penny about half
    # the time, and `Reconciliation`'s own invariant would then reject a correct result.
    modelled_minor = sum(p.modelled_burning_cost for p in perils)
    ratio = (Decimal(modelled_minor) / Decimal(observed_minor)).quantize(
        Decimal("0.000001")
    )
    return ReconciliationResult(
        perils=tuple(perils),
        observed_burning_cost=observed_minor,
        modelled_burning_cost=modelled_minor,
        tolerance=tolerance,
        ratio=ratio,
    )


# -- internals -----------------------------------------------------------------------------


def _cost(prediction: PerilPrediction) -> npt.NDArray[np.float64]:
    """The peril's expected cost before its large-loss treatment (FR-188)."""
    if prediction.method is PerilMethod.FREQUENCY_SEVERITY:
        if prediction.frequency is None:
            raise ModellingError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                f"peril {prediction.peril}: a frequency_severity peril needs frequency "
                "predictions (FR-188)",
            )
        if prediction.severity is None:
            raise ModellingError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                f"peril {prediction.peril}: a frequency_severity peril needs severity "
                "predictions. A frequency alone would sum into the premium as a cost "
                "three orders of magnitude too small (FR-188)",
            )
        if prediction.frequency.size != prediction.severity.size:
            raise ModellingError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                f"peril {prediction.peril}: frequency and severity predict different "
                "numbers of rows",
            )
        return np.asarray(prediction.frequency * prediction.severity, dtype=np.float64)

    if prediction.burning_cost is None:
        raise ModellingError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            f"peril {prediction.peril}: a burning_cost peril needs burning cost "
            "predictions (FR-188)",
        )
    return np.asarray(prediction.burning_cost, dtype=np.float64)


def _restore(
    cost: npt.NDArray[np.float64], prediction: PerilPrediction
) -> npt.NDArray[np.float64]:
    """FR-189's treatment, applied to one peril's cost."""
    treatment = prediction.large_loss
    match treatment.kind:
        case LargeLossKind.NONE:
            return cost
        case LargeLossKind.CAPPED:
            assert treatment.restoration_loading is not None  # contract invariant
            return cost * float(treatment.restoration_loading)
        case LargeLossKind.FLAT_LOADING:
            assert treatment.loading_factor is not None  # contract invariant
            return cost * float(treatment.loading_factor)
        case LargeLossKind.SEPARATE_MODEL:
            raise ModellingError(
                "LOSS_TREATMENT_UNIMPLEMENTED",
                f"peril {prediction.peril}: the 'separate_model' large-loss treatment is "
                "declared by FR-189 and computed by nothing yet — it needs the "
                "excess-layer model's own predictions. Reconciling it as though it were "
                "'none' would under-state the premium by exactly the excess layer",
            )


def _to_minor(amount: float) -> int:
    """Round an exposure-weighted mean to integer minor units, explicitly.

    `money.to_minor` refuses anything not already exact, which is right for a rated amount
    and wrong for a fitted mean — every one of these is inexact by construction. Banker's
    rounding, stated here rather than inherited from whatever `round()` does.
    """
    return int(Decimal(repr(amount)).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))
