"""ID-1..ID-4: artifact identity and the canonical reference form."""

import pytest
from pydantic import ValidationError

from model_schema.envelope import ArtifactEnvelope
from model_schema.refs import ArtifactRef


@pytest.mark.req("FR-6")
def test_canonical_reference_round_trips():
    assert str(ArtifactRef.parse("model:motor-ad-frequency@7")) == "model:motor-ad-frequency@7"


@pytest.mark.req("FR-6")
@pytest.mark.parametrize(
    "bad",
    [
        "model:motor-ad-frequency",          # no version
        "model:motor-ad-frequency@0",        # versions start at 1 (ID-2)
        "model:Motor-AD@1",                  # slugs are lower-case
        "nonsense:motor-ad@1",               # unknown artifact type
        "motor-ad@1",                        # no type
    ],
)
def test_malformed_references_are_refused(bad):
    with pytest.raises(
        ValueError, match=r"must have the form|slug is outside|unknown artifact type"
    ):
        ArtifactRef.parse(bad)


@pytest.mark.req("FR-4")
def test_artifact_reference_is_immutable():
    ref = ArtifactRef.parse("rating_version:motor-gb@27")
    with pytest.raises(ValidationError):
        ref.version = 28  # type: ignore[misc]


@pytest.mark.req("FR-4")
def test_envelope_is_frozen_and_forbids_undeclared_fields(envelope_kwargs):
    env = ArtifactEnvelope(**envelope_kwargs)
    with pytest.raises(ValidationError):
        env.status = "approved"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ArtifactEnvelope(**envelope_kwargs, undeclared="x")


@pytest.mark.req("FR-9")
def test_a_reference_that_can_be_built_can_be_re_read():
    """RL-1383 Ruled items 1-2: a field-built reference is validated like a parsed one."""
    ref = ArtifactRef(type="factor", slug="veh_brand", version=1)  # positive control
    assert ArtifactRef.parse(str(ref)) == ref
    assert ArtifactRef.model_validate(ref.model_dump(mode="json")) == ref
    # `_` belongs to the factor grammar only.
    with pytest.raises(ValidationError):
        ArtifactRef(type="model", slug="motor_gb", version=1)
    with pytest.raises(ValidationError):
        ArtifactRef(type="factor", slug="veh brand", version=1)
    with pytest.raises(ValidationError):
        ArtifactRef(type="widget", slug="x-y", version=1)


_BAD_FACTOR_SLUGS = ["", "Veh Brand", "a:b@1", "a" * 65, "a"]
_GOOD_FACTOR_SLUGS = ["veh_brand", "driver-age-1a2b"]


@pytest.mark.req("FR-83")
@pytest.mark.parametrize("slug", [*_BAD_FACTOR_SLUGS, *_GOOD_FACTOR_SLUGS])
def test_a_factor_create_refuses_a_slug_outside_the_factor_grammar(slug):
    """`FactorSlug` admits exactly what the parser's `factor` grammar admits (FD-1384)."""
    from pydantic import TypeAdapter

    from model_schema.refs import FactorSlug, slug_is_admitted

    admitted = slug_is_admitted("factor", slug)
    assert admitted == (slug in _GOOD_FACTOR_SLUGS)  # the table is the grammar's
    adapter = TypeAdapter(FactorSlug)
    if admitted:
        assert adapter.validate_python(slug) == slug
    else:
        with pytest.raises(ValidationError):
            adapter.validate_python(slug)


@pytest.mark.req("FR-209")
def test_a_stored_factor_slug_is_not_revalidated_on_read():
    """The read model stays tolerant: a stored slug outside the grammar still loads."""
    from model_schema import Factor

    stored = Factor.model_validate(
        {
            "id": "0197a3c0-0000-7000-8000-000000000001",
            "slug": "Veh Brand",
            "dataset_id": "0197a3c0-0000-7000-8000-000000000002",
            "version": 1,
            "type": "identity",
            "source_columns": ["veh_brand"],
        }
    )
    assert stored.slug == "Veh Brand"
