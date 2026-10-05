"""The Environment, Deployment and Deployment Request shapes (`03` §4.12, `07` §4.2).

Each class validates its documented example and refuses an unknown key: a Deployment is an
append-only record (`00` FR-4), so a field the platform does not know must be a refusal, not
a silent drop.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from model_schema import (
    ARTIFACT_TYPES,
    ArtifactRef,
    Deployment,
    DeploymentCreate,
    DeploymentRequest,
    DeploymentRequestCreate,
    Environment,
    EnvironmentCreate,
    EnvironmentUpdate,
    ScopeType,
)

_WS = str(uuid4())
_USER = str(uuid4())

_EXAMPLES: dict[type[BaseModel], dict[str, Any]] = {
    Environment: {
        "slug": "prod",
        "name": "Production",
        "description": "Production quoting",
        "promotion_order": 3,
        "requires_prior_environment": "uat",
        "retired_at": None,
        "live_deployments": [
            {
                "rating_version_ref": "rating_version:motor-gb@27",
                "deployed_at": "2026-10-01T06:00:00Z",
                "bundle_hash": "sha256:" + "9f" * 32,
            }
        ],
    },
    EnvironmentCreate: {
        "slug": "staging",
        "name": "Staging",
        "description": "Pre-production",
        "promotion_order": 4,
        "requires_prior_environment": "uat",
    },
    EnvironmentUpdate: {"name": "Staging 2", "description": "Renamed"},
    Deployment: {
        "id": str(uuid4()),
        "workspace_id": _WS,
        "environment": "prod",
        "rating_version_ref": "rating_version:motor-gb@27",
        "bundle_hash": "sha256:" + "9f" * 32,
        "deployed_by": _USER,
        "deployed_at": "2026-10-01T06:00:00Z",
        "reason": "Annual rate review",
        "deployment_request_ref": "deployment:prod@3",
    },
    DeploymentCreate: {
        "rating_version_ref": "rating_version:motor-gb@27",
        "reason": "Annual rate review",
        "deployment_request_ref": "deployment:prod@3",
    },
    DeploymentRequest: {
        "id": str(uuid4()),
        "workspace_id": _WS,
        "ref": "deployment:prod@3",
        "environment": "prod",
        "rating_version_ref": "rating_version:motor-gb@27",
        "change_summary": "Annual rate review",
        "status": "review",
        "approval_request_id": str(uuid4()),
        "evidence": {
            "rating_version_approval": str(uuid4()),
            "uat_deployment": str(uuid4()),
        },
        "submitted_by": _USER,
        "created_at": "2026-10-01T05:00:00Z",
    },
    DeploymentRequestCreate: {
        "rating_version_ref": "rating_version:motor-gb@27",
        "change_summary": "Annual rate review",
        "skip": {"skipped_environment": "uat", "reason": "UAT frozen for the release"},
    },
}


@pytest.mark.req("FR-267")
@pytest.mark.parametrize("cls", list(_EXAMPLES), ids=lambda c: c.__name__)
def test_each_shape_validates_its_example(cls: type[BaseModel]) -> None:
    """Predicted red before `deployments.py` exists: `ImportError`."""
    assert cls.model_validate(_EXAMPLES[cls]) is not None


@pytest.mark.req("FR-267")
@pytest.mark.parametrize("cls", list(_EXAMPLES), ids=lambda c: c.__name__)
def test_each_shape_refuses_an_unknown_key(cls: type[BaseModel]) -> None:
    """Negative: `extra="forbid"` on every class of this module."""
    with pytest.raises(ValidationError, match="not_a_field"):
        cls.model_validate({**_EXAMPLES[cls], "not_a_field": 1})


@pytest.mark.req("FR-428")
def test_an_environment_update_refuses_a_slug() -> None:
    """RL-1301 A.6: the slug is immutable, so a body naming it is refused naming the field."""
    with pytest.raises(ValidationError, match="slug"):
        EnvironmentUpdate.model_validate({"name": "x", "slug": "other"})


@pytest.mark.req("FR-428")
@pytest.mark.parametrize("bad", ["Prod", "p", "has space", "-lead", "x" * 64])
def test_an_environment_create_slug_is_the_reference_slug_grammar(bad: str) -> None:
    """The slug is `refs.Slug`, never a second copy of the pattern (N1)."""
    with pytest.raises(ValidationError, match="slug"):
        EnvironmentCreate.model_validate({**_EXAMPLES[EnvironmentCreate], "slug": bad})


@pytest.mark.req("FR-267")
def test_a_deployment_create_carries_no_skip() -> None:
    """RL-1301 A.5: a skip is made at the request, never at the deploy route."""
    with pytest.raises(ValidationError, match="skip"):
        DeploymentCreate.model_validate(
            {
                **_EXAMPLES[DeploymentCreate],
                "skip": {"skipped_environment": "uat", "reason": "x"},
            }
        )


@pytest.mark.req("FR-267")
def test_references_are_typed_not_strings() -> None:
    """A malformed reference is refused; the typed field is an `ArtifactRef`."""
    with pytest.raises(ValidationError, match="rating_version_ref"):
        DeploymentCreate.model_validate(
            {**_EXAMPLES[DeploymentCreate], "rating_version_ref": "not a ref"}
        )
    deployment = Deployment.model_validate(_EXAMPLES[Deployment])
    assert isinstance(deployment.rating_version_ref, ArtifactRef)


@pytest.mark.req("FR-267")
def test_deployment_is_a_reference_type_and_environment_a_scope() -> None:
    """RL-1301 A.1 and B.1."""
    assert "deployment" in ARTIFACT_TYPES
    assert ScopeType.ENVIRONMENT.value == "environment"
    assert ArtifactRef.model_validate("deployment:prod@3").type == "deployment"
