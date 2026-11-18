"""The `Job` shape (`07` §4.1)."""

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

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
