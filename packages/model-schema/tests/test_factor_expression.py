"""The `expression` Factor's field and validator arm, and a Banding over an expression.

`RL-1615` (WK-690 Slice 4, `SL-1274`): `Factor` gains `expression`, `banding_id` is allowed
on `banding` **and** `expression`, and a `Banding` is cut over **either** a dataset column
**or** the text of an `expression` Factor's formula (`source_expression`) — exactly one.
`PL-1665` 4.1' lists the shapes. Each test is red first, by its cause: `expression` and
`source_expression` do not exist on the types today, so the types refuse them as extras.
"""

from __future__ import annotations

from uuid import uuid4

import pydantic
import pytest

from model_schema import Banding, BandingMethod, BandingProposal, Factor, FactorType

DATASET = uuid4()


def _expression_factor(**over: object) -> Factor:
    base: dict[str, object] = {
        "id": uuid4(),
        "slug": "age_x_power",
        "dataset_id": DATASET,
        "version": 1,
        "type": FactorType.EXPRESSION,
        "source_columns": ("driver_age", "vehicle_power"),
        "expression": "driver_age * vehicle_power",
    }
    base.update(over)
    return Factor(**base)  # type: ignore[arg-type]


def _banding(**over: object) -> Banding:
    base: dict[str, object] = {
        "id": uuid4(),
        "slug": "age-x-power-bands",
        "dataset_id": DATASET,
        "version": 1,
        "method": BandingMethod.MANUAL,
        "boundaries": (0.0, 500.0, 1000.0, 9999.0),
        "labels": ("low", "mid", "high"),
    }
    base.update(over)
    return Banding(**base)  # type: ignore[arg-type]


def _require_the_new_fields() -> None:
    """The first assert of every test: the cause this slice removes, stated where it fails.

    `PL-1665` 4.1' / 4.3': `Factor.expression` and `Banding.source_expression` do not exist
    yet, so the helpers below cannot build the input. Asserting the fields first puts the
    red at the test's own assert, so a later partial fix cannot turn a test green (or move
    its red elsewhere) for a reason other than the behaviour it names.
    """
    assert "expression" in Factor.model_fields, (
        "PL-1665 4.1': Factor must carry `expression` (FR-95)"
    )
    assert "source_expression" in Banding.model_fields, (
        "PL-1665 4.1': Banding must carry `source_expression` (FR-97)"
    )


@pytest.mark.req("FR-95")
def test_an_expression_factor_carries_its_expression_text() -> None:
    """`02` §4.1: the text is stored on the Factor, so it is declared, versioned and audited."""
    _require_the_new_fields()
    factor = _expression_factor()
    assert factor.expression == "driver_age * vehicle_power"
    assert factor.type is FactorType.EXPRESSION


@pytest.mark.req("FR-95")
def test_an_expression_factor_without_an_expression_is_refused() -> None:
    """The same state as a `banding` with no Banding: a name with no transformation behind it."""
    _require_the_new_fields()
    with pytest.raises(pydantic.ValidationError, match="names no expression"):
        _expression_factor(expression=None)


@pytest.mark.req("FR-95")
def test_a_non_expression_factor_that_names_an_expression_is_refused() -> None:
    """Nothing would evaluate it, and a formula on an artifact that ignores it reads as used."""
    _require_the_new_fields()
    with pytest.raises(pydantic.ValidationError, match="names an expression"):
        Factor(
            id=uuid4(),
            slug="age",
            dataset_id=DATASET,
            version=1,
            type=FactorType.IDENTITY,
            source_columns=("driver_age",),
            expression="driver_age * 2",
        )


@pytest.mark.req("FR-95")
def test_an_expression_factor_declares_the_columns_it_reads() -> None:
    """FR-95's "over dataset columns only": the declared set is `source_columns`, never empty."""
    _require_the_new_fields()
    with pytest.raises(pydantic.ValidationError, match="source_columns"):
        _expression_factor(source_columns=())


@pytest.mark.req("FR-97")
def test_banding_id_is_allowed_on_an_expression_factor_and_still_only_on_two_types() -> None:
    """`RL-1615` DP-S4-1 (a2): the Banding is how a numeric result becomes categorical."""
    _require_the_new_fields()
    pinned = uuid4()
    assert _expression_factor(banding_id=pinned).banding_id == pinned
    with pytest.raises(pydantic.ValidationError, match="names a banding_id"):
        Factor(
            id=uuid4(),
            slug="g",
            dataset_id=DATASET,
            version=1,
            type=FactorType.IDENTITY,
            source_columns=("driver_age",),
            banding_id=pinned,
        )


@pytest.mark.req("FR-97")
def test_a_banding_is_cut_over_a_column_or_over_an_expression_never_both_or_neither() -> None:
    """`RL-1615` DP-S4-1: "Exactly one of `Banding.column` and `Banding.source_expression`"."""
    _require_the_new_fields()
    over_expression = _banding(source_expression="driver_age * vehicle_power")
    assert over_expression.source_expression == "driver_age * vehicle_power"
    assert over_expression.column is None

    over_column = _banding(column="driver_age")
    assert over_column.source_expression is None

    with pytest.raises(pydantic.ValidationError, match="exactly one"):
        _banding(column="driver_age", source_expression="driver_age * 2")
    with pytest.raises(pydantic.ValidationError, match="exactly one"):
        _banding()


@pytest.mark.req("FR-95")
def test_an_expression_text_is_bounded_on_all_three_carriers() -> None:
    """A text is stored and echoed, so it is bounded as `Objective.loss` is (`max_length=2000`).

    The boundary: 2000 characters are accepted and 2001 are refused, on the Factor's
    `expression`, the Banding's `source_expression` and the proposal's `source_expression`.
    """
    _require_the_new_fields()
    at_limit = "driver_age" + " + 1" * 497  # 10 + 4 * 497 = 1998 chars, then padded to 2000
    at_limit = at_limit + " " * (2000 - len(at_limit))
    assert len(at_limit) == 2000
    too_long = at_limit + " "
    assert len(too_long) == 2001

    assert _expression_factor(expression=at_limit).expression == at_limit
    with pytest.raises(pydantic.ValidationError, match="at most 2000"):
        _expression_factor(expression=too_long)

    assert _banding(source_expression=at_limit).source_expression == at_limit
    with pytest.raises(pydantic.ValidationError, match="at most 2000"):
        _banding(source_expression=too_long)

    version = uuid4()
    method = BandingMethod.EQUAL_WIDTH
    accepted = BandingProposal(
        dataset_version_id=version, method=method, source_expression=at_limit
    )
    assert accepted.source_expression == at_limit
    with pytest.raises(pydantic.ValidationError, match="at most 2000"):
        BandingProposal(dataset_version_id=version, method=method, source_expression=too_long)
