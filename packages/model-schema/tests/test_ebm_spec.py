"""The EBM arm of `ModelSpec` (`02` §4.4, §3.5).

Every test here is a **prohibition**, for the reason `test_gbm_spec.py` gives: a shape
that can represent a nonsense model eventually holds one, and a Model is what a Rating
Version references.

The refusals are the spec's own, by name (FR-MODEL-87's staging rule, dated note in
`02` §4.4): `interpret`'s objectives are `rmse` and `mae`, so §7's families and binomial
`log_loss` are refused rather than translated; `interactions=2` (triples) is
declared-and-unbuilt, so it is refused rather than stored; and offsets stay GLM-only, so
an EBM that declares one is refused rather than silently fitted without it.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    GlmFitResult,
    GlmSpec,
    Model,
    ModelStatus,
    OffsetSpec,
    SplitRef,
    WeightSpec,
    new_uuid7,
)
from model_schema.modelling import (
    EbmCategoricalBins,
    EbmFitResult,
    EbmNumericBins,
    EbmSpec,
    EbmTerm,
)


def _spec(**over: object) -> EbmSpec:
    base: dict[str, object] = {
        "model_type": "ebm",
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": new_uuid7(),
        "response_column": "ad_claim_count",
        "offset": OffsetSpec(kind="none"),
    }
    base.update(over)
    return EbmSpec(**base)  # type: ignore[arg-type]


def _term(term_features: tuple[int, ...], term_name: str, n_slots: int) -> EbmTerm:
    """A flat univariate term with `n_slots` all-zero slots — valid under the 0.7.8
    slot-layout checks when `n_slots` matches the feature's bins, which is what lets a
    test break one array without disturbing the others."""
    return EbmTerm(
        term_features=term_features,
        term_name=term_name,
        scores=(0.0,) * n_slots,
        standard_deviations=(0.0,) * n_slots,
        bin_weights=(0.0,) * n_slots,
    )


def _grid(term_features: tuple[int, ...], term_name: str, rows: int, cols: int) -> EbmTerm:
    """A pair term's rectangular grid: `rows` rows of `cols` all-zero slots each."""
    row = (0.0,) * cols
    return EbmTerm(
        term_features=term_features,
        term_name=term_name,
        scores=(row,) * rows,
        standard_deviations=(row,) * rows,
        bin_weights=(row,) * rows,
    )


