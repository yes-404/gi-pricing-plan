"""Blob Upload route shapes (`07` §5.1, FR-421; the Blob Upload record is FR-1776's).

The request and the response of `POST /blobs/upload-url`. They were hand-written in the API
module until SL 1722, which moved them here (the maintainer (by delegation), 2026-10-16
10:16:17 BST, DP-1722-WIRE (a)): a shape that crosses the wire is `model-schema`'s
(`CLAUDE.md` §2), generated into `docs/contracts/`, never written twice.

Field names are the wire names and did not change in the move. `key` is the **staging key**
the bytes land on before `POST /blobs/uploads/{id}/complete` moves them to their content
address; the database column is `staging_key`, the wire name stays `key`.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["UploadUrlRequest", "UploadUrlResponse"]


class UploadUrlRequest(BaseModel):
    """The body of `POST /blobs/upload-url`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    media_type: str
    parts: Annotated[int, Field(ge=1, le=10_000)] = 1


class UploadUrlResponse(BaseModel):
    """The 200 of `POST /blobs/upload-url`: the Blob Upload `id` and the presigned parts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    key: str
    upload_id: str | None
    urls: list[str]
    expires_in_s: int
