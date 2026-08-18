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

import hashlib
import json
import time
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl
from scipy import stats

from model_schema import (
    Banding,
    BlobRef,
    Coefficient,
    Factor,
    GlmFitResult,
    GlmSpec,
    Grouping,
    RelativityLevel,
)
from pricing_core.modelling.factors import FactorMatrix, resolve_factors
from pricing_core.progress import NullProgress, ProgressCallback

__all__ = [
    "COVARIANCE_MEDIA_TYPE",
    "GlmFit",
    "GlmFitError",
    "decode_covariance",
    "encode_covariance",
    "fit_glm",
]

#: The exact two-sided 97.5 % normal quantile. Spelled out because 1.96 is a rounding of
#: it, and a rounded interval is a different interval.
_NORMAL_975 = 1.959963984540054

#: |β| past which a fit is separation rather than an effect. `exp(20)` is 4.9e8 — a
#: relativity no book contains.
_SEPARATION_ETA = 20.0

#: The covariance blob is JSON, for the reason the booster is `xgboost_json` and never a
#: pickle (ADR-0003): a stored artifact must be readable by something that did not fit it.
COVARIANCE_MEDIA_TYPE = "application/json"


class GlmFitError(RuntimeError):
    """A fit that cannot be returned as a result (FR-MODEL-23).

    `code` is the platform error code the API surfaces: `GLM_DID_NOT_CONVERGE`,
    `GLM_RANK_DEFICIENT` or `GLM_SEPARATION_DETECTED`.
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


@dataclass(frozen=True)
class GlmFit:
    """What a GLM fit returns: the artifact, and the covariance bytes it addresses.

    Two values rather than one for the reason `GbmFit` is two — `pricing-core` cannot store
    a blob (ADR-0001) and the artifact cannot hold a `p x p` matrix (`02` §4.8, and the
    field comment on `covariance_blob`). The `BlobRef` inside `result` is already complete,
    because a content-addressed reference is a pure function of the payload, so the caller's
    job is to store `covariance_bytes` under that digest — and a caller that forgets has a
    reference resolving to nothing rather than a model that half exists.

    The GBM arm reached this shape first and this is the GLM arm arriving at it, not a
    second convention: one dataclass per fit, carrying the artifact and the bytes it names.
    """

    result: GlmFitResult
    covariance_bytes: bytes


def encode_covariance(terms: Sequence[str], matrix: npt.NDArray[np.float64]) -> bytes:
    """Serialise `V` with the term order that makes it readable.

    **The term order is stored inside the blob, not merely alongside it.** A covariance
    matrix is positional, and `x'Vx` computed against a design built in a different order
    is a variance for a model nobody fitted — which comes out a plausible positive number,
    so nothing downstream would catch it. Storing the names lets the scorer *assert* the
    order it is about to use, which is what FR-MODEL-71 does for the GBM's `base_margin`
    and for the same reason: the silent failure is the one worth a byte.

    Canonical JSON — sorted keys, no incidental whitespace — because the digest is taken
    over these bytes and two encodings of one matrix must not be two blobs.
    """
    if matrix.shape != (len(terms), len(terms)):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            f"the covariance matrix is {matrix.shape} for {len(terms)} terms. A "
            "non-square matrix, or one that does not match the coefficient vector, cannot "
            "be paired with the terms it is supposed to describe.",
            terms=terms,
        )
    payload = {
        "terms": list(terms),
        "matrix": [[float(value) for value in row] for row in matrix],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def decode_covariance(
    payload: bytes, terms: Sequence[str]
) -> npt.NDArray[np.float64]:
    """Read `V` back, **refusing** a blob whose term order is not the one asked for.

    The check is the reason this is a named function rather than a `json.loads`. A stored
    covariance matrix is positional: pair it with a design built in a different order and
    `x'Vx` is the variance of a linear combination nobody estimated. That comes out a
    plausible positive number, so no downstream assertion catches it and the interval is
    simply wrong — the failure mode FR-MODEL-71 guards for the GBM's `base_margin`, in the
    other direction.

    `terms` is the caller's expected order, intercept first, as `encode_covariance` wrote it.
    """
    try:
        document = json.loads(payload)
        stored = list(document["terms"])
        matrix = np.asarray(document["matrix"], dtype=np.float64)
    except (ValueError, KeyError, TypeError) as exc:
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "the covariance blob is not a covariance matrix this module wrote: "
            f"{exc}. An interval cannot be derived from it.",
            terms=terms,
        ) from exc
    if stored != list(terms):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "the covariance blob was written for a different set of terms than the "
            "coefficients it is being paired with. Using it positionally would report the "
            "variance of a linear combination that was never estimated, which reads as a "
            "valid interval.",
            terms=terms,
        )
    if matrix.shape != (len(stored), len(stored)):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            f"the covariance blob holds a {matrix.shape} matrix for {len(stored)} terms.",
            terms=terms,
        )
    return matrix


def _covariance_ref(payload: bytes) -> BlobRef:
    """The complete reference, computed here so the caller only has to store the bytes."""
    return BlobRef(
        sha256=hashlib.sha256(payload).hexdigest(),
        bytes=len(payload),
        media_type=COVARIANCE_MEDIA_TYPE,
    )


def _levels(series: pl.Series, exposure: pl.Series | None) -> list[str]:
    """A factor's levels, **base first**, chosen by `largest_exposure` (`02` §4.1).

    The base was "first alphabetically", which the schema's own `base_level_method` says it
    is not. It matters beyond tidiness: every other level's relativity is expressed against
    the base, so a base holding 5 % of the exposure gives every relativity the standard
    error of a thin cell. With no exposure column the largest **count** is the same idea
    with the only weight available.

    `cast(pl.String)` throughout rather than Python's `str()`: polars renders a boolean as
    `"true"`, `str(True)` gives `"True"`, and the two never matched — a boolean factor
    produced an all-zero dummy and was then reported as collinear.
    """
    text = series.cast(pl.String)
    observed = [v for v in text.unique().sort().to_list() if v is not None]
    if not observed:
        return []

    weights: dict[str, float] = {}
    for level in observed:
        mask = text == level
        weights[level] = (
            float(exposure.cast(pl.Float64).filter(mask).sum())
            if exposure is not None
            else float(mask.sum())
        )
    base = max(observed, key=lambda level: (weights[level], level))
    return [base, *[level for level in observed if level != base]]


def _design(
    matrix: FactorMatrix, exposure: pl.Series | None
) -> tuple[pl.DataFrame, dict[str, list[str]]]:
    """One-hot the categoricals, base level excluded, and keep the mapping.

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
            observed = _levels(series, exposure)
            levels[slug] = observed
            text = series.cast(pl.String)
            for level in observed[1:]:  # index 0 is the base
                columns[f"{slug}[{level}]"] = (text == level).cast(pl.Float64)
        else:
            columns[slug] = series.cast(pl.Float64)

    return pl.DataFrame(columns), levels


