"""Rate-table operations (03 §3.3, slice W10-2): seeding, validation, diffs.

FR-230 (seeding from an approved model), FR-234 (validation on save with named
failures) and FR-231 (cell-level diffs with exposure weighting). The operations are
pure: cells are rows of decimal strings (R2), weights are supplied by the caller, and
nothing here touches a database.
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from model_schema.modelling import (
    GlmFitResult,
    GlmSpec,
    Model,
    ModelStatus,
    OffsetSpec,
    RelativityLevel,
)
from model_schema.rating import (
    RateTableKey,
    RateTableValue,
)
from pricing_core.rate_tables.operations import (
    SeedResult,
    check_model_approved,
    diff_vs_previous,
    diff_vs_seed,
    extract_relativity_table,
    seed_from_model,
    validate_rate_table,
)

#: One table: driver_age_band → relativity, as a GLM's fit carries it.
_DRIVER_LEVELS = (
    RelativityLevel(level="17-20", relativity=1.92, estimate=0.65),
    RelativityLevel(level="21-24", relativity=1.41, estimate=0.34),
    RelativityLevel(level="25-29", relativity=1.12, estimate=0.11),
)


def _glm_model(
    status: ModelStatus,
    relativities: dict[str, tuple[RelativityLevel, ...]] | None = None,
) -> Model:
    """A minimal Model that carries the given factor relativities."""
    spec = GlmSpec(
        model_family_slug="motor-ad-frequency",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure"),
    )
    return Model(
        id=uuid4(),
        model_family_slug=spec.model_family_slug,
        version=1,
        status=status,
        spec=spec,
        spec_hash="v3:sha256:" + "b" * 64,
        fit_result=GlmFitResult(
            converged=True,
            iterations=8,
            fit_seconds=1.0,
            relativities=relativities or {"driver_age_band": _DRIVER_LEVELS},
        ),
        diagnostics_id=uuid4(),
        dataset_version_id=spec.dataset_version_id,
    )


def _key(name: str = "driver_age_band") -> RateTableKey:
    return RateTableKey(name=name, type="string", banding_ref=None)


def _value(name: str = "relativity") -> RateTableValue:
    return RateTableValue(name=name, type="relativity", unit="factor", min=None, max=None)


def _domain() -> dict[str, frozenset[str]]:
    return {"driver_age_band": frozenset({"17-20", "21-24", "25-29"})}


@pytest.mark.req("FR-230")
class TestExtractRelativityTable:
    """A GLM's relativity table is the seed source (FR-230)."""

    def test_extracts_relativities_to_rows(self) -> None:
        """Each factor level becomes a row with the value column."""
        rows = extract_relativity_table(_glm_model(ModelStatus.APPROVED))
        assert rows == [
            {"driver_age_band": "17-20", "relativity": "1.92"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]

    def test_skips_levels_without_a_relativity(self) -> None:
        """A level with `relativity=None` (non-log link) is not seeded."""
        model = _glm_model(
            ModelStatus.APPROVED,
            relativities={
                "factor": (
                    RelativityLevel(level="a", relativity=1.5, estimate=0.4),
                    RelativityLevel(level="b", relativity=None, estimate=1.2),
                )
            },
        )
        rows = extract_relativity_table(model)
        assert rows == [{"factor": "a", "relativity": "1.5"}]

    def test_values_are_decimal_strings_not_floats(self) -> None:
        """Seeded values carry the decimal-string form (R2), never JSON floats."""
        rows = extract_relativity_table(_glm_model(ModelStatus.APPROVED))
        for row in rows:
            assert isinstance(row["relativity"], str)


@pytest.mark.req("FR-230")
class TestCheckModelApproved:
    """FR-20: seeding references only approved models."""

    def test_an_approved_model_passes(self) -> None:
        check_model_approved(_glm_model(ModelStatus.APPROVED))

    @pytest.mark.parametrize(
        "status", [ModelStatus.DRAFT, ModelStatus.FITTED, ModelStatus.REVIEW]
    )
    def test_a_non_approved_model_is_refused(self, status: ModelStatus) -> None:
        with pytest.raises(ValueError, match="PIN_NOT_APPROVED"):
            check_model_approved(_glm_model(status))


@pytest.mark.req("FR-230")
class TestSeedFromModel:
    """Seeding creates the table definition, cells and seed origin (FR-230)."""

    def test_seed_returns_table_cells_and_origin(self) -> None:
        result = seed_from_model(
            _glm_model(ModelStatus.APPROVED),
            table_slug="motor-driver-age-relativity",
            change_note="Seeded from motor-ad-frequency@1",
            seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
        )
        assert isinstance(result, SeedResult)
        assert result.table.slug == "motor-driver-age-relativity"
        assert result.table.rateable is True
        assert result.table.storage == "rows"
        assert [k.name for k in result.table.keys] == ["driver_age_band"]
        assert result.table.value.name == "relativity"
        assert len(result.cells) == 3
        assert str(result.seeded_from.model_ref) == "model:motor-ad-frequency@1"
        assert result.seeded_from.seeded_at == datetime(2026, 7, 2, 10, 0, tzinfo=UTC)

    def test_seeding_a_non_approved_model_fails(self) -> None:
        with pytest.raises(ValueError, match="PIN_NOT_APPROVED"):
            seed_from_model(
                _glm_model(ModelStatus.FITTED),
                table_slug="motor-driver-age-relativity",
                change_note="x",
                seeded_at=datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            )


@pytest.mark.req("FR-234")
class TestValidateRateTable:
    """Validation on save, with a named failure for each mode (FR-234)."""

    def test_complete_coverage_passes(self) -> None:
        cells = [
            {"driver_age_band": "17-20", "relativity": "1.92"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]
        issues = validate_rate_table(cells, [_key()], _value(), key_domains=_domain())
        assert issues == []

    def test_missing_domain_value_is_incomplete(self) -> None:
        cells = [
            {"driver_age_band": "17-20", "relativity": "1.92"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
        ]
        issues = validate_rate_table(cells, [_key()], _value(), key_domains=_domain())
        assert len(issues) == 1
        assert issues[0].code == "INCOMPLETE_KEY_DOMAIN"
        assert "25-29" in issues[0].message

    def test_null_value_is_named(self) -> None:
        cells = [
            {"driver_age_band": "17-20", "relativity": ""},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]
        issues = validate_rate_table(cells, [_key()], _value(), key_domains=_domain())
        assert any(i.code == "NULL_VALUE" for i in issues)
        assert issues[0].code == "NULL_VALUE"

    def test_out_of_bounds_value_is_named(self) -> None:
        cells = [
            {"driver_age_band": "17-20", "relativity": "5.50"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]
        value = RateTableValue(
            name="relativity", type="relativity", unit="factor", min=Decimal("0.2"),
            max=Decimal("2.0"),
        )
        issues = validate_rate_table(cells, [_key()], value, key_domains=_domain())
        assert any(i.code == "OUT_OF_BOUNDS" for i in issues)

    def test_duplicate_key_is_named(self) -> None:
        cells = [
            {"driver_age_band": "17-20", "relativity": "1.92"},
            {"driver_age_band": "17-20", "relativity": "1.50"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]
        issues = validate_rate_table(cells, [_key()], _value(), key_domains=_domain())
        assert any(i.code == "DUPLICATE_KEY" for i in issues)

    def test_default_row_waives_coverage(self) -> None:
        """An explicit default_row satisfies the key-domain coverage (FR-234)."""
        cells = [
            {"driver_age_band": "17-20", "relativity": "1.92"},
        ]
        issues = validate_rate_table(
            cells, [_key()], _value(), key_domains=_domain(),
            default_row={"driver_age_band": "other", "relativity": "1.00"},
        )
        assert issues == []

    def test_multikey_coverage_is_cartesian(self) -> None:
        """With two keys every declared combination must appear."""
        cells = [
            {"age": "young", "area": "a", "relativity": "1.1"},
            {"age": "young", "area": "b", "relativity": "1.2"},
            {"age": "old", "area": "a", "relativity": "0.9"},
        ]
        keys = [_key("age"), _key("area")]
        issues = validate_rate_table(
            cells, keys, _value(),
            key_domains={
                "age": frozenset({"young", "old"}),
                "area": frozenset({"a", "b"}),
            },
        )
        assert len(issues) == 1
        assert issues[0].code == "INCOMPLETE_KEY_DOMAIN"


@pytest.mark.req("FR-231")
class TestDiff:
    """Cell-level diffs: counts, max absolute change, exposure-weighted mean."""

    BEFORE = (
        {"driver_age_band": "17-20", "relativity": "1.00"},
        {"driver_age_band": "21-24", "relativity": "2.00"},
        {"driver_age_band": "25-29", "relativity": "3.00"},
    )
    AFTER = (
        {"driver_age_band": "17-20", "relativity": "1.10"},
        {"driver_age_band": "21-24", "relativity": "2.00"},
        {"driver_age_band": "25-29", "relativity": "3.30"},
    )

    def test_diff_counts_changed_cells_and_max_abs_change(self) -> None:
        diff = diff_vs_previous(
            self.BEFORE, self.AFTER, [_key()], _value(),
            weights={
                ("17-20",): Decimal("100"),
                ("25-29",): Decimal("300"),
            },
        )
        assert diff.changed_cells == 2
        assert diff.max_abs_change_pct == Decimal("10")

    def test_exposure_weighted_mean_change(self) -> None:
        """The weighted mean uses the supplied weights, signed per cell (FR-231)."""
        after = [
            {"driver_age_band": "17-20", "relativity": "1.10"},
            {"driver_age_band": "21-24", "relativity": "2.00"},
            {"driver_age_band": "25-29", "relativity": "3.30"},
            {"driver_age_band": "30-39", "relativity": "0.90"},
        ]
        before = [
            {"driver_age_band": "17-20", "relativity": "1.00"},
            {"driver_age_band": "21-24", "relativity": "2.00"},
            {"driver_age_band": "25-29", "relativity": "3.00"},
            {"driver_age_band": "30-39", "relativity": "1.00"},
        ]
        diff = diff_vs_previous(
            before, after, [_key()], _value(),
            weights={
                ("17-20",): Decimal("100"),
                ("30-39",): Decimal("200"),
                ("25-29",): Decimal("300"),
            },
        )
        # 17-20: +10% w=100; 30-39: -10% w=200; 25-29: +10% w=300
        expected = (
            Decimal("100") * Decimal("10")
            + Decimal("200") * Decimal("-10")
            + Decimal("300") * Decimal("10")
        ) / Decimal("600")
        assert diff.changed_cells == 3
        assert diff.exposure_weighted_mean_change_pct == expected

    def test_diff_vs_seed_compares_against_the_origin(self) -> None:
        seed_cells = [
            {"driver_age_band": "17-20", "relativity": "1.92"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]
        edited = [
            {"driver_age_band": "17-20", "relativity": "1.84"},
            {"driver_age_band": "21-24", "relativity": "1.41"},
            {"driver_age_band": "25-29", "relativity": "1.12"},
        ]
        diff = diff_vs_seed(seed_cells, edited, [_key()], _value())
        assert diff.changed_cells == 1
        assert diff.max_abs_change_pct is not None
        assert diff.max_abs_change_pct == pytest.approx(
            Decimal("4.166666666666666666666666667"), abs=Decimal("1e-9")
        )

    def test_no_changes_yields_none_percentages(self) -> None:
        diff = diff_vs_previous(
            self.BEFORE, list(self.BEFORE), [_key()], _value(),
            weights={("17-20",): Decimal("1")},
        )
        assert diff.changed_cells == 0
        assert diff.max_abs_change_pct is None
        assert diff.exposure_weighted_mean_change_pct is None

    def test_zero_baseline_counts_as_changed_but_not_in_percentages(self) -> None:
        before = [{"driver_age_band": "17-20", "relativity": "0.00"}]
        after = [{"driver_age_band": "17-20", "relativity": "0.50"}]
        diff = diff_vs_previous(
            before, after, [_key()], _value(),
            weights={("17-20",): Decimal("1")},
        )
        assert diff.changed_cells == 1
        assert diff.max_abs_change_pct is None
        assert diff.exposure_weighted_mean_change_pct is None

    def test_added_and_removed_cells_count_as_changed(self) -> None:
        before = [
            {"driver_age_band": "17-20", "relativity": "1.00"},
            {"driver_age_band": "21-24", "relativity": "2.00"},
        ]
        after = [
            {"driver_age_band": "17-20", "relativity": "1.10"},
            {"driver_age_band": "25-29", "relativity": "3.00"},
        ]
        diff = diff_vs_previous(before, after, [_key()], _value())
        assert diff.changed_cells == 3  # 17-20 changed, 21-24 removed, 25-29 added
