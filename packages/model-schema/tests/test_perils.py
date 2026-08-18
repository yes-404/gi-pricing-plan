"""The Peril Structure's invariants (`02` FR-MODEL-58..61, FR-MODEL-74, §4.10).

§4.10 prints an example, not a contract: it shows one well-formed structure and says nothing
about which malformed ones must be impossible. Choosing those is this file, and each test is
the record of one choice.

The prohibitions worth reading twice, because each is a mispricing rather than a typo:

* **a `frequency_severity` peril missing its severity model.** The risk premium would be a
  frequency, silently — a number three orders of magnitude too small that still adds up;
* **a `capped` treatment with no restoration loading.** FR-MODEL-59 caps to stabilise the
  fit and restores the mean afterwards. Capping without restoring under-prices the book by
  exactly the large-loss share, which is the part nobody can afford to lose;
* **a peril both modelled and excluded.** FR-MODEL-60 asks for every peril to be one or the
  other; being both means the reader cannot tell whether its cost is in the total;
* **a reconciliation whose `status` is stored.** Derived from `ratio` and `tolerance`
  instead, for the reason §4.9's `kinds` is derived: two statements of one fact disagree,
  and this one is cited in an approval.

`restoration_loading < 1` is refused for the same reason as the missing loading. A
restoration that shrinks the mean is a cap applied twice.
"""

from __future__ import annotations

import datetime as _datetime
from decimal import Decimal

import pydantic
import pytest

from model_schema import (
    VALID_PERIL_STRUCTURE_TRANSITIONS,
    BlobRef,
    ExcludedPeril,
    LargeLossKind,
    LargeLossTreatment,
    PerilComponent,
    PerilMethod,
    PerilStructure,
    PerilStructureStatus,
    ReconciledPeril,
    Reconciliation,
    ReconciliationStatus,
    new_uuid7,
)

AD_FREQ = "model:motor-ad-frequency@7"
AD_SEV = "model:motor-ad-severity@5"
WS_BC = "model:motor-ws-bc@2"
EXCESS = "model:motor-tpbi-excess@2"
EVIDENCE = BlobRef(sha256="a" * 64, bytes=4_096, media_type="application/json")


def _none() -> LargeLossTreatment:
    return LargeLossTreatment(kind=LargeLossKind.NONE)


def _capped(loading: str = "1.043") -> LargeLossTreatment:
    return LargeLossTreatment(
        kind=LargeLossKind.CAPPED,
        cap_minor=2_500_000,
        restoration_loading=Decimal(loading),
        evidence_blob=EVIDENCE,
    )


def _ad(large_loss: LargeLossTreatment | None = None) -> PerilComponent:
    return PerilComponent(
        peril="AD",
        method=PerilMethod.FREQUENCY_SEVERITY,
        frequency_model=AD_FREQ,
        severity_model=AD_SEV,
        large_loss=large_loss or _none(),
    )


def _windscreen() -> PerilComponent:
    return PerilComponent(
        peril="WINDSCREEN",
        method=PerilMethod.BURNING_COST,
        burning_cost_model=WS_BC,
        large_loss=_none(),
    )


def _structure(**overrides: object) -> PerilStructure:
    kwargs: dict[str, object] = {
        "id": new_uuid7(),
        "slug": "motor-gb-2026h2",
        "version": 2,
        "perils": (_ad(), _windscreen()),
        "excluded_perils": (),
        "status": PerilStructureStatus.DRAFT,
        "created_at": _datetime.datetime(2026, 8, 18, tzinfo=_datetime.UTC),
    }
    kwargs.update(overrides)
    return PerilStructure(**kwargs)  # type: ignore[arg-type]


