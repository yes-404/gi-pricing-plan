"""A Grouping with a parent refuses a value that is a source level of one of its ancestors.

FR-104 / FR-109: a Factor on a Grouping reads a column at the Grouping's own source level. A
value that is a source level of an *ancestor* in the chain sits at the wrong level for it, and
under `map_to_default` or `map_to_base` the declared behaviour would price it as if unknown.
It is refused instead, naming the Factor and never the value. A value the Grouping maps keeps
its price byte for byte; a value no ancestor knows keeps the declared behaviour; following the
chain to resolve a value is not built. The ancestors are supplied with the Groupings: a caller
that does not supply them (a stored Bundle) keeps today's behaviour.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    Grouping,
    GroupingMethod,
    OffsetSpec,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import (
    FactorResolutionError,
    GroupingAncestorLevelError,
    GroupingError,
    fit_glm,
    grouping_ancestors,
)
from pricing_core.modelling.factors import resolve_factor_columns
from pricing_core.modelling.predict import predict_glm, predict_glm_row
from pricing_core.safe_error import CodedError, safe_error_detail

pytestmark = pytest.mark.req("FR-109")

DATASET = uuid4()
CODE = "GROUPING_VALUE_AT_ANCESTOR_LEVEL"
SENTINEL = "ZZ9-SENTINEL"

#: The prices of the control model, fitted at the base of this change, before any chain check
#: existed: a column already at the Grouping's level must price identically after it.
CONTROL_AB = 0.18114038519983092
CONTROL_CD = 0.07297814206002928


def _grouping(
    slug: str,
    column: str,
    mapping: dict[str, str],
    behaviour: UnseenLevelBehaviour = UnseenLevelBehaviour.ERROR,
    parent: Grouping | None = None,
) -> Grouping:
    return Grouping(
        id=uuid4(), slug=slug, dataset_id=DATASET, version=1, column=column,
        method=GroupingMethod.MANUAL, mapping=mapping, unseen_level_behaviour=behaviour,
        default_target_level=(
            next(iter(mapping.values())) if behaviour is UnseenLevelBehaviour.MAP_TO_DEFAULT
            else None
        ),
        parent_grouping_id=parent.id if parent else None,
    )


class Chain:
    """fine (AB1..CD2 → AB, CD) ← region (AB, CD → R1, R2) fitted on a column of areas."""

    def __init__(self, behaviour: UnseenLevelBehaviour = UnseenLevelBehaviour.MAP_TO_DEFAULT):
        self.fine = _grouping(
            "fine", "area",
            {"AB1": "AB", "AB2": "AB", "CD1": "CD", "CD2": "CD", SENTINEL: "CD"},
        )
        self.region = _grouping(
            "region", "area", {"AB": "R1", "CD": "R2"}, behaviour, parent=self.fine
        )
        self.factors = (
            Factor(
                id=uuid4(), slug="region_f", dataset_id=DATASET, version=1,
                type=FactorType.GROUPING, source_columns=("area",),
                grouping_id=self.region.id,
            ),
            Factor(
                id=uuid4(), slug="fuel", dataset_id=DATASET, version=1,
                type=FactorType.IDENTITY, source_columns=("fuel",),
            ),
        )
        self.spec = GlmSpec(
            model_family_slug="chain", dataset_version_id=DATASET, response_column="claims",
            offset=OffsetSpec(kind="log_column", column="exposure"),
            factors=tuple(f.id for f in self.factors), family="poisson", link="log",
        )
        rng = np.random.default_rng(5)
        area = rng.choice(["AB", "CD"], 800)
        self.fit: GlmFitResult = fit_glm(
            pl.DataFrame(
                {
                    "area": area,
                    "fuel": rng.choice(["x", "y"], 800),
                    "exposure": np.ones(800),
                    "claims": rng.poisson(0.05 + 0.15 * (area == "AB")).astype(float),
                }
            ),
            self.spec, list(self.factors), groupings={self.region.id: self.region},
        ).result

    def groupings(self, with_ancestors: bool = True) -> dict[Any, Grouping]:
        out = {self.region.id: self.region}
        if with_ancestors:
            out[self.fine.id] = self.fine
        return out

    def frame(self, area: str, with_ancestors: bool = True) -> float:
        return float(
            predict_glm(
                self.fit, pl.DataFrame({"area": [area], "fuel": ["x"], "exposure": [1.0]}),
                self.factors, self.spec, groupings=self.groupings(with_ancestors),
            )[0]
        )

    def row(self, area: str, with_ancestors: bool = True) -> float:
        return predict_glm_row(
            self.fit, {"area": area, "fuel": "x", "exposure": 1.0},
            self.factors, self.spec, groupings=self.groupings(with_ancestors),
        )


def _raises(call: Any, *args: Any) -> GroupingError:
    with pytest.raises(GroupingError) as refused:
        call(*args)
    return refused.value


# --- a price that is right today is unchanged ---------------------------------------------


@pytest.mark.parametrize("path", ["frame", "row"])
def test_a_column_already_at_the_groupings_level_prices_byte_for_byte_as_before(path: str) -> None:
    chain = Chain()
    price = getattr(chain, path)
    # Pinned across fits: a refit can differ in the last digit, so the pin is to 1e-12; the two
    # comparisons below, over one fit, are exact.
    assert price("AB") == pytest.approx(CONTROL_AB, rel=1e-12)
    assert price("CD") == pytest.approx(CONTROL_CD, rel=1e-12)
    assert price("AB") == price("AB", with_ancestors=False)
    assert price("CD") == price("CD", with_ancestors=False)


@pytest.mark.parametrize("path", ["frame", "row"])
def test_a_value_no_ancestor_knows_keeps_the_declared_behaviour(path: str) -> None:
    chain = Chain()
    price = getattr(chain, path)
    assert price("GH") == price("AB")  # the default level, R1


# --- a value at an ancestor's level is refused ---------------------------------------------


@pytest.mark.parametrize("path", ["frame", "row"])
@pytest.mark.parametrize(
    "behaviour", [UnseenLevelBehaviour.MAP_TO_DEFAULT, UnseenLevelBehaviour.MAP_TO_BASE]
)
def test_a_value_at_an_ancestors_level_is_refused_never_priced(
    path: str, behaviour: UnseenLevelBehaviour
) -> None:
    chain = Chain(behaviour)
    refused = _raises(getattr(chain, path), "AB1")
    assert refused.code == CODE
    refused = _raises(getattr(chain, path), "CD2")
    assert refused.code == CODE


def test_without_its_ancestors_the_grouping_behaves_as_it_did() -> None:
    """A stored Bundle carries no ancestors: the check cannot run, and nothing changes."""
    chain = Chain()
    assert chain.frame("AB1", with_ancestors=False) == chain.frame("GH", with_ancestors=False)
    assert chain.row("AB1", with_ancestors=False) == chain.row("GH", with_ancestors=False)


def test_the_refusal_names_the_factor_and_never_the_value() -> None:
    chain = Chain()
    for call in (chain.frame, chain.row):
        text = str(_raises(call, SENTINEL))
        assert SENTINEL not in text
        assert "'region_f'" in text
        assert "'region'@1" in text
        assert "'fine'@1" in text


def test_the_walk_reaches_every_ancestor_of_a_longer_chain() -> None:
    chain = Chain()
    zone = _grouping(
        "zone", "area", {"R1": "Z", "R2": "Z"}, UnseenLevelBehaviour.MAP_TO_BASE,
        parent=chain.region,
    )
    zone_factor = Factor(
        id=uuid4(), slug="zone_f", dataset_id=DATASET, version=1, type=FactorType.GROUPING,
        source_columns=("area",), grouping_id=zone.id,
    )
    spec = chain.spec.model_copy(update={"factors": (zone_factor.id, chain.factors[1].id)})
    book = pl.DataFrame(
        {
            "area": ["R1", "R2"] * 200, "fuel": ["x", "y"] * 200, "exposure": [1.0] * 400,
            "claims": [0.0, 1.0] * 200,
        }
    )
    factors = [zone_factor, chain.factors[1]]
    groupings = {zone.id: zone, chain.region.id: chain.region, chain.fine.id: chain.fine}
    fit = fit_glm(book, spec, factors, groupings={zone.id: zone}).result

    def score(area: str) -> float:
        return float(
            predict_glm(
                fit, pl.DataFrame({"area": [area], "fuel": ["x"], "exposure": [1.0]}),
                factors, spec, groupings=groupings,
            )[0]
        )

    assert score("R1") > 0 or score("R1") == 0
    assert _raises(score, "AB").code == CODE  # an ancestor two links up
    assert _raises(score, "AB1").code == CODE
    assert [g.slug for g in grouping_ancestors(zone, groupings)] == ["region", "fine"]


def test_ancestors_stop_at_a_missing_link_and_never_loop() -> None:
    chain = Chain()
    assert grouping_ancestors(chain.region, chain.groupings(False)) == ()
    loop = chain.fine.model_copy(update={"parent_grouping_id": chain.region.id})
    found = grouping_ancestors(chain.region, {chain.region.id: chain.region, loop.id: loop})
    assert [g.slug for g in found] == ["fine"]


# --- the `error` message counts, it does not list ------------------------------------------


def test_an_error_behaviour_refusal_names_a_count_never_the_values() -> None:
    chain = Chain(UnseenLevelBehaviour.ERROR)
    for call in (chain.frame, chain.row):
        with pytest.raises(FactorResolutionError) as refused:
            call(SENTINEL)
        text = str(refused.value)
        assert SENTINEL not in text
        assert "1 level" in text


# --- the raise site, called directly -------------------------------------------------------


@pytest.mark.req("NFR-499", "FR-109")
def test_the_refusal_resolve_factor_columns_raises_names_no_level() -> None:
    """The one resolution every caller shares: fit, predict, score and the rate-table weights.

    `test_error_sinks.py` registers the re-wrap in `resolve_factor_columns` (`{refused}` in its
    f-string) on the strength of this test, so the text is proved free of a level here, once, at
    the raise site, for every caller. The sentinel is a source level of the ancestor and the
    value of the column in the frame; the control is that the text names the Factor, the
    Groupings of the chain and the column, so it is there to be searched.
    """
    chain = Chain()
    frame = pl.DataFrame({"area": [SENTINEL], "fuel": ["x"]})
    with pytest.raises(GroupingAncestorLevelError) as refused:
        resolve_factor_columns(frame, chain.factors, groupings=chain.groupings())
    assert isinstance(refused.value, CodedError)
    assert refused.value.code == CODE
    text = str(refused.value)
    for named in ("'region_f'", "'region'@1", "'fine'@1", "'area'"):
        assert named in text, f"control: the refusal names {named}"
    assert SENTINEL not in text
    assert SENTINEL not in safe_error_detail(refused.value)
