"""A banding or grouping factor resolves through its artifact — or not at all (FR-MODEL-1).

This file exists because of what an injection found. Deleting the banding branch of
`resolve_factors`, so that a `banding` factor silently returned its raw column, broke
**nothing**: the banding suite tested `apply_banding` directly and the GLM suite only ever
fitted `identity` factors. The one thing FR-MODEL-1's closed set is *for* — that a factor's
declared type is the transformation actually applied — had no test at all.

The fit at the end is the real assertion: a banded age factor fitted on a book with three
plateaus recovers three levels with the right relativities, which an unbanded fit on the
raw column cannot produce.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorIntent,
    FactorType,
    GlmSpec,
    Grouping,
    GroupingMethod,
    OffsetSpec,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import FactorResolutionError, fit_glm, resolve_factors

DATASET = uuid4()

#: Age drives frequency in three flat steps, so the *banded* factor is the correct model
#: and every relativity has a known value: the ratio of two steps.
_STEP = {0: 0.05, 1: 0.075, 2: 0.10}

#: The same steps, keyed by the band label that covers them.
_BAND_STEP = {"18-37": 0.10, "38-57": 0.075, "58+": 0.05}


def _book(n: int = 30_000, seed: int = 20260815) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    step = np.where(age < 38, 2, np.where(age < 58, 1, 0))
    exposure = rng.uniform(0.5, 1.0, n)
    counts = rng.poisson(np.array([_STEP[s] for s in step]) * exposure)
    region = rng.choice(["N1", "N2", "S1", "S2"], n)
    return pl.DataFrame(
        {
            "driver_age": age,
            "region": region,
            "exposure_years": exposure,
            "claim_count": counts.astype(float),
            "claim_amount_minor": (counts * 200_000).astype(np.int64),
        }
    )


def _banding() -> Banding:
    """Bands cut exactly where the steps are, so a correct resolution is unambiguous."""
    return Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1,
        column="driver_age", method=BandingMethod.MANUAL,
        boundaries=(18.0, 38.0, 58.0, 78.0), labels=("18-37", "38-57", "58+"),
    )


def _grouping() -> Grouping:
    return Grouping(
        id=uuid4(), slug="region-ns", dataset_id=DATASET, version=1,
        column="region", method=GroupingMethod.MANUAL,
        mapping={"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH", "S2": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )


def _factor(slug: str, column: str, **over: object) -> Factor:
    base: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": DATASET, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    base.update(over)
    return Factor(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-1")
def test_a_banding_factor_resolves_to_its_bands_not_its_column() -> None:
    """The claim the injection proved untested: the declared type is what gets applied."""
    banding = _banding()
    factor = _factor(
        "age_banded", "driver_age", type=FactorType.BANDING, banding_id=banding.id
    )
    matrix = resolve_factors(_book(500), [factor], bandings={banding.id: banding})

    column = matrix.terms["age_banded"]
    assert column != "driver_age"
    assert column in matrix.categorical
    assert set(matrix.frame[column].unique().to_list()) <= set(banding.labels)


@pytest.mark.req("FR-MODEL-1")
def test_a_grouping_factor_resolves_to_its_target_levels() -> None:
    grouping = _grouping()
    factor = _factor(
        "region_ns", "region", type=FactorType.GROUPING, grouping_id=grouping.id
    )
    matrix = resolve_factors(_book(500), [factor], groupings={grouping.id: grouping})
    column = matrix.terms["region_ns"]
    assert sorted(matrix.frame[column].unique().to_list()) == ["NORTH", "SOUTH"]


@pytest.mark.req("FR-MODEL-1")
def test_a_banding_factor_without_its_banding_is_refused() -> None:
    """Not a fallback to the raw column: that is a different model wearing this one's name."""
    banding = _banding()
    factor = _factor(
        "age_banded", "driver_age", type=FactorType.BANDING, banding_id=banding.id
    )
    with pytest.raises(FactorResolutionError, match="was not supplied"):
        resolve_factors(_book(100), [factor])


@pytest.mark.req("FR-MODEL-1")
def test_a_grouping_factor_without_its_grouping_is_refused() -> None:
    grouping = _grouping()
    factor = _factor(
        "region_ns", "region", type=FactorType.GROUPING, grouping_id=grouping.id
    )
    with pytest.raises(FactorResolutionError, match="was not supplied"):
        resolve_factors(_book(100), [factor])


