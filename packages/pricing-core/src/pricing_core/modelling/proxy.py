"""Proxy assessment: how strongly a Factor is associated with a protected characteristic
(`02` FR-91, FR-2137 to FR-2142).

**This is evidence, never a gate.** Nothing here compares a number with a limit, and the
result has no field that says pass, fail or flagged (FR-2141). Whether an association
amounts to unlawful discrimination is a legal judgement, so the module measures and stops.

**One computation serves both granularities** (FR-2138). A reference table holds, per
key, a share for every class. An individual-level table is the case whose shares are all 0
or 1, so there is no second code path for it. A matched row's exposure is split across the
classes by those shares, which gives the *expected joint weight* ``W(level, class)`` that
every measure reads (FR-2139):

* **Mutual information**, in bits, of level and class under ``W``, and the same divided by
  the class entropy (null when that entropy is 0).
* **One-vs-rest AUC per class**, where a row's score is its level's ``W``-share of the class
  (in-sample, so the best a level-wise rule could do). A row contributes positive weight
  ``exposure * share`` and negative weight ``exposure * (1 - share)`` at its level's score,
  and tied scores are averaged. This is exactly the AUC of the same rows replicated as a
  weighted positive and a weighted negative, which is how the tests check it.
* **Coverage**: matched exposure over total exposure.

Pure Polars and NumPy, no new dependency, and nothing is persisted: the reference rows are
read and dropped (FR-2140). The scoring path is untouched.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
import polars as pl
from numpy.typing import NDArray

#: Shares must sum to one within this, and lie in [0, 1] (FR-2138).
SHARE_TOLERANCE = 1e-6


class ProxyAssessmentError(ValueError):
    """The frame or the reference table cannot be assessed; the message names the cause."""


@dataclass(frozen=True)
class FactorProxyResult:
    """One Factor's association measures. There is deliberately no verdict field."""

    factor: str
    mutual_information_bits: float
    #: ``None`` when the class entropy is 0, so there is nothing to normalise by.
    normalised_mutual_information: float | None
    #: ``None`` for a class with no positive or no negative weight at all.
    auc_by_class: Mapping[str, float | None]


@dataclass(frozen=True)
class ProxyAssessmentResult:
    matched_rows: int
    matched_exposure: float
    total_exposure: float
    #: ``matched_exposure / total_exposure``; 0.0 when there is no exposure at all.
    coverage: float
    factors: tuple[FactorProxyResult, ...]


def assess_proxies(
    frame: pl.DataFrame,
    factors: Sequence[str],
    reference: pl.DataFrame,
    *,
    key: str,
    reference_key: str,
    classes: Sequence[str],
    exposure: str = "exposure_years",
) -> ProxyAssessmentResult:
    """Measure each of ``factors`` (columns already resolved to Levels) against ``classes``.

    ``reference`` holds ``reference_key`` and one share column per class. Rows of ``frame``
    whose ``key`` is not in the reference are unmatched: excluded from every measure and
    counted in the coverage (FR-2138).
    """
    class_list = list(classes)
    _validate(frame, factors, reference, key, reference_key, class_list, exposure)

    weight = pl.col(exposure).cast(pl.Float64)
    kept = list(dict.fromkeys([*factors, key]))
    clash = [c for c in [*class_list, "_w"] if c in kept]
    if clash:
        raise ProxyAssessmentError(f"class names clash with frame columns {clash}")
    joined = frame.select([*kept, weight.alias("_w")]).join(
        reference.select([pl.col(reference_key).alias(key), *class_list]),
        on=key,
        how="left",
    )
    total_exposure = float(joined["_w"].sum())
    matched = joined.filter(pl.col(class_list[0]).is_not_null())
    matched_exposure = float(matched["_w"].sum())
    coverage = matched_exposure / total_exposure if total_exposure > 0 else 0.0

    results = tuple(_assess_factor(matched, factor, class_list) for factor in factors)
    return ProxyAssessmentResult(
        matched_rows=matched.height,
        matched_exposure=matched_exposure,
        total_exposure=total_exposure,
        coverage=coverage,
        factors=results,
    )


