"""The Custom Objective catalogue and its certification (`02` §4.5/§4.7, FR-142, FR-143, FR-144,
FR-145, FR-146, FR-152, FR-153, FR-154, FR-163, FR-164, FR-165).

**The parametrised certification test is the test for the maths.** This module ships 12
templates, each with an analytic gradient and an analytic hessian written out by hand — 24
derivatives, any one of which could carry a sign error that a fit would absorb into a
plausible-looking book. Certification compares every one of them against a
Richardson-extrapolated numeric derivative of that template's own loss (FR-149), so
`test_every_template_certifies` proves all 24 at once, and a mistake in any of them fails
with the template's name on it.

That is also why the assertions here are on **check statuses**, not on the outcome alone:
`certified_with_findings` is the ordinary result for a pricing loss (§4.7's own worked
example is one), and asserting only `overall != failed` would pass with both derivative
checks warning.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
import pytest
import sympy

from model_schema import (
    TEMPLATE_APPLICABILITY,
    Applicability,
    CertificateOutcome,
    CheckStatus,
    CustomObjective,
    DerivedBlock,
    HessianStrategy,
    ObjectiveBackend,
    ObjectiveKind,
    ObjectiveTemplate,
    ResponseKind,
    SamplingSpec,
    YDomain,
)
from pricing_core.modelling import (
    ObjectiveFns,
    certify_objective,
    compile_objective,
    make_lgb_objective,
    make_xgb_objective,
)
from pricing_core.modelling.errors import (
    NonFiniteDerivativeError,
    ObjectiveError,
    RoundBudgetExceededError,
)
from pricing_core.modelling.expression_objective import (
    Derived,
    certify_expression_objective,
    compile_expression_objective,
    derive,
)
from pricing_core.modelling.objectives import (
    _TEMPLATES,
    _TOLERANCE_PASS,
    _TOLERANCE_WARN,
    DEFAULT_ROUND_BUDGET_S,
    _finite_or_abort,
)
from pricing_core.safe_error import CodedError, safe_error_detail

T = ObjectiveTemplate

#: Money parameters are integer minor units (`CLAUDE.md` §7), so a `cap` of 500 000 is
#: £5 000 — a plausible large-loss cap on a severity book whose y runs to £10 000.
_PARAMS: dict[ObjectiveTemplate, dict[str, float | int]] = {
    T.POISSON: {},
    T.GAMMA: {},
    T.TWEEDIE: {"p": 1.5},
    T.CAPPED_GAMMA: {"cap": 500_000},
    T.SPLICED_SEVERITY: {"threshold": 300_000, "tail_shape": 1.5},
    T.ASYMMETRIC_SQUARED: {"w_under": 2.0, "w_over": 1.0},
    T.ASYMMETRIC_POISSON: {"w_under": 2.0, "w_over": 1.0},
    T.HUBER: {"delta": 100_000},
    T.PSEUDO_HUBER: {"delta": 100_000},
    T.QUANTILE: {"alpha": 0.7},
    T.ZERO_INFLATED_POISSON: {"pi": 0.3},
    T.FOCAL_BINOMIAL: {"gamma": 2.0},
}

#: A grid per template, because one grid cannot serve all of them: a count response over
#: `y ∈ [1, 1e6]` is not a count, and a severity in minor units over `f ∈ [-2, 2]` predicts
#: 7 pence. The sampling block is part of the certificate for exactly this reason (§4.7).
_COUNT_Y = (0.0, 5.0)
_COUNT_F = (-2.0, 2.0)
_MONEY_Y = (1.0, 1_000_000.0)
_MONEY_F = (8.0, 14.0)
_GRIDS: dict[ObjectiveTemplate, tuple[tuple[float, float], tuple[float, float]]] = {
    T.POISSON: (_COUNT_Y, _COUNT_F),
    T.ASYMMETRIC_POISSON: (_COUNT_Y, _COUNT_F),
    T.ZERO_INFLATED_POISSON: (_COUNT_Y, _COUNT_F),
    T.TWEEDIE: (_MONEY_Y, _COUNT_F),
    T.FOCAL_BINOMIAL: ((0.0, 1.0), (-4.0, 4.0)),
}

#: `quantile` and `asymmetric_squared` have a hessian that is negative over much of the
#: domain (FR-152), so they are certified under the strategy an author would actually
#: deploy them with. `clip_to_min` is the default and covers the rest.
_STRATEGIES: dict[ObjectiveTemplate, HessianStrategy] = {
    T.QUANTILE: HessianStrategy.ABS,
    T.ASYMMETRIC_SQUARED: HessianStrategy.GAUSS_NEWTON,
}

_SEED = 20260818


def _objective(
    template: ObjectiveTemplate,
    *,
    strategy: HessianStrategy | None = None,
    params: dict[str, float | int] | None = None,
    applicability: Applicability | None = None,
) -> CustomObjective:
    return CustomObjective(
        id=uuid4(),
        slug=f"test-{template.value.replace('_', '-')}",
        version=1,
        template=template,
        params=dict(_PARAMS[template]) if params is None else params,
        applicability=applicability or TEMPLATE_APPLICABILITY[template],
        hessian_strategy=strategy or _STRATEGIES.get(template, HessianStrategy.CLIP_TO_MIN),
    )


def _sampling(template: ObjectiveTemplate, *, n_points: int = 1_000) -> SamplingSpec:
    y_range, f_range = _GRIDS.get(template, (_MONEY_Y, _MONEY_F))
    return SamplingSpec(
        n_points=n_points, seed=_SEED, y_range=y_range, f_range=f_range, w_range=(0.1, 3.0)
    )


def _status(result: Any, name: str) -> CheckStatus:
    return next(check.status for check in result.checks if check.name == name)


def _detail(result: Any, name: str) -> str:
    return next(check.detail for check in result.checks if check.name == name)


# --- the catalogue ---------------------------------------------------------------------


@pytest.mark.req("FR-143")
@pytest.mark.parametrize("template", list(T), ids=lambda t: t.value)
def test_every_template_certifies(template: ObjectiveTemplate) -> None:
    """All 12 templates, and both of their analytic derivatives, against numerics.

    The derivative checks are asserted `pass` rather than merely not-`failed`: a warning
    there means the analytic form and the loss disagree by more than finite-difference
    noise, which is a wrong derivative reported politely.
    """
    result = certify_objective(_objective(template), sampling=_sampling(template))

    assert result.overall is not CertificateOutcome.FAILED
    assert _status(result, "analytic_vs_numeric_gradient") is CheckStatus.PASS
    assert _status(result, "analytic_vs_numeric_hessian") is CheckStatus.PASS
    assert _status(result, "finiteness") is CheckStatus.PASS
    assert _status(result, "smoke_fit") is not CheckStatus.FAILED


@pytest.mark.req("FR-146")
@pytest.mark.parametrize("template", list(T), ids=lambda t: t.value)
def test_every_certificate_carries_every_check(template: ObjectiveTemplate) -> None:
    """§4.7's nine checks, on every objective — a missing check is not a passing one."""
    result = certify_objective(_objective(template), sampling=_sampling(template))

    assert [check.name for check in result.checks] == [
        "analytic_vs_numeric_gradient",
        "analytic_vs_numeric_hessian",
        "finiteness",
        "convexity",
        "branch_discontinuity",
        "minimum_at_truth",
        "monotone_loss",
        "scale_behaviour",
        "smoke_fit",
    ]
    assert result.sampling == _sampling(template)
    assert set(result.library_versions) >= {"numpy", "xgboost"}