def _fit(**over: object) -> EbmFitResult:
    """A fit whose shapes satisfy every `EbmFitResult` validator: two numeric features
    (61 cuts → 64 slots) and one categorical (3 levels → 5 slots), with one univariate
    term per feature."""
    base: dict[str, object] = {
        "model_type": "ebm",
        "objective": "rmse",
        "intercept": -2.4181,
        "feature_order": ("speed", "age_band", "area"),
        "bins": (
            EbmNumericBins(cuts=tuple(range(61))),
            EbmCategoricalBins(levels=("0-1", "2-4", "5-9")),
            EbmNumericBins(cuts=tuple(range(61))),
        ),
        "terms": (
            _term((0,), "speed", 64),
            _term((1,), "age_band", 5),
            _term((2,), "area", 64),
        ),
        "best_iteration": 412,
        "rows": 678_013,
        "fit_seconds": 41.2,
        "library_versions": {"interpret-core": "0.7.8"},
    }
    base.update(over)
    return EbmFitResult(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-37")
def test_the_objective_vocabulary_is_rmse_and_mae() -> None:
    with pytest.raises(pydantic.ValidationError, match="poisson"):
        _spec(objective="poisson")


@pytest.mark.req("FR-MODEL-87")
@pytest.mark.parametrize(
    "objective",
    ["poisson", "gamma", "tweedie", "inverse_gaussian", "negative_binomial", "log_loss"],
)
def test_the_families_and_binomial_log_loss_are_refused_by_name(objective: str) -> None:
    with pytest.raises(pydantic.ValidationError, match=objective):
        _spec(objective=objective)


@pytest.mark.req("FR-MODEL-37")
def test_max_bins_is_a_power_of_two_between_16_and_32768() -> None:
    assert _spec(max_bins=32).max_bins == 32
    for bad in (50, 8, 65536):
        with pytest.raises(pydantic.ValidationError, match="max_bins"):
            _spec(max_bins=bad)


@pytest.mark.req("FR-MODEL-37")
def test_the_interaction_grid_stays_in_the_jsonb_envelope() -> None:
    with pytest.raises(pydantic.ValidationError, match="interactions"):
        _spec(interactions=1, max_bins=512)
    assert _spec(interactions=1, max_bins=256).max_bins == 256


@pytest.mark.req("FR-MODEL-87")
def test_interactions_are_zero_or_one() -> None:
    with pytest.raises(pydantic.ValidationError, match="interactions"):
        _spec(interactions=2)


@pytest.mark.req("FR-MODEL-28")
def test_monotone_constraints_are_directions() -> None:
    with pytest.raises(pydantic.ValidationError, match="direction"):
        _spec(monotone_constraints={"age": 2})
    assert _spec(monotone_constraints={"age": 1, "area": 0}).monotone_constraints == {
        "age": 1,
        "area": 0,
    }
    assert _spec(monotone_constraints={}).monotone_constraints == {}


@pytest.mark.req("FR-MODEL-37")
def test_an_ebm_declares_no_offset() -> None:
    with pytest.raises(pydantic.ValidationError, match="GLM-only"):
        _spec(offset=OffsetSpec(kind="log_column", column="exposure_years"))


@pytest.mark.req("FR-MODEL-25")
def test_an_ebm_spec_round_trips_through_the_adapter() -> None:
    """`ebm` discriminates to `EbmSpec` — the sibling of the gbm test that used to name
    it as the unknown model type."""
    payload = _spec().model_dump(mode="json")
    assert isinstance(MODEL_SPEC_ADAPTER.validate_python(payload), EbmSpec)


@pytest.mark.req("FR-MODEL-37")
def test_the_common_block_flows_into_the_ebm_arm() -> None:
    spec = _spec(
        weight=WeightSpec(kind="column", column="n_claims"),
        seed=7,
        split_ref=SplitRef(split_artifact_id=new_uuid7()),
    )
    assert spec.weight == WeightSpec(kind="column", column="n_claims")
    assert spec.seed == 7
    assert spec.split_ref is not None


@pytest.mark.req("FR-MODEL-25")
def test_an_ebm_spec_cannot_hold_a_glm_fit() -> None:
    """Both unions are on one artifact, so the pairing has to be stated.

    An `EbmSpec` beside a `GlmFitResult` would be a model whose coefficient table
    describes a fit nobody made with the spec it sits beside.
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


@pytest.mark.req("FR-MODEL-37")
def test_the_bins_align_with_the_feature_order() -> None:
    """`bins` and `feature_order` are positional: a scoring frame reads bin `i` of
    feature `i`, so a list one short of the order is a model scored on the wrong
    feature's cuts, silently."""
    fit = _fit()
    assert len(fit.bins) == len(fit.feature_order)
    with pytest.raises(pydantic.ValidationError, match="bin definitions"):
        _fit(feature_order=("speed", "age_band"))


@pytest.mark.req("FR-MODEL-37")
def test_a_term_names_only_existing_features() -> None:
    base = _fit()
    with pytest.raises(pydantic.ValidationError, match="feature index"):
        _fit(terms=(_term((7,), "ghost", 64), base.terms[1], base.terms[2]))


@pytest.mark.req("FR-MODEL-37")
def test_the_lookup_shapes_match_the_bins() -> None:
    """61 cuts → 64 slots, 3 levels → 5 slots (the pinned 0.7.8 layout). A term whose
    arrays are not one score per slot is a lookup that will be read off-by-one."""
    base = _fit()
    with pytest.raises(pydantic.ValidationError, match="slots"):
        _fit(terms=(_term((0,), "speed", 63), base.terms[1], base.terms[2]))
    with pytest.raises(pydantic.ValidationError, match="slots"):
        _fit(terms=(base.terms[0], _term((1,), "age_band", 4), base.terms[2]))


@pytest.mark.req("FR-MODEL-37")
def test_an_interaction_grid_is_rectangular() -> None:
    """A pair term's scores are a grid with one row per bin of the first feature; a
    ragged grid, or one whose dims do not match the pair's slot counts, would mis-score
    every lookup after the first row."""
    base = _fit()
    valid = _grid((0, 2), "speed:area", 64, 64)
    assert _fit(terms=(valid, base.terms[1], base.terms[2])).terms[0].scores[0] == (0.0,) * 64
    with pytest.raises(pydantic.ValidationError, match="rows"):
        _fit(terms=(_grid((0, 2), "speed:area", 63, 64), base.terms[1], base.terms[2]))
    with pytest.raises(pydantic.ValidationError, match="columns"):
        _fit(terms=(_grid((0, 2), "speed:area", 64, 32), base.terms[1], base.terms[2]))
    ragged = EbmTerm(
        term_features=(0, 2),
        term_name="speed:area",
        scores=((0.0,) * 64,) * 63 + ((0.0,) * 63,),
        standard_deviations=((0.0,) * 64,) * 63 + ((0.0,) * 63,),
        bin_weights=((0.0,) * 64,) * 63 + ((0.0,) * 63,),
    )
    with pytest.raises(pydantic.ValidationError, match="rectangular"):
        _fit(terms=(ragged, base.terms[1], base.terms[2]))


@pytest.mark.req("FR-MODEL-37")
def test_the_base_slot_is_never_a_real_bin() -> None:
    """Slot 0 is the unused base slot — a nonzero weight on it would make the
    complexity count lie about the real bins."""
    base = _fit()
    bad = EbmTerm(
        term_features=(0,),
        term_name="speed",
        scores=(0.0,) * 64,
        standard_deviations=(0.0,) * 64,
        bin_weights=(1.0,) + (0.0,) * 63,
    )
    with pytest.raises(pydantic.ValidationError, match="base slot"):
        _fit(terms=(bad, base.terms[1], base.terms[2]))


@pytest.mark.req("FR-MODEL-25")
def test_a_fit_result_discriminates_on_model_type() -> None:
    payload = _fit().model_dump(mode="json")
    assert isinstance(FIT_RESULT_ADAPTER.validate_python(payload), EbmFitResult)


@pytest.mark.req("FR-MODEL-25")
def test_a_model_cannot_hold_a_fit_from_another_model_type() -> None:
    """Both unions are on one artifact, so the pairing has to be stated.

    An `EbmSpec` beside a `GlmFitResult` would be a model whose coefficient table
    describes a fit nobody made with the spec it sits beside; the reverse pairing is a
    lookup table sitting under a GLM spec. Neither discriminator can see the other, so
    nothing but `Model` refuses it.
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
    glm = GlmSpec(
        model_family_slug="motor-ad-frequency",
        dataset_version_id=new_uuid7(),
        response_column="ad_claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
    )
    with pytest.raises(pydantic.ValidationError, match="model_type"):
        Model(
            id=new_uuid7(),
            model_family_slug=glm.model_family_slug,
            version=1,
            status=ModelStatus.FITTED,
            spec=glm,
            spec_hash="v3:sha256:" + "b" * 64,
            fit_result=_fit(),
            diagnostics_id=new_uuid7(),
            dataset_version_id=glm.dataset_version_id,
        )
