"""Scoring a fitted GLM from its artifact alone (`02` FR-MODEL-62, ADR-0003).

The point of this module is what it does **not** import. `glum` fits; nothing here needs
it. A Model is a set of named coefficients, and scoring is rebuilding the design columns
those names describe and taking a dot product — which a process that never ran the fitting
library can do, which is the whole of ADR-0003.

The term naming is the contract between `glm._design` and this module: a categorical
contributes `slug[level]` for every level except the base, and a continuous factor
contributes `slug`. A term this module cannot parse is an error rather than a zero,
because a coefficient silently dropped is a prediction that looks fine and is wrong.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping, Sequence
from statistics import NormalDist
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl

from model_schema import (
    Banding,
    Coefficient,
    Factor,
    FitResult,
    GbmFitResult,
    GlmFitResult,
    GlmSpec,
    Grouping,
    ModelSpec,
)
from pricing_core.modelling.factors import resolve_factors

__all__ = [
    "PredictionError",
    "detect_quantile_crossing",
    "linear_predictor",
    "predict_glm",
    "predict_glm_interval",
    "score_fitted",
]

#: `slug[level]` — the shape `glm._design` writes for a categorical dummy.
_DUMMY = re.compile(r"^(?P<slug>.+)\[(?P<level>.*)\]$")


class PredictionError(RuntimeError):
    """A model that cannot be scored against this frame.

    Distinct from a fit error: the model is fine, the data it was pointed at is not.
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


def _inverse_link(eta: npt.NDArray[np.float64], link: str) -> npt.NDArray[np.float64]:
    """`g⁻¹`, the only place the link is inverted.

    Written out rather than taken from the fitting library so that scoring and fitting
    cannot drift apart — and so that a reader can check the arithmetic against the spec
    without installing `glum`.
    """
    if link == "log":
        return np.exp(eta)
    if link == "identity":
        return eta
    if link == "logit":
        return 1.0 / (1.0 + np.exp(-eta))
    if link == "inverse":
        with np.errstate(divide="ignore"):
            return 1.0 / eta
    raise PredictionError(
        "MODEL_LINK_UNSUPPORTED",
        f"link {link!r} has no inverse in this module. A prediction cannot be produced "
        "from a link the scorer does not implement, and guessing would be a price.",
    )


def _term_vectors(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> Iterator[tuple[Coefficient, npt.NDArray[np.float64]]]:
    """One column of `X` per coefficient, **in coefficient order**, intercept included.

    Extracted so that `linear_predictor` and `predict_glm_interval` cannot build different
    design matrices from the same model: `η̂` and `x'Vx` are the centre and the width of one
    interval, and a term resolved one way for the first and another way for the second
    produces a width that does not belong to the centre it is drawn around.

    A generator rather than a matrix because the accumulating caller is the hot one — the
    backtest scores the full dataset, and materialising `n x p` there would be hundreds of
    megabytes to compute a dot product that needs one column at a time.
    """
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)

    for coefficient in fit.coefficients:
        term = coefficient.term
        if term == "intercept":
            yield coefficient, np.ones(data.height, dtype=np.float64)
            continue

        match = _DUMMY.match(term)
        if match is not None:
            slug, level = match.group("slug"), match.group("level")
            column = matrix.terms.get(slug)
            if column is None:
                raise PredictionError(
                    "MODEL_TERM_UNRESOLVED",
                    f"term {term!r} names factor {slug!r}, which this frame does not "
                    "resolve. Scoring with the term dropped would silently move every "
                    "prediction toward the base level.",
                    terms=[term],
                )
            indicator = (matrix.frame[column].cast(pl.String) == level).cast(pl.Float64)
            yield coefficient, indicator.to_numpy()
            continue

        column = matrix.terms.get(term)
        if column is None:
            raise PredictionError(
                "MODEL_TERM_UNRESOLVED",
                f"term {term!r} is neither a level indicator nor a factor this frame "
                "resolves.",
                terms=[term],
            )
        yield coefficient, matrix.frame[column].cast(pl.Float64).to_numpy()


