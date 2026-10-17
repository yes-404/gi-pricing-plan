"""DP-2 (SL-1543): a book with no unknown-amount rows fits bit-identically to main 055b5e6b.

FR-111's severity population changed on this branch (unknown amounts are excluded and
counted). That is only safe without a `spec_hash` bump if no fit that succeeded before can
now give a different result. This pins the converse: a null-free severity book, weight-0
rows included, gives the coefficients and the `spec_hash` main gave.

The golden was computed once on a detached worktree of main 055b5e6b (`git worktree add
--detach .claude/worktrees/dp2-main-055b5e6b 055b5e6b`, `uv sync --all-packages --frozen`),
by running this module's `_fit()` there — not by reading this branch's output back. No database.
"""

from __future__ import annotations

from uuid import UUID

import numpy as np
import polars as pl
import pytest

from app.platform.modelling import spec_hash
from model_schema import Factor, FactorType, GlmSpec, ResponseKind, WeightSpec
from pricing_core.modelling import fit_glm

DATASET = UUID("00000000-0000-0000-0000-0000000000d2")
AREA = Factor(
    id=UUID("00000000-0000-0000-0000-00000000a001"), slug="area", dataset_id=DATASET,
    version=1, type=FactorType.IDENTITY, source_columns=("area",),
)
SPEC = GlmSpec(
    model_family_slug="sev", dataset_version_id=DATASET,
    response=ResponseKind.CLAIM_SEVERITY, response_column="claim_severity",
    weight=WeightSpec(kind="column", column="claim_count"),
    factors=(AREA.id,), family="gamma", link="log",
)

#: Main 055b5e6b's values; `repr(float)` strings, compared for equality, not closeness.
MAIN_SPEC_HASH = "v11:sha256:08feb14f38e3ffe0fa066eb4250518a7916c1bfcddbf86bfd71a7055914eec01"
MAIN_ESTIMATES = ["7.276352218695058", "-0.37636314579832136"]


def _fit() -> list[str]:
    rng = np.random.default_rng(7)
    n = 400
    area = rng.choice(["A", "B"], n)
    severity = rng.gamma(20.0, 50.0 * np.where(area == "B", 1.5, 1.0), n)
    claims = np.where(rng.random(n) < 0.1, 0.0, rng.integers(1, 3, n).astype(float))
    book = pl.DataFrame({"area": area, "claim_count": claims, "claim_severity": severity})
    return [repr(c.estimate) for c in fit_glm(book, SPEC, [AREA]).result.coefficients]


@pytest.mark.req("FR-111")
def test_a_null_free_severity_fit_is_bit_identical_to_main() -> None:
    assert spec_hash(SPEC) == MAIN_SPEC_HASH
    assert _fit() == MAIN_ESTIMATES
