"""DP-2 (SL-1543): a book with no unknown-amount rows fits bit-identically to main 055b5e6b.

FR-111's severity population changed on this branch (unknown amounts are excluded and
counted). That is only safe without a `spec_hash` bump if no fit that succeeded before can
now give a different result. This pins the converse: a null-free severity book, weight-0
rows included, gives the coefficients and the `spec_hash` main gave.

The golden was computed once on a detached worktree of main 055b5e6b (`git worktree add
--detach .claude/worktrees/dp2-main-055b5e6b 055b5e6b`, `uv sync --all-packages --frozen`),
by running this module's `_fit()` there — not by reading this branch's output back. No database.

The golden is **host-bound at the bit level**: PR #1335's CI gave `-0.3763631457983215` where
this host gave `-0.37636314579832136` (1 ulp; intercept and `spec_hash` identical). So the
estimates are compared within 4 ulp, and `spec_hash` stays exact. The governed precision is
NFR-481 (`docs/specs/02-modelling.md:2974`): "identical `spec_hash` + seed reproduces identical
coefficients to 1e-10 (GLM) ... on the same library versions". 4 ulp (~1e-15 relative) is far
tighter than 1e-10, so this is not a loosening against the spec. The bit-exact claim that the
unknown-amount exclusion changes nothing is made where it holds, on one host, in
`test_unknown_amount_rows_are_excluded_without_touching_the_fit`.
"""

from __future__ import annotations

from uuid import UUID

import numpy as np
import polars as pl
import pytest

from app.platform.modelling import spec_hash
from model_schema import Factor, FactorType, GlmSpec, ResponseKind, WeightSpec
from pricing_core.modelling import fit_glm
from pricing_core.modelling.weights import drop_zero_weight_rows

DATASET = UUID("00000000-0000-0000-0000-0000000000d2")
AREA = Factor(
    id=UUID("00000000-0000-0000-0000-00000000a001"),
    slug="area",
    dataset_id=DATASET,
    version=1,
    type=FactorType.IDENTITY,
    source_columns=("area",),
)
SPEC = GlmSpec(
    model_family_slug="sev",
    dataset_version_id=DATASET,
    response=ResponseKind.CLAIM_SEVERITY,
    response_column="claim_severity",
    weight=WeightSpec(kind="column", column="claim_count"),
    factors=(AREA.id,),
    family="gamma",
    link="log",
)

#: Main 055b5e6b's values as `repr(float)` strings; compared within 4 ulp (see the docstring).
MAIN_SPEC_HASH = "v11:sha256:08feb14f38e3ffe0fa066eb4250518a7916c1bfcddbf86bfd71a7055914eec01"
MAIN_ESTIMATES = ["7.276352218695058", "-0.37636314579832136"]


def _book() -> pl.DataFrame:
    rng = np.random.default_rng(7)
    n = 400
    area = rng.choice(["A", "B"], n)
    severity = rng.gamma(20.0, 50.0 * np.where(area == "B", 1.5, 1.0), n)
    claims = np.where(rng.random(n) < 0.1, 0.0, rng.integers(1, 3, n).astype(float))
    return pl.DataFrame({"area": area, "claim_count": claims, "claim_severity": severity})


def _estimates(book: pl.DataFrame) -> list[float]:
    return [c.estimate for c in fit_glm(book, SPEC, [AREA]).result.coefficients]


@pytest.mark.req("FR-111")
def test_a_null_free_severity_fit_matches_main() -> None:
    assert spec_hash(SPEC) == MAIN_SPEC_HASH
    np.testing.assert_array_max_ulp(
        np.array(_estimates(_book())), np.array([float(s) for s in MAIN_ESTIMATES]), maxulp=4
    )


@pytest.mark.req("FR-111")
def test_unknown_amount_rows_are_excluded_without_touching_the_fit() -> None:
    """Same host, exact: appending unknown-amount rows leaves every coefficient bit-identical.

    The rows are excluded by `weights._exclude` (weights.py:75-96: a `claim_severity` fit drops
    a null response and counts it in `WeightExclusion.excluded_unknown`; `fit_glm` calls it at
    glm.py:561). The fit result carries no count, so the count is read from that helper.
    """
    book = _book()
    unknown = pl.DataFrame(
        {
            "area": ["A", "B", "A", "B", "B"],
            "claim_count": [1.0, 2.0, 1.0, 1.0, 2.0],
            "claim_severity": pl.Series([None] * 5, dtype=pl.Float64),
        }
    )
    # The precondition: no new level, so the design-matrix encoding cannot change.
    assert set(unknown["area"]) <= set(book["area"])
    with_unknown = pl.concat([book, unknown])
    assert drop_zero_weight_rows(with_unknown, SPEC).excluded_unknown == unknown.height
    assert [repr(e) for e in _estimates(with_unknown)] == [repr(e) for e in _estimates(book)]