@pytest.mark.req("FR-151")
def test_certification_is_reproducible() -> None:
    """Same objective, same sampling, same verdicts — a certificate is evidence.

    Nothing in certification reads a clock or an unseeded generator, so a re-run on the
    library versions the certificate records reproduces it. A certificate that cannot be
    re-run is an assertion.
    """
    objective = _objective(T.TWEEDIE)
    first = certify_objective(objective, sampling=_sampling(T.TWEEDIE))
    second = certify_objective(objective, sampling=_sampling(T.TWEEDIE))

    assert first.overall is second.overall
    assert [(c.name, c.status) for c in first.checks] == [
        (c.name, c.status) for c in second.checks
    ]
    # Every detail but the smoke fit's, which records its own elapsed time. §4.7's worked
    # example records one too: how long a certification took is what an author needs to
    # size the next one, and it is the single figure in a certificate that is not a
    # property of the objective.
    assert [(c.name, c.detail) for c in first.checks if c.name != "smoke_fit"] == [
        (c.name, c.detail) for c in second.checks if c.name != "smoke_fit"
    ]
    recovered = [
        check.detail.split(";")[0]
        for result in (first, second)
        for check in result.checks
        if check.name == "smoke_fit"
    ]
    assert recovered[0] == recovered[1]


# --- what certification is supposed to find --------------------------------------------


@pytest.mark.req("FR-152")
def test_a_non_convex_objective_is_flagged_and_not_refused() -> None:
    """`quantile`'s hessian is its gradient — negative wherever the gradient is.

    FR-152 in one test: the finding reaches the approver (`violated`, with the share
    and the mitigation named) and does not block (`certified_with_findings`, not `failed`).
    """
    result = certify_objective(_objective(T.QUANTILE), sampling=_sampling(T.QUANTILE))

    assert _status(result, "convexity") is CheckStatus.VIOLATED
    assert result.overall is CertificateOutcome.CERTIFIED_WITH_FINDINGS
    detail = _detail(result, "convexity")
    assert "%" in detail
    assert "abs" in detail


@pytest.mark.req("FR-152")
def test_a_convex_objective_is_not_flagged() -> None:
    """The negative control. Poisson's hessian is `w·exp(f)`, positive everywhere."""
    result = certify_objective(_objective(T.POISSON), sampling=_sampling(T.POISSON))

    assert _status(result, "convexity") is CheckStatus.PASS
    assert result.overall is CertificateOutcome.CERTIFIED


@pytest.mark.req("FR-147")
def test_points_near_a_branch_boundary_are_excluded_and_counted() -> None:
    """A central difference straddling `exp(f) = y` compares two different functions.

    The exclusion is what keeps the gradient check meaningful on a piecewise loss; the
    count is what stops the exclusion from being a way to pass.
    """
    result = certify_objective(
        _objective(T.ASYMMETRIC_SQUARED), sampling=_sampling(T.ASYMMETRIC_SQUARED)
    )

    detail = _detail(result, "analytic_vs_numeric_gradient")
    assert "excluded within h of" in detail
    assert "Richardson" in detail

    # The negative control, in the same test: a smooth template has nothing to exclude,
    # and says so rather than leaving the reader to infer it from a missing clause.
    smooth = certify_objective(_objective(T.GAMMA), sampling=_sampling(T.GAMMA))
    assert "no branch boundary" in _detail(smooth, "analytic_vs_numeric_gradient")


@pytest.mark.req("FR-148")
@pytest.mark.parametrize(
    "template",
    [T.CAPPED_GAMMA, T.SPLICED_SEVERITY, T.HUBER, T.QUANTILE, T.ZERO_INFLATED_POISSON],
    ids=lambda t: t.value,
)
def test_a_branch_is_a_reported_finding(template: ObjectiveTemplate) -> None:
    """Every piecewise template says where it changes form, not merely that it did."""
    result = certify_objective(_objective(template), sampling=_sampling(template))

    assert _status(result, "branch_discontinuity") is CheckStatus.WARN
    assert _detail(result, "branch_discontinuity") != ""


@pytest.mark.req("FR-148")
def test_a_template_with_no_branch_says_so() -> None:
    """The negative control for the branch check: Gamma is smooth in `f` everywhere."""
    result = certify_objective(_objective(T.GAMMA), sampling=_sampling(T.GAMMA))

    assert _status(result, "branch_discontinuity") is CheckStatus.PASS


