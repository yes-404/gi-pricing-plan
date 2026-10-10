"""FR-231's exposure weight: Σ `exposure_years` per cell of a rate table version.

`exposure_weights` joins a portfolio frame (`read_portfolio`'s output) onto a table's
cells through each key's binding (`RL-1361` item 2, `RL-1418` T5): a `factor_ref` key
through that Factor's resolution, a `banding_ref` key through that Banding, an unbound
key by the column of its own name, each compared in the key's declared type. Every
expected figure below is a literal worked by hand, never computed by the code under test.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import uuid4

import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    Grouping,
    GroupingMethod,
    UnseenLevelBehaviour,
)
from model_schema.rating import RateTableDiffCell, RateTableKey, RateTableValue
from pricing_core.rate_tables.operations import diff_cells, diff_vs_previous
from pricing_core.rate_tables.weights import (
    PortfolioWeights,
    WeightJoinError,
    exposure_weights,
)
from pricing_core.rating.analysis import read_portfolio

DATASET = uuid4()
D = Decimal


def _portfolio(**columns: list[Any]) -> pl.LazyFrame:
    n = len(next(iter(columns.values())))
    frame = pl.LazyFrame({"quote_id": [f"q{i}" for i in range(n)], **columns})
    return read_portfolio(frame)


def _key(name: str, type_: str = "string", **over: Any) -> RateTableKey:
    return RateTableKey(name=name, type=type_, **over)  # type: ignore[arg-type]


def _factor(slug: str, column: str, **over: Any) -> Factor:
    base: dict[str, Any] = {
        "id": uuid4(), "slug": slug, "dataset_id": DATASET, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    base.update(over)
    return Factor(**base)


def _banding(column: str = "driver_age", **over: Any) -> Banding:
    base: dict[str, Any] = {
        "id": uuid4(), "slug": "age-steps", "dataset_id": DATASET, "version": 1,
        "column": column, "method": BandingMethod.MANUAL,
        "boundaries": (18.0, 38.0, 58.0, 78.0), "labels": ("18-37", "38-57", "58+"),
    }
    base.update(over)
    return Banding(**base)


def _grouping() -> Grouping:
    return Grouping(
        id=uuid4(), slug="region-ns", dataset_id=DATASET, version=1, column="region",
        method=GroupingMethod.MANUAL,
        mapping={"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH", "S2": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )


def _ref(slug: str) -> str:
    return f"factor:{slug}@1"


@pytest.mark.req("FR-231")
def test_an_unbound_key_weights_by_its_same_named_column() -> None:
    keys = [_key("region"), _key("ncd", "int")]
    cells = [
        {"region": "N", "ncd": "1", "relativity": "1.0"},
        {"region": "N", "ncd": "2", "relativity": "0.9"},
        {"region": "S", "ncd": "1", "relativity": "1.1"},
        {"region": "S", "ncd": "2", "relativity": "1.2"},
    ]
    frame = _portfolio(
        region=["N", "N", "S", "S"], ncd=[1, 2, 1, 1],
        exposure_years=[D("0.5"), D("0.25"), D("1"), D("2")],
    )
    result = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    assert result == PortfolioWeights(
        weights={("N", "1"): D("0.5"), ("N", "2"): D("0.25"), ("S", "1"): D("3")},
        portfolio_exposure=D("3.75"),
        matched_exposure=D("3.75"),
    )


def _identity_case() -> tuple[Any, ...]:
    factor = _factor("area_f", "area_col")
    frame = _portfolio(area_col=["A", "A", "B"], exposure_years=[D("1"), D("1.5"), D("2")])
    cells = [{"area_k": "A", "relativity": "1"}, {"area_k": "B", "relativity": "1"}]
    return factor, [factor], {}, {}, frame, cells, {("A",): D("2.5"), ("B",): D("2")}


def _banding_case() -> tuple[Any, ...]:
    banding = _banding()
    factor = _factor("age_f", "driver_age", type=FactorType.BANDING, banding_id=banding.id)
    frame = _portfolio(
        driver_age=[20.0, 30.0, 40.0, 70.0], exposure_years=[D("1"), D("2"), D("4"), D("8")]
    )
    cells = [{"age_k": lab, "relativity": "1"} for lab in ("18-37", "38-57", "58+")]
    weights = {("18-37",): D("3"), ("38-57",): D("4"), ("58+",): D("8")}
    return factor, [factor], {banding.id: banding}, {}, frame, cells, weights


def _grouping_case() -> tuple[Any, ...]:
    grouping = _grouping()
    factor = _factor("region_f", "region", type=FactorType.GROUPING, grouping_id=grouping.id)
    frame = _portfolio(
        region=["N1", "N2", "S1"], exposure_years=[D("1"), D("2"), D("4")]
    )
    cells = [{"region_k": "NORTH", "relativity": "1"}, {"region_k": "SOUTH", "relativity": "1"}]
    return factor, [factor], {}, {grouping.id: grouping}, frame, cells, {
        ("NORTH",): D("3"), ("SOUTH",): D("4"),
    }


def _interaction_case() -> tuple[Any, ...]:
    banding = _banding()
    grouping = _grouping()
    age = _factor("age_f", "driver_age", type=FactorType.BANDING, banding_id=banding.id)
    region = _factor("region_f", "region", type=FactorType.GROUPING, grouping_id=grouping.id)
    cross = Factor(
        id=uuid4(), slug="age_region", dataset_id=DATASET, version=1,
        type=FactorType.INTERACTION, source_columns=(),
        operand_factor_ids=(age.id, region.id),
    )
    frame = _portfolio(
        driver_age=[20.0, 20.0, 50.0], region=["N1", "S1", "N2"],
        exposure_years=[D("1"), D("2"), D("4")],
    )
    cells = [
        {"x_k": "18-37 | NORTH", "relativity": "1"},
        {"x_k": "18-37 | SOUTH", "relativity": "1"},
        {"x_k": "38-57 | NORTH", "relativity": "1"},
    ]
    weights = {("18-37 | NORTH",): D("1"), ("18-37 | SOUTH",): D("2"), ("38-57 | NORTH",): D("4")}
    return (
        cross, [cross, age, region], {banding.id: banding}, {grouping.id: grouping},
        frame, cells, weights,
    )


@pytest.mark.req("FR-231")
@pytest.mark.parametrize(
    ("case", "key_name"),
    [
        (_identity_case, "area_k"),
        (_banding_case, "age_k"),
        (_grouping_case, "region_k"),
        (_interaction_case, "x_k"),
    ],
    ids=["identity", "banding", "grouping", "interaction"],
)
def test_a_factor_ref_key_weights_through_each_factor_type(case: Any, key_name: str) -> None:
    head, factors, bandings, groupings, frame, cells, expected = case()
    keys = [_key(key_name, factor_ref=_ref(head.slug))]
    result = exposure_weights(
        frame, keys, cells, factors={_ref(head.slug): factors},
        bandings=bandings, groupings=groupings,
    )
    assert result.weights == expected
    assert result.matched_exposure == result.portfolio_exposure == sum(expected.values())


@pytest.mark.req("FR-231")
def test_a_same_named_join_on_the_identity_case_refuses_column_absent() -> None:
    """The break that makes the identity test red: the key's own name is not a column."""
    _, _, _, _, frame, cells, _ = _identity_case()
    with pytest.raises(WeightJoinError, match="area_k"):
        exposure_weights(frame, [_key("area_k")], cells, factors={}, bandings={}, groupings={})


