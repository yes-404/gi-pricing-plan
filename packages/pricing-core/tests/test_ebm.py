"""The EBM arm of the fit (`02` §5.2). What is proven here is the fit: tables exported
verbatim, the round-trip identity, constraints, weights, seed. The platform seam is
`backend/tests/test_ebm_model_jobs.py`."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4

import numpy as np
import polars as pl
import pytest
from interpret.glassbox import ExplainableBoostingRegressor

from model_schema import (
    Banding,
    BandingMethod,
    EbmCategoricalBins,
    EbmFeatureBins,
    EbmFitResult,
    EbmNumericBins,
    EbmSpec,
    Factor,
    FactorType,
    SplitRef,
    WeightSpec,
)
from pricing_core.modelling.ebm import EbmFitError, fit_ebm
from pricing_core.modelling.factors import resolve_factors
from pricing_core.modelling.predict import PredictionError, predict_ebm


def _book(n: int = 2000, seed: int = 20260821) -> pl.DataFrame:
    """A synthetic motor book: numeric `speed`, categorical `area` (A/B/C), banded `age`.

    `claim_count` depends on all three so every term has signal; `n_claims` is a
    deliberately skewed column the weights test perturbs with (5 % of rows carry 20x the
    weight of the rest).
    """
    rng = np.random.default_rng(seed)
    speed = rng.uniform(0.0, 120.0, n)
    area = rng.choice(["A", "B", "C"], size=n)
    age = rng.uniform(17.0, 90.0, n)
    eta = (
        -1.0
        + 0.012 * speed
        + np.where(area == "A", 0.0, np.where(area == "B", 0.4, 0.8))
        + 0.02 * (age - 40.0)
    )
    return pl.DataFrame(
        {
            "speed": speed,
            "area": area,
            "age": age,
            "exposure_years": rng.uniform(0.5, 1.0, n),
            "claim_count": rng.poisson(np.exp(eta)).astype(float),
            "n_claims": np.where(rng.uniform(0.0, 1.0, n) < 0.05, 10.0, 0.5),
        }
    )


AGE_BANDING = Banding(
    id=uuid4(), slug="age-band", dataset_id=uuid4(), version=1,
    column="age", method=BandingMethod.MANUAL,
    boundaries=(16.0, 25.0, 35.0, 50.0, 90.0),
    labels=("16-24", "25-34", "35-49", "50-89"),
)
BANDINGS = {AGE_BANDING.id: AGE_BANDING}


def _factor(slug: str, column: str, **over: object) -> Factor:
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": uuid4(), "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    fields.update(over)
    return Factor(**fields)  # type: ignore[arg-type]


FACTORS = [
    _factor("speed", "speed"),
    _factor("area", "area"),
    _factor("age_band", "age", type=FactorType.BANDING, banding_id=AGE_BANDING.id),
]


def _spec(**over: object) -> EbmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "split_ref": SplitRef(split_artifact_id=uuid4()),
        "response_column": "claim_count",
        "objective": "rmse",
        "factors": tuple(f.id for f in FACTORS),
    }
    base.update(over)
    return EbmSpec(**base)  # type: ignore[arg-type]


def _design(
    frame: pl.DataFrame, factors: Sequence[Factor]
) -> tuple[np.ndarray, list[str | tuple[str, ...]]]:
    """The feature matrix and `feature_types` — the same construction `fit_ebm` makes.

    The tests rebuild the estimator's inputs this way so `predict` can stand as the
    reference the exported tables are measured against. The mapping mirrors `fit_ebm`'s
    dated note of 2026-08-21: 0.7.8 knows `"nominal"` and ordered levels lists, not
    `"categorical"`.
    """
    matrix = resolve_factors(frame, factors, bandings=BANDINGS)
    columns: list[np.ndarray] = []
    feature_types: list[str | tuple[str, ...]] = []
    for factor in factors:
        column = matrix.terms[factor.slug]
        if column in matrix.categorical:
            columns.append(matrix.frame[column].cast(pl.String).to_numpy())
            if factor.type is FactorType.BANDING:
                feature_types.append(BANDINGS[factor.banding_id].levels)
            else:
                feature_types.append("nominal")
        else:
            columns.append(matrix.frame[column].cast(pl.Float64).to_numpy())
            feature_types.append("continuous")
    return np.column_stack(columns), feature_types


def _estimator(
    spec: EbmSpec, feature_types: list[str | tuple[str, ...]]
) -> ExplainableBoostingRegressor:
    """The estimator `fit_ebm` would build for `spec`, mirroring its construction."""
    return ExplainableBoostingRegressor(
        interactions=spec.interactions,
        max_bins=spec.max_bins,
        max_rounds=spec.max_rounds,
        # The full positional list, exactly as the fit builds it — 0.7.8 consumes
        # `monotone_constraints` by position, and a constrained spec's list is built
        # by `fit_ebm` from the same slug map this mirror leaves all-zero.
        monotone_constraints=[0] * len(feature_types),
        random_state=spec.seed,
        feature_types=feature_types,
    )


def _slots(
    fit: EbmFitResult, estimator: ExplainableBoostingRegressor, x: np.ndarray
) -> list[np.ndarray]:
    """Each feature's slot per row — the index rule the artifact pins, applied inline.

    Numeric: `np.searchsorted(cuts, v, side="right") + 1` — slot 0 is the unused base,
    the populated bins are `1..c+1`, and the trailing missing-value slot is never
    reached without a NaN. Categorical: the estimator's own 1-based level dict, with the
    artifact's `levels` asserted to be that dict's keys written through verbatim so the
    two agree by construction.
    """
    slots: list[np.ndarray] = []
    for index, bins in enumerate(fit.bins):
        values = x[:, index]
        if isinstance(bins, EbmNumericBins):
            slots.append(
                np.searchsorted(np.asarray(bins.cuts), values, side="right") + 1
            )
        else:
            level_dict = estimator.bins_[index][0]
            # Iterating the dict yields its keys in order (SIM118).
            assert tuple(str(k) for k in level_dict) == bins.levels, (
                "the artifact's levels must be the fitted dict's keys in order"
            )
            slots.append(np.asarray([level_dict[v] for v in values]))
    return slots


def _rebuilt(fit: EbmFitResult, slots: list[np.ndarray]) -> np.ndarray:
    """`intercept + Σ(term scores at each row's bins)`, inline from the exported tables."""
    rebuilt = np.full(slots[0].shape, fit.intercept)
    for term in fit.terms:
        if len(term.term_features) == 2:
            first, second = term.term_features
            rebuilt = rebuilt + np.asarray(term.scores)[slots[first], slots[second]]
        else:
            (feature,) = term.term_features
            rebuilt = rebuilt + np.asarray(term.scores)[slots[feature]]
    return rebuilt


# --------------------------------------------------------------------------------------
# FR-140 — the fit and the verbatim tables
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-140")
def test_fit_returns_the_expected_tables() -> None:
    data = _book()
    result = fit_ebm(data, _spec(), FACTORS, bandings=BANDINGS)

    assert result.feature_order == ("speed", "area", "age_band")
    assert len(result.terms) == 3  # one univariate term per factor
    assert all(len(term.term_features) == 1 for term in result.terms)
    by_feature = {term.term_features[0]: term for term in result.terms}

    speed_bins = result.bins[0]
    assert isinstance(speed_bins, EbmNumericBins)
    assert len(by_feature[0].scores) == len(speed_bins.cuts) + 3
    assert by_feature[0].bin_weights[0] == 0.0

    area_bins = result.bins[1]
    assert isinstance(area_bins, EbmCategoricalBins)
    assert len(by_feature[1].scores) == len(area_bins.levels) + 2
    assert by_feature[1].bin_weights[0] == 0.0

    age_bins = result.bins[2]
    assert isinstance(age_bins, EbmCategoricalBins)
    assert len(by_feature[2].scores) == len(age_bins.levels) + 2

    assert np.isfinite(result.intercept)
    assert result.best_iteration >= 0
    assert result.library_versions["interpret"] == "0.7.8"
    assert result.rows == data.height


@pytest.mark.req("FR-140")
@pytest.mark.req("NFR-535")
def test_the_exported_tables_reproduce_interpret_predict() -> None:
    """The round trip: the artifact alone must rescore a frame `interpret` can score.

    This is where the spike's index rule and slot layout are enforced against 0.7.8 —
    if the cuts/scores relationship is off by one it fails HERE, before any backend
    code exists, and the fix is a dated one-liner in the export, never a weakened
    tolerance. The sweep covers below-first-cut, mid-range and above-last-cut values so
    the rule has to agree with the library at both edges.
    """
    data = _book()
    spec = _spec()
    fit = fit_ebm(data, spec, FACTORS, bandings=BANDINGS)

    x, feature_types = _design(data, FACTORS)
    estimator = _estimator(spec, feature_types)
    estimator.fit(x, data["claim_count"].cast(pl.Float64).to_numpy())

    sweep = pl.DataFrame(
        {
            "speed": [-20.0, 1.0, 30.0, 80.0, 150.0],
            "area": ["A", "B", "C", "A", "B"],
            "age": [20.0, 30.0, 40.0, 60.0, 70.0],
        }
    )
    x_sweep, _ = _design(sweep, FACTORS)

    rebuilt = _rebuilt(fit, _slots(fit, estimator, x_sweep))
    assert np.allclose(rebuilt, estimator.predict(x_sweep), atol=1e-9)


@pytest.mark.req("FR-140")
def test_an_interaction_fit_exports_a_rectangular_grid() -> None:
    data = _book()
    pair = FACTORS[:2]  # speed x area: exactly one pair
    spec = _spec(factors=tuple(f.id for f in pair), interactions=1)
    fit = fit_ebm(data, spec, pair, bandings=BANDINGS)

    grid_terms = [term for term in fit.terms if len(term.term_features) == 2]
    assert len(grid_terms) == 1
    grid = grid_terms[0]
    first, second = grid.term_features

    def slots_of(bins: EbmFeatureBins) -> int:
        return (
            len(bins.cuts) + 3
            if isinstance(bins, EbmNumericBins)
            else len(bins.levels) + 2
        )

    assert len(grid.scores) == slots_of(fit.bins[first])
    assert all(len(row) == slots_of(fit.bins[second]) for row in grid.scores)

    x, feature_types = _design(data, pair)
    estimator = _estimator(spec, feature_types)
    estimator.fit(x, data["claim_count"].cast(pl.Float64).to_numpy())

    sweep = pl.DataFrame(
        {"speed": [0.0, 60.0, 120.0], "area": ["A", "C", "B"]}
    )
    x_sweep, _ = _design(sweep, pair)
    rebuilt = _rebuilt(fit, _slots(fit, estimator, x_sweep))
    assert np.allclose(rebuilt, estimator.predict(x_sweep), atol=1e-9)


# --------------------------------------------------------------------------------------
# FR-140 — `predict_ebm`, scoring from the exported tables
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-140")
def test_scoring_matches_interpret_on_a_held_out_frame() -> None:
    """`predict_ebm` agrees with the fitted estimator on a frame the fit never saw.

    `interactions=1` on purpose: the pair term is scored through the 2-D lookup
    `scores[slots[a], slots[b]]`, and this is the test that measures it against
    `interpret` — an unexercised branch of the scorer is a silently wrong grid.

    The same `atol=1e-9` as the Task 6 round trip: the scorer re-runs the same
    arithmetic the estimator ran — lookups into the exported tables — so the tolerance
    is a reproduction tolerance, not a model tolerance.
    """
    data = _book()
    spec = _spec(interactions=1)
    fit = fit_ebm(data, spec, FACTORS, bandings=BANDINGS)

    x, feature_types = _design(data, FACTORS)
    estimator = _estimator(spec, feature_types)
    estimator.fit(x, data["claim_count"].cast(pl.Float64).to_numpy())

    held_out = _book(seed=7)
    mu = predict_ebm(fit, held_out, FACTORS, bandings=BANDINGS)
    x_held, _ = _design(held_out, FACTORS)
    assert np.allclose(mu, estimator.predict(x_held), atol=1e-9)


@pytest.mark.req("FR-131")
def test_an_unseen_level_is_refused_by_name() -> None:
    """A level the fit never saw has no slot — inventing one would score it as
    whichever level shares the number (the `gbm._encode` rule, FR-131)."""
    fit = fit_ebm(_book(), _spec(), FACTORS, bandings=BANDINGS)
    frame = pl.DataFrame({"speed": [30.0], "area": ["Q"], "age": [40.0]})

    with pytest.raises(PredictionError) as error:
        predict_ebm(fit, frame, FACTORS, bandings=BANDINGS)
    assert error.value.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert "area" in str(error.value)


@pytest.mark.req("FR-140")
def test_a_scored_term_resolves_from_the_artifact_alone() -> None:
    """The artifact's `feature_order` and `bins` are the only ground truth.

    Fresh `Factor` identities and a fresh frame: the fit-time `factors` and `data` are
    dropped, and only the slugs have to match — scoring a model needs the model, and
    the model is the tables.
    """
    data = _book()
    spec = _spec()
    fit = fit_ebm(data, spec, FACTORS, bandings=BANDINGS)

    x, feature_types = _design(data, FACTORS)
    estimator = _estimator(spec, feature_types)
    estimator.fit(x, data["claim_count"].cast(pl.Float64).to_numpy())

    fresh = [
        _factor("speed", "speed"),
        _factor("area", "area"),
        _factor("age_band", "age", type=FactorType.BANDING, banding_id=AGE_BANDING.id),
    ]
    frame = _book(seed=11)
    mu = predict_ebm(fit, frame, fresh, bandings=BANDINGS)
    x_fresh, _ = _design(frame, fresh)
    assert np.allclose(mu, estimator.predict(x_fresh), atol=1e-9)


# --------------------------------------------------------------------------------------
# FR-122 — monotone constraints, by name and by the feature that got them
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-122")
def test_a_monotone_constraint_lands_on_the_right_feature() -> None:
    data = _book()
    plain = fit_ebm(data, _spec(), FACTORS, bandings=BANDINGS)
    constrained = fit_ebm(
        data, _spec(monotone_constraints={"speed": 1}), FACTORS, bandings=BANDINGS
    )

    speed_term = next(t for t in constrained.terms if t.term_features == (0,))
    # The real bins only: slot 0 is the unused base and the trailing slot is
    # missing-value, so `scores[1:-1]` is exactly the populated lookup.
    #
    # Dated note 2026-08-21: the brief's `np.diff(...) <= 1e-9` asserted the wrong
    # direction — it requires the term to be non-**increasing**, contradicting +1's
    # documented meaning ("the partial response ... should be monotonically
    # increasing") and failing on 0.7.8's own constrained fit, whose speed term is
    # non-decreasing (verified against the pinned library). The tolerance is
    # untouched; the direction is what the library's docstring defines.
    assert np.all(np.diff(speed_term.scores[1:-1]) >= -1e-9)

    # The other terms are unchanged in shape.
    plain_by_feature = {term.term_features[0]: term for term in plain.terms}
    for term in constrained.terms:
        assert len(term.scores) == len(plain_by_feature[term.term_features[0]].scores)


@pytest.mark.req("FR-140")
def test_a_monotone_constraint_on_a_categorical_feature_is_refused_by_name() -> None:
    with pytest.raises(EbmFitError) as error:
        fit_ebm(_book(), _spec(monotone_constraints={"area": 1}), FACTORS, bandings=BANDINGS)
    assert error.value.code == "EBM_MONOTONE_CONSTRAINT_INCOMPLETE"


@pytest.mark.req("FR-140")
def test_a_monotone_constraint_naming_an_unknown_slug_is_refused_by_name() -> None:
    with pytest.raises(EbmFitError) as error:
        fit_ebm(
            _book(),
            _spec(monotone_constraints={"no_such_factor": 1}),
            FACTORS,
            bandings=BANDINGS,
        )
    assert error.value.code == "EBM_MONOTONE_CONSTRAINT_INCOMPLETE"


# --------------------------------------------------------------------------------------
# FR-184 / FR-140 — weights and the spec seed
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-184")
def test_weights_reach_the_estimator() -> None:
    data = _book()
    plain = fit_ebm(data, _spec(), FACTORS, bandings=BANDINGS)
    weighted = fit_ebm(
        data,
        _spec(weight=WeightSpec(kind="column", column="n_claims")),
        FACTORS,
        bandings=BANDINGS,
    )

    plain_speed = next(t for t in plain.terms if t.term_features == (0,))
    weighted_speed = next(t for t in weighted.terms if t.term_features == (0,))
    assert not np.array_equal(plain_speed.scores, weighted_speed.scores)


@pytest.mark.req("FR-140")
def test_the_fit_is_reproducible_under_the_spec_seed() -> None:
    data = _book()
    first = fit_ebm(data, _spec(), FACTORS, bandings=BANDINGS)
    second = fit_ebm(data, _spec(), FACTORS, bandings=BANDINGS)
    assert first.terms == second.terms
    assert first.intercept == second.intercept

    # Different seeds must change the term scores — the spike found `intercept_` is
    # data-determined and equal across seeds, so the intercept is not the discriminator.
    other = fit_ebm(data, _spec(seed=1), FACTORS, bandings=BANDINGS)
    different = fit_ebm(data, _spec(seed=2), FACTORS, bandings=BANDINGS)
    other_speed = next(t for t in other.terms if t.term_features == (0,))
    different_speed = next(t for t in different.terms if t.term_features == (0,))
    assert not np.array_equal(other_speed.scores, different_speed.scores)


@pytest.mark.req("FR-140")
def test_fit_seconds_and_library_versions_are_recorded() -> None:
    result = fit_ebm(_book(), _spec(), FACTORS, bandings=BANDINGS)
    assert result.fit_seconds >= 0.0
    assert result.library_versions


@pytest.mark.req("FR-179")
def test_fit_ebm_refuses_a_seed_argument() -> None:
    """FR-179: `fit_ebm` carried the same dead kwarg as `fit_glm`, and it is gone too.

    Its docstring said outright that the parameter mirrored `fit_glm`'s "vestigial kwarg for
    call-site symmetry" and was "deliberately **not** the reproducibility source" — the fact
    was documented in the one file where nobody reading `fit_glm` would find it. The seed
    that works is `spec.seed`, which reaches `random_state`, and the test above already
    proves two spec seeds give different term scores.
    """
    with pytest.raises(TypeError, match="seed"):
        fit_ebm(pl.DataFrame(), _spec(), [], seed=0)  # type: ignore[call-arg]
