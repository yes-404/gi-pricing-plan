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
from model_schema import GlmSpec, OffsetSpec


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
def test_every_code_the_fit_path_can_raise_is_registered() -> None:
    """Derived from `pricing-core`, so a new named failure is covered on the day it lands.

    The previous test names one code. This one asks the source of truth — the codes
    `GlmFitError` is actually constructed with — and would have caught the gap without
    anyone knowing which code was missing.
    """
    import ast
    import pathlib

    import pricing_core.modelling.glm as glm_module

    tree = ast.parse(pathlib.Path(glm_module.__file__).read_text())
    raised = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "GlmFitError"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }
    assert raised, "the parse found no GlmFitError call sites, so it proves nothing"
    assert raised <= MODELLING_ERROR_CODES, sorted(raised - MODELLING_ERROR_CODES)
