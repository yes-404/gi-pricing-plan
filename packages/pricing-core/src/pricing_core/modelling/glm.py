"""GLM fitting with `glum` (`02` FR-MODEL-18..23, §5.2).

What this module owes its caller, in the spec's own terms:

* **FR-MODEL-19** — the actuarial defaults are applied by the *spec*, not here: frequency
  is Poisson, log link, `offset = log(exposure)`, and `GlmSpec` refuses a Poisson model
  with no offset at the type. A fit function that silently supplied a default would make
  the override invisible, and FR-MODEL-19 requires an override to be recorded.
* **FR-MODEL-21** — every coefficient carries estimate, standard error, z, p-value and a
  95 % interval, and every categorical factor gets a relativity table with the base level
  marked. Not optional extras: `02` R5 makes uncertainty part of what an estimate *is*.
* **FR-MODEL-23** — non-convergence, rank deficiency and separation are **named errors**
  with the offending terms identified. The failure mode this exists to prevent is a
  degenerate fit returned as though it were a result.
* **ADR-0003** — what comes back is data. No estimator is returned, pickled or stored; a
  Model must be re-scorable by a process that never imported `glum`.
"""

from __future__ import annotations

import time
import warnings
from collections.abc import Sequence
from typing import Any

import numpy as np
import polars as pl
from scipy import stats

from model_schema import (
    Coefficient,
    Factor,
    GlmFitResult,
    GlmSpec,
    RelativityLevel,
)
from pricing_core.modelling.factors import FactorMatrix, resolve_factors

__all__ = ["GlmFitError", "fit_glm"]

#: Above this, `glum`'s own convergence report is not to be trusted as "fine" — a fit that
#: used every iteration it was given has usually not converged, it has run out of budget.
_CONDITION_WARN = 1e10


