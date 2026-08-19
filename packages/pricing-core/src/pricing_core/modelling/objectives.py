"""Custom Objectives: the template catalogue, its derivatives, and certification.

`02` §3.7 (FR-MODEL-38..48, 68/69/70, 75/76), §4.5's catalogue, §4.7's certificate, §5.2.

**Phase 1 is templates only** (FR-MODEL-75). `model_schema.CustomObjective` refuses to be
constructed with `kind: expression` at all, so nothing here has to guard against one — the
two Phase-2 entry points `parse_expression` and `derive_derivatives` are *not* stubbed here
either. A stub is a shape a caller can import and a test can pretend to exercise; their
absence is the same statement the flag makes, in the one place a Phase-2 author will look.

**What a template is, here.** Three vectorised functions of `(y, f, params)` — loss,
gradient and hessian with respect to the raw score `f` — plus, where the loss is piecewise,
the `f` at which its branch flips. `w` never enters them: every template's loss is linear
in the case weight, so `compile_objective` multiplies once and the templates stay readable.
That is not a convenience, it is the property FR-MODEL-48's fit path depends on — a weight
that entered the arithmetic could change the *sign* of a hessian, and the clipping strategy
is chosen against the unweighted shape.

**Every template is log-link except `focal_binomial`**, which is logistic. `μ = exp(f)`
throughout, so the offset (`base_margin`, FR-MODEL-72) is additive in `f` and multiplicative
in `μ` — the same arithmetic the built-in objectives use, which is what lets a custom
objective be swapped for `count:poisson` without touching anything else in `GbmSpec`.

**Certification is the point of the module** (FR-MODEL-76). `certify_objective` is not a
test helper: it is the machinery §4.7 requires, run on templates in Phase 1 so that the
first user-authored loss in Phase 2 meets a path that has been running for a phase. It is
also, incidentally, the best test these 24 analytic derivatives could have — every one of
them is checked against a Richardson-extrapolated numeric derivative of its own loss, so a
sign error anywhere in this file fails a check with the template's name on it.

ADR-0001 holds. Nothing here allocates an id or reads a clock: `certify_objective` returns
a `CertificateResult`, and the platform wraps it in the `ObjectiveCertificate` that carries
the id, the job and the timestamp — exactly the `compute_diagnostics`/`DiagnosticsResult`
split, and a divergence from §5.2's declared return type recorded there with its date.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Final, Literal

import numpy as np
import numpy.typing as npt

from model_schema import (
    TEMPLATE_PARAMETERS,
    CertificateCheck,
    CertificateResult,
    CheckStatus,
    CustomObjective,
    HessianStrategy,
    ObjectiveTemplate,
    ResponseKind,
    SamplingSpec,
    YDomain,
)
from pricing_core.modelling.errors import NonFiniteDerivativeError, ObjectiveError
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = [
    "ObjectiveFns",
    "certify_objective",
    "compile_objective",
    "make_lgb_objective",
    "make_xgb_objective",
    "template_loss",
]

#: Vectorised arrays throughout; the templates are written against `np.float64` only.
_Arr = npt.NDArray[np.float64]
#: A boolean selection over one of them.
_Mask = npt.NDArray[np.bool_]

#: The finite-difference step. `1e-6` is what §4.7's example records, and FR-MODEL-70 is
#: the requirement that says why it is not used: truncation error alone reaches ~4e-4 there
#: on a steeply-curved loss. With Richardson extrapolation the error scales as `h**4`, so a
#: *larger* step is strictly better — it moves the comparison away from the cancellation
#: floor without paying for it in truncation.
_STEP: Final = 1e-4

#: Where a Richardson-extrapolated central difference lands on a smooth loss. Anything
#: above this and below `_TOLERANCE_WARN` is a finding rather than a failure: a genuinely
#: stiff loss can miss the tight figure without being wrong, and FR-MODEL-70's whole point
#: is that a fixed tight tolerance is not meaningful.
_TOLERANCE_PASS: Final = 1e-6
_TOLERANCE_WARN: Final = 1e-3


# --------------------------------------------------------------------------------------
# The catalogue (§4.5, FR-MODEL-39)
# --------------------------------------------------------------------------------------

_P = Mapping[str, float]
_Fn = Callable[[_Arr, _Arr, _P], _Arr]
#: `(y, params) -> f` values at which a piecewise loss flips branch. Empty when smooth.
_Boundaries = Callable[[_Arr, _P], tuple[_Arr, ...]]


@dataclass(frozen=True)
class _Template:
    """One catalogue entry: its arithmetic, its kinks, and the `y` worth sampling at.

    `gauss_newton` is present only where the loss is a least-squares one, because that is
    where a Gauss-Newton hessian is *defined* — dropping the curvature-of-residual term.
    Offering it on the others would have meant inventing a positive-definite surrogate and
    letting the author believe it was the named strategy.
    """

    loss: _Fn
    grad: _Fn
    hess: _Fn
    gauss_newton: _Fn | None = None
    f_boundaries: _Boundaries | None = None
    #: `y` values where the loss changes form. Not excluded from the derivative check — a
    #: central difference in `f` never straddles one — but reported under FR-MODEL-69, and
    #: sampled at deliberately, since a uniform grid over `[0, 1e7]` hits `y = 0` never.
    y_anchors: Callable[[_P], tuple[float, ...]] | None = None
    #: What the branch *is*, for the certificate's prose. `None` where the loss is smooth.
    branch_description: str | None = None
    #: `g^-1`, the transform from the booster's score to the mean. Every template here
    #: models `mu = exp(f)` bar the binomial one; it is recorded rather than inferred
    #: because a custom objective leaves the backend with no link of its own, so scoring
    #: has nothing else to read.
    inverse_link: Literal["exp", "logistic"] = "exp"


def _mu(f: _Arr) -> _Arr:
    return np.exp(f)


# --- Poisson ---------------------------------------------------------------------------


def _poisson_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _mu(f) - y * f


def _poisson_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _mu(f) - y


def _poisson_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _mu(f)


# --- Gamma -----------------------------------------------------------------------------


def _gamma_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return y * np.exp(-f) + f


def _gamma_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return 1.0 - y * np.exp(-f)


def _gamma_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return y * np.exp(-f)


# --- Tweedie ---------------------------------------------------------------------------


def _tweedie_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    power = p["p"]
    return -y * np.exp((1.0 - power) * f) / (1.0 - power) + np.exp((2.0 - power) * f) / (
        2.0 - power
    )


def _tweedie_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    power = p["p"]
    return -y * np.exp((1.0 - power) * f) + np.exp((2.0 - power) * f)


def _tweedie_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    power = p["p"]
    return -y * (1.0 - power) * np.exp((1.0 - power) * f) + (2.0 - power) * np.exp(
        (2.0 - power) * f
    )


# --- Capped Gamma ----------------------------------------------------------------------
#
# §4.5 reads "Gamma loss on `min(y, cap)`, plus a recorded loading to restore the uncapped
# mean". Only the first half is an objective: the loading is a ratio of two sample means
# and cannot be computed from `(y, f)` one row at a time. It is `LossTreatment`'s
# `flat_loading` (FR-MODEL-73), which `apply_loss_treatment` already computes and
# `reconcile` already reports — so capping here and loading there is the same arithmetic
# the built-in path performs, not a gap. Recorded as a §4.5 note dated 2026-08-18.


def _capped(y: _Arr, p: _P) -> _Arr:
    return np.minimum(y, p["cap"])


def _capped_gamma_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _gamma_loss(_capped(y, p), f, p)


def _capped_gamma_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _gamma_grad(_capped(y, p), f, p)


def _capped_gamma_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _gamma_hess(_capped(y, p), f, p)


def _capped_gamma_anchors(p: _P) -> tuple[float, ...]:
    return (float(p["cap"]),)


# --- Spliced severity ------------------------------------------------------------------
#
# A Gamma body and a Pareto tail whose **scale is `μ`** — which is what ties the tail to
# the model at all. The alternative reading of §4.5, a Pareto with a fixed scale of
# `threshold`, contains no `μ`: its gradient is identically zero and the large claims then
# contribute nothing to the fit, which is not "one model" but two with the second discarded.
# Here a tail row pushes `μ` up with constant force `tail_shape`, and its hessian is zero —
# so `hessian_min` does the work, and the certificate says so.


def _spliced_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    alpha = p["tail_shape"]
    tail = y > p["threshold"]
    body = y * np.exp(-f) + f
    # `log y` is finite because the template's `y_domain` is `y > 0`.
    upper = -alpha * f + (alpha + 1.0) * np.log(np.where(tail, y, 1.0)) - math.log(alpha)
    return np.where(tail, upper, body)


def _spliced_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    tail = y > p["threshold"]
    return np.where(tail, -p["tail_shape"], 1.0 - y * np.exp(-f))


def _spliced_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    tail = y > p["threshold"]
    return np.where(tail, 0.0, y * np.exp(-f))


def _spliced_anchors(p: _P) -> tuple[float, ...]:
    return (float(p["threshold"]),)


# --- Asymmetric squared ----------------------------------------------------------------


def _asym_weight(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return np.where(_mu(f) < y, p["w_under"], p["w_over"])


def _asym_sq_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _asym_weight(y, f, p) * (y - _mu(f)) ** 2


def _asym_sq_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    mu = _mu(f)
    return 2.0 * _asym_weight(y, f, p) * (mu - y) * mu


def _asym_sq_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    mu = _mu(f)
    return 2.0 * _asym_weight(y, f, p) * (2.0 * mu - y) * mu


def _asym_sq_gn(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return 2.0 * _asym_weight(y, f, p) * _mu(f) ** 2


def _log_y_boundary(y: _Arr, p: _P) -> tuple[_Arr, ...]:
    with np.errstate(divide="ignore"):
        return (np.where(y > 0.0, np.log(np.where(y > 0.0, y, 1.0)), -np.inf),)


# --- Asymmetric Poisson ----------------------------------------------------------------


def _asym_pois_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    """`c(y, f)` times the Poisson unit **deviance**, not the negative log-likelihood.

    The distinction is the whole template. `mu - y*f` is a log-likelihood term: it is
    negative over most of the domain and it does not vanish where the prediction is right,
    so scaling it by `w_under` on one side of `mu = y` and `w_over` on the other makes the
    loss *discontinuous at the point it is supposed to reward* — and, since `w_under > 1`
    multiplies a negative number into a smaller one, it penalises under-prediction by making
    it cheaper. Certification found this: `minimum_at_truth` reported that stepping away
    from the stationary point lowered the loss.

    The unit deviance `2(y*log(y/mu) - y + mu)` is non-negative and zero exactly at
    `mu = y`, so the asymmetric weight scales a penalty rather than a likelihood, the two
    branches meet at zero, and the minimum stays at `f = log y` while the *slopes* either
    side of it differ — which is what an asymmetric pricing loss is for.
    """
    mu = _mu(f)
    positive = y > 0.0
    cross_entropy = np.where(positive, y * (np.log(np.where(positive, y, 1.0)) - f), 0.0)
    return _asym_weight(y, f, p) * 2.0 * (cross_entropy - y + mu)


def _asym_pois_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _asym_weight(y, f, p) * 2.0 * (_mu(f) - y)


def _asym_pois_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _asym_weight(y, f, p) * 2.0 * _mu(f)


# --- Huber and pseudo-Huber ------------------------------------------------------------


def _huber_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    delta = p["delta"]
    r = y - _mu(f)
    return np.where(np.abs(r) <= delta, 0.5 * r**2, delta * (np.abs(r) - 0.5 * delta))


def _huber_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    delta = p["delta"]
    mu = _mu(f)
    r = y - mu
    return np.where(np.abs(r) <= delta, (mu - y) * mu, -delta * np.sign(r) * mu)


def _huber_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    delta = p["delta"]
    mu = _mu(f)
    r = y - mu
    return np.where(np.abs(r) <= delta, (2.0 * mu - y) * mu, -delta * np.sign(r) * mu)


def _huber_gn(y: _Arr, f: _Arr, p: _P) -> _Arr:
    delta = p["delta"]
    mu = _mu(f)
    return np.where(np.abs(y - mu) <= delta, mu**2, 0.0)


def _huber_boundaries(y: _Arr, p: _P) -> tuple[_Arr, ...]:
    delta = p["delta"]
    lower = y - delta
    with np.errstate(divide="ignore"):
        return (
            np.where(lower > 0.0, np.log(np.where(lower > 0.0, lower, 1.0)), -np.inf),
            np.log(y + delta),
        )


def _ph_s(y: _Arr, f: _Arr, p: _P) -> tuple[_Arr, _Arr, _Arr]:
    mu = _mu(f)
    r = y - mu
    return mu, r, np.sqrt(1.0 + (r / p["delta"]) ** 2)


def _pseudo_huber_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    _, _, s = _ph_s(y, f, p)
    return p["delta"] ** 2 * (s - 1.0)


def _pseudo_huber_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    mu, r, s = _ph_s(y, f, p)
    return -mu * r / s


def _pseudo_huber_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    delta = p["delta"]
    mu, r, s = _ph_s(y, f, p)
    return -mu * r / s + mu**2 / s - mu**2 * r**2 / (delta**2 * s**3)


def _pseudo_huber_gn(y: _Arr, f: _Arr, p: _P) -> _Arr:
    mu, _, s = _ph_s(y, f, p)
    return mu**2 / s**3


# --- Quantile --------------------------------------------------------------------------


def _pinball_weight(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return np.where(y - _mu(f) > 0.0, p["alpha"], p["alpha"] - 1.0)


def _quantile_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return _pinball_weight(y, f, p) * (y - _mu(f))


def _quantile_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    return -_pinball_weight(y, f, p) * _mu(f)


def _quantile_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    # The pinball loss is piecewise **linear** in `μ`, so its exact second derivative is
    # its first — negative on the under-prediction side. That is not an approximation to
    # improve on: it is why FR-MODEL-43 exists, and why this template certifies
    # `convexity: violated` and needs a declared strategy and a second Approver.
    return -_pinball_weight(y, f, p) * _mu(f)


# --- Zero-inflated Poisson -------------------------------------------------------------
#
# §4.5 names the parameter `pi_link`, which presumes a second score to link. A booster
# produces one, so `pi` is a **fixed** zero-inflation probability here; a modelled `π`
# needs multi-output boosting and is Phase 2 at the earliest. Recorded as a §4.5 note
# dated 2026-08-18.


def _zip_parts(y: _Arr, f: _Arr, p: _P) -> tuple[_Arr, _Arr, _Arr, _Arr]:
    pi = p["pi"]
    mu = _mu(f)
    a = (1.0 - pi) * np.exp(-mu)
    return mu, a, pi + a, y == 0.0


def _zip_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    pi = p["pi"]
    mu, _, d, zero = _zip_parts(y, f, p)
    return np.where(zero, -np.log(d), mu - y * f - math.log(1.0 - pi))


def _zip_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    mu, a, d, zero = _zip_parts(y, f, p)
    return np.where(zero, mu * a / d, mu - y)


def _zip_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    pi = p["pi"]
    mu, a, d, zero = _zip_parts(y, f, p)
    return np.where(zero, mu * a / d - mu**2 * a * pi / d**2, mu)


def _zip_anchors(p: _P) -> tuple[float, ...]:
    return (0.0,)


# --- Focal binomial --------------------------------------------------------------------

#: `p` never reaches 0 or 1, so `log p`, `log(1-p)` and `p ** (gamma - 2)` stay finite at
#: the ends of `f_range`. `sigmoid(-20)` is 2e-9, well inside this.
_P_FLOOR: Final = 1e-12


def _focal_parts(f: _Arr, p: _P) -> tuple[_Arr, _Arr]:
    prob = np.clip(1.0 / (1.0 + np.exp(-f)), _P_FLOOR, 1.0 - _P_FLOOR)
    return prob, 1.0 - prob


def _focal_loss(y: _Arr, f: _Arr, p: _P) -> _Arr:
    g = p["gamma"]
    prob, u = _focal_parts(f, p)
    return -(y * u**g * np.log(prob) + (1.0 - y) * prob**g * np.log(u))


def _focal_dl_dp(y: _Arr, prob: _Arr, u: _Arr, g: float) -> _Arr:
    return (
        y * g * u ** (g - 1.0) * np.log(prob)
        - y * u**g / prob
        - (1.0 - y) * g * prob ** (g - 1.0) * np.log(u)
        + (1.0 - y) * prob**g / u
    )


def _focal_d2l_dp2(y: _Arr, prob: _Arr, u: _Arr, g: float) -> _Arr:
    return (
        -y * g * (g - 1.0) * u ** (g - 2.0) * np.log(prob)
        + 2.0 * y * g * u ** (g - 1.0) / prob
        + y * u**g / prob**2
        - (1.0 - y) * g * (g - 1.0) * prob ** (g - 2.0) * np.log(u)
        + 2.0 * (1.0 - y) * g * prob ** (g - 1.0) / u
        + (1.0 - y) * prob**g / u**2
    )


def _focal_grad(y: _Arr, f: _Arr, p: _P) -> _Arr:
    prob, u = _focal_parts(f, p)
    return _focal_dl_dp(y, prob, u, p["gamma"]) * prob * u


def _focal_hess(y: _Arr, f: _Arr, p: _P) -> _Arr:
    g = p["gamma"]
    prob, u = _focal_parts(f, p)
    s = prob * u
    return _focal_d2l_dp2(y, prob, u, g) * s**2 + _focal_dl_dp(y, prob, u, g) * s * (
        1.0 - 2.0 * prob
    )


_TEMPLATES: Final[dict[ObjectiveTemplate, _Template]] = {
    ObjectiveTemplate.POISSON: _Template(_poisson_loss, _poisson_grad, _poisson_hess),
    ObjectiveTemplate.GAMMA: _Template(_gamma_loss, _gamma_grad, _gamma_hess),
    ObjectiveTemplate.TWEEDIE: _Template(_tweedie_loss, _tweedie_grad, _tweedie_hess),
    ObjectiveTemplate.CAPPED_GAMMA: _Template(
        _capped_gamma_loss,
        _capped_gamma_grad,
        _capped_gamma_hess,
        y_anchors=_capped_gamma_anchors,
        branch_description="the cap, y = cap — a branch in y, not in f",
    ),
    ObjectiveTemplate.SPLICED_SEVERITY: _Template(
        _spliced_loss,
        _spliced_grad,
        _spliced_hess,
        y_anchors=_spliced_anchors,
        branch_description="the splice, y = threshold — a branch in y, not in f",
    ),
    ObjectiveTemplate.ASYMMETRIC_SQUARED: _Template(
        _asym_sq_loss,
        _asym_sq_grad,
        _asym_sq_hess,
        gauss_newton=_asym_sq_gn,
        f_boundaries=_log_y_boundary,
        branch_description="the asymmetry, exp(f) = y",
    ),
    ObjectiveTemplate.ASYMMETRIC_POISSON: _Template(
        _asym_pois_loss,
        _asym_pois_grad,
        _asym_pois_hess,
        f_boundaries=_log_y_boundary,
        branch_description="the asymmetry, exp(f) = y",
    ),
    ObjectiveTemplate.HUBER: _Template(
        _huber_loss,
        _huber_grad,
        _huber_hess,
        gauss_newton=_huber_gn,
        f_boundaries=_huber_boundaries,
        branch_description="the quadratic/linear switch, |y - exp(f)| = delta",
    ),
    ObjectiveTemplate.PSEUDO_HUBER: _Template(
        _pseudo_huber_loss,
        _pseudo_huber_grad,
        _pseudo_huber_hess,
        gauss_newton=_pseudo_huber_gn,
    ),
    ObjectiveTemplate.QUANTILE: _Template(
        _quantile_loss,
        _quantile_grad,
        _quantile_hess,
        f_boundaries=_log_y_boundary,
        branch_description="the pinball kink, exp(f) = y",
    ),
    ObjectiveTemplate.ZERO_INFLATED_POISSON: _Template(
        _zip_loss,
        _zip_grad,
        _zip_hess,
        y_anchors=_zip_anchors,
        branch_description="the zero-inflation branch, y = 0 — a branch in y, not in f",
    ),
    ObjectiveTemplate.FOCAL_BINOMIAL: _Template(
        _focal_loss, _focal_grad, _focal_hess, inverse_link="logistic"
    ),
}


# --------------------------------------------------------------------------------------
# Compilation (FR-MODEL-39, FR-MODEL-43, §5.2)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ObjectiveFns:
    """A compiled Custom Objective: `.loss`, `.grad`, `.hess` over `(y, f, w)`.

    `hess` is the **analytic** hessian, negative where the loss is non-convex. Clipping is
    a separate step (`stabilise`) because the two are read by different audiences: the
    certificate's `convexity` check must see the hessian the maths produces, and the
    booster must see one that is positive. Returning the clipped hessian from `hess` would
    certify every objective as convex, which is FR-MODEL-43's failure written as a helper.
    """

    ref: str
    template: ObjectiveTemplate
    params: Mapping[str, float]
    hessian_strategy: HessianStrategy
    hessian_min: float
    y_domain: YDomain
    _template: _Template

    @property
    def inverse_link(self) -> Literal["exp", "logistic"]:
        """`g^-1`, for the caller that has to turn a score into a mean.

        Neither backend can supply this once the objective is a callable: XGBoost's
        `predict` returns the margin, and LightGBM's raw-score path never transformed
        anything. `fit_gbm` copies it onto `GbmFitResult` so `predict_gbm` does not need
        the objective artifact to score.
        """
        return self._template.inverse_link

    def loss(self, y: _Arr, f: _Arr, w: _Arr) -> _Arr:
        return w * self._template.loss(y, f, self.params)

    def grad(self, y: _Arr, f: _Arr, w: _Arr) -> _Arr:
        return w * self._template.grad(y, f, self.params)

    def hess(self, y: _Arr, f: _Arr, w: _Arr) -> _Arr:
        return w * self._template.hess(y, f, self.params)

    def stabilise(self, y: _Arr, f: _Arr, w: _Arr) -> _Arr:
        """The hessian the booster is given — FR-MODEL-43's declared strategy, applied.

        §5.2's sketch shows `np.maximum(h, fns.hessian_min)`, which is `clip_to_min` and
        only that. The other two strategies are not a clip of the same number: `abs`
        reflects it and `gauss_newton` computes a different one, so the choice cannot live
        at the call site without each backend re-implementing it.
        """
        if self.hessian_strategy is HessianStrategy.GAUSS_NEWTON:
            gn = self._template.gauss_newton
            if gn is None:
                raise ObjectiveError(
                    "OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED",
                    f"objective {self.ref} declares hessian_strategy=gauss_newton, and "
                    f"template {self.template.value!r} is not a least-squares loss, so it "
                    "has no Gauss-Newton hessian to drop a term from. Use clip_to_min or "
                    "abs, which are defined for every template.",
                    terms=[self.ref, self.template.value],
                )
            raw = w * gn(y, f, self.params)
        elif self.hessian_strategy is HessianStrategy.ABS:
            raw = np.abs(self.hess(y, f, w))
        else:
            raw = self.hess(y, f, w)
        return np.maximum(raw, self.hessian_min)


def compile_objective(objective: CustomObjective) -> ObjectiveFns:
    """Bind a Custom Objective's parameters into vectorised `loss`/`grad`/`hess`.

    Defaults are resolved here rather than at construction: `CustomObjective.params` holds
    what the **author** chose, and a stored artifact that silently gained §4.5's defaults
    would make a later change to a default rewrite the meaning of an approved objective.
    """
    if objective.template is None:  # pragma: no cover - the contract refuses this
        raise ObjectiveError(
            "OBJECTIVE_KIND_NOT_ENABLED",
            f"objective {objective.slug}@{objective.version} is not a template objective. "
            "Phase 1 compiles templates only (FR-MODEL-75).",
            terms=[objective.slug],
        )
    template = _TEMPLATES[objective.template]
    resolved: dict[str, float] = {}
    for parameter in TEMPLATE_PARAMETERS[objective.template]:
        value = objective.params.get(parameter.name, parameter.default)
        # `CustomObjective` refuses a missing required parameter, so `value` is not None.
        resolved[parameter.name] = float(value)  # type: ignore[arg-type]
    fns = ObjectiveFns(
        ref=f"custom_objective:{objective.slug}@{objective.version}",
        template=objective.template,
        params=resolved,
        hessian_strategy=objective.hessian_strategy,
        hessian_min=objective.hessian_min,
        y_domain=objective.applicability.y_domain,
        _template=template,
    )
    if objective.hessian_strategy is HessianStrategy.GAUSS_NEWTON and (
        template.gauss_newton is None
    ):
        # Refused at compile time, not at the first boosting round: a fit that reaches
        # round 1 has already written a Job row and spent the dataset load.
        one = np.array([1.0])
        fns.stabilise(one, np.zeros(1), one)
    return fns


def template_loss(template: ObjectiveTemplate) -> _Fn:
    """The catalogue's loss for one template — the metric path's single source (FR-MODEL-103).

    Public so `metrics.py` reuses this arithmetic rather than copying it. Nothing else about
    `_TEMPLATES` is exported: the gradient and hessian are the fitting path's business, and a
    metric has no use for either.
    """
    return _TEMPLATES[template].loss


def _finite_or_abort(
    fns: ObjectiveFns, g: _Arr, h: _Arr, y: _Arr, f: _Arr, round_index: int
) -> None:
    """FR-MODEL-48: abort naming the round and the offending input range."""
    bad = ~(np.isfinite(g) & np.isfinite(h))
    if not bad.any():
        return
    y_bad, f_bad = y[bad], f[bad]
    raise NonFiniteDerivativeError(
        f"objective {fns.ref} produced a non-finite gradient or hessian on "
        f"{int(bad.sum())} of {bad.size} rows at boosting round {round_index}. The "
        f"offending inputs span y ∈ [{y_bad.min():.6g}, {y_bad.max():.6g}], "
        f"f ∈ [{f_bad.min():.6g}, {f_bad.max():.6g}].",
        round_index=round_index,
        terms=[fns.ref],
    )


def make_xgb_objective(fns: ObjectiveFns) -> Callable[[_Arr, Any], tuple[_Arr, _Arr]]:
    """The `obj=` callable for `xgboost.train` (§5.2's sketch, FR-MODEL-48).

    `base_margin` is not a parameter, unlike the sketch: XGBoost has already added it into
    `preds` by the time the objective is called, so accepting one would invite a caller to
    add it a second time — which under a log link doubles the exposure and looks like a
    plausible fit.
    """
    counter = {"round": 0}

    def objective(preds: _Arr, dtrain: Any) -> tuple[_Arr, _Arr]:
        y = np.asarray(dtrain.get_label(), dtype=np.float64)
        weight = np.asarray(dtrain.get_weight(), dtype=np.float64)
        w = weight if weight.size == y.size else np.ones_like(y)
        f = np.asarray(preds, dtype=np.float64)
        g, h = fns.grad(y, f, w), fns.stabilise(y, f, w)
        _finite_or_abort(fns, g, h, y, f, counter["round"])
        counter["round"] += 1
        return g, h

    return objective


def make_lgb_objective(fns: ObjectiveFns) -> Callable[[_Arr, Any], tuple[_Arr, _Arr]]:
    """The callable LightGBM's `params["objective"]` accepts.

    **`(preds, dataset)`, not §5.2's three-argument `(y_true, y_pred, weight)`** — that
    form is the scikit-learn wrapper's, and `lgb.train` calls
    `fobj(self.__inner_predict(data_idx=0), self.train_set)` (lightgbm 4.7.0,
    `basic.py:4276`). Passing the sklearn shape here raises `TypeError: missing 1 required
    positional argument` on the first boosting round, which is how this was found. The
    weights are read off the dataset instead, so nothing is dropped; §5.2 carries the
    dated correction.

    `preds` is the raw score with `init_score` already added, exactly as XGBoost's `preds`
    carries `base_margin` — so neither adapter adds the offset, and FR-MODEL-72's
    asymmetry is a *scoring*-time one only.
    """
    counter = {"round": 0}

    def objective(preds: _Arr, dataset: Any) -> tuple[_Arr, _Arr]:
        y = np.asarray(dataset.get_label(), dtype=np.float64)
        f = np.asarray(preds, dtype=np.float64)
        weight = dataset.get_weight()
        w = np.ones_like(y) if weight is None else np.asarray(weight, dtype=np.float64)
        g, h = fns.grad(y, f, w), fns.stabilise(y, f, w)
        _finite_or_abort(fns, g, h, y, f, counter["round"])
        counter["round"] += 1
        return g, h

    return objective


# --------------------------------------------------------------------------------------
# Certification (§4.7, FR-MODEL-42/43/68/69/70/76)
# --------------------------------------------------------------------------------------

_EPS: Final = float(np.finfo(np.float64).eps)

#: Which synthetic dataset the smoke fit builds, when an objective applies to several.
#: Severity first because it is the response with no point mass at zero, so a recovered
#: relativity means the same thing for every template — a median-seeking `quantile` on a
#: mostly-zero count response would report a relativity of `0/0` and call the objective
#: broken for a property of the data.
_SMOKE_ORDER: Final = (
    ResponseKind.CLAIM_SEVERITY,
    ResponseKind.BURNING_COST,
    ResponseKind.CLAIM_COUNT,
    ResponseKind.CONVERSION,
    ResponseKind.RETENTION,
)
_SMOKE_ROWS: Final = 20_000
_SMOKE_ROUNDS: Final = 80
_TRUE_RELATIVITY: Final = 1.5


def _grid(objective: CustomObjective, sampling: SamplingSpec, fns: ObjectiveFns) -> tuple[
    _Arr, _Arr, _Arr, tuple[float, float]
]:
    """The `(y, f, w)` points every check is evaluated on.

    Three departures from a plain uniform draw, each of which a uniform draw gets wrong:

    * **`y` is clipped into the objective's own `y_domain`.** Sampling `y = 0` for a Gamma
      template would report `-inf` under `finiteness` for a point the objective never sees.
    * **A third of `y` is drawn log-uniformly.** A uniform draw over `[0, 1e7]` puts 999 in
      1000 points above 1e4, and the small-claim end is where a severity loss is stiffest.
    * **Branch anchors are sampled at.** `zero_inflated_poisson`'s whole behaviour lives at
      `y = 0`, which a continuous draw hits with probability zero.
    """
    rng = np.random.default_rng(sampling.seed)
    n = sampling.n_points
    lo, hi = sampling.y_range
    domain = fns.y_domain
    if domain.lower is not None:
        lo = max(lo, domain.lower)
    if domain.upper is not None:
        hi = min(hi, domain.upper)
    span = max(hi - lo, 0.0)
    if domain.min_exclusive is not None and lo <= domain.min_exclusive:
        # A relative nudge, not an absolute one: `1e-9` is a rounding error on a claim in
        # pence and the entire domain of a conversion probability.
        lo = domain.min_exclusive + max(span * 1e-9, _EPS)
    if domain.max_exclusive is not None and hi >= domain.max_exclusive:
        hi = domain.max_exclusive - max(span * 1e-9, _EPS)

    y = rng.uniform(lo, hi, n)
    third = n // 3
    if third and hi > 0.0:
        floor = max(lo, hi * 1e-9)
        y[:third] = np.exp(rng.uniform(math.log(floor), math.log(hi), third))
    anchors = _TEMPLATES[objective.template].y_anchors if objective.template else None
    if anchors is not None:
        values = np.array([v for v in anchors(fns.params) if lo <= v <= hi], dtype=float)
        if values.size:
            take = max(n // 10, 1)
            y[-take:] = rng.choice(values, take)
    # The declared endpoints are checked, not merely spanned — `finiteness` claims them.
    y[0], y[1] = lo, hi

    f_lo, f_hi = sampling.f_range
    f = rng.uniform(f_lo, f_hi, n)
    f[0], f[1] = f_lo, f_hi
    w_lo, w_hi = sampling.w_range
    w = np.exp(rng.uniform(math.log(max(w_lo, _EPS)), math.log(max(w_hi, _EPS)), n))
    w[0], w[1] = w_lo, w_hi
    return y, f, w, (lo, hi)


def _central(fn: Callable[[_Arr], _Arr], f: _Arr, h: float) -> _Arr:
    return (fn(f + h) - fn(f - h)) / (2.0 * h)


def _richardson(fn: Callable[[_Arr], _Arr], f: _Arr, h: float) -> _Arr:
    """Central differences at `h` and `h/2`, extrapolated — `O(h**2)` error becomes `O(h**4)`.

    FR-MODEL-70 requires the method to be recorded because it is what makes the tolerance
    meaningful: at `h = 1e-6` a plain central difference cannot do better than ~4e-4 on a
    steeply-curved loss, so a certificate quoting a tight tolerance without naming the
    method is quoting a number nothing could have achieved.
    """
    return (4.0 * _central(fn, f, h / 2.0) - _central(fn, f, h)) / 3.0


def _agreement(
    analytic: _Arr, numeric: _Arr, magnitude: _Arr, h: float, mask: _Mask
) -> tuple[float, int]:
    """Max relative error, floored by the precision a finite difference can deliver.

    A pure relative error is meaningless where the derivative passes through zero: the
    numeric estimate there is cancellation noise of size `eps * |value| / h`, and dividing
    a noise-sized difference by a noise-sized derivative reports `O(1)` disagreement for an
    exactly correct formula. `magnitude` is the quantity being differenced, so the noise is
    the one *at that point* — which is what makes the tolerance step-aware (FR-MODEL-70)
    rather than a constant chosen to make the check pass.

    The noise enters **twice**, and it has to: as a floor under the denominator, and
    subtracted from the difference. Flooring alone is not enough wherever the derivative is
    orders of magnitude smaller than the quantity differenced — a Gamma hessian at
    `y=1.8, f=13.9` is `5.5e-07` against a gradient of `0.33`, so the cancellation noise in
    the numeric estimate is `6e-12` absolute while the hessian it is compared against is
    `5.5e-07`. A difference of `9e-13` — well inside what the method can resolve — then
    divided out as a relative error of `1.6e-06` and warned, which is an exactly correct
    derivative reported as a suspect one. (Found 2026-08-18, when the grid floor rose to
    1 000 points and three of the twelve templates warned.)
    """
    if not mask.any():
        return 0.0, 0
    a, n = analytic[mask], numeric[mask]
    noise = 8.0 * _EPS * np.abs(magnitude[mask]) / h
    denom = np.maximum(np.maximum(np.abs(a), np.abs(n)), noise)
    with np.errstate(invalid="ignore", divide="ignore"):
        error = np.maximum(np.abs(a - n) - noise, 0.0) / denom
    error = error[np.isfinite(error)]
    return (float(error.max()) if error.size else 0.0), int(mask.sum())


def _status_for(error: float) -> CheckStatus:
    if error <= _TOLERANCE_PASS:
        return CheckStatus.PASS
    if error <= _TOLERANCE_WARN:
        return CheckStatus.WARN
    return CheckStatus.FAILED


def _branch_mask(fns: ObjectiveFns, y: _Arr, f: _Arr) -> tuple[_Mask, int]:
    """FR-MODEL-68: drop the points a central difference would straddle a kink at."""
    boundaries = fns._template.f_boundaries
    if boundaries is None:
        return np.ones_like(f, dtype=bool), 0
    keep = np.ones_like(f, dtype=bool)
    # Richardson evaluates as far as `h` either side, so the exclusion radius is `h` —
    # widened a little because the boundary itself is computed in floating point.
    radius = _STEP * 1.5
    for edge in boundaries(y, fns.params):
        keep &= ~(np.abs(f - edge) <= radius)
    return keep, int((~keep).sum())


def _derivative_checks(
    fns: ObjectiveFns, y: _Arr, f: _Arr, w: _Arr
) -> tuple[CertificateCheck, CertificateCheck]:
    """FR-MODEL-76's `analytic_vs_numeric` pair — the check the 24 derivatives answer to."""
    keep, excluded = _branch_mask(fns, y, f)
    loss, grad = fns.loss(y, f, w), fns.grad(y, f, w)
    finite = np.isfinite(loss) & np.isfinite(grad)
    mask = keep & finite

    numeric_g = _richardson(lambda fs: fns.loss(y, fs, w), f, _STEP)
    g_error, compared = _agreement(grad, numeric_g, loss, _STEP, mask)
    numeric_h = _richardson(lambda fs: fns.grad(y, fs, w), f, _STEP)
    h_error, _ = _agreement(fns.hess(y, f, w), numeric_h, grad, _STEP, mask)

    # FR-MODEL-68 asks for the excluded count, and a count reported only when it is
    # non-zero is a count the reader cannot distinguish from an unreported one.
    branch = fns._template.branch_description
    where = (
        f", {excluded:,} of {y.size:,} excluded within h of {branch}"
        if branch is not None
        else ", no branch boundary to exclude near"
    )
    return (
        CertificateCheck(
            name="analytic_vs_numeric_gradient",
            status=_status_for(g_error),
            detail=(
                f"max relative error {g_error:.3g} over {compared:,} sampled (y,f,w) "
                f"points{where}; h={_STEP:g}, Richardson-extrapolated, tolerance floored "
                f"at the finite-difference noise of each point (FR-MODEL-68/70)"
            ),
        ),
        CertificateCheck(
            name="analytic_vs_numeric_hessian",
            status=_status_for(h_error),
            detail=(
                f"max relative error {h_error:.3g} against the numeric derivative of the "
                f"analytic gradient over the same {compared:,} points; h={_STEP:g}, "
                f"Richardson-extrapolated (FR-MODEL-70)"
            ),
        ),
    )


def _finiteness_check(
    fns: ObjectiveFns, y: _Arr, f: _Arr, w: _Arr, y_range: tuple[float, float],
    sampling: SamplingSpec,
) -> CertificateCheck:
    bad = ~(
        np.isfinite(fns.loss(y, f, w))
        & np.isfinite(fns.grad(y, f, w))
        & np.isfinite(fns.hess(y, f, w))
    )
    span = (
        f"y ∈ [{y_range[0]:.6g}, {y_range[1]:.6g}], "
        f"f ∈ [{sampling.f_range[0]:.6g}, {sampling.f_range[1]:.6g}], "
        f"w ∈ [{sampling.w_range[0]:.6g}, {sampling.w_range[1]:.6g}]"
    )
    if not bad.any():
        return CertificateCheck(
            name="finiteness", status=CheckStatus.PASS, detail=f"no NaN/inf for {span}"
        )
    return CertificateCheck(
        name="finiteness",
        status=CheckStatus.FAILED,
        detail=(
            f"{int(bad.sum()):,} of {bad.size:,} sampled points produced NaN or inf, at "
            f"y ∈ [{y[bad].min():.6g}, {y[bad].max():.6g}], "
            f"f ∈ [{f[bad].min():.6g}, {f[bad].max():.6g}], within {span}"
        ),
    )


def _convexity_check(fns: ObjectiveFns, y: _Arr, f: _Arr, w: _Arr) -> CertificateCheck:
    """FR-MODEL-43: non-convex is a finding with a declared mitigation, never a refusal."""
    hess = fns.hess(y, f, w)
    negative = hess[np.isfinite(hess)] < 0.0
    share = float(negative.mean()) if negative.size else 0.0
    if share == 0.0:
        return CertificateCheck(
            name="convexity",
            status=CheckStatus.PASS,
            detail=f"hessian ≥ 0 at every one of {hess.size:,} sampled points",
        )
    return CertificateCheck(
        name="convexity",
        status=CheckStatus.VIOLATED,
        detail=(
            f"hessian < 0 at {share:.1%} of this sampling grid. The share is strongly "
            f"dependent on y_range/f_range and is only meaningful alongside the sampling "
            f"block. Mitigated by hessian_strategy={fns.hessian_strategy.value}, "
            f"hessian_min={fns.hessian_min:g}; FR-MODEL-43 requires an additional Approver"
        ),
    )


def _branch_check(fns: ObjectiveFns, y: _Arr, f: _Arr, w: _Arr) -> CertificateCheck:
    """FR-MODEL-69: where the derivatives are discontinuous, and over how much of the grid.

    A branch in `y` is reported as well as a branch in `f`, and named as such. Only the
    latter invalidates a central difference, but an approver reading "smooth" about
    `spliced_severity` would be reading the opposite of what the loss does at the splice.
    """
    description = fns._template.branch_description
    if description is None:
        return CertificateCheck(
            name="branch_discontinuity",
            status=CheckStatus.PASS,
            detail="the loss is a single smooth expression; gradient and hessian are "
            "continuous over the whole sampled domain",
        )
    _, excluded = _branch_mask(fns, y, f)
    if fns._template.f_boundaries is not None:
        return CertificateCheck(
            name="branch_discontinuity",
            status=CheckStatus.WARN,
            detail=(
                f"gradient and hessian are discontinuous at {description}; "
                f"{excluded:,} of {f.size:,} sampled points fell within h of it and were "
                f"excluded from the derivative comparison (FR-MODEL-68/69). A "
                f"discontinuous hessian affects boosting stability"
            ),
        )
    anchors = fns._template.y_anchors
    edge = anchors(fns.params)[0] if anchors is not None else 0.0
    above = float((y > edge).mean())
    return CertificateCheck(
        name="branch_discontinuity",
        status=CheckStatus.WARN,
        detail=(
            f"the loss changes form at {description}; {above:.1%} of the sampled y lie "
            f"above it. A central difference in f never straddles this branch, so no "
            f"point was excluded (FR-MODEL-68), but the two sides have different "
            f"curvature and an approver must see that (FR-MODEL-69)"
        ),
    )


def _minimisers(
    fns: ObjectiveFns, y: _Arr, f_range: tuple[float, float]
) -> tuple[_Arr, _Mask]:
    """For each `y`, the `f` where the gradient crosses zero upwards — or NaN if none.

    A scan then a bisection, rather than a solver: the gradient of a piecewise loss is not
    continuous, and a Newton step across a kink lands anywhere. The scan finds the bracket
    the crossing is actually in, and 64 bisections close it to machine precision.
    """
    ones = np.ones((1, 1))
    grid = np.linspace(f_range[0], f_range[1], 2001)[None, :]
    column = y[:, None]
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        gradient = fns.grad(column, grid + 0.0 * column, ones)
    crossing = (gradient[:, :-1] < 0.0) & (gradient[:, 1:] >= 0.0)
    has = crossing.any(axis=1)
    index = np.argmax(crossing, axis=1)
    lo = np.where(has, grid[0, :-1][index], np.nan)
    hi = np.where(has, grid[0, 1:][index], np.nan)
    for _ in range(64):
        mid = 0.5 * (lo + hi)
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            negative = fns.grad(y, mid, np.ones_like(y)) < 0.0
        lo = np.where(negative, mid, lo)
        hi = np.where(negative, hi, mid)
    return np.where(has, 0.5 * (lo + hi), np.nan), has


def _shape_checks(
    fns: ObjectiveFns, y: _Arr, sampling: SamplingSpec
) -> tuple[CertificateCheck, CertificateCheck]:
    """`minimum_at_truth` and `monotone_loss` — the two checks that read the loss's shape."""
    sample = y[np.linspace(0, y.size - 1, min(32, y.size)).astype(int)]
    minimiser, found = _minimisers(fns, sample, sampling.f_range)
    ones = np.ones_like(sample)

    if not found.any():
        detail = (
            "the loss is monotone in f for every sampled y over "
            f"f ∈ [{sampling.f_range[0]:g}, {sampling.f_range[1]:g}] — no interior "
            "minimum to locate. A loss a booster can only push in one direction is "
            "legitimate for a tail component but is worth an approver's attention"
        )
        return (
            CertificateCheck(name="minimum_at_truth", status=CheckStatus.WARN, detail=detail),
            CertificateCheck(
                name="monotone_loss",
                status=CheckStatus.WARN,
                detail="not evaluated: the loss has no interior minimum to move away from",
            ),
        )

    at = minimiser[found]
    truth = np.log(np.maximum(sample[found], _EPS))
    deviation = float(np.nanmax(np.abs(at - truth)))
    base = fns.loss(sample[found], at, ones[found])
    steps = (0.05, 0.2, 0.5, 1.0, 2.0)
    rises = np.array(
        [
            [fns.loss(sample[found], at + sign * step, ones[found]) for step in steps]
            for sign in (-1.0, 1.0)
        ]
    )
    # A minimum, not merely a stationary point: every step away raises the loss.
    above = bool(np.all(rises >= base - 1e-9 * np.maximum(np.abs(base), 1.0)))
    increasing = bool(np.all(np.diff(rises, axis=1) >= -1e-9 * np.maximum(np.abs(base), 1.0)))
    missing = int((~found).sum())
    unresolved = (
        f"; {missing} of {sample.size} sampled y had no interior minimum" if missing else ""
    )

    verdict = (
        "every stationary point of the analytic gradient is a genuine minimum of the loss"
        if above
        else "a step away from a stationary point of the analytic gradient LOWERS the "
        "loss, so the loss is not minimised where its gradient vanishes - either the two "
        "are not derivatives of one another, or the loss is discontinuous"
    )

    return (
        CertificateCheck(
            name="minimum_at_truth",
            status=CheckStatus.PASS if above else CheckStatus.WARN,
            detail=(
                f"{verdict}, over {int(found.sum())} of {sample.size} sampled y; max "
                f"|f* - log y| = {deviation:.3g}{unresolved}. A non-zero deviation is "
                f"expected wherever the template deliberately targets something other than "
                f"the mean (quantile, the asymmetric pair, capped_gamma above its cap); a "
                f"y with no interior minimum is a property of the sampled f range, not of "
                f"the objective"
            ),
        ),
        CertificateCheck(
            name="monotone_loss",
            status=CheckStatus.PASS if increasing else CheckStatus.WARN,
            detail=(
                "loss increases with |f - f*| in both directions at steps of "
                + ", ".join(f"{s:g}" for s in steps)
                if increasing
                else "loss does not increase monotonically away from its minimum - the "
                "loss surface has more than one turning point over the sampled f range"
            ),
        ),
    )


def _scale_check(fns: ObjectiveFns, y: _Arr, f: _Arr, w: _Arr) -> CertificateCheck:
    magnitude = np.abs(fns.grad(y, f, w))
    magnitude = magnitude[np.isfinite(magnitude) & (magnitude > 0.0)]
    if magnitude.size == 0:
        return CertificateCheck(
            name="scale_behaviour",
            status=CheckStatus.WARN,
            detail="the gradient is identically zero over the sampled domain",
        )
    orders = float(np.log10(magnitude.max() / magnitude.min()))
    detail = (
        f"gradient magnitude spans {orders:.1f} orders over the sampled domain "
        f"({magnitude.min():.3g} to {magnitude.max():.3g})"
    )
    if orders <= 6.0:
        return CertificateCheck(name="scale_behaviour", status=CheckStatus.PASS, detail=detail)
    return CertificateCheck(
        name="scale_behaviour",
        status=CheckStatus.WARN,
        detail=(
            f"{detail} — a range this wide makes a single learning rate a compromise "
            f"across the book; consider a log-scale variant or a narrower y_domain"
        ),
    )


def _smoke_data(
    response: ResponseKind, rng: np.random.Generator
) -> tuple[_Arr, _Arr, _Arr, str]:
    """One binary factor with a known relativity, under the response's own distribution.

    The relativity is multiplicative on the raw score for every response here — a rate
    ratio for counts and burning cost, a severity ratio, an odds ratio for conversion — so
    one number is recoverable the same way whatever the objective, and the check does not
    need a per-template notion of what "recovered" means.
    """
    x = rng.integers(0, 2, _SMOKE_ROWS).astype(float)
    relativity = _TRUE_RELATIVITY**x
    exposure = rng.uniform(0.2, 1.0, _SMOKE_ROWS)
    zeros = np.zeros(_SMOKE_ROWS)
    if response is ResponseKind.CLAIM_SEVERITY:
        y = rng.gamma(2.0, 1500.0 * relativity / 2.0)
        return x, np.maximum(y, 1.0), zeros, "gamma severity, mean 1500 x relativity"
    if response is ResponseKind.BURNING_COST:
        counts = rng.poisson(0.15 * exposure * relativity)
        y = counts * rng.gamma(2.0, 1500.0, _SMOKE_ROWS)
        return x, y, np.log(exposure), "compound Poisson-gamma, log-exposure offset"
    if response is ResponseKind.CLAIM_COUNT:
        y = rng.poisson(0.15 * exposure * relativity).astype(float)
        return x, y, np.log(exposure), "Poisson counts, log-exposure offset"
    base = math.log(0.08 / 0.92)
    probability = 1.0 / (1.0 + np.exp(-(base + math.log(_TRUE_RELATIVITY) * x)))
    y = rng.binomial(1, probability).astype(float)
    return x, y, zeros, "Bernoulli outcomes, 8% base rate"


def _smoke_fit_check(
    fns: ObjectiveFns, objective: CustomObjective, seed: int, versions: dict[str, str]
) -> CertificateCheck:
    """Does the objective actually train a booster, and does the booster learn the truth?

    The one check that runs the objective through XGBoost rather than over a grid. It is
    where a compiled objective that is mathematically perfect and numerically unusable
    shows up — a `quantile` left on `clip_to_min` diverges here and nowhere else.
    """
    responses = objective.applicability.responses
    response = next((r for r in _SMOKE_ORDER if r in responses), None)
    if response is None:  # pragma: no cover - every template names an applicable response
        return CertificateCheck(
            name="smoke_fit",
            status=CheckStatus.WARN,
            detail="no synthetic generator for this objective's declared responses",
        )
    try:
        import xgboost as xgb
    except ImportError:  # pragma: no cover - xgboost is a hard dependency of this package
        return CertificateCheck(
            name="smoke_fit", status=CheckStatus.WARN, detail="xgboost is not installed"
        )
    versions["xgboost"] = str(xgb.__version__)

    rng = np.random.default_rng(seed)
    x, y, margin, description = _smoke_data(response, rng)
    started = time.perf_counter()
    try:
        booster = xgb.train(
            {
                "max_depth": 2,
                "eta": 0.2,
                "tree_method": "hist",
                "seed": seed,
                "base_score": 0.0,
                # Bounds the leaf step in raw-score space. Not a thumb on the scale: a
                # clipped hessian makes `-sum(g)/(sum(h)+lambda)` arbitrarily large, and
                # without this the check would measure XGBoost's divergence behaviour
                # rather than the objective's.
                "max_delta_step": 0.7,
            },
            xgb.DMatrix(x.reshape(-1, 1), label=y, base_margin=margin),
            num_boost_round=_SMOKE_ROUNDS,
            obj=make_xgb_objective(fns),
        )
        raw = booster.predict(
            xgb.DMatrix(np.array([[0.0], [1.0]])), output_margin=True
        )
        recovered = float(np.exp(raw[1] - raw[0]))
    except Exception as failure:
        return CertificateCheck(
            name="smoke_fit",
            status=CheckStatus.FAILED,
            detail=(
                f"fitting {_SMOKE_ROWS:,} rows of {description} for {_SMOKE_ROUNDS} rounds "
                f"raised {type(failure).__name__}: {failure}"
            ),
        )
    elapsed = time.perf_counter() - started
    if not math.isfinite(recovered):
        return CertificateCheck(
            name="smoke_fit",
            status=CheckStatus.FAILED,
            detail=(
                f"the fit produced a non-finite raw score on {description}; the objective "
                f"cannot be trained with hessian_strategy={fns.hessian_strategy.value}"
            ),
        )
    error = abs(recovered / _TRUE_RELATIVITY - 1.0)
    detail = (
        f"recovered a relativity of {recovered:.4g} against a true {_TRUE_RELATIVITY} "
        f"({error:.1%}) on {description}, n={_SMOKE_ROWS:,}; {_SMOKE_ROUNDS} rounds, "
        f"{elapsed:.1f}s"
    )
    if error <= 0.20:
        return CertificateCheck(name="smoke_fit", status=CheckStatus.PASS, detail=detail)
    return CertificateCheck(
        name="smoke_fit",
        status=CheckStatus.WARN,
        detail=(
            f"{detail} - a template that deliberately targets something other than the "
            f"mean will not recover it, so this is a finding for an approver to read "
            f"against the objective's intent, not a defect on its own"
        ),
    )


def certify_objective(
    objective: CustomObjective,
    *,
    sampling: SamplingSpec,
    progress: ProgressCallback | None = None,
) -> CertificateResult:
    """Run §4.7's checks over a Custom Objective and return the certificate's contents.

    Two departures from §5.2's declared signature, both recorded there with their date:

    * **Returns `CertificateResult`, not `ObjectiveCertificate`.** The certificate carries
      an id, a job and a `certified_at`, none of which `pricing-core` may allocate
      (ADR-0001). The same split as `compute_diagnostics`/`DiagnosticsResult`.
    * **No `seed` parameter.** `SamplingSpec` already carries the seed that makes the grid
      reproducible, and a second one would let a caller record a certificate whose stated
      sampling does not reproduce it.
    """
    report = progress or NullProgress()
    fns = compile_objective(objective)
    report.check_cancelled()
    report.update(0.05, "sampling the (y, f, w) grid")
    y, f, w, y_range = _grid(objective, sampling, fns)
    versions: dict[str, str] = {"numpy": str(np.__version__)}

    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        report.update(0.15, "comparing analytic and numeric derivatives")
        gradient_check, hessian_check = _derivative_checks(fns, y, f, w)
        report.check_cancelled()
        report.update(0.35, "checking finiteness, convexity and branches")
        checks = [
            gradient_check,
            hessian_check,
            _finiteness_check(fns, y, f, w, y_range, sampling),
            _convexity_check(fns, y, f, w),
            _branch_check(fns, y, f, w),
        ]
        report.update(0.5, "locating the loss minimum")
        checks.extend(_shape_checks(fns, y, sampling))
        checks.append(_scale_check(fns, y, f, w))

    report.check_cancelled()
    report.update(0.7, "smoke fit")
    checks.append(_smoke_fit_check(fns, objective, sampling.seed, versions))
    report.update(1.0, "certified")

    ordered = tuple(checks)
    return CertificateResult(
        checks=ordered,
        sampling=sampling,
        overall=CertificateResult.outcome_of(ordered),
        library_versions=versions,
    )
