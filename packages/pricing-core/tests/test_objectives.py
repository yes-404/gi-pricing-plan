"""The Custom Objective catalogue and its certification (`02` §4.5/§4.7, FR-142, FR-143, FR-144, FR-145, FR-146, FR-152, FR-153, FR-154, FR-163, FR-164, FR-165).

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

from dataclasses import replace
from typing import Any
from uuid import uuid4

import numpy as np
import pytest

from model_schema import (
    TEMPLATE_APPLICABILITY,
    Applicability,
    CertificateOutcome,
    CheckStatus,
    CustomObjective,
    HessianStrategy,
    ObjectiveBackend,
    ObjectiveTemplate,
    ResponseKind,
    SamplingSpec,
)
from pricing_core.modelling import (
    ObjectiveFns,
    certify_objective,
    compile_objective,
    make_lgb_objective,
    make_xgb_objective,
)
from pricing_core.modelling.errors import NonFiniteDerivativeError, ObjectiveError
from pricing_core.modelling.objectives import _TEMPLATES, _finite_or_abort

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
