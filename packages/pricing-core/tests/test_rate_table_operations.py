"""Rate-table operations (03 §3.3, slice W10-2): seeding, validation, diffs.

FR-230 (seeding from an approved model), FR-234 (validation on save with named
failures) and FR-231 (cell-level diffs with exposure weighting). The operations are
pure: cells are rows of decimal strings (R2), weights are supplied by the caller, and
nothing here touches a database.
"""

import re
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from model_schema.modelling import (
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    Model,
    ModelStatus,
    OffsetSpec,
    RelativityLevel,
)
from model_schema.rating import (
    RateTableCell,
    RateTableKey,
    RateTableStorageMode,
    RateTableValue,
    RateTableVersion,
)
from model_schema.refs import ArtifactRef
from pricing_core.rate_tables.operations import (
    SeedResult,
    apply_cell_edits,
    check_model_approved,
    diff_cells,
    diff_vs_previous,
    diff_vs_seed,
    extract_relativity_table,
    import_from_csv,
    seed_from_model,
    uplift_table,
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
            factor="driver_age_band",
            factors=[_factor("driver_age_band")],
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
                factor="driver_age_band",
                factors=[],
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


# --- WK-1178 SL-1377 (PL-1376, RL-1361, FD-1357): one seeded table per Factor ----------

_REGION_LEVELS = (
    RelativityLevel(level="north", relativity=1.30, estimate=0.26),
    RelativityLevel(level="south", relativity=0.90, estimate=-0.10),
)
_TWO_FACTORS = {"driver_age_band": _DRIVER_LEVELS, "region": _REGION_LEVELS}


def _factor(slug: str, version: int = 1) -> Factor:
    return Factor(
        id=uuid4(),
        slug=slug,
        dataset_id=uuid4(),
        version=version,
        type=FactorType.IDENTITY,
        source_columns=(slug,),
    )


def _seed(model: Model, factor: str, factors: list[Factor]) -> SeedResult:
    return seed_from_model(
        model,
        factor=factor,
        factors=factors,
        table_slug="motor-relativity",
        change_note="seed",
        seeded_at=datetime(2026, 10, 3, 10, 0, tzinfo=UTC),
    )


@pytest.mark.req("FR-230")
@pytest.mark.req("FR-228")
def test_the_seeded_key_is_bound_to_the_pinned_factor_version() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    result = _seed(model, "region", [_factor("driver_age_band"), _factor("region", 4)])
    assert [k.model_dump(mode="json") for k in result.table.keys] == [
        {
            "name": "region",
            "type": "string",
            "banding_ref": None,
            "factor_ref": "factor:region@4",
        }
    ]
    assert result.table.keys[0].banding_ref is None
    assert {row["region"] for row in result.cells} == {"north", "south"}
    assert all(set(row) == {"region", "relativity"} for row in result.cells)


@pytest.mark.req("FR-230")
def test_a_two_factor_model_seeds_one_table_per_factor_purely() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    factors = [_factor("driver_age_band"), _factor("region")]
    age = _seed(model, "driver_age_band", factors)
    region = _seed(model, "region", factors)
    assert [k.name for k in age.table.keys] == ["driver_age_band"]
    assert len(age.cells) == 3
    assert [k.name for k in region.table.keys] == ["region"]
    assert len(region.cells) == 2


@pytest.mark.req("FR-230")
def test_an_interaction_entry_seeds_one_table_of_the_crossed_labels() -> None:
    crossed = (
        RelativityLevel(level="17-20 x north", relativity=1.1, estimate=0.1),
        RelativityLevel(level="17-20 x south", relativity=0.9, estimate=-0.1),
    )
    model = _glm_model(ModelStatus.APPROVED, relativities={"age_x_region": crossed})
    result = _seed(model, "age_x_region", [_factor("age_x_region")])
    assert [k.name for k in result.table.keys] == ["age_x_region"]
    assert {row["age_x_region"] for row in result.cells} == {"17-20 x north", "17-20 x south"}


@pytest.mark.req("FR-230")
def test_a_factor_that_names_no_relativity_entry_is_refused() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    ok = _seed(model, "region", [_factor("region")])  # positive control
    assert ok.cells
    with pytest.raises(ValueError, match="names no relativity entry") as caught:
        _seed(model, "vehicle_age", [_factor("vehicle_age")])
    assert "vehicle_age" in str(caught.value)
    assert not str(caught.value).partition(": ")[0].isupper()


@pytest.mark.req("FR-230")
def test_a_continuous_factor_has_no_relativity_entry_and_is_refused() -> None:
    # A continuous factor is absent from `GlmFitResult.relativities` (glm.py iterates
    # categorical levels only), so it is the same refusal.
    model = _glm_model(ModelStatus.APPROVED, relativities={"region": _REGION_LEVELS})
    with pytest.raises(ValueError, match="names no relativity entry"):
        _seed(model, "driver_age", [_factor("driver_age"), _factor("region")])


@pytest.mark.req("FR-230")
def test_a_relativity_entry_with_no_pinned_factor_of_its_slug_is_refused() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    ok = _seed(model, "region", [_factor("region")])  # positive control
    assert ok.table.keys[0].factor_ref is not None
    # Broken input: a fallback to an unbound key would make this seed succeed.
    with pytest.raises(ValueError, match="no pinned Factor with slug 'region'"):
        _seed(model, "region", [_factor("driver_age_band")])
    with pytest.raises(ValueError, match="no pinned Factor with slug 'region'"):
        _seed(model, "region", [])


@pytest.mark.req("FR-230")
def test_two_pinned_factors_with_the_slug_are_refused() -> None:
    model = _glm_model(ModelStatus.APPROVED, relativities=_TWO_FACTORS)
    with pytest.raises(ValueError, match="2 pinned Factors with slug 'region'"):
        _seed(model, "region", [_factor("region", 1), _factor("region", 2)])


@pytest.mark.req("FR-234")
def test_a_row_lacking_a_declared_key_is_a_named_refusal() -> None:
    keys = [_key("driver_age_band"), _key("region")]
    one_key_row = [{"driver_age_band": "17-20", "relativity": "1.92"}]
    domains = {
        "driver_age_band": frozenset({"17-20"}),
        "region": frozenset({"north"}),
    }
    with pytest.raises(ValueError, match="row 0 lacks declared key 'region'") as caught:
        validate_rate_table(one_key_row, keys, _value(), key_domains=domains)
    # Never an `UPPER_SNAKE: ` prefix: `_map_operation_error` would read it as a code.
    assert not str(caught.value).partition(": ")[0].isupper()
    with pytest.raises(ValueError, match="lacks declared key 'region'"):
        diff_vs_previous(one_key_row, one_key_row, keys, _value())
    with pytest.raises(ValueError, match="lacks declared key 'region'"):
        diff_vs_seed(one_key_row, one_key_row, keys, _value())


@pytest.mark.req("FR-230")
@pytest.mark.parametrize("slug", ["Region", "x", "veh brand"])
def test_a_pinned_factor_slug_outside_the_factor_grammar_is_refused_by_name(slug: str) -> None:
    """RL-1383 Ruled item 3: `Factor.slug` is an unconstrained `str` (FD-1384), so the seed
    refuses a slug the reference grammar cannot hold, by name, rather than failing later."""
    ok = _seed(
        _glm_model(ModelStatus.APPROVED, relativities={"veh_brand": _REGION_LEVELS}),
        "veh_brand",
        [_factor("veh_brand")],
    )  # positive control: an underscore slug is inside the factor grammar
    assert ok.table.keys[0].factor_ref == ArtifactRef(type="factor", slug="veh_brand", version=1)
    model = _glm_model(ModelStatus.APPROVED, relativities={slug: _REGION_LEVELS})
    with pytest.raises(ValueError, match="outside the factor slug grammar") as caught:
        _seed(model, slug, [_factor(slug)])
    assert repr(slug) in str(caught.value)
    assert not str(caught.value).partition(": ")[0].isupper()


# --- FR-234: every value is a finite decimal (FD-1803, SL-1810) -----------------------

_NON_FINITE = ("NaN", "sNaN", "Infinity", "-Infinity", "inf", "-nan")

#: The three value columns FR-234 distinguishes: unbounded, one-sided, two-sided.
_COLUMNS = {
    "unbounded": {},
    "min_only": {"min": Decimal("0.2")},
    "min_and_max": {"min": Decimal("0.2"), "max": Decimal("5.0")},
}


def _bounded_value(bounds: dict[str, Decimal]) -> RateTableValue:
    return RateTableValue(name="relativity", type="relativity", unit="factor", **bounds)


def _cells_with(raw: str) -> list[dict[str, str]]:
    return [
        {"driver_age_band": "17-20", "relativity": raw},
        {"driver_age_band": "21-24", "relativity": "1.41"},
        {"driver_age_band": "25-29", "relativity": "1.12"},
    ]


def _rows_version(raw: str = "1.92", **bounds: Decimal) -> RateTableVersion:
    return RateTableVersion(
        slug="motor-driver-age-relativity",
        version=1,
        rateable=True,
        storage=RateTableStorageMode.ROWS,
        keys=[_key()],
        value=_bounded_value(bounds),
        rows=_cells_with(raw),
        change_note="finite-decimal test version",
    )


@pytest.mark.req("FR-234")
class TestEveryValueIsAFiniteDecimal:
    """A non-finite decimal is a named `OUT_OF_BOUNDS` refusal, never a pass or a 500."""

    @pytest.mark.parametrize("column", sorted(_COLUMNS))
    @pytest.mark.parametrize("raw", _NON_FINITE)
    def test_a_non_finite_value_is_refused_by_name(self, raw: str, column: str) -> None:
        issues = validate_rate_table(
            _cells_with(raw),
            [_key()],
            _bounded_value(_COLUMNS[column]),
            key_domains=_domain(),
        )
        assert len(issues) == 1
        assert issues[0].code == "OUT_OF_BOUNDS"
        assert issues[0].field == "relativity"
        assert issues[0].message.endswith("is not a finite decimal number")

    def test_nan_with_bounds_is_a_named_issue_not_an_exception(self) -> None:
        issues = validate_rate_table(
            _cells_with("NaN"),
            [_key()],
            _bounded_value(_COLUMNS["min_and_max"]),
            key_domains=_domain(),
        )
        assert [i.code for i in issues] == ["OUT_OF_BOUNDS"]

    def test_an_unparseable_value_keeps_its_own_message(self) -> None:
        issues = validate_rate_table(_cells_with("abc"), [_key()], _value(), key_domains=_domain())
        assert len(issues) == 1
        assert issues[0].message.endswith("is not a decimal number")

    def test_the_value_bounds_cannot_themselves_be_non_finite(self) -> None:
        """The bounds test of PL-1809: no `min`/`max` input reaches a comparison as non-finite."""
        for bound in ("min", "max"):
            for raw in (
                float("inf"),
                float("-inf"),
                float("nan"),
                Decimal("Infinity"),
                Decimal("NaN"),
                "Infinity",
                "NaN",
            ):
                with pytest.raises(ValueError, match=bound):
                    RateTableValue(name="r", type="relativity", unit="factor", **{bound: raw})
            for literal in ("1e999", "-1e999", '"Infinity"', "Infinity"):
                with pytest.raises(ValueError, match=bound):
                    RateTableValue.model_validate_json(
                        '{"name":"r","type":"relativity","unit":"factor",'
                        + f'"{bound}":{literal}'
                        + "}"
                    )

    @pytest.mark.parametrize("relativity", [float("inf"), float("nan")])
    def test_seeding_a_non_finite_relativity_is_refused(self, relativity: float) -> None:
        levels = (RelativityLevel(level="17-20", relativity=relativity, estimate=0.65),)
        model = _glm_model(ModelStatus.APPROVED, {"driver_age_band": levels})
        with pytest.raises(ValueError, match=r"^OUT_OF_BOUNDS:"):
            _seed(model, "driver_age_band", [_factor("driver_age_band")])

    def test_a_manual_edit_to_nan_is_a_named_edit_issue(self) -> None:
        edit = RateTableCell({"driver_age_band": "17-20", "relativity": "NaN"})
        result = apply_cell_edits(_rows_version(), [edit])
        assert [(i.index, i.code, i.message) for i in result.issues] == [
            (
                0,
                "OUT_OF_BOUNDS",
                "value 'NaN' for key ('17-20',) is not a finite decimal number",
            )
        ]
        assert result.cells == ()

    def test_an_imported_infinity_is_refused(self) -> None:
        content = b"driver_age_band,relativity\n17-20,Infinity\n21-24,1.41\n25-29,1.12\n"
        message = (
            "OUT_OF_BOUNDS: value 'Infinity' for key ('17-20',) is not a finite decimal number"
        )
        with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
            import_from_csv(_rows_version(), content, filename="import.csv")

    def test_a_bulk_operation_cannot_be_given_a_non_finite_percentage(self) -> None:
        """Pinned, green already: the operation record's schema refuses it before FR-234's
        result check runs, so a bulk operation has no other way to a non-finite result."""
        with pytest.raises(ValueError, match="finite number"):
            uplift_table(_rows_version(), percentage=Decimal("NaN"))

    def test_a_diff_over_a_stored_non_finite_cell_is_named(self) -> None:
        """`_index_rows` hardening: a row stored before the rule is a named refusal."""
        with pytest.raises(ValueError, match=r"^OUT_OF_BOUNDS:.*not a finite decimal number"):
            diff_cells(_cells_with("NaN"), _cells_with("1.92"), [_key()], _value())