@pytest.mark.req("FR-149")
def test_the_derivative_tolerance_is_step_aware() -> None:
    """The check reports its step and its measured error, not a bare verdict.

    FR-149 exists because a fixed tight tolerance at `h = 1e-6` fails a *correct*
    derivative on a steeply-curved loss. What makes the tolerance step-aware is visible in
    the detail: the step, and an error expressed against the finite-difference noise floor
    rather than against a constant.
    """
    result = certify_objective(_objective(T.TWEEDIE), sampling=_sampling(T.TWEEDIE))

    detail = _detail(result, "analytic_vs_numeric_hessian")
    assert "h=" in detail
    assert "1e-04" in detail or "0.0001" in detail


def _with_a_broken_derivative(
    monkeypatch: pytest.MonkeyPatch,
    template: ObjectiveTemplate,
    which: str,
    break_it: Any,
) -> None:
    """Swap one of a template's analytic derivatives for a deliberately wrong one.

    Patching the catalogue entry rather than `ObjectiveFns` keeps the break upstream of
    `compile_objective`, so the whole public path — compile, sample, difference, grade —
    runs exactly as it does for a real objective.
    """
    good = _TEMPLATES[template]
    fn = getattr(good, which)
    monkeypatch.setitem(
        _TEMPLATES,
        template,
        replace(good, **{which: lambda y, f, params: break_it(fn(y, f, params))}),
    )


@pytest.mark.req("FR-151")
@pytest.mark.parametrize("which", ["grad", "hess"])
def test_a_wrong_derivative_fails_certification(
    monkeypatch: pytest.MonkeyPatch, which: str
) -> None:
    """§13.4: the check is shown to fail on deliberately broken input.

    A derivative 1 % too large is the shape of the mistake certification exists to catch —
    a dropped constant or a mis-transcribed term, not a sign error a fit would blow up on.
    It must reach `failed` rather than `certified_with_findings`: a finding is carried to
    the approver (FR-152), and an objective whose gradient is simply wrong is not
    something an approver should be offered.
    """
    _with_a_broken_derivative(monkeypatch, T.GAMMA, which, lambda d: d * 1.01)

    result = certify_objective(_objective(T.GAMMA), sampling=_sampling(T.GAMMA))

    name = "analytic_vs_numeric_gradient" if which == "grad" else "analytic_vs_numeric_hessian"
    assert _status(result, name) is CheckStatus.FAILED
    assert result.overall is CertificateOutcome.FAILED