@pytest.mark.req("FR-231")
def test_a_banding_ref_key_weights_through_apply_banding() -> None:
    banding = _banding()
    keys = [_key("age_band", banding_ref="banding:age-steps@1")]
    cells = [{"age_band": lab, "relativity": "1"} for lab in ("18-37", "38-57", "58+")]
    # The key is named `age_band`, but the banding reads its own column, `driver_age`.
    frame = _portfolio(
        driver_age=[20, 30, 40, 70], exposure_years=[D("1"), D("2"), D("4"), D("8")]
    )
    result = exposure_weights(
        frame, keys, cells, factors={}, bandings={banding.id: banding}, groupings={}
    )
    assert result.weights == {("18-37",): D("3"), ("38-57",): D("4"), ("58+",): D("8")}


@pytest.mark.req("FR-231")
def test_keys_compare_in_their_declared_type() -> None:
    keys = [_key("ncd", "int"), _key("garaged", "bool")]
    cells = [{"ncd": "03", "garaged": "True", "relativity": "0.9"}]
    frame = _portfolio(
        ncd=[3, 3], garaged=[True, True], exposure_years=[D("0.5"), D("0.25")]
    )
    result = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    assert result.weights == {("03", "True"): D("0.75")}
    assert result.matched_exposure == result.portfolio_exposure == D("0.75")