def _reconciliation(**overrides: object) -> Reconciliation:
    kwargs: dict[str, object] = {
        "dataset_version_id": new_uuid7(),
        "part": "holdout",
        "perils": (
            ReconciledPeril(
                peril="AD",
                large_loss_kind=LargeLossKind.NONE,
                modelled_burning_cost_minor=15_000,
            ),
            ReconciledPeril(
                peril="WINDSCREEN",
                large_loss_kind=LargeLossKind.NONE,
                modelled_burning_cost_minor=3_337,
            ),
        ),
        "observed_burning_cost_minor": 18_412,
        "modelled_burning_cost_minor": 18_337,
        "tolerance": Decimal("0.02"),
        "computed_at": _datetime.datetime(2026, 8, 18, tzinfo=_datetime.UTC),
    }
    kwargs.update(overrides)
    return Reconciliation(**kwargs)  # type: ignore[arg-type]


# -- the method decides which model references are required ------------------------------


@pytest.mark.req("FR-MODEL-58")
def test_a_well_formed_structure_round_trips() -> None:
    structure = _structure()
    again = PerilStructure.model_validate(structure.model_dump(mode="json"))
    assert again == structure


@pytest.mark.req("FR-MODEL-58")
def test_frequency_severity_needs_both_models() -> None:
    with pytest.raises(pydantic.ValidationError, match="severity_model"):
        PerilComponent(
            peril="AD",
            method=PerilMethod.FREQUENCY_SEVERITY,
            frequency_model=AD_FREQ,
            large_loss=_none(),
        )


@pytest.mark.req("FR-MODEL-58")
def test_frequency_severity_refuses_a_burning_cost_model() -> None:
    """Both routes present is two answers to what the peril costs."""
    with pytest.raises(pydantic.ValidationError, match="burning_cost_model"):
        PerilComponent(
            peril="AD",
            method=PerilMethod.FREQUENCY_SEVERITY,
            frequency_model=AD_FREQ,
            severity_model=AD_SEV,
            burning_cost_model=WS_BC,
            large_loss=_none(),
        )


@pytest.mark.req("FR-MODEL-58")
def test_burning_cost_needs_its_model() -> None:
    with pytest.raises(pydantic.ValidationError, match="burning_cost_model"):
        PerilComponent(
            peril="WINDSCREEN", method=PerilMethod.BURNING_COST, large_loss=_none()
        )


@pytest.mark.req("FR-MODEL-58")
def test_burning_cost_refuses_frequency_or_severity_models() -> None:
    with pytest.raises(pydantic.ValidationError, match="frequency_model"):
        PerilComponent(
            peril="WINDSCREEN",
            method=PerilMethod.BURNING_COST,
            burning_cost_model=WS_BC,
            frequency_model=AD_FREQ,
            large_loss=_none(),
        )


# -- large-loss treatment ------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-59")
def test_capped_needs_a_cap_and_a_restoration_loading() -> None:
    with pytest.raises(pydantic.ValidationError, match="cap_minor"):
        LargeLossTreatment(
            kind=LargeLossKind.CAPPED,
            restoration_loading=Decimal("1.043"),
            evidence_blob=EVIDENCE,
        )
    with pytest.raises(pydantic.ValidationError, match="restoration_loading"):
        LargeLossTreatment(
            kind=LargeLossKind.CAPPED, cap_minor=2_500_000, evidence_blob=EVIDENCE
        )


@pytest.mark.req("FR-MODEL-59")
def test_a_restoration_loading_below_one_is_refused() -> None:
    """Restoration puts the capped mean *back*. Below 1 it caps a second time."""
    with pytest.raises(pydantic.ValidationError, match="restoration_loading"):
        _capped("0.98")


@pytest.mark.req("FR-MODEL-59")
def test_none_carries_no_parameters() -> None:
    with pytest.raises(pydantic.ValidationError, match="cap_minor"):
        LargeLossTreatment(kind=LargeLossKind.NONE, cap_minor=2_500_000)