@pytest.mark.req("FR-149")
def test_a_wrong_derivative_is_caught_where_the_true_one_is_near_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The noise term is a floor on what the method can resolve, not a place to hide.

    `_agreement` subtracts the finite-difference noise from the difference as well as
    flooring the denominator (added 2026-08-18, when a correct Gamma hessian of `5.5e-07`
    was warned over a difference of `9e-13`). Loosening a tolerance is how a check stops
    checking, so this pins the other side of it: an error of `1e-08` — absolutely tiny, and
    two hundred times the noise at the points where the Gamma hessian is smallest — is
    still `failed`. Sampled `y/mu` never approaches 1 closely enough for the *gradient* to
    reach that regime, which is why this fixes the hessian specifically.
    """
    _with_a_broken_derivative(monkeypatch, T.GAMMA, "hess", lambda d: d + 1e-8)

    result = certify_objective(_objective(T.GAMMA), sampling=_sampling(T.GAMMA))

    assert _status(result, "analytic_vs_numeric_hessian") is CheckStatus.FAILED
    assert _status(result, "analytic_vs_numeric_gradient") is CheckStatus.PASS


# --- compilation -----------------------------------------------------------------------


@pytest.mark.req("FR-143")
def test_compile_resolves_the_templates_defaults() -> None:
    """§4.5's defaults are resolved when the objective is compiled, not when it is stored.

    A stored artifact that silently gained a default would mean two readers of the same
    row disagree about the loss — the one that read it before the default changed, and the
    one that read it after.
    """
    objective = _objective(T.TWEEDIE, params={})
    assert objective.params == {}

    fns = compile_objective(objective)
    assert fns.params["p"] == pytest.approx(1.5)
    assert fns.ref == f"custom_objective:{objective.slug}@1"


@pytest.mark.req("FR-143")
def test_gauss_newton_is_refused_where_there_is_no_gauss_newton_form() -> None:
    """A Gauss-Newton surrogate exists for a least-squares loss and is invented elsewhere.

    Refused at compile time — before a Job row exists — rather than at the first boosting
    round, where the failure would arrive as a dead job with a traceback in a worker log.
    """
    objective = _objective(T.POISSON, strategy=HessianStrategy.GAUSS_NEWTON)

    with pytest.raises(ObjectiveError) as raised:
        compile_objective(objective)

    assert raised.value.code == "OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED"
    assert "poisson" in str(raised.value)


@pytest.mark.req("FR-143")
@pytest.mark.parametrize(
    "template", [T.ASYMMETRIC_SQUARED, T.HUBER, T.PSEUDO_HUBER], ids=lambda t: t.value
)
def test_gauss_newton_is_accepted_where_the_loss_is_least_squares(
    template: ObjectiveTemplate,
) -> None:
    """The positive control: the three templates that do have one, and it is positive."""
    fns = compile_objective(_objective(template, strategy=HessianStrategy.GAUSS_NEWTON))
    y = np.array([1.0e5, 5.0e5, 9.0e5])
    f = np.log(np.array([2.0e5, 5.0e5, 4.0e5]))
    w = np.ones(3)

    assert np.all(fns.stabilise(y, f, w) > 0.0)


@pytest.mark.req("FR-152")
def test_clip_to_min_floors_a_negative_hessian_without_hiding_it() -> None:
    """`hess` stays analytic so `convexity` can see the truth; `stabilise` is what fits.

    Two methods rather than one because a single clipped hessian would make every
    objective look convex to its own certificate.
    """
    fns = compile_objective(_objective(T.QUANTILE, strategy=HessianStrategy.CLIP_TO_MIN))
    y = np.array([1.0e5, 9.0e5])
    f = np.log(np.array([5.0e5, 5.0e5]))
    w = np.ones(2)

    analytic = fns.hess(y, f, w)
    stabilised = fns.stabilise(y, f, w)

    assert analytic.min() < 0.0
    assert np.all(stabilised >= fns.hessian_min)


@pytest.mark.req("FR-152")
def test_abs_preserves_the_magnitude_a_clip_would_discard() -> None:
    fns = compile_objective(_objective(T.QUANTILE, strategy=HessianStrategy.ABS))
    y = np.array([1.0e5, 9.0e5])
    f = np.log(np.array([5.0e5, 5.0e5]))
    w = np.ones(2)

    assert np.allclose(fns.stabilise(y, f, w), np.abs(fns.hess(y, f, w)))


# --- the backend adapters ---------------------------------------------------------------


class _DMatrix:
    """The two methods the adapters read off a `DMatrix` or a `Dataset`, and nothing else.

    Both backends expose `get_label` and `get_weight` under those names, so one stub serves
    both adapters — which is also the reason the two are as close in shape as they are.
    """

    def __init__(self, y: np.ndarray, w: np.ndarray) -> None:
        self._y, self._w = y, w

    def get_label(self) -> np.ndarray:
        return self._y

    def get_weight(self) -> np.ndarray:
        return self._w


@pytest.mark.req("FR-165")
def test_the_xgboost_adapter_returns_the_weighted_pair() -> None:
    """`preds` already carries `base_margin`, so the adapter must not add the offset again.

    Asserted by construction: the adapter takes no `base_margin` argument, and what it
    returns is exactly `grad`/`stabilise` of the score it was handed.
    """
    fns = compile_objective(_objective(T.POISSON))
    y = np.array([0.0, 1.0, 3.0])
    w = np.array([0.5, 1.0, 2.0])
    f = np.array([-0.5, 0.0, 0.5])

    grad, hess = make_xgb_objective(fns)(f, _DMatrix(y, w))

    assert np.allclose(grad, fns.grad(y, f, w))
    assert np.allclose(hess, fns.stabilise(y, f, w))


@pytest.mark.req("FR-165")
def test_the_lightgbm_adapter_takes_the_form_lgb_train_calls() -> None:
    """`(preds, dataset)` — `lgb.train`'s form, not the sklearn wrapper's `(y, f, w)`.

    §5.2 sketched the three-argument form; `lgb.train` calls
    `fobj(inner_predict(0), self.train_set)` and the sklearn shape raises `TypeError` on
    the first boosting round. The weights come off the dataset, so the case weights the
    three-argument form was chosen for are still there — asserted below, since dropping
    them fits a different model and raises nothing.
    """
    fns = compile_objective(_objective(T.POISSON))
    y = np.array([0.0, 1.0, 3.0])
    w = np.array([0.5, 1.0, 2.0])
    f = np.array([-0.5, 0.0, 0.5])

    grad, hess = make_lgb_objective(fns)(f, _DMatrix(y, w))

    assert np.allclose(grad, fns.grad(y, f, w))
    assert np.allclose(hess, fns.stabilise(y, f, w))
    assert not np.allclose(grad, fns.grad(y, f, np.ones_like(y)))


@pytest.mark.req("FR-165")
def test_a_non_finite_derivative_aborts_naming_the_round_and_the_inputs() -> None:
    """FR-165's abort is only useful if it says *where*.

    A boosting fit that dies on round 41 with `nan` and no further detail leaves an author
    with a 20-million-row dataset and no way in; the round and the offending input range
    are the way in.
    """
    fns = compile_objective(_objective(T.GAMMA))
    y = np.array([1.0, 2.0, 3.0])
    f = np.array([0.0, 1.0, 2.0])
    grad = np.array([1.0, np.inf, 3.0])
    hess = np.array([1.0, 1.0, np.nan])

    with pytest.raises(NonFiniteDerivativeError) as raised:
        _finite_or_abort(fns, grad, hess, y, f, round_index=41)

    assert raised.value.round_index == 41
    assert raised.value.code == "OBJECTIVE_NONFINITE_DERIVATIVE"
    message = str(raised.value)
    assert "round 41" in message
    assert "2 of 3 rows" in message


@pytest.mark.req("FR-165")
def test_a_finite_pair_does_not_abort() -> None:
    fns = compile_objective(_objective(T.GAMMA))
    ok = np.array([1.0, 2.0, 3.0])

    _finite_or_abort(fns, ok, ok, ok, ok, round_index=0)


# --- applicability ----------------------------------------------------------------------


@pytest.mark.req("FR-153")
def test_an_author_may_narrow_applicability_and_the_narrowed_form_still_certifies() -> None:
    """A Huber restricted to severity is still a Huber; certification follows the objective.

    The refusal to *widen* is enforced on the artifact (`model-schema`), and the refusal to
    *use* an objective outside its applicability is enforced at spec validation. What this
    test covers is the half in between: the compiled functions honour the declaration they
    were given rather than the template's.
    """
    narrowed = Applicability(
        responses=frozenset({ResponseKind.CLAIM_SEVERITY}),
        backends=frozenset({ObjectiveBackend.XGBOOST}),
        y_domain=TEMPLATE_APPLICABILITY[T.HUBER].y_domain,
    )
    objective = _objective(T.HUBER, applicability=narrowed)

    result = certify_objective(objective, sampling=_sampling(T.HUBER))

    assert result.overall is not CertificateOutcome.FAILED
    assert "severity" in _detail(result, "smoke_fit")


# --- progress ---------------------------------------------------------------------------


class _Recorder:
    """A `ProgressCallback` that keeps what it was told."""

    def __init__(self) -> None:
        self.fractions: list[float] = []
        self.stages: list[str] = []

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        self.fractions.append(fraction)
        self.stages.append(stage)

    def check_cancelled(self) -> None:
        return None


@pytest.mark.req("FR-151")
def test_certification_reports_progress_monotonically() -> None:
    """Certification runs as a Job, and a Job with no progress reads as a hung one."""
    recorder = _Recorder()

    certify_objective(_objective(T.GAMMA), sampling=_sampling(T.GAMMA), progress=recorder)

    assert recorder.fractions == sorted(recorder.fractions)
    assert recorder.fractions[-1] == pytest.approx(1.0)
    assert len({stage for stage in recorder.stages}) > 1


@pytest.mark.req("FR-143")
def test_compiled_functions_are_linear_in_the_case_weight() -> None:
    """Every template's loss is linear in `w`, which is why `w` is not in the templates.

    Checked once, across the catalogue, because a template that folded `w` into its own
    body would break the weighted-sum identity a booster's leaf value depends on.
    """
    y = np.array([1.0e5, 4.0e5])
    f = np.log(np.array([2.0e5, 3.0e5]))
    ones = np.ones(2)
    w = np.array([0.25, 4.0])

    for template in (T.GAMMA, T.HUBER, T.PSEUDO_HUBER, T.QUANTILE, T.ASYMMETRIC_SQUARED):
        fns: ObjectiveFns = compile_objective(_objective(template))
        assert np.allclose(fns.loss(y, f, w), w * fns.loss(y, f, ones))
        assert np.allclose(fns.grad(y, f, w), w * fns.grad(y, f, ones))
        assert np.allclose(fns.hess(y, f, w), w * fns.hess(y, f, ones))


# --- expression objectives, the per-round budget and the non-finite abort (WK-690 S2) -----

_ADAPTERS = [make_xgb_objective, make_lgb_objective]
_EXPRESSION_LOSS = "w * (exp(f) - y * f)"


def _expression_fns(loss: str = _EXPRESSION_LOSS) -> ObjectiveFns:
    return compile_expression_objective(
        ref="custom_objective:test-expression@1",
        loss=loss,
        parameters={},
        y_domain=YDomain(min_inclusive=0.0),
        hessian_strategy=HessianStrategy.CLIP_TO_MIN,
        hessian_min=1e-6,
    )


def _slowed(fns: ObjectiveFns, seconds: float) -> ObjectiveFns:
    """`fns` with a `grad` that sleeps: the template's, or the expression's kernel."""
    if fns.template is not None:

        class _Slow(ObjectiveFns):
            def grad(self, y: Any, f: Any, w: Any) -> Any:
                time.sleep(seconds)
                return super().grad(y, f, w)

        return _Slow(**{k: getattr(fns, k) for k in fns.__dataclass_fields__})
    kernels = fns._expression
    assert kernels is not None
    inner = kernels.grad

    def slow(y: Any, f: Any, w: Any) -> Any:
        time.sleep(seconds)
        return inner(y, f, w)

    return replace(fns, _expression=replace(kernels, grad=slow))


_ROUND_INPUTS = (np.array([0.0, 1.0, 3.0, 2.0]), np.array([0.1, 0.2, 0.3, 0.4]))


@pytest.mark.req("FR-165")
@pytest.mark.req("NFR-483")
@pytest.mark.parametrize("adapter", _ADAPTERS, ids=["xgboost", "lightgbm"])
@pytest.mark.parametrize("kind", ["template", "expression"])
def test_round_budget_aborts_a_slow_objective_naming_the_round(
    adapter: Any, kind: str
) -> None:
    """The budget binds both kinds at the one place both pass through (DP-S2-3 (a))."""
    fns = compile_objective(_objective(T.POISSON)) if kind == "template" else _expression_fns()
    y, f = _ROUND_INPUTS
    objective = adapter(_slowed(fns, 0.05), round_budget_s=0.01)

    with pytest.raises(RoundBudgetExceededError) as raised:
        objective(f, _DMatrix(y, np.ones_like(y)))

    assert raised.value.round_index == 0
    assert raised.value.code == "OBJECTIVE_ROUND_BUDGET_EXCEEDED"
    assert "round 0" in str(raised.value)
    assert isinstance(raised.value, CodedError)


@pytest.mark.req("FR-165")
@pytest.mark.req("NFR-483")
@pytest.mark.parametrize("adapter", _ADAPTERS, ids=["xgboost", "lightgbm"])
@pytest.mark.parametrize("kind", ["template", "expression"])
def test_round_budget_positive_control(adapter: Any, kind: str) -> None:
    """The same slowed objective inside its budget completes: the abort above is the budget's."""
    fns = compile_objective(_objective(T.POISSON)) if kind == "template" else _expression_fns()
    y, f = _ROUND_INPUTS
    grad, hess = adapter(_slowed(fns, 0.05), round_budget_s=5.0)(f, _DMatrix(y, np.ones_like(y)))
    assert grad.shape == y.shape
    assert hess.shape == y.shape


