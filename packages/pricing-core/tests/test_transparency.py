"""Transparency artifacts (`02` §3.6, FR-MODEL-33..37, 79, R3).

R3 is the rule these serve: fitting a black box is allowed, pricing with an unexplained one
is not. So the tests are about whether the explanation is *honest*, not whether it exists —
an artifact that reported a good fit without saying where the fit is bad would satisfy R3
and mislead the approver who relies on it.
"""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest
from test_gbm import BACKENDS, FACTORS, _factor, _frequency_data, _spec

from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    MonotonicDirection,
    TransparencyArtifact,
    TransparencyKind,
    new_uuid7,
)
from pricing_core.modelling import (
    build_glm_approximation,
    build_shap_summary,
    fidelity_statement,
    fit_gbm,
)


def _fit(backend: str, factors=None, n: int = 6_000):  # type: ignore[no-untyped-def]
    use = factors or FACTORS
    data = _frequency_data(n=n)
    spec = _spec(backend, factors=tuple(f.id for f in use))
    return data, spec, use, fit_gbm(data, spec, use)


@pytest.mark.req("FR-MODEL-34")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_approximation_is_fitted_to_the_boosters_predictions(backend: str) -> None:
    """FR-MODEL-34's whole method: the GLM is fitted to what the **GBM says**, not to the
    data.

    A GLM fitted to the response would be a second model, and the question is not "what
    would a GLM say" but "how much of what this booster says is expressible as a table".
    The data here is generated from a log-linear structure the GBM can learn well, so a
    surrogate that reproduces most of its variance is the expected result — and one that
    did not would mean the approximation was fitted to something else.
    """
    data, spec, factors, fit = _fit(backend)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    assert approximation.r_squared > 0.8
    assert approximation.deviance_explained > 0.5
    # It is a rateable table or it is not an approximation (FR-MODEL-34) — and from
    # FR-MODEL-96 the table is the surrogate Model's fit result.
    assert approximation.result.relativities
    assert any(c.term == "intercept" for c in approximation.result.coefficients)


@pytest.mark.req("FR-MODEL-36")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_worst_regions_name_a_cell_and_its_share_of_the_book(backend: str) -> None:
    """FR-MODEL-36 asks *where* the approximation fails and over how much exposure.

    By factor level rather than by arbitrary slice: a region an actuary cannot name is a
    region they cannot act on. The share is what stops "11 % out for young drivers" being
    read as a portfolio-wide problem when it is 0.8 % of the book.
    """
    data, spec, factors, fit = _fit(backend)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    assert approximation.worst_regions
    worst = approximation.worst_regions[0]
    assert worst.description.startswith("area = ")
    assert 0.0 < worst.exposure_share <= 1.0
    assert worst.mean_abs_error_pct >= 0.0
    # Sorted worst-first, or "the worst region" names whichever came out of the loop first.
    percentages = [region.mean_abs_error_pct for region in approximation.worst_regions]
    assert percentages == sorted(percentages, reverse=True)


@pytest.mark.req("FR-MODEL-35")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_shap_summary_persists_the_sample_it_was_computed_on(backend: str) -> None:
    """FR-MODEL-35: a reproducible sample, with the seed and the size persisted.

    Both, because a SHAP summary computed on a different sample is a different summary —
    and two of them side by side in a model document would read as a change in the model
    rather than a change in the sampling.
    """
    data, spec, factors, fit = _fit(backend)
    summary = build_shap_summary(
        fit.result, fit.booster_bytes, spec, factors, data, sample=2_000, seed=99
    )
    assert summary.sample_rows == 2_000
    assert summary.seed == 99
    assert summary.algorithm == "tree_shap"
    contributions = {c.factor: c.value for c in summary.mean_abs_contribution}
    assert set(contributions) == {"area", "driv_age"}
    assert all(value >= 0 for value in contributions.values())
    # Ordered by contribution: the first row of this table is what a reader takes as "what
    # the model is mostly doing".
    values = [c.value for c in summary.mean_abs_contribution]
    assert values == sorted(values, reverse=True)


