"""The `Job` shape (`07` §4.1)."""

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

import pytest
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from model_schema.input_free import InputFreeError
from model_schema.jobs import Job, JobError, JobErrorLocation


def _queued_job(**extra: Any) -> Job:
    return Job.model_validate(
        {
            "id": uuid4(),
            "workspace_id": uuid4(),
            "kind": "dataset.ingest",
            "status": "queued",
            "queue": "compute",
            "submitted_by": {"kind": "system"},
            "source": "system",
            "queued_at": datetime(2026, 9, 29, tzinfo=UTC),
            **extra,
        }
    )


@pytest.mark.req("FR-18")
def test_job_platform_build_defaults_to_none() -> None:
    assert _queued_job().platform_build is None


@pytest.mark.req("FR-18")
def test_job_platform_build_round_trips() -> None:
    build = "0.1.0+97b15726b1dd60ba407c6aba44735ad5cbe207ed"
    job = _queued_job(platform_build=build)
    assert job.platform_build == build
    assert Job.model_validate_json(job.model_dump_json()).platform_build == build


def _failed_error(**extra: Any) -> JobError:
    return JobError.model_validate(
        {"code": "RATING_STEP_INVALID", "message": "refused", "retryable": False, **extra}
    )


@pytest.mark.req("FR-403")
def test_job_error_location_defaults_to_none_and_old_rows_validate() -> None:
    # A row stored before `location` existed has no such key.
    assert _failed_error().location is None


