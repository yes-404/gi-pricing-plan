"""Groupings: merging Levels into ones a rate table can carry (`02` §3.3).

A grouping is the most consequential edit an actuary makes to a factor and the easiest one
to make invisibly — fifty vehicle groups become eight, every relativity moves, and the
model still fits. FR-MODEL-15 is the counterweight: the artifact carries the **change in
fit** the merge implies, so the decision is defensible as a decision.

* **FR-MODEL-13** — exhaustive over observed Levels, with `unseen_level_behaviour`
  mandatory. The mandatory part is enforced at the type (`Grouping` has no default);
  exhaustiveness is enforced here, against the version being fitted.
* **FR-MODEL-14** — `credibility_weighted`, `hierarchical_clustering` and `tree` are
  implemented; `tree` since FR-MODEL-85 (OQ-MODEL-9, decided 2026-08-17).
  `reference_hierarchy` is refused by name, for the reason the refusal gives.
* **FR-MODEL-15** — the evidence: source and target level counts, Poisson deviance before
  and after, degrees of freedom saved, and the likelihood-ratio p-value.
* **FR-MODEL-80** — both credibility theories OQ-MODEL-5 decided on (2026-08-15):
  `limited_fluctuation` (the default) and `buhlmann_straub`, chosen per grouping in
  `method_params` and differing **only** in `Z`. Bühlmann-Straub persists its variance
  components — EVPV, VHM and `k` — in the evidence, so a reviewer re-derives `Z` rather
  than taking it.

**Deviance is Poisson deviance of claim counts against exposure**, the response the merge
is judged on, computed from the level rates rather than from a refitted GLM. The question a
grouping answers is "how much of the between-level signal did the merge discard?", and a
one-factor comparison answers exactly that — without a second fit's factor set, offset and
convergence risk inside a proposal endpoint. It is therefore a **marginal** statement about
this factor alone, not the deviance the eventual multi-factor model will report.
"""

from __future__ import annotations

import math
from uuid import UUID

import numpy as np
import polars as pl
from scipy import stats

from model_schema import (
    CredibilityModel,
    Grouping,
    GroupingEvidence,
    GroupingMethod,
    GroupingProposal,
    OneWayRow,
    OneWaySummary,
    UnseenLevelBehaviour,
    new_uuid7,
)
from pricing_core.data.profile import one_way
from pricing_core.modelling.errors import FactorResolutionError, GroupingError

__all__ = ["apply_grouping", "grouping_evidence", "propose_grouping"]

def _full_credibility_claims(p: float, k: float) -> float:
    """The claim count at which a Poisson estimate is within ±`k` with probability `p`.

    `(z_{(1+p)/2} / k)²` — 1 082 at the classical `p = 0.90, k = 0.05`. **Derived, not
    tabulated**: FR-MODEL-80 stores the `(p, k)` pair beside the count precisely so a
    reviewer can check one against the other, and a hard-coded 1 082 sitting next to a
    stored `(0.99, 0.01)` would be exactly the unattributable number the requirement
    objects to.
    """
    return float((stats.norm.ppf((1.0 + p) / 2.0) / k) ** 2)


