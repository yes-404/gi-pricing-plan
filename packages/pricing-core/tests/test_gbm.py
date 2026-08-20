"""GBM fitting and scoring, on both backends (`02` FR-MODEL-25..32, 71..73, §5.2).

**Every test that can run on both backends does.** That is not thoroughness for its own
sake: FR-MODEL-72 exists because the two libraries agree at fit time and disagree at
prediction time, and a suite that exercised only the primary backend would have reported
the secondary one working while it under-predicted by exactly the offset. `parametrize`
over `BACKENDS` is the mechanism, and a test that names one backend explicitly should say
why.

The offset asymmetry was re-verified in this environment before any of this was written
(xgboost 3.4.1, lightgbm 4.7.0): XGBoost's `predict` applies `base_margin` when the
prediction matrix carries one and substitutes `base_score` when it does not, while
LightGBM's `Booster.predict` has no offset parameter at all — the signature is
`(data, start_iteration, num_iteration, raw_score, pred_leaf, pred_contrib, …)`.
"""

from __future__ import annotations

import hashlib
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    TEMPLATE_APPLICABILITY,
    Applicability,
    Banding,
    BandingMethod,
    CustomMetric,
    CustomObjective,
    EarlyStopping,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    LossTreatment,
    MetricDirection,
    MetricStatus,
    MonotonicDirection,
    ObjectiveBackend,
    ObjectiveStatus,
    ObjectiveTemplate,
    OffsetSpec,
    ResponseKind,
    SplitRef,
    YDomain,
)
from pricing_core.modelling.gbm import GbmFitError, fit_gbm, predict_gbm

BACKENDS = ["xgboost", "lightgbm"]

EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")


def _factor(slug: str, column: str, **over: object) -> Factor:
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": uuid4(), "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    fields.update(over)
    return Factor(**fields)  # type: ignore[arg-type]


FACTORS = [_factor("area", "area"), _factor("driv_age", "driv_age")]


def _frequency_data(n: int = 8_000, seed: int = 20260817) -> pl.DataFrame:
    """A Poisson book with a genuine exposure offset.

    Exposure varies over nearly an order of magnitude on purpose: a model that dropped the
    offset would still look plausible on a book where every row is one policy-year.
    """
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.1, 1.0, n)
    urban = rng.integers(0, 2, n)
    age = rng.integers(18, 80, n)
    eta = np.log(exposure) - 2.0 + 0.5 * urban + 0.03 * (age - 40)
    return pl.DataFrame(
        {
            "exposure_years": exposure,
            "area": ["urban" if u else "rural" for u in urban],
            "driv_age": age.astype(float),
            "claim_count": rng.poisson(np.exp(eta)).astype(float),
        }
    )


def _spec(backend: str, **over: object) -> GbmSpec:
    base: dict[str, object] = {
        "model_type": backend,
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "split_ref": SplitRef(split_artifact_id=uuid4()),
        "response_column": "claim_count",
        "offset": EXPOSURE,
        "objective": GbmFunctionRef(kind="builtin", name="count:poisson"),
        "categorical_handling": "native",
        "hyperparameters": {"max_depth": 3, "eta": 0.1, "num_boost_round": 40},
        "early_stopping": None,
        "factors": tuple(f.id for f in FACTORS),
    }
    base.update(over)
    return GbmSpec(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------------------------------
# FR-MODEL-27 / FR-MODEL-72 — the offset, at fit time and at scoring time
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-72")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_prediction_scales_exactly_with_exposure(backend: str) -> None:
    """The decisive test for FR-MODEL-72, and the reason it is parametrized.

    With `log(exposure)` as the offset, `μ = exposure · exp(f(x))`. Doubling exposure must
    therefore double the prediction *exactly* — it is arithmetic, not a fitted effect.

    A scoring path that forgot the offset returns `exp(f(x))` whatever the exposure, so
    this ratio comes back as 1. That is the LightGBM failure mode the requirement names,
    and it is invisible to every test that only checks predictions look reasonable.
    """
    data = _frequency_data()
    fit = fit_gbm(data, _spec(backend), FACTORS)

    single = predict_gbm(fit.result, fit.booster_bytes, data)
    doubled = predict_gbm(
        fit.result, fit.booster_bytes,
        data.with_columns(pl.col("exposure_years") * 2.0),
    )
    ratio = (doubled / single).to_numpy()
    # `rtol=1e-5` rather than exact: XGBoost returns **float32**, and the worst element
    # here sits 1.03e-6 from two — measured, not guessed, and consistent with a few ulp
    # across two roundings and a division. The tolerance is still four orders of magnitude
    # from the failure this test exists for: a scoring path that dropped the offset returns
    # the same prediction for both frames, and the ratio is 1.
    assert np.allclose(ratio, 2.0, rtol=1e-5), f"{backend}: exposure is not in the score"


@pytest.mark.req("FR-MODEL-27")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_fitted_model_reproduces_the_observed_claim_total(backend: str) -> None:
    """The offset on the *fit* side, in the units an actuary would check first.

    A Poisson fit with a log link and an exposure offset reproduces the observed total on
    the data it was fitted to. Drop the offset at fit time and the total is out by the
    average exposure — here roughly a factor of two, which no tolerance hides.
    """
    data = _frequency_data()
    # Enough rounds to converge the level. Boosting starts from the offset alone — every
    # row's initial prediction is its exposure, a mean of 0.55 against a true 0.15 — so a
    # 40-round fit is still descending toward the right total and would fail this by 35 %.
    # The default elsewhere in this file is deliberately short because those tests are
    # about structure rather than calibration.
    spec = _spec(backend, hyperparameters={"max_depth": 3, "eta": 0.2, "num_boost_round": 300})
    fit = fit_gbm(data, spec, FACTORS)
    predicted = predict_gbm(fit.result, fit.booster_bytes, data).sum()
    observed = float(data["claim_count"].sum())
    assert predicted == pytest.approx(observed, rel=0.05)


@pytest.mark.req("FR-MODEL-71")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_scoring_frame_without_the_offset_column_is_refused(backend: str) -> None:
    """FR-MODEL-71: a booster whose offset cannot be reconstructed is a **hard failure**.

    Never a warning and never a silent fallback to no offset, because that fallback is the
    thing that fails silently: the predictions come back, they are the right shape, and
    every one of them is wrong by a factor of the exposure.
    """
    data = _frequency_data()
    fit = fit_gbm(data, _spec(backend), FACTORS)
    with pytest.raises(GbmFitError, match="exposure_years"):
        predict_gbm(fit.result, fit.booster_bytes, data.drop("exposure_years"))


@pytest.mark.req("FR-MODEL-27")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_counting_objective_refuses_a_book_with_no_exposure(backend: str) -> None:
    """The spec refuses this at the type; this is the fit path refusing the *data*.

    `GbmSpec` cannot be built with a counting objective and no offset, so the reachable
    failure is an offset column of zeros — a row contributing no information whose
    `log(0)` is `-inf`, which trains happily and scores as zero for ever.
    """
    data = _frequency_data().with_columns(
        pl.when(pl.int_range(pl.len()) < 5)
        .then(0.0)
        .otherwise(pl.col("exposure_years"))
        .alias("exposure_years")
    )
    with pytest.raises(GbmFitError, match="non-positive"):
        fit_gbm(data, _spec(backend), FACTORS)


# --------------------------------------------------------------------------------------
# FR-MODEL-31 / NFR-MODEL-6 — what is persisted, and that it reproduces
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-31")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_booster_is_the_backends_own_text_format_and_addresses_itself(
    backend: str,
) -> None:
    """FR-MODEL-31 / ADR-0003: JSON or text, content-addressed, never a pickle.

    The digest is checked against the bytes rather than trusted: a `BlobRef` whose sha256
    does not describe its payload is a reference that will resolve to something else after
    the first collision-free store, and nothing downstream re-checks it.
    """
    fit = fit_gbm(_frequency_data(), _spec(backend), FACTORS)
    blob = fit.result.booster_blob
    assert blob.sha256 == hashlib.sha256(fit.booster_bytes).hexdigest()
    assert blob.bytes_ == len(fit.booster_bytes)
    assert fit.result.booster_format in {"xgboost_json", "lightgbm_text"}
    # The format is readable as itself — a pickle would not survive either of these.
    text = fit.booster_bytes.decode()
    assert text.lstrip().startswith("{" if backend == "xgboost" else "tree")