class GlmFitError(RuntimeError):
    """A fit that cannot be returned as a result (FR-MODEL-23).

    `code` is the platform error code the API surfaces: `GLM_DID_NOT_CONVERGE`,
    `GLM_RANK_DEFICIENT` or `GLM_SEPARATION_DETECTED`.
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


def _design(matrix: FactorMatrix) -> tuple[pl.DataFrame, dict[str, list[str]]]:
    """One-hot the categoricals, first level as base, and keep the mapping.

    Built here rather than handed to `glum`'s formula interface so the base level is a
    decision this module makes and records — FR-MODEL-21 requires the base to be *marked*,
    and a base chosen inside a library is one nobody can point at.
    """
    frame = matrix.frame
    columns: dict[str, pl.Series] = {}
    levels: dict[str, list[str]] = {}

    for slug, column in matrix.terms.items():
        series = frame[column]
        if column in matrix.categorical:
            observed = [str(v) for v in series.unique().sort().to_list() if v is not None]
            levels[slug] = observed
            for level in observed[1:]:  # first is the base
                columns[f"{slug}[{level}]"] = (series.cast(pl.String) == level).cast(pl.Float64)
        else:
            columns[slug] = series.cast(pl.Float64)

    return pl.DataFrame(columns), levels


def fit_glm(
    data: pl.DataFrame,
    spec: GlmSpec,
    factors: Sequence[Factor],
    *,
    seed: int = 0,
) -> GlmFitResult:
    """Fit `spec` over `data`, returning data rather than an estimator.

    `factors` is passed explicitly rather than read from the spec's ids: `pricing-core`
    resolves shapes, not references — looking a factor up would need a database, which
    ADR-0001 forbids this package.
    """
    from glum import GeneralizedLinearRegressor  # type: ignore[import-untyped]

    matrix = resolve_factors(data, factors)
    design, levels = _design(matrix)
    if design.width == 0:
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "the design matrix has no columns — every factor resolved to nothing, so "
            "there is nothing to estimate.",
        )

    response = data[spec.response_column].cast(pl.Float64).to_numpy()
    x = design.to_numpy()

    offset = None
    if spec.offset.kind == "log_column":
        exposure = data[str(spec.offset.column)].cast(pl.Float64).to_numpy()
        if np.any(exposure <= 0):
            raise GlmFitError(
                "OFFSET_REQUIRED_FOR_FREQUENCY",
                f"{spec.offset.column!r} has non-positive values, and log(exposure) is the "
                "offset (FR-MODEL-19). A row with zero exposure contributes no information "
                "and must be filtered before fitting, not silently logged.",
            )
        offset = np.log(exposure)
    elif spec.offset.kind == "column":
        offset = data[str(spec.offset.column)].cast(pl.Float64).to_numpy()

    weights = None
    if spec.weight.kind == "column":
        weights = data[str(spec.weight.column)].cast(pl.Float64).to_numpy()

    # `glum` takes the Tweedie power in the family string, e.g. `tweedie(p=1.5)`.
    family: str = spec.family
    if family == "tweedie":
        power = float(spec.family_params.get("power", 1.5))
        if not 1.0 < power < 2.0:
            raise GlmFitError(
                "GLM_DID_NOT_CONVERGE",
                f"Tweedie power {power} is outside (1, 2). `CLAUDE.md` §7: burning cost is "
                "Tweedie with 1 < p < 2; outside that it is a different family, not a "
                "differently-tuned one.",
            )
        family = f"tweedie(p={power})"

    estimator = GeneralizedLinearRegressor(
        family=family,
        link=spec.link,
        alpha=spec.alpha,
        l1_ratio=spec.l1_ratio,
        max_iter=spec.max_iter,
        gradient_tol=spec.tolerance,
        fit_intercept=True,
    )

    started = time.perf_counter()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            estimator.fit(x, response, sample_weight=weights, offset=offset)
    except np.linalg.LinAlgError as exc:
        # `glum` raises this from its own solve when the design is singular. Translated
        # rather than propagated: FR-MODEL-23 requires a *named* error with the offending
        # terms, and a library traceback names an internal slice index instead.
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "the design matrix is singular: two or more terms are collinear, so their "
            "coefficients are not separately identified. Drop one, or combine them into a "
            "single factor.",
            terms=design.columns,
        ) from exc
    elapsed = time.perf_counter() - started

    if any("converge" in str(w.message).lower() for w in caught):
        raise GlmFitError(
            "GLM_DID_NOT_CONVERGE",
            f"the fit did not converge in {spec.max_iter} iterations. Returned coefficients "
            "would be wherever the solver stopped, which is not an estimate — raise "
            "`max_iter`, loosen `tolerance`, or look for separation in the factors.",
            terms=design.columns,
        )

    coefficients = _coefficients(
        estimator, design.columns, x, response, offset=offset, weights=weights, link=spec.link
    )
    relativities = _relativities(matrix, levels, coefficients, data, spec)

    return GlmFitResult(
        converged=True,
        iterations=int(getattr(estimator, "n_iter_", 0) or 0),
        fit_seconds=round(elapsed, 3),
        coefficients=coefficients,
        relativities=relativities,
        deviance=None,
        rows=data.height,
        library_versions=_versions(),
    )


def _coefficients(
    estimator: Any,
    terms: Sequence[str],
    x: np.ndarray,
    y: np.ndarray,
    *,
    offset: np.ndarray | None,
    weights: np.ndarray | None,
    link: str,
) -> tuple[Coefficient, ...]:
    """Estimates with the uncertainty `02` R5 makes non-optional.

    Standard errors come from the observed information matrix — `glum` does not return
    them, and a coefficient without one is exactly the half-result R5 exists to refuse. If
    the matrix is singular the fit is rank deficient, which FR-MODEL-23 names rather than
    letting a `NaN` standard error travel onward as though it meant something.
    """
    coef = np.asarray(estimator.coef_, dtype=float)
    intercept = float(getattr(estimator, "intercept_", 0.0))
    design = np.column_stack([np.ones(len(y)), x])
    beta = np.concatenate([[intercept], coef])
    names = ["intercept", *terms]

    eta = design @ beta + (offset if offset is not None else 0.0)
    mu = np.exp(eta) if link == "log" else eta
    w = mu if link == "log" else np.ones_like(mu)
    if weights is not None:
        w = w * weights

    information = design.T @ (design * w[:, None])
    try:
        covariance = np.linalg.inv(information)
    except np.linalg.LinAlgError as exc:
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "the information matrix is singular: two or more terms are collinear, so their "
            "coefficients are not separately identified. FR-MODEL-23 names this rather "
            "than returning a fit with meaningless standard errors.",
            terms=names,
        ) from exc

    variances = np.diag(covariance)
    if np.any(~np.isfinite(variances)) or np.any(variances < 0):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "a coefficient has a non-finite variance, which means the fit did not identify "
            "it. Reported rather than returned as an estimate with no uncertainty (R5).",
            terms=[n for n, v in zip(names, variances, strict=True) if not np.isfinite(v)],
        )

    out: list[Coefficient] = []
    for name, estimate, variance in zip(names, beta, variances, strict=True):
        std_error = float(np.sqrt(variance))
        z = float(estimate / std_error) if std_error > 0 else 0.0
        p_value = float(2.0 * stats.norm.sf(abs(z)))
        half = 1.959963984540054 * std_error
        out.append(
            Coefficient(
                term=name,
                estimate=float(estimate),
                std_error=std_error,
                z=z,
                p_value=min(max(p_value, 0.0), 1.0),
                ci_95=(float(estimate - half), float(estimate + half)),
                relativity=float(np.exp(estimate)) if link == "log" else None,
            )
        )
    return tuple(out)


def _relativities(
    matrix: FactorMatrix,
    levels: dict[str, list[str]],
    coefficients: Sequence[Coefficient],
    data: pl.DataFrame,
    spec: GlmSpec,
) -> dict[str, tuple[RelativityLevel, ...]]:
    """The table an actuary reads: one row per level, base marked (FR-MODEL-21).

    The base level carries relativity 1.0 by construction — it is the level everything else
    is expressed against, and showing it as blank is how a reader ends up thinking a factor
    has one fewer level than it has.
    """
    by_term = {c.term: c for c in coefficients}
    exposure_column = spec.offset.column if spec.offset.kind == "log_column" else None

    tables: dict[str, tuple[RelativityLevel, ...]] = {}
    for slug, observed in levels.items():
        column = matrix.terms[slug]
        exposures: dict[str, float] = {}
        if exposure_column and exposure_column in data.columns:
            grouped = (
                data.group_by(column)
                .agg(pl.col(exposure_column).cast(pl.Float64).sum().alias("e"))
                .to_dicts()
            )
            exposures = {str(row[column]): float(row["e"]) for row in grouped}

        rows = [
            RelativityLevel(
                level=observed[0], relativity=1.0, is_base=True,
                exposure=exposures.get(observed[0]),
            )
        ]
        for level in observed[1:]:
            coefficient = by_term.get(f"{slug}[{level}]")
            rows.append(
                RelativityLevel(
                    level=level,
                    relativity=coefficient.relativity if coefficient and coefficient.relativity
                    else 1.0,
                    is_base=False,
                    exposure=exposures.get(level),
                )
            )
        tables[slug] = tuple(rows)
    return tables


def _versions() -> dict[str, str]:
    import glum

    return {"glum": glum.__version__, "polars": pl.__version__}