def _buhlmann_straub_components(
    source: tuple[OneWayRow, ...], *, column: str
) -> dict[str, float]:
    """EVPV, VHM and `k` for Buhlmann-Straub credibility on claim frequency (FR-MODEL-80).

    Each Level `i` is one risk, observed once: its weight `m_i` is exposure years and its
    observation `X_i` is the frequency `claim_count / m_i` — **the same rate limited
    fluctuation shrinks** (`_relativity`), so the two theories differ in `Z` and nowhere
    else, which is what makes the recorded choice meaningful.

    One observation per risk is why the textbook within-risk estimator of `s²`,
    `Sum_i Sum_j m_ij (X_ij - Xbar_i)² / Sum_i (n_i - 1)`, is unusable here: with `n_i = 1`
    both its numerator and its denominator are zero. The frequency case supplies `s²`
    directly instead. Claim counts are Poisson with `Var(N_i | Theta_i) = m_i lambda_i`, so
    `Var(X_i | Theta_i) = lambda_i / m_i` — exactly Buhlmann-Straub's `sigma²(Theta) / m_i`
    with `sigma²(Theta) = lambda(Theta)`. Hence

        EVPV = s² = E[sigma²(Theta)] = E[lambda(Theta)] = mu,

    estimated by the exposure-weighted portfolio frequency `Xbar = Sum m_i X_i / m_dot`.

    VHM is the standard unbiased between-risk estimator. Writing
    `T = Sum_i m_i (X_i - Xbar)²`, the model gives
    `E[T] = (I - 1) s² + a (m_dot - Sum_i m_i² / m_dot)`, so

        VHM = a = (T - (I - 1) s²) / (m_dot - Sum_i m_i² / m_dot),   k = s² / a,
        Z_i = m_i / (m_i + k).

    *Buhlmann & Gisler, `A Course in Credibility Theory and its Applications` (2005) §4.8
    for the estimators; the Poisson process-variance identity is the standard frequency
    specialisation — Klugman, Panjer & Willmot, `Loss Models`, greatest-accuracy
    credibility.*

    **Nothing here is clamped.** Every degenerate case is refused by name, because a
    non-positive `a` is not a small credibility — it is the finding that the levels are
    indistinguishable, and `grouping.schema.json` gives `k` `exclusiveMinimum: 0` precisely
    so an artifact cannot carry a credibility nobody could compute.
    """
    rows = [row for row in source if float(row.exposure_years) > 0]
    if len(rows) < 2:
        raise GroupingError(
            "CREDIBILITY_VARIANCE_NOT_ESTIMABLE",
            f"Buhlmann-Straub separates within-level from between-level variance and needs "
            f"at least two levels of {column!r} carrying exposure to do it; this version "
            f"has {len(rows)}. `limited_fluctuation` estimates nothing between levels and "
            "remains available (FR-MODEL-80).",
        )

    weights = np.asarray([float(row.exposure_years) for row in rows], dtype=np.float64)
    observed = np.asarray([float(row.claim_count) for row in rows], dtype=np.float64) / weights
    total_exposure = float(weights.sum())
    evpv = float((weights * observed).sum() / total_exposure)
    if evpv <= 0:
        raise GroupingError(
            "CREDIBILITY_VARIANCE_NOT_ESTIMABLE",
            f"{column!r} carries no claims on this version, so the Poisson process variance "
            "E[lambda(Theta)] is zero and Buhlmann-Straub's `k = s²/a` is 0/0. That is an "
            "absent credibility, not a small one (FR-MODEL-80).",
        )

    between = float((weights * (observed - evpv) ** 2).sum())
    scale = total_exposure - float((weights**2).sum()) / total_exposure
    if scale <= 0:
        raise GroupingError(
            "CREDIBILITY_VARIANCE_NOT_ESTIMABLE",
            f"one level of {column!r} holds effectively all of the exposure, so the "
            "between-level estimator's scale `m_dot - Sum m_i²/m_dot` collapses to zero and "
            "VHM is undefined. There is no second risk to be different from (FR-MODEL-80).",
        )

    vhm = (between - (len(rows) - 1) * evpv) / scale
    if vhm <= 0:
        raise GroupingError(
            "CREDIBILITY_VARIANCE_NOT_ESTIMABLE",
            f"Buhlmann-Straub's between-level variance estimate for {column!r} is "
            f"{vhm:.6g}, which is not positive: the levels' observed spread is no wider "
            "than Poisson noise on their exposures, so the model gives every level `Z = 0` "
            "and `k = s²/a` is unbounded. Refused rather than clamped — a clamped `k` would "
            "record a credibility nobody computed, and `grouping.schema.json` gives `k` "
            "`exclusiveMinimum: 0` for that reason. Re-run with `limited_fluctuation`, "
            "which needs no between-level estimate, or group a column that carries signal "
            "(FR-MODEL-80).",
        )
    return {"evpv": evpv, "vhm": vhm, "k": evpv / vhm}