@pytest.mark.req("NFR-MODEL-6")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_same_spec_and_seed_produce_the_same_booster(backend: str) -> None:
    """NFR-MODEL-6: an identical `spec_hash` and seed reproduce an identical booster hash.

    Stated over the **digest**, not over the predictions: two boosters that predict alike
    on one frame are not the same model, and FR-OVR-8's reproducibility claim is about the
    artifact.
    """
    data = _frequency_data()
    first = fit_gbm(data, _spec(backend, seed=7), FACTORS)
    second = fit_gbm(data, _spec(backend, seed=7), FACTORS)
    assert first.result.booster_blob.sha256 == second.result.booster_blob.sha256


# --------------------------------------------------------------------------------------
# FR-MODEL-28 / FR-MODEL-30 / FR-MODEL-32 — the constraints and the vocabulary
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-28")
@pytest.mark.parametrize("backend", BACKENDS)
def test_monotone_constraints_are_derived_from_the_factors_and_hold(backend: str) -> None:
    """FR-MODEL-28: the direction is declared on the Factor and derived here.

    Checked as *behaviour* as well as as a persisted vector, because a constraint vector
    that reached the backend in the wrong order would still be persisted correctly and
    still be wrong. Sweeping the factor and asserting the predictions never fall is the
    only form of the check that notices.
    """
    data = _frequency_data()
    factors = [
        _factor("area", "area"),
        _factor("driv_age", "driv_age", monotonic_direction=MonotonicDirection.INCREASING,
                monotonic_rationale="claim frequency rises with age in this book"),
    ]
    fit = fit_gbm(data, _spec(backend, factors=tuple(f.id for f in factors)), factors)

    position = fit.result.feature_order.index("driv_age")
    assert fit.result.monotone_constraints[position] == 1

    sweep = pl.DataFrame({
        "exposure_years": np.ones(60),
        "area": ["urban"] * 60,
        "driv_age": np.linspace(18, 80, 60),
    })
    predictions = predict_gbm(fit.result, fit.booster_bytes, sweep).to_numpy()
    assert np.all(np.diff(predictions) >= -1e-12), f"{backend}: the constraint did not hold"


LICENCE_BANDING = Banding(
    id=uuid4(), slug="licence-years", dataset_id=uuid4(), version=1,
    column="licence_years", method=BandingMethod.MANUAL,
    boundaries=(0.0, 2.0, 5.0, 10.0, 50.0),
    labels=("0-1", "2-4", "5-9", "10-49"),
)


def _licence_data(n: int = 8_000, seed: int = 20260817) -> pl.DataFrame:
    """A book whose frequency falls with licence years — the effect the constraint names."""
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.1, 1.0, n)
    years = rng.uniform(0.0, 49.0, n)
    eta = np.log(exposure) - 1.4 - 0.06 * years
    return pl.DataFrame({
        "exposure_years": exposure,
        "licence_years": years,
        "claim_count": rng.poisson(np.exp(eta)).astype(float),
    })


