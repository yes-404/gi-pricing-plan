"""Evaluating and certifying a Custom Metric — FR-MODEL-103/104/105, `02` §4.7 and §4.13.

`pricing-core` is handed the artifact and never resolves a reference (ADR-0001): every
function here takes a `CustomMetric`, and the backend is what turned a
`custom_metric:<slug>@<version>` string into one.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import numpy.typing as npt

from model_schema.metrics import CustomMetric, MetricDirection
from model_schema.objectives import (
    CertificateCheck,
    CertificateResult,
    CheckStatus,
    ObjectiveTemplate,
    SamplingSpec,
)
from pricing_core.modelling.objectives import template_loss

__all__ = ["certify_metric", "evaluate_metric"]

_Arr = npt.NDArray[np.float64]

#: The sampling grid the certificate reports. Fixed rather than tunable: a certificate whose
#: grid the author chose is a certificate the author can pass by choosing.
_N_POINTS: Final = 10_000
_Y_RANGE: Final = (0.0, 1e7)
_F_RANGE: Final = (-20.0, 20.0)
_W_RANGE: Final = (1e-3, 1e4)


def _template_of(metric: CustomMetric) -> ObjectiveTemplate:
    """Narrow `metric.template` from `ObjectiveTemplate | None` — refused at the type.

    `CustomMetric._only_templates_are_built` already guarantees a template-kind metric
    carries one; this is the runtime check that lets mypy --strict see it too, following
    `certify_objective`'s own pattern rather than silencing the narrowing.
    """
    if metric.template is None:  # pragma: no cover — refused at the type
        raise ValueError("a Phase 1 metric always names a template (FR-MODEL-103)")
    return metric.template


def evaluate_metric(metric: CustomMetric, y: _Arr, f: _Arr, w: _Arr) -> float:
    """The template's loss as an exposure-weighted mean (FR-MODEL-103).

    `f` is the **raw score**, not the transformed prediction — the same convention the
    objective path uses, and the reason FR-MODEL-107 exists: a backend's builtin metric
    receives the raw score under a callable objective and silently means something else.
    """
    template = _template_of(metric)
    per_row = template_loss(template)(y, f, dict(metric.params))
    return float(np.average(per_row, weights=w))


def _grid(seed: int) -> tuple[_Arr, _Arr, _Arr]:
    rng = np.random.default_rng(seed)
    y = rng.uniform(*_Y_RANGE, _N_POINTS)
    f = rng.uniform(*_F_RANGE, _N_POINTS)
    w = rng.uniform(*_W_RANGE, _N_POINTS)
    return y, f, w


def _better(direction: MetricDirection, candidate: float, reference: float) -> bool:
    if direction is MetricDirection.LOWER_IS_BETTER:
        return candidate < reference
    return candidate > reference


def certify_metric(metric: CustomMetric, *, seed: int) -> CertificateResult:
    """§4.7's four metric checks (FR-MODEL-105).

    Returns the findings only: no id, no clock, no Job — the backend stamps those around
    this into a `MetricCertificate` (ADR-0001, the same split as `certify_objective`).
    """
    template = _template_of(metric)
    y, f, w = _grid(seed)
    checks: list[CertificateCheck] = []

    values = template_loss(template)(y, f, dict(metric.params))
    finite = bool(np.all(np.isfinite(values)))
    checks.append(
        CertificateCheck(
            name="finiteness",
            status=CheckStatus.PASS if finite else CheckStatus.FAILED,
            detail=(
                f"no NaN/inf over {_N_POINTS:,} sampled points, y in {_Y_RANGE}, "
                f"f in {_F_RANGE}, w in {_W_RANGE}"
                if finite
                else f"{int(np.sum(~np.isfinite(values))):,} of {_N_POINTS:,} sampled "
                "points are NaN or inf"
            ),
        )
    )

    # `direction_holds`: at the truth `f = log(y)` the metric must be better than at a
    # perturbed score. This is what catches a `direction` declared backwards — the defect
    # that otherwise halves the value of early stopping while producing a fitted model.
    truthful = np.log(np.clip(y, 1e-9, None))
    at_truth = evaluate_metric(metric, y, truthful, w)
    perturbed = evaluate_metric(metric, y, truthful + 1.0, w)
    holds = _better(metric.direction, at_truth, perturbed)
    checks.append(
        CertificateCheck(
            name="direction_holds",
            status=CheckStatus.PASS if holds else CheckStatus.FAILED,
            detail=(
                f"value at f=log(y) is {at_truth:.6g} against {perturbed:.6g} one unit away; "
                f"the metric declares {metric.direction.value}"
            ),
        )
    )

    small = evaluate_metric(metric, y, truthful, w)
    large = evaluate_metric(metric, y * 10.0, np.log(np.clip(y * 10.0, 1e-9, None)), w)
    span = abs(large) / abs(small) if small else float("inf")
    checks.append(
        CertificateCheck(
            name="scale_behaviour",
            status=CheckStatus.PASS if span < 1e3 else CheckStatus.WARN,
            detail=f"value changes by a factor of {span:.3g} when y is scaled by 10",
        )
    )

    # `smoke_evaluation`: on a constant population the weighted mean of a constant loss is
    # that loss, which is computable without this module.
    ones_y = np.ones(1_000)
    ones_f = np.zeros(1_000)
    ones_w = np.full(1_000, 3.0)
    expected = float(template_loss(template)(ones_y, ones_f, dict(metric.params))[0])
    observed = evaluate_metric(metric, ones_y, ones_f, ones_w)
    agrees = bool(np.isclose(observed, expected, rtol=1e-12))
    checks.append(
        CertificateCheck(
            name="smoke_evaluation",
            status=CheckStatus.PASS if agrees else CheckStatus.FAILED,
            detail=(
                f"constant population of 1,000: {observed:.12g} against the hand-computable "
                f"{expected:.12g}"
            ),
        )
    )

    frozen = tuple(checks)
    return CertificateResult(
        checks=frozen,
        sampling=SamplingSpec(
            n_points=_N_POINTS,
            seed=seed,
            y_range=_Y_RANGE,
            f_range=_F_RANGE,
            w_range=_W_RANGE,
        ),
        overall=CertificateResult.outcome_of(frozen),
        library_versions={"numpy": np.__version__},
    )