def propose_grouping(
    frame: pl.DataFrame,
    proposal: GroupingProposal,
    *,
    dataset_id: UUID,
    slug: str,
) -> Grouping:
    """Propose a mapping of source Levels to target Levels (FR-MODEL-14).

    As with `propose_banding`, identity is the platform's to allocate, so `dataset_id` and
    `slug` arrive as arguments. The mapping comes back **editable**: FR-MODEL-14 says
    manual override is always available, which is only true if the proposal is a draft.
    """
    if proposal.method is GroupingMethod.MANUAL:
        raise GroupingError(
            "GROUPING_NOT_EXHAUSTIVE",
            "a `manual` grouping has nothing to propose — the mapping is the actuary's. "
            "Persist it directly.",
        )
    if proposal.method is GroupingMethod.REFERENCE_HIERARCHY:
        raise GroupingError(
            "GROUPING_NOT_EXHAUSTIVE",
            "`reference_hierarchy` rolls levels up through a Reference Table (`01` "
            "FR-DATA-30), which `pricing-core` cannot read — ADR-0001 keeps the database "
            "out of this package. It arrives as a platform-side proposal that supplies the "
            "hierarchy as data.",
        )

    if proposal.column not in frame.columns:
        raise FactorResolutionError(
            f"cannot group {proposal.column!r}: this dataset version does not have it "
            "(FR-MODEL-2)."
        )

    summary = one_way(
        frame,
        column=proposal.column,
        exposure_column=proposal.exposure_column,
        claim_count_column=proposal.claim_count_column,
        claim_amount_column=proposal.claim_amount_column,
    )
    source = tuple(summary.rows)
    if not source:
        raise GroupingError(
            "GROUPING_NOT_EXHAUSTIVE",
            f"{proposal.column!r} has no observed levels in this dataset version.",
        )

    if proposal.method is GroupingMethod.CREDIBILITY_WEIGHTED:
        clusters = _credibility_weighted(source, proposal)
    elif proposal.method is GroupingMethod.TREE:
        clusters = _tree(source, proposal)
    else:
        clusters = _hierarchical(source, proposal)

    mapping = {
        row.level: _target_name(index)
        for index, cluster in enumerate(clusters)
        for row in cluster
    }
    default = (
        _target_name(_largest_cluster(clusters))
        if proposal.unseen_level_behaviour is UnseenLevelBehaviour.MAP_TO_DEFAULT
        else None
    )
    if proposal.default_target_level:
        default = proposal.default_target_level

    return Grouping(
        id=new_uuid7(),
        slug=slug,
        dataset_id=dataset_id,
        version=1,
        column=proposal.column,
        method=proposal.method,
        method_params=_method_params(proposal),
        derived_on_dataset_version_id=proposal.dataset_version_id,
        mapping=mapping,
        unseen_level_behaviour=proposal.unseen_level_behaviour,
        default_target_level=default,
        evidence=grouping_evidence(
            frame,
            mapping,
            column=proposal.column,
            exposure_column=proposal.exposure_column,
            claim_count_column=proposal.claim_count_column,
            claim_amount_column=proposal.claim_amount_column,
            # The source summary is already in hand. Recomputing it cost **four seconds**
            # on a 10 000-level column — a `one_way` at that width spends its time in
            # per-level scipy interval quantiles, and doing it twice was most of the
            # proposal's wall-clock (NFR-MODEL-3).
            source=source,
            # Which theory ran, so the evidence can carry FR-MODEL-80's variance
            # components. `grouping_evidence` re-derives them from the same `source` rows
            # `_credibility_weighted` shrank on, so the recorded `k` is the one that
            # produced the mapping rather than a second estimate of it.
            credibility_model=(
                proposal.credibility_model
                if proposal.method is GroupingMethod.CREDIBILITY_WEIGHTED
                else None
            ),
        ),
    )


def _method_params(proposal: GroupingProposal) -> dict[str, object]:
    """What the grouping records about how it was derived (`grouping.schema.json`).

    The credibility settings go **in** `method_params` rather than beside them, which is
    where the contract has carried `credibility_model` since Phase 0. `credibility_pk` and
    the count it implies are written together, so the two cannot drift apart.

    The **effective** settings, not only the ones the caller named: a `tree` grouping that
    records neither `random_state` nor `min_samples_leaf` cannot be reproduced from its own
    artifact, and reproducing a stored artifact is the point of storing how it was made.
    """
    params: dict[str, object] = dict(proposal.method_params)
    if proposal.method is GroupingMethod.TREE:
        params.setdefault("min_samples_leaf", 1)
        params.setdefault("random_state", 0)
    if proposal.method is GroupingMethod.CREDIBILITY_WEIGHTED:
        params["credibility_model"] = proposal.credibility_model.value
        # The `(p, k)` pair and the count it implies belong to **limited fluctuation** and
        # to nothing else. Bühlmann-Straub derives no full-credibility standard, so writing
        # `(0.90, 0.05)` — the proposal's defaults, which it never reads — onto a
        # `buhlmann_straub` artifact would record a standard that did not run, which is the
        # failure FR-MODEL-80 exists to prevent. Its variance components go in the evidence.
        if proposal.credibility_model is CredibilityModel.LIMITED_FLUCTUATION:
            params["credibility_pk"] = {
                "p": proposal.credibility_p,
                "k": proposal.credibility_k,
            }
            params.setdefault(
                "credibility_standard_claims",
                round(_full_credibility_claims(proposal.credibility_p, proposal.credibility_k)),
            )
    return params


