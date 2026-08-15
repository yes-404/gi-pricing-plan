"""Groupings against levels whose true structure is known (`02` FR-MODEL-13..17).

The book below has twenty observed levels drawn from **four** distinct underlying rates, so
a proposal asked for four groups has a right answer and the evidence has a right shape: the
merge should cost almost no deviance, because there was almost nothing there to lose.

The rest is refusal. FR-MODEL-13 makes unseen-level behaviour mandatory, and the reason a
default is forbidden is that the wrong one prices an unknown vehicle group as the cheapest
cell in the book.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    CredibilityModel,
    Grouping,
    GroupingMethod,
    GroupingProposal,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import (
    FactorResolutionError,
    GroupingError,
    apply_grouping,
    grouping_evidence,
    propose_grouping,
)

DATASET = uuid4()
VERSION = uuid4()

#: Twenty levels, four true rates. `L00`-`L04` share one, `L05`-`L09` the next, and so on.
_TRUE_EFFECT = {f"L{i:02d}": [0.6, 0.9, 1.3, 1.9][i // 5] for i in range(20)}


def _book(n: int = 40_000, seed: int = 20260815) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    level = rng.choice(sorted(_TRUE_EFFECT), n)
    exposure = rng.uniform(0.5, 1.0, n)
    rate = np.array([_TRUE_EFFECT[x] for x in level]) * 0.08
    counts = rng.poisson(rate * exposure)
    return pl.DataFrame(
        {
            "vehicle_group": level,
            "exposure_years": exposure,
            "claim_count": counts.astype(float),
            "claim_amount_minor": (counts * 200_000).astype(np.int64),
        }
    )


def _proposal(**over: object) -> GroupingProposal:
    base: dict[str, object] = {
        "dataset_version_id": VERSION,
        "column": "vehicle_group",
        "method": GroupingMethod.HIERARCHICAL_CLUSTERING,
        "n_groups": 4,
        "unseen_level_behaviour": UnseenLevelBehaviour.ERROR,
    }
    base.update(over)
    return GroupingProposal(**base)  # type: ignore[arg-type]


def _manual(**over: object) -> Grouping:
    base: dict[str, object] = {
        "id": uuid4(), "slug": "vg", "dataset_id": DATASET, "version": 1,
        "column": "vehicle_group", "method": GroupingMethod.MANUAL,
        "mapping": {"L00": "A", "L01": "A", "L02": "B"},
        "unseen_level_behaviour": UnseenLevelBehaviour.ERROR,
    }
    base.update(over)
    return Grouping(**base)  # type: ignore[arg-type]


# --- the shape of a Grouping ------------------------------------------------------------


@pytest.mark.req("FR-MODEL-13")
def test_unseen_level_behaviour_has_no_default() -> None:
    """The field is mandatory, so a caller cannot omit the decision and get one anyway."""
    with pytest.raises(ValueError, match="unseen_level_behaviour"):
        Grouping(
            id=uuid4(), slug="vg", dataset_id=DATASET, version=1, column="c",
            method=GroupingMethod.MANUAL, mapping={"a": "A"},
        )  # type: ignore[call-arg]


@pytest.mark.req("FR-MODEL-13")
def test_map_to_default_must_name_a_default_that_exists() -> None:
    with pytest.raises(ValueError, match="names no default"):
        _manual(unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT)
    with pytest.raises(ValueError, match="not one of its target levels"):
        _manual(
            unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
            default_target_level="Z",
        )


@pytest.mark.req("FR-MODEL-13")
def test_a_default_nobody_consults_is_refused() -> None:
    """It reads as protection that is not there."""
    with pytest.raises(ValueError, match="reads as protection"):
        _manual(default_target_level="A")


@pytest.mark.req("FR-MODEL-80")
def test_a_credibility_model_belongs_only_to_the_method_that_uses_one() -> None:
    """It lives in `method_params`, which is where `grouping.schema.json` has always had it."""
    with pytest.raises(ValueError, match="does not use one"):
        _manual(method_params={"credibility_model": "limited_fluctuation"})


@pytest.mark.req("FR-MODEL-80")
def test_an_unknown_credibility_model_is_refused() -> None:
    """`method_params` is loosely typed by the contract; the enum is still closed."""
    with pytest.raises(ValueError, match="not one of"):
        _manual(
            method=GroupingMethod.CREDIBILITY_WEIGHTED,
            method_params={"credibility_model": "vibes"},
        )


# --- proposing --------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-14")
def test_clustering_recovers_the_levels_that_share_a_rate() -> None:
    """Twenty levels, four true rates: the proposal must not split a true group."""
    grouping = propose_grouping(_book(), _proposal(), dataset_id=DATASET, slug="vg-4")

    assert len(grouping.target_levels) == 4
    by_truth: dict[float, set[str]] = {}
    for level, target in grouping.mapping.items():
        by_truth.setdefault(_TRUE_EFFECT[level], set()).add(target)
    assert all(len(targets) == 1 for targets in by_truth.values()), grouping.mapping


@pytest.mark.req("FR-MODEL-15")
def test_the_evidence_says_what_the_merge_cost() -> None:
    """FR-MODEL-15: a grouping is a modelling decision and must be defensible as one.

    Collapsing twenty levels that are really four should give up almost no deviance, so the
    likelihood-ratio p-value is high — "these could be the same" is the honest reading.
    """
    grouping = propose_grouping(_book(), _proposal(), dataset_id=DATASET, slug="vg-4")
    evidence = grouping.evidence
    assert evidence is not None
    assert evidence.source_level_count == 20
    assert evidence.target_level_count == 4
    assert evidence.df_saved == 16
    assert evidence.deviance_before is not None
    assert evidence.deviance_after is not None
    # Merging can only make the fit worse; the question is by how much.
    assert evidence.deviance_after >= evidence.deviance_before
    assert evidence.chi2_p_value is not None
    assert evidence.chi2_p_value > 0.05
    assert len(evidence.target_level_stats) == 4


@pytest.mark.req("FR-MODEL-15")
def test_a_merge_that_destroys_real_signal_is_reported_as_one() -> None:
    """The p-value has to move, or it is decoration.

    Collapsing all twenty levels into one throws away four genuinely different rates, and
    the evidence must say so rather than reporting the same comfortable number.
    """
    frame = _book()
    everything = dict.fromkeys(sorted(_TRUE_EFFECT), "ONE")
    evidence = grouping_evidence(frame, everything, column="vehicle_group")
    assert evidence.chi2_p_value is not None
    assert evidence.chi2_p_value < 1e-6


@pytest.mark.req("FR-MODEL-14")
def test_credibility_weighted_merges_on_shrunk_rates() -> None:
    """Limited fluctuation, named on the artifact so a reviewer knows which theory ran."""
    grouping = propose_grouping(
        _book(),
        _proposal(method=GroupingMethod.CREDIBILITY_WEIGHTED),
        dataset_id=DATASET,
        slug="vg-cred",
    )
    assert grouping.credibility_model is CredibilityModel.LIMITED_FLUCTUATION
    # FR-MODEL-80: the (p, k) pair is stored beside the count it implies, so a reviewer can
    # check one against the other rather than take 1 082 on faith.
    assert grouping.method_params["credibility_pk"] == {"p": 0.90, "k": 0.05}
    assert grouping.method_params["credibility_standard_claims"] == 1082
    assert 1 < len(grouping.target_levels) < 20
    assert set(grouping.mapping) == set(_TRUE_EFFECT)


@pytest.mark.req("FR-MODEL-14")
def test_buhlmann_straub_is_refused_rather_than_silently_substituted() -> None:
    """FR-MODEL-80 specifies it and this build does not implement it.

    Refused rather than substituted: the requirement makes the model a recorded property of
    the grouping, so returning limited fluctuation's answer under its name would be the one
    failure it exists to prevent — and `credibility_components` would come back null for a
    model that is meant to persist them.
    """
    with pytest.raises(GroupingError, match="not implemented"):
        propose_grouping(
            _book(),
            _proposal(
                method=GroupingMethod.CREDIBILITY_WEIGHTED,
                credibility_model=CredibilityModel.BUHLMANN_STRAUB,
            ),
            dataset_id=DATASET,
            slug="vg-bs",
        )


@pytest.mark.req("FR-MODEL-14")
@pytest.mark.parametrize(
    ("method", "fragment"),
    [
        (GroupingMethod.MANUAL, "nothing to propose"),
        (GroupingMethod.TREE, "tree"),
        (GroupingMethod.REFERENCE_HIERARCHY, "reference_hierarchy"),
    ],
)
def test_unimplemented_methods_are_refused_by_name(
    method: GroupingMethod, fragment: str
) -> None:
    with pytest.raises(GroupingError, match=fragment):
        propose_grouping(_book(), _proposal(method=method), dataset_id=DATASET, slug="x")


@pytest.mark.req("FR-MODEL-13")
def test_a_proposal_defaults_unseen_levels_to_the_largest_group() -> None:
    """Where it is least wrong: a thin cell would hand it that cell's standard error."""
    grouping = propose_grouping(
        _book(),
        _proposal(unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT),
        dataset_id=DATASET,
        slug="vg-default",
    )
    assert grouping.default_target_level in grouping.target_levels

    stats = {row.level: float(row.exposure_years) for row in grouping.evidence.target_level_stats}  # type: ignore[union-attr]
    assert grouping.default_target_level == max(stats, key=lambda level: stats[level])


