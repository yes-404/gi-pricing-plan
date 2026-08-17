"""Comparing fitted models on a shared holdout (`02` FR-MODEL-56, §5.2).

`wf-01` E1: two or more candidates, aligned metrics, double lift, and the factor-by-factor
relativity differences an actuary actually argues from.

**The declared signature was `compare_models(models, holdout)` and could not be written.**
That is the third instance of one defect: a `Model` carries *references* — factor ids,
banding ids, a dataset version — and resolving one needs a database, which ADR-0001 forbids
this package. `predict_glm` and `compute_diagnostics` were corrected the same way on
2026-08-16. The caller resolves; this module computes. `ComparisonCandidate` is that
resolution, and it carries the model's canonical ref purely so the output can be labelled.

Two refusals are the module's own, not the platform's:

* **A comparison of one model** is a diagnostics read. Naming it a comparison would let an
  approval cite it as evidence a candidate had been weighed.
* **Candidates with different weighting schemes.** FR-MODEL-55 makes the weighting part of
  the metric, so an exposure-weighted A/E beside a claim-count-weighted one is two
  quantities in one column — precisely the comparison the requirement exists to prevent.
  A frequency model and a severity model are not rivals; they are different questions.

The metric helpers are imported from `diagnostics` rather than reimplemented. A second
exposure-weighted Gini would be a second answer to the same question, and the comparison
would then be able to disagree with the diagnostics each model already carries.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl

from model_schema import (
    Banding,
    ComparisonMetric,
    ComparisonSummary,
    ComparisonValue,
    DoubleLift,
    DoubleLiftBin,
    Factor,
    GlmFitResult,
    GlmSpec,
    Grouping,
    MetricDirection,
    RelativityDifference,
    Weighting,
)
from pricing_core.modelling.diagnostics import (
    _bin_index,
    _gini,
    _weighting,
    _weights,
    deviance,
)
from pricing_core.modelling.errors import ModellingError
from pricing_core.modelling.predict import predict_glm

__all__ = ["ComparisonCandidate", "compare_models"]

#: Deciles, as everywhere else in `02` §3.8's charts. The same constant is `_BINS` in
#: `diagnostics`; it is restated rather than imported because a future decision to bin double
#: lift differently from lift is a real one, and sharing the name would hide it.
_BINS = 10


@dataclass(frozen=True, slots=True)
class ComparisonCandidate:
    """One model, resolved to everything scoring it needs (ADR-0001).

    `ref` is the canonical `{type}:{slug}@{version}` string (ID-3) and is used only as a
    label: this module never resolves it, because resolving it is the database work the
    package may not do.
    """

    ref: str
    fit: GlmFitResult
    spec: GlmSpec
    factors: tuple[Factor, ...]
    bandings: Mapping[UUID, Banding] = field(default_factory=dict)
    groupings: Mapping[UUID, Grouping] = field(default_factory=dict)


def compare_models(
    candidates: Sequence[ComparisonCandidate],
    holdout: pl.DataFrame,
    *,
    baseline: str | None = None,
) -> ComparisonSummary:
    """Align two or more candidates on one holdout (FR-MODEL-56).

    `baseline` names the model double lift is measured against, defaulting to the first
    candidate. The `split_ref` is **not** verified here — that is the platform's job, because
    it needs the split artifact — but every candidate must agree on one, and the disagreement
    is refused rather than silently resolved to the first.
    """
    _refuse_an_incomparable_set(candidates, holdout)

    refs = tuple(c.ref for c in candidates)
    baseline_ref = baseline or refs[0]
    if baseline_ref not in refs:
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            f"baseline {baseline_ref!r} is not among the candidates {list(refs)}. Double "
            "lift is measured against the baseline, so a reference line from outside the "
            "set is one the reader cannot look up.",
        )

    scheme = _weighting(candidates[0].spec)
    exposure = _weights(candidates[0].spec, holdout)
    response = candidates[0].spec.response_column
    actual = holdout[response].cast(pl.Float64).to_numpy()
    predicted = {c.ref: _score(c, holdout) for c in candidates}

    split_ref = candidates[0].spec.split_ref
    assert split_ref is not None  # guarded in `_refuse_an_incomparable_set`

    return ComparisonSummary(
        model_refs=refs,
        baseline_ref=baseline_ref,
        split_ref=split_ref,
        holdout_rows=holdout.height,
        metrics=_metrics(candidates, actual, exposure, predicted, scheme),
        double_lift=tuple(
            _double_lift(
                baseline_ref=baseline_ref,
                challenger_ref=ref,
                actual=actual,
                exposure=exposure,
                baseline_mu=predicted[baseline_ref],
                challenger_mu=predicted[ref],
                scheme=scheme,
            )
            for ref in refs
            if ref != baseline_ref
        ),
        relativity_differences=_relativity_differences(candidates),
    )


# -- refusals -----------------------------------------------------------------------------


def _refuse_an_incomparable_set(
    candidates: Sequence[ComparisonCandidate], holdout: pl.DataFrame
) -> None:
    if len(candidates) < 2:
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            f"a comparison needs two or more models and was given {len(candidates)} "
            "(FR-MODEL-56). One model measured against nothing is a diagnostics read, and "
            "calling it a comparison would let an approval cite it as evidence that a "
            "candidate had been considered.",
        )
    if holdout.height == 0:
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            "the holdout is empty. Metrics on no rows cannot be wrong, which is not the "
            "same as two models being indistinguishable.",
        )

    refs = [c.ref for c in candidates]
    if len(set(refs)) != len(refs):
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            f"{refs} names a model twice. A version compared with itself produces agreement "
            "it did not have to earn.",
        )

    schemes = {c.ref: _weighting(c.spec) for c in candidates}
    if len(set(schemes.values())) > 1:
        detail = ", ".join(f"{ref} is {s.value}" for ref, s in schemes.items())
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            f"the candidates disagree about weighting — {detail}. FR-MODEL-55 makes the "
            "weighting part of the metric, so aligning them in one table would put two "
            "different quantities in one column. A frequency model and a severity model are "
            "not rivals; they answer different questions.",
        )

    responses = {c.spec.response_column for c in candidates}
    if len(responses) > 1:
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            f"the candidates model different responses ({sorted(responses)}). Their metrics "
            "would be computed against different columns of the same holdout.",
        )

    splits = {c.spec.split_ref for c in candidates}
    if None in splits or len(splits) > 1:
        raise ModellingError(
            "MODELS_NOT_COMPARABLE",
            "the candidates do not cite one shared split. FR-MODEL-56 compares models "
            "fitted on the same holdout, and `01` FR-DATA-36 records the split on the parent "
            "version precisely so that 'the same holdout' is one artifact two models cite "
            "rather than two derivations believed to match.",
        )


def _score(candidate: ComparisonCandidate, holdout: pl.DataFrame) -> npt.NDArray[np.float64]:
    return predict_glm(
        candidate.fit,
        holdout,
        candidate.factors,
        candidate.spec,
        bandings=candidate.bandings,
        groupings=candidate.groupings,
    )


# -- metrics ------------------------------------------------------------------------------


def _metrics(
    candidates: Sequence[ComparisonCandidate],
    actual: npt.NDArray[np.float64],
    exposure: npt.NDArray[np.float64],
    predicted: Mapping[str, npt.NDArray[np.float64]],
    scheme: Weighting,
) -> tuple[ComparisonMetric, ...]:
    """The aligned table (FR-MODEL-56), recomputed on the shared holdout.

    Recomputed rather than read from each model's stored diagnostics, deliberately. Two
    models' diagnostics were computed by two Jobs, and the point of the comparison is that
    every number in the table came from the same rows in the same run — an alignment nothing
    downstream can verify once the numbers are copied out of two artifacts.
    """
    by_ref: dict[str, dict[str, float | None]] = {}
    for candidate in candidates:
        mu = predicted[candidate.ref]
        expected = float(np.sum(mu))
        gini, gini_normalised = _gini(actual, mu, exposure)
        power = float(candidate.spec.family_params.get("power", 1.5))
        by_ref[candidate.ref] = {
            "ae_overall": (float(np.sum(actual)) / expected) if expected > 0 else None,
            "gini": gini,
            "gini_normalised": gini_normalised,
            "holdout_deviance": deviance(
                actual, mu, family=candidate.spec.family, power=power
            ),
            "rows": float(actual.size),
        }

    directions = {
        "ae_overall": MetricDirection.CLOSER_TO_ONE_IS_BETTER,
        "gini": MetricDirection.HIGHER_IS_BETTER,
        "gini_normalised": MetricDirection.HIGHER_IS_BETTER,
        "holdout_deviance": MetricDirection.LOWER_IS_BETTER,
        "rows": MetricDirection.NOT_ORDERED,
    }
    return tuple(
        ComparisonMetric(
            metric=metric,
            weighting=scheme,
            direction=direction,
            values=tuple(
                ComparisonValue(model_ref=c.ref, value=by_ref[c.ref][metric])
                for c in candidates
            ),
            leader=_leader({c.ref: by_ref[c.ref][metric] for c in candidates}, direction),
        )
        for metric, direction in directions.items()
    )


def _leader(
    values: Mapping[str, float | None], direction: MetricDirection
) -> str | None:
    """Which model wins, or `None` where the question does not arise.

    Three reasons for `None`, all of them states a table has to render: the metric does not
    order, no model produced a value, or two models tie. A tie broken silently by dictionary
    order is a winner the data did not choose.
    """
    if direction is MetricDirection.NOT_ORDERED:
        return None
    scored = {ref: v for ref, v in values.items() if v is not None}
    if not scored:
        return None

    if direction is MetricDirection.HIGHER_IS_BETTER:
        best = max(scored.values())
    elif direction is MetricDirection.LOWER_IS_BETTER:
        best = min(scored.values())
    else:
        closest = min(abs(v - 1.0) for v in scored.values())
        winners = [ref for ref, v in scored.items() if abs(v - 1.0) == closest]
        return winners[0] if len(winners) == 1 else None

    winners = [ref for ref, v in scored.items() if v == best]
    return winners[0] if len(winners) == 1 else None


# -- double lift --------------------------------------------------------------------------


def _double_lift(
    *,
    baseline_ref: str,
    challenger_ref: str,
    actual: npt.NDArray[np.float64],
    exposure: npt.NDArray[np.float64],
    baseline_mu: npt.NDArray[np.float64],
    challenger_mu: npt.NDArray[np.float64],
    scheme: Weighting,
) -> DoubleLift:
    """One challenger against the baseline, binned by the **ratio** of their predictions.

    The ordering is the chart. Sorting by either model's prediction gives two lift curves
    side by side, which answers "does each model order risk?"; sorting by the ratio answers
    "where they disagree, which one does the data support?" — the question a selection
    decision actually turns on (`wf-01` E2).

    Per-bin figures are means **per unit of exposure**, matching `LiftBin` in diagnostics, so
    a reader moving between the two charts is reading the same kind of number.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(baseline_mu > 0, challenger_mu / baseline_mu, 0.0)
    bins = _bin_index(ratio, _BINS)

    rendered: list[DoubleLiftBin] = []
    for b in range(1, _BINS + 1):
        mask = bins == b
        rows = int(np.count_nonzero(mask))
        if rows == 0:
            continue
        bin_exposure = float(np.sum(exposure[mask]))
        divisor = bin_exposure if bin_exposure > 0 else float(rows)
        rendered.append(
            DoubleLiftBin(
                bin=b,
                rows=rows,
                actual=float(np.sum(actual[mask])) / divisor,
                baseline_predicted=float(np.sum(baseline_mu[mask])) / divisor,
                challenger_predicted=float(np.sum(challenger_mu[mask])) / divisor,
                exposure_years=Decimal(str(round(bin_exposure, 6))),
            )
        )
    return DoubleLift(
        baseline_ref=baseline_ref,
        challenger_ref=challenger_ref,
        weighting=scheme,
        bins=tuple(rendered),
    )