def _target_name(index: int) -> str:
    return f"G{index + 1}"


def _largest_cluster(clusters: list[list[OneWayRow]]) -> int:
    """The cluster holding the most exposure — where an unseen level is least wrong.

    Not the smallest, and not the first: an unknown vehicle group priced on a thin cell
    inherits that cell's standard error, and priced on the first cluster inherits whatever
    the sort order happened to be.
    """
    return max(
        range(len(clusters)),
        key=lambda i: sum(float(row.exposure_years) for row in clusters[i]),
    )


def _relativity(row: OneWayRow) -> float | None:
    """A level's observed frequency relative to nothing — the raw rate.

    `None` where the level carries no exposure, because a rate with a zero denominator is
    not a small number, it is an absent one.
    """
    exposure = float(row.exposure_years)
    return row.claim_count / exposure if exposure > 0 else None


def _credibility_weighted(
    source: tuple[OneWayRow, ...], proposal: GroupingProposal
) -> list[list[OneWayRow]]:
    """Merge Levels whose credibility-adjusted rates are within a tolerance (FR-MODEL-14).

    Each level's observed **frequency** — claim count per exposure year, `_relativity` — is
    shrunk toward the portfolio frequency, and the levels are then swept in shrunk-rate
    order and merged while the adjusted rates stay within `merge_tolerance_relativity` of
    the group's running anchor.

    Shrinkage before merging is the whole point: without it, a level with three claims has a
    rate estimated to ±60 % and is merged — or not — on noise.

    Which `Z` does the shrinking is FR-MODEL-80's recorded choice, and the two theories
    differ **only** there (OQ-MODEL-5, decided 2026-08-15):

    * `limited_fluctuation` (the default, and what a UK GI reviewer expects to see) —
      `Z = sqrt(min(n / n_full, 1))` on the level's **claim count**, against a
      full-credibility standard derived from `(p, k)`.
    * `buhlmann_straub` — `Z = m / (m + k)` on the level's **exposure**, with
      `k = EVPV / VHM` estimated across the levels by `_buhlmann_straub_components`.

    They disagree hardest exactly where the choice matters. A level with 200 claims out of
    1 082 gets `Z ≈ 0.43` from limited fluctuation whatever the rest of the book looks like;
    Bühlmann-Straub gives it `Z` near 1 when the levels are genuinely far apart and `Z` near
    0 when they are not, because `k` is estimated from this book rather than from a table.
    """
    tolerance = float(proposal.method_params.get("merge_tolerance_relativity", 0.05))
    buhlmann_straub = proposal.credibility_model is CredibilityModel.BUHLMANN_STRAUB
    components = (
        _buhlmann_straub_components(source, column=proposal.column) if buhlmann_straub else None
    )

    if components is None:
        full = float(
            proposal.method_params.get(
                "credibility_standard_claims",
                _full_credibility_claims(proposal.credibility_p, proposal.credibility_k),
            )
        )
        total_exposure = sum(float(row.exposure_years) for row in source)
        total_claims = sum(row.claim_count for row in source)
        complement = total_claims / total_exposure if total_exposure > 0 else 0.0
        credibility = [
            math.sqrt(min(row.claim_count / full, 1.0)) if full > 0 else 1.0 for row in source
        ]
    else:
        # `evpv` **is** the collective frequency: `s² = E[sigma²(Theta)] = E[lambda(Theta)]
        # = mu` under the Poisson process variance, so the single estimate plays both roles
        # and the complement of credibility cannot drift from the component recorded beside
        # it. The portfolio ratio would differ here whenever a zero-exposure level carries a
        # claim, and a reviewer re-deriving `Z` from the evidence could then not reproduce
        # the shrunk rate — which is the one thing the components are stored for.
        complement = components["evpv"]
        credibility = [
            float(row.exposure_years) / (float(row.exposure_years) + components["k"])
            for row in source
        ]

    adjusted: list[tuple[float, OneWayRow]] = []
    for weight, row in zip(credibility, source, strict=True):
        observed = _relativity(row)
        rate = (
            weight * observed + (1 - weight) * complement
            if observed is not None
            else complement
        )
        adjusted.append((rate, row))
    adjusted.sort(key=lambda pair: pair[0])

    clusters: list[list[OneWayRow]] = []
    current: list[OneWayRow] = []
    anchor = 0.0
    for rate, row in adjusted:
        if current and (anchor <= 0 or abs(rate - anchor) / anchor > tolerance):
            clusters.append(current)
            current = []
        if not current:
            anchor = rate
        current.append(row)
    if current:
        clusters.append(current)
    return clusters