@pytest.mark.req("FR-MODEL-1")
def test_a_banding_of_a_different_column_is_refused() -> None:
    """Bands, a fit, and nonsense — the failure a name check costs nothing to prevent."""
    banding = _banding()
    factor = _factor(
        "wrong", "exposure_years", type=FactorType.BANDING, banding_id=banding.id
    )
    with pytest.raises(FactorResolutionError, match="pins a banding of"):
        resolve_factors(_book(100), [factor], bandings={banding.id: banding})


@pytest.mark.req("FR-MODEL-1")
def test_the_type_and_its_transformation_must_agree_on_the_factor_itself() -> None:
    """Both directions: a banding with no artifact, and an artifact on a non-banding."""
    with pytest.raises(ValueError, match="names no banding_id"):
        _factor("b", "driver_age", type=FactorType.BANDING)
    with pytest.raises(ValueError, match="names a banding_id"):
        _factor("i", "driver_age", banding_id=uuid4())
    with pytest.raises(ValueError, match="names no grouping_id"):
        _factor("g", "region", type=FactorType.GROUPING)


@pytest.mark.req("FR-MODEL-1")
def test_two_bandings_of_one_column_are_two_design_columns() -> None:
    """Both writing back to `driver_age` would leave the second silently overwriting the first."""
    coarse = _banding()
    fine = Banding(
        id=uuid4(), slug="age-fine", dataset_id=DATASET, version=1,
        column="driver_age", method=BandingMethod.MANUAL,
        boundaries=(18.0, 28.0, 38.0, 48.0, 58.0, 78.0),
        labels=("18-27", "28-37", "38-47", "48-57", "58+"),
    )
    factors = [
        _factor("age_coarse", "driver_age", type=FactorType.BANDING, banding_id=coarse.id),
        _factor("age_fine", "driver_age", type=FactorType.BANDING, banding_id=fine.id),
    ]
    matrix = resolve_factors(
        _book(500), factors, bandings={coarse.id: coarse, fine.id: fine}
    )
    assert len(set(matrix.terms.values())) == 2
    assert matrix.frame[matrix.terms["age_coarse"]].n_unique() == 3
    assert matrix.frame[matrix.terms["age_fine"]].n_unique() == 5


@pytest.mark.req("FR-MODEL-21")
def test_a_glm_through_a_banding_and_a_grouping_recovers_the_step_relativities() -> None:
    """End to end: the transformation is applied, and the numbers prove which one ran.

    Age drives frequency in three flat steps of 0.05 / 0.075 / 0.10. Banded on the step
    boundaries and based on the widest band, the fitted relativities must be near 1.5 and
    2.0 — values a fit on the raw column, or on an unbanded factor, cannot produce.
    """
    banding, grouping = _banding(), _grouping()
    factors = [
        _factor("age_banded", "driver_age", type=FactorType.BANDING, banding_id=banding.id),
        _factor("region_ns", "region", type=FactorType.GROUPING, grouping_id=grouping.id),
    ]
    spec = GlmSpec(
        model_family_slug="steps",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors),
    )
    result = fit_glm(
        _book(),
        spec,
        factors,
        bandings={banding.id: banding},
        groupings={grouping.id: grouping},
    ).result

    age = {row.level: row for row in result.relativities["age_banded"]}
    assert set(age) == set(_BAND_STEP)

    # The base is whichever band holds the most exposure (`02` §4.1's `largest_exposure`),
    # which an even age draw leaves to the data rather than to the test. So the assertion
    # is on the *ratios*, which is what a relativity is: each band's fitted relativity must
    # be its true step divided by the base band's.
    base = next(level for level, row in age.items() if row.is_base)
    assert age[base].relativity == pytest.approx(1.0)
    for level, step in _BAND_STEP.items():
        assert age[level].relativity == pytest.approx(
            step / _BAND_STEP[base], rel=0.12
        ), (level, base, age[level].relativity)

    # The relativity table weights levels by exposure, which only works because the
    # resolved column reached the frame the table is built from.
    assert all(row.exposure is not None and row.exposure > 0 for row in age.values())

    region = {row.level: row for row in result.relativities["region_ns"]}
    assert set(region) == {"NORTH", "SOUTH"}


