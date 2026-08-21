"""The Tweedie series density for 1 < p < 2 (Dunn & Smyth 2005).

FR-MODEL-22's estimate is the argmax of the profile log-likelihood
`L(p) = sum_i w_i log f(y_i; mu_i(p), phi_hat(p), p)`, so the density `f` is the whole
point of the mechanism: the deviance `glum` reports is not a likelihood profile for
Tweedie — the saturated-model term and the p-dependent normaliser do not cancel out of
the argmin — and the spec's 2026-08-21 amendment records that the deviance argmin was
measured biased. This module evaluates the series representation of `f` exactly as the
R `tweedie` package's `dtweedie_series` does: the point mass `exp(-lambda)` at `y = 0`
and, for `y > 0`, the compound-Poisson-Gamma term sum, all in log space with a running
log-sum-exp and the reference implementation's `drop = 37` accuracy constant.

The terms are unimodal in the term index `j` with the mode near
`j_max = y^(2-p) / (phi (2-p))`, so a row-by-row early exit once a term falls more than
37 log-units below the running maximum loses nothing float64 can represent.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from scipy.special import gammaln

#: The reference implementation's accuracy constant: a term more than `_DROP` log-units
#: below the running maximum contributes less than `e^-37 ~ 1e-16` of it, so stopping
#: there loses nothing representable in float64.
_DROP = 37.0


def tweedie_log_density(
    y: npt.NDArray[np.float64],
    mu: npt.NDArray[np.float64],
    phi: float,
    power: float,
) -> npt.NDArray[np.float64]:
    """log f(y; mu, phi, power) for the Tweedie family with 1 < power < 2, vectorized.

    `f(0) = exp(-lambda)` is the exact zero mass; for `y > 0` the series density is
    evaluated in log space — every quantity here is a log, and the term sum is a running
    log-sum-exp with the max-subtraction trick, so nothing large is ever exponentiated.

    With `alpha = (2-power)/(1-power)` (negative) and `alpha1 = 1 - alpha`:
    `tau = phi (power-1) mu^(power-1)` and `lambda = mu^(2-power) / (phi (2-power))`;
    for `y > 0`, `r = -alpha log y + alpha log(power-1) - alpha1 log phi - log(2-power)`
    and `log f = -y/tau - lambda - log y + log sum_j exp(r j - lgamma(1+j) - lgamma(-alpha j))`
    over `j = 1, 2, ...` — the mu dependence lives entirely in `tau` and `lambda`.
    """
    y = np.asarray(y, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    if y.shape != mu.shape:
        raise ValueError(
            f"y and mu must have the same shape, got {y.shape} and {mu.shape}"
        )
    if not np.all(y >= 0.0):
        raise ValueError("y must be non-negative — the Tweedie response is a cost or a claim count")
    if not np.all(mu > 0.0):
        raise ValueError(
            "mu must be strictly positive — the fitted mean of a log-link Tweedie GLM is"
        )
    if not (phi > 0.0):
        raise ValueError(f"phi must be strictly positive, got {phi}")
    if not (1.0 < power < 2.0):
        raise ValueError(
            f"power must lie strictly inside (1, 2), got {power} — at 1 the family is "
            "Poisson and at 2 it is Gamma, and the series representation is not defined there"
        )

    alpha = (2.0 - power) / (1.0 - power)  # negative
    alpha1 = 1.0 - alpha
    tau = phi * (power - 1.0) * mu ** (power - 1.0)
    lam = mu ** (2.0 - power) / (phi * (2.0 - power))

    log_f = np.empty(y.shape, dtype=np.float64)
    at_zero = y == 0.0
    log_f[at_zero] = -lam[at_zero]

    positive = ~at_zero
    if np.any(positive):
        y_pos = y[positive]
        r = (
            -alpha * np.log(y_pos)
            + alpha * np.log(power - 1.0)
            - alpha1 * np.log(phi)
            - np.log(2.0 - power)
        )
        log_f[positive] = (
            -y_pos / tau[positive] - lam[positive] - np.log(y_pos) + _series_logsum(r, alpha)
        )
    return log_f


def _series_logsum(
    r: npt.NDArray[np.float64],
    alpha: float,
) -> npt.NDArray[np.float64]:
    """log(sum_j exp(r*j - lgamma(1+j) - lgamma(-alpha*j))) over j = 1, 2, ..., per row.

    The terms are unimodal in `j` (mode near `y^(2-p)/(phi (2-p))`, clipped to >= 1), so
    a running log-sum-exp can stop each row once its term falls more than `_DROP` below
    the running maximum: the remaining tail is then less than `e^-37` of the largest
    term. Rows that have already converged drop out of the loop while the rest continue.
    """
    log_sum = np.zeros(r.shape, dtype=np.float64)  # log of sum of exp(term - running max)
    running_max = np.full(r.shape, -np.inf, dtype=np.float64)
    active = np.ones(r.shape, dtype=bool)
    j = 1
    while np.any(active):
        logt = r[active] * j - gammaln(1.0 + j) - gammaln(-alpha * j)
        new_max = np.maximum(running_max[active], logt)
        log_sum[active] = np.logaddexp(
            log_sum[active] + running_max[active] - new_max, logt - new_max,
        )
        running_max[active] = new_max
        active[active] = logt >= running_max[active] - _DROP
        j += 1
    return log_sum + running_max
