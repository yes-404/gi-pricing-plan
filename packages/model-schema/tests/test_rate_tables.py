"""FR-RATE-14, FR-RATE-15, FR-RATE-21, FR-RATE-62: rate table contracts and invariants.

W10-1 adds RateTable and RateTableVersion to model-schema. These tests verify the shapes
parse correctly, immutability invariants hold, and storage mode is fixed at write time.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import FrozenInstanceError, ValidationError

from model_schema.rating import (
    RateTable,
    RateTableKey,
    RateTableValue,
    RateTableVersion,
)
from model_schema.refs import ArtifactRef


@pytest.mark.req("FR-RATE-14")
class TestRateTableShape:
    """A Rate Table declares keys, a value column, optional default row, and storage mode."""

    def test_rate_table_parses_with_required_fields(self):
        """A valid RateTable has slug, version, rateable, storage, keys, value."""
        table = RateTable(
            slug="vehicle-age",
            version=1,
            rateable=True,
            storage="rows",
            keys=[
                RateTableKey(name="age", type="int", banding_ref=None),
            ],
            value=RateTableValue(
                name="relativity",
                type="relativity",
                unit="factor",
                min=Decimal("0.5"),
                max=Decimal("2.0"),
            ),
            default_row=None,
        )
        assert table.slug == "vehicle-age"
        assert table.version == 1
        assert table.rateable is True
        assert table.storage == "rows"

    def test_rate_table_key_with_banding_ref(self):
        """A RateTableKey may reference a Banding artifact."""
        key = RateTableKey(
            name="postcode",
            type="string",
            banding_ref=ArtifactRef(
                type="Banding",
                slug="uk-postcodes",
                version=1,
            ),
        )
        assert key.banding_ref is not None
        assert key.banding_ref.slug == "uk-postcodes"

    def test_rate_table_value_types_are_enforced(self):
        """RateTableValue.type must be one of: relativity, money_minor, percentage, count."""
        # Valid types
        for value_type in ["relativity", "money_minor", "percentage", "count"]:
            value = RateTableValue(
                name="test",
                type=value_type,
                unit="factor",
                min=None,
                max=None,
            )
            assert value.type == value_type

    def test_rate_table_value_rejects_invalid_type(self):
        """RateTableValue rejects invalid type literals."""
        with pytest.raises(ValidationError):
            RateTableValue(
                name="test",
                type="invalid",  # type: ignore
                unit="factor",
                min=None,
                max=None,
            )

    def test_rate_table_storage_mode_is_rows_or_parquet(self):
        """storage field must be 'rows' or 'parquet'."""
        # Valid modes
        for mode in ["rows", "parquet"]:
            table = RateTable(
                slug="test",
                version=1,
                rateable=True,
                storage=mode,  # type: ignore
                keys=[RateTableKey(name="k", type="int")],
                value=RateTableValue(name="v", type="relativity", unit="factor"),
            )
            assert table.storage == mode

    def test_rate_table_rejects_invalid_storage_mode(self):
        """storage field must be 'rows' or 'parquet', nothing else."""
        with pytest.raises(ValidationError):
            RateTable(
                slug="test",
                version=1,
                rateable=True,
                storage="invalid",  # type: ignore
                keys=[RateTableKey(name="k", type="int")],
                value=RateTableValue(name="v", type="relativity", unit="factor"),
            )

    def test_rate_table_value_bounds_are_optional(self):
        """min and max on RateTableValue are optional."""
        value = RateTableValue(
            name="relativity",
            type="relativity",
            unit="factor",
            min=None,
            max=None,
        )
        assert value.min is None
        assert value.max is None

    def test_rate_table_default_row_is_optional(self):
        """default_row is optional on RateTable."""
        table = RateTable(
            slug="test",
            version=1,
            rateable=True,
            storage="rows",
            keys=[RateTableKey(name="k", type="int")],
            value=RateTableValue(name="v", type="relativity", unit="factor"),
            default_row=None,
        )
        assert table.default_row is None


@pytest.mark.req("FR-RATE-15")
class TestRateTableVersionImmutability:
    """Rate Table Versions are immutable (FR-RATE-15)."""

    def test_rate_table_version_is_frozen(self):
        """RateTableVersion model is frozen (immutable)."""
        version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Initial version",
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        with pytest.raises(FrozenInstanceError):
            version.storage = "parquet"  # type: ignore

    def test_rate_table_version_requires_change_note(self):
        """change_note is required on RateTableVersion."""
        with pytest.raises(ValidationError):
            RateTableVersion(
                id=uuid4(),
                workspace_id=uuid4(),
                rate_table_id=uuid4(),
                version_number=1,
                storage="rows",
                change_note=None,  # Missing required field
                created_at=datetime.now(),
                created_by=uuid4(),
            )

    def test_rate_table_version_storage_is_immutable(self):
        """storage field is immutable with the version (FR-RATE-62)."""
        version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Initial version",
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        assert version.storage == "rows"
        with pytest.raises(FrozenInstanceError):
            version.storage = "parquet"  # type: ignore

    def test_rate_table_version_tracks_seed_source(self):
        """seeded_from tracks the source model reference and timestamp (FR-RATE-16)."""
        model_ref = ArtifactRef(
            type="Model",
            slug="pricing-model-v2",
            version=5,
        )
        version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Seeded from model",
            seeded_from=model_ref,
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        assert version.seeded_from == model_ref


@pytest.mark.req("FR-RATE-21")
class TestRateTableRateableFlag:
    """A rate table declares whether it is rateable (part of price) or diagnostic."""

    def test_rate_table_rateable_flag_is_boolean(self):
        """rateable is a boolean flag on RateTable (FR-RATE-21)."""
        rateable_table = RateTable(
            slug="price-table",
            version=1,
            rateable=True,
            storage="rows",
            keys=[RateTableKey(name="k", type="int")],
            value=RateTableValue(name="v", type="relativity", unit="factor"),
        )
        assert rateable_table.rateable is True

        diagnostic_table = RateTable(
            slug="diagnostic-table",
            version=1,
            rateable=False,
            storage="rows",
            keys=[RateTableKey(name="k", type="int")],
            value=RateTableValue(name="v", type="relativity", unit="factor"),
        )
        assert diagnostic_table.rateable is False


@pytest.mark.req("FR-RATE-62")
class TestStorageMode:
    """Storage mode is a version property, immutable at write time (FR-RATE-62)."""

    def test_storage_mode_defaults_to_rows_or_parquet(self):
        """storage is a property on RateTableVersion."""
        rows_version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Row storage",
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        assert rows_version.storage == "rows"

        parquet_version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="parquet",
            change_note="Parquet storage",
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        assert parquet_version.storage == "parquet"

    def test_storage_is_immutable_with_version(self):
        """Once written, storage cannot change (FR-RATE-62)."""
        version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Initial",
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        with pytest.raises(FrozenInstanceError):
            version.storage = "parquet"  # type: ignore
