"""FR-228, FR-229, FR-236, FR-232: rate table contracts and invariants.

W10-1 adds RateTable and RateTableVersion to model-schema. These tests verify the shapes
parse correctly, immutability invariants hold, and storage mode is fixed at write time.
W10-2 extends the contract with `SeededFrom` (FR-230) and `RateTableDiff`
(FR-231) per 03 §4.2. W10-3 reshapes RateTableVersion to the 03 §4.2 wire form and
adds the BulkOperation record (04 §4.4) and the import verdict/preview (03 §5.2).
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from model_schema.jobs import JobKind
from model_schema.rating import (
    BULK_OPERATION_ADAPTER,
    BulkOperation,
    ImportPreview,
    ImportVerdict,
    RateTable,
    RateTableDiff,
    RateTableKey,
    RateTableValue,
    RateTableVersion,
    SeededFrom,
)
from model_schema.refs import ArtifactRef, BlobRef


@pytest.mark.req("FR-228")
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


_DEFAULT_ROWS = [
    {"driver_age_band": "17-20", "relativity": "1.9200"},
    {"driver_age_band": "21-24", "relativity": "1.4100"},
]


def _version(
    slug: str = "motor-driver-age-relativity",
    version: int = 1,
    storage: str = "rows",
    change_note: str = "Initial version",
    rows: list[dict[str, str]] | None = None,
    cells: BlobRef | None = None,
    **extra: object,
) -> RateTableVersion:
    """A complete RateTableVersion in the 03 §4.2 wire form.

    Defaults to row storage with two rows; pass `cells` (and `rows=None`) for a
    parquet version, or an explicit `rows` to replace the default cells.
    """
    return RateTableVersion(
        slug=slug,
        version=version,
        rateable=True,
        storage=storage,
        keys=[RateTableKey(name="driver_age_band", type="string")],
        value=RateTableValue(name="relativity", type="relativity", unit="factor"),
        default_row=None,
        rows=rows if rows is not None else _DEFAULT_ROWS if cells is None else rows,
        cells=cells,
        change_note=change_note,
        **extra,
    )


@pytest.mark.req("FR-229")
class TestRateTableVersionImmutability:
    """Rate Table Versions are immutable (FR-229, FR-232)."""

    def test_rate_table_version_is_frozen(self):
        """RateTableVersion model is frozen (immutable)."""
        with pytest.raises(ValidationError):
            _version().storage = "parquet"  # type: ignore

    def test_rate_table_version_requires_change_note(self):
        """change_note is required on RateTableVersion."""
        with pytest.raises(ValidationError):
            RateTableVersion(
                slug="motor-driver-age-relativity",
                version=1,
                rateable=True,
                storage="rows",
                keys=[RateTableKey(name="driver_age_band", type="string")],
                value=RateTableValue(name="relativity", type="relativity", unit="factor"),
                rows=[{"driver_age_band": "17-20", "relativity": "1.9200"}],
                change_note=None,  # Missing required field
            )

    def test_rate_table_version_storage_is_immutable(self):
        """storage field is immutable with the version (FR-232)."""
        version = _version()
        assert version.storage == "rows"
        with pytest.raises(ValidationError):
            version.storage = "parquet"  # type: ignore

    def test_rate_table_version_tracks_seed_source(self):
        """seeded_from tracks the source model reference and timestamp (FR-230)."""
        version = _version(
            seeded_from=SeededFrom(
                model_ref=ArtifactRef(type="model", slug="pricing-model-v2", version=5),
                seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            )
        )
        assert version.seeded_from is not None
        assert version.seeded_from.model_ref.slug == "pricing-model-v2"

    def test_rate_table_version_carries_the_wire_form(self):
        """The version carries the definition, the cells, and the creation metadata
        (03 §4.2) — the shape §5.2's operations take and return."""
        version = _version(
            version=6,
            rows=[{"driver_age_band": "17-20", "relativity": "1.8400"}],
        )
        assert version.slug == "motor-driver-age-relativity"
        assert version.version == 6
        assert [key.name for key in version.keys] == ["driver_age_band"]
        assert version.value.name == "relativity"
        assert version.rows == [{"driver_age_band": "17-20", "relativity": "1.8400"}]
        assert version.created_by_operation is None
        assert version.created_by_import is None

    def test_creation_metadata_is_mutually_exclusive(self):
        """A version is created by an operation or by an import, never both (03 §4.2)."""
        with pytest.raises(ValidationError):
            _version(
                created_by_operation=BULK_OPERATION_ADAPTER.validate_python(
                    {
                        "kind": "uplift_table",
                        "parameters": {"percentage": "0.10"},
                        "applied_to": "rate_table:motor-driver-age-relativity@6",
                        "result": {
                            "changed_cells": 3,
                            "new_version": "rate_table:motor-driver-age-relativity@7",
                        },
                    }
                ),
                created_by_import=ImportVerdict(
                    filename="motor-relativity.csv",
                    content_sha256="a" * 64,
                    round_trip="passed",
                ),
            )


