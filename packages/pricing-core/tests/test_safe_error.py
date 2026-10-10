"""`safe_error_text`: an ALLOW-list of exception text (NFR-499, RL-917).

An exception's text is kept only where it is ours and known to be input-free: a coded error
(`CODE: message`), and a Pydantic `ValidationError` rebuilt from its declared field names, its
error types, its constraint bounds and, for the listed fixed-text types only, its `msg`. Anything
else is its type name. Each test plants a sentinel where the input would be and checks it is
absent; the controls check what an operator needs (the field, the type, the bound) is present.
"""

from __future__ import annotations

import enum
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal

import polars as pl
import pytest
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)
from test_rating_score import _compiled
from test_rating_score_batch import _contexts, _ctx_to_row

from model_schema.input_free import InputFreeError, identifier
from pricing_core.rating.score import _batch_error_code, score_batch
from pricing_core.safe_error import (
    _AUTHORED_TEXT,
    _FIXED_TEXT_TYPES,
    CodedError,
    safe_error_detail,
    safe_error_text,
    safe_exc_info,
    safe_validation_message,
)

_SENTINEL = "SENTINEL-quote-input-b81e4f27"


class _Colour(enum.Enum):
    RED = "red"
    BLUE = "blue"


class _Inner(BaseModel):
    n: int


def _cases() -> dict[str, tuple[type[BaseModel], dict[str, Any]]]:
    """One (model, bad input) per fixed-text error type. Where the input can be a string the
    sentinel is the input; where it cannot (a number that breaks a bound) the input's own text
    is what must not appear."""

    def model(**fields: Any) -> type[BaseModel]:
        from pydantic import create_model

        return create_model("_Case", **fields)

    return {
        "missing": (model(a=(int, ...)), {}),
        "extra_forbidden": (
            create_forbid(),
            {"a": 1, _SENTINEL: 2},
        ),
        "int_type": (model(a=(int, ...)), {"a": [_SENTINEL]}),
        "int_parsing": (model(a=(int, ...)), {"a": _SENTINEL}),
        "float_type": (model(a=(float, ...)), {"a": [_SENTINEL]}),
        "float_parsing": (model(a=(float, ...)), {"a": _SENTINEL}),
        "string_type": (model(a=(str, ...)), {"a": [_SENTINEL]}),
        "bool_type": (model(a=(bool, ...)), {"a": [_SENTINEL]}),
        "bool_parsing": (model(a=(bool, ...)), {"a": _SENTINEL}),
        "decimal_type": (model(a=(Decimal, ...)), {"a": [_SENTINEL]}),
        "decimal_parsing": (model(a=(Decimal, ...)), {"a": _SENTINEL}),
        "decimal_max_digits": (
            model(a=(Annotated[Decimal, Field(max_digits=2)], ...)),
            {"a": "99999"},
        ),
        "date_type": (model(a=(date, ...)), {"a": [_SENTINEL]}),
        "date_from_datetime_parsing": (model(a=(date, ...)), {"a": _SENTINEL}),
        "datetime_type": (model(a=(datetime, ...)), {"a": [_SENTINEL]}),
        "datetime_from_date_parsing": (model(a=(datetime, ...)), {"a": _SENTINEL}),
        "literal_error": (model(a=(Literal["x", "y"], ...)), {"a": _SENTINEL}),
        "enum": (model(a=(_Colour, ...)), {"a": _SENTINEL}),
        "string_pattern_mismatch": (
            model(a=(Annotated[str, Field(pattern="^[a-z]{3}$")], ...)),
            {"a": _SENTINEL},
        ),
        "string_too_long": (
            model(a=(Annotated[str, Field(max_length=3)], ...)),
            {"a": _SENTINEL},
        ),
        "string_too_short": (model(a=(Annotated[str, Field(min_length=99)], ...)), {"a": "s"}),
        "greater_than": (model(a=(Annotated[int, Field(gt=10)], ...)), {"a": 10}),
        "greater_than_equal": (model(a=(Annotated[int, Field(ge=10_000_000)], ...)), {"a": 123456}),
        "less_than": (model(a=(Annotated[int, Field(lt=10)], ...)), {"a": 987654321}),
        "less_than_equal": (model(a=(Annotated[int, Field(le=10)], ...)), {"a": 987654321}),
        "too_short": (
            model(a=(Annotated[list[str], Field(min_length=3)], ...)),
            {"a": [_SENTINEL]},
        ),
        "too_long": (
            model(a=(Annotated[list[str], Field(max_length=1)], ...)),
            {"a": [_SENTINEL, _SENTINEL]},
        ),
        "list_type": (model(a=(list[int], ...)), {"a": _SENTINEL}),
        "dict_type": (model(a=(dict[str, int], ...)), {"a": _SENTINEL}),
        "model_type": (model(a=(_Inner, ...)), {"a": _SENTINEL}),
    }


