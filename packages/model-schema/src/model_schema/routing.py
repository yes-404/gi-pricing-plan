"""Date routing and shadow configuration (`03` §4.13, FR-270, FR-271; WK-674 Slice 6).

Added 2026-10-21 (`RL-1834` D1 and D2). The routing rule is an Environment's date ranges,
written whole and appended, never updated; the shadow configuration is likewise appended.
Nothing else declares these shapes (`CLAUDE.md` §2: a shape defined twice will diverge).

A range is half-open: `[effective_from, effective_to)`, with `effective_to` `None` for an
open end. Every `environment` field is the Environment's immutable slug (`refs.Slug`).
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from model_schema.refs import ArtifactRef, Slug

__all__ = [
    "RoutedRange",
    "RoutingRange",
    "RoutingRule",
    "RoutingRuleUpdate",
    "ShadowConfig",
    "ShadowConfigUpdate",
]

_BUNDLE_HASH = r"^sha256:[a-f0-9]{64}$"


class RoutingRange(BaseModel):
    """One date range of a routing rule, naming the Rating Version it selects."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_ref: ArtifactRef
    effective_from: date
    effective_to: date | None = None


class RoutingRuleUpdate(BaseModel):
    """The body of `PUT /api/v1/environments/{env}/routing`. Empty `ranges` clears the rule."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ranges: list[RoutingRange]


class RoutedRange(RoutingRange):
    """A stored range: `deployment_id` is the latest Deployment of that Rating Version in the
    Environment at write time, set by the server."""

    deployment_id: UUID


class RoutingRule(BaseModel):
    """An Environment's current routing rule (the 200 body and the Audit Event's `after`)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: Slug
    ranges: list[RoutedRange]
    written_by: UUID
    written_at: datetime


class ShadowConfigUpdate(BaseModel):
    """The body of `PUT /api/v1/environments/{env}/shadow`. `fraction` is a sampling rate."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate_rating_version_ref: ArtifactRef
    fraction: float = Field(gt=0, le=1)


class ShadowConfig(BaseModel):
    """An Environment's current shadow configuration (the 200 body and the Audit Event's
    `after`). `candidate_bundle_hash` is the candidate's compiled bundle at write time."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: Slug
    candidate_rating_version_ref: ArtifactRef
    candidate_bundle_hash: str = Field(pattern=_BUNDLE_HASH)
    fraction: float = Field(gt=0, le=1)
    written_by: UUID
    written_at: datetime