@pytest.mark.req("FR-236")
class TestRateTableRateableFlag:
    """A rate table declares whether it is rateable (part of price) or diagnostic."""

    def test_rate_table_rateable_flag_is_boolean(self):
        """rateable is a boolean flag on RateTable (FR-236)."""
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


@pytest.mark.req("FR-232")
class TestStorageMode:
    """Storage mode is a version property, immutable at write time (FR-232)."""

    def test_storage_mode_defaults_to_rows_or_parquet(self):
        """storage is a property on RateTableVersion."""
        rows_version = _version()
        assert rows_version.storage == "rows"

        parquet_version = _version(
            storage="parquet",
            rows=None,
            cells=BlobRef(
                sha256="a" * 64,
                bytes=1234,
                media_type="application/vnd.apache.parquet",
            ),
        )
        assert parquet_version.storage == "parquet"

    def test_parquet_cells_are_a_blob_ref_not_inline_rows(self):
        """Above the threshold the cells are addressed by a BlobRef (FR-232)."""
        parquet = _version(
            storage="parquet",
            rows=None,
            cells=BlobRef(
                sha256="b" * 64,
                bytes=1234,
                media_type="application/vnd.apache.parquet",
            ),
        )
        assert parquet.cells is not None
        assert parquet.rows is None

    def test_storage_mode_and_cells_agree(self):
        """rows storage never carries a blob, and parquet never carries inline rows."""
        with pytest.raises(ValidationError):
            _version(storage="parquet")  # rows present, no blob
        with pytest.raises(ValidationError):
            RateTableVersion(
                slug="motor-driver-age-relativity",
                version=1,
                rateable=True,
                storage="rows",
                keys=[RateTableKey(name="driver_age_band", type="string")],
                value=RateTableValue(name="relativity", type="relativity", unit="factor"),
                rows=None,  # rows storage with no cells
                change_note="rows storage with no cells",
            )

    def test_rows_storage_rejects_a_blob(self):
        """A rows-stored version never carries a blob alongside its inline rows."""
        with pytest.raises(ValidationError):
            _version(
                storage="rows",
                rows=[{"driver_age_band": "17-20", "relativity": "1.8400"}],
                cells=BlobRef(
                    sha256="c" * 64,
                    bytes=1234,
                    media_type="application/vnd.apache.parquet",
                ),
            )

    def test_parquet_storage_rejects_inline_rows_alongside_the_blob(self):
        """A parquet version addresses cells by the blob alone — never both."""
        with pytest.raises(ValidationError):
            _version(
                storage="parquet",
                rows=[{"driver_age_band": "17-20", "relativity": "1.8400"}],
                cells=BlobRef(
                    sha256="d" * 64,
                    bytes=1234,
                    media_type="application/vnd.apache.parquet",
                ),
            )

    def test_parquet_storage_rejects_a_version_with_no_cells_at_all(self):
        """A parquet version with neither blob nor rows is refused."""
        with pytest.raises(ValidationError):
            RateTableVersion(
                slug="motor-driver-age-relativity",
                version=1,
                rateable=True,
                storage="parquet",
                keys=[RateTableKey(name="driver_age_band", type="string")],
                value=RateTableValue(name="relativity", type="relativity", unit="factor"),
                rows=None,
                change_note="parquet storage with no cells",
            )

    def test_storage_is_immutable_with_version(self):
        """Once written, storage cannot change (FR-232)."""
        version = _version()
        with pytest.raises(ValidationError):
            version.storage = "parquet"  # type: ignore


@pytest.mark.req("FR-230")
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
        version = _version(
            seeded_from=SeededFrom(
                model_ref=ArtifactRef(type="model", slug="motor-ad-frequency", version=7),
                seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            )
        )
        assert version.seeded_from is not None
        assert str(version.seeded_from.model_ref) == "model:motor-ad-frequency@7"


@pytest.mark.req("FR-231")
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