def _hierarchical(
    source: tuple[OneWayRow, ...], proposal: GroupingProposal
) -> list[list[OneWayRow]]:
    """Ward clustering on the observed rate, exposure-weighted (FR-MODEL-14).

    The weighting is what makes it actuarial rather than merely geometric: a level holding
    0.1 % of the exposure should not pull a cluster boundary as hard as one holding 20 %.
    It is applied by repeating each level's rate in proportion to its exposure share, which
    is the standard trick for a clusterer with no sample-weight parameter.

    Levels are ordered by rate and cut into contiguous groups, so the result reads as an
    ordered banding of a categorical — which is what a rate table can actually carry.
    """
    from scipy.cluster.hierarchy import fcluster, linkage

    rated = [(r, row) for row in source if (r := _relativity(row)) is not None]
    if not rated:
        raise GroupingError(
            "GROUPING_NOT_EXHAUSTIVE",
            f"no level of {proposal.column!r} carries exposure, so there are no rates to "
            "cluster on.",
        )
    rated.sort(key=lambda pair: pair[0])
    zero_exposure = [row for row in source if _relativity(row) is None]

    target = min(proposal.n_groups, len(rated))
    if target <= 1:
        clusters = [[row for _, row in rated]]
    else:
        total = sum(float(row.exposure_years) for _, row in rated) or 1.0
        weights = np.asarray(
            [max(1, round(100 * float(row.exposure_years) / total)) for _, row in rated],
            dtype=np.int64,
        )
        observations = np.repeat(
            np.asarray([rate for rate, _ in rated], dtype=np.float64), weights
        ).reshape(-1, 1)
        owner = np.repeat(np.arange(len(rated)), weights)
        assignment = fcluster(linkage(observations, method="ward"), t=target, criterion="maxclust")

        # One label per *level*, by majority of its repeated observations — a level whose
        # copies straddle a boundary belongs to whichever side holds most of its exposure.
        buckets: dict[int, list[int]] = {}
        for index in range(len(rated)):
            labels = assignment[owner == index]
            buckets.setdefault(int(np.bincount(labels).argmax()), []).append(index)
        clusters = [
            [rated[i][1] for i in sorted(members)]
            for _, members in sorted(
                buckets.items(), key=lambda item: min(rated[i][0] for i in item[1])
            )
        ]

    if zero_exposure:
        # A level nobody was exposed to has no rate to cluster on. It joins the largest
        # cluster rather than forming one of its own, which would be a target level with no
        # data behind it — FR-MODEL-11's objection, in the grouping direction.
        clusters[_largest_cluster(clusters)].extend(zero_exposure)
    return clusters


