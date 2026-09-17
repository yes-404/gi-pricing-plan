"""FR-112/FR-182: the cross-validated penalty path, persisted on `Diagnostics`.

FR-112 asks for the full scanned path, not only the alpha selected. FR-182 asks
for per-fold metrics **and their dispersion**, not the mean alone — `path` carries the
first (`std_score` is the path's own dispersion across folds, at every alpha scanned),
`fold_metrics` carries the second (the raw per-fold scores, at the alpha actually
selected).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from model_schema import (
    ComplexityDiagnostic,
    CrossValidationDiagnostics,
    CvFoldMetric,
    CvPathPoint,
    Diagnostics,
    PartitionDiagnostics,
    UniversalDiagnostics,
    Weighting,
    new_uuid7,
)


def _path(*alphas: float) -> tuple[CvPathPoint, ...]:
    return tuple(
        CvPathPoint(alpha=a, mean_score=0.5 - 0.01 * i, std_score=0.02)
        for i, a in enumerate(alphas)
    )


def _fold_metrics(n: int) -> tuple[CvFoldMetric, ...]:
    return tuple(CvFoldMetric(fold=i, rows=100, score=0.48 + 0.001 * i) for i in range(n))


@pytest.mark.req("FR-112")
def test_the_path_carries_every_scanned_alpha() -> None:
    cv = CrossValidationDiagnostics(
        method="random", seed=7, folds=3, metric="deviance",
        selected_alpha=0.01, path=_path(0.0, 0.01, 0.1), fold_metrics=_fold_metrics(3),
    )
    assert [p.alpha for p in cv.path] == [0.0, 0.01, 0.1]
    assert cv.selected_alpha == 0.01


@pytest.mark.req("FR-112")
def test_a_selected_alpha_that_is_not_on_the_path_is_refused() -> None:
    """Negative: the selection must be a point the path actually scored, or the artifact
    claims a decision that was never made."""
    with pytest.raises(ValidationError, match="not one of the path"):
        CrossValidationDiagnostics(
            method="random", seed=7, folds=3, metric="deviance",
            selected_alpha=0.5, path=_path(0.0, 0.01, 0.1), fold_metrics=_fold_metrics(3),
        )


@pytest.mark.req("FR-182")
def test_fold_metrics_carry_dispersion_not_only_the_mean() -> None:
    """The requirement's own phrase: per-fold metrics, not the mean alone."""
    metrics = _fold_metrics(4)
    cv = CrossValidationDiagnostics(
        method="grouped_by_key", seed=1, folds=4, metric="deviance",
        selected_alpha=0.1, path=_path(0.0, 0.1), fold_metrics=metrics,
    )
    assert len(cv.fold_metrics) == 4
    assert len({m.score for m in cv.fold_metrics}) > 1, "fold scores are not forced equal"


@pytest.mark.req("FR-182")
def test_fold_metrics_missing_a_declared_fold_is_refused() -> None:
    """Negative: `folds=4` promises four folds' worth of dispersion; three is a fold that
    was never scored, silently dropped from the very number the requirement asks for."""
    with pytest.raises(ValidationError, match="never scored"):
        CrossValidationDiagnostics(
            method="random", seed=1, folds=4, metric="deviance",
            selected_alpha=0.1, path=_path(0.0, 0.1), fold_metrics=_fold_metrics(3),
        )


@pytest.mark.req("FR-182")
def test_fold_metrics_double_counting_a_fold_is_refused() -> None:
    """Negative: metrics for folds 0, 0, 1, 2 cover every one of `folds=3`'s folds, so the
    missing-fold check alone passes — but fold 0's score enters the dispersion twice, and a
    spread that double-counts one fold is not the per-fold dispersion FR-182 asks
    for."""
    duplicated = _fold_metrics(3)[:1] + _fold_metrics(3)
    with pytest.raises(ValidationError, match="double-count"):
        CrossValidationDiagnostics(
            method="random", seed=1, folds=3, metric="deviance",
            selected_alpha=0.1, path=_path(0.0, 0.1), fold_metrics=duplicated,
        )


@pytest.mark.req("FR-182")
def test_diagnostics_carries_cross_validation_when_the_fit_selected_by_cv() -> None:
    """`Diagnostics.cross_validation` was declared and always `None` (2026-08-18's note on
    the class); this is the slice that populates it, so the field must round-trip inside
    the artifact it was declared for."""
    partition = PartitionDiagnostics(
        weighting=Weighting.EXPOSURE, rows=1000, ae_overall=1.02, gini=0.3, gini_normalised=0.6,
    )
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=new_uuid7(),
        computed_at=datetime.now(UTC),
        universal=UniversalDiagnostics(train=partition, holdout=partition),
        complexity=ComplexityDiagnostic(factor_count=2, parameter_count=3),
        cross_validation=CrossValidationDiagnostics(
            method="random", seed=7, folds=3, metric="deviance",
            selected_alpha=0.1, path=_path(0.0, 0.1, 1.0), fold_metrics=_fold_metrics(3),
        ),
    )
    assert diagnostics.cross_validation is not None
    assert diagnostics.cross_validation.selected_alpha == 0.1
    dumped = diagnostics.model_dump(mode="json")
    assert Diagnostics.model_validate(dumped) == diagnostics


@pytest.mark.req("FR-170")
def test_diagnostics_without_cv_still_carries_none() -> None:
    """FR-170: computed once at fit time. A fixed-alpha GLM or a GBM was never
    cross-validated, and `None` is the honest reading of that — not an empty path
    standing in for a scan that never ran."""
    partition = PartitionDiagnostics(
        weighting=Weighting.EXPOSURE, rows=1000, ae_overall=1.02, gini=0.3, gini_normalised=0.6,
    )
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=new_uuid7(),
        computed_at=datetime.now(UTC),
        universal=UniversalDiagnostics(train=partition, holdout=partition),
        complexity=ComplexityDiagnostic(factor_count=2, parameter_count=3),
    )
    assert diagnostics.cross_validation is None