@pytest.mark.req("FR-MODEL-28")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_monotone_direction_holds_on_a_banded_factor(backend: str) -> None:
    """A banding is **ordered**, so FR-MODEL-28 applies to it — `02` §4.4's own example is a
    monotone constraint on `driver_age_banded`, and `wf-01` C7 declares one.

    The order has to come from the Banding artifact. Encoding the levels with a plain
    `sorted()` puts `"10-49"` second, between `"0-1"` and `"2-4"`, so a decreasing
    constraint would hold in the alphabet and mean nothing about licence years — and the
    fit would still succeed, still persist `-1`, and still look right. The labels here are
    chosen so the two orders differ; sweeping the bands in the artifact's order is the only
    check that notices.

    Found by the `wf-01` journey test on 2026-08-17: the guard refused this constraint
    outright, because the encoding it was defending against was the module's own.
    """
    banded = _factor(
        "licence_years_banded", "licence_years", type=FactorType.BANDING,
        banding_id=LICENCE_BANDING.id,
        monotonic_direction=MonotonicDirection.DECREASING,
        monotonic_rationale="claim frequency falls with driving experience",
    )
    bandings = {LICENCE_BANDING.id: LICENCE_BANDING}
    spec = _spec(backend, response_column="claim_count", factors=(banded.id,))
    fit = fit_gbm(_licence_data(), spec, [banded], bandings=bandings)

    assert sorted(LICENCE_BANDING.labels) != list(LICENCE_BANDING.labels), (
        "the labels no longer distinguish artifact order from alphabetical order, so this "
        "test would pass against the bug it exists for"
    )
    codes = fit.result.categorical_maps["licence_years_banded"]
    assert sorted(codes, key=lambda level: codes[level]) == list(LICENCE_BANDING.labels)

    position = fit.result.feature_order.index("licence_years_banded")
    assert fit.result.monotone_constraints[position] == -1

    # One row per band, swept in the artifact's order, at the midpoint of each.
    midpoints = [
        (lower + upper) / 2
        for lower, upper in zip(
            LICENCE_BANDING.boundaries, LICENCE_BANDING.boundaries[1:], strict=False
        )
    ]
    sweep = pl.DataFrame({
        "exposure_years": np.ones(len(midpoints)),
        "licence_years": midpoints,
    })
    predictions = predict_gbm(
        fit.result, fit.booster_bytes, sweep, [banded], bandings=bandings
    ).to_numpy()
    assert np.all(np.diff(predictions) <= 1e-12), f"{backend}: the constraint did not hold"


@pytest.mark.req("FR-MODEL-28")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_monotone_direction_on_an_unordered_categorical_is_refused(backend: str) -> None:
    """"Increasing in `area`" is not a claim that can be true.

    The backends accept the constraint and apply it to whatever integer codes the levels
    happened to receive, so the model becomes monotone in an ordering nobody chose and the
    artifact records a direction that reads as an actuarial judgement.
    """
    factors = [
        _factor("area", "area", monotonic_direction=MonotonicDirection.INCREASING,
                monotonic_rationale="deliberately nonsensical — area is unordered"),
        _factor("driv_age", "driv_age"),
    ]
    with pytest.raises(GbmFitError, match="area"):
        fit_gbm(_frequency_data(), _spec(backend, factors=tuple(f.id for f in factors)), factors)


@pytest.mark.req("FR-MODEL-30")
@pytest.mark.parametrize("backend", BACKENDS)
def test_early_stopping_without_the_holdout_frame_is_refused(backend: str) -> None:
    """FR-MODEL-30: early stopping requires a declared holdout, and a declared holdout is
    not the same as one that arrived.

    `GbmSpec` refuses a stopping rule with no `split_ref`; this refuses a caller that
    declared the split and then passed no rows. Without it the backend falls back to
    evaluating on the training set, which is what the requirement forbids — reached by
    omission rather than by asking for it.
    """
    spec = _spec(backend, early_stopping=EarlyStopping(
        on="holdout", metric="poisson-nloglik", rounds=10))
    with pytest.raises(GbmFitError, match="holdout"):
        fit_gbm(_frequency_data(), spec, FACTORS)


@pytest.mark.req("FR-MODEL-30")
@pytest.mark.parametrize("backend", BACKENDS)
def test_early_stopping_records_the_curve_and_the_iteration_it_chose(backend: str) -> None:
    """FR-MODEL-30: the chosen iteration count, the full curve and the metric are persisted.

    All three, because each answers a different question at review: which model this is,
    whether it had stopped improving, and against what.
    """
    data = _frequency_data()
    spec = _spec(backend, early_stopping=EarlyStopping(
        on="holdout", metric="poisson-nloglik", rounds=10))
    fit = fit_gbm(data, spec, FACTORS, holdout=_frequency_data(n=3_000, seed=99))
    assert fit.eval_curve
    assert fit.result.best_iteration >= 1
    assert {point.metric for point in fit.eval_curve} == {"poisson-nloglik"}
    # FR-MODEL-52 asks for **both** partitions, and FR-MODEL-54 calls one of them alone a
    # defect. A curve on the holdout only cannot show the divergence early stopping exists
    # to catch, which is the whole reason the pair is one row rather than two series.
    assert all(point.holdout is not None for point in fit.eval_curve)
    assert all(point.train is not None for point in fit.eval_curve)


@pytest.mark.req("FR-MODEL-32")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_categorical_encoding_is_persisted_and_reused(backend: str) -> None:
    """FR-MODEL-32: silent label-encoding is refused — so the map is part of the artifact.

    Reused rather than recomputed at scoring time: a map derived from the scoring frame
    would renumber the levels whenever a level was absent from it, and every prediction
    after that would be for a different level.
    """
    data = _frequency_data()
    fit = fit_gbm(data, _spec(backend), FACTORS)
    assert fit.result.categorical_maps["area"] == {"rural": 0, "urban": 1}

    rural_only = data.filter(pl.col("area") == "rural")
    both = predict_gbm(fit.result, fit.booster_bytes, data)
    subset = predict_gbm(fit.result, fit.booster_bytes, rural_only)
    assert np.allclose(subset.to_numpy(), both.filter(data["area"] == "rural").to_numpy())


@pytest.mark.req("FR-MODEL-32")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_level_the_model_never_saw_is_refused_at_scoring(backend: str) -> None:
    """A level absent from the persisted map has no code, and inventing one would score it
    as whichever level happens to share the number."""
    data = _frequency_data()
    fit = fit_gbm(data, _spec(backend), FACTORS)
    unseen = data.head(5).with_columns(pl.lit("coastal").alias("area"))
    with pytest.raises(GbmFitError, match="coastal"):
        predict_gbm(fit.result, fit.booster_bytes, unseen)


@pytest.mark.req("FR-MODEL-26")
@pytest.mark.parametrize("backend", BACKENDS)
def test_an_objective_outside_the_supported_set_is_named_not_passed_through(
    backend: str,
) -> None:
    """FR-MODEL-26 names a closed set, and it is spelled in XGBoost's vocabulary.

    Translating it per backend is what FR-MODEL-25's "one contract" means: `count:poisson`
    is `poisson` to LightGBM, and a spec that fitted on one backend and failed on the other
    would be a forked contract wearing a shared name.
    """
    spec = _spec(backend, objective=GbmFunctionRef(kind="builtin", name="rank:pairwise"))
    with pytest.raises(GbmFitError, match="rank:pairwise"):
        fit_gbm(_frequency_data(), spec, FACTORS)