def fit_glm(
    data: pl.DataFrame,
    spec: GlmSpec,
    factors: Sequence[Factor],
    *,
    seed: int = 0,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    progress: ProgressCallback | None = None,
) -> GlmFit:
    """Fit `spec` over `data`, returning data rather than an estimator.

    `factors`, `bandings` and `groupings` are passed explicitly rather than read from the
    spec's ids: `pricing-core` resolves shapes, not references — looking one up would need
    a database, which ADR-0001 forbids this package.

    `progress` is `00` §5.5's injected callback. It was dropped from this signature during
    the spine and a long fit then sat at one fraction for its whole duration, which is the
    failure FR-PLAT-8 exists to prevent. The stages are the four that actually take time,
    reported before each rather than after, so the label names what is happening now.
    """
    from glum import GeneralizedLinearRegressor, TweedieLink  # type: ignore[import-untyped]

    report = progress or NullProgress()
    report.check_cancelled()
    report.update(0.05, "resolving factors")
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    exposure_series = (
        data[str(spec.offset.column)]
        if spec.offset.kind == "log_column" and spec.offset.column in data.columns
        else None
    )
    report.update(0.15, "building the design matrix")
    design, levels = _design(matrix, exposure_series)
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

    # `glum` takes the power **positionally**: `tweedie(1.5)`. Written `tweedie(p=1.5)` it
    # parses the power by calling `float("p=1.5")`, so every burning cost fit raised a bare
    # `ValueError` from inside the library — not even a named `GlmFitError`, and the whole
    # family was dead. The range is `GlmSpec`'s to check: it is a fact about the spec.
    family: str = spec.family
    if family == "tweedie":
        family = f"tweedie({float(spec.family_params.get('power', 1.5))})"

    # `glum` has no `"inverse"` spelling. Its link vocabulary is identity/log/logit/cloglog/
    # tweedie, and the string reaches `fit` unrecognised and raises a bare `ValueError` from
    # inside the library. The link is not missing, only unnamed: `TweedieLink(p)` is
    # `mu**(1-p)`, so `TweedieLink(2)` **is** `1/mu`. FR-MODEL-18 declares `inverse`
    # supported and `GlmSpec.link` accepts it, and `predict._inverse_link` has always
    # implemented it — the gap was here, in the translation, and it killed every Gamma fit
    # on the canonical link at `estimator.fit`.
    link: Any = TweedieLink(2) if spec.link == "inverse" else spec.link

    estimator = GeneralizedLinearRegressor(
        family=family,
        link=link,
        alpha=spec.alpha,
        l1_ratio=spec.l1_ratio,
        max_iter=spec.max_iter,
        gradient_tol=spec.tolerance,
        fit_intercept=True,
    )

    report.check_cancelled()
    report.update(0.30, f"fitting {spec.family} over {data.height:,} rows", terms=design.width)
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

    report.update(0.80, "standard errors and intervals")
    covariance = _covariance(
        estimator, design.columns, x, response, offset=offset, weights=weights
    )
    coefficients = _coefficients(estimator, design.columns, covariance, link=spec.link)
    _refuse_separation(coefficients)
    report.update(0.95, "relativity tables")
    relativities = _relativities(matrix, levels, coefficients, spec, link=spec.link)

    covariance_bytes = encode_covariance(["intercept", *design.columns], covariance)

    report.update(1.0, "fitted")
    return GlmFit(
        result=GlmFitResult(
            converged=True,
            iterations=int(getattr(estimator, "n_iter_", 0) or 0),
            fit_seconds=round(elapsed, 3),
            coefficients=coefficients,
            relativities=relativities,
            dispersion=_dispersion(estimator, x, response, weights=weights, offset=offset),
            deviance=None,
            rows=data.height,
            library_versions=_versions(),
            covariance_blob=_covariance_ref(covariance_bytes),
        ),
        covariance_bytes=covariance_bytes,
    )


