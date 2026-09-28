"""`safe_error_text`: exception text with no input value in it (NFR-499, RL-917).

A Pydantic `ValidationError`'s `str()` prints every failing `input_value`; this keeps the
field path, the message and the error type. A database error is recognised by shape, an `orig`
driver exception beside a `statement`, because this package imports no database library, and
is reduced to the driver's type, SQLSTATE and constraint. Anything else is its own text.
"""

from __future__ import annotations

import logging

import pytest
from pydantic import BaseModel, ValidationError

from pricing_core.rating.score import _batch_error_code
from pricing_core.safe_error import safe_error_detail, safe_error_text, safe_exc_info

_SENTINEL = "SENTINEL-quote-input-b81e4f27"


class _Quote(BaseModel):
    driver_age: int
    nested: list[int] = []


def _failure(**extra: object) -> ValidationError:
    with pytest.raises(ValidationError) as caught:
        _Quote.model_validate({"driver_age": _SENTINEL, **extra})
    return caught.value


@pytest.mark.req("NFR-499")
def test_a_validation_errors_text_drops_the_value_and_keeps_the_path_and_type() -> None:
    exc = _failure(nested=[1, _SENTINEL])
    assert _SENTINEL in str(exc), "control: the raw text carries the input"
    text = safe_error_text(exc)
    assert _SENTINEL not in text
    assert text.startswith("ValidationError: 2 validation error(s) for _Quote: ")
    assert "driver_age: " in text
    assert "int_parsing" in text
    assert "nested.1: " in text, "a nested location is kept as a dotted path"


@pytest.mark.req("NFR-499")
def test_the_batch_error_code_uses_the_safe_text_and_keeps_the_named_convention() -> None:
    code, message = _batch_error_code(_failure())
    assert code == "ValidationError"
    assert _SENTINEL not in message
    assert "driver_age" in message
    # `CODE: message` is still parsed back into its parts, unchanged.
    assert _batch_error_code(ValueError("INPUT_CONTRACT_VIOLATION: premium_in is null")) == (
        "INPUT_CONTRACT_VIOLATION",
        "premium_in is null",
    )
    assert _batch_error_code(ValueError("plain")) == ("ValueError", "plain")


class _DriverError(Exception):
    sqlstate = "23514"
    constraint_name = "ck_scoring_traces_blob_sha256_format"


class _StatementError(Exception):
    """The shape of SQLAlchemy's `StatementError` family: an `orig` beside a `statement`."""

    def __init__(self, orig: Exception) -> None:
        super().__init__(
            f"({orig}) [parameters: ('{_SENTINEL}',)] Failing row contains ({_SENTINEL})"
        )
        self.orig = orig
        self.statement = "INSERT INTO t VALUES ($1)"


@pytest.mark.req("NFR-499")
def test_a_database_errors_text_is_the_driver_type_sqlstate_and_constraint_only() -> None:
    exc = _StatementError(_DriverError(f"Failing row contains ({_SENTINEL})"))
    assert _SENTINEL in str(exc), "control: the raw text carries the value"
    text = safe_error_text(exc)
    assert _SENTINEL not in text
    assert text == (
        "_StatementError: _DriverError, sqlstate 23514, "
        "constraint ck_scoring_traces_blob_sha256_format"
    )


@pytest.mark.req("NFR-499")
def test_any_other_exception_keeps_its_own_text() -> None:
    assert safe_error_text(ValueError("the dataset has no exposure column")) == (
        "ValueError: the dataset has no exposure column"
    )
    assert safe_error_detail(KeyError("k")) == str(KeyError("k"))


@pytest.mark.req("NFR-499")
def test_the_logged_traceback_keeps_the_frames_and_ends_in_the_safe_text() -> None:
    try:
        _Quote.model_validate({"driver_age": _SENTINEL})
    except ValidationError as exc:
        rendered = logging.Formatter().formatException(safe_exc_info(exc))
    assert _SENTINEL not in rendered
    assert "test_the_logged_traceback_keeps_the_frames" in rendered
    assert "driver_age" in rendered