@pytest.mark.req("FR-MODEL-39")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_custom_objective_reference_with_no_artifact_is_refused(backend: str) -> None:
    """The reference is not the loss, and `pricing-core` cannot fetch the difference.

    Until 2026-08-18 this refusal read "Custom Objectives are not built"; they are now, and
    the refusal that remains is ADR-0001's. `pricing-core` does not read the objective
    store, so a spec naming a reference with no artifact beside it is a caller that
    resolved nothing, and the message says so rather than failing deeper in.
    """
    spec = _spec(backend, objective=GbmFunctionRef(
        kind="custom", ref="custom_objective:capped-gamma@2"))
    with pytest.raises(GbmFitError, match="custom_objective:capped-gamma@2") as raised:
        fit_gbm(_frequency_data(), spec, FACTORS)
    assert raised.value.code == "OBJECTIVE_NOT_SUPPLIED"


# --------------------------------------------------------------------------------------
# FR-MODEL-73 — the loss treatment, applied at fit time
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-73")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_capped_response_is_capped_as_the_model_is_fitted(backend: str) -> None:
    """FR-MODEL-73: the cap is applied to the response here, never to the dataset.

    Asserted as an equivalence — fitting capped data with no treatment must give the same
    booster as fitting raw data with the treatment — because that is the property that
    makes one validated Dataset Version serve many capping assumptions.
    """
    data = _frequency_data().with_columns(
        pl.when(pl.int_range(pl.len()) < 20).then(40.0)
        .otherwise(pl.col("claim_count")).alias("claim_count")
    )
    treated = fit_gbm(
        data,
        _spec(backend, loss_treatment=LossTreatment(
            kind="capped", cap_minor=3, restoration_loading=1.02)),
        FACTORS,
    )
    pre_capped = data.with_columns(pl.col("claim_count").clip(upper_bound=3.0))
    plain = fit_gbm(pre_capped, _spec(backend), FACTORS)
    assert treated.result.booster_blob.sha256 == plain.result.booster_blob.sha256

    uncapped = fit_gbm(data, _spec(backend), FACTORS)
    assert uncapped.result.booster_blob.sha256 != treated.result.booster_blob.sha256


@pytest.mark.req("FR-MODEL-73")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_treatment_this_slice_does_not_implement_is_refused_by_name(backend: str) -> None:
    """`spliced` and `excess` are declared by FR-MODEL-73 and built by nothing.

    Refused with the requirement's name in the message rather than applied as `none`,
    which would silently fit an uncapped model under a spec that says otherwise — and the
    spec is what `spec_hash` and the model document both report.
    """
    spec = _spec(backend, loss_treatment=LossTreatment(kind="excess", cap_minor=3))
    with pytest.raises(GbmFitError, match="excess"):
        fit_gbm(_frequency_data(), spec, FACTORS)


@pytest.mark.req("FR-MODEL-29")
@pytest.mark.parametrize("backend", BACKENDS)
def test_an_interaction_group_naming_an_unknown_feature_is_refused(backend: str) -> None:
    """FR-MODEL-29's constraint is positional once it reaches either backend, and both
    **ignore** a name that matches no feature.

    Ignored means the group silently permits what it was written to forbid — the failure
    mode of a constraint is that nothing happens, and nothing happening looks exactly like
    a constraint that was satisfied.
    """
    spec = _spec(backend, interaction_constraints=(("driv_age", "vehicle_group"),))
    with pytest.raises(GbmFitError, match="vehicle_group"):
        fit_gbm(_frequency_data(), spec, FACTORS)


@pytest.mark.req("FR-MODEL-29")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_declared_interaction_group_reaches_the_backend(backend: str) -> None:
    """The happy path, because the refusal above proves only the refusal.

    Permitting interaction only *within* `{area, driv_age}` is the whole feature set here,
    so the constraint cannot change the answer — what is being asserted is that both
    libraries accept the translated form rather than rejecting the parameter, which is the
    part that differs between them.
    """
    spec = _spec(backend, interaction_constraints=(("area", "driv_age"),))
    fit = fit_gbm(_frequency_data(), spec, FACTORS)
    assert fit.result.feature_order == ("area", "driv_age")


# --------------------------------------------------------------------------------------
# FR-MODEL-52 — GBM diagnostics
# --------------------------------------------------------------------------------------


def _diagnose(backend: str, factors: list[Factor] | None = None):  # type: ignore[no-untyped-def]
    from pricing_core.modelling import compute_gbm_diagnostics

    use = factors or FACTORS
    train, holdout = _frequency_data(), _frequency_data(n=3_000, seed=4242)
    fit = fit_gbm(train, _spec(backend, factors=tuple(f.id for f in use)), use)
    return fit, compute_gbm_diagnostics(
        fit.result, fit.booster_bytes,
        _spec(backend, factors=tuple(f.id for f in use)), use,
        train=train, holdout=holdout, eval_curve=fit.eval_curve,
    )


@pytest.mark.req("FR-MODEL-54")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_gbm_reports_both_partitions_through_the_same_code_as_a_glm(backend: str) -> None:
    """FR-MODEL-50 says the universal diagnostics are for *all model types*, and
    FR-MODEL-54 says both partitions or it is a defect.

    Both hold here because `_partition` takes `mu` and knows nothing about how it was
    produced — the same function computes a GLM's A/E and a GBM's. Two implementations
    would drift, and FR-MODEL-56's comparison would then be two conventions placed side by
    side rather than a comparison.
    """
    _, diagnostics = _diagnose(backend)
    assert diagnostics.universal.train.ae_overall > 0
    assert diagnostics.universal.holdout.ae_overall > 0
    assert diagnostics.universal.train.ae_by_factor
    assert diagnostics.glm is None
    assert diagnostics.gbm is not None


@pytest.mark.req("FR-MODEL-52")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_three_split_importances_are_reported_and_cover_is_honest(backend: str) -> None:
    """FR-MODEL-52 asks for gain, cover and frequency.

    LightGBM exposes `split` and `gain` and **no cover**, so `cover` is `None` there rather
    than zero. A zero would read as a measurement — "this feature covered no rows" — when
    the truth is that the backend does not report the quantity at all.
    """
    _, diagnostics = _diagnose(backend)
    assert diagnostics.gbm is not None
    importances = {i.feature: i for i in diagnostics.gbm.importances}
    assert set(importances) == {"area", "driv_age"}
    assert importances["driv_age"].gain > 0
    if backend == "xgboost":
        assert importances["driv_age"].cover is not None
    else:
        assert all(i.cover is None for i in diagnostics.gbm.importances)


