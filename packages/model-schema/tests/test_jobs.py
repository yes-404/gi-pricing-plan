"""The `Job` shape (`07` §4.1)."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema.jobs import Job, JobError


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
    "location",
    [
        {},  # empty: points nowhere
        {"value": "42"},  # a key outside the declared set
        {"step_id": 42},  # a number is never a location value
        {"step_id": "has a space"},  # free text
        {"ref": "not-a-reference"},  # outside REF_PATTERN
        {"field": "inputs.age = 42"},  # not a path of identifiers
        {"feature": "age is 42"},
    ],
)
def test_job_error_location_refuses_what_it_must_never_carry(location: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _failed_error(location=location)