@pytest.mark.req("FR-165")
@pytest.mark.parametrize("adapter", _ADAPTERS, ids=["xgboost", "lightgbm"])
def test_the_default_round_budget_is_the_rulings(adapter: Any) -> None:
    assert DEFAULT_ROUND_BUDGET_S == 30.0
    y, f = _ROUND_INPUTS
    grad, _ = adapter(_expression_fns())(f, _DMatrix(y, np.ones_like(y)))
    assert np.all(np.isfinite(grad))


@pytest.mark.req("FR-165")
@pytest.mark.parametrize("adapter", _ADAPTERS, ids=["xgboost", "lightgbm"])
def test_nonfinite_aborts_an_expression_naming_the_round_and_no_value(adapter: Any) -> None:
    """DP-S2-4 (b): `exp(exp(10))` overflows. The text names the round, the row count and the
    fields, and carries no input value; the ranges are structured attributes."""
    fns = _expression_fns("w * exp(exp(f))")
    y = np.array([7.25, 7.75])
    f = np.array([10.0, 0.0])

    with pytest.raises(NonFiniteDerivativeError) as raised:
        adapter(fns)(f, _DMatrix(y, np.ones_like(y)))

    error = raised.value
    assert error.round_index == 0
    assert error.rows == 1
    assert error.f_range == (10.0, 10.0)
    assert error.y_range == (7.25, 7.25)
    text = str(error)
    assert "round 0" in text
    assert "1 of 2 rows" in text
    assert "y" in text
    assert "f" in text
    for value in ("7.25", "7.75", "10"):
        assert value not in text
    assert isinstance(error, CodedError)
    assert error.code == "OBJECTIVE_NONFINITE_DERIVATIVE"
    assert safe_error_detail(error) == text  # what a job record would keep


