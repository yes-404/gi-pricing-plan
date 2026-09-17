"""The Phase 1b rating version shape and its status transitions (OD1, W7-3)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pydantic
import pytest

from model_schema import ArtifactRef, RatingVersion, RatingVersionStatus


def _rating(**over: object) -> RatingVersion:
    fields: dict[str, object] = {
        "id": uuid4(),
        "workspace_id": uuid4(),
        "slug": "fremtpl2-demo",
        "version": 1,
        "status": RatingVersionStatus.DRAFT,
        "dataset_version_id": uuid4(),
        "model_ref": ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
        "created_at": datetime(2026, 8, 27, tzinfo=UTC),
        "created_by": uuid4(),
        "updated_at": datetime(2026, 8, 27, tzinfo=UTC),
    }
    fields.update(over)
    return RatingVersion(**fields)  # type: ignore[arg-type]


@pytest.mark.req("FR-440")
def test_a_rating_version_constructs_in_draft() -> None:
    rating = _rating()
    assert rating.status is RatingVersionStatus.DRAFT
    assert rating.model_ref.type == "model"


@pytest.mark.req("FR-440")
def test_a_rating_version_round_trips_through_every_status() -> None:
    for status in RatingVersionStatus:
        rating = _rating(status=status)
        reloaded = RatingVersion.model_validate(rating.model_dump(mode="json"))
        assert reloaded.status is status


@pytest.mark.req("FR-440")
def test_the_status_must_be_a_member_of_the_closed_set() -> None:
    with pytest.raises(pydantic.ValidationError, match="status"):
        RatingVersion.model_validate(_rating(status="deployed").model_dump(mode="json"))


@pytest.mark.req("FR-440")
def test_the_version_number_is_positive() -> None:
    with pytest.raises(pydantic.ValidationError, match="version"):
        _rating(version=0)
