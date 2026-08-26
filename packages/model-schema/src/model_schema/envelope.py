"""The envelope every persisted artifact carries (`00-overview.md` §4.3)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from model_schema.money import Currency
from model_schema.refs import Slug

__all__ = ["ArtifactEnvelope"]


class ArtifactEnvelope(BaseModel):
    """Common fields for every artifact.

    `frozen=True` is the type-level expression of FR-OVR-1: an artifact is immutable once
    it leaves `draft`, and corrections create a new version rather than editing in place.
    Making the model mutable "for convenience" would put that invariant back into review
    comments, where it does not survive.

    `extra="forbid"` is deliberate too — ADR-0002 makes this package the single source of
    truth, so a field that is not declared here does not exist, and silently accepting one
    would let a shape drift into being without a contract change.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    slug: Slug
    version: int = Field(ge=1)
    status: str
    created_at: datetime
    created_by: UUID
    #: Non-null (OQ-OVR-16, resolved 2026-08-26): an artifact is created and updated in
    #: the same moment, and a nullable timestamp made the two moments indistinguishable
    #: from "never updated".
    updated_at: datetime
    archived_at: datetime | None = None
    parent_id: UUID | None = None
    #: The workspace's single currency (OQ-OVR-3, decided 2026-08-14). Recorded on every
    #: artifact even where no money is stored: multi-currency arrives in Phase 4, and
    #: carrying the code from the start makes that an addition of FX effective-dating
    #: rather than a migration of every monetary column in the platform. An artifact that
    #: does not know its own currency is one whose figures cannot be re-read later.
    currency: Currency = "GBP"

    labels: dict[str, str] = Field(default_factory=dict)
    description: str | None = None
    schema_version: int = Field(default=1, ge=1)