@pytest.mark.req("FR-MODEL-59")
def test_separate_model_needs_an_excess_model_and_an_attachment() -> None:
    with pytest.raises(pydantic.ValidationError, match="attachment_minor"):
        LargeLossTreatment(
            kind=LargeLossKind.SEPARATE_MODEL, excess_model=EXCESS, evidence_blob=EVIDENCE
        )
    with pytest.raises(pydantic.ValidationError, match="excess_model"):
        LargeLossTreatment(
            kind=LargeLossKind.SEPARATE_MODEL,
            attachment_minor=100_000_000,
            evidence_blob=EVIDENCE,
        )


@pytest.mark.req("FR-MODEL-59")
def test_flat_loading_needs_its_factor() -> None:
    with pytest.raises(pydantic.ValidationError, match="loading_factor"):
        LargeLossTreatment(kind=LargeLossKind.FLAT_LOADING, evidence_blob=EVIDENCE)


@pytest.mark.req("FR-MODEL-59")
def test_every_treatment_but_none_carries_its_calibration_evidence() -> None:
    """FR-MODEL-59: "whatever is chosen is recorded with its calibration evidence".

    A restoration loading of 1.043 is a *number someone calibrated*. Without the evidence
    behind it, an approver is asked to accept it because it is written down.
    """
    with pytest.raises(pydantic.ValidationError, match="evidence_blob"):
        LargeLossTreatment(
            kind=LargeLossKind.CAPPED,
            cap_minor=2_500_000,
            restoration_loading=Decimal("1.043"),
        )
    assert LargeLossTreatment(kind=LargeLossKind.NONE).evidence_blob is None


# -- coherence across the structure --------------------------------------------------------


@pytest.mark.req("FR-MODEL-60")
def test_a_duplicate_peril_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="AD"):
        _structure(perils=(_ad(), _ad()))


@pytest.mark.req("FR-MODEL-60")
def test_a_peril_cannot_be_both_modelled_and_excluded() -> None:
    with pytest.raises(pydantic.ValidationError, match="AD"):
        _structure(
            excluded_perils=(ExcludedPeril(peril="AD", reason="Bundled service cost."),)
        )


@pytest.mark.req("FR-MODEL-60")
def test_an_exclusion_needs_a_reason() -> None:
    with pytest.raises(pydantic.ValidationError):
        ExcludedPeril(peril="COURTESY_CAR", reason="   ")


@pytest.mark.req("FR-MODEL-58")
def test_a_structure_with_no_perils_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError):
        _structure(perils=())


# -- the reconciliation --------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-60")
def test_status_and_ratio_are_derived_not_stored() -> None:
    """Within tolerance, so `pass` — and neither field can be asserted independently."""
    reconciliation = _reconciliation()
    assert reconciliation.ratio == Decimal("0.995927")
    assert reconciliation.status is ReconciliationStatus.PASS
    payload = reconciliation.model_dump(mode="json")
    assert payload["ratio"] == "0.995927"
    assert payload["status"] == "pass"


@pytest.mark.req("FR-MODEL-60")
def test_a_reconciliation_round_trips_through_its_own_serialised_form() -> None:
    """The derived fields **are** serialised, so any payload round-tripped back carries
    them — and `extra="forbid"` would otherwise reject the artifact's own output.

    They are dropped and recomputed rather than compared: a stored or hand-edited `ratio`
    then has no way to be believed, which is the guarantee "derived, not stored" is for.
    This is not hypothetical — the platform's `load_structure` hit it on the first run.
    """
    original = _reconciliation()
    again = Reconciliation.model_validate(original.model_dump(mode="json"))
    assert again == original

    tampered = original.model_dump(mode="json") | {"ratio": "9.999999", "status": "pass"}
    assert Reconciliation.model_validate(tampered).ratio == original.ratio


