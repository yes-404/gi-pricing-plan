"""Cursor pagination (`00` §5.2), used by every collection endpoint.

```
GET /api/v1/jobs?limit=50&cursor=<opaque>&status=running
→ 200 {"items": [...], "next_cursor": "<opaque>|null", "total_estimate": 1234}
```

Cursor rather than offset, and the reason is in the spec's own words — *stable under
concurrent writes*. With `OFFSET`, a row inserted while a client pages through results
shifts everything after it, so the client sees one row twice and misses another. On a job
list that is refreshed while jobs are being submitted, that is the normal case rather than
an edge one.

The cursor is opaque on purpose. It encodes the sort key, and clients that decode it end up
depending on the sort key, which then cannot change without breaking them.
"""

from __future__ import annotations

import base64
import binascii
from typing import Annotated, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.errors import PlatformError

__all__ = [
    "MAX_LIMIT",
    "Page",
    "decode_cursor",
    "decode_int_cursor",
    "encode_cursor",
]

DEFAULT_LIMIT: Final = 50
MAX_LIMIT: Final = 200

#: Counting is capped rather than exact. FR-PLAT-14 retains job history for ≥ 13 months, so
#: an unbounded `COUNT(*)` on the jobs table would scan the year to render one page. The
#: field is `total_estimate` in the spec for exactly this reason.
COUNT_CAP: Final = 10_000

Limit = Annotated[int, Field(ge=1, le=MAX_LIMIT)]


class Page[T](BaseModel):
    """One page of a collection response."""

    model_config = ConfigDict(extra="forbid")

    items: list[T]
    next_cursor: str | None = Field(
        default=None,
        description="Opaque; pass back verbatim. Null when this is the last page.",
    )
    total_estimate: int = Field(
        ge=0,
        description=f"Matching rows, counted up to {COUNT_CAP}. An estimate by design.",
    )


def encode_cursor(value: UUID | int) -> str:
    """Encode a sort key as an opaque cursor.

    Accepts either key the platform sorts by: a UUIDv7 primary key, or a database-assigned
    sequence where insertion order matters more than creation time (job logs — UUIDv7 does
    not order within a millisecond).
    """
    return base64.urlsafe_b64encode(str(value).encode()).decode().rstrip("=")


def _decode_raw(cursor: str) -> str:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        return base64.urlsafe_b64decode(padded).decode()
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise _malformed() from exc


def _malformed() -> PlatformError:
    return PlatformError(
        "VALIDATION_FAILED",
        "Malformed cursor",
        400,
        "The cursor is not one this API issued. Omit it to start from the beginning.",
    )


def decode_int_cursor(cursor: str | None) -> int | None:
    """Decode a cursor encoding a sequence number."""
    if cursor is None:
        return None
    raw = _decode_raw(cursor)
    try:
        return int(raw)
    except ValueError as exc:
        raise _malformed() from exc


def decode_cursor(cursor: str | None) -> UUID | None:
    """Decode a cursor, rejecting anything malformed with a typed error.

    A bad cursor is a client error, not a server one — returning an empty page would look
    like "no more results" and silently truncate whatever the caller was iterating.
    """
    if cursor is None:
        return None
    raw = _decode_raw(cursor)
    try:
        return UUID(raw)
    except ValueError as exc:
        raise _malformed() from exc

