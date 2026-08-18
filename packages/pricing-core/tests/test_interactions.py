"""Crossing Factors: the `interaction` arm of FR-MODEL-1 (FR-MODEL-91).

An interaction crosses **Factors**, not columns, so every test here builds its operands
first and pins them by id. That is the whole point of the design: crossing the raw columns
of `driver_age` and `region` gives 60 x 4 cells of one policy each, which is not a rating
structure — crossing `age_banded` with `region_ns` gives six cells an actuary can read.

The refusals matter more than the happy path. A cross resolved wrongly is a design column
with plausible-looking levels and the wrong rows behind them, which is the failure mode
`resolve_factors` exists to refuse for every other type.

**A continuous operand is refused by name** (OQ-MODEL-12). Crossing with one is a varying
*slope*, and `03`'s rating DAG is tables — a product term would fit perfectly well and
would not be rateable. The refusal names the remedy: band it first.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GlmSpec,
    Grouping,
    GroupingMethod,
    OffsetSpec,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import FactorResolutionError, fit_glm, resolve_factors

DATASET = uuid4()


def _book(n: int = 2_000, seed: int = 20260818) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    exposure = rng.uniform(0.5, 1.0, n)
    return pl.DataFrame(
        {
            "driver_age": age,
            "region": rng.choice(["N1", "N2", "S1", "S2"], n),
            "exposure_years": exposure,
            "claim_count": rng.poisson(0.08 * exposure).astype(float),
        }
    )


def _banding() -> Banding:
    return Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1,
        column="driver_age", method=BandingMethod.MANUAL,
        boundaries=(18.0, 38.0, 58.0, 78.0), labels=("18-37", "38-57", "58+"),
    )


def _grouping() -> Grouping:
    return Grouping(
        id=uuid4(), slug="region-ns", dataset_id=DATASET, version=1,
        column="region", method=GroupingMethod.MANUAL,
        mapping={"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH", "S2": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )


def _factor(slug: str, column: str, **over: object) -> Factor:
    base: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": DATASET, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    base.update(over)
    return Factor(**base)  # type: ignore[arg-type]


def _cross(slug: str, *operands: Factor) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=DATASET, version=1,
        type=FactorType.INTERACTION, source_columns=(),
        operand_factor_ids=tuple(f.id for f in operands),
    )


def _age(banding: Banding) -> Factor:
    return _factor(
        "age_banded", "driver_age", type=FactorType.BANDING, banding_id=banding.id
    )


def _region(grouping: Grouping) -> Factor:
    return _factor(
        "region_ns", "region", type=FactorType.GROUPING, grouping_id=grouping.id
    )


# -- the cross itself ----------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-91")
def test_an_interaction_crosses_its_operands_resolved_levels() -> None:
    """The cross is of `18-37` with `NORTH`, never of 23.0 with `N1`."""
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    crossed = _cross("age_x_region", age, region)

    matrix = resolve_factors(
        _book(), [age, region, crossed],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    )
    column = matrix.terms["age_x_region"]
    assert column in matrix.categorical
    assert set(matrix.frame[column].unique().to_list()) == {
        f"{band} | {side}"
        for band in ("18-37", "38-57", "58+")
        for side in ("NORTH", "SOUTH")
    }


@pytest.mark.req("FR-MODEL-91")
def test_an_operand_contributes_no_term_of_its_own() -> None:
    """A full cross spans every cell, so its operands' main effects are collinear with it.

    `fit_glm` designs on every factor it is handed, so without this rule the natural call —
    pass the cross and the operands it needs — would build `age + region + age:region` on a
    combined factor and be rank-deficient. The operands are resolved, because the cross
    needs their levels, and they are not terms.
    """
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    crossed = _cross("age_x_region", age, region)

    matrix = resolve_factors(
        _book(500), [age, region, crossed],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    )
    assert set(matrix.terms) == {"age_x_region"}

    # …and without the cross, both are ordinary terms again.
    plain = resolve_factors(
        _book(500), [age, region],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    )
    assert set(plain.terms) == {"age_banded", "region_ns"}


@pytest.mark.req("FR-MODEL-91")
def test_only_observed_combinations_become_levels() -> None:
    """An empty cell would be a coefficient fitted on nothing — and on a wide cross most
    cells are empty, so this is the ordinary case rather than the corner."""
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    crossed = _cross("age_x_region", age, region)

    book = _book().filter(
        ~((pl.col("driver_age") < 38) & (pl.col("region").is_in(["S1", "S2"])))
    )
    matrix = resolve_factors(
        book, [age, region, crossed],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    )
    levels = set(matrix.frame[matrix.terms["age_x_region"]].unique().to_list())
    assert "18-37 | SOUTH" not in levels
    assert "18-37 | NORTH" in levels


@pytest.mark.req("FR-MODEL-91")
def test_an_interaction_resolves_wherever_it_appears_in_the_sequence() -> None:
    """Operands are looked up by id, so a caller need not order the list — a resolution
    that depended on order would be a fit that depended on it."""
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    crossed = _cross("age_x_region", age, region)

    matrix = resolve_factors(
        _book(500), [crossed, age, region],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    )
    assert matrix.frame[matrix.terms["age_x_region"]].n_unique() == 6


@pytest.mark.req("FR-MODEL-91")
def test_a_three_way_interaction_is_one_factor_over_three_operands() -> None:
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    halves = Banding(
        id=uuid4(), slug="exposure-halves", dataset_id=DATASET, version=1,
        column="exposure_years", method=BandingMethod.MANUAL,
        boundaries=(0.5, 0.75, 1.0), labels=("short", "long"),
    )
    exposure = _factor(
        "exposure_banded", "exposure_years", type=FactorType.BANDING, banding_id=halves.id
    )
    crossed = _cross("three_way", age, region, exposure)

    matrix = resolve_factors(
        _book(3_000), [age, region, exposure, crossed],
        bandings={banding.id: banding, halves.id: halves},
        groupings={grouping.id: grouping},
    )
    sample = matrix.frame[matrix.terms["three_way"]][0]
    assert sample.count("|") == 2, sample


# -- the refusals --------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-91")
def test_an_operand_that_was_not_supplied_is_refused() -> None:
    """The `bandings` map's refusal one level up: resolving the cross without one of its
    sides would produce the other side alone, under the interaction's name."""
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    crossed = _cross("age_x_region", age, region)

    with pytest.raises(FactorResolutionError, match="was not supplied"):
        resolve_factors(
            _book(200), [age, crossed],
            bandings={banding.id: banding}, groupings={grouping.id: grouping},
        )