@pytest.mark.req("FR-165")
def test_an_expression_objective_refuses_gauss_newton() -> None:
    """FR-152: a Gauss-Newton hessian exists only for a least-squares template."""
    with pytest.raises(ObjectiveError) as raised:
        compile_expression_objective(
            ref="custom_objective:test-expression@1",
            loss=_EXPRESSION_LOSS,
            parameters={},
            y_domain=YDomain(min_inclusive=0.0),
            hessian_strategy=HessianStrategy.GAUSS_NEWTON,
            hessian_min=1e-6,
        )
    assert raised.value.code == "OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED"


@pytest.mark.req("FR-144")
def test_an_expression_objective_matches_the_builtin_it_equals() -> None:
    """`w * (exp(f) - y * f)` is Poisson's deviance up to a constant in `f`: the compiled
    expression and the builtin give the same gradient and hessian."""
    y = np.array([0.0, 1.0, 3.0, 2.0])
    f = np.array([-0.5, 0.0, 0.5, 1.0])
    w = np.array([0.5, 1.0, 2.0, 1.5])
    builtin = compile_objective(_objective(T.POISSON))
    expression = _expression_fns()
    assert np.allclose(expression.grad(y, f, w), builtin.grad(y, f, w))
    assert np.allclose(expression.stabilise(y, f, w), builtin.stabilise(y, f, w))
    assert expression.inverse_link == "exp"


# --- the expression certificate (WK-690 S2, FR-146 to FR-151) ------------------------------

_SPEC_EXAMPLE = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
_SPEC_PARAMS = {"w_under": 2.0, "w_over": 1.0}
_EXPRESSION_SAMPLING = SamplingSpec(
    n_points=1000, seed=_SEED, y_range=(0.1, 50.0), f_range=(-2.0, 4.0), w_range=(0.5, 2.0)
)


def _certify_expression(
    loss: str,
    *,
    parameters: dict[str, float] | None = None,
    derived: Derived | None = None,
    sampling: SamplingSpec = _EXPRESSION_SAMPLING,
) -> Any:
    return certify_expression_objective(
        ref="custom_objective:test-expression@1",
        loss=loss,
        parameters=parameters or {},
        derived=derived,
        y_domain=YDomain(min_inclusive=0.0),
        hessian_strategy=HessianStrategy.CLIP_TO_MIN,
        hessian_min=1e-6,
        inverse_link="exp",
        sampling=sampling,
    )


_SYMBOLIC_NAMES = (
    "symbolic_vs_numeric_gradient",
    "symbolic_vs_numeric_hessian",
    "finiteness",
    "convexity",
    "branch_discontinuity",
    "minimum_at_truth",
    "monotone_loss",
    "scale_behaviour",
    "smoke_fit",
)


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-147")
@pytest.mark.req("FR-148")
@pytest.mark.req("FR-151")
def test_expression_certificate_spec_example() -> None:
    """§4.6's example, certified: nine checks with the symbolic pair, a real `where()`
    boundary found and excluded, and the SymPy version recorded."""
    result = _certify_expression(_SPEC_EXAMPLE, parameters=_SPEC_PARAMS)

    assert tuple(c.name for c in result.checks) == _SYMBOLIC_NAMES
    assert result.overall is CertificateOutcome.CERTIFIED_WITH_FINDINGS
    assert _status(result, "convexity") is CheckStatus.VIOLATED
    assert _status(result, "branch_discontinuity") is CheckStatus.WARN
    assert _status(result, "symbolic_vs_numeric_gradient") is CheckStatus.PASS
    assert _status(result, "symbolic_vs_numeric_hessian") is CheckStatus.PASS
    match = re.search(r"([\d,]+) of [\d,]+ excluded within h of", _detail(
        result, "symbolic_vs_numeric_gradient"))
    assert match is not None
    assert int(match.group(1).replace(",", "")) > 0
    assert result.library_versions["sympy"] == sympy.__version__


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-149")
def test_expression_certificate_smooth_loss() -> None:
    """No `where()`: nothing to exclude, and the symbolic pair agrees with the numerics."""
    result = _certify_expression(_EXPRESSION_LOSS)

    assert _status(result, "branch_discontinuity") is CheckStatus.PASS
    assert "no branch boundary" in _detail(result, "branch_discontinuity")
    assert "no branch boundary" in _detail(result, "symbolic_vs_numeric_gradient")
    assert _status(result, "symbolic_vs_numeric_gradient") is CheckStatus.PASS
    assert _status(result, "symbolic_vs_numeric_hessian") is CheckStatus.PASS


