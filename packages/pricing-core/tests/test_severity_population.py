"""FR-111 (amended 2026-10-17, SL-1543): the severity model's population is `claim_count > 0`
and a known, positive amount.

An unknown amount (a null `claim_severity`) is excluded and counted; a known amount that is
not positive is refused by the Gamma family, never dropped and never relabelled as unknown.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmSpec, ResponseKind, WeightSpec
from pricing_core.modelling import compute_diagnostics, fit_glm
from pricing_core.modelling.glm import GlmFitError

DATASET = uuid4()
AREA = Factor(
    id=uuid4(), slug="area", dataset_id=DATASET, version=1,
    type=FactorType.IDENTITY, source_columns=("area",),
)
SPEC = GlmSpec(
    model_family_slug="sev", dataset_version_id=DATASET,
    response=ResponseKind.CLAIM_SEVERITY, response_column="claim_severity",
    weight=WeightSpec(kind="column", column="claim_count"),
    factors=(AREA.id,), family="gamma", link="log",
)


def _book(n: int = 400) -> pl.DataFrame:
    rng = np.random.default_rng(7)
    area = rng.choice(["A", "B"], n)
    severity = rng.gamma(20.0, 50.0 * np.where(area == "B", 1.5, 1.0), n)
    return pl.DataFrame(
        {"area": area, "claim_count": np.ones(n), "claim_severity": severity}
    )


def _unknown(book: pl.DataFrame, rows: list[int]) -> pl.DataFrame:
    """`rows` are claimants (claim_count 1) whose amount is unknown: severity null."""
    mask = pl.Series([i in rows for i in range(book.height)])
    return book.with_columns(
        pl.when(mask).then(None).otherwise(pl.col("claim_severity")).alias("claim_severity")
    )


@pytest.mark.req("FR-111")
def test_unknown_amount_rows_are_excluded_and_the_count_is_reported() -> None:
    """Red on main: a null response with weight 1 reaches glum, which refuses the fit."""
    clean = _book()
    # 4 train rows (3, 10, 50, 70) and 1 holdout row (300) are unknown.
    with_unknown = _unknown(clean, [3, 10, 50, 70, 300])
    kept = [i for i in range(clean.height) if i not in (3, 10, 50, 70, 300)]
    train, holdout = with_unknown[:200], with_unknown[200:]

    fit = fit_glm(train, SPEC, [AREA]).result
    reference = fit_glm(clean[[i for i in kept if i < 200]], SPEC, [AREA]).result
    assert [c.estimate for c in fit.coefficients] == [c.estimate for c in reference.coefficients]

    diag = compute_diagnostics(
        fit, SPEC, [AREA], train=train, holdout=holdout, type_iii=False
    )
    assert diag.universal.train.rows_excluded_unknown_response == 4
    assert diag.universal.holdout.rows_excluded_unknown_response == 1
    assert diag.universal.train.rows == 196
    assert diag.universal.holdout.rows == 199
    assert diag.universal.train.rows_excluded_zero_weight == 0


@pytest.mark.req("FR-111")
def test_a_known_zero_amount_is_refused_not_dropped() -> None:
    """A recorded 0 is a known value outside the Gamma domain: refused, never excluded."""
    book = _book().with_columns(
        pl.when(pl.int_range(pl.len()) == 5).then(0.0)
        .otherwise(pl.col("claim_severity")).alias("claim_severity")
    )
    with pytest.raises(GlmFitError) as raised:
        fit_glm(book, SPEC, [AREA])
    assert raised.value.code == "GLM_FIT_FAILED"


@pytest.mark.req("FR-111")
def test_the_unknown_count_is_none_off_a_severity_spec() -> None:
    """A fit whose response is not `claim_severity` has no such population: None, not 0."""
    book = _book().with_columns(pl.col("claim_count").alias("n")).drop("claim_count")
    spec = GlmSpec(
        model_family_slug="g", dataset_version_id=DATASET, response_column="claim_severity",
        factors=(AREA.id,), family="gamma", link="log",
    )
    fit = fit_glm(book, spec, [AREA]).result
    diag = compute_diagnostics(
        fit, spec, [AREA], train=book[:200], holdout=book[200:], type_iii=False
    )
    assert diag.universal.train.rows_excluded_unknown_response is None