def _validate(
    frame: pl.DataFrame,
    factors: Sequence[str],
    reference: pl.DataFrame,
    key: str,
    reference_key: str,
    classes: list[str],
    exposure: str,
) -> None:
    if not classes or len(set(classes)) != len(classes):
        raise ProxyAssessmentError("classes must be a non-empty list of distinct names")
    missing = [c for c in [*factors, key, exposure] if c not in frame.columns]
    if missing:
        raise ProxyAssessmentError(f"frame has no column {missing}")
    missing = [c for c in [reference_key, *classes] if c not in reference.columns]
    if missing:
        raise ProxyAssessmentError(f"reference has no column {missing}")
    if reference[reference_key].is_duplicated().any():
        raise ProxyAssessmentError(f"reference key {reference_key!r} is repeated")
    shares = reference.select(classes).to_numpy().astype(np.float64)
    if np.isnan(shares).any():
        raise ProxyAssessmentError("reference shares must not be null")
    if (shares < 0).any() or (shares > 1).any():
        raise ProxyAssessmentError("reference shares must lie in [0, 1]")
    off = np.abs(shares.sum(axis=1) - 1.0) > SHARE_TOLERANCE
    if off.any():
        bad = reference[reference_key].filter(pl.Series(off)).head(5).to_list()
        raise ProxyAssessmentError(f"reference shares do not sum to 1 for keys {bad}")
    exposures = frame[exposure].cast(pl.Float64)
    if exposures.null_count() or (exposures < 0).any():
        raise ProxyAssessmentError("exposure must be non-null and non-negative")


def _assess_factor(matched: pl.DataFrame, factor: str, classes: list[str]) -> FactorProxyResult:
    grouped = matched.group_by(factor).agg(
        [(pl.col("_w") * pl.col(c)).sum().alias(c) for c in classes]
    )
    joint = grouped.select(classes).to_numpy().astype(np.float64)  # levels x classes
    return FactorProxyResult(
        factor=factor,
        mutual_information_bits=_mutual_information_bits(joint),
        normalised_mutual_information=_normalised(joint),
        auc_by_class={c: _auc(joint, k) for k, c in enumerate(classes)},
    )


def _entropy_bits(p: NDArray[np.float64]) -> float:
    nz = p[p > 0]
    return float(-(nz * np.log2(nz)).sum())


def _mutual_information_bits(joint: NDArray[np.float64]) -> float:
    total = joint.sum()
    if total <= 0:
        return 0.0
    p = joint / total
    outer = np.outer(p.sum(axis=1), p.sum(axis=0))
    nz = p > 0
    mi = float((p[nz] * np.log2(p[nz] / outer[nz])).sum())
    return max(mi, 0.0)  # rounding can leave -1e-17 on an independent table


def _normalised(joint: NDArray[np.float64]) -> float | None:
    total = joint.sum()
    if total <= 0:
        return None
    entropy = _entropy_bits(joint.sum(axis=0) / total)
    if entropy <= 0:
        return None
    return _mutual_information_bits(joint) / entropy


def _auc(joint: NDArray[np.float64], k: int) -> float | None:
    """One-vs-rest AUC of class ``k``, scoring each level by its share of that class."""
    level_total = joint.sum(axis=1)
    pos = joint[:, k]
    neg = level_total - pos
    positive, negative = float(pos.sum()), float(neg.sum())
    if positive <= 0 or negative <= 0:
        return None
    keep = level_total > 0
    score = pos[keep] / level_total[keep]
    # Levels with an equal score tie: pool them, then count each pool's positives against
    # the negatives scored strictly below it plus half of its own (ties averaged).
    _, pool = np.unique(score, return_inverse=True)
    pool_pos = np.bincount(pool, weights=pos[keep])
    pool_neg = np.bincount(pool, weights=neg[keep])
    below = np.cumsum(pool_neg) - pool_neg
    auc = float((pool_pos * (below + 0.5 * pool_neg)).sum() / (positive * negative))
    return min(max(auc, 0.0), 1.0) if math.isfinite(auc) else None