# -- Intent, the second refusal axis (OQ-MODEL-25, decided 2026-08-22) -------------------
#
# `Factor.intent` was read in exactly one place in the repository — `rateable()`, which no
# production code calls yet because `03` is unbuilt — so no arm of the enum changed a fit.
# `risk` and `control` were correct by coincidence: being fitted with a free coefficient is
# what both *mean*. `offset` and `diagnostic`, the two arms FR-MODEL-3 never glossed, were
# accepted through the API and quietly fitted the same way. These are the tests that were
# missing while that was true.


@pytest.mark.req("FR-MODEL-116")
def test_an_offset_intent_factor_is_refused_and_the_refusal_is_permanent() -> None:
    """FR-MODEL-116: superseded, so the message must not say "yet"."""
    factor = _factor("exposure_offset", "exposure_years", intent=FactorIntent.OFFSET)
    with pytest.raises(FactorResolutionError) as excinfo:
        resolve_factors(_book(200), [factor])

    message = str(excinfo.value)
    assert "exposure_offset" in message
    assert "FR-MODEL-116" in message
    assert "superseded" in message
    # The distinction FR-MODEL-114 draws for the type arm, held here for the intent arm:
    # a permanent refusal that reads as a pending one invites a caller to wait for it.
    assert "yet" not in message


@pytest.mark.req("FR-MODEL-117")
def test_a_diagnostic_intent_factor_is_refused_and_the_refusal_is_pending() -> None:
    """FR-MODEL-117: refused because it has no meaning, not because it will never have one."""
    factor = _factor("age_watch", "driver_age", intent=FactorIntent.DIAGNOSTIC)
    with pytest.raises(FactorResolutionError) as excinfo:
        resolve_factors(_book(200), [factor])

    message = str(excinfo.value)
    assert "FR-MODEL-117" in message
    assert "OQ-MODEL-27" in message
    # The two arms do not share a reason, and a reader must be able to tell which applies.
    assert "superseded" not in message


@pytest.mark.req("FR-MODEL-3")
def test_risk_and_control_intents_still_resolve_and_are_fitted() -> None:
    """The other half of the refusal: it must not swallow the two arms that are correct.

    FR-MODEL-3's amendment of 2026-08-22 states what the enum had never said — `risk` and
    `control` both enter the design matrix with a free coefficient and differ only in
    rateability. A refusal that caught them would be a worse defect than the one it fixed.
    """
    risk = _factor("age", "driver_age")
    control = _factor("region_control", "region", intent=FactorIntent.CONTROL)
    matrix = resolve_factors(_book(200), [risk, control])

    assert set(matrix.terms) == {"age", "region_control"}


@pytest.mark.req("FR-MODEL-116")
def test_the_intent_refusal_reaches_the_fit_and_not_only_the_resolver() -> None:
    """Sited in `resolve_factors` precisely so every path inherits it.

    Asserting it on `resolve_factors` alone would prove the refusal exists, not that a fit
    is unable to route around it — which is the claim FR-MODEL-116 actually makes.
    """
    factor = _factor("exposure_offset", "exposure_years", intent=FactorIntent.OFFSET)
    spec = GlmSpec(
        model_family_slug="steps",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=(factor.id,),
    )
    with pytest.raises(FactorResolutionError, match="FR-MODEL-116"):
        fit_glm(_book(2_000), spec, [factor])


@pytest.mark.req("FR-MODEL-116")
def test_an_interaction_declaring_a_refused_intent_is_refused_too() -> None:
    """The check sits above the second-pass `continue`, which is why this holds.

    An `interaction` is deferred to a second pass part-way down the loop. A refusal placed
    after that deferral would let exactly one factor type through — and it is the type that
    reaches the design matrix carrying its operands with it.
    """
    left = _factor("age", "driver_age")
    right = _factor("region", "region")
    cross = _factor(
        "age_x_region", "driver_age",
        type=FactorType.INTERACTION,
        source_columns=(),
        operand_factor_ids=(left.id, right.id),
        intent=FactorIntent.OFFSET,
    )
    with pytest.raises(FactorResolutionError, match="FR-MODEL-116"):
        resolve_factors(_book(200), [left, right, cross])
