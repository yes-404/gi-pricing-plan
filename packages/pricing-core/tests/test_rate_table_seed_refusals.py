"""The seed-from-model refusals are coded and name identifiers, never a value (#1712 row 3).

`seed_from_model` refuses with a `CodedError` (the allow-list's marker), so the API keeps the text
through the unchanged `_map_operation_error` fallback instead of redacting it to the type name.
The text names only identifiers: a Factor slug the Model stores (through `repr`, cut at
`FACTOR_NAME_CAP` and marked when cut), the model family@version, a fit kind or a count; a name
that exists only in the caller's request and is not in the Model is shown only when the factor slug
grammar admits it, and is otherwise counted. Never a cell value. The sites are accounted for in
`test_quote_input_raise_sites._INPUT_FREE` (maintainer 2026-11-15, S7 STOP #2 (a)).
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from test_rate_table_operations import _REGION_LEVELS, _TWO_FACTORS, _factor, _glm_model, _seed

from model_schema.modelling import Factor, FactorIntent, FactorType, ModelStatus
from pricing_core.rate_tables.operations import FACTOR_NAME_CAP, seed_from_model
from pricing_core.safe_error import CodedError

_SENTINEL = "SENTINEL-request-name-9d2c"


@pytest.mark.req("NFR-499")
def test_a_long_stored_factor_slug_is_cut_and_marked_in_a_refusal() -> None:
    """A name the Model stores is named as stored, through `repr`, but never past the cap: a
    longer one is cut and the cut is marked."""
    slug = "R" * (FACTOR_NAME_CAP + 136)
    model = _glm_model(ModelStatus.APPROVED, relativities={slug: _REGION_LEVELS})
    with pytest.raises(ValueError, match="outside the factor slug grammar") as caught:
        _seed(model, slug, [_factor(slug)])
    text = str(caught.value)
    assert repr("R" * FACTOR_NAME_CAP) in text, "control: the head of the name is still shown"
    assert slug not in text
    assert f"cut at {FACTOR_NAME_CAP} of {len(slug)} characters" in text
    assert isinstance(caught.value, CodedError), "the allow-list keeps a CodedError's text"


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("name", [_SENTINEL, "Bad Name!", "X" * 300])
def test_a_requested_factor_name_outside_the_grammar_is_counted_not_shown(name: str) -> None:
    """A name that exists only in the caller's request, and is not in the Model, is named only
    when it matches the factor slug grammar (#1827 (b)); otherwise it is counted."""
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    with pytest.raises(ValueError, match="names no relativity entry") as caught:
        _seed(model, name, [_factor("region")])
    text = str(caught.value)
    assert name not in text
    assert name[:8] not in text
    assert "1 requested factor name outside the factor slug grammar" in text
    assert isinstance(caught.value, CodedError), "the allow-list keeps a CodedError's text"


@pytest.mark.req("NFR-499")
def test_a_stored_relativity_entry_with_no_pinned_factor_is_named_with_the_cap() -> None:
    """The entry is the Model's own name (it passed the first check), so it is shown through
    `_named`: a well-formed one in full, a long one cut and marked."""
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    with pytest.raises(ValueError, match="no pinned Factor with slug 'region'") as caught:
        _seed(model, "region", [])
    assert isinstance(caught.value, CodedError)
    long_slug = "L" * (FACTOR_NAME_CAP + 10)
    long_model = _glm_model(ModelStatus.APPROVED, relativities={long_slug: _REGION_LEVELS})
    with pytest.raises(ValueError, match="no pinned Factor") as long_caught:
        _seed(long_model, long_slug, [])
    assert long_slug not in str(long_caught.value)
    assert f"cut at {FACTOR_NAME_CAP} of {len(long_slug)} characters" in str(long_caught.value)


@pytest.mark.req("NFR-499")
def test_a_fit_that_is_not_a_glm_is_refused_by_model_and_kind_as_a_coded_error() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS).model_copy(
        update={"fit_result": None}
    )
    with pytest.raises(ValueError, match="carries a absent fit result") as caught:
        _seed(model, "region", [_factor("region")])
    assert "'motor-ad-frequency'@1" in str(caught.value), "control: the model is named"
    assert isinstance(caught.value, CodedError)


def _crossing(slug: str, *operand_ids, intent: FactorIntent = FactorIntent.RISK) -> Factor:
    return Factor(
        id=uuid4(),
        slug=slug,
        dataset_id=uuid4(),
        version=1,
        type=FactorType.INTERACTION,
        source_columns=(),
        operand_factor_ids=tuple(operand_ids),
        intent=intent,
    )


@pytest.mark.req("FR-88")
@pytest.mark.req("NFR-499")
def test_a_control_factor_in_the_rateable_path_keeps_its_code_and_is_a_coded_error() -> None:
    """The code is in the text already; `CodedError` makes the allow-list keep it by class, not
    by the API's string partition (tidying, not a leak fix)."""
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    control = _factor("region").model_copy(update={"intent": FactorIntent.CONTROL})
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH: ") as caught:
        _seed(model, "region", [control])
    text = str(caught.value)
    assert text.startswith("CONTROL_FACTOR_IN_RATEABLE_PATH: ")
    assert "Factor region@1 has intent 'control'" in text, "the text is unchanged by the class"
    assert isinstance(caught.value, CodedError)


@pytest.mark.req("FR-88")
@pytest.mark.req("NFR-499")
def test_an_interaction_with_an_unsupplied_operand_keeps_its_code_and_is_a_coded_error() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    missing = uuid4()
    cross = _crossing("region", missing, uuid4())  # an interaction crosses two or more Factors
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH: ") as caught:
        _seed(model, "region", [cross])
    text = str(caught.value)
    assert text.startswith("CONTROL_FACTOR_IN_RATEABLE_PATH: ")
    assert "Factor region@1 crosses " in text, "the text is unchanged by the class"
    assert str(missing) in text, "control: the operand id is named"
    assert isinstance(caught.value, CodedError)


def test_the_seed_still_succeeds_for_a_well_formed_factor() -> None:
    """Positive control for the refusals above: the same Model seeds when nothing is wrong."""
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    result = seed_from_model(
        model,
        factor="region",
        factors=[_factor("region")],
        table_slug="motor-relativity",
        change_note="seed",
        seeded_at=datetime(2026, 10, 3, 10, 0, tzinfo=UTC),
    )
    assert result.cells
