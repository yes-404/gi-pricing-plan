"""Model quality evidence, computed once at fit time (`02` §3.8, FR-MODEL-49..55, 81).

What this module owes its caller, in the spec's own terms:

* **FR-MODEL-54 — train and holdout, always both.** Every metric here is computed twice
  over two frames and returned in a shape that cannot hold one without the other. The
  requirement calls a one-sided diagnostic a defect; `UniversalDiagnostics` makes it
  unrepresentable rather than merely discouraged.
* **FR-MODEL-55 — the weighting is part of the metric.** Derived once from the spec, in
  `_weighting`, and recorded on both partitions. An exposure-weighted A/E and an
  unweighted one differ by more than rounding on any real book.
* **FR-MODEL-50/51 — universal metrics for every model type, GLM metrics for GLMs.** The
  split is the roadmap's: FR-MODEL-50 is the gate, and 51 rides along because the GLM is
  the only thing this platform can currently fit. FR-MODEL-52's GBM block is owned by the
  slice that produces a GBM.
* **FR-MODEL-81 — complexity is recorded on every fit**, beside the thresholds it was
  judged against.

**Deviance is computed here, not in `glm`.** The spine declared `GlmFitResult.deviance`
and never populated it; a field that is always `None` teaches a reader that the model has
no deviance rather than that nobody computed it. It is a diagnostic, so it lives with the
diagnostics and the fit result carries it for convenience.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl
from scipy import stats

from model_schema import (
    AeCell,
    Banding,
    CalibrationBin,
    ComplexityDiagnostic,
    Factor,
    GlmDiagnostics,
    GlmFitResult,
    GlmSpec,
    Grouping,
    LiftBin,
    PartitionDiagnostics,
    ResidualSummary,
    TypeIIITest,
    UniversalDiagnostics,
    Weighting,
)
from pricing_core.modelling.factors import resolve_factors
from pricing_core.modelling.predict import predict_glm
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = ["DiagnosticsResult", "compute_diagnostics", "deviance", "unit_deviance"]

#: Bins for the lift, gains and calibration curves. Ten is what `02` §3.8 says ("predicted
#: decile") and what every actuarial reviewer expects to see.
_BINS = 10

#: The exact two-sided 97.5 % normal quantile, as `glm` spells it. A rounded 1.96 gives a
#: different interval, and the two modules must not disagree about the same number.
_NORMAL_975 = 1.959963984540054


@dataclass(frozen=True)
class DiagnosticsResult:
    """What a fit's diagnostics amount to, before the platform gives them an identity.

    `pricing-core` computes; it does not allocate ids or know about rows. The backend wraps
    this in the persisted `Diagnostics` artifact.
    """

    universal: UniversalDiagnostics
    complexity: ComplexityDiagnostic
    glm: GlmDiagnostics | None = None


def _weighting(spec: GlmSpec) -> Weighting:
    """What the metrics are weighted by, decided once (FR-MODEL-55).

    Exposure when the model carries an exposure offset — every frequency and burning-cost
    model. Claim count when a weight column is declared, which is severity's convention
    (`CLAUDE.md` §7). Otherwise the rows themselves, said plainly rather than implied.
    """
    if spec.offset.kind in {"log_column", "column"}:
        return Weighting.EXPOSURE
    if spec.weight.kind == "column":
        return Weighting.CLAIM_COUNT
    return Weighting.COUNT


def _weights(spec: GlmSpec, data: pl.DataFrame) -> npt.NDArray[np.float64]:
    """The per-row weight the chosen scheme implies."""
    if spec.offset.kind in {"log_column", "column"} and str(spec.offset.column) in data.columns:
        return data[str(spec.offset.column)].cast(pl.Float64).to_numpy()
    if spec.weight.kind == "column" and str(spec.weight.column) in data.columns:
        return data[str(spec.weight.column)].cast(pl.Float64).to_numpy()
    return np.ones(data.height, dtype=np.float64)


def unit_deviance(
    y: npt.NDArray[np.float64],
    mu: npt.NDArray[np.float64],
    *,
    family: str,
    power: float = 1.5,
) -> npt.NDArray[np.float64]:
    """Each row's contribution to the deviance, `2·(L(yᵢ;yᵢ) - L(yᵢ;μᵢ))`.

    Per row rather than summed because the residual plots need exactly this, and computing
    it twice — once vectorised for the total and once in a loop for the residuals — is how
    the two quantities drift apart.

    Spelled out per family rather than taken from the fitting library, for the reason
    `predict` gives: a reviewer must be able to check the arithmetic against a textbook,
    and `02` §4.3's grouping evidence already depends on this being a real
    likelihood-ratio quantity rather than an approximation.

    `y·log(y/μ)` is taken as 0 at `y = 0`, which is its limit — the standard convention,
    and the difference between a deviance and a `nan` on any book with claim-free rows.
    """
    eps = np.finfo(np.float64).tiny
    safe_mu = np.maximum(mu, eps)

    if family in {"poisson", "negative_binomial"}:
        ratio = np.where(y > 0, y * np.log(np.maximum(y, eps) / safe_mu), 0.0)
        return 2.0 * (ratio - (y - mu))
    if family == "gamma":
        return 2.0 * (-np.log(np.maximum(y, eps) / safe_mu) + (y - mu) / safe_mu)
    if family == "gaussian":
        return (y - mu) ** 2
    if family == "inverse_gaussian":
        return np.asarray((y - mu) ** 2 / (np.maximum(y, eps) * safe_mu**2), dtype=np.float64)
    if family == "binomial":
        first = np.where(y > 0, y * np.log(np.maximum(y, eps) / safe_mu), 0.0)
        second = np.where(
            y < 1, (1 - y) * np.log(np.maximum(1 - y, eps) / np.maximum(1 - mu, eps)), 0.0
        )
        return 2.0 * (first + second)
    if family == "tweedie":
        p = power
        return 2.0 * (
            np.power(np.maximum(y, 0.0), 2 - p) / ((1 - p) * (2 - p))
            - y * np.power(safe_mu, 1 - p) / (1 - p)
            + np.power(safe_mu, 2 - p) / (2 - p)
        )

    raise ValueError(f"no deviance implemented for family {family!r}")


def deviance(
    y: npt.NDArray[np.float64],
    mu: npt.NDArray[np.float64],
    *,
    family: str,
    power: float = 1.5,
    weights: npt.NDArray[np.float64] | None = None,
) -> float:
    """The family's total deviance — `unit_deviance` summed, weighted where declared.

    Deviance is non-negative by construction: it is twice the log-likelihood gap between
    the saturated model and this one, and the saturated model cannot be beaten. A fit that
    reproduces its data exactly therefore lands at 0 — and floating-point accumulation puts
    it a few ulps *below* zero, which is how `-4.7e-17` reaches a screen as a deviance.

    Clamped, but only within tolerance. A genuinely negative total means the unit deviance
    for that family is wrong, and silently zeroing it would turn a wrong formula into a
    plausible number — so anything past the tolerance raises instead.
    """
    unit = unit_deviance(y, mu, family=family, power=power)
    total = float(np.sum(unit if weights is None else weights * unit))
    if total >= 0.0:
        return total

    # Scaled to the data: an absolute tolerance means nothing across books whose responses
    # differ by six orders of magnitude.
    tolerance = 1e-9 * max(1.0, float(np.sum(np.abs(unit))))
    if total < -tolerance:
        raise ValueError(
            f"deviance for family {family!r} came out at {total}, negative by more than "
            f"accumulation error ({tolerance:g}). Deviance cannot be negative; this is a "
            "defect in the unit deviance, not a property of the fit."
        )
    return 0.0


def _log_likelihood(
    y: npt.NDArray[np.float64],
    mu: npt.NDArray[np.float64],
    *,
    family: str,
    dispersion: float,
    weights: npt.NDArray[np.float64] | None = None,
) -> float | None:
    """The exact log-likelihood, or `None` where this module does not have one.

    `None` rather than a deviance-based stand-in. AIC differing from another tool's AIC by
    an additive constant is the classic way to make two correct numbers look like a
    disagreement — and Tweedie's density has no closed form at all (it needs a series
    evaluation), so a number produced here would be an approximation reported as a
    likelihood.
    """
    w = np.ones_like(y) if weights is None else weights
    eps = np.finfo(np.float64).tiny

    if family == "poisson":
        from scipy.special import gammaln

        return float(
            np.sum(w * (y * np.log(np.maximum(mu, eps)) - mu - gammaln(y + 1.0)))
        )
    if family == "gaussian":
        n = float(np.sum(w))
        rss = float(np.sum(w * (y - mu) ** 2))
        return -0.5 * (n * math.log(2.0 * math.pi * dispersion) + rss / dispersion)
    if family == "gamma":
        from scipy.special import gammaln

        nu = 1.0 / dispersion
        z = nu * y / mu
        return float(
            np.sum(
                w
                * (
                    nu * np.log(np.maximum(z, eps))
                    - z
                    - np.log(np.maximum(y, eps))
                    - gammaln(nu)
                )
            )
        )
    if family == "binomial":
        return float(
            np.sum(
                w
                * (
                    y * np.log(np.maximum(mu, eps))
                    + (1 - y) * np.log(np.maximum(1 - mu, eps))
                )
            )
        )
    return None


def _gini(
    actual: npt.NDArray[np.float64],
    predicted: npt.NDArray[np.float64],
    exposure: npt.NDArray[np.float64],
) -> tuple[float, float]:
    """Exposure-weighted Gini, and its share of the achievable maximum.

    Ordered by predicted **rate** rather than predicted amount: on a book with varying
    exposure the two orderings differ, and the amount ordering rewards a model for
    knowing which policies are long rather than which are risky.

    The normalised figure divides by the Gini of a perfect ordering on the same data —
    which is what makes it comparable between two books, and is the number `02` §3.8 means
    by "normalised Gini".
    """
    total_actual = float(np.sum(actual))
    total_exposure = float(np.sum(exposure))
    if total_actual <= 0 or total_exposure <= 0:
        return 0.0, 0.0

    def _coefficient(order_key: npt.NDArray[np.float64]) -> float:
        order = np.argsort(order_key, kind="stable")
        x = np.cumsum(exposure[order]) / total_exposure
        y = np.cumsum(actual[order]) / total_actual
        # Trapezoidal area under the Lorenz curve, with the origin included.
        area = float(np.trapezoid(np.concatenate([[0.0], y]), np.concatenate([[0.0], x])))
        return 1.0 - 2.0 * area

    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(exposure > 0, predicted / exposure, 0.0)
        oracle = np.where(exposure > 0, actual / exposure, 0.0)

    model = _coefficient(rate)
    perfect = _coefficient(oracle)
    return model, (model / perfect if perfect > 0 else 0.0)


def _bin_index(values: npt.NDArray[np.float64], bins: int) -> npt.NDArray[np.int64]:
    """Equal-count bins of `values`, 1-based.

    By rank rather than by value: a predicted-rate distribution with a long tail puts
    almost every row in one value-width bin, and a decile chart with nine empty bins is
    not a decile chart.
    """
    n = values.size
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    order = np.argsort(values, kind="stable")
    ranks = np.empty(n, dtype=np.int64)
    ranks[order] = np.arange(n)
    return np.minimum(ranks * bins // n, bins - 1) + 1


def _partition(
    data: pl.DataFrame,
    spec: GlmSpec,
    fit: GlmFitResult,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> PartitionDiagnostics:
    """Every universal metric for one partition (FR-MODEL-50)."""
    y = data[spec.response_column].cast(pl.Float64).to_numpy()
    mu = predict_glm(fit, data, factors, spec, bandings=bandings, groupings=groupings)
    exposure = _weights(spec, data)
    scheme = _weighting(spec)

    expected_total = float(np.sum(mu))
    actual_total = float(np.sum(y))
    ae_overall = actual_total / expected_total if expected_total > 0 else 0.0

    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    cells: list[AeCell] = []
    for slug, column in matrix.terms.items():
        if column not in matrix.categorical:
            continue
        levels = matrix.frame[column].cast(pl.String)
        for level in sorted({v for v in levels.unique().to_list() if v is not None}):
            mask = (levels == level).to_numpy()
            actual = float(np.sum(y[mask]))
            expected = float(np.sum(mu[mask]))
            if expected <= 0:
                continue
            ratio = actual / expected
            # The interval is on the ratio, treating the claim count as the only random
            # quantity — the standard actuarial A/E interval. With no claims in the cell
            # there is nothing to build one from, and a zero-width interval would read as
            # certainty rather than absence.
            half = _NORMAL_975 * math.sqrt(actual) / expected if actual > 0 else None
            cells.append(
                AeCell(
                    factor=slug,
                    level=level,
                    actual=actual,
                    expected=expected,
                    ae=ratio,
                    ci_95=(ratio - half, ratio + half) if half is not None else None,
                    exposure_years=Decimal(str(round(float(np.sum(exposure[mask])), 6))),
                )
            )

    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(exposure > 0, mu / exposure, 0.0)
    bins = _bin_index(rate, _BINS)

    lift: list[LiftBin] = []
    calibration: list[CalibrationBin] = []
    for b in range(1, _BINS + 1):
        mask = bins == b
        rows = int(np.count_nonzero(mask))
        if rows == 0:
            continue
        bin_exposure = float(np.sum(exposure[mask]))
        predicted_mean = float(np.sum(mu[mask])) / bin_exposure if bin_exposure > 0 else 0.0
        actual_mean = float(np.sum(y[mask])) / bin_exposure if bin_exposure > 0 else 0.0
        lift.append(
            LiftBin(
                bin=b,
                rows=rows,
                predicted=predicted_mean,
                actual=actual_mean,
                exposure_years=Decimal(str(round(bin_exposure, 6))),
            )
        )
        calibration.append(
            CalibrationBin(bin=b, rows=rows, predicted=predicted_mean, actual=actual_mean)
        )

    power = float(spec.family_params.get("power", 1.5))
    # The signed deviance residual: `sign(y - μ)·√dᵢ`. Clamped at zero before the root
    # because a unit deviance can land at -1e-17 on an exactly-fitted row, and `sqrt` of
    # that is `nan` — one row of which poisons every summary statistic below.
    unit = np.sign(y - mu) * np.sqrt(
        np.maximum(unit_deviance(y, mu, family=spec.family, power=power), 0.0)
    )

    residuals = (
        ResidualSummary(
            mean=float(np.mean(unit)),
            std=float(np.std(unit)),
            minimum=float(np.min(unit)),
            maximum=float(np.max(unit)),
            p01=float(np.percentile(unit, 1)),
            p99=float(np.percentile(unit, 99)),
        )
        if unit.size
        else None
    )

    gini, gini_normalised = _gini(y, mu, exposure)
    return PartitionDiagnostics(
        weighting=scheme,
        rows=data.height,
        ae_overall=ae_overall,
        ae_by_factor=tuple(cells),
        lift=tuple(lift),
        calibration=tuple(calibration),
        gini=gini,
        gini_normalised=gini_normalised,
        residual_summary=residuals,
    )


def _type_iii(
    data: pl.DataFrame,
    spec: GlmSpec,
    factors: Sequence[Factor],
    full_deviance: float,
    *,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> tuple[TypeIIITest, ...]:
    """Drop each factor, refit, and report the deviance it was worth (FR-MODEL-51).

    A likelihood-ratio test, so the p-value means what a reader assumes: `Δdeviance` on
    `Δdf` degrees of freedom is χ². The alternative — a Wald test read off the coefficient
    table — answers a different question for a multi-level factor, and answers it one level
    at a time.

    Refitting is the cost. It is paid once, at fit time, because FR-MODEL-49 says
    diagnostics are computed once and read thereafter.
    """
    from pricing_core.modelling.glm import GlmFitError, fit_glm

    if len(factors) < 2:
        # Dropping the only factor leaves an intercept-only model, which is the null
        # deviance already reported. A "test" of it would restate that number as though it
        # were a comparison.
        return ()

    y = data[spec.response_column].cast(pl.Float64).to_numpy()
    power = float(spec.family_params.get("power", 1.5))

    tests: list[TypeIIITest] = []
    for factor in factors:
        remaining = [f for f in factors if f.id != factor.id]
        reduced_spec = spec.model_copy(update={"factors": tuple(f.id for f in remaining)})
        try:
            reduced = fit_glm(
                data, reduced_spec, remaining, seed=spec.seed,
                bandings=bandings, groupings=groupings,
            )
        except GlmFitError:
            # A reduced model that will not fit says nothing about the factor's
            # contribution; it says the reduced design is degenerate. Reporting a p-value
            # derived from a failed fit would be inventing evidence.
            continue

        # Recomputed from the reduced fit's own predictions rather than read off
        # `GlmFitResult.deviance` — which the spine declared and never populates, so a
        # test that trusted it would silently produce no tests at all.
        reduced_mu = predict_glm(
            reduced, data, remaining, reduced_spec, bandings=bandings, groupings=groupings
        )
        delta = deviance(y, reduced_mu, family=spec.family, power=power) - full_deviance
        df = _term_count(factor, data, bandings, groupings)
        p = float(stats.chi2.sf(max(delta, 0.0), df))
        tests.append(TypeIIITest(factor=factor.slug, deviance_delta=delta, df=df, p_value=p))
    return tuple(tests)


def _term_count(
    factor: Factor,
    data: pl.DataFrame,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> int:
    """Degrees of freedom a factor spends: levels - 1 for a categorical, 1 otherwise."""
    matrix = resolve_factors(data, [factor], bandings=bandings, groupings=groupings)
    column = matrix.terms.get(factor.slug)
    if column is None or column not in matrix.categorical:
        return 1
    return max(1, matrix.frame[column].cast(pl.String).n_unique() - 1)


def compute_diagnostics(
    fit: GlmFitResult,
    spec: GlmSpec,
    factors: Sequence[Factor],
    *,
    train: pl.DataFrame,
    holdout: pl.DataFrame,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    max_factor_count: int | None = None,
    min_exposure_per_parameter: float | None = None,
    type_iii: bool = True,
    progress: ProgressCallback | None = None,
) -> DiagnosticsResult:
    """Everything `02` §3.8 asks of a GLM fit, for both partitions (FR-MODEL-49..55, 81).

    `train` and `holdout` are both required and neither defaults. A caller with only one
    frame is a caller about to report a one-sided diagnostic, and FR-MODEL-54 calls that a
    defect — so the signature refuses it rather than the reviewer having to notice.
    """
    report = progress or NullProgress()
    report.check_cancelled()
    report.update(0.05, "diagnostics: train")
    train_part = _partition(
        train, spec, fit, factors, bandings=bandings, groupings=groupings
    )
    report.check_cancelled()
    report.update(0.35, "diagnostics: holdout")
    holdout_part = _partition(
        holdout, spec, fit, factors, bandings=bandings, groupings=groupings
    )

    report.update(0.55, "diagnostics: deviance and information criteria")
    y = train[spec.response_column].cast(pl.Float64).to_numpy()
    mu = predict_glm(fit, train, factors, spec, bandings=bandings, groupings=groupings)
    power = float(spec.family_params.get("power", 1.5))
    full_deviance = deviance(y, mu, family=spec.family, power=power)
    null_deviance = deviance(
        y, np.full_like(y, float(np.mean(y))), family=spec.family, power=power
    )

    parameters = len(fit.coefficients)
    dispersion = fit.dispersion if fit.dispersion is not None else 1.0
    log_likelihood = _log_likelihood(
        y, mu, family=spec.family, dispersion=dispersion
    )
    aic = -2.0 * log_likelihood + 2.0 * parameters if log_likelihood is not None else None
    bic = (
        -2.0 * log_likelihood + parameters * math.log(max(train.height, 1))
        if log_likelihood is not None
        else None
    )

    tests: tuple[TypeIIITest, ...] = ()
    if type_iii:
        report.check_cancelled()
        report.update(0.70, "diagnostics: type-III tests")
        tests = _type_iii(
            train, spec, factors, full_deviance, bandings=bandings, groupings=groupings
        )

    report.update(0.95, "diagnostics: complexity")
    exposure_total = float(np.sum(_weights(spec, train)))
    claims_total = float(np.sum(y))
    complexity = ComplexityDiagnostic(
        factor_count=len(factors),
        parameter_count=parameters,
        exposure_per_parameter=exposure_total / parameters if parameters else None,
        claims_per_parameter=claims_total / parameters if parameters else None,
        max_factor_count=max_factor_count,
        min_exposure_per_parameter=min_exposure_per_parameter,
    )

    report.update(1.0, "diagnostics complete")
    return DiagnosticsResult(
        universal=UniversalDiagnostics(train=train_part, holdout=holdout_part),
        complexity=complexity,
        glm=GlmDiagnostics(
            deviance=full_deviance,
            null_deviance=null_deviance,
            aic=aic,
            bic=bic,
            dispersion=dispersion,
            degrees_of_freedom=max(train.height - parameters, 0),
            type_iii_tests=tests,
        ),
    )