@pytest.mark.req("FR-MODEL-91")
@pytest.mark.req("FR-MODEL-97")
def test_a_continuous_operand_is_refused_by_name_with_its_remedy() -> None:
    """OQ-MODEL-12, decided 2026-08-18 as FR-MODEL-97 — see the module docstring. A product
    term would fit and would not be rateable, which is the kind of success worth refusing.
    The decision keeps the `diagnostic`-intent variant open, so what this test pins is the
    refusal, not the absence of any future product term."""
    banding = _banding()
    age = _age(banding)
    raw = _factor("exposure_raw", "exposure_years")
    crossed = _cross("age_x_exposure", age, raw)

    with pytest.raises(FactorResolutionError) as refused:
        resolve_factors(
            _book(200), [age, raw, crossed], bandings={banding.id: banding}
        )
    message = str(refused.value)
    assert "exposure_raw" in message
    assert "band" in message.lower()


@pytest.mark.req("FR-MODEL-5")
def test_a_prohibited_operand_is_refused_through_the_cross() -> None:
    """FR-MODEL-5 has to reach *through* the interaction. A prohibited factor that cannot
    enter a spec directly but can enter one crossed with something else is not prohibited.
    """
    banding, grouping = _banding(), _grouping()
    age = _age(banding)
    region = _factor(
        "region_ns", "region", type=FactorType.GROUPING, grouping_id=grouping.id,
        prohibited=True, prohibited_reason="Proxy for a protected characteristic.",
    )
    crossed = _cross("age_x_region", age, region)

    with pytest.raises(FactorResolutionError, match="prohibited"):
        resolve_factors(
            _book(200), [age, region, crossed],
            bandings={banding.id: banding}, groupings={grouping.id: grouping},
        )


@pytest.mark.req("FR-MODEL-91")
def test_an_interaction_of_an_interaction_is_refused() -> None:
    """A three-way interaction is one factor over three operands. Nesting would give two
    names for one design column, and the resolver a cycle to chase."""
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    inner = _cross("age_x_region", age, region)
    outer = _cross("nested", inner, age)

    with pytest.raises(FactorResolutionError, match="three"):
        resolve_factors(
            _book(200), [age, region, inner, outer],
            bandings={banding.id: banding}, groupings={grouping.id: grouping},
        )


# -- the reason interactions exist ---------------------------------------------------------


@pytest.mark.req("FR-MODEL-21")
def test_a_glm_on_a_crossed_factor_recovers_the_cell_rates() -> None:
    """The real assertion, and the reason an interaction exists at all.

    Frequency here depends on age and region **jointly**: the young/NORTH cell runs at
    double what its two main effects predict. Two separate factors cannot represent that
    cell; the crossed factor can, and the fitted cell relativities recover the ratios that
    were built into the book.
    """
    banding, grouping = _banding(), _grouping()
    age, region = _age(banding), _region(grouping)
    crossed = _cross("age_x_region", age, region)

    rng = np.random.default_rng(20260818)
    n = 60_000
    driver_age = rng.integers(18, 78, n).astype(float)
    raw_region = rng.choice(["N1", "N2", "S1", "S2"], n)
    north = np.isin(raw_region, ["N1", "N2"])
    young = driver_age < 38
    rate = 0.05 * (1 + 0.5 * north) * (1 + 0.5 * young) * (1 + 1.0 * (north & young))
    exposure = rng.uniform(0.5, 1.0, n)
    book = pl.DataFrame(
        {
            "driver_age": driver_age,
            "region": raw_region,
            "exposure_years": exposure,
            "claim_count": rng.poisson(rate * exposure).astype(float),
        }
    )

    spec = GlmSpec(
        model_family_slug="crossed",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=(crossed.id,),
    )
    result = fit_glm(
        book, spec, [age, region, crossed],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    ).result

    cells = {row.level: row for row in result.relativities["age_x_region"]}
    assert len(cells) == 6

    built_in = {
        "18-37 | NORTH": 0.05 * 1.5 * 1.5 * 2.0,
        "18-37 | SOUTH": 0.05 * 1.0 * 1.5,
        "38-57 | NORTH": 0.05 * 1.5,
        "38-57 | SOUTH": 0.05,
        "58+ | NORTH": 0.05 * 1.5,
        "58+ | SOUTH": 0.05,
    }
    base = next(row for row in cells.values() if float(row.relativity) == 1.0)
    for level, rate_built in built_in.items():
        expected = rate_built / built_in[base.level]
        got = float(cells[level].relativity)
        assert abs(got - expected) < 0.15, (level, got, expected)
