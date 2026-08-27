"""The Phase 1b rating version (OD1, W7-3) — the smallest artifact 03's approval can pin.

The full 03 surface — compile, score, rate tables, deployment — stays Phase 2. This is
the artifact the exit demo needs: a slugged, versioned, draft → review → approved rating
version that pins an approved Model, so `wf-01`'s journey ends with something a rating
version can be approved against and the demo can display.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from model_schema.refs import ArtifactRef, Slug


class RatingVersionStatus(StrEnum):
    """The three states a minimal rating version passes through (OD1)."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"


#: The lifecycle, as data rather than scattered `if` statements. `draft` may skip review
#: straight to `approved` only where the caller is an approver deciding in one step; the
#: normal path goes through `review`.
VALID_RATING_VERSION_TRANSITIONS: dict[
    RatingVersionStatus, frozenset[RatingVersionStatus]
] = {
    RatingVersionStatus.DRAFT: frozenset(
        {RatingVersionStatus.REVIEW, RatingVersionStatus.APPROVED}
    ),
    RatingVersionStatus.REVIEW: frozenset({RatingVersionStatus.APPROVED}),
    RatingVersionStatus.APPROVED: frozenset(),
}


class RatingVersion(BaseModel):
    """A Phase 1b-minimal rating version that pins an approved Model (OD1, W7-3).

    The envelope is inline (00 §4.3), like `DatasetVersion`. `model_ref` is the pinned
    approved Model as an `ArtifactRef` (`model:{slug}@{version}`), so the approval trail
    names the exact model a version of rating logic would be approved against.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    slug: Slug
    version: int = Field(ge=1)
    status: RatingVersionStatus
    dataset_version_id: UUID
    model_ref: ArtifactRef
    created_at: datetime
    created_by: UUID
    updated_at: datetime
