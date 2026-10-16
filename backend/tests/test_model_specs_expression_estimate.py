"""An expression Factor never makes the complexity estimate smaller than the truth.

`02` FR-185's gate refuses a spec whose parameters outrun its exposure. The estimate behind
it sized every factor from `source_columns[0]`, which is right for an identity factor and
under-counts an expression: a formula over two columns can take as many levels as the
columns' combinations. An under-count *weakens a refusal*, so it is a defect and not a
rounding (the maintainer, 2026-10-16 10:42:37, Q1; `LG-8062`).

Pure tests: `complexity_or_refuse` takes the factors and a profile, no database.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.platform.model_specs import complexity_or_refuse
from model_schema import (
    ColumnProfile,
    Factor,
    FactorType,
    Profile,
    SemanticType,
    SpecProblemKind,
)

_DATASET = uuid4()


def _column(name: str, distinct: int, *, nulls: int = 0) -> ColumnProfile:
    return ColumnProfile(
        name=name,
        dtype="string",
        semantic_type=SemanticType.CATEGORICAL,
        row_count=1000,
        null_count=nulls,
        null_rate=nulls / 1000,
        distinct_count=distinct,
    )


def _profile(*columns: ColumnProfile) -> Profile:
    return Profile(
        id=uuid4(),
        dataset_version_id=uuid4(),
        computed_at=datetime(2026, 10, 16, tzinfo=UTC),
        row_count=1000,
        columns=columns,
    )


def _expression(slug: str, sources: tuple[str, ...], formula: str) -> Factor:
    return Factor(
        id=uuid4(),
        slug=slug,
        dataset_id=_DATASET,
        version=1,
        type=FactorType.EXPRESSION,
        source_columns=sources,
        expression=formula,
    )


def _check(factors: list[Factor], profile: Profile | None, *, floor: float | None):
    return complexity_or_refuse(
        factors=factors,
        profile=profile,
        exposure_years=Decimal(1000),
        max_factor_count=None,
        min_exposure_per_parameter=floor,
    )


@pytest.mark.req("FR-185")
def test_a_two_column_expression_is_counted_at_the_product_of_its_columns() -> None:
    """10 x 10 combinations: 99 + the intercept = 100 parameters, not the 10 of column one."""
    factor = _expression("area_make", ("area", "make"), "concat(area, make)")
    profile = _profile(_column("area", 10), _column("make", 10))

    problems, parameters, per_parameter = _check([factor], profile, floor=None)

    assert parameters == 100
    assert per_parameter == pytest.approx(10.0)
    assert problems == []


@pytest.mark.req("FR-185")
def test_a_spec_over_the_limit_only_because_of_an_expression_factor_is_refused() -> None:
    """At 100 parameters the spec has 10.0 per parameter; a floor of 10.5 must refuse it.

    Sized from `source_columns[0]` alone the spec has 10 parameters and 100.0 per
    parameter, passes any floor under 100, and the refusal this test pins never happens.
    """
    factor = _expression("area_make", ("area", "make"), "concat(area, make)")
    profile = _profile(_column("area", 10), _column("make", 10))

    problems, _, _ = _check([factor], profile, floor=10.5)

    assert [p.kind for p in problems] == [SpecProblemKind.COMPLEXITY_LIMIT]
    assert problems[0].subject == "modelling.min_exposure_per_parameter"


@pytest.mark.req("FR-185")
def test_the_same_spec_just_under_the_limit_is_accepted() -> None:
    """The control: 10.0 per parameter against a floor of exactly 10.0 is not below it."""
    factor = _expression("area_make", ("area", "make"), "concat(area, make)")
    profile = _profile(_column("area", 10), _column("make", 10))

    problems, _, _ = _check([factor], profile, floor=10.0)

    assert problems == []


@pytest.mark.req("FR-185")
def test_a_null_in_a_source_column_can_be_a_level_of_the_expression() -> None:
    """`distinct_count` excludes nulls, so a nullable source column contributes one more."""
    factor = _expression("area_make", ("area", "make"), "concat(area, make)")
    profile = _profile(_column("area", 10, nulls=5), _column("make", 10))

    _, parameters, _ = _check([factor], profile, floor=None)

    assert parameters == 11 * 10  # (11 * 10) levels - 1, + the intercept


@pytest.mark.req("FR-185")
def test_an_expression_over_a_column_the_profile_lacks_is_refused_when_a_floor_is_set() -> None:
    """No count means no bound; an unbounded estimate cannot be allowed to pass a gate."""
    factor = _expression("ratio", ("area", "unprofiled"), "concat(area, unprofiled)")
    profile = _profile(_column("area", 10))

    problems, _, _ = _check([factor], profile, floor=1.0)

    assert [p.kind for p in problems] == [SpecProblemKind.COMPLEXITY_LIMIT]
    assert problems[0].subject == "ratio"


@pytest.mark.req("FR-185")
def test_without_a_profile_or_a_floor_the_gate_still_costs_and_refuses_nothing() -> None:
    """`None` is "no gate" (OQ-580): an unbounded expression is not a reason to refuse."""
    factor = _expression("ratio", ("area", "unprofiled"), "concat(area, unprofiled)")

    problems, _, _ = _check([factor], None, floor=None)

    assert problems == []
