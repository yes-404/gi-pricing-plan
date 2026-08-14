"""ID-1..ID-4: artifact identity and the canonical reference form."""

import pytest
from pydantic import ValidationError

from model_schema.envelope import ArtifactEnvelope
from model_schema.refs import ArtifactRef


@pytest.mark.req("FR-OVR-3")
def test_canonical_reference_round_trips():
    assert str(ArtifactRef.parse("model:motor-ad-frequency@7")) == "model:motor-ad-frequency@7"


@pytest.mark.req("FR-OVR-3")
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
    with pytest.raises(ValueError):
        ArtifactRef.parse(bad)


@pytest.mark.req("FR-OVR-1")
def test_artifact_reference_is_immutable():
    ref = ArtifactRef.parse("rating_version:motor-gb@27")
    with pytest.raises(ValidationError):
        ref.version = 28  # type: ignore[misc]


@pytest.mark.req("FR-OVR-1")
def test_envelope_is_frozen_and_forbids_undeclared_fields(envelope_kwargs):
    env = ArtifactEnvelope(**envelope_kwargs)
    with pytest.raises(ValidationError):
        env.status = "approved"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ArtifactEnvelope(**envelope_kwargs, undeclared="x")