def create_forbid() -> type[BaseModel]:
    from pydantic import create_model

    return create_model("_Forbid", __config__=ConfigDict(extra="forbid"), a=(int, ...))


def _failure(model: type[BaseModel], data: dict[str, Any]) -> ValidationError:
    with pytest.raises(ValidationError) as caught:
        model.model_validate(data)
    return caught.value


@pytest.mark.req("NFR-499")
def test_every_listed_fixed_text_type_has_a_case_and_leaks_no_input() -> None:
    cases = _cases()
    assert set(cases) == set(_FIXED_TEXT_TYPES), "a listed type without a case, or a case unlisted"
    for error_type, (model, data) in cases.items():
        exc = _failure(model, data)
        assert error_type in {e["type"] for e in exc.errors()}, f"{error_type}: not produced"
        detail = safe_error_detail(exc)
        assert f"[{error_type}]" in detail, (error_type, detail)
        assert _SENTINEL not in detail, (error_type, detail)
        for number in ("987654321", "123456", "99999"):
            assert number not in detail, (error_type, detail)


class _Checked(BaseModel):
    a: int

    @field_validator("a")
    @classmethod
    def _positive(cls, value: int) -> int:
        raise ValueError(f"the value {_SENTINEL} is not acceptable")


class _Asserting(BaseModel):
    a: str

    @field_validator("a")
    @classmethod
    def _check(cls, value: str) -> str:
        assert value == "ok", f"expected ok, got {value}"
        return value


class _Cat(BaseModel):
    kind: Literal["cat"]


class _Dog(BaseModel):
    kind: Literal["dog"]


class _Pets(BaseModel):
    pet: Annotated[_Cat | _Dog, Field(discriminator="kind")]


class _Linked(BaseModel):
    url: AnyUrl


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    ("error_type", "model", "data", "echo"),
    [
        ("value_error", _Checked, {"a": 1}, "not acceptable"),
        ("assertion_error", _Asserting, {"a": _SENTINEL}, "expected ok"),
        ("union_tag_invalid", _Pets, {"pet": {"kind": _SENTINEL}}, "does not match any"),
        ("url_parsing", _Linked, {"url": _SENTINEL}, "valid URL"),
    ],
)
def test_a_type_outside_the_allow_list_keeps_its_type_and_drops_its_message(
    error_type: str, model: type[BaseModel], data: dict[str, Any], echo: str
) -> None:
    exc = _failure(model, data)
    assert error_type not in _FIXED_TEXT_TYPES
    assert _SENTINEL in str(exc) or echo in str(exc), "control: the raw text carries the message"
    detail = safe_error_detail(exc)
    assert f"[{error_type}]" in detail
    assert _SENTINEL not in detail
    assert echo not in detail, "the message of an unlisted type was kept"


class _Authored(BaseModel):
    family: str

    @field_validator("family")
    @classmethod
    def _refuse(cls, value: str) -> str:
        if value == "authored":
            raise InputFreeError("a Poisson model must declare an offset")
        raise ValueError(f"unacceptable family {value}")


class _RefusedIdentifier(BaseModel):
    step: str

    @field_validator("step")
    @classmethod
    def _name(cls, value: str) -> str:
        raise InputFreeError(
            "step {step} is refused", step=identifier(value, r"[a-z][a-z0-9_]*")
        )