def _tree(
    source: tuple[OneWayRow, ...], proposal: GroupingProposal
) -> list[list[OneWayRow]]:
    """Merge Levels by a depth-limited regression tree on the observed rate (FR-MODEL-85).

    Each Level is one observation, target-encoded by its own rate, weighted by its
    exposure; the tree's leaves become the target Levels. On a single sorted feature the
    leaves are contiguous rate intervals, so — as with `hierarchical_clustering` — the
    result reads as an ordered banding of a categorical, which is what a rate table can
    carry.

    It is a genuinely different method from Ward linkage rather than a second spelling of
    it: the tree partitions greedily to minimise weighted squared error under a leaf-count
    budget, where Ward merges agglomeratively. On the same column they routinely disagree,
    which is why FR-MODEL-14 names both and why substituting one for the other was refused.
    """
    from sklearn.tree import DecisionTreeRegressor

    rated = [(r, row) for row in source if (r := _relativity(row)) is not None]
    if not rated:
        raise GroupingError(
            "GROUPING_NOT_EXHAUSTIVE",
            f"no level of {proposal.column!r} carries exposure, so there are no rates to "
            "fit a tree on.",
        )
    rated.sort(key=lambda pair: pair[0])
    zero_exposure = [row for row in source if _relativity(row) is None]

    target = min(proposal.n_groups, len(rated))
    if target <= 1:
        clusters = [[row for _, row in rated]]
    else:
        rates = np.asarray([rate for rate, _ in rated], dtype=np.float64).reshape(-1, 1)
        weights = np.asarray(
            [float(row.exposure_years) for _, row in rated], dtype=np.float64
        )
        tree = DecisionTreeRegressor(
            max_leaf_nodes=target,
            min_samples_leaf=int(proposal.method_params.get("min_samples_leaf", 1)),
            random_state=int(proposal.method_params.get("random_state", 0)),
        )
        tree.fit(rates, rates.ravel(), sample_weight=weights)

        buckets: dict[int, list[int]] = {}
        for index, leaf in enumerate(tree.apply(rates)):
            buckets.setdefault(int(leaf), []).append(index)
        clusters = [
            [rated[i][1] for i in sorted(members)]
            for _, members in sorted(
                buckets.items(), key=lambda item: min(rated[i][0] for i in item[1])
            )
        ]

    if zero_exposure:
        # Same rule as `_hierarchical`: a level nobody was exposed to has no rate to split
        # on, and a target level with no data behind it is FR-MODEL-11's objection.
        clusters[_largest_cluster(clusters)].extend(zero_exposure)
    return clusters


def apply_grouping(series: pl.Series, grouping: Grouping) -> pl.Series:
    """Map a column's Levels onto their target Levels (FR-MODEL-13).

    Unseen levels follow the declared behaviour, and `error` names them — the behaviour is
    mandatory precisely so that the silent case does not exist.
    """
    text = series.cast(pl.String)
    if text.null_count():
        raise FactorResolutionError(
            f"grouping {grouping.slug!r} met {text.null_count()} null value(s) in "
            f"{grouping.column!r}. `02` §4.3 gives a Grouping no null level — a missing "
            "vehicle group is not a group, and mapping it to one would price it as though "
            "it were known."
        )
    unseen = sorted(
        {
            value
            for value in text.unique().to_list()
            if value is not None and value not in grouping.mapping
        }
    )
    if unseen:
        if grouping.unseen_level_behaviour is UnseenLevelBehaviour.ERROR:
            raise FactorResolutionError(
                f"grouping {grouping.slug!r} met level(s) {unseen[:10]} in "
                f"{grouping.column!r} that it does not map, and its unseen-level behaviour "
                "is `error` (FR-MODEL-13). Re-derive the grouping on this version, or "
                "declare where an unknown level should go."
            )
        fallback = (
            grouping.default_target_level
            if grouping.unseen_level_behaviour is UnseenLevelBehaviour.MAP_TO_DEFAULT
            else grouping.target_levels[0]
        )
    else:
        fallback = None

    mapped = text.replace_strict(
        grouping.mapping, default=fallback, return_dtype=pl.String
    )
    return mapped.rename(series.name)