def _covariance(
    estimator: Any,
    terms: Sequence[str],
    x: np.ndarray,
    y: np.ndarray,
    *,
    offset: np.ndarray | None,
    weights: np.ndarray | None,
) -> npt.NDArray[np.float64]:
    """`V`, the coefficient covariance matrix — FR-MODEL-21's errors and FR-MODEL-63's.

    **This replaced a call to `estimator.std_errors()`, and costs nothing extra.** glum's
    `std_errors` is defined as `sqrt(covariance_matrix(...).diagonal())` — verified against
    the installed source, not assumed — so the matrix was already being computed on every
    fit and everything off the diagonal thrown away. FR-MODEL-63's interval needs
    `x'Vx`, which is off-diagonal: `Var(sum b_j x_j)` is not the sum of the coefficient
    variances unless the estimates are independent, which for a design with a shared
    intercept they never are. Keeping what was already computed is the whole change.

    `robust=False` is explicit because **glum's default is `True`** — the HC-1 sandwich.
    That is a defensible estimator and a different one, and FR-MODEL-21 asks for the
    model-based standard error that pairs with the z and p-value beside it.

    The ordering is glum's: index 0 is the intercept, then the design columns in order.
    Verified rather than assumed — a column with a hundredth of the variance of its
    neighbour carries the correspondingly larger standard error at the expected index.
    """
    names = ["intercept", *terms]
    try:
        matrix = np.asarray(
            estimator.covariance_matrix(
                x, y, sample_weight=weights, offset=offset, robust=False
            ),
            dtype=np.float64,
        )
    except (np.linalg.LinAlgError, ValueError) as exc:
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "the coefficient covariance matrix could not be computed: the information "
            "matrix is singular, so two or more terms are collinear and their coefficients "
            "are not separately identified.",
            terms=names,
        ) from exc
    if matrix.shape != (len(names), len(names)):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            f"the estimator returned a {matrix.shape} covariance matrix for {len(names)} "
            "coefficients. Pairing it with the terms by position would attach a variance "
            "to the wrong term, which is worse than reporting none.",
            terms=names,
        )
    return matrix


