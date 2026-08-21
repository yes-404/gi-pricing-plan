"""The GBM arm of `ModelSpec` and its fit result (`02` §3.5, §4.4, §4.8).

Every test here is a **prohibition**, for the reason `test_comparison.py` gives: a shape
that can represent a nonsense model eventually holds one, and a Model is what a Rating
Version references.

Four of them exist because the specification said a thing twice and the two copies could
disagree — `backend` beside `model_type`, `base_margin` beside `offset`. The union arm
carries one of each, and these tests are what makes "one" enforceable rather than a
convention.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    MODEL_SPEC_ADAPTER,
    BlobRef,
    EarlyStopping,
    GbmFitResult,
    GbmFunctionRef,
    GbmSpec,
    GlmFitResult,
    GlmSpec,
    IntervalFor,
    LossTreatment,
    Model,
    ModelStatus,
    OffsetSpec,
    SplitRef,
    new_uuid7,
)

EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")


def _spec(**over: object) -> GbmSpec:
    base: dict[str, object] = {
        "model_type": "xgboost",
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": new_uuid7(),
        "split_ref": SplitRef(split_artifact_id=new_uuid7()),
        "response_column": "ad_claim_count",
        "offset": EXPOSURE,
        "objective": GbmFunctionRef(kind="builtin", name="count:poisson"),
        "categorical_handling": "native",
        "hyperparameters": {"max_depth": 5, "eta": 0.05, "num_boost_round": 500},
        "early_stopping": EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=50),
    }
    base.update(over)
    return GbmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-24")
def test_a_gbm_offset_from_another_model_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="GLM specs only"):
        _spec(offset=OffsetSpec(kind="model", offset_model_ref="model:base@1"))


def _fit(**over: object) -> GbmFitResult:
    base: dict[str, object] = {
        "model_type": "xgboost",
        "booster_blob": BlobRef(sha256="a" * 64, bytes=2048, media_type="application/json"),
        "booster_format": "xgboost_json",
        "feature_order": ("driver_age_banded", "vehicle_group_rated"),
        "feature_dtypes": {"driver_age_banded": "i32", "vehicle_group_rated": "i32"},
        "monotone_constraints": (1, 0),
        "base_margin": EXPOSURE,
        "best_iteration": 312,
        "rows": 678_013,
        "fit_seconds": 41.2,
        "library_versions": {"xgboost": "3.4.1"},
    }
    base.update(over)
    return GbmFitResult(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-25")
def test_one_contract_serves_both_backends() -> None:
    """FR-MODEL-25: one `GbmSpec`, two backends, and the contract does not fork."""
    assert _spec(model_type="xgboost").model_type == "xgboost"
    assert _spec(model_type="lightgbm").model_type == "lightgbm"


@pytest.mark.req("FR-MODEL-25")
def test_the_backend_is_not_stated_twice() -> None:
    """`02` §4.4 gave the GBM arm a `backend` field beside `model_type`, whose values are
    the same two strings.

    Two fields carrying one fact can disagree, and nothing downstream would know which to
    believe. `model_type` is the discriminator the union already turns on, so it is the
    one that survives — and a payload still carrying `backend` is refused rather than
    silently ignored, because ignoring it is how the disagreement becomes invisible.
    """
    with pytest.raises(pydantic.ValidationError, match="backend"):
        _spec(backend="lightgbm")


@pytest.mark.req("FR-MODEL-27")
def test_a_frequency_gbm_without_an_offset_is_refused() -> None:
    """FR-MODEL-27: exposure rides in `base_margin`, never as a feature and never by
    weighting a count.

    The same defect `GlmSpec._frequency_declares_its_exposure` refuses: the fit succeeds,
    the numbers look reasonable, and the model has learned claims-per-record.
    """
    with pytest.raises(pydantic.ValidationError, match="offset"):
        _spec(offset=OffsetSpec())


@pytest.mark.req("FR-MODEL-27")
def test_a_frequency_gbm_may_decline_an_offset_only_in_writing() -> None:
    """FR-MODEL-27's "explicit acknowledgement of why not" — the escape hatch is a
    sentence, so the reviewer sees a decision rather than an omission."""
    spec = _spec(offset=OffsetSpec(), offset_acknowledgement="rows are one policy-year each")
    assert spec.offset.kind == "none"


@pytest.mark.req("FR-MODEL-27")
def test_the_offset_is_not_stated_twice() -> None:
    """§4.4's GBM arm carries `base_margin` beside the common block's `offset`, both of
    shape `{kind, column}`.

    FR-MODEL-27 says the platform *constructs* `base_margin` from the declared offset, so
    a second declaration is a second source of truth for one number — and the one the
    booster was actually built with is the one nobody can see afterwards. The fit result
    records what was constructed (FR-MODEL-71); the spec declares it once.
    """
    with pytest.raises(pydantic.ValidationError, match="base_margin"):
        _spec(base_margin=EXPOSURE)


@pytest.mark.req("FR-MODEL-30")
def test_early_stopping_on_the_training_set_has_no_spelling() -> None:
    """FR-MODEL-30: early stopping on the training set is refused.

    Refused by *construction* rather than by a validator — there is no `train` value to
    write — because a stopping rule read off the data being fitted stops when the model
    has finished memorising, which is the opposite of the question it was asked.
    """
    with pytest.raises(pydantic.ValidationError):
        EarlyStopping(on="train", metric="poisson-nloglik", rounds=50)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-26")
def test_an_objective_is_a_builtin_name_or_an_approved_reference_never_both() -> None:
    """FR-MODEL-26. `kind` decides which field is meaningful; carrying both leaves the
    fit path to choose, and two runs could choose differently."""
    with pytest.raises(pydantic.ValidationError, match="name"):
        GbmFunctionRef(kind="builtin", ref="custom_objective:capped-gamma@2")
    with pytest.raises(pydantic.ValidationError, match="ref"):
        GbmFunctionRef(kind="custom", name="count:poisson")
    with pytest.raises(pydantic.ValidationError):
        GbmFunctionRef(kind="builtin", name="count:poisson",
                       ref="custom_objective:capped-gamma@2")


@pytest.mark.req("FR-MODEL-32")
def test_categorical_handling_has_no_default() -> None:
    """FR-MODEL-32: silent label-encoding of an unordered categorical is refused.

    A default would be exactly that silence — the field would be satisfied by nobody
    having thought about it, which is the state the requirement exists to prevent.
    """
    with pytest.raises(pydantic.ValidationError, match="categorical_handling"):
        GbmSpec(  # type: ignore[call-arg]
            model_type="xgboost",
            model_family_slug="motor-ad-frequency",
            dataset_version_id=new_uuid7(),
            response_column="ad_claim_count",
            offset=EXPOSURE,
            objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
            hyperparameters={"num_boost_round": 500},
            early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=50),
        )


@pytest.mark.req("FR-MODEL-29")
def test_an_interaction_group_of_one_constrains_nothing() -> None:
    """FR-MODEL-29: interaction constraints permit interaction *within* declared groups.

    A group naming one feature permits nothing and forbids nothing. Written by hand it is
    almost always a truncated list, and read back it looks deliberate.
    """
    with pytest.raises(pydantic.ValidationError, match="two"):
        _spec(interaction_constraints=(("driver_age_banded",),))


@pytest.mark.req("FR-MODEL-73")
def test_a_cap_is_integer_minor_units_and_carries_its_restoration() -> None:
    """FR-MODEL-73 plus `CLAUDE.md` §7: money is integer minor units, never float.

    The restoration loading is required with the cap because FR-MODEL-74 reconciles a
    capped model against uncapped experience — without it the reconciliation reports a
    modelling error where there was an intended adjustment.
    """
    ok = LossTreatment(kind="capped", cap_minor=2_500_000, restoration_loading=1.043)
    assert ok.cap_minor == 2_500_000

    with pytest.raises(pydantic.ValidationError, match="restoration_loading"):
        LossTreatment(kind="capped", cap_minor=2_500_000)
    with pytest.raises(pydantic.ValidationError, match="cap_minor"):
        LossTreatment(kind="capped", restoration_loading=1.043)
    with pytest.raises(pydantic.ValidationError):
        LossTreatment(kind="capped", cap_minor=25_000.50, restoration_loading=1.043)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-73")
def test_an_untreated_response_carries_no_cap() -> None:
    """`kind='none'` with a cap beside it is a spec whose reader cannot tell whether the
    cap was applied. It is part of `spec_hash`, so the ambiguity would be permanent."""
    with pytest.raises(pydantic.ValidationError, match="none"):
        LossTreatment(kind="none", cap_minor=2_500_000)


@pytest.mark.req("FR-MODEL-31")
def test_a_booster_is_never_a_pickle() -> None:
    """FR-MODEL-31 / ADR-0003: the export format is the backend's JSON or text.

    `pickle` is not a refused value — it is not a value. A format enum that could spell it
    would make the persistence layer's refusal the only thing standing between a Model and
    an artifact that executes on load.
    """
    with pytest.raises(pydantic.ValidationError):
        _fit(booster_format="pickle")


@pytest.mark.req("FR-MODEL-71")
def test_a_booster_without_its_offset_construction_cannot_be_stored() -> None:
    """FR-MODEL-71: omitting the offset at scoring time fails *silently* on both backends.

    The construction is therefore required on the artifact rather than optional, so the
    load-time assertion has something to assert against. An optional field would make the
    silent failure reachable again by leaving it out.
    """
    with pytest.raises(pydantic.ValidationError, match="base_margin"):
        _fit(base_margin=None)


@pytest.mark.req("FR-MODEL-28")
def test_the_constraint_vector_is_aligned_with_the_feature_order() -> None:
    """FR-MODEL-28: the constraint vector is persisted *alongside* the feature order.

    Positional data whose length is not checked is positional data that will one day be
    off by one, and a monotone constraint applied to the wrong column is a model that is
    monotone in the wrong thing — which reads as correct on every screen that shows it.
    """
    with pytest.raises(pydantic.ValidationError, match="feature_order"):
        _fit(monotone_constraints=(1, 0, -1))


@pytest.mark.req("FR-MODEL-25")
def test_the_union_dispatches_on_model_type() -> None:
    """`02` §4.4 calls `ModelSpec` a tagged union. Until now the tag existed and the union
    did not, so `GlmSpec.model_validate` was the only reader and a GBM payload reaching it
    failed on the literal rather than on anything meaningful."""
    payload = _spec().model_dump(mode="json")
    assert isinstance(MODEL_SPEC_ADAPTER.validate_python(payload), GbmSpec)

    glm = GlmSpec(model_family_slug="motor-ad-frequency", dataset_version_id=new_uuid7(),
                  response_column="ad_claim_count", offset=EXPOSURE)
    assert isinstance(MODEL_SPEC_ADAPTER.validate_python(glm.model_dump(mode="json")), GlmSpec)


@pytest.mark.req("FR-MODEL-25")
def test_an_unknown_model_type_is_refused_by_the_discriminator() -> None:
    """`ebm` is a declared model type (`CLAUDE.md` §7) with no arm built.

    It is refused here rather than accepted-and-ignored, which is the difference between
    "not built yet" and a spec that stores as one thing and fits as another.
    """
    payload = {**_spec().model_dump(mode="json"), "model_type": "ebm"}
    with pytest.raises(pydantic.ValidationError, match="model_type"):
        MODEL_SPEC_ADAPTER.validate_python(payload)


@pytest.mark.req("FR-MODEL-25")
def test_a_model_cannot_hold_a_fit_from_another_model_type() -> None:
    """Both arms of both unions are on one artifact, so the pairing has to be stated.

    A `GbmSpec` beside a `GlmFitResult` would be a model whose coefficient table describes
    a booster nobody fitted — and the coefficient table is what a rating basis is read
    from.
    """
    spec = _spec()
    with pytest.raises(pydantic.ValidationError, match="model_type"):
        Model(
            id=new_uuid7(),
            model_family_slug=spec.model_family_slug,
            version=1,
            status=ModelStatus.FITTED,
            spec=spec,
            spec_hash="v3:sha256:" + "b" * 64,
            fit_result=GlmFitResult(converged=True, iterations=8, fit_seconds=1.0),
            diagnostics_id=new_uuid7(),
            dataset_version_id=spec.dataset_version_id,
        )


@pytest.mark.req("FR-MODEL-30")
def test_early_stopping_on_a_holdout_that_was_never_declared_is_refused() -> None:
    """FR-MODEL-30: early stopping requires a **declared** holdout or CV scheme.

    Without `split_ref` there is no holdout, so the backend would evaluate the stopping
    metric on the training rows — the training-set early stopping the requirement forbids,
    arrived at by omission rather than by asking for it.
    """
    with pytest.raises(pydantic.ValidationError, match="split_ref"):
        _spec(split_ref=None)


@pytest.mark.req("FR-MODEL-87")
def test_the_glm_arm_refuses_the_nested_regularisation_block_the_spec_used_to_show() -> None:
    """`02` §4.4 showed a nested `regularisation` object; `GlmSpec` takes the two penalty
    parameters flat, as `glum` does.

    OQ-MODEL-8 (decided 2026-08-17) separated the fields *awaiting a slice* from the ones
    *present under a different shape*, and this was the only member of the second kind: a
    caller copying the page would have sent a body the contract rejects. The page is
    corrected; this test is what stops it drifting back, because `extra="forbid"` is the
    thing that makes the divergence loud rather than silent.
    """
    with pytest.raises(pydantic.ValidationError, match="regularisation"):
        GlmSpec(
            model_family_slug="motor-ad-frequency",
            dataset_version_id=new_uuid7(),
            response_column="ad_claim_count",
            offset=EXPOSURE,
            seed=7,
            regularisation={"kind": "elastic_net", "alpha": 0.001, "l1_ratio": 0.0},
        )
    flat = GlmSpec(
        model_family_slug="motor-ad-frequency",
        dataset_version_id=new_uuid7(),
        response_column="ad_claim_count",
        offset=EXPOSURE,
        seed=7,
        alpha=0.001,
        l1_ratio=0.0,
    )
    assert (flat.alpha, flat.l1_ratio, flat.max_iter, flat.tolerance) == (0.001, 0.0, 200, 1e-8)


@pytest.mark.req("FR-MODEL-100")
def test_an_interval_bound_declares_a_two_sided_alpha() -> None:
    """`alpha` is a quantile, so 0 and 1 are not bounds — they are the whole distribution.

    Exclusive rather than inclusive because the pinball loss at `alpha = 0` has zero
    gradient everywhere the residual is positive: the fit would run, converge on nothing,
    and return a bound indistinguishable from a broken one.
    """
    for impossible in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(pydantic.ValidationError):
            IntervalFor(model_id=new_uuid7(), model_version=1, alpha=impossible)


@pytest.mark.req("FR-MODEL-100")
def test_a_bound_at_the_median_is_not_a_bound() -> None:
    """`alpha = 0.5` is the median — a central estimate, not a side of an interval.

    Refused at the type because FR-MODEL-100(iv) allocates exactly one bound per side and
    finds them by comparing `alpha` with 0.5. A median bound belongs to neither set, so
    admitting it would make "the lower bound of this model" a question with no answer at
    exactly the point the prediction path asks it.
    """
    with pytest.raises(pydantic.ValidationError, match="median"):
        IntervalFor(model_id=new_uuid7(), model_version=1, alpha=0.5)


@pytest.mark.req("FR-MODEL-100")
def test_a_bound_names_a_real_version_of_the_model_it_bounds() -> None:
    """Version 0 does not exist; `Model.version` is `ge=1` and this must agree with it.

    The pair is read back in a review as `slug@version`, and a zero there is a bound
    pointing at nothing that still renders as a citation.
    """
    with pytest.raises(pydantic.ValidationError):
        IntervalFor(model_id=new_uuid7(), model_version=0, alpha=0.05)


@pytest.mark.req("FR-MODEL-100")
def test_interval_for_is_absent_by_default_and_refused_on_a_glm() -> None:
    """A GLM has a covariance matrix; FR-MODEL-78's route is the GBM's alone.

    Asserted in both directions. The default matters because almost no GBM is a bound and a
    non-`None` default would make every ordinary model look like one; the `GlmSpec` refusal
    matters because it pins that the field was added to the GBM arm rather than to the
    common block, where it would have changed every GLM's `spec_hash` for nothing.
    """
    assert _spec().interval_for is None
    with pytest.raises(pydantic.ValidationError):
        GlmSpec(
            model_family_slug="motor-ad-frequency",
            dataset_version_id=new_uuid7(),
            response_column="claim_count",
            interval_for=IntervalFor(model_id=new_uuid7(), model_version=1, alpha=0.05),
        )  # type: ignore[call-arg]


@pytest.mark.req("FR-MODEL-100")
def test_a_bound_round_trips_through_the_tagged_union() -> None:
    """`MODEL_SPEC_ADAPTER` is what the backend validates a stored spec with.

    A field that survives construction but not the union round-trip is one that vanishes on
    the first read back from the database — which is where every consumer of the pairing
    looks for it.
    """
    bound = _spec(interval_for=IntervalFor(model_id=new_uuid7(), model_version=7, alpha=0.05))
    restored = MODEL_SPEC_ADAPTER.validate_python(bound.model_dump(mode="json"))
    assert isinstance(restored, GbmSpec)
    assert restored.interval_for == bound.interval_for
