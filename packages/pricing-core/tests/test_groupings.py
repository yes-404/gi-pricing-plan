"""Groupings against levels whose true structure is known (`02` FR-104, FR-105, FR-107, FR-108, FR-109).

The book below has twenty observed levels drawn from **four** distinct underlying rates, so
a proposal asked for four groups has a right answer and the evidence has a right shape: the
merge should cost almost no deviance, because there was almost nothing there to lose.

The rest is refusal. FR-104 makes unseen-level behaviour mandatory, and the reason a
default is forbidden is that the wrong one prices an unknown vehicle group as the cheapest
cell in the book.
"""

from __future__ import annotations

import math
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
from pricing_core.data.profile import one_way
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


def _flat_book(levels: int = 5, exposure: float = 100.0, claims: int = 10) -> pl.DataFrame:
    """Levels with **exactly** equal observed frequencies — no simulation, no seed.

    `Sum m_i (X_i - Xbar)²` is then zero by construction, so Bühlmann-Straub's unbiased
    estimate of VHM is `-(I - 1) s² / scale`: strictly negative, every time. A random book
    that happens to produce a negative estimate would test the same branch on a coin toss.
    """
    return pl.DataFrame(
        {
            "vehicle_group": [f"L{i:02d}" for i in range(levels)],
            "exposure_years": [exposure] * levels,
            "claim_count": [float(claims)] * levels,
            "claim_amount_minor": np.array([claims * 200_000] * levels, dtype=np.int64),
        }
    )