@pytest.mark.req("FR-MODEL-60")
def test_outside_the_declared_tolerance_is_a_fail() -> None:
    reconciliation = _reconciliation(
        modelled_burning_cost_minor=15_000,
        perils=(
            ReconciledPeril(
                peril="AD",
                large_loss_kind=LargeLossKind.NONE,
                modelled_burning_cost_minor=12_000,
            ),
            ReconciledPeril(
                peril="WINDSCREEN",
                large_loss_kind=LargeLossKind.NONE,
                modelled_burning_cost_minor=3_000,
            ),
        ),
    )
    assert reconciliation.status is ReconciliationStatus.FAIL


@pytest.mark.req("FR-MODEL-60")
def test_the_total_must_be_the_sum_of_the_perils() -> None:
    """FR-MODEL-58 sums over perils. A total that is not the sum is a third number."""
    with pytest.raises(pydantic.ValidationError, match="sum"):
        _reconciliation(modelled_burning_cost_minor=99_999)


@pytest.mark.req("FR-MODEL-60")
def test_a_non_positive_tolerance_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError):
        _reconciliation(tolerance=Decimal("0"))


@pytest.mark.req("FR-MODEL-60")
def test_reconciling_against_nothing_observed_is_refused() -> None:
    """A ratio needs a denominator; zero observed burning cost has none."""
    with pytest.raises(pydantic.ValidationError, match="observed"):
        _reconciliation(observed_burning_cost_minor=0)


@pytest.mark.req("FR-MODEL-74")
def test_the_reconciliation_states_each_perils_loss_treatment() -> None:
    """FR-MODEL-74 — a capped model reconciling to uncapped data reads as a modelling error
    unless the treatment is stated beside the number."""
    reconciliation = _reconciliation(
        perils=(
            ReconciledPeril(
                peril="AD",
                large_loss_kind=LargeLossKind.CAPPED,
                modelled_burning_cost_minor=15_000,
            ),
            ReconciledPeril(
                peril="WINDSCREEN",
                large_loss_kind=LargeLossKind.NONE,
                modelled_burning_cost_minor=3_337,
            ),
        )
    )
    treatments = {p.peril: p.large_loss_kind for p in reconciliation.perils}
    assert treatments == {"AD": LargeLossKind.CAPPED, "WINDSCREEN": LargeLossKind.NONE}


@pytest.mark.req("FR-MODEL-60")
def test_money_stays_integer_minor_units() -> None:
    with pytest.raises(pydantic.ValidationError):
        _reconciliation(observed_burning_cost_minor=18_412.5)


# -- the lifecycle -------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-61")
def test_a_structure_reaching_review_carries_its_reconciliation() -> None:
    """The approval policy's evidence kind *is* the reconciliation (`06` §4.2), so a
    structure in review without one is an approval with nothing to read."""
    with pytest.raises(pydantic.ValidationError, match="reconciliation"):
        _structure(status=PerilStructureStatus.REVIEW)

    reviewable = _structure(
        status=PerilStructureStatus.REVIEW, reconciliation=_reconciliation()
    )
    assert reviewable.reconciliation is not None


@pytest.mark.req("FR-MODEL-61")
def test_the_lifecycle_has_no_edge_from_draft_to_review() -> None:
    """The Model's lesson (FR-MODEL-64): a structure reaching an approver without its
    reconciliation is not a state to refuse later, it is a state with no edge into it."""
    assert (
        PerilStructureStatus.REVIEW
        not in VALID_PERIL_STRUCTURE_TRANSITIONS[PerilStructureStatus.DRAFT]
    )
    assert (
        PerilStructureStatus.REVIEW
        in VALID_PERIL_STRUCTURE_TRANSITIONS[PerilStructureStatus.RECONCILED]
    )


@pytest.mark.req("FR-MODEL-61")
def test_an_approved_structure_can_only_be_superseded() -> None:
    """A Rating Version references it (FR-MODEL-61); archiving would remove the referent
    while naming no replacement."""
    assert VALID_PERIL_STRUCTURE_TRANSITIONS[PerilStructureStatus.APPROVED] == frozenset(
        {PerilStructureStatus.SUPERSEDED}
    )
