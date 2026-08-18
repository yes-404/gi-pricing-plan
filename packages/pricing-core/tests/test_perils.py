"""Assembling a risk premium and reconciling it (`02` FR-MODEL-58, 60, 74, §5.2).

The maths is a sum of products. Everything that can go wrong is in the *composition* — which
is why almost every test here is a refusal.

Two are the reason the module exists rather than being a `.sum()` at the call site:

* **restoration happens before the comparison** (FR-MODEL-74). A capped model reconciled
  against uncapped observed data reads as a modelling error unless its mean is put back
  first, and `test_restoration_is_what_makes_a_capped_peril_reconcile` is that sentence
  as an executable one: the same peril fails without it and passes with it.
* **the per-peril figures sum to the total exactly.** Rounding each peril to minor units and
  the total independently loses a penny about half the time, and the artifact's own
  invariant (`modelled = sum(perils)`) would then reject a correct reconciliation.
"""

from __future__ import annotations

from decimal import Decimal

import numpy as np
import pytest

from model_schema import BlobRef, LargeLossKind, LargeLossTreatment, PerilMethod
from pricing_core.modelling.errors import ModellingError
from pricing_core.modelling.perils import (
    PerilPrediction,
    assemble_risk_premium,
    reconcile,
)

EVIDENCE = BlobRef(sha256="b" * 64, bytes=2_048, media_type="application/json")


def _capped(loading: str = "1.10") -> LargeLossTreatment:
    return LargeLossTreatment(
        kind=LargeLossKind.CAPPED,
        cap_minor=1_000_000,
        restoration_loading=Decimal(loading),
        evidence_blob=EVIDENCE,
    )


def _ad(frequency: list[float], severity: list[float], **kw: object) -> PerilPrediction:
    return PerilPrediction(
        peril="AD",
        method=PerilMethod.FREQUENCY_SEVERITY,
        frequency=np.array(frequency),
        severity=np.array(severity),
        **kw,  # type: ignore[arg-type]
    )


def _windscreen(burning_cost: list[float], **kw: object) -> PerilPrediction:
    return PerilPrediction(
        peril="WINDSCREEN",
        method=PerilMethod.BURNING_COST,
        burning_cost=np.array(burning_cost),
        **kw,  # type: ignore[arg-type]
    )


# -- assembly ------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-58")
def test_frequency_times_severity_summed_over_perils() -> None:
    assembled = assemble_risk_premium(
        [_ad([0.1, 0.2], [20_000.0, 10_000.0]), _windscreen([500.0, 400.0])]
    )
    assert assembled["peril_AD"].to_list() == [2_000.0, 2_000.0]
    assert assembled["peril_WINDSCREEN"].to_list() == [500.0, 400.0]
    assert assembled["risk_premium"].to_list() == [2_500.0, 2_400.0]


@pytest.mark.req("FR-MODEL-74")
def test_a_capped_peril_is_restored_before_it_is_summed() -> None:
    assembled = assemble_risk_premium(
        [_ad([0.1], [20_000.0], large_loss=_capped("1.10"))]
    )
    assert assembled["peril_AD"].to_list() == [2_200.0]


@pytest.mark.req("FR-MODEL-59")
def test_a_flat_loading_multiplies_the_peril() -> None:
    flat = LargeLossTreatment(
        kind=LargeLossKind.FLAT_LOADING,
        loading_factor=Decimal("1.05"),
        evidence_blob=EVIDENCE,
    )
    assembled = assemble_risk_premium([_windscreen([1_000.0], large_loss=flat)])
    assert assembled["peril_WINDSCREEN"].to_list() == [1_050.0]


@pytest.mark.req("FR-MODEL-59")
def test_separate_model_refuses_by_name() -> None:
    """The one treatment this slice does not compute. It needs an excess-layer model's own
    predictions, and reconciling as though it were `none` would under-state the premium by
    the excess layer — silently, which is the failure the refusal exists to prevent."""
    separate = LargeLossTreatment(
        kind=LargeLossKind.SEPARATE_MODEL,
        excess_model="model:motor-tpbi-excess@2",
        attachment_minor=100_000_000,
        evidence_blob=EVIDENCE,
    )
    with pytest.raises(ModellingError) as refused:
        assemble_risk_premium([_ad([0.1], [20_000.0], large_loss=separate)])
    assert refused.value.code == "LOSS_TREATMENT_UNIMPLEMENTED"
    assert "separate_model" in str(refused.value)


@pytest.mark.req("FR-MODEL-58")
def test_perils_of_different_lengths_are_refused() -> None:
    with pytest.raises(ModellingError, match="rows"):
        assemble_risk_premium([_ad([0.1, 0.2], [1.0, 2.0]), _windscreen([500.0])])


@pytest.mark.req("FR-MODEL-58")
def test_a_structure_with_no_perils_assembles_nothing() -> None:
    with pytest.raises(ModellingError, match="no perils"):
        assemble_risk_premium([])


@pytest.mark.req("FR-MODEL-58")
def test_a_frequency_severity_peril_without_severity_is_refused() -> None:
    """The prediction, not the contract: `PerilComponent` refuses a missing *model*, and
    this refuses a missing *array*. A frequency alone would sum as a cost."""
    with pytest.raises(ModellingError, match="severity"):
        assemble_risk_premium(
            [
                PerilPrediction(
                    peril="AD",
                    method=PerilMethod.FREQUENCY_SEVERITY,
                    frequency=np.array([0.1]),
                )
            ]
        )


