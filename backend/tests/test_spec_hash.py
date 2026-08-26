"""`spec_hash` identifies a specification, and says which algorithm identified it.

FR-MODEL-66 returns the existing model rather than fitting the same specification twice.
That only works while the digest is stable, and it stops working **silently** the moment
`GlmSpec` gains a field: every stored digest quietly stops matching its own spec, a
resubmission looks new, and the same model is fitted twice under two versions with nothing
to say why. OQ-MODEL-8 named the version tag as the precondition for the first new field.

None of these tests need a database. They are here rather than in `packages/` because
`spec_hash` is the platform's, not `pricing-core`'s: the digest is about identity in a
workspace, and identity is not maths.
"""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.db.models import ModelRow
from app.errors import MODELLING_ERROR_CODES, PlatformError
from app.platform.modelling import SPEC_HASH_VERSION, spec_hash, spec_hash_is_current
from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    ApproximatedModel,
    EbmSpec,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    IntervalFor,
    OffsetSpec,
)


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-66")
@pytest.mark.req("FR-MODEL-86")
def test_the_digest_announces_the_algorithm_that_produced_it() -> None:
    """A `v1:` digest in a database this code no longer produces is findable.

    An untagged one is not, which is the whole difference — the tag does not prevent an
    algorithm change, it makes one legible.
    """
    digest = spec_hash(_spec())
    assert digest.startswith(f"v{SPEC_HASH_VERSION}:sha256:")
    assert spec_hash_is_current(digest) is True
    assert spec_hash_is_current("sha256:" + "0" * 64) is False, (
        "an untagged digest is exactly the stale case this must detect"
    )


@pytest.mark.req("FR-MODEL-66")
@pytest.mark.req("FR-MODEL-86")
def test_the_version_is_inside_the_payload_not_only_in_front_of_it() -> None:
    """Otherwise a reader could strip the prefix and compare across algorithms.

    That comparison is not meaningful — two algorithms over the same spec are two different
    questions — so the hashed bytes must differ, not merely the label.
    """
    spec = _spec()
    untagged = json.dumps(
        spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    import hashlib

    assert not spec_hash(spec).endswith(hashlib.sha256(untagged.encode()).hexdigest())


@pytest.mark.req("FR-MODEL-66")
@pytest.mark.req("FR-MODEL-86")
def test_the_stored_column_is_wide_enough_for_a_tagged_digest() -> None:
    """A truncated digest is not a failure that reports itself — it is a *different*
    valid-looking digest, and two specs would collide on it."""
    limit = ModelRow.__table__.c.spec_hash.type.length
    assert limit is not None
    assert limit >= len(spec_hash(_spec()))


@pytest.mark.req("FR-MODEL-66")
def test_two_specs_differing_anywhere_are_two_specs() -> None:
    """Including in a seed, which changes nothing an actuary reads and everything a
    reproducibility claim rests on."""
    base = _spec()
    assert spec_hash(base) == spec_hash(base.model_copy())
    assert spec_hash(base) != spec_hash(_spec(seed=1))
    assert spec_hash(base) != spec_hash(_spec(model_family_slug="other"))
    assert spec_hash(base) != spec_hash(_spec(max_iter=201))


@pytest.mark.req("FR-MODEL-23")
def test_a_separated_fit_can_be_reported_as_the_named_refusal() -> None:
    """`GLM_SEPARATION_DETECTED` was raised by `pricing-core` and registered nowhere.

    The fit handler maps a `GlmFitError`'s code straight into a `PlatformError`, and an
    unregistered code raises `ValueError` from *inside the error path* — so the one
    failure FR-MODEL-23 exists to name arrived as a stack trace about error codes.
    """
    assert "GLM_SEPARATION_DETECTED" in MODELLING_ERROR_CODES
    problem = PlatformError(
        "GLM_SEPARATION_DETECTED", "The GLM could not be fitted", 409, "separated"
    )
    assert problem.code == "GLM_SEPARATION_DETECTED"


@pytest.mark.req("FR-MODEL-23")
@pytest.mark.parametrize(
    ("module_path", "exception_name"),
    [
        ("pricing_core.modelling.glm", "GlmFitError"),
        # FR-MODEL-106/107: `gbm.py` gained `METRIC_REF_UNRESOLVED`,
        # `METRIC_NOT_APPLICABLE` and `METRIC_NOT_FITTABLE` the day `eval_metrics`
        # started being honoured — the same gap this test caught for `glm.py`, now
        # covered on the GBM side too rather than trusted by construction.
        ("pricing_core.modelling.gbm", "GbmFitError"),
        # The same rule, applied to the EBM arm: `ebm.py` raised
        # `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` the day the W5 slice wired its fit.
        # This test does not auto-discover modules — the row is mandatory.
        ("pricing_core.modelling.ebm", "EbmFitError"),
    ],
)
def test_every_code_the_fit_path_can_raise_is_registered(
    module_path: str, exception_name: str
) -> None:
    """Derived from `pricing-core`, so a new named failure is covered on the day it lands.

    The previous test names one code. This one asks the source of truth — the codes
    `GlmFitError`/`GbmFitError` are actually constructed with — and would have caught the
    gap without anyone knowing which code was missing.
    """
    import ast
    import importlib
    import pathlib

    module = importlib.import_module(module_path)
    tree = ast.parse(pathlib.Path(str(module.__file__)).read_text())
    raised = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == exception_name
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }
    assert raised, f"the parse found no {exception_name} call sites, so it proves nothing"
    assert raised <= MODELLING_ERROR_CODES, sorted(raised - MODELLING_ERROR_CODES)