@pytest.mark.req("FR-231")
def test_a_date_key_compares_as_a_date() -> None:
    from datetime import date

    keys = [_key("start", "date")]
    cells = [{"start": "2026-01-05", "relativity": "1"}]
    frame = _portfolio(start=[date(2026, 1, 5), date(2026, 1, 6)], exposure_years=[D("1"), D("2")])
    result = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    assert result.weights == {("2026-01-05",): D("1")}
    assert result.portfolio_exposure == D("3")
    assert result.matched_exposure == D("1")


@pytest.mark.req("FR-231")
def test_a_zero_exposure_cell_carries_no_weight() -> None:
    """A cell whose Σ is 0 is left out, so `_compute_diff` never divides by a zero total."""
    keys = [_key("region")]
    frame = _portfolio(region=["N", "S"], exposure_years=[D("0"), D("2")])
    cells = [{"region": "N", "relativity": "1"}, {"region": "S", "relativity": "1"}]
    result = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    assert result.weights == {("S",): D("2")}
    assert result.matched_exposure == D("2")

    # Every weighted changed cell sums to 0: a None mean, no exception (FD-1358's red at
    # caa4e411 was `decimal.InvalidOperation`).
    value = RateTableValue(name="relativity", type="relativity", unit="x")  # type: ignore[arg-type]
    baseline = [{"region": "N", "relativity": "1.0"}, {"region": "S", "relativity": "1.0"}]
    current = [{"region": "N", "relativity": "1.1"}, {"region": "S", "relativity": "1.0"}]
    diff = diff_vs_previous(baseline, current, keys, value, weights=result.weights)
    assert diff.changed_cells == 1
    assert diff.max_abs_change_pct == D("10")
    assert diff.exposure_weighted_mean_change_pct is None
    # A zero weight handed in directly is skipped like an absent one.
    diff = diff_vs_previous(baseline, current, keys, value, weights={("N",): D("0")})
    assert diff.exposure_weighted_mean_change_pct is None


def _refusal_cases() -> list[Any]:
    cases: list[Any] = []
    # a same-named column is absent
    cases.append((
        [_key("region")], [{"region": "N", "relativity": "1"}], {}, {},
        {}, _portfolio(other=["N"], exposure_years=[D("1")]), "region",
    ))
    # a Factor's source column is absent
    factor = _factor("area_f", "area_col")
    cases.append((
        [_key("area_k", factor_ref=_ref("area_f"))], [{"area_k": "A", "relativity": "1"}],
        {_ref("area_f"): [factor]}, {}, {}, _portfolio(other=["A"], exposure_years=[D("1")]),
        "area_col",
    ))
    # a banded column is not numeric (checked before apply_banding casts)
    banding = _banding(column="driver_age")
    cases.append((
        [_key("age_k", banding_ref="banding:age-steps@1")], [{"age_k": "58+", "relativity": "1"}],
        {}, {banding.id: banding}, {},
        _portfolio(driver_age=["old"], exposure_years=[D("1")]), "driver_age",
    ))
    # a Banding with `error` policy meets an out-of-range value
    strict = _banding(below_range="error")
    cases.append((
        [_key("age_k", banding_ref="banding:age-steps@1")], [{"age_k": "58+", "relativity": "1"}],
        {}, {strict.id: strict}, {},
        _portfolio(driver_age=[5.0], exposure_years=[D("1")]), "age-steps",
    ))
    # a portfolio matches no cell
    cases.append((
        [_key("region")], [{"region": "N", "relativity": "1"}], {}, {}, {},
        _portfolio(region=["S"], exposure_years=[D("1")]), "region",
    ))
    return cases


@pytest.mark.req("FR-231")
@pytest.mark.parametrize(
    "case", _refusal_cases(),
    ids=["column-absent", "factor-source-absent", "banded-not-numeric", "banding-error-policy",
         "no-match"],
)
def test_refusals_name_the_key_or_the_column(case: Any) -> None:
    keys, cells, factors, bandings, groupings, frame, needle = case
    with pytest.raises(WeightJoinError, match=needle) as raised:
        exposure_weights(frame, keys, cells, factors=factors, bandings=bandings,
                         groupings=groupings)
    assert raised.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-231")