def _coefficients(
    estimator: Any,
    terms: Sequence[str],
    covariance: npt.NDArray[np.float64],
    *,
    link: str,
) -> tuple[Coefficient, ...]:
    """Estimates with the uncertainty `02` R5 makes non-optional.

    **The standard errors come from `glum`**, as the diagonal of the matrix `_covariance`
    obtained from it. They used to be computed here from a working weight derived from the
    *link* — `W = mu` for a log link, `1` otherwise — which is the Fisher information for
    Poisson and for nothing else. It ignores the family's variance function and the
    dispersion φ, so a Gamma severity model over amounts in minor units reported intervals
    roughly **forty-eight times too narrow**: a nominal 95 % interval with measured
    coverage of 7 %. `02` §8 had already recorded that glum's `std_errors()` was "verified
    to exist, not assumed"; this hand-rolled a replacement for a verified path and got it
    wrong for every family the spec supports except one.
    """
    coef = np.asarray(estimator.coef_, dtype=np.float64)
    intercept = float(getattr(estimator, "intercept_", 0.0))
    beta = np.concatenate([[intercept], coef])
    names = ["intercept", *terms]

    variances = covariance.diagonal()
    if np.any(variances < 0):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "a coefficient has a negative variance on the diagonal of the covariance "
            "matrix, which is not a covariance matrix. Reported rather than square-rooted "
            "into a NaN standard error that would read as an unidentified term.",
            terms=[name for name, v in zip(names, variances, strict=True) if v < 0],
        )
    std_errors = np.sqrt(variances)

    if len(std_errors) != len(beta):
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            f"the estimator returned {len(std_errors)} standard errors for {len(beta)} "
            "coefficients. Pairing them by position would attach an interval to the wrong "
            "term, which is worse than reporting none.",
            terms=names,
        )

    unidentified = [
        name
        for name, error in zip(names, std_errors, strict=True)
        if not np.isfinite(error) or error < 0
    ]
    if unidentified:
        raise GlmFitError(
            "GLM_RANK_DEFICIENT",
            "a coefficient has no finite standard error, which means the fit did not "
            "identify it. Reported rather than returned as an estimate with no uncertainty "
            "(`02` R5).",
            terms=unidentified,
        )

    out: list[Coefficient] = []
    for name, estimate, std_error in zip(names, beta, std_errors, strict=True):
        error = float(std_error)
        z = float(estimate / error) if error > 0 else 0.0
        p_value = float(2.0 * stats.norm.sf(abs(z)))
        half = _NORMAL_975 * error
        out.append(
            Coefficient(
                term=name,
                estimate=float(estimate),
                std_error=error,
                z=z,
                p_value=min(max(p_value, 0.0), 1.0),
                ci_95=(float(estimate - half), float(estimate + half)),
                # A relativity is `exp(β)`, which is a reading of a **multiplicative**
                # model. Under `logit` or `identity` the level's effect is additive on the
                # link scale and there is no relativity to report.
                relativity=float(np.exp(estimate)) if link == "log" else None,
            )
        )
    return tuple(out)