@pytest.mark.req("FR-MODEL-52")
@pytest.mark.parametrize("backend", BACKENDS)
def test_permutation_importance_degrades_the_holdout_when_signal_is_destroyed(
    backend: str,
) -> None:
    """FR-MODEL-52's permutation importance answers a different question from split
    importance: what would this model lose if the variable were noise.

    Asserted as a *degradation*, on the holdout, for a factor the data-generating process
    actually uses — if shuffling `driv_age` did not hurt, either the model never learned it
    or the permutation never reached the feature.
    """
    _, diagnostics = _diagnose(backend)
    assert diagnostics.gbm is not None
    by_feature = {p.feature: p for p in diagnostics.gbm.permutation_importances}
    assert by_feature["driv_age"].degradation > 0
    assert by_feature["driv_age"].permuted > by_feature["driv_age"].baseline


@pytest.mark.req("FR-MODEL-52")
@pytest.mark.parametrize("backend", BACKENDS)
def test_partial_dependence_carries_the_exposure_share_of_each_point(backend: str) -> None:
    """A partial dependence curve is most dramatic exactly where the book is thinnest.

    The share rides with every point so a spike over 0.2 % of exposure cannot be read as a
    rating signal by a chart that never had the denominator.
    """
    _, diagnostics = _diagnose(backend)
    assert diagnostics.gbm is not None
    curves = {c.factor: c for c in diagnostics.gbm.partial_dependence}
    area = curves["area"]
    assert [p.value for p in area.points] == ["rural", "urban"]
    assert sum(p.exposure_share for p in area.points) == pytest.approx(1.0, abs=1e-9)


@pytest.mark.req("FR-MODEL-52")
@pytest.mark.parametrize("backend", BACKENDS)
def test_monotonicity_is_verified_on_the_fitted_response_not_assumed(backend: str) -> None:
    """FR-MODEL-52: *that the fitted response actually respects declared constraints*.

    A constraint is a parameter handed to a library. What makes it true of this model is
    that something swept the factor and looked — which is also what
    `TransparencyArtifact.monotonicity_verified` will report upward under R3.
    """
    factors = [
        _factor("area", "area"),
        _factor("driv_age", "driv_age", monotonic_direction=MonotonicDirection.INCREASING,
                monotonic_rationale="claim frequency rises with age in this book"),
    ]
    _, diagnostics = _diagnose(backend, factors)
    assert diagnostics.gbm is not None
    checks = {c.factor: c for c in diagnostics.gbm.monotonicity}
    assert set(checks) == {"driv_age"}, "a factor with no declared direction has nothing to verify"
    assert checks["driv_age"].holds
    assert checks["driv_age"].declared == "increasing"


@pytest.mark.req("FR-MODEL-81")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_boosted_models_parameter_count_is_its_leaves(backend: str) -> None:
    """FR-MODEL-81 records a fitted-parameter count on every fit, and a GBM has no
    coefficient vector.

    Counting factors instead would report a stump and a thousand deep trees as equally
    complex, which is precisely the comparison exposure-per-parameter exists to make.
    """
    _, diagnostics = _diagnose(backend)
    assert diagnostics.gbm is not None
    assert diagnostics.complexity.factor_count == 2
    assert diagnostics.complexity.parameter_count > 100
    assert diagnostics.complexity.exposure_per_parameter is not None
    assert diagnostics.gbm.tree_count == 40
    assert diagnostics.gbm.max_depth <= 3


# --------------------------------------------------------------------------------------
# FR-MODEL-39..46 — fitting under a Custom Objective
# --------------------------------------------------------------------------------------


def _custom(
    template: ObjectiveTemplate = ObjectiveTemplate.POISSON,
    *,
    slug: str = "capped-gamma",
    version: int = 2,
    status: ObjectiveStatus = ObjectiveStatus.APPROVED,
    **over: object,
) -> CustomObjective:
    """A fittable Custom Objective, defaulting to the template's own applicability.

    `status` defaults past `draft` and so a `certificate_id` is required — the contract
    refuses one without it, which is FR-MODEL-42 and is tested where it lives.
    """
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "version": version, "template": template,
        "params": dict(_DEFAULTS.get(template, {})),
        "applicability": TEMPLATE_APPLICABILITY[template],
        "status": status, "certificate_id": uuid4(),
    }
    fields.update(over)
    return CustomObjective(**fields)  # type: ignore[arg-type]


#: Parameters for the templates used below. The catalogue's own defaults are resolved at
#: compile time; these are the ones with no default worth guessing at.
_DEFAULTS: dict[ObjectiveTemplate, dict[str, float]] = {
    ObjectiveTemplate.FOCAL_BINOMIAL: {"gamma": 2.0},
}


def _custom_spec(backend: str, objective: CustomObjective, **over: object) -> GbmSpec:
    fields: dict[str, object] = {
        "objective": GbmFunctionRef(
            kind="custom",
            ref=f"custom_objective:{objective.slug}@{objective.version}",
        ),
        "response": ResponseKind.CLAIM_COUNT,
    }
    fields.update(over)
    return _spec(backend, **fields)


@pytest.mark.req("FR-MODEL-72")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_custom_objective_prediction_scales_exactly_with_exposure(backend: str) -> None:
    """FR-MODEL-72's test again, and it is not a duplicate of the builtin one.

    A custom objective changes *who applies the inverse link* on both backends at once:
    XGBoost's `predict` transforms under a builtin objective and cannot under a callable
    one, having been handed gradients and no link. Both branches of `predict_gbm` are
    therefore on a different path here from the one the builtin test exercises, and a
    branch that returned the raw margin would come back as a ratio of `exp(log 2)` — no,
    of 1, because the margin is additive and the exposure doubling is not in it at all.
    """
    data = _frequency_data()
    objective = _custom()
    fit = fit_gbm(data, _custom_spec(backend, objective), FACTORS, objective=objective)

    single = predict_gbm(fit.result, fit.booster_bytes, data)
    doubled = predict_gbm(
        fit.result, fit.booster_bytes,
        data.with_columns(pl.col("exposure_years") * 2.0),
    )
    ratio = (doubled / single).to_numpy()
    assert np.allclose(ratio, 2.0, rtol=1e-5), f"{backend}: exposure is not in the score"


