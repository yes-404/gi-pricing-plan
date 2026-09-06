"""Blob upload and download (`07` §5.1, FR-421).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/blobs/upload-url` | Presigned upload so large files bypass the API process |
| `GET` | `/blobs/{sha256}` | Download, permission-checked, as a presigned redirect |

Declared by `07` §5.1 and reassigned to WK-660 by the endpoint audit: a dataset version's
parquet tables are blobs, so "download this version's data" needs them.

**Download is a 307 to a short-lived presigned URL, not a proxy.** A parquet table is
hundreds of megabytes and streaming it through the API process would tie up a worker for
the length of a download — a handful of concurrent downloads is then an outage. The
permission check happens here; the bytes never touch this process.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.authz import requires
from app.api.deps import Caller
from app.api.responses import problems
from app.db.models import BlobRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform.blobs import BlobStore, to_ref
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(prefix="/blobs", tags=["blobs"])

ReadDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_READ))]
WriteDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_WRITE))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


DatabaseDep = Annotated[Database, Depends(_database)]
BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]


class UploadUrlRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    media_type: str
    parts: Annotated[int, Field(ge=1, le=10_000)] = 1


class UploadUrlResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    upload_id: str | None
    urls: list[str]
    expires_in_s: int


@router.post(
    "/upload-url",
    summary="Presigned upload URL",
    responses=problems(401, 403, 422),
)
async def upload_url(
    body: UploadUrlRequest, caller: WriteDatasets, blob_store: BlobStoreDep
) -> UploadUrlResponse:
    """FR-421.

    The digest is not known until the bytes exist, so the object lands on a staging key and
    is promoted to its content address on completion. Asking the client for the digest up
    front would let it choose one, which is the difference between content addressing and
    client-supplied naming.
    """
    presigned = await blob_store.presign_upload(body.media_type, body.parts)
    return UploadUrlResponse(
        key=presigned.key,
        upload_id=presigned.upload_id,
        urls=list(presigned.urls),
        expires_in_s=presigned.expires_in_s,
    )


@router.get(
    "/{sha256}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Download a blob",
    responses=problems(401, 403, 404, 422),
    response_class=RedirectResponse,
)
async def download(
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")],
    caller: ReadDatasets,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    expires_in_s: Annotated[int, Query(ge=30, le=3600)] = 300,
) -> RedirectResponse:
    if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
        raise PlatformError(
            "VALIDATION_FAILED",
            "A blob is addressed by its lowercase hex SHA-256",
            422,
            f"{sha256!r} is not a 64-character lowercase hex digest.",
        )

    async with database.session() as session:
        row = (
            await session.execute(select(BlobRow).where(BlobRow.sha256 == sha256))
        ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Blob not found", 404, f"No blob with digest {sha256}."
        )

    url = await blob_store.presign_download(
        to_ref(row),
        expires_in_s=expires_in_s,
    )
    # 307 rather than 302: the method must be preserved, and a client following a 302 with
    # a rewritten method would send GET where it meant GET but need not have.
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