def _bound(**over: object) -> GbmSpec:
    """A GBM that *is* one side of another model's interval (FR-MODEL-78)."""
    base: dict[str, object] = {
        "model_type": "xgboost",
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "objective": GbmFunctionRef(kind="builtin", name="count:poisson"),
        "categorical_handling": "native",
    }
    base.update(over)
    return GbmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-86")
@pytest.mark.req("FR-MODEL-100")
@pytest.mark.req("FR-MODEL-37")
def test_the_algorithm_version_moved_with_the_new_field() -> None:
    """FR-MODEL-86: adding a spec field increments `n` in the same commit as the field.

    Asserted on the constant as well as on a digest. A digest-only test passes just as well
    after a hand-edit that added the field and forgot the constant — which is the exact
    mistake the requirement exists to catch, because its symptom is silent: every stored
    digest stops matching its own spec and FR-MODEL-66's dedup ends with no error to see.
    """
    # v7 -> v8 (2026-08-21, FR-MODEL-24): the offset-from-another-model slice renamed the
    # scaffold's `model_ref` to `offset_model_ref` — the offset a fit means is now part
    # of the payload, and two specs differing there must not share a digest or FR-MODEL-66
    # hands the second caller the first caller's model.
    # v8 -> v9 (2026-08-21, FR-MODEL-37): EbmSpec joined the union — model_type,
    # objective, interactions, max_bins, max_rounds and monotone_constraints join the
    # payload, and two EBM specs differing there must not share a digest or FR-MODEL-66
    # hands the second caller the first caller's model.
    # v9 -> v10 (2026-08-22, FR-MODEL-19/86): the **first bump for an interpretation
    # change rather than a payload one**. `weight` has been inside `ModelSpec` and inside
    # this digest since it was written, but `fit_gbm` ignored it until this date — so
    # every `v9:` digest over a weighted GBM spec describes a fit this build produces
    # differently. FR-MODEL-66 would otherwise hand the next caller the unweighted fit for
    # a weighted spec, with nothing to see. A future reader should not conclude from the
    # v1..v9 lineage that this tag tracks fields; it tracks what a digest promises.
    # v10 -> v11 (2026-08-26, FR-MODEL-129, OQ-MODEL-43): the companion `approximates_model`
    # — the slug@version address — joined the payload. How a surrogate addresses the model
    # it approximates is part of what the surrogate is, and two surrogates of the same
    # family at different versions are different models. Every `v10:` digest is now stale
    # and findable with `LIKE 'v10:%'`.
    assert SPEC_HASH_VERSION == 11, (
        "approximates_model joined the payload (FR-MODEL-129); the tag moves with it"
    )
    assert spec_hash(_bound()).startswith("v11:sha256:")
    assert spec_hash_is_current("v10:sha256:" + "0" * 64) is False, (
        "every v10 digest is now stale and must be findable with LIKE 'v10:%'"
    )