@pytest.mark.req("FR-MODEL-39")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_custom_poisson_reproduces_the_observed_claim_total(backend: str) -> None:
    """The `poisson` template *is* `count:poisson`, so the fit it produces must be one.

    Total predicted claims against total observed is the check an actuary makes first, and
    it is the one that fails loudly when the offset, the link or the gradient is wrong —
    each of which is on a different code path here from the builtin fit.
    """
    data = _frequency_data()
    objective = _custom()
    fit = fit_gbm(data, _custom_spec(backend, objective), FACTORS, objective=objective)

    predicted = predict_gbm(fit.result, fit.booster_bytes, data).sum()
    observed = float(data["claim_count"].sum())
    assert predicted == pytest.approx(observed, rel=0.05), f"{backend}: {predicted} vs {observed}"


@pytest.mark.req("FR-MODEL-94")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_artifact_records_who_applies_the_inverse_link(backend: str) -> None:
    """`inverse_link` is a claim about the *library*, not about the model's link function.

    All four combinations below are log-link Poisson models and only one of them leaves the
    transform to the backend. Recording the link instead of who applies it would have made
    these four indistinguishable, and scoring would have had to guess.
    """
    data = _frequency_data()
    objective = _custom()

    builtin = fit_gbm(data, _spec(backend), FACTORS).result
    custom = fit_gbm(
        data, _custom_spec(backend, objective), FACTORS, objective=objective
    ).result

    assert builtin.inverse_link == (None if backend == "xgboost" else "exp")
    assert custom.inverse_link == "exp"


def _conversion_data(n: int = 6_000, seed: int = 20260818) -> pl.DataFrame:
    """A binomial book with a strong signal, so the fitted scores leave `f = 0` behind.

    That matters for the test below: `exp(f)` and `1 / (1 + exp(-f))` agree to within 1% at
    `f = 0`, so a book that produced scores near zero would hide the defect this data
    exists to expose.
    """
    rng = np.random.default_rng(seed)
    urban = rng.integers(0, 2, n)
    age = rng.integers(18, 80, n)
    eta = 1.4 + 1.2 * urban + 0.04 * (age - 40)
    return pl.DataFrame(
        {
            "exposure_years": np.ones(n),
            "area": ["urban" if u else "rural" for u in urban],
            "driv_age": age.astype(float),
            "claim_count": rng.binomial(1, 1.0 / (1.0 + np.exp(-eta))).astype(float),
        }
    )


@pytest.mark.req("FR-MODEL-94")
@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("custom", [False, True], ids=["builtin", "custom"])
def test_a_binomial_model_is_scored_through_its_own_link(backend: str, custom: bool) -> None:
    """A probability is at most one, and until 2026-08-18 LightGBM's were not.

    `predict_gbm`'s LightGBM branch exponentiated the raw score unconditionally, so a
    `binary:logistic` model returned `exp(f)` — above 1 for every row the model thought
    likely, which is most of them on this book. The builtin case here is the regression
    test for that defect; the custom case is `focal_binomial`, the one template whose
    inverse link is not `exp`, and it fails the same way if the link is assumed.
    """
    data = _conversion_data()
    objective = _custom(ObjectiveTemplate.FOCAL_BINOMIAL, slug="focal-conversion")
    if custom:
        spec = _spec(
            backend,
            objective=GbmFunctionRef(
                kind="custom",
                ref=f"custom_objective:{objective.slug}@{objective.version}",
            ),
            response=ResponseKind.CONVERSION,
            offset=OffsetSpec(kind="none"),
        )
        fit = fit_gbm(data, spec, FACTORS, objective=objective)
    else:
        spec = _spec(
            backend,
            objective=GbmFunctionRef(kind="builtin", name="binary:logistic"),
            offset=OffsetSpec(kind="none"),
        )
        fit = fit_gbm(data, spec, FACTORS)

    assert fit.result.inverse_link == (None if backend == "xgboost" and not custom else "logistic")
    predicted = predict_gbm(fit.result, fit.booster_bytes, data).to_numpy()
    assert predicted.min() > 0.0
    assert predicted.max() <= 1.0, f"{backend}: a probability above one is exp(f), not g(f)"
    urban = data["area"].to_numpy() == "urban"
    assert predicted[urban].mean() > predicted[~urban].mean(), "the signal is not in the score"
    if not custom:
        # A calibrated binomial score averages to the observed rate. Not asserted of the
        # focal objective: down-weighting the examples it already gets right is what
        # `gamma` *is*, and the price of it is a score pulled towards 0.5 — a known
        # property of focal loss, not a defect in the link.
        assert predicted.mean() == pytest.approx(float(data["claim_count"].mean()), abs=0.05)