@pytest.mark.req("NFR-499")
def test_an_input_free_validator_message_is_kept_and_an_interpolating_one_is_not() -> None:
    kept = safe_error_detail(_failure(_Authored, {"family": "authored"}))
    assert "family: [value_error] Value error, a Poisson model must declare an offset" in kept
    dropped_exc = _failure(_Authored, {"family": _SENTINEL})
    assert _SENTINEL in str(dropped_exc), "control: the raw text carries the value"
    dropped = safe_error_detail(dropped_exc)
    assert _SENTINEL not in dropped
    assert "family: [value_error]" in dropped
    assert "unacceptable" not in dropped


@pytest.mark.req("NFR-499")
def test_safe_validation_message_keeps_fixed_text_and_the_marker_only() -> None:
    (authored,) = _failure(_Authored, {"family": "authored"}).errors()
    (plain,) = _failure(_Authored, {"family": _SENTINEL}).errors()
    assert safe_validation_message(authored) == authored["msg"]
    assert safe_validation_message(plain) is None
    assert safe_validation_message(
        {"type": "int_parsing", "msg": "Input should be a valid integer"}
    ) == ("Input should be a valid integer")
    assert safe_validation_message({"type": "recursion_loop", "msg": _SENTINEL}) is None
    assert safe_validation_message({"type": "union_tag_invalid", "msg": _SENTINEL}) == (
        _AUTHORED_TEXT["union_tag_invalid"]
    )
    # A CodedError is not on the allow-list of a validation message (DP-3 (a) with DP-5 (b)).
    assert safe_validation_message(
        {"type": "value_error", "msg": _SENTINEL, "ctx": {"error": CodedError("X: y")}}
    ) is None


@pytest.mark.req("NFR-499")
def test_a_marker_identifier_that_fails_its_pattern_is_not_echoed() -> None:
    """DP-8 (b), acceptance 12: the constructor refuses it, and the refusal is a plain
    ValueError, so neither the allow-list nor the stored detail carries the value."""
    exc = _failure(_RefusedIdentifier, {"step": _SENTINEL})
    (error,) = exc.errors()
    assert not isinstance(error["ctx"]["error"], InputFreeError)
    assert safe_validation_message(error) is None
    assert _SENTINEL not in safe_error_detail(exc)


def _authored_cases() -> dict[str, tuple[type[BaseModel], str | bytes, bool]]:
    """One (model, input, from-json) per _AUTHORED_TEXT type. Where the input can be a string
    the sentinel is the input; where it cannot, the input's own text is what must not appear."""
    from datetime import date as date_
    from datetime import datetime as datetime_
    from decimal import Decimal as Decimal_
    from uuid import UUID

    from pydantic import create_model

    def one(**fields: Any) -> type[BaseModel]:
        return create_model("_Case", **fields)

    return {
        "json_invalid": (one(a=(int, ...)), b'{"a": "' + _SENTINEL.encode(), True),
        # `date_parsing` and `datetime_parsing` arise only from strict JSON validation
        # (`validate_json`); a lax body, which is what FastAPI validates, gives
        # `date_from_datetime_parsing` / `datetime_from_date_parsing`, already fixed-text types.
        "date_parsing": (one(a=(date_, Field(strict=True))), '{"a": "' + _SENTINEL + '"}', True),
        "date_from_datetime_inexact": (one(a=(date_, ...)), '{"a": "2026-01-31T09:30:11"}', True),
        "datetime_parsing": (
            one(a=(datetime_, Field(strict=True))),
            '{"a": "' + _SENTINEL + '"}',
            True,
        ),
        "uuid_parsing": (one(a=(UUID, ...)), '{"a": "' + _SENTINEL + '"}', True),
        "uuid_type": (one(a=(UUID, ...)), '{"a": 987654321}', True),
        "union_tag_invalid": (_Pets, '{"pet": {"kind": "' + _SENTINEL + '"}}', True),
        "union_tag_not_found": (_Pets, '{"pet": {"nokind": "' + _SENTINEL + '"}}', True),
        "int_from_float": (one(a=(int, ...)), '{"a": 123456.5}', True),
        "decimal_max_places": (
            one(a=(Decimal_, Field(decimal_places=2))),
            '{"a": "123456.789"}',
            True,
        ),
    }


