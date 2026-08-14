"""03 R2 / FR-RATE-29: decimal-safe arithmetic in the rating path."""

from decimal import Decimal

import pytest

from pricing_core.money import apply_factor


@pytest.mark.req("FR-RATE-29")
def test_factor_application_is_exact_and_the_mode_decides_ties():
    """24150 * 1.15 is exactly 27772.5 — a tie, so the rounding mode alone decides.

    Worth pinning: the intuitive answer is 27773 (half-up), and half-even gives 27772.
    Applied across a portfolio that difference is real money, which is why FR-RATE-12
    makes the mode an explicit, per-step declaration rather than a default.
    """
    assert Decimal(24150) * Decimal("1.15") == Decimal("27772.5")
    assert apply_factor(24150, Decimal("1.15"), "half_even") == 27772
    assert apply_factor(24150, Decimal("1.15"), "half_up") == 27773


@pytest.mark.req("FR-OVR-7")
def test_float_factor_is_refused():
    """A float factor is the quiet way binary rounding re-enters the rating path."""
    with pytest.raises(TypeError, match="must be Decimal"):
        apply_factor(24150, 1.15, "half_even")  # type: ignore[arg-type]


@pytest.mark.req("FR-RATE-12")
def test_rounding_mode_changes_the_answer_and_so_must_be_declared():
    """If mode never mattered, requiring it would be ceremony. It matters."""
    assert apply_factor(1, Decimal("2.5"), "half_even") == 2
    assert apply_factor(1, Decimal("2.5"), "half_up") == 3