@pytest.mark.req("FR-233")
class TestBulkOperation:
    """The BulkOperation record (04 §4.4): four kinds, decimal-string parameters, refs."""

    def _operation(self, kind: str, parameters: dict[str, object]) -> BulkOperation:
        return BULK_OPERATION_ADAPTER.validate_python(
            {
                "kind": kind,
                "parameters": parameters,
                "applied_to": "rate_table:motor-driver-age-relativity@6",
                "result": {
                    "changed_cells": 3,
                    "new_version": "rate_table:motor-driver-age-relativity@7",
                },
            }
        )

    def test_uplift_table_operation_parses(self):
        """uplift_table carries a percentage and the applied-to/result refs."""
        op = self._operation("uplift_table", {"percentage": "0.10"})
        assert op.kind == "uplift_table"
        assert op.parameters.percentage == Decimal("0.10")
        assert str(op.applied_to) == "rate_table:motor-driver-age-relativity@6"
        assert str(op.result.new_version) == "rate_table:motor-driver-age-relativity@7"

    def test_uplift_by_filter_operation_parses(self):
        """uplift_by_filter carries a percentage and an exact-value key filter."""
        op = self._operation(
            "uplift_by_filter",
            {
                "percentage": "-0.05",
                "filter": {"driver_age_band": ["17-20", "21-24"]},
            },
        )
        assert op.parameters.percentage == Decimal("-0.05")
        assert op.parameters.filter == {"driver_age_band": ["17-20", "21-24"]}

    def test_floor_and_cap_operation_parses(self):
        """floor_and_cap carries floor and cap as decimal strings."""
        op = self._operation("floor_and_cap", {"floor": "0.5000", "cap": "2.0000"})
        assert op.parameters.floor == Decimal("0.5000")
        assert op.parameters.cap == Decimal("2.0000")

    def test_rebase_to_level_operation_parses(self):
        """rebase_to_level carries an exact-value base-level key filter."""
        op = self._operation(
            "rebase_to_level", {"base_level": {"driver_age_band": ["21-24"]}}
        )
        assert op.parameters.base_level == {"driver_age_band": ["21-24"]}

    def test_unknown_kind_is_rejected(self):
        """Only the four declared kinds parse."""
        with pytest.raises(ValidationError):
            BULK_OPERATION_ADAPTER.validate_python(
                {
                    "kind": "triple",
                    "parameters": {"percentage": "0.10"},
                    "applied_to": "rate_table:motor-driver-age-relativity@6",
                    "result": {
                        "changed_cells": 1,
                        "new_version": "rate_table:motor-driver-age-relativity@7",
                    },
                }
            )

    def test_parameters_serialise_decimals_as_strings(self):
        """Decimal parameters are decimal strings on the wire, never JSON floats (R2)."""
        op = self._operation("uplift_table", {"percentage": "0.10"})
        dumped = op.model_dump_json()
        assert '"percentage":"0.10"' in dumped, dumped

    def test_result_rejects_negative_changed_cells(self):
        """changed_cells in the operation result cannot be negative."""
        with pytest.raises(ValidationError):
            BULK_OPERATION_ADAPTER.validate_python(
                {
                    "kind": "uplift_table",
                    "parameters": {"percentage": "0.10"},
                    "applied_to": "rate_table:motor-driver-age-relativity@6",
                    "result": {
                        "changed_cells": -1,
                        "new_version": "rate_table:motor-driver-age-relativity@7",
                    },
                }
            )


@pytest.mark.req("FR-235")
class TestImportContract:
    """The import preview (03 §5.2): a diff for the would-be version + round-trip verdict."""

    def test_import_verdict_parses(self):
        """The verdict carries the filename, the content hash, round_trip and baseline."""
        verdict = ImportVerdict(
            filename="motor-relativity.csv",
            content_sha256="a" * 64,
            round_trip="passed",
            applied_to="rate_table:motor-driver-age-relativity@6",
        )
        assert verdict.filename == "motor-relativity.csv"
        assert verdict.content_sha256 == "a" * 64
        assert verdict.round_trip == "passed"
        assert str(verdict.applied_to) == "rate_table:motor-driver-age-relativity@6"

    def test_import_verdict_rejects_non_sha256_hex(self):
        """content_sha256 must be 64 lowercase hex digits."""
        with pytest.raises(ValidationError):
            ImportVerdict(
                filename="x.csv",
                content_sha256="not-a-sha256",
                round_trip="passed",
                applied_to="rate_table:motor-driver-age-relativity@6",
            )

    def test_import_verdict_requires_applied_to(self):
        """The addressed baseline is required: the inheritance check (03 §4.2) reads it."""
        with pytest.raises(ValidationError):
            ImportVerdict(
                filename="motor-relativity.csv",
                content_sha256="a" * 64,
                round_trip="passed",
            )

    def test_import_preview_carries_diff_and_verdict(self):
        """The preview is the would-be version's diff plus the round-trip verdict."""
        preview = ImportPreview(
            diff=RateTableDiff(
                changed_cells=3,
                max_abs_change_pct=Decimal("4.2"),
                exposure_weighted_mean_change_pct=Decimal("0.8"),
            ),
            created_by_import=ImportVerdict(
                filename="motor-relativity.csv",
                content_sha256="a" * 64,
                round_trip="passed",
                applied_to="rate_table:motor-driver-age-relativity@6",
            ),
        )
        assert preview.diff.changed_cells == 3
        assert preview.created_by_import.filename == "motor-relativity.csv"


@pytest.mark.req("FR-232")
def test_rate_table_diff_job_kind_exists() -> None:
    """The parquet diff answers 202 with a Job whose kind is rate_table.diff (03 §5.1)."""
    assert JobKind.RATE_TABLE_DIFF.value == "rate_table.diff"