@pytest.mark.req("FR-148")
def test_expression_certificate_names_a_dropped_dirac_delta_as_a_found_boundary() -> None:
    """DP-S2-2's condition: `abs` has a kink the printer rewrote to `where`, and the
    certificate names it rather than certifying the loss as smooth."""
    result = _certify_expression("w * abs(y - f)")

    assert _status(result, "branch_discontinuity") is CheckStatus.WARN
    assert "y" in _detail(result, "branch_discontinuity")
    assert " > " in _detail(result, "branch_discontinuity")


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-149")
def test_expression_certificate_catches_a_wrong_derivative() -> None:
    """The check on broken input: a hessian off by 1 % must fail the symbolic comparison."""
    good = derive(_EXPRESSION_LOSS)
    wrong = replace(good, hessian=f"1.01 * ({good.hessian})")

    result = _certify_expression(_EXPRESSION_LOSS, derived=wrong)

    assert _status(result, "symbolic_vs_numeric_hessian") is CheckStatus.FAILED
    assert _status(result, "symbolic_vs_numeric_gradient") is CheckStatus.PASS
    assert result.overall is CertificateOutcome.FAILED


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-165")
def test_expression_certificate_division_by_a_denominator_that_reaches_zero_fails() -> None:
    """§4.6 and DP-S2-5 (a): `f` crosses 0 over the f-range, so `/ f` fails `finiteness`
    naming the denominator. The control has a denominator bounded away from 0."""
    failing = _certify_expression("w * (y - f) ** 2 / f")
    assert _status(failing, "finiteness") is CheckStatus.FAILED
    assert "denominator" in _detail(failing, "finiteness")

    control = _certify_expression("w * (y - f) ** 2 / (1 + f ** 2)")
    assert _status(control, "finiteness") is CheckStatus.PASS
    assert control.overall is not CertificateOutcome.FAILED


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-165")
def test_expression_certificate_division_catches_an_even_order_zero() -> None:
    """DP-S2-5's refinement: `(exp(f) - 3) ** 2` touches 0 at `f = log 3` with no sign change,
    and a grid step can straddle it. The bounded refinement drives the minimum to 0."""
    result = _certify_expression("w * y / ((exp(f) - 3) ** 2 + 1e-30)")
    # The 1e-30 keeps the denominator positive, so only the refinement sees it reach 0.
    assert _status(result, "finiteness") is CheckStatus.FAILED
    assert "denominator" in _detail(result, "finiteness")


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-165")
def test_expression_certificate_division_catches_a_sign_change_with_no_zero_on_the_grid() -> None:
    """DP-S2-5's sign-change clause on its own: a denominator that jumps from -1 to 1 has no
    zero and no minimum of its magnitude for the refinement to find, so only the sign change
    sees it (by continuity a zero lies between, and here there is a discontinuity instead)."""
    result = _certify_expression("w * y / where(f < 1, -1, 1)")
    assert _status(result, "finiteness") is CheckStatus.FAILED
    assert "changes sign" in _detail(result, "finiteness")


