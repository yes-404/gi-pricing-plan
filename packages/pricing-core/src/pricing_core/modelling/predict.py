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
from collections.abc import Mapping, Sequence
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl

from model_schema import Banding, Factor, GlmFitResult, GlmSpec, Grouping
from pricing_core.modelling.factors import resolve_factors

__all__ = ["PredictionError", "linear_predictor", "predict_glm"]

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


def linear_predictor(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`η = Xβ + offset`, on the scale the link maps from.

    Exposed separately because the diagnostics need `η` for residuals and `μ` for
    everything else, and computing the design twice to get both would double the cost of
    the expensive half.
    """
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    eta = np.zeros(data.height, dtype=np.float64)

    for coefficient in fit.coefficients:
        term = coefficient.term
        if term == "intercept":
            eta += coefficient.estimate
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
            eta += coefficient.estimate * indicator.to_numpy()
            continue

        column = matrix.terms.get(term)
        if column is None:
            raise PredictionError(
                "MODEL_TERM_UNRESOLVED",
                f"term {term!r} is neither a level indicator nor a factor this frame "
                "resolves.",
                terms=[term],
            )
        eta += coefficient.estimate * matrix.frame[column].cast(pl.Float64).to_numpy()

    if spec.offset.kind in {"log_column", "column"}:
        column = str(spec.offset.column)
        if column not in data.columns:
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                f"the spec declares an offset on {column!r} and the frame has no such "
                "column. A frequency model scored without its exposure offset returns a "
                "count per unit exposure as though it were a count.",
            )
        values = data[column].cast(pl.Float64).to_numpy()
        if spec.offset.kind == "log_column":
            if np.any(values <= 0):
                raise PredictionError(
                    "MODEL_OFFSET_MISSING",
                    f"{column!r} has non-positive values and the offset is log(exposure); "
                    "such a row contributes no information and must be filtered, not "
                    "logged.",
                )
            eta += np.log(values)
        else:
            eta += values

    return eta


def predict_glm(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`μ`, the expectation, for every row of `data` (FR-MODEL-62).

    Uncertainty is **not** returned here. FR-MODEL-63 wants a prediction interval from the
    covariance matrix, which the fit stores as a blob this signature does not take; adding
    a half-interval derived from the coefficient standard errors alone would be a number
    that reads like an interval and is not one.
    """
    return _inverse_link(
        linear_predictor(fit, data, factors, spec, bandings=bandings, groupings=groupings),
        spec.link,
    )