@pytest.mark.req("FR-MODEL-44")
@pytest.mark.parametrize("backend", BACKENDS)
def test_an_objective_outside_its_declared_applicability_is_refused(backend: str) -> None:
    """FR-MODEL-44, on each of the three axes an author can narrow.

    Refused before the fit rather than reported after it: every one of these produces a
    model that converges, and a Poisson loss fitted to severity converges to a number that
    looks like a severity.
    """
    data = _frequency_data()

    severity_only = _custom(ObjectiveTemplate.GAMMA, slug="gamma-severity")
    spec = _custom_spec(backend, severity_only)
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(data, spec, FACTORS, objective=severity_only)
    assert raised.value.code == "OBJECTIVE_NOT_APPLICABLE"
    assert "claim_severity" in str(raised.value)

    other = "lightgbm" if backend == "xgboost" else "xgboost"
    one_backend = _custom(
        applicability=TEMPLATE_APPLICABILITY[ObjectiveTemplate.POISSON].model_copy(
            update={"backends": frozenset({ObjectiveBackend(other)})}
        ),
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(data, _custom_spec(backend, one_backend), FACTORS, objective=one_backend)
    assert raised.value.code == "OBJECTIVE_NOT_APPLICABLE"
    assert other in str(raised.value)

    needs_offset = _custom()
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(
            data,
            _custom_spec(backend, needs_offset, offset=OffsetSpec(kind="none")),
            FACTORS,
            objective=needs_offset,
        )
    assert raised.value.code == "OBJECTIVE_REQUIRES_OFFSET"


@pytest.mark.req("FR-MODEL-44")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_custom_objective_without_a_declared_response_is_refused(backend: str) -> None:
    """A builtin objective names its family; a custom one does not, and neither may guess.

    `response` is what FR-MODEL-44's applicability check and the diagnostics deviance are
    both read from — see `objective_family`. Fitting with it unset would mean picking one
    of the five, and the fit would be reported under a family nobody chose.
    """
    objective = _custom()
    spec = _custom_spec(backend, objective, response=None)
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(_frequency_data(), spec, FACTORS, objective=objective)
    assert raised.value.code == "OBJECTIVE_RESPONSE_UNDECLARED"


@pytest.mark.req("FR-MODEL-46")
@pytest.mark.parametrize(
    "status", [ObjectiveStatus.DRAFT, ObjectiveStatus.DEPRECATED], ids=lambda s: s.value
)
def test_an_objective_that_is_not_fittable_is_refused_by_its_status(
    status: ObjectiveStatus,
) -> None:
    """`02` R4: a model may not be fitted under an uncertified or withdrawn loss.

    Both ends of FR-MODEL-46's lifecycle, because they fail for opposite reasons — a draft
    has never been certified and a deprecated one has been withdrawn — and a check written
    as `status is not approved` would pass `deprecated` straight through if the enum ever
    gained a member.
    """
    objective = _custom(status=status, certificate_id=None if status is
                        ObjectiveStatus.DRAFT else uuid4())
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(
            _frequency_data(), _custom_spec("xgboost", objective), FACTORS,
            objective=objective,
        )
    assert raised.value.code == "OBJECTIVE_NOT_APPROVED"
    assert status.value in str(raised.value)


@pytest.mark.req("FR-MODEL-39")
def test_an_artifact_that_is_not_the_one_the_spec_names_is_refused() -> None:
    """The spec's reference and the artifact handed in must be the same objective.

    Not a redundant check: the caller resolves the reference, so nothing between the spec
    and the fit compares them. A model fitted under a loss its own spec does not name
    cannot be reproduced from the spec, which is what a rebuild reads.
    """
    objective = _custom(version=3)
    spec = _spec(
        "xgboost",
        objective=GbmFunctionRef(kind="custom", ref="custom_objective:capped-gamma@2"),
        response=ResponseKind.CLAIM_COUNT,
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(_frequency_data(), spec, FACTORS, objective=objective)
    assert raised.value.code == "OBJECTIVE_REF_MISMATCH"


@pytest.mark.req("FR-MODEL-39")
def test_an_artifact_supplied_for_a_builtin_spec_is_refused() -> None:
    """Two objectives, one fit. Ignoring either silently is the failure this refuses.

    The artifact would lose, since `spec.objective` is what reaches the backend — and the
    stored result would name the builtin, so nothing downstream could tell that a
    certified loss had been handed in and dropped.
    """
    objective = _custom()
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(_frequency_data(), _spec("xgboost"), FACTORS, objective=objective)
    assert raised.value.code == "OBJECTIVE_NOT_APPLICABLE"
    assert "count:poisson" in str(raised.value)


@pytest.mark.req("FR-MODEL-45")
@pytest.mark.parametrize("backend", BACKENDS)
def test_early_stopping_under_a_custom_objective_is_refused_by_name(backend: str) -> None:
    """FR-MODEL-45 is not built, and this is the shape of its absence.

    Under a callable objective both backends hand a builtin metric the raw score rather
    than the transformed prediction, so the metric it stops on is not the metric it names —
    and stopping on the wrong metric produces a model that is merely worse, never one that
    errors. Refused with FR-MODEL-45 named, so the message says which capability is
    missing.
    """
    objective = _custom()
    spec = _custom_spec(
        backend, objective,
        early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=5),
    )
    with pytest.raises(GbmFitError, match="FR-MODEL-45") as raised:
        fit_gbm(_frequency_data(), spec, FACTORS, objective=objective)
    assert raised.value.code == "OBJECTIVE_EARLY_STOPPING_UNSUPPORTED"


# --------------------------------------------------------------------------------------
# FR-MODEL-106 / FR-MODEL-107 — `eval_metrics` honoured, early stopping on a custom metric
# --------------------------------------------------------------------------------------

_METRIC_REF = "custom_metric:poisson-nll@1"


def _metric(
    template: ObjectiveTemplate = ObjectiveTemplate.POISSON,
    *,
    slug: str = "poisson-nll",
    version: int = 1,
    status: MetricStatus = MetricStatus.APPROVED,
    **over: object,
) -> CustomMetric:
    """A fittable Custom Metric, defaulting to the template's own applicability.

    Mirrors `_custom` above (the same defaulting-past-`draft` reasoning applies): a
    `status` past `draft` needs a `certificate_id`, supplied unconditionally here since
    `draft` tolerates one too.
    """
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "version": version, "template": template,
        "params": dict(_DEFAULTS.get(template, {})),
        "applicability": TEMPLATE_APPLICABILITY[template],
        "direction": MetricDirection.LOWER_IS_BETTER,
        "status": status, "certificate_id": uuid4(),
    }
    fields.update(over)
    return CustomMetric(**fields)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-107")
@pytest.mark.parametrize("backend", BACKENDS)
def test_early_stopping_on_a_custom_metric_is_allowed_under_a_custom_objective(
    backend: str,
) -> None:
    """The refusal FR-MODEL-45 was deferred behind is retired for a metric the spec names.

    `evaluate_metric` is written against the raw score by construction, so the reason the
    unconditional refusal gave — a builtin metric silently sees the wrong quantity under a
    callable objective — never applied to a custom one.
    """
    objective = _custom()
    metric = _metric()
    spec = _custom_spec(
        backend, objective,
        eval_metrics=(GbmFunctionRef(kind="custom", ref=_METRIC_REF),),
        early_stopping=EarlyStopping(on="holdout", metric=_METRIC_REF, rounds=5),
    )
    fit = fit_gbm(
        _frequency_data(), spec, FACTORS, holdout=_frequency_data(n=3_000, seed=99),
        objective=objective, metrics={_METRIC_REF: metric},
    )
    assert fit.result.best_iteration is not None
    assert fit.eval_curve
    assert {point.metric for point in fit.eval_curve} == {_METRIC_REF}
    assert all(point.holdout is not None for point in fit.eval_curve)
    assert all(point.train is not None for point in fit.eval_curve)