# -- relativity differences ----------------------------------------------------------------


def _relativity_differences(
    candidates: Sequence[ComparisonCandidate],
) -> tuple[RelativityDifference, ...]:
    """Every (factor, level) either model prices, with each model's relativity beside it.

    Ordered by the widest gap, because that is the order the table is read in: two models can
    score almost identically and disagree by 15 % on young drivers, and no aggregate metric
    shows it.

    A level one model does not have gets `None`, not `1.0`. Reporting the absent relativity as
    "no effect" is the defect the spine audit found in `RelativityLevel`, and it would be
    worse here — a difference of 0.0 says the two models agree.
    """
    levels: dict[tuple[str, str], dict[str, float | None]] = {}
    for candidate in candidates:
        for factor, entries in candidate.fit.relativities.items():
            for entry in entries:
                levels.setdefault((factor, entry.level), {})[candidate.ref] = entry.relativity

    rows: list[RelativityDifference] = []
    for (factor, level), by_ref in levels.items():
        values = tuple(
            ComparisonValue(model_ref=c.ref, value=by_ref.get(c.ref)) for c in candidates
        )
        present = [v.value for v in values if v.value is not None]
        rows.append(
            RelativityDifference(
                factor=factor,
                level=level,
                values=values,
                max_abs_difference=(
                    max(present) - min(present) if len(present) >= 2 else None
                ),
            )
        )
    return tuple(
        sorted(
            rows,
            key=lambda r: (-(r.max_abs_difference or -1.0), r.factor, r.level),
        )
    )
