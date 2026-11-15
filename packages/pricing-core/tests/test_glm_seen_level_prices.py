"""A level the fit saw prices exactly as the fitted coefficients say, on both paths (FR-2143).

The goldens below were computed from the product files of the change's base commit (a8a59866) on
both paths, over a fixed hand-written fit (so no estimator and no platform float enters), and are
pinned as `repr(float)`: the unseen-level rule must not move the price of a quote it does not touch.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    Coefficient,
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    OffsetSpec,
    RelativityLevel,
)
from pricing_core.modelling.predict import linear_predictor, linear_predictor_row

pytestmark = pytest.mark.req("FR-2143")

DATASET = uuid4()

#: `quote name -> (frame path eta, one-row path eta)` as `repr(float)`, from origin/main.
GOLDEN: dict[str, tuple[str, str]] = {
    "A-young": ("-2.10803", "-2.10803"),
    "A-mid": ("-2.3189599999999997", "-2.3189599999999997"),
    "B-old": ("-2.325989", "-2.325989"),
    "B-young": ("-2.4132", "-2.4132"),
}


def _coefficient(term: str, estimate: float) -> Coefficient:
    return Coefficient(
        term=term, estimate=estimate, std_error=0.1, z=1.0, p_value=0.5,
        ci_95=(estimate - 0.2, estimate + 0.2),
    )


def build() -> tuple[GlmFitResult, GlmSpec, tuple[Factor, ...], dict[Any, Banding]]:
    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="age",
        method=BandingMethod.MANUAL, boundaries=(18.0, 30.0, 60.0, 90.0),
        labels=("young", "mid", "old"),
    )
    area = Factor(
        id=uuid4(), slug="area", dataset_id=DATASET, version=1, type=FactorType.IDENTITY,
        source_columns=("area",),
    )
    age = Factor(
        id=uuid4(), slug="age_band", dataset_id=DATASET, version=1, type=FactorType.BANDING,
        source_columns=("age",), banding_id=banding.id,
    )
    spec = GlmSpec(
        model_family_slug="seen-level-prices", dataset_version_id=DATASET,
        response_column="claims", offset=OffsetSpec(), factors=(area.id, age.id),
        family="gamma", link="log",
    )
    fit = GlmFitResult(
        converged=True, iterations=1, fit_seconds=0.0, rows=100,
        coefficients=(
            _coefficient("intercept", -2.4132),
            _coefficient("area[A]", 0.30517),
            _coefficient("age_band[mid]", -0.21093),
            _coefficient("age_band[old]", 0.087211),
        ),
        relativities={
            "area": (
                RelativityLevel(level="B", is_base=True),
                RelativityLevel(level="A", is_base=False),
            ),
            "age_band": (
                RelativityLevel(level="young", is_base=True),
                RelativityLevel(level="mid", is_base=False),
                RelativityLevel(level="old", is_base=False),
            ),
        },
    )
    return fit, spec, (area, age), {banding.id: banding}


QUOTES: dict[str, dict[str, Any]] = {
    "A-young": {"area": "A", "age": 20.0},
    "A-mid": {"area": "A", "age": 45.0},
    "B-old": {"area": "B", "age": 70.0},
    "B-young": {"area": "B", "age": 18.0},
}


def compute() -> dict[str, tuple[str, str]]:
    fit, spec, factors, bandings = build()
    out: dict[str, tuple[str, str]] = {}
    for name, quote in QUOTES.items():
        frame = linear_predictor(
            fit, pl.DataFrame([quote]), factors, spec, bandings=bandings
        )
        one = linear_predictor_row(fit, quote, factors, spec, bandings=bandings)
        out[name] = (repr(float(frame[0])), repr(float(one[0])))
    return out


def test_a_seen_level_quote_prices_at_its_pinned_value_on_both_paths() -> None:
    assert GOLDEN, "the goldens are computed from origin/main and pinned here"
    assert compute() == GOLDEN