@pytest.mark.req("FR-146")
def test_expression_certificate_records_the_patched_sympy_version_derivation_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1289's second violation, on the certificate: `library_versions.sympy` is read from
    `sympy.__version__` at the call, never written from a literal."""
    monkeypatch.setattr(sympy, "__version__", "9.9.9")
    result = _certify_expression(_EXPRESSION_LOSS)
    assert result.library_versions["sympy"] == "9.9.9"


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-165")
def test_expression_certificate_division_by_the_even_order_zero_of_rl_1328() -> None:
    """RL-1328's acceptance for DP-S2-5: a denominator `(exp(f) - y) ** 2` does not pass
    `finiteness` on the default grid."""
    result = _certify_expression("w / (exp(f) - y) ** 2")
    assert _status(result, "finiteness") is CheckStatus.FAILED


@pytest.mark.req("FR-144")
def test_the_expression_path_takes_the_model_schema_domain_and_strategy_types() -> None:
    """DP-S2-1 (c): primitives, with the existing types and never a hand-written copy."""
    import inspect

    for function in (compile_expression_objective, certify_expression_objective):
        hints = inspect.signature(function).parameters
        assert "YDomain" in str(hints["y_domain"].annotation)
        assert "HessianStrategy" in str(hints["hessian_strategy"].annotation)


_BEFORE = json.loads(
    (Path(__file__).parent / "data" / "template_certificates_before_wk690s2.json").read_text(
        encoding="utf-8"
    )
)


_MAX_RELATIVE_ERROR = re.compile(r"max relative error (\S+)")

#: Every figure a certificate detail prints that is a measurement rather than an input, as
#: `certify_objective` produces it (the producer sweep is FD-1354's addendum). Each is
#: replaced before the comparison, because each depends on the runner's floating point,
#: its BLAS or its threading: the two finite-difference errors, the deviation of the
#: minimiser from log y, the gradient's span and extremes, the share of negative hessians,
#: the share of sampled y above a branch, the smoke fit's recovered relativity and its
#: percentage error, and its elapsed time.
_MEASURED_FIGURES = (
    (_MAX_RELATIVE_ERROR, "max relative error <e>"),
    (re.compile(r"\|f\* - log y\| = [^;. ]+(?:\.\d+)?(?:e[-+]\d+)?"), "|f* - log y| = <d>"),
    (
        re.compile(r"spans \S+ orders over the sampled domain \([^)]*\)"),
        "spans <o> orders over the sampled domain (<lo> to <hi>)",
    ),
    (re.compile(r"hessian < 0 at \S+%"), "hessian < 0 at <p>%"),
    (re.compile(r"; \S+% of the sampled y lie"), "; <p>% of the sampled y lie"),
    (re.compile(r"relativity of \S+ against a true ([\d.]+) \(\S+%\)"),
     r"relativity of <r> against a true \1 (<p>%)"),
    (re.compile(r"\d+\.\ds$"), "<t>s"),
)


def _normalise_measured(detail: str) -> str:
    """Replace every runner-dependent measurement in a certificate detail."""
    for pattern, placeholder in _MEASURED_FIGURES:
        detail = pattern.sub(placeholder, detail)
    return detail


#: What a rendered detail prints that is an INPUT, not a measurement, and so may keep its
#: figures: the sampling ranges (`y ∈ [a, b]`, `f ∈ [a, b]`, `w ∈ [a, b]` - they come from
#: the `SamplingSpec` the test passes), the finite-difference step `h=`, the objective's own
#: `hessian_min=`, the smoke fit's
#: true relativity, and the loss-surface steps. The guard tells them apart from a
#: measurement by this closed list of shapes, so a new figure of any other shape fails.
_DETERMINISTIC_INPUTS = re.compile(
    r"[yfw] ∈ \[[^\]]*\]|h=[0-9.e+-]+|hessian_min=[0-9.e+-]+|against a true [0-9.]+"
    r"|steps of [0-9., ]+"
)
#: A float in fixed, g or e notation: the shape every measured figure is rendered in.
_FLOAT_LITERAL = re.compile(r"\d+\.\d+(?:e[-+]?\d+)?|\d+e[-+]?\d+")


def _surviving_floats(detail: str) -> list[str]:
    return _FLOAT_LITERAL.findall(_DETERMINISTIC_INPUTS.sub("", _normalise_measured(detail)))


@pytest.mark.req("FR-146")
@pytest.mark.parametrize("template", list(T), ids=lambda t: t.value)
def test_no_measured_figure_survives_normalisation_in_a_template_certificate(
    template: ObjectiveTemplate,
) -> None:
    """A measured figure is normalised or the test fails here, every time.

    Without this, a certificate figure that the comparison above forgot to normalise
    fails only on the runner whose floating point differs - one run in N (main went red
    on `max relative error` and then on `max |f* - log y|`, each found by CI, not by
    reading). This renders every template's certificate and fails if a float in fixed or
    exponent notation survives `_normalise_measured`, outside the closed list of
    deterministic inputs in `_DETERMINISTIC_INPUTS`. FD-1354 has the producer sweep.
    """
    result = certify_objective(_objective(template), sampling=_sampling(template))
    survivors = {c.name: _surviving_floats(c.detail) for c in result.checks}
    assert {name: found for name, found in survivors.items() if found} == {}


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-151")
@pytest.mark.parametrize("template", list(T), ids=lambda t: t.value)
def test_template_certificate_unchanged(template: ObjectiveTemplate) -> None:
    """A template certificate is what it was before this slice, check by check.

    The reference is `certify_objective`'s own output at `origin/main` 71b67220, on this
    file's `_objective` and `_sampling`, with the smoke fit's elapsed seconds normalised:
    the ledger (LG-1350, Task 5) records how it was produced.
    """
    result = certify_objective(_objective(template), sampling=_sampling(template))
    expected = _BEFORE[template.value]
    assert result.overall.value == expected["overall"]
    assert sorted(result.library_versions) == expected["library_versions_keys"]
    got = [
        {
            "name": c.name,
            "status": c.status.value,
            "detail": _normalise_measured(c.detail),
        }
        for c in result.checks
    ]
    assert got == [
        {**c, "detail": _normalise_measured(c["detail"])} for c in expected["checks"]
    ]
    # The finite-difference error varies by runner (2.28e-12 against 3.21e-12 at the same
    # tree), so it is normalised above and bounded here: each reported figure must lie
    # within the engine's own tolerance for the status the check carries. The other
    # measured figures have no engine symbol to bound them (the deviation from log y has no
    # tolerance; the scale and smoke-fit thresholds are inline literals), so those checks
    # are held by their status, which is compared above and which each figure decides.
    for c in result.checks:
        for figure in _MAX_RELATIVE_ERROR.findall(c.detail):
            bound = _TOLERANCE_PASS if c.status.value == "pass" else _TOLERANCE_WARN
            assert float(figure) <= bound, (c.name, figure, bound)


# --- fit-time compilation of an `expression` objective (WK-690 S3 Task 6, RL-1362 DP-S3-1) ----


def _expression_artifact(
    *,
    loss: str = _EXPRESSION_LOSS,
    derived: Derived | None = None,
    responses: frozenset[ResponseKind] = frozenset({ResponseKind.BURNING_COST}),
    stored: bool = True,
) -> CustomObjective:
    """An `expression` artifact as the platform stores it: `derived` is the stored block.

    `draft`: `compile_objective` reads no status; the fit gate is `gbm._compile_custom`'s.
    """
    text = derived or derive(loss)
    block = DerivedBlock(
        gradient=text.gradient,
        hessian=text.hessian,
        derivation_tool="sympy",
        derivation_version=text.derivation_version,
        derived_at=datetime(2026, 10, 4, tzinfo=UTC),
    )
    return CustomObjective(
        id=uuid4(),
        slug="test-expression",
        version=1,
        kind=ObjectiveKind.EXPRESSION,
        bound_symbols=["y", "f", "w"],
        parameters=[],
        loss=loss,
        derived=block if stored else None,
        applicability=Applicability(
            responses=responses,
            backends=frozenset({ObjectiveBackend.XGBOOST, ObjectiveBackend.LIGHTGBM}),
            offset_required=False,
            y_domain=YDomain(min_inclusive=0.0),
        ),
    )


def _grid() -> tuple[Any, Any, Any]:
    rng = np.random.default_rng(_SEED)
    return rng.uniform(0.5, 5.0, 50), rng.uniform(-1.0, 1.0, 50), rng.uniform(0.5, 2.0, 50)


@pytest.mark.req("FR-144")
def test_compile_dispatch_an_expression_objective_compiles() -> None:
    fns = compile_objective(_expression_artifact())
    reference = _expression_fns()
    y, f, w = _grid()
    assert fns.ref == "custom_objective:test-expression@1"
    assert np.array_equal(fns.grad(y, f, w), reference.grad(y, f, w))
    assert np.array_equal(fns.hess(y, f, w), reference.hess(y, f, w))


@pytest.mark.req("FR-144")
def test_compile_dispatch_uses_the_stored_derived_text_and_never_re_derives() -> None:
    """RL-1362 DP-S3-1: the Approver read the stored text, so that text is what is compiled."""
    fresh = derive(_EXPRESSION_LOSS)
    stored = replace(fresh, hessian="3 * w * exp(f)")
    assert stored.hessian != fresh.hessian
    fns = compile_objective(_expression_artifact(derived=stored))
    y, f, w = _grid()
    assert np.allclose(fns.hess(y, f, w), np.maximum(3 * w * np.exp(f), 1e-6))
    assert not np.allclose(fns.hess(y, f, w), _expression_fns().hess(y, f, w))


@pytest.mark.req("FR-144")
def test_compile_dispatch_refuses_an_underived_expression_objective_by_name() -> None:
    with pytest.raises(ObjectiveError, match=r"test-expression@1.*no stored derivation") as refused:
        compile_objective(_expression_artifact(stored=False))
    assert refused.value.code == "VALIDATION_FAILED"
    assert "/derive" in str(refused.value)


@pytest.mark.req("FR-144")
@pytest.mark.parametrize(
    ("responses", "link"),
    [
        (frozenset({ResponseKind.BURNING_COST}), "exp"),
        (frozenset({ResponseKind.CONVERSION}), "logistic"),
    ],
)
def test_compile_dispatch_reads_the_link_through_inverse_link_for(
    responses: frozenset[ResponseKind], link: str
) -> None:
    fns = compile_objective(_expression_artifact(responses=responses))
    assert fns._expression is not None
    assert fns._expression.inverse_link == link
