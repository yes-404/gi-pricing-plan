"""The coded failures a fit or backtest Job stores when a model refuses (FR-2143), without a DB.

A coded Job's error is STORED, and a `PredictionError`'s own text can carry a quote's value
(`rating/runtime.py` passes the code only). So the handler maps a refusal to its code and a FIXED,
value-free sentence, never `str(exc)`.
"""

from __future__ import annotations

import pytest

from app.errors import PlatformError
from app.worker import model_handlers
from pricing_core.modelling.predict import PredictionError

SENTINEL = "SENTINEL-4e8b"


def _refusal() -> PredictionError:
    return PredictionError(
        "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED",
        f"factor 'area' carries the level {SENTINEL!r} that the fitted model never saw",
        terms=["area"],
    )


@pytest.mark.req("FR-2143")
def test_an_offset_refusal_is_its_code_and_a_fixed_sentence_never_the_exception_text() -> None:
    mapped = model_handlers._offset_refusal(_refusal())

    assert isinstance(mapped, PlatformError)
    assert mapped.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert mapped.status_code == 409
    assert mapped.detail == (
        "The offset model could not be scored for this data. Next step: declare “map to base” on "
        "that factor, or re-split the data so that the holdout holds no level the offset model "
        "never saw."
    )
    assert SENTINEL not in f"{mapped.title} {mapped.detail} {mapped}"


@pytest.mark.req("FR-2143")
def test_a_diagnostics_refusal_is_its_code_and_a_fixed_sentence_never_the_exception_text() -> None:
    mapped = model_handlers._diagnostics_refusal(_refusal())

    assert mapped.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert mapped.status_code == 409
    assert mapped.detail is not None
    assert "Declare “map to base” on the factor concerned, or re-split the data." in mapped.detail
    assert SENTINEL not in f"{mapped.title} {mapped.detail} {mapped}"


@pytest.mark.req("FR-2143")
def test_an_all_rows_refusal_carries_the_count_and_the_next_step() -> None:
    """Every row of a partition is excluded: the stored detail names the partition and the COUNT
    and says what to do next; it is built from those alone (never a level or a value).

    This test is the ONLY guard of that. The raise-site census (`test_worker_raise_sites.py`)
    cannot see `detail = str(exc)`: the expression is `detail` either way. So the equality on
    `mapped.detail` below, against a subclass whose text carries a sentinel, is what fails if the
    mapper ever reads the exception's text."""
    from pricing_core.modelling.predict import ALL_ROWS_UNSEEN_TEXT, AllRowsUnseenError

    class SentinelMessageError(AllRowsUnseenError):
        """The same attributes, but an exception text that carries a value."""

        def __str__(self) -> str:
            return f"the level {SENTINEL!r} is unseen"

    mapped = model_handlers._all_rows_refusal(SentinelMessageError(partition="holdout", rows=87))

    assert mapped.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert mapped.status_code == 409
    # the detail is the sentence BUILT from the attributes, and nothing of the exception's text
    assert mapped.detail == ALL_ROWS_UNSEEN_TEXT.format(count=87, partition="holdout")
    assert "every one of the 87 holdout rows" in mapped.detail
    assert "Declare “map to base” on that factor, or re-split the data." in mapped.detail
    assert SENTINEL not in f"{mapped.title} {mapped.detail}"


@pytest.mark.req("FR-2143")
def test_the_code_an_all_rows_refusal_carries_is_registered_and_declared() -> None:
    """The code the error carries is the literal one, a registered modelling code that 02 §5.1
    (and only §5.1: the section is sliced, not the whole file) declares."""
    from pathlib import Path

    from app.errors import MODELLING_ERROR_CODES
    from pricing_core.modelling.predict import AllRowsUnseenError

    literal = "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    error = AllRowsUnseenError(partition="holdout", rows=3)
    code = error.code
    assert code == literal
    assert code in MODELLING_ERROR_CODES
    text = (Path(__file__).resolve().parents[2] / "docs" / "specs" / "02-modelling.md").read_text(
        encoding="utf-8"
    )
    section = text.split("### 5.1 REST API", 1)[1].split("### 5.2 ", 1)[0]
    assert f"`{code}`" in section
    mapped = model_handlers._all_rows_refusal(error)
    assert mapped.code == literal


_STEPS = {
    "MODEL_TERM_UNRESOLVED": "every column the model's factors read",
    "MODEL_OFFSET_MISSING": "the model's exposure column",
    "MODEL_LINK_UNSUPPORTED": "a link the scorer implements",
    "MODEL_NOT_FITTED": "carries no fit to score",
}
_MAPPERS = {"offset": "_offset_refusal", "diagnostics": "_diagnostics_refusal",
            "backtest": "_backtest_refusal"}


def _map(mapper: str, exc: PredictionError) -> model_handlers.PlatformError:
    result: model_handlers.PlatformError = getattr(model_handlers, _MAPPERS[mapper])(exc)
    return result


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize("mapper", sorted(_MAPPERS))
@pytest.mark.parametrize("code", sorted(_STEPS))
def test_a_refusal_code_stores_its_own_next_step_not_the_unseen_level_advice(
    mapper: str, code: str
) -> None:
    """Each code has its own correct next step; none of them says to declare `map_to_base`, and
    the stored detail carries no value from the exception's text."""
    exc = PredictionError(code, f"a term names {SENTINEL!r}", terms=["area"])

    mapped = _map(mapper, exc)

    assert mapped.code == code
    assert mapped.status_code == 409
    assert mapped.detail is not None
    assert _STEPS[code] in mapped.detail
    assert "map to base" not in mapped.detail
    assert SENTINEL not in f"{mapped.title} {mapped.detail}"


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize("mapper", sorted(_MAPPERS))
def test_an_unlisted_refusal_code_gets_the_generic_next_step(mapper: str) -> None:
    mapped = _map(mapper, PredictionError("MODEL_INTERVAL_UNAVAILABLE", f"{SENTINEL!r}"))

    assert mapped.code == "MODEL_INTERVAL_UNAVAILABLE"
    assert mapped.detail is not None
    assert "error code names the refusal." in mapped.detail
    assert "map to base" not in mapped.detail
    assert SENTINEL not in f"{mapped.title} {mapped.detail}"


@pytest.mark.req("FR-2143")
def test_the_backtests_unseen_level_advice_names_the_backtest_data_not_a_holdout() -> None:
    mapped = model_handlers._backtest_refusal(_refusal())
    offset = model_handlers._offset_refusal(_refusal(), where="the backtest data")

    for stored in (mapped.detail, offset.detail):
        assert stored is not None
        assert "backtest data" in stored
        assert "holdout" not in stored
        assert "map to base" in stored


@pytest.mark.req("FR-109")
def test_a_grouping_that_maps_none_is_a_409_naming_the_factor_and_never_a_value() -> None:
    """A fit refusal against the data is 409 like the rest of this module; 422 is the request's
    own shape. The creation-time refusals of a chain stay 422."""
    from pricing_core.modelling import GroupingCoverageError

    exc = GroupingCoverageError(
        "GROUPING_MAPS_NO_VALUE",
        "factor 'region_f' pins grouping 'region'@1 over column 'area', and none of the "
        "column's 200 row(s) is a source level that grouping maps (FR-109).",
    )
    mapped = model_handlers._grouping_refusal(exc, "glm")

    assert mapped.code == "GROUPING_MAPS_NO_VALUE"
    assert mapped.status_code == 409
    assert mapped.detail is not None
    assert "'region_f'" in mapped.detail
    assert SENTINEL not in f"{mapped.title} {mapped.detail} {mapped}"
