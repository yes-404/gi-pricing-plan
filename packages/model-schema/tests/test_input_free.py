"""`InputFreeError` and `identifier` (NFR-499; PL-1599 DP-8 (b), acceptance 12): a marker message
may name an identifier of the submitted artifact's own structure only when it matches the field's
own schema pattern; the constructor refuses anything else without echoing it."""

from __future__ import annotations

import re

import pytest

from model_schema.input_free import InputFreeError, identifier

_SENTINEL = "SENTINEL-input-free-7d3a91c4"
_SLUG = r"[a-z][a-z0-9-]*"


@pytest.mark.req("NFR-499")
def test_a_literal_message_is_kept_byte_for_byte() -> None:
    assert str(InputFreeError("a Poisson model must declare an offset (FR-111).")) == (
        "a Poisson model must declare an offset (FR-111)."
    )


@pytest.mark.req("NFR-499")
def test_braces_in_a_literal_message_stay_as_written() -> None:
    text = "an artifact reference must have the form {type}:{slug}@{version}"
    assert str(InputFreeError(text)) == text


@pytest.mark.req("NFR-499")
def test_an_identifier_that_matches_its_pattern_appears_in_the_message() -> None:
    error = InputFreeError("band {name} is empty", name=identifier("young-drivers", _SLUG))
    assert str(error) == "band 'young-drivers' is empty"
    assert isinstance(error, ValueError)


@pytest.mark.req("NFR-499")
def test_an_identifier_that_fails_its_pattern_is_refused_and_not_echoed() -> None:
    with pytest.raises(ValueError, match="did not match its pattern") as caught:
        InputFreeError("band {name} is empty", name=identifier(_SENTINEL, _SLUG))
    assert not isinstance(caught.value, InputFreeError)
    assert _SENTINEL not in str(caught.value)
    assert _SENTINEL not in repr(caught.value)
    assert re.fullmatch(r"[a-z ,.()-]+", str(caught.value)), "a literal message"


@pytest.mark.req("NFR-499")
def test_a_pattern_must_match_the_whole_value() -> None:
    with pytest.raises(ValueError, match="did not match its pattern") as caught:
        InputFreeError("band {name} is empty", name=identifier("ok-then ??? SENTINEL", _SLUG))
    assert "SENTINEL" not in str(caught.value)


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    "bad",
    [_SENTINEL, f"{_SENTINEL}:motor-ad@1", f"model:{_SENTINEL}@1", f"model:motor-ad@{_SENTINEL}"],
)
def test_a_refused_artifact_reference_does_not_echo_what_was_submitted(bad: str) -> None:
    """The rewritten `ArtifactRef` messages name the rule, not the value (PL-1599 Task 3)."""
    from pydantic import TypeAdapter, ValidationError

    from model_schema import ArtifactRef

    with pytest.raises(ValueError, match="artifact") as parsed:
        ArtifactRef.parse(bad)
    assert _SENTINEL not in str(parsed.value)
    with pytest.raises(ValidationError) as validated:
        TypeAdapter(ArtifactRef).validate_python(bad)
    for error in validated.value.errors():
        assert _SENTINEL not in error["msg"]
        assert isinstance(error.get("ctx", {}).get("error", InputFreeError("x")), InputFreeError)


@pytest.mark.req("NFR-499")
def test_the_module_level_helpers_do_not_echo_their_argument() -> None:
    from model_schema import builtin_rule, role_permissions

    for refuse in (builtin_rule, role_permissions):
        with pytest.raises(InputFreeError) as raised:
            refuse(_SENTINEL)  # type: ignore[operator]
        assert _SENTINEL not in str(raised.value)
