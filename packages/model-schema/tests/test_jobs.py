"""The `Job` shape (`07` §4.1)."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from model_schema.jobs import Job


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