def _offset(
    data: pl.DataFrame, spec: GlmSpec, model_offset: np.ndarray | None = None
) -> npt.NDArray[np.float64] | None:
    """The offset column on the linear-predictor scale, or `None` when the spec has none.

    A known constant per row: it shifts `η̂` and contributes nothing to its variance, which
    is why `predict_glm_interval` adds it to the centre and not to the width.

    `kind="model"` takes the array the backend resolved — pricing-core cannot resolve
    the ref itself, and returning `None` here would score as though no offset were
    declared (FR-MODEL-24): named, never silent.
    """
    if spec.offset.kind == "model":
        if model_offset is None:
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                "offset kind 'model' requires the resolved offset array (model_offset), "
                "and none was supplied (FR-MODEL-24).",
            )
        if model_offset.shape != (data.height,):
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                f"model_offset has {model_offset.shape[0]} rows for {data.height} "
                "data rows (FR-MODEL-24).",
            )
        if not np.all(np.isfinite(model_offset)):
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                "model_offset carries non-finite values (FR-MODEL-24).",
            )
        return np.asarray(model_offset, dtype=np.float64)
    if spec.offset.kind not in {"log_column", "column"}:
        return None
    column = str(spec.offset.column)
    if column not in data.columns:
        raise PredictionError(
            "MODEL_OFFSET_MISSING",
            f"the spec declares an offset on {column!r} and the frame has no such "
            "column. A frequency model scored without its exposure offset returns a "
            "count per unit exposure as though it were a count.",
        )
    values = data[column].cast(pl.Float64).to_numpy()
    if spec.offset.kind == "column":
        return np.asarray(values, dtype=np.float64)
    if np.any(values <= 0):
        raise PredictionError(
            "MODEL_OFFSET_MISSING",
            f"{column!r} has non-positive values and the offset is log(exposure); "
            "such a row contributes no information and must be filtered, not "
            "logged.",
        )
    return np.log(values)


