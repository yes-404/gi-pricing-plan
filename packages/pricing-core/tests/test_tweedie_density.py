"""FR-114: the Tweedie series density, in log space, negative cases first.

The density is the whole point of the mechanism: the estimated power is the argmax of
the profile log-likelihood, and the profile is informative only because the density
carries the p-dependent normaliser (02 §3.4 amendment 2026-08-21). These tests pin the
density itself — the exact mass at zero, the two identities that make the series a
density (it integrates to the remaining mass, and its mean is mu), and finiteness
across the y range the fit path sees.
"""

from __future__ import annotations

import numpy as np
import pytest

from pricing_core.modelling.tweedie_density import tweedie_log_density


@pytest.mark.req("FR-114")
def test_the_density_at_zero_is_the_exact_mass() -> None:
    """Negative first: outside the support the density is not defined, and a number for
    an impossible input would let a broken book score as if it were fine — y < 0, mu <= 0,
    phi <= 0 and power outside (1, 2) each raise. Then the positive claim: f(0) is the
    exact point mass exp(-lambda) of the compound-Poisson-Gamma representation — the
    probability of zero claims — which the series part must integrate to (test 2)."""
    y = np.array([1.0, 2.0])
    mu = np.array([1.0, 2.0])
    with pytest.raises(ValueError, match="y must be non-negative"):
        tweedie_log_density(np.array([-1.0, 1.0]), mu, 1.0, 1.5)
    with pytest.raises(ValueError, match="mu must be strictly positive"):
        tweedie_log_density(y, np.array([0.0, 1.0]), 1.0, 1.5)
    with pytest.raises(ValueError, match="mu must be strictly positive"):
        tweedie_log_density(y, np.array([-1.0, 1.0]), 1.0, 1.5)
    with pytest.raises(ValueError, match="phi must be strictly positive"):
        tweedie_log_density(y, mu, 0.0, 1.5)
    with pytest.raises(ValueError, match="phi must be strictly positive"):
        tweedie_log_density(y, mu, -1.0, 1.5)
    with pytest.raises(ValueError, match="power must lie strictly inside"):
        tweedie_log_density(y, mu, 1.0, 1.0)
    with pytest.raises(ValueError, match="power must lie strictly inside"):
        tweedie_log_density(y, mu, 1.0, 2.0)

    for mu_val, phi, power in ((4.48, 1.0, 1.5), (1.0, 1.0, 1.5), (400.0, 40.0, 1.5)):
        lam = mu_val ** (2.0 - power) / (phi * (2.0 - power))
        log_f = tweedie_log_density(np.array([0.0]), np.array([mu_val]), phi, power)
        assert log_f[0] == pytest.approx(-lam)
        assert np.exp(log_f[0]) == pytest.approx(np.exp(-lam))


@pytest.mark.req("FR-114")
@pytest.mark.parametrize(
    ("mu_val", "phi", "power"),
    [(4.48, 1.0, 1.5), (1.0, 1.0, 1.5), (400.0, 40.0, 1.5)],
)
def test_the_density_integrates_to_the_nonzero_mass(
    mu_val: float, phi: float, power: float,
) -> None:
    """The continuous part integrates to the remaining mass and its mean is mu — the two
    identities that make the series the density of the model the fit claims. Tolerances
    are integration error only: a log-spaced grid is coarse where the density is flat."""
    lam = mu_val ** (2.0 - power) / (phi * (2.0 - power))
    y = np.geomspace(1e-6, 40.0 * mu_val, 20_000)
    log_f = tweedie_log_density(y, np.full_like(y, mu_val), phi, power)
    f = np.exp(log_f)
    assert np.trapezoid(f, y) == pytest.approx(1.0 - np.exp(-lam), abs=1e-2)
    assert np.trapezoid(y * f, y) == pytest.approx(mu_val, rel=1e-2)


@pytest.mark.req("FR-114")
@pytest.mark.parametrize(
    ("mu_val", "phi", "power"),
    [(4.48, 1.0, 1.5), (1.0, 1.0, 1.5), (400.0, 40.0, 1.5)],
)
def test_the_density_is_positive_and_finite(
    mu_val: float, phi: float, power: float,
) -> None:
    """Across the y range the fit path sees — very small claims, the mean, and mu*20 —
    log f is finite and exp(log f) > 0: no underflow to zero (which would log to -inf
    and poison the profile sum) and no overflow."""
    y = np.array([1e-6, 0.01, mu_val, 2.0 * mu_val, 5.0 * mu_val, 20.0 * mu_val])
    log_f = tweedie_log_density(y, np.full_like(y, mu_val), phi, power)
    assert np.all(np.isfinite(log_f))
    assert np.all(np.exp(log_f) > 0.0)