def test_a_refusal_never_carries_a_portfolio_value() -> None:
    keys = [_key("region")]
    frame = _portfolio(region=["SECRET-VALUE"], exposure_years=[D("1")])
    with pytest.raises(WeightJoinError) as raised:
        exposure_weights(frame, keys, [{"region": "N", "relativity": "1"}],
                         factors={}, bandings={}, groupings={})
    assert "SECRET-VALUE" not in str(raised.value)


@pytest.mark.req("FR-231")
def test_coverage_is_the_fixtures_total_and_matched_exposure() -> None:
    keys = [_key("region")]
    frame = _portfolio(
        region=["N", "S", None, "X"], exposure_years=[D("1"), D("2"), D("4"), D("8")]
    )
    cells = [{"region": "N", "relativity": "1"}, {"region": "S", "relativity": "1"}]
    result = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    # A null key and an unknown value match nothing but still count in the total.
    assert result.portfolio_exposure == D("15")
    assert result.matched_exposure == D("3")


@pytest.mark.req("FR-231")
def test_a_match_with_no_changed_cell_is_a_none_mean_not_a_refusal() -> None:
    keys = [_key("region")]
    value = RateTableValue(name="relativity", type="relativity", unit="x")  # type: ignore[arg-type]
    cells = [{"region": "N", "relativity": "1.0"}, {"region": "S", "relativity": "1.0"}]
    frame = _portfolio(region=["N"], exposure_years=[D("2")])
    weights = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    changed = [{"region": "N", "relativity": "1.0"}, {"region": "S", "relativity": "1.5"}]
    diff = diff_vs_previous(cells, changed, keys, value, weights=weights.weights)
    assert diff.changed_cells == 1
    assert diff.exposure_weighted_mean_change_pct is None


@pytest.mark.req("FR-231")
def test_rows_that_map_with_zero_exposure_are_no_weight_not_a_refusal() -> None:
    """Rows map but every matched row has zero exposure: defined, and it never divides.

    No row-to-cell mapping is missing, so there is no refusal (T5: "a portfolio whose rows
    map to no cell"). Every cell's sum is 0, so `weights` is empty, the coverage figures say
    0 matched of 0 total, and the diff's weighted mean is `None`, as for "no changed cell".
    """
    keys = [_key("region")]
    value = RateTableValue(name="relativity", type="relativity", unit="x")  # type: ignore[arg-type]
    frame = _portfolio(region=["N", "S"], exposure_years=[D("0"), D("0")])
    cells = [{"region": "N", "relativity": "1.0"}, {"region": "S", "relativity": "1.0"}]
    result = exposure_weights(frame, keys, cells, factors={}, bandings={}, groupings={})
    assert result == PortfolioWeights(
        weights={}, portfolio_exposure=D("0"), matched_exposure=D("0")
    )
    changed = [{"region": "N", "relativity": "1.1"}, {"region": "S", "relativity": "1.0"}]
    diff = diff_vs_previous(cells, changed, keys, value, weights=result.weights)
    assert diff.changed_cells == 1
    assert diff.exposure_weighted_mean_change_pct is None


# --- the per-cell diff (RL-1418 T2, T3; FD-1358) ---------------------------------------------


def _value() -> RateTableValue:
    return RateTableValue(name="relativity", type="relativity", unit="x")  # type: ignore[arg-type]


def _rows(*pairs: tuple[str, str]) -> list[dict[str, str]]:
    return [{"band": band, "relativity": value} for band, value in pairs]


