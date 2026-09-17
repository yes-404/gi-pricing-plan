"""FR-55's derived fields, and the pairs that must not come apart."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pydantic
import pytest

from model_schema import Dataset, DatasetStatus


def _dataset(**kwargs: object) -> Dataset:
    return Dataset(
        id=uuid4(),
        workspace_id=uuid4(),
        slug="motor-gb",
        owner_id=uuid4(),
        created_at=datetime(2026, 8, 23, tzinfo=UTC),
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.mark.req("FR-55")
def test_a_dataset_with_no_versions_carries_neither_field() -> None:
    dataset = _dataset()
    assert dataset.latest_version is None
    assert dataset.latest_version_status is None
    assert dataset.last_validated_at is None
    assert dataset.last_validated_version is None


@pytest.mark.req("FR-55")
def test_the_two_fields_may_name_different_versions() -> None:
    """The case the requirement was written for: a fresh draft above a validated version.

    A Dataset in this state must render a `draft` badge *and* a last-validated date, and
    must say the date belongs to v11 — otherwise the pair reads as one fact and the badge
    appears to contradict the date.
    """
    dataset = _dataset(
        latest_version=12,
        latest_version_status=DatasetStatus.DRAFT,
        last_validated_at=datetime(2026, 8, 20, tzinfo=UTC),
        last_validated_version=11,
    )
    assert dataset.latest_version != dataset.last_validated_version
    assert dataset.latest_version_status is DatasetStatus.DRAFT


@pytest.mark.req("FR-55")
def test_a_status_without_the_version_it_describes_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="latest_version"):
        _dataset(latest_version_status=DatasetStatus.VALIDATED)


@pytest.mark.req("FR-55")
def test_a_version_without_its_status_is_refused() -> None:
    """Both directions. A caller that batched the version numbers and forgot the statuses
    would otherwise render a blank badge for every row — which is exactly the defect
    `_latest_versions`' docstring records the list already had once."""
    with pytest.raises(pydantic.ValidationError, match="latest_version_status"):
        _dataset(latest_version=12)


@pytest.mark.req("FR-55")
def test_a_validation_date_without_its_version_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="last_validated_version"):
        _dataset(
            latest_version=11,
            latest_version_status=DatasetStatus.VALIDATED,
            last_validated_at=datetime(2026, 8, 20, tzinfo=UTC),
        )


@pytest.mark.req("FR-55")
def test_a_validated_version_without_its_date_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="last_validated_at"):
        _dataset(
            latest_version=11,
            latest_version_status=DatasetStatus.VALIDATED,
            last_validated_version=11,
        )


@pytest.mark.req("FR-82")
def test_owner_name_is_optional_and_unresolved_by_default() -> None:
    """OQ-552 (a): the resolved name is a derived field, and `None` is an honest answer.

    A projection that never resolved the id must still construct — the list renders the raw
    id as its fallback. The default (rather than a required parameter) is what lets every
    existing caller keep working while the resolving routes pass the name.
    """
    assert _dataset().owner_name is None
    assert _dataset(owner_name="Demo Analyst").owner_name == "Demo Analyst"