@pytest.mark.req("NFR-499")
def test_every_authored_text_type_has_a_case_and_leaks_no_input() -> None:
    cases = _authored_cases()
    assert set(cases) == set(_AUTHORED_TEXT), "a listed type without a case, or a case unlisted"
    assert not set(_AUTHORED_TEXT) & _FIXED_TEXT_TYPES, "one allow-list entry per type"
    for error_type, (model, data, _) in cases.items():
        with pytest.raises(ValidationError) as caught:
            model.model_validate_json(data)
        exc = caught.value
        assert error_type in {e["type"] for e in exc.errors()}, f"{error_type}: not produced"
        detail = safe_error_detail(exc)
        assert f"[{error_type}] {_AUTHORED_TEXT[error_type]}" in detail, (error_type, detail)
        for echoed in (_SENTINEL, "987654321", "123456", "09:30:11", "99999"):
            assert echoed not in detail, (error_type, echoed, detail)
        assert _AUTHORED_TEXT[error_type] == safe_validation_message(
            next(e for e in exc.errors() if e["type"] == error_type)
        )


class _Bag(BaseModel):
    model_config = ConfigDict(extra="forbid")
    inputs: dict[str, int]
    a: int = 0


@pytest.mark.req("NFR-499")
def test_a_dict_key_and_an_extra_key_in_the_location_are_replaced_by_a_placeholder() -> None:
    exc = _failure(_Bag, {"inputs": {_SENTINEL: "not-an-int"}, _SENTINEL + "-extra": 1})
    raw = str(exc.errors(include_input=False))
    assert _SENTINEL in raw, "control: the raw location carries the key"
    detail = safe_error_detail(exc)
    assert _SENTINEL not in detail
    assert "inputs.<key>: [int_parsing]" in detail
    assert "<key>: [extra_forbidden]" in detail
    assert "inputs" in detail


@pytest.mark.req("NFR-499")
def test_a_list_index_and_a_declared_field_name_are_kept_and_bounds_are_shown() -> None:
    class Quote(BaseModel):
        driver_age: Annotated[int, Field(ge=17, le=99)]
        nested: list[int] = []

    exc = _failure(Quote, {"driver_age": 5, "nested": [1, _SENTINEL]})
    detail = safe_error_detail(exc)
    assert _SENTINEL not in detail
    assert "driver_age: [greater_than_equal] ge=17" in detail
    assert "nested[1]: [int_parsing]" in detail


@pytest.mark.req("NFR-499")
def test_a_coded_error_keeps_its_text_and_anything_else_is_its_type_only() -> None:
    coded = CodedError("INPUT_CONTRACT_VIOLATION: input 'channel' is not in ['direct', 'broker']")
    assert safe_error_text(coded) == f"ValueError: {coded}"
    assert _batch_error_code(coded) == (
        "INPUT_CONTRACT_VIOLATION",
        "input 'channel' is not in ['direct', 'broker']",
    )
    assert safe_error_text(RuntimeError(_SENTINEL)) == "RuntimeError"
    assert safe_error_text(ValueError("the dataset has no exposure column")) == "ValueError"
    assert safe_error_text(KeyError(_SENTINEL)) == "KeyError"
    assert _batch_error_code(ValueError(_SENTINEL)) == ("ValueError", "ValueError")
    with pytest.raises(pl.exceptions.ComputeError) as caught:
        pl.DataFrame([{"q": {"secret": _SENTINEL}}, {"q": _SENTINEL}])
    assert _SENTINEL in str(caught.value), "control: the library's own text carries the value"
    assert safe_error_text(caught.value) == "ComputeError"


@pytest.mark.req("NFR-499")
def test_the_batch_error_code_for_a_validation_error_is_safe() -> None:
    class Quote(BaseModel):
        driver_age: int

    code, message = _batch_error_code(_failure(Quote, {"driver_age": _SENTINEL}))
    assert code == "ValidationError"
    assert _SENTINEL not in message
    assert "driver_age: [int_parsing]" in message