def _refuse_separation(coefficients: Sequence[Coefficient]) -> None:
    """FR-MODEL-23 names separation; nothing detected it.

    A perfectly separated logit returned `converged=True` with a coefficient of **640** and
    p=0 — a degenerate fit presented as a result, which is the failure the requirement
    exists to forbid. The threshold is on the linear predictor: `exp(20)` is 4.9 x 10⁸, a
    relativity no book contains, so a coefficient past it is a boundary the optimiser walked
    to rather than an effect the data supports.
    """
    extreme = [c.term for c in coefficients if abs(c.estimate) > _SEPARATION_ETA]
    if extreme:
        raise GlmFitError(
            "GLM_SEPARATION_DETECTED",
            f"{', '.join(extreme)} reached |β| > {_SEPARATION_ETA}, which means the "
            "response is perfectly (or nearly perfectly) predicted by those terms and the "
            "likelihood has no interior maximum. The estimate is where the optimiser "
            "stopped, not an effect size — drop the term, merge the level, or penalise.",
            terms=extreme,
        )


def _dispersion(
    estimator: Any,
    x: np.ndarray,
    y: np.ndarray,
    *,
    weights: np.ndarray | None,
    offset: np.ndarray | None,
) -> float | None:
    """The scale parameter φ, where the family has one to estimate.

    Poisson and binomial fix it at 1; Gamma, Gaussian, inverse-Gaussian and Tweedie do not,
    and it is the factor the old standard errors were missing. Persisted because `02` §4.8
    carries it in the Model artifact, and because a reader cannot tell a Gamma fit's
    intervals from a Poisson's without it.
    """
    try:
        value = float(
            estimator.family_instance.dispersion(
                y,
                estimator.predict(x, offset=offset),
                sample_weight=weights,
            )
        )
    except Exception:  # an estimate the family cannot supply is reported as absent
        return None
    return value if np.isfinite(value) else None


def _relativities(
    matrix: FactorMatrix,
    levels: dict[str, list[str]],
    coefficients: Sequence[Coefficient],
    spec: GlmSpec,
    *,
    link: str,
) -> dict[str, tuple[RelativityLevel, ...]]:
    """The table an actuary reads: one row per level, base marked (FR-MODEL-21).

    The base carries relativity 1.0 by construction — it is what everything else is
    expressed against, and showing it blank is how a reader ends up thinking a factor has
    one fewer level than it has.

    **Only under a multiplicative link.** A missing coefficient used to fall back to 1.0,
    and `Coefficient.relativity` is `None` for any non-log link — so a logit model produced
    a table of 1.0s for a factor spanning eighteen log-odds, reported as no effect
    anywhere. Now the estimate is carried instead and the relativity left absent, which is
    the true statement.
    """
    by_term = {c.term: c for c in coefficients}
    exposure_column = spec.offset.column if spec.offset.kind == "log_column" else None
    # The **resolved** frame, not the caller's. A banding contributes a column that exists
    # only after resolution, and grouping the raw frame by it raises — or, worse, groups by
    # the pre-banding column and reports exposure against the wrong levels.
    data = matrix.frame

    tables: dict[str, tuple[RelativityLevel, ...]] = {}
    for slug, observed in levels.items():
        if not observed:
            continue
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
                level=observed[0],
                relativity=1.0 if link == "log" else None,
                estimate=0.0,
                is_base=True,
                exposure=exposures.get(observed[0]),
            )
        ]
        for level in observed[1:]:
            coefficient = by_term.get(f"{slug}[{level}]")
            rows.append(
                RelativityLevel(
                    level=level,
                    relativity=coefficient.relativity if coefficient else None,
                    estimate=coefficient.estimate if coefficient else None,
                    is_base=False,
                    exposure=exposures.get(level),
                )
            )
        tables[slug] = tuple(rows)
    return tables


def _versions() -> dict[str, str]:
    import glum

    return {"glum": glum.__version__, "polars": pl.__version__}
