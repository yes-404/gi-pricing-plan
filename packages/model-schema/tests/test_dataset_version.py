"""`DatasetVersion`'s envelope fields and object forms (OQ-568, decided (c))."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

import pydantic
import pytest

from model_schema import (
    DatasetKind,
    DatasetStatus,
    DatasetVersion,
    DerivedFrom,
    PeriodCovered,
    SourceFingerprint,
)


def _version(**kwargs: object) -> DatasetVersion:
    values: dict[str, object] = {
        "id": uuid4(),
        "dataset_id": uuid4(),
        "workspace_id": uuid4(),
        "slug": "motor-gb",
        "version": 1,
        "status": DatasetStatus.DRAFT,
        "created_at": datetime(2026, 8, 26, tzinfo=UTC),
        "created_by": uuid4(),
        "updated_at": datetime(2026, 8, 26, tzinfo=UTC),
        **kwargs,
    }
    return DatasetVersion(**values)  # type: ignore[arg-type]


@pytest.mark.req("FR-34")
def test_the_version_carries_its_envelope_inline() -> None:
    version = _version(
        description="Q3 exposure",
        parent_id=uuid4(),
        archived_at=datetime(2026, 8, 26, 12, tzinfo=UTC),
        labels={"region": "uk"},
        schema_version=2,
    )
    assert version.slug == "motor-gb"
    assert version.description == "Q3 exposure"
    assert version.schema_version == 2
    assert version.labels == {"region": "uk"}
    assert version.currency == "GBP"


def test_a_malformed_slug_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="slug"):
        _version(slug="Motor_GB")


@pytest.mark.req("FR-4")
def test_updated_at_is_required() -> None:
    """OQ-553, resolved (a): an artifact is created and updated in the same moment,
    so a missing `updated_at` is a malformed version, not a never-updated one."""
    with pytest.raises(pydantic.ValidationError, match="updated_at"):
        _version(updated_at=None)


@pytest.mark.req("FR-73")
def test_period_covered_is_an_ordered_pair() -> None:
    version = _version(
        period_covered={"from": date(2023, 1, 1), "to": date(2026, 6, 30)}
    )
    assert version.period_covered == PeriodCovered(from_=date(2023, 1, 1), to=date(2026, 6, 30))
    assert version.period_covered.from_ == date(2023, 1, 1)


@pytest.mark.req("FR-73")
def test_an_inverted_period_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="precedes"):
        _version(period_covered={"from": date(2026, 6, 30), "to": date(2023, 1, 1)})


@pytest.mark.req("FR-73")
def test_a_period_without_an_end_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="to"):
        _version(period_covered={"from": date(2023, 1, 1)})


def test_source_fingerprint_requires_the_extraction_moment() -> None:
    """A fingerprint without `extracted_at` cannot answer "was this file re-ingested
    after its contents changed?" — OQ-568 (c) made the object form carry it."""
    with pytest.raises(pydantic.ValidationError, match="extracted_at"):
        _version(source_fingerprint={"kind": "file_sha256", "value": "a" * 64})
    ok = _version(
        source_fingerprint=SourceFingerprint(
            kind="file_sha256",
            value="a" * 64,
            extracted_at=datetime(2026, 8, 26, tzinfo=UTC),
        )
    )
    assert ok.source_fingerprint is not None
    assert ok.source_fingerprint.value == "a" * 64


def test_the_fingerprint_kind_is_closed() -> None:
    with pytest.raises(pydantic.ValidationError, match="kind"):
        _version(
            source_fingerprint={
                "kind": "md5",
                "value": "a" * 64,
                "extracted_at": datetime(2026, 8, 26, tzinfo=UTC),
            }
        )


@pytest.mark.req("FR-73")
def test_a_derived_version_names_its_parent_and_operation() -> None:
    version = _version(
        kind=DatasetKind.DERIVED,
        derived_from=DerivedFrom(
            parent_version_id=uuid4(),
            operation="split",
            params={"method": "temporal", "part": "train"},
        ),
    )
    assert version.derived_from is not None
    assert version.derived_from.operation == "split"
    assert version.derived_from.params == {"method": "temporal", "part": "train"}


@pytest.mark.req("FR-73")
def test_a_derived_version_without_derived_from_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="derived_from"):
        _version(kind=DatasetKind.DERIVED)


def test_the_derivation_operation_is_closed() -> None:
    with pytest.raises(pydantic.ValidationError, match="operation"):
        _version(
            kind=DatasetKind.DERIVED,
            derived_from={"parent_version_id": uuid4(), "operation": "merge"},
        )


@pytest.mark.req("FR-46")
def test_a_validated_version_must_name_its_report() -> None:
    with pytest.raises(pydantic.ValidationError, match="validation report"):
        _version(status=DatasetStatus.VALIDATED)