@pytest.mark.req("FR-403")
def test_job_error_location_round_trips_by_equality() -> None:
    located = {"step_id": "s_rp", "field": "feature_map.age", "ref": "model:freq@2"}
    error = _failed_error(location=located)
    dumped = error.model_dump(mode="json")
    assert dumped["location"] == {
        "step_id": "s_rp",
        "field": "feature_map.age",
        "ref": "model:freq@2",
        "objective": None,
        "structure": None,
        "factor": None,
        "key": None,
        "feature": None,
        "interaction": None,
        "operand": None,
        "peril": None,
    }
    assert JobError.model_validate_json(error.model_dump_json()) == error


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("step_id", "42"),
        ("step_id", "0.05"),
        ("key", "42"),
        ("peril", "AD"),
    ],
)
def test_job_error_location_admits_a_digit_string_the_grammar_cannot_tell_from_an_id(
    key: str, value: str
) -> None:
    """The grammar is the source field's (DP-2), not a "no number" rule: a digit string passes
    (kept out by the raise sites alone), while the same value as a JSON number is refused."""
    assert _failed_error(location={key: value}).location is not None
    with pytest.raises(ValidationError):
        _failed_error(location={key: 7})


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(
    "location",
    [
        {},  # empty: points nowhere
        {"value": "42"},  # a key outside the declared set
        {"step_id": 42},  # a number is never a location value
        {"step_id": ""},  # the source field's own `min_length=1`
        {"ref": "not-a-reference"},  # outside REF_PATTERN, the wire form of an ArtifactRef
        {"structure": "not-a-reference"},
        {"peril": "has a space"},  # outside `PerilCode`
    ],
)
def test_job_error_location_refuses_what_it_must_never_carry(location: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _failed_error(location=location)


#: The values of the review of #1930, point 3 (7 cases over 6 keys, `step_id` has two): each is a
#: valid value of its source field and a location refused it, so a raise site that built one lost
#: its code.
_SOURCE_FIELD_VALUES = [
    ("step_id", "base premium"),
    ("step_id", "s" * 129),
    ("interaction", "VehAge & DrivAge"),
    ("feature", "Veh Age"),
    ("key", "Driver Age"),
    ("objective", "reg:tweedie"),
    ("factor", "vehicle_group_rated"),
]


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(("key", "value"), _SOURCE_FIELD_VALUES)
def test_a_location_is_never_narrower_than_the_field_it_names(key: str, value: str) -> None:
    assert getattr(JobErrorLocation(**{key: value}), key) == value


#: `JobError` as it stood at origin/main 5564a6d1 (`packages/model-schema/src/model_schema/jobs.py`
#: lines 174-188), the version a rolling deploy or a rollback still runs (`07` NFR-531). Held here
#: as a frozen copy, not imported: the proof is that THIS head's stored rows pass a reader that
#: has no `location`.
class _PreviousJobError(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern="^[A-Z][A-Z0-9_]*$")
    message: str
    retryable: bool
    detail: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = Field(default=None, pattern="^[0-9a-f]{32}$")


_LOCATED = {"step_id": "base premium", "field": "inputs.age", "ref": "model:freq@2"}


def test_the_wire_dump_is_refused_by_the_previous_version_so_it_is_not_what_is_stored() -> None:
    """The control: the wire shape carries `location`, which the previous reader refuses."""
    for location in (None, _LOCATED):
        wire = _failed_error(location=location).model_dump(mode="json")
        with pytest.raises(ValidationError, match="extra_forbidden"):
            _PreviousJobError.model_validate(wire)


@pytest.mark.req("NFR-531")
@pytest.mark.parametrize("location", [None, _LOCATED])
@pytest.mark.parametrize("detail", [{}, {"kind": "model.fit"}, {"round": 1.5}])
def test_a_stored_row_is_readable_by_the_previous_version(
    location: dict[str, str] | None, detail: dict[str, Any]
) -> None:
    error = _failed_error(location=location, detail=detail)
    previous = _PreviousJobError.model_validate(error.stored_form())
    assert (previous.code, previous.message, previous.retryable) == (
        "RATING_STEP_INVALID",
        "refused",
        False,
    )
    assert "location" not in error.stored_form()
    if location is None:
        assert previous.detail == detail
    else:
        assert previous.detail == {**detail, "_location": location}


@pytest.mark.req("NFR-531")
@pytest.mark.parametrize("location", [None, _LOCATED, *({k: v} for k, v in _SOURCE_FIELD_VALUES)])
def test_the_stored_form_lifts_back_to_the_same_error_and_the_key_leaves_detail(
    location: dict[str, str] | None,
) -> None:
    error = _failed_error(location=location, detail={"kind": "model.fit"})
    stored = json.loads(json.dumps(error.stored_form()))  # through JSON, as the column is
    lifted = JobError.from_stored(stored)
    assert lifted == error
    assert "_location" not in lifted.detail
    assert JobError.from_stored(lifted.model_dump(mode="json")) == lifted  # a wire dump too


@pytest.mark.req("NFR-531")
def test_a_row_stored_before_location_existed_lifts_to_no_location() -> None:
    old = {"code": "X_Y", "message": "m", "retryable": False, "detail": {}, "trace_id": None}
    assert JobError.from_stored(old) == JobError.model_validate(old)
    assert JobError.from_stored(old).location is None


@pytest.mark.req("NFR-531")
@pytest.mark.parametrize("bad", [{"step_id": 42}, {"nope": "x"}, {}, "text", 7, None])
def test_an_invalid_stored_location_never_raises_and_lifts_to_none(bad: Any) -> None:
    stored = {"code": "X_Y", "message": "m", "retryable": False, "detail": {"_location": bad}}
    lifted = JobError.from_stored(stored)
    assert lifted.location is None
    assert "_location" not in lifted.detail


@pytest.mark.req("NFR-531")
def test_the_constructor_refuses_the_reserved_key_so_only_from_stored_consumes_it() -> None:
    with pytest.raises(ValidationError):
        _failed_error(detail={"_location": {"step_id": "s"}})
    with pytest.raises(ValidationError):
        JobError.model_validate_json(
            '{"code": "X_Y", "message": "m", "retryable": false, "detail": {"_location": {}}}'
        )


@pytest.mark.req("NFR-531")
def test_a_failing_fold_keeps_the_code_and_stores_no_location(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_: Any, **__: Any) -> Any:
        raise RuntimeError("fold failed")

    error = _failed_error(location=_LOCATED)
    monkeypatch.setattr(JobErrorLocation, "model_dump", boom)
    stored = error.stored_form()
    assert stored["code"] == "RATING_STEP_INVALID"
    assert "_location" not in stored["detail"]
    assert "location" not in stored
    _PreviousJobError.model_validate(stored)


# -- the two JSON schemas ------------------------------------------------------------------

_CONTRACTS = Path(__file__).resolve().parents[3] / "docs" / "contracts" / "schemas"


def _refusals(schema: dict[str, Any], value: Any, defs: dict[str, Any], at: str = "$") -> list[str]:
    """The JSON Schema keywords the two Job contracts use, and no others: `$ref`, `anyOf`,
    `type`, `properties`, `additionalProperties: false`, `required`, `pattern`, `maxLength`,
    `minLength`. There is no `jsonschema` in the workspace, and a new dependency is not this
    change's to add. Returns the places `value` is refused."""
    if "$ref" in schema:
        return _refusals(defs[schema["$ref"].rsplit("/", 1)[1]], value, defs, at)
    if "anyOf" in schema:
        options = [_refusals(option, value, defs, at) for option in schema["anyOf"]]
        return [] if any(not refused for refused in options) else [f"{at}: no anyOf arm"]
    types = schema.get("type")
    kinds = {"string": str, "object": dict, "boolean": bool, "null": type(None), "integer": int}
    if types is not None:
        allowed = [types] if isinstance(types, str) else types
        if not any(isinstance(value, kinds[t]) for t in allowed):
            return [f"{at}: {type(value).__name__} is not {allowed}"]
    out: list[str] = []
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            out.append(f"{at}: pattern")
        if len(value) > schema.get("maxLength", len(value)):
            out.append(f"{at}: maxLength")
        if len(value) < schema.get("minLength", 0):
            out.append(f"{at}: minLength")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        out += [f"{at}.{k}: required" for k in schema.get("required", []) if k not in value]
        if schema.get("additionalProperties") is False:
            out += [f"{at}.{k}: not declared" for k in value if k not in properties]
        for key, sub in properties.items():
            if key in value:
                out += _refusals(sub, value[key], defs, f"{at}.{key}")
    return out


def _wire_refusals(schema_file: str, error: dict[str, Any]) -> list[str]:
    schema = json.loads((_CONTRACTS / schema_file).read_text())
    return _refusals(schema["properties"]["error"], error, schema.get("$defs", {}))


def test_the_schema_walker_is_not_blind_to_a_null_in_a_string_only_key() -> None:
    """The control: it refuses what the hand-authored schema used to, so a pass means something."""
    schema = {"type": ["object", "null"], "properties": {"step_id": {"type": "string"}}}
    assert _refusals(schema, {"step_id": None}, {})


@pytest.mark.req("FR-403")
@pytest.mark.parametrize("schema", ["job.schema.json", "generated/job.schema.json"])
@pytest.mark.parametrize("location", [None, _LOCATED, *({k: v} for k, v in _SOURCE_FIELD_VALUES)])
def test_both_job_schemas_accept_the_error_the_api_sends(
    schema: str, location: dict[str, str] | None
) -> None:
    """Every location key the API does not set goes on the wire as `null`: the hand-authored
    schema typed each key `"string"` and refused a located error (review of #1930, point 2)."""
    wire = _failed_error(location=location).model_dump(mode="json")
    assert _wire_refusals(schema, wire) == []


@pytest.mark.req("FR-403")
@pytest.mark.parametrize("schema", ["job.schema.json", "generated/job.schema.json"])
@pytest.mark.parametrize(
    ("key", "bad"),
    [
        ("ref", "not-a-reference"),
        ("structure", "not-a-reference"),
        ("peril", "has a space"),
        ("step_id", ""),
        ("step_id", 42),
        ("nope", "x"),
    ],
)
def test_both_real_job_schemas_refuse_a_located_error_with_a_bad_value(
    schema: str, key: str, bad: Any
) -> None:
    """The control on the real files: a walker that stopped descending into `location` would
    pass the test above and fail this one."""
    wire = _failed_error(location=_LOCATED).model_dump(mode="json")
    wire["location"][key] = bad
    refused = _wire_refusals(schema, wire)
    assert refused, (schema, key, bad)


# -- the free-text keys: a bound, a character rule, and the same answer in every consumer -------

_FREE_TEXT_KEYS = (
    "step_id", "field", "objective", "factor", "key", "feature", "interaction", "operand",
)
_TOO_LONG = "a location key is longer than 256 characters"
_CONTROL = "a location key holds a control character"


def _the_literal_refusal(key: str, value: str) -> str:
    """The `InputFreeError` text a refused value gives: read from the error's own context, never
    from `str()` of the `ValidationError`, which also prints the input."""
    with pytest.raises(ValidationError) as refused:
        JobErrorLocation(**{key: value})
    (error,) = refused.value.errors()
    assert error["loc"] == (key,)
    assert error["type"] == "value_error"
    assert isinstance(error["ctx"]["error"], InputFreeError)
    return str(error["ctx"]["error"])


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("key", _FREE_TEXT_KEYS)
def test_a_free_text_location_key_is_bounded_and_the_refusal_is_a_literal(key: str) -> None:
    longest = "x" * 256
    assert getattr(JobErrorLocation(**{key: longest}), key) == longest
    sentinel = "SENTINEL-" + "x" * 300  # a 5,000-character value was stored before the bound
    text = _the_literal_refusal(key, sentinel)
    assert text == _TOO_LONG
    assert "SENTINEL" not in text


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("key", _FREE_TEXT_KEYS)
@pytest.mark.parametrize("bad", ["a\nb", "a\tb", "a\x00b", "a\x7fb", "a\x85b", "a\u2028b"])
def test_a_free_text_location_key_refuses_a_control_character_with_a_literal(
    key: str, bad: str
) -> None:
    assert _the_literal_refusal(key, "SENTINEL" + bad) == _CONTROL


def test_the_refusal_text_names_the_modules_bound() -> None:
    from model_schema import jobs

    assert str(jobs.LOCATION_TEXT_MAX) in _TOO_LONG


#: ONE table of strings and whether a free-text location key admits each, fed to every consumer of
#: the rule: the model, the hand-authored schema, the generated schema and a second regex engine
#: (the Rust one pydantic uses for `pattern`). `"a\n"` is the trap: Python's `$` matches before a
#: final newline and ECMA 262's does not, so the check translates a trailing `$` (see
#: `_ecma_search`). Length is in code points on every side: a 256-character astral string is
#: admitted, a 257-character one is not.
_ADMITTED = [
    ("s", True),
    ("base premium", True),
    ("VehAge & DrivAge", True),
    ("reg:tweedie", True),
    ("feature_map.age", True),
    ("café", True),
    ("\u00a0x", True),
    ("x" * 256, True),
    ("\U0001f600" * 256, True),
    ("x" * 257, False),
    ("\U0001f600" * 257, False),
    ("", False),
    ("a\n", False),
    ("a\nb", False),
    ("a\tb", False),
    ("a\x00b", False),
    ("a\x1fb", False),
    ("a\x7fb", False),
    ("a\x9fb", False),
    ("a\u2028b", False),
    ("a\u2029b", False),
]


def _text_rules(schema_file: str, key: str) -> dict[str, Any]:
    schema = json.loads((_CONTRACTS / schema_file).read_text())
    if schema_file.startswith("generated/"):  # pydantic's shape: `$defs`, and `anyOf` for `| None`
        rules = schema["$defs"]["JobErrorLocation"]["properties"][key]["anyOf"][0]
    else:
        rules = schema["properties"]["error"]["properties"]["location"]["properties"][key]
    assert {"minLength", "maxLength", "pattern"} <= rules.keys(), (
        f"{schema_file} states no bound or no character rule for {key}: {rules}"
    )
    return rules


def _ecma_search(pattern: str, value: str) -> bool:
    """`re.search` with ECMA 262's end anchor: its `$` (no `m` flag) matches only at the end."""
    if pattern.endswith("$") and not pattern.endswith("\\$"):
        pattern = pattern[:-1] + r"\Z"
    return re.search(pattern, value) is not None


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("key", _FREE_TEXT_KEYS)
@pytest.mark.parametrize("schema", ["job.schema.json", "generated/job.schema.json"])
def test_the_schemas_and_the_model_admit_the_same_free_text(schema: str, key: str) -> None:
    rules = _text_rules(schema, key)
    engine = TypeAdapter(Annotated[str, Field(pattern=rules["pattern"])])
    for value, admitted in _ADMITTED:
        try:
            JobErrorLocation(**{key: value})
            by_the_model = True
        except ValidationError:
            by_the_model = False
        in_bounds = rules["minLength"] <= len(value) <= rules["maxLength"]
        by_the_schema = in_bounds and _ecma_search(rules["pattern"], value)
        try:
            engine.validate_python(value)
            by_the_engine = in_bounds
        except ValidationError:
            by_the_engine = False
        assert (by_the_model, by_the_schema, by_the_engine) == (admitted,) * 3, (
            schema, key, ascii(value[:8]), len(value),
        )


@pytest.mark.req("NFR-499")
def test_the_two_schemas_state_one_bound_and_one_pattern_for_every_free_text_key() -> None:
    stated = {
        (schema, key): tuple(
            _text_rules(schema, key)[word] for word in ("minLength", "maxLength", "pattern")
        )
        for schema in ("job.schema.json", "generated/job.schema.json")
        for key in _FREE_TEXT_KEYS
    }
    assert len(set(stated.values())) == 1, stated
    from model_schema import jobs

    assert next(iter(stated.values())) == (1, jobs.LOCATION_TEXT_MAX, jobs.LOCATION_TEXT_PATTERN)


# -- a stored location that cannot be read: dropped, with one warning -----------------------------

_SENTINEL = "SENTINEL-location-value-5c1e"


def _stored_with(location: Any) -> dict[str, Any]:
    return {
        "code": "X_Y", "message": "m", "retryable": False, "detail": {"_location": location},
    }


@pytest.mark.req("FR-403")
def test_an_invalid_stored_location_is_dropped_with_one_warning_naming_the_job_and_no_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    job_id = uuid4()
    bad = {"step_id": _SENTINEL + "\n", "ref": "not-a-ref", "undeclared_key": _SENTINEL}
    with caplog.at_level(logging.WARNING, logger="model_schema.jobs"):
        lifted = JobError.from_stored(_stored_with(bad), job_id=job_id)
    assert lifted.location is None
    assert "_location" not in lifted.detail
    records = [r for r in caplog.records if r.name == "model_schema.jobs"]
    assert len(records) == 1, [r.getMessage() for r in records]
    text = records[0].getMessage()
    assert records[0].levelno == logging.WARNING
    assert str(job_id) in text
    assert "step_id" in text
    assert "ref" in text
    assert "undeclared:1" in text
    assert "undeclared_key" not in text
    assert _SENTINEL not in text


@pytest.mark.req("FR-403")
@pytest.mark.parametrize("bad", ["a string", 7, {}])
def test_a_stored_location_that_is_no_mapping_or_names_no_key_warns_with_no_keys(
    bad: Any, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="model_schema.jobs"):
        assert JobError.from_stored(_stored_with(bad), job_id=uuid4()).location is None
    records = [r for r in caplog.records if r.name == "model_schema.jobs"]
    assert len(records) == 1
    assert "keys=(none)" in records[0].getMessage()


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(
    "stored",
    [_stored_with({"step_id": "s"}), {"code": "X_Y", "message": "m", "retryable": False}],
)
def test_a_readable_or_absent_stored_location_logs_nothing(
    stored: dict[str, Any], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.DEBUG, logger="model_schema.jobs"):
        JobError.from_stored(stored, job_id=uuid4())
    assert [r for r in caplog.records if r.name == "model_schema.jobs"] == []
