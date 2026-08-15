"""Reference tables and their versions (`01` §4.7, FR-DATA-29..32).

A Reference Table is an effective-dated lookup — postcode to rating area, vehicle code to
group, ULR band to loading. Two properties make it safe to rate on, and both are visible in
the shapes here:

* A **version** is immutable and independently approvable. Validation and rating pin an id;
  neither ever resolves "the latest", because "latest" evaluated at scoring time is a
  different answer each month (FR-DATA-30).
* A row's `[effective_from, effective_to)` interval is **half-open**, and non-overlapping
  per key. Overlap would give a lookup two answers, and which one a quote got would depend
  on row order — a rating difference nobody could reproduce.

These live here rather than in the API module because the frontend reads them: `CLAUDE.md`
§2's rule is that a shape crossing the boundary is defined once, in `model-schema`, and
generated from there.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ReferenceLookup",
    "ReferenceRow",
    "ReferenceTable",
    "ReferenceTableVersion",
]


class ReferenceTable(BaseModel):
    """A declared table: what it is keyed by, and what it carries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    key_columns: tuple[str, ...] = ()
    payload_columns: tuple[str, ...] = ()
    description: str | None = None
    created_at: datetime | None = None
    #: The highest **published** version, or null while every version is still a draft.
    #: Null is the state that matters: a table with only drafts cannot be pinned at all,
    #: and a list that showed a version number regardless would hide that.
    latest_published_version: int | None = None
    version_count: int = 0


class ReferenceTableVersion(BaseModel):
    """An immutable version of a table (FR-DATA-30)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    version: int
    status: str = "draft"
    source_note: str | None = None
    created_at: datetime | None = None
    row_count: int = 0
    #: The period the version's rows actually cover, as `[covers_from, covers_to)`.
    #: `covers_to` is null when any row is open-ended. `VR-REF-3` fails a dataset whose
    #: declared as-at date falls outside this, so it is the version's most load-bearing
    #: fact and not a decoration.
    covers_from: date | None = None
    covers_to: date | None = None


class ReferenceRow(BaseModel):
    """One effective-dated row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    payload: dict[str, Any] = Field(default_factory=dict)
    effective_from: date
    #: Null means open-ended, and the interval is half-open: a row with
    #: `effective_to = 2026-01-01` does **not** cover 2026-01-01.
    effective_to: date | None = None


class ReferenceLookup(BaseModel):
    """What a point lookup answers (FR-DATA-31) — for debugging, never for rating."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    reference_table_version_id: UUID
    version: int
    key: str
    payload: dict[str, Any] = Field(default_factory=dict)
    effective_from: date
    effective_to: date | None = None