# --- applying ---------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-13")
def test_an_unseen_level_is_named_when_the_behaviour_is_error() -> None:
    with pytest.raises(FactorResolutionError, match="L99"):
        apply_grouping(pl.Series("vehicle_group", ["L00", "L99"]), _manual())


@pytest.mark.req("FR-MODEL-13")
def test_an_unseen_level_reaches_the_declared_default() -> None:
    grouping = _manual(
        unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
        default_target_level="B",
    )
    mapped = apply_grouping(pl.Series("vehicle_group", ["L00", "L99"]), grouping)
    assert mapped.to_list() == ["A", "B"]


@pytest.mark.req("FR-MODEL-13")
def test_map_to_base_sends_an_unseen_level_to_the_first_target() -> None:
    grouping = _manual(unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_BASE)
    mapped = apply_grouping(pl.Series("vehicle_group", ["L02", "L99"]), grouping)
    assert mapped.to_list() == ["B", "A"]


@pytest.mark.req("FR-MODEL-13")
def test_a_null_level_is_not_a_group() -> None:
    """`02` §4.3 gives a Grouping no null level, so a missing value cannot be mapped to one."""
    with pytest.raises(FactorResolutionError, match="null value"):
        apply_grouping(pl.Series("vehicle_group", ["L00", None]), _manual())


@pytest.mark.req("FR-MODEL-17")
def test_a_grouping_can_name_its_parent_in_a_chain() -> None:
    """FR-MODEL-17: outcode rolls to area rolls to region, and the chain is recorded."""
    area = _manual(slug="area", mapping={"AB1": "AB", "AB2": "AB", "CD1": "CD"})
    region = _manual(
        slug="region", mapping={"AB": "NORTH", "CD": "SOUTH"}, parent_grouping_id=area.id
    )
    assert region.parent_grouping_id == area.id
    rolled = apply_grouping(apply_grouping(pl.Series("vehicle_group", ["AB2"]), area), region)
    assert rolled.to_list() == ["NORTH"]
