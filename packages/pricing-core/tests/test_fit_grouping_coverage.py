"""A fit refuses a grouping Factor that maps none of its column's values, and counts the rest.

FR-104 / FR-109: a Grouping keyed on one level of a column and a Factor whose column holds
another level maps no row. Under `map_to_default` or `map_to_base` the fit then succeeds with
that Factor one constant level, which reads as a model; refusing it is the only honest answer.
Some rows unmapped is not refused: it is counted, with its exposure, beside the fit.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    EbmSpec,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    Grouping,
    GroupingMethod,
    OffsetSpec,
    SplitRef,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import GroupingError, fit_ebm, fit_gbm, fit_glm

pytestmark = pytest.mark.req("FR-109")

DATASET = uuid4()
SENTINEL = "ZZ-SENTINEL-9"
CODE = "GROUPING_MAPS_NO_VALUE"


def _factor(slug: str, column: str, **over: Any) -> Factor:
    base: dict[str, Any] = {
        "id": uuid4(), "slug": slug, "dataset_id": DATASET, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    base.update(over)
    return Factor(**base)


def _grouping(behaviour: UnseenLevelBehaviour, mapping: dict[str, str] | None = None) -> Grouping:
    return Grouping(
        id=uuid4(), slug="region", dataset_id=DATASET, version=1, column="area",
        method=GroupingMethod.MANUAL, mapping=mapping or {"AB": "R1", "CD": "R2"},
        unseen_level_behaviour=behaviour,
        default_target_level="R1" if behaviour is UnseenLevelBehaviour.MAP_TO_DEFAULT else None,
    )


def _book(area: list[str], seed: int = 3) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    n = len(area)
    return pl.DataFrame(
        {
            "area": area,
            "fuel": rng.choice(["x", "y"], n),
            "speed": rng.uniform(0, 100, n),
            "exposure": rng.uniform(0.5, 1.0, n),
            "claims": rng.poisson(0.2, n).astype(float),
        }
    )


def _fit_glm(book: pl.DataFrame, grouping: Grouping) -> Any:
    region = _factor("region", "area", type=FactorType.GROUPING, grouping_id=grouping.id)
    fuel = _factor("fuel", "fuel")
    spec = GlmSpec(
        model_family_slug="cov", dataset_version_id=DATASET, response_column="claims",
        offset=OffsetSpec(kind="log_column", column="exposure"),
        factors=(region.id, fuel.id), family="poisson", link="log",
    )
    return fit_glm(book, spec, [region, fuel], groupings={grouping.id: grouping}).result


def _fit_gbm(book: pl.DataFrame, grouping: Grouping) -> Any:
    region = _factor("region", "area", type=FactorType.GROUPING, grouping_id=grouping.id)
    fuel = _factor("fuel", "fuel")
    spec = GbmSpec(
        model_type="xgboost", model_family_slug="cov", dataset_version_id=DATASET,
        split_ref=SplitRef(split_artifact_id=uuid4()), response_column="claims",
        offset=OffsetSpec(kind="log_column", column="exposure"),
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 2, "eta": 0.1, "num_boost_round": 5},
        early_stopping=None, factors=(region.id, fuel.id),
    )
    return fit_gbm(book, spec, [region, fuel], groupings={grouping.id: grouping}).result


def _fit_ebm(book: pl.DataFrame, grouping: Grouping) -> Any:
    region = _factor("region", "area", type=FactorType.GROUPING, grouping_id=grouping.id)
    speed = _factor("speed", "speed")
    spec = EbmSpec(
        model_family_slug="cov", dataset_version_id=DATASET,
        split_ref=SplitRef(split_artifact_id=uuid4()), response_column="claims",
        objective="rmse", factors=(region.id, speed.id),
    )
    return fit_ebm(book, spec, [region, speed], groupings={grouping.id: grouping})


FITS: list[Callable[[pl.DataFrame, Grouping], Any]] = [_fit_glm, _fit_gbm, _fit_ebm]
BEHAVIOURS = [UnseenLevelBehaviour.MAP_TO_DEFAULT, UnseenLevelBehaviour.MAP_TO_BASE]

#: Fitted at the base of this change, before the report existed: the pinned expectation.
EXPECTED_RELATIVITIES = {"region": [1.0, 1.476041066], "fuel": [1.0, 0.722553161]}


@pytest.mark.parametrize("fit", FITS, ids=["glm", "gbm", "ebm"])
@pytest.mark.parametrize("behaviour", BEHAVIOURS, ids=["default", "base"])
def test_a_grouping_factor_that_maps_none_of_the_column_is_refused(
    fit: Callable[[pl.DataFrame, Grouping], Any], behaviour: UnseenLevelBehaviour
) -> None:
    book = _book(["AB1", "AB2", "CD1", "CD2"] * 50)
    with pytest.raises(GroupingError) as refused:
        fit(book, _grouping(behaviour))
    assert refused.value.code == CODE


def test_the_refusal_names_the_factor_and_never_a_value() -> None:
    book = _book([SENTINEL, f"{SENTINEL}-2"] * 100)
    with pytest.raises(GroupingError) as refused:
        _fit_glm(book, _grouping(UnseenLevelBehaviour.MAP_TO_DEFAULT))
    text = str(refused.value)
    assert SENTINEL not in text
    assert "'region'" in text
    assert "200" in text  # the row count


def test_some_rows_unmapped_is_counted_with_its_exposure_not_refused() -> None:
    book = _book(["AB"] * 40 + ["CD"] * 40 + ["EF"] * 10)
    result = _fit_glm(book, _grouping(UnseenLevelBehaviour.MAP_TO_DEFAULT))
    (entry,) = result.grouping_unmapped
    unmapped = book.filter(pl.col("area") == "EF")
    assert (entry.factor, entry.rows) == ("region", 10)
    assert float(entry.exposure) == pytest.approx(float(unmapped["exposure"].sum()))


def test_every_row_mapped_records_an_empty_report_and_the_fit_is_unchanged() -> None:
    book = _book(["AB"] * 60 + ["CD"] * 60)
    result = _fit_glm(book, _grouping(UnseenLevelBehaviour.ERROR))
    assert result.grouping_unmapped == ()
    levels = {
        k: [round(level.relativity, 9) for level in v] for k, v in result.relativities.items()
    }
    assert levels == EXPECTED_RELATIVITIES




def test_a_holdout_that_maps_none_is_counted_and_not_refused() -> None:
    grouping = _grouping(UnseenLevelBehaviour.MAP_TO_DEFAULT)
    region = _factor("region", "area", type=FactorType.GROUPING, grouping_id=grouping.id)
    fuel = _factor("fuel", "fuel")
    spec = GbmSpec(
        model_type="xgboost", model_family_slug="cov", dataset_version_id=DATASET,
        split_ref=SplitRef(split_artifact_id=uuid4()), response_column="claims",
        offset=OffsetSpec(kind="log_column", column="exposure"),
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 2, "eta": 0.1, "num_boost_round": 5},
        early_stopping=None, factors=(region.id, fuel.id),
    )
    fit = fit_gbm(
        _book(["AB", "CD"] * 50), spec, [region, fuel], groupings={grouping.id: grouping},
        holdout=_book([SENTINEL] * 20),
    )
    assert fit.result.grouping_unmapped == ()
    (entry,) = fit.result.holdout_grouping_unmapped
    assert (entry.factor, entry.rows) == ("region", 20)