def _dominant_book() -> pl.DataFrame:
    """One level holding all but a rounding error of the exposure.

    `m_dot - Sum m_i² / m_dot` underflows to zero, which is a different degeneracy from a
    negative VHM and would otherwise divide by it.
    """
    return pl.DataFrame(
        {
            "vehicle_group": ["BIG", "TINY"],
            "exposure_years": [1e16, 1.0],
            "claim_count": [1e15, 1.0],
            "claim_amount_minor": np.array([2_000_000, 200_000], dtype=np.int64),
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


@pytest.mark.req("FR-104")
def test_unseen_level_behaviour_has_no_default() -> None:
    """The field is mandatory, so a caller cannot omit the decision and get one anyway."""
    with pytest.raises(ValueError, match="unseen_level_behaviour"):
        Grouping(
            id=uuid4(), slug="vg", dataset_id=DATASET, version=1, column="c",
            method=GroupingMethod.MANUAL, mapping={"a": "A"},
        )  # type: ignore[call-arg]


@pytest.mark.req("FR-104")
def test_map_to_default_must_name_a_default_that_exists() -> None:
    with pytest.raises(ValueError, match="names no default"):
        _manual(unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT)
    with pytest.raises(ValueError, match="not one of its target levels"):
        _manual(
            unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
            default_target_level="Z",
        )


@pytest.mark.req("FR-104")
def test_a_default_nobody_consults_is_refused() -> None:
    """It reads as protection that is not there."""
    with pytest.raises(ValueError, match="reads as protection"):
        _manual(default_target_level="A")


@pytest.mark.req("FR-106")
def test_a_credibility_model_belongs_only_to_the_method_that_uses_one() -> None:
    """It lives in `method_params`, which is where `grouping.schema.json` has always had it."""
    with pytest.raises(ValueError, match="does not use one"):
        _manual(method_params={"credibility_model": "limited_fluctuation"})


@pytest.mark.req("FR-106")
def test_an_unknown_credibility_model_is_refused() -> None:
    """`method_params` is loosely typed by the contract; the enum is still closed."""
    with pytest.raises(ValueError, match="not one of"):
        _manual(
            method=GroupingMethod.CREDIBILITY_WEIGHTED,
            method_params={"credibility_model": "vibes"},
        )


# --- proposing --------------------------------------------------------------------------


@pytest.mark.req("FR-105")
def test_clustering_recovers_the_levels_that_share_a_rate() -> None:
    """Twenty levels, four true rates: the proposal must not split a true group."""
    grouping = propose_grouping(_book(), _proposal(), dataset_id=DATASET, slug="vg-4")

    assert len(grouping.target_levels) == 4
    by_truth: dict[float, set[str]] = {}
    for level, target in grouping.mapping.items():
        by_truth.setdefault(_TRUE_EFFECT[level], set()).add(target)
    assert all(len(targets) == 1 for targets in by_truth.values()), grouping.mapping


@pytest.mark.req("FR-103")
def test_a_tree_grouping_partitions_the_rate_order_and_separates_the_signal() -> None:
    """What a greedy weighted-SSE partition guarantees, and what it recovers.

    The guarantee is structural: leaves of a tree on one sorted feature are contiguous
    intervals of that feature, so the targets read as an ordered banding of a categorical —
    which is what a rate table can carry.

    The recovery claim is deliberately weaker than
    `test_clustering_recovers_the_levels_that_share_a_rate`'s, because on **this** book the
    two methods genuinely differ: the observed rates of the 0.072 and 0.104 groups overlap
    (`L09` at 0.086, `L10` at 0.098), and the greedy cut falls inside that overlap where
    Ward's merge order does not. Asserting the exact partition would be asserting the noise.
    So it asserts what is not noise — the two extremes stay whole and stay apart.
    """
    tree = propose_grouping(
        _book(), _proposal(method=GroupingMethod.TREE), dataset_id=DATASET, slug="vg-tree"
    )
    assert len(tree.target_levels) == 4
    assert set(tree.mapping) == set(_TRUE_EFFECT)

    cheapest = {tree.mapping[f"L{i:02d}"] for i in range(5)}
    dearest = {tree.mapping[f"L{i:02d}"] for i in range(15, 20)}
    assert len(cheapest) == 1
    assert len(dearest) == 1
    assert cheapest != dearest

    stats = tree.evidence.target_level_stats if tree.evidence else []
    rates = [row.claim_count / float(row.exposure_years) for row in stats]
    assert rates == sorted(rates), "leaves of a tree on one feature are contiguous in it"


@pytest.mark.req("FR-105")
def test_a_tree_grouping_is_not_ward_linkage_under_another_name() -> None:
    """FR-105 names both, and substituting one for the other was refused.

    A test that only checked the tree finds the right groups would pass just as well if
    `tree` dispatched to `_hierarchical`, which is the substitution the refusal existed to
    prevent — so this asks the two methods to disagree on the same book.
    """
    mappings = {
        method: propose_grouping(
            _book(), _proposal(method=method), dataset_id=DATASET, slug="vg-cmp"
        ).mapping
        for method in (GroupingMethod.TREE, GroupingMethod.HIERARCHICAL_CLUSTERING)
    }
    assert mappings[GroupingMethod.TREE] != mappings[GroupingMethod.HIERARCHICAL_CLUSTERING]


@pytest.mark.req("FR-103")
def test_a_tree_grouping_records_enough_to_reproduce_itself() -> None:
    """`n_groups` is on the proposal; `random_state` is only on the artifact if put there."""
    first = propose_grouping(
        _book(), _proposal(method=GroupingMethod.TREE), dataset_id=DATASET, slug="vg-tree"
    )
    again = propose_grouping(
        _book(), _proposal(method=GroupingMethod.TREE), dataset_id=DATASET, slug="vg-tree"
    )
    assert first.mapping == again.mapping
    assert first.method_params["random_state"] == 0
    assert first.method_params["min_samples_leaf"] == 1


@pytest.mark.req("FR-100")
def test_a_tree_grouping_still_places_every_level_it_cannot_rate() -> None:
    """A level with no exposure has no rate to split on, and no target level of its own.

    It goes to the largest cluster, as `hierarchical_clustering` already does — never to a
    group of its own, which would be FR-100's target level with no data behind it.
    """
    frame = pl.concat(
        [
            _book(),
            pl.DataFrame(
                {
                    "vehicle_group": ["L99"],
                    "exposure_years": [0.0],
                    "claim_count": [0.0],
                    "claim_amount_minor": [0],
                }
            ).with_columns(pl.col("claim_amount_minor").cast(pl.Int64)),
        ]
    )
    grouping = propose_grouping(
        frame, _proposal(method=GroupingMethod.TREE), dataset_id=DATASET, slug="vg-zero"
    )
    assert len(grouping.target_levels) == 4
    assert set(grouping.mapping) == set(_TRUE_EFFECT) | {"L99"}
    assert grouping.mapping["L99"] in grouping.target_levels


@pytest.mark.req("FR-107")
def test_the_evidence_says_what_the_merge_cost() -> None:
    """FR-107: a grouping is a modelling decision and must be defensible as one.

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


@pytest.mark.req("FR-107")
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


@pytest.mark.req("FR-107")
def test_the_evidence_carries_the_source_levels_it_collapsed() -> None:
    """FR-107 asks for source Level statistics, and the artifact carried none.

    `source_level_count` said twenty and nothing said *which* twenty, so "what were the
    cells we merged worth?" needed the one-way re-run against the dataset version the
    grouping was derived on — which is the recomputation the artifact exists to avoid.
    Declared in `grouping.schema.json` since Phase 0 and absent from the Python until
    2026-08-22; nothing caught it because the field is nested under `evidence` and the
    field-name comparison reads top-level names only.
    """
    grouping = propose_grouping(_book(), _proposal(), dataset_id=DATASET, slug="vg-4")
    evidence = grouping.evidence
    assert evidence is not None

    assert len(evidence.source_level_stats) == evidence.source_level_count == 20
    assert len(evidence.target_level_stats) == evidence.target_level_count == 4

    # The rows are the *source* levels, not the targets — the distinction the field exists
    # to make. Target names are generated (`_target_name`); source names come from the book.
    assert {row.level for row in evidence.source_level_stats} == set(_TRUE_EFFECT)
    assert {row.level for row in evidence.source_level_stats}.isdisjoint(
        {row.level for row in evidence.target_level_stats}
    )


@pytest.mark.req("FR-106")
def test_credibility_weighted_merges_on_shrunk_rates() -> None:
    """Limited fluctuation, named on the artifact so a reviewer knows which theory ran.

    Marked FR-105 until 2026-08-22. FR-105 names the *method*; the recorded
    model, the `(p, k)` pair and the standard it implies are all FR-106's, so
    `scope-audit.py` was crediting a requirement this test does not test.
    """
    grouping = propose_grouping(
        _book(),
        _proposal(method=GroupingMethod.CREDIBILITY_WEIGHTED),
        dataset_id=DATASET,
        slug="vg-cred",
    )
    assert grouping.credibility_model is CredibilityModel.LIMITED_FLUCTUATION
    # FR-106: the (p, k) pair is stored beside the count it implies, so a reviewer can
    # check one against the other rather than take 1 082 on faith.
    assert grouping.method_params["credibility_pk"] == {"p": 0.90, "k": 0.05}
    assert grouping.method_params["credibility_standard_claims"] == 1082
    assert 1 < len(grouping.target_levels) < 20
    assert set(grouping.mapping) == set(_TRUE_EFFECT)
    # No variance components: limited fluctuation estimates none, and a dict of zeros would
    # read as an estimate nobody made.
    assert grouping.evidence is not None
    assert grouping.evidence.credibility_components is None


@pytest.mark.req("FR-106")
def test_buhlmann_straub_is_selectable_and_persists_its_variance_components() -> None:
    """The second of OQ-579's two methods, built 2026-08-22.

    **This test previously asserted the opposite.** From 2026-08-15 until 2026-08-22 it was
    `test_buhlmann_straub_is_refused_rather_than_silently_substituted`: OQ-579 had
    decided *both* methods, one shipped, and the other raised rather than return limited
    fluctuation's answer under Bühlmann-Straub's name. The refusal was right while the
    variance components did not exist; the record of it stays here rather than being deleted,
    because "was it ever refused, and when did that change?" is a question a governed
    artifact has to be able to answer.

    What it asserts now is what the refusal was protecting: the model is recorded, and the
    components it is recorded *with* are the ones that produced the merge.
    """
    grouping = propose_grouping(
        _book(),
        _proposal(
            method=GroupingMethod.CREDIBILITY_WEIGHTED,
            credibility_model=CredibilityModel.BUHLMANN_STRAUB,
        ),
        dataset_id=DATASET,
        slug="vg-bs",
    )
    assert grouping.credibility_model is CredibilityModel.BUHLMANN_STRAUB
    assert grouping.evidence is not None
    components = grouping.evidence.credibility_components
    assert components is not None
    assert set(components) == {"evpv", "vhm", "k"}
    # `grouping.schema.json` gives `k` `exclusiveMinimum: 0`, and `k = EVPV / VHM` can only
    # satisfy it if both components are positive.
    assert components["evpv"] > 0
    assert components["vhm"] > 0
    assert components["k"] == pytest.approx(components["evpv"] / components["vhm"])
    # EVPV is E[lambda(Theta)] under the Poisson process variance — the portfolio frequency,
    # which this book generates at ~0.08 x mean(0.6, 0.9, 1.3, 1.9).
    assert components["evpv"] == pytest.approx(0.08 * 1.175, rel=0.15)
    # No limited-fluctuation standard: Bühlmann-Straub derives none, and recording the
    # proposal's untouched `(0.90, 0.05)` defaults would be a standard that did not run.
    assert "credibility_pk" not in grouping.method_params
    assert "credibility_standard_claims" not in grouping.method_params
    assert set(grouping.mapping) == set(_TRUE_EFFECT)


@pytest.mark.req("FR-106")
def test_the_two_credibility_models_disagree_on_thin_cells() -> None:
    """Two methods, not the same method under another name.

    The same objection `_tree` had to answer against Ward linkage (`groupings.py`'s
    "not the same method under another name"): OQ-579 decided *both* methods, so the
    second one has to be shown doing something the first does not.

    On a thin book each level carries ~6 claims, so limited fluctuation reads
    `Z = sqrt(6 / 1082) ~ 0.07` off a fixed standard and shrinks almost everything onto the
    portfolio rate — the sweep then merges nearly all of it. Bühlmann-Straub estimates `k`
    from *this* book, finds the levels genuinely far apart, and keeps far more of the
    observed spread. Same rows, same tolerance, different mapping.
    """
    thin = _book(n=1_200)
    limited = propose_grouping(
        thin,
        _proposal(method=GroupingMethod.CREDIBILITY_WEIGHTED),
        dataset_id=DATASET,
        slug="vg-lf",
    )
    buhlmann = propose_grouping(
        thin,
        _proposal(
            method=GroupingMethod.CREDIBILITY_WEIGHTED,
            credibility_model=CredibilityModel.BUHLMANN_STRAUB,
        ),
        dataset_id=DATASET,
        slug="vg-bs",
    )
    assert limited.mapping != buhlmann.mapping
    assert len(buhlmann.target_levels) > len(limited.target_levels)

    # And the mechanism, not just the outcome: the two Zs for the same thin level.
    assert buhlmann.evidence is not None
    components = buhlmann.evidence.credibility_components
    assert components is not None
    row = one_way(thin, column="vehicle_group").rows[0]
    exposure = float(row.exposure_years)
    z_limited = math.sqrt(min(row.claim_count / 1082, 1.0))
    z_buhlmann = exposure / (exposure + components["k"])
    assert z_limited < 0.15 < z_buhlmann


@pytest.mark.req("FR-106")
def test_a_reviewer_can_rederive_the_merge_from_the_stored_components() -> None:
    """FR-106's actual promise: re-derive `Z`, do not take it.

    The stored `(evpv, vhm, k)` plus the dataset version is enough to reproduce every
    level's credibility, its shrunk rate and therefore the whole mapping. Re-implemented
    here from the artifact alone — if the components were decorative, or estimated from
    different rows than the merge used, this reconstruction would not land on the same
    mapping.
    """
    frame = _book(n=1_200)
    grouping = propose_grouping(
        frame,
        _proposal(
            method=GroupingMethod.CREDIBILITY_WEIGHTED,
            credibility_model=CredibilityModel.BUHLMANN_STRAUB,
        ),
        dataset_id=DATASET,
        slug="vg-bs",
    )
    assert grouping.evidence is not None
    components = grouping.evidence.credibility_components
    assert components is not None

    shrunk: dict[str, float] = {}
    for row in one_way(frame, column="vehicle_group").rows:
        exposure = float(row.exposure_years)
        credibility = exposure / (exposure + components["k"])
        observed = row.claim_count / exposure
        shrunk[row.level] = credibility * observed + (1 - credibility) * components["evpv"]

    # The published sweep: ascending shrunk rate, a new target level whenever the rate
    # leaves `merge_tolerance_relativity` of the group's anchor (5 % by default).
    rederived: dict[str, str] = {}
    anchor: float | None = None
    index = 0
    for level in sorted(shrunk, key=lambda name: shrunk[name]):
        rate = shrunk[level]
        if anchor is not None and (anchor <= 0 or abs(rate - anchor) / anchor > 0.05):
            index += 1
            anchor = None
        if anchor is None:
            anchor = rate
        rederived[level] = f"G{index + 1}"

    assert rederived == grouping.mapping


@pytest.mark.req("FR-106")
@pytest.mark.req("FR-118")
@pytest.mark.parametrize(
    ("frame", "fragment"),
    [
        pytest.param(_flat_book(), "not positive", id="between-level-variance-non-positive"),
        pytest.param(_flat_book(levels=1), "at least two levels", id="one-exposed-level"),
        pytest.param(_flat_book(claims=0), "no claims", id="no-claims"),
        pytest.param(_dominant_book(), "all of the exposure", id="one-level-holds-everything"),
    ],
)
def test_buhlmann_straub_refuses_a_book_it_cannot_estimate_on(
    frame: pl.DataFrame, fragment: str
) -> None:
    """The degenerate cases are refused by name, never clamped into a plausible `k`.

    A non-positive VHM estimate is routine on real data — it is the finding that the levels'
    spread is no wider than Poisson noise, which makes `Z = 0` for every level and `k`
    unbounded. Clamping `a` to some small positive number would produce an artifact carrying
    a credibility nobody computed, which is what `grouping.schema.json`'s
    `exclusiveMinimum: 0` on `k` is there to stop. `limited_fluctuation` needs no
    between-level estimate and is still available on exactly this book.
    """
    proposal = _proposal(
        method=GroupingMethod.CREDIBILITY_WEIGHTED,
        credibility_model=CredibilityModel.BUHLMANN_STRAUB,
    )
    with pytest.raises(GroupingError, match=fragment) as raised:
        propose_grouping(frame, proposal, dataset_id=DATASET, slug="vg-bs")
    # Its own code: `GROUPING_NOT_EXHAUSTIVE` is about a mapping that misses a level, and a
    # caller cannot act on it here — the mapping is fine, the book is thin.
    assert raised.value.code == "CREDIBILITY_VARIANCE_NOT_ESTIMABLE"


@pytest.mark.req("FR-106")
def test_limited_fluctuation_still_groups_the_book_buhlmann_straub_refuses() -> None:
    """The refusal above is Bühlmann-Straub's, not the platform giving up on the column."""
    grouping = propose_grouping(
        _flat_book(),
        _proposal(method=GroupingMethod.CREDIBILITY_WEIGHTED),
        dataset_id=DATASET,
        slug="vg-lf-flat",
    )
    assert grouping.credibility_model is CredibilityModel.LIMITED_FLUCTUATION
    assert grouping.evidence is not None
    assert grouping.evidence.credibility_components is None


@pytest.mark.req("FR-105")
@pytest.mark.parametrize(
    ("method", "fragment"),
    [
        (GroupingMethod.MANUAL, "nothing to propose"),
        (GroupingMethod.REFERENCE_HIERARCHY, "reference_hierarchy"),
    ],
)
def test_unimplemented_methods_are_refused_by_name(
    method: GroupingMethod, fragment: str
) -> None:
    with pytest.raises(GroupingError, match=fragment):
        propose_grouping(_book(), _proposal(method=method), dataset_id=DATASET, slug="x")


@pytest.mark.req("FR-104")
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


@pytest.mark.req("FR-104")
def test_an_unseen_level_is_named_when_the_behaviour_is_error() -> None:
    with pytest.raises(FactorResolutionError, match="L99"):
        apply_grouping(pl.Series("vehicle_group", ["L00", "L99"]), _manual())


@pytest.mark.req("FR-104")
def test_an_unseen_level_reaches_the_declared_default() -> None:
    grouping = _manual(
        unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
        default_target_level="B",
    )
    mapped = apply_grouping(pl.Series("vehicle_group", ["L00", "L99"]), grouping)
    assert mapped.to_list() == ["A", "B"]


@pytest.mark.req("FR-104")
def test_map_to_base_sends_an_unseen_level_to_the_first_target() -> None:
    grouping = _manual(unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_BASE)
    mapped = apply_grouping(pl.Series("vehicle_group", ["L02", "L99"]), grouping)
    assert mapped.to_list() == ["B", "A"]


@pytest.mark.req("FR-104")
def test_a_null_level_is_not_a_group() -> None:
    """`02` §4.3 gives a Grouping no null level, so a missing value cannot be mapped to one."""
    with pytest.raises(FactorResolutionError, match="null value"):
        apply_grouping(pl.Series("vehicle_group", ["L00", None]), _manual())


@pytest.mark.req("FR-109")
def test_a_grouping_can_name_its_parent_in_a_chain() -> None:
    """FR-109: outcode rolls to area rolls to region, and the chain is recorded."""
    area = _manual(slug="area", mapping={"AB1": "AB", "AB2": "AB", "CD1": "CD"})
    region = _manual(
        slug="region", mapping={"AB": "NORTH", "CD": "SOUTH"}, parent_grouping_id=area.id
    )
    assert region.parent_grouping_id == area.id
    rolled = apply_grouping(apply_grouping(pl.Series("vehicle_group", ["AB2"]), area), region)
    assert rolled.to_list() == ["NORTH"]