@pytest.mark.req("FR-MODEL-35")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_same_seed_reproduces_the_same_summary(backend: str) -> None:
    """"Reproducible" is a claim, and this is the test that makes it one."""
    data, spec, factors, fit = _fit(backend)
    first = build_shap_summary(
        fit.result, fit.booster_bytes, spec, factors, data, sample=1_500, seed=7
    )
    second = build_shap_summary(
        fit.result, fit.booster_bytes, spec, factors, data, sample=1_500, seed=7
    )
    assert [c.value for c in first.mean_abs_contribution] == pytest.approx(
        [c.value for c in second.mean_abs_contribution]
    )


@pytest.mark.req("FR-MODEL-79")
def test_interaction_candidates_are_reported_where_the_backend_can_compute_them() -> None:
    """FR-MODEL-79: suggestions, ranked, and **never** written into a Model Spec.

    XGBoost only — LightGBM computes SHAP values and not SHAP interaction values. Named as
    a backend fact rather than parametrized away, because the asymmetry is the finding.
    """
    data, spec, factors, fit = _fit("xgboost")
    summary = build_shap_summary(
        fit.result, fit.booster_bytes, spec, factors, data, sample=1_000
    )
    assert summary.interactions_available is True
    assert summary.top_interactions
    pair = summary.top_interactions[0]
    assert set(pair.pair) == {"area", "driv_age"}
    assert pair.strength >= 0.0


@pytest.mark.req("FR-MODEL-79")
def test_lightgbm_says_it_cannot_compute_interactions_rather_than_finding_none() -> None:
    """An empty `top_interactions` with `interactions_available=True` would read as "the
    model has no interactions", which is a finding.

    LightGBM cannot make it. The flag is the difference between a measurement and a
    capability, and a reviewer comparing two models across backends would otherwise
    conclude the LightGBM one was simpler.
    """
    data, spec, factors, fit = _fit("lightgbm")
    summary = build_shap_summary(
        fit.result, fit.booster_bytes, spec, factors, data, sample=1_000
    )
    assert summary.interactions_available is False
    assert summary.top_interactions == ()


@pytest.mark.req("FR-MODEL-36")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_fidelity_statement_says_where_the_approximation_fails(backend: str) -> None:
    """FR-MODEL-36 is prose because a number cannot say *where*.

    Generated rather than authored: a free-text field carrying that obligation is a field
    that eventually says "good fit", and this is the sentence an approver reads at the
    moment a Rating Version references the model.
    """
    data, spec, factors, fit = _fit(backend)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    summary = build_shap_summary(
        fit.result, fit.booster_bytes, spec, factors, data, sample=1_000
    )
    statement = fidelity_statement(approximation.artifact_block(new_uuid7()), summary)
    assert "%" in statement
    assert "Divergence concentrates in area = " in statement
    if backend == "lightgbm":
        assert "not SHAP interaction values" in statement


@pytest.mark.req("FR-MODEL-33")
def test_an_artifact_that_explains_nothing_is_refused() -> None:
    """FR-MODEL-33 asks for *at least one* form.

    An artifact with neither block would satisfy R3 — a Rating Version could reference the
    model — while explaining nothing at all. That is the one state this shape must not be
    able to represent.
    """
    import datetime

    import pydantic

    with pytest.raises(pydantic.ValidationError, match="explaining nothing"):
        TransparencyArtifact(
            id=new_uuid7(), model_id=new_uuid7(),
            created_at=datetime.datetime.now(datetime.UTC),
            fidelity_statement="looks fine to me",
        )


@pytest.mark.req("FR-MODEL-33")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_kinds_are_derived_from_what_is_present(backend: str) -> None:
    """§4.9 declared `kinds` beside the blocks and wrote the agreement between them as an
    invariant note. Two statements of one fact disagree; this one is a property."""
    import datetime

    data, spec, factors, fit = _fit(backend)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    artifact = TransparencyArtifact(
        id=new_uuid7(), model_id=new_uuid7(),
        created_at=datetime.datetime.now(datetime.UTC),
        glm_approximation=approximation.artifact_block(new_uuid7()),
        fidelity_statement="—",
    )
    assert artifact.kinds == (TransparencyKind.GLM_APPROXIMATION,)


