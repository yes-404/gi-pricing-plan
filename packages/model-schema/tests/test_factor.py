"""The `Factor` type/transformation invariant, and the `interaction` arm (`02` §4.1).

`Factor` has always enforced "a `banding` factor carries a Banding, and only a `banding`
factor does". This file adds the third arm and tests all of it in one place — the invariant
had no direct test at all until now, only `pricing-core`'s resolution suite reaching it
sideways.

**An interaction crosses Factors, not columns.** Everywhere the specification names one it
names factors — §4.4's `interaction_constraints: [["driver_age_banded",
"vehicle_group_rated"]]`, §4.9's `top_interactions` — and crossing raw columns can express
neither. The operands are pinned **by id** for the reason `banding_id` is: a slug changes
meaning the next time someone re-cuts a boundary.

**An interaction sources no columns of its own**, which is why `source_columns` had to stop
being unconditionally non-empty. Its columns are its operands', and listing them again would
be a second statement of one fact — the kind that disagrees eventually. The requirement is
re-imposed per type in the validator, so every other arm is exactly as strict as before and
this one is stricter.
"""

from __future__ import annotations

from uuid import uuid4

import pydantic
import pytest

from model_schema import Factor, FactorType, MonotonicDirection

DATASET = uuid4()
AGE = uuid4()
VEHICLE = uuid4()


def _factor(**over: object) -> Factor:
    fields: dict[str, object] = {
        "id": uuid4(),
        "slug": "driver_age_banded",
        "dataset_id": DATASET,
        "version": 1,
        "type": FactorType.IDENTITY,
        "source_columns": ("driver_age",),
    }
    fields.update(over)
    return Factor(**fields)  # type: ignore[arg-type]


def _interaction(**over: object) -> Factor:
    fields: dict[str, object] = {
        "slug": "age_x_vehicle",
        "type": FactorType.INTERACTION,
        "source_columns": (),
        "operand_factor_ids": (AGE, VEHICLE),
    }
    fields.update(over)
    return _factor(**fields)


# -- the interaction arm -------------------------------------------------------------------


@pytest.mark.req("FR-83")
def test_an_interaction_round_trips() -> None:
    factor = _interaction()
    assert Factor.model_validate(factor.model_dump(mode="json")) == factor


@pytest.mark.req("FR-83")
def test_an_interaction_naming_no_operands_is_refused() -> None:
    """The same argument as a `banding` factor with no Banding: without them the factor is
    a name with no transformation behind it."""
    with pytest.raises(pydantic.ValidationError, match="operand_factor_ids"):
        _interaction(operand_factor_ids=())


@pytest.mark.req("FR-83")
def test_an_interaction_of_one_factor_is_refused() -> None:
    """A cross of one is that factor. Allowing it would put two names in every model
    document for one design column, and the relativity table could not say which."""
    with pytest.raises(pydantic.ValidationError, match="two"):
        _interaction(operand_factor_ids=(AGE,))


@pytest.mark.req("FR-83")
def test_an_interaction_with_a_repeated_operand_is_refused() -> None:
    """`age x age` is `age`, with every off-diagonal cell empty by construction."""
    with pytest.raises(pydantic.ValidationError, match="more than once"):
        _interaction(operand_factor_ids=(AGE, AGE))


@pytest.mark.req("FR-83")
def test_an_interaction_cannot_cross_itself() -> None:
    me = uuid4()
    with pytest.raises(pydantic.ValidationError, match="itself"):
        _interaction(id=me, operand_factor_ids=(AGE, me))


@pytest.mark.req("FR-83")
def test_an_interaction_sources_no_columns_of_its_own() -> None:
    """Its columns are its operands'. Naming them again is a second statement of one fact,
    and the two disagree the first time an operand is re-versioned onto another column."""
    with pytest.raises(pydantic.ValidationError, match="source_columns"):
        _interaction(source_columns=("driver_age", "vehicle_group"))


@pytest.mark.req("FR-83")
def test_operands_on_a_non_interaction_factor_are_refused() -> None:
    """The other half of the invariant, which the banding and grouping arms already have:
    a field nothing applies reads as a transformation the model used."""
    with pytest.raises(pydantic.ValidationError, match="operand_factor_ids"):
        _factor(operand_factor_ids=(AGE, VEHICLE))


# -- the arms that already existed, now tested directly ------------------------------------


@pytest.mark.req("FR-83")
def test_a_banding_factor_without_its_banding_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="banding_id"):
        _factor(type=FactorType.BANDING)


@pytest.mark.req("FR-83")
def test_a_grouping_id_on_an_identity_factor_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="grouping_id"):
        _factor(grouping_id=uuid4())


@pytest.mark.req("FR-83")
def test_every_other_type_still_requires_a_source_column() -> None:
    """Relaxing the field-level `min_length=1` for the interaction arm must not relax it
    for anything else — so the rule moved into the validator rather than being dropped."""
    for kind in (FactorType.IDENTITY, FactorType.SPLINE, FactorType.EXPRESSION):
        with pytest.raises(pydantic.ValidationError, match="source_columns"):
            _factor(type=kind, source_columns=())


@pytest.mark.req("FR-90")
def test_a_prohibition_still_needs_its_reason() -> None:
    with pytest.raises(pydantic.ValidationError, match="reason"):
        _factor(prohibited=True)


@pytest.mark.req("FR-89")
def test_a_monotonic_direction_still_needs_its_rationale() -> None:
    with pytest.raises(pydantic.ValidationError, match="rationale"):
        _factor(monotonic_direction=MonotonicDirection.DECREASING)