@pytest.mark.req("NFR-499")
def test_the_logged_traceback_keeps_the_frames_and_ends_in_the_safe_text() -> None:
    class Quote(BaseModel):
        driver_age: int

    try:
        Quote.model_validate({"driver_age": _SENTINEL})
    except ValidationError as exc:
        rendered = logging.Formatter().formatException(safe_exc_info(exc))
    assert _SENTINEL not in rendered
    assert "test_the_logged_traceback_keeps_the_frames" in rendered
    assert "driver_age" in rendered


@pytest.mark.req("NFR-499")
async def test_a_nested_quote_id_does_not_fail_the_frame_build_and_leaks_nothing() -> None:
    """The error row copies the raw `quote_id`. A struct-valued one made `pl.DataFrame(rows,
    schema=...)` raise `ComputeError: could not append value: {"..."} ...`, echoing the value
    into an exception outside the per-row isolation. It is now stringified, so the frame
    builds and the batch scores."""
    compiled = await _compiled()
    rows = [_ctx_to_row(c) for c in _contexts(2)]
    for row in rows:
        row["quote_id"] = {"id": row["quote_id"], "secret": _SENTINEL}
    out = score_batch(compiled, pl.DataFrame(rows).lazy()).collect()
    assert out.height == 2
    assert out["quote_id"].dtype == pl.String
    # `QuoteContext` rejects a nested id, per row, and that message carries no value either.
    assert _SENTINEL not in "".join(m or "" for m in out["error_message"].to_list())


@pytest.mark.req("NFR-499")
def test_a_coded_looking_error_that_is_not_ours_is_reduced_to_its_type() -> None:
    """Recognition is by class, not by the shape of the text: a library's `ValueError("FOO:
    secret")` looks coded and is not."""
    foreign = ValueError(f"FOO: {_SENTINEL}")
    assert safe_error_text(foreign) == "ValueError"
    assert _batch_error_code(foreign) == ("ValueError", "ValueError")
    spoof = ValueError(f"INPUT_CONTRACT_VIOLATION: {_SENTINEL}")  # a real code, not our class
    assert safe_error_text(spoof) == "ValueError"
    assert _batch_error_code(spoof) == ("ValueError", "ValueError")
    genuine = CodedError("INPUT_CONTRACT_VIOLATION: input 'channel' is not in ['direct']")
    assert _batch_error_code(genuine) == (
        "INPUT_CONTRACT_VIOLATION", "input 'channel' is not in ['direct']"
    )
    assert safe_error_text(RuntimeError(f"MODEL_CALL_FAILED: {_SENTINEL}")) == "RuntimeError"
    ours = CodedError("FOO: a fixed sentence")
    assert safe_error_text(ours) == "ValueError: FOO: a fixed sentence"
    assert isinstance(ours, ValueError), "existing `except ValueError` handling is unchanged"


@pytest.mark.req("NFR-499")
async def test_a_coded_error_does_not_carry_the_exception_it_replaced() -> None:
    """`_raise_named` raises `from None`: the exception being handled (`fromisoformat`'s, whose
    text repeats the value; the engine's) is not the coded error's context."""
    compiled = await _compiled()
    rows = [_ctx_to_row(c) for c in _contexts(1)]
    rows[0]["effective_date"] = _SENTINEL
    from pricing_core.rating.score import _row_to_ctx

    with pytest.raises(CodedError) as caught:
        _row_to_ctx(rows[0])
    assert caught.value.__suppress_context__ is True
    assert _SENTINEL not in str(caught.value)
    assert compiled is not None

    from pricing_core.rating.score import _reraise_engine_failure

    algorithm = compiled.algorithm
    def _handled() -> None:
        try:
            raise RuntimeError(f"engine says {_SENTINEL}")
        except RuntimeError as engine:
            _reraise_engine_failure(algorithm, engine)

    with pytest.raises(CodedError) as engine_caught:
        _handled()
    assert engine_caught.value.__suppress_context__ is True
    assert _SENTINEL not in str(engine_caught.value)

