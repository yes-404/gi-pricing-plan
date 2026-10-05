"""Environments, Deployments and Deployment Requests (`07` §4.2, `03` §4.12; WK-674 Slice 2).

Added 2026-10-03 (`PL-1392`, FR-267, FR-428, FR-429). The Environment is declared once, here,
for `07` §4.2; the Deployment and the Deployment Request are `03` §4.12's. Nothing else
declares them (`CLAUDE.md` §2: a shape defined twice will diverge).

**A Deployment is a record, not a Governed Artifact.** It has no status and is never updated
or deleted (`00` FR-4). The approval attaches to the **Deployment Request** that precedes it
(`RL-1301` A), whose reference is `deployment:<environment slug>@<n>`.

**The Environment's `settings` object is not here.** It lands with WK-674 Slice 3 (`OQ-1235`).
`live_deployments` is derived from the Deployment rows and never stored a second time.

**Environment slugs.** Every `environment` field below is the Environment's immutable slug
(`RL-1301` A.6), typed with `refs.Slug` so the grammar has one definition.
"""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from model_schema.approvals import PromotionSkip
from model_schema.refs import ArtifactRef, Slug

__all__ = [
    "Deployment",
    "DeploymentCreate",
    "DeploymentRequest",
    "DeploymentRequestCreate",
    "DeploymentRequestEvidence",
    "DeploymentRequestStatus",
    "Environment",
    "EnvironmentCreate",
    "EnvironmentUpdate",
    "LiveDeployment",
]

_BUNDLE_HASH = r"^sha256:[a-f0-9]{64}$"


class LiveDeployment(BaseModel):
    """One entry of an Environment's derived `live_deployments` (`07` §4.2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_ref: ArtifactRef
    deployed_at: datetime
    bundle_hash: str = Field(pattern=_BUNDLE_HASH)


class Environment(BaseModel):
    """A named place a Rating Version is deployed to (`07` §4.2, FR-428)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug = Field(description="Immutable (RL-1301 A.6); what every reference names.")
    name: str = Field(min_length=1, description="The display name; the only renamable part.")
    description: str = ""
    promotion_order: int = Field(ge=1)
    requires_prior_environment: Slug | None = Field(
        default=None, description="The predecessor Environment's slug, read by FR-429."
    )
    retired_at: datetime | None = Field(
        default=None, description="Set when retired; the row and its slug are kept."
    )
    live_deployments: tuple[LiveDeployment, ...] = Field(
        default=(), description="Derived from the Deployment rows, never stored."
    )


class EnvironmentCreate(BaseModel):
    """The body of `POST /api/v1/environments` (`07` §5.1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    name: str = Field(min_length=1)
    description: str = ""
    promotion_order: int = Field(ge=1)
    requires_prior_environment: Slug | None = None


class EnvironmentUpdate(BaseModel):
    """The body of `PATCH /api/v1/environments/{slug}`: `name` and `description` only.

    `extra="forbid"` is what refuses a body naming `slug` (RL-1301 A.6).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None


class Deployment(BaseModel):
    """One approved Rating Version bound to one Environment at a point in time (`03` §4.12)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    environment: Slug
    rating_version_ref: ArtifactRef
    bundle_hash: str = Field(
        pattern=_BUNDLE_HASH, description="The Rating Version's compiled Bundle hash (FR-239)."
    )
    deployed_by: UUID
    deployed_at: datetime
    reason: str
    deployment_request_ref: ArtifactRef | None = Field(
        default=None,
        description=(
            "The approved Deployment Request executed; null only for a target with no "
            "`deployment` policy entry (RL-1301 A.5)."
        ),
    )


class DeploymentCreate(BaseModel):
    """The body of `POST /api/v1/environments/{env}/deployments`.

    No `skip`: a skip is made at the request and pinned in its evidence (RL-1301 A.5).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_ref: ArtifactRef
    reason: str = Field(min_length=1)
    deployment_request_ref: ArtifactRef | None = None


class DeploymentRequestStatus(enum.StrEnum):
    """A Deployment Request's states (`PL-1392` Task 3); `executed` is the deploy route's."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXECUTED = "executed"


class DeploymentRequestEvidence(BaseModel):
    """The two evidence items pinned once at submission (`06` FR-356, FR-364's floor)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_approval: UUID = Field(
        description="The decided approval request of the pinned Rating Version."
    )
    uat_deployment: UUID | PromotionSkip = Field(
        description=(
            "The predecessor item: the id of the successful Deployment of that Rating Version "
            "in the predecessor Environment, or a recorded `PromotionSkip`."
        )
    )


class DeploymentRequest(BaseModel):
    """The artifact that precedes a gated deploy (`03` §4.12, RL-1301 A)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    ref: ArtifactRef = Field(description="`deployment:<environment slug>@<n>`.")
    environment: Slug
    rating_version_ref: ArtifactRef
    change_summary: str
    status: DeploymentRequestStatus
    approval_request_id: UUID | None = None
    evidence: DeploymentRequestEvidence
    submitted_by: UUID
    created_at: datetime


class DeploymentRequestCreate(BaseModel):
    """The body of `POST /api/v1/environments/{env}/deployment-requests`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_ref: ArtifactRef
    change_summary: str = Field(min_length=1)
    skip: PromotionSkip | None = None
