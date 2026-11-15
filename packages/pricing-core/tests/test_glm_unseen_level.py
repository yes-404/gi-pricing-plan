"""A GLM refuses a level its fit never saw unless the Factor declares `map_to_base` (FR-131).

An unseen level matches no dummy of its factor. Both scoring paths, frame (`predict_glm`) and
one-row (`predict_glm_row`), refuse it with `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` unless the Factor
declares `map_to_base` (which scores the level as the base level), and a declared
`error` refuses too. The check is driven by the fitted level set, so a factor fitted on one level
(which has no dummy at all) is covered.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    BelowRangePolicy,
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    Grouping,
    GroupingMethod,
    OffsetSpec,
    RelativityLevel,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import fit_glm
from pricing_core.modelling.predict import (
    PredictionError,
    predict_glm,
    predict_glm_row,
)

DATASET = uuid4()
CODE = "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"


def _factor(slug: str, column: str | None, **over: Any) -> Factor:
    base: dict[str, Any] = {
        "id": uuid4(), "slug": slug, "dataset_id": DATASET, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,) if column else (),
    }
    base.update(over)
    return Factor(**base)


def _frame(rows: int = 600) -> pl.DataFrame:
    rng = np.random.default_rng(7)
    area = rng.choice(["A", "B", "B"], rows)  # B is the largest, so the base
    fuel = rng.choice(["x", "y"], rows)
    # the (A, y) cell is never observed
    fuel = np.where(area == "A", "x", fuel)
    age = rng.uniform(0.0, 20.0, rows)
    return pl.DataFrame(
        {
            "area": area, "fuel": fuel, "age": age, "solo": ["only"] * rows,
            "exposure": np.ones(rows),
            "claims": rng.poisson(0.1 + 0.1 * (area == "A")).astype(float),
        }
    )


def _spec(factors: tuple[Factor, ...]) -> GlmSpec:
    return GlmSpec(
        model_family_slug="unseen-level", dataset_version_id=DATASET, response_column="claims",
        offset=OffsetSpec(kind="log_column", column="exposure"),
        factors=tuple(f.id for f in factors), family="poisson", link="log",
    )


class World:
    def __init__(
        self, factors: tuple[Factor, ...], book: pl.DataFrame | None = None, **fit_kwargs: Any
    ) -> None:
        self.spec = _spec(factors)
        self.factors = factors
        self.kwargs = fit_kwargs
        self.fit: GlmFitResult = fit_glm(
            _frame() if book is None else book, self.spec, list(factors), **fit_kwargs
        ).result

    def declare(self, slug: str, behaviour: UnseenLevelBehaviour | None) -> tuple[Factor, ...]:
        return tuple(
            f.model_copy(update={"unseen_level_behaviour": behaviour}) if f.slug == slug else f
            for f in self.factors
        )

    def frame(self, row: Mapping[str, Any], factors: tuple[Factor, ...]) -> float:
        return float(
            predict_glm(
                self.fit, pl.DataFrame([dict(row)]), factors, self.spec, **self.kwargs
            )[0]
        )

    def one(self, row: Mapping[str, Any], factors: tuple[Factor, ...]) -> float:
        return predict_glm_row(self.fit, row, factors, self.spec, **self.kwargs)


def _both(world: World) -> list[Any]:
    return [world.frame, world.one]


@pytest.fixture(scope="module")
def area() -> World:
    return World((_factor("area", "area"),))


def _row(**over: Any) -> dict[str, Any]:
    return {"area": "B", "fuel": "x", "age": 5.0, "solo": "only", "exposure": 1.0, **over}


def test_an_undeclared_unseen_level_is_refused_on_both_paths(area: World) -> None:
    for score in _both(area):
        with pytest.raises(PredictionError) as raised:
            score(_row(area="C"), area.factors)
        assert raised.value.code == CODE
        assert raised.value.terms == ("area",)
        assert "'C'" not in str(raised.value)  # a level of a quote is never in the text


@pytest.mark.parametrize("path", ["frame", "one"])
def test_a_declared_error_is_refused(area: World, path: str) -> None:
    factors = area.declare("area", UnseenLevelBehaviour.ERROR)
    with pytest.raises(PredictionError) as raised:
        getattr(area, path)(_row(area="C"), factors)
    assert raised.value.code == CODE
    assert "declares 'error'" in str(raised.value)


@pytest.mark.parametrize("path", ["frame", "one"])
def test_map_to_base_scores_an_unseen_level_as_the_base(area: World, path: str) -> None:
    factors = area.declare("area", UnseenLevelBehaviour.MAP_TO_BASE)
    score = getattr(area, path)
    assert score(_row(area="C"), factors).hex() == score(_row(area="B"), factors).hex()
    assert score(_row(area="A"), factors) != score(_row(area="B"), factors)


@pytest.mark.parametrize("path", ["frame", "one"])
def test_seen_levels_still_score_with_nothing_declared(area: World, path: str) -> None:
    score = getattr(area, path)
    assert score(_row(area="A"), area.factors) > 0.0
    assert score(_row(area="B"), area.factors) > 0.0


def test_the_frame_path_refuses_an_unseen_level_among_seen_rows(area: World) -> None:
    data = pl.DataFrame([_row(area="A"), _row(area="C"), _row(area="B")])
    with pytest.raises(PredictionError) as raised:
        predict_glm(area.fit, data, area.factors, area.spec)
    assert raised.value.code == CODE


def test_a_null_is_not_an_unseen_level(area: World) -> None:
    data = pl.DataFrame(
        {"area": [None, "A"], "exposure": [1.0, 1.0]}, schema_overrides={"area": pl.String}
    )
    code = None
    try:
        predict_glm(area.fit, data, area.factors, area.spec)
    except PredictionError as error:
        code = error.code
    assert code != CODE


def test_a_factor_fitted_on_one_level_refuses_another() -> None:
    # One fitted level means no dummy, so a check driven by the dummies never looks at it.
    world = World((_factor("area", "area"), _factor("solo", "solo")))
    assert not any(c.term.startswith("solo[") for c in world.fit.coefficients)
    for score in _both(world):
        with pytest.raises(PredictionError) as raised:
            score(_row(solo="other"), world.factors)
        assert raised.value.code == CODE
        assert raised.value.terms == ("solo",)


def test_an_interaction_cell_the_fit_never_saw_is_refused_unless_declared() -> None:
    area_f, fuel_f = _factor("area", "area"), _factor("fuel", "fuel")
    cross = _factor(
        "area_x_fuel", None, type=FactorType.INTERACTION,
        operand_factor_ids=(area_f.id, fuel_f.id),
    )
    world = World((area_f, fuel_f, cross))
    unseen_cell = _row(area="A", fuel="y")
    with pytest.raises(PredictionError) as raised:
        world.frame(unseen_cell, world.factors)
    assert raised.value.code == CODE
    assert raised.value.terms == ("area_x_fuel",)
    declared = world.declare("area_x_fuel", UnseenLevelBehaviour.MAP_TO_BASE)
    assert world.frame(unseen_cell, declared) > 0.0


def test_a_null_level_the_fit_never_saw_is_refused_unless_declared() -> None:
    """A band cannot be unreached (FR-100 refuses the fit), but `null_level` is outside the
    labels it checks: a fit on in-range ages has no relativity for it, and an out-of-range
    quote lands on it."""
    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="age",
        method=BandingMethod.MANUAL, boundaries=(0.0, 10.0, 20.0), labels=("low", "mid"),
        null_level="unknown", below_range=BelowRangePolicy.NULL_LEVEL,
    )
    age = _factor("age_band", "age", type=FactorType.BANDING, banding_id=banding.id)
    world = World((age,), bandings={banding.id: banding})
    assert "unknown" not in {entry.level for entry in world.fit.relativities["age_band"]}
    for score in _both(world):
        with pytest.raises(PredictionError) as raised:
            score(_row(age=-5.0), world.factors)
        assert raised.value.code == CODE
        assert raised.value.terms == ("age_band",)
        score(_row(age=5.0), world.factors)  # an in-range age is unaffected
    declared = world.declare("age_band", UnseenLevelBehaviour.MAP_TO_BASE)
    for score in _both(world):
        base = score(_row(age=-5.0), declared)
        assert base > 0.0


def _null_level_world(book: pl.DataFrame | None = None) -> World:
    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="age",
        method=BandingMethod.MANUAL, boundaries=(0.0, 10.0, 20.0), labels=("low", "mid"),
        null_level="unknown", below_range=BelowRangePolicy.NULL_LEVEL,
    )
    age = _factor("age_band", "age", type=FactorType.BANDING, banding_id=banding.id)
    return World((age,), book, bandings={banding.id: banding})


def _with_age(book: pl.DataFrame, rows: int, value: float | None) -> pl.DataFrame:
    """The first `rows` rows get `value` as their age (`None` is a missing age)."""
    return book.with_columns(
        pl.when(pl.int_range(pl.len()) < rows).then(pl.lit(value, dtype=pl.Float64))
        .otherwise(pl.col("age")).alias("age")
    )


def test_a_fit_over_a_missing_value_in_a_banded_column_is_fitted() -> None:
    """A Banding with a `null_level` fitted on data that holds a null: the null level is a level
    of the design, with its own relativity."""
    fit = _null_level_world(_with_age(_frame(), 40, None)).fit
    assert "unknown" in {entry.level for entry in fit.relativities["age_band"]}
    assert fit.unseen_level_gaps == ()  # the fit saw the null level


def test_a_fit_over_an_out_of_range_value_mapped_to_the_null_level_is_fitted() -> None:
    fit = _null_level_world(_with_age(_frame(), 40, -5.0)).fit  # below_range = null_level
    assert "unknown" in {entry.level for entry in fit.relativities["age_band"]}
    assert fit.unseen_level_gaps == ()


def test_a_fit_lists_the_null_level_it_has_no_relativity_for() -> None:
    gaps = _null_level_world().fit.unseen_level_gaps
    assert gaps is not None
    assert [(g.factor, g.level) for g in gaps] == [("age_band", "unknown")]
    assert {r.value for r in gaps[0].reached_by} == {"null_value", "below_range"}


def test_a_grouping_target_level_the_fit_never_saw_is_listed() -> None:
    from pricing_core.modelling.glm import _unseen_level_gaps

    world = _cross_world()
    grouping, = world.kwargs["groupings"].values()
    fuel = next(f for f in world.factors if f.slug == "fuel_group")
    fitted = {"fuel_group": (RelativityLevel(level="X", is_base=True),)}  # no "Y" rows
    gaps = _unseen_level_gaps(fitted, (fuel,), None, {grouping.id: grouping})
    assert [(g.factor, g.level, [r.value for r in g.reached_by]) for g in gaps] == [
        ("fuel_group", "Y", ["grouping_target"])
    ]


def test_a_fit_that_saw_the_null_level_lists_nothing() -> None:
    fit = _null_level_world(_with_age(_frame(), 40, None)).fit  # a real fit over rows with a null
    assert fit.unseen_level_gaps == ()


def _thin_check(book: pl.DataFrame) -> Any:
    from decimal import Decimal

    from pricing_core.modelling.bandings import check_banding

    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="age",
        method=BandingMethod.MANUAL, boundaries=(0.0, 10.0, 20.0), labels=("low", "mid"),
        null_level="unknown", below_range=BelowRangePolicy.NULL_LEVEL,
    )
    frame = book.rename({"exposure": "exposure_years", "claims": "claim_count"})
    return check_banding(frame, banding, min_exposure=Decimal(100))


def test_the_thin_band_floor_applies_to_the_null_level_with_no_position() -> None:
    """40 rows reach `unknown` (exposure 40, under the floor of 100): its warning names the null
    level and carries no `band_index`. The declared bands, 280 rows each, are not thin."""
    warnings = _thin_check(_with_age(_frame(), 40, None))
    assert [(w.band_label, w.band_index) for w in warnings] == [("unknown", None)]


def test_the_empty_band_refusal_still_covers_declared_bands_only() -> None:
    """A frame that never reaches `unknown` is not refused for it; one that never reaches a
    declared band is."""
    from pricing_core.modelling.errors import BandingError

    assert _thin_check(_frame()) == ()  # no row on the null level, and no thin declared band
    with pytest.raises(BandingError):
        _thin_check(_frame().filter(pl.col("age") < 10.0))  # no row in `mid`


def test_a_warning_stored_before_the_null_level_still_validates() -> None:
    from model_schema import ClaimCountBandingWarning, ExposureBandingWarning

    stored = {
        "banding": "banding:age-steps@1", "band_label": "mid", "band_index": 1,
        "measure": "exposure", "observed": "3", "minimum": "100",
    }
    assert ExposureBandingWarning.model_validate(stored).band_index == 1
    on_null = {**stored, "band_label": "unknown", "band_index": None}
    assert ExposureBandingWarning.model_validate(on_null).band_index is None
    count = {**on_null, "measure": "claim_count", "observed": 3, "minimum": 10}
    assert ClaimCountBandingWarning.model_validate(count).band_index is None


def _cross_world(book: pl.DataFrame | None = None) -> World:
    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="age",
        method=BandingMethod.MANUAL, boundaries=(0.0, 10.0, 20.0), labels=("low", "mid"),
        null_level="unknown", below_range=BelowRangePolicy.NULL_LEVEL,
    )
    grouping = Grouping(
        id=uuid4(), slug="fuel-xy", dataset_id=DATASET, version=1, column="fuel",
        method=GroupingMethod.MANUAL, mapping={"x": "X", "y": "Y"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )
    age = _factor("age_band", "age", type=FactorType.BANDING, banding_id=banding.id)
    fuel = _factor("fuel_group", "fuel", type=FactorType.GROUPING, grouping_id=grouping.id)
    cross = _factor(
        "age_x_fuel", None, type=FactorType.INTERACTION,
        operand_factor_ids=(age.id, fuel.id),
    )
    return World(
        (age, fuel, cross), book, bandings={banding.id: banding},
        groupings={grouping.id: grouping},
    )


def test_a_sparse_cross_in_the_null_level_world_names_its_unfitted_cells() -> None:
    book = _frame()
    book = book.filter(~((pl.col("age") >= 10.0) & (pl.col("fuel") == "y")))  # no mid | Y rows
    reports = _cross_world(book).fit.unseen_cell_reports
    assert reports is not None
    (report,) = reports
    assert report.factor == "age_x_fuel"
    assert report.state.value == "examined"
    assert (report.producible, report.unfitted) == (6, 3)  # {low, mid, unknown} x {X, Y}
    assert report.examples == ("mid | Y", "unknown | X", "unknown | Y")
    assert report.example_cap == 5


def test_a_cross_every_cell_of_which_is_fitted_lists_none() -> None:
    from pricing_core.modelling.glm import _unseen_cell_reports

    world = _cross_world()
    banding, = world.kwargs["bandings"].values()
    grouping, = world.kwargs["groupings"].values()
    cells = tuple(
        RelativityLevel(level=f"{a} | {b}", is_base=a == "low" and b == "X")
        for a in ("low", "mid", "unknown")
        for b in ("X", "Y")
    )
    (report,) = _unseen_cell_reports(
        {"age_x_fuel": cells}, world.factors, {banding.id: banding}, {grouping.id: grouping}
    )
    assert (report.state.value, report.producible, report.unfitted, report.examples) == (
        "examined", 6, 0, (),
    )


def _identity_cross(book: pl.DataFrame | None = None) -> World:
    area_f, fuel_f = _factor("area", "area"), _factor("fuel", "fuel")
    cross = _factor(
        "area_x_fuel", None, type=FactorType.INTERACTION,
        operand_factor_ids=(area_f.id, fuel_f.id),
    )
    return World((area_f, fuel_f, cross), book)


def test_a_sparse_grid_of_identity_operands_reports_the_exact_count_of_unseen_pairings() -> None:
    """`area` and `fuel` levels are the data's, so the report is a lower bound over the levels the
    fit saw: A, B x x, y is four pairings and the book never has `A | y`."""
    reports = _identity_cross().fit.unseen_cell_reports
    assert reports is not None
    (report,) = reports
    assert report.state.value == "lower_bound"
    assert (report.producible, report.unfitted) == (4, 1)
    assert report.examples == ("A | y",)


def test_a_full_grid_of_identity_operands_reports_zero() -> None:
    book = _frame().with_columns(pl.Series("fuel", ["x", "y"] * 300))  # every pairing occurs
    reports = _identity_cross(book).fit.unseen_cell_reports
    assert reports is not None
    (report,) = reports
    assert (report.state.value, report.producible, report.unfitted) == ("lower_bound", 4, 0)
    assert report.examples == ()


def test_the_named_cells_stop_at_the_stated_cap_and_the_count_does_not() -> None:
    from pricing_core.modelling.glm import _unseen_cell_reports

    area_f, fuel_f = _factor("area", "area"), _factor("fuel", "fuel")
    cross = _factor(
        "area_x_fuel", None, type=FactorType.INTERACTION,
        operand_factor_ids=(area_f.id, fuel_f.id),
    )
    diagonal = {
        "area_x_fuel": tuple(
            RelativityLevel(level=f"a{i} | b{i}", is_base=i == 0) for i in range(4)
        )
    }
    (report,) = _unseen_cell_reports(diagonal, (area_f, fuel_f, cross), None, None)
    assert (report.producible, report.unfitted) == (16, 12)  # 4 x 4 pairings, 4 fitted
    assert report.example_cap == 5
    assert len(report.examples) == 5
    assert report.examples == ("a0 | b1", "a0 | b2", "a0 | b3", "a1 | b0", "a1 | b2")


def test_a_cross_that_cannot_be_computed_is_not_examined() -> None:
    """A nested interaction, a missing artifact and a level holding the separator: no count."""
    from pricing_core.modelling.glm import _unseen_cell_reports

    area_f, fuel_f = _factor("area", "area"), _factor("fuel", "fuel")
    inner = _factor(
        "inner", None, type=FactorType.INTERACTION, operand_factor_ids=(area_f.id, fuel_f.id)
    )
    nested = _factor(
        "nested", None, type=FactorType.INTERACTION, operand_factor_ids=(inner.id, fuel_f.id)
    )
    banded = _factor("banded", "age", type=FactorType.BANDING, banding_id=uuid4())
    missing = _factor(
        "missing", None, type=FactorType.INTERACTION, operand_factor_ids=(banded.id, fuel_f.id)
    )
    flat = _factor(
        "flat", None, type=FactorType.INTERACTION, operand_factor_ids=(area_f.id, fuel_f.id)
    )
    cells = {
        # well-formed, so only the nesting bars it
        "nested": (RelativityLevel(level="A | x", is_base=True),),
        "missing": (RelativityLevel(level="low | x", is_base=True),),
        "flat": (RelativityLevel(level="A | B | x", is_base=True),),  # a level holds " | "
    }
    reports = _unseen_cell_reports(
        cells, (area_f, fuel_f, inner, nested, banded, missing, flat), None, None
    )
    assert {r.factor: r.state.value for r in reports} == {
        "inner": "lower_bound", "nested": "not_examined", "missing": "not_examined",
        "flat": "not_examined",
    }
    assert all(r.unfitted is None for r in reports if r.state.value == "not_examined")


def test_a_cross_with_too_many_cells_to_name_carries_the_count_only() -> None:
    from pricing_core.modelling.glm import _unseen_cell_reports

    labels = tuple(f"b{i:03d}" for i in range(101))
    banding = Banding(
        id=uuid4(), slug="wide", dataset_id=DATASET, version=1, column="age",
        method=BandingMethod.MANUAL, boundaries=tuple(float(i) for i in range(102)),
        labels=labels,
    )
    one = _factor("one", "age", type=FactorType.BANDING, banding_id=banding.id)
    two = _factor("two", "age", type=FactorType.BANDING, banding_id=banding.id)
    cross = _factor(
        "one_x_two", None, type=FactorType.INTERACTION, operand_factor_ids=(one.id, two.id)
    )
    fitted = {"one_x_two": (RelativityLevel(level="b000 | b000", is_base=True),)}
    (report,) = _unseen_cell_reports(fitted, (one, two, cross), {banding.id: banding}, None)
    assert report.state.value == "count_only"
    assert (report.producible, report.unfitted, report.examples) == (10_201, 10_200, ())


def test_a_fit_stored_before_the_report_reads_not_recorded_never_none() -> None:
    fit = _null_level_world().fit
    old = GlmFitResult.model_validate(
        fit.model_dump(mode="json", exclude={"unseen_level_gaps", "unseen_cell_reports"})
    )
    assert old.unseen_level_gaps is None  # "not recorded"
    assert old.unseen_level_gaps != ()  # which is not "none"
    assert old.unseen_cell_reports is None
    assert fit.unseen_cell_reports == ()  # a fit with no interaction term says so


def test_a_factor_declaring_map_to_default_cannot_exist() -> None:
    with pytest.raises(ValueError, match="map_to_default"):
        _factor("area", "area", unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT)
