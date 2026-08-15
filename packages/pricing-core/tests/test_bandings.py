"""Bandings against data whose bands are known (`02` FR-MODEL-8..12).

The proposals are checked against what the method *means* — an exposure quantile puts equal
exposure in each band, not equal rows — and the rest is refusal. `02` FR-MODEL-8 makes the
handling of nulls and out-of-range values explicit precisely so that the silent case cannot
exist, and a test suite that only exercises the happy path would not notice it had come
back.
"""

from __future__ import annotations

import math
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    AboveRangePolicy,
    Banding,
    BandingMethod,
    BandingProposal,
    BelowRangePolicy,
)
from pricing_core.modelling import (
    BandingError,
    FactorResolutionError,
    apply_banding,
    band_statistics,
    check_banding,
    propose_banding,
)

DATASET = uuid4()
VERSION = uuid4()


def _book(n: int = 10_000, seed: int = 20260815) -> pl.DataFrame:
    """A book whose exposure is deliberately **not** uniform in age.

    Young drivers hold a third of the rows and a tenth of the exposure, which is the case
    that separates `quantile` from `exposure_quantile`. On a uniform book the two agree and
    a test on one would silently pass for the other.
    """
    rng = np.random.default_rng(seed)
    age = np.concatenate(
        [rng.integers(18, 26, n // 3), rng.integers(26, 80, n - n // 3)]
    ).astype(float)
    exposure = np.where(age < 26, 0.1, 1.0)
    counts = rng.poisson(np.exp(np.log(exposure) - 2.0 - 0.02 * (age - 40)))
    return pl.DataFrame(
        {
            "driver_age": age,
            "exposure_years": exposure,
            "claim_count": counts.astype(float),
            "claim_amount_minor": (counts * 150_000).astype(np.int64),
        }
    )


def _proposal(**over: object) -> BandingProposal:
    base: dict[str, object] = {
        "dataset_version_id": VERSION,
        "column": "driver_age",
        "method": BandingMethod.EXPOSURE_QUANTILE,
        "n_bands": 5,
    }
    base.update(over)
    return BandingProposal(**base)  # type: ignore[arg-type]


def _manual(**over: object) -> Banding:
    base: dict[str, object] = {
        "id": uuid4(), "slug": "age", "dataset_id": DATASET, "version": 1,
        "column": "driver_age", "method": BandingMethod.MANUAL,
        "boundaries": (18.0, 30.0, 50.0, 80.0), "labels": ("18-29", "30-49", "50+"),
    }
    base.update(over)
    return Banding(**base)  # type: ignore[arg-type]


# --- the shape of a Banding -------------------------------------------------------------


@pytest.mark.req("FR-MODEL-8")
def test_boundaries_must_strictly_increase() -> None:
    """Equal cut points make an empty band; a decreasing pair makes an overlapping one."""
    with pytest.raises(ValueError, match="strictly increase"):
        _manual(boundaries=(18.0, 30.0, 30.0, 80.0), labels=("a", "b", "c"))
    with pytest.raises(ValueError, match="strictly increase"):
        _manual(boundaries=(18.0, 50.0, 30.0, 80.0), labels=("a", "b", "c"))


@pytest.mark.req("FR-MODEL-8")
def test_a_label_list_one_short_is_refused() -> None:
    """It does not drop the last band — it renames every band after the gap."""
    with pytest.raises(ValueError, match="labels for 3 bands"):
        _manual(labels=("18-29", "30-49"))


@pytest.mark.req("FR-MODEL-8")
def test_two_bands_cannot_share_a_label() -> None:
    with pytest.raises(ValueError, match="repeats a label"):
        _manual(labels=("same", "same", "50+"))


@pytest.mark.req("FR-MODEL-8")
def test_the_null_level_cannot_also_be_a_band() -> None:
    with pytest.raises(ValueError, match="also a"):
        _manual(null_level="30-49")


# --- proposing --------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-9")
def test_exposure_quantiles_split_exposure_not_rows() -> None:
    """The actuarial default, and the one a row quantile silently substitutes for.

    Each band must hold roughly a fifth of the *exposure*. On this book a row-quantile
    banding would put a third of the rows — and a tenth of the exposure — in the first band.
    """
    frame = _book()
    banding = propose_banding(frame, _proposal(), dataset_id=DATASET, slug="age-5")

    shares = [float(row.exposure_years) for row in banding.band_stats]
    total = sum(shares)
    assert len(shares) == 5
    for share in shares:
        assert abs(share / total - 0.2) < 0.05, shares


@pytest.mark.req("FR-MODEL-9")
def test_row_quantiles_and_exposure_quantiles_disagree_on_a_skewed_book() -> None:
    """If they agreed the previous test would prove nothing about which one ran."""
    frame = _book()
    by_rows = propose_banding(
        frame, _proposal(method=BandingMethod.QUANTILE), dataset_id=DATASET, slug="a"
    )
    by_exposure = propose_banding(frame, _proposal(), dataset_id=DATASET, slug="b")
    assert by_rows.boundaries != by_exposure.boundaries


@pytest.mark.req("FR-MODEL-9")
def test_equal_width_bands_are_equally_wide() -> None:
    frame = _book()
    banding = propose_banding(
        frame, _proposal(method=BandingMethod.EQUAL_WIDTH, n_bands=4),
        dataset_id=DATASET, slug="age-eq",
    )
    widths = [b - a for a, b in zip(banding.boundaries, banding.boundaries[1:], strict=False)]
    assert max(widths) - min(widths) < 1e-9


@pytest.mark.req("FR-MODEL-9")
def test_credibility_merges_until_every_band_meets_the_minimum() -> None:
    """FR-MODEL-9's `credibility`: merge until each band carries enough claims.

    Asked for twenty bands with a floor no twentieth of this book can meet, it must come
    back with fewer — and every one of them at or above the floor.
    """
    frame = _book()
    banding = propose_banding(
        frame,
        _proposal(
            method=BandingMethod.CREDIBILITY,
            n_bands=20,
            method_params={"min_claims_per_band": 150.0},
        ),
        dataset_id=DATASET,
        slug="age-cred",
    )
    assert len(banding.labels) < 20
    assert all(row.claim_count >= 150 for row in banding.band_stats[:-1])


@pytest.mark.req("FR-MODEL-10")
def test_a_proposal_carries_its_evidence() -> None:
    """FR-MODEL-10: exposure, claims, frequency and an interval, as of derivation.

    Without it a reviewer has to re-run the derivation to see whether a band is thin, which
    is the work the requirement exists to avoid.
    """
    banding = propose_banding(_book(), _proposal(), dataset_id=DATASET, slug="age-5")
    assert banding.derived_on_dataset_version_id == VERSION
    assert len(banding.band_stats) == len(banding.labels)
    for row in banding.band_stats:
        assert row.claim_count > 0
        assert row.frequency is not None
        low, high = row.frequency_ci or (0.0, 0.0)
        assert low < row.frequency < high


@pytest.mark.req("FR-MODEL-10")
def test_band_statistics_come_back_in_band_order() -> None:
    """`10-14` sorts before `5-9` as text, and a shuffled relativity chart reads as noise."""
    frame = pl.DataFrame(
        {
            "v": [1.0, 6.0, 11.0, 16.0],
            "exposure_years": [1.0, 1.0, 1.0, 1.0],
            "claim_count": [1.0, 1.0, 1.0, 1.0],
            "claim_amount_minor": [100, 100, 100, 100],
        }
    )
    banding = Banding(
        id=uuid4(), slug="v", dataset_id=DATASET, version=1, column="v",
        method=BandingMethod.MANUAL, boundaries=(0.0, 5.0, 10.0, 15.0, 20.0),
        labels=("0-4", "5-9", "10-14", "15+"),
    )
    assert [row.level for row in band_statistics(frame, banding)] == list(banding.labels)


@pytest.mark.req("FR-MODEL-9")
def test_a_manual_banding_has_nothing_to_propose() -> None:
    """Inventing boundaries to be edited would put the platform's name on the actuary's."""
    with pytest.raises(BandingError, match="nothing to propose"):
        propose_banding(
            _book(), _proposal(method=BandingMethod.MANUAL), dataset_id=DATASET, slug="m"
        )


@pytest.mark.req("FR-MODEL-9")
def test_tree_boundaries_are_refused_by_name_not_substituted() -> None:
    """A quantile banding recorded as `tree` is a method recorded as one it is not."""
    with pytest.raises(BandingError, match="tree"):
        propose_banding(
            _book(), _proposal(method=BandingMethod.TREE), dataset_id=DATASET, slug="t"
        )


@pytest.mark.req("FR-MODEL-9")
def test_exposure_quantiles_refuse_a_book_with_no_exposure_column() -> None:
    frame = _book().drop("exposure_years")
    with pytest.raises(BandingError, match="exposure_quantile"):
        propose_banding(frame, _proposal(), dataset_id=DATASET, slug="x")


# --- applying ---------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-8")
def test_the_outermost_bands_are_closed_at_both_ends() -> None:
    """Otherwise a banding derived from the observed range rejects its own maximum."""
    frame = _book()
    banding = propose_banding(frame, _proposal(), dataset_id=DATASET, slug="age-5")
    labels = apply_banding(frame["driver_age"], banding)
    assert labels.null_count() == 0
    assert set(labels.unique().to_list()) <= set(banding.labels)


@pytest.mark.req("FR-MODEL-8")
def test_a_value_below_the_range_is_refused_when_the_policy_says_error() -> None:
    banding = _manual()
    with pytest.raises(FactorResolutionError, match="below the banded range"):
        apply_banding(pl.Series("driver_age", [3.0, 40.0]), banding)


@pytest.mark.req("FR-MODEL-8")
def test_a_value_above_the_range_can_be_clamped_when_the_policy_says_so() -> None:
    banding = _manual(above_range=AboveRangePolicy.CLAMP_TO_LAST)
    labels = apply_banding(pl.Series("driver_age", [95.0, 40.0]), banding)
    assert labels.to_list() == ["50+", "30-49"]


@pytest.mark.req("FR-MODEL-8")
def test_a_null_is_not_a_band_unless_the_banding_says_it_is() -> None:
    """A missing driver age is a missing value; mapping it to a band prices it as known."""
    with pytest.raises(FactorResolutionError, match="null value"):
        apply_banding(pl.Series("driver_age", [None, 40.0], dtype=pl.Float64), _manual())

    banded = _manual(null_level="unknown")
    labels = apply_banding(pl.Series("driver_age", [None, 40.0], dtype=pl.Float64), banded)
    assert labels.to_list() == ["unknown", "30-49"]


@pytest.mark.req("FR-MODEL-8")
def test_a_right_closed_banding_puts_a_boundary_in_the_lower_band() -> None:
    """`closed` is a real choice, not decoration: 30 belongs to `(18,30]` on the right."""
    left = _manual()
    right = _manual(closed="right")
    values = pl.Series("driver_age", [30.0])
    assert apply_banding(values, left).to_list() == ["30-49"]
    assert apply_banding(values, right).to_list() == ["18-29"]


# --- validating against a version -------------------------------------------------------


@pytest.mark.req("FR-MODEL-11")
def test_an_empty_band_always_fails() -> None:
    """A level no row reaches still gets a coefficient — estimated from nothing."""
    frame = pl.DataFrame(
        {
            "driver_age": [20.0, 22.0, 70.0],
            "exposure_years": [1.0, 1.0, 1.0],
            "claim_count": [1.0, 0.0, 1.0],
            "claim_amount_minor": [100, 0, 100],
        }
    )
    with pytest.raises(BandingError, match=r"BAND_EMPTY|no row of this dataset") as caught:
        check_banding(frame, _manual())
    assert caught.value.code == "BAND_EMPTY"


@pytest.mark.req("FR-MODEL-11")
def test_a_thin_band_warns_by_default_and_fails_when_configured() -> None:
    """FR-MODEL-11's own wording: warns (default) or fails (if configured)."""
    frame = _book()
    banding = propose_banding(frame, _proposal(), dataset_id=DATASET, slug="age-5")

    warnings = check_banding(frame, banding, min_claims=10_000)
    assert warnings
    assert all("below the minimum" in w for w in warnings)

    with pytest.raises(BandingError) as caught:
        check_banding(frame, banding, min_claims=10_000, fail_on_thin=True)
    assert caught.value.code == "BAND_BELOW_MIN_EXPOSURE"


@pytest.mark.req("FR-MODEL-11")
def test_a_banding_that_fits_the_version_reports_nothing() -> None:
    frame = _book()
    banding = propose_banding(frame, _proposal(), dataset_id=DATASET, slug="age-5")
    assert check_banding(frame, banding) == ()


@pytest.mark.req("FR-MODEL-8")
def test_a_column_of_one_value_cannot_be_banded() -> None:
    """Every proposed boundary collapses onto the same point; the honest answer is no."""
    frame = pl.DataFrame(
        {
            "driver_age": [40.0] * 50,
            "exposure_years": [1.0] * 50,
            "claim_count": [1.0] * 50,
            "claim_amount_minor": [100] * 50,
        }
    )
    with pytest.raises(BandingError, match="too few distinct values"):
        propose_banding(frame, _proposal(), dataset_id=DATASET, slug="flat")


@pytest.mark.req("FR-MODEL-8")
def test_the_below_range_policy_can_send_a_value_to_the_null_level() -> None:
    banding = _manual(below_range=BelowRangePolicy.NULL_LEVEL, null_level="unknown")
    labels = apply_banding(pl.Series("driver_age", [3.0, 40.0]), banding)
    assert labels.to_list() == ["unknown", "30-49"]


@pytest.mark.req("FR-MODEL-8")
def test_a_policy_pointing_at_a_null_level_that_does_not_exist_is_refused() -> None:
    banding = _manual(below_range=BelowRangePolicy.NULL_LEVEL)
    with pytest.raises(FactorResolutionError, match="declares none"):
        apply_banding(pl.Series("driver_age", [3.0, 40.0]), banding)


@pytest.mark.req("FR-MODEL-10")
def test_the_published_frequency_reconciles_with_the_published_counts() -> None:
    """A reader dividing the printed claims by the printed exposure gets the printed rate."""
    banding = propose_banding(_book(), _proposal(), dataset_id=DATASET, slug="age-5")
    for row in banding.band_stats:
        assert row.frequency is not None
        assert math.isclose(
            row.frequency, row.claim_count / float(row.exposure_years), rel_tol=1e-9
        )