@pytest.mark.req("FR-MODEL-66")
@pytest.mark.req("FR-MODEL-37")
def test_an_ebm_spec_hashes_distinctly() -> None:
    """An EBM is a different fitted question than a GLM over the same skeleton.

    FR-MODEL-66 answers by digest, so the moment EbmSpec joins the union it must hash away
    from every other arm's spec — a resubmission as an EBM must not receive the GLM fitted
    on the same design. And within the arm, the fields a fit actually consumes are part of
    the identity: two EBM specs differing only in their bin grid or their objective are two
    different models, and a dedup that conflates them hands the second caller the first
    caller's fit.
    """
    skeleton: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="none"),
        "factors": (uuid4(),),
    }
    ebm = EbmSpec(**skeleton)
    # The same skeleton as a GLM: poisson would refuse the shared no-offset (FR-MODEL-19),
    # so the comparison uses a family the skeleton fits.
    glm = GlmSpec(**skeleton, family="gaussian")
    assert spec_hash(ebm) != spec_hash(glm)

    assert spec_hash(EbmSpec(**skeleton, max_bins=128)) != spec_hash(ebm)
    assert spec_hash(EbmSpec(**skeleton, objective="mae")) != spec_hash(ebm)


@pytest.mark.req("FR-MODEL-100")
def test_two_bounds_against_different_central_models_do_not_collide() -> None:
    """The whole reason the link lives in the spec rather than beside it.

    Two bounds identical but for the model they bound must hash differently. If they did
    not, `reserve_model` would answer the second caller with the first caller's model
    (FR-MODEL-66), and the second central model would silently acquire a bound fitted for
    another one — an interval around a model nobody fitted, rendering identically.
    """
    shared = {"dataset_version_id": uuid4()}
    left = _bound(
        interval_for=IntervalFor(model_id=uuid4(), model_version=7, alpha=0.05), **shared
    )
    right = _bound(
        interval_for=IntervalFor(model_id=uuid4(), model_version=7, alpha=0.05), **shared
    )
    assert spec_hash(left) != spec_hash(right)


@pytest.mark.req("FR-MODEL-129")
def test_two_surrogates_of_different_models_do_not_collide() -> None:
    """The companion joins the payload, so the address is part of the identity.

    Two surrogates identical but for the model they address — same family at different
    versions, or different families at the same version — must hash differently, or
    FR-MODEL-66 would answer the second caller with the first caller's fit.
    """
    shared = {"response_column": SURROGATE_RESPONSE_COLUMN}
    base = {"model_slug": "motor-ad-frequency", "model_version": 7}
    left = _spec(
        approximates_model_id=uuid4(),
        approximates_model=ApproximatedModel(**base),
        **shared,
    )
    different_version = _spec(
        approximates_model_id=uuid4(),
        approximates_model=ApproximatedModel(model_slug="motor-ad-frequency", model_version=8),
        **shared,
    )
    different_family = _spec(
        approximates_model_id=uuid4(),
        approximates_model=ApproximatedModel(model_slug="motor-ad-severity", model_version=7),
        **shared,
    )
    assert spec_hash(left) != spec_hash(different_version)
    assert spec_hash(left) != spec_hash(different_family)


@pytest.mark.req("FR-MODEL-100")
def test_the_two_sides_of_one_pair_do_not_collide() -> None:
    """The alpha is in the payload too, so a lower and an upper bound are distinct specs.

    Otherwise fitting the upper bound after the lower would return the lower one under
    FR-MODEL-66 and the pair would be one model referenced twice.
    """
    central, dataset = uuid4(), uuid4()
    lower = _bound(
        interval_for=IntervalFor(model_id=central, model_version=7, alpha=0.05),
        dataset_version_id=dataset,
    )
    upper = _bound(
        interval_for=IntervalFor(model_id=central, model_version=7, alpha=0.95),
        dataset_version_id=dataset,
    )
    assert spec_hash(lower) != spec_hash(upper)


@pytest.mark.req("FR-MODEL-100")
def test_an_ordinary_gbm_and_a_bound_do_not_collide() -> None:
    """`interval_for=None` must hash differently from any populated one.

    A central model and a bound fitted on the same design differ *only* by this field, so if
    it did not reach the payload the bound would dedup onto its own central model.
    """
    dataset = uuid4()
    plain = _bound(dataset_version_id=dataset)
    bound = _bound(
        interval_for=IntervalFor(model_id=uuid4(), model_version=7, alpha=0.05),
        dataset_version_id=dataset,
    )
    assert spec_hash(plain) != spec_hash(bound)