@pytest.mark.req("FR-MODEL-58")
def test_a_duplicate_peril_is_refused() -> None:
    with pytest.raises(ModellingError, match="AD"):
        assemble_risk_premium([_ad([0.1], [1.0]), _ad([0.2], [2.0])])


@pytest.mark.req("FR-MODEL-58")
def test_a_negative_prediction_is_refused() -> None:
    """A negative expected cost is not a risk premium, and summed with positives it hides."""
    with pytest.raises(ModellingError, match="negative"):
        assemble_risk_premium([_windscreen([-1.0, 500.0])])


# -- reconciliation ------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-60")
def test_reconciliation_compares_exposure_weighted_means() -> None:
    assembled = assemble_risk_premium([_windscreen([100.0, 300.0])])
    result = reconcile(
        assembled,
        observed=np.array([120.0, 280.0]),
        exposure=np.array([1.0, 1.0]),
        tolerance=Decimal("0.02"),
        treatments={"WINDSCREEN": LargeLossKind.NONE},
    )
    assert result.modelled_burning_cost_minor == 200
    assert result.observed_burning_cost_minor == 200
    assert result.ratio == Decimal("1.000000")
    assert result.status == "pass"


@pytest.mark.req("FR-MODEL-60")
def test_outside_tolerance_fails_and_says_by_how_much() -> None:
    assembled = assemble_risk_premium([_windscreen([100.0, 100.0])])
    result = reconcile(
        assembled,
        observed=np.array([150.0, 150.0]),
        exposure=np.array([1.0, 1.0]),
        tolerance=Decimal("0.02"),
        treatments={"WINDSCREEN": LargeLossKind.NONE},
    )
    assert result.status == "fail"
    assert result.ratio < 1


@pytest.mark.req("FR-MODEL-74")
def test_restoration_is_what_makes_a_capped_peril_reconcile() -> None:
    """FR-MODEL-74 in one test: the same capped model against the same uncapped observed
    data, failing without its restoration loading and passing with it."""
    observed = np.array([220.0, 220.0])
    exposure = np.array([1.0, 1.0])

    uncorrected = reconcile(
        assemble_risk_premium([_windscreen([200.0, 200.0])]),
        observed=observed,
        exposure=exposure,
        tolerance=Decimal("0.02"),
        treatments={"WINDSCREEN": LargeLossKind.NONE},
    )
    assert uncorrected.status == "fail"

    restored = reconcile(
        assemble_risk_premium([_windscreen([200.0, 200.0], large_loss=_capped("1.10"))]),
        observed=observed,
        exposure=exposure,
        tolerance=Decimal("0.02"),
        treatments={"WINDSCREEN": LargeLossKind.CAPPED},
    )
    assert restored.status == "pass"


@pytest.mark.req("FR-MODEL-60")
def test_the_per_peril_figures_sum_to_the_total_exactly() -> None:
    """Rounding three perils and the total independently loses a penny about half the time,
    and the artifact's own invariant would then reject a correct reconciliation."""
    assembled = assemble_risk_premium(
        [
            _windscreen([33.333]),
            _ad([1.0], [33.333]),
            PerilPrediction(
                peril="TP_BI",
                method=PerilMethod.BURNING_COST,
                burning_cost=np.array([33.334]),
            ),
        ]
    )
    result = reconcile(
        assembled,
        observed=np.array([100.0]),
        exposure=np.array([1.0]),
        tolerance=Decimal("0.02"),
        treatments=dict.fromkeys(("WINDSCREEN", "AD", "TP_BI"), LargeLossKind.NONE),
    )
    assert (
        sum(p.modelled_burning_cost_minor for p in result.perils)
        == result.modelled_burning_cost_minor
    )


@pytest.mark.req("FR-MODEL-60")
def test_zero_exposure_is_refused() -> None:
    assembled = assemble_risk_premium([_windscreen([100.0])])
    with pytest.raises(ModellingError, match="exposure"):
        reconcile(
            assembled,
            observed=np.array([100.0]),
            exposure=np.array([0.0]),
            tolerance=Decimal("0.02"),
            treatments={"WINDSCREEN": LargeLossKind.NONE},
        )


@pytest.mark.req("FR-MODEL-60")
def test_a_treatment_missing_from_the_map_is_refused() -> None:
    """FR-MODEL-74 requires the treatment to be stated beside the number. A peril whose
    treatment nobody supplied would be reported as `none`, which is a claim."""
    assembled = assemble_risk_premium([_windscreen([100.0])])
    with pytest.raises(ModellingError, match="WINDSCREEN"):
        reconcile(
            assembled,
            observed=np.array([100.0]),
            exposure=np.array([1.0]),
            tolerance=Decimal("0.02"),
            treatments={},
        )


@pytest.mark.req("FR-MODEL-60")
def test_a_non_positive_tolerance_is_refused() -> None:
    assembled = assemble_risk_premium([_windscreen([100.0])])
    with pytest.raises(ModellingError, match="tolerance"):
        reconcile(
            assembled,
            observed=np.array([100.0]),
            exposure=np.array([1.0]),
            tolerance=Decimal("0"),
            treatments={"WINDSCREEN": LargeLossKind.NONE},
        )


@pytest.mark.req("FR-MODEL-60")
def test_nothing_observed_is_refused_rather_than_divided_by() -> None:
    assembled = assemble_risk_premium([_windscreen([100.0])])
    with pytest.raises(ModellingError, match="observed"):
        reconcile(
            assembled,
            observed=np.array([0.0]),
            exposure=np.array([1.0]),
            tolerance=Decimal("0.02"),
            treatments={"WINDSCREEN": LargeLossKind.NONE},
        )
