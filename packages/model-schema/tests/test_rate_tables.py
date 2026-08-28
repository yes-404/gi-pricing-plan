"""FR-RATE-14, FR-RATE-15, FR-RATE-21, FR-RATE-62: rate table contracts and invariants.

W10-1 adds RateTable and RateTableVersion to model-schema. These tests verify the shapes
parse correctly, immutability invariants hold, and storage mode is fixed at write time.
W10-2 extends the contract with `SeededFrom` (FR-RATE-16) and `RateTableDiff`
(FR-RATE-17) per 03 §4.2.
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema.rating import (
    RateTable,
    RateTableDiff,
    RateTableKey,
    RateTableValue,
    RateTableVersion,
    SeededFrom,
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
        with pytest.raises(ValidationError):
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
        with pytest.raises(ValidationError):
            version.storage = "parquet"  # type: ignore

    def test_rate_table_version_tracks_seed_source(self):
        """seeded_from tracks the source model reference and timestamp (FR-RATE-16)."""
        version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Seeded from model",
            seeded_from=SeededFrom(
                model_ref=ArtifactRef(type="model", slug="pricing-model-v2", version=5),
                seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            ),
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        assert version.seeded_from is not None
        assert version.seeded_from.model_ref.slug == "pricing-model-v2"


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
        with pytest.raises(ValidationError):
            version.storage = "parquet"  # type: ignore


@pytest.mark.req("FR-RATE-16")
class TestSeededFrom:
    """Seeded-from metadata: the source model reference and the timestamp (03 §4.2)."""

    def test_seeded_from_parses_with_model_ref_and_timestamp(self):
        """`seeded_from` is `{model_ref, seeded_at}` on the wire (03 §4.2)."""
        seeded = SeededFrom(
            model_ref=ArtifactRef(type="model", slug="motor-ad-frequency", version=7),
            seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
        )
        assert seeded.model_ref.slug == "motor-ad-frequency"
        assert seeded.seeded_at == datetime(2026, 7, 2, 10, 0, tzinfo=UTC)

    def test_rate_table_version_carries_seeded_from(self):
        """A seeded RateTableVersion records model_ref and seeded_at."""
        version = RateTableVersion(
            id=uuid4(),
            workspace_id=uuid4(),
            rate_table_id=uuid4(),
            version_number=1,
            storage="rows",
            change_note="Seeded from model",
            seeded_from=SeededFrom(
                model_ref=ArtifactRef(type="model", slug="motor-ad-frequency", version=7),
                seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            ),
            created_at=datetime.now(),
            created_by=uuid4(),
        )
        assert version.seeded_from is not None
        assert str(version.seeded_from.model_ref) == "model:motor-ad-frequency@7"


@pytest.mark.req("FR-RATE-17")
class TestRateTableDiff:
    """The cell-diff artifact (03 §4.2): counts and percentages, never floats."""

    def test_diff_parses_with_changed_cells(self):
        """A diff requires changed_cells and carries the two percentages."""
        diff = RateTableDiff(
            changed_cells=3,
            max_abs_change_pct=Decimal("4.2"),
            exposure_weighted_mean_change_pct=Decimal("0.8"),
        )
        assert diff.changed_cells == 3
        assert diff.max_abs_change_pct == Decimal("4.2")
        assert diff.exposure_weighted_mean_change_pct == Decimal("0.8")

    def test_diff_serialises_decimals_as_strings(self):
        """Percentages are decimal strings on the wire, never JSON floats (R2)."""
        diff = RateTableDiff(
            changed_cells=3,
            max_abs_change_pct=Decimal("4.20"),
            exposure_weighted_mean_change_pct=Decimal("0.8"),
        )
        dumped = diff.model_dump_json()
        assert '"max_abs_change_pct":"4.20"' in dumped, dumped
        assert '"exposure_weighted_mean_change_pct":"0.8"' in dumped, dumped

    def test_diff_accepts_absent_percentages(self):
        """A diff with no comparable values has None percentages."""
        diff = RateTableDiff(changed_cells=0)
        assert diff.max_abs_change_pct is None
        assert diff.exposure_weighted_mean_change_pct is None

    def test_diff_rejects_negative_changed_cells(self):
        """changed_cells cannot be negative."""
        with pytest.raises(ValidationError):
            RateTableDiff(changed_cells=-1)