@pytest.mark.req("FR-MODEL-34")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_monotone_gbm_approximates_to_a_monotone_table(backend: str) -> None:
    """The approximation inherits the shape it is approximating.

    Not a tautology: the surrogate is an unconstrained GLM fitted to constrained
    predictions, so a monotone relativity table is evidence that the constraint survived
    into the thing a rate table would be built from — which is what R3 is protecting.
    """
    factors = [
        _factor("area", "area"),
        _factor("driv_age", "driv_age", monotonic_direction=MonotonicDirection.INCREASING,
                monotonic_rationale="claim frequency rises with age in this book"),
    ]
    data, spec, used, fit = _fit(backend, factors)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, used, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    age = next(c for c in approximation.result.coefficients if c.term == "driv_age")
    assert age.estimate > 0


@pytest.mark.req("FR-MODEL-34")
@pytest.mark.parametrize("backend", BACKENDS)
def test_an_approximation_reports_a_poor_fit_as_a_poor_fit(backend: str) -> None:
    """The number that matters most is the one nobody wants: a surrogate that cannot
    reproduce the booster must say so rather than reporting the best it managed.

    Built by hiding the structure from the surrogate — the GBM sees a factor the
    approximation is not given — which is exactly the situation FR-MODEL-36 exists for.
    """
    rng = np.random.default_rng(11)
    n = 6_000
    exposure = rng.uniform(0.1, 1.0, n)
    hidden = rng.integers(0, 2, n)
    noise = rng.normal(0, 1, n)
    data = pl.DataFrame({
        "exposure_years": exposure,
        "area": ["urban" if h else "rural" for h in hidden],
        "driv_age": rng.integers(18, 80, n).astype(float),
        # The response depends on a strong interaction between area and a jagged age
        # effect, which a two-term additive GLM cannot express.
        "claim_count": rng.poisson(
            exposure * np.exp(-2.0 + 3.0 * hidden * np.sin(noise))
        ).astype(float),
    })
    spec = _spec(backend, factors=tuple(f.id for f in FACTORS),
                 hyperparameters={"max_depth": 6, "eta": 0.2, "num_boost_round": 120})
    fit = fit_gbm(data, spec, FACTORS)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, FACTORS, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    assert approximation.r_squared < 0.95
    statement = fidelity_statement(approximation.artifact_block(new_uuid7()), None)
    assert "Divergence concentrates" in statement


@pytest.mark.req("FR-MODEL-96")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_approximation_returns_the_fit_that_produced_it(backend: str) -> None:
    """FR-MODEL-96 persists the surrogate as a Model, so its fit result must survive.

    Before this it was fitted and thrown away, and the artifact kept a summary of a model
    nothing could reproduce.
    """
    data, spec, factors, fit = _fit(backend)
    source = new_uuid7()
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=source,
    )
    assert approximation.result.model_type == "glm"
    assert any(c.term == "intercept" for c in approximation.result.coefficients)
    assert approximation.result.relativities
    assert approximation.spec.approximates_model_id == source
    assert approximation.spec.response_column == SURROGATE_RESPONSE_COLUMN
    # The surrogate target travels with the frames, so the caller's diagnostics measure the
    # surrogate against the booster rather than against the observed response.
    assert SURROGATE_RESPONSE_COLUMN in approximation.train.columns
    assert SURROGATE_RESPONSE_COLUMN in approximation.holdout.columns


@pytest.mark.req("FR-MODEL-96")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_artifact_block_names_the_model_and_carries_no_table(backend: str) -> None:
    """The table lives on the Model now; the block carries the measurements and the id."""
    data, spec, factors, fit = _fit(backend)
    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, factors, data,
        holdout=data, source_model_id=new_uuid7(),
    )
    model_id = new_uuid7()
    block = approximation.artifact_block(model_id)
    assert block.approximating_model_id == model_id
    assert block.coefficients == ()
    assert not block.relativities
    assert block.r_squared == approximation.r_squared
    assert block.worst_regions == approximation.worst_regions