def linear_predictor(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`η = Xβ + offset`, on the scale the link maps from.

    Exposed separately because the diagnostics need `η` for residuals and `μ` for
    everything else, and computing the design twice to get both would double the cost of
    the expensive half.

    `model_offset` is the offset-from-another-model array (FR-MODEL-24): the referenced
    fitted GLM's linear predictor, resolved by the backend and required when
    `spec.offset.kind == "model"`.
    """
    eta = np.zeros(data.height, dtype=np.float64)
    for coefficient, vector in _term_vectors(
        fit, data, factors, bandings=bandings, groupings=groupings
    ):
        eta += coefficient.estimate * vector

    offset = _offset(data, spec, model_offset)
    if offset is not None:
        eta += offset
    return eta


def predict_glm(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`μ`, the expectation, for every row of `data` (FR-MODEL-62).

    Uncertainty is **not** returned here, and deliberately still is not. FR-MODEL-63's
    interval needs the covariance matrix, which the fit stores as a blob this signature
    does not take — `predict_glm_interval` is the entry point that does. Every caller that
    only wants `μ` (the diagnostics, the backtest, the comparison, the peril structure)
    keeps a signature that costs one column of the design at a time.

    `model_offset` is the offset-from-another-model array (FR-MODEL-24), required when
    `spec.offset.kind == "model"`.
    """
    return _inverse_link(
        linear_predictor(
            fit, data, factors, spec,
            model_offset=model_offset, bandings=bandings, groupings=groupings,
        ),
        spec.link,
    )


def predict_glm_interval(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    covariance_bytes: bytes,
    level: float = 0.95,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> tuple[
    npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]
]:
    """`μ` and FR-MODEL-63's interval around it: `(expected, lower, upper)`.

    **What this interval is.** `Var(η̂) = x'Vx`, the sampling variance of the *estimated*
    linear predictor, so `g⁻¹(η̂ ± z·√(x'Vx))` is a confidence interval for `E[Y|x]` — how
    precisely the fit located the mean. It is not a prediction interval for an individual
    outcome, which would add the process variance `φ·V(μ)` the covariance matrix does not
    contain. `model_schema.UncertaintyKind` carries that distinction into the response as
    `confidence_interval_mean`, and `02` FR-MODEL-63 has the dated note.

    **The offset is in the centre and not in the width.** It is a known constant per row, so
    it shifts `η̂` and contributes no variance — the interval on a frequency prediction is
    the interval on the rate, scaled by exposure, which is what a reader of a per-policy
    expected count wants.

    **The bounds are re-ordered after the link, not before.** `g⁻¹` for `inverse` is
    decreasing, so the transformed endpoints of a symmetric interval on `η` come back
    swapped; `PredictedRow` refuses a reversed pair, and this is where the pair stops being
    reversed.

    Unlike `predict_glm` this materialises the `n x p` design, which is why it is a separate
    entry point rather than a flag: `02` §5.1 scopes `/predict` to "dev/debug scale", and
    the callers that score a whole dataset (backtest, diagnostics, comparison) must keep the
    streaming path.
    """
    if not 0.0 < level < 1.0:
        raise PredictionError(
            "MODEL_INTERVAL_UNAVAILABLE",
            f"a confidence level of {level} is not a probability strictly between 0 and 1.",
        )
    from pricing_core.modelling.glm import decode_covariance

    terms = [coefficient.term for coefficient in fit.coefficients]
    covariance = decode_covariance(covariance_bytes, terms)

    columns: list[npt.NDArray[np.float64]] = []
    beta: list[float] = []
    for coefficient, vector in _term_vectors(
        fit, data, factors, bandings=bandings, groupings=groupings
    ):
        columns.append(vector)
        beta.append(coefficient.estimate)

    design = np.column_stack(columns) if columns else np.zeros((data.height, 0))
    eta = design @ np.asarray(beta, dtype=np.float64)
    offset = _offset(data, spec, model_offset)
    if offset is not None:
        eta = eta + offset

    # `x'Vx` row by row without forming the `n x n` product `X V X'`, which for the 10 000
    # rows this endpoint allows would be 800 MB to read 10 000 numbers off its diagonal.
    variance = np.einsum("ij,jk,ik->i", design, covariance, design)
    # A variance that comes back very slightly negative is floating-point noise on a
    # near-zero quantity, not a negative variance; clipped so it becomes a zero-width
    # interval rather than a NaN bound that would serialise as `null` and read as absent.
    half = NormalDist().inv_cdf(1.0 - (1.0 - level) / 2.0) * np.sqrt(
        np.clip(variance, 0.0, None)
    )

    expected = _inverse_link(eta, spec.link)
    first = _inverse_link(eta - half, spec.link)
    second = _inverse_link(eta + half, spec.link)
    return expected, np.minimum(first, second), np.maximum(first, second)


def score_fitted(
    fit: FitResult,
    spec: ModelSpec,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    booster: bytes | None = None,
) -> npt.NDArray[np.float64]:
    """`μ` for a fitted model of **either** kind, on the mean scale.

    The dispatch is the only thing that separates scoring a GLM from scoring a GBM, and two
    callers need it: the comparison (`wf-01` E1, an actuary weighing a booster's lift
    against a GLM's transparency) and the peril structure (E4, where each peril's models are
    scored before they are summed). It lives here rather than in either, because a second
    copy of a dispatch is a second place for the two kinds to diverge — and a peril priced
    through the wrong branch is a silently wrong risk premium.

    A GBM's `booster` is required: a GLM's fit result *is* its model, a GBM's is a reference
    to bytes the caller must fetch (ADR-0001 keeps that fetch out of this package).

    `model_offset` is forwarded on the GLM arm only (FR-MODEL-24): a `GbmSpec` declaring
    `kind="model"` is schema-refused, so there is no GBM arm that could use it.
    """
    if isinstance(fit, GbmFitResult):
        from pricing_core.modelling.gbm import predict_gbm

        if booster is None:
            raise PredictionError(
                "MODEL_NOT_FITTED",
                "a GBM cannot be scored without its booster bytes: its fit result is a "
                "reference to them, not the model itself",
            )
        return np.asarray(
            predict_gbm(
                fit, booster, data, factors, bandings=bandings, groupings=groupings
            ).to_numpy(),
            dtype=np.float64,
        )
    assert isinstance(fit, GlmFitResult)
    assert isinstance(spec, GlmSpec)
    return predict_glm(
        fit, data, factors, spec,
        model_offset=model_offset, bandings=bandings, groupings=groupings,
    )


def detect_quantile_crossing(
    lower: npt.NDArray[np.float64], upper: npt.NDArray[np.float64]
) -> tuple[int, float]:
    """How often, and how badly, a quantile pair contradicts itself (FR-MODEL-78).

    Returns `(rows_crossing, worst_gap)`. **It reorders nothing** — that is the
    requirement's own word, and the reason this returns numbers rather than a corrected
    pair: a reordered pair still does not describe one distribution, and hiding that is the
    failure mode OQ-MODEL-2 was decided to avoid.

    Both figures, because either alone misleads. One crossing row in a million is a
    curiosity; one crossing row by a factor of ten is a bound nobody should quote, and a
    count describes them identically.

    `lower == upper` is **not** crossing: the two fits agreeing exactly at a row is
    degenerate, not inverted, and counting it would report a defect on every row where a
    bound is constant — which is what a booster returns for a leaf with one level.
    """
    if lower.shape != upper.shape:
        raise PredictionError(
            "MODEL_INTERVAL_UNAVAILABLE",
            f"the bounds have different lengths ({lower.shape} and {upper.shape}); they "
            "were scored over different row sets, and NumPy would broadcast them into a "
            "confident answer about a comparison nobody made.",
        )
    gaps = lower - upper
    crossing = gaps > 0.0
    return int(crossing.sum()), float(gaps.max()) if bool(crossing.any()) else 0.0