@pytest.mark.req("FR-MODEL-107")
@pytest.mark.parametrize("backend", BACKENDS)
def test_early_stopping_on_a_builtin_metric_is_still_refused_under_a_custom_objective(
    backend: str,
) -> None:
    """The narrowing must not become a removal — the raw-score problem is unchanged for a
    metric the spec did not name as one of its own `eval_metrics`.

    A *different* Custom Metric is declared on the same spec, so this also proves the
    refusal is keyed on the named metric matching a declared ref, not on whether any
    Custom Metric is declared at all.
    """
    objective = _custom()
    metric = _metric()
    spec = _custom_spec(
        backend, objective,
        eval_metrics=(GbmFunctionRef(kind="custom", ref=_METRIC_REF),),
        early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=5),
    )
    with pytest.raises(GbmFitError, match="FR-MODEL-45") as raised:
        fit_gbm(
            _frequency_data(), spec, FACTORS, objective=objective, metrics={_METRIC_REF: metric}
        )
    assert raised.value.code == "OBJECTIVE_EARLY_STOPPING_UNSUPPORTED"


_OTHER_METRIC_REF = "custom_metric:poisson-nll-other@1"


@pytest.mark.req("FR-MODEL-107")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_second_custom_eval_metric_survives_early_stopping_on_the_first(
    backend: str,
) -> None:
    """A declared custom eval metric the fit does not stop on must still reach the curve.

    LightGBM's early-stopping callback can only target "the first metric" by *name*
    (`first_metric_only`), never one by name — but `first_metric_only` decides which
    metric *drives the stop*, not which metrics are *reported*. Nothing before this test
    declared more than one custom eval metric on the same spec, so a version of this
    module that mistook the first for a license to drop the second passed every other
    test in this file. `gbm.py`'s own module docstring commits to FR-MODEL-25's "one
    contract, two backends" — this pins that XGBoost and LightGBM agree here, and that
    stopping still lands on the iteration a single-metric fit would choose, not on
    whichever metric happens to be first in `metrics`' insertion order.
    """
    metric = _metric()
    other = _metric(slug="poisson-nll-other")
    holdout = _frequency_data(n=3_000, seed=99)
    # Enough rounds, and an aggressive enough learning rate, that the holdout genuinely
    # overfits before the round cap — otherwise "stopped at the cap" and "stopped because
    # of the named metric" are indistinguishable.
    hyperparameters = {"max_depth": 6, "eta": 0.3, "num_boost_round": 300}
    spec = _spec(
        backend, response=ResponseKind.CLAIM_COUNT, hyperparameters=hyperparameters,
        eval_metrics=(
            GbmFunctionRef(kind="custom", ref=_METRIC_REF),
            GbmFunctionRef(kind="custom", ref=_OTHER_METRIC_REF),
        ),
        early_stopping=EarlyStopping(on="holdout", metric=_METRIC_REF, rounds=5),
    )
    fit = fit_gbm(
        _frequency_data(), spec, FACTORS, holdout=holdout,
        metrics={_METRIC_REF: metric, _OTHER_METRIC_REF: other},
    )
    assert {point.metric for point in fit.eval_curve} == {_METRIC_REF, _OTHER_METRIC_REF}

    solo_spec = spec.model_copy(
        update={"eval_metrics": (GbmFunctionRef(kind="custom", ref=_METRIC_REF),)}
    )
    solo = fit_gbm(
        _frequency_data(), solo_spec, FACTORS, holdout=holdout, metrics={_METRIC_REF: metric}
    )
    assert fit.result.best_iteration == solo.result.best_iteration


@pytest.mark.req("FR-MODEL-106")
def test_a_custom_eval_metric_that_was_not_supplied_refuses_the_fit() -> None:
    """ADR-0001: `pricing-core` does not resolve refs, so an unsupplied one is the
    caller's bug, not a lookup failure to retry."""
    spec = _spec(
        "xgboost", response=ResponseKind.CLAIM_COUNT,
        eval_metrics=(GbmFunctionRef(kind="custom", ref="custom_metric:absent@1"),),
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(_frequency_data(), spec, FACTORS)
    assert raised.value.code == "METRIC_REF_UNRESOLVED"


@pytest.mark.req("FR-MODEL-106")
def test_a_metric_whose_applicability_excludes_the_backend_refuses_the_fit() -> None:
    lightgbm_only = _metric(
        applicability=Applicability(
            responses=(ResponseKind.CLAIM_COUNT,),
            backends=(ObjectiveBackend.LIGHTGBM,),
            offset_required=True,
            y_domain=YDomain(min_inclusive=0.0),
        )
    )
    spec = _spec(
        "xgboost", response=ResponseKind.CLAIM_COUNT,
        eval_metrics=(GbmFunctionRef(kind="custom", ref=_METRIC_REF),),
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(_frequency_data(), spec, FACTORS, metrics={_METRIC_REF: lightgbm_only})
    assert raised.value.code == "METRIC_NOT_APPLICABLE"


@pytest.mark.req("FR-MODEL-106")
def test_a_draft_metric_cannot_be_fitted_with() -> None:
    """FITTABLE_METRIC_STATUSES excludes draft: an uncertified metric is unproven."""
    draft = _metric(status=MetricStatus.DRAFT)
    spec = _spec(
        "xgboost", response=ResponseKind.CLAIM_COUNT,
        eval_metrics=(GbmFunctionRef(kind="custom", ref=_METRIC_REF),),
    )
    with pytest.raises(GbmFitError) as raised:
        fit_gbm(_frequency_data(), spec, FACTORS, metrics={_METRIC_REF: draft})
    assert raised.value.code == "METRIC_NOT_FITTABLE"


@pytest.mark.req("FR-MODEL-106")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_builtin_eval_metric_reaches_the_backend(backend: str) -> None:
    """The half that needed no FR-MODEL-45 machinery and was ignored anyway."""
    spec = _spec(backend, eval_metrics=(GbmFunctionRef(kind="builtin", name="poisson-nloglik"),))
    fit = fit_gbm(
        _frequency_data(), spec, FACTORS, holdout=_frequency_data(n=3_000, seed=99)
    )
    assert "poisson-nloglik" in {point.metric for point in fit.eval_curve}