@pytest.mark.req("FR-231")
def test_diff_cells_gives_each_cells_change_and_weight() -> None:
    """Two changed cells; every figure is worked by hand."""
    keys = [_key("band")]
    baseline = _rows(("a", "1.0"), ("b", "2.0"), ("c", "5.0"))
    current = _rows(("a", "1.1"), ("b", "1.5"), ("c", "5.0"))
    weights = {("a",): D("3"), ("b",): D("2")}
    cells = diff_cells(baseline, current, keys, _value(), weights=weights)
    assert cells == [
        RateTableDiffCell(
            key={"band": "a"}, change="changed", baseline_value=D("1.0"),
            current_value=D("1.1"), abs_change=D("0.1"), rel_change_pct=D("10"), weight=D("3"),
        ),
        RateTableDiffCell(
            key={"band": "b"}, change="changed", baseline_value=D("2.0"),
            current_value=D("1.5"), abs_change=D("-0.5"), rel_change_pct=D("-25"), weight=D("2"),
        ),
    ]


@pytest.mark.req("FR-231")
def test_the_cells_are_in_key_order_by_code_point() -> None:
    """`"10"` sorts before `"9"`: each value compared as its stored string."""
    keys = [_key("band")]
    baseline = _rows(("9", "1.0"), ("10", "1.0"), ("2", "1.0"))
    current = _rows(("9", "2.0"), ("10", "2.0"), ("2", "2.0"))
    cells = diff_cells(baseline, current, keys, _value())
    assert [c.key["band"] for c in cells] == ["10", "2", "9"]


@pytest.mark.req("FR-231")
def test_the_weight_has_three_states() -> None:
    """Null with no weights; null on a removed cell; `"0"` on a current cell no row maps to
    and on one whose weight is 0, which is also left out of the mean."""
    keys = [_key("band")]
    baseline = _rows(("a", "1.0"), ("b", "1.0"), ("gone", "1.0"), ("z", "1.0"))
    current = _rows(("a", "1.1"), ("b", "1.1"), ("new", "1.0"), ("z", "1.2"))
    unweighted = diff_cells(baseline, current, keys, _value())
    assert [c.weight for c in unweighted] == [None, None, None, None, None]

    weights = {("a",): D("2"), ("b",): D("0"), ("gone",): D("9")}
    by_band = diff_cells(baseline, current, keys, _value(), weights=weights)
    weighted = {c.key["band"]: c for c in by_band}
    assert weighted["a"].weight == D("2")
    assert weighted["b"].weight == D("0")  # Σ 0: reads "0", not null
    assert weighted["z"].weight == D("0")  # no row maps to it
    assert weighted["new"].weight == D("0")  # an added cell is a cell of the current version
    assert weighted["gone"].weight is None  # removed: rows map only to the current version
    assert weighted["gone"].change == "removed"
    assert weighted["new"].change == "added"
    assert weighted["new"].baseline_value is None
    assert weighted["gone"].current_value is None
    assert weighted["new"].abs_change is None
    assert weighted["new"].rel_change_pct is None


@pytest.mark.req("FR-231")
@pytest.mark.parametrize("with_weights", [False, True])
def test_the_cells_agree_with_the_summary(with_weights: bool) -> None:
    """The summary is recomputed from the items: one pass, so they cannot disagree. A
    zero baseline is a change but never a percentage, in the cells and in the summary."""
    keys = [_key("band")]
    baseline = _rows(("a", "1.0"), ("b", "2.0"), ("c", "0"), ("d", "4.0"), ("gone", "1.0"))
    current = _rows(("a", "1.1"), ("b", "1.0"), ("c", "3.0"), ("d", "4.0"), ("new", "1.0"))
    weights = (
        {("a",): D("3"), ("b",): D("1"), ("c",): D("5"), ("new",): D("7")} if with_weights else None
    )
    summary = diff_vs_previous(baseline, current, keys, _value(), weights=weights)
    cells = diff_cells(baseline, current, keys, _value(), weights=weights)

    assert summary.changed_cells == len(cells) == 5
    pcts = [c.rel_change_pct for c in cells if c.rel_change_pct is not None]
    assert summary.max_abs_change_pct == max(abs(pct) for pct in pcts) == D("50")
    pairs = [
        (c.weight, c.rel_change_pct) for c in cells
        if c.weight is not None and c.weight != 0 and c.rel_change_pct is not None
    ]
    if with_weights:
        total = sum((w for w, _ in pairs), D(0))
        mean = sum((w * p for w, p in pairs), D(0)) / total
        assert summary.exposure_weighted_mean_change_pct == mean
        assert summary.exposure_weighted_mean_change_pct == D("-5")
    else:
        assert pairs == []
        assert summary.exposure_weighted_mean_change_pct is None