def grouping_evidence(
    frame: pl.DataFrame,
    mapping: dict[str, str],
    *,
    column: str,
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
    source: tuple[OneWayRow, ...] | None = None,
    credibility_model: CredibilityModel | None = None,
) -> GroupingEvidence:
    """What the merge cost, in deviance and degrees of freedom (FR-MODEL-15).

    Poisson deviance of the observed claim counts against the fitted cell means, before
    (one mean per source level) and after (one per target level). The difference is a
    likelihood-ratio statistic on the degrees of freedom the merge saved, so the p-value
    answers the actuary's real question: *could* these levels be the same?

    `source` lets a caller that already has the source-level summary hand it over rather
    than pay for it twice; the level *count* and — under `buhlmann_straub` — the source
    rates are read from it.

    `credibility_model` names which theory a `credibility_weighted` grouping applied, and is
    the only way this function can know: it receives a mapping, not a `Grouping`. Under
    `buhlmann_straub` the evidence gains `credibility_components` — EVPV, VHM and `k`,
    **re-derived here from the same source rows the merge shrank on**, so a reviewer can
    recompute every `Z = m / (m + k)` rather than take it (FR-MODEL-80). It stays `None`
    under `limited_fluctuation`, which estimates no variance components, and `None` for a
    grouping that used no credibility model at all.
    """
    grouped = frame.with_columns(
        pl.col(column).cast(pl.String).replace_strict(mapping, default=None).alias("_group")
    )
    before = (
        one_way(
            frame,
            column=column,
            exposure_column=exposure_column,
            claim_count_column=claim_count_column,
            claim_amount_column=claim_amount_column,
        )
        if source is None
        else OneWaySummary(column=column, rows=source)
    )
    after = one_way(
        grouped,
        column="_group",
        exposure_column=exposure_column,
        claim_count_column=claim_count_column,
        claim_amount_column=claim_amount_column,
    )

    deviance_before = _poisson_deviance(
        grouped, level_column=column, exposure_column=exposure_column,
        claim_count_column=claim_count_column,
    )
    deviance_after = _poisson_deviance(
        grouped, level_column="_group", exposure_column=exposure_column,
        claim_count_column=claim_count_column,
    )
    df_saved = max(len(before.rows) - len(after.rows), 0)
    statistic = (
        deviance_after - deviance_before
        if deviance_before is not None and deviance_after is not None
        else None
    )
    p_value = (
        float(stats.chi2.sf(statistic, df_saved))
        if statistic is not None and statistic >= 0 and df_saved > 0
        else None
    )
    components = (
        _buhlmann_straub_components(tuple(before.rows), column=column)
        if credibility_model is CredibilityModel.BUHLMANN_STRAUB
        else None
    )
    return GroupingEvidence(
        source_level_count=len(before.rows),
        target_level_count=len(after.rows),
        deviance_before=deviance_before,
        deviance_after=deviance_after,
        df_saved=df_saved,
        chi2_p_value=p_value,
        credibility_components=components,
        source_level_stats=tuple(before.rows),
        target_level_stats=tuple(after.rows),
    )


def _poisson_deviance(
    frame: pl.DataFrame,
    *,
    level_column: str,
    exposure_column: str,
    claim_count_column: str,
) -> float | None:
    """`2 Σ [y·log(y/mu) - (y - mu)]` over **rows**, with `mu` the level rate times exposure.

    Row-level rather than cell-level, so `deviance_before` and `deviance_after` are the two
    numbers `02` §4.3's example carries — deviances of two fitted models against the same
    saturated model — and their difference is the likelihood-ratio statistic. Comparing
    them at cell grain would give the same *difference* and two numbers a reader could not
    reconcile with any model output.

    `None` when the version carries no exposure or no claim count: a deviance without a
    response is not a small number, it is an absent one.
    """
    if exposure_column not in frame.columns or claim_count_column not in frame.columns:
        return None

    rates = (
        frame.group_by(level_column)
        .agg(
            pl.col(exposure_column).cast(pl.Float64).sum().alias("_e"),
            pl.col(claim_count_column).cast(pl.Float64).sum().alias("_y"),
        )
        .with_columns(
            _rate=pl.when(pl.col("_e") > 0).then(pl.col("_y") / pl.col("_e")).otherwise(0.0)
        )
        .select(level_column, "_rate")
    )
    joined = frame.join(rates, on=level_column, how="left")
    y = joined[claim_count_column].cast(pl.Float64).to_numpy()
    mu = (
        joined["_rate"].cast(pl.Float64).to_numpy()
        * joined[exposure_column].cast(pl.Float64).to_numpy()
    )

    usable = np.isfinite(y) & np.isfinite(mu) & (mu > 0)
    if not usable.any():
        return None
    y, mu = y[usable], mu[usable]
    term = -(y - mu)
    positive = y > 0
    term[positive] += y[positive] * np.log(y[positive] / mu[positive])
    return float(2.0 * term.sum())
